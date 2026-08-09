# CQ-05: The Expression Boundary: Instantiation versus Extension

**Status:** Open
**Dependencies:** None strictly. Related to CQ-03 (weaponization analysis as method) and to Section II (scope, assumptions, and non-claims).
**Opened:** July 2026
**Origin:** Arose during Tier 1 of the legislative guidance work, on the question of how to classify a requirement whose premise is sourced and whose institutional form is not.

## Statement

The framework describes itself as a conjecture and a constrained proposal with mathematical structure rather than a completed theorem. A thing that describes itself that way expects to be instantiated. Legislative instruments, operator specifications, adopting statutes, and standards documents will each have to express the framework in a form it does not itself supply, because the framework specifies architecture and deliberately declines to prescribe institutions.

This creates a classification problem with governance consequences.

**The question:** What distinguishes a legitimate expression of the framework, meaning an instantiation of something the framework commits to, from an extension that adds structure the framework does not contain?

A resolution would need to provide:

- A test applicable by a reader who did not construct the artifact being tested, and failable by a plausible-seeming extension that does not belong
- A specification of who applies the test, and of what record the application leaves
- An account of whether expressions compose, meaning whether an expression of an expression remains within the boundary
- A treatment of the ensemble case, in which each link in a chain of expressions passes individually and the chain arrives somewhere the framework does not support

## Why this matters

**The framework cannot operate without expression, and cannot survive unbounded expression.** Every downstream artifact instantiates. Without a boundary, each such artifact either under-claims, marking sourced material as invented and weakening what the framework actually establishes, or over-claims, presenting constructed institutional form as derived architecture. The second failure is the serious one, because it launders a drafting choice into a structural requirement and gives it the authority of the framework's grounding claim.

**The boundary is itself a governance surface.** Whoever determines what counts as legitimate expression determines what the framework requires, without amending anything. This is the revision-pipeline attack in the existing attack inventory, aimed at the interpretive layer rather than at the measurement layer. The person who invokes expression three years from now to install something the framework does not imply will do so in good faith and will be wrong, and an unanswered question here leaves nothing to check them against. An open CQ on this point is an open attack surface, not an untidy taxonomy.

**It is the reflexive case.** The framework's own discipline is to apply the specification-gaming test to itself rather than only to the alternatives it retires. This question applies that test to the framework's interpretation rather than to its operation, which is the one place the discipline has not yet been turned.

## Thread

### Candidate approach: a four-condition test

An artifact is a legitimate expression of the framework when all four hold:

1. **The premise is sourced.** The claim the artifact rests on is established in the framework rather than assumed by the artifact.
2. **The mechanism is sourced.** The artifact extends a mechanism the framework specifies rather than introducing a new one.
3. **The extension changes the object, not the behavior.** The mechanism is applied to something new while its specified behavior is preserved.
4. **Its absence would leave a framework commitment with no institutional expression.**

Condition 4 is load-bearing and does most of the discriminating work. Expression fills a slot the framework leaves empty. Extension creates the slot.

### First application, and why it is evidence rather than illustration

The test was constructed against a single provision in the legislative guidance, a conditional-access requirement, and applied to that provision's five clauses. It did not sort them uniformly, which is the property that makes it usable.

Two clauses classified as expression. The premise is sourced in the dependency and cultivation results; the mechanism extended is the graduated trust curve; the curve's specified behavior, asymptotic approach, never reaching unconditional, disproportionate decay on anomaly, is preserved while the object it operates on changes; and without the provision, the framework's dependency commitment has no institutional consequence anywhere in the architecture.

One clause classified as extension. It concerns standing to contest determinations, an object the framework does not address. No mechanism is being extended, and its absence leaves no framework commitment unexpressed. It exists because the drafter identified a hazard and closed it, which is a good reason and not a derivation.

One clause classified as mixed, with its entry condition sourced and its floor a drafting choice the framework does not make.

A test that returns the same answer for everything it examines is not measuring anything. This one returned three answers for five clauses.

