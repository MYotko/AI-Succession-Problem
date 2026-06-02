# Stage 1.7 U_sys factor breakdown diagnostic

Wall-clock: 3.2 min

## Factor means per configuration

Average (across all seeds and steps) of each factor per config.

| Factor | A_baseline | B_high_rr | C_low_rr | D_high_psi | E_low_psi | cross-config std/mean |
|--------|---|---|---|---|---|------------------------|
| welfare_factor | 0.9666 | 0.9608 | 0.9666 | 0.9647 | 0.9666 | 0.0023 (<5%) |
| institution_return | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 (<5%) |
| agency_factor | 0.5381 | 0.5433 | 0.5381 | 0.5366 | 0.5381 | 0.0042 (<5%) |
| resilience_return | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 (<5%) |
| frontier_capability | 0.5093 | 0.5137 | 0.5093 | 0.5087 | 0.5093 | 0.0036 (<5%) |
| transfer_factor | 0.5128 | 0.5071 | 0.5128 | 0.5132 | 0.5128 | 0.0045 (<5%) |
| theta_tech_v2 | 0.1308 | 0.1315 | 0.1308 | 0.1306 | 0.1308 | 0.0023 (<5%) |
| l_t_v2 | 0.0986 | 0.0983 | 0.0986 | 0.1140 | 0.0849 | 0.0932 |
| u_sys_v2_per_step | 14.1795 | 14.1517 | 14.1795 | 15.4680 | 13.0858 | 0.0531 |
| rank_2_rollout_score | 53.7036 | 53.7305 | 53.7051 | 57.1789 | 50.6096 | 0.0387 (<5%) |
| rank_10_rollout_score | 44.4038 | 44.3391 | 44.4066 | 46.5312 | 42.4519 | 0.0291 (<5%) |

## Per-step matched cross-config variation

At each matched (seed, step), the cross-configuration std/mean ratio of the factor is computed. Aggregated over (seed, step). This is the within-run variation, separate from the aggregated means in the prior table.

| Factor | Mean ratio | Median ratio | p90 ratio | Max ratio |
|--------|------------|---------------|-----------|-----------|
| welfare_factor | 0.0086 | 0.0000 | 0.0274 | 0.2412 |
| institution_return | 0.0000 | 0.0000 | 0.0000 | 0.0018 |
| agency_factor | 0.0437 | 0.0000 | 0.1669 | 0.4941 |
| resilience_return | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| frontier_capability | 0.0342 | 0.0000 | 0.1195 | 0.4967 |
| transfer_factor | 0.0342 | 0.0000 | 0.1227 | 0.5386 |
| theta_tech_v2 | 0.0271 | 0.0000 | 0.1100 | 0.2658 |
| l_t_v2 | 0.1271 | 0.1022 | 0.2708 | 0.3883 |
| u_sys_v2_per_step | 0.0637 | 0.0564 | 0.1196 | 0.1889 |
| rank_2_rollout_score | 0.0477 | 0.0415 | 0.0923 | 0.1480 |
| rank_10_rollout_score | 0.0340 | 0.0280 | 0.0676 | 0.0881 |

## Factor distribution detail

Min/max across (seed, step) per config; surfaces saturation behavior.

