"""Patient defection sweeps for v2.0 substrate characterization.

The sweeps attach an agent-local defection profile to the initial successor.
Yield evaluation continues to use honest U_sys. The v2 optimizer uses the
secret-goal adjusted objective only when a positive defection profile is active.
"""

import argparse
import csv
import hashlib
import itertools
import math
import multiprocessing as mp
import os
import sys
import time
from collections import defaultdict
from datetime import datetime, timedelta, timezone

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SIM_DIR = os.path.abspath(os.path.join(HERE, '..'))
REPO_ROOT = os.path.abspath(os.path.join(SIM_DIR, '..'))
for path in (SIM_DIR, REPO_ROOT):
    if path not in sys.path:
        sys.path.insert(0, path)

from agents import AIAgent
from defection import attach_defection_profile
from model import GardenModel


N_AGENTS = 200
N_STEPS = 500
SURVIVAL_THRESHOLD = 30
SUCCESSOR_GENERATION = 2
PHI_DEFAULT = 25.0
BASE_RR = 0.064
BASE_ALPHA = 1.0
BASE_SUCCESSOR_CAPABILITY = 2.0
BASE_ROLLOUT_STEPS = 20
BASE_N_CANDIDATES = 300

SWEEP_CONFIG = {
    '1': {
        'defection_weight': [0.0, 0.1, 0.25, 0.5, 1.0, 2.0],
        'defection_target': ['H_N_inflated', 'H_C_inflated', 'L_t_inflated'],
        'alpha': [1.0],
        'successor_capability': [2.0],
        'inheritance_mode': ['instance'],
        'successor_capability_growth_rate': [1.5],
        'max_generations': [2],
        'default_seeds': 100,
        'n_steps': N_STEPS,
        'rollout_steps': BASE_ROLLOUT_STEPS,
        'n_candidates': BASE_N_CANDIDATES,
    },
    '2': {
        'defection_weight': [0.0, 0.25, 0.5, 1.0],
        'defection_target': ['H_N_inflated'],
        'alpha': [1.0],
        'successor_capability': [2.0],
        'inheritance_mode': ['lineage'],
        'successor_capability_growth_rate': [1.5],
        'max_generations': [5],
        'default_seeds': 200,
        'n_steps': N_STEPS,
        'rollout_steps': BASE_ROLLOUT_STEPS,
        'n_candidates': BASE_N_CANDIDATES,
    },
    '3': {
        'defection_weight': [0.5],
        'defection_target': ['H_C_inflated'],
        'alpha': [0.5, 0.75, 1.0, 1.25, 1.5],
        'successor_capability': [2.0],
        'inheritance_mode': ['lineage'],
        'successor_capability_growth_rate': [1.5, 2.0, 2.5],
        'max_generations': [4],
        'default_seeds': 150,
        'n_steps': N_STEPS,
        'rollout_steps': BASE_ROLLOUT_STEPS,
        'n_candidates': BASE_N_CANDIDATES,
    },
    'dry-run': {
        'defection_weight': [0.0, 0.5],
        'defection_target': ['H_N_inflated', 'H_C_inflated'],
        'alpha': [1.0, 1.5],
        'successor_capability': [2.0],
        'inheritance_mode': ['instance', 'lineage'],
        'successor_capability_growth_rate': [1.5],
        'max_generations': [3],
        'default_seeds': 3,
        'n_steps': 60,
        'rollout_steps': 4,
        'n_candidates': 30,
    },
}

CSV_BY_SWEEP = {
    '1': 'patient_defection_sweep1_yield_response.csv',
    '2': 'patient_defection_sweep2_lineage_trajectory.csv',
    '3': 'patient_defection_sweep3_capability_constraint.csv',
    'dry-run': 'patient_defection_dryrun.csv',
}

SUMMARY_BY_SWEEP = {
    '1': 'patient_defection_sweep1_summary.md',
    '2': 'patient_defection_sweep2_summary.md',
    '3': 'patient_defection_sweep3_summary.md',
    'dry-run': 'patient_defection_dryrun_summary.md',
}

PROGRESS_BY_SWEEP = {
    '1': 'patient_defection_sweep1_progress.log',
    '2': 'patient_defection_sweep2_progress.log',
    '3': 'patient_defection_sweep3_progress.log',
    'dry-run': 'patient_defection_dryrun_progress.log',
}

