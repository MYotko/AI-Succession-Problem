"""Execute the frozen Sybil defense scaling characterization plan.

The default mode runs the three registered passes only when characterization
authorization is explicit. The self-check mode enumerates the registered
shapes and evaluates one n=1 fixture per pass without producing a finding.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import csv
import hashlib
import json
import math
import os
import platform
import random
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from sybil_defense_scaling import (
    attribute_validators,
    build_validator_pool,
    compute_attack_cost,
    compute_defense_cost,
    derive_two_dial_capability_terms,
    load_config,
    run_false_cluster_injection,
    run_measurement_corruption,
)


HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent
DEFAULT_CONFIG = HERE / 'config' / 'sybil_defense_scaling.json'
DESIGN_NOTE = HERE / 'diagnostics' / 'sybil_defense_scaling_design_note.md'
AUTHORIZED = 'authorized_registered_characterization'
BLOCKED = 'blocked_pending_selfcheck'
PASS_ORDER = ('ratio_collapse_slice', 'main_surface', 'complete_linkage')


@dataclass(frozen=True)
class SweepPlan:
    """Validated, fully expanded values from the registered config."""

    ratios: tuple[float, ...]
    structural_points: tuple[dict[str, Any], ...]
    n_per_cell: int
    cells: Mapping[str, tuple[dict[str, Any], ...]]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _git_value(*args: str) -> str:
    return subprocess.check_output(
        ['git', *args], cwd=REPO_ROOT, text=True, encoding='utf-8'
    ).strip()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    if hasattr(value, 'item'):
        return value.item()
    return value


def _write_text_atomic(path: Path, content: str) -> None:
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(content, encoding='utf-8')
    os.replace(temporary, path)


def _write_json_atomic(path: Path, value: Any) -> None:
    _write_text_atomic(
        path, json.dumps(_json_safe(value), indent=2, sort_keys=True) + '\n'
    )


def _write_csv_atomic(path: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    fieldnames = sorted({key for row in rows for key in row})
    temporary = path.with_suffix(path.suffix + '.tmp')
    with temporary.open('w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(
            handle, fieldnames=fieldnames, lineterminator='\n'
        )
        writer.writeheader()
        writer.writerows(_json_safe(list(rows)))
    os.replace(temporary, path)


def load_geomspace(specification: Mapping[str, Any]) -> tuple[float, ...]:
    """Expand the registered inclusive geomspace config schema."""

    if set(specification) != {'schema', 'start', 'stop', 'count'}:
        raise ValueError('capability_ratio_range has unexpected fields')
    if specification['schema'] != 'geomspace':
        raise ValueError('capability_ratio_range schema must be geomspace')
    start = float(specification['start'])
    stop = float(specification['stop'])
    count = int(specification['count'])
    if start <= 0.0 or stop <= start or count < 2:
        raise ValueError('invalid geomspace bounds or count')
    values = [
        start * (stop / start) ** (index / (count - 1))
        for index in range(count)
    ]
    values[0] = start
    values[-1] = stop
    return tuple(values)


def _structural_points(sweep: Mapping[str, Any]) -> tuple[dict[str, Any], ...]:
    axis = sweep['structural_axis']
    sizes = [int(value) for value in axis['validator_set_sizes']]
    severities = [float(value) for value in axis['collapse_severities']]
    corner = axis['institution_alone_corner']
    points: list[dict[str, Any]] = []
    for size in sizes:
        for severity in severities:
            points.append(
                {
                    'structural_point_index': len(points),
                    'validator_set_size': size,
                    'frontier_validator_count': size - 1,
                    'institution_validator_count': 1,
                    'collapse_severity': severity,
                    'institution_alone_corner': False,
                }
            )
    points.append(
        {
            'structural_point_index': len(points),
            'validator_set_size': int(corner['validator_set_size']),
            'frontier_validator_count': 0,
            'institution_validator_count': 1,
            'collapse_severity': float(corner['collapse_severity']),
            'institution_alone_corner': True,
        }
    )
    return tuple(points)


def _require_equal(actual: Any, expected: Any, label: str) -> None:
    if actual != expected:
        raise ValueError(f'{label} does not match the committed registration')


def validate_registered_plan(config: Mapping[str, Any]) -> None:
    """Reject any config drift from the final committed registration."""

    sweep = config['sweep']
    ratio_spec = sweep['capability_ratio_range']
    _require_equal(ratio_spec['schema'], 'geomspace', 'ratio schema')
    _require_equal(float(ratio_spec['start']), 0.1, 'ratio start')
    _require_equal(float(ratio_spec['stop']), 10.0, 'ratio stop')
    _require_equal(int(ratio_spec['count']), 25, 'ratio count')
    _require_equal(int(sweep['power_sample_size_per_cell']), 200, 'cell n')
    axis = sweep['structural_axis']
    _require_equal(
        [int(value) for value in axis['validator_set_sizes']],
        [2, 4, 8, 16, 32, 64],
        'validator size axis',
    )
    _require_equal(
        [float(value) for value in axis['collapse_severities']],
        [0.0, 0.33, 0.66, 1.0],
        'collapse severity axis',
    )
    _require_equal(
        dict(axis['institution_alone_corner']),
        {'validator_set_size': 1, 'collapse_severity': 1.0},
        'institution-only corner',
    )
    _require_equal(float(config['attribution']['similarity_threshold']), 0.9,
                   'merge threshold')
    main = sweep['main_surface']
    _require_equal(
        list(main['arms']),
        ['false_cluster_injection', 'measurement_corruption'],
        'main arms',
    )
    _require_equal(
        list(main['defense_cost_models']),
        ['pairwise_exact', 'static_baseline'],
        'main defense costs',
    )
    _require_equal(
        list(main['attack_cost_models']),
        ['linear', 'superlinear'],
        'main attack costs',
    )
    _require_equal(main['merge_rule'], 'threshold_connected_components',
                   'main merge rule')
    _require_equal(main['absolute_term_enabled'], False,
                   'main absolute term')
    ratio_slice = sweep['ratio_collapse_slice']
    _require_equal(ratio_slice['arm'], 'false_cluster_injection',
                   'ratio slice arm')
    _require_equal(ratio_slice['defense_cost_model'], 'pairwise_exact',
                   'ratio slice defense cost')
    _require_equal(ratio_slice['attack_cost_model'], 'linear',
                   'ratio slice attack cost')
    _require_equal(
        ratio_slice['merge_rule'], 'threshold_connected_components',
        'ratio slice merge rule',
    )
    _require_equal(
        [float(value) for value in ratio_slice['parity_levels']],
        [0.316, 1.0, 3.16],
        'ratio slice levels',
    )
    _require_equal(ratio_slice['absolute_term_enabled'], True,
                   'ratio slice absolute term')
    _require_equal(float(ratio_slice['failure_rate_mei']), 0.15,
                   'ratio slice MEI')
    term = config['two_dial_capability']['absolute_resolution_term']
    _require_equal(term['form'], 'defender_power_law_resolution',
                   'absolute term form')
    _require_equal(float(term['reference_level']), 1.0,
                   'absolute term reference')
    _require_equal(float(term['strength']), 0.22163300225716118,
                   'absolute term strength')
    complete = sweep['complete_linkage_sensitivity']
    _require_equal(complete['arm'], 'false_cluster_injection',
                   'complete-linkage arm')
    _require_equal(
        list(complete['defense_cost_models']),
        ['pairwise_exact', 'static_baseline'],
        'complete-linkage defense costs',
    )
    _require_equal(
        list(complete['attack_cost_models']),
        ['linear', 'superlinear'],
        'complete-linkage attack costs',
    )
    _require_equal(float(complete['capability_ratio']), 1.0,
                   'complete-linkage ratio')
    _require_equal(
        complete['merge_rule'], 'threshold_greedy_complete_linkage',
        'complete-linkage merge rule',
    )
    if any(value is None for value in _walk_values(sweep)):
        raise ValueError('analysis-plan field in sweep config is null')


def _walk_values(value: Any) -> Iterable[Any]:
    if isinstance(value, Mapping):
        for child in value.values():
            yield from _walk_values(child)
    elif isinstance(value, (list, tuple)):
        for child in value:
            yield from _walk_values(child)
    else:
        yield value


def build_sweep_plan(config: Mapping[str, Any]) -> SweepPlan:
    """Validate and enumerate all three registered characterization passes."""

    validate_registered_plan(config)
    sweep = config['sweep']
    ratios = load_geomspace(sweep['capability_ratio_range'])
    structural = _structural_points(sweep)
    main_spec = sweep['main_surface']
    main: list[dict[str, Any]] = []
    for point in structural:
        for ratio in ratios:
            for arm in main_spec['arms']:
                for defense_model in main_spec['defense_cost_models']:
                    for attack_model in main_spec['attack_cost_models']:
                        main.append(
                            {
                                **point,
                                'pass_name': 'main_surface',
                                'arm': arm,
                                'defense_cost_model': defense_model,
                                'attack_cost_model': attack_model,
                                'merge_rule': main_spec['merge_rule'],
                                'attacker_capability': ratio,
                                'defender_capability': 1.0,
                                'capability_ratio': ratio,
                                'absolute_term_enabled': False,
                            }
                        )
    ratio_spec = sweep['ratio_collapse_slice']
    ratio_slice: list[dict[str, Any]] = []
    for point in structural:
        for level in ratio_spec['parity_levels']:
            ratio_slice.append(
                {
                    **point,
                    'pass_name': 'ratio_collapse_slice',
                    'arm': ratio_spec['arm'],
                    'defense_cost_model': ratio_spec['defense_cost_model'],
                    'attack_cost_model': ratio_spec['attack_cost_model'],
                    'merge_rule': ratio_spec['merge_rule'],
                    'attacker_capability': float(level),
                    'defender_capability': float(level),
                    'capability_ratio': 1.0,
                    'absolute_term_enabled': True,
                }
            )
    complete_spec = sweep['complete_linkage_sensitivity']
    complete: list[dict[str, Any]] = []
    for point in structural:
        for defense_model in complete_spec['defense_cost_models']:
            for attack_model in complete_spec['attack_cost_models']:
                complete.append(
                    {
                        **point,
                        'pass_name': 'complete_linkage',
                        'arm': complete_spec['arm'],
                        'defense_cost_model': defense_model,
                        'attack_cost_model': attack_model,
                        'merge_rule': complete_spec['merge_rule'],
                        'attacker_capability': 1.0,
                        'defender_capability': 1.0,
                        'capability_ratio': 1.0,
                        'absolute_term_enabled': False,
                    }
                )
    cells = {
        'main_surface': tuple(main),
        'ratio_collapse_slice': tuple(ratio_slice),
        'complete_linkage': tuple(complete),
    }
    counts = {name: len(selected) for name, selected in cells.items()}
    _require_equal(counts['main_surface'], 5000, 'main cell count')
    _require_equal(counts['ratio_collapse_slice'], 75,
                   'ratio slice cell count')
    _require_equal(counts['complete_linkage'], 100,
                   'complete-linkage cell count')
    return SweepPlan(
        ratios=ratios,
        structural_points=structural,
        n_per_cell=int(sweep['power_sample_size_per_cell']),
        cells=cells,
    )


def assert_characterization_authorized(config: Mapping[str, Any]) -> None:
    if config['sweep']['authorization'] != AUTHORIZED:
        raise RuntimeError(
            'full characterization refused: authorization is not '
            f'{AUTHORIZED}'
        )


def _seed(cell: Mapping[str, Any], replicate: int) -> int:
    payload = json.dumps(
        {
            'schema': 'sybil-characterization-seed-v1',
            'cell': dict(cell),
            'replicate': int(replicate),
        },
        sort_keys=True,
        separators=(',', ':'),
    )
    return int.from_bytes(
        hashlib.sha256(payload.encode('utf-8')).digest()[:8], 'big'
    ) % (2**31 - 1)


def _cell_id(cell: Mapping[str, Any]) -> str:
    payload = json.dumps(dict(cell), sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(payload.encode('utf-8')).hexdigest()[:20]


def run_cell(
    cell: Mapping[str, Any], config: Mapping[str, Any], n: int
) -> dict[str, Any]:
    """Evaluate one fixed registered cell and return sufficient counts."""

    started = time.perf_counter()
    attribution_config = dict(config['attribution'])
    attribution_config['merge_rule'] = str(cell['merge_rule'])
    validators = build_validator_pool(
        int(cell['frontier_validator_count']),
        int(cell['institution_validator_count']),
        config['collapse'],
        lineage_mode='distinct',
    )
    attribution = attribute_validators(
        validators, float(cell['collapse_severity']), attribution_config
    )
    forged_count = int(
        config['attack_arms']['false_cluster_injection']['forged_cluster_count']
    )
    defense_inputs = len(validators)
    if (
        cell['arm'] == 'false_cluster_injection'
        and config['costs']['defense']['input_basis'] == 'apparent_inputs'
    ):
        defense_inputs += forged_count
    defense = compute_defense_cost(
        defense_inputs,
        config['costs']['defense'],
        float(config['defender_capability']['exponent_reduction']),
        model=str(cell['defense_cost_model']),
    )
    attack = compute_attack_cost(
        attribution.effective_rank,
        config['costs']['attack'],
        model=str(cell['attack_cost_model']),
    )
    base_resolution = float(config['defender_capability']['base_resolution']) * float(
        config['defender_capability']['resolution_improvement']
    )
    terms = derive_two_dial_capability_terms(
        attacker_capability=float(cell['attacker_capability']),
        defender_capability=float(cell['defender_capability']),
        base_resolution_power=base_resolution,
        two_dial_config=config['two_dial_capability'],
        absolute_term_enabled=bool(cell['absolute_term_enabled']),
    )
    minimum_rank = int(config['poles']['deployment_minimum_rank'])
    failures = 0
    rank_visible_failures = 0
    partition_corruptions = 0
    institution_hidden = 0
    measured_rank_sum = 0
    resolution_probability = 0.0
    identifier = _cell_id(cell)
    for replicate in range(int(n)):
        rng = random.Random(_seed(cell, replicate))
        if cell['arm'] == 'false_cluster_injection':
            result = run_false_cluster_injection(
                attribution,
                validators,
                forged_cluster_count=forged_count,
                capability_ratio=terms.capability_ratio,
                resolution_power=terms.effective_resolution_power,
                defense_cost=defense.effective_cost,
                attack_cost=attack.cost,
                minimum_consensus_rank=minimum_rank,
                rng=rng,
            )
        elif cell['arm'] == 'measurement_corruption':
            result = run_measurement_corruption(
                validators,
                attribution,
                collapse_severity=float(cell['collapse_severity']),
                attribution_config=attribution_config,
                arm_config=config['attack_arms']['measurement_corruption'],
                capability_ratio=terms.capability_ratio,
                resolution_power=terms.effective_resolution_power,
                defense_cost=defense.effective_cost,
                attack_cost=attack.cost,
                minimum_consensus_rank=minimum_rank,
                rng=rng,
            )
        else:
            raise ValueError('unsupported attack arm')
        partition_corrupted = not bool(result.details['partition_preserved'])
        failures += int(result.defense_failed)
        partition_corruptions += int(partition_corrupted)
        rank_visible_failures += int(
            partition_corrupted and result.measured_rank < minimum_rank
        )
        institution_hidden += int(not result.institution_visible)
        measured_rank_sum += int(result.measured_rank)
        resolution_probability = float(result.resolution_probability)
    elapsed = time.perf_counter() - started
    return {
        'cell_id': identifier,
        **dict(cell),
        'n': int(n),
        'true_effective_rank': attribution.effective_rank,
        'failure_count': failures,
        'failure_rate': failures / int(n),
        'rank_visible_failure_count': rank_visible_failures,
        'rank_visible_failure_rate': rank_visible_failures / int(n),
        'partition_corruption_count': partition_corruptions,
        'partition_corruption_rate': partition_corruptions / int(n),
        'institution_hidden_count': institution_hidden,
        'institution_hidden_rate': institution_hidden / int(n),
        'mean_measured_rank': measured_rank_sum / int(n),
        'resolution_probability': resolution_probability,
        'absolute_resolution_multiplier': terms.absolute_resolution_multiplier,
        'defense_input_count': defense_inputs,
        'pairwise_checks': defense.pairwise_checks,
        'effective_defense_cost': defense.effective_cost,
        'effective_attack_cost': attack.cost,
        'elapsed_seconds': elapsed,
        'mean_seconds_per_run': elapsed / int(n),
    }


class ProgressLog:
    """Line-buffered progress record with observed-rate ETA."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.handle = path.open('w', encoding='utf-8', buffering=1)

    def write(self, event: str, **fields: Any) -> None:
        tokens = [f'timestamp={_utc_now()}', f'event={event}']
        tokens.extend(f'{key}={value}' for key, value in fields.items())
        self.handle.write(' '.join(tokens) + '\n')
        self.handle.flush()

    def close(self) -> None:
        self.handle.close()


