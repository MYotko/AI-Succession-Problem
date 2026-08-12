# Future-State Idea: Distributed Cross-Audit Architecture for Check Integrity

**Status: HYPOTHESIS. Not tested, not simulated, not validated. This is a
direction of approach, not a result. Nothing here is evidentiary toward the
framework as it currently stands, and it must never be cited or represented
as such.** It is a design conversation, preserved at idea-level confidence,
sequenced as a post-CUSUM research arc if pursued at all.

## Where it came from

The Sybil defense scaling study (validated, merged) produced a characterized
negative finding: the residual Sybil risk localizes in check integrity, not
pool size. Under measurement corruption (Arm B), the independence check is
compromised far more often (strict failure mean ~0.757) than the pool's true
independent rank is driven below the floor (rank-visible mean ~0.059). The
defense mostly preserves real independence; what it fails to do is know it
has. This is the same failure class as Sub-Threshold Drift: a check reporting
healthy while the measured object is compromised.

This idea is a candidate architecture for hardening that check. It is the
answer to a question the validated study raised; it is not itself validated.

## The core idea, in one line

Make accurate computation easy to perform covertly, and make directed
falsification hard to perform covertly, by denying any single validator
enough global knowledge of the validation topology to corrupt a specific
result without exposing itself.

## The moves that distinguish it

- **Calibration-dominant workload.** Nearly all work presented to validators
  is known-answer calibration; genuine governance-relevant validation is a
  hidden, sparse subset within a constant daily stream. The system does not
  visibly spin up for real events. This decouples semantic visibility (what a
  chunk means) from strategic visibility (whether it matters), which is the
  answer to the semantic-reconstruction objection raised against the earlier
  version.
- **Hidden randomized overlap.** Validators receive overlapping and
  mathematically related chunks without being told which overlap, so
  consistency evidence exists without the audit topology being visible to
  participants.
- **Late-bound random assignment.** The assignment graph is regenerated with
  fresh randomness each period, so long-term reconnaissance does not pay.
- **Commit-then-compare ledger.** An append-only cryptographically verifiable
  ledger provides commitment, ordering, and tamper evidence (not proof of
  correct computation), freezing answers before cross-audit so no validator
  adapts to others' results.
- **Decomposed orchestration.** No single orchestrator knows the whole graph.
- **Effective independent rank, not headcount**, as the security-determining
  quantity, connecting directly to the Sybil study's central result.
- **Incentive framing.** Stated in the framework's own register: not "be
  honest," but an information structure where honest computation preserves
  cover and directed manipulation requires knowledge whose acquisition
  increases exposure. A mechanism-design hypothesis, not yet a dominance
  result.

## The three load-bearing assumptions the threat model must defend, not assume

1. **Calibration indistinguishability.** The whole edifice rests on genuine
   validation chunks being indistinguishable from calibration chunks TO A
   FRONTIER-CAPABLE DISCRIMINATOR, not merely to a statistical test. Frontier
   models are exactly the systems good at detecting distributional anomalies.
   If genuine chunks carry any detectable signature, the attacker flags
   anomalies and focuses corruption there, and calibration density stops
   protecting. This is the semantic-reconstruction problem reincarnated one
   level up and is the single hardest claim in the design.
2. **Cross-audit under correlated validators.** The cross-audit catches a liar
   because independent auditors disagree with the lie. But the framework's own
   thesis is that frontier models converge, so auditors share blind spots.
   Correlated validators can produce consistently corrupted results that
   cross-audit clean against each other without coordination. The scheme's
   security therefore reduces to effective independent rank, the very quantity
   the Sybil study found to be the vulnerability. This is not an independent
   defense against the Sybil floor problem; it is a mechanism whose own
   security depends on the same quantity. At maximum model collapse both
   degrade together. The threat model must state this circularity plainly.
3. **Orchestration decomposition is an unsolved problem, not a bullet point.**
   Distributing task decomposition, randomness, assignment, and aggregation
   without recreating a trusted party in the seams is a hard distributed-
   systems and cryptography problem. Randomness generation alone is load-
   bearing: a corrupted source that only looks random lets an attacker predict
   assignments and collapses the late-binding defense. This is the deepest
   unsolved piece.

## Variant: hide the composition, not the data

A second form of the same underlying move, developed as a follow-on thought.
Same status: hypothesis only.

**The move.** Instead of hiding genuine validation chunks inside an
indistinguishable calibration stream, make ALL the work real and public and
hide only the composition rule that assembles the succession decision from
it. Compute a large, fixed, public space of validation primitives, all of
them genuine, all auditable. The secret is not which chunks matter but which
function selects and composes the governance-relevant result out of the fully
computed space. Concealment moves from the workload (which chunks are real)
to the selection function (which combination is the decision).

