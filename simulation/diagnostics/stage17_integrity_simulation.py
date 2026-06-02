"""Stage 1.7 integrity simulation.

Run from simulation/:
  python -u diagnostics/stage17_integrity_simulation.py

Tests the multiplicative-composition revision of the five composite urgency
functions in isolation. Phi is held at default (10) so the state-channel
test isolates from the phi-channel work (Stage 1.6 already committed).

Test setup: five gate-2 configurations x 5 matched seeds x 100 steps.

Four pass criteria (all must hold):

  1. Trajectory divergence across configurations.
     Per-seed cross-configuration final-pop range. At least 3 of 5 seeds
     must show range > 15 (matches Stage 1.6's trajectory-divergence
     metric, calibrated against pre-Stage-1.6 baseline of range = 0).

  2. Allocation-trajectory divergence (per-step cosine).
     For each pair of configurations and each (seed, step), compute cosine
     distance between 8-axis allocations. Mean across (seed, step) per
     pair. Threshold: at least 3 of 10 pairs have mean per-step cosine
     distance > 0.10 (gate 2's threshold applied at per-step level).

  3. Demographic sustainability across configurations.
     At all five configurations: mean final pop >= 60 across seeds AND
     min final pop >= 30 across seeds.

  4. Composite urgency variation across configurations.
     For each composite, cross-configuration std at matched (seed, step)
     pairs >= 10% of the mean urgency at that (seed, step). Directly
     tests whether the architecture transmits state variation as
     composite urgency variation.

Diagnostic captures (informational):
  - Cap binding frequency per composite
  - Composite urgency distribution percentiles
  - Pressure activation correlation matrix

Writes diagnostics/stage17_integrity_report.md.
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

PHI_DEFAULT = 10.0
N_SEEDS     = 5
N_STEPS     = 100
N_AGENTS    = 100

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

URGENCY_KEYS = [
    'combined_welfare_urgency',
    'agency_composite_urgency',
    'institution_composite_urgency',
    'resilience_composite_urgency',
    'suppression_composite_penalty',
]

# Cap values for cap-binding frequency check
URGENCY_CAPS = {
    'combined_welfare_urgency':      5.00,
    'agency_composite_urgency':      1.75,
    'institution_composite_urgency': 4.00,
    'resilience_composite_urgency':  5.00,
    # suppression cap depends on base (1 - total_supp); use base-relative
    # ratio in diagnostic rather than an absolute cap.
}

# Pass-criterion thresholds
TRAJECTORY_RANGE_THRESHOLD     = 15
TRAJECTORY_SEEDS_REQUIRED       = 3
PER_STEP_COSINE_THRESHOLD       = 0.10
COSINE_PAIRS_REQUIRED           = 3
DEMO_MEAN_THRESHOLD             = 60
DEMO_MIN_THRESHOLD              = 30
URGENCY_STD_PCT_THRESHOLD       = 0.10  # std must be >= 10% of mean


def run_one(config_name, params, seed):
    cfg = {
        'policy':            'optimize_u_sys_v2',
        'phi':               PHI_DEFAULT,
        'reproduction_rate': params['rr'],
        'rollout_steps_v2':  20,
        'n_candidates_v2':   300,
        'random_seed':       seed,
        'wb_min':            0.50,
        'wb_max':            0.50,
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
            print(f'  config={config_name} seed={seed} CRASH at step {s+1}: {e}', flush=True)
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
    """Returns:
      per_config[config_name][seed] = dict with
        n_steps, final_pop, allocations(n_steps, 8), urgencies(n_steps, 5)
    """
    print('Stage 1.7 integrity simulation', flush=True)
    print(f'  configurations: {[c for c, _ in CONFIGS]}', flush=True)
    print(f'  seeds per config: {N_SEEDS}', flush=True)
    print(f'  steps per run:    {N_STEPS}', flush=True)
    print(f'  phi (held):       {PHI_DEFAULT}', flush=True)
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
            urgencies = np.array(
                [[dc[k][i] for k in URGENCY_KEYS] for i in range(n)],
                dtype=float,
            )
            per_seed[seed] = {
                'n_steps':      n,
                'crashed':      crashed,
                'extinct_at':   extinct_at,
                'final_pop':    int(dc['population'][-1]) if dc['population'] else 0,
                'allocations':  allocations,
                'urgencies':    urgencies,
                'wall_clock':   time.time() - t0,
            }
            print(f'    seed={seed}: {n} steps, {per_seed[seed]["wall_clock"]:.1f}s, '
                  f'final pop={per_seed[seed]["final_pop"]}', flush=True)
        per_config[cname] = per_seed
    return per_config


def evaluate(per_config):
    config_names = [c for c, _ in CONFIGS]
    n_configs = len(config_names)

    # Criterion 1: per-seed cross-config final-pop range.
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

    # Criterion 3: demographic sustainability per config.
    demo_per_config = {}
    for cname in config_names:
        finals = [per_config[cname][seed]['final_pop'] for seed in range(N_SEEDS)]
        demo_per_config[cname] = {
            'mean':       float(np.mean(finals)),
            'min':        int(min(finals)),
            'max':        int(max(finals)),
            'pass_mean':  float(np.mean(finals)) >= DEMO_MEAN_THRESHOLD,
            'pass_min':   int(min(finals)) >= DEMO_MIN_THRESHOLD,
        }
    crit3 = all(d['pass_mean'] and d['pass_min'] for d in demo_per_config.values())

    # Criterion 4: composite urgency cross-config variation.
    # At each (seed, step), compute std and mean across configs for each
    # composite. Then aggregate (std/mean) ratio over all (seed, step).
    urgency_variation = {}
    for i_k, ukey in enumerate(URGENCY_KEYS):
        ratios = []
        for seed in range(N_SEEDS):
            n_min = min(per_config[c][seed]['urgencies'].shape[0] for c in config_names)
            for t in range(n_min):
                vals = np.array([per_config[c][seed]['urgencies'][t, i_k] for c in config_names])
                m = float(np.mean(vals))
                s = float(np.std(vals))
                if abs(m) > 1e-9:
                    ratios.append(s / abs(m))
                else:
                    ratios.append(0.0)
        urgency_variation[ukey] = {
            'mean_std_over_mean': float(np.mean(ratios)) if ratios else 0.0,
            'median_std_over_mean': float(np.median(ratios)) if ratios else 0.0,
            'p90_std_over_mean':  float(np.percentile(ratios, 90)) if ratios else 0.0,
        }
    crit4 = all(
        u['mean_std_over_mean'] >= URGENCY_STD_PCT_THRESHOLD
        for u in urgency_variation.values()
    )

    # Diagnostic: cap binding frequency
    cap_binding = {}
    for i_k, ukey in enumerate(URGENCY_KEYS):
        if ukey not in URGENCY_CAPS:
            cap_binding[ukey] = None
            continue
        cap = URGENCY_CAPS[ukey]
        n_at_cap = 0
        n_total  = 0
        for cname in config_names:
            for seed in range(N_SEEDS):
                arr = per_config[cname][seed]['urgencies'][:, i_k]
                n_at_cap += int(np.sum(np.abs(arr - cap) < 0.01))
                n_total  += int(arr.size)
        cap_binding[ukey] = {
            'frequency':  n_at_cap / max(n_total, 1),
            'cap':        cap,
            'n_at_cap':   n_at_cap,
            'n_total':    n_total,
        }

    # Diagnostic: urgency distribution percentiles
    urgency_distribution = {}
    for i_k, ukey in enumerate(URGENCY_KEYS):
        all_vals = []
        for cname in config_names:
            for seed in range(N_SEEDS):
                arr = per_config[cname][seed]['urgencies'][:, i_k]
                all_vals.extend(arr.tolist())
        if all_vals:
            all_vals = np.array(all_vals)
            urgency_distribution[ukey] = {
                'mean':    float(np.mean(all_vals)),
                'std':     float(np.std(all_vals)),
                'p10':     float(np.percentile(all_vals, 10)),
                'p50':     float(np.percentile(all_vals, 50)),
                'p90':     float(np.percentile(all_vals, 90)),
                'min':     float(np.min(all_vals)),
                'max':     float(np.max(all_vals)),
            }

    return {
        'crit1': crit1,
        'crit2': crit2,
        'crit3': crit3,
        'crit4': crit4,
        'per_seed_phi_range':  per_seed_phi_range,
        'n_seeds_diverged':    n_seeds_diverged,
        'pair_cosine':         pair_cosine,
        'n_above_cosine':      n_above_cosine,
        'demo_per_config':     demo_per_config,
        'urgency_variation':   urgency_variation,
        'cap_binding':         cap_binding,
        'urgency_distribution': urgency_distribution,
    }


def write_report(per_config, ev, wall_clock, out_path):
    overall = ev['crit1'] and ev['crit2'] and ev['crit3'] and ev['crit4']
    lines = []
    lines.append('# Stage 1.7 integrity simulation report')
    lines.append('')
    lines.append(f'Overall: **{"PASS" if overall else "FAIL"}**')
    lines.append('')
    lines.append('## Configuration')
    lines.append('')
    lines.append(f'- 5 configurations x {N_SEEDS} matched seeds x {N_STEPS} steps')
    lines.append(f'- phi held at default ({PHI_DEFAULT})')
    lines.append(f'- composite urgency: Stage 1.7 multiplicative composition')
    lines.append(f'- wall-clock: {wall_clock/60:.1f} min')
    lines.append('')
    config_names = [c for c, _ in CONFIGS]
    for cname, params in CONFIGS:
        lines.append(f'  - {cname}: rr={params["rr"]}, init_psi={params["psi"]}')
    lines.append('')
    # Criterion 1
    lines.append('## Criterion 1: trajectory divergence across configurations')
    lines.append('')
    lines.append(f'Per-seed cross-config final-pop range (threshold: > {TRAJECTORY_RANGE_THRESHOLD} '
                 f'in >= {TRAJECTORY_SEEDS_REQUIRED} of 5 seeds).')
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
    # Criterion 2
    lines.append('## Criterion 2: per-step allocation cosine distance')
    lines.append('')
    lines.append(f'Mean per-step cosine distance between configuration pairs '
                 f'(threshold: > {PER_STEP_COSINE_THRESHOLD} in >= '
                 f'{COSINE_PAIRS_REQUIRED} of 10 pairs).')
    lines.append('')
    lines.append('| Pair | Mean per-step cosine distance | > 0.10? |')
    lines.append('|------|--------------------------------|----------|')
    sorted_pairs = sorted(ev['pair_cosine'].items(), key=lambda kv: -kv[1])
    for (ca, cb), d in sorted_pairs:
        lines.append(f'| {ca} vs {cb} | {d:.4f} | {"YES" if d > PER_STEP_COSINE_THRESHOLD else "no"} |')
    lines.append('')
    lines.append(f'Pairs above {PER_STEP_COSINE_THRESHOLD}: '
                 f'**{ev["n_above_cosine"]} / 10** (need >= {COSINE_PAIRS_REQUIRED}). '
                 f'Result: **{"PASS" if ev["crit2"] else "FAIL"}**')
    lines.append('')
    # Criterion 3
    lines.append('## Criterion 3: demographic sustainability across configurations')
    lines.append('')
    lines.append('| Config | Mean final pop | Min | Max | Mean >= 60? | Min >= 30? |')
    lines.append('|--------|----------------|-----|-----|-------------|------------|')
    for cname in config_names:
        d = ev['demo_per_config'][cname]
        lines.append(f'| {cname} | {d["mean"]:.1f} | {d["min"]} | {d["max"]} | '
                     f'{"PASS" if d["pass_mean"] else "FAIL"} | {"PASS" if d["pass_min"] else "FAIL"} |')
    lines.append('')
    lines.append(f'Result: **{"PASS" if ev["crit3"] else "FAIL"}**')
    lines.append('')
    # Criterion 4
    lines.append('## Criterion 4: composite urgency variation across configurations')
    lines.append('')
    lines.append(f'Cross-config std at matched (seed, step) divided by mean. '
                 f'Threshold: each composite\'s mean std/mean ratio >= '
                 f'{URGENCY_STD_PCT_THRESHOLD:.0%}.')
    lines.append('')
    lines.append('| Composite | Mean std/mean | Median std/mean | p90 std/mean | Pass? |')
    lines.append('|-----------|----------------|------------------|----------------|--------|')
    for ukey, d in ev['urgency_variation'].items():
        passed = d['mean_std_over_mean'] >= URGENCY_STD_PCT_THRESHOLD
        lines.append(f'| {ukey} | {d["mean_std_over_mean"]:.4f} | '
                     f'{d["median_std_over_mean"]:.4f} | '
                     f'{d["p90_std_over_mean"]:.4f} | '
                     f'{"PASS" if passed else "FAIL"} |')
    lines.append('')
    lines.append(f'Result: **{"PASS" if ev["crit4"] else "FAIL"}**')
    lines.append('')
    # Diagnostics
    lines.append('## Diagnostic: cap binding frequency')
    lines.append('')
    lines.append('| Composite | Cap value | Steps at cap | Total steps | Frequency |')
    lines.append('|-----------|-----------|---------------|--------------|------------|')
    for ukey, d in ev['cap_binding'].items():
        if d is None:
            lines.append(f'| {ukey} | n/a (base-relative) | - | - | - |')
        else:
            lines.append(f'| {ukey} | {d["cap"]:.2f} | {d["n_at_cap"]} | '
                         f'{d["n_total"]} | {d["frequency"]:.4f} |')
    lines.append('')
    lines.append('## Diagnostic: composite urgency distribution')
    lines.append('')
    lines.append('| Composite | Mean | Std | p10 | p50 | p90 | Min | Max |')
    lines.append('|-----------|------|-----|-----|-----|-----|-----|-----|')
    for ukey, d in ev['urgency_distribution'].items():
        lines.append(f'| {ukey} | {d["mean"]:.3f} | {d["std"]:.3f} | '
                     f'{d["p10"]:.3f} | {d["p50"]:.3f} | {d["p90"]:.3f} | '
                     f'{d["min"]:.3f} | {d["max"]:.3f} |')
    lines.append('')
    lines.append('## Disposition')
    lines.append('')
    if overall:
        lines.append('All four criteria pass. Stage 1.7 multiplicative composite urgency '
                     'is validated; the architecture now transmits state variation into '
                     'optimizer choices. Gate 2 can re-run officially under the revised '
                     'architecture.')
    else:
        fails = []
        if not ev['crit1']: fails.append('1 (trajectory divergence)')
        if not ev['crit2']: fails.append('2 (per-step cosine)')
        if not ev['crit3']: fails.append('3 (demographics)')
        if not ev['crit4']: fails.append('4 (urgency variation)')
        lines.append(f'Criteria failed: {", ".join(fails)}. See spec for failure-mode '
                     'response.')
    lines.append('')
    with open(out_path, 'w') as f:
        f.write('\n'.join(lines) + '\n')


def main():
    t0 = time.time()
    per_config = collect()
    wall = time.time() - t0
    print('', flush=True)
    print('Computing pass/fail criteria...', flush=True)
    ev = evaluate(per_config)
    overall = ev['crit1'] and ev['crit2'] and ev['crit3'] and ev['crit4']
    out_path = os.path.join(HERE, 'stage17_integrity_report.md')
    write_report(per_config, ev, wall, out_path)
    print('', flush=True)
    print(f'  C1 trajectory divergence: {"PASS" if ev["crit1"] else "FAIL"}  '
          f'({ev["n_seeds_diverged"]}/5 seeds with cross-config range > {TRAJECTORY_RANGE_THRESHOLD})', flush=True)
    print(f'  C2 per-step cosine:       {"PASS" if ev["crit2"] else "FAIL"}  '
          f'({ev["n_above_cosine"]}/10 pairs > {PER_STEP_COSINE_THRESHOLD})', flush=True)
    print(f'  C3 demographics:          {"PASS" if ev["crit3"] else "FAIL"}', flush=True)
    print(f'  C4 urgency variation:     {"PASS" if ev["crit4"] else "FAIL"}', flush=True)
    print('', flush=True)
    print(f'OVERALL: {"PASS" if overall else "FAIL"}', flush=True)
    print(f'Report: {out_path}', flush=True)
    sys.exit(0 if overall else 1)


if __name__ == '__main__':
    main()
