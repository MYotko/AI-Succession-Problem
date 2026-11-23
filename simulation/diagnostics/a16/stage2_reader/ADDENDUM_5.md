# Addendum 5 to the stage 2 reader specification (2026-11-22)

**Applies to** the draft (`3ac0f425…5822`) as amended by Addenda 1 to 4. Where it differs from them, it governs.

**Source:** the interpreter's repairs on the second check of the pilot and Addendum 4, `fixtures\pilot_check\REPORT.md`. That check found the pilot SOUND and Addendum 4 NOT SOUND as written. A5.n answers its finding n. The interpreter confirmed the code facts at `4dcc18c2`:
- `proof_authority` returns `None` silently when the job id differs, and tests only that the producer is not `None` (`compatibility_a10.py:143-146`);
- `_eligible` takes the ordinary or survival-first split from the protection period's cohort certificate, which reads ages and welfare, never the tables (`integration.py:159-168`, `:227-239`).

Everything else is the check's measurement or reading, and is labelled so where it matters.

## A5.1 Incidence coverage by defect class, and an L1 derivation fixture (replaces A4.6's "Required variety")

- **The finding.** In every case 1 run measured, 43 in all, the ordinary steps were exactly steps 0 to 24. The split comes from the cohort certificate, so no table setting moves it. Three cheap mis-derivations matched the record in 11 of 14 runs, and a hard-coded 25 matched in 43 of 43 (the check's measurements). A variety rule is the wrong detector.
- **F6's required conditions.** Its manifest names a run for each, and its test asserts each:
  - (a) a run with at least ten absorbed steps, whose extinction step is not a multiple of ten;
  - (b) a run with a fired review;
  - (c) a run with a held review;
  - (d) a case 1 run whose ordinary count is not 25.
- **The screen for (d).** The generator screens up to 100 runs for it. Comparator-shaped (linear `g`) seeds come first, since σ-shaped runs gave 50 in 2 of 10. Then sqrt- and crowding-shaped seeds. The generator reports what it found.
- **New fixture F17, L1, the derivation.** `L1_ARRAYS.json` gains hand-built per-run `diagnostics` and `yield_events` lists, with the expected derived denominators stated in the file. Each builder's section 4.4 code must reproduce them exactly. The lists cover:
  - an ordinary count other than 25;
  - absorbed steps after an extinction at a step that is not a multiple of ten;
  - held and fired reviews;
  - a review skipped for want of a successor, and one at the deadline exit;
  - survival-first steps on both sides of a protection period;
  - a run whose ordinary plus survival-first equals `allocation_steps` only when the `allocation_evaluated` condition is applied.

  F17 is required whether or not the screen finds (d).
- **Setting S2, stated fully:** groups 3, runs per group 8, particles 8, burn 0, measure 200. Its purpose is continuation availability and fire coverage. The check measured unavailable rules per step falling from about 21 of 25 to 3.2, and firing runs rising from 8 of 14 to 12 of 14. It does not give variety in the ordinary count. The pilot's probe file calls this setting "S3".

## A5.2 The guard-authority adapter, pinned (amends A4.1's bounds)

1. `_proof_producer` is set to `code_identity()` exactly, never another value. A non-running value would also widen `read_identities` (`compatibility_a10.py:117-126`).
2. Both context variables are set inside the worker process, around one native `worker` call. They are set in nested `try/finally`, as `_execute_proof` does (`compatibility_a10.py:174-197`), and are `None` afterwards. A parent process never sets them before forking.
3. **Before each call,** the wrapper asserts that `proof_authority(job)` returns a value other than `None` for that job. A miss is an error, not a silent un-adapted run.
4. **After each root,** the generator records the count of yield events with `local_gate_authorized` false. Insufficient votes can still give such an event legitimately. Any nonzero count is reported with the job ids, and the second check re-counts it.
5. The fixture manifest is the only record of the adapter, because outputs carry no trace of it. The manifest names it per root and per job.

## A5.3 Copied values are distinct (adds item 23 to A3.3)

Some hand-chosen values are copied by the reader into its own output keys. Every such value is distinct from every other such value in the same record:
- in the A14 fixture record, `E` differs from `E2`, `P` from `M`, and `tests_round1` from `tests_round2`, for example 20, 17, 19 and 13, with `P` not equal to `M`;
- the same rule applies to the A16 fixtures and to every fixture whose values feed `family.*` or `family_error.*` keys.

That way a transposed field shows as a difference.

## A5.4 Fixture manifests in the A4 field set (amends A4.4)

- **Each fixture table's manifest is built in the A4 publication's field set,** as `table_validation_a4.py:816-822` builds a fresh one. It is not the A1 assembly manifest patched. It has no `input_output_hashes`, and it carries what A4 writes, including `design.amendment`.
- `source_family.file_sha256` hashes the archived native assembly file. Table bytes are then reproducible from the archived assembly.
- "Generated once" still holds, because run outputs carry timing in their envelope: `seconds`, `started_epoch`, `finished_epoch`, `peak_rss_bytes` and `runtime`.
- Estimator outputs carry four timing fields, not three: `scoring_seconds_by_k_star` (`offline_estimator.py:235-236`) as well as those at `:244-246`.
- F7's "equal in every field" means the output's `result`, compared by the native `comparison_bytes`.

## A5.5 Fixture rows keep the A1 row form, and builders read only D:219's fields (adds item 24 to A3.3)

- Fixture rows are A1-form rows with the named status changes. Real A4 rows carry `a4` on every row, `a1_reason`, `a1_primary_reason`, `c0` on plain rows, and no `reason` key when estimated (`table_validation_a4.py:631-669`, as the check read it).
- The fixture manifest names the absent A4 fields and the retained A1 fields.
- With no C0, fixture lookups at population category 0 go by exact bin (`production_tables.py:262-264`). That changes fixture run behaviour, not anything a reader reads.
- **Binding on both builders:** a reader reads row fields only through `ProductionTables`, and only the fields of D:219. A build that reads any other row field is a defect.

## A5.6 F7's arm is crowding-shaped (amends F7)

A σ shape has 625 rows and cap 0, so the native binding refuses the twin's one admitted row. F7's arm is therefore crowding-shaped, with 2,875 rows and cap 2, and the twin's binding is native.

## A5.7 A16 records hold label path strings too (extends A4.5)

A4.5's two rules extend to the A16 round records, round-reference records and family records:
- fixture records hold label strings, not absolute paths;
- the reader compares no path string inside them.

The native A16 writers assert real path strings (`validation_extension_a16.py:646`, `:1268`, as the check read them). Where an assertion blocks a native write in a fixture root, the generator writes the record by hand with label strings, as a named fabrication.

## A5.8 Removing real records from the export (replaces A4.7's second bullet)

- The export carries three committed identity records: nominal, sqrt and crowding. It also carries 87 other tracked files under `v3/runs`, 22 of them under `registered/` (the check's count).
- The generator removes, from each fixture root, every tracked file under `v3/runs/` that no fixture needs, and lists them. The parent calibration at `v3/runs/registered/v3_rerun_calibration.json` stays.
- Afterwards it re-asserts `code_identity()`, repeats the family checks, runs one run per family, and reports any native read of a removed file.

## A5.9 Smaller corrections

- **Citation:** the read in A4.1 is `production_runner.py:274`. `:273` is the import.
- **The fixture manifest** of the full generation holds the per-file and per-field fabrication list in machine-readable form, not only in a prose document.
- **Job tag:** fixture jobs carry tag `validation` and real ones `v3_rerun` (`tables_a10.py:239`). That keeps fixture job ids and seeds apart from real ones. It is not a mode term, because the reader tests no tag value.
- **Null exposure:** at least one fabricated violation cell has `exposure: null`, so that A2.7's null-as-0.0 rule is exercised.
- **The pilot's run table** reads "10, in 8 runs" for family 1, not 7. That is the check's count. The pilot report is kept as written; this correction is recorded here.

## A5.10 Staged generation

The fixture generation proceeds in two stages, each with a separate second check.

- **G1, the remaining shapes and the hard cases:**
  - an A16-scope family, crowding-shaped and admitted after round 1, built as natively as A5.7 allows, for F13(e) and F14(d);
  - the crowding-shaped and σ0²×0.1-shaped families at S2;
  - the F6 screen of A5.1;
  - `L1_ARRAYS.json`, with F1 to F5 and F17;
  - the cleaned roots of A5.8;
  - the adapter of A5.2.
- **G2, the full set:** F1 to F17 with every variant of Addenda 1 to 5; both fixture roots and the twin; run specs and root manifests; inventories; the fixture authorized-hash document; the machine-readable fixture manifest; and the fixture list hash.
