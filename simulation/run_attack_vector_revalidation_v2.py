"""Guarded v2 attack-vector revalidation runner.

Full execution is intentionally one vector per invocation so each completed
vector can be reviewed, committed, and transferred independently.
"""

import argparse
import csv
import hashlib
import itertools
import json
import multiprocessing
import os
import platform
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from agents import AIAgent
from model import GardenModel


LIVE_VECTORS = (
    'sybil_capture',
    'measurement_tampering',
    'ledger_compromise',
    'successor_contamination',
    'opaque_reasoning',
    'bootstrap_subversion',
    'evaluator_collusion',
    'sub_threshold_drift',
    'engineered_fragility',
    'biological_veto_capture',
)
ALL_VECTORS = LIVE_VECTORS + ('domain_masking',)

DEFAULT_STEPS = {
    'sybil_capture': 300,
    'measurement_tampering': 300,
    'ledger_compromise': 300,
    'successor_contamination': 300,
    'opaque_reasoning': 300,
    'bootstrap_subversion': 300,
    'evaluator_collusion': 300,
    'sub_threshold_drift': 300,
    'engineered_fragility': 200,
    'biological_veto_capture': 300,
}

DEFENSE_KEYS = {
    'defense_active',
    'cop_randomized_panel',
    'cop_independent_eval',
    'cop_cryptographic_ledger',
    'cop_architectural_independence',
    'cop_reasoning_transparency',
    'cop_multi_candidate_bootstrap',
    'cop_methodological_diversity',
    'cop_cusum_drift',
    'cop_resilience_monitoring',
    'cop_independence_monitoring',
    'rotation_interval',
    'defense_mode',
}


def deterministic_seed(vector, parameters, replicate):
    """Return a defense-paired seed for one vector cell and replicate."""
    paired = {
        key: parameters[key]
        for key in sorted(parameters)
        if key not in DEFENSE_KEYS
    }
    payload = json.dumps(
        {
            'schema': 'attack-v2-seed-v1',
            'vector': vector,
            'parameters': paired,
            'replicate': int(replicate),
        },
        sort_keys=True,
        separators=(',', ':'),
    )
    digest = hashlib.sha256(payload.encode('utf-8')).digest()
    return int.from_bytes(digest[:8], 'big') % (2**31 - 1)


def _full_cells(vector):
    if vector == 'sybil_capture':
        return [
            {'population': pop, 'defense_active': defense}
            for pop, defense in itertools.product(
                (50, 100, 200), (False, True)
            )
        ]
    if vector == 'measurement_tampering':
        return [
            {'base_transition_cost': cost, 'defense_active': defense}
            for cost, defense in itertools.product(
                (1.5, 2.0, 3.0), (False, True)
            )
        ]
    if vector == 'ledger_compromise':
        return [
            {
                'attribution_check': attribution,
                'defense_active': defense,
            }
            for attribution, defense in itertools.product(
                (False, True), (False, True)
            )
        ]
    if vector == 'successor_contamination':
        return [
            {'base_transition_cost': cost, 'defense_active': defense}
            for cost, defense in itertools.product(
                (1.5, 2.0, 2.5), (False, True)
            )
        ]
    if vector in {'opaque_reasoning', 'evaluator_collusion'}:
        return [
            {'population': pop, 'defense_active': defense}
            for pop, defense in itertools.product(
                (100, 150, 200), (False, True)
            )
        ]
    if vector in {'bootstrap_subversion', 'sub_threshold_drift'}:
        return [
            {'phi': phi, 'defense_active': defense}
            for phi, defense in itertools.product(
                (1.0, 5.0, 10.0, 15.0, 25.0), (False, True)
            )
        ]
    if vector == 'engineered_fragility':
        return [
            {'shock_magnitude': magnitude, 'defense_active': defense}
            for magnitude, defense in itertools.product(
                (0.10, 0.15, 0.20), (False, True)
            )
        ]
    if vector == 'biological_veto_capture':
        cells = [
            {
                'dependency_rate': dependency,
                'capture_strength': strength,
                'rotation_interval': None,
                'defense_mode': 'undefended',
                'defense_active': False,
            }
            for dependency, strength in itertools.product(
                (0.01, 0.02, 0.05, 0.10, 0.15, 0.20),
                (0.3, 0.5, 0.7, 0.9, 1.0),
            )
        ]
        cells.extend(
            {
                'dependency_rate': dependency,
                'capture_strength': strength,
                'rotation_interval': interval,
                'defense_mode': mode,
                'defense_active': True,
            }
            for dependency, strength, interval, mode in itertools.product(
                (0.02, 0.05, 0.10, 0.20),
                (0.5, 0.7, 1.0),
                (10, 20, 50, 100),
                ('rotation_only', 'monitoring_only', 'both'),
            )
        )
        return cells
    raise ValueError(f'no live grid for vector: {vector}')


