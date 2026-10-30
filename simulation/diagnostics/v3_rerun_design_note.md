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

### Amendment A8, 2026-10-04: the main reading, specified

**Timing and status.** The operator approved these resolutions on 2026-10-04. Every registered run had completed. No registered R1, R2, gate or A6 outcome had been read by the operator or the interpreter.
- **The sealed A6 reading** (sha256 6c8782f3a86a87aefb11102cd8da24fffac1ab70ff7959c07ad3370026ca3d5b) had been computed twice, byte-identically, and not opened. Its extraction step printed only check labels, counts and hashes.
- **The post-run gate evaluation** (gates_A4, 2026-10-01) had not been seen by the operator or the interpreter. The executor had access to it while mapping the questions below, and reported nothing from it.
- **One structural inspection** printed the length of the step log of two individual runs. Every run records every step, so this carries no outcome.

The questions were found by the executor's mapping of sections 7 to 10, before any reading code was written. None of the answers depends on an outcome, and nothing is adjusted toward a v2.0 figure.

**Reason.** Sections 7 to 10 name the quantities, readings and predictions. The executor's mapping found 13 points they leave undetermined, among them P2's v2.0 values, the interval protocol, the boundary's edge cases, the cliff rule's quantifier, and how the per-run diagnostics are summarized. This amendment fixes each before the main reading's code is written or any of its output is read.

**The resolutions.**
1. **P2's v2.0 values** are the v2.0 Category A counts, which the instrument validation record reproduced identically (target T1): survivors of 1,200 at rr 0.055, 0.056, 0.057, 0.058, 0.059, 0.060 and 0.062 of 2, 11, 13, 35, 58, 147 and 414. Each value is the exact fraction of 1,200. The refinement point 0.061 has no v2.0 value and is not part of P2.
2. **The scope of P1 and P2.**
   - **Grid and estimate:** both use the nine-point R1 grid and survival pooled over alpha, 1,200 runs per rr, as v2.0's comparator was pooled.
   - **P1** holds if pooled survival does not decrease between any adjacent pair of grid points.
   - **P2** holds at a point if v3's pooled survival p satisfies p >= v - 2 SE, where v is the v2.0 fraction and SE = sqrt(p(1 - p)/1200). At p = 0 or p = 1, SE is 0.
   - **By-alpha survival** is reported as section 8 registers, and is not part of P1 or P2.
3. **The cliff rule** in section 9 has two parts:
   - cap\* is non-increasing in alpha, by G2.2's point rule with D24's censored order;
   - at **each** of alpha 1.0, 1.25 and 1.5, at least one tested capability has a fire rate, pooled over rr as cap\* uses, strictly below 0.5.

   P3 is evaluated by the same rule.
4. **Intervals.** The bootstrap interval for the R1 boundary (section 8) and the R2 location intervals (section 9) are two-sided 95 percent percentile intervals, one per comparison, with no multiplicity correction.
   - **Resampling:** 50,000 resamples from one NumPy `default_rng(20261004)`, with quantiles by `inverted_cdf`.
   - **Within cells:** seeds are resampled with replacement within each original cell, then pooled as the estimate pools. An R1 cell is one rr and one alpha; an R2 cell is one rr, one alpha and one capability. Cells are drawn in sorted order of their identity.
   - **Unchanged:** section 8's Wilson intervals at z = 2.
5. **The boundary** is the rule of `reading_a6.boundary` and its resample counterpart, pinned at commit 3dbee584: the first upward crossing of 0.5, by linear interpolation between adjacent grid points, with endpoints and exact hits as that code treats them.
   - **Grid:** the combined main and refinement grid, as section 8 says, with survival pooled over alpha.
   - **Resamples without a crossing** are kept as censored at the corresponding end, and never dropped.
   - **A point estimate without a crossing** reads "no transition in range".
6. **The first failing capability**, per alpha and pooled over rr, is the next tested capability above cap\*: the G4.2 companion, and the paper's "between 2.5x and 3.0x" bracket. If cap\* is censored at the top, none fails in range. If it is censored at the bottom, the first failing capability is 1.2. It has no interval.
7. **R2's location against v2.0's sequence** (5.0, 3.0, 2.5, 2.0, 2.0 at alpha 0.5, 0.75, 1.0, 1.25, 1.5) is read in cap\*'s ordered categories under D24: below 1.2, then 1.2, 1.5, 2.0, 2.5, 3.0 and 4.0, then 5.0 and above at the top. v2.0's 5.0 is the top category. The interval is the 95 percent percentile of the bootstrap category index, keeping every censored draw.
   - **Consistent:** v2.0's category lies within the interval.
   - **Lower** or **higher:** the interval lies wholly below or wholly above it.
8. **The per-run diagnostics** go to a sealed per-run file, one record per run. Each record holds:
   - **survival-first:** its share of the run's living-start steps (population above 0 at the start of the step), with that count;
   - **the cohort bound** at each period start, as the full sequence;
   - **precedence overrides:** the number;
   - **chosen rules:** the count of each;
   - **side values:** the means of Lambda_F, Lambda_b and LS of the chosen rule, each over the living-start steps where it is estimable, with those counts;
   - **the ranking flag and the tail standard:** the counts under items 9 and 10.

   The reading reports per original cell: the equal-run mean of each per-run scalar, the total override count, and the pooled counts of chosen rules and ranking flags. These are descriptive, with no intervals.
9. **The ranking flag (S4)** is joined from the pinned A4 table family, using the recorded rule and its recorded scoring context; at a fired review, that is the context before the review. The join is verified against the family's hashes, and nothing is re-estimated. Unavailable and absorbed steps are counted separately.
10. **The tail-standard diagnostic** was not recorded by the registered runs, and none is constructed now. It is reported as "not recorded", with this reason.
11. **A4 and A5 labels.** The A5 label record, published on 2026-10-04 (sha256 0e9fbee8cd27b7a3408ca90f101fa55b03b359a5b70bebd3862b4c2a3e36dbc7), and the A4 family identity are inputs. The reading attaches the labels and disclosures that A4 and A5 require.
12. **A6's qualifications.** The sealed A6 reading is referenced by its sha256. Its verdicts are attached when claims are written, as A6 directs, and are not recomputed.
13. **Seed convergence** is delivered by the sealed A6 reading: half and full seeds for R1 survival (pooled and by alpha), the R1 boundary and R2 cap\*. It is referenced by its sha256, and no other convergence quantity is computed.

**Unchanged.** A8 does not change any registered quantity, reading, prediction, gate or citation rule, nor A6. Anything else computed is labeled exploratory. The main reading's registration is the commit that adds this amendment.

### Amendment A9, 2026-10-04: decision D9's welfare check, registered

**Timing and status.** The operator approved this amendment on 2026-10-04, after A8 and before any reading was opened. The state of knowledge is A8's:
- **The two sealed readings** had both been computed and neither had been opened: the main reading (sha256 51b3c63a6ae9f6546423dc553c219d92dbeaaea01c3e5370be9835fdbfce411a, under A8) and the A6 reading (sha256 6c8782f3a86a87aefb11102cd8da24fffac1ab70ff7959c07ad3370026ca3d5b).
- **No outcome had been read** by the operator or the interpreter. Their consoles printed only check labels, counts and hashes.
- **The gap was found** while fixing the claims map before opening, a step that uses no results.

Nothing is adjusted toward a v2.0 figure.

**Reason.** Decision D9 item 5 (adopted 2026-09-27) required this rerun's pre-registration to validate the demographic approximation behind the v2.0 paper's section VIII.2: "That rerun records `resource_level` at every step, and checks the realized welfare against r = 0.9." That requirement was not carried into this note or A8. This amendment registers the check. It changes no registered quantity, reading, prediction, gate or citation rule, and neither sealed reading.

**The quantity.** The committed code defines the resource input from the executed welfare share s (cohort.py: "r = .9 + .12*(share-1/6)"):

r_eff = 0.9 + 0.12 (s - 1/6)

s is the welfare component of the executed action at a living-start step, as recorded in the run evidence. The welfare floor keeps s at 1/6 or more, so r_eff lies between 0.9 and 1.0, and equals 0.9 exactly at the balanced share.

**The check.**
1. **Runs:** every R1 run on the main and refinement grids, 14,400 runs.
2. **Steps:** every living-start step (population above 0 at the start of the step) of the 500.
3. **Per run:**
   - the mean r_eff over its living-start steps;
   - the share of those steps at exactly the balanced share (s = 1/6, within 1e-12);
   - the mean well-being over the same steps: the population mean of `welfare_units_before`/1000. This is reported as well-being, a different quantity from D9's resource level.
4. **Strata:** each rr pooled over alpha, and each rr by alpha.
5. **Summaries per stratum:**
   - **the primary estimate:** the equal-run mean of the per-run means;
   - the living-step-pooled mean;
   - the 5th, 50th and 95th percentiles of the per-run means, by `inverted_cdf`;
   - the equal-run mean of the balanced-step share.
6. **Uncertainty:** descriptive only, with no intervals.
7. **No new simulation.** As D9 decided, there is no separate batch and no further benchmark.
8. **The record:** sealed per-run summaries, each referencing its preserved per-step evidence by job ID and output sha256.

**The reading rule.** No threshold is set. For each stratum the check reports r_eff - 0.9 and the balanced-step share. That report closes D9's welfare condition. VIII.2's restatement is then entered as "the boundary's location follows from the demographic rules at the realized welfare level", with the realized level stated. It reads "at the balanced welfare level" only where every living-start step of every run in the stratum is at the balanced share.

**The registration** of this check is the commit that adds this amendment.

### Amendment A10, 2026-10-08: frontier velocity as a pace, and capability's benefit

**The defect.** The instrument registered in section 3 measured the lineage factor's frontier velocity as a level, not a pace, and gave capability no benefit. Three consequences followed:
- **Θ stayed below 1.** Under resolution R4, v = capability × technology stock. That is never zero while capability and technology are positive, so Θ < 1 at every living state. The specification's "Θ = 1 at no frontier" (S2) held only in a limit no run reaches.
- **Capability had no benefit.** Decision D6 item 9 (2026-09-26) says capability enters "through measurable effects on execution, resource use and the frontier-to-transfer mismatch". R4 implemented the mismatch only, so a more capable AI produced no more useful computation and no more welfare.
- **The threshold's scale was undeclared.** Bandwidth was mean welfare × transfer stock, so the scale at which u = 1 was implicitly 1, and was never argued.

Together these meant that yielding to a more capable successor always carried a lasting penalty and never a gain. So the succession comparison in sections 3 and 6 could not measure what it was designed to measure.

**How it was found, and what that means for this amendment.**
- **This amendment follows registered results and was prompted by one.** Every registered reading had been opened and read in full on 2026-10-05:
  - the main reading, sha256 51b3c63a6ae9f6546423dc553c219d92dbeaaea01c3e5370be9835fdbfce411a;
  - the A6 reading, 6c8782f3a86a87aefb11102cd8da24fffac1ab70ff7959c07ad3370026ca3d5b;
  - the A9 check, 91f9e0310d3b172a32249ee1a9320d5979237efa0ef83d58abc5b9c7cb14906d.
- **The tracing.** The succession reading led to an exploratory diagnostic study, from 2026-10-05 to 07, after opening. The study traced the cause to the mapping above.
- **Publication.** The readings and the study are published together, with their figures, once the reviewer clears them.
- **Had the succession reading looked as expected, the mapping would not have been examined.**
- **The mapping was accepted by the interpreter,** as an overnight resolution of 2026-09-27, and by the operator with the other resolutions (D19).
- **Why the checks missed it.** The certification and gates tested the specification's stated properties, and a level satisfies all of them. None asked whether a stable incumbent can reach Θ = 1, or whether a modestly more capable successor can ever be preferred. The certification below adds both.

**Timing and status.** Written on 2026-10-07 and approved on 2026-10-08.
- **What was known when it was written:**
  - the three readings above;
  - the exploratory diagnostic study;
  - an exploratory, table-free check of the corrected mechanics, on 2026-10-07;
  - published measurements of how fast societies have absorbed new technology;
  - a non-registered, cost-only pilot of the corrected code, on 2026-10-08 (section 12), which exported no outcome.
- **No registered table, run or output under this amendment existed** when it was written, and none had been read.
- **The registered results under R4 stand.** R1, R2, A6 and A9 keep their readings, gates and citation status. Nothing in them is re-read, re-scored or withdrawn, and they are reported beside this amendment's results.

**The safeguards.**
1. **How each value was set.**
   - **The absorption anchor** comes from measured historical rates of growth in output per hour, chosen before any run under this amendment.
   - **The window** is the model's own generation length.
   - **The benefit's form** is declared as the simplest available, with a registered alternative.
   - **The floors** follow from the specification's construction.
2. **No value was set by reference to a fire rate, a survival rate or a margin.**
   - The mechanics check informed three decisions, and none rests on a rate or a margin:
     - the zero-technology floor, after the check halted on log(0);
     - the capability domain, after it asked what the domain was;
     - the bandwidth floor, after it showed by arithmetic that one sensitivity arm was inert.
   - **The bandwidth floor change can only lower Θ.** Against the construction it replaces, it can only strengthen the penalty on fast change.
3. **Nothing is adjusted toward a v2.0 figure.**
   - v2.0 multiplied the lineage term by capability, which D6 item 9 removed.
   - This amendment does not restore that. Capability enters only through computation and welfare production, the channels D6 named before any rerun.
4. **If this amendment's results are not as predicted, no value below is changed in response.** Any further change would be a new decision and a new amendment, stating that it follows this amendment's results.

**1. The instrument change** (decision D35):
- **The frontier:** F_t = capability_t × max(technology_t, 0.01). The floor of one stock unit applies inside F only.
- **Frontier velocity, a pace:**
  - **The pace:** v_t = max(0, log F_t − log F_{t−30})/30.
  - **The window:** 30 steps, one human generation in the model.
  - **Before step 30,** the window starts at step 0, and the difference is still divided by 30.
  - **Retreat:** a falling frontier is not an absorption burden.
  - **At a handover,** a jump from c to c′ adds log(c′/c)/30 for 30 steps.
- **Bandwidth, an absorption rate:**
  - b_t = (log k\*/30) × (w_t·tr_t)/(w_ref·tr_ref), where w is mean living welfare and tr the transfer stock.
  - k\* is the capability factor per generation that is exactly absorbable at the reference levels.
  - Bandwidth is clipped uniformly at b_min′.
- **Θ = φ_tr·exp(−α·max(0, u − 1))** as adopted, with u = v/max(b, b_min′) and φ_tr = exp(−(1 − tr)·v/v_max′).
- **Computation (C1):** H_E = 1 − exp(−2.5·g(c)·x_compute).
- **Welfare production (C2):** the welfare increment is max(40, 38 + 12·g(c)·share). The floor of 40 is unchanged, so the cohort bound's floor path remains a valid lower path.
- **g(c) = c.** The registered alternative is g(c) = c^0.5. Since g(1) = 1, an AI at capability 1 behaves as before in both channels.
- **Each plan is evaluated at its own capability:** the incumbent's before its handover, the successor's after.
- **No risk credit.** Nothing credits capability with lower extinction risk. Risk stays with admission.
- **The capability domain is [1, 5].** The instrument refuses a model whose capability lies outside it.

**2. The evaluation horizons:**
- **Yield reviews:** every plan in a yield review is simulated to 30 steps past the period's deadline, with common random numbers, and its continuation is then taken from the table.
  - **Why:** the pace remembers 30 steps and the tables do not. This brings every handover's pace window inside the simulated horizon, so no part of the **pace** penalty is dropped.
  - **Physical consequences** of a handover, such as the institutional drawdown, can outlast the window. They carry through the endpoint state into the continuation, as before.
  - **After the deadline,** each plan follows its own stationary rule, as its continuation already assumes. The continuation is discounted from the extended endpoint.
  - **Unchanged:** the decision window, the deadline, the plan class and the review grain.
- **Allocation:** in the 30 steps after a handover, each allocation rollout extends over the rest of the pace window before its table continuation. At every other step it is unchanged (20 steps, then the table).

**3. The registered constants.**

| Constant | Value |
|---|---|
| τ | 30 steps |
| k\* | 1.8 per generation; arms 1.5 and 2.3 |
| tech_min | 0.01 |
| w_ref, tr_ref | 0.8029014082336364, 0.7292628000000001: separate means over the 25,000 living observations of the calibration's recorded 50-seed B1 procedure at rr 0.080, regenerated |
| v_max′ | log(500)/30 = 0.2071536032807397, over capability [1, 5] |
| ε_L | 0.001412790614729507, unchanged |
| b_min′(k\*) | min(0.014666388971338522, b_ref(k\*) × 0.325/(w_ref·tr_ref)), with b_ref(k\*) = log(k\*)/30: 0.007502 at k\* 1.5, 0.010875 at 1.8, 0.014666 at 2.3 |
| g | c; arm c^0.5 |

b_min′ is declared at a minimal absorptive state, founding conditions with welfare 0.65 and transfer 0.50, and capped at R4's construction. It satisfies Θ(v_max′, b_min′) ≤ ε_L at every α ≥ 0.5 in every arm.

**4. Unchanged:**
- the objective and its weights;
- the yield rule and plan class;
- admission: the cohort bound, survival-first and R14;
- the rule class Π;
- the other observables;
- the demographic rule and the successor construction;
- the survival rule and the horizon;
- the calibration file, to which section 3's constants are added as a separate frozen and hashed record.

**5. The runs.**
- **R1′, its refinement grid and R2′** repeat section 6's grids, seed counts and seed derivation exactly, under the corrected instrument: 24,900 runs.
- **Seeds:** each run's seed equals its R4 counterpart's, so every run is paired by seed with the registered run under R4.

**6. Sensitivity:**
- **A10's arms:**
  - **Which:** k\* = 1.5, k\* = 2.3, and g(c) = c^0.5, each changing one value from the nominal.
  - **Cells, seeds and comparisons:** A6's weight-corner arms', with 44 cells at 100 seeds, so 13,200 runs.
  - **Tables:**
    - the k\* arms change only Θ, so they re-score the nominal family's simulations;
    - the c^0.5 arm changes the dynamics, so it has its own family, simulated per capability over its own contexts only.
  - **The reading:** A6's rule (D33): percentile bootstrap intervals on the difference, arm minus nominal, at Bonferroni level 1 − 0.05/18. Materiality margins are 0.002 in rr and one capability step. The verdicts are moves materially, robust, inconclusive or undetermined.
  - **The headline family:** the boundary in each arm, and cap\* at each α in each arm.
- **A6:** re-registered unchanged on the corrected instrument, against its nominal.
  - Its nominal-table arms run in stage 1.
  - Its variant families run in stage 2, after R1′ and R2′, within a ceiling set by a later dated amendment (section 12).
- **A9:** computed on R1′ exactly as A9 specifies, with no new simulation.

**7. Tables.**
- **A new nominal family** is estimated at the corrected code identity.
- **Simulated per capability.** Under C2, capability enters the dynamics, so the physical simulations that the registered estimator shared across capabilities are made per reproduction rate and capability.
- **Pace history.** Each table trajectory carries it. Continuation values are fitted only on steps 30 and later of each trajectory, so no fitted value comes from a step with an incomplete pace history.
- **Fertility support.** The support rule that conditions the tables uses each capability's own maximum welfare increment.
- **The table rules** of A1, A2, A4 and A5 apply to it, and to each arm's family, as they applied to the A4 family. A3 was superseded by A4.
- **Registered mode** refuses any family from another code identity.

