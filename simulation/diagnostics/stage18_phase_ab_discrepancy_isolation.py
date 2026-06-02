"""Isolate the two harness differences between Phase A and Phase B A_baseline.

Phase A run_one (per seed):
    cfg = { ... rr=0.066, phi=10 ... }     # no wb_min/wb_max
    m = GardenModel(n_agents=200, ...)
    # no explicit init_psi (uses PSI_INST_INITIAL = 0.5)

Phase B run_one (per seed) at A_baseline (rr=0.066, psi=0.50):
    cfg = { ... rr=0.066, phi=10, wb_min=0.50, wb_max=0.50 ... }
    m = GardenModel(n_agents=100, ...)
    m.psi_inst_stock = 0.50

Result: Phase A mean=151.6 (min 110); Phase B A_baseline mean=46.4 (min 24).
Both share seeds 0..4 and PSI_INST_INITIAL = init_psi = 0.50.

Two suspect differences:
  (a) n_agents: 200 (Phase A) vs 100 (Phase B)
  (b) initial wb: default uniform [0.5, 0.8] (Phase A) vs uniform [0.50, 0.50]
      (Phase B)

Controls run here (all rr=0.066, init_psi=0.50, phi=10.0, seeds 0..4, 100 steps):
  C1   n_agents=200, wb defaults                # Phase A baseline (reproduce)
  C2a  n_agents=200, wb_min=wb_max=0.50         # isolate wb tightening
  C2b  n_agents=100, wb defaults                # isolate n_agents halving
  C2c  n_agents=100, wb_min=wb_max=0.50         # Phase B A_baseline (reproduce)
"""

import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SIM_DIR = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, SIM_DIR)

from model import GardenModel

N_SEEDS = 5
N_STEPS = 100

CONTROLS = [
    ('C1_PhaseA_repro',     {'n_agents': 200, 'wb_pin': False}),
    ('C2a_n200_wb_pinned',  {'n_agents': 200, 'wb_pin': True}),
    ('C2b_n100_wb_default', {'n_agents': 100, 'wb_pin': False}),
    ('C2c_PhaseB_repro',    {'n_agents': 100, 'wb_pin': True}),
]


def run_one(n_agents, wb_pin, seed):
    cfg = {
        'policy':            'optimize_u_sys_v2',
        'phi':               10.0,
        'reproduction_rate': 0.066,
        'rollout_steps_v2':  20,
        'n_candidates_v2':   300,
        'random_seed':       seed,
    }
    if wb_pin:
        cfg['wb_min'] = 0.50
        cfg['wb_max'] = 0.50
    m = GardenModel(n_agents=n_agents, ai_policy='optimize_u_sys_v2', config=cfg)
    m.psi_inst_stock = 0.50
    m.previous_psi_inst_stock = 0.50
    extinct_at = None
    for s in range(N_STEPS):
        if not m.step():
            extinct_at = s + 1
            break
    dc = m.datacollector
    return int(dc['population'][-1]) if dc['population'] else 0, extinct_at


def main():
    print('Phase A / Phase B A_baseline isolation', flush=True)
    print(f'  seeds: {N_SEEDS}, steps: {N_STEPS}, rr=0.066, init_psi=0.50, phi=10.0',
          flush=True)
    print('', flush=True)
    results = {}
    for label, params in CONTROLS:
        print(f'  {label} (n_agents={params["n_agents"]}, wb_pin={params["wb_pin"]}):',
              flush=True)
        finals = []
        for seed in range(N_SEEDS):
            t0 = time.time()
            pop, extinct = run_one(params['n_agents'], params['wb_pin'], seed)
            finals.append(pop)
            note = f' EXTINCT at step {extinct}' if extinct else ''
            print(f'    seed={seed}: {time.time()-t0:.1f}s, final pop={pop}{note}',
                  flush=True)
        results[label] = finals
        print(f'    -> mean={np.mean(finals):.1f}, min={min(finals)}, '
              f'max={max(finals)}', flush=True)
        print('', flush=True)

    print('Summary:', flush=True)
    print(f'{"Control":<24} {"finals":<35} {"mean":>6} {"min":>4} {"max":>4}',
          flush=True)
    print('-' * 80, flush=True)
    for label, _ in CONTROLS:
        finals = results[label]
        print(f'{label:<24} {str(finals):<35} '
              f'{np.mean(finals):>6.1f} {min(finals):>4} {max(finals):>4}',
              flush=True)


if __name__ == '__main__':
    main()
