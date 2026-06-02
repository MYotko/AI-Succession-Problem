"""Stage 1.7 pressure/state/welfare-factor diagnostic.

Run from simulation/:
  python -u diagnostics/stage17_pressure_diagnostic.py

Three diagnostic captures:

  1. Per-config pressure values at matched (seed, step). 9 pressure
     scalars per step (viability, capacity, shrinkage, growth, four
     decline pressures, resilience deficit). Compute cross-configuration
     std/mean ratio. Identifies where the architecture's input signal
     differentiates configurations.

  2. Pre-extinction state and allocation trajectories at steps
     {5, 15, 25, 35}. Captures the transient before any extinction
     truncates runs. Isolates: did configurations diverge during
     the transient, or always converge?

  3. Welfare_factor (net_welfare_return * combined_welfare_urgency,
     clamped to [0, 1]) at matched (seed, step). The actual product
     that drives optimizer behavior; urgency alone can be misleading.

All three are computed from the existing datacollector + state struct.
No production-code modification.

Writes diagnostics/stage17_pressure_diagnostic_report.md.
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
from metrics import (
    compute_viability_pressure, compute_capacity_pressure,
    compute_demographic_pressures, compute_decline_pressure,
    compute_resilience_pressure,
    compute_combined_welfare_urgency,
    welfare_return_curve, dependency_drag_function,
    DiagnosticStateV2,
    _build_state_from_model,
)

PHI_DEFAULT = 10.0
N_SEEDS  = 5
N_STEPS  = 100
N_AGENTS = 100

CONFIGS = [
    ('A_baseline',  {'rr': 0.066, 'psi': 0.50}),
    ('B_high_rr',   {'rr': 0.085, 'psi': 0.50}),
    ('C_low_rr',    {'rr': 0.055, 'psi': 0.50}),
    ('D_high_psi',  {'rr': 0.066, 'psi': 0.85}),
    ('E_low_psi',   {'rr': 0.066, 'psi': 0.20}),
]

PRESSURE_KEYS = [
    'viability_pressure',
    'capacity_pressure',
    'shrinkage_pressure',
    'growth_pressure',
    'avg_wb_decline',
    'population_decline',
    'psi_inst_decline',
    'resilience_decline',
    'resilience_pressure',
]

STATE_KEYS = ['avg_well_being', 'population', 'psi_inst_stock', 'resilience_stock']
ALLOC_KEYS = [
    'x_compute', 'x_bio_welfare', 'x_novelty_agency',
    'x_institutional_capacity', 'x_transfer_comprehension', 'x_resilience',
    'c_protective', 'c_suppressive',
]

SAMPLE_STEPS = [5, 15, 25, 35]


def _build_state_from_dc(dc, i, mvp, cc, reproductive_share):
    """Reconstruct DiagnosticStateV2 from a datacollector row at index i.
    Uses reproductive_share captured at run start (held constant for
    projection; for actual model state, we approximate from initial)."""
    return DiagnosticStateV2(
        avg_wb=float(dc['avg_well_being'][i]),
        population=int(dc['population'][i]),
        min_viable_population=int(mvp),
        carrying_capacity=int(cc),
        expected_births=float(dc['expected_births'][i]) if dc.get('expected_births') else 0.0,
        expected_deaths=float(dc['expected_deaths'][i]) if dc.get('expected_deaths') else 0.0,
        psi_inst_stock=float(dc['psi_inst_stock'][i]),
        resilience_stock=float(dc['resilience_stock'][i]),
        avg_wb_trend=float(dc['avg_wb_trend'][i]),
        population_trend=float(dc['population_trend'][i]),
        psi_inst_trend=float(dc['psi_inst_trend'][i]),
        resilience_trend=float(dc['resilience_trend'][i]),
        projected_avg_age=30.0,  # not used by pressure functions
        reproductive_share=reproductive_share,
    )


def compute_pressures_from_state(state):
    viab = compute_viability_pressure(state.population, state.min_viable_population)
    capa = compute_capacity_pressure(state.population, state.carrying_capacity)
    shrink, growth = compute_demographic_pressures(
        state.expected_births, state.expected_deaths, state.population
    )
    avg_wb_decl = compute_decline_pressure(state.avg_wb_trend)
    pop_decl    = compute_decline_pressure(state.population_trend)
    psi_decl    = compute_decline_pressure(state.psi_inst_trend)
    res_decl    = compute_decline_pressure(state.resilience_trend)
    res_def     = compute_resilience_pressure(state.resilience_stock)
    return {
        'viability_pressure':    viab,
        'capacity_pressure':     capa,
        'shrinkage_pressure':    shrink,
        'growth_pressure':       growth,
        'avg_wb_decline':        avg_wb_decl,
        'population_decline':    pop_decl,
        'psi_inst_decline':      psi_decl,
        'resilience_decline':    res_decl,
        'resilience_pressure':   res_def,
    }


def compute_welfare_factor(x_bio_welfare, x_novelty_agency, welfare_urgency):
    raw = welfare_return_curve(x_bio_welfare)
    drag = dependency_drag_function(x_bio_welfare, x_novelty_agency)
    net = max(0.0, min(1.0, raw - drag))
    return max(0.0, min(1.0, net * welfare_urgency)), net


def run_one(cname, params, seed):
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
    initial_state = _build_state_from_model(m)
    reproductive_share = float(initial_state.reproductive_share)
    extinct_at = None
    for s in range(N_STEPS):
        if not m.step():
            extinct_at = s + 1
            break
    return m, reproductive_share, extinct_at


def collect():
    print('Stage 1.7 pressure diagnostic', flush=True)
    print(f'  configurations: {[c for c, _ in CONFIGS]}', flush=True)
    print(f'  seeds: {N_SEEDS}, steps: {N_STEPS}', flush=True)
    print('', flush=True)
    per_config = {}
    for cname, params in CONFIGS:
        print(f'  config={cname}:', flush=True)
        per_seed = {}
        for seed in range(N_SEEDS):
            t0 = time.time()
            m, reproductive_share, extinct_at = run_one(cname, params, seed)
            dc = m.datacollector
            n = len(dc['population'])
            mvp = m.min_viable_population
            cc = m.config.get('carrying_capacity', 1600)
            # Compute pressures and welfare_factor at every step
            pressures_per_step = []
            welfare_factor_per_step = []
            net_welfare_per_step = []
            for i in range(n):
                state = _build_state_from_dc(dc, i, mvp, cc, reproductive_share)
                pressures_per_step.append(compute_pressures_from_state(state))
                wf, net = compute_welfare_factor(
                    dc['x_bio_welfare'][i],
                    dc['x_novelty_agency'][i],
                    dc['combined_welfare_urgency'][i],
                )
                welfare_factor_per_step.append(wf)
                net_welfare_per_step.append(net)
            per_seed[seed] = {
                'n_steps':       n,
                'extinct_at':    extinct_at,
                'final_pop':     int(dc['population'][-1]) if dc['population'] else 0,
                'states':        {k: list(dc[k]) for k in STATE_KEYS if dc.get(k)},
                'allocations':   {k: list(dc[k]) for k in ALLOC_KEYS if dc.get(k)},
                'urgencies':     {
                    'combined_welfare_urgency':      list(dc.get('combined_welfare_urgency', [])),
                    'agency_composite_urgency':      list(dc.get('agency_composite_urgency', [])),
                    'institution_composite_urgency': list(dc.get('institution_composite_urgency', [])),
                    'resilience_composite_urgency':  list(dc.get('resilience_composite_urgency', [])),
                    'suppression_composite_penalty': list(dc.get('suppression_composite_penalty', [])),
                },
                'pressures':     pressures_per_step,
                'welfare_factor': welfare_factor_per_step,
                'net_welfare':    net_welfare_per_step,
                'wall_clock':    time.time() - t0,
            }
            print(f'    seed={seed}: {n} steps ({per_seed[seed]["wall_clock"]:.1f}s) '
                  f'extinct@{extinct_at if extinct_at else "-"} pop={per_seed[seed]["final_pop"]}', flush=True)
        per_config[cname] = per_seed
    return per_config


def analyze(per_config):
    config_names = [c for c, _ in CONFIGS]

    # Q1: per-config pressure means and cross-config std/mean ratios.
    # Aggregate (mean, std) of each pressure across (seed, step) per config.
    pressure_stats = {}
    for cname in config_names:
        stats = {}
        for pkey in PRESSURE_KEYS:
            vals = []
            for seed in range(N_SEEDS):
                vals.extend([p[pkey] for p in per_config[cname][seed]['pressures']])
            arr = np.array(vals)
            stats[pkey] = {
                'mean':  float(arr.mean()) if arr.size else 0.0,
                'std':   float(arr.std())  if arr.size else 0.0,
                'n':     int(arr.size),
            }
        pressure_stats[cname] = stats

    # Cross-config std/mean ratio per pressure
    cross_config_pressure = {}
    for pkey in PRESSURE_KEYS:
        means = np.array([pressure_stats[c][pkey]['mean'] for c in config_names])
        m = float(means.mean())
        s = float(means.std())
        ratio = (s / abs(m)) if abs(m) > 1e-9 else 0.0
        cross_config_pressure[pkey] = {
            'config_means': dict(zip(config_names, [float(x) for x in means])),
            'mean_of_means': m,
            'std_of_means':  s,
            'ratio_std_over_mean': ratio,
        }

    # Q2: state and allocation values at SAMPLE_STEPS.
    sample_step_analysis = {}
    for step in SAMPLE_STEPS:
        per_config_at_step = {}
        for cname in config_names:
            states = []
            allocs = []
            n_present = 0
            for seed in range(N_SEEDS):
                rec = per_config[cname][seed]
                if step < rec['n_steps']:
                    s = {k: rec['states'][k][step] for k in STATE_KEYS if k in rec['states']}
                    a = [rec['allocations'][k][step] for k in ALLOC_KEYS if k in rec['allocations']]
                    states.append(s)
                    allocs.append(a)
                    n_present += 1
            per_config_at_step[cname] = {
                'n_present':  n_present,
                'mean_state': {
                    k: float(np.mean([s[k] for s in states])) if states else 0.0
                    for k in STATE_KEYS
                },
                'mean_alloc': np.array(allocs).mean(axis=0).tolist() if allocs else [0.0] * 8,
            }
        sample_step_analysis[step] = per_config_at_step

    # Cross-config variance at each sample step: std/mean of state values
    sample_step_variance = {}
    for step in SAMPLE_STEPS:
        cross_state = {}
        for k in STATE_KEYS:
            vals = np.array([sample_step_analysis[step][c]['mean_state'][k] for c in config_names])
            m = float(vals.mean())
            cross_state[k] = {
                'mean_across_configs': m,
                'std_across_configs':  float(vals.std()),
                'ratio': float(vals.std() / abs(m)) if abs(m) > 1e-9 else 0.0,
            }
        # Allocation cross-config cosine distance (max pair)
        max_cos = 0.0
        for (ca, cb) in combinations(config_names, 2):
            a = np.array(sample_step_analysis[step][ca]['mean_alloc'])
            b = np.array(sample_step_analysis[step][cb]['mean_alloc'])
            na, nb = np.linalg.norm(a), np.linalg.norm(b)
            if na > 0 and nb > 0:
                cd = float(1.0 - np.dot(a, b) / (na * nb))
                if cd > max_cos:
                    max_cos = cd
        sample_step_variance[step] = {
            'state':            cross_state,
            'max_alloc_cos':    max_cos,
        }

    # Q3: welfare_factor cross-config analysis.
    welfare_factor_stats = {}
    for cname in config_names:
        vals = []
        net_vals = []
        u_vals = []
        for seed in range(N_SEEDS):
            vals.extend(per_config[cname][seed]['welfare_factor'])
            net_vals.extend(per_config[cname][seed]['net_welfare'])
            u_vals.extend(per_config[cname][seed]['urgencies']['combined_welfare_urgency'])
        welfare_factor_stats[cname] = {
            'wf_mean':       float(np.mean(vals)) if vals else 0.0,
            'wf_std':        float(np.std(vals)) if vals else 0.0,
            'wf_p10':        float(np.percentile(vals, 10)) if vals else 0.0,
            'wf_p90':        float(np.percentile(vals, 90)) if vals else 0.0,
            'net_mean':      float(np.mean(net_vals)) if net_vals else 0.0,
            'urgency_mean':  float(np.mean(u_vals)) if u_vals else 0.0,
        }
    wf_means = np.array([welfare_factor_stats[c]['wf_mean'] for c in config_names])
    welfare_factor_cross_config = {
        'config_means': dict(zip(config_names, [float(x) for x in wf_means])),
        'mean_of_means': float(wf_means.mean()),
        'std_of_means':  float(wf_means.std()),
        'ratio_std_over_mean': float(wf_means.std() / abs(wf_means.mean())) if abs(wf_means.mean()) > 1e-9 else 0.0,
    }

    return {
        'pressure_stats':             pressure_stats,
        'cross_config_pressure':      cross_config_pressure,
        'sample_step_analysis':       sample_step_analysis,
        'sample_step_variance':       sample_step_variance,
        'welfare_factor_stats':       welfare_factor_stats,
        'welfare_factor_cross_config': welfare_factor_cross_config,
    }


def write_report(per_config, analysis, wall_clock, out_path):
    config_names = [c for c, _ in CONFIGS]
    lines = []
    lines.append('# Stage 1.7 pressure / state / welfare-factor diagnostic')
    lines.append('')
    lines.append(f'Wall-clock: {wall_clock/60:.1f} min')
    lines.append('')
    lines.append('## Run summary')
    lines.append('')
    lines.append('| Config | Per-seed extinct steps | Per-seed final pops |')
    lines.append('|--------|------------------------|---------------------|')
    for cname in config_names:
        extincts = [per_config[cname][s]['extinct_at'] for s in range(N_SEEDS)]
        finals = [per_config[cname][s]['final_pop'] for s in range(N_SEEDS)]
        e_str = ', '.join(str(e) if e is not None else '-' for e in extincts)
        f_str = ', '.join(str(f) for f in finals)
        lines.append(f'| {cname} | {e_str} | {f_str} |')
    lines.append('')
    # Q1: pressures
    lines.append('## Q1: pressure values across configurations')
    lines.append('')
    lines.append('Mean (across all seeds and steps) of each pressure scalar '
                 'per configuration. Cross-configuration std/mean ratio shown '
                 'in the last column.')
    lines.append('')
    lines.append('| Pressure | ' + ' | '.join(config_names) + ' | std/mean across configs |')
    lines.append('|----------|' + '|'.join(['---'] * len(config_names)) + '|--------------------------|')
    for pkey in PRESSURE_KEYS:
        cells = ' | '.join(f'{analysis["pressure_stats"][c][pkey]["mean"]:.4f}'
                            for c in config_names)
        ratio = analysis['cross_config_pressure'][pkey]['ratio_std_over_mean']
        flag = ' (>10%)' if ratio > 0.10 else (' (<5%)' if ratio < 0.05 else '')
        lines.append(f'| {pkey} | {cells} | {ratio:.4f}{flag} |')
    lines.append('')
    # Q2: pre-extinction trajectories
    lines.append('## Q2: pre-extinction state and allocation divergence')
    lines.append('')
    for step in SAMPLE_STEPS:
        lines.append(f'### Step {step}')
        lines.append('')
        # Per-config state
        lines.append('| Config | n_seeds_present | avg_wb | population | psi_inst | resilience |')
        lines.append('|--------|------------------|--------|------------|----------|-----------|')
        for cname in config_names:
            d = analysis['sample_step_analysis'][step][cname]
            ms = d['mean_state']
            lines.append(f'| {cname} | {d["n_present"]}/{N_SEEDS} | '
                         f'{ms.get("avg_well_being", 0):.3f} | '
                         f'{ms.get("population", 0):.1f} | '
                         f'{ms.get("psi_inst_stock", 0):.3f} | '
                         f'{ms.get("resilience_stock", 0):.3f} |')
        lines.append('')
        sv = analysis['sample_step_variance'][step]
        lines.append(f'Cross-config std/mean ratios at step {step}:')
        for k in STATE_KEYS:
            d = sv['state'][k]
            lines.append(f'  - {k}: mean={d["mean_across_configs"]:.3f}, '
                         f'std={d["std_across_configs"]:.3f}, ratio={d["ratio"]:.4f}')
        lines.append(f'Max pairwise allocation cosine distance at step {step}: '
                     f'**{sv["max_alloc_cos"]:.4f}**')
        lines.append('')
    # Q3: welfare_factor
    lines.append('## Q3: welfare_factor cross-configuration')
    lines.append('')
    lines.append('welfare_factor = clamp(net_welfare_return * combined_welfare_urgency, 0, 1).')
    lines.append('The actual product that gates the optimizer\'s welfare-related '
                 'candidate ranking.')
    lines.append('')
    lines.append('| Config | net_welfare_return mean | combined_welfare_urgency mean | welfare_factor mean | wf_p10 | wf_p90 |')
    lines.append('|--------|--------------------------|--------------------------------|----------------------|--------|--------|')
    for cname in config_names:
        d = analysis['welfare_factor_stats'][cname]
        lines.append(f'| {cname} | {d["net_mean"]:.4f} | {d["urgency_mean"]:.4f} | '
                     f'{d["wf_mean"]:.4f} | {d["wf_p10"]:.4f} | {d["wf_p90"]:.4f} |')
    lines.append('')
    wfcc = analysis['welfare_factor_cross_config']
    lines.append(f'Cross-config welfare_factor mean across configs: {wfcc["mean_of_means"]:.4f}')
    lines.append(f'Cross-config welfare_factor std across configs:  {wfcc["std_of_means"]:.4f}')
    lines.append(f'Cross-config welfare_factor std/mean ratio:      {wfcc["ratio_std_over_mean"]:.4f}')
    lines.append('')
    with open(out_path, 'w') as f:
        f.write('\n'.join(lines) + '\n')


def main():
    t0 = time.time()
    per_config = collect()
    wall = time.time() - t0
    print('', flush=True)
    print('Analyzing diagnostic captures...', flush=True)
    analysis = analyze(per_config)
    out_path = os.path.join(HERE, 'stage17_pressure_diagnostic_report.md')
    write_report(per_config, analysis, wall, out_path)
    print('', flush=True)
    print(f'Wall-clock: {wall/60:.1f} min', flush=True)
    print(f'Report:     {out_path}', flush=True)


if __name__ == '__main__':
    main()
