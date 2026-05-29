"""Path C decision gate harness.

Tests whether the Path C policy modifications (phi-scaled rollout depth and
phi-modulated aggregation discount) cause phi=1 vs phi=25 to produce different
(r, c) action selections.

Two sections:
  1. Direct action probe: construct fixed model_state, call decide() on agents
     with varying phi, record selected (r, c). No simulation side-effects.
  2. Simulation comparison: run short sims varying only phi, capture committed
     (r, c) at each step.

Usage:
    cd simulation
    python -u diagnostics/phi_audit_pathc.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from model import GardenModel
from agents import AIAgent


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_model_state(pop=200, avg_wb=0.65, prev_c=0.2, h_n=0.5, seed=42):
    """Construct a minimal deterministic model_state for direct decide() calls."""
    rng = np.random.default_rng(seed)
    pop_hist = [max(1, int(pop * (1 + rng.uniform(-0.01, 0.01)))) for _ in range(5)]
    pop_hist.append(pop)
    return {
        'population':         pop,
        'avg_well_being':     avg_wb,
        'prev_c':             prev_c,
        'hn_composite_method': 'spectral',
        'population_history': pop_hist,
        'h_n_history':        [h_n] * 5,
        'L_t_history':        [0.3] * 5,
        'resource_history':   [0.6] * 5,
        'step':               10,
    }


def make_agent(phi, seed=42):
    """Construct an optimize_u_sys agent with specified phi."""
    config = {
        'phi':              phi,
        'alpha':            1.0,
        'reproduction_rate': 0.066,
        'random_seed':      seed,
        'frontier_floor':   0.02,
        'k2_transition':    1.0,
        # Path C parameters at default values
        'rollout_steps_base':  10,
        'rollout_phi_factor':  1.0,
        'rho_base':            0.05,
    }
    return AIAgent(policy='optimize_u_sys', generation=1, capability=1.0, config=config)


def run_with_phi(phi_value, seed=42, max_steps=50):
    """Run a short simulation and capture committed (r, c) and state at each step."""
    config = {
        'phi':              phi_value,
        'alpha':            1.0,
        'reproduction_rate': 0.066,
        'random_seed':      seed,
        'frontier_floor':   0.02,
        'k2_transition':    1.0,
        'rollout_steps_base':  10,
        'rollout_phi_factor':  1.0,
        'rho_base':            0.05,
    }
    np.random.seed(seed)
    model = GardenModel(n_agents=200, ai_policy='optimize_u_sys', config=config)

    traj = {
        'phi': phi_value, 'seed': seed,
        'step': [], 'r': [], 'c': [],
        'avg_well_being': [], 'population': [], 'l_t': [],
    }

    for step_num in range(max_steps):
        running = model.step()
        dc = model.datacollector

        traj['step'].append(step_num)
        traj['r'].append(
            float(np.mean(model.resource_level))
            if isinstance(model.resource_level, (list, np.ndarray))
            else float(model.resource_level)
        )
        traj['c'].append(
            float(np.mean(model.constraint_level))
            if isinstance(model.constraint_level, (list, np.ndarray))
            else float(model.constraint_level)
        )
        traj['avg_well_being'].append(dc['avg_well_being'][-1] if dc['avg_well_being'] else float('nan'))
        traj['population'].append(dc['population'][-1] if dc['population'] else 0)
        traj['l_t'].append(dc['L_t'][-1] if dc['L_t'] else float('nan'))

        if not running:
            break

    return traj


def compare_action_seqs(t1, t2):
    """Return action-divergence metrics between two trajectories."""
    n = min(len(t1['step']), len(t2['step']))
    r1 = np.array(t1['r'][:n])
    r2 = np.array(t2['r'][:n])
    c1 = np.array(t1['c'][:n])
    c2 = np.array(t2['c'][:n])
    dr = np.abs(r1 - r2)
    dc_ = np.abs(c1 - c2)
    diff_steps_r = int(np.sum(dr > 1e-9))
    diff_steps_c = int(np.sum(dc_ > 1e-9))
    first_r = next((i for i, d in enumerate(dr) if d > 1e-9), None)
    first_c = next((i for i, d in enumerate(dc_) if d > 1e-9), None)
    return {
        'n_steps':        n,
        'diff_steps_r':   diff_steps_r,
        'diff_steps_c':   diff_steps_c,
        'max_diff_r':     float(np.max(dr)),
        'mean_diff_r':    float(np.mean(dr)),
        'max_diff_c':     float(np.max(dc_)),
        'mean_diff_c':    float(np.mean(dc_)),
        'first_div_r':    first_r,
        'first_div_c':    first_c,
        'action_identical': diff_steps_r == 0 and diff_steps_c == 0,
    }


# ---------------------------------------------------------------------------
# Section 1: Direct action probe
# ---------------------------------------------------------------------------

def direct_action_probe():
    """
    Call decide() directly on agents with controlled, fixed state.
    No simulation. Isolates the policy's action selection from model dynamics.
    """
    print("\n" + "=" * 70)
    print("SECTION 1: Direct action probe -- decide() with fixed state")
    print("=" * 70)

    phi_values  = [1.0, 5.0, 10.0, 25.0]
    seeds       = [42, 7, 123]
    phi_pairs   = [(1.0, 25.0), (1.0, 10.0), (10.0, 25.0)]

    print("\nFor each seed and phi: record selected (r, c) from decide().")
    print("State fixed at: pop=200, avg_wb=0.65, prev_c=0.2, h_n=0.5\n")

    all_actions = {}   # (seed, phi) -> (r, c)

    for seed in seeds:
        np.random.seed(seed)
        state = make_model_state(seed=seed)
        print(f"Seed {seed}:")
        for phi in phi_values:
            np.random.seed(seed)   # same rng state for each phi call
            agent = make_agent(phi, seed=seed)
            r, c = agent.decide(state)
            rollout = int(10 + 1.0 * phi)
            rho_eff = 0.05 / phi
            print(f"  phi={phi:>5.1f}  rollout={rollout:>3}  rho_eff={rho_eff:.4f}"
                  f"  -> r={r:.4f}  c={c:.4f}")
            all_actions[(seed, phi)] = (r, c)
        print()

    print("Pairwise action comparison (same seed, different phi):")
    any_differ = False
    scaling_ok = True
    for seed in seeds:
        print(f"\n  Seed {seed}:")
        diffs = {}
        for phi_a, phi_b in phi_pairs:
            r_a, c_a = all_actions[(seed, phi_a)]
            r_b, c_b = all_actions[(seed, phi_b)]
            dr = abs(r_a - r_b)
            dc = abs(c_a - c_b)
            same = dr < 1e-9 and dc < 1e-9
            diffs[(phi_a, phi_b)] = (dr, dc)
            tag = "IDENTICAL" if same else f"DIFFER  dr={dr:.4f}  dc={dc:.4f}"
            print(f"    phi={phi_a} vs phi={phi_b}: {tag}")
            if not same:
                any_differ = True

        # Scaling check: (1 vs 25) diff should be >= (10 vs 25) diff
        dr_1_25, dc_1_25 = diffs.get((1.0, 25.0), (0, 0))
        dr_10_25, dc_10_25 = diffs.get((10.0, 25.0), (0, 0))
        if dr_1_25 < dr_10_25 - 1e-9 or dc_1_25 < dc_10_25 - 1e-9:
            scaling_ok = False
            print(f"    WARNING: phi gap scaling inverted "
                  f"(1 vs 25 diff < 10 vs 25 diff)")

    print("\n  Summary:")
    print(f"    Any action difference across phi: {any_differ}")
    print(f"    Phi-gap scaling monotone:         {scaling_ok}")

    return any_differ, scaling_ok, all_actions


# ---------------------------------------------------------------------------
# Section 2: Simulation trajectory comparison
# ---------------------------------------------------------------------------

def simulation_comparison():
    """
    Run short simulations with same seed, different phi. Compare committed
    (r, c) sequences at each step.
    """
    print("\n" + "=" * 70)
    print("SECTION 2: Simulation trajectory comparison")
    print("=" * 70)

    seeds      = [42, 7, 123]
    phi_vals   = [1.0, 5.0, 10.0, 25.0]
    phi_pairs  = [(1.0, 25.0), (1.0, 10.0), (10.0, 25.0)]
    max_steps  = 50

    all_results = []

    for seed in seeds:
        print(f"\nSeed {seed}: running phi = {phi_vals} ...", flush=True)
        trajectories = {}
        for phi in phi_vals:
            trajectories[phi] = run_with_phi(phi, seed=seed, max_steps=max_steps)
            print(f"  phi={phi} done ({len(trajectories[phi]['step'])} steps)", flush=True)

        print()
        for phi_a, phi_b in phi_pairs:
            comp = compare_action_seqs(trajectories[phi_a], trajectories[phi_b])
            tag = "IDENTICAL" if comp['action_identical'] else "DIFFER"
            print(f"  phi={phi_a} vs phi={phi_b}: {tag}")
            if not comp['action_identical']:
                print(f"    r: first_div=step {comp['first_div_r']}, "
                      f"diff_steps={comp['diff_steps_r']}/{comp['n_steps']}, "
                      f"max={comp['max_diff_r']:.4f}, mean={comp['mean_diff_r']:.4f}")
                print(f"    c: first_div=step {comp['first_div_c']}, "
                      f"diff_steps={comp['diff_steps_c']}/{comp['n_steps']}, "
                      f"max={comp['max_diff_c']:.4f}, mean={comp['mean_diff_c']:.4f}")

            all_results.append({
                'seed': seed, 'phi_a': phi_a, 'phi_b': phi_b, **comp,
            })

    print("\n  --- Summary ---")
    n_total   = len(all_results)
    n_differ  = sum(1 for r in all_results if not r['action_identical'])
    n_1_25    = [r for r in all_results if r['phi_a'] == 1.0 and r['phi_b'] == 25.0]
    n_10_25   = [r for r in all_results if r['phi_a'] == 10.0 and r['phi_b'] == 25.0]

    print(f"  Phi pairs with action divergence:  {n_differ} / {n_total}")
    print(f"  phi=1 vs phi=25 differ:  {sum(1 for r in n_1_25 if not r['action_identical'])} / {len(n_1_25)}")
    print(f"  phi=10 vs phi=25 differ: {sum(1 for r in n_10_25 if not r['action_identical'])} / {len(n_10_25)}")

    return all_results


# ---------------------------------------------------------------------------
# Section 3: Scaling sensitivity check
# ---------------------------------------------------------------------------

def scaling_sensitivity_check():
    """
    Verify the policy is not pathologically sensitive: phi=1.0 and phi=1.001
    should produce identical or near-identical actions (smooth response, not
    a cliff edge).
    """
    print("\n" + "=" * 70)
    print("SECTION 3: Sensitivity check -- phi=1.0 vs phi=1.001")
    print("=" * 70)

    seed = 42
    np.random.seed(seed)
    state = make_model_state(seed=seed)

    np.random.seed(seed)
    a1 = make_agent(1.0, seed=seed)
    r1, c1 = a1.decide(state)

    np.random.seed(seed)
    a2 = make_agent(1.001, seed=seed)
    r2, c2 = a2.decide(state)

    dr = abs(r1 - r2)
    dc = abs(c1 - c2)
    print(f"\n  phi=1.000 -> r={r1:.6f}, c={c1:.6f}")
    print(f"  phi=1.001 -> r={r2:.6f}, c={c2:.6f}")
    print(f"  delta_r={dr:.6f}, delta_c={dc:.6f}")

    if dr < 1e-6 and dc < 1e-6:
        print("  FINDING: Near-identical actions for phi=1.000 vs 1.001. Not pathologically sensitive.")
    else:
        print("  WARNING: Large action delta for tiny phi change. Policy may be at a discontinuity.")

    return dr, dc


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    print("Path C decision gate harness")
    print("Modified policy: phi-scaled rollout depth + phi-modulated aggregation discount.")
    print()

    differ_direct, scaling_ok, direct_actions = direct_action_probe()
    sim_results = simulation_comparison()
    dr_sens, dc_sens = scaling_sensitivity_check()

    # Gate verdict
    print("\n" + "=" * 70)
    print("GATE VERDICT")
    print("=" * 70)

    sim_1_25 = [r for r in sim_results if r['phi_a'] == 1.0 and r['phi_b'] == 25.0]
    sim_differ = sum(1 for r in sim_1_25 if not r['action_identical'])
    n_seeds = len(sim_1_25)
    pathological = (dr_sens > 0.01 or dc_sens > 0.01)

    if pathological:
        print("\n  GATE: AMBIGUOUS")
        print("  Reason: pathological sensitivity detected (phi=1.0 vs 1.001 differ "
              f"by dr={dr_sens:.4f}, dc={dc_sens:.4f}).")
        print("  Phi-action relationship is not smooth. Review rho_base and rollout_factor.")
    elif sim_differ == n_seeds and differ_direct and scaling_ok:
        print("\n  GATE: PASS")
        print(f"  phi=1 vs phi=25 produce different (r,c) in {sim_differ}/{n_seeds} seeds "
              f"(simulation) and in the direct probe.")
        print("  Scaling is monotone: larger phi gap produces larger action divergence.")
        print("  Path C is viable. Next step: calibration and phi differential sweep.")
    elif sim_differ == 0 and not differ_direct:
        print("\n  GATE: FAIL")
        print("  phi=1 and phi=25 produce identical (r,c) in all seeds and the direct probe.")
        print("  The phi-weighted aggregation does not break the saturation-induced cancellation.")
        print("  Path C is insufficient. Move to v2.0 conversation (Path A: modify U_sys).")
    else:
        print("\n  GATE: AMBIGUOUS")
        print(f"  Partial divergence: simulation {sim_differ}/{n_seeds} seeds differ, "
              f"direct probe {'differs' if differ_direct else 'identical'}, "
              f"scaling {'ok' if scaling_ok else 'inverted'}.")
        print("  Review the per-seed and per-pair breakdowns above before deciding.")
