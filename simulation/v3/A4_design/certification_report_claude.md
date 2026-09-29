# Blind certification: continuation validation design

Certifier: independent (Claude). I did not write this design. For each item I derived the
mathematics before comparing. Verdicts are certified, certified with named changes, or
not certified.

## Item 1: Living-source restriction. Certified.

The residual is `r = (1 - beta) f + beta V(x') - C(b)`. C is a table value for cell b.

Where is C used? `production_tables.lookup` returns a score per state, but the registered
allocation calls it only where the trajectory is live. Extinct/absorbing states skip
allocation entirely (`integration.py` builds the absorbing record with
`allocation_evaluated: False`), and for an extinct next state the value used is the
extinction flow `lower`, not C. So C never enters at an extinct source or an extinct
endpoint. The committed fit (`continuation.fit_transitions`), by contrast, keeps every
training-bin source regardless of aliveness (`keep = train & (current >= 0)`), so extinct
states enter as population-category-0 sources. Only population-category-0 cells can contain
extinct states: any bin with population category above 0 requires n/K > 0.05, hence live.
So the contamination is confined to the population-0 cell, which is exactly the cell the
design refits.

Restricting to living sources removes a bias rather than adding one: it conditions the fit
and the screen on the same event under which C is consulted. It cannot bias the living-state
value, because living states are the estimand. The FV route resamples living particles, so
the restriction is a no-op there and is applied only for uniformity. Correct.

## Item 2: Plain population-0 refit. Certified.

Fixed point. `C0 = a / (N - beta T)`, T = in-cell transitions, a = the non-in-cell
contributions. Existence and uniqueness: for the chosen one-cell partition this is a scalar
equation with denominator `N - beta T >= N(1 - beta) > 0`, so unique. The committed `refit`
in `run_p3.py` solves the general coarse case with `np.linalg.solve(diag(counts) - beta T, a)`;
each row of that matrix has `counts[i] - beta sum_j t[i,j] >= counts[i](1 - beta) > 0`, so it
is strictly diagonally dominant and invertible. Extinct and unpublished next states are handled
correctly: extinct takes priority over the population-0 self-loop (`internal = ~dead & nc>=0`,
boundary `lower` for dead), and transitions into unpublished cells are excluded from both fit
and validation. C0 stays in range: with every f and every external value in `[lower, upper]`,
the numerator is bounded so that `lower <= C0 <= upper`. I verified both endpoints
algebraically.

Neighbor effect. Non-population-0 cells keep A1 values that were fitted against the old,
contaminated population-0 values. After the refit, a neighbor that flows into the population-0
cell is validated with C0, not the old value, so its residual can shift. This is sound: the
certificate is empirical, so a neighbor whose residual worsens simply fails its test and is
unpublished. It cannot produce a false certificate. P3 shows coverage holds (pop0_one/refit,
global, table, 6,144 traj: 65% of cells, 100% of visits certified).

Named change (minor): state explicitly in the design that neighbor cells are re-validated
against C0 and that soundness rests on that re-test, not on the neighbors being unaffected.

## Item 3: Empirical Bernstein. Certified.

Maurer and Pontil (2009), Theorem 4, for i.i.d. `X_i in [0,1]`: with probability at least
`1 - delta`, `E[X] <= Xbar + sqrt(2 V_n ln(2/delta)/n) + 7 ln(2/delta)/(3(n-1))`, `V_n` the
unbiased sample variance. This is one-sided. A two-sided bound applies it twice at `delta/2`,
giving `ln(2/(delta/2)) = ln(4/delta)`. With per-cell `delta = alpha/M`, `ln(4/delta) =
ln(4M/alpha)`. Rescaling to a variable in an interval of width w (set `Y = (X - min)/w`):
`V_n(X) = w^2 V_n(Y)`, so the variance term becomes `sqrt(2 V_n(X) ln(4/delta)/n)` and the
range term becomes `7 w ln(4/delta)/(3(n-1))`. This is exactly the design's `rho`, and matches
`eb_certified` in `analyze_p3.py`. The 7/3 constant is correct.

