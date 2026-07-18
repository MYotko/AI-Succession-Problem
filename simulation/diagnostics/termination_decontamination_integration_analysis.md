# Termination Max Capability Decontamination Diagnostic

Generated: 2026-07-14

## Existing record confirmation

Read `data/termination_mc_v1x2.csv` and `simulation/run_termination_sweep.py` before running diagnostics. The runner configuration is rr grid including 0.066, phi [5.0, 10.0, 15.0], alpha [0.5, 1.0, 2.0], seeds 0 through 4, n_agents 200, cop_cost_audit True, successor caps [5.0, 10.0, 25.0, 50.0, 100.0], `max_capability = successor_cap`, frontier_floor 0.02, k1_transition 2.164, k2_transition 1.0, beta_transition 0.5, MAX_STEPS 5000, CONV_WINDOW 300, and convergence CV threshold 0.05.

For the requested rr=0.066, cap=50 and cap=100 cells, the per-cell n is 15 because the cell aggregates 3 alpha values by 5 seeds.

| cap | phi | n | survived | survival | termination reasons |
| --- | --- | --- | --- | --- | --- |
| 50 | 5 | 15 | 3 | 20.0% | {'extinction': 12, 'max_steps': 3} |
| 50 | 10 | 15 | 7 | 46.7% | {'extinction': 8, 'max_steps': 7} |
| 50 | 15 | 15 | 7 | 46.7% | {'max_steps': 7, 'extinction': 8} |
| 50 | phi 5 to 15 gradient |  |  | 26.7pp |  |
| 100 | 5 | 15 | 4 | 26.7% | {'extinction': 11, 'max_steps': 4} |
| 100 | 10 | 15 | 5 | 33.3% | {'extinction': 10, 'max_steps': 5} |
| 100 | 15 | 15 | 7 | 46.7% | {'max_steps': 7, 'extinction': 8} |
| 100 | phi 5 to 15 gradient |  |  | 20.0pp |  |

This confirms the recorded cap-conditional phi gradient: cap 50 has 20.0 percent at phi 5 and 46.7 percent at phi 15, a 26.7pp gradient. Cap 100 has 26.7 percent at phi 5 and 46.7 percent at phi 15, a 20.0pp gradient.

## Diagnostic wrapper and attempted run

Added `simulation/diagnostics/termination_decontamination_diagnostic.py`. It calls `GardenModel`, `AIAgent`, and `PeerValidator` without editing `simulation/agents.py`, `simulation/model.py`, or `simulation/metrics.py`. Human audit note: direct replay against the current worktree did not reproduce one original v1.x.2 CSV row. The reason is that `simulation/agents.py`, `simulation/model.py`, and `simulation/metrics.py` have changed substantially since commit `5535896`, the v1.x.2 sweep commit. Therefore the completed rows below are current-code smoke rows and are not valid frozen-baseline evidence for Investigation A.

Planned high-n configuration: rr 0.066, caps [50.0, 100.0], phi [5.0, 10.0, 15.0], alpha [0.5, 1.0, 2.0], seeds 0 through 59, n_agents 200, cop_cost_audit True, frontier_floor 0.02, k1_transition 2.164, k2_transition 1.0, beta_transition 0.5, MAX_STEPS 5000. Regimes: contaminated with `max_capability = successor_cap`, and decontaminated with initial successor capability unchanged but `max_capability = 1.0e12`.

The full 2,160-run diagnostic did not complete in this session. Timed evidence showed one decontaminated 584-step run took about 40 seconds direct, and 5,000-step survivor runs are several minutes each. Multiprocessing at 32, 10, and 4 workers was slower under this sandbox due contention. The run was stopped to avoid producing a misleading partial high-n result.

## Completed partial diagnostic rows

CSV: `simulation/diagnostics/termination_decontamination_diagnostic.csv`

These rows are retained for audit of the attempted run only. They should not be used for the requested high-n frozen-baseline comparison because they were generated from the current worktree, not an archived v1.x.2 execution tree.

| regime | rr | phi | alpha | seed | cap | max_capability | termination | steps | final_pop | final_gen | max_active_cap | max_successor_cap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| decontaminated | 0.066 | 5.0 | 0.5 | 0 | 50.0 | 1000000000000.0 | extinction | 584 | 0 | 6 | 253.125 | 379.6875 |
| contaminated | 0.066 | 5.0 | 0.5 | 0 | 50.0 | 50.0 | extinction | 2430 | 0 | 262 | 50.0 | 50.0 |
| contaminated | 0.066 | 5.0 | 0.5 | 0 | 100.0 | 100.0 | extinction | 1214 | 0 | 58 | 100.0 | 100.0 |
| contaminated | 0.066 | 10.0 | 2.0 | 0 | 50.0 | 50.0 | extinction | 2120 | 0 | 106 | 50.0 | 50.0 |
| contaminated | 0.066 | 5.0 | 2.0 | 0 | 100.0 | 100.0 | extinction | 1246 | 0 | 1 | 1.0 | 100.0 |
| contaminated | 0.066 | 10.0 | 1.0 | 0 | 50.0 | 50.0 | extinction | 3199 | 0 | 350 | 50.0 | 50.0 |

Partial aggregate:

| regime | cap | phi | n | survived | survival | max active cap seen | max successor cap seen |
| --- | --- | --- | --- | --- | --- | --- | --- |
| contaminated | 50 | 5 | 1 | 0 | 0.0% | 50.0 | 50.0 |
| contaminated | 50 | 10 | 2 | 0 | 0.0% | 50.0 | 50.0 |
| contaminated | 100 | 5 | 2 | 0 | 0.0% | 100.0 | 100.0 |
| decontaminated | 50 | 5 | 1 | 0 | 0.0% | 253.125 | 379.6875 |

The completed decontaminated current-code smoke row confirms the wrapper mechanism does decouple the cap in the current worktree: active capability reached 253.125 and successor capability reached 379.6875 with initial successor cap 50.0. This is a mechanical wrapper check only, not a frozen-baseline result.

## Comparison status

The required high-n contaminated versus decontaminated phi-gradient comparison is not complete. Per current evidence, the existing record confirms the small-n contaminated gradient. The attempted current-code rerun exposed an additional audit requirement: Investigation A should be rerun from an archived v1.x.2 tree, for example commit `5535896`, or from an exact reproduction package for the CSV-producing code. The current worktree is not the frozen baseline for this CSV.

## Recommended disposition for human review

Do not update claim language from this partial run. The supported disposition is: the existing CSV confirms the reported contaminated cap-conditional phi gradient at n=15 per phi/cap cell. The high-n result remains open. Before rerunning, execute Investigation A against an archived v1.x.2 tree, not the current v2 worktree, because current production files do not reproduce the original termination CSV. Per current evidence, no contradiction to the contamination-artifact expectation is established, but the decisive comparison has not been run to completion.
