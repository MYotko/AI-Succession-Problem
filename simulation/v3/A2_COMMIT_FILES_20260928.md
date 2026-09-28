# A2+A3 combined commit file list, 2026-09-28

Prepared only. No commit was made. D24 adopts A3 and settles A2's censored
cap* rules. Commit the combined package before registered rerun dispatch
or output review. Use `A2_RUN_ON_X2.md` for repair and launch. Do not
resume the old wrapper into its A1 rerun step. No registered rerun
manifest, job or output existed while the amendments were written.

Include these code, tests, protocol, policy and launch files explicitly:

- simulation/v3/gates.py
- simulation/v3/recording.py
- simulation/v3/recording_validation.py
- simulation/v3/table_compatibility.py
- simulation/v3/table_compatibility_A2.json
- simulation/v3/table_compatibility_a3.py
- simulation/v3/table_compatibility_A3.json
- simulation/v3/artifacts.py
- simulation/v3/production_runner.py
- simulation/v3/service.py
- simulation/v3/production_tables.py
- simulation/v3/integration.py
- simulation/v3/d23_validation.py
- simulation/v3/a1_screen_diagnosis.py
- simulation/v3/table_repair_a3.py
- simulation/v3/A1_TABLE_DIAGNOSIS_20260928.json
- simulation/v3/A3_REVIEW_20260928.md
- simulation/test_v3_a1_diagnosis.py
- simulation/test_v3_a2_review.py
- simulation/test_v3_d24.py
- simulation/test_v3_second_review.py
- simulation/test_v3_paths.py
- simulation/test_v3_legacy_scope.py
- simulation/test_v3_b2_estimators.py
- simulation/test_v3_b2_pilot.py
- simulation/test_v3_b2_runner.py
- simulation/test_v3_table_amendment.py
- simulation/test_v3_gates.py
- simulation/test_v3_recording.py
- simulation/test_v3_unpublished_bins.py
- simulation/test_v3_d23.py
- simulation/diagnostics/v3_rerun_design_note.md
- simulation/diagnostics/v3_instrument_implementation_note.md
- simulation/v3/A2_RUN_ON_X2.md
- simulation/v3/A2_COMMIT_FILES_20260928.md

All root v3 Python modules scanned by code_identity are included, either
already tracked or explicitly listed above. A3 code is adopted, not an
excluded diagnostic extra. Both compatibility JSON policies are scanned
and subject to the committed-and-clean registration check. No omitted
local helper contributes to the final identity.

Include the unchanged authorized calibration and historical gate records:

- simulation/v3/runs/registered/v3_rerun_calibration.json
- simulation/v3/runs/v3_rerun_gates.json
- simulation/v3/runs/v3_rerun_gates.md
- simulation/v3/runs/w7_validation_20260928.json

The calibration file SHA256 is
fd86358a39e3b643fb9adc4e81a2372915ca50a1866e9b0e330a874b41746e01.

Retain these historical compact records under
`simulation/v3/runs/a2_recording_validation/`:

- noninterference.json
- cost_projection.json
- coverage_diagnostics.json
- before_validation.json
- final_validation.json
- archive_manifest.json
- a2_validation_records_20260928.zip
- gates/v3_rerun_gates.json
- gates/v3_rerun_gates.md

The archive supplies the exact original sparse probe and baseline inputs.
Tests can read the probe from this archive in a clean checkout.

Retain these historical compact records under
`simulation/v3/runs/a2_d23_validation/final/`:

- inputs.json
- spec.json
- comparison.json
- validation.json
- archive_manifest.json
- d23_validation_records_20260928.zip
- gates/v3_rerun_gates.json
- gates/v3_rerun_gates.md

Retain these historical compact records under
`simulation/v3/runs/a2_review_validation/final/`:

- inputs.json
- spec.json
- comparison.json
- validation.json
- compatibility_validation.json
- commit_source_files.json
- archive_manifest.json
- a2_review_validation_records_20260928.zip
- before/v3_rerun_gates.json
- before/v3_rerun_gates.md
- gates/v3_rerun_gates.json
- gates/v3_rerun_gates.md

