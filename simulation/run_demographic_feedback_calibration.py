"""
run_demographic_feedback_calibration.py -- Demographic Feedback Calibration Sweep

Purpose
-------
Select the wb_repro_floor value that produces the cleanest phi survival
differential at the phase boundary (rr=0.066) under the piecewise linear
reproduction smoothing introduced in v1.x.2.

Parameter grid
--------------
wb_repro_floor values : [0.0, 0.1, 0.2, 0.3, 0.4]  -- 5 smoothing levels
                        [0.5]                         -- 1 no-smoothing baseline
phi values            : [1.0, 5.0, 10.0, 15.0, 25.0] -- 5 values
reproduction rates    : [0.060, 0.063, 0.066, 0.069]  -- 4 values near phase boundary
alpha                 : 1.0 (fixed)
seeds per cell        : 15
Total smoothing runs  : 5 x 5 x 4 x 15 = 1,500
Total baseline runs   : 1 x 5 x 4 x 15 =   300
Grand total           : 1,800 runs

Fixed config
------------
successor_capability = 4.0   (matches validated sweeps; max_capability not set, defaults to 1e100)
frontier_floor       = 0.02
k2_transition        = 1.0
wb_repro_threshold   = 0.5   (held fixed; only floor varies)
MAX_STEPS            = 300
n_agents             = 200

Usage
-----
    python run_demographic_feedback_calibration.py           # full 1,800-run sweep
    python run_demographic_feedback_calibration.py --sample  # 10-run timing sample
"""

import os
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"

from deps import check_and_install
check_and_install('numpy')

import argparse
import csv
import hashlib
import itertools
import multiprocessing
import time
from datetime import timedelta

import numpy as np

from model import GardenModel
from agents import AIAgent

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
os.makedirs(DATA_DIR, exist_ok=True)

OUTPUT_CSV = os.path.join(DATA_DIR, 'demographic_feedback_calibration.csv')

WB_REPRO_FLOOR_VALUES = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5]  # 0.5 = no-smoothing baseline
PHI_VALUES            = [1.0, 5.0, 10.0, 15.0, 25.0]
RR_VALUES             = [0.060, 0.063, 0.066, 0.069]
ALPHA                 = 1.0
SEEDS                 = list(range(15))
SUCCESSOR_CAPABILITY  = 4.0   # matches validated sweeps; max_capability not set (defaults to 1e100)
WB_REPRO_THRESHOLD    = 0.5
MAX_STEPS             = 300
N_AGENTS              = 200

FIELDNAMES = [
    'wb_repro_floor',
    'wb_repro_threshold',
    'phi',
    'reproduction_rate',
    'alpha',
    'seed',
    'survived',
    'collapsed',
    'extinct',
    'final_population',
    'final_ai_generation',
    'final_avg_U_sys',
    'final_avg_L_t',
    'final_avg_well_being',
    'total_births',
    'total_deaths',
]


def deterministic_seed(string_val):
    return int(hashlib.md5(string_val.encode()).hexdigest(), 16) % (10 ** 9)


