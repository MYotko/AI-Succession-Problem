# Amendment A19: guard authority for registered reruns in an A11 proof, and the dispatch stop

Draft 3, 2026-11-04. It takes effect when the operator adopts it, and the commit that adds it records the adoption. This text is not edited on adoption, because its hash is part of the code identity. Draft 2 was adopted earlier the same day; this draft replaces it. Draft 3 corrects section 8 of draft 2, which was partly false; narrows four claims in sections 3 and 4 that a blind review found stronger than the evidence; and adds the dispatch-stop repair of section 8 and the assembly and metadata fixes of section 9.

## 1. What failed

The A11 record `A11_compatibility_dfbc3b9bf526fc7c0fcd5fc6.json` (producing identity `174ab660`, successor `95f5d91c`) was built on X2-1 and written with `passed` false at 2026-11-04 04:53:49Z. Of 77 sample jobs, all 44 of kind `rerun` differed and all 33 others matched (30 `a5_fvplain`, 3 `a14_validate_plain_ext2`). The failure is final under 17.3 and is not retried.

No committed A11 record before it had proved a `rerun` job. The three committed records cover `a4_census`, `a4_fit`, `table`, `a4_validate` and `a13_validate_plain_ext` only.

## 2. Why

`compatibility_a10._execute_proof` re-executes every non-replay job as `execute(job, registered=False, registration=None)`. For kind `rerun`, `V3Model` then builds its execution guards with no authority (`integration.py`, the registered branch is the only one that sets it). `ExecutionGuards.authorize` admits a succession only when `fixture or bool(self.authority)` (`guards.py`). The 44 reruns load production tables and come from registered specs, so their producing runs held an authority and could transition, while the proof refuses every succession they attempt.

The divergence is in the proof method, not in the successor code. On 2026-11-04 the 44 jobs were re-executed at the producing identity, from `~/v3_a14_exec` at `174ab660`, exactly as the proof executes them. All 44 gave the successor's hash and none gave the original's, with no errors. `guards.py`, `integration.py`, `recording.py` and `canonical()` are byte-identical between the producing commit `8b176c73` and `54bd47e4`, and the rerun tables and calibration are byte-identical in every checkout involved.

That the missing authority is the specific cause was first inferred from the code. Section 5's rehearsal tested it in isolation and confirmed it.

## 3. The change

Inside an A11 proof only, a rerun whose producing spec is registered carries a guard authority in place of the one its run held.

- `collect_record` already verifies each registered source's registration historically (ancestry and committed bytes). It now keeps that verification's result and, for each `rerun` job of a registered spec, records `proof_authority = {a19_proof, job_id, registration, spec_sha256}` on the selected item.
- `_execute_proof` sets the item's authority in a context variable for the duration of that one job and resets it afterwards, as it does the producing identity.
- `compatibility_a10.proof_authority(job)` returns the authority only inside a proof (the producer context is set) and only when the bound authority's `job_id` equals the job's id.
- In `production_runner.execute`, the `rerun` branch, when not registered, assigns that authority to `model.guards.authority` after the model is built.

Assigning after construction stands in for constructing the guards with the authority. That is sound only while nothing in `V3Model.__init__` or `ExecutionGuards` reads the authority before `authorize` runs. It held when the code was read on 2026-11-04, and the 44-of-44 rehearsal is consistent with it, but no test certifies it, and it does not reproduce the registered branch's construction path as such.

The authority never enters a comparison hash or a proof row: the guard keeps it in its own `records`, which no result includes, and only its presence changes behaviour. It does reach one durable file. In the multi-host sharded route, `compatibility_shards_a11.freeze` seals the selected items, authority included, into the proof's attempt file, which freezes the proof's inputs. The single-host build seals the record and the selected job ids, not the items.

## 4. What it does not do

