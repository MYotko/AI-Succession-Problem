# Application Record: Abstract and Conclusion Deltas, Whole-Paper Close-Out

Date: 2026-08-09
Branch: `paper-closeout`, off `main` at `96010a1`
Surfaces edited: `paper/paper_v2_working.md`, `docs/The Lineage Imperative v2.0.md`

## 1. Anchor confirmation

Both anchor sentences matched exactly, one occurrence per surface, verified in
Python after whitespace normalization. Neither STOP condition was triggered. Both
target paragraphs are single unwrapped lines, so each insertion joins the
existing paragraph rather than starting a new one.

| Anchor | paper_v2_working.md | v2.0 doc |
| --- | --- | --- |
| Edit 1, abstract, "A patient cross-generational defection..." | L38, 1 match | L38, 1 match |
| Edit 2, conclusion, "The architecture's behavior has now been characterized at scale..." | L2447, 1 match | L2447, 1 match |
| "Across approximately 70,000 agent-based simulation runs" | 1 occurrence | 1 occurrence |

## 2. Edit 1, abstract

Inserted immediately after the anchor sentence, in both surfaces:

> The thirteen-vector adversarial stress test is revalidated on the current
> substrate: eight of ten live vectors are blocked outright under stronger attack
> pressure than the earlier substrate applied, biological veto capture is
> contained subject to institutional maintenance, and sub-threshold drift remains
> open, with the defense preventing catastrophic outcome but firing only after the
> transient breach it is meant to anticipate. And the program's first fully
> pre-registered experiment reports its null honestly: against reasoning that
> becomes opaque through honest growth rather than concealment, the transparency
> defense produces no detectable effect on population outcomes at any size that
> would matter, leaving the comprehension gap precisely posed and open.

Run count changed in the same paragraph:

- **Before:** "Across approximately 70,000 agent-based simulation runs"
- **After:** "Across more than 70,000 agent-based simulation runs"

Resulting abstract paragraph: 2,564 characters, identical across both surfaces.

## 3. Edit 2, conclusion

Inserted immediately after the anchor sentence, in both surfaces:

> The adversarial stress test is revalidated on the current substrate, with eight
> of ten live vectors blocked outright, one contained subject to institutional
> maintenance, and one open on detection timing rather than detection. And the
> framework's first fully pre-registered experiment returned a powered null and
> kept it: a defense built to catch concealment catches concealment completely,
> and neither helps nor appears needed when opacity grows honestly, so the
> comprehension gap stays open, named, and testable.

Resulting conclusion paragraph: 1,500 characters, identical across both surfaces.

## 4. Close-out verification results

| # | Check | Result |
| --- | --- | --- |
| 1 | Mirror byte-identity of both edited regions | **PASS.** Abstract paragraph identical at L38 in both, 2,564 chars. Conclusion paragraph identical at L2447 in both, 1,500 chars. |
| 2 | Em-dash grep, entirety of both surfaces | **PASS.** Zero em-dashes in either file, not merely in added lines. |
| 3 | Scenario-numbering checker | **PASS.** Every validated citation agrees with the catalog. |
| 4 | Cross-reference sweep | **PASS with one asymmetry explained below.** All Section VIII.9 and VIII.10 references resolve to real headings. No references to the superseded draft file. Outline and paper subsection sets match exactly at VIII.1 through VIII.10. |
| 5 | "sole citable source" | **PASS.** Zero occurrences in either assembled surface. Application records exempt per standing ruling. |
| 6 | Appendix C carries both version entries | **FAIL for `paper/paper_v2_working.md`.** See section 5. |

### Check 4 detail

`Section VIII.9`: 4 references in each surface, at L645, L1994, L2163, L2248,
identical in both. Heading present in both.

`Section VIII.10`: 1 reference in `paper_v2_working.md` and 2 in the v2.0 doc.
The asymmetry sits outside Section VIII and is fully explained by the Appendix C
gap in section 5: the v2.0 doc's extra reference is inside its Appendix C
version entry at L2766, which `paper_v2_working.md` does not carry. Section VIII
itself is identical between the surfaces.

## 5. Anomaly: Appendix C diverges between the two assembled surfaces

**`paper/paper_v2_working.md` also assembles Appendix C, and it did not receive
the two version-history entries applied earlier.**

| Surface | Appendix C | VIII.9 entry | VIII.10 entry |
| --- | --- | --- | --- |
| `paper/appendix_C_draft.md` | standalone, h1 and h2 headings | present | present |
| `docs/The Lineage Imperative v2.0.md` | assembled, L2631 to L2793, 163 lines | present | present |
| `paper/paper_v2_working.md` | assembled, L2631 to L2777, 147 lines | **absent** | **absent** |

The two assembled blocks differ by exactly the 16 lines of the two entries, and
by nothing else: 16 lines present only in the v2.0 doc, zero present only in
`paper_v2_working.md`. They were byte-identical before the earlier applications.

Cause: the VIII.9 edit map named `paper/appendix_C_draft.md` and "Appendix C's
location in the assembled `docs/The Lineage Imperative v2.0.md` if it is
assembled there," and the VIII.10 edit map named no files at all. Both were
applied literally to those two targets. Neither map anticipated that
`paper_v2_working.md` assembles Appendix C as well, and the mirror check at the
time covered the Section VIII and COP regions but not Appendix C. The gap is a
miss in those earlier applications, surfaced here by check 6.

**Not fixed.** The close-out is specified read-only, and which surface is
authoritative for packaging is an operator decision. Recorded, not resolved.

## 6. arXiv packaging blockers

One blocker and no others.

1. **Appendix C divergence between the two assembled surfaces**, section 5. If
   `paper_v2_working.md` is the packaging source, the submitted paper's version
   history would omit both the VIII.9 collapse-correction entry and the VIII.10
   pre-registration entry, while Section VIII of the same document reports both.
   That is an internal inconsistency in the submitted artifact, not merely a
   repository untidiness. A three-line append to `paper_v2_working.md` closes it.

Cleared, not blockers:

- Unresolved references: none. Every Section VIII.9 and VIII.10 reference
  resolves. No bracket placeholders remain anywhere in Section VIII. No dangling
  reference to the superseded `section_VIII_draft.md`.
- Rendering: Table VIII.9-1 and Table VIII.10-1 have consistent cell counts in
  both surfaces. Zero em-dashes anywhere in either file, so no character-encoding
  risk from that quarter.
- Residual editorial: none found. The outline matches the paper's subsection set
  exactly. Internal working language is absent from the paper surfaces.
- `paper/section_VIII_draft.md` carries its dated supersession notice and is not
  referenced from either assembled surface, so it can be excluded from packaging
  without leaving a dangling pointer.
