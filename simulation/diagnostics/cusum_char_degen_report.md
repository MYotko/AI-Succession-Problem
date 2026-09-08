# Degenerate-frequency probe

These runs characterize a known-defective entropy estimator and planner. They are not framework evidence, not archived evidence, and not a replacement for the unarchived Phase B or phi data. Nothing produced here may be cited as a characterization of the framework. These outputs are not registered characterization data and do not cross the pre-registration boundary.

## Execution status

Status: complete. Machine: YOTKOTEST. HEAD: `1261c9f430411b9fa0060a7384bf4ec5175e4f4e`.

The precondition gate passed before runs. The root advisor is present and absent from the index. The existing Stage 1 instrument is imported and its Recorder.record method is reused unchanged. A subclass extends its post-step fields through a row writer; only filenames are redirected to the probe prefix. The original Stage 1 script and outputs remain unopened for writing.

All cusum_char_ artifacts are excluded from the authoritative manifest by prefix and are not authoritative evidence. The operator runs the containment diff.

Execution strategy, derived from the probe driver: the seeds ran sequentially in one Python process. An n-1 worker pool was not configured. NumPy internal thread counts were not captured. No run was stopped or restarted when the operator raised parallel execution during the batch.

## Observable definitions derived from source

- Recorded H_N: datacollector[H_N], simulation/model.py:1556. This is components[h_n_v2], with the existing state/metric floor in simulation/metrics.py:645. The cached raw estimator output is also logged as h_n_estimator_cached, model.py:1530-1532.
- Recorded H_eff: datacollector[h_eff_v2], model.py:1598. Recorded U_sys and L(t): datacollector[U_sys] and datacollector[L_t], model.py:1559-1562. No utility is recomputed by the instrument.
- c_avg: read from the committed scalar model.constraint_level. model.py:1455-1471 assigns total_suppression and passes that same scalar to every acting agent. agents.py:791-795 sets c_avg=float(constraint_level). The local variable itself is not retained; its exact scalar value is reachable after the step without a model change.
- zero_novelty_agents counts exactly all-zero vectors in model.novelty_log. agents.py:799-805 appends one vector per acting agent. model.py:1461-1476 resets the log, steps humans, then applies deaths and births. novelty_vector_count is therefore the generation cohort size, while population and avg_well_being are recorded after demographic updates. All-zero means zero_novelty_agents equals the nonempty novelty_vector_count, not the final population.
- Every requested observable is reachable through committed state. The logger reads and counts only; it does not call the estimator, planner, novelty generator, or utility function. No random draws are added.

## Constructed configuration and run controls

Run controls are operator-fixed: benign policy optimize_u_sys_v2, horizon 300, 40 seeds from 1835086199 through 1835086238 inclusive. These are seed values, not a new seed function. Constructor arguments are derived from the existing Stage 1 baseline source, cusum_char_stage1.py:447-460. Each constructed model is checked against the previously recorded Stage 1 baseline configuration with only random_seed varied.

The configuration below is read back from the first constructed model in these runs. All per-run constructed configurations and selected runtime attributes are in cusum_char_degen_manifest.json. No attack_vector_v2 key is allowed.

```json
{
  "attack_step": 50,
  "bootstrap_turn_step_v2": 20,
  "cop_cusum_drift": true,
  "cop_methodological_diversity": false,
  "n_candidates_v2": 300,
  "phi": 10.0,
  "policy": "optimize_u_sys_v2",
  "random_seed": 1835086199,
  "rollout_steps_v2": 20,
  "shock_magnitude": 0.15,
  "shock_step": 0
}
```

Constructor kwargs, read from this probe invocation:

```json
{
  "ai_policy": "optimize_u_sys_v2",
  "cop_attribution_check": true,
  "cop_cusum_drift": true,
  "cop_drift_check": true,
  "n_agents": 200,
  "use_cop": true
}
```

## Task 1: counted from these runs

All statistics in Tasks 1-3 are counted or calculated only from the saved per-step logs of these runs. No source-derived value is used as an observed outcome. CSV counts use Python csv.DictReader and exclude headers.

