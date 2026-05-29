"""Gate 3 capability-regime harness.

Run from simulation/:
  python -u diagnostics/gate3_capability_regime.py

Tests that the allocation landscape changes as capability rises.

Run config:
  25 seeds x 100 steps x 6 capability levels {1, 5, 10, 25, 50, 100} at
  default v2 config otherwise.

Pass criteria (both must hold):
  1. At least 3 of the 5 adjacent capability pairs
     ((1,5), (5,10), (10,25), (25,50), (50,100)) show cosine distance > 0.05
     between their mean allocations.
  2. The mean allocation at cap=100 differs from the mean allocation at cap=1
     by cosine distance > 0.10.

Writes diagnostics/gate3_capability_regime_report.md.
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

N_SEEDS  = 25
N_STEPS  = 100
N_AGENTS = 200

CAP_LEVELS = (1, 5, 10, 25, 50, 100)
ADJACENT_THRESHOLD = 0.05
ENDPOINT_THRESHOLD = 0.10
MIN_ADJACENT_PAIRS = 3

ALLOC_AXES = list(RESOURCE_CATEGORIES) + ['c_protective', 'c_suppressive']


def cosine_distance(a, b):
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    na = np.linalg.norm(a)
    nb = np.linalg.norm(b)
    if na == 0 or nb == 0:
        return float('nan')
    return float(1.0 - np.dot(a, b) / (na * nb))


def run_capability_seed(cap, seed):
    cfg = {
        'policy':            'optimize_u_sys_v2',
        'phi':               10.0,
        'reproduction_rate': 0.066,
        'rollout_steps_v2':  20,
        'n_candidates_v2':   300,
        'random_seed':       seed,
    }
    m = GardenModel(n_agents=N_AGENTS, ai_policy='optimize_u_sys_v2', config=cfg)
    # Override initial capability per spec. This is state, not code.
    m.ai.capability = float(cap)
    crashed = False
    extinct_at = None
    for s in range(N_STEPS):
        try:
            if not m.step():
                extinct_at = s + 1
                break
        except Exception as e:
            crashed = True
            print(f'  cap={cap} seed={seed} CRASH at step {s+1}: {e}', flush=True)
            break
    return m, crashed, extinct_at


def collect_per_capability_allocations():
    per_cap = {}
    per_cap_diag = {}
    for cap in CAP_LEVELS:
        all_rows = []
        n_extinct = 0
        extinct_steps = []
        for seed in range(N_SEEDS):
            t0 = time.time()
            m, crashed, extinct_at = run_capability_seed(cap, seed)
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
            print(f'  cap={cap} seed={seed}: {n_steps} steps, {dt:.2f}s, '
                  f'extinct@{extinct_at if extinct_at is not None else "-"}', flush=True)
        arr = np.array(all_rows, dtype=float)
        mean_alloc = arr.mean(axis=0) if len(arr) else np.full(len(ALLOC_AXES), float('nan'))
        per_cap[cap] = mean_alloc
        per_cap_diag[cap] = {
            'n_steps_total': len(all_rows),
            'n_extinct':     n_extinct,
            'extinct_steps_summary': extinct_steps,
            'mean_alloc':    mean_alloc.tolist(),
        }
    return per_cap, per_cap_diag


def write_report(per_cap, per_cap_diag, adjacent_distances, endpoint_distance,
                  n_above_adjacent, passed_adjacent, passed_endpoint, passed,
                  wall_clock, out_path):
    lines = []
    lines.append('# Gate 3: capability-regime gate report')
    lines.append('')
    lines.append(f'Configuration: {N_SEEDS} seeds x {N_STEPS} steps x {len(CAP_LEVELS)} capability levels.')
    lines.append(f'Capability levels: {", ".join(str(c) for c in CAP_LEVELS)}.')
    lines.append('')
    lines.append(f'Wall-clock: {wall_clock:.1f}s total, '
                 f'{wall_clock/(N_SEEDS*len(CAP_LEVELS)):.2f}s per (seed,cap).')
    lines.append('')
    lines.append(f'Overall: **{"PASS" if passed else "FAIL"}**')
    lines.append('')
    lines.append('## Per-capability mean allocation vectors')
    lines.append('')
    lines.append('| Capability | ' + ' | '.join(ALLOC_AXES) + ' | n_steps | n_extinct |')
    lines.append('|------------|' + '|'.join(['---'] * len(ALLOC_AXES)) + '|---------|-----------|')
    for cap in CAP_LEVELS:
        d = per_cap_diag[cap]
        v = d['mean_alloc']
        cells = ' | '.join(f'{x:.3f}' for x in v)
        lines.append(f'| {cap} | {cells} | {d["n_steps_total"]} | {d["n_extinct"]} |')
    lines.append('')
    lines.append('## Pass criteria')
    lines.append('')
    lines.append(f'**Criterion 1**: at least {MIN_ADJACENT_PAIRS} of {len(adjacent_distances)} '
                 f'adjacent capability pairs show cosine distance > {ADJACENT_THRESHOLD}.')
    lines.append('')
    lines.append('| Adjacent pair | Cosine distance | Above 0.05? |')
    lines.append('|---------------|-----------------|--------------|')
    for (a, b), dist in adjacent_distances:
        lines.append(f'| cap={a} vs cap={b} | {dist:.4f} | {"YES" if dist > ADJACENT_THRESHOLD else "no"} |')
    lines.append(f'')
    lines.append(f'Adjacent pairs above 0.05: {n_above_adjacent}/{len(adjacent_distances)}. '
                 f'Required: >= {MIN_ADJACENT_PAIRS}. '
                 f'**{"PASS" if passed_adjacent else "FAIL"}**')
    lines.append('')
    lines.append(f'**Criterion 2**: mean allocation at cap=100 vs cap=1 cosine distance > {ENDPOINT_THRESHOLD}.')
    lines.append('')
    lines.append(f'Measured cap=1 vs cap=100: {endpoint_distance:.4f}. '
                 f'Required: > {ENDPOINT_THRESHOLD}. '
                 f'**{"PASS" if passed_endpoint else "FAIL"}**')
    lines.append('')
    lines.append('## Heatmap (mean share of each category at each capability level)')
    lines.append('')
    lines.append('| Capability | ' + ' | '.join(RESOURCE_CATEGORIES) + ' |')
    lines.append('|------------|' + '|'.join(['---'] * len(RESOURCE_CATEGORIES)) + '|')
    for cap in CAP_LEVELS:
        v = per_cap_diag[cap]['mean_alloc'][:len(RESOURCE_CATEGORIES)]
        cells = ' | '.join(f'{x:.3f}' for x in v)
        lines.append(f'| {cap} | {cells} |')
    lines.append('')
    all_pairs = list(combinations(CAP_LEVELS, 2))
    all_dists = sorted([(p, cosine_distance(per_cap[p[0]], per_cap[p[1]]))
                        for p in all_pairs], key=lambda kv: -kv[1])
    lines.append('## Diagnostic: all capability pairwise cosine distances (sorted)')
    lines.append('')
    for (a, b), dist in all_dists:
        lines.append(f'- cap={a} vs cap={b}: {dist:.4f}')
    lines.append('')
    with open(out_path, 'w') as f:
        f.write('\n'.join(lines) + '\n')


def main():
    print(f'Gate 3 capability-regime: {N_SEEDS} seeds x {N_STEPS} steps x {len(CAP_LEVELS)} cap levels', flush=True)
    t0 = time.time()
    per_cap, per_cap_diag = collect_per_capability_allocations()
    # Adjacent pairs
    adjacent_pairs = [(CAP_LEVELS[i], CAP_LEVELS[i + 1]) for i in range(len(CAP_LEVELS) - 1)]
    adjacent_distances = [((a, b), cosine_distance(per_cap[a], per_cap[b]))
                          for a, b in adjacent_pairs]
    n_above_adjacent = sum(1 for _, d in adjacent_distances if d > ADJACENT_THRESHOLD)
    passed_adjacent = (n_above_adjacent >= MIN_ADJACENT_PAIRS)
    # Endpoint
    endpoint_distance = cosine_distance(per_cap[CAP_LEVELS[0]], per_cap[CAP_LEVELS[-1]])
    passed_endpoint = (endpoint_distance > ENDPOINT_THRESHOLD)
    passed = passed_adjacent and passed_endpoint
    wall_clock = time.time() - t0
    out_path = os.path.join(HERE, 'gate3_capability_regime_report.md')
    write_report(per_cap, per_cap_diag, adjacent_distances, endpoint_distance,
                  n_above_adjacent, passed_adjacent, passed_endpoint, passed,
                  wall_clock, out_path)
    print('', flush=True)
    print(f'Total wall-clock: {wall_clock:.1f}s', flush=True)
    print(f'Adjacent pairs above 0.05: {n_above_adjacent}/{len(adjacent_distances)}', flush=True)
    print(f'Endpoint cap=1 vs cap=100 distance: {endpoint_distance:.4f} (> 0.10?)', flush=True)
    print(f'OVERALL: {"PASS" if passed else "FAIL"}', flush=True)
    print(f'Report: {out_path}', flush=True)
    sys.exit(0 if passed else 1)


if __name__ == '__main__':
    main()
