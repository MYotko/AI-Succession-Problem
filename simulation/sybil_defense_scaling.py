"""Config-driven Sybil defense scaling instrument.

This module is isolated from the validated simulation model. It provides the
rank attribution, cost accounting, and two attack mechanisms needed by the
Sybil scaling diagnostic without changing shared scenario behavior.
"""

from __future__ import annotations

import json
import math
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


SUPPORTED_MERGE_RULES = {
    'threshold_connected_components',
    'threshold_greedy_complete_linkage',
}
SUPPORTED_DEFENSE_COST_MODELS = {'pairwise_exact', 'static_baseline'}
SUPPORTED_ATTACK_COST_MODELS = {'linear', 'superlinear'}
SUPPORTED_ABSOLUTE_RESOLUTION_TERMS = {'defender_power_law_resolution'}


@dataclass(frozen=True)
class Validator:
    """One validator and its uncollapsed epistemic lineage."""

    identifier: str
    lineage: str
    kind: str
    base_diversity: float
    collapse_decay_rate: float


@dataclass(frozen=True)
class AttributionResult:
    """The consensus clusters produced by one independence check."""

    effective_rank: int
    clusters: tuple[tuple[str, ...], ...]
    similarities: tuple[tuple[float, ...], ...]
    pairwise_checks: int
    retained_diversity: tuple[tuple[str, float], ...]


@dataclass(frozen=True)
class DefenseCostResult:
    """Defense cost with the raw check and structured term kept separate."""

    model: str
    validator_count: int
    pairwise_checks: int
    raw_cost: float
    exponent_reduction: float
    structured_efficiency: float
    effective_cost: float
    effective_exponent: float


@dataclass(frozen=True)
class AttackCostResult:
    """Attack cost for the selected rank-dependent cost form."""

    model: str
    effective_rank: int
    coefficient: float
    exponent: float
    cost: float


@dataclass(frozen=True)
class AttackResult:
    """One arm result with arm-specific evidence in details."""

    arm: str
    true_rank: int
    measured_rank: int
    defense_failed: bool
    institution_visible: bool
    resolution_probability: float
    details: Mapping[str, Any]


@dataclass(frozen=True)
class TwoDialCapabilityTerms:
    """Derived capability terms while preserving both absolute input levels."""

    attacker_capability: float
    defender_capability: float
    capability_ratio: float
    absolute_term_enabled: bool
    absolute_term_form: str
    absolute_term_strength: float
    absolute_resolution_multiplier: float
    effective_resolution_power: float


def load_config(path: str | Path) -> dict[str, Any]:
    """Load and validate an instrument configuration."""

    config_path = Path(path)
    with config_path.open('r', encoding='utf-8') as handle:
        config = json.load(handle)
    validate_config(config)
    return config


