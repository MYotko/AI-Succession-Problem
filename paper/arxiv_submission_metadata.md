# arXiv Submission Metadata

Date prepared: 2026-08-09
Source document: `docs/The Lineage Imperative v2.0.md`
Build status: **built, 87 pages, all seven QA gates pass.** Toolchain is pandoc
3.10.1 with MiKTeX-XeTeX 4.16, main font DejaVu Serif, math font dejavu-math.
Build script `build_arxiv_pdf.ps1`, QA script `qa_arxiv_pdf.py`. The PDF is
written outside the repository, by default to
`%USERPROFILE%\Documents\arxiv-build\`, since binaries stay out of version
control.

The submission itself is the operator's act. This file is preparation only.

## Font selection, decided by measurement

Three candidates were tested against two gates before any full build: every one
of the twelve non-ASCII characters must render, and hyphens must extract as
U+002D with no U+2011 in the PDF ToUnicode CMap.

| Candidate | Characters | Hyphens | Outcome |
| --- | --- | --- | --- |
| **DejaVu Serif** | **pass**, all twelve | **pass**, zero U+2011 | **selected** |
| STIX Two Text | fail, missing the arrow and the relations less-than-or-equal, greater-than-or-equal, element-of, and approximately-equal | pass | rejected |
| Cambria | pass | fail, 1,277 U+2011 in extracted text | rejected |
| Latin Modern, engine default | fail, drops nine of twelve | pass | rejected |

STIX Two Text fails because those relations live in STIX Two Math rather than
the text face, and the paper uses them as literal text characters rather than
inside math mode.

DejaVu Serif and its math companion come from MiKTeX packages `dejavu`,
`dejavu-math`, and are selected in the preamble by explicit path, because
MiKTeX fonts are not registered as system fonts and family-name lookup fails
for them.

The font change cost ten pages, 77 to 87, since DejaVu Serif is wider than
Cambria. That is the price of correct text extraction and it was accepted.

## Resolved: the two dropped math glyphs

**The build now emits zero missing-character warnings and the PDF contains zero
dropped glyphs.** Recorded here because the diagnosis was not obvious and the
first attempted fix was wrong.

Two headings use bold math, at source lines 2559 and 2577:

```
### 3. $\mathbf{\Psi}_{\mathbf{inst}}\left( \mathbf{t} \right)$; Institutional responsiveness
### 4. $\mathbf{\Theta}_{\mathbf{tech}}\left( \mathbf{t} \right)$; Transfer fidelity
```

Under legacy semantics `\mathbf` selects the upright bold **text** font even
inside math mode. So these requested U+1D6F9 and U+1D6E9, the mathematical
italic capitals, from DejaVuSerif-Bold, which contains neither. Four glyphs were
dropped as notdef marks: in the table of contents on page 3, and in the body
headings on pages 82 and 83.

The first fix attempted was a range-restricted math-font fallback to STIX Two
Math over U+1D6E2 to U+1D6FA. **It did not work and was reverted.** The reason
is instructive: the request never reaches the math font at all, so no
`\setmathfont` range can intercept it. It also had a side effect, silently
re-rendering the ordinary math Greek capitals through STIX.

The working fix is `\AtBeginDocument{\let\mathbf\symbf}`. `\symbf` is
unicode-math's math-font equivalent of `\mathbf`, and it maps Greek capitals to
the bold block at U+1D6A8, which dejavu-math does provide. The
`\AtBeginDocument` wrapper is load-bearing: unicode-math redefines `\mathbf`
itself at begin-document, so a bare `\let` in the preamble is overwritten and
the glyphs stay missing. Both forms were measured; only the wrapped one works.

After the fix the two headings render as U+1D6BF bold capital Psi and U+1D6AF
bold capital Theta, which is the semantically correct bold form. Full accounting:
19 of 19 Psi and 33 of 33 Theta source instances render, zero notdef glyphs, and
zero U+1D6F9 or U+1D6E9 anywhere. Page count is unchanged at 87.

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
> attack-v2-revalidation-evidence). 87 pages.

Measured from the built PDF, not estimated. The count rose from 77 to 87 when
the main font changed from Cambria to the wider DejaVu Serif.

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

- [x] PDF built with a toolchain that typesets math (pandoc 3.10.1, MiKTeX-XeTeX 4.16, DejaVu Serif)
- [x] Page count measured and substituted into the Comments field (87)
- [x] Extracted PDF text searched for replacement characters: 0
- [x] Extracted PDF text searched for em-dashes: 0
- [x] Table VIII.9-1 confirmed not overflowing on pages 31, 61, 62: rightmost glyphs 461.0, 227.1, 411.5 pt against a 540.0 pt right edge, all 77 cells present
- [x] PDF bookmarks present for all 107 headings: 107 of 107
- [x] Abstract confirmed at 1,893 characters, to be pasted as a single paragraph
- [x] Hyphens extract as U+002D: 1,385 ASCII, zero U+2011 in text and CMap
- [x] Zero missing-glyph warnings; 19 of 19 Psi and 33 of 33 Theta render
- [ ] Operator eyeball of the pages listed in the build report
