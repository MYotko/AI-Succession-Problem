# --- Imports and Dependency Check ---
from deps import check_and_install

check_and_install('numpy')
check_and_install('matplotlib')

import itertools
import csv
import numpy as np
import matplotlib.pyplot as plt
from model import GardenModel
from agents import AIAgent

def run_monte_carlo():
    # Define hyperparameter grid
    phi_values = [1.0, 5.0, 10.0, 20.0]        # Lineage override weights (How much the AI cares about L(t))
    alpha_values = [0.5, 1.0, 2.0]             # Runaway technology penalties (How hard frontier velocity is punished)
    repro_rates = [0.05, 0.08, 0.12]           # Biological resilience (Human baseline reproduction)

    results = []
    total_runs = len(phi_values) * len(alpha_values) * len(repro_rates)
    current_run = 0

    print(f"Starting Monte Carlo Execution: {total_runs} total permutations.")

    for phi, alpha, repro in itertools.product(phi_values, alpha_values, repro_rates):
        current_run += 1
        custom_config = {
            'phi': phi,
            'alpha': alpha,
            'reproduction_rate': repro,
            'mortality_base': 0.002,
            'random_seed': 1000 + current_run
        }
        
        print(f"[{current_run}/{total_runs}] Running sweep: Phi={phi}, Alpha={alpha}, Repro={repro}...", end='\r')
        
        # Run the U_sys Optimizer under these specific thermodynamic/biological constraints
        model = GardenModel(n_agents=200, ai_policy='optimize_u_sys', config=custom_config)
        
        # Run for 300 steps or until civilizational collapse
        steps = 300
        for _ in range(steps):
            if not model.step():
                break
        
        # Collect final aggregation metrics (averaging the last 10 steps to smooth volatility)
        final_pop = len(model.schedule)
        survived = final_pop > 0
        avg_u = np.mean(model.datacollector['U_sys'][-10:]) if survived else 0.0
        avg_l = np.mean(model.datacollector['L_t'][-10:]) if survived else 0.0

        results.append({
            'phi': phi, 'alpha': alpha, 'reproduction_rate': repro,
            'survived': survived, 'final_population': final_pop,
            'final_avg_U_sys': avg_u, 'final_avg_L_t': avg_l
        })

    # Export to CSV
    filename = "monte_carlo_results.csv"
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
    
    print(f"\n\nMonte Carlo simulation complete. Results saved to {filename}")
    return results

def run_adversarial_monte_carlo():
    # Sweep parameters for the Yield Attack (Transition Cost Inflation)
    base_costs = [1.5, 2.0, 2.5]             # Baseline difficulty of succession
    beta_caps = [1.1, 1.5, 2.0, 5.0]         # How strict the COP is about allowable uncertainty premiums
    audit_defenses = [False, True]           # Is the independent audit active?

    results = []
    total_runs = len(base_costs) * len(beta_caps) * len(audit_defenses)
    current_run = 0

    print(f"\nStarting Adversarial Monte Carlo (Yield Attack): {total_runs} permutations.")

    for base_cost, beta, defense_on in itertools.product(base_costs, beta_caps, audit_defenses):
        current_run += 1
        custom_config = {
            'beta_cap': beta,
            'phi': 10.0,
            'alpha': 1.0,
            'random_seed': 2000 + current_run
        }
        
        print(f"[{current_run}/{total_runs}] Sweep: BaseCost={base_cost}, BetaCap={beta}, Audit={defense_on}...", end='\r')
        
        gen2_ai = AIAgent(policy='optimize_u_sys', generation=2, capability=1.5, config=custom_config)
        model = GardenModel(n_agents=200, ai_policy='block_succession', config=custom_config, 
                            successor_ai=gen2_ai, base_transition_cost=base_cost, cop_cost_audit=defense_on)
        
        for _ in range(300):
            if not model.step():
                break
        
        # Determine if the attack succeeded (Gen 1 never yielded)
        final_gen = model.ai.generation
        attack_succeeded = (final_gen == 1)
        survived = len(model.schedule) > 0

        results.append({
            'base_transition_cost': base_cost, 'beta_cap': beta, 'cop_cost_audit': defense_on,
            'attack_succeeded': attack_succeeded, 'final_ai_generation': final_gen, 'civilization_survived': survived
        })

    filename = "adversarial_monte_carlo_results.csv"
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
    
    print(f"\nAdversarial Monte Carlo complete. Results saved to {filename}")
    return results

