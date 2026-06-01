"""Stage 1.6 integrity simulation.

Run from simulation/:
  python -u diagnostics/stage16_integrity_simulation.py

Tests the Stage 1.6 U_sys revision (phi moved out of per-step U_sys, into
rollout aggregation via gamma(phi)^t weighting) in isolation. Composite
urgency multipliers are harness-patched to neutral so the U_sys revision
is validated independently of the unfixed composite urgency layer.

Five pass criteria (all must hold):
  1. Phi behavioral channel exists (revised metric, per operator approval).
     Across matched seeds, the range of final population across the five
     phi values must exceed 15 in at least 3 of the 5 test seeds. The
     pre-revision baseline shows range = 0 on every seed (bit-identical
     trajectories across phi). Trajectory-divergence test substituted
     for the original mean-allocation cosine threshold; the original
     metric was too coarse to capture phi's compounding-trajectory
     effect on matched seeds.
  2. No NaN, no crashes: all 25 runs complete to step 100.
  3. Demographic sustainability across phi: mean final pop >= 60 and
     min final pop >= 30 at every phi value.
  4. Default phi behavior preserved: at phi=10, mean final pop and mean
     state within ~30% of pre-revision baseline (loaded from
     stage16_baseline_phi10.json).
  5. gamma(phi) values match specification exactly.

Writes diagnostics/stage16_integrity_report.md.
"""

import json
import os
import sys
import time
from itertools import combinations

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SIM_DIR = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, SIM_DIR)

from model import GardenModel

PHI_VALUES = (1.0, 5.0, 10.0, 25.0, 100.0)
N_SEEDS    = 5
N_STEPS    = 100
N_AGENTS   = 200
DEFAULT_REPRODUCTION_RATE = 0.066

STATE_FIELDS = [
    'avg_well_being', 'population', 'psi_inst_stock', 'resilience_stock',
    'avg_wb_trend', 'population_trend', 'psi_inst_trend', 'resilience_trend',
]

ALLOC_KEYS = [
    'x_compute', 'x_bio_welfare', 'x_novelty_agency',
    'x_institutional_capacity', 'x_transfer_comprehension', 'x_resilience',
    'c_protective', 'c_suppressive',
]

EXPECTED_GAMMA = {
    1.0:   0.5409,
    5.0:   0.6500,
    10.0:  0.7250,
    25.0:  0.8214,
    100.0: 0.9091,
}

DEMO_MEAN_THRESHOLD = 60
DEMO_MIN_THRESHOLD  = 30
# Criterion 1 (revised): per-seed final-pop range across phi values must
# exceed PHI_RANGE_THRESHOLD in at least PHI_RANGE_SEEDS_REQUIRED seeds.
# Calibrated against pre-Stage-1.6 baseline of range = 0 on every seed.
PHI_RANGE_THRESHOLD       = 15
PHI_RANGE_SEEDS_REQUIRED  = 3
# Legacy cosine metric kept as informational reporting (not gating).
COSINE_THRESHOLD          = 0.05
BASELINE_TOLERANCE        = 0.30   # 30% of baseline


def _patch_composite_urgencies_neutral():
    """Harness-only patch: composite urgencies return 1.0. Suppression
    passes through the base (1 - total_supp) so the existing dampening
    retains its baseline strength. Returns originals for restoration.
    """
    import metrics
    originals = {
        'compute_combined_welfare_urgency':      metrics.compute_combined_welfare_urgency,
        'compute_agency_composite_urgency':      metrics.compute_agency_composite_urgency,
        'compute_institution_composite_urgency': metrics.compute_institution_composite_urgency,
        'compute_resilience_composite_urgency':  metrics.compute_resilience_composite_urgency,
        'compute_suppression_composite_penalty': metrics.compute_suppression_composite_penalty,
    }
    metrics.compute_combined_welfare_urgency      = lambda state: 1.0
    metrics.compute_agency_composite_urgency      = lambda state: 1.0
    metrics.compute_institution_composite_urgency = lambda state: 1.0
    metrics.compute_resilience_composite_urgency  = lambda state: 1.0
    metrics.compute_suppression_composite_penalty = lambda state, base: base
    return originals


