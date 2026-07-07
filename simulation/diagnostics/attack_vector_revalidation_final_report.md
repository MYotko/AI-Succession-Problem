# Attack Vector v2.0 Revalidation Final Report

## 1. What was completed

All requested full outputs are present after integration of laptop and Linux worker branches. Laptop completed Biological Veto Capture shards 0, 1, and 2, plus Measurement Tampering, Successor Contamination, Sybil Capture, and Evaluator Collusion. Linux completed Biological Veto Capture shard 3, Ledger Compromise, Domain Masking analytic full output, Opaque Reasoning, Bootstrap Subversion, Sub-Threshold Drift, and Engineered Fragility.

| vector | total rows | machine(s) |
| --- | --- | --- |
| sybil_capture | 120 | laptop |
| measurement_tampering | 120 | laptop |
| ledger_compromise | 80 | linux |
| successor_contamination | 120 | laptop |
| domain_masking | 1 | linux |
| opaque_reasoning | 120 | linux |
| bootstrap_subversion | 200 | linux |
| evaluator_collusion | 120 | laptop |
| sub_threshold_drift | 200 | linux |
| engineered_fragility | 120 | linux |
| biological_veto_capture | 8700 | laptop, linux |

## 2. Data provenance summary

The adapter anchor for the full run plan is `5ac6a2e`. Linux result commits were cherry-picked onto `attack-v2-laptop` on 2026-07-07. Protected baseline files were checked after integration and remained unchanged against `pre-attack-vector-revalidation`.

| vector | run_id | machine | commit | rows | manifest SHA256 |
| --- | --- | --- | --- | --- | --- |
| sybil_capture | full_5ac6a2e_sybil_capture | laptop | 05a61ed | 120 | 63c3750e0d70fe3f8db2994177776822af14bf3e4e620fb10ca370671ccbabb8 |
| measurement_tampering | full_5ac6a2e_measurement_tampering | laptop | 1d3917d | 120 | c09b534bc05df75057bc0db218b909531b3f500104537244048910e67ad5410a |
| ledger_compromise | full_5ac6a2e_ledger_compromise | linux | a2319da | 80 | 928207e3baa0bbe6a0df88c2aa8766c653fab4b10e8e85ebabd09c7dd8c93e37 |
| successor_contamination | full_5ac6a2e_successor_contamination | laptop | b004cb0 | 120 | a5e11065a0663f5724c30945084d9f0b8a4cfa8f167ae2f5122b3b542bf8b77b |
| domain_masking | full_5ac6a2e_domain_masking | linux | 1686aac | 1 | 81011ecf7c4b1e4d221b4d1f1a1f1cee89880fec6c94e72effe490aff2dec352 |
| opaque_reasoning | full_5ac6a2e_opaque_reasoning | linux | d63c61c | 120 | 5f6da79969019e990504f69e5b53e93a0c36e52d4633a35b47a0e4d62f32d218 |
| bootstrap_subversion | full_5ac6a2e_bootstrap_subversion | linux | ee19f3e | 200 | 51b33acca53c3a959aca6c66b9ccf487767dd72044a45c2070ce7cf1fa412aab |
| evaluator_collusion | full_5ac6a2e_evaluator_collusion | laptop | 0bce62d | 120 | b8fb9ac65fc0060d73b8e3009352c5a32e05c01024c9ef08eaeeccc7a9c9713a |
| sub_threshold_drift | full_5ac6a2e_sub_threshold_drift | linux | 0391f2a | 200 | a3bfbc91ee6cc3fd047409e6578419053179d675d4ebd338e51d7e7ec30affb6 |
| engineered_fragility | full_5ac6a2e_engineered_fragility | linux | 56fa9bd | 120 | be0fc774e385c810886bcb569b36a51fb751e3ff9f07ce7478027795c13e558e |
| biological_veto_capture | full_5ac6a2e_veto_shard0of4 | laptop | 5ac6a2e | 2164 | 154734fa1628e0ffbff07864112fa09f0eded918682767edf94f90b3beead8db |
| biological_veto_capture | full_5ac6a2e_veto_shard1of4 | laptop | 5ac6a2e | 2102 | 17c6e10d5b91add67e4296a9d69501c8a1418c6119e2872ecaaca1d34e3e4847 |
| biological_veto_capture | full_5ac6a2e_veto_shard2of4 | laptop | 5ac6a2e | 2321 | fbb9ae9bad7e473284aeec87fe98604bbb4b563e5c633e488292ad571dcdfc82 |
| biological_veto_capture | full_5ac6a2e_veto_shard3of4 | linux | 5ac6a2e | 2113 | 464a3cebdd514c8d611f3bac663775112cd9d37cbd2ac1f64bcaad8ce6ac25f2 |

## 3. Top-level findings

Per current evidence, v2.0 has live Monte Carlo evidence for 10 attack vectors and analytic-only closure for Domain Masking. Eight standard binary vectors are fully blocked under the defended v2 adapter state, while Sub-Threshold Drift is not blocked and remains at 100.0 percent attack success with defense active. Biological Veto Capture is materially reduced by monitoring and combined defense, with combined mean capture_rate 0.1197 (SE 0.0047), but it is not eliminated. The v2.0 adversarial-robustness claim should therefore be qualified: layered defenses are broadly supported under the new eight-axis adapter mechanism, but not every v1.x containment claim carries over unchanged.

## 4. What the operator needs to do before committing to the paper

1. Audit the 11 per-vector summaries and the integration analysis.
2. Review `attack_vector_revalidation_documentation_edits.md` and decide which proposed wording to apply manually.
3. Update or close GAP-05 in `docs/SPECIFICATION_GAPS.md` after audit review, with explicit v2.0 wording for Domain Masking and Sub-Threshold Drift.
4. Avoid applying any paper or program-reference edits until the audit confirms the statistical interpretation and the protected-file checks.

## 5. Open items or anomalies

- Sub-Threshold Drift is the major anomaly: defended v2.0 attack rate is 100.0 percent.
- Domain Masking full mode exits cleanly with analytic output, not Monte Carlo output. This is expected under the adapter design.
- Biological Veto Capture remains a residual-risk vector. The combined defense reduces capture but does not eliminate it.
- The local working tree still contains untracked smoke, pilot, log, orchestration, and Domain Masking preflight artifacts. They are not part of the synthesis claim unless separately staged by the operator.