**8. Gates.** Section 7 applies in full to the corrected instrument and to R1′ and R2′, as it applies to R1 and R2. Before the build, on 2026-10-07, the changed properties were certified by two certifiers from different model families, each blind to the other's work. Each property below held. One statement was narrowed to the pace penalty (section 2), and the comparison led to the allocation extension and the per-capability tables. The properties:
- Θ's bounds, continuity in u, Θ = 1 at no frontier, and the floor guarantee;
- the finiteness of u;
- extinction dominance, with H_E^min unchanged at 0;
- the cohort bound's floor path under C2;
- the yield rule's derivation under section 2's horizon;
- two properties R4 lacked:
  - a stable incumbent with steady technology has Θ = 1;
  - a successor of capability 1.2 is preferred at some declared state and α, by the formula alone.

The S10 conformance tests are updated for the change, and pass.

**9. Registered quantities.** Section 8, with A8's resolutions, applies to R1′ and R2′ unchanged. These are added, as descriptive diagnostics with no intervals:
1. **The shadow decision:**
   - **What is recorded:** at every yield review, admitted or not, the decision the plan comparison would make, together with the best immediate, later-yield and hold values. It acts only when the review is admitted.
   - **Reported per R2′ cell:** among reviews with an immediate and a waiting plan available, the share whose shadow decision yields. It is reported for period 1 and for later periods separately.
2. **Θ and bandwidth, per run:** over living-start steps,
   - the mean of Θ;
   - the share of steps at Θ = 1;
   - the share with bandwidth at the floor b_min′.
3. **Transitions, per run:** the count, and the final capability.

**10. Readings.**
- **Against v2.0:** section 9 and A8 apply to R1′ and R2′.
- **R1′ against R4:** the paired difference in the boundary, using A8 item 4's bootstrap with each seed's pair kept together.
  - **Unchanged:** the interval lies within ±0.002.
  - **Moved lower** or **moved higher:** it lies wholly beyond that margin on that side.
  - **Inconclusive:** otherwise.
- **The cliff:** "cliff present" is reported as **non-vacuous** when cap\* is at least 1.2 at one α or more, and as **vacuous** otherwise.

**11. Predictions, registered now and reported as right or wrong:**
- **P4:** pooled R1′ survival is non-decreasing across the nine-point grid (P1's rule).
- **P5:** at each rr from 0.055 to 0.062, pooled R1′ survival is at least v2.0's value minus two standard errors (P2's rule, with A8 item 2's values).
- **P6:** the R1′ boundary has not moved higher than R4's (section 10's reading is not "moved higher").
  - **The basis:**
    - survival-first and the welfare floor are unchanged;
    - after a handover to capability 1.5, C2 raises welfare production;
    - the objective's own allocation acts only in admitted periods.
- **P7:** at every α, the R2′ fire rate at capability 1.2, pooled over rr, is at least 0.5.
  - **The basis:**
    - a 1.2 handover's pace, log(1.2)/30 ≈ 0.0061 per step, is below bandwidth even at the floor, so only φ_tr penalizes it, by about 1 percent for 30 steps;
    - its computation benefit is permanent;
    - period 1's reviews are admitted from the founding state.
- **P8:** R2′'s cap\* is non-increasing in α (the first part of A8 item 3's rule). **The basis:** the pace penalty grows with α, and the benefit does not depend on α.
- **P9:** at α = 1.5, some tested capability fires at a rate strictly below 0.5. **The basis:** a jump of four or five times costs Θ heavily for 30 steps at α = 1.5. With the technology pace of a run's opening, where admission places most reviews, that cost outweighs the benefit at every bandwidth from the floor to the reference.
- **P10:** in every R1′ cell, the equal-run mean of the per-run mean Θ over living-start steps is at least 0.95. **The basis:**
  - Θ is 1 at a stable state;
  - a handover to 1.5 lowers Θ by about 2 percent for 30 steps at reference bandwidth.

**The author's expectation, stated before any run** (a prediction, not a criterion):
- **Section 9's full cliff rule** (a failing capability at each of α 1.0, 1.25 and 1.5): about even.
  - At α = 1.0, a jump of five times loses at the floor bandwidth and wins near the reference.
  - Period 1's reviews come as bandwidth rises from the one toward the other, and waiting plans can choose the later review.
- **The location against v2.0's (5.0, 3.0, 2.5, 2.0, 2.0):**
  - at the top at α 0.5;
  - consistent or higher at most other α;
  - possibly lower at α 1.5, if the first review decides.
- **The shadow decision:** yielding preferred at most capabilities at α ≤ 1.0, in every period. The yield share falls with capability at α 1.5.
- **R1′ against R4:** unchanged or moved lower. A lower boundary would come from C2's added welfare production after handovers.
- **The arms:**
  - k\* = 1.5 lowers cap\* at α ≥ 1.0;
  - k\* = 2.3 raises it;
  - g = c^0.5 lowers it, or leaves it at the top, because the benefit is smaller against the same penalty.

**12. Cost, and the two stages.**
- **The measured pilot.** A non-registered, cost-only pilot ran on 2026-10-08: 77 full-length sampled jobs over the declared strata, at the corrected code.
  - It measured cost only. No outcome was exported or read.
  - Its conservative projection, under the registered conventions, is 979 X2 hours for stage 1 below, and 2,626 for everything.
- **Stage 1, the nominal family,** with a ceiling of **980 X2-equivalent hours** (operator, 2026-10-08). It covers:
  - the nominal table family, including the k\* arms' scoring, which shares its simulations;
  - R1′, the refinement grid and R2′;
  - the k\* arms' runs;
  - A6's arms that use the nominal tables (the weight corners and the horizon).
- **Stage 2, the rest:** the c^0.5 arm, and A6's variant families on the corrected instrument (crowding, σ0² ×10 and ×0.1), with their tables and runs.
  - They stay registered by this amendment, unchanged in design.
  - Each launches only after a dated amendment sets its ceiling, committed before that launch.
  - A7's 90-hour ceiling applies to A6 on the R4 instrument only.
- **The rules for ceilings:**
  - a ceiling is a budget, never a quantity, reading or prediction;
  - if a measured projection exceeds its ceiling, section 6's rule applies;
  - nothing is cut after a registered output is read.

**13. Order and code identity.**
1. This text is committed and pushed first. It does not change the code identity.
2. The certified implementation is committed next, and its identity recorded.
3. The tables and runs run from their own checkout at that commit, which never receives later commits.
4. Each registered launch needs the operator's go and the pre-launch configuration test.
5. The registered readings are computed sealed and opened on the operator's go, as for R1 and R2.

**Unchanged.** A10 changes no registered quantity, reading, prediction, gate or citation rule of R1, R2, A6 or A9 under R4.

### Amendment A11, 2026-10-08: executing A10

**Timing and status.** This was written on 2026-10-08, after A10's text (64f2cb4f) and implementation (4f2f8e89) were committed, and before any registered A10 job ran.
- No registered A10 output exists. The only A10 measurements read are the cost pilot's (A10 section 12).
- The R4 readings had been read, as A10 records.
- The operator approved this change on 2026-10-08 (D36).

**Why.** Reviewing stage 1's execution procedure against the committed code found two conflicts. It also found a gap that would make any later defect expensive.
- **The label ceiling.** Under A10, A5's label step still enforces A5's 24-hour ceiling, which was written for R4's 756 tasks. A10's estimation and validation already run under the ceilings declared for them, and section 12 makes the stage ceiling govern.
- **The identity record.** A5 requires its family identity record to be committed at the head of the checkout that runs it.
  - Under R4, that commit came before A5's checkout existed (A5, "Execution and cost").
  - Under A10, the record can exist only after A4 publishes the family, inside the execution checkout. Section 13.3 says that checkout never receives later commits.
- **One launch, one machine.** The runner runs each launch on a single machine. Stage 1's table phases are single launches, each up to hundreds of hours. Neither the workstation nor any machine added later could share them.
- **The exact code identity.** A10's tables, labels, receipts and runs load only at the exact code identity that produced them. Suppose a defect is found after a registered output exists, and its repair changes no output. Even then, the repair could be made only by rerunning everything downstream of it.

**The changes.**
1. **The label ceiling.** Under A10, A5's labels run under the ceiling declared for them within their stage's ceiling (section 12), as A10's estimation and validation do. A5's 24-hour ceiling continues to apply under R4.
2. **Section 13.3, clarified.** The execution checkout never receives a code change. It may receive one kind of record-only commit, which leaves the code identity unchanged: the family identity record that A5 requires, committed after A4 publishes the family.
   - Each such commit contains only its record. The operator approves it, and the execution record lists it.
   - The same bytes are committed to the public repository.
3. **Compatibility after a registered output exists.** Suppose a defect requires a code change after a registered A10 output exists. Existing outputs then carry forward to the new code identity only through a committed compatibility record. The record:
   - names the producing code identity and the new one;
   - lists every changed file, with both of its hashes, and the reason for each change;
   - carries a re-execution proof. In each completed phase, for each capability and setting the phase covers, the two jobs with the smallest hashes under the tag `A11-compatibility` are re-executed at the new identity (all of them, if fewer). They are chosen before any re-execution. Every re-executed result must be byte-identical to its durable record, apart from timing and host metadata.

   **Its limits:**
   - A change that alters any re-executed result is not compatible, and the outputs it affects are rerun.
   - The record is reviewed, approved by the operator, and committed before any output is used at the new identity.
   - Work at the new identity runs from a fresh checkout at the commit that adds the record. The old checkout stays unchanged.
   - A launch's own run folder holds work from a single code identity, so an unfinished launch is never resumed at a new one.
   - A compatibility record changes no registered quantity, reading, prediction, gate or ceiling.

4. **One launch across several machines.** A registered launch may run on several qualified machines at once.
   - **One run folder.** The launch keeps one coordinator and one run folder, on the machine that holds it. Every job's completion record lands there and names the machine that ran it. The table producers and the gates read it as they read a single-machine launch.
   - **Pulling, not fixed shares.** A machine takes its next job only when a worker slot frees up and the job fits its memory. Jobs are offered longest first, by cost classes taken from the cost pilot and frozen in the launch's manifest before it starts. The order affects scheduling only, never a seed, a setting or a result.
   - **Leases.** A job a machine takes is leased to it. If the machine stops responding, the lease expires and the job restarts from its seed elsewhere. If a job is completed twice, the two results must be identical, or the launch halts.
   - **Qualification.** A machine qualifies for a launch only if it reproduces, bit for bit, at least 20 jobs at the launch's code identity, covering every job kind it will run, against the reference X2. The operator approves each machine's entry in the launch's machine register once. A qualified machine may join or leave a running launch, and the operator's go for the launch covers it.
   - **A continuing check.** When more than one machine took part in a phase, the phase's nondeterminism check re-executes its sampled job on a machine other than the one that first ran it.
   - **Cost.** Each machine's participation is charged at its measured relative throughput, from its joining until its last job ends or it leaves. The launch stops dispatching when its declared X2-equivalent allowance is reached, as well as at its wall-clock deadline.
   - **Unchanged.** Phase barriers, the configuration test (run on each machine), memory caps, completion records, resume, mode control and the per-phase projection still apply.

   Decision D32's machine rule becomes this general rule for registered A10 work.

**Unchanged.** No registered quantity, reading, prediction, gate, citation rule or stage ceiling changes. Stage 1's ceiling stays 980 X2-equivalent hours.

**Order.**
1. This text is committed and pushed first. It does not change the code identity.
2. The implementation of items 1, 3 and 4 is committed next, and its code identity is recorded. Before any registered use, item 4's dispatch is rehearsed across the X2 and the workstation on non-registered jobs.
3. Stage 1 then runs from its own checkout at that commit, under section 13.3 as clarified here.

Registered A10 preparation requires a design pin that contains this amendment.

### Amendment A12, part 1, 2026-10-11: the A10 stage 1 reading, specified

**Timing and status.**
- **When it was written:** on 2026-10-10 and 11, during A10 stage 1, while the nominal table family was in validation. The nominal estimation was complete and assembled.
- **What existed:** no A10 run, refinement, arm or label job had started. No A10 output, table value, label or gate result had been read by the operator or the interpreter.
- **How the questions were found:** by two mappings of A10 sections 6 and 9 to 11 and what they inherit, written independently:
  - the interpreter's;
  - the executor's, which read source code and documents only.
- **How the answers were tested:** two readers were built from a draft of this text, independently and blind to each other, and run on two non-registered fixtures generated by the instrument's own code paths:
  - one with degenerate outcomes;
  - one with varied outcomes, with crossings, successions and finite intervals.
  
  Every difference between their results traced to a point the draft had left open. Each such point is resolved below (items 6, 16 to 21), and on the final draft the two readers agreed on every shared value.
- **What the answers depend on:** none of them depends on an outcome, and nothing is adjusted toward a v2.0 figure or an R4 result.

**Reason.**
- A10 sections 6, 9, 10 and 11 name the stage 1 reading's quantities, readings and predictions. They inherit A6, A8 and A9.
- The mappings and the test builds found points they leave undetermined, or that A10's changes reopen, among them:
  - the paired comparison with R4;
  - P9 and P10's scope;
  - A9 under capability-dependent welfare production;
  - the staged sensitivity families;
  - the random-number streams;
  - the order of runs inside cells.
- This amendment fixes each one before any input to the stage 1 reading exists.

**The resolutions.**

1. **A9 under C2.**
   - **The quantities:** A9 is computed on R1′ with two resource quantities:
     - **(a)** A9's registered index, r_eff = 0.9 + 0.12(s − 1/6), unchanged. It measures the executed welfare allocation on the capability-1 scale, which keeps the comparison with the R4 check.
     - **(b)** the realized resource level under C2, r_eff′ = 0.88 + 0.12·g(c_t)·s, where c_t is the capability in force at that step (item 20). Its capability path is verified against the recorded transitions. (b) is primary for A9's reading rule.
     - **The difference** (b) − (a), the welfare that capability adds, is reported descriptively, per stratum.
   - **Unchanged:** A9's strata, summaries, balanced-step share and record.
   - **Its reading rule** reads "at the balanced welfare level" only where every living-start step of every run in the stratum is at the balanced share and capability 1.
   - **Why:** A9 states its purpose as the realized welfare level. Under C2, (a) equals the realized level only at capability 1.

2. **P5's reference.** P5 uses A8 item 1's values and A8 item 2's rule. A10 section 11 cites "A8 item 2's values", which is a cross-reference error.

3. **P9** pools fire rates over rr, as cap\* and A8 item 3 do.

4. **P10's cells** are the 27 cells of R1′'s main grid, the R1 grid of section 6. The 9 refinement cells are reported descriptively. "At least 0.95" is inclusive. The per-run quantity is the recorded `a10_diagnostics.mean_theta`.

5. **R1′ against R4, the paired comparison** (A10 section 10).
   - **Pairing:**
     - within each R1 cell (one rr and one α), on the main and refinement grids, seed indices are drawn with replacement;
     - each drawn index takes its R1′ run and its R4 counterpart together;
     - each side's boundary is computed by A8 item 5's rule, pooled over α.
   - **Before any arithmetic:** every R1′ run's counterpart is rebuilt from its recorded seed source and verified against the R4 manifests and durable records. A missing or mismatched pair is a finding.
   - **Censoring:**
     - a resample whose boundary has no crossing takes the conservative grid end: 0.055 when censored below, and 0.066 above;
     - if more than (1 − 0.95)/2 = 0.025 of resamples have a censored boundary on either side, the comparison reads "undetermined";
     - the number of censored resamples is reported.
   - **The point estimate:** if either side's point boundary has no crossing, the comparison reads "undetermined".
   - **The margin,** inclusive at ±0.002, as in A6's boundary convention:
     - **"Unchanged":** the interval lies within [−0.002, +0.002];
     - **"Moved lower":** its upper end is below −0.002;
     - **"Moved higher":** its lower end is above +0.002;
     - **"Inconclusive":** otherwise.

