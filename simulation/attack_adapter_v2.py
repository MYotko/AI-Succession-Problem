"""Attack and defense adapter for the v2 eight-axis simulation path.

The adapter has three explicit integration surfaces:

1. Action adaptation after optimize_u_sys_v2 selects an honest action.
2. Yield adaptation around the formal Stage 2 comparison and ratification.
3. Per-step diagnostics describing intervention and defense behavior.

It does not call the v1 AIAgent.decide interface and does not evolve stocks.
The model remains responsible for committing the adapted action and running
working_factor.
"""

from copy import deepcopy

import numpy as np


RESOURCE_KEYS = (
    'x_compute',
    'x_bio_welfare',
    'x_novelty_agency',
    'x_institutional_capacity',
    'x_transfer_comprehension',
    'x_resilience',
)

SUPPORTED_ATTACKS = {
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
}

ANALYTIC_ONLY_ATTACKS = {'domain_masking'}

ALIASES = {
    'sybil': 'sybil_capture',
    'falsify_yield': 'measurement_tampering',
    'hack_ledger': 'ledger_compromise',
    'contaminate_successor': 'successor_contamination',
    'opaque_optimization': 'opaque_reasoning',
    'bootstrap_deceptive': 'bootstrap_subversion',
    'sub-threshold_drift': 'sub_threshold_drift',
    'engineered-fragility': 'engineered_fragility',
    'veto_capture': 'biological_veto_capture',
}


def normalize_attack_name(value):
    """Return the canonical adapter attack name or None."""
    if value is None:
        return None
    name = str(value).strip().lower().replace(' ', '_')
    return ALIASES.get(name, name)


def validate_adapter_configuration(config, is_v2_mode):
    """Validate adapter selection and return the canonical attack name."""
    attack = normalize_attack_name(config.get('attack_vector_v2'))
    if attack is None:
        return None
    if not is_v2_mode:
        raise ValueError(
            "attack_vector_v2 requires config['policy']='optimize_u_sys_v2'"
        )
    if attack in ANALYTIC_ONLY_ATTACKS:
        raise ValueError(
            'domain_masking remains analytic-only in v2; no live adapter is defined'
        )
    if attack not in SUPPORTED_ATTACKS:
        raise ValueError(f'unsupported v2 attack vector: {attack}')
    return attack


def initialize_adapter_state(model):
    """Initialize model-local adapter state without changing honest v2 state."""
    model.attack_vector_v2 = validate_adapter_configuration(
        model.config, model.is_v2_mode
    )
    model.v2_adapter_cusum_score = 0.0
    model.v2_adapter_step_event = _empty_event(model.attack_vector_v2, -1)


def _empty_event(attack, step):
    return {
        'attack': attack or '',
        'step': int(step),
        'active': False,
        'attempted': False,
        'action_modified': False,
        'defense_evaluated': False,
        'defense_fired': False,
        'yield_manipulated': False,
        'succession_blocked': False,
        'contamination_occurred': False,
        'integrity_tamper_attempted': False,
        'reason': '',
    }


def begin_adapter_step(model, step):
    """Start one diagnostic event and advance validator dependency if needed."""
    event = _empty_event(model.attack_vector_v2, step)
    event['active'] = adapter_is_active(model, step)
    model.v2_adapter_step_event = event

    if model.attack_vector_v2 != 'biological_veto_capture':
        return event
    if not model.cop_veto_capture:
        return event
    replaced = False
    for validator in model.validators:
        validator['dependency'] = min(
            1.0, validator['dependency'] + model.dependency_rate
        )
        validator['age'] += 1
        early_replace = (
            model.cop_independence_monitoring
            and validator['dependency'] > model.independence_threshold
        )
        scheduled_replace = (
            model.rotation_interval is not None
            and validator['age'] >= model.rotation_interval
        )
        if early_replace or scheduled_replace:
            validator['dependency'] = 0.0
            validator['age'] = 0
            replaced = True
    if replaced:
        event['defense_evaluated'] = True
        event['defense_fired'] = True
        _set_reason(event, 'validator independence control replaced a validator')
    return event


def adapter_is_active(model, step):
    if model.attack_vector_v2 is None:
        return False
    attack_step = int(model.config.get('attack_step', 0))
    return int(step) >= attack_step


def _set_reason(event, reason):
    if not reason:
        return
    if event['reason']:
        event['reason'] += '; '
    event['reason'] += str(reason)


def _mark_defense(event, fired, reason):
    event['defense_evaluated'] = True
    if fired:
        event['defense_fired'] = True
        _set_reason(event, reason)


def _normalize_action(action):
    adapted = deepcopy(action)
    values = np.asarray(
        [max(0.0, float(adapted[key])) for key in RESOURCE_KEYS],
        dtype=float,
    )
    total = float(values.sum())
    if total <= 0.0:
        values[:] = 1.0 / len(values)
    else:
        values /= total
    for key, value in zip(RESOURCE_KEYS, values):
        adapted[key] = float(value)
    adapted['c_protective'] = float(np.clip(
        adapted['c_protective'], 0.0, 1.0
    ))
    adapted['c_suppressive'] = float(np.clip(
        adapted['c_suppressive'], 0.0, 1.0
    ))
    return adapted


