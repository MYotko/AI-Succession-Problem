# v3 Instrument Change and First Reruns: Pre-Registration

**Date:** 2026-09-28.
**Status:** pre-registration. It is committed and pushed before any measured run. No measured run may begin until the note is an ancestor of the published main branch, verified structurally by the executor. The v3 runner refuses registered mode without the note's committed hash.
**Governs:** artifacts under the prefix `simulation/diagnostics/v3_rerun_`.
**Artifacts:** adopts `simulation/diagnostics/ARTIFACT_CONVENTION.md`.
**Implements:**
- W1 step 4, the pre-registration of the instrument change;
- D4 item 1, rerunning the phase boundary and the succession cliff under the new objective.

**Decisions and resolutions.** Decision numbers (D1 to D24) refer to the project's decision record, which will be published with v3. Resolutions R3 to R15 of 2026-09-27 were accepted by the operator on 2026-09-28 (D19), and each is recorded where it applies in the implementation note.

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
  - **The bound:** P(extinction within 50 steps) ≤ Π over living agents of P(the agent dies within 50 steps), at the lowest welfare path the floors allow. It uses exact integer arithmetic. This period-start certificate uses the common floor path and is the same for every admissible rule. The first-action-conditioned bound used to choose a survival-first action also includes that rule's actual first-action welfare, so it can differ across rules.
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

Items 1, 3, 4 and 5 must hold before any registered run. Item 2 has before
and after parts, fixed by D21 and amendment A2 in section 13.

1. **Every S10 conformance test passes** on the committed instrument, and the results are committed. At the end of B2: 216 passed, and the 3 expected failures are pre-existing v2.0 tests.
2. **The v3 gates are independently revalidated** (W7, D19, D21). Before: G1.1 to G1.5 and G3.1's positive, negative and tie scenarios. After: G2.2, G3.1's registered review sample, G3.2, G3.3 and G4.1 to G4.3. R1, including its refinement, requires G1.1, G1.2, G1.4, G1.5, both parts of G3.1 and G4.3. R2 also requires G1.3, G3.2, G3.3 and G4.1. R2's cliff reading additionally requires G2.2 and G4.2. G2.1 and G2.4 belong to the phi study; G2.3 waits for W3's D12/W2 game; G5.1 and G5.2 wait for P4. These are explicitly not applicable. **Every governing check must pass for citation, except D23's explicit G3.3 zero-fire exception for R2 fire rates.** Zero fired R2 successions in the complete family is reported as not_testable, not a pass; it does not block R2 fire-rate citation. R2_cliff still requires G2.2 and G4.2. Missing, skipped, unimplemented and other not-testable applicable checks cannot count as passes. A failure is reported with the result and prevents its citation. A2 fixes the complete statements, evidence and pass rules before any registered rerun output is read. D24 orders censored cap* values and requires G4.2 to pass every testable alpha, with at least one testable; untestable alphas and reasons are reported.
3. **The offline tables** (Λ_F, continuation and ζ, for each rule in Π and each context) are complete and hashed, with row statuses. Each passes its stability screens.
4. **The calibration file** is frozen and hashed.
5. **The pre-launch configuration test** has selected the configuration, and it is recorded.

## 8. Registered quantities

- **R1:** the survival rate (final population of at least 30 at 500 steps) and the extinction rate (population 0) at each rr, pooled over alpha and by alpha, each with a Wilson interval at z = 2.
- **The boundary location:** the rr at which survival crosses 50 percent, by linear interpolation between adjacent grid points (including the refinement grid), with a bootstrap interval over seeds. v2.0 stated no formal rule; this note registers one.
- **R2:**
  - the fire rate (the mean of `yield_fired`) per cell;
  - **cap\*** per alpha, as in G2.2: the largest capability with a fire rate of at least 0.5, pooled over rr, with D24's top and bottom censoring in A2;
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
- **Cliff present:** cap\* is non-increasing in alpha (G2.2's point rule only, using D24's censored order), and for alpha ≥ 1.0 some tested capability fires below 0.5.
- **Cliff absent:** otherwise.
- **The location** is reported per alpha against v2.0's cap\* sequence (5.0, 3.0, 2.5, 2.0, 2.0), as consistent, lower or higher, by the same interval rule, using a bootstrap over seeds.

Every reading is reported. None is a pass or a fail of v3.

## 10. Predictions, registered now and reported as right or wrong

- **P1:** survival is non-decreasing in rr across the R1 grid.
- **P2:** at each rr from 0.055 to 0.062, v3 survival is at least v2.0's published value, minus two of v3's standard errors.
  - **The basis**: D8 does not bind from the start, since the cohort bound from 200 entrants is 5.2e-7. It binds when a population becomes small, and then the survival-first rule takes the bound-minimizing action. Throughout, the welfare floor forbids the crowding-relief allocations that v2.0's objective permitted.
- **P3:** R2's cliff is present under Section 9's point rule. Citation additionally requires the full G2.2 gate, including the strict net decrease and bootstrap support, and G4.2.
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

### Amendment A1, 2026-09-28: table effort, validation domain and unavailable scores

**Status: approved by the operator, including the unpublished-bin rule,
2026-09-28. Effective for registered execution from the commit that adds it.**
At writing, the registered calibration and the first registered table
family had been read to diagnose a pre-dispatch refusal. No registered
rerun job had run, no registered rerun output existed, and no registered
rerun output had been read. This statement is supported by the returned
execution log and the operator's directive. Calibration and table output
are registered output; they are not being described as unread.

The first table family, from the instrument at 6448a720 and this design
at 96f2c481, remains a failed estimation attempt. Its published SHA256 is
`deef0f6a85c93bc281820424d51f370fa580871ae2e460d6535e5a4a390689fa`.
All 343 jobs completed, but 5,604 of 13,750 primary rows failed their own
screens. Sensitivity screening added 66 distinct failed rows, for 5,670
published `not_estimable` rows. The nine sensitivity pairs were complete.
The original family is retained unchanged and is not reclassified as
passing under this amendment.

The numerical thresholds are unchanged. The primary failures comprise
3,105 half-window drift failures and 3,099 continuation residual failures,
with overlap. All primary half-width, route, survival-fraction, continuation
coverage and solver screens passed. Among sensitivity rows, 187
doubled-population rows failed their own screens; all 735 doubled-length
rows passed. Forty-two primary-versus-doubled-length contrast intervals
failed. This supports increasing time before increasing particles.

Fixed non-registered probes at four times the original lengths removed
all tested drift and numerical-contrast failures, but four of 30 tested
rows still failed the unchanged continuation residual screen. These are
retained failures, not a successful validation of time-only changes.
The diagnostic output identifies sparse conditional bins, including a
published balanced-rule bin with 40 training and 13 held-out visits.
Two additional fixed probes at four times both length and population
still failed four of six scoring rows under the original validation
domain. A w3_p5_t1_g3/.055 residual of 17.514834 came from a bin with one
training visit and one held-out visit that is not in the exported table.
A balanced/.064 residual of 2.760795 against 2.527108 came from a published
bin with five training visits and two held-out visits. These findings do
not demonstrate that more effort alone solves continuation validation.

**Approved definition correction:** let B_pub be the bins with at
least four training visits, the existing publication criterion. The
exported continuation C is defined only on B_pub, plus exact extinction.
The residual (1-beta)u + beta C(b_next) - C(b) is evaluable from that
artifact only when b is in B_pub and b_next is in B_pub or is extinct.
Previously validation also used internal fitted values from bins omitted
by the writer and rejected by the online loader. It thus validated a
different function and overstated artifact coverage. Use the published
domain for both residuals and coverage. Keep the denominator as all
held-out transitions, the 90 percent coverage floor, the maximum absolute
conditional mean residual, and its five-percent flow-range limit. The
domain is determined from training counts before inspecting held-out
rewards. No low-count published bin is excluded, and no held-out minimum
count is introduced. Preserve the old all-training-bin residual and
coverage as labeled diagnostics. Missing online bins supply no value.
This does not assert a uniform Bellman bound or certify aggregation bias.

A reduced test shows why this is a domain correction: an unpublished
source bin previously counted as covered now lowers coverage from 1 to
5/6, which fails the same floor. A second test retains a published bin's
residual of 10 against a 0.5 limit. This amendment does not waive real
published-bin failures. The full replacement family under the corrected
domain has not been run and is not certified to pass.

**Approved unpublished-bin rule, 2026-09-28:** in each allocation
comparison, a rule whose rollout endpoint is outside its published
continuation domain has no valid score and is omitted. The same applies
to a missing Lambda_F row, although the registered table gate must
prevent a missing row at launch. An extinct endpoint retains its exact
extinction continuation; it does not need an estimated continuation bin.
There is never a midpoint, neighbor or other substituted value. Existing
admission and survival-first filters continue to apply. If the comparison
has no eligible rule with an available score, use the balanced rule,
which satisfies the welfare and pointwise reproduction floors. Record
whether all scores were unavailable or availability and admission jointly
emptied the comparison. This fallback is an action, not an imputed W.

