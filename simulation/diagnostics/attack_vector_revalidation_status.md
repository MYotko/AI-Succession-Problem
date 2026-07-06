# Attack Vector v2.0 Revalidation Status

## Current state

**V2 ATTACK ADAPTER IMPLEMENTED LOCALLY. FULL REVALIDATION NOT STARTED.**

Phase 1 remains complete as the anchored inventory and compatibility audit. A
separately authorized adapter implementation phase has now modified production
code locally. No full sweeps were run. No baseline artifact, paper, or
program-reference file was modified. Nothing was committed.

## Preflight

- `git fetch --prune --tags origin`: passed
- Clean `git status --porcelain=v1`: passed
- Branch `main`: passed
- `HEAD == origin/main`: passed
- Verified commit: `e41c4f61e0af929a86248ef6902807e1854e91c0`
- Required tests: `39 passed in 28.86s`
- Anchor tag: annotated `pre-attack-vector-revalidation`, created at the verified commit and pushed to origin
- Python: `3.14.3` (`MSC v.1944 64 bit (AMD64)`)
- NumPy: `2.4.4`
- Platform: `Windows-11-10.0.26200-SP0`
- Logical CPU count: `16`

## Findings

- Scenario mapping is confirmed, including Sub-Threshold Drift as Scenarios 29-30.
- All live comprehensive and veto-capture baseline artifacts were generated on the v1.x path.
- `data/veto_capture_sweep_v2.csv` is revision 2 of the sweep design, not v2.0 substrate evidence.
- Domain Masking rows in both comprehensive artifacts are injected analytic stubs, not simulation output.
- Existing sweep constructors do not set `config['policy'] = 'optimize_u_sys_v2'`.
- Legacy attacks return the v1 resource-and-constraint interface and cannot modify the v2 eight-axis action.
- Named v1 COP defenses are intentionally absent from `_step_v2`.
- Formal Stage 2 yield logic and `working_factor` are present in v2, but existing attack sweeps never enter that path.

## Adapter implementation status

- Added `simulation/attack_adapter_v2.py`.
- Integrated action hooks, Stage 2 measurement hooks, biological ratification,
  successor contamination, and adapter diagnostics into `_step_v2`.
- Supported live vectors: Sybil Capture, Measurement Tampering, Ledger
  Compromise, Successor Contamination, Opaque Reasoning, Bootstrap Subversion,
  Evaluator Collusion, Sub-Threshold Drift, Engineered Fragility, and Biological
  Veto Capture.
- Domain Masking remains analytic-only and is rejected by live adapter
  configuration.
- Adapter tests: `13 passed`.
- Original regression gate after integration: `39 passed`.
- Existing comprehensive and veto constructors still select v1.x and must not be
  used for v2 revalidation.

## Approved later orchestration plan

- The laptop will act as the sole coordinator.
- The coordinator will use SSH to preflight, launch, monitor, verify, and collect Linux work.
- Linux computation will run in persistent `tmux` or equivalent sessions so connection loss does not stop jobs.
- The machines will retain separate clones, worker branches, status files, manifests, logs, and output paths.
- Completed Linux vectors will be committed and pushed individually, then fetched, verified, and cherry-picked by the laptop.
- This plan remains gated on adapter review, v2 constructor implementation,
  matched-seed smoke runs, timing pilots, and SSH connection configuration.

## Linux worker provisioning

- Passwordless SSH verified with the dedicated coordinator key.
- Host: `yotko-Legion-T5-26IOB6` at `100.66.189.26`.
- The preexisting checkout at
  `/home/yotko/projects/AI-Succession-Problem` contains unrelated chart changes
  and will not be used or modified.
- Clean worker clone:
  `/home/yotko/projects/AI-Succession-Problem-attack-v2`
- Worker branch: `attack-v2-linux`
- Provisioned base: `e41c4f61e0af929a86248ef6902807e1854e91c0`
- The clean worker branch currently has no adapter changes. Adapter transfer
  must wait for a reviewed adapter base commit or another explicitly approved
  transfer mechanism.

## Deliverables

- `simulation/diagnostics/attack_vector_revalidation_inventory.md`
- `simulation/diagnostics/attack_vector_revalidation_process_validation.md`
- `simulation/diagnostics/attack_vector_revalidation_status.md`
- `simulation/diagnostics/attack_vector_v2_adapter_validation.md`

## Stop condition

Do not run full attack-vector revalidation yet. The next steps are review,
v2-specific constructor implementation, matched-seed smoke tests, and timing
pilots. Linux launch additionally requires the operator's SSH host or alias and
remote repository path.