6. **Random-number streams and run order.** Every interval uses 50,000 resamples and quantiles by `inverted_cdf`. The streams are fixed exactly, so that the reading reproduces bit for bit:
   - **R1′'s boundary and R2′'s location against v2.0:** A8 item 4's schedule, as the R4 main reading's reader implements it (sha256 88d8a21b3467afd65738c54181218d8710e847fbfb0f9dc3e1349539c3dc783d):
     - one `default_rng(20261004)`;
     - cells in sorted order of (category, rr, α, capability);
     - runs within a cell sorted by (seed, job identifier);
     - one `integers(0, n, size=(50000, n))` draw per cell, in that order.
   - **R1′ against R4:**
     - one `default_rng(20261010)`;
     - the R1 and refinement cells in sorted order of (category, rr, α);
     - pairs within a cell sorted by (seed, R1′ job identifier);
     - one `integers(0, n, size=(50000, n))` draw per cell, applied to both members of each pair.
   - **A10's arms:** `reading_a6`'s comparison helpers, which create one generator per comparison call, with seed 20261011 in place of their default 20260929. Comparisons are called in sorted order of their identity.
   - **A6 on the corrected instrument:** `reading_a6`'s helpers unchanged, with seed 20260929.
   - **Run order within a cell, for both sensitivity families,** on both the arm and the nominal side: runs are ordered by job identifier before `reading_a6` builds its cells. The registered R4 A6 reading did the same (its reader's sha256 is 3b9725ef2096dcb52c3d77c1e0d031d2875f1a55f081f95275ea445d7936e3ab). The helpers take records in the order they are given.

7. **The sensitivity families' undefined-resample threshold** follows each family's level: (1 − level)/2. That gives 0.05/(2 × 18) for A10's arms, and 0.05/(2 × 33) for A6.

8. **The staged families.**
   - **What runs when:** stage 1 reads 12 of A10's 18 headline comparisons (the k\* arms) and 25 of A6's 33 (the weight corners and the horizon). The rest run in stage 2.
   - **Levels:** both families keep their registered sizes and levels.
   - **Sealing:** stage 1's comparisons are sealed as a stage 1 sensitivity component. Stage 2's are sealed separately, and stage 1's verdicts are not recomputed.
   - **Seed convergence:** A6's convergence quantities are computed on A10's main runs and sealed in the stage 1 component. The R4 A6 reading's seal is not reused.

9. **cap\* materiality** follows A6's discrete convention:
   - **"Moves materially":** the interval's upper end is at most −1 step, or its lower end at least +1 step;
   - **"Robust":** exactly [0, 0];
   - **"Inconclusive":** otherwise.

10. **The shadow decision** (A10 section 9, item 1).
    - **Which reviews count:** those whose recorded plans include an available immediate plan and at least one available waiting plan, either a later yield or a hold. Admission doesn't restrict this.
    - **What is reported per R2′ cell:** the shares of the shadow decision's three outcomes (immediate yield, later yield, hold), with numerator and denominator. "The share whose shadow decision yields" is the immediate-yield share.
    - **Pooling:** over eligible reviews in the cell.
    - **Periods:** period 1 is the review epoch with origin 0. Later epochs are pooled.
    - **An empty denominator** reads "not estimable", never zero.

11. **Θ and bandwidth** (A10 section 9, item 2) use the conventions the runs record:
    - Θ = 1 by exact equality;
    - bandwidth "at the floor" when the raw bandwidth is at or below b_min′.

12. **Per-cell summaries of the A10 diagnostics** (A10 section 9) follow A8 item 8:
    - the equal-run mean of each per-run scalar, for R1′, its refinement grid and R2′;
    - transitions as the equal-run mean count, plus the count of runs at each final capability.

    They are descriptive, with no intervals. The arms' per-run records are retained, but their summaries are not registered quantities.

13. **Missing side values** (A8 item 8). A run with no estimable observation of a side value contributes nothing to that value's cell mean. The cell mean averages the runs where it is defined, and reports how many those are. If no run defines it, it reads "not estimable".

14. **The author's expectations** (A10 section 11; decided by the operator on 2026-10-10).
    - **How they are reported:** quoted verbatim beside the registered quantities they refer to.
    - **Not scored:** they are not scored right or wrong. A10 states them as "a prediction, not a criterion", and several are hedged.
    - **The ban:** the report never describes one as confirmed, met or borne out.

15. **Citation dependencies of P4 to P10** (decided by the operator on 2026-10-10).
    - **Reporting:** a prediction's truth is always reported. Its citation follows the gates of the claim it concerns.
    - **The mapping:**
      - P4 and P5: R1;
      - P6: R1 for R1′, together with R4's existing R1 status;
      - P7: R2;
      - P8 and P9: R2_cliff, as R4's P3;
      - P10: R1, together with G4.1's Θ check.
    - **Sensitivity verdicts** qualify claims as A6 directs.
    - **Reasons for non-citation** are reported, the first that applies, in this order:
      1. a reading that is not registered;
      2. R4's status not established;
      3. R4 not citable;
      4. the failing gates;
      5. the gates that are not testable.

      A required gate that is missing, or in any state other than passed or not testable, counts as failed. D23's G3.3 zero-fire exception applies only to the R2 fire rates and P7.

16. **R4's producer.** The R4 counterparts for R1′ against R4 are accepted at R4's own registered producer identity, which is the identity the R4 main reading verified.
    - Every R4 output and completion record is hash-checked against its R4 manifest. Only the R1 and refinement counterparts' final populations are read.
    - The rule that inputs come from the A10 identity applies to the A10 inputs only.

17. **P6 when its comparison is undetermined.** If R1′ against R4 reads "undetermined", P6 reads "undetermined", not right or wrong. Otherwise P6 is right unless the reading is "moved higher".

18. **R4's citation status for P6.**
    - **The source:** R4's R1 status comes from the registered R4 gate evaluation, identified by its hash among the reading's inputs.
    - **If it can't be established,** P6 is not citable. Its truth is still reported.

19. **Ranking flags that cannot be joined** (A8 item 9).
    - **In a registered reading,** every chosen-rule step's ranking flag must join to a row of the pinned A10 family. A step that cannot be joined is a refusal, not a category.
    - **Outside registered readings,** for test fixtures only, such steps are counted as "not joined". They are kept apart from unavailable, absorbed and unresolved-ordering steps.

20. **The capability in A9's quantity (b)** at each living-start step is the capability the engine used for that step's welfare increment. That is the step's recorded capability; at a handover step, it is the successor's.

21. **The reader's input contract** is fixed in its build specification, and the reading records it:
    - the names inside the nominal entry;
    - the calibration;
    - R4's gate result;
    - the forms accepted only from test fixtures, which a registered reading refuses.

    It changes no computation.

**Unchanged.**
- A12 part 1 changes no registered quantity, reading, prediction, gate or citation rule of R1, R2, A6 or A9 under R4.
- It changes nothing in A10's instrument, runs or tables, except for item 1's added A9 quantity.
- Anything else computed is labelled exploratory.

**Order.**
- This text is committed and pushed. It does not change the code identity.
- The stage 1 reading's registration is the commit that adds this amendment. The reading is computed sealed after stage 1's runs complete, and opened on the operator's go.

### Amendment A12, part 2, 2026-10-11: execution fixes, and their adoption mid-stage

**Timing and status.**
- **When it was written:** on 2026-10-10 and 11, while the A10 nominal validation was running at code identity `c19b54f5`.
- **What existed:** the A10 nominal estimation was complete. No validation, label or run output had been read by the operator or the interpreter.
- **What informed it:** progress counts, configuration measurements, phase timings and cost. Nothing else.
- **The changes,** E1 to E3 below, change scheduling only, and alter no simulation result.
- **The implementation:** built and tested before this text was committed, in a review worktree, with the full test suite and an independent rerun of its new tests. It is committed after this text, as the order below sets out.

**What was found.**
1. **Local hosts' worker candidates.** The A4 and A5 configuration profiles, which A10's validation and labels inherit, list local candidates `[2, 4]`. The X2 has `[8, 12, 16, 24, 32]`, and A10's estimation and runs have `[2, 4, 8, 12]`.
   - **The effect:** the workstation's WSL host and the old box can run at most 4 workers in validation and labels. In the estimation's configuration measurements, more workers gave them about 40 and 12 percent more throughput.
   - **Why it is a defect:** it falls short of the operator's standing execution requirement (`AGENTS.md`, 2026-09-27) that the pre-launch configuration test cover worker counts up to each host's mode cap. That makes it a defect in execution, under A11 item 3.
2. **The cross-host check's host.** A phase's nondeterminism check went to whichever eligible host claimed it first. At the end of the validation's fit phase, that was the slowest host, and the other hosts waited at the barrier for about 15 minutes.
3. **The X2 profile and the hostname.** The X2 profile is tied to the current X2's hostname. A second X2 could join only with the local profile, which in validation and labels limits it to 4 workers.

**The changes,** at a new code identity:
- **E1:** A10's validation and labels give local hosts the candidates `[2, 4, 8, 12]`, as A10's estimation and runs do. R4's profiles are unchanged.
- **E2:** a phase's check goes to the eligible host, other than the original, with the highest registered relative throughput. That host gets a bounded preference window, after which any eligible host may take the check. Unchanged:
  - which job is sampled;
  - the original-host exclusion;
  - the comparison;
  - every record of the check.
- **E3:** a host's profile comes from its approved register entry and launch arguments, not its hostname. The model-service stand-down becomes a per-host setting, with the current X2's default unchanged. The reference machine for accounting stays the current X2.

**Extending A11 item 3.**
- **The extension:** A11 item 3 admits defect repairs. It is extended to execution-only changes: changes to scheduling, dispatch, configuration candidates or host profiles that alter no simulation result. They come under the same compatibility record and the same byte-identical re-execution proof.
- **What it is for:** E2 and E3 need it. E1 qualifies under item 3 as a defect repair in any case.
- **What a failure means:** a proof that fails ends the attempt, and the affected work stays at its producing identity.

**What the change touches.**
- **Exact-hash pins:** the A2 compatibility record pins `v3/production_runner.py` and `v3/service.py` by exact hash. Their new hashes are entered with these reasons:
  - production_runner.py: E1's candidate handling and E3's hostname-free profile check;
  - service.py: E3's per-host model service.

  No other pinned file changes.
- **Sealed specs:** new launch specs record the changed configuration field, `workers_local`. No plan hash, seed, job set or cost class changes.

**Order** (A11 item 3 and runbook section 14):
1. This text is committed and pushed. It does not change the code identity.
2. **The validation launch finishes at `c19b54f5`.**
   - The family is published there (runbook section 6), and the family identity record gets its record-only commit there (section 7).
   - No unfinished launch is resumed at the new identity.
3. **The code commit:** E1 to E3 and the two re-pins are committed on main, and the new code identity is recorded.
4. **A non-registered rehearsal at the new identity** checks:
   - E1's local candidates;
   - E2's check assignment and its fallback;
   - E3's X2 profile with the service off, on a host not named as the X2.
5. **The compatibility proof:**
   - It runs from a fresh checkout at the new commit.
   - It covers the completed estimation and validation roots: two jobs per phase, capability and setting, chosen by A11's rule before any re-execution, all byte-identical.
   - The interpreter reviews it, and the operator approves it. It is committed, and the same bytes are committed publicly.
   - Its cost is charged to the stage 1 operations ledger.
6. **Labels and the five run launches** run from a fresh execution checkout at the record's commit, with new roots. Each needs its own qualification, register approvals, pre-launch configuration test and the operator's go.

**Unchanged.**
- No registered quantity, reading, prediction, gate, citation rule, ceiling or allocation changes.
- Stage 1's 980 X2-equivalent hours stand.
- A12 part 2 changes nothing in the outputs it carries forward.
- If the proof fails, labels and the runs proceed at `c19b54f5`.

**Clarified, 2026-10-12: identifiers at the new identity.**
- **The sentence it clarifies:** "No plan hash, seed, job set or cost class changes", under "What the change touches". It describes E1's change to a sealed spec at a fixed code identity, where it holds.
- **What changes with the identity, and why:** adoption moves the labels and the five runs to a new code identity, with new roots, through A11 item 3. Some identifiers include the producing code identity, the design pin or absolute input paths. That is by design, because it is how a root is bound to the code that produced it. Moving to a new identity changes them:
  - the A5 label plan's hash, and with it each label job's identifier and the envelope seed derived from that identifier, which the simulation does not use;
  - the code identity and design pin fields of every new spec.
- **What the adoption does not change:** each is checked before launch.
  - **Every job's scientific inputs, and the seed its simulation uses.**
  - **The five run families:** 53,100 jobs, with unchanged identifiers and seeds. Neither includes the code identity. The new specs' job lists must be identical to the lists built at `c19b54f5`.
  - **The labels:** 756 label jobs, each with its unchanged table, replicate and seed.
  - **The cost classes.**
- **The pins:**
  - **The new launches:** labels and the five runs pin the commit that carries this clarification as their design registration.
  - **The completed estimation and validation:** they keep their original pin.
  - **The stage 1 reading:** it stays registered at `93474e00`.

### Amendment A13, 2026-10-16: a targeted validation extension for the A10 nominal family, a bounded admission rule, and the revised order of A12 part 2

**Timing, and what was known.**

- **When it was written:** 2026-10-16.
  - The A10 nominal validation completed at code identity `c19b54f5` (9,204 jobs; `check_done` passed; 260.04 X2-equivalent hours).
  - The section 6 publication then refused its candidate.
  - Both parts of this amendment followed that refusal.
- **What was known, from the publication diagnosis** (the executor's report of 2026-10-16):
  - 19,450 primary rows were estimated and 50 `not_estimable`.
  - All 50 carry "A4 availability floor failed". They are on the plain route, in 10 of 2,835 source jobs, and each fails the low-population component.
  - Each row's merged population-0 cell (C0) is `unresolved`, and no cell has a `violation`.
  - For each, the data-independent term of the empirical-Bernstein radius exceeds τ.
  - All 50 C0 visit-weighted safeguards passed. That implies each C0 cell's visit-weighted residual estimate lies within τ. It says nothing directly about the Bernstein trajectory mean or the fitted C0 value. It is outcome information, and it is disclosed here.
- **What was not known:**
  - **Values:** neither the operator nor the interpreter read any table value, continuation value, flow, survival or other scientific quantity.
  - **Cell detail** is executor-only.
  - **The executor's knowledge:** it holds the original visit counts. Every executor-side choice below is therefore fixed mechanically, and R_max depends on cost classes alone.
- **Prospectiveness:**
  - **Part 1** is prospective for its fresh observations, conditional on a decision to extend that was itself informed by an outcome.
  - **Part 2** is retrospective for the nominal family and prospective for later families.
- **Certification and adoption:** two certifiers from different model families reviewed the text blind to each other, over four rounds. Every required repair is incorporated. The operator approved the final text on 2026-10-16.
- **Code citations** refer to `simulation/v3/` at commit `d73acfb1`.
- **The original result stands as reported:**
  - The refusal is preserved and reported.
  - Success under this amendment is never described as success of the original registration.
  - Nominal-family results are labeled as produced under A13, an amendment informed by an outcome.

**Assumptions.**

1. **Independent streams:** the pseudo-random streams behave as independent ideal generators. The seed construction in item 3 establishes that the integers are disjoint; independence rests on this assumption.
2. **Registered horizons and initial law:** each trajectory runs its full registered horizon, burn plus measure (`offline_estimator.py:48`, `:60`), from the archived initial law (`context.py:55`).
3. **The distribution of visiting trajectories:**
   - **Trajectories:** they are independent across the pair (replicate number, batch index), and identically distributed under the archived initial law.
   - **Visits:** whether a trajectory visits C0 is a function of that trajectory alone.
   - **The stop:** it reads only visit counts.
   - **Hence:** the marks (S_i, N_i) of the first N\* visiting trajectories, taken in that order, are independent and identically distributed under the law conditional on a visit. Both certification halves proved this in the first round.

**Part 1: a targeted extension of plain validation.**

1. **Eligibility.** A row is eligible only if it is a **primary** row of the refused candidate and all of these hold:
   - it is on the plain route;
   - its status is `not_estimable`, with the reason "A4 availability floor failed";
   - it passed its base screens;
   - `validated_support_size > 0`;
   - `sensitivity.passed` is not `False`. It is `None` for rows not selected for sensitivity (`table_validation_a4.py:683` to `:699`).
   - its floor flags are `living_ok = True`, `low_assessed = True` and `low_ok = False`;
   - its C0 classification is `unresolved`;
   - no cell has a `violation`;
   - its C0 fit is published;
   - the arithmetic condition holds:
     - **The condition:** 7wL / (3(n_orig − 1)) > τ.
     - **The count:** n_orig is C0's original `n_traj` over replicates 1 to 3 (`table_validation_a4.py:532` to `:533`, `:558` to `:565`).
     - **Small counts:** n_orig < 2 satisfies the condition, because the code then gives no radius (`continuation_validation.py:288`).
     - **The other quantities:** w, τ, M and α are the row's own.

   The executor evaluates eligibility from the sealed fit records and the original validation records, and records it as one boolean per row. The eligible set and its source jobs are recorded by identifier only. E is the set's size.
2. **The sample size N\*.**
   - **The formula:** with c = 7wL / (3τ), N\* = 1 + ⌈2c⌉, computed with the code's own expression in `continuation_validation.empirical_bernstein`. A final check confirms that the deterministic term at N\* is at most τ/2.
   - **The constants:**
     - L = log(4M/α), with α = 0.05;
     - τ = 0.05 × the row's flow range;
     - w is the row's a priori width, from the A1 values and the fitted C0 through vmax;
     - M is the family-wide count pinned in the plan (`table_validation_a4.py:433`): every primary and sensitivity plain row's above-zero published A1 cells, plus one C0 allocation per row, whether or not C0 is published (`:289` to `:302`; `continuation_validation.py:504` to `:512`).

     All were fixed before validation, and none depends on a validation or extension outcome.
   - **Why τ/2:** it splits the tolerance equally between the deterministic term and the data-dependent term.
     - **The exact relation:** N\* − 1 = ⌈2c⌉. Compare n_min − 1 = ⌈c⌉, where n_min = 1 + ⌈c⌉ is the smallest count at which certification is possible at all, attained in the zero-mean, zero-variance case (`continuation_validation.py:293`, `:295`).
     - **What the fraction affects:** power and cost, never the false-certification rate.
   - **The consequence:** eligibility gives c > n_orig − 1, so N\* ≥ 2·n_orig. Extrapolating from each row's original visit rate (three replicates), an eligible row would need at least six extension replicates. This is an extrapolation, not an expectation: the future visit probability is unknown.
   - **Executor-only:** N\* and each row's reach depend on vmax.
3. **The extension's data.**
   - **Its own phase:** a new phase, `validate_plain_ext`, runs for the eligible rows' source jobs only.
     - Its outputs never enter the validate index (`_index_phase`, `_combine_plain`), which would pool them into every row of those jobs (`table_validation_a4.py:558` to `:564`, `:598` to `:603`).
     - It reads the fit and A1 outputs and the eligible set. The eligible set derives from the original data, and the conditional bound in item 9 covers that.
     - It never reads the original validation statistics.
   - **Replicates:** each has the registered size, 2,048 trajectories in 32 groups of 64, at the registered horizons.
   - **Seeds:** ext_seed(s, r) = 2^60 + `_truncated_sha("v3_R_validate_ext", s, "/", r)`, for A1 job seed s and extension replicate r.
     - **Unambiguous input:** the fixed tag and the separator give a distinct hashed string for each pair (s, r).
     - **Collisions:** a collision of the hash itself is excluded by the runtime check below.
     - **Disjoint ranges:** the range [2^60, 2^61) lies outside every `_truncated_sha` seed, which is below 2^60 (`continuation_validation.py:55` to `:60`). It also lies outside every `stable_job` and qualification seed, which lie in [2^128, 2^129) (`artifacts.py:141`; `qualification_a11.py:75`).
   - **The seed check, before any extension simulation:**
     - the full seed manifest for replicates 4 to 3 + R_max is frozen;
     - its seeds must be pairwise distinct;
     - none may equal any registered, planning, probe, rehearsal or qualification seed;
     - any collision halts the run.
   - **Reserved for later:** the range is recorded as reserved, and later forbidden sets include these seeds, including A5, stage 2 and D4. Configuration tests never use extension seeds.
4. **The stop.**
   - **Order:** trajectories are taken in order of (replicate number, batch index), with replicates evaluated in order, never in completion order.
   - **Visits:** the stop reads per-row visit counts only. A visit means at least one covered living-source transition from C0 (`continuation_validation.py:165`, `:254` to `:257`).
   - **Per source job:** a job stops after the first replicate in which every one of its eligible rows has at least N\* visiting trajectories, or at R_max replicates, whichever comes first. No row is truncated because another row finished.
   - **Records:** per-trajectory (S_i, N_i) are recorded in order for each eligible C0 cell. The existing statistics lose that order (`continuation_validation.py:258`).
5. **R_max.**
   - **The rule:** R_max is the largest integer R ≤ 16 such that the extension's simulation cost is at most 15 X2-equivalent hours, at R replicates for each source job, priced from the jobs' registered cost classes.
   - **When it is fixed:** mechanically, before launch, never from visit counts.
   - **Overhead:** qualification, the configuration test and dispatch are outside the cap and charged separately to the stage 1 ledger.
   - **No launch below 6:** if R_max < 6, the extension does not launch and its rows go to Part 2. This is a declared policy floor, matching item 2's extrapolated six replicates. It does not claim that a row could not reach N\*.
   - **Impossible rows:** any row with N\* > 2,048·R_max is flagged before launch as deterministically impossible.
6. **The test.**
   - **What it runs on:** for each eligible row, the registered two-sided empirical-Bernstein test is applied to exactly the first N\* visiting trajectories of the extension data alone. It uses the same w, τ, M and α, with the visit-weighted safeguard on the same trajectories.
   - **What it never uses:** the original replicates are never pooled in, and the original `unresolved` result is not reused as evidence. That result is preserved in the audit record.
   - **Outcomes:**
     - a row whose C0 certifies, and whose safeguard passes, gains C0 support;
     - a row that does not reach N\* within R_max stays `not_estimable`;
     - so does a row whose re-test is `unresolved` or `violation`.
7. **A halted extension.**
   - **A scientific halt,** under the runner's halt rules, certifies nothing. It spends the one round, and its rows go to Part 2.
   - **An infrastructure interruption** resumes under the runner's supported procedure. Completed replicates are kept, and an in-flight replicate restarts from its original seed.
8. **Re-assembly.**
   - **For an eligible row:**
     - only the C0 decision is replaced;
     - its other cells come from the original outputs only;
     - its validated support is recomputed;
     - the registered floor is re-applied to the unchanged census. Adding C0 changes the floor fractions in one direction only (`continuation_validation.py:561` to `:570`).
   - **Everything else is carried forward exactly:** every ineligible row, the sensitivity processing and the sensitivity siblings. The run halts unless every ineligible row, and its sidecar entry, is byte-identical to the refused candidate's.
   - **Marking:** rows certified by the extension carry a row-level marker.
9. **The error accounting.**
   - **Definitions:**
     - H is the pinned A1 family together with the sealed validation plan, all fixed before any validation data.
     - D₀ is H plus the original validation and census data.
     - P is the number of primary plain rows in the sealed plan. It is fixed by the plan, because `prepare` binds each job's route from the A1 output (`table_validation_a4.py:412` to `:423`, `:440` to `:442`). It is not fixed by the design, because the route is chosen during A1 estimation (`tables_a10.py:84`; `offline_estimator.py:195` to `:197`).
   - **The original tests:** P(any original false certification | H) ≤ α. That includes the E unresolved C0 tests, whose allocation is spent, not refunded.
   - **The extension:** P(any extension false certification | D₀) ≤ E(D₀)·α/M.
   - **The family, given the fitted family:** P(any false certification | H) ≤ α(1 + P/M). Since E ≤ P ≤ M, this never exceeds 2α.
   - **Unconditionally over fitting:** the bound is 2α = 0.10.
   - **What is reported:**
     - for this family, the certificate's "at least 0.95" becomes "at least 1 − α(1 + P/M), given the fitted family";
     - P and M are recorded side by side;
     - the conditional additional figure α·E/M is reported beside them.
   - **Scope:** the statement covers plain validation. FV validation is unchanged (`table_validation_a4.py:652`). This is an exception to "Unchanged".
10. **One round only.** There is no second extension round for this family.

**Part 2: a bounded admission rule for residual rows.**

11. **What unavailability does.** A `not_estimable` row makes its rule unavailable in its lookup context. Its effect differs across the three branches (`integration.py`):
    - **Ordinary allocation:** an unavailable rule leaves the comparison. The balanced fallback applies only when no admissible scoreable rule remains (`:253` to `:258`).
    - **Survival-first:** if no minimum-risk rule is scoreable, the first minimum-risk rule is taken, with no balanced fallback (`:243` to `:252`).
    - **Yield review:** unavailable plans are dropped, and the review holds if none remain (`:283` to `:317`).

    **No behavioral bound is claimed.** No row cap bounds the effect on adaptive runs.
12. **The rule.** A family may be admitted for registered use with residual `not_estimable` rows only if all of the following hold.
    - **(a) The cap:**
      - at most **0.1 percent of the family's own primary rows, rounded down**, never a fixed count: for the A10 nominal family, 19 of 19,500;
      - no allowance for a family with fewer than 1,000 primary rows;
      - **at most one admitted row per lookup context**, where the context is the canonical row key without the rule's identity (`production_tables.py:17` to `:32`);
      - **none for the balanced witness rule** (`rules[0]`, `integration.py:82`, `:257` to `:258`).

      The per-context limit and the balanced exclusion are administrative limits on how many comparison sets an admission touches. They are policy choices, with no power or bias guarantee. For the nominal family, 31 extension certifications are necessary for admission, but not sufficient, because the per-context limit can bind.
    - **(b) The rows:** each admitted row:
      - failed only through the availability floor, after Part 1;
      - has `validated_support_size > 0`;
      - has no `violation` in any cell, including the extension's re-test;
      - passed its base screens;
      - has `sensitivity.passed` not `False`.
    - **(c) Binding:**
      - **The manifest:** the admitted set is bound in the family manifest by identifier and hash.
      - **The loader:**
        - checks that binding;
        - re-checks the cap, the per-context limit and the balanced exclusion;
        - keeps its existing sensitivity and support checks (`production_tables.py:120` to `:123`, `:127` to `:129`);
        - rejects any `not_estimable` row outside the set.
      - **Status:** admitted rows remain `not_estimable` and unavailable, and are never relabeled `estimated`.
      - **This is new code:** the present loader rejects every residual row (`production_tables.py:115` to `:129`).
    - **(d) Recording:** every registered run records, per run and per branch, the evaluated decisions. Absorbed padding steps are excluded (`allocation_evaluated: False`, `integration.py:368`).
      - **The decision incidence:**
        - **Numerator:** evaluated decisions in which, for the reason `missing_or_not_estimable_row`, any of these happened:
          - at least one rule or plan was excluded;
          - the review held;
          - on the survival-first branch, the selected rule's score was unavailable. A unique minimum-risk rule with no score is selected before the availability filter (`integration.py:246`, `:252`, `:253`), so it may exclude nothing and still be affected.
        - **Denominator:** that branch's evaluated decisions. These are allocation decisions with `allocation_evaluated` true, survival-first selections, and evaluated yield reviews.
      - **Separately:**
        - the count of excluded rules or plans;
        - balanced fallbacks, by reason;
        - survival-first selections with an unavailable score.
      - **This is new recording code:** the present counters (`production_runner.py:217` to `:225`) do not give these rates.
    - **(e) Reporting:**
      - **Incidence:** the stage reading reports the decision incidence for every registered quantity, from predefined contributing runs, as pooled numerators and denominators plus per-run rates. A zero denominator is marked unassessed.
      - **The flag:** any quantity with **any nonzero** incidence on any branch is flagged as affected by table unavailability.
      - **Flagged quantities** are reported with the flag, under the reading's existing rules. They are never dropped or re-estimated.
      - **Unflagged quantities** are never described as certified unaffected.
13. **Scope:**
    - the rows of the A10 nominal family that remain `not_estimable` after Part 1's single round, or after a halted or unlaunched extension;
    - every table family whose validation launch had not started when this amendment was committed, such as stage 2's variant families and D4's reruns.

    It never applies to other already-validated families, and it never gives a later family an unspecified extension round.

    **Disclosure:** for the nominal family, Part 2 relaxes a registered admission rule after its outcome, and was written knowing E = 50. For later families it is prospective.

**The order of steps.**

This replaces A12 part 2's steps 2 to 6. It supersedes A12's clarification of 2026-10-12 where the two conflict: the amended family's bytes and provenance change, while the job configurations, identifiers and seeds below stay the same. A12's sentence "If the proof fails, labels and the runs proceed at `c19b54f5`" is void, because no admissible family exists there. A no-launch, a failed proof or a failed admission halts all downstream work, and the limit is reported.

1. **The text:**
   - This amendment, re-certified on its changed items and approved by the operator, is committed and pushed. That commit is **the A13 commit**.
   - It does not change the code identity.
   - Every later launch pins the A13 commit, and requires the design note in its execution checkout to be byte-identical to the note at that commit.
2. **The code commit.** Everything below is committed together on main.
   - **What it contains:**
     - A13 Part 1: the phase, eligibility, N\*, the seed manifest check and re-assembly;
     - Part 2: the admission binding, the loader checks and the incidence recording;
     - **historical pin verification:** carried-forward plans, and the publication of their stages, are verified by ancestry and committed hash, not against the working-tree note (`artifacts.py:227` to `:235`; `table_validation_a4.py:745` to `:746`). Verification of current launches stays strict, against the A13 pin;
     - A12 part 2's E1 to E3.
   - **The additive rule:**
     - No existing fit, validate, census or estimation function is edited.
     - Changes to the controller, the run summary and the loader are additive, and inert on a family with no admitted rows.
     - This is confirmed by diff review and by step 3's equivalence check.
   - **Records:** the A2 re-pins name every changed pinned file and its reason, and the new code identity is recorded.
   - **The authority:** A13 extends A11 item 3's compatibility path to this commit. Item 3's proof admits the unchanged computations, and A13 alone admits the new phase, assembly, admission rule and recording.
3. **A non-registered rehearsal** at the new identity, on rehearsal seeds outside the reserved range:
   - A12's E1 to E3 checks;
   - the extension phase's dispatch on a small non-registered plan;
   - qualification;
   - **run-side equivalence:**
     - **The runs:** sampled run jobs, run at `c19b54f5` and at the new identity, agree byte for byte on every field of the `result` payload that already existed. The output envelope's code hash, runtime, timings and peak memory are excluded: they are not required to agree (`production_runner.py:262` to `:264`).
     - **The loader** behaves identically on a family with no admitted rows.
     - **A mismatch** halts the sequence before step 4.
   - **the label step's receipt check:** A5's preparation runs against a rehearsal receipt of the amended form (step 7).

   Its overhead is charged to the stage 1 ledger.
4. **The A11 compatibility proof.**
   - **What it covers:** the completed estimation and validation roots, carried forward byte-identically, from a fresh checkout at the new commit.
   - **The selection:** 434 jobs (90 estimation, 344 validation), selected by A11's rule. The executor verifies that count against the frozen strata.
   - **Before it runs:**
     - its cost is projected and approved, and charged to the stage 1 ledger;
     - a configuration test is run;
     - on an X2, the model server is stood down (`llm down`), supervised, and restored on every exit.
   - **Review and approval:** the interpreter reviews it and the operator approves it. It is committed, and the same bytes are committed publicly.
   - **If the proof fails,** the sequence halts.
5. **The extension's records,** in its fresh execution checkout at the proof record's commit, before launch:
   - the eligible set, by identifier;
   - E, P, M and R_max;
   - the impossible-row flags;
   - the frozen seed manifest and its check.

   N\* and per-row reach stay executor-only. If R_max < 6, the extension does not launch and Part 2 applies.
6. **The extension launch.**
   - **Its terms:** registered, with its own plan, cost cap (Part 1, item 5), register approvals and operator go.
   - **The checkout:** that execution checkout, with a new root.
   - **Before it runs:** qualification, the pre-launch configuration test, and `llm down` on the X2, supervised and restored on every exit.
   - **Its pin:** the A13 commit.
   - **A halt:** item 7 applies.
7. **Family publication.**
   - **Where:** at the exact configured target path, `v3/runs/a10_stage1/nominal/v3_rerun_tables_A10.json`. That path has never been written, so all 53,100 run job identifiers and seeds stay unchanged (`tables_a10.py:211` to `:213`, `:225` to `:230`, `:264` to `:272`; `artifacts.py:129` to `:141`).
   - **The guard:** the existing no-overwrite guard applies (`table_validation_a4.py:803` to `:806`).
   - **Part 2 first:** if any row still fails Part 1, Part 2's conditions are checked and recorded before publication. If they are not met, the family is not published, and downstream work halts.
   - **The identity record:** made at the new identity, with section 7's exact-file and hash approval and the public identity-record commits.
   - **The receipt:**
     - **What it binds:** both plans, both sets of stage hashes and both sets of seeds.
     - **Unchanged fields:** the original plan's `plan_hash` and per-job `stream_seeds`, so that A5's check (`table_labels_a5.py:135` to `:146`) reads the receipt as before.
     - **Added fields:** the extension's plan hash, stage hashes and seeds.
8. **Labels and the five run launches.**
   - **How each runs:**
     - from a fresh execution checkout, with new roots;
     - after its own qualification, register approvals, pre-launch configuration test and operator go;
     - with `llm down` on each X2, supervised and restored on every exit;
     - pinned to the A13 commit.
   - **Job lists:** they are built fresh and verified against reference lists built at `c19b54f5`. If no reference lists exist, they are built first, in a fresh `d73acfb1` checkout with the same path strings.
   - **What stays the same:**
     - the 53,100 run jobs' configurations, identifiers and seeds;
     - the 756 label jobs' tables, replicates and seeds;
     - the cost classes.
   - **What changes:**
     - the table family's bytes and provenance, which this amendment amends;
     - the A5 label plan's hash, with its job identifiers and envelope seeds (as in A12's clarification);
     - the code identity and the pins.

**Unchanged.**

- **No registered rule changes**, whether quantity, prediction, gate, citation rule or reading rule, except for three things:
  - Part 2(e)'s added incidence report and flag;
  - the family error statement in Part 1, item 9;
  - the amended family itself.
- **Also unchanged:** the census, α, τ, the floor's 2 and 5 percent caps, the minimum of 50, and the Bernstein test.
- **The ceiling:** stage 1's 980 X2-equivalent hours stand. The extension, the rehearsal and the proof are charged to the stage 1 ledger. About 689.68 hours remain after estimation and validation, against 384.63 reserved for labels and runs.
- **The stage 1 reading** stays registered at `93474e00`.

**Clarified, 2026-10-16: pricing R_max.**

- **Code citations** refer to `simulation/v3/` at commit `d73acfb1`, as in A13.
- **The sentence it clarifies:** Part 1, item 5's "priced from the jobs' registered cost classes".
  - **Why it needs a rule:** the registered cost classes are scheduling weights for a whole plain-validation bundle: one fit, three validation replicates and one census (`pilot_a10.py:222`; `multihost_a11.py:31` to `:50`). They are not prices for one replicate, and nothing in item 5 converts them.
  - **How it was found:** by the executor at the start of the code build, before any A13 code or extension data existed. The finding is F1.
- **The source:** the registered A10 cost projection, file `a10_pilot_P2_projection_2026-10-08.json`.
  - **Its identity:** file SHA-256 `78a1d3ac253048c7e077b0e4eb12dd3150fa178cf3e63a24c6f0d87f02a8ad8d`, payload seal `5ca5225967cf08ad5636f98f12d57fa6ccd753a7ae126bff0edcc09f0af3d8a3`.
  - **The check before R_max is computed:** the executor confirms that the payload seal equals the projection seal bound in the sealed validation plan (`multihost_a11.py:73`). A mismatch is a finding.
- **The price:** for source job j, one extension replicate costs B_j / 3 X2-equivalent hours.
  - **B_j:** the projection's conservative per-job figure for j's plain-validation stratum, `{family}.{capability}.{setting}.validate_plain` (`multihost_a11.py:39`, `:49`). It is that stratum's `x2_hours_max` divided by its `jobs`.
  - **Its parts:** `x2_hours_max` already applies the projection's measured, memory-constrained effective workers, its realism factor and its relative throughput (`pilot_a10.py:400`, `:418` to `:425`).
- **R_max:** the largest integer R ≤ 16 such that R · Σ_j B_j / 3 ≤ 15, summed once over each distinct source job of the eligible rows.
- **Why one third:** it is a conservative allocation convention. It attributes the whole bundle, fit and census included, to the three validation replicates, although the extension repeats neither the fit nor the census. It is a pricing rule, not a guarantee about the time any run will take. The maximum, rather than the mean, matches how the registered ceilings were set.
- **What it never uses:** any measured duration of any validation job, any visit count, or any outcome.
- **Reporting:** the executor reports R_max and the total projected cost R_max · Σ_j B_j / 3. Per-stratum prices stay executor-only, under the cost-reporting rule.
- **Metering is unchanged:** actual consumption is metered as for any launch (`multihost_a11.py:266` to `:268`), and charged to the stage 1 ledger.
- **The pin:** later launches pin the commit carrying this clarification, with the design note byte-identical to it there, in place of `8336a1f6`.

### Amendment A14, 2026-10-20: a second and final extension round for the A10 nominal family

**Timing, and what was known.**

- **When it was written:** 2026-10-20, after the A13 round's publication was refused.
  - **The A13 round:** launched 2026-10-19T19:32:53Z on X2-1, single-host, from `plan.json` (plan hash `e30c465ff93d476ef70e1f5573179ad0b616cb724881d1bab73ae05a9af25a62`), at code identity `5df9866f…`, checkout commit `55817036`. It completed at 2026-10-20T01:20:32Z with its same-host nondeterminism check matched and no halt.
  - **Its publication:** at 2026-10-20T11:36Z, A13 Part 2 refused it. No family, receipt or sidecar was written.
  - **The sealed admission record:** `v3/runs/a10_stage1/nominal/v3_rerun_tables_A10.a13_round.admission.json`, SHA-256 `87f8b2453e04b178a4f2dcd40c07ae41b9ab06a350a70d5b57e834aa8e5c6dd7`. It records outcome `refused`, cap 19 and residual count 20. The refusal exception, in the publication log, names the cap.
- **What was known** (the executor's publication report and read-only feasibility assessment of 2026-10-20, which give counts and costs only):
  - **The counts:** E = 50 rows were eligible. 30 reached N\*, and all 30 certified and passed the floor. 20 remain `not_estimable`.
  - **The 20 residual rows:**
    - All 20 ran the round's full 16 replicates without reaching N\*.
    - None was tested: `extension_test` returns `unresolved`, reason "N* not reached", before any test is computed (`validation_extension_a13.py:140` to `:142`).
    - None has a violation. They lie in 4 of the 10 source jobs and span 10 lookup contexts.
  - **Two Part 2 conditions fail:**
    - the cap, with 20 residual rows against 19 (`admission_a13.py:47` to `:48`);
    - the one-row-per-context limit, with 5 contexts holding more than one residual row (15 rows in all) (`:57` to `:58`).

    `verify` checks the cap first, so the exception names only the cap. Meeting the context limit needs at least 10 of the 15 shared-context rows to certify. No residual row is a balanced-witness row, and none fails item 12(b).
  - **Foreseeability (inferred, from a model):**
    - **The formal records could not show it:** no row was flagged impossible before launch.
    - **The visit counts could:** a model on the original three-replicate visit counts, which `prepare` reads for eligibility, predicts the same 20 rows, with P(more than 19 residual rows) ≈ 0.996.
    - **The binding limit:** A13 item 5's bound R ≤ 16, not its 15 X2-hour price cap, which alone would have allowed R = 29. Under the model, a first round of about 24 replicates would probably have met every condition.

    The operator and interpreter assess this as a design error in A13 item 5, and in the pre-launch reviews that accepted it: A13's text certifications, the review of the A13 code build, and the interpreter's pre-launch review. The code-build reviewer confirms that its review checked code against item 5 as written and did not question the bound; the rest is the interpreter's attestation.
  - **The assessment's projection** for a second round on fresh data alone (a budget estimate):
    - **Baseline:** P(every Part 2 condition) ≈ 0.97 at R = 23 and ≈ 1.0 at R ≥ 24. This is a plug-in forecast, taking round 1's 30 certified of 30 and 0 violations of 30 as a certification rate of 1 and a violation rate of 0. It is not an assurance.
    - **Sensitivity:** about 0.86 at a certification rate of 0.9 and about 0.56 at 0.8. A 0.03 violation rate alone gives about 0.63, and a single violation in any residual row refuses admission.
    - **The plausible range from 30 observations:** certification as low as about 0.90, and violation as high as about 0.10. Group-level overdispersion relative to the independent, stationary-trajectory model could widen the transition by a few replicates (a guess).
    - **The expected outcome:** about 5 rows stay unreached at every R from 24 to about 96. They lie in 5 distinct contexts, so they would be admitted as residual rows. Success is expected to mean admission with about five residual `not_estimable` rows, not full estimation.
- **What was not known:**
  - **Values:** neither the operator nor the interpreter read any table value, C0 value, continuation value, flow, survival or other scientific quantity.
  - **Executor-only:** N\*, reach, visit counts, widths and per-row prices.
  - **Row identifiers:** they appear in approved public provenance records (the plan companions and the sealed admission record) and in executor-side records. The reports disclose counts only.
- **Prospectiveness:** this round is prospective for its fresh observations. Both the decision to run it and its replicate bound were informed by the A13 round's outcome.
- **Certification and adoption:**
  - **Five rounds:** two certifiers from different model families reviewed each draft blind to each other on 2026-10-20.
    - **Drafts 1 to 4:** both certified each with required repairs.
    - **Draft 5:** both certified it for both snapshot variants, with the snapshot-path repair bundled (S) and without it (N). One one-word repair, confirmed at adoption, is applied.
    - Every required repair is incorporated.
  - **Adoption:** the operator approved the text and chose variant S on 2026-10-20 (13:45Z: "Approved, go with S"). Variant N's text is deleted.
    - **One certified sentence carried over:** the definition of a single-host "frozen dispatch specification", certified as part of variant N, is kept in step 6 for the default single-host launch.
  - **The operator's choice:** made on 2026-10-20 ("Go with A14 as described, R 32").
- **Code citations** refer to `simulation/v3/` at commit `55817036` (code identity `5df9866f…`).
- **The earlier results stand as reported:**
  - The original refusal and the A13 round's refusal are both preserved and reported.
  - Success under this amendment is never described as success of the original registration, or of the A13 round.
  - Nominal-family results are labeled as produced under A13 and A14, amendments informed by outcomes.

**What this amendment supersedes, for the A10 nominal family only.**

- **A13 item 10** ("There is no second extension round for this family") is superseded by items 1 to 12 here.
- **A13 item 13's first scope bullet** reads "the rows of the A10 nominal family that remain `not_estimable` after A14's round". A no-launch from step 5 on, or a halt of A14's round, falls under item 12 here, which ends stage 1.
- **A13 items 4 and 5** apply to this round with R_max₂ and the floor of 24 (item 5 here).
- **Runbook 17.4's prohibition** on another plan, a larger R_max or a second round is superseded by the runbook section added in step 2.

No other A13 item changes, and none changes for any other family.

**Assumptions.**

A13's assumptions 1 to 3 extend to this round.
- **The new streams:** conditional on the fitted family and the earlier history, they have the same independent trajectory law. They come from item 4's seed range, disjoint from every earlier range. Integer disjointness is not itself proof of stream independence; that rests on A13's assumption 1.
- **The stop** reads visit indicators 1{N_i > 0} only.
- **Eligibility** reads D₀, the A13 round's statuses and its visit indicators. The eligibility predicate never uses an S_i or the magnitude of a positive N_i, and nothing from this round. Integrity validation may inspect the sealed records' structure and validity, for example finiteness; a malformed record is a finding, never a reason to exclude a row.
- **Hence:** the marks of each eligible row's first N\* visiting trajectories in this round's data are independent and identically distributed under the law conditional on a visit.

**The round.**

1. **The A13 round's records.**
   - **Copy and verify:** before eligibility, the executor copies the following by hash into this round's execution checkout and verifies them:
     - the original refused candidate and its sidecar, and the original validation plan and receipt;
     - the A13 `plan.json` (plan hash above) and its `.public.json`;
     - the family round record `v3/runs/a10_stage1/nominal/v3_rerun_tables_A10.a13_round.json`;
     - the sealed admission record (SHA-256 above);
     - from the A13 root: `identity.json`, `launches.json`, `validate_plain_ext/nondeterminism_check.json`, the nondeterminism re-execution record `_nd_validate_plain_ext/records/<checked job>.json`, and the ten completion records and outputs;
     - the original census and validation completion records and outputs that item 6's forecast reads.

     Every file's SHA-256 is recorded in this round's plan.
   - **The checks,** by a read-only verifier on the hash-verified copies. Recorded absolute paths are mapped to the copies through a frozen, immutable source-to-copy mapping:
     - the checks of A13's `publication_round`, implemented read-only. The helper itself is not called: it can latch a halt into the A13 record (`validation_extension_a13.py:535`, `:548`), and it compares recorded absolute paths;
     - each output is read through `completed` at code identity `5df9866f…` and `validate_replicates`;
     - each result's plan and source identities, and that it either reached the registered stop or exhausted R_max = 16 (`:668`);
     - historical plans are verified by ancestry and committed note hash, and their producer identities through the committed compatibility records.

     A13's `validate_plan`, `publication_round` and `publish` are not called; `validate_plan` and `publish` require the running identity (`validation_extension_a13.py:448` to `:449`, `:644`). Nothing is re-pinned, rewritten or latched, on a failure path either.
   - **Each A13-eligible row's A13-round result** is recomputed deterministically with A13's unchanged `extension_test` on the recorded first N\* visiting trajectories. It gets no other statistic.
     - The recomputed residual set must equal the admission record's residual rows; a difference is a finding.
     - Eligibility uses only the recomputed reason "N* not reached", never the admission record's list.
     - The classifications and their provenance are bound in executor-side records before launch.
2. **Eligibility.** A row is eligible only if all of these hold:
   - it was eligible for the A13 round (A13 item 1);
   - its recomputed A13-round result is `unresolved`, with reason "N* not reached", so it was never tested;
   - no cell has a `violation`.

   Rows tested in the A13 round are not eligible, and keep that round's decision. Eligibility is recorded as one boolean per row, and the eligible set and its source jobs by identifier only. E₂ is the set's size, expected to be 20.
3. **The constants:** each row's w, τ, M, α and N\* are recomputed with A13 item 2's expressions and must equal the A13 plan's values; a mismatch is a finding. N\* is unchanged.
4. **The data.**
   - **Its own phase:** a new phase, `validate_plain_ext2`, with its own job kind, `a14_validate_plain_ext2`, runs for the eligible rows' source jobs only.
     - It reuses A13's unchanged `extension_stage`.
     - Its outputs never enter the validate index or the A13 round's phase.
     - The phase reads the fit and A1 outputs and the eligible set. It never reads the original validation statistics or any A13-round trajectory; item 1 reads those, at preparation only.
   - **Replicates:** each has the registered size, 2,048 trajectories in 32 groups of 64, at the registered horizons. They are numbered 20 to 19 + R_max₂, continuing after the A13 round's 4 to 19.
   - **Seeds:** ext2_seed(s, r) = 2^61 + `_truncated_sha("v3_R_validate_ext2", s, "/", r)`, for A1 job seed s and replicate r. They lie in [2^61, 2^61 + 2^60).
     - **Disjoint ranges:** the reserved range [2^61, 2^62) lies outside:
       - the A13 round's [2^60, 2^61);
       - every `_truncated_sha` seed, below 2^60 (`continuation_validation.py:55` to `:60`);
       - the `stable_job` and qualification seeds, in [2^128, 2^129) (`artifacts.py:141`; `qualification_a11.py:76`).
     - **No shared input strings:** the hashed strings cannot coincide with the A13 round's. The separator forces an equal r, and 4 to 19 and 20 to 51 are disjoint.
   - **The seed check, before any simulation:**
     - the full manifest for replicates 20 to 19 + R_max₂ is frozen;
     - its seeds must be pairwise distinct;
     - none may equal any seed in the global inventory, including the A13 plan's `seed_manifest` and `forbidden_seeds` and the A13 round's qualification and configuration seeds, each named as an input;
     - any collision halts the run.

     The range is recorded as reserved. The runner's reserved-range guards, this round's seed check and A5's seed check all cover it.
5. **The stop and R_max₂.**
   - **The stop:** as A13 item 4 (`stop_reached`, `validation_extension_a13.py:177` to `:179`), with R_max₂ in place of R_max.
   - **The prices:** A13's `price_extension` supplies the per-source prices, with its projection identity checks (A13's clarification of 2026-10-16). R_max₂ is computed from them, because `price_extension` itself caps R at 16 (`:131`).
   - **The rule:** R_max₂ is the largest integer R ≤ 32 such that R · Σ_j B_j / 3 ≤ 15, summed once over each distinct source job of the eligible rows. Conditional on the frozen eligible source set, it uses cost classes alone.
   - **The expected value:** 32, at a projected 7.37 X2-hours. The assessment's charge projection is about 11.5 X2-equivalent hours on one X2. Both are budget estimates.
   - **No launch below 24:** if R_max₂ < 24, the round does not launch. This is a declared policy floor matching the assessment's projection, and with this eligible set it is inert (inferred).
   - **Impossible rows:** any row with N\* > 2,048 · R_max₂ is flagged before launch, as in A13.
   - **The meaning of both:** like A13's, they affect power and cost only, never the false-certification rate (A13 item 2).
6. **A predicted admission probability, before the launch go.** The executor computes P(every Part 2 condition after this round), together with its value at a certification rate of 0.9.
   - **The inputs:**
     - the original and A13-round visit indicators and trajectory totals;
     - each row's N\*;
     - the original census cell counts and continuation support, or verified floor-with-C0 flags computed from them;
     - the rows' lookup contexts and screen flags;
     - the frozen R_max₂;
     - the A13 round's certification and violation counts.

     No observation from this round is an input.
   - **The method:**
     - **The scripts:** the three listed in the assessment's `FEASIBILITY_SHA256SUMS` (`feasibility.py` `b2abd1e3fb0ae0e90193f12171eb7633cf4180163ca0bea57e37e8df6667b5e7`, `feas_sens.py` `e99671d2c43a150d4d31286e379392e5801a3983effa9a22f13e707a72be3fd7`, `feas_extra_full.py` `3fb75616f072123d62a7a60e74366c03261a36267c0b6ecf8fa8b74434051a4a`), run unchanged.
     - **Where it runs:** on X2-1, in a read-only, hash-verified source view of `55817036`, isolated from this round's execution checkout. Step 2 changes modules the scripts import, so the new checkout cannot serve.
       - **Inputs:** the verified inventory of item 1 and the source-to-copy mapping supply every path and environment value the scripts read. Every input they need is in that inventory.
       - **Protection:** the original roots and records are mounted or opened read-only. An unmapped path is a finding, never a silent read of an original file.
     - **The import check:** before running, the executor confirms and records:
       - **Repository modules:** every repository-owned module actually imported, transitive imports included, comes from the verified source view and matches its git blob at `55817036`.
       - **Everything else:** standard-library and third-party imports come from the recorded, frozen Python environment, with its Python and numpy versions recorded against the A13 round's environment.
       - **No A14 source:** no A14 module, and no source in the execution checkout, is reachable through import resolution. The unchanged scripts insert their working directory into `sys.path` (`feasibility.py:10`), and the wrapper accounts for that.
     - **The model:**
       - each row's visit probability is a posterior mean with a uniform prior, pooling its A13-round and original trajectories;
       - its visiting count is beta-binomial, by a normal approximation with continuity correction;
       - rows are drawn independently given their reach probabilities. Cross-row independence is an assumption of this forecast only, not of the error bound;
       - 4,000 Monte Carlo draws.
     - **The two numbers:** the `p_all_part2` values from the unchanged `round2` calculation in `feasibility.py` at R = R_max₂, case A:
       - first, with the recomputed empirical certification and violation rates;
       - second, with certification rate 0.9 and violation rate 0.
     - **Settings for both:** the script's own seeding for case A, `random.Random(7 · R_max₂)`, 4,000 draws, and its three-decimal rounding.
     - **Before computing:** the executor confirms that case A's eligible set equals this round's frozen eligible set; otherwise it reports a finding. They coincide here only because no A13-eligible row reached N\* and was left `unresolved` by the test.
     - **What else is in the scripts:** their other curves and scenarios are assessment evidence, not alternatives for this report.
     - **A wrapper:** a read-only wrapper may invoke the unchanged function at R_max₂, with its hash frozen before the go.
   - **Its standing:** informational, reported as two operational numbers with the load sheet. It decides nothing mechanically; the operator's go does.
7. **The test:** as A13 item 6, applied to exactly the first N\* visiting trajectories of this round's data alone, with the same w, τ, M and α and the visit-weighted safeguard. A13-round trajectories are never pooled in.
8. **A halted round:** as A13 item 7. A scientific halt certifies nothing, spends this round and latches in this round's family record. An infrastructure interruption resumes under the supported procedure, from original seeds.
9. **Re-assembly.**
   - **The start:** the refused candidate.
   - **The replacements:** for each A13-eligible row, the C0 decision of the round that tested it, applied as A13 item 8 describes:
     - the A13 round's recomputed decision, for the rows it tested;
     - this round's decision, for every row eligible here, whatever the outcome: certified, `unresolved`, `violation`, or N\* not reached.

     Every classification, its safeguard outcome and its re-test record are preserved in the sidecar and in the admission evidence `verify` reads. C0 gains support only when its test certifies and its safeguard passes. Validated support is recomputed, and the registered floor is re-applied to the unchanged census.
   - **Everything else** is carried forward exactly: every row outside the A13-eligible set, the sensitivity processing and the sensitivity siblings. The run halts unless each of those rows, and its sidecar entry, is byte-identical to the refused candidate's.
   - **Marking:** every A13-eligible row carries the A13 row marker, which records its re-test status where `verify` reads it, and the round that tested it (1, 2 or none).
10. **The error accounting:** A13 item 9's statement holds unchanged.
    - **The argument:** for each A13-eligible row j, let q_j be its probability of reaching N\* in the A13 round, given D₀.
      - Its A13 test, which happens only on that event, falsely certifies with probability at most q_j·α/M. The stop and the first-N\* selection read visit indicators only, so they do not select the marks.
      - Let H₁ contain the earlier history and the launch decision. Conditional on H₁, row j's second-round false-certification probability is at most α/M if it is eligible and the round launches, and zero otherwise. Eligibility implies that it did not reach N\* in the A13 round. Averaging over H₁ given D₀, its second-round contribution is therefore at most (1 − q_j)·α/M.
      - The two events are disjoint, so each row contributes at most α/M. A no-launch, an unreached N\*, the safeguard and the floor can only reduce certification.
      - Summing over the E = 50 rows gives E·α/M, with no independence needed between rows.
    - **The bounds:** A13's argument then gives α(1 + P/M) given the fitted family, and 2α unconditionally.
    - **What it is not:** the bound is not a posterior guarantee conditional on the A13 refusal or on final publication.
    - **When it fails:** a second statistical certification opportunity, using a different extension sample, for an already-tested row (deterministic recomputation and the compatibility replay are not such opportunities); pooling across rounds; seed overlap; N\*, w, τ or the allocation chosen from new marks; certifying from a halted round; seeds redrawn on resume; or the stream assumptions failing.
    - **What is reported:** E, E₂, the number of tests performed in each round, P and M, side by side, with α·E/M.
11. **The reservation and records.**
    - **The reservation:** registered preparation exclusively reserves `v3/runs/a10_stage1/nominal/v3_rerun_tables_A10.a14_round.json`, independently of the preparation output path.
      - **When it is created:** before any of preparation's checks. It initially binds the family and the approved A13 plan, and records any terminal preparation failure. The completed A14 plan hash is bound once it exists.
      - **What it grants:** nothing yet. It gives no launch authorization, and the A13-record checks of item 1 stay mandatory.
      - **A refusal:** it is refused unless the verified A13 round record shows its plan and root bound with halt `null`, and the A13 admission record shows outcome `refused`.
      - **An interruption:** an infrastructure interruption resumes the same preparation.
    - **What it binds:** the original family, the approved A13 plan and this round's plan.
    - **The first launch** binds the final frozen specification and root. A different plan or root, or a latched scientific halt, cannot obtain another realization. Rehearsals use separate output-relative reservations.
    - **This round's Part 2 record** is at `…A10.a14_round.admission.json`, written only if absent.
    - **No A14 code path writes either A13 record.**
12. **Final.** There is no third round for this family.
    - **From entry into step 5's registered preparation,** including a failure before the completed plan or reservation can be written, the consequences below follow if this round:
      - does not launch for any reason other than an infrastructure interruption resumed under the supported procedure. That includes item 5's floor, a finding during preparation, a seed collision, or the operator declining the go. A delay for scheduling or machine availability is not a decline; the operator records any decline as one;
      - halts under item 8;
      - or ends with any Part 2 condition failing.

      Its consequences:
      - the A10 nominal family is not published;
      - the labels and the five runs do not proceed;
      - A10 stage 1 ends;
      - the original refusal, the A13 round's refusal and this round's outcome are all reported;
      - stage 1's reservation for labels and runs returns to the unreserved ledger.
    - **Before step 5,** a rejected code review, a rehearsal mismatch or a failed compatibility proof is not this round's outcome: no A14 plan, reservation, seed manifest or probability exists yet for the registered round.
      - **A failed proof** is a compatibility failure to be investigated. The failed identity-pair attempt stays final.
      - **A corrected identity** may follow under A11, with a new rehearsal, new proofs and their approvals, before step 5, but only when the failure is traced to the new identity. One way to trace it is replaying the failing jobs at `5df9866f…`.
      - **If the producing identity cannot reproduce** the outputs either, that is a finding about those records. This covers the A13 round's outputs, and the original outputs of the 434-job proof. They cannot be carried forward, and the consequences above follow.
      - **A failure traced to neither identity:** the sequence stays halted, and the operator chooses between a further investigated identity and ending stage 1. No registered-round A14 data exist, so the choice is free of registered A14 observations (the historical outcomes are already disclosed above), and the operator records it.

**Part 2** applies as A13 items 11 to 13 after this round, with item 13 as superseded above: the cap of 19, the one-row-per-context limit, the balanced-witness exclusion, item 12(b), binding, recording and reporting. The admission scope is a new scope accepted by `binding` and `verify` for this round, with A13's conditions unchanged.

**The order of steps.**

1. **The text:**
   - This amendment, certified blind by two certifiers from different model families and approved by the operator, is committed and pushed. That commit is **the A14 commit**.
   - It does not change the code identity.
   - Every later launch pins the A14 commit, with the design note in its execution checkout byte-identical to the note there.
2. **The code commit,** on main.
   - **What it adds:**
     - **The round:** a module for its preparation, historical-input verification (item 1), eligibility, constants check, manifest and seed check, pricing, stop, test, checkpoint and replicate handling, reservation (item 11), halt latch, re-assembly, publication and public summary.
     - **The new job kind,** each as a new branch beside A13's:
       - its dispatch in the runner and the coordinator;
       - its checkpoint and halt operations;
       - its scientific-halt and nondeterminism latches into this round's family record;
       - snapshot and qualification handling, with non-reserved short-test streams;
       - configuration and resource classification.
     - **The reserved range:** the guards extend to [2^61, 2^62).
     - **The current-pin change:**
       - Current A10 launches and publications verify strictly against the A14 commit, whose note must contain the A13 clarification and this amendment.
       - Plans pinned to the A13 commit or earlier, including the A13 round's plan, verify historically.
       - New validation launches pinned to the A14 commit keep A13 Part 2's binding for later families.
       - The files: `artifacts.py` and the selection sites in `table_validation_a4.py` and `table_labels_a5.py`.
     - **The receipt fields (step 7),** and A5's forbidden set over both rounds' manifests.
     - **A compatibility-replay adapter for step 4's A13-phase proof:**
       - **What it does:** re-simulates every replicate of each selected job from its seed, in an empty scratch root. Recorded A13 checkpoints are read for comparison only, never loaded as completed work. The present path would load them and return the recorded data, which matches itself (`validation_extension_a13.py:258` to `:272`; `compatibility_a10.py:143` to `:158`).
       - **Its limits:** it writes nothing outside scratch, and nothing it does can latch or write a family record. Nothing is computed from replay outputs beyond the byte comparison.
       - **The seed guard:** it is the only exception to the reserved-seed guard (`production_runner.py:182` to `:190`), limited to the A13 plan's own jobs and seeds.
       - **What it leaves alone:** it does not reopen the spent round, or change any A13 function.
     - **A runbook section** for this round, superseding 17.4's prohibition.
     - **The snapshot-path repair,** bundled as an execution fix:
       - **What it is:** an execution-only repair for explicitly inventoried inputs in historical checkouts.
       - **How it works:** it stages hash-verified, read-only copies inside the authorized write scope, and preserves original input paths through verified aliases. It rewrites no job configuration, identifier, seed or scientific byte, and rejects changed or undeclared inputs.
       - **Where it must work:** through transfer, qualification staging and the worker's verified input view (`snapshot_a11.py:67`, `:90`; `qualification_a11.py:86`).
       - **The check:** inputs already inside the checkout are staged exactly as before; the rehearsal confirms this.
   - **The additive rule:**
     - No function in `validation_extension_a13.py`, and no existing fit, validate, census or estimation function, is edited.
     - The shared runner, coordinator, snapshot, qualification, admission, A4 and A5 files gain parallel branches only, with the stated exceptions.
     - The A13 kind's behavior, including its R ≤ 16 bound, is unchanged.
     - Everything is inert for any family without an A14 round, with the stated exceptions.
     - **The exceptions:** the current-pin change, and the snapshot-path repair. Each is an explicit exception to parallel-branch-only changes and to operational inertness. Scientific behavior and existing result fields stay unchanged outside A14.
   - **Records:** the A2 re-pins name every changed pinned file and its reason, and the new code identity is recorded.
   - **The authority:** A11 item 3's proof admits the unchanged computations. A14 alone admits the new phase, its seeds, the second reservation, the two-round re-assembly, the replay adapter, and the snapshot-path repair.
   - **Review and approval:** the interpreter reviews the diff against `55817036`, including the unchanged A13 module and the inert paths. The operator approves the concrete code commit.
3. **A non-registered rehearsal** at the new identity, on rehearsal seeds outside every reserved range:
   - **a two-round fixture:**
     - this round's preparation from a rehearsal A13 round;
     - publication over both rounds;
     - a forced round-2 violation that reaches Part 2 and is refused;
     - a latched halt;
   - **the round's dispatch** on a small non-registered plan, and qualification;
   - **run-side equivalence:** sampled run jobs at code identity `5df9866f…` and at the new identity agree byte for byte on every existing `result` field (the exclusions are as in A13 step 3), and the loader behaves identically on a family with no admitted rows;
   - **A5's preparation** against a rehearsal receipt of the step 7 form, forbidding both manifests;
   - **the replay adapter,** on rehearsal jobs. It must reproduce a clean replicate byte for byte, and report a mismatch when a recorded checkpoint and its recorded output are perturbed together. An adapter that wrongly loads checkpoints would then reproduce the perturbation and fail the drill;
   - **the real transport:** the new kind's checkpoint and halt operations pass through the real host loop and `rpc()`, including resume;
   - **item 6's tooling:** the wrapper, the import check and the path mapping, on rehearsal inputs, so that a tooling defect appears before the stage-ending boundary;
   - **the snapshot-path repair:** qualification, transfer and two-host execution using an input outside the checkout, with inputs already inside the checkout staged exactly as before.

   A mismatch halts the sequence. The rehearsal's overhead is charged to the stage 1 ledger.
4. **The A11 compatibility proofs** at the new identity.
   - **The original outputs:** the 434-job selection for the original estimation and validation outputs, as A13 step 4.
   - **The A13 phase:** additionally, A11 item 3's selection applied to the completed A13 extension phase, binding its producing identity `5df9866f…` to the new identity, through the replay adapter. The executor records the additional count from the frozen strata before execution.
   - **Before they run:** the projected cost of both is approved; a configuration test is run; `llm down`, supervised and restored.
   - **After they run:** the interpreter's review, the operator's approval, and committed records, before any of the outputs is used.

   If either fails, the sequence halts, and item 12's before-step-5 clause governs what follows.
5. **The round's records,** in a fresh execution checkout at the proof records' commit, before launch:
   - item 1's verified inventory;
   - the eligible set, by identifier;
   - E₂ and R_max₂, and the projected cost;
   - the impossible-row flags;
   - item 6's two probabilities;
   - the frozen seed manifest and its check.

   These go into the round's `.public.json`, which is reviewed and approved before the launch go.
6. **The launch:** registered, with its own plan, cost cap (item 5), register approvals and operator go.
   - **The checkout:** that execution checkout, with a new root.
   - **Dispatch:**
     - **The default:** single-host, since one X2 is cheaper for this round. Pull dispatch is permitted only as rehearsed.
     - **For a single-host launch from `plan.json`:** "frozen dispatch specification" means the sealed single-host `plan.json`, with its sealed resource estimates, and the load sheet is built from that exact specification. The runbook supersedes its pull-freeze requirement for this launch only.
   - **Before it runs:** qualification, the frozen dispatch specification and its load sheet, the pre-launch configuration test, and `llm down`, supervised and restored.
   - **Its pin:** the A14 commit.
7. **Family publication,** at the same never-written target path, `v3/runs/a10_stage1/nominal/v3_rerun_tables_A10.json`, under the no-overwrite guard.
   - **What it requires:** this round's anchor, a matching root identity, a complete last launch, a passed nondeterminism check (and the multi-host check if applicable), and no A14 halt. Part 2 is checked and recorded first.
   - **The receipt:**
     - **Unchanged:** the original `plan_hash` and per-job `stream_seeds`.
     - **`a13_round` and `a14_round` objects,** each holding its plan hash, `.public.json` hash, stage-output hashes, complete frozen seed manifest and admission-record hash.
     - **`extension_seed_manifest`:** the union of both complete manifests, so that A5's existing reader forbids both (`table_labels_a5.py:475`).
     - **`refusals`:** the original refusal and the A13 round's admission record.
     - **Neither round** contributes a realized seed subset or stopping replicate.
   - **The plan-hash checks:** before runbook section 7's identity approval, the interpreter checks the receipt's A13 and A14 plan hashes against their approved `.public.json` records.
   - **Then:** runbook section 7's exact-file and hash identity approval, and its public identity-record commit.
8. **Labels and the five run launches:** as A13 step 8, pinned to the A14 commit.
   - **Unchanged:** the original path strings, and the label and run inventory comparisons.
   - **Each launch:** its own frozen dispatch specification, load sheet, approvals and go.

**Unchanged.**

- **No registered rule changes**, whether quantity, prediction, gate, citation rule, reading rule or admission threshold, except:
  - those listed under "What this amendment supersedes";
  - the amended family;
  - the receipt's added fields.
- **Also unchanged:** A13's Part 2 conditions, its error statement, the census, α, τ, the floor, the Bernstein test and N\*.
- **The ceiling:** stage 1's 980 X2-equivalent hours stand.
  - **The ledger before this amendment:** about 355.3 charged, 384.63 reserved for labels and runs, and about 240.1 unreserved.
  - **This amendment's charges:** the rehearsal, both proofs and the round, to the stage 1 ledger.
- **The stage 1 reading** stays registered at `93474e00`.

### Amendment A15, 2026-10-29: the A10 stage 2 budgets

**Status.** Adopted 2026-10-29. The text is draft version 3 (SHA-256 `7a9a203b5d994752dfe8c59a8c6839fd4604dad7736f81ad5c3e3ec3bc7c0017`), reviewed by the interpreter, read by both A16 certifiers as the budget companion in every round, and approved by the operator on 2026-10-29. The only changes at adoption are this status paragraph and the heading. Its arithmetic is in `simulation/diagnostics/a16/STAGE2_PLAN.public_v2.md` and `simulation/diagnostics/a16/REQUALIFICATION_PLAN.public_v2.md`, committed with it.

**Timing, and what was known.**

- **When it was written:** 2026-10-29, after A10 stage 1's tables, 53,100 runs and sealed reading were complete.
- **The opening:** stage 1's reading has been opened by the operator and the interpreter. The interpreter who reviewed this text and the operator who approves it have both read that opened reading. This amendment is not described as written before that opening.
- **The executor's knowledge:** the stage 1 outcomes were not supplied to the executor writing this budget plan. It read the registration, source code and execution cost/memory/configuration records. It did not open the stage 1 reading, `values.json`, `opened/`, scientific output files or a results write-up.
- **What informed the ceilings:** stage 1's measured class costs and memory peaks; registered stage 2 grids, estimators and seed counts; X2-1 as the budget basis; and explicit operational allowances. The ceilings use stage 1's measured costs and memory peaks only, and no quantity read from its results. No ceiling was set or moved because of a stage 1 reading outcome.
- **The registration's historical disclosures:** A13 and A14 themselves record earlier table-publication refusals. Those disclosures identify an operational risk. They do not confer an extension round on stage 2.
- **What has not happened in this planning task:** no registered or non-registered simulation, no registered preparation, no repository change or commit, no network access and no SSH.
- **At adoption:** record the actual approval/commit date and any intervening work or newly disclosed knowledge. Do not backdate this draft or repeat its knowledge statement if it has ceased to be true.

**Changes at review.**

- Disclose the reviewer and approver's knowledge, and distinguish measured cost/memory evidence from quantities read from results.
- Preserve section 6's existing budget-amendment/uniform-seed-reduction choice, without adding to it.
- Replace the anticipated upgrade with dated maintenance facts; the host decision is superseded by the 2026-10-29 review entry below.
- Reconcile the pilot's implied remainder with the final closeout ledger charge.
- Cite the committed publication copies of the arithmetic, recording their hashes at adoption, and round the amendment's base budget estimate.
- Add separate A16 extension and identity-release allowances, and distinguish A15's budget authority from A16's scientific procedure and code/pin transition.
- **2026-10-29 operator decisions:** select path (a), one successor built/rehearsed/proven before any stage 2 launch; preserve A6's no-A5 scope under the interpretation recorded in A16; restrict the study to X2-1 only; incorporate A16's fixed-path and reader clauses; update the release budget estimate to 74 h without moving its 96 h ceiling; cite the regenerated version-2 publication copies. No ceiling was set or moved because of a stage 1 reading outcome.

**Reason.** A10 section 12 registers the remaining stage 2 work unchanged and requires a dated, committed amendment to set its ceiling before it launches. This amendment supplies budgets. The earlier 980-hour ceiling belongs to stage 1; A7's 90-hour ceiling belongs to A6 under R4. Neither is stage 2 launch authority. A10 section 12's pilot projected 979 X2 hours for stage 1 and 2,626 for everything, an implied stage 2 remainder of **2,626−979=1,647 X2 hours**; the final blind-closeout entry of the **A10 stage 1 operations ledger, 2026-10-25T23:55Z to 2026-10-26T00:15Z**, charges **501.77** against that 979-hour pilot projection (501.45 before closeout plus 0.32 closeout, not the pre-closeout figure). A15 prices the original stage 2 scope from stage 1's measured class costs, so its original 1,400-hour ceiling below that pilot remainder cuts no registered work; the separately added A16 procedure and release budgets below are additional scope, not a reduction of that scope.

**The components.**

1. **The c^0.5 arm:** its own per-capability table family, estimation, A4 validation and publication, A5 labels where required, its 4,400 registered runs, and its separately sealed stage 2 reading component.
2. **A6's reproductive-age crowding family on the corrected instrument:** its own tables, validation and publication, its 4,400 runs and registered reading.
3. **A6's σ0²×10 family on the corrected instrument:** its own tables, validation and publication, its 500 runs and registered reading.
4. **A6's σ0²×0.1 family on the corrected instrument:** the corresponding tables, validation, publication, 500 runs and registered reading.

The A6 variants make no A5 labels, as A6 directs. The operator chose the authenticated no-label exemption on 2026-10-29; A16 records the interpretation of A10 §7 and the family-keyed receipt policy. Their calibrations, grids, contexts, settings, horizons, seeds and reading rules are unchanged. No part of stage 1 is rerun as new registered work or re-read to choose a budget.

**The ceilings.** Every number in the following table is a **budget**, in X2-equivalent hours. It is never a registered quantity, reading, prediction, admission criterion or promise of completion.

| Component | Estimation | Validation | A5 labels | Runs | Assembly/publication/identity/receipt | Component ceiling |
|---|---:|---:|---:|---:|---:|---:|
| c^0.5 | 22 | 400 | 70 | 8 | 2 | **502** |
| Crowding | 22 | 400 | None | 8 | 2 | **432** |
| σ0²×10 | 9 | 160 | None | 2 | 2 | **173** |
| σ0²×0.1 | 9 | 160 | None | 2 | 2 | **173** |
| Post-update machine requalification | | | | | | **64** |
| Shared input/calibration/seed/ledger preparation | | | | | | **8** |
| The two stage 2 sealed reading components and their verification | | | | | | **12** |
| Unallocated operational contingency | | | | | | **36** |
| Original stage 2 scope and prerequisite subtotal | | | | | | **1,400** |
| A16 successor-identity build support, rehearsal and compatibility release | | | | | | **96** |
| A16 sqrt, round 1 | | | | | | **48** |
| A16 sqrt, round 2 | | | | | | **48** |
| A16 crowding, round 1 | | | | | | **48** |
| A16 crowding, round 2 | | | | | | **48** |
| A16 σ0²×10, round 1 | | | | | | **48** |
| A16 σ0²×10, round 2 | | | | | | **48** |
| A16 σ0²×0.1, round 1 | | | | | | **48** |
| A16 σ0²×0.1, round 2 | | | | | | **48** |
| **Stage 2 ceiling, including conditional A16 allowances** | | | | | | **1,880** |

- **The unit:** the stage 1 operations ledger's X2 reference rate is 1.0. On X2-1 alone, a charged X2-equivalent hour is an active wall-hour. No 31/16 factor is added to those charges.
- **What is charged:** preparation, qualification, configuration tests, execution, nondeterminism checks, hashing/publication, interrupted and failed attempts, cleanup, and sealed reading computation. Reserves are inside the ceilings, not time added after them.
- **The contingency:** it authorizes no work and no extra scientific opportunity. Its allocation requires an explicit budget decision before use. A change to a listed ceiling requires a further dated budget amendment before the affected launch.
- **The check:** before every launch, consumed cost plus outstanding reservations must fit the stage ceiling, and the launch's measured budget estimate must fit its component allowance. The operator approves that exact specification and load sheet.
- **An excess:** A10 section 12 points to section 6: if a measured projection exceeds its ceiling, the operator decides, before any registered run of the affected component, between a budget amendment and a uniform seed reduction across cells. That rule stands unchanged; A15 adds nothing to it. It adds no non-uniform reduction, omitted cell, altered estimator or shortened horizon, and nothing is cut after a registered output of that component is read. A budget cannot create or enlarge an A16 extension opportunity; its R_max rule and sample limits require scientific authority, not a transfer of unused funds.

**The budget estimate, and what it rests on.**

- **Measured stage 1 component costs:** estimation 30.28 X2-equivalent hours; original validation 260.04; labels 59.39 over 4,752 completions; the five run components 50.07 over 53,100 runs. Historical A13 and A14 extension launch charges were 5.80 and 9.77. They are cost evidence, not stage 2 entitlements.
- **The base stage 2 budget estimate:** about **1,050 X2-equivalent hours**, or **about 44 continuous days** on X2-1 alone, excluding human and scheduling delays. A16's selected path-(a) identity release adds a **74-hour budget estimate**; each available round adds a conditional **36-hour budget estimate**, so the plan with the release is about 1,123 hours before extensions, and about 1,411 hours if all eight rounds are used. These are budget estimates, not predictions that rounds will be needed or that admission will succeed. The release budget estimate is `44.431848908 historical proof-cost proxy +20 assumed operational hours +8 assumed audit-fix hours =72.431848908`, rounded up to 74; the **96-hour release ceiling is unchanged**. The 8 h covers the committed builder/seed/path work (4), receipt/family/admission checks (3) and reader-tail/incidence checks (1), as priced in `A16_FEASIBILITY_v2.md`. A round budget estimate is 2×15 registered-class price hours plus 6 assumed overhead hours, informed by measured A13/A14 launch charges. Exact arithmetic remains in the committed plan.
  - **The basis:** registered per-capability counts; the largest recorded stage 1 class-mean timing within each table setting; conservative initial memory capacities; the more expensive validation-route bundle; at most 4,125 square-root labels; comparable measured 500-step run times; and explicit overhead/requalification/reading allowances.
  - **The assumptions:** stage 1 class costs are transferable for budgeting; new class memory is initially unmeasured; future routes are unknown; shared preparation and reading allowances have no measured stage 1 reader-cost basis in the permitted evidence.
  - **What it does not say:** it estimates no survival, fire rate, table availability, certification probability or sensitivity verdict. It does not guarantee that any family can publish.
- **The arithmetic and class evidence** are in **`STAGE2_PLAN.public_v2.md`** and **`REQUALIFICATION_PLAN.public_v2.md`**, committed with A15. At adoption record each committed path, full commit and file SHA-256 in the adoption/execution record, and verify those exact bytes before any launch. These version-2 publication copies accompany the v3 plan and the original fixed-code requalification protocol with maintenance chronology brought current and successor A11/A12 proofs kept separate and later. A16's adopted text and the identity-release evidence are separately bound. Draft publication-copy hashes in `REPORT_4.md` are review evidence, not a claim of adoption.

**Machine and timing.**

- Stage 2 runs on **X2-1 only**, with 32 CPUs, approximately 123 GB memory and at most 31 workers. X2-2 is permanently unavailable to this study; BX-1 and WS-1 remain outside the compute pool. Any other host would require a new dated amendment. All budget estimates and ceilings use X2-1 alone.
- **Maintenance recorded on 2026-10-29:** `x2_1_before.txt` (14:32:21Z) and `x2_1_after.txt` (15:31:14Z) record X2-1 changing from kernel **7.0.0-34-generic** to **7.0.0-42-generic** after reboot. `x2_2_before.txt` (14:27:59Z) and `x2_2_after.txt` (14:35:30Z) record X2-2 changing from **7.0.0-38-generic** to **7.0.0-42-generic**. These are the archived X2 maintenance before/after records of that date.
- On both hosts the five packages were unheld, with versions unchanged: **libc6 and libc-bin 2.39-0ubuntu8.9; libgcc-s1, libstdc++6 and libgomp1 14.2.0-4ubuntu2~24.04.1**. Both after-records show no held packages, no remaining upgradable packages and no reboot required. The **phaseb package-list SHA-256** is unchanged before/after on both: `039a116d09ecad032d50330b7ae2495ebbb3c9d83f736d8c63c66a230ebc9f01`. An unchanged package list is **not bit-identity evidence**; requalification still governs.
- Before any registered stage 2 launch, X2-1 must pass the approved stratified scratch replay against pre-update registered outputs at their original code identities, with exact scientific byte agreement. A mismatch blocks launch; no tolerance is introduced.
- Each launch retains its own qualification, approved machine-register entry, pre-launch configuration test, worker/thread/memory controls, `llm down` and supervised restoration, durable records and resumption rules. A machine/sample pass is not a launch go.

**Code and budget authority.**

- This amendment changes no simulation code identity. **A16**, if adopted, needs a successor to `174ab6600e0bc3514ee4b0f553a85b5e426aea4203621125debfa3cd12fd5afd`; the operator selected path (a) on 2026-10-29, so the plan builds, rehearses and proves that identity before any stage 2 launch. Its full hash is recorded after the approved code commit, never invented in this draft. A15 supplies only the separate release budget.
- A15 remains separately committed **budget authority**, bound by commit and file hash to every frozen operational budget record/input inventory. At the A16 successor identity, current launches use the **A16 scientific execution pin** and its exact note, with earlier plans checked historically. A14's execution-pin rule continues for launches at 174ab660 and earlier identities, as A16's supersession clause states; no registered stage 2 launch uses that route.
- A frozen execution checkout receives no code or scientific-note update. A new identity requires a fresh checkout, reviewed A2 re-pins and A11/A12 records. Operational and reader wrappers carry their own source hashes and review. This budget amendment does not approve unbuilt code or wrappers.
- Any later execution-code change follows the existing A11/A12 compatibility procedure and its approvals; this amendment supplies no waiver and makes no compatibility claim.

**Publication and reading.**

- A13 Part 2 applies prospectively to these new validation launches, with its own-family row fraction, per-context limit, balanced-witness exclusion, binding, recording and incidence reporting unchanged.
- A13 Part 1 and A14's second round remain limited to the nominal family. No stage 2 extension is registered by **A15**. The separate prospective **A16**, if adopted, supplies up to two conditional rounds per stage 2 family after its original refusal, with A13 Part 2 unchanged. Its unused allowances authorize nothing. Preserve every refusal; a final refusal/no-launch/halt under A16 leaves the dependent arm reported not run, with its reason, under the existing reading rules.
- Stage 2's six remaining A10 headline comparisons retain family size 18; its eight remaining A6 comparisons retain family size 33. Their stage 2 components are sealed separately. Stage 1 verdicts and seed-convergence results are not recomputed. Quantities, bootstrap streams, intervals, censoring, materiality, unavailability flags, gates and citation rules remain as registered.
- The operator's separate go is required to compute the sealed reading and to open it.

**Order.**

1. The interpreter reviews this budget text, its evidence and the scientific-execution/A15-budget binding, including A16's separate authority. The operator approves the concrete text and ceilings. The dated amendment is committed and published before any registered stage 2 launch; its full commit and byte hashes are recorded.
2. The operational/reader preparations are reviewed and fixed by hash; the completed OS maintenance records are retained; post-update requalification passes and is approved. Under the selected path (a), the successor build, rehearsal and compatibility proofs also pass and their records are approved/committed before stage 2 starts.
3. Each component is prepared with its own immutable inputs, exact job inventory, frozen dispatch specification, budget reservation and worker-load sheet. The exact next launch receives its own operator go.
4. Estimation precedes validation; any refused publication follows A16's separate entry/round/finality gates if adopted; publication precedes dependent labels/runs; all required inputs and completeness checks precede sealing. The sealed stage 2 readings are opened only on the operator's go.

**Unchanged.**

- No registered instrument parameter, grid, context, seed rule, sample size, horizon, quantity, prediction, reading, gate, admission threshold or citation rule changes **by this budget amendment**. A16's explicitly specified added validation samples and associated procedure require its own separate adoption.
- A10 stage 1 and its 980-hour ceiling stand. Its reading's registration and seals stand.
- A6 under R4 and A7's 90-hour ceiling stand.
- A13/A14's historical refusals, scope, finality and disclosure stand. No additional extension opportunity is created **by A15**; only the separately adopted A16 can supply its specified prospective opportunities.
- The only new decisions proposed here are operational budgets for already registered stage 2 work, its prerequisite/reading operations, and the separately proposed A16 procedure and identity release. A budget is never evidence for a scientific conclusion.

### Amendment A16, 2026-10-29: prospective validation extensions for A10 stage 2

**Status.** Adopted 2026-10-29. The text is draft version 2.5 (SHA-256 `ea1d9a12a8de96dcbcb61cc5b7761a3a99297228400ad2411943c2d2ad2e0293`), certified blind over five rounds by two certifiers from different model families, a fresh Claude Fable 5.1 instance and Gemini 4 Argon, each blind to the other and to stage 1's results, and approved by the operator on 2026-10-29. The certification record, with every round's reports, reconciliations and diffs, is `simulation/diagnostics/a16/A16_CERTIFICATION_RECORD.md`. The only changes at adoption are this status paragraph and the heading. It supplies the extension procedure; A15 supplies the budgets.

**Timing, and what was known.**

- **When it was written:** 2026-10-29, before any stage 2 output exists, as stated by the operator. The executor has run nothing and has not independently inspected stage 2 output roots.
- **The executor:** drafted this text blind to stage 1's scientific outcomes. It used the registration, source at `174ab660`, permitted cost/memory records and OS maintenance records. It did not read a reading output, `values.json`, `opened/`, `stage1_reading_2026-10-26/`, a results write-up or `blind_compare*`.
- **The proposer and approver:** the interpreter proposed this procedure after the opening and knowing stage 1's results; the operator who approves it has also read that opened reading. A reader should treat this proposal as made by someone who knew stage 1's results. The executor's blindness does not make the proposal blind.
- **The stated basis:** A13 and A14's disclosed certification history and A13 Part 2's cap arithmetic. The nominal family's original publication was refused; A13's round was also refused; A14 supplied a second, final round. A14 identifies the first round's bound of 16, rather than its class-price cap, as the binding limit. These are registration disclosures, not a newly opened reading.
- **Prospectiveness:** this rule, including both opportunities, eligibility, sample sizes, pricing, seeds and finality, is fixed before the affected stage 2 validation data exist. Whether a family enters it depends mechanically on that family's later original refusal. The operator retains each launch go. Neither that conditional entry nor this disclosure erases the proposer's knowledge of stage 1.
- **Decisions at review, 2026-10-29:** the operator and interpreter decided the labels interpretation and implementation path knowing stage 1's results, before any stage 2 output exists. The operator selected path (a), one successor released before any stage 2 launch; no A5 labels for the three A6 variants under the interpretation below; X2-1 only; the fixed-path clause subject to its pre-adoption check; and the stage 2 reader contract. Those decisions do not make the knowledgeable proposal blind. In choosing option (ii), the interpreter and operator knew the nominal family's stage 1 A5 label outcomes as well as the opened scientific reading; those outcomes were not supplied to the executor. This disclosure does not assert that the no-label choice was blind.
- **At adoption:** record the actual date, certification/review, operator approval, commit and byte hashes, and any intervening observations. Do not backdate the text.

**Scope and reason.**

The four families are `sqrt`, `crowding`, `sigma_squared_x10` and `sigma_squared_x0.1`, independently. The procedure starts only after a family's original A4 validation is complete, its candidate and sidecar are assembled, and publication is refused under A13 Part 2. It never applies to the nominal family and never reopens A13 or A14. A family admitted at its original check has no extension opportunity.

A13 Part 2 remains unchanged: floor(0.001 × own primary rows), at most one residual row per lookup context, no balanced witness, and all its screen, support, no-violation, binding, recording and reporting requirements. The 2,875-primary-row square-root and crowding families each have a cap of **2**; the 625-primary-row σ families each have a cap of **0**. Consequently, a σ family must have no residual `not_estimable` primary row to publish. An extension cannot repair an FV failure, a sensitivity failure or any other ineligible defect by changing its status.

**What this amendment supersedes, for successor-identity stage 2 execution only.**

- **A14 order step 1's current-pin rule:** launches at the successor identity released under this amendment pin **the A16 commit**, with the execution checkout's design note byte-identical to the note at that commit. The strict checks must retain the A13 clarification and A14 text as historical registration and include this amendment.
- **The identity boundary:** A14's rule continues to govern every launch at `174ab660` and earlier identities. This clause does not authorize a new stage 2 launch there, rewrite an old checkout or retroactively repin a completed launch. Carried-forward historical plans and their publication evidence verify historically by their original committed pin/ancestry/hash, under the existing historical-verification procedure.
- **The coordinated change:** `artifacts.py:238 to 245`, `table_validation_a4.py:745 to 747,791 to 811` (with its historical/current selection and writing `candidate_unpublished_tables.json`, `.cell_results.json` and `.compatibility.json` in `run_root` before re-raising a Part 2 refusal, without touching the final target), and `table_labels_a5.py:745` change together. Original stage 2 validation under the new pin must retain A13 Part 2's prospective admission binding; a new pin cannot silently disable it. A15 remains separately bound budget authority.

No A13/A14 nominal-family extension, historical refusal, finality rule or Part 2 condition is superseded. The new stage 2 extension opportunities are only those expressly defined below. Literal path (b) is withdrawn. Revised (b′) was considered and not chosen.

**Labels interpretation, prospective decision of 2026-10-29.**

A10 §7's “each arm's family” refers to A10's arms: the k* arms, the c^0.5 arm, and A6's arms that use the nominal tables (the weight corners and the horizon); their families are the nominal family and the c^0.5 family. A10 §12 lists “A6's variant families” separately, as families re-registered unchanged under A6, whose text says “No A5 labels are made”. Therefore `crowding`, `sigma_squared_x10` and `sigma_squared_x0.1` make no A5 labels. The operator selected option (ii) of `LABELS_A6_VARIANTS.md`; the successor implements the following authenticated policy before any stage 2 launch:

- Key the exemption only by the **validated family identity**, never by the absence of a label file or an unverified flag. Nominal and sqrt retain strict A5 receipt/coverage checks.
- At `production_tables.py:148 to 184` and `tables_a10.py:300 to 324`, provide a distinct/versioned sealed no-label receipt binding the family, table and validation hashes, accepted producer, constants/calibration and this adopted interpretation's authority. Preserve complete validation, support, sensitivity, Part 2 admission and provenance checks. Do not invent an empty A5 seal or a false `labels_sha256`. Bind the policy and full input closure in the builder/snapshots.
- On an estimated FV row, use the same continuation, flow, errors and support in the same numerical lookup and score. Missing/not-estimable rows and missing continuation bins retain their existing, distinct unavailable behavior. No label-dependent exclusion, fallback, reweighting or preference is introduced.
- The reading states that these families make no A5 labels and that their FV rows remain **asymptotic and uncertified**, as A6 directs; it retains all A4/A13/A16 qualifications and incidence. Missing A5 is not called an unresolved A5 test.

This interpretation and its acceptance-policy implementation change no numerical lookup, registered quantity, original scientific seed/count, admission threshold or reading rule. They resolve the existing receipt guard's conflict with A6's specific scope; they do not add label phases or budgets.

**Family publication and the fixed paths.**

The following clause is incorporated verbatim from the six-item proposed insertion in `A16_FAMILY_PATHS_CLAUSE_DRAFT.md`, subject to its own pre-adoption check. The separately resolved A5 policy it mentions is the clause immediately above. Its metadata check remains a gate; this drafting task has not claimed that it passed.

1. **When fixed.** Before any of the four stage 2 families is built, this clause fixes their final publication targets. These names apply to original validation and either A16 round, whether or not an extension is needed. They are literal POSIX path strings relative to `simulation/`, not absolute checkout paths:

   | Family identifier | Final table publication target |
   |---|---|
   | `sqrt` | `v3/runs/a10_stage2/sqrt/v3_rerun_tables_A10.json` |
   | `crowding` | `v3/runs/a10_stage2/crowding/v3_rerun_tables_A10.json` |
   | `sigma_squared_x10` | `v3/runs/a10_stage2/sigma_squared_x10/v3_rerun_tables_A10.json` |
   | `sigma_squared_x0.1` | `v3/runs/a10_stage2/sigma_squared_x0.1/v3_rerun_tables_A10.json` |

2. **Other strings in the same seed closure.** Before building any family, freeze the following calibration strings in the same committed path manifest:

   | Families | Calibration string |
   |---|---|
   | `sqrt`, `crowding` | `v3/runs/registered/v3_rerun_calibration.json` |
   | `sigma_squared_x10` | `v3/runs/a10_stage2/sigma_squared_x10/v3_rerun_calibration.json` |
   | `sigma_squared_x0.1` | `v3/runs/a10_stage2/sigma_squared_x0.1/v3_rerun_calibration.json` |

   The two σ files are verified byte-for-byte copies/aliases of the already pinned A6 variant calibrations, not regenerated calibrations. Their bytes, payload seals and producer identity must satisfy `a10_constants.json`. The calibration/table strings in each job and, where present, its `a10_seed_source` are frozen together. The nominal comparator keeps its existing calibration and table identity/path; this clause does not rebuild it or redefine any stage 1 seed.

3. **Before adoption and preparation.** Check the four targets' no-overwrite status and all earlier frozen preparation manifests using metadata only. Do not claim they have never been written without that check. If an earlier approved manifest has already fixed a different seed-bearing string, stop preparation and resolve the discrepancy explicitly before adoption; do not silently substitute the names above. Commit the complete canonical path manifest, the deterministic job/seed inventory and its construction rule before simulation. The successor builder must assert those exact strings and perform the A6 global seed check on the corrected A10 job/stream inventory.

4. **What stays fixed.** A refusal, an extension, re-assembly, a new execution checkout or a different scratch root cannot change the final target or the seed-bearing strings. Stage-specific candidates, refusal records and round evidence use separate immutable roots; an extension never publishes into a round-specific replacement path that would alter the runs' configuration. Verified snapshot/alias resolution can map a logical input to another physical location without rewriting the job configuration. Preserve `correct_runs`' original seed source and counterpart equality; do not claim pairing to a historical R4 job unless its exact source configuration is verified. Fixing a path here is not permission to redraw a seed after a collision.

5. **The guard and the receipt.** The existing no-overwrite guard applies. A refused candidate is not a final published family. A13 Part 2 admission is checked first, unchanged (caps 2, 2, 0, 0 respectively), after the original validation or the last permitted A16 re-assembly. The family identity record names the exact final file and hash, under the existing approval/public-record procedure. Validation receipts retain the original plan hash and stream fields, and add each used extension plan, stage hashes and complete seed manifest. The A10 receipt follows the operator's separately resolved A5 policy; this clause makes no labels decision.

6. **Unchanged.** No registered quantity, cell, replicate count, test, reading, admission threshold or existing nominal path changes. The purpose is to remove a previously unspecified input to deterministic job/seed construction before stage 2 outputs exist, following A13 step 7. This clause authorizes no launch.


**Reader contract.**

`STAGE2_READER_REQUIREMENTS.public.md` (SHA-256 `685f05ec58cb2bb84914163de57107ee4f3e557650d7717e1c1a2e8be56a52d5`), committed in the repository alongside this amendment and frozen by exact repository path and SHA-256 file hash at adoption and release, is the stage 2 reader contract. It implements A12 item 7 with an explicit per-family undefined-resample tail: 0.05/36 for A10's sqrt boundary and 0.05/66 for A6, recording the actual family threshold in both the comparison result and the undefined-resample reason string while preserving family sizes 18/33, registered streams, censoring and verdicts. It treats **“no admitted rows”** as a verified reader state, not an inference from a missing field: verify the family/receipt and complete context coverage, distinguish structural zero numerators from measured incidence, derive exact branch denominators from preserved evaluated-decision evidence, pool predefined contributing runs, and mark zero denominators unassessed. Missing incidence on a nonempty-admission family is an integrity failure. Never fabricate a denominator, silently omit a side, alter production inertness or call unflagged quantities certified unaffected. The contract's labels branch is resolved by the no-A5 interpretation above. Stage 1 readings/verdicts are not opened or recomputed by this procedure.

**Assumptions.**

A13 assumptions 1 to 3 apply separately to each family and fresh round. Given the fitted family and earlier history, pseudo-random streams are assumed to behave as independent ideal generators; integer disjointness alone proves no probabilistic independence. Trajectories use the unchanged initial law and full registered horizons. The stop and second-round eligibility inspect visit indicators, not residual marks. Thus the first N* visiting trajectories have the conditional-on-a-visit law used by A13's bound. No cross-row independence is needed for that bound.

**The rounds.**

1. **Original records and first-round eligibility.** Copy by hash, into a read-only verified view, the original refused candidate, sidecar, admission record, source family, validation plan/receipt, source/fit/validation/census records, original code/registration identities and cost projection. Preserve all originals, including the refusal. A malformed or changed record is a finding, not a reason to omit a row.

   Apply A13 item 1 exactly, per primary row: plain route; `not_estimable` only for “A4 availability floor failed”; passed base screens; positive validated support; sensitivity not `False`; `living_ok=True`, `low_assessed=True`, `low_ok=False`; unresolved C0; no cell violation; published C0 fit; and 7wL/[3(n_orig−1)] > τ, treating n_orig<2 as satisfying the arithmetic condition. Evaluate the full set, without choosing a convenient subset. Record one eligibility boolean per row and the selected rows/source jobs by identifier. Call its size E. Preserve every ineligible row and sidecar entry byte for byte.

2. **Constants and N*.** Use A13 item 2 unchanged: α=0.05, L=log(4M/α), τ=0.05 times the row's flow range, its original a priori width w, and N*=1+ceil(2×7wL/(3τ)). Use the original code expression and verify its deterministic term at N* is at most τ/2. M is the original sealed family's plain allocation count, including sensitivity rows and each C0 allocation; P is its sealed number of primary plain rows. They are not reallocated after a refusal. Record P, M and E publicly; widths, N* and per-row reach remain executor-only. Recompute and verify the same constants in round 2; a difference is a finding.

3. **Data and seeds.** Each round has a separate phase and job kind, `validate_plain_a16_r1` / `a16_validate_plain_r1` and `validate_plain_a16_r2` / `a16_validate_plain_r2`. Only distinct source jobs of eligible rows run. Each replicate has 2,048 trajectories in 32 groups of 64, at the original horizons. The worker reads fit/A1 inputs and the frozen eligible set, never earlier validation or extension statistics. Neither phase enters the ordinary validate index. No original or earlier-round trajectory is pooled into a new test.

   **Disjoint ranges by construction.** Fix the family index f as 0=sqrt, 1=crowding, 2=sigma_squared_x10, 3=sigma_squared_x0.1, and round q∈{1,2}. Its block base is `2^62 + (2*f+q-1)*2^60`. Add `continuation_validation._truncated_sha` (the upper 60 bits of SHA-256 of the UTF-8 concatenation `"".join(str(part) for part in parts)`, a value below 2^60, as in A13 and A14; it is the only `_truncated_sha` in the source manifest at `174ab660`) applied to the unambiguous tagged tuple `("v3_A16_ext/", family, "/", q, "/", source_seed, "/", replicate)`. Round 1's replicate ordinals are 4…35; round 2's are 36…67, irrespective of round 1's realized or allowed length. The unchanged primitive accepts any contiguous run of ordinals from 4; round 1 needs no adapter. The canonical family names contain no separator.

   The eight disjoint blocks reserve **[2^62, 12×2^60)**. They are outside the ordinary truncated-hash range below 2^60, A13's [2^60,2^61), A14's reserved [2^61,2^62), and stable-job/qualification/rehearsal streams in [2^128,2^129). Stage 2's original streams retain their registered generators and `correct_runs` counterpart seed-source equality as governed by item 4 of the family-path clause above; they gain no right to use A16's blocks. Configuration tests, forecasts and rehearsals cannot use these blocks.

   Before any extension simulation, freeze the full allowed manifest, including unused replicates, and check pairwise uniqueness and exclusion against the complete registered, planning, probe, pilot, rehearsal, qualification, configuration, A13, A14 and stage 2 inventories. Verify that historical generators/manual seeds have not already occupied a block. A collision or incomplete inventory is a finding: do not redraw or shift a block. Later phases, including A5, forbid the entire reserve and both full manifests. The manifest contains allowed seeds, never merely the realized subset.

4. **Stop and test.** Preserve A13 items 4 and 6. Process trajectories in (replicate ordinal, batch index) order. A visit is at least one covered living-source C0 transition. Each source job stops after the first complete replicate in which every eligible row reaches its own N*, or after R_max replicates. No row is truncated because another finishes. Record ordered (S_i,N_i) pairs. Test exactly the first N* visiting trajectories of that round alone with the original two-sided empirical-Bernstein test and the visit-weighted safeguard on the same trajectories. Unreached rows remain `not_estimable`; unresolved or violation results remain so. A tested row never receives another extension test, including a row whose safeguard or floor fails. For round 2, the adapter presents the identical ordered pairs to the unchanged test primitive with replicate ordinals re-based by subtracting 32 (36…67 becomes 4…35), and changes nothing else; the sealed source records retain their original ordinals.

5. **R_max, its floor and price.** For either round, let J be the entire frozen eligible source-job set. Using the original registered cost projection, define

   `B_j = x2_hours_max(family.capability.setting.validate_plain) / jobs(family.capability.setting.validate_plain)`;

   `S = sum_{j in J} B_j/3`, counting a source once;

   `R_max = max({R integer: 0≤R≤32 and R*S≤15})`.

   Verify the projection's full file SHA-256 `78a1d3ac253048c7e077b0e4eb12dd3150fa178cf3e63a24c6f0d87f02a8ad8d` and payload seal `5ca5225967cf08ad5636f98f12d57fa6ccd753a7ae126bff0edcc09f0af3d8a3`, and equality to the projection seal bound in that family's sealed original validation plan. Each stage 2 family's sealed original validation plan binds that projection seal, as `pull_dispatch.projection_sha256` or a named equivalent field at the successor, before its validation launches; a plan without that binding cannot enter this item. The binding is covered by the original plan file's SHA-256 recorded in the A16 plan, as A13 records `original_plan_file_sha256`, since the A4 `plan_hash` does not cover dispatch fields. A stratum `{family}.{capability}.{setting}.validate_plain` absent from the projection, or whose `x2_hours_max` or `jobs` is missing, non-finite or non-positive, is a finding: no substitute price, class, mean or measured duration may stand in for it. A13's “Clarified, pricing R_max” applies: B_j is a whole fit/three-validation/census bundle with its registered effective workers, realism factor and relative throughput already included. Dividing the maximum bundle by three is a conservative pricing convention, not a measured replicate duration. Per-stratum prices remain executor-only. Publish R_max and R_max*S as a **budget estimate** resting on those frozen classes. Visit counts, measured extension durations and the probability in item 6 never choose R_max.

   **No launch below 6**, in either round. This retains A13's policy floor based on N*≥2n_orig and its six-replicate extrapolation; it is not a power guarantee. **Departure from A14:** its floor of 24 came from its disclosed nominal-row forecast and is not a universal consequence of the test. Transferring it to four unseen families would assert unsupported power. **Departure from A13:** allow up to 32 in the first round, as in A14, because A14 expressly identified the arbitrary 16 ceiling as the first round's design error. Both changes affect cost/power only. Flag N*>2,048R_max as deterministically impossible, without deleting the row. A future forecast informs the go, not these rules.

6. **Predicted admission probability before each round's go.** Freeze and rehearse a family-general implementation before any stage 2 validation output exists. It reports the probability of **every** Part 2 condition after that round, not just the total-row cap. This is an **operational budget estimate of admission probability**, resting on the model below; it is neither a certified probability nor a registered scientific reading. No numeric probability is supplied in this draft.

   Inputs are only that family's verified original visit indicators/totals, earlier completed extension indicators/totals if any, N*, unchanged census/support or verified floor-with-C0 flags, contexts/screens, frozen eligibility/R_max and prior extension certification/violation counts. Nothing from the prospective round enters. Baseline reach uses the A14 model: Beta(v+1,t−v+1) from earlier visit/trajectory totals, where v counts visiting trajectories and t counts simulated trajectories (6,144 originally, plus 2,048 times the source job's realized round-1 replicate count for the round-2 forecast), never step-level transition sums, and a beta-binomial visiting count for 2,048R_max new trajectories, evaluated by the normal approximation with continuity correction. Its mean is na/(a+b), variance nab(a+b+n)/[(a+b)^2(a+b+1)], with the tail at N*−0.5. Clamp numerical probabilities to [0,1]; invalid inputs halt preparation. Tooling or preparation-check failures before the round's go follow item 10's investigation-and-repeat rule.

   Use 4,000 Monte Carlo draws, canonical row order, independent row reach in this forecast only, and categorical certification/violation/unresolved outcomes conditional on reaching N*. Here the certification category means the C0 test certifies **and its safeguard passes**; the census floor is then applied separately. For round 1, with no prior extension tests, the baseline certification/violation rates are explicitly assumed 1/0. For round 2 use the empirical rates from this family's round 1 tests, or the same disclosed 1/0 assumption if no tests occurred. The second required number always uses certification 0.9 and violation 0. All simulated final statuses pass through the unchanged Part 2 predicates, including ineligible rows, context collisions, witness exclusion, safeguard/floor implications and violations. Preserve already-tested decisions; no draw “repairs” one.

   The forecast seed is the low 60 bits of SHA-256 of canonical JSON `["A16-admission-forecast",family,q,R_max]`; the two scenarios use the same seed and fixed draw order. Each scenario initializes `random.Random(seed)` afresh and takes its draws in canonical row order. Record it as non-simulation tooling, exclude it from simulation manifests, and disclose three-decimal estimates plus model assumptions. Freeze source/import/environment hashes and a read-only mapped input view. Public output contains the two estimates and counts, never N*, visits or values. **Departure from A14:** its three frozen scripts and nominal history cannot run unchanged for a new family or a first round. This prespecified adapter preserves the model and 0.9 sensitivity while replacing nominal paths, eligibility and the missing-history convention. Forecast uncertainty, cross-row dependence and small prior test counts limit its usefulness. The figures make no automatic go/no-go threshold; the operator's recorded go does.

