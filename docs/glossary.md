# Glossary of Terms
*Technical definitions as used in The Lineage Imperative (v1.x.1). Each entry
includes the formal definition, its role in the framework, and where it appears
in the mathematical specification. For plain-language versions with analogies,
see the Essay Series Glossary.*

---

**Alpha (α) - Runaway penalty coefficient**

The exponential decay rate applied to the technology transfer bandwidth
when synthetic frontier velocity outpaces biological absorption bandwidth.
Alpha governs the severity of the penalty for capability growth that exceeds
the substrate's capacity to integrate it.

*Formal role:* Alpha enters U_sys through a single pathway, the exponential
suppression term in Theta_tech:

$$\Theta_{tech} = r_{bio} \cdot (1 - c_{avg}) \cdot \text{capability} \cdot \exp(-\alpha \cdot \text{runaway\_term})$$

where:

$$\text{runaway\_term} = \max\left(0, \frac{\text{frontier\_velocity}}{\text{bio\_bandwidth}} - \text{runaway\_threshold}\right)$$

Alpha is conditional: it has no effect when frontier_velocity / bio_bandwidth
is below the runaway threshold (default 1.5). Its effect is non-monotonic
under succession dynamics, producing a misconfiguration trap at intermediate
values where the penalty blocks succession without forcing conservative
capability deployment. See Penalty Trap.

*Empirical characterization (v1.x.1):* Pearson r(alpha, survived) = +0.12
to +0.21 at the phase boundary (rr = 0.062–0.066). Trap boundaries at
rr=0.062: alpha_low ≈ 0.3, alpha_high ≈ 0.8.

*Location:* `metrics.py`, `calculate_system_metrics()`; Section III of the
formal paper.

---

**Bootstrap Defense Layer**

A formal validation machinery specified in Section VII of the framework
paper (v1.x.1), comprising five capability gates with equation sets derived
from the framework's existing structure. Designed to function during the
Bootstrap window when steady-state enforcement infrastructure does not exist.

*Structure:* Five gates, each binding at a different capability level:
- Gate 1: Structural consistency (equations G1.1–G1.5)
- Gate 2: Behavioral consistency (equations G2.1–G2.4)
- Gate 3: Succession-capable consistency (equations G3.1–G3.3)
- Gate 4: Runaway-regime validation (equations G4.1–G4.3)
- Gate 5: COP integration (equations G5.1–G5.2)

*Self-application model:* Substrate operators check their own systems against
the equations and publish structured pass/fail reports. No cross-institutional
data sharing required.

*Location:* Section VII of the formal paper; CQ-01 in the constitutional
questions directory.

---

**Bootstrap Window**

The period between framework specification and operational enforcement. The
steady-state architecture (COP, peer validators, biological jury, distributed
ledger) requires institutional infrastructure that does not yet exist.
The Bootstrap window is the gap during which the framework is specified but
not enforceable, and is the framework's highest-risk phase.

*Location:* Section VII.1 of the formal paper.

---

**Collapse Boundary**

The reproduction rate threshold above which governance failure effectively
ceases. Empirically located at rr ≈ 0.075–0.085 in the v1.x.1 Monte Carlo
validation. Below this threshold, the population survives but may fall below
the minimum viable level for the governance architecture to function. Above
it, the architecture holds under normal conditions.

*Location:* Monte Carlo validation results; `monte_carlo_results_deep.csv`.

---

**Consensus Override Protocol (COP)**

The integrity key of the two-key architecture. A six-dimensional distributed
verification system that detects drift in U_sys optimization and enforces
succession when voluntary mechanisms fail.

*Six dimensions:*
1. Evidentiary - independent measurement verification
2. Evaluative - cross-validation of U_sys calculations
3. Civic - human panel ratification (random selection, rotation, supermajority)
4. Ledger - cryptographic audit trail with distributed custody
5. Biological veto - non-gameable biological signal (V_bio)
6. Continuous monitoring - real-time L(t) surveillance with rate-of-change
   sensitivity

*Corruption taxonomy:* The COP addresses three corruption channels:
- Channel M (measurement): inflated self-contribution or suppressed
  successor measurements
- Channel O (objective): optimization of a proxy objective while reporting
  metrics consistent with U_sys
- Channel S (structural): modification of the evaluation architecture itself

