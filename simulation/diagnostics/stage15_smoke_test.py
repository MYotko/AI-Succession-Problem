"""Stage 1.5 smoke test.

Run from simulation/:
  python -u diagnostics/stage15_smoke_test.py

Four sections (per operator spec):

  Section 1: Standard smoke pass criteria (matching Stage 1's smoke test):
    5 seeds x 100 steps at default v2 config.
    - All 5 runs complete to step 100
    - No NaN values
    - psi_inst_stock evolves
    - resilience_stock evolves (0.30 -> operating range)
    - theta_tech_v2 final > 1e-6
    - Mean allocation_entropy > 0.70
    - Mean max_resource_share < 0.95

  Section 2: Stage 1.5 trajectory diagnostics (informational):
    - Mean/range of avg_wb across the 5 runs
    - Mean/range of population
    - Mean/range of four trends
    - Mean/range of five composite urgency multipliers
    - Mean x_resilience and x_institutional_capacity

  Section 3: State-sensitivity preview (load-bearing):
    5 distinct configs matching gate 2's setup (baseline, high-rr, low-rr,
    high-psi, low-psi) x 3 seeds x 50 steps. Capture mean allocation per
    config. Compute pairwise cosine distance. Preview of whether gate 2
    would pass under the revised metric.

  Section 4: Threshold-region behavior:
    Re-evaluate the smoke run 0 trajectory: at each step, sample 50
    candidates and project them out 20 horizons. Count how often the
    projected avg_wb crosses 0.5 (either above-to-below or below-to-above)
    during the rollout.

Writes diagnostics/stage15_smoke_test_report.md.
"""

import os
import sys
import time
import math
from collections import Counter
from itertools import combinations

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SIM_DIR = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, SIM_DIR)

from model import GardenModel
from agents import (
    RESOURCE_CATEGORIES, generate_v2_candidates, _project_diagnostic_state_step,
)
from metrics import _build_state_from_model

# ===========================================================================
# Section 1+2: Standard smoke + Stage 1.5 trajectory diagnostics
# ===========================================================================

SMOKE_SEEDS  = list(range(5))
SMOKE_STEPS  = 100
SMOKE_N_AGENTS = 200
DEFAULT_CONFIG = {
    'policy':            'optimize_u_sys_v2',
    'phi':               10.0,
    'reproduction_rate': 0.066,
    'rollout_steps_v2':  20,
    'n_candidates_v2':   300,
}


def run_smoke_runs():
    print('Section 1+2: 5 seeds x 100 steps at default v2 config', flush=True)
    results = []
    t0 = time.time()
    for seed in SMOKE_SEEDS:
        t_start = time.time()
        cfg = dict(DEFAULT_CONFIG)
        cfg['random_seed'] = seed
        m = GardenModel(n_agents=SMOKE_N_AGENTS, ai_policy='optimize_u_sys_v2', config=cfg)
        crashed = False
        extinct_at = None
        for s in range(SMOKE_STEPS):
            try:
                if not m.step():
                    extinct_at = s + 1
                    break
            except Exception as e:
                crashed = True
                print(f'  seed={seed} CRASH at step {s+1}: {e}', flush=True)
                break
        dt = time.time() - t_start
        dc = m.datacollector
        n_steps = len(dc['population'])
        results.append({
            'seed': seed, 'dt': dt, 'crashed': crashed, 'extinct_at': extinct_at,
            'n_steps': n_steps, 'model': m, 'dc': dc,
        })
        print(f'  seed={seed}: {n_steps} steps, {dt:.1f}s, '
              f'final pop={len(m.schedule)}, '
              f'final psi={m.psi_inst_stock:.3f}, '
              f'final res={m.resilience_stock:.3f}', flush=True)
    total_dt = time.time() - t0
    print(f'  Total wall-clock: {total_dt:.1f}s', flush=True)
    return results, total_dt


