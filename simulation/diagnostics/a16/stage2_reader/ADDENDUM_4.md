# Addendum 4 to the stage 2 reader specification (2026-11-22)

**Applies to** `STAGE2_READER_SPEC_DRAFT.md` (`3ac0f425…5822`) as amended by Addenda 1 (`f1a26843…f103`), 2 (`74f7c0a6…2edc`) and 3 (`e6602478…`). Where it differs from them, it governs.

**Source:** the interpreter's decisions on the fixture generator pilot, `fixtures\pilot\PILOT_REPORT.md`, verdict FEASIBLE WITH CHANGES. Section A4.n answers the pilot's section 6.n. Code facts were confirmed at `4dcc18c2` by the interpreter, or are labelled as the pilot's measurements.

## A4.1 Fired reviews: a fixture guard-authority adapter (amends F6, A1.14 and the L2 fixtures generally)

- **The finding.** It was confirmed in code: `ExecutionGuards.authorize` admits a succession only when `fixture` is true or `authority` is set (`guards.py:38`). A registered-shaped table has `fixture: false` (`integration.py:363`). `authority` is set only for a registered run (`integration.py:115-126`) or inside an A11 proof (`production_runner.py:267-276`). So no succession is admitted in a non-registered run against a registered-shaped table. The pilot saw 26 attempts refused and 0 fires.
- **The decision: option (b).**
  - In fixture roots only, the generator authorizes successions through A19's proof mechanism, `compatibility_a10.proof_authority`, read at `production_runner.py:273`. It sets the mechanism's state so that each fixture run's guards carry an authority bound to that run's job id, exactly as a proof rerun's guards carry its producing run's authority.
  - This makes fixture runs decide succession as registered runs do, which is the behaviour the reader will meet in real outputs.
- **Bounds:**
  - It is set only inside the generator's process, in a standalone fixture root, never in a repository checkout and never in a reader.
  - It applies to every fixture run, arm-shaped and comparator-shaped alike, so both sides of a fixture comparison decide alike.
  - The fixture manifest names the adapter per root and per job.
  - The reader sees only outputs, and its gates are unchanged.
- **What it buys:** F6's fired-review condition and A1.14 stand. At least one L2 cap* fixture must show fire rates that are not degenerate on either side. The pilot's probe gave 8 firing runs of 14, with 10 fired reviews and every denominator matching.

## A4.2 FV rows: a declared forced-route subset (adds to A3.2)

