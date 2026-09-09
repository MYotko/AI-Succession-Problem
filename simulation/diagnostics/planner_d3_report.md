# v2.1 step 2: rollout magnitude projection and bounded measurement

Implementation and the requested measurements completed. All enumerated T0 checks and T1 through T3 measurement gates passed. No corrected published figure is derived. No characterization sweep was run. The fixed-state measurements executed no model steps; the required existing regression suite retained its own test execution.

## T0. Preconditions and environment record

| Check | Read result | Result |
| --- | --- | --- |
| a. Branch | `git rev-parse --abbrev-ref HEAD` returned `main`, exit 0 | PASS |
| b. Ancestry | `git merge-base --is-ancestor 399e96f6bbc853fb497524382b5d89db310067ae HEAD` exited 0 | PASS |
| c. Tracked status | `git status --porcelain --untracked-files=no` exited 0 with zero stdout lines | PASS |
| d. metrics.py raw SHA256 | `b87c7b7b511977b5858285241cf8dffed7319194a648ef432acc5d32525d483f` | PASS |
| e. model.py and agents.py | Raw and LF-normalized SHA256 recorded below before editing; no expected pin was specified | RECORDED |
| f. Constants read from metrics.py | H_N_V_REF = 0.0238802249185; H_N_MAGNITUDE_SAT_K = 3.0 | PASS |

HEAD read during T0: `399e96f6bbc853fb497524382b5d89db310067ae`. Read-only Git commands used `GIT_OPTIONAL_LOCKS=0`. The status command used the exact requested arguments.

The following T0 stderr warning was recorded and did not halt:

```text
warning: unable to access 'C:\Users\matty/.config/git/ignore': Permission denied
```

The operator-established CRLF worktree/LF blob condition was accepted without comparing worktree bytes with Git blob bytes. Existing production line endings were retained. No file was normalized in place. The unreadable cache and global ignore conditions were accepted as expected and were not repaired. No cache warning was emitted by the exact tracked-only status command.

## T1. Projection constant derived from committed evidence

The source set consists of 40 committed `simulation/diagnostics/drift_char_steps_baseline_*.csv` files, seeds 1835086199 through 1835086238. Paths were enumerated by read-only Git and each CSV was read with `git cat-file blob 399e96f6bbc853fb497524382b5d89db310067ae:<path>`. No working-tree evidence CSV was parsed. The exact paths, Git blob SHA1 values, LF-normalized SHA256 values, full columns, and counted row totals appear in [planner_d3_t1.json](planner_d3_t1.json) and the manifest input inventory.

Counted with csv.DictReader excluding headers: 300 records per file, 12,000 records total, and 11,600 records with step >= 10. Define A = avg_wb * (1 - total_suppression). The filter step >= 10, V > 0, A > 0 retains 9,205 records.

| Quantity calculated from the committed records | Value |
| --- | --- |
| Median V / A^2, frozen K | 0.24292031137077771 |
| K to six decimal places | 0.242920 |
| Mean V / A^2 | 0.24307906093454265 |
| Sample standard deviation, ddof = 1 | 0.0095689871807177387 |
| Population standard deviation, ddof = 0 | 0.0095684673954336327 |
| p05, linear interpolation | 0.22763937639921533 |
| p95, linear interpolation | 0.25888131198848391 |
| Pearson correlation of V and A^2 | 0.99827197819633129 |
| Median absolute relative error of K * A^2 against V | 0.026890085308972234 |

The count, six-decimal K pin, correlation >= 0.99, and median absolute relative error <= 0.05 all passed. The filtered records and per-record calculations are in [planner_d3_t1_filtered.csv](planner_d3_t1_filtered.csv). K was frozen at `2026-09-09T01:28:02.717173+00:00`, before the production edit at `2026-09-09T01:33:50.368954+00:00`.

### Zero variance and contagion

Counted over step >= 10: all 2,395 of 2,395 records with V == 0 have total_suppression >= 1.0. Exception count: 0.

