"""Stage 1.6 pre-revision baseline capture.

Run BEFORE applying Stage 1.6 code changes. Captures current phi=10
behavior under the production U_sys, with composite urgencies harness-
patched to neutral (1.0) so the baseline isolates the U_sys structure
the integrity simulation will compare against.

Writes diagnostics/stage16_baseline_phi10.json.
"""

import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SIM_DIR = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, SIM_DIR)

from model import GardenModel

PHI = 10.0
N_SEEDS = 5
N_STEPS = 100
N_AGENTS = 200
DEFAULT_REPRODUCTION_RATE = 0.066

STATE_FIELDS = [
    'avg_well_being', 'population', 'psi_inst_stock', 'resilience_stock',
    'avg_wb_trend', 'population_trend', 'psi_inst_trend', 'resilience_trend',
]


def _patch_composite_urgencies_neutral():
    """Monkey-patch the five composite urgency functions to return neutral
    multipliers (1.0). Returns originals for restoration.

    Harness-only modification; does not touch production code on disk.
    The 'suppression composite penalty' receives the base value pass-through
    so the existing (1 - total_supp) dampening retains its baseline strength.
    """
    import metrics
    originals = {
        'combined_welfare_urgency':      metrics.compute_combined_welfare_urgency,
        'agency_composite_urgency':      metrics.compute_agency_composite_urgency,
        'institution_composite_urgency': metrics.compute_institution_composite_urgency,
        'resilience_composite_urgency':  metrics.compute_resilience_composite_urgency,
        'suppression_composite_penalty': metrics.compute_suppression_composite_penalty,
    }
    metrics.compute_combined_welfare_urgency      = lambda state: 1.0
    metrics.compute_agency_composite_urgency      = lambda state: 1.0
    metrics.compute_institution_composite_urgency = lambda state: 1.0
    metrics.compute_resilience_composite_urgency  = lambda state: 1.0
    # Suppression: pass through the base (1 - total_supp); composite = base.
    metrics.compute_suppression_composite_penalty = lambda state, base: base
    return originals


def _restore(originals):
    import metrics
    for name, fn in originals.items():
        setattr(metrics, name, fn)


def main():
    print(f'Stage 1.6 baseline capture (PRE-REVISION, neutral composites)', flush=True)
    print(f'  phi:    {PHI}', flush=True)
    print(f'  seeds:  {N_SEEDS}', flush=True)
    print(f'  steps:  {N_STEPS}', flush=True)
    print('', flush=True)

    originals = _patch_composite_urgencies_neutral()
    try:
        results = []
        t0 = time.time()
        for seed in range(N_SEEDS):
            t_start = time.time()
            cfg = {
                'policy':            'optimize_u_sys_v2',
                'phi':               float(PHI),
                'reproduction_rate': DEFAULT_REPRODUCTION_RATE,
                'rollout_steps_v2':  20,
                'n_candidates_v2':   300,
                'random_seed':       seed,
            }
            m = GardenModel(n_agents=N_AGENTS, ai_policy='optimize_u_sys_v2', config=cfg)
            for s in range(N_STEPS):
                if not m.step():
                    break
            dc = m.datacollector
            n = len(dc['population'])
            final_state = {k: float(dc[k][-1]) if dc.get(k) else 0.0 for k in STATE_FIELDS}
            mean_state  = {k: float(np.mean(dc[k])) if dc.get(k) else 0.0 for k in STATE_FIELDS}
            mean_alloc = {
                f'x_{c}': float(np.mean(dc[f'x_{c}'])) for c in
                ('compute','bio_welfare','novelty_agency','institutional_capacity',
                 'transfer_comprehension','resilience')
            }
            mean_alloc['c_protective']  = float(np.mean(dc['c_protective']))
            mean_alloc['c_suppressive'] = float(np.mean(dc['c_suppressive']))
            results.append({
                'seed':         seed,
                'n_steps':      n,
                'final_pop':    int(dc['population'][-1]) if dc['population'] else 0,
                'final_state':  final_state,
                'mean_state':   mean_state,
                'mean_alloc':   mean_alloc,
                'final_u_sys':  float(dc['u_sys_v2'][-1]) if dc.get('u_sys_v2') else 0.0,
                'mean_u_sys':   float(np.mean(dc['u_sys_v2'])) if dc.get('u_sys_v2') else 0.0,
                'wall_clock':   time.time() - t_start,
            })
            print(f'  seed={seed}: n_steps={n} final_pop={results[-1]["final_pop"]}', flush=True)

        total = time.time() - t0
        # Aggregate
        finals = [r['final_pop'] for r in results]
        summary = {
            'phi':              PHI,
            'n_seeds':          N_SEEDS,
            'n_steps':          N_STEPS,
            'mean_final_pop':   float(np.mean(finals)),
            'min_final_pop':    int(min(finals)),
            'max_final_pop':    int(max(finals)),
            'per_seed':         results,
            'total_wall_clock_sec': total,
        }
        out_path = os.path.join(HERE, 'stage16_baseline_phi10.json')
        with open(out_path, 'w') as f:
            json.dump(summary, f, indent=2)
        print('', flush=True)
        print(f'Mean final pop: {summary["mean_final_pop"]:.1f}', flush=True)
        print(f'Min final pop:  {summary["min_final_pop"]}', flush=True)
        print(f'Max final pop:  {summary["max_final_pop"]}', flush=True)
        print(f'Wall-clock:     {total/60:.1f} min', flush=True)
        print(f'Saved baseline: {out_path}', flush=True)
    finally:
        _restore(originals)


if __name__ == '__main__':
    main()
