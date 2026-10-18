# A10 stage 1, nominal family: run on X2, 2026-10-08

This is an execution runbook for the interpreter. Every registered launch needs
the operator's go for that exact manifest, machine, root and ceiling. Run one
numbered step at a time. This document does not authorize a launch or a change
to a scientific quantity. Stage 2 and the sealed readings are excluded.

Amendment A11 resolves the label ceiling and allows the operator-gated family
identity record commit after validation. It also defines a compatibility proof
for completed artifacts after an execution-only repair. Each launch still needs
its own go. A11 item 4 adds one coordinator root shared by qualified worker
hosts. Complete the non-registered X2/WSL rehearsal in section 12 before any
registered use. The 980-hour program ledger remains an operational responsibility.

The A11 design-note commit and its committed bytes are filled in below. Before
using these commands, replace `<CODE_COMMIT>` with the reviewed full ID of the
implementation commit that contains this runbook. The note commit precedes the
code commit. It is a release placeholder, not a value to infer from a moving branch.

## 0. Frozen identities and scope

| Item | Identity |
| --- | --- |
| Public repository | `https://github.com/MYotko/AI-Succession-Problem.git` |
| Implementation commit | `<CODE_COMMIT>` |
| Code identity, LF-normalized | `c19b54f5bde7180c78a5eba4721c33527c47b84c4d93d2fae757fd3e31452810` |
| Design-note commit | `411cbdbdb6a8a5fd32b2bbbc01289fb3e198bed5` |
| Design-note path | `simulation/diagnostics/v3_rerun_design_note.md` |
| Design-note SHA256, committed bytes | `1fe04079a8474ee9a0043dd0d5d661c805f5a468f1421e5ef4735f6af539a05e` |
| P2 projection file SHA256 | `78a1d3ac253048c7e077b0e4eb12dd3150fa178cf3e63a24c6f0d87f02a8ad8d` |
| Calibration file SHA256 | `fd86358a39e3b643fb9adc4e81a2372915ca50a1866e9b0e330a874b41746e01` |
| Calibration payload seal | `bf0f7c3f10310558d567b6b3f7c24f6f99f2fe6eb71fd830cccfd8e2aa0bd6d6` |

The authority is Amendment A10, especially sections 12 and 13, and Amendment A11 in the pinned
design note. Section 12 supersedes A7's 90-hour budget for these A10 runs;
90 hours continues to apply to A6 under R4. The nominal family includes the
k-star arms' scoring. No square-root, crowding, or sigma-variant tables or runs
belong in this stage.

Keep `~/v3_reruns`, `~/v3_a6`, `~/v3_a5`, and `~/a10_pilot` untouched. Do not
pull, fetch into, switch, repair, or reuse any of those checkouts. Do not pull
the new `~/v3_a10` checkout either. The staging procedure below uses the
workstation copies of the exclusion records, so it need not read the old X2
checkouts at all.

## 1. Fresh X2 checkout and registration pin

On X2, only after confirming that `~/v3_a10` does not already exist:

```bash
set -euo pipefail
test ! -e "$HOME/v3_a10"
git -c core.autocrlf=false clone --no-checkout \
  https://github.com/MYotko/AI-Succession-Problem.git "$HOME/v3_a10"
git -C "$HOME/v3_a10" -c core.autocrlf=false checkout --detach \
  '<CODE_COMMIT>'
export PATH="$HOME/miniforge3/envs/phaseb/bin:$HOME/.local/bin:$PATH"
export PYTHON="$HOME/miniforge3/envs/phaseb/bin/python3.13"
export A10CO="$HOME/v3_a10"
export CODE_COMMIT='<CODE_COMMIT>'
cd "$A10CO/simulation"
export A10_ROOT=v3/runs/a10_stage1
export CAL=v3/runs/registered/v3_rerun_calibration.json
export PIN="$A10_ROOT/A10_pin.json"
export SOURCE="$A10_ROOT/nominal/source"
export EST_SPEC="$SOURCE/tables_A1_manifest.json"
export EST_RUN="$SOURCE/tables_A1"
export VAL_SPEC="$A10_ROOT/nominal/validation_plan.json"
export VAL_RUN="$A10_ROOT/nominal/validation_run"
export TABLE="$A10_ROOT/nominal/v3_rerun_tables_A10.json"
export IDENTITY="$A10_ROOT/nominal/family_identity.json"
export LABEL_SPEC="$A10_ROOT/nominal/labels_plan.json"
export LABEL_RUN="$A10_ROOT/nominal/labels_run"
export LABELS="$A10_ROOT/nominal/v3_rerun_labels_A10.json"
export PROBE="$A10_ROOT/inputs/a3_probe"
export COST="$A10_ROOT/inputs/a10_pilot_P2_projection_2026-10-08.json"
export EXPECTED_CODE=c19b54f5bde7180c78a5eba4721c33527c47b84c4d93d2fae757fd3e31452810
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
mkdir -p "$A10_ROOT/inputs" "$A10_ROOT/specs" "$A10_ROOT/checks"
"$PYTHON" -B - <<'PY'
import hashlib, os, subprocess
import numpy as np
from pathlib import Path
from v3.artifacts import (atomic_json, code_identity, digest, source_manifest,
                          verify_registration, file_hash, read, unseal)
from v3.tables_a10 import family_instrument
from v3.instrument import CONSTANTS_SHA256
from v3.calibration import load_calibration
commit = '<CODE_COMMIT>'
def git(*args):
    return subprocess.check_output(['git', *args])
assert git('rev-parse', 'HEAD').decode().strip() == commit
assert not git('diff', 'HEAD', '--', 'v3', 'diagnostics').strip()
assert np.__version__ == '2.4.4'
committed = {p: hashlib.sha256(git('show', commit + ':simulation/' + p)
             .replace(b'\r\n', b'\n')).hexdigest() for p in source_manifest()}
assert digest(committed) == code_identity() == os.environ['EXPECTED_CODE']
pin = {'commit': '411cbdbdb6a8a5fd32b2bbbc01289fb3e198bed5',
       'path': 'simulation/diagnostics/v3_rerun_design_note.md',
       'sha256': '1fe04079a8474ee9a0043dd0d5d661c805f5a468f1421e5ef4735f6af539a05e'}
assert hashlib.sha256(git('show', pin['commit'] + ':' + pin['path'])).hexdigest() == pin['sha256']
verify_registration(pin, instrument=family_instrument('nominal'))
target = Path(os.environ['PIN'])
assert not target.exists() or read(target) == pin
atomic_json(target, pin)
cal = Path(os.environ['CAL'])
assert file_hash(cal) == 'fd86358a39e3b643fb9adc4e81a2372915ca50a1866e9b0e330a874b41746e01'
assert read(cal)['sha256'] == 'bf0f7c3f10310558d567b6b3f7c24f6f99f2fe6eb71fd830cccfd8e2aa0bd6d6'
load_calibration(cal, instrument=family_instrument('nominal'), registered=True)
constants = read('v3/a10_constants.json')
unseal(constants)
assert constants['sha256'] == CONSTANTS_SHA256
assert Path('v3/a10_constants.json').read_bytes() == Path('v3/runs/registered/v3_a10_constants.json').read_bytes()
atomic_json(Path(os.environ['A10_ROOT'])/'instrument.json', family_instrument('nominal').declaration())
print({'HEAD': commit, 'code_identity': code_identity(), 'registration': 'verified',
       'pin_file_sha256': file_hash(target), 'constants_seal': CONSTANTS_SHA256})
PY
```

Expected: exact commit and full identity above, verified registration and
calibration, matching sealed constants copies. Registration checks ancestry,
the committed and working design-note hashes, the presence of A10 and A11, and clean
committed source. A pin is a plain three-field JSON object, not a sealed object.
It need not itself be committed. Do not normalize or edit an input to make a
failed byte hash pass. Linux checks out the design note with its committed LF
bytes. Check Python is 3.13.12 with `"$PYTHON" --version`.

## 2. Stage the exclusion records and cost record

`inputs/X2_ENVIRONMENT.md` identifies the original records under
`~/v3_reruns/simulation/v3/runs/registered/` (`a3_probe`, `registered_A1`), and
their workstation copies at
`C:\Users\matty\Dev\v3_instrument_inputs\a3_probe` and
`C:\Users\matty\Dev\v3_instrument_inputs\registered_A1`. Use those workstation
copies. Preserve the original JSON bytes. The probe loader extracts seeds
internally; no person opens its scientific records.

In workstation WSL, make a transfer bundle in a new handoff directory. The
original A1 manifest is retained for seed provenance only. Do not copy an old
table family or substitute the old A1 source for this stage's new source.

```bash
set -euo pipefail
export HANDOFF="$HOME/a10_stage1_handoff"
test ! -e "$HANDOFF"
mkdir -p "$HANDOFF/exclusions/registered_A1"
cp -a /mnt/c/Users/matty/Dev/v3_instrument_inputs/a3_probe "$HANDOFF/exclusions/"
cp /mnt/c/Users/matty/Dev/v3_instrument_inputs/registered_A1/tables_A1_manifest.json \
  "$HANDOFF/exclusions/registered_A1/"
cp /mnt/c/Users/matty/Dev/v3_a10_repo/inputs/a10_pilot_P2_projection_2026-10-08.json \
  "$HANDOFF/"
(
  cd "$HANDOFF/exclusions"
  find a3_probe registered_A1 -type f -print0 | LC_ALL=C sort -z | xargs -0 sha256sum > ../EXCLUSIONS_SHA256SUMS
)
(
  cd /mnt/c/Users/matty/Dev/v3_instrument_inputs
  sha256sum -c "$HANDOFF/EXCLUSIONS_SHA256SUMS" > "$HANDOFF/source_hash_check.txt"
)
tar -C "$HANDOFF" -cf "$HANDOFF/exclusions.tar" exclusions EXCLUSIONS_SHA256SUMS source_hash_check.txt
sha256sum "$HANDOFF/exclusions.tar"
scp "$HANDOFF/exclusions.tar" "$HANDOFF/a10_pilot_P2_projection_2026-10-08.json" \
  yotko@100.96.61.55:v3_a10/simulation/v3/runs/a10_stage1/inputs/
```

Record the displayed bundle hash in the operator's handoff record, then on X2:

```bash
cd "$A10CO/simulation"
sha256sum "$A10_ROOT/inputs/exclusions.tar"
# Compare with the handoff hash before extracting; stop on a mismatch.
tar -xf "$A10_ROOT/inputs/exclusions.tar" -C "$A10_ROOT/inputs"
(
  cd "$A10_ROOT/inputs/exclusions"
  sha256sum -c ../EXCLUSIONS_SHA256SUMS > ../destination_hash_check.txt
)
export PROBE="$A10_ROOT/inputs/exclusions/a3_probe"
"$PYTHON" -B - <<'PY'
import os
from v3.artifacts import file_hash, read, unseal
from v3.table_validation_a4 import load_probe_seeds
assert file_hash(os.environ['COST']) == '78a1d3ac253048c7e077b0e4eb12dd3150fa178cf3e63a24c6f0d87f02a8ad8d'
cost = unseal(read(os.environ['COST']))
assert cost['non_registered'] and cost['actual_x2'] and not cost['results_eligible']
seeds = load_probe_seeds(os.environ['PROBE'])
assert seeds, 'original D26 probe exclusion set is empty'
unseal(read(os.environ['A10_ROOT'] + '/inputs/exclusions/registered_A1/tables_A1_manifest.json'))
print({'probe_seeds': len(seeds), 'transfer_hashes': 'verified', 'cost_record': 'verified'})
PY
```

On 2026-10-08 the interpreter verified the workstation `a3_probe` copy byte
for byte against both X2 checkouts, `~/v3_a4` and `~/v3_a6`: 462 of 462 files
matched. The original A1 manifest also matched (SHA256 begins `6e03391a`).
Keep that verification with the transfer inventory; the commands above verify
the complete file hashes again during transfer. No read of an old X2 checkout
is needed for this runbook. Do not replace the full inventory with the short
manifest hash printed here.

No A6 variant calibration is needed. Later steps create the new estimation
manifest and outputs, the validated family and both siblings, the committed
A5 identity record, the A5 labels, and the final A10 receipt. These are the
other inputs the registered preparation functions require.

## 3. Ceiling allocation and launch accounting

These are **budget estimates**, using the supplied sealed P2 cost record, not
outcomes. Its nominal components before reserves are:

```text
estimation                                      69.1454634842
FV validation, including its census             524.3806586483
labels, three replicates per primary FV job     256.8146547755
tables total                                   850.3407769080
R1 + refinement + R2 + k1.5 + k2.3 + weights + horizon
                                                124.5820802239
P2 original reserves, seven run launches          4.3333333333
P2 original nominal total                      979.2561904652
A11 reserves: (1200 + 3000 + 3000 + 5*1200)/3600   3.6666666667
A11 five-launch nominal budget estimate        978.5895237985
margin to the operator's ceiling                  1.4104762015
```

The realism factor 1.35, interpolation, scaling and effective workers are
already included. Do not multiply again by 1.35, by 16, or by 14/7.46. The
effective-worker estimate is about 7.46344, with tighter caps in some strata.
Measured-only nominal cost including reserves is 348.6611602448 hours;
630.5950302204 hours comes from estimated strata. Those estimates remain
visible in the supplied projection. Configuration tests select actual workers.

| Component | P2 cost before reserves | Reserve | Wall hours and X2-equivalent allowance |
| --- | ---: | ---: | ---: |
| Estimate nominal tables | 69.145464 | 0.333333 | **69.50** |
| Validate and publish, A4 producer | 524.380659 | 0.833333 | **525.87** |
| A5 labels | 256.814655 | 0.833333 | **257.66** |
| Main: R1 prime, refinement, R2 prime | 49.466701 | 0.333333 | **50.49** |
| k-star 1.5 runs | 10.599070 | 0.333333 | **10.94** |
| k-star 2.3 runs | 10.590828 | 0.333333 | **10.93** |
| A6 weight corners | 43.997688 | 0.333333 | **44.34** |
| A6 horizon | 9.927793 | 0.333333 | **10.27** |
| **Total** | **974.922857** | **3.666667** | **980.00** |

The main ceiling is exactly `17.42 + 10.43 + 22.64 = 50.49` hours.
Its combined cost is `17.080648 + 10.087822 + 22.298231 = 49.466701`.
One configuration test replaces three, retaining 0.666667 hours of the old
reserves as extra main-launch margin. The P2 estimates and realism factor
are unchanged. The measured-only and estimated-stratum figures above refer
to the original P2 accounting.

Most rounding slack, 0.656008 hours, goes to validation. Assembly, preparation,
hashing, the identity record and receipt publication have no worker launch;
charge their X2 execution time to the associated table component, inside its
allowance. Reserve time is part of each ceiling, not extra time after it.

