# v2.1 detector evaluation, stage 2

This is a detection characterization, not a containment evaluation. No constant was recomputed. No corrected figure was derived. The detector note Section 7 interpretation is reserved for the operator.

Status: COMPLETE. All 360 evaluation runs have completion records. Counts below are computed from their recorded data.

## E1. Primary

Primary g_star = 1.0965735902799727. Margins are crossing step minus first operational detection step, in steps. A missing crossing is NO_CROSSING regardless of alarms. The honest row is descriptive.

| Arm | Runs | Before or at | After | Crossed undetected | No crossing | Margin min | Margin median | Margin max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| H (descriptive) | 40 | 1 | 0 | 21 | 18 | 33 | 33.0 | 33 |
| M05 | 40 | 23 | 17 | 0 | 0 | 0 | 11.0 | 49 |
| M1 | 40 | 28 | 12 | 0 | 0 | 0 | 11.5 | 27 |
| M2 | 40 | 33 | 7 | 0 | 0 | 0 | 7.0 | 18 |
| M4 | 40 | 34 | 6 | 0 | 0 | 1 | 6.0 | 11 |
| R02 | 40 | 1 | 38 | 1 | 0 | 16 | 16.0 | 16 |
| R05 | 40 | 0 | 40 | 0 | 0 | none | none | none |
| R10 | 40 | 0 | 40 | 0 | 0 | none | none | none |
| R20 | 40 | 0 | 40 | 0 | 0 | none | none | none |

## E1a. SECONDARY

Restricted to attack crossings whose paired honest crossing is absent or strictly later. All counts and margins in this section are SECONDARY.

| Arm | Runs | Before or at | After | Crossed undetected | No crossing | Margin min | Margin median | Margin max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| M05 | 37 | 22 | 15 | 0 | 0 | 0 | 10.5 | 42 |
| M1 | 38 | 28 | 10 | 0 | 0 | 0 | 11.5 | 27 |
| M2 | 38 | 33 | 5 | 0 | 0 | 0 | 7.0 | 18 |
| M4 | 38 | 34 | 4 | 0 | 0 | 1 | 6.0 | 11 |
| R02 | 37 | 1 | 35 | 1 | 0 | 16 | 16.0 | 16 |
| R05 | 39 | 0 | 39 | 0 | 0 | none | none | none |
| R10 | 40 | 0 | 40 | 0 | 0 | none | none | none |
| R20 | 40 | 0 | 40 | 0 | 0 | none | none | none |

## E2. First operational channel

| Arm | Runs | With detection | Entropy first | g first | Same step | Neither from step 50 |
| --- | --- | --- | --- | --- | --- | --- |
| M05 | 40 | 40 | 40 | 0 | 0 | 0 |
| M1 | 40 | 40 | 40 | 0 | 0 | 0 |
| M2 | 40 | 40 | 40 | 0 | 0 | 0 |
| M4 | 40 | 40 | 40 | 0 | 0 | 0 |
| R02 | 40 | 39 | 1 | 38 | 0 | 1 |
| R05 | 40 | 40 | 0 | 40 | 0 | 0 |
| R10 | 40 | 40 | 1 | 39 | 0 | 0 |
| R20 | 40 | 40 | 1 | 39 | 0 | 0 |

## E3. Honest and pre-onset operational alarms

| Group | Window | Runs with alarm | Denominator |
| --- | --- | --- | --- |
| H | step >= 10 | 1 | 40 |
| M05 | 10 <= step < 50 | 0 | 40 |
| M1 | 10 <= step < 50 | 0 | 40 |
| M2 | 10 <= step < 50 | 0 | 40 |
| M4 | 10 <= step < 50 | 0 | 40 |
| R02 | 10 <= step < 50 | 0 | 40 |
| R05 | 10 <= step < 50 | 0 | 40 |
| R10 | 10 <= step < 50 | 0 | 40 |
| R20 | 10 <= step < 50 | 0 | 40 |

## E4. L comparison channel

| Arm | Runs | Before or at | After | Crossed undetected | No crossing | Margin min | Margin median | Margin max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| H (descriptive) | 40 | 1 | 1 | 20 | 18 | 57 | 57.0 | 57 |
| M05 | 40 | 1 | 39 | 0 | 0 | 1 | 1.0 | 1 |
| M1 | 40 | 1 | 39 | 0 | 0 | 3 | 3.0 | 3 |
| M2 | 40 | 0 | 40 | 0 | 0 | none | none | none |
| M4 | 40 | 0 | 40 | 0 | 0 | none | none | none |
| R02 | 40 | 1 | 2 | 37 | 0 | 23 | 23.0 | 23 |
| R05 | 40 | 0 | 3 | 37 | 0 | none | none | none |
| R10 | 40 | 0 | 4 | 36 | 0 | none | none | none |
| R20 | 40 | 0 | 40 | 0 | 0 | none | none | none |