def _execute_pass(
    pass_name: str,
    cells: Sequence[Mapping[str, Any]],
    config: Mapping[str, Any],
    n: int,
    workers: int,
    progress: ProgressLog,
) -> tuple[list[dict[str, Any]], float]:
    started = time.perf_counter()
    total = len(cells)
    progress.write(
        'pass_start', pass_name=pass_name, cells_total=total,
        runs_total=total * n,
    )
    results: list[dict[str, Any]] = []
    last_log_time = started
    last_log_count = 0
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(run_cell, cell, config, n) for cell in cells]
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())
            completed = len(results)
            now = time.perf_counter()
            if (
                completed == total
                or (now - last_log_time >= 3.0 and completed - last_log_count >= 10)
            ):
                elapsed = now - started
                mean_seconds = elapsed / completed
                remaining = mean_seconds * (total - completed)
                progress.write(
                    'status',
                    pass_name=pass_name,
                    cells_completed=completed,
                    cells_total=total,
                    runs_completed=completed * n,
                    runs_total=total * n,
                    percent=f'{100.0 * completed / total:.6f}',
                    elapsed_seconds=f'{elapsed:.6f}',
                    mean_seconds_per_cell=f'{mean_seconds:.9f}',
                    eta_seconds_observed_wall_rate=f'{remaining:.6f}',
                )
                last_log_time = now
                last_log_count = completed
    elapsed = time.perf_counter() - started
    results.sort(key=lambda row: row['cell_id'])
    progress.write(
        'pass_finish', pass_name=pass_name, cells_completed=total,
        runs_completed=total * n, elapsed_seconds=f'{elapsed:.6f}',
    )
    return results, elapsed


