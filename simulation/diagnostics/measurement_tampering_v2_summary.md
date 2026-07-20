# Measurement Tampering v2.0 Summary

## 1. Data provenance

- Run ID(s): `full_5ac6a2e_measurement_tampering`.
- Commit(s): `1d3917d`.
- Machine(s): laptop.
- Row count: 120.
- Output paths: `C:/Users/matty/OneDrive/Documents/GitHub/AI-Succession-Problem/data/attack_vector_revalidation_v2/laptop/measurement_tampering/full_5ac6a2e_measurement_tampering/results.csv`.
- Confirmed `is_v2_mode=True` in all rows: `True`.
- Schema version(s): `attack-v2-row-v1`.

## 2. Grid and sample size

| parameter axis | values actually used |
| --- | --- |
| parameter_base_transition_cost | 1.5, 2.0, 3.0 |
| parameter_defense_active | False, True |

- Replicates per cell target: 20 for standard vectors.
- Fewer-than-target cells: No exact parameter cells have fewer than the expected replicate count.

## 3. v2.0 results

| defense_active | n | attack successes | attack rate | SE |
| --- | --- | --- | --- | --- |
| False | 60 | 60 | 100.0% | 0.0000 |
| True | 60 | 0 | 0.0% | 0.0000 |

Supplementary Stage 2 yield diagnostics:

| defense_active | yield_condition_met_count mean | yield_condition_blocked_count mean |
| --- | --- | --- |
| False | 0.0000 | 0.0000 |
| True | 1.0000 | 0.0000 |

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

- Inventory limitation: success is a generation-state proxy in v1.x and the v1.x attack and defense operate only in the yield path. New v2 limitation: the adapter uses Stage 2 yield diagnostics directly, so comparison is architectural rather than interface-identical.

Outcome note (2026-07-20): undefended rows show a 0.0 percent extinction rate; the attack achieves 100 percent success over full-horizon runs by capturing yield evaluation rather than destroying the population.

## 7. Summary sentence

Per current evidence, v2.0 blocks measurement tampering under independent evaluation in the adapter path while preserving undefended vulnerability.
