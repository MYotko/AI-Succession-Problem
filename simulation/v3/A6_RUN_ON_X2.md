# A6 sensitivity and convergence: run on X2, 2026-09-30

Use a clean checkout of the operator-approved A6 implementation commit. Run every
command from `simulation/`. A6 adds new `*_a6*.py` modules only; it changes no
existing file that enters the code identity, and asserts this against the rerun
commit before any registered launch. The model server is down for every batch;
the X2 launch wrapper handles `llm down` and `llm up`.

**The A6 ceiling is 90 X2-equivalent hours (amendment A7, decision D34).** The
honest planned total is about 82 X2-equivalent hours, now within the ceiling, so
the first registered projection does not refuse. The planned total may still
exceed the ceiling after any future estimate change, in which case the projection
refuses and the operator chooses a budget amendment or a uniform seed reduction.
Confirm it up front:
`python -B -c "from v3 import budget_a6 as b; print(round(b.planned_total_hours(),1), 'X2-equivalent hours; ceiling', b.PROGRAM_CEILING_HOURS, 'exceeds:', b.planned_total_hours() > b.PROGRAM_CEILING_HOURS)"`.

## 0. Environment

Export every variable the steps below read, before step 1 uses them:

```text
export RERUN_COMMIT=<the approved rerun commit hash>
export A6_LEDGER=v3/runs/a6/A6_budget.json
export A6_LOG=v3/runs/a6/A6_consumption.jsonl
export A6_REGISTRY=v3/runs/a6/A6_seed_registry.json
export PATH=$HOME/.local/bin:$PATH   # so llm is on PATH on the X2
```

The order is: variant calibrations, then the three variant table families
(estimation, validation, publication), then the runs. The weight-corner and
horizon arms run in the rerun checkout; the crowding and sigma arms run at A6's
implementation identity. The variant families may run during the reruns on a
machine established as bit-identical to the X2, otherwise after them.

**Sequencing and code identity.** The A6 design-note text is committed
separately, **before the rerun pin**, so the sensitivity grids cannot be chosen
after the main results are seen. The A6 implementation code is committed **after
the rerun commit**, and its commit **precedes** A5's implementation commit,
because A5 edits `production_runner.py` and `table_compatibility_A2.json`, both
rerun-path files. If A6 were committed after A5, its checkout would carry A5's
edits and the rerun-path invariance check against the rerun commit would fail. A6
therefore always runs from its own checkout at its own commit (the rerun commit
plus the new `*_a6*.py` modules only), and asserts invariance against the rerun
commit at every step (variant calibrations, family estimation and validation, and
every run spec).

**The A6 budget (A7): 90 X2-equivalent wall hours.** One total of 90
X2-equivalent wall hours (amendment A7, D34; `budget_a6.PROGRAM_CEILING_HOURS`)
covers the whole A6 program. `budget_a6.build_ledger()` holds a fixed planning
estimate for each component, built from the committed measurements:
`<family>_tables_estimation` and `<family>_tables_validation` for each of the
three families, `nominal_runs`, and one run component per variant arm
(`crowding_runs`, `sigma_squared_x10_runs`, `sigma_squared_x0.1_runs`).
Consumption is an append-only JSONL log, separate from the ledger;
`budget_a6.load(ledger, log)` replays it, and building a ledger over an existing
one refuses. Before each launch, `budget_a6.project(ledger, component, machine,
workers)` projects the component's planning estimate rescaled to the machine and
workers (effective workers capped at the plateau, 16 on the X2, 12 x 0.37 on WSL)
plus that launch's configuration-test and cleanup reserve, and refuses (raises)
when the consumed time plus this projection plus the planning estimates of every
component not yet run would exceed the ceiling. The runner wall ceiling for the
launch is `budget_a6.runner_ceiling_hours(ledger, component)` = the ceiling less
the consumed time and every later component's estimate, so a component uses only
slack no other needs and the total can never pass the ceiling. Every estimation
spec, A4 validation plan and run spec takes its wall from this ceiling, never A4's
48-hour default. Build the ledger once:

```text
python -B - <<'PY'
from v3 import budget_a6
budget_a6.write_ledger("v3/runs/a6/A6_budget.json", budget_a6.build_ledger())
print(budget_a6.build_ledger()["planning_hours"])
PY
```

Record each launch's measured wall afterward with
`budget_a6.append_consumption("v3/runs/a6/A6_consumption.jsonl", <component>,
<hours>)`; the entry is written before any check that might raise.

