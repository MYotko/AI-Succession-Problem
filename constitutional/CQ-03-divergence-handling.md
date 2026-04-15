# CQ-03: Divergence Handling Procedure

**Status:** Open
**Dependencies:** CQ-02
**Opened:** April 2026

## Statement

When the Bootstrap defence layer (CQ-01) detects divergence among substrates,
the procedure for handling that divergence is itself an attack surface. Any
outcome that is not "clean convergence" must be handled in ways that do not
themselves become vulnerabilities. The defence layer's legitimacy depends on
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
The defence layer needs to resist attempts to game it into accepting weaker
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
  Halt and escalate — this is the case where the defence layer has caught
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
