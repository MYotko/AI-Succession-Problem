"""
run_to_termination.py -- run a GardenModel simulation to natural termination.

GAP-01 MOTIVATION
-----------------
The spec integral runs to inf.  The phi*L(t) tail component cannot be estimated
analytically without knowing how L(t) behaves after the simulation ends.
Running to natural termination resolves this:

  EXTINCTION termination  (population = 0):
      L(T) = 0 at the terminal step.  Therefore integral_T^inf phi*L(t) dt = 0.
      integral_U_sys captures the COMPLETE U_sys contribution.
      GAP-01 sub-problem 2 is CLOSED for this run.

  CONVERGENCE termination (L(t) stable, L* > 0):
      The civilization has reached a healthy steady state.  The integral
      integral_T^inf phi*A*L* dt diverges -- correctly, because a sustained civilization
      generates infinite discounted utility.  This is not a gap; it is the
      right answer.  The steady-state rate u_sys[T] characterises the ongoing
      per-cycle contribution.

  MAX_STEPS cap:
      Safety ceiling; same situation as the prior T=300 hard cap but larger.

TERMINATION CONDITIONS (checked each step in priority order)
------------------------------------------------------------
1. EXTINCTION:   model.step() returns False (population = 0)
2. CONVERGENCE:  coefficient of variation of L(t) over the last CONV_WINDOW
                 steps falls below CONV_CV_THRESHOLD
3. MAX_STEPS:    safety ceiling

CONFIGURATION
-------------
Edit the constants below.  Recommended starting points:
  - rr = 0.060-0.064  ->  near phase boundary; mix of extinction and convergence
  - rr = 0.050        ->  deep sub-viable; extinction expected within ~1,000 steps
  - rr = 0.090        ->  healthy; convergence to steady state expected

v1.x.2: SUCCESSOR_CAP is now a list; one output CSV is written per cap value.
Output files: data/run_to_termination_v1x2_cap{N}.csv
"""

import os
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"

import os
import sys
import csv
import time
import numpy as np

# -- Configuration --------------------------------------------------------------

N_AGENTS          = 200
REPRODUCTION_RATE = 0.064      # near phase boundary -- produces both outcomes
PHI               = 10.0
ALPHA             = 1.0
# v1.x.2: loop over cap values; one CSV per cap
SUCCESSOR_CAP_VALUES = [5.0, 10.0, 25.0, 50.0, 100.0]
SEED              = 42

MAX_STEPS         = 50_000     # safety ceiling -- increase for deep sub-viable runs
VERBOSE_INTERVAL  = 500        # print a progress line every N steps

CONV_WINDOW       = 300        # steps to evaluate L(t) stability over
CONV_CV_THRESHOLD = 0.05       # coefficient of variation < this -> converged

# -- Output --------------------------------------------------------------------

DATA_DIR  = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
# OUT_FILE is generated per cap value: run_to_termination_v1x2_cap{N}.csv

# -- Convergence check ----------------------------------------------------------

def _converged(l_history):
    """True if L(t) CV < CONV_CV_THRESHOLD over the last CONV_WINDOW steps."""
    if len(l_history) < CONV_WINDOW:
        return False
    recent = np.array(l_history[-CONV_WINDOW:], dtype=float)
    if not np.all(np.isfinite(recent)):
        return False
    mean = recent.mean()
    if mean < 1e-4:
        return False          # near-zero means extinction is occurring, not stability
    return (recent.std() / mean) < CONV_CV_THRESHOLD


# -- Main runner ----------------------------------------------------------------