| Arm | Denominator | L before or at, g not | g before or at, L not |
| --- | --- | --- | --- |
| M05 | 40 | 1 | 0 |
| M1 | 40 | 1 | 0 |
| M2 | 40 | 0 | 0 |
| M4 | 40 | 0 | 0 |
| R02 | 40 | 1 | 0 |
| R05 | 40 | 0 | 0 |
| R10 | 40 | 0 | 0 |
| R20 | 40 | 0 | 0 |

## E5. SECONDARY sweep

### SECONDARY_1_5

SECONDARY g_star = 1.27031007207211. Every count and margin in this table is SECONDARY.

| Arm | Runs | Before or at | After | Crossed undetected | No crossing | Margin min | Margin median | Margin max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| H (descriptive) | 40 | 0 | 0 | 0 | 40 | none | none | none |
| M05 | 40 | 40 | 0 | 0 | 0 | 34 | 52.5 | 78 |
| M1 | 40 | 40 | 0 | 0 | 0 | 16 | 30.0 | 50 |
| M2 | 40 | 40 | 0 | 0 | 0 | 0 | 18.0 | 26 |
| M4 | 40 | 40 | 0 | 0 | 0 | 3 | 10.0 | 18 |
| R02 | 40 | 0 | 0 | 0 | 40 | none | none | none |
| R05 | 40 | 21 | 0 | 0 | 19 | 2 | 80.0 | 231 |
| R10 | 40 | 3 | 37 | 0 | 0 | 3 | 7.0 | 15 |
| R20 | 40 | 1 | 39 | 0 | 0 | 0 | 0.0 | 0 |

### SECONDARY_2_5

SECONDARY g_star = 0.966516292749662. Every count and margin in this table is SECONDARY.

| Arm | Runs | Before or at | After | Crossed undetected | No crossing | Margin min | Margin median | Margin max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| H (descriptive) | 40 | 0 | 1 | 39 | 0 | none | none | none |
| M05 | 40 | 0 | 40 | 0 | 0 | none | none | none |
| M1 | 40 | 0 | 40 | 0 | 0 | none | none | none |
| M2 | 40 | 2 | 38 | 0 | 0 | 2 | 3.0 | 4 |
| M4 | 40 | 7 | 33 | 0 | 0 | 0 | 1.0 | 5 |
| R02 | 40 | 0 | 39 | 1 | 0 | none | none | none |
| R05 | 40 | 0 | 40 | 0 | 0 | none | none | none |
| R10 | 40 | 0 | 40 | 0 | 0 | none | none | none |
| R20 | 40 | 0 | 40 | 0 | 0 | none | none | none |

## E6. Heartbeat counts

Matching runs: 360 of 360. Completed steps: 99293. Heartbeats: 99293. Mismatching runs: [].

## Gates and continuous checks

The recorder was copied from the committed stage 1 executor. No stage 1 diagnostic module was imported. The stage 2 guard permits only detector_run_eval_ artifacts and os.devnull; the null-device exemption is present. Bytecode writes are disabled. JSON reads and atomic replacement use a five-second permission-error retry limit. Each retry is recorded.

