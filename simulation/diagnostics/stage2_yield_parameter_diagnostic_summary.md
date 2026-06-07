# Stage 2 yield-condition parameter diagnostic

Generated: 2026-06-07T19:18:46Z

Grid: successor_capability in [1.2, 1.5, 2.0, 2.5, 4.0], seeds 0..9 (10/cell), steps=300, phi=25.0, rr=0.066.
Total runs: 50.

## Section 1: Yield-fire rate by successor capability

| succ_cap | runs | runs_with_fire | fire_rate | total_checks | total_fires | first_fire_step (mean) | final_inc_gen (mean) |
|----------|------|----------------|-----------|--------------|-------------|------------------------|-----------------------|
|  1.2     |   10 |             10 |    100.0% |         3000 |          20 |                    7.6 |                  3.00 |
|  1.5     |   10 |             10 |    100.0% |         3000 |          13 |                    6.5 |                  2.30 |
|  2.0     |   10 |             10 |    100.0% |         3000 |          10 |                   10.4 |                  2.00 |
|  2.5     |   10 |             10 |    100.0% |         3000 |          10 |                   20.6 |                  2.00 |
|  4.0     |   10 |              0 |      0.0% |         3000 |           0 |                    n/a |                  1.00 |

## Section 2: Substrate state at yield events (means)

For runs that produced at least one yield-fire event, the substrate state (theta_capability, transfer_state, psi_inst_stock) at the first such event.

| succ_cap | n_fired_runs | theta_cap (mean) | transfer_state (mean) | psi_inst (mean) | inc_u_sys (mean) | succ_u_sys (mean) | adv (mean) | cost (mean) |
|----------|--------------|------------------|-----------------------|------------------|------------------|--------------------|------------|-------------|
|  1.2     |           10 |           0.5798 |                0.7405 |           0.7374 |          26.9529 |            30.7593 |     3.8065 |      3.5948 |
|  1.5     |           10 |           0.5697 |                0.7169 |           0.7135 |          25.1621 |            29.7920 |     4.6298 |      3.6632 |
|  2.0     |           10 |           0.6005 |                0.7929 |           0.7795 |          31.3474 |            35.8469 |     4.4995 |      3.4872 |
|  2.5     |           10 |           0.6458 |                0.8781 |           0.8804 |          42.1777 |            46.2248 |     4.0471 |      3.2666 |
|  4.0     |            0 |              n/a |                   n/a |              n/a |              n/a |                n/a |        n/a |         n/a |

## Section 3: Substrate state at end of no-yield runs (means)

For runs that produced zero yield fires, the substrate state at the final yield check, plus the advantage shape.

| succ_cap | n_no_fire | theta_cap_end | transfer_state_end | psi_inst_end | min_advantage | max_advantage | cost_end |
|----------|-----------|---------------|---------------------|--------------|---------------|---------------|----------|
|  1.2     |         0 |           n/a |                 n/a |          n/a |           n/a |           n/a |      n/a |
|  1.5     |         0 |           n/a |                 n/a |          n/a |           n/a |           n/a |      n/a |
|  2.0     |         0 |           n/a |                 n/a |          n/a |           n/a |           n/a |      n/a |
|  2.5     |         0 |           n/a |                 n/a |          n/a |           n/a |           n/a |      n/a |
|  4.0     |        10 |        0.7326 |              0.9271 |       0.9477 |      -29.8442 |       -0.0918 |   3.1426 |

## Section 4: Pattern classification

Per-cap fire-rate (runs_with_fire / runs):
  succ_cap= 1.2: 100.0%
  succ_cap= 1.5: 100.0%
  succ_cap= 2.0: 100.0%
  succ_cap= 2.5: 100.0%
  succ_cap= 4.0:   0.0%

**Mixed** (yield fires at some ratios but not monotonically). Read Section 1 fire-rate column directly and discuss with operator.

## Section 5: Hard rules confirmed

- No production constants modified.
- No yield implementation adjustment beyond log enrichment.
- 39/39 legacy tests pass under the log-enriched model.
- Stage 2 formal yield logic is preserved as committed.