def _run_one_cap(successor_cap):
    """Run one full simulation to termination for a single successor_cap value."""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from model import GardenModel
    from agents import AIAgent

    config = {
        'random_seed':       SEED,
        'reproduction_rate': REPRODUCTION_RATE,
        'phi':               PHI,
        'alpha':             ALPHA,
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

    print('=' * 72, flush=True)
    print(f'  run_to_termination.py  --  cap={successor_cap}  GAP-01 phi*L(t) tail closure',
          flush=True)
    print('=' * 72, flush=True)
    print(f'  n_agents={N_AGENTS}  rr={REPRODUCTION_RATE}  phi={PHI}  '
          f'alpha={ALPHA}  cap={successor_cap}  seed={SEED}', flush=True)
    print(f'  max_steps={MAX_STEPS:,}  conv_window={CONV_WINDOW}  '
          f'conv_cv_threshold={CONV_CV_THRESHOLD}', flush=True)
    print(flush=True)

    hdr = (f'{"Step":>9} | {"Pop":>6} | {"Gen":>4} | {"U_sys":>9} | '
           f'{"Integral":>13} | {"Tail":>9} | {"L(t)":>8} | {"L(t) CV":>8}')
    print(hdr, flush=True)
    print('-' * len(hdr), flush=True)

    termination_reason = 'max_steps'
    t_start = time.time()

    for step in range(MAX_STEPS):
        alive = model.step()

        dc  = model.datacollector
        pop = dc['population'][-1]
        u   = dc['U_sys'][-1]
        ig  = dc['integral_U_sys'][-1]
        tl  = dc['u_sys_tail_estimate'][-1]
        lt  = dc['L_t'][-1]
        gen = dc['ai_generation'][-1]

        # Compute rolling CV for display even when not yet at full window
        recent_l = dc['L_t'][-min(CONV_WINDOW, len(dc['L_t'])):]
        mean_l   = np.mean(recent_l)
        cv_l     = (np.std(recent_l) / mean_l) if mean_l > 1e-4 else float('nan')

        if (step + 1) % VERBOSE_INTERVAL == 0:
            elapsed = time.time() - t_start
            rate    = (step + 1) / elapsed if elapsed > 0 else 0
            cv_str  = f'{cv_l:.4f}' if not np.isnan(cv_l) else '  n/a '
            print(f'{step+1:>9,} | {pop:>6,} | {gen:>4} | {u:>9.3f} | '
                  f'{ig:>13,.2f} | {tl:>9.4f} | {lt:>8.4f} | {cv_str:>8}'
                  f'   [{elapsed:.0f}s, {rate:.0f} st/s]', flush=True)

        if not alive:
            termination_reason = 'extinction'
            break

        if step >= CONV_WINDOW and _converged(dc['L_t']):
            termination_reason = 'convergence'
            break

    # -- Terminal summary ------------------------------------------------------
    dc           = model.datacollector
    steps_run    = len(dc['U_sys'])
    ig_final     = dc['integral_U_sys'][-1]
    tail_final   = dc['u_sys_tail_estimate'][-1]
    total_final  = dc['u_sys_total_estimate'][-1]
    pop_final    = dc['population'][-1]
    lt_final     = dc['L_t'][-1]
    u_final      = dc['U_sys'][-1]
    gen_final    = dc['ai_generation'][-1]
    elapsed      = time.time() - t_start

    print(flush=True)
    print('=' * 72, flush=True)
    print(f'  TERMINATION: {termination_reason.upper()}  (cap={successor_cap})', flush=True)
    print(f'  Steps run:   {steps_run:,}', flush=True)
    print(f'  Population:  {pop_final:,}', flush=True)
    print(f'  AI gen:      {gen_final}', flush=True)
    print(f'  L(t) final:  {lt_final:.6f}', flush=True)
    print(f'  Elapsed:     {elapsed:.1f}s  ({steps_run/elapsed:.0f} steps/sec)', flush=True)
    print(flush=True)
    print('  -- U_sys integral accounting --------------------------------', flush=True)
    print(f'  integral_U_sys       {ig_final:>18,.4f}   (trapezoidal, steps 0->T)', flush=True)
    print(f'  u_sys_tail_estimate  {tail_final:>18.4f}   (integral_T^inf A*e^(-rho*t)/rho, lower bound)', flush=True)
    print(f'  u_sys_total_estimate {total_final:>18,.4f}   (integral + tail)', flush=True)
    print(flush=True)

    if termination_reason == 'extinction':
        print('  -- GAP-01 sub-problem 2: CLOSED ------------------------------', flush=True)
        print('  L(T) = 0  ->  phi*L(t) tail = 0  ->  no unaccounted contribution', flush=True)
        print(f'  Complete U_sys = {ig_final:,.4f}', flush=True)
        print(f'  Tail fraction: {100*tail_final/max(total_final,1e-9):.3f}%  (negligible at large T)', flush=True)

    elif termination_reason == 'convergence':
        rho = config.get('rho', 0.01)
        print('  -- GAP-01 sub-problem 2: NOT A GAP --------------------------', flush=True)
        print(f'  L(T) = {lt_final:.4f} > 0  ->  integral_T^inf phi*L(t) dt diverges.', flush=True)
        print('  This is the correct result: the civilization persists and', flush=True)
        print('  generates infinite integrated utility.  The integral is a', flush=True)
        print('  lower bound; the ongoing per-cycle contribution is:', flush=True)
        print(f'    U_sys[T] = {u_final:.4f} per governance cycle', flush=True)
        print(f'    Discount-tail lower bound / rho: {tail_final:.4f} / {rho} = {tail_final/rho:.2f}', flush=True)

    else:
        print('  -- GAP-01 sub-problem 2: OPEN (max_steps reached) ------------', flush=True)
        print(f'  Increase MAX_STEPS beyond {MAX_STEPS:,} to reach natural termination.', flush=True)

    print('=' * 72, flush=True)

    # -- Write output CSV ------------------------------------------------------
    os.makedirs(DATA_DIR, exist_ok=True)
    cap_str  = str(int(successor_cap)) if successor_cap == int(successor_cap) else str(successor_cap)
    out_file = f'run_to_termination_v1x2_cap{cap_str}.csv'
    out_path = os.path.join(DATA_DIR, out_file)

    fields = ['step', 'population', 'ai_generation', 'U_sys',
              'integral_U_sys', 'u_sys_tail_estimate', 'u_sys_total_estimate',
              'L_t', 'H_N', 'H_E', 'Theta_tech', 'Psi_inst',
              'resource_level', 'constraint_level', 'runaway_term']

    with open(out_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
        writer.writeheader()
        dc_fields = [f for f in fields if f != 'step']
        n = len(dc['U_sys'])
        for i in range(n):
            row = {k: dc[k][i] for k in dc_fields}
            row['step'] = i
            writer.writerow(row)

    print(f'\n  Data -> {out_path}  ({steps_run:,} rows)', flush=True)
    return model, termination_reason


def run():
    results = []
    for cap in SUCCESSOR_CAP_VALUES:
        model, reason = _run_one_cap(cap)
        results.append((cap, reason))
    print('\n  === All cap values complete ===', flush=True)
    for cap, reason in results:
        print(f'  cap={cap:6.1f}  ->  {reason}', flush=True)
    return results


if __name__ == '__main__':
    run()
