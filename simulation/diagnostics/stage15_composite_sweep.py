"""Stage 1.5 composite urgency architecture Monte Carlo sweep.

Standalone script. The operator runs this outside Claude Code. The session
that built it ends after small-scale validation; the 10000-sample run is
launched manually by the operator.

Sweeps 31 composite urgency parameters using Sobol quasi-random sampling.
Per sample: evaluates three good-behavior criteria (demographic
sustainability, state sensitivity, urgency dynamic range). Writes
incremental CSV after each sample; regenerates checkpoint summary every
500 samples and at completion.

Production code is bit-for-bit unmodified by this script. Each sample
overrides the relevant module-level constants in `metrics` for the
duration of that sample's evaluation, then restores them. Each worker
process maintains its own module namespace, so cross-sample contamination
is impossible.

Usage:
    python -u simulation/diagnostics/stage15_composite_sweep.py \\
      --samples 10000 --workers 8 --candidates 50 \\
      --smoke-steps 50 --sensitivity-steps 50 \\
      --output-dir simulation/diagnostics/ \\
      [--resume]
"""

import argparse
import csv
import math
import multiprocessing as mp
import os
import sys
import time
import traceback
from collections import OrderedDict
from datetime import datetime

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SIM_DIR = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, SIM_DIR)


# ===========================================================================
# Parameter ranges (31 parameters)
# ===========================================================================

PARAM_RANGES = OrderedDict([
    # Composite caps (5)
    ('WELFARE_URGENCY_CAP',                 (1.0, 5.0)),
    ('AGENCY_URGENCY_CAP',                  (0.8, 3.0)),
    ('INSTITUTION_URGENCY_CAP',             (1.0, 4.0)),
    ('RESILIENCE_URGENCY_CAP',              (1.0, 4.0)),
    ('SUPPRESSION_PENALTY_CAP_MULTIPLIER',  (1.2, 4.0)),
    # Welfare composite coefficients (5)
    ('K_WELFARE_VIABILITY',     (0.0, 1.0)),
    ('K_WELFARE_CAPACITY',      (0.0, 0.5)),
    ('K_WELFARE_SHRINKAGE',     (0.0, 0.7)),
    ('K_WELFARE_AVG_WB_TREND',  (0.0, 0.3)),
    ('K_WELFARE_POP_TREND',     (0.0, 0.2)),
    # Agency composite coefficients (3)
    ('K_AGENCY_VIABILITY',      (0.0, 0.7)),
    ('K_AGENCY_SHRINKAGE',      (0.0, 0.5)),
    ('K_AGENCY_POP_TREND',      (0.0, 0.2)),
    # Institution composite coefficients (6)
    ('K_INSTITUTION_VIABILITY', (0.0, 0.7)),
    ('K_INSTITUTION_CAPACITY',  (0.0, 1.0)),
    ('K_INSTITUTION_SHRINKAGE', (0.0, 0.7)),
    ('K_INSTITUTION_GROWTH',    (0.0, 0.5)),
    ('K_INSTITUTION_POP_TREND', (0.0, 0.3)),
    ('K_INSTITUTION_PSI_TREND', (0.0, 0.4)),
    # Resilience composite coefficients (7)
    ('K_RESILIENCE_VIABILITY',            (0.0, 1.0)),
    ('K_RESILIENCE_CAPACITY',             (0.0, 0.7)),
    ('K_RESILIENCE_SHRINKAGE',            (0.0, 0.5)),
    ('K_RESILIENCE_GROWTH',               (0.0, 0.4)),
    ('K_RESILIENCE_DEFICIT_CONTRIBUTION', (0.0, 0.8)),
    ('K_RESILIENCE_POP_TREND',            (0.0, 0.3)),
    ('K_RESILIENCE_RES_TREND',            (0.0, 0.4)),
    # Suppression composite coefficients (5)
    ('K_SUPPRESSION_VIABILITY', (0.0, 1.0)),
    ('K_SUPPRESSION_CAPACITY',  (0.0, 0.5)),
    ('K_SUPPRESSION_SHRINKAGE', (0.0, 0.7)),
    ('K_SUPPRESSION_POP_TREND', (0.0, 0.3)),
    ('K_SUPPRESSION_PSI_TREND', (0.0, 0.3)),
])

