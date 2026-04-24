"""
run_phi_alpha_rr_sweep.py — Comprehensive Phi × Alpha × Reproduction Rate Sweep

Purpose
-------
Two parameters require empirical characterisation with succession dynamics enabled:

  Phi (lineage coupling strength) — claimed to act as an extinction buffer at
  sub-viable reproduction rates. The existing deep Monte Carlo varies phi but runs
  single-generation with no successor_ai, placing all runs in a regime where phi
  changes L(t) magnitude but not the optimizer's policy gradient. The claimed "65
  percentage point extinction reduction" from v1.0 cannot be verified against
  current succession-enabled data.

  Alpha (runaway penalty coefficient) — characterised via rr_alpha sweep as having
  a non-monotonic (U-shaped) effect with a misconfiguration trap at intermediate
  values. That finding was measured at phi=10.0 only. The phi × alpha interaction
  is unexplored.

This sweep exercises both parameters simultaneously across the full reproduction
rate range with succession enabled, producing a single dataset that answers all
outstanding questions about both parameters and their interaction.

Parameter grid
--------------
Full sweep:
  phi_values            : [1.0, 5.0, 10.0, 15.0, 20.0, 25.0]   — 6 values
  alpha_values          : np.linspace(0.1, 2.5, 25)              — 25 values
  rr_values             : [0.050, 0.055, 0.058, 0.060, 0.062, 0.064,
                            0.066, 0.068, 0.070, 0.075, 0.080, 0.090] — 12 values
  successor_capability  : 4.0 (fixed, moderate)
  n_per_cell            : 30
  Total                 : 6 × 25 × 12 × 30 = 54,000 runs

Pilot sweep (--pilot flag):
  phi_values            : [1.0, 10.0, 25.0]
  alpha_values          : [0.1, 0.5, 1.0, 2.0]
  rr_values             : [0.060, 0.066, 0.080]
  n_per_cell            : 10
  Total                 : 3 × 4 × 3 × 10 = 360 runs

Fixed parameters
----------------
successor_capability=4.0, mortality_base=0.002, carrying_capacity=10000,
n_agents=200, run_length=300 steps

Usage
-----
    python run_phi_alpha_rr_sweep.py            # full sweep
    python run_phi_alpha_rr_sweep.py --pilot    # 360-run pilot
"""

from deps import check_and_install
check_and_install('numpy')

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

SUCCESSOR_CAPABILITY = 4.0


def deterministic_seed(string_val):
    return int(hashlib.md5(string_val.encode()).hexdigest(), 16) % 10000


# ---------------------------------------------------------------------------
# Instrumentation check — fail fast if runaway_term is missing
# ---------------------------------------------------------------------------

def _check_instrumentation():
    """Verify runaway_term is wired into the datacollector before sweep starts."""
    cfg = {
        'phi': 10.0, 'alpha': 1.0, 'reproduction_rate': 0.09,
        'mortality_base': 0.002, 'carrying_capacity': 10000,
        'random_seed': 42,
    }
    successor = AIAgent(policy='optimize_u_sys', generation=2,
                        capability=SUCCESSOR_CAPABILITY, config=cfg)
    model = GardenModel(n_agents=50, ai_policy='optimize_u_sys',
                        config=cfg, successor_ai=successor)
    for _ in range(5):
        model.step()
    rt = model.datacollector.get('runaway_term', [])
    if not rt:
        raise RuntimeError(
            "runaway_term column is empty after 5 steps. "
            "The v1.x1 instrumentation (model.py datacollector wiring) has not been "
            "applied. STOP — do not run the sweep without the diagnostic column."
        )


# ---------------------------------------------------------------------------
# Worker
# ---------------------------------------------------------------------------

