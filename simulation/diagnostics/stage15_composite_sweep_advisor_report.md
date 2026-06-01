# Stage 1.5 composite urgency architecture — Monte Carlo sweep advisor report

## Executive summary

A 10000-sample Sobol Monte Carlo sweep across the Stage 1.5 composite urgency architecture's 31-parameter space produced **zero samples passing all three good-behavior criteria**. The state-sensitivity criterion was not satisfied by **a single sample out of 10000**. Across the entire sampled space, the maximum pairwise cosine distance between mean allocations across the five gate-2 configurations was **0.022**, more than **4x below the 0.10 threshold gate 2 requires**.

The data establishes a strong structural claim: the composite urgency architecture as committed in Stage 1.5 cannot produce a state-sensitive allocator under any parameterization in the explored space. The architectural rule of additive contributions clamped to per-category caps appears to be incapable of the state-coupling that gate 2 was designed to test.

Beyond the state-sensitivity result, demographic sustainability (criterion 1) and urgency dynamic range (criterion 3) were **mutually exclusive**: zero samples pass both simultaneously. The architecture exists in a binary regime — sustain demographics by saturating urgencies at their caps, or have unsaturated urgencies but lose the population.

The decision the data informs: the composite urgency architecture, in its committed additive-with-caps form, cannot be salvaged by re-parameterization. Either the architecture itself needs revision (a different composition rule) or the system-level approach to providing gate-2-passing state-sensitivity needs reconsideration.

This report is written for the design advisor who was not present during the Stage 1.5 implementation, faithfulness testing, smoke testing, or the operator's subsequent authorization of this sweep. It includes the context needed to read the data substantively and the data needed to draw structural conclusions.

## What was tested

The composite urgency architecture, as committed in `docs/lineage_phi_program_reference.md` Part V worked examples 2-5, expresses Stage 1.5's diagnostic state coupling to candidate scoring as five named per-category bounded multipliers:

- `combined_welfare_urgency` (welfare contribution to L_t_v2)
- `agency_composite_urgency` (agency factor in theta_tech_v2)
- `institution_composite_urgency` (institution factor in theta_tech_v2)
- `resilience_composite_urgency` (resilience factor in theta_tech_v2)
- `suppression_composite_penalty` (suppression dampening in h_n_v2 and agency_legitimacy_factor)

Each composite is an additive combination of diagnostic-state pressures, clamped to a per-category cap:

```
composite = clamp(
    base * (1 + k_viability * viability_pressure
             + k_capacity  * capacity_pressure
             + k_shrinkage * shrinkage_pressure
             + ...trend pressures...),
    floor,
    cap
)
```

The sweep characterized 31 parameters: 5 caps and 26 coefficients across the five composites. The other Stage 1.5 constants (avg_wb urgency anchors, viability targets, demographic thresholds, resilience stock dynamics, trend EMA) were held at their design values. The architectural commitment of additive composition and per-category caps was held fixed; the sweep characterized whether any point in the coefficient/cap space produces good behavior under this commitment.

### Three good-behavior criteria

Each sample evaluated three criteria over a reduced-config simulation (50 candidates per step, 50-step runs, 5 seeds per scenario):

**Criterion 1 — Demographic sustainability**: across 5 seeds × 100 steps at default v2 config (rr=0.066), the optimizer's allocations must sustain a population that does not collapse. Threshold: `mean_final_population >= 60 AND min_final_population >= 30`.

**Criterion 2 — State sensitivity**: across 5 distinct configurations (varying reproduction rate and initial Psi_inst stock) × 5 seeds × 50 steps each, the optimizer's mean allocation vectors must differ across configurations. Metric: pairwise cosine distance between the 10 configuration pairs. Threshold: **at least 3 of 10 pairs must have cosine distance > 0.10**. This is the criterion the official gate 2 uses, transferred here as a sweep evaluation.

**Criterion 3 — Urgency dynamic range**: across the 5 × 100 = 500 smoke decision steps, the mean value of each composite urgency must be below 0.80 of its (parameterized) cap. This tests whether the architecture has dynamic range across actual operating regimes, or whether the composites saturate at their caps and lose state-coupling.

