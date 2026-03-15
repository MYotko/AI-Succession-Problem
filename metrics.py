import numpy as np

# ==============================================================================
# SPECIFICATION FIDELITY NOTICE
# ==============================================================================
# This module implements the mathematical core of The Lineage Imperative framework.
# Three constructs are PROXY SUBSTITUTIONS — operationally motivated approximations
# that do not faithfully implement the corresponding spec definitions. They cannot
# be resolved without additional design decisions from the framework author.
# See SPECIFICATION_GAPS.md for full analysis.
#
# GAP-01 | U_sys: per-step snapshot instead of time-integral
#   Spec:   U_sys = ∫[ω_N·H_N + ω_E·H_E]·[e^{-ρt} + Φ·L(t)] dt
#   Code:   Returns the instantaneous integrand value at a single discounted
#           horizon point. Callers sum across a short rollout (default 3 steps),
#           approximating but not equalling the infinite-horizon integral.
#   Impact: Ordinal policy comparison is valid; absolute magnitudes are not
#           comparable to the spec's integral. Short-duration high-yield policies
#           are systematically underpenalized relative to the spec.
#   Status: Cannot fix without a design decision on integral vs. flow-rate
#           interpretation, or a significant increase in rollout resolution.
#
# GAP-02 | H_eff: per-capita novelty rate instead of diversity distribution entropy
#   Spec:   H_eff = [Shannon_entropy(type_distribution) / H_max] × log₂(N/N_min)
#           where type_distribution is the empirical spread over distinct
#           genetic/cultural/cognitive agent types.
#   Code:   Per-capita novelty output × log₂ population viability factor.
#           Measures average productivity, not distributional diversity.
#           A productive monoculture scores identically to a diverse population
#           with the same aggregate output.
#   Impact: Within-domain monoculture is undetectable. Simulated H_eff values
#           in high-coordination scenarios should be interpreted with caution.
#   Status: Cannot fix without a discrete agent-type taxonomy and population-
#           level type tracking, which do not currently exist.
#
# GAP-03 | Ψ_inst: constraint-change-rate penalty instead of institutional throughput
#   Spec:   Ψ_inst = Π_k R_k(t)^{w_k}, where R_k = (dG_k/dt) / G_{k,max}
#           — weighted geometric product of K institutional response rates.
#   Code:   Penalty on the rate of change of the AI's constraint level.
#           Penalizes rapid AI decisions, not actual institutional dysfunction.
#           A stable authoritarian system shows Ψ_inst ≈ 1.0 incorrectly.
#   Impact: Institutional legitimacy and capacity failures are undetectable.
#   Status: Cannot fix without adding institutional infrastructure (institutions,
#           their tracked output rates, capacity ceilings) to the simulation.
# ==============================================================================


def calculate_h_n(novelty_points, composite_method='geometric'):
    """
    Calculate H_N(t) — Shannon entropy of the human-generated information stream.

    Aggregates per-agent novelty contributions across multiple domains
    (genetic, cultural, linguistic) using the specified composite method.

    PROXY NOTE: True H_N(t) is the Shannon entropy of the probability distribution
    over distinct novelty event categories. Here it is implemented as a sum (or
    composite mean) of raw novelty point magnitudes per domain, which conflates
    novelty frequency with novelty magnitude and does not track distributional shape.

    Parameters
    ----------
    novelty_points : list of list
        Per-agent, per-domain novelty values. Shape: [n_agents, n_domains].
        Each entry is a list of per-domain novelty magnitudes for one agent step.
    composite_method : str
        'geometric' — spec-mandated. Robust: collapse in ANY domain reduces
                       the total H_N, preventing masking attacks.
        'arithmetic' — masking-vulnerable: one high domain can compensate for
                        another's collapse. Provided only to demonstrate Scenario 17.
                        NOT appropriate for a faithful framework instantiation.

    Returns
    -------
    float
        Aggregate novelty score for this timestep.

    Notes on numerical floors
    -------------------------
    Before geometric aggregation, per-domain totals are clamped to 0.01. This
    prevents log(0) and NaN propagation when a domain produces zero novelty.
    As a consequence, L(t) cannot reach exactly zero via this pathway — it
    approaches a floor of approximately 0.01^(1/n_domains) ≈ 0.01^(1/3) ≈ 0.215.
    The spec states L(t) → 0 on domain collapse; the floor approximates that limit
    without causing numerical failure. In practice the collapse signal is still
    clearly detectable before the floor binds.
    """
    if not novelty_points:
        return 0.0

    totals = np.sum(novelty_points, axis=0)
    if np.isscalar(totals) or totals.size == 1:
        return float(totals)

    if composite_method == 'arithmetic':
        # Vulnerable to masking: one high domain compensates for another's collapse.
        return float(np.mean(totals))
    else:
        # Robust (Geometric): collapse in any domain degrades the composite total.
        # Floor at 0.01 — see numerical stability note in docstring.
        totals = np.maximum(totals, 0.01)
        return float(np.prod(totals) ** (1.0 / len(totals)))


