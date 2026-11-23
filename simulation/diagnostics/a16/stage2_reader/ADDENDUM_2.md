# Addendum 2 to the stage 2 reader specification (2026-11-21)

**Applies to** `STAGE2_READER_SPEC_DRAFT.md` (`3ac0f425…5822`) as amended by `ADDENDUM_1.md` (`f1a26843…f103`). Where this addendum differs from either, it governs.

**Source:** the interpreter's repairs on the final check, `spec_checks\final_check\REPORT.md`, verdict NOT CLEAN. Section A2.n answers that report's finding n. I confirmed the code facts below at `4dcc18c2` before writing them, except where a statement is marked as the final check's measurement.

## A2.1 The nominal comparator's admission: a third G6 branch (amends A1.3, D:358-365, D:326-329, A1.2)

**The finding:** the nominal family was published under A14. Its binding scope is `A10_nominal_after_A14` (`admission_a13.py:10`; `validation_extension_a14.py:639`), which neither A1.3 branch matches.

**The branch,** for the family `nominal` only. `A10_nominal_after_A14` on any other family refuses.
1. **The binding:** `manifest.a13_admission.scope == "A10_nominal_after_A14"`, with no `a16` key in the binding.
2. **The A14 round's admission record,** `<stem>.a14_round.admission.json` beside the nominal table (`validation_extension_a14.py:637`):
   - its seal verifies, and `outcome == "passed"`;
   - `primary_rows`, `cap` and `residual_count` agree with the loaded table, and `admitted_set_sha256` equals the manifest binding's;
   - its `plan_hash` equals the validation receipt's `a14_round.plan_hash` (`:718`), not the receipt's top-level `plan_hash`;
   - its file sha256 equals `a14_round.admission_record_sha256` (`:719`; the file hash is returned at `:662`).
3. **The preserved A13 round refusal,** `<stem>.a13_round.admission.json` (`history_a14.py:27-28`):
   - its file sha256 equals both the receipt's `refusals.a13_admission_record_sha256` (`validation_extension_a14.py:723`) and `a13_round.admission_record_sha256` (`:717`). Both are file hashes (`history_a14.py:344`);
   - it reads `outcome: "refused"`.