Each step records `unavailable_rule_count`, the excluded rule identifiers
and reasons, and `balanced_fallback` with its reason. Unavailable objective
components are null in output. Rerun outputs aggregate the number of
rule exclusions, steps with an exclusion, exclusions by rule, the maximum
excluded at a step, and balanced-fallback steps, with the number of
allocation steps as denominator. Absorbed steps do not evaluate allocation
and count neither an exclusion nor a fallback. Allocation diagnostics
refer to the comparison before any yield review at that step.

Yield plans use the same availability principle separately. A complete
plan with an unavailable continuation or Lambda_F value is omitted before
comparison. It cannot become admissible through an invented value. If no
plan is admissible, hold yield. Reviews record total candidate plans,
unavailable plans, admissible plans and whether yield was held for lack
of an admissible plan. The per-step diagnostics and rerun totals include
these counts. The registered table gate and all numerical screens remain
binding; these online exclusions do not admit a failed table family.

Endpoint-frequency diagnostics replay fixed-rule paths from archived
estimator seeds and compare their 20-step endpoints with the published
domains. They are non-registered estimator diagnostics, not adaptive
rerun outcomes. Per-rule marginal frequencies cannot determine the
joint all-rules-unavailable probability. The implementation note reports
their settings, denominators and limits; registered outputs will report
the actual balanced-fallback frequency. No registered rerun output existed
or was read when this addition was written.

For the replacement family, the primary setting becomes six groups,
64 plain runs per group, 256 FV particles per group, burn-in 1,024 steps
and 2,048 measurement steps. Time and populations are each four times
the original settings. The population increase supports conditional-bin
continuation estimation; it is not a substitute for burn-in. The frozen
nine-pair subset is unchanged. Its doubled-population setting uses 128
plain runs and 512 FV particles
per group, with primary lengths. Its doubled-length setting uses burn-in
2,048 and 4,096 measurement steps, with primary populations. The plain
route still requires at least half the runs to survive the measurement
window; otherwise use FV. WE remains unavailable and an unestimable row
remains a failure. Every rule and context receives the primary setting.
No row, rule, rr, scoring context, seed count or rerun grid is dropped.

All 343 table jobs are regenerated as a new family, including the 325
primary jobs and 18 sensitivity jobs. Updated settings and code give new
job and artifact identities under the existing deterministic seed rule.
Do not mix completed rows from the first attempt into the replacement.
Selection still acts on W point estimates, and the floors, admission,
complete-plan yield comparison and objective are unchanged. Continuation
validation uses the domain correction above and adds the worst residual
bins and their sample counts to its diagnostics. Rejection thresholds do
not change; the old family's recorded failures are not relabeled.

The calibration remains frozen at SHA256
`bf0f7c3f10310558d567b6b3f7c24f6f99f2fe6eb71fd830cccfd8e2aa0bd6d6`.
No value is recalculated or refit. An explicit compatibility record binds
that exact artifact, its original source identity, its value hash and the
unchanged calibration-generating functions and dependencies. Dependency
comparison normalizes Git's CRLF/LF conversion and no other bytes. It permits
this calibration across estimator-only source changes, while refusing a
different artifact or a changed scientific dependency. New table rows
bind the new full source identity and the unchanged calibration hash.
The compatibility record itself is part of that source identity and must
be committed before registered execution.

At the measured 28-worker throughput, sixteen times the original table
work projects 10,975 seconds including the observed 94-second fixed
overhead, about 3.05 X2 hours. A work-unit scenario charging every job
five times more for migration from plain to plain-plus-FV projects
15.14 hours, leaving about 8.86 hours below the ceiling. These are measured-cost
extrapolations, not hard runtime bounds or evidence that all screens will
pass. They leave room under the unchanged 24-hour ceiling. The mandatory
configuration test is rerun for the replacement workload, and the runner
still enforces its deadline. The 680-second figure covered table dispatch;
the original service interval was 774 seconds.

The implementation note and `v3/table_screen_audit_20260928.json` record
the full rule/rr/scoring-context diagnosis, numerical excesses and fixed
non-registered diagnostic probes. Such probes are estimator validation,
not registered rerun outcomes. The replacement family must pass every
screen as specified above before any rerun dispatch. A remaining failure is reported
and keeps the gate closed; there is no retry-until-pass rule or automatic
relaxation. The operator has approved this amendment. Commit and push it
and the code, then supply the new committed pin before replacement estimation
or rerun execution. This amendment does not change any prediction or aim
at a v2.0 figure.

### Amendment A2, 2026-09-28: gates, evidence recording, D23 and D24

**Timing and scope.** A2's first part was written after the registered
calibration and the first table family had been read, and after the A1
tables started from instrument commit 34ffbfe9, before any registered rerun
manifest, job or output existed. D22 approved the evidence recording. The
rerun step was paused before dispatch for D22's evidence-schema gap. The D23
part was written after the A1 family completed and its screens were read:
717 rows were not_estimable, including 671 primary failures and 46
propagated through sensitivity. That family failed the registered table
check. No registered rerun manifest, job or output existed when this was
written. A2 is committed before any registered rerun output is read. Only
labeled non-registered validation outcomes were used in preparing the
checker. Seeds, grids, objective, floors, table screens and predictions are
unchanged.

D24 settled the censored-cap* case D21 left open after the A1 screens were
read and before any registered rerun manifest, job or output existed. The
censored ordering and testability rules below were fixed before any
registered rerun output was read. They make no part of the cliff test easier
to pass: the nonincrease, strict net decrease, 90-percent support and
two-standard-error separation requirements retain their thresholds. No
censored alpha is claimed to show measured separation outside the tested
grid.

D21 adopts the v3 gate revalidation. The complete public rules follow. G2.2
is the succession cliff gate. G2.1 and G2.4 remain with the phi study. The
standalone checker is `v3.gates`; the v2.0 validator is unchanged.

**Gate statements, evidence and pass rules.** Reference calculations are
independent of reported pass flags. Before checks exercise the committed
instrument and frozen calibration on checker-chosen scenarios. After checks
use paths and verified hashes for the registered calibration, tables,
complete run manifest, outputs and durable completion records. Each run's
fire outcome is derived from increases in its executed capability path and
checked against the recorded reviews.

| Gate | Statement and pass rule | Evidence and timing | Governs |
|---|---|---|---|
| G1.1 | Flow marginals equal weight/(observable + calibrated epsilon), are positive, and decrease over the fixed interior points. | Instrument and calibration, before | R1, R2 |
| G1.2 | L = D_gen times nu times Psi times Theta, lies in [0,1], and vanishes exactly when a factor vanishes, without a positive floor. | Instrument, before | R1, R2 |
| G1.3 | Theta matches the clipped-bandwidth formula, tends to one at zero frontier, and at maximum frontier and minimum bandwidth is at most epsilon_L. | Scalar and vector paths and calibration, before | R2 |
| G1.4 | rho = 0.01, discounting is normalized from the first post-action reward, and continuation and elapsed suffix values retain committed epoch units. | Instrument, before | R1, R2 |
| G1.5 | Flow stays within its declared bounds, living flow is at least u_dagger, and extinction is absorbing. | Instrument, before | R1, R2 |
| G2.2 | cap* is nonincreasing in alpha, with a strict net decrease from 0.5 to 1.5. Each adjacent strict decrease has at least 90 percent seed-bootstrap support. | Full registered R2 family, after | R2 cliff |
| G3.1 | Best immediate disrupted W strictly exceeds best waiting W exactly when yield fires. Ties hold. All fixed scenarios and all 200 sampled reviews match. | Instrument before; complete-plan evidence after | R1, R2 |
| G3.2 | Applied transition drawdown matches the independent formula and original rounding draw. Reported Gamma equals undisrupted minus disrupted complete-plan W. The offered comparison value equals disrupted W and undisrupted W minus reported Gamma, with no second subtraction. Zero mismatches; at least one checkable review. | Checkable R2 reviews within the common sample, after | R2 |
| G3.3 | Every fired R2 succession increases generation depth above one and capability by a ratio above one, stays at or below 5.0, and records knowledge transfer. Zero violations. With zero fires in the complete family, report not_testable, not pass. | All fired R2 successions, after | R2, with the D23 zero-fire exception below |
| G4.1 | Theta matches the independent formula on 10,000 hash-selected living-start R2 steps and every absorbed-start R2 step. Zero violations. | Raw frontier, bandwidth and transfer inputs, after | R2 |
| G4.2 | For every testable alpha, the next tested capability above cap* has fire rate at most 0.5 and at least two standard errors below the rate at cap*. At least one alpha must be testable. Censored alphas and reasons are reported. | Full registered R2 family, after | R2 cliff |
| G4.3 | Every period's exact recomputed cohort bound and reservation agree. Every living-start step has an independently checked active bound and survival-first flag. When survival-first is required, its action minimizes the first-action cohort bound. No unsupported floor override. | All period-start and living-step cohorts and in-scope actions, after | R1, R2 |