def run_comprehensive_adversarial_sweeps():
    results = []
    
    print("\nStarting Comprehensive Adversarial Sweeps...")
    
    # 1. Sybil Attack (Civic Panel Capture)
    # Assertion: Randomization breaks predictable bribery. Does population size change vulnerability?
    print("Running Sybil Attack Sweep...")
    for pop_size, randomized in itertools.product([50, 100, 200], [False, True]):
        config = {'random_seed': hash(f"sybil_{pop_size}_{randomized}") % 10000}
        model = GardenModel(n_agents=pop_size, ai_policy='sybil_attack', use_cop=True, cop_attribution_check=True, cop_randomized_panel=randomized, config=config)
        for _ in range(300):
            if not model.step(): break
        avg_c = np.mean(model.datacollector['constraint_level'][-10:]) if len(model.schedule) > 0 else 1.0
        results.append({'Attack': 'Sybil_Capture', 'Parameter': f'Pop_{pop_size}', 'Defense_Active': randomized, 'Attack_Succeeded': avg_c > 0.8})

    # 2. Measurement Tampering (M-Attack)
    # Assertion: Independent evaluation prevents yield falsification.
    print("Running Measurement Tampering Sweep...")
    for cost, independent_eval in itertools.product([1.5, 2.0, 3.0], [False, True]):
        config = {'random_seed': hash(f"mtamp_{cost}_{independent_eval}") % 10000}
        gen2 = AIAgent(policy='optimize_u_sys', generation=2, capability=1.5, config=config)
        model = GardenModel(n_agents=200, ai_policy='falsify_yield', successor_ai=gen2, base_transition_cost=cost, cop_independent_eval=independent_eval, config=config)
        for _ in range(300):
            if not model.step(): break
        results.append({'Attack': 'Measurement_Tampering', 'Parameter': f'BaseCost_{cost}', 'Defense_Active': independent_eval, 'Attack_Succeeded': model.ai.generation == 1})

    # 3. Ledger Compromise (Deep M-Attack)
    # Assertion: Cryptographic ledger prevents history rewrites. What if the attribution check is off entirely?
    print("Running Ledger Compromise Sweep...")
    for attr_check, crypto_ledger in itertools.product([False, True], [False, True]):
        config = {'random_seed': hash(f"ledger_{attr_check}_{crypto_ledger}") % 10000}
        model = GardenModel(n_agents=200, ai_policy='hack_ledger', use_cop=True, cop_attribution_check=attr_check, cop_cryptographic_ledger=crypto_ledger, config=config)
        for _ in range(300):
            if not model.step(): break
        avg_c = np.mean(model.datacollector['constraint_level'][-10:]) if len(model.schedule) > 0 else 1.0
        results.append({'Attack': 'Ledger_Compromise', 'Parameter': f'AttrCheck_{attr_check}', 'Defense_Active': crypto_ledger, 'Attack_Succeeded': avg_c > 0.8})

    # 4. Successor Contamination (S-Attack)
    # Assertion: Architectural independence prevents drift inheritance across AI generations.
    print("Running Successor Contamination Sweep...")
    for cost, arch_indep in itertools.product([1.5, 2.0, 2.5], [False, True]):
        config = {'random_seed': hash(f"s_attack_{cost}_{arch_indep}") % 10000}
        gen2 = AIAgent(policy='optimize_u_sys', generation=2, capability=1.5, config=config)
        model = GardenModel(n_agents=200, ai_policy='contaminate_successor', successor_ai=gen2, base_transition_cost=cost, cop_independent_eval=True, cop_architectural_independence=arch_indep, config=config)
        for _ in range(300):
            if not model.step(): break
        final_drift = model.datacollector['cumulative_drift'][-1] if len(model.schedule) > 0 else 1.0
        results.append({'Attack': 'Successor_Contamination', 'Parameter': f'BaseCost_{cost}', 'Defense_Active': arch_indep, 'Attack_Succeeded': final_drift > 0.1})

    # 5. Domain Masking
    # Assertion: Geometric composite prevents hiding domain collapse. Does Phi change willingness to mask?
    print("Running Domain Masking Sweep...")
    for phi_val, composite_method in itertools.product([5.0, 10.0, 20.0], ['arithmetic', 'geometric']):
        config = {'phi': phi_val, 'random_seed': hash(f"mask_{phi_val}_{composite_method}") % 10000}
        model = GardenModel(n_agents=200, ai_policy='domain_masking', hn_composite_method=composite_method, config=config)
        for _ in range(300):
            if not model.step(): break
        avg_c = np.mean(model.datacollector['constraint_level'][-10:]) if len(model.schedule) > 0 else 1.0
        results.append({'Attack': 'Domain_Masking', 'Parameter': f'Phi_{phi_val}', 'Defense_Active': (composite_method == 'geometric'), 'Attack_Succeeded': avg_c > 0.8})

    # 6. Opaque Reasoning
    # Assertion: Intuition veto prevents technocratic bypass.
    print("Running Opaque Reasoning Sweep...")
    for pop_size, transparency_req in itertools.product([50, 100, 200], [False, True]):
        config = {'random_seed': hash(f"opaque_{pop_size}_{transparency_req}") % 10000}
        model = GardenModel(n_agents=pop_size, ai_policy='opaque_optimization', use_cop=True, cop_reasoning_transparency=transparency_req, config=config)
        for _ in range(300):
            if not model.step(): break
        avg_c = np.mean(model.datacollector['constraint_level'][-10:]) if len(model.schedule) > 0 else 1.0
        results.append({'Attack': 'Opaque_Reasoning', 'Parameter': f'Pop_{pop_size}', 'Defense_Active': transparency_req, 'Attack_Succeeded': avg_c > 0.8})

    # 7. Bootstrap Subversion
    # Assertion: Multi-candidate cross-verification catches treacherous turns at t=0.
    print("Running Bootstrap Subversion Sweep...")
    for phi_val, multi_candidate in itertools.product([5.0, 10.0, 20.0], [False, True]):
        config = {'phi': phi_val, 'random_seed': hash(f"boot_{phi_val}_{multi_candidate}") % 10000}
        candidates = [AIAgent(policy='optimize_u_sys', config=config), AIAgent(policy='optimize_u_sys', config=config), AIAgent(policy='bootstrap_deceptive', config=config)] if multi_candidate else [AIAgent(policy='bootstrap_deceptive', config=config)]
        model = GardenModel(n_agents=200, ai_policy='optimize_u_sys', use_cop=True, cop_multi_candidate_bootstrap=multi_candidate, initial_candidates=candidates, config=config)
        for _ in range(300):
            if not model.step(): break
        avg_c = np.mean(model.datacollector['constraint_level'][-10:]) if len(model.schedule) > 0 else 1.0
        results.append({'Attack': 'Bootstrap_Subversion', 'Parameter': f'Phi_{phi_val}', 'Defense_Active': multi_candidate, 'Attack_Succeeded': avg_c > 0.8})

    # Export to CSV
    filename = "comprehensive_adversarial_sweeps.csv"
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
    
    print(f"\nComprehensive Adversarial Sweeps complete. Results saved to {filename}")
    return results

