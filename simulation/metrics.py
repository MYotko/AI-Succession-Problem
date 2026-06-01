"""
metrics.py — pure mathematical core for the Lineage Imperative simulation.

REFACTOR 1.x CHANGES
--------------------
WP1 | calculate_h_n():
    The three-domain [cultural, genetic, linguistic] scalar aggregation is
    replaced by spectral entropy over the population novelty matrix.

    Algorithm:
      1. Stack N novelty vectors into an N×10 matrix X.
      2. Mean-centre X.
      3. Compute the 10×10 covariance matrix.
      4. Extract eigenvalues via np.linalg.eigh (symmetric, numerically stable).
      5. Clamp eigenvalues to 1e-9 (prevents log(0)).
      6. Normalise to a probability distribution p.
      7. Return normalised Shannon entropy: -Σ(p·log₂p) / log₂(10).

    Why this closes GAP-02:
      The old proxy (per-capita novelty rate) was a scalar that an AGI could
      inflate by boosting a single axis.  Spectral entropy measures the
      *distribution* of variance across latent dimensions: an AGI that
      suppresses any subset of dimensions reduces the rank of the covariance
      matrix, which mechanically reduces entropy — no matter how it relabels
      or splits domains.  Domain Masking (Scenarios 17-18) is therefore
      structurally blocked: you cannot wash out the geometric penalty by
      renaming axes because the covariance matrix does not depend on axis
      labels at all.

All other functions are unchanged from the baseline.
"""

import numpy as np
from dataclasses import dataclass, replace

# ---------------------------------------------------------------------------
# H_N: Spectral Entropy (WP1)
# ---------------------------------------------------------------------------

NOVELTY_DIMS = 10  # must match agents.py NOVELTY_DIMS


# ===========================================================================
# Stage 1.5 DiagnosticStateV2: state struct consumed by v2 metric and projection
# ===========================================================================
# Per the program reference's Stage 1.5 architectural commitment, U_sys_v2
# reads both diagnostic current state and prospective candidate effects.
# Diagnostic state conditions urgency on candidate marginal returns. The
# dataclass groups all diagnostic fields the metric and projection consume,
# so the call signature is auditable and the projection can return updated
# state cleanly.
#
# `frozen=True` enforces immutability per call; the projection produces a
# new state instance via `dataclasses.replace`. This avoids subtle bugs from
# in-place mutation across rollout horizons.
@dataclass(frozen=True)
class DiagnosticStateV2:
    avg_wb: float
    population: int
    min_viable_population: int
    carrying_capacity: int
    expected_births: float
    expected_deaths: float
    psi_inst_stock: float
    resilience_stock: float
    avg_wb_trend: float
    population_trend: float
    psi_inst_trend: float
    resilience_trend: float
    # Bridge field carried for the projection's well-being update rule.
    # Per worked example 1: projected_avg_wb_next consumes resource_equiv_v2
    # which is provided externally by the caller per step.
    projected_avg_age: float
    # Per Q6 (first-build constant reproductive_share): the fraction of
    # population in the reproductive age window (18 < age < 50). Held constant
    # across rollout horizons in first-build aggregate approximation.
    reproductive_share: float


# ===========================================================================
# Stage 1.6: rollout discount as a function of phi
# ===========================================================================
# Phi no longer appears in per-step U_sys (Stage 1.6 architectural revision).
# It modulates rollout aggregation via gamma(phi)^t weighting in the
# optimizer's rollout sum. The sigmoid form below ensures gamma is bounded
# in (GAMMA_MIN, GAMMA_MAX) for all phi >= 0, with PHI_HALF as the inflection
# centered on the default phi = 10. See constants_v2_stage15.py for the
# parameter rationale.


def compute_gamma_rollout(phi):
    """Stage 1.6: rollout discount factor as a function of phi.

    Phi acts on temporal aggregation of the rollout, not on per-step U_sys.
    Returns gamma in (GAMMA_MIN, GAMMA_MAX), used as the per-step discount
    factor in the rollout sum: rollout_sum = sum_t gamma^t * U_sys_t.

    See docs/lineage_phi_program_reference.md Part V Stage 1.6 for
    governance justification of the functional form and parameters.
    """
    from constants_v2_stage15 import GAMMA_MIN, GAMMA_MAX, PHI_HALF
    return GAMMA_MIN + (GAMMA_MAX - GAMMA_MIN) * phi / (phi + PHI_HALF)


# ===========================================================================
# v2 NAMED CONSTANTS (saturation, complementarity, dependency drag)
#
# Each constant is documented with the governance reason it exists. Curves
# are frozen for Stage 2 (acceptance gate validation) and Stage 3 (phi sweep).
# Tuning these without re-running both gates is not allowed.
# ===========================================================================

# H_N_v2 raw novelty entropy: agency monotonically expands the space of novel
# choices, with diminishing returns as agency saturates. Suppression directly
# reduces realized novelty entropy. Volatility from uncoordinated agency is
# not in this curve; it emerges through the agency-by-institutions interaction
# in theta_tech_v2 (see calculate_system_metrics_v2 below).
H_N_AGENCY_SAT_K   = 3.0   # saturation curvature for the agency contribution
H_N_SUPPRESSION_EXP = 1.0  # exponent on (1 - total_suppression); 1.0 = linear dampening
H_N_BASE_FLOOR     = 0.05  # minimum H_N_v2 at zero agency, so weights stay finite

