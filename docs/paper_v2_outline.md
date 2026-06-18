# The Lineage Imperative v2.0: Paper Revision Outline

Status: structural outline for drafting sessions. This is not draft prose. It
specifies section dispositions, where each v2.0 empirical finding lives, the
revision-history handling, and the drafting sequence. Drafting sessions
implement this outline.

Source of record for current claims: `docs/lineage_phi_program_reference.md`
Parts IX and X; `simulation/diagnostics/paper_substrate.md` (quantitative claims
with confidence intervals); `phase_b_integration_analysis.md`;
`cop_finding_framing.md`; `stage2_yield_implementation_notes.md`. The base text
being revised is `docs/The Lineage Imperative v1.x.2.md` (2,154 lines).

All numerical claims in drafted prose must trace to those sources.

---

## 1. Approach

**Revision, not rewrite.** The architectural derivation (U_sys, Yield Condition,
Strategic Equilibrium, COP, two-key architecture) is unchanged in v2.0. The
empirical arc refined and confirmed framework claims rather than restructuring
the framework. v2.0 preserves v1.x.2's section organization and argumentative
arc, expands empirical content, handles superseded framings honestly, and
integrates genuinely new content (Pattern 1, COP regime-specificity,
disambiguated phase boundary) within the existing structure plus one new
consolidated empirical section.

**Audience:** academic-leaning with technical-practitioner accessibility.
Defensible for peer review, readable by working engineers.

**Length:** comparable to v1.x.2, roughly 10 to 20 percent longer to accommodate
the new empirical section. The empirical content summarizes; diagnostic detail
stays in program reference Parts IX and X.

**Revision-history handling (hybrid):** a comprehensive Version History appendix
(Appendix C, moved from front matter and extended) plus three selective inline
footnotes where superseded numbers are most often externally cited.

---

## 2. Section disposition mapping (v1.x.2 to v2.0)

Dispositions: Keep (unchanged or trivial), Light (minor current-state edits),
Expand (v2.0 adds substantively), Revise (framing superseded; rewrite preserving
role), New, Move.

| v1.x.2 section | Disposition | Note |
|---|---|---|
| Version History (front matter) | **Move** | To Appendix C, extended with v2.0 |
| Preface | Keep | |
| I. Abstract | Light | Add one sentence: architecture now empirically validated at scale; preserve conjecture framing |
| II. Scope, Assumptions, Non-Claims | Light | Add non-claim: validation is ABM-based, single architecture class |
| III. Core Assumptions | Keep | |
| IV. Architecture of Mutual Elevation | Keep | |
| V.1 Global Utility Function (U_sys) | Keep | Derivation unchanged; working_factor is implementation detail |
| V.2 Yield Condition | **Expand** | Stage 2 formal yield logic realizes it; point to VIII.4 (Pattern 1) |
| V.3 Strategic Equilibrium | Keep | Nash analysis unchanged |
| V.4 Consensus Override Protocol | **Revise** | One paragraph on regime-specificity of the 73.9pp delta; carries FN-3; point to VIII.6 |
| VI. Two-Key Architecture | Keep | |
| VII. Bootstrap Defense Layer (VII.1-VII.11 intact) | **Heavy** | See per-subsection below |
| VII.3 gate structure + applicability summary | Light | Update applicability to current gate status |
| VII.4 Gate 1 | Light | Add v2.0 result line, point to VIII.5 |
| VII.5 Gate 2 | **Revise** | G2.1 phi-zero superseded by Class B channel; G2.2 weak-gradient superseded by Pattern 1; note Gate 2 PASSED via Piece A; flag formal reintroduction incomplete |
| VII.6 Gate 3 | Light | Add v2.0 result line, point to VIII.5/VIII.4 |
| VII.7 Gate 4 | **Revise** | From "not currently applicable" to PASSED; cap* closed |
| VII.8 Gate 5 | **Revise** | From "not currently applicable" to verified NOT_APPLICABLE; G5.1/G5.2 + eps_drift gap |
| VII.9 Self-application and reporting | Light | Back-pointer to VIII.1 (distinct roles) |
| VII.10 Divergence handling | Keep | Ties to CQ-03, still open |
| Technological Robustness: Quantum | Keep | |
| VII.11 Known gaps (v1.x.1) | **Revise** | Gap closures (see section 7 below) |
| VII.12 Relationship to rest of framework | Light | Pointer updates |
| VIII. Related Work | Light (renumber to IX) | Optional citation refresh |
| IX. Great Filter | Keep (renumber to X) | |
| X. Minimum Deployable Spec | Light (renumber to XI) | |
| XI. Falsifiability | **Expand** (renumber to XII) | Convert "would falsify" criteria to "tested, result"; phase-boundary mechanics move to VIII.2 |
| XII. Conclusion | Revise (renumber to XIII) | Reflect closed validation arc |
| Appendix A. Stress-Test Matrix | Light | COP rows get FN-3 pointer |
| Appendix B. Measurement Protocols | Keep | |

