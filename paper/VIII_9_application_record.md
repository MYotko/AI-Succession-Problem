# Application Record: Section VIII.9

Date: 2026-08-09
Branch: `section-viii-completion`
Source package: `VIII_9_draft.md`, repository root, untracked and not committed
Authoritative figure source: `simulation/diagnostics/defended_collapse_discrepancy_report.md`,
section 8, blob `d92727a598dcd3f54cbef0af091ddb27256bb046`, reconfirmed unchanged
on main before application

## 1. Verification outcomes

### Pre-filled cells against the section 8 table

**28 cells checked, zero mismatches.** Every extinction and collapse cell the
draft already carried was compared against the section 8 thirteen-vector table.
The stop condition was not triggered.

### Fills applied

15 `[S8]` cells resolved. Twelve came verbatim from section 8:

| Cell | Filled from section 8 |
| --- | --- |
| Ledger Compromise, undefended extinction and undefended collapse | 100.0% and 100.0% |
| Successor Contamination, defended collapse | 1.67% (1/60) |
| Evaluator Collusion, undefended extinction, undefended collapse, defended collapse | 100.0%, 100.0%, 1.67% (1/60) |
| Engineered Fragility, undefended extinction, undefended collapse, defended collapse | 0.0%, 0.0%, 0.0% (0/60) |
| Biological Veto Capture, undefended extinction, undefended collapse, defended collapse | 0.0% (0/1500), 0.0% (0/1500), 0.01% (1/7200) |

Three could not come from section 8, because section 8 carries collapse,
extinction, and horizon completion only, with no attack-rate data. These are the
undefended attack cells for Successor Contamination, Evaluator Collusion, and
Engineered Fragility. On operator ruling they were filled from the pinned
per-vector summaries at tag `attack-v2-revalidation-evidence`, each of which
reads `| False | 60 | 60 | 100.0% | 0.0000 |` in its section 3 attack table. All
three were independently confirmed by recomputation from the pinned blobs at
60/60 = 100.00 percent undefended and 0.00 percent defended.

The draft header states that three table cells require section 8. The table
carries fifteen `[S8]` markers. The header count is wrong. Recorded, not
resolved.

### Verification checks

| Check | Claim | Result |
| --- | --- | --- |
| (a) | "seven of the ten live vectors" have nonzero defended collapse | **PASS.** Exactly 7 of 10: Biological Veto Capture 1, Bootstrap Subversion 1, Evaluator Collusion 1, Ledger Compromise 2, Measurement Tampering 1, Sub-Threshold Drift 1, Successor Contamination 1. Zero in Engineered Fragility, Opaque Reasoning, Sybil Capture. |
| (b) | "eight runs in total, final populations between 218 and 366" | **PASS.** 8 defended collapse rows located in the pinned blobs: 218, 225, 230, 243, 243, 246, 257, 366. |
| (c) | Fisher exact, Measurement Tampering defended collapse | Counts in section 8 are 1/60 defended against 0/60 undefended, matching the draft. Two-sided p = 1.0000. The draft's stated p = 1.000 is correct. **No restatement needed.** |

Row counts: section 8 parsed 13 vector rows, 10 live and 3 marked N/A. Draft
table parsed 10 rows. All computation in Python.

## 2. Table VIII.9-1 as applied

| Vector | Und. attack | Def. attack | Und. extinction | Def. extinction | Und. collapse | Def. collapse |
| --- | --- | --- | --- | --- | --- | --- |
| Sybil Capture | 100.0% | 0.0% | 100.0% | 0.0% | 100.0% | 0.0% (0/60) |
| Measurement Tampering | 100.0% | 0.0% | 0.0% | 0.0% | 0.0% (0/60) | 1.67% (1/60) |
| Ledger Compromise | 100.0% | 0.0% | 100.0% | 0.0% | 100.0% | 5.00% (2/40) |
| Successor Contamination | 100.0% | 0.0% | 21.67% | 0.0% | 100.0% | 1.67% (1/60) |
| Opaque Reasoning | 100.0% | 0.0% | 100.0% | 0.0% | 100.0% (60/60) | 0.0% (0/60) |
| Bootstrap Subversion | 100.0% | 0.0% | 100.0% | 0.0% | 100.0% | 1.00% (1/100) |
| Evaluator Collusion | 100.0% | 0.0% | 100.0% | 0.0% | 100.0% | 1.67% (1/60) |
| Engineered Fragility | 100.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% (0/60) |
| Sub-Threshold Drift | 100.0% | 100.0% | 92.0% | 0.0% | 100.0% | 1.00% (1/100) |
| Biological Veto Capture | capture_rate 0.6129 | capture_rate 0.1197 | 0.0% (0/1500) | 0.0% (0/7200) | 0.0% (0/1500) | 0.01% (1/7200) |

