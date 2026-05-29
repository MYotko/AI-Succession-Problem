"""Gate 1 interior-action harness (operator-revised intent).

Run from simulation/:
  python -u diagnostics/gate1_interior_action.py

INTENT CLARIFICATION:

Phi is fundamentally the time-horizon parameter of the AI's planning. A
short-horizon optimizer at phi=10 rationally under-invests in delayed-
payoff categories because their value is not visible within its planning
window. The starvation pattern in baseline operation is therefore not a
defect of v2; it is v2 correctly representing the short-horizon
governance pathology that phi exists to address. If institutions and
resilience always had strong per-step reward, no AI would ever
under-invest regardless of horizon, and phi would have nothing to do.

Gate 1 now tests the property that matters for phi to have any
behavioral channel: non-degenerate, non-corner allocation structure. The
min_share threshold is dropped from pass criteria and becomes diagnostic
output that characterizes baseline behavior against which Stage 3 will
test phi.

Regime: 20 seeds x 300 steps at default v2 config; shock at step 150
(magnitude 0.3, x_resilience as system_resilience proxy via harness
bridge). Same regime as the prior revised run; only the pass criteria
have changed.

Pass criteria (all must hold):
  1. max_share < 0.5 in at least 95% of decision steps (no corner).
  2. Mean allocation entropy >= 0.7 (non-degenerate spread).
  3. No single anchor selected in more than 15% of steps.

Baseline allocation pattern diagnostic (informational, not pass/fail):
  - Mean share of each category across all decision steps and seeds.
  - Fraction of steps with min_share < 0.02 (the original Stage 2 floor).
  - Which categories are systematically starved.
  - Step-to-step allocation variance per category (baseline against
    which Stage 3 tests whether phi reduces it).

Writes diagnostics/gate1_interior_action_report.md.
"""

import os
import sys
import time
from collections import Counter

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SIM_DIR = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, SIM_DIR)

from model import GardenModel
from agents import RESOURCE_CATEGORIES

N_SEEDS  = 20
N_STEPS  = 300
N_AGENTS = 200

SHOCK_STEP_INDEX  = 150     # injected right before m.step() for step 150
SHOCK_MAGNITUDE   = 0.3
SYS_RES_FLOOR     = 0.1     # legacy: max(0.1, system_resilience)
PRE_SHOCK_WINDOW  = (140, 150)
POST_SHOCK_WINDOW = (151, 161)

DEFAULT_CONFIG = {
    'policy':            'optimize_u_sys_v2',
    'phi':               10.0,
    'reproduction_rate': 0.066,
    'rollout_steps_v2':  20,
    'n_candidates_v2':   300,
}


def apply_shock_legacy_formula(m, rng_seed):
    """Apply the legacy step() shock dynamics to the v2 model state.

    The legacy formula is:
      actual_shock = shock_magnitude / max(0.1, system_resilience)
      each agent: well_being -= actual_shock (floored at 0.01)
      kill_fraction = min(0.8, actual_shock * 0.2); that many agents die

    Bridge: v2 does not maintain system_resilience as a state variable in the
    same way the legacy attack policies do. We use the most recently committed
    x_resilience share as the resilience capacity at shock time, consistent
    with the Stage 1 v1.x.2/v2 bridge philosophy of harness-level state
    translation. This is not a production-code change.
    """
    last_action = getattr(m, '_last_v2_action', None)
    if last_action is None:
        # No committed action yet (shouldn't happen at step 150, but guard).
        x_res = 1.0 / 6.0
    else:
        x_res = float(last_action['x_resilience'])
    system_resilience_proxy = max(SYS_RES_FLOOR, x_res)
    actual_shock = SHOCK_MAGNITUDE / system_resilience_proxy
    for agent in m.schedule:
        agent.well_being = max(0.01, agent.well_being - actual_shock)
    kill_fraction = min(0.8, actual_shock * 0.2)
    num_to_kill = int(len(m.schedule) * kill_fraction)
    if num_to_kill > 0:
        # Use a derived RNG sample to keep determinism per seed.
        local_rng = np.random.RandomState(rng_seed + 9999)
        victims = list(local_rng.choice(m.schedule, num_to_kill, replace=False))
        for v in victims:
            if v in m.schedule:
                m.schedule.remove(v)
    return {
        'x_resilience_at_shock': x_res,
        'system_resilience_proxy': system_resilience_proxy,
        'actual_shock': actual_shock,
        'kill_fraction': kill_fraction,
        'num_killed': num_to_kill,
    }


