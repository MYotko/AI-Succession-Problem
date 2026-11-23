# Addendum 8 to the stage 2 reader specification, version 3 (2026-11-22)

**Applies to** the draft (`3ac0f425…5822`) as amended by Addenda 1 to 7 (Addendum 6 at version 5, `6d6ea4a3…ec13`; Addendum 7 `19983112…48f8`). Where it differs from them, it governs.

**Source:** the interpreter's decisions on the second check of fixture stage G2, `fixtures\g2_check\REPORT.md` (`6bd90cd1…4baf`), verdict SOUND, whose section 4 drafted much of this text. Version 2 applied the second check of version 1 (`spec_checks\addendum8_check\REPORT.md`, verdict NOT SOUND), adopting its replacement text with the choices its repair note states. Version 3 applies the final check of version 2 (`spec_checks\addendum8_final_check\REPORT.md`, NOT SOUND narrowly) in the same way. Facts are those checks' measurements and readings, labelled where they matter.

**What this addendum does:**
- it pins the record schemas and key sets that G2 had to choose (A8.1 to A8.5);
- it adds fixture variants and changes to the fixture deliverables (A8.6);
- it settles A6.4a's negative controls and infinity points and adds a key-check rung (A8.7), and settles the not-run reason forms (A8.8);
- it states F11(h)'s expected disclosure rows (A8.9);
- it names G1's and G2's fabrications (A8.10), lists what is accepted as built (A8.11), and records the G2 rulings that bear on the specification (A8.12).

## A8.1 Authorized-hash documents (amends D:261-267, A1.12, A2.5, A3.5 rows 1 to 3, 9 and 12)

**The gap.** The specification names the authorized-hash document but gives it no schema. A3.5 rows 1 to 3 in fixture mode compare the spec with "the fixture manifest's job list and counts", which no reader input carries.

**Both documents:**
- are sealed: `{"payload": ..., "sha256": seal(payload)}`, canonical bytes plus a newline. The reader verifies the seal;
- hold exactly the fields listed for their mode, plus `schema`. Any other key refuses;
- have every listed field present. `inventories`, `identity_records` and `fixture_layout` have one entry per run arm, plus `comparator` (`nominal` in `identity_records`), and none for a not-run arm. `not_run_evidence` has one entry per not-run arm and none for a run arm. `supplementary_records` follows A8.4. A missing or extra entry refuses. `sqrt_admission_check_sha256` is null when sqrt is not run. `supplementary_records` and `not_run_evidence` are `{}` when empty.

Registered mode accepts only schema `a10-stage2-authorized-hashes-1`, and fixture mode only `a10-stage2-authorized-hashes-fixture-1` (A3.5 row 9). Map keys are the component names `sqrt`, `crowding`, `sigma_squared_x10`, `sigma_squared_x0.1` and `comparator` unless stated otherwise.

**The registered document,** `AUTHORIZED_HASHES_STAGE2.json`, schema `a10-stage2-authorized-hashes-1`:

| Field | Type and content |
|---|---|
| `inventories` | `{component: {file_sha256, seal}}`, the reading-input inventory of each run arm and of the comparator |
| `specification_set` | the ordered list of `{name, sha256}` of the specification documents (A2.11) |
| `specification_set_digest` | `v3.artifacts.digest` of that list (A3.7) |
| `requirements_sha256` | the file sha256 of REQ |
| `registration` | `{commit, path, sha256}` |
| `not_run_evidence` | `{family: {evidence name: sha256, or a list of sha256 in the evidence list's order}}` (A8.3) |
| `sqrt_admission_check_sha256` | a file sha256, or null when sqrt is not run |
| `supplementary_records` | A8.4 |

In registered mode, identity records stay bound by committed bytes (A3.5 row 6). The registered document carries no `identity_records` field.

**The fixture document,** `AUTHORIZED_HASHES_FIXTURE.json`, schema `a10-stage2-authorized-hashes-fixture-1`, holds every field of the registered document, plus:

| Field | Type and content |
|---|---|
| `identity_records` | `{family: file sha256}`, `nominal` included (A3.5 row 6, fixture mode) |
| `a13_refusal_admission_record_sha256` | a file sha256 (A3.5 row 11) |
| `fixture_list_hash` | the fixture's file list hash, below (A3.5 row 12) |
| `fixture_layout` | `{component: {seeds_per_cell, job_count}}`, the layout of the untampered fixture |