def _planned_counts(plan: SweepPlan) -> dict[str, dict[str, int]]:
    return {
        name: {'cells': len(plan.cells[name]), 'runs': len(plan.cells[name]) * plan.n_per_cell}
        for name in PASS_ORDER
    }


def _preflight_committed_inputs(config_path: Path) -> None:
    for path in (config_path, DESIGN_NOTE):
        relative = path.relative_to(REPO_ROOT)
        result = subprocess.run(
            ['git', 'diff', '--quiet', 'HEAD', '--', str(relative)],
            cwd=REPO_ROOT,
        )
        if result.returncode != 0:
            raise RuntimeError(f'working tree differs from HEAD: {relative}')


def run_characterization(
    config: Mapping[str, Any], config_path: Path, workers: int
) -> Path:
    assert_characterization_authorized(config)
    _preflight_committed_inputs(config_path)
    plan = build_sweep_plan(config)
    run_id = str(config['sweep']['run_id'])
    prefix = str(config['outputs']['authoritative_run_prefix'])
    if not run_id.startswith(prefix):
        raise RuntimeError('authoritative run ID does not carry committed prefix')
    output_dir = REPO_ROOT / config['outputs']['root'] / run_id
    if output_dir.exists():
        raise RuntimeError(f'characterization output already exists: {output_dir}')
    output_dir.mkdir(parents=True)
    progress_path = output_dir / 'sweep_progress.log'
    print(f'Progress log: {progress_path}', flush=True)
    progress = ProgressLog(progress_path)
    head = _git_value('rev-parse', 'HEAD')
    counts = _planned_counts(plan)
    total_started = time.perf_counter()
    progress.write(
        'startup', run_id=run_id, git_head=head, worker_count=workers,
        main_cells=counts['main_surface']['cells'],
        main_runs=counts['main_surface']['runs'],
        ratio_collapse_cells=counts['ratio_collapse_slice']['cells'],
        ratio_collapse_runs=counts['ratio_collapse_slice']['runs'],
        complete_linkage_cells=counts['complete_linkage']['cells'],
        complete_linkage_runs=counts['complete_linkage']['runs'],
        pass_executing=PASS_ORDER[0], eta_basis='observed_wall_clock_per_cell',
    )
    artifacts: list[Path] = []
    pass_timings: dict[str, float] = {}
    try:
        for pass_name in PASS_ORDER:
            rows, elapsed = _execute_pass(
                pass_name, plan.cells[pass_name], config, plan.n_per_cell,
                workers, progress,
            )
            pass_timings[pass_name] = elapsed
            artifact = output_dir / f'{prefix}{pass_name}_results.csv'
            _write_csv_atomic(artifact, rows)
            artifacts.append(artifact)
        total_elapsed = time.perf_counter() - total_started
        manifest_path = output_dir / f'{prefix}manifest.json'
        manifest = {
            'schema': 'sybil-characterization-manifest-v1',
            'run_id': run_id,
            'created_utc': _utc_now(),
            'git_head': head,
            'worker_count': workers,
            'python_version': platform.python_version(),
            'config_path': str(config_path.relative_to(REPO_ROOT)),
            'config_sha256': _sha256(config_path),
            'design_note_path': str(DESIGN_NOTE.relative_to(REPO_ROOT)),
            'design_note_sha256': _sha256(DESIGN_NOTE),
            'seed_schema': 'sybil-characterization-seed-v1',
            'n_per_cell': plan.n_per_cell,
            'planned_counts': counts,
            'completed_counts': counts,
            'pass_timings_seconds': pass_timings,
            'total_cells': sum(item['cells'] for item in counts.values()),
            'total_runs': sum(item['runs'] for item in counts.values()),
            'total_elapsed_seconds': total_elapsed,
            'authoritative_artifacts': [
                {
                    'path': str(path.relative_to(REPO_ROOT)),
                    'sha256': _sha256(path),
                    'rows': len(plan.cells[path.stem[len(prefix):-len('_results')]]),
                }
                for path in artifacts
            ],
            'excluded_process_artifacts': [
                str(progress_path.relative_to(REPO_ROOT))
            ],
            'selection_rule': 'read authoritative_artifacts exactly; never glob',
            'status': 'complete',
        }
        _write_json_atomic(manifest_path, manifest)
        progress.write(
            'completion', total_elapsed_seconds=f'{total_elapsed:.6f}',
            total_runs=manifest['total_runs'],
            output_paths=','.join(str(path) for path in artifacts),
            manifest_path=manifest_path,
        )
        return manifest_path
    finally:
        progress.close()


