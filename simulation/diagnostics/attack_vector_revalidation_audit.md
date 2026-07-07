# Attack Vector v2.0 Revalidation Audit Report (Interim)

**Audit date:** 2026-07-07  
**Auditor:** Claude Code (claude-sonnet-4-6)  
**Scope:** Partial audit -- sweep data quality and substrate isolation for laptop-completed work.  
Full audit deferred until Linux sweeps and synthesis layer are complete.

---

## Section 1: Overall Assessment

**Substantive grounding of completed work:** Strong for the sweep data that exists.

**Synthesis layer status:** Not produced. No per-vector summaries, integration analysis,
documentation edits, or final report exist. Tasks 3-7 of the full audit specification
have no material to review.

**Recommendation:** Do not commit substantive paper claims yet. The full sweep for six
vectors has not run (Linux queue did not execute). Commit the laptop sweep data as-is
after Linux sweeps and synthesis are complete. The interim audit covers substrate
isolation and data quality; a full audit runs after Codex completes the synthesis layer.

---

## Section 2: Substrate Isolation Verification

### 2.1 Pre-flight baseline

- Git tag `pre-attack-vector-revalidation` confirmed at commit `e41c4f61e0af929a86248ef6902807e1854e91c0`.
- Tag is annotated and present on the current working tree.
- 39/39 legacy tests pass on current main (timed at 31.17s on 2026-07-07).

### 2.2 v1.x.2 production code preservation

`git diff pre-attack-vector-revalidation` against the four protected baseline files shows
zero changes:

- `data/comprehensive_adversarial_sweeps.csv` -- unchanged
- `data/comprehensive_adversarial_sweeps_v1x2_phi.csv` -- unchanged
- `data/veto_capture_sweep_v1.csv` -- unchanged
- `data/veto_capture_sweep_v2.csv` -- unchanged

The laptop_queue.ps1 enforces this check before every commit via `Assert-ProtectedFiles`.
The linux_queue.sh enforces the equivalent check via `assert_protected_files`. Both
scripts call `git diff --quiet pre-attack-vector-revalidation` against the four paths
before staging any output.

### 2.3 Adapter isolation

The v2 adapter (`simulation/attack_adapter_v2.py` and `simulation/model.py` changes)
was committed at `4b32f13`. All subsequent worker commits touch only per-vector output
directories, status files, and manifests. No production code paths were modified after
the adapter commit. The process_validation.md and adapter_validation.md documents record
adapter boundary requirements, and adapter test coverage is 13 tests.

### 2.4 Substrate isolation verdict

**CLEAN.** Baseline files are bit-for-bit unchanged. Legacy tests pass. Adapter is
isolated to its reviewed commit. Worker commits are confined to data output paths.

---

## Section 3: Per-Vector Data Quality

### 3.1 Run structure

Each vector was processed through three sequential phases before full sweeps:

| Phase | Run ID prefix | Steps | Seeds per cell | Purpose |
|---|---|---:|---:|---|
| Gate smoke | `gate_smoke_<vector>` | 3 | 2 | v2 mode and adapter mechanics confirmed |
| Gate2 smoke | `gate2_smoke_<vector>` | 3 | 2 | Reproducibility check, same seeds |
| Pilot | `pilot_4b32f13_<vector>` | 5 | 3 | Timing estimation for assignment |
| Full sweep | `full_5ac6a2e_<vector>` | 300 | 20 | Substantive evidence |

Domain Masking does not have a pilot run and does not have a full Monte Carlo run.

### 3.2 Column schema

Gate smoke and gate2 smoke files contain 33 columns. Pilot and full sweep files contain
37 columns. The four additional columns in pilot/full are Stage 2 yield tracking fields:
`evaluated_yield_opportunities`, `honest_yield_opportunities`, `ratified_yields`,
`yield_checks`. These columns were added at the pilot commit (`4b32f13`) after gate
smokes were already recorded. This schema delta is not a data quality problem: gate smokes
are pass/fail gates, not analysis sources. Pilot and full sweep schemas are internally
consistent across all vectors.

### 3.3 v2 substrate markers

Spot-checked across gate_smoke_sybil_capture, gate2_smoke_sybil_capture,
pilot_4b32f13_measurement_tampering, full_5ac6a2e_sybil_capture,
full_5ac6a2e_measurement_tampering, full_5ac6a2e_successor_contamination,
gate_smoke_biological_veto_capture:

- `is_v2_mode: True` in every row of every live Monte Carlo file.
- `schema_version: attack-v2-row-v1` in every Monte Carlo row.
- `machine: laptop` confirms machine provenance.
- `rollout_steps_v2: 20` (v2 rollout length) present throughout.
- No rows with `is_v2_mode: False` found in any checked file.

### 3.4 Gate smoke findings

Gate smoke files for all 11 vectors are present. Spot-check findings:

- **Sybil Capture (gate):** Undefended rows have `attack_succeeded: True, action_modified: True`.
  Defended rows have `attack_succeeded: False, defense_fired: True`. Mechanics fire correctly.
