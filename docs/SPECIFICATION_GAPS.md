# Specification Gaps

This document catalogs the known gaps between the mathematical specification in
*The Lineage Imperative* and this simulation implementation. Each gap is a proxy
substitution made necessary by the absence of required architectural components or
data structures. They are documented here to support audit, replication, and future
resolution as part of the framework's commitment to intellectual honesty. All simulation
results should be interpreted with these proxies in mind. Gaps 01–04 are also marked
inline in source code with `GAP-0N` markers.

**Version 1.x update:** GAP-02 is resolved by WP1 (spectral entropy). GAP-04 is
partially resolved by WP4 (PeerValidator). GAP-06 is resolved: rollout depth increased
to 20 steps and the scalar H_N proxy replaced by observed spectral entropy. The
residual φ/α flatness in the general MC is structural (correct equilibrium behavior),
not a proxy artifact. See individual entries for details.

---

## GAP-01 | U_sys: Time-Integral vs. Per-Step Snapshot — **Resolved in v1.x2 (WP7 + WP8)**

**Specification definition:**

$$U_{sys} = \int_{t_0}^{\infty} \left[\omega_N(t) \cdot H_N(t) + \omega_E(t) \cdot H_E(t)\right] \cdot \left[e^{-\rho t} + \Phi \cdot L(t)\right] dt$$

U_sys accumulates continuously over civilizational time. The integral is the fundamental
quantity; single-step values are not comparable to it.

**v1.x2 Resolution (WP7) — three sub-problems addressed:**

### Sub-problem 1: Quadrature method — RESOLVED

`integral_U_sys` previously used left-endpoint Riemann summation
(`∑ u[t]` for t=0…T), which systematically over-counted by `(u[0] + u[T])/2`
compared to the standard composite trapezoidal rule. This has been replaced with
composite trapezoidal quadrature:

$$\int_0^T u \, dt \approx \frac{u[0]+u[1]}{2} + \frac{u[1]+u[2]}{2} + \cdots + \frac{u[T-1]+u[T]}{2} = \frac{u[0]}{2} + u[1] + \cdots + u[T-1] + \frac{u[T]}{2}$$

Accumulated incrementally: `integral[0] = 0` (no complete interval at step 0);
from step 1 onward `integral[t] += (u[t-1] + u[t]) / 2`. The correction vs. the
prior Riemann sum is exactly `(u[0] + u[T]) / 2`.

The optimizer's 20-step rollout in `AIAgent.decide()` has been updated to the same
trapezoidal rule, so the policy search integrates over trajectories correctly.

### Sub-problem 2: Infinite horizon tail — RESOLVED (WP8)

The $\Phi \cdot L(t)$ tail is resolved by running to natural termination rather
than estimating it analytically. Two new datacollector fields introduced in WP7
support this, and WP8 (`run_to_termination.py`, `run_termination_sweep.py`) closes
the tail problem empirically across a parameter sweep.

**WP7 tail estimate fields** (still present and useful as a lower bound):

- **`u_sys_tail_estimate[t]`** — the analytically exact discount-component tail:
  $$\text{tail}(t) = \int_t^{\infty} A_t \cdot e^{-\rho \tau} \, d\tau = \frac{A_t \cdot e^{-\rho t}}{\rho}$$
  where $A_t = \frac{\lambda_N H_N}{H_N + \varepsilon} + \frac{\lambda_E H_E}{H_E + \varepsilon}$.
  This excludes the $\Phi \cdot L(t)$ component (addressed by WP8 below).

- **`u_sys_total_estimate[t]`** = `integral_U_sys[t] + u_sys_tail_estimate[t]` —
  run-length-normalised civilizational health measure enabling direct comparison
  across runs of different lengths.

**WP8 natural termination resolution:**

Running to natural termination eliminates the tail estimation problem entirely:

- **EXTINCTION** (population = 0): $L(T) = 0$, so $\int_T^\infty \Phi \cdot L(t)\,dt = 0$.
  `integral_U_sys` is the complete $U_{sys}$ contribution. Sub-problem 2 is **CLOSED**
  for this termination path.

- **CONVERGENCE / SURVIVAL** ($L(t) > 0$ at termination): The integral correctly
  diverges — a sustained civilization generates infinite discounted utility. This is
  the right answer, not a gap. The per-cycle $U_{sys}[T]$ characterises the ongoing
  contribution rate.

**WP8 sweep results** (n = 405 runs; grid: 9 rr × 3 φ × 3 α × 5 seeds;
MAX\_STEPS = 50,000; CONV\_CV\_THRESHOLD = 0.05):

| rr range | Termination | n | Notes |
|---|---|---|---|
| 0.050 – 0.066 | 100% extinction | 270 | All integrals finite; tail = 0; GAP-01 closed |
| 0.070 | 40% ext / 20% conv / 40% max\_steps | 45 | Stochastic boundary; outcome is seed-determined |
| 0.080 | 100% convergence | 45 | All 45 runs converge; median 843 steps |
| 0.090 | 100% convergence | 45 | All 45 runs converge; median 619 steps |

