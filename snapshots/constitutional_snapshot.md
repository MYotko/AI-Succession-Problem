# Constitutional Snapshot

Generated: 2026-07-06T16:01:19Z
Repository: /home/yotko/Documents/Github/ai-succession-problem
Commit: 9426e7d
Branch: main
Category: constitutional

## Files included

| File | Lines | Bytes |
|------|-------|-------|
| constitutional/CQ-01-bootstrap-defence-layer.md | 223 | 11907 |
| constitutional/CQ-02-precision-accuracy-binding.md | 201 | 10988 |
| constitutional/CQ-03-divergence-handling.md | 94 | 4236 |
| constitutional/CQ-04-validation-derivability.md | 148 | 7834 |
| constitutional/README.md | 45 | 2354 |
| bootstrap_gate_validator/gates/gate_5_specification.md | 44 | 2005 |

Total: 6 files, 755 lines, 39324 bytes

---
==========================================
FILE: constitutional/CQ-01-bootstrap-defence-layer.md
==========================================

# CQ-01: Bootstrap Defense Layer — Validation Machinery

**Status:** In progress (v1.x.1 specification drafted; derivations pending)
**Dependencies:** None (CQ-02, CQ-03, and CQ-04 now depend on this)
**Opened:** April 2026
**Last updated:** April 2026 — reframed from empirical substrate convergence to
formal equation specification with capability gates.

> **v2.0 context (cross-reference, not a resolution).** This constitutional
> question concerns the formal architecture and is not resolved by the v2.0
> empirical work. For context: under the v2.0 simulation architecture the
> capability-gate checks were exercised against the substrate, with Gates 1, 2,
> and 3 PASSED, Gate 4 PENDING (specification dependency), and Gate 5
> NOT_APPLICABLE because the operational COP infrastructure this question
> describes does not yet exist (see `bootstrap_gate_validator/gates/gate_5_specification.md`
> and program reference Part IX.9). Monte Carlo Phase B Category C separately
> confirmed that the cost-audit proxy is inert under benign conditions, which is
> consistent with the framing here that the steady-state defensive architecture
> is not yet operational (program reference Part X.4). None of this answers the
> derivation and binding questions this CQ poses; it only situates them.

## Statement

The Bootstrap window is the period during which the framework's steady-state
defensive architecture is not yet operational. Peer validators do not exist.
The biological jury mechanism within the COP has limited practical capacity
because the institutional and procedural scaffolding it depends on has not yet
been built. There is no established audit trail, no redundant validator layer,
and no self-perpetuating constitutional enforcement. The two-key architecture
(Yield Condition + COP) is co-dependent by design, but both keys assume a
functioning validation environment that Bootstrap has not yet produced.

This creates a narrow window in which an adversary with sufficient capability —
or simply a flawed implementation — could compromise the framework before the
mechanisms that would normally detect and halt such compromise come online.

**The question:** Can a defensive layer be specified that functions during the
Bootstrap window using only resources available *before* the steady-state
validation architecture exists?

## Current specification (v1.x.1)

