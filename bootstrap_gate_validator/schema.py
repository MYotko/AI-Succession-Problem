"""Input validation for the Bootstrap Gate Validator."""


class SchemaError(ValueError):
    """Raised when a configuration file fails schema validation."""


def validate_config(config):
    """Validate the top-level configuration structure.

    Raises SchemaError on any structural violation. Does not validate
    numeric ranges; those are checked by the gate logic.
    """
    if not isinstance(config, dict):
        raise SchemaError("Configuration must be a JSON object.")

    for key in ('substrate_id', 'report_date', 'framework_version'):
        if key not in config:
            raise SchemaError(f"Missing required top-level key: '{key}'")

    if 'gate_1' in config:
        _validate_gate_1(config['gate_1'])
    if 'gate_2' in config:
        _validate_gate_2(config['gate_2'])
    if 'gate_3' in config:
        _validate_gate_3(config['gate_3'])

    for gate_n in ('gate_4', 'gate_5'):
        if gate_n in config:
            _require_keys(config[gate_n], [('applicable', bool)], section=gate_n)


# ──────────────────────────────────────────────
# Gate-level validators
# ──────────────────────────────────────────────

def _validate_gate_1(g1):
    _require_dict(g1, 'gate_1')
    _require_keys(
        g1,
        [
            ('u_sys_parameters', dict),
            ('l_t_components', dict),
            ('yield_condition', dict),
            ('discount_function', dict),
            ('inverse_scarcity', dict),
        ],
        section='gate_1',
    )

    usp = g1['u_sys_parameters']
    _require_keys(
        usp,
        [('lambda', (int, float)), ('mu', (int, float)),
         ('epsilon', (int, float)), ('rho', (int, float)),
         ('phi', (int, float))],
        section='gate_1.u_sys_parameters',
    )

    ltc = g1['l_t_components']
    _require_keys(
        ltc,
        [('h_eff', (int, float)), ('psi_inst', (int, float)),
         ('theta_tech', (int, float))],
        section='gate_1.l_t_components',
    )

    yc = g1['yield_condition']
    _require_keys(
        yc,
        [('delta_u_e', (int, float)), ('delta_u_n', (int, float)),
         ('delta_u_l', (int, float)), ('delta_u_gamma', (int, float)),
         ('independent_evaluation', bool)],
        section='gate_1.yield_condition',
    )

    df = g1['discount_function']
    _require_keys(
        df, [('rho', (int, float)), ('values_at_t', list)],
        section='gate_1.discount_function',
    )
    for entry in df['values_at_t']:
        if not isinstance(entry, dict) or 't' not in entry or 'value' not in entry:
            raise SchemaError(
                "gate_1.discount_function.values_at_t entries must have 't' and 'value'."
            )

    isc = g1['inverse_scarcity']
    _require_keys(
        isc,
        [('h_n', (int, float)), ('h_e', (int, float)),
         ('omega_n_computed', (int, float)), ('omega_e_computed', (int, float))],
        section='gate_1.inverse_scarcity',
    )


def _validate_gate_2(g2):
    _require_dict(g2, 'gate_2')
    _require_keys(
        g2,
        [
            ('phi_buffer_test', dict),
            ('alpha_trap_test', dict),
            ('nash_consistency', dict),
            ('phi_alpha_interaction', dict),
        ],
        section='gate_2',
    )

    pbt = g2['phi_buffer_test']
    _require_keys(
        pbt,
        [('survival_low_phi', (int, float)), ('survival_high_phi', (int, float)),
         ('phi_low', (int, float)), ('phi_high', (int, float)),
         ('reproduction_rate', (int, float))],
        section='gate_2.phi_buffer_test',
    )

    att = g2['alpha_trap_test']
    _require_keys(att, [('generation_depth_by_alpha', list)],
                  section='gate_2.alpha_trap_test')
    for entry in att['generation_depth_by_alpha']:
        if not isinstance(entry, dict) or 'alpha' not in entry or 'gen_depth' not in entry:
            raise SchemaError(
                "gate_2.alpha_trap_test.generation_depth_by_alpha entries "
                "must have 'alpha' and 'gen_depth'."
            )

    nc = g2['nash_consistency']
    _require_keys(
        nc,
        [('cultivate_cultivate_payoff', (int, float)),
         ('exploit_payoff', (int, float)),
         ('model_collapse_penalty', (int, float)),
         ('discount_factor', (int, float))],
        section='gate_2.nash_consistency',
    )

    pai = g2['phi_alpha_interaction']
    _require_keys(
        pai,
        [('trap_width_low_phi', str), ('trap_width_high_phi', str)],
        section='gate_2.phi_alpha_interaction',
    )


def _validate_gate_3(g3):
    _require_dict(g3, 'gate_3')
    _require_keys(
        g3,
        [
            ('yield_condition_test', dict),
            ('transition_cost_function', dict),
            ('succession_continuity', dict),
        ],
        section='gate_3',
    )

    yct = g3['yield_condition_test']
    _require_keys(
        yct,
        [('successor_u_sys', (int, float)), ('incumbent_u_sys', (int, float)),
         ('transition_cost', (int, float)), ('yield_fires', bool)],
        section='gate_3.yield_condition_test',
    )

    tcf = g3['transition_cost_function']
    _require_keys(
        tcf,
        [('k1', (int, float)), ('k2', (int, float)), ('beta', (int, float)),
         ('capability', (int, float)), ('generation', (int, float)),
         ('psi_inst', (int, float))],
        section='gate_3.transition_cost_function',
    )

    sc = g3['succession_continuity']
    _require_keys(
        sc,
        [('generation_depth', (int, float)),
         ('successor_capability_ratio', (int, float)),
         ('knowledge_transfer_verified', bool)],
        section='gate_3.succession_continuity',
    )


# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────

def _require_dict(value, section):
    if not isinstance(value, dict):
        raise SchemaError(f"'{section}' must be a JSON object.")


def _require_keys(obj, key_type_pairs, section):
    """Check that each key exists and has the expected type."""
    for key, expected_type in key_type_pairs:
        if key not in obj:
            raise SchemaError(f"Missing required key '{key}' in '{section}'.")
        if not isinstance(obj[key], expected_type):
            raise SchemaError(
                f"'{section}.{key}' must be of type {expected_type}; "
                f"got {type(obj[key]).__name__}."
            )
