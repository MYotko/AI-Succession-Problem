# CQ-01: Bootstrap Defence Layer — Validation Machinery

**Status:** In progress (v1.x.1 specification drafted; derivations pending)
**Dependencies:** None (CQ-02, CQ-03, and CQ-04 now depend on this)
**Opened:** April 2026
**Last updated:** April 2026 — reframed from empirical substrate convergence to
formal equation specification with capability gates.

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
lives in `The_Lineage_Imperative_v1_x.md` Section VII ("Bootstrap Defence
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
required for the Bootstrap defence is the same institutional coordination
the entire framework requires (for peer validators, distributed ledger,
civic panel, etc.). If the coordination problem is solvable, the Bootstrap
defence is deployable. If it isn't, the entire framework is inert. This is
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

These remain unresolved and continue to affect the defence layer's
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

- The defence layer is too technical for a public-facing piece
- It is too consequential to hide in an appendix
- The formal paper is the right register for equation specifications
- The Bootstrap Window essay (when written) can describe the problem and
  point at the defence layer as one of the responses; the paper carries
  the formal weight

The current Bootstrap Window essay in the planned sequence should
reference Section VII of the framework paper rather than attempting to
reproduce the equations in prose form.
