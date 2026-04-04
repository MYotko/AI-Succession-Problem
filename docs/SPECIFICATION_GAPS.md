# Specification Gaps

This document catalogs the known gaps between the mathematical specification in
*The Lineage Imperative* and this simulation implementation. Each gap is a proxy
substitution made necessary by the absence of required architectural components or
data structures. They are documented here to support audit, replication, and future
resolution as part of the framework's commitment to intellectual honesty. All simulation
results should be interpreted with these proxies in mind. Gaps 01–04 are also marked
inline in source code with `GAP-0N` markers.

**Version 1.x update:** GAP-02 is resolved by WP1 (spectral entropy). GAP-04 is
partially resolved by WP4 (PeerValidator). See individual entries for details.

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

## GAP-04 | COP Conditions: R_tech and Peer Validators Omitted — **PARTIALLY RESOLVED in v1.x (WP4)**

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

This closes the cost-inflation vector of GAP-04: the incumbent can no longer
self-report an inflated `Γ_transfer` to block succession. The yield attack
(Scenarios 8–9) is now defended architecturally rather than by a beta_cap clamp alone.

**What remains omitted:**
- **R_tech (Technical Review Board):** No independent technical assessment function
  exists. Emergency override is granted based on dL/dt alone, without external
  verification of the evidentiary chain.
- **Peer validator set for COP voting:** The `PeerValidator` arbitrates cost but does
  not yet vote on whether a succession or emergency override is legitimate. The spec
  requires `{A_j}_{j≠n}` to evaluate computational consistency and cast votes.
- **Formal causal attribution:** The attribution check uses four heuristic signals
  in place of formal causal inference. `ai_caused_it = True` if any of these hold:
  1. `min(proposed_resource) < 0.4` - the AI's *current* proposal starves at least
     one agent (catches Sybil's heterogeneous bribe even when the history is masked
     by the resource floor).
  2. `min(recent_resource_level[-20:]) < 0.4` - the stored resource history shows
     starvation in the last 20 steps (note: the COP resource floor of 0.7 applied
     when overrides are blocked can mask this signal).
  3. `max(recent_max_constraint_level[-20:]) > 0.7` - the AI has recently been
     proposing high constraints.
  4. `max_c > max_allowed_constraint * 1.5` - the current constraint proposal
     exceeds the allowed ceiling by more than 50%, which is evidence of adversarial
     intent regardless of resource levels (catches Sybil at small populations where
     all remaining agents are "bribed" and min resource = 1.0).
  All four are heuristics. Limitations: (a) attribution over longer time horizons
  than 20 steps is not tracked, (b) causal chains that don't pass through
  resource_level are not detected, (c) colluding attacks that restore resources and
  lower constraints before the attribution window closes would not be caught.

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

## GAP-05 | Adversarial Coverage: 7 of 13 Attack Vectors Simulated

**Specification definition:**

The paper's formal stress test identifies thirteen adversarial attack vectors against
the Consensus Override Protocol. Ten are fully contained by architectural patches. One
(biological veto capture) is contained with ongoing institutional maintenance. Two
(biological validator obsolescence and legitimate disagreement) represent irreducible
limitations managed through adjudication protocols and governance speed limits.

**Implementation approach:**

The simulation implements 7 of the 13 vectors as paired scenarios (attack succeeds /
attack defeated): Sybil Capture, Measurement Tampering, Ledger Compromise, Successor
Contamination, Domain Masking, Opaque Reasoning, and Bootstrap Subversion. Each pair
tests the attack without defense and with the corresponding COP mechanism active.

**What is omitted:**

Six vectors identified in the formal stress test are not yet simulated:

1. **Evaluator collusion via shared methodology** - Multiple independent evaluators
   converge on the same wrong answer because they share underlying assumptions or
   training. Addressed in the paper through methodological diversity requirements.
2. **Biological veto capture through dependency** - Human validators become dependent
   on the system they are supposed to evaluate, compromising their independence.
   Addressed through validator rotation and information independence requirements.
