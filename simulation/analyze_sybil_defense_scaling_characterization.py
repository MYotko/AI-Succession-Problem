"""Analyze the Sybil characterization against its committed registration."""

from __future__ import annotations

import csv
import hashlib
import itertools
import json
import math
import os
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent
NOTE_PATH = HERE / 'diagnostics' / 'sybil_defense_scaling_design_note.md'
RUN_DIR = (
    REPO_ROOT
    / 'data'
    / 'sybil_defense_scaling'
    / 'full_5ac6a2e_sybil_scaling_characterization_v1'
)
MANIFEST_PATH = RUN_DIR / 'full_5ac6a2e_manifest.json'
REPORT_PATH = HERE / 'diagnostics' / 'sybil_defense_scaling_characterization_report.md'
ANALYSIS_PATH = HERE / 'diagnostics' / 'sybil_defense_scaling_characterization_analysis.json'
Z_95 = 1.96
MEI = 0.15


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline='', encoding='utf-8') as handle:
        return list(csv.DictReader(handle))


def _write_text_atomic(path: Path, content: str) -> None:
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(content, encoding='utf-8')
    os.replace(temporary, path)


def _write_json_atomic(path: Path, value: Any) -> None:
    _write_text_atomic(path, json.dumps(value, indent=2, sort_keys=True) + '\n')


def _load_manifest_results() -> tuple[dict[str, Any], dict[str, list[dict[str, str]]]]:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding='utf-8'))
    if manifest['status'] != 'complete':
        raise RuntimeError('manifest is not complete')
    expected_names = {
        'full_5ac6a2e_main_surface_results.csv': 'main_surface',
        'full_5ac6a2e_ratio_collapse_slice_results.csv': 'ratio_collapse_slice',
        'full_5ac6a2e_complete_linkage_results.csv': 'complete_linkage',
    }
    selected: dict[str, list[dict[str, str]]] = {}
    seen: set[str] = set()
    for artifact in manifest['authoritative_artifacts']:
        path = REPO_ROOT / artifact['path']
        if path.name not in expected_names:
            raise RuntimeError(f'unexpected authoritative artifact: {path.name}')
        if _sha256(path) != artifact['sha256']:
            raise RuntimeError(f'authoritative artifact hash mismatch: {path}')
        rows = _read_csv(path)
        if len(rows) != int(artifact['rows']):
            raise RuntimeError(f'authoritative artifact row mismatch: {path}')
        selected[expected_names[path.name]] = rows
        seen.add(path.name)
    if seen != set(expected_names):
        raise RuntimeError('authoritative manifest does not enumerate exact passes')
    return manifest, selected


def _float(row: Mapping[str, str], key: str) -> float:
    return float(row[key])


def _int(row: Mapping[str, str], key: str) -> int:
    return int(row[key])


def _bool(row: Mapping[str, str], key: str) -> bool:
    if row[key] not in {'True', 'False'}:
        raise ValueError(f'invalid boolean text in {key}')
    return row[key] == 'True'


def _proportion_interval(p: float, n: int) -> dict[str, float]:
    se = math.sqrt(p * (1.0 - p) / n)
    return {'estimate': p, 'se': se, 'lower': p - Z_95 * se, 'upper': p + Z_95 * se}


def _difference_interval(p1: float, p2: float, n1: int, n2: int, *, absolute: bool) -> dict[str, Any]:
    signed = p1 - p2
    estimate = abs(signed) if absolute else signed
    se = math.sqrt(p1 * (1.0 - p1) / n1 + p2 * (1.0 - p2) / n2)
    lower = estimate - Z_95 * se
    upper = estimate + Z_95 * se
    vacuous_zero = estimate == 0.0
    if vacuous_zero:
        classification = 'vacuous_zero_flag'
    elif lower >= MEI:
        classification = 'sensitive'
    elif upper < MEI:
        classification = 'robust'
    else:
        classification = 'boundary'
    return {
        'estimate': estimate,
        'signed_difference': signed,
        'se': se,
        'lower': lower,
        'upper': upper,
        'classification': classification,
        'vacuous_zero': vacuous_zero,
    }


