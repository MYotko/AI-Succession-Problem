# Attack Vector v2.0 Process Validation

## Gate result

**ANCHOR AUDIT RESULT: BLOCKED BY MISSING V2 ATTACK ADAPTER**

The repository statement is confirmed. v2 mode is selected only by `config['policy'] == 'optimize_u_sys_v2'` (`simulation/model.py:153-156`), and `step()` then dispatches directly to `_step_v2` (`simulation/model.py:651-653`). The v2 implementation explicitly states that the v1.x attack policies and COP defenses are intentionally inactive (`simulation/model.py:1196-1205`).

These line references and the compatibility table below resolve against anchor
commit `e41c4f61e0af929a86248ef6902807e1854e91c0`.

## Post-audit adapter implementation

The missing adapter has now been implemented locally, without a commit or full
sweep. The anchor audit result above remains the correct description of the
anchored repository state.

- Configuration validation and supported vectors:
  `simulation/attack_adapter_v2.py:28-80`
- Per-step activation and veto dependency updates:
  `simulation/attack_adapter_v2.py:108-144`
- Eight-axis action adapter:
  `simulation/attack_adapter_v2.py:234-365`
- Stage 2 measurement adapter:
  `simulation/attack_adapter_v2.py:368-403`
- Stage 2 biological ratification:
  `simulation/attack_adapter_v2.py:406-437`
- Succession contamination hook:
  `simulation/attack_adapter_v2.py:440-459`
- Machine-readable per-step diagnostics:
  `simulation/attack_adapter_v2.py:462-486`
- `_step_v2` integration:
  `simulation/model.py:1257-1645`

Domain Masking is rejected as analytic-only rather than represented by synthetic
live rows. Thirteen adapter tests pass, and the original 39-test regression gate
also passes. Full revalidation remains gated on code review, constructor work,
matched-seed smoke runs, timing pilots, and protected output paths.

## Architecture findings

The v2 action has six budget shares plus protective and suppressive constraint postures (`simulation/agents.py:24-31`, `133-144`). `optimize_u_sys_v2` generates and scores those actions directly (`simulation/agents.py:643-690`). Legacy attacks return a scalar or list resource allocation plus one constraint value (`simulation/agents.py:966-1167`). `_step_v2` does not call `AIAgent.decide`; it calls `optimize_u_sys_v2` (`simulation/model.py:1247-1259`, `1348-1353`). Changing an `AIAgent.policy` to a legacy attack name therefore cannot modify the selected v2 action.

The existing comprehensive worker configs do not set the v2 selector (`simulation/monte_carlo.py:103-170`, `207-294`). Its ordinary and phi task constructors only add attack parameters and phi (`simulation/monte_carlo.py:326-382`, `588-640`). The veto constructor also omits the selector and creates `optimize_u_sys` agents (`simulation/run_veto_capture_sweep.py:110-138`). Consequently:

- `data/comprehensive_adversarial_sweeps.csv` is v1.x evidence.
- `data/comprehensive_adversarial_sweeps_v1x2_phi.csv` is v1.x.2 phi evidence.
- Both veto capture artifacts are v1.x evidence.
- `v2` in `veto_capture_sweep_v2.csv` identifies the revised experimental grid, not the simulation substrate.

The formal Stage 2 yield condition is live only inside `_step_v2` when a successor exists (`simulation/model.py:1213-1279`). It compares successor and incumbent v2 utility, records an event, and performs succession when advantage exceeds canonical transition cost (`simulation/model.py:1281-1345`). The v1 falsification, independent evaluation, contamination, architectural independence, cost audit, and validator ratification checks are absent from this block.

`working_factor` is active in `_step_v2` and advances four infrastructure stocks (`simulation/model.py:1385-1406`). It is inactive in every existing attack sweep because those constructors never select v2.

## Per-vector compatibility gate

