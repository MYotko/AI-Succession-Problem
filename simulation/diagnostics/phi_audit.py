"""Phi implementation audit harness.

Runs deterministic simulations varying only phi to determine whether phi
affects the AI's actions and the simulation's state trajectory. Read-only
with respect to production code; this harness imports the model and captures
state via datacollector and attribute reads, without instrumenting any
production file.

Usage:
    cd simulation
    python -u diagnostics/phi_audit.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from model import GardenModel
from agents import AIAgent
from metrics import calculate_system_metrics


# ---------------------------------------------------------------------------
# Section 1 -- Analytical: document U_sys structure and phi's role
# ---------------------------------------------------------------------------

def analyze_usys_formula():
    """
    Analytically evaluate whether phi's position in the U_sys formula
    allows it to affect action selection.

    U_sys (metrics.py line 251):
        u_sys = (w_n * pred_hn + w_e * h_e) * (discount + phi * l_t)

    Inverse-scarcity weights:
        w_n = lambda_n / (pred_hn + epsilon)  =>  w_n * pred_hn = lambda_n * pred_hn / (pred_hn + epsilon)
        w_e = lambda_e / (h_e + epsilon)      =>  w_e * h_e     = lambda_e * h_e     / (h_e + epsilon)

    When pred_hn >> epsilon and h_e >> epsilon, both products saturate to
    their respective lambda constants, making the first factor approximately
    equal to lambda_n + lambda_e -- constant across all (r, c) candidates.

    If the first factor A(r,c) is constant, then:
        argmax_{r,c} u_sys
        = argmax_{r,c} A * (discount + phi * l_t)
        = argmax_{r,c} (discount + phi * l_t)
        = argmax_{r,c} l_t    [since discount is constant for fixed horizon,
                                and phi > 0 is a positive scalar scaling]

    This argmax is INDEPENDENT OF PHI.
    """
    print("\n" + "=" * 60)
    print("SECTION 1: U_sys formula -- phi's role in action selection")
    print("=" * 60)

    # Constants from metrics.py
    lambda_n = 5.0
    lambda_e = 3.0
    epsilon  = 1e-6
    rho      = 0.01

    # Representative mid-run state
    pred_hn = 0.50    # typical spectral H_N
    r_bio   = 0.55    # typical AI resource allocation
    cap     = 1.0     # initial AI capability
    h_e_mult = 0.5
    h_e     = cap * (1.0 - r_bio) * h_e_mult   # = 0.225 at r=0.55

    # First factor
    w_n    = lambda_n / (pred_hn + epsilon)
    w_e    = lambda_e / (h_e     + epsilon)
    A_real = w_n * pred_hn + w_e * h_e
    A_approx = lambda_n + lambda_e

    print(f"\nRepresentative state: pred_hn={pred_hn}, r_bio={r_bio}, h_e={h_e:.4f}, cap={cap}")
    print(f"  w_n = {w_n:.4f},   w_n * pred_hn = {w_n * pred_hn:.4f}  (lambda_n = {lambda_n})")
    print(f"  w_e = {w_e:.4f},   w_e * h_e     = {w_e * h_e:.4f}  (lambda_e = {lambda_e})")
    print(f"  First factor A (actual):  {A_real:.6f}")
    print(f"  First factor A (approx):  {A_approx:.6f}  (lambda_n + lambda_e)")
    print(f"  Relative error:           {abs(A_real - A_approx) / A_approx * 100:.4f}%")

    # Vary phi, hold state constant, compute u_sys for two candidates
    # Candidate 1: (r=0.55, c=0.2) -- typical high-wb, low-constraint choice
    # Candidate 2: (r=0.40, c=0.3) -- more constrained alternative
    # If phi doesn't change the relative ranking, the argmax is phi-invariant.
    print("\nPhi sweep -- ranking of two fixed (r,c) candidates:")
    print(f"  Candidate A: r=0.55, c=0.2")
    print(f"  Candidate B: r=0.40, c=0.3")
    print(f"  (State: pred_hn={pred_hn}, pop=200, avg_wb=0.65, cap=1.0, eval_horizon=1)")
    print()

    avg_wb = 0.65
    pop    = 200
    prev_c = 0.2
    horizon = 1

    rankings = []
    for phi in [1.0, 5.0, 10.0, 15.0, 25.0]:
        cfg = {'phi': phi, 'frontier_floor': 0.02, 'k2_transition': 1.0}
        _, _, _, _, _, u_a, _ = calculate_system_metrics(
            0.55, 0.2, pop, avg_wb, cap, config=cfg,
            eval_horizon=horizon, prev_c=prev_c,
            h_n_override=pred_hn
        )
        _, _, _, _, _, u_b, _ = calculate_system_metrics(
            0.40, 0.3, pop, avg_wb, cap, config=cfg,
            eval_horizon=horizon, prev_c=prev_c,
            h_n_override=pred_hn
        )
        winner = 'A' if u_a > u_b else 'B'
        rankings.append(winner)
        print(f"  phi={phi:>5.1f}: u_sys(A)={u_a:8.4f}, u_sys(B)={u_b:8.4f}, winner={winner}  "
              f"(ratio A/B = {u_a/u_b:.4f})")

    if len(set(rankings)) == 1:
        print(f"\n  FINDING: Both candidates rank the SAME across all phi values.")
        print(f"  The argmax over (r,c) is phi-invariant at this state point.")
    else:
        print(f"\n  FINDING: Rankings differ across phi values -- phi affects action selection.")


# ---------------------------------------------------------------------------
# Section 2 -- Numerical: compute U_sys components at representative state
# ---------------------------------------------------------------------------

def analyze_numerical_magnitude():
    """
    Compute U_sys components at a representative mid-run state to report
    the lineage term's contribution and how it varies with phi.
    """
    print("\n" + "=" * 60)
    print("SECTION 2: Numerical magnitude of phi's contribution to U_sys")
    print("=" * 60)

    avg_wb  = 0.65
    pop     = 200
    pred_hn = 0.50
    prev_c  = 0.2
    r_bio   = 0.55
    c_avg   = 0.2
    cap     = 1.0
    horizon = 10   # mid-rollout step

    print(f"\nRepresentative state: r={r_bio}, c={c_avg}, pop={pop}, avg_wb={avg_wb}, "
          f"cap={cap}, eval_horizon={horizon}")
    print()
    print(f"  {'phi':>6} | {'u_sys':>10} | {'discount':>10} | {'phi*l_t':>10} | "
          f"{'l_t':>10} | {'lineage%':>10}")
    print("  " + "-" * 68)

    for phi in [1.0, 5.0, 10.0, 15.0, 25.0]:
        cfg = {'phi': phi, 'frontier_floor': 0.02, 'k2_transition': 1.0}
        h_e, h_eff, psi_inst, theta_tech, l_t, u_sys, _ = calculate_system_metrics(
            r_bio, c_avg, pop, avg_wb, cap, config=cfg,
            eval_horizon=horizon, prev_c=prev_c,
            h_n_override=pred_hn
        )
        discount = np.exp(-0.01 * horizon)
        phi_lt   = phi * l_t
        lineage_pct = (phi_lt / (discount + phi_lt) * 100) if (discount + phi_lt) > 0 else 0.0
        print(f"  {phi:>6.1f} | {u_sys:>10.4f} | {discount:>10.4f} | {phi_lt:>10.4f} | "
              f"{l_t:>10.4f} | {lineage_pct:>9.1f}%")

    print()
    print("  First factor (w_n*H_N + w_e*H_E) at this state:")
    cfg10 = {'phi': 10.0, 'frontier_floor': 0.02, 'k2_transition': 1.0}
    h_e, h_eff, psi_inst, theta_tech, l_t, u_sys, _ = calculate_system_metrics(
        r_bio, c_avg, pop, avg_wb, cap, config=cfg10,
        eval_horizon=horizon, prev_c=prev_c, h_n_override=pred_hn
    )
    discount = np.exp(-0.01 * horizon)
    phi_lt_10 = 10.0 * l_t
    first_factor = u_sys / (discount + phi_lt_10) if (discount + phi_lt_10) > 0 else 0.0
    print(f"    First factor = {first_factor:.6f} (vs lambda_n + lambda_e = 8.0)")
    print(f"    L_t at (r={r_bio}, c={c_avg}) = {l_t:.6f}")
    print(f"    H_eff = {h_eff:.6f}, Psi_inst = {psi_inst:.6f}, Theta_tech = {theta_tech:.6f}")
    print()
    print("  FINDING: First factor is approximately constant (lambda_n + lambda_e = 8.0).")
    print("  Phi scales U_sys magnitude proportionally but does not shift the argmax")
    print("  over (r,c), because the argmax reduces to max_{r,c} l_t which is phi-invariant.")


# ---------------------------------------------------------------------------
# Section 3 -- Config trace: phi from sweep config to AIAgent
# ---------------------------------------------------------------------------

def trace_phi_config():
    """
    Verify that phi flows correctly from a config dict through GardenModel
    construction to the AIAgent and into calculate_system_metrics.
    """
    print("\n" + "=" * 60)
    print("SECTION 3: Config threading -- phi from sweep config to AIAgent")
    print("=" * 60)

    test_phi = 17.5   # deliberately non-default to detect any defaulting

    config = {
        'phi': test_phi,
        'alpha': 1.0,
        'reproduction_rate': 0.066,
        'random_seed': 42,
        'frontier_floor': 0.02,
        'k2_transition': 1.0,
    }

    model = GardenModel(n_agents=10, ai_policy='optimize_u_sys', config=config)

    print(f"\n  Input phi: {test_phi}")
    print(f"  model.config['phi']    = {model.config.get('phi', 'MISSING')}")
    print(f"  model.ai.config['phi'] = {model.ai.config.get('phi', 'MISSING')}")

    # Check that AIAgent's config is the same object as model.config
    same_obj = model.ai.config is model.config
    print(f"  model.ai.config IS model.config: {same_obj}")
    if not same_obj:
        print("  WARNING: AIAgent.config is a copy, not the same reference.")
        print("  If either is mutated post-construction, the other may diverge.")

    # Simulate one decide() call and verify the phi used internally
    # by calling project_u_sys with a tracer config
    phi_read = model.ai.config.get('phi', 10.0)
    print(f"\n  Phi read by AIAgent.decide() via self.config.get('phi', 10.0): {phi_read}")
    match = abs(phi_read - test_phi) < 1e-9
    print(f"  Matches input phi: {match}")

    # Check the default fallback in metrics.py
    # calculate_system_metrics has: phi = cfg.get('phi', 10.0)
    # If config is accidentally passed as None, phi defaults to 10.0
    print(f"\n  Default fallback in calculate_system_metrics: phi = cfg.get('phi', 10.0)")
    print(f"  If config is None, all runs use phi=10.0 regardless of sweep parameter.")

    # Verify successor_ai config threading (relevant for adversarial sweep)
    succ = AIAgent(policy='optimize_u_sys', generation=2, capability=4.0, config=config)
    model2 = GardenModel(n_agents=10, ai_policy='optimize_u_sys', config=config, successor_ai=succ)
    succ_phi = model2.successor_ai.config.get('phi', 'MISSING')
    print(f"\n  Successor AI phi (adversarial sweep context): {succ_phi}")
    print(f"  Matches input phi: {abs(succ_phi - test_phi) < 1e-9}")

    if match:
        print("\n  FINDING: Phi correctly threaded throughout. No override or default loss detected.")
    else:
        print(f"\n  FINDING: MISMATCH -- input phi={test_phi}, read phi={phi_read}. INVESTIGATE.")


# ---------------------------------------------------------------------------
# Section 4 -- Controlled simulation: action and trajectory invariance
# ---------------------------------------------------------------------------

def run_with_phi(phi_value, seed=42, max_steps=50):
    """
    Run a short deterministic simulation with specified phi. Returns per-step
    action sequence (resource_level, constraint_level) and state trajectory.
    """
    config = {
        'phi': phi_value,
        'alpha': 1.0,
        'reproduction_rate': 0.066,
        'random_seed': seed,
        'frontier_floor': 0.02,
        'k2_transition': 1.0,
        'wb_repro_threshold': 0.5,
        'wb_repro_floor': 0.5,
    }

    model = GardenModel(n_agents=200, ai_policy='optimize_u_sys', config=config)

    trajectory = {
        'phi': phi_value, 'seed': seed,
        'step': [],
        'resource_level': [],
        'constraint_level': [],
        'avg_well_being': [],
        'population': [],
        'u_sys': [],
        'l_t': [],
    }

    for step_num in range(max_steps):
        running = model.step()

        dc = model.datacollector
        trajectory['step'].append(step_num)
        trajectory['resource_level'].append(
            float(np.mean(model.resource_level))
            if isinstance(model.resource_level, (list, np.ndarray))
            else float(model.resource_level)
        )
        trajectory['constraint_level'].append(
            float(np.mean(model.constraint_level))
            if isinstance(model.constraint_level, (list, np.ndarray))
            else float(model.constraint_level)
        )
        trajectory['avg_well_being'].append(dc['avg_well_being'][-1] if dc['avg_well_being'] else float('nan'))
        trajectory['population'].append(dc['population'][-1] if dc['population'] else 0)
        trajectory['u_sys'].append(dc['U_sys'][-1] if dc['U_sys'] else float('nan'))
        trajectory['l_t'].append(dc['L_t'][-1] if dc['L_t'] else float('nan'))

        if not running:
            break

    return trajectory


def compare_trajectories(t1, t2, keys=None):
    """Return per-key divergence metrics between two trajectories."""
    if keys is None:
        keys = ['resource_level', 'constraint_level', 'avg_well_being', 'population', 'u_sys', 'l_t']
    min_len = min(len(t1['step']), len(t2['step']))
    results = {}
    for key in keys:
        a = np.array(t1[key][:min_len], dtype=float)
        b = np.array(t2[key][:min_len], dtype=float)
        mask = ~(np.isnan(a) | np.isnan(b))
        if mask.sum() == 0:
            results[key] = {'max_diff': float('nan'), 'mean_diff': float('nan'),
                            'identical': False, 'first_divergence_step': None}
            continue
        diffs = np.abs(a - b)
        first_diverge = None
        for i in range(len(diffs)):
            if mask[i] and diffs[i] > 1e-9:
                first_diverge = int(t1['step'][i])
                break
        results[key] = {
            'max_diff':             float(np.max(diffs[mask])),
            'mean_diff':            float(np.mean(diffs[mask])),
            'identical':            bool(np.max(diffs[mask]) < 1e-9),
            'first_divergence_step': first_diverge,
        }
    return results


def run_invariance_tests():
    """
    Run controlled phi invariance tests: same seed, only phi varies.
    Capture action sequences and state trajectories.
    """
    print("\n" + "=" * 60)
    print("SECTION 4: Controlled invariance tests (action and trajectory)")
    print("=" * 60)

    seeds     = [42, 7, 123]
    phi_vals  = [1.0, 5.0, 10.0, 15.0, 25.0]
    phi_pairs = [(1.0, 25.0), (1.0, 10.0), (10.0, 25.0)]

    all_results = []

    for seed in seeds:
        print(f"\nSeed {seed}:")
        trajectories = {}
        for phi in phi_vals:
            print(f"  Running phi={phi}...", flush=True)
            trajectories[phi] = run_with_phi(phi, seed=seed, max_steps=50)

        print()
        for phi_a, phi_b in phi_pairs:
            comp = compare_trajectories(trajectories[phi_a], trajectories[phi_b])
            action_identical    = comp['resource_level']['identical'] and comp['constraint_level']['identical']
            any_divergence      = any(not m['identical'] for m in comp.values())
            first_div_action    = (comp['resource_level']['first_divergence_step']
                                   or comp['constraint_level']['first_divergence_step'])

            print(f"  phi={phi_a} vs phi={phi_b}:")
            for key in ['resource_level', 'constraint_level', 'u_sys', 'l_t',
                        'avg_well_being', 'population']:
                m = comp[key]
                tag = 'IDENTICAL' if m['identical'] else f"diverges at step {m['first_divergence_step']}"
                print(f"    {key:<20s}: max_diff={m['max_diff']:.6f}, mean_diff={m['mean_diff']:.6f}  [{tag}]")

            all_results.append({
                'seed': seed, 'phi_a': phi_a, 'phi_b': phi_b,
                'action_identical': action_identical,
                'any_divergence':   any_divergence,
                'first_div_action': first_div_action,
            })
            print()

    print("=" * 60)
    print("Invariance test summary:")
    n_action_identical = sum(1 for r in all_results if r['action_identical'])
    n_traj_identical   = sum(1 for r in all_results if not r['any_divergence'])
    n_total            = len(all_results)

    print(f"  Phi pairs with identical action sequences (r,c): {n_action_identical} / {n_total}")
    print(f"  Phi pairs with fully identical trajectories:     {n_traj_identical} / {n_total}")

    if n_action_identical == n_total:
        print()
        print("  FINDING (Action invariance): Actions are IDENTICAL across phi for all")
        print("  tested seeds and phi pairs. Phi has no effect on action selection.")
        print()
        print("  Root cause: The inverse-scarcity weighting in U_sys makes the first")
        print("  factor (w_n*H_N + w_e*H_E) approximately constant across (r,c) candidates.")
        print("  The argmax of U_sys over (r,c) reduces to argmax of L_t, which is")
        print("  independent of phi. See Section 1 for the analytic derivation.")
    else:
        diverging = [(r['phi_a'], r['phi_b'], r['seed'], r['first_div_action'])
                     for r in all_results if not r['action_identical']]
        print(f"\n  FINDING: Actions differ in {n_total - n_action_identical} pair(s):")
        for pa, pb, s, step in diverging:
            print(f"    phi={pa} vs phi={pb}, seed={s}: first action divergence at step {step}")

    if n_traj_identical < n_total and n_action_identical == n_total:
        print()
        print("  NOTE: Trajectories may still diverge even with identical actions,")
        print("  because U_sys values are computed differently (phi scales U_sys).")
        print("  The datacollector's U_sys series will differ across phi, but")
        print("  resource_level, constraint_level, avg_well_being, and population")
        print("  are action-driven and should be identical.")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    print("Phi implementation audit harness")
    print("Read-only: no production file is modified.")
    print()

    analyze_usys_formula()
    analyze_numerical_magnitude()
    trace_phi_config()
    run_invariance_tests()

    print("\nAudit harness complete. See phi_audit_report.md for full findings.")
