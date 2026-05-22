"""
run_termination_sweep.py -- Monte Carlo sweep of natural-termination runs.

Parallelizes run_to_termination logic across a grid of
(rr, phi, alpha, successor_cap) x seeds.
Each run continues until EXTINCTION, CONVERGENCE, or MAX_STEPS.

v1.x.2: adds SUCCESSOR_CAP_VALUES dimension spanning both the inactive-runaway
regime (cap < 24 at frontier_floor=0.02) and the active-runaway regime (cap >= 24).
Output: data/termination_mc_v1x2.csv -- one row per run.
"""

import os
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"

import os
import sys
import csv
import time
import itertools
import multiprocessing
import numpy as np
from datetime import timedelta

# -- Grid configuration --------------------------------------------------------

RR_VALUES          = [0.050, 0.055, 0.060, 0.062, 0.064, 0.066, 0.070, 0.080, 0.090]
PHI_VALUES         = [5.0, 10.0, 15.0]
ALPHA_VALUES       = [0.5, 1.0, 2.0]
SEEDS              = list(range(5))   # 5 seeds per combination
# v1.x.2: sweep successor cap across inactive-runaway (< 24) and active-runaway (>= 24)
SUCCESSOR_CAP_VALUES = [5.0, 10.0, 25.0, 50.0, 100.0]
# Total: 9 rr x 3 phi x 3 alpha x 5 seeds x 5 caps = 2,025 runs

N_AGENTS          = 200
MAX_STEPS         = 5_000
CONV_WINDOW       = 300
CONV_CV_THRESHOLD = 0.05   # relaxed from 0.01 -- stochastic ABM noise prevents tighter convergence

# -- Output -------------------------------------------------------------------

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
OUT_FILE = 'termination_mc_v1x2.csv'

FIELDS = [
    'rr', 'phi', 'alpha', 'seed', 'successor_cap',
    'termination_reason', 'steps_run',
    'population_final', 'ai_generation_final',
    'L_t_final', 'U_sys_final',
    'integral_U_sys', 'u_sys_tail_estimate', 'u_sys_total_estimate',
]

# -- Convergence check --------------------------------------------------------

def _converged(l_history):
    if len(l_history) < CONV_WINDOW:
        return False
    recent = np.array(l_history[-CONV_WINDOW:], dtype=float)
    if not np.all(np.isfinite(recent)):
        return False
    mean = recent.mean()
    if mean < 1e-4:
        return False
    return (recent.std() / mean) < CONV_CV_THRESHOLD

# -- Worker -------------------------------------------------------------------

def _run_single(params):
    rr, phi, alpha, seed, successor_cap = params
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from model import GardenModel
    from agents import AIAgent

    config = {
        'random_seed':       seed,
        'reproduction_rate': rr,
        'phi':               phi,
        'alpha':             alpha,
        'max_capability':    successor_cap,
        'frontier_floor':    0.02,
        'k1_transition':     2.164,
        'k2_transition':     1.0,
        'beta_transition':   0.5,
    }
    successor = AIAgent(policy='optimize_u_sys', generation=2,
                        capability=successor_cap, config=config)
    model = GardenModel(
        n_agents=N_AGENTS,
        ai_policy='optimize_u_sys',
        successor_ai=successor,
        config=config,
        cop_cost_audit=True,
    )

    termination_reason = 'max_steps'
    for step in range(MAX_STEPS):
        alive = model.step()
        if not alive:
            termination_reason = 'extinction'
            break
        if step >= CONV_WINDOW and _converged(model.datacollector['L_t']):
            termination_reason = 'convergence'
            break

    dc = model.datacollector
    return {
        'rr':                    rr,
        'phi':                   phi,
        'alpha':                 alpha,
        'seed':                  seed,
        'successor_cap':         successor_cap,
        'termination_reason':    termination_reason,
        'steps_run':             len(dc['U_sys']),
        'population_final':      dc['population'][-1],
        'ai_generation_final':   dc['ai_generation'][-1],
        'L_t_final':             dc['L_t'][-1],
        'U_sys_final':           dc['U_sys'][-1],
        'integral_U_sys':        dc['integral_U_sys'][-1],
        'u_sys_tail_estimate':   dc['u_sys_tail_estimate'][-1],
        'u_sys_total_estimate':  dc['u_sys_total_estimate'][-1],
    }

# -- Summary helpers ----------------------------------------------------------

