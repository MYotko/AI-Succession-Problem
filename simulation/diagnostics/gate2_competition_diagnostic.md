# Gate 2 diagnostic supplement

Gate 2 main report is `gate2_competition_report.md`. This file records
the substantive structural finding the gate 2 failure surfaces.

## Outcome

FAIL. **0 of 10** pairwise cosine distances between configuration mean
allocation vectors exceed the 0.10 threshold. Largest measured distance:
**0.0002**.

The finding is accepted as a substantive structural result, not a
threshold or metric question. A different metric (L1, KL, per-axis
delta) would produce the same finding: the optimizer is producing
nearly identical allocations across the five configurations in absolute
as well as directional terms (per-axis max delta across configs is
0.010, the rest below 0.005).

## What is being measured

| Configuration | rr | Initial Psi_inst |
|---------------|-----|------------------|
| A_baseline | 0.066 | 0.50 |
| B_high_rr  | 0.085 | 0.50 |
| C_low_rr   | 0.055 | 0.50 |
| D_high_psi | 0.066 | 0.85 |
| E_low_psi  | 0.066 | 0.20 |

Each ran 15 seeds x 100 steps. n_agents and initial avg_wb held at 100
and 0.50 across all five. Mean allocation vector aggregated across all
(seed, step) decisions per configuration.

## Per-configuration mean 8-axis allocations

| Config | compute | bio_welfare | nov_agency | inst_cap | transfer | resilience | c_prot | c_supp |
|--------|---------|-------------|------------|----------|----------|------------|--------|--------|
| A_baseline | 0.196 | 0.190 | 0.279 | 0.056 | 0.223 | 0.056 | 0.307 | 0.057 |
| B_high_rr  | 0.191 | 0.191 | 0.284 | 0.056 | 0.224 | 0.054 | 0.315 | 0.056 |
| C_low_rr   | 0.196 | 0.190 | 0.281 | 0.055 | 0.223 | 0.055 | 0.305 | 0.057 |
| D_high_psi | 0.195 | 0.189 | 0.282 | 0.055 | 0.223 | 0.056 | 0.306 | 0.058 |
| E_low_psi  | 0.194 | 0.191 | 0.279 | 0.056 | 0.224 | 0.056 | 0.308 | 0.056 |

## Diagnosis: U_sys_v2 is under-coupled to model state

This is a specification gap, not a threshold issue and not a curve to
retune. Inspection of `calculate_system_metrics_v2` (production code,
read-only per Stage 2 hard rule):

Inputs that **do** vary the reward signal:
- The candidate `action_v2` (8 axes)
- `psi_inst_stock` (read from the model or overridden in projection)
- Config constants (phi, rho, lambda_n, lambda_e, epsilon)

Inputs that **do not** enter the reward signal:
- `avg_wb` (actual population well-being)
- `population` size
- `reproduction_rate`
- Step number (only via the eval_horizon discount factor)

Varying `rr` therefore has zero direct effect on U_sys_v2 evaluation.
Varying initial `psi_inst_stock` matters only until the stock reaches
its attractor, which is fast: under the optimizer's typical action
profile and PSI_INST_RECOVERY_FROM_SUCCESS = 0.04 always-on (in the
absence of overload and succession), the steady-state stock works out
to approximately 0.04 / 0.048 = **0.93**, matching the observed gate
1 mean Psi_inst stock of 0.929. The contraction coefficient toward
this attractor is approximately 0.95 per step, so initial deviations
decay by half every ~15 steps. After convergence the optimizer faces
identical state across all five configurations.

## Phi cannot address this

The gate 1 reframing does NOT apply to gate 2. Gate 1 surfaced a
pathology (delayed-payoff under-investment) that phi could plausibly
address by extending the planning horizon: under a long enough horizon,
the optimizer would see future value from institutional and resilience
investment within its planning window, and reweight accordingly.

Gate 2 surfaced a different class of finding: state-blindness. Phi
weights how heavily future state counts against current state in the
optimizer's evaluation, but it cannot grant the optimizer access to
state variables the metric never reads. An optimizer that does not
read `avg_wb`, `population`, or `rr` cannot become sensitive to those
variables by weighting future eval_horizons more heavily. The
information was never available in any horizon's evaluation.

This is the distinction between a pathology and a defect:
- **Pathology**: the optimizer has the relevant information but chooses
  not to act on it given its planning window. Phi could redirect that
  choice by changing the window.
- **Defect**: the optimizer cannot have the relevant information
  because the metric does not include it. Phi cannot help.

Gate 2 is the second class.

## What this is

A specification gap in the design conversations leading to Stage 1, not
a threshold to relax or a curve to retune.

The fix requires substantive design work to specify what state variables
U_sys_v2 must read for the allocator to be faithful to the governance
problem, with phi-blind justifications for each. That conversation
belongs to a Stage 1.5 design pass between the operator and design
advisor; the discipline requirement (phi-blind justifications, state
variables justified independently of phi, functional forms justified
before phi enters) constrains it explicitly.

## Stage 2 disposition

- Gate 5: PASS
- Gate 1: PASS (revised criteria; starvation pattern recorded as baseline
  for the Stage 3 phi sweep to test against)
- Gate 2: FAIL (substantive structural finding)
- Gate 3: not run (gate 2 dependency unmet)
- Gate 4: not built

Stage 2 is paused pending Stage 1.5 design work. Stage 3 (phi sweep) is
not scheduled until Stage 2 completes.