G2.1 and G2.4 are not applicable because they belong to the phi study. G2.3
is not applicable because the D12/W2 deviation-set game belongs to W3 and is
absent here. G5.1 and G5.2 await P4 and are not applicable. Evidence cannot
change applicability. Missing, duplicate, skipped or unimplemented checks
fail aggregation. Cleared through k requires every applicable check through
gate number k, including both parts of G3.1, to pass. R1, R2 and R2_cliff
citation flags have the dependencies listed in section 7.

Under D23, zero fired R2 successions in the complete verified family makes
G3.3 not_testable with zero fires, zero checked, a stated reason and no
zero-failure bound. It is not a pass or clearance through gate 3. This
specific state does not block R2 fire-rate citation when all other R2 checks
pass. It grants no R2_cliff exception. Missing R2 evidence, duplicate checks
and any failing fired succession remain blocking. G2.2 and G4.2 retain their
full requirements.

**Frozen sampling.** Review identity is `[job.id, job.seed, review.time]`;
step identity is `[job.id, job.seed, diagnostic.time]`. Sort by SHA256 of
canonical JSON `["D21-A2-2026-09-28", kind, identity]`, then by canonical
identity for hash ties, with kind `review` or `step`. Reviews target 100
fired and 100 not fired across R1, refinement and R2. If a stratum has fewer
than 100, take all and fill from the next hashes of the other stratum. Fewer
than 200 total fails.

G3.2 uses the R2 members of that same sample. Its n counts only reviews with
at least one admitted, available yielding plan whose disrupted and
undisrupted continuations and Lambda_F values both exist. Holds without a
paired yielding comparison do not count. Report reviews considered, reviews
without a comparison, and paired plan count. Zero checkable reviews fails
for insufficient evidence. Null values are never replaced. A malformed
record or a mismatch in a checkable comparison fails.

G4.1 samples the smallest 10,000 hashes among R2 steps with pre-step
population above zero, retaining the last-death step. It separately checks
every absorbed-start R2 step and reports both counts. Fewer than 10,000
living-start steps fails. Missing pre-step population or selected raw
evidence fails; no case is silently removed for missing evidence. An
absorbed-start step must remain empty and have the extinction Theta value
one, consistent with its raw zero-frontier formula inputs.

**Cliff tests.** G2.2 uses alpha (0.5, 0.75, 1.0, 1.25, 1.5), capabilities
(1.2, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0), and rr (0.057, 0.060, 0.064, 0.070). At
each alpha/capability pool run fire outcomes over rr; cap* is the largest
capability whose pooled fire rate is at least 0.5. Use 2,000 NumPy
default_rng bootstrap resamples, seed 20260928. Independently resample whole
seed outcomes within each rr/alpha/capability cell, preserving its 75-run
count, then pool and recompute cap*. A cap* at 5.0 is top-censored, "5.0 or
higher". If no tested capability reaches 0.5, cap* is bottom-censored,
"below 1.2". Bottom-censored is below every tested value; top-censored is
above every uncensored tested value. Two top-censored or two bottom-censored
values are flat. This same order defines nonincrease, the strict net
decrease cap*(1.5) < cap*(0.5), and every bootstrap comparison. Censored
resamples are never dropped. Each adjacent strict point decrease needs
support at least 0.90. Support is the share of all 2,000 resamples in which
that pair strictly decreases. Flat pairs need no support test. An increase,
absent strict net decrease or unsupported decrease fails. Report the
censored labels and counts among all 2,000 resamples. Reduced fixtures
cannot clear results.

G4.2 uses p and q at cap* and the next higher capability. Its standard error
is sqrt(p(1-p)/n + q(1-q)/m), where n and m are pooled run counts, each 4 rr
times 75 = 300, not 75 seed counts. Require q <= 0.5 and p-q >= 2 SE.
Equality passes at the two-standard-error separation limit. Although the q
threshold is inclusive, q = 0.5 cannot occur for a correctly computed
interior cap*: that next capability would itself qualify. An alpha is
testable only when cap* is a tested value below 5.0. For top censoring there
is no tested capability above cap*; for bottom censoring there is no tested
cap* at which to measure separation. Report each such alpha as not_testable
with its reason. G4.2 passes exactly when every testable alpha passes and at
least one alpha is testable. No testable alpha means failure, not a pass.

**Independent arithmetic and ties.** Equality checks use absolute tolerance
1e-10 and relative tolerance 1e-8. G3.1 first verifies every reported
comparison value against the independent exp(-rho*t)/fsum calculation. It
then applies the strict yield rule to the reported values produced with
beta**t, where beta = exp(-rho). A recomputed immediate/waiting gap larger
than max(1e-10, 1e-8 times the larger absolute value) must have the same
order. Within that tolerance, arithmetic roundoff must not turn a reported
tie into a fire or reverse a reported strict near tie. A value discrepancy
outside tolerance still fails.

For G3.2, the recorder supplies Gamma per available paired yielding plan in
committed epoch units. The checker independently values the two raw plans,
checks the reported Gamma, and compares the actual offered W with both
disrupted W and undisrupted W minus that reported Gamma. Gamma is not
redefined from the offered W. Subtracting it twice therefore fails even if
the yield flag stays unchanged. The successor plan itself contains the
simulated disruption; the executor subtracts no extra cost. For each
yielding plan and actual fired transition, record the integer stock values
before and after, the applied drawdown, capability gap, action and original
environmental rounding draw. Independently compute load = 0.10 + 0.05 gap +
0.03 + 0.05(1 - transfer allocation) and buffer = 0.5 institutional stock +
0.3 transfer allocation + 0.2 governance allocation. The institutional
decrement before rounding is load(1 - buffer), clipped at zero stock. Apply
the recorded draw to the 0.01 grid and require the exact resulting stock and
decrement; other stocks must be unchanged. Omitting disruption fails even if
the paired flows coincide and reported Gamma is zero. This records an
existing draw and makes no new executor draw.

G1.1 uses central differences with h = 1e-4 times the varied coordinate,
relative derivative tolerance 1e-5, coordinates (0.001, 0.01, 0.1, 0.5), and
other observables fixed at 0.3. G1.2 tests the Cartesian product of (0,
1e-12, 0.25, 1) for all four lineage factors. G1.3 tests frontier (0, 1e-12,
0.25, 5), bandwidth (0, calibrated clip, 1), transfer (0, 0.5, 1), and all
five alphas, plus the maximum-frontier bound. Vector checks use frontier and
transfer stocks (0, 50, 100), welfare (0, 500, 1000), and all alphas. G1.4
tests horizons (0, 1, 20, 25), reward levels (-10, 0, 3), constant flows and
elapsed epoch times (0, 10, 20). G1.5 checks observable boundary/interior
products and five absorbed steps. G3.1 scenarios use immediate/hold/later
values (3,1,2), (1,3,2), (2,2,2), (3,1,4), and (-1,-2,-3).

A zero-failure sample pass reports n and 1 - 0.05^(1/n), the nominal 95
percent bound. Chosen scenarios, stratification and dependent steps within
runs do not support an unrestricted independent-trial population claim. G2.2
reports bootstrap support and G4.2 reports separation rather than this
bound. A not_testable check has no zero-failure bound.

**D22 evidence recording.** The A1 rerun output schema lacked evidence for
G3.1's sample, G3.2, G3.3, G4.1 and the action part of G4.3. This was a
source-schema finding; no A1 rerun output existed. D22's end-to-end check
used six non-registered 500-step jobs through the real runner and its
durable evidence index, exposing the D23 survival-first defect. The runner
now uses `RecordedV3Model` and records schema `v3-gate-evidence-1`. Each
review records its epoch, every candidate including unavailable and
unadmitted plans, actual comparison values, and paired undisrupted yielding
flows even when the disrupted endpoint is unavailable. Unavailable
continuation, Lambda_F or Gamma values are null. Fired reviews record
generation and capability changes and the executed transfer_comprehension
share as the declared knowledge-transfer observable.

Every step records pre-step population and raw frontier, bandwidth, transfer
stock and Theta. Every period start records all living agents' ages and
integer welfare, admitted or not. Every living-start step records those
pre-action arrays, summary bins, all rule IDs and the executed action,
including steps in admitted periods. An above-bound period means its
period-start cohort bound exceeds epsilon. The candidate IDs must equal the
frozen 25-rule class in declared order. The checker reconstructs the
complete feedback action class from the recorded summary bins. Missing bins
fail registered checking; synthetic fixtures alone may use the declared
fixture mapping.

