# X2-1 post-update requalification: planning only, 2026-10-29

**Verdict: registered stage 2 must wait for a clean post-reboot byte-identity pass at the original producing identities.** A source hash, a successful import, unchanged Python package versions, or a replay against another post-update replay is not that pass.

**Budget estimate:** 48 X2-equivalent hours, equal to 48 active X2-1 wall-hours at reference rate 1.0; proposed budget ceiling 64 hours. This budget estimate uses measured stage 1 compatibility/extension/label/run costs plus an assumed allowance for single-host memory limits and harness/preflight work. The arithmetic is below. The OS maintenance occurred on **2026-10-29**; this requalification is still to be executed **later, after approval**, against the preserved pre-update references. It authorizes no execution now.

## 1. Scope and release conditions

**Maintenance recorded on 2026-10-29:** the X2-1 before-record at 14:32:21Z shows kernel **7.0.0-34-generic**; the after-record at 15:31:14Z shows **7.0.0-42-generic** and a completed reboot. The five held packages were unheld with versions unchanged: **libc6/libc-bin 2.39-0ubuntu8.9; libgcc-s1/libstdc++6/libgomp1 14.2.0-4ubuntu2~24.04.1**. The after-record shows no held/upgradable packages and no reboot required. The phaseb package-list SHA-256 is unchanged: `039a116d09ecad032d50330b7ae2495ebbb3c9d83f736d8c63c66a230ebc9f01`. The model service was active. These are facts from the archived 2026-10-29 X2-1 maintenance before/after records, not bit-identity evidence. Requalification covers the resulting machine/runtime, using historical registered job definitions and output bytes as the reference. It does not overwrite registered outputs, resume a spent extension, produce a new scientific realization, change an admission decision, or add any result to stage 2.

Use **X2-1 only**, 32 CPUs and at most 31 workers. X2-2 is permanently unavailable to this study; any other host requires a new dated amendment. Hash-verified historical other-host records may be read-only references, never new execution hosts.

Two things are separate:

1. **Environment requalification:** the same source identity and registered job, rerun after the update, compared with its pre-update durable result. This document specifies it.
2. **Code compatibility:** the operator-selected path (a) builds one successor Y before stage 2. Its A11/A12 proofs are a **separate, later comparison**, after this fixed-code environment acceptance, as specified in `A16_FEASIBILITY_v2.md` §2. First compare historical producer X on the new runtime E with archived X outputs; only after that pass compare Y on accepted E with the same archived references. Shared inventories, aliases, selected jobs and setup evidence may support both packets, but a single Y execution cannot prove both transitions. A fixed-code mismatch blocks code acceptance; a Y-only mismatch after X/E passes is investigated as a code-migration failure. Each comparison retains its own approvals, hashes, evidence and cost; no overlap saving is assumed.

## 2. Freeze the reference and sample before replay

From verified immutable pre-update archives, before replay, prepare a reference inventory without displaying scientific values. Record full hashes of the producing source manifests, exact source commits, registered manifests/plans, original design pins, job configurations/seeds, completion records, outputs, calibration/constants, tables/receipts, dependency files and historical compatibility records. The inventory is read-only. If a needed archive is missing or cannot be verified, stop before rerunning that stratum; do not substitute a newly generated reference.

This planning task has **not** opened or copied those scientific outputs. Their machine-only hash verification and comparison belong to the later approved requalification. Keep its human-facing output to sample identifiers, hashes, comparison status, cost, memory, environment and failure provenance.

Select deterministically from configuration/identity metadata, never survival, fire rate, margins, visits, table values, availability or a previous comparison outcome. Freeze the complete list and its hash before executing any selected job. No replacement of a failing, slow or inconvenient selected job.