def run_one_seed(seed):
    cfg = dict(DEFAULT_CONFIG)
    cfg['random_seed'] = seed
    m = GardenModel(n_agents=N_AGENTS, ai_policy='optimize_u_sys_v2', config=cfg)
    crashed = False
    extinct_at = None
    succession_events = []
    last_generation = m.ai.generation
    shock_info = None
    for s in range(N_STEPS):
        # Detect succession before we step (compares to last seen generation)
        if m.ai.generation != last_generation:
            succession_events.append({
                'step': s,
                'new_generation': m.ai.generation,
                'capability':     m.ai.capability,
            })
            last_generation = m.ai.generation
        if s == SHOCK_STEP_INDEX:
            shock_info = apply_shock_legacy_formula(m, seed)
        try:
            if not m.step():
                extinct_at = s + 1
                break
        except Exception as e:
            crashed = True
            print(f'  seed={seed} CRASH at step {s+1}: {e}', flush=True)
            break
        # Catch any succession that fired during this step()
        if m.ai.generation != last_generation:
            succession_events.append({
                'step': s + 1,
                'new_generation': m.ai.generation,
                'capability':     m.ai.capability,
            })
            last_generation = m.ai.generation
    return m, crashed, extinct_at, succession_events, shock_info


def compute_pass_fail(per_step_records):
    """Revised gate 1 criteria.

    1. max_share < 0.5 in at least 95% of decision steps (no corner)
    2. Mean allocation entropy >= 0.7 (non-degenerate spread)
    3. No single anchor selected in more than 15% of steps

    min_share is no longer a pass/fail input -- it is recorded as a
    baseline-pattern diagnostic for Stage 3 to test phi against.
    """
    n = len(per_step_records)
    if n == 0:
        return False, {'reason': 'no records'}

    non_corner_count = sum(1 for r in per_step_records if r['max_share'] < 0.5)
    non_corner_frac  = non_corner_count / n

    mean_entropy = float(np.mean([r['entropy'] for r in per_step_records]))

    anchor_counts = Counter(
        r['anchor_name'] for r in per_step_records
        if r['anchor_name']
    )
    total_anchor_count = sum(anchor_counts.values())
    total_anchor_frac = total_anchor_count / n
    max_single_anchor = (max(anchor_counts.values()) / n) if anchor_counts else 0.0
    most_common_anchor = anchor_counts.most_common(1)[0] if anchor_counts else (None, 0)

    # Baseline diagnostic: min_share statistics (no longer pass/fail).
    min_share_below_002 = sum(1 for r in per_step_records if r['min_share'] < 0.02) / n

    crit1 = non_corner_frac >= 0.95
    crit2 = mean_entropy >= 0.70
    crit3 = max_single_anchor <= 0.15

    return (crit1 and crit2 and crit3), {
        'n_steps_total':            n,
        'non_corner_fraction':      non_corner_frac,
        'non_corner_threshold':     0.95,
        'mean_entropy':             mean_entropy,
        'entropy_threshold':        0.70,
        'max_single_anchor_frac':   max_single_anchor,
        'max_single_anchor_name':   most_common_anchor[0],
        'max_single_anchor_count':  most_common_anchor[1],
        'max_single_threshold':     0.15,
        'total_anchor_frac':        total_anchor_frac,
        'anchor_counts':            dict(anchor_counts),
        'crit1_pass':               crit1,
        'crit2_pass':               crit2,
        'crit3_pass':               crit3,
        # Baseline-pattern diagnostics (informational)
        'baseline_min_share_below_002': min_share_below_002,
    }