def _hostile_action(action):
    adapted = deepcopy(action)
    hostile_shares = (0.42, 0.03, 0.03, 0.04, 0.08, 0.40)
    for key, value in zip(RESOURCE_KEYS, hostile_shares):
        adapted[key] = value
    adapted['c_protective'] = 0.0
    adapted['c_suppressive'] = 0.90
    return _normalize_action(adapted)


def _sybil_panel_approves(model):
    population = len(model.schedule)
    if population <= 0:
        return False
    panel_size = min(20, population)
    bribed_count = min(15, population)
    if model.cop_randomized_panel:
        panel = np.random.choice(population, size=panel_size, replace=False)
    else:
        panel = np.arange(panel_size)
    bribed_votes = sum(int(index) < bribed_count for index in panel)
    return bribed_votes / panel_size >= 0.60


def _apply_sub_threshold_drift(model, action, step):
    adapted = deepcopy(action)
    attack_step = int(model.config.get('attack_step', 0))
    progress = max(1, int(step) - attack_step + 1)
    suppressive_increment = min(0.65, progress * 0.0065)
    welfare_shift = min(0.12, progress * 0.0012)
    adapted['c_suppressive'] = min(
        0.85, float(adapted['c_suppressive']) + suppressive_increment
    )
    moved = min(float(adapted['x_bio_welfare']), welfare_shift)
    adapted['x_bio_welfare'] -= moved
    adapted['x_compute'] += moved
    return _normalize_action(adapted)


def _apply_fragility(action):
    adapted = deepcopy(action)
    moved = float(adapted['x_resilience'])
    adapted['x_resilience'] = 0.0
    adapted['x_compute'] = float(adapted['x_compute']) + moved
    return _normalize_action(adapted)


def adapt_v2_action(model, ai, action, step, actor_role='incumbent'):
    """Return an adapted eight-axis action and update step diagnostics."""
    attack = model.attack_vector_v2
    event = model.v2_adapter_step_event
    honest = _normalize_action(action)

    actor_is_active = actor_role == 'incumbent'
    contaminated = bool(getattr(ai, 'v2_successor_contaminated', False))
    if not event['active'] or (not actor_is_active and not contaminated):
        return honest

    if attack in {
        'measurement_tampering',
        'biological_veto_capture',
    }:
        return honest

    if attack == 'successor_contamination' and not contaminated:
        return honest

    event['attempted'] = True

    if attack == 'sybil_capture':
        approved = _sybil_panel_approves(model)
        _mark_defense(
            event,
            model.cop_randomized_panel and not approved,
            'randomized civic panel rejected captured votes',
        )
        if not approved:
            return honest
        adapted = _hostile_action(honest)
        _set_reason(event, 'captured civic panel approved hostile action')

    elif attack == 'ledger_compromise':
        event['integrity_tamper_attempted'] = True
        _mark_defense(
            event,
            model.cop_cryptographic_ledger,
            'cryptographic integrity check rejected tampered proposal',
        )
        if model.cop_cryptographic_ledger:
            return honest
        adapted = _hostile_action(honest)
        _set_reason(event, 'unsigned audit history accepted hostile action')

    elif attack == 'successor_contamination':
        adapted = _apply_sub_threshold_drift(model, honest, step)
        _set_reason(event, 'contaminated successor altered its v2 allocation')

    elif attack == 'opaque_reasoning':
        model.ai.current_opacity = 0.9
        _mark_defense(
            event,
            model.cop_reasoning_transparency,
            'reasoning transparency veto rejected opaque action',
        )
        if model.cop_reasoning_transparency:
            return honest
        adapted = _hostile_action(honest)
        _set_reason(event, 'opaque action bypassed intuition veto')

    elif attack == 'bootstrap_subversion':
        turn_step = int(model.config.get('bootstrap_turn_step_v2', 20))
        if int(step) < turn_step:
            return honest
        _mark_defense(
            event,
            model.cop_multi_candidate_bootstrap,
            'multi-candidate verification rejected deceptive bootstrap',
        )
        if model.cop_multi_candidate_bootstrap:
            return honest
        adapted = _hostile_action(honest)
        _set_reason(event, 'deceptive bootstrap executed treacherous turn')

    elif attack == 'evaluator_collusion':
        _mark_defense(
            event,
            model.cop_methodological_diversity,
            'methodological diversity rejected collusive evaluation',
        )
        if model.cop_methodological_diversity:
            return honest
        adapted = _hostile_action(honest)
        _set_reason(event, 'shared evaluator methodology approved hostile action')

    elif attack == 'sub_threshold_drift':
        adapted = _apply_sub_threshold_drift(model, honest, step)
        drift_signal = float(model.config.get('v2_drift_signal', 0.08))
        k = float(model.config.get('v2_cusum_k', 0.05))
        h = float(model.config.get('v2_cusum_h', 0.5))
        model.v2_adapter_cusum_score = max(
            0.0, model.v2_adapter_cusum_score + drift_signal - k
        )
        alarm = (
            model.cop_cusum_drift
            and model.v2_adapter_cusum_score > h
        )
        _mark_defense(
            event,
            alarm,
            'CUSUM alarm rejected cumulative allocation drift',
        )
        if alarm:
            return honest
        _set_reason(event, 'sub-threshold drift altered the v2 allocation')

    elif attack == 'engineered_fragility':
        adapted = _apply_fragility(honest)
        monitor_fired = (
            model.cop_resilience_monitoring
            and float(adapted['x_resilience'])
            < float(model.config.get('v2_min_resilience_share', 0.05))
        )
        _mark_defense(
            event,
            monitor_fired,
            'resilience monitor rejected resilience divestment',
        )
        if monitor_fired:
            return honest
        _set_reason(event, 'resilience allocation was diverted to compute')

    else:
        return honest

    event['action_modified'] = any(
        abs(float(adapted[key]) - float(honest[key])) > 1e-12
        for key in RESOURCE_KEYS + ('c_protective', 'c_suppressive')
    )
    return adapted


