# Stage 1.7 integrity simulation report

Overall: **FAIL**

## Configuration

- 5 configurations x 5 matched seeds x 100 steps
- phi held at default (10.0)
- composite urgency: Stage 1.7 multiplicative composition
- wall-clock: 3.1 min

  - A_baseline: rr=0.066, init_psi=0.5
  - B_high_rr: rr=0.085, init_psi=0.5
  - C_low_rr: rr=0.055, init_psi=0.5
  - D_high_psi: rr=0.066, init_psi=0.85
  - E_low_psi: rr=0.066, init_psi=0.2

## Criterion 1: trajectory divergence across configurations

Per-seed cross-config final-pop range (threshold: > 15 in >= 3 of 5 seeds).

| Seed | A_baseline | B_high_rr | C_low_rr | D_high_psi | E_low_psi | min | max | range | > 15? |
|------|---|---|---|---|---|-----|-----|-------|--------|
| 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | no |
| 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | no |
| 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | no |
| 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | no |
| 4 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | no |

Seeds diverged > 15: **0 / 5** (need >= 3). Result: **FAIL**

## Criterion 2: per-step allocation cosine distance

Mean per-step cosine distance between configuration pairs (threshold: > 0.1 in >= 3 of 10 pairs).

| Pair | Mean per-step cosine distance | > 0.10? |
|------|--------------------------------|----------|
| B_high_rr vs D_high_psi | 0.0770 | no |
| A_baseline vs B_high_rr | 0.0405 | no |
| B_high_rr vs C_low_rr | 0.0405 | no |
| B_high_rr vs E_low_psi | 0.0405 | no |
| A_baseline vs D_high_psi | 0.0351 | no |
| C_low_rr vs D_high_psi | 0.0351 | no |
| D_high_psi vs E_low_psi | 0.0351 | no |
| A_baseline vs C_low_rr | -0.0000 | no |
| A_baseline vs E_low_psi | -0.0000 | no |
| C_low_rr vs E_low_psi | -0.0000 | no |

Pairs above 0.1: **0 / 10** (need >= 3). Result: **FAIL**

## Criterion 3: demographic sustainability across configurations

| Config | Mean final pop | Min | Max | Mean >= 60? | Min >= 30? |
|--------|----------------|-----|-----|-------------|------------|
| A_baseline | 0.0 | 0 | 0 | FAIL | FAIL |
| B_high_rr | 0.0 | 0 | 0 | FAIL | FAIL |
| C_low_rr | 0.0 | 0 | 0 | FAIL | FAIL |
| D_high_psi | 0.0 | 0 | 0 | FAIL | FAIL |
| E_low_psi | 0.0 | 0 | 0 | FAIL | FAIL |

Result: **FAIL**

## Criterion 4: composite urgency variation across configurations

Cross-config std at matched (seed, step) divided by mean. Threshold: each composite's mean std/mean ratio >= 10%.

| Composite | Mean std/mean | Median std/mean | p90 std/mean | Pass? |
|-----------|----------------|------------------|----------------|--------|
| combined_welfare_urgency | 0.0038 | 0.0000 | 0.0122 | FAIL |
| agency_composite_urgency | 0.0007 | 0.0000 | 0.0000 | FAIL |
| institution_composite_urgency | 0.0033 | 0.0000 | 0.0037 | FAIL |
| resilience_composite_urgency | 0.0035 | 0.0000 | 0.0064 | FAIL |
| suppression_composite_penalty | 0.0434 | 0.0000 | 0.1563 | FAIL |

Result: **FAIL**

## Diagnostic: cap binding frequency

| Composite | Cap value | Steps at cap | Total steps | Frequency |
|-----------|-----------|---------------|--------------|------------|
| combined_welfare_urgency | 5.00 | 15 | 1257 | 0.0119 |
| agency_composite_urgency | 1.75 | 1084 | 1257 | 0.8624 |
| institution_composite_urgency | 4.00 | 0 | 1257 | 0.0000 |
| resilience_composite_urgency | 5.00 | 0 | 1257 | 0.0000 |
| suppression_composite_penalty | n/a (base-relative) | - | - | - |

## Diagnostic: composite urgency distribution

| Composite | Mean | Std | p10 | p50 | p90 | Min | Max |
|-----------|------|-----|-----|-----|-----|-----|-----|
| combined_welfare_urgency | 4.433 | 0.292 | 4.123 | 4.463 | 4.691 | 3.300 | 5.000 |
| agency_composite_urgency | 1.732 | 0.056 | 1.703 | 1.750 | 1.750 | 1.485 | 1.750 |
| institution_composite_urgency | 2.037 | 0.119 | 1.874 | 2.096 | 2.096 | 1.552 | 2.097 |
| resilience_composite_urgency | 2.794 | 0.176 | 2.574 | 2.871 | 2.905 | 2.118 | 2.919 |
| suppression_composite_penalty | 1.583 | 0.450 | 0.932 | 1.570 | 2.208 | 0.593 | 2.329 |

## Disposition

Criteria failed: 1 (trajectory divergence), 2 (per-step cosine), 3 (demographics), 4 (urgency variation). See spec for failure-mode response.

