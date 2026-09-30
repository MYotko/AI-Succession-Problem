# A6 design, version 2: the W11 sensitivity and convergence runs, completed

**Status:** revised after blind double certification, 2026-09-29 (overnight), by the reviewer. Both halves (Gemini 3.1 Pro and a fresh Claude Code session) certified every item except the reading rule, and named changes; `certification_comparison_A6.md` gives each change and its disposition. Nothing here is adopted. It becomes amendment A6 only after the operator's approval, and must be committed before any R1 or R2 output is read.

**Changes from v1:**
- a new reading rule: difference intervals, a Bonferroni family and materiality margins;
- the nominal-table arms run in the rerun checkout, so the loader accepts the nominal family;
- variant families score only their arm's contexts;
- the σ0² narrowing is stated as a change, with its risk.

## 1. Purpose

Section 6 of the design note registers five sensitivity and convergence arms. Three gaps stop them running as written:
1. **No job builder.** Nothing builds their jobs.
2. **Missing tables.** The crowding and σ0² arms need their own table families, because the tables' kernel identity includes the crowding variant and the novelty protocol, which holds σ0².
3. **No reading rule.** Section 8 lists no sensitivity quantity, so every sensitivity result would be exploratory.

A6 closes the three gaps. It makes one change to section 6, authorized by the operator under option O2 (D32): **the σ0² arm is narrowed from R1's nine rr to five** (section 2). Every other arm, grid, weight, horizon and seed count in section 6 is unchanged.

## 2. The arms

| Arm | Grid | Seeds per cell | Tables | Runs |
|---|---|---|---|---|
| Weight corners, κ ∈ {0.75, 8} × θ ∈ {0.25, 0.75} | R1's 9 rr at alpha 1.0, capability 1.5; R2's 5 alpha × 7 capabilities at rr 0.064 (44 cells) | 100 | nominal A4 family, which already scores κ = 0.75 on these contexts | 17,600 |
| Horizon | R1's 9 rr at alpha 1.0, 1,000 steps | 200 | nominal | 1,800 (3,600 run-equivalents) |
| Crowding, the reproductive-age variant | the weight-corner grid (44 cells) | 100 | **crowding family** | 4,400 |
| σ0² ×10 and σ0² ×0.1 | the five R1 rr nearest v2.0's registered inflection, 0.063 (section 9): 0.059, 0.060, 0.062, 0.064, 0.066; alpha 1.0 | 100 | **two σ0² families** | 1,000 |
| Seed convergence | R1 and R2 at half and full seeds | none | none | 0 |

**Readings made explicit:**
- **Crowding seeds.** D18's "a quarter of the seeds" is read as a quarter of R1's 400 per cell, which gives 100.
- **The σ0² narrowing is a change, authorized under O2.**
  - **The choice:** by distance from the registered v2.0 inflection, fixed before any v3 rerun output. The tie at 0.003 (0.060 and 0.066) includes both.
  - **Its cost:** a σ0² variant whose boundary falls below 0.059 reads "undetermined, below range" (section 5).
- **Unvaried weights:** at the center (κ = 8, θ = 0.5), with capability 1.5 on R1's grid.

## 3. The variant table families

**Composition.** Each family is built with the committed table-job settings, and its **scoring contexts are exactly its arm's cells at κ = 8.** It does not use the committed `scoring_for_rr`, which would add κ = 0.75 rows and R1's other alphas that no arm looks up, and whose failure could sink a family.
- **Crowding family:** R1's 9 rr × 25 rules, with the kernel's crowding set to "reproductive".
  - **Contexts:** alpha 1.0 × the capabilities from 1.5 at every rr, plus R2's alpha × capability contexts at 0.064.
  - **Sensitivity jobs:** the frozen table-sensitivity subset at 0.055 and 0.064 adds 12 double-population and double-length jobs, for 237 jobs in all.
- **σ0² families:** for each variant, the 5 rr × 25 rules with that variant's calibration, and contexts of alpha 1.0 × the capabilities from 1.5. The sensitivity subset at 0.064 adds 6 jobs, for 131 jobs in all.

**Assembly.** A family is complete when every one of its own contexts has a row. The nominal `assemble_tables` completeness check is hard-coded to the nominal contexts, so A6 supplies its own check with the same logic.

**The σ0² calibrations:**
- σ0² is set to 10 and 0.1 times its frozen value.
- **ε_N is re-derived** from the registered calibration trajectories on the same seeds, by the committed protocol (`calibration.py:66-94`). ε_N is the only calibrated value that depends on σ0²; both certifiers traced this independently.
- **Every other value stays frozen:** the fixed center, N_ref, ε_E, ε_L and c_E.
- Each variant calibration is sealed with its own hash before any variant table job runs.

**Estimation and validation,** unchanged:
- A1's estimation settings and screens.
- Then amendment A4 in full, with each family's own M and M_FV counted from its own outputs before its validation data exist:
  - the plain tier certified;
  - the Fleming-Viot tier "asymptotic, not certified";
  - the census under the family's own kernel;
  - the availability floor.
- No A5 labels.

**Seeds:**
- Each variant table job's seed follows from its own job identity, which includes its kernel and calibration.
- A4's stream seeds follow from those.
- A global collision check before any simulation covers every A1, A4, A5, rerun, probe, planning and variant seed.