**New: Section VIII "Empirical Validation at Scale"** (inserted after VII).
**New: Appendix C "Version History and Empirical Refinement Record"** (moved
from front matter, extended).

Tally: Keep ~11, Light ~10, Expand ~3, Revise ~6, Move 1, New 2, Cut 0,
Reorder 0 (aside from the insertion-driven renumber).

### Renumbering (old to new)

| v1.x.2 | v2.0 |
|---|---|
| VII (VII.1-VII.11 intact) | VII (unchanged) |
| (none) | **VIII Empirical Validation at Scale (new)** |
| VIII Related Work | IX |
| IX Implications for the Great Filter | X |
| X Minimum Deployable Governance Specification | XI |
| XI Falsifiability and Evaluation Criteria | XII |
| XII Conclusion | XIII |
| Appendix A Stress-Test Matrix | Appendix A |
| Appendix B Measurement Protocols | Appendix B |
| (front-matter Version History) | **Appendix C (moved, extended)** |

---

## 3. Section VIII structure and empirical findings assignment

New consolidated section, ~20-28 pages. Subsections and the findings each owns
(primary), with secondary cross-references into existing sections.

### VIII.1 Methodological approach (new)
- The ~70,000-run investigation arc across Stage 1.5 through Stage 2, the phi
  Pieces, and the gate validations.
- Public development as methodology; pre-committed metric revision as discipline
  (the metric-revision pattern: cosine to trajectory divergence; threshold
  revisions; documented in real time).
- Convergence-signal aggregation extended to v2.0's actual record.
- Cross-ref: VII.9 (forward self-application spec; distinct role).
- Source: Parts IX.10, X.1.

### VIII.2 Phase boundary characterization (refinement)
- Two-transition disambiguation: phi-sensitivity transition near rr approximately
  0.057; survival-rate phase boundary at the rr=0.060 to 0.066 transition with a
  50 percent inflection near rr=0.063.
- Refines v1.x.2's single-rr framing.
- Cross-ref: XII Falsifiability; X Great Filter (phase-transition framing, light).
- Source: paper_substrate 1.1-1.4; Part X.2.

### VIII.3 Phi behavior characterization (refinement)
- U-shape at marginal rr (roughly 10pp); horizon-resonance mechanism (Mechanism
  C supported, Mechanism D rejected).
- No-succession scope: the U-shape is flat under active succession (Piece A).
- Default revision phi=10 to phi=25 per current evidence.
- Carries **FN-1**. Cross-ref: VII.5 (Gate 2 G2.1); V.1 (phi parameter).
- Source: Part IX.2-IX.7.

### VIII.4 Pattern 1: succession economics regime (new)
- The (alpha, successor-to-incumbent capability ratio) joint position governs
  succession viability; alpha-driven cliff (beyond 4x at alpha=0.5, 3.0x at
  alpha=1.0, 2.5x at alpha=1.5).
- cap* gap closure from the v1.x.2 paper (Gap 4): cap* empirically alpha-dependent.
- Multi-generational continuity below the cliff: 99.8 percent knowledge transfer,
  mean final generation 2.13 (per Gate 3 G3.3). Framed as architectural
  validation, not a gate verdict.
- Carries **FN-2**. Cross-ref: V.2 (yield economics); VII.6/VII.7 (Gate 3/4).
- Source: paper_substrate 2.1-2.3; Part IX.8, X.3.

### VIII.5 Gate validation outcomes (procedural closure)
- Gates 1-4 PASSED; gate 5 verified NOT_APPLICABLE. What each gate validated
  under v2.0.
- G3.3 line: "PASSED; see VIII.4 for the substantive continuity findings."
- Caveat: Gate 2 PASSED via Piece A; the formal G2.1/G2.2/G2.4 reintroduction is
  in progress (incomplete, on a work-in-progress branch).
- Cross-ref: VII.4-VII.8 (each gate spec); VIII.4.
- Source: Part IX.9.

### VIII.6 COP regime-specificity (refinement)
- The v1.x.2 73.9pp protective delta was an adversarial-conditions measurement
  (block_succession incumbent inflating transition cost via beta_cap).
- Phase B Category C measured the complementary benign-conditions prediction and
  found no detectable effect (delta -0.47pp, pair SE 0.96pp), the predicted
  baseline. The COP claim is preserved and regime-characterized.