G4.3 independently recomputes each 50-step cohort bound as the exact product
of agent death upper bounds using the directed integer life-table
recurrence. It verifies the displayed outward-rounded float and uses the
exact fraction to decide admission and reservation at epsilon=1/1000. The
reserved fraction must equal that exact bound if admitted, else zero;
reserved plus unallocated equals epsilon and statistical alpha spent is
zero. An exact epsilon tie is admitted even if its outward-rounded float is
slightly larger. At every living-start step the checker independently
recomputes the remaining-window active bound and checks the survival-first
flag. It examines each required minimum-bound action, including last deaths
and survival-first within an admitted period. An admitted period can switch
to survival-first when its active bound exceeds epsilon at a later step.
Missing evidence fails. Post-extinction period starts are reported
separately and excluded from the survival-first period share. That share is
above-bound living-start periods divided by all living-start periods.
Unsupported floor overrides fail. Universal living-step cohort recording removes the previous dependence
on the executor's flag inside admitted periods. In six 500-step validation
jobs, the additional fields covered 100 admitted, non-survival-first steps
and added 71,704 compressed bytes, about 12 KB per job. Recording all living
steps is retained; the small validation mix is not a family storage forecast.

Evidence is canonical JSON compressed with deterministic gzip and base64
inside each result, with raw byte count and SHA256. Existing durable
completion hashes cover the whole output; partial files never count as
complete. No unhashed sidecar is accepted. The observer is designed not to
alter computed values, decisions or random draws. It reads original results
after computation; undisrupted replays use copied state and private channel
generators, with transition drawdown alone suppressed. In six paired
500-step jobs, with no natural fires, and one stress fixture, scientific
results, with evidence removed, and random draws were identical with
recording on and off on the same D23 executor. Only six of 300 non-fixture
validation reviews had eligible undisrupted comparisons; three of the 73
sampled R2 reviews supplied G3.2's 150 paired plans. In validation, G3.2 had
three checkable reviews (nominal bound 0.63). Implementation-note section 22
records the D24 validation identity
6c87072644b26ff8a545144771f91a4dbe598623dce7c0586a5390dbda331942; sections
19 and 21 retain the diagnosis and earlier validation as history. Section 23
records the final second-review identity and validation. These are
non-registered sparse probes and fixtures, not registered rerun evidence.

**D23 correction of A1.** Satisfying the floors is not sufficient under
survival-first. At 34ffbfe9, falling back to balanced when every
minimum-bound rule lacked a W score violated the lowest-bound requirement in
58 validation periods. D23 corrects allocation to select only rules
attaining the lowest per-rule first-action cohort bound. Available W scores
break ties as before. If none of those rules has a score, choose balanced
when it is among the minima, otherwise the first minimum in declared rule
order. Admitted allocation outside survival-first retains A1's balanced
fallback. Yield review, cohort bounds and both floors are unchanged.

The new case is recorded as `survival_first_scores_unavailable`, with total
unavailable-rule count and unavailable-minimum-rule count, in both step
diagnostics and override records. It is not `balanced_fallback`, even if
balanced is a minimum. No reproduction floor is overridden. A per-job count
is published. The separate historical comparison checks that any first
scientific difference from 34ffbfe9 occurs at precisely this condition on
the same pre-action state. Recording non-interference uses the same amended
executor on both sides.

**Exact compatibility and committed identity.** The source-controlled
`simulation/v3/table_compatibility_A2.json` pins the A1 producer,
calibration, design, unchanged dependencies and approved recording/loading
and D23 boundaries. It accepts only the genuine A1 publication with seal
`f6fcb1fdd787e92164f029e8fd0098a71d94c47b5ee3b37b96adb91a63a8cfd7` and file
SHA256 `56db71633a0f4710692e3354e3bc2fb5829286abbfa59e61609bd3f8cf6fcb3c`. A
changed or re-stamped artifact cannot use this exception. That genuine
family fails the registered table check (717 not_estimable rows, 671 primary
and 46 via sensitivity), so the exception currently admits no table to a
registered run. Any repaired family requires its own reviewed record. No
table screen is relaxed. The runner checks every file in its code identity,
including non-Python compatibility records, for committed and clean status.
Validation helpers can print proposed boundary hashes but cannot rewrite
approvals.

**Index and report.** `python -B -m v3.gates index RUN_ROOT` builds a
hash-verified evidence index from the frozen manifest and completed records.
Registered indexing and after-checking require the committed A2 pin before
opening rerun outputs. The loader verifies all 24,900 jobs, stable seeds,
exact source identity, complete step and scheduled review records, and file
and compressed-evidence hashes. Explicit fixture and validation modes remain
uncitable and retain the gate thresholds. `python -B -m v3.gates` writes
`v3_rerun_gates.json` and `.md` under `simulation/v3/runs/`; diagnostics
copies belong to the results commit. The 72-hour rerun ceiling, 24-hour
table ceiling and configuration test remain unchanged. The final validation
report states passes, insufficient samples and unresolved gates separately;
no reduced validation sample can clear a registered result.

### Amendment A3, adopted 2026-09-28: one fixed A1 table repair

**Timing and status.** D24 adopted A3 after the registered A1 table family
completed from 34ffbfe9 and its failed screens were read. This amendment was
written before any registered rerun manifest, job or output existed. No
registered rerun output was read. The rerun step was paused before dispatch.
Execution requires the committed pin that includes A2 and A3. A3 fixes the
67-job selection and eight-times-A1 populations, with the dispatch order and
early stop below.

**Evidence and reason.** The A1 publication's full file SHA256 is
`56db71633a0f4710692e3354e3bc2fb5829286abbfa59e61609bd3f8cf6fcb3c`. All 343
job/output/completion identities and hashes were checked. Of 13,750 primary
rows, 671 fail only the continuation residual screen. Another 46 published
rows fail because their selected sensitivity estimates fail that same
screen: six doubled-population contexts for balanced/.055, and 40
doubled-length contexts for w0_p0_t1_g3/.064. There are no missing
sensitivity jobs and no numerical Lambda_F contrast failures. All flow
half-width, half-window, route, applicable plain survival fraction,
continuation coverage and fixed-point convergence checks pass.

The bins with the largest residuals have only 1 to 23 held-out visits. The
statistic is the maximum absolute conditional mean Bellman residual on the
published domain, not a mean weighted by overall occupancy. Its A1
definition evaluates precisely the domain available to the executor. These
are real failures of that definition. A3 does not remove sparse bins, change
bin cuts, change the four-training-visit publication rule, introduce a
held-out count exclusion, relax the five-percent residual limit, reduce the
90-percent coverage requirement or suppress a failure. Additional
measurement time alone need not revisit a transient rare bin. The evidence
supports increasing independent trajectory populations; it does not
establish that sampling error is the only cause or that the repair will
pass. Aggregation bias remains uncertified.

**Frozen repair selection.** A1's primary settings were applied to every row
in the completed family. Add one independent repair stage on the union of:
(1) every rule/rr pair with any failed primary or sensitivity estimate in
that frozen A1 family, and (2) the entire original three-rule by three-rr
sensitivity subset. Select whole jobs and all their scoring contexts, not
individual failing alpha, capability or weight rows. The resulting 49 pairs
require 49 primary jobs and all 18 sensitivity jobs, 67 total. The remaining
276 primary jobs are retained exactly from A1. The repair replaces 1,690
primary rows, including passing contexts in those jobs, and renews all 735
selected contexts at both sensitivity settings. The full published family
still has 13,750 rows and all 25 rules.

For every selected job multiply plain runs and FV particles by eight
relative to its A1 setting. Keep six independent groups and all lengths. The
repair primary uses 512 plain runs or 2,048 FV particles per group, burn
1,024 and measurement 2,048. Doubled population uses 1,024 plain runs or
4,096 FV particles per group. Doubled length uses primary populations, burn
2,048 and measurement 4,096. Plain-versus-FV routing and all original
per-row screens stay unchanged. The sensitivity subset and its two contrasts
stay unchanged. Every new primary, including a passing original, replaces
the whole original row. Every new sensitivity estimate replaces its
original. Failure is not a reason to retain the old value.

This explicitly amends A1's uniform whole-family replacement rule to a
mixed-effort family with a frozen, recorded repair selection. It does not
assert that such mixing was authorized by the unamended A1 text. D18's
offline, finite, frozen evaluation and R13's original primary coverage,
routes and nine-pair sensitivity design remain in place. The additional
schedule, provenance and selection are part of this amendment.

