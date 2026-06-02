"""Stage 1.8 Phase A integrity simulation.

Run from simulation/:
  python -u diagnostics/stage18_integrity_simulation_phase_a.py

Validates the working_factor architecture's basic functioning:
  1. No crashes / NaN across 25 runs (5 phi x 5 seeds x 100 steps)
  2. Demographic sustainability at default phi (mean final pop >= 60,
     min final pop >= 30)
  3. State responsiveness (std of avg_wb, psi_inst_stock, resilience_stock
     each > 0.05 across the 100-step run)
  4. Phi behavioral channel preserved (per-seed cross-phi final pop range
     > 15 in at least 3 of 5 seeds)

Phase A is configured at default v2 (composite urgency layer is retired
in the production code; nothing to disable). Phi varies across {1, 5,
10, 25, 100}. Same per-seed/per-config structure as Stage 1.6 integrity.

Writes diagnostics/stage18_integrity_phase_a_report.md.
"""

import os
import sys
import time
import math
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

DEMO_MEAN_THRESHOLD = 60
DEMO_MIN_THRESHOLD  = 30
STATE_STD_THRESHOLD = 0.05
PHI_RANGE_THRESHOLD = 15
PHI_RANGE_SEEDS_REQUIRED = 3


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
            print(f'  phi={phi} seed={seed} CRASH step {s+1}: {e}', flush=True)
            break
    dc = m.datacollector
    if dc.get('u_sys_v2'):
        for v in dc['u_sys_v2']:
            if v != v:
                nan_found = True
                break
    return m, crashed, nan_found, extinct_at


def collect():
    print('Stage 1.8 Phase A integrity simulation', flush=True)
    print(f'  phi values: {list(PHI_VALUES)}', flush=True)
    print(f'  seeds: {N_SEEDS}, steps: {N_STEPS}', flush=True)
    print('', flush=True)
    per_phi = {}
    for phi in PHI_VALUES:
        print(f'  phi={phi:6.1f}:', flush=True)
        seeds_data = []
        for seed in range(N_SEEDS):
            t0 = time.time()
            m, crashed, nan_found, extinct_at = run_one(phi, seed)
            dc = m.datacollector
            n = len(dc['population'])
            final_pop = int(dc['population'][-1]) if dc['population'] else 0
            avg_wb_series = dc['avg_well_being']
            psi_series = dc['psi_inst_stock']
            res_series = dc['resilience_stock']
            theta_series = dc.get('theta_capability', [])
            xfer_series = dc.get('transfer_state', [])
            seeds_data.append({
                'seed': seed, 'n_steps': n, 'crashed': crashed, 'nan': nan_found,
                'extinct_at': extinct_at, 'final_pop': final_pop,
                'avg_wb_std':    float(np.std(avg_wb_series)) if avg_wb_series else 0.0,
                'psi_std':       float(np.std(psi_series)) if psi_series else 0.0,
                'res_std':       float(np.std(res_series)) if res_series else 0.0,
                'theta_std':     float(np.std(theta_series)) if theta_series else 0.0,
                'xfer_std':      float(np.std(xfer_series)) if xfer_series else 0.0,
                'final_state': {
                    'avg_wb': float(avg_wb_series[-1]) if avg_wb_series else 0.0,
                    'psi':    float(psi_series[-1])    if psi_series else 0.0,
                    'res':    float(res_series[-1])    if res_series else 0.0,
                    'theta':  float(theta_series[-1])  if theta_series else 0.0,
                    'xfer':   float(xfer_series[-1])   if xfer_series else 0.0,
                },
                'wall_clock': time.time() - t0,
            })
            print(f'    seed={seed}: {n} steps, {seeds_data[-1]["wall_clock"]:.1f}s, '
                  f'final pop={final_pop}', flush=True)
        per_phi[phi] = seeds_data
    return per_phi