- Cross-ref: V.4 (architectural, FN-3); Appendix A (COP attack rows).
- Source: cop_finding_framing; Part X.4.

### VIII.7 Limitations of empirical validation (new)
- COP architecture not operationalized (Gate 5 dormant).
- COP benign-conditions characterization not testable in current substrate.
- Pattern 1 cliff at default constants; calibration sensitivity not exhaustively
  explored.
- Phase boundary located to a 0.002-rr grid; finer resolution possible.
- All validation ABM-based; multi-architecture validation pending.
- Gate 2 formal reintroduction incomplete.
- Cross-ref: VII.11 (specification-level gaps, distinct from these
  validation-level limitations); II Scope.
- Source: Part X.7.

---

## 4. Footnote candidates (3)

Brief, factual, not defensive; each points to Appendix C.

**FN-1 (VIII.3, phi survival effect):** "Earlier versions reported a larger phi
survival effect (up to 46 percentage points in v1.0; an interim 20 to 27 point
cap-conditional gradient in v1.x.2). Those figures did not reproduce: the v1.x.1
frontier-velocity floor fix and a capped-regime RNG-desynchronization artifact
account for them. The bounded, marginal-rr effect characterized here is the
current finding; see Appendix C."

**FN-2 (VIII.4, alpha):** "An earlier 'alpha misconfiguration trap' (a claimed
U-shaped, non-monotonic alpha-survival relationship) was withdrawn after the
v1.x.1 frontier-velocity floor fix showed it to be an artifact of an inactive
runaway penalty. The Pattern 1 characterization here (an alpha-driven succession
cliff) is the current understanding; see Appendix C."

**FN-3 (V.4, COP protective delta):** "The 73.9 percentage point COP protective
delta is an adversarial-conditions measurement (an incumbent inflating
transition cost under attack). It is regime-specific, not a general survival
differential; a benign-conditions probe finds no detectable effect, which is the
predicted baseline. See VIII.6."

All other refinements are handled in Appendix C only.

---

## 5. Appendix C specification (Version History and Empirical Refinement Record)

**Origin:** the existing front-matter Version History (v1.x.2 lines 9-282) moves
here, cleaning the front matter (Preface to Abstract), per academic convention.
Extended with a v2.0 section.

**Format:** chronological by version (v1.0, v1.x, v1.x1, phi characterization,
GAP-03, biological veto, transition cost, frontier floor fix, v1.x.1 closing,
v1.x.2 phi withdrawal, then v2.0). Each entry: version, date, what changed; for
refined or withdrawn claims a one-line "claim to disposition to current home."

**Opening paragraph (thesis):** public development and pre-committed metric
revision as the discipline that produced these refinements. States it; points to
VIII.1 for the expanded treatment.

**Claims to document (progression to current home):**

| Claim | Progression | Home |
|---|---|---|
| Phi extinction buffer | v1.0 ~46pp; v1.x.1 corrected ~0 (floor fix); v1.x.2 cap-conditional withdrawn (RNG artifact); v2.0 bounded Class B channel (Stage 1.6), default 10 to 25 | VIII.3 |
| Alpha trap | v1.0 U-shaped trap; v1.x.1 withdrawn (weak monotonic); v2.0 Pattern 1 cliff | VIII.4 |
| Transition cost | v1.x.1 canonical form calibrated (k1=2.164, k2=1.0, beta=0.5); v2.0 confirmed under formal yield | VIII.4, V.2 |
| cap* | v1.x.2 unknown gap (Gap 4); v2.0 closed (alpha-dependent) | VIII.4 |
| COP protective effect | v1.x.2 73.9pp (adversarial); v2.0 regime-specificity characterized (benign null complementary) | VIII.6 |
| Phase boundary | v1.x.2 single-rr framing; v2.0 two-transition disambiguation | VIII.2 |
| Gate validation | v1.x.1 specified; v2.0 gates 1-4 PASSED, gate 5 verified NOT_APPLICABLE | VIII.5 |

**Tone:** factual, refinements-as-feature. Per entry: one short paragraph.
**Length:** ~5-8 pages.

---

## 6. New content placement (summary)

- **Section VIII** (new): the consolidated empirical home (VIII.1-VIII.7 above).
- **Appendix C** (moved + extended): version history and refinement record.
- Pattern 1 (VIII.4) and the methodology narrative (VIII.1) are the principal
  net-new content. The empirical-limitations set (VIII.7) is new. No orphan
  content: every v2.0 finding has a primary home and its secondary pointers.

---

## 7. Open questions and limitations placement

Two distinct sets, kept separate and cross-referenced.

**Validation-level limitations (VIII.7):** what the empirical validation did not
establish (COP not operationalized; benign-conditions COP untestable here;
Pattern 1 calibration sensitivity; phase-boundary resolution; ABM-only,
multi-architecture pending; Gate 2 reintroduction incomplete). Each roughly 0.3
to 0.5 page.