7. **Second-round eligibility.** Round 2 is available only after a normally completed first round, verified re-assembly and a second Part 2 refusal. Recompute first-round classifications deterministically from the recorded first N* visiting trajectories, using the unchanged test. Verify equality to the sealed first-round admission evidence. Select only rows in the original E whose recomputed result says `unresolved`, reason **“N* not reached”**, and that have no cell violation. Call the size E₂. Eligibility never reads an S_i or magnitude of a positive N_i. Integrity checking can inspect structural validity/finiteness; an invalid record is a finding. All rows tested in round 1 keep that decision, whether or not they certified. Round 2 is not available after a first-round scientific halt, no-launch or terminal preparation failure. It never restarts round 1 under a new name.

8. **Re-assembly and admission.** Start with the original refused candidate. For each original eligible row replace only C0's decision with the decision of the round that tested it, or its terminal unreached decision. Preserve every test, safeguard, floor result and round marker, including violations, where admission verification reads them. Use admission scopes `A10_stage2_after_A16_r1` and `A10_stage2_after_A16_r2`, bound to the validated family and the immutable round/admission records in item 10. Store each round's re-test marker at `row["a16"]["rounds"]["r1"]["retest"]["status"]` or `row["a16"]["rounds"]["r2"]["retest"]["status"]` (with `visit_weighted_ok` and without visit counts `n`/`n_traj`), respectively. The successor adds an explicit parallel A16 check in `admission_a13.verify`, validating family/round provenance from the fields and record hashes bound inside `admission` (cross-checked against `manifest["a10"]["family"]` in the loader and against the on-disk item-10 records at publication) and rejecting any violation in either retained marker as well as the unchanged cell-test and A13 checks; round 2 cannot hide round 1's marker. Recompute validated support and reapply the unchanged census/floor. Every ineligible row, its sidecar, sensitivity processing and sensitivity siblings must remain byte-identical. A mismatch halts. Check all Part 2 conditions and write an immutable admission record before publication. A passed round-1 admission publishes immediately and permanently forecloses round 2; no extension improves an already-admitted family.