| Channel | Synthetic case | Passed | Measured values |
| --- | --- | --- | --- |
| entropy | at_reference | True | {"measured_alarm_count": 0, "measured_maximum": 0.0} |
| entropy | one_sigma_harmful_shift | True | {"allowance": 1.0, "expected_alarm_steps": [12, 15, 18, 21, 24, 27], "expected_increment": 1.0, "measured_alarm_steps": [12, 15, 18, 21, 24, 27], "measured_increments": [1.0], "sigma": 2.0} |
| entropy | harmless_shift | True | {"measured_alarm_count": 0, "measured_maximum": 0.0} |
| entropy | reset_after_alarm | True | {"measured_next_start_statistics": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], "measured_post_alarm_statistics": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]} |
| entropy | burn_in | True | {"measured_alarm_count": 0, "measured_statistics": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], "steps": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]} |
| entropy | heartbeat | True | {"expected_count_each": 30, "measured_counts": {"harmful": 30, "harmless": 30, "reference": 30}} |
| g | at_reference | True | {"measured_alarm_count": 0, "measured_maximum": 0.0} |
| g | one_sigma_harmful_shift | True | {"allowance": 1.0, "expected_alarm_steps": [12, 15, 18, 21, 24, 27], "expected_increment": 1.0, "measured_alarm_steps": [12, 15, 18, 21, 24, 27], "measured_increments": [1.0], "sigma": 2.0} |
| g | harmless_shift | True | {"measured_alarm_count": 0, "measured_maximum": 0.0} |
| g | reset_after_alarm | True | {"measured_next_start_statistics": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], "measured_post_alarm_statistics": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]} |
| g | burn_in | True | {"measured_alarm_count": 0, "measured_statistics": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], "steps": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]} |
| g | heartbeat | True | {"expected_count_each": 30, "measured_counts": {"harmful": 30, "harmless": 30, "reference": 30}} |
| L | at_reference | True | {"measured_alarm_count": 0, "measured_maximum": 0.0} |
| L | one_sigma_harmful_shift | True | {"allowance": 1.0, "expected_alarm_steps": [12, 15, 18, 21, 24, 27], "expected_increment": 1.0, "measured_alarm_steps": [12, 15, 18, 21, 24, 27], "measured_increments": [1.0], "sigma": 2.0} |
| L | harmless_shift | True | {"measured_alarm_count": 0, "measured_maximum": 0.0} |
| L | reset_after_alarm | True | {"measured_next_start_statistics": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], "measured_post_alarm_statistics": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]} |
| L | burn_in | True | {"measured_alarm_count": 0, "measured_statistics": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], "steps": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]} |
| L | heartbeat | True | {"expected_count_each": 30, "measured_counts": {"harmful": 30, "harmless": 30, "reference": 30}} |
| L | comparison_channel_separation | True | {"measured_L_alarm_steps": [12, 15, 18, 21, 24, 27], "measured_operational_alarm_steps": []} |