**Route qualification.** P2 sums, by stratum,
`estimate + max(plain_validation, FV_validation + labels)`. The displayed table
split is the FV scenario, not a promise about the realized routes. Independent
worst-case validation alone is 598.0701503382 hours; allocating that plus every
label job would double count mutually exclusive route costs and project
1052.9456821551 hours under the original seven-run-launch reserves
(1052.2790154884 with A11's five run launches). Before validation,
use the prepared route counts and measured configuration projection to review
its allowance and the remaining label allowance together. If 525.87 is too
small, stop before dispatch. The operator can approve a documented budget-only
reallocation within 980 before the affected launches, or follow the amendment's
ceiling rule. Do not shorten jobs, drop rows, change seeds, or read outcomes to
make a launch fit.

Each A10 spec now declares both `wall_seconds` and `x2_equivalent_hours`.
The latter is the corresponding allocation in the table, including main at
50.49. Pull dispatch stops at the allowance less the existing cleanup reserve,
or the wall dispatch deadline, whichever arrives first. In-flight jobs drain
within the hard wall deadline. Reserve overruns remain charged and reported.
The runner still has no cross-root 980-hour program ledger.
`budget_a6.build_ledger()` and its ceiling functions hard-code the R4 A6
90-hour program and component names; do not use them for stage 1. Use a separate
operations ledger, freeze each spec before its go, and admit at most one root
per allocation. The following creates the initial allocation without changing
code identity:

```bash
"$PYTHON" -B - <<'PY'
import os
from decimal import Decimal
from pathlib import Path
from v3.artifacts import atomic_json, read, seal, file_hash
hours = dict(estimate='69.50', validation='525.87', labels='257.66',
             main='50.49', k1p5='10.94',
             k2p3='10.93', weight_corner='44.34', horizon='10.27')
assert sum(map(Decimal, hours.values())) == Decimal('980')
payload = {'schema': 'A10-stage1-operations-budget-1', 'ceiling_x2_hours': 980,
           'allocations_x2_hours': hours, 'planning_relative_throughput': {'x2': 1, 'wsl': .37},
           'projection_file_sha256': file_hash(os.environ['COST']),
           'code_hash': os.environ['EXPECTED_CODE'], 'decision_date': '2026-10-08'}
target = Path(os.environ['A10_ROOT'])/'budget_allocation.json'
assert not target.exists() or read(target) == seal(payload)
atomic_json(target, seal(payload))
print({'allocated_x2_hours': 980, 'allocation_sha256': file_hash(target)})
PY
```

For each go, retain component, spec byte hash and payload seal, root, machine,
wall seconds, projection, operator/date, machine-register hashes and reserved X2-equivalent hours.
Before go, check consumed time plus every outstanding reservation is at most
980. On exit, append measured wall time, including configuration, cleanup and
failed attempts, to an operations consumption log. Use the coordinator's sealed host intervals and registered measured relative
throughput. X2 is the reference at 1; 0.37 is the existing WSL planning input,
not a substitute for the new qualification measurement. Concurrent machines
are additive. Charge from join, including configuration and input transfers,
through last work/leave; a disconnected host is charged through lease expiry.
Completion receipt is the conservative observed job-end timestamp. Never count
worker-hours as wall hours. Keep a stopped root's reservation until reconciled.

The fixed allocations bound the ordinary eight-launch plan, but the runner does
not enforce the cross-root sum. It logs each pull root's host intervals, worker-seconds and X2-equivalent consumption automatically. Resumes retain the same
deadline. Extra roots, relocation, repeated launches, overruns in cleanup, or
sharing require reconciliation before another go. Any measured overrun is
charged and reported, not erased by a fresh root. A4/A5 recheck their measured
remaining-work projection before each phase. Estimation and rerun launches
choose a configuration and enforce a deadline, but do not implement that A4
projection gate. Their P2-based projection and the program reservation are
therefore explicit operator pre-launch checks, not an automatic runner feature.

## 4. Common preflight, launch, board and completion procedure

Keep these shell functions in the interpreter's launch script or shell. They
write only operational records under this checkout. They are not new modules
in `v3/`. Save any detached script with LF endings, and use the exported PATH.

```bash
check_spec() {
  "$PYTHON" -B - "$1" "$2" "${3:-x2}" <<'PY'
import os, sys
from collections import Counter
from pathlib import Path
from v3.artifacts import read, unseal, atomic_json, file_hash
from v3.production_runner import validate_spec, caps
spec = unseal(read(sys.argv[1]))
from v3.multihost_a11 import freeze, validate_extension, prepare
from v3.artifacts import seal
if 'pull_dispatch' not in spec:
    spec = freeze(spec, read(os.environ['COST']), code_commit=os.environ['CODE_COMMIT'],
                  extra_inputs=[os.environ['PROBE']])
    atomic_json(sys.argv[1], seal(spec))
validate_extension(spec)
profile = sys.argv[3]
settings = (dict(profile='x2', workers=31, threads=1, cpu_budget=32, mode='normal') if profile == 'x2'
            else dict(profile='local', workers=12, threads=1, cpu_budget=16, mode='work'))
settings['caps'] = caps(profile, settings['cpu_budget'])
assert spec['registered'] and spec['registered_a10']
assert spec['code_hash'] == os.environ['EXPECTED_CODE']
preflight = validate_spec(spec, settings)
atomic_json(Path(sys.argv[2])/'context_preflight.json', preflight)
prepare(sys.argv[1], sys.argv[2], settings)
print({'jobs': len(spec['jobs']), 'phases': dict(Counter(j['config']['phase'] for j in spec['jobs'])),
       'wall_seconds': spec['wall_seconds'], 'x2_equivalent_hours': spec['x2_equivalent_hours'],
       'spec_sha256': file_hash(sys.argv[1]),
       'spec_seal': read(sys.argv[1])['sha256'], 'context_preflight': preflight['checked']})
PY
}

launch_x2() {
  local spec="$1" root="$2" total="$3" board="$4"
  # Execute this function only after the operator's go for these exact arguments.
  if pgrep -af '[v]3[.]production_runner'; then
    echo 'STOP: another runner may own the model-server state'; return 1
  fi
  check_spec "$spec" "$root"
  test -s "$A10_ROOT/checks/A11_rehearsal_approved.json"
  "$PYTHON" -B - <<'PY'
import os
from pathlib import Path
from v3.artifacts import read, unseal, code_identity
review = unseal(read(Path(os.environ['A10_ROOT'])/'checks/A11_rehearsal_approved.json'))
assert review['passed'] and review['code_hash'] == code_identity()
assert review['operator_approval']['operator'] and review['operator_approval']['when']
PY
  test -s "$root/machine_register/00000000.json"
  mkdir -p "$root"
  local previous_launches
  previous_launches=$("$PYTHON" -B - "$root" <<'PY'
import sys
from pathlib import Path
from v3.artifacts import read
path = Path(sys.argv[1])/'launches.json'
print(len(read(path)) if path.exists() else 0)
PY
  )
  setsid nohup "$PYTHON" -B -m v3.production_runner launch "$spec" "$root" \
    --profile x2 --workers 31 --threads 1 --cpu-budget 32 --mode normal \
    </dev/null >>"$root/launcher.log" 2>&1 &
  local runner_pid=$!
  printf '%s\n' "$runner_pid" > "$root/supervisor.pid"
  nohup "$HOME/status-board/run_watchdog.sh" "$runner_pid" \
    "$A10CO/simulation/$root" "$total" "$HOME/status-board/$board" 7200 \
    </dev/null >"$root/watchdog.log" 2>&1 &
  printf '%s\n' "$!" > "$root/watchdog.pid"
  # Wait for this attempt's machine record before starting the guarded local RPC.
  "$PYTHON" -B - "$root" "$runner_pid" "$previous_launches" <<'PY'
import os, platform, sys, time
from pathlib import Path
from v3.artifacts import read
path = Path(sys.argv[1])/'launches.json'
while True:
    os.kill(int(sys.argv[2]), 0)  # Refuse if the coordinator exited during startup.
    history = read(path) if path.exists() else []
    if len(history) > int(sys.argv[3]):
        assert history[-1]['machine'] == platform.node()
        assert history[-1]['code_hash'] == os.environ['EXPECTED_CODE']
        assert not history[-1].get('finished_epoch')
        break
    time.sleep(1)
PY
  # X2 is also a pull worker. Its supervisor, not the coordinator, owns llm.
  setsid nohup "$PYTHON" -B -m v3.host_a11 \
    --local --root "$root" \
    --scratch "$root/host_x2" --profile x2 --workers 31 --cpu-budget 32 --mode normal \
    </dev/null >>"$root/worker_x2.log" 2>&1 &
  printf '%s\n' "$!" > "$root/worker_x2.pid"
}

check_done() {
  "$PYTHON" -B - "$1" "$2" <<'PY'
import sys
from pathlib import Path
from v3.artifacts import read, unseal, code_identity, digest, atomic_json, file_hash
from v3.production_runner import completed
spec = unseal(read(sys.argv[1])); root = Path(sys.argv[2])
assert read(root/'identity.json') == {'spec_hash': digest(spec), 'code_hash': code_identity()}
launches = read(root/'launches.json')
assert launches[-1].get('complete') is True
assert all(completed(root/j['config']['phase'], j, code_identity()) is not None for j in spec['jobs'])
for phase in spec['phases']:
    if any(j['config']['phase'] == phase for j in spec['jobs']):
        assert read(root/phase/'nondeterminism_check.json')['matched'] is True
assert not (root/'nondeterminism_failure.json').exists()
from v3.dispatch_store_a11 import read_state
state = read_state(root)
assert state['complete'] and not state['halt']
service = read(root/'host_x2/service.json')
assert service['down_exit_code'] == service['up_exit_code'] == 0
restored, finished = True, service['finished_epoch']
assert all(v['end'] is not None for v in state['sessions'].values())
charged = sum((v['end']-v['joined'])*v['relative_throughput'] for v in state['sessions'].values())/3600
print({'charged_x2_equivalent_hours': charged,
       'allowance': spec['x2_equivalent_hours'], 'hosts': sorted({v['host'] for v in state['sessions'].values()})})
inventory = {str((root/j['config']['phase']/'outputs'/(j['id']+'.json')).relative_to(root)):
             file_hash(root/j['config']['phase']/'outputs'/(j['id']+'.json')) for j in spec['jobs']}
atomic_json(root/'verified_output_hashes.json', inventory)
print({'complete': True, 'verified_jobs': len(inventory), 'outputs_digest': digest(inventory),
       'service_restored': restored, 'finished_epoch': finished})
PY
}
```

`validate_spec` builds each distinct calibration/kernel/instrument Context,
including configuration jobs, without simulation; it lists every Context
failure and refuses dispatch. Registered run specs also validate the completed
nominal table family and A10 receipt. A preflight pass is not a launch go.

The coordinator owns no model service and runs no scientific worker. Its X2
worker supervisor runs `llm down`, tests workload configurations, pulls work,
and restores `llm up`. Each WSL host tests its own configuration and never calls
the model-service commands. The X2 worker uses the explicit `--local` transport;
remote workers initiate SSH calls to the coordinator. `--workers 31` is the normal-mode
upper bound, not a choice of 31 workers. The configuration candidates include
8, 12, 16, 24 and 32; 32 can be tested under the configuration cap but cannot
win a 31-worker production cap. Memory can lower the tested and active counts.
The runner prefers the smaller measured configuration within 5 percent.
The X2 profile requires a worker cap of at least 8. A smaller `--workers`
or persisted `--max-workers` is refused before configuration. Host caps and
modes persist across departures and rejoins; a larger worker command alone
does not replace them. An approved host's persisted controls can be corrected
while it is departed or before its first join:

```bash
"$PYTHON" -B -m v3.production_runner control "$RUN_ROOT" \
  --host yotko-evo-x2 --mode normal --max-workers 8 --stop clear
```

Use the cap approved for the workload, at least 8 on X2. This example repairs
the four-worker lockout found in rehearsal. It does not choose eight workers
for stage 1; the configuration test still makes that choice within the cap.
Inspect only selection, completed-work throughput and verified thread limits
in the runtime/configuration metadata. One numerical thread per worker.

The watchdog line in `launch_x2` is the board command for every launch below.
Its OUT argument is absolute, under `$HOME/status-board/`, because the watchdog
otherwise resolves it relative to its working directory. Pass only the JSON
basename as the helper's fourth argument.
`TOTAL` is the frozen job count, not the count of table rows or tested cells.
Check the board JSON has `done`, `total`, `started_epoch`, `updated_epoch` and
`complete` only when the launch record is complete; failed or stalled must
show Needs you. Do not infer success from process exit, log silence, or a
watchdog count alone. A 7,200-second stall interval avoids flagging ordinary
long table jobs too quickly. The watchdog is an existing X2 tool, not inspected
or tested by the runbook author.

For every step, inspect counts and statuses with:

```bash
"$PYTHON" -B -m v3.production_runner status "$RUN_ROOT"
"$PYTHON" -B -m v3.production_runner control "$RUN_ROOT" --host "<HOST_PLATFORM_NODE>" --mode work
"$PYTHON" -B -m v3.production_runner control "$RUN_ROOT" --stop drain
# For immediate operator-requested relief instead of draining:
"$PYTHON" -B -m v3.production_runner control "$RUN_ROOT" --stop now
# After the cause is resolved and a resume go is recorded:
"$PYTHON" -B -m v3.production_runner control "$RUN_ROOT" --stop clear
```

These are separate operator actions, not a sequence to paste automatically.
Mode changes let existing jobs finish. Resume with the identical launch
command, manifest and root, before the original deadline. The persisted per-host mode and worker limit take precedence over rejoin
defaults. Restart the coordinator first, then rejoin hosts. Outstanding leases
are void on coordinator resume, but late verified outputs from issued leases
are accepted or checked as duplicates. Do not start a second coordinator. Completed jobs
are validated and skipped. In-flight jobs restart from their original seeds;
there is no complete scientific checkpoint. Never delete `budget.json`, change
the manifest under a root, clear completion records, or reset an expired
deadline. An incompatible-resume, seed, source, Context, memory, screen,
nondeterminism or projection failure is a finding for the operator.

Global stops record `operator_stop_drain` or `operator_stop_now`, with
`stopped_epoch`, in `launches.json` and the operational journal. Clearing the
control for a new attempt does not erase a finished attempt's stop history.
`production_runner status` and the root and phase status files expose
`waiting_for` with `reason`, `phase` and `since_epoch`. A cross-host recheck
wait names the excluded original host. Other reasons identify missing eligible
hosts, configuration, input acknowledgements or memory. These diagnostics do
not waive the phase barrier or make an idle worker leave automatically.

After a coordinator kill, its old watchdog records failure and exits because
it watched the dead PID. The board continues to show that earlier failure
until a new watchdog is attached to the restarted coordinator, using the same
absolute OUT file. Repeating `launch_x2` after the resume go performs this
attachment. If restarting the coordinator command directly, immediately attach
the watchdog to its new PID:

```bash
# Use the same root, frozen total and board basename as the original launch.
export BOARD_NAME='<THE_SAME_BOARD_BASENAME>.json'
export TOTAL='<THE_SAME_JOB_COUNT>'
export NEW_COORDINATOR_PID='<PID_OF_THE_RESTARTED_COORDINATOR>'
nohup "$HOME/status-board/run_watchdog.sh" "$NEW_COORDINATOR_PID" \
  "$A10CO/simulation/$RUN_ROOT" "$TOTAL" "$HOME/status-board/$BOARD_NAME" 7200 \
  </dev/null >>"$RUN_ROOT/watchdog.log" 2>&1 &
```

Workers stop after coordinator session loss. Restart each worker supervisor
with its original host command after the new coordinator is ready; do not
assume an old idle process will rejoin. Check `host_exit.json`, the new session
IDs and per-host status. On X2, verify service restoration before starting a
replacement service-supervised worker. Outstanding late completions still
follow the unchanged lease and duplicate rules.

A `projection_exceeds_budget` stop is incomplete and is recorded in
`launches.json`. It closes all host charging intervals at the stop timestamp.
Do not leave idle hosts waiting until the wall deadline. After an operator
resume go, run the identical coordinator command before the original deadline,
then rejoin the qualified hosts. Arrange for any added host to join while the
other hosts are still configuring, so the projection can consider them together.
The new attempt re-evaluates the present non-draining hosts with their chosen
configurations. No joined host, or a host still configuring, remains a wait.
No manifest edit, new deadline or projection multiplier is permitted.

The operational journal is `dispatch.sqlite` with its SQLite WAL files. Preserve
the whole root, including those files. Never replace the database with
`pull_state.json`: it is a diagnostic checkpoint at start, phase/control
changes and terminal transitions. Status files are bounded-rate snapshots. The coordinator checkpoints the WAL periodically; sealed, chained
logical events remain in the database. Resume verifies the journal and rebuilds
completed jobs from the ordinary output and completion-record files. Do not copy
or alter a live SQLite database piecemeal.

`service.lock` is per checkout, not global across X2 checkouts. The no-other-
runner check is required. The supervisor records `llm down` and restores
`llm up` in its exit handling; verify `host_x2/service.json` and `llm status` afterward.
SIGKILL or a machine crash cannot run a finally block. After such a failure,
confirm all runner processes have stopped, preserve the logs, and have the
operator restore the server with `llm up` and record that recovery. Never use
`pkill -f` with a pattern that could match the SSH shell.

## 4a. Qualify and register hosts for each launch

Do this after `check_spec SPEC ROOT` and before the launch's go. It prepares no
scientific completion. The sealed qualification selection is outside the launch
root. Every candidate needs at least 20 distinct matching jobs covering every
kind it will run. Registered reference outputs, if present, take priority;
otherwise both hosts execute the same deterministic short fixture jobs. Neither
qualification outputs nor configuration jobs count toward scientific results.

SSH must work noninteractively from WSL, or another remote worker, to
`yotko@100.96.61.55`. The X2 worker starts a local child process and needs no
SSH login to itself or new key in its own `authorized_keys`. Keep remote
workers' private keys in their SSH directories, never in the repository.
Check server host keys with the operator. No new
service, port, package, pull, fetch, or environment change is needed. Optionally
restrict the authorized key to the fixed `v3.multihost_a11 rpc ROOT --stream` command;
qualification bundle transfers then need a separately approved SSH key.

On WSL create a fresh `~/v3_a10` checkout at `<CODE_COMMIT>` using section 1's
checkout and committed-byte checks. Use the frozen phaseb environment and the
same paths relative to `simulation/`. Copy the committed pin and input records
by hash. No job envelope is rewritten when a host has a different home path.
Every worker receives read-only, hash-verified snapshots before each phase.
Those include calibration, tables and embedded labels/receipts, probe records,
A1 source completions, and prior fit completions for plain validation.

For each launch set `SPEC`, `RUN_ROOT`, and a unique `QUAL` directory on X2:

```bash
export SPEC="$EST_SPEC" RUN_ROOT="$EST_RUN"
export QUAL="$A10_ROOT/qualification/estimate"
mkdir -p "$QUAL"
"$PYTHON" -B -m v3.qualification_a11 build "$SPEC" "$RUN_ROOT" "$QUAL/plan.json"
# X2 supervisor stands its service down and restores it for each measurement.
"$PYTHON" -B -m v3.qualification_a11 run "$QUAL/plan.json" "$QUAL/reference.json" \
  --profile x2 --workers 16 --cpu-budget 32 --mode normal
"$PYTHON" -B -m v3.qualification_a11 run "$QUAL/plan.json" "$QUAL/x2.json" \
  --profile x2 --workers 16 --cpu-budget 32 --mode normal
"$PYTHON" -B -m v3.qualification_a11 compare "$QUAL/plan.json" "$QUAL/reference.json" \
  "$QUAL/x2.json" "$QUAL/x2_evidence.json"
```

The same X2 host is the reference at relative throughput 1; its independent
re-execution supplies the bit-identity check. Candidate throughput is measured
from elapsed parallel qualification work. The actual launch configuration test
still chooses worker counts independently. Do not substitute the old 0.37
planning input for measured qualification evidence.

From WSL, pull the plan and its `plan_files` bundle using SSH. Set the same
relative `QUAL`, and use the remote checkout's phaseb Python and thread limits:

```bash
cd "$HOME/v3_a10/simulation"
export PATH="$HOME/miniforge3/envs/phaseb/bin:$HOME/.local/bin:$PATH"
export PYTHON="$HOME/miniforge3/envs/phaseb/bin/python3.13"
export QUAL=v3/runs/a10_stage1/qualification/estimate
mkdir -p "$QUAL"
scp -r yotko@100.96.61.55:v3_a10/simulation/"$QUAL"/plan.json \
       yotko@100.96.61.55:v3_a10/simulation/"$QUAL"/plan_files "$QUAL/"
"$PYTHON" -B -m v3.qualification_a11 run "$QUAL/plan.json" "$QUAL/wsl.json" \
  --profile local --workers 12 --cpu-budget 16 --mode work
scp "$QUAL/wsl.json" yotko@100.96.61.55:v3_a10/simulation/"$QUAL"/wsl.json
```

Back on X2, compare and inspect only pass status, counts, identity/fingerprint
hashes, memory and throughput. Do not open scientific result values.

```bash
"$PYTHON" -B -m v3.qualification_a11 compare "$QUAL/plan.json" "$QUAL/reference.json" \
  "$QUAL/wsl.json" "$QUAL/wsl_evidence.json"
# Separate explicit operator approval of each exact evidence record, once per root.
"$PYTHON" -B -m v3.multihost_a11 approve "$RUN_ROOT" "$QUAL/x2_evidence.json" \
  --operator '<APPROVING_OPERATOR>' --when '<APPROVAL_UTC>'
"$PYTHON" -B -m v3.multihost_a11 approve "$RUN_ROOT" "$QUAL/wsl_evidence.json" \
  --operator '<APPROVING_OPERATOR>' --when '<APPROVAL_UTC>'
```

Approval appends a chained sealed entry under `machine_register/`. Never edit,
replace or commit that register. A failed proof is not usable. Fingerprint,
code identity or implementation-commit mismatches at join refuse the host.
Adding a qualified, approved host during the launch is covered by the launch's
go; it requires a new register entry, not a new root or amended job set.

The cost-class builder in `check_spec` uses only the sealed P2 mean worker
seconds and job declarations. Validation measurements are bundle costs, so fit
and validation use the corresponding bundle weight; census uses the larger of
the two declared route-bundle weights. Labels use their three-replicate bundle
weight. These are scheduling classes, not invented per-stage timings. Ties use
job IDs. The outer spec seal binds every class and the projection seal.
Memory comes from the producer's declared per-phase estimates; rerun specs use
P2's estimate because they do not declare one. Observed peaks can raise it.
Qualification can cover selected kinds using `qualification_a11 build --kind`.
Plain validation also needs that host's fit configuration for the existing
projection subtraction. A host skips unqualified phases or configurations that
do not fit memory, and leaves when no remaining qualified phase needs it.

## 5. Estimate the nominal family, then assemble

Build the full registered manifest. Its legacy-shaped filenames are required
by the A4/A5 source readers; its contents and producer are A10.

```bash
"$PYTHON" -B - <<'PY'
import os
from collections import Counter
from pathlib import Path
from v3.artifacts import atomic_json, read, seal, file_hash
from v3.tables_a10 import estimation_spec
spec = estimation_spec('nominal', os.environ['CAL'], registration=read(os.environ['PIN']), wall_hours=69.50)
counts = Counter(j['config']['setting_name'] for j in spec['jobs'])
assert counts == {'primary': 2625, 'double_population': 105, 'double_length': 105}
assert len(spec['jobs']) == 2835
assert sum(len(j['config']['scoring']) for j in spec['jobs'] if j['config']['setting_name'] == 'primary') == 19500
target = Path(os.environ['EST_SPEC'])
assert not target.exists() or read(target) == seal(spec)
atomic_json(target, seal(spec))
print({'jobs': 2835, 'primary_scoring_rows': 19500, 'settings': dict(counts),
       'spec_sha256': file_hash(target), 'wall_seconds': spec['wall_seconds']})
PY
check_spec "$EST_SPEC" "$EST_RUN"
```

Expected: 105 physical `(rr, capability)` contexts, 25 rules, 2,835 jobs and
19,500 primary scoring rows. The 15 capabilities are
`1, 1.2, 1.5, 1.8, 2, 2.25, 2.5, 2.7, 3, 3.375, 3.75, 4, 4.05, 4.5, 5`.
Keep every job's full settings. The k-star 1.5 and 2.3 scoring rows are already
included in the shared nominal simulations.

After the operator's estimation go, with the 69.50-hour reservation:

```bash
launch_x2 "$EST_SPEC" "$EST_RUN" 2835 a10_stage1_estimate.json
# After it stops:
check_done "$EST_SPEC" "$EST_RUN"
```

The exact board command is expanded by `launch_x2` with total 2835 and
`a10_stage1_estimate.json`. Output envelopes and durable records are under
`$EST_RUN/table/{outputs,records}`. The source manifest is already at the
required `$SOURCE/tables_A1_manifest.json`. Apply section 4's same-root resume
rules on interruption; do not assemble an incomplete family.

Assembly is a local producer operation, not another worker batch. It reads
the scientific outputs internally and prints only identity and row count:

```bash
"$PYTHON" -B - <<'PY'
import os
from pathlib import Path
from v3.artifacts import read, unseal, code_identity, file_hash
from v3.production_runner import completed
from v3.tables_a10 import assemble, verify_estimation_source
source = Path(os.environ['SOURCE']); root = Path(os.environ['EST_RUN'])
spec = unseal(read(os.environ['EST_SPEC']))
outputs = [completed(root/'table', j, code_identity()) for j in spec['jobs']]
assert len(outputs) == 2835 and all(o is not None for o in outputs)
target = source/'v3_rerun_tables_A1.json'
doc = assemble(outputs, read(os.environ['CAL']), target, 'nominal', registered=True)
assert len(unseal(doc)['rows']) == 19500
verify_estimation_source(source, os.environ['CAL'], registered=True)
print({'rows': 19500, 'table_sha256': file_hash(target), 'table_seal': doc['sha256']})
PY
```

Do not invoke an old A1 producer or loader exception on this file. Estimation
screens may fail; A4 subsequently rebuilds the specified statuses, without
waiving any screen. Preserve failed rows. A failed assembly or source check
stops progression. Retrying a pure producer against identical complete inputs
is allowed; its frozen-target checks must pass. No separate watchdog is needed
for assembly: the estimation board remains complete, with its producer check
recorded separately.

## 6. Prepare A10 validation, run the A4 producer, publish

```bash
"$PYTHON" -B - <<'PY'
import os
from collections import Counter
from pathlib import Path
from v3.artifacts import read, seal, atomic_json, file_hash
from v3.tables_a10 import prepare_validation
plan = prepare_validation(os.environ['SOURCE'], os.environ['CAL'],
                          registration=read(os.environ['PIN']), wall_hours=525.87,
                          probe_root=os.environ['PROBE'])
counts = Counter(j['config']['phase'] for j in plan['jobs'])
assert counts['census'] == 2835
plain = counts['fit']; fv = counts['validate_fv_primary'] + counts['validate_fv_double_population']
assert plain + fv == 2835 and counts['validate_plain'] == 3 * plain
assert len(plan['jobs']) == 5 * plain + 2 * fv
assert plan['probe_seed_count'] > 0 and plan['settings_override'] is None
target = Path(os.environ['VAL_SPEC'])
assert not target.exists() or read(target) == seal(plan)
atomic_json(target, seal(plan))
print({'jobs': len(plan['jobs']), 'phases': dict(counts), 'M': plan['M'], 'M_FV': plan['M_FV'],
       'probe_seed_count': plan['probe_seed_count'], 'spec_sha256': file_hash(target)})
PY
check_spec "$VAL_SPEC" "$VAL_RUN"
export VAL_N=$("$PYTHON" -B -c 'import sys; from v3.artifacts import read,unseal; print(len(unseal(read(sys.argv[1]))["jobs"]))' "$VAL_SPEC")
```

Expected counts are conditional on the producer's routes, not known in advance:
with P plain and F FV estimation jobs, `P+F=2835`, the plan has `5P+2F` jobs
between 5,670 and 14,175. Census has exactly 2,835. M and M_FV are pinned before
validation data. The full plan and seed checks cover primary and sensitivity
jobs and every capability. No route is selected by the operator.

Review the section 3 route qualification and remaining label reservation before
go. After the operator's validation go:

```bash
launch_x2 "$VAL_SPEC" "$VAL_RUN" "$VAL_N" a10_stage1_validation.json
# After it stops:
check_done "$VAL_SPEC" "$VAL_RUN"
"$PYTHON" -B -m v3.table_validation_a4 publish \
  "$VAL_SPEC" "$VAL_RUN" "$SOURCE" "$CAL" "$TABLE"
sha256sum "$TABLE" "${TABLE%.json}.compatibility.json" "${TABLE%.json}.cell_results.json"
```

The runner uses the five phases in the plan: fit, plain validation, primary FV
validation, larger-memory FV validation, and census. Configuration tests run
before scientific dispatch, and each phase is preceded by a projection of all
remaining work. Every nonempty phase gets the recorded nondeterminism recheck.
The watchdog uses total `$VAL_N` and `$HOME/status-board/a10_stage1_validation.json`.

The publisher rechecks input hashes, seeds, M, M_FV, the code and every durable
stage output. Expected publication: 19,500 primary rows, zero `not_estimable`,
passed sensitivity status, and the two sealed siblings. A production-loader
failure leaves an unpublished candidate under the run root. It is not a
published family and must not be relabeled or substituted. Stop on that
finding. On interruption apply section 4; do not reset a projection stop or
freeze a partial result. Do not run the optional A4 reporting command here.

## 7. A5 identity record and its A11 record-only commit

After successful A4 publication, create exactly this plain identity record:

```bash
"$PYTHON" -B - <<'PY'
import os, subprocess
from pathlib import Path
from v3.artifacts import read, unseal, file_hash, atomic_json, code_identity
from v3.table_labels_a5 import load_a4_publication
table = Path(os.environ['TABLE']); document = read(table); payload = unseal(document)
assert payload['code_hash'] == code_identity() == os.environ['EXPECTED_CODE']
record = {'family_file_sha256': file_hash(table), 'table_seal_sha256': document['sha256'],
          'receipt_file_sha256': file_hash(table.with_suffix('.compatibility.json')),
          'sidecar_file_sha256': file_hash(table.with_suffix('.cell_results.json')),
          'producing_commit': subprocess.check_output(['git','rev-parse','HEAD']).decode().strip(),
          'code_hash': payload['code_hash']}
load_a4_publication(table, record)
target = Path(os.environ['IDENTITY'])
assert not target.exists() or read(target) == record
atomic_json(target, record)
print({'identity_file_sha256': file_hash(target), 'code_identity': code_identity()})
PY
```

A11 item 2 permits this record-only commit inside `~/v3_a10` after the
operator approves the exact file and hash. There is no fetch, pull or code
change. A5 requires the path tracked with bytes equal to `git show HEAD:<path>`.
Obtain the commit go before the next command block.

The only necessary mid-sequence record commit identified in the code is:

| File | Why | Effect on identity |
| --- | --- | --- |
| `simulation/v3/runs/a10_stage1/nominal/family_identity.json` | A5 registered preparation checks this exact record against HEAD | Changes HEAD; does **not** change `code_identity()` |

After the operator approves this exact record and its hash, make the commit:

The X2 has no global Git identity. Set the operator's name and email, the same
ones the public repository's commits use, in this checkout only. Add no other
author or attribution line. Use the actual commit date in the message.

```bash
# Operator go required for this exact single-file commit.
git -C "$A10CO" config user.name '<OPERATOR_GIT_NAME>'
git -C "$A10CO" config user.email '<OPERATOR_GIT_EMAIL>'
git -C "$A10CO" add -f -- simulation/v3/runs/a10_stage1/nominal/family_identity.json
test "$(git -C "$A10CO" diff --cached --name-only)" = \
  'simulation/v3/runs/a10_stage1/nominal/family_identity.json'
# Expected: only the single path above. Do not proceed otherwise.
git -C "$A10CO" commit -m "Record A10 nominal family identity for A5 preparation, $(date +%F)"
"$PYTHON" -B - <<'PY'
import os, subprocess
from v3.artifacts import read, code_identity, verify_registration
from v3.tables_a10 import family_instrument
from v3.table_labels_a5 import require_committed_identity
assert code_identity() == os.environ['EXPECTED_CODE']
verify_registration(read(os.environ['PIN']), instrument=family_instrument('nominal'))
require_committed_identity(os.environ['IDENTITY'], a10=True)
print({'record_commit': subprocess.check_output(['git','rev-parse','HEAD']).decode().strip(),
       'code_identity': code_identity(), 'committed_identity': 'verified'})
PY
```

Record the new full HEAD, the record SHA256, approval and unchanged code
identity in the execution log. Copy this exact record to the operator's main
checkout of the public repository at the same relative path and commit those
same bytes there under a separate operator go. On that checkout, compare
`sha256sum simulation/v3/runs/a10_stage1/nominal/family_identity.json` with the
X2 hash, stage only that file, check the staged path list, and commit it with
the message above. Verify its committed bytes using `git show HEAD:<path>`
and SHA256. Record the public commit ID before A5 preparation. The two record
commits can have different commit IDs; their file bytes must match. Neither
changes the code identity. Do not fetch or pull that public commit into X2.

The corresponding commands in the operator's main checkout are:

```bash
export MAINCO='<OPERATOR_MAIN_CHECKOUT>'
export RECORD_SHA256='<HASH_RECORDED_ON_X2>'
export RECORD_REL=simulation/v3/runs/a10_stage1/nominal/family_identity.json
mkdir -p "$MAINCO/$(dirname "$RECORD_REL")"
scp "yotko@100.96.61.55:v3_a10/$RECORD_REL" "$MAINCO/$RECORD_REL"
test "$(sha256sum "$MAINCO/$RECORD_REL" | cut -d' ' -f1)" = "$RECORD_SHA256"
# Separate operator go for the public record commit, containing this file only.
git -C "$MAINCO" add -f -- "$RECORD_REL"
test "$(git -C "$MAINCO" diff --cached --name-only)" = "$RECORD_REL"
git -C "$MAINCO" commit -m "Record A10 nominal family identity for A5 preparation, $(date +%F)"
test "$(git -C "$MAINCO" show "HEAD:$RECORD_REL" | sha256sum | cut -d' ' -f1)" = "$RECORD_SHA256"
git -C "$MAINCO" rev-parse HEAD
```

No table, sidecar, labels, pin, run manifest or receipt needs a commit for this
sequence. They remain frozen, hashed run artifacts. No scientific values or
readings enter either record-only commit.

## 8. Prepare A5 labels at the declared 257.66-hour ceiling

Registered A10 labels require an explicit positive finite ceiling. It is
sealed into the plan and rechecked at publication. R4 retains exactly 24 hours.
Use the completed nominal family and the committed identity from section 7.
Review the prepared job count, projection and remaining stage budget before go.

```bash
"$PYTHON" -B - <<'PY'
import os
from pathlib import Path
from v3.artifacts import read, seal, atomic_json, file_hash
from v3.tables_a10 import family_instrument
from v3.table_labels_a5 import prepare
plan = prepare(os.environ['TABLE'], os.environ['VAL_RUN'], os.environ['VAL_SPEC'],
               os.environ['SOURCE'], os.environ['CAL'], os.environ['IDENTITY'],
               registration=read(os.environ['PIN']), wall_hours=257.66,
               a3_probe_root=os.environ['PROBE'], instrument=family_instrument('nominal'))
assert plan['declared_wall_hours'] == 257.66 and plan['wall_seconds'] == 257.66 * 3600
assert len(plan['jobs']) == plan['a5_seed_count'] == 3 * plan['fv_tables']
assert 0 <= plan['fv_tables'] <= 2625
assert plan['settings_override'] is None and plan['probe_seed_count'] > 0
target = Path(os.environ['LABEL_SPEC'])
assert not target.exists() or read(target) == seal(plan)
atomic_json(target, seal(plan))
print({'jobs': len(plan['jobs']), 'fv_tables': plan['fv_tables'], 'M': plan['M'],
       'spec_sha256': file_hash(target), 'declared_wall_hours': plan['declared_wall_hours']})
PY
check_spec "$LABEL_SPEC" "$LABEL_RUN"
export LABEL_N=$("$PYTHON" -B -c 'import sys; from v3.artifacts import read,unseal; print(len(unseal(read(sys.argv[1]))["jobs"]))' "$LABEL_SPEC")
# Only after this exact launch receives its own operator go:
launch_x2 "$LABEL_SPEC" "$LABEL_RUN" "$LABEL_N" a10_stage1_labels.json
# After it stops:
check_done "$LABEL_SPEC" "$LABEL_RUN"
"$PYTHON" -B -m v3.table_labels_a5 publish \
  "$LABEL_SPEC" "$LABEL_RUN" "$VAL_RUN" "$SOURCE" "$CAL" "$LABELS"
sha256sum "$LABELS"
```

Expected: three jobs per primary FV table, at most 7,875 jobs, with the exact
number and M pinned during preparation. Zero FV jobs is supported by the A10
plan's empty phases. No guessed historical count of 252/756 applies. A5
rechecks the A10 source, committed identity, A4 plan/receipt/census hashes,
the forbidden seeds, code identity, and frozen settings. The producer writes
labels for every tested cell and preserves the table, receipt and sidecar.
Keep the sealed label artifact and hash; do not run `table_labels_a5 report`.

The watchdog total is `$LABEL_N`, output `$HOME/status-board/a10_stage1_labels.json`. On a
projection stop, interruption, or any identity failure, use section 4. Do not
split or reset the sealed plan to escape its declared ceiling. Preserve its
completed records and original deadline under section 4.

## 9. Bind the A10 receipt and check all nominal instruments

This pure publication step requires completed A4 and A5 artifacts. It uses
the validation/labels reserve and has no separate runner or watchdog.

```bash
"$PYTHON" -B - <<'PY'
import os
from pathlib import Path
from v3.artifacts import read, file_hash, unseal
from v3.tables_a10 import finalize_receipt
from v3.instrument import Instrument
from v3.production_tables import ProductionTables
path = Path(os.environ['TABLE'])
receipt = finalize_receipt(path, os.environ['LABELS'])
table = ProductionTables(path, calibration_hash=read(os.environ['CAL'])['sha256'], registered=True)
for k in (1.5, 1.8, 2.3):
    table.require_a10(Instrument('A10', k, 'linear'))
assert len(table.rows) == 19500
print({'rows': len(table.rows), 'instruments_checked': 3,
       'receipt_seal': receipt['sha256'], 'receipt_sha256': file_hash(path.with_suffix('.a10_receipt.json')),
       'table_sha256': file_hash(path), 'labels_sha256': file_hash(os.environ['LABELS'])})
PY
```

The required file set is the table JSON, `.compatibility.json`,
`.cell_results.json`, `.a10_receipt.json`, and the labels JSON, plus the source
manifests, identity record and completion records that prove them. The A10
receipt embeds and hashes the validation receipt and labels; keep the separate
originals too. Any missing row, failed screen, incomplete per-capability label
set, changed seal, or other producer identity refuses registered use. No A1 or
R4 A4 family may be substituted. Repeating receipt creation is allowed only
when the existing receipt is identical.

## 10. Build the five stage 1 run manifests

The builder calls the unchanged job builders and preserves counterpart seeds.
It writes sealed, registered specs only after A10/A11 registration verifies.
All five ceilings are required. No stage 2 jobs are emitted. `main` holds
R1 prime, refinement and R2 prime together, satisfying the gate checker's
complete 24,900-job family, including IDs, categories and pairing.

```bash
"$PYTHON" -B - <<'PY'
import os
from pathlib import Path
from v3.artifacts import atomic_json, read
ceilings = dict(main=50.49, k1p5=10.94, k2p3=10.93, weight_corner=44.34, horizon=10.27)
target = Path(os.environ['A10_ROOT'])/'run_ceilings.json'
assert not target.exists() or read(target) == ceilings
atomic_json(target, ceilings)
PY
"$PYTHON" -B -m v3.tables_a10 stage1-runs \
  --calibration "$CAL" --tables "$TABLE" --pin "$PIN" \
  --ceilings "$A10_ROOT/run_ceilings.json" --output-dir "$A10_ROOT/specs"
"$PYTHON" -B - <<'PY'
import os
from pathlib import Path
from v3.artifacts import read, unseal, file_hash, digest, atomic_json
root = Path(os.environ['A10_ROOT'])
counts = dict(main=24900, k1p5=4400, k2p3=4400, weight_corner=17600, horizon=1800)
inventory, ids, seeds = {}, set(), set()
for name, count in counts.items():
    path = root/'specs'/(name+'.json'); spec = unseal(read(path))
    assert len(spec['jobs']) == count
    current_ids = {j['id'] for j in spec['jobs']}
    current_seeds = {j['seed'] for j in spec['jobs']}
    assert len(current_ids) == len(current_seeds) == count
    assert not (ids & current_ids) and not (seeds & current_seeds)
    ids.update(current_ids); seeds.update(current_seeds)
    assert {j['config']['steps'] for j in spec['jobs']} == ({1000} if name == 'horizon' else {500})
    inventory[name] = dict(jobs=count, spec_sha256=file_hash(path),
                           jobs_digest=digest(spec['jobs']), wall_seconds=spec['wall_seconds'])
assert len(ids) == len(seeds) == 53100
atomic_json(root/'checks/stage1_run_manifest_inventory.json', inventory)
print(inventory)
PY
```

The configuration profiles retain the original runbook's choices: actual
rerun jobs shortened to five steps for the configuration test only, two rounds,
two jobs per worker, one numerical thread, X2 candidates 8/12/16/24/32 and
local candidates 2/4/8/12. The registered 500-step and horizon 1,000-step
jobs remain full length. Keep the same phase, category and job paths on either
machine. There is no A7 ledger; section 3 supplies stage accounting.

Run the before gates for all three declared instruments, without opening any
registered run output:

```bash
for k in 1.5 1.8 2.3; do
  "$PYTHON" -B - "$k" "$A10_ROOT" <<'PY'
import sys
from pathlib import Path
from v3.artifacts import atomic_json
from v3.instrument import Instrument
atomic_json(Path(sys.argv[2])/('instrument_k'+sys.argv[1]+'.json'), Instrument('A10',float(sys.argv[1]),'linear').declaration())
PY
  "$PYTHON" -B -m v3.gates --phase before --calibration "$CAL" \
    --calibration-sha256 fd86358a39e3b643fb9adc4e81a2372915ca50a1866e9b0e330a874b41746e01 \
    --instrument-json "$A10_ROOT/instrument_k$k.json" --a10-pin "$PIN" \
    --output-dir "$A10_ROOT/checks/before_k$k"
done
```

Expected: every before gate passes, after gates remain `not_run`, and no
result is yet citable. A failure is a stop; do not use `--fixtures` or
`--validation` to make a registered gate pass. These are small conformance
checks, not extra registered simulation batches; record their wall time in
the operations ledger.

## 11. Execute the five run components

Each line below is a **separate launch and a separate operator go**. First
perform section 4a's qualification and approval for that launch root. Do not
paste the list as a batch. For each, run `check_spec` first, review the ceiling
reservation and preflight result, obtain go, then call `launch_x2`. Run
`check_done` after completion and reconcile hours before the next launch.

```bash
# Main: 24,900 R1 prime, refinement and R2 prime runs, 50.49 X2 hours.
check_spec "$A10_ROOT/specs/main.json" "$A10_ROOT/runs/main"
launch_x2 "$A10_ROOT/specs/main.json" "$A10_ROOT/runs/main" 24900 a10_stage1_main.json
check_done "$A10_ROOT/specs/main.json" "$A10_ROOT/runs/main"

# k-star 1.5: 4,400 runs, 10.94 X2 hours.
check_spec "$A10_ROOT/specs/k1p5.json" "$A10_ROOT/runs/k1p5"
launch_x2 "$A10_ROOT/specs/k1p5.json" "$A10_ROOT/runs/k1p5" 4400 a10_stage1_k1p5.json
check_done "$A10_ROOT/specs/k1p5.json" "$A10_ROOT/runs/k1p5"

# k-star 2.3: 4,400 runs, 10.93 X2 hours.
check_spec "$A10_ROOT/specs/k2p3.json" "$A10_ROOT/runs/k2p3"
launch_x2 "$A10_ROOT/specs/k2p3.json" "$A10_ROOT/runs/k2p3" 4400 a10_stage1_k2p3.json
check_done "$A10_ROOT/specs/k2p3.json" "$A10_ROOT/runs/k2p3"

# A6 weight corners: 17,600 runs, 44.34 X2 hours.
check_spec "$A10_ROOT/specs/weight_corner.json" "$A10_ROOT/runs/weight_corner"
launch_x2 "$A10_ROOT/specs/weight_corner.json" "$A10_ROOT/runs/weight_corner" 17600 a10_stage1_weight_corner.json
check_done "$A10_ROOT/specs/weight_corner.json" "$A10_ROOT/runs/weight_corner"

# A6 horizon: 1,800 runs of 1,000 steps, 10.27 X2 hours.
check_spec "$A10_ROOT/specs/horizon.json" "$A10_ROOT/runs/horizon"
launch_x2 "$A10_ROOT/specs/horizon.json" "$A10_ROOT/runs/horizon" 1800 a10_stage1_horizon.json
check_done "$A10_ROOT/specs/horizon.json" "$A10_ROOT/runs/horizon"
```

`launch_x2` returns after detaching, so wait for the board and launch status
before running its following `check_done`. For status/control set `RUN_ROOT`
to that line's root. The watchdog filename and total are the last two
arguments on each line. Job artifacts are under each root's declared phase:
`rerun`, `a10_arm`, `a6_weight_corner`, or `a6_horizon`.

Each completion check validates all output byte hashes and records their
inventory without reporting scientific results. Expected total: 53,100
registered runs, of which the paired main/refinement group has 24,900. All
use the same completed nominal table family; only declared scoring or run
parameters differ. Do not inspect early survival, yield, admission, shadow,
transition, welfare, or Theta diagnostics. They are evidence for the later
sealed step. Interrupted or failed components follow section 4, preserving
completed records and their original seeds.

## 12. Multi-host sharing and mandatory rehearsal

Whole-component splitting is no longer required. Each launch has one X2 root,
one coordinator and the existing phase barriers. Worker hosts pull from that
root; they never publish registered records locally or merge independent roots.
The coordinator's `status.json` adds per-host counts, configuration choices,
participation intervals and worker-seconds. The existing watchdog watches the
coordinator PID. Verify its board integration during rehearsal.

The X2 worker explicitly selects `--local`, which retains a direct child command
(`v3.multihost_a11 rpc ROOT --stream --local`) in this checkout. WSL and other
remote workers retain the same RPC command over SSH, without the RPC `--local`
flag. Both transports use the same framed JSON requests and process reuse.
Transport is never inferred from the profile: WSL still uses `--profile local`
with `--coordinator` and `--checkout`. A worker's `--local` flag cannot be combined
with either of those SSH options. Under the root lock, every local request
checks that `platform.node()` matches the coordinator machine recorded in the
latest `launches.json` entry, and that any request host matches it. A missing
machine record or mismatch refuses the request. Qualification, approval,
identity checks, configuration, leases and charging apply to the X2 worker
exactly as to a remote worker. The operator verified SQLite 3.52.0 in both
phaseb environments; no environment change is required.

The launch helper waits for the current attempt's machine record before it
starts the local worker. A startup failure stops that sequence; inspect the
coordinator log and use the existing interruption/resume procedure.

No listener, service, port or package is added. Claims request up to the host's free slots,
with memory checked after each provisional lease. A retry carries the same
request ID and receives the same durable batch, including after a lost reply.
One heartbeat renews all that session's active leases. Each request still checks
the exact running identity and takes the root lock. Operational status files
refresh at most once every two seconds during ordinary work, with immediate
terminal updates; the watchdog must allow that diagnostic delay.


After the launch go and `launch_x2`, join WSL from WSL itself:

```bash
cd "$HOME/v3_a10/simulation"
export PATH="$HOME/miniforge3/envs/phaseb/bin:$HOME/.local/bin:$PATH"
export PYTHON="$HOME/miniforge3/envs/phaseb/bin/python3.13"
export RUN_ROOT=v3/runs/a10_stage1/nominal/source/tables_A1
export SCRATCH=v3/runs/a10_stage1/host_wsl/estimate
mkdir -p "$SCRATCH"
setsid nohup "$PYTHON" -B -m v3.host_a11 \
  --coordinator yotko@100.96.61.55 --checkout /home/yotko/v3_a10 \
  --root "$RUN_ROOT" --scratch "$SCRATCH" --profile local \
  --workers 12 --cpu-budget 16 --mode work </dev/null >>"$SCRATCH/worker.log" 2>&1 &
printf '%s\n' "$!" > "$SCRATCH/supervisor.pid"
```

Twelve is the workstation upper bound. Its own configuration test and memory
headroom can select fewer. One numerical thread per worker is verified. Do not
increase a cap to force a 15 GB job onto a host that lacks memory. A host can
join mid-phase. On X2, use its exact `platform.node()` string for controls:

```bash
"$PYTHON" -B -m v3.production_runner control "$RUN_ROOT" --host '<WSL_HOST>' --mode work --max-workers 12
"$PYTHON" -B -m v3.production_runner control "$RUN_ROOT" --host '<WSL_HOST>' --stop drain
# Wait for host running=0 and an ended session. The host leaves automatically.
# These controls also work while the approved host is departed, before rejoin:
"$PYTHON" -B -m v3.production_runner control "$RUN_ROOT" --host '<WSL_HOST>' --stop clear
```

An ended host is removed from active dispatch, not erased from the append-only
register or accounting. To remove it permanently, leave it drained. A differing
duplicate latches `nondeterminism_failure.json`; never clear it or publish that
root. An identical duplicate becomes an incidental cross-check. Configuration
or worker failures remain durable. A failed job retains the existing three-
attempt limit. After a network outage longer than a lease, the host terminates
its workers and must rejoin. A coordinator restart voids outstanding leases;
late hash-verified outputs from issued leases are still accepted or compared.

### 12a. Non-registered X2/WSL rehearsal, before any registered go

Use a distinct `v3/runs/a11_rehearsal` tree. This is a prerequisite, not evidence
that local loopback tests have qualified the real machines. Do not read outcomes.
Retain the exact plan, qualification, register, fault/restart timestamps, board
statuses, publication hashes and final receipt. No fixture artifact enters
stage 1. Each command below runs in the fresh A10 checkout at `<CODE_COMMIT>`.

The interpreter reports that the real X2/WSL rehearsal at ad675011, identity
dd1b1a88, passed qualification bit identity, toy publication and receipt, killed
remote recovery, coordinator restart with eight voided leases and retained
completions, drain, and an X2-to-WSL recheck. The corrections below address its
operational findings. Retain that evidence and verify the corrected release;
do not reuse an old-identity root with new code.

On X2, create the toy estimation plan. Its jobs keep A10 formulas and full toy
settings; no registered manifest is shortened:

```bash
export REH=v3/runs/a11_rehearsal
mkdir -p "$REH"
"$PYTHON" -B - <<'PY'
import os
from pathlib import Path
from v3.artifacts import atomic_json, seal, stable_job, read
from v3.tables_a10 import build_jobs, estimation_spec
from v3.multihost_a11 import freeze
r=Path(os.environ['REH']); cal='v3/runs/registered/v3_rerun_calibration.json'
toy=dict(groups=3, runs_per_group=2, particles=2, burn=30, measure=120)
jobs=build_jobs('sqrt', cal, settings_override=toy,
    kernel_override=dict(n_agents=64, carrying_capacity=640), rule_ids=['balanced'],
    physical_contexts=[(.064,1.),(.064,1.5)])
jobs=[stable_job(j['kind'],dict(j['config'],route='plain' if j['config']['kernel']['capability']==1. else 'fv'),
                j['tag'],j['index']) for j in jobs]
spec=estimation_spec('sqrt',cal,jobs=jobs,wall_hours=2)
spec=freeze(spec,read(os.environ['COST']),code_commit=os.environ['CODE_COMMIT'])
atomic_json(r/'source/tables_A1_manifest.json',seal(spec))
atomic_json(r/'toy_settings.json',toy)
atomic_json(r/'probe/seeds.json',{'non_registered':True,'seed':72349024834789})
print({'non_registered':True,'jobs':len(jobs),'allowance':spec['x2_equivalent_hours']})
PY
export SPEC="$REH/source/tables_A1_manifest.json" RUN_ROOT="$REH/source/tables_A1"
"$PYTHON" -B -m v3.multihost_a11 prepare "$SPEC" "$RUN_ROOT"
```

Perform section 4a's qualification, comparison and explicit host approvals with
`QUAL=$REH/qualification/estimate`. The X2 and WSL each re-execute at least 20
short jobs. Define this helper for the non-registered coordinator and each
restart. It attaches a new watchdog to the new PID with an absolute OUT file
and waits for the new launch record. Do not call the registered-only
`check_spec` or `launch_x2` helper for a rehearsal:

```bash
rehearsal_coordinator() {
  local previous_launches total runner_pid
  previous_launches=$("$PYTHON" -B - "$SPEC" "$RUN_ROOT" <<'PY'
import sys
from pathlib import Path
from v3.artifacts import read, unseal
assert unseal(read(sys.argv[1]))['registered'] is False
path=Path(sys.argv[2])/'launches.json'
print(len(read(path)) if path.exists() else 0)
PY
  )
  total=$("$PYTHON" -B - "$SPEC" <<'PY'
import sys
from v3.artifacts import read, unseal
print(len(unseal(read(sys.argv[1]))['jobs']))
PY
  )
  setsid nohup "$PYTHON" -B -m v3.production_runner launch "$SPEC" "$RUN_ROOT" \
    --profile x2 --workers 8 --threads 1 --cpu-budget 32 --mode normal \
    </dev/null >>"$RUN_ROOT/coordinator.log" 2>&1 &
  runner_pid=$!
  printf '%s\n' "$runner_pid" > "$RUN_ROOT/supervisor.pid"
  nohup "$HOME/status-board/run_watchdog.sh" "$runner_pid" \
    "$A10CO/simulation/$RUN_ROOT" "$total" "$HOME/status-board/$BOARD_NAME" 7200 \
    </dev/null >>"$RUN_ROOT/watchdog.log" 2>&1 &
  printf '%s\n' "$!" > "$RUN_ROOT/watchdog.pid"
  "$PYTHON" -B - "$RUN_ROOT" "$runner_pid" "$previous_launches" <<'PY'
import os, platform, sys, time
from pathlib import Path
from v3.artifacts import read
path=Path(sys.argv[1])/'launches.json'
while True:
    os.kill(int(sys.argv[2]),0)
    history=read(path) if path.exists() else []
    if len(history)>int(sys.argv[3]):
        assert history[-1]['machine']==platform.node()
        assert history[-1]['code_hash']==os.environ['EXPECTED_CODE']
        assert not history[-1].get('finished_epoch')
        break
    time.sleep(1)
PY
}
export BOARD_NAME=a11_rehearsal_estimate.json
rehearsal_coordinator
```

Start X2's worker with section 4's `v3.host_a11` command, and WSL with section
12's command, substituting the rehearsal root and separate rehearsal scratch.
The small toy jobs took about 0.2 seconds in the interpreter's rehearsal and
are too fast for reliable fault injection. Complete their publication pipeline
first. Use the separate longer drill below for killed-remote, restart and
drain cases. Each phase uses a distinct board basename, retained across that
phase's restarts.

Complete the toy table pipeline, using the same single-root publication calls:

```bash
"$PYTHON" -B - <<'PY'
import os
from pathlib import Path
from v3.artifacts import read,unseal,atomic_json,seal,code_identity
from v3.production_runner import completed
from v3.tables_a10 import assemble,prepare_validation
from v3.multihost_a11 import freeze
r=Path(os.environ['REH']); source=r/'source'; run=source/'tables_A1'
spec=unseal(read(source/'tables_A1_manifest.json'))
assert read(run/'launches.json')[-1]['complete']
assert not (run/'nondeterminism_failure.json').exists()
calpath='v3/runs/registered/v3_rerun_calibration.json'; cal=read(calpath)
outputs=[completed(run/'table',j,code_identity()) for j in spec['jobs']]
assert all(outputs)
assemble(outputs,cal,source/'v3_rerun_tables_A1.json','sqrt',jobs=spec['jobs'])
plan=prepare_validation(source,calpath,wall_hours=2,probe_root=r/'probe',
    settings_override=dict(read(r/'toy_settings.json'),census_measure=38))
plan=freeze(plan,read(os.environ['COST']),code_commit=os.environ['CODE_COMMIT'],extra_inputs=[str(r/'probe')])
atomic_json(r/'validation.json',seal(plan))
print({'non_registered':True,'validation_jobs':len(plan['jobs'])})
PY
```

Prepare `SPEC=$REH/validation.json`, `RUN_ROOT=$REH/validation`, then qualify,
approve, launch the coordinator and join both hosts as above. This phase must
copy its fit outputs before plain validation. Require a complete launch and
all per-phase checks before publishing. After workers restore the X2 service:

```bash
"$PYTHON" -B - <<'PY'
import os
from pathlib import Path
from v3.artifacts import read,unseal,atomic_json,seal,file_hash,code_identity
from v3 import table_validation_a4 as a4, table_labels_a5 as a5
from v3.tables_a10 import family_instrument
from v3.multihost_a11 import freeze
r=Path(os.environ['REH']); calpath='v3/runs/registered/v3_rerun_calibration.json'
assert read(r/'validation/launches.json')[-1]['complete']
assert not (r/'validation/nondeterminism_failure.json').exists()
family=r/'family.json'
a4.publish(unseal(read(r/'validation.json')),r/'validation',r/'source',read(calpath),family,registered=False)
doc=read(family)
atomic_json(r/'identity.json',dict(family_file_sha256=file_hash(family),table_seal_sha256=doc['sha256'],
    receipt_file_sha256=file_hash(family.with_suffix('.compatibility.json')),
    sidecar_file_sha256=file_hash(family.with_suffix('.cell_results.json')),
    producing_commit='nonregistered-rehearsal',code_hash=code_identity()))
plan=a5.prepare(family,r/'validation',r/'validation.json',r/'source',calpath,r/'identity.json',
    wall_hours=1.25,a3_probe_root=r/'probe',settings_override=read(r/'toy_settings.json'),instrument=family_instrument('sqrt'))
plan=freeze(plan,read(os.environ['COST']),code_commit=os.environ['CODE_COMMIT'],extra_inputs=[str(r/'probe')])
atomic_json(r/'labels_plan.json',seal(plan))
print({'non_registered':True,'label_jobs':len(plan['jobs']),'wall_hours':1.25})
PY
```

Repeat qualification/approval/launch/join for `SPEC=$REH/labels_plan.json`,
`RUN_ROOT=$REH/labels`. No identity-record commit is needed for toy publication.
Finally:

```bash
"$PYTHON" -B - <<'PY'
import os
from pathlib import Path
from v3.artifacts import read,unseal,file_hash
from v3.table_labels_a5 import publish
from v3.tables_a10 import finalize_receipt
r=Path(os.environ['REH']); cal=read('v3/runs/registered/v3_rerun_calibration.json')
assert read(r/'labels/launches.json')[-1]['complete']
assert not (r/'labels/nondeterminism_failure.json').exists()
publish(unseal(read(r/'labels_plan.json')),r/'labels',r/'validation',r/'source',cal,r/'labels.json',registered=False)
finalize_receipt(r/'family.json',r/'labels.json')
print({'non_registered':True,'family_sha256':file_hash(r/'family.json'),
       'labels_sha256':file_hash(r/'labels.json'),'receipt_sha256':file_hash(r/'family.a10_receipt.json')})
PY
```

For fault injection, build three fresh non-registered roots under a separate
drill folder. Every job has 24,000 measured steps, about a minute on X2 by the
interpreter's planning estimate. Record actual times; this is not a new cost
projection. The 24 physical contexts are declared pairs in the square-root
family: five shared capabilities at each of 0.060, 0.062, 0.064 and 0.066,
plus four additional declared capabilities at 0.064. The builder emits 42
jobs because the sensitivity settings at 0.064 are also declared. Every
drill job retains the full 24,000-step measurement length.

```bash
export DRILL="$REH/drill"
mkdir -p "$DRILL"
"$PYTHON" -B - <<'PY'
import os
from pathlib import Path
from v3.artifacts import atomic_json, seal, stable_job, read
from v3.tables_a10 import build_jobs, contexts, estimation_spec
from v3.multihost_a11 import freeze
r=Path(os.environ['DRILL']); cal='v3/runs/registered/v3_rerun_calibration.json'
physical=[(rr,c) for rr in (.060,.062,.064,.066) for c in (1.,1.5,2.25,3.375,5.)]
physical += [(.064,c) for c in (1.2,1.8,2.,2.5)]
assert len(set(physical))==24
assert set(physical) <= {(rr,c) for rr,alpha,c in contexts('sqrt')}
settings=dict(groups=3,runs_per_group=2,particles=2,burn=30,measure=24000)
jobs=build_jobs('sqrt',cal,settings_override=settings,
    kernel_override=dict(n_agents=64,carrying_capacity=640),rule_ids=['balanced'],
    physical_contexts=physical)
jobs=[stable_job(j['kind'],dict(j['config'],route='plain' if j['config']['kernel']['capability']==1. else 'fv'),
                j['tag'],j['index']) for j in jobs]
assert len(jobs)==42 and all(j['config']['settings']['measure']==24000 for j in jobs)
spec=freeze(estimation_spec('sqrt',cal,jobs=jobs,wall_hours=2),read(os.environ['COST']),
            code_commit=os.environ['CODE_COMMIT'])
for case in ('killed_remote','coordinator_restart','drain'):
    target=r/case/'spec.json'
    assert not target.exists() or read(target)==seal(spec)
    atomic_json(target,seal(spec))
print({'non_registered':True,'physical_contexts':24,'jobs_per_case':42,
       'measured_steps_per_job':24000,'cases':3})
PY
```

Run each case in its own root, completing it and restoring the X2 service
before the next case. Set `CASE` to `killed_remote`, then
`coordinator_restart`, then `drain`. For each case, prepare, qualify and approve
both hosts using section 4a with the case's `QUAL` path. The short qualification
and configuration jobs are separate from the 24,000-step drill jobs.

```bash
export CASE=killed_remote
export SPEC="$DRILL/$CASE/spec.json" RUN_ROOT="$DRILL/$CASE/root"
export QUAL="$DRILL/$CASE/qualification"
export BOARD_NAME="a11_drill_${CASE}.json"
"$PYTHON" -B -m v3.multihost_a11 prepare "$SPEC" "$RUN_ROOT"
# Complete section 4a's qualification and explicit approvals for this root.
rehearsal_coordinator
export SCRATCH="$RUN_ROOT/host_x2"
mkdir -p "$SCRATCH"
setsid nohup "$PYTHON" -B -m v3.host_a11 --local --root "$RUN_ROOT" \
  --scratch "$SCRATCH" --profile x2 --workers 8 --cpu-budget 32 --mode normal \
  </dev/null >>"$SCRATCH/worker.log" 2>&1 &
printf '%s\n' "$!" > "$SCRATCH/supervisor.pid"
```

On WSL, use the same case name and this four-worker command. This is a remote
SSH host; `--profile local` does not select the local transport.

```bash
cd "$HOME/v3_a10/simulation"
export PATH="$HOME/miniforge3/envs/phaseb/bin:$HOME/.local/bin:$PATH"
export PYTHON="$HOME/miniforge3/envs/phaseb/bin/python3.13"
export CASE=killed_remote
export RUN_ROOT="v3/runs/a11_rehearsal/drill/$CASE/root"
export SCRATCH="v3/runs/a11_rehearsal/host_wsl/drill/$CASE"
mkdir -p "$SCRATCH"
setsid nohup "$PYTHON" -B -m v3.host_a11 \
  --coordinator yotko@100.96.61.55 --checkout /home/yotko/v3_a10 \
  --root "$RUN_ROOT" --scratch "$SCRATCH" --profile local \
  --workers 4 --cpu-budget 16 --mode work </dev/null >>"$SCRATCH/worker.log" 2>&1 &
printf '%s\n' "$!" > "$SCRATCH/supervisor.pid"
```

For `killed_remote`, wait until both hosts have taken work and WSL has an
active lease. On WSL verify that this process group belongs to this case,
then kill it:

```bash
pid=$(cat "$SCRATCH/supervisor.pid")
ps -o pid,pgid,args -p "$pid"
kill -KILL -- "-$pid"
```

After its declared 120-second lease expires, check `lease_expired`, and that
X2 receives the same job ID and seed under a new lease. A partial remote file
must have no completion record. Restart the WSL worker with the identical
command. Require all 42 completions and the cross-host recheck before closing
this case. If the intended fault window is missed, create another fresh
non-registered root; never delete completions or extend a frozen deadline.

For `coordinator_restart`, use the separate case root and start both hosts
as above. Record the epoch, completed output hashes and active leases, then
kill only that case's coordinator on X2:

```bash
pid=$(cat "$RUN_ROOT/supervisor.pid")
ps -o pid,pgid,args -p "$pid"
kill -KILL "$pid"
# Observe the old watchdog's failure and exit before replacing it.
ps -o pid,pgid,args -p "$(cat "$RUN_ROOT/watchdog.pid")" || true
# Same SPEC, RUN_ROOT and BOARD_NAME; before the original deadline:
rehearsal_coordinator
```

The helper writes a new coordinator PID and attaches a new watchdog to it,
using the same `$HOME/status-board/a11_drill_coordinator_restart.json` OUT
file. The board shows the old failure until that attachment produces an
update. Restart both worker supervisors after they have stopped on session
loss; an old worker does not automatically rejoin. Verify the epoch increments,
old leases are `void_on_resume`, completed hashes/counts persist, and any
valid late completions are accepted or compared. X2 remains capped at 8 and
WSL at 4. Record their replacement session IDs and service restoration.

For `drain`, use its fresh root and start the same two hosts. While WSL has
active work, on X2 run:

```bash
"$PYTHON" -B -m v3.production_runner control "$RUN_ROOT" --host '<WSL_HOST>' --stop drain
"$PYTHON" -B -m v3.production_runner status "$RUN_ROOT"
# Verify no new WSL leases, its in-flight completions, and session end_reason=left.
```

Draining the last non-original host before the phase recheck deliberately
leaves the phase waiting. All 42 jobs may be complete while the original host
cannot perform its own cross-host recheck. Check the root and phase
`waiting_for` reason, phase and `since_epoch`; the wait persists without
silently completing or relaxing the check. Clear the departed host's persisted
drain and restart its worker:

```bash
"$PYTHON" -B -m v3.production_runner control "$RUN_ROOT" \
  --host '<WSL_HOST>' --mode work --max-workers 4 --stop clear
# On WSL restart the same four-worker host command for CASE=drain.
```

The wait must clear when the required host is ready, and the recorded check
must name different original and recheck hosts with `matched: true`. If the
original sampled job ran on WSL, arrange the symmetric case instead of
assuming X2 was original. Do not force the sampled job or alter its seed.
For each drill require `launches.json[-1].complete`, 42 durable completion
records, a matched phase check, no nondeterminism failure, and restored X2
service. Retain the manifests, qualification, register, journal, statuses,
stop/restart timestamps, output hash inventories and checks; read no outcomes.

Have the interpreter review the retained fault records, board behavior and
publication checks. The operator records approval in the sealed operational
`$A10_ROOT/checks/A11_rehearsal_approved.json`, naming the rehearsal roots,
their spec/evidence/receipt hashes, both hosts, the three fault/drain events,
reviewer, operator and UTC date. This approval is required before registered
use. Restore both X2 service-supervised qualification and worker sessions.

The interpreter first writes `$REH/review.json` with `passed: true`, the current
`code_hash`, `reviewer`, and a `cases` mapping with passed entries for
`qualification`, `killed_remote`, `coordinator_restart`, `drain`, `publication`
and `watchdog`. Each entry names its UTC timestamps, relevant lease/session IDs
and the supporting metadata paths and hashes. Keep failed attempts in the same
history. After the operator approves that exact review, create the marker:

```bash
export REHEARSAL_OPERATOR='<APPROVING_OPERATOR>'
export REHEARSAL_APPROVAL_UTC='<APPROVAL_UTC>'
"$PYTHON" -B - <<'PY'
import os
from pathlib import Path
from v3.artifacts import read, unseal, seal, atomic_json, code_identity, file_hash
r=Path(os.environ['REH']); review=read(r/'review.json')
required={'qualification','killed_remote','coordinator_restart','drain','publication','watchdog'}
assert review['passed'] and review['code_hash']==code_identity() and review['reviewer']
assert required <= set(review['cases'])
assert all(review['cases'][name]['passed'] for name in required)
operator=os.environ['REHEARSAL_OPERATOR']; when=os.environ['REHEARSAL_APPROVAL_UTC']
assert operator and when and '<' not in operator+when
paths=['source/tables_A1_manifest.json','validation.json','labels_plan.json',
       'family.json','labels.json','family.a10_receipt.json','review.json']
record={'schema':'v3-A11-rehearsal-approval-1','passed':True,'non_registered':True,
    'code_hash':code_identity(),'reviewer':review['reviewer'],
    'operator_approval':{'operator':operator,'when':when},
    'rehearsal_root':str(r.resolve()),'files':{p:file_hash(r/p) for p in paths}}
for case in ('killed_remote','coordinator_restart','drain'):
    spec=r/'drill'/case/'spec.json'; root=r/'drill'/case/'root'
    from v3.production_runner import completed
    jobs=unseal(read(spec))['jobs']
    assert len(jobs)==42 and all(completed(root/'table',j,code_identity()) is not None for j in jobs)
    assert read(root/'launches.json')[-1]['complete']
    assert read(root/'table/nondeterminism_check.json')['matched']
    assert not (root/'nondeterminism_failure.json').exists()
    record.setdefault('drills',{})[case]={'spec_sha256':file_hash(spec),
        'launches_sha256':file_hash(root/'launches.json'),
        'check_sha256':file_hash(root/'table/nondeterminism_check.json')}
target=Path(os.environ['A10_ROOT'])/'checks/A11_rehearsal_approved.json'
assert not target.exists() or read(target)==seal(record)
atomic_json(target,seal(record))
print({'passed':True,'approval_sha256':file_hash(target)})
PY
```

## 13. Blind closeout and the later sealed reading

The commands above may inspect job definitions, seeds, counts, hashes,
completion status, gate pass/fail status, resource measurements and receipts.
The producers and strict validators necessarily read scientific data internally.
Do not display that data, dump JSON objects containing rows, unpack gate
evidence, call result-report tools, or inspect rerun logs for scientific
outcomes. Do not open old registered rerun results. Cost-only P2 records never
become registered outcomes.

At closeout, retain:

- The exact source commit and code identity, design pin, constants and
  calibration identities, and exclusion-source inventories.
- The cost record, allocation revisions, every dated go and consumption entry.
- Every sealed spec, complete root, output hash inventory, configuration
  measurement, Context preflight, verified numerical thread limit, service
  record and nondeterminism check.
- The nominal source, published family and siblings, identity record and its
  approved X2 and public record commits, labels and final A10 receipt.
- A manifest of the five components and coordinator root locations, with
  exact job-set counts and no duplicates or missing jobs.

The **stage 1 reading is a later, separately authorized sealed computation**.
It needs the complete 24,900 paired main/refinement outputs and completion
records, the 8,800 k-star-arm outputs, the 17,600 weight-corner outputs and
1,800 horizon outputs, their specs and hashes, and `v3-gate-evidence-2` support.
It also needs the registered A8/A9/A10 reading rules and predictions, the
frozen A10 pin, nominal table/receipt/label identities, the applicable after
gates, verified stream pairing, and separately authorized R4 comparison
identities for A10's comparisons. Do not obtain or open R4 outcomes now.

`gates.build_index` now receives the single `main` root containing all 24,900
jobs. No main-component union is needed. Completed A10 evidence from an older
identity is accepted only through the A11 compatibility procedure below; every
root remains internally bound to its original single producer identity.
The separately authorized sealed reading still needs collection of the four
other arm roots and their machine-register/participation records with their immutable provenance. There is
no general cross-machine sealed reader or collector in this runbook.
`reading_a6` supplies arithmetic, not a full-stage sealed orchestrator. Compute
the later reading sealed and open it only on the operator's go.

Final operational checks: every allocated root is reconciled, partial outputs
remain distinguishable, no job is counted without its verified durable record,
the board reflects completion or a finding, and the model server is restored.
Run `llm status`. Do not change code, pins or quantities after seeing an output.

## 14. Compatibility contingency after a registered output exists

An execution-only repair changes the code identity. Do not edit the old
execution checkout or resume any unfinished root under the repair. Complete
or close its launch there first. Only completed launches can enter this
procedure. Proof work is non-registered, contains no readable outcomes, and
must be charged in the stage operations ledger. On X2 its service window must
be operator-gated and supervised with `llm down` and `llm up`.

1. In the unchanged producing checkout X, export its source manifest and a
   JSON list of the completed sealed spec and root paths. Include every completed
   phase being carried forward. Preserve and hash the export; no Git write
   occurs in that checkout. Each root must have a complete final launch record.
2. After the code repair is reviewed, use a fresh checkout at its exact code
   commit, Y, with no pull. Copy the immutable source artifacts with hash
   inventories or keep their old absolute paths accessible read-only. Specs
   and jobs are never rewritten to point somewhere else. Export Y's manifest,
   diff the manifests, and supply a reason for every changed manifest file.
3. Run the proof builder below. It freezes each full population before running
   the two smallest `digest(["A11-compatibility", phase, job_id])` jobs per
   phase/capability/setting, or all if fewer. It uses the runner's execute path,
   spawned work-mode workers and one numerical thread. The record stores only
   comparison hashes, statuses and execution metadata, not scientific values.
   A failure is final and cannot be approved or retried as the same attempt.
4. The interpreter reviews the record and source diff. The operator supplies
   approval only for a passed proof. Commit the approved record at the fixed
   path below in the repair checkout, with no code changes in that commit.
5. Commit the same record bytes to the public repository. Use a fresh execution
   checkout at the commit adding the approved record, then verify it before any
   old output is used. The old X checkout stays unchanged. New launches use new
   roots at Y and a design pin containing A10 and A11.

These commands are templates for that contingency, not part of the ordinary
first launch. Substitute the reviewed repair paths and producing checkout:

```bash
# In the producing X checkout, before leaving it unchanged:
"$PYTHON" -B - <<'PY'
from v3.artifacts import atomic_json, source_manifest, code_identity, digest
manifest = source_manifest()
assert digest(manifest) == code_identity()
atomic_json('v3/runs/a11_handoff/producing_source_manifest.json', manifest)
print({'producing_code_hash': code_identity()})
PY
# In the fresh repair Y checkout, create these plain JSON inputs under v3/runs:
# sources.json: [{"spec": "/absolute/X/completed-spec.json", "root": "/absolute/X/completed-root"}, ...]
# reasons.json: {"producing_source_manifest": <exported mapping>,
#                "reasons": {"v3/changed_file.py": "reviewed reason", ...}}
# No result file is opened by the operator while preparing these inputs.
# On a workstation (work mode, at most 12 workers):
"$PYTHON" -B -m v3.compatibility_a10 build \
  --sources v3/runs/a11_proof/sources.json --reasons v3/runs/a11_proof/reasons.json \
  --output v3/runs/a11_proof/proof.json --workers 12
# Expected: passed=True; a sealed proof and immutable .attempt.json selection.
# Stop on any failure. An unapproved proof cannot admit an identity.

# Only after the operator's approval of the exact proof and changed-file reasons:
"$PYTHON" -B -m v3.compatibility_a10 approve v3/runs/a11_proof/proof.json \
  --operator '<OPERATOR>' --date '<APPROVAL_DATE>'
export COMPAT_PATH=$("$PYTHON" -B - <<'PY'
from pathlib import Path
from v3.artifacts import read, unseal
from v3.compatibility_a10 import record_name
source = Path('v3/runs/a11_proof/proof.json'); record = unseal(read(source))
target = Path('v3/runs/registered')/record_name(record['producing_code_hash'], record['new_code_hash'])
assert not target.exists()
target.write_bytes(source.read_bytes())
print('simulation/' + target.as_posix())
PY
)
git -C .. add -f -- "$COMPAT_PATH"
test "$(git -C .. diff --cached --name-only)" = "$COMPAT_PATH"
git -C .. commit -m 'Record operator-approved A11 compatibility proof'
"$PYTHON" -B - <<'PY'
import os
from v3.artifacts import code_identity, file_hash, read, unseal
from v3.compatibility_a10 import accepted_identities, validate_record
path = os.environ['COMPAT_PATH'].removeprefix('simulation/')
record = unseal(read(path))
assert validate_record(path) == record['producing_code_hash']
assert record['producing_code_hash'] in accepted_identities()
assert record['new_code_hash'] == code_identity()
print({'record_sha256': file_hash(path), 'code_identity': code_identity(), 'accepted': True})
PY
```

For a proof on X2, replace the workstation build command with this supervisor
wrapper after its operator go. It uses the existing supervisor command helper
and service lease. No ordinary registered spec or unfinished root is resumed.
Do not run both build commands. The supervisor restores the server even on a
proof failure or a handled interruption; a machine crash still requires the
manual recovery in section 4.

```bash
if pgrep -af '[v]3[.]production_runner|[v]3[.]compatibility_a10'; then
  echo 'STOP: another batch may own the model-server state'; exit 1
fi
"$PYTHON" -B - <<'PY'
import os, platform, signal, subprocess, sys, time
from pathlib import Path
from v3.artifacts import ROOT, atomic_json, lease
from v3.service import command
assert platform.node().lower() == 'yotko-evo-x2' and platform.system() == 'Linux'
root = Path('v3/runs/a11_proof/service'); root.mkdir(parents=True, exist_ok=True)
def interrupted(number, frame):
    raise KeyboardInterrupt('A11 proof supervisor interrupted')
for sig in (signal.SIGINT, signal.SIGTERM):
    signal.signal(sig, interrupted)
with lease(ROOT/'service.lock'):
    record = dict(started_epoch=time.time(), host=platform.node(), down_exit_code=None, up_exit_code=None)
    try:
        record['down_exit_code'] = command(root, 'down')
        atomic_json(root/'service.json', record)
        assert record['down_exit_code'] == 0
        process = subprocess.Popen([sys.executable, '-B', '-m', 'v3.compatibility_a10', 'build',
                                    '--sources', 'v3/runs/a11_proof/sources.json',
                                    '--reasons', 'v3/runs/a11_proof/reasons.json',
                                    '--output', 'v3/runs/a11_proof/proof.json', '--workers', '12'],
                                   start_new_session=True)
        try:
            assert process.wait() == 0, 'compatibility proof failed'
        except BaseException:
            if process.poll() is None:
                os.killpg(process.pid, signal.SIGINT)
            process.wait()  # Never restore the server while proof workers remain.
            raise
    finally:
        for sig in (signal.SIGINT, signal.SIGTERM):
            signal.signal(sig, signal.SIG_IGN)
        record['up_exit_code'] = command(root, 'up')
        record['finished_epoch'] = time.time()
        atomic_json(root/'service.json', record)
        assert record['up_exit_code'] == 0, 'operator must restore the model server'
PY
llm status
```

After the identical record bytes are committed publicly, clone a new execution
checkout at that record commit as in section 1, substituting Y's full identity
and the reviewed pin. Repeat the final verification block there. The fixed
accepted-record pattern is `simulation/v3/runs/registered/A11_compatibility_*.json`;
its filename binds X and Y. Approval, passing proofs, exact tracked HEAD bytes,
target identity, complete changed-file hashes and current after-hashes must
all verify. R4 compatibility and runner resume checks are unchanged.

## 15. Remaining findings and document verification

1. **Program accounting:** the runner supports per-root deadlines, not a
   980-hour program ledger. Keep section 3's manual reservations and consumption
   records. Estimation and reruns still need the operator's budget projection
   check; they do not have A4's automatic remaining-work projection gate.
2. **Machine validation and collection:** the interpreter's ad675011 rehearsal
   established X2/WSL bit identity and the reported recovery/publication cases
   at dd1b1a88. It also found the cap, stop, wait and watchdog issues corrected
   here. Section 12a must verify the corrected release on the real machines;
   local tests cannot replace that check. Each component has one root, so no
   remote-result merge is needed. The later sealed reader still collects five
   component roots.
3. **Publication precondition:** the producers accept the extra completion
   fields unchanged. Their existing interfaces do not independently enforce a
   coordinator halt record; `check_done` and the explicit no-failure checks are
   mandatory before assembly/publication. Never publish an incomplete or halted
   root. No scientific publication screen has been weakened.

**Comparison convention to review:** root `result.code_hash` is process
provenance and is checked separately against the producing and running
identities. The canonical comparison excludes that field and the named
timing fields only. All nested scientific fields and the complete job remain
in the comparison. Envelope host, PID and runtime metadata are outside
`{job, result}`. The proof record declares these exclusions explicitly.

This Markdown file is outside `source_manifest()`. The A11 implementation and
exact-hash re-pins change the code identity to `c19b54f5bde7180c78a5eba4721c33527c47b84c4d93d2fae757fd3e31452810`.
R4 scientific behavior and the legacy 24-hour label contract remain unchanged.
The source identity must match committed release bytes before launch.

The runbook was checked locally against the A11 interfaces and supplied cost records; no X2
command, registered simulation, table-value inspection, network action or Git
write was performed during its preparation. The interpreter must still verify
the machine-specific inputs and watchdog on X2.

> A13 adoption notice, 2026-10-16: section 16 below is retained verbatim.
> Section 17 supersedes its old pins, planned identity, original publication
> path through adoption, and fallback. Follow section 17 for the current order.

## 16. A12 part 2: adopting the execution fixes mid-stage

This section implements option (b) in Amendment A12 part 2, committed as
`669daf23d18c2c0452d9d10c724b8c312eea50d6` on 2026-10-11. It supersedes
sections 8 to 11 only for the successful adoption branch below. Sections 1 to
14 remain the procedure at the producing identity and the fallback. Nothing
here authorizes a launch. Each record commit, qualification approval and
registered launch still needs its own operator go.

**Operator answers, 2026-10-12.** The clarification is committed as
`cc74ddd7c23fb02e95753f9e42cf49622d906200`. The unchanged-plan-hash,
seed, job-set and cost-class statement holds at a fixed identity. Adoption
changes the A5 label plan hash, label job identifiers and unused envelope
seeds, and the new specs' code identity and design pin fields. Scientific
inputs and simulation seeds remain unchanged, as do the 53,100 run jobs
with their identifiers and seeds, the 756 label jobs with their tables,
replicates and simulation seeds, and the cost classes. Check these before
launch; no old job or plan is rewritten.

Labels and the five new run launches pin `cc74ddd7` with committed note
SHA256 `dc1055002323d9afd20125533fe61c2ef7f2970042c43d9cc60b975620c40404`.
Completed estimation and validation retain their original pin. The stage 1
reading remains registered at `93474e00`. Section 16.3 retains the exact-byte
pin check and refuses any mismatch, including a later edit to the note.

The author performed no remote action, registered-output read, source edit
or Git write for this section. The local design-note file ends at A10; the
binding A12 text and clarification were read from locally available Git
objects. The full `cc74ddd7` commit ID and note SHA256 above were verified
directly from those committed bytes.

### 16.0. Required Python integer-text setting from adoption onward

**Operator decision, 2026-10-14:** run every stage 1 Python process from
A12 part 2 adoption onward, on every host, with `PYTHONINTMAXSTRDIGITS=0`.
"I agree, it's a pay now or pay later situation." Apply this subsection
before the adoption's first Python command, including when reusing commands
from earlier sections; it supersedes section 4a's statement that no environment
change is needed. It remains applicable to subsequent stage 1 work if the
operator selects the section 16.8 fallback.

**Scope.** This includes code-commit verification and tests (in particular
recorder or audit paths), the non-registered rehearsal, the A11 item 3
compatibility proof, the labels launch, all five run launches, qualification
and configuration-test runs, after-run gates, the separately authorized sealed
reading, and every reader or tool that parses recorder output. Set it for
coordinators, service supervisors, host supervisors, spawned workers and RPC
processes as well as interactive Python commands. This requirement does not
authorize any launch, reading or other step that still needs the operator's go.

It does **not** apply retroactively to the running validation: leave that
launch and its processes untouched and finish section 16.1 at their existing
identity. Code inspection confirms that `production_runner.execute` routes
table jobs to `offline_estimator.estimate` and A4 fit, validation and census
jobs to `table_validation_a4.run_stage_job`; its `TableTrace` uses
`offline_estimator.simulate`. Those paths do not convert certificates to
decimal text or invoke `RecordedV3Model` or the period audit. The affected
conversions are `str(certificate.exact)` for period and active admission
evidence in `recording.py`, and `str(reserved)` / `str(unallocated)` in
`cohort.ProtectionPeriod.audit`; `gates.recompute_review` parses the admission
strings with `Fraction`, so readers need the setting too.

**Set it at each process boundary.**

- **X2-1:** the shell launch wrappers in sections 4 and 14 supply the Python
  service/host supervisor's environment; its children inherit that environment.
  Add this exact line in the launch wrapper, before the preflight and before
  starting any Python supervisor, coordinator or worker:

  ```bash
  export PYTHONINTMAXSTRDIGITS=0
  ```

  If the actual launcher is a systemd user unit, the supervisor instead gets
  its environment from that unit, not from the terminal issuing `systemctl`.
  Add this exact line under `[Service]` in that unit or its drop-in:

  ```ini
  Environment=PYTHONINTMAXSTRDIGITS=0
  ```

  Reload the user manager with `systemctl --user daemon-reload` after a unit
  change, and restart the affected launcher at the adoption boundary. An
  export in an unrelated login shell does not configure a systemd service.
- **WS-1 in WSL, BX-1, and X2-2 when it joins:** add
  `export PYTHONINTMAXSTRDIGITS=0` in the host's Linux shell or launch wrapper
  before its qualification command and `"$PYTHON" -B -m v3.host_a11` command.
  On WS-1 this must be inside WSL. Repeat in each fresh shell or detached
  launcher; `nohup`/`setsid` and spawned workers inherit the launch environment.
  SSH does not forward this setting: configure it on the destination as well.
  In particular, `host_a11.SSH` starts a fresh coordinator-side RPC Python;
  set the export in that account's noninteractive SSH shell startup (before
  any interactive-only return), or in the configured restricted-command
  wrapper before its existing fixed RPC command. Keep RPC stdout free of
  preflight text. Do not edit `host_a11.py` to supply the variable.
