# Readiness of the registered W11 sensitivity and convergence runs (reviewer, 2026-09-29)

**Status:** a scoping note from reading the code and the design note. Nothing was run, and no registered output was read.

**A correction to my own earlier suggestion.** I proposed pre-registering the sensitivity and convergence runs. They are already registered, in section 6 of the design note ("Sensitivity and convergence (W11), registered now"). What is missing is their implementation, and two of their arms have no tables. The five parameter-register decisions belong to a different, unregistered item: the W11 item 3 global screen (for example, Morris elementary effects over the arbitrary constants).

## The registered arms, and what each needs

| Arm (design note section 6) | Needs its own tables? | Why |
|---|---|---|
| Weight corners, κ ∈ {0.75, 8} × θ ∈ {0.25, 0.75} | No | The table family already scores κ = 0.75 rows on exactly these grids (`study.scoring_for_rr`). θ enters only the online score (`integration.py:186`). |
| Horizon, 1,000 steps | No | The tables are discounted and horizon-free; only the run length changes. |
| Seed convergence | No | The R1 and R2 estimates are reported at half and full seed counts. |
| Crowding, the reproductive-age variant | **Yes** | The tables' kernel identity includes crowding (`tables.kernel_identity`), so the loader refuses nominal tables. The table jobs are built with the nominal kernel only. |
| σ0², one decade either side | **Yes, twice** | σ0² is the novelty protocol's `sigma_squared`, and the protocol is part of the kernel identity. The ε values are calibrated from σ0²-dependent measurements (`calibration.py:63-126`). |

The readiness pilot had already flagged this: "extra kernels for crowding/novelty sensitivities remain explicit" (`pilot.py:113`).

## Gaps

