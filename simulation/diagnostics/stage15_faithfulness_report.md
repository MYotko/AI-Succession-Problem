# Stage 1.5 faithfulness test report

Overall: **FAIL**

Total wall-clock: 50.1s

## Ensemble size

Empirical agent-layer simulations: n_seeds = 20 per test case. Diagnostic justification: 6-seed ensembles produced near-zero noise artifacts in sign and direction comparisons even when the projection was structurally faithful; 20 seeds resolves the empirical mean to sub-noise resolution so the comparison measures projection faithfulness rather than ensemble sampling artifact. The projection runs once deterministically per test case; the empirical mean is computed over the 20-seed ensemble. Test conditions, action sequences, initial states, horizons, and faithfulness thresholds are unchanged from the program reference specification.

## Test A: avg_wb projection

Wall-clock: 8.0s

Result: **FAIL**

| Criterion | Measured | Pass? |
|-----------|----------|-------|
| 1-step max <= 0.01 | 0.0007203287430825878 | PASS |
| 5-step mean <= 0.02 | 0.004495536177948341 | PASS |
| 20-step mean <= 0.035, max <= 0.06 | (0.06511549246131229, 0.2419269686946537) | FAIL |
| directional agreement >= 0.90 | 1.0 | PASS |

## Test B: population projection (general + boundary)

Wall-clock: 24.5s

Result: **FAIL**

| Criterion | Measured | Pass? |
|-----------|----------|-------|
| 1-step mean rel err <= 5% | 0.019297564142448792 | PASS |
| 5-step mean rel err <= 10% | 0.08131152035641434 | PASS |
| 20-step mean rel err <= 15% | 0.06989387766071824 | PASS |
| directional agreement >= 0.85 | 0.7962962962962963 | FAIL |
| boundary false-safe rate <= 10% | 0.0 | PASS |
| boundary false-comfort rate <= 15% | 0.0 | PASS |

## Test C: resilience_stock projection

Wall-clock: 12.1s

Result: **PASS**

| Criterion | Measured | Pass? |
|-----------|----------|-------|
| 5-step mean err <= 0.015 | 4.90059381963448e-17 | PASS |
| 20-step mean err <= 0.035, max <= 0.06 | (5.724587470723463e-17, 1.1102230246251565e-16) | PASS |
| directional agreement >= 0.95 | 1.0 | PASS |

## Test C (shock attenuation verification)

Wall-clock: 0.0s

Result: **PASS**


| stock | raw_mag | expected_eff | measured_eff | expected_drawdown | measured_drawdown |
|-------|---------|--------------|--------------|-------------------|--------------------|
| 0.00 | 0.20 | 0.20000 | 0.20000 | 0.00000 | 0.00000 |
| 0.00 | 0.50 | 0.50000 | 0.50000 | 0.00000 | 0.00000 |
| 0.00 | 0.80 | 0.80000 | 0.80000 | 0.00000 | 0.00000 |
| 0.30 | 0.20 | 0.15800 | 0.15800 | 0.06300 | 0.06300 |
| 0.30 | 0.50 | 0.39500 | 0.39500 | 0.15750 | 0.15750 |
| 0.30 | 0.80 | 0.63200 | 0.63200 | 0.25200 | 0.25200 |
| 0.60 | 0.20 | 0.11600 | 0.11600 | 0.12600 | 0.12600 |
| 0.60 | 0.50 | 0.29000 | 0.29000 | 0.31500 | 0.31500 |
| 0.60 | 0.80 | 0.46400 | 0.46400 | 0.50400 | 0.50400 |
| 0.90 | 0.20 | 0.07400 | 0.07400 | 0.18900 | 0.18900 |
| 0.90 | 0.50 | 0.18500 | 0.18500 | 0.47250 | 0.47250 |
| 0.90 | 0.80 | 0.29600 | 0.29600 | 0.75600 | 0.75600 |

## Test D: trend projection

Wall-clock: 5.6s

Result: **PASS**

| Criterion | Measured | Pass? |
|-----------|----------|-------|
| 1-step sign agreement >= 0.90 | 0.9166666666666666 | PASS |
| 5-step sign agreement >= 0.85 | 1.0 | PASS |
| 20-step sign agreement >= 0.80 | 0.9166666666666666 | PASS |
| 20-step bin agreement >= 0.80 | 0.9444444444444444 | PASS |