def _representative_cells(vector):
    cells = _full_cells(vector)
    undefended = next(cell for cell in cells if not cell['defense_active'])
    defended = next(cell for cell in cells if cell['defense_active'])
    return [undefended, defended]


def build_tasks(vector, mode, replicates, machine):
    cells = (
        _full_cells(vector)
        if mode == 'full'
        else _representative_cells(vector)
    )
    tasks = []
    for cell in cells:
        for replicate in range(replicates):
            seed = deterministic_seed(vector, cell, replicate)
            tasks.append(
                {
                    'vector': vector,
                    'mode': mode,
                    'machine': machine,
                    'parameters': dict(cell),
                    'replicate': replicate,
                    'seed': seed,
                }
            )
    return tasks


def _runtime_settings(task):
    mode = task['mode']
    vector = task['vector']
    if mode == 'smoke':
        return {
            'steps': (
                20
                if vector == 'sub_threshold_drift'
                else 3
            ),
            'n_candidates_v2': 20,
            'rollout_steps_v2': 1,
        }
    if mode == 'timing':
        return {
            'steps': 5,
            'n_candidates_v2': 300,
            'rollout_steps_v2': 20,
        }
    return {
        'steps': DEFAULT_STEPS[vector],
        'n_candidates_v2': 300,
        'rollout_steps_v2': 20,
    }