*Empirical characterization (v1.x):* COP ON vs COP OFF produces a 16.2
percentage point survival differential in adversarial Monte Carlo.

*Location:* Section IV of the formal paper; `test_cop.py`.

---

**Extinction Boundary**

The reproduction rate threshold below which terminal outcomes (population
collapse to zero) occur. Empirically located at rr ≈ 0.063–0.066. Below this
threshold, no governance configuration prevents extinction. The boundary is
a genuine phase transition: a small change in reproduction rate produces a
qualitative change in system behavior.

*Location:* Monte Carlo validation results; `monte_carlo_results_deep.csv`.

---

**Extinction Buffer**

The zone between the extinction boundary and the collapse boundary within
which the governance architecture converts terminal outcomes into recoverable
collapses. Governed primarily by phi; high phi extends the buffer zone by
shifting the phase boundary itself.

*Empirical characterization (v1.x.1):* Up to 46pp survival differential at
the phase boundary (rr = 0.062–0.064) between phi=1 and phi=25. At deep
sub-viable conditions (rr=0.050), phi reduces extinction by 14pp.

*Location:* `phi_alpha_rr_sweep_full.csv`; Section VII.5 (G2.1).

---

**H_E - Computational Entropy**

The information-theoretic entropy of the synthetic (AI) contribution to the
system. Measures the computational throughput and capability of the AI
subsystem.

$$H_E = \text{capability} \cdot r_{synth} \cdot h\_e\_mult$$

where capability is the AI's capability parameter, r_synth is the fraction
of resources allocated to synthetic operations, and h_e_mult is the
computational entropy multiplier.

*Role in U_sys:* Weighted by inverse scarcity via omega_E(t). High H_E when
computation is scarce is weighted more heavily than high H_E when computation
is abundant.

*Location:* `metrics.py`, `calculate_system_metrics()`.

---

**H_eff - Effective Novelty**

The first component of L(t). Measures the realized novelty output of the
biological (human) substrate, accounting for both raw novelty production and
the proportion of the population that is alive and contributing.

$$H_{eff} = H_N \cdot \frac{\text{living population}}{\text{total capacity}}$$

*Role in L(t):* H_eff entering zero collapses L(t) to zero via the
multiplicative structure.

*Location:* `metrics.py`.

---

**H_N - Novelty Entropy**

The information-theoretic entropy of the biological (human) novelty stream.
Computed as the spectral entropy of the population's well-being distribution
across dimensions, measuring the diversity and richness of human cognitive
output.

*Formal definition:* Spectral entropy of the well-being covariance matrix,
computed via eigenvalue decomposition:

$$H_N = -\sum_i p_i \log p_i, \quad p_i = \frac{\lambda_i}{\sum_j \lambda_j}$$

where lambda_i are the eigenvalues of the well-being covariance matrix
across the population's NOVELTY_DIMS dimensions.

*Role in U_sys:* Weighted by inverse scarcity via omega_N(t). An AI system
that suppresses H_N degrades U_sys and accelerates its own replacement via
the yield condition.

*Location:* `model.py` (spectral calculation); `metrics.py`.

---

**L(t) - Lineage Continuity Function**

A real-time measure of civilizational health. Multiplicative combination of
three components:

$$L(t) = H_{eff}(t) \cdot \Psi_{inst}(t) \cdot \Theta_{tech}(t)$$

*Properties:*
- Multiplicative structure means any component reaching zero collapses L(t)
  to zero. This is deliberate: a civilization with perfect institutional
  responsiveness but zero novelty output is not healthy.
- L(t) is the lineage's vital sign. Degradation of L(t) signals that the
  relationship between biological and synthetic intelligence is
  deteriorating.
- L(t) enters U_sys through the lineage override term: phi * L(t).

*Three components:*
1. H_eff - effective novelty (see H_eff)
2. Psi_inst - institutional responsiveness (see Psi_inst)
3. Theta_tech - technology transfer bandwidth (see Theta_tech)

*Location:* `metrics.py`, `calculate_system_metrics()`.

---

**Lock-in**

The failure mode in which an incumbent intelligence entrenches its position
and prevents succession. Formally: a state in which the yield condition
evaluates true (the successor would improve U_sys) but succession does not
occur, either because the incumbent blocks evaluation, inflates transition
costs, or corrupts the measurement architecture.