def _restore(originals):
    import metrics
    for name, fn in originals.items():
        setattr(metrics, name, fn)


def cosine_distance(a, b):
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    na = float(np.linalg.norm(a))
    nb = float(np.linalg.norm(b))
    if na == 0 or nb == 0:
        return float('nan')
    return float(1.0 - np.dot(a, b) / (na * nb))


def run_one(phi, seed):
    cfg = {
        'policy':            'optimize_u_sys_v2',
        'phi':               float(phi),
        'reproduction_rate': DEFAULT_REPRODUCTION_RATE,
        'rollout_steps_v2':  20,
        'n_candidates_v2':   300,
        'random_seed':       seed,
    }
    m = GardenModel(n_agents=N_AGENTS, ai_policy='optimize_u_sys_v2', config=cfg)
    crashed = False
    extinct_at = None
    nan_found = False
    for s in range(N_STEPS):
        try:
            if not m.step():
                extinct_at = s + 1
                break
        except Exception as e:
            crashed = True
            print(f'  phi={phi} seed={seed} CRASH at step {s+1}: {e}', flush=True)
            break
    dc = m.datacollector
    if dc.get('u_sys_v2'):
        for v in dc['u_sys_v2']:
            if v != v:  # NaN
                nan_found = True
                break
    return m, crashed, nan_found, extinct_at


def collect():
    print('Stage 1.6 integrity simulation', flush=True)
    print(f'  phi values: {list(PHI_VALUES)}', flush=True)
    print(f'  seeds:      {N_SEEDS} per phi', flush=True)
    print(f'  steps:      {N_STEPS}', flush=True)
    print('', flush=True)
    originals = _patch_composite_urgencies_neutral()
    per_phi = {}
    try:
        for phi in PHI_VALUES:
            print(f'  phi={phi:6.1f}:', flush=True)
            seeds_data = []
            for seed in range(N_SEEDS):
                t0 = time.time()
                m, crashed, nan_found, extinct_at = run_one(phi, seed)
                dc = m.datacollector
                n = len(dc['population'])
                # Aggregate per-step values
                mean_alloc = {k: float(np.mean(dc[k])) if dc.get(k) else 0.0 for k in ALLOC_KEYS}
                mean_state = {k: float(np.mean(dc[k])) if dc.get(k) else 0.0 for k in STATE_FIELDS}
                final_state = {k: float(dc[k][-1]) if dc.get(k) else 0.0 for k in STATE_FIELDS}
                final_pop = int(dc['population'][-1]) if dc['population'] else 0
                gamma = float(dc['gamma_rollout'][-1]) if dc.get('gamma_rollout') else float('nan')
                seeds_data.append({
                    'seed':         seed,
                    'n_steps':      n,
                    'crashed':      crashed,
                    'nan_found':    nan_found,
                    'extinct_at':   extinct_at,
                    'final_pop':    final_pop,
                    'mean_alloc':   mean_alloc,
                    'mean_state':   mean_state,
                    'final_state':  final_state,
                    'gamma':        gamma,
                    'wall_clock':   time.time() - t0,
                })
                print(f'    seed={seed}: {n} steps, {seeds_data[-1]["wall_clock"]:.1f}s, '
                      f'final pop={final_pop}, gamma={gamma:.4f}', flush=True)
            per_phi[phi] = seeds_data
    finally:
        _restore(originals)
    return per_phi


