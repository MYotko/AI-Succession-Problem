# Planning study P1: findings (reviewer, 2026-09-28)

Non-registered planning data. Nothing here enters any registered result (D28 item 2). The blind holds: no survival, extinction or fire rates, and no rule identities or rankings. Endpoint figures are fractions of living endpoints only.

## Data

- **Jobs:** 24 A1 table jobs (15 Fleming-Viot, 9 plain), each with 32 fresh validation groups and fresh seeds, on the X2 in about 5 hours.
- **Analysis:** `analysis_summary.md` (methods i to iv, G = 8, 16, 32, row and subset scope) and `supplementary_P1.json` (per-row census, estimand gap).
- **Reviewer fixes before the analysis:** workstation paths replaced by `SIM_DIR` and `A1_TABLES_PATH`. M now counts published bins in scope, per the directive, instead of the full 6,144-bin grid.

## Findings

1. **The A1 fitted values look sound.** No bin shows a violation under any method: no interval lies wholly outside [-tau, tau].
   - **Point estimates at 32 groups:** no plain bin exceeds tau. On the FV route, 33 of 35,320 bins do, one bin in each of 33 rows, holding a negligible share of visits.
   - **Reading:** the A1 screen failures look like thin held-out evidence, not wrong tables. This supports D28 item 5, reusing the A1 fitted values.
2. **Only the plain route has a certified method.** The plain route has 79 of the 343 tables and 3,165 of the 15,220 rows.
   - **Method:** trajectory-level empirical Bernstein (iii).
   - **Correction (reviewer, same day):** the Bellman residual `(1-beta) f + beta C(next) - C(bin)` lies in [-W, W], so its range is 2W, not W. The directive, and the first version of this note, used W, which halved the certified bounds' range term. The figures below use 2W (`supplementary_P1b.json`). Methods (i) and (ii) pass nothing or almost nothing either way. Method (iv) has no range term and is unaffected.
   - **Two error-control families,** each at alpha = 0.05, all 280 plain rows, 32 groups:

     | Family | M | Bins certified | Visits in certified bins, mean (worst row) | Living endpoints excluded, median (worst row) |
     |---|---|---|---|---|
     | Per row | the row's published bins | 32% | 97.4% (93.0%) | 1.0% (3.1%) |
     | Global, every published plain bin | 164,090 | 18% | 94.9% (82.0%) | 2.6% (11.6%) |

   - **The global family is range-limited at 2,048 trajectories.** Its range term, `7 (2W) log(4M/alpha) / (3(n-1))`, is 3.66 against tau = 4.91 at n = 2,048. More trajectories reduce it in proportion.
   - **Group-level Hoeffding (i):** passes nothing at any G, as predicted.
   - **Uncorrected figures, superseded:** 45% of bins, 97.7% of visits, worst row 0.8% excluded (row family).
3. **The certified plain support misses the low-population region.**
   - **Scale:** in 150 of 280 plain rows, every low-population living endpoint lands in an uncertified bin. In the other 130 rows, none does.
   - **Cost to close it:** certifying the failing low-population bins by brute force needs a median of 4.3 times the current trajectories, a 90th percentile of 67 times, and far more at the tail. These multipliers were computed with range W, so under 2W they are larger. The pattern is unchanged under 2W.
   - **Remedy:** this is D28's option C (coarser states near extinction).
4. **The FV route has no certified method at a feasible size.** It has 264 tables and 12,055 rows, 79% of all rows.
   - **Why:** its independent units are groups. Group-level empirical Bernstein would need roughly 410 groups per job, against 32 here: weeks of X2 time for all FV tables.
   - **Ratio method (iv):** passes 99% of FV bins at 32 groups. With at most 32 units per bin, that is an asymptotic check, not a certificate.
5. **Estimand gap.** The certified trajectory methods bound the mean of per-trajectory means. The committed screen uses the visit-weighted mean.
   - **Size of the gap:** over 11,475 plain bins with at least 30 trajectories, it is a median of 1.2% of tau and a 90th percentile of 5.3%. The point estimates classify 14 bins differently.
   - **Consequence:** certifying on the trajectory mean requires an amendment defining the screen quantity that way.

## Registered validation compute (by arithmetic from the P1 timings)

- **Plain:** 79 tables × about 900 s at 32 groups ≈ 20 core-hours, about 1.3 h on 16 workers.
- **FV:** 264 tables × about 3,500 s at 32 groups ≈ 257 core-hours. At about 9.5 GB per FV job, memory limits the X2 to about 10 workers, so about 26 h.
