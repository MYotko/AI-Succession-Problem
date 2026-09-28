# v3 Instrument Change and First Reruns: Pre-Registration

**Date:** 2026-09-28.
**Status:** pre-registration. It is committed and pushed before any measured run. No measured run may begin until the note is an ancestor of the published main branch, verified structurally by the executor. The v3 runner refuses registered mode without the note's committed hash.
**Governs:** artifacts under the prefix `simulation/diagnostics/v3_rerun_`.
**Artifacts:** adopts `simulation/diagnostics/ARTIFACT_CONVENTION.md`.
**Implements:**
- W1 step 4, the pre-registration of the instrument change;
- D4 item 1, rerunning the phase boundary and the succession cliff under the new objective.

**Decisions and resolutions.** Decision numbers (D1 to D19) refer to the project's decision record, which will be published with v3. Resolutions R3 to R15 of 2026-09-27 were accepted by the operator on 2026-09-28 (D19), and each is recorded where it applies in the implementation note.

**Supersedes nothing.** The v2.0 results, the Phase B rerun (`phase_b_rerun_design_note.md`) and its verdicts stand as historical results under the old objective.

---

## 1. What this is, and the order of events

v2.0's objective, U_sys, has three independent defects, recorded in `docs/v2_0_instrument_validation_record.md`:
- it diverges for any surviving lineage;
- its inverse-scarcity weights are inert;
- its lineage term vanishes as the lineage collapses.

The operator decided on 2026-09-26 to replace the objective in the paper and the instrument together. The replacement was specified, certified twice and blind, and adopted as decisions D6 to D18. The specification this note implements is the v3 objective specification, draft 3, published with this note as `docs/v3_objective_specification.md`.

**In v2.0, the objective is not only reported; it drives behavior.**
- **Allocation:** `optimize_u_sys_v2` (`simulation/agents.py`) chooses the AI's allocation each step, as the argmax over 300 candidates of a 20-step discounted rollout of U_sys. The allocation sets resource levels, and through them well-being, births and deaths.
- **Yield:** the yield decision (`simulation/model.py`) compares one-step snapshot values of U_sys for the incumbent and the successor against a transition cost.

**Changing the objective therefore changes both the survival dynamics behind the phase boundary and the comparison behind the succession cliff.** These two reruns measure what the new objective does, not only what it reports.

**Order of events, stated because this note follows results.** The author writes knowing:
1. **the v2.0 figures:**
   - the phase boundary's survival curve, with its 50 percent inflection near rr 0.063 (paper Section VIII.2);
   - the succession cliff's fire rates by alpha and capability (Section VIII.4, and Phase B Category B);
2. **the Phase B rerun of 2026-09-24 to 26,** which reproduced Categories A, B and C exactly under the old objective (validation record, item 4, second stage);
3. **the extinction rates of the demographic core (P5) under constant allocations,** from the rare-event work of 2026-09-27:
   - at r = 0.9, about 2.1e-3 per step at b = 0.063, 6.2e-4 at 0.066, 1.07e-5 at 0.070, and 1.4e-18 at 0.080;
   - at r = 1, b = 0.080, about 4.9e-24;
   - finite-horizon confidence certificates from 200 entrants, at ε = 10^−3 for windows up to 1,000 steps;
4. **every certification and decision from D1 to D18;**
5. **the v3 instrument's development:**
   - stages A, B1 and B2, and their implementation note;
   - a non-registered X2 pilot of 2026-09-27 to 28. It measured cost only. Its reruns used fixture tables, so its outcomes are not results and were not used to set anything here.

**The safeguards:**
- no construction parameter in this note is chosen by reference to those figures;
- the rerun grids are v2.0's own, with one change, stated in Section 6;
- every value still open is set by the calibration protocol in Section 5, from runs that do not measure either target.

## 2. What this is not

- **Not a replication of v2.0.** The objective differs by design. The v2.0 figures are comparators, not targets, and nothing is adjusted toward them.
- **Not a certification of the tail standard.** At full scale the rejection test is a diagnostic until certified bias bounds exist (D17 item 5). No run here issues or relies on a tail certificate.
- **Not the other D4 reruns.** Defense and attack wait for the protocol repairs (W3). Cost-audit and phi are new pre-registered studies of their own.
- **Not a paper claim until the gates are revalidated** (W7), and the claims register records the outcome.

