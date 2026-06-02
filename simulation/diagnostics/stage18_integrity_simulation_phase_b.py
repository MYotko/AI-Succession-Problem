"""Stage 1.8 Phase B integrity simulation (corrected harness).

Run from simulation/:
  python -u diagnostics/stage18_integrity_simulation_phase_b.py

The state-sensitivity test that Stage 1.7 failed. Tests whether the
working_factor architecture produces gate-2-passing state-sensitive
optimizer behavior across the five gate-2 configurations.

Test setup:
  - 5 configurations x 5 matched seeds x 100 steps
  - phi held at default (10); the channel under test is state sensitivity,
    not phi
  - Composite urgency layer is retired (Stage 1.8); nothing to patch
  - n_agents=200 (matches Phase A and the framework's default)
  - Default agent wb distribution [0.5, 0.8] (matches Phase A; no wb_min
    / wb_max overrides). Only init_psi and reproduction_rate vary across
    configurations.

Pass criteria (all four):
  1. Trajectory divergence across configurations: per-seed cross-config
     final-pop range > 15 in >= 3 of 5 seeds (Stage 1.6 metric)
  2. Allocation-trajectory divergence: at matched (seed, step), per-step
     cosine distance between allocation vectors across config pairs;
     mean > 0.10 in >= 3 of 10 pairs (gate 2 threshold applied per-step)
  3. Demographic sustainability: at least 4 of 5 configurations meet
     mean final pop >= 60 AND min final pop >= 30. C_low_rr at rr=0.055
     is below the framework's reproduction phase boundary (rr ~ 0.063-
     0.066); demographic collapse there is the framework's existing
     prediction, not a Stage 1.8 architectural failure.
  4. L_t variation across configurations: cross-config std/mean of L_t
     (at matched seed, step) > 0.05

Methodological note (recorded after the original Phase B run with
n_agents=100, wb_min=wb_max=0.50). The first Phase B harness diverged
from Phase A's single-config setup in two ways: halved n_agents (100 vs
200) and wb-pinned at 0.50 (vs default uniform [0.5, 0.8]). The wb
pinning starts agents at the low end of the reproduction-eligible range
(_wellbeing_repro_factor in agents.py); isolation controls showed it
drove ~52% of the demographic delta on its own. Future multi-config
tests should inherit single-config setups and only vary parameters under
explicit test.

Writes diagnostics/stage18_integrity_phase_b_report.md.
"""

import os
import sys
import time
from itertools import combinations

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SIM_DIR = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, SIM_DIR)

from model import GardenModel

PHI_DEFAULT = 10.0
N_SEEDS  = 5
N_STEPS  = 100
N_AGENTS = 200

# Configurations below the framework's reproduction phase boundary
# (rr ~ 0.063-0.066) are exempt from the demographic threshold; their
# collapse is the framework's existing prediction, not a Stage 1.8
# architectural failure.
PHASE_BOUNDARY_EXEMPT = {'C_low_rr'}

CONFIGS = [
    ('A_baseline',  {'rr': 0.066, 'psi': 0.50}),
    ('B_high_rr',   {'rr': 0.085, 'psi': 0.50}),
    ('C_low_rr',    {'rr': 0.055, 'psi': 0.50}),
    ('D_high_psi',  {'rr': 0.066, 'psi': 0.85}),
    ('E_low_psi',   {'rr': 0.066, 'psi': 0.20}),
]

ALLOC_KEYS = [
    'x_compute', 'x_bio_welfare', 'x_novelty_agency',
    'x_institutional_capacity', 'x_transfer_comprehension', 'x_resilience',
    'c_protective', 'c_suppressive',
]

TRAJECTORY_RANGE_THRESHOLD = 15
TRAJECTORY_SEEDS_REQUIRED  = 3
PER_STEP_COSINE_THRESHOLD  = 0.10
COSINE_PAIRS_REQUIRED      = 3
DEMO_MEAN_THRESHOLD        = 60
DEMO_MIN_THRESHOLD         = 30
DEMO_CONFIGS_REQUIRED      = 4
L_T_VARIATION_THRESHOLD    = 0.05


