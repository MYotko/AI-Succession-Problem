# arXiv Submission Metadata

Date prepared: 2026-08-09
Source document: `docs/The Lineage Imperative v2.0.md`
Build status: **PDF not built.** No LaTeX engine or pandoc is present on this
machine. See `build_arxiv_pdf.ps1` and the close-out report for options.

The submission itself is the operator's act. This file is preparation only.

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
> attack-v2-revalidation-evidence). [PAGE COUNT PENDING BUILD] pages.

The page count placeholder must be replaced with the real figure once the PDF is
built. Estimate from the source is 70 to 90 pages at roughly 34,600 words plus
five tables and 75 display equations, but an estimate is not a substitute for
the built figure and must not be submitted as one.

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

- [ ] PDF built with a toolchain that typesets math
- [ ] Page count measured and substituted into the Comments field
- [ ] Extracted PDF text searched for replacement characters, expecting zero
- [ ] Extracted PDF text searched for em-dashes, expecting zero
- [ ] Table VIII.9-1 confirmed not overflowing the page
- [ ] PDF bookmarks present for all 107 headings
- [ ] Abstract pasted as a single paragraph, confirmed at 1,893 characters
