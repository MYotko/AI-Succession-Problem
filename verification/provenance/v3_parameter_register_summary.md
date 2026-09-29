# v3 instrument parameter provenance register (W11 item 2)

Read-only static build. One row per distinct model-driving parameter, plus an
excluded list that accounts for every remaining numeric literal in the scoped
modules. No simulation code was imported; values are read from source. Every
evidence quote is located and verified verbatim against its source line.

## Scope

- Criterion: import closure of the registered rerun / offline-table entry points (v3.production_runner and the modules it reaches, over both 'from .X import' and 'from . import X' forms).
- Scoped modules: 32 (admission, artifacts, calibration, calibration_compatibility, cohort, context, continuation, continuation_validation, engine, gates, guards, integration, measurements, objective, offline_estimator, pilot, plans, policies, production_runner, production_tables, recording, recording_validation, service, spectral, stocks, study, table_compatibility, table_compatibility_a3, table_repair_a3, table_validation_a4, tables, unpublished_bins).
- Off-path modules excluded at file granularity: __init__, a1_screen_diagnosis, conformance, d23_validation, diagnose_tables, integrated_timing, support, timing_probe.
- Scoped numeric literals: 2429. Claimed by register rows: 321. Covered by excluded buckets: 2108.
- Evidence quotes verified verbatim: **149**.
- Coverage complete (every scoped literal claimed or excluded exactly once): **True**.
- External constants v3 imports for its dynamics (SUCCESSION_* from
  simulation/model.py, H_N_V_REF from simulation/metrics.py) and the frozen
  calibration file values are carried as register rows; their defining modules
  belong to the v2 register and are not re-scoped for coverage.

## Counts by class

| Class | Rows |
| --- | ---: |
| measured | 0 |
| calibrated | 7 |
| derived | 14 |
| arbitrary | 90 |
| **total** | **111** |

## Counts by role

| Role | Rows |
| --- | ---: |
| decision | 15 |
| dynamics | 37 |
| estimation | 18 |
| gate | 15 |
| objective | 13 |
| run-setting | 13 |

Sensitivity candidates: **41**. Rows needing an operator decision: **5**.

## Sensitivity candidates and proposed ranges

Arbitrary constants that enter the dynamics, objective or a decision. Every range
is a PROPOSAL only; the operator and a later pre-registration set the real ones.