## 3. The instrument change

The instrument implements specification draft 3, sections S1 to S7. The implementation note, `simulation/diagnostics/v3_instrument_implementation_note.md`, is committed with this note. The specification is published as `docs/v3_objective_specification.md` (D19), with SHA256 `b74048e489e0e9086570de84c183da89e0ea1db9c553d2f122e8109f44a61559`. That published form differs from the working draft the implementation note pins (`57653952e6d65c21907af3e6982ca71cab8f6c5967fcb593b86c93f14f643e13`) only in its references to private files.

**What changes in the simulation:**
- **The per-step flow** u (S3) replaces U_sys. After extinction, the flow is u†.
  - **Novelty H_N** (R3): n = 64 samples, taken about a fixed center with divisor n, each coordinate clipped at 1.0 from the center, a lookback of 10 steps, and the zero fallback.
  - **H_E** keeps c_E = 2.5, with one common H_E^min.
  - **Lineage L = D_gen × ν × Ψ × Θ,** with these declared, labeled observables (R4):
    - D_gen is the diversity of novelty propensities, a proxy and not genetic diversity;
    - Ψ is the institutional stock alone;
    - the frontier is v = capability × θ_capability, over bandwidth b = mean welfare × transfer;
    - bandwidth is clipped uniformly at b_min;
    - φ_tr = exp(−(1 − transfer)·v/v_max).
- **The objective** is W = θ·D_ρ + (1 − θ)·Λ_F (S4), with ρ = 0.01 per step and Δ = 1 step (R6). phi does not enter (D6).
- **The evaluation model** (D18 item 1):
  - a declared class Π of **25 stationary feedback allocation rules**, reduced from 289 before any estimate (R5, R11), and frozen by rule IDs and a class hash;
  - each rule satisfies the welfare floor and the pointwise reproduction floor by construction, and this is checked over the whole age and welfare grid;
  - each step, the AI evaluates θ·D_ρ(π | current state) + (1 − θ)·Λ_F(π) for every rule. D_ρ is rolled out for 20 steps, with a per-rule continuation table over the rule's summary bins (R6), and acts on point estimates. Overlapping intervals are recorded as unresolved ordering.
- **The offline tables** (R13):
  - Λ_F comes from plain independent runs wherever at least half the runs survive through the measurement window, and from Fleming-Viot otherwise;
  - ζ comes from Fleming-Viot where it resolves the rate, and is otherwise reported as an upper bound or unresolved;
  - sensitivity settings run on a declared subset of 3 rules × 3 rr;
  - the tables are frozen and hashed, and registered mode rejects fixture, missing or stale rows.
- **Admission** (D8, R8): by the deterministic cohort bound, certified twice in W1E.
  - **The bound:** P(extinction within 50 steps) ≤ Π over living agents of P(the agent dies within 50 steps), at the lowest welfare path the floors allow. It is exact integer arithmetic, and the same for every admissible rule.
  - **From v2.0's initial law,** the bound is 5.209e-7, below ε_surv = 10^−3 for every rule and rr.
  - **Protection periods** of T_P = 25 steps, each with its own ledger, look 50 steps ahead from the period's start.
  - **Where the bound exceeds ε,** the admissible action minimizing it is taken, both floors hold, and yield is held (R14). A failed bound is not recorded as infeasibility.
- **The no-write-off rule** (R7): γ = 0.05, relative to extinction probability.
- **Yield** (S7, R9):
  - it is reviewed every 10 steps;
  - V_n is the best of yielding at the next review, yielding at a later review up to the period's 25-step deadline, or holding to the deadline;
  - plans form a declared restricted class, and values are in the epoch's committed units;
  - the transition's actual disruption is simulated inside the successor plan, so Γ is counted once, and v2.0's transition-cost formula is not used;
  - successor chains stay at fixed capability, with the ceiling at 5.0.
- **Finite grids** (R4, R14): stocks on a 0.01 grid with 16 environmental microsteps per step, and welfare on a 0.001 grid. Mean paths track v2.0's continuous dynamics within the stated tolerance; the full law is not identical.