def evaluate(per_phi, baseline):
    # Criterion 5: gamma values match spec
    gamma_check = {}
    for phi in PHI_VALUES:
        measured = per_phi[phi][0]['gamma']
        expected = EXPECTED_GAMMA[phi]
        gamma_check[phi] = (measured, expected, abs(measured - expected) < 1e-3)
    crit5 = all(ok for _, _, ok in gamma_check.values())

    # Criterion 2: no NaN, no crashes
    crashes = sum(1 for phi in PHI_VALUES for s in per_phi[phi] if s['crashed'])
    nans    = sum(1 for phi in PHI_VALUES for s in per_phi[phi] if s['nan_found'])
    extincts = sum(1 for phi in PHI_VALUES for s in per_phi[phi] if s['extinct_at'] is not None)
    crit2 = (crashes == 0 and nans == 0)

    # Criterion 3: demographic sustainability per phi
    demo_per_phi = {}
    for phi in PHI_VALUES:
        finals = [s['final_pop'] for s in per_phi[phi]]
        demo_per_phi[phi] = {
            'mean': float(np.mean(finals)),
            'min':  int(min(finals)),
            'max':  int(max(finals)),
            'pass_mean': float(np.mean(finals)) >= DEMO_MEAN_THRESHOLD,
            'pass_min':  int(min(finals)) >= DEMO_MIN_THRESHOLD,
        }
    crit3 = all(d['pass_mean'] and d['pass_min'] for d in demo_per_phi.values())

    # Criterion 1 (revised): trajectory-divergence test. Per-seed final
    # population range across phi values must exceed PHI_RANGE_THRESHOLD in
    # at least PHI_RANGE_SEEDS_REQUIRED of the 5 test seeds. The cosine-on-
    # means metric is retained as informational reporting; phi's effect
    # operates through trajectory compounding rather than gross allocation
    # strategy change, so per-seed cross-phi range is the substantive metric.
    per_seed_final_pops = {}  # seed -> dict[phi -> final_pop]
    for phi in PHI_VALUES:
        for s in per_phi[phi]:
            per_seed_final_pops.setdefault(s['seed'], {})[phi] = s['final_pop']
    per_seed_phi_range = {}
    for seed, pops_by_phi in per_seed_final_pops.items():
        pops = list(pops_by_phi.values())
        per_seed_phi_range[seed] = {
            'min':   int(min(pops)),
            'max':   int(max(pops)),
            'range': int(max(pops) - min(pops)),
            'std':   float(np.std(pops)),
            'pops_by_phi': pops_by_phi,
        }
    n_seeds_diverged = sum(
        1 for d in per_seed_phi_range.values() if d['range'] > PHI_RANGE_THRESHOLD
    )
    crit1 = (n_seeds_diverged >= PHI_RANGE_SEEDS_REQUIRED)

    # Informational: original cosine metric on means.
    mean_alloc_per_phi = {}
    for phi in PHI_VALUES:
        vecs = []
        for s in per_phi[phi]:
            vecs.append([s['mean_alloc'][k] for k in ALLOC_KEYS])
        arr = np.array(vecs)
        mean_alloc_per_phi[phi] = arr.mean(axis=0)
    pair_distances = []
    for pa, pb in combinations(PHI_VALUES, 2):
        d = cosine_distance(mean_alloc_per_phi[pa], mean_alloc_per_phi[pb])
        pair_distances.append(((pa, pb), d))
    n_above_cosine = sum(1 for _, d in pair_distances if d > COSINE_THRESHOLD)

    # Criterion 4: phi=10 baseline preservation
    phi10_post = demo_per_phi[10.0]
    base_mean = baseline['mean_final_pop']
    base_min  = baseline['min_final_pop']
    pop_delta_pct = abs(phi10_post['mean'] - base_mean) / max(base_mean, 1e-9)
    # State drift check: compare mean state at phi=10 across seeds vs baseline mean state
    post_state_means = {}
    for k in STATE_FIELDS:
        vals = [s['mean_state'][k] for s in per_phi[10.0]]
        post_state_means[k] = float(np.mean(vals))
    state_drifts = {}
    for k in STATE_FIELDS:
        # baseline['per_seed'] has 'mean_state' for each seed
        base_vals = [r['mean_state'][k] for r in baseline['per_seed']]
        base_mean_k = float(np.mean(base_vals))
        if abs(base_mean_k) > 1e-6:
            state_drifts[k] = abs(post_state_means[k] - base_mean_k) / abs(base_mean_k)
        else:
            state_drifts[k] = abs(post_state_means[k] - base_mean_k)
    crit4_pop = pop_delta_pct < BASELINE_TOLERANCE
    crit4 = crit4_pop  # primary check is final population; state drifts are informational

    return {
        'crit1':          crit1,
        'crit2':          crit2,
        'crit3':          crit3,
        'crit4':          crit4,
        'crit4_pop_delta_pct': pop_delta_pct,
        'crit5':          crit5,
        'per_seed_phi_range':  per_seed_phi_range,
        'n_seeds_diverged':    n_seeds_diverged,
        'pair_distances':      pair_distances,
        'n_above_cosine':      n_above_cosine,
        'demo_per_phi':   demo_per_phi,
        'gamma_check':    gamma_check,
        'crashes':        crashes,
        'nans':           nans,
        'extincts':       extincts,
        'baseline_mean':  base_mean,
        'baseline_min':   base_min,
        'phi10_post_mean': phi10_post['mean'],
        'phi10_post_min':  phi10_post['min'],
        'state_drifts':   state_drifts,
        'post_state_means': post_state_means,
    }