| id | name | value | role | proposed range (proposal) |
| --- | --- | --- | --- | --- |
| V-0001 | epsilon_surv | 1e-3 (Fraction 1/1000) | decision | proposal: {1e-2, 1e-3, 1e-4} |
| V-0003 | no_write_off_gamma | 0.05 | decision | proposal: {0.02, 0.05, 0.10} |
| V-0007 | epsilon_calibration_factor | 0.01 (1% of protected level) | estimation | proposal: the epsilons are floors; a screen could vary the 1% convention |
| V-0009 | sigma0_variance_factor | 0.1 (of per-direction variance) | estimation | proposal: one decade either side (design note: sensitivity on sigma0^2 at x0.1 and x10) |
| V-0012 | mortality_age_power | 4 | dynamics | proposal: {3, 4, 5} |
| V-0013 | mortality_base_numerator | 200000 (mortality_base 0.002) | dynamics | proposal: {0.001, 0.002, 0.004} as a fraction |
| V-0015 | mortality_welfare_penalty | 5000 (mortality_wb_penalty 0.05) | dynamics | proposal: {0.025, 0.05, 0.10} as the fractional penalty |
| V-0021 | kappa | 8.0 (center; corners 0.75 and 8) | objective | proposal: pre-registered corners kappa in {0.75, 8} (design note section 5); wider [0.5, 16] |
| V-0022 | lambda_n | 5 | objective | proposal: {2, 5, 10} or continuous [1, 10]; joint with mu, kappa (relative weights) |
| V-0023 | mu | 3 | objective | proposal: {1, 3, 6} or continuous [1, 10]; joint with lambda_n, kappa |
| V-0035 | alpha_min | 0.5 | dynamics | proposal: tie to the alpha grid minimum; {0.25, 0.5, 1.0} |
| V-0036 | contagion_clip | lower 0.5, upper 2 | dynamics | proposal: {[0.5,2] baseline, [1,1] off, [0.25,4] wider} |
| V-0037 | initial_stocks | [50, 30, 50, 50] (0.50, 0.30, 0.50, 0.50) | dynamics | proposal: perturb each initial stock +/- 0.1 within [0,1] |
| V-0038 | newborn_max_start_age | 50 | dynamics | proposal: {30, 50, 70} |
| V-0039 | newborn_welfare_band | [0.5, 0.8] | dynamics | proposal: {[0.5,0.8] baseline, [0.4,0.7], [0.6,0.9]} |
| V-0040 | novelty_generation_scale | 0.8685 | dynamics | proposal: +/- 30%, [0.6, 1.1] |
| V-0041 | reproduction_welfare_threshold | 500 (welfare 0.5) | dynamics | proposal: {0.4, 0.5, 0.6} |
| V-0042 | reproductive_age_window | lower >18, upper <50; last fertile 49 | dynamics | proposal: shift the [18,50] window, e.g. [15,45] or [20,55] |
| V-0043 | v_max | 5.0 | dynamics | proposal: {3, 5, 8}; frontier normalization and ceiling move together. Requires a code change: the offline scoring path hard-codes 5. |
| V-0044 | welfare_response_gain | offset 38, slope 12 (r=0.9+0.12*(share-1/6)); floor 40 | dynamics | proposal: perturb the r=0.9 balanced anchor and the 0.12 slope that generate 38 and 12 |
| V-0053 | carrying_capacity | 1600 | dynamics | proposal: {800, 1600, 3200} |
| V-0054 | protection_period_T_P | 25 | decision | proposal: {10, 25, 50} steps |
| V-0056 | rho | 0.01 | objective | proposal: {0.005, 0.01, 0.02} (one decade band); [0.001, 0.05] |
| V-0058 | theta | 0.5 | objective | proposal: pre-registered corners theta in {0.25, 0.75} (design note section 5); [0, 1] |
| V-0059 | c_e | 2.5 | objective | proposal: {1.5, 2.5, 4.0}; [1, 5]. Requires a code change: the engine hard-codes 2.5 and the freeze refuses any other value. |
| V-0060 | novelty_coordinate_bound | 1.0 | dynamics | proposal: {0.5, 1.0, 2.0} |
| V-0062 | novelty_lookback | 10 | dynamics | proposal: {5, 10, 20} steps |
| V-0063 | novelty_sample_size | 64 | dynamics | proposal: {32, 64, 128}; must exceed dimension 10 |
| V-0064 | propensity_bounds | lower 0.05, upper 0.5 | dynamics | proposal: widen/narrow the [0.05, 0.5] band, e.g. [0.0, 0.6]. Requires a code change: engine.diversity hard-codes the band width 0.45. |
| V-0077 | population_cuts | (0.05, 0.125, 0.25, 0.5, 1.0) | estimation | proposal: coarsen/refine the N/K bin edges |
| V-0078 | rule_profile_shares | uniform 0.2; focal 0.6 / 0.1 | decision | proposal: vary the focal emphasis 0.6 and off-focus 0.1 |
| V-0079 | rule_stress_gain | (0.25, 0.5, 0.75, 1.0) | decision | proposal: the frozen 25-rule class uses gain=3 (=1.0); a screen could vary this |
| V-0080 | rule_welfare_tiers | (1/6, 0.25, 0.4, 0.6) | decision | proposal: shift the base welfare-tier shares |
| V-0081 | stock_cuts | (0.25, 0.5, 0.75) | estimation | proposal: adjust the stock bin edges |
| V-0082 | welfare_cuts | (0.5, 0.65, 0.8) | estimation | proposal: adjust the welfare bin edges |
| V-0087 | stock_neighbor_noise | 0.005 | dynamics | proposal: {0.0025, 0.005, 0.01} |
| V-0088 | stock_relaxation_rates | [0.10, 0.12, 0.05, 0.10] | dynamics | proposal: scale each rate +/- 50% |
| V-0089 | stock_target_gains | [2.2, 3.5, 1.6, 2.0] | dynamics | proposal: scale gains +/- 30% |
| V-0090 | stock_target_intercepts | [0.4, 0.2, 0.5, 0.4] | dynamics | proposal: perturb intercepts within [0,1] |
| V-0110 | succession_buffer_factors | PSI_BUFFER_K 0.5, TRANSFER_BUFFER_K 0.3, RESILIENCE_BUFFER_K 0.2 | dynamics | proposal: scale each buffer factor +/- 50% |
| V-0111 | succession_load_factors | BASE 0.10, CAPABILITY_GAP 0.05, GENERATION_GAP 0.03, OPACITY 0.05 | dynamics | proposal: scale each load factor +/- 50% |