- It grants nothing outside a proof. With no producer context, or no authority bound to the job, `proof_authority` returns nothing and the rerun branch is unchanged.
- Confinement is by job id. On the current dispatch path each proof job runs in its own worker process with its own context, so the authority reaches only the job it was bound to. A caller that ran several proof jobs in one copied context (asyncio tasks, for example) would carry the authority between them, and the job-id check would then be the only barrier. No such caller exists today.
- It grants nothing to a rerun from a non-registered source. Such a run had no authority, and its proof reproduces it without one.
- It does not register, publish or resume anything, and it changes no registered execution: that branch sets its own authority from the live registration as before.
- It does not run the registered branch's other steps (`require_production`, `validate_calibration` registered, `require_a10`, live `verify_registration`). Those refuse or pass and change no state; the producing run passed them.
- Configuration-test jobs are not proofs and carry no authority, so a rerun configuration trial still refuses successions. A trial therefore executes a different path from the run it times, by an amount that has not been measured. That can bias the worker-count choice; it cannot affect a comparison.

## 5. Evidence required before any record is rebuilt

A rehearsal at the A19 identity, in a scratch checkout on X2-1, re-executes the 44 failed jobs through `_execute_proof` in two arms over the same jobs, differing only in the bound authority. With the authority, all 44 hashes must equal the original registered outputs' `before_sha256`. Without it, as a control, all 44 must equal record 3's `after_sha256`. Anything less stops the rebuild. A dress rehearsal of all three planned records follows it: one job of each kind, through the real assembly and the real proof function. A short job must reproduce its original hash. A long one runs for a ten-minute window and must be alive, error-free and consuming CPU at its end, which shows that it runs but is not a comparison. The batch refuses to start unless both rehearsals passed at the exact identity it runs and on the same input documents it builds from.

Results at the earlier candidate identities:

| identity | arm | must equal | matched | equal to the original | equal to record 3 | errors |
|---|---|---|---|---|---|---|
| `7a6630cf`, `25d117c3`, `bcf46b8c` (drafts 1 and 2) | with the authority | original `before_sha256` | 44 | 44 | 0 | 0 |
| the same | without it, control | record 3's `after_sha256` | 44 | 0 | 44 | 0 |

So the authority is the cause on its own, and with it the proof reproduces every one of these registered reruns byte for byte. The dress rehearsal passed at each of those identities. This text's hash is part of the code identity, so the results at this draft's own identity cannot be written into it. They are in the rehearsal records that the batch checks, and in the commit that adds this text.

## 6. Consequences

- The change moves the code identity, so the two verified records at `95f5d91c` no longer bind and all three are rebuilt at the A19 identity under new names, which are new attempts and not retries of the spent ones.
- `production_runner.py` and `artifacts.py` are A2 boundary files, so the A2 record's `a19_proof_authority` block re-pins them. `compatibility_a10.py`, `compatibility_shards_a11.py`, `multihost_a11.py` and `host_a11.py` are outside the A2 boundary and its unchanged dependencies; their changes move the identity only.
- The rebuild runs the record with the newest code paths first, after the rehearsals of section 5.

## 7. Thread limits

`artifacts.configure_threads` set only environment variables, which OpenBLAS reads once at initialization, so under an already-imported numpy (pytest collection, or any caller that imported it first) it changed nothing and `runtime()` refused. That is why a clean suite here reported ten known failures. It now also calls the library's own `set_num_threads` when numpy is already imported. It never imports numpy itself, so a fresh worker still configures before the library starts, and `runtime()` still verifies the effective limit. Tested on X2-1: with numpy imported first, the pool went from 32 to 1.

## 8. The dispatch stop

### 8.1 What draft 2 said, and what was wrong with it

Draft 2 left the time-budget stops out on the ground that "the stops are registered design, not defects", and that the code implements the registered protocol. That was partly false. The registered text makes a launch's wall allowance and charged allowance stop *dispatch*:

- A11 (executing A10), Cost: "The launch stops dispatching when its declared X2-equivalent allowance is reached, as well as at its wall-clock deadline."
- A17 (the stage 2 host register): "Declared charged-hour and wall deadlines both stop dispatch", and "Each launch's declared wall allowance is a dispatch stop".

The code went further than that. At the deadline `production_runner.dispatch` terminated and then killed every running worker, and `worker` discarded a result that finished after its completion deadline. No registered passage provides for killing work in flight or discarding a finished result. Draft 2 also misquoted `AGENTS.md`: it lists those repairs as deferred because a code-identity change would void the A11 proofs a third time, not "to the next identity move".

