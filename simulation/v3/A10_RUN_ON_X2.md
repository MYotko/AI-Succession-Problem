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