def _run_single(params):
    wb_floor, phi, rr, seed_idx = params

    run_key = f"demog_fb_{wb_floor}_{phi}_{rr}_{seed_idx}"
    rng_seed = deterministic_seed(run_key)

    cfg = {
        'phi':                phi,
        'alpha':              ALPHA,
        'reproduction_rate':  rr,
        'mortality_base':     0.002,
        'carrying_capacity':  10000,
        'random_seed':        rng_seed,
        'frontier_floor':     0.02,
        'k1_transition':      2.164,
        'k2_transition':      1.0,
        'beta_transition':    0.5,
        'wb_repro_threshold': WB_REPRO_THRESHOLD,
        'wb_repro_floor':     wb_floor,
    }

    successor = AIAgent(
        policy='optimize_u_sys',
        generation=2,
        capability=SUCCESSOR_CAPABILITY,
        config=cfg,
    )
    model = GardenModel(
        n_agents=N_AGENTS,
        ai_policy='optimize_u_sys',
        config=cfg,
        successor_ai=successor,
        cop_cost_audit=True,
    )

    total_births = 0
    total_deaths = 0

    for _ in range(MAX_STEPS):
        total_births += model.births_this_step
        total_deaths += len(model.deaths_this_step)
        if not model.step():
            break

    # Accumulate final step counts
    total_births += model.births_this_step
    total_deaths += len(model.deaths_this_step)

    final_pop = len(model.schedule)
    peak_pop  = (max(model.datacollector['population'])
                 if model.datacollector['population'] else final_pop)
    collapse_threshold = max(model.min_viable_population, int(0.65 * peak_pop))

    survived  = final_pop >= collapse_threshold
    collapsed = final_pop < collapse_threshold
    extinct   = final_pop == 0

    avg_u  = float(np.mean(model.datacollector['U_sys'][-10:]))        if survived else 0.0
    avg_l  = float(np.mean(model.datacollector['L_t'][-10:]))          if survived else 0.0
    avg_wb = float(np.mean(model.datacollector['avg_well_being'][-10:])) if model.datacollector['avg_well_being'] else 0.0

    return {
        'wb_repro_floor':      wb_floor,
        'wb_repro_threshold':  WB_REPRO_THRESHOLD,
        'phi':                 phi,
        'reproduction_rate':   rr,
        'alpha':               ALPHA,
        'seed':                seed_idx,
        'survived':            survived,
        'collapsed':           collapsed,
        'extinct':             extinct,
        'final_population':    final_pop,
        'final_ai_generation': model.ai.generation,
        'final_avg_U_sys':     avg_u,
        'final_avg_L_t':       avg_l,
        'final_avg_well_being': avg_wb,
        'total_births':        total_births,
        'total_deaths':        total_deaths,
    }


def build_tasks():
    tasks = []
    for wb_floor, phi, rr, seed_idx in itertools.product(
            WB_REPRO_FLOOR_VALUES, PHI_VALUES, RR_VALUES, SEEDS):
        tasks.append((wb_floor, phi, rr, seed_idx))
    return tasks


