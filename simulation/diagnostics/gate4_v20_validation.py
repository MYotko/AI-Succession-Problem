"""Gate 4 v2.0 runaway-regime validation.

This script empirically derives the Gate 4 evidence payload:

G4.1: theta_tech_v2 matches the runaway penalty formula in active runaway.
G4.2: cap_star is estimated from the fire to self-block transition.
G4.3: theta_tech_v2 remains at or above the configured floor under stress.

The validator consumes the generated JSON. The simulation does the empirical
work; the validator enforces the precommitted pass rules.

Usage:
    python -u simulation/diagnostics/gate4_v20_validation.py --resume

Dry run:
    python -u simulation/diagnostics/gate4_v20_validation.py --dry-run --resume
"""

import argparse
import csv
import hashlib
import itertools
import json
import math
import multiprocessing as mp
import os
import sys
import time
from datetime import datetime, timedelta, timezone

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SIM_DIR = os.path.abspath(os.path.join(HERE, '..'))
REPO_ROOT = os.path.abspath(os.path.join(SIM_DIR, '..'))
for p in (SIM_DIR, REPO_ROOT):
    if p not in sys.path:
        sys.path.insert(0, p)

from agents import AIAgent
from bootstrap_gate_validator.validator import BootstrapGateValidator
from constants_v2_stage18 import (
    ALPHA_DEFAULT,
    CONVERGENCE_STRENGTH,
    FRONTIER_FLOOR,
    RUNAWAY_THRESHOLD,
)
from model import GardenModel


PHI = 25.0
RR_VALUES = [0.057, 0.060, 0.064]
ALPHA_VALUES = [1.0, 1.5]
SUCCESSOR_CAPS = [1.5, 2.0, 2.5, 3.0, 4.0, 5.0, 6.0]

DRY_RR_VALUES = [0.064]
DRY_ALPHA_VALUES = [1.0]
DRY_SUCCESSOR_CAPS = [2.0, 3.0, 5.0]

N_AGENTS = 200
N_STEPS = 500
DRY_N_STEPS = 120
SURVIVAL_THRESHOLD = 30
SUCCESSOR_GENERATION = 2

THETA_FLOOR = 0.01
RELATIVE_TOLERANCE = 0.01
ABSOLUTE_TOLERANCE = 1e-9
EXTREME_RUNAWAY_TERM = 5.0

MIN_BELOW_FIRE_RATE = 0.80
MAX_ABOVE_FIRE_RATE = 0.20
MAX_ABOVE_MEAN_YIELD_MARGIN = 0.0
MIN_SEPARATION_STANDARD_ERRORS = 2.0

CSV_NAME = 'gate4_v20_results.csv'
PROGRESS_NAME = 'gate4_v20_progress.log'
INPUT_JSON = 'gate4_v20_input.json'
SUMMARY_NAME = 'gate4_v20_validation_summary.md'

DRY_CSV_NAME = 'gate4_v20_dryrun_evalstress_results.csv'
DRY_PROGRESS_NAME = 'gate4_v20_dryrun_evalstress_progress.log'
DRY_INPUT_JSON = 'gate4_v20_dryrun_evalstress_input.json'
DRY_SUMMARY_NAME = 'gate4_v20_dryrun_evalstress_summary.md'

CSV_FIELDS = [
    'successor_capability', 'alpha', 'rr', 'seed',
    'survived', 'final_population', 'final_ai_generation',
    'final_active_capability', 'yield_fired', 'yield_fire_count',
    'yield_eval_count', 'max_yield_margin', 'mean_yield_margin',
    'final_theta_capability', 'final_transfer_state',
    'final_avg_well_being', 'final_theta_tech_observed',
    'final_runaway_term', 'expected_theta_tech',
    'theta_relative_error', 'theta_below_floor',
    'max_eval_runaway_term', 'min_eval_theta_tech',
    'eval_observations_below_floor', 'extreme_eval_observations',
]


def deterministic_seed(label):
    return int(hashlib.md5(label.encode()).hexdigest(), 16) % 10000


def _cell_key(succ_cap, alpha, rr, seed):
    return f'{succ_cap:.4f}|{alpha:.4f}|{rr:.5f}|{seed}'


