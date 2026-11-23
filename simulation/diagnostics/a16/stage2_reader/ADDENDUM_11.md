# Addendum 11 to the stage 2 reader specification (2026-11-23)

**Applies to** the draft (`3ac0f425…5822`) as amended by Addenda 1 to 10, Addendum 10 in its specification-set text (`13295613…37f5`). Where it differs from them, it governs. Draft lines are cited `D:n`, addendum sections `An.m`.

**Source:**
- the operator's decision of 2026-11-23, recorded by the interpreter: "approve A6.2 addition, keep A6.4a, sigma inventories at 93a453b2";
- the question of what A10.3b's form test covers (A11.2).

Round 1 found no difference between the builds on any criterion of D:653-659 or A10.9 item 5. This addendum changes no output that round 1 compared.

**Labels:** [R] read from the cited text; [I] inferred, with the reasoning stated.

## A11.1 A refused pass writes only `refusal.json` (amends A10.3c and A10.3d; restores A6.4a and A6.4 step 3)

**The decision.** The operator approved A10.3d's addition to A6.2 item 1. A6.2 item 1 reads, as A10.3d states: "`verify` refuses, `collect` refuses, or the two collection folders of A10.3d differ;".

The operator kept A6.4a as adopted [R], and with it A6.4 step 3 [I: the operator named A6.4a; Addendum 10 had amended the two together]:
- A6.4a: "A refused pass writes only `refusal.json` (D:484)".
- A6.4 step 3: "A refused pass writes no ladder".

**Withdrawn from Addendum 10:**
1. In A10.3c, the two sentences "A refused pass writes `<out>/refusal.json`. A component folder whose `SEAL.json` was written before the refusal stays, and is listed in the event record (A6.4 step 1)."
2. In A10.3d's Events paragraph, the two sentences from "A10.3c also amends two sentences of A6.4" through "is hashed and locked at A6.4 step 1." The paragraph keeps its first two sentences, and its last sentence now reads: "No other text of Addendum 6 changes, beyond A6.4 step 8 as above."
3. In the A10.3 heading's list of what it amends, "A6.4 step 3" and "A6.4a". The heading's list now reads: "(amends D:277-287, D:341, D:482, D:484, D:531, D:698, A6.2 item 1 and A6.4 step 8)".
4. In "What this addendum does", the words "and amends A6.4a's and A6.4 step 3's refused-pass sentences".

**The rule, in their place.**
1. **Nothing is published before everything has passed.** A `read` writes no file under `<out>` until three things hold:
   - every gate of G0 to G9 has passed;
   - every computation of every component it was asked for has completed without a refusal;
   - the change-detection re-hash (D:275) has passed.

   That holds with one component named or with `--component both`. G3's sealed temporary file (D:352) is written outside `<out>`, in the process's temporary directory; it is not a file under `<out>` for this rule, and the map reaches `<out>` only as `contributing_runs.json` at publication.
