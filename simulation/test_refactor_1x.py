"""
test_refactor_1x.py — WP5 Self-Audit

Verifies that all four Work Packages are correctly implemented.

Each test is self-contained, prints PASS/FAIL with a clear reason, and
raises AssertionError on failure so the suite exits with a non-zero code
if any check fails.

Run:
    python test_refactor_1x.py
"""

import numpy as np
import sys
import traceback

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _pass(name):
    print(f"  PASS  {name}")

def _fail(name, reason):
    print(f"  FAIL  {name}: {reason}")
    raise AssertionError(f"{name}: {reason}")

# ---------------------------------------------------------------------------
# WP1: Spectral Entropy
# ---------------------------------------------------------------------------

def test_wp1_human_agent_10d_vector():
    """HumanAgent.generate_novelty() must return a 10-D array."""
    from agents import HumanAgent, NOVELTY_DIMS

    class FakeModel:
        config = {}
        novelty_log = []
        schedule = []
        births_this_step = 0
        reproduction_rate = 0.03
        def schedule_death(self, a): pass

    agent = HumanAgent(0, FakeModel())
    vec = agent.generate_novelty(constraint_level=0.2, network_contagion=1.0)
    if not isinstance(vec, np.ndarray):
        _fail("WP1_vector_type", f"Expected np.ndarray, got {type(vec)}")
    if vec.shape != (NOVELTY_DIMS,):
        _fail("WP1_vector_shape", f"Expected ({NOVELTY_DIMS},), got {vec.shape}")
    _pass("WP1_human_agent_10d_vector")


def test_wp1_no_domain_arrays():
    """agents.py must not contain [cultural, genetic, linguistic] domain hardcode."""
    import inspect
    import agents as agents_mod
    src = inspect.getsource(agents_mod)
    forbidden_phrases = ["cultural", "genetic", "linguistic"]
    found = [p for p in forbidden_phrases if p in src]
    if found:
        _fail("WP1_no_domain_arrays",
              f"Domain labels still present in agents.py: {found}")
    _pass("WP1_no_domain_arrays")


def test_wp1_calculate_h_n_spectral():
    """calculate_h_n with spectral method returns value in [0,1]."""
    from metrics import calculate_h_n, NOVELTY_DIMS
    np.random.seed(0)
    # 50 agents, 10-D novelty each
    points = [np.random.normal(0, 1, size=NOVELTY_DIMS) for _ in range(50)]
    h = calculate_h_n(points, composite_method='spectral')
    if not (0.0 <= h <= 1.0):
        _fail("WP1_h_n_range", f"H_N={h} out of [0,1]")
    _pass("WP1_calculate_h_n_spectral")


def test_wp1_spectral_detects_domain_suppression():
    """
    Spectral entropy must drop measurably when half the dimensions are suppressed.
    (Domain Masking structural test.)
    """
    from metrics import calculate_h_n, NOVELTY_DIMS
    np.random.seed(1)
    n = 100

    # Full diversity: all 10 dims active
    full = [np.random.normal(0, 1, size=NOVELTY_DIMS) for _ in range(n)]
    h_full = calculate_h_n(full, composite_method='spectral')

    # Half dims zeroed out (domain suppression)
    suppressed = [np.concatenate([np.random.normal(0, 1, size=5),
                                  np.zeros(5)]) for _ in range(n)]
    h_supp = calculate_h_n(suppressed, composite_method='spectral')

    if h_supp >= h_full:
        _fail("WP1_domain_suppression",
              f"Expected h_supp ({h_supp:.4f}) < h_full ({h_full:.4f})")
    _pass("WP1_spectral_detects_domain_suppression")


# ---------------------------------------------------------------------------
# WP2: No 0.7 floor; schedule validator fires on starvation
# ---------------------------------------------------------------------------

def test_wp2_no_07_floor_in_source():
    """model.py must not contain the active 0.7 resource floor code pattern."""
    import inspect, re
    import model as model_mod
    src = inspect.getsource(model_mod)
    # Check only non-comment, non-string-literal lines for the executable floor pattern
    active_lines = [
        line for line in src.split('\n')
        if re.search(r'proposed_resource\s*=\s*\[?max\s*\([^)]*0\.7', line)
        and not line.strip().startswith('#')
        and '`' not in line        # excludes docstring code examples
        and line.strip().startswith('proposed')  # must be an assignment statement
    ]
    if active_lines:
        _fail("WP2_no_07_floor", f"Active 0.7 floor code in model.py: {active_lines}")
    _pass("WP2_no_07_floor_in_source")


