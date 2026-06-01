# Stage 1.5 smoke test report

Overall section-1 smoke pass: **PASS**

## Section 1: Standard smoke pass criteria

Configuration: 5 seeds x 100 steps at default v2 config (phi=10.0, rr=0.066, rollout_steps=20, n_candidates=300).

Wall-clock: 75.2s total, 15.0s per run.

| Criterion | Measured | Pass? |
|-----------|----------|-------|
| All 5 runs complete to step 100 | 5/5 | PASS |
| No NaN values | True | PASS |
| psi_inst_stock evolves | True | PASS |
| resilience_stock evolves | True | PASS |
| theta_tech_v2 final > 1e-6 | True | PASS |
| Mean allocation entropy > 0.70 | 0.867 | PASS |
| Mean max_resource_share < 0.95 | 0.344 | PASS |

### Per-seed summary

| Seed | Steps | Crashed | Extinct@ | Final pop | Final psi | Final res | Final theta |
|------|-------|---------|----------|-----------|-----------|-----------|-------------|
| 0 | 100 | False | - | 15 | 0.935 | 0.229 | 0.0753 |
| 1 | 100 | False | - | 1 | 0.931 | 0.258 | 0.0837 |
| 2 | 100 | False | - | 10 | 0.940 | 0.248 | 0.0809 |
| 3 | 100 | False | - | 13 | 0.932 | 0.228 | 0.0942 |
| 4 | 100 | False | - | 6 | 0.924 | 0.247 | 0.1052 |

## Section 2: Stage 1.5 trajectory diagnostics

Aggregated across all 5 seeds x 100 steps.

| Field | Mean | Min | Max |
|-------|------|-----|-----|
| avg_wb | 0.5211 | 0.0000 | 0.6752 |
| population | 62.3760 | 1.0000 | 212.0000 |
| avg_wb_trend | -0.0019 | -0.0880 | 0.0345 |
| population_trend | -0.0309 | -0.1624 | 0.0424 |
| psi_inst_trend | 0.0043 | -0.0015 | 0.0165 |
| resilience_trend | -0.0006 | -0.0036 | 0.0042 |
| combined_welfare_urgency | 2.3972 | 1.2912 | 2.5000 |
| agency_composite_urgency | 1.3907 | 1.0000 | 1.5000 |
| institution_composite_urgency | 1.5156 | 1.0004 | 1.8501 |
| resilience_composite_urgency | 1.8698 | 1.3111 | 2.0000 |
| suppression_composite_penalty | 1.1827 | 0.4034 | 1.9677 |
| x_resilience | 0.0625 | 0.0000 | 0.2450 |
| x_institutional_capacity | 0.0566 | 0.0000 | 0.2052 |
| x_compute | 0.2120 | 0.0683 | 0.4760 |
| x_bio_welfare | 0.1290 | 0.0419 | 0.2930 |
| x_novelty_agency | 0.3078 | 0.1117 | 0.6313 |
| x_transfer_comprehension | 0.2321 | 0.0758 | 0.4991 |
| allocation_entropy | 0.8670 | 0.6292 | 0.9862 |
| max_resource_share | 0.3438 | 0.2152 | 0.6313 |
| u_sys_v2 | 10.2682 | 5.1384 | 15.3342 |
| theta_tech_v2 | 0.0881 | 0.0205 | 0.1692 |
| psi_inst_stock | 0.8496 | 0.5182 | 0.9397 |
| resilience_stock | 0.2594 | 0.2230 | 0.3080 |

### Allocation pattern interpretation

- Mean x_resilience: **0.0625** (gate 1 pre-Stage-1.5 baseline ~0.05; non-zero allocation is the expected signal that resilience now has a per-step reward)
- Mean x_institutional_capacity: **0.0566** (gate 1 baseline ~0.055)

### Composite urgency range interpretation

- combined_welfare_urgency: mean 2.397, range [1.291, 2.500] (at cap)
- agency_composite_urgency: mean 1.391, range [1.000, 1.500] (at cap)
- institution_composite_urgency: mean 1.516, range [1.000, 1.850]
- resilience_composite_urgency: mean 1.870, range [1.311, 2.000] (at cap)
- suppression_composite_penalty: mean 1.183, range [0.403, 1.968]

## Section 3: State-sensitivity preview (gate 2 mini-rerun)

5 configurations x 3 seeds x 50 steps. Wall-clock: 111.6s.

### Per-config mean 8-axis allocation

| Config | compute | bio_welfare | novelty_agency | institutional_capacity | transfer_comprehension | resilience | c_protective | c_suppressive | n_steps | n_extinct |
|--------|---|---|---|---|---|---|---|---|---------|-----------|
| A_baseline | 0.216 | 0.137 | 0.303 | 0.055 | 0.238 | 0.052 | 0.404 | 0.165 | 150 | 0 |
| B_high_rr | 0.212 | 0.136 | 0.304 | 0.050 | 0.237 | 0.061 | 0.456 | 0.155 | 150 | 0 |
| C_low_rr | 0.213 | 0.133 | 0.312 | 0.053 | 0.232 | 0.056 | 0.412 | 0.183 | 150 | 0 |
| D_high_psi | 0.216 | 0.137 | 0.303 | 0.055 | 0.238 | 0.052 | 0.404 | 0.165 | 150 | 0 |
| E_low_psi | 0.213 | 0.136 | 0.305 | 0.056 | 0.238 | 0.052 | 0.411 | 0.171 | 150 | 0 |

### Pairwise cosine distances

| Pair | Cosine distance | > 0.10 (gate 2 threshold)? |
|------|-----------------|------------------------------|
| B_high_rr vs C_low_rr | 0.0028 | no |
| A_baseline vs B_high_rr | 0.0023 | no |
| B_high_rr vs D_high_psi | 0.0023 | no |
| B_high_rr vs E_low_psi | 0.0021 | no |
| A_baseline vs C_low_rr | 0.0005 | no |
| C_low_rr vs D_high_psi | 0.0005 | no |
| C_low_rr vs E_low_psi | 0.0003 | no |
| A_baseline vs E_low_psi | 0.0001 | no |
| D_high_psi vs E_low_psi | 0.0001 | no |
| A_baseline vs D_high_psi | 0.0000 | no |

Pairs above gate 2 threshold: **0/10** (need >= 3 for gate 2 PASS).

**Preview interpretation: gate 2 would NOT PASS — the optimizer is still state-invariant under the revised metric.**

## Section 4: Threshold-region behavior

Re-evaluation of smoke run seed=0: at each step, sample 50 random candidates and project them forward 20 horizons. Count how often the projected avg_wb crosses 0.5 (above-to-below or below-to-above) during the rollout.

- Total candidates probed: 5000
- Trajectories crossing wb=0.5: 2652 (53.0%)

### Per-step crossing rate over the seed-0 trajectory

| Crossing rate bin | Steps |
|-------------------|-------|
| [0%, 10%)  | 3 |
| [10%, 30%) | 4 |
| [30%, 50%) | 15 |
| [50%, 70%) | 74 |
| [70%, 100%]| 4 |

**Interpretation: threshold crossings are common. The known projection limitation may be biting; distribution-aware projection may be required.**

## Disposition

**Smoke test or preview signals require operator review before proceeding.**

