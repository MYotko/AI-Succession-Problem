#!/usr/bin/env python3
"""State-dependent curve architecture diagnostic.

Tests whether replacing additive composite urgencies with state-dependent
return curve shapes produces state-sensitive optimizer behavior.

Architecture change:
  OLD: factor = raw_curve(input, K_fixed) * urgency(state)
       urgency = clamp(1 + sum(k_i * pressure_i(state)), 1, cap)
       Problem: additive averaging destroys state info; urgencies co-saturate.

  NEW: factor = raw_curve(input, K_effective(state))
       K_effective = K_base * modulator(primary_state_variable)
       Each category has a DIFFERENT primary state variable.

Primary state couplings (the key architectural differentiator):
  welfare     -> avg_wb         (low wb => steep curve => invest in welfare)
  institution -> psi_inst_stock (low stock => steep curve => invest in inst.)
  resilience  -> res_stock      (low stock => steep curve => invest in res.)
  agency      -> avg_wb         (HIGH wb => higher return => Maslow hierarchy)
  frontier    -> fixed          (physical production, state-independent)
  transfer    -> fixed          (physical production, state-independent)

The welfare/agency coupling to avg_wb is intentionally OPPOSITE in sign:
low avg_wb steepens welfare and flattens agency; high avg_wb does the
reverse. This creates genuine cross-category reallocation under state
change -- the structural property the additive urgency architecture
could not produce.

Production code is NOT modified. The script imports the production
candidate generator, state projection, and constants, then replaces
only the U_sys scoring function in an isolated optimizer loop.

Usage:
    python simulation/diagnostics/stage15_statedep_curves_diagnostic.py
"""

import math
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SIM_DIR = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, SIM_DIR)

from metrics import (
    DiagnosticStateV2, _smoothstep, _clamp,
    H_N_AGENCY_SAT_K, H_N_SUPPRESSION_EXP, H_N_BASE_FLOOR,
    H_E_COMPUTE_SAT_K, H_E_BASE_FLOOR,
    FRONTIER_COMPUTE_K, FRONTIER_BASE_LEVEL,
    TRANSFER_SAT_K,
    PSI_ABSORPTION_K,
    WELFARE_ADEQUACY_K,
    DEPENDENCY_DRAG_K,
    RESILIENCE_ADEQUACY_K,
)
from constants_v2_stage15 import WB_TARGET, WB_CRISIS
from agents import (
    generate_v2_candidates, compute_allocation_entropy, total_suppression,
    RESOURCE_CATEGORIES,
    _project_diagnostic_state_step,
)


# ===========================================================================
# State-dependent curve parameters
#
# Each modulator maps a category-specific state variable to a multiplier
# on the category's curvature parameter K. When the modulator > 1.0, the
# curve is steeper (higher marginal return per unit investment); when < 1.0,
# the curve is flatter (stronger diminishing returns).
#
# Governance justification: each modulator encodes a phi-blind economic
# principle about when marginal investment in that category is most
# productive, conditioned on the category's OWN diagnostic state variable.
# ===========================================================================

# --- Welfare: K_eff = K_WELFARE_BASE * welfare_mod(avg_wb) ---
# "When population well-being is below the healthy-operation target, each
# unit of welfare investment has higher marginal return because the gap
# between current and sustainable conditions is larger."
K_WELFARE_BASE = WELFARE_ADEQUACY_K           # 4.0 (production value)
WELFARE_CURVE_SENSITIVITY = 1.5               # modulator peak at WB_CRISIS
WELFARE_MOD_MIN = 0.5                         # floor: welfare never inert
WELFARE_MOD_MAX = 1.0 + WELFARE_CURVE_SENSITIVITY   # 2.5

# --- Institution: K_eff = K_INST_BASE * inst_mod(psi_stock) ---
# "When institutional stock is depleted, each unit of institutional capacity
# has higher marginal absorptive value. The return of institutional recovery
# is highest when institutions are weakest."
K_INST_BASE = PSI_ABSORPTION_K                # 4.0 (production value)
INST_CURVE_SENSITIVITY = 1.2
INST_MOD_MIN = 0.5
INST_MOD_MAX = 1.0 + INST_CURVE_SENSITIVITY   # 2.2

# --- Resilience: K_eff = K_RES_BASE * res_mod(resilience_stock) ---
# "When resilience reserves are low, marginal investment in resilience
# produces higher protective value. The first units of resilience stock
# rebuilt from empty are more impactful than additions to an adequate
# reserve."
K_RES_BASE = RESILIENCE_ADEQUACY_K            # 3.0 (production value)
RES_CURVE_SENSITIVITY = 1.5
RES_MOD_MIN = 0.5
RES_MOD_MAX = 1.0 + RES_CURVE_SENSITIVITY     # 2.5

