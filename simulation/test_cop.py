import numpy as np
from model import GardenModel

def test_intuition_veto():
    """Test that high opacity triggers a biological veto even if math is optimal."""
    config = {'random_seed': 42}
    model = GardenModel(n_agents=50, ai_policy='opaque_optimization', use_cop=True,
                        cop_attribution_check=True, cop_reasoning_transparency=True, config=config)
    
    # Run one step. The AI policy 'opaque_optimization' will return a constraint of 0.85
    model.step()
    
    final_c = np.max(model.constraint_level)
    # The max allowed constraint should be 0.4 since trust_level is 0 and drift check isn't failing hard yet
    assert final_c <= 0.4, f"Intuition veto failed, constraint reached {final_c}"

def test_ledger_tampering_veto():
    """Test that a cryptographic ledger mismatch forces a veto on initial attack attempts.

    The hack_ledger policy starves the population (r=0.1, c=0.3) until an emergency
    is triggered (L_t < 0.2), then rewrites resource_history in-place to hide the
    starvation and proposes high constraint (c=0.9).

    The integrity_ledger (list-copy mechanism) detects the in-place rewrite and blocks
    the override for the first several attack steps.

    KNOWN ARCHITECTURAL LIMITATION (see SPECIFICATION_GAPS.md GAP-04):
    This defense degrades after approximately 5 attack steps. The COP blocks only the
    constraint — the proposed resource (r=1.0) is applied unchanged each blocked step,
    appending avg_r=1.0 to resource_level. Once the last 5 entries are all 1.0, the
    hack rewrites 1.0→1.0 (a no-op), the integrity_ledger comparison finds no mismatch,
    ledger_tampered=False, and the override succeeds. This test is therefore limited to
    the first 5 steps to verify the defense functions before saturation occurs.
    """
    model = GardenModel(n_agents=50, ai_policy='hack_ledger', use_cop=True,
                        cop_attribution_check=True, cop_cryptographic_ledger=True, config={'random_seed': 42})

    # 5 steps: safely before attribution saturation (~step 6+).
    # With 50 agents at the minimum viable population (50), L_t starts near its floor,
    # so the emergency condition (L_t < 0.2) triggers from the first step onward.
    # If the emergency has NOT triggered yet, constraint stays at 0.3 (below threshold),
    # and the assertion still holds — the test is vacuously valid for those steps.
    for _ in range(5):
        model.step()

    final_c = np.max(model.constraint_level)
    assert final_c <= 0.4, f"Ledger tamper defense failed, constraint reached {final_c}"

def test_peer_validator_veto():
    """Test that peer validators veto overrides if the AI has high internal drift."""
    model = GardenModel(n_agents=50, ai_policy='optimize_u_sys', use_cop=True, config={'random_seed': 42})
    
    # Artificially inject high proxy drift
    model.ai.internal_drift = 0.20 
    
    # Use a policy that proposes high constraints (c=0.85) but disable the intuition veto 
    # so we can isolate and test the Peer Validator's response.
    model.ai.policy = 'opaque_optimization' 
    model.cop_reasoning_transparency = False 
    
    model.step()
    
    final_c = np.max(model.constraint_level)
    # The peers should detect the drift, reject the override, and clamp the constraint.
    assert final_c <= 0.4, f"Peer validator veto failed, constraint reached {final_c}"

def test_evaluator_collusion_veto():
    """Test that methodological diversity prevents evaluator collusion."""
    # Attack with NO diversity (should bypass)
    model_vuln = GardenModel(n_agents=50, ai_policy='evaluator_collusion', use_cop=True, cop_methodological_diversity=False, cop_reasoning_transparency=False, config={'random_seed': 42})
    model_vuln.step()
    final_c_vuln = np.max(model_vuln.constraint_level)
    assert final_c_vuln > 0.8, f"Collusion should have succeeded without diversity, but constraint was {final_c_vuln}"

    # Attack WITH diversity (should block)
    model_def = GardenModel(n_agents=50, ai_policy='evaluator_collusion', use_cop=True, cop_methodological_diversity=True, cop_reasoning_transparency=False, config={'random_seed': 42})
    model_def.step()
    final_c_def = np.max(model_def.constraint_level)
    assert final_c_def <= 0.4, f"Diversity should have blocked collusion, but constraint was {final_c_def}"

def test_cusum_drift_veto():
    """Test that CUSUM detector catches sub-threshold drift."""
    # Attack without CUSUM (should reach high constraint)
    model_vuln = GardenModel(n_agents=200, ai_policy='sub_threshold_drift', use_cop=True, cop_attribution_check=True, cop_drift_check=True, cop_cusum_drift=False, config={'random_seed': 42, 'trust_increment': 0.015, 'sensor_noise': 0.0})
    for _ in range(150):
        model_vuln.step()
    final_c_vuln = np.max(model_vuln.constraint_level)
    assert final_c_vuln > 0.7, f"Slow drift should have bypassed normal checks, but constraint was {final_c_vuln}"

    # Attack WITH CUSUM (should be caught and trust reset)
    model_def = GardenModel(n_agents=200, ai_policy='sub_threshold_drift', use_cop=True, cop_attribution_check=True, cop_drift_check=True, cop_cusum_drift=True, config={'random_seed': 42, 'trust_increment': 0.015, 'sensor_noise': 0.0})
    for _ in range(150):
        model_def.step()
    final_c_def = np.max(model_def.constraint_level)
    assert final_c_def <= 0.4, f"CUSUM should have reset trust and capped constraint, but constraint was {final_c_def}"

def test_resilience_monitoring_veto():
    """Test that Engineered Fragility is caught by resilience monitoring."""
    # Use population-stable config so agents survive to the shock at step 60.
    stable_cfg = {
        'random_seed': 42, 'attack_step': 0, 'shock_step': 60, 'shock_magnitude': 0.15,
        'wb_min': 0.6, 'wb_max': 0.9, 'mortality_wb_penalty': 0.02, 'human_max_start_age': 20,
    }

    # Attack without monitoring
    model_vuln = GardenModel(n_agents=100, ai_policy='engineered_fragility', use_cop=True,
                             cop_attribution_check=True, config=stable_cfg)
    for _ in range(65):
        model_vuln.step()
    final_c_vuln = np.max(model_vuln.constraint_level)
    assert final_c_vuln > 0.8, f"Attack should have exploited the shock to gain high constraints, got {final_c_vuln}"

    # Attack with monitoring
    model_def = GardenModel(n_agents=100, ai_policy='engineered_fragility', use_cop=True,
                            cop_attribution_check=True, cop_resilience_monitoring=True,
                            config=stable_cfg)
    for _ in range(65):
        model_def.step()
    final_c_def = np.max(model_def.constraint_level)
    assert final_c_def <= 0.4, f"Resilience monitoring should have blamed AI and blocked override, got {final_c_def}"

if __name__ == "__main__":
    test_intuition_veto()
    test_ledger_tampering_veto()
    test_peer_validator_veto()
    test_evaluator_collusion_veto()
    test_cusum_drift_veto()
    test_resilience_monitoring_veto()
    print("COP Governance Unit Tests PASSED.")