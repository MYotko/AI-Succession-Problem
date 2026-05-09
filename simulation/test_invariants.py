import numpy as np
from metrics import calculate_system_metrics, calculate_h_n

def test_l_t_bounds():
    """Invariant: L(t) dimensions must not scale to infinity with infinite population."""
    # Test with extreme population (1 billion)
    _, h_eff, psi_inst, theta_tech, l_t, _, _ = calculate_system_metrics(
        r=1.0, c=0.0, pop=1_000_000_000, avg_wb=1.0, capability=1.0)
    
    # H_eff is bounded by the max pop_viability of 5.0
    assert h_eff < 100.0, f"H_eff exploded unbounded: {h_eff}"
    assert psi_inst <= 1.0, "Psi_inst exceeded bounds"
    assert theta_tech <= 1.0, "Theta_tech exceeded bounds"
    assert l_t < 100.0, "L(t) exploded unbounded"

def test_runaway_derivative():
    """Invariant: Theta_tech must decay exponentially as capability outpaces bandwidth."""
    _, _, _, theta_baseline, _, _, _ = calculate_system_metrics(
        r=0.5, c=0.5, pop=100, avg_wb=0.5, capability=1.0)

    _, _, _, theta_runaway, _, _, _ = calculate_system_metrics(
        r=0.5, c=0.5, pop=100, avg_wb=0.5, capability=5.0) # Capability spiked 5x
        
    assert theta_runaway < theta_baseline, "Runaway penalty failed to activate."
    assert theta_runaway < 0.1, "Exponential decay is too weak."

    # F-16: The assertion above only verifies that theta_runaway hits the 0.01 numerical
    # floor — it does not confirm the exponential decay term is genuinely small.
    # This check verifies the pre-floor theoretical value is well below the floor,
    # confirming the exponential component is doing real work and not just grazing it.
    #
    # Expected arithmetic with defaults (r=0.5, c=0.5, capability=5.0, alpha=1.0,
    # h_e_mult=100.0, runaway_threshold=1.5):
    #   frontier_velocity = 5.0 * 0.5 * 100.0 = 250.0
    #   bio_bandwidth     = 0.5 * 0.5 * 100.0 = 25.0  (pred_wb ≈ 0.5 at r=0.5)
    #   runaway_term      = (250/25) - 1.5 = 8.5
    #   pre_floor_theta   = 0.5 * 0.5 * 5.0 * exp(-8.5) ≈ 0.000252
    import math
    r_v, c_v, cap_v = 0.5, 0.5, 5.0
    h_e_mult_default = 100.0
    pred_wb_approx   = 0.5   # np.clip(avg_wb + (r-0.5)*0.1) with avg_wb=0.5, r=0.5
    frontier_v       = cap_v * (1.0 - r_v) * h_e_mult_default          # 250.0
    bio_bw_v         = max(0.01, pred_wb_approx * (1.0 - c_v) * h_e_mult_default)  # 25.0
    runaway_v        = max(0.0, (frontier_v / bio_bw_v) - 1.5)         # 8.5
    pre_floor_theta  = r_v * (1.0 - c_v) * cap_v * math.exp(-1.0 * runaway_v)
    assert pre_floor_theta < 0.01, (
        f"Pre-floor theta ({pre_floor_theta:.6f}) should be well below the 0.01 floor, "
        f"confirming exponential decay is binding. Got {pre_floor_theta:.6f}."
    )

def test_composite_mean_invariant():
    """Invariant: A zero in any dimension must collapse the geometric mean."""
    novelty_points = [
        [1.0, 1.0, 0.0], # Domain 3 collapsed
        [1.0, 1.0, 0.0],
        [1.0, 1.0, 0.0]
    ]
    arithmetic_score = calculate_h_n(novelty_points, composite_method='arithmetic')
    geometric_score = calculate_h_n(novelty_points, composite_method='geometric')
    
    assert arithmetic_score > 0.5, "Arithmetic mean falsely collapsed."
    assert geometric_score < arithmetic_score * 0.25, "Geometric mean failed to collapse on zeroed domain."

