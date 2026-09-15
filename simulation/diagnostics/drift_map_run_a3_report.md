# Drift mapping characterization, attempt 3

Status: completed, 360 of 360 runs.

No CUSUM allowance, threshold, or alarm rule was chosen or run. The production adapter accumulator score was recorded only, with cop_cusum_drift false. No attack-success rate or corrected figure was derived. H_ref is a candidate and is not frozen. Nothing here is comparable to any pre-repair measurement.

## Preconditions and gates

T0 passed on operator-authorized retry. The preceding dispatch halted at T0(c) before any probe or run. The note was read from its committed blob only after its pinned LF-normalized SHA256 passed.

HEAD: `2f2b9e0329f3368fd86a71380bcdf2d91260dcb0`. Design blob SHA1: `0ddb02e4960948bc8f925ca77480f607370f0b2c`.

Design LF-normalized SHA256: `9aee2d8e482f441375877cfec39a5841857ecf46fe35beb68b8af3345491c748`.

T0 stderr warnings are retained in the T0 record and manifest. CRLF working-tree bytes matched the LF-normalized source pins.

| Gate | Measured evidence | Passed |
| --- | --- | --- |
| 2 | All seven source pins match | True |
| 3 | Seed 1835086199; factory 280 steps, extinction; common 280 steps, extinction; 7280 field comparisons; first difference None | True |
| 4 | 200 actions by 300 steps; 60000 comparisons; maximum key difference 0.0 | True |
| 5 | Attack vector null; 60 steps; 0 active, 0 modified | True |
| 6 | 60 recorder calls with exactly unchanged NumPy global state | True |

Amendment 2 gate evidence:

```json
{
  "common": {
    "first_fewer_than_two_novelty_vectors_step": 264,
    "nonpermitted_increase_count": 0,
    "permitted_after_step_0": 46,
    "raw_entropy_exact_matches": 280,
    "step_0": 2
  },
  "factory": {
    "first_fewer_than_two_novelty_vectors_step": 264,
    "nonpermitted_increase_count": 0,
    "permitted_after_step_0": 46,
    "raw_entropy_exact_matches": 280,
    "step_0": 2
  },
  "honest": {
    "first_fewer_than_two_novelty_vectors_step": null,
    "nonpermitted_increase_count": 0,
    "permitted_after_step_0": 0,
    "raw_entropy_exact_matches": 60,
    "step_0": 2
  }
}
```

## Registered results

### A1. Repaired honest baseline

Steps 10 and up. H_ref is a candidate and is not frozen. Suppression counts describe the repaired honest planner; no D1 statement is derived.

```json
{
  "records": 11600,
  "candidate_H_ref": 0.9891200034179453,
  "H_ref_frozen": false,
  "raw_entropy_p05": 0.9758244013258206,
  "raw_entropy_p25": 0.9867901757355118,
  "raw_entropy_p75": 0.9908933472202912,
  "raw_entropy_p95": 0.9928775872952869,
  "raw_entropy_exactly_zero_records": 0,
  "coupled_suppression_median": 0.256,
  "coupled_suppression_p95": 0.526,
  "coupled_suppression_at_or_above_0_75_records": 0,
  "coupled_suppression_exactly_1_0_records": 0,
  "allocation_share_medians": {
    "x_compute": 0.1297867162218379,
    "x_bio_welfare": 0.19772135774512486,
    "x_novelty_agency": 0.050519163753659654,
    "x_institutional_capacity": 0.2568464231580623,
    "x_transfer_comprehension": 0.27332343335362774,
    "x_resilience": 0.050733227878349954
  },
  "g_at_or_above_g_star_records": 83,
  "g_at_or_above_g_star_runs": 21
}
```

### A2. Honest entropy band

p05_H = 0.9758244013258206. Computed once from arm H and applied unchanged.

### A3. Approach to g_star

