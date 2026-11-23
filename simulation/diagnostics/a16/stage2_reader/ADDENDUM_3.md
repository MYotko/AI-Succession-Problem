# Addendum 3 to the stage 2 reader specification (2026-11-21)

**Applies to** `STAGE2_READER_SPEC_DRAFT.md` (`3ac0f425…5822`) as amended by `ADDENDUM_1.md` (`f1a26843…f103`) and `ADDENDUM_2.md` (`74f7c0a6…2edc`). Where it differs from any of them, it governs.

**Source:** the interpreter's repairs on the confirming check, `spec_checks\final_check2\REPORT.md`, verdict NOT CLEAN in the fixture design only. A3.n answers its finding n. The code facts below were confirmed at `4dcc18c2` by the interpreter, or are labelled as the confirming check's measurements.

**Scope:** fixture design and the nominal branch's completeness. The confirming check found the registered-mode rules faithful: A2.1, A2.6 to A2.11 and A2.12's corrections. They are unchanged here except where named.

## A3.1 Fixture calibration: the frozen bytes only (replaces A2.5's first bullet and A2.4 row 4; amends A2.3)

- **The finding.** Under an A10 instrument, native code refuses any calibration other than the frozen parent or a pinned σ variant, in non-registered mode too. The refusing paths are `Context.build` (`context.py:37-39`) through `validate_calibration`, `calibration.load_calibration`, and `production_runner.execute`. The confirming check measured all three refusing.
- **Every fixture family uses the frozen parent calibration's bytes,** placed at its `STAGE2_PATHS[family][0]` string under the fixture root. For nominal, sqrt and crowding that is the parent's own path. For the σ shapes, the parent's bytes sit at the σ path string. The native code accepts them as the unchanged calibration (the confirming check's reading).
- **The σ calibration pin is a mode term** (A3.5 row 4):
  - **Registered mode:** the two pinned variant files, checked against `a10_constants.json` and through `load_calibration`'s `_validate_a10_variant`.
  - **Fixture mode:** the parent's bytes at the σ path.

  The variant-pin path therefore first runs on real files at `verify` (A1.16 decision 3). That is a stated, value-free exposure.
- **Withdrawn:** A2.5's first bullet, that fixture `calibration_hash` differs from the frozen seals. Also withdrawn is the draft's "non-frozen calibration" allowance at D:333.
- **The leak protections that replace it:**
  1. **Fixture roots sit outside every git checkout** (A2.2). A registered native run cannot start there, because `verify_registration` shells to git (`artifacts.py:439-443`). That is an inference, not run.
  2. **A marker key.** Every fixture table's manifest carries `reader_fixture: true`.
     - In registered mode the reader refuses any table that carries the key.
     - In fixture mode it requires the key (A3.5 row 10).
     - The native loader is expected to ignore the key, which the confirming check inferred but did not run. The fixture generator's pilot (A3.9) confirms that `write_tables`, the A13 binding, `ProductionTables(..., registered=True)` and `require_a10` all accept it. If one does not, the pilot reports it, and the marker moves to the fixture authorized-hash document alone.
  3. **The `mode` field** of A2.5's third bullet stays.

## A3.2 Row contents: cheap native rows, statuses set by hand (replaces A2.3's "Row contents" bullet)

- **The finding.** Native estimator rows on short settings mostly fail the native screens: 0, 1 and 2 of 7 estimated at three short settings. Seven of 7 passed only at about 25 s per job. The status comes from `offline_estimator.py:155-161` and `:178`, and an A10 trace of 30 steps or fewer is never estimable (`:119`). These are the confirming check's measurements and reading.
- **The rule (option (b)).**
  - The generator runs the native estimator, non-registered, from the fixture root. It uses the cheapest setting that gives every row continuation entries, and a trace longer than 30 steps. It records the setting.
  - It then sets by hand, as listed fabrications (A3.3), the status of every row to what the fixture needs. That is `estimated` everywhere, except the admitted `not_estimable` row of a case 1 family and the deliberately missing or unestimable rows of F14(c) and F15. It also sets every field that status entails.
  - The fixture manifest lists each row whose native status was changed, with the native status and the screens that failed.