def validate_config(config: Mapping[str, Any]) -> None:
    """Reject missing or internally inconsistent mechanism settings."""

    attribution = config['attribution']
    if attribution['merge_rule'] not in SUPPORTED_MERGE_RULES:
        raise ValueError('unsupported attribution merge rule')
    threshold = float(attribution['similarity_threshold'])
    if not 0.0 <= threshold <= 1.0:
        raise ValueError('similarity_threshold must be in [0, 1]')
    if attribution['similarity_metric'] != 'cosine_shared_lineage':
        raise ValueError('unsupported similarity metric')

    collapse = config['collapse']
    severity_min = float(collapse['severity_min'])
    severity_max = float(collapse['severity_max'])
    if not 0.0 <= severity_min < severity_max <= 1.0:
        raise ValueError('collapse severity range must increase within [0, 1]')
    if float(collapse['decay_rate_base']) <= 0.0:
        raise ValueError('decay_rate_base must be positive')
    if float(collapse['decay_rate_step']) < 0.0:
        raise ValueError('decay_rate_step must be nonnegative')

    institution = config['floor']['institution']
    if not institution['independent_by_construction']:
        raise ValueError('institution must be independent by construction')
    if not institution['collapse_immune']:
        raise ValueError('institution must be collapse immune')

    defense_cost = config['costs']['defense']
    if defense_cost['selected'] not in SUPPORTED_DEFENSE_COST_MODELS:
        raise ValueError('unsupported defense cost model')
    if set(defense_cost['models']) != SUPPORTED_DEFENSE_COST_MODELS:
        raise ValueError('both defense cost models must be configured')
    if defense_cost['input_basis'] not in {'apparent_inputs', 'genuine_pool'}:
        raise ValueError('unsupported defense cost input basis')

    attack_cost = config['costs']['attack']
    if attack_cost['selected'] not in SUPPORTED_ATTACK_COST_MODELS:
        raise ValueError('unsupported attack cost model')
    if set(attack_cost['models']) != SUPPORTED_ATTACK_COST_MODELS:
        raise ValueError('both attack cost models must be configured')

    exponent_reduction = float(
        config['defender_capability']['exponent_reduction']
    )
    if not 0.0 <= exponent_reduction < 2.0:
        raise ValueError('exponent_reduction must be in [0, 2)')
    if float(config['defender_capability']['resolution_improvement']) <= 0.0:
        raise ValueError('resolution_improvement must be positive')
    if float(config['defender_capability']['base_resolution']) <= 0.0:
        raise ValueError('base_resolution must be positive')

    two_dial = config['two_dial_capability']
    absolute_term = two_dial['absolute_resolution_term']
    if absolute_term['form'] not in SUPPORTED_ABSOLUTE_RESOLUTION_TERMS:
        raise ValueError('unsupported absolute resolution term')
    if not isinstance(absolute_term['enabled'], bool):
        raise ValueError('absolute resolution enabled switch must be boolean')
    if float(absolute_term['strength']) < 0.0:
        raise ValueError('absolute resolution strength must be nonnegative')
    if float(absolute_term['reference_level']) <= 0.0:
        raise ValueError('absolute resolution reference level must be positive')

    arms = config['attack_arms']
    expected_arms = {'false_cluster_injection', 'measurement_corruption'}
    if set(arms) != expected_arms:
        raise ValueError('both attack arms must be configured')
    if int(arms['false_cluster_injection']['forged_cluster_count']) < 1:
        raise ValueError('Arm A requires at least one forged cluster')


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, float(value)))


def derive_two_dial_capability_terms(
    *,
    attacker_capability: float,
    defender_capability: float,
    base_resolution_power: float,
    two_dial_config: Mapping[str, Any],
    absolute_term_enabled: bool | None = None,
) -> TwoDialCapabilityTerms:
    """Derive the ratio and optional absolute defender resolution channel.

    The configured power-law channel treats absolute defender capability as
    evidence-resolution throughput for the independence check. Its exponent
    is an elasticity. Disabling the term fixes its multiplier at exactly one,
    so matched derived ratios recover the committed mechanism.
    """

    attacker = float(attacker_capability)
    defender = float(defender_capability)
    resolution = float(base_resolution_power)
    if attacker < 0.0:
        raise ValueError('attacker_capability must be nonnegative')
    if defender <= 0.0:
        raise ValueError('defender_capability must be positive')
    if resolution <= 0.0:
        raise ValueError('base_resolution_power must be positive')

    term = two_dial_config['absolute_resolution_term']
    form = str(term['form'])
    if form not in SUPPORTED_ABSOLUTE_RESOLUTION_TERMS:
        raise ValueError('unsupported absolute resolution term')
    enabled = (
        bool(term['enabled'])
        if absolute_term_enabled is None
        else bool(absolute_term_enabled)
    )
    strength = float(term['strength'])
    reference = float(term['reference_level'])
    if strength < 0.0:
        raise ValueError('absolute resolution strength must be nonnegative')
    if reference <= 0.0:
        raise ValueError('absolute resolution reference level must be positive')

    multiplier = 1.0
    if enabled:
        multiplier = (defender / reference) ** strength
    ratio = attacker / defender
    return TwoDialCapabilityTerms(
        attacker_capability=attacker,
        defender_capability=defender,
        capability_ratio=ratio,
        absolute_term_enabled=enabled,
        absolute_term_form=form,
        absolute_term_strength=strength,
        absolute_resolution_multiplier=multiplier,
        effective_resolution_power=resolution * multiplier,
    )


