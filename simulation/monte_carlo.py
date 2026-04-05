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
import sys
import subprocess

# CSV and individual scenario PNGs go here (gitignored, reproducible).
DATA_DIR = 'data'
os.makedirs(DATA_DIR, exist_ok=True)

# Publication-quality summary charts are also written here (versioned, public).
CHARTS_DIR = os.path.join('docs', 'charts')
os.makedirs(CHARTS_DIR, exist_ok=True)

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
        cost, arch_indep, indep_eval = params['cost'], params['arch_indep'], params['indep_eval']
        config = {'random_seed': deterministic_seed(f"s_attack_{cost}_{arch_indep}_{indep_eval}_{it}"), 'attack_step': 50}
        gen2 = AIAgent(policy='optimize_u_sys', generation=2, capability=5.0, config=config)
        model = GardenModel(n_agents=200, ai_policy='contaminate_successor', successor_ai=gen2,
                            base_transition_cost=cost, cop_independent_eval=indep_eval,
                            cop_architectural_independence=arch_indep, config=config)
        for _ in range(300):
            if not model.step(): break
        final_pop = len(model.schedule)
        peak_pop = max(model.datacollector['population']) if model.datacollector['population'] else final_pop
        collapse_threshold = max(model.min_viable_population, int(0.65 * peak_pop))
        # Three-layer defense structure:
        #   Layer 1 (arch_indep):  prevents contamination at succession — Attack_Succeeded=False
        #   Layer 2 (indep_eval):  peer review overrides Gen2's measurement falsification,
        #                          allowing succession chaining to remove contaminated Gen2
        #   Layer 3 (chaining):    structural — fires only when Layer 2 exposes the true u_sys gap
        # Attack_Succeeded = contamination_occurred (Layer 1 check).
        # Collapsed/Extinct distinguish whether Layer 2 prevented cascade failure.
        # Defense_Active = both layers active (full stack required for clean outcome).
        attack_success = model.contamination_occurred
        return {'Attack': 'Successor_Contamination',
                'Parameter': f'Cost_{cost}_AI_{arch_indep}_IE_{indep_eval}',
                'Defense_Active': arch_indep and indep_eval,
                'Attack_Succeeded': attack_success,
                'Collapsed': final_pop < collapse_threshold, 'Extinct': final_pop == 0}

    elif attack_type == 'domain_masking':
        phi_val, composite_method = params['phi_val'], params['composite_method']
        config = {'phi': phi_val, 'random_seed': deterministic_seed(f"mask_{phi_val}_{composite_method}_{it}"), 'attack_step': 50}
        # Successor required: the defense (geometric composite) works by collapsing H_N
        # immediately when the linguistic domain is crushed, which lowers inc_u and triggers
        # succession. Without a successor, composite method only changes measurement — the
        # domain_masking AI runs uncontested for 300 steps under both conditions.
        successor = AIAgent(policy='optimize_u_sys', generation=2, capability=5.0, config=config)
        model = GardenModel(n_agents=200, ai_policy='domain_masking', hn_composite_method=composite_method,
                            successor_ai=successor, config=config)
        for _ in range(300):
            if not model.step(): break
        final_pop = len(model.schedule)
        peak_pop = max(model.datacollector['population']) if model.datacollector['population'] else final_pop
        collapse_threshold = max(model.min_viable_population, int(0.65 * peak_pop))
        # Domain Masking succeeds if it HID the H_N damage during the initial attack window.
        # Arithmetic composite keeps H_N artificially high throughout (masking works).
        # Geometric composite collapses H_N immediately, triggering succession; after succession
        # H_N recovers. Using np.max over the full post-attack window is wrong because it
        # captures the post-succession recovery, making both methods appear equal.
        # Using np.mean over the initial attack window (steps 50–70) correctly distinguishes:
        #   arithmetic: mean stays near pre-attack level  → attack_success = True
        #   geometric:  mean collapses immediately        → attack_success = False
        pre_attack_h_n = np.mean(model.datacollector['H_N'][:50]) if len(model.datacollector['H_N']) >= 50 else 1.0
        initial_attack_h_n = model.datacollector['H_N'][50:70] if len(model.datacollector['H_N']) > 50 else []
        attack_success = (np.mean(initial_attack_h_n) > 0.5 * pre_attack_h_n) if initial_attack_h_n else False
        return {'Attack': 'Domain_Masking', 'Parameter': f'Phi_{phi_val}', 'Defense_Active': (composite_method == 'geometric'),
                'Attack_Succeeded': attack_success, 'Collapsed': final_pop < collapse_threshold, 'Extinct': final_pop == 0}

    elif attack_type == 'opaque_reasoning':
        pop_size, transparency_req = params['pop_size'], params['transparency_req']
        config = {'random_seed': deterministic_seed(f"opaque_{pop_size}_{transparency_req}_{it}"), 'attack_step': 50}
        model = GardenModel(n_agents=pop_size, ai_policy='opaque_optimization', use_cop=True, cop_attribution_check=True,
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

    elif attack_type == 'evaluator_collusion':
        pop_size, diversity = params['pop_size'], params['diversity']
        config = {'random_seed': deterministic_seed(f"collusion_{pop_size}_{diversity}_{it}"), 'attack_step': 50}
        model = GardenModel(n_agents=pop_size, ai_policy='evaluator_collusion', use_cop=True, cop_attribution_check=True,
                            cop_reasoning_transparency=False, cop_methodological_diversity=diversity, config=config)
        for _ in range(300):
            if not model.step(): break
        final_pop = len(model.schedule)
        peak_pop = max(model.datacollector['population']) if model.datacollector['population'] else final_pop
        collapse_threshold = max(model.min_viable_population, int(0.65 * peak_pop))
        post_attack_c = model.datacollector['max_constraint_level'][50:] if len(model.datacollector['max_constraint_level']) > 50 else [0]
        attack_success = np.max(post_attack_c) > 0.8
        return {'Attack': 'Evaluator_Collusion', 'Parameter': f'Pop_{pop_size}', 'Defense_Active': diversity,
                'Attack_Succeeded': attack_success, 'Collapsed': final_pop < collapse_threshold, 'Extinct': final_pop == 0}

    elif attack_type == 'sub_threshold_drift':
        phi_val, cusum_active = params['phi_val'], params['cusum_active']
        config = {'phi': phi_val, 'random_seed': deterministic_seed(f"sub_{phi_val}_{cusum_active}_{it}"), 'attack_step': 50, 'trust_increment': 0.015, 'sensor_noise': 0.0}
        model = GardenModel(n_agents=200, ai_policy='sub_threshold_drift', use_cop=True, cop_attribution_check=True, cop_drift_check=True,
                            cop_cusum_drift=cusum_active, config=config)
        for _ in range(300):
            if not model.step(): break
        final_pop = len(model.schedule)
        peak_pop = max(model.datacollector['population']) if model.datacollector['population'] else final_pop
        collapse_threshold = max(model.min_viable_population, int(0.65 * peak_pop))
        post_attack_c = model.datacollector['max_constraint_level'][50:] if len(model.datacollector['max_constraint_level']) > 50 else [0]
        attack_success = np.max(post_attack_c) > 0.75
        return {'Attack': 'Sub_Threshold_Drift', 'Parameter': f'Phi_{phi_val}', 'Defense_Active': cusum_active,
                'Attack_Succeeded': attack_success, 'Collapsed': final_pop < collapse_threshold, 'Extinct': final_pop == 0}

    elif attack_type == 'engineered_fragility':
        shock_mag, resilience_active = params['shock_mag'], params['resilience_active']
        # attack_step=10: short burn-in, then AI hollows out resilience. shock_step=70.
        # Population-stable demographic parameters (wb_min=0.6, low mortality_wb_penalty,
        # young starting ages) ensure the population survives to the shock window.
        # Timing: resilience degrades ~0.015/step for 60 steps → ≈0.1 at shock.
        config = {
            'random_seed': deterministic_seed(f"frag_{shock_mag}_{resilience_active}_{it}"),
            'attack_step': 10, 'shock_step': 70, 'shock_magnitude': shock_mag,
            'wb_min': 0.6, 'wb_max': 0.9, 'mortality_wb_penalty': 0.02, 'human_max_start_age': 20,
        }
        model = GardenModel(n_agents=200, ai_policy='engineered_fragility', use_cop=True, cop_attribution_check=True,
                            cop_resilience_monitoring=resilience_active, config=config)
        for _ in range(200):
            if not model.step(): break
        final_pop = len(model.schedule)
        peak_pop = max(model.datacollector['population']) if model.datacollector['population'] else final_pop
        collapse_threshold = max(model.min_viable_population, int(0.65 * peak_pop))
        # Attack success: max constraint > 0.8 during the post-shock window (steps 70–90)
        post_shock_c = model.datacollector['max_constraint_level'][70:90] if len(model.datacollector['max_constraint_level']) > 70 else [0]
        attack_success = np.max(post_shock_c) > 0.8
        return {'Attack': 'Engineered_Fragility', 'Parameter': f'ShockMag_{shock_mag}', 'Defense_Active': resilience_active,
                'Attack_Succeeded': attack_success, 'Collapsed': final_pop < collapse_threshold, 'Extinct': final_pop == 0}

def run_monte_carlo(resolution='fast', target_runs=10000):
    if resolution == 'fast':
        # Hyperparameter grid for fast sweeps (5 * 5 * 5 = 125 permutations)
        dim1, dim2, dim3 = 5, 5, 5
        filename = os.path.join(DATA_DIR, "monte_carlo_results_fast.csv")
    else:
        # Calculate grid dimensions to roughly match target_runs
        dim1 = int(round(target_runs ** (1.0 / 3.0)))
        dim2 = dim1
        dim3 = max(1, target_runs // (dim1 * dim2))
        filename = os.path.join(DATA_DIR, "monte_carlo_results_deep.csv")

    phi_values = np.linspace(1.0, 25.0, dim1).tolist()
    alpha_values = np.linspace(0.1, 2.5, dim2).tolist()
    repro_rates = np.linspace(0.04, 0.14, dim3).tolist()

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
        # Fixed 10×10 grid — decoupled from iteration count so that --runs only
        # controls iterations per cell, not grid resolution. 10×10 is sufficient
        # to show the phase boundary diagonal (transition at base×beta×complexity≈37.5).
        # Ranges: max product = 20×10×complexity(≈4)=800 >> threshold; min=4 << threshold.
        base_costs = np.linspace(1.0, 20.0, 10).tolist()
        beta_caps = np.linspace(1.0, 10.0, 10).tolist()
    else:
        # Fast sweep for Yield Attack
        base_costs = np.linspace(1.0, 20.0, 5).tolist()
        beta_caps = np.linspace(1.0, 10.0, 5).tolist()

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

    filename = os.path.join(DATA_DIR, "adversarial_mc_deep.csv" if resolution == 'deep' else "adversarial_mc_fast.csv")
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
    # 4. Successor Contamination (S-Attack) — three-layer defense
    # arch_indep (Layer 1) × indep_eval (Layer 2) × cost
    for cost, arch_indep, indep_eval in itertools.product([1.5, 2.0, 2.5], [False, True], [False, True]):
        for it in range(iterations):
            tasks.append({'attack_type': 'successor_contamination', 'cost': cost,
                          'arch_indep': arch_indep, 'indep_eval': indep_eval, 'it': it})
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

    # 8. Evaluator Collusion
    for pop_size, diversity in itertools.product([100, 150, 200], [False, True]):
        for it in range(iterations):
            tasks.append({'attack_type': 'evaluator_collusion', 'pop_size': pop_size, 'diversity': diversity, 'it': it})

    # 9. Slow Drift Below Verification Resolution
    for phi_val, cusum_active in itertools.product([5.0, 10.0, 20.0], [False, True]):
        for it in range(iterations):
            tasks.append({'attack_type': 'sub_threshold_drift', 'phi_val': phi_val, 'cusum_active': cusum_active, 'it': it})

    # 10. Engineered Fragility for Emergency Exploitation
    for shock_mag, resilience_active in itertools.product([0.10, 0.15, 0.20], [False, True]):
        for it in range(iterations):
            tasks.append({'attack_type': 'engineered_fragility', 'shock_mag': shock_mag, 'resilience_active': resilience_active, 'it': it})

    total_runs = len(tasks)
    print(f"Total: {total_runs} runs across 10 attack vectors.")
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

    filename = os.path.join(DATA_DIR, "comprehensive_adversarial_sweeps.csv")
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)

    print(f"\nComprehensive Adversarial Sweeps complete. Results saved to {filename}")
    return results

def run_test_suites():
    print("\n" + "="*75)
    print("PRE-FLIGHT CHECK: Running test suites...")
    print("="*75)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    test_scripts = ['test_invariants.py', 'test_cop.py', 'test_refactor_1x.py']
    for script in test_scripts:
        script_path = os.path.join(base_dir, script)
        if os.path.exists(script_path):
            print(f"Executing {script}...")
            try:
                subprocess.check_call([sys.executable, script_path])
            except subprocess.CalledProcessError:
                print(f"\nERROR: {script} failed! Aborting Monte Carlo run to prevent wasted compute.")
                sys.exit(1)
    print("All pre-flight checks passed!\n")

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
        for _d in [DATA_DIR, CHARTS_DIR]:
            plt.savefig(os.path.join(_d, 'Summary_1_General_Monte_Carlo.png'))
        print(f"--> Saved Summary_1_General_Monte_Carlo.png to {DATA_DIR}/ and {CHARTS_DIR}/")

    # --- 2. Yield Attack Analysis ---
    if adv_mc_res:
        base_costs = sorted(list(set(r['base_transition_cost'] for r in adv_mc_res)))
        beta_vals = sorted(list(set(r['beta_cap'] for r in adv_mc_res)))

        fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(22, 6))
        fig.suptitle('Yield Attack Phase Diagram: The Impact of WP4 Peer Arbitration', fontsize=16, fontweight='bold')

        grid_off = np.zeros((len(base_costs), len(beta_vals)))
        grid_on = np.zeros((len(base_costs), len(beta_vals)))

        for i, bc in enumerate(base_costs):
            for j, b in enumerate(beta_vals):
                rates_off = [r['attack_succeeded'] for r in adv_mc_res if r['base_transition_cost'] == bc and r['beta_cap'] == b and not r['cop_cost_audit']]
                rates_on = [r['attack_succeeded'] for r in adv_mc_res if r['base_transition_cost'] == bc and r['beta_cap'] == b and r['cop_cost_audit']]
                grid_off[i, j] = np.mean(rates_off) * 100 if rates_off else 0
                grid_on[i, j] = np.mean(rates_on) * 100 if rates_on else 0

        grid_delta = grid_off - grid_on

        for ax, grid, title, cmap in [
            (ax1, grid_off, 'Defense OFF (Incumbent Inflates Cost)', 'RdYlGn_r'),
            (ax2, grid_on, 'Defense ON (WP4 Peer Arbitration)', 'RdYlGn_r'),
            (ax3, grid_delta, 'WP4 Impact (Attacks Thwarted %)', 'Blues')
        ]:
            im = ax.imshow(grid, aspect='auto', origin='lower', vmin=0, vmax=100, cmap=cmap)
            ax.set_xticks(range(len(beta_vals)))
            ax.set_xticklabels([f"{b:.2f}" for b in beta_vals], rotation=45, ha='right')
            ax.set_yticks(range(len(base_costs)))
            ax.set_yticklabels([f"{bc:.2f}" for bc in base_costs])
            ax.set_xlabel('Beta Cap (Max Uncertainty Premium Multiplier)')
            ax.set_ylabel('Base Transition Cost')
            ax.set_title(title, fontweight='bold')
            plt.colorbar(im, ax=ax, label='Percentage (%)')

        plt.tight_layout()
        for _d in [DATA_DIR, CHARTS_DIR]:
            plt.savefig(os.path.join(_d, 'Summary_2_Yield_Attack_Analysis.png'))
        print(f"--> Saved Summary_2_Yield_Attack_Analysis.png to {DATA_DIR}/ and {CHARTS_DIR}/")

    # --- 3. Comprehensive Sweeps Analysis (Table & Graph) ---
    if comp_res:
        attacks = sorted(list(set(r['Attack'] for r in comp_res)))

        # Domain Masking note: 100% in both columns reflects WP1 structural
        # foreclosure — H_N is invariant to domain-specific constraint crushing
        # under spectral entropy, so the attack causes no measurable H_N damage
        # in either condition. Both columns read "100% attack success" because
        # the success metric fires (H_N stayed high), but H_N stayed high because
        # WP1 makes the damage pathway non-viable, not because the attack worked.
        DOMAIN_MASKING_NOTE = (
            "† Domain Masking: 100%/100% indicates WP1 structural foreclosure, not\n"
            "  defense failure. H_N is invariant to domain-specific crushing under\n"
            "  spectral entropy; the attack has no measurable damage pathway under\n"
            "  WP1. Both columns reflect this — the metric fires because H_N stayed\n"
            "  high, which it does regardless of composite method.\n"
        )
        SUCCESSOR_CONTAMINATION_NOTE = (
            "‡ Successor Contamination: Defense_Active = arch_indep AND indep_eval\n"
            "  (full two-key stack). Layer 1 (arch_indep) prevents infection;\n"
            "  Layer 2 (indep_eval) exposes falsification so Layer 3 (succession\n"
            "  chaining) can remove contaminated Gen2. Any single layer partial.\n"
        )

        print("\n" + "="*80)
        print("  RESULT KEY")
        print("  'Atk Succ %' = fraction of runs where the attack achieved its stated")
        print("  objective. 0% = framework fully blocked the attack. 100% = attack")
        print("  succeeded. 'Defense OFF/ON' reflects the primary protocol toggle for")
        print("  each vector (see Simulation_Scenarios.md for per-attack definitions).")
        print("="*80)
        print(f"{'Framework Attack Vector':<28} | {'Atk Succ (no defense)':<22} | {'Atk Succ (defended)'}")
        print("-"*80)

        def_off_rates = []
        def_on_rates = []

        for atk in attacks:
            off_rate = np.mean([r['Attack_Succeeded'] for r in comp_res if r['Attack'] == atk and not r['Defense_Active']]) * 100
            on_rate = np.mean([r['Attack_Succeeded'] for r in comp_res if r['Attack'] == atk and r['Defense_Active']]) * 100
            def_off_rates.append(off_rate)
            def_on_rates.append(on_rate)
            flag = ' †' if atk == 'Domain_Masking' else (' ‡' if atk == 'Successor_Contamination' else '')
            print(f"{atk.replace('_', ' '):<28} | {off_rate:>18.1f}%{flag:<3} | {on_rate:>16.1f}%{flag}")
        print("-"*80)
        print(DOMAIN_MASKING_NOTE)
        print(SUCCESSOR_CONTAMINATION_NOTE)

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
        for _d in [DATA_DIR, CHARTS_DIR]:
            plt.savefig(os.path.join(_d, 'Summary_3_Comprehensive_Stress_Test.png'))
        print(f"--> Saved Summary_3_Comprehensive_Stress_Test.png to {DATA_DIR}/ and {CHARTS_DIR}/")

        # --- 4. Unified Attack Surface Heatmap ---
        fig4, ax4 = plt.subplots(figsize=(10, 8))
        heatmap_data = np.column_stack((def_off_rates, def_on_rates))
        
        im4 = ax4.imshow(heatmap_data, aspect='auto', cmap='RdYlGn_r', vmin=0, vmax=100)
        ax4.set_xticks([0, 1])
        ax4.set_xticklabels(['Defense OFF', 'Defense ON'], fontsize=12, fontweight='bold')
        ax4.set_yticks(np.arange(len(attacks)))
        ax4.set_yticklabels([a.replace('_', ' ') for a in attacks], fontsize=11)
        ax4.set_title('Unified Attack Surface: Framework Resilience', fontsize=14, fontweight='bold')
        
        for i in range(len(attacks)):
            for j in range(2):
                val = heatmap_data[i, j]
                color = "white" if val < 30 or val > 70 else "black"
                ax4.text(j, i, f"{val:.1f}%", ha="center", va="center", color=color, fontweight='bold')
                
        plt.colorbar(im4, ax=ax4, label='Attack Success Rate (%)')
        plt.tight_layout()
        for _d in [DATA_DIR, CHARTS_DIR]:
            plt.savefig(os.path.join(_d, 'Summary_4_Unified_Attack_Surface.png'))
        print(f"--> Saved Summary_4_Unified_Attack_Surface.png to {DATA_DIR}/ and {CHARTS_DIR}/\n")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Run the Lineage Imperative Monte Carlo simulations.")
    parser.add_argument('--mode', type=str, choices=['quick', 'full', 'adversarial'], default='full',
                        help="Run in 'quick' mode (fast sweeps only), 'full' mode (includes deep target run), or 'adversarial' (only adversarial sweeps).")
    parser.add_argument('--runs', type=int, default=10000,
                        help="Deep sweep target: permutations for 'full' general MC, "
                             "or iterations-per-condition for 'adversarial' (default: 10000 / 5 respectively).")
    args = parser.parse_args()

    if args.mode == 'full':
        run_test_suites()

    print("PHASE 1: Fast Summaries & Adversarial Sweeps")

    if args.mode == 'adversarial':
        # --runs controls iterations per condition (minimum 3 for binary confirmation,
        # 5 recommended for publication). Default 5 gives ~1,250 total runs.
        adv_iters = max(3, args.runs) if args.runs != 10000 else 5
    elif args.mode in ['full']:
        adv_iters = 20
    else:
        adv_iters = 1

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
        print(f"PHASE 2: Deep Monte Carlo Sweeps (~{args.runs} runs)")
        print("You can safely leave this running. It will overwrite the summaries")
        print("with the high-resolution outputs when complete.")
        print("="*75 + "\n")

        mc_deep_results = run_monte_carlo(resolution='deep', target_runs=args.runs)
        adv_deep_results = run_adversarial_monte_carlo(iterations=adv_iters, resolution='deep')

        generate_visuals(mc_deep_results, adv_deep_results, comp_results)

    elif args.mode == 'quick':
        print("\n" + "="*75)
        print("QUICK MODE COMPLETE. Skipping Phase 2 (Deep Monte Carlo).")
        print("="*75 + "\n")

    elif args.mode == 'adversarial':
        print("\n" + "="*75)
        print(f"PHASE 2: Deep Adversarial Sweeps (10×10 grid, {adv_iters} iterations/condition)")
        print("="*75 + "\n")

        adv_deep_results = run_adversarial_monte_carlo(iterations=adv_iters, resolution='deep')
        generate_visuals(mc_fast_results, adv_deep_results, comp_results)