At the cheap setting, the native `auto` route chose plain on every job (the pilot's measurement; `offline_estimator.py:196-197`).
- **The rule.** The generator may set `config["route"] = "fv"` on a declared subset of table jobs, re-make each with `stable_job`, and run the native estimator, which then takes its own FV route.
- **The subset:** the jobs of the rules at odd index in the rule class, 12 of 25, as in the pilot. The fixture manifest names it.
- Row keys do not depend on the route, so families stay full-key. The pilot measured this.

## A4.3 Additions to the minimum fabrication list (adds to A3.3)

16. the forced `route` of A4.2, a job field;
17. `screens`, `primary_status`, `primary_reason` and `sensitivity.passed`, as fields a hand-set status entails. `sensitivity.contrasts` stays native, so a row can read `passed: true` over failing contrasts, and the manifest says so. No loader reads the contrasts (the pilot's reading);
18. `fv_label: "asymptotic, not certified"` on estimated FV rows of every family, labelled ones included, as A4 writes it (`table_validation_a4.py:652`). This replaces A3.3 item 3's "of a no-label family";
19. `manifest.validated_continuation` and `manifest.source_family`;
20. the admitted row's whole `a4` block, and for the nominal shape its `a13` marker;
21. for the nominal shape, an A13 public record (because `receipt.a13_round.public_file_sha256` needs a file), and the placeholder digests under `receipt.refusals.original` (because a fixture has no original refused candidate);
22. the guard-authority adapter of A4.1, named per root and per job.

## A4.4 Reproducibility (amends A1.1's fixture list hash and A1.10)

- **The finding.** Table manifests hash whole estimator outputs, and those carry timing fields (`study.py:176`; `offline_estimator.py:244-246`). So a fresh estimator pass gives different table bytes from the same rows. The pilot measured this for the rows and outputs, and inferred it for the table.
- **The rule.**
  - The fixture set is generated once.
  - Its estimator outputs are archived with it.
  - The fixture list hash covers the built files.
  - Only the build from the archived outputs is required to reproduce byte for byte, which the pilot showed: 29 of 29 files identical across two roots.

## A4.5 Path strings in round records

- The native A13 and A14 round records hold absolute paths. Fixture round records hold label strings (`fixture-root:/simulation/…`) instead, so that a root and its twin agree.
- **The reader compares no path string held inside a round record or a round's admission record**, in either mode. Real records hold X2-1 absolute paths. The reader binds these records by file hash, seal and the fields A1.3, A2.1, A2.6 and A3.4 name.

## A4.6 Richer tables, for variety in the counts (replaces A3.2's "cheapest setting")

- **The finding.** At the cheapest setting, rows held one to five continuation entries. The ordinary and survival-first denominators were 25 and 475 in 19 of 24 full runs (the pilot's measurement).
- **The concern.** Constant counts would let a counting defect pass the fixtures unseen.
- **The rule.** The full generation uses setting S2: groups 3, runs per group 8, burn 0, measure 200. It gave 8 to 19 entries per row at 2 to 3.5 s per job in the pilot's probe. That adds about 5 CPU-hours over the cheap setting, the pilot's inference.
- **Required variety.** Across F6's runs, each derived denominator takes at least three distinct values per branch.
- **If S2 does not give that,** the generator reports it before generating further, with the setting it would need.

## A4.7 Real committed records in the export (amends A2.2)

`git archive … simulation` brings the real committed identity records of nominal and sqrt, and other tracked files under `v3/runs`, into each fixture root. The fixture identity records are meant to replace them in the copy.
- The generator never reads the real records' contents.
- It removes from each fixture root every tracked file under `v3/runs/` that no fixture needs, and lists what it removed. The real records stay intact in the repository and the pristine export.

## A4.8 Sidecars

Fixture cell-results sidecars follow the native form: primary rows and the sensitivity settings' rows. The pilot's held primary rows only.

## A4.9 Environment, closed

X2-1's phaseb environment reads Python 3.13.12 and NumPy 2.4.4 (`~/miniforge3/envs/phaseb/bin/python3.13`). The interpreter read it on 2026-11-22 at 05:10:46Z, a read-only session under one second with no runner alive. That equals the pilot's WS-1 WSL phaseb environment, so A3.7's version check is closed.

## A4.10 Build plan time (replaces A3.8)

The figures below are budget estimates, resting on the pilot's measurements:
- **Estimation at S2:** about 5 to 8 CPU-hours across the five family shapes, under an hour of wall time at 15 workers.
- **Fixture runs:** about 157 s per 500-step run at 15 concurrent, the pilot's mean. A 284-run root is about 12.4 CPU-hours and 50 minutes of wall time. With the twin root and the variants, about 27 to 45 CPU-hours, or 2 to 3 hours of wall time.
- **Fixture generation, with its second check:** about two working days elapsed.
- **The whole build:** about six working days to the freeze.

## A4.11 Small items

- **WSL working files.** Generator scripts are staged inside the generator's own WSL folder, never at `~/x.sh` (the pilot did this already).
- **Native lock files.** Those left beside fixture records, such as `….a14_round.admission.lock`, are not fixture files. They are excluded from the fixture list hash.
- **Disk.** The pilot's WSL folder (`~/v3_wsl/reader_fixture_pilot/`, 8.0 GB) stays until the full generation reuses or replaces it. Its removal is the operator's call.