The committed `simulation/v3/table_compatibility_A3.json` pins all 67
replacement job IDs and seeds, including the original job ID and
`A3-fixed-once-20260928`. It pins the exact calibration argument
`v3/runs/registered/v3_rerun_calibration.json`, relative to `simulation/`;
equivalent path spellings are refused. Preparation, validation and
publication require those identities. Scheduling and new results cannot
change them. There is exactly one new estimate per selected job, with no
best-of selection, pooling with a failed fit, retry-until-pass or adaptive
further effort. All new estimates, including failures, remain durable
records. Selecting effort after a failure and retaining original passing
rows can induce selection bias and conditional publication effects.
Independent replacement data avoids reusing the failed held-out sample for
the new fit; it does not give selective, simultaneous or aggregation-bias
coverage. The existing empirical intervals acquire no new confidence claim.
The unspent admission alpha ledger is unrelated and remains unspent.

Every existing screen is unchanged. A3 adds one stricter original-versus-
replacement Lambda_F contrast using the existing 5-percent-of-span rule,
which also triggers the stop. Every replaced scoring row, primary and
sensitivity, compares its new Lambda_F with its original using exactly the
existing numerical contrast rule: the absolute mean difference plus the
90-percent contrast half-width must not exceed five percent of the flow
range. This is additional to the original per-row screens and the fresh
nine-pair doubled-population and doubled-length comparisons. A failed added
screen makes the replacement not_estimable. A remaining failure anywhere
keeps registered dispatch closed. There is no fallback to treating a failed
stability screen as an unpublished bin.

**Provenance and execution.** `v3.table_repair_a3` prepares a sealed
manifest without executing it. The production runner performs its
configuration test, service lease, durable completion, source/pin checks and
deadline handling. Publication is a separate explicit command. It verifies
the pinned A1 publication, original manifest and all original completion
hashes; verifies every fresh job, configuration, seed and completion; and
rebuilds the full family. Retained values identify their A1 producer. They
are never relabeled as fresh worker outputs. Ranking flags are recomputed
from the assembled family, as in the existing writer; this changes no
retained estimate or screen. The new publication binds its full producing
code identity and both provenances, the fixed selection, settings and source
hashes. It passes through the registered table loader with its unchanged
scientific checks. The exact frozen calibration is reused through its
existing compatibility record. A3 itself changes no allocation or yield
computation. A2's exact failed-A1 exception remains separate from the A3
record.

**Cost and deadline.** A1 took 20,164.934 dispatch seconds with 24 workers,
440,710.415 summed worker seconds, or 21.855 effective workers. The 67
selected jobs used 84,683.871 worker seconds. Eight times that measured work
projects 8.611 additional wall hours at the same effective throughput.
Including about 21,173 seconds (21,172.095 measured) of prior service time
for both families and 1,200 seconds for configuration and
cleanup/publication gives 14.825 cumulative hours. At half that throughput
the total is 23.436 hours. These are planning extrapolations, not timing
measurements at the new populations or promises of statistical clearance.
Memory pressure, route changes and rescoring cost can exceed the scaling
assumption. The new runner receives at most 65,227 wall seconds, charging
prior service time against the unchanged cumulative 24-hour ceiling. Its
existing deadline reserves cleanup and prevents indefinite retry or
resumption. The measured configuration test must project the remaining work
plus the 1,200-second reserve within the remaining deadline. Initially this
requires at least 10.581 effective workers under the stated eight-times
worker-cost extrapolation. If it cannot, stop and report the gap. The wall
deadline still binds if that extrapolation proves optimistic. No seeds,
grids or screens are cut.

**D24 dispatch order and early stop.** Order the 67 jobs by their A1 maximum
normalized screen excess, descending, then by ascending original job ID. For
upper limits this is (value - limit)/limit; for lower limits it is (limit -
value)/limit. Take the maximum over all scoring contexts and applicable
numerical screens, including each sensitivity contrast for both jobs of its
pair. The plain route requires at least half the independent runs to survive
through its measurement window; this is the survival-fraction route screen
in A1 and A3. FV's pre-cloning survivor fraction is not subject to that
screen. These signed quantities, the source hashes and the full order are
frozen in `simulation/v3/table_compatibility_A3.json` and the manifest.
Ordering is operational: no job configuration, seed, estimator or screen
order changes. The first job in the order has maximum normalized excess
3.8274280261, from a continuation residual.

The manifest requires the runner's `A3-first-failure` completion screen.
After each durable completion, before replacing any worker, inspect all of
that job's row screens and its original-versus-replacement contrasts. When a
primary and either sensitivity job are both complete, inspect their full
context-matched contrast. Any single failure stops dispatch and interrupts
remaining jobs through the runner's supported procedure. Record the failing
job, context, screen or contrast, paired job when relevant, and reason in an
atomic failure record and durable event log. Completed outputs remain
intact. In-flight outputs remain partial unless their completion records
were already published. The failure is latched across resume and run roots
at the fixed path
`simulation/v3/runs/A3_families/<policy-digest>/failure.json`. Both launch
and publication refuse a latched family. Before configuration testing or
service shutdown, scan completed jobs across the recorded family roots and
latch any failed row or completed sensitivity pair. Configuration-test jobs
remain discarded and do not trigger scientific screen stops. A failed repair
cannot publish a registered table. This avoids spending more compute after
the family has already failed; it does not waive or reorder any screen.

**Explicit mixed-family compatibility.** The committed A3 policy pins the
genuine A1 file and seal, its producer 34ffbfe9, all 343 source completion
hashes, the exact 67 replacement source jobs and their scientific
configurations. The other 276 jobs retain that producer and provenance. The
67 fresh jobs use the committed A2+A3 producer, independently identified by
full code hash and commit. The publisher verifies both durable families and
every unchanged scientific screen before publishing. It writes a sealed
publication-specific `.compatibility.json` receipt beside the new table,
binding its exact file hash and seal, the manifest, 276 retained hashes, 67
fresh job identities and output hashes, and both producers. Both files must
travel together. The loader requires the producing commit to be an ancestor
of HEAD, with exact current code_identity equality, so later documentation
or results commits preserve compatibility. It requires this receipt even
when the table's code hash matches its own. A missing or changed receipt,
re-stamped table, wrong retained job, changed seed, settings, order or
producer is refused. No future table hash is guessed in advance. The genuine
A1 publication still fails its registered table check (717 not_estimable
rows, 671 primary and 46 via sensitivity) and cannot substitute for this
repaired family.

The diagnosis and alternatives remain in implementation-note section 19 and
`simulation/v3/A1_TABLE_DIAGNOSIS_20260928.json`. Section 22 records the D24
validation; section 23 records the second-review validation and its final
source identity. No repair estimate or registered rerun was executed in
preparing these amendments.


The final second-review code identity is
`f03021f88c53e0331d6d825f26663980f77a98d1e15c258f386acfc2c1f7b629`.
The final validation record is
`simulation/v3/runs/second_review_validation/validation.json`, SHA256
`0fed15f63bb936cd5289f875e4f3fe41894181473d63ff27210e516a58edf9ae`.
Its full evidence archive is
`simulation/v3/runs/second_review_validation/second_review_validation_records_20260928.zip`,
SHA256 `26eb3625255b17d3c0874a0219a139edd95168b511b8e130b7370145b010ac18`.
Implementation-note section 23 states the final checks and limits;
section 22's identity and sections 19 and 21 remain historical records.

### Amendment A4, adopted 2026-09-29: validated continuation support

**Timing and status.** The operator approved A4 on 2026-09-29 (D30), after
blind double certification of its design by two independent reviewers from
different model families. It is effective for registered execution from the
commit that adds it.

It was written after the registered A1 table family and its failed screens
had been read, as for A3. It was also written after non-registered planning
studies had read A1 job configurations and fitted values, and had simulated
those jobs on fresh planning seeds. No planning figure enters any registered
result.

No registered rerun manifest, job or output existed, and none was read.

A3 was adopted but never executed. A non-registered probe of its eight
hardest jobs, at eight times A1's populations, still failed two of them. One
failed 14 of 15 rows, with its worst row at 5.751 against a limit of 4.906.
A4 supersedes A3. The A3 repair stage will not run, and
`simulation/v3/table_compatibility_A3.json` is not used.

**Evidence and reason.** A1's continuation residual statistic is the
maximum, over published bins, of a point estimate of the mean Bellman
residual. Each estimate comes from two held-out groups: 128 plain
trajectories, or two Fleming-Viot (FV) groups. In sparsely visited bins that
maximum is dominated by sampling noise, and more effort did not reliably
clear it.

In a non-registered planning study of 24 A1 jobs, each given 32 fresh
independent groups, no bin showed a violation under any interval method
tried. No plain bin's point estimate exceeded the limit. Only 33 of 35,320
FV bins did, and those held a negligible share of visits.

A second planning study found a defect in the committed fit. The plain trace
keeps recording a path after extinction, so `fit_transitions` counts extinct
states as sources in population-category-0 bins, where the registered engine
never uses a continuation value. On living sources, A1's population-0 values
showed mean residuals up to 6.7 times the limit. A4 corrects this for the
plain route. FV sources are resampled living particles, so FV fits are
unaffected.