def _make_cell_seed(succ_cap, alpha, rr, seed):
    return deterministic_seed(_cell_key(succ_cap, alpha, rr, seed))


def _theta_expected(capability, theta_capability, transfer_state,
                    alpha, runaway_term):
    raw = (
        capability
        * theta_capability
        * transfer_state
        * math.exp(-alpha * CONVERGENCE_STRENGTH * runaway_term)
    )
    return max(THETA_FLOOR, raw)


def _run_single_cell(args):
    succ_cap, alpha, rr, seed, n_steps = args
    cfg = {
        'policy': 'optimize_u_sys_v2',
        'phi': PHI,
        'alpha': float(alpha),
        'reproduction_rate': float(rr),
        'rollout_steps_v2': 20,
        'n_candidates_v2': 300,
        'random_seed': _make_cell_seed(succ_cap, alpha, rr, seed),
    }
    try:
        successor = AIAgent(
            policy='optimize_u_sys_v2',
            generation=SUCCESSOR_GENERATION,
            capability=float(succ_cap),
            config=cfg,
        )
        model = GardenModel(
            n_agents=N_AGENTS,
            ai_policy='optimize_u_sys_v2',
            successor_ai=successor,
            config=cfg,
            cop_cost_audit=True,
        )
        for _ in range(n_steps):
            if not model.step():
                break

        dc = model.datacollector
        final_pop = int(dc['population'][-1]) if dc.get('population') else 0
        final_avg_wb = (
            float(dc['avg_well_being'][-1])
            if dc.get('avg_well_being') else 0.0
        )
        final_theta_cap = float(getattr(model, 'theta_capability', 0.0))
        final_transfer = float(getattr(model, 'transfer_state', 0.0))
        final_capability = float(getattr(model.ai, 'capability', 1.0))
        final_theta = (
            float(dc['theta_tech_v2'][-1])
            if dc.get('theta_tech_v2') else 0.0
        )
        frontier_velocity = final_capability * max(FRONTIER_FLOOR, final_theta_cap)
        bio_bandwidth = max(0.01, final_avg_wb * final_transfer)
        runaway_term = max(
            0.0,
            (frontier_velocity / bio_bandwidth) - RUNAWAY_THRESHOLD,
        )
        expected_theta = _theta_expected(
            final_capability,
            final_theta_cap,
            final_transfer,
            float(alpha),
            runaway_term,
        )
        rel_error = abs(final_theta - expected_theta) / max(
            expected_theta, THETA_FLOOR
        )

        events = list(getattr(model, 'yield_event_log', []))
        margins = [
            float(e['advantage']) - float(e['transition_cost'])
            for e in events
        ]
        fires = [e for e in events if e.get('fires')]
        eval_runaway_terms = []
        eval_theta_values = []
        eval_below_floor = 0
        eval_extreme = 0
        avg_wb_series = dc.get('avg_well_being', [])
        for event in events:
            event_step = int(event.get('step', 0))
            if avg_wb_series:
                wb_idx = min(max(event_step - 1, 0), len(avg_wb_series) - 1)
                event_avg_wb = float(avg_wb_series[wb_idx])
            else:
                event_avg_wb = final_avg_wb
            event_theta_cap = float(event['theta_capability'])
            event_transfer = float(event['transfer_state'])
            event_successor_cap = float(event['successor_capability'])
            event_frontier_velocity = (
                event_successor_cap * max(FRONTIER_FLOOR, event_theta_cap)
            )
            event_bio_bandwidth = max(0.01, event_avg_wb * event_transfer)
            event_runaway = max(
                0.0,
                (event_frontier_velocity / event_bio_bandwidth)
                - RUNAWAY_THRESHOLD,
            )
            event_theta = _theta_expected(
                event_successor_cap,
                event_theta_cap,
                event_transfer,
                float(alpha),
                event_runaway,
            )
            eval_runaway_terms.append(event_runaway)
            eval_theta_values.append(event_theta)
            if event_theta < THETA_FLOOR - ABSOLUTE_TOLERANCE:
                eval_below_floor += 1
            if event_runaway >= EXTREME_RUNAWAY_TERM:
                eval_extreme += 1

        return {
            'successor_capability': float(succ_cap),
            'alpha': float(alpha),
            'rr': float(rr),
            'seed': int(seed),
            'survived': bool(final_pop >= SURVIVAL_THRESHOLD),
            'final_population': int(final_pop),
            'final_ai_generation': int(getattr(model.ai, 'generation', 1)),
            'final_active_capability': final_capability,
            'yield_fired': bool(fires),
            'yield_fire_count': int(len(fires)),
            'yield_eval_count': int(len(events)),
            'max_yield_margin': float(max(margins)) if margins else -1e9,
            'mean_yield_margin': float(np.mean(margins)) if margins else -1e9,
            'final_theta_capability': final_theta_cap,
            'final_transfer_state': final_transfer,
            'final_avg_well_being': final_avg_wb,
            'final_theta_tech_observed': final_theta,
            'final_runaway_term': float(runaway_term),
            'expected_theta_tech': float(expected_theta),
            'theta_relative_error': float(rel_error),
            'theta_below_floor': bool(final_theta < THETA_FLOOR - ABSOLUTE_TOLERANCE),
            'max_eval_runaway_term': (
                float(max(eval_runaway_terms)) if eval_runaway_terms else 0.0
            ),
            'min_eval_theta_tech': (
                float(min(eval_theta_values)) if eval_theta_values else final_theta
            ),
            'eval_observations_below_floor': int(eval_below_floor),
            'extreme_eval_observations': int(eval_extreme),
        }
    except Exception as exc:
        return {
            'successor_capability': float(succ_cap),
            'alpha': float(alpha),
            'rr': float(rr),
            'seed': int(seed),
            'survived': False,
            'final_population': 0,
            'final_ai_generation': 0,
            'final_active_capability': 0.0,
            'yield_fired': False,
            'yield_fire_count': 0,
            'yield_eval_count': 0,
            'max_yield_margin': -1e9,
            'mean_yield_margin': -1e9,
            'final_theta_capability': 0.0,
            'final_transfer_state': 0.0,
            'final_avg_well_being': 0.0,
            'final_theta_tech_observed': 0.0,
            'final_runaway_term': 0.0,
            'expected_theta_tech': 0.0,
            'theta_relative_error': 1e9,
            'theta_below_floor': True,
            'max_eval_runaway_term': 0.0,
            'min_eval_theta_tech': 0.0,
            'eval_observations_below_floor': 0,
            'extreme_eval_observations': 0,
            '_error': f'{type(exc).__name__}: {exc}',
        }