| Stratum group | Selection | Count | Producing identity for replay |
|---|---|---:|---|
| Original table estimation | Reuse the already frozen A11 selection: two smallest `digest(["A11-compatibility", phase, job_id])` per phase/capability/setting, all if fewer | **90** | `c19b54f5bde7180c78a5eba4721c33527c47b84c4d93d2fae757fd3e31452810` |
| Original fit/plain validate/FV validate/census | Same frozen A11 selection, including primary, doubled population and doubled length; all declared capabilities and both routes | **344** | Same c19b54f5 producer |
| A13 extension | Reuse its A11 selection: capability 1.5 has 2, 1.8 has 2, 2.5 has 1 | **5** | Original full `5df9866f…` identity from its sealed plan/source manifest |
| A14 extension | All completed source jobs, including all recorded replicates of each | **4** | `174ab6600e0bc3514ee4b0f553a85b5e426aea4203621125debfa3cd12fd5afd` |
| A5 labels | Two smallest tagged hashes per capability × replicate index among actual primary-FV label jobs; all if fewer | **At most 90** = 15×3×2 | 174ab660 |
| Main runs | Two per category × α × first-successor capability: R1 3 strata, refinement 3, R2 35 | **82** | 174ab660 |
| k*=1.5 and k*=2.3 | Two per arm × grid × α × first-successor capability: each arm has 1+35 strata | **144** | 174ab660 |
| Weight corners | Two per corner × grid × α × first-successor capability: 4×(1+35) strata | **288** | 174ab660 |
| Horizon | Two from its registered horizon stratum | **2** | 174ab660 |
| **Total** | **434 table + 5 A13 + 4 A14 + ≤90 labels + 516 runs** | **≤1,049 full jobs** | Multiple isolated original-identity checkouts |

For the new run/label selections, sort by `(SHA256(canonical(["A15-OS-requalification-2026-10-29", stratum_tuple, job_id])), job_id)` and take two. Include component/corner identity in the stratum tuple so separate arms cannot merge. Table selections retain their original tag exactly. Report the actual label strata/count before the go; an absent stratum is documented, not silently replaced. Verify the 434 original-table and five A13 selections against their archived selection metadata.

This is a stratified finite sample, not a proof of every possible floating-point operation or every future trajectory. It covers all historical job kinds, table routes/settings, run grids, α values, successor capabilities and weight/horizon modes used as proxies for stage 2. It has no outcome-selected extreme cases. A pass supports the operator's requalification decision; it cannot certify universal determinism.

## 3. Environment and scratch isolation

Retain the archived before/after maintenance records and capture/verify the corresponding current replay fingerprint for:

- machine identity, boot ID, kernel, OS release, CPU model/features/microcode, available affinity/cgroup CPU budget and memory in bytes;
- versions and hashes/provenance of the five unheld packages and actual loaded libc/libgcc/libstdc++/libgomp libraries;
- exact Python executable/version, NumPy version, BLAS/OpenMP libraries and linkage, environment/package lock; stage 1's runbook records Python 3.13.12 and NumPy 2.4.4, which must be checked against the actual archived producing environment;
- numerical thread variables and effective queried library limits, multiprocessing start method, integer-text setting, model-service state and swap/memory preflight;
- full LF-normalized source manifest and exact checkout commit for each producer. Code identity is not merely a Git short hash.

Preserve the archived registered Python/NumPy environment after the completed update unless the operator separately changes it; do not reinstall or change a library to make a mismatch disappear without recording the change. A changed runtime requires a fresh full acceptance sample. Restore known required settings, including spawned processes and `PYTHONINTMAXSTRDIGITS=0` for recorder/reader paths, before testing. Validate effective thread count in each spawned worker.

Create separate scratch source views for c19b54f5, 5df9866f and 174ab660 from locally available immutable commits/archives. The source views are byte-verified and remain unchanged. Put writable scratch job roots under the approved scratch checkout's `simulation/v3/` scope so existing scoped-write guards still apply. Map original absolute input paths through hash-verified, read-only aliases/input views. Do not rewrite a job configuration to change its ID or seed.

Mount or otherwise enforce the original roots and all staged reference copies read-only. No fallback path may reach a writable original. Original completion records/checkpoints are never installed as completed work in the new scratch root. Assert that the fresh output/checkpoint locations are empty before each replay. Preserve scratch failures; cleanup is only a later, explicitly scoped operation.

Run and record `llm down`; verify the actual service and process state. Use supervised `llm up` restoration on every exit. The historical `model_service=none` setting is not a post-reboot assumption. Check at least 16 GB free swap under the existing X2 worker-safety rule, and base worker admission on live available RAM rather than swap.

## 4. Reuse existing nondeterminism machinery, with bounded adapters

Reuse `production_runner.completed` for durable-record validation, the spawned execution/worker-safety path, `configure_threads` and effective-runtime checks. Reuse the comparison conventions in `compatibility_a10.comparison_bytes`. A4's existing `production_runner.nondeterminism_check` is useful for individual table-phase checks, but it selects one short task, writes check records beside the phase, and is not by itself this stratified OS test. Never point it at an original registered root. Run it only on an isolated scratch view where any sibling fit dependency is a verified read-only input.

