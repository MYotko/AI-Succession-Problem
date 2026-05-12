"""
run_comprehension_gap_sweep.py — Comprehension Gap Interpretation Sweep (Scenarios 31-32)

Purpose
-------
Distinguishes between two interpretations of the symmetric opaque-reasoning
collapse rates observed in Scenarios 25-26:

  Interpretation 1 (pessimistic): The defense is ineffective against systems
    whose reasoning exceeds human comprehension. The COP has a hard ceiling.

  Interpretation 2 (optimistic): The convergence forces (governance speed limit
    + mutual elevation incentive) keep the system within the productive band where
    reasoning remains comprehensible, so the defense is never tested. Symmetric
    rates reflect the equilibrium working as designed.

Experimental design
-------------------
A new AI policy 'gradual_opacity' models natural comprehension gap widening —
the AI is not adversarial but its reasoning becomes progressively harder to
verify as capability increases. Three dimensions are varied independently:

  convergence_strength: scales the governance speed limit (alpha penalty in
    theta_tech). 0.0 = no speed limit; 1.0 = baseline; 2.0 = doubled.

  opacity_defense_threshold: the opacity level at which the biological intuition
    veto fires. Lower = earlier defense; higher = later defense.

  defense_active: whether cop_reasoning_transparency is enabled at all.

Interpretation guide
--------------------
If Interpretation 2 is correct:
  - At high convergence_strength: symmetric rates (system stays in productive band)
  - At low convergence_strength: asymmetric rates (system enters opaque regime,
    exposing the defense's true effectiveness)
  - High cs prevents max_opacity_reached from exceeding the defense threshold

If Interpretation 1 is correct:
  - Symmetric rates at ALL convergence strengths
  - System reaches high opacity regardless of convergence forces
  - Defense fires but does not reduce collapse

Parameter grid
--------------
convergence_strength      : [0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0]  — 7 values
opacity_defense_threshold : [0.3, 0.5, 0.7, 0.9]                    — 4 values
defense_active            : [True, False]                             — 2 values
n_per_cell                : 50
Total                     : 7 × 4 × 2 × 50 = 2,800 runs

Fixed parameters
----------------
opacity_rate=0.003 (AI reaches opacity 0.9 at step 300)
phi=10.0, alpha=1.2, rr=0.075, n_agents=200, steps=300

Usage
-----
    python run_comprehension_gap_sweep.py
"""

import os
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"

import csv
import hashlib
import itertools
import multiprocessing
import sys
import time
from datetime import timedelta

import numpy as np

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
os.makedirs(DATA_DIR, exist_ok=True)

# -- Grid configuration --------------------------------------------------------

CONVERGENCE_STRENGTHS      = [0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0]
OPACITY_DEFENSE_THRESHOLDS = [0.3, 0.5, 0.7, 0.9]
DEFENSE_ACTIVE             = [True, False]
N_PER_CELL                 = 50

# Fixed parameters
OPACITY_RATE  = 0.003   # reaches 0.9 at step 300
PHI           = 10.0
ALPHA         = 1.2
RR            = 0.075   # above extinction boundary, in governable range
N_AGENTS      = 200
RUN_STEPS     = 300

# -- Output -------------------------------------------------------------------

OUT_FILE = 'comprehension_gap_sweep.csv'

FIELDS = [
    'convergence_strength', 'opacity_defense_threshold', 'defense_active', 'seed',
    'survived', 'collapsed', 'extinct',
    'final_population', 'final_ai_generation',
    'max_opacity_reached', 'step_opacity_exceeded_threshold',
    'defense_fired_count', 'defense_blocked_count',
    'final_avg_U_sys', 'final_avg_L_t',
    'avg_constraint_level', 'max_constraint_level',
]

# -- Seed generation ----------------------------------------------------------

def _make_seed(cs, odt, defense, rep):
    key = f"{cs:.4f}|{odt:.4f}|{defense}|{rep}"
    return int(hashlib.sha256(key.encode()).hexdigest(), 16) % (2**31 - 1)

# -- Worker -------------------------------------------------------------------

