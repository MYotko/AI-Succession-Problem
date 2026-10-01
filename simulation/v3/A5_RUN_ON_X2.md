# A5 plain-law certification labels for FV tables: run on X2, 2026-09-29

A5 is label-only. It reads the sealed A4 publication and tests every validated
support cell of every primary FV `estimated` row on independent plain
trajectories, writing a sealed label record. It never changes the A4 family, the
reruns' behavior or any row status.

## Placeholders (define once)

```text
export A4CO=$HOME/v3_a4
```

- `A4CO` (`$HOME/v3_a4`) : the existing A4 checkout, holding the completed A4 run
  and its staged read-only inputs.
- `A5CO = ~/v3_a5` : the new, separate A5 checkout this run uses.
- `A5COMMIT` : the operator-approved A5 implementation commit.

The A4 artifacts are read read-only from `A4CO` by absolute path:

- A1 records:        `$A4CO/simulation/v3/runs/registered_A1`
- D26 probe records: `$A4CO/simulation/v3/runs/a3_probe`
- A4 plan:           `$A4CO/simulation/v3/runs/registered/A4_plan_3.json`
- A4 run root:       `$A4CO/simulation/v3/runs/registered/A4_run_3`
- A4 family:         `$A4CO/simulation/v3/runs/registered/v3_rerun_tables_A4.json`
  and its two siblings `v3_rerun_tables_A4.compatibility.json` (receipt) and
  `v3_rerun_tables_A4.cell_results.json` (sidecar). All three travel together.

(If the A4 run used a different numbered root or family path, substitute it once
here.)

## The A5 checkout

A5 has its own code identity by design, so it runs from a separate checkout at
the implementation commit:

```text
git -C ~/v3_a4 fetch
git worktree add ~/v3_a5 A5COMMIT
cd ~/v3_a5/simulation
```

Run every command from `~/v3_a5/simulation`. The A5 run root, plan and pin all
live under `~/v3_a5`. The model server is down for the whole run; the X2 launch
wrapper handles `llm down` and `llm up`.

The calibration is tracked, so it is already present in the checkout at
`v3/runs/registered/v3_rerun_calibration.json`; nothing needs staging for it.

## The committed identity record

The A4 post-run sequence commits the A4-family identity record at the fixed
repository path `simulation/v3/runs/registered/A4_family_identity.json`, in the
record commit that precedes `A5COMMIT`, so it is tracked and present in `~/v3_a5`.
It is a plain JSON object with six fields:

```json
{
  "family_file_sha256": "<sha256 of v3_rerun_tables_A4.json bytes>",
  "table_seal_sha256":  "<the family document inner seal, read(family)['sha256']>",
  "receipt_file_sha256":"<sha256 of the .compatibility.json bytes>",
  "sidecar_file_sha256":"<sha256 of the .cell_results.json bytes>",
  "producing_commit":   "<the commit that published the A4 family>",
  "code_hash":          "<the A4 family producer code hash, read(family)['payload']['code_hash']>"
}
```

A registered `prepare` requires exactly this repository path, requires the file
to be tracked, and requires its bytes to equal `git show HEAD:<path>`. It halts
otherwise, and halts on any mismatch between these values and the A4 files, the
receipt fields, or the A4 census stage output hashes in the receipt.

## Confirm the reruns are finished and not to be resumed (no overlap)

Launch A5 only after the registered reruns are finished and not to be resumed.
A5's `llm up` on exit would restart the model server, and `service.lock` is per
checkout so it would not block a rerun in another checkout, which must not happen
mid-run. Check first that no runner is live in any checkout (the bracket keeps
pgrep from matching its own command line):

```text
pgrep -af '[v]3[.]production_runner' || echo 'no live production_runner; safe to launch A5'
```

Proceed only when that prints the safe message.

## Prepare the sealed plan

First create the registration pin `v3/runs/registered/A5_pin.json`, with `commit`
equal to `A5COMMIT`, `path` equal to
`simulation/diagnostics/v3_rerun_design_note.md`, and `sha256` equal to the
SHA-256 of that committed file's bytes. Then:

```text
export PATH=$HOME/.local/bin:$PATH   # llm lives here; a non-interactive shell lacks it
python -B -m v3.table_labels_a5 prepare \
  $A4CO/simulation/v3/runs/registered/v3_rerun_tables_A4.json \
  $A4CO/simulation/v3/runs/registered/A4_run_3 \
  $A4CO/simulation/v3/runs/registered/A4_plan_3.json \
  $A4CO/simulation/v3/runs/registered_A1 \
  v3/runs/registered/v3_rerun_calibration.json \
  v3/runs/registered/A4_family_identity.json \
  v3/runs/registered/A5_plan.json \
  --pin v3/runs/registered/A5_pin.json --wall-hours 24 \
  --a3-probe-root $A4CO/simulation/v3/runs/a3_probe
```

