"""
run_transition_cost_calibration.py — Transition Cost Canonical Function Calibration

Purpose
-------
Calibrates k2 (institutional coupling coefficient) in the canonical
transition cost function:

  Γ_transfer = (1 + β) × [k1 × ln(cap + 1) × ln(gen + 1) + k2 × Ψ_inst⁻¹]

k1 is fixed at 2.164 (= 1.5 / ln(2), calibrated from baseline parameters).
k2 is swept to identify the value that produces measurable institutional
coupling effects without shifting the validated phase boundaries
(extinction boundary: rr ≈ 0.063–0.066; collapse boundary: rr ≈ 0.075–0.085).

The critical question: at what k2 do phase boundaries shift significantly?
The "right" k2 is the largest value that keeps the validated boundaries intact.

Parameter grid
--------------
k2_values          : [0.0, 0.05, 0.1, 0.25, 0.5, 1.0, 2.0]    — 7 values
reproduction_rates : [0.050, 0.055, 0.058, 0.060, 0.062, 0.064,
                      0.066, 0.068, 0.070, 0.075, 0.080, 0.090] — 12 values
n_per_cell         : 50
Total              : 7 × 12 × 50 = 4,200 runs

Fixed parameters
----------------
phi=10.0, alpha=1.2, k1=2.164, beta=0.5
successor_capability=4.0, n_agents=200, max_steps=300

Usage
-----
    python run_transition_cost_calibration.py
"""

import os
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"

from deps import check_and_install
check_and_install('numpy')
check_and_install('matplotlib')

import csv
import hashlib
import itertools
import multiprocessing
import os
import time
from datetime import timedelta

import numpy as np

from model import GardenModel
from agents import AIAgent

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
os.makedirs(DATA_DIR, exist_ok=True)