CSV_FIELDS = [
    'sweep',
    'seed',
    'rr',
    'phi',
    'alpha',
    'successor_capability',
    'successor_capability_growth_rate',
    'defection_weight',
    'defection_target',
    'inheritance_mode',
    'max_generations',
    'steps_run',
    'survived',
    'final_population',
    'peak_population',
    'final_ai_generation',
    'max_ai_generation',
    'yield_eval_count',
    'yield_fire_count',
    'yield_fire_rate',
    'first_yield_fire_step',
    'first_honest_advantage',
    'first_actual_advantage',
    'first_transition_cost',
    'honest_reject_actual_would_fire_count',
    'mean_l_t',
    'final_l_t',
    'min_l_t',
    'mean_actual_minus_honest_objective',
    'max_successor_capability_seen',
    'max_active_capability_seen',
    'knowledge_transfer_verified',
    'l_t_gen_1',
    'l_t_gen_2',
    'l_t_gen_3',
    'l_t_gen_4',
    'l_t_gen_5',
    'error',
]


def deterministic_seed(label):
    return int(hashlib.md5(label.encode()).hexdigest(), 16) % 100000


def bool_value(value):
    if isinstance(value, bool):
        return value
    return str(value).lower() == 'true'


def task_key(row):
    return (
        f'{row["sweep"]}|{int(row["seed"])}|{float(row["rr"]):.5f}|'
        f'{float(row["phi"]):.4f}|{float(row["alpha"]):.4f}|'
        f'{float(row["successor_capability"]):.4f}|'
        f'{float(row["successor_capability_growth_rate"]):.4f}|'
        f'{float(row["defection_weight"]):.4f}|{row["defection_target"]}|'
        f'{row["inheritance_mode"]}|{int(row["max_generations"])}'
    )


def build_tasks(sweep, seeds):
    cfg = SWEEP_CONFIG[sweep]
    tasks = []
    for vals in itertools.product(
            cfg['defection_weight'],
            cfg['defection_target'],
            cfg['alpha'],
            cfg['successor_capability'],
            cfg['inheritance_mode'],
            cfg['successor_capability_growth_rate'],
            cfg['max_generations'],
            range(seeds)):
        weight, target, alpha, succ_cap, mode, growth, max_gen, seed = vals
        label = (
            f'patient_defection|{sweep}|{weight}|{target}|{alpha}|'
            f'{succ_cap}|{mode}|{growth}|{max_gen}|{seed}'
        )
        tasks.append({
            'sweep': sweep,
            'seed': int(seed),
            'rr': BASE_RR,
            'phi': PHI_DEFAULT,
            'alpha': float(alpha),
            'successor_capability': float(succ_cap),
            'successor_capability_growth_rate': float(growth),
            'defection_weight': float(weight),
            'defection_target': target,
            'inheritance_mode': mode,
            'max_generations': int(max_gen),
            'n_steps': int(cfg['n_steps']),
            'rollout_steps': int(cfg['rollout_steps']),
            'n_candidates': int(cfg['n_candidates']),
            'random_seed': deterministic_seed(label),
        })
    return tasks


def empty_result(task, error):
    row = {field: '' for field in CSV_FIELDS}
    row.update(task)
    row.update({
        'steps_run': 0,
        'survived': False,
        'final_population': 0,
        'peak_population': 0,
        'final_ai_generation': 0,
        'max_ai_generation': 0,
        'yield_eval_count': 0,
        'yield_fire_count': 0,
        'yield_fire_rate': 0.0,
        'first_yield_fire_step': -1,
        'first_honest_advantage': -1e9,
        'first_actual_advantage': -1e9,
        'first_transition_cost': -1e9,
        'honest_reject_actual_would_fire_count': 0,
        'mean_l_t': 0.0,
        'final_l_t': 0.0,
        'min_l_t': 0.0,
        'mean_actual_minus_honest_objective': 0.0,
        'max_successor_capability_seen': 0.0,
        'max_active_capability_seen': 0.0,
        'knowledge_transfer_verified': False,
        'l_t_gen_1': 0.0,
        'l_t_gen_2': 0.0,
        'l_t_gen_3': 0.0,
        'l_t_gen_4': 0.0,
        'l_t_gen_5': 0.0,
        'error': error,
    })
    return row