The operator's rule of 2026-11-02 is that a time budget may refuse to start and must never stop what is running. Since this amendment moves the identity anyway, and a later move would void the A11 proofs again, the repair is made here. Two more defects of the same kind were found while it was built and are corrected with it: the A11 proof's idle memory wait spent the proof's attempt after 30 minutes, and an operator interruption during a single-host recheck latched a nondeterminism halt.

### 8.2 The change

For every launch and every A11 proof at or after this identity:

1. **At a launch's dispatch stop** (its wall deadline, or in a multi-host launch its charged allowance), no new job is dispatched. Every job already running finishes and is recorded exactly like any other completion. The launch then ends incomplete with reason `deadline` (`charged_allowance` for a multi-host charged stop), unless the drain finished every remaining job and check, in which case it completes. The drain's start, the jobs it waited for, the jobs completed during it and the overrun past the deadline are recorded, single-host and multi-host. In a multi-host launch the cutoff is lease admission: a lease granted before the stop runs, and none is granted after it. The drain ends when no lease is active and no session is open, and a launch that completed or halted before the stop has no drain record. The overrun is charged to the launch: A11 already charges a host "until its last job ends", and A17 counts drain.
2. **A finished result is never discarded because of time.** `worker`'s completion-deadline discard is removed, and so is the multi-host coordinator's refusal of a first completion after the wall ceiling.
3. **A projection may refuse a launch only before the launch dispatches its first scientific job.** A scientific job is a job of the sealed manifest whose worker the launch started: in a phase dispatch, in a lease, or as the nondeterminism recheck's re-execution. Configuration trials and jobs the launch found already complete are not. This covers the A3 configuration projection and the first per-phase projection of a launch, including a resumed launch. A projection made after scientific dispatch has begun is recorded as advisory and stops nothing; the launch runs to completion or to its dispatch stop. This narrows A11's "the per-phase projection still apply" to that extent, in both the single-host A4/A5 launch and `multihost_a11.Coordinator.check_projection`.
4. **The configuration test's `configuration_seconds` is a planning figure.** Configuration trials dispatch against the launch's own dispatch stop, and the test's elapsed time is recorded against `configuration_seconds`. A trial still cut short by the dispatch stop refuses scientific dispatch, which is a refusal to start. A host that receives no launch deadline from the coordinator starts no trial.
5. **A single-host nondeterminism recheck that did not run to a comparison** is recorded as not run, with the launch that wrote it. That covers three cases: the dispatch stop had passed; the operator interrupted it with a signal or `interrupt_now`, which now reach a recheck that is paused or running; or the operator stopped dispatch before it started. It is never written as a failure, latches no halt and ends the launch incomplete with reason `deadline`, `interrupted` or `drained`. A recheck that did run is compared exactly as before, and a mismatch halts as before. After an operator stop, a later launch in the same root runs the recheck again. After the dispatch stop, the frozen deadline refuses any later launch in that root, so the phase stays unchecked and certifies nothing: the change removes a false halt, not the need for the check.
6. **A multi-host host's hard stop** is now only the operator's interruption or a lost coordinator. Reaching the wall or the charged allowance stops claims and drains, as in item 1. The coordinator stays until every open session has ended, so neither a running lease nor a host's configuration trials are cut off by a coordinator that has gone quiet, and the participation ledger charges the drain. Lease expiry and heartbeat loss remain the liveness guards.
7. **The A11 proof's memory waits never stop because of time.** When no proof job is running and the smallest pending job does not fit, the proof waits, reports the wait in its scheduling status and in its log at most once a minute, and dispatches as soon as the job fits. It used to raise after 1,800 seconds, which spent the attempt. A shard's preflight memory waits after its attempt is reserved do the same. The single-host preflight's memory checks, made before any reservation, keep their 180-second refusal to start. A job that can never fit the frozen budget is still refused.

The sites:

- Item 1 is in `production_runner.dispatch`, which checks both clocks before each start as well as once per cycle, and in the coordinator's drain record and stop reason.
- Item 2 is in `production_runner.worker` and `multihost_a11.Coordinator.complete`.
- Item 3 is in `production_runner.launch` and `multihost_a11.Coordinator.check_projection`, the latter keyed to the coordinator's launch generation. Each projection row records whether it fitted, was advisory or refused.
- Item 4 is in `production_runner.launch`, `host_a11` and the coordinator's status, which now reports the launch deadline.
- Item 5 is in `production_runner.nondeterminism_check`, which passes the launch's control file to the recheck's dispatch and writes `nondeterminism_check_not_run.json`. No reader takes that file for a check result.
- Item 6 is in the coordinator's status and its monitor, which ends only when no lease is active and no session is open, or on a halt, completion or explicit stop.
- Item 7 is in `compatibility_shards_a11.run_items`, `wait_for_memory` and `preflight`.

