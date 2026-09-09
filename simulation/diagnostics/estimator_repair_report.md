# v2.1 step 1: novelty entropy estimator repair

Implementation and component measurement completed. All requested validation checks passed. The positive control failed before the edit and passed afterward. This report provides measurements and the requested mechanical prediction; it derives no corrected published figure.

## T0. Preconditions and environment observations

All seven enumerated checks passed. Commands ran with `GIT_OPTIONAL_LOCKS=0` to disable optional Git locks. The exact tracked-only status form was used.

| Check | Read result | Result |
| --- | --- | --- |
| a. `git rev-parse --abbrev-ref HEAD` | `main`, exit 0 | PASS |
| b. Required commit ancestry | `merge-base --is-ancestor 2044f50a8cf71874f259e74fd05ec495169b9ae4 HEAD`, exit 0 | PASS |
| c. `git rev-parse HEAD:simulation/metrics.py` | `ce59c48e7e729917dc27df273c8c2bf1fd8e248b`, exit 0 | PASS |
| d. `git status --porcelain --untracked-files=no` | Exit 0; zero stdout lines | PASS |
| e. Raw worktree metrics SHA256 | `536a77fb5e45d6d167480ab7af6ea9f5a0e56b9927be0d09713400aa873fae63` | PASS |
| f. Advisor | Present at root; `git ls-files --error-unmatch LINEAGE_IMPERATIVE_ADVISOR.md` exited 1 | PASS |
| g. T1 calibration row | Re-read steps_ge_10 median V as `0.0238802249185` | PASS |

HEAD read during T0: `2044f50a8cf71874f259e74fd05ec495169b9ae4`.

The calibration row was read from [drift_char_report.md](drift_char_report.md), T1:

```text
| steps_ge_10 | 11600 | 0.0238802249185 | 0.0705886247884 | 0.124174294722 | 2395 |
```

T0 stderr warning from the tracked-only status command, recorded without halting:

```text
warning: unable to access 'C:\Users\matty/.config/git/ignore': Permission denied
```

The absent-index advisor check emitted the expected diagnostic:

```text
error: pathspec 'LINEAGE_IMPERATIVE_ADVISOR.md' did not match any file(s) known to git
Did you forget to 'git add'?
```

An initial source-display command encountered a cp1252 `UnicodeEncodeError` while displaying an existing mathematical symbol. The read was repeated with stdout configured as UTF-8. This involved no measurement or file write.

Known conditions, supplied by the operator and accepted without re-investigation: 380 of 1,537 tracked worktree files contain CRLF against LF Git blobs, with independently audited zero content differences; `.pytest_cache/` is unreadable, absent from `.gitignore`, and contains zero tracked files. Neither condition halted this attempt. The exact tracked-only command emitted no cache warning. No worktree bytes were compared with Git blob bytes, and no file was normalized. The prior halt records are historical and closed by the revised instructions.

## T1. Measurements before the edit

The fixed draw uses `numpy.random.default_rng(20260908)` to generate a 200 by 10 standard-normal matrix. For the amplitude control, it is centered and scaled once by `sqrt(V_ref / trace(covariance))`. The measured starting covariance trace is `0.023880224918499993`. Each requested amplitude multiplies this same matrix. The calibration-scaled control and the unit-variance preservation arm are separate fixtures.

[Instrument validation record, Section 6](../../docs/v2_0_instrument_validation_record.md), lines 333-345, records the scale-invariance pattern but does not identify its draw or seed there. The deterministic fixture here reproduces that pattern; its entropy value is measured independently. The fixture was fixed before either measurement phase.

| Amplitude | Measured pre-edit H_N | Measured post-edit H_N |
| --- | --- | --- |
| 1 | 0.985251420932311 | 0.936198641078819 |
| 0.80000000000000004 | 0.985251420932311 | 0.840806703174814 |
| 0.5 | 0.985251420932311 | 0.519851603643329 |
| 0.10000000000000001 | 0.985251420932311 | 0.029118580066229 |
| 0.001 | 0.985251420932311 | 0.000002955749829 |
| 0 | 1.000000000000000 | 0.000000000000000 |

Before the edit, all five nonzero amplitudes are identical at fifteen decimal places. The full-precision measured spread is `3.3306690738754696e-16`. At zero amplitude, the measured value is exactly `1.0`. The positive control, requiring strict decrease and a zero endpoint, FAILED as required. Full-precision values and covariance traces are retained in the amplitude CSVs.

The pre-edit component JSON, both pre-edit CSVs, and the pre-edit regression outputs were written before the production edit. Their timestamps and the later edit timestamp are retained in their JSON records.

## T2. Implemented expression

