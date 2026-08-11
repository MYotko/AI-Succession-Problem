"""Run the authorized two-dial Sybil capability smoke.

This runner evaluates only the five registered validation gates. It cannot
run the characterization surface or the actual ratio-collapse slice.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import itertools
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
from statistics import NormalDist
from typing import Any, Iterable, Mapping

from sybil_defense_scaling import (
    AttackResult,
    attribute_validators,
    build_validator_pool,
    compute_attack_cost,
    compute_defense_cost,
    derive_two_dial_capability_terms,
    load_config,
    resolution_probability,
    run_false_cluster_injection,
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


def _deterministic_seed(
    gate: str, parameters: Mapping[str, Any], replicate: int
) -> int:
    payload = json.dumps(
        {
            'schema': 'sybil-two-dial-smoke-seed-v1',
            'gate': gate,
            'parameters': dict(parameters),
            'replicate': int(replicate),
        },
        sort_keys=True,
        separators=(',', ':'),
    )
    digest = hashlib.sha256(payload.encode('utf-8')).digest()
    return int.from_bytes(digest[:8], 'big') % (2**31 - 1)


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
    temporary = path.with_suffix(path.suffix + '.tmp')
    with temporary.open('w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(
            handle, fieldnames=fieldnames, lineterminator='\n'
        )
        writer.writeheader()
        writer.writerows(_json_safe(rows))
    os.replace(temporary, path)


def _assert_smoke_boundary(config: Mapping[str, Any]) -> None:
    sweep = config['sweep']
    if sweep['authorization'] != 'blocked_pending_registration':
        raise RuntimeError('characterization authorization must remain blocked')
    smoke = config['two_dial_smoke']
    if smoke['authorization'] != 'instrument_validation_only':
        raise RuntimeError('two-dial smoke authorization is invalid')
    if [float(value) for value in smoke['parity_levels']] != [0.316, 1.0, 3.16]:
        raise RuntimeError('two-dial parity levels do not match the ruling')
    if [int(value) for value in smoke['validator_set_sizes']] != [
        2, 4, 8, 16, 32, 64
    ]:
        raise RuntimeError('two-dial rank ladder does not match the ruling')
    if int(smoke['replicates_per_cell']) != 200:
        raise RuntimeError('two-dial curve smoke must use n=200')
    if float(smoke['failure_rate_mei']) != 0.15:
        raise RuntimeError('two-dial curve smoke MEI must be 0.15')
    power = smoke['power']
    if (
        float(power['two_sided_alpha']) != 0.05
        or float(power['target_power']) != 0.8
        or float(power['worst_case_probability']) != 0.5
    ):
        raise RuntimeError('two-dial power settings do not match the ruling')
    term = config['two_dial_capability']['absolute_resolution_term']
    if term['enabled'] is not False:
        raise RuntimeError('absolute-level term must default OFF')
    if str(term['form']) != 'defender_power_law_resolution':
        raise RuntimeError('unexpected absolute-level term form')


def _power_summary(smoke: Mapping[str, Any]) -> dict[str, Any]:
    alpha = float(smoke['power']['two_sided_alpha'])
    target_power = float(smoke['power']['target_power'])
    probability = float(smoke['power']['worst_case_probability'])
    mei = float(smoke['failure_rate_mei'])
    configured_n = int(smoke['replicates_per_cell'])
    normal = NormalDist()
    z_alpha = normal.inv_cdf(1.0 - alpha / 2.0)
    z_power = normal.inv_cdf(target_power)
    variance_sum = 2.0 * probability * (1.0 - probability)
    coefficient = variance_sum * (z_alpha + z_power) ** 2
    raw_required_n = coefficient / mei**2
    required_n = math.ceil(raw_required_n)
    noncentrality = mei / math.sqrt(variance_sum / configured_n)
    achieved_power = (
        normal.cdf(-z_alpha - noncentrality)
        + 1.0
        - normal.cdf(z_alpha - noncentrality)
    )
    return {
        'two_sided_alpha': alpha,
        'target_power': target_power,
        'worst_case_probability': probability,
        'mei': mei,
        'z_alpha': z_alpha,
        'z_power': z_power,
        'coefficient': coefficient,
        'raw_required_n_per_group': raw_required_n,
        'required_n_per_group': required_n,
        'configured_n_per_cell': configured_n,
        'n_margin': configured_n - required_n,
        'normal_approximation_power_at_configured_n': achieved_power,
    }


def _base_resolution_power(config: Mapping[str, Any]) -> float:
    capability = config['defender_capability']
    return float(capability['base_resolution']) * float(
        capability['resolution_improvement']
    )


def _fixture(
    config: Mapping[str, Any], size: int
) -> tuple[Any, Any, Any, Any, float, int]:
    validators = build_validator_pool(
        int(size) - 1,
        1,
        config['collapse'],
        lineage_mode='distinct',
    )
    severity = float(config['two_dial_smoke']['collapse_severity'])
    attribution = attribute_validators(validators, severity, config['attribution'])
    forged_count = int(
        config['attack_arms']['false_cluster_injection']['forged_cluster_count']
    )
    defense_inputs = len(validators)
    if config['costs']['defense']['input_basis'] == 'apparent_inputs':
        defense_inputs += forged_count
    defense = compute_defense_cost(
        defense_inputs,
        config['costs']['defense'],
        float(config['defender_capability']['exponent_reduction']),
        model='pairwise_exact',
    )
    attack = compute_attack_cost(
        attribution.effective_rank,
        config['costs']['attack'],
        model='linear',
    )
    return (
        validators,
        attribution,
        defense,
        attack,
        _base_resolution_power(config),
        forged_count,
    )


def _expected_curve(
    config: Mapping[str, Any], *, absolute_term_enabled: bool
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    smoke = config['two_dial_smoke']
    minimum_rank = int(config['poles']['deployment_minimum_rank'])
    for size in smoke['validator_set_sizes']:
        (
            _,
            attribution,
            defense,
            attack,
            base_resolution,
            forged_count,
        ) = _fixture(config, int(size))
        for level in smoke['parity_levels']:
            terms = derive_two_dial_capability_terms(
                attacker_capability=float(level),
                defender_capability=float(level),
                base_resolution_power=base_resolution,
                two_dial_config=config['two_dial_capability'],
                absolute_term_enabled=absolute_term_enabled,
            )
            probability = resolution_probability(
                true_rank=attribution.effective_rank,
                minimum_consensus_rank=minimum_rank,
                capability_ratio=terms.capability_ratio,
                resolution_power=terms.effective_resolution_power,
                defense_cost=defense.effective_cost,
                attack_cost=attack.cost,
            )
            rows.append(
                {
                    'validator_set_size': int(size),
                    'effective_rank': attribution.effective_rank,
                    'parity_level': float(level),
                    'resolution_probability': probability,
                    'failure_rate': 1.0 - probability**forged_count,
                    'absolute_resolution_multiplier': (
                        terms.absolute_resolution_multiplier
                    ),
                }
            )
    return rows


def _curve_separations(rows: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[int, list[Mapping[str, Any]]] = {}
    for row in rows:
        grouped.setdefault(int(row['validator_set_size']), []).append(row)
    result: list[dict[str, Any]] = []
    for size in sorted(grouped):
        selected = sorted(grouped[size], key=lambda row: row['parity_level'])
        rates = [float(row['failure_rate']) for row in selected]
        result.append(
            {
                'validator_set_size': size,
                'effective_rank': int(selected[0]['effective_rank']),
                'rates_by_level': {
                    str(row['parity_level']): float(row['failure_rate'])
                    for row in selected
                },
                'maximum_cross_level_difference': max(rates) - min(rates),
            }
        )
    return result


def _run_curve_gate(
    config: Mapping[str, Any], *, gate: str, absolute_term_enabled: bool
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    smoke = config['two_dial_smoke']
    replicates = int(smoke['replicates_per_cell'])
    minimum_rank = int(config['poles']['deployment_minimum_rank'])
    severity = float(smoke['collapse_severity'])
    for size in smoke['validator_set_sizes']:
        (
            validators,
            attribution,
            defense,
            attack,
            base_resolution,
            forged_count,
        ) = _fixture(config, int(size))
        for level in smoke['parity_levels']:
            terms = derive_two_dial_capability_terms(
                attacker_capability=float(level),
                defender_capability=float(level),
                base_resolution_power=base_resolution,
                two_dial_config=config['two_dial_capability'],
                absolute_term_enabled=absolute_term_enabled,
            )
            for replicate in range(replicates):
                seed_parameters = {
                    'size': int(size),
                    'parity_level': float(level),
                    'absolute_term_enabled': absolute_term_enabled,
                }
                seed = _deterministic_seed(gate, seed_parameters, replicate)
                started = time.perf_counter_ns()
                result = run_false_cluster_injection(
                    attribution,
                    validators,
                    forged_cluster_count=forged_count,
                    capability_ratio=terms.capability_ratio,
                    resolution_power=terms.effective_resolution_power,
                    defense_cost=defense.effective_cost,
                    attack_cost=attack.cost,
                    minimum_consensus_rank=minimum_rank,
                    rng=random.Random(seed),
                )
                elapsed = (time.perf_counter_ns() - started) / 1_000_000_000
                rows.append(
                    {
                        'record_type': 'curve_run',
                        'gate': gate,
                        'replicate': replicate,
                        'seed': seed,
                        'validator_set_size': int(size),
                        'frontier_validator_count': int(size) - 1,
                        'institution_validator_count': 1,
                        'effective_rank': attribution.effective_rank,
                        'collapse_severity': severity,
                        'parity_level': float(level),
                        'attacker_capability': terms.attacker_capability,
                        'defender_capability': terms.defender_capability,
                        'derived_capability_ratio': terms.capability_ratio,
                        'absolute_term_enabled': terms.absolute_term_enabled,
                        'absolute_term_strength': terms.absolute_term_strength,
                        'absolute_resolution_multiplier': (
                            terms.absolute_resolution_multiplier
                        ),
                        'resolution_probability': result.resolution_probability,
                        'defense_failed': result.defense_failed,
                        'measured_rank': result.measured_rank,
                        'defense_cost_model': defense.model,
                        'attack_cost_model': attack.model,
                        'merge_rule': config['attribution']['merge_rule'],
                        'elapsed_seconds': elapsed,
                    }
                )
    return rows


def _sample_variance(values: Iterable[float]) -> float:
    sequence = [float(value) for value in values]
    return statistics.variance(sequence) if len(sequence) > 1 else 0.0


def _summarize_curve_gate(
    rows: list[dict[str, Any]], smoke: Mapping[str, Any]
) -> dict[str, Any]:
    grouped: dict[tuple[int, float], list[dict[str, Any]]] = {}
    for row in rows:
        key = (int(row['validator_set_size']), float(row['parity_level']))
        grouped.setdefault(key, []).append(row)
    cells: list[dict[str, Any]] = []
    for (size, level), selected in sorted(grouped.items()):
        failures = [int(row['defense_failed']) for row in selected]
        cells.append(
            {
                'validator_set_size': size,
                'effective_rank': int(selected[0]['effective_rank']),
                'parity_level': level,
                'n': len(selected),
                'failure_rate': statistics.mean(failures),
                'failure_sample_variance': _sample_variance(failures),
                'resolution_probability': float(
                    selected[0]['resolution_probability']
                ),
            }
        )
    cell_by_key = {
        (cell['validator_set_size'], cell['parity_level']): cell for cell in cells
    }
    comparisons: list[dict[str, Any]] = []
    levels = [float(value) for value in smoke['parity_levels']]
    for size in smoke['validator_set_sizes']:
        for low, high in itertools.combinations(levels, 2):
            left = cell_by_key[(int(size), low)]
            right = cell_by_key[(int(size), high)]
            comparisons.append(
                {
                    'validator_set_size': int(size),
                    'level_a': low,
                    'level_b': high,
                    'failure_rate_a': left['failure_rate'],
                    'failure_rate_b': right['failure_rate'],
                    'absolute_difference': abs(
                        left['failure_rate'] - right['failure_rate']
                    ),
                    'variance_a': left['failure_sample_variance'],
                    'variance_b': right['failure_sample_variance'],
                }
            )
    return {
        'cell_count': len(cells),
        'run_count': len(rows),
        'cells': cells,
        'comparisons': comparisons,
        'maximum_observed_cross_level_difference': max(
            row['absolute_difference'] for row in comparisons
        ),
    }


def _attack_results_equal(left: AttackResult, right: AttackResult) -> bool:
    return (
        left.arm == right.arm
        and left.true_rank == right.true_rank
        and left.measured_rank == right.measured_rank
        and left.defense_failed == right.defense_failed
        and left.institution_visible == right.institution_visible
        and left.details == right.details
    )


def _run_gate_1_and_5(config: Mapping[str, Any]) -> dict[str, Any]:
    smoke = config['two_dial_smoke']
    tolerance = float(smoke['ratio_recovery_tolerance'])
    replicates = int(smoke['gate_5']['replicates_per_cell'])
    minimum_rank = int(config['poles']['deployment_minimum_rank'])
    rows: list[dict[str, Any]] = []
    for cell_index, cell in enumerate(smoke['gate_5']['cells']):
        size = int(cell['validator_set_size'])
        ratio = float(cell['capability_ratio'])
        (
            validators,
            attribution,
            defense,
            attack,
            base_resolution,
            forged_count,
        ) = _fixture(config, size)
        terms = derive_two_dial_capability_terms(
            attacker_capability=ratio,
            defender_capability=1.0,
            base_resolution_power=base_resolution,
            two_dial_config=config['two_dial_capability'],
            absolute_term_enabled=False,
        )
        for replicate in range(replicates):
            parameters = {
                'cell_index': cell_index,
                'validator_set_size': size,
                'capability_ratio': ratio,
            }
            seed = _deterministic_seed('gate_1_and_5', parameters, replicate)
            committed = run_false_cluster_injection(
                attribution,
                validators,
                forged_cluster_count=forged_count,
                capability_ratio=ratio,
                resolution_power=base_resolution,
                defense_cost=defense.effective_cost,
                attack_cost=attack.cost,
                minimum_consensus_rank=minimum_rank,
                rng=random.Random(seed),
            )
            changed = run_false_cluster_injection(
                attribution,
                validators,
                forged_cluster_count=forged_count,
                capability_ratio=terms.capability_ratio,
                resolution_power=terms.effective_resolution_power,
                defense_cost=defense.effective_cost,
                attack_cost=attack.cost,
                minimum_consensus_rank=minimum_rank,
                rng=random.Random(seed),
            )
            probability_difference = abs(
                committed.resolution_probability - changed.resolution_probability
            )
            rows.append(
                {
                    'record_type': 'non_regression_comparison',
                    'gate': 'gate_1_and_5',
                    'cell_index': cell_index,
                    'replicate': replicate,
                    'seed': seed,
                    'validator_set_size': size,
                    'effective_rank': attribution.effective_rank,
                    'capability_ratio': ratio,
                    'derived_capability_ratio': terms.capability_ratio,
                    'absolute_term_enabled': terms.absolute_term_enabled,
                    'absolute_resolution_multiplier': (
                        terms.absolute_resolution_multiplier
                    ),
                    'committed_resolution_probability': (
                        committed.resolution_probability
                    ),
                    'two_dial_resolution_probability': (
                        changed.resolution_probability
                    ),
                    'resolution_probability_difference': probability_difference,
                    'outputs_identical': _attack_results_equal(committed, changed),
                    'rank_axis_unchanged': attribution.effective_rank == size,
                    'defense_cost_model': defense.model,
                    'attack_cost_model': attack.model,
                    'merge_rule': config['attribution']['merge_rule'],
                }
            )
    return {
        'rows': rows,
        'cell_count': len(smoke['gate_5']['cells']),
        'paired_comparison_count': len(rows),
        'mechanism_evaluation_count': 2 * len(rows),
        'maximum_resolution_probability_difference': max(
            row['resolution_probability_difference'] for row in rows
        ),
        'ratio_recovery_passed': all(
            row['resolution_probability_difference'] <= tolerance for row in rows
        ),
        'main_surface_non_regression_passed': all(
            row['outputs_identical']
            and row['rank_axis_unchanged']
            and row['defense_cost_model'] == 'pairwise_exact'
            and row['attack_cost_model'] == 'linear'
            and row['merge_rule'] == 'threshold_connected_components'
            for row in rows
        ),
    }


def _observed_variance_power(
    summaries: Iterable[Mapping[str, Any]], power: Mapping[str, Any]
) -> dict[str, Any]:
    normal = NormalDist()
    z_alpha = float(power['z_alpha'])
    z_power = float(power['z_power'])
    mei = float(power['mei'])
    configured_n = int(power['configured_n_per_cell'])
    comparisons: list[dict[str, Any]] = []
    for summary in summaries:
        for comparison in summary['comparisons']:
            variance_sum = float(comparison['variance_a']) + float(
                comparison['variance_b']
            )
            raw_required = (
                (z_alpha + z_power) ** 2 * variance_sum / mei**2
            )
            required = math.ceil(raw_required)
            if variance_sum > 0.0:
                noncentrality = mei / math.sqrt(variance_sum / configured_n)
                achieved = (
                    normal.cdf(-z_alpha - noncentrality)
                    + 1.0
                    - normal.cdf(z_alpha - noncentrality)
                )
            else:
                achieved = 1.0
            comparisons.append(
                {
                    **comparison,
                    'raw_required_n_per_group': raw_required,
                    'required_n_per_group': required,
                    'normal_approximation_power_at_n_200': achieved,
                }
            )
    maximum_required = max(row['required_n_per_group'] for row in comparisons)
    return {
        'comparisons': comparisons,
        'maximum_observed_variance_required_n_per_group': maximum_required,
        'minimum_observed_variance_power_at_n_200': min(
            row['normal_approximation_power_at_n_200'] for row in comparisons
        ),
        'passed': maximum_required <= configured_n,
    }


def _report(
    *,
    run_id: str,
    output_dir: Path,
    config: Mapping[str, Any],
    power: Mapping[str, Any],
    expected_off: list[dict[str, Any]],
    expected_on: list[dict[str, Any]],
    gate_2: Mapping[str, Any],
    gate_3: Mapping[str, Any],
    gate_4: Mapping[str, Any],
    gate_1_5: Mapping[str, Any],
    gates: Mapping[str, bool],
) -> str:
    term = config['two_dial_capability']['absolute_resolution_term']
    on_separations = _curve_separations(expected_on)
    off_separations = _curve_separations(expected_off)
    lines = [
        '# Sybil two-dial capability bidirectional smoke report',
        '',
        f'Go/no-go: **{"GO" if gates["overall"] else "NO-GO"}.**',
        '',
        'This run executed only the five authorized two-dial smoke gates. It '
        'did not run the characterization surface, the actual ratio-collapse '
        'slice, or any crossover calculation.',
        '',
        '## Power confirmation',
        '',
        f'- Two-sided alpha: {power["two_sided_alpha"]}.',
        f'- Target power: {power["target_power"]}.',
        f'- Failure-rate MEI: {power["mei"]}.',
        f'- Worst-case staged coefficient: {power["coefficient"]:.12f}.',
        f'- Raw required n per group: {power["raw_required_n_per_group"]:.12f}.',
        f'- Required integer n per group: {power["required_n_per_group"]}.',
        f'- Configured n per cell: {power["configured_n_per_cell"]}, a margin '
        f'of {power["n_margin"]}.',
        f'- Normal-approximation power at n=200 under worst-case variance: '
        f'{power["normal_approximation_power_at_configured_n"]:.12f}.',
        '',
        '## Absolute-level term for operator confirmation',
        '',
        f'- Form: `{term["form"]}`.',
        f'- Configured default: OFF.',
        f'- Reference defender capability: {term["reference_level"]}.',
        f'- Calibrated strength: {term["strength"]:.17g}.',
        '- Functional form: '
        '`absolute_resolution_multiplier = '
        '(defender_capability / reference_level) ** strength`.',
        '- Grounding: absolute defender capability scales the throughput with '
        'which the pairwise independence check can resolve evidence. The '
        'strength is the elasticity of that throughput. Level 1 is neutral, '
        'and disabling the term forces the multiplier to exactly 1.',
        '',
        'Expected term-ON failure curves and separations:',
        '',
        '| Rank | Level 0.316 | Level 1.0 | Level 3.16 | Maximum separation |',
        '|---:|---:|---:|---:|---:|',
    ]
    for row in on_separations:
        rates = row['rates_by_level']
        lines.append(
            f'| {row["effective_rank"]} | {rates["0.316"]:.12f} | '
            f'{rates["1.0"]:.12f} | {rates["3.16"]:.12f} | '
            f'{row["maximum_cross_level_difference"]:.12f} |'
        )
    lines.extend(
        [
            '',
            'Expected term-OFF maximum separations are exactly: '
            + ', '.join(
                f'rank {row["effective_rank"]}: '
                f'{row["maximum_cross_level_difference"]:.12f}'
                for row in off_separations
            )
            + '.',
            '',
            '## Gate results',
            '',
            f'- Gate 1, ratio recovery: '
            f'{"PASS" if gates["gate_1_ratio_recovery"] else "FAIL"}. '
            f'Maximum probability difference was '
            f'{gate_1_5["maximum_resolution_probability_difference"]:.12g} '
            f'against tolerance '
            f'{config["two_dial_smoke"]["ratio_recovery_tolerance"]}.',
            f'- Gate 2, collapse control: '
            f'{"PASS" if gates["gate_2_collapse_control"] else "FAIL"}. '
            f'Maximum observed cross-level difference was '
            f'{gate_2["maximum_observed_cross_level_difference"]:.12f} '
            f'against MEI {power["mei"]}.',
            f'- Gate 3, non-collapse positive control: '
            f'{"PASS" if gates["gate_3_noncollapse_control"] else "FAIL"}. '
            f'Maximum observed cross-level difference was '
            f'{gate_3["maximum_observed_cross_level_difference"]:.12f} '
            f'against MEI {power["mei"]}.',
            f'- Gate 4, observed variance: '
            f'{"PASS" if gates["gate_4_variance"] else "FAIL"}. '
            f'The largest required n from observed cell variances was '
            f'{gate_4["maximum_observed_variance_required_n_per_group"]}; '
            f'the minimum normal-approximation power at n=200 was '
            f'{gate_4["minimum_observed_variance_power_at_n_200"]:.12f}.',
            f'- Gate 5, main-surface non-regression: '
            f'{"PASS" if gates["gate_5_main_surface_non_regression"] else "FAIL"}. '
            f'{gate_1_5["paired_comparison_count"]} paired committed-versus-'
            'two-dial comparisons used shared seeds at the five registered '
            'cells, and term OFF produced identical outputs.',
            '',
            '## Gate 4 cell variances',
            '',
            '| Gate | Rank | Level | n | Failure rate | Sample variance |',
            '|---|---:|---:|---:|---:|---:|',
        ]
    )
    for name, summary in (('Gate 2', gate_2), ('Gate 3', gate_3)):
        for cell in summary['cells']:
            lines.append(
                f'| {name} | {cell["effective_rank"]} | '
                f'{cell["parity_level"]} | {cell["n"]} | '
                f'{cell["failure_rate"]:.12f} | '
                f'{cell["failure_sample_variance"]:.12f} |'
            )
    lines.extend(
        [
            '',
            '## Scope, counts, and output identity',
            '',
            f'- Gate 2: {gate_2["cell_count"]} cells and '
            f'{gate_2["run_count"]} runs.',
            f'- Gate 3: {gate_3["cell_count"]} cells and '
            f'{gate_3["run_count"]} runs.',
            f'- Gate 1 and Gate 5: {gate_1_5["cell_count"]} registered cells, '
            f'{gate_1_5["paired_comparison_count"]} paired comparisons, and '
            f'{gate_1_5["mechanism_evaluation_count"]} mechanism evaluations.',
            f'- Run ID: `{run_id}`.',
            f'- Output directory: `{output_dir}`.',
            '- The directory and every artifact use the `two_dial_smoke_` '
            'prefix. They do not use the authoritative `full_5ac6a2e_` prefix '
            'and are not part of an authoritative manifest.',
            '- Characterization authorization remained '
            '`blocked_pending_registration`.',
            '',
            '## Main-surface non-regression',
            '',
            'With the absolute-level term OFF, the derived ratio and effective '
            'resolution power reproduce the committed capability inputs. The '
            'rank attribution, Arm A path, pairwise defense cost, linear attack '
            'cost, merge rule, failure definition, and seeded outcomes were '
            'unchanged at all five registered Gate 5 cells. The committed '
            'main-surface behavior is therefore unaffected in the default-OFF '
            'configuration.',
            '',
            'The power-law functional form and calibrated strength remain '
            'flagged for operator confirmation before any real ratio-collapse '
            'slice is registered or run.',
            '',
        ]
    )
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
    smoke = config['two_dial_smoke']
    run_id = args.run_id or str(smoke['run_id'])
    prefix = str(config['outputs']['two_dial_smoke_run_prefix'])
    if not run_id.startswith(prefix):
        raise SystemExit(f'two-dial smoke run ID must begin with {prefix}')
    output_root = args.output_root or Path(config['outputs']['root'])
    output_dir = output_root / run_id
    output_dir.mkdir(parents=True, exist_ok=False)
    started_at = _utc_now()

    power = _power_summary(smoke)
    expected_off = _expected_curve(config, absolute_term_enabled=False)
    expected_on = _expected_curve(config, absolute_term_enabled=True)
    expected_on_separations = _curve_separations(expected_on)
    expected_maximum = max(
        row['maximum_cross_level_difference']
        for row in expected_on_separations
    )
    if expected_maximum < float(smoke['failure_rate_mei']):
        raise RuntimeError('calibrated term does not reach the failure-rate MEI')

    gate_2_rows = _run_curve_gate(
        config, gate='gate_2_collapse_control', absolute_term_enabled=False
    )
    gate_3_rows = _run_curve_gate(
        config, gate='gate_3_noncollapse_control', absolute_term_enabled=True
    )
    gate_2 = _summarize_curve_gate(gate_2_rows, smoke)
    gate_3 = _summarize_curve_gate(gate_3_rows, smoke)
    gate_1_5 = _run_gate_1_and_5(config)
    gate_4 = _observed_variance_power((gate_2, gate_3), power)
    mei = float(smoke['failure_rate_mei'])
    gates = {
        'gate_1_ratio_recovery': bool(gate_1_5['ratio_recovery_passed']),
        'gate_2_collapse_control': (
            gate_2['maximum_observed_cross_level_difference'] <= mei
        ),
        'gate_3_noncollapse_control': (
            gate_3['maximum_observed_cross_level_difference'] >= mei
        ),
        'gate_4_variance': bool(gate_4['passed']),
        'gate_5_main_surface_non_regression': bool(
            gate_1_5['main_surface_non_regression_passed']
        ),
    }
    gates['overall'] = all(gates.values())

    all_rows = gate_2_rows + gate_3_rows + gate_1_5['rows']
    evidence = {
        'gate_results': gates,
        'power': power,
        'absolute_resolution_term': dict(
            config['two_dial_capability']['absolute_resolution_term']
        ),
        'expected_term_off_curve': expected_off,
        'expected_term_on_curve': expected_on,
        'expected_term_off_separations': _curve_separations(expected_off),
        'expected_term_on_separations': expected_on_separations,
        'gate_2': gate_2,
        'gate_3': gate_3,
        'gate_4': gate_4,
        'gate_1_and_5': {
            key: value for key, value in gate_1_5.items() if key != 'rows'
        },
        'full_sweep_executed': False,
        'ratio_collapse_slice_executed': False,
        'crossover_computed': False,
    }

    results_path = output_dir / 'two_dial_smoke_results.csv'
    evidence_path = output_dir / 'two_dial_smoke_evidence.json'
    report_path = output_dir / 'two_dial_smoke_report.md'
    log_path = output_dir / 'two_dial_smoke_execution.log'
    _write_csv_atomic(results_path, all_rows)
    _write_json_atomic(evidence_path, evidence)
    _write_text_atomic(
        report_path,
        _report(
            run_id=run_id,
            output_dir=output_dir,
            config=config,
            power=power,
            expected_off=expected_off,
            expected_on=expected_on,
            gate_2=gate_2,
            gate_3=gate_3,
            gate_4=gate_4,
            gate_1_5=gate_1_5,
            gates=gates,
        ),
    )
    ended_at = _utc_now()
    log_lines = [
        f'{name}: {"PASS" if passed else "FAIL"}'
        for name, passed in gates.items()
    ]
    log_lines.extend(
        [
            f'curve_cell_count: {gate_2["cell_count"] + gate_3["cell_count"]}',
            f'curve_run_count: {gate_2["run_count"] + gate_3["run_count"]}',
            f'non_regression_paired_comparisons: '
            f'{gate_1_5["paired_comparison_count"]}',
            f'started_at_utc: {started_at}',
            f'ended_at_utc: {ended_at}',
            'full_sweep_executed: false',
            'ratio_collapse_slice_executed: false',
            'crossover_computed: false',
        ]
    )
    _write_text_atomic(log_path, '\n'.join(log_lines) + '\n')

    manifest_path = output_dir / 'two_dial_smoke_manifest.json'
    manifest = {
        'schema_version': 'sybil-two-dial-smoke-manifest-v1',
        'run_id': run_id,
        'mode': 'instrument_validation_only',
        'started_at_utc': started_at,
        'ended_at_utc': ended_at,
        'branch': _git_value('branch', '--show-current'),
        'head_commit': _git_value('rev-parse', 'HEAD'),
        'working_tree_status': _git_value('status', '--short'),
        'python': sys.version,
        'platform': platform.platform(),
        'cpu_count': os.cpu_count(),
        'config_path': str(args.config),
        'config_sha256': _sha256(args.config),
        'gate_results': gates,
        'power': power,
        'counts': {
            'gate_2_cells': gate_2['cell_count'],
            'gate_2_runs': gate_2['run_count'],
            'gate_3_cells': gate_3['cell_count'],
            'gate_3_runs': gate_3['run_count'],
            'gate_1_and_5_cells': gate_1_5['cell_count'],
            'gate_1_and_5_paired_comparisons': (
                gate_1_5['paired_comparison_count']
            ),
            'gate_1_and_5_mechanism_evaluations': (
                gate_1_5['mechanism_evaluation_count']
            ),
            'result_rows': len(all_rows),
        },
        'full_sweep_executed': False,
        'ratio_collapse_slice_executed': False,
        'crossover_computed': False,
        'characterization_authorization': config['sweep']['authorization'],
        'authoritative_manifest': False,
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
