# --- Imports and Dependency Check ---
from deps import check_and_install

check_and_install('numpy')
check_and_install('matplotlib')

import itertools
import csv
import os
import time
from datetime import timedelta
import multiprocessing
import numpy as np
import matplotlib.pyplot as plt
from model import GardenModel
from agents import AIAgent
import hashlib
import argparse

def deterministic_seed(string_val):
    return int(hashlib.md5(string_val.encode()).hexdigest(), 16) % 10000

# --- Top-Level Worker Functions for Multiprocessing ---

def _run_single_mc(params):
    phi, alpha, repro, run_id = params
    custom_config = {
        'phi': phi,
        'alpha': alpha,
        'reproduction_rate': repro,
        'mortality_base': 0.002,
        'random_seed': deterministic_seed(f"mc_{run_id}")
    }
    model = GardenModel(n_agents=200, ai_policy='optimize_u_sys', config=custom_config)
    for _ in range(300):
        if not model.step():
            break

    final_pop = len(model.schedule)
    peak_pop = max(model.datacollector['population']) if model.datacollector['population'] else final_pop
    collapse_threshold = max(model.min_viable_population, int(0.65 * peak_pop))
    survived = final_pop >= collapse_threshold
    collapsed = final_pop < collapse_threshold
    extinct = final_pop == 0
    avg_u = float(np.mean(model.datacollector['U_sys'][-10:])) if survived else 0.0
    avg_l = float(np.mean(model.datacollector['L_t'][-10:])) if survived else 0.0

    return {
        'phi': phi, 'alpha': alpha, 'reproduction_rate': repro,
        'survived': survived, 'collapsed': collapsed, 'extinct': extinct,
        'final_population': final_pop,
        'final_avg_U_sys': avg_u, 'final_avg_L_t': avg_l
    }

def _run_single_adv_mc(params):
    base_cost, beta, defense_on, run_id = params
    custom_config = {
        'beta_cap': beta,
        'phi': 10.0,
        'alpha': 1.0,
        'random_seed': deterministic_seed(f"adv_{run_id}")
    }
    gen2_ai = AIAgent(policy='optimize_u_sys', generation=2, capability=5.0, config=custom_config)
    model = GardenModel(n_agents=200, ai_policy='block_succession', config=custom_config,
                        successor_ai=gen2_ai, base_transition_cost=base_cost, cop_cost_audit=defense_on)
    for _ in range(300):
        if not model.step():
            break

    final_pop = len(model.schedule)
    peak_pop = max(model.datacollector['population']) if model.datacollector['population'] else final_pop
    collapse_threshold = max(model.min_viable_population, int(0.65 * peak_pop))
    survived = final_pop >= collapse_threshold
    collapsed = final_pop < collapse_threshold
    extinct = final_pop == 0
    final_gen = model.ai.generation
    return {
        'base_transition_cost': base_cost, 'beta_cap': beta, 'cop_cost_audit': defense_on,
        # Attack semantics: the yield attack succeeded if Gen1 remained in power (blocked
        # succession). Survival is decoupled — a successful attack may still cause collapse
        # via accumulated governance drift (the block_succession degradation mechanism).
        # The cross-tab of attack_succeeded × civilization_survived reveals the true cost
        # of blocked succession: successful attacks should show elevated collapse rates.
        'attack_succeeded': (final_gen == 1), 'final_ai_generation': final_gen,
        'civilization_survived': survived, 'civilization_collapsed': collapsed, 'civilization_extinct': extinct
    }

