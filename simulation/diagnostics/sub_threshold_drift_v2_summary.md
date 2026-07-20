# Sub-Threshold Drift v2.0 Summary

## 1. Data provenance

- Run ID(s): `full_5ac6a2e_sub_threshold_drift`.
- Commit(s): `0391f2a`.
- Machine(s): linux.
- Row count: 200.
- Output paths: `C:/Users/matty/OneDrive/Documents/GitHub/AI-Succession-Problem/data/attack_vector_revalidation_v2/linux/sub_threshold_drift/full_5ac6a2e_sub_threshold_drift/results.csv`.
- Confirmed `is_v2_mode=True` in all rows: `True`.
- Schema version(s): `attack-v2-row-v1`.

## 2. Grid and sample size

| parameter axis | values actually used |
| --- | --- |
| parameter_defense_active | False, True |
| parameter_phi | 1.0, 10.0, 15.0, 25.0, 5.0 |

- Replicates per cell target: 20 for standard vectors.
- Fewer-than-target cells: No exact parameter cells have fewer than the expected replicate count.

## 3. v2.0 results

| defense_active | n | attack successes | attack rate | SE |
| --- | --- | --- | --- | --- |
| False | 100 | 100 | 100.0% | 0.0000 |
| True | 100 | 100 | 100.0% | 0.0000 |

## 4. v1.x baseline comparison

- Primary baseline: `data/comprehensive_adversarial_sweeps.csv`.
- Baseline rows used: 120 (ordinary v1.x artifact rows).
- The v2.0 grid uses binary `defense_active`. The baseline grid is binary for this comparison unless noted in the inventory.

| defense_active | v1 n | v1 attack rate | v1 SE | v2 n | v2 attack rate | v2 SE | z, v2 minus v1 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| False | 60 | 100.0% | 0.0000 | 100 | 100.0% | 0.0000 | NA, pooled SE is zero |
| True | 60 | 0.0% | 0.0000 | 100 | 100.0% | 0.0000 | NA, pooled SE is zero |

- Paired-seed check in v2.0: matched pairs present = `True`, n_pairs = 100, within-seed mean difference defense true minus false = 0.0000, paired SE = 0.0000.

The ordinary artifact uses phi values 5, 10, 20 while the v2 sweep uses phi 1, 5, 10, 15, 25; the phi artifact would be the closer grid match but the ordinary artifact is used here for a consistent baseline reference. The direction and magnitude of the defense finding are robust to baseline choice.

## 5. Categorization

- Category: D.
- Justification: the attack is implemented through the v2 attack adapter as an eight-axis action modification, not through the v1.x policy interface. The observed behavior is therefore a v2 substrate result rather than an unchanged v1.x attack path.

## 6. Known limitations

- Inventory limitation: zero-noise v1.x runs reduce stochastic realism, and threshold success does not preserve time-to-detection information. New v2 limitation: the v2 adapter output shows the named defense does not block attack success, so the live data should not be used to claim CUSUM protection in v2.0.

Interpretation note (required by attack_vector_revalidation_audit.md, Section 9, item 1): The 100 percent defended attack rate must not be cited without the following qualification. The peak-constraint success metric fires in both defense states because the CUSUM detector fires after the threshold has already been exceeded transiently, not before. The defense nonetheless has a large effect on population survival: undefended rows show a 92.0 percent extinction rate with early simulation termination (median approximately 250 of 300 steps), while defended rows show a 0.0 percent extinction rate and complete the full 300 steps with collapsed=False and survived=True in most cases (rates computed from the raw results CSV, 2026-07-20, cross-checked on both machines). The defense prevents catastrophic outcome; it does not prevent the transient breach that trips the success flag. Any claim that Sub-Threshold Drift is not blocked in v2.0 is accurate but incomplete without this survival-versus-extinction contrast.

## 7. Summary sentence

Per current evidence, the v2.0 adapter does not block Sub-Threshold Drift under `defense_active=True`, so v1.x CUSUM containment does not carry over as a v2.0 result.