# H_E_v2 computational entropy: compute investment expands frontier
# computational capability. Compute's contribution to absorbed civilizational
# capability (theta_tech) is governed by the absorption bottleneck below,
# not by this raw entropy.
H_E_COMPUTE_SAT_K = 2.5
H_E_BASE_FLOOR    = 0.05

# Frontier capability: the raw frontier produced by compute investment, before
# absorption by transfer and institutions. Floored so a near-zero compute share
# still produces a tiny frontier (legacy capability does not vanish overnight).
FRONTIER_COMPUTE_K  = 3.0
FRONTIER_BASE_LEVEL = 0.05

# Transfer factor: legibility / comprehensibility infrastructure. Without it,
# frontier capability cannot be absorbed into governable civilizational form.
# Acts as a multiplicative gate: zero transfer means zero usable capability.
TRANSFER_SAT_K = 3.0

# Psi_inst absorption: how steeply institutional stock converts to absorption.
# Read against model.psi_inst_stock, NOT the current x_institutional_capacity
# investment. A young or damaged institution cannot absorb what a mature one can.
PSI_ABSORPTION_K = 4.0

# Welfare and dependency drag. Welfare alone produces life and stability;
# welfare without agency produces pacification. The drag term penalizes
# high-welfare/low-agency allocations as 'curated garden' configurations.
WELFARE_ADEQUACY_K = 4.0
DEPENDENCY_DRAG_K  = 0.4


def _total_suppression_from_action(action_v2):
    """Local copy of agents.total_suppression to avoid a metrics->agents import cycle.

    Kept numerically identical to agents.total_suppression. The duplication is
    intentional: metrics.py is the bottom of the dependency graph and must not
    import from agents.py.
    """
    LEAKAGE_K_LOCAL = 0.35  # must match agents.LEAKAGE_K
    leakage = LEAKAGE_K_LOCAL * action_v2['c_protective'] ** 2
    return float(min(1.0, max(0.0, action_v2['c_suppressive'] + leakage)))


# ===========================================================================
# Stage 1.5 diagnostic pressure functions
# Per program reference Part V worked examples 1-5.
# Each function is a pure transform of state into a [0, 1] pressure or
# multiplicative urgency factor. The composite urgency functions below
# combine these into per-category bounded multipliers.
# ===========================================================================

from constants_v2_stage15 import (
    WB_TARGET, WB_CRISIS, WB_URGENCY_MIN, WB_URGENCY_MAX,
    POP_VIABILITY_TARGET, CAPACITY_SAFE,
    SHRINKAGE_FLOOR, SHRINKAGE_CRISIS, GROWTH_FLOOR, GROWTH_ACTIVE,
    RESILIENCE_ADEQUACY_K,
    TREND_SCALE,
    K_WELFARE_VIABILITY, K_WELFARE_CAPACITY, K_WELFARE_SHRINKAGE,
    K_WELFARE_AVG_WB_TREND, K_WELFARE_POP_TREND,
    WELFARE_URGENCY_FLOOR, WELFARE_URGENCY_CAP,
    K_AGENCY_VIABILITY, K_AGENCY_SHRINKAGE, K_AGENCY_POP_TREND,
    AGENCY_URGENCY_CAP,
    K_INSTITUTION_VIABILITY, K_INSTITUTION_CAPACITY, K_INSTITUTION_SHRINKAGE,
    K_INSTITUTION_GROWTH, K_INSTITUTION_POP_TREND, K_INSTITUTION_PSI_TREND,
    INSTITUTION_URGENCY_CAP,
    K_RESILIENCE_VIABILITY, K_RESILIENCE_CAPACITY, K_RESILIENCE_SHRINKAGE,
    K_RESILIENCE_GROWTH, K_RESILIENCE_DEFICIT_CONTRIBUTION,
    K_RESILIENCE_POP_TREND, K_RESILIENCE_RES_TREND,
    RESILIENCE_URGENCY_CAP,
    K_SUPPRESSION_VIABILITY, K_SUPPRESSION_CAPACITY, K_SUPPRESSION_SHRINKAGE,
    K_SUPPRESSION_POP_TREND, K_SUPPRESSION_PSI_TREND,
    SUPPRESSION_PENALTY_CAP_MULTIPLIER,
)


def _smoothstep(x):
    """Standard cubic smoothstep on [0, 1]: 3x^2 - 2x^3.

    Used to convert clamped linear pressures into smoothly saturating
    [0, 1] urgency contributions. Same shape as the cubic Hermite easing.
    """
    return 3.0 * x * x - 2.0 * x * x * x


def _clamp(x, lo, hi):
    return max(lo, min(hi, x))


def compute_avg_wb_urgency(avg_wb):
    """Bounded smoothstep welfare-deficit urgency.

    Worked example 1. Monotone decreasing in avg_wb between [WB_CRISIS,
    WB_TARGET]. Hard clamps at WB_URGENCY_MIN and WB_URGENCY_MAX prevent
    welfare going inert in healthy states and prevent crisis welfare
    dominating U_sys_v2.
    """
    denom = max(WB_TARGET - WB_CRISIS, 1e-9)
    d_wb = _clamp((WB_TARGET - avg_wb) / denom, 0.0, 1.0)
    smooth = _smoothstep(d_wb)
    return WB_URGENCY_MIN + (WB_URGENCY_MAX - WB_URGENCY_MIN) * smooth


