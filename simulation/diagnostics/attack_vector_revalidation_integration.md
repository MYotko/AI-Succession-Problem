# Attack Vector v2.0 Revalidation Integration Analysis

## 1. Completion inventory

| vector | run_id(s) | total rows | category | status |
| --- | --- | --- | --- | --- |
| sybil_capture | full_5ac6a2e_sybil_capture | 120 | D | completed |
| measurement_tampering | full_5ac6a2e_measurement_tampering | 120 | D | completed |
| ledger_compromise | full_5ac6a2e_ledger_compromise | 80 | D | completed |
| successor_contamination | full_5ac6a2e_successor_contamination | 120 | D | completed |
| domain_masking | full_5ac6a2e_domain_masking | 1 | D | completed |
| opaque_reasoning | full_5ac6a2e_opaque_reasoning | 120 | D | completed |
| bootstrap_subversion | full_5ac6a2e_bootstrap_subversion | 200 | D | completed |
| evaluator_collusion | full_5ac6a2e_evaluator_collusion | 120 | D | completed |
| sub_threshold_drift | full_5ac6a2e_sub_threshold_drift | 200 | D | completed |
| engineered_fragility | full_5ac6a2e_engineered_fragility | 120 | D | completed |
| biological_veto_capture | full_5ac6a2e_veto_shard0of4, full_5ac6a2e_veto_shard1of4, full_5ac6a2e_veto_shard2of4, full_5ac6a2e_veto_shard3of4 | 8700 | D | completed |

## 2. v2.0 adversarial robustness position

Ten vectors were tested with live Monte Carlo evidence. Domain Masking is analytic-only. Using a practical defense-effectiveness threshold of attack rate at or below 5 percent for binary attack metrics, and mean capture_rate at or below 0.20 for the combined Biological Veto Capture defense, 9 of 10 live vectors show meaningful defended effectiveness in v2.0. The exception is Sub-Threshold Drift, where `defense_active=True` still has attack rate 100.0 percent with SE 0.0000.

This differs from the v1.x characterization in two ways. First, the advisor-level claim that six of seven vectors were fully blocked was based on the older v1.x policy and COP wiring, not the v2 optimizer substrate. Second, `SPECIFICATION_GAPS.md` described 11 vectors simulated, but the authoritative inventory shows that Domain Masking was injected analytic output and the other baselines were v1.x or v1.x.2 evidence. The present revalidation provides v2.0 live evidence for 10 vectors and analytic v2.0 closure for Domain Masking.

The substantive substrate change is structural. The adapter replaces v1 attack tuples and v1 COP paths with explicit eight-axis v2 action modifications inside the v2 step path. This means the result is not a parameter shift within the old evidence base. It is a re-expression of attack pressure in the v2 action substrate, with formal Stage 2 yield logic active where relevant.

## 3. Reconciliation with prior claims

The broad claim that layered defenses are load-bearing is preserved per current evidence, but the exact prior claim that identified v1.x attack vectors are fully contained should be qualified. Eight standard binary vectors are fully blocked under the defended v2 adapter state, Biological Veto Capture is materially reduced but not eliminated, and Sub-Threshold Drift is not blocked in the v2 adapter data. Domain Masking remains structurally closed, but only as an analytic architectural result.

The documentation should therefore stop treating v1.x adversarial coverage as direct evidence for v2.0. It can state that v2.0 revalidation supports most of the earlier robustness position under a new adapter mechanism, while identifying Sub-Threshold Drift as unresolved and Biological Veto Capture as an institutional-maintenance risk.

## 4. Cross-vector consistency check

No per-vector summary claims that Sub-Threshold Drift is defended in v2.0. The integration position is consistent with the Sub-Threshold Drift summary: v1.x CUSUM containment does not carry over as a v2.0 result. Domain Masking is consistently treated as analytic-only, not as a Monte Carlo result. Biological Veto Capture is consistently treated as reduced rather than fully eliminated.

## 5. What remains unresolved

Sub-Threshold Drift requires follow-up before paper claims can state v2.0 containment. The current data show 100.0 percent attack success in both defense states. Biological Veto Capture requires careful wording because combined defense reduces mean capture_rate to 0.1197, SE 0.0047, but does not eliminate capture. Domain Masking is architecturally closed in the audited substrate, but no live masking intervention has been defined. Any future claim that all attack vectors are fully blocked would require additional adapter work and a rerun.