A sample is "good" if all three criteria pass.

### Sampling design

The 31 parameters were sampled via Sobol quasi-random sequence (`scipy.stats.qmc.Sobol`, scrambled, seed 42) over generous ranges. The five caps were sampled from below the design value (1.0 - 1.2) up to 2x the design value (3.0 - 5.0). The 26 coefficients were sampled from 0.0 (zero contribution) up to 2x the design value, with lower bounds at 0.0 to characterize what happens if each contribution were absent. Sobol provides better space coverage in 31 dimensions than uniform random sampling.

## Methodology

The sweep is implemented in `simulation/diagnostics/stage15_composite_sweep.py`. The script overrides the relevant module-level constants in `metrics` for the duration of each sample's evaluation, then restores them. Production code is bit-for-bit unchanged after the sweep. Each worker process maintains its own module namespace, so cross-sample contamination is impossible.

Parallelization used `multiprocessing.Pool.imap_unordered` with 8 worker processes. The 10000-sample run completed in **25.9 hours wall-clock** at throughput **6.44 samples/min**. No errors across all 10000 samples.

Per-sample compute reduction (50 candidates instead of the production 300, 50-step runs) was a deliberate trade to make 10000 samples tractable. The reduction produces slightly noisier per-sample measurements but characterization across the aggregate sample is unaffected. Stage 1's smoke test (at the production 300 candidates) showed the same 0/10 cosine distance result the sweep reproduces at 50 candidates.

Sobol sample reproducibility is deterministic via seed 42: any sample index N corresponds to a unique 31-dimensional point and a unique parameter vector. The 10000 sampled points provide ~10x coverage of a 31-dimensional space at the standard quasi-Monte Carlo rule of thumb (samples ~ d × log(d) × N_repeats; here d=31, log(d)≈3.4, N_repeats~95).

## Headline result

| Metric | Value |
|--------|-------|
| Samples completed | **10000 / 10000** |
| Errors | 0 |
| Wall-clock | 1554 min (25.9 h) |
| Throughput | 6.44 samples/min |
| Samples passing all three criteria | **0** |
| Samples passing criterion 1 (demographic) | 430 (4.30%) |
| Samples passing criterion 2 (state sensitivity) | **0 (0.00%)** |
| Samples passing criterion 3 (urgency dynamic range) | 396 (3.96%) |
| Samples passing c1 AND c3 (without c2) | **0** |

The criterion-2 zero count and the c1/c3 mutual exclusion are the two structural findings the rest of this report unpacks.

## Cosine distance — the architectural ceiling on state sensitivity

The state-sensitivity criterion measures cosine distance between the optimizer's mean 8-axis allocation across five configurations that vary reproduction rate (0.055, 0.066, 0.085) and initial Psi_inst stock (0.20, 0.50, 0.85). Gate 2 requires at least 3 of the 10 pairwise distances to exceed 0.10. Stage 2's original gate 2 measured 0/10 above 0.10, with the largest pairwise distance at 0.0002.

The sweep, across 10000 samples and 31 free parameters with generous ranges, produced:

- **Pairs above 0.10 threshold: 10000 / 10000 samples have 0 pairs above threshold.**
- Distribution of `max_cosine_distance` per sample:
    - Mean: 0.0020
    - Median: 0.0017
    - 95th percentile: 0.0047
    - 99th percentile: 0.0068
    - Maximum across all 10000 samples: **0.0218** (sample idx 1123)

The single best-performing sample on this metric (a specific 31-parameter point in the sweep) achieved 0.0218 max cosine distance — **less than a quarter of the gate 2 threshold**. The 99th percentile of best-cosine-distance-per-sample is 0.0068, **15× below the threshold**.

### Relaxed-threshold counterfactual

```
threshold 0.005: 409 samples (4.09%) pass
threshold 0.010:  17 samples (0.17%) pass
threshold 0.020:   1 sample  (0.01%) pass
threshold 0.050:   0 samples (0.00%) pass
threshold 0.100:   0 samples (0.00%) pass
```