PARAM_NAMES = list(PARAM_RANGES.keys())
N_PARAMS = len(PARAM_NAMES)  # 31

# Design point (production constants) for sweep-comparison reporting.
DESIGN_POINT = OrderedDict([
    ('WELFARE_URGENCY_CAP',                 2.50),
    ('AGENCY_URGENCY_CAP',                  1.50),
    ('INSTITUTION_URGENCY_CAP',             2.00),
    ('RESILIENCE_URGENCY_CAP',              2.00),
    ('SUPPRESSION_PENALTY_CAP_MULTIPLIER',  2.00),
    ('K_WELFARE_VIABILITY',     0.50),
    ('K_WELFARE_CAPACITY',      0.25),
    ('K_WELFARE_SHRINKAGE',     0.35),
    ('K_WELFARE_AVG_WB_TREND',  0.15),
    ('K_WELFARE_POP_TREND',     0.10),
    ('K_AGENCY_VIABILITY',      0.35),
    ('K_AGENCY_SHRINKAGE',      0.25),
    ('K_AGENCY_POP_TREND',      0.10),
    ('K_INSTITUTION_VIABILITY', 0.35),
    ('K_INSTITUTION_CAPACITY',  0.50),
    ('K_INSTITUTION_SHRINKAGE', 0.35),
    ('K_INSTITUTION_GROWTH',    0.25),
    ('K_INSTITUTION_POP_TREND', 0.15),
    ('K_INSTITUTION_PSI_TREND', 0.20),
    ('K_RESILIENCE_VIABILITY',            0.50),
    ('K_RESILIENCE_CAPACITY',             0.35),
    ('K_RESILIENCE_SHRINKAGE',            0.25),
    ('K_RESILIENCE_GROWTH',               0.20),
    ('K_RESILIENCE_DEFICIT_CONTRIBUTION', 0.40),
    ('K_RESILIENCE_POP_TREND',            0.15),
    ('K_RESILIENCE_RES_TREND',            0.20),
    ('K_SUPPRESSION_VIABILITY', 0.50),
    ('K_SUPPRESSION_CAPACITY',  0.25),
    ('K_SUPPRESSION_SHRINKAGE', 0.35),
    ('K_SUPPRESSION_POP_TREND', 0.15),
    ('K_SUPPRESSION_PSI_TREND', 0.15),
])


# ===========================================================================
# Per-sample evaluation
# ===========================================================================

GATE2_CONFIGS = [
    ('A_baseline',  {'rr': 0.066, 'psi': 0.50}),
    ('B_high_rr',   {'rr': 0.085, 'psi': 0.50}),
    ('C_low_rr',    {'rr': 0.055, 'psi': 0.50}),
    ('D_high_psi',  {'rr': 0.066, 'psi': 0.85}),
    ('E_low_psi',   {'rr': 0.066, 'psi': 0.20}),
]
SMOKE_N_AGENTS         = 200
SMOKE_N_SEEDS          = 5
SENSITIVITY_N_AGENTS   = 100
SENSITIVITY_N_SEEDS    = 5
COSINE_THRESHOLD       = 0.10
DEMO_MEAN_THRESHOLD    = 60
DEMO_MIN_THRESHOLD     = 30
URGENCY_RATIO_THRESHOLD = 0.80


def _override_constants(overrides):
    """Temporarily set module-level constants in metrics for this sample's
    composite urgency functions. Returns the saved originals for restoration.
    """
    import metrics
    saved = {}
    for name, value in overrides.items():
        if hasattr(metrics, name):
            saved[name] = getattr(metrics, name)
            setattr(metrics, name, value)
    return saved


def _restore_constants(saved):
    import metrics
    for name, value in saved.items():
        setattr(metrics, name, value)


def _run_one_sim(n_agents, seed, rr, psi_override, n_steps, candidates):
    from model import GardenModel
    cfg = {
        'policy':            'optimize_u_sys_v2',
        'phi':               10.0,
        'reproduction_rate': rr,
        'rollout_steps_v2':  20,
        'n_candidates_v2':   candidates,
        'random_seed':       seed,
    }
    m = GardenModel(n_agents=n_agents, ai_policy='optimize_u_sys_v2', config=cfg)
    if psi_override is not None:
        m.psi_inst_stock = float(psi_override)
        m.previous_psi_inst_stock = float(psi_override)
    for s in range(n_steps):
        if not m.step():
            break
    return m