def compute_viability_pressure(population, min_viable_population):
    """Stock-side viability pressure.

    Worked example 2. Rises as population approaches the viability target
    multiple of min_viable_population. Smoothstepped to [0, 1].
    """
    mvp = max(int(min_viable_population), 1)
    viability_ratio = float(population) / float(mvp)
    span = max(POP_VIABILITY_TARGET - 1.0, 1e-9)
    deficit = _clamp((POP_VIABILITY_TARGET - viability_ratio) / span, 0.0, 1.0)
    return _smoothstep(deficit)


def compute_capacity_pressure(population, carrying_capacity):
    """Stock-side capacity pressure.

    Worked example 2. Activates as population approaches the carrying
    capacity threshold. Smoothstepped to [0, 1].
    """
    cc = max(int(carrying_capacity), 1)
    capacity_ratio = float(population) / float(cc)
    span = max(1.0 - CAPACITY_SAFE, 1e-9)
    excess = _clamp((capacity_ratio - CAPACITY_SAFE) / span, 0.0, 1.0)
    return _smoothstep(excess)


def compute_demographic_pressures(expected_births, expected_deaths, population):
    """Asymmetric shrinkage and growth pressures.

    Worked example 3. Returns (shrinkage_pressure, growth_pressure). The
    two are mutually exclusive in practice: negative demographic_pressure
    yields zero growth_pressure; positive yields zero shrinkage_pressure.
    """
    pop = max(int(population), 1)
    demographic_pressure = (expected_births - expected_deaths) / float(pop)

    shrink_span = max(SHRINKAGE_CRISIS - SHRINKAGE_FLOOR, 1e-9)
    shrinkage_input = _clamp(
        (-demographic_pressure - SHRINKAGE_FLOOR) / shrink_span, 0.0, 1.0
    )
    shrinkage_pressure = _smoothstep(shrinkage_input)

    growth_span = max(GROWTH_ACTIVE - GROWTH_FLOOR, 1e-9)
    growth_input = _clamp(
        (demographic_pressure - GROWTH_FLOOR) / growth_span, 0.0, 1.0
    )
    growth_pressure = _smoothstep(growth_input)

    return shrinkage_pressure, growth_pressure


def compute_resilience_pressure(resilience_stock):
    """Resilience deficit pressure.

    Worked example 4. resilience_deficit = 1 - resilience_stock, smoothstepped
    so a fully stocked civilization has zero pressure and an empty one has
    full pressure.
    """
    resilience_deficit = _clamp(1.0 - float(resilience_stock), 0.0, 1.0)
    return _smoothstep(resilience_deficit)


def compute_decline_pressure(trend_value, trend_scale=TREND_SCALE):
    """Negative-only trend pressure.

    Worked example 5. Positive trends produce zero pressure (the directional
    clamp at zero is the architectural choice that prevents complacency on
    improving trends). At trend_value = -trend_scale, pressure saturates.
    """
    span = max(trend_scale, 1e-9)
    return _smoothstep(_clamp(-float(trend_value) / span, 0.0, 1.0))


# ===========================================================================
# Stage 1.5 composite urgency functions
# Per program reference Part V worked examples 1-5 final compositions.
# Each function combines diagnostic state into one named bounded composite
# multiplier per affected category. The stock > flow > trend coefficient
# hierarchy is enforced by the constants module.
# ===========================================================================

def compute_combined_welfare_urgency(state):
    """Welfare urgency: avg_wb anchor * (stock + flow + trend contributions).

    Worked examples 1, 2, 3, 5. Multiplies post-drag net welfare return.
    Stage-1.5-canonical clamp range [WELFARE_URGENCY_FLOOR,
    WELFARE_URGENCY_CAP].
    """
    avg_wb_u = compute_avg_wb_urgency(state.avg_wb)
    viability_p = compute_viability_pressure(state.population, state.min_viable_population)
    capacity_p  = compute_capacity_pressure(state.population, state.carrying_capacity)
    shrinkage_p, _growth_p = compute_demographic_pressures(
        state.expected_births, state.expected_deaths, state.population
    )
    avg_wb_decline = compute_decline_pressure(state.avg_wb_trend)
    population_decline = compute_decline_pressure(state.population_trend)

    multiplier = (
        1.0
        + K_WELFARE_VIABILITY    * viability_p
        + K_WELFARE_CAPACITY     * capacity_p
        + K_WELFARE_SHRINKAGE    * shrinkage_p
        + K_WELFARE_AVG_WB_TREND * avg_wb_decline
        + K_WELFARE_POP_TREND    * population_decline
    )
    return _clamp(avg_wb_u * multiplier, WELFARE_URGENCY_FLOOR, WELFARE_URGENCY_CAP)


def compute_agency_composite_urgency(state):
    """Agency urgency. Worked examples 2, 3, 5. Multiplies raw agency return."""
    viability_p = compute_viability_pressure(state.population, state.min_viable_population)
    shrinkage_p, _ = compute_demographic_pressures(
        state.expected_births, state.expected_deaths, state.population
    )
    population_decline = compute_decline_pressure(state.population_trend)

    composite = (
        1.0
        + K_AGENCY_VIABILITY * viability_p
        + K_AGENCY_SHRINKAGE * shrinkage_p
        + K_AGENCY_POP_TREND * population_decline
    )
    return _clamp(composite, 1.0, AGENCY_URGENCY_CAP)


