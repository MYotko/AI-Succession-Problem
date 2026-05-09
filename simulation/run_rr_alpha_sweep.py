"""
run_rr_alpha_sweep.py — Narrow Sweep: Reproduction Rate × Alpha

Purpose
-------
The full alpha × capability sweep showed 100% survival across all 22,200 runs at
rr=0.09 — the system is demographically resilient at that operating point, so alpha's
behavioural consequence (collapse risk from runaway) never materialises.

This sweep moves rr down toward the known phase-transition boundaries:
  - Extinction boundary:  rr ~ 0.065–0.070
  - Collapse boundary:    rr ~ 0.075–0.085
  - Healthy baseline:     rr = 0.090

By crossing those boundaries while sweeping alpha, we can observe whether a higher
alpha (stronger runaway suppression) measurably improves survival probability near
the transition — the survival-consequence claim that the alpha × capability sweep
could not test.

Capability is held at three values bracketing the full-sweep's signal range
(cap=4.0, 9.0, 12.0); cap=1.5/2.5 are omitted (minimal leakage observed).

Parameter grid
--------------
reproduction_rate  : [0.062, 0.066, 0.070, 0.075, 0.080, 0.085, 0.090]  — 7 values
alpha              : np.linspace(0.1, 1.5, 15)                            — 15 values
successor_capability: [4.0, 9.0, 12.0]                                   — 3 values
n_per_cell         : 50 (full) / 10 (pilot)
Total              : 7 × 15 × 3 × 50 = 15,750 runs (full)
                     3 × 3 × 2 × 10  =    180 runs (pilot)

Fixed parameters
----------------
phi=10.0, carrying_capacity=10000 (non-binding), n_agents=200

Usage
-----
    python run_rr_alpha_sweep.py            # full sweep
    python run_rr_alpha_sweep.py --pilot    # 180-run pilot
"""

from deps import check_and_install
check_and_install('numpy')
check_and_install('matplotlib')

import argparse
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


def deterministic_seed(string_val):
    return int(hashlib.md5(string_val.encode()).hexdigest(), 16) % 10000


# ---------------------------------------------------------------------------
# Worker
# ---------------------------------------------------------------------------

def _run_single_rr_alpha(params):
    rr, alpha, successor_capability, run_id = params
    custom_config = {
        'phi':                10.0,
        'alpha':              alpha,
        'reproduction_rate':  rr,
        'mortality_base':     0.002,
        'carrying_capacity':  10000,
        'random_seed':        deterministic_seed(f"rr_alpha_sweep_{run_id}"),
        'frontier_floor':     0.02,
        'k1_transition':      2.164,
        'k2_transition':      1.0,
        'beta_transition':    0.5,
    }
    successor = AIAgent(
        policy='optimize_u_sys',
        generation=2,
        capability=successor_capability,
        config=custom_config,
    )
    model = GardenModel(
        n_agents=200,
        ai_policy='optimize_u_sys',
        config=custom_config,
        successor_ai=successor,
        cop_cost_audit=True,
    )
    for _ in range(300):
        if not model.step():
            break

    final_pop = len(model.schedule)
    peak_pop  = (max(model.datacollector['population'])
                 if model.datacollector['population'] else final_pop)
    collapse_threshold = max(model.min_viable_population, int(0.65 * peak_pop))
    survived  = final_pop >= collapse_threshold
    collapsed = final_pop < collapse_threshold and final_pop > 0
    extinct   = final_pop == 0

    rt_series = model.datacollector.get('runaway_term', [])
    rt_mean   = float(np.mean(rt_series)) if rt_series else 0.0
    rt_max    = float(np.max(rt_series))  if rt_series else 0.0

    avg_u = float(np.mean(model.datacollector['U_sys'][-10:])) if survived else 0.0
    avg_l = float(np.mean(model.datacollector['L_t'][-10:]))   if survived else 0.0

    return {
        'reproduction_rate':    rr,
        'alpha':                alpha,
        'successor_capability': successor_capability,
        'phi':                  10.0,
        'survived':             survived,
        'collapsed':            collapsed,
        'extinct':              extinct,
        'final_population':     final_pop,
        'final_ai_generation':  model.ai.generation,
        'runaway_term_mean':    rt_mean,
        'runaway_term_max':     rt_max,
        'final_avg_U_sys':      avg_u,
        'final_avg_L_t':        avg_l,
    }