**Why this is potentially stronger than the calibration-dominant form.** It
dissolves load-bearing assumption 1 (calibration indistinguishability), the
hardest claim in the calibration approach. If every chunk is real and
computed, there is nothing to distinguish, so a frontier-capable discriminator
gains nothing from knowing what a chunk means, because meaning no longer
correlates with governance relevance. The secret becomes small (a composition
rule) rather than a distributional property (indistinguishability) that an
adversary is actively trying to break. Small, rotatable secrets are easier to
distribute and reason about than indistinguishability properties. This is the
same principle as one-time-pad or compute-over-encrypted-data: the ciphertext
(the public result space) can be fully exposed; all security lives in the key
(the composition rule). Late-bind the composition, regenerate it with fresh
randomness per succession, and distribute it so no single party holds it
whole, and corrupting a specific primitive no longer reliably moves the
outcome, because the attacker does not know whether that primitive is even in
this round's recipe.

**Why the strong "compute the entire space" form does NOT work.** The space of
possible validation calculations over a frontier-model population is not a
bounded, enumerable set. It grows with validator count, their relationships,
the framings of each relationship, and the compositions of those. It is not
finitely computable in any practical sense. The moment it is bounded to
something computable, that bounding is itself a selection an attacker can
attack, reintroducing the hidden-selection problem the exhaustive version
tried to escape. So the workable form is "large fixed PUBLIC primitive basis
plus hidden composition," not "compute everything." No known bounded,
enumerable calculability space for succession assessment is on record, and the
framework's own quantities (novelty entropy, computational entropy, the
lineage term, independence rank) are continuous or population-growing, none
finitely enumerable. Whether some restricted formulation admits a bounded
primitive basis is an open question for the threat-model stage; secure
multiparty computation and functional-encryption literature may have relevant
bounded-basis constructions and should be checked then, not assumed now.

**The concentrated risk this variant carries.** Security relocates rather than
vanishes. It now lives ENTIRELY in the composition function: how it is
generated, kept secret, and distributed so no orchestrator holds it whole.
This is load-bearing assumption 3 (orchestration decomposition) promoted from
one layer among several to the entire ballgame, with no calibration-density
backstop underneath it. If the composition key leaks, or the generating party
is corruptible, or the randomness selecting the composition is predictable,
the whole thing falls. The trade is a hard distributional assumption
(calibration indistinguishability) for a concentrated one (composition-key
secrecy and generation integrity). Whether that is a good trade is an open
research question, not a settled improvement, but it is a legible and more
concentrated trade, which is itself progress. Load-bearing assumption 2
(correlated collusion undermining cross-audit) still applies to this variant
unchanged.

**How the two variants relate.** Not mutually exclusive. The composition-
hiding variant could layer on top of the calibration-dominant one, or replace
its indistinguishability dependence. The threat-model work should evaluate
both and their combination, treating "where does the irreducible secret live,
and how concentrated is it" as the central design axis.

## Variant: hide the function itself (universal-circuit / PFE)

A third form, surfaced from the cryptography literature. Same status:
hypothesis only, and carrying additional unverified-citation and feasibility
caveats noted below.

**The move.** Every validator executes a substantially invariant computational
substrate, a universal circuit U(x, k), where x is validation evidence, U is
fixed universal evaluation machinery, and k is a hidden program/selector that
determines which validation function the envelope actually instantiates
(independence, consistency, provenance, adversarial correlation, a control
task, or a composition). Changing k changes what is computed without changing
the outward computation. This is the literal technical analogue of the "hidden
key" intuition: k is secret configuration information selecting the circuit.

**Why it is a genuine strengthening.** It targets structural leakage directly.
The original semantic-reconstruction worry was "could a frontier-capable
validator infer what its chunk really does from the chunk's structure." A
universal substrate hides not just labels and not just which chunk matters,
but the computational topology that reveals what role a chunk serves. Private
function evaluation exists precisely to hide function structure during
evaluation, so this is an established direction, not an invented one. Valiant's
universal circuit (1970s) is the safe, foundational citation.

**The bound, correctly stated.** This does not give "all calculability." It
gives: every validation program expressible within the protocol's
computational envelope (bounded circuit complexity, input dimension, precision,
execution budget). That set is finite but not enumerated; the universal circuit
represents the CAPACITY to execute any allowed member, like owning a machine
that can display any document rather than storing every document. This is the
correct form of your original "compute the whole space" instinct: fixed
universal envelope plus hidden selector, not exhaustive enumeration.