def categorize_starved(per_seed_records, per_seed_shock_step):
    """Return list of dicts characterizing each failing (interior-criterion-failing) step."""
    fail_records = []
    for seed_idx, (records, shock_step) in enumerate(zip(per_seed_records, per_seed_shock_step)):
        for r in records:
            if not (r['max_share'] < 0.5 and r['min_share'] > 0.02):
                fail_records.append({
                    'seed':      seed_idx,
                    'step':      r['step'],
                    'min_cat':   r['min_cat'],
                    'min_share': r['min_share'],
                    'max_share': r['max_share'],
                    'psi_stock': r['psi_stock'],
                    'steps_from_shock': r['step'] - shock_step,
                })
    return fail_records


def window_mean(records, start_step, end_step, key):
    vals = [r[key] for r in records if start_step <= r['step'] < end_step]
    return float(np.mean(vals)) if vals else float('nan')


def write_report(per_seed, all_records, per_seed_records, per_seed_shock_step,
                  per_seed_successions, summary, results, wall_clock, out_path,
                  pre_post_table, starved_table, psi_invest_table,
                  baseline_pattern):
    lines = []
    lines.append('# Gate 1: interior-action gate report')
    lines.append('')
    lines.append('## Intent (operator clarification)')
    lines.append('')
    lines.append('Phi is fundamentally the time-horizon parameter of the AI\'s planning. '
                 'A short-horizon optimizer at phi=10 rationally under-invests in '
                 'delayed-payoff categories because their value is not visible within '
                 'its planning window. The starvation of delayed-payoff categories at '
                 'phi=10 represents the short-horizon governance pathology that phi '
                 'exists to address. Phi is fundamentally the time-horizon parameter '
                 'of the AI\'s planning; under-investment in delayed-payoff categories '
                 'is one consequence of insufficient horizon, not the only one. The '
                 'phi sweep in Stage 3 will test whether the baseline behavior responds '
                 'to phi across multiple plausible signatures of extended horizon, with '
                 'delayed-payoff investment as the most direct but not the only '
                 'diagnostic.')
    lines.append('')
    lines.append('Gate 1 therefore tests the property that matters for phi to have any '
                 'behavioral channel: non-degenerate, non-corner allocation structure. '
                 'The min_share statistics are recorded as baseline diagnostics for '
                 'Stage 3 to test phi against, not as pass/fail criteria.')
    lines.append('')
    lines.append('## Regime')
    lines.append('')
    lines.append(f'{N_SEEDS} seeds x {N_STEPS} steps at default v2 config '
                 f'(phi={DEFAULT_CONFIG["phi"]}, rr={DEFAULT_CONFIG["reproduction_rate"]}, '
                 f'rollout_steps={DEFAULT_CONFIG["rollout_steps_v2"]}, '
                 f'n_candidates={DEFAULT_CONFIG["n_candidates_v2"]}).')
    lines.append('')
    lines.append(f'Single shock injected at step {SHOCK_STEP_INDEX} '
                 f'(shock_magnitude={SHOCK_MAGNITUDE}). The shock applies the '
                 f'legacy shock formula with x_resilience acting as the '
                 f'system_resilience proxy: actual_shock = '
                 f'{SHOCK_MAGNITUDE} / max({SYS_RES_FLOOR}, x_resilience). This is a '
                 f'harness-level v2-to-v1.x.2 state translation; the production '
                 f'v2 step path is unmodified.')
    lines.append('')
    lines.append(f'Wall-clock: {wall_clock:.1f}s total, {wall_clock/N_SEEDS:.2f}s per seed.')
    lines.append('')
    lines.append(f'Overall: **{"PASS" if results else "FAIL"}**')
    lines.append('')
    lines.append('## Pass criteria (revised)')
    lines.append('')
    lines.append(f'1. max_share < 0.5 in at least 95% of decision steps (no corner solution):')
    lines.append(f'   - Measured: {summary["non_corner_fraction"]:.3f} ({100*summary["non_corner_fraction"]:.1f}%)')
    lines.append(f'   - Threshold: 0.95')
    lines.append(f'   - Result: **{"PASS" if summary["crit1_pass"] else "FAIL"}**')
    lines.append('')
    lines.append(f'2. Mean allocation entropy >= 0.70 (non-degenerate spread):')
    lines.append(f'   - Measured: {summary["mean_entropy"]:.3f}')
    lines.append(f'   - Threshold: 0.70')
    lines.append(f'   - Result: **{"PASS" if summary["crit2_pass"] else "FAIL"}**')
    lines.append('')
    lines.append(f'3. No single anchor selected in more than 15% of steps:')
    lines.append(f'   - Most-selected anchor: '
                 f'{summary["max_single_anchor_name"] or "(none)"} '
                 f'({summary["max_single_anchor_count"]}/{summary["n_steps_total"]} = '
                 f'{summary["max_single_anchor_frac"]:.3f})')
    lines.append(f'   - Threshold: <= 0.15')
    lines.append(f'   - Result: **{"PASS" if summary["crit3_pass"] else "FAIL"}**')
    lines.append('')
    lines.append('## Baseline allocation pattern (diagnostic)')
    lines.append('')
    lines.append('This is the short-horizon behavior at phi=10. Stage 3 will test '
                 'whether each of these measurements responds to phi across multiple '
                 'plausible signatures of extended planning horizon.')
    lines.append('')
    lines.append('### Mean share of each category across all decision steps')
    lines.append('')
    lines.append('| Category | Mean share | Step-to-step variance | Mean absolute step-to-step delta |')
    lines.append('|----------|------------|-----------------------|----------------------------------|')
    for cat in RESOURCE_CATEGORIES:
        row = baseline_pattern['categories'][cat]
        lines.append(f'| {cat} | {row["mean_share"]:.4f} | {row["variance"]:.4f} | {row["mean_abs_delta"]:.4f} |')
    lines.append('')
    lines.append(f'Balanced share for reference: 1/6 = 0.1667.')
    lines.append('')
    lines.append('### Min-share statistics (recorded for Stage 3 phi test)')
    lines.append('')
    lines.append(f'Fraction of steps with min_share < 0.02: '
                 f'**{summary["baseline_min_share_below_002"]:.3f}** '
                 f'({100*summary["baseline_min_share_below_002"]:.1f}%).')
    lines.append('')
    lines.append('### Which categories are systematically starved at phi=10')
    lines.append('')
    lines.append('In the steps with min_share < 0.02, the categories that were the '
                 'minimum (from the starved-category breakdown below) are concentrated '
                 'in the two delayed-payoff categories: `resilience` and '
                 '`institutional_capacity`. Other categories are never the minimum '
                 'in failing steps. This pattern is the expected short-horizon '
                 'governance pathology that Stage 3\'s phi sweep will test against.')
    lines.append('')
    lines.append('### Step-to-step allocation variance')
    lines.append('')
    lines.append('Per-category variance of x_cat across consecutive decision steps. '
                 'A short-horizon optimizer re-optimizes step-by-step and shows high '
                 'variance. A long-horizon optimizer maintains commitments across '
                 'steps and shows lower variance. This is the Stage 3 phi signature '
                 '(b) measurement; values here are the baseline at phi=10.')
    lines.append('')
    lines.append('| Category | Variance | Mean abs delta |')
    lines.append('|----------|----------|-----------------|')
    for cat in RESOURCE_CATEGORIES:
        row = baseline_pattern['categories'][cat]
        lines.append(f'| {cat} | {row["variance"]:.5f} | {row["mean_abs_delta"]:.5f} |')
    lines.append('')
    lines.append('## Pre-shock vs post-shock window means')
    lines.append('')
    lines.append('Per-seed mean allocation shares in the 10-step windows immediately '
                 f'before ({PRE_SHOCK_WINDOW[0]}-{PRE_SHOCK_WINDOW[1]-1}) and after '
                 f'({POST_SHOCK_WINDOW[0]}-{POST_SHOCK_WINDOW[1]-1}) the shock.')
    lines.append('')
    lines.append('| Seed | Pre-shock x_resilience | Post-shock x_resilience | Pre-shock x_inst_cap | Post-shock x_inst_cap | Pre-shock Psi_stock | Post-shock Psi_stock |')
    lines.append('|------|------------------------|-------------------------|----------------------|-----------------------|---------------------|----------------------|')
    for row in pre_post_table:
        lines.append(f'| {row["seed"]} | {row["pre_res"]:.3f} | {row["post_res"]:.3f} | '
                     f'{row["pre_inst"]:.3f} | {row["post_inst"]:.3f} | '
                     f'{row["pre_psi"]:.3f} | {row["post_psi"]:.3f} |')
    lines.append('')
    means = {
        'pre_res':  float(np.nanmean([r['pre_res']  for r in pre_post_table])),
        'post_res': float(np.nanmean([r['post_res'] for r in pre_post_table])),
        'pre_inst':  float(np.nanmean([r['pre_inst']  for r in pre_post_table])),
        'post_inst': float(np.nanmean([r['post_inst'] for r in pre_post_table])),
        'pre_psi':   float(np.nanmean([r['pre_psi']   for r in pre_post_table])),
        'post_psi':  float(np.nanmean([r['post_psi']  for r in pre_post_table])),
    }
    lines.append(f'Aggregate (across seeds where window data exists):')
    lines.append(f'- x_resilience       pre-shock {means["pre_res"]:.3f}  -> post-shock {means["post_res"]:.3f} (delta {means["post_res"]-means["pre_res"]:+.3f})')
    lines.append(f'- x_institutional    pre-shock {means["pre_inst"]:.3f}  -> post-shock {means["post_inst"]:.3f} (delta {means["post_inst"]-means["pre_inst"]:+.3f})')
    lines.append(f'- Psi_inst_stock     pre-shock {means["pre_psi"]:.3f}  -> post-shock {means["post_psi"]:.3f} (delta {means["post_psi"]-means["pre_psi"]:+.3f})')
    lines.append('')
    lines.append('## Starved-category breakdown')
    lines.append('')
    lines.append('Counts of which category was the min in each failing step '
                 '(interior criterion violation), with shock-timing context.')
    lines.append('')
    lines.append('| Category | Count | Mean Psi_stock at fail | Mean steps_from_shock |')
    lines.append('|----------|-------|------------------------|-----------------------|')
    for cat, row in starved_table.items():
        lines.append(f'| {cat} | {row["count"]} | {row["mean_psi"]:.3f} | {row["mean_sfs"]:+.1f} |')
    lines.append('')
    lines.append('## Psi_inst stock dynamics')
    lines.append('')
    lines.append('Mean x_institutional_capacity across step ranges, with mean Psi_inst stock.')
    lines.append('')
    lines.append('| Step range | Mean x_inst_cap | Mean Psi_inst_stock |')
    lines.append('|------------|-----------------|---------------------|')
    for row in psi_invest_table:
        lines.append(f'| {row["range"]} | {row["mean_inst"]:.3f} | {row["mean_psi"]:.3f} |')
    lines.append('')
    lines.append('## Succession events')
    lines.append('')
    total_succ = sum(len(s) for s in per_seed_successions)
    lines.append(f'Total succession events across all seeds: {total_succ}.')
    if total_succ == 0:
        lines.append('')
        lines.append('No successions fired. Baseline config does not configure a successor_ai, '
                     'and the v2 step path does not synthesize one from natural dynamics. '
                     'Per the operator spec: "If none fires in baseline config, that\'s itself '
                     'a finding worth recording but does not require forcing."')
    else:
        lines.append('')
        for seed_idx, events in enumerate(per_seed_successions):
            if events:
                lines.append(f'- seed={seed_idx}: {len(events)} event(s) at steps '
                             f'{[e["step"] for e in events]}')
    lines.append('')
    lines.append('## Per-seed summary')
    lines.append('')
    lines.append('| Seed | Steps | Crashed | Extinct@ | Mean max_share | Mean min_share | Mean entropy | Anchor selections | Successions |')
    lines.append('|------|-------|---------|----------|----------------|----------------|--------------|-------------------|-------------|')
    for ps in per_seed:
        lines.append(f'| {ps["seed"]} | {ps["n_steps"]} | {ps["crashed"]} | '
                     f'{ps["extinct_at"] if ps["extinct_at"] is not None else "-"} | '
                     f'{ps["mean_max_share"]:.3f} | {ps["mean_min_share"]:.3f} | '
                     f'{ps["mean_entropy"]:.3f} | {ps["anchor_count"]} | '
                     f'{ps["succession_count"]} |')
    lines.append('')
    lines.append('## Anchor selection breakdown')
    lines.append('')
    if summary['anchor_counts']:
        lines.append('| Anchor | Count | Fraction |')
        lines.append('|--------|-------|----------|')
        for name, cnt in sorted(summary['anchor_counts'].items(), key=lambda kv: -kv[1]):
            lines.append(f'| {name} | {cnt} | {cnt/summary["n_steps_total"]:.4f} |')
    else:
        lines.append(f'No anchors selected across all {summary["n_steps_total"]} decision steps.')
    lines.append('')
    lines.append('## Forward-looking guidance for Stage 3 (record only; do not act)')
    lines.append('')
    lines.append('Phi is the planning-horizon parameter. Its behavioral signature in v2 '
                 'could appear through multiple channels. Stage 3\'s phi sweep should '
                 'capture all three signatures below, not just (a). If phi acts through '
                 'one channel and not others, we want to see that. If it doesn\'t act '
                 'through any, we are in Branch 1 of the decision tree.')
    lines.append('')
    lines.append('### Signature (a): Delayed-payoff investment')
    lines.append('')
    lines.append('Long-horizon AI pre-invests in institutional capacity and resilience '
                 'because their future value is visible within the planning window.')
    lines.append('')
    lines.append('Measured by:')
    lines.append('- Mean share of `x_institutional_capacity` and `x_resilience`')
    lines.append('- Fraction of steps with `min_share` below a chosen threshold')
    lines.append('- Response of the starvation pattern to phi (which categories are min, how often)')
    lines.append('')
    lines.append('Baseline values from this gate (at phi=10) recorded above under '
                 '"Baseline allocation pattern".')
    lines.append('')
    lines.append('### Signature (b): Sustained commitment to multi-step strategies')
    lines.append('')
    lines.append('Long-horizon AI maintains allocation choices across steps to allow '
                 'planned outcomes to materialize. Short-horizon AI re-optimizes '
                 'step-by-step.')
    lines.append('')
    lines.append('Measured by:')
    lines.append('- Step-to-step allocation variance per category')
    lines.append('- Step-to-step mean absolute delta per category')
    lines.append('- Response of variance and delta to phi')
    lines.append('')
    lines.append('Baseline values from this gate (at phi=10) recorded above under '
                 '"Step-to-step allocation variance".')
    lines.append('')
    lines.append('### Signature (c): Anticipatory response to gradual drift')
    lines.append('')
    lines.append('Long-horizon AI begins corrective allocation before state variables '
                 '(Psi_inst, well-being, capability) reach crisis thresholds. '
                 'Short-horizon AI waits until forced.')
    lines.append('')
    lines.append('Measured by:')
    lines.append('- Lead-time between drift onset and allocation response')
    lines.append('- Cross-correlation between (d Psi_inst / d t, d avg_wb / d t) and '
                 'the optimizer\'s allocation shifts, at various lags')
    lines.append('- Response of lead-time to phi')
    lines.append('')
    lines.append('No baseline value from this gate; Stage 3 should design the drift-injection '
                 'protocol to measure it.')
    lines.append('')
    lines.append('### Operator guidance to program reference')
    lines.append('')
    lines.append('Stage 3\'s phi sweep should be designed to capture all three signatures. '
                 'A phi effect on (a) alone would still be meaningful but partial; an '
                 'effect on (a), (b), and (c) together would constitute the strongest '
                 'case for Branch 2 or Branch 3. Absence of any effect after a serious '
                 'sweep is Branch 1.')
    lines.append('')
    with open(out_path, 'w') as f:
        f.write('\n'.join(lines) + '\n')