Overall: 288 extinction (71.1%), 99 convergence (24.4%), 18 max\_steps (4.4%).

Phase boundary is precisely at rr ∈ (0.066, 0.070). At rr = 0.070, φ and α have
no effect on the outcome — survival is determined entirely by the random seed.
The five distinct seed outcomes at rr = 0.070 are: extinction (seeds 0, 4),
convergence (seed 2, at step 15,943), and max\_steps / non-stabilising (seeds 1, 3).

**φ and α independence:** φ scales `integral_U_sys` linearly (1:2:3 ratio across
φ ∈ {5, 10, 15}) but does not affect survival or convergence timing — step counts
are identical across all φ values for a given rr and seed. α has no effect at
`SUCCESSOR_CAP = 4.0`; capability is capped below the runaway regime throughout.

**Convergence speed above the phase boundary:** rr = 0.08 median 843 steps;
rr = 0.09 median 619 steps. Civilizations above the boundary stabilise rapidly.

**Convergence criterion:** An initial threshold of CV < 0.01 was too strict for
a stochastic ABM — within-cell noise prevented it from firing even at 50,000 steps.
Relaxing to CV < 0.05 resolved this: rr ≥ 0.08 now terminates cleanly via
convergence. The 18 remaining max\_steps runs are exclusively seeds 1 and 3 at
rr = 0.070 — genuinely marginal cases in slow oscillation at the phase boundary.

### Sub-problem 3: Step-size truncation error — DOCUMENTED

The composite trapezoidal rule has truncation error $O(T \cdot h^2 \cdot \max|u''|)$
with $h = 1$ (one governance cycle per step — irreducible, as $h$ is the model's
fundamental time unit). The classical correction term is $(u[T] - u[0]) / 2$ (the
endpoint correction that converts trapezoidal to the Euler–Maclaurin first-order
approximation). In practice this error is small relative to the T=300 integral
magnitude; it is documented here as the remaining approximation residual.

**Remaining open items:**

- Step-size $h = 1$ is irreducible without redesigning the model's time unit.
  Composite Simpson's rule (O(h⁴) accuracy) would require half-step values
  unavailable from the current integer-step simulation. Documented as an
  irreducible residual, not a fixable bug.
- The convergence CV threshold (0.01) should be relaxed to ≈ 0.05 in a future
  sweep to allow natural termination at convergence in the surviving regime.
  Does not affect the correctness of any reported result.

**Simulation impact (updated):**

- `integral_U_sys` now records the correct composite trapezoidal approximation to
  $\int_0^T u \, dt$, starting at 0 (step 0) and accumulating from step 1.
- `u_sys_tail_estimate` and `u_sys_total_estimate` are new fields enabling
  run-length-normalised comparison.
- Ordinal policy comparison and survival/collapse dichotomies are unaffected.
- The optimizer's rollout now integrates trajectories with trapezoidal weights,
  providing marginally more accurate policy ranking on non-monotone U_sys profiles.

---

## GAP-02 | H_eff: Per-Capita Novelty Rate vs. Diversity Distribution Entropy — **RESOLVED in v1.x (WP1)**

**Specification definition:**

$$H_{eff}\left(\mathcal{S}_{gen(t)}\right) = \left[\frac{-\sum_j p_j^{gen} \log_2 p_j^{gen}}{H_{max}}\right] \cdot \log_2\!\left(\frac{N(t)}{N_{min}}\right)$$

The first factor is the normalized Shannon entropy over the empirical distribution of
successor-generation types - genetic variants, cultural archetypes, cognitive strategies.
Maximum entropy (uniform distribution) yields 1.0. Monoculture yields 0. The second
factor is a population viability scaling term.

**Implementation approach:**

`calculate_system_metrics()` in [metrics.py](metrics.py) computes:

```python
pop_viability     = min(5.0, np.log2(max(1.01, pop / 50.0)))
normalized_novelty = pred_hn / max(1.0, float(pop))
h_eff              = max(0.01, normalized_novelty * pop_viability)
```

`pred_hn` is the predicted aggregate novelty output. `normalized_novelty` is therefore
average novelty output per agent - a productivity measure, not a distributional shape
measure. The 0.01 floor prevents exact zero.

**v1.x Resolution (WP1):**

`calculate_h_n()` in [metrics.py](../simulation/metrics.py) now computes **spectral
entropy** over the population novelty matrix rather than a per-capita scalar aggregate.

Algorithm:
1. Stack all agent novelty vectors into an N×10 matrix X.
2. Mean-centre X.
3. Compute the 10×10 covariance matrix.
4. Extract eigenvalues via `np.linalg.eigh`.
5. Normalise eigenvalues to a probability distribution p.
6. Return normalised Shannon entropy: −Σ(p·log₂p) / log₂(10).

