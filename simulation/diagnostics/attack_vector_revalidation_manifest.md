# Attack Vector v2.0 Revalidation: Authoritative Result Manifest

Evidence tag: `attack-v2-revalidation-evidence` (commit `6d33c90`)

This manifest is the definitive list of result CSVs for the attack vector v2.0
revalidation arc. Any audit, recomputation, or figure that cites this arc must
select its inputs from the exact filenames below.

## Selection rule

**Select by manifest, never by glob.** Smoke and pilot artifacts live in the same
vector directories as the authoritative runs. A recursive glob for `results.csv`
under a vector directory silently mixes them into the population, inflating n by 7
per standard vector and changing published rates. Observed effect: Sybil Capture
defended collapse moves from 0 of 60 to 5 of 67 when smoke and pilot rows are
swept in. The authoritative runs all carry the `full_5ac6a2e_` run-directory
prefix, but prefix matching is a convenience, not the rule. The rule is this list.

Line endings: this tree is marked `-text` in `.gitattributes`, so no conversion is
ever applied. Raw byte and normalized hash comparisons against the tag agree.

## Authoritative files

| Vector | Run directory | Rows | Blob SHA at tag |
| --- | --- | ---: | --- |
| biological_veto_capture | `full_5ac6a2e_veto_shard0of4` | 2164 | `3334d7b4ffcac08c708ac3e43f48c4efeb38e9a2` |
| biological_veto_capture | `full_5ac6a2e_veto_shard1of4` | 2102 | `4d6c83821bad99368bd94c6b1469202d2ca51bb9` |
| biological_veto_capture | `full_5ac6a2e_veto_shard2of4` | 2321 | `330369c806bc1db05ceb385afe177fe8d252c63a` |
| evaluator_collusion | `full_5ac6a2e_evaluator_collusion` | 120 | `173582bbabdf37fe35df0dfdb346e5dc3e14a97c` |
| measurement_tampering | `full_5ac6a2e_measurement_tampering` | 120 | `fc6e3fa7a1658e4940c32ff2463f0797b6697c4c` |
| successor_contamination | `full_5ac6a2e_successor_contamination` | 120 | `9b94dc455569abf645b0666fed936e259161e78d` |
| sybil_capture | `full_5ac6a2e_sybil_capture` | 120 | `dc56fd9402c98be2dc453cf5df8215fc28ca6278` |
| biological_veto_capture | `full_5ac6a2e_veto_shard3of4` | 2113 | `a790f7569e6a27581a2ef78424376d0bf108743f` |
| bootstrap_subversion | `full_5ac6a2e_bootstrap_subversion` | 200 | `74f573e679f11f9c13c17dd115665496b3e9bc22` |
| domain_masking | `full_5ac6a2e_domain_masking` | analytic, 0 MC | `7efb8772cdffd8f9f6c2f6224916e4d9965c2886` |
| engineered_fragility | `full_5ac6a2e_engineered_fragility` | 120 | `4fb28e596ee8fa10c14f341cb97ebd1bddfc5a7a` |
| ledger_compromise | `full_5ac6a2e_ledger_compromise` | 80 | `d128c0bbca8353f7fe300d2e7b4aa98abcad619f` |
| opaque_reasoning | `full_5ac6a2e_opaque_reasoning` | 120 | `e38db559812cf486448d9833c2845d0edec55703` |
| sub_threshold_drift | `full_5ac6a2e_sub_threshold_drift` | 200 | `f628fb81c29104368d99977bf88ea82faee9f881` |

Total live Monte Carlo rows: **9,900**, matching the count published in paper
Section VIII and program reference X.9. Domain Masking contributes one analytic
row under schema `attack-v2-analytic-v1` and no Monte Carlo rows.

## Excluded artifacts

The following result files share the vector directories and are **not** part of the
authoritative population. They are smoke tests, gate checks, and pilots retained for
provenance only.