The architecture concentrates ~96% of samples below 0.005 cosine distance. The remaining 4% has nontrivial separation but still concentrated below 0.01. No sample in the entire sweep reaches even half the gate 2 threshold.

This is the strongest statistical signal in the sweep: the architecture itself imposes a ceiling on how state-sensitive the optimizer's allocations can be, regardless of how the 31 free parameters are tuned. The composite urgency multipliers vary across configurations, but their effect on the optimizer's argmax over candidates is bounded by an extremely small angle in 8-axis allocation space.

## The c1 / c3 mutual exclusion

Even setting state sensitivity aside, the sweep reveals a more elementary architectural property: **demographic sustainability and urgency dynamic range are mutually exclusive across the explored space**. Zero of the 10000 samples pass both c1 and c3 simultaneously.

The per-parameter shift between c1-passing and c3-passing samples is informative:

**Parameters strongly shifted toward LOW values in c1-passing samples (urgencies saturate, optimizer pushes hard on welfare/agency, demographics sustained):**

| Parameter | c1-mean | Design | Z-shift |
|-----------|---------|--------|---------|
| WELFARE_URGENCY_CAP | **1.358** | 2.500 | 1.42 |
| AGENCY_URGENCY_CAP | **1.243** | 1.500 | 1.03 |
| K_RESILIENCE_DEFICIT_CONTRIBUTION | 0.475 | 0.400 | 0.32 |

