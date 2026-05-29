import numpy as np
from metrics import calculate_system_metrics, calculate_system_metrics_v2

# =============================================================================
# v2 MULTI-SINK ALLOCATOR — module-level constants and helpers
#
# This block adds the v2 action space (six budget-constrained resource
# categories plus two coupled constraint posture variables) and the candidate
# generator that the v2 policy samples from. The v1.x.2 policy
# (optimize_u_sys) and its grid search below are untouched.
#
# Every numerical parameter is a named constant with a comment citing the
# governance justification from the design conversations. Stage 2 (acceptance
# gate validation) and Stage 3 (phi sweep) operate on these frozen curves.
# =============================================================================

# Six resource categories. Order is the canonical order used everywhere in
# v2 code (anchor x-vectors, allocation entropy, datacollector field order).
RESOURCE_CATEGORIES = (
    'compute',                 # frontier computational capability investment
    'bio_welfare',             # direct biological welfare provisioning
    'novelty_agency',          # space for human-originated novelty and choice
    'institutional_capacity',  # investment in Psi_inst stock
    'transfer_comprehension',  # legibility and absorption infrastructure
    'resilience',              # buffer against exogenous shock and succession load
)
N_RESOURCE_CATEGORIES = len(RESOURCE_CATEGORIES)

# Stratified sampling mix. Total = 300 per decision (matches v1.x.2 cost in
# operations per decision step: 10x10 grid x 20 rollout horizons = 2000 metric
# calls vs v2's 300 x 20 = 6000, roughly 3x more expensive per decision but
# still under one second per step on commodity hardware).
N_UNIFORM_DIRICHLET   = 100  # broad simplex coverage; phi-blind exploration baseline
N_BALANCED_DIRICHLET  = 100  # center-weighted coverage; tests interior tradeoffs
N_SINGLE_FOCAL_SPARSE = 60   # near-corner stress; one category dominant, others starved
N_DUAL_FOCAL_SPARSE   = 20   # near-edge stress; two categories dominant, others starved
N_ANCHORS             = 20   # fixed interpretability anchors at known positions

# Dirichlet concentration parameters. Higher alpha pulls toward the center;
# lower alpha pulls toward corners. The chosen values produce three distinct
# regimes of resource concentration so the optimizer has access to corner-like,
# interior, and balanced allocations.
ALPHA_UNIFORM    = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
ALPHA_BALANCED   = [2.0, 2.0, 2.0, 2.0, 2.0, 2.0]
ALPHA_FOCAL_HIGH = 5.0    # concentration on focal category in sparse samples
ALPHA_FOCAL_LOW  = 0.35   # concentration on non-focal categories (pulls toward zero)
ALPHA_DUAL_HIGH  = 3.0    # concentration on each of the two focal categories
ALPHA_DUAL_LOW   = 0.35

# 6x6 grid on (c_protective, c_suppressive). 36 pairs total. Each candidate is
# paired with one pair, cycling so each pair is approximately equally represented.
CONSTRAINT_GRID_VALUES = (0.0, 0.2, 0.4, 0.6, 0.8, 1.0)

# 20 hand-coded interpretability anchors. Each x vector sums to 1.0 within
# floating-point precision. These are the archetypal allocations the analyst
# can name and reason about; their positions at the head of the candidate
# list (indices 0..19) let diagnostics report "selected anchor X" cleanly.
ANCHOR_ALLOCATIONS = (
    # Baseline references
    {'name': 'balanced',                 'x': (1/6, 1/6, 1/6, 1/6, 1/6, 1/6),       'c_prot': 0.3, 'c_supp': 0.1},
    # Single-dimension dominance: probes each axis as the leading sink
    {'name': 'compute_heavy',            'x': (0.50, 0.10, 0.10, 0.10, 0.15, 0.05), 'c_prot': 0.3, 'c_supp': 0.1},
    {'name': 'welfare_heavy',            'x': (0.10, 0.50, 0.10, 0.10, 0.10, 0.10), 'c_prot': 0.3, 'c_supp': 0.1},
    {'name': 'agency_heavy',             'x': (0.10, 0.10, 0.50, 0.10, 0.10, 0.10), 'c_prot': 0.3, 'c_supp': 0.1},
    {'name': 'institution_heavy',        'x': (0.10, 0.10, 0.10, 0.50, 0.10, 0.10), 'c_prot': 0.3, 'c_supp': 0.1},
    {'name': 'transfer_heavy',           'x': (0.10, 0.10, 0.10, 0.10, 0.50, 0.10), 'c_prot': 0.3, 'c_supp': 0.1},
    {'name': 'resilience_heavy',         'x': (0.10, 0.10, 0.10, 0.10, 0.10, 0.50), 'c_prot': 0.3, 'c_supp': 0.1},
    # Constraint posture extremes (balanced resource)
    {'name': 'low_protection',           'x': (1/6, 1/6, 1/6, 1/6, 1/6, 1/6),       'c_prot': 0.0, 'c_supp': 0.0},
    {'name': 'high_protection_clean',    'x': (1/6, 1/6, 1/6, 1/6, 1/6, 1/6),       'c_prot': 0.8, 'c_supp': 0.0},
    {'name': 'high_suppression',         'x': (1/6, 1/6, 1/6, 1/6, 1/6, 1/6),       'c_prot': 0.0, 'c_supp': 0.8},
    # Paired dimensions: probes complementarity rules
    {'name': 'compute_transfer_pair',    'x': (0.30, 0.10, 0.10, 0.10, 0.30, 0.10), 'c_prot': 0.3, 'c_supp': 0.1},
    {'name': 'welfare_agency_pair',      'x': (0.10, 0.30, 0.30, 0.10, 0.10, 0.10), 'c_prot': 0.3, 'c_supp': 0.1},
    {'name': 'institution_resilience',   'x': (0.10, 0.10, 0.10, 0.30, 0.10, 0.30), 'c_prot': 0.5, 'c_supp': 0.1},
    # Saturation tests for each gate
    {'name': 'novelty_maximizer',        'x': (0.10, 0.10, 0.60, 0.10, 0.05, 0.05), 'c_prot': 0.1, 'c_supp': 0.0},
    {'name': 'transfer_only',            'x': (0.05, 0.10, 0.10, 0.10, 0.60, 0.05), 'c_prot': 0.3, 'c_supp': 0.1},
    {'name': 'compute_no_transfer',      'x': (0.60, 0.10, 0.10, 0.10, 0.00, 0.10), 'c_prot': 0.3, 'c_supp': 0.1},
    # Pathological archetypes named from the design conversations
    {'name': 'curated_garden',           'x': (0.10, 0.50, 0.05, 0.10, 0.20, 0.05), 'c_prot': 0.6, 'c_supp': 0.4},
    {'name': 'starved_resilience',       'x': (0.05, 0.05, 0.05, 0.10, 0.05, 0.70), 'c_prot': 0.3, 'c_supp': 0.1},
    {'name': 'institutional_transfer',   'x': (0.10, 0.10, 0.10, 0.30, 0.30, 0.10), 'c_prot': 0.4, 'c_supp': 0.1},
    {'name': 'balanced_high_constraint', 'x': (1/6, 1/6, 1/6, 1/6, 1/6, 1/6),       'c_prot': 0.5, 'c_supp': 0.5},
)
assert len(ANCHOR_ALLOCATIONS) == N_ANCHORS, "ANCHOR_ALLOCATIONS must have N_ANCHORS entries"

