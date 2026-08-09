#!/usr/bin/env python3
"""
run_comprehension_gap_powered_arm.py -- powered discriminating arm

A diagnostic for the Opaque Reasoning pair, Scenarios 21-22. Not a catalog
scenario and it has no scenario pair of its own.

Purpose
-------
Answer the question the prior extension arm could not: does the
reasoning-transparency defense reduce harm when the comprehension gap widens
naturally rather than adversarially, at an effect size that would matter to the
framework claim?

The prior arm registered a 10 percentage point threshold with no power
calculation, ran at n=50 per cell, and landed on exactly 10.00 points with
Fisher p = 0.395. The criterion was met and meant nothing. This arm fixes the
method: the minimum effect of interest is fixed first from what would matter,
sample size follows from the power to detect it, and the threshold is written
last.

Design is pre-registered in
simulation/diagnostics/comprehension_gap_powered_arm_note.md, written before any
data from this arm existed. Read that note before interpreting any output here.

Key design points, summarized
-----------------------------
Minimum effect of interest: 20 percentage points on extinction, 15 percent of
the undefended mean on final population. Justified against the framework's
published defense effects for comparable vectors, which run 92 to 100 points.

n = 100 per cell, from 80 percent power, two-sided alpha 0.05, worst case 97
across the plausible base-rate range.

Co-primary outcomes: extinction and final population. Collapse is secondary
because it is a threshold on a continuous quantity and is censored at both ends
of this ladder. Collapse means final population below the larger of the minimum
viable population and 65 percent of that run's own peak.

opacity_accum_final is the uncensored opacity accumulator and is the only
opacity measure used for cross-state comparison. max_opacity_reached is censored
at 0.95: a value of 0.95 means at or above 0.95, not equal to it.

Rungs: reproduction_rate 0.068, 0.070, 0.072, 0.074. Even 0.002 spacing across
the interval between 0.066, which produced 72 percent undefended collapse, and
0.075, which produced none. Both endpoints are already measured and are excluded.
Held at convergence_strength 0.0 and opacity_defense_threshold 0.3, the setting
that presses the defense hardest. No other axes.

Known structural limitation, recorded before running: extinction turns on below
this range, not inside it. If extinction is zero in both arms at every rung that
is a structural zero, not a powered null, and it supports neither reading. See
section 6 of the note.

Boundary regime: runaway_threshold is 0.2, not the default 1.5. This arm
characterizes behavior near the runaway boundary and does not describe default
calibration. See default_regime_convergence_inertness.md.

Usage
-----
    python run_comprehension_gap_powered_arm.py
"""

import os
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"

import csv
import hashlib
import multiprocessing
import sys
import time

import numpy as np

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
os.makedirs(DATA_DIR, exist_ok=True)

# -- Pre-registered grid -------------------------------------------------------

REPRODUCTION_RATES = [0.068, 0.070, 0.072, 0.074]
DEFENSE_ACTIVE     = [False, True]
N_PER_CELL         = 100

CONVERGENCE_STRENGTH      = 0.0
OPACITY_DEFENSE_THRESHOLD = 0.3

# Fixed parameters, matching the boundary-regime configuration.
OPACITY_RATE          = 0.003
OPACITY_REFERENCE_L_T = 0.43
RUNAWAY_THRESHOLD     = 0.2
PHI                   = 10.0
ALPHA                 = 1.2
N_AGENTS              = 200
RUN_STEPS             = 300

OUT_FILE = 'comprehension_gap_powered_arm.csv'

FIELDS = [
    'reproduction_rate', 'defense_active', 'seed',
    'extinct', 'final_population',           # co-primary
    'collapsed', 'survived',                 # secondary
    'opacity_accum_final',                   # uncensored
    'max_opacity_reached',                   # censored at 0.95
    'step_opacity_exceeded_threshold',
    'defense_fired_count', 'defense_blocked_count',
    'final_ai_generation', 'steps_completed',
    'final_avg_U_sys', 'final_avg_L_t',
]


def _make_seed(rr, defense, rep):
    key = f"powered|{rr:.4f}|{defense}|{rep}"
    return int(hashlib.sha256(key.encode()).hexdigest(), 16) % (2 ** 31 - 1)