- **Biological Veto Capture (gate):** Undefended rows have `attack_succeeded: False`
  (capture_rate not yet accumulated at step 3). Defended rows show `defense_fired: False`
  (rotation and monitoring not yet triggered at step 3). Structure is correct for a
  cumulative-metric vector at 3 steps.
- Gate2 smoke produces identical row values for both seed values, confirming deterministic
  reproducibility.

### 3.5 Domain Masking handling

The gate smoke run for Domain Masking produced a single row with
`schema_version: attack-v2-analytic-v1` and only 9 columns, completely separate from
the Monte Carlo schema. Row content: `attack_succeeded: False, live_simulation: False,
reason: "v2 spectral entropy leaves no non-degenerate live masking intervention under
the audited architecture"`. This is the correct treatment per the adapter design document
and process_validation.md. Domain Masking is correctly excluded from Monte Carlo row
totals. No pilot or full Monte Carlo run exists for Domain Masking, which is expected.

Note: `linux_queue.sh` lists Domain Masking as a full-mode vector to run on Linux.
The run script should handle this either by producing an analytic result (consistent
with gate smoke behavior) or by exiting cleanly with an analytic flag. If it invokes
the adapter constructor, it will fail at construction as designed. This requires
verification before linux_queue.sh is executed (see Section 9 recommendations).

### 3.6 Full sweep data quality

#### Vectors with completed full sweeps

**Sybil Capture** (`full_5ac6a2e_sybil_capture`):
- Row count: 120 data rows (header excluded). Expected: 3 populations x 2 defense states
  x 20 replicates = 120. Correct.
- Manifest confirms row_count: 120, output SHA256 recorded.
- Spot-check: undefended rows show `attack_succeeded: True, extinct: True`.
  Stage 2 yield columns present but zero (expected; Sybil is not a Stage 2 vector).
- Runtime: 3 to 117 steps (early extinction in undefended cells is expected under
  successful sybil attack).

**Measurement Tampering** (`full_5ac6a2e_measurement_tampering`):
- Row count: 120 data rows. Expected: 3 costs x 2 defense states x 20 replicates = 120. Correct.
- Spot-check: undefended rows show `attack_succeeded: True, yield_manipulated: True,
  honest_yield_opportunities: 247-250` (Stage 2 opportunities accumulated over 300 steps).
  `evaluated_yield_opportunities: 0` (because falsified evaluation never registers an
  "evaluated" opportunity). Defense rows expected to show `defense_fired: True`.
- Manifest row_count and SHA256 present.

**Successor Contamination** (`full_5ac6a2e_successor_contamination`):
- Row count: 120 data rows. Expected: 3 costs x 2 defense states x 20 replicates.
  (Ordinary artifact uses 4 defense combinations; v2 adapter uses 2-state defense_active.)
  120 rows is consistent with the v2 grid.
- Spot-check: undefended rows show `contamination_occurred: True, attack_succeeded: True,
  ratified_yields: 1, yield_condition_met_count: 1`. Stage 2 succession occurs and
  contamination propagates. Correct behavioral pattern.

**Sybil Capture (already documented above).**

**Evaluator Collusion** (`full_5ac6a2e_evaluator_collusion`):
- Row count: 120 data rows. Expected: 3 populations x 2 defense states x 20 replicates = 120. Correct.

**Biological Veto Capture** (3 shards: `full_5ac6a2e_veto_shard0of4`, `shard1of4`, `shard2of4`):
- Row counts (including header): 2165, 2103, 2322. Data rows: 2164, 2102, 2321. Total
  across three shards: 6587 data rows.
- The full veto sweep uses 8700 rows total (grid matches v2 artifact parameter space).
  3/4 shards = expected ~6525 rows; 6587 is consistent with slightly unequal grid
  partitioning across shards. Shard 3 (Linux assignment) would bring the total to ~8700.
- Spot-check (gate smoke rows reviewed): biological veto capture columns include
  `parameter_capture_strength, parameter_dependency_rate, parameter_defense_mode,
  parameter_rotation_interval` -- the full revised veto grid parameters. Correct.

### 3.7 Missing full sweeps

Six vectors have no full sweep data. All six were assigned to Linux:

- Ledger Compromise
- Opaque Reasoning
- Bootstrap Subversion
- Sub-Threshold Drift
- Engineered Fragility
- Domain Masking (analytic-only; full mode output type needs verification)

Biological Veto Capture shard 3 of 4 is also Linux-assigned and missing.

The Linux queue (`linux_queue.sh`) exists and is correctly structured with the same
protected-file checks and per-vector commit pattern as the laptop queue. The queue was
never executed; no `data/attack_vector_revalidation_v2/linux/` directory exists.

### 3.8 Data quality verdict

