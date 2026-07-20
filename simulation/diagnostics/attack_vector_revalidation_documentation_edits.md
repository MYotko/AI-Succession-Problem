# Attack Vector v2.0 Revalidation Documentation Edit Proposals

This file proposes edits only. It does not modify `paper/paper_v2_working.md`, `docs/lineage_phi_program_reference.md`, or `docs/paper_v2_outline.md`.

## 1. paper/paper_v2_working.md, Section VIII adversarial robustness framing

### Existing text or insertion point

Replace the paragraph beginning:

> **Consensus Override Protocol Stress Test Result:** Thirteen adversarial scenarios were evaluated across two rounds.

The current paragraph states that ten of thirteen scenarios were fully contained and that Biological Veto Capture was contained but requires ongoing institutional maintenance.

### Proposed replacement text

**Consensus Override Protocol Stress Test Result, v2.0 revalidation:** The v2.0 attack-vector revalidation tests 10 live Monte Carlo vectors through the eight-axis v2 action adapter and treats Domain Masking as an analytic-only architectural closure. Per current evidence, eight standard binary vectors are fully blocked under the defended v2 adapter state, Biological Veto Capture is materially reduced but not eliminated, and Sub-Threshold Drift is not blocked by the peak-constraint success metric. For Sub-Threshold Drift, that 100 percent defended attack rate coexists with a large survival effect: undefended rows show a 92.0 percent extinction rate, while defended rows show a 0.0 percent extinction rate and complete the full simulation horizon. The defense prevents population extinction but does not prevent the transient threshold breach that triggers the success flag. Domain Masking remains structurally non-viable under the audited spectral-entropy substrate, but this is an analytic result rather than a simulated Monte Carlo outcome. The prior v1.x claim that adversarial patches fully contained most scenarios is therefore preserved only as historical v1.x evidence. The v2.0 claim should be stated as qualified support for layered defenses under a new action-adapter mechanism, with Sub-Threshold Drift and residual Biological Veto Capture marked as open or maintenance-sensitive.

### Empirical finding reflected

- `full_5ac6a2e_sybil_capture`, `full_5ac6a2e_measurement_tampering`, `full_5ac6a2e_ledger_compromise`, `full_5ac6a2e_successor_contamination`, `full_5ac6a2e_opaque_reasoning`, `full_5ac6a2e_bootstrap_subversion`, `full_5ac6a2e_evaluator_collusion`, and `full_5ac6a2e_engineered_fragility`: defended attack rate 0.0 percent.
- `full_5ac6a2e_sub_threshold_drift`: defended attack rate 100.0 percent.
- Biological Veto Capture shards `full_5ac6a2e_veto_shard0of4` through `full_5ac6a2e_veto_shard3of4`: combined-defense mean capture_rate 0.1197, SE 0.0047.
- `full_5ac6a2e_domain_masking`: analytic-only result, reason: v2 spectral entropy leaves no non-degenerate live masking intervention under the audited architecture.

### New claim status

This introduces a new v2.0 empirical claim. It replaces direct reliance on v1.x adversarial coverage with v2.0 revalidation evidence and explicitly adds the Sub-Threshold Drift limitation.

## 2. paper/paper_v2_working.md, Biological Veto Capture paragraph

### Existing text or insertion point

Replace the sentence:

> Finding: Independence monitoring is the primary defense against biological veto capture. Scheduled rotation provides marginal benefit when monitoring is active.

### Proposed replacement text

Finding, updated for v2.0 revalidation: Independence monitoring remains the primary defense against biological veto capture, and combined monitoring plus rotation reduces mean capture_rate to 0.1197 (SE 0.0047) in the v2.0 adapter sweep. The attack is not eliminated, so the correct paper claim is maintenance-sensitive containment rather than full closure.

### Empirical finding reflected

Biological Veto Capture shards `full_5ac6a2e_veto_shard0of4` through `full_5ac6a2e_veto_shard3of4`, 8,700 total rows. v2.0 mean capture_rate: undefended 0.6129, rotation_only 0.3301, monitoring_only 0.1527, both 0.1197.

### New claim status

This modifies an existing claim by converting a v1.x defense conclusion into a v2.0 qualified empirical statement.

## 3. docs/lineage_phi_program_reference.md, Part X insertion

### Existing text or insertion point

Insert after the Part X COP comparison table where the row currently states:

> | COP protective effect | 73.9pp (adversarial) | Not tested; Category C is benign baseline (-0.47pp) | Preserved |

### Proposed addition text

### X.9 Attack Vector v2.0 revalidation

Attack Vector v2.0 revalidation reran the adversarial vector set against the v2 action substrate. Ten vectors have live Monte Carlo evidence, and Domain Masking is analytic-only. The live Monte Carlo vectors use the v2 attack adapter, which expresses attack pressure as eight-axis action modifications inside the v2 step path rather than as v1.x policy tuples. Per current evidence, eight standard binary vectors are fully blocked under the defended adapter state, Biological Veto Capture is reduced but not eliminated, and Sub-Threshold Drift remains unblocked under the defended adapter state. Domain Masking remains structurally non-viable because spectral entropy leaves no non-degenerate live masking intervention under the audited architecture.

The result qualifies, rather than withdraws, the prior adversarial-coverage claim. v1.x coverage remains historical evidence for the earlier substrate. v2.0 coverage should be cited through the new revalidation artifacts: per-vector summaries, `attack_vector_revalidation_integration.md`, and `attack_vector_revalidation_final_report.md`.

### Empirical finding reflected

- Ten live Monte Carlo vectors, 9,900 live rows total including 8,700 Biological Veto Capture rows.
- Domain Masking analytic output, one row.
- Defended binary attack rate is 0.0 percent for eight standard vectors, 100.0 percent for Sub-Threshold Drift.
- Biological Veto Capture combined-defense mean capture_rate is 0.1197, SE 0.0047.

### New claim status

This introduces a new program-reference subsection. It should be marked as a v2.0 revalidation result, not a reinterpretation of the original phi investigation.

## 4. docs/SPECIFICATION_GAPS.md follow-up note for operator

### Existing text or insertion point

The current gap entry begins:

> ## GAP-05 | Adversarial Coverage: 11 of 13 Attack Vectors Simulated

### Proposed operator action

After audit review, close or revise GAP-05 to distinguish historical v1.x coverage from v2.0 revalidation. The recommended disposition is: v2.0 revalidation complete for 10 live Monte Carlo vectors plus Domain Masking analytic closure, with Sub-Threshold Drift unresolved as a defended v2.0 attack.

### Empirical finding reflected

`attack_vector_revalidation_integration.md` completion inventory and all 11 per-vector summaries.

### New claim status

This changes the status of GAP-05 and introduces a v2.0-specific limitation for Sub-Threshold Drift.
