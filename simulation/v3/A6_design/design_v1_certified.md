# A6 design, version 1: the W11 sensitivity and convergence runs, completed

**Status:** draft for blind certification, 2026-09-29, by the reviewer. The operator chose option O2 and its defaults (D32) after the readiness note (`SENSITIVITY_READINESS_2026-09-29.md`). Nothing here is adopted. It becomes amendment A6 only after blind double certification and the operator's approval. It must be committed before any R1 or R2 output is read.

## 1. Purpose

Section 6 of the design note registers five sensitivity and convergence arms. Three gaps stop them from running as written:
1. **No job builder.** Nothing builds their jobs.
2. **Missing tables.** The crowding and σ0² arms need table families of their own. The tables' kernel identity includes the crowding variant and the novelty protocol, which holds σ0². No such families are registered or budgeted.
3. **No reading rule.** Section 8 lists no sensitivity quantity, so under its last line every sensitivity result would be exploratory. W11 requires a pre-registered reading.

A6 closes these gaps. Every other element of section 6 is unchanged: the arms, grids, weights, horizon and seed counts.

## 2. The arms

| Arm | Grid | Seeds per cell | Tables | Runs |
|---|---|---|---|---|
| Weight corners: κ ∈ {0.75, 8} × θ ∈ {0.25, 0.75} | R1's 9 rr at alpha 1.0, capability 1.5; R2's 5 alpha × 7 capabilities at rr 0.064 | 100 | nominal A4 family (it already scores κ = 0.75 on exactly these contexts) | 4 × 44 × 100 = 17,600 |
| Horizon | R1's 9 rr at alpha 1.0, 1,000 steps | 200 | nominal | 1,800 (3,600 run-equivalents) |
| Crowding, reproductive-age variant | the weight-corner grid, 44 cells | 100 | **crowding family** (below) | 4,400 |
| σ0² ×10 and σ0² ×0.1 | R1's five rr nearest v2.0's inflection, 0.063 (section 9): 0.059, 0.060, 0.062, 0.064, 0.066; alpha 1.0 | 100 | **two σ0² families** (below) | 1,000 |
| Seed convergence | R1 and R2 estimates at half and full seed counts | none | none | 0 |

**Two readings made explicit:**
- **Crowding seeds.** D18's "a quarter of the seeds" is read as a quarter of R1's 400 per cell, which gives 100, the count every other arm uses.
- **The σ0² narrowing.** It is fixed by distance from the registered v2.0 inflection, chosen before any v3 rerun output exists. The one tie at distance 0.003 (0.060 and 0.066) includes both.

**All other weights are at the center** (κ = 8, θ = 0.5), with successor capability 1.5 on R1's grid and the nominal kernel and calibration, except where an arm varies them.

## 3. The variant table families

**Composition.** Each family is built by the committed table-job logic (`study.table_jobs` and `scoring_for_rr`) restricted to its arm's contexts:
- **Crowding family:** R1's 9 rr (0.064 included) × 25 rules, with the kernel's crowding set to "reproductive". Its scoring contexts are its arm's contexts at κ = 8. The frozen sensitivity subset where its rr lie in the grid adds 12 double-population and double-length jobs, for 237 jobs in all.
- **σ0² families:** for each variant, the 5 rr × 25 rules, with that variant's calibration. The frozen sensitivity subset at rr 0.064 adds 6 jobs, for 131 jobs in all.

**The σ0² calibrations:**
- σ0² is set to 10 and 0.1 times its frozen value.
- Every value the committed calibration protocol derives from σ0² is re-derived from the registered calibration trajectories, on the same seeds. That includes ε_N, and any other ε or reference scale that depends on σ0².
- Every other calibrated or declared value stays frozen.
- Each variant calibration is sealed with its own hash before any variant table job runs.

**Estimation and validation,** unchanged:
- A1's estimation settings and screens.
- Then amendment A4 in full, with each family's own M and M_FV counted from its own A1-style outputs before its validation data exist:
  - the plain tier certified;
  - the Fleming-Viot tier "asymptotic, not certified";
  - the availability floor.
- No plain-law labels (A5) are made for variant families.

**Seeds:**
- Each variant table job's seed follows from its own job identity, which includes its kernel and calibration.
- A4's stream seeds follow from those.
- **The global collision check,** before any simulation, covers:
  - every A1, A4, A5 and rerun seed;
  - every probe and planning seed;
  - every variant seed.

**If a variant family fails,** it cannot load, because a row is not_estimable or the floor fails. Its arm is then reported as not run, with the reason. Any repair is a new amendment. No arm is rescued after any R1 or R2 output has been read.

## 4. The runs

**Configuration.** Each sensitivity run is a rerun job with its arm's settings: κ and θ, steps, the crowding variant or the σ0² calibration, and the matching table family.

**Seeds** are derived from each run's cell and index under the tag `v3_rerun`, as section 6 specifies. The cell identity includes the arm's settings. Seeds are asserted distinct from the 24,900 main reruns and from each other.

**Execution.** The runner and the evidence recording are the reruns'. Section 7's gates govern R1 and R2 citation, and are not re-applied per arm. The arms are read by section 5.

## 5. The reading, registered now

For each arm, the quantities are section 8's, computed on the arm's cells:
- **R1-grid arms:**
  - survival at each rr;
  - the boundary location, by the same interpolation, with a bootstrap interval over seeds. Five points suffice for the σ0² arms, which bracket 0.063.
- **R2-grid arms:** cap\* per alpha at rr 0.064, with D24's censoring.

**Each arm is compared with the nominal v3 result on the same cells,** by the section 9 interval rule:
- **Robust:** the nominal point estimate lies inside the arm's bootstrap interval.
- **Moves lower** or **moves higher:** the interval lies wholly on one side.
- **Undetermined:** the arm's quantity is undefined, for example no crossing in range.

**What a movement means.** Under W11, a headline result that moves under any arm is treated as sensitive to that choice until shown otherwise. Every claim resting on it carries the arm's name in the claims register and wherever it is cited.

**Seed convergence** is reported as the half-seed and full-seed estimates with their intervals. There is no verdict.

## 6. Budget, machines and order

**Ceiling:** 72 X2 wall hours, for the three variant families and the sensitivity runs together. It replaces section 6's separate 48-hour sensitivity ceiling and D18's 24-hour table ceiling for these families.
- The configuration test measures a projection before any registered launch.
- If the projection exceeds the ceiling, the operator decides before any registered run, between a budget amendment and a uniform seed reduction across the arms' cells.

**Planning estimate:**

| Stage | Estimate |
|---|---|
| Tables, crowding family | about 28 h |
| Tables, each σ0² family | about 15 h |
| Runs | about 12 h |

**Machines:** the X2, and any machine the operator has established as bit-identical to it on this workload (D32).

**Order:**
1. **This specification:** committed before any R1 or R2 output is read.
2. **The implementation** (the job builder, the variant calibrations, and the variant families' plans): changes the code identity, so it is committed after the commit the reruns run from, as A5's code is.
3. **The variant families:** may run during the reruns on a bit-identical machine, otherwise after them.
4. **The sensitivity runs:** after all three families are published and the nominal family is in place.

## 7. What A6 does not establish

- **Robustness beyond the arms and ranges registered.** It does not cover the W11 item 3 global screen over the parameter register's constants, which stays unregistered.
- **Anything about the crowding variant as a model** (section 11 says so: it is a sensitivity, not robustness).
- **Certification of variant Fleming-Viot cells beyond A4's asymptotic tier.**