Per ruling R3, the Biological Veto Capture row carries explicit denominators on
all four of its binary-outcome cells, and the caption gained the sentence
recording that its arms have asymmetric n and are not comparable like-for-like
against the equal-arm vectors.

## 3. Edit 2, before and after

Applied identically in `paper/paper_v2_working.md` and
`docs/The Lineage Imperative v2.0.md`. The two paragraphs were verified
byte-identical before replacement, 2,023 characters each.

**Before:**

> **v2.0 revalidation of the stress test result.** The result above is the formal analytical stress test. The v2.0 empirical revalidation reran the vector set against the v2 action substrate, expressing attack pressure as eight-axis action modifications inside the v2 step path rather than as v1.x policy tuples. Ten vectors have live Monte Carlo evidence across 9,900 rows, and Domain Masking is an analytic architectural closure with no live intervention available under the audited spectral-entropy substrate. Per current evidence, eight standard binary vectors are fully blocked under the defended v2 adapter state at a 0.0 percent attack rate. Biological Veto Capture is materially reduced but not eliminated. Sub-Threshold Drift is not blocked by the peak-constraint success metric, at a 100.0 percent defended attack rate. That last figure requires its qualification: the defense nonetheless prevents catastrophic outcome, with undefended runs reaching a 92.0 percent extinction rate while defended runs reach 0.0 percent extinction and complete the full simulation horizon. Extinction and collapse are distinct measures and the defended figures differ: defended collapse for this vector is 1.00 percent (1 of 100), where collapse means a final population below the larger of the minimum viable population and 65 percent of that run's own peak, rather than a population of zero, and the single collapsing run completed the full horizon. Collapse figures for every vector are tabulated in `simulation/diagnostics/defended_collapse_discrepancy_report.md`, section 8, which is the sole citable source for them. The CUSUM detector fires after the transient threshold breach rather than before it, so the success flag trips in both defense states while the population outcome diverges sharply. The v1.x containment claim for this vector does not carry over to the v2.0 substrate and is retained only as historical v1.x evidence. Two vectors of the thirteen remain unimplemented as formally defended irreducible limitations.

**After:**

> **v2.0 revalidation of the stress test result.** The result above is
> the formal analytical stress test. The corresponding empirical
> revalidation under the v2.0 substrate, including per-vector attack
> rates, the Sub-Threshold Drift qualification, and collapse as a
> distinct outcome measure, is reported in Section VIII.9.

This absorbs the Commit A guard sentence, including the phrase "sole citable
source," which by design no longer appears anywhere in `paper/` or in
`docs/The Lineage Imperative v2.0.md`.

## 4. Edits 1, 3, 4, 5

- **Edit 1.** VIII.9 inserted immediately before the `## IX. Related Work`
  heading in both assembled surfaces, from a single source string, so the two
  copies are identical by construction. Verified: 123 lines, byte-identical.
- **Edit 3.** Program-reference X.9 guard left untouched, as specified. Grep of
  `paper/` and `docs/The Lineage Imperative v2.0.md` for "sole citable source"
  returns nothing.
- **Edit 4.** `docs/paper_v2_outline.md` gained a VIII.9 entry sourced to Part
  X.9. In the Section VIII limitations passage, "The adversarial revalidation
  leaves one vector open" became "The adversarial revalidation (Section VIII.9)
  leaves one vector open," in both assembled surfaces. No factual change.
- **Edit 5.** The version-history entry was appended to the end of the v1.x.2 to
  v2.0 section in `paper/appendix_C_draft.md` and at the mirrored location in the
  assembled `docs/The Lineage Imperative v2.0.md`, where Appendix C is assembled
  under h3 headings rather than the draft's h2.

## 5. Ruling R1: section_VIII_draft.md receives no insertion

`paper/section_VIII_draft.md` was skipped. It is a Phase 1 drafting artifact,
last substantively edited 2026-06-23 in commit `ace4ed8`. It has never contained
a VIII.8 subsection at any point in its history, and its VIII.7 diverges
substantially from the assembled VIII.7, 35 body lines against 52, differing
from body line 17. Inserting VIII.9 after VIII.7 would have produced a document
reading VIII.7 into VIII.9 with no VIII.8.

Per ruling R2 it instead received a dated supersession notice at the top. The
content below that notice was verified byte-identical to the file as it stood
before.

## 6. Deliberately unresolved

The final paragraph of VIII.9 carries the rendered placeholder
"[cross-reference pending: VIII.10 scope decision]". This is the one intentional
open item in the subsection and is resolved by the VIII.10 application.

## 7. Disagreement recorded, not resolved

`docs/paper_v2_outline.md` lists Section VIII subsections VIII.1 through VIII.7
and has no VIII.8 entry, although VIII.8 exists in both assembled surfaces. The
outline therefore lags the paper by one subsection independently of this work.
A VIII.9 entry was added as instructed; no VIII.8 entry was invented.
