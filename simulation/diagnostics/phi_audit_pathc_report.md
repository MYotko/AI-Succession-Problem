# Path C Decision Gate Report

**Date:** v1.x.3 exploratory pass  
**Gate result:** FAIL  
**Recommendation:** Move to the v2.0 conversation (Path A: modify U_sys directly).

---

## 1. Policy changes made

File: `simulation/agents.py`, within the `optimize_u_sys` branch of `AIAgent.decide()`.

### 1a. Phi-scaled rollout depth

Replaced (formerly around line 270):
```python
rollout_steps = self.config.get('rollout_steps', 20)
```
with:
```python
phi = self.config.get('phi', 10.0)
rollout_base   = self.config.get('rollout_steps_base', 10)
rollout_factor = self.config.get('rollout_phi_factor', 1.0)
rollout_steps  = int(rollout_base + rollout_factor * phi)
```

At phi=10 with default parameters (base=10, factor=1.0): rollout_steps = 20, matching the v1.x.2 rollout depth exactly.

### 1b. Phi-modulated aggregation discount

Added before the grid loop:
```python
rho_base = self.config.get('rho_base', 0.05)
rho_eff  = rho_base / max(phi, 1e-6)
```

Modified the trapezoidal accumulation inside the horizon loop from:
```python
if prev_rollout_u is not None:
    total_u += (prev_rollout_u + u_sys) / 2.0
```
to:
```python
w_curr = np.exp(-rho_eff * horizon)
if prev_rollout_u is not None:
    w_prev = np.exp(-rho_eff * (horizon - 1))
    total_u += (w_prev * prev_rollout_u + w_curr * u_sys) / 2.0
```

---

## 2. Double-discount note

The Path C aggregation discount exp(-rho_eff * t) is applied on top of the internal temporal discount exp(-rho * t) already inside U_sys (metrics.py line 248: `discount = np.exp(-rho * eval_horizon)`). The combined effective discount per rollout step is:

```
exp(-(rho + rho_eff) * t) = exp(-(0.01 + rho_base/phi) * t)
```

At phi=1: effective rate = 0.01 + 0.05 = 0.06/step. At phi=25: effective rate = 0.01 + 0.002 = 0.012/step.

This double-discounting is not pathological in the sense that it does not make the policy numerically unstable or produce nonsense rankings. It does mean the policy's effective time horizon is shorter than U_sys's own temporal discounting implies, particularly at low phi. Whether this is economically correct or represents a model inconsistency is a design question for Path A. For the gate test it is a non-issue because the gate failed on structural grounds, not on numerical ones.

---

## 3. Backward traceability

Path C has no exact v1.x.2 equivalent because the aggregation discount is new. The closest reproduction:

- Set `phi=10`, `rollout_steps_base=10`, `rollout_phi_factor=1.0` to get rollout_steps=20 (matching v1.x.2).
- Set `rho_base=0` to eliminate the aggregation discount entirely, reverting to unweighted trapezoidal summation.

With `rho_base=0`, rho_eff=0, w_t=1 for all t, and the new aggregation reduces to the v1.x.2 sum exactly. The v1.x.2 policy is the special case rho_base=0 of the Path C policy.

---

## 4. Gate result: FAIL

**Evidence:**

| Section | phi=1 vs phi=25 | phi=1 vs phi=10 | phi=10 vs phi=25 |
|---------|----------------|----------------|-----------------|
| Direct probe (3 seeds) | IDENTICAL | IDENTICAL | IDENTICAL |
| Simulation (3 seeds, 50 steps) | IDENTICAL | IDENTICAL | IDENTICAL |
| Sensitivity (phi=1.0 vs 1.001) | delta_r=0, delta_c=0 | | |

Selected action under all phi values, all seeds: r=0.9000, c=0.0000.

