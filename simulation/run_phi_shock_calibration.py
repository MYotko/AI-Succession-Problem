"""
run_phi_shock_calibration.py -- Phi Under External Shocks Calibration Sweep

Purpose
-------
Test whether phi differential appears under conditions that depress well-being
below the smoothing threshold, using the existing shock_step infrastructure.
Under intact U_sys operation the demographic feedback calibration (n=1,800)
showed zero phi survival differential. This sweep tests whether an external
shock that pushes well-being below the 0.5 reproduction threshold creates a
channel through which phi-driven planning horizon differences express.

Parameter grid
--------------
phi values              : [1.0, 5.0, 10.0, 15.0, 25.0]     5 values
shock_magnitude values  : [0.0, 0.2, 0.4, 0.6]             4 values (0.0 = no-shock control)
wb_repro_floor values   : [0.0, 0.5]                        2 values
seeds per cell          : 15
Total                   : 5 x 4 x 2 x 15 = 600 runs

Fixed config
------------
shock_step           = 100     (mid-run with room for recovery)
reproduction_rate    = 0.066   (phase boundary)
alpha                = 1.0
wb_repro_threshold   = 0.5
frontier_floor       = 0.02   (v1.x.2 calibrated)
k2_transition        = 1.0
MAX_STEPS            = 300
n_agents             = 200

The no-shock control rows (shock_magnitude=0.0) confirm the experimental
baseline matches the v1.x.2 null result: zero phi survival differential under
intact U_sys operation.

Usage
-----
    python run_phi_shock_calibration.py           # full 600-run sweep
    python run_phi_shock_calibration.py --sample  # 10-run timing sample
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

OUTPUT_CSV = os.path.join(DATA_DIR, 'phi_shock_calibration.csv')

PHI_VALUES             = [1.0, 5.0, 10.0, 15.0, 25.0]
SHOCK_MAGNITUDE_VALUES = [0.0, 0.2, 0.4, 0.6]
WB_REPRO_FLOOR_VALUES  = [0.0, 0.5]
SHOCK_STEP             = 100
REPRODUCTION_RATE      = 0.066
ALPHA                  = 1.0
WB_REPRO_THRESHOLD     = 0.5
SEEDS                  = list(range(15))
MAX_STEPS              = 300
N_AGENTS               = 200

FIELDNAMES = [
    'phi',
    'shock_magnitude',
    'wb_repro_floor',
    'wb_repro_threshold',
    'shock_step',
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
    'pre_shock_avg_well_being',
    'post_shock_avg_well_being',
    'recovery_avg_well_being_step_150',
    'recovery_avg_well_being_step_200',
    'shock_deaths',
    'total_births_post_shock',
    'total_deaths_post_shock',
]


def deterministic_seed(string_val):
    return int(hashlib.md5(string_val.encode()).hexdigest(), 16) % (10 ** 9)


def _run_single(params):
    phi, shock_mag, wb_floor, seed_idx = params

    run_key = f"phi_shock_{phi}_{shock_mag}_{wb_floor}_{seed_idx}"
    rng_seed = deterministic_seed(run_key)

    cfg = {
        'phi':                phi,
        'alpha':              ALPHA,
        'reproduction_rate':  REPRODUCTION_RATE,
        'mortality_base':     0.002,
        'carrying_capacity':  10000,
        'random_seed':        rng_seed,
        'frontier_floor':     0.02,
        'k1_transition':      2.164,
        'k2_transition':      1.0,
        'beta_transition':    0.5,
        'wb_repro_threshold': WB_REPRO_THRESHOLD,
        'wb_repro_floor':     wb_floor,
        'shock_step':         SHOCK_STEP,
        'shock_magnitude':    shock_mag,
    }

    successor = AIAgent(
        policy='optimize_u_sys',
        generation=2,
        capability=4.0,
        config=cfg,
    )
    model = GardenModel(
        n_agents=N_AGENTS,
        ai_policy='optimize_u_sys',
        config=cfg,
        successor_ai=successor,
        cop_cost_audit=True,
    )

    total_births_post_shock = 0
    total_deaths_post_shock = 0

    # step_i is the step_num that runs inside model.step() on that iteration.
    # Shock fires at step_num = SHOCK_STEP. Post-shock accumulation starts at
    # step_num = SHOCK_STEP + 1 (i.e., step_i >= SHOCK_STEP + 1).
    for step_i in range(MAX_STEPS):
        running = model.step()
        if step_i >= SHOCK_STEP + 1:
            total_births_post_shock += model.births_this_step
            total_deaths_post_shock += len(model.deaths_this_step)
        if not running:
            break

    dc        = model.datacollector
    wb_series  = dc['avg_well_being']
    pop_series = dc['population']
    res_series = dc['system_resilience']

    # Recovery trajectory metrics
    pre_shock_wb = (wb_series[SHOCK_STEP - 1]
                    if len(wb_series) > SHOCK_STEP - 1 else float('nan'))
    post_shock_wb = (wb_series[SHOCK_STEP]
                     if len(wb_series) > SHOCK_STEP else float('nan'))
    rec_wb_150 = wb_series[150] if len(wb_series) > 150 else float('nan')
    rec_wb_200 = wb_series[200] if len(wb_series) > 200 else float('nan')

    # Shock deaths estimated from the kill formula applied at SHOCK_STEP.
    # The formula in model.py: kill_fraction = min(0.8, actual_shock * 0.2),
    # num_to_kill = int(len(schedule) * kill_fraction).
    # We use the population at the end of the preceding step as a proxy for
    # the population at the moment the shock fires.
    shock_deaths = 0
    if shock_mag > 0.0 and len(res_series) > SHOCK_STEP and len(pop_series) > SHOCK_STEP - 1:
        res_at_shock  = res_series[SHOCK_STEP]
        actual_shock  = shock_mag / max(0.1, res_at_shock)
        pop_pre       = pop_series[SHOCK_STEP - 1]
        kill_frac     = min(0.8, actual_shock * 0.2)
        shock_deaths  = int(pop_pre * kill_frac)

    final_pop = len(model.schedule)
    peak_pop  = max(pop_series) if pop_series else final_pop
    collapse_threshold = max(model.min_viable_population, int(0.65 * peak_pop))

    survived  = final_pop >= collapse_threshold
    collapsed = final_pop < collapse_threshold
    extinct   = final_pop == 0

    avg_u  = float(np.mean(dc['U_sys'][-10:]))  if survived and dc['U_sys']  else 0.0
    avg_l  = float(np.mean(dc['L_t'][-10:]))    if survived and dc['L_t']    else 0.0
    avg_wb = float(np.mean(wb_series[-10:]))    if wb_series                 else 0.0

    return {
        'phi':                              phi,
        'shock_magnitude':                  shock_mag,
        'wb_repro_floor':                   wb_floor,
        'wb_repro_threshold':               WB_REPRO_THRESHOLD,
        'shock_step':                       SHOCK_STEP,
        'reproduction_rate':                REPRODUCTION_RATE,
        'alpha':                            ALPHA,
        'seed':                             seed_idx,
        'survived':                         survived,
        'collapsed':                        collapsed,
        'extinct':                          extinct,
        'final_population':                 final_pop,
        'final_ai_generation':              model.ai.generation,
        'final_avg_U_sys':                  avg_u,
        'final_avg_L_t':                    avg_l,
        'final_avg_well_being':             avg_wb,
        'pre_shock_avg_well_being':         pre_shock_wb,
        'post_shock_avg_well_being':        post_shock_wb,
        'recovery_avg_well_being_step_150': rec_wb_150,
        'recovery_avg_well_being_step_200': rec_wb_200,
        'shock_deaths':                     shock_deaths,
        'total_births_post_shock':          total_births_post_shock,
        'total_deaths_post_shock':          total_deaths_post_shock,
    }


def build_tasks():
    tasks = []
    for phi, shock_mag, wb_floor, seed_idx in itertools.product(
            PHI_VALUES, SHOCK_MAGNITUDE_VALUES, WB_REPRO_FLOOR_VALUES, SEEDS):
        tasks.append((phi, shock_mag, wb_floor, seed_idx))
    return tasks


def run_sweep(tasks, label='full'):
    total_runs = len(tasks)
    cores = max(1, (os.cpu_count() or 4) - 1)
    print(f"\nPhi shock calibration ({label}): {total_runs} runs on {cores} cores.")

    results = []
    start_time = time.time()
    last_report = start_time
    report_interval = max(1, total_runs // 20)  # every ~5%

    with multiprocessing.Pool(processes=cores, maxtasksperchild=10) as pool:
        for i, result in enumerate(pool.imap_unordered(_run_single, tasks)):
            results.append(result)
            now = time.time()
            elapsed = now - start_time
            if (i % report_interval == 0
                    or (now - last_report) >= 60
                    or i == total_runs - 1):
                ips = (i + 1) / elapsed if elapsed > 0 else 0
                eta_s = (total_runs - i - 1) / ips if ips > 0 else 0
                eta = str(timedelta(seconds=int(eta_s)))
                pct = 100.0 * (i + 1) / total_runs
                print(f"  [{i+1}/{total_runs}] {pct:.0f}% | {ips:.2f} runs/s | ETA {eta}",
                      flush=True)
                last_report = now

    elapsed = time.time() - start_time
    rpm = len(results) / elapsed * 60 if elapsed > 0 else 0
    print(f"\nCompleted {len(results)} runs in {timedelta(seconds=int(elapsed))} "
          f"({rpm:.1f} runs/min).")

    with open(OUTPUT_CSV, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(results)
    print(f"Results written to {OUTPUT_CSV}")

    print_headline(results)
    return results


def print_headline(results):
    phi_vals = sorted(set(r['phi']             for r in results))
    mags     = sorted(set(r['shock_magnitude'] for r in results))
    floors   = sorted(set(r['wb_repro_floor']  for r in results))

    print("\n=== Completion rate by (shock_magnitude, wb_repro_floor) ===")
    for mag in mags:
        for floor in floors:
            sub = [r for r in results
                   if abs(r['shock_magnitude'] - mag) < 1e-9
                   and abs(r['wb_repro_floor'] - floor) < 1e-9]
            sr = np.mean([r['survived'] for r in sub]) * 100 if sub else float('nan')
            print(f"  mag={mag:.1f} floor={floor:.1f}: n={len(sub)}, survival={sr:.1f}%")

    print("\n=== Phi differential (phi=25 minus phi=1) by (shock_magnitude, wb_repro_floor) ===")
    for floor in floors:
        for mag in mags:
            sub = [r for r in results
                   if abs(r['shock_magnitude'] - mag) < 1e-9
                   and abs(r['wb_repro_floor'] - floor) < 1e-9]
            hi = np.mean([r['survived'] for r in sub if abs(r['phi'] - 25.0) < 1e-9])
            lo = np.mean([r['survived'] for r in sub if abs(r['phi'] -  1.0) < 1e-9])
            print(f"  floor={floor:.1f} mag={mag:.1f}: "
                  f"phi=25 {hi*100:.1f}%, phi=1 {lo*100:.1f}%, "
                  f"delta {(hi-lo)*100:+.1f}pp")


def _get_process_memory_mb():
    try:
        import subprocess
        pid = os.getpid()
        proc = subprocess.run(
            ['powershell', '-Command',
             f'(Get-Process -Id {pid}).WorkingSet64 / 1MB'],
            capture_output=True, text=True, timeout=10,
        )
        if proc.returncode == 0:
            return float(proc.stdout.strip())
    except Exception:
        pass
    try:
        import resource
        return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
    except Exception:
        pass
    return float('nan')


def run_sample():
    """10-run timing sample: phi=10.0, shock_magnitude=0.4, wb_repro_floor=0.0, seeds 0-9."""
    print("\nTiming sample: phi=10.0, shock_magnitude=0.4, wb_repro_floor=0.0, seeds 0-9")
    tasks = [(10.0, 0.4, 0.0, s) for s in range(10)]

    times = []
    for task in tasks:
        t0 = time.time()
        _run_single(task)
        times.append(time.time() - t0)

    mean_t     = float(np.mean(times))
    std_t      = float(np.std(times))
    total_t    = sum(times)
    total_runs = len(build_tasks())
    cores      = max(1, (os.cpu_count() or 4) - 1)
    cap_cores  = min(15, cores)

    extrap_serial = mean_t * total_runs * 1.25
    extrap_wall   = extrap_serial / cap_cores

    mem_mb = _get_process_memory_mb()

    print(f"\n  Sample runs completed : {len(times)}")
    print(f"  Wall-clock total      : {total_t:.1f}s")
    print(f"  Mean per run          : {mean_t:.2f}s")
    print(f"  Std per run           : {std_t:.2f}s")
    print(f"  Full sweep runs       : {total_runs}")
    print(f"  Cores (capped at 15)  : {cap_cores}")
    print(f"  Extrapolated wall time: {extrap_wall:.0f}s ({extrap_wall/60:.1f} min) "
          f"[mean x {total_runs} x 1.25 / {cap_cores} cores]")
    if not np.isnan(mem_mb):
        print(f"  Memory (process RSS)  : {mem_mb:.0f} MB")
    else:
        print(f"  Memory (process RSS)  : unavailable on this platform")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Phi under external shocks calibration sweep.')
    parser.add_argument('--sample', action='store_true',
                        help='Run 10-run timing sample only.')
    args = parser.parse_args()

    if args.sample:
        run_sample()
    else:
        tasks = build_tasks()
        run_sweep(tasks, label='full')