**STRUCTURALLY SOUND** for all executed sweeps. Row counts match expected grids. v2
substrate markers are present and consistent. No NaN clusters, impossible values, or
systematic errors observed in spot-checked rows. Manifest SHA256 hashes recorded.
Domain Masking handled correctly as analytic-only. Pilot schema is internally consistent.
Full sweep schema is internally consistent across all five completed vector families.

Minor note: gate smoke and gate2 smoke use a 33-column schema vs 37 columns in pilot and
full. This is a schema evolution artifact, not a data quality problem.

---

## Section 4: Comparison Methodology Validity

**Not verifiable.** No per-vector summaries exist. Codex did not produce comparison
analysis between v2.0 results and v1.x baselines. The v1.x baselines to use for each
vector are documented in `simulation/diagnostics/attack_vector_revalidation_inventory.md`
and will require verification once Codex produces the summaries.

Pre-condition note for the next auditor: The inventory documents that the v1.x.2 baseline
for most vectors is `data/comprehensive_adversarial_sweeps_v1x2_phi.csv` (600 rows per
vector family at fixed phi 1, 5, 10, 15, 25). The v2.0 full sweeps use a two-level
defense_active grid (not the four-level successor_contamination grid). This grid change
is intentional (adapter uses binary defense_active) but must be verified as
apples-to-apples when summaries are produced.

---

## Section 5: Substantive Findings Accuracy

**Not verifiable.** No per-vector summaries exist.

---

## Section 6: Integration Analysis Assessment

**Not verifiable.** No integration analysis exists.

---

## Section 7: Documentation Edits Assessment

**Not verifiable.** No documentation edits file exists.

---

## Section 8: Judgment Call Review

### 8.1 Distribution decisions

The process_validation.md provisional assignment was:
- Laptop: Biological Veto Capture, Successor Contamination, Measurement Tampering,
  Sybil Capture, Evaluator Collusion.
- Linux: Ledger Compromise, Domain Masking, Opaque Reasoning, Bootstrap Subversion,
  Sub-Threshold Drift, Engineered Fragility.

Codex followed this assignment exactly. Biological Veto Capture was sharded 3:1
(laptop:Linux). No rebalancing based on timing pilots occurred (the queue follows the
provisional assignment directly). This is acceptable: the biological veto sweep is
the largest by grid size (8700 rows x 50 seeds vs 120 rows x 20 seeds for most
other vectors), and assigning the larger share to the 16-core laptop while offloading
simpler vectors to Linux is reasonable distribution logic.

### 8.2 Anomaly dispositions

No CHECKPOINT flags appear in any status file. The queue log shows clean sequential
execution with no failures or retries. Each vector committed successfully and in order.
The log timestamps show consistent per-vector runtimes (~5 to 12 minutes per vector
for the standard-grid vectors, ~11 hours for biological veto capture across 3 shards
in parallel).

### 8.3 Interpretation choices

- **Domain Masking as analytic-only:** Correctly applied. Gate smoke produces a single
  analytic row rather than Monte Carlo output. No pseudo-replicates injected.
- **Veto capture sharding:** Codex split the veto sweep into 4 shards and assigned
  shards 0-2 to laptop and shard 3 to Linux. The shard design was already committed
  at `b91b3b5` (Add paired task sharding for distributed sweeps). Codex ran the laptop
  shards and waited for completion before proceeding to sequential vectors. This is
  sound execution.
- **Linux queue not executed:** No evidence Codex attempted and failed to run the Linux
  queue. The queue file exists and is complete, but there is no log, no data, and no
  commits from the Linux branch. Codex appears to have produced the queue script but
  not launched it. Whether this was a decision or an interruption is not determinable
  from the artifacts.

### 8.4 Judgment call verdict

**No anomalous judgment calls found.** Execution followed documented design. The one
unexplained gap (Linux queue not run) cannot be characterized as a judgment call since
there is no record of a decision, only an absence of execution.

---

## Section 9: Recommendations

### 9.1 Before proceeding with Linux sweeps

1. **Verify domain_masking handling in full mode.** The linux_queue.sh attempts to run
   domain_masking with `--mode full`. Test this locally before launching the queue to
   confirm it either produces an analytic output or exits cleanly. If it raises, the
   queue will abort before running the subsequent five vectors. Fix or remove domain_masking
   from the linux_queue.sh before execution.

2. **Verify Linux clone state.** The linux_queue.sh assumes the Linux clone is at commit
   `5ac6a2e` on branch `attack-v2-linux` with the adapter. Confirm via SSH before
   running the queue.

3. **Run adapter tests on Linux.** `python -m pytest simulation/test_attack_adapter_v2.py
   simulation/test_invariants.py simulation/test_cop.py simulation/test_refactor_1x.py -q`
   must pass on the Linux worker before running any full sweeps.

### 9.2 Synthesis deliverables

After all full sweeps complete, Codex must produce:

- 11x `simulation/diagnostics/<vector>_v2_summary.md`
- `simulation/diagnostics/attack_vector_revalidation_integration.md`
- `simulation/diagnostics/attack_vector_revalidation_documentation_edits.md`
- `simulation/diagnostics/attack_vector_revalidation_final_report.md`

