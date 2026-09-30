# A5 Blind Certification Report
**Date:** 2026-09-29
**Author:** Independent Certifier (Reviewer)

## Verdicts

### 1. Validity of the plain-law screen for FV-fitted tables
**Verdict: Certified**
- **Markov-property argument:** The argument is sound. Under the fixed allocation rules of the evaluation model, the state transition probabilities and resulting Bellman residuals depend purely on the current state. They do not depend on the history of the trajectory or the macroscopic regime (plain vs. conditioned FV) that produced the occupancy.
- **Living-source restriction:** Correct. In the Fleming-Viot regime, extinct states are instantly replaced by living states via resampling, meaning transitions only ever propagate from living sources. Validating strictly on living sources matches the effective domain of the tables.
- **Meaning of the certificate:** Validating under the plain law provides a highly meaningful certificate. The certificate formally guarantees that, under the exact plain occupancy law that governs the project's reruns and census, the expected Bellman residual on living-source transitions within published FV cells is bounded by $\tau$. This provides direct assurance for the dynamics the reruns rely on.

### 2. The test
**Verdict: Certified**
- **Empirical Bernstein form:** The test properly implements the Maurer and Pontil trajectory-level empirical Bernstein formula, matching the certified A4 plain tier, correctly using the multiple-testing corrected $\delta = \alpha / M$.
- **Table-conditional width:** The width $w_{row} = (1 - \beta)W + \beta(v_{max} - lower)$ strictly and tightly bounds the residual for any given cell. For a fixed source cell, $V(source)$ is constant, and the variation arises solely from $f \in [lower, upper]$ and $V(next) \in [lower, v_{max}]$ (since extinct states map to $lower$ and transitions to unpublished cells are excluded).
- **Safeguard:** The visit-weighted safeguard successfully guards against correlated trajectory lengths skewing the empirical Bernstein trajectory-mean estimate.
- **Random number of trajectories:** Selecting trajectories by $N_i \ge 1$ makes the sample size $n$ a random variable, but the trajectories that visit the cell are conditionally independent draws from the trajectory distribution. This completely satisfies the assumptions required for the empirical Bernstein bound.

### 3. The family
**Verdict: Certified**
- **M fixed before data:** $M$ is defined as the number of published FV cells in the frozen A4 publication, preventing any data-dependent manipulation of the family size.
- **Separate family:** Asserting plain-law validity over FV cells is a distinct statistical statement from A4's plain tier. It is statistically sound to evaluate this new family of $M_{FV}$ assertions with its own dedicated Bonferroni correction to preserve the $\alpha$ family-wise error rate.
- **Tested but not counted:** Cells with zero or one visit result in an "unresolved" status and are not certified, but they remain counted in $M_{FV}$. Transitions from unpublished cells are explicitly excluded from coverage. No test escapes the correction.

### 4. Label-only soundness
**Verdict: Certified**
- **Reruns unchanged:** By acting purely as a labeling step, A5 preserves the exact values, support, and rules of the A4 tables, ensuring identical rerun execution.
- **Honest citation:** The reruns evaluate allocations and census coverage on plain-law paths. Demonstrating that the FV values hold under those exact plain-law paths provides a highly honest and applicable certificate.
- **Handling of violations:** Disclosing violations without dropping the cells correctly informs the operator. If a cell fails under the plain law, the operator can transparently decide if claims relying on that cell stand.

### 5. Seeds and independence
**Verdict: Certified**
- By using the unique `v3_R_fvplain` hash tag and deriving seeds natively, A5 guarantees deterministic independence from A1 fits, A4 validation, A4 census, and all planning runs.

### 6. The planning evidence
**Verdict: Certified**
- P4 robustly supports the design, showing that a majority of cells can be certified and that these cells cover over 98.5% of plain-law visits. The caveat that the 15-table sample does not guarantee all registered rows will clear a certified-only floor is correctly mitigated by A5's decision to remain strictly label-only.

### 7. Anything else
**Verdict: Certified with named changes**
- Because A5 operates as an independent, non-destructive layer over the A4 artifacts, it creates no race conditions or structural conflicts with A4's publication receipt.
- However, A5's Section 7 ("What A5 does not establish") omits the trajectory-versus-visit estimand gap. While A5 correctly adopts the visit-weighted safeguard from A4, it must explicitly disclose that the rigorous mathematical 0.95 certificate applies only to the trajectory-averaged mean `theta_b^plain`, not the operational visit-weighted mean.

## Required Changes (Ranked by Severity)
1. **Estimand gap disclosure:** Add the trajectory-versus-visit gap to Section 7 ("What A5 does not establish"), explicitly stating that the rigorous certificate bounds the trajectory mean, not the visit-weighted mean. This aligns with the precedent established in A4 version 2.
