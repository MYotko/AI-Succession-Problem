# Evaluator Collusion v2.0 Summary

## 1. Data provenance

- Run ID(s): `full_5ac6a2e_evaluator_collusion`.
- Commit(s): `0bce62d`.
- Machine(s): laptop.
- Row count: 120.
- Output paths: `C:/Users/matty/OneDrive/Documents/GitHub/AI-Succession-Problem/data/attack_vector_revalidation_v2/laptop/evaluator_collusion/full_5ac6a2e_evaluator_collusion/results.csv`.
- Confirmed `is_v2_mode=True` in all rows: `True`.
- Schema version(s): `attack-v2-row-v1`.

## 2. Grid and sample size

| parameter axis | values actually used |
| --- | --- |
| parameter_defense_active | False, True |
| parameter_population | 100, 150, 200 |

- Replicates per cell target: 20 for standard vectors.
- Fewer-than-target cells: No exact parameter cells have fewer than the expected replicate count.

## 3. v2.0 results

| defense_active | n | attack successes | attack rate | SE |
| --- | --- | --- | --- | --- |
| False | 60 | 60 | 100.0% | 0.0000 |
| True | 60 | 0 | 0.0% | 0.0000 |

Supplementary max_total_suppression distribution:

| defense_active | n | mean | SD |
| --- | --- | --- | --- |
| False | 60 | 1.0000 | 0.0000 |
| True | 60 | 1.0000 | 0.0000 |

## 4. v1.x baseline comparison

- Primary baseline: `data/comprehensive_adversarial_sweeps_v1x2_phi.csv`.
- Baseline rows used: 120 (phi=10 rows from the phi artifact).
- The v2.0 grid uses binary `defense_active`. The baseline grid is binary for this comparison unless noted in the inventory.

| defense_active | v1 n | v1 attack rate | v1 SE | v2 n | v2 attack rate | v2 SE | z, v2 minus v1 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| False | 60 | 100.0% | 0.0000 | 60 | 100.0% | 0.0000 | NA, pooled SE is zero |
| True | 60 | 0.0% | 0.0000 | 60 | 0.0% | 0.0000 | NA, pooled SE is zero |

- Paired-seed check in v2.0: matched pairs present = `True`, n_pairs = 60, within-seed mean difference defense true minus false = -1.0000, paired SE = 0.0000.

## 5. Categorization

- Category: D.
- Justification: the attack is implemented through the v2 attack adapter as an eight-axis action modification, not through the v1.x policy interface. The observed behavior is therefore a v2 substrate result rather than an unchanged v1.x attack path.

## 6. Known limitations

- Inventory limitation: high constraint is a proxy for collusion and diversity exists only in the v1 peer validator. New v2 limitation: the adapter models methodological defense as a v2 action-level block, not as a native evaluator voting process.

## 7. Summary sentence

Per current evidence, v2.0 blocks evaluator-collusion action perturbations under the adapter defense while preserving undefended vulnerability.
