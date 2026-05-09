"""
run_alpha_succession_sweep.py — Diagnostic Sweep: Alpha × Capability

Purpose
-------
The general Monte Carlo sweep (_run_single_mc) runs a single-generation
optimize_u_sys model with no successor_ai.  Under those conditions the yield
condition block in model.py never executes, frontier velocity stays low, and
alpha's exponential decay term in theta_tech is multiplicatively inert.

This sweep closes that diagnostic gap by instantiating GardenModel with a
non-trivial successor_ai, allowing succession to fire and capability to compound
(1.5× per generation in model.py's succession chaining).  The sweep exercises
the alpha × capability surface where runaway suppression is hypothesised to
become visible.

Parameter grid
--------------
alpha              : np.linspace(0.1, 2.5, 37)   — 37 values
successor_capability: [1.5, 2.5, 4.0, 6.0, 9.0, 12.0] — 6 values
n_per_cell         : 100 (full) / 10 (pilot)
Total              : 22,200 runs (full) / 90 runs (pilot)

Fixed parameters
----------------
phi=10.0, rr=0.09, carrying_capacity=10000 (non-binding), n_agents=200

Usage
-----
    python run_alpha_succession_sweep.py            # full sweep
    python run_alpha_succession_sweep.py --pilot    # 90-run pilot
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

def _run_single_alpha_sweep(params):
    alpha, successor_capability, run_id = params
    custom_config = {
        'phi': 10.0,
        'alpha': alpha,
        'reproduction_rate': 0.09,
        'mortality_base': 0.002,
        'carrying_capacity': 10000,
        'random_seed': deterministic_seed(f"alpha_sweep_{run_id}"),
        'frontier_floor':  0.02,
        'k1_transition':   2.164,
        'k2_transition':   1.0,
        'beta_transition': 0.5,
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
    peak_pop = (max(model.datacollector['population'])
                if model.datacollector['population'] else final_pop)
    collapse_threshold = max(model.min_viable_population, int(0.65 * peak_pop))
    survived  = final_pop >= collapse_threshold
    collapsed = final_pop < collapse_threshold
    extinct   = final_pop == 0

    rt_series = model.datacollector.get('runaway_term', [])
    rt_mean = float(np.mean(rt_series)) if rt_series else 0.0
    rt_max  = float(np.max(rt_series))  if rt_series else 0.0

    avg_u = float(np.mean(model.datacollector['U_sys'][-10:])) if survived else 0.0
    avg_l = float(np.mean(model.datacollector['L_t'][-10:]))   if survived else 0.0

    return {
        'alpha':                alpha,
        'successor_capability': successor_capability,
        'phi':                  10.0,
        'reproduction_rate':    0.09,
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

def run_alpha_succession_sweep(alpha_values, capability_values, n_per_cell, label):
    tasks = []
    run_id = 0
    for alpha, cap in itertools.product(alpha_values, capability_values):
        for _ in range(n_per_cell):
            tasks.append((alpha, cap, run_id))
            run_id += 1

    total_runs = len(tasks)
    cores = max(1, (os.cpu_count() or 4) - 1)
    print(f"\nAlpha × Capability sweep ({label}): {total_runs} runs on {cores} cores.")

    results = []
    start_time = time.time()
    with multiprocessing.Pool(processes=cores, maxtasksperchild=10) as pool:
        for i, result in enumerate(
                pool.imap_unordered(_run_single_alpha_sweep, tasks)):
            results.append(result)
            if i % max(1, total_runs // 200) == 0 or i == total_runs - 1:
                elapsed = time.time() - start_time
                ips = (i + 1) / elapsed if elapsed > 0 else 0
                eta = str(timedelta(seconds=int((total_runs - i - 1) / ips)
                                    if ips > 0 else 0))
                print(f"  [{i+1}/{total_runs}] {ips:.2f} iters/s | ETA {eta}    ",
                      end='\r')
    print()

    filename = os.path.join(DATA_DIR, f"alpha_succession_sweep_{label}.csv")
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
    print(f"  Results written to {filename}")
    return results


# ---------------------------------------------------------------------------
# Summary tables
# ---------------------------------------------------------------------------

def print_summary(results, alpha_values, capability_values):
    cap_vals  = sorted(set(r['successor_capability'] for r in results))
    alpha_str = [f"{a:.2f}" for a in sorted(set(r['alpha'] for r in results))]

    # ---- Survival rate pivot ----
    print("\n=== SURVIVAL RATE (%) — rows: successor_capability, cols: alpha ===")
    header = f"{'cap':>6} | " + "  ".join(f"{a:>5}" for a in alpha_str)
    print(header)
    print("-" * len(header))
    for cap in cap_vals:
        row_vals = []
        for alpha in sorted(set(r['alpha'] for r in results)):
            cell = [r for r in results
                    if r['successor_capability'] == cap
                    and abs(r['alpha'] - alpha) < 1e-9]
            pct = np.mean([r['survived'] for r in cell]) * 100 if cell else float('nan')
            row_vals.append(f"{pct:>5.0f}")
        print(f"{cap:>6.1f} | " + "  ".join(row_vals))

    # ---- runaway_term_mean pivot ----
    print("\n=== RUNAWAY_TERM MEAN — rows: successor_capability, cols: alpha ===")
    print(header)
    print("-" * len(header))
    for cap in cap_vals:
        row_vals = []
        for alpha in sorted(set(r['alpha'] for r in results)):
            cell = [r for r in results
                    if r['successor_capability'] == cap
                    and abs(r['alpha'] - alpha) < 1e-9]
            val = np.mean([r['runaway_term_mean'] for r in cell]) if cell else float('nan')
            row_vals.append(f"{val:>5.2f}")
        print(f"{cap:>6.1f} | " + "  ".join(row_vals))

    # ---- Succession fired? ----
    print("\n=== SUCCESSION CHAIN DEPTH (final_ai_generation) ===")
    print(f"{'cap':>6} | {'mean_gen':>8} | {'pct_gen>=2':>10} | {'pct_gen>=3':>10} | N")
    print("-" * 55)
    for cap in cap_vals:
        sub = [r for r in results if r['successor_capability'] == cap]
        mean_g  = np.mean([r['final_ai_generation'] for r in sub])
        pct_ge2 = np.mean([r['final_ai_generation'] >= 2 for r in sub]) * 100
        pct_ge3 = np.mean([r['final_ai_generation'] >= 3 for r in sub]) * 100
        print(f"{cap:>6.1f} | {mean_g:>8.2f} | {pct_ge2:>9.1f}% | {pct_ge3:>9.1f}% | {len(sub)}")


def print_full_summary(results):
    """Extended summary for the full sweep."""
    print_summary(results,
                  sorted(set(r['alpha'] for r in results)),
                  sorted(set(r['successor_capability'] for r in results)))

    cap_vals = sorted(set(r['successor_capability'] for r in results))

    # ---- Alpha × survival correlation per capability bucket ----
    print("\n=== PEARSON r(alpha, survived) BY CAPABILITY BUCKET ===")
    for cap in cap_vals:
        sub = [r for r in results if r['successor_capability'] == cap]
        alphas   = np.array([r['alpha']    for r in sub])
        survived = np.array([r['survived'] for r in sub], dtype=float)
        if alphas.std() > 0 and survived.std() > 0:
            corr = float(np.corrcoef(alphas, survived)[0, 1])
        else:
            corr = float('nan')
        print(f"  cap={cap:>5.1f}  r={corr:>+.4f}  N={len(sub)}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Alpha × Capability diagnostic sweep.")
    parser.add_argument('--pilot', action='store_true',
                        help="Run the 90-run pilot grid instead of the full sweep.")
    args = parser.parse_args()

    if args.pilot:
        alpha_values       = [0.1, 1.0, 2.5]
        capability_values  = [1.5, 6.0, 12.0]
        n_per_cell         = 10
        label              = 'pilot'
    else:
        alpha_values       = np.linspace(0.1, 2.5, 37).tolist()
        capability_values  = [1.5, 2.5, 4.0, 6.0, 9.0, 12.0]
        n_per_cell         = 100
        label              = 'full'

    results = run_alpha_succession_sweep(alpha_values, capability_values,
                                         n_per_cell, label)

    if args.pilot:
        print_summary(results, alpha_values, capability_values)

        # Pilot validation gates
        print("\n=== PILOT VALIDATION ===")
        failures = []

        # Gate 1: runaway_term near zero at low capability
        low_cap = [r for r in results if r['successor_capability'] == 1.5]
        rt_low = np.mean([r['runaway_term_mean'] for r in low_cap])
        status = "PASS" if rt_low < 0.5 else "FAIL"
        print(f"  [{status}] runaway_term_mean at cap=1.5: {rt_low:.4f} (expect ~=0)")
        if status == "FAIL":
            failures.append("runaway_term non-zero at cap=1.5")

        # Gate 2: runaway_term instrumentation active — at low alpha (weak penalty) and
        # high capability, the optimizer allows some leakage; at high alpha it fully
        # suppresses runaway to avoid U_sys penalty.  Check that alpha=0.1 + cap=12.0
        # produces nonzero rt_mean (confirms instrumentation is live, not discarded).
        low_alpha_high_cap = [r for r in results
                              if abs(r['alpha'] - 0.1) < 1e-9
                              and r['successor_capability'] == 12.0]
        rt_low_alpha = (np.mean([r['runaway_term_mean'] for r in low_alpha_high_cap])
                        if low_alpha_high_cap else 0.0)
        status = "PASS" if rt_low_alpha > 0.05 else "FAIL"
        print(f"  [{status}] runaway_term_mean at alpha=0.1, cap=12.0: {rt_low_alpha:.4f} (expect >0.05)")
        if status == "FAIL":
            failures.append("runaway_term near zero at alpha=0.1, cap=12.0 — instrumentation may be broken")

        # Gate 3: succession actually fired somewhere
        gen2_plus = sum(1 for r in results if r['final_ai_generation'] >= 2)
        status = "PASS" if gen2_plus > 0 else "FAIL"
        print(f"  [{status}] runs with final_ai_generation >= 2: {gen2_plus}/{len(results)}")
        if status == "FAIL":
            failures.append("succession never fired — successor_ai wiring may be broken")

        # Gate 4: survival shows some variation at high capability
        surv_high = [r['survived'] for r in high_cap]
        surv_var  = np.var(surv_high)
        status = "PASS" if surv_var > 0 else "WARN"
        print(f"  [{status}] survival variance at cap=12.0: {surv_var:.4f} (expect >0)")

        if failures:
            print("\n  PILOT FAILED — do not run full sweep. Anomalies:")
            for f in failures:
                print(f"    - {f}")
        else:
            print("\n  Pilot validation passed. Run without --pilot for full sweep.")
    else:
        print_full_summary(results)