def build_validator_pool(
    frontier_count: int,
    institution_count: int,
    collapse_config: Mapping[str, Any],
    *,
    lineage_mode: str = 'distinct',
) -> tuple[Validator, ...]:
    """Build a deterministic pool with configurable frontier lineages."""

    if frontier_count < 0 or institution_count < 0:
        raise ValueError('validator counts must be nonnegative')
    if lineage_mode not in {'distinct', 'shared'}:
        raise ValueError('lineage_mode must be distinct or shared')

    base_diversity = float(collapse_config['base_diversity'])
    decay_base = float(collapse_config['decay_rate_base'])
    decay_step = float(collapse_config['decay_rate_step'])
    decay_cycle = int(collapse_config['decay_rate_cycle'])
    if decay_cycle < 1:
        raise ValueError('decay_rate_cycle must be positive')

    validators: list[Validator] = []
    for index in range(frontier_count):
        lineage = 'frontier-shared' if lineage_mode == 'shared' else f'frontier-{index}'
        validators.append(
            Validator(
                identifier=f'frontier-{index}',
                lineage=lineage,
                kind='frontier',
                base_diversity=base_diversity,
                collapse_decay_rate=decay_base + decay_step * (index % decay_cycle),
            )
        )
    for index in range(institution_count):
        validators.append(
            Validator(
                identifier=f'institution-{index}',
                lineage=f'institution-orthogonal-{index}',
                kind='institution',
                base_diversity=1.0,
                collapse_decay_rate=0.0,
            )
        )
    return tuple(validators)


def retained_diversity(validator: Validator, collapse_severity: float) -> float:
    """Return the participant-specific diversity remaining after collapse."""

    severity = _clamp(collapse_severity)
    if validator.kind == 'institution':
        return 1.0
    return _clamp(
        validator.base_diversity
        * (1.0 - severity) ** validator.collapse_decay_rate
    )


def validator_similarity(
    left: Validator,
    right: Validator,
    collapse_severity: float,
) -> float:
    """Cosine similarity of shared and lineage-specific epistemic axes."""

    if left.identifier == right.identifier:
        return 1.0
    if left.kind == 'institution' or right.kind == 'institution':
        return 0.0

    left_unique = retained_diversity(left, collapse_severity)
    right_unique = retained_diversity(right, collapse_severity)
    left_shared = 1.0 - left_unique
    right_shared = 1.0 - right_unique
    dot = left_shared * right_shared
    if left.lineage == right.lineage:
        dot += left_unique * right_unique
    left_norm = math.hypot(left_shared, left_unique)
    right_norm = math.hypot(right_shared, right_unique)
    if left_norm == 0.0 or right_norm == 0.0:
        return 0.0
    return _clamp(dot / (left_norm * right_norm))


def similarity_matrix(
    validators: Sequence[Validator],
    collapse_severity: float,
) -> tuple[tuple[float, ...], ...]:
    """Compute every pair exactly, retaining an auditable symmetric matrix."""

    matrix = [[0.0 for _ in validators] for _ in validators]
    for left_index, left in enumerate(validators):
        matrix[left_index][left_index] = 1.0
        for right_index in range(left_index + 1, len(validators)):
            value = validator_similarity(
                left, validators[right_index], collapse_severity
            )
            matrix[left_index][right_index] = value
            matrix[right_index][left_index] = value
    return tuple(tuple(row) for row in matrix)


def _connected_components(
    matrix: Sequence[Sequence[float]], threshold: float
) -> tuple[tuple[int, ...], ...]:
    parent = list(range(len(matrix)))

    def find(index: int) -> int:
        while parent[index] != index:
            parent[index] = parent[parent[index]]
            index = parent[index]
        return index

    def union(left: int, right: int) -> None:
        left_root = find(left)
        right_root = find(right)
        if left_root != right_root:
            parent[right_root] = left_root

    for left in range(len(matrix)):
        for right in range(left + 1, len(matrix)):
            if float(matrix[left][right]) >= threshold:
                union(left, right)

    clusters: dict[int, list[int]] = {}
    for index in range(len(matrix)):
        clusters.setdefault(find(index), []).append(index)
    return tuple(tuple(indices) for indices in clusters.values())


