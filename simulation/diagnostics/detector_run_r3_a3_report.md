# Detector round 3, stage A, attempt 3

Complete. No model was stepped, no arm was run, no detector was evaluated, and nothing was interpreted. Stage B is a separate dispatch that may begin only after these outputs are committed and pushed.

Attempts 1 and 2 each halted in authoring before derivation and produced no constant. This attempt used the same registered scientific procedure. Its script was authored through the shell from one base64 payload and parsed with compile before execution, without bytecode output.

From pre-registration Section 1, verbatim:

> This observable was chosen knowing how the attack
> works.

## Derived values and pinned values

All comparisons below use exact numeric equality without rounding or tolerance.

| Quantity | Derived | Pinned | Matched |
| --- | --- | --- | --- |
| attempt1 logs | 107 | 107 | True |
| attempt2 logs | 13 | 13 | True |
| median x_compute | 0.13058054663961136 | 0.13058054663961136 | True |
| median x_bio_welfare | 0.19789308864393101 | 0.19789308864393101 | True |
| median x_novelty_agency | 0.050694324487428735 | 0.050694324487428735 | True |
| median x_institutional_capacity | 0.25643120498706085 | 0.25643120498706085 | True |
| median x_transfer_comprehension | 0.27322100367503155 | 0.27322100367503155 | True |
| median x_resilience | 0.051169013866533296 | 0.051169013866533296 | True |
| A reference | 0.27535941373839806 | 0.27535941373839806 | True |
| A sample standard deviation | 0.09062135730471185 | 0.09062135730471185 | True |
| A allowance | 0.045310678652355926 | 0.045310678652355926 | True |
| A threshold 97.5 PRIMARY | 0.7701182670542909 | 0.7701182670542909 | True |
| A maxima at or above 97.5 | 3 | 3 | True |
| A threshold 95.0 SECONDARY | 0.6957853699901844 | 0.6957853699901844 | True |
| A maxima at or above 95.0 | 6 | 6 | True |
| A threshold 90.0 SECONDARY | 0.6044759669277072 | 0.6044759669277072 | True |
| A maxima at or above 90.0 | 12 | 12 | True |
| transfer_share reference | 0.27322100367503155 | 0.27322100367503155 | True |
| transfer_share allowance | 0.034737970363912324 | 0.034737970363912324 | True |
| transfer_share threshold 97.5 SECONDARY | 0.42746784963836376 | 0.42746784963836376 | True |
| transfer_share maxima at or above 97.5 | 3 | 3 | True |
| compute_share reference | 0.13058054663961136 | 0.13058054663961136 | True |
| compute_share allowance | 0.04276403212505429 | 0.04276403212505429 | True |
| compute_share threshold 97.5 SECONDARY | 0.6568684632630958 | 0.6568684632630958 | True |
| compute_share maxima at or above 97.5 | 3 | 3 | True |

## Evidence and derivation

Counted: 120 committed completion records and their named logs; 107 attempt1 logs and 13 attempt2 logs. All 120 log hashes matched their completion records before parsing. Counted raw CSV records: 36000. Counted records at steps 10 and up: 34800.

Every committed input was retrieved with git cat-file from ddbbacd40e71c0e82fbee399bfd0f1789bdd2126. Each input's read commit, LF-normalized SHA256, and Git blob SHA1 are recorded in the constants and manifest.

The six median shares use the registered order and all records at steps 10 and up. A is the sum of the six absolute deviations. Sample standard deviations use ddof=1, and allowances are half those values. Per-run maxima come from the unchanged committed channel_cusum with threshold=None, without resets. Threshold percentiles use NumPy method='linear'.

| Channel | Direction | Role | Sample standard deviation | Records |
| --- | --- | --- | --- | --- |
| A | upper | PRIMARY | 0.09062135730471185 | 34800 |
| transfer_share | lower | SECONDARY, attack-specific | 0.06947594072782465 | 34800 |
| compute_share | upper | SECONDARY, attack-specific | 0.08552806425010857 | 34800 |

The constants file includes the 120 seed-labeled maxima behind each channel's thresholds and a binary64 hexadecimal mirror of every numeric constant, count, and per-run value. The maxima CSV has one row per channel and seed. Its row count is recorded in the manifest using csv.DictReader excluding the header.

## Carried-forward values

The following values were copied from the committed round 1 and round 2 files without recomputation.

| Channel | Reference | Allowance | Threshold |
| --- | --- | --- | --- |
| entropy | 0.9890951785336365 | 0.003549173553323096 | 0.17319485850717864 |
| g | 0.9786446054615587 | 0.022160874873702576 | 4.507729894543943 |
| L | 0.7360674421560752 | 0.056644201005884506 | 15.04497999532887 |

| Case | g_star | k |
| --- | --- | --- |
| PRIMARY_2_0 | 1.0965735902799727 | 9 |
| SECONDARY_1_5 | 1.27031007207211 | 2 |
| SECONDARY_2_5 | 0.966516292749662 | 106 |

> At a reference successor capability of 2.5, g_star lies below the honest median of g, every honest calibration run spends long spans above it, and k is accordingly large. A hazard there measures persistence far beyond honest behavior rather than the approach to a defection boundary.

## Preconditions and provenance

