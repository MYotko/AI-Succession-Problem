# Addendum 9 to the stage 2 reader specification, version 2 (2026-11-22)

**Applies to** the draft (`3ac0f425…5822`) as amended by Addenda 1 to 8 (Addendum 6 at version 5, `6d6ea4a3…ec13`; Addendum 8 final, `a795fb12…1dff`). Where it differs from them, it governs.

**Source:** the interpreter's decisions on the five recommendations of the G2 repair round, `fixtures\g2_repair\G2_REPAIR_REPORT.md` (`a1d199e2…7cc1`), section 10, and on its gap 3. Two are reader pins that two blind builders could implement differently; the rest settle generator-side choices. Version 2 applies the check of version 1 (`fixtures\g2_repair_check\REPORT.md`, NOT SOUND narrowly), adopting its replacement text, and then the confirming check of version 2 (`spec_checks\addendum9_confirm\REPORT.md`, NOT CONFIRMED narrowly), adopting its replacement text for A9.3 and A9.6.

## A9.1 The A16 error statement's key (amends D:519)

For an A16 family with `rounds_used > 0`, the statement D:519 names is the value of the key `family_error.<name>.statement`, the string `"at least 1 - alpha(1 + P/M), given the fitted family"` exactly. The nominal family carries no `statement` key (A3.4).

## A9.2 `claims_conditional_on_violations` (amends A1.5 and A2.7)

In `disclosure.<quantity>`, `claims_conditional_on_violations` is `true` exactly when `disclosure_rows` is not empty, and `false` when it is empty (A2.7's empty case).

## A9.3 Inventories keep their descriptive keys (amends A8.6 item 4)

A8.6 item 4's dropping of keys outside a pinned set applies to three kinds of file, whose key sets are pinned: the authorized-hash documents (A8.1), the closeout records (A8.2), and the `inputs.json` blocks (A8.3).

An inventory has no pinned exact key set, so a fixture inventory may keep `reader_fixture: true` and its descriptive blocks (A8.10 item 34). The reader reads these inventory keys and ignores every other key:
- the subset of D:248-256, with the `published_files_and_inputs` keys that A2.10, A3.6 and A8.3 add;
- INV-S's `failed_attempt.{path, not_run_reason}` (D:205, D:299);
- the comparator inventory's `registration_pin` (A2.10, A3.6), which A1.6 compares with the comparator spec's recorded pin in registered mode. In fixture mode the pin terms are not applied (A3.5 row 7).

The reason recorded for an excluded root (D:535) is the inventory's `failed_attempt.not_run_reason` (D:299). The `reason` in `inputs.json`'s `excluded_roots` is neither recorded nor compared.

## A9.4 The overall hash's form (amends A8.1)

The fixture set's overall hash is `v3.artifacts.digest` of the dictionary the fixture manifest holds as `overall_hash_inputs`, as its `overall_hash_definition` states. The freeze record cites that definition, the hash, and the packaged manifest's sha256.

## A9.5 F13a2's records are accepted as hand-written (amends A8.6 item 1)

F13a2's round-2 admission record and latched family record are named fabrications: native records of root `a16r2` altered by hand. The altered admission record's `classifications` block no longer matches its residual rows. No reader rule reads that block. A native round-2 refusal is not required.

## A9.6 The fixture documents list ten documents (amends A8.6 item 4)

- **The change.** Each fixture document's `specification_set` gains `ADDENDUM_9.md` at its final sha256, as its tenth entry. The generator recomputes `specification_set_digest` and re-seals each document.
- **What else it updates.** Every file that carries a document's hash or size:
  - each `fixture.json`;
  - the packaged manifest and the full manifest: their `specification_set` and digest; per fixture, `authorized_hashes_sha256`, `control_files["AUTHORIZED_HASHES_FIXTURE.json"]`, `bytes` and `fixture_json.sha256`; `overall_hash_inputs` and `overall_hash`;
  - the package README and its source;
  - both copies of `SHA256SUMS.txt`.
- **What does not move.** The per-fixture list hashes, and every other fixture file. No model run is needed.
- **Also.** At the same regeneration, F12e's `expected_outcome.binder_checks_expected_to_fail`, in its `fixture.json` and in both manifests, gains `g2.seeds_distinct`. The duplicated job repeats its seed, and D:349 requires seeds pairwise distinct. The generator's `g2.seeds_distinct` check tests that seeds are pairwise distinct across the specs read, and the binder is rerun, so F12e's `binder` record and the manifest's `binder` block agree with the declared list. This changes no other fixture's record.
- **Order.** `ADDENDUM_9.md` is final before the regeneration starts.

## A9.7 Generator records in the packaged manifest (amends A8.6, "What a builder receives")

The packaged manifest may carry the generator's value-free records:
- `run_roots`, with its per-run extraction facts;
- `tamper_variants`;
- `families.*.checks`;
- `reproducibility`;
- `estimator_archive`;
- each fixture's `binder` block.

They are part of the builder package, and both builders receive the same records. A8.6 withholds the generator's `work_copy\` files, not facts the packaged manifest restates. The four `screens` keys of A8.6 item 3 stay out of the package.

## A9.8 The closeout record's `canonical_run_roots_checked` (amends A8.2)

The field holds the two canonical run roots of A2.9 as strings relative to `simulation/`: `v3/runs/a10_stage2/runs/<family>` and `v3/runs/a10_stage2/<family>/runs_run`. These are the roots, not A2.9's `*/records/` patterns. The reader does not test its value.