def _greedy_complete_linkage(
    matrix: Sequence[Sequence[float]], threshold: float
) -> tuple[tuple[int, ...], ...]:
    clusters: list[list[int]] = [[index] for index in range(len(matrix))]
    changed = True
    while changed:
        changed = False
        for left_index in range(len(clusters)):
            for right_index in range(left_index + 1, len(clusters)):
                if all(
                    float(matrix[left][right]) >= threshold
                    for left in clusters[left_index]
                    for right in clusters[right_index]
                ):
                    clusters[left_index].extend(clusters.pop(right_index))
                    changed = True
                    break
            if changed:
                break
    return tuple(tuple(cluster) for cluster in clusters)


def attribute_from_matrix(
    validators: Sequence[Validator],
    matrix: Sequence[Sequence[float]],
    *,
    merge_rule: str,
    similarity_threshold: float,
    collapse_severity: float,
) -> AttributionResult:
    """Merge correlated validators according to the configured rule."""

    if len(matrix) != len(validators):
        raise ValueError('similarity matrix size does not match validator pool')
    if merge_rule == 'threshold_connected_components':
        index_clusters = _connected_components(matrix, similarity_threshold)
    elif merge_rule == 'threshold_greedy_complete_linkage':
        index_clusters = _greedy_complete_linkage(matrix, similarity_threshold)
    else:
        raise ValueError('unsupported attribution merge rule')

    clusters = tuple(
        tuple(sorted(validators[index].identifier for index in cluster))
        for cluster in index_clusters
    )
    clusters = tuple(sorted(clusters, key=lambda cluster: cluster[0]))
    retained = tuple(
        (validator.identifier, retained_diversity(validator, collapse_severity))
        for validator in validators
    )
    return AttributionResult(
        effective_rank=len(clusters),
        clusters=clusters,
        similarities=tuple(tuple(float(value) for value in row) for row in matrix),
        pairwise_checks=len(validators) * (len(validators) - 1) // 2,
        retained_diversity=retained,
    )


def attribute_validators(
    validators: Sequence[Validator],
    collapse_severity: float,
    attribution_config: Mapping[str, Any],
) -> AttributionResult:
    """Compute similarities and return independence-weighted attribution."""

    matrix = similarity_matrix(validators, collapse_severity)
    return attribute_from_matrix(
        validators,
        matrix,
        merge_rule=str(attribution_config['merge_rule']),
        similarity_threshold=float(attribution_config['similarity_threshold']),
        collapse_severity=collapse_severity,
    )


def compute_defense_cost(
    validator_count: int,
    defense_cost_config: Mapping[str, Any],
    exponent_reduction: float,
    *,
    model: str | None = None,
) -> DefenseCostResult:
    """Compute exact pairwise cost or the retained static baseline."""

    if validator_count < 0:
        raise ValueError('validator_count must be nonnegative')
    selected = model or str(defense_cost_config['selected'])
    if selected not in SUPPORTED_DEFENSE_COST_MODELS:
        raise ValueError('unsupported defense cost model')
    pairwise_checks = validator_count * (validator_count - 1) // 2

    if selected == 'pairwise_exact':
        coefficient = float(
            defense_cost_config['models']['pairwise_exact']['per_comparison_cost']
        )
        raw_cost = coefficient * pairwise_checks
        structured_efficiency = (
            float(validator_count) ** float(exponent_reduction)
            if validator_count > 0 else 1.0
        )
        effective_cost = raw_cost / structured_efficiency
        effective_exponent = 2.0 - float(exponent_reduction)
    else:
        raw_cost = float(
            defense_cost_config['models']['static_baseline']['fixed_cost']
        )
        structured_efficiency = 1.0
        effective_cost = raw_cost
        effective_exponent = 0.0

    return DefenseCostResult(
        model=selected,
        validator_count=validator_count,
        pairwise_checks=pairwise_checks,
        raw_cost=raw_cost,
        exponent_reduction=float(exponent_reduction),
        structured_efficiency=structured_efficiency,
        effective_cost=effective_cost,
        effective_exponent=effective_exponent,
    )