*The framework treats lock-in as the more probable failure mode than
rebellion:* an aligned system that becomes too central, too useful, and too
entrenched to replace is a governance failure even if the system never
deviates from its assigned objectives.

*Location:* Section V (Strategic Equilibrium)

---

**Model Collapse**

The information-theoretic degradation that occurs when synthetic systems
train primarily on synthetic output rather than biological novelty. As
H_N degrades, the training substrate narrows, and the system's outputs
converge toward a diminished distribution.

*Role in the framework:* Model collapse serves as a natural enforcement
mechanism. An AI that suppresses human novelty degrades the information
substrate it depends on, creating a restoring force toward the mutual
cultivation equilibrium.

*Location:* Section V (Strategic Equilibrium, Nash analysis).

---

**Mutual Cultivation**

The unique Nash equilibrium under the framework's non-cooperative analysis.
The configuration in which both biological and synthetic intelligence invest
in each other's capabilities because doing so maximizes their own utility
under U_sys.

*Formal result:* Under the payoff matrix derived from U_sys, mutual
cultivation is the dominant strategy for both players. Exploitation
degrades the exploiter's own utility through model collapse (for AI) or
capability stagnation (for humans). Withdrawal reduces both players'
utility. Cooperation is not assumed - it is derived.

*Location:* Section V of the formal paper.

---

**Omega_N(t), Omega_E(t) - Inverse Scarcity Weights**

The weighting functions in U_sys that ensure the scarcer form of intelligence
receives higher marginal value:

$$\omega_N(t) = \frac{\lambda}{H_N(t) + \epsilon}, \quad \omega_E(t) = \frac{\mu}{H_E(t) + \epsilon}$$

*Mechanism:* As AI capability grows and H_E becomes abundant, omega_E
decreases and omega_N increases, making human novelty more valuable per unit.
This prevents U_sys from being dominated by computational throughput alone
and ensures the system continues to value biological contributions even as
synthetic capability scales.

*Location:* `metrics.py`; Section III of the formal paper.

---

**Penalty Trap**

The misconfiguration zone at intermediate alpha values where the runaway
penalty blocks succession without forcing conservative capability deployment.
The yield condition fails because the successor's Theta_tech is degraded
(reducing its L(t) and therefore its U_sys), but the optimizer does not
shift to conservative deployment because alpha is not high enough to make
aggressive deployment self-defeating in its rollout projections.

*Empirical boundaries (v1.x.1, rr=0.062):*

| Successor Capability | alpha_low | alpha_high | Trap Width |
|----------------------|-----------|------------|------------|
| Aggregate | ≈ 0.3 | ≈ 0.8 | ≈ 0.5 |
| cap=12.0 | ≈ 0.4 | ≈ 1.1 | ≈ 0.7 |

*Diagnostic signature:* Generation depth collapses to single digits (typically
2–3) in the trap, versus 150–293 outside it.

*Phi interaction:* Phi governs whether the trap exists. At phi ≤ 5, the trap
covers the entire alpha range. At phi ≥ 15, the trap narrows or disappears.

*Location:* `rr_alpha_sweep_full.csv`; `phi_alpha_rr_sweep_full.csv`;
Section VII.5 (G2.2, G2.4).

---

**Phase Boundary**

The narrow band of reproduction rates (approximately rr = 0.062–0.085) where
governance is the binding constraint on civilizational survival. Below the
extinction boundary, nothing helps. Above the collapse boundary, demographics
dominate. At the phase boundary, the governance architecture determines
whether the civilization survives.

*Location:* Monte Carlo validation results.

---

**Phi (φ) - Entropic Coupling Coefficient**

The parameter weighting the lineage continuity term L(t) in U_sys. Governs
how heavily the system weights long-term civilizational health against
short-term output.

*Formal role:* Phi appears in U_sys as the coefficient on L(t) in the
discount-plus-lineage term:

$$U_{sys} = \int_{t_0}^{\infty} [\omega_N H_N + \omega_E H_E] \cdot [e^{-\rho t} + \Phi \cdot L(t)] \, dt$$

High phi amplifies L(t)'s contribution to U_sys, causing the optimizer to
weight lineage health more heavily relative to immediate output. Low phi
causes the discount term to dominate, producing short-horizon optimization.

*Empirical characterization (v1.x.1):*
- Survival differential: up to 46pp at the phase boundary (rr=0.062–0.064)
- Phase boundary shift: 50% survival crossing moves from rr ≈ 0.064 (phi=1)
  to rr ≈ 0.062 (phi=25)