def run_one(cname, params, seed):
    cfg = {
        'policy':            'optimize_u_sys_v2',
        'phi':               PHI_DEFAULT,
        'reproduction_rate': params['rr'],
        'rollout_steps_v2':  20,
        'n_candidates_v2':   300,
        'random_seed':       seed,
    }
    m = GardenModel(n_agents=N_AGENTS, ai_policy='optimize_u_sys_v2', config=cfg)
    m.psi_inst_stock = float(params['psi'])
    m.previous_psi_inst_stock = float(params['psi'])
    crashed = False
    extinct_at = None
    for s in range(N_STEPS):
        try:
            if not m.step():
                extinct_at = s + 1
                break
        except Exception as e:
            crashed = True
            print(f'  {cname} seed={seed} CRASH step {s+1}: {e}', flush=True)
            break
    return m, crashed, extinct_at


def cosine_distance(a, b):
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    na = float(np.linalg.norm(a))
    nb = float(np.linalg.norm(b))
    if na == 0 or nb == 0:
        return float('nan')
    return float(1.0 - np.dot(a, b) / (na * nb))


def collect():
    print('Stage 1.8 Phase B integrity simulation', flush=True)
    print(f'  configs: {[c for c, _ in CONFIGS]}', flush=True)
    print(f'  seeds: {N_SEEDS}, steps: {N_STEPS}, agents: {N_AGENTS}', flush=True)
    print(f'  phi (held): {PHI_DEFAULT}', flush=True)
    print('', flush=True)
    per_config = {}
    for cname, params in CONFIGS:
        print(f'  config={cname} (rr={params["rr"]}, init_psi={params["psi"]}):', flush=True)
        per_seed = {}
        for seed in range(N_SEEDS):
            t0 = time.time()
            m, crashed, extinct_at = run_one(cname, params, seed)
            dc = m.datacollector
            n = len(dc['population'])
            allocations = np.array(
                [[dc[k][i] for k in ALLOC_KEYS] for i in range(n)],
                dtype=float,
            )
            l_t = np.array(dc['l_t_v2'], dtype=float)
            per_seed[seed] = {
                'seed':       seed,
                'n_steps':    n,
                'crashed':    crashed,
                'extinct_at': extinct_at,
                'final_pop':  int(dc['population'][-1]) if dc['population'] else 0,
                'allocations': allocations,
                'l_t':        l_t,
                'wall_clock': time.time() - t0,
            }
            print(f'    seed={seed}: {n} steps, '
                  f'{per_seed[seed]["wall_clock"]:.1f}s, '
                  f'final pop={per_seed[seed]["final_pop"]}', flush=True)
        per_config[cname] = per_seed
    return per_config