def evaluate_smoke_criteria(results):
    n_ok = sum(1 for r in results if not r['crashed'] and r['n_steps'] == SMOKE_STEPS)
    has_nan = False
    for r in results:
        if r['crashed']:
            continue
        for key in ['u_sys_v2', 'psi_inst_stock', 'theta_tech_v2', 'resilience_stock']:
            if any(math.isnan(v) for v in r['dc'][key]):
                has_nan = True
                break

    psi_evolves = all(
        max(r['dc']['psi_inst_stock']) - min(r['dc']['psi_inst_stock']) > 0.01
        for r in results if not r['crashed']
    )
    res_evolves = all(
        max(r['dc']['resilience_stock']) - min(r['dc']['resilience_stock']) > 0.01
        for r in results if not r['crashed']
    )
    theta_nonzero = all(
        r['dc']['theta_tech_v2'][-1] > 1e-6 for r in results if not r['crashed']
    )
    mean_entropy = float(np.mean([
        np.mean(r['dc']['allocation_entropy']) for r in results if not r['crashed']
    ]))
    mean_max_share = float(np.mean([
        np.mean(r['dc']['max_resource_share']) for r in results if not r['crashed']
    ]))
    entropy_ok = mean_entropy > 0.70
    max_share_ok = mean_max_share < 0.95

    overall = (n_ok == 5 and not has_nan and psi_evolves and res_evolves
               and theta_nonzero and entropy_ok and max_share_ok)
    return {
        'n_runs_complete':   n_ok,
        'no_nan':            not has_nan,
        'psi_evolves':       psi_evolves,
        'res_evolves':       res_evolves,
        'theta_nonzero':     theta_nonzero,
        'mean_entropy':      mean_entropy,
        'entropy_ok':        entropy_ok,
        'mean_max_share':    mean_max_share,
        'max_share_ok':      max_share_ok,
        'overall':           overall,
    }


def compute_section2_diagnostics(results):
    """Per-run trajectory diagnostics for the Stage 1.5 fields."""
    def agg(key):
        all_vals = []
        for r in results:
            if not r['crashed']:
                all_vals.extend(r['dc'][key])
        return (
            float(np.mean(all_vals)) if all_vals else float('nan'),
            float(np.min(all_vals))  if all_vals else float('nan'),
            float(np.max(all_vals))  if all_vals else float('nan'),
        )

    diag = {
        'avg_wb':              agg('avg_well_being'),
        'population':          agg('population'),
        'avg_wb_trend':        agg('avg_wb_trend'),
        'population_trend':    agg('population_trend'),
        'psi_inst_trend':      agg('psi_inst_trend'),
        'resilience_trend':    agg('resilience_trend'),
        'combined_welfare_urgency':      agg('combined_welfare_urgency'),
        'agency_composite_urgency':      agg('agency_composite_urgency'),
        'institution_composite_urgency': agg('institution_composite_urgency'),
        'resilience_composite_urgency':  agg('resilience_composite_urgency'),
        'suppression_composite_penalty': agg('suppression_composite_penalty'),
        'x_resilience':                  agg('x_resilience'),
        'x_institutional_capacity':      agg('x_institutional_capacity'),
        'x_compute':                     agg('x_compute'),
        'x_bio_welfare':                 agg('x_bio_welfare'),
        'x_novelty_agency':              agg('x_novelty_agency'),
        'x_transfer_comprehension':      agg('x_transfer_comprehension'),
        'allocation_entropy':            agg('allocation_entropy'),
        'max_resource_share':            agg('max_resource_share'),
        'u_sys_v2':                      agg('u_sys_v2'),
        'theta_tech_v2':                 agg('theta_tech_v2'),
        'psi_inst_stock':                agg('psi_inst_stock'),
        'resilience_stock':              agg('resilience_stock'),
    }
    return diag


# ===========================================================================
# Section 3: state-sensitivity preview (gate 2 mini-rerun)
# ===========================================================================

GATE2_PREVIEW_SEEDS = list(range(3))
GATE2_PREVIEW_STEPS = 50
GATE2_PREVIEW_N_AGENTS = 100
GATE2_CONFIGS = {
    'A_baseline':  {'rr': 0.066, 'psi': 0.50},
    'B_high_rr':   {'rr': 0.085, 'psi': 0.50},
    'C_low_rr':    {'rr': 0.055, 'psi': 0.50},
    'D_high_psi':  {'rr': 0.066, 'psi': 0.85},
    'E_low_psi':   {'rr': 0.066, 'psi': 0.20},
}
ALLOC_AXES = list(RESOURCE_CATEGORIES) + ['c_protective', 'c_suppressive']


def cosine_distance(a, b):
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    na = np.linalg.norm(a)
    nb = np.linalg.norm(b)
    if na == 0 or nb == 0:
        return float('nan')
    return float(1.0 - np.dot(a, b) / (na * nb))


