# Blind Certification Report: Continuation Validation Design

## 1. Living-source restriction
**Verdict:** Certified.
**Reasoning:** In `production_tables.py`, the `lookup` method suppresses the missing bin error for extinct endpoints and returns zero, but the engine handles extinct states explicitly (e.g., by directly assigning `extinction_flow`). The Bellman value of an extinct state is mathematically fixed to `lower`. The engine does not use the tabulated continuation value for an extinct state. Thus, excluding extinct sources from the fit correctly avoids polluting the tabular values with the degenerate post-extinction trace. This does not bias the value for living states because transitions from living to extinct correctly use the fixed `lower` value.

## 2. The plain population-0 refit
**Verdict:** Certified.
**Reasoning:** The Bellman fixed point `C0 = a / (N - beta T)` is well defined and unique because `T <= N` and `beta < 1`, guaranteeing `N - beta T > 0` for `N >= 1`. The exclusion of unpublished next states correctly matches the validation domain. While changing C0 shifts the true Bellman target for neighboring cells (whose A1 values were fitted against the old population-0 values), the validation test evaluates all published cells' residuals using the new C0. Therefore, if the new C0 increases a neighbor's residual beyond tau, that neighbor will fail the empirical Bernstein test and be unpublished; no invalid certificate is issued.

## 3. Empirical Bernstein
**Verdict:** Certified.
**Reasoning:** Theorem 4 of Maurer and Pontil gives the bound for variables in [0, 1]. For variables scaled to width `w`, substituting the variance `V_X = V_Y / w^2`, multiplying by `w`, and using the two-sided failure rate `delta = alpha/M`, we exactly recover the formula in the design. Although the number of visiting trajectories `n` is a binomial random variable, the selected trajectories are exactly `n` independent and identically distributed draws from the conditional distribution of trajectories given that they visit the cell. Thus, conditional on any `n >= 2`, the Maurer and Pontil bound holds mathematically.

## 4. The a priori width `w_row`
**Verdict:** Certified.
**Reasoning:** The residual for any transition is `r = (1 - beta) f + beta V(next) - C(b)`. The run asserts that all flow values and published values fall within `[lower, upper]`. The next state's value `V(next)` is either a published value (bounded by `vmax`) or `lower` (if extinct). Thus the maximum possible value for `r + C(b)` is `(1 - beta) upper + beta vmax`, and the minimum is `(1 - beta) lower + beta lower = lower`. The difference is exactly `w_row`. Since every covered residual falls in this interval, their trajectory mean `m_i` does as well. The width is fixed before validation because it depends only on absolute limits and the fixed A1 table properties.

## 5. The estimand
**Verdict:** Certified with named changes.
**Reasoning:** The estimand `theta_b` is the unweighted mean over trajectories. The committed screen uses the visit-weighted mean. Averaging trajectory means un-weights trajectories that visit the cell multiple times. If trajectories that get stuck in a cell have systematically different errors, `theta_b` will suffer from aggregation bias across trajectories and fail to bound the true visit-weighted expected error. Since the sequential allocator encounters errors in proportion to state visitation frequencies, the visit-weighted mean is the more appropriate screen quantity. Certifying `theta_b` only guarantees a bounded trajectory-average error. The amendment must explicitly acknowledge this estimand gap and state that the certificate does not bound the visit-weighted Bellman error.

## 6. The global family
**Verdict:** Certified.
**Reasoning:** The union bound correctly allocates an error probability of `alpha / M` to each of the `M` cells. `M` is defined as the number of published plain cells after the population-0 merge from the A1 run, which is fixed before validation data is drawn. Any cell that is tested and passes is among these `M` cells. Cells with `n < 2` are unresolved and therefore unpublished, so they do not receive a certificate, preserving the global bound's integrity.

## 7. The FV asymptotic tier
**Verdict:** Certified with named changes.
**Reasoning:** The delta-method variance formula for a ratio estimator correctly matches the classical asymptotic variance. Using the Student t critical value accounts for variance estimation but assumes the group-level sums are normally distributed, which they are not. The label "asymptotic, not certified" is honest and prevents confusion with the rigorous Bernstein certificates. However, for a small sample of 32 groups where the variables are bounded and skewed, bootstrap percentile intervals for the ratio estimator would be a much better small-sample practice than delta-method and Student t, at essentially zero additional compute.

## 8. Seeds and data independence
**Verdict:** Certified.
**Reasoning:** Hashing distinct tags with the A1 job seed guarantees statistically independent random number generator streams for the refit, the validation replicates, and the census. This ensures the validation data is strictly independent from the data used to fit the A1 values and the new C0 value.

## 9. The availability floor
**Verdict:** Not certified.
**Reasoning:** Condition (b) requires checking that at most 5% of a row's low-population living endpoints fall outside the validated support. The design specifies using the committed census law `v3/unpublished_bins.endpoint_counts` for this. However, the committed `endpoint_counts` function in `unpublished_bins.py` only computes the overall fraction of excluded living endpoints (`fraction_among_living_endpoints`). It does not split endpoints by population category. It is therefore impossible to evaluate condition (b) using the unmodified committed function. The census function must be updated, or the validation script must compute the low-population exclusion fraction independently.

## 10. Anything else
**Verdict:** Certified.
**Reasoning:** The halt conditions and the interaction with the registered allocator are sound. If violating cells are unpublished, the availability floor naturally captures the loss in coverage. If the floor is passed but the registered allocator later hits an unpublished cell, it raises a KeyError and halts. This correctly enforces the "repair and reporting the limit" protocol.

## Required Changes (Ranked by Severity)

1. **Census logic update:** Update the validation script to compute the exclusion fraction for low-population living endpoints, because the unmodified `v3/unpublished_bins.endpoint_counts` function cannot evaluate condition (b).
2. **Estimand gap disclosure:** Explicitly document that certifying `theta_b` does not guarantee a bounded visit-weighted Bellman error, and that aggregation bias across trajectories is not covered by the certificate.
3. **FV small-sample practice:** Replace the delta-method and Student t interval for the FV tier with bootstrap percentile intervals to better handle small-sample skewness within the same compute budget.