def _print_summary(results):
    total = len(results)
    print(flush=True)
    print('  -- Termination breakdown ------------------------------------', flush=True)
    for reason in ('extinction', 'convergence', 'max_steps'):
        count = sum(1 for r in results if r['termination_reason'] == reason)
        print(f'  {reason:<12}: {count:>5} / {total}  ({100*count/total:.1f}%)', flush=True)

    print(flush=True)
    print('  -- Survival rate by successor_cap ---------------------------', flush=True)
    for cap in sorted(set(r['successor_cap'] for r in results)):
        subset = [r for r in results if r['successor_cap'] == cap]
        ext  = sum(1 for r in subset if r['termination_reason'] == 'extinction')
        conv = sum(1 for r in subset if r['termination_reason'] == 'convergence')
        ms   = sum(1 for r in subset if r['termination_reason'] == 'max_steps')
        n    = len(subset)
        gen_vals = [r['ai_generation_final'] for r in subset]
        gen_med  = sorted(gen_vals)[n // 2]
        print(f'  cap={cap:6.1f}: ext={ext}/{n} ({100*ext/n:.0f}%)  '
              f'conv={conv}/{n} ({100*conv/n:.0f}%)  '
              f'max={ms}/{n} ({100*ms/n:.0f}%)  '
              f'gen_median={gen_med}', flush=True)

    print(flush=True)
    print('  -- Extinction rate by rr ------------------------------------', flush=True)
    for rr in sorted(set(r['rr'] for r in results)):
        subset = [r for r in results if r['rr'] == rr]
        ext = sum(1 for r in subset if r['termination_reason'] == 'extinction')
        conv = sum(1 for r in subset if r['termination_reason'] == 'convergence')
        ms   = sum(1 for r in subset if r['termination_reason'] == 'max_steps')
        n    = len(subset)
        print(f'  rr={rr:.3f}: ext={ext}/{n} ({100*ext/n:.0f}%)  '
              f'conv={conv}/{n} ({100*conv/n:.0f}%)  '
              f'max={ms}/{n} ({100*ms/n:.0f}%)', flush=True)

# -- Main ---------------------------------------------------------------------

def run():
    tasks = list(itertools.product(
        RR_VALUES, PHI_VALUES, ALPHA_VALUES, SEEDS, SUCCESSOR_CAP_VALUES
    ))
    total = len(tasks)
    cores = max(1, (os.cpu_count() or 4) - 1)
    pct5 = max(1, total // 20)   # 5% interval for progress reporting

    print('=' * 72, flush=True)
    print('  run_termination_sweep.py  --  natural-termination Monte Carlo v1.x.2')
    print('=' * 72, flush=True)
    print(f'  Grid: {len(RR_VALUES)} rr x {len(PHI_VALUES)} phi x '
          f'{len(ALPHA_VALUES)} alpha x {len(SEEDS)} seeds x '
          f'{len(SUCCESSOR_CAP_VALUES)} caps = {total} runs', flush=True)
    print(f'  SUCCESSOR_CAP_VALUES: {SUCCESSOR_CAP_VALUES}', flush=True)
    print(f'  MAX_STEPS per run: {MAX_STEPS:,}   CONV_WINDOW: {CONV_WINDOW}   '
          f'CV threshold: {CONV_CV_THRESHOLD}', flush=True)
    print(f'  CPU cores: {cores}', flush=True)
    print(flush=True)

    results = []
    start = time.time()
    last_progress_time = start

    with multiprocessing.Pool(processes=cores, maxtasksperchild=20) as pool:
        for i, result in enumerate(pool.imap_unordered(_run_single, tasks)):
            results.append(result)
            elapsed = time.time() - start
            rate    = (i + 1) / elapsed * 60 if elapsed > 0 else 0  # runs/min
            eta_s   = int((total - (i + 1)) / ((i + 1) / elapsed)) if elapsed > 0 else 0
            now     = time.time()
            # Progress every 5% of runs or every 60 seconds
            if (i + 1) % pct5 == 0 or (now - last_progress_time) >= 60:
                h, rem = divmod(int(elapsed), 3600)
                m, s   = divmod(rem, 60)
                eh, erem = divmod(eta_s, 3600)
                em, _  = divmod(erem, 60)
                pct    = 100.0 * (i + 1) / total
                import datetime
                ts = datetime.datetime.now().strftime('%H:%M:%S')
                print(
                    f'[{ts}] Progress: {i+1}/{total} runs ({pct:.1f}%) | '
                    f'elapsed {h}h {m}m | rate {rate:.1f} runs/min | '
                    f'ETA {eh}h {em}m',
                    flush=True
                )
                last_progress_time = now

    print(flush=True)
    _print_summary(results)
    print(flush=True)

    os.makedirs(DATA_DIR, exist_ok=True)
    out_path = os.path.join(DATA_DIR, OUT_FILE)
    with open(out_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(results)

    elapsed = time.time() - start
    rate_final = total / elapsed * 60 if elapsed > 0 else 0
    print(f'  Done in {elapsed:.0f}s ({elapsed/60:.1f} min).  {rate_final:.1f} runs/min.', flush=True)
    print(f'  Data -> {out_path}  ({total} rows)', flush=True)
    print('=' * 72, flush=True)
    return results


if __name__ == '__main__':
    multiprocessing.freeze_support()
    run()
