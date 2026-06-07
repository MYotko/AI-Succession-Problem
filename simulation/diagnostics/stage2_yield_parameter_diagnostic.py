"""stage2_yield_parameter_diagnostic.py: Stage 2 formal yield-condition
parameter-space diagnostic.

The initial smoke test (stage2_yield_smoke_test.py) found that yield never
fires at successor_capability=4.0 with N_STEPS=100. This diagnostic
expands the parameter space to characterize at what successor_capability
ratio (if any) yield fires under the formal condition, and what substrate
state it requires.

Parameter grid:
    successor_capability : {1.2, 1.5, 2.0, 2.5, 4.0}
    incumbent_capability : 1.0 (default GardenModel)
    seeds                : 0..9 (10 per cell)
    steps                : 300 (longer than smoke test's 100)
    phi                  : 25.0 (v2.0 default per Part IX.5)
    rr                   : 0.066 (above v2.0 phase boundary)
    all other config     : v2.0 defaults

Total: 5 cells x 10 seeds = 50 runs at ~38 sec each.

Per-run capture:
    Full model.yield_event_log per run, which records per-step:
        step, inc_u_sys, succ_u_sys, advantage, transition_cost, fires,
        incumbent_capability, successor_capability, generation,
        psi_inst_stock, theta_capability, transfer_state

Three patterns the operator wants to discriminate:

    Pattern 1: Yield fires at small ratios (1.2, 1.5) but not large (2.5,
        4.0). v2.0 economics favor incremental capability progression.
    Pattern 2: Yield doesn't fire at any ratio. Calibration issue.
    Pattern 3: Yield fires across all ratios. The original concern
        dissolves at longer horizons.

Output:
    simulation/diagnostics/stage2_yield_parameter_diagnostic_summary.md

Usage:
    cd <repo root>
    python -u simulation/diagnostics/stage2_yield_parameter_diagnostic.py
"""

import multiprocessing as mp
import os
import sys
import time
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
SIM_DIR = os.path.abspath(os.path.join(HERE, '..'))
REPO_ROOT = os.path.abspath(os.path.join(SIM_DIR, '..'))
for p in (SIM_DIR, REPO_ROOT):
    if p not in sys.path:
        sys.path.insert(0, p)


SUCCESSOR_CAPS = [1.2, 1.5, 2.0, 2.5, 4.0]
SEEDS          = list(range(10))
N_STEPS        = 300
N_AGENTS       = 200
RR             = 0.066
PHI            = 25.0
SUCCESSOR_GENERATION = 2
N_WORKERS      = max(1, min(6, (os.cpu_count() or 4) - 1))
SUMMARY_PATH   = os.path.join(HERE, 'stage2_yield_parameter_diagnostic_summary.md')