`prepare` verifies the A4 family, receipt and sidecar against the committed
identity record; verifies the A4 plan against the receipt and the A1 manifest
(plan hash, per-job stream seeds, A1 seeds); verifies the A4 census stage outputs
against the receipt; requires the canonical A1 file hash and a non-fixture A4
family; refuses any `--wall-hours` other than 24; builds the tested set, per-row
widths and M from the A4 values before any A5 data; asserts the global seed guard
(halting on any collision, and asserting the 756 A5 seeds are pairwise distinct);
and writes the sealed plan. It launches nothing.

## Launch through the production runner

```text
python -B -m v3.production_runner launch v3/runs/registered/A5_plan.json v3/runs/registered/A5_run \
  --profile x2 --workers 31 --threads 1 --cpu-budget 32 --mode normal
```

`--workers 31` is the normal-mode cap (`budget - 1` on a 32-CPU budget), so the
configuration test's measured 24 can win, while 32 is dropped because it exceeds
the cap; the memory cap the runner computes (about 2.3 GB per task) still governs.
The runner acquires the service lease, runs `llm down`, runs the measured
configuration test (tasks of the real workload, length-shortened only), projects
the single phase against the 24-hour budget and stops before it if it will not
fit, dispatches `a5_fvplain` (756 tasks, about 950 s each), and after the phase
re-executes one completed task in a fresh worker and compares result hashes. The
A5 stream seeds travel in each job's config; the runner's own job seed is unused.
One numerical thread per worker. `llm up` runs on every exit path.

Live mode control, status and resume are as for A4:

```text
python -B -m v3.production_runner control v3/runs/registered/A5_run --mode work
python -B -m v3.production_runner control v3/runs/registered/A5_run --max-workers 12
python -B -m v3.production_runner status  v3/runs/registered/A5_run
```

Resume by rerunning the same launch command with the same root; completed stage
outputs are reused and only missing ones run.

**Halts and what to do:**
- **Projection stop** (`reason: projection_exceeds_budget`): stop and report the
  gap; do not raise `--wall-hours`. The operator decides.
- **Refused resume** (`incompatible resumption`): the plan or code changed; do not
  delete the root; investigate.
- **Memory-guard, nondeterminism, or any value/seed/A4-hash halt**: a finding.
  Inspect the durable outputs and events; do not retry blindly.

## Publish and report

Only after the phase completes:

```text
python -B -m v3.table_labels_a5 publish v3/runs/registered/A5_plan.json v3/runs/registered/A5_run \
  $A4CO/simulation/v3/runs/registered/A4_run_3 \
  $A4CO/simulation/v3/runs/registered_A1 \
  v3/runs/registered/v3_rerun_calibration.json \
  v3/runs/registered/v3_rerun_labels_A5.json

python -B -m v3.table_labels_a5 report v3/runs/registered/v3_rerun_labels_A5.json \
  v3/runs/registered/v3_rerun_report_A5.json
```

`publish` re-verifies the A4 identity, the A1 source, the calibration, the code
identity, the plan hash, M and the 24-hour ceiling; takes the census hashes from
the re-verified receipt; asserts 252 FV tables and 756 stage jobs; combines the
replicates; classifies each tested row-cell; writes the sealed label record with
the exact strings "certified under the plain law" and "asymptotic, not certified";
asserts the classified cell count equals M; refuses to overwrite a published
record; and asserts the A4 family, receipt and sidecar bytes are unchanged.
`report` writes per-row and pooled totals, the visit and census shares, and every
violation with its exposure. Neither carries a survival, extinction or fire rate.

## Where the label record lives

The label record carries a per-cell entry for all M tested cells. At M in the
hundreds of thousands, each entry is roughly 150 to 200 bytes of canonical JSON,
so the sealed record can reach about 80 to 100 MB, near GitHub's 100 MB file
limit. Estimate it before committing: the A4 plan's counts bound M (M is at most
the A1 published FV cells of the primary rows).

Therefore:
- The **label record** `v3_rerun_labels_A5.json` stays on the X2, with a
  workstation backup, identified by its SHA-256. It is not committed.
- The **A5 report** `v3_rerun_report_A5.json` is small and is committed.
- A **hash record** (the label record's SHA-256, plus M, the A4 identity and the
  plan hash) is committed too, as A4's receipt is, so the uncommitted record's
  identity is provable.

## What to send back

- The A5 plan file, the registration pin, the committed identity record, and the
  full A5 run root (durable stage outputs, records, leases, events, configuration
  measurements, `nondeterminism_check.json`, `launches.json`).
- The A5 implementation commit, `git -C ~/v3_a5 rev-parse HEAD`.
- `v3_rerun_labels_A5.json` (the sealed label record) with its SHA-256, kept on
  the X2 with a workstation backup; and the committed hash record.
- The A5 report: per-row and total counts of certified, unresolved and violating
  cells; the share of plain-law visits in certified cells; the pooled share of
  living census endpoints in certified cells; every violation with its exposure;
  M; and the measured configuration and wall time. No survival, extinction or
  fire rate.
- Any halt: the condition, the job, and the durable evidence.

A5 never loads the A4 family through the production loader. The only boundary
change is `production_runner.py`, re-pinned in `table_compatibility_A2.json` with
an `a5` note, so the loader and `gates.verify_instrument` accept the A5 instrument
while still refusing any unapproved change.