def evaluate(per_phi):
    # Criterion 1: no crashes / no NaN
    crashes = sum(1 for phi in PHI_VALUES for s in per_phi[phi] if s['crashed'])
    nans = sum(1 for phi in PHI_VALUES for s in per_phi[phi] if s['nan'])
    crit1 = (crashes == 0 and nans == 0)

    # Criterion 2: demographic sustainability at default phi=10
    phi10_finals = [s['final_pop'] for s in per_phi[10.0]]
    demo_mean = float(np.mean(phi10_finals))
    demo_min  = int(min(phi10_finals))
    crit2 = (demo_mean >= DEMO_MEAN_THRESHOLD and demo_min >= DEMO_MIN_THRESHOLD)

    # Criterion 3: state responsiveness at default phi=10
    avg_wb_stds = [s['avg_wb_std'] for s in per_phi[10.0]]
    psi_stds    = [s['psi_std']    for s in per_phi[10.0]]
    res_stds    = [s['res_std']    for s in per_phi[10.0]]
    theta_stds  = [s['theta_std']  for s in per_phi[10.0]]
    xfer_stds   = [s['xfer_std']   for s in per_phi[10.0]]
    state_mean_stds = {
        'avg_wb':           float(np.mean(avg_wb_stds)),
        'psi_inst_stock':   float(np.mean(psi_stds)),
        'resilience_stock': float(np.mean(res_stds)),
        'theta_capability': float(np.mean(theta_stds)),
        'transfer_state':   float(np.mean(xfer_stds)),
    }
    crit3 = all(v > STATE_STD_THRESHOLD for k, v in state_mean_stds.items()
                if k in ('avg_wb', 'psi_inst_stock', 'resilience_stock'))

    # Criterion 4: phi behavioral channel (Stage 1.6 trajectory divergence)
    per_seed_phi_range = {}
    for seed in range(N_SEEDS):
        pops = [next((s['final_pop'] for s in per_phi[phi] if s['seed'] == seed), 0)
                for phi in PHI_VALUES]
        per_seed_phi_range[seed] = {
            'pops':  dict(zip(PHI_VALUES, pops)),
            'min':   int(min(pops)),
            'max':   int(max(pops)),
            'range': int(max(pops) - min(pops)),
        }
    n_seeds_diverged = sum(1 for d in per_seed_phi_range.values()
                            if d['range'] > PHI_RANGE_THRESHOLD)
    crit4 = (n_seeds_diverged >= PHI_RANGE_SEEDS_REQUIRED)

    return {
        'crit1': crit1, 'crashes': crashes, 'nans': nans,
        'crit2': crit2, 'demo_mean': demo_mean, 'demo_min': demo_min,
        'phi10_finals': phi10_finals,
        'crit3': crit3, 'state_mean_stds': state_mean_stds,
        'crit4': crit4, 'n_seeds_diverged': n_seeds_diverged,
        'per_seed_phi_range': per_seed_phi_range,
    }