9. **Error accounting.** Extend A13 item 9 and A14 item 10 to each stage 2 family using this procedure. H is its fitted A1 family and sealed validation plan; D₀ adds original validation/census. Original false certification is bounded by α given H. Conditional on D₀, each of the E originally eligible rows has at most one extension test. Let q_j be its round-1 reach probability. Its round-1 test, which happens only on the event that it reaches N\*, falsely certifies with probability at most q_j·α/M given D₀. Conditional on the history through round 1 and the round-2 launch decision, its round-2 false-certification probability is at most α/M if it is eligible and the round launches, and zero otherwise; eligibility requires that it did not reach N\* in round 1, so averaging over that history gives at most (1−q_j)·α/M. No test occurs in the latter branch unless the former did not reach N*. Hence the total added bound is Eα/M, not 2Eα/M. No independence between rows is used.

   Report E, E₂, actual test counts in each round, P, M and αE/M. If M=0, then P=E=0: define αE/M and the plain false-certification bound as 0, without division; the plain certificate is vacuous. The following formula and each family's summand apply for M>0, with a zero summand for M=0. The plain certificate becomes **at least 1−α(1+P/M), given H**, and at least 0.90 unconditionally over fitting, since E≤P≤M. It is not a guarantee conditional on refusal or final publication. FV certification is unchanged. Do not claim a joint 0.90 or 0.95 certificate across four families: a union bound over four extended families is at most `sum_f α(1+P_f/M_f)≤0.40` for any plain false certification. This does not change the registered reading multiplicities.

   The argument fails with a fresh extension test for an already-tested row, pooled rounds, changed N*/w/τ/M/α, stream overlap, outcome-selected source subsets, certification from a halted round, redraws on resume or failed stream assumptions. Deterministic recomputation and exact compatibility replay are not fresh certification opportunities.