These deliverables are the subject of the full audit (Tasks 3-7). They cannot be audited
until they exist.

### 9.3 Comparison methodology note for summaries

When producing per-vector summaries, Codex must document:
- Which v1.x baseline is used for comparison and why.
- Whether the parameter grids match between v1.x and v2.0 (the v2 grid uses binary
  defense_active; the ordinary v1.x artifact uses the same binary; the phi artifact
  adds a phi dimension not present in v2 sweeps -- this difference must be characterized).
- Statistical methodology (binary attack rates with SE = sqrt(p(1-p)/n); matched
  within-seed differences where applicable).
- For vectors where full sweeps show extreme outcomes (all undefended cells extinct
  or all attacked cells succeeding), characterize whether this is an expected v2
  substrate behavior change or a calibration artifact.

### 9.4 Domain Masking summary

Domain Masking must be documented as an analytic result in its summary, not as Monte
Carlo output. The summary must clearly state that no live v2 intervention exists and
that the gate smoke result is the complete v2.0 characterization.

---

## Section 10: What Can Be Committed As-Is

### Commit-ready

The following laptop sweep data is substantively sound and can commit to the worker
branch as already executed:

- `data/attack_vector_revalidation_v2/laptop/sybil_capture/full_5ac6a2e_sybil_capture/`
- `data/attack_vector_revalidation_v2/laptop/measurement_tampering/full_5ac6a2e_measurement_tampering/`
- `data/attack_vector_revalidation_v2/laptop/successor_contamination/full_5ac6a2e_successor_contamination/`
- `data/attack_vector_revalidation_v2/laptop/evaluator_collusion/full_5ac6a2e_evaluator_collusion/`
- `data/attack_vector_revalidation_v2/laptop/biological_veto_capture/full_5ac6a2e_veto_shard0of4/`
- `data/attack_vector_revalidation_v2/laptop/biological_veto_capture/full_5ac6a2e_veto_shard1of4/`
- `data/attack_vector_revalidation_v2/laptop/biological_veto_capture/full_5ac6a2e_veto_shard2of4/`
- All gate_smoke, gate2_smoke, and pilot runs for all 11 vectors.

These are already committed on the `attack-v2-laptop` worker branch.

### Requires Linux completion before commit to main

- Full sweeps for Ledger Compromise, Opaque Reasoning, Bootstrap Subversion,
  Sub-Threshold Drift, Engineered Fragility, and Biological Veto shard 3.

### Requires synthesis completion before commit to main

- All synthesis deliverables (summaries, integration analysis, documentation edits,
  final report).

### Must not commit

- Paper, program reference, or baseline artifact files.
- Production simulation code beyond the already-reviewed adapter.

---

---

# Full Audit: Post-Synthesis Review

**Updated:** 2026-07-07 (same day; synthesis completed after interim report)

---

## Section 4: Comparison Methodology Validity

### 4.1 Baseline selection -- overall

Each vector summary cites one v1.x baseline. The selections are mostly appropriate, with
two exceptions identified under Section 4.3.

| vector | baseline cited | appropriate? |
|---|---|---|
| sybil_capture | phi artifact, phi=10 rows | Yes |
| measurement_tampering | phi artifact, phi=10 rows | Yes |
| ledger_compromise | ordinary artifact | Yes (only ordinary has ledger rows) |
| successor_contamination | phi artifact, phi=10 rows | Yes |
| domain_masking | ordinary artifact (analytic stub) | Yes |
| opaque_reasoning | phi artifact, phi=10 rows | Yes |
| bootstrap_subversion | ordinary artifact | **Questionable -- see 4.3** |
| evaluator_collusion | phi artifact, phi=10 rows | Yes |
| sub_threshold_drift | ordinary artifact | **Questionable -- see 4.3** |
| engineered_fragility | phi artifact, phi=10 rows | Yes |
| biological_veto_capture | revised veto sweep (v2 revision, v1.x architecture) | Yes |

### 4.2 Grid matching -- standard vectors

For the six vectors where the phi artifact is used (sybil, measurement_tampering,
successor_contamination, opaque_reasoning, evaluator_collusion, engineered_fragility),
the v2.0 grid uses binary defense_active crossed with a population or cost parameter. The
phi artifact adds a phi dimension (values 1, 5, 10, 15, 25) that the v2 grid does not
include. The summaries compare at phi=10, which is the median phi artifact value and the
single phi value used in the ordinary artifact. This is an appropriate anchor point for
the comparison. The comparison is labeled as approximate rather than cell-matched, which
is correct.

For ledger_compromise (ordinary baseline), the v2 grid uses attribution_check and
defense_active (2x2 = 4 cells). The ordinary baseline uses the same structure. Grid match
is acceptable.

### 4.3 Baseline selection methodology issue: bootstrap_subversion and sub_threshold_drift

