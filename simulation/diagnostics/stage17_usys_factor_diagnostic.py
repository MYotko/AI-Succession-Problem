"""Stage 1.7 U_sys factor breakdown diagnostic.

Run from simulation/:
  python -u diagnostics/stage17_usys_factor_diagnostic.py

Captures the full per-step U_sys factor decomposition across the five
Stage 1.7 test configurations:

  welfare_factor        (= h_eff_v2 = clamp(net_welfare_return *
                          combined_welfare_urgency, 0, 1))
  institution_return    (= clamp(raw_institution_return *
                          institution_composite_urgency, 0, 1))
  agency_factor         (= clamp(raw_agency_return *
                          agency_composite_urgency, 0, 1))
  resilience_return     (= clamp(raw_resilience_return *
                          resilience_composite_urgency, 0, 1))
  frontier_capability   (action-only)
  transfer_factor       (action-only)
  theta_tech_v2         (= frontier * transfer * institution_return *
                          agency_factor * resilience_return)
  l_t_v2                (= welfare_factor * psi_inst_stock * theta_tech_v2)
  per-step u_sys_v2     (= A_t * (discount + LAMBDA * l_t_v2))
  rank_2_u_sys          (rollout sum of 2nd-best candidate)
  rank_10_u_sys         (rollout sum of 10th-best candidate)

All factors recomputed from action + state + urgencies already in the
datacollector. No production code changes.

For each factor, compute cross-config std/mean ratio at matched (seed,
step). Identifies which factors actually vary across configurations and
where the variation gets washed out.

Writes diagnostics/stage17_usys_factor_diagnostic_report.md.
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

# Import the production constants so factor reconstruction uses the same
# values as the live model.
from metrics import (
    H_N_AGENCY_SAT_K, H_N_SUPPRESSION_EXP, H_N_BASE_FLOOR,
    H_E_COMPUTE_SAT_K, H_E_BASE_FLOOR,
    FRONTIER_COMPUTE_K, FRONTIER_BASE_LEVEL,
    TRANSFER_SAT_K, PSI_ABSORPTION_K,
    WELFARE_ADEQUACY_K, DEPENDENCY_DRAG_K, RESILIENCE_ADEQUACY_K,
    welfare_return_curve, dependency_drag_function, raw_resilience_return,
    _total_suppression_from_action, _clamp,
)
from constants_v2_stage15 import LAMBDA_LINEAGE_COUPLING

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

FACTOR_KEYS = [
    'welfare_factor',
    'institution_return',
    'agency_factor',
    'resilience_return',
    'frontier_capability',
    'transfer_factor',
    'theta_tech_v2',
    'l_t_v2',
    'u_sys_v2_per_step',
    'rank_2_rollout_score',
    'rank_10_rollout_score',
]


def reconstruct_factors_at_step(dc, i):
    """Recompute U_sys factor breakdown at step i from datacollector state.

    Pulls action, state, urgencies from the row at index i and reproduces
    the calculate_system_metrics_v2 formulas. Returns a dict of all factors
    listed in FACTOR_KEYS.
    """
    # Action
    x_compute   = float(dc['x_compute'][i])
    x_welfare   = float(dc['x_bio_welfare'][i])
    x_agency    = float(dc['x_novelty_agency'][i])
    x_inst_cap  = float(dc['x_institutional_capacity'][i])
    x_transfer  = float(dc['x_transfer_comprehension'][i])
    x_resilience = float(dc['x_resilience'][i])
    c_protective  = float(dc['c_protective'][i])
    c_suppressive = float(dc['c_suppressive'][i])
    action = {
        'x_compute':                x_compute,
        'x_bio_welfare':            x_welfare,
        'x_novelty_agency':         x_agency,
        'x_institutional_capacity': x_inst_cap,
        'x_transfer_comprehension': x_transfer,
        'x_resilience':             x_resilience,
        'c_protective':             c_protective,
        'c_suppressive':            c_suppressive,
    }

    # State at this step
    psi_stock = float(dc['psi_inst_stock'][i])

    # Urgencies (already computed; pull from datacollector)
    welfare_u = float(dc['combined_welfare_urgency'][i])
    agency_u  = float(dc['agency_composite_urgency'][i])
    inst_u    = float(dc['institution_composite_urgency'][i])
    res_u     = float(dc['resilience_composite_urgency'][i])
    supp_composite = float(dc['suppression_composite_penalty'][i])

    # Suppression dampening: composite already clamped to [base, CAP_MULT*base];
    # the downstream usage clamps to [0, 1].
    enhanced_dampening = max(0.0, min(1.0, supp_composite))

    # Welfare factor: clamp(net_welfare_return * welfare_u, 0, 1)
    raw_welfare = welfare_return_curve(x_welfare)
    drag = dependency_drag_function(x_welfare, x_agency)
    net_welfare = max(0.0, min(1.0, raw_welfare - drag))
    welfare_factor = max(0.0, min(1.0, net_welfare * welfare_u))

    # Agency factor: clamp(x_novelty_agency * enhanced_dampening * agency_u, 0, 1)
    raw_agency_return = x_agency * enhanced_dampening
    agency_factor = max(0.0, min(1.0, raw_agency_return * agency_u))

    # Institution return: clamp(institutional_saturation * inst_u, 0, 1)
    raw_inst_return = float(1.0 - np.exp(-PSI_ABSORPTION_K * psi_stock))
    institution_return = max(0.0, min(1.0, raw_inst_return * inst_u))

    # Resilience return: clamp(raw_resilience_return * res_u, 0, 1)
    raw_res = raw_resilience_return(float(dc['resilience_stock'][i]))
    resilience_return = max(0.0, min(1.0, raw_res * res_u))

    # Frontier capability and transfer factor are action-only
    frontier = float(FRONTIER_BASE_LEVEL + (1.0 - FRONTIER_BASE_LEVEL) * (
        1.0 - np.exp(-FRONTIER_COMPUTE_K * x_compute)
    ))
    transfer = float(1.0 - np.exp(-TRANSFER_SAT_K * x_transfer))

    # theta_tech_v2 (5-factor product)
    theta_tech = frontier * transfer * institution_return * agency_factor * resilience_return

    # l_t_v2 = welfare_factor * psi_stock * theta_tech
    l_t = welfare_factor * psi_stock * theta_tech

    # per-step u_sys_v2 reconstructed from datacollector (already stored)
    u_sys_per_step = float(dc['u_sys_v2'][i])

    # Rollout-score proxies via the rank_2 / rank_10 datacollector entries
    rank_2  = float(dc.get('rank_2_u_sys',  [0.0])[i]) if dc.get('rank_2_u_sys') else 0.0
    rank_10 = float(dc.get('rank_10_u_sys', [0.0])[i]) if dc.get('rank_10_u_sys') else 0.0

    return {
        'welfare_factor':       welfare_factor,
        'institution_return':   institution_return,
        'agency_factor':        agency_factor,
        'resilience_return':    resilience_return,
        'frontier_capability':  frontier,
        'transfer_factor':      transfer,
        'theta_tech_v2':        theta_tech,
        'l_t_v2':               l_t,
        'u_sys_v2_per_step':    u_sys_per_step,
        'rank_2_rollout_score':  rank_2,
        'rank_10_rollout_score': rank_10,
    }


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
    for s in range(N_STEPS):
        if not m.step():
            break
    return m


def collect():
    print('Stage 1.7 U_sys factor breakdown diagnostic', flush=True)
    print(f'  configs: {[c for c, _ in CONFIGS]}', flush=True)
    print(f'  seeds: {N_SEEDS}, steps: {N_STEPS}', flush=True)
    print('', flush=True)
    per_config = {}
    for cname, params in CONFIGS:
        print(f'  config={cname}:', flush=True)
        per_seed = {}
        for seed in range(N_SEEDS):
            t0 = time.time()
            m = run_one(cname, params, seed)
            dc = m.datacollector
            n = len(dc['population'])
            factors_per_step = []
            for i in range(n):
                factors_per_step.append(reconstruct_factors_at_step(dc, i))
            per_seed[seed] = {
                'n_steps':          n,
                'final_pop':        int(dc['population'][-1]) if dc['population'] else 0,
                'factors':          factors_per_step,
                'psi_inst_stock':   list(dc['psi_inst_stock']),
                'wall_clock':       time.time() - t0,
            }
            print(f'    seed={seed}: n={n} ({per_seed[seed]["wall_clock"]:.1f}s) '
                  f'final_pop={per_seed[seed]["final_pop"]}', flush=True)
        per_config[cname] = per_seed
    return per_config


def analyze(per_config):
    config_names = [c for c, _ in CONFIGS]

    # Per-config per-factor mean across all (seed, step)
    factor_stats = {}
    for cname in config_names:
        stats = {}
        for fkey in FACTOR_KEYS:
            vals = []
            for seed in range(N_SEEDS):
                vals.extend([f[fkey] for f in per_config[cname][seed]['factors']])
            arr = np.array(vals)
            stats[fkey] = {
                'mean':  float(arr.mean()) if arr.size else 0.0,
                'std':   float(arr.std())  if arr.size else 0.0,
                'min':   float(arr.min())  if arr.size else 0.0,
                'max':   float(arr.max())  if arr.size else 0.0,
            }
        factor_stats[cname] = stats

    # Cross-config std/mean ratio per factor
    cross_config_factor = {}
    for fkey in FACTOR_KEYS:
        means = np.array([factor_stats[c][fkey]['mean'] for c in config_names])
        m = float(means.mean())
        s = float(means.std())
        ratio = (s / abs(m)) if abs(m) > 1e-9 else 0.0
        cross_config_factor[fkey] = {
            'config_means':     dict(zip(config_names, [float(x) for x in means])),
            'mean_of_means':    m,
            'std_of_means':     s,
            'ratio':            ratio,
        }

    # Per-step matched cross-config variation: for each (seed, step), compute
    # cross-config std/mean of each factor; aggregate over (seed, step).
    per_step_variation = {}
    for fkey in FACTOR_KEYS:
        ratios = []
        for seed in range(N_SEEDS):
            n_min = min(per_config[c][seed]['n_steps'] for c in config_names)
            for t in range(n_min):
                vals = np.array([per_config[c][seed]['factors'][t][fkey] for c in config_names])
                vm = float(vals.mean())
                vs = float(vals.std())
                if abs(vm) > 1e-9:
                    ratios.append(vs / abs(vm))
                else:
                    ratios.append(0.0)
        per_step_variation[fkey] = {
            'mean_ratio':   float(np.mean(ratios)) if ratios else 0.0,
            'median_ratio': float(np.median(ratios)) if ratios else 0.0,
            'p90_ratio':    float(np.percentile(ratios, 90)) if ratios else 0.0,
            'max_ratio':    float(np.max(ratios)) if ratios else 0.0,
        }

    return {
        'factor_stats':        factor_stats,
        'cross_config_factor': cross_config_factor,
        'per_step_variation':  per_step_variation,
    }


def write_report(per_config, analysis, wall_clock, out_path):
    config_names = [c for c, _ in CONFIGS]
    lines = []
    lines.append('# Stage 1.7 U_sys factor breakdown diagnostic')
    lines.append('')
    lines.append(f'Wall-clock: {wall_clock/60:.1f} min')
    lines.append('')

    lines.append('## Factor means per configuration')
    lines.append('')
    lines.append('Average (across all seeds and steps) of each factor per config.')
    lines.append('')
    lines.append('| Factor | ' + ' | '.join(config_names) + ' | cross-config std/mean |')
    lines.append('|--------|' + '|'.join(['---'] * len(config_names)) + '|------------------------|')
    for fkey in FACTOR_KEYS:
        cells = ' | '.join(f'{analysis["factor_stats"][c][fkey]["mean"]:.4f}'
                            for c in config_names)
        ratio = analysis['cross_config_factor'][fkey]['ratio']
        flag = ' (>10%)' if ratio > 0.10 else (' (<5%)' if ratio < 0.05 else '')
        lines.append(f'| {fkey} | {cells} | {ratio:.4f}{flag} |')
    lines.append('')

    lines.append('## Per-step matched cross-config variation')
    lines.append('')
    lines.append('At each matched (seed, step), the cross-configuration std/mean '
                 'ratio of the factor is computed. Aggregated over (seed, step). '
                 'This is the within-run variation, separate from the aggregated '
                 'means in the prior table.')
    lines.append('')
    lines.append('| Factor | Mean ratio | Median ratio | p90 ratio | Max ratio |')
    lines.append('|--------|------------|---------------|-----------|-----------|')
    for fkey in FACTOR_KEYS:
        d = analysis['per_step_variation'][fkey]
        lines.append(f'| {fkey} | {d["mean_ratio"]:.4f} | {d["median_ratio"]:.4f} | '
                     f'{d["p90_ratio"]:.4f} | {d["max_ratio"]:.4f} |')
    lines.append('')

    lines.append('## Factor distribution detail')
    lines.append('')
    lines.append('Min/max across (seed, step) per config; surfaces saturation behavior.')
    lines.append('')
    lines.append('| Factor | Config | mean | std | min | max |')
    lines.append('|--------|--------|------|-----|-----|-----|')
    for fkey in FACTOR_KEYS:
        for cname in config_names:
            d = analysis['factor_stats'][cname][fkey]
            lines.append(f'| {fkey} | {cname} | {d["mean"]:.4f} | {d["std"]:.4f} | '
                         f'{d["min"]:.4f} | {d["max"]:.4f} |')
    lines.append('')

    with open(out_path, 'w') as f:
        f.write('\n'.join(lines) + '\n')


def main():
    t0 = time.time()
    per_config = collect()
    wall = time.time() - t0
    print('', flush=True)
    print('Analyzing factor variation...', flush=True)
    analysis = analyze(per_config)
    out_path = os.path.join(HERE, 'stage17_usys_factor_diagnostic_report.md')
    write_report(per_config, analysis, wall, out_path)
    print('', flush=True)
    print(f'Wall-clock: {wall/60:.1f} min', flush=True)
    print(f'Report:     {out_path}', flush=True)


if __name__ == '__main__':
    main()
