# Addendum 1 to the stage 2 reader specification draft (2026-11-21)

**Applies to** `STAGE2_READER_SPEC_DRAFT.md`, sha256 `3ac0f425cd2b1f27c31a6cf0b757a7ba9e62515ab128a85049f3c5a33d835822`. Where this addendum and the draft disagree, this addendum governs. Draft lines are cited `D:n`.

**Source:** the interpreter's repair round on the separate second check (`spec_checks\second_check\REPORT.md`). Every code fact below was confirmed at `4dcc18c2` by the interpreter before it was written here, unless it is marked otherwise. Section numbers A1.n follow the second check's findings F-n. A1.16 records the interpreter's decisions on the draft's open questions.

## A1.1 L2 fixtures are registered-shaped (replaces D:566-567; amends F6, F7, F9, F10, F11, F13 to F15)

**The problem:** `require_production` rejects a table whose `fixture` is true, whose tag is not `v3_tables`, or whose `complete_family` is false (`production_tables.py:121-124`). A non-registered publication writes no `a13_admission` binding (`table_validation_a4.py:831-841`). `admission_a13.verify` caps admitted rows at `len(rows) // 1000` (`admission_a13.py:129`). So a toy family made by the non-registered path would refuse at G6, and its registered branch would first run at item 43.

**The rule:**
1. **Shape.** Every L2 fixture family table is written by `write_tables` at the running identity with `fixture: false`, tag `v3_tables`, `complete_family: true`, `sensitivity_status: "passed"`, and a real `a13_admission` binding built by `admission_a13.binding` (or `checked_binding`) over the fixture's rows.
2. **One code path.** G6 and G7 run the same code path in fixture mode and registered mode: `ProductionTables(..., registered=True)` and `require_a10`. No fixture-only branch exists in G6 or G7.
3. **Mode.** It is still decided by the specs' `registered` flags (D:333). L2 fixture specs are non-registered. A registered-shaped table under a non-registered spec is the fixture case, and only that case.
4. **Location.** Fixture tables live only under the fixture root, which is outside the execution checkout and every registered path. The fixture list hash in the freeze record binds them. A registered-shaped fixture table is never copied to, or read from, a path in `STAGE2_PATHS`.
5. **Padding, the one permitted adapter.** A case 1 fixture family needs at least 1,000 primary rows and at least one admitted `not_estimable` row that meets every evidence screen (`admission_a13.py:126-157`). The generator pads with estimated synthetic rows to reach the row count. Padding is the only permitted adapter.
   - The fixture manifest lists the padded row keys and the admitted row.
   - No padded row lies in a context a contributing fixture run looks up.

   This follows stage 1's interpreter decision, which allowed fixture-only adapters for the mixed fixture. It is recorded for the operator in the repair note.
6. **The gate terms that differ by mode are exactly these:**
   - job equality with `stage2_runs` (G2);
   - the exact seed counts per cell (100, 400, 75);
   - the frozen calibration pins;
   - the model keys `n_agents`, `carrying_capacity` and `rollout_steps`;
   - fewer seeds per cell;
   - `path_map`.

   Everything else runs identically in both modes. Each builder's report lists every `if fixture` branch in its code, and the final comparison checks that list against this one.
7. **F7's twin.** A job's identity and seed include `tables_path` (`artifacts.py:257-272`). So the twin is run under a second simulation root that holds the twin table at the same relative path. Job, seed and relative path are identical. Only the table bytes differ, by the one admitted row.

**Registered structure** (exact counts, `stage2_runs` equality, refusal of fixture-only inputs) is still tested on synthetic specs with no outputs, as in D:590.

## A1.2 The comparator has its own root and its own binding (amends D:189, D:246, D:273-274, D:301-331, D:348)

- **Two roots.** `inputs.json` gains `comparator.execution_simulation`, the comparator checkout's `simulation` directory. The stage 1 `main_r2` root is on X2-1 under `~/v3_a5_labels/simulation/v3/runs/a12_stage1/runs/` (`REQUIREMENTS_DIGEST.md:59`). Its job path strings resolve against that root, never against the stage 2 execution root.
- **Chain item 4, comparator form:**
  - Every contributing comparator job's `config["tables_path"]` and `config["calibration_path"]` equal `STAGE2_PATHS["nominal"]` (`tables_a10.py:323`).
  - The supplied nominal table is the file at that relative path under `comparator.execution_simulation`.
  - Its bytes are bound by the nominal identity record (`v3/runs/a10_stage1/nominal/family_identity.json`, committed bytes).

  The main spec has no `a10_family_paths` field, so this replaces the arm form for the comparator.