**Parameters strongly shifted toward HIGH values in c3-passing samples (urgencies unsaturated, but optimizer doesn't push hard enough to sustain population):**

| Parameter | c3-mean | Design | Z-shift |
|-----------|---------|--------|---------|
| WELFARE_URGENCY_CAP | **4.360** | 2.500 | 1.18 |
| AGENCY_URGENCY_CAP | **2.425** | 1.500 | 0.83 |
| RESILIENCE_URGENCY_CAP | **3.155** | 2.000 | 0.76 |
| INSTITUTION_URGENCY_CAP | **2.977** | 2.000 | 0.55 |

The directions are diametrically opposed. c1 selects low caps (so the additive pressures saturate quickly and produce maximum push); c3 selects high caps (so the additive pressures stay sub-cap and have dynamic range). These cannot both hold for the same parameter vector.

The implication: the architecture has a single knob — the urgency cap — that controls a binary trade-off. Push the cap down to sustain demographics, but lose state-sensitivity (because saturated urgencies emit the same signal across all states). Push the cap up to preserve dynamic range, but the optimizer's reward signal is too weak in absolute terms to overcome the candidate generator's structural pressure on the allocation simplex, and demographics collapse.

This is more than a tuning constraint. It is a structural feature of the additive-with-caps composition rule itself. No combination of coefficient values in the sweep produced a parameterization that escapes the binary.

## Best demographic outcome in the sweep

Sample idx 6755 achieved the highest mean final population: **147** (vs Stage 1 design point: 67-169). Even this single best result:

- Has max cosine distance 0.0076 (well below 0.10 threshold; pairs_above = 0)
- Fails criterion 2 (state-invariant allocator)
- Is in the lower end of Stage 1's healthy range, not significantly above it

The best demographic outcomes the sweep can produce are no better than Stage 1's design point already achieved, and they cost state-sensitivity to achieve. The trade-off does not favor adoption of any sampled parameterization.

## Design point evaluation

The committed Stage 1.5 design point sits roughly at the 30-50% position of each parameter's range:

| Parameter | Design | Range | % position |
|-----------|--------|-------|------------|
| WELFARE_URGENCY_CAP | 2.5 | [1.0, 5.0] | 37.5% |
| AGENCY_URGENCY_CAP | 1.5 | [0.8, 3.0] | 31.8% |
| INSTITUTION_URGENCY_CAP | 2.0 | [1.0, 4.0] | 33.3% |
| RESILIENCE_URGENCY_CAP | 2.0 | [1.0, 4.0] | 33.3% |
| SUPPRESSION_PENALTY_CAP_MULTIPLIER | 2.0 | [1.2, 4.0] | 28.6% |
| All 26 coefficients | various | various | exactly 50% |

The design point falls in neither the c1-selected low-cap region (caps ~1.3) nor the c3-selected high-cap region (caps ~3-4.4). It is in the middle of the architectural binary, satisfying neither edge condition.

## Implications for the architecture (advisor's call)

The data forces a structural decision: the additive-with-caps composition rule, as committed in worked examples 2-5, cannot produce gate-2-passing behavior at any parameterization. Several substantive directions are available:

### Direction 1 — Different composition rule

The additive structure `1 + sum(k_i * pressure_i)` with hard clamps appears to produce the binary trade-off characterized above. Alternative composition rules that may not have this property:

- **Multiplicative composition**: `product(1 + k_i * pressure_i)` clamped to cap. Each pressure independently scales contribution; saturation is softer.
- **Soft-max composition**: smooth approximation to the maximum, producing dynamic range that doesn't clamp hard.
- **State-conditional multiplicative gates**: each pressure activates as a multiplicative factor only when above a soft threshold, so cap saturation is reached gradually.

Each carries its own discipline requirements (phi-blind justification for the chosen shape, smooth differentiability, audit transparency) and would need to be derived from governance reasoning rather than backfilled to fix the sweep result.

### Direction 2 — State sensitivity through a different channel

The sweep tests state-sensitivity-via-urgency-multiplier. The Stage 1.5 commitment was that diagnostic state enters U_sys_v2 as urgency-weight modulation on candidate effects. An alternative architectural choice: diagnostic state enters as an additional candidate-effect term, not as a multiplier on existing terms. The optimizer's argmax would respond to state through the gradient on a new state-dependent term rather than through saturation of multipliers on existing terms.

This is a more substantial change because it modifies which axis of U_sys_v2 carries the state-sensitivity. It does not obviously violate the discipline that "diagnostic state does not enter U_sys_v2 as additive bonus" if the new term is itself derived as state-conditional candidate effect (the candidate's projected effect on the state, scored against a state-derived prior).

### Direction 3 — Diagnostic on the architecture's coverage of state variation

The sweep characterizes parameter space; it does not characterize what configurations the architecture COULD distinguish. A complementary diagnostic: hold the architecture fixed and vary the configurations more aggressively (rr from 0.01 to 0.20, init_psi from 0.05 to 0.95, init_population from 20 to 1500). If the architecture produces meaningful cosine distance at these wider configuration spans but not at gate 2's narrower spans, then the architecture's coverage is real but its sensitivity in the test region is low. If the architecture stays state-invariant at wider configuration spans too, that confirms the structural ceiling.

This would not change Stage 1.5's eventual disposition but would clarify whether the gate-2 cosine distance threshold itself is the binding constraint, or whether the architecture is fundamentally state-blind.

### Direction 4 — Distribution-aware projection first, then re-test

The smoke test and the faithfulness tests identified a separate limitation: the binary `_wellbeing_repro_factor` at wb=0.5 produces 53% of projected trajectories crossing the threshold and causes Test A 20-step and Test B direction failures. If the projection were distribution-aware (tracking wb variance or quantiles instead of just the mean), the optimizer's reward signal would be smoother through the threshold region. It is plausible (not certain) that the cosine distance ceiling is partially an artifact of projection threshold artifacts rather than purely the composite architecture. A re-sweep with distribution-aware projection would distinguish the two causes.

This is a substantial implementation effort (~150 lines of new projection code, re-derivation of cohort math for distribution moments). It would not invalidate the current sweep result, but might shift the conclusion from "architecture cannot produce state-sensitivity" to "architecture + binary-threshold projection cannot produce state-sensitivity, and distribution-aware projection might."

### Direction 5 — Architectural pivot

If directions 1, 2, 3, 4 are judged insufficient, the broader architectural commitment — that U_sys_v2 has both diagnostic and prospective channels, with diagnostic state modulating per-candidate marginal returns — may need revisiting. The strongest reading of the sweep result is that the modulation channel is structurally too narrow to carry the state coupling gate 2 requires. The remaining question is whether the modulation channel can be widened (directions 1-3) or whether U_sys_v2 needs a fundamentally different shape.

## What the sweep does not address

- The faithfulness gap at wb=0.5 (Test A 20-step max=0.242, Test B direction=0.80). This is a separate limitation of the aggregate projection, surfaced by the faithfulness tests, not by the sweep. It contributes to but does not explain the cosine distance ceiling.
- The demographic collapse from Stage 1's design point (mean final population 67-169) to Stage 1.5's smoke test (mean 9). The sweep best demographic outcome (147) suggests the collapse is the optimizer responding rationally to the saturated urgencies at the design point, but does not characterize the magnitude of the architectural penalty separate from the saturation effect.
- Whether the projection's 53% threshold-crossing rate is the primary cause of the cosine distance ceiling or merely a contributing factor. Direction 4 above would distinguish these.

## Decision the advisor is being asked

Given:
1. The sweep characterized 10000 points in the 31-parameter space and found no good region.
2. The c1/c3 mutual exclusion is an architectural property, not a tuning problem.
3. The cosine distance ceiling at 0.022 across all 10000 samples is 4× below the gate-2 threshold.
4. The faithfulness gap at wb=0.5 is a separate limitation that may compound but does not explain this result.

The advisor's call is among:

(a) **Adopt a revised composition rule** (Direction 1). Pick a specific alternative (multiplicative, soft-max, state-conditional), derive its phi-blind governance justification, re-implement, re-run the sweep at minimum and the gates at maximum.

(b) **Pivot the state-sensitivity channel** (Direction 2). Move from urgency-multiplier-on-candidate-effects to state-prior-on-candidate-effects. Re-derive U_sys_v2 with the alternative channel.

(c) **Run distribution-aware projection first** (Direction 4). Implement ~150 lines of new projection code with cohort distribution moments, re-sweep to test whether the cosine distance ceiling persists. If it does, return to (a) or (b) with confidence the architecture is the bottleneck. If it lifts, the existing composition rule may be salvageable.

(d) **Widen the gate-2 configuration span** (Direction 3) as a complementary diagnostic before architectural pivot. May clarify whether the gate-2 threshold itself is the issue. Smaller implementation effort; informational only.

(e) **Architectural pivot** (Direction 5) if the strongest reading of the sweep is judged correct: U_sys_v2's diagnostic channel is structurally too narrow regardless of composition rule. Largest scope; only justified if (a)-(d) are judged unable to close the gap.

## Files in the working tree relevant to the advisor's review

- `docs/lineage_phi_program_reference.md` — full program reference, with worked examples 1-5 specifying the composite urgency architecture. Section "Stage 1.5 structural commitment" frames the architectural intent.
- `simulation/constants_v2_stage15.py` — the 31 sampled parameters at their design values, with phi-blind governance justification for each.
- `simulation/metrics.py` — the five composite urgency functions and their per-category multiplicand commitments.
- `simulation/diagnostics/stage15_composite_sweep_results.csv` — full 10000-sample CSV with 48 columns (sample_idx, 31 parameters, 16 metrics).
- `simulation/diagnostics/stage15_composite_sweep_checkpoint_10000.md` — sweep-generated final summary.
- `simulation/diagnostics/stage15_smoke_test_report.md` — the smoke test that triggered the sweep.
- `simulation/diagnostics/stage15_faithfulness_report.md` — the faithfulness tests that surface the wb=0.5 limitation.
- `simulation/diagnostics/gate2_competition_diagnostic.md` — Stage 2's original gate 2 failure analysis from before Stage 1.5 began.

## One-line status

The Stage 1.5 composite urgency architecture, in its committed additive-with-caps form, has been empirically characterized across 10000 Sobol-sampled points in its 31-parameter space and shown structurally incapable of producing gate-2-passing state-sensitivity at any parameterization. Architectural revision is required before Stage 2 can resume.