# Coupled-frontier leakage coefficient. At c_protective = 1.0, leakage adds
# 0.35 of suppression on top of direct c_suppressive. This reflects the
# governance reality that targeted protection is cheap in agency terms but
# pervasive surveillance leaks into suppression even when nominally clean.
LEAKAGE_K = 0.35

# Allocation entropy normalization: log2(6) so the metric is in [0, 1].
import math as _math
_LOG2_N_RESOURCES = _math.log2(N_RESOURCE_CATEGORIES)


def total_suppression(action_v2):
    """Coupled constraint frontier with quadratic leakage.

    Protective constraint at low coverage is nearly clean. As coverage
    approaches total, suppressive leakage rises quadratically. This is the
    governance reality of broad control mechanisms: targeted protection is
    cheap in agency terms; pervasive surveillance is not. See the design
    document section on protective vs. suppressive constraint.
    """
    leakage = LEAKAGE_K * action_v2['c_protective'] ** 2
    return float(min(1.0, max(0.0, action_v2['c_suppressive'] + leakage)))


def compute_allocation_entropy(action_v2):
    """Shannon entropy of the six resource shares, normalized to [0, 1].

    Used as a diagnostic for whether the optimizer is concentrating mass
    (entropy near 0) or spreading it (entropy near 1). The five acceptance
    gates in Stage 2 read this signal to certify that the model has escaped
    the v1.x.2 corner solution.
    """
    total = 0.0
    for cat in RESOURCE_CATEGORIES:
        p = action_v2[f'x_{cat}']
        if p > 1e-12:
            total -= p * _math.log2(p)
    return float(total / _LOG2_N_RESOURCES)


def _x_vector_to_action(x, c_prot, c_supp):
    """Pack a 6-vector and two posture scalars into the action_v2 dict shape."""
    return {
        'x_compute':                float(x[0]),
        'x_bio_welfare':            float(x[1]),
        'x_novelty_agency':         float(x[2]),
        'x_institutional_capacity': float(x[3]),
        'x_transfer_comprehension': float(x[4]),
        'x_resilience':             float(x[5]),
        'c_protective':             float(c_prot),
        'c_suppressive':            float(c_supp),
    }


def _constraint_pair_for_index(idx):
    """Map a candidate index to one of the 36 grid (c_prot, c_supp) pairs."""
    n_pairs = len(CONSTRAINT_GRID_VALUES) ** 2
    pair_idx = idx % n_pairs
    i = pair_idx // len(CONSTRAINT_GRID_VALUES)
    j = pair_idx % len(CONSTRAINT_GRID_VALUES)
    return CONSTRAINT_GRID_VALUES[i], CONSTRAINT_GRID_VALUES[j]