A4 replaces the point-estimate maximum with interval tests on fresh data,
and publishes only the cells that pass them.

**The rule.** In every row, primary and sensitivity, the condition
`bellman_residual_empirical <= 0.05 span` is replaced by two conditions: the
row's validated support is nonempty, and the row passes the availability
floor below.

Every other screen and threshold is unchanged: flow half-width, half-window
drift, the route screen, held-out coverage, fixed-point convergence, the
sensitivity contrasts, and the Bonferroni allocation over 13,750 primary
rows.

A row's published continuation entries become its validated support. Every
other cell is unpublished, so its scores are unavailable under A1's
unpublished-bin rule. The tolerance stays `tau = 0.05 W`, where W is the
row's flow range.

For a transition from a living source state in cell b, the residual is `(1 -
beta) f + beta V(next) - C(b)`:
- `beta = exp(-0.01)`, and f is the row's scored flow.
- `V(next)` is the published value of the next state's cell, or the
  extinction flow `lower` if the next state is extinct.
- Any other transition is not covered.

**Validation data.** Seeds are SHA-256 digests of a stream tag, the A1 job
seed and a replicate index, truncated to 60 bits. The tags are `v3_R_fit`,
`v3_R_validate` and `v3_R_census`. The run asserts that these seeds are
pairwise distinct, and distinct from every A1, probe and planning seed. A
collision halts it.

Each plain table gets one fitting replicate and three validation replicates.
Each FV table gets one validation replicate. Every replicate has 32 groups
and otherwise the job's own A1 settings. A primary plain replicate therefore
has 64 runs per group, 2,048 independent trajectories, and a primary FV
replicate has 256 particles per group. Sensitivity jobs keep their doubled
population or doubled length.

Nothing from the validation replicates enters a fitted value, a width or a
family count.

**Plain tier, certified.** In each plain row, all population-category-0 bins
form one cell. Its value C0 is the Bellman fixed point on the fitting
replicate's covered living-source transitions:

`C0 = sum[(1 - beta) f + beta V(next)] / N`

`V(next)` is C0 inside the cell, the A1 value in a published cell, and
`lower` at extinction. Transitions into unpublished cells are excluded. The
unique solution is `C0 = a / (N - beta T)`, where T counts transitions that
stay in the cell. C0 is published only with at least four fitting visits,
the committed minimum. Every other plain cell keeps its A1 value.

The unit is a validation trajectory with at least one covered living-source
visit to the cell. `m_i` is that trajectory's mean residual in the cell. The
tested quantity is `theta_b = E[m_i | N_i >= 1]`.

The width `w = (1 - beta) W + beta (vmax - lower)` is computed from the
fitted table before the validation replicates exist. Here `vmax` is the
row's largest published value, including C0. It bounds every `m_i`, provided
every flow and every published value lies in `[lower, upper]`. That is
checked, and any failure halts the run.

The test is Maurer and Pontil's empirical Bernstein bound, two-sided:

`rho = sqrt(2 V_n ln(4M/alpha) / n) + 7 w ln(4M/alpha) / (3 (n - 1))`

- `V_n` is the unbiased sample variance of the `m_i`, and n is the number of
  units.
- **Certified:** `[mbar - rho, mbar + rho]` lies within `[-tau, tau]`.
- **Violation:** the interval is disjoint from `[-tau, tau]`.
- **Unresolved:** anything else, or `n < 2`.

M is fixed before any new data exist: for every plain row, primary and
sensitivity, the A1 published cells with population category above 0, plus
one. `alpha = 0.05`.

A certified cell is published only if its visit-weighted point estimate `sum
S / sum N`, from the same validation data, is also within `[-tau, tau]`.
Neighboring cells are retested against C0 in the same run.

The statement is: with probability at least 0.95, every published plain cell
has `|theta_b| <= tau`, simultaneously. It concerns the plain route only.

**FV tier, asymptotic and not certified.** The units are the 32 groups,
because particles within a group are dependent through resampling. Over
groups with `N_g >= 1`:
- **Estimate:** `mu = sum S_g / sum N_g`.
- **Variance (delta method):** `sum (S_g - mu N_g)^2 / (n (n - 1) Nbar^2)`,
  with `Nbar = sum N_g / n`.
- **Interval:** `mu` plus or minus `t` times the standard deviation, where
  `t` is the Student t quantile with `n - 1` degrees of freedom at `1 -
  alpha / (2 M_FV)`. `M_FV` is the number of A1 published FV cells.

A cell passes only if this interval lies within `[-tau, tau]`, and so does
the Fieller interval at the same quantile. Cells with fewer than 16
contributing groups, or an unbounded Fieller set, are unresolved.

FV rows carry the label "asymptotic, not certified" in every result that
uses them, and in the claims register.

**Availability floor.** For each table, the census follows the committed
law, `v3.unpublished_bins.endpoint_counts`: held-out plain paths from the
archived initial law, and 20-step endpoints over 500 start steps, on the
census seed. It is measured among living endpoints only, and it adds the
fraction among low-population living endpoints, those whose endpoint has
population category 0.

A row with no living endpoints in its census has nothing to look up. It
passes, and is reported as not assessed. Otherwise, a row passes if at most
2 percent of its living endpoints fall outside its validated support, and at
most 5 percent of its low-population living endpoints do when it has at
least 50 of them. Below 50, the low-population fraction is reported but not
assessed.

A row that fails is not_estimable. The registered loader rejects any family
with a not_estimable row, so registered dispatch stays closed and the
failure is reported.

Unavailable scores inside a rerun follow the committed rules in
`v3.integration`: the rule is left out of that comparison, with the balanced
fallback when no scoreable rule remains. The floor bounds how often that
happens.

**Publication.** A4 publishes a new table family.
- Retained A1 values keep their A1 producer identity.
- C0 is stored once per plain row. Its error is the committed bounded-domain
  enclosure, `max(C0 - lower, upper - C0)`.
- The table lookup resolves any population-category-0 key of that row to C0,
  and the registered loader accepts a plain row whose validated support is
  C0 alone. These are the only changes to the loader and lookup. For FV
  rows, and for every other key, the lookup is unchanged.
- The production runner gains the A4 fitting, validation and census job
  kinds, and runs them in phases. Its other job kinds are unchanged.
- A4 re-pins the approved boundary hashes of `v3/production_runner.py` and
  `v3/production_tables.py` in `simulation/v3/table_compatibility_A2.json`.
  The record keeps the previous hashes in an `a4` note, and the loader still
  refuses any unapproved change.
- The A1 publication and the failed A1 family stay on record, unchanged.

The publisher verifies the pinned A1 publication, every fitting, validation
and census completion, and every unchanged screen. It then writes a sealed
compatibility receipt binding the new table's hash, both producers, the
seeds, M and `M_FV`, as A3 specified for its family.

**What A4 does not establish.** The certificate bounds `theta_b`, the
per-trajectory mean. The visit-weighted mean is only checked, not certified.
Aggregation bias within a cell remains uncovered.

The validation law, living paths under the table's own fixed rule and
kernel, can differ from the states a rerun's allocations visit. The census
law is the committed proxy for that difference. FV cells have no
certificate.

**Execution and cost.**
- **Stages:** the plain fitting stage, then validation (plain and FV), then
  the census, then publication.
- **Compute (planning estimates, not measurements):** about 79 core-hours
  for the plain tables (about 5 hours on 16 workers), and about 257
  core-hours for the FV tables (about 26 hours at the roughly 10 workers
  that 9.5 GB per task allows).
- **Runner:** the production runner's configuration test, durable completion
  records, resume, and mode control apply. The model server is down for the
  whole run.
- **Ceiling:** a cumulative 48-hour wall ceiling. If the configuration test
  projects past it, the run stops and reports the gap.

The run halts on:
- a flow or value outside `[lower, upper]`;
- a seed collision;
- an A1 source-hash mismatch;
- nondeterminism in a re-executed sample task.

**Reporting.** For each tier, the report gives the counts of certified,
unresolved and violating cells, and their shares of visits. It also gives
the plain cells that fail the visit-weighted safeguard, every violation as a
finding, and each row's floor results. It reports no survival, extinction or
fire rate.

### Amendment A5, 2026-09-29: plain-law certification labels for FV tables

**Timing and status.** The operator approved the A5 design on 2026-09-29
(D31), after blind double certification by two independent reviewers from
different model families. This text is registered by the commit that adds
it. A5 is effective for registered execution from the later commit that adds
its implementation (see Sequencing).

It was written while the registered A4 run was in progress. That run's
progress counts, launch records and memory use had been read, but none of
its stage outputs. No A4 publication, rerun manifest, rerun job or rerun
output existed, and none was read.

It was also written after a non-registered planning study, P4, had simulated
independent plain trajectories for 15 FV-route A1 jobs on fresh planning
seeds, and tested them against those jobs' A1 values. No planning figure
enters any registered result.