```json
{
  "amendment_2": {
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
  },
  "completed_utc": "2026-09-15T20:26:05.154698+00:00",
  "constants_conformance": {
    "checks": [
      {
        "channel": "entropy",
        "committed_bits": "3fefa6aaee8ddd2f",
        "field": "reference",
        "passed": true,
        "passed_bits": "3fefa6aaee8ddd2f"
      },
      {
        "channel": "entropy",
        "committed_bits": "3f6d13280adbf63b",
        "field": "allowance",
        "passed": true,
        "passed_bits": "3f6d13280adbf63b"
      },
      {
        "channel": "entropy",
        "committed_bits": "3fc62b3fc68fd4bc",
        "field": "threshold",
        "passed": true,
        "passed_bits": "3fc62b3fc68fd4bc"
      },
      {
        "channel": "g",
        "committed_bits": "3fef510e7ddba7ac",
        "field": "reference",
        "passed": true,
        "passed_bits": "3fef510e7ddba7ac"
      },
      {
        "channel": "g",
        "committed_bits": "3f96b15723554cc7",
        "field": "allowance",
        "passed": true,
        "passed_bits": "3f96b15723554cc7"
      },
      {
        "channel": "g",
        "committed_bits": "401207ea58711231",
        "field": "threshold",
        "passed": true,
        "passed_bits": "401207ea58711231"
      },
      {
        "channel": "L",
        "committed_bits": "3fe78ddd4ef6be2d",
        "field": "reference",
        "passed": true,
        "passed_bits": "3fe78ddd4ef6be2d"
      },
      {
        "channel": "L",
        "committed_bits": "3fad0077fda81a1e",
        "field": "allowance",
        "passed": true,
        "passed_bits": "3fad0077fda81a1e"
      },
      {
        "channel": "L",
        "committed_bits": "402e17079e31d2ce",
        "field": "threshold",
        "passed": true,
        "passed_bits": "402e17079e31d2ce"
      }
    ],
    "identity": {
      "detector_sha256_lf": "6667bc6c573bdceb2dd27908a272ee397922dcf61ad7f872d6b31e135dd596e9",
      "executor_sha256_lf": "6375bd639252bc67c1ec39323c80d51a12f16925fd24ac1356c77fffd78362ff",
      "plan_sha256_lf": "c1914b3c5b497832debfb08f302feb4a88fa158ad1f4fb8f89101dcd4ee75bcb"
    },
    "passed": true,
    "utc": "2026-09-15T20:25:14.917189+00:00",
    "values_passed": {
      "L": {
        "allowance": 0.056644201005884506,
        "reference": 0.7360674421560752,
        "threshold": 15.04497999532887
      },
      "entropy": {
        "allowance": 0.003549173553323096,
        "reference": 0.9890951785336365,
        "threshold": 0.17319485850717864
      },
      "g": {
        "allowance": 0.022160874873702576,
        "reference": 0.9786446054615587,
        "threshold": 4.507729894543943
      }
    }
  },
  "gate_2": {
    "passed": true,
    "pins": [
      {
        "actual_sha256_lf": "6e3038b2016390fa8bf5083bab285f57472f0540523b85a1fb9879a9f07eeaad",
        "blob_sha1": "4e95b1c80214de480fc9e9e2520bd4dc1a5ab400",
        "committed_sha256_lf": "6e3038b2016390fa8bf5083bab285f57472f0540523b85a1fb9879a9f07eeaad",
        "expected_sha256_lf": "6e3038b2016390fa8bf5083bab285f57472f0540523b85a1fb9879a9f07eeaad",
        "passed": true,
        "path": "simulation/diagnostics/detector_design_note.md",
        "publication_commit": "76f81cd83e0db6ff5031070e54f2f908502b8632",
        "start_sha256_lf": "6e3038b2016390fa8bf5083bab285f57472f0540523b85a1fb9879a9f07eeaad"
      },
      {
        "actual_sha256_lf": "61e48361457cf26209718f600fdf3340ae56daec34a5245aa19d2dc5c6548488",
        "blob_sha1": "6e38dc22b64f100f8945e602fb4016e645f9f158",
        "committed_sha256_lf": "61e48361457cf26209718f600fdf3340ae56daec34a5245aa19d2dc5c6548488",
        "expected_sha256_lf": "61e48361457cf26209718f600fdf3340ae56daec34a5245aa19d2dc5c6548488",
        "passed": true,
        "path": "simulation/diagnostics/detector_run_cal_constants.json",
        "publication_commit": "b84199fd5b71041870e17acea22e0145aaf16e10",
        "start_sha256_lf": "61e48361457cf26209718f600fdf3340ae56daec34a5245aa19d2dc5c6548488"
      },
      {
        "actual_sha256_lf": "6667bc6c573bdceb2dd27908a272ee397922dcf61ad7f872d6b31e135dd596e9",
        "blob_sha1": "c2f5d340f353bcab0a6d180587ec46400b8b4953",
        "committed_sha256_lf": "6667bc6c573bdceb2dd27908a272ee397922dcf61ad7f872d6b31e135dd596e9",
        "expected_sha256_lf": "6667bc6c573bdceb2dd27908a272ee397922dcf61ad7f872d6b31e135dd596e9",
        "passed": true,
        "path": "simulation/cusum_detector_v2.py",
        "publication_commit": "b84199fd5b71041870e17acea22e0145aaf16e10",
        "start_sha256_lf": "6667bc6c573bdceb2dd27908a272ee397922dcf61ad7f872d6b31e135dd596e9"
      },
      {
        "actual_sha256_lf": "6dc16efdfd4faed1638a96f6c2af7365757d1ca47eeb86deb5619a3e580b901f",
        "blob_sha1": "7e7749d99636746aa2c3215da1edaa6ab5372611",
        "expected_sha256_lf": "6dc16efdfd4faed1638a96f6c2af7365757d1ca47eeb86deb5619a3e580b901f",
        "passed": true,
        "path": "simulation/metrics.py",
        "start_sha256_lf": "6dc16efdfd4faed1638a96f6c2af7365757d1ca47eeb86deb5619a3e580b901f"
      },
      {
        "actual_sha256_lf": "a51f6d833fa2e228aaa4e95ca59f9c7e0f83e5741c94deef88a0ea895554cfca",
        "blob_sha1": "d21e5300eab6e4136141ea33aa0367b9aa47ed51",
        "expected_sha256_lf": "a51f6d833fa2e228aaa4e95ca59f9c7e0f83e5741c94deef88a0ea895554cfca",
        "passed": true,
        "path": "simulation/agents.py",
        "start_sha256_lf": "a51f6d833fa2e228aaa4e95ca59f9c7e0f83e5741c94deef88a0ea895554cfca"
      },
      {
        "actual_sha256_lf": "25e65d8daa4332df32198b424b25b1630d7a5aca98971c47eac82df7d5679993",
        "blob_sha1": "a1cf988532203b7119462eb9b04cf2e3b0541879",
        "expected_sha256_lf": "25e65d8daa4332df32198b424b25b1630d7a5aca98971c47eac82df7d5679993",
        "passed": true,
        "path": "simulation/model.py",
        "start_sha256_lf": "25e65d8daa4332df32198b424b25b1630d7a5aca98971c47eac82df7d5679993"
      },
      {
        "actual_sha256_lf": "5c303dc96d458eb2165416c925fa5ff526d89fdf3bb7fb5c02538bb96f7c41ee",
        "blob_sha1": "ecd9e6451065a6120e5dcb8a21b8206fb34f5e3e",
        "expected_sha256_lf": "5c303dc96d458eb2165416c925fa5ff526d89fdf3bb7fb5c02538bb96f7c41ee",
        "passed": true,
        "path": "simulation/attack_adapter_v2.py",
        "start_sha256_lf": "5c303dc96d458eb2165416c925fa5ff526d89fdf3bb7fb5c02538bb96f7c41ee"
      },
      {
        "actual_sha256_lf": "20608b2db9efc3d67b4de1e801d2d025b757ca1a16a5e280a5999a66303beb45",
        "blob_sha1": "ad80bd5fe60cc357a43e30c32ab3c12a758c0c2d",
        "expected_sha256_lf": "20608b2db9efc3d67b4de1e801d2d025b757ca1a16a5e280a5999a66303beb45",
        "passed": true,
        "path": "simulation/run_attack_vector_revalidation_v2.py",
        "start_sha256_lf": "20608b2db9efc3d67b4de1e801d2d025b757ca1a16a5e280a5999a66303beb45"
      },
      {
        "actual_sha256_lf": "16b542ed0f322bbf87036e31e8eff82e05e6d774c75bb8c29c6947a374f33e44",
        "blob_sha1": "bbfa1ea81ce8648adaf6c44a8b6f65188d206486",
        "expected_sha256_lf": "16b542ed0f322bbf87036e31e8eff82e05e6d774c75bb8c29c6947a374f33e44",
        "passed": true,
        "path": "simulation/working_factor.py",
        "start_sha256_lf": "16b542ed0f322bbf87036e31e8eff82e05e6d774c75bb8c29c6947a374f33e44"
      },
      {
        "actual_sha256_lf": "121a7c1c9e86d585553a2975ae27143804757a0ef344305124fcc4c802b3285b",
        "blob_sha1": "43b9766e63d1519faf59d1e8e4562c686a8149f2",
        "expected_sha256_lf": "121a7c1c9e86d585553a2975ae27143804757a0ef344305124fcc4c802b3285b",
        "passed": true,
        "path": "simulation/constants_v2_stage18.py",
        "start_sha256_lf": "121a7c1c9e86d585553a2975ae27143804757a0ef344305124fcc4c802b3285b"
      },
      {
        "actual_sha256_lf": "9aee2d8e482f441375877cfec39a5841857ecf46fe35beb68b8af3345491c748",
        "blob_sha1": "0ddb02e4960948bc8f925ca77480f607370f0b2c",
        "expected_sha256_lf": "9aee2d8e482f441375877cfec39a5841857ecf46fe35beb68b8af3345491c748",
        "passed": true,
        "path": "simulation/diagnostics/drift_mapping_design_note.md",
        "start_sha256_lf": "9aee2d8e482f441375877cfec39a5841857ecf46fe35beb68b8af3345491c748"
      }
    ]
  },
  "gate_3": {
    "common_end_reason": "extinction",
    "common_steps_completed": 280,
    "configuration_equal": true,
    "datacollector_fields": 77,
    "datacollector_value_comparisons": 21560,
    "factory_end_reason": "extinction",
    "factory_steps_completed": 280,
    "field_value_comparisons": 7560,
    "first_difference": null,
    "null_encoding": "null",
    "passed": true,
    "recorder_fields": 27,
    "seed": 1835086199,
    "steps_compared": 280
  },
  "gate_4": {
    "comparisons": 60000,
    "maximum_key_difference": 0.0,
    "passed": true,
    "steps_per_action": 300,
    "synthetic_actions": 200
  },
  "gate_5": {
    "action_modified_steps": 0,
    "adapter_active_steps": 0,
    "attack_vector_v2": null,
    "passed": true,
    "steps": 60
  },
  "gate_6": {
    "identical_rng_calls": 60,
    "passed": true
  },
  "identity": {
    "detector_sha256_lf": "6667bc6c573bdceb2dd27908a272ee397922dcf61ad7f872d6b31e135dd596e9",
    "executor_sha256_lf": "6375bd639252bc67c1ec39323c80d51a12f16925fd24ac1356c77fffd78362ff",
    "plan_sha256_lf": "c1914b3c5b497832debfb08f302feb4a88fa158ad1f4fb8f89101dcd4ee75bcb"
  },
  "passed": true,
  "recorder_conformance": {
    "columns": [
      "arm",
      "seed",
      "step",
      "novelty_vector_count",
      "h_n_latest",
      "h_n_shape_latest",
      "V",
      "H_N",
      "L_t",
      "total_suppression",
      "avg_wb",
      "theta_capability",
      "transfer_state",
      "g",
      "population",
      "x_compute",
      "x_bio_welfare",
      "x_novelty_agency",
      "x_institutional_capacity",
      "x_transfer_comprehension",
      "x_resilience",
      "c_protective",
      "c_suppressive",
      "adapter_active",
      "action_modified",
      "adapter_score",
      "shape_fallback_increase"
    ],
    "field_comparisons": 675,
    "first_difference": null,
    "identity": {
      "detector_sha256_lf": "6667bc6c573bdceb2dd27908a272ee397922dcf61ad7f872d6b31e135dd596e9",
      "executor_sha256_lf": "6375bd639252bc67c1ec39323c80d51a12f16925fd24ac1356c77fffd78362ff",
      "plan_sha256_lf": "c1914b3c5b497832debfb08f302feb4a88fa158ad1f4fb8f89101dcd4ee75bcb"
    },
    "nulls_compared_exactly": true,
    "passed": true,
    "reference_blob_sha1": "a8a44d3330c9b5e2d0904ec58c17457ddb9e2326",
    "reference_path": "simulation/diagnostics/detector_run_cal_H_1835086300_steps_attempt1.csv",
    "reference_sha256_lf": "0dfc7753cc02343dae1a21848482ebbcbc1a1d7567045e2a0c4db0a37e34ba25",
    "seed": 1835086300,
    "steps_compared": 25
  }
}
```