4. **Primary rows:** 19,500, with cap 19. That is `build_jobs("nominal")` at `4dcc18c2`, as the final check measured. The reader asserts equality with the loaded table, and with that literal in registered mode.
5. **The case:** nominal is case 1 (`REQUIREMENTS_DIGEST.md:92` records five residual rows). Its case is still decided at run time from the verified manifest (D:411).
6. **Inputs:** `comparator.family` in `inputs.json` gains `admission_check` (the A14 round's admission record) and `a13_round_admission` (the preserved refusal). The fifth inventory binds both, by file hash and seal.
7. **Fixtures:** the fixture comparator family carries this scope. F14 gains variants:
   - (e) the A14 admission record's `plan_hash` replaced by the receipt's top-level `plan_hash`;
   - (f) the A13 refusal's bytes altered;
   - (g) the scope `A10_nominal_after_A14` on an arm family.

   Each must refuse.

## A2.2 Fixture roots (amends A1.1 items 1, 4 and 7)

`atomic_json` refuses any path outside the running code's `simulation/v3` (`artifacts.py:129-130`), as the final check measured. The native runner reads tables at `SIMULATION / config["tables_path"]` (`production_runner.py:250`, `:265`). So:

- **Each fixture root is a standalone copy of `simulation/`,** code plus fixture files, outside every git checkout of the repository.
  - The generator runs the native code from inside it, so native writers and runners resolve their paths there.
  - Fixture tables sit at the `STAGE2_PATHS` relative strings under the copy's `simulation/`, as chain items 3 and 4 (D:273-274) require.
  - `code_identity()` run from the copy equals `93a453b2…`. The generator asserts this before and after generating.
- **The reader never runs from a fixture root.** It runs from its own git checkout and takes the fixture root as `execution_simulation` (and `comparator.execution_simulation`). Its G0, `verify_registration` and `accepted_identities()` run in that checkout.
- **Replacing A1.1 item 4:** no fixture file is ever placed under any git checkout of the repository. The relative path strings are used only under a fixture root.
- **F7's twin** (A1.1 item 7) is a second fixture root, a copy of the first that differs only in the twin table's bytes.

## A2.3 Full-key fixture families, and the permitted fabrications (replaces A1.1 item 5)

- **No padding.** Every L2 fixture family is a full-key family: its row keys equal `tables_a10.expected_keys(tables_a10.build_jobs(family, <fixture calibration>), <fixture calibration>)` for the family it imitates. That makes 2,875 rows for sqrt- and crowding-shaped families, 625 for σ-shaped and 19,500 for nominal-shaped. Then:
  - the primary-row counts and caps of G6 (2, 2, 0, 0 and 19) hold in fixture mode as in registered mode;
  - case 2 condition 5 holds without exemption.
- **Row contents** come from the native estimator, run non-registered on short settings from the fixture root: `build_jobs(..., settings_override=<short>)`, then the native assembly.
- **Permitted fabrications.** Only the shape fields and records below may be written by hand. The fixture manifest names each one per family:
  1. the registered-shape manifest fields `fixture: false`, tag `v3_tables`, `complete_family: true` and `sensitivity_status: "passed"`;
  2. the A13 binding, built by `admission_a13.binding` or `checked_binding` over the rows after `add_ranking_flags`, as `table_validation_a4.py:835` does. Over unranked rows the loader refuses, as the final check measured;
  3. for a case 1 family, the admitted `not_estimable` row's status and its evidence fields: `reason`, `a4.base_screens_ok`, `a4.validated_support_size`, `a4.floor.passed`, support and `cell_tests` (`admission_a13.py:144-152`);
  4. the A4 validation receipt and the A10 receipt, schema-identical to what the native writers produce. The no-label receipt must equal what `finalize_no_label_receipt` would write;
  5. for a sqrt- or nominal-shaped family, an A5 label record covering every estimated FV row (`production_tables.py:188-200`), with the violations the fixture needs;
  6. the identity record, the admission check record or records, the A13 and A14 or A16 round records a fixture needs, the reading-input inventories, the authorized-hash document, and `verified_output_hashes.json` (A1.11).
- **If a full-key family proves infeasible,** the generator stops and reports. Padding comes back only by a later addendum.

## A2.4 The mode-dependent gate terms, complete (replaces A1.1 item 6)

Fixture runs use default `n_agents` and 500 steps. A1.14's 60-step minimum is met. The terms below, and only these, differ between fixture mode and registered mode. Each builder's report lists every `if fixture` branch, and the list must match this one.

| # | Term | Registered mode | Fixture mode |
|---:|---|---|---|
| 1 | G2 arm job equality | `spec.jobs == stage2_runs(STAGE2_PATHS)[family]` | Not applied. The spec's jobs equal the fixture manifest's job list |
| 2 | Seeds per cell | 100, 400, 75 | The fixture manifest's counts, the same for every cell of a side |
| 3 | Comparator jobs and counts | `paired_runs(*STAGE2_PATHS["nominal"])`, 24,900 jobs, 6,225 contributing | The fixture manifest's list and counts |
| 4 | Calibration pins | The three frozen calibrations' file hashes and seals | The fixture calibration, whose seal differs from all three (A2.5) |
| 5 | Model keys | No `n_agents`, `carrying_capacity` or `rollout_steps` | `n_agents` allowed only on F8's zero-agent run |
| 6 | Committed-bytes tests (identity records, seed registry) | Bytes equal `git show HEAD:` in the reader's checkout | Bytes bound by the fixture authorized-hash document |
| 7 | Spec registration and seed-registry digest (A1.6, A1.12) | Applied | Not applied. Fixture specs are non-registered and carry neither |
| 8 | `path_map` | Refused | Allowed |
| 9 | Inventory inputs | The arm and comparator inventories bound by the operator-authorized document | Fixture inventories bound by the fixture authorized-hash document |

Everything else runs the same code in both modes. That includes G5's structure checks at 500 steps, the filters of D:133-137, G6, G7 and every incidence rule.

## A2.5 Keeping fixtures distinguishable (adds to A1.1)

- Every fixture table's `manifest.calibration_hash` differs from the seals of the three frozen calibrations. A native registered load of a fixture table with a frozen calibration then fails at the calibration check (`production_tables.py:91`).
- If any native check in G6 or G7 pins the frozen calibration itself, so that a fixture calibration cannot pass, the generator reports it. That check then becomes a listed mode term by a later addendum.
- `reading.json` and `SEAL.json` gain `mode`: `"registered"` or `"fixture"`. In fixture mode the reader also records the fixture list hash.

## A2.6 A16 admission, completed (amends A1.3)

- **Names:** "the round record" in A1.3 means the round's **admission record**, `<stem>.a16_round<q>.admission.json` (`validation_extension_a16.py:441-442`; its `outcome` is written at `:1285`). The **round record** proper is `<stem>.a16_round<q>.json` (`:437-438`). `inputs.json` names both (D:318-319).
- **Carried over to the round's admission record:** the seal test, and the agreement of `primary_rows`, `cap` and `residual_count` with the loaded table.
- **Added checks:**
  - the A16 family record has `published_round == q` and `terminal` null;
  - the original admission record has scope `validation_launched_under_A13` and `plan_hash` equal to the validation receipt's `plan_hash` (`history_a16.py:197-198`);
  - for q = 2, round 1's admission record reads `outcome: "refused"`;
  - `a16_rounds.r<q>.plan_hash == manifest.a13_admission.a16.plan_hash`;
  - the round's public record's file sha256 equals `a16_rounds.r<q>.public_file_sha256`.

## A2.7 A5 disclosures, defined (amends A1.5)

- **Looked-up rows** means the configured set, which needs no output value. For a job, it is every rule of its family at its (rr, alpha) and each capability in `study.capabilities(successor_capability)`, under its instrument and crowding, as stage 1 reader B computed it (rB/`nominal.py:311-327`).
- **Fields from the label record** (`table_labels_a5.py:720-725`):
  - the row is its `row_key`;
  - violated cells are `violation`, which equals `violation_count` and `len(violations)`;
  - total exposure is `violation_exposure_total`, which counts a null exposure as 0.0.
- **Key presence:** every quantity in both components carries `disclosure.<quantity>`. A side whose family has no A5 labels (crowding and both σ families) contributes no rows. A quantity with no violation row on any side has `{disclosure_rows: [], claims_conditional_on_violations: false}`. The words "in the stage 1 form" are withdrawn: stage 1 wrote a count, and this is the list A5 requires.

## A2.8 Warning filters (amends A1.4)

- `warnings.simplefilter("ignore")` is set at process start, again after the last import, and again inside every `warnings.catch_warnings()` block that wraps a helper call. A filter an imported module adds at import otherwise outranks the first one; the final check measured NumPy's `RankWarning` filter doing this.
- Helpers are called only in the main thread. Parse workers, if the operator allows them (draft question 8), never call a statistical helper, and they start with the same filters.

## A2.9 Not-run, both run-root patterns (amends A1.7)

- **The contradiction check** tests both `v3/runs/a10_stage2/runs/<family>/*/records/` and `v3/runs/a10_stage2/<family>/runs_run/*/records/`. The second is the pattern of sqrt's failed attempt (D:205).
- **The item 42 closeout record** for a not-run arm states that no other run root of the family exists.
- **An arm that entered A16 and holds neither a terminal latch nor a publication has no not-run form.** The reader refuses it. The operator latches it through the native procedure before the reading.

## A2.10 The new inventories' schema, and the comparator pin (amends A1.2, A1.6, and A1.16 item 9)

- **Schema.** The fifth (comparator) inventory and the two σ inventories use the schema string `stage2-reading-input-inventory-2`. Its key names are those of INV-C (`stage2-crowding-reading-input-inventory-1`), plus these keys under `published_files_and_inputs`, each `{path, sha256, seal}` or null:
  - `admission_check` (the binding admission record);
  - `a13_round_admission` (nominal only);
  - `a16_family_record` and `a16_round_admission_records` (a list), when A16 was used;
  - `labels` (sqrt and nominal only).

  The comparator inventory also records `registration_pin` and the job path strings.
- **The reader's inventory adapter** handles exactly three schemas: INV-S's, INV-C's and this one. The reader is frozen before the three new inventories exist. They are made to conform to this key list, and the confirming checks of each inventory test that they do.
- **The comparator's pin:** besides A1.6, its commit equals `artifacts.A14_COMMIT`, `17f17ef9cee4b18d70f043a1e097359cd6642693` (`artifacts.py:373`).

## A2.11 Specification identity (amends D:482 and D:531)

The specification is a set of documents: the draft and each addendum, in order.
- `reading.json` and `SEAL.json` record `specification_set`, the ordered list of `{name, sha256}`, and its `digest`. They replace the single `spec_sha256`.
- The freeze record lists the same.
- The documents are not consolidated before freeze. A consolidation would be a new document needing its own check.

## A2.12 Smaller corrections

- **The environment:** fixtures and the build's tests run in the registered environment. That is the phaseb environment of X2-1: Python 3.13 with its NumPy. On WS-1 that means the WSL phaseb environment, bit-identical to X2-1. F3's counts (53 and 60) are reconfirmed there.
- **F3's pins** (A1.9), as the final check measured, for both wrappers: estimate `-0.0001023460872303511`, arm boundary `0.06572413793103449`, comparator boundary `0.06582648401826484`, and for the A6 wrapper `interval: null`. They are reconfirmed in the registered environment.
- **F8** must be shown under the A10 instrument. If a zero-agent run is not possible there, the generator reports it and F8 is replaced by a later addendum.
- **Citations:** the runbook writer is `A10_RUN_ON_X2.md:449-451`. The binding condition is `table_validation_a4.py:831-838`.
- **Overstatements withdrawn:**
  - Addendum 1's header claim that every code fact was confirmed did not cover A1.1's feasibility, which was not tested.
  - "Repaired" for F-1 and F-3 in the repair note means repaired for the cases the second check named.
  - F-6's title: an old pin without `instrument` still fails at `artifacts.py:456` when the working note differs. Only a different commit with identical note bytes would pass. The repair stands.