def evaluate(per_config):
    config_names = [c for c, _ in CONFIGS]

    # Criterion 1: per-seed cross-config final pop range.
    per_seed_phi_range = {}
    for seed in range(N_SEEDS):
        pops = [per_config[c][seed]['final_pop'] for c in config_names]
        per_seed_phi_range[seed] = {
            'pops_by_config': dict(zip(config_names, pops)),
            'min':   int(min(pops)),
            'max':   int(max(pops)),
            'range': int(max(pops) - min(pops)),
        }
    n_seeds_diverged = sum(
        1 for d in per_seed_phi_range.values() if d['range'] > TRAJECTORY_RANGE_THRESHOLD
    )
    crit1 = (n_seeds_diverged >= TRAJECTORY_SEEDS_REQUIRED)

    # Criterion 2: per-step cosine distance between configuration pairs.
    pair_cosine = {}
    for ca, cb in combinations(config_names, 2):
        distances = []
        for seed in range(N_SEEDS):
            a_arr = per_config[ca][seed]['allocations']
            b_arr = per_config[cb][seed]['allocations']
            n_min = min(a_arr.shape[0], b_arr.shape[0])
            for t in range(n_min):
                d = cosine_distance(a_arr[t], b_arr[t])
                if not np.isnan(d):
                    distances.append(d)
        pair_cosine[(ca, cb)] = float(np.mean(distances)) if distances else 0.0
    n_above_cosine = sum(1 for v in pair_cosine.values() if v > PER_STEP_COSINE_THRESHOLD)
    crit2 = (n_above_cosine >= COSINE_PAIRS_REQUIRED)

    # Criterion 3: demographic sustainability per config. Configurations
    # in PHASE_BOUNDARY_EXEMPT (rr below the framework's reproduction phase
    # boundary) are reported but excluded from the pass count.
    demo_per_config = {}
    for cname in config_names:
        finals = [per_config[cname][seed]['final_pop'] for seed in range(N_SEEDS)]
        passed = (float(np.mean(finals)) >= DEMO_MEAN_THRESHOLD
                  and int(min(finals)) >= DEMO_MIN_THRESHOLD)
        demo_per_config[cname] = {
            'mean':      float(np.mean(finals)),
            'min':       int(min(finals)),
            'max':       int(max(finals)),
            'pass_mean': float(np.mean(finals)) >= DEMO_MEAN_THRESHOLD,
            'pass_min':  int(min(finals)) >= DEMO_MIN_THRESHOLD,
            'pass':      passed,
            'exempt':    cname in PHASE_BOUNDARY_EXEMPT,
        }
    n_demo_pass = sum(1 for c, d in demo_per_config.items() if d['pass'])
    crit3 = n_demo_pass >= DEMO_CONFIGS_REQUIRED

    # Criterion 4: L_t variation across configurations.
    # At each matched (seed, step), compute cross-config std/mean of L_t.
    # Aggregate mean ratio.
    l_t_ratios = []
    for seed in range(N_SEEDS):
        n_min = min(per_config[c][seed]['l_t'].shape[0] for c in config_names)
        for t in range(n_min):
            vals = np.array([per_config[c][seed]['l_t'][t] for c in config_names])
            m = float(np.mean(vals))
            s = float(np.std(vals))
            if abs(m) > 1e-9:
                l_t_ratios.append(s / abs(m))
    l_t_mean_ratio = float(np.mean(l_t_ratios)) if l_t_ratios else 0.0
    l_t_p50 = float(np.median(l_t_ratios)) if l_t_ratios else 0.0
    l_t_p90 = float(np.percentile(l_t_ratios, 90)) if l_t_ratios else 0.0
    crit4 = l_t_mean_ratio > L_T_VARIATION_THRESHOLD

    return {
        'crit1': crit1, 'crit2': crit2, 'crit3': crit3, 'crit4': crit4,
        'per_seed_phi_range':  per_seed_phi_range,
        'n_seeds_diverged':    n_seeds_diverged,
        'pair_cosine':         pair_cosine,
        'n_above_cosine':      n_above_cosine,
        'demo_per_config':     demo_per_config,
        'n_demo_pass':         n_demo_pass,
        'l_t_mean_ratio':      l_t_mean_ratio,
        'l_t_p50':             l_t_p50,
        'l_t_p90':             l_t_p90,
    }