**What does not change:**
- the demographic step rule, and the successor construction at 1.5 times the incumbent's capability;
- the survival rule of the targets: final population of at least 30 at the horizon;
- the horizon: 500 steps.

**The grain of the yield decision.** v2.0 evaluated yield at every step; v3 reviews it every 10 steps (R9). The cliff's fire rate is therefore measured at a coarser decision grain. The readings in Section 9 are unchanged; the difference is reported beside them.

## 4. Pre-registration choices (S12), as decided

| Choice | Value | Source |
|---|---|---|
| Shocks | None. v2.0's Categories A and B ran with no shock. | D18 item 9 |
| Model set M | The nominal model only. The reproductive-age crowding variant is a sensitivity, at a quarter of the seeds. | D18 items 4 and 9 |
| T_P, H, ε_surv | T_P = 25, H = 25, ε_surv = 10^−3 | D18 item 5; R6 for the split |
| No-write-off tolerance γ | 0.05, relative to extinction probability | D18 item 9; R7 |
| H_N | n = 64, fixed center from calibration, lookback 10, size tolerance the larger of 5 percent or 0.01 bits | D18 item 9; R3 |
| Tail-standard benchmark set S | Π at 95 percent simultaneous confidence; a diagnostic at full scale | D18 items 7 and 9 |
| Evaluation model | Section 3 | D18 item 1; R5 to R9, R13 |
| Capability ceiling | 5.0, inclusive; a cell above it is reported as not admissible | D18 item 3 |
| Confidence budget | Not spent: admission is deterministic. The α = 0.01 ledger stays unspent. | D18 item 6; R8 |

## 5. Calibration protocol

**The rule:** every calibrated value is set from runs that measure neither target, and frozen, with its hash, in `v3_rerun_calibration.json` before any registered run. No calibrated value is revised after any registered output is read. A revision needs an amendment, and a restart of every affected part.

- **Calibration runs:** the balanced honest baseline at rr = 0.080, no successor, 50 seeds and 500 steps. Its seeds are disjoint from the registered rule's, because they use a different tag.
- **Values set from them:**
  - **σ0² = 0.1 × V_ref/d,** where V_ref is the baseline's **total** novelty variance, so that σ0² is one tenth of the per-direction variance (D9; R3).
  - the H_N fixed center;
  - N_ref and the reference scales;
  - **each ε** at 1 percent of the smaller of its declared protected level and its calibration lower measurement bound. If no positive reliable bound exists, calibration is unresolved and no run is registered.
- **Values set by declaration, not calibration:**
  - ρ = 0.01 per step, with Δ = 1 step (R6);
  - c_E = 2.5, the legacy value;
  - Ψ uses one weight, on the institutional stock (R4);
  - **the weight region** (D18 item 2): the center κ = 8, θ = 0.5, with corners κ ∈ {0.75, 8} × θ ∈ {0.25, 0.75} at reduced seeds;
  - α is swept by the grids, as in v2.0;
  - the capability ceiling is 5.0, with v_max = 5.0;
  - b_min = v_max / (1 + ln(1/ε_L)/α_min), with α_min = 0.5, so that Θ(v_max, b_min) ≤ ε_L for every declared α.

## 6. The reruns

**R1, the phase boundary** (v2.0 Category A).
- **Grid:** rr ∈ {0.055, 0.056, 0.057, 0.058, 0.059, 0.060, 0.062, 0.064, 0.066} × alpha ∈ {0.5, 1.0, 1.5}, with successor capability 1.5.
- **The one change: phi is dropped** as a grid factor, because it does not enter the v3 objective (D6). v2.0's 1,200 runs per rr came from 4 phi × 3 alpha × 100 seeds. **R1 keeps 1,200 per rr, as 3 alpha × 400 seeds**, so the per-point precision is v2.0's: a standard error of at most 1.45 points.
- **Total:** 10,800 runs.
- **A refinement grid,** registered now: rr ∈ {0.061, 0.063, 0.065}, at the same seeds per cell (3,600 runs).

**R2, the succession cliff** (v2.0 Category B).
- **Grid:** rr ∈ {0.057, 0.060, 0.064, 0.070} × alpha ∈ {0.5, 0.75, 1.0, 1.25, 1.5} × successor capability ∈ {1.2, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0}, with 75 seeds per cell. phi is dropped as in R1; v2.0 fixed it at 25 here.
- **Total:** 10,500 runs.