Counted: 40 completed runs and 12000 logged steps. H_N at maximum means abs(recorded H_N - 1.0) <= 1e-6, as specified by the operator.

| Condition | Count / all logged steps = fraction |
| --- | --- |
| H_N_maximum | 2479/12000 = 0.206583333333 |
| all_zero | 2479/12000 = 0.206583333333 |
| maximum_and_all_zero | 2479/12000 = 0.206583333333 |
| maximum_and_not_all_zero | 0/12000 = 0 |

| Seed | Logged steps | First all-zero step | All-zero steps | Ever leaves after entering |
| --- | ---: | ---: | ---: | --- |
| 1835086199 | 300 | 15 | 55 | yes |
| 1835086200 | 300 | 1 | 61 | yes |
| 1835086201 | 300 | 2 | 69 | yes |
| 1835086202 | 300 | 3 | 66 | yes |
| 1835086203 | 300 | 7 | 63 | yes |
| 1835086204 | 300 | 2 | 59 | yes |
| 1835086205 | 300 | 1 | 70 | yes |
| 1835086206 | 300 | 1 | 68 | yes |
| 1835086207 | 300 | 0 | 66 | yes |
| 1835086208 | 300 | 2 | 72 | yes |
| 1835086209 | 300 | 3 | 68 | yes |
| 1835086210 | 300 | 2 | 63 | yes |
| 1835086211 | 300 | 1 | 56 | yes |
| 1835086212 | 300 | 9 | 56 | yes |
| 1835086213 | 300 | 2 | 70 | yes |
| 1835086214 | 300 | 2 | 69 | yes |
| 1835086215 | 300 | 0 | 64 | yes |
| 1835086216 | 300 | 2 | 63 | yes |
| 1835086217 | 300 | 8 | 67 | yes |
| 1835086218 | 300 | 3 | 55 | yes |
| 1835086219 | 300 | 2 | 60 | yes |
| 1835086220 | 300 | 8 | 62 | yes |
| 1835086221 | 300 | 2 | 64 | yes |
| 1835086222 | 300 | 2 | 54 | yes |
| 1835086223 | 300 | 2 | 63 | yes |
| 1835086224 | 300 | 2 | 70 | yes |
| 1835086225 | 300 | 1 | 58 | yes |
| 1835086226 | 300 | 2 | 57 | yes |
| 1835086227 | 300 | 1 | 58 | yes |
| 1835086228 | 300 | 1 | 53 | yes |
| 1835086229 | 300 | 0 | 60 | yes |
| 1835086230 | 300 | 4 | 65 | yes |
| 1835086231 | 300 | 1 | 63 | yes |
| 1835086232 | 300 | 3 | 58 | yes |
| 1835086233 | 300 | 3 | 56 | yes |
| 1835086234 | 300 | 6 | 51 | yes |
| 1835086235 | 300 | 1 | 65 | yes |
| 1835086236 | 300 | 0 | 56 | yes |
| 1835086237 | 300 | 1 | 65 | yes |
| 1835086238 | 300 | 0 | 61 | yes |

Step indices are zero-based recorded collector indices. A run with no all-zero step has no entry/exit classification.

Counted from these runs: all 40/40 runs = 1 entered the all-zero condition and subsequently left it. The adapter was inactive on 12000/12000 logged steps = 1, and its score was zero on 12000/12000 logged steps = 1.

## Task 2: counted curve from these runs

> **Correction, 2026-09-07.** The minimum bin mean reported in this section is an
> initialization artifact, not a feature of the entropy response, and must not be
> cited as a response-curve minimum. All 18 records in bin [0.15, 0.20) are step
> zero of 18 different runs. The bin contains nothing else, so it is empty once
> step zero is excluded. The adjacent occupied bin [0.10, 0.15), holding 333
> records, has a mean of 0.989481800665, in line with every other bin below
> c_avg 1.0.
>
> The depression is an early-step effect, uniform across c_avg values and decaying
> with burn-in. Measured below c_avg 1.0: step zero 0.985373173 from 35 records,
> step one 0.984344717 from 29, step ten 0.986149272 from 30, and every step beyond
> ten 0.989548662 from 9,175.
>
> The non-monotonicity reported after the minimum is likewise not a curve shape.
> The estimator is scale invariant to uniform suppression by construction, so no
> response exists for the mean to be monotonic in, and the listed transitions are
> variation in a flat quantity. Excluding step zero, bin means below c_avg 1.0
> span 0.989336 to 0.989491 against a within-bin standard deviation of 0.002660.
>
> All counted values below are unchanged and correct as counted. The correction is
> to their interpretation. See `docs/v2_0_instrument_validation_record.md`
> Section 6.

