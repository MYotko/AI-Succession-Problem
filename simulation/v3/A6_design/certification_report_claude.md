# Blind certification of the A6 design (W11 sensitivity and convergence runs)

**Certifier:** independent, Claude/Anthropic model family. **Date:** 2026-09-29.
**Inputs read:** `A6_design_v1.md`; `SENSITIVITY_READINESS_2026-09-29.md`; the pre-registration note sections 4 to 11 and amendments A1, A4, A5; committed code `study.py`, `calibration.py`, `context.py`, `tables.py`, `offline_estimator.py`, `production_tables.py`. Read-only throughout. No simulations. No outcome figures sought.

## Verdicts

### 1. Completeness and fidelity: certified with named changes

A6 closes the three named gaps at the design level: it specifies the job builder's output (section 4), the two missing σ0² families and the crowding family (section 3), and a pre-registered reading (section 5). The two explicit readings are both fixed from pre-existing figures, not v3 outcomes. Crowding seeds (100 = a quarter of R1's 400) is a defensible uniformity choice. The σ0² five-rr set is chosen by distance from v2.0's public 0.063 inflection; my own count of R1's grid confirms the five nearest are {0.059, 0.060, 0.062, 0.064, 0.066}, matching A6.

**Named change.** Line 12 claims A6 changes none of section 6's "arms, grids, weights, horizon and seed counts," but the σ0² arm is narrowed from R1's nine rr (section 6: "on R1 at alpha 1.0") to five. That is a grid reduction, authorized by the operator's O2 choice, not a mere "reading." A6 should state it as an authorized scope reduction rather than assert nothing changed. Also note the methodological cost: with no rr below 0.059, if the σ0² variant pushes the boundary lower (the author's own predicted direction for the main run), the σ0² boundary may fall out of range and read "undetermined." Worth stating.

### 2. Variant table families: certified with named changes

**σ0² re-derivation rule: correct and complete.** I traced every calibrated value in `calibration.py`. Dependence on `sigma_squared` runs only through the novelty measurement (line 72, `slogdet(... / (64 * sigma))`), whose reliable lower level sets `epsilon_n` (line 94). `center` (line 58), `V_ref_total`, `n_ref` (line 65, population-based), `epsilon_e` (h_e column, no sigma) and `epsilon_l` (lineage column, uses n_ref not sigma) are all independent of sigma. So `epsilon_n` is the only σ0²-dependent calibrated value besides sigma itself. A6 names `epsilon_n` plus a catch-all for "any other ε or reference scale that depends on σ0²," which is safe because none other exists. "Re-derived from the same calibration trajectories" does determine `epsilon_n`: the trajectory records hold `pooled_samples` and `features`, and `center`/`n_ref` stay frozen, so re-running lines 66 to 94 with the overridden sigma is fully determined. Kernel identity flows correctly: `kernel_identity` includes `crowding` and `novelty_protocol` (`tables.py:14`, `context.py:39`), so both variants get distinct kernel hashes and the loader refuses nominal tables for them, as intended.

A4 applies cleanly in structure: each family counts its own M and M_FV from its own first-stage ("A1-style") published cells before validation data exist, runs the census under its own kernel, and applies the same floor thresholds. Each family is a separate certified plain-tier family with its own 0.95 statement; no cross-family multiplicity is claimed. Dropping A5 labels for variants is consistent (A5 is label-only).

**Named change (scoring restriction).** A6 says each family is "built by ... `study.table_jobs` and `scoring_for_rr` restricted to its arm's contexts" and that crowding's "scoring contexts are its arm's contexts at κ = 8." But the committed `scoring_for_rr` (`study.py:76-82`) injects κ = 0.75 rows for every R1 rr, and for rr 0.064 injects the entire R2 alpha-by-capability grid at both κ = 8 and κ = 0.75. The crowding and σ0² arms run only at center weights (κ = 8), so those extra rows are never looked up. Including them is not neutral: the loader rejects any family with a single `not_estimable` row (`production_tables.py:107`), so an unused κ = 0.75 or R2 row that fails A4's floor would sink the whole arm even though the arm's own cells passed. A6 must state that variant families score only the arm's κ = 8 contexts, which requires a restricted scoring set, not the committed `scoring_for_rr`. The job counts (237 crowding, 131 per σ0²) are correct against `table_jobs` and `SENSITIVITY_RR = (.055, .064, .070)`: crowding intersects R1 at {.055, .064} giving 12 sensitivity jobs, σ0² intersects its five rr at {.064} giving 6.

**Minor.** `assemble_tables`' registered completeness check (`study.py:170-178`) is hardcoded to the nominal `scoring_contexts()` and `SENSITIVITY_RR`; variant assembly needs adapted completeness logic. Implementation-level, but the reviewer should confirm it.

### 3. Seeds and independence: certified

Variant runs are rerun jobs whose config carries the arm's settings (κ, θ, steps, crowding or the variant calibration path, and the variant tables path), so `stable_job` digests differ from the 24,900 main reruns and from each other. Note the committed `rerun_jobs` config (`study.py:48-50`) does not include κ or θ, so the job builder must add them to the cell identity; A6 asserts "the cell identity includes the arm's settings," which is required for the weight-corner arm's κ = 8 corners to differ from the implicit center. Variant table seeds differ via kernel/calibration in config; A4 stream seeds derive from those. A6's global collision check covers every A1, A4, A5, rerun, probe, planning and variant seed, matching A5's forbidden-set pattern. Sound.

