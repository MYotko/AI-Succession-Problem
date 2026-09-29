# Continuation validation design: draft for blind certification

**Status:** draft, 2026-09-29, by the reviewer. It implements D28 and D29. Nothing here is adopted. It becomes an amendment only after blind double certification (D28 item 3) and the operator's approval. Planning evidence comes from the non-registered planning studies P1 and P3. No registered number will come from them (D28 item 2).

## 1. What is validated, and why only at living states

**Tables.** The A1 table family has 343 tables: 79 on the plain route (3,165 rows) and 264 on the Fleming-Viot (FV) route (12,055 rows). Each row is a continuation table C over cells, for one (rule, kernel, scoring) context.

**Use.** The registered engine looks C up only at living states. In `v3/production_tables.py`, `lookup` never uses C at an extinct endpoint. An unpublished cell at a living endpoint makes the score unavailable, with no neighbor substitution.

**Residual.** For a transition from a living source state x in cell b to a next state x':

`r = (1 - beta) f + beta V(x') - C(b)`

- `beta = exp(-0.01)`, and f is the row's scored flow.
- `V(x')` is C of the cell of x' when that cell is published, and the lower bound `lower` (the extinction flow) when x' is extinct.
- Any other transition is not covered.

This matches `v3/continuation.py` (`fit_transitions`), apart from the living-source restriction in section 2.

