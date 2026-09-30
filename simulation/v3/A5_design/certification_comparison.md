# A5 blind certification: comparison of the two reports (reviewer, 2026-09-29)

**Reports:** Gemini 3.1 Pro (`cert_gemini/certification_report.md`) and a fresh Claude Code session (`cert_claude/certification_report.md`). Each was blind to the other.

**Both verdicts:** certified with named changes. Neither found a defect in the mathematics.

## Where they agree

| Item | Gemini | Claude |
|---|---|---|
| 1. Plain-law screen for FV tables | certified | certified, with a framing change |
| 2. The test (EB form, width, safeguard, random n) | certified | certified, with its own derivations |
| 3. The family | certified | certified, with a precision change |
| 4. Label-only soundness | certified | certified, with a governance change |
| 5. Seeds | certified | certified, with an implementation change |
| 6. Planning evidence | certified | certified |
| 7. Anything else | one disclosure change | three low changes |

**Depth.** The Claude report derived each item before comparing: the width interval, the random-n marginalization and the Maurer-Pontil log term. The Gemini report mostly restates the design. So the agreement on items 2 and 6 rests mainly on Claude's derivations, and I rechecked the load-bearing ones myself (below).

## Changes and their disposition

| # | Change | Source | Severity | Checked against the code | Disposition |
|---|---|---|---|---|---|
| 1 | Violation governance: state the A4/A5 asymmetry (A4 drops a failing cell, A5 leaves it in use) and make the operator path concrete | Claude | medium | A4 `assemble_fv_row` publishes only passing cells; A5 changes nothing the reruns load | **Adopted,** with a mechanical, pre-registered rule (v2 section 5) |
| 2 | Seed assertion must forbid the full A4 stream set plus `planning_P4` | Claude | medium | Confirmed: `assert_seeds_distinct` forbids only the A1, P1, P1-census, P3 (0 to 3) and probe seeds | **Adopted,** extended to a global check over every seed in the A4 plan (v2 section 3) |
| 3 | Count M from the sealed A4 publication, per row-cell; say whether sensitivity rows are tested | Claude | low-medium | Confirmed: the A4 family published to the reruns holds primary rows only (`assemble_family` returns `primary`); the reruns use only `estimated` rows (`production_tables.py:107`). The A4 plan has 252 primary and 12 sensitivity FV jobs | **Adopted:** A5 tests the 252 primary FV tables only, and M counts the support cells of their `estimated` rows. v1's "264 tables" and its sensitivity sentence were wrong |
| 4 | Markov framing: shared one-step advance kernel, differing within-cell visitation law | Claude | low | Confirmed: A4's FV trace records pre-resampling transitions (`offline_estimator.py:217`) | **Adopted** (v2 sections 1 and 7). It is also the aggregation point the reviewer raised before the reports |
| 5 | The A4 plain, A4 FV and A5 statements do not compose to a joint 0.95 | Claude | low | n/a | **Adopted** (v2 section 7) |
| 6 | State the per-replicate count: 32 groups x 64 runs = 2,048 | Claude | low | Confirmed: `PRIMARY["runs_per_group"] = 64`, `cv.GROUPS = 32`, as in P4 | **Adopted** (v2 section 3) |
| 7 | The certificate bounds the trajectory mean, not the visit-weighted mean | Gemini | low | Matches A4 v2's disclosure | **Adopted** (v2 section 7) |

## Reviewer additions, not raised by either report

- **P4's family was larger.** P4 used M_FV = 797,225 (every A1-published FV cell, primary and sensitivity, any status). A5's M is the A4-validated support of primary estimated rows, which is smaller, so P4's 52% certified is conservative for A5. (Claude noted this in item 6; v2 states it.)
- **Order relative to the reruns.** v1 let A5 run before or after the reruns while leaving violations to the operator's judgement. If A5 finishes after the rerun results are seen, that judgement could depend on the outcomes. v2 fixes the handling now, so the order no longer matters to any decision.
- **Exposure.** v2 reports, for each violation, the share of the row's living census endpoints that fall in the violated cell, so a reader can see how much the reruns lean on it.

## Recheck of the load-bearing mathematics (reviewer)

- **Width.** For a covered transition out of cell b, `r` lies in `[lower - C(b), (1 - beta) upper + beta vmax - C(b)]`, of length `w_row`, and so does each trajectory mean `m_i`. This agrees with Claude.
- **Random n.** Plain trajectories are independent, and the total count is fixed by the plan. So conditional on n = k the selected `m_i` are i.i.d. from the law given `N_i >= 1`, and coverage survives marginalizing over k. This agrees with Claude.
- **Values tested.** FV published values are the A1 values (`assemble_fv_row` takes `support_values` from `a1_published_fv`), so P4 and A5 test the same numbers.

**Result:** all seven changes adopted into `A5_design_v2.md`. None changes the test.
