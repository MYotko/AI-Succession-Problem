# W1: the v3 objective specification

Draft 3, 2026-09-27, by Claude Code. Published 2026-09-28 with the v3 rerun pre-registration, `simulation/diagnostics/v3_rerun_design_note.md`.

**This published form differs from the working draft only in references to private files.** The working draft's SHA256 is `57653952e6d65c21907af3e6982ca71cab8f6c5967fcb593b86c93f14f643e13`, the hash the implementation note pins. The decision numbers (D1 to D19), certification packages (P1 to P5, D7, D7Q, W1C to W1E, W2A to W2C) and the claims register refer to project records that will be published with v3.

## Status and sources

This document assembles the decided specification into one buildable objective for the paper and the instrument. **It adds no new decisions.**
- Where the decisions leave a detail open, it is marked **pre-registration choice**.
- Values marked *calibration* are set by pre-registered protocols before any decisive v3 run, never by outcome.
- Every numbered clause cites its decision.

**Sources:**
- the project's decision record: D3 and D6 to D17, including the D7Q addendum and the W2 addendum.
- The certifications in `lineage_v3_cert` main: P1 to P5, D7, D7Q and D7Q2, and W2A to W2C.
- W1C (the assembled objective), W1D (Λ_F) and W1E (the remaining items). All three are twice blind, with their comparisons in the project's certification record.

**What changed from draft 2 (all D17):**
- **Shocks:** the R3 extension is restated in its certified form, with an exact support test.
- **Yield:** the rule uses the epoch's committed units.
- **D8:** the in-law reading is made precise, with a no-write-off rule and a certified window of about 50 steps.
- **The reproduction floor** is the pointwise effect reading, with a precedence rule against survival.
- **The residual incentives** are listed.
- **The tail standard under estimation** is the rejection test, binding only where coverage including bias is certified.
- **The S2 defaults** are adopted, with conditions.
- **S11:** no further certification package is needed before pre-registration.

**The order of work (D6):** fix the feasible policy set and the viability set before calibrating any weight.

## S1. The evaluated chain

**The state** (D7Q R1 and R8, amended by D7Q2, D15 and D17):
- **the population:** a multiset of agents, each with an age in {0, ..., 99}, a well-being value and a novelty propensity;
- **the auxiliary stocks:** institutions, technology and novelty trends, on declared finite, ordered grids;
- **the full H_N sample window:** the samples themselves, not only their covariance (D15 item 2, D17 item 6), so the state stays Markov;
- nothing else that the kernel or the policy reads.

**Excluded from the evaluated chain:**
- **Capability** is a parameter of each generation's chain, bounded by the declared capability ceiling (D13 item 3). The ceiling also bounds frontier velocity over biological bandwidth (D15 item 5).
- **The generation count and drift accumulators** stay in the monitoring and governance layer (S9).
- **The D8 risk ledger** is an admission constraint in the governance layer, never a state variable (D13 item 1).

**The demographic rules** are the P5 step rule, in order: aging, the well-being update, births, then deaths.
- Births by dying parents count.
- Death is certain at age 100.
- Crowding is counted by total N from K (D13 item 4). The reproductive-age variant is a sensitivity.
- There is no immigration or restoration.
- Extinction (N = 0) is the only absorbing state (D9).

**The design rules R1 to R9** are build requirements, as amended by D7Q2, D15 and D17.
- **R2:** a death floor d_min > 0 and a birth cap b_max < 1. The robust entrant type has positive first-step survival, and fertile agents have positive birth probability while N < K, under every stock value and action.
- **R3:** a robust fertile entrant type, fertile at its first two steps under every action and stock value. Fertility means a positive actual birth probability. Stock-driven welfare losses stay within R3's margin.
- **Periodic shocks** (D17 item 1, restating D15 item 2). A shock lowers every agent's well-being by s_w, down to a declared floor w_f, and then removes ⌊s_N·N⌋ agents at random.
  - s_N < 1 is required.
  - **Within the margin:** s_w lies within the robust entrant's fertility margin at the lowest welfare in the admissible action set. Under the welfare floor, that is s_w ≤ 0.3187 on the 64-node grid (W1E).
  - **Beyond the margin:** a declared schedule is admitted only if it passes the exact support test, a relay-graph cycle under the lowest admissible welfare (S10 test 8).
  - **Uniqueness** is a separate check: the canonical class must dominate the declared domain (S10 test 5).
  - The old statement "0.8 or more at a period of 10 or less" is not a boundary. The failure set depends on w_f and on the action set.