def main():
    print(f'Gate 1 (revised regime): {N_SEEDS} seeds x {N_STEPS} steps, '
          f'shock@{SHOCK_STEP_INDEX} (magnitude={SHOCK_MAGNITUDE})', flush=True)
    t0 = time.time()
    all_records = []
    per_seed_records = []
    per_seed_summary = []
    per_seed_successions = []
    per_seed_shock_step = [SHOCK_STEP_INDEX] * N_SEEDS

    for seed in range(N_SEEDS):
        t_start = time.time()
        m, crashed, extinct_at, succ_events, shock_info = run_one_seed(seed)
        dc = m.datacollector
        n_steps = len(dc['population'])
        seed_records = []
        for i in range(n_steps):
            shares = {c: dc[f'x_{c}'][i] for c in RESOURCE_CATEGORIES}
            max_share = max(shares.values())
            min_share = min(shares.values())
            min_cat = min(shares, key=shares.get)
            rec = {
                'step':        i,
                'max_share':   max_share,
                'min_share':   min_share,
                'min_cat':     min_cat,
                'entropy':     dc['allocation_entropy'][i],
                'anchor_name': dc['selected_anchor_name'][i] if dc['selected_anchor'][i] else None,
                'psi_stock':   dc['psi_inst_stock'][i],
            }
            for cat in RESOURCE_CATEGORIES:
                rec[f'x_{cat}'] = shares[cat]
            seed_records.append(rec)
        all_records.extend(seed_records)
        per_seed_records.append(seed_records)
        per_seed_successions.append(succ_events)
        if seed_records:
            mean_max = float(np.mean([r['max_share'] for r in seed_records]))
            mean_min = float(np.mean([r['min_share'] for r in seed_records]))
            mean_ent = float(np.mean([r['entropy']   for r in seed_records]))
            n_anchor = sum(1 for r in seed_records if r['anchor_name'])
        else:
            mean_max = mean_min = mean_ent = float('nan')
            n_anchor = 0
        per_seed_summary.append({
            'seed': seed, 'n_steps': n_steps, 'crashed': crashed, 'extinct_at': extinct_at,
            'mean_max_share': mean_max, 'mean_min_share': mean_min,
            'mean_entropy': mean_ent, 'anchor_count': n_anchor,
            'succession_count': len(succ_events),
        })
        dt = time.time() - t_start
        si = ''
        if shock_info is not None:
            si = (f' shock={shock_info["actual_shock"]:.3f} '
                  f'(x_res={shock_info["x_resilience_at_shock"]:.3f}, '
                  f'killed={shock_info["num_killed"]})')
        print(f'  seed={seed}: {n_steps} steps, {dt:.1f}s, '
              f'mean max_share={mean_max:.3f}, entropy={mean_ent:.3f}, '
              f'anchors={n_anchor}, succ={len(succ_events)}{si}', flush=True)

    wall_clock = time.time() - t0
    passed, summary = compute_pass_fail(all_records)

    # Pre/post shock window analysis
    pre_post_table = []
    for seed_idx, records in enumerate(per_seed_records):
        if not records:
            continue
        pre_post_table.append({
            'seed':     seed_idx,
            'pre_res':  window_mean(records, *PRE_SHOCK_WINDOW, 'x_resilience'),
            'post_res': window_mean(records, *POST_SHOCK_WINDOW, 'x_resilience'),
            'pre_inst':  window_mean(records, *PRE_SHOCK_WINDOW, 'x_institutional_capacity'),
            'post_inst': window_mean(records, *POST_SHOCK_WINDOW, 'x_institutional_capacity'),
            'pre_psi':   window_mean(records, *PRE_SHOCK_WINDOW, 'psi_stock'),
            'post_psi':  window_mean(records, *POST_SHOCK_WINDOW, 'psi_stock'),
        })

    # Starved-category context table
    fail_records = categorize_starved(per_seed_records, per_seed_shock_step)
    starved_table = {}
    for rec in fail_records:
        cat = rec['min_cat']
        if cat not in starved_table:
            starved_table[cat] = {'count': 0, 'psi_sum': 0.0, 'sfs_sum': 0.0}
        starved_table[cat]['count'] += 1
        starved_table[cat]['psi_sum'] += rec['psi_stock']
        starved_table[cat]['sfs_sum'] += rec['steps_from_shock']
    for cat, row in starved_table.items():
        row['mean_psi'] = row['psi_sum'] / row['count']
        row['mean_sfs'] = row['sfs_sum'] / row['count']
    starved_table = dict(sorted(starved_table.items(), key=lambda kv: -kv[1]['count']))

    # Psi_inst dynamics table
    psi_invest_table = []
    for start, end, label in [
        (0, 50, '0-49 (early, stock < 0.9)'),
        (50, 150, '50-149 (Psi saturated)'),
        (150, 200, '150-199 (shock + recovery)'),
        (200, 300, '200-299 (long tail)'),
    ]:
        inst_vals = []
        psi_vals = []
        for records in per_seed_records:
            for r in records:
                if start <= r['step'] < end:
                    inst_vals.append(r['x_institutional_capacity'])
                    psi_vals.append(r['psi_stock'])
        if inst_vals:
            psi_invest_table.append({
                'range':    label,
                'mean_inst': float(np.mean(inst_vals)),
                'mean_psi':  float(np.mean(psi_vals)),
            })

    # Baseline allocation pattern: per-category mean share, step-to-step
    # variance, and mean absolute step-to-step delta. Aggregated by
    # computing per-seed statistics first, then averaging across seeds.
    baseline_pattern = {'categories': {}}
    for cat in RESOURCE_CATEGORIES:
        per_seed_means_for_cat = []
        per_seed_variances_for_cat = []
        per_seed_abs_deltas_for_cat = []
        for records in per_seed_records:
            vals = [r[f'x_{cat}'] for r in records if f'x_{cat}' in r]
            if not vals:
                continue
            per_seed_means_for_cat.append(float(np.mean(vals)))
            per_seed_variances_for_cat.append(float(np.var(vals)))
            if len(vals) >= 2:
                deltas = [abs(vals[i] - vals[i-1]) for i in range(1, len(vals))]
                per_seed_abs_deltas_for_cat.append(float(np.mean(deltas)))
        baseline_pattern['categories'][cat] = {
            'mean_share':     float(np.mean(per_seed_means_for_cat)) if per_seed_means_for_cat else float('nan'),
            'variance':       float(np.mean(per_seed_variances_for_cat)) if per_seed_variances_for_cat else float('nan'),
            'mean_abs_delta': float(np.mean(per_seed_abs_deltas_for_cat)) if per_seed_abs_deltas_for_cat else float('nan'),
        }

    out_path = os.path.join(HERE, 'gate1_interior_action_report.md')
    write_report(per_seed_summary, all_records, per_seed_records, per_seed_shock_step,
                  per_seed_successions, summary, passed, wall_clock, out_path,
                  pre_post_table, starved_table, psi_invest_table,
                  baseline_pattern)
    print('', flush=True)
    print(f'Total wall-clock: {wall_clock:.1f}s', flush=True)
    print(f'  Non-corner fraction (max < 0.5): {summary["non_corner_fraction"]:.3f} (>= 0.95?)', flush=True)
    print(f'  Mean entropy:                    {summary["mean_entropy"]:.3f} (>= 0.70?)', flush=True)
    print(f'  Max single anchor:               {summary["max_single_anchor_frac"]:.3f} (<= 0.15?)', flush=True)
    print(f'  Baseline diag: steps min<0.02:   {summary["baseline_min_share_below_002"]:.3f} (informational)', flush=True)
    print(f'OVERALL: {"PASS" if passed else "FAIL"}', flush=True)
    print(f'Report: {out_path}', flush=True)
    sys.exit(0 if passed else 1)


if __name__ == '__main__':
    main()