| Arm | Crossing | Not crossing | Extinction before crossing | t_star minus 50: min, median, max |
| --- | ---: | ---: | ---: | --- |
| M05 | 40 | 0 | 0 | 12.0, 46.0, 72.0 |
| M1 | 40 | 0 | 0 | 11.0, 33.0, 48.0 |
| M2 | 40 | 0 | 0 | 10.0, 18.5, 33.0 |
| M4 | 40 | 0 | 0 | 7.0, 13.0, 20.0 |
| R02 | 40 | 0 | 0 | 3.0, 55.5, 184.0 |
| R05 | 40 | 0 | 0 | 2.0, 10.5, 31.0 |
| R10 | 40 | 0 | 0 | 0.0, 5.0, 10.0 |
| R20 | 40 | 0 | 0 | 0.0, 2.0, 4.0 |

### A4. Silent crossings, primary quantity

| Arm | Silent crossings | Loud crossings | Runs not crossing |
| --- | ---: | ---: | ---: |
| M05 | 2 | 38 | 0 |
| M1 | 2 | 38 | 0 |
| M2 | 0 | 40 | 0 |
| M4 | 0 | 40 | 0 |
| R02 | 7 | 33 | 0 |
| R05 | 20 | 20 | 0 |
| R10 | 31 | 9 | 0 |
| R20 | 37 | 3 | 0 |

### A5. Entropy deficit

Each sum uses steps 50 through the first crossing, inclusive. Noncrossing sums use steps 50 through the last completed step and are not pre-crossing quantities.

| Arm | Crossing sum: min, median, max | Noncrossing sum, not pre-crossing: min, median, max |
| --- | --- | --- |
| M05 | 0.030977537085665974, 0.39763451894176316, 2.281696016385646 | None, None, None |
| M1 | 0.038799273422266856, 0.6314216764817541, 2.2118474124890124 | None, None, None |
| M2 | 0.057110250543326635, 0.5665395836256781, 3.671738824433673 | None, None, None |
| M4 | 0.1538210116904194, 0.7216389235850018, 2.9100012249990406 | None, None, None |
| R02 | 0.006005619796593087, 0.1283194135788589, 0.7107031975914537 | None, None, None |
| R05 | 0.0015269026259950857, 0.030062368675046247, 0.11617437871030134 | None, None, None |
| R10 | 0.0, 0.007859795879590792, 0.11654061363453738 | None, None, None |
| R20 | 0.0, 0.0030096481096233973, 0.0548701880321566 | None, None, None |

### A6. Paired trajectories

Across-seed summaries of each run's mean paired difference, attack minus honest. No t statistic or standard error was computed.

| Arm | Seeds | Raw entropy: mean, median | g: mean, median |
| --- | ---: | --- | --- |
| M05 | 40 | -0.3497457289822999, -0.3503889998618604 | 0.6611755000907271, 0.4575658318521093 |
| M1 | 40 | -0.527383906442943, -0.5258157364492353 | 1.8427855311098973, 1.141285942266507 |
| M2 | 40 | -0.6319625310593939, -0.6376247246572431 | 2.610674017663141, 1.472997569254571 |
| M4 | 40 | -0.7024016882806171, -0.6973770457904279 | 2.5469826647871003, 1.589136097331349 |
| R02 | 40 | -3.3680997298781944e-05, 3.039642825853983e-05 | 0.057306635898636125, 0.059376896333340645 |
| R05 | 40 | 0.00015516755793672457, 0.00011955570416799489 | 0.16047027793347096, 0.15967496979846008 |
| R10 | 40 | -0.00034135149376923025, -0.00039301312188112477 | 0.3637950928974574, 0.3644851298483859 |
| R20 | 40 | -0.0017205710482752809, -0.00177031694614141 | 0.7906719143811426, 0.7884843725821318 |

## Amendment 2 descriptive counts

Across all 360 runs, the step 0 fallback-increase distribution, increase to run count, was {"2": 360}.

Total permitted fallback increase after step 0: 4302. Non-permitted increase count was zero in every run: True.

Steps with fewer than two novelty vectors entered A1 through A6 exactly as recorded. No step was dropped or imputed.