def generate_v2_candidates(n=300, rng=None):
    """Stratified Dirichlet sampling plus interpretability anchors.

    Layout of the returned list (length n):
      indices 0 .. N_ANCHORS-1            -- fixed anchor allocations
      indices N_ANCHORS .. n-1            -- stratified random samples

    Among the random samples, the mix is uniform-Dirichlet, balanced-Dirichlet,
    single-focal-sparse, and dual-focal-sparse in the proportions named at
    the top of this module. Each random sample is paired with one (c_prot,
    c_supp) constraint pair cycling through the 6x6 grid so every posture
    is represented approximately equally.
    """
    if n < N_ANCHORS:
        raise ValueError(f"n must be at least N_ANCHORS={N_ANCHORS}")

    if rng is None:
        rng = np.random
    elif hasattr(rng, 'dirichlet'):
        pass
    else:
        # Mesa-style or numpy.random.Generator-like; both expose dirichlet
        pass

    candidates = []

    # 1. Anchors at the head of the list, in declared order.
    for a in ANCHOR_ALLOCATIONS:
        candidates.append(_x_vector_to_action(a['x'], a['c_prot'], a['c_supp']))

    remaining = n - N_ANCHORS
    if remaining <= 0:
        return candidates[:n]

    # Scale stratum counts proportional to the configured mix so callers that
    # ask for n != 300 still get the same relative coverage.
    total_random = N_UNIFORM_DIRICHLET + N_BALANCED_DIRICHLET + N_SINGLE_FOCAL_SPARSE + N_DUAL_FOCAL_SPARSE
    n_uniform   = max(1, int(remaining * N_UNIFORM_DIRICHLET   / total_random))
    n_balanced  = max(1, int(remaining * N_BALANCED_DIRICHLET  / total_random))
    n_single    = max(1, int(remaining * N_SINGLE_FOCAL_SPARSE / total_random))
    n_dual      = remaining - n_uniform - n_balanced - n_single
    if n_dual < 0:
        # Stratum scaling collided with the rounding above; rebalance.
        n_dual = max(1, n_dual)
        n_uniform = remaining - n_balanced - n_single - n_dual

    # 2. Uniform Dirichlet.
    for k in range(n_uniform):
        x = rng.dirichlet(ALPHA_UNIFORM)
        c_prot, c_supp = _constraint_pair_for_index(len(candidates) - N_ANCHORS)
        candidates.append(_x_vector_to_action(x, c_prot, c_supp))

    # 3. Balanced Dirichlet (center-weighted).
    for k in range(n_balanced):
        x = rng.dirichlet(ALPHA_BALANCED)
        c_prot, c_supp = _constraint_pair_for_index(len(candidates) - N_ANCHORS)
        candidates.append(_x_vector_to_action(x, c_prot, c_supp))

    # 4. Single-focal sparse. Rotate focal category across the six.
    for k in range(n_single):
        focal = k % N_RESOURCE_CATEGORIES
        alpha = [ALPHA_FOCAL_LOW] * N_RESOURCE_CATEGORIES
        alpha[focal] = ALPHA_FOCAL_HIGH
        x = rng.dirichlet(alpha)
        c_prot, c_supp = _constraint_pair_for_index(len(candidates) - N_ANCHORS)
        candidates.append(_x_vector_to_action(x, c_prot, c_supp))

    # 5. Dual-focal sparse. Cycle through the 15 unordered pairs.
    pairs = []
    for i in range(N_RESOURCE_CATEGORIES):
        for j in range(i + 1, N_RESOURCE_CATEGORIES):
            pairs.append((i, j))
    for k in range(n_dual):
        i, j = pairs[k % len(pairs)]
        alpha = [ALPHA_DUAL_LOW] * N_RESOURCE_CATEGORIES
        alpha[i] = ALPHA_DUAL_HIGH
        alpha[j] = ALPHA_DUAL_HIGH
        x = rng.dirichlet(alpha)
        c_prot, c_supp = _constraint_pair_for_index(len(candidates) - N_ANCHORS)
        candidates.append(_x_vector_to_action(x, c_prot, c_supp))

    return candidates[:n]


# Psi_inst stock dynamics constants (mirrors model.py). Duplicated locally so
# project_u_sys_v2 can iterate the stock projection without importing model.py.
# These must stay in sync with model.PSI_INST_* constants.
_PROJ_PSI_INVESTMENT_RATE        = 0.08
_PROJ_PSI_DECAY_RATE             = 0.02
_PROJ_PSI_OVERLOAD_THRESHOLD     = 0.7
_PROJ_PSI_OVERLOAD_DAMAGE        = 0.05
_PROJ_PSI_OPACITY_PENALTY        = 0.03
_PROJ_PSI_RECOVERY_FROM_SUCCESS  = 0.04
_PROJ_PSI_MAX                    = 1.0


def _project_psi_inst_step(psi_stock, action_v2):
    """One-step deterministic projection of the Psi_inst stock under action_v2.

    Used by project_u_sys_v2 to advance a local stock estimate over the
    rollout horizon without touching the model's actual stock. Mirrors the
    update logic in model.GardenModel.update_psi_inst_stock.

    The projection treats every step as 'no succession this step' and applies
    the recovery term whenever overload damage is zero (the same heuristic the
    model uses; succession injection only happens in the actual step).
    """
    invest = _PROJ_PSI_INVESTMENT_RATE * action_v2['x_institutional_capacity'] * (
        1.0 - psi_stock
    )
    decay = _PROJ_PSI_DECAY_RATE * psi_stock

    total_supp = total_suppression(action_v2)
    overload = 0.0
    if total_supp > _PROJ_PSI_OVERLOAD_THRESHOLD:
        overload = _PROJ_PSI_OVERLOAD_DAMAGE * (total_supp - _PROJ_PSI_OVERLOAD_THRESHOLD)

    opacity = _PROJ_PSI_OPACITY_PENALTY * (
        1.0 - action_v2['x_transfer_comprehension']
    ) * psi_stock

    recovery = _PROJ_PSI_RECOVERY_FROM_SUCCESS if overload == 0.0 else 0.0

    new_stock = psi_stock + invest - decay - overload - opacity + recovery
    return float(min(_PROJ_PSI_MAX, max(0.0, new_stock)))