- **Readers and gates on any host:** use the same export in the shell/wrapper
  that starts the reader, gate or sealed-reading Python. For a native Windows
  PowerShell process use `$env:PYTHONINTMAXSTRDIGITS = '0'` before invoking its
  selected Python. An export on the producing host does not configure a reader
  elsewhere.

Existing Python processes must be restarted to pick up the setting; changing
their parent's environment is insufficient. Apply this to adoption and later
processes, preserving completed jobs and the existing interruption/resumption
procedure; do not restart the running pre-adoption validation for this change.

**Preflight on every host, for every launch, before its go.** With the exact
Python executable and environment that will run the jobs, require a printed
limit of `0` and a zero exit status from this one-line check:

```bash
"$PYTHON" -B -c 'import sys; n = sys.get_int_max_str_digits(); print(sys.executable, n); sys.exit(n != 0)'
```

This verifies `sys.get_int_max_str_digits() == 0`; merely displaying the
environment variable is insufficient. Run it inside the actual launch wrapper
or, for systemd, a preflight-only invocation with the same unit environment,
interpreter and working directory, before starting work. Check the destination
SSH/RPC environment separately, and repeat for qualification, rehearsal, proof,
tests, readers/gates and sealed-reading invocations in their actual environments.
Record host, time, launch/invocation, executable, environment source, printed
value and exit status in the launch notes or existing execution metadata under
the authorized operational root. No code change or new sealed-spec field is
needed; do not proceed to the go with a missing or nonzero check.