**Tolerance.** `tau = 0.05 W`, with `W = upper - lower` (the row's `flow_range`), as committed.

## 2. Changes from the committed screen

1. **Living sources only (new).**
   - **The defect:** the plain trace keeps recording a path after extinction. The committed fit and screen then count those extinct states as sources in population-category-0 bins, where the table is never used.
   - **The evidence (P3):** on living sources, the A1 fitted values of population-0 fine bins show mean residuals up to 6.7 tau. A living-source refit of the population-0 cell brings the largest to 0.033 tau.
   - **FV route:** its sources are resampled living particles, so the restriction changes nothing there. It is applied anyway, for uniformity.
2. **Screen quantity (D29 item 1).**
   - **Plain:** `theta_b = E[m_i | N_i >= 1]`, where `m_i` is trajectory i's mean covered residual in cell b and `N_i` its number of covered visits there.
   - **FV:** the committed visit-weighted mean residual, with groups as units.
3. **Plain route, population category 0 (D29 item 3):** one cell per row, with its value refit (section 4). Every other plain cell keeps its A1 value.
4. **Fresh validation data,** never used for fitting. Certified or asymptotic intervals replace the committed point-estimate maximum over bins.
5. **Validated support.** A cell is published for registered use only if it passes its tier's test. Every other cell is unpublished, so its scores are unavailable under the committed rules.

## 3. Data and seeds

**Seed streams.** Each stream is the SHA-256 of a tag, the A1 job seed and the replicate index, truncated to 60 bits:
- `v3_R_fit`: plain refit, 1 replicate;
- `v3_R_validate`: plain, replicates 1 to 3; FV, 1 replicate;
- `v3_R_census`: the census.

The run asserts that these seeds are pairwise distinct and distinct from the A1, probe, P1 and P3 seeds. A collision halts it.

**Replicate sizes.**
- **Plain:** a replicate is 32 groups of 64 runs, which is 2,048 independent trajectories. Otherwise the A1 settings apply: burn 1,024, measure 2,048.
- **FV:** a replicate is 32 groups of 256 particles. Otherwise the A1 settings apply.

## 4. Plain tier: certified

**Population-0 cell value.** The Bellman fixed point on the fitting replicate's covered living-source transitions:

`C0 = sum[(1 - beta) f + beta V(next)] / N`

- **V(next):** C0 when the next state is in the cell, the A1 value when it is in a published cell, and `lower` when it is extinct.
- **Excluded:** transitions into unpublished cells.
- **Closed form:** `C0 = a / (N - beta T)`, where T counts transitions that stay in the cell. `N - beta T > 0`, because `beta < 1` and `T <= N`.
- **Publication:** C0 is published only with at least 4 fitting visits, the committed `min_visits`.

**Unit.** A validation trajectory i with at least one covered living-source visit to cell b. The trajectories are independent runs from the same initial law, so conditional on selection they are i.i.d.

**A priori width, fixed before any validation data exist.**

`w_row = (1 - beta) W + beta (vmax - lower)`

`vmax` is the row's largest published value, including C0. Every `m_i` in cell b lies in `[lower - C(b), (1 - beta) upper + beta vmax - C(b)]`, an interval of length `w_row`.

This needs every f and every published value to lie in `[lower, upper]`. The run checks this at every transition and value, and halts if it fails. In P3 the median `w_row` was 0.246 of 2W.

**Test.** Maurer and Pontil empirical Bernstein, two-sided, with `delta = alpha / M` per cell:

`rho = sqrt(2 V_n ln(4M/alpha) / n) + 7 w_row ln(4M/alpha) / (3 (n - 1))`

- `V_n` is the unbiased sample variance of the `m_i`, and n is the number of units.
- **Certified:** `[mbar - rho, mbar + rho]` lies inside `[-tau, tau]`.
- **Violation:** the interval is disjoint from `[-tau, tau]`.
- **Unresolved:** anything else, or `n < 2`.

**Family.** Global, with `alpha = 0.05`. M is the number of published plain cells across all plain rows of the registered set, after the population-0 merge, counted before any validation data exist.

**Statement.** With probability at least 0.95, every certified plain cell has `|theta_b| <= tau`, simultaneously for all cells (union bound).

**Violations.** A violating cell is unpublished and reported as a finding. It does not halt the run.

## 5. FV tier: asymptotic, not certified

**Unit.** A group: 32 independent groups. Particles within a group depend on one another through resampling.

**Estimate.** Over the groups with `N_g >= 1`, `mu_b = sum S_g / sum N_g`.

**Variance (delta method).** `(sum S_g^2 - 2 mu sum S_g N_g + mu^2 sum N_g^2) / (n (n - 1) Nbar^2)`, with `Nbar = sum N_g / n`.

**Interval.** `mu_b +/- t_{n-1, 1 - alpha/(2 M_FV)} * sd`:
- `M_FV` is the number of published FV cells, about 797,225.
- Student t replaces the normal quantile, to temper the small-n tail: `t_31 = 7.06`, against `z = 5.41`.
- Cells with fewer than 16 contributing groups are unresolved.
- **P1 cost:** 92% of FV cells pass under this rule, against 98.7% under z. The passing cells hold 100% of visits either way.

**Label.** "Asymptotic, not certified" everywhere: the amendment, the claims register and every result that uses FV rows (D29 item 2, D28 option D).

## 6. Availability floor (D28 item 4)

**Census.** For each table, the committed census law (`v3/unpublished_bins.endpoint_counts`): held-out plain paths from the archived initial law, and 20-step endpoints over 500 start steps, with the `v3_R_census` seed. It is measured among living endpoints only.

**A row passes if both hold:**
- (a) at most 2% of its living endpoints fall outside its validated support;
- (b) at most 5% of its low-population living endpoints do, when it has at least 50 of them. Otherwise (b) is reported, not assessed.

**Planning basis:**
- P3 (9 plain tables, 280 rows, this configuration): the worst row was 0.8% on (a) and 0% on (b).
- P1 (15 FV tables, 535 rows, the ratio check): the worst row was 0.02% on (a).

The floors leave room for the 70 plain and 249 FV tables outside the planning sample, and they still bound the rate of unavailable scores the reruns will meet.

**Failure.** A row that fails the floor is `not_estimable` for registered use. Registered execution already rejects `not_estimable` rows, so the reruns halt, and the operator decides between repair and reporting the limit.

## 7. What the result does and does not cover

**Covers:** the mean Bellman residual of each validated cell, over the validation law. That law is living sources, from the archived initial law, under the table's fixed rule and kernel.

**Does not cover:**
- aggregation bias within a cell (the committed flag `aggregation_bias_covered` stays false);
- the shift between the validation law and the states the reruns' allocations actually visit (the census law is the committed proxy);
- a certificate for the FV tier.

## 8. Halt conditions

- a flow or published value outside `[lower, upper]`;
- a seed collision;
- an A1 source-hash mismatch;
- nondeterminism: one sampled task, rerun, must reproduce bit-identically.

## 9. Compute

- **Plain:** 79 tables × 4 replicates × about 900 s ≈ 79 core-hours, about 5 h on 16 workers.
- **FV:** 264 tables × about 3,500 s ≈ 257 core-hours. About 9.5 GB per task limits the X2 to about 10 workers, so about 26 h.
- **Census:** minutes.
- **Operations:** the model server is down throughout, and a pre-launch configuration test runs first.

## 10. Planning evidence (non-registered)

The files are in `v3_instrument_inputs\planning_study\`:
- **`P1_findings.md`:** 24 jobs with 32 fresh groups each. It covers methods, families, the estimand gap and the range correction.
- **`analysis_P3.md`:** 9 plain jobs, 1 fitting replicate plus 3 validation replicates. It covers partitions, range modes, families and trajectory counts.
- **The chosen configuration, P3 at 6,144 trajectories:** "pop0_one/refit, global, table".
  - Cells certified: 65%. Visits in certified cells: 100%, and 99.8% in the worst row.
  - Low-population visits in certified cells: 100% in every row.
  - Living endpoints excluded: median 0%, worst row 0.8%. Low-population living endpoints excluded: 0% in every row.
- **Rejected alternatives:**
  - The 2W width needs about 1.5 times the trajectories under the global family.
  - Splitting population 0 by welfare left refit cells with residuals up to 1.63 tau.
  - The per-row family is weaker, because its 0.05 applies to each of about 3,000 rows separately.