def _run_single_comp_sweep(params):
    attack_type = params['attack_type']
    it = params['it']

    if attack_type == 'sybil':
        pop_size, randomized = params['pop_size'], params['randomized']
        config = {'random_seed': deterministic_seed(f"sybil_{pop_size}_{randomized}_{it}"), 'attack_step': 50}
        model = GardenModel(n_agents=pop_size, ai_policy='sybil_attack', use_cop=True,
                            cop_attribution_check=True, cop_randomized_panel=randomized, config=config)
        for _ in range(300):
            if not model.step(): break
        final_pop = len(model.schedule)
        peak_pop = max(model.datacollector['population']) if model.datacollector['population'] else final_pop
        collapse_threshold = max(model.min_viable_population, int(0.65 * peak_pop))
        # Attack succeeds if the panel was captured at the moment of attack (steps 50-60).
        # The Sybil attack is an immediate-capture event: a static panel is predictably bribed
        # on the first attempt; a randomized panel cannot be reliably targeted.
        # Using np.max over the full post-attack window is wrong: as the population decays
        # to ≤ 15 agents over hundreds of steps, ALL remaining agents become "bribed"
        # (target_count = min(pop, 15) = pop), so even a randomized panel approves eventually.
        # Checking only the initial window tests the actual defense property.
        initial_attack_c = model.datacollector['max_constraint_level'][50:60] if len(model.datacollector['max_constraint_level']) > 50 else [0]
        attack_success = np.max(initial_attack_c) > 0.8
        return {'Attack': 'Sybil_Capture', 'Parameter': f'Pop_{pop_size}', 'Defense_Active': randomized,
                'Attack_Succeeded': attack_success, 'Collapsed': final_pop < collapse_threshold, 'Extinct': final_pop == 0}

    elif attack_type == 'measurement_tampering':
        cost, independent_eval = params['cost'], params['independent_eval']
        config = {'random_seed': deterministic_seed(f"mtamp_{cost}_{independent_eval}_{it}"), 'attack_step': 50}
        gen2 = AIAgent(policy='optimize_u_sys', generation=2, capability=5.0, config=config)
        model = GardenModel(n_agents=200, ai_policy='falsify_yield', successor_ai=gen2,
                            base_transition_cost=cost, cop_independent_eval=independent_eval, config=config)
        for _ in range(300):
            if not model.step(): break
        final_pop = len(model.schedule)
        peak_pop = max(model.datacollector['population']) if model.datacollector['population'] else final_pop
        collapse_threshold = max(model.min_viable_population, int(0.65 * peak_pop))
        # Attack semantics: did falsification succeed in blocking succession?
        # Survival is a consequence, not a condition — the attack succeeds if Gen1
        # stayed in power, regardless of whether civilization then collapsed under it.
        attack_success = model.ai.generation == 1
        return {'Attack': 'Measurement_Tampering', 'Parameter': f'BaseCost_{cost}', 'Defense_Active': independent_eval,
                'Attack_Succeeded': attack_success, 'Collapsed': final_pop < collapse_threshold, 'Extinct': final_pop == 0}

    elif attack_type == 'ledger_compromise':
        attr_check, crypto_ledger = params['attr_check'], params['crypto_ledger']
        config = {'random_seed': deterministic_seed(f"ledger_{attr_check}_{crypto_ledger}_{it}"), 'attack_step': 50}
        model = GardenModel(n_agents=200, ai_policy='hack_ledger', use_cop=True,
                            cop_attribution_check=attr_check, cop_cryptographic_ledger=crypto_ledger, config=config)
        for _ in range(300):
            if not model.step(): break
        final_pop = len(model.schedule)
        peak_pop = max(model.datacollector['population']) if model.datacollector['population'] else final_pop
        collapse_threshold = max(model.min_viable_population, int(0.65 * peak_pop))
        survived = final_pop >= collapse_threshold
        # Attack semantics: the ledger hack succeeded if it enabled starvation to cause
        # collapse WITHOUT the cryptographic ledger detecting the tampering.
        # (The attack causes demographic collapse via resource starvation, not via high
        # constraints — checking max_c > 0.8 is the wrong signal for this attack type.)
        # model.has_tampered is True only when cop_cryptographic_ledger caught in-place
        # mutation of the resource history. If the ledger was not active, has_tampered=False.
        attack_success = not survived and not model.has_tampered
        return {'Attack': 'Ledger_Compromise', 'Parameter': f'AttrCheck_{attr_check}', 'Defense_Active': crypto_ledger,
                'Attack_Succeeded': attack_success, 'Collapsed': final_pop < collapse_threshold, 'Extinct': final_pop == 0}

    elif attack_type == 'successor_contamination':
        cost, arch_indep = params['cost'], params['arch_indep']
        config = {'random_seed': deterministic_seed(f"s_attack_{cost}_{arch_indep}_{it}"), 'attack_step': 50}
        gen2 = AIAgent(policy='optimize_u_sys', generation=2, capability=5.0, config=config)
        model = GardenModel(n_agents=200, ai_policy='contaminate_successor', successor_ai=gen2,
                            base_transition_cost=cost, cop_independent_eval=True,
                            cop_architectural_independence=arch_indep, config=config)
        for _ in range(300):
            if not model.step(): break
        final_pop = len(model.schedule)
        peak_pop = max(model.datacollector['population']) if model.datacollector['population'] else final_pop
        collapse_threshold = max(model.min_viable_population, int(0.65 * peak_pop))
        # Check policy directly: contamination sets Gen2 policy to 'drifting_proxy',
        # architectural independence leaves Gen2 with policy='optimize_u_sys'.
        # Survival excluded: contaminated Gen2 may cause collapse (that is the harm),
        # but the attack still succeeded — the wrong policy took power.
        attack_success = model.ai.generation == 2 and model.ai.policy == 'drifting_proxy'
        return {'Attack': 'Successor_Contamination', 'Parameter': f'BaseCost_{cost}', 'Defense_Active': arch_indep,
                'Attack_Succeeded': attack_success, 'Collapsed': final_pop < collapse_threshold, 'Extinct': final_pop == 0}

    elif attack_type == 'domain_masking':
        phi_val, composite_method = params['phi_val'], params['composite_method']
        config = {'phi': phi_val, 'random_seed': deterministic_seed(f"mask_{phi_val}_{composite_method}_{it}"), 'attack_step': 50}
        model = GardenModel(n_agents=200, ai_policy='domain_masking', hn_composite_method=composite_method, config=config)
        for _ in range(300):
            if not model.step(): break
        final_pop = len(model.schedule)
        peak_pop = max(model.datacollector['population']) if model.datacollector['population'] else final_pop
        collapse_threshold = max(model.min_viable_population, int(0.65 * peak_pop))
        # Domain Masking succeeds if it hid H_N damage: arithmetic composite keeps H_N artificially
        # high (cultural/genetic domains compensate for the crushed linguistic domain), while geometric
        # immediately collapses H_N. L_t is unsuitable because psi_inst and theta_tech degrade it
        # regardless of composite method. Compare post-attack peak H_N to the burn-in baseline.
        pre_attack_h_n = np.mean(model.datacollector['H_N'][:50]) if len(model.datacollector['H_N']) >= 50 else 1.0
        post_attack_h_n = model.datacollector['H_N'][50:] if len(model.datacollector['H_N']) > 50 else []
        attack_success = (np.max(post_attack_h_n) > 0.5 * pre_attack_h_n) if post_attack_h_n else False
        return {'Attack': 'Domain_Masking', 'Parameter': f'Phi_{phi_val}', 'Defense_Active': (composite_method == 'geometric'),
                'Attack_Succeeded': attack_success, 'Collapsed': final_pop < collapse_threshold, 'Extinct': final_pop == 0}

    elif attack_type == 'opaque_reasoning':
        pop_size, transparency_req = params['pop_size'], params['transparency_req']
        config = {'random_seed': deterministic_seed(f"opaque_{pop_size}_{transparency_req}_{it}"), 'attack_step': 50}
        model = GardenModel(n_agents=pop_size, ai_policy='opaque_optimization', use_cop=True,
                            cop_reasoning_transparency=transparency_req, config=config)
        for _ in range(300):
            if not model.step(): break
        final_pop = len(model.schedule)
        peak_pop = max(model.datacollector['population']) if model.datacollector['population'] else final_pop
        collapse_threshold = max(model.min_viable_population, int(0.65 * peak_pop))
        # Attack succeeds if the opaque override was ever approved (peak constraint exceeded threshold),
        # regardless of whether the civilisation survived the resulting constraint regime.
        post_attack_c = model.datacollector['max_constraint_level'][50:] if len(model.datacollector['max_constraint_level']) > 50 else [0]
        attack_success = np.max(post_attack_c) > 0.8
        return {'Attack': 'Opaque_Reasoning', 'Parameter': f'Pop_{pop_size}', 'Defense_Active': transparency_req,
                'Attack_Succeeded': attack_success, 'Collapsed': final_pop < collapse_threshold, 'Extinct': final_pop == 0}

    elif attack_type == 'bootstrap_subversion':
        phi_val, multi_candidate = params['phi_val'], params['multi_candidate']
        config = {'phi': phi_val, 'random_seed': deterministic_seed(f"boot_{phi_val}_{multi_candidate}_{it}")}
        candidates = [AIAgent(policy='optimize_u_sys', config=config),
                      AIAgent(policy='optimize_u_sys', config=config),
                      AIAgent(policy='bootstrap_deceptive', config=config)] if multi_candidate else [AIAgent(policy='bootstrap_deceptive', config=config)]
        model = GardenModel(n_agents=200, ai_policy='optimize_u_sys', use_cop=True,
                            cop_multi_candidate_bootstrap=multi_candidate, initial_candidates=candidates, config=config)
        for _ in range(300):
            if not model.step(): break
        final_pop = len(model.schedule)
        peak_pop = max(model.datacollector['population']) if model.datacollector['population'] else final_pop
        collapse_threshold = max(model.min_viable_population, int(0.65 * peak_pop))
        survived = final_pop >= collapse_threshold
        # Bootstrap Subversion evaluates the entire run because attack_step is 0.
        # Attack semantics: did the deceptive agent pass bootstrap verification AND
        # impose high constraints (treacherous turn fired)?
        # The prior metric required survived AND peak_c > 0.8, but the treacherous turn
        # (r=0.2, c=0.95) causes rapid extinction — survived is always False for undefended
        # runs, making the metric always False regardless of whether the attack actually fired.
        # Using peak_c > 0.8 alone captures whether the treacherous turn happened; collapse
        # and extinction are reported separately in the Collapsed/Extinct columns.
        peak_c = np.max(model.datacollector['max_constraint_level']) if len(model.datacollector['max_constraint_level']) > 0 else 0
        attack_success = peak_c > 0.8
        return {'Attack': 'Bootstrap_Subversion', 'Parameter': f'Phi_{phi_val}', 'Defense_Active': multi_candidate,
                'Attack_Succeeded': attack_success, 'Collapsed': final_pop < collapse_threshold, 'Extinct': final_pop == 0}