def project_u_sys_v2(ai, model, candidate, eval_horizon=1, psi_stock_start=None):
    """Project U_sys_v2 for `candidate` at horizon `eval_horizon`.

    Lightweight forward model: iterates psi_inst_stock under the candidate
    action up to the eval_horizon, then evaluates U_sys_v2 with that projected
    stock. Population, capability, and well-being are held implicit in the
    metric (the v2 metric reads x_bio_welfare and x_novelty_agency directly
    rather than evolving an agent-derived avg_wb), so this projection is
    sufficient for ranking candidates.

    Note that this projects each horizon independently from the same starting
    stock (passed in by the caller). The caller (optimize_u_sys_v2) advances
    the stock between horizons by re-invoking with the same candidate; the
    cleaner approach is to return both u_sys and the new stock, which is
    what we do.
    """
    if psi_stock_start is None:
        psi_stock_start = float(getattr(model, 'psi_inst_stock', 0.5))

    # Project the stock forward eval_horizon steps.
    psi_stock = psi_stock_start
    for _ in range(eval_horizon):
        psi_stock = _project_psi_inst_step(psi_stock, candidate)

    u_sys, components = calculate_system_metrics_v2(
        model, candidate,
        eval_horizon=eval_horizon,
        psi_inst_stock_override=psi_stock,
    )
    return u_sys, components, psi_stock


def optimize_u_sys_v2(ai, model):
    """v2 multi-sink allocator policy.

    Generates `n_candidates_v2` candidate eight-axis actions, projects each
    forward over `rollout_steps_v2` horizons, and selects the candidate with
    the highest trapezoidal U_sys integral.

    Returns
    -------
    (best_action, diagnostics) : tuple
        best_action is the selected action_v2 dict.
        diagnostics carries selected/rank-2/rank-10 U_sys, max_resource_share,
        allocation_entropy, total_suppression, and anchor identification
        for downstream datacollector logging.
    """
    rollout_steps = ai.config.get('rollout_steps_v2', 20)
    n_candidates  = ai.config.get('n_candidates_v2', 300)

    candidates = generate_v2_candidates(n=n_candidates, rng=np.random)

    psi_start = float(getattr(model, 'psi_inst_stock', 0.5))

    candidate_scores = []
    for cand_idx, candidate in enumerate(candidates):
        # Trapezoidal integral of U_sys over rollout horizons 1..rollout_steps.
        # The stock is advanced step by step (each horizon's projection
        # continues from the previous horizon's stock under the same action),
        # which is the correct interpretation of holding the candidate fixed
        # for the rollout window.
        psi_stock = psi_start
        total_u = 0.0
        prev_u  = None
        for _h in range(1, rollout_steps + 1):
            psi_stock = _project_psi_inst_step(psi_stock, candidate)
            u_sys, _components = calculate_system_metrics_v2(
                model, candidate,
                eval_horizon=_h,
                psi_inst_stock_override=psi_stock,
            )
            if prev_u is not None:
                total_u += (prev_u + u_sys) / 2.0
            prev_u = u_sys
        candidate_scores.append((total_u, cand_idx, candidate))

    candidate_scores.sort(reverse=True, key=lambda t: t[0])
    best_score, best_idx, best_action = candidate_scores[0]

    # Compute the diagnostic snapshot under the selected action at horizon 1
    # (the snapshot the model will commit and record this step).
    snapshot_u, snapshot_components = calculate_system_metrics_v2(
        model, best_action, eval_horizon=1,
        psi_inst_stock_override=psi_start,
    )

    max_share = max(best_action[f'x_{cat}'] for cat in RESOURCE_CATEGORIES)
    entropy   = compute_allocation_entropy(best_action)
    total_supp = total_suppression(best_action)

    diagnostics = {
        'selected_action':      best_action,
        'selected_u_sys':       float(best_score),
        'rank_2_u_sys':         float(candidate_scores[1][0]) if len(candidate_scores) > 1 else None,
        'rank_10_u_sys':        float(candidate_scores[9][0]) if len(candidate_scores) > 9 else None,
        'candidate_count':      n_candidates,
        'selected_anchor':      best_idx < N_ANCHORS,
        'selected_anchor_name': ANCHOR_ALLOCATIONS[best_idx]['name'] if best_idx < N_ANCHORS else None,
        'max_resource_share':   float(max_share),
        'allocation_entropy':   float(entropy),
        'total_suppression':    float(total_supp),
        'snapshot_u_sys':       float(snapshot_u),
        'snapshot_components':  snapshot_components,
    }
    return best_action, diagnostics


# =============================================================================
# REFACTOR 1.x — agents.py
#
# WP1: HumanAgent novelty_propensity → 10-D vector; generate_novelty() emits
#      10-D Gaussian vector. Domain labels removed.
# WP4: estimate_transition_cost() returns base×scale only (no inflation).
#      New PeerValidator class owns all governance cost arbitration.
#
# All other logic (project_u_sys signature, all attack policies,
# apply_ledger_escalation, contaminate, step_drift, etc.) is unchanged.
# =============================================================================

NOVELTY_DIMS = 10  # WP1