**When a launch hits the runner's hard stop** (its wall ceiling), the runner
stops it (`projection_exceeds_budget` or the wall deadline). Per A6, the operator
decides between a budget amendment and a uniform seed reduction across the arms'
cells; the batch resumes only in a new launch within the remaining budget.

## 0. Staging (exact paths, all read-only inputs)

- The 50 registered calibration outputs at a readable path, for example
  `simulation/v3/runs/registered_calibration_outputs/` (each a runner envelope
  whose `result` is a trajectory record).
- The frozen calibration at `simulation/v3/runs/registered/v3_rerun_calibration.json`.
- The read-only A1 root at `simulation/v3/runs/registered_A1` (as for A4).
- The a3_probe records at `simulation/v3/runs/a3_probe` (the D26 probe seeds).
- The nominal A4 tables at `simulation/v3/runs/registered/v3_rerun_tables_A4.json`
  (published at the A4 code identity; A5 adds plain-law labels only and does not
  change the table identity; needed only in the rerun checkout).
- The sealed main rerun manifest at
  `simulation/v3/runs/registered/reruns_manifest.json` (the 24,900 rerun jobs) and
  the rerun design-note pin at `simulation/v3/runs/registered/rerun_pin.json`.

Set `RERUN_COMMIT` to the approved rerun commit hash. Every registered A6 step
takes `a1_source_root=v3/runs/registered_A1`, a non-empty
`probe_root=v3/runs/a3_probe`, and the sealed `rerun_manifest` from
`reruns_manifest.json`; there is no fallback, and the family's own root is never
substituted for the A1 source root.

## 1. Rerun-path invariance (before anything registered)

```text
python -B -c "from v3.sensitivity_a6 import assert_rerun_path_invariant as a; import os; print(a(os.environ['RERUN_COMMIT']))"
```

This asserts every source-manifest file except the new `*_a6*.py` modules is
byte-identical (LF-normalized) to the rerun commit. It halts on any mismatch.

## 2. Variant calibrations

```text
export RERUN_COMMIT=<approved rerun commit>
python -B - <<'PY'
import json, os
from v3 import calibration_a6 as c6
frozen = json.load(open("v3/runs/registered/v3_rerun_calibration.json"))
targets = {"sigma_squared_x10": "v3/runs/registered/v3_rerun_calibration_sigma_x10.json",
           "sigma_squared_x0.1": "v3/runs/registered/v3_rerun_calibration_sigma_x0p1.json"}
print(c6.seal_variants("v3/runs/registered_calibration_outputs", frozen, targets,
                       rerun_commit=os.environ["RERUN_COMMIT"]))
PY
```

`seal_variants` requires the rerun commit in registered mode (it asserts
rerun-path invariance first, and never overwrites an existing variant with
differing bytes). The self-check must report "reproduced frozen values exactly".
Each variant seals at A6's code identity with a re-derived epsilon_N and every
other value frozen. If the self-check halts, stop and report; do not proceed.

### 2b. The one A6 seed registry (first A6 step)

Compute every A6 seed from the configurations and seal the registry, before any
A6 simulation. Every later step asserts its own seeds against it.

```text
python -B - <<'PY'
from v3 import sensitivity_a6 as s6
from v3.artifacts import atomic_json, read, seal, unseal
rm = unseal(read("v3/runs/registered/reruns_manifest.json"))
family_cals = {"crowding": "v3/runs/registered/v3_rerun_calibration.json",
               "sigma_squared_x10": "v3/runs/registered/v3_rerun_calibration_sigma_x10.json",
               "sigma_squared_x0.1": "v3/runs/registered/v3_rerun_calibration_sigma_x0p1.json"}
run_paths = {"nominal": ("v3/runs/registered/v3_rerun_calibration.json", "v3/runs/registered/v3_rerun_tables_A4.json"),
             "crowding": ("v3/runs/registered/v3_rerun_calibration.json", "v3/runs/registered/v3_rerun_tables_crowding.json"),
             "sigma_squared_x10": ("v3/runs/registered/v3_rerun_calibration_sigma_x10.json", "v3/runs/registered/v3_rerun_tables_sigma_x10.json"),
             "sigma_squared_x0.1": ("v3/runs/registered/v3_rerun_calibration_sigma_x0p1.json", "v3/runs/registered/v3_rerun_tables_sigma_x0p1.json")}
reg = s6.build_seed_registry(family_cals, run_paths, a1_source_root="v3/runs/registered_A1",
                             probe_root="v3/runs/a3_probe", rerun_manifest=rm)
atomic_json("v3/runs/a6/A6_seed_registry.json", seal(reg))
print({"total_seeds": reg["total_seeds"]})
PY
```