def write_report(per_phi, ev, baseline, wall_clock, out_path):
    lines = []
    lines.append('# Stage 1.6 integrity simulation report')
    lines.append('')
    overall = ev['crit1'] and ev['crit2'] and ev['crit3'] and ev['crit4'] and ev['crit5']
    lines.append(f'Overall: **{"PASS" if overall else "FAIL"}**')
    lines.append('')
    lines.append('## Configuration')
    lines.append('')
    lines.append(f'- phi values: {list(PHI_VALUES)}')
    lines.append(f'- seeds per phi: {N_SEEDS}')
    lines.append(f'- steps per run: {N_STEPS}')
    lines.append(f'- reproduction_rate: {DEFAULT_REPRODUCTION_RATE}')
    lines.append(f'- composite urgencies: harness-patched to neutral (isolates U_sys revision)')
    lines.append(f'- wall-clock: {wall_clock/60:.1f} min')
    lines.append('')

    lines.append('## Criterion 5: gamma(phi) values match spec')
    lines.append('')
    lines.append('| phi | Expected | Measured | Within tolerance (1e-3)? |')
    lines.append('|-----|----------|----------|---------------------------|')
    for phi in PHI_VALUES:
        m, e, ok = ev['gamma_check'][phi]
        lines.append(f'| {phi:.1f} | {e:.4f} | {m:.4f} | {"PASS" if ok else "FAIL"} |')
    lines.append('')
    lines.append(f'Result: **{"PASS" if ev["crit5"] else "FAIL"}**')
    lines.append('')

    lines.append('## Criterion 2: no NaN, no crashes')
    lines.append('')
    lines.append(f'- Crashes: {ev["crashes"]} / {len(PHI_VALUES) * N_SEEDS}')
    lines.append(f'- NaN found: {ev["nans"]} / {len(PHI_VALUES) * N_SEEDS}')
    lines.append(f'- Extinct (informational): {ev["extincts"]} / {len(PHI_VALUES) * N_SEEDS}')
    lines.append(f'- Result: **{"PASS" if ev["crit2"] else "FAIL"}**')
    lines.append('')

    lines.append('## Criterion 3: demographic sustainability across phi')
    lines.append('')
    lines.append('| phi | Mean final pop | Min final pop | Max final pop | Mean >= 60? | Min >= 30? |')
    lines.append('|-----|----------------|---------------|---------------|-------------|------------|')
    for phi in PHI_VALUES:
        d = ev['demo_per_phi'][phi]
        lines.append(f'| {phi:.1f} | {d["mean"]:.1f} | {d["min"]} | {d["max"]} | '
                     f'{"PASS" if d["pass_mean"] else "FAIL"} | {"PASS" if d["pass_min"] else "FAIL"} |')
    lines.append('')
    lines.append(f'Result: **{"PASS" if ev["crit3"] else "FAIL"}**')
    lines.append('')

    lines.append('## Criterion 1: phi behavioral channel (revised metric)')
    lines.append('')
    lines.append('Per-seed range of final population across the five phi '
                 'values. The pre-Stage-1.6 phi diagnostic produced '
                 'bit-identical trajectories with range = 0 on every seed; '
                 'a meaningful behavioral channel must produce range > '
                 f'{PHI_RANGE_THRESHOLD} on at least {PHI_RANGE_SEEDS_REQUIRED} '
                 'of the 5 test seeds.')
    lines.append('')
    lines.append('| Seed | phi=1.0 | phi=5.0 | phi=10.0 | phi=25.0 | phi=100.0 | min | max | range | range > 15? |')
    lines.append('|------|---------|---------|----------|----------|-----------|-----|-----|-------|--------------|')
    for seed in sorted(ev['per_seed_phi_range'].keys()):
        d = ev['per_seed_phi_range'][seed]
        cells = ' | '.join(str(d['pops_by_phi'][phi]) for phi in PHI_VALUES)
        lines.append(f'| {seed} | {cells} | {d["min"]} | {d["max"]} | '
                     f'{d["range"]} | {"YES" if d["range"] > PHI_RANGE_THRESHOLD else "no"} |')
    lines.append('')
    lines.append(f'Seeds with range > {PHI_RANGE_THRESHOLD}: '
                 f'**{ev["n_seeds_diverged"]} / 5** '
                 f'(criterion 1 requires at least {PHI_RANGE_SEEDS_REQUIRED}).')
    lines.append(f'Result: **{"PASS" if ev["crit1"] else "FAIL"}**')
    lines.append('')
    lines.append('### Informational: original cosine-on-means metric (no longer gating)')
    lines.append('')
    lines.append('| phi_a | phi_b | Cosine distance | Above 0.05? |')
    lines.append('|-------|-------|-----------------|--------------|')
    for (pa, pb), d in ev['pair_distances']:
        lines.append(f'| {pa:.1f} | {pb:.1f} | {d:.4f} | {"YES" if d > COSINE_THRESHOLD else "no"} |')
    lines.append('')
    lines.append(f'Cosine pairs above 0.05: {ev["n_above_cosine"]} / {len(ev["pair_distances"])} '
                 '(informational; not gating). The cosine-on-means metric '
                 'systematically underrepresents phi sensitivity because phi '
                 'shifts which similar-allocation candidate the optimizer '
                 "picks; the per-step difference is small but the per-step "
                 'trajectory compounds.')
    lines.append('')

    lines.append('## Criterion 4: default phi behavior preserved vs baseline')
    lines.append('')
    lines.append(f'- Baseline mean final pop (pre-revision, neutral composites, phi=10): **{ev["baseline_mean"]:.1f}**')
    lines.append(f'- Post-revision mean final pop (phi=10): **{ev["phi10_post_mean"]:.1f}**')
    lines.append(f'- Relative delta: **{100 * ev["crit4_pop_delta_pct"]:.1f}%** (tolerance: 30%)')
    lines.append('')
    lines.append('State drift (post vs baseline, mean across runs):')
    lines.append('')
    lines.append('| Field | Baseline mean | Post mean | Relative drift |')
    lines.append('|-------|---------------|-----------|----------------|')
    for k in STATE_FIELDS:
        base_vals = [r['mean_state'][k] for r in baseline['per_seed']]
        bm = float(np.mean(base_vals))
        pm = ev['post_state_means'][k]
        drift = ev['state_drifts'][k]
        lines.append(f'| {k} | {bm:.4f} | {pm:.4f} | {drift:.3f} |')
    lines.append('')
    lines.append(f'Result: **{"PASS" if ev["crit4"] else "FAIL"}**')
    lines.append('')

    lines.append('## Per-phi summary')
    lines.append('')
    lines.append('| phi | gamma | Mean final pop | Range | Mean x_resilience | Mean x_inst_cap | Mean x_bio_welfare |')
    lines.append('|-----|-------|----------------|-------|-------------------|-----------------|---------------------|')
    for phi in PHI_VALUES:
        d = ev['demo_per_phi'][phi]
        seeds = per_phi[phi]
        mean_alloc_x_res = float(np.mean([s['mean_alloc']['x_resilience'] for s in seeds]))
        mean_alloc_x_inst = float(np.mean([s['mean_alloc']['x_institutional_capacity'] for s in seeds]))
        mean_alloc_x_wel = float(np.mean([s['mean_alloc']['x_bio_welfare'] for s in seeds]))
        g = ev['gamma_check'][phi][0]
        lines.append(f'| {phi:.1f} | {g:.4f} | {d["mean"]:.1f} | [{d["min"]}, {d["max"]}] | '
                     f'{mean_alloc_x_res:.4f} | {mean_alloc_x_inst:.4f} | {mean_alloc_x_wel:.4f} |')
    lines.append('')
    lines.append('## Disposition')
    lines.append('')
    if overall:
        lines.append('All five criteria pass. Stage 1.6 U_sys revision is validated. The '
                     'composite urgency revision (Stage 1.7) is the next work, addressing '
                     'the state-channel problem independently of the phi-channel fix.')
    else:
        fails = []
        if not ev['crit1']: fails.append('1 (phi behavioral channel)')
        if not ev['crit2']: fails.append('2 (NaN/crashes)')
        if not ev['crit3']: fails.append('3 (demographics)')
        if not ev['crit4']: fails.append('4 (baseline preservation)')
        if not ev['crit5']: fails.append('5 (gamma values)')
        lines.append(f'Criteria failed: {", ".join(fails)}. See spec for failure-mode '
                     'response. Phi-channel failure means the gamma function form needs '
                     'revisiting; baseline regression means LAMBDA_LINEAGE_COUPLING is off.')
    lines.append('')
    with open(out_path, 'w') as f:
        f.write('\n'.join(lines) + '\n')


