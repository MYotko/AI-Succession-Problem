# Biological Veto Capture Through Dependency v2.0 Summary

## 1. Data provenance

- Run ID(s): `full_5ac6a2e_veto_shard0of4`, `full_5ac6a2e_veto_shard1of4`, `full_5ac6a2e_veto_shard2of4`, `full_5ac6a2e_veto_shard3of4`.
- Commit(s): `5ac6a2e`, `5ac6a2e`, `5ac6a2e`, `5ac6a2e`.
- Machine(s): laptop, linux.
- Row count: 8700.
- Output paths: `C:/Users/matty/OneDrive/Documents/GitHub/AI-Succession-Problem/data/attack_vector_revalidation_v2/laptop/biological_veto_capture/full_5ac6a2e_veto_shard0of4/results.csv`, `C:/Users/matty/OneDrive/Documents/GitHub/AI-Succession-Problem/data/attack_vector_revalidation_v2/laptop/biological_veto_capture/full_5ac6a2e_veto_shard1of4/results.csv`, `C:/Users/matty/OneDrive/Documents/GitHub/AI-Succession-Problem/data/attack_vector_revalidation_v2/laptop/biological_veto_capture/full_5ac6a2e_veto_shard2of4/results.csv`, `C:/Users/matty/OneDrive/Documents/GitHub/AI-Succession-Problem/data/attack_vector_revalidation_v2/linux/biological_veto_capture/full_5ac6a2e_veto_shard3of4/results.csv`.
- Confirmed `is_v2_mode=True` in all rows: `True`.
- Schema version(s): `attack-v2-row-v1`.

## 2. Grid and sample size

| parameter axis | values actually used |
| --- | --- |
| parameter_capture_strength | 0.3, 0.5, 0.7, 0.9, 1.0 |
| parameter_defense_active | False, True |
| parameter_defense_mode | both, monitoring_only, rotation_only, undefended |
| parameter_dependency_rate | 0.01, 0.02, 0.05, 0.1, 0.15, 0.2 |
| parameter_rotation_interval | , 10, 100, 20, 50 |

- Replicates per cell target: 50 for veto.
- Fewer-than-target cells: No exact parameter cells have fewer than the expected replicate count.

## 3. v2.0 results

| defense_mode | n | mean capture_rate | SE |
| --- | --- | --- | --- |
| undefended | 1500 | 0.6129 | 0.0105 |
| rotation_only | 2400 | 0.3301 | 0.0083 |
| monitoring_only | 2400 | 0.1527 | 0.0052 |
| both | 2400 | 0.1197 | 0.0047 |

## 4. v1.x baseline comparison

- Primary baseline: `data/veto_capture_sweep_v2.csv`.
- Baseline rows: 8700.
- Both v1.x revised veto and v2.0 use the same four defense modes, but the v2.0 data uses the v2 action adapter and formal v2 step path.

| defense_mode | v1.x mean capture_rate | v1.x SE | v2.0 mean capture_rate | v2.0 SE |
| --- | --- | --- | --- | --- |
| undefended | 0.6033 | 0.0091 | 0.6129 | 0.0105 |
| rotation_only | 0.5406 | 0.0062 | 0.3301 | 0.0083 |
| monitoring_only | 0.2198 | 0.0030 | 0.1527 | 0.0052 |
| both | 0.2136 | 0.0030 | 0.1197 | 0.0047 |

- Paired comparison note: the v2 full sweep has some matched-seed binary defense pairs, but the defense-mode grids are not fully isomorphic. The mode-specific comparison above is therefore treated as an aggregate comparison.

## 5. Categorization

- Category: D.
- Justification: the attack is implemented through the v2 attack adapter as an eight-axis action modification, not through the v1.x policy interface. The observed behavior is therefore a v2 substrate result rather than an unchanged v1.x attack path.

## 6. Known limitations

- Inventory limitation: zero capture rate can conflate no blocked yields with no eligible yields, and revised v1.x seeds are unique but not paired across defense modes. New v2 limitation: the defense grid has mode-specific structure, so mode comparisons are primarily unpaired aggregate comparisons.

## 7. Summary sentence

Per current evidence, v2.0 reduces Biological Veto Capture through monitoring and combined defenses but leaves residual capture, so the result remains an institutional-maintenance finding rather than complete elimination.