### Open sub-questions

**Who applies the test.** The same structural problem as any other pre-committed criterion: the criteria can be published and versioned in advance, and someone still applies them to a particular artifact. That applier holds interpretive authority, and the framework's standing answer elsewhere is that such a role must be independent of the parties to the decision and must leave a record. Whether that answer transfers here is unresolved.

**Whether condition 3 admits degree.** Applying a mechanism to a new object may require parameter changes for the mechanism to function at all. At what point does a parameter change become a behavior change? The conditional-access case did not test this, because the curve transferred without modification.

**Whether expressions compose.** If E1 is a legitimate expression of the framework, may E2 be a legitimate expression of E1? Chained interpretation is the normal mechanism of drift in constitutional systems, and a test that is silent on composition will be applied compositionally by default.

**Whether a commitment inventory is required.** Condition 4 presupposes knowing which commitments the framework makes. No such inventory exists as an artifact. Without one, condition 4 is applied from a reading rather than against a list, which is exactly the softness an adversary would target.

**What status an expression holds once made.** Does a legitimate expression bind subsequent instantiations, or does each adopting instrument re-derive from the framework independently? The first answer accumulates interpretive precedent, with the drift properties that implies. The second discards accumulated work and invites divergent instantiations of the same commitment.

### Weaponization analysis

**Condition 4 is invertible.** An extender who wishes to install a favored institution can read the framework as committing to something it does not commit to, thereby manufacturing an unexpressed commitment for the institution to fill. This is the strongest available attack and it runs directly at the condition doing the most work. The commitment inventory above is the corresponding defense, which is why its absence matters.

**The ensemble case.** Each expression in a sequence passes the test individually while the sequence arrives somewhere the framework does not support. This is the same structure as the amendment-set problem already identified in the attack inventory, where a decade of individually defensible changes exhibits a direction that no single change exhibits. The corresponding defense is set-level audit: expressions recorded with their claimed sourcing, auditable as a chain rather than only as entries. That requirement follows from the record provisions the framework already specifies, if it is applied to expressions and not only to transitions.

**Terminological capture.** "Sourced" and "changes the object rather than the behavior" are contestable in application. An adversary does not need to defeat the test; it needs only to establish a reading of its terms. The framework's usual response to a contestable judgment is to characterize the expected variance and treat excursions as symptoms, which suggests that the rate at which artifacts claim expression status, and the rate at which those claims survive audit, may themselves be monitorable quantities.

### Relationship to CQ-03

CQ-03 established that a procedure which halts and investigates without rollback can be gamed by inducing failures and then arguing for relaxed tolerances, and that the repair is asymmetric, imposing cost on the party applying pressure. The analogous question here is whether a contested expression claim, once rejected, returns the artifact to its prior state or leaves the claim available for re-argument in a modified form. Without an asymmetry, the boundary erodes at the rate an interested party is willing to re-argue.

### Notes on scope

This question concerns the framework's interpretation, not its content. Resolving it does not add to what the framework claims, and leaving it open does not subtract. What it changes is whether the framework's downstream artifacts can be checked against it by someone who did not write them, which is the property the provenance layer of those artifacts exists to provide.

---

## Housekeeping notes for the author, not part of the CQ

**Numbering.** CQ-01 through CQ-04 are occupied; CQ-05 assumed next. Filename following the existing convention would be `CQ-05-expression-boundary.md`.

**Style.** This draft carries no em-dashes, en-dashes, or curly quotes, per the repository style rule. The existing CQ files do contain em-dashes, and CQ-01's filename uses a British spelling. Both are pre-existing and neither is addressed here.

**Provenance.** This is the second item the legislative work has fed back into the framework, the first being the proposed Section V.4 refinement on the civic panel selection specification. Worth noting as a pattern: the instrument-drafting pass is functioning as a stress test on the framework's specification, which is the expected behavior of a downstream instantiation and is evidence the layering is doing its job.
