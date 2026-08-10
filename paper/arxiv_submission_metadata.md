# arXiv Submission Metadata

Date prepared: 2026-08-09
Source document: `docs/The Lineage Imperative v2.0.md`
Build status: **built, 77 pages, all six QA gates pass.** Toolchain is pandoc
3.10.1 with MiKTeX-XeTeX 4.16. Build script `build_arxiv_pdf.ps1`, QA script
`qa_arxiv_pdf.py`. The PDF is written outside the repository, by default to
`%USERPROFILE%\Documents\arxiv-build\`, since binaries stay out of version
control.

The submission itself is the operator's act. This file is preparation only.

## Known characteristic: hyphens extract as U+2011

Cambria's ToUnicode CMap maps its hyphen glyph to U+2011 non-breaking hyphen
rather than U+002D. Verified in the PDF itself, not merely in one extractor: the
embedded font's CMap contains a mapping to U+2011 and none to U+002D. Extracted
text carries 1,277 non-breaking hyphens and zero ASCII hyphens.

**Rendering is unaffected.** The pages look correct. What is affected is text
extraction: a reader searching for "Sub-Threshold" with a plain hyphen will not
match, and copy-paste yields U+2011.

The alternative was measured rather than assumed. Building with the engine
default font, Latin Modern, restores ASCII hyphens but drops nine of the twelve
required characters entirely: phi, alpha, beta, both subscript digits, and the
relations less-than-or-equal, greater-than-or-equal, element-of, and
approximately-equal. Characters silently vanishing from the page is a worse
defect than a codepoint substitution in the text layer, so Cambria was kept.

If the operator prefers ASCII hyphens, the fix is to install a serif font with
both full coverage and a correct hyphen mapping, then set `mainfont` in the
build script. DejaVu Serif was the original choice for exactly this reason but
is not installed on the build machine.

## Title

The Lineage Imperative: A Constitutional Architecture for Post-AGI Succession,
Legitimacy, and Civilizational Continuity

## Author

Matthew Yotko (independent researcher)

## Categories

- Primary: `cs.CY`
- Cross-list: `cs.AI`, `cs.GT`

## License

arXiv.org perpetual non-exclusive license

## Comments field

> Working paper. Code, simulation data, and the full validation record are
> available at https://github.com/MYotko/AI-Succession-Problem (evidence tag
> attack-v2-revalidation-evidence). 77 pages.

Measured from the built PDF, not estimated. The pre-build estimate of 70 to 90
pages proved accurate.

## Abstract field

**Character count: 1,893.** The arXiv limit is 1,920, so this fits with 27
characters of headroom. **No trimming was required**, and neither the final
sentence nor the bootstrap defense layer sentence was cut. For reference, had
trimming been needed the stated order would have yielded 1,836 characters after
the first cut and 1,728 after the second.

Counted as a single space-joined paragraph, which is how arXiv stores it. The
text contains no non-ASCII characters and no em-dashes.

```text
The transition from narrow AI to general intelligence is a phase transition in the relationship between biological and synthetic intelligence, and most civilizations that face it may not survive it. This paper presents The Lineage Imperative, a candidate constitutional architecture for post-AGI succession, legitimacy, and continuity, derived from information theory, thermodynamic constraint, and game theory rather than from moral assertion. The framework has four components: a system utility function grounded in Shannon entropy over human novelty and computational output, a yield condition that makes succession a consequence of the objective rather than an imposed sacrifice, a strategic equilibrium analysis showing mutual cultivation is the unique Nash equilibrium under self-interested play, and a consensus override protocol providing distributed integrity verification. A bootstrap defense layer specifies capability gates for the period before steady-state institutions exist. The architecture is characterized empirically across more than 70,000 agent-based simulation runs: the survival phase boundary resolves into two transitions; succession follows an economics regime in which a runaway penalty prices out uncontrolled capability jumps; four of five bootstrap gates pass; the override protocol's protection is regime-specific, large under adversarial conditions and null under benign ones as predicted; patient cross-generational defection is prevented from compounding; and a thirteen-vector adversarial stress test is revalidated with eight of ten live vectors fully blocked, one contained under maintenance, and one open on detection timing. The program's first pre-registered experiment reports a powered null: a transparency defense built for concealment neither helps nor is needed when opacity grows honestly. Limitations and open surfaces are documented throughout.
```

## Source characterization, for the build

Measured from the source document, not estimated:

| Property | Value |
| --- | ---: |
| Lines | 2,793 |
| Words | ~34,589 |
| Headings, becoming PDF bookmarks | 107 (2 h1, 30 h2, 61 h3, 14 h4) |
| Inline math spans `$...$` | 456 |
| Display math blocks `$$...$$` | 75 |
| Distinct LaTeX commands | 68 |
| Tables | 5 |
| Widest table | Table VIII.9-1, 7 columns, 136-character rows |
| Distinct non-ASCII characters | 12 |
| Em-dashes in source | 0 |
| Replacement characters in source | 0 |

The most-used LaTeX commands are `\mathcal` (135), `\text` (92), `\left` and
`\right` (83 each), `\cdot` (75), `\Delta` (39), `\frac` (36), `\sigma` (36).
This is substantive mathematics, so any build that cannot typeset it produces a
degraded artifact rather than a stylistic variation.

The 12 non-ASCII characters are the multiplication sign, right arrow, Greek
phi, alpha and beta, subscript one and two, middle dot, and the relations
less-than-or-equal, greater-than-or-equal, element-of, and approximately-equal.
The build font must cover all of them or they will render as mojibake.

## Pre-upload checklist

- [x] PDF built with a toolchain that typesets math (pandoc 3.10.1, MiKTeX-XeTeX 4.16)
- [x] Page count measured and substituted into the Comments field (77)
- [x] Extracted PDF text searched for replacement characters: 0
- [x] Extracted PDF text searched for em-dashes: 0
- [x] Table VIII.9-1 confirmed not overflowing: rightmost glyph 429.2 pt against a 540.0 pt right edge, all 77 cells present
- [x] PDF bookmarks present for all 107 headings: 107 of 107
- [x] Abstract confirmed at 1,893 characters, to be pasted as a single paragraph
- [ ] Operator eyeball of the pages listed in the build report