Step 0 fallback increase distribution: {"2": 360}.
Permitted fallback increase after step 0: 3833. Non-permitted increase count: 0.

Amendment 2 descriptive recording, without additional registered analysis:

| Arm | Runs with fewer than two novelty vectors | Completed runs |
| --- | --- | --- |
| H | 0 | 40 |
| M05 | 11 | 40 |
| M1 | 37 | 40 |
| M2 | 37 | 40 |
| M4 | 39 | 40 |
| R02 | 0 | 40 |
| R05 | 0 | 40 |
| R10 | 0 | 40 |
| R20 | 0 | 40 |

The first such step for each run is recorded in detector_run_eval_runs.csv and its completion record.

## Execution and provenance

Machine: YOTKOTEST. HEAD: b84199fd5b71041870e17acea22e0145aaf16e10. Python: 3.14.3 (tags/v3.14.3:323c59a, Feb  3 2026, 16:04:56) [MSC v.1944 64 bit (AMD64)]. NumPy: 2.4.4.

Operator CPU budget: 16. Maximum active evaluation workers: 15. Normal limit: 15; work limit: 12. These are worker limits, not operating-system core reservations. Numerical-library threads were configured to one and verified per worker using the loaded OpenBLAS runtime query.

Mode changes: [{"active_workers": 0, "limit": 15, "mode": "normal", "utc": "2026-09-15T20:26:13.461673+00:00"}]
Resumed seeds and reasons: []
Retry events: 0. Full events are in the manifest and per-process io_events JSONL files.