Random n. Units are trajectories with at least one covered visit. Selection is a
per-trajectory event; the trajectories are i.i.d. draws from the initial law, so conditional
on the count n the selected `m_i` are i.i.d. from the law of `m | N>=1`. The bound holds for
each fixed n, hence unconditionally; `n < 2` is declared unresolved. Valid.

## Item 4: A priori width w_row. Certified.

`w_row = (1 - beta) W + beta (vmax - lower)`, `vmax` the row's largest published value
including C0. Because C(b) is a fixed constant it shifts the interval for `m_i` but does not
widen it, so the range of `m_i` is `(1 - beta)(range of f) + beta (range of V) <=
(1 - beta) W + beta (vmax - lower) = w_row`. Every `m_i` therefore lies in an interval of
length `w_row`. This needs every f in `[lower, upper]` and every published value in
`[lower, vmax]`; the run checks flows and values against `[lower, upper]` and halts otherwise.

No gaps. Extinct endpoints take `V = lower` (inside the interval). Values of never-visited
cells are still bounded by `vmax`, which is the max over all published values, not just
visited ones. C0 cannot fall outside: `vmax` is defined to include it, and I showed
`C0 in [lower, upper]`. w_row is tighter than the 2W range flagged in P1, and correctly so,
because 2W treats C(b) as varying; here it is fixed.

Clarification (minor): w_row depends on the fit replicate through C0 and vmax, so it is fixed
before the validation (test) replicates, not before all data. That is what the certificate
requires (fit is independent of the test data). The wording "before any validation data
exist" should be read that way.

## Item 5: The estimand. Certified with named changes.

`theta_b = E[m_i | N_i >= 1]` is the mean of per-trajectory means. It is the right unit for
empirical Bernstein, because visits within a trajectory are serially dependent and only whole
trajectories are i.i.d. But C enters the allocation once per visit, so the operationally exact
quantity is the visit-weighted mean the committed screen uses. These differ. P1 reports the
gap at a median 1.2% of tau, 90th percentile 5.3%, with 14 bins classified differently.

Certifying `theta_b` guarantees the trajectory-averaged mean residual is within tau; it does
not by itself guarantee the visit-weighted mean is within tau, nor per-visit or aggregation
bounds. The gap is small and, importantly, measurable: `run_p3` records both `sum_m` (the
trajectory mean) and `sum_S`, `sum_N` (the visit-weighted mean) per cell.

Named changes: (1) for each certified cell, compute the visit-weighted mean from the recorded
sums and confirm it also lies within tau, reporting any cell where it does not; (2) add the
trajectory-versus-visit gap to the section 7 "does not cover" list, which currently omits it.

## Item 6: The global family. Certified.

Union bound. A cell is certified when its two-sided `(1 - delta)` interval lies inside
`[-tau, tau]`, `delta = alpha/M`. If a certified cell truly had `|theta_b| > tau`, its
interval failed to cover, probability at most `delta`. Over M cells, `M * (alpha/M) = alpha =
0.05`. So with probability at least 0.95 every certified plain cell satisfies `|theta_b| <=
tau` simultaneously. Correct.

M is a function of the A1 tables and the fixed merge rule, both set before validation; the fit
replicate's role in C0 publication is independent of the test data, so M is fixed with respect
to the tested sample, and over-counting (P3 used 164,090 fine bins for coarser partitions) is
conservative. Nothing is tested but not counted: refit and neighbor cells are ordinary
published plain cells inside M.

Named notes (minor): M must be recomputed as the registered 79-table post-merge count, not the
P3 planning value 164,090. Plain and FV are separate families; the 0.95 statement is
plain-only, which is acceptable because FV is labeled not certified, but the design should say
so explicitly.

## Item 7: FV asymptotic tier. Certified with named changes.