At [metrics.py](../metrics.py), lines 42-47, the added constants are `H_N_V_REF = 0.0238802249185` and `H_N_MAGNITUDE_SAT_K = 3.0`. The calibration comment records the 40 runs, 11,600 records at steps 10 and up, publication in drift_char T1, and operator ratification on 2026-09-08.

At lines 799-801, raw covariance trace is read immediately after covariance construction and bounded below by zero for floating-point error. The existing spectral calculation supplies the clipped shape value. Lines 815-817 apply:

```python
shape = float(np.clip(h_n, 0.0, 1.0))
magnitude = -np.expm1(-H_N_MAGNITUDE_SAT_K * V / H_N_V_REF)
return float(np.clip(shape * magnitude, 0.0, 1.0))
```

The requested patch is recorded in [estimator_repair_metrics.diff](estimator_repair_metrics.diff). Existing CRLF line endings were retained in the production edit. The diff and normalized hashes operate on an in-memory LF representation.

## T3. Measurements after the edit

The amplitude table above shows strictly decreasing measured H_N across the five nonzero factors. At factor zero, the repaired estimator returns exactly `0.0`. The positive control PASSED.

### Calibration pin

With V set exactly equal to V_ref, the measured magnitude is `0.9502129316321360`, equal to the specified binary64 value for `1 - exp(-3)`. The median factor re-read from drift_char T1 is `0.950212895482`. Their difference is `3.6150135995782762e-08`. This is the expected distinction between the transform of an interpolated median and the interpolated median of a concave transform, as specified by the operator. The small floating-point trace difference in the amplitude fixture is separate from this exact-pin calculation.

### Shape preservation and saturation

The preservation arm uses the original unit-variance seeded draw, its reversed-axis copy, and a copy with the last five axes set to zero. Measured results:

| Matrix | Covariance trace V | Pre-edit H_N | Post-edit magnitude | Recovered shape: H_N_post / magnitude |
| --- | --- | --- | --- | --- |
| unit_variance | 9.6747493945742953 | 0.985251420932311 | 1 | 0.985251420932311 |
| axis_permuted | 9.6747493945742953 | 0.985251420932311 | 1 | 0.985251420932311 |
| rank_reduced | 5.0479180145982587 | 0.69459295463365522 | 1 | 0.69459295463365522 |

The largest measured absolute deviation between recovered shape and pre-edit H_N is `0.0`. Axis permutation deviation is `0.0`. The rank-reduced matrix has a lower recovered shape than the full matrix. These preservation checks PASSED. For the unit-variance matrix, measured V is `9.6747493945742953` and magnitude is exactly `1.0`, passing saturation.

### Existing regression suite

`simulation/test_refactor_1x.py` was executed through `runpy.run_path(..., run_name="__main__")` before and after the edit, in fresh guarded Python processes. Its test order and source were retained. The wrapper sets the initial NumPy seed to 20260908 before entry; the suite also retains its own internal deterministic seeds.

| Phase | Exit | Counted passes | Counted failures | Measured suite elapsed seconds |
| --- | --- | --- | --- | --- |
| Pre-edit | 0 | 22 | 0 | 1.1903093000000808 |
| Post-edit | 0 | 22 | 0 | 1.1880982000002405 |

The suite reported `22 passed / 0 failed / 22 total` in both phases. Captured stdout is identical and captured stderr is identical and empty. Changes in reported values: none. Wrapper elapsed times are recorded separately from suite-reported values. JSON preserves the captured output using Unicode escapes. The plain-text transcripts replace only the existing banner dash with an ASCII hyphen to comply with the editorial rule.

### Consumption-floor assertion

The assertion read `h_n = max(H_N_FLOOR, float(state.h_n))` in metrics.py line 652, corresponding to pre-edit line 645. The read H_N_FLOOR is `0.01`. A returned `0.0` is therefore floored to `0.01`. With the read defaults lambda_n = 5.0 and epsilon = 1e-6 (lines 630 and 632), the line 687 denominator is `0.010001`, and the calculated weight is `499.9500049995001`, finite and nonzero-denominator. This was an assertion only. Empty-input and single-agent component checks also returned exactly `0.0`.

## T4. Requested mechanical prediction

The prior T1 record reports 2,395 of 11,600 steps-10-and-up baseline records with V = 0. As a mechanical consequence of this repair, those estimator outputs move from `1.0` to `0.0`: zero raw trace gives zero magnitude. This is a prediction from the expression and the previously recorded count, not a new baseline measurement. No sweep was run to quantify it, and no corrected published figure was derived.

## Execution and hashes

Machine: `YOTKOTEST`. Python: `3.14.3 (tags/v3.14.3:323c59a, Feb  3 2026, 16:04:56) [MSC v.1944 64 bit (AMD64)]`. NumPy: `2.4.4`. HEAD: `2044f50a8cf71874f259e74fd05ec495169b9ae4`.