**A3.5 rows 1 to 3 in fixture mode** read `fixture_layout`:
- every registry cell of the component holds exactly `seeds_per_cell` jobs;
- no job lies outside the registry cells;
- the spec holds `job_count` jobs.

Fixture mode tests counts only. Equality of the job list is tested in registered structure, F12(g). This replaces row 1's fixture term "the fixture manifest's job list". Residual, stated: no L2 fixture holds a non-contributing comparator job, so the selection of the 6,225 contributing runs from the comparator's 24,900 jobs (D:354) is tested only by each builder's registered-structure tests.

**The set fields.** The reader verifies that `specification_set_digest` equals `v3.artifacts.digest(specification_set)`. It copies `specification_set`, the digest and `requirements_sha256` into `reading.json` and `SEAL.json` (A2.11). It compares them with nothing else. A new addendum changes the document, not the reader's source (A6.4 step 7).

**The fixture list hash.**
- **Per fixture.** `fixture_list_hash` is `v3.artifacts.digest` of the sorted list of `[tree, relative path, sha256]` over every file of the fixture's three trees, except `AUTHORIZED_HASHES_FIXTURE.json` itself and the materialized `inputs.json`.
- **What the reader does.** It copies the field into `reading.json` and `SEAL.json` (A2.5, A3.5 row 12). It recomputes nothing.
- **The set's overall hash** is the digest of each fixture's list hash, each fixture document's file sha256, the L1 file's sha256, and the sha256 of each negative-control and registered-structure file. It is recorded in the fixture manifest and in the freeze record (D:671), and in no fixture document.

## A8.2 The item 42 closeout record (amends A1.7(b))

A1.7(b) names the operator's item 42 closeout record without a schema. The registered reader must parse the real record with the code that parses the fixture's, so there is one schema, `a10-stage2-item42-closeout-1`.

**The record** is sealed, one per not-run arm, and holds exactly `schema` and these fields:
- `family`;
- `status: "not run"`;
- `reason`, a non-empty string;
- `a16_entered: false`;
- `refused_admission_record: {path, sha256}`;
- `canonical_run_roots_checked`: the list of the two root patterns of A2.9, as strings relative to `simulation/`;
- `no_other_run_root_of_the_family_exists: true`.

**The reader checks:**
- the seal and `schema`;
- `family` against the arm, and `status == "not run"`;
- `a16_entered is False`, and that no file exists at the family record's path, `Path(STAGE2_PATHS[family][1]).with_suffix(".a16_family.json")` under the execution root (`validation_extension_a16.py:433-434`);
- that the record holds no key outside the listed set;
- `reason` is a non-empty string;
- `refused_admission_record.sha256` equals the evidence file's sha256;
- `no_other_run_root_of_the_family_exists is True`.

## A8.3 `inputs.json` keys and paths (amends D:301-331, D:323, A2.1 item 6, A3.6)

- **`comparator.family`** holds exactly these keys:
  - `table`, `validation_receipt`, `cell_results`, `a10_receipt`, `labels` and `identity`;
  - `admission_check`, the A14 round's admission record;
  - `a13_round_admission`, the preserved A13 refusal;
  - `a13_round_record`, `a14_round_record`, `a14_public_record` and `a13_public_record`.
- **The A13 public record.** `a13_public_record` is the A13 public record that `receipt.a13_round.public_file_sha256` names (A4.3 item 21). The reader checks that its file sha256 equals that field (`validation_extension_a14.py:715`). Schema `stage2-reading-input-inventory-2` gains the key `a13_public_record`, in A3.6's entry form.
- **Name map.** Between `inputs.json` and an inventory:
  - `table` binds to `family_table`, `identity` to `family_identity`, and `pre_spec` to `run_spec_family`;
  - an arm's `admission_check` binds to `a13_admission`, and `comparator.family.admission_check` to `a14_round_admission`;
  - `a16.family_record` binds to `a16_family_record`, and `a16.rounds.r<q>.{round_record, admission_record, public}` to entry q of `a16_round_records`, `a16_round_admission_records` and `a16_public_records`;
  - every other key keeps its name.