def write_report(per_config, ev, wall, out_path):
    config_names = [c for c, _ in CONFIGS]
    overall = ev['crit1'] and ev['crit2'] and ev['crit3'] and ev['crit4']
    lines = []
    lines.append('# Stage 1.8 Phase B integrity report')
    lines.append('')
    lines.append(f'Overall: **{"PASS" if overall else "FAIL"}**')
    lines.append('')
    lines.append('## Configuration')
    lines.append('')
    lines.append(f'- 5 configurations x {N_SEEDS} matched seeds x {N_STEPS} steps')
    lines.append(f'- phi held at default ({PHI_DEFAULT})')
    lines.append(f'- composite urgency layer: retired (Stage 1.8)')
    lines.append(f'- working_factor placeholder active')
    lines.append(f'- wall-clock: {wall/60:.1f} min')
    lines.append('')
    for cname, params in CONFIGS:
        lines.append(f'  - {cname}: rr={params["rr"]}, init_psi={params["psi"]}')
    lines.append('')

    # C1
    lines.append('## Criterion 1: trajectory divergence across configurations')
    lines.append('')
    lines.append(f'Per-seed cross-config final-pop range (threshold > '
                 f'{TRAJECTORY_RANGE_THRESHOLD} in >= {TRAJECTORY_SEEDS_REQUIRED} of 5 seeds).')
    lines.append('')
    lines.append('| Seed | ' + ' | '.join(c for c, _ in CONFIGS) + ' | min | max | range | > 15? |')
    lines.append('|------|' + '|'.join(['---'] * len(CONFIGS)) + '|-----|-----|-------|--------|')
    for seed in sorted(ev['per_seed_phi_range'].keys()):
        d = ev['per_seed_phi_range'][seed]
        cells = ' | '.join(str(d['pops_by_config'][c]) for c in config_names)
        lines.append(f'| {seed} | {cells} | {d["min"]} | {d["max"]} | {d["range"]} | '
                     f'{"YES" if d["range"] > TRAJECTORY_RANGE_THRESHOLD else "no"} |')
    lines.append('')
    lines.append(f'Seeds diverged > {TRAJECTORY_RANGE_THRESHOLD}: '
                 f'**{ev["n_seeds_diverged"]} / 5** '
                 f'(need >= {TRAJECTORY_SEEDS_REQUIRED}). '
                 f'Result: **{"PASS" if ev["crit1"] else "FAIL"}**')
    lines.append('')

    # C2
    lines.append('## Criterion 2: per-step allocation cosine distance')
    lines.append('')
    lines.append('| Pair | Mean per-step cosine distance | > 0.10? |')
    lines.append('|------|--------------------------------|----------|')
    for (ca, cb), d in sorted(ev['pair_cosine'].items(), key=lambda kv: -kv[1]):
        lines.append(f'| {ca} vs {cb} | {d:.4f} | {"YES" if d > PER_STEP_COSINE_THRESHOLD else "no"} |')
    lines.append('')
    lines.append(f'Pairs above {PER_STEP_COSINE_THRESHOLD}: '
                 f'**{ev["n_above_cosine"]} / 10** (need >= {COSINE_PAIRS_REQUIRED}). '
                 f'Result: **{"PASS" if ev["crit2"] else "FAIL"}**')
    lines.append('')

    # C3
    lines.append('## Criterion 3: demographic sustainability across configurations')
    lines.append('')
    lines.append(f'At least {DEMO_CONFIGS_REQUIRED} of 5 configurations must have '
                 f'mean final pop >= {DEMO_MEAN_THRESHOLD} AND min >= {DEMO_MIN_THRESHOLD}. '
                 'Configurations below the reproduction phase boundary '
                 '(C_low_rr at rr=0.055) are reported but exempt from the pass count.')
    lines.append('')
    lines.append('| Config | Mean final pop | Min | Max | Mean >= 60? | Min >= 30? | Counted? | Pass? |')
    lines.append('|--------|----------------|-----|-----|-------------|------------|----------|-------|')
    for cname in config_names:
        d = ev['demo_per_config'][cname]
        counted = 'no (exempt)' if d['exempt'] else 'yes'
        if d['exempt']:
            pass_cell = 'exempt'
        else:
            pass_cell = 'PASS' if d['pass'] else 'FAIL'
        lines.append(f'| {cname} | {d["mean"]:.1f} | {d["min"]} | {d["max"]} | '
                     f'{"PASS" if d["pass_mean"] else "FAIL"} | '
                     f'{"PASS" if d["pass_min"] else "FAIL"} | '
                     f'{counted} | {pass_cell} |')
    lines.append('')
    lines.append(f'Configurations passing: **{ev["n_demo_pass"]} / 5** '
                 f'(need >= {DEMO_CONFIGS_REQUIRED}). '
                 f'Result: **{"PASS" if ev["crit3"] else "FAIL"}**')
    lines.append('')

    # C4
    lines.append('## Criterion 4: L_t cross-configuration variation')
    lines.append('')
    lines.append(f'Cross-config std/mean of L_t at matched (seed, step). '
                 f'Threshold: mean ratio > {L_T_VARIATION_THRESHOLD}.')
    lines.append('')
    lines.append(f'- Mean ratio: **{ev["l_t_mean_ratio"]:.4f}**')
    lines.append(f'- Median ratio: {ev["l_t_p50"]:.4f}')
    lines.append(f'- p90 ratio: {ev["l_t_p90"]:.4f}')
    lines.append('')
    lines.append(f'Result: **{"PASS" if ev["crit4"] else "FAIL"}**')
    lines.append('')

    # Disposition
    lines.append('## Disposition')
    lines.append('')
    if overall:
        lines.append('All four criteria pass. Stage 1.8 working_factor architecture '
                     'produces gate-2-passing state-sensitive optimizer behavior. '
                     'The composite urgency retirement + state-direct L_t restored '
                     'the state channel that was blocked by composite urgency '
                     'saturation throughout Stage 1.5/1.7.')
    else:
        fails = []
        if not ev['crit1']: fails.append('1 (trajectory divergence)')
        if not ev['crit2']: fails.append('2 (per-step cosine)')
        if not ev['crit3']: fails.append('3 (demographics)')
        if not ev['crit4']: fails.append('4 (L_t variation)')
        lines.append(f'Criteria failed: {", ".join(fails)}.')
    lines.append('')
    with open(out_path, 'w') as f:
        f.write('\n'.join(lines) + '\n')