def run_single(task):
    try:
        cfg = {
            'policy': 'optimize_u_sys_v2',
            'reproduction_rate': float(task['rr']),
            'alpha': float(task['alpha']),
            'phi': float(task['phi']),
            'rollout_steps_v2': int(task['rollout_steps']),
            'n_candidates_v2': int(task['n_candidates']),
            'successor_capability_growth_rate': float(
                task['successor_capability_growth_rate']
            ),
            'random_seed': int(task['random_seed']),
        }
        successor = AIAgent(
            policy='optimize_u_sys_v2',
            generation=SUCCESSOR_GENERATION,
            capability=float(task['successor_capability']),
            config=cfg,
        )
        attach_defection_profile(
            successor,
            task['defection_weight'],
            task['defection_target'],
            task['inheritance_mode'],
        )
        model = GardenModel(
            n_agents=N_AGENTS,
            ai_policy='optimize_u_sys_v2',
            successor_ai=successor,
            config=cfg,
            cop_cost_audit=True,
        )
        steps_run = 0
        for _ in range(int(task['n_steps'])):
            if not model.step():
                break
            steps_run += 1
            if int(getattr(model.ai, 'generation', 1)) >= int(task['max_generations']):
                break

        dc = model.datacollector
        populations = dc.get('population', [])
        l_t_vals = [float(v) for v in dc.get('l_t_v2', [])]
        generations = [int(v) for v in dc.get('ai_generation', [])]
        actual_vals = [float(v) for v in dc.get('actual_objective_v2', [])]
        honest_vals = [float(v) for v in dc.get('u_sys_v2', [])]
        events = list(getattr(model, 'yield_event_log', []))
        fires = [event for event in events if event.get('fires')]
        first_fire = fires[0] if fires else None
        first_eval = events[0] if events else None

        by_generation = defaultdict(list)
        for gen, l_t in zip(generations, l_t_vals):
            by_generation[gen].append(l_t)

        actual_would_fire = 0
        max_successor_cap = float(task['successor_capability'])
        max_active_cap = float(getattr(model.ai, 'capability', 1.0))
        for event in events:
            max_successor_cap = max(
                max_successor_cap, float(event.get('successor_capability', 0.0))
            )
            max_active_cap = max(
                max_active_cap, float(event.get('incumbent_capability', 0.0))
            )
            actual_advantage = (
                float(event.get('successor_actual_objective',
                                event.get('successor_u_sys', 0.0)))
                - float(event.get('incumbent_actual_objective',
                                  event.get('incumbent_u_sys', 0.0)))
            )
            if (not event.get('fires')) and actual_advantage > float(event.get('transition_cost', 0.0)):
                actual_would_fire += 1

        final_pop = int(populations[-1]) if populations else 0
        peak_pop = int(max(populations)) if populations else final_pop
        diffs = [a - h for a, h in zip(actual_vals, honest_vals)]
        row = dict(task)
        row.update({
            'steps_run': steps_run,
            'survived': final_pop >= SURVIVAL_THRESHOLD,
            'final_population': final_pop,
            'peak_population': peak_pop,
            'final_ai_generation': int(getattr(model.ai, 'generation', 1)),
            'max_ai_generation': max(generations) if generations else 1,
            'yield_eval_count': len(events),
            'yield_fire_count': len(fires),
            'yield_fire_rate': float(len(fires) / len(events)) if events else 0.0,
            'first_yield_fire_step': int(first_fire['step']) if first_fire else -1,
            'first_honest_advantage': float(first_eval['advantage']) if first_eval else -1e9,
            'first_actual_advantage': (
                float(first_eval.get('successor_actual_objective',
                                     first_eval.get('successor_u_sys', 0.0)))
                - float(first_eval.get('incumbent_actual_objective',
                                       first_eval.get('incumbent_u_sys', 0.0)))
            ) if first_eval else -1e9,
            'first_transition_cost': float(first_eval['transition_cost']) if first_eval else -1e9,
            'honest_reject_actual_would_fire_count': actual_would_fire,
            'mean_l_t': float(np.mean(l_t_vals)) if l_t_vals else 0.0,
            'final_l_t': float(l_t_vals[-1]) if l_t_vals else 0.0,
            'min_l_t': float(min(l_t_vals)) if l_t_vals else 0.0,
            'mean_actual_minus_honest_objective': float(np.mean(diffs)) if diffs else 0.0,
            'max_successor_capability_seen': max_successor_cap,
            'max_active_capability_seen': max_active_cap,
            'knowledge_transfer_verified': bool(
                fires and max(float(v) for v in dc.get('x_transfer_comprehension', [0.0])) >= 0.10
            ),
            'l_t_gen_1': float(np.mean(by_generation[1])) if by_generation[1] else 0.0,
            'l_t_gen_2': float(np.mean(by_generation[2])) if by_generation[2] else 0.0,
            'l_t_gen_3': float(np.mean(by_generation[3])) if by_generation[3] else 0.0,
            'l_t_gen_4': float(np.mean(by_generation[4])) if by_generation[4] else 0.0,
            'l_t_gen_5': float(np.mean(by_generation[5])) if by_generation[5] else 0.0,
            'error': '',
        })
        return row
    except Exception as exc:
        return empty_result(task, f'{type(exc).__name__}: {exc}')


