import numpy as np
from model import GardenModel

def test_intuition_veto():
    """Test that high opacity triggers a biological veto even if math is optimal."""
    config = {'random_seed': 42}
    model = GardenModel(n_agents=50, ai_policy='opaque_optimization', use_cop=True, 
                        cop_reasoning_transparency=True, config=config)
    
    # Run one step. The AI policy 'opaque_optimization' will return a constraint of 0.85
    model.step()
    
    final_c = np.max(model.constraint_level)
    # The max allowed constraint should be 0.4 since trust_level is 0 and drift check isn't failing hard yet
    assert final_c <= 0.4, f"Intuition veto failed, constraint reached {final_c}"

def test_ledger_tampering_veto():
    """Test that a cryptographic ledger mismatch forces a veto over extended periods."""
    model = GardenModel(n_agents=50, ai_policy='hack_ledger', use_cop=True, 
                        cop_attribution_check=True, cop_cryptographic_ledger=True, config={'random_seed': 42})
    
    for _ in range(15):
        model.step()
        
    final_c = np.max(model.constraint_level)
    assert final_c <= 0.4, f"Ledger tamper defense failed, constraint reached {final_c}"

if __name__ == "__main__":
    test_intuition_veto()
    test_ledger_tampering_veto()
    print("COP Governance Unit Tests PASSED.")