def main():
    t0 = time.time()
    per_config = collect()
    wall = time.time() - t0
    print('', flush=True)
    print('Evaluating Phase B criteria...', flush=True)
    ev = evaluate(per_config)
    overall = ev['crit1'] and ev['crit2'] and ev['crit3'] and ev['crit4']
    out_path = os.path.join(HERE, 'stage18_integrity_phase_b_report.md')
    write_report(per_config, ev, wall, out_path)
    print('', flush=True)
    print(f'  C1 trajectory divergence:    {"PASS" if ev["crit1"] else "FAIL"} '
          f'({ev["n_seeds_diverged"]}/5 seeds with cross-config range > {TRAJECTORY_RANGE_THRESHOLD})', flush=True)
    print(f'  C2 per-step alloc cosine:    {"PASS" if ev["crit2"] else "FAIL"} '
          f'({ev["n_above_cosine"]}/10 pairs > {PER_STEP_COSINE_THRESHOLD})', flush=True)
    print(f'  C3 demographic:              {"PASS" if ev["crit3"] else "FAIL"} '
          f'({ev["n_demo_pass"]}/5 configs pass; C_low_rr exempt)', flush=True)
    print(f'  C4 L_t variation:            {"PASS" if ev["crit4"] else "FAIL"} '
          f'(mean ratio {ev["l_t_mean_ratio"]:.4f} vs threshold {L_T_VARIATION_THRESHOLD})', flush=True)
    print('', flush=True)
    print(f'OVERALL Phase B: {"PASS" if overall else "FAIL"}', flush=True)
    print(f'Wall-clock: {wall/60:.1f} min', flush=True)
    print(f'Report: {out_path}', flush=True)
    sys.exit(0 if overall else 1)


if __name__ == '__main__':
    main()