Pass `seed_registry=unseal(read("v3/runs/a6/A6_seed_registry.json"))` to every
`estimation_spec`, `prepare_validation` and run-spec call below, so each step
asserts its own seeds equal the registry.

## 3. The three variant table families

For each family, do estimation, then assembly, then A4 validation, then
publication. The families and their calibrations:

- **crowding**: calibration `v3/runs/registered/v3_rerun_calibration.json`
  (sigma0^2 unchanged), source root `v3/runs/a6/crowding`, 237 table jobs.
- **sigma_squared_x10**: calibration
  `v3/runs/registered/v3_rerun_calibration_sigma_x10.json`, source root
  `v3/runs/a6/sigma_x10`, 131 table jobs.
- **sigma_squared_x0.1**: calibration
  `v3/runs/registered/v3_rerun_calibration_sigma_x0p1.json`, source root
  `v3/runs/a6/sigma_x0p1`, 131 table jobs.

Create `v3/runs/registered/A6_pin.json` with `commit` equal to the approved A6
implementation commit, `path` equal to
`simulation/diagnostics/v3_rerun_design_note.md`, and `sha256` equal to that
committed file's exact bytes.

### 3a. Build the estimation spec (also the A4 source manifest)

```text
export RERUN_COMMIT=<approved rerun commit>
python -B - <<'PY'
import os
from pathlib import Path
from v3 import tables_a6 as t6
from v3.artifacts import atomic_json, read, seal, unseal
FAM = "crowding"; CAL = "v3/runs/registered/v3_rerun_calibration.json"; SRC = "v3/runs/a6/crowding"
from v3 import budget_a6
ledger = budget_a6.load(read("v3/runs/a6/A6_budget.json"), "v3/runs/a6/A6_consumption.jsonl")
rm = unseal(read("v3/runs/registered/reruns_manifest.json"))
reg = unseal(read("v3/runs/a6/A6_seed_registry.json"))
spec = t6.estimation_spec(FAM, CAL, read("v3/runs/registered/A6_pin.json"),
                          ledger=ledger, rerun_commit=os.environ["RERUN_COMMIT"],
                          a1_source_root="v3/runs/registered_A1", probe_root="v3/runs/a3_probe",
                          rerun_manifest=rm, seed_registry=reg)
Path(SRC).mkdir(parents=True, exist_ok=True)
atomic_json(SRC + "/tables_A1_manifest.json", seal(spec))
print({"family": FAM, "jobs": len(spec["jobs"]), "wall_hours": spec["a6_wall_share_hours"]})
PY
```

`estimation_spec` takes the wall ceiling from the ledger's
`crowding_tables_estimation` component (asserts rerun-path invariance, runs the
global seed check and the registry assertion, requires the A1 source root, a
non-empty probe root and the rerun manifest with no fallback, and rejects any
settings override). Repeat for each sigma family (its calibration path and source
root); each takes its own `_tables_estimation` component.

### 3b. Configuration test, projection and launch the estimation

Stand the model server down first (`export PATH=$HOME/.local/bin:$PATH; llm
down`). Launch through the unchanged production runner with the mode cap as
`--workers`; the runner's own configuration test times candidates (8, 12, 16, 24,
32) at one numerical thread per worker and selects the fastest within the cap
(preferring the smaller within 5 percent). Before launching, project against the
budget and refuse if it would exceed the A6 ceiling (A7, 90):

```text
python -B -c "from v3 import budget_a6; from v3.artifacts import read; print(budget_a6.project(budget_a6.load(read('v3/runs/a6/A6_budget.json'), 'v3/runs/a6/A6_consumption.jsonl'), 'crowding_tables_estimation', 'x2', 16))"
python -B -m v3.production_runner launch v3/runs/a6/crowding/tables_A1_manifest.json v3/runs/a6/crowding/tables_A1 --profile x2 --workers 31 --threads 1 --cpu-budget 32 --mode normal
```

After the launch, record the measured wall to the consumption log with
`budget_a6.append_consumption("v3/runs/a6/A6_consumption.jsonl",
"crowding_tables_estimation", <hours>)`.

The estimation publication is deliberately `None`: the runner's built-in table
publication is hard-coded to the nominal completeness, so A6 assembles the family
in the next step.

### 3c. Assemble the A1-equivalent family

