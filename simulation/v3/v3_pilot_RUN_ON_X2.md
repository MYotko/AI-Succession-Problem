# v3 B2 pilot: operator launch on X2

This is a non-registered, `pilot`-tagged cost study. Its jobs never enter
registered results. Launch only after the separate stage 4 tranche has
finished and restored its model service. The v3 service lease serializes
v3 launches; it does not take ownership of the stage 4 runner's lease.

The archive contains public baseline Python dependencies, new v3 code,
the frozen pilot specification and this runbook. It contains no private
input documents. NumPy must already be installed in the selected Python
environment. No network, installation or remote launch is performed by
the code. Use the operator's existing environment on `yotko-evo-x2`.

## Verify and launch

Extract `v3_pilot_bundle.zip` to a new directory. From that directory:

```bash
export PYTHONPATH="$PWD/simulation"
export PYTHONDONTWRITEBYTECODE=1
python -B -m v3.pilot verify .
python -B -m v3.production_runner launch \
  simulation/v3/pilot_manifest.json simulation/v3/runs/pilot \
  --profile x2 --workers 31 --threads 1 --cpu-budget 32 --mode normal
```

The CLI validates the frozen code/specification identities, takes the
exclusive v3 service lease, records `llm down`, and starts the configuration
test in that service state. It always attempts `llm up` before releasing
the service lease, including on a failed down command, exceptions,
interruptions, incomplete work or deadlines. Check `service.json` and
both service logs. Successful `llm up` records command success, not an
independent readiness probe. If up fails, restore it manually and retain
the failure record.

The configuration test is mandatory on every launch and resume. It uses
actual short rerun, plain, FV and calibration jobs at 8,12,16,24,28,31,32
workers, one numerical thread each, in two opposite-order rounds. The
32-worker case is dedicated configuration mode only. Normal launches cap
at 31 and work launches at 28. Selection uses completed jobs/hour and
prefers the smaller configuration within five percent. No two-thread test
is authorized without material numerical-thread profiling evidence.

The requested worker count is a launch upper limit, not a fixed choice.
The fastest measured admissible configuration is selected separately for
each workload. All numerical-library limits are configured before import
and queried in the worker. An unverifiable limit stops that job.

## Pilot work and outputs

The frozen specification contains 35 scientific pilot jobs:

* 18 complete 500-step reruns: six R1/R2 grid cases, three independent
  tagged seeds each. Every step still evaluates all 25 rules. Population
  paths, selected rules, admission, yields and objective diagnostics are
  retained. Until registered calibration and full tables exist, these
  reruns use explicit fixture tables. Their outcomes are not scientific
  rerun results, and the final production decisions can change their cost.
* 12 primary table jobs: three rules, rr=.055 and .070, both forced plain
  and forced FV routes. A plain route that fails its survival screen is
  flagged, not accepted to save compute. These jobs rescore every relevant
  fixed-capability, alpha and weight context, including weight corners.
* Two full doubled-setting cost jobs at balanced, rr=.064: doubled
  populations and doubled length. These measure the sensitivity cost;
  production sensitivities remain the frozen 3-rule by 3-rr subset.
* Three balanced calibration cost trajectories of 500 steps at rr=.080.
  They do not create the registered 50-seed calibration file.

`cost_projection.json` projects all 24,900 primary/refinement reruns,
325 nominal rule/kernel primary table jobs, the 18 prescribed sensitivity
jobs, and the 50-seed calibration. It uses measured X2 configuration
efficiency and actual complete-job times, with average-case and maximum
tested-case rerun projections. Table estimates use the more expensive
observed primary route and measured doubled-setting costs. Budget gaps
against 72 and 24 hours are explicit. Trajectory and rescoring costs are
recorded separately; primary rescoring time is scaled to the largest
150-context family while preserving measured trajectory cost. This is a measured pilot projection,
not a throughput guarantee across unobserved population paths or extra
crowding/novelty-sensitivity kernels. Row failures are counted, not removed.

All output remains below `simulation/v3/runs/pilot/`. Each phase has
`outputs/`, hash-validated `records/`, `failures/`, `events.jsonl`,
`active.json` and `status.json`. Configuration jobs are stored separately
under `configuration/` and never count as completed pilot results.

## Live controls and resumption

Run these from a second shell with the same PYTHONPATH:

```bash
python -B -m v3.production_runner status simulation/v3/runs/pilot
python -B -m v3.production_runner control simulation/v3/runs/pilot --mode work
python -B -m v3.production_runner control simulation/v3/runs/pilot --mode normal
python -B -m v3.production_runner control simulation/v3/runs/pilot --stop drain
python -B -m v3.production_runner control simulation/v3/runs/pilot --stop now
```

Work mode stops replacing jobs until active workers drain to the selected
lower cap. Existing jobs finish by default. `--stop now` records in-flight
jobs as requiring restart from their original seed; completed records
remain valid. The model is not checkpointed by per-step logs. The latest
mode persists across resumption. Configuration tests use their explicitly
declared test mode, including the 32-worker case.

To resume within the original deadline, clear the stop flag, then repeat
the identical launch command:

```bash
python -B -m v3.production_runner control simulation/v3/runs/pilot --stop clear
```

Resumption verifies code, specification, exact job configurations, seeds
and output hashes. Completed jobs are skipped. It refuses incompatible
artifacts or an active recorded worker registry. It never steals an
active job lease. If a supervisor was killed forcibly, inspect surviving
worker processes and the service before resuming.

## Three-hour ceiling

The persisted deadline begins before `llm down`. The total allowance is
10,800 seconds. Configuration tests share at most 900 seconds. New work
ends with a 300-second cleanup reserve; in-flight workers are interrupted
at that deadline, then the service is restored. Resumption does not reset
the clock. An expired or incomplete pilot reports incomplete status and
does not claim either production budget passed. Do not edit the frozen
budget to extend it without operator review.

No X2 launch was performed while preparing this bundle. Return the bundle
receipt and the complete `runs/pilot/` tree for review. Keep it separate
from every registered dataset.

## Later registered runs

`python -B -m v3.study` prepares full calibration, table or 24,900-job
rerun manifests without launching them. It requires a pin JSON containing
`commit`, repository-relative `path`, and the pre-registration `sha256`.
The runner checks that commit locally as an ancestor of HEAD, verifies
the committed and working file bytes, and refuses uncommitted source.
Registered reruns require non-fixture calibrated tables with all required
rows and successful sensitivity screens. Missing contexts or continuation
bins fail closed; there is no fallback to pilot or midpoint values.
The extracted pilot archive lacks the Git history needed for registration.