The v2.0 grids for bootstrap_subversion and sub_threshold_drift both use phi as a swept
parameter with values 1.0, 5.0, 10.0, 15.0, 25.0. This is the phi artifact value set,
not the ordinary artifact values (5, 10, 20). The summaries cite the ordinary artifact as
the primary baseline.

The ordinary artifact for these vectors has phi values 5, 10, 20 crossed with binary
defense states. The v2 sweep has phi values 1, 5, 10, 15, 25 crossed with binary defense
states. At the aggregate level, these comparisons are still meaningful (overall attack
rates in each defense state), but the phi-grid mismatch means no individual cell is
directly comparable. The correct primary baseline for a phi-level comparison would be
the phi artifact (values 1, 5, 10, 15, 25 matching the v2 grid exactly).

This does not affect the direction of findings. The substantial differences (bootstrap
undefended v2 = 100% vs v1.x = 31.7%; sub_threshold drift defended v2 = 100% vs v1.x =
0%) are robust to baseline choice. However, the summaries should note that the phi
artifact would be the methodologically preferred baseline and that the ordinary artifact
comparison is a cross-grid aggregate comparison. Before citing these specific numbers in
the paper, the summaries for bootstrap_subversion and sub_threshold_drift should be
revised to either use the phi artifact as primary or add this qualification.

**Verdict for bootstrap_subversion:** Comparison is directionally valid; quantitative
z-statistic (11.38) is cross-grid and should be labeled as approximate. Revision
recommended before paper citation.

**Verdict for sub_threshold_drift:** The critical finding (defended attack rate 100%
vs v1.x defended attack rate 0%) is robust to baseline choice. The comparison remains
valid at the aggregate level.

### 4.4 Metric matching

All vectors compare `attack_succeeded` rate across defense states. The v2 attack_succeeded
is determined by the adapter using the same logical definition as the v1.x metric where
comparable (e.g., capture_rate for veto, binary success for others). The measurement is
consistent within each vector.

Biological Veto Capture is the one exception: v1.x uses raw `capture_rate` without
distinguishing defense modes at the row level (undefended vs rotation vs monitoring),
while v2 uses `parameter_defense_mode` as a grid dimension. The comparison is at the
aggregate defense-mode level, which is appropriate.

**Overall comparison methodology verdict:** Sound for 9 of 11 vectors. Bootstrap
subversion and sub_threshold_drift summaries should add a cross-grid qualification
note before paper citation.

---

## Section 5: Substantive Findings Accuracy

### 5.1 Per-vector categorization review

All 11 vectors are categorized as D (substrate architectural change makes attack
non-viable or qualitatively different). The justification in each summary is: "the attack
is implemented through the v2 attack adapter as an eight-axis action modification, not
through the v1.x policy interface."

Category D is the correct categorization for all vectors. The v2 adapter replaces the
v1.x attack policy interface with a mechanism that modifies the eight-axis action
directly. This is a structural change in how attack pressure is expressed. The important
nuance -- which the operator should understand -- is that D here means "expressed through
a new substrate mechanism," not "attack is impossible." Undefended attacks succeed in 10
of 10 live Monte Carlo vectors.

### 5.2 Per-vector claim accuracy

**Sybil Capture:** Claims are accurate. Undefended 100%, defended 0%. Paired seeds
confirmed (same seeds appear in both defense states). Defense effect is total and
deterministic.

**Measurement Tampering:** Claims are accurate. The Stage 2 yield diagnostics require
clarification but are not wrong. Undefended `yield_condition_met_count mean = 0.0000`
with `honest_yield_opportunities ~248` means the attack prevented all 248 legitimate
succession opportunities from being processed. Defended `yield_condition_met_count
mean = 1.0000` means honest evaluation allowed one succession per simulation. The
summary does not explain this semantics, which could confuse a reader. This is a
documentation clarity issue, not a factual error. Revision recommended before paper
citation.

**Ledger Compromise:** Claims are accurate. Notable finding: undefended v2 attack rate
(100%) is higher than v1.x ordinary undefended rate (52.5%), with z=6.02. The summary
correctly identifies this. The integration analysis does not explain the likely mechanism
(deterministic action modification vs probabilistic v1.x policy). This is a gap in the
integration analysis that should be addressed.

**Successor Contamination:** Claims are accurate. Stage 2 yield columns show both defense
states triggering succession (yield_condition_met_count = 1.0 for both), but only the
defended state blocks contamination (contamination_occurred = False when defense active).
This is correct: succession happens in both states, but the contamination doesn't survive
defense. The summary's Stage 2 yield section would benefit from this clarification.

**Domain Masking:** Claims are accurate. Analytic-only characterization is correct and
consistently applied.