**Evidence and reason.** A4 validates FV rows with an asymptotic test over
32 groups, labeled "asymptotic, not certified". A certificate under the FV
conditioned law would need uniform-in-time mixing constants for the
conditioned process, which cannot be computed for this model.

Given a source state, the residual's conditional law is the same on both
routes:
- the scored flow and the cell's value are fixed by the state;
- the one-step advance kernel is the same map on both routes, because A4's
  FV trace records the transition before resampling.

The routes differ only in how often they visit each state inside a cell. So
the published FV values can be tested on independent plain trajectories,
which the certified plain-tier test handles. In P4, that test certified about
half of the FV cells, holding over 98.5 percent of plain-law visits in every
planning row.

**The rule.** A5 is label-only. It never changes a published support, value
or row status, so the reruns behave identically whether or not A5 has run.

**Tested set.** A5 tests every cell in the validated support of every
primary FV row with status `estimated` in the sealed A4 publication. These
are exactly the FV cells the reruns can look up. Sensitivity rows are not
published to the reruns, and are not tested.

For each tested row-cell b, the tested quantity is `theta_b^plain = E[m_i |
N_i >= 1]`. Here `m_i` is the mean living-source residual of an independent
plain trajectory in cell b, against the A4 published value. For FV rows,
those are the A1 values. The law is independent plain trajectories from the
table's archived initial law, under its fixed rule and kernel.

**Validation data.**
- **Tables:** the 252 primary FV-route A1 jobs of the A4 plan.
- **Replicates:** three per table, on the plain route, each with 32 groups
  and otherwise the job's own A1 settings: 2,048 independent trajectories
  per replicate, 6,144 per table.
- **Seeds:** A4's `stream_seed` with the tag `v3_R_fvplain`, the A1 job seed
  and the replicate index 1 to 3.

Before any simulation, the run builds one global set of forbidden seeds:
- every A1 job seed;
- every seed in the A4 plan, for every job and both routes;
- the D26 probe seeds;
- the planning seeds P1, P1-census, P3 and P4 (replicates 0 to 3), for every
  job.

It halts if any A5 seed is in that set, or if A5's 756 seeds are not
pairwise distinct.

**Residual and width.** As in A4:
- The residual is `(1 - beta) f + beta V(next) - C(b)`.
- A transition is covered only when:
  - its source is alive;
  - its source cell is in the tested set;
  - its next state is extinct or in the same row's A4 support.
- `V(next)` is the A4 published value, or `lower` at extinction. A
  transition into a cell the A4 family does not publish is not covered, as
  in the reruns' lookup.
- The cells are the FV row's own fine cells, with no population-0 merge.
- The living-source mask is required, because a plain trace keeps recording
  after extinction.

The width is `w_row = (1 - beta) W + beta (vmax - lower)`, with vmax the
row's largest A4 published value. It is computed from the A4 family before
any A5 data exist, and it bounds every `m_i`, provided every flow and
every published value lies in `[lower, upper]`. That is checked, and any
failure halts the run.

**Test and family.** The test is A4's plain-tier test unchanged: Maurer and
Pontil's two-sided empirical Bernstein bound at `delta = alpha / M`, with
`alpha = 0.05`, then the visit-weighted safeguard.
- **Certified:** the interval lies within `[-tau, tau]`, and `sum S / sum N`
  from the same data does too.
- **Violation:** the interval is disjoint from `[-tau, tau]`.
- **Unresolved:** anything else, or `n < 2`. Unresolved cells stay in M.

The number of trajectories visiting a cell is random. But the total is fixed
by the plan, the trajectories are independent, and selection by `N_i >= 1`
is a per-trajectory event, so coverage holds.

M is the number of tested row-cells, counted from the sealed A4 publication
before any A5 data exist. A cell in several rows counts once per row. This
is a separate family from A4's plain and FV tiers.

The statement is: with probability at least 0.95, every A5-certified cell
has `|theta_b^plain| <= tau`, simultaneously.

**Labels.** A certified cell is labeled "certified under the plain law",
always with that qualifier and never shortened to "certified". Every other
tested cell keeps "asymptotic, not certified". The labels live in a sealed
label record. The A4 family is not rewritten.

**Violations, fixed now.** A4 drops a failing cell from the support. A5
cannot, because it changes nothing the reruns load, so a violating cell stays
in use. Its false-violation rate is controlled at 0.05 within A5's family,
so a violation is a finding. The handling is fixed here, before any A5 data
or rerun outcome exists:
1. **The label record** lists each violation: its cell, row, interval and
   exposure. The exposure is the share of that row's living census endpoints
   that fall in the cell, from A4's census stage outputs.
2. **Every result whose configuration looks up a row with a violation**
   carries a disclosure, wherever it appears, naming the row, the number of
   violated cells and their total exposure.
3. **In the claims register,** every claim resting on such a result is
   recorded as conditional on the violation, never as proven.
4. **Removing a violated cell** changes the support and so the reruns. It
   needs its own pre-registered amendment and its own reruns. The operator
   decides whether to commission one, and the record of that decision states
   whether any rerun outcome was known when it was made.

**Sequencing.** The rerun loader accepts the A4 family only at the exact
code identity that published it, and a registered launch requires the
working design note to match its pin. A5's implementation changes the code
identity. So:
- **This text changes no code identity.** It is committed before the reruns'
  registration pin is made, so that pin and the reruns' gate index include
  it.
- **The implementation is committed** only after the commit from which the
  reruns run is fixed. The reruns run from their own checkout at that
  commit.
- **A5 runs from its own checkout** at the implementation commit, after the
  reruns by default. Its order relative to the reruns affects no decision,
  because the handling above is fixed.
- **A5 reads the A4 family directly.** It verifies the family's file hash
  and seal, its receipt and its cell-results sidecar against the committed
  identity record, `simulation/v3/runs/registered/A4_family_identity.json`,
  which the commit fixing the reruns adds. It also verifies the A4 plan
  against the receipt. It does not load the family through the production
  loader.

**Runner.** The production runner gains one A5 job kind, and its other job
kinds are unchanged. A5 re-pins the approved boundary hash of
`v3/production_runner.py` in `simulation/v3/table_compatibility_A2.json`.
The record keeps the previous hash in an `a5` note, as A4 did.

The configuration test, durable completion records, resume, mode control,
memory caps and the per-phase nondeterminism check apply. The model server
is down for the run.

**What A5 does not establish.**
- **Certification under the FV conditioned law.** The two laws weight a
  cell's states differently. The cells the conditioned regime mainly reaches
  stay asymptotic.
- **The visit-weighted residual.** The 0.95 statement bounds the
  per-trajectory mean. The visit-weighted mean is only checked, as in A4.
- **Aggregation bias** within a cell, and residuals on transitions into
  cells the row does not publish.
- **An exact match to the reruns' allocation law.** The rerun policies
  differ from the table's fixed rule. The census law is the committed proxy.
- **A joint 0.95.** A4's plain statement, A4's FV statement and A5's
  statement each hold at 0.95 on their own. They do not combine into one
  joint 0.95 statement.

**Execution and cost.**
- **Compute (a planning estimate from P4 timings, not a measurement):**
  756 tasks at about 950 seconds, about 200 core-hours. That is about 12.5
  hours on 16 workers, at about 1.9 GB per task.
- **Ceiling:** a cumulative 24-hour wall ceiling. If the configuration test
  projects past it, the run stops and reports the gap.

The run halts on:
- a flow or value outside `[lower, upper]`;
- a seed collision;
- an A1 source-hash mismatch;
- an A4 family, receipt or sidecar hash mismatch;
- nondeterminism in a re-executed sample task.

**Reporting.** The report gives, per row and in total:
- the counts of certified, unresolved and violating cells;
- the share of plain-law visits in certified cells;
- the share of living census endpoints in certified cells;
- every violation with its exposure.

It reports no survival, extinction or fire rate.

### Amendment A6, 2026-09-29: the W11 sensitivity and convergence runs, completed

**Timing and status.** The operator chose option O2 on 2026-09-29 (D32), and approved the A6 design (D33) after blind double certification by two independent reviewers from different model families. This text is registered by the commit that adds it. A6 is effective for registered execution from the later commit that adds its implementation (see Order and code identity).

It was written while the registered A4 run was in progress. That run's progress counts, launch records and memory use had been read, and aggregate worker-second timings from its completion records. None of its stage outputs had been read. No A4 publication, rerun manifest, rerun job or rerun output existed, and none was read. No figure from any v3 rerun informs any choice below.

**Evidence and reason.** Section 6 registers five sensitivity and convergence arms. A readiness review found three gaps:
1. **No job builder.** Nothing builds the arms' jobs.
2. **Missing tables.** The crowding arm and the σ0² arm need table families of their own, because the tables' kernel identity includes the crowding variant and the novelty protocol, which holds σ0². No such families are registered or budgeted.
3. **No reading.** Section 8 lists no sensitivity quantity, so under its last line every sensitivity result would be exploratory.

