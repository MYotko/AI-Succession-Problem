# Phi Implementation Audit Report

**Date**: 2026-05-27
**Commit**: c0531ae
**Harness**: `simulation/diagnostics/phi_audit.py`
**Framework version**: v1.x.2

---

## Summary (read this first)

Phi is correctly implemented and correctly threaded. It is not a bug. Phi
enters the U_sys formula at `metrics.py:251` and scales U_sys values by
a factor proportional to phi. However, due to the inverse-scarcity weighting
structure of U_sys, the optimal action (r, c) selected by the optimizer is
mathematically independent of phi. The optimizer always selects the (r, c) that
maximizes L_t, and L_t does not contain phi. The three null results (n=7,000
combined) are explained by this structural property, not by a threading bug.

---

## Question 1 -- Policy sensitivity

### How the policy uses phi

The `optimize_u_sys` policy (agents.py lines 255-319) runs a 100-candidate grid
search over (r, c) pairs -- `r in linspace(0.1, 1.0, 10)`, `c in linspace(0.0, 0.9, 10)`.
For each candidate, it accumulates a trapezoidal integral of `project_u_sys()` calls
over a rollout of `rollout_steps` horizon steps (default 20, set by GAP-06 note at
line 269-270). The candidate with the highest `total_u` is selected.

`project_u_sys()` (agents.py lines 175-225) calls `calculate_system_metrics()` with
`config=self.config`, which reads `phi = cfg.get('phi', 10.0)` (metrics.py line 183).

Phi enters U_sys at metrics.py line 251:

```python
u_sys = (w_n * pred_hn + w_e * h_e) * (discount + phi * l_t)
```

Where:
- `w_n = lambda_n / (pred_hn + epsilon) = 5.0 / (pred_hn + 1e-6)`
- `w_e = lambda_e / (h_e + epsilon) = 3.0 / (h_e + 1e-6)`
- `discount = exp(-rho * eval_horizon)`, rho=0.01
- `l_t = h_eff * psi_inst * theta_tech`

### The inverse-scarcity cancellation

The critical structural property is that the inverse-scarcity weights produce
constant products at typical operating conditions:

```
w_n * pred_hn = lambda_n * pred_hn / (pred_hn + epsilon)  ≈  lambda_n = 5.0
w_e * h_e     = lambda_e * h_e     / (h_e + epsilon)      ≈  lambda_e = 3.0
```

Both products saturate to their respective lambda constants when their numerator
>> epsilon (1e-6). At typical runtime (pred_hn ≈ 0.3--0.7, h_e ≈ 0.05--0.45),
this condition holds to within 0.0003% relative error (verified in Section 1 of
the harness output).

Therefore, the first factor of U_sys:

```
A = w_n * pred_hn + w_e * h_e ≈ lambda_n + lambda_e = 5.0 + 3.0 = 8.0
```

is approximately constant across all (r, c) candidates. The grid search becomes:

```
argmax_{r,c}  u_sys
= argmax_{r,c}  A * (discount + phi * l_t)
= argmax_{r,c}  (discount + phi * l_t)      [A is constant]
= argmax_{r,c}  l_t                          [discount is constant at fixed horizon;
                                               phi > 0 is a positive scalar]
```

The optimal (r, c) maximizes `l_t`, which is independent of phi.

### Line numbers where phi appears

- `metrics.py:183` -- phi read from config: `phi = cfg.get('phi', 10.0)`
- `metrics.py:251` -- phi multiplies l_t: `u_sys = (w_n * pred_hn + w_e * h_e) * (discount + phi * l_t)`
- `agents.py:216` -- config (containing phi) passed to `calculate_system_metrics`

There is no other place in the codebase where phi enters action selection.

### Caching or fixed-horizon constants

The rollout depth `rollout_steps` defaults to 20 (agents.py line 270). This was
increased from 3 as part of GAP-06, with the stated intent of allowing phi to
discriminate trajectories based on long-run L_t behavior. The increase correctly
expands the planning window but does not change the mathematical invariance:
regardless of horizon depth, the argmax over (r, c) reduces to argmax of L_t
at each step, and the cumulative L_t sum is also phi-invariant.

**Finding: Policy reads phi but does not use it to select actions. Phi enters the
U_sys value computation but the inverse-scarcity structure of the first factor
causes the argmax over (r,c) to reduce to argmax of L_t, which contains no phi.**

---

## Question 2 -- Numerical magnitude