def _cosine_distance(a, b):
    na = float(np.linalg.norm(a))
    nb = float(np.linalg.norm(b))
    if na == 0 or nb == 0:
        return float('nan')
    return float(1.0 - np.dot(a, b) / (na * nb))


def evaluate_sample(sample_idx, params, candidates, smoke_steps, sensitivity_steps):
    """Run one sample's evaluation. Returns (idx, params, metrics_dict)."""
    t_start = time.time()
    saved = _override_constants(params)
    try:
        from agents import RESOURCE_CATEGORIES

        # --- Criterion 1: demographic sustainability (smoke runs) ---
        smoke_finals = []
        smoke_urgency_means = {
            'combined_welfare_urgency':      [],
            'agency_composite_urgency':      [],
            'institution_composite_urgency': [],
            'resilience_composite_urgency':  [],
            'suppression_composite_penalty': [],
        }
        for seed in range(SMOKE_N_SEEDS):
            m = _run_one_sim(SMOKE_N_AGENTS, seed, 0.066, None,
                              smoke_steps, candidates)
            dc = m.datacollector
            smoke_finals.append(dc['population'][-1] if dc['population'] else 0)
            for k in smoke_urgency_means:
                if dc.get(k):
                    smoke_urgency_means[k].append(float(np.mean(dc[k])))

        mean_final = float(np.mean(smoke_finals)) if smoke_finals else 0.0
        min_final  = float(np.min(smoke_finals))  if smoke_finals else 0.0
        crit1 = (mean_final >= DEMO_MEAN_THRESHOLD
                 and min_final >= DEMO_MIN_THRESHOLD)

        # --- Criterion 2: state sensitivity (5 configs x N seeds) ---
        per_config_mean_alloc = {}
        for cname, cparams in GATE2_CONFIGS:
            all_rows = []
            for seed in range(SENSITIVITY_N_SEEDS):
                m = _run_one_sim(SENSITIVITY_N_AGENTS, seed,
                                  cparams['rr'], cparams['psi'],
                                  sensitivity_steps, candidates)
                dc = m.datacollector
                for i in range(len(dc['population'])):
                    row = [dc[f'x_{c}'][i] for c in RESOURCE_CATEGORIES]
                    row.append(dc['c_protective'][i])
                    row.append(dc['c_suppressive'][i])
                    all_rows.append(row)
            arr = np.array(all_rows, dtype=float)
            mean_alloc = (arr.mean(axis=0) if len(arr)
                          else np.zeros(len(RESOURCE_CATEGORIES) + 2))
            per_config_mean_alloc[cname] = mean_alloc

        config_names = [c for c, _ in GATE2_CONFIGS]
        pair_distances = []
        for i in range(len(config_names)):
            for j in range(i + 1, len(config_names)):
                d = _cosine_distance(per_config_mean_alloc[config_names[i]],
                                       per_config_mean_alloc[config_names[j]])
                pair_distances.append(d)
        pair_distances_clean = [d for d in pair_distances if not math.isnan(d)]
        if pair_distances_clean:
            pairs_above = sum(1 for d in pair_distances_clean if d > COSINE_THRESHOLD)
            max_cos = max(pair_distances_clean)
            mean_cos = float(np.mean(pair_distances_clean))
        else:
            pairs_above = 0
            max_cos = 0.0
            mean_cos = 0.0
        crit2 = (pairs_above >= 3)

        # --- Criterion 3: urgency dynamic range (mean-to-cap ratio) ---
        # Use parameterized caps from this sample.
        cap_lookup = {
            'combined_welfare_urgency':      params.get('WELFARE_URGENCY_CAP',
                                                         DESIGN_POINT['WELFARE_URGENCY_CAP']),
            'agency_composite_urgency':      params.get('AGENCY_URGENCY_CAP',
                                                         DESIGN_POINT['AGENCY_URGENCY_CAP']),
            'institution_composite_urgency': params.get('INSTITUTION_URGENCY_CAP',
                                                         DESIGN_POINT['INSTITUTION_URGENCY_CAP']),
            'resilience_composite_urgency':  params.get('RESILIENCE_URGENCY_CAP',
                                                         DESIGN_POINT['RESILIENCE_URGENCY_CAP']),
            'suppression_composite_penalty': params.get('SUPPRESSION_PENALTY_CAP_MULTIPLIER',
                                                         DESIGN_POINT['SUPPRESSION_PENALTY_CAP_MULTIPLIER']),
        }
        ratios = {}
        for k, cap in cap_lookup.items():
            if smoke_urgency_means[k]:
                grand_mean = float(np.mean(smoke_urgency_means[k]))
                if k == 'suppression_composite_penalty':
                    # The suppression composite caps at CAP_MULT * base, where
                    # base = (1 - total_supp). We compare normalized by an
                    # approximate base of 1.0 to keep the metric comparable
                    # across runs without tracking total_supp per step.
                    ratios[k] = grand_mean / float(cap) if cap > 0 else 0.0
                else:
                    ratios[k] = grand_mean / float(cap) if cap > 0 else 0.0
            else:
                ratios[k] = 0.0
        crit3 = all(r < URGENCY_RATIO_THRESHOLD for r in ratios.values())

        wall_clock = time.time() - t_start
        metrics_out = {
            'mean_final_population':            mean_final,
            'min_final_population':             min_final,
            'pairs_above_threshold':            pairs_above,
            'max_cosine_distance':              max_cos,
            'mean_cosine_distance':             mean_cos,
            'welfare_mean_to_cap':              ratios.get('combined_welfare_urgency', 0.0),
            'agency_mean_to_cap':               ratios.get('agency_composite_urgency', 0.0),
            'institution_mean_to_cap':          ratios.get('institution_composite_urgency', 0.0),
            'resilience_mean_to_cap':           ratios.get('resilience_composite_urgency', 0.0),
            'suppression_mean_to_cap':          ratios.get('suppression_composite_penalty', 0.0),
            'criterion_1_pass':                 bool(crit1),
            'criterion_2_pass':                 bool(crit2),
            'criterion_3_pass':                 bool(crit3),
            'overall_good':                     bool(crit1 and crit2 and crit3),
            'wall_clock_sec':                   wall_clock,
            'error':                            '',
        }
        return sample_idx, params, metrics_out
    except Exception as e:
        wall_clock = time.time() - t_start
        return sample_idx, params, {
            'error':           f'{type(e).__name__}: {e}',
            'wall_clock_sec':  wall_clock,
            'criterion_1_pass': False,
            'criterion_2_pass': False,
            'criterion_3_pass': False,
            'overall_good':    False,
        }
    finally:
        _restore_constants(saved)


