# Blind certification comparison: continuation validation design (version 1)

**The halves:**
- **Gemini half:** Gemini 3.1 Pro through Antigravity, `cert_gemini\certification_report.md`, about 1,000 words.
- **Claude half:** a fresh headless Claude Code session, `cert_claude\certification_report.md`, about 2,000 words.

Both worked from the same directive, `CERT_DIRECTIVE.md`, blind to each other. The reviewer compared them on 2026-09-29.

## Verdicts

| Item | Gemini | Claude | Agreement |
|---|---|---|---|
| 1. Living-source restriction | certified | certified | yes |
| 2. Population-0 refit | certified | certified, minor note | yes |
| 3. Empirical Bernstein | certified | certified, full re-derivation | yes |
| 4. A priori width | certified | certified, wording note | yes |
| 5. Estimand | with changes | with changes | yes, the same change |
| 6. Global family | certified | certified, notes | yes |
| 7. FV asymptotic tier | with changes | with changes | yes, different remedies |
| 8. Seeds and independence | certified | certified | yes |
| 9. Availability floor | **not certified** | certified | no: an implementation gap, resolved below |
| 10. Other interactions | certified | notes | Gemini made a factual error, below |

**Depth.** Claude re-derived every formula: the two-sided `ln(4M/alpha)`, the width rescaling, strict diagonal dominance of the refit matrix, `lower <= C0 <= upper`, and the delta-method expansion. Gemini's reasoning was correct where it went, but shallower.

## Accepted changes, now in version 2

1. **Estimand (both).**
   - Disclose that the certificate bounds the trajectory mean, not the visit-weighted mean (section 7).
   - Add a safeguard: a certified plain cell is published only if its visit-weighted point estimate is also within tau (section 4). Claude proposed exactly this, and the reviewer had reached the same remedy independently.
2. **Family (Claude).** M is counted on the registered set after the population-0 merge, not taken from the P3 planning value. The 0.95 statement covers the plain route only (section 4).
3. **FV small-sample practice (both asked for better practice).** Added: a Fieller interval at the same t critical value, which a cell must also pass (section 5).
   - **Correction:** a first draft said Fieller "should almost always agree" with the delta method. The reviewer checked this on P1 and it was wrong. Fieller is stricter: 84.0% of cells pass against 92.2%. The passing cells still hold 99.998% of visits.
4. **Census (Gemini, item 9).** The committed `endpoint_counts` reports only the overall fraction. The registered code adds the low-population fraction under the same law (section 6). This resolves Gemini's "not certified": the gap was in implementation, not in the design's logic.
5. **Documentation (Claude, items 2, 4 and 10):**
   - neighboring cells are retested against C0;
   - the width is fixed before the test replicates, and depends on the fitting replicate;
   - unavailable scores take the committed fallback, so the floor bounds how often fallbacks happen;
   - one failing row halts every rerun, through the committed all-or-nothing `require_production`;
   - the validated support ships as a new manifest, because the A1 files are frozen.

## Rejected

1. **Bootstrap intervals for the FV tier:** Gemini proposed percentile intervals, and Claude named BCa as a second option. The family needs a tail of `alpha/(2 M_FV)`, about 3e-8. With 32 groups, a bootstrap cannot represent that tail: resampled means are bounded by the observed group values, so the extreme quantiles collapse to the sample extremes. Fieller was adopted instead.
2. **Gemini's item 10 claim** that the allocator "raises a KeyError and halts" at an unpublished cell. This is wrong. `v3/integration.py` calls `lookup_available` and takes the documented fallbacks; the reviewer verified this in the code. Claude's account is correct.

## Result

The design is certified by both halves once the accepted changes are in. No item needs a new round: the one "not certified" was an implementation gap, now specified. Version 2 is ready for the operator.