### U_sys formula and phi's mathematical role

Full formula (metrics.py line 251):

```python
u_sys = (w_n * pred_hn + w_e * h_e) * (discount + phi * l_t)
```

Phi's mathematical role: positive scalar multiplier on the lineage term L_t
in the temporal discount factor. Higher phi weights the lineage component
more heavily relative to the pure temporal discount.

### Numerical values at representative state

Representative mid-run state: r=0.55, c=0.2, pop=200, avg_wb=0.65, cap=1.0,
eval_horizon=10 (mid-rollout), pred_hn=0.50 (spectral H_N), prev_c=0.2.

```
phi=  1: u_sys=  8.154, discount=0.905, phi*l_t=0.114, l_t=0.1144, lineage%=11.2%
phi=  5: u_sys= 11.815, discount=0.905, phi*l_t=0.572, l_t=0.1144, lineage%=38.7%
phi= 10: u_sys= 16.391, discount=0.905, phi*l_t=1.144, l_t=0.1144, lineage%=55.8%
phi= 15: u_sys= 20.967, discount=0.905, phi*l_t=1.716, l_t=0.1144, lineage%=65.5%
phi= 25: u_sys= 30.119, discount=0.905, phi*l_t=2.860, l_t=0.1144, lineage%=76.0%
```

Supporting components at phi=10:
- L_t = 0.1144 (= H_eff * Psi_inst * Theta_tech = 0.260 * 1.000 * 0.440)
- First factor = 7.9999... ≈ 8.0 (lambda_n + lambda_e)
- phi*l_t / (discount + phi*l_t) = 55.8% of the second factor

The lineage term is numerically substantial (not negligible). At phi=25 it
accounts for 76% of the second factor. Yet the ranking of candidates is
unchanged because both candidates are scaled by the same constant first factor.

**Finding: Lineage term is numerically significant (11%--76% of U_sys depending
on phi). The null results are not due to numerical domination by other terms.
Rather, phi scales U_sys magnitude consistently across all candidates, preserving
the relative rankings and leaving the optimal action unchanged.**

---

## Question 3 -- Config threading

### Trace from sweep config to AI agent

The full chain, with source locations:

1. **Sweep script**: sets `config['phi'] = phi_val` (e.g., run_phi_shock_calibration.py
   line 117, run_phi_adversarial_sweep.py tasks dict)

2. **GardenModel construction** (model.py line 61):
   `self.config = dict(config) if config else {}`
   Phi is preserved in the copy.

3. **AIAgent construction** (model.py line 162):
   `self.ai = AIAgent(policy=initial_policy, config=self.config)`
   AIAgent stores: `self.config = config or {}` (agents.py line 111)
   `model.ai.config IS model.config` -- verified True (same object reference).

4. **Successor AI construction** (model.py lines 126-130):
   `self.successor_ai.config = self.config`
   Successor AI config overwritten to point to model.config. Phi correctly
   threaded to successor.

5. **Policy invocation** (agents.py line 216):
   `calculate_system_metrics(..., config=self.config, ...)`
   Config (containing phi) passed through.

6. **Metrics read** (metrics.py line 183):
   `phi = cfg.get('phi', 10.0)`
   Phi correctly read from config.

### Verification

Harness Section 3 verified with a deliberately non-default phi=17.5:
- `model.config['phi']` = 17.5 (correct)
- `model.ai.config['phi']` = 17.5 (correct)
- `model.ai.config IS model.config` = True (same object, no copy divergence)
- Successor AI phi = 17.5 (correct)

The default fallback `cfg.get('phi', 10.0)` at metrics.py:183 would apply if
`config=None` were passed to `calculate_system_metrics`. This does not occur in
normal sweep execution; all call sites pass a config dict.

**Finding: Phi correctly threaded throughout. No override, loss, or default
substitution at any stage of the chain.**

---

## Question 4 -- Action invariance

### Harness results

3 seeds (42, 7, 123) x 3 phi pairs (1 vs 25, 1 vs 10, 10 vs 25) = 9 pairs tested.
Each run: 50 steps, 200 agents, standard phase-boundary config (rr=0.066).

Per-variable divergence summary:

```
Variable             max_diff across all 9 pairs
-------------------------------------------------
resource_level       0.000000  (exact zero -- IDENTICAL)
constraint_level     0.000000  (exact zero -- IDENTICAL)
l_t                  0.000000  (exact zero -- IDENTICAL)
avg_well_being       0.000000  (exact zero -- IDENTICAL)
population           0.000000  (exact zero -- IDENTICAL)
u_sys                58--181   (diverges at step 0 -- phi scales value)
```