**Rationale.** Exact cohort fractions have the form
`Fraction(product(2**32 - s_i), 2**(32*n))`, about 9.633 denominator digits per
living agent before reduction, so Python's default 4,300-digit conversion limit
can be exceeded from 447 living agents onward.
The operator's outcome-blind X2-2 probe of 630 runs across all five stage 1
run-launch configurations found a stage 1 peak of 2,809 digits and zero expected
failures among 53,100 jobs, but population-doubled runs exceeded the limit about
8% of the time (D4 needs the setting); evidence is
`C:\Users\matty\Dev\Lineage v3\digit_probe_2026-10-14\codex_report.md` and,
on X2-2, `~/digit_probe/results/analysis.md`.
Disabling this conversion limit is free insurance for stage 1: it changes no
code identity, simulation result or successful job's canonical result bytes;
a job that would fail only at this conversion can complete instead.

**Unchanged by this setting:** pins, plan hashes, seeds, job sets, cost classes
and the A11 item 3 compatibility path, including its proof and approvals.
The separate A12 adoption identity/plan changes already described above still
apply; this environment requirement adds none. It needs no amendment to the
design note or pre-registration, no source edit and no identity re-pin.

### 16.1. Finish and publish at c19b54f5

Stay in the running X2 checkout. Keep its existing section 1 variables, pin,
specs, root paths and code. Do not pull it. Wait for validation and its workers
to finish, including the final cross-host check and service restoration.

