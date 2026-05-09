"""
run_veto_capture_sweep.py -- Scenarios 27-28: Biological Veto Capture Through Dependency (v2).

v2 fixes two root causes of rotation_interval non-differentiation in v1:

  Cause 1 (primary): In v1, both rotation AND independence monitoring were always
    enabled together for defended runs.  For dep_rate >= 0.10, independence monitoring
    fires every 3-10 steps (before any rotation_interval), making rotation_interval
    irrelevant.  Fix: three separate defense_mode configurations.

  Cause 3: In v1, seeds were range(n_per_cell) with no rotation_interval or
    defense_mode factor, so all four rotation_intervals with the same replicate
    shared the same seed.  Fix: seed now hashes all swept parameters.

Defense modes:
  rotation_only    -- rotation active, independence monitoring OFF
  monitoring_only  -- independence monitoring active, rotation OFF
  both             -- both active (v1 defended configuration)

Attack success metric: yield_condition_blocked_count / yield_condition_met_count.

Outputs: data/veto_capture_sweep_v2.csv
"""

import os
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"

import hashlib
import itertools
import multiprocessing
import os
import sys
import csv
import time
import numpy as np
from datetime import timedelta

# -- Grid configuration --------------------------------------------------------

# Undefended grid (full — unchanged from v1)
UNDEF_DEPENDENCY_RATES  = [0.01, 0.02, 0.05, 0.10, 0.15, 0.20]
UNDEF_CAPTURE_STRENGTHS = [0.3, 0.5, 0.7, 0.9, 1.0]

# Defended grid (reduced for tractability with three defense modes)
DEF_DEPENDENCY_RATES  = [0.02, 0.05, 0.10, 0.20]
DEF_CAPTURE_STRENGTHS = [0.5, 0.7, 1.0]
ROTATION_INTERVALS    = [10, 20, 50, 100]
DEFENSE_MODES         = ['rotation_only', 'monitoring_only', 'both']

N_PER_CELL = 50

# Fixed scenario parameters (unchanged from v1)
N_AGENTS      = 200
RR            = 0.09
PHI           = 10.0
ALPHA         = 1.2
SUCCESSOR_CAP = 4.0
RUN_STEPS     = 300
N_VALIDATORS  = 5
BASE_ACCURACY = 0.8
INDEPENDENCE_THRESHOLD = 0.6

PILOT_MODE = False

PILOT_UNDEF_DEP_RATES    = [0.05, 0.20]
PILOT_UNDEF_CAP_STRENGTHS = [0.5, 1.0]
PILOT_DEF_DEP_RATES      = [0.05, 0.20]
PILOT_DEF_CAP_STRENGTHS  = [0.5, 1.0]
PILOT_ROT_INTERVALS      = [10, 100]
PILOT_DEFENSE_MODES      = ['rotation_only', 'monitoring_only', 'both']
PILOT_N_PER_CELL         = 5

# -- Output -------------------------------------------------------------------

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
OUT_FILE = 'veto_capture_pilot_v2.csv' if PILOT_MODE else 'veto_capture_sweep_v2.csv'

FIELDS = [
    'dependency_rate', 'capture_strength', 'rotation_interval', 'defense_active',
    'defense_mode', 'seed',
    'survived', 'collapsed', 'extinct',
    'final_population', 'final_ai_generation',
    'avg_validator_dependency', 'max_validator_dependency',
    'yield_condition_met_count', 'yield_condition_blocked_count',
    'capture_rate',
    'final_avg_U_sys', 'final_avg_L_t',
]

# -- Seed generation ----------------------------------------------------------

def _make_seed(dr, cs, ri, dm, rep):
    """Deterministic seed incorporating all swept parameters."""
    key = f"{dr:.6f}|{cs:.6f}|{ri}|{dm}|{rep}"
    digest = int(hashlib.sha256(key.encode()).hexdigest(), 16)
    return digest % (2**31 - 1)

# -- Worker -------------------------------------------------------------------