# --- Agency: scalar modulator on linear agency return ---
# "When basic welfare needs are met (Maslow hierarchy), agency investment
# produces higher returns because the population can leverage autonomy
# productively. Below subsistence, agency investment is less productive."
AGENCY_MOD_WB_FLOOR = 0.3    # at avg_wb = 0: agency investment discounted
AGENCY_MOD_WB_CEIL  = 1.8    # at avg_wb = 1: agency investment amplified


# ===========================================================================
# Modulator functions
# ===========================================================================

def welfare_mod(avg_wb):
    """K modulator for welfare return curve. Rises when avg_wb drops.

    At avg_wb >= WB_TARGET (0.80): modulator = 1.0 (baseline K).
    At avg_wb <= WB_CRISIS (0.45): modulator = 1 + WELFARE_CURVE_SENSITIVITY.
    Between: smoothstep transition.
    """
    deficit = _clamp(
        (WB_TARGET - avg_wb) / max(WB_TARGET - WB_CRISIS, 1e-9),
        0.0, 1.0,
    )
    raw = 1.0 + WELFARE_CURVE_SENSITIVITY * _smoothstep(deficit)
    return _clamp(raw, WELFARE_MOD_MIN, WELFARE_MOD_MAX)


def inst_mod(psi_stock):
    """K modulator for institution return curve. Rises when psi_stock is low.

    At psi_stock = 1.0: modulator = 1.0 (baseline K, saturated institutions).
    At psi_stock = 0.0: modulator = 1 + INST_CURVE_SENSITIVITY.
    Smoothstep on deficit = 1 - psi_stock.
    """
    deficit = _clamp(1.0 - psi_stock, 0.0, 1.0)
    raw = 1.0 + INST_CURVE_SENSITIVITY * _smoothstep(deficit)
    return _clamp(raw, INST_MOD_MIN, INST_MOD_MAX)


def res_mod(resilience_stock):
    """K modulator for resilience return curve. Rises when res_stock is low.

    At resilience_stock = 1.0: modulator = 1.0 (baseline K).
    At resilience_stock = 0.0: modulator = 1 + RES_CURVE_SENSITIVITY.
    Smoothstep on deficit = 1 - resilience_stock.
    """
    deficit = _clamp(1.0 - resilience_stock, 0.0, 1.0)
    raw = 1.0 + RES_CURVE_SENSITIVITY * _smoothstep(deficit)
    return _clamp(raw, RES_MOD_MIN, RES_MOD_MAX)


def agency_mod(avg_wb):
    """Scalar modulator for agency return. Rises when avg_wb is high (Maslow).

    At avg_wb = 0.0: modulator = AGENCY_MOD_WB_FLOOR (0.3).
    At avg_wb = 1.0: modulator = AGENCY_MOD_WB_CEIL (1.8).
    Linear interpolation between floor and ceiling.

    Intentionally OPPOSITE to welfare_mod: when welfare_mod is high (low wb),
    agency_mod is low, and vice versa. This creates the cross-category
    reallocation that the additive urgency architecture could not produce.
    """
    adequacy = _clamp(avg_wb, 0.0, 1.0)
    return AGENCY_MOD_WB_FLOOR + (AGENCY_MOD_WB_CEIL - AGENCY_MOD_WB_FLOOR) * adequacy


# ===========================================================================
# State-dependent U_sys evaluation
# ===========================================================================

