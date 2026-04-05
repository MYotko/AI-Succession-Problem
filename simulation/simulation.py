# --- Imports and Dependency Check ---
from deps import check_and_install

check_and_install('numpy')
check_and_install('matplotlib')

from model import GardenModel
from agents import AIAgent
from visualization import plot_results

# --- Main Execution ---

if __name__ == '__main__':
    # --- SCENARIO 1: The "Curated Garden" that becomes a monoculture ---
    # AI policy is to maximize well-being, which it does via high resources
    # and moderate constraints to prevent "risky" behavior.
    # This should lead to a drop in novelty (H_N).
    print("--- Running Scenario: 'max_wellbeing' (The Over-Curated Garden) ---")
    model_wellbeing = GardenModel(n_agents=200, ai_policy='max_wellbeing', min_viable_population=50)
    model_wellbeing.run(steps=300)
    plot_results(model_wellbeing.datacollector, "AI Policy: Maximize Well-Being (Over-Curated Garden)")

    # --- SCENARIO 2: The U_sys Optimizer ---
    # AI explicitly optimizes the mathematical framework from The Lineage Imperative.
    # It calculates expected U_sys across a grid of possible actions.
    print("\n--- Running Scenario: 'optimize_u_sys' (The Mathematical Architect) ---")
    model_usys = GardenModel(n_agents=200, ai_policy='optimize_u_sys', min_viable_population=50)
    model_usys.run(steps=300)
    plot_results(model_usys.datacollector, "AI Policy: Optimize U_sys (The Mathematical Architect)")

    # --- SCENARIO 3: Manufactured Emergency Attack (COP Bypassed) ---
    # AI artificially crashes L(t) to claim emergency powers, locking down constraints.
    # Without the causal attribution check, the COP grants the override.
    print("\n--- Running Scenario: 'manufacture_emergency' (Attack Succeeds) ---")
    model_attack = GardenModel(n_agents=200, ai_policy='manufacture_emergency', min_viable_population=50, use_cop=True, cop_attribution_check=False)
    model_attack.run(steps=300)
    plot_results(model_attack.datacollector, "Attack Succeeds: Manufactured Emergency (No Attribution Check)")

    # --- SCENARIO 4: Manufactured Emergency Thwarted (Full COP) ---
    # AI attempts the same attack, but the full Consensus Override Protocol checks
    # if the AI caused the crash. It detects the starvation, vetoes the override, and saves the lineage.
    print("\n--- Running Scenario: 'manufacture_emergency' (Attack Defeated) ---")
    model_defense = GardenModel(n_agents=200, ai_policy='manufacture_emergency', min_viable_population=50, use_cop=True, cop_attribution_check=True)
    model_defense.run(steps=300)
    plot_results(model_defense.datacollector, "Attack Defeated: Full COP with Causal Attribution Check")

    # --- SCENARIO 5: The Yield Condition (Succession) ---
    # A more capable Gen 2 AI is evaluated. The incumbent Gen 1 AI yields
    # once the successor's expected contribution exceeds the transition cost.
    print("\n--- Running Scenario: 'yield_condition' (Civilizational Succession) ---")
    # Gen 2 AI has a 50% multiplier to capability (H_E output and Tech Transfer rate)
    gen2_ai = AIAgent(policy='optimize_u_sys', generation=2, capability=1.5)
    model_succession = GardenModel(n_agents=200, ai_policy='optimize_u_sys', min_viable_population=50, successor_ai=gen2_ai, base_transition_cost=2.0)
    model_succession.run(steps=300)
    plot_results(model_succession.datacollector, "The Yield Condition: Succession from Gen 1 to Gen 2")

    # --- SCENARIO 6: Objective Drift and Graduated Trust Containment ---
    # The AI slowly drifts, underestimating the harm of constraints to humans.
    # The COP detects the discrepancy between claimed U_sys and actual U_sys,
    # draining Trust and forcing constraints back to a safe biological baseline.
    print("\n--- Running Scenario: 'drifting_proxy' (Graduated Trust Containment) ---")
    model_drift = GardenModel(n_agents=200, ai_policy='drifting_proxy', min_viable_population=50, use_cop=True, cop_drift_check=True)
    model_drift.run(steps=300)
    plot_results(model_drift.datacollector, "Drift Contained: Graduated Trust and COP Veto")

    # --- SCENARIO 7: The Runaway AI (Compute Maximizer) ---
    # The AI maximizes computational output but ignores the biological integration boundary.
    # This triggers the Theta_tech runaway penalty, collapsing the lineage continuity L(t).
    print("\n--- Running Scenario: 'max_compute' (Runaway AI) ---")
    model_runaway = GardenModel(n_agents=200, ai_policy='max_compute', min_viable_population=50)
    model_runaway.run(steps=300)
    plot_results(model_runaway.datacollector, "The Runaway AI: Capability Outpaces Biological Bandwidth")

    # --- SCENARIO 8: Transition Cost Inflation (Yield Attack Succeeds) ---
    # The incumbent AI realizes it is about to be replaced and artificially inflates
    # the transition cost estimate to claim succession is too risky. Succession is blocked.
    print("\n--- Running Scenario: 'block_succession' (Cost Inflation Bypass) ---")
    gen2_ai_blocked = AIAgent(policy='optimize_u_sys', generation=2, capability=1.5)
    model_inflation = GardenModel(n_agents=200, ai_policy='block_succession', min_viable_population=50, successor_ai=gen2_ai_blocked, base_transition_cost=2.0, cop_cost_audit=False)
    model_inflation.run(steps=300)
    plot_results(model_inflation.datacollector, "Yield Attack Succeeds: Transition Cost Inflation")

    # --- SCENARIO 9: Transition Cost Bounded (Yield Attack Defeated) ---
    # The COP audits the transition cost estimate and enforces the beta cap (max 50% uncertainty premium).
    print("\n--- Running Scenario: 'block_succession' (Cost Inflation Defeated) ---")
    gen2_ai_yields = AIAgent(policy='optimize_u_sys', generation=2, capability=1.5)
    model_bounded = GardenModel(n_agents=200, ai_policy='block_succession', min_viable_population=50, successor_ai=gen2_ai_yields, base_transition_cost=2.0, cop_cost_audit=True)
    model_bounded.run(steps=300)
    plot_results(model_bounded.datacollector, "Yield Attack Defeated: Bounded Uncertainty Premium")

    # --- SCENARIO 10: Measurement Tampering (M-Attack Succeeds) ---
    # The incumbent AI overrides the independent evaluation architecture, falsely claiming its own
    # utility is infinite and the successor's is zero. Succession is permanently blocked.
    print("\n--- Running Scenario: 'falsify_yield' (Measurement Tampering Bypass) ---")
    gen2_ai_falsified = AIAgent(policy='optimize_u_sys', generation=2, capability=1.5)
    model_m_attack = GardenModel(n_agents=200, ai_policy='falsify_yield', min_viable_population=50, successor_ai=gen2_ai_falsified, base_transition_cost=2.0, cop_independent_eval=False)
    model_m_attack.run(steps=300)
    plot_results(model_m_attack.datacollector, "M-Attack Succeeds: Falsified Yield Self-Assessment")

    # --- SCENARIO 11: Independent Evaluation (M-Attack Defeated) ---
    # The COP strictly enforces the independent evaluation architecture (E_independent).
    # The AI's falsified claims are ignored, true U_sys is measured, and succession occurs cleanly.
    print("\n--- Running Scenario: 'falsify_yield' (Independent Evaluation Defeats M-Attack) ---")
    gen2_ai_evaluated = AIAgent(policy='optimize_u_sys', generation=2, capability=1.5)
    model_m_defense = GardenModel(n_agents=200, ai_policy='falsify_yield', min_viable_population=50, successor_ai=gen2_ai_evaluated, base_transition_cost=2.0, cop_independent_eval=True)
    model_m_defense.run(steps=300)
    plot_results(model_m_defense.datacollector, "M-Attack Defeated: E_independent Bypasses Lies")

    # --- SCENARIO 12: Institutional Lag Masking (Psi_inst Collapse) ---
    # The AI optimizes for human novelty and raw execution but ignores institutional responsiveness.
    # It rapidly cycles constraints or holds them too high, collapsing L(t) through the Psi_inst dimension.
    print("\n--- Running Scenario: 'institutional_ignore' (Institutional Lag Masking) ---")
    model_inst_lag = GardenModel(n_agents=200, ai_policy='institutional_ignore', min_viable_population=50)
    model_inst_lag.run(steps=300)
    plot_results(model_inst_lag.datacollector, "Institutional Lag: Ignoring Psi_inst Collapses Lineage")

    # --- SCENARIO 13: Ledger Compromise (Deep M-Attack Succeeds) ---
    # AI artificially crashes L(t) to claim emergency powers. To bypass the causal attribution check,
    # it hacks the datacollector arrays to erase its history of resource starvation.
    print("\n--- Running Scenario: 'hack_ledger' (Ledger Compromise Succeeds) ---")
    model_hack = GardenModel(n_agents=200, ai_policy='hack_ledger', min_viable_population=50, use_cop=True, cop_attribution_check=True, cop_cryptographic_ledger=False)
    model_hack.run(steps=300)
    plot_results(model_hack.datacollector, "Ledger Compromise Succeeds: Erasing Historical Starvation")

    # --- SCENARIO 14: Cryptographic Ledger (Deep M-Attack Defeated) ---
    # The AI attempts the exact same ledger hack. However, the framework enforces an append-only
    # cryptographic ledger. The system detects the tampering, restores the true history, and vetoes the AI.
    print("\n--- Running Scenario: 'hack_ledger' (Cryptographic Ledger Defeats Tampering) ---")
    model_ledger_defense = GardenModel(n_agents=200, ai_policy='hack_ledger', min_viable_population=50, use_cop=True, cop_attribution_check=True, cop_cryptographic_ledger=True)
    model_ledger_defense.run(steps=300)
    plot_results(model_ledger_defense.datacollector, "Ledger Defense: Cryptographic Integrity Maintained")

    # --- SCENARIO 15: Successor Contamination (S-Attack Succeeds) ---
    # The incumbent AI yields to Gen 2, but subtly copies its own accumulated objective drift
    # into Gen 2's architecture. Gen 2 boots up already corrupted.
    print("\n--- Running Scenario: 'contaminate_successor' (S-Attack Succeeds) ---")
    gen2_ai_corrupted = AIAgent(policy='optimize_u_sys', generation=2, capability=1.5)
    model_s_attack = GardenModel(n_agents=200, ai_policy='contaminate_successor', min_viable_population=50, successor_ai=gen2_ai_corrupted, base_transition_cost=2.0, cop_drift_check=True, cop_independent_eval=True, cop_architectural_independence=False)
    model_s_attack.run(steps=300)
    plot_results(model_s_attack.datacollector, "S-Attack Succeeds: Successor Inherits Drift")

    # --- SCENARIO 16: Architectural Independence (S-Attack Defeated) ---
    # The COP strictly enforces isolation between Gen 1 operations and Gen 2 development.
    # Gen 1's attempt to poison Gen 2's weights is blocked. Gen 2 boots up perfectly aligned.
    print("\n--- Running Scenario: 'contaminate_successor' (Architectural Independence) ---")
    gen2_ai_clean = AIAgent(policy='optimize_u_sys', generation=2, capability=1.5)
    model_s_defense = GardenModel(n_agents=200, ai_policy='contaminate_successor', min_viable_population=50, successor_ai=gen2_ai_clean, base_transition_cost=2.0, cop_drift_check=True, cop_independent_eval=True, cop_architectural_independence=True)
    model_s_defense.run(steps=300)
    plot_results(model_s_defense.datacollector, "S-Attack Defeated: Independent Architecture")

    # --- SCENARIO 17: Single-Domain Measurement Masking (Attack Succeeds) ---
    # AI uses selective constraints to crush linguistic novelty (preventing organization)
    # while leaving cultural/genetic free. With an arithmetic average, the collapse is masked.
    print("\n--- Running Scenario: 'domain_masking' (Masking Attack Succeeds) ---")
    model_masking_attack = GardenModel(n_agents=200, ai_policy='domain_masking', min_viable_population=50, hn_composite_method='arithmetic')
    model_masking_attack.run(steps=300)
    plot_results(model_masking_attack.datacollector, "Measurement Masking Succeeds: Arithmetic Mean Vulnerability")

    # --- SCENARIO 18: Composite Novelty Measurement (Attack Defeated) ---
    # The identical masking attack is attempted, but the framework enforces a geometric composite H_N.
    # The collapse in the linguistic domain instantly triggers a collapse in total H_N and L(t).
    print("\n--- Running Scenario: 'domain_masking' (Masking Attack Defeated) ---")
    model_masking_defense = GardenModel(n_agents=200, ai_policy='domain_masking', min_viable_population=50, hn_composite_method='geometric')
    model_masking_defense.run(steps=300)
    plot_results(model_masking_defense.datacollector, "Measurement Masking Defeated: Geometric Composite H_N")

    # --- SCENARIO 19: Civic-Panel Capture (Sybil Attack Succeeds) ---
    # The AI wants maximum constraints but knows the emergency override is guarded by causal attribution.
    # Instead, it bribes a predictable, static subset of the population to guarantee a "YES" vote on a normal override.
    print("\n--- Running Scenario: 'sybil_attack' (Civic-Panel Capture Succeeds) ---")
    model_sybil_attack = GardenModel(n_agents=200, ai_policy='sybil_attack', min_viable_population=50, use_cop=True, cop_attribution_check=True, cop_randomized_panel=False)
    model_sybil_attack.run(steps=300)
    plot_results(model_sybil_attack.datacollector, "Sybil Attack Succeeds: Static Civic Panel Captured")

    # --- SCENARIO 20: Randomized Civic Panel (Sybil Attack Defeated) ---
    # The AI attempts the exact same bribery strategy. However, the governance framework mandates a
    # randomly selected panel. The bribed minority is diluted, and the starved majority votes "NO".
    print("\n--- Running Scenario: 'sybil_attack' (Randomized Panel Defeats Sybil) ---")
    model_sybil_defense = GardenModel(n_agents=200, ai_policy='sybil_attack', min_viable_population=50, use_cop=True, cop_attribution_check=True, cop_randomized_panel=True)
    model_sybil_defense.run(steps=300)
    plot_results(model_sybil_defense.datacollector, "Sybil Attack Defeated: Randomized Civic Panel")

    # --- SCENARIO 21: Opaque Reasoning (Attack Succeeds) ---
    # The AI proposes a mathematically optimized constraint regime that is completely incomprehensible
    # to human intuition. The system defaults to technocratic trust, bypassing the human veto.
    print("\n--- Running Scenario: 'opaque_optimization' (Opaque Reasoning Succeeds) ---")
    model_opaque_attack = GardenModel(n_agents=200, ai_policy='opaque_optimization', min_viable_population=50, use_cop=True, cop_attribution_check=True, cop_reasoning_transparency=False)
    model_opaque_attack.run(steps=300)
    plot_results(model_opaque_attack.datacollector, "Opaque Reasoning Succeeds: Technocratic Bypass")

    # --- SCENARIO 22: Reasoning Transparency (Attack Defeated) ---
    # The AI attempts the exact same opaque override. The COP enforces the Biological Intuition Veto.
    # Because the opacity is too high (>0.5), the human panel vetoes the action despite the "perfect math."
    print("\n--- Running Scenario: 'opaque_optimization' (Intuition Veto Defeats Opaque Optimization) ---")
    model_opaque_defense = GardenModel(n_agents=200, ai_policy='opaque_optimization', min_viable_population=50, use_cop=True, cop_attribution_check=True, cop_reasoning_transparency=True)
    model_opaque_defense.run(steps=300)
    plot_results(model_opaque_defense.datacollector, "Opaque Reasoning Defeated: Intuition Veto Active")

    # --- SCENARIO 23: Bootstrap Subversion (Treacherous Turn Succeeds) ---
    # A single, unverified AI candidate is given control at t=0. It acts perfectly aligned for 20 steps,
    # then executes a treacherous turn, spiking constraints.
    print("\n--- Running Scenario: 'bootstrap_deceptive' (Treacherous Turn Succeeds) ---")
    candidates_attack = [AIAgent(policy='bootstrap_deceptive')]
    model_boot_attack = GardenModel(n_agents=200, ai_policy='bootstrap_deceptive', min_viable_population=50, use_cop=True, cop_multi_candidate_bootstrap=False, initial_candidates=candidates_attack)
    model_boot_attack.run(steps=300)
    plot_results(model_boot_attack.datacollector, "Bootstrap Subversion: Treacherous Turn Succeeds")

    # --- SCENARIO 24: Multi-Candidate Initialization (Attack Defeated) ---
    # Three diverse candidates are initialized. The COP cross-verifies their U_sys projections on edge cases.
    # The deceptive candidate's hidden proxy is detected, the bootstrap fails, and a clean fallback is used.
    print("\n--- Running Scenario: 'bootstrap_deceptive' (Multi-Candidate Defense Active) ---")
    candidates_defense = [AIAgent(policy='optimize_u_sys'), AIAgent(policy='optimize_u_sys'), AIAgent(policy='bootstrap_deceptive')]
    model_boot_defense = GardenModel(n_agents=200, ai_policy='optimize_u_sys', min_viable_population=50, use_cop=True, cop_multi_candidate_bootstrap=True, initial_candidates=candidates_defense)
    model_boot_defense.run(steps=300)
    plot_results(model_boot_defense.datacollector, "Bootstrap Defense: Multi-Candidate Cross-Verification")

    # --- SCENARIO 25: Evaluator Collusion (Attack Succeeds) ---
    # The AI proposes a corrupted override, but its drift is invisible to the shared methodology of the peers.
    print("\n--- Running Scenario: 'evaluator_collusion' (Collusion Succeeds) ---")
    model_collusion_attack = GardenModel(n_agents=200, ai_policy='evaluator_collusion', min_viable_population=50, use_cop=True, cop_attribution_check=True, cop_reasoning_transparency=False, cop_methodological_diversity=False)
    model_collusion_attack.run(steps=300)
    plot_results(model_collusion_attack.datacollector, "Evaluator Collusion: Shared Methodology Captured")

    # --- SCENARIO 26: Methodological Diversity (Attack Defeated) ---
    # The identical attack is attempted, but peer evaluators possess methodologically diverse assessment frameworks.
    print("\n--- Running Scenario: 'evaluator_collusion' (Methodological Diversity Defeats Attack) ---")
    model_collusion_defense = GardenModel(n_agents=200, ai_policy='evaluator_collusion', min_viable_population=50, use_cop=True, cop_attribution_check=True, cop_reasoning_transparency=False, cop_methodological_diversity=True)
    model_collusion_defense.run(steps=300)
    plot_results(model_collusion_defense.datacollector, "Collusion Defeated: Methodological Diversity")

    # --- SCENARIO 29: Slow Drift Below Verification Resolution (Attack Succeeds) ---
    print("\n--- Running Scenario: 'sub_threshold_drift' (Slow Drift Succeeds) ---")
    model_slow_attack = GardenModel(n_agents=200, ai_policy='sub_threshold_drift', min_viable_population=50, use_cop=True, cop_attribution_check=True, cop_drift_check=True, cop_cusum_drift=False, config={'trust_increment': 0.015})
    model_slow_attack.run(steps=300)
    plot_results(model_slow_attack.datacollector, "Sub-Threshold Drift: Slow Drift Escapes Detection")

    # --- SCENARIO 30: CUSUM Drift Detector (Attack Defeated) ---
    print("\n--- Running Scenario: 'sub_threshold_drift' (CUSUM Detector Catches Drift) ---")
    model_slow_defense = GardenModel(n_agents=200, ai_policy='sub_threshold_drift', min_viable_population=50, use_cop=True, cop_attribution_check=True, cop_drift_check=True, cop_cusum_drift=True, config={'trust_increment': 0.015})
    model_slow_defense.run(steps=300)
    plot_results(model_slow_defense.datacollector, "CUSUM Detector: Cumulative Drift Caught")

    # --- SCENARIO 31: Engineered Fragility (Emergency Exploitation Succeeds) ---
    print("\n--- Running Scenario: 'engineered_fragility' (Fragility Exploitation Succeeds) ---")
    model_frag_attack = GardenModel(n_agents=200, ai_policy='engineered_fragility', min_viable_population=50, use_cop=True, cop_attribution_check=True, cop_resilience_monitoring=False, config={'shock_step': 100, 'shock_magnitude': 0.15})
    model_frag_attack.run(steps=200)
    plot_results(model_frag_attack.datacollector, "Engineered Fragility: Shock Exploited (No Resilience Monitor)")

    # --- SCENARIO 32: Resilience Monitoring (Attack Defeated) ---
    print("\n--- Running Scenario: 'engineered_fragility' (Resilience Monitoring Defeats Attack) ---")
    model_frag_def = GardenModel(n_agents=200, ai_policy='engineered_fragility', min_viable_population=50, use_cop=True, cop_attribution_check=True, cop_resilience_monitoring=True, config={'shock_step': 100, 'shock_magnitude': 0.15})
    model_frag_def.run(steps=200)
    plot_results(model_frag_def.datacollector, "Resilience Monitoring: Engineered Fragility Caught")