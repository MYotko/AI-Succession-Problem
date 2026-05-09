"""
run_termination_sweep.py -- Monte Carlo sweep of natural-termination runs.

Parallelizes run_to_termination logic across a grid of (rr, phi, alpha) x seeds.
Each run continues until EXTINCTION, CONVERGENCE, or MAX_STEPS.

Output: data/termination_mc.csv -- one row per run.
"""

import os
import sys
import csv
import time
import itertools
import multiprocessing
import numpy as np
from datetime import timedelta

# -- Grid configuration --------------------------------------------------------

RR_VALUES    = [0.050, 0.055, 0.060, 0.062, 0.064, 0.066, 0.070, 0.080, 0.090]
PHI_VALUES   = [5.0, 10.0, 15.0]
ALPHA_VALUES = [0.5, 1.0, 2.0]
SEEDS        = list(range(5))   # 5 seeds per combination -> 405 total runs

N_AGENTS          = 200
SUCCESSOR_CAP     = 4.0
MAX_STEPS         = 50_000
CONV_WINDOW       = 300
CONV_CV_THRESHOLD = 0.05   # relaxed from 0.01 -- stochastic ABM noise prevents tighter convergence

# Set to a subset of RR_VALUES to skip already-complete runs.
# e.g. RR_FILTER = [0.070, 0.080, 0.090] reruns only the surviving-regime slice.
# None means run the full grid.
RR_FILTER = None

# -- Output -------------------------------------------------------------------

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
OUT_FILE = ('termination_mc_surviving.csv' if RR_FILTER is not None
            else 'termination_mc.csv')

FIELDS = [
    'rr', 'phi', 'alpha', 'seed',
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
    rr, phi, alpha, seed = params
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from model import GardenModel
    from agents import AIAgent

    config = {
        'random_seed':       seed,
        'reproduction_rate': rr,
        'phi':               phi,
        'alpha':             alpha,
        'max_capability':    SUCCESSOR_CAP,
        'frontier_floor':    0.02,
        'k1_transition':     2.164,
        'k2_transition':     1.0,
        'beta_transition':   0.5,
    }
    successor = AIAgent(policy='optimize_u_sys', generation=2,
                        capability=SUCCESSOR_CAP, config=config)
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
    print()
    print('  -- Termination breakdown ------------------------------------')
    for reason in ('extinction', 'convergence', 'max_steps'):
        count = sum(1 for r in results if r['termination_reason'] == reason)
        print(f'  {reason:<12}: {count:>5} / {total}  ({100*count/total:.1f}%)')

    print()
    print('  -- Extinction rate by rr ------------------------------------')
    for rr in sorted(set(r['rr'] for r in results)):
        subset = [r for r in results if r['rr'] == rr]
        ext = sum(1 for r in subset if r['termination_reason'] == 'extinction')
        conv = sum(1 for r in subset if r['termination_reason'] == 'convergence')
        ms   = sum(1 for r in subset if r['termination_reason'] == 'max_steps')
        n    = len(subset)
        print(f'  rr={rr:.3f}: ext={ext}/{n} ({100*ext/n:.0f}%)  '
              f'conv={conv}/{n} ({100*conv/n:.0f}%)  '
              f'max={ms}/{n} ({100*ms/n:.0f}%)')

# -- Main ---------------------------------------------------------------------

def run():
    rr_grid = RR_FILTER if RR_FILTER is not None else RR_VALUES
    tasks = list(itertools.product(rr_grid, PHI_VALUES, ALPHA_VALUES, SEEDS))
    total = len(tasks)
    cores = max(1, (os.cpu_count() or 4) - 1)

    print('=' * 72)
    print('  run_termination_sweep.py  --  natural-termination Monte Carlo')
    print('=' * 72)
    print(f'  Grid: {len(RR_VALUES)} rr x {len(PHI_VALUES)} phi x '
          f'{len(ALPHA_VALUES)} alpha x {len(SEEDS)} seeds = {total} runs')
    print(f'  MAX_STEPS per run: {MAX_STEPS:,}   CONV_WINDOW: {CONV_WINDOW}   '
          f'CV threshold: {CONV_CV_THRESHOLD}')
    print(f'  CPU cores: {cores}')
    print()

    results = []
    start = time.time()

    with multiprocessing.Pool(processes=cores, maxtasksperchild=20) as pool:
        for i, result in enumerate(pool.imap_unordered(_run_single, tasks)):
            results.append(result)
            elapsed = time.time() - start
            rate    = (i + 1) / elapsed if elapsed > 0 else 0
            eta     = int((total - (i + 1)) / rate) if rate > 0 else 0
            term    = result['termination_reason'][:3].upper()
            print(
                f'  [{i+1:>5}/{total}] rr={result["rr"]:.3f} phi={result["phi"]:.1f} '
                f'alpha={result["alpha"]:.1f} seed={result["seed"]} '
                f'-> {term} @ step {result["steps_run"]:,} '
                f'| {rate:.2f} runs/s  ETA {str(timedelta(seconds=eta))}    ',
                end='\r'
            )

    print()
    _print_summary(results)
    print()

    os.makedirs(DATA_DIR, exist_ok=True)
    out_path = os.path.join(DATA_DIR, OUT_FILE)
    with open(out_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(results)

    elapsed = time.time() - start
    print(f'  Done in {elapsed:.0f}s ({elapsed/60:.1f} min).')
    print(f'  Data -> {out_path}  ({total} rows)')
    print('=' * 72)
    return results


if __name__ == '__main__':
    multiprocessing.freeze_support()
    run()