**Sensitivity and convergence (W11), registered now:**
- **Weight corners:** each of the four (κ, θ) corners, on R1's rr grid at alpha 1.0 and on R2's alpha × capability grid at rr 0.064, with 100 seeds per cell.
- **Horizon:** R1's grid at 1,000 steps, alpha 1.0, 200 seeds.
- **Crowding:** the reproductive-age variant (Section 4).
- **σ0²:** one decade either side, on R1 at alpha 1.0, 100 seeds.
- **Seed convergence:** the R1 and R2 estimates are reported at half and full seed counts.

**Seeds.** Each run's seed is derived from its cell and index by a hash, independent of worker and schedule, with the tag `v3_rerun`. It shares no seed with v2.0, Phase B or the pilot.

**Cost.**
- **Ceilings** (D18 item 8), in X2 wall hours:
  - 72 for R1, R2 and the refinement grid;
  - 48 for the sensitivity runs;
  - 24 for the offline tables.
- **The pilot's measured projection** (non-registered, X2, 2026-09-27; `simulation/diagnostics/v3_pilot_cost_projection.json`):
  - R1, R2 and the refinement grid need **about 11.2 X2 wall hours**, and 11.9 in the most expensive tested case;
  - the tables need **about 1.0 hour**, on the conservative route;
  - the calibration needs under a minute.

  The configuration test selected 16 workers for the reruns and tables, and 31 for calibration. Near the boundary, the pilot's populations averaged 42 to 195 agents, never exceeding 282.

  **Limits:** the pilot used fixture scoring tables, so the calibrated tables can change the decisions and the cost. The sensitivity runs were not piloted separately. Scaled by run-equivalents, they need about 12 hours, against 48.
- **If a measured projection exceeds its ceiling,** the operator decides, before any registered run, between a budget amendment and a uniform seed reduction across cells. Nothing is cut after a registered output is read.

## 7. Gates

Items 1, 3, 4 and 5 must hold before any registered run. Item 2 follows the runs.

1. **Every S10 conformance test passes** on the committed instrument, and the results are committed. At the end of B2: 216 passed, and the 3 expected failures are pre-existing v2.0 tests.
2. **The gates are revalidated after the reruns, on their registered outputs** (W7, D19). Gate G2.2 is defined on the cliff's own output, cap\*, and Gate 3 carried the earlier boundary and cliff grids, so revalidation follows the runs. **No result of this note is cited until W7 has revalidated the gates that govern it.** A result whose governing gate fails revalidation is reported with that failure and is not cited.
3. **The offline tables** (Λ_F, continuation and ζ, for each rule in Π and each context) are complete and hashed, with row statuses. Each passes its stability screens.
4. **The calibration file** is frozen and hashed.
5. **The pre-launch configuration test** has selected the configuration, and it is recorded.

## 8. Registered quantities

- **R1:** the survival rate (final population of at least 30 at 500 steps) and the extinction rate (population 0) at each rr, pooled over alpha and by alpha, each with a Wilson interval at z = 2.
- **The boundary location:** the rr at which survival crosses 50 percent, by linear interpolation between adjacent grid points (including the refinement grid), with a bootstrap interval over seeds. v2.0 stated no formal rule; this note registers one.
- **R2:**
  - the fire rate (the mean of `yield_fired`) per cell;
  - **cap\*** per alpha, as in G2.2: the largest capability with a fire rate of at least 0.5, pooled over rr;
  - the first failing capability, as in the paper's prose.
- **Diagnostics, per run:**
  - the share of steps under survival-first;
  - the cohort bound at each period start;
  - the number of precedence overrides (expected zero, since a failed bound never overrides);
  - the chosen rules;
  - Λ_F, Λ_b and LS of the chosen rules where estimable, and the ranking flag (S4);
  - the tail-standard diagnostic.

**Anything else computed is labeled exploratory, and may not be cited as a result of this note.**

## 9. Readings, declared now

The targets are new measurements, not reproductions, so there is no identical or faithful verdict. Each v2.0 comparison is classified:

**R1, the boundary location against v2.0's inflection near 0.063:**
- **Consistent:** v2.0's inflection lies inside the v3 bootstrap interval.
- **Shifted lower** or **shifted higher:** the interval lies wholly on that side.
- **No transition in range:** survival does not cross 50 percent inside [0.055, 0.066].

**R2:**
- **Cliff present:** cap\* is non-increasing in alpha (G2.2's rule), and for alpha ≥ 1.0 some tested capability fires below 0.5.
- **Cliff absent:** otherwise.
- **The location** is reported per alpha against v2.0's cap\* sequence (5.0, 3.0, 2.5, 2.0, 2.0), as consistent, lower or higher, by the same interval rule, using a bootstrap over seeds.

Every reading is reported. None is a pass or a fail of v3.

## 10. Predictions, registered now and reported as right or wrong

- **P1:** survival is non-decreasing in rr across the R1 grid.
- **P2:** at each rr from 0.055 to 0.062, v3 survival is at least v2.0's published value, minus two of v3's standard errors.
  - **The basis**: D8 does not bind from the start, since the cohort bound from 200 entrants is 5.2e-7. It binds when a population becomes small, and then the survival-first rule takes the bound-minimizing action. Throughout, the welfare floor forbids the crowding-relief allocations that v2.0's objective permitted.
- **P3:** R2's cliff is present, as defined in Section 9.
  - **The basis:** the lineage factor Θ carries the same kind of penalty on frontier velocity over bandwidth that produced v2.0's cliff.

**The author's expectation, stated before any run** (a prediction, not a criterion):
- **R1 shifted lower,** by up to about 0.003 in rr.
  - **The reasoning:** in the demographic core, moving from r = 0.9 toward r = 1 lowers the extinction rate by orders of magnitude near the boundary. Survival-first should push allocation toward full welfare as populations shrink.
  - **The uncertainty:** how much of the v2.0 allocation was already near full welfare is not known.
- **R2's cliff present,** with its location uncertain in both directions:
  - the strict rule and full waiting plans make marginal yields rarer;
  - removing v2.0's separate transition cost makes them more common;
  - the coarser review grain can move it either way.

## 11. What this cannot establish

- **That the objective is right.** The reruns measure what it does, under declared weights, calibration, observables and an evaluation model.
- **Anything beyond the declared model set M,** which is the nominal model. The crowding variant is a sensitivity, not robustness.
- **A tail certificate.** The tail standard is diagnostic at full scale.
- **Anything about windows beyond 50 steps.** Admission uses the cohort window. The deterministic bounds of the rare-event work reach no further.
- **Transfer outside the tested grids,** or to shocks.
- **Anything about policies outside Π, or plans outside the declared plan class.** The optimum over Π is not the optimum over all stationary policies.
- **Genetic diversity or multi-channel responsiveness.** D_gen and Ψ are declared proxies (R4).

## 12. Execution, which is the operator's

The runner (`v3.production_runner`) meets `AGENTS.md`, including:
- persisted completion records, and seeds independent of schedule;
- resume that validates completed jobs;
- live `work` and `normal` modes;
- one numerical-library thread per worker unless the configuration test selects otherwise;
- a recorded execution record.

It refuses registered mode without the committed hash of this note, and without non-fixture calibrated tables.

**On the X2,** the service lease stands the model server down with `llm down` for the registered parts, and records it. It is restored with `llm up` on every exit path.

**The pre-launch configuration test** (AGENTS.md, 2026-09-27) runs short jobs of the actual workload at 8, 12, 16, 24, 28, 31 and 32 workers, 32 in a dedicated test mode only. It selects the fastest admissible configuration, preferring the smaller within 5 percent, and records the measurements. Launch caps are 31 (normal) and 28 (work). On 2026-09-27 the test selected 24 workers for proof arithmetic and 16 for full-size direct simulation, so the choice is measured per workload.

**A test-mode or pilot run is declared non-registered.** An error row is a finding, and it is never retried silently.

## 13. Amendment rule

- Any change to this note after commit is a dated amendment, committed and pushed before the output it affects is read.
- Each amendment states whether any registered output had been read when it was written.
- Nothing is adjusted toward a v2.0 figure.