The available CPU budget is the operator-stated 16 cores in normal mode, with a ceiling of 15 independent workers. Each validation phase used two parallel processes because two independent jobs were available: the component measurements and the regression suite. At most one process ran model steps inside the suite. No simulation sweep ran. All six numerical-library thread environment settings were 1 before NumPy import. The OpenBLAS runtime query `scipy_openblas_get_num_threads64_` verified one effective thread in each of the four validation processes. No operating-system core reservation was configured.

Bytecode writes were disabled. Guarded measurement, edit, and reporting processes reject writable file opens outside metrics.py, the authorized estimator_repair_ artifact paths, and the explicit os.devnull exemption. No out-of-scope writable-open attempt was recorded. The operator performs the containment diff; this report does not constitute a scope audit.

| metrics.py basis | Pre-edit SHA256 | Post-edit SHA256 |
| --- | --- | --- |
| Raw CRLF worktree bytes | 536a77fb5e45d6d167480ab7af6ea9f5a0e56b9927be0d09713400aa873fae63 | b87c7b7b511977b5858285241cf8dffed7319194a648ef432acc5d32525d483f |
| LF-normalized bytes | 667465e55e087c9be193184228f3470c866565fea53af90e3092bc9de275a8ab | 311e0239e539c2c32473536d5ae6eddf8c2fec88774c83148b4068acbe894fda |

Per-module SHA256 values below use LF-normalized bytes. Raw hashes and phase-specific module inventories are also recorded in [estimator_repair_validation.json](estimator_repair_validation.json). The test entry point is included explicitly because runpy removes its temporary module after returning.

| Module | Pre-edit SHA256, LF basis | Post-edit SHA256, LF basis |
| --- | --- | --- |
| simulation/agents.py | f0c1049370c001c9ac85191f47338ec4be8a197cc5a29332547b95d85a1168c3 | f0c1049370c001c9ac85191f47338ec4be8a197cc5a29332547b95d85a1168c3 |
| simulation/attack_adapter_v2.py | 5c303dc96d458eb2165416c925fa5ff526d89fdf3bb7fb5c02538bb96f7c41ee | 5c303dc96d458eb2165416c925fa5ff526d89fdf3bb7fb5c02538bb96f7c41ee |
| simulation/constants_v2_stage15.py | 9637604b34f472dd97035fb42db5b9ce77620560776f2bfe2c6e5188e5d9b5c7 | 9637604b34f472dd97035fb42db5b9ce77620560776f2bfe2c6e5188e5d9b5c7 |
| simulation/constants_v2_stage18.py | 121a7c1c9e86d585553a2975ae27143804757a0ef344305124fcc4c802b3285b | 121a7c1c9e86d585553a2975ae27143804757a0ef344305124fcc4c802b3285b |
| simulation/defection.py | 071abb31a84231386572cdfd901524647a5800f56d8117c89c44c5f75e24f97a | 071abb31a84231386572cdfd901524647a5800f56d8117c89c44c5f75e24f97a |
| simulation/diagnostics/estimator_repair_harness.py | f4164788946b1b0eb4b1e7a74b367196467590dc9db75692469c136996ede711 | f4164788946b1b0eb4b1e7a74b367196467590dc9db75692469c136996ede711 |
| simulation/metrics.py | 667465e55e087c9be193184228f3470c866565fea53af90e3092bc9de275a8ab | 311e0239e539c2c32473536d5ae6eddf8c2fec88774c83148b4068acbe894fda |
| simulation/model.py | 0a42a62268857c25c4bc99fa2162bfeb74c444bfa1f4fef6705a3a7e618d76b7 | 0a42a62268857c25c4bc99fa2162bfeb74c444bfa1f4fef6705a3a7e618d76b7 |
| simulation/test_refactor_1x.py | d4f52bd9e8c828c007fa569e2202f0c31a8fdbe367711d5160630387f66feeac | d4f52bd9e8c828c007fa569e2202f0c31a8fdbe367711d5160630387f66feeac |

## Artifact record

[estimator_repair_manifest.json](estimator_repair_manifest.json) enumerates every current estimator_repair_ output, including the retained historical halt record. Hashes use SHA256 over CRLF-to-LF normalized bytes, without normalizing any file in place. CSV row counts are counted with csv.DictReader excluding the header; non-CSV counts are null. The manifest self-entry has a null hash to avoid self-reference; its final LF-normalized digest is emitted separately.

The harness supports `pre`, `post`, `suite-pre`, and `suite-post`. Pre-edit measurements refer to the pinned pre-edit source; the pre command checks that raw source pin before execution. Current complete status and validation results supersede the prior halted reports. No measurement anomaly occurred in T1 through T3.