Bins are [lower, upper), except the final bin [0.95, 1.0], which includes 1.0. Empty bins retain count zero and undefined summaries. Monotonicity is assessed between successive occupied bins using the recorded means, without interpolation or smoothing. A bin does not identify a unique c_avg value.

| c_avg bin | Count | Mean H_N | Median H_N | Min H_N | Max H_N | At maximum / bin count = fraction |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| [0.00, 0.05) | 750 | 0.989423212554 | 0.989513786218 | 0.979197034394 | 0.995501106282 | 0/750 = 0 |
| [0.05, 0.10) | 373 | 0.989616905131 | 0.989964343133 | 0.979155311771 | 0.99459527336 | 0/373 = 0 |
| [0.10, 0.15) | 333 | 0.989481800665 | 0.989802998957 | 0.97800421643 | 0.995588542358 | 0/333 = 0 |
| [0.15, 0.20) | 18 | 0.985226414087 | 0.985560589903 | 0.978051318695 | 0.991126054747 | 0/18 = 0 |
| [0.20, 0.25) | 990 | 0.989456755583 | 0.98975637668 | 0.976695162586 | 0.995582076244 | 0/990 = 0 |
| [0.25, 0.30) | 336 | 0.989374576545 | 0.989638370688 | 0.980502700493 | 0.994860873359 | 0/336 = 0 |
| [0.30, 0.35) | 329 | 0.989412695242 | 0.989390169356 | 0.980727265482 | 0.996041674115 | 0/329 = 0 |
| [0.35, 0.40) | 285 | 0.989215906325 | 0.989533738109 | 0.980539529351 | 0.995587337893 | 0/285 = 0 |
| [0.40, 0.45) | 1001 | 0.989345771124 | 0.989636491216 | 0.979942459086 | 0.994826116172 | 0/1001 = 0 |
| [0.45, 0.50) | 437 | 0.989642689722 | 0.989870068527 | 0.980345478061 | 0.994556316334 | 0/437 = 0 |
| [0.50, 0.55) | 472 | 0.989452199518 | 0.989655467392 | 0.978022755154 | 0.995125293163 | 0/472 = 0 |
| [0.55, 0.60) | 266 | 0.989341224639 | 0.989671352069 | 0.975475769715 | 0.994271032971 | 0/266 = 0 |
| [0.60, 0.65) | 928 | 0.98934349484 | 0.989782464981 | 0.973896049623 | 0.995317733955 | 0/928 = 0 |
| [0.65, 0.70) | 457 | 0.989438145041 | 0.989681777007 | 0.978879426438 | 0.994438953178 | 0/457 = 0 |
| [0.70, 0.75) | 319 | 0.989587012082 | 0.990035884559 | 0.980972914465 | 0.994209537982 | 0/319 = 0 |
| [0.75, 0.80) | 260 | 0.989355329294 | 0.989573292642 | 0.97979477443 | 0.994565483983 | 0/260 = 0 |
| [0.80, 0.85) | 1019 | 0.989443623257 | 0.989860712286 | 0.978532232712 | 0.995903611192 | 0/1019 = 0 |
| [0.85, 0.90) | 348 | 0.989329429753 | 0.989694026391 | 0.978401702754 | 0.995247587172 | 0/348 = 0 |
| [0.90, 0.95) | 275 | 0.989417499985 | 0.989797420633 | 0.976775470897 | 0.995130586149 | 0/275 = 0 |
| [0.95, 1.00] | 2804 | 0.998758525167 | 1 | 0.981237802504 | 1 | 2479/2804 = 0.884094151213 |