```text
python -B - <<'PY'
import json
from v3 import tables_a6 as t6
from v3.artifacts import code_identity, read, unseal
from v3.production_runner import completed
FAM = "crowding"; SRC = "v3/runs/a6/crowding"; CAL = "v3/runs/registered/v3_rerun_calibration.json"
cal = read(CAL)
manifest = unseal(read(SRC + "/tables_A1_manifest.json"))
outputs = [completed(__import__("pathlib").Path(SRC + "/tables_A1/table"), j, code_identity()) for j in manifest["jobs"]]
t6.assemble(outputs, cal, SRC + "/v3_rerun_tables_A1.json", FAM, registered=True)
print("assembled", SRC + "/v3_rerun_tables_A1.json")
PY
```

Registered assembly checks the family's estimation completeness (every own
context has a row) and the sensitivity contrasts; it halts here only on missing
or duplicate estimation rows. The **not_estimable halt is later, at 3f**: A4
validation marks a row not_estimable (availability floor, empty support or a
failed FV cell), and the registered load inside `publish_validation` rejects such
a family. That family's arm is then reported as not run, with the reason, and no
repair is made after any R1 or R2 output has been read.

### 3d. Prepare the A4 plan

```text
python -B - <<'PY'
import os
from v3 import tables_a6 as t6, budget_a6
from v3.artifacts import atomic_json, read, seal, unseal
FAM = "crowding"; SRC = "v3/runs/a6/crowding"; CAL = "v3/runs/registered/v3_rerun_calibration.json"
ledger = budget_a6.load(read("v3/runs/a6/A6_budget.json"), "v3/runs/a6/A6_consumption.jsonl")
rm = unseal(read("v3/runs/registered/reruns_manifest.json"))
reg = unseal(read("v3/runs/a6/A6_seed_registry.json"))
plan = t6.prepare_validation(SRC, CAL, family=FAM, registration=read("v3/runs/registered/A6_pin.json"),
                             ledger=ledger, rerun_commit=os.environ["RERUN_COMMIT"], a3_probe_root="v3/runs/a3_probe",
                             a1_source_root="v3/runs/registered_A1", rerun_manifest=rm, seed_registry=reg)
atomic_json("v3/runs/a6/crowding/A6_validation_plan.json", seal(plan))
print({"M": plan["M"], "M_FV": plan["M_FV"], "stage_jobs": len(plan["jobs"]), "wall_hours": plan["wall_seconds"] / 3600})
PY
```