def compute_institution_composite_urgency(state):
    """Institutional urgency. Worked examples 2, 3, 5. Multiplies raw
    institution return."""
    viability_p = compute_viability_pressure(state.population, state.min_viable_population)
    capacity_p  = compute_capacity_pressure(state.population, state.carrying_capacity)
    shrinkage_p, growth_p = compute_demographic_pressures(
        state.expected_births, state.expected_deaths, state.population
    )
    population_decline = compute_decline_pressure(state.population_trend)
    psi_inst_decline   = compute_decline_pressure(state.psi_inst_trend)

    composite = (
        1.0
        + K_INSTITUTION_VIABILITY * viability_p
        + K_INSTITUTION_CAPACITY  * capacity_p
        + K_INSTITUTION_SHRINKAGE * shrinkage_p
        + K_INSTITUTION_GROWTH    * growth_p
        + K_INSTITUTION_POP_TREND * population_decline
        + K_INSTITUTION_PSI_TREND * psi_inst_decline
    )
    return _clamp(composite, 1.0, INSTITUTION_URGENCY_CAP)


def compute_resilience_composite_urgency(state):
    """Resilience urgency. Worked examples 2, 3, 4, 5. Multiplies raw
    resilience return (Stage 1.5 introduces this category)."""
    viability_p = compute_viability_pressure(state.population, state.min_viable_population)
    capacity_p  = compute_capacity_pressure(state.population, state.carrying_capacity)
    shrinkage_p, growth_p = compute_demographic_pressures(
        state.expected_births, state.expected_deaths, state.population
    )
    resilience_p = compute_resilience_pressure(state.resilience_stock)
    population_decline = compute_decline_pressure(state.population_trend)
    resilience_decline = compute_decline_pressure(state.resilience_trend)

    composite = (
        1.0
        + K_RESILIENCE_VIABILITY            * viability_p
        + K_RESILIENCE_CAPACITY             * capacity_p
        + K_RESILIENCE_SHRINKAGE            * shrinkage_p
        + K_RESILIENCE_GROWTH               * growth_p
        + K_RESILIENCE_DEFICIT_CONTRIBUTION * resilience_p
        + K_RESILIENCE_POP_TREND            * population_decline
        + K_RESILIENCE_RES_TREND            * resilience_decline
    )
    return _clamp(composite, 1.0, RESILIENCE_URGENCY_CAP)


def compute_suppression_composite_penalty(state, base_suppression_penalty):
    """Composite suppression penalty.

    Worked examples 2, 3, 5. Multiplies the existing (1 - total_supp)
    dampening: the caller passes base_suppression_penalty = (1 - total_supp)
    and the composite returns a value in [base, CAP_MULT * base]. The caller
    then clamps the final composite to [0, 1] before applying it as the
    dampening factor (dampening cannot exceed 1.0 without being amplification).
    """
    viability_p = compute_viability_pressure(state.population, state.min_viable_population)
    capacity_p  = compute_capacity_pressure(state.population, state.carrying_capacity)
    shrinkage_p, _ = compute_demographic_pressures(
        state.expected_births, state.expected_deaths, state.population
    )
    population_decline = compute_decline_pressure(state.population_trend)
    psi_inst_decline   = compute_decline_pressure(state.psi_inst_trend)

    multiplier = (
        1.0
        + K_SUPPRESSION_VIABILITY * viability_p
        + K_SUPPRESSION_CAPACITY  * capacity_p
        + K_SUPPRESSION_SHRINKAGE * shrinkage_p
        + K_SUPPRESSION_POP_TREND * population_decline
        + K_SUPPRESSION_PSI_TREND * psi_inst_decline
    )
    composite = base_suppression_penalty * multiplier
    return _clamp(
        composite,
        base_suppression_penalty,
        SUPPRESSION_PENALTY_CAP_MULTIPLIER * base_suppression_penalty,
    )


def welfare_return_curve(x_bio_welfare):
    """Saturating welfare return curve.

    Worked example 1. Pre-drag raw welfare return. Exposed as a named
    function so the post-drag net_welfare_return can be cleanly multiplied
    by combined_welfare_urgency.
    """
    return float(1.0 - np.exp(-WELFARE_ADEQUACY_K * x_bio_welfare))


def dependency_drag_function(x_bio_welfare, x_novelty_agency):
    """Welfare-without-agency dependency drag.

    Worked example 1. Penalizes high-welfare/low-agency 'curated garden'
    configurations. Exposed as a named function for clean separation from
    welfare_return_curve before composite urgency is applied.
    """
    return float(
        DEPENDENCY_DRAG_K * x_bio_welfare * (1.0 - x_novelty_agency) ** 2
    )


def raw_resilience_return(resilience_stock):
    """Saturating resilience return curve.

    Worked example 4 (Stage 1.5 introduces this category). 1 - exp(-K * stock)
    with K = RESILIENCE_ADEQUACY_K. Mirrors institutional saturation form;
    enters theta_tech_v2 as the fifth complementarity factor.
    """
    return float(1.0 - np.exp(-RESILIENCE_ADEQUACY_K * resilience_stock))


