"""Dense corner diagnostic for patient-defection sweep 3.

The production patient-defection helper is reused directly. This wrapper only
changes the grid and sample size, keeping the sweep-3 defection setup intact.
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

HERE = os.path.dirname(os.path.abspath(__file__))
SIM_DIR = os.path.abspath(os.path.join(HERE, '..'))
REPO_ROOT = os.path.abspath(os.path.join(SIM_DIR, '..'))
for path in (HERE, SIM_DIR, REPO_ROOT):
    if path not in sys.path:
        sys.path.insert(0, path)

from patient_defection_sweeps import (
    BASE_RR,
    BASE_SUCCESSOR_CAPABILITY,
    CSV_FIELDS,
    PHI_DEFAULT,
    deterministic_seed,
    run_single,
)


OUT_FILE = 'patient_defection_corner_density.csv'
ALPHA_VALUES = [0.40, 0.50, 0.60]
ALPHA_VALUES = [0.40]
GROWTH_VALUES = [1.25, 1.40, 1.50, 1.60, 1.75]

SWEEP3_FIXED = {
    'sweep': '3-corner-density',
    'rr': BASE_RR,
    'phi': PHI_DEFAULT,
    'successor_capability': BASE_SUCCESSOR_CAPABILITY,
    'defection_weight': 0.5,
    'defection_target': 'H_C_inflated',
    'inheritance_mode': 'lineage',
    'max_generations': 4,
    'n_steps': 500,
    'rollout_steps': 20,
    'n_candidates': 300,
}


def build_tasks(seeds):
    tasks = []
    for alpha, growth, seed in itertools.product(
            ALPHA_VALUES, GROWTH_VALUES, range(seeds)):
        label = (
            f'patient_defection|3-corner-density|0.5|H_C_inflated|'
            f'{alpha}|{BASE_SUCCESSOR_CAPABILITY}|lineage|{growth}|4|{seed}'
        )
        task = dict(SWEEP3_FIXED)
        task.update({
            'seed': int(seed),
            'alpha': float(alpha),
            'successor_capability_growth_rate': float(growth),
            'random_seed': deterministic_seed(label),
        })
        tasks.append(task)
    return tasks


def write_rows(path, rows):
    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row[field] for field in CSV_FIELDS})


def task_key(row):
    return (
        f'{float(row["alpha"]):.4f}|'
        f'{float(row["successor_capability_growth_rate"]):.4f}|'
        f'{int(float(row["seed"]))}'
    )


def ensure_csv(path):
    if os.path.exists(path):
        return
    with open(path, 'w', newline='', encoding='utf-8') as f:
        csv.DictWriter(f, fieldnames=CSV_FIELDS).writeheader()


def completed_keys(path):
    if not os.path.exists(path):
        return set()
    keys = set()
    with open(path, 'r', newline='', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            if row.get('error'):
                continue
            keys.add(task_key(row))
    return keys


def append_rows(path, rows):
    if not rows:
        return
    with open(path, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        for row in rows:
            writer.writerow({field: row[field] for field in CSV_FIELDS})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--seeds', type=int, default=200)
    parser.add_argument('--workers', type=int, default=max(1, (os.cpu_count() or 2) - 1))
    parser.add_argument('--output-dir', default=HERE)
    parser.add_argument('--resume', action='store_true')
    args = parser.parse_args()

    tasks = build_tasks(args.seeds)
    out_path = os.path.join(args.output_dir, OUT_FILE)
    os.makedirs(args.output_dir, exist_ok=True)
    ensure_csv(out_path)
    if args.resume:
        done = completed_keys(out_path)
        tasks = [task for task in tasks if task_key(task) not in done]
    print(
        f'{datetime.now(timezone.utc).isoformat(timespec="seconds")} '
        f'planned={len(tasks)} seeds=0..{args.seeds - 1} workers={args.workers}'
    )
    start = time.time()
    buffer = []
    errors = 0
    checkpoint_every = max(1, min(10, len(tasks) // 100))
    with mp.Pool(args.workers, maxtasksperchild=20) as pool:
        for idx, row in enumerate(pool.imap_unordered(run_single, tasks), start=1):
            buffer.append(row)
            if row.get('error'):
                errors += 1
            if len(buffer) >= 10:
                append_rows(out_path, buffer)
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
    append_rows(out_path, buffer)
    print(
        f'{datetime.now(timezone.utc).isoformat(timespec="seconds")} '
        f'wrote={out_path} new_rows={len(tasks)} errors={errors}'
    )


if __name__ == '__main__':
    mp.freeze_support()
    main()
