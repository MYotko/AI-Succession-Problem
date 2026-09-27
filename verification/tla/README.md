# Consensus Override Protocol model checks

This directory contains a bounded TLA+ model of the protocol in `docs/The Lineage Imperative v2.0.md`, a candidate correction, exact TLC configurations, raw logs, durable completion records, and the generated report in `results.md`.

The two entry modules instantiate the same `COP_core.tla`. `COP_as_written` sets `Corrected` to false. `COP_candidate` sets it to true. The default candidate includes F060 and F061. Configurations named `quorum-only` deliberately disable those safeguards to expose defects otherwise masked by F062.

`COP_guard_probes.tla` restricts the candidate's initial inputs to isolate one absent emergency safeguard at a time. It retains the candidate's exact Spec and Next relations. Its jobs are declared in `guard-probe-jobs.ps1`. The full report includes these diagnostics and the main ambiguity and fault-budget matrix.

Run from the repository root in PowerShell:

```powershell
& './verification/tla/RunChecks.ps1'
```

Run an individual configuration from this directory:

```powershell
& 'C:/Users/matty/Dev/tools/jre/bin/java.exe' -XX:+UseParallelGC -XX:ActiveProcessorCount=2 -XX:ParallelGCThreads=2 -Xmx768m '-Djava.io.tmpdir=tmp' -cp 'C:/Users/matty/Dev/tools/tla/tla2tools.jar' tlc2.TLC -workers 2 -seed 0 -fp 0 -metadir meta/manual-candidate -config COP_candidate.cfg COP_candidate
```

The default `.cfg` files check `TypeOK` and `TwoKeySafety`. The complete suite checks each requested property separately, both liveness routes, the Byzantine budget boundary, ambiguity variants, missing safeguards, and trust reset. `run-manifest.json` records every configuration. A positive `NeverEmergency` or `NeverReset` counterexample is a reachability witness, not a failed protocol requirement.

The runner launches one Java process at a time with two TLC workers. This keeps the total TLC worker count at two while the unrelated simulation batch runs. It never invokes Python, changes Python processes, downloads prerequisites, or runs mutating git commands. JVM temporary files and every TLC metadata directory are inside this directory. There is no operating system CPU reservation or affinity claim.

Completed results are published atomically after their logs close. Resumption validates the model, configuration, and log SHA-256 hashes before skipping a completed check. An interrupted check restarts, with its own metadata directory, and does not count as completed. The TLC seed and fingerprint polynomial are fixed for reproducibility; two-worker error discovery order and partial counts can still differ. Full passing state counts are reproducible.

`current-run.json` records the owned Java PID and completed, running, and pending counts. Set `stopAfterCurrent` to true in `control.json` to stop between checks; restore false and invoke the runner again to resume. The worker budget remains two. A preliminary trust-abstraction defect and its discarded certification run are preserved under `history/pre-trust-fix`; only the final production matrix belongs in `results.md`.

The bounds are one through four validators in each class. Actual faulty-peer counts range from zero through the constant `f`, capped by the current peer-set size. Peer and biological identities are distinct, the incumbent is excluded, and interested humans are excluded. The representation quotients identity permutations by approval counts, separately for honest and faulty peers. It does not discard any approval-count or honest/faulty overlap case relevant to these predicates.

This is a single-proposal authorization model with voting, adversarial votes, execution, trust decay, and re-bootstrap. It is not a network consensus implementation, a cryptographic proof, a probability model, or a proof for arbitrary validator counts. The zero-peer founding bootstrap is outside the explicitly requested nonempty bounds. See `results.md` for precise assumptions and the conflicting emergency readings.