`prepare_validation` pins the family's own source hash in place of A4's hard-coded
A1 hash, counts the family's own M and M_FV, binds the A6 registration into
`plan_hash` with the jobs rebuilt under that hash, takes its wall from the
`crowding_tables_validation` ceiling, asserts rerun-path invariance and the
registry, requires the A1 source root, a non-empty probe root and the rerun
manifest with no fallback (the family's own root is never substituted), and
rejects any settings override. The plan keeps the `v3-A4-validation-1` schema, so
the runner's own in-launch projection also applies; project against the budget
before launching, as in 3b.

### 3e. Configuration test and launch the A4 stages

Launch the five phased stage lists through the runner (run root
`v3/runs/a6/crowding/validation`), the mode cap as `--workers`, its own
configuration test choosing:

```text
python -B -m v3.production_runner launch v3/runs/a6/crowding/A6_validation_plan.json v3/runs/a6/crowding/validation --profile x2 --workers 31 --threads 1 --cpu-budget 32 --mode normal
```

After the validation launch, record its measured wall in the consumption log:
`python -B -c "from v3 import budget_a6; budget_a6.append_consumption('$A6_LOG', 'crowding_tables_validation', <hours>)"` (add `machine='wsl'` when run on the WSL workstation).

### 3f. Publish the validated family

```text
python -B - <<'PY'
from v3 import tables_a6 as t6
from v3.artifacts import read, unseal
FAM = "crowding"; SRC = "v3/runs/a6/crowding"; CAL = "v3/runs/registered/v3_rerun_calibration.json"
plan = unseal(read("v3/runs/a6/crowding/A6_validation_plan.json"))
print(t6.publish_validation(plan, SRC + "/validation", SRC, read(CAL),
      "v3/runs/registered/v3_rerun_tables_crowding.json",
      registered=True, registration=read("v3/runs/registered/A6_pin.json")))
PY
```

This writes the family, a receipt (`.compatibility.json`) and a sidecar
(`.cell_results.json`), and loads the result through
`ProductionTables(..., registered=True)` at A6's identity. **Where a not_estimable
row halts:** publish assembles the family, then loads it registered; a row that is
not estimable (or a family with an availability-floor or sensitivity failure) is
rejected there, at the registered load inside `publish_validation`. That family's
arm is then reported as not run, with the reason, and no repair is made after any
R1 or R2 output has been read. Repeat 3a-3f for each sigma family, publishing to
`v3_rerun_tables_sigma_x10.json` and `v3_rerun_tables_sigma_x0p1.json`.

## 4. Build the run manifests

Each family's published tables path must be in place before its runs. Confirm the
measured wall projection before each registered launch is within the 90-hour A6
program ceiling; if it exceeds it, stop and report for the operator's decision.

### 4a. The nominal-table arms (weight corners and horizon), rerun checkout

Build this spec at A6's checkout; it runs in the **rerun checkout**. Its
`code_hash` is stamped to the rerun commit's identity.

Both builders need the sealed main rerun manifest, so the rerun seeds come from
it, not rebuilt path strings.

```text
python -B - <<'PY'
import os
from v3 import sensitivity_a6 as s6, budget_a6
from v3.artifacts import atomic_json, read, seal, unseal
rerun_manifest = unseal(read("v3/runs/registered/reruns_manifest.json"))
ledger = budget_a6.load(read("v3/runs/a6/A6_budget.json"), "v3/runs/a6/A6_consumption.jsonl")
reg = unseal(read("v3/runs/a6/A6_seed_registry.json"))
spec = s6.nominal_run_spec(os.environ["RERUN_COMMIT"], read("v3/runs/registered/rerun_pin.json"),
        a1_source_root="v3/runs/registered_A1", probe_root="v3/runs/a3_probe",
        rerun_manifest=rerun_manifest, ledger=ledger, seed_registry=reg)
atomic_json("v3/runs/a6/a6_nominal_runs.json", seal(spec))
print({"jobs": len(spec["jobs"]), "phases": spec["phases"], "wall_hours": spec["a6_wall_share_hours"]})
PY
```

`rerun_pin.json` is the rerun commit's design-note pin (the same pin the reruns
use); `reruns_manifest.json` is the sealed main rerun manifest. The nominal spec's
`code_hash` is stamped to the rerun commit's identity (its wall is the
`nominal_runs` ceiling).
Move `v3/runs/a6/a6_nominal_runs.json` to the **rerun checkout** and launch it
there, in its own run root, against the nominal tables, after its configuration
test:

```text
# in the rerun checkout, from simulation/
python -B -m v3.production_runner launch v3/runs/a6/a6_nominal_runs.json v3/runs/a6_nominal_runroot --profile x2 --workers 31 --threads 1 --cpu-budget 32 --mode normal
```

The nominal jobs carry `tables_path = v3/runs/registered/v3_rerun_tables_A4.json`,
which the rerun checkout's loader accepts at the rerun code identity.

### 4b. The variant arms, one separate spec per arm, A6 checkout

Each variant arm has its own spec and its own run root, so a failed family
reports only its own arm as not run. Each takes its ledger run share and asserts
invariance, the arm run counts (crowding 4,400; each sigma 500), seed
distinctness, disjointness from the full forbidden set, and the global seed check.

```text
python -B - <<'PY'
import os
from v3 import sensitivity_a6 as s6, budget_a6
from v3.artifacts import atomic_json, read, seal, unseal
COMMIT = os.environ["RERUN_COMMIT"]; PIN = read("v3/runs/registered/A6_pin.json")
rm = unseal(read("v3/runs/registered/reruns_manifest.json"))
ledger = budget_a6.load(read("v3/runs/a6/A6_budget.json"), "v3/runs/a6/A6_consumption.jsonl")
reg = unseal(read("v3/runs/a6/A6_seed_registry.json"))
common = dict(a1_source_root="v3/runs/registered_A1", probe_root="v3/runs/a3_probe", rerun_manifest=rm,
              ledger=ledger, seed_registry=reg)
crowd = s6.crowding_run_spec(COMMIT, PIN, crowding_paths=(
        "v3/runs/registered/v3_rerun_calibration.json", "v3/runs/registered/v3_rerun_tables_crowding.json"), **common)
atomic_json("v3/runs/a6/a6_crowding_runs.json", seal(crowd))
for v, tag in (("sigma_squared_x10", "sigma_x10"), ("sigma_squared_x0.1", "sigma_x0p1")):
    spec = s6.sigma_run_spec(COMMIT, PIN, v, (
        "v3/runs/registered/v3_rerun_calibration_%s.json" % tag,
        "v3/runs/registered/v3_rerun_tables_%s.json" % tag), **common)
    atomic_json("v3/runs/a6/a6_%s_runs.json" % tag, seal(spec))
print("built crowding and both sigma run specs")
PY
```