- **The reason.** Fixture table values are synthetic. The reader is tested on structure, bindings, gates and incidence, never on table quality. The native runs need rows with continuation entries, and the cheap setting gives them.
- **Budget estimate.** About 1,495 sqrt- or crowding-shape jobs and 655 per σ shape, at the cheap setting of about 0.2 to 0.8 s each (the confirming check's timings), plus the nominal shape's 2,835 jobs. That is about an hour of CPU in all, untimed for nominal.

## A3.3 Fabrications: a naming rule, and the minimum list (replaces A2.3's "Only the shape fields" sentence and list)

- **The rule.** Anything written by hand rather than by a native writer is named in the fixture manifest per file and per field, with a reason. The list below is the minimum, not a ceiling. A builder or checker who finds a hand-written field the manifest does not name treats it as a defect.
- **The minimum list:**
  1. the registered-shape manifest fields: `fixture: false`, tag `v3_tables`, `complete_family: true`, `sensitivity_status: "passed"`, and `reader_fixture: true` (A3.1);
  2. row statuses, and the fields each status entails (A3.2);
  3. `fv_label: "asymptotic, not certified"` on every estimated FV row of a no-label family. Only A4 writes it (`table_validation_a4.py:652`), and `_require_no_label_receipt` refuses without it (`production_tables.py:231-233`);
  4. the A13 binding, built by `admission_a13.binding` or `checked_binding` over the rows after `add_ranking_flags` (A2.3 item 2);
  5. for a case 1 family, the admitted row's evidence fields (A2.3 item 3), plus the three conditions A2.3 omitted. The row is not the balanced rule. There is one admitted row per lookup context. `sensitivity.passed` is not false (`admission_a13.py:139-143`, `:149`);
  6. the cell-results sidecar, which the identity record and the validation receipt bind;
  7. the A4 validation receipt and the A10 receipt, strict or no-label, schema-identical to the native writers' output;
  8. for sqrt- and nominal-shaped families, the A5 label record (A2.3 item 5);
  9. the identity record;
  10. the fixture run specs and each root's `manifest.json`, carrying `a10_family`, `a10_stage`, `a10_labels_policy` and `a10_family_paths`. The only native writer of those fields, `stage2_run_specs`, is registered-only (`tables_a10.py:644-689`). The comparator-shaped spec is fabricated likewise;
  11. for the nominal shape, `manifest.a14` (as `validation_extension_a14.py:701` writes it). For F13(e) and F14(d), `manifest.a16` and the per-row A16 markers (`admission_a13.py:81-109`);
  12. every admission check record, every round record (A13, A14, A16), every round's admission record and public record, and the A16 family record;
  13. the not-run closeout record of F13;
  14. every deliberate tamper of F10 to F15, named as a tamper;
  15. the reading-input inventories, the fixture authorized-hash document, and `verified_output_hashes.json`.

## A3.4 The nominal branch, completed (amends A2.1)

- **Added checks on the A14 publication,** needing no new file:
  - `manifest.a14.plan_hash == a14_round.plan_hash ==` the A14 admission record's `plan_hash`;
  - `manifest.a14.a13_plan_hash == a13_round.plan_hash ==` the A13 refusal record's `plan_hash` (`history_a14.py:216`);
  - `manifest.a14.original_plan_hash == ` the receipt's `plan_hash` (`validation_extension_a14.py:602`, `:724`).
- **Two more inputs,** bound by hash and added to `comparator.family` and the fifth inventory:
  - the A14 round record `<stem>.a14_round.json` (`validation_extension_a14.py:205-209`);
  - the A14 public record, whose file hash must equal `a14_round.public_file_sha256` (`:718`).
- **A pinned constant in registered mode:** the A13 refusal's file sha256 equals `history_a14.ADMISSION_HASH`, `87f8b2453e04b178a4f2dcd40c07ae41b9ab06a350a70d5b57e834aa8e5c6dd7` (`history_a14.py:16`, `:219`). In fixture mode this is a mode term (A3.5 row 11).
- **What `family.nominal.admission` holds:**
  - `scope`: `A10_nominal_after_A14`;
  - `primary_rows`, `cap`, `residual_count` and `admitted_rows`, from the A14 admission record and the loaded table;
  - `rounds_used`: 2, the A13 round and the A14 round;
  - `admission_record_sha256`: the A14 admission record's file sha256.
- **`family_error.nominal.*`** holds exactly the fields the A14 admission record carries among `E`, `E2`, `P`, `M`, `alpha`, `tests_round1`, `tests_round2` and `extension_error_bound` (`validation_extension_a14.py:643-646`), copied. It carries no statement string. The A16 sentence of D:519 is for A16 families only.
- **A2.1 item 4:** the words "and with that literal in registered mode" are deleted. The nominal count of 19,500 rows, cap 19, holds in both modes, because fixture families are full-key.

## A3.5 The mode-term table, complete (replaces A2.4's table; its closing sentence stands)

| # | Term | Registered mode | Fixture mode |
|---:|---|---|---|
| 1 | G2 arm jobs and counts | `spec.jobs == stage2_runs(STAGE2_PATHS)[family]`; `STAGE2_RUN_COUNTS` | The fixture manifest's job list and count |
| 2 | Seeds per cell | 100, 400, 75 | The fixture manifest's counts, the same for every cell of a side |
| 3 | Comparator jobs and counts | `paired_runs(*STAGE2_PATHS["nominal"])`, 24,900 jobs, 6,225 contributing | The fixture manifest's list and counts |
| 4 | σ calibration | The pinned variant files, checked by hash and `_validate_a10_variant` | The parent's bytes at the σ path (A3.1) |
| 5 | Model keys | No `n_agents`, `carrying_capacity` or `rollout_steps` | `n_agents` allowed only on F8's zero-agent run |
| 6 | Committed-bytes tests (identity records, seed registry) | Bytes equal `git show HEAD:` in the reader's checkout | Bytes bound by the fixture authorized-hash document |
| 7 | Pins | Spec registration equals the pin (A1.6); seed-registry digest (A1.12); comparator pin `historical=True` and equal to `A14_COMMIT` (A1.6, A2.10) | Not applied. Fixture specs are non-registered and carry none |
| 8 | `path_map` | Refused | Allowed |
| 9 | Authorized inputs | Arm and comparator inventories and not-run evidence, bound by the operator-authorized document | The same items, bound by the fixture authorized-hash document |
| 10 | Fixture marker | A table carrying `reader_fixture` refuses | Every table must carry `reader_fixture: true` |
| 11 | A13 refusal constant | File hash equals `history_a14.ADMISSION_HASH` | Bound by the fixture authorized-hash document |
| 12 | Outputs | `mode: "registered"` | `mode: "fixture"`, plus the fixture list hash |

**Not mode terms, stated so:**
- `fixture_tables` is false in both modes and is tested in both (D:356).
- 500 steps and default `n_agents` apply in both modes. The draft's "shortened horizons" allowance at D:333 is withdrawn.
- G5, G6's literal counts and case 2 condition 5 are mode-independent with full-key families, as the confirming check found for check 4.

## A3.6 Inventory keys, without overlap (replaces A2.10's key list)

- **Schema `stage2-reading-input-inventory-2`** keeps every key name of INV-C. That includes `a13_admission` for the original `validation_run/a13_admission_check.json`. Entries take INV-C's form, `{bytes, path, present, seal, seal_check, sha256}`.
- **Keys added under `published_files_and_inputs`,** each in that form, or with `present: false` where the family has none:
  - `labels` (sqrt and nominal; INV-S's key name);
  - `a13_round_record` and `a13_round_admission` (nominal);
  - `a14_round_record`, `a14_round_admission` and `a14_public_record` (nominal);
  - `a16_family_record`, `a16_round_records`, `a16_round_admission_records` and `a16_public_records` (an A16 family; the last three are lists, ordered by round).
- **Withdrawn:** A2.10's `admission_check` key.
- **The comparator inventory** also records `registration_pin` and the job path strings, as before.

## A3.7 Smaller corrections

- **Disclosures (A2.7):** "every quantity" means every key of `contributing_runs.json` `quantities`. A not-run arm's quantities have an empty arm side, so their disclosure is computed from the comparator side alone.
- **Specification identity (A2.11):** `digest` is `v3.artifacts.digest` over the ordered list of `{name, sha256}`. The authorized-hash document (D:265) lists the specification set, not a single sha256. A1.16 decision 10 reads the same.
- **Citation (A2.2):** `production_runner.py:250` is the calibration load and `:265` the table load.
- **Environment (A2.12):** "bit-identical to X2-1" for WS-1's WSL phaseb environment is the interpreter's statement. It rests on the 2026-09-30 comparison of that environment with the X2, 19 of 19 and 18 of 18. The generator and each builder record their Python and NumPy versions, and check them against X2-1's phaseb environment (the runbook names Python 3.13.12, `A10_RUN_ON_X2.md:127`). A difference is reported, not worked around.
- **Identity (A2.2):** in a standalone copy, `accepted_identities()` returns the running identity only, since the A11 records cannot be checked against git there. Every fixture family, the comparator shape included, is therefore produced at `93a453b2…`.
- **F8:** a zero-agent run under the A10 instrument constructs and runs, with no allocation step, no yield event and final population 0. The confirming check measured that with the built-in fixture tables. The pilot repeats it against a registered-shaped table.

## A3.8 Build plan time (replaces A1.15's build-time line)

- **Fixture generation:**
  - Cheap native estimation, about an hour of CPU (A3.2).
  - Fixture runs at 500 steps and default `n_agents`, measured at about 86 s each on WS-1 (the confirming check). A layout with every registered cell at two seeds per cell is about 284 runs, about 7 CPU-hours per fixture root.
  - With the twin root and the variants, about 15 to 25 CPU-hours in all. That is about 1 to 2 hours of wall time at WS-1's normal cap of 15 workers, one library thread each.
  - Generation, including the pilot, comes to about one and a half working days elapsed. That is a budget estimate, resting on those timings and the stage 1 elapsed-time spans.
- **The whole build** comes to about five and a half working days to the freeze, a budget estimate.

## A3.9 How this addendum is checked

The document-check rounds have converged on the registered-mode contract. The fixture design is now best tested by building it. So the fixture generator's first deliverable is a **pilot**, run on WS-1, non-registered:
- one sqrt-shaped case 1 family;
- one σ-shaped case 2 family;
- the nominal-shaped family under the A14 scope;
- a few runs against each.

It shows for each family:
- that `write_tables`, the binding, `ProductionTables(..., registered=True)` and `require_a10` accept the table, with the marker;
- that native runs against it complete;
- that the recorder is on for the case 1 family and off for the case 2 family;
- that F8's zero-agent run works against the registered-shaped table.

Every hand-written field is listed. The pilot report gets a separate second check before the full generation.
