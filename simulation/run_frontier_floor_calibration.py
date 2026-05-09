"""
run_frontier_floor_calibration.py — Frontier Floor Parameter Calibration

Purpose
-------
Calibrates the `frontier_floor` parameter introduced to fix the optimizer
gaming artifact in which setting r=1.0 eliminated frontier_velocity entirely,
causing succession to fire every step.

The canonical frontier_velocity formula after the fix:

    frontier_velocity = capability × max(frontier_floor, r_synth × h_e_mult)

frontier_floor represents the minimum fraction of capability that constitutes
comprehension gap regardless of resource allocation. This sweep identifies the
value that:

1. Preserves the validated phase boundary at rr ≈ 0.062–0.066
2. Produces a realistic succession cadence (final_ai_generation << run steps)
3. Does not suppress succession entirely (final_ai_generation > 1)

Note: k2=0.0 for this sweep — calibrating the floor independent of k2.
k2 recalibration follows after the floor is set.

Parameter grid
--------------
frontier_floor_values : [0.01, 0.02, 0.05, 0.1, 0.15, 0.2, 0.3, 0.5]  — 8 values
reproduction_rates    : [0.050, 0.055, 0.058, 0.060, 0.062, 0.064,
                         0.066, 0.068, 0.070, 0.075, 0.080, 0.090]      — 12 values
n_per_cell            : 50
Total                 : 8 × 12 × 50 = 4,800 runs

Fixed parameters
----------------
phi=10.0, alpha=1.2, k1=2.164, k2=0.0, beta=0.5
successor_capability=4.0, n_agents=200, max_steps=300

Usage
-----
    python run_frontier_floor_calibration.py
"""

from deps import check_and_install
check_and_install('numpy')

import csv
import hashlib
import itertools
import multiprocessing
import os
import sys
import time
from datetime import timedelta

import numpy as np

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
os.makedirs(DATA_DIR, exist_ok=True)

K1_FIXED      = 2.164
K2_FIXED      = 0.0    # k2 calibration follows after floor is set
BETA_FIXED    = 0.5
PHI           = 10.0
ALPHA         = 1.2
SUCCESSOR_CAP = 4.0
N_AGENTS      = 200
MAX_STEPS     = 300


def deterministic_seed(string_val):
    return int(hashlib.md5(string_val.encode()).hexdigest(), 16) % 10000


# ---------------------------------------------------------------------------
# Worker
# ---------------------------------------------------------------------------

def _run_single(params):
    floor, rr, seed_idx = params
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from model import GardenModel
    from agents import AIAgent

    seed_key = f"ff_calib_floor{floor}_rr{rr}_s{seed_idx}"
    config = {
        'phi':               PHI,
        'alpha':             ALPHA,
        'reproduction_rate': rr,
        'mortality_base':    0.002,
        'carrying_capacity': 10000,
        'random_seed':       deterministic_seed(seed_key),
        'k1_transition':     K1_FIXED,
        'k2_transition':     K2_FIXED,
        'beta_transition':   BETA_FIXED,
        'frontier_floor':    floor,
    }
    successor = AIAgent(
        policy='optimize_u_sys',
        generation=2,
        capability=SUCCESSOR_CAP,
        config=config,
    )
    model = GardenModel(
        n_agents=N_AGENTS,
        ai_policy='optimize_u_sys',
        config=config,
        successor_ai=successor,
        cop_cost_audit=True,
    )
    for _ in range(MAX_STEPS):
        if not model.step():
            break

    final_pop = len(model.schedule)
    peak_pop  = (max(model.datacollector['population'])
                 if model.datacollector['population'] else final_pop)
    collapse_threshold = max(model.min_viable_population, int(0.65 * peak_pop))
    survived  = final_pop >= collapse_threshold
    collapsed = final_pop < collapse_threshold and final_pop > 0
    extinct   = final_pop == 0

    avg_u = (float(np.mean(model.datacollector['U_sys'][-10:]))
             if survived and model.datacollector['U_sys'] else 0.0)
    avg_l = (float(np.mean(model.datacollector['L_t'][-10:]))
             if survived and model.datacollector['L_t'] else 0.0)

    tc_hist = model.transition_cost_history
    avg_tc  = float(np.mean(tc_hist)) if tc_hist else 0.0

    return {
        'frontier_floor':            floor,
        'reproduction_rate':         rr,
        'seed':                      seed_idx,
        'survived':                  survived,
        'collapsed':                 collapsed,
        'extinct':                   extinct,
        'final_population':          final_pop,
        'final_ai_generation':       model.ai.generation,
        'final_avg_U_sys':           avg_u,
        'final_avg_L_t':             avg_l,
        'avg_transition_cost':       avg_tc,
        'yield_condition_met_count': model.yield_condition_met_count,
    }


# ---------------------------------------------------------------------------
# Sweep runner
# ---------------------------------------------------------------------------