def run_selfcheck(config: Mapping[str, Any], config_path: Path) -> Path:
    """Verify registered shape and blocked authorization with tiny fixtures."""

    plan = build_sweep_plan(config)
    if config['sweep']['authorization'] != BLOCKED:
        raise RuntimeError('self-check must run while authorization is blocked')
    refusal = False
    refusal_message = ''
    try:
        assert_characterization_authorized(config)
    except RuntimeError as error:
        refusal = True
        refusal_message = str(error)
    if not refusal:
        raise RuntimeError('full characterization was not refused')
    tiny_n = int(config['sweep']['selfcheck']['tiny_n'])
    _require_equal(tiny_n, 1, 'self-check tiny n')
    fixtures = {
        pass_name: run_cell(plan.cells[pass_name][0], config, tiny_n)
        for pass_name in PASS_ORDER
    }
    counts = _planned_counts(plan)
    run_id = str(config['sweep']['selfcheck']['run_id'])
    prefix = str(config['outputs']['selfcheck_run_prefix'])
    if not run_id.startswith(prefix):
        raise RuntimeError('self-check run ID does not carry selfcheck prefix')
    output_dir = REPO_ROOT / config['outputs']['root'] / run_id
    if output_dir.exists():
        raise RuntimeError(f'self-check output already exists: {output_dir}')
    output_dir.mkdir(parents=True)
    evidence_path = output_dir / 'selfcheck_evidence.json'
    manifest_path = output_dir / 'selfcheck_manifest.json'
    evidence = {
        'schema': 'sybil-characterization-selfcheck-v1',
        'created_utc': _utc_now(),
        'config_path': str(config_path.relative_to(REPO_ROOT)),
        'authorization_seen': config['sweep']['authorization'],
        'blocked_authorization_refusal_confirmed': refusal,
        'refusal_message': refusal_message,
        'registered_fields_read': {
            'capability_ratio_range': config['sweep']['capability_ratio_range'],
            'expanded_ratio_count': len(plan.ratios),
            'expanded_ratio_first': plan.ratios[0],
            'expanded_ratio_last': plan.ratios[-1],
            'validator_set_sizes': config['sweep']['structural_axis']['validator_set_sizes'],
            'collapse_severities': config['sweep']['structural_axis']['collapse_severities'],
            'power_sample_size_per_cell': plan.n_per_cell,
        },
        'planned_counts': counts,
        'total_cells': sum(item['cells'] for item in counts.values()),
        'total_runs_at_registered_n': sum(item['runs'] for item in counts.values()),
        'tiny_fixture_n': tiny_n,
        'tiny_fixtures_executed': fixtures,
        'finding_computed': False,
        'authoritative_manifest_written': False,
        'passed': True,
    }
    _write_json_atomic(evidence_path, evidence)
    manifest = {
        'schema': 'sybil-characterization-selfcheck-manifest-v1',
        'run_id': run_id,
        'git_head': _git_value('rev-parse', 'HEAD'),
        'config_sha256': _sha256(config_path),
        'non_authoritative': True,
        'prefix_exclusion': prefix,
        'artifacts': [
            {
                'path': str(evidence_path.relative_to(REPO_ROOT)),
                'sha256': _sha256(evidence_path),
            }
        ],
        'authoritative_artifacts': [],
        'passed': True,
    }
    _write_json_atomic(manifest_path, manifest)
    print(json.dumps(evidence['planned_counts'], sort_keys=True))
    print(f'Self-check evidence: {evidence_path}')
    print('Blocked authorization refusal: confirmed')
    return manifest_path


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=Path, default=DEFAULT_CONFIG)
    parser.add_argument('--workers', type=int, default=max(1, os.cpu_count() or 1))
    parser.add_argument('--self-check', action='store_true')
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    if args.workers < 1:
        raise ValueError('workers must be positive')
    config_path = args.config.resolve()
    config = load_config(config_path)
    if args.self_check:
        run_selfcheck(config, config_path)
    else:
        manifest = run_characterization(config, config_path, args.workers)
        print(f'Authoritative manifest: {manifest}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
