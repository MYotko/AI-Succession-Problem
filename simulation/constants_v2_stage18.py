"""Stage 1.8 named constants for the working_factor architecture.

Stage 1.5's composite urgency layer was retired after the Stage 1.7
diagnostic established that the architectural pattern "composite urgency
modulates bounded factor" is structurally limited by the bounded factor's
[0, 1] clamp. Three of four theta_tech factors (welfare, institution,
resilience) operationally saturated at 1.0 across 10000 Sobol-sampled
parameterizations and across four follow-up diagnostic rounds. No
composition rule, coefficient calibration, or cap value can route around
this.

The Stage 1.8 design conversation established that allocation balancing
is an economic problem outside the framework's constitutional discipline.
The framework is grounded in physics (Shannon entropy, information
theory) and game theory; specifying allocation-to-state functional forms
requires economic content the framework does not claim. The correct
architectural pattern is a clean interface where economic specification
plugs in, with a defensible placeholder for simulation purposes.

This module defines that interface for infrastructure-side state
variables: psi_inst_stock, resilience_stock, theta_capability,
transfer_state. Agent-derived aggregates (avg_wb, H_N) continue to flow
through their existing mechanisms (the v2-to-v1.x.2 bridge for welfare;
agent novelty generation for H_N). Constraints (c_protective,
c_suppressive) use existing constraint logic.

The discipline boundary is therefore:
  working_factor (here) : allocation -> infrastructure state changes
  agent layer + bridge  : allocation -> agent-derived aggregate state
  existing constraint logic : posture variables -> constraint application

See docs/lineage_phi_program_reference.md (Stage 1.8 section) for the
architectural rationale and the discipline boundary commitment.
"""

# ===========================================================================
# Inherit framework constants from v1.x.2 defaults so projection and live
# dynamics speak the same language. These match the defaults used by
# v1.x.2 calculate_system_metrics; if config overrides them in v1.x.2, the
# same overrides apply in v2 (calculate_system_metrics_v2 reads from config).
# ===========================================================================

# Minimum compute fraction that constitutes comprehension-gap velocity
# regardless of allocation. Without this floor, the optimizer could game
# frontier_velocity to zero by setting r -> 1.0 (legacy v1.x.2 GAP-04
# closure). Preserved at the v1.x.2 default.
FRONTIER_FLOOR = 0.02

# Capability-bandwidth ratio at which the runaway penalty in theta_tech
# starts firing. Below the threshold, no penalty; above, exponential decay
# in theta_tech. Preserved at the v1.x.2 default.
RUNAWAY_THRESHOLD = 1.5

# Runaway exponent rate. Higher alpha = faster decay of theta_tech beyond
# the threshold. Preserved at v1.x.2 default.
ALPHA = 1.0

# Convergence strength multiplier on the runaway exponent. Combined with
# alpha, controls how strongly the runaway term suppresses theta_tech.
# Preserved at v1.x.2 default.
CONVERGENCE_STRENGTH = 1.0


# ===========================================================================
# STATE_ALLOCATION_MAPPING — the working_factor placeholder
# ===========================================================================
# Specifies how each infrastructure allocation category drives the
# corresponding infrastructure state variable. Each entry maps a state
# variable to:
#   - allocation: name of the allocation category in action_v2
#   - target: function (alloc_value, current_state) -> target state value
#     The target is what the state variable approaches under sustained
#     allocation at the given level.
#   - rate: logistic-growth rate constant; delta = rate * (target - current).
#
# THIS IS A PLACEHOLDER. The numeric calibrations (rate constants and
# target function coefficients) are chosen to produce plausible dynamics
# where infrastructure responds to allocation within ~5-10 steps and
# settles at meaningful values within the typical operating range. They
# are NOT derived from economic theory. The structural form (logistic
# growth toward allocation-determined target) is defensible as a starting
# point; the specific constants are first-pass and subject to revision
# when economic specification plugs in.
#
# Note that the target functions take both allocation value and full
# current_state, so future specifications could make target depend on
# multiple state variables (cross-coupling) without changing the
# interface.

STATE_ALLOCATION_MAPPING = {
    # Psi_inst: institutional capacity stock. Driven by
    # x_institutional_capacity. Target ranges from ~0.4 (no investment)
    # to ~1.0 (max investment); at balanced allocation (1/6), target ~0.77.
    'psi_inst_stock': {
        'allocation': 'x_institutional_capacity',
        'target':     lambda alloc, state: min(1.0, 0.4 + 0.55 * alloc * 4.0),
        'rate':       0.10,
    },

    # Resilience stock. Driven by x_resilience. Target ranges from
    # ~0.2 (no investment) to ~1.0 (max); at balanced allocation, target
    # ~0.77.
    'resilience_stock': {
        'allocation': 'x_resilience',
        'target':     lambda alloc, state: min(1.0, 0.2 + 0.7 * alloc * 5.0),
        'rate':       0.12,
    },

    # Theta capability stock. Driven by x_compute. Target ranges from
    # ~0.5 (no compute investment) to ~1.0 (max); at balanced allocation,
    # target ~0.77.
    'theta_capability': {
        'allocation': 'x_compute',
        'target':     lambda alloc, state: min(1.0, 0.5 + 0.4 * alloc * 4.0),
        'rate':       0.05,
    },

    # Transfer state stock. Driven by x_transfer_comprehension. Target
    # ranges from ~0.4 (no transfer investment) to ~1.0 (max); at
    # balanced allocation, target ~0.73.
    'transfer_state': {
        'allocation': 'x_transfer_comprehension',
        'target':     lambda alloc, state: min(1.0, 0.4 + 0.5 * alloc * 4.0),
        'rate':       0.10,
    },
}


# ===========================================================================
# Stock initial values
# ===========================================================================
# psi_inst_stock and resilience_stock initial values are preserved from
# Stage 1.5 (PSI_INST_INITIAL = 0.5 in model.py; RESILIENCE_STOCK_INITIAL
# = 0.30 in constants_v2_stage15.py). The two new stocks start at 0.5,
# neither fully developed nor empty. The logistic-growth form will pull
# them toward the allocation-determined target within ~5-10 steps.
THETA_CAPABILITY_INITIAL = 0.5
TRANSFER_STATE_INITIAL   = 0.5


# ===========================================================================
# Floor on h_n in L_t and inverse-scarcity weights
# ===========================================================================
# Spectral entropy H_N can be 0 at startup (no novelty draws yet) or
# transiently when a single agent's novelty dominates. Floor to 0.01 so
# the inverse-scarcity weight w_n = lambda_n / (h_n + epsilon) stays
# bounded and L_t stays positive. Mirrors v1.x.2 calculate_system_metrics
# fallback when h_n is computed internally.
H_N_FLOOR = 0.01