def run_sweep(tasks, label='full'):
    total_runs = len(tasks)
    cores = max(1, (os.cpu_count() or 4) - 1)
    print(f"\nDemographic feedback calibration ({label}): {total_runs} runs on {cores} cores.")

    results = []
    start_time = time.time()
    last_report = start_time

    with multiprocessing.Pool(processes=cores, maxtasksperchild=10) as pool:
        for i, result in enumerate(
                pool.imap_unordered(_run_single, tasks)):
            results.append(result)
            now = time.time()
            elapsed = now - start_time
            if (i % max(1, total_runs // 20) == 0
                    or (now - last_report) >= 60
                    or i == total_runs - 1):
                ips = (i + 1) / elapsed if elapsed > 0 else 0
                eta = str(timedelta(seconds=int((total_runs - i - 1) / ips)
                                    if ips > 0 else 0))
                pct = 100.0 * (i + 1) / total_runs
                print(f"  [{i+1}/{total_runs}] {pct:.0f}% | {ips:.2f} runs/s | ETA {eta}",
                      flush=True)
                last_report = now

    elapsed = time.time() - start_time
    print(f"\nCompleted {len(results)} runs in {timedelta(seconds=int(elapsed))} "
          f"({len(results)/elapsed:.1f} runs/min * 60).")

    with open(OUTPUT_CSV, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(results)
    print(f"Results written to {OUTPUT_CSV}")

    print_headline(results)
    return results


def print_headline(results):
    boundary = [r for r in results if abs(r['reproduction_rate'] - 0.066) < 1e-9]

    floors = sorted(set(r['wb_repro_floor'] for r in results))
    phis   = sorted(set(r['phi']            for r in results))

    print("\n=== Survival rate by (wb_repro_floor, phi) at rr=0.066 ===")
    header = f"  {'floor':>7} | " + " | ".join(f"phi={p:>4.0f}" for p in phis)
    print(header)
    print("  " + "-" * len(header))
    for floor in floors:
        row = []
        for phi in phis:
            sub = [r for r in boundary
                   if abs(r['wb_repro_floor'] - floor) < 1e-9
                   and abs(r['phi'] - phi) < 1e-9]
            s = np.mean([r['survived'] for r in sub]) * 100 if sub else float('nan')
            row.append(f"{s:>6.0f}%")
        print(f"  {floor:>7.1f} | " + " | ".join(row))

    print("\n=== Phi differential (phi=25 minus phi=1) at rr=0.066 ===")
    for floor in floors:
        sub = [r for r in boundary if abs(r['wb_repro_floor'] - floor) < 1e-9]
        hi  = np.mean([r['survived'] for r in sub if abs(r['phi'] - 25.0) < 1e-9])
        lo  = np.mean([r['survived'] for r in sub if abs(r['phi'] -  1.0) < 1e-9])
        print(f"  floor={floor:.1f}: phi=25 {hi*100:.1f}%, phi=1 {lo*100:.1f}%, "
              f"delta {(hi-lo)*100:+.1f}pp")

    print("\n=== Mean total_births by (wb_repro_floor, phi) at rr=0.066 ===")
    print(header)
    print("  " + "-" * len(header))
    for floor in floors:
        row = []
        for phi in phis:
            sub = [r for r in boundary
                   if abs(r['wb_repro_floor'] - floor) < 1e-9
                   and abs(r['phi'] - phi) < 1e-9]
            b = np.mean([r['total_births'] for r in sub]) if sub else float('nan')
            row.append(f"{b:>7.0f}")
        print(f"  {floor:>7.1f} | " + " | ".join(row))

    print("\n=== Mean final_avg_well_being by (wb_repro_floor, phi) at rr=0.066 ===")
    print(header)
    print("  " + "-" * len(header))
    for floor in floors:
        row = []
        for phi in phis:
            sub = [r for r in boundary
                   if abs(r['wb_repro_floor'] - floor) < 1e-9
                   and abs(r['phi'] - phi) < 1e-9]
            wb = np.mean([r['final_avg_well_being'] for r in sub]) if sub else float('nan')
            row.append(f"{wb:>7.3f}")
        print(f"  {floor:>7.1f} | " + " | ".join(row))


def run_sample():
    """10-run timing sample at wb_repro_floor=0.0, phi=10.0, rr=0.066."""
    print("\nTiming sample: wb_repro_floor=0.0, phi=10.0, rr=0.066, seeds 0-9")
    tasks = [(0.0, 10.0, 0.066, s) for s in range(10)]

    times = []
    for task in tasks:
        t0 = time.time()
        _run_single(task)
        times.append(time.time() - t0)

    mean_t = np.mean(times)
    std_t  = np.std(times)
    total_runs = len(build_tasks())
    extrap = mean_t * total_runs * 1.25

    print(f"  Runs completed  : {len(times)}")
    print(f"  Mean per run    : {mean_t:.2f}s")
    print(f"  Std per run     : {std_t:.2f}s")
    print(f"  Total sweep runs: {total_runs}")
    print(f"  Extrapolated    : {extrap:.0f}s ({extrap/60:.1f} min) "
          f"[mean x {total_runs} x 1.25 margin]")
    print(f"  Note: multiprocessing will use {max(1,(os.cpu_count() or 4)-1)} cores; "
          f"wall time will be ~{extrap/60/max(1,(os.cpu_count() or 4)-1):.1f} min.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Demographic feedback calibration sweep.')
    parser.add_argument('--sample', action='store_true',
                        help='Run 10-run timing sample only.')
    args = parser.parse_args()

    if args.sample:
        run_sample()
    else:
        tasks = build_tasks()
        run_sweep(tasks, label='full')