def write_report(per_phi, ev, wall, out_path):
    overall = ev['crit1'] and ev['crit2'] and ev['crit3'] and ev['crit4']
    lines = []
    lines.append('# Stage 1.8 Phase A integrity report')
    lines.append('')
    lines.append(f'Overall: **{"PASS" if overall else "FAIL"}**')
    lines.append('')
    lines.append('## Configuration')
    lines.append('')
    lines.append(f'- phi values: {list(PHI_VALUES)}')
    lines.append(f'- seeds: {N_SEEDS}, steps: {N_STEPS}, agents: {N_AGENTS}')
    lines.append(f'- composite urgency layer: retired (Stage 1.8)')
    lines.append(f'- working_factor: STATE_ALLOCATION_MAPPING placeholder')
    lines.append(f'- wall-clock: {wall/60:.1f} min')
    lines.append('')
    lines.append('## Criterion 1: no crashes, no NaN')
    lines.append(f'- Crashes: {ev["crashes"]} / 25')
    lines.append(f'- NaN values: {ev["nans"]} / 25')
    lines.append(f'- Result: **{"PASS" if ev["crit1"] else "FAIL"}**')
    lines.append('')
    lines.append('## Criterion 2: demographic sustainability at default phi=10')
    lines.append('')
    lines.append(f'- Final populations (seeds 0-4): {ev["phi10_finals"]}')
    lines.append(f'- Mean: {ev["demo_mean"]:.1f} (threshold: >= {DEMO_MEAN_THRESHOLD})')
    lines.append(f'- Min:  {ev["demo_min"]} (threshold: >= {DEMO_MIN_THRESHOLD})')
    lines.append(f'- Result: **{"PASS" if ev["crit2"] else "FAIL"}**')
    lines.append('')
    lines.append('## Criterion 3: state responsiveness at default phi=10')
    lines.append('')
    lines.append('Mean (across seeds) of per-run std for each state variable.')
    lines.append('avg_wb, psi_inst_stock, resilience_stock must each exceed '
                 f'{STATE_STD_THRESHOLD}.')
    lines.append('')
    lines.append('| State variable | Mean std | Threshold | Pass? |')
    lines.append('|----------------|----------|-----------|-------|')
    for k, v in ev['state_mean_stds'].items():
        threshold = STATE_STD_THRESHOLD if k in ('avg_wb', 'psi_inst_stock', 'resilience_stock') else 'informational'
        if isinstance(threshold, float):
            passed = v > threshold
            lines.append(f'| {k} | {v:.4f} | > {threshold} | {"PASS" if passed else "FAIL"} |')
        else:
            lines.append(f'| {k} | {v:.4f} | informational | - |')
    lines.append('')
    lines.append(f'Result: **{"PASS" if ev["crit3"] else "FAIL"}**')
    lines.append('')
    lines.append('## Criterion 4: phi behavioral channel preserved')
    lines.append('')
    lines.append(f'Per-seed final pop range across phi values; need range > '
                 f'{PHI_RANGE_THRESHOLD} in >= {PHI_RANGE_SEEDS_REQUIRED} of 5 seeds '
                 '(Stage 1.6 metric).')
    lines.append('')
    lines.append('| Seed | phi=1 | phi=5 | phi=10 | phi=25 | phi=100 | range | > 15? |')
    lines.append('|------|-------|-------|--------|--------|---------|-------|-------|')
    for seed, d in ev['per_seed_phi_range'].items():
        pops = ' | '.join(str(d['pops'][phi]) for phi in PHI_VALUES)
        passed = d['range'] > PHI_RANGE_THRESHOLD
        lines.append(f'| {seed} | {pops} | {d["range"]} | {"YES" if passed else "no"} |')
    lines.append('')
    lines.append(f'Seeds diverged: **{ev["n_seeds_diverged"]} / 5** (need >= {PHI_RANGE_SEEDS_REQUIRED}). '
                 f'Result: **{"PASS" if ev["crit4"] else "FAIL"}**')
    lines.append('')
    lines.append('## Per-seed final state snapshot (phi=10)')
    lines.append('')
    lines.append('| Seed | final pop | avg_wb | psi | resilience | theta_capability | transfer_state |')
    lines.append('|------|-----------|--------|-----|------------|-------------------|------------------|')
    for s in per_phi[10.0]:
        fs = s['final_state']
        lines.append(f'| {s["seed"]} | {s["final_pop"]} | {fs["avg_wb"]:.3f} | {fs["psi"]:.3f} | '
                     f'{fs["res"]:.3f} | {fs["theta"]:.3f} | {fs["xfer"]:.3f} |')
    lines.append('')
    with open(out_path, 'w') as f:
        f.write('\n'.join(lines) + '\n')


def main():
    t0 = time.time()
    per_phi = collect()
    wall = time.time() - t0
    print('', flush=True)
    print('Evaluating Phase A criteria...', flush=True)
    ev = evaluate(per_phi)
    out_path = os.path.join(HERE, 'stage18_integrity_phase_a_report.md')
    write_report(per_phi, ev, wall, out_path)
    overall = ev['crit1'] and ev['crit2'] and ev['crit3'] and ev['crit4']
    print('', flush=True)
    print(f'  C1 no crashes/NaN:       {"PASS" if ev["crit1"] else "FAIL"} ({ev["crashes"]} crashes, {ev["nans"]} nans)', flush=True)
    print(f'  C2 demographic (phi=10): {"PASS" if ev["crit2"] else "FAIL"} (mean {ev["demo_mean"]:.1f}, min {ev["demo_min"]})', flush=True)
    print(f'  C3 state responsiveness: {"PASS" if ev["crit3"] else "FAIL"}', flush=True)
    print(f'  C4 phi channel:          {"PASS" if ev["crit4"] else "FAIL"} ({ev["n_seeds_diverged"]}/5 seeds with cross-phi range > {PHI_RANGE_THRESHOLD})', flush=True)
    print('', flush=True)
    print(f'OVERALL Phase A: {"PASS" if overall else "FAIL"}', flush=True)
    print(f'Wall-clock: {wall/60:.1f} min', flush=True)
    print(f'Report: {out_path}', flush=True)
    sys.exit(0 if overall else 1)


if __name__ == '__main__':
    main()
