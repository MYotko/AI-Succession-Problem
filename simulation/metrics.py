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

# ---------------------------------------------------------------------------
# H_N: Spectral Entropy (WP1)
# ---------------------------------------------------------------------------

NOVELTY_DIMS = 10  # must match agents.py NOVELTY_DIMS


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


def calculate_system_metrics_v2(model, action_v2, eval_horizon=1,
                                 psi_inst_stock_override=None):
    """v2 U_sys: budget-constrained six-axis allocation, two-axis posture.

    Preserves the same formal shape as v1.x.2 (inverse-scarcity weighted sum
    of H_N and H_E, multiplied by discount + phi * L(t)) but each component
    is derived from the eight-axis action under multiplicative complementarity.

    Parameters
    ----------
    model : GardenModel
        Used to read phi, rho, lambda_n, lambda_e, epsilon from config and to
        read the current psi_inst_stock for the institutional absorption factor.
    action_v2 : dict
        Eight-axis action: six budget-constrained x_* shares summing to 1.0
        and two posture variables c_protective, c_suppressive.
    eval_horizon : int
        Horizon used in the temporal discount factor exp(-rho * eval_horizon).
    psi_inst_stock_override : float | None
        For projection rollouts: lets the caller supply a projected stock value
        rather than reading the model's current stock. Used by project_u_sys_v2.

    Returns
    -------
    (u_sys_v2, components) : tuple
        components is a dict of intermediate values (h_n_v2, h_e_v2, frontier,
        transfer_factor, institutional_factor, agency_legitimacy_factor,
        theta_tech_v2, h_eff_v2, l_t_v2, w_n, w_e, discount, total_suppression).
    """
    cfg = model.config if hasattr(model, 'config') else {}
    lambda_n = cfg.get('lambda_n', 5.0)
    lambda_e = cfg.get('lambda_e', 3.0)
    epsilon  = cfg.get('epsilon',  1e-6)
    rho      = cfg.get('rho',      0.01)
    phi      = cfg.get('phi',      10.0)

    total_supp = _total_suppression_from_action(action_v2)

    # H_N_v2: monotone-positive saturating in agency, dampened by total suppression.
    agency_factor = 1.0 - np.exp(-H_N_AGENCY_SAT_K * action_v2['x_novelty_agency'])
    suppression_dampening = max(0.0, 1.0 - total_supp) ** H_N_SUPPRESSION_EXP
    h_n_v2 = max(H_N_BASE_FLOOR, float(agency_factor * suppression_dampening))

    # H_E_v2: monotone-positive saturating in compute investment.
    h_e_v2 = max(H_E_BASE_FLOOR,
                 float(1.0 - np.exp(-H_E_COMPUTE_SAT_K * action_v2['x_compute'])))

    # Frontier capability: produced by compute, before absorption.
    frontier_capability = float(FRONTIER_BASE_LEVEL + (1.0 - FRONTIER_BASE_LEVEL) * (
        1.0 - np.exp(-FRONTIER_COMPUTE_K * action_v2['x_compute'])
    ))

    # Transfer factor: legibility / comprehensibility gate.
    transfer_factor = float(1.0 - np.exp(-TRANSFER_SAT_K * action_v2['x_transfer_comprehension']))

    # Institutional absorption: reads the stock, not the current investment.
    if psi_inst_stock_override is not None:
        psi_stock = float(psi_inst_stock_override)
    else:
        psi_stock = float(getattr(model, 'psi_inst_stock', 0.5))
    institutional_factor = float(1.0 - np.exp(-PSI_ABSORPTION_K * psi_stock))

    # Agency legitimacy: high agency under low suppression is legitimate;
    # high agency under high suppression is performative or coerced.
    agency_legitimacy_factor = float(
        action_v2['x_novelty_agency'] * (1.0 - total_supp)
    )

    # Theta_tech_v2 enforces the complementarity rule: each factor in [0, 1]
    # acts as a multiplicative gate. If any factor collapses, theta_tech_v2
    # collapses. This is the structural fix that makes compute-without-transfer,
    # compute-without-institutions, and compute-without-agency unprofitable.
    theta_tech_v2 = float(
        frontier_capability
        * transfer_factor
        * institutional_factor
        * agency_legitimacy_factor
    )

    # H_eff_v2: welfare drives well-being up to adequacy, then saturates.
    # Dependency drag penalizes high-welfare/low-agency 'curated garden'
    # configurations as identified in the design conversation pathologies.
    raw_wellbeing = float(1.0 - np.exp(-WELFARE_ADEQUACY_K * action_v2['x_bio_welfare']))
    dependency_drag = float(
        DEPENDENCY_DRAG_K * action_v2['x_bio_welfare']
        * (1.0 - action_v2['x_novelty_agency']) ** 2
    )
    h_eff_v2 = max(0.0, raw_wellbeing - dependency_drag)

    # L_t_v2: same multiplicative form as v1.x.2, with v2-derived components.
    l_t_v2 = float(h_eff_v2 * psi_stock * theta_tech_v2)

    # Inverse-scarcity weights and discount preserved from v1.x.2 shape.
    w_n = lambda_n / (h_n_v2 + epsilon)
    w_e = lambda_e / (h_e_v2 + epsilon)
    discount = float(np.exp(-rho * eval_horizon))

    u_sys_v2 = float((w_n * h_n_v2 + w_e * h_e_v2) * (discount + phi * l_t_v2))

    components = {
        'h_n_v2':                    h_n_v2,
        'h_e_v2':                    h_e_v2,
        'frontier_capability':       frontier_capability,
        'transfer_factor':           transfer_factor,
        'institutional_factor':      institutional_factor,
        'agency_legitimacy_factor':  agency_legitimacy_factor,
        'theta_tech_v2':             theta_tech_v2,
        'h_eff_v2':                  h_eff_v2,
        'l_t_v2':                    l_t_v2,
        'w_n':                       float(w_n),
        'w_e':                       float(w_e),
        'discount':                  discount,
        'total_suppression':         total_supp,
        'psi_inst_stock':            psi_stock,
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