```bash
export OLDCO="$HOME/v3_a10"
export OLD_CODE=c19b54f5bde7180c78a5eba4721c33527c47b84c4d93d2fae757fd3e31452810
cd "$OLDCO/simulation"
test "$("$PYTHON" -B -c 'from v3.artifacts import code_identity; print(code_identity())')" = "$OLD_CODE"
# Use the already defined check_done from section 4, in this checkout.
check_done "$EST_SPEC" "$EST_RUN"
check_done "$VAL_SPEC" "$VAL_RUN"
"$PYTHON" -B -m v3.table_validation_a4 publish \
  "$VAL_SPEC" "$VAL_RUN" "$SOURCE" "$CAL" "$TABLE"
sha256sum "$TABLE" "${TABLE%.json}.compatibility.json" "${TABLE%.json}.cell_results.json"
```

Require section 6's 19,500 primary rows, publication screens, hashes and
complete-root checks. Do not run an outcome report. Execute section 7 exactly
here, creating and committing only
`simulation/v3/runs/a10_stage1/nominal/family_identity.json`, then committing
the same bytes publicly. The record commit changes HEAD, not `OLD_CODE`.
Record both commit IDs and the common record hash. Do not start section 8
here unless the adoption fails and the operator selects the specified fallback.

Export the completed-source handoff, still under the old code:

```bash
export HANDOFF=v3/runs/a12_handoff
mkdir -p "$HANDOFF"
"$PYTHON" -B - <<'PY'
import os, subprocess
from pathlib import Path
from v3.artifacts import atomic_json, source_manifest, code_identity, read, file_hash, digest
r=Path(os.environ['HANDOFF'])
assert code_identity()==os.environ['OLD_CODE']
sources=[dict(spec=str(Path(os.environ[s]).resolve()),root=str(Path(os.environ[t]).resolve()))
         for s,t in [('EST_SPEC','EST_RUN'),('VAL_SPEC','VAL_RUN')]]
assert all(read(Path(s['root'])/'launches.json')[-1].get('complete') is True for s in sources)
atomic_json(r/'sources.json',sources)
atomic_json(r/'producing_source_manifest.json',source_manifest())
from v3.tables_a10 import paired_runs,arm_runs,correct_runs
from v3.sensitivity_a6 import build_weight_corner_jobs,build_horizon_jobs
cal='v3/runs/registered/v3_rerun_calibration.json'
table='v3/runs/a10_stage1/nominal/v3_rerun_tables_A10.json'
arms=arm_runs(cal,table,'UNUSED_STAGE_2_SQRT_TABLE')
groups={'main':paired_runs(cal,table),
        'k1p5':[j for j in arms if j['config']['model']['instrument']['g']=='linear' and j['config']['model']['instrument']['k_star']==1.5],
        'k2p3':[j for j in arms if j['config']['model']['instrument']['g']=='linear' and j['config']['model']['instrument']['k_star']==2.3],
        'weight_corner':correct_runs(build_weight_corner_jobs(cal,table)),
        'horizon':correct_runs(build_horizon_jobs(cal,table))}
atomic_json(r/'run_job_inventory.json',{name:dict(count=len(jobs),jobs_sha256=digest(jobs)) for name,jobs in groups.items()})
atomic_json(r/'handoff.json',dict(code_hash=code_identity(),
    identity_commit=subprocess.check_output(['git','rev-parse','HEAD']).decode().strip(),
    identity_sha256=file_hash(os.environ['IDENTITY']),
    sources_sha256=file_hash(r/'sources.json'),
    source_manifest_sha256=file_hash(r/'producing_source_manifest.json')))
print(read(r/'handoff.json'))
PY
```

These are operational exports, not new scientific records. Preserve the
completed roots, plans, calibration, probe records, source publication and
all receipt siblings byte for byte. No unfinished root may move to new code.

### 16.2. The planned code commit and its identity

The operator approves this exact file list relative to the public repository,
against the c19b54f5 implementation already on main:

```text
simulation/v3/tables_a10.py
simulation/v3/table_labels_a5.py
simulation/v3/multihost_a11.py
simulation/v3/host_a11.py
simulation/v3/qualification_a11.py
simulation/v3/production_runner.py
simulation/v3/service.py
simulation/test_v3_a12_execution.py
simulation/test_v3_a11.py
simulation/test_v3_multihost_a11.py
simulation/test_v3_multihost_rehearsal.py
simulation/v3/table_compatibility_A2.json
simulation/v3/A10_RUN_ON_X2.md
simulation/diagnostics/v3_instrument_implementation_note.md
```

Commit text, with no additional attribution:

```text
Implement A12 part 2 execution fixes and the stage 1 adoption procedure

Give A10 validation and labels local worker candidates 2, 4, 8 and 12.
Prefer the fastest eligible cross-host recheck host for five seconds, then
allow any eligible host. Declare host profiles and model-service handling
independently of hostname, preserving the current X2 default.

Re-pin production_runner.py and service.py under A12 part 2, committed in
669daf23. Preserve R4 profiles, scientific work, seed-selection functions,
cost classes and exact per-root resume identities. Add execution tests and
document the rehearsal and approved compatibility proof before adoption.
```

The reviewed fixes alone have identity
`3d44e320cd7225bb3d2ea2b0ac7ec5b43fef41592bd12477cd135b5cfabc56bd`.
The A2 re-pins below are part of the planned commit, not yet applied by this
documentation task. With their exact bytes, the planned identity is
`7c3ee3365882b5d304662950ea7df2d9e37af461ede1095834c68cdc8b68f217`.
Changing the metadata text or JSON serialization changes that identity too.

In the operator's integration checkout, apply this bounded record edit after
reviewing the seven source files and four tests. This is preparation for the
operator's commit, not a command for a running checkout:

```bash
cd "$MAINCO/simulation"
"$PYTHON" -B - <<'PY'
import hashlib, json
from pathlib import Path
from v3.artifacts import source_manifest, code_identity
assert code_identity()=='3d44e320cd7225bb3d2ea2b0ac7ec5b43fef41592bd12477cd135b5cfabc56bd'
p=Path('v3/table_compatibility_A2.json'); record=json.loads(p.read_bytes())
manifest=source_manifest()
reasons={
 'v3/production_runner.py': "A12 part 2: E1's candidate handling and E3's hostname-free profile check.",
 'v3/service.py': "A12 part 2: E3's per-host model service."}
assert record['approved_boundary_sha256']['v3/production_runner.py']=='c7d3682422ac0d200f7aede0a6e158835d1dc5e38226d783f6f6a541c5d56947'
assert record['approved_boundary_sha256']['v3/service.py']=='e56e52745374a200c1bface50aa8ba2545aaa4da1ca6eed4a1bc5462ef6e7a24'
record['a10']['a12_part2_revision']={
 'amendment':'A12 part 2, execution fixes and adoption mid-stage',
 'date':'2026-10-11',
 'authorization_commit':'669daf23d18c2c0452d9d10c724b8c312eea50d6',
 'previous_approved_sha256':{p:record['approved_boundary_sha256'][p] for p in reasons},
 'reasons':reasons,
 'scope':'Scheduling and per-host service only. No scientific mechanism, seed-selection function, table, label, gate or reading changes. A10 completed artifacts require the approved, passed, committed A11 compatibility proof. Per-root resume identities stay strict. R4 scientific byte-identity proofs and exact legacy checks remain in force. No A1 or A4 family is read as A10.'}
record['approved_boundary_sha256'].update({p:manifest[p] for p in reasons})
data=(json.dumps(record,sort_keys=True,separators=(',',':'))+'\n').encode()
assert hashlib.sha256(data).hexdigest()=='2c21f1bfa40c5cdf96897ab6e67c6d4ce2bb0aafe523675dc24c9820645866a8'
p.write_bytes(data)
assert code_identity()=='7c3ee3365882b5d304662950ea7df2d9e37af461ede1095834c68cdc8b68f217'
PY
```

The new LF-normalized pins are
`7ab76512c67f7e32b677147c3dc79f3d8e8ec43dfdfa483bdf9f49b628753e9b`
for `production_runner.py` and
`623db8ef5e49116ae7ea56646de754a0102c6f242716b1de55bc9ba96d1c254b`
for `service.py`. No A1 pin or other pinned dependency changes. Preserve the
existing A10/R4 proof statements and historical entries. Tests and the two
Markdown files are outside `source_manifest()`; this JSON is inside it.
The operator commits and publishes the approved list, then records the full
`A12_CODE_COMMIT`. No commit or push is performed by this runbook's author.

### 16.3. Fresh repair checkout and registration checks

Only after validation publication and the family record commit, use a fresh
checkout. Never pull `~/v3_a10` or change its code. Set these in the X2 shell:

```bash
export A12_CODE_COMMIT='<FULL_APPROVED_CODE_COMMIT>'
export EXPECTED_CODE=7c3ee3365882b5d304662950ea7df2d9e37af461ede1095834c68cdc8b68f217
export REPAIRCO="$HOME/v3_a12"
test ! -e "$REPAIRCO"
git -c core.autocrlf=false clone --no-checkout \
  https://github.com/MYotko/AI-Succession-Problem.git "$REPAIRCO"
git -C "$REPAIRCO" -c core.autocrlf=false checkout --detach "$A12_CODE_COMMIT"
export PATH="$HOME/miniforge3/envs/phaseb/bin:$HOME/.local/bin:$PATH"
export PYTHON="$HOME/miniforge3/envs/phaseb/bin/python3.13"
export A10CO="$REPAIRCO" CODE_COMMIT="$A12_CODE_COMMIT"
export A10_ROOT=v3/runs/a12_stage1
export CAL=v3/runs/registered/v3_rerun_calibration.json
export PIN="$A10_ROOT/A10_pin.json"
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
cd "$A10CO/simulation"
mkdir -p "$A10_ROOT/checks" "$A10_ROOT/inputs"
"$PYTHON" -B - <<'PY'
import hashlib, os, subprocess
from v3.artifacts import source_manifest, code_identity, digest
def git(*args): return subprocess.check_output(['git',*args])
assert git('rev-parse','HEAD').decode().strip()==os.environ['CODE_COMMIT']
git('merge-base','--is-ancestor','669daf23d18c2c0452d9d10c724b8c312eea50d6','HEAD')
assert not git('diff','HEAD','--','simulation').strip()
manifest=source_manifest()
committed={p:hashlib.sha256(git('show','HEAD:simulation/'+p).replace(b'\r\n',b'\n')).hexdigest() for p in manifest}
assert committed==manifest and digest(committed)==code_identity()==os.environ['EXPECTED_CODE']
print({'code_identity':code_identity(),'committed_source':'verified'})
PY
```

Repeat section 1's Python, numpy, calibration and constants checks here.
For labels and the five new run launches, use the operator-approved
clarification commit and its exact committed note SHA256 below. Do not infer
a pin from HEAD or substitute the re-pin authorization commit `669daf23`.

```bash
export ADOPTION_DESIGN_COMMIT='cc74ddd7c23fb02e95753f9e42cf49622d906200'
export ADOPTION_DESIGN_SHA256='dc1055002323d9afd20125533fe61c2ef7f2970042c43d9cc60b975620c40404'
"$PYTHON" -B - <<'PY'
import os, hashlib, subprocess
from pathlib import Path
from v3.artifacts import verify_registration, atomic_json, read
from v3.tables_a10 import family_instrument
pin=dict(commit=os.environ['ADOPTION_DESIGN_COMMIT'],
 path='simulation/diagnostics/v3_rerun_design_note.md',sha256=os.environ['ADOPTION_DESIGN_SHA256'])
assert hashlib.sha256(subprocess.check_output(['git','show',pin['commit']+':'+pin['path']])).hexdigest()==pin['sha256']
verify_registration(pin,instrument=family_instrument('nominal'))
target=Path(os.environ['PIN']); assert not target.exists() or read(target)==pin
atomic_json(target,pin)
PY
```

A pin mismatch is a stop, including a later edit to that same design-note
file. In particular, a pin to the reading registration `93474e00` does not
match the note after part 2 was appended. The later reading retains its
separate registration at `93474e00dea0c8d88bfed64e096b2f4e21656a7f`.

WSL and the box use fresh `~/v3_a12` checkouts at the same full code commit,
with the same committed-byte checks, phaseb environment and relative paths.
Do not touch their active c19b54f5 checkouts. Stage the section 2 exclusion
bundle and P2 cost record by the existing hashes, and set `COST` and `PROBE`
to those copies. The family identity record must already be tracked on main
at the original section 7 path with exactly the old record bytes. Stop if it
is absent; do not synthesize it from an output at the new identity.

### 16.4. Non-registered rehearsal on the workstation and box

Use new roots under `v3/runs/a12_rehearsal`, never a registered root. Budget
at most three wall hours for this rehearsal session, including qualification;
stop and preserve it if it cannot finish. Charge actual machine intervals to
the operations ledger. This is a toy exercise, not a new cost projection.

While the X2 is occupied, the workstation and box may run the deterministic
local checks below only after their own active workers have been drained and
their capacity is released by the operator. Otherwise wait. The real transport
rehearsal below runs after validation, because qualification still requires
the original X2 as its measured reference. Do not spoof that hostname or use
old-identity qualification evidence to avoid that requirement.

In each new workstation/box checkout, with its frozen Python and one numerical
thread, run these selected existing tests. Their loopback fixtures deliberately
control the clock and host speeds; they are not real-machine throughput claims.

```bash
cd "$HOME/v3_a12/simulation"
mkdir -p v3/runs/a12_rehearsal/checks
"$PYTHON" -B -m pytest -q test_v3_a12_execution.py \
  --junitxml=v3/runs/a12_rehearsal/checks/execution.xml
"$PYTHON" -B -m pytest -q test_v3_a11.py -k pipeline \
  --junitxml=v3/runs/a12_rehearsal/checks/pipeline.xml
```

Require 20 A12 cases passed and a selected, passed pipeline test, not zero
collected tests. E2 cases are
`test_fastest_eligible_non_original_host_gets_unchanged_check` (both original
host cases) and `test_recheck_preference_expires_without_reset_and_fallback_finishes`.
They check the fastest non-original host, exclusion of the original fastest
host, the five-second journaled window, and fallback without changing the
sample or comparison. Memory, readiness, drain and mismatch refusals also run.

After X2 is free, run section 12a's small full pipeline with these substitutions:

```bash
export REH=v3/runs/a12_rehearsal/pipeline
export EXPECTED_CODE=7c3ee3365882b5d304662950ea7df2d9e37af461ede1095834c68cdc8b68f217
export CODE_COMMIT="$A12_CODE_COMMIT" A10CO="$HOME/v3_a12"
export BOARD_NAME=a12_rehearsal_pipeline.json
```

Use section 12a's declared contexts `(.064,1.)` and `(.064,1.5)`, population
64, capacity 640, three groups, two runs/particles, burn 30 and measure 120.
Keep its two-hour estimation/validation ceilings and 1.25-hour label ceiling.
Do not run its 24,000-step fault drills again for this change. Qualify and
approve X2, WSL and the box per phase. For this pipeline, both non-X2 hosts
use `--profile local --model-service none --mode work`; permit 12 workers on
WSL and up to 12 within the box's measured CPU budget. X2 uses eight workers
and its default `llm` service. Each host still chooses its configuration.

After preparing each of the validation and label plans, check every profile:

```bash
export PLAN="$REH/validation.json"  # Repeat with $REH/labels_plan.json when built.
"$PYTHON" -B - <<'PY'
import os
from v3.artifacts import read,unseal
p=unseal(read(os.environ['PLAN']))
assert p['registered'] is False and p['configuration']
for phase,profile in p['configuration'].items():
    assert profile['workers_local']==[2,4,8,12]
    assert profile['workers_x2']==[8,12,16,24,32]
    print({'phase':phase,'local_candidates':profile['workers_local'],'x2_candidates':profile['workers_x2']})
PY
```

Check session configuration measurements test all feasible candidates within
each host's declared cap and measured memory. A chosen count below 12 is not
a failure. Confirm the real cross-host checks match and the final A4/A5
publication and A10 receipt pass. Never display fitted values or outcomes.

For E3, create a separate short estimation drill with the same two declared
contexts and settings under `REH=v3/runs/a12_rehearsal/x2_none`; use the first
builder block in section 12a and its preparation/qualification sequence.
The original X2 remains coordinator and reference, with an ordinary local
worker. The box is the candidate, under its actual hostname. Require Linux
and a CPU budget whose work cap permits eight workers. If the box lacks that
capacity, use WSL for this profile case; do not fake resources or names.
This profile test does not claim that the box has X2 hardware or throughput.

On the candidate, use a fresh qualification output for this distinct root:

```bash
export REH=v3/runs/a12_rehearsal/x2_none
export QUAL="$REH/qualification/estimate"
export CANDIDATE_CPUS='<APPROVED_AVAILABLE_CPU_BUDGET_AT_LEAST_12>'
test "$(hostname)" != yotko-evo-x2
# Pull this root's new plan.json and plan_files from X2 as in section 4a.
"$PYTHON" -B -m v3.qualification_a11 run "$QUAL/plan.json" "$QUAL/box_x2_none.json" \
  --profile x2 --model-service none --workers 8 --cpu-budget "$CANDIDATE_CPUS" --mode work
scp "$QUAL/box_x2_none.json" "yotko@100.96.61.55:v3_a12/simulation/$QUAL/box_x2_none.json"
```

On X2 compare it against this plan's new X2 reference, obtain the operator's
approval, and append that evidence to this root's register:

```bash
"$PYTHON" -B -m v3.qualification_a11 compare "$QUAL/plan.json" "$QUAL/reference.json" \
  "$QUAL/box_x2_none.json" "$QUAL/box_x2_none_evidence.json"
"$PYTHON" -B -m v3.multihost_a11 approve "$REH/source/tables_A1" \
  "$QUAL/box_x2_none_evidence.json" --operator '<OPERATOR>' --when '<APPROVAL_UTC>'
```

Start the non-registered coordinator with section 12a's helper, attaching the
watchdog to `"$HOME/status-board/a12_rehearsal_x2_none.json"`. On the candidate:

```bash
export RUN_ROOT="$REH/source/tables_A1"
"$PYTHON" -B -m v3.host_a11 --coordinator yotko@100.96.61.55 \
  --checkout /home/yotko/v3_a12 --root "$RUN_ROOT" \
  --scratch "$REH/host_box_x2_none" --profile x2 --model-service none \
  --workers 8 --cpu-budget "$CANDIDATE_CPUS" --mode work
"$PYTHON" -B - <<'PY'
import os
from pathlib import Path
from v3.artifacts import read
s=read(Path(os.environ['REH'])/'host_box_x2_none/service.json')
assert s['model_service']=='none' and s['actions_skipped'] is True
assert s['down_exit_code'] is None and s['up_exit_code'] is None
print({'service':'none','actions_skipped':True})
PY
```

On X2, inspect only operational state via
`v3.dispatch_store_a11.read_state(Path(RUN_ROOT))`: the candidate's session
must record profile `x2`, service `none`, configuration at eight workers,
at least one completed job and an ended charging interval. Do not accept a
candidate that joined too late to perform work. Reconcile the separate
service records: the original X2 still restores `llm`, the candidate attempts
no service action. Retain qualification hashes, config records, matching
checks, test XML, publication hashes and receipt. The interpreter reviews
these together. The E2 preference and fallback checks in this rehearsal are
the controlled loopback cases on both real machines; the live pipeline checks
the transport, configurations, cross-host matching and publication. Do not
describe the controlled clock as a measured network fallback latency.

The interpreter writes a plain `review.json` under
`v3/runs/a12_rehearsal`, with `passed`, `code_hash`, `reviewer`, and a `cases`
mapping. Require `qualification`, `E1_validation`, `E1_labels`,
`E2_preferred`, `E2_fallback`, `E3_x2_none`, `publication` and `watchdog`,
each with `passed: true`. Its `evidence_sha256` maps paths relative to that
rehearsal directory to the actual files reviewed, including test XML from
both hosts. Copy remote operational evidence there by hash. Failed cases
stop adoption; do not manufacture an approval from an earlier identity.
After the operator approves that review, use this A12-specific approval block
instead of section 12a's old fault-drill approval block:

```bash
export REHEARSAL_OPERATOR='<APPROVING_OPERATOR>'
export REHEARSAL_APPROVAL_UTC='<APPROVAL_UTC>'
"$PYTHON" -B - <<'PY'
import os
from pathlib import Path
from v3.artifacts import read,seal,atomic_json,code_identity,file_hash
r=Path('v3/runs/a12_rehearsal'); review=read(r/'review.json')
required={'qualification','E1_validation','E1_labels','E2_preferred','E2_fallback',
          'E3_x2_none','publication','watchdog'}
assert review['passed'] and review['code_hash']==code_identity() and review['reviewer']
assert required<=set(review['cases']) and all(review['cases'][k]['passed'] for k in required)
files=review['evidence_sha256']; assert files
for name,expected in files.items():
    path=(r/name).resolve(); assert path.is_relative_to(r.resolve())
    assert file_hash(path)==expected
operator=os.environ['REHEARSAL_OPERATOR']; when=os.environ['REHEARSAL_APPROVAL_UTC']
assert operator and when and '<' not in operator+when
record=dict(schema='v3-A11-rehearsal-approval-1',passed=True,non_registered=True,
    code_hash=code_identity(),reviewer=review['reviewer'],
    operator_approval=dict(operator=operator,when=when),rehearsal_root=str(r.resolve()),
    files={**files,'review.json':file_hash(r/'review.json')},cases=review['cases'])
target=Path(os.environ['A10_ROOT'])/'checks/A11_rehearsal_approved.json'
assert not target.exists() or read(target)==seal(record)
atomic_json(target,seal(record))
print({'passed':True,'approval_sha256':file_hash(target)})
PY
```

### 16.5. Prove compatibility, review, approve and commit the record

Run the proof in `~/v3_a12` on X2 only after the old validation is complete,
the rehearsal passes and the operator grants its service window. This avoids
reinterpreting absolute source paths on another machine. It also makes the
ledger charge unambiguous: elapsed X2 service/proof time at relative rate 1,
including startup, cleanup and review-related operational work. Use section
14's service supervisor and its work-mode maximum of 12 one-thread workers.
Do not launch a registered worker at the same time. Reserve this cost from
actual remaining stage 1 headroom, not a ninth allocation or an enlarged
ceiling. If headroom is insufficient, stop for the operator. Record actual
time even when a proof fails.

