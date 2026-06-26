# Patient Defection Final Report

Generated: 2026-06-26T09:22:00+00:00

## 1. Files Added

- `simulation/defection.py`
- `simulation/diagnostics/patient_defection_sweeps.py`
- `simulation/diagnostics/patient_defection_dryrun.csv`
- `simulation/diagnostics/patient_defection_dryrun_summary.md`
- `simulation/diagnostics/patient_defection_sweep1_yield_response.csv`
- `simulation/diagnostics/patient_defection_sweep1_summary.md`
- `simulation/diagnostics/patient_defection_sweep2_lineage_trajectory.csv`
- `simulation/diagnostics/patient_defection_sweep2_summary.md`
- `simulation/diagnostics/patient_defection_sweep3_capability_constraint.csv`
- `simulation/diagnostics/patient_defection_sweep3_summary.md`
- `simulation/diagnostics/patient_defection_integration_analysis.md`
- `simulation/diagnostics/patient_defection_documentation_suggested_edits.md`
- `simulation/diagnostics/patient_defection_final_report.md`

## 2. Files Modified

- `simulation/agents.py`: v2 optimizer score can use an agent-local defection-adjusted objective. Honest U_sys remains logged and used by yield evaluation.
- `simulation/model.py`: v2 successor construction supports configurable growth rate and lineage-mode defection inheritance. V2 logs honest and actual objective diagnostics.

Files intentionally not modified:

- `docs/lineage_phi_program_reference.md`
- `paper/section_VIII_draft.md`
- `docs/paper_v2_outline.md`
- Legacy test files

Suggested documentation changes are captured only in `patient_defection_documentation_suggested_edits.md`.

## 3. Sweep Runs

| sweep | rows | errors |
| --- | --- | --- |
| Dry run | 16 | 0 |
| Sweep 1 | 1800 | 0 |
| Sweep 2 | 800 | 0 |
| Sweep 3 | 2250 | 0 |

Total substantive rows: 4850.

## 4. Prediction Outcomes

| prediction | outcome | characterization |
| --- | --- | --- |
| Prediction 1: yield rejects defecting successors more often than aligned successors | Refined downward | Eventual first succession occurs in 100 percent of Sweep 1 cells. Honest-evaluation pressure appears in actual-would-fire rejection counts, but it does not block first succession. |
| Prediction 2: L(t) degradation compounds across defecting generations | Not observed | Sweep 2 reaches only generation 2.00 on average for every weight, with zero second-fire rate and no significant final L(t) degradation. |
| Prediction 3: cliff constrains defecting capability accumulation | Supported and sharpened | Sweep 3 second-fire rate is 0 percent in 14 of 15 cells, and 10 percent only at alpha=0.50 with 1.5x growth. No tested cell reaches generation 4 or active capability above 3.0. |

## 5. Framework Defense Characterization

Per current evidence, the v2.0 substrate does not detect patient defection as such. A defecting successor can pass first succession in the below-cliff configuration.

The observed defense is continuation suppression. Formal yield economics and the runaway penalty prevent the tested hidden-goal lineage from compounding across generations. The framework defense therefore holds for the tested cross-generational capability-compounding scenario, but not through first-yield detection.

Gate 5 remains NOT_APPLICABLE. Operational COP defenses against patient defection remain future work.

## 6. Recommended Paper Update

Add a new VIII.8 subsection titled `Cross-Generational Defection`.

Recommended framing:

- Do not claim first-yield detection.
- Do claim that tested patient defection does not compound under v2.0 formal yield economics.
- State that the current substrate defense is continuation suppression, not hidden-goal detection.
- Keep operational COP patient-defection detection as future work.

## 7. Verification

Legacy tests:

```bash
env PYTHONPATH=simulation NUMEXPR_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 OMP_NUM_THREADS=1 pytest simulation/test_invariants.py simulation/test_cop.py simulation/test_refactor_1x.py -q
```

Result:

```text
39 passed in 35.43s
```

Disabled-mode isolation checks:

- v2 zero-profile run matched the same v2 run without an attached defection profile exactly.
- legacy zero-profile run matched the same legacy run without an attached defection profile exactly.

## 8. Commit Boundary

Suggested commit boundary:

```text
Add v2 patient defection characterization
```

Include:

- `simulation/defection.py`
- `simulation/agents.py`
- `simulation/model.py`
- `simulation/diagnostics/patient_defection_sweeps.py`
- patient-defection CSV, summary, integration, suggested-edit, and final-report files

Do not include unrelated pre-existing diagnostics or terminal logs.

## 9. Operator Review Flags

1. Sweep 1 refutes the simple "yield catches first-generation defection" framing. The paper should not use that claim.

2. Sweep 2 does not establish L(t) compounding because lineage depth is blocked. That is a useful defense result, but it means L(t) degradation remains unobserved for patient defection under default formal yield.

3. Sweep 3 supports the cross-generational defense claim through continuation suppression. This is the strongest empirical result.

4. A future isolated L(t) degradation experiment would need intentionally altered conditions, such as fixed successor capability or reduced transition cost, and should be framed as a stress diagnostic rather than the default substrate behavior.