- **A not-run arm's `inputs.json` entry** holds `status` and `evidence` only. D:323's `reason` key is withdrawn; the reason comes from the evidence (A1.7).
- **Evidence sets.** `evidence` holds exactly one of two key sets, and any other set refuses:
  - for A1.7(a): `{a16_family_record, refused_admission_record, a16_round_admission_records}`, the last a list ordered by round, possibly empty;
  - for A1.7(b): `{refused_admission_record, closeout_record}`.
- **Paths in `inputs.json` locate files and are not compared with literals.**
  - The reader opens each file at the path `inputs.json` gives, and binds it by hash to its inventory entry or its authorized hash.
  - The comparator spec is the file at `comparator.spec`, bound to the fifth inventory's `roots.runs.spec.{file_sha256, seal}`.
  - The reader compares no inventory `path` value with an `inputs.json` path. It compares no `inputs.json` path with a literal, except A1.2's test that the nominal table is the file at `STAGE2_PATHS["nominal"][1]` under `comparator.execution_simulation`.
  - Every path-string gate of D:273-274, A1.2, A1.7 and A2.9 stands.

## A8.4 A16 records of an arm inventoried under INV-S or INV-C (amends A2.10, A3.6)

The INV-S and INV-C schemas have no key for A16 records. If a registered arm with one of those inventories went through A16, nothing would bind its family, round, admission and public records.

- **Selection.** The inventory adapter selects by the inventory's `schema` string alone, in both modes. No family is tied to a schema.
- **Presence.** `supplementary_records.<family>` exists exactly when the family's `inputs.json` entry has `family.a16` not null and its inventory's schema is INV-S's or INV-C's. It holds `a16_family_record`, `a16_round_records`, `a16_round_admission_records` and `a16_public_records` in A3.6's entry form, the lists ordered by round. A missing block, an extra block, or a block beside a schema 2 inventory refuses.
- **Binding.** Each file `family.a16` names hashes to its entry's `sha256`, and its seal equals the entry's `seal`, as D:271 states for an inventory.
- **Fixtures.** G2 adds three variants of F13(e) inventoried under INV-C:
  - F13e4, with the block. It is valid.
  - F13e5, with one entry's `sha256` replaced and the document re-sealed. It refuses.
  - F13e6, with the block absent. It refuses.
- **Residuals, stated:** a sqrt arm under INV-S with A16 has no fixture; it takes the same code path. No fixture has an extra block, a block beside a schema 2 inventory, a seal mismatch in the block, or a two-round block.

## A8.5 Quantities and keys (amends D:494-519, D:499)

- **Quantity keys.** The two components together have 84 quantity keys, 30 in A10 and 54 in A6, whether or not an arm ran. These are the D:494-497 keys, including `<F>.boundary_point.<arm>` and `<F>.capstar_point.<arm>.<a>`.
- **An arm that ran.** Each of its quantities carries `incidence.<quantity>`, `incidence_status.<quantity>`, `incidence_counts.<quantity>` and `disclosure.<quantity>`.
- **A not-run arm.**
  - Its comparison keys hold `status: "not run"`, `verdict: "undetermined"`, `reason: "arm not run: <reason>"`, and `estimate`, `interval` and `undefined_share` null (D:384, A1.8). `level_alpha` is the registry level. `undefined_tail` is the registry tail for a boundary and null for cap*.
  - In `contributing_runs.json`, `quantities[<key>]` of a not-run arm's quantity is the sorted list of the comparator side's runs alone, and the empty list for `survival.<arm>.<rr>`. The file carries no status; `values.json` does. This replaces D:499's "listed with `status: "not run"`".
  - Those comparator runs are contributing runs. They are in `runs`, pass G4, enter K and the `records/main` rung, and have entries in `incidence_per_run.json`. No incidence is pooled for the quantity.
  - Its `boundary_point`, `capstar_point`, `survival` and `survival_difference` keys each hold `{"status": "not run"}`.
  - It has no `incidence.*`, `incidence_status.*` or `incidence_counts.*` key (D:499).
  - Each of its quantities carries `disclosure.<quantity>`, from the comparator side alone (A3.7).
  - It has `family.<name>.status`, and no `family.<name>.labels`, `family.<name>.admission` or `family_error.<name>.*` key.