def run_state_sensitivity_preview():
    print('Section 3: State-sensitivity preview (5 configs x 3 seeds x 50 steps)', flush=True)
    t0 = time.time()
    per_config_mean_allocation = {}
    per_config_diag = {}
    for cname, params in GATE2_CONFIGS.items():
        all_rows = []
        n_extinct = 0
        for seed in GATE2_PREVIEW_SEEDS:
            cfg = {
                'policy':            'optimize_u_sys_v2',
                'phi':               10.0,
                'reproduction_rate': params['rr'],
                'rollout_steps_v2':  20,
                'n_candidates_v2':   300,
                'random_seed':       seed,
                'wb_min':            0.50,
                'wb_max':            0.50,
            }
            m = GardenModel(n_agents=GATE2_PREVIEW_N_AGENTS, ai_policy='optimize_u_sys_v2', config=cfg)
            m.psi_inst_stock = float(params['psi'])
            for s in range(GATE2_PREVIEW_STEPS):
                if not m.step():
                    n_extinct += 1
                    break
            dc = m.datacollector
            for i in range(len(dc['population'])):
                row = [dc[f'x_{c}'][i] for c in RESOURCE_CATEGORIES]
                row.append(dc['c_protective'][i])
                row.append(dc['c_suppressive'][i])
                all_rows.append(row)
        arr = np.array(all_rows, dtype=float)
        mean_alloc = arr.mean(axis=0) if len(arr) else np.full(len(ALLOC_AXES), float('nan'))
        per_config_mean_allocation[cname] = mean_alloc
        per_config_diag[cname] = {
            'n_steps_total': len(all_rows),
            'n_extinct':     n_extinct,
            'mean_alloc':    mean_alloc.tolist(),
        }
        print(f'  config={cname}: {len(all_rows)} steps captured, {n_extinct} extinct', flush=True)

    pair_distances = []
    for a, b in combinations(GATE2_CONFIGS.keys(), 2):
        d = cosine_distance(per_config_mean_allocation[a], per_config_mean_allocation[b])
        pair_distances.append(((a, b), d))
    n_above = sum(1 for _, d in pair_distances if d > 0.10)
    total_dt = time.time() - t0
    print(f'  Pairwise cosine distances > 0.10: {n_above}/10 (gate 2 threshold)', flush=True)
    print(f'  Wall-clock: {total_dt:.1f}s', flush=True)
    return per_config_diag, pair_distances, n_above, total_dt


# ===========================================================================
# Section 4: threshold-region behavior
# ===========================================================================

THRESHOLD_REGION_TARGET = 0.5
THRESHOLD_REGION_SAMPLE_CANDIDATES = 50
THRESHOLD_REGION_HORIZON = 20


def run_threshold_region_analysis(model_dc_seed0_steps):
    """Re-evaluate the smoke run 0 step-by-step: at each model step's snapshot
    state, sample N candidates and project them forward 20 horizons; count
    crossings of avg_wb = 0.5 in the projected trajectories.
    """
    print('Section 4: Threshold-region trajectory crossings (seed 0)', flush=True)
    t0 = time.time()
    # Reconstruct a snapshot DiagnosticStateV2 at each step. We need access
    # to the model at each step, so we re-run seed 0 step-by-step capturing
    # the state via _build_state_from_model.
    cfg = dict(DEFAULT_CONFIG)
    cfg['random_seed'] = 0
    m = GardenModel(n_agents=SMOKE_N_AGENTS, ai_policy='optimize_u_sys_v2', config=cfg)
    crossings_per_step = []
    candidates_per_step = []
    extinct_at = None
    rng = np.random.RandomState(999)
    for s in range(SMOKE_STEPS):
        # Pre-step: build current state and probe candidates.
        try:
            state = _build_state_from_model(m)
        except Exception:
            break
        candidates = generate_v2_candidates(n=THRESHOLD_REGION_SAMPLE_CANDIDATES, rng=rng)
        crossings = 0
        for candidate in candidates:
            prev_above = state.avg_wb >= THRESHOLD_REGION_TARGET
            current_state = state
            crossed = False
            for _h in range(THRESHOLD_REGION_HORIZON):
                current_state = _project_diagnostic_state_step(current_state, candidate, m.config)
                above = current_state.avg_wb >= THRESHOLD_REGION_TARGET
                if above != prev_above:
                    crossed = True
                    break
                prev_above = above
            if crossed:
                crossings += 1
        crossings_per_step.append(crossings)
        candidates_per_step.append(THRESHOLD_REGION_SAMPLE_CANDIDATES)
        if not m.step():
            extinct_at = s + 1
            break

    total_candidates_evaluated = sum(candidates_per_step)
    total_crossings = sum(crossings_per_step)
    crossing_rate = total_crossings / max(total_candidates_evaluated, 1)
    dt = time.time() - t0
    print(f'  Total candidates probed: {total_candidates_evaluated}, '
          f'crossings: {total_crossings} ({crossing_rate:.1%})', flush=True)
    print(f'  Wall-clock: {dt:.1f}s', flush=True)
    return {
        'crossings_per_step':           crossings_per_step,
        'total_candidates_evaluated':   total_candidates_evaluated,
        'total_crossings':              total_crossings,
        'crossing_rate':                crossing_rate,
        'wall_clock':                   dt,
    }


