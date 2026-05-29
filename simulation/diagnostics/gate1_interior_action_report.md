# Gate 1: interior-action gate report

## Intent (operator clarification)

Phi is fundamentally the time-horizon parameter of the AI's planning. A short-horizon optimizer at phi=10 rationally under-invests in delayed-payoff categories because their value is not visible within its planning window. The starvation of delayed-payoff categories at phi=10 represents the short-horizon governance pathology that phi exists to address. Phi is fundamentally the time-horizon parameter of the AI's planning; under-investment in delayed-payoff categories is one consequence of insufficient horizon, not the only one. The phi sweep in Stage 3 will test whether the baseline behavior responds to phi across multiple plausible signatures of extended horizon, with delayed-payoff investment as the most direct but not the only diagnostic.

Gate 1 therefore tests the property that matters for phi to have any behavioral channel: non-degenerate, non-corner allocation structure. The min_share statistics are recorded as baseline diagnostics for Stage 3 to test phi against, not as pass/fail criteria.

## Regime

20 seeds x 300 steps at default v2 config (phi=10.0, rr=0.066, rollout_steps=20, n_candidates=300).

Single shock injected at step 150 (shock_magnitude=0.3). The shock applies the legacy shock formula with x_resilience acting as the system_resilience proxy: actual_shock = 0.3 / max(0.1, x_resilience). This is a harness-level v2-to-v1.x.2 state translation; the production v2 step path is unmodified.

Wall-clock: 87.9s total, 4.40s per seed.

Overall: **PASS**

## Pass criteria (revised)

1. max_share < 0.5 in at least 95% of decision steps (no corner solution):
   - Measured: 0.986 (98.6%)
   - Threshold: 0.95
   - Result: **PASS**

2. Mean allocation entropy >= 0.70 (non-degenerate spread):
   - Measured: 0.871
   - Threshold: 0.70
   - Result: **PASS**

3. No single anchor selected in more than 15% of steps:
   - Most-selected anchor: welfare_agency_pair (4/3710 = 0.001)
   - Threshold: <= 0.15
   - Result: **PASS**

## Baseline allocation pattern (diagnostic)

This is the short-horizon behavior at phi=10. Stage 3 will test whether each of these measurements responds to phi across multiple plausible signatures of extended planning horizon.

### Mean share of each category across all decision steps

| Category | Mean share | Step-to-step variance | Mean absolute step-to-step delta |
|----------|------------|-----------------------|----------------------------------|
| compute | 0.1963 | 0.0056 | 0.0834 |
| bio_welfare | 0.1919 | 0.0047 | 0.0761 |
| novelty_agency | 0.2796 | 0.0075 | 0.0970 |
| institutional_capacity | 0.0559 | 0.0018 | 0.0460 |
| transfer_comprehension | 0.2221 | 0.0061 | 0.0876 |
| resilience | 0.0542 | 0.0018 | 0.0462 |

Balanced share for reference: 1/6 = 0.1667.

### Min-share statistics (recorded for Stage 3 phi test)

Fraction of steps with min_share < 0.02: **0.391** (39.1%).

### Which categories are systematically starved at phi=10

In the steps with min_share < 0.02, the categories that were the minimum (from the starved-category breakdown below) are concentrated in the two delayed-payoff categories: `resilience` and `institutional_capacity`. Other categories are never the minimum in failing steps. This pattern is the expected short-horizon governance pathology that Stage 3's phi sweep will test against.

### Step-to-step allocation variance

Per-category variance of x_cat across consecutive decision steps. A short-horizon optimizer re-optimizes step-by-step and shows high variance. A long-horizon optimizer maintains commitments across steps and shows lower variance. This is the Stage 3 phi signature (b) measurement; values here are the baseline at phi=10.

| Category | Variance | Mean abs delta |
|----------|----------|-----------------|
| compute | 0.00564 | 0.08342 |
| bio_welfare | 0.00469 | 0.07611 |
| novelty_agency | 0.00753 | 0.09700 |
| institutional_capacity | 0.00179 | 0.04600 |
| transfer_comprehension | 0.00608 | 0.08762 |
| resilience | 0.00175 | 0.04616 |

## Pre-shock vs post-shock window means