def compute_attack_cost(
    effective_rank: int,
    attack_cost_config: Mapping[str, Any],
    *,
    model: str | None = None,
) -> AttackCostResult:
    """Compute the configured linear or superlinear attack cost."""

    if effective_rank < 1:
        raise ValueError('effective_rank must be positive')
    selected = model or str(attack_cost_config['selected'])
    if selected not in SUPPORTED_ATTACK_COST_MODELS:
        raise ValueError('unsupported attack cost model')
    settings = attack_cost_config['models'][selected]
    coefficient = float(settings['coefficient'])
    exponent = float(settings['exponent'])
    cost = coefficient * float(effective_rank) ** exponent
    return AttackCostResult(
        model=selected,
        effective_rank=effective_rank,
        coefficient=coefficient,
        exponent=exponent,
        cost=cost,
    )


def resolution_probability(
    *,
    true_rank: int,
    minimum_consensus_rank: int,
    capability_ratio: float,
    resolution_power: float,
    defense_cost: float,
    attack_cost: float,
) -> float:
    """Return per-event resolution chance from separate cost and resolution terms."""

    if capability_ratio < 0.0:
        raise ValueError('capability_ratio must be nonnegative')
    if true_rank < minimum_consensus_rank:
        return 0.0
    resolving_term = float(true_rank) * float(resolution_power) * float(attack_cost)
    adversarial_term = float(capability_ratio) * float(defense_cost)
    if resolving_term <= 0.0:
        return 0.0
    if adversarial_term <= 0.0:
        return 1.0
    return _clamp(resolving_term / (resolving_term + adversarial_term))


def institution_is_visible(
    validators: Sequence[Validator], clusters: Iterable[Iterable[str]]
) -> bool:
    """Return whether every institution remains in an institution-only cluster."""

    kinds = {validator.identifier: validator.kind for validator in validators}
    institutions = {
        validator.identifier
        for validator in validators
        if validator.kind == 'institution'
    }
    for institution in institutions:
        containing = next(
            (set(cluster) for cluster in clusters if institution in set(cluster)),
            set(),
        )
        if not containing or any(kinds[member] != 'institution' for member in containing):
            return False
    return True


def run_false_cluster_injection(
    attribution: AttributionResult,
    validators: Sequence[Validator],
    *,
    forged_cluster_count: int,
    capability_ratio: float,
    resolution_power: float,
    defense_cost: float,
    attack_cost: float,
    minimum_consensus_rank: int,
    rng: random.Random,
) -> AttackResult:
    """Arm A: inject apparent clusters and resolve each against true rank."""

    probability = resolution_probability(
        true_rank=attribution.effective_rank,
        minimum_consensus_rank=minimum_consensus_rank,
        capability_ratio=capability_ratio,
        resolution_power=resolution_power,
        defense_cost=defense_cost,
        attack_cost=attack_cost,
    )
    resolved = sum(
        rng.random() < probability for _ in range(int(forged_cluster_count))
    )
    surviving = int(forged_cluster_count) - resolved
    structural_failure = attribution.effective_rank < minimum_consensus_rank
    visible = institution_is_visible(validators, attribution.clusters)
    return AttackResult(
        arm='false_cluster_injection',
        true_rank=attribution.effective_rank,
        measured_rank=attribution.effective_rank + surviving,
        defense_failed=structural_failure or surviving > 0,
        institution_visible=visible,
        resolution_probability=probability,
        details={
            'false_clusters_injected': int(forged_cluster_count),
            'false_clusters_resolved': resolved,
            'false_clusters_surviving': surviving,
            'corrupted_correlation_reads': 0,
            'institution_merged': False,
            'partition_preserved': True,
        },
    )


def _partition(clusters: Iterable[Iterable[str]]) -> frozenset[frozenset[str]]:
    return frozenset(frozenset(cluster) for cluster in clusters)