def _worker(args):
    """Wrapper for Pool.imap_unordered."""
    sample_idx, params, candidates, smoke_steps, sensitivity_steps = args
    try:
        return evaluate_sample(sample_idx, params, candidates, smoke_steps, sensitivity_steps)
    except Exception as e:
        return sample_idx, params, {
            'error':            f'WORKER FATAL: {type(e).__name__}: {e}',
            'wall_clock_sec':   0.0,
            'criterion_1_pass': False,
            'criterion_2_pass': False,
            'criterion_3_pass': False,
            'overall_good':     False,
        }


# ===========================================================================
# Sobol sampling, CSV writing, checkpointing
# ===========================================================================

def make_sobol_points(n_samples, seed=42):
    """Generate n_samples Sobol points of dimension N_PARAMS in [0, 1)."""
    from scipy.stats import qmc
    sampler = qmc.Sobol(d=N_PARAMS, scramble=True, seed=seed)
    # Scipy's Sobol works best at powers of 2; suppress warnings about non-power.
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        points = sampler.random(n=n_samples)
    return points


def point_to_params(point):
    """Map a Sobol point in [0, 1)^N to parameter values."""
    params = OrderedDict()
    for i, (name, (lo, hi)) in enumerate(PARAM_RANGES.items()):
        params[name] = float(lo + point[i] * (hi - lo))
    return params