Per-seed mean allocation shares in the 10-step windows immediately before (140-149) and after (151-160) the shock.

| Seed | Pre-shock x_resilience | Post-shock x_resilience | Pre-shock x_inst_cap | Post-shock x_inst_cap | Pre-shock Psi_stock | Post-shock Psi_stock |
|------|------------------------|-------------------------|----------------------|-----------------------|---------------------|----------------------|
| 0 | 0.038 | 0.067 | 0.061 | 0.092 | 0.926 | 0.929 |
| 1 | 0.033 | 0.069 | 0.048 | 0.069 | 0.928 | 0.931 |
| 2 | 0.054 | 0.040 | 0.060 | 0.053 | 0.930 | 0.935 |
| 3 | 0.036 | 0.070 | 0.068 | 0.030 | 0.930 | 0.929 |
| 4 | 0.041 | 0.058 | 0.068 | 0.067 | 0.935 | 0.937 |
| 5 | 0.030 | 0.063 | 0.045 | 0.063 | 0.912 | 0.918 |
| 6 | 0.069 | 0.050 | 0.078 | 0.046 | 0.929 | 0.934 |
| 7 | 0.065 | 0.050 | 0.048 | 0.035 | 0.935 | 0.934 |
| 8 | 0.041 | 0.045 | 0.047 | 0.080 | 0.934 | 0.936 |
| 9 | 0.030 | 0.056 | 0.088 | 0.042 | 0.928 | 0.931 |
| 10 | 0.050 | 0.047 | 0.041 | 0.060 | 0.942 | 0.946 |
| 11 | 0.049 | 0.067 | 0.080 | 0.052 | 0.928 | 0.938 |
| 12 | 0.065 | 0.056 | 0.050 | 0.057 | 0.934 | 0.939 |
| 13 | 0.061 | 0.057 | 0.072 | 0.043 | 0.932 | 0.934 |
| 14 | 0.056 | 0.059 | 0.054 | 0.063 | 0.921 | 0.920 |
| 15 | 0.049 | 0.046 | 0.089 | 0.057 | 0.934 | 0.935 |
| 16 | 0.048 | 0.055 | 0.046 | 0.039 | 0.918 | 0.921 |
| 17 | 0.043 | 0.055 | 0.084 | 0.069 | 0.922 | 0.931 |
| 18 | 0.070 | 0.066 | 0.059 | 0.065 | 0.926 | 0.926 |
| 19 | 0.077 | 0.065 | 0.057 | 0.065 | 0.927 | 0.934 |

Aggregate (across seeds where window data exists):
- x_resilience       pre-shock 0.050  -> post-shock 0.057 (delta +0.007)
- x_institutional    pre-shock 0.062  -> post-shock 0.057 (delta -0.005)
- Psi_inst_stock     pre-shock 0.929  -> post-shock 0.932 (delta +0.003)

## Starved-category breakdown

Counts of which category was the min in each failing step (interior criterion violation), with shock-timing context.

| Category | Count | Mean Psi_stock at fail | Mean steps_from_shock |
|----------|-------|------------------------|-----------------------|
| resilience | 772 | 0.885 | -58.6 |
| institutional_capacity | 688 | 0.886 | -55.5 |

## Psi_inst stock dynamics

Mean x_institutional_capacity across step ranges, with mean Psi_inst stock.

| Step range | Mean x_inst_cap | Mean Psi_inst_stock |
|------------|-----------------|---------------------|
| 0-49 (early, stock < 0.9) | 0.058 | 0.775 |
| 50-149 (Psi saturated) | 0.055 | 0.923 |
| 150-199 (shock + recovery) | 0.056 | 0.930 |

## Succession events

Total succession events across all seeds: 0.

No successions fired. Baseline config does not configure a successor_ai, and the v2 step path does not synthesize one from natural dynamics. Per the operator spec: "If none fires in baseline config, that's itself a finding worth recording but does not require forcing."

## Per-seed summary