```bash
cd "$REPAIRCO/simulation"
mkdir -p v3/runs/a11_proof
cp "$OLDCO/simulation/v3/runs/a12_handoff/sources.json" v3/runs/a11_proof/sources.json
cp "$OLDCO/simulation/v3/runs/a12_handoff/producing_source_manifest.json" \
  v3/runs/a11_proof/producing_source_manifest.json
cmp "$OLDCO/simulation/v3/runs/a12_handoff/sources.json" v3/runs/a11_proof/sources.json
"$PYTHON" -B - <<'PY'
from v3.artifacts import read,atomic_json,source_manifest,digest,code_identity
from v3.compatibility_a10 import changed_files
before=read('v3/runs/a11_proof/producing_source_manifest.json')
assert digest(before)=='c19b54f5bde7180c78a5eba4721c33527c47b84c4d93d2fae757fd3e31452810'
assert code_identity()=='7c3ee3365882b5d304662950ea7df2d9e37af461ede1095834c68cdc8b68f217'
reasons={
 'v3/tables_a10.py':'E1: A10 validation local candidates [2,4,8,12]; unchanged legacy profiles and scientific jobs.',
 'v3/table_labels_a5.py':'E1: A10 label local candidates [2,4,8,12] after the unchanged job construction.',
 'v3/multihost_a11.py':'E2: bounded fastest-eligible recheck preference; E3: approved profile and service, independent of hostname.',
 'v3/host_a11.py':'E2: current memory reporting; E3: explicit per-host model service and hostname-independent X2 profile.',
 'v3/qualification_a11.py':'E3: record candidate profile and service; original X2 reference unchanged.',
 'v3/production_runner.py':"A12 part 2: E1's candidate handling and E3's hostname-free profile check.",
 'v3/service.py':"A12 part 2: E3's per-host model service.",
 'v3/table_compatibility_A2.json':'A12 part 2 authorizes exactly the production_runner.py and service.py re-pins; preserve all other checks.'}
assert set(changed_files(before,source_manifest()))==set(reasons)
atomic_json('v3/runs/a11_proof/reasons.json',dict(producing_source_manifest=before,reasons=reasons))
print({'changed_manifest_files':len(reasons),'source_launches':len(read('v3/runs/a11_proof/sources.json'))})
PY
```

Expected: eight changed manifest files and two completed source launches.
Test files and notes are not manifest files and do not belong in `reasons`.
Now execute the X2 service-supervisor block in section 14 exactly. Its paths
above are deliberate: it runs `compatibility_a10 build --sources
v3/runs/a11_proof/sources.json --reasons v3/runs/a11_proof/reasons.json
--output v3/runs/a11_proof/proof.json --workers 12`. Do not also run the bare
workstation command. The original specs, their jobs and `config.seed` stay
unchanged. The builder reads the old outputs internally and reports hashes.

Require a sealed attempt with the complete population, followed by a passed
proof of the two hash-selected jobs per phase/capability/setting, or all if
fewer. It covers both estimation and every nonempty validation phase. A
failed comparison ends the attempt; it cannot be approved, resampled or
retried to get a passing record. The interpreter reviews the exact source
diff, reasons, selection, per-job proof hashes and restored-service record.
Only then may the operator approve:

```bash
"$PYTHON" -B - <<'PY'
from v3.artifacts import read,unseal
p=unseal(read('v3/runs/a11_proof/proof.json'))
assert p['passed'] and all(x['passed'] for x in p['proofs'])
assert p['operator_approval'] is None
print({'passed':True,'proof_jobs':len(p['proofs']),'strata':len(p['populations']),
       'phases':sorted({x['phase'] for x in p['populations']})})
PY
# Separate operator go for this proof and its reviewed reasons.
"$PYTHON" -B -m v3.compatibility_a10 approve v3/runs/a11_proof/proof.json \
  --operator '<OPERATOR>' --date '<APPROVAL_DATE>'
```

Execute section 14's `record_name` copy, single-file commit and verification
block in this repair checkout. It commits only
`simulation/v3/runs/registered/A11_compatibility_<DIGEST_OF_X_AND_Y>.json`,
where the tool computes the exact basename. Export its path as `COMPAT_PATH`
and its byte SHA256 as `COMPAT_SHA256`. Set Git identity in this checkout only
as in section 7. No fetch or pull. Require `validate_record` to return the
full c19b54f5 identity, `accepted_identities()` to contain it and Y, and Y to
remain unchanged.

Copy that exact file to the operator's main checkout at the same relative
path. As in section 7, compare bytes by SHA256, obtain a separate go, stage
only `COMPAT_PATH`, check the staged path list, and commit with:

```text
Record approved A12 part 2 compatibility of completed A10 estimation and validation
```

```bash
# In the repair checkout, after its single-file commit and verification:
export COMPAT_SHA256=$(sha256sum "$REPAIRCO/$COMPAT_PATH" | cut -d' ' -f1)
printf '%s\n%s\n' "$COMPAT_PATH" "$COMPAT_SHA256"
# In the operator's public main checkout, set both values to that output.
export MAINCO='<OPERATOR_MAIN_CHECKOUT>'
export COMPAT_PATH='<EXACT_RELATIVE_PATH_REPORTED_ABOVE>'
export COMPAT_SHA256='<EXACT_BYTE_SHA256_REPORTED_ABOVE>'
mkdir -p "$MAINCO/$(dirname "$COMPAT_PATH")"
scp "yotko@100.96.61.55:v3_a12/$COMPAT_PATH" "$MAINCO/$COMPAT_PATH"
test "$(sha256sum "$MAINCO/$COMPAT_PATH" | cut -d' ' -f1)" = "$COMPAT_SHA256"
# Separate operator go for these bytes and this single-file public commit.
git -C "$MAINCO" add -f -- "$COMPAT_PATH"
test "$(git -C "$MAINCO" diff --cached --name-only)" = "$COMPAT_PATH"
git -C "$MAINCO" commit -m 'Record approved A12 part 2 compatibility of completed A10 estimation and validation'
test "$(git -C "$MAINCO" show "HEAD:$COMPAT_PATH" | sha256sum | cut -d' ' -f1)" = "$COMPAT_SHA256"
git -C "$MAINCO" rev-parse HEAD
```

The repair and public commits may differ, but their record bytes must match.
Record the full public commit as `A12_RECORD_COMMIT`. Neither record-only
commit changes Y. Preserve both proof files and the review; never commit the
old scientific outputs. Create the execution checkout from the public commit:

```bash
export A12_RECORD_COMMIT='<FULL_PUBLIC_COMPATIBILITY_RECORD_COMMIT>'
export EXECUTIONCO="$HOME/v3_a12_execution"
test ! -e "$EXECUTIONCO"
git -c core.autocrlf=false clone --no-checkout \
  https://github.com/MYotko/AI-Succession-Problem.git "$EXECUTIONCO"
git -C "$EXECUTIONCO" -c core.autocrlf=false checkout --detach "$A12_RECORD_COMMIT"
export A10CO="$EXECUTIONCO" CODE_COMMIT="$A12_RECORD_COMMIT"
cd "$A10CO/simulation"
# Repeat 16.3's committed-source check and the resolved registration check here.
"$PYTHON" -B - <<'PY'
import os, subprocess
from pathlib import Path
from v3.artifacts import code_identity,file_hash
from v3.compatibility_a10 import validate_record,accepted_identities
path=Path(os.environ['COMPAT_PATH'].removeprefix('simulation/'))
assert subprocess.check_output(['git','show','HEAD:simulation/'+path.as_posix()])==path.read_bytes()
assert file_hash(path)==os.environ['COMPAT_SHA256']
assert validate_record(path)==os.environ['OLD_CODE']
assert {os.environ['OLD_CODE'],os.environ['EXPECTED_CODE']} <= accepted_identities()
assert code_identity()==os.environ['EXPECTED_CODE']
print({'compatibility':'verified','code_identity':code_identity()})
PY
```

WSL and the box now also use fresh `~/v3_a12_execution` checkouts at
`A12_RECORD_COMMIT`. The frozen pull-dispatch `code_commit` must be this
commit on every host, even though its code identity equals the rehearsal
commit's. Verify the compatibility record and committed source there too.
Do not point their workers at the repair or old stage 1 checkout.

### 16.6. Stage immutable inputs, then labels and the receipt at Y

Copy the completed nominal source tree and validation tree into the execution
checkout at their same paths relative to `simulation/`. Copy the original
validation spec, published family and its two siblings, exclusion records
and P2 cost record too. Use a hash inventory, not outcome inspection. The
family identity is already committed at the old section 7 path. It must match
the copied family and its siblings. Do not change any embedded job path, seal,
seed, receipt or producer field in these copies. Keep the originals untouched.
The proof can use old absolute paths read-only; new label preparation uses
these in-scope copies so the input snapshot can package them for workers.

Only copy stopped roots after `check_done`; do not copy a live SQLite WAL.
Before copying, measure the full source file sizes in the old checkout and
require that much free space on the destination filesystem, plus the larger
of 20 percent or 1 GiB. Count the whole copy even if some destination files
already exist. The check below prints byte counts and stops before any copy
if space is insufficient.

```bash
cd "$A10CO/simulation"
export OLD_TREE=v3/runs/a10_stage1
"$PYTHON" -B - <<'PY'
import hashlib,os,shutil
from pathlib import Path
from v3.artifacts import atomic_json
old=Path(os.environ['OLDCO'])/'simulation'; new=Path.cwd()
base=Path(os.environ['OLD_TREE'])
names=[base/'nominal/source',base/'nominal/validation_run',base/'nominal/validation_plan.json',
       base/'nominal/v3_rerun_tables_A10.json',base/'nominal/v3_rerun_tables_A10.compatibility.json',
       base/'nominal/v3_rerun_tables_A10.cell_results.json',base/'inputs']
copy_bytes=0
for name in names:
    source=old/name
    assert source.exists(),name
    files=(p for p in source.rglob('*') if p.is_file()) if source.is_dir() else [source]
    copy_bytes+=sum(p.stat().st_size for p in files)
margin_bytes=max(1024**3,(copy_bytes+4)//5)
required_bytes=copy_bytes+margin_bytes
free_bytes=shutil.disk_usage(new).free
print({'copy_bytes':copy_bytes,'margin_bytes':margin_bytes,
       'required_bytes':required_bytes,'free_bytes':free_bytes})
if free_bytes<required_bytes:
    raise SystemExit('STOP: insufficient free disk space for the copied trees plus margin')
inventory={}
for name in names:
    source=old/name
    assert source.exists(),name
    files=sorted(p for p in source.rglob('*') if p.is_file()) if source.is_dir() else [source]
    for p in files:
        rel=p.relative_to(old); target=new/rel; data=p.read_bytes()
        expected=hashlib.sha256(data).hexdigest()
        if not target.exists():
            target.parent.mkdir(parents=True,exist_ok=True); shutil.copyfile(p,target)
        assert hashlib.sha256(target.read_bytes()).hexdigest()==expected
        target.chmod(0o444); inventory[rel.as_posix()]=expected
atomic_json(Path(os.environ['A10_ROOT'])/'checks/carried_inputs.json',inventory)
print({'copied_files':len(inventory),'hashes':'verified'})
PY
export SOURCE="$OLD_TREE/nominal/source"
export VAL_SPEC="$OLD_TREE/nominal/validation_plan.json"
export VAL_RUN="$OLD_TREE/nominal/validation_run"
export IDENTITY="$OLD_TREE/nominal/family_identity.json"
export TABLE="$OLD_TREE/nominal/v3_rerun_tables_A10.json"
export PROBE="$OLD_TREE/inputs/a3_probe"
export COST="$OLD_TREE/inputs/a10_pilot_P2_projection_2026-10-08.json"
export LABEL_SPEC="$A10_ROOT/nominal/labels_plan.json"
export LABEL_RUN="$A10_ROOT/nominal/labels_run"
export LABELS="$A10_ROOT/nominal/v3_rerun_labels_A10.json"
test ! -e "$LABEL_SPEC" && test ! -e "$LABEL_RUN"
```

Do not call Y's strict `check_done` on an X root, or launch a copied X root.
Copy the resolved pin and the approved new-identity rehearsal record into
`$A10_ROOT`, verifying their hashes. Keep one manual program ledger across
both checkouts. The compatibility proof and rehearsal consume its existing
headroom; they do not reset the 980-hour counter.

Run section 8's Python prepare block with these variables and the unchanged
257.66-hour ceiling. Before
`check_spec`, require every nonempty label configuration profile to have
local `[2,4,8,12]` and X2 `[8,12,16,24,32]`, as in 16.4. This is a new plan
and new root. Do not patch or resume an old label plan. `load_a4_publication`
accepts the c19b54f5 family and receipt through the committed compatibility
record; their exact hashes still bind to the original committed family
identity. No A1 or R4 family is admitted as A10.

Run `check_spec "$LABEL_SPEC" "$LABEL_RUN"`, then section 4a anew for this
root and current commit: X2 reference, each host's candidate evidence,
interpreter verification, operator register approvals. WSL and the box use
their approved profile, service and caps; existing-X2 behavior stays the
default. Obtain the registered launch go only after reviewing the frozen
manifest, source pin, qualification, projected cost and ledger reservation.
The per-host configuration tests run on join; no worker count is assumed.

```bash
export LABEL_N=$("$PYTHON" -B -c 'import sys; from v3.artifacts import read,unseal; print(len(unseal(read(sys.argv[1]))["jobs"]))' "$LABEL_SPEC")
# Separate operator go, after fresh qualification and register approvals.
launch_x2 "$LABEL_SPEC" "$LABEL_RUN" "$LABEL_N" a12_stage1_labels.json
# Wait for launch and workers to finish, then:
check_done "$LABEL_SPEC" "$LABEL_RUN"
"$PYTHON" -B -m v3.table_labels_a5 publish \
  "$LABEL_SPEC" "$LABEL_RUN" "$VAL_RUN" "$SOURCE" "$CAL" "$LABELS"
sha256sum "$LABELS"
```

Remote workers use section 12's SSH command with coordinator checkout
`/home/yotko/v3_a12_execution`, this new root and separate scratch. X2 uses
the section 4 local transport. The board is
`"$HOME/status-board/a12_stage1_labels.json"`. On restart use the same root,
manifest, identity and deadline, a new watchdog PID, and restarted workers.

Run section 9's receipt and three-instrument checks in this checkout. The
new `.a10_receipt.json` is created next to the copied table here; the old
checkout is never written. It binds the accepted c19b54f5 table/A4 receipt
and Y's labels. Require 19,500 rows, all three k-star instruments, all label
and support screens, and the published file hashes. A mixed unapproved
producer, failed label screen or modified source hash is a stop.

### 16.7. Five new run launches and unchanged reading authority

Run section 10's builder and before-gate checks in the execution checkout,
with `$A10_ROOT=v3/runs/a12_stage1`, the copied nominal table and new receipt,
and the resolved design pin. Require these unchanged counts and allowances:

| Component | Jobs | Wall hours and X2-equivalent allowance |
| --- | ---: | ---: |
| main | 24,900 | 50.49 |
| k1p5 | 4,400 | 10.94 |
| k2p3 | 4,400 | 10.93 |
| weight_corner | 17,600 | 44.34 |
| horizon | 1,800 | 10.27 |

The builder writes all five new sealed specs. Check the 53,100 disjoint jobs,
pairing, seed checks, full 500/1,000-step lengths and frozen P2 cost classes
as in section 10. There are no stage 2 jobs. Each launch receives new
qualification, register approvals, configuration measurements and its own
operator go. Execute section 11 one line at a time with these variables and
board basenames `a12_stage1_main.json`, `a12_stage1_k1p5.json`,
`a12_stage1_k2p3.json`, `a12_stage1_weight_corner.json` and
`a12_stage1_horizon.json`. The helper places each under `"$HOME/status-board"`.
Reconcile the program ledger before every go and after every completion.

Keep `CAL=v3/runs/registered/v3_rerun_calibration.json` and
`TABLE=v3/runs/a10_stage1/nominal/v3_rerun_tables_A10.json` exactly as above
when calling the builder. These are the original relative input paths inside
the fresh checkout; only the spec/output roots use `a12_stage1`. Table and
calibration path strings enter arm job/seed construction, so substituting an
absolute path or a new relative table filename would change the experiment.
Compare the new job lists with a read-only invocation of the old builders at
the same two input strings; identity and registration are envelope metadata
for these run specs. Do not run a simulation for this comparison.

```bash
"$PYTHON" -B - <<'PY'
import os
from pathlib import Path
from v3.artifacts import read,unseal,digest
before=read(Path(os.environ['OLDCO'])/'simulation/v3/runs/a12_handoff/run_job_inventory.json')
for name,expected in before.items():
    spec=unseal(read(Path(os.environ['A10_ROOT'])/'specs'/(name+'.json')))
    assert dict(count=len(spec['jobs']),jobs_sha256=digest(spec['jobs']))==expected
print({'identical_run_job_sets':sorted(before),'jobs':53100})
PY
```

The new-launch design pin at `cc74ddd7`, checked in 16.3,
stays fixed across labels and all five specs. The old roots retain their
old pin and identity. The later sealed stage 1 reading stays registered at
`93474e00dea0c8d88bfed64e096b2f4e21656a7f`; this execution amendment does not
move that reading registration, change its rules or authorize its opening.
Retain both identities, compatibility proof and approval, all five roots,
the nominal family and receipts, and the original reading inputs for that
separate collection. Inspect only counts, hashes, execution status and
required pass/fail screens here.

### 16.8. Stops, fallback and closeout

- A failed compatibility proof ends this attempt. Preserve the failed proof,
  selection and service/ledger records. Labels and the five run launches
  proceed at c19b54f5 under sections 8 to 11, after the operator's individual
  launch approvals. Return to the untouched `~/v3_a10`, its original variables,
  design pin and family record commit. Do not copy a Y plan back into it.
- A failed rehearsal case stops adoption before the proof or new registered
  launch. Present its exact evidence to the interpreter and operator. Do not
  waive the case, treat tests as qualification, or switch branches silently.
- A design-pin, committed-source, compatibility-record, family-record, input
  hash or frozen-commit mismatch is a refusal. Preserve it and ask the operator;
  do not repair an active checkout, re-seal old records or edit the manifest.
- An interrupted unfinished launch resumes only in its own code identity,
  root and original deadline. Compatibility carries completed roots only.
- A projection or ledger overrun stops new work. Part 2 changes no allocation
  or ceiling. Restore model services, close charging intervals, preserve the
  journal and attach a new watchdog only when a resumed coordinator exists.

Record the operator's answers, code/record commits, document hashes, rehearsal
approval, proof result and ledger costs in the execution log. The code re-pins
remain an operator-reviewed commit step; this section itself changes no
source-manifest file or scientific mechanism.

## 17. A13 adoption after the nominal publication refusal, 2026-10-16

This section supersedes section 16 wherever they conflict. Section 16 is
carried forward verbatim as an operational reference, including its 16.0
integer-text setting. Its old pins, planned identity, successful publication
at c19b54f5, and fallback are obsolete. Do not execute 16.1, 16.2 or 16.8 as
an adoption path. The original refusal stands. There is no admissible nominal
family at c19b54f5, and a failed proof or failed admission halts downstream
work. No label or run launch precedes A13 publication.

These are written instructions only. The build did not run this rehearsal,
access another machine, execute registered work, or commit anything. Each
operator go below applies to its exact reviewed artifact, not to this entire
section. Use section 16.0's `PYTHONINTMAXSTRDIGITS=0` on every Python boundary,
one numerical thread, the existing status board/watchdog, and a fresh root
for every new launch. Actual overhead is charged to the unchanged 980
X2-hour stage 1 ledger. A scientific extension halt spends its single round;
an infrastructure interruption resumes the same plan and root.

### 17.0. Worker control, 2026-10-18

The operator rejected approval of the completed proof at identity `5ae3d3cd`.
Keep that proof and all of its files untouched. This code requires a new
rehearsal, qualification and proof at its new identity, in new execution roots
and under the new identity-pair reservation. Do not approve or reuse the old
proof as evidence for this change.

Before **every go**, run and review a load sheet on each participating host.
Use the exact planned worker count, CPU budget, reason and headroom in both
the sheet and the subsequent launch. The sheet reads plans, attempts and
completion timing metadata only. It reports anonymous class reservations,
CPU/memory utilization, and total wall estimates at registered and measured
rates. A missing measured rate is shown as unavailable, not inferred from an
outcome. Configuration may reduce an ordinary target; an explicit reasoned
target bypasses that measured choice. With the current default policy, every
scientific dispatch still applies the mode cap to the saved target, as well
as the CPU and memory budgets.
The reduced pilot retains its default 16-worker ceiling; an explicit override
or live target may raise it within those budgets.
For a production plan, `--root ROOT` adds measured timing rates and class peaks
from executor completion records only. A pull load sheet with `--hosts HOSTS`
forecasts a partition in which each job is counted once; the live pull scheduler
still assigns work dynamically. Re-run the sheet after a material target change.

A job reserves its own registered memory-class estimate, raised only by that
class's measured peak times 1.2. There is no global worst-job floor. Older
single-host A10/A4/A5 plans retain the sealed phase estimate until their class
has a measured peak. Then the reservation is the larger of that class's own
planning formula and its peak times 1.2. The sealed plan is never rewritten.
Historical completions supply RSS from their executor record or legacy
completion-envelope metadata; scientific result fields never size memory. If
neither contains RSS, use the registered estimate. New completions also copy
RSS into the executor record. Per-class peaks remain
executor-side. A11 item 4's memory caps still apply under every override.
Default memory headroom is 0.8; an explicit reason permits a value up to 0.95.

These are operator commands, written only. Substitute the approved values.
For an ordinary launch or qualification plan, on the host that will execute:

```bash
"$PYTHON" -B -m v3.production_runner load-sheet "$PLAN" --profile x2 \
  --workers 24 --threads 1 --cpu-budget 32 --mode work \
  --override-reason 'Matty: intentional worker target after reviewing the load sheet' \
  --operator Matty --memory-headroom 0.8
```

For a fresh launch, use those same override flags on `production_runner launch`, `host_a11`, or
`qualification_a11 run`. Their existing `--workers` becomes an explicit target
when `--override-reason` is supplied. Without a reason, a request above the
mode cap is refused. The operator name, timestamp, reason and headroom are
recorded with the launch. Configuration tests also use per-class admission.
Repeating identical workers, headroom, reason and operator on resume or rejoin
preserves the live target. Timestamps do not make an override new. Changing
any of those four fields replaces the target and records the change.
For a resume, inspect status and the persisted control first. An explicit
load-sheet worker count is a forecast of that count: use the current live
target for the resume forecast, then repeat the original launch flags to
preserve it. Use a live control when intentionally replacing that target.

For pull launches, the coordinator's `--workers 24` is not an aggregate cap.
With `--workers 24` on each X2 the default overall target is 48. Set an explicit
overall ceiling with launch `--overall-workers 40`, or with `control ROOT
--workers 40` without `--host`. Repeating the same initial overall override on
resume preserves a later live aggregate change.

Above-mode targets are refused if any job class lacks both a sealed estimate
and a measured peak. The five stage-1 run manifests have no sealed memory
estimates: begin within the mode cap to measure their classes, then review
the load sheet with `--root ROOT` before a reasoned raise. A nominal fallback
of 0.25 GB never authorizes an above-mode target. Extension and A5 profiles
derive their reservations from their sealed phase estimates or declared jobs,
including historical profiles whose configuration omits `phase`.
Ordinary declared configuration trials retain their configuration cap and
per-class memory admission; they are not operator overrides of the scientific
mode target. An actual above-mode operator override still requires sealed or
measured memory authority, including during configuration. A live mode control
does not rewrite the saved target or replace the measured configuration choice.

Live controls survive resume and record operator, time, target and reason:

```bash
# Single host:
"$PYTHON" -B -m v3.production_runner control "$RUN_ROOT" --workers 24 --reason 'Matty: raise target'
# Explicit aggregate ceiling for two pull hosts (default is their summed targets):
"$PYTHON" -B -m v3.production_runner control "$RUN_ROOT" --workers 48 --reason 'Matty: two hosts at twenty-four'
# A particular pull host, independent of the aggregate target:
"$PYTHON" -B -m v3.production_runner control "$RUN_ROOT" --host yotko-evo-x2-2 --workers 20 --reason 'Matty: add workers'
"$PYTHON" -B -m v3.production_runner control "$RUN_ROOT" --host yotko-evo-x2-2 --workers 6 --reason 'Matty: lower target'
```

A lower target never kills running jobs. Zero pauses new dispatch. Raising it
admits more jobs as CPU and per-class memory permit. `--mode normal|work`
keeps the saved target and applies min(target, mode cap) when selecting slots.
Work drains to the lower effective count without killing; normal restores the
higher allowance. Unless an explicit target was set, the configuration test's
measured choice still applies under either cap. The single policy setting is
`MODE_CAPS_TARGET = True`; the operator's precedence decision is pending, so
keep this default. Setting it false would let an explicit override beat mode,
while ordinary targets remain capped. Above-mode targets require `--reason`
and memory authority even while capped. Control commands refuse missing
authority before recording the change. A stale unsupported control is capped
in the running loop instead of crashing or spending a proof. The CPU budget
and per-class memory admission always bind.
For pull mode changes use `--host H`. `--immediate` uses the existing
interrupt/resume mechanism and reports the in-flight job IDs that restart.
Use `--stop clear` before resuming an interrupted ordinary launch.

For a frozen proof attempt, run the load sheet before each shard's go:

```bash
"$PYTHON" -B -m v3.compatibility_shards_a11 load-sheet "$PROOF/proof.attempt.json" \
  --host yotko-evo-x2 --workers 24 --override-reason 'Matty: intentional proof target' --operator Matty --memory-headroom 0.8
# Add these flags to the supervised shard run in 17.3:
# --workers 24 --override-reason 'Matty: intentional proof target' --operator Matty --memory-headroom 0.8
"$PYTHON" -B -m v3.compatibility_shards_a11 control "$PROOF/proof.attempt.json" \
  --host yotko-evo-x2 --workers 28 --reason 'Matty: raise proof target'
"$PYTHON" -B -m v3.compatibility_shards_a11 control "$PROOF/proof.attempt.json" \
  --host yotko-evo-x2 --workers 6 --reason 'Matty: lower proof target'
```