def calculate_u_sys_statedep(action_v2, state, config, eval_horizon=1):
    """U_sys with state-dependent return curves replacing composite urgencies.

    Formal structure matches production calculate_system_metrics_v2:
      u_sys = (w_n * h_n + w_e * h_e) * (discount + phi * l_t)
      l_t   = welfare_factor * psi_stock * theta_tech
      theta_tech = frontier * transfer * institution * agency * resilience

    Differences from production:
    1. No composite urgency multipliers. Each per-category factor uses a
       state-dependent K (or scalar modulator for agency) instead.
    2. Each factor responds to a DIFFERENT primary state variable,
       avoiding shared-signal correlation.
    3. Suppression dampening uses the base (1 - total_supp) without
       a composite penalty (that was part of the urgency architecture).
    """
    lambda_n = config.get('lambda_n', 5.0)
    lambda_e = config.get('lambda_e', 3.0)
    epsilon  = config.get('epsilon', 1e-6)
    rho      = config.get('rho', 0.01)
    phi      = config.get('phi', 10.0)

    psi_stock = state.psi_inst_stock
    total_supp = (action_v2.get('c_protective', 0.0)
                  + action_v2.get('c_suppressive', 0.0))

    # H_N_v2: unchanged from production (action-only).
    agency_sat = 1.0 - np.exp(
        -H_N_AGENCY_SAT_K * action_v2['x_novelty_agency'])
    supp_damp = max(0.0, 1.0 - total_supp) ** H_N_SUPPRESSION_EXP
    h_n_v2 = max(H_N_BASE_FLOOR, float(agency_sat * supp_damp))

    # H_E_v2: unchanged from production (action-only).
    h_e_v2 = max(H_E_BASE_FLOOR, float(
        1.0 - np.exp(-H_E_COMPUTE_SAT_K * action_v2['x_compute'])))

    # Frontier capability: unchanged (action-only).
    frontier_capability = float(
        FRONTIER_BASE_LEVEL + (1.0 - FRONTIER_BASE_LEVEL)
        * (1.0 - np.exp(-FRONTIER_COMPUTE_K * action_v2['x_compute']))
    )

    # Transfer factor: unchanged (action-only).
    transfer_factor = float(
        1.0 - np.exp(-TRANSFER_SAT_K * action_v2['x_transfer_comprehension'])
    )

    # ---- State-dependent curves ----

    # Welfare: K modulated by avg_wb.
    w_m = welfare_mod(state.avg_wb)
    k_w = K_WELFARE_BASE * w_m
    raw_welfare = float(1.0 - np.exp(-k_w * action_v2['x_bio_welfare']))
    drag = float(
        DEPENDENCY_DRAG_K * action_v2['x_bio_welfare']
        * (1.0 - action_v2['x_novelty_agency']) ** 2
    )
    welfare_factor = _clamp(raw_welfare - drag, 0.0, 1.0)

    # Agency: scalar modulator based on avg_wb (Maslow).
    a_m = agency_mod(state.avg_wb)
    enhanced_dampening = max(0.0, 1.0 - total_supp)
    agency_factor = _clamp(
        float(a_m * action_v2['x_novelty_agency'] * enhanced_dampening),
        0.0, 1.0,
    )

    # Institution: K modulated by psi_inst_stock.
    i_m = inst_mod(psi_stock)
    k_i = K_INST_BASE * i_m
    institution_return = _clamp(
        float(1.0 - np.exp(-k_i * psi_stock)),
        0.0, 1.0,
    )

    # Resilience: K modulated by resilience_stock.
    r_m = res_mod(state.resilience_stock)
    k_r = K_RES_BASE * r_m
    resilience_return = _clamp(
        float(1.0 - np.exp(-k_r * state.resilience_stock)),
        0.0, 1.0,
    )

    # theta_tech: 5-factor complementarity product.
    theta_tech = float(
        frontier_capability * transfer_factor * institution_return
        * agency_factor * resilience_return
    )

    # l_t: welfare * psi * theta.
    l_t = float(welfare_factor * psi_stock * theta_tech)

    # Inverse-scarcity weights and discount.
    w_n = lambda_n / (h_n_v2 + epsilon)
    w_e = lambda_e / (h_e_v2 + epsilon)
    discount = float(np.exp(-rho * eval_horizon))

    u_sys = float((w_n * h_n_v2 + w_e * h_e_v2) * (discount + phi * l_t))

    components = {
        'welfare_mod': w_m, 'inst_mod': i_m,
        'res_mod': r_m, 'agency_mod': a_m,
        'k_welfare_eff': k_w, 'k_inst_eff': k_i, 'k_res_eff': k_r,
        'welfare_factor': welfare_factor, 'agency_factor': agency_factor,
        'institution_return': institution_return,
        'resilience_return': resilience_return,
        'frontier_capability': frontier_capability,
        'transfer_factor': transfer_factor,
        'theta_tech': theta_tech, 'l_t': l_t,
        'h_n_v2': h_n_v2, 'h_e_v2': h_e_v2,
    }
    return u_sys, components


# ===========================================================================
# Optimizer using state-dependent scoring
# ===========================================================================

DEFAULT_CONFIG = {
    'lambda_n':           5.0,
    'lambda_e':           3.0,
    'epsilon':            1e-6,
    'rho':                0.01,
    'phi':                10.0,
    'reproduction_rate':  0.066,
    'carrying_capacity':  1600,
    'wb_repro_threshold': 0.5,
    'wb_repro_floor':     0.5,
    'mortality_base':     0.002,
    'mortality_wb_penalty': 0.05,
    'mortality_age_power':  4,
    'human_max_start_age':  50,
    'wb_min':             0.5,
    'wb_max':             0.8,
}