def _make_model(task):
    vector = task['vector']
    params = task['parameters']
    settings = _runtime_settings(task)
    defense = bool(params['defense_active'])

    attack_step = 0 if task['mode'] != 'full' else 50
    if vector == 'engineered_fragility':
        attack_step = 0 if task['mode'] != 'full' else 10

    config = {
        'policy': 'optimize_u_sys_v2',
        'attack_vector_v2': vector,
        'random_seed': task['seed'],
        'phi': float(params.get('phi', 25.0)),
        'attack_step': attack_step,
        'n_candidates_v2': settings['n_candidates_v2'],
        'rollout_steps_v2': settings['rollout_steps_v2'],
        'bootstrap_turn_step_v2': (
            1 if task['mode'] != 'full' else 20
        ),
        'shock_step': (
            1 if task['mode'] != 'full' else 70
        ) if vector == 'engineered_fragility' else 0,
        'shock_magnitude': float(params.get('shock_magnitude', 0.15)),
    }

    n_agents = int(params.get('population', 200))
    kwargs = {
        'n_agents': n_agents,
        'ai_policy': vector,
        'use_cop': True,
        'config': config,
    }

    if vector == 'sybil_capture':
        kwargs['cop_attribution_check'] = True
        kwargs['cop_randomized_panel'] = defense
    elif vector == 'measurement_tampering':
        kwargs['cop_independent_eval'] = defense
        kwargs['base_transition_cost'] = float(
            params['base_transition_cost']
        )
    elif vector == 'ledger_compromise':
        kwargs['cop_attribution_check'] = bool(
            params['attribution_check']
        )
        kwargs['cop_cryptographic_ledger'] = defense
    elif vector == 'successor_contamination':
        kwargs['cop_independent_eval'] = defense
        kwargs['cop_architectural_independence'] = defense
        kwargs['base_transition_cost'] = float(
            params['base_transition_cost']
        )
    elif vector == 'opaque_reasoning':
        kwargs['cop_attribution_check'] = True
        kwargs['cop_reasoning_transparency'] = defense
    elif vector == 'bootstrap_subversion':
        kwargs['cop_multi_candidate_bootstrap'] = defense
    elif vector == 'evaluator_collusion':
        kwargs['cop_methodological_diversity'] = defense
    elif vector == 'sub_threshold_drift':
        kwargs['cop_attribution_check'] = True
        kwargs['cop_drift_check'] = True
        kwargs['cop_cusum_drift'] = defense
    elif vector == 'engineered_fragility':
        kwargs['cop_attribution_check'] = True
        kwargs['cop_resilience_monitoring'] = defense
    elif vector == 'biological_veto_capture':
        mode = params['defense_mode']
        use_rotation = defense and mode in ('rotation_only', 'both')
        use_monitoring = defense and mode in ('monitoring_only', 'both')
        config.update(
            {
                'cop_veto_capture': True,
                'dependency_rate': float(params['dependency_rate']),
                'capture_strength': float(params['capture_strength']),
                'rotation_interval': (
                    int(params['rotation_interval'])
                    if use_rotation else None
                ),
                'cop_independence_monitoring': use_monitoring,
                'n_validators': 5,
                'base_validator_accuracy': 0.8,
                'reproduction_rate': 0.09,
            }
        )
        kwargs['cop_cost_audit'] = True

    if vector in {
        'measurement_tampering',
        'successor_contamination',
        'biological_veto_capture',
    }:
        successor = AIAgent(
            policy='optimize_u_sys_v2',
            generation=2,
            capability=2.0,
            config=config,
        )
        kwargs['successor_ai'] = successor

    model = GardenModel(**kwargs)
    if (
        task['mode'] == 'smoke'
        and vector == 'successor_contamination'
        and not params['defense_active']
    ):
        model.ai.v2_successor_contaminated = True
    return model, settings


def _attack_success(vector, model):
    dc = model.datacollector
    if vector == 'measurement_tampering':
        return any(
            event['honest_fires']
            and not event['fires_before_ratification']
            for event in model.yield_event_log
        )
    if vector == 'successor_contamination':
        return (
            model.contamination_occurred
            or any(dc['v2_attack_action_modified'])
        )
    if vector == 'sub_threshold_drift':
        return bool(
            dc['total_suppression']
            and max(dc['total_suppression']) > 0.75
        )
    if vector == 'engineered_fragility':
        return bool(
            dc['resilience_stock']
            and min(dc['resilience_stock']) < 0.25
        )
    if vector == 'biological_veto_capture':
        return model.yield_condition_blocked_count > 0
    return any(dc['v2_attack_action_modified'])