- **`family.<name>.status`** is `{"status": "run"}`, or `{"status": "not run", "reason": <the evidence's reason, without the "arm not run: " prefix>}`.
- **The nominal family.** Each component's `values.json` carries `family.nominal.status`, `family.nominal.labels` and `family.nominal.admission`. `family.nominal.labels` is `{policy: "a5_labels_required", labels_sha256}`. The policy string is pinned here as a literal, because `tables_a10.STAGE2_LABELS_POLICY` has no `nominal` entry. `admission` is as A3.4 states.
- **G2 adds to the manifest,** for F13a, F13d and F13d2: the keys each component's `values.json` must hold, each not-run comparison entry in full, and each component's `quantities` lists. All follow from the specs and the evidence, with no model run.

## A8.6 Fixture changes for the G2 repair (amends A5.10's G2 deliverables)

The generator makes these changes in its repair. None needs a model run.

1. **New refusing or valid variants.** Re-binding an entry in an inventory also re-binds that inventory's own entry in the fixture document.
   - **F14f2:** the A13 refusal's bytes altered and re-sealed, with the inventory entry (`sha256` and `seal`) and the fixture document's `a13_refusal_admission_record_sha256` re-bound, and the receipt untouched. The alteration is F14f's. Only A2.1 item 3's receipt comparison fails. Residual, stated: both receipt fields (`refusals.a13_admission_record_sha256` and `a13_round.admission_record_sha256`) fail together; isolating each needs a rebuilt receipt chain.
   - **F12c2:** an output's bytes altered by F12c's alteration and its record's `output_hash` re-bound, with `verified_output_hashes.json` stale. Only the hash-file comparison fails.
   - **F12c3:** an output's bytes altered by F12c's alteration, with `verified_output_hashes.json` and the inventory re-bound and the record stale. Only the record comparison fails.
   - **F12f2:** one extra job in the σ0²×0.1 spec only, in the arm's own category and grid label, at rr 0.061 (a `REFINEMENT_RR` value, `study.py:6`, off the σ grid), with no output and no record. The final spec, the pre-dispatch spec, the root's `manifest.json` and `identity.json` and the inventory follow the altered spec. The "no job outside the registry cells" test and the `job_count` test both fail; the per-cell test holds. They cannot be separated: with every cell at `seeds_per_cell`, a job outside the cells always changes the count. Native `select_boundary_cells` ignores an off-grid record (`reading_a6.py:260`), so only the reader's own tests refuse it.
   - **F13i:** F13d2 with a sealed A16 family record present at sqrt's family-record path (A8.2). Only the "no family record" test fails.
   - **F13j:** F13d2 with the closeout record's `a16_entered` true, the record re-sealed and re-bound in the fixture document. Only that test fails.
   - **F13f:** a not-run arm with a file under `runs/<family>/*/records/`.
   - **F13f2:** the same, with the file under `<family>/runs_run/*/records/`.
   - **F13g:** an arm declared `not_run` under A1.7(a), whose A16 family record has `terminal` null and `published_round` null. Only the terminal-latch test fails.
   - **F13h:** a not-run arm with a published table at its target and a run root holding records for some jobs. The table check and the records check both fail. It is a combined case, not isolated, and redundant with F13b and F13f; it is kept as a combined case.
   - **F13a2:** a not-run arm whose family record reads `round 2 Part 2 refused; no third round`, with both rounds' refused admission records as evidence. It is valid.
   - **F13e4 to F13e6** (A8.4).
2. **The incidence reference and screens over 84 keys.** In the manifest, `fixtures.<ID>.reference.incidence` and `screens.<ID>` are regenerated over A8.5's keys, and the report states the count.
3. **The packaged manifest without L2 facts.** The builder package's copy of the manifest drops these keys of `screens.<ID>`:
   - `infinite_interval_end`;
   - `undefined_point_boundary`;
   - `cap_star_with_non_degenerate_fire_rates_on_both_sides`;
   - `full_native_results`.