The external harness must implement explicit same-identity selection/execution. `compatibility_a10.collect_record` requires two different source identities and therefore must **not** be presented as an unchanged same-identity OS-check command. Its lower-level execution/comparison logic can be reused; the OS acceptance record is a separate record, not a forged A11 compatibility record.

For plain-validation replays, mount the original fit result read-only in the dependency view and independently replay the selected fit strata. For table/label/run jobs, provide their exact archived calibration, tables, receipts and provenance. The harness returns hashes and runtime metadata, not scientific values.

**Extensions need special care.** A14's `replay_a14.py` already demonstrates scratch-only A13 replay: it recomputes each recorded replicate from its seed and compares checkpoint bytes instead of loading them as completed work. Reuse that method at the original producer's functions through an external harness. There is no equivalent ready-made A14 extension replay adapter in the inspected code. Prepare and review that bounded external adapter before this plan is launched:

- whitelist the four original A14 jobs, plan hash and original seed manifest;
- invoke the unchanged producing identity's underlying extension computation in fresh scratch, at each recorded replicate seed and full registered settings;
- compare every newly computed replicate, its ordering and required result fields with the archive; reconstruct/verify derived bookkeeping from the fresh replicates, never accept copied scientific fields as proof;
- perform no new draw, statistical opportunity, extended stopping search, publication or family-reservation/halt mutation;
- reserve all writes to scratch and prevent the extension's ordinary launch/publication controllers from touching family records.

At c19b54f5 and 5df9866f, adapters must use those source trees' functions, not transplant a later scientific module. External harness source is separately hashed, outside the simulation identity. The existing A13 adapter's approach is reusable; its newer module cannot be silently inserted into an old identity and still called the old identity.

Before real replay, later approved fixture-only harness checks must demonstrate: a clean comparison passes; altered result bytes fail; altered recorded checkpoint **and** corresponding recorded output together still fail because computation is fresh; missing dependency and unmapped-path access fail closed; a mismatch cannot write/latch anything in a registered family. These checks are included in the requalification budget. None runs during this planning task.

### What “byte-identical” means

First verify the exact SHA-256 of each complete archived output file against its durable completion record. Then compare canonical serialized **job plus scientific result** byte for byte, with no numerical tolerance, rounding, ULP allowance, field loss or aggregate comparison.

Whole output envelopes contain new host/runtime/timing/RSS metadata and therefore cannot literally reproduce their old file bytes. Record those differences separately. Use only the existing named timing exclusions at the result root (`seconds`, `trajectory_seconds`, `rescore_seconds`, `scoring_seconds_by_k_star`); retain every nested result, trajectory, step and scientific field. Assert the envelope and optional result `code_hash` equal the same full original producer identity on both sides, although the existing A11 helper excludes that field from its comparison, same-identity requalification must check it explicitly. Job ID, configuration and seed are byte-identical. Compare raw deterministic serialized checkpoint/result artifacts where the existing producer gives that contract. State these exact exclusions in the acceptance record, rather than claiming identical envelopes.

## 5. Load sheet and cost

All future numbers here are **budget estimates**. At an assumed 123 decimal GB and .8 headroom, usable pool budget is 98.4 GB, replaced by actual post-update `MemAvailable`. Use historical full-job peaks as sizing evidence, retaining 20% RSS margin and the registered estimate. Default one numerical-library thread; no more than 31 workers across all concurrent work. Run one producer group at a time and respect data dependencies.

| Replay class | Historical peak evidence | Proposed concurrency budget estimate / binding cap |
|---|---|---|
| Estimation primary/doubled | 1.562 / 2.996 GB | Up to 31 / 27 after verified class sizing; smaller if memory/configuration binds |
| Plain fit/validate primary/doubled | 1.689 / 3.244 GB | Up to 31 / 25 at 1.2×RSS; preserve actual class reservations |
| FV validate primary/doubled | 6.370 / 12.525 GB | Up to 12 / 6 at 1.2×RSS; memory binds |
| Census | .433 GB | Up to 31; CPU/runnable count binds |
| Main/arms/horizon | 1.043 / 1.103 GB | Up to 31 after qualification; run-spec reserve 2 GB is larger than 1.2×these peaks |
| Labels | Only short-profile .637 GB directly available here; A5 separately retains the older P4 1.9 GB anchor plus 20% | 16 target; conservative ≥4.56 GB planning allowance, or larger actual sealed reservation; verify full-job peak later |
| A13/A14 extension replay | Source-class/replicate memory, plus archive parsing; A14 short trial reservation reached 7.597 GB | At most five / four sample jobs, and memory cap; do not infer ETA from a 31-worker flag |

