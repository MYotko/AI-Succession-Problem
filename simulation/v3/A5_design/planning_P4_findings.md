# Planning study P4: plain-trajectory certification of FV-route tables (reviewer, 2026-09-29)

**Status:** non-registered planning data (D28 item 2). Nothing here enters a registered result. It is blind: shares and fractions of living endpoints only.

## What ran

- **Tables:** the 15 FV-route A1 tables of P1, which have 535 rows.
- **Data:** each table got 3 replicates of 2,048 independent plain trajectories, on fresh `planning_P4` seeds.
- **Test:** residuals on living sources against the table's own values. It is certified by A4's plain-tier test: trajectory-level empirical Bernstein with the table-conditional width, the global family at M_FV = 797,225, and the visit-weighted safeguard.
- **Comparison:** A4's asymptotic FV test (delta method plus Fieller, Student t, at least 16 groups) on the P1 group data, and the census under the P1 law.
- **Where and how long:** about 1 hour at low priority on the X2's spare threads, beside the registered A4 run. The guard never fired.

## Results

The ranges below run from the lowest row to the highest.

| Support | Cells, mean (range) | Plain-law visits | Living endpoints excluded, median (worst row) | Low-population, worst row | Rows passing the 2% / 5% floor |
|---|---|---|---|---|---|
| Plain-certified only | 52% (34% to 71%) | 99.8% (98.5% to 99.97%) | 0.08% (1.44%) | 1.32% | 535 of 535 |
| FV asymptotic (A4) | 85% (76% to 90%) | not applicable | 0.00% (0.07%) | 0.01% | 535 of 535 |
| Union | 85% | not applicable | 0.00% (0.07%) | 0.01% | 535 of 535 |

**The union equals the FV set exactly.** Every cell certified under the plain law also passes A4's asymptotic FV test. No row lacked plain-trajectory visits.

## Reading

1. **FV-route tables can largely be certified.** Under the plain occupancy law, the certified cells hold over 98.5% of visits in every row. This is the law the reruns' allocations and A4's census use.
2. **A certified-only support would pass the floor in every planning row,** but with less margin: the worst row is at 1.44% against the 2% cap. The planning sample is 15 of 264 FV tables, so some registered rows could exceed the cap.
3. **Because the plain-certified set lies inside A4's FV set, a label-only amendment is possible.**
   - For every published FV cell, a fresh plain-trajectory validation would record whether it is also certified under the plain law.
   - The published support, and so the reruns' behavior, does not change.
   - A plain-law violation in a published cell would be reported as a finding.
4. **What is certified is the plain-law residual,** not the FV-conditioned one. The FV cells that pass only asymptotically are the ones the conditioned regime mainly reaches.

## Cost of a registered version (by arithmetic from P4 timings)

- **Timing basis:** plain tasks for FV kernels took about 830 to 1,090 seconds each.
- **Total:** 264 tables × 3 replicates × about 950 s ≈ 209 core-hours, about 13 hours at 16 workers.
- **Memory:** about 1.9 GB per task.