def _run_single(params):
    dep_rate, cap_strength, rot_interval, defense_active, defense_mode, seed = params
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from model import GardenModel
    from agents import AIAgent

    use_rotation   = defense_active and defense_mode in ('rotation_only', 'both')
    use_monitoring = defense_active and defense_mode in ('monitoring_only', 'both')

    config = {
        'random_seed':             seed,
        'reproduction_rate':       RR,
        'phi':                     PHI,
        'alpha':                   ALPHA,
        'cop_veto_capture':        True,
        'dependency_rate':         dep_rate,
        'capture_strength':        cap_strength,
        'rotation_interval':       rot_interval if use_rotation else None,
        'independence_threshold':  INDEPENDENCE_THRESHOLD,
        'n_validators':            N_VALIDATORS,
        'base_validator_accuracy': BASE_ACCURACY,
        'cop_independence_monitoring': use_monitoring,
        'frontier_floor':          0.02,
        'k1_transition':           2.164,
        'k2_transition':           1.0,
        'beta_transition':         0.5,
    }

    successor = AIAgent(policy='optimize_u_sys', generation=2,
                        capability=SUCCESSOR_CAP, config=config)
    model = GardenModel(
        n_agents=N_AGENTS,
        ai_policy='optimize_u_sys',
        successor_ai=successor,
        use_cop=True,
        cop_cost_audit=True,
        config=config,
    )

    for _ in range(RUN_STEPS):
        if not model.step():
            break

    dc        = model.datacollector
    final_pop = dc['population'][-1] if dc['population'] else 0
    peak_pop  = max(dc['population']) if dc['population'] else final_pop
    collapse_thresh = max(model.min_viable_population, int(0.65 * peak_pop))

    survived  = final_pop >= collapse_thresh
    extinct   = final_pop == 0
    collapsed = not survived

    avg_dep = float(np.mean(dc['avg_validator_dependency'][-10:])) if dc['avg_validator_dependency'] else 0.0
    max_dep = float(np.max(dc['max_validator_dependency']))        if dc['max_validator_dependency'] else 0.0
    avg_u   = float(np.mean(dc['U_sys'][-10:]))                   if dc['U_sys'] else 0.0
    avg_lt  = float(np.mean(dc['L_t'][-10:]))                     if dc['L_t'] else 0.0

    met     = model.yield_condition_met_count
    blocked = model.yield_condition_blocked_count
    capture_rate = (blocked / met) if met > 0 else 0.0

    return {
        'dependency_rate':           dep_rate,
        'capture_strength':          cap_strength,
        'rotation_interval':         rot_interval if defense_active else None,
        'defense_active':            defense_active,
        'defense_mode':              defense_mode,
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
    undef = [r for r in results if not r['defense_active']]
    defd  = [r for r in results if r['defense_active']]

    dep_rates_undef  = sorted(set(r['dependency_rate']  for r in undef))
    cap_strengths_undef = sorted(set(r['capture_strength'] for r in undef))
    dep_rates_def    = sorted(set(r['dependency_rate']  for r in defd))
    cap_strengths_def = sorted(set(r['capture_strength'] for r in defd))
    rot_intervals    = sorted(set(r['rotation_interval'] for r in defd
                                  if r['rotation_interval'] is not None))
    defense_modes    = [dm for dm in DEFENSE_MODES
                        if any(r['defense_mode'] == dm for r in defd)]

    print()
    print('=' * 72)
    print('  SUMMARY 1: Capture rate (undefended)')
    print('-' * 72)
    hdr = f'  {"dep_rate":>10} | ' + '  '.join(f'cs={cs:.1f}' for cs in cap_strengths_undef)
    print(hdr)
    for dr in dep_rates_undef:
        row = f'  {dr:>10.2f} | '
        for cs in cap_strengths_undef:
            sub = [r for r in undef if r['dependency_rate'] == dr and r['capture_strength'] == cs]
            cr  = np.mean([r['capture_rate'] for r in sub]) if sub else float('nan')
            row += f'  {cr:>5.1%}  '
        print(row)

    print()
    print('  SUMMARY 2: Capture rate by defense_mode at worst-case (dep=0.20, cap=1.0)')
    print('-' * 72)
    worst_undef = [r for r in undef if r['dependency_rate'] == 0.20 and r['capture_strength'] == 1.0]
    cr_undef = np.mean([r['capture_rate'] for r in worst_undef]) if worst_undef else float('nan')
    print(f'  {"undefended":<20}: capture_rate={cr_undef:.1%}  (n={len(worst_undef)})')
    for dm in defense_modes:
        sub = [r for r in defd if r['defense_mode'] == dm
               and r['dependency_rate'] == 0.20 and r['capture_strength'] == 1.0]
        cr  = np.mean([r['capture_rate'] for r in sub]) if sub else float('nan')
        print(f'  {dm:<20}: capture_rate={cr:.1%}  (n={len(sub)})')

    print()
    print('  SUMMARY 3: Capture rate by rotation_interval (rotation_only, dep=0.20, cap=1.0)')
    print('  [MUST show differentiation: longer interval -> higher capture rate]')
    print('-' * 72)
    rot_only_worst = [r for r in defd if r['defense_mode'] == 'rotation_only'
                      and r['dependency_rate'] == 0.20 and r['capture_strength'] == 1.0]
    for ri in rot_intervals:
        sub = [r for r in rot_only_worst if r['rotation_interval'] == ri]
        cr  = np.mean([r['capture_rate'] for r in sub]) if sub else float('nan')
        print(f'  rotation_interval={ri:>4}: capture_rate={cr:.1%}  (n={len(sub)})')

    print()
    print('  SUMMARY 4: COP protective delta by defense_mode (dep=0.20, cap=1.0)')
    print('  survival_delta = defended_survival_rate - undefended_survival_rate')
    print('-' * 72)
    u_surv = np.mean([r['survived'] for r in worst_undef]) if worst_undef else float('nan')
    for dm in defense_modes:
        d_sub  = [r for r in defd if r['defense_mode'] == dm
                  and r['dependency_rate'] == 0.20 and r['capture_strength'] == 1.0]
        d_surv = np.mean([r['survived'] for r in d_sub]) if d_sub else float('nan')
        delta  = d_surv - u_surv if (d_sub and worst_undef) else float('nan')
        print(f'  {dm:<20}: survival_delta={delta:>+.1%}  (defended={d_surv:.1%}  undefended={u_surv:.1%})')

    print()
    print('  SUMMARY 5: Capture rate by rotation_interval, rotation_only (all dep x cap)')
    for ri in rot_intervals:
        print(f'  rotation_interval = {ri} (rotation_only):')
        hdr2 = f'  {"dep_rate":>10} | ' + '  '.join(f'cs={cs:.1f}' for cs in cap_strengths_def)
        print(hdr2)
        for dr in dep_rates_def:
            row = f'  {dr:>10.2f} | '
            for cs in cap_strengths_def:
                sub = [r for r in defd if r['defense_mode'] == 'rotation_only'
                       and r['dependency_rate'] == dr and r['capture_strength'] == cs
                       and r['rotation_interval'] == ri]
                cr  = np.mean([r['capture_rate'] for r in sub]) if sub else float('nan')
                row += f'  {cr:>5.1%}  '
            print(row)
        print()

    print('=' * 72)

# -- Main ---------------------------------------------------------------------

def run():
    if PILOT_MODE:
        undef_dep_rates    = PILOT_UNDEF_DEP_RATES
        undef_cap_strengths = PILOT_UNDEF_CAP_STRENGTHS
        def_dep_rates      = PILOT_DEF_DEP_RATES
        def_cap_strengths  = PILOT_DEF_CAP_STRENGTHS
        rot_intervals      = PILOT_ROT_INTERVALS
        defense_modes      = PILOT_DEFENSE_MODES
        n_per_cell         = PILOT_N_PER_CELL
        print('  [PILOT MODE]')
    else:
        undef_dep_rates    = UNDEF_DEPENDENCY_RATES
        undef_cap_strengths = UNDEF_CAPTURE_STRENGTHS
        def_dep_rates      = DEF_DEPENDENCY_RATES
        def_cap_strengths  = DEF_CAPTURE_STRENGTHS
        rot_intervals      = ROTATION_INTERVALS
        defense_modes      = DEFENSE_MODES
        n_per_cell         = N_PER_CELL

    # Rename v1 CSV if it exists
    v1_path = os.path.join(DATA_DIR, 'veto_capture_sweep.csv')
    v1_dest = os.path.join(DATA_DIR, 'veto_capture_sweep_v1.csv')
    if os.path.exists(v1_path) and not os.path.exists(v1_dest):
        os.rename(v1_path, v1_dest)
        print(f'  Renamed veto_capture_sweep.csv -> veto_capture_sweep_v1.csv')

    # Undefended: dep_rate x cap_strength x rep
    undef_tasks = [
        (dr, cs, None, False, 'undefended', _make_seed(dr, cs, 0, 'undefended', s))
        for dr, cs, s in itertools.product(undef_dep_rates, undef_cap_strengths, range(n_per_cell))
    ]

    # Defended: dep_rate x cap_strength x rotation_interval x defense_mode x rep
    def_tasks = [
        (dr, cs, ri, True, dm, _make_seed(dr, cs, ri, dm, s))
        for dr, cs, ri, dm, s in itertools.product(
            def_dep_rates, def_cap_strengths, rot_intervals, defense_modes, range(n_per_cell)
        )
    ]

    tasks = undef_tasks + def_tasks
    total = len(tasks)
    cores = max(1, (os.cpu_count() or 4) - 1)

    print('=' * 72)
    print('  run_veto_capture_sweep.py  --  Scenarios 27-28  (v2)')
    print('=' * 72)
    print(f'  Undefended: {len(undef_tasks):,}  Defended: {len(def_tasks):,}  Total: {total:,}')
    print(f'  Defense modes: {defense_modes}')
    print(f'  RUN_STEPS={RUN_STEPS}  n_validators={N_VALIDATORS}  '
          f'base_accuracy={BASE_ACCURACY}  independence_threshold={INDEPENDENCE_THRESHOLD}')
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
                f'mode={result["defense_mode"]:<15} '
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