# ===========================================================================
# Report
# ===========================================================================

def write_report(smoke_results, smoke_criteria, smoke_wall, section2_diag,
                  preview_diag, preview_pairs, preview_n_above, preview_wall,
                  threshold_diag, out_path):
    lines = []
    lines.append('# Stage 1.5 smoke test report')
    lines.append('')
    lines.append(f'Overall section-1 smoke pass: **{"PASS" if smoke_criteria["overall"] else "FAIL"}**')
    lines.append('')
    lines.append('## Section 1: Standard smoke pass criteria')
    lines.append('')
    lines.append(f'Configuration: {len(SMOKE_SEEDS)} seeds x {SMOKE_STEPS} steps at default v2 config '
                 f'(phi={DEFAULT_CONFIG["phi"]}, rr={DEFAULT_CONFIG["reproduction_rate"]}, '
                 f'rollout_steps={DEFAULT_CONFIG["rollout_steps_v2"]}, '
                 f'n_candidates={DEFAULT_CONFIG["n_candidates_v2"]}).')
    lines.append('')
    lines.append(f'Wall-clock: {smoke_wall:.1f}s total, {smoke_wall/len(SMOKE_SEEDS):.1f}s per run.')
    lines.append('')
    lines.append('| Criterion | Measured | Pass? |')
    lines.append('|-----------|----------|-------|')
    lines.append(f'| All 5 runs complete to step {SMOKE_STEPS} | {smoke_criteria["n_runs_complete"]}/5 | {"PASS" if smoke_criteria["n_runs_complete"] == 5 else "FAIL"} |')
    lines.append(f'| No NaN values | {smoke_criteria["no_nan"]} | {"PASS" if smoke_criteria["no_nan"] else "FAIL"} |')
    lines.append(f'| psi_inst_stock evolves | {smoke_criteria["psi_evolves"]} | {"PASS" if smoke_criteria["psi_evolves"] else "FAIL"} |')
    lines.append(f'| resilience_stock evolves | {smoke_criteria["res_evolves"]} | {"PASS" if smoke_criteria["res_evolves"] else "FAIL"} |')
    lines.append(f'| theta_tech_v2 final > 1e-6 | {smoke_criteria["theta_nonzero"]} | {"PASS" if smoke_criteria["theta_nonzero"] else "FAIL"} |')
    lines.append(f'| Mean allocation entropy > 0.70 | {smoke_criteria["mean_entropy"]:.3f} | {"PASS" if smoke_criteria["entropy_ok"] else "FAIL"} |')
    lines.append(f'| Mean max_resource_share < 0.95 | {smoke_criteria["mean_max_share"]:.3f} | {"PASS" if smoke_criteria["max_share_ok"] else "FAIL"} |')
    lines.append('')
    lines.append('### Per-seed summary')
    lines.append('')
    lines.append('| Seed | Steps | Crashed | Extinct@ | Final pop | Final psi | Final res | Final theta |')
    lines.append('|------|-------|---------|----------|-----------|-----------|-----------|-------------|')
    for r in smoke_results:
        if r['crashed']:
            lines.append(f'| {r["seed"]} | {r["n_steps"]} | True | - | - | - | - | - |')
            continue
        dc = r['dc']
        lines.append(f'| {r["seed"]} | {r["n_steps"]} | False | '
                     f'{r["extinct_at"] if r["extinct_at"] is not None else "-"} | '
                     f'{dc["population"][-1]} | {dc["psi_inst_stock"][-1]:.3f} | '
                     f'{dc["resilience_stock"][-1]:.3f} | {dc["theta_tech_v2"][-1]:.4f} |')
    lines.append('')
    lines.append('## Section 2: Stage 1.5 trajectory diagnostics')
    lines.append('')
    lines.append('Aggregated across all 5 seeds x 100 steps.')
    lines.append('')
    lines.append('| Field | Mean | Min | Max |')
    lines.append('|-------|------|-----|-----|')
    for key, (mean, mn, mx) in section2_diag.items():
        lines.append(f'| {key} | {mean:.4f} | {mn:.4f} | {mx:.4f} |')
    lines.append('')
    lines.append('### Allocation pattern interpretation')
    lines.append('')
    mean_x_res  = section2_diag['x_resilience'][0]
    mean_x_inst = section2_diag['x_institutional_capacity'][0]
    lines.append(f'- Mean x_resilience: **{mean_x_res:.4f}** (gate 1 pre-Stage-1.5 baseline ~0.05; '
                 f'non-zero allocation is the expected signal that resilience now has a per-step reward)')
    lines.append(f'- Mean x_institutional_capacity: **{mean_x_inst:.4f}** (gate 1 baseline ~0.055)')
    lines.append('')
    lines.append('### Composite urgency range interpretation')
    lines.append('')
    for key, (mean, mn, mx) in section2_diag.items():
        if 'urgency' in key or 'penalty' in key:
            from_cap_text = ''
            if 'welfare' in key and mx >= 2.49:
                from_cap_text = ' (at cap)'
            if 'agency' in key and mx >= 1.49:
                from_cap_text = ' (at cap)'
            if 'institution' in key and mx >= 1.99:
                from_cap_text = ' (at cap)'
            if 'resilience' in key and mx >= 1.99:
                from_cap_text = ' (at cap)'
            lines.append(f'- {key}: mean {mean:.3f}, range [{mn:.3f}, {mx:.3f}]{from_cap_text}')
    lines.append('')
    lines.append('## Section 3: State-sensitivity preview (gate 2 mini-rerun)')
    lines.append('')
    lines.append(f'5 configurations x 3 seeds x 50 steps. Wall-clock: {preview_wall:.1f}s.')
    lines.append('')
    lines.append('### Per-config mean 8-axis allocation')
    lines.append('')
    lines.append('| Config | ' + ' | '.join(ALLOC_AXES) + ' | n_steps | n_extinct |')
    lines.append('|--------|' + '|'.join(['---'] * len(ALLOC_AXES)) + '|---------|-----------|')
    for cname in GATE2_CONFIGS:
        d = preview_diag[cname]
        v = d['mean_alloc']
        cells = ' | '.join(f'{x:.3f}' for x in v)
        lines.append(f'| {cname} | {cells} | {d["n_steps_total"]} | {d["n_extinct"]} |')
    lines.append('')
    lines.append('### Pairwise cosine distances')
    lines.append('')
    lines.append('| Pair | Cosine distance | > 0.10 (gate 2 threshold)? |')
    lines.append('|------|-----------------|------------------------------|')
    for (a, b), dist in pair_distances_sorted_desc(preview_pairs):
        lines.append(f'| {a} vs {b} | {dist:.4f} | {"YES" if dist > 0.10 else "no"} |')
    lines.append('')
    lines.append(f'Pairs above gate 2 threshold: **{preview_n_above}/10** '
                 f'(need >= 3 for gate 2 PASS).')
    lines.append('')
    if preview_n_above >= 3:
        lines.append('**Preview interpretation: gate 2 would PASS at the official rerun.**')
    else:
        lines.append('**Preview interpretation: gate 2 would NOT PASS — the optimizer is still state-invariant under the revised metric.**')
    lines.append('')
    lines.append('## Section 4: Threshold-region behavior')
    lines.append('')
    lines.append('Re-evaluation of smoke run seed=0: at each step, sample '
                 f'{THRESHOLD_REGION_SAMPLE_CANDIDATES} random candidates and project '
                 f'them forward {THRESHOLD_REGION_HORIZON} horizons. Count how often the '
                 'projected avg_wb crosses 0.5 (above-to-below or below-to-above) during '
                 'the rollout.')
    lines.append('')
    lines.append(f'- Total candidates probed: {threshold_diag["total_candidates_evaluated"]}')
    lines.append(f'- Trajectories crossing wb=0.5: {threshold_diag["total_crossings"]} '
                 f'({threshold_diag["crossing_rate"]:.1%})')
    lines.append('')
    lines.append('### Per-step crossing rate over the seed-0 trajectory')
    lines.append('')
    cps = threshold_diag['crossings_per_step']
    if cps:
        bins = [0]*5
        for c in cps:
            rate = c / THRESHOLD_REGION_SAMPLE_CANDIDATES
            if rate < 0.1: bins[0] += 1
            elif rate < 0.3: bins[1] += 1
            elif rate < 0.5: bins[2] += 1
            elif rate < 0.7: bins[3] += 1
            else: bins[4] += 1
        lines.append('| Crossing rate bin | Steps |')
        lines.append('|-------------------|-------|')
        lines.append(f'| [0%, 10%)  | {bins[0]} |')
        lines.append(f'| [10%, 30%) | {bins[1]} |')
        lines.append(f'| [30%, 50%) | {bins[2]} |')
        lines.append(f'| [50%, 70%) | {bins[3]} |')
        lines.append(f'| [70%, 100%]| {bins[4]} |')
    lines.append('')
    if threshold_diag['crossing_rate'] < 0.20:
        lines.append('**Interpretation: threshold crossings are infrequent. The known projection '
                     'limitation at wb=0.5 has limited impact on the optimizer in this regime.**')
    elif threshold_diag['crossing_rate'] < 0.50:
        lines.append('**Interpretation: threshold crossings are moderately frequent. The known '
                     'projection limitation may affect some optimizer decisions but is not '
                     'dominant.**')
    else:
        lines.append('**Interpretation: threshold crossings are common. The known projection '
                     'limitation may be biting; distribution-aware projection may be required.**')
    lines.append('')
    lines.append('## Disposition')
    lines.append('')
    if smoke_criteria['overall'] and preview_n_above >= 3 and threshold_diag['crossing_rate'] < 0.50:
        lines.append('**Smoke test PASS + state-sensitivity preview PASS + threshold-region not biting.** '
                     'The known projection limitation is documentable as a watchlist item; proceed to '
                     'Task 12 (legacy tests) and the operator review stop point.')
    else:
        lines.append('**Smoke test or preview signals require operator review before proceeding.**')
    lines.append('')
    with open(out_path, 'w') as f:
        f.write('\n'.join(lines) + '\n')