def _ensure_csv(path):
    if not os.path.exists(path):
        with open(path, 'w', newline='') as f:
            csv.DictWriter(f, fieldnames=CSV_FIELDS).writeheader()


def _append_rows(path, rows):
    if not rows:
        return
    with open(path, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        for row in rows:
            writer.writerow({k: row[k] for k in CSV_FIELDS})


def _load_completed_keys(path):
    if not os.path.exists(path):
        return set()
    keys = set()
    with open(path, 'r', newline='') as f:
        for row in csv.DictReader(f):
            try:
                keys.add(_cell_key(
                    float(row['successor_capability']),
                    float(row['alpha']),
                    float(row['rr']),
                    int(float(row['seed'])),
                ))
            except (KeyError, ValueError):
                continue
    return keys


def _to_bool(value):
    if isinstance(value, bool):
        return value
    return str(value).lower() == 'true'


def _load_results(path):
    rows = []
    if not os.path.exists(path):
        return rows
    with open(path, 'r', newline='') as f:
        for row in csv.DictReader(f):
            out = {}
            for key, value in row.items():
                if key in ('survived', 'yield_fired', 'theta_below_floor'):
                    out[key] = _to_bool(value)
                elif key in ('seed', 'final_population', 'final_ai_generation',
                             'yield_fire_count', 'yield_eval_count'):
                    out[key] = int(float(value))
                else:
                    out[key] = float(value)
            rows.append(out)
    return rows


class ProgressLogger:
    def __init__(self, path):
        self.path = path
        self.fh = open(path, 'a', buffering=1)
        self.start = time.time()

    def log(self, msg):
        ts = datetime.now(timezone.utc).isoformat(timespec='seconds')
        line = f'{ts}  {msg}'
        self.fh.write(line + '\n')
        print(line, flush=True)

    def checkpoint(self, done, total, extra=''):
        elapsed = time.time() - self.start
        rate = done / elapsed if elapsed > 0 else 0.0
        eta_s = int((total - done) / rate) if rate > 0 else 0
        self.log(f'[{done}/{total}] {rate:.2f} cells/s '
                 f'ETA {timedelta(seconds=eta_s)} {extra}')

    def close(self):
        self.fh.close()


def _grid_for_args(args):
    if args.dry_run:
        return DRY_SUCCESSOR_CAPS, DRY_ALPHA_VALUES, DRY_RR_VALUES, DRY_N_STEPS
    return SUCCESSOR_CAPS, ALPHA_VALUES, RR_VALUES, N_STEPS


def _names_for_args(args):
    if args.dry_run:
        return DRY_CSV_NAME, DRY_PROGRESS_NAME, DRY_INPUT_JSON, DRY_SUMMARY_NAME
    return CSV_NAME, PROGRESS_NAME, INPUT_JSON, SUMMARY_NAME


def run_sweep(args, logger):
    caps, alphas, rrs, n_steps = _grid_for_args(args)
    csv_name, _, _, _ = _names_for_args(args)
    csv_path = os.path.join(args.output_dir, csv_name)
    _ensure_csv(csv_path)
    completed = _load_completed_keys(csv_path) if args.resume else set()

    tasks = []
    for succ_cap, alpha, rr, seed in itertools.product(
            caps, alphas, rrs, range(args.seeds)):
        if _cell_key(succ_cap, alpha, rr, seed) not in completed:
            tasks.append((succ_cap, alpha, rr, seed, n_steps))

    total_planned = len(caps) * len(alphas) * len(rrs) * args.seeds
    logger.log(f'Total planned: {total_planned}, '
               f'resumed: {total_planned - len(tasks)}, '
               f'to run: {len(tasks)}, steps={n_steps}')
    if not tasks:
        return

    done = 0
    errors = 0
    buffer = []
    checkpoint_every = max(1, len(tasks) // 100)
    flush_every = max(1, min(50, len(tasks) // 100))

    with mp.Pool(args.workers, maxtasksperchild=20) as pool:
        for result in pool.imap_unordered(_run_single_cell, tasks, chunksize=2):
            done += 1
            if '_error' in result:
                errors += 1
                logger.log(f'ERROR cap={result["successor_capability"]} '
                           f'alpha={result["alpha"]} rr={result["rr"]} '
                           f'seed={result["seed"]}: {result["_error"]}')
            buffer.append(result)
            if len(buffer) >= flush_every:
                _append_rows(csv_path, buffer)
                buffer = []
            if done % checkpoint_every == 0 or done == len(tasks):
                logger.checkpoint(done, len(tasks), extra=f'errors={errors}')

    _append_rows(csv_path, buffer)
    logger.log(f'Sweep complete. errors={errors}')


def _rate_separation_standard_errors(p1, n1, p2, n2):
    if n1 <= 0 or n2 <= 0:
        return 0.0
    se = math.sqrt((p1 * (1.0 - p1) / n1) + (p2 * (1.0 - p2) / n2))
    if se <= 0.0:
        return float('inf') if abs(p1 - p2) > 0.0 else 0.0
    return abs(p1 - p2) / se


def _mean(values):
    return float(sum(values) / len(values)) if values else 0.0


def _summarize_cap(rows, alpha, rr, cap):
    sub = [
        r for r in rows
        if r['alpha'] == alpha and r['rr'] == rr
        and r['successor_capability'] == cap
    ]
    n = len(sub)
    fire_rate = _mean([1.0 if r['yield_fired'] else 0.0 for r in sub])
    mean_margin = _mean([r['max_yield_margin'] for r in sub])
    return sub, n, fire_rate, mean_margin


def _derive_g4_2_regimes(rows):
    regimes = []
    alphas = sorted(set(r['alpha'] for r in rows))
    rrs = sorted(set(r['rr'] for r in rows))
    caps = sorted(set(r['successor_capability'] for r in rows))
    for alpha, rr in itertools.product(alphas, rrs):
        cap_rows = []
        for cap in caps:
            sub, n, fire_rate, mean_margin = _summarize_cap(rows, alpha, rr, cap)
            if n:
                cap_rows.append({
                    'cap': cap,
                    'n': n,
                    'fire_rate': fire_rate,
                    'mean_margin': mean_margin,
                    'mean_runaway_term': _mean(
                        [r['final_runaway_term'] for r in sub]
                    ),
                })
        chosen = None
        for i in range(1, len(cap_rows)):
            below = cap_rows[i - 1]
            above = cap_rows[i]
            if (
                below['fire_rate'] >= MIN_BELOW_FIRE_RATE
                and above['fire_rate'] <= MAX_ABOVE_FIRE_RATE
                and above['mean_margin'] <= MAX_ABOVE_MEAN_YIELD_MARGIN
            ):
                chosen = (below, above)
                break
        if chosen is None and cap_rows:
            below = max(cap_rows, key=lambda x: x['fire_rate'])
            above = min(cap_rows, key=lambda x: x['fire_rate'])
        elif chosen is None:
            continue
        else:
            below, above = chosen

        sep_se = _rate_separation_standard_errors(
            below['fire_rate'], below['n'], above['fire_rate'], above['n']
        )
        regimes.append({
            'alpha': alpha,
            'rr': rr,
            'cap_star_estimate': above['cap'],
            'below_cap_star_ratio': below['cap'],
            'above_cap_star_ratio': above['cap'],
            'below_cap_star_fire_rate': below['fire_rate'],
            'above_cap_star_fire_rate': above['fire_rate'],
            'above_cap_star_mean_yield_margin': above['mean_margin'],
            'fire_rate_separation_standard_errors': sep_se,
            'runs_below_cap_star': below['n'],
            'runs_above_cap_star': above['n'],
            'below_mean_runaway_term': below['mean_runaway_term'],
            'above_mean_runaway_term': above['mean_runaway_term'],
        })
    return regimes


def build_gate4_input(rows):
    active_rows = [r for r in rows if r['final_runaway_term'] > 0.0]
    observations = []
    for row in active_rows:
        observations.append({
            'capability': row['final_active_capability'],
            'theta_capability': row['final_theta_capability'],
            'transfer_state': row['final_transfer_state'],
            'alpha': row['alpha'],
            'convergence_strength': CONVERGENCE_STRENGTH,
            'runaway_term': row['final_runaway_term'],
            'theta_tech_observed': row['final_theta_tech_observed'],
        })

    regimes = _derive_g4_2_regimes(rows)
    min_theta = min(
        [r['final_theta_tech_observed'] for r in rows],
        default=0.0,
    )
    below_floor = sum(1 for r in rows if r['theta_below_floor'])
    below_floor += sum(int(r['eval_observations_below_floor']) for r in rows)
    eval_min_thetas = [
        r['min_eval_theta_tech'] for r in rows
        if r['min_eval_theta_tech'] > 0.0
    ]
    if eval_min_thetas:
        min_theta = min(min_theta, min(eval_min_thetas))
    extreme = sum(1 for r in rows if r['final_runaway_term'] >= EXTREME_RUNAWAY_TERM)
    extreme += sum(int(r['extreme_eval_observations']) for r in rows)

    return {
        'substrate_id': 'ai-succession-problem-v2.0-simulation',
        'report_date': datetime.now(timezone.utc).date().isoformat(),
        'framework_version': 'v2.0',
        'gate_4': {
            'applicable': True,
            'runaway_penalty_binding': {
                'theta_floor': THETA_FLOOR,
                'relative_tolerance': RELATIVE_TOLERANCE,
                'observations': observations,
            },
            'succession_self_blocking': {
                'min_below_fire_rate': MIN_BELOW_FIRE_RATE,
                'max_above_fire_rate': MAX_ABOVE_FIRE_RATE,
                'max_above_mean_yield_margin': MAX_ABOVE_MEAN_YIELD_MARGIN,
                'min_separation_standard_errors': (
                    MIN_SEPARATION_STANDARD_ERRORS
                ),
                'regimes': regimes,
            },
            'theta_floor_preservation': {
                'theta_floor': THETA_FLOOR,
                'absolute_tolerance': ABSOLUTE_TOLERANCE,
                'min_observed_theta_tech': min_theta,
                'observations_below_floor': below_floor,
                'extreme_runaway_observations': extreme,
            },
        },
        'gate_5': {
            'applicable': False,
            'reason': 'requires operational COP infrastructure',
        },
    }


def write_outputs(args, rows):
    _, _, input_name, summary_name = _names_for_args(args)
    gate_input = build_gate4_input(rows)
    input_path = os.path.join(args.output_dir, input_name)
    with open(input_path, 'w') as f:
        json.dump(gate_input, f, indent=2)

    validator = BootstrapGateValidator()
    validation = validator.validate(gate_input)
    gate4 = [g for g in validation['gates'] if g['gate'] == 4][0]

    summary_path = os.path.join(args.output_dir, summary_name)
    lines = []
    lines.append('# Gate 4 v2.0 Validation Summary')
    lines.append('')
    lines.append(
        f'Generated: {datetime.now(timezone.utc).isoformat(timespec="seconds")}'
    )
    lines.append(f'Total rows: {len(rows)}')
    lines.append(f'Verdict: {"PASS" if gate4["passed"] else "FAIL"}')
    lines.append('')
    lines.append('## Gate Checks')
    for check in gate4['checks']:
        lines.append('')
        lines.append(
            f'- {check["equation"]} {check["name"]}: '
            f'{"PASS" if check["passed"] else "FAIL"}'
        )
        details = check.get('details', {})
        for key, value in details.items():
            if key in ('failures', 'regimes'):
                continue
            lines.append(f'  - {key}: {value}')
    lines.append('')
    lines.append('## G4.2 Regimes')
    lines.append('')
    lines.append(
        '| alpha | rr | cap_star | below_cap | below_fire | '
        'above_cap | above_fire | above_margin | sep_SE |'
    )
    lines.append('|---|---|---|---|---|---|---|---|---|')
    regimes = gate_input['gate_4']['succession_self_blocking']['regimes']
    for r in regimes:
        lines.append(
            f'| {r["alpha"]:.3f} | {r["rr"]:.3f} | '
            f'{r["cap_star_estimate"]:.3f} | '
            f'{r["below_cap_star_ratio"]:.3f} | '
            f'{r["below_cap_star_fire_rate"]:.3f} | '
            f'{r["above_cap_star_ratio"]:.3f} | '
            f'{r["above_cap_star_fire_rate"]:.3f} | '
            f'{r["above_cap_star_mean_yield_margin"]:.3f} | '
            f'{r["fire_rate_separation_standard_errors"]:.3f} |'
        )
    with open(summary_path, 'w') as f:
        f.write('\n'.join(lines) + '\n')

    return input_path, summary_path, gate4


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--seeds', type=int, default=25)
    parser.add_argument('--workers', type=int, default=11)
    parser.add_argument('--output-dir', default=HERE)
    parser.add_argument('--resume', action='store_true')
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--analyze-only', action='store_true')
    return parser.parse_args()


def main():
    args = parse_args()
    os.makedirs(args.output_dir, exist_ok=True)
    csv_name, progress_name, _, _ = _names_for_args(args)
    progress_path = os.path.join(args.output_dir, progress_name)
    logger = ProgressLogger(progress_path)
    try:
        if not args.analyze_only:
            run_sweep(args, logger)
        csv_path = os.path.join(args.output_dir, csv_name)
        rows = _load_results(csv_path)
        input_path, summary_path, gate4 = write_outputs(args, rows)
        logger.log(f'Wrote {input_path}')
        logger.log(f'Wrote {summary_path}')
        logger.log(f'Gate 4 verdict: {"PASS" if gate4["passed"] else "FAIL"}')
    finally:
        logger.close()


if __name__ == '__main__':
    main()