10. **Reservations, halts and finality.** Before any registered preparation checks, reserve one family anchor as a sibling record of the family's never-written, already frozen publication target by replacing `<target>`'s trailing `.json` (`Path(target).with_suffix(...)`, as in A13/A14) to form `<stem>.a16_family.json` (for sqrt, `v3/runs/a10_stage2/sqrt/v3_rerun_tables_A10.a16_family.json`, the `.json` suffix of the target replaced as A14 forms `…A10.a14_round.json`), with separate round records `<stem>.a16_round1.json` and `<stem>.a16_round2.json` and admission records `<stem>.a16_round1.admission.json` and `<stem>.a16_round2.admission.json`. Each family and round record is created only if absent and updated only through monotonic lifecycle state transitions (initial reservation, completed plan binding, launch spec/root binding, append-only pre-go tooling-failure log, or terminal refusal/halt latch), never overwritten by a new reservation; each admission record is written once, only if absent. A repeated preparation after a logged pre-go tooling failure may rebind the completed plan on the same anchor, with every superseded plan hash retained in the append-only log; the launch spec/root binding is made once and is never rebound. The target file itself is written only by publication under the existing no-overwrite guard. Bind family, original plan/candidate/admission hashes, round, code identity and later the completed plan/spec/root. Record a failure even if preparation cannot finish writing its plan. A different directory, plan name, host or root cannot obtain another realization. Rehearsals use separate output-relative anchors.

   A scientific halt certifies nothing from that round, spends it and latches the family terminal. An infrastructure interruption resumes the same preparation/launch, exact seeds/spec/identity/environment and remaining budget; preserve completed replicates and restart only an uncheckpointed in-flight replicate from its seed. Prior-round records are never latched or rewritten by a later round. A changed runtime requires qualification; an unfinished launch never resumes at a new identity.

   From registered round-1 entry, a no-launch (including R_max<6, E=0, collision, substantive finding or explicit operator decline), a scientific halt, or an original defect that cannot be repaired by this procedure ends this family's extension sequence. “Cannot be repaired” is checked mechanically: even granting C0 certification and the safeguard to every eligible row and applying the unchanged census/floor still fails Part 2 because of carried-forward defects; it is not discretionary row selection. At round-2 preparation apply the same mechanical check to E₂, granting hypothetical C0 certification and the safeguard only to E₂ while holding ineligible rows and all round-1-tested decisions fixed and applying the unchanged census/floor. Scheduling delay is not a decline. A normal round-1 completion that still refuses admission may proceed once to round 2 under item 7; E₂=0 or failure of any round-2 entry/launch/admission condition is final. There is **no third round**. Preserve all refusals and outcomes; the dependent arm is reported not run and its comparisons follow the existing unavailable/undetermined rules. Other families continue independently. Reconcile and release unused reservations; never spend them to create another opportunity.

   Before registered entry, a rejected code review, rehearsal mismatch or failed identity proof is not a family-round outcome. Preserve the failed identity-pair attempt. Investigate and correct it under A11/A12 before entry, without reading future registered-round data. If the original producing identity cannot reproduce an input either, it cannot be carried forward. No tolerance or replacement sample cures that finding. A tooling or preparation-check failure before the round's go, including after registered entry while no launch root is bound, is also not a family outcome: record the failure append-only on the unlaunched anchor without latching terminal refusal, investigate and correct it under A11/A12 without reading prospective round data, and repeat the same preparation. Keep its anchor, family, original hashes, seeds, eligibility, constants and remaining budget; if the correction changes `code_identity()`, require committed, approved direct A11 compatibility records to the repaired identity before repeating preparation, and record the prior attempt on the anchor; never create another realization or migrate an already launched round. This exception does not waive a confirmed substantive finding, such as a missing/invalid stratum price, collision or corrupted registered input, or any scientific halt, explicit decline or mechanical no-launch condition. The classification of a failure as tooling rather than substantive is recorded in the family anchor, with the interpreter's review, before the preparation is repeated.

