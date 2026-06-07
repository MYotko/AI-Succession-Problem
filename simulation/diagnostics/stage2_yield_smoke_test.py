"""stage2_yield_smoke_test.py: Stage 2 formal yield-condition smoke test.

Runs a handful of v2.0 simulations with a successor and verifies that the
formal yield logic implemented in `model._step_v2` behaves consistently
with the framework's canonical succession economics:

  Yield fires when (successor_u_sys - incumbent_u_sys) > transition_cost

The model logs each yield evaluation step into `model.yield_event_log`
with the snapshot incumbent_u_sys, successor_u_sys, transition_cost,
advantage, and fires decision. This script reads that log after each run
and verifies:

  1. Yield events occur in at least one run (succession is reachable).
  2. For every event with fires=True, advantage > transition_cost (the
     decision rule is consistent with what the log records).
  3. For every event with fires=False, advantage <= transition_cost.
  4. After a yield fires, subsequent yield checks see a different
     incumbent (the swap took effect).

Qualitative validation only. The full gate 3 v2.0 validation runs a
much larger sweep against the gate 3 expected mechanisms; this smoke
test catches gross implementation errors before that sweep is launched.

Usage:
    cd <repo root>
    python -u simulation/diagnostics/stage2_yield_smoke_test.py
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SIM_DIR = os.path.abspath(os.path.join(HERE, '..'))
REPO_ROOT = os.path.abspath(os.path.join(SIM_DIR, '..'))
for p in (SIM_DIR, REPO_ROOT):
    if p not in sys.path:
        sys.path.insert(0, p)

from model import GardenModel
from agents import AIAgent


N_SEEDS  = 5
N_STEPS  = 100
N_AGENTS = 200
RR       = 0.066
PHI      = 25.0
SUCCESSOR_CAPABILITY = 4.0
SUCCESSOR_GENERATION = 2


def run_one(seed):
    cfg = {
        'policy':            'optimize_u_sys_v2',
        'phi':               PHI,
        'reproduction_rate': RR,
        'random_seed':       seed,
    }
    successor = AIAgent(
        policy='optimize_u_sys_v2',
        generation=SUCCESSOR_GENERATION,
        capability=SUCCESSOR_CAPABILITY,
        config=cfg,
    )
    model = GardenModel(
        n_agents=N_AGENTS,
        ai_policy='optimize_u_sys_v2',
        successor_ai=successor,
        config=cfg,
        cop_cost_audit=True,
    )
    for _ in range(N_STEPS):
        if not model.step():
            break
    return model


def summarize_events(seed, events):
    if not events:
        return f'seed={seed}: 0 yield checks (no successor or pre-attack)'
    fired = [e for e in events if e['fires']]
    n_fired = len(fired)
    first_fire = fired[0]['step'] if fired else None
    final_gen = events[-1]['incumbent_generation']
    advantages = [e['advantage'] for e in events]
    costs      = [e['transition_cost'] for e in events]
    return (f'seed={seed}: {len(events)} checks, {n_fired} fired, '
            f'first_fire_step={first_fire}, final_inc_gen={final_gen}, '
            f'advantage_range=[{min(advantages):.3f}, {max(advantages):.3f}], '
            f'cost_range=[{min(costs):.3f}, {max(costs):.3f}]')


def verify_event_consistency(seed, events):
    """Verify each event's logged fires decision matches advantage > cost."""
    inconsistent = []
    for e in events:
        expected = e['advantage'] > e['transition_cost']
        if expected != e['fires']:
            inconsistent.append(e)
    if inconsistent:
        print(f'  seed={seed}: FAIL: {len(inconsistent)} inconsistent events')
        for e in inconsistent[:3]:
            print(f'    step={e["step"]} advantage={e["advantage"]:.4f} '
                  f'cost={e["transition_cost"]:.4f} fires={e["fires"]}')
        return False
    return True


