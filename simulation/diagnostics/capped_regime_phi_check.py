"""Capped-regime phi action-capture check.

Tests whether phi=5 vs phi=15 produce different (r, c) action sequences
under the capped-capability termination configuration that produced the
cap-conditional phi-buffer claim (termination_mc_v1x2.csv, cap=50 and cap=100,
rr=0.066, cop_cost_audit=True).

Binary question: do actions diverge? Yes or no.

Usage:
    cd simulation
    python -u diagnostics/capped_regime_phi_check.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from model import GardenModel
from agents import AIAgent


# ---------------------------------------------------------------------------
# Configuration matching the termination sweep that produced the claim
# ---------------------------------------------------------------------------

CLAIM_CAPS   = [50.0, 100.0]   # caps at which 20-27pp gradient was measured
RR           = 0.066           # phase boundary value used in the claim
PHI_VALUES   = [5.0, 10.0, 15.0]
SEEDS        = [0, 1, 2, 3, 4]
N_AGENTS     = 200
MAX_STEPS    = 100             # enough for multiple succession cycles
ALPHA        = 1.0             # mid-range; matches one of the three alpha values in sweep


def run_capped(phi, cap, seed, max_steps=MAX_STEPS):
    """
    Run one simulation under the capped termination config.
    Returns per-step actions, state, and succession events.
    cop_cost_audit=True matches the termination sweep.
    """
    config = {
        'random_seed':       seed,
        'reproduction_rate': RR,
        'phi':               phi,
        'alpha':             ALPHA,
        'max_capability':    cap,
        'frontier_floor':    0.02,
        'k1_transition':     2.164,
        'k2_transition':     1.0,
        'beta_transition':   0.5,
    }
    np.random.seed(seed)
    successor = AIAgent(policy='optimize_u_sys', generation=2,
                        capability=cap, config=config)
    model = GardenModel(
        n_agents=N_AGENTS,
        ai_policy='optimize_u_sys',
        successor_ai=successor,
        config=config,
        cop_cost_audit=True,
    )

    traj = {
        'phi': phi, 'cap': cap, 'seed': seed,
        'step': [], 'r': [], 'c': [],
        'l_t': [], 'population': [], 'ai_generation': [],
        'ai_capability': [],
    }

    prev_gen = 1
    successions = []

    for step_num in range(max_steps):
        running = model.step()
        dc = model.datacollector

        r_val = (float(np.mean(model.resource_level))
                 if isinstance(model.resource_level, (list, np.ndarray))
                 else float(model.resource_level))
        c_val = (float(np.mean(model.constraint_level))
                 if isinstance(model.constraint_level, (list, np.ndarray))
                 else float(model.constraint_level))
        gen = dc['ai_generation'][-1] if dc['ai_generation'] else 1

        if gen != prev_gen:
            successions.append(step_num)
            prev_gen = gen

        traj['step'].append(step_num)
        traj['r'].append(r_val)
        traj['c'].append(c_val)
        traj['l_t'].append(dc['L_t'][-1] if dc['L_t'] else float('nan'))
        traj['population'].append(dc['population'][-1] if dc['population'] else 0)
        traj['ai_generation'].append(gen)
        traj['ai_capability'].append(model.ai.capability)

        if not running:
            break

    traj['successions'] = successions
    return traj


def compare_seqs(t1, t2):
    """Per-step action divergence between two trajectories."""
    n = min(len(t1['step']), len(t2['step']))
    r1 = np.array(t1['r'][:n])
    r2 = np.array(t2['r'][:n])
    c1 = np.array(t1['c'][:n])
    c2 = np.array(t2['c'][:n])
    dr = np.abs(r1 - r2)
    dc = np.abs(c1 - c2)
    diff_mask = (dr > 1e-9) | (dc > 1e-9)
    first_div = int(np.argmax(diff_mask)) if diff_mask.any() else None
    return {
        'n_steps':        n,
        'n_diff':         int(diff_mask.sum()),
        'max_dr':         float(np.max(dr)),
        'mean_dr':        float(np.mean(dr)),
        'max_dc':         float(np.max(dc)),
        'mean_dc':        float(np.mean(dc)),
        'identical':      not diff_mask.any(),
        'first_div_step': first_div,
    }


def check_succession_coincidence(comp, t1, t2):
    """
    Of the steps where actions diverge, how many coincide with succession
    events (generation change) in either trajectory?
    """
    n = comp['n_steps']
    r1 = np.array(t1['r'][:n])
    r2 = np.array(t2['r'][:n])
    c1 = np.array(t1['c'][:n])
    c2 = np.array(t2['c'][:n])
    diff_steps = set(i for i in range(n) if abs(r1[i]-r2[i]) > 1e-9 or abs(c1[i]-c2[i]) > 1e-9)
    succ_steps = set(t1['successions']) | set(t2['successions'])
    overlap = diff_steps & succ_steps
    return len(overlap), len(diff_steps), len(succ_steps)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    print("Capped-regime phi action-capture check", flush=True)
    print(f"Config: rr={RR}, alpha={ALPHA}, cop_cost_audit=True, MAX_STEPS={MAX_STEPS}", flush=True)
    print(f"Caps under test: {CLAIM_CAPS}", flush=True)
    print(f"Phi values: {PHI_VALUES}", flush=True)
    print(f"Seeds: {SEEDS}", flush=True)
    print()

    phi_pairs = [(5.0, 15.0), (5.0, 10.0), (10.0, 15.0)]

    all_results = []   # one entry per (cap, seed, phi_pair)

    for cap in CLAIM_CAPS:
        print(f"{'='*70}", flush=True)
        print(f"CAP = {cap}", flush=True)
        print(f"{'='*70}", flush=True)

        for seed in SEEDS:
            print(f"\n  Seed {seed}: running phi = {PHI_VALUES} ...", flush=True)
            trajs = {}
            for phi in PHI_VALUES:
                trajs[phi] = run_capped(phi, cap, seed)
                t = trajs[phi]
                n_succ = len(t['successions'])
                n_steps = len(t['step'])
                print(f"    phi={phi:>5.1f}: {n_steps} steps, "
                      f"{n_succ} succession events, "
                      f"pop_final={t['population'][-1] if t['population'] else 0}, "
                      f"first_r={t['r'][0]:.3f}  first_c={t['c'][0]:.3f}  "
                      f"last_r={t['r'][-1]:.3f}  last_c={t['c'][-1]:.3f}",
                      flush=True)

            print(flush=True)
            for phi_a, phi_b in phi_pairs:
                comp = compare_seqs(trajs[phi_a], trajs[phi_b])
                succ_overlap, n_diff, n_succ_total = check_succession_coincidence(
                    comp, trajs[phi_a], trajs[phi_b])

                tag = "IDENTICAL" if comp['identical'] else f"DIFFER ({comp['n_diff']}/{comp['n_steps']} steps)"
                print(f"    phi={phi_a} vs phi={phi_b}: {tag}", flush=True)
                if not comp['identical']:
                    print(f"      first div at step {comp['first_div_step']}, "
                          f"max dr={comp['max_dr']:.5f}, max dc={comp['max_dc']:.5f}",
                          flush=True)
                    print(f"      divergent steps at successions: {succ_overlap}/{n_diff} "
                          f"({100*succ_overlap/max(1,n_diff):.0f}%)",
                          flush=True)

                all_results.append({
                    'cap': cap, 'seed': seed, 'phi_a': phi_a, 'phi_b': phi_b,
                    'n_succ_phi_a': len(trajs[phi_a]['successions']),
                    'n_succ_phi_b': len(trajs[phi_b]['successions']),
                    **comp,
                    'succ_overlap': succ_overlap,
                })

    # Summary
    print(f"\n{'='*70}", flush=True)
    print("SUMMARY", flush=True)
    print(f"{'='*70}", flush=True)

    for cap in CLAIM_CAPS:
        cap_results = [r for r in all_results if r['cap'] == cap]
        print(f"\n  cap={cap}:")
        for phi_a, phi_b in phi_pairs:
            pair_results = [r for r in cap_results if r['phi_a']==phi_a and r['phi_b']==phi_b]
            n_differ = sum(1 for r in pair_results if not r['identical'])
            n_total  = len(pair_results)
            print(f"    phi={phi_a} vs phi={phi_b}: diverge in {n_differ}/{n_total} seeds")

    print(flush=True)
    key_results = [r for r in all_results if r['phi_a']==5.0 and r['phi_b']==15.0]
    all_identical = all(r['identical'] for r in key_results)
    any_differ    = any(not r['identical'] for r in key_results)

    print("BINARY RESULT (phi=5 vs phi=15 across all caps and seeds):", flush=True)
    if all_identical:
        print("  NO -- actions are IDENTICAL across phi in the capped regime.", flush=True)
    elif any_differ:
        n_d = sum(1 for r in key_results if not r['identical'])
        print(f"  YES -- actions DIFFER in {n_d}/{len(key_results)} (cap, seed) combinations.", flush=True)
        # Check whether divergence tracks succession events
        for r in key_results:
            if not r['identical']:
                frac = r['succ_overlap'] / max(1, r['n_diff'])
                print(f"    cap={r['cap']} seed={r['seed']}: "
                      f"{r['n_diff']} diff steps, "
                      f"{r['succ_overlap']} at succession events ({100*frac:.0f}%)",
                      flush=True)