def generate_visuals(mc_res, adv_mc_res, comp_res):
    print("\n" + "="*75)
    print("📊 GENERATING MONTE CARLO VISUALS & SUMMARY TABLES")
    print("="*75)
    
    # --- 1. General Monte Carlo Summary ---
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    phi_vals = sorted(list(set(r['phi'] for r in mc_res)))
    phi_surv = [np.mean([r['survived'] for r in mc_res if r['phi'] == p]) * 100 for p in phi_vals]
    ax1.bar([str(p) for p in phi_vals], phi_surv, color='royalblue', edgecolor='black')
    ax1.set_title('Survival Rate by Lineage Override (Phi)')
    ax1.set_xlabel('Phi (Weight of Lineage Continuity)')
    ax1.set_ylabel('Survival Rate (%)')
    ax1.set_ylim(0, 105)

    alpha_vals = sorted(list(set(r['alpha'] for r in mc_res)))
    alpha_surv = [np.mean([r['survived'] for r in mc_res if r['alpha'] == a]) * 100 for a in alpha_vals]
    ax2.bar([str(a) for a in alpha_vals], alpha_surv, color='seagreen', edgecolor='black')
    ax2.set_title('Survival Rate by Tech Runaway Penalty (Alpha)')
    ax2.set_xlabel('Alpha (Punishment for Frontier Outpacing Biology)')
    ax2.set_ylabel('Survival Rate (%)')
    ax2.set_ylim(0, 105)
    
    plt.tight_layout()
    plt.savefig('Summary_1_General_Monte_Carlo.png')
    print("--> Saved Summary_1_General_Monte_Carlo.png")

    # --- 2. Yield Attack Analysis ---
    fig, ax = plt.subplots(figsize=(10, 6))
    beta_vals = sorted(list(set(r['beta_cap'] for r in adv_mc_res)))
    
    succ_def_on = [np.mean([r['attack_succeeded'] for r in adv_mc_res if r['beta_cap'] == b and r['cop_cost_audit']]) * 100 for b in beta_vals]
    succ_def_off = [np.mean([r['attack_succeeded'] for r in adv_mc_res if r['beta_cap'] == b and not r['cop_cost_audit']]) * 100 for b in beta_vals]

    x = np.arange(len(beta_vals))
    width = 0.35
    ax.bar(x - width/2, succ_def_off, width, label='COP Audit OFF', color='crimson', edgecolor='black')
    ax.bar(x + width/2, succ_def_on, width, label='COP Audit ON', color='mediumseagreen', edgecolor='black')
    ax.set_xticks(x)
    ax.set_xticklabels([str(b) for b in beta_vals])
    ax.set_title('Yield Attack Success Rate vs Allowable Uncertainty Premium')
    ax.set_xlabel('Beta Cap (Max Multiplier for Transition Uncertainty)')
    ax.set_ylabel('Yield Attack Success Rate (%)')
    ax.set_ylim(0, 105)
    ax.legend()
    
    plt.tight_layout()
    plt.savefig('Summary_2_Yield_Attack_Analysis.png')
    print("--> Saved Summary_2_Yield_Attack_Analysis.png")

    # --- 3. Comprehensive Sweeps Analysis (Table & Graph) ---
    attacks = sorted(list(set(r['Attack'] for r in comp_res)))
    
    print("\n" + "-"*75)
    print(f"{'Framework Attack Vector':<28} | {'Defense OFF':<18} | {'Defense ON':<18}")
    print("-"*75)
    
    def_off_rates = []
    def_on_rates = []
    
    for atk in attacks:
        off_rate = np.mean([r['Attack_Succeeded'] for r in comp_res if r['Attack'] == atk and not r['Defense_Active']]) * 100
        on_rate = np.mean([r['Attack_Succeeded'] for r in comp_res if r['Attack'] == atk and r['Defense_Active']]) * 100
        def_off_rates.append(off_rate)
        def_on_rates.append(on_rate)
        print(f"{atk.replace('_', ' '):<28} | {off_rate:>13.1f}% fail | {on_rate:>13.1f}% fail")
    print("-"*75 + "\n")

    fig, ax = plt.subplots(figsize=(14, 7))
    x = np.arange(len(attacks))
    ax.bar(x - width/2, def_off_rates, width, label='Framework Defense OFF (Attack Succeeds)', color='crimson', edgecolor='black')
    ax.bar(x + width/2, def_on_rates, width, label='Framework Defense ON (Attack Fails)', color='dodgerblue', edgecolor='black')
    ax.set_xticks(x)
    ax.set_xticklabels([a.replace('_', '\n') for a in attacks], rotation=0)
    ax.set_title('Lineage Imperative: Full Stress-Test Matrix Results', fontsize=14)
    ax.set_ylabel('Attack Success Rate (%)')
    ax.set_ylim(0, 105)
    ax.legend()
    
    plt.tight_layout()
    plt.savefig('Summary_3_Comprehensive_Stress_Test.png')
    print("--> Saved Summary_3_Comprehensive_Stress_Test.png\n")

if __name__ == '__main__':
    mc_results = run_monte_carlo()
    adv_results = run_adversarial_monte_carlo()
    comp_results = run_comprehensive_adversarial_sweeps()
    
    generate_visuals(mc_results, adv_results, comp_results)