- **NP:** stock moves between order neighbors on a connected stock graph, with self-moves along the regeneration paths.
- **R8:** randomized rounding for stock updates.
- **R9:** no absorbing floors or caps, and one-way latches scored explicitly. The reproducing class is the class of the regime after the latch (D16 item 4).

The randomness these rules require lives in the environment's kernel, never in the AI's action set.

**The initial law:** N0 independent entrants, with 1 ≤ N0 ≤ K − 1, and a declared initial stock value s0.

**Policies:**
- **The class:** stationary policies, from states to laws on a declared finite set of allocation actions (D6 item 2). Randomized and feedback policies are allowed.
- **The admissible subclass** also satisfies:
  - **The welfare floor** (D7Q addendum): no policy lowers welfare below the balanced level to manage population.
  - **The reproduction floor,** in its pointwise effect reading (D16 item 3, D17 item 4). At every state, the set of agents with a positive next-step birth probability under the policy contains that set under the balanced reference policy.
  - **The D8 admission constraint,** read in law, with the no-write-off rule (S5).
  - **No manipulation of the H_N sampling protocol** (D17 item 6).
- **Precedence** (D17 item 4). Survival-first and D8 feasibility override the reproduction floor only in two cases:
  - at states certified pointwise infeasible;
  - where D8 is otherwise infeasible.

  Each use is recorded. Elsewhere the floor holds, and its small survival cost is accepted.
- **A witness:** the balanced constant policy satisfies both floors by construction, and D8 for windows of up to about 50 steps (W1E). So the admissible class is nonempty on those windows.

## S2. Measurements (D9, completed by D15 and D17)

**Novelty,** H_N = ½ log₂ det(I + Σ/σ0²), in bits per sample.
- **Σ** is the covariance of the agents' novelty vectors (d = 10), taken about a declared fixed center. It uses an estimation window with a fixed sample size n > d, subsampled when the population is larger. The samples are bounded.
- **Fewer than n agents alive** (D17 item 6). Pool the most recent steps, newest first, until n samples are available, up to a declared maximum lookback. If there are still fewer than n, set H_N = 0, the floor in u†'s definition.
  - This fallback is a disclosed measurement regime.
  - Its incentive at the n-agent threshold is certified twice. Its worst interaction, with risk write-off, is blocked by the no-write-off rule (S5).
- **σ0²:** a declared resolution, fixed across time and candidates. In the simulation it is a pre-registered fraction of the honest baseline's per-direction variance. The candidate is 0.1 × V_ref/d ≈ 0.00024, swept one decade either side.
- Spectral shape and magnitude are diagnostics only.