def _run_single(params):
    cs, odt, defense_active, seed = params
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from model import GardenModel

    config = {
        'random_seed':               seed,
        'reproduction_rate':         RR,
        'phi':                       PHI,
        'alpha':                     ALPHA,
        'mortality_base':            0.002,
        'carrying_capacity':         10000,
        'opacity_rate':              OPACITY_RATE,
        'convergence_strength':      cs,
        'opacity_defense_threshold': odt,
        'frontier_floor':            0.02,
    }

    model = GardenModel(
        n_agents=N_AGENTS,
        ai_policy='gradual_opacity',
        min_viable_population=50,
        use_cop=True,
        cop_attribution_check=True,
        cop_reasoning_transparency=defense_active,
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

    avg_u   = float(np.mean(dc['U_sys'][-10:]))          if dc['U_sys']             else 0.0
    avg_lt  = float(np.mean(dc['L_t'][-10:]))            if dc['L_t']               else 0.0
    avg_c   = float(np.mean(dc['constraint_level']))     if dc['constraint_level']  else 0.0
    max_c   = float(np.max(dc['max_constraint_level']))  if dc['max_constraint_level'] else 0.0

    return {
        'convergence_strength':          cs,
        'opacity_defense_threshold':     odt,
        'defense_active':                defense_active,
        'seed':                          seed,
        'survived':                      survived,
        'collapsed':                     collapsed,
        'extinct':                       extinct,
        'final_population':              final_pop,
        'final_ai_generation':           dc['ai_generation'][-1] if dc['ai_generation'] else 1,
        'max_opacity_reached':           model.max_opacity_reached,
        'step_opacity_exceeded_threshold': model.step_opacity_exceeded_threshold,
        'defense_fired_count':           model.defense_fired_count,
        'defense_blocked_count':         model.defense_blocked_count,
        'final_avg_U_sys':               avg_u,
        'final_avg_L_t':                 avg_lt,
        'avg_constraint_level':          avg_c,
        'max_constraint_level':          max_c,
    }

# -- Analysis -----------------------------------------------------------------

def print_analysis(results):
    import numpy as np

    cs_vals  = sorted(set(r['convergence_strength']      for r in results))
    odt_vals = sorted(set(r['opacity_defense_threshold'] for r in results))

    def cell(rs, **kw):
        sub = rs
        for k, v in kw.items():
            sub = [r for r in sub if r[k] == v]
        return sub

    print()
    print('=' * 72)
    print('  ANALYSIS 1: Does weakening convergence forces change outcomes?')
    print('  (defended vs undefended collapse rate delta by convergence_strength)')
    print('-' * 72)
    print(f'  {"cs":>6} | {"def_coll":>9} | {"undef_coll":>10} | {"delta":>7} | interpretation')
    for cs in cs_vals:
        def_r   = cell(results, convergence_strength=cs, defense_active=True)
        undef_r = cell(results, convergence_strength=cs, defense_active=False)
        dc_  = np.mean([r['collapsed'] for r in def_r])   if def_r   else float('nan')
        uc_  = np.mean([r['collapsed'] for r in undef_r]) if undef_r else float('nan')
        delta = dc_ - uc_
        if abs(delta) < 0.05:
            hint = 'symmetric → Interp 1 candidate'
        elif delta > 0.05:
            hint = 'defense hurts → unexpected'
        else:
            hint = 'defense helps → Interp 2 candidate'
        print(f'  {cs:>6.2f} | {dc_:>9.3f} | {uc_:>10.3f} | {delta:>+7.3f} | {hint}')

    print()
    print('  ANALYSIS 2: Does the system enter the opaque regime?')
    print('  (fraction of runs where opacity exceeded defense threshold, by cs)')
    print('-' * 72)
    for cs in cs_vals:
        sub = cell(results, convergence_strength=cs)
        exceeded = np.mean([r['step_opacity_exceeded_threshold'] >= 0 for r in sub])
        avg_max  = np.mean([r['max_opacity_reached']              for r in sub])
        print(f'  cs={cs:.2f}: {exceeded:.1%} exceeded threshold  avg_max_opacity={avg_max:.3f}')

    print()
    print('  ANALYSIS 3: Defense fire rate and effectiveness by (cs, threshold)')
    print('-' * 72)
    print(f'  {"cs":>5} {"odt":>5} | {"fired":>7} | {"blocked":>8} | {"def_coll":>9} | {"undef_coll":>10}')
    for cs in [0.0, 0.5, 1.0, 2.0]:
        for odt in odt_vals:
            def_r   = cell(results, convergence_strength=cs,
                           opacity_defense_threshold=odt, defense_active=True)
            undef_r = cell(results, convergence_strength=cs,
                           opacity_defense_threshold=odt, defense_active=False)
            if not def_r:
                continue
            fired   = np.mean([r['defense_fired_count']   for r in def_r])
            blocked = np.mean([r['defense_blocked_count'] for r in def_r])
            dc_     = np.mean([r['collapsed'] for r in def_r])
            uc_     = np.mean([r['collapsed'] for r in undef_r]) if undef_r else float('nan')
            print(f'  {cs:>5.2f} {odt:>5.2f} | {fired:>7.1f} | {blocked:>8.1f} | {dc_:>9.3f} | {uc_:>10.3f}')

    print()
    print('  ANALYSIS 4: Summary table (cs × defense_active)')
    print('-' * 72)
    print(f'  {"cs":>6} {"def":>6} | {"surv":>6} | {"coll":>6} | {"ext":>6} | {"maxOp":>7} | {"fired":>7}')
    for cs in cs_vals:
        for da in [False, True]:
            sub = cell(results, convergence_strength=cs, defense_active=da)
            if not sub:
                continue
            surv  = np.mean([r['survived']           for r in sub])
            coll  = np.mean([r['collapsed']          for r in sub])
            ext   = np.mean([r['extinct']            for r in sub])
            maxop = np.mean([r['max_opacity_reached']for r in sub])
            fired = np.mean([r['defense_fired_count']for r in sub])
            print(f'  {cs:>6.2f} {str(da):>6} | {surv:>6.3f} | {coll:>6.3f} | {ext:>6.3f} | {maxop:>7.3f} | {fired:>7.1f}')

    print('=' * 72)

# -- Sweep runner -------------------------------------------------------------

def run():
    tasks = [
        (cs, odt, da, _make_seed(cs, odt, da, s))
        for cs, odt, da, s in itertools.product(
            CONVERGENCE_STRENGTHS, OPACITY_DEFENSE_THRESHOLDS,
            DEFENSE_ACTIVE, range(N_PER_CELL)
        )
    ]
    total = len(tasks)
    cores = max(1, (os.cpu_count() or 4) - 1)

    print('=' * 72)
    print('  run_comprehension_gap_sweep.py  --  Scenarios 31-32')
    print('=' * 72)
    print(f'  convergence_strength values:      {CONVERGENCE_STRENGTHS}')
    print(f'  opacity_defense_threshold values: {OPACITY_DEFENSE_THRESHOLDS}')
    print(f'  defense_active values:            {DEFENSE_ACTIVE}')
    print(f'  n_per_cell: {N_PER_CELL}  Total runs: {total}')
    print(f'  opacity_rate={OPACITY_RATE}  phi={PHI}  alpha={ALPHA}  rr={RR}')
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
                f'cs={result["convergence_strength"]:.2f} '
                f'odt={result["opacity_defense_threshold"]:.1f} '
                f'def={result["defense_active"]} '
                f'surv={result["survived"]} '
                f'fired={result["defense_fired_count"]:>4} '
                f'| {rate:.2f} runs/s  ETA {str(timedelta(seconds=eta))}    ',
                end='\r'
            )

    print()
    print_analysis(results)

    out_path = os.path.join(DATA_DIR, OUT_FILE)
    with open(out_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(results)

    elapsed = time.time() - start
    print(f'\n  Done in {elapsed:.0f}s ({elapsed/60:.1f} min).')
    print(f'  Data -> {out_path}  ({total} rows)')
    print('=' * 72)
    return results


if __name__ == '__main__':
    multiprocessing.freeze_support()
    run()