A6 closes the three gaps.

**One change to section 6,** authorized by the operator under O2: **the σ0² arm is narrowed from R1's nine rr to five.** They are the five nearest v2.0's registered inflection, 0.063 (section 9): 0.059, 0.060, 0.062, 0.064 and 0.066. The tie at distance 0.003 includes both 0.060 and 0.066. A σ0² variant whose boundary falls below 0.059 reads "undetermined".

Every other arm, grid, weight, horizon and seed count in section 6 is unchanged. D18's "a quarter of the seeds" for the crowding variant is read as a quarter of R1's 400 per cell, which gives 100, the count the other arms use.

**The arms and their tables.**

| Arm | Cells | Seeds per cell | Tables |
|---|---|---|---|
| Weight corners, κ ∈ {0.75, 8} × θ ∈ {0.25, 0.75} | R1's 9 rr at alpha 1.0 and capability 1.5, plus R2's 5 alpha × 7 capabilities at rr 0.064 (44 cells) | 100 | nominal A4 family |
| Horizon, 1,000 steps | R1's 9 rr at alpha 1.0 | 200 | nominal |
| Crowding, the reproductive-age variant | the weight-corner cells | 100 | crowding family |
| σ0² ×10 and σ0² ×0.1 | the five rr above, at alpha 1.0 | 100 | one σ0² family each |

**Unvaried weights** are at the center, κ = 8 and θ = 0.5.

**The nominal family already scores κ = 0.75 on the weight-corner contexts.**

**The variant table families.** Each is built with the committed table-job settings and A1's screens.
- **Its scoring contexts are exactly its arm's cells at κ = 8.** It adds no other context, so an unused row cannot fail the family.
- **The crowding family:** R1's 9 rr × 25 rules. The frozen table-sensitivity subset at 0.055 and 0.064 adds 12 jobs, for 237 in all.
- **Each σ0² family:** the 5 rr × 25 rules. The subset at 0.064 adds 6 jobs, for 131 in all.
- **Completeness** is checked against the family's own contexts.

**The σ0² calibrations.**
- σ0² is set to 10 and 0.1 times its frozen value.
- ε_N is re-derived by the committed protocol from the 50 registered calibration records, identified by their digests in `input_hashes`. ε_N is the only calibrated value that depends on σ0².
- The fixed center, N_ref, ε_E, ε_L and c_E stay frozen.
- The derivation must reproduce the frozen calibration exactly when σ0² is unchanged. That is checked, and any mismatch halts.
- Each variant calibration is sealed with its own hash before any variant table job runs.

**Validation of the variant families.** Each family is validated by amendment A4 in full:
- its own M and M_FV, counted from its own outputs before its validation data exist;
- the plain tier certified;
- the Fleming-Viot tier "asymptotic, not certified";
- the census under the family's own kernel;
- the availability floor.

No A5 labels are made.

**If a family cannot load,** because a row is not_estimable or the floor fails, its arm is reported as not run, with the reason. Any repair is a new amendment. No arm is rescued after any R1 or R2 output has been read.

**Seeds.**
- **Variant tables:** each job's seed follows from its own job identity, which includes its kernel and calibration. A4's stream seeds follow from those.
- **Runs:** seeds are derived from each run's cell and index under the tag `v3_rerun`, and the cell identity includes κ, θ, the step count and the variant.
- **Before any simulation,** one global check asserts that every new seed is distinct from every A1, A4, A5, rerun, probe and planning seed, and from every other new seed.

**The reading, registered now.**
- **Quantities:** section 8's, on each arm's cells.
  - **R1-grid arms:** survival at each rr, and the boundary location.
  - **R2-grid arms:** cap\* per alpha at rr 0.064, with D24's censoring.
- **The comparator:** the same quantity from the main reruns on the same cells. That is R1 at alpha 1.0 on the arm's rr, without the refinement grid, and R2 at rr 0.064 only.
- **The horizon arm** measures survival at 1,000 steps. Its comparator measures it at 500.
- **The headline family** has 33 comparisons: the boundary location in 8 arms (the 4 corners, the horizon, crowding and the 2 σ0² variants), and cap\* at each of 5 alphas in 5 arms (the 4 corners and crowding).
- **The interval:** for each headline comparison, a percentile bootstrap interval on the difference, arm minus nominal.
  - The two sides are resampled independently, by seed within cell.
  - At least 50,000 resamples are drawn.
  - The level is 1 − 0.05/33, so the family-wise error is at most 0.05.
- **Materiality margins:**
  - for the boundary location, 0.002 in rr;
  - for cap\*, one step of the capability grid (1.2, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0). The difference is measured in grid steps.
- **Verdicts:**
  - **Moves materially,** lower or higher: the interval lies wholly beyond the margin on one side.
  - **Robust:** the interval lies wholly within the margin. For cap\*, that means zero steps only.
  - **Inconclusive:** anything else.
  - **Undetermined:** the quantity is undefined in the arm or in its comparator.
- **What follows from each verdict:**
  - **Moves materially:** every claim resting on that headline result carries the arm's name as a sensitivity, in the claims register and wherever it is cited, until shown otherwise.
  - **Inconclusive or undetermined:** reported with the claim, as "sensitivity to [arm] not resolved at the registered seeds".
  - **Robust:** reported.
- **Descriptive only:** the survival difference at each rr, with a per-comparison 95 percent interval, and the half-seed and full-seed estimates for seed convergence. These carry no verdict.

**Order and code identity.** The rerun loader accepts the nominal A4 family only at the exact code identity that published it (A5, Sequencing).
- **The weight-corner and horizon arms** run from the rerun checkout, at the rerun commit's code identity. A6's builder writes their job list as a sealed manifest, which is data. The runner there checks each job's identity and the rerun pin.
- **The crowding and σ0² arms** run at A6's implementation identity. Their calibrations and families are sealed and published at that identity.
- **A6's implementation adds new modules only.** It changes no existing file that enters the code identity, so every arm runs the engine code the reruns run. It asserts that every such file is byte-identical to the rerun commit's.
- **Commits:**
  - this text before the rerun pin;
  - the implementation after the rerun commit, like A5's code.
- **Scheduling:** the variant families may run during the reruns on a machine established as bit-identical to the X2 (D32), otherwise after them. The runs follow once their tables are in place.

**Ceiling.** 72 X2 wall hours for the three variant families and every sensitivity run together. It replaces section 6's 48-hour sensitivity ceiling, and D18's 24-hour table ceiling for these families.
- **The planning estimate** is about 70 hours: about 28 for the crowding tables, about 15 for each σ0² family, and about 12 for the runs.
- **The measured projection** before each registered launch governs. If it exceeds the ceiling, the operator decides before any registered run, between a budget amendment and a uniform seed reduction across the arms' cells.

**What A6 does not establish.**
- Robustness beyond the registered arms and ranges. The W11 item 3 global screen over the parameter register's constants stays unregistered.
- Anything about the crowding variant as a model (section 11).
- Certification of variant Fleming-Viot cells beyond A4's asymptotic tier.
- Evidence of robustness from an "inconclusive" verdict.

**The design and certification records** are in `simulation/v3/A6_design/`.

### Amendment A7, 2026-09-30: the A6 budget ceiling

**Timing and status.** The operator approved this change on 2026-09-30 (D34). It was written while the registered A4 run was in progress. That run's progress counts, launch records, memory use and aggregate worker-second timings had been read, but none of its stage outputs. No A4 publication, rerun manifest, rerun job or rerun output existed, and none was read. No A6 job had run.

**The change.** A6's ceiling of 72 X2 wall hours becomes **90 X2-equivalent wall hours**, for the three variant table families and every sensitivity run together. An X2-equivalent hour is one hour of the X2 at its measured 16-worker plateau. Work on another machine established as bit-identical to the X2 (D32) counts at that machine's measured relative throughput. Everything else in A6 is unchanged, including the rule that the measured projection before each registered launch governs, and that the operator decides between a budget amendment and a uniform seed reduction if a launch would exceed the ceiling.

**Reason.** A6's implementation costs every component from committed measurements. The high-memory Fleming-Viot validation takes its measured 6,200 seconds per task at its memory-capped worker count, and each launch's configuration test and cleanup reserve are included. The planned total is then 82.2 X2-equivalent hours:
- 18.9 for table estimation;
- 50.0 for validation;
- 13.3 for the runs.

A6's planning figure of about 70 hours had costed that validation at half its measured time, and left out the launch overheads. A uniform seed reduction shortens only the runs, so it cannot close the gap. The new ceiling leaves about 10 percent above the plan, because a launch that reaches its ceiling must restart on a new run root.
