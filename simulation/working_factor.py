"""Stage 1.8 working_factor: the discipline boundary interface.

apply_working_factor(allocation, current_state, step) -> delta_state

Maps allocation categories to infrastructure-stock state changes via the
STATE_ALLOCATION_MAPPING configuration in constants_v2_stage18.py. Each
infrastructure stock evolves toward an allocation-determined target via
logistic-growth dynamics (delta = rate * (target - current)).

This is the placeholder for economic specification. Real economic
specification would substitute a more nuanced allocation-to-state mapping
here. The interface (allocation in, delta_state out) is stable; the
internal mapping is replaceable.

Out of scope for working_factor:
  - avg_wb evolution (agent-derived via v1.x.2/v2 bridge -> resource_level
    -> HumanAgent.step)
  - H_N evolution (agent novelty generation)
  - Population dynamics (HumanAgent reproduction and mortality)
  - Constraint application (c_protective, c_suppressive enter via
    existing constraint logic)

See docs/lineage_phi_program_reference.md (Stage 1.8 section) for the
architectural rationale and the discipline boundary commitment.
"""

from constants_v2_stage18 import STATE_ALLOCATION_MAPPING


def apply_working_factor(allocation, current_state, step):
    """Compute infrastructure-stock state changes from allocation.

    Parameters
    ----------
    allocation : dict
        Mapping from allocation category names (e.g., 'x_compute',
        'x_bio_welfare') to allocation values (each in [0, 1], the six
        x_* sum to 1.0).
    current_state : dict
        Mapping from state variable names to current values. Must
        include all state variables referenced as keys in
        STATE_ALLOCATION_MAPPING.
    step : int
        Step number (informational; not used by the placeholder but
        available for future specifications that depend on temporal
        context).

    Returns
    -------
    dict
        Mapping from state variable names (subset of current_state keys)
        to the delta to apply this step. Caller integrates these deltas
        into the state.

    Structural properties (satisfied by this implementation):
      - Budget-constrained: ignores allocation values for categories not
        in the mapping; consumes the named ones only.
      - Monotone in well-spent allocation: target is monotone in alloc
        (positive coefficient); higher alloc -> higher target -> larger
        positive delta when state < target.
      - Bounded above: target is bounded above (clamped to 1.0 in
        STATE_ALLOCATION_MAPPING's target functions); state cannot grow
        without bound.
      - Differentiable/responsive: small alloc changes produce small
        target changes produce small delta changes.
      - State-dependent: delta = rate * (target - current); marginal
        effect depends on current state via the (target - current) gap.
    """
    delta_state = {}
    for state_var, mapping in STATE_ALLOCATION_MAPPING.items():
        allocation_category = mapping['allocation']
        target_function     = mapping['target']
        rate_constant       = mapping['rate']

        alloc_value = float(allocation.get(allocation_category, 0.0))
        current_value = float(current_state.get(state_var, 0.0))
        target = float(target_function(alloc_value, current_state))

        delta_state[state_var] = rate_constant * (target - current_value)

    return delta_state


def apply_delta_state(state_dict, delta_state, clamp_to_unit_interval=True):
    """Helper: apply delta_state to a state dict in place (returning the
    updated dict). Optionally clamps the updated values to [0, 1] since
    all four infrastructure stocks are fractions.
    """
    for state_var, delta in delta_state.items():
        if state_var in state_dict:
            new_value = state_dict[state_var] + delta
            if clamp_to_unit_interval:
                new_value = max(0.0, min(1.0, new_value))
            state_dict[state_var] = new_value
    return state_dict