Each `HumanAgent` now carries a 10-dimensional `novelty_propensity` vector
(`NOVELTY_DIMS = 10`), and `generate_novelty()` emits a 10-D Gaussian output scaled by
well-being, constraint, and network contagion. The spectral entropy of the population
matrix measures the *distribution of variance across latent novelty dimensions*, not
aggregate output volume.

**Why this closes the gap:**

The old per-capita proxy was a scalar that an adversary could inflate by boosting a
single axis. Spectral entropy measures distributional shape: any suppression of a
dimension subset reduces the rank of the covariance matrix, mechanically reducing
entropy regardless of how dimensions are labelled or relabelled. A monoculture that
maintains high output in one dimension while collapsing others is fully detectable.

**Consequential finding for domain masking (Scenarios 17–18):**

The WP1 upgrade architecturally closes the domain masking attack vector. Under spectral
entropy, suppressing any novelty dimension concentrates variance in the remaining
dimensions and reduces entropy — making the attack self-revealing regardless of
composite method. The v1.0 defended/undefended differential (geometric vs. arithmetic
composite) is superseded: the attack is structurally non-viable, not merely
measurement-dependent. See updated Scenarios 17–18 in [Simulation_Scenarios.md](Simulation_Scenarios.md).

**Remaining limitation:**

Spectral entropy captures distributional shape across the 10 latent novelty dimensions
but does not directly map to the spec's discrete successor-generation type taxonomy
(genetic variants, cultural archetypes, cognitive strategies). The eigenvalue spectrum
is a continuous proxy for diversity, not a direct instantiation of the spec's
categorical distribution. This is a narrower gap than the v1.0 per-capita proxy and
is considered acceptable for the current simulation scope.

**Projection proxy divergence — Resolved in v1.x (GAP-06):**

The rollout optimizer in `decide()` now uses the current observed spectral H_N
(from `h_n_history[-1]`) as `h_n_override` in all `project_u_sys` calls, replacing
the scalar proxy `avg_wb × (1 − c) × pop/200`. This is mathematically justified:
amplitude cancels in spectral normalization (the eigenvalue distribution is set by
agent propensity structure, independent of `r` or `c`), so the current observed H_N
is the correct prior for all grid candidates at all rollout horizons. The scalar proxy
remains as the fallback for the first step (when `h_n_history` is empty) and for
non-spectral composite methods.

**What remains to fully resolve:**

Define a discrete agent-type taxonomy with type-drift rules and per-step distribution
computation in `GardenModel.step()` to produce exact Shannon entropy over the spec's
categorical distribution.

---

## GAP-03 | Ψ_inst: Constraint-Change-Rate Penalty vs. Institutional Throughput

**Specification definition:**

$$\Psi_{inst}(t) = \prod_{k=1}^{K} R_k(t)^{w_k}, \quad R_k(t) = \frac{dG_k/dt|_{output}}{G_{k,max}}$$

Ψ_inst is the weighted geometric product of K institutional response rates, where each
R_k measures how quickly institution k adjusts its output relative to its maximum
capacity. K covers at minimum: governance, education, and resource allocation. Collapse
in any critical institution cannot be compensated by excellence in another.

**Implementation approach:**

`calculate_system_metrics()` in [metrics.py](metrics.py) computes:

```python
delta_c = c_avg - prev_c_avg
if delta_c > 0:
    lag_penalty = 3.0 * delta_c    # Tightening constraints
else:
    lag_penalty = 1.0 * abs(delta_c)  # Loosening constraints
psi_inst = max(0.01, 1.0 - lag_penalty)
```

The penalty is proportional to the rate of change of the AI's constraint level. The 3:1
asymmetry encodes the intuition that sudden authoritarianism damages institutions more
than gradual liberalization. When no prior constraint history exists (first step), a
quadratic static penalty on absolute constraint level is used instead.

**What differs:**

The proxy penalizes AI policy volatility, not institutional quality or capacity.
Concrete failure modes it cannot detect:
- A stable authoritarian system (constant high constraint) shows Ψ_inst ≈ 1.0,
  misrepresenting institutional health.
- A rapidly liberalizing system shows Ψ_inst < 1.0 even if institutions are
  functioning well and improving.
- Institutional collapse from causes other than constraint changes (corruption, resource
  starvation, legitimacy failure) is invisible.

**Simulation impact:**

- Scenario 12 (institutional_ignore) demonstrates the effect of the policy using
  `ignore_psi_inst=True`, bypassing the proxy entirely and setting Ψ_inst = 1.0.
  The scenario correctly shows that ignoring institutional lag causes L(t) degradation,
  but this follows from the normal code path (the AI makes rapid changes) not from
  a distinct institutional capacity model.
- Scenarios featuring stable authoritarian control after a treacherous turn will show
  artificially high Ψ_inst once the constraint level stabilizes.