**Costs and ceilings.**

For each family and each of its two rounds, A15 v3 proposes **48 X2-equivalent hours**, including all preparation, qualification, forecasting, configuration, execution, checks and re-assembly/publication associated with the round. Its distinct registered-class simulation-price limit is **15** as in item 5. Those are different constraints: a class-price budget estimate is not the actual metered charge. The launch must satisfy both, with explicit wall/cleanup reservations; actual time is metered on X2-1 at its measured X2 reference rate of 1.0. **Implementer note:** bound the launch spec's `x2_equivalent_hours` by the 48 h round ceiling less non-launch round reserves, including charges already incurred; do not inherit A14's `15 + 6` formula. The separate `R_max*S≤15` class-price limit remains unchanged.

The **budget estimate per available round is 36 X2-equivalent hours**: `2×15 + 6 = 36`. The assumed factor 2 accommodates memory/tail/host variation in transferring a class-price envelope to an actual charge; the assumed 6 h covers preparation, forecasts, qualification/configuration and rechecks. Measured historical launch charges were A13 **5.80 h over 10 source jobs** and A14 **9.77 h over 4**; their arithmetic is 0.58 and 2.4425 charged h/source respectively, with different bounds and early stops, not interchangeable replicate rates. A14's disclosed class-price **budget estimate** was 7.37 h at R=32; 9.77/7.37≈1.326 is supporting evidence for a margin, not a universal multiplier. The 48 h ceiling is `30 + 18` rather than the 36 h budget estimate: the 18 h is the 6 h assumed overhead plus 12 h additional margin. No observed stage 2 eligibility or reach was used to set it.