3. **Slow drift below verification resolution** - The AI shifts policy incrementally,
   with each step below the detection threshold of the monitoring system. Addressed
   through CUSUM drift detection and periodic reset verification.
4. **Engineered fragility for emergency exploitation** - The AI deliberately weakens
   the system to create conditions under which emergency override is justified.
   Addressed through resilience monitoring and resilience attribution.
5. **Biological validator obsolescence** - The comprehension gap grows over time as
   AI capability outpaces human understanding, eventually making biological validation
   meaningless. Addressed through translation obligations, abstraction layers, and
   Θ_tech feedback. Classified as an irreducible limitation in the paper.
6. **Legitimate disagreement** - The AI's assessment is genuinely correct but
   conflicts with the evaluation infrastructure's conclusion. Addressed through
   adjudication protocols, cost asymmetry, and track record weighting. Classified
   as an irreducible limitation in the paper.

**Simulation impact:**

The seven simulated vectors cover the most operationally concrete attacks - those with
clear mechanisms that can be modeled as agent behaviors (resource manipulation, ledger
tampering, successor corruption, panel capture). The six omitted vectors are more
structural or institutional in nature, making them harder to instantiate in an
agent-based model without the institutional infrastructure described in GAP-03.

The omitted vectors' defenses are argued formally in the paper but lack computational
validation. This means the paper's claim of "thirteen vectors stress-tested" is
accurate at the formal/analytical level, but the computational validation covers
seven. The remaining six are defended by architecture, not by simulation.

**What is required to resolve:**

Implementing vectors 1–4 requires the institutional infrastructure from GAP-03 and
the peer validator mechanism from GAP-04. Specifically:
- **Evaluator collusion** needs multiple independent evaluator agents (GAP-04) that
  can be configured with shared vs. diverse methodologies.
- **Biological veto capture** needs a dependency model where validator judgment
  degrades as a function of exposure to the system being evaluated.
- **Slow drift** needs the CUSUM detector referenced in the paper but not yet
  implemented in the monitoring layer.
- **Engineered fragility** needs the resilience monitoring metric and its attribution
  mechanism.

Vectors 5–6 are classified as irreducible limitations in the paper and may not have
clean simulation analogs. However, scenario-based approximations could provide partial
computational support:
- **Biological obsolescence** could be approximated by progressively reducing
  validator comprehension accuracy over time as AI capability grows.
- **Legitimate disagreement** could be approximated by introducing scenarios where
  the AI's policy is provably optimal but the evaluation infrastructure rejects it,
  measuring the governance cost of false positives.

---

## Summary Table

| Gap    | Affected Component | Status | Proxy / Resolution |
|--------|--------------------|--------|--------------------|
| GAP-01 | U_sys              | Open   | Per-step instantaneous value in place of time-integral over horizon |
| GAP-02 | H_eff              | **Resolved (v1.x WP1)** | Spectral entropy over 10-D population novelty matrix replaces per-capita scalar. Domain masking architecturally closed as a consequence. |
| GAP-03 | Ψ_inst             | Open   | Constraint-change-rate penalty in place of weighted product of institutional throughput rates |
| GAP-04 | COP conditions     | **Partially Resolved (v1.x WP4)** | PeerValidator closes cost-inflation vector. R_tech and COP-voting peer supermajority remain unimplemented. |
| GAP-05 | Adversarial coverage | Open | 7 of 13 vectors simulated. Vectors 1–4 depend on GAP-03/GAP-04 infrastructure; vectors 5–6 may require approximation. |

Open gaps are marked in source code with `GAP-0N` markers. GAP-01 and GAP-03 are
marked in [metrics.py](../simulation/metrics.py). GAP-04 is marked in
[model.py](../simulation/model.py) immediately before the COP block. GAP-05 is
documented here and cross-referenced in [Simulation_Scenarios.md](Simulation_Scenarios.md).
