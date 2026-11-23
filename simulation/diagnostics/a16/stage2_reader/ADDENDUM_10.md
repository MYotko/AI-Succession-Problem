# Addendum 10 to the stage 2 reader specification (2026-11-23), repaired after the second check

**Version.** Draft `968c4306…728c`, second-checked NOT READY on one high, three medium and eleven low findings (`spec\checks\addendum10-check\REPORT.md`). The repair (`349faa1d…6611`) was final-checked READY WITH FINDINGS, eight low (`spec\checks\addendum10-final-check\REPORT.md`). This version applies those too; every disposition is in the interpreter's record. This is the specification-set text: every statement of which build made which choice, and each builder's rule-question numbers, are removed, so that neither builder learns the other's work. No rule text differs from the interpreter's attributed text, sha256 `d765e3647b88781feab9fdb34512d43fd4270553905924f41de309546005b7cc`.

**Applies to** the draft (`3ac0f425…5822`) as amended by Addenda 1 to 9 (Addendum 6 at version 5, `6d6ea4a3…ec13`; Addendum 8 final, `a795fb12…1dff`; Addendum 9, `01b42ad3…7927`). Where it differs from them, it governs. Draft lines are cited `D:n`. Files of the repository at `4dcc18c2` are cited `name.py:n` for `simulation/v3/name.py`.

