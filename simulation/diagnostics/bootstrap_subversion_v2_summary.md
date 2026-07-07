# Bootstrap Subversion v2.0 Summary

## 1. Data provenance

- Run ID(s): `full_5ac6a2e_bootstrap_subversion`.
- Commit(s): `ee19f3e`.
- Machine(s): linux.
- Row count: 200.
- Output paths: `C:/Users/matty/OneDrive/Documents/GitHub/AI-Succession-Problem/data/attack_vector_revalidation_v2/linux/bootstrap_subversion/full_5ac6a2e_bootstrap_subversion/results.csv`.
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
| True | 100 | 0 | 0.0% | 0.0000 |

## 4. v1.x baseline comparison

- Primary baseline: `data/comprehensive_adversarial_sweeps.csv`.
- Baseline rows used: 120 (ordinary v1.x artifact rows).
- The v2.0 grid uses binary `defense_active`. The baseline grid is binary for this comparison unless noted in the inventory.

| defense_active | v1 n | v1 attack rate | v1 SE | v2 n | v2 attack rate | v2 SE | z, v2 minus v1 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| False | 60 | 31.7% | 0.0601 | 100 | 100.0% | 0.0000 | 11.38 |
| True | 60 | 0.0% | 0.0000 | 100 | 0.0% | 0.0000 | NA, pooled SE is zero |

- Paired-seed check in v2.0: matched pairs present = `True`, n_pairs = 100, within-seed mean difference defense true minus false = -1.0000, paired SE = 0.0000.

## 5. Categorization

- Category: D.
- Justification: the attack is implemented through the v2 attack adapter as an eight-axis action modification, not through the v1.x policy interface. The observed behavior is therefore a v2 substrate result rather than an unchanged v1.x attack path.

## 6. Known limitations

- Inventory limitation: v1.x bootstrap verification uses the scalar `project_u_sys` interface and success does not require survival. New v2 limitation: the adapter emulates bootstrap attack pressure through v2 action construction, not through a full multi-candidate bootstrap institution.

## 7. Summary sentence

Per current evidence, v2.0 blocks bootstrap-subversion action perturbations under the defended adapter state, while undefended v2 attack pressure is stronger than the v1.x ordinary baseline.