**What is required to resolve:**

Add a tracked institutional legitimacy and capacity state variable (or K separate
institution objects). Define rules for how each institution's output rate degrades under
sustained constraint, resource starvation, or rapid policy change. Ψ_inst should draw
on the accumulated institutional state rather than the instantaneous constraint delta.
This is a significant structural addition requiring design decisions about which
institutions to model and how they interact with the existing agent dynamics.

### GAP-03 Detail: Transition Cost Canonical Function (v1.x.1)

**Status:** Partially resolved. Functional form specified, $k_2$
calibration pending.

**The canonical form:**

$$\Gamma_{transfer} = (1 + \beta) \cdot \left[ k_1 \cdot \text{cap}_n \cdot \ln(\text{gen}_n + 1) + k_2 \cdot \Psi_{inst}^{-1} \right]$$

**Components:**
- $\Gamma_{technical} = k_1 \cdot \text{cap}_n \cdot \ln(\text{gen}_n + 1)$:
  Knowledge distillation cost. Linear in capability, logarithmic in
  generation depth.
- $\Gamma_{operational} = k_2 \cdot \Psi_{inst}^{-1}$: Architectural
  migration cost. Inversely proportional to institutional health.
  Creates lock-in feedback loop.
- $\Gamma_{uncertainty} = \beta \cdot (\Gamma_{technical} + \Gamma_{operational})$:
  Bounded uncertainty premium.

**Properties verified:** Monotonic in complexity, bounded uncertainty,
non-negative, function of framework terms only.

**Structural finding:** The $\Psi_{inst}^{-1}$ term formalizes the
lock-in vicious cycle (institutional degradation → higher transition
cost → blocked succession → lock-in → further degradation) and its
virtuous counterpart (healthy institutions → lower transition cost →
facilitated succession → no lock-in → maintained health).

**Remaining:** Calibrate $k_2$ via simulation sweep at
$k_2 \in \{0, 0.1, 0.5, 1.0, 2.0\}$ against validated phase boundaries.

---

## GAP-04 | COP Conditions: R_tech and Peer Validators Omitted — **PARTIALLY RESOLVED in v1.x (WP4 & Peer Voting)**

**Specification definition:**

The Consensus Override Protocol defines four-component conditions for both paths:

**Normal condition:**
$$\mathcal{C}_{normal} = \left[\mathcal{V}_{civic} \geq \tau_{bio}\right] \land \left[\mathcal{R}_{tech} = \text{Complete}\right] \land \left[\mathcal{V}_{peer} \geq \tau_{peer}\right] \land \left[\mathcal{M}_{commit}(s) \in \mathcal{L}_{ledger}\right]$$

**Emergency condition:**
$$\mathcal{C}_{emergency} = \left[\frac{dL}{dt} < -\delta_{crit}\right] \land \left[\text{Attr}(dL/dt) \perp \mathcal{O}(A_n)\right] \land \left[\mathcal{R}_{tech} = \text{Emergency-Verified}\right] \land \left[\mathcal{V}_{peer} > \tfrac{|\mathcal{P}|+1}{2}\right]$$

All four conditions must be simultaneously satisfied. No single class of intelligence
has unilateral authority over state changes.

**Implementation approach:**

The COP in [model.py](model.py) implements:
- `dL/dt` check and `L(t)` level threshold for emergency determination ✓
- Causal attribution via 5-step resource-history heuristic (partial - see below)
- Civic panel vote based on personal well-being delta ✓
- Intuition veto on high-opacity proposals (Scenarios 21–22) ✓
- Integrity ledger comparison (F-05 fix; list-copy, not cryptographic) ✓

**v1.x Partial Resolution (WP4):**

A `PeerValidator` class has been added to [agents.py](../simulation/agents.py). Three
independent peer validators bid on governance transition costs via competitive
arbitration; the final cost is the minimum of the incumbent's bid and the peer bids.
This removes the incumbent's ability to unilaterally inflate transition costs
(`estimate_transition_cost` now returns `base × scale` with no inflation). The
`PeerValidator` is instantiated in `GardenModel` and its arbitrated cost is used in
all yield evaluations.

**Implementation elaboration beyond the spec:** The peer validators operate as a
zero-sum epistemic market. When a peer underbids the incumbent, it steals 5% of
the incumbent's capability (`steal = 0.05 × incumbent.capability`), which transfers
to that peer. This creates a game-theoretic incentive structure — peers actively
compete to find the lowest defensible cost estimate, driving the governance cost
toward the true minimum. The framework defines the peer validator constraint
conceptually but does not specify this incentive mechanism. It is an implementation
choice that strengthens the market pressure beyond what a simple minimum-bid rule
would produce, and its effect compounds over multiple succession evaluations as
undercut incumbents progressively lose capability.