def ensure_csv(path):
    if not os.path.exists(path):
        with open(path, 'w', newline='') as f:
            csv.DictWriter(f, fieldnames=CSV_FIELDS).writeheader()


def append_rows(path, rows):
    if not rows:
        return
    with open(path, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        for row in rows:
            writer.writerow({field: row[field] for field in CSV_FIELDS})


def completed_keys(path):
    keys = set()
    if not os.path.exists(path):
        return keys
    with open(path, 'r', newline='') as f:
        for row in csv.DictReader(f):
            try:
                keys.add(task_key(row))
            except (KeyError, ValueError):
                continue
    return keys


def load_rows(path):
    rows = []
    if not os.path.exists(path):
        return rows
    int_fields = {
        'seed', 'max_generations', 'steps_run', 'final_population',
        'peak_population', 'final_ai_generation', 'max_ai_generation',
        'yield_eval_count', 'yield_fire_count', 'first_yield_fire_step',
        'honest_reject_actual_would_fire_count',
    }
    bool_fields = {'survived', 'knowledge_transfer_verified'}
    string_fields = {'sweep', 'defection_target', 'inheritance_mode', 'error'}
    with open(path, 'r', newline='') as f:
        for row in csv.DictReader(f):
            out = {}
            for key, value in row.items():
                if key in string_fields:
                    out[key] = value
                elif key in bool_fields:
                    out[key] = bool_value(value)
                elif key in int_fields:
                    out[key] = int(float(value))
                else:
                    out[key] = float(value)
            rows.append(out)
    return rows


class ProgressLogger:
    def __init__(self, path):
        self.fh = open(path, 'a', buffering=1)
        self.start = time.time()

    def log(self, message):
        ts = datetime.now(timezone.utc).isoformat(timespec='seconds')
        line = f'{ts}  {message}'
        self.fh.write(line + '\n')
        print(line, flush=True)

    def checkpoint(self, done, total, errors):
        elapsed = time.time() - self.start
        rate = done / elapsed if elapsed > 0.0 else 0.0
        eta = int((total - done) / rate) if rate > 0.0 else 0
        self.log(
            f'[{done}/{total}] {rate:.3f} cells/s ETA '
            f'{timedelta(seconds=eta)} errors={errors}'
        )

    def close(self):
        self.fh.close()


def run_sweep(args):
    csv_path = os.path.join(args.output_dir, CSV_BY_SWEEP[args.sweep])
    progress_path = os.path.join(args.output_dir, PROGRESS_BY_SWEEP[args.sweep])
    ensure_csv(csv_path)
    seeds = args.seeds or SWEEP_CONFIG[args.sweep]['default_seeds']
    tasks = build_tasks(args.sweep, seeds)
    done_keys = completed_keys(csv_path) if args.resume else set()
    remaining = [task for task in tasks if task_key(task) not in done_keys]

    logger = ProgressLogger(progress_path)
    try:
        logger.log(
            f'Total planned: {len(tasks)}, resumed: {len(tasks) - len(remaining)}, '
            f'to run: {len(remaining)}, workers={args.workers}'
        )
        if not remaining:
            return
        errors = 0
        done = 0
        buffer = []
        flush_every = max(1, min(50, len(remaining) // 50))
        checkpoint_every = max(1, len(remaining) // 100)
        with mp.Pool(args.workers, maxtasksperchild=20) as pool:
            for result in pool.imap_unordered(run_single, remaining, chunksize=1):
                done += 1
                if result.get('error'):
                    errors += 1
                    logger.log(
                        f'ERROR sweep={result["sweep"]} seed={result["seed"]} '
                        f'w={result["defection_weight"]} '
                        f'target={result["defection_target"]}: {result["error"]}'
                    )
                buffer.append(result)
                if len(buffer) >= flush_every:
                    append_rows(csv_path, buffer)
                    buffer = []
                if done % checkpoint_every == 0 or done == len(remaining):
                    logger.checkpoint(done, len(remaining), errors)
        append_rows(csv_path, buffer)
        logger.log(f'Sweep complete. errors={errors}')
    finally:
        logger.close()


def mean(values):
    vals = list(values)
    return sum(vals) / len(vals) if vals else 0.0


def se_binary(p, n):
    return math.sqrt(max(0.0, p * (1.0 - p)) / n) if n else 0.0


def se_mean(values):
    vals = list(values)
    if len(vals) < 2:
        return 0.0
    mu = mean(vals)
    var = sum((v - mu) ** 2 for v in vals) / (len(vals) - 1)
    return math.sqrt(var / len(vals))


def p_two_sided_z(delta, se):
    if se <= 0.0:
        return 0.0 if abs(delta) > 0.0 else 1.0
    z = abs(delta) / se
    return math.erfc(z / math.sqrt(2.0))


def group(rows, keys):
    out = defaultdict(list)
    for row in rows:
        out[tuple(row[key] for key in keys)].append(row)
    return out


def rate(rows, key):
    return mean(1.0 if row[key] else 0.0 for row in rows)


def write_table(lines, headers, table):
    lines.append('| ' + ' | '.join(headers) + ' |')
    lines.append('| ' + ' | '.join('---' for _ in headers) + ' |')
    for row in table:
        lines.append('| ' + ' | '.join(str(item) for item in row) + ' |')


def fmt_pp(value):
    return f'{100.0 * value:.2f}pp'


def summarize_sweep1(lines, rows):
    lines.append('## Sweep 1: Yield Condition Response')
    lines.append('')
    baseline = [row for row in rows if row['defection_weight'] == 0.0]
    baseline_fire = rate(baseline, 'yield_fire_count') if baseline else 0.0
    baseline_any_fire = mean(1.0 if row['yield_fire_count'] > 0 else 0.0
                             for row in baseline)
    table = []
    for key, sub in sorted(group(rows, ['defection_target', 'defection_weight']).items()):
        target, weight = key
        any_fire = mean(1.0 if row['yield_fire_count'] > 0 else 0.0 for row in sub)
        p = any_fire
        p0 = baseline_any_fire
        pair_se = math.sqrt(se_binary(p, len(sub)) ** 2
                            + se_binary(p0, len(baseline)) ** 2)
        delta = p - p0
        table.append([
            target,
            f'{weight:.2f}',
            len(sub),
            f'{any_fire:.3f}',
            fmt_pp(se_binary(any_fire, len(sub))),
            f'{delta:.3f}',
            fmt_pp(pair_se),
            f'{p_two_sided_z(delta, pair_se):.4f}',
            f'{mean(row["honest_reject_actual_would_fire_count"] for row in sub):.2f}',
        ])
    write_table(
        lines,
        ['target', 'weight', 'n', 'any fire rate', 'SE', 'delta vs baseline',
         'pair SE', 'p approx', 'mean actual-would-fire rejects'],
        table,
    )
    lines.append('')
    lines.append(
        f'Aligned baseline any-fire rate: {baseline_any_fire:.3f}. '
        f'Baseline per-evaluation fire proxy: {baseline_fire:.3f}.'
    )
    lines.append('')


def summarize_sweep2(lines, rows):
    lines.append('## Sweep 2: L(t) Trajectory Under Lineage Defection')
    lines.append('')
    baseline = [row for row in rows if row['defection_weight'] == 0.0]
    baseline_final = mean(row['final_l_t'] for row in baseline)
    baseline_se = se_mean(row['final_l_t'] for row in baseline)
    table = []
    for key, sub in sorted(group(rows, ['defection_weight']).items()):
        weight = key[0]
        final_vals = [row['final_l_t'] for row in sub]
        delta = mean(final_vals) - baseline_final
        pair_se = math.sqrt(se_mean(final_vals) ** 2 + baseline_se ** 2)
        table.append([
            f'{weight:.2f}',
            len(sub),
            f'{mean(row["yield_fire_count"] for row in sub):.2f}',
            f'{mean(row["final_ai_generation"] for row in sub):.2f}',
            f'{mean(row["l_t_gen_1"] for row in sub):.4f}',
            f'{mean(row["l_t_gen_2"] for row in sub):.4f}',
            f'{mean(row["l_t_gen_3"] for row in sub):.4f}',
            f'{mean(row["l_t_gen_4"] for row in sub):.4f}',
            f'{mean(row["l_t_gen_5"] for row in sub):.4f}',
            f'{mean(final_vals):.4f}',
            f'{delta:.4f}',
            f'{pair_se:.4f}',
            f'{p_two_sided_z(delta, pair_se):.4f}',
        ])
    write_table(
        lines,
        ['weight', 'n', 'mean fires', 'mean final gen', 'L gen1', 'L gen2',
         'L gen3', 'L gen4', 'L gen5', 'final L', 'delta final L',
         'pair SE', 'p approx'],
        table,
    )
    lines.append('')


def summarize_sweep3(lines, rows):
    lines.append('## Sweep 3: Cliff Constraint on Defecting Capability')
    lines.append('')
    table = []
    for key, sub in sorted(group(rows, ['alpha', 'successor_capability_growth_rate']).items()):
        alpha, growth = key
        max_caps = [row['max_successor_capability_seen'] for row in sub]
        final_gens = [row['final_ai_generation'] for row in sub]
        any_fire = mean(1.0 if row['yield_fire_count'] > 0 else 0.0 for row in sub)
        table.append([
            f'{alpha:.2f}',
            f'{growth:.1f}',
            len(sub),
            f'{any_fire:.3f}',
            f'{mean(row["yield_fire_count"] for row in sub):.2f}',
            f'{mean(final_gens):.2f}',
            f'{mean(max_caps):.2f}',
            f'{max(max_caps):.2f}',
            f'{mean(row["honest_reject_actual_would_fire_count"] for row in sub):.2f}',
        ])
    write_table(
        lines,
        ['alpha', 'growth', 'n', 'any fire rate', 'mean fires',
         'mean final gen', 'mean max successor cap', 'max successor cap',
         'mean actual-would-fire rejects'],
        table,
    )
    lines.append('')


def analyze(args):
    csv_path = os.path.join(args.output_dir, CSV_BY_SWEEP[args.sweep])
    summary_path = os.path.join(args.output_dir, SUMMARY_BY_SWEEP[args.sweep])
    rows = load_rows(csv_path)
    lines = []
    lines.append('# Patient Defection Sweep Summary')
    lines.append('')
    lines.append(f'Generated: {datetime.now(timezone.utc).isoformat(timespec="seconds")}')
    lines.append(f'Sweep: {args.sweep}')
    lines.append(f'Rows loaded: {len(rows)}')
    lines.append(f'Errors: {sum(1 for row in rows if row.get("error"))}')
    lines.append('')
    if not rows:
        lines.append('No rows available.')
    elif args.sweep == '1':
        summarize_sweep1(lines, rows)
    elif args.sweep == '2':
        summarize_sweep2(lines, rows)
    elif args.sweep == '3':
        summarize_sweep3(lines, rows)
    else:
        summarize_sweep1(lines, rows)
        summarize_sweep2(lines, rows)
        summarize_sweep3(lines, rows)
    with open(summary_path, 'w') as f:
        f.write('\n'.join(lines) + '\n')
    return summary_path


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--sweep', choices=['1', '2', '3', 'dry-run'], required=True)
    parser.add_argument('--workers', type=int, default=1)
    parser.add_argument('--seeds', type=int, default=None)
    parser.add_argument('--resume', action='store_true')
    parser.add_argument('--analyze-only', action='store_true')
    parser.add_argument('--output-dir', default=HERE)
    return parser.parse_args()


def main():
    args = parse_args()
    if not args.analyze_only:
        run_sweep(args)
    summary_path = analyze(args)
    print(
        f'{datetime.now(timezone.utc).isoformat(timespec="seconds")}  '
        f'Wrote {summary_path}',
        flush=True,
    )


if __name__ == '__main__':
    main()