**Source:** round 0 of section 8.3, the interpreter's first blind comparison of the two builds on the G2 fixture set, and the two builders' reports, each with its own rule questions. Round 0 found [R, the interpreter's table]:

| Criterion (D:653-659) | Round 0 |
|---|---|
| 1. Byte identity of each build's two runs; `both` against separate | Pass in both builds |
| `LADDER.json` across builds | Identical on all 24 components |
| 2. `values.json` | A10 identical on all 12 valid fixtures. A6 differs on 11, only in `incidence_counts.<quantity>` for a pool holding no case 1 run |
| 3. `quantities` | Equal on all 24 |
| 3. `incidence_per_run.json` by hash | Differs on all 24. Every per-run record and every `per_run_sha256` is equal; the envelope differs |
| 4. Refusal phase | Equal on all 38 |
| 5. Expected outcomes | None "not held". One reference block of F08a names a job of F08b |

Every difference sits where the text leaves a form open or a rule unstated. D:661 says such a gap "is fixed here, by addendum, before freeze, never by one builder copying the other." This addendum is that fix. Each ruling is taken from the specification and the native code. Where a build report describes its builder's choice, that choice was read as a candidate and nothing more.

**Labels:** [M] measured by the drafter in this session; [R] read from the cited file; [I] inferred, with the reasoning stated; [G] guessed. Native measurements were made in the interpreter's clone at `4dcc18c2`, `code_identity()` `93a453b27c82a9cb16ed0d04b1029168014b73c1f3d97f5b884e1b6d52f161da` [M], in the WSL phaseb environment. A label followed by "second check" or "interpreter" marks a measurement or reading by that party, as the interpreter's record shows.

**What this addendum does:**
- it pins `incidence_counts.<quantity>` (A10.1) and `incidence_per_run.json` (A10.2);
- it pins one common collection, the `verify` command's output, and the opening of the item 43 sequence (A10.3);
- it adds two events to A6.2 item 1 and amends A6.4a's and A6.4 step 3's refused-pass sentences (A10.3c, A10.3d), for the operator;
- it states which inventory fields are tested and which are only recorded (A10.4), and which identity an inventory carries (A10.5);
- it states which producer fields G1 tests, and how the calibrations are accepted (A10.6);
- it corrects F08a's reference block (A10.7);
- it rules on the remaining rule questions that can make the two builds diverge (A10.8);
- it lists the fixture changes that follow (A10.9), and closes with the table of rulings and what none of them changes (A10.10).

## A10.1 `incidence_counts.<quantity>`, every field (amends D:468 and D:515)

**The question.** D:515 gives one shape. D:468 says the separate counts are "pooled over case 1 runs only, by reason, with the count of runs they cover", and "for case 2 runs they read `not recorded`". Neither says what a pool with no case 1 run holds. Two readings were candidates: each reason map as `{}`, or the string `"not recorded"`.

**What it rests on.**
- D:467-468, D:515; A1.16 decision 7 ("Not recorded"); REQ section 3 case 1 ("Preserve the separate exclusion, fallback and survival-first unavailable-score counts by reason") [R].
- The native record: `admission_a13.summarize` writes the three maps per branch as `dict(Counter)` (`admission_a13.py:205-222`) [R]. A case 1 run in which nothing was excluded records `{}` in each: `summarize([])` returns `{}` for all nine maps [M]. So `{}` is a recorded fact.
- A6.1 removed D:434's "not recorded" for denominators. The literal survives only here, for the separate counts.

**The ruling.** For a quantity whose arm ran, let its pool be the list `quantities[<quantity>]` of `contributing_runs.json`. Each run has the status of its family (D:467): `recorded` (case 1) or `no admitted rows` (case 2). Then `incidence_counts.<quantity>` is exactly:

```
{"recorded_runs": <int>,
 "not_recorded_runs": <int>,
 "branches": {"ordinary_allocation": <C>, "survival_first": <C>, "yield_review": <C>}}

<C> = {"excluded_by_reason": <V>,
       "balanced_fallbacks_by_reason": <V>,
       "survival_first_unavailable_selections_by_reason": <V>}
```

1. `recorded_runs` is the number of runs of the pool with status `recorded`. `not_recorded_runs` is the number with status `no admitted rows`. Both are JSON integers, and their sum is the length of the pool.
2. `branches` always holds the three branches, and each branch always holds the three count names.
3. **When `recorded_runs` is 0,** every `<V>`, all nine, is the JSON string `"not recorded"`.
4. **When `recorded_runs` is positive,** every `<V>` is a JSON object from reason to integer: for each reason that is a key of that map in at least one `recorded` run of the pool, the sum of that key's values over the `recorded` runs. A reason is kept whenever it appears, whatever its sum. A map with no reason in any `recorded` run is `{}`. Reason keys are the strings of the output file, copied and never interpreted. The case 2 runs of the pool add nothing to any map; `not_recorded_runs` states how many they are.
5. A not-run arm's quantities have no `incidence_counts` key (A8.5). A pool is never empty for an arm that ran, because G2 puts at least one job in every registry cell.

**The reason.** The text supports both `{}` and the string for the empty-coverage pool. The string is chosen because it keeps an unrecorded fact apart from a recorded zero: `{}` is what a case 1 run writes when it excluded nothing [M], and D:468's own words for case 2 are "they read `not recorded`". For a mixed pool the literal reading of D:468 stands: the maps cover the case 1 runs, and the two run counts say how much of the pool that is.

**Worked example, synthetic.** Four runs. `main/rerun_m1` and `main/rerun_m2` are case 1; `crowding/rerun_c1` and `crowding/rerun_c2` are case 2. Their records are the ones in A10.2's example. `synthetic_reason_b` is an invented reason string. The values below are `v3.artifacts.canonical` of each result [M].

A pool with no case 1 run, `A6.survival.crowding.0.064`, runs `c1` and `c2`:

```
{"branches":{"ordinary_allocation":{"balanced_fallbacks_by_reason":"not recorded","excluded_by_reason":"not recorded","survival_first_unavailable_selections_by_reason":"not recorded"},"survival_first":{"balanced_fallbacks_by_reason":"not recorded","excluded_by_reason":"not recorded","survival_first_unavailable_selections_by_reason":"not recorded"},"yield_review":{"balanced_fallbacks_by_reason":"not recorded","excluded_by_reason":"not recorded","survival_first_unavailable_selections_by_reason":"not recorded"}},"not_recorded_runs":2,"recorded_runs":0}
```

A mixed pool, `A6.survival_difference.crowding.0.064`, all four runs:

```
{"branches":{"ordinary_allocation":{"balanced_fallbacks_by_reason":{},"excluded_by_reason":{"missing_or_not_estimable_row":1,"synthetic_reason_b":5},"survival_first_unavailable_selections_by_reason":{}},"survival_first":{"balanced_fallbacks_by_reason":{"synthetic_reason_b":3},"excluded_by_reason":{"missing_or_not_estimable_row":2,"synthetic_reason_b":40},"survival_first_unavailable_selections_by_reason":{"missing_or_not_estimable_row":1,"synthetic_reason_b":2}},"yield_review":{"balanced_fallbacks_by_reason":{},"excluded_by_reason":{"missing_or_not_estimable_row":1},"survival_first_unavailable_selections_by_reason":{}}},"not_recorded_runs":2,"recorded_runs":2}
```

A pool of `m1` and `m2` alone gives the same `branches` with `"not_recorded_runs":0,"recorded_runs":2`.

**Fixture expectations changed:** none. The packaged manifest holds no reference value for any `incidence_counts` key [M: the string occurs only in key lists]. The printed values below are references for round 1 (A10.9 item 3).

## A10.2 `incidence_per_run.json` (amends D:481, D:523 and D:554)

**The question.** D:481 gives the file's content as "per-run normalized incidence records and statuses" and marks it sealed. D:554 compares it by sha256. No passage gives its schema string, envelope, entry fields or key form. The two builds agree on the schema string, on the key form and on every record, and differ in the rest.

**What it rests on.** D:481; D:488 (the key form `"<component>/<job_id>"` and the `runs` map of `contributing_runs.json`); D:467 (the two statuses); D:523 ("the run's record": the recorded field exactly as in the output for case 1, the normalized record of D:428-432 for case 2); A6.4a (the input component names); A8.5 (the comparator runs of a not-run arm's quantities "have entries in `incidence_per_run.json`") [R].

**The ruling.**
1. **Bytes.** `canonical(seal(payload)) + b"\n"`, with `v3.artifacts.canonical` and `seal` (`{"payload": payload, "sha256": digest(payload)}` [M, source read through the running code]).
2. **Payload.** Exactly two keys:

```
{"schema": "a10-stage2-incidence-per-run-1",
 "runs": {"<input component>/<job_id>": {"record": <record>, "status": <status>}}}
```

3. **Keys of `runs`.** Exactly the keys of `runs` in the same component's `contributing_runs.json`. The input component is one of `main`, `sqrt`, `crowding`, `sigma_squared_x10`, `sigma_squared_x0.1`.
4. **Entry.** Exactly two keys.
   - `status` is `"recorded"` for a run of a case 1 family and `"no admitted rows"` for a run of a case 2 family.
   - `record` is, for `recorded`, the output's `result["a13_decision_incidence"]` exactly as parsed: three branches, each with its seven native fields. For `no admitted rows` it is the object of the three branches, each the normalized record of D:428-432 with its `provenance`.
5. **No reason and no family per run.** A case 2 entry carries no `reason` key, and no entry carries a `family` key. The status literal `no admitted rows` is the per-run statement. D:467's reason text is a per-family coverage fact; where it is written is unchanged by this addendum.
6. **No `component` key.** The payload follows `contributing_runs.json` (D:488), whose `runs` map it mirrors key for key and which carries none.
7. **`per_run_sha256`** (D:523) is unchanged: sha256 of `canonical(m)` with no newline, `m` mapping each of the quantity's contributing keys to that run's `record` value. Both builds already agree on it [R, round 0].
8. **The comparison** of D:554 is of the file's sha256.

**The reason.** This is the most literal reading of D:481: records and statuses, and nothing else. A family is a function of the input component, and a reason string repeated per run is a constant; neither is a per-run record or status. The unrecorded and the recorded stay distinct: a case 2 record carries `provenance` and no reason maps, and a case 1 record carries the reason maps and no `provenance`.

**Worked example, synthetic.** The four runs of A10.1's example. The file's exact text, one line and a newline, 2,928 bytes, sha256 `a94e65974de1eb2aad0e1515959a15246737f030627fbccfb9bf479ea75aa806` [M]:

```
{"payload":{"runs":{"crowding/rerun_c1":{"record":{"ordinary_allocation":{"assessed":true,"denominator":25,"numerator":0,"provenance":{"denominator":"derived_from_recorded_decisions","numerator":"structural_zero_from_verified_family"},"rate":0.0},"survival_first":{"assessed":true,"denominator":475,"numerator":0,"provenance":{"denominator":"derived_from_recorded_decisions","numerator":"structural_zero_from_verified_family"},"rate":0.0},"yield_review":{"assessed":true,"denominator":4,"numerator":0,"provenance":{"denominator":"derived_from_recorded_decisions","numerator":"structural_zero_from_verified_family"},"rate":0.0}},"status":"no admitted rows"},"crowding/rerun_c2":{"record":{"ordinary_allocation":{"assessed":false,"denominator":0,"numerator":0,"provenance":{"denominator":"derived_from_recorded_decisions","numerator":"structural_zero_from_verified_family"},"rate":null},"survival_first":{"assessed":false,"denominator":0,"numerator":0,"provenance":{"denominator":"derived_from_recorded_decisions","numerator":"structural_zero_from_verified_family"},"rate":null},"yield_review":{"assessed":false,"denominator":0,"numerator":0,"provenance":{"denominator":"derived_from_recorded_decisions","numerator":"structural_zero_from_verified_family"},"rate":null}},"status":"no admitted rows"},"main/rerun_m1":{"record":{"ordinary_allocation":{"assessed":true,"balanced_fallbacks_by_reason":{},"denominator":25,"excluded_by_reason":{"missing_or_not_estimable_row":1,"synthetic_reason_b":3},"numerator":1,"rate":0.04,"survival_first_unavailable_selections_by_reason":{}},"survival_first":{"assessed":true,"balanced_fallbacks_by_reason":{"synthetic_reason_b":2},"denominator":475,"excluded_by_reason":{"synthetic_reason_b":40},"numerator":0,"rate":0.0,"survival_first_unavailable_selections_by_reason":{"synthetic_reason_b":2}},"yield_review":{"assessed":true,"balanced_fallbacks_by_reason":{},"denominator":4,"excluded_by_reason":{},"numerator":0,"rate":0.0,"survival_first_unavailable_selections_by_reason":{}}},"status":"recorded"},"main/rerun_m2":{"record":{"ordinary_allocation":{"assessed":true,"balanced_fallbacks_by_reason":{},"denominator":25,"excluded_by_reason":{"synthetic_reason_b":2},"numerator":0,"rate":0.0,"survival_first_unavailable_selections_by_reason":{}},"survival_first":{"assessed":true,"balanced_fallbacks_by_reason":{"synthetic_reason_b":1},"denominator":30,"excluded_by_reason":{"missing_or_not_estimable_row":2},"numerator":2,"rate":0.06666666666666667,"survival_first_unavailable_selections_by_reason":{"missing_or_not_estimable_row":1}},"yield_review":{"assessed":true,"balanced_fallbacks_by_reason":{},"denominator":5,"excluded_by_reason":{"missing_or_not_estimable_row":1},"numerator":1,"rate":0.2,"survival_first_unavailable_selections_by_reason":{}}},"status":"recorded"}},"schema":"a10-stage2-incidence-per-run-1"},"sha256":"f89e30ad4afb666183a482d6ad611c1fa580e811ac3421587d24cfd7a94be438"}
```

For the same runs, `per_run_sha256` is `5bce962f6ff98c9fbd9afb41b779b0a16565ebeb9f33ab0abc1522e2c5055080` for the pool `c1`, `c2`, and `a5dd92d09919befc93b88e55a22738f58d6771352a495762aff284d2d3c247e0` for all four [M].

**Fixture expectations changed:** none; the manifest holds no reference for this file [M].

## A10.3 The collection, `verify`'s output, and the opening of the item 43 sequence (amends D:277-287, D:341, D:482, D:484, D:531, D:698, A6.2 item 1, A6.4 step 3, A6.4 step 8 and A6.4a)

**The question.** D:279-287 make `collect` a command of the frozen reader, and take the collection's form from the stage 1 collection contract, which neither builder was given for stage 2. D:698 runs a single `collect` before "reader A `verify`; reader B `verify`", but each reader has its own `collect`. Each build defined its own sealed collection. Rule questions from both builders ask the same things.

**What it rests on.** D:277-287 (the two steps; files read in place; the folder new and outside every input root; strict JSON; "a registered `read` requires the sealed collection"; "the sealed collection binds the exact emitted reader input and file inventory"); D:301-333; D:337 ("`verify` runs them and stops. `read` runs them again and then computes"); D:482 and D:531 (`collection_sha256`); D:543; A1.4; A6.3 ("It writes only pass, or a refusal record"); A6.4 step 8 and A6.7 (when `collect` is repeated); A8.3 (paths locate files) [R].

**The decision: one common collection.** Both readers write the same collection, byte for byte, from the same operator document, and either reader accepts a collection the other wrote. D:698's single `collect` then means what it says, and the second reader's `collect` becomes a cross-check on the first.

### A10.3a The collection's form

1. **The operator's document** is the `inputs.json` of D:301-331 as amended by A1.2, A2.1 item 6, A3.4 and A8.3. This addendum adds no key to it and removes none. It holds no `collection` object: D:282's words "inputs-with-collection-object" come from the stage 1 contract and are withdrawn. Every file leaf (item 5), `execution_simulation`, `comparator.execution_simulation`, `comparator.root`, each arm's `root` and each `excluded_roots[].path` is an absolute path. `registration.path` is a repository-relative name inside the registration pin (D:309, A1.6); it is no location and is not tested for absoluteness. No other string of the document is a path.
2. **The folder** named by `--out` holds exactly two files: `inputs.json` and `collection.json`.
3. **`inputs.json`** is `canonical(document) + b"\n"`, where `document` is the operator's document as strictly parsed, with nothing added, removed or rewritten.
4. **`collection.json`** is `canonical(seal(payload)) + b"\n"`, with payload exactly:

```
{"schema": "a10-stage2-collection-1",
 "inputs_sha256": "<sha256 of the bytes of the folder's inputs.json>",
 "files": {"<label>": {"bytes": <int>, "sha256": "<lowercase hex>"}}}
```

5. **File leaves and labels.** `files` has one entry per file leaf of the document. The file leaves are:
   - the top-level `authorized_hashes`;
   - under each `arms/<family>`: every string at any depth under every key except `status`, `root` and `excluded_roots`;
   - under `comparator`: every string at any depth under every key except `execution_simulation` and `root`.

   A `null` is no leaf. Any other non-string value under those keys refuses. The label is the path of keys from the document's top, joined by `/`, with a list element named by its zero-based index: `arms/sqrt/family/table`, `arms/crowding/family/a16/rounds/r1/admission_record`, `arms/sigma_squared_x0.1/evidence/a16_round_admission_records/0`, `comparator/family/labels`.
6. **Entry.** `bytes` is the file's size and `sha256` the sha256 of its bytes, both from one read of the file in place. A file leaf is opened by its path with symbolic links followed. It is accepted when the file reached is a regular file, and `bytes` is the length of the bytes read. A symbolic link to a regular file is not refused.
7. **Nothing else is in it.** No reader identity, role, time, host or mode. The directories (`execution_simulation`, each `root`, each excluded root), the run outputs, the completion records and the files a reader finds by convention under a root are not collected. The inventories bind those, and D:275's ledger watches every file a pass reads.
8. **`collection_sha256`** in `SEAL.json` and `reading.json` (D:482, D:531) is the sha256 of the bytes of `collection.json`.

### A10.3b What `collect` checks, and what only `verify` checks

- **`collect` does this and no more:** it parses the operator's document strictly; it checks the document's form, and that each path A10.3a item 1 names is absolute; it reads each file leaf once to hash it; it requires the destination to be new and outside every input root; it writes the two files under temporary names and renames them, `collection.json` last (A6.4a's write order).
- **Form** means: strict JSON; the top-level key set; the four family names under `arms`; each arm's key set for its status, the `comparator` and `comparator.family` key sets and the evidence key sets, as D:301-331, A1.2 and A8.3 pin them; and the value types (string, null, list, object, boolean) in those places. Every other test of the document, A10.8 item 6 included, belongs to `verify`.
- **The input roots** are `execution_simulation`, `comparator.execution_simulation`, `comparator.root`, each arm's `root` and each `excluded_roots[].path`. The destination must not exist, and must not be inside, or equal to, any of them. Inside and equal are decided on `os.path.realpath` of the destination and of each input root, by whole path components. G0's rule for the `verify` and `read` destinations (D:341) names the same set.
- **`collect` may refuse only for:** a document that is not strict JSON or not in that form; a non-string, non-null value where A10.3a item 5 looks for leaves; a relative path; a file leaf that is missing, unreadable or not a regular file; the destination. A build may also assert G0 at the start of any command. Every refusal has phase `input_verification`.
- **`collect` parses no file but the operator's document.** It verifies no seal, loads no table, reads no spec, and decides no mode beyond the document's own `fixture` flag (for `path_map`, D:287).
- **Every gate G0 to G9 runs in `verify`, and again in `read`, in full,** whatever `collect` checked (D:337). That includes the document-form tests, the agreement of `fixture` with the specs' `registered` flags (D:333), and every content test of every collected file. No gate is satisfied by a `collect` having passed.
- **`verify` and `read` also test the collection,** in both modes; it is not a mode term:
  1. the `--inputs` path is a file named `inputs.json` whose folder holds `collection.json`;
  2. `collection.json`'s seal verifies and its payload has exactly the three keys and the schema string;
  3. the sha256 of `inputs.json`'s bytes equals `inputs_sha256`;
  4. the key set of `files` equals the label set the reader derives from the document;
  5. each collected file, on the pass's first read of it, has the entry's `bytes` and `sha256`. Every collected file is read in every pass.

  A failure of any of the five refuses at `input_verification`.
- **Tested at `collect` only:** the absoluteness of paths and the location of the collection folder. That leaves no gap: `verify` and `read` take `<C>`, which both `collect` runs produced and A10.3d compares.

### A10.3c `verify`'s output, `read`'s folders and `refusal.json`

Only as far as the item 43 sequence needs the two builds to match.

- **`verify`** takes `--inputs <collection folder>/inputs.json --out <new folder>`. The sequence always passes `--out`.
  - On pass the folder holds `verify.json`, and `run_log.json` if the build writes one. `verify.json` is canonical JSON plus a newline, an object with `"status": "pass"` and whatever value-free provenance the build adds within A1.13 and A6.8. It is compared with nothing.
  - On refusal the folder holds only `refusal.json`.
- **`read --component both --out <new folder>`** writes `<out>/A10/` and `<out>/A6/`, each with the six files of D:476-482 and A6.4a, and `<out>/run_log.json`. With one component named, `<out>` holds that component's folder and `run_log.json`. A refused pass writes `<out>/refusal.json`. A component folder whose `SEAL.json` was written before the refusal stays, and is listed in the event record (A6.4 step 1).
- **`refusal.json`** is a bare JSON object, not a sealed envelope, holding exactly `phase`, `reason_class` and `status` with the literal `refused`, with the values of the printed line (D:543), plus `exception_class` only for an exception the reader did not raise (A1.4). The item 43 record takes label and phase from the captured line, which D:543 already pins.
- **Exit status** is 0 exactly when a command passed.

### A10.3d The sequence (replaces the first three steps of D:698)

1. Reader A: `collect --inputs <operator document> --out <C>`.
2. Reader B: `collect --inputs <the same document> --out <C2>`.
3. The byte-identity tool compares `<C>` and `<C2>`. Both files must be identical. A difference is an event (A6.2 item 1) on the A6.3 route.
4. Reader A: `verify --inputs <C>/inputs.json --out <new folder>`. Reader B: the same, on `<C>`.
5. From there D:698 continues as amended by A6.11, every `read` taking `<C>/inputs.json`.

`<C2>` is kept as the record of the cross-check and is never an input. Where A6.4 step 8 repeats `collect`, it repeats steps 1 to 3.

**Events.** A6.2 item 1 now reads: "`verify` refuses, `collect` refuses, or the two collection folders of A10.3d differ;". Each is handled on the A6.3 route. A10.3c also amends two sentences of A6.4: A6.4a's "A refused pass writes only `refusal.json` (D:484)" and step 3's "A refused pass writes no ladder". Under `--component both`, a component folder sealed before the refusal stays, with its ladder, and is hashed and locked at A6.4 step 1. No other text of Addendum 6 changes.

**The reason.** A collection written by one build and trusted by the other without a common form would put one build's input bookkeeping under both readings unseen. A common form costs a pinned schema, and buys a value-free cross-check on the very first step. Keeping `collect` to hashing and document form keeps every gate refusal in `verify`, where A6.3 records it and where both builds run it.

**Worked example, synthetic.** A10.11 gives a document, the content rule for its 46 files, and the resulting hashes.

**Fixture expectations changed:** none. D:658 fixes phase and fact, and both hold in both builds. A refusal keeps its phase whichever command first meets it.

## A10.4 Inventory fields: tested, or recorded (amends D:248-256, D:271-272 and D:343)

**The question.** D:254 lists `jobs`, `records` and `outputs` among the keys read, and no passage says what they are compared with. One reading refuses when they differ from what the reader verifies. The other records them and compares them with nothing.

**The ruling.** The reader's tests on an inventory are exactly these. Every other key is ignored (A9.3), and the keys of D:248-256 not named below are copied into `reading.json` provenance and compared with nothing.

| Tested | Against | Basis |
|---|---|---|
| The inventory's file sha256 and seal | the authorized-hash document's `inventories.<component>` | D:263, A8.1 |
| `verdict`, `findings`, `roots.runs.all_checks_pass` | `complete and consistent`, empty, true | D:343 |
| `identity.code_identity` | the running identity (A10.5) | D:343 |
| `roots.runs.spec.{file_sha256, seal}` | the spec file | D:271 |
| the root's `manifest.json` | its bytes equal the spec's | D:271 |
| `roots.runs.verified_output_hashes_sha256`, `roots.runs.outputs_digest` | `verified_output_hashes.json`, as D:272 states | D:272, A1.11 |
| each published file's `{sha256, seal}` | the file `inputs.json` names, by A8.3's name map | D:271, A8.3 |
| the comparator inventory's `registration_pin` | the comparator spec's pin, registered mode | A1.6, A9.3 |
| INV-S's `failed_attempt.{path, not_run_reason}` | read and recorded | D:299, A9.3 |

**Recorded only:** `roots.runs.jobs`, `roots.runs.records`, `roots.runs.outputs`, `roots.runs.identity_file_sha256`, `roots.runs.manifest_file_sha256`, `roots.runs.path`, every `path` (A8.3), `identity.checkout_commit`. The same holds for a run spec's `pull_dispatch.code_commit` (D:213). The reader does not open a root's `identity.json`.

**The reason.**
- It is the literal reading. D:271-272 and D:343 state the tests, and the counts are in none of them.
- A count can contradict nothing the reader does not already test on a hash-bound file. The spec's jobs are fixed by G2. Every contributing record and output is fixed by G4 against the spec and the hash file. The hash file is fixed by D:272. A count that disagreed with those would show a defect in the inventory's own bookkeeping, which `verdict`, `findings` and `all_checks_pass` already state.
- The exact meaning of the three counts in the two registered inventories is not visible to the drafter or to either builder (a scalar or a per-phase map; files found or files verified). A gate built on an unseen layout is the failure D:12 ranks high.
- `manifest_file_sha256` is recorded only. D:271 already binds the root's `manifest.json` to the spec's bytes, and the spec's bytes to `roots.runs.spec.file_sha256`. Given those two tests, a test of this field could fail only if the field meant something other than the manifest's hash, which would be a wrong refusal of a genuine inventory. In the packaged fixture inventories it equals the manifest's hash [M, second check]; INV-S and INV-C were not opened for this addendum.

**Fixture expectations changed:** none. F12e and F12f2 refuse at G2, as the generator's binder names for them (A9.6), at phase `input_verification`, in any build that follows this ruling [I: the count test is gone, and each fixture's expected outcome names G2].

## A10.5 The inventory identity test (amends D:343; adds to A1.2 and A2.10)

**The question.** D:343 requires that an inventory's `identity.code_identity` "is the running identity". Read literally, that applies to every inventory, the comparator's included, so an inventory made at another accepted identity would refuse at G1. The comparator's root was produced at `174ab660…`, which is accepted only through an A11 record (D:50).

**What it rests on.** D:48 ("Both inventories record this identity for the stage 2 roots", and "INV-C records it at checkout `4dcc18c2`"); D:343; A1.2 (the fifth inventory, made under item 42 with the crowding schema); A2.10 ("The reader is frozen before the three new inventories exist. They are made to conform") [R]. `accepted_identities()` returns the running identity and the producing identities of valid committed A11 records (`compatibility_a10.py:104-114`), and an A11 record is a proof about run outputs: sampled jobs re-executed and compared by `comparison_bytes` (`compatibility_a10.py:71-101`, `:149-156`) [R].

**The ruling.**
1. **Every inventory the reader reads carries the running identity.** For each run arm's inventory and for the comparator's, `identity.code_identity` must equal `93a453b2…f161da` exactly, in both modes. Membership in `accepted_identities()` suffices for none of them.
2. **What the field means, pinned for schema `stage2-reading-input-inventory-2`.** `identity.code_identity` is `v3.artifacts.code_identity()` of the checkout from which the inventory session ran its checks. It is not the producer of the root it describes.
3. **The root's producer is a different field under a different rule.** It is the spec's `code_hash`, repeated in every completion record and output envelope. G1 tests it by membership in `accepted_identities()` (D:343); G4 requires every record and output to carry the spec's value (D:354); and for an arm G2 also requires it to equal the running identity (D:347). The comparator's `174ab660…` passes there, by its A11 record.
4. **The consequence for item 42.** The comparator inventory and the two σ inventories are made by a session whose checkout has code identity `93a453b2…`. The comparator inventory is not made from a checkout at the comparator's own producer.

**The reason.** It is the literal reading of D:343, which names no exception. An inventory is a set of checks, and it is trusted because the code that ran them is the code the reader runs under. An A11 record gives no ground for trusting checks run under other code: it shows that two identities produce equal run outputs, and says nothing about a hashing and counting session.

**The facts, as the interpreter found them.** No registered inventory was opened for this addendum.
- INV-S and INV-C record `93a453b2…` in `identity.code_identity` (D:48) [R].
- The comparator inventory exists. Its maker, `Lineage v3\stage2_inventory_comparator_2026-11-22\x2_upload\scripts\invk_main.py`, writes the session's own `code_identity()` into `identity.code_identity` (`:1320`) and halts unless that equals `93a453b2…` (`:72`, `:877-896`). Its executor report records `93a453b2…f161da` for the session's checkout (`REPORT.md:28`) [R, interpreter]. Its `identity` block therefore meets item 1, and item 2's meaning is the one its maker uses.
- If INV-S's or INV-C's `identity.code_identity` in fact records the root's producer and not the session's identity, the rule's outcome for those two is unchanged: D:48 gives `93a453b2…` for both, and for sqrt and crowding the producer and the running identity are the same value [R, I].
- If any of the three inventories still to be accepted already exists with another identity, or can only be made from a checkout at another identity, the reader is not relaxed. The inventory is remade under item 42. If that is not possible, the question returns to the interpreter with the fact, for a further addendum before the freeze.
- The interpreter confirms these facts before the freeze (the interpreter's record, open point 1).

**Fixture expectations changed:** none. All 236 packaged fixture inventories carry `93a453b2…` [M, final check report, section 6].

## A10.6 Producer fields, and how the calibrations are accepted (amends D:343; adds to D:233-240 and A3.1)

**The question.** D:343 says "every producer field met (`code_hash`, `producer_code_hash`) is in `accepted_identities()`". A3.1 makes the frozen parent calibration mandatory for every fixture family, and D:233 for nominal, sqrt and crowding. The parent's producer is `20e58c03…e4e3`, outside the four accepted identities (measured below).

**What was verified.**
- **The field.** A calibration's producer is `payload["code_hash"]`, which `calibration.freeze` sets to `code_identity()` at the time it is frozen (`calibration.py:96-97`) [R].
- **Its value in the frozen parent.** Loaded through native `load_calibration(<STAGE2_PATHS["nominal"][0]>, registered=True, instrument=<declaration>)`, the parent has seal `bf0f7c3f10310558d567b6b3f7c24f6f99f2fe6eb71fd830cccfd8e2aa0bd6d6` and `code_hash` `20e58c03ea5c21403a592e5a7e07a6b3cc463c3ebffdb485f7042233ceffe4e3` [M]. `accepted_identities()` in the clone returns `174ab660…`, `5df9866f…`, `93a453b2…` and `c19b54f5…` [M]. The parent's producer is in none of them [M].
- **How the native loader treats it.** Under an A10 instrument, `validate_calibration` accepts the document when its seal equals `instrument.CALIBRATION_SHA256` (`calibration.py:177`; `instrument.py:16`), or else sends it to `_validate_a10_variant` (`:178-179`). The one test that compares `code_hash` with the running code applies only when the instrument is not A10 (`:182-185`), and it uses the calibration's own compatibility record, not A11. `registered=True` adds only the fixture, tag, trajectory-count and step tests (`:186-187`) [R]. The load was accepted under the nominal, sqrt and crowding instruments, all of mapping A10 (`tables_a10.py:13`, `:34`) [M]. So the native code accepts the parent by its exact seal and never asks who produced it.
- **The σ variants.** `_validate_a10_variant` requires `payload["code_hash"]` to equal the pinned `producer_code_hash` of `a10_constants.json` (`calibration.py:152`) [R]. That pin is `bd656b8f038c73d94c72ee4112806ca784f9ae3f4e4d4b99c0fd8a8d9fdcf7ed` for both variants, and it is also outside the accepted identities [M]. The same conflict would have met the two σ calibrations at the first registered `verify`.

**The ruling.**
1. **Calibrations are accepted by exact identity, never by producer membership.**
   - The parent: file sha256 `fd86358a…6e01` and seal `bf0f7c3f…d6d6` (D:233), and the native `load_calibration(path, registered=True, instrument=<declaration>)`.
   - A σ variant, registered mode: the `byte_sha256` and `payload_sha256` of D:235-238, and the same native load, whose `_validate_a10_variant` tests the pinned producer itself.
   - Fixture mode: as A3.1 and A3.5 row 4 state.
2. **G1's membership test does not apply** to a calibration's `payload["code_hash"]`, nor to the `producer_code_hash` values inside `a10_constants.json`. Each is copied into `reading.json` provenance (D:533) and compared with nothing by the reader.
3. **The producer fields G1 does test** are the ones among the fields D:211-231 list as read:
   - a run spec's `code_hash`;
   - a completion record's `code_hash` and an output envelope's `code_hash`;
   - a family table's `code_hash` and its `manifest.a10.producer_code_hash`;
   - a validation receipt's `producer_code_hash`;
   - an A10 receipt's `producer_code_hash`, and that of the validation receipt embedded in it;
   - an identity record's `code_hash`;
   - the A5 label record's `code_hash`, as `require_a10` tests it (`production_tables.py:186`).

   A reader tests no other field for membership, and does not search a document for keys named `code_hash` or `producer_code_hash`. The native loaders keep their own producer tests inside G6 and G7 (`production_tables.py:78-83`, `:145-156`, `:165-186` for the strict receipt, and `:202-226` for the no-label receipt), unchanged. Every family-chain field listed above, from the family table's to the A5 label record's, is already membership-tested there, or required equal to one that is [R, second check]. The run spec's `code_hash` is membership-tested by G1 alone, and the completion record and output envelope values equal it (D:354). So the reader's own test adds no refusal on a genuine chain.
4. **The reader keeps no producer list of its own** (D:51). The two calibration producers above are stated here as measurements. They are not literals for a reader's source.

**The reason.** A3.1, the later text, makes the parent's bytes mandatory, and the native code that every stage 2 run used accepts those bytes by seal. A reader that refused them on the producer would refuse every family. Item 3 is the literal reading of "producer field met": D:211-231 say which fields the reader reads, D:217 says "nothing else is read", and A5.5 binds the builders to those lists for rows. A recursive search for producer-named keys reaches fields the specification never made inputs, such as an A16 family record's `code_hash` (`validation_extension_a16.py:513-514`), and would give one build a refusal the other cannot have.

**Fixture expectations changed:** none.

## A10.7 Erratum: F08a's reference block

**The defect, verified [M].**
- In the packaged manifest, `fixtures.F08a.reference.twin_denominators_of_the_zero_agent_runs` holds two entries, `rerun_8d5f08c6e4fcb99c4720c97a` and `rerun_d368fdf0ce0bf1646a8cc510`, each with all three denominators 0.
- F08a's descriptor replaces one crowding job: `rerun_a022309bd27b46f7492a196f` by its zero-agent job `rerun_8d5f08c6…`. Its crowding job list holds `rerun_8d5f08c6…` and the unreplaced `rerun_151f8cdff55698056f982edf`. The string `rerun_d368fdf0…` does not occur in F08a's descriptor.
- F08b's descriptor replaces both jobs, and its crowding job list holds `rerun_8d5f08c6…` and `rerun_d368fdf0…`.
- The manifest's F08b entry has no `twin_denominators_of_the_zero_agent_runs` block.

So the block is one shared list filed under F08a alone. Neither reading of the block is wrong; the block is.

**The erratum.**
1. For F08a the block has one entry, `rerun_8d5f08c6e4fcb99c4720c97a`.
2. For F08b the block has both entries, `rerun_8d5f08c6e4fcb99c4720c97a` and `rerun_d368fdf0ce0bf1646a8cc510`.
3. **"Held" means:** for every entry of the fixture's block, the A6 `incidence_per_run.json` has the key `crowding/<job id>`, with status `no admitted rows` and a normalized record whose three denominators equal the entry's. An entry naming a job that is in none of the fixture's specs makes the block wrong, not "not checkable".
4. Until the manifest is regenerated (A10.9), a build checks F08a against item 1 and F08b against item 2, reading both from the block filed under F08a.

**Fixture expectations changed:** this one block, in F08a and F08b. Under the erratum, F08a's block reads "held" in a correct build, and F08b gains one entry [I].

## A10.8 The remaining rule questions that can diverge

The full classification of both builders' rule questions is in the interpreter's record. These are the ones ruled here and not above.

1. **D:455's preconditions apply to every contributing run** (amends D:420, D:455 and A6.1). The derivation of D:438-455 runs on a case 1 run for the self-check as it does on a case 2 run, and its preconditions are tested first on both. A failure refuses at `input_verification` in either case. A6.1's label `incidence denominators not derivable` is required for a case 2 run; for a case 1 run the label is the build's own. *Reason:* D:455 says "checked per run before the counts are trusted", and the self-check on real case 1 runs is the only production evidence that the derivation is exact (D:457). A precondition that fails on a real comparator run is A6.1's third cause, and it must surface at `verify` in both builds.
2. **D:417-420 is the complete list of tests on a recorded incidence record** (amends D:607). The three branches; the types, order and consistency of `numerator`, `denominator`, `rate` and `assessed`; the three maps as objects of non-negative integers; the denominator self-check. A reader applies no test relating a numerator to the reason maps. D:607's words "which also checks reason consistency" describe a stage 1 function and carry no rule over. *Reason:* section 4.3 is the governing text and REQ section 3 case 1 lists the same tests. An unspecified test applied to at least 6,225 real records, with no fixture, could refuse a native record in one build alone (RS:299).
3. **G0 asserts one numerical thread** (amends D:341). G0 calls `v3.artifacts.runtime(1)` (`artifacts.py:314`), the check each native worker makes before it executes (`production_runner.py:330`), and refuses if it raises. *Reason:* D:53 puts "one numerical library thread" among the conditions the reader runs under, beside `PYTHONINTMAXSTRDIGITS`, which G0 already asserts. A condition gated in one build and not in the other would be a refusal in one build only. `runtime(1)` raises unless numpy's bundled OpenBLAS is found and every query returns 1 (`artifacts.py:314-335`) [R, second check]. Its return value, which includes the machine name, is not written to any sealed file (D:538).
4. **The registration pin has one value** (amends D:266, D:309 and D:341). `inputs.json`'s `registration` equals the authorized-hash document's `registration`, key for key, in both modes, and G0 verifies that pin (A1.6). A difference refuses.
5. **Scopes by family** (amends A1.3 and A2.1). The family `nominal` passes G6 only with scope `A10_nominal_after_A14`. An arm family passes only with `validation_launched_under_A13`, `A10_stage2_after_A16_r1` or `A10_stage2_after_A16_r2`. `A10_nominal_after_A13` (`admission_a13.py:10`) refuses for every family. *Reason:* A2.1 item 1 states the binding the nominal branch requires, and A3.4's checks need records only an A14 publication has.
6. **A labels file for a no-label family** (amends D:371). The test is on `inputs.json` alone: a `labels` key under a crowding or σ arm's `family` refuses. The reader searches no directory for a labels file (A8.3).
7. **The pre-dispatch spec** (amends D:294). Where the arm's inventory has a `run_spec_family` entry with `present: true`, `pre_spec` must name a file, bound by that entry, and D:294's reconstruction test applies; a null `pre_spec` there refuses. Where the inventory has no such entry, or one with `present: false`, the reader applies no test to `pre_spec` beyond the collection's hash.
8. **Not-run evidence under A1.7(a)** (adds to A1.7 and A8.3). Besides A1.7 and A2.9: the family record's `family` equals the arm (`validation_extension_a16.py:508`, `:513`); `refused_admission_record` and every record of `a16_round_admission_records` read `outcome: "refused"`. The reader infers no expected number of round records from `terminal`. *Reason:* A8.2 already requires the closeout record of A1.7(b) to name its arm, and the same evidence in its A16 form should not be weaker.

**Fixture expectations changed:** none by any of the eight.

## A10.9 Fixture changes that follow (amends A8.6 item 4, A9.6 and D:653-659)

1. **The specification set has eleven documents.** At the next regeneration each fixture document's `specification_set` gains `ADDENDUM_10.md` at its final sha256, as its eleventh entry, by A9.6's procedure and with A9.6's list of files that move. `ADDENDUM_10.md` is final before the regeneration starts. No per-fixture list hash moves for this.
2. **F08a and F08b.** The manifest's two reference blocks are written as A10.7 items 1 and 2 state.
3. **The printed values are the references for round 1.** Each builder reproduces, in its own unit tests and through its reader's own code:
   - the three `incidence_counts` values of A10.1;
   - A10.2's `incidence_per_run.json` bytes, sha256 and seal, and its two `per_run_sha256` values;
   - A10.11's `inputs.json` sha256, its 46 labels, its `files` digest, and `collection.json`'s bytes, seal and sha256.

   A10.11's paths do not exist, so its test supplies each leaf's content by the content rule through a hook that replaces only how each leaf is reached and read (its existence and regular-file test, and its bytes), and leaves the label derivation, hashing and serialization as the reader runs them. Each builder names its hook in its report.
4. **At the interpreter's option, not a precondition of round 1:** a generated `reference.incidence_counts` block per valid fixture in the manifest, and the same examples added to `L1_ARRAYS.json`.
5. **Criteria added to D:653-659.** On every fixture on which `collect` passes in both builds:
   - where both builds collect from one materialized `inputs.json`, the two collection folders are byte-identical;
   - where each build materialized the fixture for itself, the two `collection.json` payloads have equal `files`, compared by `v3.artifacts.digest`.

   Paths differ between two materializations, so `inputs_sha256` does; labels, sizes and hashes do not.
6. **No model run is needed** for any of these, and no fixture output, table or record moves.

## A10.10 The rulings, and what none of them changes

| # | Question | Ruling | Fixture expectations changed |
|---|---|---|---|
| A10.1 | `incidence_counts` with no case 1 run, and mixed | Nine strings `"not recorded"` when `recorded_runs` is 0; otherwise maps summed over the case 1 runs, with both run counts | None; the printed values are references |
| A10.2 | `incidence_per_run.json` | Sealed; payload `schema` and `runs`; entry `record` and `status`; no reason, family or component key | None |
| A10.3 | The collection; `verify`'s output; the sequence | One common collection of two files, pinned; `collect` hashes and checks document form only; both readers collect, the folders are compared, both verify the first | None; two criteria added |
| A10.4 | Inventory counts | Recorded, compared with nothing; the tested fields are listed | None |
| A10.5 | Inventory identity | The running identity, for every inventory; membership does not suffice | None |
| A10.6 | Calibration producer; producer fields | Calibrations by exact pins and the native load; G1 tests a listed set of producer fields and searches for no other | None |
| A10.7 | F08a's reference block | One entry for F08a, two for F08b; "held" defined | That block, in F08a and F08b |
| A10.8 | Eight smaller rules | As listed | None |

**What no ruling changes [I, with the measured parts marked].** Every ruling acts on one of four things: the written form of the reason-count maps; the envelope of one output file; input-side records and commands; or whether a gate refuses. None touches the registry, a filter, a cell, a seed, a resample count, a helper call or the call to `pooled_incidence`. So no ruling changes a computed estimate, interval, verdict, undefined share, survival count or rate, Wilson interval, survival difference, incidence numerator, denominator or rate, flag, `per_run_sha256`, `quantities` list or ladder rung. Round 0 already found all of those equal between the builds [R]. The rulings add no file under `simulation/v3/` and none at the top level of `simulation/`, so `code_identity()` stays `93a453b2…f161da` (D:52). The drafter measured that value in the clone during this drafting [M].

**What does change:** bytes of `values.json` in the `incidence_counts` keys of pools with no case 1 run, in a build that wrote `{}` there; bytes of `incidence_per_run.json` in a build whose file differs from A10.2; the collection's bytes, and with them `collection_sha256` in `SEAL.json` and `reading.json`; and possibly which command first refuses a refusing fixture.

## A10.11 Worked example for A10.3, synthetic

**The document.** Its canonical text is the collection's `inputs.json`, one line and a newline, 2,799 bytes, sha256 `4aa653e434d81dba5e2f5684e0990cb5605ddf03203247568b5f80d837ca65af` [M]. Its key names follow D:301-331, A1.2 and A8.3, and equal those of every packaged `inputs.template.json` [M, second check].

```
{"arms":{"crowding":{"calibration":"/fx/arm/simulation/v3/runs/registered/v3_rerun_calibration.json","excluded_roots":[],"family":{"a10_receipt":"/fx/c/a10.json","a16":{"family_record":"/fx/c/a16_family.json","rounds":{"r1":{"admission_record":"/fx/c/r1.admission.json","public":"/fx/c/r1.public.json","round_record":"/fx/c/r1.json"}}},"admission_check":"/fx/c/admission.json","cell_results":"/fx/c/cells.json","identity":"/fx/c/identity.json","table":"/fx/c/table.json","validation_receipt":"/fx/c/receipt.json"},"inventory":"/fx/control/inventory_crowding.json","pre_spec":"/fx/c/run_spec.json","root":"/fx/c/root","spec":"/fx/c/runs_plan.json","status":"run"},"sigma_squared_x0.1":{"evidence":{"a16_family_record":"/fx/x01/a16_family.json","a16_round_admission_records":["/fx/x01/r1.admission.json","/fx/x01/r2.admission.json"],"refused_admission_record":"/fx/x01/admission.json"},"status":"not_run"},"sigma_squared_x10":{"evidence":{"closeout_record":"/fx/x10/closeout.json","refused_admission_record":"/fx/x10/admission.json"},"status":"not_run"},"sqrt":{"calibration":"/fx/arm/simulation/v3/runs/registered/v3_rerun_calibration.json","excluded_roots":[{"inventory_key":"failed_attempt","path":"/fx/arm/simulation/v3/runs/a10_stage2/sqrt/runs_run","reason":"not run"}],"family":{"a10_receipt":"/fx/s/a10.json","a16":null,"admission_check":"/fx/s/admission.json","cell_results":"/fx/s/cells.json","identity":"/fx/s/identity.json","labels":"/fx/s/labels.json","table":"/fx/s/table.json","validation_receipt":"/fx/s/receipt.json"},"inventory":"/fx/control/inventory_sqrt.json","pre_spec":null,"root":"/fx/arm/simulation/v3/runs/a10_stage2/runs/sqrt","spec":"/fx/arm/simulation/v3/runs/a10_stage2/sqrt/runs_plan.json","status":"run"}},"authorized_hashes":"/fx/control/AUTHORIZED_HASHES_FIXTURE.json","comparator":{"binding":"/fx/control/inventory_comparator.json","calibration":"/fx/cmp/simulation/v3/runs/registered/v3_rerun_calibration.json","execution_simulation":"/fx/cmp/simulation","family":{"a10_receipt":"/fx/n/a10.json","a13_public_record":"/fx/n/a13.public.json","a13_round_admission":"/fx/n/a13.admission.json","a13_round_record":"/fx/n/a13.json","a14_public_record":"/fx/n/a14.public.json","a14_round_record":"/fx/n/a14.json","admission_check":"/fx/n/a14.admission.json","cell_results":"/fx/n/cells.json","identity":"/fx/n/identity.json","labels":"/fx/n/labels.json","table":"/fx/n/table.json","validation_receipt":"/fx/n/receipt.json"},"root":"/fx/cmp/root","spec":"/fx/cmp/spec.json"},"execution_simulation":"/fx/arm/simulation","fixture":true,"registration":{"commit":"0000000000000000000000000000000000000000","path":"simulation/diagnostics/v3_rerun_design_note.md","sha256":"0000000000000000000000000000000000000000000000000000000000000000"},"schema":"a10-stage2-reader-inputs-1"}
```

**The content rule.** No file of the example exists. For the example, each file leaf's content is its own label followed by one newline, in UTF-8. So `arms/sqrt/spec` has 15 bytes and sha256 `66da8e3c838911e387d77d151c7b9b388d241e50bd7c369cdf9f21c5ac6dea7c`, and `authorized_hashes` has 18 bytes and sha256 `495437b0f7f5870a128f01ba35221040d8f0b9cea9f8df98e3c8a91ee3f14915` [M].

**The 46 labels,** in sorted order [M]:

```
arms/crowding/calibration
arms/crowding/family/a10_receipt
arms/crowding/family/a16/family_record
arms/crowding/family/a16/rounds/r1/admission_record
arms/crowding/family/a16/rounds/r1/public
arms/crowding/family/a16/rounds/r1/round_record
arms/crowding/family/admission_check
arms/crowding/family/cell_results
arms/crowding/family/identity
arms/crowding/family/table
arms/crowding/family/validation_receipt
arms/crowding/inventory
arms/crowding/pre_spec
arms/crowding/spec
arms/sigma_squared_x0.1/evidence/a16_family_record
arms/sigma_squared_x0.1/evidence/a16_round_admission_records/0
arms/sigma_squared_x0.1/evidence/a16_round_admission_records/1
arms/sigma_squared_x0.1/evidence/refused_admission_record
arms/sigma_squared_x10/evidence/closeout_record
arms/sigma_squared_x10/evidence/refused_admission_record
arms/sqrt/calibration
arms/sqrt/family/a10_receipt
arms/sqrt/family/admission_check
arms/sqrt/family/cell_results
arms/sqrt/family/identity
arms/sqrt/family/labels
arms/sqrt/family/table
arms/sqrt/family/validation_receipt
arms/sqrt/inventory
arms/sqrt/spec
authorized_hashes
comparator/binding
comparator/calibration
comparator/family/a10_receipt
comparator/family/a13_public_record
comparator/family/a13_round_admission
comparator/family/a13_round_record
comparator/family/a14_public_record
comparator/family/a14_round_record
comparator/family/admission_check
comparator/family/cell_results
comparator/family/identity
comparator/family/labels
comparator/family/table
comparator/family/validation_receipt
comparator/spec
```

`arms/sqrt/pre_spec` and `arms/sqrt/family/a16` are null and have no entry. No `root`, `status`, `excluded_roots` or `execution_simulation` value has one.

**The result [M].** `v3.artifacts.digest(files)` is `44c9841172253e506f32b23bb9232c23f1ccba399465c73fdb3a30281bb3ed78`. `collection.json` is 5,940 bytes, with seal `d840a8e1fba65ab41905017b5244fd98bf4b59dd7a578a20ca3132194d4fb259` and file sha256 `5df084d106f490a27815537256b16a44d5144fe3fffa53cb939ac7537541e31e`. The script that produced every measured value of this addendum is `/home/yotko/v3_wsl/interp/a10draft/native_check.py`.