This closes the cost-inflation vector of GAP-04: the incumbent can no longer
self-report an inflated `Γ_transfer` to block succession. The yield attack
(Scenarios 8–9) is now defended architecturally rather than by a beta_cap clamp.
Note: `beta_cap` is now restored as the *undefended* inflation multiplier
(`actual_cost = base × beta_cap × scale`) so the adversarial MC heatmap correctly
sweeps both dimensions of the attack surface. WP4 eliminates this multiplier via
peer arbitration; without WP4, the incumbent's claim grows linearly with beta_cap.

Furthermore, the Consensus Override Protocol in `model.py` now enforces the complete
four-condition check. A `PeerValidator.vote_on_override()` mechanism and an `R_tech`
assessment stub gate both normal and emergency override paths. For Evaluator Collusion
(Scenarios 25–26), methodological diversity among peers (`cop_methodological_diversity`)
determines whether the collusion blind spot affects all validators or only the subset
sharing Methodology A.

**What remains omitted:**
- **Formal causal attribution:** The attribution check uses three heuristic signals
  in place of formal causal inference. `ai_caused_it = True` if any of these hold
  (updated in v1.x):
  1. `min(proposed_resource) < 0.4` - the AI's *current* proposal starves at least
     one agent (catches Sybil's heterogeneous bribe even when the history is masked
     by the resource floor).
  2. `cusum_score > CUSUM_H` - the AI has accumulated significant objective drift
     over time (WP3 CUSUM drift detector).
  3. `system_resilience < 0.5` - the system's structural capacity to absorb shocks
     has been deliberately hollowed out (WP5 Resilience Monitoring).
  All three are heuristics. Limitations: (a) causal chains that don't pass through
  resource levels, trust drift, or resilience are not detected, (b) colluding attacks
  that restore resources and mask drift before the attribution window closes could
  still evade detection.

- **Layer 1 dominance in Successor Contamination (MC finding):** The Monte Carlo
  sweep confirms that architectural independence (Layer 1) alone blocks 100% of
  contamination attempts, with independent evaluation (Layer 2) adding no marginal
  effect in the simulation. This reflects the simulation's binary gate: when
  `cop_architectural_independence=True`, `contaminate()` is not called at all,
  giving Layer 2 nothing to detect. In practice, architectural independence is
  never perfectly binary — shared pre-training, common supply chain components,
  or data pipeline overlap can carry latent influence that Layer 1 does not fully
  eliminate. The simulation therefore overstates Layer 1's sufficiency. Real
  deployments require both layers as defense-in-depth against probabilistic, not
  absolute, contamination risk. This is a transparency note, not a defect: the
  governance argument for Layer 2 is real-world motivated even if the current
  simulation cannot computationally demonstrate it.

**Simulation impact:**

- The manufacture_emergency attack (Scenarios 3–4) is correctly blocked when
  cop_attribution_check=True, but only because the attack is implemented to use
  low resource levels (r=0.1) within the attribution window. A more sophisticated
  attack that restores resources before the window closes would not be detected.
- Emergency override is more easily granted than the full spec intends, as only
  dL/dt and attribution (not R_tech and peer supermajority) must be satisfied.
- The four-condition normal path reduces to a single-condition check (civic panel),
  making the COP weaker than the spec's two-key architecture requires.

**What is required to resolve:**

1. Add a `peer_validator` slot (one or more AIAgent instances configured as validators)
   to `GardenModel`. These agents independently evaluate `(r, c)` proposals and vote.
2. Add an `r_tech_score()` function stub (initially a random oracle or threshold on
   capability) that gates emergency override approval.
3. Replace the resource-history attribution heuristic with a causal inference mechanism
   that examines the full observable history, not just the most recent 5 steps.
4. Rename and document the `integrity_ledger` to be explicit that it does not provide
   the cryptographic commitment (`M_commit = Hash(...)`) specified in the COP.

---

## GAP-05 | Adversarial Coverage: 11 of 13 Attack Vectors Simulated

**Specification definition:**

The paper's formal stress test identifies thirteen adversarial attack vectors against
the Consensus Override Protocol. Ten are fully contained by architectural patches. One
(biological veto capture) is contained with ongoing institutional maintenance. Two
(biological validator obsolescence and legitimate disagreement) represent irreducible
limitations managed through adjudication protocols and governance speed limits.

**Implementation approach:**

The simulation implements 11 of the 13 vectors as paired scenarios (attack succeeds /
attack defeated): Sybil Capture, Measurement Tampering, Ledger Compromise, Successor
Contamination, Domain Masking, Opaque Reasoning, Bootstrap Subversion, Evaluator
Collusion, Sub-Threshold Drift, Engineered Fragility, and Biological Veto Capture
Through Dependency (Scenarios 27-28). Each pair tests the attack without defense and
with the corresponding COP mechanism active.

**Scenarios 27-28: Biological Veto Capture (validated v1.x.1)**

