# Addendum 6 to the stage 2 reader specification, version 5 (2026-11-22)

**Applies to** the draft (`3ac0f425…5822`) as amended by Addenda 1 to 5. Where it differs from them, it governs.

**Versions:** each earlier version is kept beside this one.

| Version | File | sha256 | Check | Result |
|---:|---|---|---|---|
| 1 | `ADDENDUM_6_v1_as_second_checked.md` | `0cf187c7…` | second check | NOT SOUND |
| 2 | `ADDENDUM_6_v2_as_final_checked.md` | `1146b3f8…` | final check | NOT CLEAN |
| 3 | `ADDENDUM_6_v3_as_confirm_checked.md` | `16e5044c…` | confirming check (`spec_checks\addendum6_confirm\REPORT.md`) | NOT CLEAN, narrowly |
| 4 | `ADDENDUM_6_v4_as_confirm2_checked.md` | `acded451…` | second confirming check (`spec_checks\addendum6_confirm2\REPORT.md`) | NOT CLEAN, narrowly: three must-changes of a few sentences each, five smaller, no leak, no wrong reading |

This version replaces all four. It applies the second confirming check's fixes as that check wrote them, and closes the document-check rounds on this addendum. The builders and their checks read it next, before the freeze; any remaining inconsistency is found there, before any stage 2 value exists.

**Authority (unchanged from version 4):**
- **The operator's decisions** of 2026-11-22 at 01:10 EST (`DECISIONS_2026-11-22.md` section 1): A6.1, A6.3, and the existence of a procedure for a defect found after computation and before opening.
- **Seven interpreter proposals,** each in effect only once the operator adopts it and the adoption is recorded before the freeze:
  - **P1:** lock and retire without a go (A6.4 steps 1 and 5);
  - **P2:** the decided opening of retired outputs (A6.4 step 10);
  - **P3:** the rules after opening (A6.5);
  - **P4:** diagnosis agents (A6.6);
  - **P5:** the last resort (A6.6);
  - **P6:** the terminal rules (A6.6);
  - **P7:** the unlock (A6.4b).

  Text that depends on a proposal is marked with it.
- **Everything else** is the interpreter's drafting under decision 3.
- **If any proposal is not adopted,** this addendum is revised and re-checked before the freeze.

These were given before any stage 2 reading computation, with no stage 2 output opened. The sqrt and crowding run outputs existed then, sealed and unread (A1.15).

**Purpose:** the reader opens run outputs read-only and in place, bound by hash. So reader, tooling and specification defects cannot alter or invalidate the runs. What they can damage is the reading's credibility, in three ways:
- a fix made after values exist;
- a stuck reading;
- an outcome leaking before opening.

This addendum fixes in advance what happens at each point, and who decides.

## A6.1 Refusal on an underivable denominator (operator decision)

- **The rule.** If any precondition of D:455 fails for a no-admitted-rows run, the reader refuses at gate G8, during `verify` or any later pass, before any estimator runs. The label is `incidence denominators not derivable`, with phase `input_verification`.
- **It follows the adopted plan,** which says "an unrecoverable denominator is an integrity refusal" (`STAGE2_PLAN.public_v2.md:336`). It is stricter than the letter of REQ section 3 ("report them as not recorded and fail the complete pooled-incidence requirement", REQ:50). The operator chose it knowing that.
- **The causes:**
  - an inconsistency inside one output;
  - a counting defect in the reader;
  - a precondition of D:455 that is wrong for a record the native code can emit. RS:299 treats a check that refuses a native record as a defect; here the check is specification text.

  The event takes the route A6.2's timing gives.
- **The residual.** Diagnosis might show that sound native records truly cannot give exact denominators. Then the refusal would be final, and no reading would exist where REQ's letter would give one marked "not recorded". That disposition is a registration matter for the operator, and probably needs a dated amendment under section 13 (DN:263) before any output is read.

## A6.2 Events, attempts and timing