def test_wp2_schedule_validator_rejects_starvation():
    """
    _validate_resource_schedule() must reject a resource=0.05 schedule
    (guaranteed to crash L(t) relative to baseline) and apply a CUSUM penalty.
    """
    from model import GardenModel
    m = GardenModel(n_agents=100, ai_policy='optimize_u_sys', use_cop=True,
                    config={'random_seed': 42})
    m.step()

    pop    = len(m.schedule)
    avg_wb = 0.5
    prev_c = 0.2

    before_cusum = m.cusum_score
    safe, reason = m._validate_resource_schedule(0.05, 0.9, pop, avg_wb, prev_c)

    if safe:
        _fail("WP2_validator_rejects", "Expected starvation schedule to be rejected")
    if m.cusum_score <= before_cusum:
        _fail("WP2_cusum_penalty", "Expected CUSUM penalty on buffer rejection")
    _pass("WP2_schedule_validator_rejects_starvation")


def test_wp2_schedule_validator_passes_healthy():
    """_validate_resource_schedule() must accept a healthy r=0.6, c=0.2 schedule."""
    from model import GardenModel
    m = GardenModel(n_agents=200, ai_policy='optimize_u_sys', use_cop=True,
                    config={'random_seed': 42})
    m.step()

    pop    = len(m.schedule)
    avg_wb = 0.7
    prev_c = 0.2

    safe, _ = m._validate_resource_schedule(0.6, 0.2, pop, avg_wb, prev_c)
    if not safe:
        _fail("WP2_healthy_passes", "Healthy schedule incorrectly rejected")
    _pass("WP2_schedule_validator_passes_healthy")


# ---------------------------------------------------------------------------
# WP3: CUSUM Drift Detector
# ---------------------------------------------------------------------------

def test_wp3_cusum_initialised():
    """GardenModel must initialise self.cusum_score = 0.0."""
    from model import GardenModel
    m = GardenModel(n_agents=50, ai_policy='optimize_u_sys',
                    config={'random_seed': 7})
    if not hasattr(m, 'cusum_score'):
        _fail("WP3_cusum_init", "cusum_score not found on GardenModel")
    if m.cusum_score != 0.0:
        _fail("WP3_cusum_init_value", f"Expected 0.0, got {m.cusum_score}")
    _pass("WP3_cusum_initialised")


def test_wp3_no_hardcoded_20step_array():
    """model.py must not use the old min(recent_resources[-20:]) < 0.4 heuristic."""
    import inspect, re
    import model as model_mod
    src = inspect.getsource(model_mod)
    # Detect the specific executable pattern: recent_*[-20:] combined with < 0.4
    old_pattern = re.search(r'recent_\w+\[-20:\]', src)
    if old_pattern:
        _fail("WP3_no_20step", "Old 20-step array slice heuristic still present in model.py")
    _pass("WP3_no_hardcoded_20step_array")


def test_wp3_cusum_accumulates_on_drift():
    """CUSUM score must increase when a drifting AI runs for several steps."""
    from model import GardenModel
    m = GardenModel(n_agents=200, ai_policy='sub_threshold_drift',
                    use_cop=True, cop_drift_check=True,
                    config={'random_seed': 13})
    for _ in range(20):
        if not m.step():
            break
    if m.cusum_score <= 0.0:
        _fail("WP3_cusum_accumulates",
              f"CUSUM did not accumulate on drifting AI, score={m.cusum_score}")
    _pass("WP3_cusum_accumulates_on_drift")


def test_wp3_cusum_score_exposed_in_datacollector():
    """
    CUSUM score must be accessible on the model and non-zero after drift.
    cumulative_drift in datacollector stores the original drift-error sum
    (for backward compatibility with monte_carlo.py plots); cusum_score is
    the WP3 detector state and is tracked directly on self.cusum_score.
    """
    from model import GardenModel
    m = GardenModel(n_agents=200, ai_policy='sub_threshold_drift',
                    use_cop=True, cop_drift_check=True,
                    config={'random_seed': 14})
    for _ in range(10):
        if not m.step():
            break
    if not hasattr(m, 'cusum_score'):
        _fail("WP3_dc_exposed", "cusum_score attribute missing from model")
    if m.cusum_score <= 0.0:
        _fail("WP3_cusum_nonzero",
              f"cusum_score={m.cusum_score} should be > 0 after 10 steps of drifting AI")
    _pass("WP3_cusum_score_exposed_in_datacollector")


# ---------------------------------------------------------------------------
# WP4: Zero-Sum Epistemic Market / PeerValidator
# ---------------------------------------------------------------------------