CSV_METRIC_FIELDS = [
    'mean_final_population', 'min_final_population',
    'pairs_above_threshold', 'max_cosine_distance', 'mean_cosine_distance',
    'welfare_mean_to_cap', 'agency_mean_to_cap', 'institution_mean_to_cap',
    'resilience_mean_to_cap', 'suppression_mean_to_cap',
    'criterion_1_pass', 'criterion_2_pass', 'criterion_3_pass',
    'overall_good', 'wall_clock_sec', 'error',
]


def csv_header():
    return ['sample_idx'] + PARAM_NAMES + CSV_METRIC_FIELDS


def init_csv(csv_path):
    if not os.path.exists(csv_path):
        with open(csv_path, 'w', newline='') as f:
            w = csv.writer(f)
            w.writerow(csv_header())


def append_csv(csv_path, sample_idx, params, metrics_out):
    row = [sample_idx]
    for name in PARAM_NAMES:
        row.append(f'{params.get(name, 0.0):.6f}')
    for field in CSV_METRIC_FIELDS:
        v = metrics_out.get(field, '')
        if isinstance(v, float):
            row.append(f'{v:.6f}')
        elif isinstance(v, bool):
            row.append('1' if v else '0')
        else:
            row.append(str(v))
    with open(csv_path, 'a', newline='') as f:
        w = csv.writer(f)
        w.writerow(row)


def read_completed_indices(csv_path):
    """Return set of sample_idx that already have rows in the CSV."""
    if not os.path.exists(csv_path):
        return set()
    completed = set()
    with open(csv_path, 'r', newline='') as f:
        r = csv.reader(f)
        next(r, None)  # skip header
        for row in r:
            if row:
                try:
                    completed.add(int(row[0]))
                except (ValueError, IndexError):
                    pass
    return completed


def log_progress(progress_path, sample_idx, total, elapsed, throughput_per_min, eta_min):
    msg = (f'[{datetime.now().isoformat(timespec="seconds")}] '
           f'sample {sample_idx + 1}/{total} '
           f'elapsed {elapsed/60:.1f}min '
           f'throughput {throughput_per_min:.2f}/min '
           f'ETA {eta_min:.1f}min')
    with open(progress_path, 'a') as f:
        f.write(msg + '\n')
    print(msg, flush=True)