| Vector | Existing sweep selects v2 | Legacy attack can modify eight-axis action | Named defense evaluated in `_step_v2` | Formal Stage 2 yield participation | `working_factor` in existing run | Result status | Evidence produced by existing sweep |
|---|---|---|---|---|---|---|---|
| Sybil Capture | No | No | No. Randomized panel exists only in v1 COP at `simulation/model.py:945-971`. | Not relevant | No | Unsupported in v2 | Live v1.x |
| Measurement Tampering | No | No | No. Independent evaluation is v1 logic at `simulation/model.py:735-747`. | Relevant in a v2 run with a successor, but falsification and its defense do not participate | No | Unsupported in v2 | Live v1.x |
| Ledger Compromise | No | No | No. Escalation and integrity restoration are v1 logic at `simulation/model.py:816-833`. | Not relevant | No | Unsupported in v2 | Live v1.x |
| Successor Contamination | No | No | No. Architectural independence and contamination are v1 logic at `simulation/model.py:789-801`. | Relevant in a v2 run with a successor, but contamination and the defense do not participate | No | Unsupported in v2 | Live v1.x |
| Domain Masking | No live task | No | Partially at the metric substrate only. `_step_v2` calculates `H_N` with `hn_composite_method` at `simulation/model.py:1433-1443`, but there is no v2 masking intervention or defense comparison. | Not relevant | No | Stubbed and unsupported as a v2 attack | Injected v1.0 to v1.x analytic stub |
| Opaque Reasoning | No | No | No. Transparency attribution and intuition veto are v1 logic at `simulation/model.py:917-923`, `973-983`. | Not relevant | No | Unsupported in v2 | Live v1.x |
| Bootstrap Subversion | No | No | No. Candidate verification occurs in the constructor and calls the v1 scalar projection at `simulation/model.py:255-285`. | Not relevant in the current constructor, which has no successor | No | Unsupported in v2 | Live v1.x |
| Evaluator Collusion | No | No | No. Methodological diversity and peer voting are v1 components at `simulation/agents.py:1183-1191`, `1225-1240`. | Not relevant | No | Unsupported in v2 | Live v1.x |
| Sub-Threshold Drift | No | No | No. CUSUM and trust checks are v1 logic at `simulation/model.py:852-877`, `899-943`. | Not relevant | No | Unsupported in v2 | Live v1.x |
| Engineered Fragility | No | No | No. v2 has stock and shock mechanics at `simulation/model.py:1408-1424`, but it never checks `cop_resilience_monitoring`; the named defense is v1-only at `simulation/model.py:912-915`. | Not relevant | No | Unsupported in v2 | Live v1.x |
| Biological Veto Capture | No | No direct attack action exists | No. `_step_v2` does not accumulate validator dependency or ratify succession, and records dependency fields as zero at `simulation/model.py:1481-1482`. | Relevant and active for successor comparison, but validator capture cannot block the result | No | Unsupported in v2 | Live v1.x despite revised filename |

## Required adapter boundary for a later phase

The local adapter implementation is evaluated against this boundary:

1. Set the v2 selector explicitly in every constructor and assert `model.is_v2_mode`.
2. Transform or constrain the eight-axis action after or during v2 optimization without silently falling back to the legacy tuple interface.
3. Place each named defense in the v2 decision or commit path and expose a defense-fired diagnostic.
4. Preserve formal Stage 2 yield logic for Measurement Tampering, Successor Contamination, and Veto Capture, while adding the attack and defense semantics around that logic.
5. Preserve `working_factor` state evolution and define how attacks may affect its inputs or stocks.
6. Reject a run if expected v2 datacollector fields or adapter diagnostics are absent.
7. Keep Domain Masking analytic unless a non-degenerate v2 intervention and falsifiable success condition are specified.

## Two-machine execution design for the later phase

### Preconditions

- Do not start full sweeps while the compatibility gate is blocked.
- Implement and review the v2 adapter in a separately authorized phase.
- Record the reviewed adapter base commit as `ADAPTER_BASE`.
- Keep `pre-attack-vector-revalidation` immutable as the audit anchor.
- Run the same 39-test preflight plus adapter-specific tests on both machines.

### Branches and transfer model

- Laptop worker branch: `attack-v2-laptop`
- Linux worker branch: `attack-v2-linux`
- The laptop is the sole coordinator. It connects to the Linux worker through SSH to perform preflight, launch persistent jobs, inspect status, and collect results.
- Linux jobs run inside `tmux` or an equivalent persistent supervisor so an SSH or laptop-session interruption does not terminate computation.
- The coordinator records the Linux host identity, remote repository path, session name, process ID, branch, commit, command, and log path before considering a launch successful.
- SSH orchestration does not permit concurrent writes to one checkout. The laptop and Linux machine use separate clones and their assigned worker branches.
- Never commit worker results to `main`.
- Commit and push after each completed vector. One vector equals one independently cherry-pickable result commit.
- After each Linux vector completes, the laptop verifies the remote status and artifact hashes, fetches the Linux branch, and cherry-picks the completed vector commit onto `attack-v2-laptop`.
- The original no-commits rule is incompatible with autonomous cross-machine artifact transfer and restart-safe provenance. The later execution phase should permit worker-branch commits and continue to prohibit commits to `main`.

### SSH coordinator workflow

For each Linux assignment, the laptop coordinator follows this order:

1. Connect by SSH and verify the expected host key and host identity.
2. Fetch origin, check out `attack-v2-linux`, and verify the required base commit and clean worktree.
3. Run the required tests and compare the Linux environment manifest with the laptop-side expectations.
4. Launch the smoke or sweep command in a named persistent session with stdout and stderr directed to a unique log.
5. Confirm that the process remains alive after detaching and that its recorded command targets only Linux-specific output paths.
6. Poll the machine-specific status file, process state, log tail, and partial artifact hashes from the laptop.
7. On successful completion, run protected-file and baseline-hash checks remotely.
8. Commit and push only that completed vector from `attack-v2-linux`.
9. Fetch and independently verify the commit on the laptop before cherry-picking it.

Do not place credentials in repository files, commands, logs, manifests, or status files. Use SSH keys managed outside the repository. Pin the expected host key before unattended execution.

### Machine-local status and output paths

- Laptop status: `simulation/diagnostics/attack_vector_revalidation_status_laptop.md`
- Linux status: `simulation/diagnostics/attack_vector_revalidation_status_linux.md`
- Laptop outputs: `data/attack_vector_revalidation_v2/laptop/<vector>/<run_id>.csv`
- Linux outputs: `data/attack_vector_revalidation_v2/linux/<vector>/<run_id>.csv`
- Manifests: `data/attack_vector_revalidation_v2/<machine>/manifests/<vector>_<run_id>.json`
- Timing pilots: `data/attack_vector_revalidation_v2/<machine>/timing/<vector>_<run_id>.json`

No later command may write any of the four baseline artifact paths.

### Protected-file checks

For each worker commit, build the changed-path list against both the immutable anchor and `ADAPTER_BASE`.

- Against `ADAPTER_BASE`, allow only the machine's unique output subtree, its machine-specific status file, and its environment or timing manifests.
- Against `pre-attack-vector-revalidation`, allow the same worker paths plus the exact reviewed adapter paths recorded in an adapter allowlist with expected blob hashes.
- Reject changes to production code not present in the reviewed adapter allowlist.
- Always reject changes under paper, program-reference, or baseline artifact paths.
- Before push, require `git diff --name-only <base>...HEAD` to be a subset of the applicable allowlist and verify the four baseline artifact hashes against the anchor tag.

### Environment manifests

Each machine records:

- OS and kernel, CPU model, logical and physical core counts, RAM
- Python executable and version
- Exact package versions, including NumPy
- Commit, anchor tag resolution, `ADAPTER_BASE`, branch, and dirty-state check
- Test command and result
- Sweep command, configuration JSON, output hash, start and end timestamps
- Thread limits and worker-process count
- Seed namespace, ordered seed list, and replicate count

### Seeds, pairing, and uncertainty

- Generate a versioned master seed table before assignment.
- Use the same seed for attack and defense members of each condition pair.
- Include vector, grid cell, and replicate ID in records, but do not mix defense state into the underlying random seed.
- Preserve output ordering by explicit keys, not multiprocessing completion order.
- Report binary attack rates with standard error `sqrt(p * (1 - p) / n)`.
- For matched attack-defense binary differences, also report the standard error of within-seed differences.
- Report continuous metric means with `SE = sample_standard_deviation / sqrt(n)`.
- For matched continuous comparisons, report the mean within-seed difference and its paired standard error.
- State denominators and missing or terminated pairs explicitly.

### Smoke, timing, and assignment

Before assignment, each machine runs only an authorized smoke set and timing pilot:

1. One representative attack and defense cell per vector with two matched seeds.
2. Assertions that v2 mode, eight-axis action fields, adapter diagnostics, Stage 2 events where relevant, and `working_factor` stocks are present.
3. A representative timing sample large enough to estimate median seconds per step and per replicate.
4. Estimated core-hours per vector using measured throughput and the final grid.
5. Rebalance by estimated core-hours, not by vector count.

Provisional assignment:

- Laptop: Biological Veto Capture, Successor Contamination, Measurement Tampering, Sybil Capture, Evaluator Collusion.
- Linux: Ledger Compromise, Domain Masking, Opaque Reasoning, Bootstrap Subversion, Sub-Threshold Drift, Engineered Fragility.

Timing pilots may rebalance this assignment.

### Domain Masking policy

If Domain Masking remains analytically closed under v2:

- Do not inject pseudo-replicates into a live Monte Carlo file.
- Produce a separately typed analytic result with the proof assumptions, architecture commit, and applicability limits.
- Exclude it from Monte Carlo row totals, binary standard errors, and pooled attack-rate summaries.
- Run a live sweep only if a reviewed v2-native masking intervention has a non-degenerate damage path and a falsifiable success definition.

## Process conclusion

Running the existing constructors would still regenerate v1.x evidence, plus an injected Domain Masking stub. They have not yet been replaced by v2 revalidation constructors. The adapter removes the architecture-level blocker locally, but full revalidation remains blocked on review, v2 constructor implementation, smoke validation, and timing gates.