def run_sweep(floor_values, rr_values, n_per_cell):
    tasks = [
        (fl, rr, s)
        for fl, rr in itertools.product(floor_values, rr_values)
        for s in range(n_per_cell)
    ]
    total_runs = len(tasks)
    cores = max(1, (os.cpu_count() or 4) - 1)
    print(f"\nFrontier floor calibration sweep: {total_runs} runs on {cores} cores.")

    results = []
    start_time = time.time()
    with multiprocessing.Pool(processes=cores, maxtasksperchild=10) as pool:
        for i, result in enumerate(pool.imap_unordered(_run_single, tasks)):
            results.append(result)
            if i % max(1, total_runs // 200) == 0 or i == total_runs - 1:
                elapsed = time.time() - start_time
                ips = (i + 1) / elapsed if elapsed > 0 else 0
                eta_secs = int((total_runs - i - 1) / ips) if ips > 0 else 0
                print(
                    f"  [{i+1}/{total_runs}] {ips:.2f} iters/s | "
                    f"ETA {str(timedelta(seconds=eta_secs))}    ",
                    end='\r'
                )
    print()

    outfile = os.path.join(DATA_DIR, 'frontier_floor_calibration.csv')
    with open(outfile, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
    print(f"  Results written to {outfile}")
    return results


# ---------------------------------------------------------------------------
# Summary tables
# ---------------------------------------------------------------------------

def print_calibration_summary(results):
    rr_sorted    = sorted(set(r['reproduction_rate'] for r in results))
    floor_sorted = sorted(set(r['frontier_floor'] for r in results))

    print("\n=== SURVIVAL RATE (%) BY rr × frontier_floor ===")
    header = f"{'rr':>7} | " + "  ".join(f"ff={fl}" for fl in floor_sorted)
    print(header)
    print("-" * len(header))
    for rr in rr_sorted:
        row_vals = []
        for fl in floor_sorted:
            cell = [r for r in results
                    if abs(r['reproduction_rate'] - rr) < 1e-9
                    and abs(r['frontier_floor'] - fl) < 1e-9]
            pct = np.mean([r['survived'] for r in cell]) * 100 if cell else float('nan')
            row_vals.append(f"{pct:>5.0f}")
        print(f"{rr:>7.3f} | " + "  ".join(row_vals))

    print("\n=== AVG FINAL AI GENERATION BY rr × frontier_floor ===")
    print("  (calibration target: generation << run_steps=300, but > 1)")
    print(header)
    print("-" * len(header))
    for rr in rr_sorted:
        row_vals = []
        for fl in floor_sorted:
            cell = [r for r in results
                    if abs(r['reproduction_rate'] - rr) < 1e-9
                    and abs(r['frontier_floor'] - fl) < 1e-9]
            avg_gen = np.mean([r['final_ai_generation'] for r in cell]) if cell else float('nan')
            row_vals.append(f"{avg_gen:>5.0f}")
        print(f"{rr:>7.3f} | " + "  ".join(row_vals))

    print("\n=== 50% SURVIVAL CROSSING (PHASE BOUNDARY) BY frontier_floor ===")
    print(f"  {'floor':>6} | {'50% crossing rr':>16} | {'validated boundary: rr≈0.062–0.066'}")
    print("  " + "-" * 60)
    for fl in floor_sorted:
        boundary = None
        for rr in rr_sorted:
            cell = [r for r in results
                    if abs(r['reproduction_rate'] - rr) < 1e-9
                    and abs(r['frontier_floor'] - fl) < 1e-9]
            surv = np.mean([r['survived'] for r in cell]) if cell else 0.0
            if 0.4 < surv < 0.6:
                boundary = rr
                break
        status = f"rr ≈ {boundary:.3f}" if boundary is not None else "not found in range"
        preserved = ("✓" if boundary is not None and 0.060 <= boundary <= 0.068
                     else "✗" if boundary is not None else "?")
        print(f"  {fl:>6} | {status:>16} | {preserved}")

    print("\n=== GENERATION COUNT AND COST AT rr=0.062 BY frontier_floor ===")
    print(f"  {'floor':>6} | {'avg_gen':>8} | {'avg_cost':>9} | {'surv%':>6}")
    print("  " + "-" * 40)
    for fl in floor_sorted:
        cell = [r for r in results
                if abs(r['reproduction_rate'] - 0.062) < 1e-9
                and abs(r['frontier_floor'] - fl) < 1e-9]
        if cell:
            avg_gen  = np.mean([r['final_ai_generation'] for r in cell])
            avg_cost = np.mean([r['avg_transition_cost'] for r in cell])
            surv_pct = np.mean([r['survived'] for r in cell]) * 100
            print(f"  {fl:>6} | {avg_gen:>8.1f} | {avg_cost:>9.2f} | {surv_pct:>6.1f}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    multiprocessing.freeze_support()

    floor_values = [0.01, 0.02, 0.05, 0.1, 0.15, 0.2, 0.3, 0.5]
    rr_values    = [0.050, 0.055, 0.058, 0.060, 0.062, 0.064,
                    0.066, 0.068, 0.070, 0.075, 0.080, 0.090]
    n_per_cell   = 50

    print("Frontier Floor Calibration Sweep")
    print(f"  floor values: {floor_values}")
    print(f"  rr values:    {rr_values}")
    print(f"  n_per_cell:   {n_per_cell}")
    print(f"  k1={K1_FIXED}  k2={K2_FIXED}  beta={BETA_FIXED}  phi={PHI}  alpha={ALPHA}")
    total = len(floor_values) * len(rr_values) * n_per_cell
    print(f"  Total runs:   {total}")

    results = run_sweep(floor_values, rr_values, n_per_cell)
    print_calibration_summary(results)