def write_checkpoint(checkpoint_path, csv_path, sample_n, total, elapsed, throughput_per_min, eta_min):
    """Regenerate checkpoint summary at this sample count."""
    rows = []
    if os.path.exists(csv_path):
        with open(csv_path, 'r', newline='') as f:
            r = csv.DictReader(f)
            for row in r:
                rows.append(row)

    n_done = len(rows)
    good_rows = [r for r in rows if r.get('overall_good') == '1']
    pass1 = sum(1 for r in rows if r.get('criterion_1_pass') == '1')
    pass2 = sum(1 for r in rows if r.get('criterion_2_pass') == '1')
    pass3 = sum(1 for r in rows if r.get('criterion_3_pass') == '1')
    errors = [r for r in rows if r.get('error', '').strip()]

    lines = []
    lines.append(f'# Stage 1.5 composite sweep checkpoint at sample {sample_n}')
    lines.append('')
    lines.append(f'Generated: {datetime.now().isoformat(timespec="seconds")}')
    lines.append('')
    lines.append('## Progress')
    lines.append('')
    lines.append(f'- Samples completed: {n_done} / {total}')
    lines.append(f'- Samples remaining: {total - n_done}')
    lines.append(f'- Elapsed: {elapsed/60:.1f} min')
    lines.append(f'- Throughput: {throughput_per_min:.2f} samples/min')
    lines.append(f'- ETA: {eta_min:.1f} min')
    lines.append(f'- Errors: {len(errors)}')
    lines.append('')
    lines.append('## Headline')
    lines.append('')
    lines.append(f'**Good samples (passing all three criteria): {len(good_rows)} / {n_done} '
                 f'({100*len(good_rows)/max(n_done,1):.2f}%)**')
    lines.append('')
    lines.append('## Per-criterion pass counts')
    lines.append('')
    lines.append('| Criterion | Pass | Pass rate |')
    lines.append('|-----------|------|-----------|')
    lines.append(f'| 1 (demographic sustainability) | {pass1} | {100*pass1/max(n_done,1):.1f}% |')
    lines.append(f'| 2 (state sensitivity, pairs >= 3) | {pass2} | {100*pass2/max(n_done,1):.1f}% |')
    lines.append(f'| 3 (urgency dynamic range, all ratios < 0.80) | {pass3} | {100*pass3/max(n_done,1):.1f}% |')
    lines.append('')

    if good_rows:
        lines.append('## Good-behavior region characterization')
        lines.append('')
        lines.append('Distribution of each parameter among the `overall_good` samples '
                     'vs. the full sample range. Tight distributions indicate a parameter '
                     'that constrains good behavior.')
        lines.append('')
        lines.append('| Parameter | Range | Good mean | Good min | Good Q25 | Good Q50 | Good Q75 | Good max |')
        lines.append('|-----------|-------|-----------|----------|----------|----------|----------|----------|')
        for name, (lo, hi) in PARAM_RANGES.items():
            vals = []
            for r in good_rows:
                try:
                    vals.append(float(r[name]))
                except (KeyError, ValueError):
                    pass
            if vals:
                a = np.array(vals)
                lines.append(f'| {name} | [{lo}, {hi}] | {a.mean():.3f} | {a.min():.3f} | '
                             f'{np.percentile(a, 25):.3f} | {np.percentile(a, 50):.3f} | '
                             f'{np.percentile(a, 75):.3f} | {a.max():.3f} |')
            else:
                lines.append(f'| {name} | [{lo}, {hi}] | - | - | - | - | - | - |')
        lines.append('')
        lines.append('## Top 5 best samples')
        lines.append('')
        scored = []
        for r in good_rows:
            try:
                pairs = int(r.get('pairs_above_threshold', 0))
                ratios = [float(r.get(k, 1.0)) for k in
                          ('welfare_mean_to_cap', 'agency_mean_to_cap',
                           'institution_mean_to_cap', 'resilience_mean_to_cap',
                           'suppression_mean_to_cap')]
                max_ratio = max(ratios)
                score = pairs - 5 * max_ratio
                scored.append((score, r))
            except (ValueError, KeyError):
                pass
        scored.sort(reverse=True, key=lambda kv: kv[0])
        lines.append('| Rank | sample_idx | pairs_above | max_ratio | mean_final_pop | min_final_pop |')
        lines.append('|------|------------|-------------|-----------|----------------|---------------|')
        for rank, (sc, r) in enumerate(scored[:5], 1):
            try:
                pairs = r.get('pairs_above_threshold', '0')
                ratios = [float(r.get(k, 1.0)) for k in
                          ('welfare_mean_to_cap', 'agency_mean_to_cap',
                           'institution_mean_to_cap', 'resilience_mean_to_cap',
                           'suppression_mean_to_cap')]
                lines.append(f'| {rank} | {r["sample_idx"]} | {pairs} | {max(ratios):.3f} | '
                             f'{r.get("mean_final_population", "-")} | {r.get("min_final_population", "-")} |')
            except (KeyError, ValueError):
                pass
        lines.append('')
    else:
        lines.append('## Good-behavior region')
        lines.append('')
        lines.append('No samples have passed all three criteria yet.')
        lines.append('')
        # Pass-1/pass-2 only characterization for diagnostic insight
        for filter_field, filter_label in [
            ('criterion_1_pass', 'pass criterion 1 only'),
            ('criterion_2_pass', 'pass criterion 2 only'),
            ('criterion_3_pass', 'pass criterion 3 only'),
        ]:
            subset = [r for r in rows if r.get(filter_field) == '1']
            if not subset:
                continue
            lines.append(f'### Samples that {filter_label}: {len(subset)}')
            lines.append('')

    lines.append('## Design point evaluation')
    lines.append('')
    lines.append('| Parameter | Design value | Range | Position in range |')
    lines.append('|-----------|--------------|-------|-------------------|')
    for name, design in DESIGN_POINT.items():
        lo, hi = PARAM_RANGES[name]
        pos = (design - lo) / (hi - lo) if hi > lo else 0.0
        lines.append(f'| {name} | {design} | [{lo}, {hi}] | {pos:.2%} |')
    lines.append('')

    with open(checkpoint_path, 'w') as f:
        f.write('\n'.join(lines) + '\n')