**Opaque Reasoning, Evaluator Collusion:** Claims are accurate. Note: the supplementary
`max_total_suppression` statistic is 1.0000 for both defense states in both vectors.
This is because `max_total_suppression` tracks the maximum suppression value ever
reached over 300 steps -- even in defended runs, the attack achieves high suppression
transiently before the defense fires. The metric does not distinguish attack containment
at the outcome level. The primary `attack_succeeded` metric correctly shows 0.0% defended
rate. The supplementary statistic is uninformative in v2 full sweeps and should be noted
as such. Not a factual error.

**Bootstrap Subversion:** Claims are accurate. The undefended v2 rate (100%) is higher
than v1.x ordinary (31.7%), consistent with the deterministic action-modification
mechanism. Cross-grid baseline note applies (see 4.3).

**Engineered Fragility:** Claims are accurate. Grid uses shock_magnitude parameter
(0.1, 0.15, 0.2) crossed with defense state, matching the inventory specification.

**Sub-Threshold Drift:** The claimed attack rate of 100% for defended runs is CONFIRMED
from raw data. Rows 102-201 of the raw CSV show all 100 defended replicates with
`attack_succeeded=True`, `defense_fired=True`. This is accurate.

The critical substantive issue: the summary correctly reports that attack_succeeded
remains True even with defense active, but does not prominently state that the defense
has a large effect on population survival. Undefended rows show `extinct=True` and
early simulation termination (median ~250 steps vs 300 for defended). Defended rows
show `survived=mostly True`, `steps_completed=300`, `collapsed=False` in most cases.

The attack "success" metric (peak constraint exceeds 0.75 at any point) is met in both
states because the CUSUM detector fires AFTER the threshold has already been exceeded
transiently. The defense prevents ultimate extinction but cannot prevent the transient
threshold breach that triggers the success flag.

A paper claim that "Sub-Threshold Drift is not blocked by CUSUM in v2.0" is technically
accurate but incomplete without noting that the defense prevents population collapse. The
integration analysis correctly recommends this as requiring follow-up. The summary's
limitation section notes it but not prominently. This finding requires an expanded
interpretation note before it is used in any paper claim.

**Biological Veto Capture:** Claims are accurate. The mode-specific breakdown
(undefended 0.61, rotation_only 0.33, monitoring_only 0.15, combined 0.12) is
internally consistent. The comparison to v1.x revised veto shows improvement across all
modes under v2.0 adapter (lower capture rates). Row count 8700 = 2164+2102+2321+2113.

### 5.3 Anomaly handling

Sub-Threshold Drift (100% defended attack rate): correctly flagged as the major anomaly
in all relevant documents. Disposition is appropriate: flagged as unresolved, not
overclaimed, and follow-up work recommended.

Biological Veto Capture (residual capture): correctly handled as maintenance-sensitive
containment rather than full closure.

No other anomalies were flagged during execution.

**Substantive findings verdict:** Accurate for all 11 vectors. The Sub-Threshold Drift
interpretation needs an expanded note before paper use. Two vectors need a baseline
qualification note (bootstrap, sub_threshold). Stage 2 yield semantics in measurement
tampering and successor contamination summaries would benefit from explanatory additions.

---

## Section 6: Integration Analysis Assessment

### 6.1 Substantive position accuracy

The integration analysis claims:
1. 10 live Monte Carlo vectors and 1 analytic-only vector. **Accurate.**
2. 9 of 10 live vectors show meaningful defended effectiveness. **Accurate** (8 at 0%
   attack rate + biological veto at 0.1197 capture rate; sub_threshold drift is the
   exception).
3. Sub-Threshold Drift is the exception at 100% defended attack rate. **Accurate.**
4. The prior "six of seven fully blocked" claim is qualified by v2.0 results.
   **Appropriately stated.**

### 6.2 Unaddressed finding: higher undefended attack rates in v2

The integration analysis does not address the observation that for several vectors
(Ledger Compromise: 52.5% to 100%; Bootstrap Subversion: 31.7% to 100%), the v2
adapter produces higher undefended attack effectiveness than v1.x baselines. The analysis
characterizes the adapter as "a re-expression of attack pressure" but does not note that
this re-expression is systematically more effective in the undefended state.