Ratio estimator `mu = sum S_g / sum N_g`. Delta-method variance of a ratio is
`[sum(S_g - mu N_g)^2] / (n(n-1) Nbar^2)`, and expanding the square gives exactly the design's
`(sum S^2 - 2 mu sum SN + mu^2 sum N^2) / (n(n-1) Nbar^2)`. Correct. The two-sided Bonferroni
critical value `t_{n-1, 1 - alpha/(2 M_FV)}` is right; I confirmed the normal quantile
`z = 5.41` at `alpha/(2 M_FV)`, `M_FV = 797,225`, and `t_31 = 7.06` is the expected heavier-tail
value. The `n >= 16` rule is a reasonable asymptotic guard. The label "asymptotic, not
certified," applied to the amendment, the register, and every FV-derived result, is honest and
sufficient.

Minor point: the variance uses `n` = contributing groups and `Nbar = sum N/n`, rather than all
32 groups. This is slightly conservative (ratio of variances `(m-1)n / (m(n-1)) >= 1` for
`n <= m`), so acceptable.

Better small-sample practice within the same compute: use a Fieller interval for the ratio
instead of delta-method-plus-t. Fieller handles the ratio's skew and a near-zero denominator
correctly and needs no extra simulation. A BCa bootstrap over the 32 groups is a second option.
Either could be reported alongside the current interval as a sanity floor.

## Item 8: Seeds and data independence. Certified.

Streams are SHA-256 of (tag, A1 seed, replicate index), truncated to 60 bits, with distinct
tags `v3_R_fit`, `v3_R_validate`, `v3_R_census`. The run asserts pairwise distinctness and
distinctness from the A1, probe, P1 and P3 seeds, and halts on collision. Distinct tags give
independent streams; 60 bits over a handful of seeds makes accidental collision negligible and
it is checked anyway. The chain of independence holds: C0 is fit on `v3_R_fit`, tested on
`v3_R_validate`, and both are independent of the A1 values used as fixed neighbors and of vmax.
The census stream is separate. So the certificate is computed on data independent of the tables
being tested.

## Item 9: Availability floor. Certified.

The census law matches the committed `unpublished_bins.endpoint_counts`: held-out plain paths,
20-step endpoints over 500 starts, `v3_R_census` seed, measured among living endpoints. Test
(a) `misses / living_endpoints <= 2%`; test (b) `<= 5%` among low-population living endpoints
when there are at least 50, else reported. The floors leave room over the planning worst cases
(P3: 0.8% on (a), 0% on (b); P1: 0.02% on (a)). The 50-endpoint minimum avoids noise on tiny
samples. A failing row is `not_estimable`; `production_tables.require_production` rejects any
not_estimable row, so registered execution cannot load the family and halts, and the operator
decides. Consistent with the committed engine.

Disclosed caveat (already in section 7): the census is a plain-path proxy, not the adaptive
all-rule allocation law, and for FV rows it is a plain-path proxy as well. This is a limit on
what the floor demonstrates, not an error.

## Item 10: Other interactions.

- Unavailable scores do not halt a rerun. `integration.py` uses `lookup_available` and, when a
  state's cell is unpublished, takes a documented balanced or survival-first fallback. So the
  availability floor bounds fallback frequency, not a crash. Good, and worth stating in the
  design.
- One row failing the floor makes the entire registered family unloadable (require_production
  raises on any not_estimable row), so a single floor failure halts all reruns. The design's
  "reruns halt, operator decides" is consistent, but the all-or-nothing coupling should be
  stated.
- The committed tables are frozen (`write_tables` refuses to overwrite). Publishing the
  validated support is an amendment producing a new manifest; the executor must not attempt to
  rewrite the frozen file.

## Required changes, ranked

1. Item 5: report the visit-weighted mean per certified cell and confirm it lies within tau,
   and list the trajectory-versus-visit gap in section 7. This is the one place the certified
   quantity differs from the operational one.
2. Item 6: recompute M as the registered 79-table post-merge published-cell count before
   validation, and state that the 0.95 guarantee is plain-only.
3. Item 7: add a Fieller (or BCa bootstrap) interval for the FV ratio alongside the delta-method
   interval; keep the "not certified" label.
4. Items 2, 4, 10 (documentation): state that neighbors are re-validated against C0; clarify
   that w_row is fixed before the test replicates; note the fallback behavior, the all-or-nothing
   floor coupling, and the frozen-table amendment path.

Overall the design is mathematically sound. Every formula I re-derived matches, and no item
fails certification.