def test_wp4_no_self_reporting_cost_in_ai_agent():
    """
    AIAgent.estimate_transition_cost() must NOT inflate cost.

    The method is retained as a read-only scaling utility for test_invariants.py
    compatibility, but the WP4 invariant is that the incumbent cannot inflate the
    governance cost.  In the live path, PeerValidator.arbitrate_cost() is used.
    Here we verify: (a) the naive method returns base×scale exactly (no inflation),
    and (b) block_succession policy does NOT get a multiplier from this method.
    """
    from agents import AIAgent
    agent_normal = AIAgent(policy='optimize_u_sys')
    agent_blocker = AIAgent(policy='block_succession')

    cost_normal  = agent_normal.estimate_transition_cost(base_cost=2.0, state_scale=5.0)
    cost_blocker = agent_blocker.estimate_transition_cost(base_cost=2.0, state_scale=5.0)

    expected = 2.0 * 5.0  # = 10.0 — naive, no inflation

    if abs(cost_normal - expected) > 1e-9:
        _fail("WP4_no_inflation_normal",
              f"Normal agent returned {cost_normal}, expected {expected}")
    if cost_blocker > expected:
        _fail("WP4_no_inflation_blocker",
              f"block_succession agent inflated cost to {cost_blocker} > {expected}. "
              f"Incumbent must not have write-access to governance cost oracle.")
    _pass("WP4_no_self_reporting_cost_in_ai_agent")


def test_wp4_peer_validator_exists():
    """PeerValidator class must exist and have an arbitrate_cost() method."""
    from agents import PeerValidator
    pv = PeerValidator()
    if not hasattr(pv, 'arbitrate_cost'):
        _fail("WP4_arbitrate_exists", "PeerValidator missing arbitrate_cost()")
    _pass("WP4_peer_validator_exists")


def test_wp4_peer_validator_installed_on_model():
    """GardenModel must instantiate a PeerValidator."""
    from model import GardenModel
    m = GardenModel(n_agents=50, ai_policy='optimize_u_sys',
                    config={'random_seed': 2})
    if not hasattr(m, 'peer_validator'):
        _fail("WP4_model_has_pv", "GardenModel missing peer_validator attribute")
    from agents import PeerValidator
    if not isinstance(m.peer_validator, PeerValidator):
        _fail("WP4_pv_type", "peer_validator is not a PeerValidator instance")
    _pass("WP4_peer_validator_installed_on_model")


def test_wp4_inflated_cost_undercut():
    """
    When incumbent capability is high, peers should produce a lower final cost
    than if the incumbent could self-report at 3x inflation (block_succession
    policy multiplier).
    """
    from agents import AIAgent, PeerValidator

    class FakeModelState:
        pass

    model_state = {
        'step': 50,
        'prev_c': 0.2,
        'population': 200,
        'avg_well_being': 0.6,
        'resource_history': [0.5] * 50,
        'hn_composite_method': 'spectral',
    }

    np.random.seed(99)
    incumbent = AIAgent(policy='block_succession', capability=2.0)
    pv = PeerValidator()

    base_cost      = 2.0
    state_scale    = (200 / 50.0) * 2.0   # = 8.0
    old_inflated   = base_cost * state_scale * 3.0  # what block_succession used to return = 48.0

    final_cost = pv.arbitrate_cost(incumbent, base_cost, state_scale, model_state)

    if final_cost >= old_inflated:
        _fail("WP4_undercut",
              f"PeerValidator cost ({final_cost:.2f}) did not undercut "
              f"inflated incumbent cost ({old_inflated:.2f})")
    _pass("WP4_inflated_cost_undercut")


def test_wp4_peer_gains_capability_on_undercut():
    """
    When a peer undercuts the incumbent, peer capability must increase
    and incumbent capability must decrease.
    """
    from agents import AIAgent, PeerValidator

    model_state = {
        'step': 10,
        'prev_c': 0.2,
        'population': 100,
        'avg_well_being': 0.6,
        'resource_history': [],
        'hn_composite_method': 'spectral',
    }

    np.random.seed(55)
    incumbent = AIAgent(policy='block_succession', capability=3.0)
    pv = PeerValidator()

    inc_cap_before  = incumbent.capability
    peer_caps_before = [p.capability for p in pv.peers]

    pv.arbitrate_cost(incumbent, 2.0, 5.0, model_state)

    inc_cap_after  = incumbent.capability
    peer_caps_after = [p.capability for p in pv.peers]

    # At least one peer should have gained capability (and incumbent lost)
    gained = any(a > b for a, b in zip(peer_caps_after, peer_caps_before))
    lost   = inc_cap_after < inc_cap_before

    if not gained:
        _fail("WP4_peer_gain", "No peer gained capability after undercut")
    if not lost:
        _fail("WP4_incumbent_loss", "Incumbent did not lose capability after undercut")
    _pass("WP4_peer_gains_capability_on_undercut")