Before the substantial replay, perform the bounded configuration test in the service-down state, 8/12/16/24/31 candidates where memory and runnable counts permit. Select fastest, smaller within 5%; no two-thread trial without profiling justification. Keep checks from the original process-launch mode; do not compare an in-process run with a spawned original.

Cost basis from `STAGE2_PLAN.public_v2.md` evidence keys COST/CLASS/RUN/LABEL/EXT:

| Charge basis | Budget-estimate arithmetic | X2-equivalent / one-X2 wall h |
|---|---|---:|
| Original 434-job table sample | Measured 19.73 h prior proof × assumed 1.5 allowance for one-host memory/headroom and overhead variation | 29.595 |
| A13 five-job replay | Measured prior A13-phase proof charge | 2.950 |
| A14 four-job full replay | Measured entire four-source-job launch charge used as conservative proxy | 9.770 |
| At most 90 labels | 90×59.39/4,752 measured component charge/job | 1.125 |
| 516 runs | 516×119.98/(31×3,600), using comparable 500-step observed maximum as proxy; horizon difference covered in margin | .555 |
| Harness checks, environment capture, sample freezing, copies, configuration, hashing/cleanup | Assumed operational allowance | 4.000 |
| **Budget estimate** | **47.9946, rounded** | **48.00** |
| **Proposed ceiling (budget)** | Includes retries/uncertainty; not a promised completion time | **64.00** |

The 1.5 factor is an assumption, not measured single-host scaling. Historical proof cost includes different host scheduling; raw worker-hours are not substituted for X2 wall-hours. Before the go, recompute from the frozen sample and actual resource classes. A higher budget estimate requires a budget decision before launching, not a smaller sample.

Operator overrides are limited to operational worker/thread targets, lower caps, memory headroom with reason, timing and budget allocation within the approved ceiling. They may not change the selected jobs, source identities, comparison exclusions or pass rule after replay begins. A failed attempt consumes budget and remains in the record.

## 6. Pass, mismatch and resumption

**Pass requires all of the following:**

1. The exact frozen selection is complete; every archive/dependency hash and original producer pin is verified.
2. Every selected job genuinely re-executed from its original seed in scratch, under its original full source identity and registered settings.
3. Every required deterministic byte comparison agrees; no skipped/missing comparison or unexpected field is treated as a pass.
4. Effective thread limits, process mode, environment fingerprint and memory/concurrency controls are recorded and valid; no uninvestigated OOM/worker death or contamination remains.
5. The interpreter reviews the full comparison/provenance record, and the operator explicitly approves X2-1's post-update qualification. Freeze the acceptance record and source/environment hashes before any stage 2 registered launch.

**On the first mismatch:** stop new dispatch, drain or interrupt safely, preserve scratch/reference hashes and the failed acceptance record, and block stage 2. Do not loosen tolerance, drop the stratum, choose a replacement, redraw a seed or bless aggregate agreement.

Investigate source/input corruption, changed process mode, integer/thread settings, Python/NumPy/BLAS linkage and the changed system libraries/kernel. Reproduce the failing comparison with the same frozen job as a diagnostic, not as a replacement attempt. The original failure remains reported. If restoring a known runtime is proposed, it needs operator approval and a fresh full acceptance sample. If a code repair is proposed, freeze a new identity and follow A11/A12 compatibility/review rules; an environment pass does not grant output compatibility. If the original producing environment also cannot reproduce the archived record, report an integrity/reproducibility finding and do not carry it forward.

An infrastructure interruption preserves completed replay evidence and resumes the same frozen sample/code/environment after verification; an in-flight uncheckpointed job restarts from its original seed. Any environment change between attempts invalidates the shared acceptance fingerprint and requires the full acceptance run again. Reconcile measured cost and the remaining 64-hour allowance before continuing. A sample pass is mandatory but does not remove each stage 2 launch's own qualification, pre-launch configuration, machine-register approval and nondeterminism checks.