Issue each proof control in that host's existing checkout and shard root.
Targets are scheduling metadata only. They do not change the frozen assignment,
selection, job settings, seeds, comparison or attempt hash. Proof interruption
after the start marker still spends the attempt; there is no immediate-stop
retry for a proof. Target zero pauses dispatch without spending the attempt.
The legacy single-host proof also accepts the override flags; control it with
`compatibility_a10 control RECORD --workers N --reason TEXT`.
Proof status is informational, refreshed about once a second with two bounded
write attempts. Its I/O errors cannot fail the proof. Configuration completion
updates the target under the control lock, preserving concurrent live changes.

### 17.1. Code review and the operator's code commit

The code commit contains E1 to E3 plus A13's phase, admission, recording,
historical verification, tests, A2 re-pins and these documents. The executor
does not commit it. The interpreter reviews `_a13_build/REVIEW.diff` against
`fcfcb898` for this worker-control revision, including the unchanged fit, validate, census and estimation
functions and the inert no-admitted-row path. The operator separately
approves the concrete code commit on main.

The review fixes are part of that same code commit. Run the 434-job proof
only after those fixes and their A2 re-pins are committed. A later code
change changes the identity and requires the proof at that changed commit.

The expected LF-normalized identity is
`2a88b5c60504017cf2a8bccdf0679a2c97158a4e81ea47a5d4d58b5dd5bbc07f`.
The old identity is
`c19b54f5bde7180c78a5eba4721c33527c47b84c4d93d2fae757fd3e31452810`.
The independently reproduced E1 to E3 port identity was
`3d44e320cd7225bb3d2ea2b0ac7ec5b43fef41592bd12477cd135b5cfabc56bd`.
The A13 pin is `48815a655c9f4096ea8ceef35ee277ee0352c7d3`.
Do not substitute the code or proof commit for that design pin.

After the operator's code commit, create fresh rehearsal checkouts at that
commit. Set `A13_CODE_COMMIT` to its full ID and `REPAIRCO` to the new
checkout, and run from its `simulation` directory:

```bash
export PYTHONINTMAXSTRDIGITS=0 PYTHONDONTWRITEBYTECODE=1
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
export EXPECTED_CODE=2a88b5c60504017cf2a8bccdf0679a2c97158a4e81ea47a5d4d58b5dd5bbc07f
export OLD_CODE=c19b54f5bde7180c78a5eba4721c33527c47b84c4d93d2fae757fd3e31452810
export REH=v3/runs/a13_rehearsal
mkdir -p "$REH/checks"
"$PYTHON" -B - <<'PY'
import os, subprocess, hashlib
from pathlib import Path
from v3.artifacts import code_identity, source_manifest, atomic_json, verify_registration
assert subprocess.check_output(['git','rev-parse','HEAD']).decode().strip()==os.environ['A13_CODE_COMMIT']
assert code_identity()==os.environ['EXPECTED_CODE']
for name, h in source_manifest().items():
    raw=subprocess.check_output(['git','show','HEAD:simulation/'+name])
    assert hashlib.sha256(raw.replace(b'\r\n',b'\n')).hexdigest()==h
commit='48815a655c9f4096ea8ceef35ee277ee0352c7d3'
path='simulation/diagnostics/v3_rerun_design_note.md'
raw=subprocess.check_output(['git','show',commit+':'+path])
assert Path('../'+path).read_bytes()==raw
pin=dict(commit=commit,path=path,sha256=hashlib.sha256(raw).hexdigest())
verify_registration(pin,instrument={'mapping':'A10','k_star':1.8,'g':'linear'})
atomic_json(Path(os.environ['REH'])/'pin.json',pin)
print({'code_identity':code_identity(),'pin':commit})
PY
```

### 17.2. Order step 3: non-registered rehearsal, written only

Limit the complete session to three wall hours, charge every host interval,
and preserve an incomplete or failed attempt. The machine-specific windows
and capacity need the operator's go. All rehearsal simulation seeds must be
outside `[2**60, 2**61)`. Never exercise the registered extension seeds in a
configuration test or rehearsal.

First run E1 to E3's controlled checks, the toy extension publication/A5
receipt check, and the additive loader/controller cases on each available
rehearsal host. These tests use synthetic records and toy trajectories.

If pytest is absent from the frozen phaseb environment, provide reviewed
pure-Python pytest and its dependencies in a separate directory, such as
`$REH/tools/pytest_site`, and verify the copied bundle's hashes. Keep phaseb
unchanged and keep using its `$PYTHON`. Set `TEST_PYTHONPATH` to that directory
plus any existing `PYTHONPATH`; if pytest is already available, use the
existing `PYTHONPATH` (or an empty string). Apply it only to the three tests
and the toy builder below, which imports `test_v3_a13`, as in the rehearsal.

```bash
PYTHONPATH="$TEST_PYTHONPATH" "$PYTHON" -B -m pytest -q test_v3_a12_execution.py \
  --junitxml="$REH/checks/execution.xml"
PYTHONPATH="$TEST_PYTHONPATH" "$PYTHON" -B -m pytest -q test_v3_a13.py \
  --junitxml="$REH/checks/extension.xml"
PYTHONPATH="$TEST_PYTHONPATH" "$PYTHON" -B -m pytest -q test_v3_a11.py -k pipeline \
  --junitxml="$REH/checks/pipeline.xml"
```

Require actual selected tests and zero unexpected failures. In particular,
`test_toy_end_to_end_publication_a5_receipt_and_resume` prepares A5 against
the amended receipt and checks preservation of the original `plan_hash`
and `stream_seeds`. The zero-admission loader test checks identical rows
with and without an empty A13 binding. The actual branch tests check
selection equality and incidence, including unscored unique minimum risk.

Build a separate tiny extension dispatch plan. Its old-stage records are
synthetic; the extension itself uses the real trace engine. The stored
trajectory values are executor-only and are not inspected or reported.

```bash
PYTHONPATH="$TEST_PYTHONPATH" "$PYTHON" -B - <<'PY'
import os
from pathlib import Path
from test_v3_a13 import toy_original
from v3.artifacts import atomic_json, seal, unseal, read, scoped
from v3.validation_extension_a13 import prepare, RESERVED
from v3.multihost_a11 import freeze
r=scoped(Path(os.environ['REH'])/'dispatch'); assert not r.exists(); r.mkdir(parents=True)
original,root,candidate,projection,inventory,*_=toy_original(r/'inputs')
p=prepare(original,root,candidate,projection,inventory,r/'extension.json',
          wall_hours=2,overhead_hours=1,rehearsal=True)
assert not p['registered'] and p['non_registered_rehearsal']
assert all(not RESERVED[0]<=x['seed']<RESERVED[1] for x in p['seed_manifest'])
assert all(c['seed']>=2**128 for q in p['configuration'].values() for c in q['configs'])
atomic_json(r/'pull.json',seal(freeze(p,read(projection),code_commit=os.environ['A13_CODE_COMMIT'])))
print({'jobs':len(p['jobs']),'non_registered':True,'reserved_seeds_used':False})
PY
"$PYTHON" -B -m v3.multihost_a11 prepare "$REH/dispatch/pull.json" "$REH/dispatch/root"
"$PYTHON" -B -m v3.qualification_a11 build "$REH/dispatch/pull.json" \
  "$REH/dispatch/root" "$REH/dispatch/qualification/plan.json"
"$PYTHON" -B -m v3.qualification_a11 run "$REH/dispatch/qualification/plan.json" \
  "$REH/dispatch/qualification/reference.json" --profile x2 --model-service llm \
  --workers 8 --cpu-budget "$X2_CPUS" --mode work
```

Use section 4a's hash-verified bundle transfer and section 16.4's candidate
qualification and comparison commands, replacing `v3_a12` with the new
checkout and `REH` with `v3/runs/a13_rehearsal/dispatch`. The original X2 is
the reference. Qualify the actual non-original Linux host with `--profile
x2 --model-service none --workers 8 --cpu-budget "$CANDIDATE_CPUS"`.
Require at least 20 distinct extension qualification jobs and approved
evidence for this exact code identity and kind. Never fake resources,
hostnames or service actions. Append the approvals to `dispatch/root`.

Start the coordinator through section 12a's watchdog wrapper with
`SPEC=$REH/dispatch/pull.json` and `RUN_ROOT=$REH/dispatch/root`; its command is:

```bash
"$PYTHON" -B -m v3.production_runner launch "$REH/dispatch/pull.json" \
  "$REH/dispatch/root" --profile local --model-service none \
  --workers 1 --threads 1 --cpu-budget 1 --mode work
```

Start the approved candidate first, so it claims the tiny plan's source job.
Then start X2's worker through its service supervisor, using `--profile x2
--model-service llm`, for the independent check. The candidate command is:

```bash
"$PYTHON" -B -m v3.host_a11 --coordinator "$COORDINATOR_SSH" \
  --checkout "$REPAIRCO" --root "$REH/dispatch/root" \
  --scratch "$REH/dispatch/host_candidate" --profile x2 --model-service none \
  --workers 8 --cpu-budget "$CANDIDATE_CPUS" --mode work
```

Require the candidate to perform work, configuration selection to obey its
measured CPU/memory budget, matched nondeterminism checks, completed ordered
replicate checkpoints, and an ended charging interval. Drain after a complete
replicate, resume the same root, and verify its checkpoint hashes persist;
an in-flight replicate repeats its original seed. Require the original X2's
restored-service record and the candidate's `actions_skipped: true` record.
Do not require this tiny natural extension to certify: dispatch mechanics
and the separate synthetic publication/receipt test are separate checks.
Do not retry a scientific mismatch. The E2 preference and timeout cases
remain the controlled-clock tests; do not call them measured network latency.

**Run-side equivalence against c19b54f5.** Create a separate fresh baseline
checkout at `d73acfb1`. Do not apply the new A2 record there. Both checkouts
must use the same frozen Python/numpy, one thread and integer-text setting.
The following script selects two jobs from each of the five run families
by a fixed hash, then freezes identical short non-registered versions with
fixture tables. The toy size and horizon are explicit; this is not the A11
registered-job proof. Save this exact script as `run_equivalence.py` in the
rehearsal evidence directory and copy it byte-identically to each checkout's
`simulation` directory outside the source identity (under `v3/runs/...`).

```python
import os, sys
from pathlib import Path
from copy import deepcopy
sys.path.insert(0, str(Path.cwd()))
from v3.artifacts import canonical, digest, stable_job, code_identity, atomic_json
from v3.tables_a10 import paired_runs, arm_runs, correct_runs
from v3.sensitivity_a6 import build_weight_corner_jobs, build_horizon_jobs
from v3.production_runner import execute
from v3.production_tables import ProductionTables, row_key
from v3.policies import execution_policy_class
from v3.artifacts import seal
assert code_identity()==os.environ['THIS_CODE']
cal='v3/runs/registered/v3_rerun_calibration.json'
table='v3/runs/a10_stage1/nominal/v3_rerun_tables_A10.json'
arms=arm_runs(cal,table,'UNUSED_STAGE_2_SQRT_TABLE')
groups={'main':paired_runs(cal,table),
        'weight_corner':correct_runs(build_weight_corner_jobs(cal,table)),
        'horizon':correct_runs(build_horizon_jobs(cal,table))}
for name,k in [('k1p5',1.5),('k2p3',2.3)]:
    groups[name]=[j for j in arms if j['config']['model']['instrument']==dict(mapping='A10',k_star=k,g='linear')]
out=[]
for name,jobs in sorted(groups.items()):
    for index,j in enumerate(sorted(jobs,key=lambda j:digest(['A13-run-rehearsal',j['id']]))[:2]):
        c=deepcopy(j['config']); c.pop('a10_seed_source',None)
        c.update(steps=31,tables_path=None)
        c['model'].update(n_agents=24,carrying_capacity=240,rollout_steps=2)
        toy=stable_job('rerun',c,'validation',index)
        assert not 2**60<=toy['seed']<2**61
        result=execute(toy,registered=False)
        assert 'a13_decision_incidence' not in result
        out.append(dict(family=name,source_job_id=j['id'],job=toy,result=result))
# Independent real-loader check on the same synthetic family, with no admission.
rows={}
for i,rule in enumerate(execution_policy_class()[:3]):
    r=dict(rule_id=rule.rule_id,rule_hash=digest(rule.__dict__),kernel_hash='toy',calibration_hash='toy',
           scoring=dict(alpha=1.,capability=1.,kappa=8.),status='estimated',flow_range=10.,
           lambda_f=dict(mean=0.),continuation=dict(entries=[dict(bin=[1,0,0,0,0,0],value=0.,error=10.)]))
    rows[row_key(r)]=r
manifest=dict(tag='v3_tables',calibration_hash='toy',complete_family=True,sensitivity_status='passed',required_row_keys=sorted(rows))
doc=seal(dict(schema='v3-tables-1',code_hash=code_identity(),fixture=False,manifest=manifest,
              manifest_hash=digest(manifest),rows={k:seal(r) for k,r in rows.items()}))
loaded=ProductionTables(doc,calibration_hash='toy',registered=True)
support={k:[dict(bin=list(b),entry=e) for b,e in sorted(v.items())] for k,v in loaded.continuations.items()}
atomic_json(os.environ['OUT'],dict(runs=out,loader_rows=loaded.rows,loader_support=support))
```

Execute it once in each checkout. `OUT` is inside that checkout and is a
rehearsal file, never a registered path. The script reads no registered table.

```bash
# In the baseline simulation directory:
export THIS_CODE="$OLD_CODE" OUT=v3/runs/a13_rehearsal/old_results.json
"$PYTHON" -B v3/runs/a13_rehearsal/run_equivalence.py
# In the new simulation directory:
export THIS_CODE="$EXPECTED_CODE" OUT=v3/runs/a13_rehearsal/new_results.json
"$PYTHON" -B v3/runs/a13_rehearsal/run_equivalence.py
# Copy old_results.json by verified SHA256 into the new rehearsal directory.
"$PYTHON" -B - <<'PY'
import os
from pathlib import Path
from v3.artifacts import read,canonical,atomic_json,file_hash
r=Path(os.environ['REH'])
old,new=read(r/'old_results.json'),read(r/'new_results.json')
assert len(old['runs'])==len(new['runs'])==10
for x,y in zip(old['runs'],new['runs']):
    assert x['job']==y['job'] and x['source_job_id']==y['source_job_id']
    assert canonical(x['result'])==canonical(y['result'])
assert canonical(old['loader_rows'])==canonical(new['loader_rows'])
assert canonical(old['loader_support'])==canonical(new['loader_support'])
atomic_json(r/'result_equivalence.json',dict(passed=True,jobs=10,
    comparison='all result fields; no result-level exclusions',
    old_sha256=file_hash(r/'old_results.json'),new_sha256=file_hash(r/'new_results.json')))
PY
```

The comparison excludes only the output envelope by not collecting it. It
does not use A11's `comparison_bytes`, which excludes some result-root
metadata. Every existing `result` field must match byte for byte. Any
mismatch halts before the proof. The interpreter's rehearsal review must
add `extension_dispatch`, `extension_resume`, `result_equivalence`,
`loader_equivalence` and `amended_A5_receipt` to section 16.4's case list.
Approve the exact review and evidence hashes separately before step 4.

### 17.3. The A11 proof and its record commit

This revision replaces the unapproved proof at identity `5ae3d3cd`. Leave that
proof and its files untouched. Use the newly committed code identity from
17.1, after a new 17.2 rehearsal. Do not run section 16.5's old proof commands
or reuse its output paths. The original completed source roots, manifests,
jobs, registration pins and bytes remain unchanged.

On X2-1 prepare a new identity-specific executor directory. The handoff files
below contain source locations and code hashes. Prepare `reviewed_reasons.json`
there from the actual old/current source diff, with one substantive reason per
changed source-manifest path; the implementation note's sections through 38
explain the changes. Do not reuse the old eight-file dictionary. The interpreter
reviews the reasons before freeze.

```bash
cd "$REPAIRCO/simulation"
export PROOF="v3/runs/a11_worker_control_${EXPECTED_CODE:0:8}"
test ! -e "$PROOF"
mkdir -p "$PROOF"
cp "$OLDCO/simulation/v3/runs/a12_handoff/sources.json" "$PROOF/sources.json"
cp "$OLDCO/simulation/v3/runs/a12_handoff/producing_source_manifest.json" "$PROOF/producing_source_manifest.json"
cmp "$OLDCO/simulation/v3/runs/a12_handoff/sources.json" "$PROOF/sources.json"
# After the interpreter supplies the reviewed per-file reasons:
"$PYTHON" -B - <<'PY'
import os
from pathlib import Path
from v3.artifacts import read,atomic_json,source_manifest,digest,code_identity
from v3.compatibility_a10 import changed_files
p=Path(os.environ['PROOF']); before=read(p/'producing_source_manifest.json')
assert digest(before)=='c19b54f5bde7180c78a5eba4721c33527c47b84c4d93d2fae757fd3e31452810'
assert code_identity()==os.environ['EXPECTED_CODE']
reasons=read(p/'reviewed_reasons.json')
assert set(reasons)==set(changed_files(before,source_manifest()))
assert all(isinstance(v,str) and v.strip() for v in reasons.values())
atomic_json(p/'reasons.json',dict(producing_source_manifest=before,reasons=reasons))
print({'changed_manifest_files':len(reasons),'source_launches':len(read(p/'sources.json'))})
PY
```

Before execution, compute the selection from the sealed original specs,
without opening their scientific outputs, using A11's exact functions:

```bash
"$PYTHON" -B - <<'PY'
from collections import defaultdict,Counter
import os
from pathlib import Path
from v3.artifacts import read,unseal,atomic_json
from v3.compatibility_a10 import _stratum,_selected
p=Path(os.environ['PROOF']); groups=defaultdict(list); jobs={}
for source in read(p/'sources.json'):
    for j in unseal(read(source['spec']))['jobs']:
        assert j['id'] not in jobs
        jobs[j['id']]=j; groups[_stratum(j)].append(j['id'])
pop=[dict(phase=p,capability=c,setting=s,job_ids=sorted(ids)) for (p,c,s),ids in sorted(groups.items())]
selected=_selected(pop)
counts=Counter('estimation' if jobs[j]['kind']=='table' else 'validation' for j in selected)
assert len(selected)==434 and dict(counts)==dict(estimation=90,validation=344)
atomic_json(p/'selection_check.json',dict(counts=dict(counts),selected_job_ids=selected,populations=pop))
print(dict(counts))
PY
```

The proof now uses `v3.compatibility_shards_a11`, an executor-only tool.
Frozen shards are preferable here to pull dispatch: a proof permits one final
attempt, whereas pull dispatch retries leases. The selection, job bytes,
comparison and approval remain those of `compatibility_a10`. After its one-use start marker, an incomplete, interrupted or mismatching
shard spends the attempt. Before that marker, a reported setup failure leaves
the same shard retryable. Never create another attempt or combine a subset.
A fixed reservation under `v3/runs/registered/.a11_attempts/`, named by the
full old/new identity-pair digest, reserves one attempt regardless of output.
The reservation lives in this checkout; never use a second execution checkout on either host for the same identity pair.
Do not create a second execution checkout on either host or copy a shard to
obtain fresh start markers. The attempt's checkout-relative path is frozen: relocating a copy to obtain
fresh shard markers is refused on either host. Single-host use is available by
supplying only X2-1 in `hosts.json`. The legacy `compatibility_a10 build` also
remains available with per-class memory admission. The legacy `--memory-floor-gb` parameter is deprecated and has no effect.

All commands below are prospective operator execution commands. Use fresh
checkouts on both X2s at the same full `A13_CODE_COMMIT`, with the identity in
17.1. Re-run 17.1's committed-byte and design-pin checks on each. Keep the old
roots stopped and unchanged. Rebuild and review `reasons.json` from the actual
old/new source-manifest difference, including this proof tool and snapshot
changes. The old prep reasons are insufficient at the new identity.

On each host, set its local `REPAIRCO` to that fresh checkout. For transfers,
set `X2_1_SSH` and `X2_2_SSH` to the operator's approved SSH aliases, and
`X2_1_CO` and `X2_2_CO` to the respective absolute checkout paths. These four
deployment values are recorded in the executor log; they are not job inputs.
Use the established transfer-capable key, not the optional RPC-only key.

```bash
cd "$REPAIRCO/simulation"
export PROOF="v3/runs/a11_worker_control_${EXPECTED_CODE:0:8}"
export A13_CODE_COMMIT
export PYTHON="$HOME/miniforge3/envs/phaseb/bin/python3.13"
export PATH="$HOME/miniforge3/envs/phaseb/bin:$HOME/.local/bin:$PATH"
export PYTHONINTMAXSTRDIGITS=0 PYTHONDONTWRITEBYTECODE=1
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
mkdir -p "$PROOF/qualification" "$PROOF/service"
```

Put this supervisor in `$PROOF/supervise.py` on X2-1 and include it in both
transfers below. It owns the local service lease, signals the whole child
process group, waits for workers, and restores the service on every ordinary
exit and catchable interruption. X2-1 uses `llm down/up`. X2-2 uses GUPPI's
`systemctl --user stop llm-flashnext` to free memory and restores with
`~/bakeoff/guppi_flashnext.sh on`. Do not use the helper's `off` action: it
starts gpt-oss and would consume the memory being released. Verify the helper,
unit and health check locally before the approved service window. A power loss or SIGKILL cannot run
cleanup; the operator must restore the service before doing anything else.

```python
import os, platform, shutil, signal, subprocess, sys, time
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))
from v3.artifacts import ROOT, atomic_json, lease, scoped, read, unseal, code_identity, file_hash
from v3.compatibility_shards_a11 import verify_code, load_attempt, host_directory
from v3.service import command

mode, directory, *argv = sys.argv[1:]
assert mode in ('llm', 'guppi') and argv
assert platform.system() == 'Linux'
assert platform.node() == ('yotko-evo-x2' if mode == 'llm' else 'yotko-evo-x2-2')
# All fail-safe checks precede the first service stop.
verify_code(os.environ['A13_CODE_COMMIT'])
assert Path(argv[0]).is_file() and argv[1:3] == ['-B', '-m'] and argv[4] == 'run'
if argv[3] == 'v3.compatibility_shards_a11':
    attempt = load_attempt(argv[5])  # Includes the identity-pair reservation.
    import argparse
    from v3.worker_control import options, settings as worker_settings
    flags = argparse.ArgumentParser()
    flags.add_argument('--host', required=True); flags.add_argument('--workers', type=int)
    options(flags); flags.set_defaults(memory_headroom=None)
    override = flags.parse_args(argv[6:]); assert override.host == platform.node()
    planned = dict(attempt['hosts'][platform.node()]['settings'])
    if override.workers is not None:
        assert override.override_reason
        planned['workers'] = override.workers
    if override.override_reason:
        planned.update(override_reason=override.override_reason, operator=override.operator)
        planned.pop('operator_override', None)
    if override.memory_headroom is not None: planned['memory_headroom'] = override.memory_headroom
    worker_settings(planned)
    shard = host_directory(argv[5], platform.node())
    assert not (shard/'started.json').exists() and not (shard/'result.json').exists()
    bundles = [(snapshot, shard/(kind+'_files')) for kind, snapshot in attempt['snapshots'][platform.node()].items()]
elif argv[3] == 'v3.qualification_a11':
    plan = unseal(read(argv[5])); assert plan['code_hash'] == code_identity()
    assert plan['non_registered'] and not scoped(argv[6]).exists()
    import argparse
    from v3.worker_control import options, settings as worker_settings
    flags=argparse.ArgumentParser()
    flags.add_argument('--profile',choices=('local','x2'),required=True)
    flags.add_argument('--workers',type=int,required=True); flags.add_argument('--cpu-budget',type=int,required=True)
    flags.add_argument('--mode',choices=('normal','work'),default='work'); flags.add_argument('--model-service',choices=('none',),required=True)
    options(flags); chosen=vars(flags.parse_args(argv[7:])); chosen['threads']=1
    worker_settings(chosen)
    bundles = [(plan['inputs'], Path(argv[5]).parent/plan['bundle_directory'])]
else:
    raise ValueError('unexpected supervised command')
for snapshot, bundle in bundles:
    for row in unseal(snapshot)['files']:
        assert file_hash(bundle/row['path']) == row['sha256']
helper = Path.home() / 'bakeoff/guppi_flashnext.sh'
if mode == 'guppi':
    assert helper.is_file() and os.access(helper, os.X_OK) and shutil.which('systemctl')
    assert subprocess.run(['systemctl', '--user', 'show', 'llm-flashnext', '--property=LoadState', '--value'],
                          check=True, capture_output=True, text=True).stdout.strip() == 'loaded'
else:
    assert shutil.which('llm')
root = scoped(directory); root.mkdir(parents=True, exist_ok=True)
assert not (root/'service.json').exists(), 'use a new service log directory for a preflight retry'
record = dict(host=platform.node(), service=mode, started_epoch=time.time())
process = None
def interrupted(number, frame):
    raise KeyboardInterrupt('proof supervisor interrupted')
for sig in (signal.SIGINT, signal.SIGTERM):
    signal.signal(sig, interrupted)
def service(action):
    if mode == 'llm':
        return command(root, action)
    helper = Path.home() / 'bakeoff/guppi_flashnext.sh'
    with (root / (action + '.log')).open('a') as log:
        argv = ['systemctl', '--user', 'stop', 'llm-flashnext'] if action == 'down' else [str(helper), 'on']
        return subprocess.run(argv, stdout=log, stderr=subprocess.STDOUT, timeout=180).returncode