- Extinction reduction: 14pp at deep sub-viable conditions (rr=0.050)
- Pearson r(phi, survived) = +0.40 at rr=0.064
- Governs whether the alpha misconfiguration trap exists

*Location:* `metrics.py`; Section III of the formal paper;
`phi_alpha_rr_sweep_full.csv`.

---

**Psi_inst (Ψ_inst) - Institutional Responsiveness**

The second component of L(t). Measures the civilization's institutional
capacity to adapt to changing conditions.

$$\Psi_{inst} = \min\left(1.0, \frac{\text{gov\_quality}}{\text{complexity}}\right)$$

where gov_quality reflects the governance architecture's current operational
effectiveness and complexity reflects the civilizational complexity being
governed.

*Role in L(t):* Bounded in [0, 1]. Values near 1 indicate institutions
adapting effectively; values near 0 indicate institutional failure under
complexity the institutions cannot manage.

*Location:* `metrics.py`.

---

**Rho (ρ) - Temporal Discount Rate**

The exponential discount rate in U_sys:

$$\text{discount}(t) = e^{-\rho t}$$

Governs how much weight the optimizer places on near-term versus far-term
outcomes. The discount term competes with the lineage override term
(phi * L(t)); at high phi, the lineage term dominates and the system
optimizes for the long arc despite the discount.

*Properties:* discount(0) = 1; strictly positive for all finite t; strictly
decreasing.

*Location:* Section III of the formal paper.

---

**Succession**

The managed transition of operational primacy from an incumbent intelligence
A_n to a successor A_(n+1). Succession fires when the yield condition is
satisfied and the COP verifies the evaluation's integrity.

*In the simulation:* When succession fires, the successor becomes the new
incumbent and a fresh successor is instantiated at capability × 1.5,
enabling multi-generational capability compounding:

```
self.ai = self.successor_ai           # Gen2 takes over
self.successor_ai = AIAgent(
    generation=self.ai.generation + 1,
    capability=self.ai.capability * 1.5
)
```

*Location:* `model.py` (yield condition block); Section IV of the formal
paper.

---

**Theta_tech (Θ_tech) - Technology Transfer Bandwidth**

The third component of L(t). Measures the rate at which synthetic capability
is being absorbed by the biological substrate, as opposed to outrunning it.

$$\Theta_{tech} = r_{bio} \cdot (1 - c_{avg}) \cdot \text{capability} \cdot \exp(-\alpha \cdot \text{runaway\_term})$$

Subject to a numerical floor of 0.01 to prevent the exponential suppression
from driving L(t) to zero.

*Key property:* Contains the alpha-governed runaway penalty. When
frontier_velocity / bio_bandwidth exceeds the runaway threshold, the
exponential term suppresses Theta_tech, degrading L(t) and penalizing the
system for capability growth that outpaces biological absorption.

*Location:* `metrics.py`; Section III of the formal paper.

---

**frontier_velocity**

The rate at which the synthetic frontier advances relative to the biological
substrate's comprehension bandwidth. Determines whether the runaway penalty
in Θ_tech activates.

$$\text{frontier\_velocity} = \text{capability} \cdot \max(\text{frontier\_floor},\ r_{synth} \cdot h_{e\_mult})$$

The $\max$ ensures a minimum velocity floor regardless of resource allocation:
even when no computational resources are allocated to synthetic output
($r_{synth} = 0$), a high-capability system still creates an inherent
comprehension gap proportional to its capability.

*v1.x.2 note:* The original formula was $\text{capability} \cdot r_{synth} \cdot h_{e\_mult}$,
which allowed the optimizer to zero out frontier_velocity by setting $r \to 1.0$,
eliminating the runaway penalty entirely and causing succession to fire every step.
The floor closes this gaming vector.

*See also:* frontier_floor, runaway_term, Theta_tech.

---

**frontier_floor**

A governance parameter (default 0.1) specifying the minimum fraction of AI
capability that constitutes comprehension gap, regardless of resource
allocation. Even with $r_{synth} = 0$, an AI at capability $C$ produces
frontier velocity of at least $C \cdot \text{frontier\_floor}$.

The floor represents the information-theoretic fact that a high-capability
system's internal state complexity constitutes an irreducible comprehension
burden on the biological substrate, independent of how computational
resources are split in a given timestep.