Launch each in its own run root; if a family failed to publish, skip that arm and
report it as not run:

```text
python -B -m v3.production_runner launch v3/runs/a6/a6_crowding_runs.json v3/runs/a6_crowding_runroot --profile x2 --workers 31 --threads 1 --cpu-budget 32 --mode normal
python -B -m v3.production_runner launch v3/runs/a6/a6_sigma_x10_runs.json v3/runs/a6_sigma_x10_runroot --profile x2 --workers 31 --threads 1 --cpu-budget 32 --mode normal
python -B -m v3.production_runner launch v3/runs/a6/a6_sigma_x0p1_runs.json v3/runs/a6_sigma_x0p1_runroot --profile x2 --workers 31 --threads 1 --cpu-budget 32 --mode normal
```

### 4c. Project each run against the budget

Before each run launch, `budget_a6.project(ledger,
'nominal_runs'|'crowding_runs'|'sigma_squared_x10_runs'|'sigma_squared_x0.1_runs',
'x2', <workers>)`; it refuses a launch that would bring the total over the A6
ceiling (A7, 90). Record
the measured consumption afterward with
`budget_a6.append_consumption("v3/runs/a6/A6_consumption.jsonl", <component>,
<hours>)`.

## 5. Operational

- **`llm down` / `llm up`.** Prepend the local bin to PATH first:
  `export PATH=$HOME/.local/bin:$PATH`. The X2 launch wrapper stands the model
  server down before every batch expected to exceed an hour and restores it when
  the batch ends. Record both in the execution metadata.
- **No overlap.** Before each launch, confirm no other production run is active:
  `pgrep -af '[v]3[.]production_runner'` returns nothing but the launch you are
  about to start.
- **Modes.** Honor `work` and `normal` mode messages through the runner's control
  file; do not kill running jobs to change modes.
- **Machine (WSL vs X2).** The unchanged runner's `--profile x2` refuses any host
  whose node name is not exactly `yotko-evo-x2` and is not Linux (validate_spec,
  `production_runner.py`). The bit-identical WSL workstation (D32) has a different
  node name, so `--profile x2` refuses it. `--profile local` has no host check;
  its cap is min(12, budget - 1). A6's own configuration profiles list
  `workers_local` 8 and 12, the only counts the runner tests, so the local
  configuration test can select up to 12 workers.
  - **So a registered A6 family or run can run on the WSL workstation** under
    `--profile local` at up to 12 workers. WSL has no `llm`, so there is no model
    server to stand down and no service wrapper; run the launch directly, for
    example:
    `python -B -m v3.production_runner launch <spec> <run_root> --profile local --workers 12 --threads 1 --cpu-budget 13 --mode normal`.
    Keep to 4 or fewer workers if the WSL bit-identity test or other work is using
    the machine's cores.
  - **The X2 `--profile x2` path is primary.** The runner is not changed; use the
    WSL workstation under `--profile local` only if the operator directs it.

## 6. The reading

`reading_a6` operates on in-memory arrays and never reads a registered rerun
output. Run it against the arm and nominal per-seed outcomes (survival final
populations per rr, or fire indicators per capability) once those exist, off the
X2, not in this batch. It reports the boundary and cap* difference intervals at
level 1 - 0.05/33, the four verdicts and the margins, and the descriptive per-rr
survival differences and half/full-seed convergence.

## 7. Send back

- The self-check line from step 2 and each variant's sha256 and epsilon_N.
- The seed registry's `total_seeds`, and the rerun-path invariance output for each
  step (the `matched` count and the empty mismatch/removed/added lists).
- Every sealed spec: the three estimation specs, the three A4 validation plans,
  the nominal run spec and the three variant run specs (their job counts and
  wall_seconds).
- For each family: the assembly result, the A4 plan M and M_FV, the publication
  summary (rows, not_estimable count, sensitivity status), or the not-run reason.
- The ledger (`A6_budget.json`) and its consumption log (`A6_consumption.jsonl`),
  and each launch's projection.
- Each run root's `launches.json`, the chosen worker configurations, the `llm
  down`/`llm up` records and the no-overlap confirmation for each launch.
- Do not send any survival, extinction or fire rate, rule ranking or outcome.
