# A5 design, version 2: plain-law certification labels for FV-route tables

**Status:** revised after blind double certification, 2026-09-29, by the reviewer. Both certifiers (Gemini 3.1 Pro and a fresh Claude Code session) certified v1 with named changes; `certification_comparison_A5.md` gives each change and its disposition. Nothing here is adopted. It becomes an amendment only after the operator's approval.

**Evidence:** the planning evidence is non-registered: P4 (`planning_study/P4_findings.md`) and P1.

**Changes from v1:**
- the primary FV tables only, 252 rather than 264;
- M counted from the reruns' support;
- a mechanical violation rule;
- the full seed exclusion set;
- sharper framing and three disclosures.

## 1. Purpose

**The gap.** Amendment A4 validates Fleming-Viot (FV) route tables with an asymptotic test over 32 independent groups, labeled "asymptotic, not certified". Particles within an FV group depend on one another through resampling, so the groups are the only independent units.

**The fact A5 uses.** Given a source state, the residual's conditional law is the same on both routes.
- The flow and the cell's value are fixed by the state.
- The one-step advance kernel to the next state is the same map on both routes, because A4's FV trace records the pre-resampling transition.

What differs between the routes is only how often each state inside a cell is visited.

**The proposal.** A5 certifies published FV cells on independent **plain** trajectories:
- living sources only;
- the same certified empirical Bernstein test and table-conditional width as A4's plain tier.

The result is a per-cell statement under the plain visitation law.

**A5 is label-only.** It never changes a table's published support, values or row status. So the reruns behave identically whether A5 has run or not.

## 2. What is certified

**The tested set.** Every cell in the validated support of every primary FV row with status `estimated` in the sealed A4 publication. These are exactly the FV cells the reruns can look up. Sensitivity rows are not published to the reruns, so they are not tested.

**The quantity.** For each tested row-cell b:

`theta_b^plain = E[m_i | N_i >= 1]`

- `m_i` is the mean living-source residual of an independent plain trajectory in cell b, against the A4 published value. For FV rows these are the A1 values.
- **The law** is independent plain trajectories from the table's archived initial law, under its fixed rule and kernel.

This is not the FV conditioned law the table was fitted under. It is the law of the plain dynamics, which the reruns' allocations run under and which A4's census uses.

## 3. Data and seeds

**Tables:** the 252 primary FV-route A1 jobs of the A4 plan.

**Replicates:** 3 per table, each on the plain route with the job's own A1 settings and 32 groups. That is 32 × 64 = 2,048 independent trajectories per replicate, 6,144 per table, as in P4. The groups are only batching; on the plain route no resampling couples trajectories.

**Seeds:** SHA-256 of the tag `v3_R_fvplain`, the A1 job seed and the replicate index (1 to 3), truncated to 60 bits, by A4's `stream_seed`.

**The assertion is global.** Before any simulation, the runner builds the full set of forbidden seeds and halts on any collision:
- every A1 job seed;
- every seed in the A4 plan: fit, validate replicates, the FV validate replicate and census, for every job and both routes;
- the D26 probe seeds;
- the planning seeds P1, P1-census, P3 (replicates 0 to 3) and P4 (replicates 0 to 3), for every job.

It also asserts that A5's own 756 seeds are pairwise distinct. This extends A4's per-job `assert_seeds_distinct`, which does not forbid A4's own streams or P4.

## 4. Residual, test and family

**Residual:** as in A4.
- `(1 - beta) f + beta V(next) - C(b)`, with `beta = exp(-0.01)`.
- `V(next)` is the published value of the next cell, or `lower` if the next state is extinct.
- A transition is covered only when its source is alive, the source cell is in the tested set, and the next state is extinct or in a published cell of the same row.
- The cells are the FV row's own fine published cells. There is no population-0 merge, because the FV fit has no C0 cell.
- The living-source mask is required here, not inherited: a plain trace keeps recording after extinction.

**Width:** `w_row = (1 - beta) W + beta (vmax - lower)`, with vmax the row's largest published value.
- Every covered residual, and so every `m_i`, lies in `[lower - C(b), (1 - beta) upper + beta vmax - C(b)]`, an interval of length `w_row`.
- The run halts if any flow or published value lies outside `[lower, upper]`.