Retain the original unpinned A3 selection evidence under
`simulation/v3/runs/a1_screen_diagnosis/`:

- A3_REVIEW_ONLY_manifest.json
- validation.json

The first file is also used by the clean-checkout D24 policy test. It is
historical and must never be launched. The expanded 62 MB audit is
reproducible from the read-only source records and is not a commit input.

Retain the historical D24 records under
`simulation/v3/runs/d24_validation/`:

- A3_REVIEW_ONLY_manifest.json
- commit_source_files.json
- compatibility_validation.json
- validation.json
- archive_manifest.json
- d24_validation_records_20260928.zip
- full_suite.txt
- before/v3_rerun_gates.json
- before/v3_rerun_gates.md
- recording/inputs.json
- recording/spec.json
- recording/comparison.json
- recording/gates/v3_rerun_gates.json
- recording/gates/v3_rerun_gates.md

The D24 archive retains exact paired outputs, real-runner outputs, durable
records, configuration measurements, evidence index and state/RNG audits.
Its manifest records each archived hash. All rerun outputs in these
archives are explicitly non-registered validation artifacts. The D24
review manifest is unpinned, records the adopted order and first-failure
option, and cannot launch. Regenerate production manifests from the
approved combined commit, with the actual pin and paths.

Do not stage whole directories. Exclude loose archive duplicates,
disposable baseline and clean-source copies, `_pytest_v3`, `_gates_*`,
`_recording_*`, `_d23_*`, `_a1_*`, locks, leases, expanded audits and the
pre-existing pilot zip. The pilot manifest must match HEAD. Do not stage
anything under bootstrap_gate_validator or outside the authorized scope.

The historical D24 report and source identity are recorded in
implementation-note section 22 and
`simulation/v3/runs/d24_validation/validation.json`.
Earlier validation identities in archived reports remain historical.
The table repair has not run; no scientific clearance is promised.

Historical D24 source identity:
`6c87072644b26ff8a545144771f91a4dbe598623dce7c0586a5390dbda331942`.
Full suite: 376 passed, three existing expected failures. Clean-source
check: 137 passed, followed by all 20 final D24 cases. All six before
gates pass. The final six observer comparisons match scientific bytes,
states and original draws; G4.3 passes 120 periods and 2,900 actions with
zero violations. The D24 archive contains 80 verified files, 7,218,219
bytes, SHA256 4114503ef92dcc095b9dc5756f845c0dbcd2155aa0d51d74b8440bb7a29758d6.


Include the final second-review records under
`simulation/v3/runs/second_review_validation/`:

- A3_REVIEW_ONLY_manifest.json
- commit_source_files.json
- compatibility_validation.json
- storage_cost.json
- validation.json
- archive_manifest.json
- second_review_validation_records_20260928.zip
- full_suite.txt
- before/v3_rerun_gates.json
- before/v3_rerun_gates.md
- recording/inputs.json
- recording/spec.json
- recording/comparison.json
- recording/gates/v3_rerun_gates.json
- recording/gates/v3_rerun_gates.md

The final identity is
`f03021f88c53e0331d6d825f26663980f77a98d1e15c258f386acfc2c1f7b629`,
covering the exact 76 files listed in commit_source_files.json. Tests are
excluded from code_identity but all changed and new tests are listed above.
The full suite passed 391 tests with three existing expected failures;
the six before gates and all six recording comparisons passed. G4.3
checked 3,000 living-step bounds and 2,900 actions with zero violations.
Section 23 records the new universal-cohort storage cost and the limited
G3.2 sample. Do not stage loose duplicates of the archive members.

Final validation.json SHA256:
`0fed15f63bb936cd5289f875e4f3fe41894181473d63ff27210e516a58edf9ae`.
The archive has 81 verified files, 7,875,931 bytes, SHA256
`26eb3625255b17d3c0874a0219a139edd95168b511b8e130b7370145b010ac18`.
No A3 estimate or registered rerun was executed. The 67 replacement IDs,
seeds and exact calibration argument in the committed compatibility
policy must match production preparation. The policy-scoped failure
latch is checked across run roots before service/configuration work and
by publication. A2 and A3 remain uncommitted for operator review.
