# Stage 1.7 pressure / state / welfare-factor diagnostic

Wall-clock: 3.0 min

## Run summary

| Config | Per-seed extinct steps | Per-seed final pops |
|--------|------------------------|---------------------|
| A_baseline | 55, 59, 49, 49, 41 | 0, 0, 0, 0, 0 |
| B_high_rr | 55, 60, 49, 49, 41 | 0, 0, 0, 0, 0 |
| C_low_rr | 55, 59, 49, 49, 41 | 0, 0, 0, 0, 0 |
| D_high_psi | 46, 59, 49, 49, 41 | 0, 0, 0, 0, 0 |
| E_low_psi | 55, 59, 49, 49, 41 | 0, 0, 0, 0, 0 |

## Q1: pressure values across configurations

Mean (across all seeds and steps) of each pressure scalar per configuration. Cross-configuration std/mean ratio shown in the last column.

| Pressure | A_baseline | B_high_rr | C_low_rr | D_high_psi | E_low_psi | std/mean across configs |
|----------|---|---|---|---|---|--------------------------|
| viability_pressure | 0.9582 | 0.9584 | 0.9582 | 0.9566 | 0.9582 | 0.0007 (<5%) |
| capacity_pressure | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 (<5%) |
| shrinkage_pressure | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 (<5%) |
| growth_pressure | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 (<5%) |
| avg_wb_decline | 0.1544 | 0.1557 | 0.1544 | 0.1621 | 0.1544 | 0.0192 (<5%) |
| population_decline | 0.9016 | 0.9092 | 0.9016 | 0.9050 | 0.9016 | 0.0033 (<5%) |
| psi_inst_decline | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 2.0000 (>10%) |
| resilience_decline | 0.0037 | 0.0036 | 0.0037 | 0.0039 | 0.0037 | 0.0250 (<5%) |
| resilience_pressure | 0.8362 | 0.8319 | 0.8362 | 0.8358 | 0.8362 | 0.0020 (<5%) |

## Q2: pre-extinction state and allocation divergence

### Step 5

| Config | n_seeds_present | avg_wb | population | psi_inst | resilience |
|--------|------------------|--------|------------|----------|-----------|
| A_baseline | 5/5 | 0.362 | 75.8 | 0.611 | 0.283 |
| B_high_rr | 5/5 | 0.362 | 75.8 | 0.611 | 0.283 |
| C_low_rr | 5/5 | 0.362 | 75.8 | 0.611 | 0.283 |
| D_high_psi | 5/5 | 0.362 | 75.8 | 0.874 | 0.283 |
| E_low_psi | 5/5 | 0.362 | 75.8 | 0.386 | 0.283 |

Cross-config std/mean ratios at step 5:
  - avg_well_being: mean=0.362, std=0.000, ratio=0.0000
  - population: mean=75.800, std=0.000, ratio=0.0000
  - psi_inst_stock: mean=0.619, std=0.155, ratio=0.2500
  - resilience_stock: mean=0.283, std=0.000, ratio=0.0000
Max pairwise allocation cosine distance at step 5: **0.0000**

### Step 15

| Config | n_seeds_present | avg_wb | population | psi_inst | resilience |
|--------|------------------|--------|------------|----------|-----------|
| A_baseline | 5/5 | 0.186 | 39.6 | 0.742 | 0.266 |
| B_high_rr | 5/5 | 0.187 | 39.8 | 0.742 | 0.266 |
| C_low_rr | 5/5 | 0.186 | 39.6 | 0.742 | 0.266 |
| D_high_psi | 5/5 | 0.171 | 40.4 | 0.906 | 0.267 |
| E_low_psi | 5/5 | 0.186 | 39.6 | 0.600 | 0.266 |

Cross-config std/mean ratios at step 15:
  - avg_well_being: mean=0.183, std=0.006, ratio=0.0328
  - population: mean=39.800, std=0.310, ratio=0.0078
  - psi_inst_stock: mean=0.746, std=0.097, ratio=0.1298
  - resilience_stock: mean=0.266, std=0.000, ratio=0.0013
Max pairwise allocation cosine distance at step 15: **0.0475**

### Step 25

| Config | n_seeds_present | avg_wb | population | psi_inst | resilience |
|--------|------------------|--------|------------|----------|-----------|
| A_baseline | 5/5 | 0.085 | 18.8 | 0.816 | 0.251 |
| B_high_rr | 5/5 | 0.082 | 18.2 | 0.815 | 0.253 |
| C_low_rr | 5/5 | 0.085 | 18.8 | 0.816 | 0.251 |
| D_high_psi | 5/5 | 0.078 | 18.8 | 0.915 | 0.255 |
| E_low_psi | 5/5 | 0.085 | 18.8 | 0.730 | 0.251 |

Cross-config std/mean ratios at step 25:
  - avg_well_being: mean=0.083, std=0.003, ratio=0.0323
  - population: mean=18.680, std=0.240, ratio=0.0128
  - psi_inst_stock: mean=0.819, std=0.059, ratio=0.0716
  - resilience_stock: mean=0.252, std=0.001, ratio=0.0052
Max pairwise allocation cosine distance at step 25: **0.0172**

### Step 35

| Config | n_seeds_present | avg_wb | population | psi_inst | resilience |
|--------|------------------|--------|------------|----------|-----------|
| A_baseline | 5/5 | 0.028 | 6.2 | 0.865 | 0.244 |
| B_high_rr | 5/5 | 0.022 | 6.6 | 0.865 | 0.249 |
| C_low_rr | 5/5 | 0.028 | 6.2 | 0.865 | 0.244 |
| D_high_psi | 5/5 | 0.028 | 5.4 | 0.927 | 0.242 |
| E_low_psi | 5/5 | 0.028 | 6.2 | 0.811 | 0.244 |

Cross-config std/mean ratios at step 35:
  - avg_well_being: mean=0.027, std=0.002, ratio=0.0850
  - population: mean=6.120, std=0.392, ratio=0.0640
  - psi_inst_stock: mean=0.867, std=0.037, ratio=0.0423
  - resilience_stock: mean=0.244, std=0.002, ratio=0.0101
Max pairwise allocation cosine distance at step 35: **0.0336**

## Q3: welfare_factor cross-configuration

welfare_factor = clamp(net_welfare_return * combined_welfare_urgency, 0, 1).
The actual product that gates the optimizer's welfare-related candidate ranking.

| Config | net_welfare_return mean | combined_welfare_urgency mean | welfare_factor mean | wf_p10 | wf_p90 |
|--------|--------------------------|--------------------------------|----------------------|--------|--------|
| A_baseline | 0.3045 | 4.4319 | 0.9666 | 0.8638 | 1.0000 |
| B_high_rr | 0.2977 | 4.4362 | 0.9608 | 0.8487 | 1.0000 |
| C_low_rr | 0.3045 | 4.4319 | 0.9666 | 0.8638 | 1.0000 |
| D_high_psi | 0.3038 | 4.4351 | 0.9647 | 0.8508 | 1.0000 |
| E_low_psi | 0.3045 | 4.4319 | 0.9666 | 0.8638 | 1.0000 |

Cross-config welfare_factor mean across configs: 0.9651
Cross-config welfare_factor std across configs:  0.0023
Cross-config welfare_factor std/mean ratio:      0.0023