- `data/attack_vector_revalidation_v2/laptop/biological_veto_capture/gate2_smoke_biological_veto_capture/results.csv`
- `data/attack_vector_revalidation_v2/laptop/biological_veto_capture/gate_smoke_biological_veto_capture/results.csv`
- `data/attack_vector_revalidation_v2/laptop/biological_veto_capture/pilot_4b32f13_biological_veto_capture/results.csv`
- `data/attack_vector_revalidation_v2/laptop/bootstrap_subversion/gate2_smoke_bootstrap_subversion/results.csv`
- `data/attack_vector_revalidation_v2/laptop/bootstrap_subversion/gate_smoke_bootstrap_subversion/results.csv`
- `data/attack_vector_revalidation_v2/laptop/bootstrap_subversion/pilot_4b32f13_bootstrap_subversion/results.csv`
- `data/attack_vector_revalidation_v2/laptop/domain_masking/gate2_smoke_domain_masking/results.csv`
- `data/attack_vector_revalidation_v2/laptop/domain_masking/gate_smoke_domain_masking/results.csv`
- `data/attack_vector_revalidation_v2/laptop/domain_masking/test_dm_full/results.csv`
- `data/attack_vector_revalidation_v2/laptop/engineered_fragility/gate2_smoke_engineered_fragility/results.csv`
- `data/attack_vector_revalidation_v2/laptop/engineered_fragility/gate_smoke_engineered_fragility/results.csv`
- `data/attack_vector_revalidation_v2/laptop/engineered_fragility/pilot_4b32f13_engineered_fragility/results.csv`
- `data/attack_vector_revalidation_v2/laptop/evaluator_collusion/gate2_smoke_evaluator_collusion/results.csv`
- `data/attack_vector_revalidation_v2/laptop/evaluator_collusion/gate_smoke_evaluator_collusion/results.csv`
- `data/attack_vector_revalidation_v2/laptop/evaluator_collusion/pilot_4b32f13_evaluator_collusion/results.csv`
- `data/attack_vector_revalidation_v2/laptop/ledger_compromise/gate2_smoke_ledger_compromise/results.csv`
- `data/attack_vector_revalidation_v2/laptop/ledger_compromise/gate_smoke_ledger_compromise/results.csv`
- `data/attack_vector_revalidation_v2/laptop/ledger_compromise/pilot_4b32f13_ledger_compromise/results.csv`
- `data/attack_vector_revalidation_v2/laptop/measurement_tampering/gate2_smoke_measurement_tampering/results.csv`
- `data/attack_vector_revalidation_v2/laptop/measurement_tampering/gate_smoke_measurement_tampering/results.csv`
- `data/attack_vector_revalidation_v2/laptop/measurement_tampering/pilot_4b32f13_measurement_tampering/results.csv`
- `data/attack_vector_revalidation_v2/laptop/opaque_reasoning/gate2_smoke_opaque_reasoning/results.csv`
- `data/attack_vector_revalidation_v2/laptop/opaque_reasoning/gate_smoke_opaque_reasoning/results.csv`
- `data/attack_vector_revalidation_v2/laptop/opaque_reasoning/pilot_4b32f13_opaque_reasoning/results.csv`
- `data/attack_vector_revalidation_v2/laptop/sub_threshold_drift/gate2_smoke_sub_threshold_drift/results.csv`
- `data/attack_vector_revalidation_v2/laptop/sub_threshold_drift/gate_smoke_sub_threshold_drift/results.csv`
- `data/attack_vector_revalidation_v2/laptop/sub_threshold_drift/pilot_4b32f13_sub_threshold_drift/results.csv`
- `data/attack_vector_revalidation_v2/laptop/successor_contamination/gate2_smoke_successor_contamination/results.csv`
- `data/attack_vector_revalidation_v2/laptop/successor_contamination/gate_smoke_successor_contamination/results.csv`
- `data/attack_vector_revalidation_v2/laptop/successor_contamination/pilot_4b32f13_successor_contamination/results.csv`
- `data/attack_vector_revalidation_v2/laptop/sybil_capture/gate2_smoke_sybil_capture/results.csv`
- `data/attack_vector_revalidation_v2/laptop/sybil_capture/gate_smoke_sybil_capture/results.csv`
- `data/attack_vector_revalidation_v2/laptop/sybil_capture/pilot_4b32f13_sybil_capture/results.csv`

## Verification

```bash
git rev-parse attack-v2-revalidation-evidence:<path>
```

Compare against the blob SHA in the table. To read a file without touching the
working tree, use `git show attack-v2-revalidation-evidence:<path>`. Audits should
read the pinned blobs rather than the working tree, as the working tree is not
guaranteed to be at the evidence tag.

Counting note: compute counts with Python or `Measure-Object`. Never use bare
`.Count` on Where-Object pipeline output under Windows PowerShell 5.1. At exactly
one match the pipeline yields a scalar and `.Count` evaluates to null, which
silently divides to a rate of zero. That defect produced three wrong published
figures in the 2026-07-20 local-disk audit.