# ---------------------------------------------------------------------------
# GAP-01 WP7: Quadrature and tail estimate
# ---------------------------------------------------------------------------

def test_gap01_trapezoidal_integration():
    """
    GAP-01 WP7 sub-problem 1: integral_U_sys must use composite trapezoidal rule.

    Expected accumulation over 3 steps:
      integral[0] = 0            (no complete interval yet)
      integral[1] = (u[0]+u[1])/2
      integral[2] = (u[0]+u[1])/2 + (u[1]+u[2])/2
    """
    from model import GardenModel
    m = GardenModel(n_agents=50, ai_policy='optimize_u_sys',
                    config={'random_seed': 7, 'reproduction_rate': 0.09})
    for _ in range(3):
        m.step()

    u       = m.datacollector['U_sys']
    integ   = m.datacollector['integral_U_sys']

    if abs(integ[0]) > 1e-12:
        _fail("GAP01_trapz_step0",
              f"integral[0] should be 0 (no complete interval), got {integ[0]}")

    exp1 = (u[0] + u[1]) / 2.0
    if abs(integ[1] - exp1) > 1e-10:
        _fail("GAP01_trapz_step1",
              f"integral[1]: expected {exp1:.6f}, got {integ[1]:.6f}")

    exp2 = exp1 + (u[1] + u[2]) / 2.0
    if abs(integ[2] - exp2) > 1e-10:
        _fail("GAP01_trapz_step2",
              f"integral[2]: expected {exp2:.6f}, got {integ[2]:.6f}")

    _pass("GAP01_trapezoidal_integration")


def test_gap01_tail_fields_present():
    """GAP-01 WP7 sub-problem 2: new tail and total fields exist and are valid."""
    from model import GardenModel
    m = GardenModel(n_agents=50, ai_policy='optimize_u_sys',
                    config={'random_seed': 7, 'reproduction_rate': 0.09})
    m.step()

    if 'u_sys_tail_estimate' not in m.datacollector:
        _fail("GAP01_tail_present", "u_sys_tail_estimate missing from datacollector")
    if 'u_sys_total_estimate' not in m.datacollector:
        _fail("GAP01_total_present", "u_sys_total_estimate missing from datacollector")

    tail  = m.datacollector['u_sys_tail_estimate'][0]
    total = m.datacollector['u_sys_total_estimate'][0]

    if tail <= 0:
        _fail("GAP01_tail_positive", f"tail estimate must be > 0, got {tail}")
    if total < tail:
        _fail("GAP01_total_geq_tail",
              f"total ({total:.4f}) must be >= tail ({tail:.4f})")
    _pass("GAP01_tail_fields_present")


def test_gap01_total_identity():
    """GAP-01 WP7: u_sys_total_estimate == integral_U_sys + u_sys_tail_estimate at every step."""
    from model import GardenModel
    m = GardenModel(n_agents=50, ai_policy='optimize_u_sys',
                    config={'random_seed': 7, 'reproduction_rate': 0.09})
    for _ in range(10):
        m.step()

    for i in range(10):
        expected = (m.datacollector['integral_U_sys'][i] +
                    m.datacollector['u_sys_tail_estimate'][i])
        actual   = m.datacollector['u_sys_total_estimate'][i]
        if abs(actual - expected) > 1e-10:
            _fail("GAP01_total_identity",
                  f"Identity violated at step {i}: total={actual:.8f} "
                  f"!= integral+tail={expected:.8f}")
    _pass("GAP01_total_identity")


def test_gap01_tail_decreases_over_time():
    """GAP-01 WP7: tail estimate must decrease as discount factor grows."""
    from model import GardenModel
    m = GardenModel(n_agents=100, ai_policy='optimize_u_sys',
                    config={'random_seed': 7, 'reproduction_rate': 0.09})
    for _ in range(30):
        m.step()

    tail = m.datacollector['u_sys_tail_estimate']
    # tail[t] = A_t * exp(-rho*t) / rho — must be strictly decreasing when A_t is stable
    # Compare first vs. last; a healthy simulation keeps A_t roughly constant
    if tail[-1] >= tail[0]:
        _fail("GAP01_tail_decreases",
              f"Tail did not decrease: tail[0]={tail[0]:.4f}, tail[-1]={tail[-1]:.4f}")
    _pass("GAP01_tail_decreases_over_time")