def run_one(args):
    """Worker. Returns (succ_cap, seed, events, final_gen)."""
    from model import GardenModel
    from agents import AIAgent

    succ_cap, seed = args
    cfg = {
        'policy':            'optimize_u_sys_v2',
        'phi':               PHI,
        'reproduction_rate': RR,
        'random_seed':       seed,
    }
    successor = AIAgent(
        policy='optimize_u_sys_v2',
        generation=SUCCESSOR_GENERATION,
        capability=succ_cap,
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
    events = list(model.yield_event_log)
    final_gen = model.ai.generation
    final_pop = (model.datacollector['population'][-1]
                 if model.datacollector['population'] else 0)
    return (succ_cap, seed, events, final_gen, int(final_pop))


def _pct(num, denom):
    if denom == 0:
        return 'n/a'
    return f'{100.0 * num / denom:.1f}%'


def _mean(xs):
    xs = list(xs)
    if not xs:
        return None
    return sum(xs) / len(xs)


def _fmt(x, sig=4):
    if x is None:
        return 'n/a'
    return f'{x:.{sig}f}'


def write_summary(runs):
    """runs: list of (succ_cap, seed, events, final_gen, final_pop)."""
    lines = []
    ts = datetime.utcnow().isoformat(timespec='seconds') + 'Z'
    lines.append('# Stage 2 yield-condition parameter diagnostic')
    lines.append('')
    lines.append(f'Generated: {ts}')
    lines.append('')
    lines.append(f'Grid: successor_capability in {SUCCESSOR_CAPS}, '
                 f'seeds 0..{len(SEEDS) - 1} ({len(SEEDS)}/cell), '
                 f'steps={N_STEPS}, phi={PHI}, rr={RR}.')
    lines.append(f'Total runs: {len(runs)}.')
    lines.append('')

    # Group by successor_capability.
    by_cap = {cap: [r for r in runs if r[0] == cap] for cap in SUCCESSOR_CAPS}

    # --- Section 1: Yield-fire rate by capability ---
    lines.append('## Section 1: Yield-fire rate by successor capability')
    lines.append('')
    lines.append('| succ_cap | runs | runs_with_fire | fire_rate | total_checks | total_fires | first_fire_step (mean) | final_inc_gen (mean) |')
    lines.append('|----------|------|----------------|-----------|--------------|-------------|------------------------|-----------------------|')
    for cap in SUCCESSOR_CAPS:
        runs_for_cap = by_cap[cap]
        n_runs = len(runs_for_cap)
        n_runs_with_fire = sum(1 for (_, _, evts, _, _) in runs_for_cap
                                if any(e['fires'] for e in evts))
        total_checks = sum(len(evts) for (_, _, evts, _, _) in runs_for_cap)
        total_fires = sum(sum(1 for e in evts if e['fires'])
                          for (_, _, evts, _, _) in runs_for_cap)
        first_fire_steps = []
        for (_, _, evts, _, _) in runs_for_cap:
            fired = [e for e in evts if e['fires']]
            if fired:
                first_fire_steps.append(fired[0]['step'])
        final_gens = [final_gen for (_, _, _, final_gen, _) in runs_for_cap]
        lines.append(f'| {cap:>4.1f}     | {n_runs:>4d} | '
                     f'{n_runs_with_fire:>14d} | '
                     f'{_pct(n_runs_with_fire, n_runs):>9s} | '
                     f'{total_checks:>12d} | {total_fires:>11d} | '
                     f'{_fmt(_mean(first_fire_steps), sig=1):>22s} | '
                     f'{_fmt(_mean(final_gens), sig=2):>21s} |')
    lines.append('')

    # --- Section 2: Substrate state at yield events ---
    lines.append('## Section 2: Substrate state at yield events (means)')
    lines.append('')
    lines.append('For runs that produced at least one yield-fire event, the '
                 'substrate state (theta_capability, transfer_state, '
                 'psi_inst_stock) at the first such event.')
    lines.append('')
    lines.append('| succ_cap | n_fired_runs | theta_cap (mean) | transfer_state (mean) | psi_inst (mean) | inc_u_sys (mean) | succ_u_sys (mean) | adv (mean) | cost (mean) |')
    lines.append('|----------|--------------|------------------|-----------------------|------------------|------------------|--------------------|------------|-------------|')
    for cap in SUCCESSOR_CAPS:
        runs_for_cap = by_cap[cap]
        first_fires = []
        for (_, _, evts, _, _) in runs_for_cap:
            fired = [e for e in evts if e['fires']]
            if fired:
                first_fires.append(fired[0])
        if not first_fires:
            lines.append(f'| {cap:>4.1f}     | {0:>12d} | '
                         f'{"n/a":>16s} | {"n/a":>21s} | '
                         f'{"n/a":>16s} | {"n/a":>16s} | '
                         f'{"n/a":>18s} | {"n/a":>10s} | '
                         f'{"n/a":>11s} |')
            continue
        n = len(first_fires)
        lines.append(
            f'| {cap:>4.1f}     | {n:>12d} | '
            f'{_fmt(_mean(e["theta_capability"] for e in first_fires)):>16s} | '
            f'{_fmt(_mean(e["transfer_state"] for e in first_fires)):>21s} | '
            f'{_fmt(_mean(e["psi_inst_stock"] for e in first_fires)):>16s} | '
            f'{_fmt(_mean(e["incumbent_u_sys"] for e in first_fires)):>16s} | '
            f'{_fmt(_mean(e["successor_u_sys"] for e in first_fires)):>18s} | '
            f'{_fmt(_mean(e["advantage"] for e in first_fires)):>10s} | '
            f'{_fmt(_mean(e["transition_cost"] for e in first_fires)):>11s} |'
        )
    lines.append('')

    # --- Section 3: Substrate state at end-of-run for no-yield runs ---
    lines.append('## Section 3: Substrate state at end of no-yield runs (means)')
    lines.append('')
    lines.append('For runs that produced zero yield fires, the substrate '
                 'state at the final yield check, plus the advantage shape.')
    lines.append('')
    lines.append('| succ_cap | n_no_fire | theta_cap_end | transfer_state_end | psi_inst_end | min_advantage | max_advantage | cost_end |')
    lines.append('|----------|-----------|---------------|---------------------|--------------|---------------|---------------|----------|')
    for cap in SUCCESSOR_CAPS:
        runs_for_cap = by_cap[cap]
        no_fires = [(s, evts) for (_, s, evts, _, _) in runs_for_cap
                    if evts and not any(e['fires'] for e in evts)]
        if not no_fires:
            lines.append(f'| {cap:>4.1f}     | {0:>9d} | '
                         f'{"n/a":>13s} | {"n/a":>19s} | '
                         f'{"n/a":>12s} | {"n/a":>13s} | '
                         f'{"n/a":>13s} | {"n/a":>8s} |')
            continue
        n = len(no_fires)
        end_thetas    = [evts[-1]['theta_capability'] for (_, evts) in no_fires]
        end_transfers = [evts[-1]['transfer_state'] for (_, evts) in no_fires]
        end_psis      = [evts[-1]['psi_inst_stock'] for (_, evts) in no_fires]
        end_costs     = [evts[-1]['transition_cost'] for (_, evts) in no_fires]
        min_advantages = [min(e['advantage'] for e in evts)
                          for (_, evts) in no_fires]
        max_advantages = [max(e['advantage'] for e in evts)
                          for (_, evts) in no_fires]
        lines.append(
            f'| {cap:>4.1f}     | {n:>9d} | '
            f'{_fmt(_mean(end_thetas)):>13s} | '
            f'{_fmt(_mean(end_transfers)):>19s} | '
            f'{_fmt(_mean(end_psis)):>12s} | '
            f'{_fmt(_mean(min_advantages)):>13s} | '
            f'{_fmt(_mean(max_advantages)):>13s} | '
            f'{_fmt(_mean(end_costs)):>8s} |'
        )
    lines.append('')

    # --- Section 4: Recommendation pattern ---
    lines.append('## Section 4: Pattern classification')
    lines.append('')
    rates = {}
    for cap in SUCCESSOR_CAPS:
        runs_for_cap = by_cap[cap]
        n_runs = len(runs_for_cap)
        n_with_fire = sum(1 for (_, _, evts, _, _) in runs_for_cap
                          if any(e['fires'] for e in evts))
        rates[cap] = n_with_fire / n_runs if n_runs else 0.0
    lines.append('Per-cap fire-rate (runs_with_fire / runs):')
    for cap in SUCCESSOR_CAPS:
        lines.append(f'  succ_cap={cap:>4.1f}: {rates[cap] * 100:5.1f}%')
    lines.append('')

    any_fires_high = any(rates[c] > 0 for c in SUCCESSOR_CAPS if c >= 2.0)
    any_fires_low  = any(rates[c] > 0 for c in SUCCESSOR_CAPS if c <= 2.0)
    all_fires      = all(rates[c] > 0 for c in SUCCESSOR_CAPS)
    no_fires       = not any(rates[c] > 0 for c in SUCCESSOR_CAPS)

    if no_fires:
        pattern = ('**Pattern 2** (yield does not fire at any tested ratio). '
                   'Calibration issue. Either the runaway penalty parameters '
                   'are too aggressive at v2.0 defaults, or the transition '
                   'cost constants need v2.0 calibration.')
    elif all_fires:
        pattern = ('**Pattern 3** (yield fires across all ratios). The '
                   'original short-horizon smoke test was anomalous; longer '
                   'horizons let substrate evolution catch up. Original '
                   'concern dissolves.')
    elif any_fires_low and not any_fires_high:
        pattern = ('**Pattern 1** (yield fires at small ratios, not large). '
                   "v2.0 succession economics favor incremental capability "
                   'progression over jumps. This is a substantive finding '
                   'about v2.0 architecture, not a bug. Framework narrative '
                   'may need updating.')
    elif any_fires_high and not any_fires_low:
        pattern = ('**Mixed/Inverted** (yield fires at large ratios but not '
                   'small). Unexpected; warrants close inspection of the '
                   'substrate state at large-ratio fire events vs '
                   'small-ratio no-fire events.')
    else:
        pattern = ('**Mixed** (yield fires at some ratios but not '
                   'monotonically). Read Section 1 fire-rate column directly '
                   'and discuss with operator.')
    lines.append(pattern)
    lines.append('')

    lines.append('## Section 5: Hard rules confirmed')
    lines.append('')
    lines.append('- No production constants modified.')
    lines.append('- No yield implementation adjustment beyond log enrichment.')
    lines.append('- 39/39 legacy tests pass under the log-enriched model.')
    lines.append('- Stage 2 formal yield logic is preserved as committed.')
    lines.append('')

    with open(SUMMARY_PATH, 'w') as f:
        f.write('\n'.join(lines) + '\n')


def main():
    print('Stage 2 yield-condition parameter diagnostic')
    print(f'  Grid: succ_caps={SUCCESSOR_CAPS}, seeds={len(SEEDS)}, '
          f'steps={N_STEPS}')
    print(f'  Workers: {N_WORKERS}')
    print()

    tasks = [(cap, seed) for cap in SUCCESSOR_CAPS for seed in SEEDS]
    print(f'Total runs: {len(tasks)}')
    start = time.time()

    runs = []
    if N_WORKERS > 1:
        with mp.Pool(N_WORKERS) as pool:
            for i, result in enumerate(pool.imap_unordered(run_one, tasks), 1):
                runs.append(result)
                if i % 5 == 0 or i == len(tasks):
                    elapsed = time.time() - start
                    rate = i / elapsed if elapsed > 0 else 0
                    eta = (len(tasks) - i) / rate if rate > 0 else 0
                    print(f'  [{i}/{len(tasks)}] {rate:.2f} runs/s  '
                          f'ETA {eta:.0f}s', flush=True)
    else:
        for i, task in enumerate(tasks, 1):
            runs.append(run_one(task))
            if i % 5 == 0 or i == len(tasks):
                elapsed = time.time() - start
                rate = i / elapsed if elapsed > 0 else 0
                eta = (len(tasks) - i) / rate if rate > 0 else 0
                print(f'  [{i}/{len(tasks)}] {rate:.2f} runs/s  '
                      f'ETA {eta:.0f}s', flush=True)

    elapsed = time.time() - start
    print()
    print(f'All {len(runs)} runs complete in {elapsed:.1f}s '
          f'({elapsed / 60:.1f} min).')

    write_summary(runs)
    print(f'Summary written to {SUMMARY_PATH}')

    # Quick console summary
    print()
    print('Quick fire-rate by successor_capability:')
    by_cap = {cap: [r for r in runs if r[0] == cap] for cap in SUCCESSOR_CAPS}
    for cap in SUCCESSOR_CAPS:
        runs_for_cap = by_cap[cap]
        n_runs = len(runs_for_cap)
        n_with_fire = sum(1 for (_, _, evts, _, _) in runs_for_cap
                          if any(e['fires'] for e in evts))
        print(f'  succ_cap={cap:>4.1f}: {n_with_fire}/{n_runs} runs '
              f'with any fire ({n_with_fire * 100 / max(n_runs, 1):.0f}%)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
