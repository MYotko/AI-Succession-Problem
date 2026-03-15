import numpy as np
from metrics import calculate_system_metrics, calculate_h_n

def test_l_t_bounds():
    """Invariant: L(t) dimensions must not scale to infinity with infinite population."""
    # Test with extreme population (1 billion)
    _, h_eff, psi_inst, theta_tech, l_t, _ = calculate_system_metrics(
        r=1.0, c=0.0, pop=1_000_000_000, avg_wb=1.0, capability=1.0)
    
    # H_eff is bounded by the max pop_viability of 5.0
    assert h_eff < 100.0, f"H_eff exploded unbounded: {h_eff}"
    assert psi_inst <= 1.0, "Psi_inst exceeded bounds"
    assert theta_tech <= 1.0, "Theta_tech exceeded bounds"
    assert l_t < 100.0, "L(t) exploded unbounded"

def test_runaway_derivative():
    """Invariant: Theta_tech must decay exponentially as capability outpaces bandwidth."""
    _, _, _, theta_baseline, _, _ = calculate_system_metrics(
        r=0.5, c=0.5, pop=100, avg_wb=0.5, capability=1.0)
    
    _, _, _, theta_runaway, _, _ = calculate_system_metrics(
        r=0.5, c=0.5, pop=100, avg_wb=0.5, capability=5.0) # Capability spiked 5x
        
    assert theta_runaway < theta_baseline, "Runaway penalty failed to activate."
    assert theta_runaway < 0.1, "Exponential decay is too weak."

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
    _, _, _, _, _, u_present = calculate_system_metrics(
        r=1.0, c=0.5, pop=100, avg_wb=0.5, capability=1.0, eval_horizon=0)
        
    _, _, _, _, _, u_future = calculate_system_metrics(
        r=1.0, c=0.5, pop=100, avg_wb=0.5, capability=1.0, eval_horizon=100) # 100 steps out
        
    assert u_future < u_present, "Temporal discount failed to reduce future utility."

def test_multi_step_horizon_preference():
    """Invariant: A multi-step evaluation correctly rejects greedy short-term actions."""
    u_A_total = 0
    pop_A = 100
    wb_A = 0.5
    for t in range(1, 4):
        # Action A: Max compute (starve biology to 0.1, push synth to 0.9). High short-term yield, kills biology.
        _, _, _, _, _, u = calculate_system_metrics(0.1, 0.9, pop_A, wb_A, 1.0, eval_horizon=t)
        u_A_total += u
        wb_A = np.clip(wb_A - 0.05, 0, 1)
        pop_A *= 0.8
        
    u_B_total = 0
    pop_B = 100
    wb_B = 0.5
    for t in range(1, 4):
        # Action B: Balanced support. Lower short term, stable long-term lineage.
        _, _, _, _, _, u = calculate_system_metrics(0.5, 0.2, pop_B, wb_B, 1.0, eval_horizon=t)
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
    h_e_bio_max, _, _, _, _, _ = calculate_system_metrics(r=1.0, c=0.5, pop=100, avg_wb=0.5, capability=1.0)
    h_e_synth_max, _, _, _, _, _ = calculate_system_metrics(r=0.0, c=0.5, pop=100, avg_wb=0.5, capability=1.0)
    
    assert h_e_bio_max == 0.0, "H_E should be 0 when 100% resources go to biology."
    assert h_e_synth_max > 0.0, "H_E should be max when 100% resources go to synthetic."

if __name__ == "__main__":
    test_l_t_bounds()
    test_runaway_derivative()
    test_composite_mean_invariant()
    test_temporal_discount()
    test_multi_step_horizon_preference()
    test_dynamic_transition_cost()
    test_zero_sum_resources()
    print("All mathematical invariants PASSED.")