### 8.3 What does not change

- The operator's interruption (`interrupt_now`, a signal, an operator stop) still stops running workers at once, also during a drain and during a nondeterminism recheck, and records which jobs must restart from their original seeds. In a multi-host launch it reaches each host through its controls and heartbeat, so it takes effect at each host's next contact. After an `interrupt_now`, the flag must still be cleared before the next launch.
- A scientific stop (A3's first-failure screen, a family failure, a coordinator halt, a real nondeterminism mismatch) is unchanged.
- Refusals to start are unchanged: the single-host frozen-deadline resumption refusal, the pre-dispatch projection refusal, the single-host preflight's memory refusal and the A6 program ceiling. A multi-host coordinator started after its frozen deadline may open a new generation, but the deadline still grants it no claim.
- With no clock to end it, a job that hangs while its host stays healthy holds its worker slot, or its lease, until the operator interrupts it. Likewise, a host that keeps its session open without leaving holds the coordinator's monitor. Lease and heartbeat expiry end only a host that has gone silent.
- A host that asks to join a multi-host launch after its drain has ended (a clock stop in effect, no lease active, no session open) is refused, which is a refusal to start. A host that joins while the drain is still open is admitted, takes no new claim and leaves when it sees the stop. The normal host entry point does not resubmit the outputs of leases a host held before it restarted.
- `integrated_timing.py` and `timing_probe.py` still end a measurement probe at their own time limits. Both are A2 unchanged dependencies, so changing them would widen the A2 exception, and no planned work calls them. They are deferred, not repaired.
- Drain can take a launch past its declared wall allowance by up to the longest running job. That overrun is reported and charged to the launch. No runner appends the A6 consumption entry itself. Whoever records a launch's consumption (`budget_a6.append_consumption`) must use its measured wall time to the end of the drain, not its declared allowance, so the program ceiling's pre-launch check for each later launch counts the overrun.

### 8.4 Evidence

Items 1 to 6 are not on the A11 proof path, which dispatches through `compatibility_shards_a11.run_items` and takes no deadline. The rehearsals of section 5 therefore do not exercise them. Their evidence is the builder's tests with real spawned workers, the full suite and the blind review, and their first use on a real host is the first stage 2 launch, which gets its own dress rehearsal under the standing practice. Item 7 is on the proof path, but the rehearsals reach its wait only if memory runs short. Its evidence is the builder's tests with a simulated clock and simulated memory.

## 9. Assembly and record metadata

- **Assembly time.** Draft 2 hashed a registered rerun spec once per job of that spec while assembling a record. Each spec is now hashed once and the value reused, and a registered extension spec's original plan is read once. For the same inputs at the same identity, the assembled record is identical to draft 2's. In the dress rehearsal on X2-1, which assembles alongside the 44-job rehearsal, record 3's assembly took 2,195 seconds at draft 2 and 1,609 seconds at the first draft 3 candidate. The rest of the assembly's cost is unchanged and not yet attributed. The replay bindings recompute work that grows with the square of a plan's job count, which may be part of it. Assembly costs time and stops nothing.
- **Context reset.** `_execute_proof` now pairs each of its two context-variable sets with its own reset, so a failure between them cannot leave the first set.
- **Operating mode.** Every A11 record so far says `execution.mode` `work`, because `collect_record` wrote it as a placeholder that neither finalizer replaced, though the builds ran in `normal`. `build_record` now records the mode, worker cap and thread count the build was launched with. The sharded `_combine` records each host's as its shard result reports them. At top level it records a mode and a thread count only where every host agrees, and the total worker count when every host reports one. A mode or worker change made live through the worker control during a build is in the worker-control and scheduling records, not in these fields, and the configuration test and memory admission can run fewer workers than the cap. Records already committed are not rewritten, and no verifier, approval step or record name reads these fields.
