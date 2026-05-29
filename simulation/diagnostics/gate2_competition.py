"""Gate 2 competition harness.

Run from simulation/:
  python -u diagnostics/gate2_competition.py

Tests that different states produce different winning allocations.

Run config:
  15 seeds x 100 steps x 5 distinct configurations.

The five configurations vary the starting state:
  A baseline:  rr=0.066, Psi_inst=0.50, pop=100, wb=0.50
  B high-rr:   rr=0.085, Psi_inst=0.50, pop=100, wb=0.50
  C low-rr:    rr=0.055, Psi_inst=0.50, pop=100, wb=0.50
  D high-psi:  rr=0.066, Psi_inst=0.85, pop=100, wb=0.50
  E low-psi:   rr=0.066, Psi_inst=0.20, pop=100, wb=0.50

Pass criterion: at least 3 of 10 pairwise cosine distances between the five
configurations' mean allocation vectors are > 0.10.

Writes diagnostics/gate2_competition_report.md.
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
from agents import RESOURCE_CATEGORIES

N_SEEDS  = 15
N_STEPS  = 100
N_AGENTS = 100  # fixed at 100 per spec
COSINE_THRESHOLD = 0.10
MIN_PAIRS = 3
N_PAIRS_TOTAL = 10  # C(5, 2)

CONFIGS = {
    'A_baseline':  {'rr': 0.066, 'psi': 0.50},
    'B_high_rr':   {'rr': 0.085, 'psi': 0.50},
    'C_low_rr':    {'rr': 0.055, 'psi': 0.50},
    'D_high_psi':  {'rr': 0.066, 'psi': 0.85},
    'E_low_psi':   {'rr': 0.066, 'psi': 0.20},
}

ALLOC_AXES = list(RESOURCE_CATEGORIES) + ['c_protective', 'c_suppressive']


def cosine_distance(a, b):
    """1 - cos similarity; result in [0, 2] for general vectors, [0, 1] for non-negative."""
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    na = np.linalg.norm(a)
    nb = np.linalg.norm(b)
    if na == 0 or nb == 0:
        return float('nan')
    return float(1.0 - np.dot(a, b) / (na * nb))


def run_config_seed(config_name, params, seed):
    cfg = {
        'policy':            'optimize_u_sys_v2',
        'phi':               10.0,
        'reproduction_rate': params['rr'],
        'rollout_steps_v2':  20,
        'n_candidates_v2':   300,
        'random_seed':       seed,
        # Force initial avg_wb = 0.5 by clamping the uniform sampler endpoints
        'wb_min':            0.50,
        'wb_max':            0.50,
    }
    m = GardenModel(n_agents=N_AGENTS, ai_policy='optimize_u_sys_v2', config=cfg)
    # Override initial Psi_inst stock per config spec. This is state, not code.
    m.psi_inst_stock = float(params['psi'])
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


def collect_per_config_allocations():
    """Return dict mapping config_name -> mean 8-dim allocation vector across all
    (seeds x steps) decision steps; plus per-config diagnostics."""
    per_config = {}
    per_config_diag = {}
    for cname, params in CONFIGS.items():
        all_rows = []
        n_extinct = 0
        extinct_steps = []
        for seed in range(N_SEEDS):
            t0 = time.time()
            m, crashed, extinct_at = run_config_seed(cname, params, seed)
            dc = m.datacollector
            n_steps = len(dc['population'])
            for i in range(n_steps):
                row = [dc[f'x_{c}'][i] for c in RESOURCE_CATEGORIES]
                row.append(dc['c_protective'][i])
                row.append(dc['c_suppressive'][i])
                all_rows.append(row)
            if extinct_at is not None:
                n_extinct += 1
                extinct_steps.append(extinct_at)
            dt = time.time() - t0
            print(f'  config={cname} seed={seed}: {n_steps} steps, {dt:.2f}s, '
                  f'extinct@{extinct_at if extinct_at is not None else "-"}', flush=True)
        arr = np.array(all_rows, dtype=float)
        mean_alloc = arr.mean(axis=0) if len(arr) else np.full(len(ALLOC_AXES), float('nan'))
        per_config[cname] = mean_alloc
        per_config_diag[cname] = {
            'n_steps_total': len(all_rows),
            'n_extinct':     n_extinct,
            'extinct_steps_summary': extinct_steps,
            'mean_alloc':    mean_alloc.tolist(),
        }
    return per_config, per_config_diag


def write_report(per_config, per_config_diag, pair_distances, n_above, passed,
                  wall_clock, out_path):
    lines = []
    lines.append('# Gate 2: competition gate report')
    lines.append('')
    lines.append(f'Configuration: {N_SEEDS} seeds x {N_STEPS} steps x {len(CONFIGS)} configurations.')
    lines.append('')
    lines.append(f'Wall-clock: {wall_clock:.1f}s total, '
                 f'{wall_clock/(N_SEEDS*len(CONFIGS)):.2f}s per (seed,config).')
    lines.append('')
    lines.append(f'Overall: **{"PASS" if passed else "FAIL"}**')
    lines.append('')
    lines.append('## Configurations')
    lines.append('')
    lines.append('| Name | rr | Initial Psi_inst | n_agents | Initial avg_wb |')
    lines.append('|------|----|------------------|----------|----------------|')
    for cname, params in CONFIGS.items():
        lines.append(f'| {cname} | {params["rr"]} | {params["psi"]} | {N_AGENTS} | 0.50 |')
    lines.append('')
    lines.append('## Per-configuration mean allocation vectors')
    lines.append('')
    lines.append('| Config | ' + ' | '.join(ALLOC_AXES) + ' | n_steps | n_extinct |')
    lines.append('|--------|' + '|'.join(['---'] * len(ALLOC_AXES)) + '|---------|-----------|')
    for cname in CONFIGS:
        d = per_config_diag[cname]
        v = d['mean_alloc']
        cells = ' | '.join(f'{x:.3f}' for x in v)
        lines.append(f'| {cname} | {cells} | {d["n_steps_total"]} | {d["n_extinct"]} |')
    lines.append('')
    lines.append('## Pairwise cosine distances (between mean allocation vectors)')
    lines.append('')
    lines.append('| Pair | Cosine distance | Above threshold (0.10)? |')
    lines.append('|------|-----------------|-------------------------|')
    for (a, b), dist in pair_distances:
        lines.append(f'| {a} vs {b} | {dist:.4f} | {"YES" if dist > COSINE_THRESHOLD else "no"} |')
    lines.append('')
    lines.append(f'Pairs above threshold (0.10): **{n_above}/{N_PAIRS_TOTAL}**')
    lines.append(f'Required: >= {MIN_PAIRS}')
    lines.append('')
    sorted_pairs = sorted(pair_distances, key=lambda kv: -kv[1])
    lines.append('## Diagnostic: which configurations differ most from which')
    lines.append('')
    lines.append('Sorted by descending cosine distance:')
    lines.append('')
    for (a, b), dist in sorted_pairs:
        lines.append(f'- {a} vs {b}: {dist:.4f}')
    lines.append('')
    with open(out_path, 'w') as f:
        f.write('\n'.join(lines) + '\n')


def main():
    print(f'Gate 2 competition: {N_SEEDS} seeds x {N_STEPS} steps x {len(CONFIGS)} configs', flush=True)
    t0 = time.time()
    per_config, per_config_diag = collect_per_config_allocations()
    pair_distances = []
    for a, b in combinations(CONFIGS.keys(), 2):
        d = cosine_distance(per_config[a], per_config[b])
        pair_distances.append(((a, b), d))
    n_above = sum(1 for _, d in pair_distances if d > COSINE_THRESHOLD)
    passed = (n_above >= MIN_PAIRS)
    wall_clock = time.time() - t0
    out_path = os.path.join(HERE, 'gate2_competition_report.md')
    write_report(per_config, per_config_diag, pair_distances, n_above, passed, wall_clock, out_path)
    print('', flush=True)
    print(f'Total wall-clock: {wall_clock:.1f}s', flush=True)
    print(f'Pairs above cosine threshold (0.10): {n_above}/{N_PAIRS_TOTAL}', flush=True)
    print(f'OVERALL: {"PASS" if passed else "FAIL"}', flush=True)
    print(f'Report: {out_path}', flush=True)
    sys.exit(0 if passed else 1)


if __name__ == '__main__':
    main()