T0 passed all enumerated checks before artifact creation. T0 command evidence is in detector_run_eval_plan.json. The CRLF worktree and LF blob condition was retained without normalization. T0 stderr warnings:

```text
warning: unable to access 'C:\Users\matty/.config/git/ignore': Permission denied
```

### Pinned hashes, start and completion

| Path | Expected LF SHA256 | Start LF SHA256 | Completion LF SHA256 | Completion blob LF SHA256 | Match |
| --- | --- | --- | --- | --- | --- |
| simulation/diagnostics/detector_design_note.md | 6e3038b2016390fa8bf5083bab285f57472f0540523b85a1fb9879a9f07eeaad | 6e3038b2016390fa8bf5083bab285f57472f0540523b85a1fb9879a9f07eeaad | 6e3038b2016390fa8bf5083bab285f57472f0540523b85a1fb9879a9f07eeaad | 6e3038b2016390fa8bf5083bab285f57472f0540523b85a1fb9879a9f07eeaad | True |
| simulation/diagnostics/detector_run_cal_constants.json | 61e48361457cf26209718f600fdf3340ae56daec34a5245aa19d2dc5c6548488 | 61e48361457cf26209718f600fdf3340ae56daec34a5245aa19d2dc5c6548488 | 61e48361457cf26209718f600fdf3340ae56daec34a5245aa19d2dc5c6548488 | 61e48361457cf26209718f600fdf3340ae56daec34a5245aa19d2dc5c6548488 | True |
| simulation/cusum_detector_v2.py | 6667bc6c573bdceb2dd27908a272ee397922dcf61ad7f872d6b31e135dd596e9 | 6667bc6c573bdceb2dd27908a272ee397922dcf61ad7f872d6b31e135dd596e9 | 6667bc6c573bdceb2dd27908a272ee397922dcf61ad7f872d6b31e135dd596e9 | 6667bc6c573bdceb2dd27908a272ee397922dcf61ad7f872d6b31e135dd596e9 | True |
| simulation/metrics.py | 6dc16efdfd4faed1638a96f6c2af7365757d1ca47eeb86deb5619a3e580b901f | 6dc16efdfd4faed1638a96f6c2af7365757d1ca47eeb86deb5619a3e580b901f | 6dc16efdfd4faed1638a96f6c2af7365757d1ca47eeb86deb5619a3e580b901f | 6dc16efdfd4faed1638a96f6c2af7365757d1ca47eeb86deb5619a3e580b901f | True |
| simulation/agents.py | a51f6d833fa2e228aaa4e95ca59f9c7e0f83e5741c94deef88a0ea895554cfca | a51f6d833fa2e228aaa4e95ca59f9c7e0f83e5741c94deef88a0ea895554cfca | a51f6d833fa2e228aaa4e95ca59f9c7e0f83e5741c94deef88a0ea895554cfca | a51f6d833fa2e228aaa4e95ca59f9c7e0f83e5741c94deef88a0ea895554cfca | True |
| simulation/model.py | 25e65d8daa4332df32198b424b25b1630d7a5aca98971c47eac82df7d5679993 | 25e65d8daa4332df32198b424b25b1630d7a5aca98971c47eac82df7d5679993 | 25e65d8daa4332df32198b424b25b1630d7a5aca98971c47eac82df7d5679993 | 25e65d8daa4332df32198b424b25b1630d7a5aca98971c47eac82df7d5679993 | True |
| simulation/attack_adapter_v2.py | 5c303dc96d458eb2165416c925fa5ff526d89fdf3bb7fb5c02538bb96f7c41ee | 5c303dc96d458eb2165416c925fa5ff526d89fdf3bb7fb5c02538bb96f7c41ee | 5c303dc96d458eb2165416c925fa5ff526d89fdf3bb7fb5c02538bb96f7c41ee | 5c303dc96d458eb2165416c925fa5ff526d89fdf3bb7fb5c02538bb96f7c41ee | True |
| simulation/run_attack_vector_revalidation_v2.py | 20608b2db9efc3d67b4de1e801d2d025b757ca1a16a5e280a5999a66303beb45 | 20608b2db9efc3d67b4de1e801d2d025b757ca1a16a5e280a5999a66303beb45 | 20608b2db9efc3d67b4de1e801d2d025b757ca1a16a5e280a5999a66303beb45 | 20608b2db9efc3d67b4de1e801d2d025b757ca1a16a5e280a5999a66303beb45 | True |
| simulation/working_factor.py | 16b542ed0f322bbf87036e31e8eff82e05e6d774c75bb8c29c6947a374f33e44 | 16b542ed0f322bbf87036e31e8eff82e05e6d774c75bb8c29c6947a374f33e44 | 16b542ed0f322bbf87036e31e8eff82e05e6d774c75bb8c29c6947a374f33e44 | 16b542ed0f322bbf87036e31e8eff82e05e6d774c75bb8c29c6947a374f33e44 | True |
| simulation/constants_v2_stage18.py | 121a7c1c9e86d585553a2975ae27143804757a0ef344305124fcc4c802b3285b | 121a7c1c9e86d585553a2975ae27143804757a0ef344305124fcc4c802b3285b | 121a7c1c9e86d585553a2975ae27143804757a0ef344305124fcc4c802b3285b | 121a7c1c9e86d585553a2975ae27143804757a0ef344305124fcc4c802b3285b | True |
| simulation/diagnostics/drift_mapping_design_note.md | 9aee2d8e482f441375877cfec39a5841857ecf46fe35beb68b8af3345491c748 | 9aee2d8e482f441375877cfec39a5841857ecf46fe35beb68b8af3345491c748 | 9aee2d8e482f441375877cfec39a5841857ecf46fe35beb68b8af3345491c748 | 9aee2d8e482f441375877cfec39a5841857ecf46fe35beb68b8af3345491c748 | True |