For each run, the prior recorded H_N was paired with the current record population and used in `clip(prev_H_N / max(1, population), 0.5, 2.0)`. The first record of each run has no prior recorded value and was excluded. Counted pairs: 11,960. The maximum raw ratio calculated from these records is `0.005235602094240838`. The distinct clipped-value set is exactly `{0.5}`. Counted unclipped records: 0. Per-record calculations are in [planner_d3_t1_contagion.csv](planner_d3_t1_contagion.csv).

### Operating-point consistency

| Quantity calculated over all records with step >= 10 | Value |
| --- | --- |
| Median avg_wb | 0.80316254042436896 |
| Median total_suppression | 0.61399999999999999 |
| K * (median avg_wb * (1 - median total_suppression))^2 | 0.023347765781868909 |
| V_proj / H_N_V_REF | 0.97770292623087507 |

The operating-point ratio is within the required inclusive interval [0.5, 2.0].

## T2. Implemented changes

In metrics.py, line 55 defines `H_N_V_PROJ_K = 0.24292031137077771` with the requested calibration provenance and ratification comment. Line 57 initializes the observable module counter `H_N_SHAPE_FALLBACK_COUNT`. `DiagnosticStateV2.h_n_shape` is a required field with no default at line 107.

`calculate_h_n` has the keyword-only `return_components=False` parameter at metrics.py line 769. The spectral components branch at lines 843-844 returns `(h_n, shape, V)` when requested. The default spectral return and the existing early-return and legacy expressions retain their prior behavior.

`_build_state_from_model`, beginning at metrics.py line 493, reads the cached shape or obtains it alongside entropy from the novelty log. If shape is unavailable, it uses 1.0 and increments the module counter at line 585. In model.py, the cache is initialized at line 219 and populated from the components call at lines 1531-1539. Scalar early-return and legacy results leave shape unavailable for the observable builder fallback.

In agents.py, lines 531-534 compute the magnitude projection from the cohort-corrected `new_avg_wb` and `total_suppression(candidate)`. Line 553 supplies `h_n=h_n_proj`; dataclasses.replace carries h_n_shape forward without an override:

```python
S_proj = total_suppression(candidate)
V_proj = H_N_V_PROJ_K * (new_avg_wb * (1.0 - S_proj)) ** 2
magnitude = -np.expm1(-H_N_MAGNITUDE_SAT_K * V_proj / H_N_V_REF)
h_n_proj = float(np.clip(state.h_n_shape * magnitude, 0.0, 1.0))
```

## T3. One fixed state and deterministic measurements

The fixture was recorded before production edits in [planner_d3_fixture.json](planner_d3_fixture.json). One model was initialized with 200 agents and seed 20260908. One novelty vector per initialized agent was observed using the existing generate_novelty method at the initial constraint level 0.2 and network_contagion 0.5. Neither model.step nor agent.step was called. The resulting matrix is retained in [planner_d3_fixed_novelty.csv](planner_d3_fixed_novelty.csv). One DiagnosticStateV2 was then built from this observation and reused for all grid and candidate-set comparisons.

The configuration as constructed was:

```json
{
  "cop_cusum_drift": false,
  "cop_methodological_diversity": false,
  "n_candidates_v2": 300,
  "phi": 25.0,
  "policy": "optimize_u_sys_v2",
  "random_seed": 20260908,
  "reproduction_rate": 0.09,
  "rollout_steps_v2": 20
}
```

The six resource axes were each held at 1/6 for every constraint-grid cell. `_constraint_pair_for_index` supplied indices 0 through 35. Each score used `project_u_sys_v2_rollout` with the configured 20 horizons and phi 25.0. The separate standard candidate set contains 300 candidates from `generate_v2_candidates(n=300, rng=numpy.random.default_rng(20260908))`, generated once and reused in both projection conditions.

The measured state values are recorded completely in [planner_d3_fixed_state.json](planner_d3_fixed_state.json). Selected values:

| Fixed-state quantity | Value |
| --- | --- |
| avg_wb | 0.64924284131027521 |
| population | 200 |
| projected_avg_age | 25.315000000000001 |
| h_n | 0.98274232695199548 |
| h_n_shape | 0.98302859774297568 |
| theta_capability | 0.5 |
| transfer_state | 0.5 |

Component API checks on this observation found exact equality between the default return and the entropy component, and between the measured shape component and state.h_n_shape. Empty-input and single-agent early returns remained scalar 0.0 with either setting of return_components.