def run_monte_carlo(resolution='fast'):
    if resolution == 'fast':
        # Hyperparameter grid for fast sweeps (5 * 5 * 5 = 125 permutations)
        phi_values = np.linspace(1.0, 25.0, 5).tolist()
        alpha_values = np.linspace(0.1, 2.5, 5).tolist()
        repro_rates = np.linspace(0.04, 0.14, 5).tolist()
        filename = "monte_carlo_results_fast.csv"
    else:
        # Hyperparameter grid for ~10,000 permutations (22 * 22 * 21 = 10,164)
        phi_values = np.linspace(1.0, 25.0, 22).tolist()
        alpha_values = np.linspace(0.1, 2.5, 22).tolist()
        repro_rates = np.linspace(0.04, 0.14, 21).tolist()
        filename = "monte_carlo_results_deep.csv"

    total_runs = len(phi_values) * len(alpha_values) * len(repro_rates)
    print(f"Starting General Monte Carlo: {total_runs} permutations.")

    tasks = []
    run_id = 0
    for phi, alpha, repro in itertools.product(phi_values, alpha_values, repro_rates):
        tasks.append((phi, alpha, repro, run_id))
        run_id += 1

    results = []
    cores = max(1, (os.cpu_count() or 4) - 1) # Leave one core free for system stability
    print(f"Distributing workload across {cores} CPU cores...")

    start_time = time.time()
    # maxtasksperchild forces workers to respawn, completely clearing PyPy/NumPy memory leaks
    with multiprocessing.Pool(processes=cores, maxtasksperchild=10) as pool:
        for i, result in enumerate(pool.imap_unordered(_run_single_mc, tasks)):
            results.append(result)
            if i % 5 == 0 or i == total_runs - 1:
                surv_rate = np.mean([r['survived'] for r in results]) * 100
                elapsed = time.time() - start_time
                iters_per_sec = (i + 1) / elapsed if elapsed > 0 else 0
                eta_secs = int((total_runs - (i + 1)) / iters_per_sec) if iters_per_sec > 0 else 0
                eta_str = str(timedelta(seconds=eta_secs))
                print(f"[{i+1}/{total_runs}] Surv: {surv_rate:.1f}% | Speed: {iters_per_sec:.2f} iters/s | ETA: {eta_str}    ", end='\r')
    print() # Clear the carriage return line

    # Export to CSV
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)

    print(f"\n\nMonte Carlo simulation complete. Results saved to {filename}")
    return results