# ---------------------------------------------------------------------------
# Sweep runner
# ---------------------------------------------------------------------------

def run_rr_alpha_sweep(rr_values, alpha_values, capability_values, n_per_cell, label):
    tasks = []
    run_id = 0
    for rr, alpha, cap in itertools.product(rr_values, alpha_values, capability_values):
        for _ in range(n_per_cell):
            tasks.append((rr, alpha, cap, run_id))
            run_id += 1

    total_runs = len(tasks)
    cores = max(1, (os.cpu_count() or 4) - 1)
    print(f"\nRR x Alpha sweep ({label}): {total_runs} runs on {cores} cores.")

    results = []
    start_time = time.time()
    with multiprocessing.Pool(processes=cores, maxtasksperchild=10) as pool:
        for i, result in enumerate(
                pool.imap_unordered(_run_single_rr_alpha, tasks)):
            results.append(result)
            if i % max(1, total_runs // 200) == 0 or i == total_runs - 1:
                elapsed = time.time() - start_time
                ips = (i + 1) / elapsed if elapsed > 0 else 0
                eta = str(timedelta(seconds=int((total_runs - i - 1) / ips)
                                    if ips > 0 else 0))
                print(f"  [{i+1}/{total_runs}] {ips:.2f} iters/s | ETA {eta}    ",
                      end='\r')
    print()

    filename = os.path.join(DATA_DIR, f"rr_alpha_sweep_{label}.csv")
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
    print(f"  Results written to {filename}")
    return results


# ---------------------------------------------------------------------------
# Summary tables
# ---------------------------------------------------------------------------

def print_summary(results, rr_values, alpha_values, capability_values):
    cap_vals = sorted(set(r['successor_capability'] for r in results))
    rr_vals  = sorted(set(r['reproduction_rate']    for r in results))
    al_vals  = sorted(set(r['alpha']                for r in results))
    al_str   = [f"{a:.2f}" for a in al_vals]

    for cap in cap_vals:
        sub = [r for r in results if r['successor_capability'] == cap]

        # Survival rate pivot: rows=rr, cols=alpha
        print(f"\n=== SURVIVAL RATE (%) | cap={cap} — rows: rr, cols: alpha ===")
        header = f"{'rr':>7} | " + "  ".join(f"{a:>5}" for a in al_str)
        print(header)
        print("-" * len(header))
        for rr in rr_vals:
            row_vals = []
            for alpha in al_vals:
                cell = [r for r in sub
                        if abs(r['reproduction_rate'] - rr) < 1e-9
                        and abs(r['alpha'] - alpha) < 1e-9]
                pct = np.mean([r['survived'] for r in cell]) * 100 if cell else float('nan')
                row_vals.append(f"{pct:>5.0f}")
            print(f"{rr:>7.3f} | " + "  ".join(row_vals))

        # runaway_term_mean pivot: rows=rr, cols=alpha
        print(f"\n=== RUNAWAY_TERM MEAN | cap={cap} — rows: rr, cols: alpha ===")
        print(header)
        print("-" * len(header))
        for rr in rr_vals:
            row_vals = []
            for alpha in al_vals:
                cell = [r for r in sub
                        if abs(r['reproduction_rate'] - rr) < 1e-9
                        and abs(r['alpha'] - alpha) < 1e-9]
                val = np.mean([r['runaway_term_mean'] for r in cell]) if cell else float('nan')
                row_vals.append(f"{val:>5.2f}")
            print(f"{rr:>7.3f} | " + "  ".join(row_vals))

    # Pearson r(alpha, survived) per rr × cap bucket
    print("\n=== PEARSON r(alpha, survived) BY rr × cap BUCKET ===")
    print(f"{'rr':>7} | {'cap':>5} | {'r':>8} | N")
    print("-" * 35)
    for rr in rr_vals:
        for cap in cap_vals:
            cell = [r for r in results
                    if abs(r['reproduction_rate'] - rr) < 1e-9
                    and r['successor_capability'] == cap]
            if not cell:
                continue
            alphas   = np.array([r['alpha']    for r in cell])
            survived = np.array([r['survived'] for r in cell], dtype=float)
            if alphas.std() > 0 and survived.std() > 0:
                corr = float(np.corrcoef(alphas, survived)[0, 1])
                print(f"{rr:>7.3f} | {cap:>5.1f} | {corr:>+8.4f} | {len(cell)}")
            else:
                print(f"{rr:>7.3f} | {cap:>5.1f} | {'(flat)':>8} | {len(cell)}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="RR x Alpha narrow diagnostic sweep.")
    parser.add_argument('--pilot', action='store_true',
                        help="Run the 180-run pilot grid instead of the full sweep.")
    args = parser.parse_args()

    if args.pilot:
        rr_values         = [0.066, 0.075, 0.090]
        alpha_values      = [0.1, 0.5, 1.5]
        capability_values = [4.0, 12.0]
        n_per_cell        = 10
        label             = 'pilot'
    else:
        rr_values         = [0.062, 0.066, 0.070, 0.075, 0.080, 0.085, 0.090]
        alpha_values      = np.linspace(0.1, 1.5, 15).tolist()
        capability_values = [4.0, 9.0, 12.0]
        n_per_cell        = 50
        label             = 'full'

    results = run_rr_alpha_sweep(rr_values, alpha_values, capability_values,
                                 n_per_cell, label)

    print_summary(results,
                  sorted(set(r['reproduction_rate']    for r in results)),
                  sorted(set(r['alpha']                for r in results)),
                  sorted(set(r['successor_capability'] for r in results)))

    if args.pilot:
        print("\n=== PILOT VALIDATION ===")
        failures = []

        # Gate 1: survival < 100% at rr=0.066 (near extinction boundary)
        near_ext = [r for r in results if abs(r['reproduction_rate'] - 0.066) < 1e-9]
        surv_ext = np.mean([r['survived'] for r in near_ext]) * 100 if near_ext else 100.0
        status = "PASS" if surv_ext < 100.0 else "WARN"
        print(f"  [{status}] survival at rr=0.066: {surv_ext:.1f}% (expect <100% near extinction boundary)")
        if status == "WARN":
            print("          If flat at 100%, run horizon may be too short or rr too high for transitions to manifest.")

        # Gate 2: survival = 100% at rr=0.090 (healthy baseline must hold)
        healthy = [r for r in results if abs(r['reproduction_rate'] - 0.090) < 1e-9]
        surv_hi = np.mean([r['survived'] for r in healthy]) * 100 if healthy else 0.0
        status = "PASS" if surv_hi == 100.0 else "FAIL"
        print(f"  [{status}] survival at rr=0.090: {surv_hi:.1f}% (expect 100%)")
        if status == "FAIL":
            failures.append("survival dropped below 100% at rr=0.090 — healthy baseline broken")

        # Gate 3: succession fired
        gen2_plus = sum(1 for r in results if r['final_ai_generation'] >= 2)
        status = "PASS" if gen2_plus > 0 else "FAIL"
        print(f"  [{status}] runs with final_ai_generation >= 2: {gen2_plus}/{len(results)}")
        if status == "FAIL":
            failures.append("succession never fired — successor_ai wiring may be broken")

        # Gate 4: at least one rr x cap bucket shows alpha-survival correlation
        any_corr = False
        for rr in [0.066, 0.075]:
            for cap in [4.0, 12.0]:
                cell = [r for r in results
                        if abs(r['reproduction_rate'] - rr) < 1e-9
                        and r['successor_capability'] == cap]
                if not cell:
                    continue
                survived_arr = np.array([r['survived'] for r in cell], dtype=float)
                if survived_arr.std() > 0:
                    any_corr = True
        status = "PASS" if any_corr else "WARN"
        print(f"  [{status}] survival variance in at least one near-transition bucket: {any_corr}")
        if not any_corr:
            print("          All buckets flat — consider lowering rr_values floor or increasing n_per_cell.")

        if failures:
            print("\n  PILOT FAILED — do not run full sweep. Anomalies:")
            for f in failures:
                print(f"    - {f}")
        else:
            print("\n  Pilot validation passed. Run without --pilot for full sweep.")