2. **Publication.** Only then does the reader publish: each component folder, in A6.4a's write order within the folder, then `<out>/run_log.json`. Under `--component both`, `A10/` is published before `A6/`. No success line (D:540) is printed before `run_log.json` is in place.
3. **A refusal before publication** leaves `<out>` holding exactly `refusal.json`, as A6.4a states, whichever component the refusal arose in.
4. **A failure during publication** is the one way a refused pass can leave more than `refusal.json`. It covers an exception raised while a file under `<out>` is written, fsynced or renamed. The reader deletes nothing under `<out>`, temporary files included [I, from D:474's "written once and never replaced"]. Whatever folder the failure leaves, partial or complete, is hashed, locked and listed at A6.4 step 1, and a partial folder's unlisted files are not compared (A6.4 step 9). The reader writes `refusal.json`, with phase `after_computation_started`, and prints its refusal line (A1.4, A10.3c).
5. **A pass that is killed or interrupted** leaves what it leaves. It is an A6.2 item 3 event, and A6.4 step 1 locks what is there. The reader adds no signal handling for this rule.
6. **`verify`** is unchanged: on pass `verify.json`, on refusal only `refusal.json` (A10.3c).

**The reason.** This is the operator's decision. A6.4a's "only `refusal.json`" and step 3's "no ladder" hold for every refusal the reader decides. Item 4 is the one exception: a fault of the file system or the process, which adopted A6 already expects (A6.2 item 3, A6.4 steps 1 and 9). It can leave a sealed `A10/`, with its `LADDER.json`, beside `refusal.json`. No reader can rule this out. It is stated here for the operator's acknowledgement before the freeze. A reader that holds its outputs until every check has passed cannot leave a sealed component beside a refusal for any cause in its inputs.

**What it costs [I].** Holding both components' outputs in memory before writing adds their size to the peak. The six files are written from structures the reader already holds after computation, and they are small next to the parsed inputs. This is a judgment, not a measurement; the throughput and memory probe of D section 8.2 step 6 measures the peak with this rule in force. A pass that does not publish leaves no `run_log.json`. A6.4's class (f) evidence for it is the exit status, the signal and the kernel's out-of-memory line.

**Fixture expectations changed:** none. No fixture reaches a refusal inside `read`, because every refusing fixture expects phase `input_verification` [R, the packaged manifest], and every gate runs in `verify` (A10.3b).

**Tests each builder adds:**
- a `read --component both` in which a refusal is injected after the first component's computation and before publication. It must leave `<out>` holding only `refusal.json`, and print the refusal line and no success line;
- a publication failure injected when `A6/`'s first file is renamed into place. `<out>` must then hold `A10/` with its six files, `A6/` with no file under any of the six names of D:476-482 and A6.4a, `refusal.json` with phase `after_computation_started`, and no `run_log.json`. Temporary files in `A6/`, and `refusal.json`'s `reason_class` and `exception_class`, are the build's own and are not compared (A6.4 step 9, D:658). No success line may be printed.

## A11.2 What `collect`'s "form" covers (clarifies A10.3b)

**The question.** A10.3b defines form as: strict JSON; the top-level key set; the four family names under `arms`; each arm's key set for its status; the `comparator` and `comparator.family` key sets and the evidence key sets; and the value types in those places. It does not name four structures:
- an arm's `family` key set;
- the `a16` block's shape;
- `registration`'s key set;
- an `excluded_roots` entry's key set.

The text already says "Every other test of the document ... belongs to `verify`." Whether that sentence covers these four is the question ruled here.

**The ruling.** It does. The list of A10.3b's "Form" bullet is exhaustive. `collect` tests no key set it does not name, and tests none of the four structures above beyond what A10.3a item 5 requires for leaves: a string, a `null`, or a refusal for any other value. Each of the four is tested by `verify` and by `read`, at phase `input_verification`.

Two tests reach inside these structures, because A10.3b needs them:
- where `excluded_roots` is a list, `collect` requires each element to be an object whose `path` is a string and an absolute path; any other element refuses at form. `collect` tests nothing else inside an `excluded_roots` entry;
- an arm `status` other than `run` or `not_run` refuses at form.

**The reason.** It is the literal reading of A10.3b. Pinning it removes the one way two readers could differ in which command first refuses a malformed document [I: phase and collection bytes are already fixed by A10.3; only the first refusing command could differ].

**Fixture expectations changed:** none. D:658 fixes the phase and the fact of refusal, and every `collect` and `verify` refusal has phase `input_verification` (A10.3b). The ruling can move only which command first refuses.

## A11.3 Recorded decisions with no reader change

- **Item 42's inventories (A10.5 item 4).** The operator decided that the two σ inventories are made from a checkout at code identity `93a453b2…`, as the comparator inventory was. A reader enforces this through A10.5 item 1 and needs no change. The inventories themselves still need the operator's go when item 42 is reached.
- **A6.2 item 1.** As in A11.1. A reader is unaffected; the item 43 record applies it.

## A11.4 The specification set and the fixtures (amends A10.9 item 1)

1. The specification set has twelve documents. At the next regeneration, each fixture document's `specification_set` gains `ADDENDUM_10.md` and then `ADDENDUM_11.md`, each at the sha256 of its specification-set text, by A9.6's procedure. No per-fixture list hash moves for this.
2. Round 2 runs on the existing builder package, with A10.7's erratum applied by each builder when it evaluates F08a and F08b, as in round 1.

## A11.5 The rulings

| # | Question | Ruling | Fixture expectations changed |
|---|---|---|---|
| A11.1 | A refused `read` under `--component both` | Nothing is published before every gate, every component's computation and the D:275 re-hash have passed; a refusal before publication leaves only `refusal.json`. A6.4a and step 3 stand as adopted for every refusal the reader decides; a publication fault is the one exception, for the operator's acknowledgement | None |
| A11.2 | The four structures A10.3b's form does not name | Tested by `verify` and `read`, never by `collect`, apart from `excluded_roots[].path` and the arm `status` value | None |
| A11.3 | Item 42's inventories; A6.2 item 1 | Recorded; no reader change | None |
| A11.4 | Specification set | Twelve documents at the next regeneration | None |

**What no ruling changes.** No ruling touches the registry, a filter, a cell, a seed, a resample count, a helper call or `pooled_incidence`. So no computed value, ladder rung, `quantities` list, `values.json` key or `incidence_per_run.json` byte changes. Nothing is added under `simulation/v3/` or at the top level of `simulation/`, so `code_identity()` stays `93a453b2…f161da`.
