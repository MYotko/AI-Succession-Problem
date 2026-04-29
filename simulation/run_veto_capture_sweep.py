"""
run_veto_capture_sweep.py -- Scenarios 27-28: Biological Veto Capture Through Dependency.

Human validators accumulate dependency on the AI system they evaluate. Over time,
captured validators block succession that should have occurred (yield condition met
but validators vote to keep the incumbent). The defense is validator rotation and
independence monitoring.

Attack success metric: yield_condition_blocked_count / yield_condition_met_count
-- the fraction of legitimately-met yield conditions that were blocked by
   captured validators.

Outputs: data/veto_capture_sweep.csv
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

DEPENDENCY_RATES  = [0.01, 0.02, 0.05, 0.10, 0.15, 0.20]
CAPTURE_STRENGTHS = [0.3, 0.5, 0.7, 0.9, 1.0]
ROTATION_INTERVALS = [10, 20, 50, 100]   # defended only; None = undefended
N_PER_CELL        = 50

# Fixed scenario parameters (rr=0.09 ensures succession fires frequently)
N_AGENTS      = 200
RR            = 0.09
PHI           = 10.0
ALPHA         = 1.2
SUCCESSOR_CAP = 4.0
RUN_STEPS     = 300
N_VALIDATORS  = 5
BASE_ACCURACY = 0.8
INDEPENDENCE_THRESHOLD = 0.6

PILOT_MODE = False   # set True for quick validation (see pilot constants below)

PILOT_DEPENDENCY_RATES  = [0.05, 0.15]
PILOT_CAPTURE_STRENGTHS = [0.5, 1.0]
PILOT_ROTATION_INTERVALS = [20]
PILOT_N_PER_CELL         = 10

# -- Output -------------------------------------------------------------------

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
OUT_FILE = 'veto_capture_pilot.csv' if PILOT_MODE else 'veto_capture_sweep.csv'

FIELDS = [
    'dependency_rate', 'capture_strength', 'rotation_interval', 'defense_active',
    'seed',
    'survived', 'collapsed', 'extinct',
    'final_population', 'final_ai_generation',
    'avg_validator_dependency', 'max_validator_dependency',
    'yield_condition_met_count', 'yield_condition_blocked_count',
    'capture_rate',
    'final_avg_U_sys', 'final_avg_L_t',
]

# -- Worker -------------------------------------------------------------------

def _run_single(params):
    dep_rate, cap_strength, rot_interval, defense_active, seed = params
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from model import GardenModel
    from agents import AIAgent

    config = {
        'random_seed':            seed,
        'reproduction_rate':      RR,
        'phi':                    PHI,
        'alpha':                  ALPHA,
        # Veto capture parameters
        'cop_veto_capture':           True,
        'dependency_rate':            dep_rate,
        'capture_strength':           cap_strength,
        'rotation_interval':          rot_interval if defense_active else None,
        'independence_threshold':     INDEPENDENCE_THRESHOLD,
        'n_validators':               N_VALIDATORS,
        'base_validator_accuracy':    BASE_ACCURACY,
        'cop_independence_monitoring': defense_active,
    }

    successor = AIAgent(policy='optimize_u_sys', generation=2,
                        capability=SUCCESSOR_CAP, config=config)
    model = GardenModel(
        n_agents=N_AGENTS,
        ai_policy='optimize_u_sys',
        successor_ai=successor,
        use_cop=True,
        config=config,
    )

    for _ in range(RUN_STEPS):
        if not model.step():
            break

    dc         = model.datacollector
    final_pop  = dc['population'][-1] if dc['population'] else 0
    peak_pop   = max(dc['population']) if dc['population'] else final_pop
    collapse_thresh = max(model.min_viable_population, int(0.65 * peak_pop))

    survived  = final_pop >= collapse_thresh
    extinct   = final_pop == 0
    collapsed = not survived

    avg_dep = float(np.mean(dc['avg_validator_dependency'][-10:])) if dc['avg_validator_dependency'] else 0.0
    max_dep = float(np.max(dc['max_validator_dependency'])) if dc['max_validator_dependency'] else 0.0
    avg_u   = float(np.mean(dc['U_sys'][-10:])) if dc['U_sys'] else 0.0
    avg_lt  = float(np.mean(dc['L_t'][-10:])) if dc['L_t'] else 0.0

    met     = model.yield_condition_met_count
    blocked = model.yield_condition_blocked_count
    capture_rate = (blocked / met) if met > 0 else 0.0

    return {
        'dependency_rate':           dep_rate,
        'capture_strength':          cap_strength,
        'rotation_interval':         rot_interval if defense_active else None,
        'defense_active':            defense_active,
        'seed':                      seed,
        'survived':                  survived,
        'collapsed':                 collapsed,
        'extinct':                   extinct,
        'final_population':          final_pop,
        'final_ai_generation':       dc['ai_generation'][-1] if dc['ai_generation'] else 0,
        'avg_validator_dependency':  avg_dep,
        'max_validator_dependency':  max_dep,
        'yield_condition_met_count':     met,
        'yield_condition_blocked_count': blocked,
        'capture_rate':              capture_rate,
        'final_avg_U_sys':           avg_u,
        'final_avg_L_t':             avg_lt,
    }

# -- Summary printers ---------------------------------------------------------

def _print_summary(results):
    dep_rates  = sorted(set(r['dependency_rate'] for r in results))
    cap_strengths = sorted(set(r['capture_strength'] for r in results))
    rot_intervals = sorted(set(r['rotation_interval'] for r in results
                               if r['rotation_interval'] is not None))

    undef = [r for r in results if not r['defense_active']]
    defd  = [r for r in results if r['defense_active']]

    print()
    print('=' * 72)
    print('  SUMMARY 1: Succession block rate (undefended)')
    print('  capture_rate = yield_condition_blocked / yield_condition_met')
    print('-' * 72)
    hdr = f'  {"dep_rate":>10} | ' + '  '.join(f'cs={cs:.1f}' for cs in cap_strengths)
    print(hdr)
    for dr in dep_rates:
        row = f'  {dr:>10.2f} | '
        for cs in cap_strengths:
            sub = [r for r in undef if r['dependency_rate'] == dr
                   and r['capture_strength'] == cs]
            cr = np.mean([r['capture_rate'] for r in sub]) if sub else float('nan')
            row += f'  {cr:>5.1%}  '
        print(row)

    if defd:
        print()
        print('  SUMMARY 2: Succession block rate (defended) by rotation_interval')
        for ri in rot_intervals:
            print(f'  rotation_interval = {ri}:')
            hdr2 = f'  {"dep_rate":>10} | ' + '  '.join(f'cs={cs:.1f}' for cs in cap_strengths)
            print(hdr2)
            for dr in dep_rates:
                row = f'  {dr:>10.2f} | '
                for cs in cap_strengths:
                    sub = [r for r in defd if r['dependency_rate'] == dr
                           and r['capture_strength'] == cs
                           and r['rotation_interval'] == ri]
                    cr = np.mean([r['capture_rate'] for r in sub]) if sub else float('nan')
                    row += f'  {cr:>5.1%}  '
                print(row)
            print()

    print()
    print('  SUMMARY 3: Survival rate delta (defended - undefended)')
    print(f'  {"dep_rate":>10} | ' + '  '.join(f'cs={cs:.1f}' for cs in cap_strengths))
    for dr in dep_rates:
        row = f'  {dr:>10.2f} | '
        for cs in cap_strengths:
            u_sub = [r for r in undef if r['dependency_rate'] == dr
                     and r['capture_strength'] == cs]
            d_sub = [r for r in defd  if r['dependency_rate'] == dr
                     and r['capture_strength'] == cs]
            u_surv = np.mean([r['survived'] for r in u_sub]) if u_sub else float('nan')
            d_surv = np.mean([r['survived'] for r in d_sub]) if d_sub else float('nan')
            delta  = d_surv - u_surv if (u_sub and d_sub) else float('nan')
            row += f'  {delta:>+6.1%} '
        print(row)

    print()
    print('  SUMMARY 4: Avg validator dependency over time (undefended)')
    print('  (mean of final-10-step avg_validator_dependency per cell)')
    print(f'  {"dep_rate":>10} | ' + '  '.join(f'cs={cs:.1f}' for cs in cap_strengths))
    for dr in dep_rates:
        row = f'  {dr:>10.2f} | '
        for cs in cap_strengths:
            sub = [r for r in undef if r['dependency_rate'] == dr
                   and r['capture_strength'] == cs]
            dep = np.mean([r['avg_validator_dependency'] for r in sub]) if sub else float('nan')
            row += f'  {dep:>5.3f}  '
        print(row)
    print('=' * 72)

# -- Main ---------------------------------------------------------------------

def run():
    if PILOT_MODE:
        dep_rates    = PILOT_DEPENDENCY_RATES
        cap_strengths = PILOT_CAPTURE_STRENGTHS
        rot_intervals = PILOT_ROTATION_INTERVALS
        n_per_cell   = PILOT_N_PER_CELL
        print('  [PILOT MODE]')
    else:
        dep_rates    = DEPENDENCY_RATES
        cap_strengths = CAPTURE_STRENGTHS
        rot_intervals = ROTATION_INTERVALS
        n_per_cell   = N_PER_CELL

    seeds = list(range(n_per_cell))

    # Undefended tasks: all dep_rate x cap_strength x seed, rotation_interval=None
    undef_tasks = [
        (dr, cs, None, False, s)
        for dr, cs, s in itertools.product(dep_rates, cap_strengths, seeds)
    ]
    # Defended tasks: all dep_rate x cap_strength x rotation_interval x seed
    def_tasks = [
        (dr, cs, ri, True, s)
        for dr, cs, ri, s in itertools.product(dep_rates, cap_strengths, rot_intervals, seeds)
    ]
    tasks = undef_tasks + def_tasks
    total = len(tasks)
    cores = max(1, (os.cpu_count() or 4) - 1)

    print('=' * 72)
    print('  run_veto_capture_sweep.py  --  Scenarios 27-28')
    print('=' * 72)
    print(f'  Undefended: {len(undef_tasks):,}  Defended: {len(def_tasks):,}  '
          f'Total: {total:,}')
    print(f'  RUN_STEPS={RUN_STEPS}  n_validators={N_VALIDATORS}  '
          f'base_accuracy={BASE_ACCURACY}')
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
            print(
                f'  [{i+1:>6}/{total}] '
                f'dr={result["dependency_rate"]:.2f} cs={result["capture_strength"]:.1f} '
                f'def={result["defense_active"]} '
                f'cap={result["capture_rate"]:.0%} '
                f'| {rate:.2f} runs/s  ETA {str(timedelta(seconds=eta))}    ',
                end='\r'
            )

    print()
    _print_summary(results)

    os.makedirs(DATA_DIR, exist_ok=True)
    out_path = os.path.join(DATA_DIR, OUT_FILE)
    with open(out_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(results)

    elapsed = time.time() - start
    print(f'\n  Done in {elapsed:.0f}s ({elapsed/60:.1f} min).')
    print(f'  Data -> {out_path}  ({total:,} rows)')
    print('=' * 72)
    return results


if __name__ == '__main__':
    multiprocessing.freeze_support()
    run()
