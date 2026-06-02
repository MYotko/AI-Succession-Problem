# Stage 1.8 Phase A integrity report

Overall: **FAIL**

## Configuration

- phi values: [1.0, 5.0, 10.0, 25.0, 100.0]
- seeds: 5, steps: 100, agents: 200
- composite urgency layer: retired (Stage 1.8)
- working_factor: STATE_ALLOCATION_MAPPING placeholder
- wall-clock: 3.9 min

## Criterion 1: no crashes, no NaN
- Crashes: 0 / 25
- NaN values: 0 / 25
- Result: **PASS**

## Criterion 2: demographic sustainability at default phi=10

- Final populations (seeds 0-4): [157, 110, 121, 178, 192]
- Mean: 151.6 (threshold: >= 60)
- Min:  110 (threshold: >= 30)
- Result: **PASS**

## Criterion 3: state responsiveness at default phi=10

Mean (across seeds) of per-run std for each state variable.
avg_wb, psi_inst_stock, resilience_stock must each exceed 0.05.

| State variable | Mean std | Threshold | Pass? |
|----------------|----------|-----------|-------|
| avg_wb | 0.0369 | > 0.05 | FAIL |
| psi_inst_stock | 0.0825 | > 0.05 | PASS |
| resilience_stock | 0.0282 | > 0.05 | FAIL |
| theta_capability | 0.0549 | informational | - |
| transfer_state | 0.0822 | informational | - |

Result: **FAIL**

## Criterion 4: phi behavioral channel preserved

Per-seed final pop range across phi values; need range > 15 in >= 3 of 5 seeds (Stage 1.6 metric).

| Seed | phi=1 | phi=5 | phi=10 | phi=25 | phi=100 | range | > 15? |
|------|-------|-------|--------|--------|---------|-------|-------|
| 0 | 187 | 187 | 157 | 146 | 135 | 52 | YES |
| 1 | 118 | 110 | 110 | 151 | 173 | 63 | YES |
| 2 | 121 | 121 | 121 | 168 | 168 | 47 | YES |
| 3 | 138 | 178 | 178 | 177 | 117 | 61 | YES |
| 4 | 147 | 181 | 192 | 172 | 162 | 45 | YES |

Seeds diverged: **5 / 5** (need >= 3). Result: **PASS**

## Per-seed final state snapshot (phi=10)

| Seed | final pop | avg_wb | psi | resilience | theta_capability | transfer_state |
|------|-----------|--------|-----|------------|-------------------|------------------|
| 0 | 157 | 0.797 | 0.921 | 0.372 | 0.716 | 0.935 |
| 1 | 110 | 0.781 | 0.961 | 0.429 | 0.708 | 0.954 |
| 2 | 121 | 0.790 | 0.932 | 0.356 | 0.723 | 0.936 |
| 3 | 178 | 0.818 | 0.959 | 0.437 | 0.679 | 0.940 |
| 4 | 192 | 0.783 | 0.957 | 0.377 | 0.728 | 0.942 |

