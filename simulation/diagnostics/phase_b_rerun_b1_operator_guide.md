# Phase B rerun operator guide

This runner executes the recovered bytecode without changing its task builder or run function. The build agent runs only non-registered validation tasks. Registered runs are launched by the operator.

## Windows commands

Run from the repository root. Before a registered launch, complete the two-machine crosscheck and retain its comparison result.

Write the override file simulation/diagnostics/phase_b_rerun_runtime_control_YOTKOTEST.json:
{"workers":15,"until":"2026-09-25T07:00:00"}

Launch all four parts on YOTKOTEST:
python -B simulation/diagnostics/phase_b_rerun_executor.py --machine-label YOTKOTEST

Resume the same selection:
python -B simulation/diagnostics/phase_b_rerun_executor.py --machine-label YOTKOTEST --resume

Read status without changing files:
python -B simulation/diagnostics/phase_b_rerun_executor.py --machine-label YOTKOTEST --status

The pinned worktree paths and CPython 3.13 path from the dispatch are defaults. The controller may use CPython 3.13 or newer. Each model run uses the configured CPython 3.13 interpreter in a fresh child.

## Runtime worker control

The operator can replace the runtime control file atomically or edit it directly. The runner rereads it within 30 seconds. Invalid or out-of-range input is logged and retains the previous cap. A reduction lets active children finish.

Explicit count with expiry:
{"workers":10,"until":"2026-09-25T17:00:00"}

Named work mode:
{"mode":"work"}

Clear the override in PowerShell:
Remove-Item -LiteralPath simulation/diagnostics/phase_b_rerun_runtime_control_YOTKOTEST.json

Schedule: simulation/diagnostics/phase_b_rerun_schedule_YOTKOTEST.json.
Progress: simulation/diagnostics/phase_b_rerun_progress.json.
Healthy progress has recent updated_utc, increasing completed counts, running counts within the requested cap after a reduction has drained, decreasing pending counts, and errors recorded explicitly. A transition can temporarily leave running above a newly reduced cap. No child is killed to change the cap.

Use --priority normal to skip the default below-normal Windows priority or Linux nice increment of 10. Priority is execution metadata and does not change tasks.

## Second machine

The operator supplies Git, CPython 3.13 with NumPy, and unchanged copies of the executor, common support, child entry, and crosscheck comparison scripts. The designated interpreter is /home/yotko/miniforge3/bin/python. The declared Linux environment is Python 3.13.12 and NumPy 2.4.4.

The main checkout must contain the amended note as an ancestor of origin/main. Provide two read-only worktrees at:
- O: 45409d469a82bb599fe354e8ae3760e4cc3af048
- R: a370925d53a786a3cdaeb36543c02e7135a0ecab

Each worktree needs the committed evidence bytecode copied to simulation/diagnostics/monte_carlo_phase_b.pyc, raw SHA256 2d79795ca50405ff2586a2751fb38861b592d32008aa5e1aebffd07619781d6b. The executor never creates or modifies those worktrees.

Assuming the operator placed the worktrees at /home/yotko/Dev/phase-b-rerun-O and /home/yotko/Dev/phase-b-rerun-R, run from the Linux repository root:
/home/yotko/miniforge3/bin/python -B simulation/diagnostics/phase_b_rerun_executor.py --python313 /home/yotko/miniforge3/bin/python --arm-o-worktree /home/yotko/Dev/phase-b-rerun-O --arm-r-worktree /home/yotko/Dev/phase-b-rerun-R --machine-label yotko-legion-t5-26iob6 --cpu-budget 12 --crosscheck

Copy phase_b_rerun_xcheck_yotko-legion-t5-26iob6_rows.json to the Windows diagnostics directory. Compare it with the Windows crosscheck:
python -B simulation/diagnostics/phase_b_rerun_xcheck_compare.py simulation/diagnostics/phase_b_rerun_xcheck_YOTKOTEST_rows.json simulation/diagnostics/phase_b_rerun_xcheck_yotko-legion-t5-26iob6_rows.json

Keep the result regardless of whether it is IDENTICAL or DIFFERENT, and copy the comparison result JSON back to the Linux diagnostics directory for any later cross-machine resume. A DIFFERENT result requires whole parts to remain on one machine. An IDENTICAL result permits cross-machine resume under the identity checks. Each machine must retain the interpreter and NumPy versions attested by that crosscheck; an unattested version change is refused.

For a split assignment, assign Part 2 to Linux and Parts 1, 3, and 4 to Windows. Do not also launch the all-parts Windows command above.

Linux Part 2:
/home/yotko/miniforge3/bin/python -B simulation/diagnostics/phase_b_rerun_executor.py --python313 /home/yotko/miniforge3/bin/python --arm-o-worktree /home/yotko/Dev/phase-b-rerun-O --arm-r-worktree /home/yotko/Dev/phase-b-rerun-R --machine-label yotko-legion-t5-26iob6 --cpu-budget 12 --parts 2

Windows remaining parts:
python -B simulation/diagnostics/phase_b_rerun_executor.py --machine-label YOTKOTEST --parts 1 3 4

The Linux default schedule uses its CPU budget less one, with no time rules. Its schedule and override filenames include its machine label. The Linux command above uses 11 workers unless overridden.

## Bringing back a merged part

After the remote part completes, copy these five files into one transfer directory:
- phase_b_rerun_part2_manifest.json
- phase_b_rerun_part2_runs.csv
- phase_b_rerun_part2_completions.jsonl
- phase_b_rerun_part2_steps.csv
- phase_b_rerun_part2_interruption_journal.jsonl

Run the import while the local controller is inactive. Resume an execution with the same --parts selection it started with.

For example, with the transfer directory C:/Users/matty/Downloads/phase-b-part2:
python -B simulation/diagnostics/phase_b_rerun_executor.py --machine-label YOTKOTEST --import-part C:/Users/matty/Downloads/phase-b-part2/phase_b_rerun_part2_manifest.json C:/Users/matty/Downloads/phase-b-part2/phase_b_rerun_part2_runs.csv C:/Users/matty/Downloads/phase-b-part2/phase_b_rerun_part2_completions.jsonl C:/Users/matty/Downloads/phase-b-part2/phase_b_rerun_part2_steps.csv C:/Users/matty/Downloads/phase-b-part2/phase_b_rerun_part2_interruption_journal.jsonl

The import checks every file hash, every run's row hash, and per-run step recovery before placing files. It refuses to overwrite a differing local file. Importing merged evidence does not launch a model run.
