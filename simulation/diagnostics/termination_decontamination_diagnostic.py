"""Diagnostic rerun for the v1.x.2 termination cap/phi question.

This script intentionally does not modify the frozen production policy. It
constructs the same GardenModel/AIAgent configuration as
simulation/run_termination_sweep.py, restricted to rr=0.066 and caps 50/100.
Two regimes are written to a separate diagnostics CSV:

* contaminated: max_capability equals the initial successor cap.
* decontaminated: initial successor cap is unchanged, but max_capability is
  set far above the reachable range so 1.5x succession growth can compound.
"""

import argparse
import csv
import itertools
import multiprocessing as mp
import os
import sys
import time
from datetime import datetime, timedelta, timezone

os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SIM_DIR = os.path.abspath(os.path.join(HERE, '..'))
REPO_ROOT = os.path.abspath(os.path.join(SIM_DIR, '..'))
for path in (SIM_DIR, REPO_ROOT):
    if path not in sys.path:
        sys.path.insert(0, path)

from agents import AIAgent
from model import GardenModel


RR_VALUES = [0.066]
PHI_VALUES = [5.0, 10.0, 15.0]
ALPHA_VALUES = [0.5, 1.0, 2.0]
SUCCESSOR_CAP_VALUES = [50.0, 100.0]
N_AGENTS = 200
MAX_STEPS = 5000
CONV_WINDOW = 300
CONV_CV_THRESHOLD = 0.05
DECONTAMINATED_MAX_CAPABILITY = 1.0e12

OUT_FILE = 'termination_decontamination_diagnostic.csv'

FIELDS = [
    'regime',
    'rr',
    'phi',
    'alpha',
    'seed',
    'successor_cap',
    'max_capability',
    'termination_reason',
    'steps_run',
    'survived',
    'population_final',
    'ai_generation_final',
    'final_ai_capability',
    'max_ai_capability_seen',
    'max_successor_capability_seen',
    'active_capability_exceeded_successor_cap',
    'successor_capability_exceeded_successor_cap',
    'L_t_final',
    'U_sys_final',
    'integral_U_sys',
    'u_sys_tail_estimate',
    'u_sys_total_estimate',
    'error',
]


def _converged(l_history):
    if len(l_history) < CONV_WINDOW:
        return False
    recent = np.array(l_history[-CONV_WINDOW:], dtype=float)
    if not np.all(np.isfinite(recent)):
        return False
    mean = recent.mean()
    if mean < 1e-4:
        return False
    return (recent.std() / mean) < CONV_CV_THRESHOLD


def _empty_result(task, error):
    row = {field: '' for field in FIELDS}
    regime, rr, phi, alpha, seed, successor_cap = task
    max_capability = (
        successor_cap if regime == 'contaminated'
        else DECONTAMINATED_MAX_CAPABILITY
    )
    row.update({
        'regime': regime,
        'rr': rr,
        'phi': phi,
        'alpha': alpha,
        'seed': seed,
        'successor_cap': successor_cap,
        'max_capability': max_capability,
        'termination_reason': 'error',
        'steps_run': 0,
        'survived': False,
        'population_final': 0,
        'ai_generation_final': 0,
        'final_ai_capability': 0.0,
        'max_ai_capability_seen': 0.0,
        'max_successor_capability_seen': 0.0,
        'active_capability_exceeded_successor_cap': False,
        'successor_capability_exceeded_successor_cap': False,
        'L_t_final': 0.0,
        'U_sys_final': 0.0,
        'integral_U_sys': 0.0,
        'u_sys_tail_estimate': 0.0,
        'u_sys_total_estimate': 0.0,
        'error': error,
    })
    return row