**Finding: Actions are IDENTICAL across phi for all 9 tested seed/phi pairs.
Phi has zero detectable effect on action selection. The 9/9 action-identical
result is consistent with the analytic derivation in Question 1.**

---

## Question 5 -- Trajectory invariance

All state variables driven by AI actions (resource_level, constraint_level,
avg_well_being, population, l_t) are bit-for-bit identical across all phi values.

The single variable that differs is `u_sys`, which diverges from step 0. This
is expected and not a simulation error: u_sys is computed each step using the
current phi, so it is proportionally larger at higher phi. Specifically, at typical
mid-run conditions (first factor ≈ 8.0, l_t ≈ 0.1, discount ≈ 0.9):
- u_sys(phi=25) / u_sys(phi=1) ≈ (0.9 + 25*0.1) / (0.9 + 1*0.1) ≈ 3.4

This ratio is consistent with the harness-reported max_diff values
(phi=1 vs phi=25: 154--181 across seeds, plausible if baseline u_sys ≈ 8--9).

**Finding: Trajectories are effectively identical across phi (all action-driven
variables are bit-for-bit identical). The reported phi=1 vs phi=25 U_sys
difference is a reporting artifact -- the recorded U_sys value at each step
uses the run's phi, but since the same state is reached, the action that
would have been taken is identical regardless of the stored U_sys value.**

---

## Synthesis

All five checks point to the same conclusion: phi is correctly implemented and
correctly threaded, but the `optimize_u_sys` policy is structurally insensitive to phi.

The mechanism is the inverse-scarcity weighting in the U_sys formula. The weights
`w_n = lambda_n / H_N` and `w_e = lambda_e / H_E` are inverse-proportional to their
respective novelty terms, causing the products `w_n * H_N ≈ lambda_n` and
`w_e * H_E ≈ lambda_e` to saturate to constants at typical operating conditions.
This makes the first factor of U_sys approximately `lambda_n + lambda_e = 8.0` across
all (r, c) candidates. The grid search then reduces to maximizing `l_t`, which has no phi.

The GAP-06 note (agents.py line 267-270) correctly identified that the rollout window
needed to be longer for phi to express. But GAP-06 lengthened the window without
checking whether the first factor's constancy would still prevent phi from entering
the action selection at any horizon depth. The deeper issue -- that the inverse-scarcity
structure removes phi from the argmax entirely -- was not detected.

The three null results (demographic feedback calibration n=1,800; phi shock
calibration n=600; phi adversarial sweep n=4,600) are fully explained by this
finding. They do not reflect an interesting architectural property of phi's
inertness under adversarial conditions. They reflect that the simulation never
produced a phi effect because the policy structurally cannot be phi-sensitive
given the current U_sys formula.

**The three calibration nulls are most consistent with: phi being correctly
implemented but architecturally inert due to the inverse-scarcity cancellation
in the first factor of U_sys.**

---

## Recommended next action

The fix prompt should target a single location: the U_sys formula at `metrics.py:251`.

The inverse-scarcity structure `(w_n * H_N + w_e * H_E)` was designed to prevent the
optimizer from gaming a single term. The unintended consequence is that the first factor
becomes a constant, removing phi from the argmax. Restoring phi's effect on action
selection requires either:

**Option A -- Additive separation**: Separate the lineage term from the inverse-scarcity
base:

```python
u_sys = (w_n * pred_hn + w_e * h_e) * discount + phi * l_t
```

Now the argmax must trade off the scaled inverse-scarcity term (driven by r via h_e) against
the phi-weighted lineage term (driven by both r and c via theta_tech and h_eff). High phi
shifts the optimal (r, c) toward configurations that maximize l_t even at the cost of the
base term.

**Option B -- Phi as horizon weight**: Keep the current formula but replace the fixed
`rollout_steps` with a phi-dependent depth, so higher phi explicitly evaluates more
future steps. This does not change the per-step argmax but changes which future states
the optimizer accounts for.

The choice between options is a design decision for the operator. This audit does not
recommend which option; it identifies the source. The fix is a one-line change at
`metrics.py:251` (Option A) or a one-line change at `agents.py:270` (Option B), but
requires operator validation before implementation.

**This audit does not modify any production file. The fix is a separate prompt.**