### T3a. Negative control

The harness bypassed only the projected entropy: after each state update, it replaced h_n with the incoming state.h_n. This in-memory wrapper leaves the other state updates in place and preserves h_n across every horizon. It is not a production option. Measured maximum score minus minimum score over 36 cells: `0.0`, exactly. The control passed. Raw scores are in [planner_d3_negative_grid.csv](planner_d3_negative_grid.csv).

### T3b. Projection-active ordered grid

The following values are measured at the fixed state. V_proj and h_n refer to horizon 1, before the downstream entropy floor. Score is the configured 20-horizon rollout score. The full-precision CSV is [planner_d3_positive_grid.csv](planner_d3_positive_grid.csv).

| c_protective | c_suppressive | total_suppression | V_proj, horizon 1 | h_n, horizon 1 | Score |
| --- | --- | --- | --- | --- | --- |
| 0.0 | 0.0 | 0.0 | 0.10686397261573607 | 0.9830271450809558 | 113.36228584174854 |
| 0.2 | 0.0 | 0.014000000000000002 | 0.10389272672112815 | 0.9830264877885866 | 113.36227181285524 |
| 0.4 | 0.0 | 0.05600000000000001 | 0.09523033310089656 | 0.9830223332573287 | 113.36217829540557 |
| 0.6 | 0.0 | 0.126 | 0.08163082394581801 | 0.9829940147702335 | 113.36146728806055 |
| 0.0 | 0.2 | 0.2 | 0.06839294247407109 | 0.982846162328668 | 113.35722456598114 |
| 0.2 | 0.2 | 0.21400000000000002 | 0.06602013482611128 | 0.9827828059465354 | 113.35528336181838 |
| 0.8 | 0.0 | 0.22400000000000003 | 0.06435091957385349 | 0.9827254612259974 | 113.35348627268657 |
| 0.4 | 0.2 | 0.256 | 0.05915305594582408 | 0.9824461875211076 | 113.34434889413343 |
| 0.6 | 0.2 | 0.326 | 0.04854573802398611 | 0.9808208235701704 | 113.28507467971512 |
| 1.0 | 0.0 | 0.35 | 0.045150028430148495 | 0.9796462248210872 | 113.23880616167409 |
| 0.0 | 0.4 | 0.4 | 0.03847103014166498 | 0.9752011245855967 | 113.05025396493515 |
| 0.2 | 0.4 | 0.41400000000000003 | 0.0366966607403533 | 0.9732465545834923 | 112.96279570253922 |
| 0.8 | 0.2 | 0.42400000000000004 | 0.035454901378558445 | 0.9715951070943801 | 112.88728777351407 |
| 0.4 | 0.4 | 0.456 | 0.03162489660001048 | 0.9645299308036868 | 112.55122125010827 |
| 0.6 | 0.4 | 0.526 | 0.024009769911413115 | 0.9348765402264944 | 111.00086928085575 |
| 1.0 | 0.2 | 0.55 | 0.021639954454686545 | 0.9181786195628652 | 110.06479311777571 |
| 0.0 | 0.6 | 0.6 | 0.01709823561851777 | 0.8682920176148193 | 107.09806396570339 |
| 0.2 | 0.6 | 0.614 | 0.01592230446385421 | 0.8500261480931894 | 105.96302316661308 |
| 0.8 | 0.4 | 0.6240000000000001 | 0.015108000992522295 | 0.8356999170321606 | 105.0578715133477 |
| 0.4 | 0.6 | 0.656 | 0.012645855063455742 | 0.7822951462700816 | 101.58479558233213 |
| 0.6 | 0.6 | 0.726 | 0.008022919608099003 | 0.6242364548278199 | 90.62336205671788 |
| 1.0 | 0.4 | 0.75 | 0.006678998288483505 | 0.558246647860029 | 85.81836480517963 |
| 0.0 | 0.8 | 0.8 | 0.004274558904629441 | 0.408449147476855 | 74.52939556754694 |
| 0.2 | 0.8 | 0.8140000000000001 | 0.0036970659966140034 | 0.36521483370749525 | 71.18586455250446 |
| 0.8 | 0.6 | 0.8240000000000001 | 0.0033102184157450384 | 0.3344484769887493 | 68.78566480266791 |
| 0.4 | 0.8 | 0.8560000000000001 | 0.0022159313361599002 | 0.23886752997990418 | 61.225809480849705 |
| 0.6 | 0.8 | 0.926 | 0.00058518711404377 | 0.06967514835074548 | 47.49993404602592 |
| 1.0 | 0.6 | 0.95 | 0.0002671599315393406 | 0.03244536760348642 | 44.426009199191306 |
| 0.0 | 1.0 | 1.0 | 0.0 | 0.0 | 42.616845958732185 |
| 0.2 | 1.0 | 1.0 | 0.0 | 0.0 | 42.616845958732185 |
| 0.4 | 1.0 | 1.0 | 0.0 | 0.0 | 42.616845958732185 |
| 0.6 | 1.0 | 1.0 | 0.0 | 0.0 | 42.616845958732185 |
| 0.8 | 0.8 | 1.0 | 0.0 | 0.0 | 42.616845958732185 |
| 0.8 | 1.0 | 1.0 | 0.0 | 0.0 | 42.616845958732185 |
| 1.0 | 0.8 | 1.0 | 0.0 | 0.0 | 42.616845958732185 |
| 1.0 | 1.0 | 1.0 | 0.0 | 0.0 | 42.616845958732185 |