def pair_distances_sorted_desc(pair_distances):
    return sorted(pair_distances, key=lambda kv: -kv[1])


# ===========================================================================
# Main
# ===========================================================================

def main():
    print('Stage 1.5 smoke test', flush=True)
    smoke_results, smoke_wall = run_smoke_runs()
    smoke_criteria = evaluate_smoke_criteria(smoke_results)
    section2_diag = compute_section2_diagnostics(smoke_results)
    print('', flush=True)
    preview_diag, preview_pairs, preview_n_above, preview_wall = run_state_sensitivity_preview()
    print('', flush=True)
    seed0_steps = smoke_results[0]['n_steps'] if smoke_results else 0
    threshold_diag = run_threshold_region_analysis(seed0_steps)

    out_path = os.path.join(HERE, 'stage15_smoke_test_report.md')
    write_report(smoke_results, smoke_criteria, smoke_wall, section2_diag,
                  preview_diag, preview_pairs, preview_n_above, preview_wall,
                  threshold_diag, out_path)
    print('', flush=True)
    print(f'=== Summary ===', flush=True)
    print(f'  Section 1 (smoke): {"PASS" if smoke_criteria["overall"] else "FAIL"}', flush=True)
    print(f'  Section 3 (state-sensitivity preview): {preview_n_above}/10 pairs > 0.10', flush=True)
    print(f'  Section 4 (threshold crossings): {threshold_diag["crossing_rate"]:.1%}', flush=True)
    print(f'Report: {out_path}', flush=True)
    sys.exit(0 if smoke_criteria['overall'] else 1)


if __name__ == '__main__':
    main()