- **G2, comparator:**
  - The main spec's jobs equal `tables_a10.paired_runs(*STAGE2_PATHS["nominal"])`. The runbook records those strings (`A10_RUN_ON_X2.md:63`; DN:2282, as the second check read them), and `verify` tests the equality without reading a value.
  - If they differ, the reader refuses. It does not substitute the spec's own strings, and the question returns to the operator.
- **The binding** is a fifth reading-input inventory, made under approvals item 42 before item 43. It uses the crowding inventory's schema (`stage2-crowding-reading-input-inventory-1` key names) and is made read-only on X2-1.
  - **What it binds for `main_r2`:** the final spec's file hash and seal, the root's `manifest.json`, the completion records and output counts, `verified_output_hashes.json` and its digest, the job path strings, and the nominal family chain (table, validation receipt, A10 receipt, labels and identity record).
  - It opens no output value.
  - Its own go and charge go to the operator.
  - The authorized-hash document lists its file hash and seal, as for the arm inventories.

## A1.3 Admission through an A16 round (replaces the fifth bullet of G6 at D:364, and case 2 condition 4 at D:405)

G6 branches on `manifest["a13_admission"]["scope"]`.

- **`validation_launched_under_A13`:** as drafted. The original `validation_run/a13_admission_check.json` reads `outcome: "passed"`, and its `plan_hash` equals the validation receipt's `plan_hash`.
- **`A10_stage2_after_A16_r<q>`:**
  - **The original admission check record** must read `outcome: "refused"`, and its file sha256 must equal the receipt's `refusals.original.admission_record_sha256` (`validation_extension_a16.py:1368-1370`).
  - **For q = 2,** the round 1 admission record's file sha256 must equal `refusals.round1_admission_record_sha256` (`:1371-1372`).
  - **The round record** is `<stem>.a16_round<q>.admission.json` (`:1285`). It must read `outcome: "passed"`, and its `plan_hash` must equal the bound `manifest.a13_admission.a16.plan_hash`. The round plan's hash is what it records (`:1270`); the validation receipt keeps the original `plan_hash` (`:1379`), which is not compared with it.
  - Its `admission_identity(record)` must equal `a16.admission_record_sha256`, and its file sha256 must equal the receipt's `a16_rounds.r<q>.admission_record_sha256` (`:1366-1367`).
- **Case 2, condition 4:** the admission record that bound the published table (the original under A13, the round record under A16) reads `outcome: "passed"` and `residual_count: 0`. An A16 family can end with zero admitted rows. That is case 2 on the same terms as any other family.
- **Fixtures:** F13 gains a variant (e): a valid A16 round 1 family, admitted, which must pass G6. F14 gains (d): the same family with the round record's `plan_hash` replaced by the receipt's original `plan_hash`, which must refuse.

## A1.4 No outcome bit may reach a terminal or log (amends D:152 and D:540-545)

At `4dcc18c2`, `reading_a6.py:359` computes `arm_b - nom_b` outside `np.errstate`. NumPy prints `RuntimeWarning: invalid value encountered in subtract` only when some resample is undefined on both sides. That is one bit of outcome. The second check observed it on F3 and not on F1.

- **Warnings off.** At process start, before any import of NumPy-using code: `warnings.simplefilter("ignore")`, and `numpy.seterr(all="ignore")` once NumPy is imported. Every helper call is also wrapped in `np.errstate(all="ignore")` and `warnings.catch_warnings()`.
- **One top-level handler.** It catches every exception. It prints only `REFUSED: <phase>: <reason_class>` and, for an exception the reader did not raise itself, the exception's class name. It never prints `str(exc)`, `repr(exc)` or a traceback. `refusal.json` holds the same fields.
- **Captured streams.** The item 43 wrapper captures stdout and stderr to files in the run's unsealed log folder. Before anyone reads the capture, the interpreter checks it holds only lines matching the allowed patterns of D:540-545, as amended here. A line outside them is reported by count only, without being read.
- **Fixture assertions.** On the F3 arrays through both wrappers, and on F1, stderr is empty and stdout holds only the allowed success lines. F16 repeats this check.

## A1.5 A5 disclosures (amends D:517; settles the draft's open question 11)

A5 requires that "every result whose configuration looks up a row with a violation carries a disclosure, wherever it appears, naming the row, the number of violated cells and their total exposure" (DN:1249-1251). A8 item 11 makes the label record an input and says the reading attaches those disclosures (DN:1488). REQ section 2 keeps sqrt on A5.