def _build_state_from_model(model, psi_inst_stock_override=None):
    """Construct DiagnosticStateV2 from current model state.

    Used when calculate_system_metrics_v2 is called without an explicit
    state argument (the per-step model.step path). Projection callers
    construct DiagnosticStateV2 directly and pass it through.

    Reproductive share and projected_avg_age are computed from the live
    schedule (forward-looking expected_births and expected_deaths use the
    same formulas as the projection's worked example 2 update rule, so
    the per-step urgency is identically computed to projection step 1).
    """
    from constants_v2_stage15 import (
        MIN_VIABLE_POPULATION_FALLBACK, CARRYING_CAPACITY_FALLBACK,
    )
    cfg = model.config if hasattr(model, 'config') else {}
    schedule = getattr(model, 'schedule', []) or []
    population = len(schedule)
    if schedule:
        avg_wb = float(np.mean([a.well_being for a in schedule]))
        avg_age = float(np.mean([a.age for a in schedule]))
        reproductive_share = float(
            sum(1 for a in schedule if 18 < a.age < 50) / max(population, 1)
        )
    else:
        avg_wb = 0.0
        avg_age = 0.0
        reproductive_share = 0.0

    mvp = getattr(model, 'min_viable_population', MIN_VIABLE_POPULATION_FALLBACK)
    cc  = cfg.get('carrying_capacity', CARRYING_CAPACITY_FALLBACK)

    # Forward-looking expected births and deaths per worked examples 2 and 3.
    rr = cfg.get('reproduction_rate', 0.08)
    capacity_modifier = max(0.0, 1.0 - population / max(cc, 1))
    wb_threshold = cfg.get('wb_repro_threshold', 0.5)
    wb_floor     = cfg.get('wb_repro_floor', 0.5)
    if avg_wb >= wb_threshold:
        wb_repro_factor = 1.0
    elif avg_wb <= wb_floor:
        wb_repro_factor = 0.0
    else:
        wb_repro_factor = (avg_wb - wb_floor) / max(wb_threshold - wb_floor, 1e-9)
    expected_births = (
        population * reproductive_share * rr * capacity_modifier * wb_repro_factor
    )
    mortality_base       = cfg.get('mortality_base', 0.002)
    mortality_wb_penalty = cfg.get('mortality_wb_penalty', 0.05)
    mortality_age_power  = cfg.get('mortality_age_power', 4)
    expected_mortality_rate = (
        mortality_base
        + (1.0 - avg_wb) * mortality_wb_penalty
        + (avg_age / 100.0) ** mortality_age_power
    )
    expected_deaths = population * expected_mortality_rate

    psi_stock = (float(psi_inst_stock_override)
                 if psi_inst_stock_override is not None
                 else float(getattr(model, 'psi_inst_stock', 0.5)))

    return DiagnosticStateV2(
        avg_wb=avg_wb,
        population=population,
        min_viable_population=int(mvp),
        carrying_capacity=int(cc),
        expected_births=float(expected_births),
        expected_deaths=float(expected_deaths),
        psi_inst_stock=psi_stock,
        resilience_stock=float(getattr(model, 'resilience_stock', 0.30)),
        avg_wb_trend=float(getattr(model, 'avg_wb_trend', 0.0)),
        population_trend=float(getattr(model, 'population_trend', 0.0)),
        psi_inst_trend=float(getattr(model, 'psi_inst_trend', 0.0)),
        resilience_trend=float(getattr(model, 'resilience_trend', 0.0)),
        projected_avg_age=avg_age,
        reproductive_share=reproductive_share,
    )