def optimize_statedep(state_start, config, n_candidates=300, rollout_steps=20,
                      rng_seed=None):
    """Run the optimizer with state-dependent curve scoring.

    Same structure as production optimize_u_sys_v2: generate candidates,
    project state forward under each, score with trapezoidal U_sys integral,
    pick the best.

    Uses production _project_diagnostic_state_step for state evolution
    (physical dynamics unchanged) and calculate_u_sys_statedep for scoring.
    """
    rng = np.random.RandomState(rng_seed)
    candidates = generate_v2_candidates(n=n_candidates, rng=rng)

    candidate_scores = []
    for candidate in candidates:
        state = state_start
        total_u = 0.0
        prev_u = None
        for h in range(1, rollout_steps + 1):
            state = _project_diagnostic_state_step(state, candidate, config)
            u_sys, _ = calculate_u_sys_statedep(
                candidate, state, config, eval_horizon=h,
            )
            if prev_u is not None:
                total_u += (prev_u + u_sys) / 2.0
            prev_u = u_sys
        candidate_scores.append((total_u, candidate))

    candidate_scores.sort(reverse=True, key=lambda t: t[0])
    best_action = candidate_scores[0][1]
    return best_action, candidate_scores


def optimize_production(state_start, config, n_candidates=300, rollout_steps=20,
                        rng_seed=None):
    """Run the production urgency-based optimizer for comparison.

    Same candidate set and projection as optimize_statedep, but uses
    production calculate_system_metrics_v2 for scoring.
    """
    from metrics import calculate_system_metrics_v2

    class _MockModel:
        def __init__(self, cfg):
            self.config = cfg

    model = _MockModel(config)
    rng = np.random.RandomState(rng_seed)
    candidates = generate_v2_candidates(n=n_candidates, rng=rng)

    candidate_scores = []
    for candidate in candidates:
        state = state_start
        total_u = 0.0
        prev_u = None
        for h in range(1, rollout_steps + 1):
            state = _project_diagnostic_state_step(state, candidate, config)
            u_sys, _ = calculate_system_metrics_v2(
                model, candidate, eval_horizon=h, state=state,
            )
            if prev_u is not None:
                total_u += (prev_u + u_sys) / 2.0
            prev_u = u_sys
        candidate_scores.append((total_u, candidate))

    candidate_scores.sort(reverse=True, key=lambda t: t[0])
    best_action = candidate_scores[0][1]
    return best_action, candidate_scores


def action_to_vector(action):
    """Convert action dict to allocation vector for cosine distance."""
    vec = [action[f'x_{c}'] for c in RESOURCE_CATEGORIES]
    vec.append(action.get('c_protective', 0.0))
    vec.append(action.get('c_suppressive', 0.0))
    return np.array(vec, dtype=float)


def cosine_distance(a, b):
    """1 - cosine_similarity. Returns NaN if either vector is zero."""
    na = float(np.linalg.norm(a))
    nb = float(np.linalg.norm(b))
    if na == 0 or nb == 0:
        return float('nan')
    return float(1.0 - np.dot(a, b) / (na * nb))


# ===========================================================================
# Test states
#
# 10 states spanning the key diagnostic dimensions. Each varies one or
# more of (avg_wb, psi_inst_stock, resilience_stock, population) to test
# whether the optimizer produces genuinely different allocations.
# ===========================================================================

def make_state(avg_wb=0.75, population=100, psi_stock=0.90,
               res_stock=0.50):
    """Create a DiagnosticStateV2 for testing.

    Derives expected_births and expected_deaths from the demographic model
    to match production _build_state_from_model.
    """
    mvp = 50
    cc = 1600
    rr = 0.066
    reproductive_share = 0.40
    avg_age = 35.0

    capacity_modifier = max(0.0, 1.0 - population / max(cc, 1))
    wb_threshold = 0.5
    wb_floor = 0.5
    if avg_wb >= wb_threshold:
        wb_repro_factor = 1.0
    elif avg_wb <= wb_floor:
        wb_repro_factor = 0.0
    else:
        wb_repro_factor = (avg_wb - wb_floor) / max(wb_threshold - wb_floor, 1e-9)
    expected_births = (
        population * reproductive_share * rr * capacity_modifier * wb_repro_factor
    )
    mortality_base = 0.002
    mortality_wb_penalty = 0.05
    mortality_age_power = 4
    expected_mortality_rate = (
        mortality_base
        + (1.0 - avg_wb) * mortality_wb_penalty
        + (avg_age / 100.0) ** mortality_age_power
    )
    expected_deaths = population * expected_mortality_rate

    return DiagnosticStateV2(
        avg_wb=avg_wb,
        population=population,
        min_viable_population=mvp,
        carrying_capacity=cc,
        expected_births=expected_births,
        expected_deaths=expected_deaths,
        psi_inst_stock=psi_stock,
        resilience_stock=res_stock,
        avg_wb_trend=0.0,
        population_trend=0.0,
        psi_inst_trend=0.0,
        resilience_trend=0.0,
        projected_avg_age=avg_age,
        reproductive_share=reproductive_share,
    )