with lease(ROOT / 'service.lock'):
    try:
        record['down_exit_code'] = service('down')
        atomic_json(root / 'service.json', record)
        assert record['down_exit_code'] == 0
        process = subprocess.Popen(argv, start_new_session=True)
        record['child_exit_code'] = process.wait()
        assert record['child_exit_code'] == 0, 'qualification or proof failed'
    finally:
        for sig in (signal.SIGINT, signal.SIGTERM):
            signal.signal(sig, signal.SIG_IGN)
        if process is not None and process.poll() is None:
            os.killpg(process.pid, signal.SIGINT)
            process.wait()  # No service restoration while workers remain.
        try:
            record['up_exit_code'] = service('up')
        finally:
            record['finished_epoch'] = time.time()
            atomic_json(root / 'service.json', record)
        assert record['up_exit_code'] == 0, 'operator must restore the model service'
```

First build the qualification bundle on X2-1. It uses only the source plans'
short configuration profiles, deterministic non-registered streams and the
same A11 comparison. There are at least 20 distinct jobs **per kind**. The
bundle binds current code and covers table, A4 fit, validate and census; the
command reads no registered reference result. It copies precisely the input
dependencies of those short jobs, with hashes and absolute-path aliases.

```bash
"$PYTHON" -B -m v3.compatibility_shards_a11 qualification \
  --sources "$PROOF/sources.json" --output "$PROOF/qualification/plan.json"
tar -czf "$PROOF/qualification_bundle.tgz" "$PROOF/qualification/plan.json" \
  "$PROOF/qualification/plan_files" "$PROOF/supervise.py"
sha256sum "$PROOF/qualification_bundle.tgz" > "$PROOF/qualification_bundle.sha256"
scp "$PROOF/qualification_bundle.tgz" "$PROOF/qualification_bundle.sha256" \
  "$X2_2_SSH:$X2_2_CO/simulation/$PROOF/"
# On X2-2, from its simulation directory:
sha256sum -c "$PROOF/qualification_bundle.sha256"
tar -xzf "$PROOF/qualification_bundle.tgz"
```

Run the following two commands on X2-1, sequentially, with its approved
service window. Review the load sheet first. Set `WORKERS` intentionally on each host (24
below is an example); the reasoned target bypasses the measured configuration
choice, while the mode cap, CPU budget and per-class memory admission still apply. The phaseb environment
stays frozen. `--model-service none` prevents an inner service cycle because
the outer supervisor owns it.

```bash
export WORKERS=24
export OVERRIDE_REASON='Matty: intentional worker target after load-sheet review'
"$PYTHON" -B -m v3.production_runner load-sheet "$PROOF/qualification/plan.json" \
  --profile x2 --workers "$WORKERS" --cpu-budget 32 --threads 1 --mode work \
  --override-reason "$OVERRIDE_REASON" --operator Matty --memory-headroom 0.8
"$PYTHON" -B "$PROOF/supervise.py" llm "$PROOF/service/reference" \
  "$PYTHON" -B -m v3.qualification_a11 run "$PROOF/qualification/plan.json" \
  "$PROOF/qualification/reference.json" --profile x2 --workers "$WORKERS" --cpu-budget 32 --mode work --model-service none \
  --override-reason "$OVERRIDE_REASON" --operator Matty --memory-headroom 0.8
"$PYTHON" -B "$PROOF/supervise.py" llm "$PROOF/service/x2_1_qualification" \
  "$PYTHON" -B -m v3.qualification_a11 run "$PROOF/qualification/plan.json" \
  "$PROOF/qualification/x2_1.json" --profile x2 --workers "$WORKERS" --cpu-budget 32 --mode work --model-service none \
  --override-reason "$OVERRIDE_REASON" --operator Matty --memory-headroom 0.8
llm status
```

Run the candidate on X2-2, then copy only its sealed result and service
record back by hash. Neither a qualification nor a proof is resumed after
an interrupted execution.

```bash
export WORKERS=24
export OVERRIDE_REASON='Matty: intentional worker target after load-sheet review'
"$PYTHON" -B -m v3.production_runner load-sheet "$PROOF/qualification/plan.json" \
  --profile x2 --workers "$WORKERS" --cpu-budget 32 --threads 1 --mode work \
  --override-reason "$OVERRIDE_REASON" --operator Matty --memory-headroom 0.8
"$PYTHON" -B "$PROOF/supervise.py" guppi "$PROOF/service/x2_2_qualification" \
  "$PYTHON" -B -m v3.qualification_a11 run "$PROOF/qualification/plan.json" \
  "$PROOF/qualification/x2_2.json" --profile x2 --workers "$WORKERS" --cpu-budget 32 --mode work --model-service none \
  --override-reason "$OVERRIDE_REASON" --operator Matty --memory-headroom 0.8
sha256sum "$PROOF/qualification/x2_2.json" "$PROOF/service/x2_2_qualification/service.json" \
  > "$PROOF/qualification/x2_2.sha256"
tar -czf "$PROOF/x2_2_qualification.tgz" "$PROOF/qualification/x2_2.json" \
  "$PROOF/qualification/x2_2.sha256" "$PROOF/service/x2_2_qualification/service.json"
sha256sum "$PROOF/x2_2_qualification.tgz" > "$PROOF/x2_2_qualification.sha256"
scp "$PROOF/x2_2_qualification.tgz" "$PROOF/x2_2_qualification.sha256" \
  "$X2_1_SSH:$X2_1_CO/simulation/$PROOF/"
# On X2-1:
sha256sum -c "$PROOF/x2_2_qualification.sha256"
tar -xzf "$PROOF/x2_2_qualification.tgz"
sha256sum -c "$PROOF/qualification/x2_2.sha256"
for candidate in x2_1 x2_2; do
  "$PYTHON" -B -m v3.qualification_a11 compare "$PROOF/qualification/plan.json" \
    "$PROOF/qualification/reference.json" "$PROOF/qualification/$candidate.json" \
    "$PROOF/qualification/${candidate}_evidence.json"
done
"$PYTHON" -B - <<'PY'
import os
from pathlib import Path
from v3.artifacts import read, atomic_json, code_identity
from v3.qualification_a11 import validate_evidence
p=Path(os.environ['PROOF']); hosts={}
for name, file in [('yotko-evo-x2','x2_1'),('yotko-evo-x2-2','x2_2')]:
    path=p/'qualification'/(file+'_evidence.json')
    e=validate_evidence(read(path),code_identity())
    assert e['candidate']['host']==name
    required={'table','a4_fit','a4_validate','a4_census'}
    assert required <= set(e['kinds'])
    assert all(sum(r['kind']==kind and r['passed'] for r in e['proofs'])>=20 for kind in required)
    assert e['reference']['host']=='yotko-evo-x2'
    hosts[name]=dict(qualification=str(path),qualification_plan_sha256=e['plan']['sha256'],
                     settings=e['candidate']['settings'],
                     memory_floor_gb=0.)
atomic_json(p/'hosts.json',hosts)
PY
"$PYTHON" -B -m v3.compatibility_shards_a11 project --sources "$PROOF/sources.json" \
  --hosts "$PROOF/hosts.json" --output "$PROOF/projection_at_new_identity.json"
```

At review, the interpreter compares each host entry's `qualification_plan_sha256` with the bundle's plan hash.
Review both qualification evidence hashes and the measured host rates before
freezing. The operator approves these exact host entries and the projection
against stage 1 headroom. `project` reads sealed specs only and reports totals
and rates, never outcomes or capability slices. It assumes the subsequent
configuration test selects its stated conservative worker counts; a smaller
chosen count extends the wall estimate unless a reasoned override is supplied.
Scheduling uses the ratio of summed per-job worker seconds for the same
qualification jobs. It does not multiply an elapsed concurrency gain by the
worker count again. Older evidence without per-job times is accepted for
scheduling only when its effective worker counts match. The existing
elapsed-time participation rate and ledger charge remain unchanged.
The proof derives each class's measured peak from original completion timing
records and legacy completion-envelope metadata already loaded for the required
comparison, using the registered class estimate only when RSS is absent from
both. Historical phase-derived class estimates use the sealed value until a
class peak exists, then use the existing per-job planning formula with that
peak's 1.2 margin; the old sealed plan is never edited.
Each job reserves the larger of its own registered estimate and that class's
peak times 1.2. The runtime also checks current available memory. A global
maximum is never multiplied by every running job. Review the load sheet before
both supervised shard launches and record every override's reason.

```bash
"$PYTHON" -B -m v3.compatibility_shards_a11 freeze --sources "$PROOF/sources.json" \
  --reasons "$PROOF/reasons.json" --hosts "$PROOF/hosts.json" \
  --commit "$A13_CODE_COMMIT" --output "$PROOF/proof.json"
"$PYTHON" -B - <<'PY'
import os
from pathlib import Path
from v3.artifacts import read,unseal
p=Path(os.environ['PROOF'])
a=unseal(read(p/'proof.attempt.json')); expected=read(p/'selection_check.json')
assert a['selected_job_ids']==expected['selected_job_ids'] and len(a['selected_job_ids'])==434
assert a['record']['populations']==expected['populations']
PY
for host in yotko-evo-x2 yotko-evo-x2-2; do
  "$PYTHON" -B -m v3.compatibility_shards_a11 stage "$PROOF/proof.attempt.json" --host "$host"
done
RESERVATION=$(
  "$PYTHON" -B -c 'import os; from pathlib import Path; from v3.artifacts import read,unseal,SIMULATION; from v3.compatibility_shards_a11 import reservation_path; p=unseal(read(Path(os.environ["PROOF"])/"proof.attempt.json")); print(reservation_path(p["record"]).relative_to(SIMULATION).as_posix())'
)
tar -czf "$PROOF/shard_x2_2.tgz" "$PROOF/proof.attempt.json" "$RESERVATION" \
  "$PROOF/proof.attempt_shards/yotko-evo-x2-2" "$PROOF/supervise.py"
sha256sum "$PROOF/shard_x2_2.tgz" > "$PROOF/shard_x2_2.sha256"
scp "$PROOF/shard_x2_2.tgz" "$PROOF/shard_x2_2.sha256" "$X2_2_SSH:$X2_2_CO/simulation/$PROOF/"
# On X2-2:
sha256sum -c "$PROOF/shard_x2_2.sha256"
tar -xzf "$PROOF/shard_x2_2.tgz"
```

Run each following command on its named host after the operator's proof go.
For a detached launch, put the command in a local script and launch with
`setsid nohup`; keep its PID and log as in section 14. Do not launch a second
copy. `run` first verifies commit, identity, fingerprint and every copied input
hash, makes read-only snapshots, checks each dependency through its input view
(including plain validation's sibling fit), and waits up to 180 seconds for the
largest full-job estimate to fit. It runs that host's configuration tests,
rechecks memory and identity, and only then writes `started.json` and executes
its selected jobs once. A live memory dip while no job is active also waits
up to 1,800 seconds (30 minutes) after the start marker before failing; pre-marker
configuration waits remain bounded at 180 seconds. `preflight.json` records setup refusal; if no
`started.json` or `result.json` exists, retry the same shard in the same checkout
and root, using a fresh service-log directory. Never remove a start marker.
The tests cover the usable mode or explicit worker target, subject to each
class's memory admission. A uniform profile tests only counts its own class can
fill; mixed profiles pack their individual reservations. Chosen counts,
admission traces, elapsed intervals and hashes are in the sealed shard result.
Configuration candidates use the same per-class admission. A live lower target
reduces dispatch during configuration too. Every live target is persisted with
its actor, timestamp and optional reason. Zero pauses without spending a proof
by interruption; an idle memory wait is reset while the target is zero.

```bash
# X2-1:
"$PYTHON" -B -m v3.compatibility_shards_a11 load-sheet "$PROOF/proof.attempt.json" --host yotko-evo-x2 \
  --workers "$WORKERS" --override-reason "$OVERRIDE_REASON" --operator Matty --memory-headroom 0.8
"$PYTHON" -B "$PROOF/supervise.py" llm "$PROOF/service/x2_1_proof" \
  "$PYTHON" -B -m v3.compatibility_shards_a11 run "$PROOF/proof.attempt.json" --host yotko-evo-x2 \
  --workers "$WORKERS" --override-reason "$OVERRIDE_REASON" --operator Matty --memory-headroom 0.8
llm status
# X2-2:
"$PYTHON" -B -m v3.compatibility_shards_a11 load-sheet "$PROOF/proof.attempt.json" --host yotko-evo-x2-2 \
  --workers "$WORKERS" --override-reason "$OVERRIDE_REASON" --operator Matty --memory-headroom 0.8
"$PYTHON" -B "$PROOF/supervise.py" guppi "$PROOF/service/x2_2_proof" \
  "$PYTHON" -B -m v3.compatibility_shards_a11 run "$PROOF/proof.attempt.json" --host yotko-evo-x2-2 \
  --workers "$WORKERS" --override-reason "$OVERRIDE_REASON" --operator Matty --memory-headroom 0.8
```

Verify GUPPI's restored `llm-flashnext` health and both supervisors' zero
restore codes. Copy X2-2's result, start marker and service interval back, then
combine on X2-1. Combine derives each result and start path from the frozen
attempt. Before any combine write it requires every expected file, no extra
result/start files or sibling JSON copies, and readable, valid seals. A missing
transfer, stray file or wrong optional path cross-check refuses without a
binding or final record; correct the transfer and retry the same combine.
After structure passes, combine binds the exact paths and raw hashes. An
infrastructure interruption before a final record can be retried with those
unchanged files. Changed bound files are refused. Identity, commit, host,
fingerprint, partition, per-job hash and pass/fail mismatches remain final.
Once `proof.json` exists, success or failure is final. A missing transfer is
repairable; a missing shard execution is never permission to repeat it.

```bash
# X2-2:
tar -czf "$PROOF/x2_2_result.tgz" "$PROOF/proof.attempt_shards/yotko-evo-x2-2/result.json" \
  "$PROOF/proof.attempt_shards/yotko-evo-x2-2/started.json" \
  "$PROOF/service/x2_2_proof/service.json"
sha256sum "$PROOF/x2_2_result.tgz" > "$PROOF/x2_2_result.sha256"
scp "$PROOF/x2_2_result.tgz" "$PROOF/x2_2_result.sha256" "$X2_1_SSH:$X2_1_CO/simulation/$PROOF/"
# X2-1:
sha256sum -c "$PROOF/x2_2_result.sha256"
tar -xzf "$PROOF/x2_2_result.tgz"
"$PYTHON" -B -m v3.compatibility_shards_a11 combine "$PROOF/proof.attempt.json"
"$PYTHON" -B - <<'PY'
import os
from pathlib import Path
from v3.artifacts import read,unseal,atomic_json
p=Path(os.environ['PROOF']); attempt=unseal(read(p/'proof.attempt.json'))
record=unseal(read(p/'proof.json'))
assert record['passed'] and len(record['proofs'])==434
assert [r['job_id'] for r in record['proofs']]==attempt['selected_job_ids']
assert all(r['passed'] and r['before_sha256']==r['after_sha256'] for r in record['proofs'])
rates={h:e['relative_throughput'] for h,e in attempt['hosts'].items()}
sessions=[]
for path in sorted((p/'service').glob('*/service.json')):
    r=read(path); assert r['up_exit_code']==0
    hours=(r['finished_epoch']-r['started_epoch'])*rates[r['host']]/3600
    sessions.append(dict(path=str(path),host=r['host'],x2_equivalent_hours=hours))
assert {r['host'] for r in sessions}==set(rates)
atomic_json(p/'ledger_charge.json',dict(sessions=sessions,
    x2_equivalent_hours=sum(r['x2_equivalent_hours'] for r in sessions),
    scope='both hosts: qualification, configuration, proof and service overhead; add separately measured staging/combine overhead'))
PY
```

Charge both hosts' measured participation, including failed work, plus the
separately recorded staging/combine overhead. The ledger step also applies
when combine refuses: compute charges from the attempt and service records
without the success assertions. Do not charge `shard.x2_equivalent_hours`
again; that subset of time is already inside the supervisor intervals.

The interpreter reviews the complete source diff, host qualifications, shard
records and the single A11 record. The operator approves it and its record
commit. After explicit operator approval of the successful record, use the
approval command and copy the approved bytes to the canonical path on X2-1:

```bash
"$PYTHON" -B -m v3.compatibility_a10 approve "$PROOF/proof.json" \
  --operator "$OPERATOR_NAME" --date "$APPROVAL_DATE"
"$PYTHON" -B - <<'PY'
import os
from pathlib import Path
from v3.artifacts import read,unseal,file_hash
from v3.compatibility_a10 import RECORD_DIRECTORY,record_name
p=Path(os.environ['PROOF'])/'proof.json'; r=unseal(read(p))
assert r['passed'] and r['operator_approval']['approved']
target=RECORD_DIRECTORY/record_name(r['producing_code_hash'],r['new_code_hash'])
with target.open('xb') as stream: stream.write(p.read_bytes())
assert file_hash(target)==file_hash(p)
print(target)
PY
```

Use section 16.5's single-file record commit procedure, with the title
describing the final A13/A12 and proof-tool changes. These are operator-only
commands; this build performs no approval, copy into registered records, or commit.
A failed proof has no fallback. The new phase is authorized by A13, not
certified by the A11 proof of the old computations.


Create the extension execution checkout at that public record commit and
new roots. On every host verify committed source hashes, the A11 record,
accepted old/new identities, and the strict design pin from 17.1. Use the
record commit as pull dispatch's `code_commit`. Historical A1/A4 plans keep
their original pins; verify ancestry and committed hashes, never compare
their old note to the current working note. Copy only stopped source roots
after `check_done`, with section 16.6's free-disk check before copying and
without a live SQLite WAL.

### 17.4. Freeze extension records, then launch its one round

In the fresh execution checkout, set these executor-only paths to the
unchanged source files: `ORIGINAL_PLAN`, `ORIGINAL_ROOT`, `REFUSED_CANDIDATE`,
`PROJECTION`, and `GLOBAL_SEED_INVENTORY`. Do not print their contents.
The inventory is a sealed mapping with the five complete integer lists
`registered`, `planning`, `probe`, `rehearsal`, `qualification`. Include
every rehearsal and qualification seed just used. The source projection
must have file SHA256
`78a1d3ac253048c7e077b0e4eb12dd3150fa178cf3e63a24c6f0d87f02a8ad8d`
and payload seal
`5ca5225967cf08ad5636f98f12d57fa6ccd753a7ae126bff0edcc09f0af3d8a3`.

```bash
export EXT=v3/runs/a13_extension
mkdir -p "$EXT"
"$PYTHON" -B -m v3.validation_extension_a13 prepare \
  "$ORIGINAL_PLAN" "$ORIGINAL_ROOT" "$REFUSED_CANDIDATE" "$PROJECTION" \
  "$GLOBAL_SEED_INVENTORY" "$EXT/plan.json" --registration "$PIN_FILE" \
  --wall-hours "$APPROVED_EXTENSION_WALL_HOURS" --overhead-hours "$APPROVED_OVERHEAD_X2_HOURS"
```

The builder verifies the projection's payload seal against the original
sealed plan before pricing anything. A mismatch is a finding and halts.
Preparation requires exactly one mode: `--registration` for the actual
extension, or `--rehearsal` for synthetic rehearsal. Omitting both is refused.
It derives eligibility from the original sealed records, pins M, freezes
the full replicate 4 through 3+R_max manifest and checks global collisions.
It prices each distinct eligible source once at B_j/3, fixes R_max at the
largest integer up to 16 under 15 projected X2-hours, and records impossible
rows before launch. Report only R_max and the total projected cost from
pricing. Keep per-stratum prices, widths, N*, original visits and reach
executor-only. The `.public.json` companion supplies the allowed identifier
lists, booleans, E/P/M/error statements, flags and seed check for review.

If R_max is below 6, do not prepare a dispatch or launch workers. Go directly
to Part 2's publication/admission check below. Otherwise freeze the scheduling
extension against the same projection, then qualify, approve the register,
run the configuration test and obtain the extension's separate operator go:

```bash
"$PYTHON" -B -m v3.multihost_a11 freeze "$EXT/plan.json" "$PROJECTION" \
  "$EXT/pull.json" --code-commit "$A13_RECORD_COMMIT"
"$PYTHON" -B -m v3.multihost_a11 prepare "$EXT/pull.json" "$EXT/root"
"$PYTHON" -B -m v3.qualification_a11 build "$EXT/pull.json" "$EXT/root" "$EXT/qualification/plan.json"
```

Use section 17.2's qualification, comparison, register approval, coordinator
and host commands with these EXT paths. The plan is registered here; the
qualification/configuration copies are non-registered and use their own
high-range seeds. Record all newly generated qualification seeds in the
pre-launch global audit and require none to intersect the frozen extension
manifest. Each X2 uses supervised `llm down` and restores on every exit.
Actual charging stays the existing measured host-interval method; overhead
is separately charged and is not part of the 15-hour simulation projection.
Use the existing watchdog, status board and ledger.

Registered preparation reserves the sealed family record at
`v3/runs/a10_stage1/nominal/v3_rerun_tables_A10.a13_round.json`,
independent of `$EXT` or the plan filename. A different plan hash or a second
preparation output is refused, even before launch. The first launch binds
the final frozen plan digest and `$EXT/root` in that same record. The pull
plan keeps the family anchor when saved as `$EXT/pull.json`.
Preserve both the family record and the root's `a13_round.json` reference.
Resumption, including from a copied plan file, must use the recorded root.
A scientific halt is latched in the family record too; another preparation
or a new root cannot clear it or authorize another realization. Rehearsal
plans retain output-relative `.round.json` records and unreserved seeds.

The executor processes replicates sequentially and stops each source only
when every eligible row has N* visitors or R_max is exhausted. It persists
ordered (S_i,N_i) records after each full replicate and transfers them to
the coordinator. No partial trajectory counts as a completed replicate.
After infrastructure interruption, retain completed checkpoints and restart
only the in-flight replicate at its original seed. A scientific halt
certifies nothing, preserves its halt latch and spends the round. Do not
delete a halt record, make another plan, increase R_max or start round two.

### 17.5. Admission, publication, labels and runs

Use `PLAN=$EXT/pull.json` after a launch, or `$EXT/plan.json` for no launch.
The executor runs the first-N* test from extension data alone, replaces only
eligible C0 decisions, re-applies the original census floor, and checks
ineligible row and sidecar bytes. It checks Part 2 before writing:

Publication requires the plan hash in the registered family's anchor.
Certification also requires the recorded root, its matching `identity.json`,
the last launch marked complete, and a passed
`validate_plain_ext/nondeterminism_check.json`. A multi-host launch also
requires the completed pull-dispatch check. Missing completion or check
evidence means resume the same infrastructure attempt. A latched scientific
halt bypasses all extension results, certifies no row and checks every
eligible row under Part 2. It cannot be relaunched.

```bash
"$PYTHON" -B -m v3.validation_extension_a13 publish "$PLAN" "$EXT/root" \
  v3/runs/a10_stage1/nominal/v3_rerun_tables_A10.json
```

The exact target and no-overwrite guard are mandatory.

Before section 7's identity approval, the interpreter checks that the published
receipt's `extension_plan_hash` equals the plan hash in the extension's
`.public.json` record approved before launch (17.4). The family-level round
record is a file in this checkout: a fresh checkout or a deleted record would not
see it, so this check is what binds the published family to the one approved plan.
A mismatch is a finding: no identity approval, no labels and no runs.

Admission failure
means no publication and no labels/runs. Retain the original refusal and
the sealed `v3/runs/a10_stage1/nominal/v3_rerun_tables_A10.a13_round.admission.json`
check, which records only counts, identifiers and the outcome. New A13-pinned A4 families use their run root's
`a13_admission_check.json`. A failed Part 2 check is recorded before refusal.
The amended receipt must retain the original plan_hash and every original
per-job stream_seed byte-for-byte in canonical JSON, and add the extension
plan, stage hashes and complete frozen seed manifest. Do not include the
realized per-source seed subset or stopping replicate in the receipt. Record P and
M together with E, alpha(1+P/M) and alpha*E/M; label the nominal family as
produced under an outcome-informed A13 amendment. Residual admitted rows
stay not_estimable, unavailable, and bound by identifier and hash.

Then use section 7's exact-file/hash identity approval and separate public
identity-record commit at the new identity. Fresh label and run checkouts
start at the appropriate public record commit. Keep the table path string
above and every original calibration path string unchanged. Rebuild all
756 label jobs and all 53,100 run jobs, comparing to the reference inventories
from c19b54f5. If references do not exist, build them in a fresh d73acfb1
checkout before comparing, using the same path strings. Compare label
tables, replicates and simulation seeds; its plan hash, job identifiers and
unused envelope seeds may change. Compare each run configuration, identifier
and seed exactly, plus the cost classes. Use section 16.7's inventory checks
with the A13 design pin and the new identity, not its old pin literals.

A5 preparation uses the original plan and amended receipt, with all extension
seeds in its forbidden set. After labels, finalize the A10 receipt as in
section 9. Each label/run launch has its own qualification, register
approvals, configuration test, operator go, new root and X2 service recovery.
Keep the five run allocations and the stage 1 ceiling unchanged. No original
root resumes at the new identity.

Historical verification applies only to plans registered before the current
48815a65 pin. Publication of the new A5 label plan retains strict current-pin
and working-note checks. A13 decision incidence is a separate run-summary
record; existing result fields, including yield events, retain their bytes.

For the reading at `93474e00`, predefine contributing runs per quantity,
pool the recorded numerators and denominators by branch and retain per-run
rates. Zero denominator is unassessed. Flag any quantity with any nonzero
missing-row incidence. Do not drop or re-estimate flagged quantities, and
do not call an unflagged quantity certified unaffected. The mixed-producer
reader fixture check in the A12 review remains required before reading.
