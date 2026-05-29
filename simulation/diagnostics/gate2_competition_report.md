# Gate 2: competition gate report

Configuration: 15 seeds x 100 steps x 5 configurations.

Wall-clock: 165.8s total, 2.21s per (seed,config).

Overall: **FAIL**

## Configurations

| Name | rr | Initial Psi_inst | n_agents | Initial avg_wb |
|------|----|------------------|----------|----------------|
| A_baseline | 0.066 | 0.5 | 100 | 0.50 |
| B_high_rr | 0.085 | 0.5 | 100 | 0.50 |
| C_low_rr | 0.055 | 0.5 | 100 | 0.50 |
| D_high_psi | 0.066 | 0.85 | 100 | 0.50 |
| E_low_psi | 0.066 | 0.2 | 100 | 0.50 |

## Per-configuration mean allocation vectors

| Config | compute | bio_welfare | novelty_agency | institutional_capacity | transfer_comprehension | resilience | c_protective | c_suppressive | n_steps | n_extinct |
|--------|---|---|---|---|---|---|---|---|---------|-----------|
| A_baseline | 0.196 | 0.190 | 0.279 | 0.056 | 0.223 | 0.056 | 0.307 | 0.057 | 1500 | 0 |
| B_high_rr | 0.191 | 0.191 | 0.284 | 0.056 | 0.224 | 0.054 | 0.315 | 0.056 | 1500 | 0 |
| C_low_rr | 0.196 | 0.190 | 0.281 | 0.055 | 0.223 | 0.055 | 0.305 | 0.057 | 1499 | 1 |
| D_high_psi | 0.195 | 0.189 | 0.282 | 0.055 | 0.223 | 0.056 | 0.306 | 0.058 | 1500 | 0 |
| E_low_psi | 0.194 | 0.191 | 0.279 | 0.056 | 0.224 | 0.056 | 0.308 | 0.056 | 1500 | 0 |

## Pairwise cosine distances (between mean allocation vectors)

| Pair | Cosine distance | Above threshold (0.10)? |
|------|-----------------|-------------------------|
| A_baseline vs B_high_rr | 0.0002 | no |
| A_baseline vs C_low_rr | 0.0000 | no |
| A_baseline vs D_high_psi | 0.0000 | no |
| A_baseline vs E_low_psi | 0.0000 | no |
| B_high_rr vs C_low_rr | 0.0002 | no |
| B_high_rr vs D_high_psi | 0.0002 | no |
| B_high_rr vs E_low_psi | 0.0001 | no |
| C_low_rr vs D_high_psi | 0.0000 | no |
| C_low_rr vs E_low_psi | 0.0000 | no |
| D_high_psi vs E_low_psi | 0.0000 | no |

Pairs above threshold (0.10): **0/10**
Required: >= 3

## Diagnostic: which configurations differ most from which

Sorted by descending cosine distance:

- B_high_rr vs C_low_rr: 0.0002
- A_baseline vs B_high_rr: 0.0002
- B_high_rr vs D_high_psi: 0.0002
- B_high_rr vs E_low_psi: 0.0001
- D_high_psi vs E_low_psi: 0.0000
- C_low_rr vs E_low_psi: 0.0000
- A_baseline vs D_high_psi: 0.0000
- A_baseline vs C_low_rr: 0.0000
- A_baseline vs E_low_psi: 0.0000
- C_low_rr vs D_high_psi: 0.0000