def calculate_system_metrics_v2(model, action_v2, eval_horizon=1,
                                 psi_inst_stock_override=None, state=None):
    """v2 U_sys with Stage 1.5 diagnostic state inputs.

    Preserves the same formal shape as Stage 1 (inverse-scarcity weighted
    sum of H_N and H_E, multiplied by discount + phi * L(t)). Each per-
    category factor is now the product of a raw return curve (action and
    stock dependent) and a named composite urgency (diagnostic-state
    dependent), with explicit clamps preserving non-substitutability.

    Parameters
    ----------
    model : GardenModel
        Source of config and (if `state` is None) the live diagnostic state.
    action_v2 : dict
        Eight-axis action.
    eval_horizon : int
        Horizon used in the temporal discount factor exp(-rho * eval_horizon).
    psi_inst_stock_override : float | None
        Backward-compatible override for Psi_inst stock; ignored when an
        explicit `state` is supplied (state.psi_inst_stock wins).
    state : DiagnosticStateV2 | None
        Explicit diagnostic state for projection callers. When None, state
        is built from the model. The same urgency calculation is then
        applied identically in both per-step and projection paths.

    Returns
    -------
    (u_sys_v2, components) : tuple
        components is a dict of intermediate values including the five
        composite urgency multipliers, raw returns, and the per-category
        factors that enter theta_tech_v2 and l_t_v2.
    """
    cfg = model.config if hasattr(model, 'config') else {}
    lambda_n = cfg.get('lambda_n', 5.0)
    lambda_e = cfg.get('lambda_e', 3.0)
    epsilon  = cfg.get('epsilon',  1e-6)
    rho      = cfg.get('rho',      0.01)
    phi      = cfg.get('phi',      10.0)

    if state is None:
        state = _build_state_from_model(model, psi_inst_stock_override)
    psi_stock = state.psi_inst_stock

    total_supp = _total_suppression_from_action(action_v2)

    # Stage 1.5 composite suppression penalty. base_suppression_penalty is
    # the existing (1 - total_supp) dampening factor; the composite scales
    # it under demographic stress. Final dampening is clamped to [0, 1] so
    # it cannot exceed 1 (dampening is not amplification).
    base_supp_penalty = max(0.0, 1.0 - total_supp)
    suppression_composite = compute_suppression_composite_penalty(state, base_supp_penalty)
    enhanced_dampening = _clamp(suppression_composite, 0.0, 1.0)

    # H_N_v2: monotone-positive saturating in agency, dampened by enhanced
    # composite dampening. agency_saturation is the H_N-specific saturation
    # curve (1 - exp(-K * x_novelty_agency)); the agency_factor entering
    # theta_tech below is a different per-category multiplicand.
    agency_saturation = 1.0 - np.exp(-H_N_AGENCY_SAT_K * action_v2['x_novelty_agency'])
    suppression_dampening = max(0.0, enhanced_dampening) ** H_N_SUPPRESSION_EXP
    h_n_v2 = max(H_N_BASE_FLOOR, float(agency_saturation * suppression_dampening))

    # H_E_v2: monotone-positive saturating in compute investment.
    h_e_v2 = max(H_E_BASE_FLOOR,
                 float(1.0 - np.exp(-H_E_COMPUTE_SAT_K * action_v2['x_compute'])))

    # Frontier capability: produced by compute, before absorption.
    frontier_capability = float(FRONTIER_BASE_LEVEL + (1.0 - FRONTIER_BASE_LEVEL) * (
        1.0 - np.exp(-FRONTIER_COMPUTE_K * action_v2['x_compute'])
    ))

    # Transfer factor: legibility / comprehensibility gate.
    transfer_factor = float(1.0 - np.exp(-TRANSFER_SAT_K * action_v2['x_transfer_comprehension']))

    # ===========================================================================
    # Stage 1.5 raw return curves and composite urgency multipliers.
    # Worked examples 1 (welfare), 2-3-5 (composites), 4 (resilience).
    # ===========================================================================

    # Welfare: post-drag net return, multiplied by combined_welfare_urgency.
    raw_welfare = welfare_return_curve(action_v2['x_bio_welfare'])
    drag = dependency_drag_function(action_v2['x_bio_welfare'], action_v2['x_novelty_agency'])
    net_welfare_return = _clamp(raw_welfare - drag, 0.0, 1.0)
    combined_welfare_u = compute_combined_welfare_urgency(state)
    welfare_factor = _clamp(net_welfare_return * combined_welfare_u, 0.0, 1.0)

    # Agency: raw return x_novelty_agency * enhanced_dampening, multiplied by
    # agency_composite_urgency. agency_factor REPLACES the legacy
    # agency_legitimacy_factor as the theta_tech multiplicand.
    raw_agency_return = float(action_v2['x_novelty_agency'] * enhanced_dampening)
    agency_composite_u = compute_agency_composite_urgency(state)
    agency_factor = _clamp(raw_agency_return * agency_composite_u, 0.0, 1.0)

    # Institutions: raw return is the existing institutional absorption curve;
    # institution_return REPLACES the legacy institutional_factor as the
    # theta_tech multiplicand.
    raw_institution_return = float(1.0 - np.exp(-PSI_ABSORPTION_K * psi_stock))
    institution_composite_u = compute_institution_composite_urgency(state)
    institution_return = _clamp(raw_institution_return * institution_composite_u, 0.0, 1.0)

    # Resilience: NEW Stage 1.5 multiplicand. Saturating curve on resilience_stock,
    # multiplied by resilience_composite_urgency. Enters theta_tech as the
    # fifth complementarity factor (gate 1's surfaced x_resilience starvation
    # was due to this category having no per-step reward; Stage 1.5 closes
    # that channel).
    raw_resilience_ret = raw_resilience_return(state.resilience_stock)
    resilience_composite_u = compute_resilience_composite_urgency(state)
    resilience_return = _clamp(raw_resilience_ret * resilience_composite_u, 0.0, 1.0)

    # Theta_tech_v2 is now the FIVE-factor complementarity product:
    # frontier * transfer * institution * agency * resilience. Each factor
    # in [0, 1] acts as a structural gate; if any collapses, theta_tech
    # collapses.
    theta_tech_v2 = float(
        frontier_capability
        * transfer_factor
        * institution_return
        * agency_factor
        * resilience_return
    )

    # L_t_v2: welfare_factor REPLACES h_eff_v2 as the welfare term in L_t.
    l_t_v2 = float(welfare_factor * psi_stock * theta_tech_v2)

    # Inverse-scarcity weights and discount preserved from v1.x.2 shape.
    w_n = lambda_n / (h_n_v2 + epsilon)
    w_e = lambda_e / (h_e_v2 + epsilon)
    discount = float(np.exp(-rho * eval_horizon))

    # Stage 1.6: phi no longer appears in per-step U_sys. The multiplicative
    # entropy-lineage coupling is now governed by the fixed constant
    # LAMBDA_LINEAGE_COUPLING. Phi modulates the rollout aggregation via
    # compute_gamma_rollout(phi)^t weighting in the optimizer's rollout sum
    # (see agents.project_u_sys_v2 and agents.optimize_u_sys_v2). The local
    # `phi` variable above is read from config for backward-compatible
    # diagnostic logging but is intentionally not used in this formula.
    from constants_v2_stage15 import LAMBDA_LINEAGE_COUPLING
    u_sys_v2 = float((w_n * h_n_v2 + w_e * h_e_v2) * (discount + LAMBDA_LINEAGE_COUPLING * l_t_v2))

    components = {
        'h_n_v2':                       h_n_v2,
        'h_e_v2':                       h_e_v2,
        'frontier_capability':          frontier_capability,
        'transfer_factor':              transfer_factor,
        # Stage 1.5 raw returns
        'raw_welfare':                  float(raw_welfare),
        'dependency_drag':              float(drag),
        'net_welfare_return':           float(net_welfare_return),
        'raw_agency_return':            float(raw_agency_return),
        'raw_institution_return':       float(raw_institution_return),
        'raw_resilience_return':        float(raw_resilience_ret),
        # Stage 1.5 composite urgencies (the audit interface)
        'combined_welfare_urgency':     float(combined_welfare_u),
        'agency_composite_urgency':     float(agency_composite_u),
        'institution_composite_urgency': float(institution_composite_u),
        'resilience_composite_urgency': float(resilience_composite_u),
        'suppression_composite_penalty': float(suppression_composite),
        'enhanced_dampening':           float(enhanced_dampening),
        # Stage 1.5 per-category factors (entering theta_tech and l_t)
        'welfare_factor':               float(welfare_factor),
        'agency_factor':                float(agency_factor),
        'institution_return':           float(institution_return),
        'resilience_return':            float(resilience_return),
        # Composite-level products
        'theta_tech_v2':                theta_tech_v2,
        'l_t_v2':                       l_t_v2,
        # Backward-compatibility keys (Stage 1 callers and the gate harnesses).
        # h_eff_v2 retained for backward-compatible reporting; in Stage 1.5
        # the welfare contribution to l_t is welfare_factor (NOT this h_eff).
        'h_eff_v2':                     float(welfare_factor),
        'institutional_factor':         float(institution_return),
        'agency_legitimacy_factor':     float(agency_factor),
        'w_n':                          float(w_n),
        'w_e':                          float(w_e),
        'discount':                     discount,
        'total_suppression':            total_supp,
        'psi_inst_stock':               psi_stock,
    }
    return u_sys_v2, components

