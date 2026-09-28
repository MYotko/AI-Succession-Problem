# A2+A3 launch on X2, 2026-09-28

Use a clean checkout of the operator-approved combined A2+A3 commit.
Do not resume the old wrapper into its A1 rerun step. That step was paused
before dispatch; no registered rerun manifest, job or output existed
when these amendments were written. The genuine A1 publication fails
the registered table check (717 not_estimable rows, 671 primary and 46
via sensitivity) and is not usable for registered reruns.

Run commands from `simulation/`. Preserve the complete read-only A1 root
at `v3/runs/registered_A1/`, containing `v3_rerun_tables_A1.json`,
`tables_A1_manifest.json`, and `tables_A1/table/{outputs,records}/`.
Place the unchanged calibration at
`v3/runs/registered/v3_rerun_calibration.json`. Its file SHA256 is
fd86358a39e3b643fb9adc4e81a2372915ca50a1866e9b0e330a874b41746e01.

Create `v3/runs/registered/A2_A3_pin.json` with `commit` equal to the
actual approved combined commit, `path` equal to
`simulation/diagnostics/v3_rerun_design_note.md`, and `sha256` equal to
the SHA256 of that committed file's exact bytes. No guessed commit or
hash is supplied. The reviewed unpinned manifest must not be launched.

Prepare the read-only diagnosis and the adopted hardest-first repair:

```text
python -B -m v3.a1_screen_diagnosis v3/runs/registered_A1 v3/runs/a1_screen_diagnosis/audit.json
python -B -m v3.table_repair_a3 prepare v3/runs/a1_screen_diagnosis/audit.json v3/runs/registered_A1/tables_A1_manifest.json v3/runs/registered/v3_rerun_calibration.json v3/runs/registered/tables_A3_manifest.json --pin v3/runs/registered/A2_A3_pin.json --source-root v3/runs/registered_A1
python -B -m v3.production_runner launch v3/runs/registered/tables_A3_manifest.json v3/runs/registered/tables_A3 --profile x2 --workers 28 --threads 1 --cpu-budget 32 --mode work
```

Before service shutdown or configuration testing, launch checks the
fixed family latch and scans durable completed jobs across its recorded
roots. Only a family with no failure proceeds. The launch acquires the
service lease, runs `llm down`, and measures the
configuration test in that state before scientific dispatch. Test mode
includes up to 32 workers; work mode caps launch at 28, normal at 31.
The fastest feasible measured configuration is used, with the existing
5-percent preference for fewer workers. `llm up` runs on success, failure
or interruption. Do not stand the service down outside this lease.
The deadline charges both prior families, leaving at most 65,227 seconds
for the repair, configuration and cleanup. The current projection is
8.611 additional dispatch hours, 14.825 cumulative hours; it is not a
measured guarantee at the enlarged populations.

The 67 job IDs, seeds and exact calibration argument are pinned in
`simulation/v3/table_compatibility_A3.json`. Use the literal calibration
argument shown above; `./v3/...` and other equivalent spellings are refused.

On the first failing row, original/new contrast or completed sensitivity
pair, dispatch stops and in-flight jobs are interrupted. Inspect
`tables_A3/table/screen_failure.json` and the durable events. Completion
records survive. The family latch at
`simulation/v3/runs/A3_families/<policy-digest>/failure.json` prevents
resume and publication from any run root. The policy digest is the
SHA256 of the compatibility policy's canonical JSON. A new root does
not reset the family. Do not delete it or retry the
scientific family. A normal operational interruption without a screen
failure may resume using the exact same manifest, root and command.

Only after all 67 jobs complete without failure, publish through the
provenance-verifying tool, then prepare and launch the reruns:

```text
python -B -m v3.table_repair_a3 publish v3/runs/registered/tables_A3_manifest.json v3/runs/registered/tables_A3 v3/runs/registered_A1 v3/runs/registered/v3_rerun_calibration.json v3/runs/registered/v3_rerun_tables_A3.json
python -B -m v3.study rerun --pin v3/runs/registered/A2_A3_pin.json --calibration v3/runs/registered/v3_rerun_calibration.json --tables v3/runs/registered/v3_rerun_tables_A3.json --output v3/runs/registered/reruns_A2_A3_manifest.json
python -B -m v3.production_runner launch v3/runs/registered/reruns_A2_A3_manifest.json v3/runs/registered/reruns_A2_A3 --profile x2 --workers 28 --threads 1 --cpu-budget 32 --mode work
```

The publisher checks all original and replacement completions, settings,
seeds, provenance and screens. Failed rows never produce the final
publication. Preserve the sibling `v3_rerun_tables_A3.compatibility.json`
with the table: its seal binds the exact new bytes and both source
families. Missing receipts or re-stamped tables are refused. Run from
the committed pin that includes A2 and A3. Later commits can load the
table only when that producer is an ancestor and the full code identity
is unchanged. No compatibility screen is relaxed.
Use a new rerun root and the new committed pin. These are not A1 resumes.

After the complete rerun family, build the index and run the standalone
gates. Substitute the full hash printed by the index command:

```text
python -B -m v3.gates index v3/runs/registered/reruns_A2_A3 --a2-pin v3/runs/registered/A2_A3_pin.json --output v3/runs/registered/reruns_A2_A3_gate_index.json
python -B -m v3.gates --phase all --calibration v3/runs/registered/v3_rerun_calibration.json --a2-pin v3/runs/registered/A2_A3_pin.json --evidence-manifest v3/runs/registered/reruns_A2_A3_gate_index.json --evidence-sha256 FULL_SHA256_PRINTED_BY_INDEX --output-dir v3/runs/registered/gates_A2_A3
```

Never use `--validation` or `--fixtures` for registered results. Copy gate
reports to diagnostics only at the results commit. D23's zero-fire G3.3
exception applies only to R2 fire-rate citation. D24's censored ordering
and G4.2 testability rules do not waive any defined separation or support
threshold. The full result family must supply every other required check.