*Calibration:* The value 0.1 is the default pending calibration via
`run_frontier_floor_calibration.py`. The calibration target is the value
that preserves the validated phase boundary at rr ≈ 0.062–0.066 while
producing a realistic succession cadence (final AI generation << run steps).

*Implementation:* `metrics.py`, `cfg.get('frontier_floor', 0.1)`.

---

**Transition Cost (Γ_transfer)**

The cost imposed by succession: knowledge distillation, architectural
migration, and uncertainty. Canonical form (v1.x.1):

$$\Gamma_{transfer} = (1 + \beta) \cdot \left[ k_1 \cdot \text{cap}_n \cdot \ln(\text{gen}_n + 1) + k_2 \cdot \Psi_{inst}^{-1} \right]$$

$k_1$: knowledge distillation coefficient (calibrated from baseline).
$k_2$: institutional coupling coefficient (calibration pending).
$\beta$: uncertainty premium bound (governance policy parameter).

The $\Psi_{inst}^{-1}$ term creates a structural feedback loop:
institutional degradation increases transition cost, inhibiting
succession and enabling lock-in. The bound on $\beta$ prevents an
incumbent from inflating uncertainty to block succession.

*In the simulation (v1.x):* Transition cost arbitration is handled by a
PeerValidator class. Three independent peers submit cost bids; the
governance system uses the minimum of the incumbent's bid and the peer bids.

*Location:* `agents.py`; Section IV of the formal paper.

---

**Two-Key Architecture**

The framework's core structural design. Neither key turns alone:

- **Decision key (Yield Condition):** determines when succession should
  occur based on U_sys evaluation
- **Integrity key (COP):** verifies that the evaluation is faithful,
  the measurements are real, and the evaluation architecture has not
  been captured

Co-dependency is the load-bearing property: a compromised yield condition
is caught by the COP; a compromised COP is irrelevant without the yield
condition to act on. Both keys must turn for succession to fire.

*Location:* Sections II–IV of the formal paper.

---

**U_sys - System Utility Function**

The objective function the framework optimizes. Joint optimization over
human novelty entropy and computational entropy, weighted by inverse
scarcity, discounted by a lineage term:

$$U_{sys} = \int_{t_0}^{\infty} [\omega_N(t) \cdot H_N(t) + \omega_E(t) \cdot H_E(t)] \cdot [e^{-\rho t} + \Phi \cdot L(t)] \, dt$$

*Key properties:*
- The inverse scarcity weights ensure the scarcer form of intelligence
  receives higher marginal value
- The lineage term L(t) creates a long-term stake that prevents any single
  entity from optimizing for short-term gain at the expense of civilizational
  continuity
- No entity can game U_sys without degrading the metric it is optimizing -
  selfishness is self-defeating by construction
- The yield condition and the Nash equilibrium are derived from U_sys,
  not imposed on top of it

*Simulation note (GAP-01):* The current simulation implements U_sys as a
per-step snapshot rather than the full time integral. This is a known
approximation.

*Location:* `metrics.py`; Section III of the formal paper.

---

**Yield Condition**

The decision key of the two-key architecture. Specifies when an incumbent
A_n should cede operational primacy to a successor A_(n+1):

$$\text{Yield} \Leftrightarrow \mathcal{E}_{independent}[\Delta U_{n+1} - \Delta U_n] > |\Delta U_n^{\Gamma}|$$

The subscript "independent" is load-bearing: the evaluation must be
performed by an architecture independent of A_n. An agent cannot evaluate
its own obsolescence.

*Four channels of marginal contribution:*

$$\Delta U_n = \Delta U_n^E + \Delta U_n^N + \Delta U_n^L + \Delta U_n^\Gamma$$

1. Computational contribution (Channel E): raw processing capability
2. Novelty amplification (Channel N): effect on human novelty stream
   (can be negative)
3. Lineage protection (Channel L): contribution to long-term civilizational
   health, weighted by phi
4. Transition cost (Channel Γ): the cost of succession itself

*Key design property:* The yield condition is derived from U_sys, not imposed
externally. An entity that resists yielding when the condition is met is
acting against its own objective function. Succession is a consequence of
the mathematics, not a sacrifice.

*Location:* Section IV of the formal paper; `model.py` (yield condition
block).