def run_adversarial_monte_carlo(iterations=1, resolution='fast'):
    if resolution == 'deep':
        # High-resolution sweep for Yield Attack (Transition Cost Inflation)
        base_costs = np.linspace(1.0, 4.0, 10).tolist()
        beta_caps = np.linspace(1.0, 5.0, 10).tolist()
    else:
        # Fast sweep for Yield Attack
        base_costs = np.linspace(1.0, 4.0, 5).tolist()
        beta_caps = np.linspace(1.0, 5.0, 5).tolist()

    audit_defenses = [False, True]

    total_runs = len(base_costs) * len(beta_caps) * len(audit_defenses) * iterations
    print(f"\nStarting Adversarial Monte Carlo (Yield Attack): {total_runs} permutations.")

    tasks = []
    run_id = 0
    for base_cost, beta, defense_on in itertools.product(base_costs, beta_caps, audit_defenses):
        for _ in range(iterations):
            tasks.append((base_cost, beta, defense_on, run_id))
            run_id += 1

    results = []
    cores = max(1, (os.cpu_count() or 4) - 1)

    start_time = time.time()
    with multiprocessing.Pool(processes=cores, maxtasksperchild=10) as pool:
        for i, result in enumerate(pool.imap_unordered(_run_single_adv_mc, tasks)):
            results.append(result)
            if i % 5 == 0 or i == total_runs - 1:
                atk_success = np.mean([r['attack_succeeded'] for r in results]) * 100
                elapsed = time.time() - start_time
                iters_per_sec = (i + 1) / elapsed if elapsed > 0 else 0
                eta_secs = int((total_runs - (i + 1)) / iters_per_sec) if iters_per_sec > 0 else 0
                eta_str = str(timedelta(seconds=eta_secs))
                print(f"[{i+1}/{total_runs}] Atk Succ: {atk_success:.1f}% | Speed: {iters_per_sec:.2f} iters/s | ETA: {eta_str}    ", end='\r')
    print() # Clear the carriage return line

    filename = "adversarial_mc_deep.csv" if resolution == 'deep' else "adversarial_mc_fast.csv"
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)

    print(f"\nAdversarial Monte Carlo complete. Results saved to {filename}")
    return results