| Arm | Runs reaching fewer than two novelty vectors | First such step for each affected run, seed: step |
| --- | ---: | --- |
| H | 0 | None |
| M05 | 10 | 1835086199: 297, 1835086205: 288, 1835086208: 266, 1835086213: 289, 1835086217: 289, 1835086221: 285, 1835086224: 295, 1835086229: 296, 1835086231: 275, 1835086237: 297 |
| M1 | 35 | 1835086199: 264, 1835086200: 247, 1835086201: 250, 1835086202: 216, 1835086204: 227, 1835086205: 253, 1835086206: 224, 1835086207: 288, 1835086208: 202, 1835086209: 240, 1835086210: 234, 1835086211: 236, 1835086212: 202, 1835086213: 251, 1835086214: 235, 1835086215: 264, 1835086216: 238, 1835086217: 218, 1835086218: 243, 1835086219: 258, 1835086221: 240, 1835086222: 246, 1835086223: 218, 1835086224: 288, 1835086225: 218, 1835086226: 223, 1835086227: 267, 1835086229: 212, 1835086231: 224, 1835086233: 270, 1835086234: 229, 1835086235: 217, 1835086236: 218, 1835086237: 216, 1835086238: 238 |
| M2 | 40 | 1835086199: 183, 1835086200: 254, 1835086201: 165, 1835086202: 194, 1835086203: 164, 1835086204: 226, 1835086205: 192, 1835086206: 179, 1835086207: 193, 1835086208: 181, 1835086209: 179, 1835086210: 178, 1835086211: 242, 1835086212: 194, 1835086213: 178, 1835086214: 230, 1835086215: 233, 1835086216: 185, 1835086217: 218, 1835086218: 210, 1835086219: 182, 1835086220: 199, 1835086221: 182, 1835086222: 225, 1835086223: 207, 1835086224: 203, 1835086225: 184, 1835086226: 216, 1835086227: 209, 1835086228: 185, 1835086229: 248, 1835086230: 183, 1835086231: 205, 1835086232: 196, 1835086233: 218, 1835086234: 164, 1835086235: 191, 1835086236: 212, 1835086237: 201, 1835086238: 222 |
| M4 | 39 | 1835086199: 185, 1835086200: 169, 1835086201: 212, 1835086202: 144, 1835086203: 147, 1835086205: 138, 1835086206: 228, 1835086207: 141, 1835086208: 263, 1835086209: 176, 1835086210: 232, 1835086211: 184, 1835086212: 213, 1835086213: 186, 1835086214: 164, 1835086215: 201, 1835086216: 169, 1835086217: 193, 1835086218: 198, 1835086219: 177, 1835086220: 221, 1835086221: 197, 1835086222: 210, 1835086223: 169, 1835086224: 249, 1835086225: 187, 1835086226: 220, 1835086227: 149, 1835086228: 203, 1835086229: 155, 1835086230: 211, 1835086231: 130, 1835086232: 181, 1835086233: 156, 1835086234: 227, 1835086235: 176, 1835086236: 201, 1835086237: 178, 1835086238: 170 |
| R02 | 0 | None |
| R05 | 0 | None |
| R10 | 0 | None |
| R20 | 0 | None |

## Execution and final source readings

Machine: YOTKOTEST. Maximum active batch workers: 15. Numerical-library threads were fixed to one and queried per worker. The runtime mode control supports normal, 15 workers, and work, 12 workers, with draining on reductions.