T0a through T0h passed. Branch main; required ancestry and publication checks passed. The exact tracked-only status command returned no output lines. There were 120 calibration-completion paths. The attempt 3 namespace was fresh before artifact creation. The nine artifacts from attempts 1 and 2 were tracked and unmodified. All 14 source pins matched at start and completion.

| Path | Start LF SHA256 | Completion LF SHA256 |
| --- | --- | --- |
| simulation/diagnostics/detector_round3_design_note.md | b1309a7463b1d7b1f277fd4dd56e997f90fecf2386411871be22ccfabed6db83 | b1309a7463b1d7b1f277fd4dd56e997f90fecf2386411871be22ccfabed6db83 |
| simulation/diagnostics/detector_round2_design_note.md | 45cfe81643e6d056310c36149c24ee47a029920a42d2e63540db2f9f05e7a632 | 45cfe81643e6d056310c36149c24ee47a029920a42d2e63540db2f9f05e7a632 |
| simulation/diagnostics/detector_run_r2_constants.json | 8340f3697b529cfa2c0afb773d13e769258ef8a439f450ec68d9512239c05b98 | 8340f3697b529cfa2c0afb773d13e769258ef8a439f450ec68d9512239c05b98 |
| simulation/diagnostics/detector_run_cal_constants.json | 61e48361457cf26209718f600fdf3340ae56daec34a5245aa19d2dc5c6548488 | 61e48361457cf26209718f600fdf3340ae56daec34a5245aa19d2dc5c6548488 |
| simulation/cusum_detector_v2.py | 6667bc6c573bdceb2dd27908a272ee397922dcf61ad7f872d6b31e135dd596e9 | 6667bc6c573bdceb2dd27908a272ee397922dcf61ad7f872d6b31e135dd596e9 |
| simulation/diagnostics/detector_design_note.md | 6e3038b2016390fa8bf5083bab285f57472f0540523b85a1fb9879a9f07eeaad | 6e3038b2016390fa8bf5083bab285f57472f0540523b85a1fb9879a9f07eeaad |
| simulation/diagnostics/detector_run_eval_executor.py | 6375bd639252bc67c1ec39323c80d51a12f16925fd24ac1356c77fffd78362ff | 6375bd639252bc67c1ec39323c80d51a12f16925fd24ac1356c77fffd78362ff |
| simulation/metrics.py | 6dc16efdfd4faed1638a96f6c2af7365757d1ca47eeb86deb5619a3e580b901f | 6dc16efdfd4faed1638a96f6c2af7365757d1ca47eeb86deb5619a3e580b901f |
| simulation/agents.py | a51f6d833fa2e228aaa4e95ca59f9c7e0f83e5741c94deef88a0ea895554cfca | a51f6d833fa2e228aaa4e95ca59f9c7e0f83e5741c94deef88a0ea895554cfca |
| simulation/model.py | 25e65d8daa4332df32198b424b25b1630d7a5aca98971c47eac82df7d5679993 | 25e65d8daa4332df32198b424b25b1630d7a5aca98971c47eac82df7d5679993 |
| simulation/attack_adapter_v2.py | 5c303dc96d458eb2165416c925fa5ff526d89fdf3bb7fb5c02538bb96f7c41ee | 5c303dc96d458eb2165416c925fa5ff526d89fdf3bb7fb5c02538bb96f7c41ee |
| simulation/run_attack_vector_revalidation_v2.py | 20608b2db9efc3d67b4de1e801d2d025b757ca1a16a5e280a5999a66303beb45 | 20608b2db9efc3d67b4de1e801d2d025b757ca1a16a5e280a5999a66303beb45 |
| simulation/working_factor.py | 16b542ed0f322bbf87036e31e8eff82e05e6d774c75bb8c29c6947a374f33e44 | 16b542ed0f322bbf87036e31e8eff82e05e6d774c75bb8c29c6947a374f33e44 |
| simulation/constants_v2_stage18.py | 121a7c1c9e86d585553a2975ae27143804757a0ef344305124fcc4c802b3285b | 121a7c1c9e86d585553a2975ae27143804757a0ef344305124fcc4c802b3285b |

Machine: YOTKOTEST. HEAD: ddbbacd40e71c0e82fbee399bfd0f1789bdd2126. Python: 3.14.3 (tags/v3.14.3:323c59a, Feb  3 2026, 16:04:56) [MSC v.1944 64 bit (AMD64)]. NumPy: 2.4.4. Simulation workers: 0. Derivation processes: 1. Numerical-library threads: 1, verified from the loaded OpenBLAS runtime.

The write guard permitted only detector_run_r3_a3_ files under simulation/diagnostics/ and os.devnull; the null-device exemption was present. Bytecode writes were disabled. No randomness was consumed. Existing working-tree line endings were not changed. The operator performs the containment diff.

Known environment conditions were recorded without repair: CRLF working-tree files against LF blobs, and permission warnings from the unreadable cache or global ignore path.

T0 stderr warnings:

```text
warning: unable to access 'C:\Users\matty/.config/git/ignore': Permission denied
```

All output hashes use LF-normalized bytes. CSV row counts use csv.DictReader excluding headers, with null for non-CSV outputs. The manifest lists itself separately with a null self-hash to avoid recursive hashing. Committed blob SHA1 values for all three detector notes, both earlier constants files, the detector module, every pinned source, and every calibration input are included.