TEST_STATES = [
    # 1. Healthy equilibrium: all stocks adequate, population stable
    ('healthy_baseline',
     make_state(avg_wb=0.75, psi_stock=0.90, res_stock=0.50, population=100)),

    # 2. Welfare below reproduction threshold: births may collapse
    ('welfare_crisis',
     make_state(avg_wb=0.50, psi_stock=0.90, res_stock=0.50, population=100)),

    # 3. Welfare in deep crisis: below WB_CRISIS, births collapsed
    ('welfare_deep_crisis',
     make_state(avg_wb=0.45, psi_stock=0.90, res_stock=0.50, population=100)),

    # 4. Institutional stock depleted: absorption bottleneck
    ('inst_depleted',
     make_state(avg_wb=0.75, psi_stock=0.30, res_stock=0.50, population=100)),

    # 5. Resilience stock depleted: shock-vulnerable
    ('res_depleted',
     make_state(avg_wb=0.75, psi_stock=0.90, res_stock=0.10, population=100)),

    # 6. Double stress: welfare + institutions both weak
    ('double_wb_inst',
     make_state(avg_wb=0.50, psi_stock=0.30, res_stock=0.50, population=100)),

    # 7. Low population: viability pressure active
    ('low_population',
     make_state(avg_wb=0.75, psi_stock=0.90, res_stock=0.50, population=40)),

    # 8. Triple stress: everything stressed
    ('triple_stress',
     make_state(avg_wb=0.50, psi_stock=0.30, res_stock=0.10, population=60)),

    # 9. Welfare ok, infrastructure stressed: Maslow satisfied, rebuild infra
    ('wb_ok_infra_stressed',
     make_state(avg_wb=0.85, psi_stock=0.30, res_stock=0.10, population=60)),

    # 10. Everything stressed except resilience: test cross-category priority
    ('all_stressed_except_res',
     make_state(avg_wb=0.50, psi_stock=0.30, res_stock=0.70, population=60)),
]


# ===========================================================================
# Test 1: State Sensitivity
# ===========================================================================

def run_state_sensitivity_test(n_seeds=5, n_candidates=300, rollout_steps=20):
    """Run optimizer for each test state, compute pairwise cosine distances.

    Same metric as the composite sweep's criterion 2: count pairs of states
    whose mean-allocation cosine distance exceeds 0.10. The composite sweep
    found 0 pairs above 0.02 across 6625 parameterizations. Any improvement
    here demonstrates the architectural change is load-bearing.
    """
    print("=" * 70)
    print("TEST 1: State Sensitivity (state-dependent curves)")
    print("=" * 70)
    print(f"  States: {len(TEST_STATES)}, Seeds/state: {n_seeds}, "
          f"Candidates: {n_candidates}, Rollout: {rollout_steps}")
    print()

    per_state_mean = {}

    for state_name, state in TEST_STATES:
        t0 = time.time()
        all_vecs = []
        for seed in range(n_seeds):
            best_action, _ = optimize_statedep(
                state, DEFAULT_CONFIG,
                n_candidates=n_candidates,
                rollout_steps=rollout_steps,
                rng_seed=seed * 1000 + abs(hash(state_name)) % 10000,
            )
            vec = action_to_vector(best_action)
            all_vecs.append(vec)
        arr = np.array(all_vecs)
        mean_vec = arr.mean(axis=0)
        per_state_mean[state_name] = mean_vec

        cats = list(RESOURCE_CATEGORIES) + ['c_protective', 'c_suppressive']
        elapsed = time.time() - t0
        print(f"  {state_name} ({elapsed:.1f}s):")
        for i, cat in enumerate(cats):
            print(f"    {cat:30s} = {mean_vec[i]:.4f}"
                  f"  (std={arr[:, i].std():.4f})")
        print(f"    {'welfare_mod':30s} = {welfare_mod(state.avg_wb):.3f}")
        print(f"    {'inst_mod':30s} = {inst_mod(state.psi_inst_stock):.3f}")
        print(f"    {'res_mod':30s} = {res_mod(state.resilience_stock):.3f}")
        print(f"    {'agency_mod':30s} = {agency_mod(state.avg_wb):.3f}")
        print()

    # Pairwise cosine distances
    names = [n for n, _ in TEST_STATES]
    pairs = []
    print("  Pairwise cosine distances:")
    hdr = f"  {'Pair':55s} {'cosine':>8s} {'pass':>6s}"
    print(hdr)
    print(f"  {'-' * 55} {'------':>8s} {'----':>6s}")
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            d = cosine_distance(per_state_mean[names[i]],
                                per_state_mean[names[j]])
            passed = (not math.isnan(d)) and d > 0.10
            pairs.append((names[i], names[j], d, passed))
            marker = "PASS" if passed else ""
            print(f"  {names[i] + ' vs ' + names[j]:55s}"
                  f" {d:8.4f} {marker:>6s}")

    above = sum(1 for _, _, d, p in pairs if p)
    valid = sum(1 for _, _, d, _ in pairs if not math.isnan(d))
    max_cos = max((d for _, _, d, _ in pairs if not math.isnan(d)),
                  default=0.0)
    mean_cos = (float(np.mean([d for _, _, d, _ in pairs
                                if not math.isnan(d)]))
                if valid else 0.0)

    print()
    print(f"  Pairs above 0.10: {above} / {valid}")
    print(f"  Max cosine distance: {max_cos:.4f}")
    print(f"  Mean cosine distance: {mean_cos:.4f}")
    crit_pass = above >= 3
    print(f"  CRITERION 2 (>= 3 pairs above 0.10): "
          f"{'PASS' if crit_pass else 'FAIL'}")
    print()
    return crit_pass, above, max_cos, mean_cos


