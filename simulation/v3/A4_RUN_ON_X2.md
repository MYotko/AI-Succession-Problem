# A4 validated continuation support: run on X2, 2026-09-29

Use a clean checkout of the operator-approved A4 commit. A4 supersedes A3;
`v3/table_compatibility_A3.json` is not used and the A3 repair stage does not
run. Run every command from `simulation/`. The model server is down for the
whole run; the X2 launch wrapper handles `llm down` and `llm up`.

## Staging (exact paths)

- Place the read-only A1 root at `simulation/v3/runs/registered_A1`, containing
  `v3_rerun_tables_A1.json` (file SHA256
  `56db71633a0f4710692e3354e3bc2fb5829286abbfa59e61609bd3f8cf6fcb3c`),
  `tables_A1_manifest.json`, and `tables_A1/table/{outputs,records}/`.
- Copy the a3_probe records (about 62 MB) to the X2 at
  `simulation/v3/runs/a3_probe` (or any readable path you pass to
  `--a3-probe-root`); they carry the 855 D26 probe seeds.
- Place the unchanged calibration at
  `simulation/v3/runs/registered/v3_rerun_calibration.json`.

A4 reads the A1 files and never rewrites them.

Create `v3/runs/registered/A4_pin.json` with `commit` equal to the actual
approved A4 commit, `path` equal to `simulation/diagnostics/v3_rerun_design_note.md`,
and `sha256` equal to the SHA256 of that committed file's exact bytes. No
guessed commit or hash is supplied.

## Prepare the sealed plan

```text
python -B -m v3.table_validation_a4 prepare v3/runs/registered_A1 v3/runs/registered/v3_rerun_calibration.json v3/runs/registered/A4_plan.json --pin v3/runs/registered/A4_pin.json --wall-hours 48 --a3-probe-root v3/runs/a3_probe
```

`--a3-probe-root` must point at the staged a3_probe records and expose the 855
D26 probe job seeds; prepare refuses a missing or empty root.

`prepare` computes M and M_FV from every A1 job output (primary and sensitivity,
any status), pins them in the plan, and asserts every validation stream seed is
pairwise distinct and disjoint from the A1, the 855 D26 probe seeds (from the
a3_probe records) and the planning seeds, halting on any collision. It refuses a
missing or empty probe root. It builds the five phased job lists and records a
per-phase memory estimate. It launches nothing.

## Launch through the production runner

```text
export PATH=$HOME/.local/bin:$PATH   # llm lives here; a non-interactive shell lacks it
python -B -m v3.production_runner launch v3/runs/registered/A4_plan.json v3/runs/registered/A4_run --profile x2 --workers 31 --threads 1 --cpu-budget 32 --mode normal
```

The runner acquires the service lease, runs `llm down`, runs the measured
configuration test for each phase (each timing tasks of that phase's own kind,
shortened in length only), then dispatches the phases in order: fit (plain),
validate plain, validate FV primary, validate FV doubled-population (a separate
phase because its tasks need about 19 GB; the six doubled-length FV jobs run
here too), then census. The A4 stream seeds travel in each job's config; the
runner's own job seed is unused. One numerical thread per worker.

The configuration test measures each phase's memory cap first, with nothing
running, and a capped phase tests only the listed worker counts at or below its
cap, plus the cap itself: at about 121 GB available, 7 for FV doubled-population,
8, 12 and 14 for FV primary, and every listed count for the plain phases and
census. Each round runs two tasks per tested worker. The whole test is
expected to take about 10 minutes, with a 30-minute ceiling. The X2 is dedicated
to this project, so launch in normal mode.

**Worker count.** Dispatch runs the smaller of `--workers`, the live
`--max-workers` control, the mode cap (normal `budget - 1` = 31, work
`budget - 4` = 28 on a 32-CPU budget), the configuration-test choice, and the
per-phase memory cap. `--workers 28` is only a ceiling. Each phase's cap is
fixed once at phase start as `floor(0.8 x MemAvailable / per-task estimate)`
(it is not recomputed from live MemAvailable, which already excludes running
tasks); a task is not started while MemAvailable is below 1.2x its estimate. At
about 121 GB available the estimates and caps are: FV doubled-population/
doubled-length 13.4 GB -> 7 workers; FV primary 6.7 GB -> 14; plain fit/validate
up to 3.35 GB -> above the CPU optimum, so the configuration test's choice
governs; census about 0.1 GB -> the mode cap. The estimates are anchored on a
measured peak: the heaviest FV primary task peaked at 5.56 GB (2026-09-29), plus
a 20% margin. Do not raise `--workers`
expecting more; the memory cap governs. A completed task's peak RSS can only
raise its phase estimate (never lower it), which only lowers the cap for the
rest of that phase.