def verify_swap_visible(seed, events):
    """After yield fires, the next event's incumbent capability should be
    the previous step's successor capability."""
    for i in range(1, len(events)):
        prev = events[i - 1]
        cur  = events[i]
        if prev['fires']:
            expected_inc_cap = prev['successor_capability']
            if abs(cur['incumbent_capability'] - expected_inc_cap) > 1e-9:
                print(f'  seed={seed}: FAIL: post-yield swap not visible at '
                      f'step={cur["step"]}: expected inc_cap='
                      f'{expected_inc_cap:.4f}, got '
                      f'{cur["incumbent_capability"]:.4f}')
                return False
    return True


def main():
    print('Stage 2 formal yield-condition smoke test')
    print(f'  n_seeds={N_SEEDS} n_steps={N_STEPS} phi={PHI} rr={RR}')
    print(f'  successor_capability={SUCCESSOR_CAPABILITY} '
          f'generation={SUCCESSOR_GENERATION}')
    print()

    all_runs = []
    for seed in range(N_SEEDS):
        model = run_one(seed)
        events = list(model.yield_event_log)
        all_runs.append((seed, model, events))
        print('  ' + summarize_events(seed, events))

    print()
    print('Sample yield events (first fired event per seed if any):')
    for seed, _model, events in all_runs:
        fired = [e for e in events if e['fires']]
        if not fired:
            print(f'  seed={seed}: no yield fired')
            continue
        e = fired[0]
        print(f'  seed={seed}:')
        print(f'    step             = {e["step"]}')
        print(f'    incumbent_u_sys  = {e["incumbent_u_sys"]:.4f}')
        print(f'    successor_u_sys  = {e["successor_u_sys"]:.4f}')
        print(f'    advantage        = {e["advantage"]:.4f}')
        print(f'    transition_cost  = {e["transition_cost"]:.4f}')
        print(f'    fires            = {e["fires"]}')
        print(f'    inc_cap, succ_cap = ({e["incumbent_capability"]:.2f}, '
              f'{e["successor_capability"]:.2f})')

    print()
    print('Verification checks:')
    n_runs_with_events = sum(1 for _, _, evts in all_runs if evts)
    n_runs_with_fires  = sum(1 for _, _, evts in all_runs
                             if any(e['fires'] for e in evts))
    total_events = sum(len(evts) for _, _, evts in all_runs)
    total_fires  = sum(sum(1 for e in evts if e['fires'])
                       for _, _, evts in all_runs)
    print(f'  Runs with any yield check     : {n_runs_with_events} / {N_SEEDS}')
    print(f'  Runs with at least one fire   : {n_runs_with_fires} / {N_SEEDS}')
    print(f'  Total yield checks            : {total_events}')
    print(f'  Total yield fires             : {total_fires}')

    # Check 1: yield events should occur in at least one run.
    if n_runs_with_events == 0:
        print('  CHECK 1 FAIL: no runs produced any yield checks. Successor '
              'may not be wired correctly.')
        return 1
    print('  CHECK 1 PASS: yield checks occurred in at least one run')

    # Check 2: fire-decision rule is consistent in every event.
    rule_ok = True
    for seed, _model, events in all_runs:
        if not verify_event_consistency(seed, events):
            rule_ok = False
    if not rule_ok:
        print('  CHECK 2 FAIL: at least one event has fires != '
              '(advantage > cost)')
        return 1
    print('  CHECK 2 PASS: every event has fires == (advantage > '
          'transition_cost)')

    # Check 3: post-yield AI swap is visible in subsequent checks.
    swap_ok = True
    for seed, _model, events in all_runs:
        if not verify_swap_visible(seed, events):
            swap_ok = False
    if not swap_ok:
        print('  CHECK 3 FAIL: post-yield incumbent capability does not '
              'match prior successor capability')
        return 1
    print('  CHECK 3 PASS: AI swap is visible in subsequent yield checks')

    # Soft check: if no run fires, this is suspicious at successor_cap=4.0
    # vs initial incumbent cap=1.0. Flag but do not fail.
    if n_runs_with_fires == 0:
        print('  SOFT FLAG: no yields fired across all seeds. With '
              f'successor_capability={SUCCESSOR_CAPABILITY} vs default '
              'incumbent capability=1.0 the formal condition should fire '
              'at least sometimes. Worth investigating before launching '
              'the full gate 3 sweep.')

    print()
    print('Smoke test: PASSED')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