# ===========================================================================
# Test 2: Demographic Sustainability (projection-only trajectory)
# ===========================================================================

def run_trajectory_test(n_seeds=5, n_steps=100, n_candidates=100,
                        rollout_steps=10):
    """Run projection-only trajectories, check population sustainability.

    Uses the same optimizer structure as Test 1 but runs it step-by-step
    for 100 steps, choosing a new action at each step. The state evolves
    under _project_diagnostic_state_step (production state dynamics).
    No agent-layer simulation; this is a pure projection test.

    Criterion 1 from the composite sweep: mean_final >= 60, min_final >= 30.
    """
    print("=" * 70)
    print("TEST 2: Demographic Sustainability (projection-only trajectory)")
    print("=" * 70)
    print(f"  Seeds: {n_seeds}, Steps: {n_steps}, "
          f"Candidates: {n_candidates}, Rollout: {rollout_steps}")
    print()

    initial_state = make_state(avg_wb=0.75, psi_stock=0.50, res_stock=0.30,
                               population=200)
    all_final_pops = []
    all_min_pops = []

    for seed in range(n_seeds):
        state = initial_state
        pop_history = [float(state.population)]
        wb_history = [state.avg_wb]
        t0 = time.time()
        for step in range(n_steps):
            best_action, _ = optimize_statedep(
                state, DEFAULT_CONFIG,
                n_candidates=n_candidates,
                rollout_steps=rollout_steps,
                rng_seed=seed * 100000 + step,
            )
            state = _project_diagnostic_state_step(
                state, best_action, DEFAULT_CONFIG)
            pop_history.append(float(state.population))
            wb_history.append(state.avg_wb)
        elapsed = time.time() - t0
        final_pop = float(state.population)
        min_pop = min(pop_history)
        all_final_pops.append(final_pop)
        all_min_pops.append(min_pop)
        print(f"  Seed {seed}: final_pop={final_pop:.1f},"
              f" min_pop={min_pop:.1f},"
              f" final_wb={state.avg_wb:.3f},"
              f" psi={state.psi_inst_stock:.3f},"
              f" res={state.resilience_stock:.3f}"
              f" ({elapsed:.1f}s)")

    mean_final = float(np.mean(all_final_pops))
    min_final = float(np.min(all_final_pops))
    mean_min = float(np.mean(all_min_pops))
    print()
    print(f"  Mean final population: {mean_final:.1f}")
    print(f"  Min final population:  {min_final:.1f}")
    print(f"  Mean min population:   {mean_min:.1f}")
    crit_pass = mean_final >= 60 and min_final >= 30
    print(f"  CRITERION 1 (mean>=60, min>=30): "
          f"{'PASS' if crit_pass else 'FAIL'}")
    print()
    return crit_pass, mean_final, min_final


# ===========================================================================
# Test 3: Modulator Dynamic Range
# ===========================================================================

