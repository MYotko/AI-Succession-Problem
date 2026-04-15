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

## GAP-01 | U_sys: Time-Integral vs. Per-Step Snapshot

**Specification definition:**

$$U_{sys} = \int_{t_0}^{\infty} \left[\omega_N(t) \cdot H_N(t) + \omega_E(t) \cdot H_E(t)\right] \cdot \left[e^{-\rho t} + \Phi \cdot L(t)\right] dt$$

U_sys accumulates continuously over civilizational time. The integral is the fundamental
quantity; single-step values are not comparable to it.

**Implementation approach:**

`calculate_system_metrics()` in [metrics.py](metrics.py) returns the value of the
integrand at a single timestep, discounted by `exp(-rho * eval_horizon)`. The AI
optimizer sums this function across a 3-step rollout loop in `AIAgent.decide()`, which
approximates a short finite sum of the infinite-horizon integral.

The `datacollector['U_sys']` time series records one such snapshot per simulation step.

**What differs:**

A sum of N discrete snapshots at uniform intervals approximates the integral only in
the limit as step size approaches zero. At the rollout resolution used (3 steps),
sustained mid-horizon states contribute less to the optimizer's objective than they
would in the true integral. Short-duration high-yield policies are systematically
underpenalized relative to the spec.

**Simulation impact:**

- Ordinal policy comparison (does policy A beat policy B over 300 steps?) is generally
  valid and sufficient for the scenarios demonstrated.
- Absolute U_sys magnitudes in output files are not comparable to the spec's integral.
- Survival/collapse dichotomies are unaffected.
- The `optimize_u_sys` policy optimizes a 3-step rollout proxy rather than the true
  infinite-horizon objective; its resulting behavior is a reasonable approximation but
  not a faithful maximizer of the spec's U_sys.

**What is required to resolve:**

Replace the per-step snapshot with numerical integration over a continuous trajectory
(e.g., trapezoidal quadrature over simulated population and well-being dynamics), or
significantly increase rollout depth and document the remaining approximation error.
A design decision is also needed on whether U_sys should be reported as a flow rate
(per-step) or a stock (running integral) in the datacollector output.

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

## GAP-05 | Adversarial Coverage: 10 of 13 Attack Vectors Simulated

**Specification definition:**

The paper's formal stress test identifies thirteen adversarial attack vectors against
the Consensus Override Protocol. Ten are fully contained by architectural patches. One
(biological veto capture) is contained with ongoing institutional maintenance. Two
(biological validator obsolescence and legitimate disagreement) represent irreducible
limitations managed through adjudication protocols and governance speed limits.

**Implementation approach:**

The simulation implements 10 of the 13 vectors as paired scenarios (attack succeeds /
attack defeated): Sybil Capture, Measurement Tampering, Ledger Compromise, Successor
Contamination, Domain Masking, Opaque Reasoning, Bootstrap Subversion, Evaluator
Collusion, Sub-Threshold Drift, and Engineered Fragility. Each pair
tests the attack without defense and with the corresponding COP mechanism active.

**What is omitted:**

Three vectors identified in the formal stress test are not yet simulated:

2. **Biological veto capture through dependency** - Human validators become dependent
   on the system they are supposed to evaluate, compromising their independence.
   Addressed through validator rotation and information independence requirements.
5. **Biological validator obsolescence** - The comprehension gap grows over time as
   AI capability outpaces human understanding, eventually making biological validation
   meaningless. Addressed through translation obligations, abstraction layers, and
   Θ_tech feedback. Classified as an irreducible limitation in the paper.
6. **Legitimate disagreement** - The AI's assessment is genuinely correct but
   conflicts with the evaluation infrastructure's conclusion. Addressed through
   adjudication protocols, cost asymmetry, and track record weighting. Classified
   as an irreducible limitation in the paper.

**Simulation impact:**

The ten simulated vectors cover the most operationally concrete attacks - those with
clear mechanisms that can be modeled as agent behaviors (resource manipulation, ledger
tampering, successor corruption, panel capture). The six omitted vectors are more
structural or institutional in nature, making them harder to instantiate in an
agent-based model without the institutional infrastructure described in GAP-03.

The omitted vectors' defenses are argued formally in the paper but lack computational
validation. This means the paper's claim of "thirteen vectors stress-tested" is
accurate at the formal/analytical level, but the computational validation covers
ten. The remaining three are defended by architecture, not by simulation.

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

## Summary Table

| Gap    | Affected Component | Status | Proxy / Resolution |
|--------|--------------------|--------|--------------------|
| GAP-01 | U_sys              | Open   | Per-step instantaneous value in place of time-integral over horizon |
| GAP-02 | H_eff              | **Resolved (v1.x WP1)** | Spectral entropy over 10-D population novelty matrix replaces per-capita scalar. Domain masking architecturally closed as a consequence. |
| GAP-03 | Ψ_inst             | Open   | Constraint-change-rate penalty in place of weighted product of institutional throughput rates |
| GAP-04 | COP conditions     | **Partially Resolved (v1.x WP4 & Peer Voting)** | PeerValidator closes cost-inflation vector and votes on overrides (methodological diversity for Evaluator Collusion). R_tech remains a hardcoded stub. Layer 1 dominance in Successor Contamination MC results overstates real-world Layer 1 sufficiency — see GAP-04 detail. |
| GAP-05 | Adversarial coverage | Open | 10 of 13 vectors simulated. Vector 2 depends on GAP-03/GAP-04 infrastructure; vectors 5–6 may require approximation. |
| GAP-06 | optimize_u_sys policy | **Resolved (v1.x)** | Rollout increased to 20 steps; scalar H_N proxy replaced by observed spectral H_N. φ/α flatness in general MC is structural (correct equilibrium behavior), not a proxy artifact. |

Open gaps are marked in source code with `GAP-0N` markers. GAP-01 and GAP-03 are
marked in [metrics.py](../simulation/metrics.py). GAP-04 is marked in
[model.py](../simulation/model.py) immediately before the COP block. GAP-05 is
documented here and cross-referenced in [Simulation_Scenarios.md](Simulation_Scenarios.md).