**Test:** Maurer and Pontil empirical Bernstein, two-sided, `delta = alpha / M` per row-cell, with `alpha = 0.05`, as in A4's `empirical_bernstein`.
- **Certified:** the interval lies within `[-tau, tau]`, and the visit-weighted point estimate `sum S / sum N` from the same data also lies within `[-tau, tau]` (A4's safeguard).
- **Violation:** the interval is disjoint from `[-tau, tau]`.
- **Unresolved:** anything else, or `n < 2`. Unresolved cells stay in M.

**Random n.** The number n of trajectories that visit a cell is random. The total trajectory count is fixed by the plan, trajectories are independent, and selection by `N_i >= 1` is a per-trajectory event. So conditional on n = k the selected `m_i` are i.i.d. from the law given `N_i >= 1`, and coverage holds after marginalizing over k.

**Family:**
- **M is fixed before any A5 data.** It is the number of tested row-cells, counted from the sealed A4 publication. A cell that recurs in several rows counts once per row.
- **It is a separate family from A4's plain tier.**
- **It is smaller than P4's.** P4 used M_FV = 797,225, every A1-published FV cell in primary and sensitivity rows, so P4's certification rate is conservative for A5.

**Statement:** with probability at least 0.95, every A5-certified FV cell has `|theta_b^plain| <= tau`, simultaneously.

## 5. Labels, violations and findings

**Labels.** A certified cell is labeled "certified under the plain law", always with that qualifier and never shortened to "certified". Every other tested cell keeps "asymptotic, not certified".

**The asymmetry with A4.** A4 drops a failing cell from the support. A5 does not: a violating cell stays in the support the reruns use, because A5 changes nothing they load. A violation is a real finding, not noise, since the false-violation rate is controlled within A5's family at 0.05. So the handling is fixed now, before any A5 data or rerun outcome, and is mechanical:

1. **The label record** lists each violation: the cell, the row, the interval and the exposure (the share of that row's living census endpoints, under A4's census law, that fall in the cell).
2. **Every result whose configuration looks up a row with a violation** carries a disclosure, wherever the result appears, naming the row, the number of violated cells and their total exposure.
3. **In the claims register,** every claim resting on such a result is recorded as conditional on the violation, never as proven.
4. **Removing a violated cell** would change the support and so the reruns. That needs its own pre-registered amendment with its own reruns. The operator decides whether to commission one. The record of that decision states whether any rerun outcomes were known when it was made.

Because the handling is fixed, the order of A5 and the reruns does not affect any decision.

**Per row, A5 also reports:**
- the share of plain-law visits in certified cells;
- the share of living census endpoints (under A4's census law) that fall in certified cells.

## 6. Planning basis (P4: 15 FV tables, 535 rows)

- **Cells certified:** 52% (34% to 71%), holding 98.5% to 99.97% of plain-law visits in every row. This was at P4's larger family, so it is conservative for A5.
- **Every plain-certified cell also passed A4's FV test.** A5 tests only A4-validated cells by construction, so this is reassuring but not load-bearing.
- **A certified-only support would pass A4's floor in every planning row,** with the worst at 1.44% against a cap of 2%. A5 does not use a certified-only support, so this margin does not bear on A5.
- **Caveats:** non-registered, 15 of 252 primary FV tables, plain law only.

## 7. What A5 does not establish

- **Certification under the FV conditioned law.** The two laws weight a cell's states differently. The cells the conditioned regime mainly reaches stay asymptotic.
- **The visit-weighted residual.** The 0.95 statement bounds the trajectory mean `theta_b^plain`. The visit-weighted safeguard is a point check, not a certificate, as in A4.
- **Aggregation bias within a cell,** or residuals on transitions into cells the row does not publish.
- **An exact match to the reruns' allocation law.** The rerun policies differ from the table's fixed rule; the census law is the committed proxy.
- **A joint 0.95 across the amendments.** A4's plain statement, A4's FV statement and A5's statement each hold at 0.95 on their own. They do not combine into one joint 0.95 statement.

## 8. Execution and cost

- **When:** after the A4 run and the A4 publication, pre-registered before any A5 data exist. It can run before or after the reruns (see section 5).
- **Compute:** 252 tables × 3 replicates × about 950 s ≈ 200 core-hours. That is about 12.5 hours on 16 workers, at about 1.9 GB per task. The model server is down, and the configuration test runs first.
- **Runner:** the production runner's A4 machinery (phases, memory caps, projection, resume, nondeterminism check) with a new stage kind. The ceiling is 24 hours.
- **Binding:** the label record is sealed and bound by hash to the A4 publication and its receipt. If A4 is ever republished to a new path, the binding must be re-pinned.
- **Output:**
  - the sealed label record;
  - a report of counts, visit shares, census coverage and every violation with its exposure.

  It contains no survival, extinction or fire rates.