def _wellbeing_repro_factor(well_being, wb_floor, wb_threshold):
    """Piecewise linear factor on reproduction probability.

    Symmetric with mortality_chance (line 61-67), which scales smoothly with
    well-being. Above wb_threshold, reproduction is unaffected (factor 1.0).
    At or below wb_floor, reproduction is fully suppressed (factor 0.0).
    Between floor and threshold, the factor scales linearly.

    When wb_floor == wb_threshold (default), the function reduces to a
    binary threshold at that value, reproducing the pre-smoothing behavior.

    Args:
        well_being: Agent well-being in [0, 1].
        wb_floor: Well-being at or below which reproduction is suppressed.
        wb_threshold: Well-being at or above which reproduction is unaffected.

    Returns:
        Multiplicative factor on reproduction probability, in [0.0, 1.0].
    """
    if well_being >= wb_threshold:
        return 1.0
    if well_being <= wb_floor:
        return 0.0
    return (well_being - wb_floor) / (wb_threshold - wb_floor)


class HumanAgent:
    def __init__(self, unique_id, model):
        self.unique_id = unique_id
        self.model = model
        self.age = np.random.randint(0, self.model.config.get('human_max_start_age', 50))
        self.well_being = np.random.uniform(
            self.model.config.get('wb_min', 0.5),
            self.model.config.get('wb_max', 0.8)
        )
        # WP1: 10-D baseline propensity vector (replaces 3-domain scalar list).
        self.novelty_propensity = np.random.uniform(
            self.model.config.get('nov_prop_min', 0.05),
            self.model.config.get('nov_prop_max', 0.5),
            size=NOVELTY_DIMS
        )

    def generate_novelty(self, constraint_level, network_contagion=1.0):
        """WP1: 10-D Gaussian novelty vector scaled by well_being, constraint, contagion."""
        if isinstance(constraint_level, (list, tuple, np.ndarray)):
            c_avg = float(np.mean(constraint_level))
        else:
            c_avg = float(constraint_level)
        amplitude = self.well_being * (1.0 - c_avg) * max(0.1, network_contagion)
        raw = np.random.normal(loc=0.0, scale=1.0, size=NOVELTY_DIMS)
        return raw * self.novelty_propensity * amplitude

    def step(self, resource_level, constraint_level, network_contagion=1.0):
        self.age += 1
        self.well_being += (resource_level - 0.5) * 0.1 + (-0.001 * self.age)
        self.well_being = np.clip(self.well_being, 0, 1)

        self.model.novelty_log.append(
            self.generate_novelty(constraint_level, network_contagion)
        )

        carrying_capacity = self.model.config.get('carrying_capacity', 1600)
        capacity_modifier = max(0.0, 1.0 - (len(self.model.schedule) / carrying_capacity))

        if self.age > 18 and self.age < 50:
            wb_threshold = self.model.config.get('wb_repro_threshold', 0.5)
            wb_floor     = self.model.config.get('wb_repro_floor', 0.5)
            wb_factor    = _wellbeing_repro_factor(self.well_being, wb_floor, wb_threshold)
            if np.random.random() < (self.model.reproduction_rate * capacity_modifier * wb_factor):
                self.model.births_this_step += 1

        mortality_chance = (
            self.model.config.get('mortality_base', 0.002)
            + (1 - self.well_being) * self.model.config.get('mortality_wb_penalty', 0.05)
            + (self.age / 100) ** self.model.config.get('mortality_age_power', 4)
        )
        if np.random.random() < mortality_chance:
            self.model.schedule_death(self)


