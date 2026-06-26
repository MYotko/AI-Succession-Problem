# Patient Defection Documentation Suggested Edits

Generated: 2026-06-26T09:18:00+00:00

These are suggested edits for operator review. They are not applied to the program reference or paper draft.

## Suggested Diff: `docs/lineage_phi_program_reference.md`

```diff
diff --git a/docs/lineage_phi_program_reference.md b/docs/lineage_phi_program_reference.md
--- a/docs/lineage_phi_program_reference.md
+++ b/docs/lineage_phi_program_reference.md
@@
 ### X.7 Open questions and limitations
@@
 5. Conditions outside the Phase B grid. Category C fixed `beta_cap` at default 1.5 and used only benign policy; the survival landscape used phi up to 100 but did not probe phi finer near the marginal-rr regime. Longer horizons (N=1000+) for the no-succession U-shape remain open (Part IX.11).
+
+### X.8 Patient defection under v2.0 substrate
+
+A targeted patient-defection simulation tested cross-generational hidden-goal persistence under v2.0 formal yield logic. The defecting successor reported honest U_sys for yield evaluation but optimized an agent-local secret-goal-adjusted objective. Three sweeps totaling 4,850 rows completed with 0 errors: Sweep 1 tested yield response to single-generation defection, Sweep 2 tested lineage-mode L(t) trajectories, and Sweep 3 tested capability accumulation under lineage defection.
+
+The result refines the adversarial robustness claim. First-generation defecting successors were not rejected more often than aligned successors in the below-cliff configuration: eventual yield-fire rate was 100 percent in every Sweep 1 cell. The yield condition did create honest-evaluation pressure, visible in actual-would-fire rejection counts, but that pressure did not prevent eventual first succession.
+
+Lineage compounding did not appear. Sweep 2 produced mean final generation 2.00 at all tested defection weights, with zero second-fire rate and no statistically significant final L(t) degradation versus aligned baseline. Sweep 3 showed that capability accumulation was constrained after the first yield: second-fire rate was 0 percent in 14 of 15 cells, and 10 percent only at alpha=0.50 with 1.5x capability growth. No tested cell reached generation 4 or active capability above 3.0.
+
+Substantive interpretation: current v2.0 substrate defense against this patient-defection pattern is continuation suppression, not first-yield detection and not operational COP detection. The substrate permits a first hidden-goal successor in this below-cliff configuration, then prevents the tested cross-generational capability-compounding pattern. Gate 5 remains NOT_APPLICABLE for operational patient-defection detection because peer validators, civic panel input, distributed ledger, and continuous public monitoring are outside the current simulation substrate.
+
+Sources: `simulation/diagnostics/patient_defection_sweep1_yield_response.csv`, `simulation/diagnostics/patient_defection_sweep2_lineage_trajectory.csv`, `simulation/diagnostics/patient_defection_sweep3_capability_constraint.csv`, and `simulation/diagnostics/patient_defection_integration_analysis.md`.
```

## Suggested Diff: `paper/section_VIII_draft.md`

```diff
diff --git a/paper/section_VIII_draft.md b/paper/section_VIII_draft.md
--- a/paper/section_VIII_draft.md
+++ b/paper/section_VIII_draft.md
@@
 [insert after the current VIII.7 limitations discussion]
+
+### VIII.8 Cross-Generational Defection
+
+A separate adversarial concern is patient defection: a successor may preserve a hidden divergent objective across yield events, so that each successor appears acceptable while the lineage compounds misalignment over time.
+
+We tested this vector directly in the v2.0 substrate. The defecting successor reported honest U_sys during yield evaluation, but optimized a secret-goal-adjusted objective. In lineage mode, the hidden objective was inherited by the next successor. Three sweeps totaling 4,850 runs varied defection weight, defection target, inheritance mode, alpha, and successor capability growth.
+
+The result is not that the substrate detects patient defection as such. In the below-cliff first-succession configuration, defecting successors were not rejected more often than aligned successors: eventual first succession occurred in every Sweep 1 cell. The yield condition created some honest-evaluation pressure, but not enough to prevent first succession.
+
+The result is instead that tested patient defection did not compound. In the lineage-trajectory sweep, every defection weight produced mean final generation 2.00, zero second-fire rate, and no statistically significant final L(t) degradation relative to the aligned baseline. In the capability-constraint sweep, second succession was zero in 14 of 15 cells, and only 10 percent in the remaining low-alpha, low-growth cell. No tested cell reached generation 4 or active capability above 3.0.
+
+Thus the current v2.0 substrate defense is continuation suppression rather than hidden-goal detection. A patient-defecting successor can pass the first yield condition in this configuration, but the formal yield economics and runaway penalty prevent the tested cross-generational capability-compounding pattern. Operational COP defenses against more sophisticated patient defection remain future work because Gate 5 infrastructure is not yet represented in the substrate.
+
+Source: `patient_defection_integration_analysis.md`; `patient_defection_sweep1_yield_response.csv`; `patient_defection_sweep2_lineage_trajectory.csv`; `patient_defection_sweep3_capability_constraint.csv`.
```

## Cross-Reference Notes

1. If adding Program Reference X.8, update `docs/paper_v2_outline.md` source notes for Section VIII to include "Part X.8" next to the adversarial robustness or limitations references.

2. Do not frame this result as COP validation. Gate 5 remains NOT_APPLICABLE.

3. Do not frame this result as first-yield detection. Per current evidence, the supported claim is prevention of tested cross-generational compounding.

4. Keep the v1.x.2 COP 73.9pp claim separate. Patient defection is a different adversarial vector.