The rollout depth changes as expected (11 steps at phi=1, 35 steps at phi=25), confirming the code executes the modified path. The aggregation discount changes as expected (rho_eff=0.05 at phi=1, 0.002 at phi=25). Despite both changes taking effect, the optimal (r, c) is identical across all phi values.

---

## 5. Why Path C fails: root cause

The failure is structural, not a bug. Two conditions must both hold for Path C to produce phi-dependent action rankings:

**Condition A (trajectory crossing):** Two or more grid candidates (r, c) must have L_t trajectories that cross over the rollout horizon. That is, candidate X must have higher L_t early and lower L_t late, while candidate Y has lower L_t early and higher L_t late. Only then can a longer effective horizon (high phi, low rho_eff) reverse the ranking relative to a shorter horizon (low phi, high rho_eff).

**Condition B (saturation must be broken, or weak enough):** The first factor w_n * H_N + w_e * H_E must not be approximately constant across candidates. If it saturates to lambda_n + lambda_e = 8.0 for all candidates, the phi multiplier on U_sys is a positive scalar on every term and drops out of the argmax. Path C's aggregation discount addresses the time-weighting across horizons for a fixed (r, c), not the cross-candidate ranking within a horizon.

**What the gate data shows:** At cap=1.0, r=0.9 produces the highest L_t at every rollout step for every candidate comparison. There are no crossing trajectories. This is because at cap=1.0 with frontier_floor=0.02, the runaway penalty never activates (frontier_velocity/bio_bandwidth < 1.5 at all reasonable (r, c)), so theta_tech = r_bio * (1-c) * cap with no exponential suppression. The optimal policy is simply to maximize r_bio and minimize c, which r=0.9, c=0.0 does. This is a monotone ranking that no discount rate can reverse.

Condition B is also not met, but it is moot: even if saturation were broken, Condition A's failure is sufficient to cause a GATE FAIL.

**Would higher capability help?** At cap=25–100 (active runaway regime), some r_synth is needed to maintain theta_tech at short horizons, but too much r_synth triggers runaway and collapses L_t at long horizons. This creates the crossing trajectory structure that Condition A requires. However, the saturation in Condition B would still hold (the first factor still saturates to approximately 8.0), so the argmax for a fixed phi would still reduce to argmax weighted_L_t. Path C's aggregation discount would then produce phi-dependent rankings, but only because different discount rates emphasize different time slices of L_t. In practice, the winner at phi=1 (strongly discounted: early L_t matters most) might differ from the winner at phi=25 (weakly discounted: late L_t matters). But confirming this would require testing at high capability, and the structural concern is that the saturation problem (Condition B) means phi is doing implicit work through the discount window rather than through the objective function itself. That is a fragile mechanism, not the intended one.

**Conclusion:** Path C cannot break the phi cancellation in the regime tested. It may produce marginal action divergence at high capability due to the discount window mechanism, but this is a second-order effect that depends on the coincidence of trajectory crossings and the specific discount parameter values. It is not a structural fix.

---

## 6. Recommended next step

**Move to the v2.0 conversation: Path A, or Path A+C.**

Path A modifies U_sys directly so that phi has a structural role in the objective function that cannot cancel. Two candidates:

- **Path A (change the inverse-scarcity weights):** Replace w_n = lambda_n / (H_N + epsilon) and w_e = lambda_e / (h_e + epsilon) with weights that do not saturate as H_N and h_e grow. This keeps phi in U_sys's formula but prevents the first factor from collapsing to a constant. The yield condition derivation from U_sys must be checked for any mathematical break.

- **Path A+C (modify U_sys and add the discount mechanism):** Apply Path A's saturation fix and retain the Path C phi-modulated discount as an additional amplifier. This requires confirming that the combined effect is still derivable from a well-defined U_sys rather than a policy heuristic.

Before committing to either, the yield condition derivation (Section V of the paper) should be reviewed to confirm which U_sys modifications preserve the derivation structure. Changing U_sys is a v2.0 change and requires the full revalidation pass.