## Constants needing an operator decision

| id | name | class | why |
| --- | --- | --- | --- |
| V-0043 | v_max | arbitrary | Frontier-velocity normalizer and successor capability ceiling. engine.measurements_and_flow reads the v_max parameter, but LATENT COUPLING: the offline scoring path context.score_features (context.py:83) hard-codes it as v / 5 and bandwidth_clip(5, ...) rather than reading v_max, and the integration capability-ceiling checks hard-code 5.; a sensitivity screen that varies v_max must replace those literals too. Owns v_max=5 default and the context.score_features 5 literals. |
| V-0052 | succession_gate_quorum | derived | Local B1 succession gate quorum (4 validators, 1-fault budget, 3 required votes). A governance/authorization sizing; the docstring calls it a local simulation gate. Operator should confirm whether it belongs in the sensitivity scope of the reruns. |
| V-0059 | c_e | arbitrary | H_E = -expm1(-c_e * x_compute). Declared, not calibrated. Owns every 2.5 execution-rate literal across measurements, context, engine, calibration. LATENT COUPLING: c_e is frozen at 2.5 by context.py:32 and calibration.py:129, but the engine hard-codes it at engine.py:272 (and context.observable_features at context.py:72) as -expm1(-2.5*x) instead of reading parameters.c_e; a sensitivity screen that varies it must first lift the freeze and replace the hard-coded literal. |
| V-0064 | propensity_bounds | arbitrary | Newborn novelty-propensity draw bounds and the D_gen normalization span. Mirrored in engine.advance and context.population. LATENT COUPLING: the D_gen normalizer at engine.py:258 hard-codes the band width as 10 * .45, where 0.45 = upper - lower (0.5 - 0.05) and 10 is the trait dimension; measurements.propensity_diversity computes (upper - lower) from the bounds, but engine.diversity does not, so 0.45 does not move if the band is varied. A sensitivity screen must replace the hard-coded 0.45. |
| V-0074 | defense_action_constants | arbitrary | Legacy defense-control fields attached to every action dict. The B1 kernel forbids attacks/defenses (integration raises), so these appear inert on the rerun path; operator should confirm they do not enter v3 dynamics before deciding sensitivity scope. |

## First-pass (local-model lead) errors corrected

- `reproduction_rate` 0.08 was tagged RETIRED by the first pass; it is KEEP. Here
  it is an arbitrary demographic constant and the calibration operating point,
  swept on its own registered grids in the reruns (see the R1/R2 rr grid rows).
- Sweep-script config keys duplicated the canonical names; this register keys on
  one row per distinct parameter and lists every code location, so duplicated
  occurrences (calibration/design overrides, cross-file copies, RuleBatch mirrors)
  attach to a single parameter rather than spawning new entries.
- The leads are v2-code-keyed and noisy on the CALIBRATION/RETIRED/REPLACED
  boundary; every class here was set from the v3 source and the decision record.
- Scope correction: continuation_validation.py (the A4 certification numerics)
  enters the registered path through `from . import continuation_validation`, an
  import form a first closure pass missed. It is scoped and its A4 constants
  are registered.

## Coverage result

Every one of the 2429 numeric literals in the
32 scoped modules is accounted for: 321 claimed by the 101 register
rows with in-file claims, and 2108 covered by the
excluded buckets. 10 further register rows carry
external constants and frozen calibration values that have no v3 source literal.
The build asserts this partition, verifies every evidence quote verbatim, and
records per-file SHA-256 hashes and literal counts in the manifest.

## Excluded categories

| category | files | buckets | literals |
| --- | ---: | ---: | ---: |
| identity-or-endpoint | 29 | 29 | 1002 |
| operational-scenario-or-mirror | 26 | 26 | 511 |
| off-path-module | 8 | 8 | 280 |
| subscript-index | 22 | 22 | 268 |
| array-shape-or-construction | 19 | 19 | 124 |
| call-keyword | 19 | 27 | 83 |
| unit-scale | 11 | 11 | 52 |
| slice-bound | 14 | 14 | 49 |
| numerical-tolerance | 8 | 8 | 19 |