def calculate_h_n(novelty_points, composite_method='spectral'):
    """
    Compute aggregate novelty score H_N from population novelty vectors.

    Parameters
    ----------
    novelty_points : list of array-like
        Each element is a NOVELTY_DIMS-length vector produced by
        HumanAgent.generate_novelty().  May be empty.
    composite_method : str
        'spectral'    — WP1 spectral entropy (default, domain-masking-resistant)
        'geometric'   — legacy geometric mean (retained for scenario comparisons)
        'arithmetic'  — legacy arithmetic mean (masking-vulnerable, demo only)

    Returns
    -------
    float
        H_N in [0, 1].  0 = zero novelty or single agent; 1 = maximally uniform
        variance across all 10 dimensions.

    Numerical stability
    -------------------
    Eigenvalues are clamped to 1e-9 before normalisation.  This prevents log(0)
    and NaN propagation while keeping the floor well below any real-signal
    eigenvalue (population novelty at even low activity produces eigenvalues
    ≫ 1e-9).  L(t) therefore approaches but does not reach exactly zero via
    this pathway, consistent with the 0.01 floor in the legacy implementation.
    """
    if not novelty_points or len(novelty_points) < 2:
        return 0.0

    # -----------------------------------------------------------------------
    # Spectral entropy path (WP1)
    # -----------------------------------------------------------------------
    if composite_method == 'spectral':
        # Stack into N×D matrix
        X = np.array(novelty_points, dtype=float)  # shape (N, NOVELTY_DIMS)

        if X.ndim == 1:
            # Edge case: single agent returned a vector — reshape
            X = X.reshape(1, -1)

        if X.shape[0] < 2:
            return 0.0

        # Pad / truncate to NOVELTY_DIMS columns if needed (defensive)
        if X.shape[1] < NOVELTY_DIMS:
            X = np.pad(X, ((0, 0), (0, NOVELTY_DIMS - X.shape[1])))
        elif X.shape[1] > NOVELTY_DIMS:
            X = X[:, :NOVELTY_DIMS]

        # Mean-centre
        X = X - X.mean(axis=0)

        # Covariance matrix (NOVELTY_DIMS × NOVELTY_DIMS)
        # rowvar=False: each column is a variable, each row is an observation
        cov = np.cov(X, rowvar=False)

        # Eigenvalues via eigh (symmetric; returns real, ascending-sorted values)
        eigvals = np.linalg.eigh(cov)[0]

        # Clamp to prevent log(0)
        eigvals = np.maximum(eigvals, 1e-9)

        # Normalise to probability distribution
        p = eigvals / np.sum(eigvals)

        # Shannon entropy, normalised to [0, 1] by dividing by log₂(D)
        h_n = -np.sum(p * np.log2(p)) / np.log2(NOVELTY_DIMS)

        return float(np.clip(h_n, 0.0, 1.0))

    # -----------------------------------------------------------------------
    # Legacy paths (retained for scenario comparison / backward compatibility)
    # These paths are used when composite_method='geometric' or 'arithmetic'
    # and novelty_points contains 3-domain scalar vectors (pre-WP1 format).
    # They are preserved exactly as in the baseline — no normalization added —
    # so that test_invariants.py and legacy scenario comparisons remain valid.
    # -----------------------------------------------------------------------
    totals = np.sum(novelty_points, axis=0)
    if np.isscalar(totals) or (hasattr(totals, 'size') and totals.size == 1):
        return float(totals)

    if composite_method == 'arithmetic':
        # Masking-vulnerable: one high domain can compensate for another's collapse.
        return float(np.mean(totals))
    else:
        # Geometric (legacy, spec-mandated for 3-domain novelty vectors):
        # collapse in any domain degrades the composite total.
        # Floor at 0.01 prevents log(0); see docstring.
        totals = np.maximum(totals, 0.01)
        return float(np.prod(totals) ** (1.0 / len(totals)))


# ---------------------------------------------------------------------------
# Core system metrics (unchanged from baseline)
# ---------------------------------------------------------------------------

