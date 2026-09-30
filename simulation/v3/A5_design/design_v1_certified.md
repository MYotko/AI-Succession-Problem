# A5 design, version 1: plain-law certification labels for FV-route tables

**Status:** draft for blind certification, 2026-09-29, by the reviewer. The operator chose to pursue it after planning study P4. Nothing here is adopted. It becomes an amendment only after blind double certification and the operator's approval.

**Evidence:** the planning evidence is non-registered: P4 (`planning_study/P4_findings.md`) and P1.

## 1. Purpose

**The gap.** Amendment A4 validates Fleming-Viot (FV) route tables with an asymptotic test over 32 independent groups, labeled "asymptotic, not certified". Particles within an FV group depend on one another through resampling, so the groups are the only independent units.

**The fact A5 uses.** By the Markov property, the Bellman residual at a living state does not depend on how that state was reached.

**The proposal.** A5 certifies published FV cells on independent **plain** trajectories:
- living sources only;
- the same certified empirical Bernstein test and table-conditional width as A4's plain tier.

**A5 is label-only.** It never changes a table's published support, values or row status. So the reruns behave identically whether A5 has run or not.

## 2. What is certified

For each published FV cell b of the A4 family, the plain-law screen quantity is:

`theta_b^plain = E[m_i | N_i >= 1]`

- `m_i` is the mean living-source residual of an independent plain trajectory in cell b, against the A4 published values.
- **The law** is independent plain trajectories from the table's archived initial law, under its fixed rule and kernel.

This law is not the FV conditioned law the table was fitted under. It is the law of the plain dynamics, which the reruns' allocations run under and which A4's census uses.

## 3. Data and seeds

**Replicates:** 3 per FV-route table, each with 32 groups and the job's own A1 settings otherwise. That is `runs_per_group` trajectories per group, and sensitivity jobs keep their doubled population or length. The simulation runs the **plain** route.

**Seeds:** SHA-256 of the tag `v3_R_fvplain`, the A1 job seed and the replicate index, truncated to 60 bits. They are asserted distinct from:
- every A1, A4, probe and planning seed, including `planning_P4`;
- each other.

## 4. Residual, test and family

**Residual:** as in A4.
- `(1 - beta) f + beta V(next) - C(b)`, with `beta = exp(-0.01)`.
- `V(next)` is the published value of the next cell, or `lower` if the next state is extinct.
- A transition is covered only when its source is alive, the source cell is published, and the next state is extinct or in a published cell.
- The cells are the FV table's own fine published cells. There is no population-0 merge, because FV fits have living sources by construction.

**Width:** `w_row = (1 - beta) W + beta (vmax - lower)`, with vmax the row's largest published value.
- The run halts if any flow or published value lies outside `[lower, upper]`.

**Test:** Maurer and Pontil empirical Bernstein, two-sided, `delta = alpha / M` per cell, with `alpha = 0.05`.
- **Certified:** the interval lies within `[-tau, tau]`, and the visit-weighted point estimate `sum S / sum N` from the same data also lies within `[-tau, tau]` (A4's safeguard).
- **Violation:** the interval is disjoint from `[-tau, tau]`.
- **Unresolved:** anything else, or `n < 2`.

**Family:** M is the number of published FV cells in the published A4 family, counted from that publication before any A5 data exist. It is a separate family from A4's plain tier.

**Statement:** with probability at least 0.95, every A5-certified FV cell has `|theta_b^plain| <= tau`, simultaneously.

## 5. Labels and findings

- A certified cell is labeled "certified under the plain law". Every other published FV cell keeps "asymptotic, not certified".
- **A violation is reported as a finding.** It names the cell, the row and the interval, and is disclosed wherever results use that row.
  - The support does not change, because A5 is label-only.
  - A violation means the published value is wrong under the plain law at the stated confidence, so the operator decides whether any claim resting on that row stands.
- **Per row, A5 also reports:**
  - the share of plain-law visits in certified cells;
  - the share of living census endpoints (under A4's census law) that fall in certified cells.

## 6. Planning basis (P4: 15 FV tables, 535 rows)

- **Cells certified:** 52% (34% to 71%), holding 98.5% to 99.97% of plain-law visits in every row.
- **Every plain-certified cell also passes A4's FV test,** so the certified cells lie inside A4's support.
- **A certified-only support would pass A4's floor in every planning row,** with the worst at 1.44% against a cap of 2%. A5 does not use a certified-only support; it only labels cells.

## 7. What A5 does not establish

- **Certification under the FV conditioned law.** The cells the conditioned regime mainly reaches stay asymptotic.
- **Aggregation bias within a cell.**
- **An exact match to the reruns' allocation law.** The rerun policies differ from the table's fixed rule; the census law is the committed proxy.

## 8. Execution and cost

- **When:** after the A4 run and the A4 publication, and pre-registered before any A5 data exist. It can run before or after the reruns, since it changes nothing they use.
- **Compute:** 264 FV tables × 3 replicates × about 950 s ≈ 209 core-hours, about 13 hours on 16 workers, at about 1.9 GB per task. The model server is down, and the configuration test runs first.
- **Runner:** the production runner's A4 machinery (phases, memory caps, projection, resume, nondeterminism check) with a new stage kind. The ceiling is 24 hours.
- **Output:** a sealed label record bound by hash to the A4 publication, and a report giving counts, visit shares, census coverage and every violation. It contains no survival, extinction or fire rates.