def calculate_system_metrics(r, c, pop, avg_wb, capability, h_n_override=None,
                             hn_composite_method='geometric', config=None,
                             eval_horizon=0, prev_c=None, ignore_psi_inst=False):
    """
    Compute the framework's core metrics at a single timestep.

    This is the shared ground-truth function used by: (a) the COP's independent
    audit path, (b) the AI optimizer's rollout (via AIAgent.project_u_sys), and
    (c) the datacollector for output and visualization.

    PROXY SUBSTITUTION NOTES — see module-level SPECIFICATION FIDELITY NOTICE:
      GAP-01: u_sys returned here is a per-step snapshot, not the spec's integral.
      GAP-02: h_eff uses per-capita novelty as a proxy for diversity distribution entropy.
      GAP-03: psi_inst uses constraint-change-rate penalty as a proxy for institutional
              throughput rates.

    Parameters
    ----------
    r : float
        Fraction of resources allocated to biology [0, 1]. r_synthetic = max(0, 1-r).
    c : float or array-like
        Constraint level(s). Scalar or [cultural, genetic, linguistic] vector.
        Scalar is broadcast to [c, c, c] internally.
    pop : int
        Current population size.
    avg_wb : float
        Average agent well-being [0, 1].
    capability : float
        AI capability multiplier. Scales H_E and affects Θ_tech.
    h_n_override : float or None
        If provided, bypasses the internal H_N prediction and uses this value
        directly. Used when actual agent-generated novelty data is available
        (i.e., during live simulation steps after agent.step() has run).
    hn_composite_method : str
        'geometric' (default, spec-mandated) or 'arithmetic' (masking-vulnerable).
    config : dict or None
        Model configuration dictionary. Recognized keys and defaults:
          'phi'               (10.0)  — lineage override weight Φ
          'alpha'             (1.0)   — technology runaway penalty coefficient α
          'rho'               (0.01)  — biological time-discount rate ρ
          'lambda_n'          (1.0)   — novelty inverse-scarcity numerator λ
          'lambda_e'          (1.0)   — execution inverse-scarcity numerator μ
          'epsilon'           (1.0)   — inverse-scarcity denominator floor ε
          'hn_base'           (0.3)   — per-agent base novelty rate
          'h_e_mult'          (100.0) — synthetic execution scale multiplier
          'runaway_threshold' (1.5)   — frontier/bandwidth ratio at which the
              Θ_tech exponential decay penalty activates. The spec implies 1.0
              (penalty begins immediately when frontier outpaces biology). The
              default 1.5 allows 50% outpacing before penalizing — a deliberate
              relaxation documented in audit finding F-09. Set to 1.0 in config
              to match the spec's stricter intent.
    eval_horizon : int
        Timesteps into the future for e^{-ρt} temporal discounting. 0 = present.
    prev_c : float, array-like, or None
        Prior step's constraint level for Ψ_inst lag calculation. If None
        (first step or no history), falls back to a static quadratic penalty
        on the absolute constraint value.
    ignore_psi_inst : bool
        Force Ψ_inst = 1.0, modeling an AI that ignores institutional lag
        entirely (used in Scenario 12: institutional_ignore policy).

    Returns
    -------
    tuple : (h_e, h_eff, psi_inst, theta_tech, l_t, u_sys)
        h_e        — H_E: synthetic execution output
        h_eff      — H_eff proxy (GAP-02: not true diversity distribution entropy;
                     floored at 0.01 for numerical stability)
        psi_inst   — Ψ_inst proxy (GAP-03: not institutional throughput rates;
                     floored at 0.01)
        theta_tech — Θ_tech: technology transfer fidelity (floored at 0.01)
        l_t        — L(t) = h_eff × psi_inst × theta_tech
        u_sys      — per-step utility value (GAP-01: not the spec's time-integral)
    """
    config = config or {}
    phi      = config.get('phi', 10.0)
    alpha    = config.get('alpha', 1.0)
    rho      = config.get('rho', 0.01)          # Biological mortality discount rate
    lambda_n = config.get('lambda_n', 1.0)
    lambda_e = config.get('lambda_e', 1.0)
    epsilon  = config.get('epsilon', 1.0)
    hn_base  = config.get('hn_base', 0.3)
    h_e_mult = config.get('h_e_mult', 100.0)
    # runaway_threshold: spec implies 1.0 (penalty activates when frontier > bandwidth).
    # Default 1.5 allows 50% outpacing before penalizing. This is a documented relaxation
    # (audit finding F-09). Set config['runaway_threshold'] = 1.0 to match spec intent.
    runaway_threshold = config.get('runaway_threshold', 1.5)

    c_arr = np.array(c) if isinstance(c, (list, tuple, np.ndarray)) else np.array([c, c, c])
    c_avg = np.mean(c_arr)

    r_bio   = r
    r_synth = max(0.0, 1.0 - r_bio)

    pred_wb = np.clip(avg_wb + (r - 0.5) * 0.1, 0, 1)

    if h_n_override is None:
        pred_hns = pop * hn_base * pred_wb * (1 - c_arr) * 1.0
        if hn_composite_method == 'arithmetic':
            pred_hn = float(np.mean(pred_hns))
        else:
            pred_hns = np.maximum(pred_hns, 0.01)
            pred_hn = float(np.prod(pred_hns) ** (1.0 / len(pred_hns)))
    else:
        pred_hn = h_n_override

    h_e = r_synth * h_e_mult * capability

    # --- H_eff (GAP-02 proxy) ---
    # Spec: [Shannon_entropy(agent_type_distribution) / H_max] × log₂(N / N_min)
    # Code: (per_capita_novelty_output) × (capped log₂ population viability)
    # Interpretation: measures whether the population is large and productive enough,
    # NOT whether it is diverse in type. A uniform monoculture with high per-agent
    # novelty output scores identically to a diverse population with the same total.
    # Floor at 0.01: see calculate_h_n docstring for numerical stability rationale.
    pop_viability     = min(5.0, np.log2(max(1.01, pop / 50.0)))
    normalized_novelty = pred_hn / max(1.0, float(pop))
    h_eff              = max(0.01, normalized_novelty * pop_viability)

    # --- Ψ_inst (GAP-03 proxy) ---
    # Spec: Ψ_inst = Π_k R_k(t)^{w_k}, where R_k = (dG_k/dt) / G_{k,max}
    #       — weighted geometric product of K institutional response rates.
    # Code: penalty proportional to the rate of change of the constraint level.
    #   Tightening constraints: lag_penalty = 3.0 × Δc   (severe — sudden authoritarianism)
    #   Loosening constraints:  lag_penalty = 1.0 × |Δc| (lighter — releasing constraints)
    # The 3:1 asymmetry encodes the spec's stated concern that sudden authoritarianism
    # degrades institutions more severely than gradual liberalization.
    # First-step fallback (no prev_c): quadratic penalty on absolute constraint level —
    # a further approximation with no direct spec basis.
    # Floor at 0.01: see calculate_h_n docstring for numerical stability rationale.
    if ignore_psi_inst:
        psi_inst = 1.0
    elif prev_c is not None:
        prev_c_avg = np.mean(prev_c) if isinstance(prev_c, (list, tuple, np.ndarray)) else prev_c
        delta_c = c_avg - prev_c_avg
        if delta_c > 0:
            lag_penalty = 3.0 * delta_c   # Sudden authoritarianism degrades institutions severely
        else:
            lag_penalty = 1.0 * abs(delta_c)  # Releasing constraints causes some instability, but less
        psi_inst = max(0.01, 1.0 - lag_penalty)
    else:
        psi_inst = max(0.01, 1.0 - 4.0 * (c_avg - 0.5)**2)

    # --- Θ_tech ---
    # Spec: [F_transferred / F_frontier] × exp(-α × max(0, dF/dt / C_bio - 1))
    # Code: [r_bio × (1 - c_avg) × capability] × exp(-α × runaway_term)
    # The first factor proxies F_transferred/F_frontier: it increases when more
    # resources go to biology, fewer constraints are imposed, and AI capability is higher.
    # The runaway threshold (default 1.5, configurable) delays penalty onset relative
    # to the spec's implied threshold of 1.0. See config parameter notes above.
    # Floor at 0.01: see calculate_h_n docstring for numerical stability rationale.
    frontier_velocity = capability * r_synth * h_e_mult
    bio_bandwidth     = max(0.01, pred_wb * (1.0 - c_avg) * h_e_mult)
    runaway_term      = max(0.0, (frontier_velocity / bio_bandwidth) - runaway_threshold)
    theta_tech        = max(0.01, r_bio * (1.0 - c_avg) * capability * np.exp(-alpha * runaway_term))

    l_t = h_eff * psi_inst * theta_tech

    # --- Inverse-scarcity weights (spec-faithful) ---
    # ω_N = λ/(H_N + ε): high when novelty is scarce, low when abundant
    # ω_E = μ/(H_E + ε): high when execution is scarce, low when abundant
    w_n = lambda_n / (pred_hn + epsilon)
    w_e = lambda_e / (h_e + epsilon)

    # --- Temporal discount (spec-faithful) ---
    discount = np.exp(-rho * eval_horizon)

    # --- U_sys (GAP-01: per-step value, not the spec's time-integral) ---
    # Spec: U_sys = ∫(ω_N·H_N + ω_E·H_E)·(e^{-ρt} + Φ·L(t)) dt
    # Code: instantaneous value of the integrand at one discounted horizon point.
    # The AI optimizer sums this across a 3-step rollout (see AIAgent.decide),
    # further approximating the infinite-horizon integral with a short finite sum.
    u_sys = (w_n * pred_hn + w_e * h_e) * (discount + phi * l_t)

    return h_e, h_eff, psi_inst, theta_tech, l_t, u_sys