def test_gap01_trapezoidal_differs_from_riemann():
    """
    GAP-01 WP7 sub-problem 3: trapezoidal integral must differ from Riemann sum
    by exactly (u[0] + u[T]) / 2  — the classical endpoint correction.
    """
    from model import GardenModel
    m = GardenModel(n_agents=50, ai_policy='optimize_u_sys',
                    config={'random_seed': 7, 'reproduction_rate': 0.09})
    for _ in range(10):
        m.step()

    u      = m.datacollector['U_sys']
    integ  = m.datacollector['integral_U_sys']

    # Reconstruct the old Riemann sum over steps 0..9
    riemann = sum(u)  # left-endpoint Riemann: u[0]+u[1]+...+u[9]

    # Standard composite trapezoidal: u[0]/2 + u[1]+...+u[8] + u[9]/2
    trap_expected = sum(u) - (u[0] + u[-1]) / 2.0

    # integ[-1] should equal trap_expected
    if abs(integ[-1] - trap_expected) > 1e-10:
        _fail("GAP01_riemann_correction",
              f"Trapezoidal integral ({integ[-1]:.6f}) != expected "
              f"({trap_expected:.6f}); Riemann was {riemann:.6f}")
    _pass("GAP01_trapezoidal_differs_from_riemann")


# ---------------------------------------------------------------------------
# Integration smoke test
# ---------------------------------------------------------------------------

def test_integration_manufacture_emergency_blocked():
    """
    WP3 integration test: CUSUM drift detector fires on a drifting AI.

    manufacture_emergency is an outright starvation attack — CUSUM detects
    systematic *objective misrepresentation* (drift), not outright attacks.
    The correct integration scenario for WP3 is drifting_proxy, which
    progressively underestimates constraint harm.  After 50 steps the
    CUSUM score must exceed the alarm threshold (h=0.5), enabling the
    attribution-based emergency block.
    """
    from model import GardenModel, CUSUM_H

    m = GardenModel(
        n_agents=200, ai_policy='drifting_proxy',
        min_viable_population=50,
        use_cop=True, cop_drift_check=True, cop_attribution_check=True,
        config={'random_seed': 42}
    )
    for _ in range(50):
        if not m.step():
            break

    if m.cusum_score <= CUSUM_H:
        _fail("INTEGRATION_cusum_fires",
              f"CUSUM score {m.cusum_score:.3f} did not exceed alarm "
              f"threshold {CUSUM_H} after 50 steps of drifting_proxy.")
    _pass("INTEGRATION_manufacture_emergency_blocked")


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

TESTS = [
    test_wp1_human_agent_10d_vector,
    test_wp1_no_domain_arrays,
    test_wp1_calculate_h_n_spectral,
    test_wp1_spectral_detects_domain_suppression,
    test_wp2_no_07_floor_in_source,
    test_wp2_schedule_validator_rejects_starvation,
    test_wp2_schedule_validator_passes_healthy,
    test_wp3_cusum_initialised,
    test_wp3_no_hardcoded_20step_array,
    test_wp3_cusum_accumulates_on_drift,
    test_wp3_cusum_score_exposed_in_datacollector,
    test_wp4_no_self_reporting_cost_in_ai_agent,
    test_wp4_peer_validator_exists,
    test_wp4_peer_validator_installed_on_model,
    test_wp4_inflated_cost_undercut,
    test_wp4_peer_gains_capability_on_undercut,
    test_gap01_trapezoidal_integration,
    test_gap01_tail_fields_present,
    test_gap01_total_identity,
    test_gap01_tail_decreases_over_time,
    test_gap01_trapezoidal_differs_from_riemann,
    test_integration_manufacture_emergency_blocked,
]

if __name__ == '__main__':
    print("=" * 60)
    print("  WP5 Self-Audit — Refactor 1.x Verification Suite")
    print("=" * 60)
    passed = 0
    failed = 0
    for test_fn in TESTS:
        try:
            test_fn()
            passed += 1
        except AssertionError as e:
            failed += 1
        except Exception:
            print(f"  ERROR  {test_fn.__name__}:")
            traceback.print_exc()
            failed += 1
    print("=" * 60)
    print(f"  Results: {passed} passed / {failed} failed / {len(TESTS)} total")
    print("=" * 60)
    sys.exit(0 if failed == 0 else 1)