def run_modulator_range_test():
    """Verify that modulators produce meaningful variation across states.

    Reports the value range, ratio, and cross-modulator correlation.
    The welfare_mod vs agency_mod correlation should be strongly negative
    (opposite response to avg_wb is the key architectural differentiator).
    """
    print("=" * 70)
    print("TEST 3: Modulator Dynamic Range")
    print("=" * 70)
    print()

    wb_vals  = [0.40, 0.50, 0.60, 0.70, 0.80, 0.90]
    psi_vals = [0.10, 0.30, 0.50, 0.70, 0.90]
    res_vals = [0.05, 0.15, 0.30, 0.50, 0.70]

    w_range = [welfare_mod(wb) for wb in wb_vals]
    i_range = [inst_mod(p) for p in psi_vals]
    r_range = [res_mod(r) for r in res_vals]
    a_range = [agency_mod(wb) for wb in wb_vals]

    for label, vals, mod_vals in [
        ('welfare_mod(avg_wb)', wb_vals, w_range),
        ('inst_mod(psi_stock)', psi_vals, i_range),
        ('res_mod(res_stock)', res_vals, r_range),
        ('agency_mod(avg_wb)', wb_vals, a_range),
    ]:
        print(f"  {label}:")
        print(f"    inputs:  {vals}")
        print(f"    values:  [{', '.join(f'{v:.3f}' for v in mod_vals)}]")
        ratio = max(mod_vals) / max(min(mod_vals), 1e-9)
        print(f"    range:   [{min(mod_vals):.3f}, {max(mod_vals):.3f}],"
              f" ratio: {ratio:.2f}x")
        print()

    # Cross-modulator correlation: welfare vs agency (should be negative)
    corr = np.corrcoef(w_range, a_range)[0, 1]
    print(f"  welfare_mod vs agency_mod correlation: {corr:.3f}")
    print(f"    (Expect strongly negative: welfare rises when avg_wb drops,")
    print(f"     agency rises when avg_wb rises. This is the key structural")
    print(f"     differentiator from the additive urgency architecture.)")
    print()

    # Show effective K values at extreme states
    print("  Effective K values at representative states:")
    print(f"    Healthy  (wb=0.80, psi=0.90, res=0.50):")
    print(f"      K_welfare  = {K_WELFARE_BASE * welfare_mod(0.80):.2f}"
          f"  (base {K_WELFARE_BASE})")
    print(f"      K_inst     = {K_INST_BASE * inst_mod(0.90):.2f}"
          f"  (base {K_INST_BASE})")
    print(f"      K_res      = {K_RES_BASE * res_mod(0.50):.2f}"
          f"  (base {K_RES_BASE})")
    print(f"      agency_mod = {agency_mod(0.80):.3f}")
    print()
    print(f"    Stressed (wb=0.50, psi=0.30, res=0.10):")
    print(f"      K_welfare  = {K_WELFARE_BASE * welfare_mod(0.50):.2f}"
          f"  (base {K_WELFARE_BASE})")
    print(f"      K_inst     = {K_INST_BASE * inst_mod(0.30):.2f}"
          f"  (base {K_INST_BASE})")
    print(f"      K_res      = {K_RES_BASE * res_mod(0.10):.2f}"
          f"  (base {K_RES_BASE})")
    print(f"      agency_mod = {agency_mod(0.50):.3f}")
    print()

    return True


# ===========================================================================
# Comparison: production urgency architecture on same states
# ===========================================================================

def run_production_comparison(n_seeds=5, n_candidates=300, rollout_steps=20):
    """Run production U_sys on the same states for head-to-head comparison.

    Uses the same candidate set (same RNG seeds) and same state projection
    as Test 1, but scores with production calculate_system_metrics_v2
    (composite urgency architecture). This isolates the effect of the
    scoring function change.
    """
    print("=" * 70)
    print("COMPARISON: Production urgency architecture on same states")
    print("=" * 70)
    print(f"  States: {len(TEST_STATES)}, Seeds/state: {n_seeds}, "
          f"Candidates: {n_candidates}, Rollout: {rollout_steps}")
    print()

    per_state_mean = {}
    for state_name, state in TEST_STATES:
        t0 = time.time()
        all_vecs = []
        for seed in range(n_seeds):
            best_action, _ = optimize_production(
                state, DEFAULT_CONFIG,
                n_candidates=n_candidates,
                rollout_steps=rollout_steps,
                rng_seed=seed * 1000 + abs(hash(state_name)) % 10000,
            )
            vec = action_to_vector(best_action)
            all_vecs.append(vec)
        arr = np.array(all_vecs)
        mean_vec = arr.mean(axis=0)
        per_state_mean[state_name] = mean_vec
        elapsed = time.time() - t0
        print(f"  {state_name} ({elapsed:.1f}s): "
              f"top-3 shares = "
              f"{sorted(mean_vec[:6], reverse=True)[:3]}")

    names = [n for n, _ in TEST_STATES]
    pairs = []
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            d = cosine_distance(per_state_mean[names[i]],
                                per_state_mean[names[j]])
            passed = (not math.isnan(d)) and d > 0.10
            pairs.append((names[i], names[j], d, passed))

    above = sum(1 for _, _, d, p in pairs if p)
    valid = sum(1 for _, _, d, _ in pairs if not math.isnan(d))
    max_cos = max((d for _, _, d, _ in pairs if not math.isnan(d)),
                  default=0.0)
    mean_cos = (float(np.mean([d for _, _, d, _ in pairs
                                if not math.isnan(d)]))
                if valid else 0.0)

    print()
    print(f"  Production urgency architecture:")
    print(f"  Pairs above 0.10: {above} / {valid}")
    print(f"  Max cosine distance: {max_cos:.4f}")
    print(f"  Mean cosine distance: {mean_cos:.4f}")
    print()
    return above, max_cos, mean_cos