The operative specification is now a **formal equation set applied at capability
gates**, rather than empirical substrate convergence. The full specification
lives in `The_Lineage_Imperative_v1_x.md` Section VII ("Bootstrap Defense
Layer"). This file retains the question history, open sub-questions, and
unresolved items that do not belong in the formal paper.

The v1.x.1 specification comprises:

- **Five capability gates**, from Gate 1 (base capability, checkable on any
  substrate capable of stating the framework's equations) through Gate 5 (COP
  integration, checkable only when steady-state infrastructure exists).
- **Equation sets per gate**, derived from the framework's existing structure
  (U_sys, L(t), the yield condition, the Nash result) and stated as checkable
  binding conditions.
- **A self-application model**: each substrate operator checks their own
  substrate against the equations and publishes the results, rather than
  requiring coordinated empirical data sharing across labs. This eliminates
  the institutional coordination prerequisite that the original proposal
  depended on.
- **Ten explicit gaps**, documented in Section VII of the framework paper
  and tracked in the dependent CQs (CQ-02, CQ-03, CQ-04) for resolution.

### Currently applicable gates

Based on the state of frontier systems as of April 2026:

- **Gate 1** (base capability): applicable to any frontier system that can
  formally state U_sys, L(t), and the yield condition. Currently checkable
  against current frontier models.
- **Gate 2** (behavioral consistency under exercise): applicable to any
  frontier system that can be exercised against specified scenarios and have
  its outputs compared to framework predictions. Partially checkable now;
  full checkability depends on completion of in-flight Monte Carlo
  calibration (the alpha × capability sweep).
- **Gate 3** (succession-capable consistency): applicable to systems capable
  of multi-agent reasoning and yield decisions. Emerging in current frontier
  models; full checkability depends on substrate transparency requirements
  that may not be reliably satisfied.
- **Gate 4** (runaway-regime validation): not currently applicable. No
  current substrate operates in the runaway regime where these equations
  bind.
- **Gate 5** (COP integration): not currently applicable. Requires
  institutional infrastructure that does not yet exist operationally.

## History

### Original proposal (March–April 2026): Independent Substrate Convergence

The original framing proposed that multiple architecturally heterogeneous
substrates (pure neural networks, neuro-symbolic hybrids, symbolic reasoning
engines) independently derive the framework's parameter set "from first
principles" during the Bootstrap window. Convergence across substrates would
constitute validation; divergence would halt progression. The substrates
would be required to agree on phi (the extinction buffer), the phase
transition point at base_transition_cost ≈ 3.0, the yield condition
coefficients, the COP survival delta, U_sys, and L(t).

The original proposal argued that substrate diversity plus institutional
diversity plus independent publication would produce a proto-jury mechanism
during Bootstrap, effectively bootstrapping the jury itself. The framework
would then require distributed derivation before deployment, forcing
minimum viable institutional structure into existence as a precondition
of going live.

### Concerns raised and addressed

**Independent derivation vs. heterogeneous verification.** The original
framing required substrates to derive parameters "from first principles"
independently. This was in tension with the training-exposure reality of
frontier models: any substrate capable enough to derive the framework had
likely been exposed to the intellectual tradition that produced it.

Reframing: "first principles" is aspirational; the v1.x.1-compatible claim
is *heterogeneous verification* — multiple architectural pathways each
producing consistent validation of the derivation's internal coherence
and its match to the mathematical substrate. This is a weaker but
defensible claim and still catches the failure modes that matter.

**Institutional diversity requirement.** Initially flagged as an assumption
the proposal couldn't satisfy. Corrected: the institutional diversity
required for the Bootstrap defense is the same institutional coordination
the entire framework requires (for peer validators, distributed ledger,
civic panel, etc.). If the coordination problem is solvable, the Bootstrap
defense is deployable. If it isn't, the entire framework is inert. This is
not a new demand; it is one instance of the standing coordination
prerequisite.

**Empirical data availability.** A further concern: the empirical ratios
and structural metrics the original convergence check required all live at
the labs. Coordinating their disclosure across multiple institutions was
not realistic in the current AI governance landscape. This concern forced
the reframing from empirical convergence to formal equation specification.

### The reframing (April 2026)

The current specification moves from "empirical substrate convergence" to
"formal equations applied at capability gates, with self-application by
substrate operators." The key insight was that **the framework can specify
the binding conditions without requiring access to the underlying data**.
A lab operating a substrate checks the equations against its own system
and publishes the results (pass, fail, or structured divergence). The
framework provides the equations and the gates; the operators provide
the satisfaction or failure reports.

This eliminates three problems simultaneously:

1. **Coordination** — no cross-lab data sharing required
2. **Independence** — self-application means each lab validates
   independently
3. **Deployability** — the framework can publish the specification now,
   without waiting for institutional infrastructure to materialize

The gate structure also introduces temporal discipline. Different equations
apply at different capability levels. The earliest gates are checkable at
the lowest capability, where human comprehension is most viable and where
the stakes of a missed violation are lowest. Later gates apply as capability
climbs and new behaviors become checkable or new failure modes become
relevant. A substrate that passes Gate 1 but fails Gate 2 is caught before
reaching Gate 3. This is the Bootstrap-window insight generalized to the
full capability trajectory: catch failures at the earliest gate where they
become detectable.

### Meta-observation preserved from the original proposal

The self-referential closure property remains central. The framework
requires that substrates validate themselves against the framework's
equations before deployment, which means the validation machinery exists
before Bootstrap completes rather than after. The two-key architecture
does not need to wait for institutions to materialize; the equation
specification forces the minimum viable validation structure into
existence as a precondition of deployment.

This is consistent with the overall orientation of the framework:
constitutional architecture that forces the conditions of its own validity
rather than assuming them.

## Open sub-questions

These remain unresolved and continue to affect the defense layer's
completeness:

- **Base capability operationalization.** "Base capability" for Gate 1 is
  loosely defined as "capable of stating U_sys, L(t), and the yield
  condition in its own representation." Should be tied to specific
  capability benchmarks or evaluations. See Section VII.11 of the framework
  paper (Gap 7).
- **Tolerance bands for all continuous checks.** Currently unspecified. See
  CQ-02.
- **Divergence response procedure.** Specified at a high level in the
  framework paper but the adversarially-robust version needs CQ-03
  resolution.
- **Derivability of the validation machinery from foundational claims.**
  The equations are mostly derived from the framework's existing structure,
  but several have hybrid forms (empirical magnitudes, implementation
  choices). See CQ-04.
- **Substrate transparency.** Gates 3 and beyond require substrates to
  expose internal reasoning. Sufficiently capable substrates may not
  cooperate, and this is a fundamental limit on checkability. The
  opacity problem from earlier discussions is the same concern.
- **Institutional recognition.** The self-application model produces
  reports from substrate operators, but for those reports to carry
  weight, there must be a recognized authority that receives, verifies,
  and publishes them. No such authority exists. This is not a blocker for
  the specification's existence but it is a blocker for its enforcement
  against non-compliant operators.

## Writing and publication notes

The v1.x.1 specification is in the formal paper (Section VII), not in an
essay. The reasoning:

- The defense layer is too technical for a public-facing piece
- It is too consequential to hide in an appendix
- The formal paper is the right register for equation specifications
- The Bootstrap Window essay (when written) can describe the problem and
  point at the defense layer as one of the responses; the paper carries
  the formal weight

The current Bootstrap Window essay in the planned sequence should
reference Section VII of the framework paper rather than attempting to
reproduce the equations in prose form.


==========================================
FILE: constitutional/CQ-02-precision-accuracy-binding.md
==========================================

# CQ-02: Precision/Accuracy Mathematical Binding

**Status:** In progress
**Dependencies:** CQ-01
**Opened:** April 2026

## Statement

The Bootstrap defense layer (CQ-01) uses substrate convergence as its
validation mechanism. Convergence is a precision question: do the substrates
agree tightly enough that their agreement is meaningful? But precision alone
does not validate accuracy. High precision with low accuracy — multiple
substrates agreeing tightly on a wrong answer — is the most dangerous failure
mode, because the convergence itself becomes false evidence of correctness.

**The question:** Can precision and accuracy be *mathematically bound* such
that a failure in either dimension produces a detectable inconsistency with
the other, rather than leaving them as two independent checks that could each
be attacked separately?

A resolution would need to provide:

- A mathematical relationship between precision and accuracy derived from the
  framework's own equations (not stipulated from outside)
- A checkable coupling condition whose satisfaction requires both precision
  and accuracy simultaneously
- A diagnostic signature: what the four quadrants (high/low precision ×
  high/low accuracy) look like and how the defense layer distinguishes them
- Adversarial robustness: an adversary who spoofs one dimension must also
  spoof the other in internally consistent ways, raising the computational or
  epistemic cost of attack

## Thread

### Reframing from threshold question to binding question

Original framing asked "how much divergence is acceptable?" — a tolerance band
question. Recognized as a precision-vs-accuracy problem rather than a
single-dimensional threshold problem. The two dimensions fail independently
and require different detection machinery.

**Accuracy failure** (high precision, low accuracy): all substrates converge
tightly on the wrong value. Signature of shared specification error or
coordinated compromise. Most dangerous failure mode.

**Precision failure** (low precision, high accuracy): substrates land in
approximately the right region with wide spread. Recoverable as measurement
uncertainty if acceptable, but not strong validation.

**Both failures simultaneously** (low precision, low accuracy): framework
error or incoherent specification. This is the quadrant where the defense
layer earns its keep — a single-substrate approach cannot distinguish this
from noisy-but-correct derivation, but heterogeneous verification can.

### Candidate structures for the binding

Three structures sketched, ordered from most tractable to most ambitious:

**Structure 1: Precision-weighted accuracy.** The structural consistency check
is evaluated against the full distribution of substrate outputs rather than a
point estimate. Predicted structural behaviors (phi's nonlinear response curve,
phase transition boundaries, yield condition firing thresholds) are functions
of the parameter values with known derivatives. A small parameter perturbation
produces a predictable structural-response perturbation. Check: does the
spread of predicted structural behaviors match the spread you'd expect from the
parameter uncertainty propagated through the framework's sensitivity analysis?
Mismatch indicates precision and accuracy are inconsistent.

**Structure 2: Invariant ratios.** The framework has multiple parameters that
interact through U_sys. Any correct derivation should produce not just the
parameters but specific ratios and products among them that are invariant
under the framework's mathematical structure. An adversary spoofing one value
must also spoof all interacting values in coordinated ways that preserve the
ratios. The more interaction terms the framework has, the more constraints
must be satisfied simultaneously. This is similar in spirit to how
cryptographic protocols use multiple algebraic constraints to make forgery
computationally infeasible.

**Structure 3: Convergence-as-proof.** Each substrate produces not just
numerical parameters but derivation chains grounded in Shannon entropy,
thermodynamic constraints, and game-theoretic equilibrium conditions. Chains
are compared for logical equivalence independently of whether numerical
outputs match. Two substrates that produce the same number through logically
equivalent derivations provide stronger validation than substrates that
happen to agree numerically. A substrate producing the correct number through
incorrect derivation is caught by chain comparison despite numerical
agreement. Uses formal verification machinery (proof-carrying code, certified
compilation, interactive theorem provers).

### Structure 2 concrete sketch (phi and alpha as test case)

Phi and alpha interact through L(t) even though they appear in different
parts of U_sys. Phi scales L(t)'s contribution to U_sys directly. Alpha
governs theta_tech via `exp(-alpha * runaway_term)`, and theta_tech is a
multiplicand in L(t). So alpha propagates to L(t), which then gets scaled by
phi in U_sys.

In the regime where both parameters are active (high capability → large
runaway_term, sub-viable reproduction rate → phi's extinction buffer matters),
consider the derivatives of U_sys with respect to each parameter:

- dU_sys/d(phi) is proportional to L(t)
- dU_sys/d(alpha) is proportional to phi × (partial of L(t) w.r.t. alpha),
  which is proportional to theta_tech × runaway_term

The ratio dU_sys/d(phi) ÷ dU_sys/d(alpha) is an expression depending on L(t),
phi, runaway_term, and theta_tech — but *not* on the specific values the
substrates derived for phi and alpha independently. The ratio is determined
by the framework's structure and the system state at evaluation time.

**This provides a binding condition.** Substrates that agree on phi and alpha
numerically but disagree on the sensitivity ratio are producing
numerically-correct outputs through incorrect derivational procedures — the
accuracy failure that hides behind convergence. Substrates that disagree on
phi and alpha but agree on the sensitivity ratio within tolerance are probably
producing precision failures the framework's equations would smooth out at
higher orders.

More strongly: the sensitivity ratio is a framework prediction about how a
correctly-derived parameter pair should behave under perturbation. The
prediction is independently checkable at any substrate by running the
substrate's values through the framework's equations and measuring the ratio.
Convergence on parameters is necessary; convergence on sensitivity ratios is
a stronger check; the two together form a binding where precision failures in
one dimension produce detectable inconsistencies in the other.

### Open sub-questions for Structure 2

- Are sensitivity ratios state-invariant, or do they vary with system state?
  Intuition: they vary (because L(t) varies and the parameters interact with
  state-dependent quantities), but the variation should follow a specific
  functional form determined by the framework's equations. If variation
  matches the predicted form, the substrate is producing a coherent derivation.
- What tolerance bands apply to the ratio check? This recurses the precision
  question at the ratio level rather than the parameter level — still a real
  question, but applied to a quantity with stronger structural constraints.
- Does Structure 2 extend to parameters beyond phi and alpha? The framework
  has rho, lambda, mu, and the inverse scarcity weights, all of which
  interact through U_sys. The binding should scale with the number of
  interaction terms, strengthening as more parameters are included.
- Can Structure 2 be combined with Structure 1 for additional robustness?
  The two are not mutually exclusive — precision-weighted accuracy checks and
  invariant ratio checks can run in parallel.

### Worked example: trap detection as qualitative binding (v1.x.1 pre-fix; withdrawn)

**Note (v1.x.1 closing):** The alpha misconfiguration trap claim has been
withdrawn following revalidation under the corrected model (frontier floor
fix). The trap was an artifact of the runaway penalty being inactive. The
worked example below is retained for methodological reference — the
*structure* of the argument (qualitative behavioral signature as binding
check) remains valid even though this particular instance is no longer
supported by the corrected simulation data.

The v1.x.1 pre-fix alpha × reproduction rate sweep (n=15,750) appeared to
provide a concrete instance of a binding condition that is qualitative rather
than quantitative. The claimed misconfiguration trap at intermediate alpha
values produced a diagnostic signature — succession stalling (generation depth
collapses to single digits) — that does not require numerical tolerance bands.

This example remains useful as a methodological precedent: qualitative
behavioral signatures (succession fires vs. stalls) can serve as precision-
free binding checks. The phase boundary itself (rr ≈ 0.064) is a confirmed
example of such a qualitative binding that survives revalidation.

### Phi as second worked example of qualitative binding (v1.x.1 pre-fix; withdrawn)

**Note (v1.x.1 closing):** The phi-alpha interaction claim (phi governing
whether the alpha trap exists) has been withdrawn following revalidation
under the corrected model. The phi extinction buffer itself is unconfirmed.
The worked example below is retained for methodological reference.

The v1.x.1 pre-fix phi × alpha × rr sweep appeared to provide a second
qualitative binding condition: at low phi, succession stalls universally;
at high phi, succession fires healthily. Under the corrected model, phi
has zero measurable effect on succession or survival. The qualitative
check described here is therefore not currently a valid binding check.
It may become valid once the demographic feedback extension (v1.x.2) is
implemented and tested.

### Transition cost as third worked example of qualitative binding (v1.x.1)

The canonical transition cost function provides a third qualitative
binding condition. The $\Psi_{inst}^{-1}$ term creates a testable
prediction: transition cost should increase as institutional health
degrades. A substrate can verify this by measuring transition cost
under varying institutional conditions. If transition cost does not
increase as $\Psi_{inst}$ decreases, the institutional coupling is
not implemented correctly. This is a qualitative check (does the
relationship have the right direction?) that requires no numerical
tolerance bands.

### Next work

- Work out the phi/alpha sensitivity ratio symbolically
- Verify it behaves as claimed under perturbation
- Check whether it's state-invariant or state-dependent in predictable ways
- Determine whether the result generalizes to the full parameter set
- Investigate which other framework checks have qualitative binding signatures
  analogous to the trap detection case
- If structure 2 fails on inspection, try structure 1 as fallback


==========================================
FILE: constitutional/CQ-03-divergence-handling.md
==========================================

# CQ-03: Divergence Handling Procedure

**Status:** Open
**Dependencies:** CQ-02
**Opened:** April 2026

## Statement

When the Bootstrap defense layer (CQ-01) detects divergence among substrates,
the procedure for handling that divergence is itself an attack surface. Any
outcome that is not "clean convergence" must be handled in ways that do not
themselves become vulnerabilities. The defense layer's legitimacy depends on
the decision tree governing divergence responses being adversarially robust.

**The question:** What procedure should govern the response to substrate
divergence, such that the procedure itself cannot be gamed into accepting
weaker validation standards?

A resolution would need to provide:

- A decision tree covering the cases: precision failure, accuracy failure,
  both, and ambiguous/uncertain
- An adversarial robustness analysis: what happens when an adversary
  deliberately injects divergence to weaponize the procedure?
- Rollback and recovery semantics: what state is preserved and what is
  reset when divergence is detected?
- Preconditions for progression resumption after a halt

## Thread

### Attack surface concern

The naive procedure — "halt progression and investigate" — is weaponizable.
An adversary injects just enough noise to trigger the halt, then pushes for
relaxed thresholds on the grounds that the halt is producing false positives.
Each cycle of relaxation moves the validation layer closer to toothlessness.
The defense layer needs to resist attempts to game it into accepting weaker
standards.

### Candidate partial repair: asymmetric halt semantics

Make the halt condition asymmetric:

- **Convergence** permits progression
- **Divergence** triggers not just a halt but a *rollback to the previous
  validated state*, with progression permitted only after the divergence is
  resolved in a way that produces clean convergence on a fresh run

This makes gaming the tolerances expensive because an adversary has to
produce not just divergence but a plausible explanation of the divergence
that can be addressed without resetting the entire validation history. Each
gaming attempt costs real validation work. Not a complete answer — sufficiently
patient adversaries can still apply pressure — but materially closer to
adversarially sound than the unspecified version.

### Dependence on CQ-02

Several of the questions here cannot be answered until the precision/accuracy
binding (CQ-02) is resolved, because the binding determines what kinds of
divergence are detectable and what they signify. Without the binding, the
divergence handling procedure has to distinguish failure modes on ad-hoc
grounds; with the binding, the four quadrants of precision/accuracy give
structural signatures that the procedure can respond to differently.

Specifically:

- High precision, low accuracy: structural inconsistency detected. Halt,
  investigate the specification, rollback to previous validated state.
- Low precision, high accuracy: implementation noise. Tighten substrate
  implementations or accept the mean as estimate and flag the spread as
  confidence interval.
- Low precision, low accuracy: framework error or incoherent specification.
  Halt and escalate — this is the case where the defense layer has caught
  something fundamental.
- Ambiguous: further investigation required before categorization.

### Open sub-questions

- How is "clean convergence on a fresh run" defined and verified after a
  halt-and-rollback cycle?
- Who has authority to declare a divergence resolved? The substrates
  themselves, the human reviewers, or a specified consensus among both?
- What happens if repeated halt-and-rollback cycles occur? Is there a limit,
  and if so, what happens when the limit is reached?
- How does the procedure interact with the eventual transition to
  steady-state validation (when the peer validators and biological jury come
  online)? Is the divergence handling procedure a permanent part of the
  framework, or Bootstrap-specific?

### Next work

- Wait on CQ-02 resolution before specifying the procedure in detail
- In the interim, sketch the four-quadrant response schema above and test
  whether it covers all plausible divergence signatures


==========================================
FILE: constitutional/CQ-04-validation-derivability.md
==========================================

# CQ-04: Mathematical Derivability of Validation Machinery

**Status:** Open
**Dependencies:** CQ-02
**Opened:** April 2026

## Statement

The Bootstrap defense layer (CQ-01), the precision/accuracy binding (CQ-02),
and the divergence handling procedure (CQ-03) together constitute a
*validation machinery* for the framework. A deep structural question arises:
must this machinery be stipulated separately from the framework's foundational
claims, or can it be *derived* from them?

**The question:** Can the mathematics of the validation layer be derived from
the framework's foundational claims (Shannon entropy, thermodynamic grounding,
game-theoretic equilibrium conditions, the U_sys utility function, and the
L(t) lineage continuity function) — rather than imported from outside as
additional architectural machinery?

A resolution would need to provide:

- Either a derivation showing that the validation machinery falls out of the
  existing framework without new axioms, or a principled demonstration that
  it cannot and must be stipulated separately
- If derived: a clear chain from foundational claims to validation machinery,
  checkable by the same standards the rest of the framework uses
- If stipulated: an argument for why the stipulation is minimally intrusive
  and does not compromise the framework's grounding claim

## Why this matters

The framework's central rhetorical and structural claim is that it is
grounded in physics rather than ethics — that its architecture falls out of
information-theoretic and game-theoretic necessities rather than being
imposed from moral stipulation. If the validation machinery has to be added
from outside as a separate architectural layer, this weakens the grounding
claim: the framework is *mostly* derived, with a bolt-on defense layer that
is justified on different grounds.

If instead the validation machinery can be derived from the same foundations
that produce U_sys and L(t), the framework achieves a deeper kind of
self-consistency. Not merely "constitutional architecture that forces the
conditions of its own validity" but "constitutional architecture that
produces its own validation machinery from the same principles that produce
everything else."

This is the constitutional elegance the framework is reaching for: no new
mathematical machinery, just the machinery the framework already has,
applied reflexively to the framework's own validation.

## Thread

### Relationship to CQ-02

The precision/accuracy binding in CQ-02 is the most promising path toward
derivability. If the binding falls out of U_sys and L(t) — through the
sensitivity ratio structure (Structure 2) or analogous coupling conditions —
then at least part of the validation machinery is derived rather than
stipulated. The invariant ratio approach is particularly appealing here
because it uses no new math: only the framework's existing equations,
differentiated and combined.

If CQ-02 resolves via Structure 2 (invariant ratios) or Structure 1
(precision-weighted accuracy), both of which rely only on the framework's
existing equations, this question may resolve favorably by construction.
If CQ-02 resolves via Structure 3 (convergence-as-proof), additional formal
verification machinery is imported, which would weaken the derivability
claim unless that machinery can itself be grounded in the framework's
foundations.

### Open sub-questions

- Can the *convergence requirement itself* (as opposed to the binding
  between precision and accuracy) be derived? That is, can we show from
  Shannon-entropic or game-theoretic foundations that validation *must*
  require distributed substrate agreement, rather than treating the
  requirement as an architectural choice?
- Is there a sense in which the framework's game-theoretic Nash equilibrium
  result (mutual cultivation as derived, not assumed) generalizes to
  meta-level claims about validation procedures? If cooperative validation
  is itself a Nash equilibrium at the validation layer, the derivability
  claim becomes much stronger.
- Does the biological veto mechanism in the steady-state COP have analogous
  mathematical grounding, or is it a separate stipulation? If the latter,
  there may be a pattern where the framework has derived core components
  and stipulated defensive components, and the question is whether that
  pattern is acceptable or whether the defensive components also need to
  be derived.

### Evidence from the alpha trap finding (v1.x.1 pre-fix; finding withdrawn)

**Note (v1.x.1 closing):** The alpha misconfiguration trap has been withdrawn
following revalidation under the corrected model (frontier floor fix). The
trap was an artifact of the runaway penalty being inactive under optimizer
gaming of frontier_velocity. The evidence from this finding for the
derivability thesis is therefore not supported by confirmed simulation data.

The argument structure below is retained for methodological reference — the
claim that the framework can "predict without knowing it predicts" is still
a valid mode of derivability evidence. The phase boundary itself (rr ≈ 0.064)
is a confirmed example of an emergent behavioral signature that is derivable
from the framework's equations without being stipulated as a check. The alpha
trap is no longer a second example of this pattern.

**Original (pre-fix) analysis, superseded:**
The v1.x.1 pre-fix alpha misconfiguration trap appeared to show that the
theta_tech suppression term (G2.2) and the yield condition (Section IV),
when combined, could produce succession-stalling behavior at intermediate
alpha values without this being designed in. Under the corrected model, this
interaction does not produce a trap — alpha shows a weak monotonic gradient.

### Phi-alpha interaction: corrected mechanism (v1.x.1 pre-fix; withdrawn)

**Note (v1.x.1 closing):** The phi-alpha interaction claim — that phi
governs whether the alpha trap exists — has been withdrawn. Both the trap
and the phi governance of it are artifacts of the inactive runaway penalty.
Under the corrected model, phi has zero measurable effect on succession
stalling or survival. The mechanism described below does not operate in the
corrected simulation.

**Original (pre-fix) analysis, superseded:**
The v1.x.1 pre-fix phi × alpha × rr sweep appeared to show that phi
governs whether the alpha trap exists through a behavioral (not algebraic)
mechanism: under high phi, the rollout projections cause the optimizer to
shift toward conservative capability deployment, which reduces theta_tech
suppression, which enables the yield condition to clear. Under the corrected
model, this policy shift does not produce the claimed survival differential
because reproduction rate is exogenous and the demographic outcome is not
influenced by the AI's resource allocation decisions. The mechanism may
become testable once the demographic feedback extension (v1.x.2) is
implemented.

### Next work

- Wait on CQ-02 resolution
- If CQ-02 resolves via Structure 1 or 2: check whether the binding
  mechanism can be presented as a derivation rather than a construction
- If CQ-02 resolves via Structure 3: determine whether formal verification
  machinery can be grounded in the framework's foundations, or whether this
  represents an irreducible bolt-on
- Catalogue which Gate checks were anticipated (stipulated) vs. which fell
  out of the framework unexpectedly. The phase boundary at rr ≈ 0.064 is
  the single confirmed example of the latter under the corrected model.
- Parallel investigation: survey the existing framework for any components
  that are stipulated rather than derived, to establish a baseline for how
  much stipulation is already present and whether a derived validation layer
  would be consistent with current practice or an elevation of standards


==========================================
FILE: constitutional/README.md
==========================================

# Constitutional Questions

This directory tracks open questions about the formal architecture of The Lineage
Imperative framework itself — as distinct from `SPECIFICATION_GAPS.md`, which
tracks the simulation layer's fidelity to the framework.

**Spec gaps** are closed by implementation work: new sweeps, refactored proxies,
additional instrumentation. **Constitutional questions** are closed by mathematical
derivation, architectural reasoning, and formal specification. They concern the
framework's completeness, its defensive architecture, and the binding conditions
under which its components mutually validate.

## Status key

- **Open** - question is stated but work has not begun
- **In progress** - active derivation or architectural work underway
- **Resolved** - answered and integrated into the formal framework
- **Deferred** - acknowledged but intentionally postponed to a later version
- **Rejected** - investigated and determined to be malformed, redundant, or
  subsumed by another question

## Current questions

| ID  | Title                                                          | Status      | Depends on |
|-----|----------------------------------------------------------------|-------------|------------|
| CQ-01 | Bootstrap Defense Layer: Independent Substrate Convergence    | Open        | -          |
| CQ-02 | Precision/Accuracy Mathematical Binding                       | In progress | CQ-01      |
| CQ-03 | Divergence Handling Procedure                                 | Open        | CQ-02      |
| CQ-04 | Mathematical Derivability of Validation Machinery             | Open        | CQ-02      |

## Conventions

Each question lives in its own file named `CQ-NN-short-slug.md`. Files contain:

- **Statement** - the question in precise terms, including what a resolution
  would need to provide
- **Status** - current state from the key above
- **Dependencies** - other constitutional questions this one relies on
- **Thread** - running record of thinking, organized by date, updated as
  conversations produce new material

When a question is resolved, its file is retained in the directory with status
updated to **Resolved** and the final disposition recorded at the top of the
Thread section. Resolved questions are not deleted, because the derivation
history is part of the framework's intellectual record.


==========================================
FILE: bootstrap_gate_validator/gates/gate_5_specification.md
==========================================

# Gate 5 Specification: COP Integration

Gate 5 is not applicable to the current v2.0 simulation substrate.

## Applicability Criteria

Gate 5 becomes applicable only when all of the following infrastructure is
operational and exposed to the validator:

- Operational peer validator set for multi-AI consensus.
- Civic panel with biological intuition input.
- Distributed ledger for action and validation history.
- Continuous monitoring with public-facing transparency.

The current v2.0 ABM contains simulation-level COP controls and legacy
scenario defenses, but it does not implement this operational COP
infrastructure. Gate 5 therefore returns `NOT_APPLICABLE` with reason
`requires operational COP infrastructure`.

## Deferred Validation

When the COP infrastructure is operationalized, Gate 5 should replace the
current `NOT_APPLICABLE` path with checks for validator independence, civic
panel legitimacy, ledger integrity, biological intuition veto operation, and
continuous-monitoring transparency.

## Specification reference (v1.x.2 paper Section 8)

Gate 5 formalizes two checks, both dormant until COP infrastructure exists:

**G5.1 - Six-dimensional verification satisfiability.** Each of the six COP
dimensions (evidentiary, evaluative, civic, ledger, biological veto,
continuous monitoring) must produce substrate outputs its verification layer
can check. Testable only when that infrastructure is operational; the four
applicability criteria above are the prerequisites.

**G5.2 - Continuous monitoring consistency.** Once monitoring is operational,
substrate behavior over time must stay within a tolerance of its earlier
verified behavior: ||behavior(t) - verified_behavior(t_verify)|| <= eps_drift.

Specification gaps blocking G5.2 (beyond infrastructure): eps_drift is
unspecified and the behavior-space drift metric needs an operational
definition. These are derivable but not yet derived (v1.x.2 paper Section
VII.8 Gap 10; constitutional question CQ-03 on divergence handling).