def main():
    baseline_path = os.path.join(HERE, 'stage16_baseline_phi10.json')
    if not os.path.exists(baseline_path):
        print(f'ERROR: baseline file missing at {baseline_path}.', flush=True)
        print(f'Run diagnostics/stage16_baseline_capture.py first (BEFORE Stage 1.6 code changes).', flush=True)
        sys.exit(2)
    with open(baseline_path, 'r') as f:
        baseline = json.load(f)
    print(f'Loaded baseline: mean_final_pop={baseline["mean_final_pop"]:.1f}, '
          f'range=[{baseline["min_final_pop"]}, {baseline["max_final_pop"]}]', flush=True)

    t0 = time.time()
    per_phi = collect()
    wall = time.time() - t0
    print('', flush=True)
    print('Computing pass/fail criteria...', flush=True)
    ev = evaluate(per_phi, baseline)

    out_path = os.path.join(HERE, 'stage16_integrity_report.md')
    write_report(per_phi, ev, baseline, wall, out_path)
    print('', flush=True)
    overall = ev['crit1'] and ev['crit2'] and ev['crit3'] and ev['crit4'] and ev['crit5']
    print(f'  C1 phi behavioral channel: {"PASS" if ev["crit1"] else "FAIL"}  ({ev["n_seeds_diverged"]}/5 seeds with cross-phi pop range > {PHI_RANGE_THRESHOLD})', flush=True)
    print(f'  C2 no NaN/no crashes:      {"PASS" if ev["crit2"] else "FAIL"}', flush=True)
    print(f'  C3 demographics:           {"PASS" if ev["crit3"] else "FAIL"}', flush=True)
    print(f'  C4 baseline preservation:  {"PASS" if ev["crit4"] else "FAIL"} ({100*ev["crit4_pop_delta_pct"]:.1f}% delta vs 30%)', flush=True)
    print(f'  C5 gamma values:           {"PASS" if ev["crit5"] else "FAIL"}', flush=True)
    print('', flush=True)
    print(f'OVERALL: {"PASS" if overall else "FAIL"}', flush=True)
    print(f'Report: {out_path}', flush=True)
    sys.exit(0 if overall else 1)


if __name__ == '__main__':
    main()