Scores are strictly decreasing across the 29 distinct total_suppression values. Equal-suppression cells are treated as ties and checked separately below. Across all 720 logged grid horizons, the carried h_n_shape exactly equals the fixed starting shape; [planner_d3_grid_horizons.csv](planner_d3_grid_horizons.csv) records these states.

### T3c. Tied groups

| total_suppression | Every (c_protective, c_suppressive) pair in the tied group | Measured maximum within-group score difference |
| --- | --- | --- |
| 1 | (0.0, 1.0); (0.2, 1.0); (0.4, 1.0); (0.6, 1.0); (0.8, 0.8); (0.8, 1.0); (1.0, 0.8); (1.0, 1.0) | 0 |

This is the only tied group in the 36-cell grid. The maximum score difference across all tied groups is exactly `0.0`.

### T3d. Effect-size measurements

| Measured quantity at the fixed state | Value |
| --- | --- |
| Projection-active constraint-grid maximum minus minimum score | 70.74543988301636 |
| Projection-active standard-candidate score standard deviation, ddof = 0 | 24.289154190602719 |
| Projection-active standard-candidate score standard deviation, ddof = 1 | 24.329737601009736 |
| Projection-bypassed standard-candidate score standard deviation, ddof = 0 | 21.771344040546573 |
| Projection-bypassed standard-candidate score standard deviation, ddof = 1 | 21.807720580601298 |

The population standard deviation treats the fixed set of 300 scores as the complete set being summarized. The sample standard deviation is also provided with its denominator convention. All candidate actions and both scores are retained in [planner_d3_standard_candidates.csv](planner_d3_standard_candidates.csv).

### T3e and T3f. Saturation and fallback

At total_suppression = 1.0, every saturated grid cell has measured horizon-1 V_proj exactly `0.0` and projected h_n exactly `0.0` before downstream flooring. The observable h_n_shape fallback counter was `0` before state construction, `0` after construction, and `0` after all fixed-state comparisons.

### T3g. Regression

`simulation/test_refactor_1x.py` ran before and after the edit in fresh guarded Python processes through runpy with its original test order and source. The wrapper set the initial NumPy seed to 20260908, while preserving the suite's internal seeds.

| Phase | Exit code | Counted PASS lines | Reported failed tests | Measured elapsed seconds |
| --- | --- | --- | --- | --- |
| Pre-edit | 0 | 22 | 0 | 1.2008986999935587 |
| Post-edit | 0 | 22 | 0 | 1.2107360999943921 |

Both runs reported `22 passed / 0 failed / 22 total`. Captured stdout matched exactly; captured stderr matched exactly and was empty. Changed suite-reported values: none. Wrapper elapsed time is recorded separately. JSON retains captured output with Unicode escapes; plain-text transcripts replace only the existing banner dash with an ASCII hyphen.