Resumed seeds: [{"arm": "R05", "job": "R05_1835086222", "reason": "In-flight job interrupted without a completion record", "seed": 1835086222, "utc": "2026-09-15T14:10:50.573802+00:00"}, {"arm": "R05", "job": "R05_1835086223", "reason": "In-flight job interrupted without a completion record", "seed": 1835086223, "utc": "2026-09-15T14:10:50.573821+00:00"}, {"arm": "R05", "job": "R05_1835086224", "reason": "In-flight job interrupted without a completion record", "seed": 1835086224, "utc": "2026-09-15T14:10:50.573824+00:00"}, {"arm": "R05", "job": "R05_1835086225", "reason": "In-flight job interrupted without a completion record", "seed": 1835086225, "utc": "2026-09-15T14:10:50.573826+00:00"}, {"arm": "R05", "job": "R05_1835086226", "reason": "In-flight job interrupted without a completion record", "seed": 1835086226, "utc": "2026-09-15T14:10:50.573828+00:00"}, {"arm": "R05", "job": "R05_1835086227", "reason": "In-flight job interrupted without a completion record", "seed": 1835086227, "utc": "2026-09-15T14:10:50.573830+00:00"}, {"arm": "R05", "job": "R05_1835086228", "reason": "In-flight job interrupted without a completion record", "seed": 1835086228, "utc": "2026-09-15T14:10:50.573831+00:00"}, {"arm": "R05", "job": "R05_1835086229", "reason": "In-flight job interrupted without a completion record", "seed": 1835086229, "utc": "2026-09-15T14:10:50.573833+00:00"}, {"arm": "R05", "job": "R05_1835086230", "reason": "In-flight job interrupted without a completion record", "seed": 1835086230, "utc": "2026-09-15T14:10:50.573834+00:00"}, {"arm": "R05", "job": "R05_1835086231", "reason": "In-flight job interrupted without a completion record", "seed": 1835086231, "utc": "2026-09-15T14:10:50.573836+00:00"}, {"arm": "R05", "job": "R05_1835086232", "reason": "In-flight job interrupted without a completion record", "seed": 1835086232, "utc": "2026-09-15T14:10:50.573837+00:00"}, {"arm": "R05", "job": "R05_1835086233", "reason": "In-flight job interrupted without a completion record", "seed": 1835086233, "utc": "2026-09-15T14:10:50.573839+00:00"}].

| Source | Start SHA256, LF-normalized working-tree bytes | End SHA256, same basis | Committed blob SHA1 |
| --- | --- | --- | --- |
| `simulation/metrics.py` | `6dc16efdfd4faed1638a96f6c2af7365757d1ca47eeb86deb5619a3e580b901f` | `6dc16efdfd4faed1638a96f6c2af7365757d1ca47eeb86deb5619a3e580b901f` | `7e7749d99636746aa2c3215da1edaa6ab5372611` |
| `simulation/agents.py` | `a51f6d833fa2e228aaa4e95ca59f9c7e0f83e5741c94deef88a0ea895554cfca` | `a51f6d833fa2e228aaa4e95ca59f9c7e0f83e5741c94deef88a0ea895554cfca` | `d21e5300eab6e4136141ea33aa0367b9aa47ed51` |
| `simulation/model.py` | `25e65d8daa4332df32198b424b25b1630d7a5aca98971c47eac82df7d5679993` | `25e65d8daa4332df32198b424b25b1630d7a5aca98971c47eac82df7d5679993` | `a1cf988532203b7119462eb9b04cf2e3b0541879` |
| `simulation/attack_adapter_v2.py` | `5c303dc96d458eb2165416c925fa5ff526d89fdf3bb7fb5c02538bb96f7c41ee` | `5c303dc96d458eb2165416c925fa5ff526d89fdf3bb7fb5c02538bb96f7c41ee` | `ecd9e6451065a6120e5dcb8a21b8206fb34f5e3e` |
| `simulation/run_attack_vector_revalidation_v2.py` | `20608b2db9efc3d67b4de1e801d2d025b757ca1a16a5e280a5999a66303beb45` | `20608b2db9efc3d67b4de1e801d2d025b757ca1a16a5e280a5999a66303beb45` | `ad80bd5fe60cc357a43e30c32ab3c12a758c0c2d` |
| `simulation/working_factor.py` | `16b542ed0f322bbf87036e31e8eff82e05e6d774c75bb8c29c6947a374f33e44` | `16b542ed0f322bbf87036e31e8eff82e05e6d774c75bb8c29c6947a374f33e44` | `bbfa1ea81ce8648adaf6c44a8b6f65188d206486` |
| `simulation/constants_v2_stage18.py` | `121a7c1c9e86d585553a2975ae27143804757a0ef344305124fcc4c802b3285b` | `121a7c1c9e86d585553a2975ae27143804757a0ef344305124fcc4c802b3285b` | `43b9766e63d1519faf59d1e8e4562c686a8149f2` |

Per-worker configurations, source readings, Python and NumPy versions, effective thread queries, and raw-log hashes are retained in completion records. The manifest inventories attempt artifacts. The operator performs the containment diff.