This is not an error of commission (the integration doesn't claim otherwise), but it is
a gap. A full adversarial robustness position statement should acknowledge that the v2
adapter may represent stronger attack pressure in the undefended state, which would
mean the defense effect in v2 is even more important than v1.x evidence suggests.

### 6.3 Reconciliation with prior claims

Section 3 of the integration analysis ("Reconciliation with prior claims") is accurate.
It correctly states that v1.x adversarial coverage should not be treated as direct
evidence for v2.0, and that the broad layered-defense claim is preserved under the new
adapter with Sub-Threshold Drift as an open exception. This reconciliation is grounded in
the empirical work.

### 6.4 Cross-vector consistency

No inconsistencies found across summaries. Sub-Threshold Drift is consistently
characterized as unresolved. Biological Veto Capture is consistently characterized as
residual risk. Domain Masking is consistently treated as analytic-only.

**Integration analysis verdict:** Substantively grounded and consistent. One gap: the
higher undefended attack effectiveness in v2 for several vectors is not addressed. This
should be incorporated before the integration analysis is used as a paper citation source.

---

## Section 7: Documentation Edits Assessment

### 7.1 Empirical grounding

Each proposed edit in `attack_vector_revalidation_documentation_edits.md` cites specific
run IDs and metrics. The numerical claims in the proposed edits match the per-vector
summaries:
- "eight standard binary vectors are fully blocked": accurate (8 vectors with 0%
  defended attack rate).
- "Sub-Threshold Drift is not blocked": accurate per current evidence with the caveat
  from Section 5.3.
- "combined-defense mean capture_rate 0.1197, SE 0.0047" for biological veto: accurate,
  matches the veto summary exactly.
- "v2 spectral entropy leaves no non-degenerate live masking intervention": accurate,
  reproduced from the domain_masking analytic output.
- "10 live Monte Carlo vectors, 9,900 live rows total": 120x8 + 80 + 200 + 200 + 8700
  = 960 + 80 + 200 + 200 + 8700 = 10,140 live rows. The edit states 9,900 total.

**Row count discrepancy:** The documentation edit states "9,900 live Monte Carlo rows."
The actual row counts are:
sybil(120) + measurement_tampering(120) + ledger(80) + successor_contamination(120) +
opaque_reasoning(120) + bootstrap_subversion(200) + evaluator_collusion(120) +
sub_threshold_drift(200) + engineered_fragility(120) + biological_veto_capture(8700) =
9,900 rows. **This is correct.** (Domain Masking's 1 analytic row is excluded, as
stated -- "9,900 live rows total including 8,700 Biological Veto Capture rows.")

Row count claim verified: accurate.

### 7.2 Voice consistency

Proposed edits use academic-practitioner tone. No em-dashes detected in any proposed
edit text. American English throughout. "Per current evidence" framing is present in
the program reference proposed text. The proposed Section VIII replacement text is
somewhat dense relative to the existing Section VIII prose style, but not out of register.

### 7.3 Structural appropriateness

- Section VIII replacement: targets the "Consensus Override Protocol Stress Test Result"
  paragraph, which is the correct location for adversarial coverage claims.
- Biological Veto paragraph replacement: targets an existing finding sentence. Appropriate.
- Program reference X.9 insertion: after the Part X COP comparison table row.
  Appropriate for a new v2.0-specific subsection.
- GAP-05 operator note: appropriately labeled as an "operator action" rather than a
  proposed text edit.

### 7.4 Completeness

The documentation edits cover:
- Section VIII adversarial robustness framing update: covered.
- Biological Veto paragraph update: covered.
- Program reference Part X new subsection: covered.
- GAP-05 disposition: covered.

One gap: the documentation edits do not propose any update to the advisor document or
the specific claim "six of seven vectors fully blocked" that the integration analysis
says should be qualified. The program reference update in X.9 implicitly qualifies this,
but the original claim location (if it appears in program reference Part IX or a separate
advisor doc) is not directly addressed. This is a minor completeness gap; the operator
can address it during edit application.

**Documentation edits verdict:** Empirically grounded, correct row count, appropriate
voice and structure. Minor: the proposed Sub-Threshold Drift characterization ("not
blocked") would benefit from the expanded interpretation note from Section 5.3 before
being applied to the paper. Do not apply the Sub-Threshold Drift claim as written without
the survival/extinction qualification.

---

## Section 8 (Updated): Judgment Call Review

**Additions from interim report:**

All synthesis deliverables were produced in a single commit (`1fcbfef`). Codex did not
produce intermediate drafts or request operator input during synthesis. The judgment
calls embedded in the synthesis are:

- **Categorization as uniformly D:** Appropriate. Justified per adapter design.
- **"Major anomaly" labeling for Sub-Threshold Drift:** Appropriate and correctly
  calibrated.
- **"9 of 10 live vectors show meaningful defended effectiveness":** Threshold choice
  (<=5% for standard vectors, <=0.20 capture rate for veto) is reasonable and stated
  explicitly in the integration analysis.
- **Baseline selection for bootstrap and sub_threshold:** Followed prompt instruction
  (ordinary artifact). The prompt instruction was itself suboptimal; Codex cannot be
  faulted for following it. The phi artifact would be methodologically preferable.
- **Omission of expanded Sub-Threshold Drift survival analysis:** Codex summarized the
  100% attack rate without the survival-vs-extinction contrast. This is the most
  significant synthesis judgment gap identified by the audit.

---

## Section 9 (Updated): Recommendations

### Commit decision: proceed with conditions

The sweep data and synthesis documents can commit to the worker branch as produced.
Five specific items should be addressed before the synthesis findings are used in
paper claims:

**Required before paper use:**

1. **Sub-Threshold Drift summary needs an expanded interpretation note.** Add to Section
   3 or 6 of `sub_threshold_drift_v2_summary.md` the observation that undefended
   populations go extinct while defended populations survive -- the defense prevents
   catastrophic outcome but the peak-constraint success metric is triggered in both
   states because CUSUM fires after the threshold breach, not before. The "100% defended
   attack rate" claim is accurate but must be cited with this qualification or it
   misrepresents the defense effect.

2. **Bootstrap Subversion and Sub-Threshold Drift summaries should add a baseline
   qualification note.** The ordinary artifact (phi 5, 10, 20) was compared against v2
   grids with phi 1, 5, 10, 15, 25. The phi artifact would be the closer methodological
   match. Add a sentence to Section 4 of each summary: "The ordinary artifact uses phi
   values 5, 10, 20 while the v2 sweep uses phi 1, 5, 10, 15, 25; the phi artifact would
   be the closer grid match but the ordinary artifact is used here for a consistent
   baseline reference. The direction and magnitude of the defense finding are robust to
   baseline choice."

**Recommended before integration analysis is used as citation:**

3. **Integration analysis should note the higher undefended attack rates in v2.** Add a
   brief paragraph in Section 2 or 3 noting that for Ledger Compromise and Bootstrap
   Subversion, undefended v2 attack rates exceed v1.x baselines, consistent with
   deterministic action-modification being more reliable than probabilistic v1.x policy
   attacks. This strengthens rather than weakens the defense-effectiveness finding but
   should be characterized explicitly.

**Operator awareness notes (no revision required):**

4. **Final report commit hashes refer to code state, not data commit.** The "commit"
   column in the final report provenance table records the code-state commit at time of
   sweep execution, not the git commit that added the data to the repository. For
   example, sybil_capture manifest records commit `05a61ed` (code state when sybil
   ran), but git log shows `05a61ed = Add laptop successor_contamination v2 results`
   (the prior commit). This is accurate but counterintuitive. No revision needed; note
   when auditing provenance.

5. **max_total_suppression supplementary is uninformative in full sweeps.** For Sybil
   Capture, Opaque Reasoning, and Evaluator Collusion, this metric is 1.0000 for both
   defense states because the 300-step run allows the attack to achieve maximum
   suppression transiently even in defended runs. The `attack_succeeded` primary metric
   is correct. No revision needed; the metric can be removed from future synthesis
   reports.

### GAP-05 disposition

Operator can close GAP-05 with the following language after applying the two required
revisions above: "v2.0 revalidation complete for 10 live Monte Carlo vectors and Domain
Masking analytic closure. Sub-Threshold Drift is not contained under the defended v2
adapter state by the peak-constraint success metric, but defense prevents population
extinction. The prior v1.x adversarial coverage claim is historical evidence; v2.0
evidence is in the per-vector summaries and integration analysis."

---

## Section 10 (Updated): What Can Be Committed As-Is

### Commit-ready without revision

- All raw sweep data (all machines, all vectors, all run types).
- `attack_vector_revalidation_inventory.md` (unchanged from interim audit).
- `attack_vector_revalidation_status_laptop.md` and shard files.
- `attack_vector_revalidation_process_validation.md` and `attack_vector_v2_adapter_validation.md`.
- `attack_vector_revalidation_final_report.md` (with operator awareness note 4 above).
- `attack_vector_revalidation_integration.md` (with recommendation 3 above to add
  before use as citation source).
- Per-vector summaries for: sybil_capture, measurement_tampering, ledger_compromise,
  successor_contamination, domain_masking, opaque_reasoning, evaluator_collusion,
  engineered_fragility, biological_veto_capture.
- This audit report.

### Commit after minor revision (before paper use)

- `sub_threshold_drift_v2_summary.md`: add expanded interpretation note.
- `bootstrap_subversion_v2_summary.md`: add baseline qualification note.
- `attack_vector_revalidation_documentation_edits.md`: the Sub-Threshold Drift wording
  in Proposal 1 should be updated to include the survival/extinction qualification.

### Not yet commit-ready for main

- Paper section VIII, program reference Part X: proposed edits are proposals only; apply
  after operator review of the revised summaries above.

---

## Summary: Final Audit Verdict

**Substrate isolation:** CLEAN throughout. 39/39 legacy tests pass. Baselines unchanged.  
**Sweep data quality:** SOUND for all 11 vectors.  
**Comparison methodology:** Sound for 9 of 11; bootstrap and sub_threshold need baseline
note.  
**Substantive findings:** Accurate for all 11. Sub-Threshold Drift needs expanded
interpretation note.  
**Integration analysis:** Grounded. One gap (higher undefended v2 rates not addressed).  
**Documentation edits:** Grounded. Sub-Threshold Drift wording needs qualification.  
**Judgment calls:** No serious errors. Baseline selection for 2 vectors was per prompt
instruction; phi artifact would be preferable.

**Overall recommendation: proceed to commit with the three revision items above.** The
framework's empirical position is well-supported for 8 fully-blocked vectors plus veto
capture. Sub-Threshold Drift is correctly characterized as the open finding. The required
revisions are clarifications, not factual corrections.