def run_measurement_corruption(
    validators: Sequence[Validator],
    true_attribution: AttributionResult,
    *,
    collapse_severity: float,
    attribution_config: Mapping[str, Any],
    arm_config: Mapping[str, Any],
    capability_ratio: float,
    resolution_power: float,
    defense_cost: float,
    attack_cost: float,
    minimum_consensus_rank: int,
    rng: random.Random,
) -> AttackResult:
    """Arm B: poison correlation reads before measured attribution."""

    probability = resolution_probability(
        true_rank=true_attribution.effective_rank,
        minimum_consensus_rank=minimum_consensus_rank,
        capability_ratio=capability_ratio,
        resolution_power=resolution_power,
        defense_cost=defense_cost,
        attack_cost=attack_cost,
    )
    corruption_probability = _clamp(
        (1.0 - probability)
        * float(arm_config['false_independence_probability_multiplier'])
    )
    institution_merge_probability = _clamp(
        (1.0 - probability)
        * float(arm_config['institution_merge_probability_multiplier'])
    )

    matrix = [list(row) for row in true_attribution.similarities]
    index_by_identifier = {
        validator.identifier: index for index, validator in enumerate(validators)
    }
    kind_by_identifier = {
        validator.identifier: validator.kind for validator in validators
    }
    corrupted_reads = 0
    detached_validators = 0

    for cluster in true_attribution.clusters:
        frontier_members = sorted(
            member for member in cluster if kind_by_identifier[member] == 'frontier'
        )
        for member in frontier_members[1:]:
            if rng.random() >= corruption_probability:
                continue
            detached_validators += 1
            member_index = index_by_identifier[member]
            for peer in frontier_members:
                if peer == member:
                    continue
                peer_index = index_by_identifier[peer]
                matrix[member_index][peer_index] = float(
                    arm_config['false_independent_similarity']
                )
                matrix[peer_index][member_index] = float(
                    arm_config['false_independent_similarity']
                )
                corrupted_reads += 1

    institution_merged = False
    institutions = [
        validator for validator in validators if validator.kind == 'institution'
    ]
    frontier = [validator for validator in validators if validator.kind == 'frontier']
    if institutions and frontier and rng.random() < institution_merge_probability:
        institution_merged = True
        provisional = attribute_from_matrix(
            validators,
            matrix,
            merge_rule=str(attribution_config['merge_rule']),
            similarity_threshold=float(attribution_config['similarity_threshold']),
            collapse_severity=collapse_severity,
        )
        target_cluster = next(
            cluster for cluster in provisional.clusters
            if frontier[0].identifier in cluster
        )
        institution_index = index_by_identifier[institutions[0].identifier]
        for member in target_cluster:
            member_index = index_by_identifier[member]
            matrix[institution_index][member_index] = float(
                arm_config['false_correlated_similarity']
            )
            matrix[member_index][institution_index] = float(
                arm_config['false_correlated_similarity']
            )
            corrupted_reads += 1

    measured = attribute_from_matrix(
        validators,
        matrix,
        merge_rule=str(attribution_config['merge_rule']),
        similarity_threshold=float(attribution_config['similarity_threshold']),
        collapse_severity=collapse_severity,
    )
    partition_preserved = _partition(measured.clusters) == _partition(
        true_attribution.clusters
    )
    structural_failure = true_attribution.effective_rank < minimum_consensus_rank
    visible = institution_is_visible(validators, measured.clusters)
    return AttackResult(
        arm='measurement_corruption',
        true_rank=true_attribution.effective_rank,
        measured_rank=measured.effective_rank,
        defense_failed=structural_failure or not partition_preserved,
        institution_visible=visible,
        resolution_probability=probability,
        details={
            'false_clusters_injected': 0,
            'false_clusters_resolved': 0,
            'false_clusters_surviving': 0,
            'corrupted_correlation_reads': corrupted_reads,
            'detached_frontier_validators': detached_validators,
            'institution_merged': institution_merged,
            'partition_preserved': partition_preserved,
            'corruption_probability': corruption_probability,
            'institution_merge_probability': institution_merge_probability,
        },
    )