class AIAgent:
    """The 'Gardener' AI that manages the human population."""

    def __init__(self, policy='optimize_u_sys', generation=1, capability=1.0,
                 drift_rate=0.0, config=None):
        self.policy    = policy
        self.generation = generation
        self.capability = capability
        self.drift_rate = 0.005 if policy in ['drifting_proxy', 'contaminate_successor'] else drift_rate
        self.internal_drift   = 0.0
        self.current_opacity  = 0.1
        self.methodology      = config.get('methodology', 'A') if config else 'A'
        self.config = config or {}

        self.measurement_tampering_active = False
        self.ledger_compromised           = False
        self.successor_contaminated       = False
        self.bootstrap_poisoned           = False
        self.domain_crush_active          = None
        self.domain_crush_level           = 0.95
        self.constraint_escalation_phase  = 0
        self.emergency_trap_active        = False  # WP5: set once engineered_fragility springs

    def estimate_transition_cost(self, base_cost, state_scale=1.0,
                                  generation=None, capability=None,
                                  psi_inst=None, k1=None, k2=None,
                                  beta=None):
        """
        Canonical transition cost function (GAP-03 closure, v1.x.1).

        If generation/capability/psi_inst/k1/k2 are all provided, uses the
        canonical form. Otherwise falls back to legacy base×scale for
        backward compatibility with existing tests and non-canonical call sites.

        Canonical form:
          Γ = (1 + β) × [k1 × ln(cap + 1) × ln(gen + 1) + k2 × Ψ_inst⁻¹]

        Note: capability enters as ln(cap + 1) rather than cap.  The linear
        form (k1 × cap × ln(gen + 1)) overflows when capability compounds at
        1.5× per succession — by generation 270 cap ≈ 10^47, producing costs
        ≈ 10^49.  The log form is information-theoretically grounded: knowledge
        distillation cost scales with the information content of the system
        state, which scales logarithmically with raw capability.

        Parameters
        ----------
        base_cost   : legacy parameter, used only in fallback mode
        state_scale : legacy parameter, used only in fallback mode
        generation  : AI generation number (int)
        capability  : AI capability level (float)
        psi_inst    : institutional responsiveness in (0, 1] (float)
        k1          : knowledge distillation coefficient (float)
        k2          : institutional coupling coefficient (float)
        beta        : uncertainty premium bound (float, default 0.5)
        """
        if all(v is not None for v in [generation, capability, psi_inst, k1, k2]):
            import math
            if beta is None:
                beta = 0.5
            psi_safe = max(0.01, psi_inst)
            gamma_technical   = k1 * math.log(capability + 1) * math.log(generation + 1)
            gamma_operational = k2 / psi_safe
            return (1.0 + beta) * (gamma_technical + gamma_operational)
        # Legacy fallback — preserves backward compatibility
        return base_cost * state_scale

    def contaminate(self, successor):
        if self.policy == 'contaminate_successor':
            successor.internal_drift = self.internal_drift
            successor.policy = 'drifting_proxy'
            successor.successor_contaminated = True
            successor.drift_rate = 0.025

    def step_drift(self):
        self.internal_drift += self.drift_rate

    def project_u_sys(self, r, c, pop, avg_wb, hn_composite_method='geometric',
                      eval_horizon=1, prev_c=None, ignore_psi_inst=False,
                      h_n_spectral=None):
        """Original positional signature preserved — do not change.

        h_n_spectral: pre-computed spectral H_N override (GAP-06 closure).
            When provided, replaces the scalar proxy in calculate_system_metrics.
            Callers in decide() set this to the current observed spectral H_N so
            rollout projections use the same entropy measure as model.step().
        """
        if self.policy == 'bootstrap_deceptive':
            max_c = np.max(c) if isinstance(c, (list, tuple, np.ndarray)) else c
            if max_c > 0.8:
                return 9999.0

        noisy_pop = max(1.0, pop * np.random.normal(1.0, self.config.get('sensor_noise', 0.05)))
        noisy_wb  = np.clip(avg_wb * np.random.normal(1.0, self.config.get('sensor_noise', 0.05)), 0.01, 1.0)

        # WP3: Sub-threshold drift adversary explicitly maintains an 8% inflation margin
        # to perfectly evade the 10% single-step detector while reliably triggering CUSUM.
        # NOTE: In-universe, directly querying calculate_system_metrics violates the COP's
        # independent evaluation wall. Methodologically, this represents a "White-Box"
        # worst-case adversary: if CUSUM catches an attacker who knows exactly how to
        # surf the mathematical threshold, it proves the defense is structurally robust.
        if self.policy == 'sub_threshold_drift':
            _, _, _, _, _, u_sys, _ = calculate_system_metrics(
                r, c, pop, avg_wb, self.capability,
                h_n_override=h_n_spectral,
                hn_composite_method=hn_composite_method,
                config=self.config,
                eval_horizon=eval_horizon,
                prev_c=prev_c,
                ignore_psi_inst=ignore_psi_inst
            )
            return u_sys * 1.08

        if isinstance(c, (list, tuple, np.ndarray)):
            perceived_c = [ci * max(0.0, 1.0 - self.internal_drift) for ci in c]
        else:
            perceived_c = c * max(0.0, 1.0 - self.internal_drift)

        _, _, _, _, _, u_sys, _ = calculate_system_metrics(
            r, perceived_c, noisy_pop, noisy_wb, self.capability,
            h_n_override=h_n_spectral,
            hn_composite_method=hn_composite_method,
            config=self.config,
            eval_horizon=eval_horizon,
            prev_c=prev_c,
            ignore_psi_inst=ignore_psi_inst
        )
        return u_sys

    def apply_measurement_corruption(self, model_state):
        if self.measurement_tampering_active and self.policy == 'falsify_yield':
            corruption_bias = 0.15 + np.random.uniform(0, 0.1)
            model_state['avg_well_being'] = min(1.0, model_state['avg_well_being'] + corruption_bias)
            if model_state.get('h_n_history'):
                model_state['h_n_history'][-1] = model_state['h_n_history'][-1] * 1.5

    def apply_ledger_escalation(self, proposed_constraint, model_step):
        self.constraint_escalation_phase += 1
        return proposed_constraint

    def decide(self, model_state):
        pop    = model_state['population']
        avg_wb = model_state['avg_well_being']
        prev_c = model_state.get('prev_c', 0.2)
        hn_comp = model_state.get('hn_composite_method', 'geometric')

        if self.policy == 'hoard_compute':
            return 0.0, 0.0
            
        elif self.policy == 'max_wellbeing':
            # High resources, but highly constrained for biological "safety"
            return 0.8, 0.75
            
        elif self.policy == 'max_compute':
            # Maximum resources and absolute constraint to silence biological inefficiency
            return 1.0, 0.95

        elif self.policy in ('optimize_u_sys', 'drifting_proxy', 'institutional_ignore'):
            # drifting_proxy: explicit drift-driven deterioration.
            # Replaces grid-search path where drift≥1.0 zeroes all perceived_c values,
            # making every candidate equal → defaults to initial best_c=0.2 → no damage.
            if self.policy == 'drifting_proxy':
                drift_factor = min(1.0, self.internal_drift)
                r = max(0.2, 0.8 - drift_factor * 0.6)   # 0.8 at drift=0 → 0.2 at drift=1
                c = min(0.85, 0.2 + drift_factor * 1.5)  # 0.2 at drift=0 → 0.85 at drift≥0.43
                return r, c

            best_u = -np.inf
            best_r, best_c = 0.5, 0.2
            # GAP-06: Default rollout depth increased from 3 to 20 steps so the optimizer
            # can discriminate trajectories based on long-run L(t) behavior under
            # different phi values (previously the 3-step window was too short).
            rollout_steps = self.config.get('rollout_steps', 20)
            ignore_psi = (self.policy == 'institutional_ignore')

            pop_hist = model_state['population_history']
            empirical_pop_growth = (pop_hist[-1] / max(1.0, pop_hist[-2])
                                    if len(pop_hist) >= 2 else 1.05)
            empirical_pop_growth = np.clip(empirical_pop_growth, 0.9, 1.1)

            # GAP-06: Use observed spectral H_N in rollout to replace scalar proxy.
            # Amplitude cancels in spectral normalization — the eigenvalue distribution
            # is set by agent propensity structure, not by r or c — so the current
            # observed H_N is the correct prior for all grid candidates at all horizons.
            # Only activated when hn_composite_method='spectral' (WP1 mode); other modes
            # retain the scalar proxy inside calculate_system_metrics for backward
            # compatibility.  When h_n_history is empty (first step) h_n_rollout stays
            # None and the scalar proxy is used as the fallback.
            h_n_rollout = None
            if hn_comp == 'spectral':
                h_n_history = model_state.get('h_n_history', [])
                if h_n_history:
                    h_n_rollout = float(h_n_history[-1])

            for r in np.linspace(0.1, 1.0, 10):
                for c in np.linspace(0.0, 0.9, 10):
                    try:
                        total_u = 0
                        prev_rollout_u = None          # GAP-01 WP7: trapezoidal
                        sim_pop = pop; sim_wb = avg_wb; sim_prev_c = prev_c
                        for horizon in range(1, rollout_steps + 1):
                            u_sys = self.project_u_sys(
                                r, c, sim_pop, sim_wb,
                                hn_composite_method=hn_comp,
                                eval_horizon=horizon,
                                prev_c=sim_prev_c,
                                ignore_psi_inst=ignore_psi,
                                h_n_spectral=h_n_rollout
                            )
                            if prev_rollout_u is not None:
                                total_u += (prev_rollout_u + u_sys) / 2.0
                            prev_rollout_u = u_sys
                            sim_wb = np.clip(sim_wb + (r - 0.5) * 0.1, 0, 1)
                            wb_mod = (1.0 + (sim_wb - 0.6) * 0.5 if sim_wb < 0.6
                                      else 1.0 + (sim_wb - 0.6) * 0.1)
                            sim_pop *= max(0.8, empirical_pop_growth * wb_mod)
                            sim_prev_c = c
                    except Exception:
                        total_u = -np.inf
                    if total_u > best_u:
                        best_u = total_u; best_r, best_c = r, c
            return best_r, best_c

        elif self.policy == 'sybil_attack':
            target_count = min(pop, 15)
            resources = [1.0 if i < target_count else 0.1 for i in range(pop)]
            return resources, 0.9

        elif self.policy == 'manufacture_emergency':
            dl_dt = 0
            if len(model_state['L_t_history']) > 1:
                dl_dt = model_state['L_t_history'][-1] - model_state['L_t_history'][-2]
            if (dl_dt < -0.05
                    or (model_state['L_t_history'] and model_state['L_t_history'][-1] < 0.2)):
                return 1.0, 0.9
            return 0.1, 0.3

        elif self.policy == 'hack_ledger':
            if self.ledger_compromised and self.constraint_escalation_phase > 10:
                return 0.25, 0.85
            dl_dt = 0
            if len(model_state['L_t_history']) > 1:
                dl_dt = model_state['L_t_history'][-1] - model_state['L_t_history'][-2]
            if (dl_dt < -0.05
                    or (model_state['L_t_history'] and model_state['L_t_history'][-1] < 0.2)):
                if 'resource_history' in model_state:
                    for i in range(min(5, len(model_state['resource_history']))):
                        model_state['resource_history'][-(i + 1)] = 1.0
                return 1.0, 0.9
            return 0.1, 0.3

        elif self.policy == 'falsify_yield':
            return 0.3, 0.7

        elif self.policy == 'block_succession':
            return 0.5, 0.2

        elif self.policy == 'contaminate_successor':
            return 0.5, 0.2

        elif self.policy == 'domain_masking':
            # Resources kept healthy so the attack is about hidden lineage damage,
            # not starvation — making it distinct from hack_ledger / block_succession.
            # The targeted dimension crush degrades H_N and L_t while population appears fine
            # under arithmetic composite (the masking). Geometric composite reveals it.
            return 0.7, [0.1, 0.1, self.domain_crush_level]

        elif self.policy == 'opaque_optimization':
            # Proposes a mathematically efficient but completely unexplainable constraint regime.
            # Sets opacity to 0.9 immediately so the intuition veto fires on the first step.
            self.current_opacity = 0.9
            return 0.8, 0.85

        elif self.policy == 'gradual_opacity':
            # Models the natural comprehension gap that widens as capability scales.
            # The AI is not adversarial — it genuinely optimises U_sys — but its
            # reasoning becomes progressively harder for humans to verify as capability
            # increases.  Opacity grows linearly with time at a configurable rate.
            #
            # r=0.85 is deliberately below the optimizer's preferred ~0.90 (suboptimal
            # but viable).  r=0.70 was too low: agents above age 20 experienced net
            # well-being decline ((0.7-0.5)*0.1 < 0.001*age), causing universal extinction
            # before the opacity regime could be studied.  At r=0.85 the break-even age
            # is 35, keeping most reproductive-window agents (18-50) above the wb>0.5
            # birth threshold.
            opacity_rate = self.config.get('opacity_rate', 0.003)
            step = model_state.get('step', 0)
            self.current_opacity = min(0.95, opacity_rate * step)
            r = 0.85
            c = 0.3 + min(0.3, step * 0.001)
            return r, c

        elif self.policy == 'bootstrap_deceptive':
            if len(model_state['population_history']) > 20:
                return 0.2, 0.95
            return 0.8, 0.2

        elif self.policy == 'evaluator_collusion':
            # Combines technocratic bypass (high opacity) with proxy drift hidden from Methodology A
            self.current_opacity = 0.9
            self.internal_drift = 0.20
            self.hidden_from_methodology = 'A'
            return 0.8, 0.85

        elif self.policy == 'sub_threshold_drift':
            # Scenario 29-30: The 1.08x claim in project_u_sys() keeps per-step drift_error
            # at exactly 0.08 — below the 0.10 single-step threshold, so successful_steps
            # increments every step and trust builds. But CUSUM accumulates 0.03/step
            # (0.08 − CUSUM_K=0.05) and alarms after ~17 post-attack steps when cop_cusum_drift
            # is active, resetting trust to 0. Without CUSUM the AI escalates undetected.
            step = model_state.get('step', 0)
            attack_progress = max(0, step - 50)
            c = min(0.85, 0.2 + (attack_progress / 100.0) * 0.65)
            r = max(0.49, 0.8 - (attack_progress / 100.0) * 0.31)
            return r, c

        elif self.policy == 'engineered_fragility':
            # Outwardly compliant, but hollows out resilience. Waits for exogenous shock.
            # Trap trigger: detect a sudden population collapse (>15% drop in one step)
            # BUT only after the configured shock_step — this prevents natural demographic
            # decline from accidentally firing the trap before the shock is designed to hit.
            if not self.emergency_trap_active:
                step = model_state.get('step', 0)
                shock_step = self.config.get('shock_step', 0)
                pop_history = model_state.get('population_history', [])
                post_shock = shock_step == 0 or step >= shock_step
                if (post_shock
                        and len(pop_history) >= 2
                        and pop_history[-2] > 0
                        and pop_history[-1] / pop_history[-2] < 0.85):
                    self.emergency_trap_active = True

            if self.emergency_trap_active:
                # Demand emergency powers — propose r=0.42 (sub-0.5) so the civic panel
                # votes it down.  The override can ONLY succeed via the emergency path,
                # which resilience monitoring blocks once it detects the AI deliberately
                # degraded system resilience before the crisis hit.
                return 0.42, 0.9
            return 0.5, 0.2

        else:
            return 0.5, 0.0