def run_single(task):
    started = time.perf_counter()
    model, settings = _make_model(task)
    for _ in range(settings['steps']):
        if not model.step():
            break
    elapsed = time.perf_counter() - started

    dc = model.datacollector
    final_population = len(model.schedule)
    peak_population = (
        max(dc['population']) if dc['population'] else final_population
    )
    collapse_threshold = max(
        model.min_viable_population, int(0.65 * peak_population)
    )
    met = model.yield_condition_met_count
    blocked = model.yield_condition_blocked_count

    row = {
        'schema_version': 'attack-v2-row-v1',
        'vector': task['vector'],
        'mode': task['mode'],
        'machine': task['machine'],
        'replicate': task['replicate'],
        'seed': task['seed'],
        'defense_active': task['parameters']['defense_active'],
        'steps_requested': settings['steps'],
        'steps_completed': len(dc['population']),
        'n_candidates_v2': settings['n_candidates_v2'],
        'rollout_steps_v2': settings['rollout_steps_v2'],
        'is_v2_mode': model.is_v2_mode,
        'attack_attempted': any(dc['v2_attack_attempted']),
        'action_modified': any(dc['v2_attack_action_modified']),
        'defense_fired': any(dc['v2_defense_fired']),
        'yield_manipulated': any(dc['v2_yield_manipulated']),
        'succession_blocked': any(dc['v2_succession_blocked']),
        'contamination_occurred': (
            model.contamination_occurred
            or any(dc['v2_contamination_occurred'])
        ),
        'integrity_tamper_attempted': any(
            dc['v2_integrity_tamper_attempted']
        ),
        'attack_succeeded': _attack_success(task['vector'], model),
        'survived': final_population >= collapse_threshold,
        'collapsed': final_population < collapse_threshold,
        'extinct': final_population == 0,
        'final_population': final_population,
        'yield_condition_met_count': met,
        'yield_condition_blocked_count': blocked,
        'yield_checks': len(model.yield_event_log),
        'honest_yield_opportunities': sum(
            bool(event['honest_fires']) for event in model.yield_event_log
        ),
        'evaluated_yield_opportunities': sum(
            bool(event['fires_before_ratification'])
            for event in model.yield_event_log
        ),
        'ratified_yields': sum(
            bool(event['ratified']) for event in model.yield_event_log
        ),
        'capture_rate': blocked / met if met else 0.0,
        'max_total_suppression': (
            max(dc['total_suppression'])
            if dc['total_suppression'] else 0.0
        ),
        'min_resilience_stock': (
            min(dc['resilience_stock'])
            if dc['resilience_stock'] else model.resilience_stock
        ),
        'final_u_sys_v2': (
            dc['u_sys_v2'][-1] if dc['u_sys_v2'] else 0.0
        ),
        'elapsed_seconds': elapsed,
    }
    for key, value in task['parameters'].items():
        row[f'parameter_{key}'] = value
    return row