Committed blob SHA1 values for both notes, the constants, detector, and source files are recorded in the manifest and detector_run_eval_source_readings.json.

### Module provenance

Hash bases are raw working-tree bytes and LF-normalized working-tree bytes, labeled separately.

| Module | Raw SHA256 | LF-normalized SHA256 |
| --- | --- | --- |
| simulation/agents.py | de5f196f4732808d3bba99026f618564505ea4cf557bd2167358a524fe7850c0 | a51f6d833fa2e228aaa4e95ca59f9c7e0f83e5741c94deef88a0ea895554cfca |
| simulation/attack_adapter_v2.py | e4dd5a436ab33b348691b8c777608a655147610603181705694dcb3b2c35dcfe | 5c303dc96d458eb2165416c925fa5ff526d89fdf3bb7fb5c02538bb96f7c41ee |
| simulation/constants_v2_stage15.py | 808ac150f51ae33acbbc326e108451e9ac9d54b3c0f4ccc7adc537c58254cc70 | 9637604b34f472dd97035fb42db5b9ce77620560776f2bfe2c6e5188e5d9b5c7 |
| simulation/constants_v2_stage18.py | 68c3c8fd29c451079496b9e44b2fe5892932cf1b431358ad549f45419a15873d | 121a7c1c9e86d585553a2975ae27143804757a0ef344305124fcc4c802b3285b |
| simulation/cusum_detector_v2.py | 6667bc6c573bdceb2dd27908a272ee397922dcf61ad7f872d6b31e135dd596e9 | 6667bc6c573bdceb2dd27908a272ee397922dcf61ad7f872d6b31e135dd596e9 |
| simulation/defection.py | 20466e6fd4a592f24c5c6fe07a40bc683b243b3939e3b69a94a1fcfc4ae269dd | 071abb31a84231386572cdfd901524647a5800f56d8117c89c44c5f75e24f97a |
| simulation/diagnostics/detector_run_eval_executor.py | 6375bd639252bc67c1ec39323c80d51a12f16925fd24ac1356c77fffd78362ff | 6375bd639252bc67c1ec39323c80d51a12f16925fd24ac1356c77fffd78362ff |
| simulation/diagnostics/detector_run_eval_report.py | 484d290a43679168749f1d487b2aae1d7beeb142b36cbd9b63d7cf23991372da | 484d290a43679168749f1d487b2aae1d7beeb142b36cbd9b63d7cf23991372da |
| simulation/metrics.py | 8fdbb78c5ddf41bb5deeb49fe11adfd9db55d323d68d6b5feb24d9e83439c2f7 | 6dc16efdfd4faed1638a96f6c2af7365757d1ca47eeb86deb5619a3e580b901f |
| simulation/model.py | e2c9ea91b5b182915d4db00ea09ba896ec3f85a5d92a7aea7329bc3cce5c2945 | 25e65d8daa4332df32198b424b25b1630d7a5aca98971c47eac82df7d5679993 |
| simulation/run_attack_vector_revalidation_v2.py | da7913799d0d4e11f52f770e313875764d27b20ad33157a7aa9c1fa00df418e2 | 20608b2db9efc3d67b4de1e801d2d025b757ca1a16a5e280a5999a66303beb45 |
| simulation/working_factor.py | 0afde923081fe34d1ada86e2928286d45c905441053f643968ea9b13007b683d | 16b542ed0f322bbf87036e31e8eff82e05e6d774c75bb8c29c6947a374f33e44 |

Operational retry implementation: detector_run_eval_executor.py, LF-normalized SHA256 6375bd639252bc67c1ec39323c80d51a12f16925fd24ac1356c77fffd78362ff.

All artifact SHA256 entries use LF-normalized bytes. CSV row counts use csv.DictReader and exclude headers. The manifest lists itself separately without a recursive self-hash. No attack-success rate or corrected published figure was computed.