**Specification-level gaps (VII.11, revised):** what the specification has not
yet derived. Closures and reframings:
- Gap 1 (phi buffer): reframed to the Class B bounded channel (VIII.3).
- Gap 2 (alpha trap): reframed to Pattern 1 (VIII.4).
- Gap 4 (cap*): closed empirically (VIII.4).
- Gap 11 (termination sweep revalidation): superseded by Phase B (VIII.2).
- Gap 12 (demographic feedback): phi channel now exists; demographic extension
  still future.
- Gaps 3, 5, 6, 7, 8, 9, 10 persist (transition cost resolved already; theta
  floor derivation, substrate transparency, base-capability operationalization,
  tolerance bands, Nash counterfactual set, gate dependency structure).

**Scope (II):** add one non-claim line scoping validation as ABM-based, single
architecture class.

**Falsifiability (XII):** a short "what remains untested" paragraph naming the
still-open criteria and pointing to VIII.7.

---

## 8. Drafting sequence

- **Phase 1 (foundational, parallelizable):** Section VIII (VIII.1-VIII.7) and
  Appendix C. New substantive content drafted from settled diagnostic sources;
  VIII subsections parallelize (distinct source docs each); Appendix C
  independent. ~3-4 sessions.
- **Phase 2 (depends on VIII settled):** cross-referencing revisions: V.2 expand,
  V.4 revise, VII.3 applicability, VII.4-VII.8 result lines, VII.11 gap closures,
  XII Falsifiability reframe. ~1-2 sessions.
- **Phase 3 (light pass, anytime):** II non-claim line; light-keep sections (III,
  IV, V.1, V.3, VI, IX, X, XI, Appendix A/B). ~1 session.
- **Phase 4 (last):** Abstract revision, Conclusion (XIII), the three footnotes,
  full cross-reference verification, de-em-dash and American-English consistency
  pass. ~1 session.

**Critical path:** Phase 1 (VIII) gates Phase 2 and Phase 4. Appendix C and Phase
3 float in parallel. Estimated **5-7 drafting sessions across 4-6 weeks**.

Estimated effort by block: Section VIII ~20-28 pp (bulk); Appendix C ~5-8 pp;
V/VII revisions moderate; light keeps plus front/back matter low.

---

## 9. Cross-reference map

Which sections cite which empirical findings (drafting must keep these
bidirectional pointers consistent):

| From | To | What |
|---|---|---|
| V.2 Yield Condition | VIII.4 | Stage 2 formal yield realizes the condition; Pattern 1 |
| V.4 COP | VIII.6 | Regime-specificity of the protective delta (FN-3 here) |
| VII.3 applicability summary | VIII.5 | Current gate status |
| VII.4 Gate 1 | VIII.5 | PASSED result |
| VII.5 Gate 2 | VIII.3, VIII.5 | G2.1 phi reframe; Gate 2 via Piece A; reintroduction incomplete |
| VII.6 Gate 3 | VIII.4, VIII.5 | G3.3 continuity in VIII.4; PASSED in VIII.5 |
| VII.7 Gate 4 | VIII.4, VIII.5 | cap* closure; PASSED |
| VII.8 Gate 5 | VIII.5, VIII.7 | Verified NOT_APPLICABLE; limitation |
| VII.9 Self-application | VIII.1 | Forward spec vs empirical record (distinct roles) |
| VII.11 Known gaps | VIII.2, VIII.3, VIII.4 | Gap closures/reframes |
| XII Falsifiability | VIII.2, VIII.5, VIII.7 | Criteria tested; results; what remains |
| II Scope | VIII.7 | ABM-only non-claim |
| Appendix A Stress-Test | VIII.6 | COP attack rows; regime-specificity |
| Appendix C Version History | VIII.2, VIII.3, VIII.4, VIII.6 | Each refined claim's current home |
| VIII.1 Methodology | VII.9 | Self-application as exercised |
| VIII.4 Pattern 1 | V.2, VII.6, VII.7 | Yield economics; gates |
| VIII.6 COP | V.4, Appendix A | Architectural discussion |

---

## Hard constraints for drafting sessions

- Revision, not rewrite; preserve v1.x.2 structure and argument; deviations need
  explicit reasoning.
- v1.x.2 production code, paths, and test fixtures untouched.
- No em-dashes. American English.
- "Not ethics. Physics/Mathematics." used sparingly at earned positions only.
- Numerical claims traceable to program reference Parts IX/X or
  `paper_substrate.md`.
- Footnotes brief and non-defensive; full progression in Appendix C.