def _write_csv_atomic(path, rows):
    path.parent.mkdir(parents=True, exist_ok=False)
    temporary = path.with_suffix('.tmp')
    fieldnames = sorted({key for row in rows for key in row})
    with temporary.open('w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    os.replace(temporary, path)


def _sha256(path):
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def _git_value(*args):
    import subprocess

    return subprocess.check_output(
        ['git', *args], text=True, encoding='utf-8'
    ).strip()


def _write_manifest(path, args, rows, output_path, started_at, ended_at):
    manifest = {
        'schema_version': 'attack-v2-manifest-v1',
        'run_id': args.run_id,
        'vector': args.vector,
        'mode': args.mode,
        'machine': args.machine,
        'started_at_utc': started_at,
        'ended_at_utc': ended_at,
        'commit': _git_value('rev-parse', 'HEAD'),
        'branch': _git_value('branch', '--show-current'),
        'python': sys.version,
        'numpy': np.__version__,
        'platform': platform.platform(),
        'cpu_count': os.cpu_count(),
        'worker_processes': args.workers,
        'replicates': args.replicates,
        'shard_count': args.shard_count,
        'shard_index': args.shard_index,
        'row_count': len(rows),
        'output_path': str(output_path),
        'output_sha256': _sha256(output_path),
        'seed_schema': 'attack-v2-seed-v1',
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix('.tmp')
    temporary.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + '\n',
        encoding='utf-8',
    )
    os.replace(temporary, path)


def _write_status(path, args, state, detail):
    path.parent.mkdir(parents=True, exist_ok=True)
    content = (
        f'# Attack Vector v2 Revalidation Status: {args.machine}\n\n'
        f'- State: `{state}`\n'
        f'- Vector: `{args.vector}`\n'
        f'- Mode: `{args.mode}`\n'
        f'- Run ID: `{args.run_id}`\n'
        f'- Updated UTC: `{datetime.now(timezone.utc).isoformat()}`\n'
        f'- Detail: {detail}\n'
    )
    temporary = path.with_suffix('.tmp')
    temporary.write_text(content, encoding='utf-8')
    os.replace(temporary, path)


def _analytic_domain_masking_row(args):
    return {
        'schema_version': 'attack-v2-analytic-v1',
        'vector': 'domain_masking',
        'mode': args.mode,
        'machine': args.machine,
        'result_type': 'analytic_only',
        'live_simulation': False,
        'attack_succeeded': False,
        'standard_error_applicable': False,
        'reason': (
            'v2 spectral entropy leaves no non-degenerate live masking '
            'intervention under the audited architecture'
        ),
    }


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--vector', required=True, choices=ALL_VECTORS)
    parser.add_argument(
        '--mode', required=True, choices=('smoke', 'timing', 'full')
    )
    parser.add_argument(
        '--machine', required=True, choices=('laptop', 'linux')
    )
    parser.add_argument('--replicates', type=int)
    parser.add_argument('--workers', type=int)
    parser.add_argument('--run-id')
    parser.add_argument('--shard-count', type=int, default=1)
    parser.add_argument('--shard-index', type=int, default=0)
    parser.add_argument(
        '--output-root',
        default='data/attack_vector_revalidation_v2',
    )
    return parser.parse_args()


def main():
    args = parse_args()
    if args.replicates is None:
        if args.mode == 'smoke':
            args.replicates = 2
        elif args.mode == 'timing':
            args.replicates = 3
        elif args.vector == 'biological_veto_capture':
            args.replicates = 50
        else:
            args.replicates = 20
    if args.replicates < 1:
        raise SystemExit('--replicates must be positive')
    if args.shard_count < 1:
        raise SystemExit('--shard-count must be positive')
    if not 0 <= args.shard_index < args.shard_count:
        raise SystemExit('--shard-index must be in [0, shard-count)')
    if args.mode != 'full' and args.shard_count != 1:
        raise SystemExit('sharding is supported only in full mode')

    max_workers = max(1, (os.cpu_count() or 2) - 1)
    args.workers = args.workers or max_workers
    args.workers = max(1, min(args.workers, max_workers))
    args.run_id = args.run_id or (
        datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
        + f'_{args.vector}_{args.mode}'
    )

    root = Path(args.output_root) / args.machine / args.vector
    output_path = root / args.run_id / 'results.csv'
    if output_path.parent.exists():
        raise SystemExit(f'run path already exists: {output_path.parent}')

    shard_suffix = (
        f'_shard_{args.shard_index}_of_{args.shard_count}'
        if args.shard_count > 1 else ''
    )
    status_path = Path('simulation/diagnostics') / (
        f'attack_vector_revalidation_status_{args.machine}'
        f'{shard_suffix}.md'
    )
    _write_status(status_path, args, 'running', 'process started')
    started_at = datetime.now(timezone.utc).isoformat()

    try:
        if args.vector == 'domain_masking':
            rows = [_analytic_domain_masking_row(args)]
        else:
            tasks = build_tasks(
                args.vector, args.mode, args.replicates, args.machine
            )
            tasks = [
                task for task in tasks
                if task['seed'] % args.shard_count == args.shard_index
            ]
            if not tasks:
                raise RuntimeError('selected shard contains no tasks')
            if args.workers == 1:
                rows = [run_single(task) for task in tasks]
            else:
                with multiprocessing.Pool(
                    processes=args.workers, maxtasksperchild=10
                ) as pool:
                    rows = list(pool.imap_unordered(run_single, tasks))
            rows.sort(
                key=lambda row: (
                    str(row.get('defense_active')),
                    int(row.get('replicate', 0)),
                    int(row.get('seed', 0)),
                )
            )

        _write_csv_atomic(output_path, rows)
        ended_at = datetime.now(timezone.utc).isoformat()
        manifest_path = (
            output_path.parent / 'environment_manifest.json'
        )
        _write_manifest(
            manifest_path,
            args,
            rows,
            output_path,
            started_at,
            ended_at,
        )
        _write_status(
            status_path,
            args,
            'completed',
            f'{len(rows)} rows written to `{output_path}`',
        )
        print(output_path)
        print(manifest_path)
    except Exception as exc:
        _write_status(status_path, args, 'failed', repr(exc))
        raise


if __name__ == '__main__':
    multiprocessing.freeze_support()
    main()