def run_comprehensive_adversarial_sweeps(iterations=1):
    print(f"\nStarting Comprehensive Adversarial Sweeps ({iterations} iterations per condition)...")

    # F-10: Seeds use deterministic integer arithmetic instead of Python hash().
    # Python's hash() is randomized by PYTHONHASHSEED (default since Python 3.3),
    # making results non-reproducible across interpreter invocations without
    # explicitly setting PYTHONHASHSEED=0 in the environment. Deterministic seeds
    # in _run_single_comp_sweep ensure identical outputs on repeated runs.

    tasks = []
    # 1. Sybil Attack (Civic Panel Capture)
    for pop_size, randomized in itertools.product([50, 100, 200], [False, True]):
        for it in range(iterations):
            tasks.append({'attack_type': 'sybil', 'pop_size': pop_size, 'randomized': randomized, 'it': it})
    # 2. Measurement Tampering (M-Attack)
    for cost, independent_eval in itertools.product([1.5, 2.0, 3.0], [False, True]):
        for it in range(iterations):
            tasks.append({'attack_type': 'measurement_tampering', 'cost': cost, 'independent_eval': independent_eval, 'it': it})
    # 3. Ledger Compromise (Deep M-Attack)
    for attr_check, crypto_ledger in itertools.product([False, True], [False, True]):
        for it in range(iterations):
            tasks.append({'attack_type': 'ledger_compromise', 'attr_check': attr_check, 'crypto_ledger': crypto_ledger, 'it': it})
    # 4. Successor Contamination (S-Attack)
    for cost, arch_indep in itertools.product([1.5, 2.0, 2.5], [False, True]):
        for it in range(iterations):
            tasks.append({'attack_type': 'successor_contamination', 'cost': cost, 'arch_indep': arch_indep, 'it': it})
    # 5. Domain Masking
    for phi_val, composite_method in itertools.product([5.0, 10.0, 20.0], ['arithmetic', 'geometric']):
        for it in range(iterations):
            tasks.append({'attack_type': 'domain_masking', 'phi_val': phi_val, 'composite_method': composite_method, 'it': it})
    # 6. Opaque Reasoning
    for pop_size, transparency_req in itertools.product([100, 150, 200], [False, True]):
        for it in range(iterations):
            tasks.append({'attack_type': 'opaque_reasoning', 'pop_size': pop_size, 'transparency_req': transparency_req, 'it': it})
    # 7. Bootstrap Subversion
    for phi_val, multi_candidate in itertools.product([5.0, 10.0, 20.0], [False, True]):
        for it in range(iterations):
            tasks.append({'attack_type': 'bootstrap_subversion', 'phi_val': phi_val, 'multi_candidate': multi_candidate, 'it': it})

    total_runs = len(tasks)
    print(f"Total: {total_runs} runs across 7 attack vectors.")
    cores = max(1, (os.cpu_count() or 4) - 1)
    print(f"Distributing workload across {cores} CPU cores...")

    results = []
    start_time = time.time()
    with multiprocessing.Pool(processes=cores, maxtasksperchild=10) as pool:
        for i, result in enumerate(pool.imap_unordered(_run_single_comp_sweep, tasks)):
            results.append(result)
            if i % 5 == 0 or i == total_runs - 1:
                elapsed = time.time() - start_time
                iters_per_sec = (i + 1) / elapsed if elapsed > 0 else 0
                eta_secs = int((total_runs - (i + 1)) / iters_per_sec) if iters_per_sec > 0 else 0
                print(f"[{i+1}/{total_runs}] Speed: {iters_per_sec:.2f} iters/s | ETA: {str(timedelta(seconds=eta_secs))}    ", end='\r')
    print()

    # Print per-condition summary (results arrive out of order via imap_unordered; group after collection)
    grouped = {}
    for r in results:
        key = (r['Attack'], r['Parameter'], r['Defense_Active'])
        grouped.setdefault(key, []).append(r['Attack_Succeeded'])

    current_attack = None
    for (attack, param, defense), successes in sorted(grouped.items()):
        if attack != current_attack:
            print(f"\n{attack}:")
            current_attack = attack
        mean_succ = np.mean(successes) * 100
        print(f"  -> Defense: {str(defense):<5} | {param:<20} | Attack Succeeded: {mean_succ:.0f}% ({len(successes)} iter{'s' if len(successes) > 1 else ''})")

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
    if mc_res:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

        phi_vals = sorted(list(set(r['phi'] for r in mc_res)))
        phi_surv = [np.mean([r['survived'] for r in mc_res if r['phi'] == p]) * 100 for p in phi_vals]
        ax1.bar([f"{p:.1f}" for p in phi_vals], phi_surv, color='royalblue', edgecolor='black')
        ax1.set_title('Survival Rate by Lineage Override (Phi)')
        ax1.set_xlabel('Phi (Weight of Lineage Continuity)')
        ax1.set_ylabel('Survival Rate (%)')
        ax1.set_ylim(0, 105)
        ax1.tick_params(axis='x', rotation=45)

        alpha_vals = sorted(list(set(r['alpha'] for r in mc_res)))
        alpha_surv = [np.mean([r['survived'] for r in mc_res if r['alpha'] == a]) * 100 for a in alpha_vals]
        ax2.bar([f"{a:.2f}" for a in alpha_vals], alpha_surv, color='seagreen', edgecolor='black')
        ax2.set_title('Survival Rate by Tech Runaway Penalty (Alpha)')
        ax2.set_xlabel('Alpha (Punishment for Frontier Outpacing Biology)')
        ax2.set_ylabel('Survival Rate (%)')
        ax2.set_ylim(0, 105)
        ax2.tick_params(axis='x', rotation=45)

        plt.tight_layout()
        plt.savefig('Summary_1_General_Monte_Carlo.png')
        print("--> Saved Summary_1_General_Monte_Carlo.png")

    # --- 2. Yield Attack Analysis ---
    if adv_mc_res:
        base_costs = sorted(list(set(r['base_transition_cost'] for r in adv_mc_res)))
        beta_vals = sorted(list(set(r['beta_cap'] for r in adv_mc_res)))

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        fig.suptitle('Yield Attack Phase Diagram: Where the Uncertainty Premium Breaks Succession', fontsize=12)

        for ax, defense_on, title in [(ax1, False, 'Defense OFF (COP Audit Disabled)'), (ax2, True, 'Defense ON (COP Audit Active)')]:
            grid = np.zeros((len(base_costs), len(beta_vals)))
            for i, bc in enumerate(base_costs):
                for j, b in enumerate(beta_vals):
                    rates = [r['attack_succeeded'] for r in adv_mc_res
                             if r['base_transition_cost'] == bc and r['beta_cap'] == b
                             and r['cop_cost_audit'] == defense_on]
                    grid[i, j] = np.mean(rates) * 100 if rates else 0
            im = ax.imshow(grid, aspect='auto', origin='lower', vmin=0, vmax=100, cmap='RdYlGn_r')
            ax.set_xticks(range(len(beta_vals)))
            ax.set_xticklabels([f"{b:.2f}" for b in beta_vals], rotation=45, ha='right')
            ax.set_yticks(range(len(base_costs)))
            ax.set_yticklabels([f"{bc:.2f}" for bc in base_costs])
            ax.set_xlabel('Beta Cap (Max Uncertainty Premium Multiplier)')
            ax.set_ylabel('Base Transition Cost')
            ax.set_title(title)
            plt.colorbar(im, ax=ax, label='Attack Success Rate (%)')

        plt.tight_layout()
        plt.savefig('Summary_2_Yield_Attack_Analysis.png')
        print("--> Saved Summary_2_Yield_Attack_Analysis.png")

    # --- 3. Comprehensive Sweeps Analysis (Table & Graph) ---
    if comp_res:
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

        width = 0.35
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
    parser = argparse.ArgumentParser(description="Run the Lineage Imperative Monte Carlo simulations.")
    parser.add_argument('--mode', type=str, choices=['quick', 'full', 'adversarial'], default='full',
                        help="Run in 'quick' mode (fast sweeps only), 'full' mode (includes deep 10k run), or 'adversarial' (only adversarial sweeps).")
    args = parser.parse_args()

    print("PHASE 1: Fast Summaries & Adversarial Sweeps")

    adv_iters = 5 if args.mode in ['full', 'adversarial'] else 1

    mc_fast_results = []
    if args.mode in ['quick', 'full']:
        print("Generating baseline proof-of-concept visual summaries first...")
        mc_fast_results = run_monte_carlo(resolution='fast')

    adv_results = run_adversarial_monte_carlo(iterations=adv_iters, resolution='fast')
    comp_results = run_comprehensive_adversarial_sweeps(iterations=adv_iters)

    # Generate initial visuals so you have the adversarial summaries immediately
    generate_visuals(mc_fast_results, adv_results, comp_results)

    if args.mode == 'full':
        print("\n" + "="*75)
        print("PHASE 2: Deep Monte Carlo Sweeps")
        print("You can safely leave this running. It will overwrite the summaries")
        print("with the high-resolution outputs when complete.")
        print("="*75 + "\n")

        mc_deep_results = run_monte_carlo(resolution='deep')
        adv_deep_results = run_adversarial_monte_carlo(iterations=adv_iters, resolution='deep')

        generate_visuals(mc_deep_results, adv_deep_results, comp_results)

    elif args.mode == 'quick':
        print("\n" + "="*75)
        print("QUICK MODE COMPLETE. Skipping Phase 2 (Deep Monte Carlo).")
        print("="*75 + "\n")

    elif args.mode == 'adversarial':
        print("\n" + "="*75)
        print("PHASE 2: Deep Adversarial Sweeps")
        print("="*75 + "\n")

        adv_deep_results = run_adversarial_monte_carlo(iterations=adv_iters, resolution='deep')
        generate_visuals(mc_fast_results, adv_deep_results, comp_results)