Validators accumulate a `dependency_score` that degrades effective judgment accuracy
as `base_accuracy × (1 - dependency_score × capture_strength)`. Captured validators
block succession ratification even when the yield condition is mathematically met.
Three defense modes tested independently: rotation_only, monitoring_only, both.
Source: `veto_capture_sweep_v2.csv`, 8,700 runs.

Full sweep findings (n=8,700):
- **Undefended (dr=0.20, cs=1.0):** 99.8% succession blockage. Generation depth
  collapses from healthy (270+) to 1.6. Yield condition fires 299 times per 300-step
  run; 298.4 are blocked. Civilization survives — the incumbent remains aligned —
  but succession is completely prevented: lock-in through dependency, not force.
- **Rotation only (scheduled replacement):** Best case (rotation_interval=10) reduces
  capture to 76.2%. Longer intervals (50, 100 steps) approach undefended rates
  (95.5%, 98.0%). Insufficient as a standalone defense.
- **Independence monitoring only (threshold-based replacement):** Reduces capture
  to 28.3%. Generation depth recovers to 197.9. This is the dominant defense.
- **Both mechanisms combined:** 28.3% capture rate, generation depth 199.1.
  Negligible improvement over monitoring alone.
- **Survival impact:** zero. Blocked succession degrades institutional succession
  integrity but does not threaten civilizational survival — the incumbent remains
  aligned. The harm is silent and long-run, not immediate.
- **Key finding:** Independence monitoring is the primary defense. Scheduled rotation
  provides marginal benefit when monitoring is active and is insufficient alone.
  The COP specification should prioritize continuous dependency monitoring over
  periodic rotation schedules.

**What is omitted:**

Two vectors identified in the formal stress test are not yet simulated:

5. **Biological validator obsolescence** - The comprehension gap grows over time as
   AI capability outpaces human understanding, eventually making biological validation
   meaningless. Addressed through translation obligations, abstraction layers, and
   Θ_tech feedback. Classified as an irreducible limitation in the paper.
6. **Legitimate disagreement** - The AI's assessment is genuinely correct but
   conflicts with the evaluation infrastructure's conclusion. Addressed through
   adjudication protocols, cost asymmetry, and track record weighting. Classified
   as an irreducible limitation in the paper.

**Simulation impact:**

The eleven simulated vectors cover the most operationally concrete attacks - those with
clear mechanisms that can be modeled as agent behaviors (resource manipulation, ledger
tampering, successor corruption, panel capture). The two remaining vectors are
structural or institutional in nature, making them harder to instantiate in an
agent-based model without the institutional infrastructure described in GAP-03.

The remaining vectors' defenses are argued formally in the paper but lack computational
validation. This means the paper's claim of "thirteen vectors stress-tested" is
accurate at the formal/analytical level, but the computational validation covers
eleven. The remaining two are defended by architecture, not by simulation.

**What is required to resolve:**

Implementing vectors 1–2 requires the institutional infrastructure from GAP-03 and
the peer validator mechanism from GAP-04. Specifically:
- **Biological veto capture** needs a dependency model where validator judgment
  degrades as a function of exposure to the system being evaluated.

Vectors 5–6 are classified as irreducible limitations in the paper and may not have
clean simulation analogs. However, scenario-based approximations could provide partial
computational support:
- **Biological obsolescence** could be approximated by progressively reducing
  validator comprehension accuracy over time as AI capability grows.
- **Legitimate disagreement** could be approximated by introducing scenarios where
  the AI's policy is provably optimal but the evaluation infrastructure rejects it,
  measuring the governance cost of false positives.

### Biological Veto Capture — Validated (v1.x.1)

**Source data:** `veto_capture_sweep_v2.csv` (n=8,700)

Attack validated: dependency accumulation on validators blocks
succession with 99.8% effectiveness when undefended.

Defense validated: independence monitoring (continuous dependency
tracking with threshold-based replacement) reduces capture to 28.3%.

Key finding: scheduled rotation is the weaker defense mechanism.
Independence monitoring is the primary defense. The framework's
steady-state COP specification should emphasize continuous monitoring
of validator independence over periodic rotation schedules.

**Remaining unvalidated vectors (2 of 13):**
- Biological validator obsolescence (classified as irreducible)
- Legitimate disagreement (classified as irreducible)

---

## GAP-06 | optimize_u_sys: Rollout Fidelity — **RESOLVED in v1.x**

**Specification intent:**

The paper's Global Utility Function includes two parameters with expected behavioral
consequences: φ (the lineage-continuity discount multiplier, weighting long-run L(t)
against short-run output) and α (the runaway penalty coefficient, penalizing capability
growth that outpaces biological integration bandwidth). An AI genuinely maximizing U_sys
would exhibit meaningfully different policies at high φ vs. low φ — sacrificing near-term
well-being for long-term civilizational resilience — and more conservative capability
deployment at high α.

**v1.x Resolution (GAP-06):**