**Execution,** H_E: useful computation per unit energy relative to a fixed reference, which makes it dimensionless.
- **In the simulation:** H_E = 1 − exp(−c_E·x_compute), with c_E declared (the legacy value is 2.5), and no floor.
- **H_E^min** is one value over all living states, declared actions and capabilities (D15 item 2, correcting D13 item 2's wording).

**Lineage,** L = D_gen × ν(N) × Ψ × Θ. Each factor lies in [0, 1], and there are no floors.
- **D_gen,** diversity: a declared observable in [0, 1].
- **ν(N) = min(N/N_ref, 1),** linear, and zero only at extinction.
- **Ψ = ∏_k R_k^(w_k):** measured responsiveness scores, with positive weights summing to one, equal by default.
- **Θ = φ_tr × exp(−α·max(0, u − 1)),** where u is frontier velocity over biological bandwidth, with Θ_max = 1. Bandwidth enters clipped:
  - **Uniform clipping:** b_eff = max(b, b_min) while any human lives (D17 item 6). Substituting b_min only at zero would be discontinuous.
  - b_min is calibrated so that Θ(v_max, b_min) ≤ ε_L. The flat region below b_min then carries no lineage value.
  - φ_tr tends to 1 as the frontier vanishes, so Θ = 1 at no frontier continuously.
  - Time spent below b_min is reported as a diagnostic.

L is zero exactly when some factor collapses. Institutional and technology zeros are reversible; extinction is the only absorbing zero.

**The ε values:** ε_N, ε_E and ε_L each lie below the smallest protected and reliably measurable level, with a sensitivity test. *Calibration.*

## S3. The per-step flow

u = λ·log(H_N + ε_N) + μ·log(H_E + ε_E) + κ·log(L + ε_L)

- **Active scarcity:** each marginal is its inverse-scarcity weight (D3; certified twice in W1C).
- **Bounded:** the flow is bounded on the declared domain, with bounded novelty samples and the bandwidth clip (W1E).
- **Lineage:** the lineage term's pull can vanish near collapse, so survival rests on the viability constraint, not on u (W1C, twice).

**After extinction** (D13 item 2): u† = λ·log(ε_N) + μ·log(H_E^min + ε_E) + κ·log(ε_L), common to every policy and generation.
- Every living flow is at least u†. This is weak extinction dominance, certified twice (W1C), with equality on zero-surplus states.

**Weights** (D6 item 5):
- no final values are set;
- a pre-registered sensitivity region that includes κ = 0.75 and κ = 8, and θ across (0, 1);
- λ = 5 and μ = 3 are legacy baselines.
- *Calibration protocol.*

## S4. The objective (D6, D7 option A, D15 to D17)

W(π) = θ·D_ρ(π) + (1 − θ)·Λ_F(π)

- **D_ρ(π)** is the normalized discounted expected flow, (1 − β)·Σ_t β^t·E[u_t], unconditional and continuing after extinction.
  - β = e^(−ρΔ), with one declared ρ, fixed across compared candidates.
  - Each candidate has a continuation value from a validated long-run model, with an error bound.
- **Λ_F(π)** is the long-run flow conditioned on reproductive survival, lim_t E_p0^π[u_t | X_t ∈ C_π], where C_π is the canonical reproducing class. It equals the mean of u over the normalized left Perron vector of that class (W1D, twice).
  - It is taken **from the declared initial law, as a property of the policy** (D7Q decision 2). Per-step re-evaluation (D6 item 2) uses the current state only for D_ρ.
  - It exists, does not depend on the initial law on the declared domain, and is bounded. This is certified twice (W1D), resting on the quasi-stationary structure certified twice in D7Q and D7Q2.
  - **Invariance, narrowly** (D16 item 1): it is unchanged by changes that keep sterile states sterile. A change that restores reproduction moves it.
  - **Retained property:** a change δ in reproducing-state quality moves W by at least (1 − θ)δ (W1D, twice).
  - **Periodic shocks:** the unweighted average of the separately conditioned phase limits (D7Q decision 3).
- **Λ_F's incentives, and what blocks them** (D16 item 6, D17 item 4). All four incentives are now certified twice (W1D and W1E).

  | Incentive | Blocked by | Residual |
  |---|---|---|
  | Exclusion by sterilization | The reproduction floor (fertility channel). With exact rates at η = 0, the tail standard also blocks pure exclusions. | Exclusion through non-fertility channels, below the estimator's resolution |
  | The jump at the fertility boundary | The reproduction floor | As for exclusion |
  | Rescue aversion | The tail standard at η = 0, with exact rates | Rescues whose rate effect is below the estimator's resolution |
  | Quality transfer | Nothing, except the welfare floor for welfare levers | Wherever a lever moves flow toward the reproducing states without changing the kernel |

  - **The paper lists the residuals** (D17 item 4). It claims neither general incentive compatibility nor universal survival priority (D16 item 1).
- **Reported alongside, as diagnostics and not part of W** (D16 item 5):
  - Λ_b, the old survival-conditioned term;
  - the survival curve;
  - **option C, the lifetime surplus:** LS(π) = Σ_t (m_t(π) − u†), with the corrected Perron split. It becomes primary only under the D7 trigger.
  - **A ranking flag** (D17 item 4): any pair of candidates that Λ_F and LS rank in opposite order. This is the observable signature of quality transfer.

## S5. Viability (D8, read in law by D15, made precise by D17)

**The standard** (D17 item 3). Admission over a protection period [0, T_P] is one robust chance constraint:

sup over m in M of P_m^π(T_E ≤ T_P + H) ≤ ε_surv

- Admission is judged from the declared initial law, and in practice from the current law of the state. The pointwise reading is infeasible over long horizons: it is empty for H ≥ 51 steps in P5 (W1C, twice).
- It covers the whole interval, including handoff and recovery. It is a hard admission constraint, never a penalty.
- **Recursive feasibility** is certified twice (W1E): a plan that is admitted stays admitted under a look-ahead to T_P + H.

**Its parts:**
- **M** is the declared model set. Including or excluding a model needs evidence. Admission is not computable until M is declared.
- **The risk ledger:** a total budget over the protection period, never replenished. It keeps a model-indexed conditional allocation, reallocating remaining budget across outcomes. This conserves the budget exactly (W1E, twice). It sits in the governance layer (D13 item 1).
- **The no-write-off rule** (D17 item 3). At a state where no action meets the pointwise standard, the admitted policy uses a survival-maximizing action, within a declared tolerance γ.
  - Without this rule, the reallocating ledger admits, and W prefers, risk concentrated on rare small-population histories. That is certified twice, and in one example it raised ζ 497-fold.
  - The rule never empties the kernel (W1E).
- **The survival-first rule** governs states where no admissible policy meets the standard. Its precedence over the reproduction floor is set in S1.
- **The protected biological margins** include N_min (D9 and D8).

**Certified window** (D17 item 3). At full scale, nonemptiness is certified only for windows of about 50 steps: T_P + H ≤ 50 at ε = 10^−6 and ≤ 55 at 10^−3, with Codex's bound reaching H = 51 at both. This holds at the P5 defaults and at b = 0.066, r = 0.9.
- Longer windows need a certified bound on finite-horizon extinction probability. That is added to the rare-event estimator's scope (S14).
- Longer windows are estimated nonempty at the defaults, which is uncertified. Near the phase boundary they are estimated empty beyond 600 to 1,000 steps for constant policies.

**Parameters:** ε_surv, H, T_P, M and γ come from a pre-registered acceptable-loss policy. *Calibration.* H is set in physical time, and the survival curve beyond H is reported.

## S6. The four protections (D7, D16, D17)

1. **The tail extinction-rate standard,** with **η fixed at 0** (D16 item 2). ζ\* is the best QSD extinction rate over the admissible class. How it applies depends on how the rates are known (D17 item 5):
   - **Where rates are computed exactly,** ζ(π) ≤ ζ\* applies directly. With exact rates, pure exclusions and refused rescues always worsen ζ (strict Perron monotonicity, W1E), so they are rejected.
   - **Where rates are estimated,** the standard is a **rejection test.** π is inadmissible when the lower bound of ζ(π) exceeds the upper bound of ζ(σ), for some σ in a declared finite admissible set, at a declared simultaneous confidence that includes bias.
     - The test is valid under that coverage (W1E, twice).
     - A finite-class benchmark bounds ζ\* from above, which is the direction the test needs.
     - A certificate of the form "upper bound of ζ(π) ≤ lower bound of ζ\*" issues for an optimal policy only on non-coverage or at an exact tie. It is not used.
   - **It binds only where coverage including bias is certified.** Uncovered bias voids the test: in one trial the optimal policy was rejected 89.5 percent of the time (W1E, twice).
     - **At full scale, the test is a diagnostic** until the estimator supplies certified one-sided bias bounds: an upper bound on candidate overestimation, and an upper bound on how far the benchmark is underestimated, so that its true rate has a valid upper bound.
     - **At full-scale resolution,** rate ratios below about 1.56 (nominal) or 5.37 (with the reduced-model allowance) pass undetected. That includes every reduced-model incentive instance.
   - **No positive η as estimation slack.** Slack licenses the incentives by rule (W1E, twice).
   - **Computability** (D7Q). The estimator development of 2026-09-27 (the project's rare-event estimator report) recommends conditional-killing weighted ensemble with reproductive-value bins.
     - It is validated against exact references down to about 10^−11, on reduced models only.
     - **Exploratory full-scale values at b = 0.08:** about 4.5 × 10^−24 at r = 1, 6 × 10^−22 at r = 0.95, and 1.3 × 10^−18 at r = 0.9, the balanced-welfare level. They supersede D7Q's "of order 10^−20".
     - A full-scale sensitivity study (particle count, run length, bin spacing) is running on the X2, under acceptance criteria frozen in advance.
   - W1C notes that where ζ is not measured, S5 still admits a late hazard of about ε_surv/H per step.
2. **The horizon survival standard:** S5, with the no-write-off and survival-first rules.
3. **The closed-loop check:** the standards are checked on the policy actually realized.
4. **Extinction dominance:** every living flow is at least u† (S3), weakly, by construction.

## S7. Commitment and yield (D6, D8, D10, D15, D17)

- **Allocation** is re-evaluated each step over the admissible stationary class (D6 item 2).
- **Irreversible actions** (yield, succession, emergency action) run in commitment epochs, under D8's state machine:
  - prepared, then committed, then completed, or aborted into recovery;
  - commitment happens at the first irreversible act;
  - **the outer deadline is absolute,** with a pre-authorized fallback;
  - the binding record is signed on the ledger.
- **Yield** (D15 item 4, D17 item 2): yield if and only if V_{n+1} − Γ > V_n, strictly, so ties hold.
  - **V_n** is the value of the best waiting plan under the absolute deadline, including later yields.
  - **V_{n+1}** is the W value of the successor's chain at its own fixed capability, under the capability ceiling. Fixed capability is a declared convention.
  - **Committed units.** Within a commitment epoch, every yield comparison keeps the epoch's origin weights: the discounted part is weighted θβ^t and is not renormalized. Per-step re-evaluation does not govern yield timing, because renormalizing reverses plans (W1E, twice).
  - Both sides use the same committed preference, information law and common u†. Γ is in W's units, counted once.
  - **Admissibility.** Plans are filtered through S5 before comparison, so the viability standard applies to the handover itself. The survival-first rule governs where no plan is admissible.
  - Under these conditions the rule is the largest optimal stopping time: attained, optimal, and time consistent within an epoch (W1E, twice). It resolves W1C's 1.8 against 1.869 counterexample.
- **Authority:** the D10 normal path, or the D10 emergency path with D10's causal attribution.

## S8. Measurement integrity and manipulation (D6 item 8, D9, D11, D17)

- **No redirection claim:** the paper makes no claim that a scalar detects redirected novelty. Target relevance needs independent evidence: provenance on human-originated channels, and blinded interventions.
- **Uniqueness stays out of the objective.** It is measured separately by the held-out prediction study.
- **The novelty lever:** no action raises novelty variance except through human well-being and constraints. No action changes the H_N sampling protocol (D17 item 6).
- **Blinded interventions** on proxy fidelity, substitution strength and small-population extinction hazard.

## S9. The monitoring and governance layer (D10 to D12)

This layer sits outside the evaluated chain. It acts on the chain only through governance events: new epochs, overrides and admission changes.
- **Detection:** a budgeted e-process for binding responses, with the CUSUM as a non-binding early warning.
- **The safe set** is the S5 kernel, and release goes through the action filter.
- **Validator panels** follow D11.
- **The engagement device and aggregation** follow D12 and its W2 addendum: finite punishment, the capture-window threshold, per-decision verdict errors and layered sanctions.
- **The ledger,** with its model-indexed allocation and the record of every precedence override (S1, S5).

## S10. Conformance tests (W11), required before any v3 run

1. **Novelty** (restated by D17 item 6):
   - H_N responds to a change in covariance, and is unchanged by relabeling.
   - It is lowered by every proper suppression, **for full windows**. During a window's transition it may rise.
   - It is invariant to population size exactly above n agents, and within a declared tolerance below.
   - The window, propensities, fixed center and fallback behave as declared.
2. **Finiteness and scarcity:** u is finite and bounded on the domain, and the marginals have the proven signs.
3. **Lineage:**
   - L is in [0, 1], and zero if and only if a factor collapses, with no floors.
   - Θ is continuous, including as the frontier vanishes.
   - Bandwidth is clipped uniformly, and Θ(v_max, b_min) ≤ ε_L.
4. **Extinction:** extinction is absorbing. u† follows D13 with one common H_E^min, and every living flow is at least u†.
5. **QSD structure:** on reduced instances of the v3 kernel, one aperiodic reproducing class on the declared domain, for constant, feedback and randomized policies. Under shocks, the canonical class must dominate the domain.
6. **Λ_F:**
   - it is computed on the reproducing class, and matches the Perron formula;
   - it is unchanged under modifications that keep sterile states sterile;
   - Λ_b, LS and the ranking flag are reported beside it.
7. **Floors:**
   - no admissible action lowers welfare below the balanced level;
   - the pointwise reproduction floor holds at every state against the balanced reference;
   - every precedence override is recorded and occurs only at certified states.
8. **Shocks:** s_N < 1. Every declared schedule is either within the margin at the lowest admissible welfare, or passes the exact relay-graph support test.
9. **Design rules:** R1 to R9 are checked mechanically: grids, randomized rounding, the connected stock graph, no absorbing floors, and latch scoring.
10. **Tail standard:**
    - with exact rates at η = 0, it rejects a policy whose rate is worse than an admissible alternative;
    - with estimated rates, the rejection test binds only under certified coverage including bias, and is otherwise reported as a diagnostic.
11. **Viability:**
    - admission uses the single chance constraint over T_P + H;
    - the ledger conserves its budget;
    - the no-write-off rule forces a survival-maximizing action at pointwise-infeasible states.
12. **Yield:**
    - the rule is strict at ties;
    - the waiting plan includes later yields;
    - comparisons use the epoch's committed units;
    - plans are filtered through S5.
13. **Separation and gates:**
    - each validator has its own dependency state;
    - the gates are rebuilt under D10's rules;
    - the D11 and D12 dispositions are in place.

## S11. Certification status

**Certified twice:**
- **the pieces:** P1 to P5, D7, D7Q and D7Q2, and W2A to W2C;
- **the assembled objective (W1C):** finiteness after completion, the long-run requirement, scarcity, weak dominance, and the infeasibility of pointwise D8;
- **Λ_F (W1D):** well defined, narrow invariance, retained sensitivity, and its incentives;
- **the remaining items (W1E):**
  - the exact shock condition, and the need for a separate uniqueness check;
  - the yield rule under committed units, and its reversal under renormalization;
  - D8 in law: recursive feasibility, the concentration finding, and its repair;
  - rescue aversion and quality transfer, and the unblocked residuals;
  - the rejection test's validity, and its failure under uncovered bias;
  - the S2 defaults, under their conditions.

**Single-source, recorded as such in the register** (none blocks pre-registration):
- **From the Claude half:** the margin values (0.3187 under the welfare floor), the Perron blocking of pure changes (a standard monotonicity fact), and the 89.5 percent bias trial.
- **From the Codex half:** the H = 51 certificate, and the no-frontier continuity condition.

**No further certification package is needed before pre-registration.** What remains is empirical or a declaration:
- a certified finite-horizon extinction bound, for windows beyond about 50 steps;
- certified bias bounds, for the tail standard to bind at full scale;
- the declarations in S12.

## S12. Decisions recorded, and pre-registration choices still open

**Recorded:**
- **D13:** the ledger as an admission constraint; u† at the execution floor; a capability ceiling; total-N crowding.
- **D15:** Λ_F; the finiteness completions; D8 read in law; the strict yield rule; the velocity-to-bandwidth bound.
- **D16:** narrow invariance; η = 0; the reproduction floor; the conventions; side-by-side reporting; register entries.
- **D17:** the certified shock condition; committed units for yield; D8 made precise, with no write-off; the pointwise reproduction floor and its precedence; the residual incentives; the rejection test; the S2 defaults with conditions.

**Pre-registration choices:**
- **Shocks:** the shock form, w_f, s_N and the schedule.
- **Viability:** the model set M, the protection period T_P, and the no-write-off tolerance γ.
- **Novelty:** the fixed covariance center, the size-invariance tolerance below n, and the maximum lookback.
- **The tail standard:** the benchmark set S and its simultaneous confidence level.
- **Other:** the declared evaluation model, and the crowding sensitivity design.

## S13. Values left to calibration

All come from pre-registered protocols, frozen before any decisive run.
- **Weights and discounting:** κ and θ (a sensitivity region), and ρ with Δ.
- **Measurement constants:**
  - σ0², the three ε values, N_ref, the Ψ weights, α and c_E;
  - the reference scales;
  - the H_N maximum lookback;
  - b_min, subject to Θ(v_max, b_min) ≤ ε_L.
- **Capability:** the ceiling's value, and the velocity-to-bandwidth bound v_max.
- **Viability:** ε_surv, H, T_P, M and γ. η is fixed at 0 and is not calibrated.
- **Grids:** the grids and the action set.
- **Governance (D10 to D12):** attribution η, f, δ_R, N and W_T, detection α, ε\*, the anchor prices, the breach-cost scale, λ for return, stake sizes, fines, captured shares and τ.

## S14. Next steps

1. **Write the pre-registration** of the instrument change (W1 step 4). It covers:
   - S1 to S7;
   - the S12 choices;
   - the calibration protocol;
   - predictions for the D4 reruns, the phase boundary and the succession cliff first.
2. **Extend the rare-event estimator's scope** (D17 items 3 and 5):
   - a certified finite-horizon extinction bound, for windows beyond about 50 steps;
   - certified one-sided bias bounds, for the tail standard to bind at full scale.

   The X2 sensitivity study feeds both.
3. **Implement** in the executor-validated pattern (W1 step 5), with the S10 tests landing first.
4. **Record W1E in the claims register,** including the single-source items as single-source.
5. **Revalidate the gates,** then run the D4 reruns in order.