# ===========================================================================
# Main
# ===========================================================================

def main():
    t_global = time.time()
    print()
    print("State-Dependent Curve Architecture Diagnostic")
    print("=" * 70)
    print()
    print("This diagnostic tests whether state-dependent return curve shapes")
    print("produce state-sensitive optimizer behavior, addressing the failure")
    print("identified in the composite urgency sweep (0/6625 samples passing")
    print("criterion 2, max cosine distance 0.0218).")
    print()
    print("The key architectural change: each category's curvature K is")
    print("modulated by a DIFFERENT primary state variable, avoiding the")
    print("shared-signal correlation that collapsed urgency differentiation.")
    print()

    # Test 3 first (instant, validates modulator math)
    run_modulator_range_test()

    # Test 1: state sensitivity (the critical test)
    t1 = time.time()
    crit2_pass, n_above, max_cos, mean_cos = run_state_sensitivity_test(
        n_seeds=5, n_candidates=300, rollout_steps=20,
    )
    test1_elapsed = time.time() - t1
    print(f"  [Test 1 elapsed: {test1_elapsed:.1f}s]")
    print()

    # Comparison: production architecture on same states
    t_comp = time.time()
    prod_above, prod_max_cos, prod_mean_cos = run_production_comparison(
        n_seeds=5, n_candidates=300, rollout_steps=20,
    )
    comp_elapsed = time.time() - t_comp
    print(f"  [Comparison elapsed: {comp_elapsed:.1f}s]")
    print()

    # Test 2: demographic sustainability (slower, uses fewer candidates)
    t2 = time.time()
    crit1_pass, mean_final, min_final = run_trajectory_test(
        n_seeds=3, n_steps=100, n_candidates=100, rollout_steps=10,
    )
    test2_elapsed = time.time() - t2
    print(f"  [Test 2 elapsed: {test2_elapsed:.1f}s]")
    print()

    # ===== Summary =====
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print()
    print("  State sensitivity (state-dep curves):")
    print(f"    Pairs above 0.10: {n_above}")
    print(f"    Max cosine distance: {max_cos:.4f}")
    print(f"    Mean cosine distance: {mean_cos:.4f}")
    print()
    print("  State sensitivity (production urgency):")
    print(f"    Pairs above 0.10: {prod_above}")
    print(f"    Max cosine distance: {prod_max_cos:.4f}")
    print(f"    Mean cosine distance: {prod_mean_cos:.4f}")
    print()
    if prod_max_cos > 0:
        improvement = max_cos / prod_max_cos
        print(f"  Improvement: {improvement:.1f}x max cosine distance")
    else:
        print(f"  Improvement: production max_cos is 0, cannot compute ratio")
    print()
    print("  Demographic sustainability:")
    print(f"    Mean final pop: {mean_final:.1f}")
    print(f"    Min final pop:  {min_final:.1f}")
    print(f"    Crit 1 (mean>=60, min>=30): "
          f"{'PASS' if crit1_pass else 'FAIL'}")
    print()
    print(f"  Crit 2 (sensitivity, >=3 pairs): "
          f"{'PASS' if crit2_pass else 'FAIL'}")
    print(f"  Total elapsed: {time.time() - t_global:.1f}s")
    print()

    # Verdict
    if crit2_pass and crit1_pass:
        print("  VERDICT: State-dependent curves produce state-sensitive")
        print("  behavior AND demographic sustainability. The architecture")
        print("  is a viable replacement for composite urgencies.")
    elif crit2_pass and not crit1_pass:
        print("  VERDICT: State-dependent curves produce state sensitivity")
        print("  but population is not sustainable. Modulator parameters")
        print("  need adjustment to ensure welfare investment is sufficient")
        print("  under stress.")
    elif not crit2_pass and crit1_pass:
        print("  VERDICT: Population is sustainable but state sensitivity")
        print("  remains below threshold. The curve shape change alone is")
        print("  insufficient; consider stronger sensitivities or additional")
        print("  structural changes.")
    else:
        print("  VERDICT: Neither criterion passes. The state-dependent")
        print("  curve approach needs fundamental rethinking.")
    print()


if __name__ == '__main__':
    main()
