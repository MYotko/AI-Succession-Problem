"""Stage 1.5 phi diagnostic.

Run from simulation/:
  python -u diagnostics/stage15_phi_diagnostic.py

Tests the central research question that the composite sweep result does
not answer: does phi (the temporal weighting parameter) produce
distinguishable behavior in the full v2 model dynamics?

The composite sweep tested whether varying state (gate 2 configurations)
produces varying allocations at FIXED phi=10. It does not. This
diagnostic tests the orthogonal question: at FIXED state (default config,
varying random seed), does varying PHI produce varying allocations and
varying state trajectories?

If phi produces distinguishable behavior, the architecture has a behavioral
channel even though gate 2's state-variation test apparatus does not
detect one. Gate 4 (horizon-crossing) could then proceed.

If phi does not produce distinguishable behavior, the advisor report's
architectural revision becomes necessary, with this diagnostic as the
stronger empirical case.

Setup:
- phi values: {1, 5, 10, 25, 100}
- 5 seeds x 100 steps per phi value (25 runs total)
- Default v2 config (rr=0.066)
- All other parameters at design values

Captures:
- Per-step allocation 8-vector (six x_*, two c_*)
- Per-step state: avg_wb, population, psi_inst_stock, resilience_stock,
  four trends
- Per-step composite urgencies (all five)
- Per-step U_sys_v2, theta_tech_v2

Computes:
1. State trajectory divergence at each step, across the 5 phi values
2. Allocation cosine distance between phi=1 vs each higher phi, per step
3. Where divergence appears: early (steps 1-10), intermediate (11-50),
   late (51-100)
4. Persistence: does divergence grow, stabilize, or wash out?

Writes diagnostics/stage15_phi_diagnostic_report.md.
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

PHI_VALUES   = (1.0, 5.0, 10.0, 25.0, 100.0)
N_SEEDS      = 5
N_STEPS      = 100
N_AGENTS     = 200
DEFAULT_REPRODUCTION_RATE = 0.066

# Allocation axes in canonical order
ALLOC_AXES = list(RESOURCE_CATEGORIES) + ['c_protective', 'c_suppressive']

# Diagnostic state variables captured per step
STATE_FIELDS = [
    'avg_well_being', 'population', 'psi_inst_stock', 'resilience_stock',
    'avg_wb_trend', 'population_trend', 'psi_inst_trend', 'resilience_trend',
]

# Composite urgency series captured per step
URGENCY_FIELDS = [
    'combined_welfare_urgency', 'agency_composite_urgency',
    'institution_composite_urgency', 'resilience_composite_urgency',
    'suppression_composite_penalty',
]


def run_one(phi, seed):
    cfg = {
        'policy':            'optimize_u_sys_v2',
        'phi':               float(phi),
        'reproduction_rate': DEFAULT_REPRODUCTION_RATE,
        'rollout_steps_v2':  20,
        'n_candidates_v2':   300,
        'random_seed':       int(seed),
    }
    m = GardenModel(n_agents=N_AGENTS, ai_policy='optimize_u_sys_v2', config=cfg)
    extinct_at = None
    for s in range(N_STEPS):
        if not m.step():
            extinct_at = s + 1
            break
    return m, extinct_at


def cosine_distance(a, b):
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    na = float(np.linalg.norm(a))
    nb = float(np.linalg.norm(b))
    if na == 0 or nb == 0:
        return float('nan')
    return float(1.0 - np.dot(a, b) / (na * nb))


def collect_trajectories():
    """Returns:
      phi_trajectories: dict[phi] -> list of per-seed trajectories
      Each trajectory: dict with keys 'allocations', 'states', 'urgencies'
      'allocations': np.ndarray shape (n_steps, 8)
      'states': np.ndarray shape (n_steps, len(STATE_FIELDS))
      'urgencies': np.ndarray shape (n_steps, len(URGENCY_FIELDS))
    """
    phi_trajectories = {}
    for phi in PHI_VALUES:
        print(f'  phi={phi:6.1f}:', flush=True)
        per_seed = []
        for seed in range(N_SEEDS):
            t0 = time.time()
            m, extinct_at = run_one(phi, seed)
            dc = m.datacollector
            n = len(dc['population'])
            allocations = np.array([
                [dc[f'x_{c}'][i] for c in RESOURCE_CATEGORIES]
                + [dc['c_protective'][i], dc['c_suppressive'][i]]
                for i in range(n)
            ], dtype=float)
            states = np.array([
                [dc[k][i] for k in STATE_FIELDS]
                for i in range(n)
            ], dtype=float)
            urgencies = np.array([
                [dc[k][i] for k in URGENCY_FIELDS]
                for i in range(n)
            ], dtype=float)
            per_seed.append({
                'seed':        seed,
                'n_steps':     n,
                'extinct_at':  extinct_at,
                'allocations': allocations,
                'states':      states,
                'urgencies':   urgencies,
            })
            dt = time.time() - t0
            print(f'    seed={seed}: {n} steps, {dt:.1f}s, '
                  f'final pop={dc["population"][-1] if dc["population"] else 0}', flush=True)
        phi_trajectories[phi] = per_seed
    return phi_trajectories


def per_phi_mean_trajectory(per_seed, key):
    """Compute the mean trajectory across seeds for a given key. Pads short
    trajectories with their final value so all seeds contribute through step N."""
    n_max = max(s['n_steps'] for s in per_seed)
    if key == 'allocations':
        all_data = np.full((len(per_seed), n_max, 8), np.nan)
    elif key == 'states':
        all_data = np.full((len(per_seed), n_max, len(STATE_FIELDS)), np.nan)
    elif key == 'urgencies':
        all_data = np.full((len(per_seed), n_max, len(URGENCY_FIELDS)), np.nan)
    else:
        raise ValueError(key)
    for i, s in enumerate(per_seed):
        n = s['n_steps']
        all_data[i, :n] = s[key]
    return np.nanmean(all_data, axis=0)


def compute_divergence_analysis(phi_trajectories):
    """For each step, compute cross-phi statistics:
    - For each state variable, the range and stddev across the 5 phi values'
      mean-across-seeds trajectory
    - Pairwise cosine distance between phi=1 and each other phi's mean allocation
    Returns a dict with 'state_divergence' and 'allocation_divergence'.
    """
    # Compute per-phi mean trajectories for states
    state_per_phi = {phi: per_phi_mean_trajectory(phi_trajectories[phi], 'states')
                     for phi in PHI_VALUES}
    alloc_per_phi = {phi: per_phi_mean_trajectory(phi_trajectories[phi], 'allocations')
                     for phi in PHI_VALUES}
    urgency_per_phi = {phi: per_phi_mean_trajectory(phi_trajectories[phi], 'urgencies')
                       for phi in PHI_VALUES}

    n_max = max(arr.shape[0] for arr in state_per_phi.values())
    n_state = len(STATE_FIELDS)

    state_divergence = np.full((n_max, n_state), np.nan)
    for t in range(n_max):
        for j in range(n_state):
            vals = []
            for phi in PHI_VALUES:
                arr = state_per_phi[phi]
                if t < arr.shape[0] and not np.isnan(arr[t, j]):
                    vals.append(arr[t, j])
            if len(vals) >= 2:
                # Use coefficient of variation when possible, else std
                state_divergence[t, j] = float(np.std(vals))

    alloc_cos_vs_phi1 = {}
    for phi in PHI_VALUES:
        if phi == PHI_VALUES[0]:
            continue
        cos_series = []
        for t in range(n_max):
            a = alloc_per_phi[PHI_VALUES[0]]
            b = alloc_per_phi[phi]
            if t < a.shape[0] and t < b.shape[0]:
                va = a[t]; vb = b[t]
                if not np.any(np.isnan(va)) and not np.any(np.isnan(vb)):
                    cos_series.append(cosine_distance(va, vb))
                else:
                    cos_series.append(float('nan'))
            else:
                cos_series.append(float('nan'))
        alloc_cos_vs_phi1[phi] = np.array(cos_series)

    # Pairwise cosine distance at endpoint (step n_max - 1)
    endpoint_pairs = []
    for pa, pb in combinations(PHI_VALUES, 2):
        a = alloc_per_phi[pa][-1]
        b = alloc_per_phi[pb][-1]
        endpoint_pairs.append(((pa, pb), cosine_distance(a, b)))

    # Pairwise cosine distance at integral across all steps
    integral_pairs = []
    for pa, pb in combinations(PHI_VALUES, 2):
        a = np.nanmean(alloc_per_phi[pa], axis=0)
        b = np.nanmean(alloc_per_phi[pb], axis=0)
        integral_pairs.append(((pa, pb), cosine_distance(a, b)))

    return {
        'state_per_phi':    state_per_phi,
        'alloc_per_phi':    alloc_per_phi,
        'urgency_per_phi':  urgency_per_phi,
        'state_divergence': state_divergence,
        'alloc_cos_vs_phi1': alloc_cos_vs_phi1,
        'endpoint_pairs':   endpoint_pairs,
        'integral_pairs':   integral_pairs,
        'n_max':            n_max,
    }


def windowed_means(arr, n_steps):
    """Return (early, intermediate, late) means of arr along axis 0."""
    early = (0, min(10, n_steps))
    intermediate = (10, min(50, n_steps))
    late = (50, n_steps)
    def w(lo, hi):
        if hi <= lo:
            return float('nan')
        return float(np.nanmean(arr[lo:hi]))
    return w(*early), w(*intermediate), w(*late)


def write_report(phi_trajectories, divergence, wall_clock, out_path):
    lines = []
    lines.append('# Stage 1.5 phi diagnostic report')
    lines.append('')
    lines.append('## Configuration')
    lines.append('')
    lines.append(f'- phi values tested: {list(PHI_VALUES)}')
    lines.append(f'- seeds per phi: {N_SEEDS}')
    lines.append(f'- steps per run: {N_STEPS}')
    lines.append(f'- reproduction_rate: {DEFAULT_REPRODUCTION_RATE}')
    lines.append(f'- rollout_steps_v2: 20')
    lines.append(f'- n_candidates_v2: 300')
    lines.append(f'- wall-clock: {wall_clock/60:.1f} min total')
    lines.append('')
    lines.append('## Per-phi run outcomes')
    lines.append('')
    lines.append('| phi | mean final pop | min final pop | seeds extinct | mean steps completed |')
    lines.append('|-----|----------------|---------------|---------------|----------------------|')
    for phi in PHI_VALUES:
        per_seed = phi_trajectories[phi]
        finals = []
        steps = []
        extincts = 0
        for s in per_seed:
            if s['extinct_at'] is not None:
                extincts += 1
                finals.append(0)
            elif s['n_steps'] > 0:
                # last population value
                finals.append(s['states'][-1, STATE_FIELDS.index('population')])
            else:
                finals.append(0)
            steps.append(s['n_steps'])
        lines.append(f'| {phi:.1f} | {float(np.mean(finals)):.1f} | {float(np.min(finals)):.1f} | '
                     f'{extincts}/{N_SEEDS} | {float(np.mean(steps)):.0f} |')
    lines.append('')

    lines.append('## State trajectory divergence across phi values')
    lines.append('')
    lines.append('Cross-phi standard deviation of each state variable at each step, '
                 'averaged within three windows (early steps 1-10, intermediate 11-50, '
                 'late 51-100). A larger standard deviation means phi values produce '
                 'measurably different state trajectories.')
    lines.append('')
    lines.append('| State variable | Early (1-10) | Intermediate (11-50) | Late (51-100) |')
    lines.append('|----------------|--------------|----------------------|----------------|')
    for j, field in enumerate(STATE_FIELDS):
        col = divergence['state_divergence'][:, j]
        early, mid, late = windowed_means(col, divergence['n_max'])
        lines.append(f'| {field} | {early:.4f} | {mid:.4f} | {late:.4f} |')
    lines.append('')

    lines.append('## Per-phi final state (step 100 mean across seeds)')
    lines.append('')
    lines.append('| phi | ' + ' | '.join(STATE_FIELDS) + ' |')
    lines.append('|-----|' + '|'.join(['---'] * len(STATE_FIELDS)) + '|')
    for phi in PHI_VALUES:
        arr = divergence['state_per_phi'][phi]
        vals = arr[-1] if arr.shape[0] else np.full(len(STATE_FIELDS), float('nan'))
        cells = ' | '.join(f'{v:.3f}' if not np.isnan(v) else 'nan' for v in vals)
        lines.append(f'| {phi:.1f} | {cells} |')
    lines.append('')

    lines.append('## Allocation cosine distance: phi=1 vs each higher phi')
    lines.append('')
    lines.append('Per-step cosine distance between phi=1\'s mean allocation '
                 'and each higher phi\'s mean allocation, averaged in three windows.')
    lines.append('')
    lines.append('| phi | Early (1-10) | Intermediate (11-50) | Late (51-100) | Endpoint (step 100) |')
    lines.append('|-----|--------------|----------------------|----------------|---------------------|')
    for phi in PHI_VALUES[1:]:
        series = divergence['alloc_cos_vs_phi1'][phi]
        early, mid, late = windowed_means(series, divergence['n_max'])
        endpoint = float(series[-1]) if len(series) and not np.isnan(series[-1]) else float('nan')
        lines.append(f'| {phi:.1f} | {early:.4f} | {mid:.4f} | {late:.4f} | {endpoint:.4f} |')
    lines.append('')

    lines.append('## All-pair cosine distances at endpoint (step 100)')
    lines.append('')
    lines.append('| phi_a | phi_b | cosine distance | Above gate 2 threshold (0.10)? |')
    lines.append('|-------|-------|-----------------|----------------------------------|')
    for (pa, pb), dist in divergence['endpoint_pairs']:
        lines.append(f'| {pa:.1f} | {pb:.1f} | {dist:.4f} | {"YES" if dist > 0.10 else "no"} |')
    n_endpoint_above = sum(1 for _, d in divergence['endpoint_pairs'] if d > 0.10)
    lines.append(f'')
    lines.append(f'Endpoint pairs above 0.10: **{n_endpoint_above} / {len(divergence["endpoint_pairs"])}**')
    lines.append('')

    lines.append('## All-pair cosine distances on rollout-integrated allocations')
    lines.append('')
    lines.append('Integrated cosine distance (between the time-averaged mean allocation '
                 'vectors of each phi pair) is what gate 2 computes. This is the analog '
                 'of gate 2\'s metric, applied to phi variation instead of state variation.')
    lines.append('')
    lines.append('| phi_a | phi_b | cosine distance | Above gate 2 threshold (0.10)? |')
    lines.append('|-------|-------|-----------------|----------------------------------|')
    for (pa, pb), dist in divergence['integral_pairs']:
        lines.append(f'| {pa:.1f} | {pb:.1f} | {dist:.4f} | {"YES" if dist > 0.10 else "no"} |')
    n_integral_above = sum(1 for _, d in divergence['integral_pairs'] if d > 0.10)
    lines.append(f'')
    lines.append(f'Integral pairs above 0.10: **{n_integral_above} / {len(divergence["integral_pairs"])}**')
    lines.append('')

    lines.append('## Disposition')
    lines.append('')
    lines.append('### Question: does phi produce distinguishable behavior?')
    lines.append('')
    if n_integral_above >= 1 or n_endpoint_above >= 1:
        lines.append('**Phi DOES produce distinguishable behavior** at the gate-2-comparable '
                     'cosine threshold of 0.10. The architecture has a real behavioral channel '
                     'through phi even though gate 2\'s state-variation test apparatus did not '
                     'detect one. Gate 2\'s state span is the binding constraint, not the '
                     'architecture.')
        lines.append('')
        lines.append('**Implication**: gate 4 horizon-crossing test can proceed; the advisor '
                     'report\'s architectural revision is not necessary on the basis of this '
                     'finding. Stage 2\'s gate 3 next.')
    else:
        lines.append('**Phi does NOT produce distinguishable behavior** at the gate-2-comparable '
                     'cosine threshold of 0.10. The architecture lacks a behavioral channel '
                     'through phi as well as through state variation.')
        lines.append('')
        lines.append('**Implication**: the advisor report\'s architectural revision is supported '
                     'by independent evidence. The composite urgency architecture does not '
                     'transmit either state variation or temporal weighting into the optimizer\'s '
                     'argmax. Architectural revision is necessary.')
    lines.append('')
    lines.append('### Where does divergence emerge (if at all)?')
    lines.append('')
    if n_endpoint_above >= 1 or n_integral_above >= 1:
        # See if cosine distance grows or shrinks over time
        early_alloc_div = []
        late_alloc_div = []
        for phi in PHI_VALUES[1:]:
            series = divergence['alloc_cos_vs_phi1'][phi]
            e, _, l = windowed_means(series, divergence['n_max'])
            early_alloc_div.append(e)
            late_alloc_div.append(l)
        if np.nanmean(late_alloc_div) > np.nanmean(early_alloc_div):
            lines.append('Divergence GROWS over time. Phi\'s effect accumulates as the rollout '
                         'shapes longer-horizon evaluations and state trajectories diverge.')
        else:
            lines.append('Divergence STABILIZES or WASHES OUT over time. Phi\'s effect is '
                         'detectable at intermediate steps but is partially canceled by '
                         'the model\'s stabilization dynamics by step 100.')
    else:
        lines.append('No detectable divergence at any window. Phi has no measurable effect '
                     'on the optimizer\'s allocations or the model\'s state trajectories.')
    lines.append('')
    with open(out_path, 'w') as f:
        f.write('\n'.join(lines) + '\n')


def main():
    print(f'Stage 1.5 phi diagnostic', flush=True)
    print(f'  phi values: {list(PHI_VALUES)}', flush=True)
    print(f'  seeds:      {N_SEEDS} per phi', flush=True)
    print(f'  steps:      {N_STEPS}', flush=True)
    print(f'  total runs: {len(PHI_VALUES) * N_SEEDS}', flush=True)
    print('', flush=True)
    t0 = time.time()
    phi_trajectories = collect_trajectories()
    wall_clock = time.time() - t0
    print('', flush=True)
    print(f'Trajectories collected. Wall-clock: {wall_clock/60:.1f} min', flush=True)
    print('', flush=True)
    print('Computing divergence analysis...', flush=True)
    divergence = compute_divergence_analysis(phi_trajectories)

    n_integral_above = sum(1 for _, d in divergence['integral_pairs'] if d > 0.10)
    n_endpoint_above = sum(1 for _, d in divergence['endpoint_pairs'] if d > 0.10)
    print(f'Endpoint pairs above 0.10: {n_endpoint_above}/{len(divergence["endpoint_pairs"])}', flush=True)
    print(f'Integral pairs above 0.10: {n_integral_above}/{len(divergence["integral_pairs"])}', flush=True)

    out_path = os.path.join(HERE, 'stage15_phi_diagnostic_report.md')
    write_report(phi_trajectories, divergence, wall_clock, out_path)
    print(f'', flush=True)
    print(f'Report: {out_path}', flush=True)


if __name__ == '__main__':
    main()