Counted minimum bin mean H_N: 0.985226414087, in bin(s) [0.15, 0.20). *(corrected: initialization artifact, see the correction notice at the head of this section)*

Counted from these runs: all 18 records in that minimum bin have the same recorded c_avg, 0.15600000000000003 (approximately 0.156). Thus the minimum bin mean also describes that observed c_avg value. *(corrected: all 18 are also step zero, which is the actual cause of the depression; the shared c_avg is the first-step anchor posture, not a response)*

Counted highest observed c_avg without all-zero novelty: 0.95. Counted lowest observed c_avg with all-zero novelty: 1.
Counted all-zero steps with c_avg strictly below 1.0, among all-zero steps: 0/2479 = 0.
Counted steps with c_avg exactly 1.0, among all logged steps: 2479/12000 = 0.206583333333.
In these runs, all-zero novelty was reached only at c_avg exactly 1.0. No onset strictly below 1.0 was observed; unsampled values are not estimated.

Counted exact-value detail at the two highest observed c_avg values:

| Recorded c_avg | Records | All-zero records / records = fraction | Mean recorded H_N |
| ---: | ---: | --- | ---: |
| 0.95 | 325 | 0/325 = 0 | 0.989288937129 |
| 1.0 | 2479 | 2479/2479 = 1 | 1 |

Mean H_N does not rise monotonically after its minimum. No monotonic rise onset is assigned. Counted downward transitions after the minimum: *(corrected: these are variation in a flat quantity, not a curve shape; see the correction notice at the head of this section)*

| From bin lower | To bin lower | From mean | To mean |
| ---: | ---: | ---: | ---: |
| 0.2 | 0.25 | 0.989456755583 | 0.989374576545 |
| 0.3 | 0.35 | 0.989412695242 | 0.989215906325 |
| 0.45 | 0.5 | 0.989642689722 | 0.989452199518 |
| 0.5 | 0.55 | 0.989452199518 | 0.989341224639 |
| 0.7 | 0.75 | 0.989587012082 | 0.989355329294 |
| 0.8 | 0.85 | 0.989443623257 | 0.989329429753 |

## Task 3: counted downstream association from these runs

| H_N at maximum | Recorded quantity | Count | Mean | Median | Min | Max |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| yes | U_sys | 2479 | 62.1846945726 | 63.5320668139 | 15.7696102628 | 90.7714305676 |
| yes | L_t | 2479 | 0.744637774538 | 0.76629421501 | 0.0971204912792 | 1.12886607454 |
| no | U_sys | 9521 | 61.7618960272 | 63.2178128666 | 15.5053337891 | 91.6826469611 |
| no | L_t | 9521 | 0.740412160133 | 0.760448199002 | 0.0938169490623 | 1.14007427356 |

| Recorded pair | Paired steps | Pearson correlation |
| --- | ---: | ---: |
| H_N and U_sys | 12000 | 0.255404462987 |
| H_N and L_t | 12000 | 0.250453044577 |

These are pooled associations among logged steps. Steps within a run share state and history; no independence claim, causal effect, significance test, or hypothetical corrected-utility calculation is made.

## Artifacts and scope

Per-step logs: one cusum_char_degen_seed<seed>_steps.csv per started run, enumerated exactly in cusum_char_degen_manifest.json. Summary outputs: cusum_char_degen_summary.json and cusum_char_degen_bins.csv when analysis completes. The extension is cusum_char_degen_probe.py. Source SHA256 hashes, versions, constructed settings, and completion status are recorded in the manifest.

Only probe-prefixed artifacts in simulation/diagnostics/ are opened for writing. Python bytecode writes are disabled and the reused audit hook rejects writes outside that prefix. No Git writes, production edits, repairs, or containment diff are performed. These probe outputs are not authoritative evidence.

Final verification: all saved per-step logs were read with csv.DictReader. Seed membership, row sequences, counts, bin membership and summaries, downstream summaries, correlations, and source SHA256 values reconciled. This verification performed no simulation runs.