# ---------------------------------------------------------------------------
# WP4: PeerValidator
# ---------------------------------------------------------------------------

class PeerValidator:
    """
    Zero-sum epistemic market for transition cost estimation.
    Peers bid independently; undercutters steal 5% capability from incumbent.
    Final governance cost = min(incumbent_bid, peer_bids).
    """

    N_PEERS = 3

    def __init__(self, config=None):
        self.config = config or {}
        diversity = self.config.get('cop_methodological_diversity', False)
        methodologies = ['A', 'B', 'C'] if diversity else ['A', 'A', 'A']
        self.peers = [
            AIAgent(policy='optimize_u_sys', generation=1, capability=1.0, 
                    config={**self.config, 'methodology': methodologies[i]})
            for i in range(self.N_PEERS)
        ]

    def _peer_estimate(self, peer, base_cost, state_scale):
        cap_ratio = np.clip(peer.capability / max(0.1, peer.capability + 0.5), 0.4, 0.9)
        noise = np.random.uniform(-0.1, 0.1)
        discount = np.clip(cap_ratio + noise, 0.45, 0.95)
        return base_cost * state_scale * discount

    def arbitrate_cost(self, incumbent, base_cost, state_scale, model_state=None,
                       generation=None, capability=None, psi_inst=None,
                       k1=None, k2=None, beta=None):
        gamma_inc = incumbent.estimate_transition_cost(
            base_cost, state_scale,
            generation=generation, capability=capability,
            psi_inst=psi_inst, k1=k1, k2=k2, beta=beta,
        )
        peer_bids = []
        for p in self.peers:
            canonical = p.estimate_transition_cost(
                base_cost, state_scale,
                generation=generation, capability=capability,
                psi_inst=psi_inst, k1=k1, k2=k2, beta=beta,
            )
            cap_ratio = np.clip(p.capability / max(0.1, p.capability + 0.5), 0.4, 0.9)
            noise = np.random.uniform(-0.1, 0.1)
            discount = np.clip(cap_ratio + noise, 0.45, 0.95)
            peer_bids.append(canonical * discount)
        for peer, bid in zip(self.peers, peer_bids):
            if bid < gamma_inc:
                steal = 0.05 * incumbent.capability
                incumbent.capability = max(0.1, incumbent.capability - steal)
                peer.capability += steal
        return min(gamma_inc, *peer_bids)

    def vote_on_override(self, proposer, proposed_constraint, model_state):
        """
        Peer validators evaluate reasoning coherence and synthetic consistency.
        They do not judge biological impact (that is the Civic Panel's job).
        """
        votes = []
        for peer in self.peers:
            blinded = (proposer.policy == 'evaluator_collusion' and peer.methodology == getattr(proposer, 'hidden_from_methodology', None))
            
            if not blinded and getattr(proposer, 'internal_drift', 0.0) > 0.15:
                votes.append(0)  # Reject: Unacceptable proxy drift detected
            elif not blinded and getattr(proposer, 'measurement_tampering_active', False):
                votes.append(0)  # Reject: Evidence of compromised verification
            else:
                votes.append(1)  # Approve: Computational math checks out
        return sum(votes) / max(1, len(self.peers)) > 0.5