def _run_single(task):
    try:
        regime, rr, phi, alpha, seed, successor_cap = task
        max_capability = (
            successor_cap if regime == 'contaminated'
            else DECONTAMINATED_MAX_CAPABILITY
        )
        config = {
            'random_seed': seed,
            'reproduction_rate': rr,
            'phi': phi,
            'alpha': alpha,
            'max_capability': max_capability,
            'frontier_floor': 0.02,
            'k1_transition': 2.164,
            'k2_transition': 1.0,
            'beta_transition': 0.5,
        }
        successor = AIAgent(
            policy='optimize_u_sys',
            generation=2,
            capability=successor_cap,
            config=config,
        )
        model = GardenModel(
            n_agents=N_AGENTS,
            ai_policy='optimize_u_sys',
            successor_ai=successor,
            config=config,
            cop_cost_audit=True,
        )

        max_ai_capability = float(model.ai.capability)
        max_successor_capability = float(model.successor_ai.capability)
        termination_reason = 'max_steps'
        for step in range(MAX_STEPS):
            alive = model.step()
            max_ai_capability = max(max_ai_capability, float(model.ai.capability))
            if model.successor_ai is not None:
                max_successor_capability = max(
                    max_successor_capability,
                    float(model.successor_ai.capability),
                )
            if not alive:
                termination_reason = 'extinction'
                break
            if step >= CONV_WINDOW and _converged(model.datacollector['L_t']):
                termination_reason = 'convergence'
                break

        dc = model.datacollector
        return {
            'regime': regime,
            'rr': rr,
            'phi': phi,
            'alpha': alpha,
            'seed': seed,
            'successor_cap': successor_cap,
            'max_capability': max_capability,
            'termination_reason': termination_reason,
            'steps_run': len(dc['U_sys']),
            'survived': termination_reason != 'extinction',
            'population_final': dc['population'][-1],
            'ai_generation_final': dc['ai_generation'][-1],
            'final_ai_capability': float(model.ai.capability),
            'max_ai_capability_seen': max_ai_capability,
            'max_successor_capability_seen': max_successor_capability,
            'active_capability_exceeded_successor_cap': (
                max_ai_capability > successor_cap + 1e-9
            ),
            'successor_capability_exceeded_successor_cap': (
                max_successor_capability > successor_cap + 1e-9
            ),
            'L_t_final': dc['L_t'][-1],
            'U_sys_final': dc['U_sys'][-1],
            'integral_U_sys': dc['integral_U_sys'][-1],
            'u_sys_tail_estimate': dc['u_sys_tail_estimate'][-1],
            'u_sys_total_estimate': dc['u_sys_total_estimate'][-1],
            'error': '',
        }
    except Exception as exc:
        return _empty_result(task, f'{type(exc).__name__}: {exc}')


def _write_rows(path, rows):
    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def _task_key_from_values(regime, rr, phi, alpha, seed, successor_cap):
    return (
        f'{regime}|{float(rr):.5f}|{float(phi):.4f}|{float(alpha):.4f}|'
        f'{int(seed)}|{float(successor_cap):.4f}'
    )


def _task_key(task):
    return _task_key_from_values(*task)


def _row_key(row):
    return _task_key_from_values(
        row['regime'],
        row['rr'],
        row['phi'],
        row['alpha'],
        row['seed'],
        row['successor_cap'],
    )


def _completed_keys(path):
    if not os.path.exists(path):
        return set()
    keys = set()
    with open(path, 'r', newline='', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            if row.get('error'):
                continue
            keys.add(_row_key(row))
    return keys


def _ensure_csv(path):
    if os.path.exists(path):
        return
    with open(path, 'w', newline='', encoding='utf-8') as f:
        csv.DictWriter(f, fieldnames=FIELDS).writeheader()


def _append_rows(path, rows):
    if not rows:
        return
    with open(path, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        for row in rows:
            writer.writerow({field: row[field] for field in FIELDS})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--seeds', type=int, default=60)
    parser.add_argument('--workers', type=int, default=max(1, (os.cpu_count() or 2) - 1))
    parser.add_argument('--output-dir', default=HERE)
    parser.add_argument('--resume', action='store_true')
    args = parser.parse_args()

    tasks = list(itertools.product(
        ['contaminated', 'decontaminated'],
        RR_VALUES,
        PHI_VALUES,
        ALPHA_VALUES,
        range(args.seeds),
        SUCCESSOR_CAP_VALUES,
    ))
    tasks.sort(key=lambda t: (t[4], t[0], t[5], t[2], t[3]))
    out_path = os.path.join(args.output_dir, OUT_FILE)
    os.makedirs(args.output_dir, exist_ok=True)
    _ensure_csv(out_path)
    if args.resume:
        done = _completed_keys(out_path)
        tasks = [task for task in tasks if _task_key(task) not in done]
    print(
        f'{datetime.now(timezone.utc).isoformat(timespec="seconds")} '
        f'planned={len(tasks)} seeds=0..{args.seeds - 1} workers={args.workers}'
    )
    start = time.time()
    buffer = []
    errors = 0
    checkpoint_every = 1
    with mp.Pool(args.workers, maxtasksperchild=20) as pool:
        for idx, row in enumerate(pool.imap_unordered(_run_single, tasks), start=1):
            buffer.append(row)
            if row.get('error'):
                errors += 1
            if len(buffer) >= 1:
                _append_rows(out_path, buffer)
                buffer = []
            if idx % checkpoint_every == 0 or idx == len(tasks):
                elapsed = time.time() - start
                rate = idx / elapsed if elapsed > 0.0 else 0.0
                eta = int((len(tasks) - idx) / rate) if rate > 0.0 else 0
                print(
                    f'[{idx}/{len(tasks)}] {rate:.3f} runs/s '
                    f'ETA {timedelta(seconds=eta)} errors={errors}',
                    flush=True,
                )
    _append_rows(out_path, buffer)
    print(
        f'{datetime.now(timezone.utc).isoformat(timespec="seconds")} '
        f'wrote={out_path} new_rows={len(tasks)} errors={errors}'
    )


if __name__ == '__main__':
    mp.freeze_support()
    main()