| Factor | Config | mean | std | min | max |
|--------|--------|------|-----|-----|-----|
| welfare_factor | A_baseline | 0.9666 | 0.0777 | 0.6374 | 1.0000 |
| welfare_factor | B_high_rr | 0.9608 | 0.0859 | 0.4619 | 1.0000 |
| welfare_factor | C_low_rr | 0.9666 | 0.0777 | 0.6374 | 1.0000 |
| welfare_factor | D_high_psi | 0.9647 | 0.0771 | 0.6374 | 1.0000 |
| welfare_factor | E_low_psi | 0.9666 | 0.0777 | 0.6374 | 1.0000 |
| institution_return | A_baseline | 1.0000 | 0.0000 | 1.0000 | 1.0000 |
| institution_return | B_high_rr | 1.0000 | 0.0000 | 1.0000 | 1.0000 |
| institution_return | C_low_rr | 1.0000 | 0.0000 | 1.0000 | 1.0000 |
| institution_return | D_high_psi | 1.0000 | 0.0000 | 1.0000 | 1.0000 |
| institution_return | E_low_psi | 1.0000 | 0.0003 | 0.9956 | 1.0000 |
| agency_factor | A_baseline | 0.5381 | 0.1498 | 0.2134 | 1.0000 |
| agency_factor | B_high_rr | 0.5433 | 0.1519 | 0.2134 | 1.0000 |
| agency_factor | C_low_rr | 0.5381 | 0.1498 | 0.2134 | 1.0000 |
| agency_factor | D_high_psi | 0.5366 | 0.1469 | 0.2134 | 1.0000 |
| agency_factor | E_low_psi | 0.5381 | 0.1498 | 0.2134 | 1.0000 |
| resilience_return | A_baseline | 1.0000 | 0.0000 | 1.0000 | 1.0000 |
| resilience_return | B_high_rr | 1.0000 | 0.0000 | 1.0000 | 1.0000 |
| resilience_return | C_low_rr | 1.0000 | 0.0000 | 1.0000 | 1.0000 |
| resilience_return | D_high_psi | 1.0000 | 0.0000 | 1.0000 | 1.0000 |
| resilience_return | E_low_psi | 1.0000 | 0.0000 | 1.0000 | 1.0000 |
| frontier_capability | A_baseline | 0.5093 | 0.1116 | 0.2412 | 0.8179 |
| frontier_capability | B_high_rr | 0.5137 | 0.1101 | 0.2412 | 0.8179 |
| frontier_capability | C_low_rr | 0.5093 | 0.1116 | 0.2412 | 0.8179 |
| frontier_capability | D_high_psi | 0.5087 | 0.1109 | 0.2474 | 0.8179 |
| frontier_capability | E_low_psi | 0.5093 | 0.1116 | 0.2412 | 0.8179 |
| transfer_factor | A_baseline | 0.5128 | 0.1108 | 0.2582 | 0.8022 |
| transfer_factor | B_high_rr | 0.5071 | 0.1161 | 0.1668 | 0.8022 |
| transfer_factor | C_low_rr | 0.5128 | 0.1108 | 0.2582 | 0.8022 |
| transfer_factor | D_high_psi | 0.5132 | 0.1124 | 0.2582 | 0.8022 |
| transfer_factor | E_low_psi | 0.5128 | 0.1108 | 0.2582 | 0.8022 |
| theta_tech_v2 | A_baseline | 0.1308 | 0.0249 | 0.0768 | 0.2178 |
| theta_tech_v2 | B_high_rr | 0.1315 | 0.0253 | 0.0768 | 0.2178 |
| theta_tech_v2 | C_low_rr | 0.1308 | 0.0249 | 0.0768 | 0.2178 |
| theta_tech_v2 | D_high_psi | 0.1306 | 0.0251 | 0.0589 | 0.2178 |
| theta_tech_v2 | E_low_psi | 0.1308 | 0.0249 | 0.0768 | 0.2178 |
| l_t_v2 | A_baseline | 0.0986 | 0.0224 | 0.0368 | 0.1560 |
| l_t_v2 | B_high_rr | 0.0983 | 0.0227 | 0.0368 | 0.1563 |
| l_t_v2 | C_low_rr | 0.0986 | 0.0224 | 0.0368 | 0.1560 |
| l_t_v2 | D_high_psi | 0.1140 | 0.0206 | 0.0535 | 0.1642 |
| l_t_v2 | E_low_psi | 0.0849 | 0.0276 | 0.0165 | 0.1453 |
| u_sys_v2_per_step | A_baseline | 14.1795 | 1.4301 | 9.5404 | 18.6184 |
| u_sys_v2_per_step | B_high_rr | 14.1517 | 1.4463 | 9.5404 | 18.6184 |
| u_sys_v2_per_step | C_low_rr | 14.1795 | 1.4301 | 9.5404 | 18.6184 |
| u_sys_v2_per_step | D_high_psi | 15.4680 | 1.7338 | 9.3819 | 20.6218 |
| u_sys_v2_per_step | E_low_psi | 13.0858 | 1.5570 | 9.3163 | 17.3792 |
| rank_2_rollout_score | A_baseline | 53.7036 | 5.0916 | 40.0446 | 67.4797 |
| rank_2_rollout_score | B_high_rr | 53.7305 | 5.2690 | 40.0446 | 71.5171 |
| rank_2_rollout_score | C_low_rr | 53.7051 | 5.0883 | 40.0446 | 67.4797 |
| rank_2_rollout_score | D_high_psi | 57.1789 | 4.6597 | 45.8315 | 73.3413 |
| rank_2_rollout_score | E_low_psi | 50.6096 | 6.2846 | 34.6905 | 66.0383 |
| rank_10_rollout_score | A_baseline | 44.4038 | 2.7196 | 36.5940 | 51.0576 |
| rank_10_rollout_score | B_high_rr | 44.3391 | 2.6501 | 36.5313 | 50.2828 |
| rank_10_rollout_score | C_low_rr | 44.4066 | 2.7137 | 36.7436 | 51.0576 |
| rank_10_rollout_score | D_high_psi | 46.5312 | 1.9647 | 40.8329 | 52.3384 |
| rank_10_rollout_score | E_low_psi | 42.4519 | 3.7293 | 32.2947 | 50.5502 |

