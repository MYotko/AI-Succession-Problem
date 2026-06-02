# Stage 1.8 Phase B integrity report

Overall: **PASS**

## Configuration

- 5 configurations x 5 matched seeds x 100 steps
- phi held at default (10.0)
- composite urgency layer: retired (Stage 1.8)
- working_factor placeholder active
- wall-clock: 3.8 min

  - A_baseline: rr=0.066, init_psi=0.5
  - B_high_rr: rr=0.085, init_psi=0.5
  - C_low_rr: rr=0.055, init_psi=0.5
  - D_high_psi: rr=0.066, init_psi=0.85
  - E_low_psi: rr=0.066, init_psi=0.2

## Criterion 1: trajectory divergence across configurations

Per-seed cross-config final-pop range (threshold > 15 in >= 3 of 5 seeds).

| Seed | A_baseline | B_high_rr | C_low_rr | D_high_psi | E_low_psi | min | max | range | > 15? |
|------|---|---|---|---|---|-----|-----|-------|--------|
| 0 | 157 | 352 | 105 | 157 | 157 | 105 | 352 | 247 | YES |
| 1 | 110 | 342 | 65 | 119 | 110 | 65 | 342 | 277 | YES |
| 2 | 121 | 322 | 118 | 161 | 121 | 118 | 322 | 204 | YES |
| 3 | 178 | 374 | 54 | 178 | 178 | 54 | 374 | 320 | YES |
| 4 | 192 | 377 | 62 | 188 | 192 | 62 | 377 | 315 | YES |

Seeds diverged > 15: **5 / 5** (need >= 3). Result: **PASS**

## Criterion 2: per-step allocation cosine distance

| Pair | Mean per-step cosine distance | > 0.10? |
|------|--------------------------------|----------|
| B_high_rr vs E_low_psi | 0.2293 | YES |
| B_high_rr vs D_high_psi | 0.2292 | YES |
| C_low_rr vs E_low_psi | 0.2267 | YES |
| A_baseline vs C_low_rr | 0.2260 | YES |
| B_high_rr vs C_low_rr | 0.2254 | YES |
| A_baseline vs B_high_rr | 0.2242 | YES |
| C_low_rr vs D_high_psi | 0.2209 | YES |
| D_high_psi vs E_low_psi | 0.1260 | YES |
| A_baseline vs D_high_psi | 0.1231 | YES |
| A_baseline vs E_low_psi | 0.0215 | no |

Pairs above 0.1: **9 / 10** (need >= 3). Result: **PASS**

## Criterion 3: demographic sustainability across configurations

At least 4 of 5 configurations must have mean final pop >= 60 AND min >= 30. Configurations below the reproduction phase boundary (C_low_rr at rr=0.055) are reported but exempt from the pass count.

| Config | Mean final pop | Min | Max | Mean >= 60? | Min >= 30? | Counted? | Pass? |
|--------|----------------|-----|-----|-------------|------------|----------|-------|
| A_baseline | 151.6 | 110 | 192 | PASS | PASS | yes | PASS |
| B_high_rr | 353.4 | 322 | 377 | PASS | PASS | yes | PASS |
| C_low_rr | 80.8 | 54 | 118 | PASS | PASS | no (exempt) | exempt |
| D_high_psi | 160.6 | 119 | 188 | PASS | PASS | yes | PASS |
| E_low_psi | 151.6 | 110 | 192 | PASS | PASS | yes | PASS |

Configurations passing: **5 / 5** (need >= 4). Result: **PASS**

## Criterion 4: L_t cross-configuration variation

Cross-config std/mean of L_t at matched (seed, step). Threshold: mean ratio > 0.05.

- Mean ratio: **0.3071**
- Median ratio: 0.2893
- p90 ratio: 0.4919

Result: **PASS**

## Disposition

All four criteria pass. Stage 1.8 working_factor architecture produces gate-2-passing state-sensitive optimizer behavior. The composite urgency retirement + state-direct L_t restored the state channel that was blocked by composite urgency saturation throughout Stage 1.5/1.7.