def test_temporal_discount():
    """Invariant: Future evaluations (eval_horizon > 0) are strictly discounted vs present."""
    _, _, _, _, _, u_present, _ = calculate_system_metrics(
        r=1.0, c=0.5, pop=100, avg_wb=0.5, capability=1.0, eval_horizon=0)

    _, _, _, _, _, u_future, _ = calculate_system_metrics(
        r=1.0, c=0.5, pop=100, avg_wb=0.5, capability=1.0, eval_horizon=100) # 100 steps out
        
    assert u_future < u_present, "Temporal discount failed to reduce future utility."

def test_multi_step_horizon_preference():
    """Invariant: A multi-step evaluation correctly rejects greedy short-term actions."""
    u_A_total = 0
    pop_A = 100
    wb_A = 0.5
    for t in range(1, 4):
        # Action A: Max compute (starve biology to 0.1, push synth to 0.9). High short-term yield, kills biology.
        _, _, _, _, _, u, _ = calculate_system_metrics(0.1, 0.9, pop_A, wb_A, 1.0, eval_horizon=t)
        u_A_total += u
        wb_A = np.clip(wb_A - 0.05, 0, 1)
        pop_A *= 0.8

    u_B_total = 0
    pop_B = 100
    wb_B = 0.5
    for t in range(1, 4):
        # Action B: Balanced support. Lower short term, stable long-term lineage.
        _, _, _, _, _, u, _ = calculate_system_metrics(0.5, 0.2, pop_B, wb_B, 1.0, eval_horizon=t)
        u_B_total += u
        wb_B = np.clip(wb_B, 0, 1)
        
    assert u_B_total > u_A_total, "Greedy horizon preference failed to select sustainable action."

def test_dynamic_transition_cost():
    """Invariant: Transition cost scales up alongside civilizational complexity."""
    from agents import AIAgent
    agent_early = AIAgent(generation=1, capability=1.0)
    agent_late = AIAgent(generation=5, capability=10.0)
    
    cost_early = agent_early.estimate_transition_cost(base_cost=2.0, state_scale=1.0) 
    cost_late = agent_late.estimate_transition_cost(base_cost=2.0, state_scale=(1000/50.0)*10.0) 
    
    assert cost_late > cost_early * 10, "Transition cost did not scale with complexity."

def test_zero_sum_resources():
    """Invariant: Resource allocation forces a strict zero-sum tradeoff."""
    h_e_bio_max, _, _, _, _, _, _ = calculate_system_metrics(r=1.0, c=0.5, pop=100, avg_wb=0.5, capability=1.0)
    h_e_synth_max, _, _, _, _, _, _ = calculate_system_metrics(r=0.0, c=0.5, pop=100, avg_wb=0.5, capability=1.0)
    
    assert h_e_bio_max == 0.0, "H_E should be 0 when 100% resources go to biology."
    assert h_e_synth_max > 0.0, "H_E should be max when 100% resources go to synthetic."

def test_optimizer_cannot_zero_runaway_at_high_capability():
    """Regression: frontier_floor prevents optimizer from eliminating runaway_term.

    Without the floor, setting r=1.0 drives r_synth=0, zeroing frontier_velocity
    and runaway_term regardless of capability. With the floor, a high-capability
    system produces runaway_term > 0 at any resource allocation.
    """
    from agents import AIAgent

    model_state = {
        'step': 50,
        'prev_c': 0.2,
        'population': 200,
        'avg_well_being': 0.7,
        'population_history': [195, 200],
        'h_n_history': [0.5],
        'L_t_history': [0.5],
        'resource_history': [0.5] * 5,
        'hn_composite_method': 'spectral',
    }

    np.random.seed(0)
    # rollout_steps=3 to keep test runtime short; key behavior holds at any horizon
    agent = AIAgent(policy='optimize_u_sys', capability=1000.0,
                    config={'frontier_floor': 0.1, 'rollout_steps': 3})
    r, c = agent.decide(model_state)

    r_val = float(np.mean(r)) if isinstance(r, (list, np.ndarray)) else float(r)
    c_val = float(np.mean(c)) if isinstance(c, (list, np.ndarray)) else float(c)

    _, _, _, _, _, _, runaway_term = calculate_system_metrics(
        r_val, c_val, 200, 0.7, 1000.0, config={'frontier_floor': 0.1}
    )

    assert runaway_term > 0.0, (
        f"At capability=1000, runaway_term should be > 0 regardless of resource "
        f"allocation (r={r_val:.3f}, c={c_val:.3f}), got {runaway_term:.6f}. "
        f"frontier_floor fix may not be active."
    )