**Failure.** A family that cannot load (a row not_estimable, or the floor failed) makes its arm "not run", reported with the reason. Any repair is a new amendment. No arm is rescued after any R1 or R2 output has been read.

## 4. The runs

**Configuration.** Each run is a rerun job whose `model` settings carry its arm's values: κ, θ, the crowding variant, and the tables and calibration paths. Its step count is its arm's. The engine takes these as arguments (`integration.py:51-53`), and the runner passes them through (`production_runner.py:190-197`).

**Seeds.** They are derived from each run's cell and index under the tag `v3_rerun`, as section 6 specifies. **The cell identity includes κ, θ, steps and the variant,** so every arm's seeds differ from the 24,900 main reruns and from each other. That is asserted before dispatch.

**Execution.** The runner and the evidence recording are the reruns'. Section 7's gates govern R1 and R2 citation, and are not re-applied per arm.

## 5. The reading, registered now

### Quantities

Section 8's, on each arm's cells:
- **R1-grid arms:** survival at each rr, and the boundary location.
- **R2-grid arms:** cap\* per alpha at rr 0.064, with D24's censoring.

**The nominal comparator** is the same quantity from the main reruns on the same cells:
- R1 at alpha 1.0 on the arm's rr, without the refinement grid;
- R2 at rr 0.064 only.

The horizon arm's survival is measured at 1,000 steps, and its comparator at 500. That is the convergence question W11 asks.

### The headline family

33 comparisons:
- the boundary location in 8 arms (4 corners, horizon, crowding, 2 σ0²);
- cap\* at each of 5 alphas in 5 arms (4 corners, crowding).

### The difference interval

For each headline comparison:
- a percentile bootstrap interval on the **difference (arm minus nominal)**;
- the arm's and the nominal runs resampled independently, by seed within cell, since they share no seed;
- at least 50,000 resamples;
- at level **1 − 0.05/33** (Bonferroni), so the family-wise error is at most 0.05.

### Materiality margins, declared now

- **Boundary location:** 0.002 in rr, the main grid's spacing between 0.060 and 0.066.
- **cap\*:** one step of the capability grid (1.2, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0). The difference is measured in grid steps.

### Verdicts

- **Moves materially,** lower or higher: the difference interval lies wholly beyond the margin on one side. For cap\*, that is at least one step.
- **Robust:** the interval lies wholly within the margin. For cap\*, it contains zero steps only.
- **Inconclusive:** anything else. At 100 seeds this is expected to be common, and it is reported as such.
- **Undetermined:** the quantity is undefined in the arm or its comparator, for example no crossing in range, or a σ0² boundary below 0.059.

### What follows

- **Moves materially:** every claim resting on that headline result carries the arm's name as a sensitivity, in the claims register and wherever it is cited, until shown otherwise (W11).
- **Inconclusive or undetermined:** reported with the claim, as "sensitivity to [arm] not resolved at the registered seeds".
- **Robust:** reported. No label.

**Descriptive only, with no verdict:**
- the survival differences at each rr, with per-comparison 95 percent intervals;
- the seed-convergence half-seed and full-seed estimates.

## 6. Order, code identity, budget and machines

**Code identity.** The rerun loader accepts the nominal A4 family only at the exact code identity that published it (A5, Sequencing).
- **The nominal-table arms** (weight corners and horizon) run from the **rerun checkout**, at the rerun commit's code identity.
  - A6's builder writes their job list as a sealed manifest, which is data.
  - The runner there checks each job's identity (`stable_job`, which is independent of code) and the rerun pin, since the design note does not change.
- **The variant arms** (crowding and σ0²) run at A6's implementation identity. There, their calibrations and families are sealed and published, and their runs load them.
- **A6's implementation adds new modules only.** It changes no existing file under `simulation/`, so every arm runs the engine code the reruns run. It asserts that the rerun-path files are byte-identical to the rerun commit's.

**Order:**
1. **This specification:** committed before any R1 or R2 output is read. The aim is before the rerun pin.
2. **The implementation:** committed after the rerun commit, like A5's code.
3. **The variant families:** during the reruns on a bit-identical machine, otherwise after them.
4. **The runs:** once their tables are in place.

**Ceiling: 72 X2 wall hours** for the three families and all sensitivity runs. It replaces section 6's 48-hour sensitivity ceiling and D18's 24-hour table ceiling for these families.
- **The planning estimate** is about 70 hours: about 28 for the crowding tables, about 15 for each σ0² family, and about 12 for the runs. The restricted scoring lowers it slightly.
- **The margin is thin,** and the crowding route mix is unmeasured.
- **The measured projection** before each registered launch governs. If it exceeds the ceiling, the operator decides before any registered run, between a budget amendment and a uniform seed reduction across the arms' cells.

**Machines:** the X2, and any machine the operator has established as bit-identical to it on this workload (D32).

## 7. What A6 does not establish

- **Robustness beyond the registered arms and ranges.** In particular it does not cover the W11 item 3 global screen over the parameter register's constants, which stays unregistered.
- **Anything about the crowding variant as a model:** it is a sensitivity, not robustness (section 11).
- **Certification of variant Fleming-Viot cells** beyond A4's asymptotic tier.
- **Power:** at 100 seeds per cell, "inconclusive" is not evidence of robustness.