- **Scope:** the sqrt family, for its six comparisons, and the nominal comparator's family, for all 14. A comparison's result is disclosed if any contributing run on either side looks up a row with a violation.
- **Keys:** `disclosure.<quantity>` with `{disclosure_rows: [{row, violated_cells, total_exposure}], claims_conditional_on_violations: bool}`, sorted by row key, in the stage 1 form (rB/`values.py:115-117`). They are computed from the hash-bound label records (sqrt `v3_rerun_labels_A10.json`; the nominal family's labels) and from each contributing job's looked-up rows. No run output value enters them.
- **Variant families:** they carry the no-label sentence of D:517 and no disclosure key. Their rows have no A5 labels under the adopted interpretation.
- **Input contract:** the comparator's `family.labels` (D:328) is required and bound by the nominal identity record chain.
- **Fixture:** F11 gains (h). A fixture sqrt-shaped family has one labelled violation row in a looked-up context, and the comparison must carry exactly that disclosure.

## A1.6 The current stage 2 pin (amends D:341 and G1)

- **G0:** `verify_registration(pin, instrument=tables_a10.NOMINAL)`, as `stage2_run_specs` calls it (`tables_a10.py:662`). Without `instrument`, the current-pin test at `artifacts.py:449-455` is skipped.
- **G1:** each arm spec's `registration` equals the pin.
- **The comparator spec:** its own recorded registration pin is verified with `verify_registration(<its pin>, instrument=tables_a10.NOMINAL, historical=True)`, and must equal the pin the fifth inventory records. It is a stage 1 spec, so the current-pin test does not apply to it.

## A1.7 Not-run handling (amends D:323, D:382-384)

- **Contradiction check, made non-vacuous.** For a `not_run` arm, the reader tests the canonical run root `v3/runs/a10_stage2/runs/<family>` under the execution root for any file under `*/records/`. Any such file refuses, whatever the operator's input supplied. No published table may exist at `STAGE2_PATHS[family][1]`, as drafted.
- **The reason comes from the evidence, never from a free string:**
  - **(a) After A16 entry:** the family record `<stem>.a16_family.json` must have `terminal` not null and `published_round` null (`validation_extension_a16.py:515`). The reason is its `terminal.reason`, which has four native forms: `round %d finding: %s` (`:583`, `:603`), `round %d declined by the operator: %s` (`:627`), `round %d scientific halt: %s` (`:724`) and `round 2 Part 2 refused; no third round` (`:1302`). Confirmed at `4dcc18c2` by the interpreter.
  - **(b) Original refusal with no A16 entry:** the refused original `validation_run/a13_admission_check.json` (`outcome: "refused"`), plus the operator's item 42 closeout record naming the arm and its not-run reason. The reason string is the closeout record's, and the authorized-hash document binds it.
- **Evidence set:** for (a), the family record and every refused admission record; for (b), the refused record and the closeout record. Every evidence file's sha256 is in the authorized-hash document.
- **An arm with a published table and an incomplete run root is never "not run".** The reader refuses, and the matter goes to item 42 as an operational question.

## A1.8 Absent helper fields (amends D:507-508)

- `reason` is null when the helper returns none.
- `undefined_share` is null when the point boundary is undefined, for every cap* entry (nothing is measured there), and for a not-run arm.
- `undefined_tail` is null for cap*.
- No build writes 0.0 for a quantity that was not measured.

## A1.9 F2 and F3 (replaces those rows of D:574-575)

- **The reader's comparison layer exposes no tail argument.** The tail comes only from the frozen registry.
- **F2** is a helper-level test outside the reader. It calls `reading_a6.compare_boundary` directly with injected tails, as the committed test does (`test_v3_stage2_phase2.py:1718-1722`).
- **F3** runs through the reader's two wrappers on the arrays of D:575. The expected outcomes were measured by the second check and are to be confirmed by the final check:
  - **A10 wrapper** (seed 20261011, alpha 0.05/18, tail 0.05/36): undefined share 53/50,000 = 0.00106; verdict `inconclusive`; interval `["-inf", "+inf"]`; `undefined_tail` 0.05/36.
  - **A6 wrapper** (seed 20260929, alpha 0.05/33, tail 0.05/66): share 60/50,000 = 0.0012; verdict `undetermined`; reason `undefined-resample share 0.0012 exceeds the Bonferroni tail 0.00076`.

## A1.10 L1 arrays are data, not prose (amends D:566 and F1 to F5)

The fixture generator writes every L1 array, exactly as specified in D:573-577 and this addendum, into one file, `L1_ARRAYS.json`. Where D:577 leaves a value open (F5's "comparator crosses between 0.060 and 0.062"), the generator fixes it and the file records it. Both builders consume that file and construct no L1 array of their own. Its sha256 goes into the freeze record.

## A1.11 `verified_output_hashes.json` (amends D:272 and D:354)

The writer is the runbook's `check_done` (`A10_RUN_ON_X2.md:447-451`), not a module under `simulation/v3/`. Keys are `<phase>/outputs/<job_id>.json`, relative to the root. Values are the file's lowercase hex sha256. The L2 fixture generator writes the file in the same form for every fixture root.

## A1.12 Inputs read but not bound (amends D:215, D:244, D:364)

- **Completion records:** the reader reads only `job`, `code_hash`, `status` and `output_hash`. `host` and `lease` are not read.
- **The sqrt admission check record:** its file sha256 goes into the authorized-hash document, since INV-S does not list it.
- **The seed registry:** its bytes must equal `git show HEAD:simulation/v3/runs/registered/A10_stage2_seed_registry.json` in the reader's checkout, and its payload digest must equal every arm spec's `seed_registry_sha256`.
- **Case 2 gains two conditions** (from the second check, section 3 item 4): every contributing job's instrument equals `tables_a10.family_instrument(family)`, and a registered job's model carries no `n_agents`.

## A1.13 `run_log.json` (amends D:538)

It holds times, file names, file hashes, byte counts, resource peaks, and the number of files and jobs verified. It holds no count derived from an output, a table row or an incidence record.

## A1.14 F6 coverage (amends the F6 row at D:578)

Each F6 run has at least 60 steps, so that it passes at least one review-period boundary. The fixture manifest names, per condition (extinction with absorbing padding, a held review, a fired review, a survival-first step), the run that covers it. The test asserts that each condition occurs in the outputs.

## A1.15 Additions to the record

- **The freeze record states the order of events:** the sqrt and crowding outputs existed, unread, when the reader was frozen.
  - REQ's verdict line says to freeze the contract "before stage 2 outputs exist". The plan's item 11 reader release did not take place before the stage 2 launches, so that letter is not met. Its purpose, a reader fixed before any result is known, is met: no stage 2 output has been opened.
  - The repair note records this as a disclosure for the operator.
- **Unsupported denominators refuse the whole reader** (D:434). This is stricter than REQ section 3's "report them as not recorded and fail the complete pooled-incidence requirement". It is chosen because a reading that fails Part 2(e) has no complete quantity to report.
- **Build plan time** (D:647): add about one working day for the registered-shaped fixtures of A1.1. That makes about five working days in all, a budget estimate.
- **The probe of build step 6** is a hard precondition of the item 43 go. If its projection exceeds 6 hours, the choice in D:724 goes to the operator before the run.

## A1.16 Decisions on the draft's open questions

| # | Decision |
|---:|---|
| 1 | Noted. REQ is frozen by hash under A16 (`AMENDMENT_A16_adopted.md:74`), and its stale line citations change nothing. This specification cites `4dcc18c2` |
| 2 | A fifth reading-input inventory for the comparator under item 42 (A1.2). Its go is the operator's |
| 3 | For the operator. The interpreter recommends yes: a value-free `verify` on the real inputs as a named step of item 43, before any `read`. Stage 1's fix rule applies (RS:227): a fix is allowed only while no outcome value has been computed |
| 4a | `status: "not run"`, `verdict: "undetermined"`, reason `arm not run: <reason>`, with the reason taken from the evidence (A1.7) |
| 4b | A1.7 |
| 5 | Pin D:68's spelling. No stage 1 comparison is recomputed, so stage 2 keys need not match stage 1 keys by string |
| 6 | A separate fixture generator that builds no reader generates the L1 file and every L2 fixture. Both builders receive files only. Each builder may add its own synthetic unit tests, as in stage 1 |
| 7 | "Not recorded". The second check adds that the survival-first count is also inexact when a fired review replaces the chosen rule (`integration.py:409-410`) |
| 8 | For the operator, after the probe |
| 9 | The σ inventories use the crowding schema and include the admission check record and the pre-dispatch run spec. The sqrt admission record is bound through the authorized-hash document (A1.12) |
| 10 | Commit this specification and its addenda with the freeze record, as the draft's section 8.5 says. Record its sha256 in every sealed output. The design note is not touched |
| 11 | Settled by A1.5 |
| 12 | The reader opens no `*.sqlite*` and nothing under `host_x2/`. It relies on the accepted item 42 inventories |
| 13 | No stage 1 value enters stage 2's process. Any comparison with stage 1 values waits until after item 44 |
| 14 | Noted (F2 is a helper-level test, A1.9) |
| 15 | Confirmed by the σ inventories when they exist |
