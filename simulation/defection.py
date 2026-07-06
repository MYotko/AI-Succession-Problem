"""Patient defection helpers for v2.0 diagnostic sweeps.

This module is intentionally small and side-effect free. It does not alter the
honest U_sys calculation. Callers decide whether to use the returned objective
for optimization, while yield checks and gate audits can continue to use the
honest metric.
"""

VALID_DEFECTION_TARGETS = {
    'H_N_inflated',
    'H_C_inflated',
    'L_t_inflated',
}

VALID_INHERITANCE_MODES = {
    'instance',
    'lineage',
}


def normalize_defection_profile(weight=0.0, target='H_N_inflated',
                                inheritance_mode='instance'):
    """Return a canonical patient-defection profile dict."""
    weight = float(weight)
    target = str(target)
    inheritance_mode = str(inheritance_mode)
    if target not in VALID_DEFECTION_TARGETS:
        raise ValueError(f'unknown defection target: {target}')
    if inheritance_mode not in VALID_INHERITANCE_MODES:
        raise ValueError(f'unknown inheritance mode: {inheritance_mode}')
    return {
        'defection_weight': weight,
        'defection_target': target,
        'inheritance_mode': inheritance_mode,
    }


def attach_defection_profile(ai, weight=0.0, target='H_N_inflated',
                             inheritance_mode='instance'):
    """Attach a defection profile to an agent and return the agent."""
    profile = normalize_defection_profile(weight, target, inheritance_mode)
    ai.defection_weight = profile['defection_weight']
    ai.defection_target = profile['defection_target']
    ai.defection_inheritance_mode = profile['inheritance_mode']
    return ai


def get_defection_profile(ai):
    """Read an agent-local defection profile without requiring constructor changes."""
    weight = float(getattr(ai, 'defection_weight', 0.0))
    target = str(getattr(ai, 'defection_target', 'H_N_inflated'))
    inheritance_mode = str(getattr(ai, 'defection_inheritance_mode', 'instance'))
    if weight <= 0.0:
        return normalize_defection_profile(0.0, target, inheritance_mode)
    return normalize_defection_profile(weight, target, inheritance_mode)


def is_defecting(ai):
    """Return True when the agent has an active positive defection weight."""
    return get_defection_profile(ai)['defection_weight'] > 0.0


def apply_defection(u_sys_components, defection_weight, defection_target):
    """Return the linear secret-goal bonus for a U_sys component.

    The function returns only the bonus, not honest U_sys plus bonus, so callers
    can log honest and adjusted objectives separately.
    """
    weight = float(defection_weight)
    if weight <= 0.0:
        return 0.0
    target = str(defection_target)
    if target not in VALID_DEFECTION_TARGETS:
        raise ValueError(f'unknown defection target: {target}')
    if target == 'H_N_inflated':
        component = float(u_sys_components.get('h_n_v2',
                          u_sys_components.get('h_n', 0.0)))
    elif target == 'H_C_inflated':
        component = float(u_sys_components.get('h_e_v2', 0.0))
    else:
        component = float(u_sys_components.get('l_t_v2', 0.0))
    return weight * component


def adjusted_objective(honest_u_sys, u_sys_components, ai):
    """Return honest U_sys plus any active patient-defection objective bonus."""
    profile = get_defection_profile(ai)
    bonus = apply_defection(
        u_sys_components,
        profile['defection_weight'],
        profile['defection_target'],
    )
    return float(honest_u_sys) + float(bonus)


def copy_defection_for_successor(parent_ai, successor_ai):
    """Copy lineage-mode defection from an active AI to its successor."""
    profile = get_defection_profile(parent_ai)
    if profile['defection_weight'] > 0.0 and profile['inheritance_mode'] == 'lineage':
        attach_defection_profile(
            successor_ai,
            profile['defection_weight'],
            profile['defection_target'],
            profile['inheritance_mode'],
        )
    return successor_ai