**Projection.** Before each phase the runner projects the remaining work
(each job scaled by its own population x length, the per-phase worker count, and
one nondeterminism recheck; the cleanup reserve is already in the deadline) and,
if it will not fit the remaining 48-hour budget, stops before that phase and
records the gap. On the real plan the projection is about 37.5 hours.

Live mode control:

```text
python -B -m v3.production_runner control v3/runs/registered/A4_run --mode normal
python -B -m v3.production_runner control v3/runs/registered/A4_run --max-workers 16
python -B -m v3.production_runner status v3/runs/registered/A4_run
```

Durable completion records and resume: rerun the same launch command with the
same root; completed stage outputs are reused, only missing ones run, and the
projection then covers only the remaining work against the remaining budget.
`llm up` runs on every exit path.

After each phase the runner re-executes one completed task (a seeded pick among
the phase's shortest) in a fresh spawned worker and compares result hashes,
recording `<phase>/nondeterminism_check.json`. A mismatch writes
`<phase>/nondeterminism_failure.json` and halts. The run also halts on a flow or
value outside `[lower, upper]`, a seed collision, an A1 source-hash mismatch, or
the memory guard finding MemAvailable below 1.2x the estimate with no task
active.

**What to do:**
- **Projection stop** (`reason: projection_exceeds_budget` in the return, and a
  `projections` entry in `launches.json`): the remaining work will not fit the
  remaining 48-hour budget. Stop and report the gap to the reviewer. Do not
  start a fresh root with a larger `--wall-hours`; that reuses no completed work
  and breaks A4's 48-hour ceiling. The operator decides the next step.
- **Refused resume** (`incompatible resumption`): the plan or code changed since
  the root was created. Do not delete the root. Use a fresh root with the plan
  that matches the committed code, or investigate the change.
- **Memory-guard halt**: MemAvailable stayed below 1.2x the estimate with no
  active task. Free memory on the shared machine and resume the same root, or
  lower `--max-workers`; if the estimate itself is wrong, report it.
- **Nondeterminism halt** or any value/seed/source halt: a finding. Inspect the
  durable outputs and events; do not retry blindly.

## Publish

Only after every phase completes:

```text
python -B -m v3.table_validation_a4 publish v3/runs/registered/A4_plan.json v3/runs/registered/A4_run v3/runs/registered_A1 v3/runs/registered/v3_rerun_calibration.json v3/runs/registered/v3_rerun_tables_A4.json
```

The publisher verifies the pinned A1 publication, the registration pin, the
calibration hash, the pinned M and M_FV, and every stage output's identity (A1
job, stream seed, code identity, plan hash), refusing any mismatch. It rebuilds
each row's status from A1's own screens (route, flow half-width, half-window
drift, held-out coverage, fixed-point convergence) plus A4's two conditions
(nonempty validated support and the availability floor); it assembles primary
and sensitivity rows separately and recomputes the sensitivity contrasts. It
keeps each retained A1 row's producer identity, stores C0 once per plain row,
prunes plain entries to the validated non-population-0 cells, and writes a
sealed `v3_rerun_tables_A4.compatibility.json` receipt binding the new hash,
both producers, the seeds, M, M_FV, the plan hash and every stage output hash.
The target is frozen: it refuses to overwrite existing published bytes. The
family must load through `require_production`; a single not_estimable row keeps
registered dispatch closed and is reported. Preserve the receipt with the
table; both travel together.

## Report

```text
python -B -m v3.table_validation_a4 report v3/runs/registered/v3_rerun_tables_A4.json v3/runs/registered/v3_rerun_report_A4.json
```

Writes `v3_rerun_report_A4.json`: per-tier cell counts and visit shares
(certified/unresolved/violation and the safeguard for plain; passed/unresolved/
violation for FV, labelled "asymptotic, not certified"), every plain cell that
fails the visit-weighted safeguard, every violation, each row's floor result,
and FV collapse effects. It carries no survival, extinction or fire rate.

## What to send back

- The A4 plan file and the full run root (durable stage outputs, records,
  leases, events, configuration measurements).
- `v3_rerun_tables_A4.json` and its sibling `.compatibility.json` receipt.
- The per-tier report: counts of certified, unresolved and violating cells and
  their shares of visits; the plain cells that fail the visit-weighted
  safeguard; every violation as a finding; each row's census floor result
  (fractions and assessed flags only, never raw endpoint counts); M and M_FV;
  and the measured configuration and wall time. No survival, extinction or fire
  rate.
- Any halt: the condition, the job, and the durable evidence.

Never load the family with `--validation` or fixture modes for registered use.
The A4 lookup and stage-dispatch edits changed `v3/production_tables.py` and
`v3/production_runner.py`; the A2 compatibility record's approved boundary was
re-pinned to their A4 hashes, with an `a4` note, so the loader and
`gates.verify_instrument` accept the A4 instrument while still refusing any
unapproved change.