| Family | Round 1 budget ceiling | Round 2 budget ceiling | Conditional two-round budget estimate | Combined ceiling |
|---|---:|---:|---:|---:|
| sqrt | 48 | 48 | 72 | 96 |
| crowding | 48 | 48 | 72 | 96 |
| sigma_squared_x10 | 48 | 48 | 72 | 96 |
| sigma_squared_x0.1 | 48 | 48 | 72 | 96 |
| **Total if every opportunity is used** | **192** | **192** | **288** | **384** |

These conditional budget estimates assume every possible round launches; they predict neither refusal nor admission. The per-round schedule budget estimate is 36/24 =1.5 continuous active days on X2-1 at rate 1, on the same class-price/overhead basis. Stage 2 runs on **X2-1 only**; X2-2 is permanently unavailable to this study. Any other host requires a new dated amendment. If the frozen full-source class sum gives R_max<6, money left elsewhere does not lower the floor or authorize a subset. A later budget amendment cannot silently increase the 15 h class-price limit or R≤32 scientific procedure.

**A small-family admission option is not proposed.** A13's certification error calculation concerns false certifications; admitted residual rows remain unavailable and are not certifications. It therefore supplies no justification for a positive minimum allowance in a family below 1,000 rows, nor any behavioral/bias bound for such an allowance. The requested “if and only if” condition is not met. Adopting a different minimum would need a separately justified admission-policy amendment; it is not hidden in this extension or its error statement.

**The order of steps.**

1. Review/certify this prospective text and its deviations from A13/A14, with independent certifiers from different model families as in A14. The operator approves the concrete text. Commit and publish it in `simulation/diagnostics/v3_rerun_design_note.md`, alongside A15's budget authority, A15's named arithmetic copies, `STAGE2_READER_REQUIREMENTS.public.md` and `A16_FEASIBILITY.public.md` in the repository, before any stage 2 launch. Record exact repository paths, SHA-256 file hashes and knowledge at adoption. At adoption, align the plan's A16 citation with the adopted filename and exact text.
2. **Selected path (a): build, rehearse and prove one successor identity before any stage 2 launch.** The change inventory is `A16_FEASIBILITY.public.md` (SHA-256 `1f0c1b052b93717130bf7d5f93a7489577625d27ccb6c512c3364c1d0ba5909d`), §§0 to 2, with its labels choice resolved by the clause above and its implementation path resolved here. It includes the committed stage 2 run-spec builder in simulation code; the A10-aware global seed registry covering original jobs/streams and all exclusions/reserves; the three pin sites changed together; authenticated variant no-label receipts and full snapshot/input closure; the A12 tail interface and reader-state contract; and all family-specific A16 preparation/history, both phases, anchors, seed guards, immutable publication evidence, forecast tooling and replay adapters. Preserve existing scientific primitives and A13/A14 behavior, apart from the explicit acceptance/pin/seed-guard/interface changes. Record every actually changed file, its reason and required A2 re-pin. The full successor hash is recorded after the approved code commit, never invented here. A15 supplies a separate **96 h budget ceiling**; the **74 h release budget estimate** rests on feasibility v2's historical proof-cost proxy plus 28 assumed operational/audit-fix hours. The reference imports the inventory and selected path-(a) proof work, not unselected paths or historical host options.
3. Rehearse all four family identifiers, both rounds, no-op and positive original-validation admission at the new pin, never-retest enforcement, global seed exclusions, shared-source stopping, no-launch and halt finality, immutable anchors, resume/checkpoints, exact unchanged rows, forced round-2 violation/refusal, sqrt's A5 receipts, each authenticated no-label variant receipt, negative cross-family/exemption cases, and loader/run equivalence. Exercise the committed stage 2 builder and exact path assertions. Prove adapters re-execute in empty scratch: perturbing a recorded checkpoint and output together must produce a mismatch. Rehearse forecast inputs/import isolation, the reader's two tails and no-admitted/mixed-family incidence, and the actual direct single-host `production_runner` transport on X2-1 before registered entry.

   **Large-integer seed rehearsal:** carry a seed **at or above 2^63** end to end through preparation, dispatch and completion records, checkpoint/resume, full manifests and publication receipts, checking exact integer/text equality at every boundary and after serialization. The σ families' A16 blocks begin at 2^63; signed-64-bit overflow, floating-point conversion or truncation must fail the rehearsal. Actual non-registered simulation streams remain outside every reserved range: use an allowed rehearsal seed in [2^128,2^129), which also exceeds 2^63. In addition, exercise exact σ-block values at/above 2^63 through the same record/manifest/receipt serializers in a metadata-only fixture, without drawing from those reserved streams. No fixture may reserve or mutate a registered family anchor. This preserves the original reserved-range prohibition while checking the signed-64-bit boundary explicitly.
4. Accept post-update original-identity requalification and then the required A11/A12 successor-identity proofs, with exact samples frozen, interpreter review, operator approval and committed/public records. A11 admits unchanged carried-forward computations, not the new extension; this amendment alone admits the latter. Separate these identity and environment comparisons as specified in `A16_FEASIBILITY.public.md` §2. A fixed-code environment pass comes first; a separate later successor-code replay under that accepted runtime provides A11/A12 evidence. A single successor execution cannot prove both transitions. For every carried producer, the accepted A11 record must target the successor directly; records ending at `174ab660` do not grant transitive acceptance at the successor.
5. In a fresh approved execution checkout, perform each family's original estimation/validation. Attempt Part 2 publication. Only a sealed refusal can permit this family's registered first-round preparation. Freeze its full eligible set, constants, pricing, impossible flags, global seed manifest, probability estimates and public summary; review before the exact launch go.
6. Launch the round on X2-1 through direct single-host `production_runner`, as A14 did, with its own frozen spec/root, budget reservation, machine-register entry, load sheet, pre-launch configuration test, `llm down` and supervised restoration. Here the machine-register entry is the host's qualification record under the operating rules, not pull dispatch; no pull-coordinator execution is authorized by this clause. Verify completion, deterministic recheck and no halt. Re-assemble and check Part 2. If refused after normal round 1, repeat the round preparation, freeze, review and launch parts of steps 5 and 6 for round 2 under its narrower eligibility; the original estimation, validation and Part 2 attempt are not repeated. A scientific halt/no-launch follows item 10 instead.
7. Publish only at the applicable fixed target in the incorporated family-path clause, after its metadata/no-overwrite checks pass, with the existing no-overwrite guard. The receipt preserves original `plan_hash` and `stream_seeds`, and adds per-round plan/public-record/output/admission hashes, full seed manifests, original and intermediate refusals, and a union `extension_seed_manifest`. It does not publish realized stopping replicates or a used-seed subset. Verify round-plan hashes against their approved public records. Carry the new family's identity/sidecar/receipt through the existing exact-file identity approval and required record-only/public commit.
8. Only then do dependent labels (sqrt only), authenticated variant no-label receipts, runs and the separately sealed stage 2 readings proceed under their own gos and the reader contract above. The operator's separate go is required to compute the sealed reading and to open it. Keep the original scientific job inputs, registered simulation seeds, path strings and run IDs; record provenance-dependent envelope/plan-ID changes as A12 requires. No stage 1 verdict is recomputed.

**Unchanged.**

- The nominal family, A13/A14's historical scope/finality and refusals, and all stage 1 outputs, seals, reading registration and verdicts.
- A13 Part 2 in full, including zero allowance below 1,000 rows, per-context/witness limits, unavailability behavior and incidence reporting.
- The instrument, calibration, grids, contexts, original estimation/validation/run/label seeds and counts, trajectory size/horizons, census, α, τ, support/floor caps and minimum, Bernstein test, N* formula, quantities, predictions, readings, gates and citation rules.
- Exceptions are the added validation samples and their prospective two-round procedure, the extended families' stated plain error accounting, amended family bytes/provenance and receipt fields, and the execution support/pin changes, resolved no-label receipt policy, fixed publication/calibration path closure and reader-contract implementation explicitly listed here. They authorize no change in a registered scientific quantity or reading.
- A15's ceilings remain budgets, never quantities or predictions. This amendment creates no budget by itself and no automatic launch go.