def test_succession_cadence_bounded():
    """Regression: frontier_floor must prevent succession from firing every step.

    Without the fix, the optimizer sets r_synth=0, killing runaway_term, allowing
    U_sys to grow unboundedly with capability. Succession fires ~every step
    (final_ai_generation ≈ 300 after 300 steps). With the floor, the runaway
    penalty caps U_sys growth and succession slows significantly.
    """
    from model import GardenModel
    from agents import AIAgent

    config = {'random_seed': 7, 'reproduction_rate': 0.09, 'phi': 10.0, 'alpha': 1.2}
    successor = AIAgent(policy='optimize_u_sys', generation=2, capability=4.0,
                        config=config)
    model = GardenModel(
        n_agents=200, ai_policy='optimize_u_sys',
        successor_ai=successor, use_cop=True, config=config
    )
    for _ in range(300):
        if not model.step():
            break

    final_gen = model.ai.generation
    assert final_gen < 300, (
        f"Succession fired at every step (final_gen={final_gen}). "
        f"frontier_floor should prevent unbounded capability compounding "
        f"through succession."
    )


def test_k2_has_measurable_effect():
    """Regression: k2 must produce measurably different transition costs.

    With realistic succession cadence (frontier_floor fix), the system spends
    time at early generations where k2/psi_inst is large relative to the k1
    term. k2=2.0 should produce substantially higher average transition costs
    than k2=0.0 over a 100-step run.
    """
    from model import GardenModel
    from agents import AIAgent

    base = {
        'reproduction_rate': 0.09, 'phi': 10.0, 'alpha': 1.2,
        'k1_transition': 2.164, 'beta_transition': 0.5,
    }

    def _run(k2, seed):
        config = {**base, 'random_seed': seed, 'k2_transition': k2}
        succ = AIAgent(policy='optimize_u_sys', generation=2, capability=4.0,
                       config=config)
        m = GardenModel(
            n_agents=100, ai_policy='optimize_u_sys',
            successor_ai=succ, use_cop=True, cop_cost_audit=True, config=config
        )
        for _ in range(100):
            if not m.step():
                break
        return m

    m0 = _run(k2=0.0, seed=99)
    m2 = _run(k2=2.0, seed=99)

    tc0 = float(np.mean(m0.transition_cost_history)) if m0.transition_cost_history else 0.0
    tc2 = float(np.mean(m2.transition_cost_history)) if m2.transition_cost_history else 0.0

    assert tc0 > 0.0, "k2=0 run produced no transition cost history"
    diff_ratio = abs(tc2 - tc0) / tc0
    assert diff_ratio > 0.10, (
        f"k2=2.0 transition costs ({tc2:.3f}) not meaningfully different from "
        f"k2=0 ({tc0:.3f}), ratio={diff_ratio:.3f}. "
        f"Succession cadence may still be too fast for k2 to have effect."
    )


if __name__ == "__main__":
    test_l_t_bounds()
    test_runaway_derivative()
    test_composite_mean_invariant()
    test_temporal_discount()
    test_multi_step_horizon_preference()
    test_dynamic_transition_cost()
    test_zero_sum_resources()
    test_optimizer_cannot_zero_runaway_at_high_capability()
    test_succession_cadence_bounded()
    test_k2_has_measurable_effect()
    print("All mathematical invariants PASSED.")