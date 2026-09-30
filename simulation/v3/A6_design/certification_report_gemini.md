# Blind Certification Report: A6 Design
**Date:** 2026-09-29
**Verdict:** Not certified. Required changes must be made before adoption.

## 1. Completeness and Fidelity
**Verdict: Certified with named changes.**
A6 successfully closes the three gaps by defining the variant table families, declaring the reading rule, and outlining the job builder's responsibilities. The explicit readings for the crowding seeds (a quarter of R1's seeds = 100) and the $\sigma_0^2$ narrowing are defensible and appropriately fixed before outcomes are known.

However, A6 contradicts itself regarding the registered grids. Section 1 states that "Every other element of section 6 is unchanged: the arms, grids...", yet Section 2 explicitly narrows the $\sigma_0^2$ grid from R1's full 9 `rr` values to the 5 values nearest the boundary. While the narrowing is a pragmatic choice, claiming the grid is unchanged is false. 
**Required Change:** Acknowledge in Section 1 that the $\sigma_0^2$ grid is amended to 5 points.

## 2. The Variant Table Families
**Verdict: Certified.**
The composition of each family is exact. The calculations for the number of jobs (237 for the crowding family and 131 for each $\sigma_0^2$ family) perfectly account for the 25 rules across the respective grids, plus the specific frozen sensitivity subsets (`SENSITIVITY_RR = (.055, .064, .070)` and `SENSITIVITY_RULES`). 

The $\sigma_0^2$ re-derivation rule is correct and complete. The fixed center and reference population size ($N_{ref}$) are determined from independent baseline trajectories that are unaffected by the scaled $\sigma_0^2$. Of the protected levels, $\epsilon_N$ correctly scales with the derived standard deviation, while $\epsilon_E$ and $\epsilon_L$ respond to different observables and do not depend on $\sigma_0^2$. Amendment A4 applies cleanly to the variant families, with $M$ and $M_{FV}$ properly counted per family.

## 3. Seeds and Independence
**Verdict: Certified.**
Because the cell identity used for hashing includes the arm's unique settings (e.g., steps=1000, specific $\kappa$/$\theta$ weights, crowding variant, or calibration), every sensitivity run is guaranteed to hash to a disjoint seed space from the nominal runs and from the other arms. The seed convergence arm correctly reuses the nominal runs.

## 4. The Reading Rule
**Verdict: Not certified.**
The proposed reading rule is statistically unsound and lacks protection against multiplicity. 
A6 applies Section 9's interval rule, which was designed to compare a noisy estimate against a *fixed historical scalar* (v2.0's 0.063), to compare two noisy v3 estimates. By checking if the nominal v3 *point estimate* lies inside the arm's bootstrap interval, the rule completely ignores the variance of the nominal estimate. This drastically underestimates the variance of the difference, guaranteeing severely inflated false positive rates (declaring a movement when the difference is solely due to sampling noise).
Furthermore, with dozens of uncorrected interval comparisons across 5 arms, spurious statistical significance is virtually guaranteed. A tiny, statistically significant but practically meaningless difference would trigger the severe consequence of permanently tagging every W11 claim with the variant's name.
**Required Change (High Severity):** Compare the estimates using the confidence interval of their *difference* (e.g., via independent bootstrap of the nominal and arm results).
**Required Change (High Severity):** Apply a multiplicity correction (e.g., Bonferroni across the comparisons within each arm) and require the interval of the difference to exclude not just zero, but a declared "material" effect-size threshold (e.g., a 5% absolute change in survival or a full capability step).

## 5. Budget, Machines and Order
**Verdict: Certified.**
The 72-hour combined ceiling is plausible based on the readiness note's extrapolations (roughly 28 hours for the crowding tables, 15 hours for each $\sigma_0^2$ table, and 12 hours for the runs, totaling about 70 hours). The execution order is sound, and the strict failure rule (an entire arm fails to load and is reported as not run if any row is not estimable) safely prevents ad-hoc rescues.

## 6. Pre-registration Integrity
**Verdict: Certified.**
The specification is committed before any registered outcomes are read. Narrowing the $\sigma_0^2$ grid based on the historical v2.0 inflection securely breaks any dependence on v3 outcomes. The strict "no rescue" rule for failed families preserves integrity.

## Summary of Required Changes
1. **(High)** Rewrite the reading rule to use the confidence interval of the *difference* between the arm and the nominal result, rather than testing the nominal point estimate against the arm's interval.
2. **(High)** Introduce a multiplicity correction and a minimum "material" effect-size threshold that the difference interval must strictly exceed to declare a movement.
3. **(Medium)** Correct the contradiction in Section 1 by explicitly stating that the $\sigma_0^2$ grid is being amended to 5 points.
