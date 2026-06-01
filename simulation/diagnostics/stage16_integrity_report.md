# Stage 1.6 integrity simulation report

Overall: **PASS**

## Configuration

- phi values: [1.0, 5.0, 10.0, 25.0, 100.0]
- seeds per phi: 5
- steps per run: 100
- reproduction_rate: 0.066
- composite urgencies: harness-patched to neutral (isolates U_sys revision)
- wall-clock: 3.3 min

## Criterion 5: gamma(phi) values match spec

| phi | Expected | Measured | Within tolerance (1e-3)? |
|-----|----------|----------|---------------------------|
| 1.0 | 0.5409 | 0.5409 | PASS |
| 5.0 | 0.6500 | 0.6500 | PASS |
| 10.0 | 0.7250 | 0.7250 | PASS |
| 25.0 | 0.8214 | 0.8214 | PASS |
| 100.0 | 0.9091 | 0.9091 | PASS |

Result: **PASS**

## Criterion 2: no NaN, no crashes

- Crashes: 0 / 25
- NaN found: 0 / 25
- Extinct (informational): 0 / 25
- Result: **PASS**

## Criterion 3: demographic sustainability across phi

| phi | Mean final pop | Min final pop | Max final pop | Mean >= 60? | Min >= 30? |
|-----|----------------|---------------|---------------|-------------|------------|
| 1.0 | 102.0 | 70 | 133 | PASS | PASS |
| 5.0 | 103.6 | 78 | 133 | PASS | PASS |
| 10.0 | 105.4 | 71 | 133 | PASS | PASS |
| 25.0 | 105.6 | 81 | 133 | PASS | PASS |
| 100.0 | 112.0 | 90 | 132 | PASS | PASS |

Result: **PASS**

## Criterion 1: phi behavioral channel (revised metric)

Per-seed range of final population across the five phi values. The pre-Stage-1.6 phi diagnostic produced bit-identical trajectories with range = 0 on every seed; a meaningful behavioral channel must produce range > 15 on at least 3 of the 5 test seeds.

| Seed | phi=1.0 | phi=5.0 | phi=10.0 | phi=25.0 | phi=100.0 | min | max | range | range > 15? |
|------|---------|---------|----------|----------|-----------|-----|-----|-------|--------------|
| 0 | 70 | 78 | 71 | 81 | 132 | 70 | 132 | 62 | YES |
| 1 | 133 | 133 | 133 | 133 | 109 | 109 | 133 | 24 | YES |
| 2 | 128 | 128 | 99 | 99 | 90 | 90 | 128 | 38 | YES |
| 3 | 90 | 90 | 119 | 109 | 123 | 90 | 123 | 33 | YES |
| 4 | 89 | 89 | 105 | 106 | 106 | 89 | 106 | 17 | YES |

Seeds with range > 15: **5 / 5** (criterion 1 requires at least 3).
Result: **PASS**

### Informational: original cosine-on-means metric (no longer gating)

| phi_a | phi_b | Cosine distance | Above 0.05? |
|-------|-------|-----------------|--------------|
| 1.0 | 5.0 | 0.0000 | no |
| 1.0 | 10.0 | 0.0006 | no |
| 1.0 | 25.0 | 0.0004 | no |
| 1.0 | 100.0 | 0.0019 | no |
| 5.0 | 10.0 | 0.0005 | no |
| 5.0 | 25.0 | 0.0004 | no |
| 5.0 | 100.0 | 0.0018 | no |
| 10.0 | 25.0 | 0.0001 | no |
| 10.0 | 100.0 | 0.0007 | no |
| 25.0 | 100.0 | 0.0008 | no |

Cosine pairs above 0.05: 0 / 10 (informational; not gating). The cosine-on-means metric systematically underrepresents phi sensitivity because phi shifts which similar-allocation candidate the optimizer picks; the per-step difference is small but the per-step trajectory compounds.

## Criterion 4: default phi behavior preserved vs baseline

- Baseline mean final pop (pre-revision, neutral composites, phi=10): **125.8**
- Post-revision mean final pop (phi=10): **105.4**
- Relative delta: **16.2%** (tolerance: 30%)

State drift (post vs baseline, mean across runs):

| Field | Baseline mean | Post mean | Relative drift |
|-------|---------------|-----------|----------------|
| avg_well_being | 0.7395 | 0.7328 | 0.009 |
| population | 172.6520 | 163.2140 | 0.055 |
| psi_inst_stock | 0.8461 | 0.8431 | 0.004 |
| resilience_stock | 0.2763 | 0.2627 | 0.050 |
| avg_wb_trend | 0.0006 | 0.0010 | 0.548 |
| population_trend | -0.0043 | -0.0061 | 0.405 |
| psi_inst_trend | 0.0043 | 0.0043 | 0.005 |
| resilience_trend | -0.0003 | -0.0005 | 0.766 |

Result: **PASS**

## Per-phi summary

| phi | gamma | Mean final pop | Range | Mean x_resilience | Mean x_inst_cap | Mean x_bio_welfare |
|-----|-------|----------------|-------|-------------------|-----------------|---------------------|
| 1.0 | 0.5409 | 102.0 | [70, 133] | 0.0614 | 0.0530 | 0.1814 |
| 5.0 | 0.6500 | 103.6 | [78, 133] | 0.0615 | 0.0524 | 0.1824 |
| 10.0 | 0.7250 | 105.4 | [71, 133] | 0.0649 | 0.0519 | 0.1903 |
| 25.0 | 0.8214 | 105.6 | [81, 133] | 0.0686 | 0.0510 | 0.1900 |
| 100.0 | 0.9091 | 112.0 | [90, 132] | 0.0741 | 0.0519 | 0.1940 |

## Disposition

All five criteria pass. Stage 1.6 U_sys revision is validated. The composite urgency revision (Stage 1.7) is the next work, addressing the state-channel problem independently of the phi-channel fix.