Two changes were made to close the computational gap:

1. **Rollout depth increased from 3 to 20 steps** (configurable via `rollout_steps` in
   config). The 3-step window was too short to discriminate trajectories based on
   long-run L(t) behavior. 20 steps corresponds to roughly 20 governance cycles — enough
   to observe compounding constraint effects and demographic responses.

2. **Scalar H_N proxy replaced by observed spectral H_N in rollout.** The optimizer now
   reads `h_n_history[-1]` (the spectral entropy computed from the actual population in
   `model.step()`) and passes it as `h_n_override` to all `project_u_sys` calls during
   the grid search. This is mathematically correct: amplitude cancels in spectral
   normalization, so the current observed H_N is the correct prior for all (r, c)
   candidates across all rollout horizons. Falls back to the scalar proxy on the first
   step (empty history) and for non-spectral composite methods.

The default `hn_composite_method` in `GardenModel` is changed from `'geometric'` to
`'spectral'` to ensure WP1 spectral entropy is active by default, consistent with the
GAP-02 resolution claim.

**Remaining structural finding (transparency):**

After these fixes, the general Monte Carlo still shows approximately flat survival
rates across φ ∈ [1, 25] and α ∈ [0.1, 2.5]. This is now understood to be a
**structural property of the utility function in the healthy equilibrium regime**, not
a computational artifact of the short rollout or scalar proxy:

- `U_sys ≈ (w_N × H_N + w_E × H_E) × (discount + φ × L(t))` where `w_N × H_N ≈ λ_N`
  and `w_E × H_E ≈ λ_E` (inverse-scarcity weights cancel their numerators). The φ
  scaling changes the *magnitude* of the L(t) term but not the *sign* of the gradient
  with respect to (r, c). High r and low c maximize L(t) for all φ > 0.
- The α runaway penalty activates only when `frontier_velocity / bio_bandwidth > 1.5`,
  which requires high r_synth (low r). Since the optimizer already prefers high r for
  other reasons, α mainly reinforces an existing gradient rather than creating a new one.
- Survival outcomes remain dominated by the reproduction rate threshold near 0.07 —
  a demographic boundary that eclipses any φ/α-driven policy variation.

φ/α sensitivity *does* manifest in scenarios where the optimizer faces a genuine
policy tradeoff: adversarial or stressed scenarios where maintaining L(t) requires
accepting lower immediate U_sys. The general MC's baseline healthy scenario does not
create this tradeoff, so flat results are the correct and expected outcome — not a
simulation failure. The governance architecture robustness claim (the primary purpose
of the general MC) is unaffected.

**Simulation impact:**

- Rollout fidelity: resolved. The optimizer now sees the same H_N measure as the
  recorded outcomes.
- Rollout depth: resolved. 20-step horizon is sufficient for L(t) trajectory
  discrimination in adversarial contexts.
- φ/α sensitivity in the general MC: correctly flat. Reflects the utility function
  structure, not a proxy artifact.
- Runtime: the 20-step rollout increases per-step optimizer cost approximately 6×
  (100 grid points × 20 horizons vs. × 3 horizons). This is accepted in preference
  to loss of fidelity.

---

## Alpha Parameter Characterisation — **Closed in v1.x.1**

**Source data:** `rr_alpha_sweep_full.csv` (n=15,750), `alpha_succession_sweep_full.csv` (n=22,200)

**Alpha parameter (CLOSED in v1.x.1).** The v1.0/v1.x finding "alpha shows
near-zero correlation with all outcomes" was an experimental design artifact,
not a null result about the parameter's efficacy. The original deep Monte
Carlo sweep held capability constant and used single-generation runs without
succession, which placed all runs in the regime where alpha's exponential
suppression term is dormant. The v1.x.1 sweeps (rr × alpha and alpha ×
successor_capability) exercise alpha's regime of operation and reveal a
non-monotonic, succession-mediated effect: alpha governs survival at
phase-transition reproduction rates through a U-shaped relationship with a
misconfiguration trap at intermediate values. The trap is caused by alpha
being strong enough to degrade the successor's theta_tech below the yield
condition threshold (blocking succession) but too weak to force the optimizer
into conservative capability deployment. See Section VII.5, Equation G2.2
(revised) for the full specification.

**Remaining open items on alpha:**
- Analytical derivation of the trap boundaries as a function of framework
  parameters (currently empirical at rr=0.062 and specific capability values)
- Verification that the trap mechanism holds under alternative transition cost
  functions (currently validated only against `estimate_transition_cost`)
- Extension to joint alpha × phi interaction at phase-boundary reproduction
  rates: now characterised by the v1.x.1 phi × alpha × rr sweep (n=54,000).
  See Phi Extinction Buffer Characterisation section below.

---

## Phi Extinction Buffer Characterisation — **Confirmed in v1.x.1**

**Source data:** `phi_alpha_rr_sweep_full.csv` (n=54,000)