4. **The control files under A8.1 to A8.5.** Every fixture's authorized-hash document, closeout record, `inputs.json`, inventory and `values` reference is regenerated under the pinned schemas and key sets. Payload keys outside a pinned set (such as `fixture`, `fixture_id`, `note`, `reader_fixture` in a document or a record) are dropped. Each regenerated fixture document lists the nine documents of the specification set, with `ADDENDUM_8.md` at its final sha256; G2 starts only after that file is final, and a later addendum means every fixture document is regenerated then; a later addendum alone moves no per-fixture list hash, only the overall hash. The fixture list hashes and the overall hash are recomputed under A8.1.
5. **F11(h)'s per-quantity lists** are added to the manifest (A8.9).
6. **The ladder controls** are regenerated with A8.7's rung, and `LADDER_D.json` is added.
7. **The builder package** is rebuilt with a new `SHA256SUMS.txt`.

**What a builder receives.** From `stage2_reader_2026-11-21\`, a builder receives only:
- the specification set: the draft, `ADDENDUM_1.md` to `ADDENDUM_5.md`, `ADDENDUM_6.md`, `ADDENDUM_7.md`, `ADDENDUM_8.md` and any later addendum;
- the rebuilt builder package;
- its own brief.

Every other file under that folder is withheld. That includes each report, each `executor_final_message.txt`, every `scripts\` and `work_copy\` folder, the full manifest, the twin root and the superseded `ADDENDUM_6_v*` files. What a builder may read outside that folder is D:627 and D:631, unchanged.

## A8.7 A6.4a and A6.7: negative controls, infinity, and a key-check rung (amends A6.4a, A6.7)

- **Negative controls.** A negative control for the ladder tool is a hand-built pair under stated test keys, or a sound build and a deliberately defective copy of it, each run once on the same fixture. Two fixture roots are never a control. K covers the bytes of every contributing output, so two ladders whose contributing outputs differ in any byte differ at every rung. Two roots that differ only outside the outputs (a table, a receipt, a label record) give identical ladders, so that pair is no control at all.
- **Infinity.** The undefined point boundary is covered at L1 (F5) and need not appear at L2. The infinite interval end is covered at L1 (F3) and at L2 (G2's screen, kept outside the package).
- **The key-check rung.** The ladder gains one rung class, `key`, walked first. The walk order is `key`, `records`, `cells`, `result`, `incidence`.
  - The class has one rung, `key/check`, whose value is `HMAC-SHA256(K, canonical({"check": "a10-stage2-ladder-1 key check"}))`, in A6.4a's rung form.
  - When the two ladders' K are equal, `key/check` is equal and the tool localizes as A6.4a describes.
  - When K differs, the tool names `key/check`, not `records/<first>`. K can differ because the contributing bytes differ, or because a build formed K wrongly (byte order, or the contributing set). Either way, a K disagreement is never mistaken for a difference in the first records rung, and a P4 diagnosis starts from that fact.
  - A component whose arms are all not run still has the rung, since K is defined over the comparator's contributing outputs.
  - This amends A6.4a's technical form and no adopted proposal: by Addendum 6's text, A6.4a carries no proposal mark, and A6.4b (P7) names the tool without reference to its rungs.
- **The rung's control.** `LADDER_A`, `B` and `C` share one key, so `key/check` is equal in all three. G2 adds `LADDER_D.json`, built from A's structures under a second stated test key. The tool must name `key/check` for A against D. A walk that starts at `records` names `records/main` instead, and a plain sorted walk names a `cells` rung. So D also tests the class order.

## A8.8 Not-run reason forms (amends A1.7(a))

The reader copies `terminal.reason` verbatim, as `arm not run: <reason>` in the comparison entries and without the prefix in `family.<name>.status` (A8.5). It tests no reason form. The native forms of A1.7(a) are facts about the writer (`validation_extension_a16.py:583`, `:603`, `:627`, `:724`, `:1302`; the latch stores `str(reason)` at `:612`). F13a2 (A8.6) covers the round-2 refusal form. No fixture of the scientific-halt form is required.

## A8.9 F11(h)'s expected disclosure rows (amends A2.7's fixture statement)

The violation rows of the labelled families (sqrt and nominal) are:
- **X:** (rr 0.064, alpha 1.0, capability 1.5), rule `w1_p0_t1_g3`;
- **Y:** (rr 0.058, alpha 1.0, capability 2.25), the same rule.

Each side contributes its own family's rows. X and Y are distinct rows in the sqrt label record and in the nominal one. By A2.7's configured-set rule (with `study.capabilities(1.5)` giving 1.0, 1.5, 2.25, 3.375 and 5.0), the expected disclosures are:
- **`boundary` and `boundary_point`:**
  - sqrt: four rows (X and Y of sqrt, X and Y of nominal);
  - crowding: two (nominal's X and Y);
  - each σ arm: one (nominal's X).
- **`capstar` and `capstar_point` at alpha 1.0:** sqrt, two rows (X of each family); crowding, one (nominal's X). At other alphas: none.
- **`survival.<arm>.<rr>`:** sqrt's own X at 0.064 and own Y at 0.058; none for crowding or a σ arm.
- **`survival_difference.<arm>.<rr>`:** at 0.064, sqrt two rows and each A6 arm one; at 0.058, sqrt two and crowding one; none elsewhere.

G2 computes the lists from the label records and adds them to the manifest. Any difference from this reading goes to the interpreter, who settles it by addendum before the builds.

## A8.10 Fabrications named (adds items 25 to 44 to A3.3)

A3.3's list has items 1 to 24 after A5.3 and A5.5.

**Items 25 to 29, G1's five:**
25. the pinned clock of the A16 writers;
26. the original refused candidate, its sidecar and its receipt;
27. the plan stub;
28. `c0` on A16-marked rows;
29. the sidecar floor's two endpoint counts.

**Items 30 to 44, G2's fifteen:**

30. the fixture authorized-hash document;
31. the item 42 closeout record;
32. the final spec's `pull_dispatch` block and the pre-dispatch spec;
33. each run root's `identity.json`, written by hand;
34. inventory blocks beyond D:248-256's subset;
35. the eligible floor triple's companion values;
36. the round-2 A16 material: the plan stub, the hand-set round-record fields, and the round markers on rows;
37. `inputs.json` key names;
38. the hand-built jobs and rows of F8, F12(f), F14(c) and F15(a);
39. the hand-written strict and no-label receipts and label records of F11;
40. the ladder test key, the rung values and the negative-control files;
41. the registered-flag structure specs;
42. the hand-written sqrt run job configurations;
43. root `c1`'s 14 copied outputs and records;
44. schema 2 for an A16 crowding arm.

Items 30, 31, 37 and 44 are now specified by A8.1 to A8.4. The files stay hand-written, under A3.3 items 13 and 15.

The full text of each item is in the manifest's `fabrications_new_since_A4.3`. The items G2's repair adds are numbered on from 45 and named in the manifest. None is a reader rule.

## A8.11 Accepted as built

- the real σ0²×10 registered job list in `registered_structure\`, which any builder can compute from the repository;
- the value-free real items of the G2 check's finding 2.5: the registration pin, the frozen parent calibration, the removed files' names and sizes, the machine name and paths in output envelopes;
- F14(c)'s `M` and `M_FV` left at base values;
- the not-run fixtures without refused candidate tables;
- the sqrt inventory's `failed_attempt` naming a root absent from the tree;
- `c1`'s G1 sidecar and floor forms (A7.7 fixes its bytes);
- MAIN's equal seed counts on both sides (F06 and the A16 fixtures cover a transposition).

## A8.12 The G2 rulings that bear on the specification

From the interpreter's nine rulings in G2's brief, these stand as decisions of the specification set:
- **Ruling 1.** The A16 publication files and round-record fields of a fixture are hand-written in the native field sets, as named fabrications. `spec_hash` is the digest of a label-path plan stub.
- **Ruling 2.** F6 condition (a)'s extinction step is the first step with `allocation_evaluated` false.
- **Ruling 3.** The F6 screen includes sqrt-shaped seeds. F6's set does not depend on it.
- **Ruling 4.** F7's twin is a second crowding-shaped table whose admitted row no F7 run looks up at run time, as the oracle comparison shows. The candidate (rr 0.055, alpha 1.0, capability 5.0) held.
- **Ruling 7.** From the generator, builders receive the builder package only: fixture files and run-root files, with no export and no repository code (the package's own `materialize.py` is a fixture tool). Each root excludes the tracked `simulation/diagnostics/` tree except files the native code or a fixture needs, extending A5.8. What a builder may read elsewhere is D:627 and D:631, unchanged. A8.6 lists what else is withheld.
- **Ruling 8.** The fixture set includes an A16 family that publishes after round 2.
- **Ruling 9.** The negative controls follow A8.7.

Rulings 5 (run batching) and 6 (carrying G1's fabrications, now A8.10) concern the generator only.