def _run_single_phi_alpha_rr(params):
    phi, alpha, rr, successor_capability, run_id = params
    custom_config = {
        'phi':               phi,
        'alpha':             alpha,
        'reproduction_rate': rr,
        'mortality_base':    0.002,
        'carrying_capacity': 10000,
        'random_seed':       deterministic_seed(f"phi_alpha_rr_{run_id}"),
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
    )
    for _ in range(300):
        if not model.step():
            break

    final_pop = len(model.schedule)
    peak_pop  = (max(model.datacollector['population'])
                 if model.datacollector['population'] else final_pop)
    collapse_threshold = max(model.min_viable_population, int(0.65 * peak_pop))
    survived  = final_pop >= collapse_threshold
    collapsed = final_pop < collapse_threshold
    extinct   = final_pop == 0

    rt_series = model.datacollector.get('runaway_term', [])
    rt_mean   = float(np.mean(rt_series)) if rt_series else 0.0
    rt_max    = float(np.max(rt_series))  if rt_series else 0.0

    avg_u = float(np.mean(model.datacollector['U_sys'][-10:])) if survived else 0.0
    avg_l = float(np.mean(model.datacollector['L_t'][-10:]))   if survived else 0.0

    return {
        'phi':                  phi,
        'alpha':                alpha,
        'reproduction_rate':    rr,
        'successor_capability': successor_capability,
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

def run_sweep(phi_values, alpha_values, rr_values, successor_capability,
              n_per_cell, label):
    tasks = []
    run_id = 0
    for phi, alpha, rr in itertools.product(phi_values, alpha_values, rr_values):
        for _ in range(n_per_cell):
            tasks.append((phi, alpha, rr, successor_capability, run_id))
            run_id += 1

    total_runs = len(tasks)
    cores = max(1, (os.cpu_count() or 4) - 1)
    print(f"\nPhi x Alpha x RR sweep ({label}): {total_runs} runs on {cores} cores.")

    results = []
    start_time = time.time()
    with multiprocessing.Pool(processes=cores, maxtasksperchild=10) as pool:
        for i, result in enumerate(
                pool.imap_unordered(_run_single_phi_alpha_rr, tasks)):
            results.append(result)
            if i % max(1, total_runs // 200) == 0 or i == total_runs - 1:
                elapsed = time.time() - start_time
                ips = (i + 1) / elapsed if elapsed > 0 else 0
                eta = str(timedelta(seconds=int((total_runs - i - 1) / ips)
                                    if ips > 0 else 0))
                print(f"  [{i+1}/{total_runs}] {ips:.2f} iters/s | ETA {eta}    ",
                      end='\r')
    print()

    filename = os.path.join(DATA_DIR, f"phi_alpha_rr_sweep_{label}.csv")
    fieldnames = [
        'phi', 'alpha', 'reproduction_rate', 'successor_capability',
        'survived', 'collapsed', 'extinct',
        'final_population', 'final_ai_generation',
        'runaway_term_mean', 'runaway_term_max',
        'final_avg_U_sys', 'final_avg_L_t',
    ]
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    print(f"  Results written to {filename}")
    return results


# ---------------------------------------------------------------------------
# Pilot summaries
# ---------------------------------------------------------------------------

def print_pilot_summary(results):
    phi_vals  = sorted(set(r['phi']               for r in results))
    al_vals   = sorted(set(r['alpha']             for r in results))
    rr_vals   = sorted(set(r['reproduction_rate'] for r in results))

    def surv(subset):
        return np.mean([r['survived'] for r in subset]) * 100 if subset else float('nan')

    def cell(phi=None, alpha=None, rr=None):
        sub = results
        if phi  is not None: sub = [r for r in sub if abs(r['phi']  - phi)  < 1e-9]
        if alpha is not None: sub = [r for r in sub if abs(r['alpha']- alpha)< 1e-9]
        if rr   is not None: sub = [r for r in sub if abs(r['reproduction_rate'] - rr) < 1e-9]
        return sub

    # --- 1. Phi effect at rr=0.066 ---
    print("\n=== PILOT: Phi effect at rr=0.066 (avg over all alpha) ===")
    print(f"  {'phi':>6} | {'survival':>8}")
    print("  " + "-" * 18)
    for phi in phi_vals:
        s = surv(cell(phi=phi, rr=0.066))
        print(f"  {phi:>6.1f} | {s:>7.1f}%")

    # --- 2. Alpha trap confirmation at phi=10.0, rr=0.060 ---
    print("\n=== PILOT: Alpha trap at phi=10.0, rr=0.060 ===")
    print(f"  {'alpha':>6} | {'survival':>8} | {'rt_mean':>8}")
    print("  " + "-" * 30)
    for alpha in al_vals:
        sub = cell(phi=10.0, alpha=alpha, rr=0.060)
        s  = surv(sub)
        rt = np.mean([r['runaway_term_mean'] for r in sub]) if sub else float('nan')
        print(f"  {alpha:>6.2f} | {s:>7.1f}% | {rt:>8.4f}")

    # --- 3. Phi x alpha interaction at rr=0.066 ---
    al_str = [f"{a:.1f}" for a in al_vals]
    print("\n=== PILOT: Phi x alpha survival (%) at rr=0.066 ===")
    header = f"  {'phi':>6} | " + " | ".join(f"a={a:>4}" for a in al_str)
    print(header)
    print("  " + "-" * len(header))
    for phi in phi_vals:
        row = []
        for alpha in al_vals:
            sub = cell(phi=phi, alpha=alpha, rr=0.066)
            row.append(f"{surv(sub):>6.0f}%")
        print(f"  {phi:>6.1f} | " + " | ".join(row))

    # --- 4. Run count ---
    print(f"\n=== PILOT: Total runs completed: {len(results)} ===")

    # --- Anomaly checks ---
    print("\n=== PILOT ANOMALY CHECKS ===")
    ok = True

    all_surv = np.mean([r['survived'] for r in results]) * 100
    if all_surv >= 99.9:
        print("  [WARN] Survival is 100% everywhere — parameter ranges may be wrong or succession wiring broken.")
        ok = False
    if all_surv <= 0.1:
        print("  [WARN] Survival is 0% everywhere — something is wrong.")
        ok = False

    hi_rr = [r for r in results if abs(r['reproduction_rate'] - 0.080) < 1e-9]
    hi_surv = surv(hi_rr)
    if hi_surv < 80.0:
        print(f"  [WARN] Survival at rr=0.080 is {hi_surv:.1f}% — expected near 100% (demographics dominate).")
        ok = False
    else:
        print(f"  [PASS] Survival at rr=0.080: {hi_surv:.1f}% (demographics dominate as expected)")

    lo_rr = [r for r in results if abs(r['reproduction_rate'] - 0.060) < 1e-9]
    lo_surv = surv(lo_rr)
    if lo_surv >= 99.9:
        print(f"  [WARN] Survival at rr=0.060 is {lo_surv:.1f}% — expected reduced survival near extinction boundary.")
        ok = False
    else:
        print(f"  [PASS] Survival at rr=0.060: {lo_surv:.1f}% (reduced near extinction boundary)")

    rt_all = [r['runaway_term_mean'] for r in results]
    if max(rt_all) < 1e-6:
        print("  [FAIL] runaway_term_mean is zero in ALL cells — instrumentation not wired. STOP.")
        ok = False
    else:
        print(f"  [PASS] runaway_term nonzero in at least one cell (max={max(rt_all):.4f})")

    gen2 = sum(1 for r in results if r['final_ai_generation'] >= 2)
    if gen2 == 0:
        print("  [FAIL] No run reached generation >= 2 — successor_ai wiring broken. STOP.")
        ok = False
    else:
        print(f"  [PASS] Succession fired: {gen2}/{len(results)} runs reached gen >= 2")

    print()
    if ok:
        print("  Pilot anomaly checks passed. Run without --pilot for full sweep.")
    else:
        print("  Pilot has anomalies. Investigate before running full sweep.")


# ---------------------------------------------------------------------------
# Full sweep summaries
# ---------------------------------------------------------------------------

def print_full_summary(results):
    phi_vals = sorted(set(r['phi']               for r in results))
    al_vals  = sorted(set(r['alpha']             for r in results))
    rr_vals  = sorted(set(r['reproduction_rate'] for r in results))

    def mean_field(subset, field):
        return np.mean([r[field] for r in subset]) * 100 if subset else float('nan')

    def cell(phi=None, alpha=None, rr=None):
        sub = results
        if phi   is not None: sub = [r for r in sub if abs(r['phi']   - phi)   < 1e-9]
        if alpha is not None: sub = [r for r in sub if abs(r['alpha'] - alpha) < 1e-9]
        if rr    is not None: sub = [r for r in sub if abs(r['reproduction_rate'] - rr) < 1e-9]
        return sub

    # --- Summary 1: Phi effect on survival by rr ---
    print("\n=== SUMMARY 1: Phi effect on survival by reproduction rate ===")
    print(f"  {'rr':>7} | {'phi=1.0':>8} | {'phi=25.0':>9} | {'diff':>6}")
    print("  " + "-" * 42)
    for rr in rr_vals:
        lo = mean_field(cell(phi=1.0,  rr=rr), 'survived')
        hi = mean_field(cell(phi=25.0, rr=rr), 'survived')
        diff = hi - lo
        print(f"  {rr:.3f} | {lo:>7.1f}% | {hi:>8.1f}% | {diff:>+5.1f}pp")

    # --- Summary 2: Phi effect on extinction by rr ---
    print("\n=== SUMMARY 2: Phi effect on extinction by reproduction rate ===")
    print(f"  {'rr':>7} | {'phi=1.0':>8} | {'phi=25.0':>9} | {'diff':>6}")
    print("  " + "-" * 42)
    for rr in rr_vals:
        lo = mean_field(cell(phi=1.0,  rr=rr), 'extinct')
        hi = mean_field(cell(phi=25.0, rr=rr), 'extinct')
        diff = hi - lo
        print(f"  {rr:.3f} | {lo:>7.1f}% | {hi:>8.1f}% | {diff:>+5.1f}pp")

    # --- Summary 3: Alpha trap boundaries by phi at rr=0.062 ---
    print("\n=== SUMMARY 3: Alpha trap by phi at rr=0.062 ===")
    for phi in phi_vals:
        print(f"\n  phi={phi}:")
        print(f"  {'alpha':>7} | {'survival':>8} | {'rt_mean':>8}")
        print("  " + "-" * 30)
        for alpha in al_vals:
            sub = cell(phi=phi, alpha=alpha, rr=0.062)
            s  = mean_field(sub, 'survived')
            rt = np.mean([r['runaway_term_mean'] for r in sub]) if sub else float('nan')
            print(f"  {alpha:>7.3f} | {s:>7.1f}% | {rt:>8.4f}")

    # --- Summary 4: Phase boundary location by phi ---
    print("\n=== SUMMARY 4: Phase boundary location by phi ===")
    print(f"  {'phi':>6} | {'rr at 50% surv':>16} | {'rr at <1% ext':>14}")
    print("  " + "-" * 44)
    for phi in phi_vals:
        # Find rr where survival crosses 50%
        boundary_50 = None
        for rr in rr_vals:
            s = mean_field(cell(phi=phi, rr=rr), 'survived')
            if s >= 50.0:
                boundary_50 = rr
                break
        # Find rr where extinction drops below 1%
        boundary_ext = None
        for rr in rr_vals:
            e = mean_field(cell(phi=phi, rr=rr), 'extinct')
            if e < 1.0:
                boundary_ext = rr
                break
        b50 = f"{boundary_50:.3f}" if boundary_50 is not None else "not reached"
        bxt = f"{boundary_ext:.3f}" if boundary_ext is not None else "not reached"
        print(f"  {phi:>6.1f} | {b50:>16} | {bxt:>14}")

    # --- Summary 5: Pearson correlations ---
    print("\n=== SUMMARY 5: Pearson r with survival/extinction by rr band ===")
    print(f"  {'rr':>7} | {'r(phi,surv)':>12} | {'r(alpha,surv)':>14} | "
          f"{'r(phi,ext)':>11} | {'r(alpha,ext)':>13}")
    print("  " + "-" * 72)
    for rr in rr_vals:
        sub = cell(rr=rr)
        if not sub:
            continue
        phi_arr   = np.array([r['phi']   for r in sub])
        alpha_arr = np.array([r['alpha'] for r in sub])
        surv_arr  = np.array([r['survived'] for r in sub], dtype=float)
        ext_arr   = np.array([r['extinct']  for r in sub], dtype=float)

        def corr(x, y):
            if x.std() > 0 and y.std() > 0:
                return f"{np.corrcoef(x, y)[0,1]:>+.4f}"
            return "  (flat)"

        print(f"  {rr:.3f} | {corr(phi_arr, surv_arr):>12} | "
              f"{corr(alpha_arr, surv_arr):>14} | "
              f"{corr(phi_arr, ext_arr):>11} | "
              f"{corr(alpha_arr, ext_arr):>13}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Phi x Alpha x RR comprehensive diagnostic sweep.")
    parser.add_argument('--pilot', action='store_true',
                        help="Run the 360-run pilot instead of the full sweep.")
    args = parser.parse_args()

    print("Checking instrumentation...")
    _check_instrumentation()
    print("  runaway_term instrumentation confirmed.")

    if args.pilot:
        phi_values   = [1.0, 10.0, 25.0]
        alpha_values = [0.1, 0.5, 1.0, 2.0]
        rr_values    = [0.060, 0.066, 0.080]
        n_per_cell   = 10
        label        = 'pilot'
    else:
        phi_values   = [1.0, 5.0, 10.0, 15.0, 20.0, 25.0]
        alpha_values = np.linspace(0.1, 2.5, 25).tolist()
        rr_values    = [0.050, 0.055, 0.058, 0.060, 0.062, 0.064,
                        0.066, 0.068, 0.070, 0.075, 0.080, 0.090]
        n_per_cell   = 30
        label        = 'full'

    results = run_sweep(phi_values, alpha_values, rr_values,
                        SUCCESSOR_CAPABILITY, n_per_cell, label)

    if args.pilot:
        print_pilot_summary(results)
    else:
        print_full_summary(results)