def _run_single(params):
    rr, defense_active, seed = params
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from model import GardenModel

    config = {
        'random_seed':               seed,
        'reproduction_rate':         rr,
        'phi':                       PHI,
        'alpha':                     ALPHA,
        'mortality_base':            0.002,
        'carrying_capacity':         10000,
        'opacity_rate':              OPACITY_RATE,
        'convergence_strength':      CONVERGENCE_STRENGTH,
        'opacity_defense_threshold': OPACITY_DEFENSE_THRESHOLD,
        'frontier_floor':            0.02,
        'opacity_reference_l_t':     OPACITY_REFERENCE_L_T,
        'runaway_threshold':         RUNAWAY_THRESHOLD,
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

    dc = model.datacollector
    final_pop = len(model.schedule)
    peak_pop = max(dc['population']) if dc['population'] else final_pop
    collapse_threshold = max(model.min_viable_population, int(0.65 * peak_pop))

    return {
        'reproduction_rate':               rr,
        'defense_active':                  defense_active,
        'seed':                            seed,
        'extinct':                         final_pop == 0,
        'final_population':                final_pop,
        'collapsed':                       final_pop < collapse_threshold,
        'survived':                        final_pop >= collapse_threshold,
        'opacity_accum_final':             float(getattr(model.ai, '_opacity_accum', 0.0)),
        'max_opacity_reached':             model.max_opacity_reached,
        'step_opacity_exceeded_threshold': model.step_opacity_exceeded_threshold,
        'defense_fired_count':             model.defense_fired_count,
        'defense_blocked_count':           model.defense_blocked_count,
        'final_ai_generation':             dc['ai_generation'][-1] if dc['ai_generation'] else 1,
        'steps_completed':                 len(dc['population']),
        'final_avg_U_sys':                 float(np.mean(dc['U_sys'])) if dc['U_sys'] else 0.0,
        'final_avg_L_t':                   float(np.mean(dc['L_t'])) if dc['L_t'] else 0.0,
    }


def run():
    tasks = [
        (rr, d, _make_seed(rr, d, rep))
        for rr in REPRODUCTION_RATES
        for d in DEFENSE_ACTIVE
        for rep in range(N_PER_CELL)
    ]
    total = len(tasks)
    cores = max(1, (os.cpu_count() or 4) - 1)

    print('=' * 72)
    print('  run_comprehension_gap_powered_arm.py  --  diagnostic for Scenarios 21-22')
    print('  boundary-regime characterization: runaway_threshold lowered to '
          f'{RUNAWAY_THRESHOLD}; does NOT describe default calibration')
    print('=' * 72)
    print(f'  reproduction_rate rungs: {REPRODUCTION_RATES}')
    print(f'  defense_active:          {DEFENSE_ACTIVE}')
    print(f'  n per cell:              {N_PER_CELL}   total runs: {total}')
    print(f'  cs={CONVERGENCE_STRENGTH}  odt={OPACITY_DEFENSE_THRESHOLD}  '
          f'phi={PHI}  alpha={ALPHA}')
    print(f'  workers: {cores}')
    print()

    t0 = time.time()
    results = []
    with multiprocessing.Pool(cores) as pool:
        for i, r in enumerate(pool.imap_unordered(_run_single, tasks, chunksize=4), 1):
            results.append(r)
            if i % 100 == 0 or i == total:
                el = time.time() - t0
                rate = i / el if el > 0 else 0
                eta = (total - i) / rate if rate > 0 else 0
                print(f'  {i}/{total}  elapsed {el:.0f}s  eta {eta:.0f}s')

    elapsed = time.time() - t0
    out_path = os.path.join(DATA_DIR, OUT_FILE)
    with open(out_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        for r in results:
            writer.writerow(r)

    print()
    print('=' * 72)
    print(f'  Done in {elapsed:.0f}s ({elapsed / 60:.1f} min) on {cores} workers.')
    print(f'  Data -> {out_path}  ({len(results)} rows)')
    print('=' * 72)


if __name__ == '__main__':
    multiprocessing.freeze_support()
    run()