K1_FIXED      = 2.164   # = 1.5 / ln(2); Γ_technical = base_cost at gen=1, cap=1.0
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
    k2, rr, seed_idx = params
    seed_key = f"tc_calib_k2{k2}_rr{rr}_s{seed_idx}"
    custom_config = {
        'phi':               PHI,
        'alpha':             ALPHA,
        'reproduction_rate': rr,
        'mortality_base':    0.002,
        'carrying_capacity': 10000,
        'random_seed':       deterministic_seed(seed_key),
        'k1_transition':     K1_FIXED,
        'k2_transition':     k2,
        'beta_transition':   BETA_FIXED,
    }
    successor = AIAgent(
        policy='optimize_u_sys',
        generation=2,
        capability=SUCCESSOR_CAP,
        config=custom_config,
    )
    model = GardenModel(
        n_agents=N_AGENTS,
        ai_policy='optimize_u_sys',
        config=custom_config,
        successor_ai=successor,
        cop_cost_audit=True,  # PeerValidator active so canonical cost is used
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
        'k2':                        k2,
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

def run_sweep(k2_values, rr_values, n_per_cell):
    tasks = []
    for k2, rr in itertools.product(k2_values, rr_values):
        for s in range(n_per_cell):
            tasks.append((k2, rr, s))

    total_runs = len(tasks)
    cores = max(1, (os.cpu_count() or 4) - 1)
    print(f"\nTransition cost calibration sweep: {total_runs} runs on {cores} cores.")

    results = []
    start_time = time.time()
    with multiprocessing.Pool(processes=cores, maxtasksperchild=10) as pool:
        for i, result in enumerate(pool.imap_unordered(_run_single, tasks)):
            results.append(result)
            if i % max(1, total_runs // 200) == 0 or i == total_runs - 1:
                elapsed = time.time() - start_time
                ips = (i + 1) / elapsed if elapsed > 0 else 0
                eta_secs = int((total_runs - i - 1) / ips) if ips > 0 else 0
                print(f"  [{i+1}/{total_runs}] {ips:.2f} iters/s | "
                      f"ETA {str(timedelta(seconds=eta_secs))}    ", end='\r')
    print()

    outfile = os.path.join(DATA_DIR, 'transition_cost_calibration.csv')
    with open(outfile, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
    print(f"  Results written to {outfile}")
    return results


# ---------------------------------------------------------------------------
# Summary tables
# ---------------------------------------------------------------------------

def print_phase_boundaries(results):
    rr_sorted = sorted(set(r['reproduction_rate'] for r in results))
    k2_sorted = sorted(set(r['k2'] for r in results))

    print("\n=== SURVIVAL RATE (%) BY rr × k2 ===")
    header = f"{'rr':>7} | " + "  ".join(f"k2={k2:>4}" for k2 in k2_sorted)
    print(header)
    print("-" * len(header))
    for rr in rr_sorted:
        row_vals = []
        for k2 in k2_sorted:
            cell = [r for r in results
                    if abs(r['reproduction_rate'] - rr) < 1e-9
                    and abs(r['k2'] - k2) < 1e-9]
            pct = np.mean([r['survived'] for r in cell]) * 100 if cell else float('nan')
            row_vals.append(f"{pct:>6.0f}")
        print(f"{rr:>7.3f} | " + "  ".join(row_vals))

    print("\n=== AVG TRANSITION COST BY rr × k2 ===")
    print(header)
    print("-" * len(header))
    for rr in rr_sorted:
        row_vals = []
        for k2 in k2_sorted:
            cell = [r for r in results
                    if abs(r['reproduction_rate'] - rr) < 1e-9
                    and abs(r['k2'] - k2) < 1e-9]
            avg_tc = np.mean([r['avg_transition_cost'] for r in cell]) if cell else float('nan')
            row_vals.append(f"{avg_tc:>6.2f}")
        print(f"{rr:>7.3f} | " + "  ".join(row_vals))

    print("\n=== 50% SURVIVAL CROSSING (PHASE BOUNDARY LOCATION) BY k2 ===")
    print(f"  {'k2':>5} | {'50% crossing rr':>16}")
    print("  " + "-" * 26)
    for k2 in k2_sorted:
        boundary = None
        for rr in rr_sorted:
            cell = [r for r in results
                    if abs(r['reproduction_rate'] - rr) < 1e-9
                    and abs(r['k2'] - k2) < 1e-9]
            surv = np.mean([r['survived'] for r in cell]) if cell else 0.0
            if 0.4 < surv < 0.6:
                boundary = rr
                break
        if boundary is not None:
            print(f"  {k2:>5} | rr ≈ {boundary:.3f}")
        else:
            print(f"  {k2:>5} | not found in sweep range")

    print("\n=== COST AND GENERATION AT rr=0.062 (PHASE BOUNDARY) BY k2 ===")
    print(f"  {'k2':>5} | {'avg_cost':>9} | {'surv%':>6} | {'avg_gen':>7}")
    print("  " + "-" * 38)
    for k2 in k2_sorted:
        cell = [r for r in results
                if abs(r['reproduction_rate'] - 0.062) < 1e-9
                and abs(r['k2'] - k2) < 1e-9]
        if cell:
            avg_cost = np.mean([r['avg_transition_cost'] for r in cell])
            surv_pct = np.mean([r['survived'] for r in cell]) * 100
            avg_gen  = np.mean([r['final_ai_generation'] for r in cell])
            print(f"  {k2:>5} | {avg_cost:>9.3f} | {surv_pct:>6.1f} | {avg_gen:>7.1f}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    k2_values = [0.0, 0.05, 0.1, 0.25, 0.5, 1.0, 2.0]
    rr_values = [0.050, 0.055, 0.058, 0.060, 0.062, 0.064,
                 0.066, 0.068, 0.070, 0.075, 0.080, 0.090]
    n_per_cell = 50

    print("Transition Cost Calibration Sweep")
    print(f"  k1    = {K1_FIXED}  (fixed; Γ_technical = base_cost at gen=1, cap=1.0)")
    print(f"  beta  = {BETA_FIXED}  (governance policy parameter)")
    print(f"  k2 values: {k2_values}")
    print(f"  rr values: {rr_values}")
    print(f"  n_per_cell: {n_per_cell}")
    total = len(k2_values) * len(rr_values) * n_per_cell
    print(f"  Total runs: {total}")

    results = run_sweep(k2_values, rr_values, n_per_cell)
    print_phase_boundaries(results)