**An event** is any evidence, from any source and found by any person or agent, that the reading may be wrong, stuck or exposed. It includes:
1. `verify` refuses;
2. a `read` pass refuses at `input_verification` or `after_computation_started` (D:543), or raises through the top-level handler (A1.4);
3. a pass is killed, stopped for memory (PLAN:328) or interrupted, or leaves a partial folder;
4. the change-detection re-hash (D:275) fails;
5. the blind comparison shows a differing key (D:556), or a hash-only comparison of `contributing_runs.json` or `incidence_per_run.json` differs (D:554);
6. a build's two runs are not byte-identical (D:547-549);
7. a captured stream holds a line outside the allowed patterns (A1.4);
8. a defect is found by reading or by fixtures. It may be in a reader's code, a tool (A6.7), the specification, a fixture or its expected outcome, an input, the environment, the procedure, or native code;
9. the redundant channel of A6.7 disagrees with the comparison tool;
10. anyone sees a value or a stray output line before item 44.

**Each event gets an id,** `E<yyyymmdd>-<n>`, assigned by the interpreter at A6.4 step 1, or at the A6.3 record.

**An attempt** is one item 43 go. A class (f) rerun is a new attempt under the same freeze hash. Retired folders are numbered by attempt.

**Timing:**
- An event before the first `read` pass of the current attempt starts takes the A6.3 route.
- A later event takes the A6.4 route.
- An event after a component is opened at item 44 takes the A6.5 route.

## A6.3 Before computation: `verify` first (operator decision)

- **Each attempt begins with `verify`** on the real inputs, for each build in turn. It runs gates G0 to G9, and the case 1 denominator self-check on every contributing run, the 6,225 comparator runs included. It computes no estimator. It writes only pass, or a refusal record.
- **G0 also asserts the Python and NumPy versions.** This is the class (h) detector.
  - The expected versions are literals in each reader's source: Python `3.13.12` and NumPy `2.4.4`, X2-1's phaseb environment (A4.9).
  - G0 compares `platform.python_version()` and `numpy.__version__` with them. The freeze record records the same two values.
  - The check runs in both modes and is not a mode term. This amends D:341.
- **The option at D:724 to fold `verify` into the first `read` pass is withdrawn.**
- **Every `verify` refusal is recorded** in that day's decisions record, with its event id: label, phase, time, cause, fix, and what any diagnosis agent saw. It is disclosed in the write-up.
- **The cause** is found from the label, the code and the fixtures. Real records are inspected only by a diagnosis agent under A6.6 (P4). Its `presence` is reported per component at most, as `none`, `some` or `all`, never a number or a breakdown.
- **A fix** goes through A6.4 steps 2, 3, 4, 6, 7 and 8, without locking or retirement.
  - In the first attempt nothing has been computed. The stage 1 rule allows the fix (RS:227).
  - In a later attempt, the earlier outputs are already retired. A6.4 steps 9 and 10 apply against them, under A6.4's own authority (A6.11).
  - After the fix, both builds run `verify` again under the new freeze.
- **`verify`'s time** is charged to the reading's ceiling (D:732).

## A6.4 After computation starts, before opening

**Steps 1 and 2 need no go.** They put the reading in a safe state, and nothing after them is urgent. The operator is needed from step 4 on.

