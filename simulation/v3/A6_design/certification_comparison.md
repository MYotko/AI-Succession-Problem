# A6 blind certification: comparison of the two reports (reviewer, 2026-09-29, overnight)

**Reports:** Gemini 3.1 Pro (`cert_gemini/certification_report.md`) and a fresh Claude Code session (`cert_claude/certification_report.md`), each blind to the other.

**Both verdicts:** not certified as written, because of the reading rule. Every other item is certified, or certified with named changes.

## Where they agree

| Item | Gemini | Claude |
|---|---|---|
| 1. Completeness and fidelity | certified with a named change (the σ0² grid is narrowed, not unchanged) | the same, plus the out-of-range risk |
| 2. Variant families | certified | certified with named changes (scoring restriction; assembly completeness) |
| 3. Seeds | certified | certified (κ and θ must enter the cell identity) |
| 4. Reading rule | **not certified** | **not certified** |
| 5. Budget, machines, order | certified | certified with a named change (loader code identity) |
| 6. Integrity | certified | certified |

**The σ0² re-derivation.** Both halves traced `calibration.py` independently and agree that ε_N is the only calibrated value that depends on σ0². The fixed center, N_ref, ε_E and ε_L do not.

## Changes and their disposition

| # | Change | Source | Severity | Checked | Disposition |
|---|---|---|---|---|---|
| 1 | The reading rule: an interval on the difference (arm minus nominal) with both sampled; a multiplicity correction; materiality margins | both | high | Confirmed: v1 compares the nominal point with the arm's interval | **Adopted,** v2 section 5 |
| 2 | Loader code identity: the weight-corner and horizon arms load the nominal A4 family, which loads only at the A4 identity, but A6's code follows the rerun commit | Claude | high | Confirmed: `production_tables.py:61`. The engine accepts κ, θ, crowding and steps as arguments (`integration.py:51-53`), the runner passes them through (`production_runner.py:190-197`), and registered mode does not restrict them | **Adopted with a different fix,** v2 section 6. The nominal-table arms run in the rerun checkout, from a job list A6's code writes as data. The variant arms run at A6's identity. A6 changes no file on the rerun path, and asserts it. No compatibility extension is needed |
| 3 | Variant families score only the arm's κ = 8 contexts, not `scoring_for_rr`, whose unused rows could fail and sink a family | Claude | moderate | Confirmed: `scoring_for_rr` adds κ = 0.75 rows and R1's other alphas | **Adopted,** v2 section 3 |
| 4 | State that the σ0² grid is narrowed, and the risk that the boundary falls below 0.059 | both | moderate | Confirmed | **Adopted,** v2 sections 1 and 2 |
| 5 | The assembly completeness check is hard-coded to the nominal contexts; note the thin budget margin | Claude | minor | Confirmed: `study.py:170-178` | **Adopted,** v2 sections 3 and 6 |
| 6 | κ and θ must enter each run's cell identity | Claude | minor | Confirmed: `rerun_jobs` omits them | **Adopted,** v2 section 4 |

## Reviewer additions

- **The variant calibration validates at A6's identity.** `validate_calibration` checks conventions and code identity, not σ0² against V_ref (`calibration.py:113-131`). A variant calibration sealed at A6's identity is therefore accepted where the variant arms run.
- **"Robust" should be an equivalence statement,** not the absence of a difference. At 100 seeds, many comparisons will be too wide to settle either way. v2 reads those as "inconclusive" and says so.