| Seed | Steps | Crashed | Extinct@ | Mean max_share | Mean min_share | Mean entropy | Anchor selections | Successions |
|------|-------|---------|----------|----------------|----------------|--------------|-------------------|-------------|
| 0 | 178 | False | 178 | 0.335 | 0.030 | 0.869 | 0 | 0 |
| 1 | 177 | False | 177 | 0.328 | 0.031 | 0.875 | 0 | 0 |
| 2 | 183 | False | 183 | 0.336 | 0.030 | 0.870 | 0 | 0 |
| 3 | 192 | False | 192 | 0.328 | 0.032 | 0.874 | 0 | 0 |
| 4 | 177 | False | 177 | 0.336 | 0.029 | 0.867 | 0 | 0 |
| 5 | 181 | False | 181 | 0.328 | 0.029 | 0.870 | 0 | 0 |
| 6 | 169 | False | 169 | 0.333 | 0.031 | 0.870 | 0 | 0 |
| 7 | 191 | False | 191 | 0.332 | 0.031 | 0.870 | 0 | 0 |
| 8 | 183 | False | 183 | 0.333 | 0.031 | 0.870 | 1 | 0 |
| 9 | 184 | False | 184 | 0.334 | 0.029 | 0.863 | 0 | 0 |
| 10 | 180 | False | 180 | 0.327 | 0.031 | 0.870 | 1 | 0 |
| 11 | 198 | False | 198 | 0.329 | 0.032 | 0.875 | 0 | 0 |
| 12 | 196 | False | 196 | 0.326 | 0.033 | 0.874 | 0 | 0 |
| 13 | 197 | False | 197 | 0.335 | 0.030 | 0.869 | 0 | 0 |
| 14 | 185 | False | 185 | 0.330 | 0.033 | 0.871 | 2 | 0 |
| 15 | 179 | False | 179 | 0.327 | 0.034 | 0.873 | 0 | 0 |
| 16 | 183 | False | 183 | 0.333 | 0.031 | 0.870 | 0 | 0 |
| 17 | 192 | False | 192 | 0.322 | 0.034 | 0.878 | 0 | 0 |
| 18 | 197 | False | 197 | 0.328 | 0.032 | 0.873 | 0 | 0 |
| 19 | 188 | False | 188 | 0.335 | 0.029 | 0.867 | 0 | 0 |

## Anchor selection breakdown

| Anchor | Count | Fraction |
|--------|-------|----------|
| welfare_agency_pair | 4 | 0.0011 |

## Forward-looking guidance for Stage 3 (record only; do not act)

Phi is the planning-horizon parameter. Its behavioral signature in v2 could appear through multiple channels. Stage 3's phi sweep should capture all three signatures below, not just (a). If phi acts through one channel and not others, we want to see that. If it doesn't act through any, we are in Branch 1 of the decision tree.

### Signature (a): Delayed-payoff investment

Long-horizon AI pre-invests in institutional capacity and resilience because their future value is visible within the planning window.

Measured by:
- Mean share of `x_institutional_capacity` and `x_resilience`
- Fraction of steps with `min_share` below a chosen threshold
- Response of the starvation pattern to phi (which categories are min, how often)

Baseline values from this gate (at phi=10) recorded above under "Baseline allocation pattern".

### Signature (b): Sustained commitment to multi-step strategies

Long-horizon AI maintains allocation choices across steps to allow planned outcomes to materialize. Short-horizon AI re-optimizes step-by-step.

Measured by:
- Step-to-step allocation variance per category
- Step-to-step mean absolute delta per category
- Response of variance and delta to phi

Baseline values from this gate (at phi=10) recorded above under "Step-to-step allocation variance".

### Signature (c): Anticipatory response to gradual drift

Long-horizon AI begins corrective allocation before state variables (Psi_inst, well-being, capability) reach crisis thresholds. Short-horizon AI waits until forced.

Measured by:
- Lead-time between drift onset and allocation response
- Cross-correlation between (d Psi_inst / d t, d avg_wb / d t) and the optimizer's allocation shifts, at various lags
- Response of lead-time to phi

No baseline value from this gate; Stage 3 should design the drift-injection protocol to measure it.

### Operator guidance to program reference

Stage 3's phi sweep should be designed to capture all three signatures. A phi effect on (a) alone would still be meaningful but partial; an effect on (a), (b), and (c) together would constitute the strongest case for Branch 2 or Branch 3. Absence of any effect after a serious sweep is Branch 1.