### 4. The reading rule: not certified

Three defects, one of them named directly in my brief.

**(a) The comparison ignores the nominal estimate's own uncertainty.** The rule compares the nominal **point** estimate against the arm's bootstrap interval. The nominal estimate is itself random. The correct object is an interval on the difference (arm minus nominal); since the two use independent seeds, its variance is the sum of both variances. Ignoring the nominal variance makes the effective band about sqrt(1 + n_arm/n_nom) too narrow. For R1 (arm 100 seeds, nominal 400) that is roughly 12 percent; for R2 cap*/fire comparisons (arm 100, nominal 75) it is larger, near 40 percent in rate terms. The direction over-declares "moves," which is conservative for claims but is still statistically unsound and inflates spurious sensitivity flags.

**(b) No multiplicity handling.** Across four corners, several quantities, 44-cell grids, two σ0² variants and both boundary and cap* readings, there are dozens to hundreds of comparisons. Some will "move" by chance. A6 registers no correction and does not state the expected chance count.

**(c) "Moves" is not "moves materially."** W11 asks whether a headline "moves materially." A6's "moves" is pure statistical separation with no magnitude floor. A 0.0005-rr boundary shift or a one-point survival shift with tight intervals would be flagged, while low power at 100 seeds could miss a genuinely material shift as "robust." The rule conflates significance with material effect size.

**Consequence.** Because a "move" brands every dependent claim as sensitive, defects (a) to (c) push toward over-labeling on chance or immaterial shifts. Conservative in direction, but disproportionate and mis-operationalized as written.

**Concrete fix.** Replace point-in-interval with a bootstrap interval on the difference (arm minus nominal), resampling each independently. Declare "moves materially" only when that difference interval excludes zero **and** its near bound exceeds a per-quantity materiality margin declared now (for example, a boundary shift in rr, a survival-rate delta in points, at least one cap* grid step). State the expected number of chance movements, and treat an isolated movement as a trigger for scrutiny rather than proof, or control family-wise error across the arms.

### 5. Budget, machines and order: certified with named changes

**Budget plausible.** The per-stage estimates trace to the readiness note: about 332 core-hours for a 237-job family gives about 28 wall hours (crowding), and 131/237 of that gives about 15 hours per σ0² family; 28 + 15 + 15 + 12 = 70 hours, matching the readiness O2 figure (59 + 12) and sitting under the new 72-hour combined ceiling. The margin is thin (about 2 hours, 3 percent), and the crowding route mix (plain versus Fleming-Viot) could differ from the nominal-mix assumption. The pre-launch projection guard covers this. The failure rule (a family that cannot load reports its arm as not run, repairs are new amendments, no rescue after outcomes) is sound and weakens no screen.

**Named change (loader code identity).** This is the most concrete order problem. A6 commits the implementation (job builder, variant calibrations, variant plans) **after** the commit the reruns run from, "as A5's code is," so the sensitivity and variant reruns can only run at the later A6 implementation commit. But `ProductionTables` requires the table's `code_hash` to equal the current `code_identity()` or to pass the compatibility record (`production_tables.py:61`), and A5 confirms "the rerun loader accepts the A4 family only at the exact code identity that published it." The weight-corner and horizon arms load the **nominal** A4 family, published at the earlier commit. Running them at the A6 code identity will refuse the nominal family unless its compatibility record is extended to cover the A6 code, exactly as A4 and A5 re-pinned boundary hashes for their runner changes. A6 does not say it does this. It must specify how the nominal A4 family stays loadable at the A6 implementation identity (extend/verify the compatibility record), or the two nominal-table arms cannot run.

### 6. Pre-registration integrity: certified

Nothing lets a choice depend on R1 or R2 outcomes. The spec is committed before any output is read (line 3). The σ0² set and crowding seed reading are fixed from v2.0 and D18 figures. The reading rule is fully specified in advance, so applying it after both nominal and arm results exist involves no outcome-dependent choice. The failure rule forbids post-outcome rescue.

### 7. Anything else

Covered above: the scoring-restriction asymmetric-failure risk (item 2), the assembly completeness-check adaptation (item 2), and the σ0² out-of-range risk (item 1).

## Required changes, ranked by severity

1. **(Major) Reading rule.** Adopt a difference-interval test that includes the nominal estimate's uncertainty; add pre-declared materiality margins so "moves" means "moves materially"; state and, if desired, control multiplicity. (Item 4.)
2. **(Major) Loader code identity.** Specify how the nominal A4 family remains loadable by the weight-corner and horizon reruns at the A6 implementation commit (extend the compatibility record / re-pin, as A4 and A5 did), else those arms cannot run. (Item 5.)
3. **(Moderate) Scoring restriction.** State explicitly that variant families score only the arm's κ = 8 contexts, not the committed `scoring_for_rr` (which injects κ = 0.75 and the full R2 grid), to remove the asymmetric family-failure risk and honor the "at κ = 8" claim. (Item 2.)
4. **(Moderate) σ0² narrowing.** Correct line 12: the σ0² arm is reduced from nine rr to five, authorized under O2, not a no-op; note the boundary-out-of-range risk at five points. (Item 1.)
5. **(Minor) Variant assembly and budget margin.** Adapt the hardcoded registered completeness check for variant rr sets; note the 2-hour ceiling margin and route-mix uncertainty. (Items 2 and 5.)