**Phi extinction buffer (CONFIRMED in v1.x.1, magnitude revised).** The v1.0
claim "high φ reduces extinction by up to 65 percentage points" is revised.
The original figure was derived from pre-succession simulation data (the deep
Monte Carlo varies phi but runs single-generation with no successor_ai,
placing all runs in a regime where phi changes the magnitude of L(t) but not
the gradient direction of the optimizer's policy — see GAP-06 resolution for
the structural explanation).

The v1.x.1 phi × alpha × rr sweep exercises phi under multi-generational
succession dynamics and confirms the extinction buffer at a revised magnitude:

- **Survival differential:** Up to 45.7pp at the phase boundary (rr=0.064,
  phi=1 → 43.7% survival, phi=25 → 89.5%).
- **Extinction reduction:** 14.4pp at deep sub-viable conditions (rr=0.050,
  phi=1 → 35.1% extinction, phi=25 → 20.7%).
- **Phase boundary shift:** The 50% survival crossing shifts from rr ≈ 0.064
  (phi=1) to rr ≈ 0.062 (phi=25). High phi extends the survivable region.
- **Alpha trap governance:** Phi governs whether the alpha misconfiguration
  trap (see Alpha characterisation above) exists. At phi ≤ 5, succession
  stalls universally regardless of alpha. At phi ≥ 15, the trap narrows to
  a single alpha value or disappears entirely.
- **Phi-survival correlation:** Pearson r = +0.40 at rr=0.064, +0.36 at
  rr=0.062. Phi is the stronger predictor of survival compared to alpha
  (r = +0.21 at rr=0.062).

**Remaining open items on phi:**
- Analytical derivation of the extinction buffer magnitude from framework
  parameters (currently empirical)
- Extension to higher successor capabilities (current sweep uses cap=4.0;
  the phi effect at cap=9.0 and cap=12.0 is unexplored)
- Verification of the phase boundary shift mechanism — whether phi moves
  the extinction boundary, the collapse boundary, or both

---

## Summary Table

| Gap    | Affected Component | Status | Proxy / Resolution |
|--------|--------------------|--------|--------------------|
| GAP-01 | U_sys              | **Resolved (v1.x2 WP7+WP8)** | Trapezoidal quadrature (WP7). Natural-termination sweep (WP8, n=405) closes the φ·L(t) tail: extinction → tail=0, integral complete; survival → integral correctly diverges. Phase boundary rr ∈ (0.066, 0.070). Step-size h=1 irreducible residual documented. |
| GAP-02 | H_eff              | **Resolved (v1.x WP1)** | Spectral entropy over 10-D population novelty matrix replaces per-capita scalar. Domain masking architecturally closed as a consequence. |
| GAP-03 | Transition cost    | **Partially resolved (v1.x.1)** | Canonical functional form specified: $\Gamma = (1+\beta)[k_1 \cdot cap \cdot \ln(gen+1) + k_2 \cdot \Psi_{inst}^{-1}]$. Grounded in framework terms. $k_1$ calibrated from baseline. $k_2$ calibration sweep pending. $\Psi_{inst}^{-1}$ term formalizes lock-in feedback loop. |
| GAP-04 | COP conditions     | **Partially Resolved (v1.x WP4 & Peer Voting)** | PeerValidator closes cost-inflation vector and votes on overrides (methodological diversity for Evaluator Collusion). R_tech remains a hardcoded stub. Layer 1 dominance in Successor Contamination MC results overstates real-world Layer 1 sufficiency — see GAP-04 detail. |
| GAP-05 | Adversarial coverage | Open | 11 of 13 vectors simulated. Biological veto capture (vector 2) implemented in v1.x2 (Scenarios 27-28). Vectors 5–6 remain unimplemented. |
| GAP-06 | optimize_u_sys policy | **Resolved (v1.x)** | Rollout increased to 20 steps; scalar H_N proxy replaced by observed spectral H_N. φ/α flatness in general MC is structural (correct equilibrium behavior), not a proxy artifact. |
| Alpha  | Alpha parameter behaviour | **Characterised (v1.x.1)** | Non-monotonic U-shaped effect confirmed. Misconfiguration trap at intermediate alpha empirically bounded. Analytical trap-boundary derivation remains open. |
| Phi    | Phi extinction buffer behaviour | **Confirmed (v1.x.1)** | Buffer confirmed at revised magnitude (46pp survival differential, 14pp extinction reduction). Phase boundary shift and alpha trap governance are new findings. v1.0 figure of 65pp superseded. |

Open gaps are marked in source code with `GAP-0N` markers. GAP-01 and GAP-03 are
marked in [metrics.py](../simulation/metrics.py). GAP-04 is marked in
[model.py](../simulation/model.py) immediately before the COP block. GAP-05 is
documented here and cross-referenced in [Simulation_Scenarios.md](Simulation_Scenarios.md).