# ===========================================================================
# Main
# ===========================================================================

def main():
    p = argparse.ArgumentParser(description='Stage 1.5 composite urgency Monte Carlo sweep')
    p.add_argument('--samples',           type=int, default=10000)
    p.add_argument('--workers',           type=int, default=max(1, mp.cpu_count() - 1))
    p.add_argument('--candidates',        type=int, default=50)
    p.add_argument('--smoke-steps',       type=int, default=50)
    p.add_argument('--sensitivity-steps', type=int, default=50)
    p.add_argument('--output-dir',        type=str, default=HERE)
    p.add_argument('--checkpoint-every',  type=int, default=500)
    p.add_argument('--resume',            action='store_true')
    p.add_argument('--sobol-seed',        type=int, default=42)
    args = p.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)
    csv_path        = os.path.join(args.output_dir, 'stage15_composite_sweep_results.csv')
    progress_path   = os.path.join(args.output_dir, 'stage15_composite_sweep_progress.log')

    print(f'Stage 1.5 composite sweep', flush=True)
    print(f'  Samples:           {args.samples}', flush=True)
    print(f'  Workers:           {args.workers}', flush=True)
    print(f'  Candidates/step:   {args.candidates}', flush=True)
    print(f'  Smoke steps:       {args.smoke_steps}', flush=True)
    print(f'  Sensitivity steps: {args.sensitivity_steps}', flush=True)
    print(f'  Output dir:        {args.output_dir}', flush=True)
    print(f'  Checkpoint every:  {args.checkpoint_every} samples', flush=True)
    print(f'  Resume:            {args.resume}', flush=True)
    print(f'  Sobol seed:        {args.sobol_seed}', flush=True)
    print('', flush=True)

    # Generate all Sobol points up front (fast, ensures deterministic mapping).
    sobol_points = make_sobol_points(args.samples, seed=args.sobol_seed)

    # Initialize CSV; determine which indices are already done.
    init_csv(csv_path)
    completed = read_completed_indices(csv_path) if args.resume else set()
    if args.resume:
        print(f'Resuming: {len(completed)} samples already completed.', flush=True)
    pending = [i for i in range(args.samples) if i not in completed]
    if not pending:
        print('Nothing to do (all samples already completed).', flush=True)
        return

    # Prepare worker arguments.
    work_items = []
    for idx in pending:
        params = point_to_params(sobol_points[idx])
        work_items.append((idx, params, args.candidates,
                           args.smoke_steps, args.sensitivity_steps))

    print(f'Dispatching {len(work_items)} pending samples to {args.workers} workers...', flush=True)

    t0 = time.time()
    done_count = len(completed)
    with mp.Pool(processes=args.workers) as pool:
        for sample_idx, params, metrics_out in pool.imap_unordered(_worker, work_items):
            append_csv(csv_path, sample_idx, params, metrics_out)
            done_count += 1
            elapsed = time.time() - t0
            throughput = (done_count - len(completed)) / max(elapsed / 60.0, 1e-9)
            eta_min = (args.samples - done_count) / max(throughput, 1e-9)
            log_progress(progress_path, sample_idx, args.samples, elapsed, throughput, eta_min)

            if done_count % args.checkpoint_every == 0 or done_count == args.samples:
                cp_path = os.path.join(
                    args.output_dir,
                    f'stage15_composite_sweep_checkpoint_{done_count:04d}.md'
                )
                write_checkpoint(cp_path, csv_path, done_count, args.samples,
                                  elapsed, throughput, eta_min)
                print(f'  Checkpoint written: {cp_path}', flush=True)

    elapsed = time.time() - t0
    print(f'', flush=True)
    print(f'Sweep complete: {args.samples} samples in {elapsed/60:.1f} min.', flush=True)
    final_cp = os.path.join(args.output_dir, 'stage15_composite_sweep_final.md')
    write_checkpoint(final_cp, csv_path, args.samples, args.samples,
                      elapsed, args.samples / max(elapsed / 60.0, 1e-9), 0.0)
    print(f'Final summary: {final_cp}', flush=True)


if __name__ == '__main__':
    main()