**CAVEAT 1, unverified citation.** The response that produced this variant
cited a specific 2026 paper claiming SAT-solving can recover hidden functions
from visible circuit topology in weaker gate-hiding schemes, used as the
load-bearing argument for hiding topology too. Valiant and the general
existence of universal-circuit PFE are safe to rely on. That specific 2026
result is NOT verified here and must be checked before it grounds any design
decision; the general principle that structural leakage is a known attack
surface is safe, the specific paper and its SAT-solving claim are a citation
to verify, not to bank.

**CAVEAT 2, cost may be disqualifying, and this is the central open question.**
Universal-circuit PFE carries substantial overhead, historically superlinear
blowup in circuit size. The entire architecture premise is a continuous,
massive validation workload (order 100,000 executions per validator per day).
Multiplying an already-heavy continuous burden by the PFE overhead factor is
exactly where cryptographic elegance meets an economic wall. Universal-
function hiding is simultaneously the most cryptographically satisfying variant
and the most likely to be economically infeasible at the required scale.
Whether it survives is a cost question that must be answered before the
elegance is trusted. The enthusiastic framing of this variant elsewhere omits
this tension; it is the most important thing to record about it.

**CAVEAT 3, do not assume the maximal stack wins.** It is tempting to conclude
the strongest architecture stacks all three variants (constant load + hidden
function + hidden overlap + calibration + commitment + peer audit). Resist
banking that. Stacking concealment layers compounds cost and complexity, and
the combined design's attack surface is the UNION of every layer's failure
modes while its feasibility is the PRODUCT of every layer's cost. More layers
is not automatically more security; it can be more places to break for
diminishing marginal concealment, at multiplied expense. The threat model
should treat "which single layer, or which minimal combination, actually
carries the security" as an open question and credit parsimony, rather than
assuming the maximal stack is best.

**What it does sharpen, honestly.** Even with the caveats, this variant turns
the attacker's problem into a much better-defined adversarial question: to
steer the outcome covertly, an adversary must determine when something matters,
which computation matters, what function the computations collectively
implement, which peers redundantly cover them, which are controls, and which
direction of falsification moves the result, all while committing before
seeing others' answers. That is not proof of security, but it is a
dramatically better-specified problem, and specifying it well is the
precondition for ever testing it.

## Filing and sequencing

- **Confidence level:** idea/hypothesis only. Keep in the idea drawer, never
  the validated record.
- **Paper:** at most a single future-work sentence, if any, pointing at check-
  integrity hardening as the next direction the Sybil finding motivates. The
  Sybil finding itself stands as characterized in Known Limitations; this does
  not.
- **Sequencing:** post-CUSUM. CUSUM is the smaller, bounded, deadline-adjacent
  arc closing an already-characterized surface. This cross-audit architecture
  is large enough that starting it now would repeat the scope-explosion risk
  the Sybil arc kept flirting with. Bank CUSUM first, then give this the
  dedicated threat-model treatment it needs.
- **First artifact if pursued:** not code. A formal protocol-and-threat-model
  specification. For the calibration-dominant form: what a validator sees and
  does not see; how genuine and calibration chunks are made statistically
  similar; overlap selection; commitment; cross-audit evaluation; reliability
  estimation; explicit and correlated collusion representation; institutional-
  validator differentiation; what counts as successful corruption; and the
  acceptable undetected-manipulation probability threshold, fixed before any
  run. For the composition-hiding variant: the public primitive basis and its
  bounding justification; the composition rule's generation, secrecy, and
  distributed custody; the randomness source and its integrity; and the same
  corruption-success and acceptable-probability definitions. For the universal-
  function-hiding variant: the bounded computational envelope's definition; the
  selector/program secrecy and custody; verification of the PFE cost at the
  required continuous scale (the potentially disqualifying question); and
  independent verification of the structural-leakage literature it rests on.
  The specification should treat two questions as the central design axes
  across all three variants: "where does the irreducible secret live, and how
  concentrated is it," and "which single layer or minimal combination actually
  carries the security, at what cost." Parsimony is a virtue to credit, not to
  assume away in favor of the maximal stack. This is pre-registration thinking
  applied to protocol design, the discipline the Sybil arc taught.

## The clean falsifiable question, for when it is pursued

Can a distributed, calibration-dominant, hidden-overlap peer-validation
protocol make covert directed corruption increasingly difficult as the number
of genuinely independent frontier-capability trust domains increases?

Concrete, falsifiable, and directly aligned with the check-integrity
vulnerability the validated Sybil study identified. But it is a question for a
future registered study, not a claim the framework currently makes.