### T3h. Argmax observation

| Projection | Argmax total_suppression |
| --- | --- |
| Off | 1.0 |
| On | 0.126 |

## T4. Provenance, diffs, and artifacts

Machine: `YOTKOTEST`. HEAD: `399e96f6bbc853fb497524382b5d89db310067ae`. Python: `3.14.3 (tags/v3.14.3:323c59a, Feb  3 2026, 16:04:56) [MSC v.1944 64 bit (AMD64)]`. NumPy: `2.4.4`.

The operator-stated CPU budget is 16 in normal mode, with a maximum of 15 independent workers. This task required no simulation batch. T1 used one analysis process; pre-edit regression used one process. Post-edit grid measurement and regression were dispatched as two independent processes. Numerical-library thread settings were 1 before NumPy import, and OpenBLAS reported one effective thread through its runtime query in each executed measurement process. No operating-system core reservation was configured.

Bytecode writes were disabled. Guarded Python processes allowed writable opens only for the three authorized production files, planner_d3_ artifacts in simulation/diagnostics, and the explicit os.devnull exemption. No out-of-scope writable-open attempt was recorded. The operator performs the containment diff; this report is not a scope audit.

| Production source | Hash basis | Pre-edit SHA256 | Post-edit SHA256 |
| --- | --- | --- | --- |
| simulation/metrics.py | Raw CRLF worktree bytes | b87c7b7b511977b5858285241cf8dffed7319194a648ef432acc5d32525d483f | 8fdbb78c5ddf41bb5deeb49fe11adfd9db55d323d68d6b5feb24d9e83439c2f7 |
| simulation/metrics.py | LF-normalized bytes | 311e0239e539c2c32473536d5ae6eddf8c2fec88774c83148b4068acbe894fda | 6dc16efdfd4faed1638a96f6c2af7365757d1ca47eeb86deb5619a3e580b901f |
| simulation/model.py | Raw CRLF worktree bytes | a4e5e95a49cea534cd02c8f412981797fd6dfa0e6c8de77aa3d5a6aa31f37c67 | e2c9ea91b5b182915d4db00ea09ba896ec3f85a5d92a7aea7329bc3cce5c2945 |
| simulation/model.py | LF-normalized bytes | 0a42a62268857c25c4bc99fa2162bfeb74c444bfa1f4fef6705a3a7e618d76b7 | 25e65d8daa4332df32198b424b25b1630d7a5aca98971c47eac82df7d5679993 |
| simulation/agents.py | Raw CRLF worktree bytes | d5bad24dc9dafb6e4d374c0ff68b74c73f24a41fbef3a6ddcaa75f8ec6d408d5 | de5f196f4732808d3bba99026f618564505ea4cf557bd2167358a524fe7850c0 |
| simulation/agents.py | LF-normalized bytes | f0c1049370c001c9ac85191f47338ec4be8a197cc5a29332547b95d85a1168c3 | a51f6d833fa2e228aaa4e95ca59f9c7e0f83e5741c94deef88a0ea895554cfca |

The requested unified diffs are [metrics](planner_d3_metrics.diff), [model](planner_d3_model.diff), and [agents](planner_d3_agents.diff). They use LF representations in memory and do not normalize production files. Per-module hashes for every recorded execution, on both labeled raw and LF-normalized bases, appear in [planner_d3_validation.json](planner_d3_validation.json) and the manifest. The harness gained its fixed-grid measurement function between the pre-regression and post-regression executions; the phase-specific harness hashes are retained.

[planner_d3_manifest.json](planner_d3_manifest.json) enumerates every current planner_d3_ output, SHA256 on LF-normalized bytes, and CSV row counts counted with csv.DictReader excluding headers. Non-CSV row counts are null. The manifest self-entry has a null hash to avoid self-reference; its final LF-normalized digest is emitted separately. Input CSVs are inventoried separately as committed sources, not as new outputs.

An initial T4 report-assembly draft referenced an undefined helper name and exited before any file write. The draft was corrected before report generation. No T1 or T3 measurement was rerun or changed. No measurement anomaly occurred in T1 through T3.