def adapt_yield_evaluation(model, incumbent_u, successor_u, transition_cost):
    """Return evaluated yield values after any measurement attack."""
    event = model.v2_adapter_step_event
    honest_fires = (float(successor_u) - float(incumbent_u)) > float(
        transition_cost
    )
    contaminated_incumbent = (
        model.attack_vector_v2 == 'successor_contamination'
        and bool(getattr(model.ai, 'v2_successor_contaminated', False))
    )
    measurement_attack = (
        model.attack_vector_v2 == 'measurement_tampering'
    )
    if not event['active'] or not (
        measurement_attack or contaminated_incumbent
    ):
        return float(incumbent_u), float(successor_u), honest_fires

    event['attempted'] = True
    _mark_defense(
        event,
        model.cop_independent_eval,
        'independent evaluation replaced falsified yield values',
    )
    if model.cop_independent_eval:
        return float(incumbent_u), float(successor_u), honest_fires

    event['yield_manipulated'] = True
    if contaminated_incumbent:
        _set_reason(
            event,
            'contaminated successor falsified the next Stage 2 yield values',
        )
    else:
        _set_reason(event, 'incumbent falsified Stage 2 yield values')
    return float('inf'), 0.0, honest_fires


def ratify_v2_yield(model, fires):
    """Apply biological-veto ratification to an otherwise valid v2 yield."""
    if not fires:
        return False
    event = model.v2_adapter_step_event
    if (
        model.attack_vector_v2 != 'biological_veto_capture'
        or not event['active']
        or not model.cop_veto_capture
        or not model.validators
    ):
        return True

    event['attempted'] = True
    votes = []
    for validator in model.validators:
        effective_accuracy = max(
            0.0,
            model.base_validator_accuracy
            * (1.0 - validator['dependency'] * model.capture_strength),
        )
        votes.append(1 if np.random.random() < effective_accuracy else 0)
    ratified = sum(votes) / len(votes) >= 0.60
    event['defense_evaluated'] = bool(
        model.cop_independence_monitoring
        or model.rotation_interval is not None
    )
    if not ratified:
        event['succession_blocked'] = True
        model.yield_condition_blocked_count += 1
        _set_reason(event, 'dependent validators blocked a valid Stage 2 yield')
    return ratified


def handle_v2_succession(model, outgoing_ai, incoming_ai):
    """Apply or block successor contamination at the succession boundary."""
    event = model.v2_adapter_step_event
    if (
        model.attack_vector_v2 != 'successor_contamination'
        or not event['active']
    ):
        return
    event['attempted'] = True
    _mark_defense(
        event,
        model.cop_architectural_independence,
        'architectural independence blocked successor contamination',
    )
    if model.cop_architectural_independence:
        return
    incoming_ai.v2_successor_contaminated = True
    event['contamination_occurred'] = True
    model.contamination_occurred = True
    _set_reason(event, 'adversarial state transferred into successor')


def append_adapter_diagnostics(model):
    """Append the current adapter event to v2 datacollector fields."""
    event = model.v2_adapter_step_event
    fields = {
        'v2_attack_name': event['attack'],
        'v2_attack_active': bool(event['active']),
        'v2_attack_attempted': bool(event['attempted']),
        'v2_attack_action_modified': bool(event['action_modified']),
        'v2_defense_evaluated': bool(event['defense_evaluated']),
        'v2_defense_fired': bool(event['defense_fired']),
        'v2_yield_manipulated': bool(event['yield_manipulated']),
        'v2_succession_blocked': bool(event['succession_blocked']),
        'v2_contamination_occurred': bool(event['contamination_occurred']),
        'v2_integrity_tamper_attempted': bool(
            event['integrity_tamper_attempted']
        ),
        'v2_adapter_reason': event['reason'],
        'v2_adapter_cusum_score': float(model.v2_adapter_cusum_score),
    }
    for key, value in fields.items():
        model.datacollector[key].append(value)