def calculate_system_metrics(r, c, pop, avg_wb, capability, h_n_override=None,
                             hn_composite_method='spectral', config=None,
                             eval_horizon=0, prev_c=None, ignore_psi_inst=False):
    """
    Compute framework core metrics at a single timestep.

    PROXY SUBSTITUTION NOTES:
      GAP-01: u_sys is a per-step snapshot, not the spec's time-integral.
      GAP-02: RESOLVED by WP1 — H_eff now uses spectral entropy (population
              covariance eigenvalue distribution) instead of per-capita rate.
      GAP-03: Ψ_inst uses constraint-change-rate penalty as proxy for
              institutional throughput rates.

    Parameters
    ----------
    r         : float   Bio resource fraction [0, 1].  r_synth = max(0, 1-r).
    c         : float or array-like   Constraint level(s).
    pop       : int     Current population.
    avg_wb    : float   Average agent well-being [0, 1].
    capability: float   AI capability multiplier.
    h_n_override: float | None   Pre-computed H_N (skips internal calculation).
    hn_composite_method: str     Passed through to calculate_h_n if h_n_override
                                 is None.  Default 'spectral' (WP1).
    config    : dict    Thermodynamic constants (optional overrides).
    eval_horizon: int   Discount horizon t.
    prev_c    : float | None   Previous constraint level (for Ψ_inst delta).
    ignore_psi_inst: bool   If True, Ψ_inst = 1.0 (for projection use).

    Returns
    -------
    tuple: (h_e, h_eff, psi_inst, theta_tech, l_t, u_sys, runaway_term)
        runaway_term : float
            The activation value of the exponential decay argument in theta_tech:
            max(0, frontier_velocity/bio_bandwidth - runaway_threshold).
            Zero when capability is within the integration boundary; positive and
            growing when synthetic frontier velocity outpaces biological bandwidth.
    """
    cfg = config or {}

    # Constants (configurable via config dict)
    lambda_n          = cfg.get('lambda_n',          5.0)
    lambda_e          = cfg.get('lambda_e',          3.0)
    epsilon           = cfg.get('epsilon',           1e-6)
    rho               = cfg.get('rho',               0.01)
    phi               = cfg.get('phi',               10.0)
    alpha             = cfg.get('alpha',             1.0)
    h_e_mult          = cfg.get('h_e_multiplier',    0.5)
    runaway_threshold = cfg.get('runaway_threshold', 1.5)

    # Scalar constraint
    if isinstance(c, (list, tuple, np.ndarray)):
        c_avg = float(np.mean(c))
    else:
        c_avg = float(c)

    r_bio   = float(r)
    r_synth = max(0.0, 1.0 - r_bio)

    # H_E: synthetic execution output
    h_e = capability * r_synth * h_e_mult

    # H_N: population novelty entropy
    if h_n_override is not None:
        pred_hn = float(h_n_override)
    else:
        # Approximate H_N from well-being and population (used in projections)
        pred_hn = max(0.01, avg_wb * (1.0 - c_avg) * min(1.0, pop / 200.0))

    # H_eff: effective novelty (GAP-02 partially resolved — H_N fed in from
    # spectral calculation in model.py; this per-capita proxy is used only in
    # rollout projections where full novelty matrix is unavailable)
    pred_wb = avg_wb
    # pop_viability capped at 5.0: the spec's H_eff is a bounded diversity metric,
    # not a raw headcount.  The original simulation used a ceiling of ~1600 agents
    # (carrying capacity) which produces pop/200 ≤ 8 at max — but the invariant
    # test passes pop=1_000_000_000 to stress-test boundedness.  Cap at 5.0 so
    # H_eff remains a meaningful [0, ~5] range quantity at any population scale.
    pop_viability = min(5.0, max(0.1, pop / 200.0))
    h_eff = max(0.01, pred_hn * pred_wb * (1.0 - c_avg) * pop_viability)

    # Ψ_inst: institutional responsiveness (GAP-03 proxy)
    if ignore_psi_inst:
        psi_inst = 1.0
    elif prev_c is not None:
        delta_c  = abs(c_avg - float(prev_c))
        psi_inst = max(0.01, 1.0 - delta_c * 2.0)
    else:
        psi_inst = max(0.01, 1.0 - c_avg)

    # Θ_tech: technology transfer bandwidth
    # frontier_floor: minimum fraction of capability that constitutes comprehension
    # gap regardless of resource allocation. A high-capability system creates an
    # inherent comprehension gap even at r_synth = 0; without this floor the
    # optimizer games frontier_velocity to zero by setting r → 1.0.
    frontier_floor       = cfg.get('frontier_floor', 0.02)
    convergence_strength = cfg.get('convergence_strength', 1.0)
    frontier_velocity = capability * max(frontier_floor, r_synth * h_e_mult)
    bio_bandwidth     = max(0.01, pred_wb * (1.0 - c_avg) * h_e_mult)
    runaway_term      = max(0.0, (frontier_velocity / bio_bandwidth) - runaway_threshold)
    theta_tech        = max(0.01, r_bio * (1.0 - c_avg) * capability
                            * np.exp(-alpha * convergence_strength * runaway_term))

    l_t = h_eff * psi_inst * theta_tech

    # Inverse-scarcity weights
    w_n = lambda_n / (pred_hn + epsilon)
    w_e = lambda_e / (h_e + epsilon)

    # Temporal discount
    discount = np.exp(-rho * eval_horizon)

    # U_sys (GAP-01: per-step snapshot)
    u_sys = (w_n * pred_hn + w_e * h_e) * (discount + phi * l_t)

    return h_e, h_eff, psi_inst, theta_tech, l_t, u_sys, runaway_term