1. **Stop and lock (P1).**
   - A pass already running is allowed to reach its exit, then locked.
   - No further pass starts, and nothing is opened.
   - The executor computes on X2-1 the sha256 of every file under the attempt's output and log folders: outputs, partial folders, `run_log.json`, captured streams and `refusal.json`. It records the hashes.
   - It removes read permission in place from every file except `refusal.json`, `run_log.json` and the captured streams. Those three hold no value (D:543, A1.13), and the label's disclosure is already bounded by A6.8. They stay readable, so the label and the resource peak can be read at steps 2 and 3. A captured stream is read only after A1.4's pattern check passes.
   - The interpreter records the event in that day's decisions record: its id, its source (A6.2), the time, and the hash list. The record holds names and hashes only, not sizes.
   - The lock is a tripwire against accident. It is not a barrier against the owning account.
   - The model service on X2-1 stays down. The operator stood it down permanently on 2026-11-01 and disabled it at boot (the repository's `AGENTS.md` project instructions, "The gpt-oss model server on `yotko-evo-x2` stays down"). The run records its state as on any exit. This amends the restoration of PLAN:340 and D:697 for this host.
2. **Provisional class.** The interpreter assigns one or more classes, with their evidence, in the decisions record. If several apply, the route the table puts first applies. An event that fits no class stays locked and goes to the operator, who decides.

| Class | Confirming evidence | Second check | Retire or resume | Remedy, and the steps that run | Gos |
|---|---|---|---|---|---|
| (a) reader defect | a reproducing fixture | yes | retire | builder fix; steps 3 to 10 | dispatch, commit, item 43 |
| (b) tooling defect | a reproducing fixture or the tool's negative control | yes | outputs stay locked in place if reader identities and inputs are unchanged by hash; otherwise retire | tool fix; repeat the affected tool step, or recompute if what the readers received was affected (A6.7) | dispatch, commit, item 43 if recomputing |
| (c) input defect | the input's hash against its authorized hash | yes, from the records | retire | item 42 remedy; the operator re-authorizes; steps 7 to 10 | operator's item 42 decision, item 43 |
| (d) specification or fixture defect | a reproducing fixture, or the text against REQ or the registration | yes | retire | dated addendum (conforming only; otherwise an amendment under section 13); steps 3 to 10 | dispatch, commit, item 43 |
| (e) native defect | a reproducing fixture against native code | yes | retire | to the operator under A11 and A12; a dated amendment if a registered rule is involved; a new code identity means a new reading plan | the operator's, by amendment |
| (f) operational | exit status or signal, the kernel's out-of-memory line, `run_log.json`'s resource peak | no | retire | rerun under the same freeze; steps 7 to 10. A second memory stop under the same freeze is class (a) until shown otherwise | item 43, naming the same freeze hash |
| (g) exposure | the record of who saw what | no | resume, on the operator's word: nothing is recomputed for an exposure alone | the exposed person or agent takes no part in classifying or fixing. If the exposed party is the interpreter or the executor, the event stays locked and goes to the operator, as an unclassified event does. A resume after any exposure needs the operator's word, which also says who runs and records the remaining steps. The operator decides whether the exposed party keeps a role for the rest of item 43 and at item 44. The exposure is disclosed in the attestation | the operator's word on the resume and the roles |
| (h) environment or platform | G0's version assertion, or a hardware or filesystem fault on record | yes, from the records | retire | restore the frozen environment; steps 7 to 10 | item 43 |
| (i) procedural error | the record of the error | yes, from the records | retire if a computed file used the wrong checkout, freeze or inputs; otherwise resume | correct the step; steps 7 to 10 if retired | item 43 if retired |

   **Route order, strictest first:** A6.5; then A6.4 with retirement; then A6.4 class (b) with outputs locked in place; then resume; then A6.3.
3. **Localize without values.** The stage hash ladder (A6.4a) is compared between builds or runs; the tool names only the first diverging rung and key. Then come code reading and new fixtures. A refused pass writes no ladder: localization uses the label, the code and fixtures, and A6.6's last resort if needed (P5).
4. **Confirm.** A separate second check confirms the class and its evidence, as the table requires, before any fix is run. The decisions record holds the second check's report hash. The operator then gives the dispatch go for the fix, and the record holds his words.
5. **Retire (P1),** for classes the table marks "retire".
   - The executor moves every locked file to `retired_<attempt>` beside its folder on X2-1, and re-hashes after the move against step 1's list.
   - The re-hash is an unlock use under A6.4b.
6. **Fix through the same chain as the build:**
   - **A reader defect:** a builder fix under its own brief, blind to the other build. Its new fixture expectations go into the freeze record (D:671), not an addendum, so the specification set does not move.
   - **A specification or fixture defect:** a dated addendum. It may conform the specification to REQ and the registration, and never change them. A correction that would change REQ or a registered rule stops here, for an amendment under section 13, committed before the affected output is read. The retired outputs are unread, so that route stays open until item 44.
   - **Every fix carries:**
     - new fixtures that would have caught the defect, with expected outcomes stated before the fix runs. Each is generated once, as A4.4 requires of the set;
     - a diff limited to the defect. The new freeze record lists every changed file with its reason, unchanged files keep their hashes, and the second check confirms the diff is minimal;
     - registry data changed only to conform to the registered values;
     - the second check, the repair round and the final check, then a new freeze record that names the retired reader identities and the reason;
     - where builds disagreed, the interpreter's record in the decisions record, written before the fix, of which build is right by which specification text.
7. **Inputs, the commit and the go.**
   - The run outputs, specs, family files, inventories and each arm's run or not-run status are unchanged across attempts, except what a class (c) remedy replaces. The decisions record names any such replacement.
   - The operator re-authorizes the authorized-hash document when an input defect changed it, or when a new addendum changed the specification set. The change is disclosed.
   - The fix and the new freeze record are committed as a record-only commit, with D:681's assertion that `code_identity()` is unchanged, on the operator's commit go.
   - Then an item 43 go names the freeze record's hash, with A15's pre-launch check (`AMENDMENT_A15_adopted.md:63`).
8. **Recompute.**
   - `collect` runs again whenever the authorized-hash document changed, or `collect` was defective. Otherwise the sealed collection is reused.
   - Then `verify`, the `read` passes, byte identity and the blind comparison.
9. **The anchor, per file.** The executor computes the hashes, and the interpreter makes the table. These rules hold when:
   - one build was unchanged;
   - the run outputs, specs, family files and arm statuses are unchanged;
   - the retired attempt ran in the frozen environment with no fault on record.

   After a class (h) fault, the interpreter writes the expected difference in the decisions record first.
   - **Always byte-identical between its retired and recomputed attempts:** `values.json`, `contributing_runs.json`, `incidence_per_run.json` and `LADDER.json`.
   - **Byte-identical only if the specification set, the authorized-hash document, the collection and the environment are all unchanged:** `reading.json` and `SEAL.json`. Otherwise the interpreter writes the expected difference in the decisions record before the recomputation.
   - **After a class (f) rerun,** every retired file listed in its folder's `SEAL.json` must match. A partial folder's unlisted files are not compared. The write order that makes this safe is A6.4a's.
   - **The corrected build** must equal the unchanged one on `values.json` and the comparisons.
   - The table of retired against recomputed hashes, per file and per build, is published with the reading. An unexpected mismatch is an event. When both builds changed, there is no anchor, and that is stated in the write-up.
10. **The effect of the defect (P2).** If any `values.json` hash changed between a retired and a recomputed attempt, the retired outputs are opened after item 44, as a disclosed comparison of the two, whichever way it falls.

### A6.4a The stage hash ladder, pinned

- **The file.** Each `read` pass writes `LADDER.json` in each component's folder. It is the folder's sixth file and a fifth entry in `SEAL.json`'s `files`, and it is in the byte-identity set. A refused pass writes only `refusal.json` (D:484).
- **The write order.** Every file of a component folder is written under a temporary name, fsynced and renamed into place. `SEAL.json` comes last, and is itself written the same way. This amends D:474.
- **Its bytes:** `canonical(seal(payload)) + b"\n"` with `v3.artifacts.canonical` and `seal`, where the payload is `{"schema": "a10-stage2-ladder-1", "component": "A10" | "A6", "rungs": {<rung name>: <lowercase hex HMAC>}}`.
- **The key.** K is the 32-byte digest `sha256(b"a10-stage2-ladder-1" + b)`, where b is the bytes of every contributing output of this reading component, concatenated in Python string order of `"<input component>/<job_id>"`. The input component is one of `main`, `sqrt`, `crowding`, `sigma_squared_x10` or `sigma_squared_x0.1`.
  - The reader feeds the outputs to the hash in that order as it hashes them in G4. With parse workers, the parent hashes in order.
  - K is never written. A list of output hashes cannot produce it. Anyone who can read the outputs could compute K, so the key defends against a rung value that escapes. The display rule and the lock carry the rest.
- **Each rung** is `HMAC-SHA256(K, canonical(structure))`. Before `canonical`, every float infinity becomes `"+inf"` or `"-inf"`, and every NaN becomes `"nan"`, as D:474 does for outputs.
- **The rungs:**
  - `records/<input component>`: a list, in `job_id` order, of each contributing run's flat record, a dictionary with exactly the 17 keys of D:109-119: `job_id`, `component`, `category`, `grid`, `arm`, `variant`, `rr`, `alpha`, `capability`, `kappa`, `theta`, `crowding`, `steps`, `k_star`, `g`, `final_population`, `fired`.
  - `cells/<comparison identity>`: for a boundary, `{"arm": {repr(rr): [values]}, "comparator": {repr(rr): [values]}}`. For cap*, the same with `repr(capability)` keys. Values are as passed to the helper, in `job_id` order, with bools as 0 or 1.
  - `result/<comparison identity>`: the helper's full result dictionary, with rr and capability keys as `repr`.
  - `result/<F>.survival_difference.<arm>`: the list `survival_differences` returns.
  - `incidence/<quantity>`: the native `pooled_incidence` return for that quantity.
  - The reader's own derived keys have no rung: Wilson intervals, `disclosure.*`, `family.*`, `family_error.*`, `label.*` and `family_size.*`. `values.json` is compared directly.
  - A not-run arm's quantities have no rung.
  - **Contributing runs** are the keys of `contributing_runs.json` `runs`, for K and for the `records` rungs alike. An input component with no contributing run has no `records` rung. In the `records` rung, `fired` is a JSON boolean.
- **The tool** walks rung classes in pipeline order, `records`, `cells`, `result`, `incidence`, with names in sorted order within each class. It prints only `identical`, or the first diverging rung's name. Rung values are never printed, recorded or published before item 44. Outside the file, only `LADDER.json`'s sha256 is recorded.
- **The freeze record** holds the tool's sha256. A fixture pair that differs at a known rung is the tool's negative control, run before and after any real comparison.
- **On fixtures,** ladder equality between builds is a freeze criterion (added to D:653-659).
  - L2 fixtures should include a `read` pass with an undefined point boundary and one with an infinite interval end, so that the infinity mapping is exercised. The generator screens for both and reports what it found.
  - If either is not found, the serializer is tested at L1 instead: F3's and F5's arrays go through each build's rung code under a fixed test key, and the rung values are compared between builds.
  - This amends D:571-588 and A5.10's stage G2.
- **On real inputs,** ladders are compared only after an event.

### A6.4b The unlock (P7)

- **Who and on what.** Read permission on locked files is restored only by the executor, and only for one of two:
  - a named tool whose sha256 is in the freeze record;
  - an A6.6 agent's account (P4).

  It covers only the files that tool or agent reads, and permission is removed again when it exits.
- **The record.** Each unlock is recorded in the decisions record with the file names, the tool hash or agent, and the times.
- **The named uses:**
  - step 5's re-hash;
  - step 9's table;
  - step 3's ladder tool;
  - a class (b) repeat of a tool step;
  - the remaining item 43 steps after a resume: byte identity, the blind comparison and the seal records;
  - an A6.6 agent.
- **The tools that may be named:** the lock, hash and retire script; the byte-identity tool; the A1.4 stream checker; the comparison tool; the ladder tool. Each has its sha256 in the freeze record.
- **The end of the lock.** This section governs before item 44. The item 44 go ends the lock on the files it names, and step 10's opening is under that go.

## A6.5 After opening (P3)

At this point everyone who can declare a defect knows the values.

- **The criterion.** A post-opening defect is real only if a fixture fails on the frozen build. The fixture's expected outcome must be derived from the registration, REQ or the frozen specification text, and stated before it is run. A separate second check confirms the failure from code and fixture, and is not told the direction of the effect on any verdict.
- **Who decides:** the finder reports; the interpreter classifies; that second check confirms; the operator decides.
- **Which reading governs:**
  - The corrected reading governs where the correction conforms the reader to the registration or REQ.
  - Where neither determines the point, the original reading governs. The alternative is reported, labelled as chosen after opening (RS:198).
  - No registered rule and no part of REQ can change after opening (DN:263).
- **The corrected reading** is computed by a fixed reader through A6.4 steps 6 to 9, opened under its own go, and published beside the original with the difference explained. Builders stay blind to the opened values while they fix.
- **Both components open under one go, at one time.**
- **For reader, tooling and specification defects,** the runs are unaffected. A native defect follows class (e).

## A6.6 Diagnosis agents, the last resort and the terminal rules (P4, P5, P6)

**A diagnosis agent (P4)** may read real run outputs before item 44, under these conditions:
- the operator gives a go for that diagnosis;
- the interpreter dispatches it, and it runs on X2-1 in its own folder with mode 700;
- its working files and transcript are sealed there, and their hashes are recorded;
- its final message is fixed to the constant `report written`;
- it takes no later role as builder, checker or fixer.

**For a rerun under the last resort,** it may run a patched copy of a reader inside its own folder, never the frozen tree. The copy is sealed with its working files.

**Its report** is a file, `DIAGNOSIS.json`, which a validator reads before anyone else does. The validator is a script whose sha256 is in the freeze record. The report must hold exactly these fields:
- `schema`: `a10-stage2-diagnosis-1`;
- `event_id`: A6.2's id;
- `component`: `A10`, `A6` or `both`;
- `class`: a list of A6.4's class letters;
- `presence`: `none`, `some`, `all` or `not_applicable`;
- `fields_involved`: a list drawn only from this set:
  - the 17 flat-record keys of A6.4a;
  - `job`, `code_hash`, `status` and `output_hash`;
  - `steps`, `final_population`, `survived_threshold_30`, `population_path`, `fixture_tables` and `yield_events`;
  - `diagnostics.time`, `diagnostics.population`, `diagnostics.capability`, `diagnostics.allocation_evaluated`, `diagnostics.survival_first` and `diagnostics.unavailable_rules`;
  - `continuation_availability.allocation_steps` and `a13_decision_incidence`;
- `specification_clause`: `D:<n>` or `A<k>.<n>`, optionally followed by one letter (as in `A6.4a`), which the validator checks exists in the specification set;
- `code_location`: `<build>/<file>:<line>`, which the validator checks is a file in the freeze record's source list with that line present.

No other field and no free text is allowed. A failing report is not read, and is rewritten.

**The last resort (P5),** for a disagreement, a refusal or a non-identity that survives the ladder, code reading and new fixtures:
- **A disagreement between builds:** one diagnosis agent reads the differing keys in both builds' sealed outputs.
- **A refusal or a within-build non-identity:** one diagnosis agent reruns the failing pass as above.

The write-up states what it saw.

**The terminal rules (P6),** for when the last resort fails. The operator declares the search failed and chooses:
**The terminal cases apply per component.** A6.5's single go still opens both components.

**A comparison's group** is its row of D:494 or D:495, with those keys' `incidence*` and `disclosure` keys. The descriptive keys of D:496-497 belong to no group.

- **Both builds completed and each is reproducible:**
  1. continue, within the ceiling, or past it under a dated budget amendment;
  2. open both readings together. Every comparison with any differing key in its group carries `verdict: "undetermined"`, with reason `builds disagree`, and shows both builds' values.
     - A differing key outside every group is reported by name, with both values.
     - A hash-only difference in `contributing_runs.json` or `incidence_per_run.json` marks every quantity of that component `undetermined`, unless a differing `incidence.*` key localizes it.
     - The marking is made in the write-up; the sealed files stand as written.
     - A verdict assigned later under A6.5 is labelled `resolved after opening`.
     - This overrides D:555's pass criterion. The registration does not require two builds to agree; that is this specification's control.
- **One build has no reading,** because it refused or its two runs were not reproducible:
  1. continue;
  2. open the completed, reproducible build's reading alone. It is labelled `single build; the other refused at <label>` or `single build; the other was not reproducible`, with the loss of independent confirmation stated.
- **Neither build has a reading:** continue.

## A6.7 Tools and redundancy

- **A tooling defect** follows class (b).
  - A `collect` defect needs a recomputation, because the collection hash is sealed in `SEAL.json` (D:482).
  - An item 43 wrapper defect needs the affected steps repeated. If it affected what the readers received, the attempt is recomputed.
- **Negative controls:** the comparison tool and the ladder tool each report a difference on a fixture pair known to differ, before the real comparison and again after it.
- **Redundant channel:** no build writes an extra key, in either mode. D:503's allowance is withdrawn. So the two builds' `values.json` sha256 values are equal exactly when the tool says `identical`. Any disagreement between the two is an event.

## A6.8 Bounded disclosure before opening

Each item below goes only to the interpreter, the operator and, where named, the fixing builder. Each is listed in the write-up.

- **Differing key names, and the first diverging rung.** Which build is right is decided from the specification text and written before the fix (A6.4 step 6). The write-up lists the names and each defect's trigger condition.
- **The changed-or-unchanged bit.** Whether a component's `values.json` hash moved after a fix says whether the real data reached the defect's trigger. It cannot be removed, and it is stated.
- **Refusals after computation started.** Each builder lists every label its reader can emit after computation starts, and says whether its trigger can depend on an outcome value. The freeze record carries the list. The write-up states any such refusal.
- **Timing:** one wall time per pass, in whole minutes, in `run_log.json`. No time per phase or per comparison. This replaces D:538 and A1.13's "times".
- **Diagnosis reports:** their `presence` values and clauses.
- **The public commit of a fix:** it shows that the real data reached a defect's trigger. It tells no decision-maker anything new.
- **Sizes:** retirement records hashes, not sizes.
- **The attestation** reads: "no sealed output was opened and no value displayed, by anyone, before item 44". It then names every diagnosis agent and any class (g) exposure, and lists what was inferable under this section.

## A6.9 Budget

- **The ceiling.** Past 12 h, the only route is a dated budget amendment, committed before the recomputation. No automatic draw is made on the 36 h contingency (`AMENDMENT_A15_adopted.md:62`; APPROVALS section 4). The registration's section 6 choice (restated at `AMENDMENT_A15_adopted.md:64`) cannot apply a seed reduction to a reading: the seed counts are gate terms (A3.5 row 2).
- **The arithmetic.** One attempt is budgeted at 2.5 to 5.5 h (D:724), so the 12 h ceiling holds two to four attempts.
- **Charged to the ceiling:** every attempt; `verify` passes; locking, unlocking and retirement; diagnosis agents' X2-1 time.

## A6.10 Residuals, stated

- **A defect shared by both builds** is invisible to the comparison, the byte identity and the ladder. It rests on fixtures and on reading the code and the specification. Its causes would be the one specification, the one fixture set, the shared native helpers, and two model builders whose misreadings can be correlated.
- **When both builds change in a cycle,** there is no anchor.

Both are accepted, and stated in the write-up.

## A6.11 Records and supersessions

**This addendum supersedes:**
- D:556's last sentence;
- RS:227's limit to fixes before computation, for the reason that outputs stay sealed and are retired unopened. This is the authority for A6.3's fixes in a later attempt;
- D:724's fold option, and A1.15's pointer to it;
- D:482 and D:549, by `LADDER.json`;
- D:503's extra-key allowance;
- D:538 and A1.13, by per-pass whole-minute times;
- D:555, by A6.6's terminal option;
- D:653-659, by the ladder freeze criterion;
- D:663-676, by the post-computation label list, the environment versions, and the sha256 of the validator, the comparison tool, the ladder tool, the byte-identity tool, the A1.4 stream checker and the lock, hash and retire script, all in the freeze record;
- D:341, by G0's version assertion (A6.3);
- D:474, by the write order (A6.4a);
- D:571-588 and A5.10, by the L2 infinity requirement (A6.4a);
- D:697 and PLAN:340, for X2-1's model service (A6.4 step 1);
- D:698, by the negative controls, the redundant channel and the ladder comparison in the item 43 sequence;
- A4.4, by fixtures added in a cycle.

**Every freeze record, the first included, states:**
- that this addendum's procedures were fixed on 2026-11-22, before any stage 2 reading computation, with no stage 2 output opened;
- that sealed, unopened stage 2 run outputs existed when it was made, which departs from REQ:56's letter ("before stage 2 results"), as A1.15 disclosed;
- for a later freeze, that an earlier attempt had been computed and retired unopened. That is a further departure from REQ:56's letter;
- A6.1's departure from REQ section 3's letter;
- the operator's adoption of P1 to P7, with its date.

The first public record of this addendum is the reader's commit.