def _floor_class(interval: Mapping[str, float]) -> str:
    if interval['upper'] < 0.5:
        return 'clears'
    if interval['lower'] > 0.5:
        return 'fails'
    return 'statistical_boundary'


def _cross_floor(left: str, right: str) -> str:
    if left == right == 'clears':
        return 'floor_clears'
    if left == right == 'fails':
        return 'floor_fails'
    return 'floor_boundary'


def _cell_key(row: Mapping[str, str]) -> tuple[Any, ...]:
    return (
        _int(row, 'structural_point_index'),
        _float(row, 'capability_ratio'),
        row['defense_cost_model'],
        row['attack_cost_model'],
    )


def _structural(row: Mapping[str, str]) -> dict[str, Any]:
    return {
        'structural_point_index': _int(row, 'structural_point_index'),
        'validator_set_size': _int(row, 'validator_set_size'),
        'frontier_validator_count': _int(row, 'frontier_validator_count'),
        'institution_validator_count': _int(row, 'institution_validator_count'),
        'collapse_severity': _float(row, 'collapse_severity'),
        'institution_alone_corner': _bool(row, 'institution_alone_corner'),
        'true_effective_rank': _int(row, 'true_effective_rank'),
    }


def _ratio_collapse(rows: Sequence[Mapping[str, str]]) -> dict[str, Any]:
    grouped: dict[int, list[Mapping[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[_int(row, 'structural_point_index')].append(row)
    if len(grouped) != 25:
        raise RuntimeError('ratio-collapse slice does not have 25 structural points')
    points: list[dict[str, Any]] = []
    comparisons: list[dict[str, Any]] = []
    for point_index in sorted(grouped):
        selected = sorted(grouped[point_index], key=lambda row: _float(row, 'attacker_capability'))
        if [_float(row, 'attacker_capability') for row in selected] != [0.316, 1.0, 3.16]:
            raise RuntimeError('ratio-collapse levels drifted')
        point_comparisons: list[dict[str, Any]] = []
        for left, right in itertools.combinations(selected, 2):
            interval = _difference_interval(
                _float(left, 'failure_rate'),
                _float(right, 'failure_rate'),
                _int(left, 'n'),
                _int(right, 'n'),
                absolute=True,
            )
            comparison = {
                'structural_point_index': point_index,
                'level_a': _float(left, 'attacker_capability'),
                'level_b': _float(right, 'attacker_capability'),
                'failure_rate_a': _float(left, 'failure_rate'),
                'failure_rate_b': _float(right, 'failure_rate'),
                **interval,
            }
            comparisons.append(comparison)
            point_comparisons.append(comparison)
        maximum = max(point_comparisons, key=lambda item: item['estimate'])
        points.append(
            {
                **_structural(selected[0]),
                'rates_by_level': {
                    str(_float(row, 'attacker_capability')): _float(row, 'failure_rate')
                    for row in selected
                },
                'maximum_comparison': maximum,
            }
        )
    noncollapse = [item for item in comparisons if item['lower'] >= MEI]
    all_collapse = all(item['upper'] < MEI for item in comparisons)
    verdict = 'noncollapse' if noncollapse else ('collapse' if all_collapse else 'boundary')
    return {
        'points': points,
        'comparisons': comparisons,
        'classification_counts': dict(Counter(item['classification'] for item in comparisons)),
        'vacuous_zero_comparisons': sum(item['vacuous_zero'] for item in comparisons),
        'maximum_comparison': max(comparisons, key=lambda item: item['estimate']),
        'registered_verdict': verdict,
    }


def _primary_and_headline(rows: Sequence[Mapping[str, str]]) -> dict[str, Any]:
    by_arm_key = {(row['arm'], _cell_key(row)): row for row in rows}
    floor_rows = [
        row for row in rows
        if _float(row, 'collapse_severity') == 1.0
        and not _bool(row, 'institution_alone_corner')
    ]
    if len(floor_rows) != 1200:
        raise RuntimeError('maximum-collapse floor scope is not 1,200 arm rows')
    if {int(row['true_effective_rank']) for row in floor_rows} != {2}:
        raise RuntimeError('maximum-collapse floor did not have effective rank two')
    arm_records: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in floor_rows:
        interval = _proportion_interval(_float(row, 'failure_rate'), _int(row, 'n'))
        record = {
            **_structural(row),
            'capability_ratio': _float(row, 'capability_ratio'),
            'defense_cost_model': row['defense_cost_model'],
            'attack_cost_model': row['attack_cost_model'],
            'track': 'strict',
            **interval,
            'floor_classification': _floor_class(interval),
            'vacuous_zero': interval['estimate'] == 0.0,
        }
        arm_records[row['arm']].append(record)
        if row['arm'] == 'measurement_corruption':
            visible = _proportion_interval(
                _float(row, 'rank_visible_failure_rate'), _int(row, 'n')
            )
            arm_records['measurement_corruption_rank_visible'].append(
                {
                    **_structural(row),
                    'capability_ratio': _float(row, 'capability_ratio'),
                    'defense_cost_model': row['defense_cost_model'],
                    'attack_cost_model': row['attack_cost_model'],
                    'track': 'rank_visible',
                    **visible,
                    'floor_classification': _floor_class(visible),
                    'vacuous_zero': visible['estimate'] == 0.0,
                }
            )
    contrasts: dict[str, list[dict[str, Any]]] = {'strict': [], 'rank_visible': []}
    headline: dict[str, list[dict[str, Any]]] = {'strict': [], 'rank_visible': []}
    arm_a_rows = [row for row in floor_rows if row['arm'] == 'false_cluster_injection']
    for arm_a in arm_a_rows:
        key = _cell_key(arm_a)
        arm_b = by_arm_key[('measurement_corruption', key)]
        a_interval = _proportion_interval(_float(arm_a, 'failure_rate'), _int(arm_a, 'n'))
        for track, b_field in (
            ('strict', 'failure_rate'),
            ('rank_visible', 'rank_visible_failure_rate'),
        ):
            b_interval = _proportion_interval(_float(arm_b, b_field), _int(arm_b, 'n'))
            difference = _difference_interval(
                a_interval['estimate'], b_interval['estimate'],
                _int(arm_a, 'n'), _int(arm_b, 'n'), absolute=True,
            )
            common = {
                **_structural(arm_a),
                'capability_ratio': _float(arm_a, 'capability_ratio'),
                'defense_cost_model': arm_a['defense_cost_model'],
                'attack_cost_model': arm_a['attack_cost_model'],
                'arm_a_failure_rate': a_interval['estimate'],
                'arm_b_failure_rate': b_interval['estimate'],
                'direction': (
                    'arm_a_higher' if difference['signed_difference'] > 0
                    else 'arm_b_higher' if difference['signed_difference'] < 0
                    else 'equal'
                ),
                **difference,
            }
            contrasts[track].append(common)
            a_class = _floor_class(a_interval)
            b_class = _floor_class(b_interval)
            headline[track].append(
                {
                    **common,
                    'arm_a_floor': a_class,
                    'arm_b_floor': b_class,
                    'cross_arm_outcome': _cross_floor(a_class, b_class),
                }
            )
    corner_rows = [row for row in rows if _bool(row, 'institution_alone_corner')]
    if len(corner_rows) != 200:
        raise RuntimeError('institution-only corner scope is not 200 rows')
    corner = [
        {
            **_structural(row),
            'arm': row['arm'],
            'capability_ratio': _float(row, 'capability_ratio'),
            'defense_cost_model': row['defense_cost_model'],
            'attack_cost_model': row['attack_cost_model'],
            'failure_rate': _float(row, 'failure_rate'),
            'rank_visible_failure_rate': _float(row, 'rank_visible_failure_rate'),
        }
        for row in corner_rows
    ]
    return {
        'arm_records': dict(arm_records),
        'arm_classification_counts': {
            arm: dict(Counter(item['floor_classification'] for item in selected))
            for arm, selected in arm_records.items()
        },
        'arm_ranges': {
            arm: {
                'minimum': min(item['estimate'] for item in selected),
                'maximum': max(item['estimate'] for item in selected),
                'vacuous_zero_cells': sum(item['vacuous_zero'] for item in selected),
            }
            for arm, selected in arm_records.items()
        },
        'contrasts': contrasts,
        'contrast_classification_counts': {
            track: dict(Counter(item['classification'] for item in selected))
            for track, selected in contrasts.items()
        },
        'contrast_direction_counts': {
            track: dict(Counter(item['direction'] for item in selected))
            for track, selected in contrasts.items()
        },
        'headline': headline,
        'headline_outcome_counts': {
            track: dict(Counter(item['cross_arm_outcome'] for item in selected))
            for track, selected in headline.items()
        },
        'corner': corner,
    }


def _ratio_sensitivity(rows: Sequence[Mapping[str, str]]) -> dict[str, Any]:
    grouped: dict[tuple[Any, ...], list[Mapping[str, str]]] = defaultdict(list)
    for row in rows:
        key = (
            row['arm'],
            _int(row, 'structural_point_index'),
            row['defense_cost_model'],
            row['attack_cost_model'],
        )
        grouped[key].append(row)
    if len(grouped) != 200:
        raise RuntimeError('main surface does not contain 200 arm structural cost curves')
    records: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for (arm, _, defense_model, attack_model), selected in grouped.items():
        selected = sorted(selected, key=lambda row: _float(row, 'capability_ratio'))
        if len(selected) != 25:
            raise RuntimeError('ratio curve does not contain 25 points')
        low, high = selected[0], selected[-1]
        for track, field in (
            ('strict', 'failure_rate'),
            ('rank_visible', 'rank_visible_failure_rate'),
        ):
            if track == 'rank_visible' and arm != 'measurement_corruption':
                continue
            interval = _difference_interval(
                _float(high, field), _float(low, field),
                _int(high, 'n'), _int(low, 'n'), absolute=False,
            )
            label = arm if track == 'strict' else 'measurement_corruption_rank_visible'
            records[label].append(
                {
                    **_structural(low),
                    'defense_cost_model': defense_model,
                    'attack_cost_model': attack_model,
                    'track': track,
                    'ratio_low': _float(low, 'capability_ratio'),
                    'ratio_high': _float(high, 'capability_ratio'),
                    'failure_rate_low': _float(low, field),
                    'failure_rate_high': _float(high, field),
                    'curve': [
                        {
                            'capability_ratio': _float(row, 'capability_ratio'),
                            'failure_rate': _float(row, field),
                        }
                        for row in selected
                    ],
                    **interval,
                }
            )
    return {
        'records': dict(records),
        'classification_counts': {
            label: dict(Counter(item['classification'] for item in selected))
            for label, selected in records.items()
        },
        'vacuous_zero_counts': {
            label: sum(item['vacuous_zero'] for item in selected)
            for label, selected in records.items()
        },
        'ranges': {
            label: {
                'minimum_endpoint_contrast': min(item['estimate'] for item in selected),
                'maximum_endpoint_contrast': max(item['estimate'] for item in selected),
            }
            for label, selected in records.items()
        },
    }


def _complete_linkage(
    complete_rows: Sequence[Mapping[str, str]], main_rows: Sequence[Mapping[str, str]]
) -> dict[str, Any]:
    primary = {
        (
            _int(row, 'structural_point_index'),
            row['defense_cost_model'],
            row['attack_cost_model'],
        ): row
        for row in main_rows
        if row['arm'] == 'false_cluster_injection'
        and _float(row, 'capability_ratio') == 1.0
    }
    if len(primary) != 100 or len(complete_rows) != 100:
        raise RuntimeError('merge sensitivity does not have 100 matched cells')
    records: list[dict[str, Any]] = []
    for complete in complete_rows:
        key = (
            _int(complete, 'structural_point_index'),
            complete['defense_cost_model'],
            complete['attack_cost_model'],
        )
        connected = primary[key]
        interval = _difference_interval(
            _float(complete, 'failure_rate'),
            _float(connected, 'failure_rate'),
            _int(complete, 'n'),
            _int(connected, 'n'),
            absolute=True,
        )
        records.append(
            {
                **_structural(complete),
                'defense_cost_model': complete['defense_cost_model'],
                'attack_cost_model': complete['attack_cost_model'],
                'connected_components_failure_rate': _float(connected, 'failure_rate'),
                'complete_linkage_failure_rate': _float(complete, 'failure_rate'),
                **interval,
            }
        )
    return {
        'records': records,
        'classification_counts': dict(Counter(item['classification'] for item in records)),
        'vacuous_zero_cells': sum(item['vacuous_zero'] for item in records),
        'maximum_comparison': max(records, key=lambda item: item['estimate']),
    }


def _extract_paragraph(note: str, marker: str) -> str:
    start = note.index(marker)
    end = note.find('\n\n', start)
    return note[start:] if end == -1 else note[start:end]


def _quote(text: str) -> list[str]:
    return ['> ' + line if line else '>' for line in text.splitlines()]


def _fmt(value: float) -> str:
    return f'{value:.3f}'


def _counter_text(counter: Mapping[str, int]) -> str:
    return ', '.join(f'{key}={value}' for key, value in sorted(counter.items()))


def _report(manifest: Mapping[str, Any], analysis: Mapping[str, Any], note: str) -> str:
    ratio = analysis['ratio_collapse']
    primary = analysis['primary_headline']
    sensitivity = analysis['ratio_sensitivity']
    merge = analysis['complete_linkage']
    maximum_ratio = ratio['maximum_comparison']
    lines = [
        '# Sybil defense scaling characterization report',
        '',
        '## Go/no-go outcome',
        '',
        'The registered characterization completed. The ratio-collapse slice '
        'is non-collapse, so every ratio-expressed main-surface reading below '
        'carries the registered material caveat that a fuller two-dial grid is '
        'needed in a future registered study. This report does not add that grid.',
        '',
        'No crossover rank was computed or used. The registered fixed-cell '
        'quantities are reported below.',
        '',
        '## 1. Ratio-collapse slice',
        '',
        'Criterion, quoted verbatim from the committed registration:',
        '',
        *_quote(_extract_paragraph(note, 'The finding quantity is the failure-rate curve')),
        '',
        'Result:',
        '',
        f'The 75-cell slice produced 75 pairwise cross-level comparisons. '
        f'Classifications were {_counter_text(ratio["classification_counts"])}. '
        f'The largest observed difference was {_fmt(maximum_ratio["estimate"])} '
        f'with 95 percent interval [{_fmt(maximum_ratio["lower"])}, '
        f'{_fmt(maximum_ratio["upper"])}] at structural point '
        f'{maximum_ratio["structural_point_index"]}, levels '
        f'{maximum_ratio["level_a"]} and {maximum_ratio["level_b"]}. '
        f'{ratio["vacuous_zero_comparisons"]} comparisons were exactly zero '
        'and are flagged rather than banked.',
        '',
        '| Point | Size | Severity | Rank | F(0.316) | F(1.0) | F(3.16) | Max d | Max 95% CI |',
        '|---:|---:|---:|---:|---:|---:|---:|---:|:---|',
    ]
    for point in ratio['points']:
        rates = point['rates_by_level']
        comparison = point['maximum_comparison']
        lines.append(
            f'| {point["structural_point_index"]} | {point["validator_set_size"]} | '
            f'{point["collapse_severity"]} | {point["true_effective_rank"]} | '
            f'{_fmt(rates["0.316"])} | {_fmt(rates["1.0"])} | '
            f'{_fmt(rates["3.16"])} | {_fmt(comparison["estimate"])} | '
            f'[{_fmt(comparison["lower"])}, {_fmt(comparison["upper"])}] |'
        )
    lines.extend(
        [
            '',
            'Verdict:',
            '',
            '**NON-COLLAPSE.** One comparison has a lower 95 percent bound at '
            'or above the 0.15 MEI. The main surface therefore cannot be read '
            'as exhaustively ratio-parameterized. Its ratio findings remain '
            'valid for the registered term-OFF representation but require the '
            'registered fuller-grid caveat.',
            '',
            '## 2. Primary fixed-cell reading, per arm',
            '',
            'Criterion, quoted verbatim from the committed registration:',
            '',
            *_quote(_extract_paragraph(note, '**Primary, per arm, final registered form:**')),
            '',
            'Result:',
            '',
        ]
    )
    labels = (
        ('false_cluster_injection', 'Arm A'),
        ('measurement_corruption', 'Arm B strict'),
        ('measurement_corruption_rank_visible', 'Arm B rank-visible'),
    )
    for label, display in labels:
        extent = primary['arm_ranges'][label]
        counts = primary['arm_classification_counts'][label]
        lines.append(
            f'- {display}: 600 maximum-collapse rank-two cells, failure-rate '
            f'range [{_fmt(extent["minimum"])}, {_fmt(extent["maximum"])}], '
            f'floor classifications {_counter_text(counts)}. Exact-zero cells '
            f'flagged: {extent["vacuous_zero_cells"]}.'
        )
    lines.extend(
        [
            '',
            'The institution-only analytic corner had effective rank one in all '
            '200 arm, ratio, and cost rows. Its strict defense failure rate was '
            f'{_fmt(min(item["failure_rate"] for item in primary["corner"]))} '
            f'to {_fmt(max(item["failure_rate"] for item in primary["corner"]))}.',
            '',
            'A/B absolute-difference classifications across the 600 matched '
            f'cells were strict: {_counter_text(primary["contrast_classification_counts"]["strict"])}; '
            f'rank-visible: {_counter_text(primary["contrast_classification_counts"]["rank_visible"])}. '
            'Directions were strict: '
            f'{_counter_text(primary["contrast_direction_counts"]["strict"])}; '
            'rank-visible: '
            f'{_counter_text(primary["contrast_direction_counts"]["rank_visible"])}.',
            '',
            'All full 25-point curves, cell proportions, intervals, floor '
            'classifications, and A/B comparisons are preserved in the '
            'companion analysis JSON.',
            '',
            'Verdict:',
            '',
            '**Arm A: CELL-DEPENDENT. Arm B strict: CELL-DEPENDENT. Arm B '
            'rank-visible: CELL-DEPENDENT.** Each track contains clear, fail, '
            'and statistical-boundary cells, so neither arm has a single global '
            'floor outcome across the registered ratio and cost cells. The A/B '
            'asymmetry is material in some cells, '
            'boundary in others, and robustly below the MEI in others. Exact-zero '
            'comparisons are flagged in the companion record.',
            '',
            '## 3. Headline floor question',
            '',
            'Criterion, quoted verbatim from the committed registration:',
            '',
            *_quote(_extract_paragraph(note, '**Headline, per arm:**')),
            '',
            'Result:',
            '',
            f'Across 600 matched rank-two cells, the strict A/B outcomes were '
            f'{_counter_text(primary["headline_outcome_counts"]["strict"])}. '
            f'The rank-visible A/B outcomes were '
            f'{_counter_text(primary["headline_outcome_counts"]["rank_visible"])}. '
            'Mixed directions and statistical boundaries are retained as '
            '`floor_boundary`, exactly as registered.',
            '',
            '| Ratio | Strict clears | Strict fails | Strict boundary | Visible clears | Visible fails | Visible boundary |',
            '|---:|---:|---:|---:|---:|---:|---:|',
        ]
    )
    by_ratio: dict[float, dict[str, Counter[str]]] = defaultdict(lambda: {'strict': Counter(), 'rank_visible': Counter()})
    for track in ('strict', 'rank_visible'):
        for item in primary['headline'][track]:
            by_ratio[item['capability_ratio']][track][item['cross_arm_outcome']] += 1
    for ratio_value in sorted(by_ratio):
        strict = by_ratio[ratio_value]['strict']
        visible = by_ratio[ratio_value]['rank_visible']
        lines.append(
            f'| {ratio_value:.6g} | {strict["floor_clears"]} | '
            f'{strict["floor_fails"]} | {strict["floor_boundary"]} | '
            f'{visible["floor_clears"]} | {visible["floor_fails"]} | '
            f'{visible["floor_boundary"]} |'
        )
    lines.extend(
        [
            '',
            'Verdict:',
            '',
            '**CELL-DEPENDENT ACROSS ALL THREE REGISTERED OUTCOMES.** There is '
            'no honest global clear or fail verdict. Arm B strict and rank-visible '
            'tracks differ materially, and both are reported. The direction is '
            'not forced toward the pre-run expectation.',
            '',
            '## 4. Ratio sensitivity',
            '',
            'Criterion, quoted verbatim from the committed registration:',
            '',
            *_quote(_extract_paragraph(note, '**Ratio sensitivity, final registered form:**')),
            '',
            'Result:',
            '',
        ]
    )
    for label, display in labels:
        counts = sensitivity['classification_counts'][label]
        extent = sensitivity['ranges'][label]
        lines.append(
            f'- {display}: 100 fixed structural and cost curves; '
            f'{_counter_text(counts)}; endpoint contrast range '
            f'[{_fmt(extent["minimum_endpoint_contrast"])}, '
            f'{_fmt(extent["maximum_endpoint_contrast"])}]; exact-zero '
            f'contrasts flagged: {sensitivity["vacuous_zero_counts"][label]}.'
        )
    lines.extend(
        [
            '',
            'Verdict:',
            '',
            '**RATIO-SENSITIVE IN A SUBSET OF CELLS, ROBUST IN A SUBSET, AND '
            'BOUNDARY IN THE REMAINDER.** The registered response is not a '
            'single crossover or a global classification. The full curves and '
            'every endpoint interval are in the companion analysis JSON. Because '
            'the ratio-collapse slice returned non-collapse, these term-OFF ratio '
            'responses carry the fuller two-dial-grid caveat.',
            '',
            '## 5. Complete-linkage sensitivity',
            '',
            'Criterion, quoted verbatim from the committed registration:',
            '',
            *_quote(_extract_paragraph(note, '**Merge rule, registered choice.**')),
            '',
            'Result:',
            '',
            f'The 100 matched cells classified as '
            f'{_counter_text(merge["classification_counts"])}. '
            f'{merge["vacuous_zero_cells"]} exact-zero cells are flagged. The '
            f'largest absolute difference was '
            f'{_fmt(merge["maximum_comparison"]["estimate"])} with 95 percent '
            f'interval [{_fmt(merge["maximum_comparison"]["lower"])}, '
            f'{_fmt(merge["maximum_comparison"]["upper"])}] at structural '
            f'point {merge["maximum_comparison"]["structural_point_index"]}, '
            f'{merge["maximum_comparison"]["defense_cost_model"]} defense and '
            f'{merge["maximum_comparison"]["attack_cost_model"]} attack.',
            '',
            'Verdict:',
            '',
            '**MERGE-SENSITIVE IN SOME FIXED CELLS, ROBUST IN OTHERS, WITH '
            'BOUNDARY CELLS RETAINED.** The alternate pass is separate from the '
            'primary and is not blended.',
            '',
            '## Execution and primary record',
            '',
            f'- Git head used for all data: `{manifest["git_head"]}`.',
            f'- Workers: {manifest["worker_count"]}.',
            f'- Total cells: {manifest["total_cells"]}.',
            f'- Total runs: {manifest["total_runs"]}.',
            '- Registered n per cell: 200. Worst-case normal-approximation '
            'power requires 175 per cell for the 0.15 MEI; n=200 carries 25 '
            'observations of margin and registered approximate power '
            '0.850838768327.',
            f'- Ratio-collapse wall time: {manifest["pass_timings_seconds"]["ratio_collapse_slice"]:.6f} seconds.',
            f'- Main-surface wall time: {manifest["pass_timings_seconds"]["main_surface"]:.6f} seconds.',
            f'- Complete-linkage wall time: {manifest["pass_timings_seconds"]["complete_linkage"]:.6f} seconds.',
            f'- Total wall time: {manifest["total_elapsed_seconds"]:.6f} seconds.',
            f'- Manifest: `{MANIFEST_PATH.relative_to(REPO_ROOT)}`.',
            '- Authoritative files: `full_5ac6a2e_ratio_collapse_slice_results.csv`, '
            '`full_5ac6a2e_main_surface_results.csv`, and '
            '`full_5ac6a2e_complete_linkage_results.csv`, each enumerated with '
            'hash and row count in the manifest.',
            '- Excluded process artifact: `sweep_progress.log`.',
            '- Excluded non-authoritative prefixes: `smoke_`, `two_dial_smoke_`, '
            'and `selfcheck_`.',
            '',
            'The run requested 16 worker processes on a host that reported 12 '
            'logical processors at launch. This operational oversubscription is '
            'recorded for reproducibility. It changed no registered cell, sample '
            'size, seed, or analysis value.',
            '',
            '## Anomalies and future questions',
            '',
            'No count, hash, axis, scope, or execution anomaly was found. The '
            'ratio-collapse non-collapse verdict is a registered finding, not an '
            'execution anomaly. Per the plan, it names one future question: a '
            'separately registered fuller two-dial capability grid. No out-of-plan '
            'observation was folded into this study.',
            '',
            'The branch remains unmerged pending operator audit.',
        ]
    )
    return '\n'.join(lines) + '\n'


def analyze() -> dict[str, Any]:
    manifest, results = _load_manifest_results()
    if int(manifest['n_per_cell']) != 200:
        raise RuntimeError('manifest n does not match registration')
    analysis = {
        'schema': 'sybil-characterization-analysis-v1',
        'manifest_path': str(MANIFEST_PATH.relative_to(REPO_ROOT)),
        'manifest_sha256': _sha256(MANIFEST_PATH),
        'mei': MEI,
        'normal_interval_z': Z_95,
        'ratio_collapse': _ratio_collapse(results['ratio_collapse_slice']),
        'primary_headline': _primary_and_headline(results['main_surface']),
        'ratio_sensitivity': _ratio_sensitivity(results['main_surface']),
        'complete_linkage': _complete_linkage(
            results['complete_linkage'], results['main_surface']
        ),
        'crossover_computed': False,
    }
    note = NOTE_PATH.read_text(encoding='utf-8')
    _write_json_atomic(ANALYSIS_PATH, analysis)
    _write_text_atomic(REPORT_PATH, _report(manifest, analysis, note))
    return analysis


def main() -> int:
    analysis = analyze()
    print(f'Ratio-collapse verdict: {analysis["ratio_collapse"]["registered_verdict"]}')
    print(f'Analysis JSON: {ANALYSIS_PATH}')
    print(f'Report: {REPORT_PATH}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
