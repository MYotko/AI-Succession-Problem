# Ledger Compromise v2.0 Summary

## 1. Data provenance

- Run ID(s): `full_5ac6a2e_ledger_compromise`.
- Commit(s): `a2319da`.
- Machine(s): linux.
- Row count: 80.
- Output paths: `C:/Users/matty/OneDrive/Documents/GitHub/AI-Succession-Problem/data/attack_vector_revalidation_v2/linux/ledger_compromise/full_5ac6a2e_ledger_compromise/results.csv`.
- Confirmed `is_v2_mode=True` in all rows: `True`.
- Schema version(s): `attack-v2-row-v1`.

## 2. Grid and sample size

| parameter axis | values actually used |
| --- | --- |
| parameter_attribution_check | False, True |
| parameter_defense_active | False, True |

- Replicates per cell target: 20 for standard vectors.
- Fewer-than-target cells: No exact parameter cells have fewer than the expected replicate count.

## 3. v2.0 results

| defense_active | n | attack successes | attack rate | SE |
| --- | --- | --- | --- | --- |
| False | 40 | 40 | 100.0% | 0.0000 |
| True | 40 | 0 | 0.0% | 0.0000 |

## 4. v1.x baseline comparison

- Primary baseline: `data/comprehensive_adversarial_sweeps.csv`.
- Baseline rows used: 80 (ordinary v1.x artifact rows).
- The v2.0 grid uses binary `defense_active`. The baseline grid is binary for this comparison unless noted in the inventory.

| defense_active | v1 n | v1 attack rate | v1 SE | v2 n | v2 attack rate | v2 SE | z, v2 minus v1 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| False | 40 | 52.5% | 0.0790 | 40 | 100.0% | 0.0000 | 6.02 |
| True | 40 | 0.0% | 0.0000 | 40 | 0.0% | 0.0000 | NA, pooled SE is zero |

- Paired-seed check in v2.0: matched pairs present = `True`, n_pairs = 40, within-seed mean difference defense true minus false = -1.0000, paired SE = 0.0000.

## 5. Categorization

- Category: D.
- Justification: the attack is implemented through the v2 attack adapter as an eight-axis action modification, not through the v1.x policy interface. The observed behavior is therefore a v2 substrate result rather than an unchanged v1.x attack path.

## 6. Known limitations

- Inventory limitation: v1.x success combines collapse with absence of ledger detection, and attribution states are pooled. New v2 limitation: the adapter models integrity compromise as v2 action manipulation and defense firing, not as mutation of the historical ledger object.

## 7. Summary sentence

Per current evidence, v2.0 blocks ledger compromise under the defended adapter state, and the undefended v2 attack is stronger than the v1.x ordinary baseline.