1. **No job builder.** `study.py` builds the 24,900 reruns and the table jobs, but no sensitivity-run jobs.
2. **Two arms need table families** that are neither registered nor budgeted:
   - **Crowding** on the weight-corner grid (R1's 9 rr values, which include 0.064): 225 table jobs.
   - **σ0²:** 225 jobs for each of the two variants on R1 at alpha 1.0, so 450.
   - **Total:** 675 jobs, about 2.1 times A1's 325 primary jobs.
3. **The rough cost is well over the registered ceilings.** The ceilings are 48 hours for the sensitivity runs and 24 for tables.

   | Stage | Basis | Estimate |
   |---|---|---|
   | Estimation | A1 took 5.7 X2 hours for 343 jobs | about 12 hours |
   | Validation | A4 takes about 35 hours for 343 tables | about 70 or more hours |
   | Plain-law labels | as A5 | about 25 more hours |

   The "about 12 hours" in section 6 counts the runs only.
4. **Two arms are underspecified:**
   - **Crowding:** section 4 says "a quarter of the seeds", but no grid is registered.
   - **σ0²:** the arm does not say whether the ε values and N_ref are re-derived under the varied σ0², or held at their frozen values.

## Decisions for the operator

1. **What a variant arm tests.**
   - **(a) Refit (recommended for crowding):** fit tables under the variant, so the policy re-optimizes in the variant world. This is the consistent test, and it is expensive.
   - **(b) Nominal tables applied in the variant world:** this tests how robust the nominal policy is to the variant. It is cheap, since only the runs are needed. But it answers a different question, and it needs a declared loader exception, because the kernel identity differs.
2. **The grids:**
   - **Crowding:** recommend the weight-corner grid, R1's rr values at alpha 1.0 and R2's alpha × capability at rr 0.064, at a quarter of the seeds.
   - **σ0²:** recommend narrowing it to the rr values nearest the phase boundary, for example 5 of R1's 9.
3. **σ0²'s dependent values:** re-derive the ε values from the varied σ0² (the consistent choice), or hold them frozen (which isolates the measurement effect).
4. **Budget:** a table-and-validation ceiling for the sensitivity families, set before any of their runs.
5. **Where it is registered:** a separate registered document, committed before any rerun output is read. It must not go into the design note between the rerun pin and the gate index, because that would break the gate index's pin check. The design note gets a dated pointer to it after the rerun gates.

## Timing

None of this delays the reruns. The specification should be committed before any R1 or R2 output is read, so the sensitivity grids cannot be chosen after the main results are seen. The implementation (the job builder, and the variant tables' estimation and validation) changes the code identity. So, like A5's code, it follows the rerun commit.

## Planning pass (operator approved, 2026-09-29): measured task costs and the options

**The inputs,** aggregates only (`scratchpad/sens_timings.py`, read-only on the X2):
- the A1 table records' worker seconds by route;
- the A4 run 3 completion records' worker seconds by phase.

No per-rr route breakdown, no stage-output content, and no survival, extinction or fire quantity.

**Measured cost per task, in worker seconds:**

| Task | Plain route | Fleming-Viot route |
|---|---|---|
| A1-style estimation, primary, R1 grid | 202 (n = 24) | 1,577 (n = 201) |
| A1-style estimation, sensitivity settings | 695 | 3,751 |
| A4 fit | 870 (n = 79) | none |
| A4 validation, per replicate | 1,026 (n = 237), 3 replicates | 3,101 (n = 32 so far), 1 replicate |
| A5-style labels, per replicate | none | about 950 (P4), 3 replicates |

**Assumed, not yet measured:**
- the A4 census, at about 150 s: it uses 6 groups and 519 steps;
- the high-memory Fleming-Viot validation, at about 6,200 s, twice the primary.

**Route mix.** 201 of the 225 primary tables on R1's rr grid are Fleming-Viot. The projections assume a variant family has the same mix; an all-plain family would cost less. Each family also includes its 12 sensitivity-setting jobs, which the table screens need for their contrasts, so a family is 237 jobs.

**Per variant family** (R1's 9 rr values, 237 jobs):
- estimation plus A4 validation: about **332 core-hours**;
- A5-style labels, optional: about 159 more.

**Wall time.** The ideal wall time is core-hours divided by 16 workers. The realistic figure multiplies that by 1.35, the ratio A4 run 3 is showing so far.

| Option | Table families refit | Estimation plus validation, realistic X2 hours | With A5-style labels | Plus the sensitivity runs |
|---|---|---|---|---|
| **O1.** Refit all three arms on the registered grids | crowding and both σ0² variants | about **84** | about 124 | +12 |
| **O2.** Refit crowding, and σ0² narrowed to 5 of R1's 9 rr values | crowding plus 2 narrowed | about **59** | about 87 | +12 |
| **O3.** Nominal tables in the variant worlds | none | 0; needs a declared loader exception | none | +12 |
| **O4.** Refit crowding only; σ0² dropped, or run on nominal tables | crowding | about **28** | about 41 | +12 |

**Ceilings.**
- D18 item 8 set 24 hours for tables and 48 for the sensitivity runs. Every refit option needs a budget amendment. O4 is closest to 24.
- The X2 is dedicated, so the real cost is calendar time. O2 without labels, plus the runs, is about 3 days after the reruns and A5.

**A risk for any refit.** A variant family must pass A4's screens and floor, as the nominal family must. If a variant row is not estimable, the registered loader refuses the whole family and that arm cannot run. The nominal family needed two amendments before its tables passed.

**Reviewer recommendation:**
- **O2 without A5-style labels.** The variant Fleming-Viot rows keep "asymptotic, not certified". Labels can be added later, since they change nothing.
- **Why refit:** it is the consistent test of "would the result differ had this arbitrary choice been different". Nominal tables would test a misspecified policy instead.
- **σ0²'s ε values** are re-derived from the varied σ0², for the same reason.
- **If calendar time matters more,** O4, with σ0² reported as not run and the reason stated.

## Suggested next step

A short planning pass that:
- counts the variant table jobs by route, since the Fleming-Viot share drives validation cost;
- projects each option from A1 and A4's measured timings;
- produces a decision table for the operator.

It is non-registered and uses no compute beyond arithmetic.
