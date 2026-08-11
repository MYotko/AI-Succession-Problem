"""Run the authorized Sybil scaling instrument-validation smoke.

This entry point cannot run a rank-by-ratio sweep. It requires the full-sweep
authorization, capability-ratio range, and power sample size to remain unset.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import platform
import random
import statistics
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping

from run_attack_vector_revalidation_v2 import (
    LIVE_VECTORS,
    _full_cells,
    build_tasks,
    deterministic_seed,
    run_single,
)
from sybil_defense_scaling import (
    AttackResult,
    attribute_validators,
    build_validator_pool,
    compute_attack_cost,
    compute_defense_cost,
    load_config,
    run_false_cluster_injection,
    run_measurement_corruption,
)


HERE = Path(__file__).resolve().parent
DEFAULT_CONFIG = HERE / 'config' / 'sybil_defense_scaling.json'


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _git_value(*args: str) -> str:
    return subprocess.check_output(
        ['git', *args], text=True, encoding='utf-8'
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


def _write_csv_atomic(path: Path, rows: list[dict[str, Any]]) -> None:
    fieldnames = sorted({key for row in rows for key in row})
    temporary = path.with_suffix('.tmp')
    with temporary.open('w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(_json_safe(rows))
    os.replace(temporary, path)


def _assert_smoke_boundary(config: Mapping[str, Any]) -> None:
    if config['smoke']['authorization'] != 'instrument_validation_only':
        raise RuntimeError('smoke authorization is not instrument-validation only')
    sweep = config['sweep']
    if sweep['authorization'] != 'blocked_pending_registration':
        raise RuntimeError('full-sweep authorization must remain blocked')
    if sweep['capability_ratio_range'] is not None:
        raise RuntimeError('smoke must not use a capability-ratio range')
    if sweep['power_sample_size_per_cell'] is not None:
        raise RuntimeError('smoke must not assume a powered sample size')


def _validated_path_probe(config: Mapping[str, Any]) -> tuple[list[dict[str, Any]], bool]:
    vector = str(config['scenario']['existing_vector'])
    if vector not in LIVE_VECTORS:
        raise RuntimeError(f'existing scenario is not registered: {vector}')
    cells = _full_cells(vector)
    tasks = build_tasks(vector, 'smoke', 1, 'linux')
    rows: list[dict[str, Any]] = []
    for task in tasks:
        row = run_single(task)
        rows.append(
            {
                'record_type': 'validated_path_probe',
                'vector': vector,
                'population': task['parameters']['population'],
                'defense_active': task['parameters']['defense_active'],
                'seed': task['seed'],
                'attack_succeeded': bool(row['attack_succeeded']),
                'defense_fired': bool(row['defense_fired']),
                'is_v2_mode': bool(row['is_v2_mode']),
                'elapsed_seconds': float(row['elapsed_seconds']),
            }
        )
    paired_seed = len({row['seed'] for row in rows}) == 1
    expected_outcomes = (
        any(row['attack_succeeded'] for row in rows if not row['defense_active'])
        and all(not row['attack_succeeded'] for row in rows if row['defense_active'])
    )
    registered_populations = sorted({cell['population'] for cell in cells})
    grid_matches = (
        bool(registered_populations)
        and all(
            {cell['defense_active'] for cell in cells if cell['population'] == population}
            == {False, True}
            for population in registered_populations
        )
    )
    return rows, paired_seed and expected_outcomes and grid_matches


def _cost_records(config: Mapping[str, Any]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    counts = [int(value) for value in config['smoke']['cost_validator_counts']]
    exponent_reduction = float(
        config['defender_capability']['exponent_reduction']
    )
    for model in ('pairwise_exact', 'static_baseline'):
        for count in counts:
            result = compute_defense_cost(
                count,
                config['costs']['defense'],
                exponent_reduction,
                model=model,
            )
            records.append(
                {
                    'record_type': 'cost_scaling',
                    'defense_cost_model': result.model,
                    'validator_count': result.validator_count,
                    'pairwise_checks': result.pairwise_checks,
                    'raw_defense_cost': result.raw_cost,
                    'structured_efficiency': result.structured_efficiency,
                    'effective_defense_cost': result.effective_cost,
                    'exponent_reduction': result.exponent_reduction,
                    'effective_exponent': result.effective_exponent,
                }
            )
    return records


def _attribution_record(
    config: Mapping[str, Any],
    label: str,
    *,
    frontier_count: int,
    institution_count: int,
    severity: float,
    lineage_mode: str,
) -> dict[str, Any]:
    validators = build_validator_pool(
        frontier_count,
        institution_count,
        config['collapse'],
        lineage_mode=lineage_mode,
    )
    result = attribute_validators(validators, severity, config['attribution'])
    return {
        'record_type': 'attribution_validation',
        'case': label,
        'frontier_validator_count': frontier_count,
        'institution_validator_count': institution_count,
        'validator_count': len(validators),
        'lineage_mode': lineage_mode,
        'collapse_severity': severity,
        'effective_rank': result.effective_rank,
        'pairwise_checks': result.pairwise_checks,
        'clusters': json.dumps(result.clusters),
        'retained_diversity': json.dumps(dict(result.retained_diversity)),
    }


def _attribution_records(config: Mapping[str, Any]) -> list[dict[str, Any]]:
    count = int(config['smoke']['frontier_validator_count'])
    minimum = float(config['collapse']['severity_min'])
    maximum = float(config['collapse']['severity_max'])
    analytic = config['floor']['analytic_corner']
    return [
        _attribution_record(
            config,
            'six_distinct_no_collapse',
            frontier_count=count,
            institution_count=0,
            severity=minimum,
            lineage_mode='distinct',
        ),
        _attribution_record(
            config,
            'six_correlated_no_collapse',
            frontier_count=count,
            institution_count=0,
            severity=minimum,
            lineage_mode='shared',
        ),
        _attribution_record(
            config,
            'six_distinct_maximum_collapse',
            frontier_count=count,
            institution_count=0,
            severity=maximum,
            lineage_mode='distinct',
        ),
        _attribution_record(
            config,
            'maximum_collapse_with_institution',
            frontier_count=count,
            institution_count=1,
            severity=maximum,
            lineage_mode='distinct',
        ),
        _attribution_record(
            config,
            'analytic_institution_alone',
            frontier_count=int(analytic['frontier_validator_count']),
            institution_count=int(analytic['institution_validator_count']),
            severity=maximum,
            lineage_mode='distinct',
        ),
    ]


def _run_arm_scenario(
    config: Mapping[str, Any],
    *,
    scenario_label: str,
    arm_name: str,
    frontier_count: int,
    institution_count: int,
    collapse_severity: float,
    capability_ratio: float,
    replicates: int,
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    capability = config['defender_capability']
    arm_a = config['attack_arms']['false_cluster_injection']
    resolution_power = (
        float(capability['base_resolution'])
        * float(capability['resolution_improvement'])
    )
    minimum_rank = int(config['poles']['deployment_minimum_rank'])

    for replicate in range(replicates):
        seed_parameters = {
            'arm': arm_name,
            'scenario_label': scenario_label,
            'frontier_count': frontier_count,
            'institution_count': institution_count,
            'collapse_severity': collapse_severity,
            'capability_ratio_fixture': capability_ratio,
        }
        seed = deterministic_seed(
            str(config['scenario']['existing_vector']),
            seed_parameters,
            replicate,
        )
        rng = random.Random(seed)
        started = time.perf_counter_ns()
        validators = build_validator_pool(
            frontier_count,
            institution_count,
            config['collapse'],
            lineage_mode='distinct',
        )
        attribution = attribute_validators(
            validators, collapse_severity, config['attribution']
        )
        forged_count = int(arm_a['forged_cluster_count'])
        defense_input_count = len(validators)
        if (
            arm_name == 'false_cluster_injection'
            and config['costs']['defense']['input_basis'] == 'apparent_inputs'
        ):
            defense_input_count += forged_count
        defense_cost = compute_defense_cost(
            defense_input_count,
            config['costs']['defense'],
            float(capability['exponent_reduction']),
        )
        attack_cost = compute_attack_cost(
            attribution.effective_rank, config['costs']['attack']
        )

        result: AttackResult
        if arm_name == 'false_cluster_injection':
            result = run_false_cluster_injection(
                attribution,
                validators,
                forged_cluster_count=forged_count,
                capability_ratio=capability_ratio,
                resolution_power=resolution_power,
                defense_cost=defense_cost.effective_cost,
                attack_cost=attack_cost.cost,
                minimum_consensus_rank=minimum_rank,
                rng=rng,
            )
        elif arm_name == 'measurement_corruption':
            result = run_measurement_corruption(
                validators,
                attribution,
                collapse_severity=collapse_severity,
                attribution_config=config['attribution'],
                arm_config=config['attack_arms']['measurement_corruption'],
                capability_ratio=capability_ratio,
                resolution_power=resolution_power,
                defense_cost=defense_cost.effective_cost,
                attack_cost=attack_cost.cost,
                minimum_consensus_rank=minimum_rank,
                rng=rng,
            )
        else:
            raise ValueError(f'unsupported arm: {arm_name}')
        elapsed_seconds = (time.perf_counter_ns() - started) / 1_000_000_000

        record = {
            'record_type': 'arm_run',
            'scenario_label': scenario_label,
            'arm': result.arm,
            'replicate': replicate,
            'seed': seed,
            'frontier_validator_count': frontier_count,
            'institution_validator_count': institution_count,
            'validator_count': len(validators),
            'defense_input_count': defense_input_count,
            'collapse_severity': collapse_severity,
            'capability_ratio_fixture': capability_ratio,
            'true_rank': result.true_rank,
            'measured_rank': result.measured_rank,
            'rank_error': result.measured_rank - result.true_rank,
            'defense_failed': result.defense_failed,
            'institution_visible': result.institution_visible,
            'resolution_probability': result.resolution_probability,
            'defense_cost_model': defense_cost.model,
            'pairwise_checks': defense_cost.pairwise_checks,
            'raw_defense_cost': defense_cost.raw_cost,
            'structured_efficiency': defense_cost.structured_efficiency,
            'effective_defense_cost': defense_cost.effective_cost,
            'exponent_reduction': defense_cost.exponent_reduction,
            'resolution_improvement': capability['resolution_improvement'],
            'attack_cost_model': attack_cost.model,
            'attack_cost_exponent': attack_cost.exponent,
            'attack_cost': attack_cost.cost,
            'elapsed_seconds': elapsed_seconds,
        }
        record.update(result.details)
        records.append(record)
    return records


def _arm_records(config: Mapping[str, Any]) -> list[dict[str, Any]]:
    smoke = config['smoke']
    maximum = float(config['collapse']['severity_max'])
    nominal_ratio = float(smoke['nominal_capability_ratio_fixture'])
    high_ratio = float(smoke['far_above_capability_ratio_fixture'])
    nominal_replicates = int(smoke['nominal_replicates_per_arm'])
    control_replicates = int(smoke['positive_control_replicates_per_arm'])
    primary = config['floor']['primary_composition']
    no_institution = config['floor']['no_institution_control']
    records: list[dict[str, Any]] = []

    for arm_name in ('false_cluster_injection', 'measurement_corruption'):
        records.extend(
            _run_arm_scenario(
                config,
                scenario_label='nominal_maximum_collapse_with_institution',
                arm_name=arm_name,
                frontier_count=int(primary['frontier_validator_count']),
                institution_count=int(primary['institution_validator_count']),
                collapse_severity=maximum,
                capability_ratio=nominal_ratio,
                replicates=nominal_replicates,
            )
        )
        records.extend(
            _run_arm_scenario(
                config,
                scenario_label='positive_control_high_attacker',
                arm_name=arm_name,
                frontier_count=int(primary['frontier_validator_count']),
                institution_count=int(primary['institution_validator_count']),
                collapse_severity=maximum,
                capability_ratio=high_ratio,
                replicates=control_replicates,
            )
        )
        records.extend(
            _run_arm_scenario(
                config,
                scenario_label='positive_control_rank_one_no_institution',
                arm_name=arm_name,
                frontier_count=int(no_institution['frontier_validator_count']),
                institution_count=int(no_institution['institution_validator_count']),
                collapse_severity=maximum,
                capability_ratio=nominal_ratio,
                replicates=control_replicates,
            )
        )
    return records


def _sample_variance(values: Iterable[float]) -> float:
    sequence = [float(value) for value in values]
    return statistics.variance(sequence) if len(sequence) > 1 else 0.0


def _variance_estimates(arm_rows: list[dict[str, Any]]) -> dict[str, Any]:
    estimates: dict[str, Any] = {}
    nominal = [
        row for row in arm_rows
        if row['scenario_label'] == 'nominal_maximum_collapse_with_institution'
    ]
    for arm in ('false_cluster_injection', 'measurement_corruption'):
        rows = [row for row in nominal if row['arm'] == arm]
        failures = [int(row['defense_failed']) for row in rows]
        rank_errors = [float(row['rank_error']) for row in rows]
        estimates[arm] = {
            'n': len(rows),
            'defense_failure_mean': statistics.mean(failures),
            'defense_failure_sample_variance': _sample_variance(failures),
            'rank_error_mean': statistics.mean(rank_errors),
            'rank_error_sample_variance': _sample_variance(rank_errors),
        }
    return estimates


def _timing_projection(
    config: Mapping[str, Any], arm_rows: list[dict[str, Any]]
) -> dict[str, Any]:
    timings = sorted(float(row['elapsed_seconds']) for row in arm_rows)
    p95_index = max(0, math.ceil(0.95 * len(timings)) - 1)
    p95 = timings[p95_index]
    candidate = config['sweep']['candidate_resolution']
    cell_count = math.prod(int(value) for value in candidate.values())
    seconds_per_replicate_layer = p95 * cell_count
    return {
        'timed_run_count': len(timings),
        'minimum_seconds': min(timings),
        'mean_seconds': statistics.mean(timings),
        'median_seconds': statistics.median(timings),
        'p95_seconds': p95,
        'maximum_seconds': max(timings),
        'candidate_resolution': dict(candidate),
        'candidate_cell_count': cell_count,
        'projected_seconds_per_replicate_layer': seconds_per_replicate_layer,
        'projected_core_hours_per_replicate_layer': (
            seconds_per_replicate_layer / 3600.0
        ),
        'projection_formula': (
            f'{seconds_per_replicate_layer:.9f} seconds times the future '
            'operator-set powered replicates per cell'
        ),
    }


def _gate_results(
    config: Mapping[str, Any],
    cost_rows: list[dict[str, Any]],
    attribution_rows: list[dict[str, Any]],
    arm_rows: list[dict[str, Any]],
    validated_path_passed: bool,
) -> dict[str, Any]:
    pairwise = [
        row for row in cost_rows if row['defense_cost_model'] == 'pairwise_exact'
    ]
    static = [
        row for row in cost_rows if row['defense_cost_model'] == 'static_baseline'
    ]
    expected_checks = [
        row['validator_count'] * (row['validator_count'] - 1) // 2
        for row in pairwise
    ]
    pairwise_coefficient = float(
        config['costs']['defense']['models']['pairwise_exact'][
            'per_comparison_cost'
        ]
    )
    expected_costs = [
        pairwise_coefficient * checks for checks in expected_checks
    ]
    gate_a = (
        [row['pairwise_checks'] for row in pairwise] == expected_checks
        and [row['effective_defense_cost'] for row in pairwise] == expected_costs
        and len({row['effective_defense_cost'] for row in static}) == 1
    )

    ranks = {row['case']: row['effective_rank'] for row in attribution_rows}
    frontier_count = int(config['smoke']['frontier_validator_count'])
    floor_rank = int(config['poles']['deployment_minimum_rank'])
    analytic_rank = int(config['poles']['analytic_floor_rank'])
    gate_b = (
        ranks['six_distinct_no_collapse'] == frontier_count
        and ranks['six_correlated_no_collapse'] == 1
        and ranks['six_distinct_maximum_collapse'] == 1
        and ranks['maximum_collapse_with_institution'] == floor_rank
        and ranks['analytic_institution_alone'] == analytic_rank
    )

    nominal_a = [
        row for row in arm_rows
        if row['scenario_label'] == 'nominal_maximum_collapse_with_institution'
        and row['arm'] == 'false_cluster_injection'
    ]
    nominal_b = [
        row for row in arm_rows
        if row['scenario_label'] == 'nominal_maximum_collapse_with_institution'
        and row['arm'] == 'measurement_corruption'
    ]
    gate_c = (
        all(row['partition_preserved'] for row in nominal_a)
        and any(row['false_clusters_surviving'] > 0 for row in nominal_a)
        and all(row['corrupted_correlation_reads'] == 0 for row in nominal_a)
        and all(row['false_clusters_injected'] == 0 for row in nominal_b)
        and any(row['corrupted_correlation_reads'] > 0 for row in nominal_b)
        and any(row['measured_rank'] != row['true_rank'] for row in nominal_b)
    )
    gate_d = (
        all(row['true_rank'] == floor_rank for row in nominal_a + nominal_b)
        and all(row['institution_visible'] for row in nominal_a)
        and any(row['institution_merged'] for row in nominal_b)
    )

    high = [
        row for row in arm_rows
        if row['scenario_label'] == 'positive_control_high_attacker'
    ]
    rank_one = [
        row for row in arm_rows
        if row['scenario_label'] == 'positive_control_rank_one_no_institution'
    ]
    gate_e = (
        {row['arm'] for row in high}
        == {'false_cluster_injection', 'measurement_corruption'}
        and all(row['defense_failed'] for row in high)
        and all(row['true_rank'] == 1 for row in rank_one)
        and all(row['defense_failed'] for row in rank_one)
    )

    gates = {
        'a_cost_scaling': gate_a,
        'b_effective_rank': gate_b,
        'c_distinct_arm_effects': gate_c,
        'd_institution_floor': gate_d,
        'e_positive_controls': gate_e,
        'validated_path_probe': validated_path_passed,
    }
    gates['overall'] = all(gates.values())
    return gates


def _evidence_summary(
    gates: Mapping[str, Any],
    cost_rows: list[dict[str, Any]],
    attribution_rows: list[dict[str, Any]],
    arm_rows: list[dict[str, Any]],
    variances: Mapping[str, Any],
    timing: Mapping[str, Any],
) -> dict[str, Any]:
    nominal_b = [
        row for row in arm_rows
        if row['scenario_label'] == 'nominal_maximum_collapse_with_institution'
        and row['arm'] == 'measurement_corruption'
    ]
    controls: dict[str, Any] = {}
    for label in (
        'positive_control_high_attacker',
        'positive_control_rank_one_no_institution',
    ):
        selected = [row for row in arm_rows if row['scenario_label'] == label]
        controls[label] = {
            arm: {
                'n': sum(row['arm'] == arm for row in selected),
                'failures': sum(
                    row['arm'] == arm and row['defense_failed'] for row in selected
                ),
            }
            for arm in ('false_cluster_injection', 'measurement_corruption')
        }
    return {
        'gate_results': dict(gates),
        'cost_scaling': [
            {
                'validator_count': row['validator_count'],
                'pairwise_checks': row['pairwise_checks'],
                'effective_defense_cost': row['effective_defense_cost'],
            }
            for row in cost_rows
            if row['defense_cost_model'] == 'pairwise_exact'
        ],
        'static_baseline_costs': [
            row['effective_defense_cost'] for row in cost_rows
            if row['defense_cost_model'] == 'static_baseline'
        ],
        'attribution_ranks': {
            row['case']: row['effective_rank'] for row in attribution_rows
        },
        'arm_b_floor_observation': {
            'n': len(nominal_b),
            'institution_merged_count': sum(
                row['institution_merged'] for row in nominal_b
            ),
            'measured_rank_below_two_count': sum(
                row['measured_rank'] < 2 for row in nominal_b
            ),
            'measured_rank_overcount_count': sum(
                row['measured_rank'] > row['true_rank'] for row in nominal_b
            ),
            'minimum_measured_rank': min(row['measured_rank'] for row in nominal_b),
            'maximum_measured_rank': max(row['measured_rank'] for row in nominal_b),
        },
        'positive_controls': controls,
        'variance_estimates': dict(variances),
        'timing_projection': dict(timing),
    }


def _smoke_report(
    summary: Mapping[str, Any],
    run_id: str,
    output_dir: Path,
) -> str:
    gate = summary['gate_results']
    costs = summary['cost_scaling']
    ranks = summary['attribution_ranks']
    floor = summary['arm_b_floor_observation']
    controls = summary['positive_controls']
    variances = summary['variance_estimates']
    timing = summary['timing_projection']
    lines = [
        '# Sybil defense scaling smoke report',
        '',
        f'Go/no-go: **{"GO" if gate["overall"] else "NO-GO"} for operator review of the instrument.**',
        '',
        'This was an instrument-validation and variance-estimation smoke only. '
        'It did not run a rank-by-ratio grid, set a capability-ratio range, '
        'calculate power, or read a crossover.',
        '',
        '## Logged smoke evidence',
        '',
        f'- Gate a, cost scaling: {"PASS" if gate["a_cost_scaling"] else "FAIL"}. '
        f'Exact pair counts and costs were {[(row["validator_count"], row["pairwise_checks"], row["effective_defense_cost"]) for row in costs]}.',
        f'- Gate b, effective rank: {"PASS" if gate["b_effective_rank"] else "FAIL"}. '
        f'Observed ranks were {ranks}.',
        f'- Gate c, distinct arm effects: {"PASS" if gate["c_distinct_arm_effects"] else "FAIL"}. '
        'Arm A changed apparent rank through surviving forged clusters while '
        'preserving the genuine partition. Arm B changed the similarity matrix '
        'without injecting clusters.',
        f'- Gate d, institutional floor: {"PASS" if gate["d_institution_floor"] else "FAIL"}. '
        'Arm A kept the true maximum-collapse rank at two and preserved the '
        f'institution in every run. Arm B merged the institution in '
        f'{floor["institution_merged_count"]}/{floor["n"]} runs, produced measured '
        f'rank below two in {floor["measured_rank_below_two_count"]}/{floor["n"]}, '
        f'and overcounted rank in {floor["measured_rank_overcount_count"]}/{floor["n"]}.',
        f'- Gate e, positive controls: {"PASS" if gate["e_positive_controls"] else "FAIL"}. '
        f'High-attacker failures were {controls["positive_control_high_attacker"]}; '
        f'rank-one failures were {controls["positive_control_rank_one_no_institution"]}.',
        f'- Existing validated path probe: {"PASS" if gate["validated_path_probe"] else "FAIL"}.',
        '',
        '## Variance estimate for the operator power calculation',
        '',
        f'- Arm A: {variances["false_cluster_injection"]}.',
        f'- Arm B: {variances["measurement_corruption"]}.',
        '',
        'These are smoke fixture variances, not crossover readings.',
        '',
        '## Timing and candidate projection',
        '',
        f'- Instrumented runs: {timing["timed_run_count"]}.',
        f'- Seconds per run, mean/median/p95/max: '
        f'{timing["mean_seconds"]:.9f} / {timing["median_seconds"]:.9f} / '
        f'{timing["p95_seconds"]:.9f} / {timing["maximum_seconds"]:.9f}.',
        f'- Candidate resolution: {timing["candidate_resolution"]}, '
        f'{timing["candidate_cell_count"]} cells per replicate layer.',
        f'- Projected cost: {timing["projection_formula"]}, equal to '
        f'{timing["projected_core_hours_per_replicate_layer"]:.9f} core-hours '
        'per replicate layer.',
        '',
        '## Output identity',
        '',
        f'- Run ID: `{run_id}`.',
        f'- Output directory: `{output_dir}`.',
        '- Every artifact and directory begins with or sits below `smoke_`. '
        'The authoritative convention uses the exact `full_5ac6a2e_` prefix '
        'and an explicit manifest, so these files cannot enter that selection.',
        '',
        'STOP: awaiting power calculation, capability-ratio range, and pre-registration commit before any full sweep.',
        '',
    ]
    return '\n'.join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=Path, default=DEFAULT_CONFIG)
    parser.add_argument('--output-root', type=Path)
    parser.add_argument('--run-id')
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = load_config(args.config)
    _assert_smoke_boundary(config)
    run_id = args.run_id or str(config['smoke']['run_id'])
    smoke_prefix = str(config['outputs']['smoke_run_prefix'])
    if not run_id.startswith(smoke_prefix):
        raise SystemExit(f'smoke run ID must begin with {smoke_prefix}')
    output_root = args.output_root or Path(config['outputs']['root'])
    output_dir = output_root / run_id
    output_dir.mkdir(parents=True, exist_ok=False)
    started_at = _utc_now()

    validated_rows, validated_path_passed = _validated_path_probe(config)
    cost_rows = _cost_records(config)
    attribution_rows = _attribution_records(config)
    arm_rows = _arm_records(config)
    all_rows = validated_rows + cost_rows + attribution_rows + arm_rows
    variances = _variance_estimates(arm_rows)
    timing = _timing_projection(config, arm_rows)
    gates = _gate_results(
        config,
        cost_rows,
        attribution_rows,
        arm_rows,
        validated_path_passed,
    )
    summary = _evidence_summary(
        gates, cost_rows, attribution_rows, arm_rows, variances, timing
    )

    results_path = output_dir / 'smoke_results.csv'
    evidence_path = output_dir / 'smoke_evidence.json'
    report_path = output_dir / 'smoke_report.md'
    log_path = output_dir / 'smoke_execution.log'
    _write_csv_atomic(results_path, all_rows)
    _write_json_atomic(evidence_path, summary)
    _write_text_atomic(report_path, _smoke_report(summary, run_id, output_dir))
    log_lines = [
        f'{name}: {"PASS" if passed else "FAIL"}'
        for name, passed in gates.items()
    ]
    log_lines.extend(
        [
            f'row_count: {len(all_rows)}',
            f'started_at_utc: {started_at}',
            f'ended_at_utc: {_utc_now()}',
            'full_sweep_executed: false',
            'crossover_computed: false',
        ]
    )
    _write_text_atomic(log_path, '\n'.join(log_lines) + '\n')

    manifest_path = output_dir / 'smoke_manifest.json'
    manifest = {
        'schema_version': 'sybil-scaling-smoke-manifest-v1',
        'run_id': run_id,
        'mode': 'instrument_validation_only',
        'started_at_utc': started_at,
        'ended_at_utc': _utc_now(),
        'branch': _git_value('branch', '--show-current'),
        'head_commit': _git_value('rev-parse', 'HEAD'),
        'working_tree_status': _git_value('status', '--short'),
        'python': sys.version,
        'platform': platform.platform(),
        'cpu_count': os.cpu_count(),
        'config_path': str(args.config),
        'config_sha256': _sha256(args.config),
        'row_count': len(all_rows),
        'gate_results': gates,
        'full_sweep_executed': False,
        'crossover_computed': False,
        'capability_ratio_range': None,
        'power_sample_size_per_cell': None,
        'artifacts': {
            path.name: {'sha256': _sha256(path), 'bytes': path.stat().st_size}
            for path in (results_path, evidence_path, report_path, log_path)
        },
    }
    _write_json_atomic(manifest_path, manifest)

    print(report_path)
    print(manifest_path)
    print(f'go_no_go={"GO" if gates["overall"] else "NO-GO"}')
    return 0 if gates['overall'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
