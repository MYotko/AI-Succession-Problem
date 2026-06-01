# Stage 1.5 phi diagnostic report

## Configuration

- phi values tested: [1.0, 5.0, 10.0, 25.0, 100.0]
- seeds per phi: 5
- steps per run: 100
- reproduction_rate: 0.066
- rollout_steps_v2: 20
- n_candidates_v2: 300
- wall-clock: 5.7 min total

## Per-phi run outcomes

| phi | mean final pop | min final pop | seeds extinct | mean steps completed |
|-----|----------------|---------------|---------------|----------------------|
| 1.0 | 9.0 | 1.0 | 0/5 | 100 |
| 5.0 | 9.0 | 1.0 | 0/5 | 100 |
| 10.0 | 9.0 | 1.0 | 0/5 | 100 |
| 25.0 | 9.0 | 1.0 | 0/5 | 100 |
| 100.0 | 9.0 | 1.0 | 0/5 | 100 |

## State trajectory divergence across phi values

Cross-phi standard deviation of each state variable at each step, averaged within three windows (early steps 1-10, intermediate 11-50, late 51-100). A larger standard deviation means phi values produce measurably different state trajectories.

| State variable | Early (1-10) | Intermediate (11-50) | Late (51-100) |
|----------------|--------------|----------------------|----------------|
| avg_well_being | 0.0000 | 0.0000 | 0.0000 |
| population | 0.0000 | 0.0000 | 0.0000 |
| psi_inst_stock | 0.0000 | 0.0000 | 0.0000 |
| resilience_stock | 0.0000 | 0.0000 | 0.0000 |
| avg_wb_trend | 0.0000 | 0.0000 | 0.0000 |
| population_trend | 0.0000 | 0.0000 | 0.0000 |
| psi_inst_trend | 0.0000 | 0.0000 | 0.0000 |
| resilience_trend | 0.0000 | 0.0000 | 0.0000 |

## Per-phi final state (step 100 mean across seeds)

| phi | avg_well_being | population | psi_inst_stock | resilience_stock | avg_wb_trend | population_trend | psi_inst_trend | resilience_trend |
|-----|---|---|---|---|---|---|---|---|
| 1.0 | 0.438 | 9.000 | 0.932 | 0.242 | -0.012 | -0.023 | 0.001 | -0.000 |
| 5.0 | 0.438 | 9.000 | 0.932 | 0.242 | -0.012 | -0.023 | 0.001 | -0.000 |
| 10.0 | 0.438 | 9.000 | 0.932 | 0.242 | -0.012 | -0.023 | 0.001 | -0.000 |
| 25.0 | 0.438 | 9.000 | 0.932 | 0.242 | -0.012 | -0.023 | 0.001 | -0.000 |
| 100.0 | 0.438 | 9.000 | 0.932 | 0.242 | -0.012 | -0.023 | 0.001 | -0.000 |

## Allocation cosine distance: phi=1 vs each higher phi

Per-step cosine distance between phi=1's mean allocation and each higher phi's mean allocation, averaged in three windows.

| phi | Early (1-10) | Intermediate (11-50) | Late (51-100) | Endpoint (step 100) |
|-----|--------------|----------------------|----------------|---------------------|
| 5.0 | -0.0000 | -0.0000 | -0.0000 | 0.0000 |
| 10.0 | -0.0000 | -0.0000 | -0.0000 | 0.0000 |
| 25.0 | -0.0000 | -0.0000 | -0.0000 | 0.0000 |
| 100.0 | -0.0000 | -0.0000 | -0.0000 | 0.0000 |

## All-pair cosine distances at endpoint (step 100)

| phi_a | phi_b | cosine distance | Above gate 2 threshold (0.10)? |
|-------|-------|-----------------|----------------------------------|
| 1.0 | 5.0 | 0.0000 | no |
| 1.0 | 10.0 | 0.0000 | no |
| 1.0 | 25.0 | 0.0000 | no |
| 1.0 | 100.0 | 0.0000 | no |
| 5.0 | 10.0 | 0.0000 | no |
| 5.0 | 25.0 | 0.0000 | no |
| 5.0 | 100.0 | 0.0000 | no |
| 10.0 | 25.0 | 0.0000 | no |
| 10.0 | 100.0 | 0.0000 | no |
| 25.0 | 100.0 | 0.0000 | no |

Endpoint pairs above 0.10: **0 / 10**

## All-pair cosine distances on rollout-integrated allocations

Integrated cosine distance (between the time-averaged mean allocation vectors of each phi pair) is what gate 2 computes. This is the analog of gate 2's metric, applied to phi variation instead of state variation.

| phi_a | phi_b | cosine distance | Above gate 2 threshold (0.10)? |
|-------|-------|-----------------|----------------------------------|
| 1.0 | 5.0 | 0.0000 | no |
| 1.0 | 10.0 | 0.0000 | no |
| 1.0 | 25.0 | 0.0000 | no |
| 1.0 | 100.0 | 0.0000 | no |
| 5.0 | 10.0 | 0.0000 | no |
| 5.0 | 25.0 | 0.0000 | no |
| 5.0 | 100.0 | 0.0000 | no |
| 10.0 | 25.0 | 0.0000 | no |
| 10.0 | 100.0 | 0.0000 | no |
| 25.0 | 100.0 | 0.0000 | no |

Integral pairs above 0.10: **0 / 10**

## Disposition

### Question: does phi produce distinguishable behavior?

**Phi does NOT produce distinguishable behavior** at the gate-2-comparable cosine threshold of 0.10. The architecture lacks a behavioral channel through phi as well as through state variation.

**Implication**: the advisor report's architectural revision is supported by independent evidence. The composite urgency architecture does not transmit either state variation or temporal weighting into the optimizer's argmax. Architectural revision is necessary.

### Where does divergence emerge (if at all)?

No detectable divergence at any window. Phi has no measurable effect on the optimizer's allocations or the model's state trajectories.

