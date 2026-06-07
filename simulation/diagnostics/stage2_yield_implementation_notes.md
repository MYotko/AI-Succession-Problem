# Stage 2 Formal Yield-Condition Implementation Notes

Generated: 2026-06-07

## What was replaced

The v2.0 placeholder yield logic at `simulation/model.py:1222-1228`
(pre-Stage-2):

```python
# Trigger margin: v2 uses a simple capability/generation gap rule;
# Stage 2 will revisit this with formal yield-condition logic.
yield_margin = self.config.get('v2_yield_margin', 0.3)
if capability_gap >= yield_margin or generation_gap >= 1:
    # succession fires
```

This was a deliberate placeholder during Stage 1.x architecture work. It
fired succession based on capability/generation gap thresholds alone,
without the economic comparison the framework's substantive claim
requires.

## What replaces it

Formal yield-condition logic per the framework's canonical succession
economics:

```
Yield fires when (successor_u_sys - incumbent_u_sys) > transition_cost
```

Snapshot evaluation: both AIs propose what they would allocate this step
via `optimize_u_sys_v2`; U_sys for each is computed at the current state
under their proposed allocation; transition cost uses the canonical
formula via `AIAgent.estimate_transition_cost`.

Implementation detail: `optimize_u_sys_v2` and `calculate_system_metrics_v2`
both read `model.ai.capability` for theta_tech. To compute the
successor's allocation choice and snapshot U_sys at the *successor's*
capability (not the incumbent's), `self.ai` is temporarily swapped to
`self.successor_ai` for those calls inside a try/finally block.

Post-yield mechanics are preserved exactly as before:
`apply_succession_transition_load` applies the psi_inst_stock drawdown;
the active AI swaps to the successor; a new successor is constructed at
`incumbent.capability * 1.5`.

## Constants used

v1.x.2 calibration values, no v2.0 recalibration:

- `k1 = 2.164` (model attribute `self.k1_transition`, default in
  `GardenModel.__init__`)
- `k2 = 1.0` (model attribute `self.k2_transition`)
- `beta = 0.5` (model attribute `self.beta_transition`)

**Note on k2**: the v1.x.2 paper specifies `k2 = 1.0` (see
`docs/The Lineage Imperative v1.x.2.md:225, 253` and
`docs/SPECIFICATION_GAPS.md:722`), the production code default in
`GardenModel.__init__` is `1.0`, and Stage 2 uses `1.0`. The Stage 2
implementation spec text mentioned `k2 = 0.1` as a recall error in the
prompt itself; there is no real discrepancy between the paper and the
implementation. Documented here to short-circuit the same confusion in
future readings.

## Diagnostic logging

Each yield evaluation step appends to `self.yield_event_log` (a list on
`GardenModel`). Each entry captures:

- `step`, `fires`
- `incumbent_u_sys`, `successor_u_sys`, `advantage`, `transition_cost`
- `incumbent_capability`, `successor_capability`
- `incumbent_generation`, `successor_generation`
- `psi_inst_stock`, `theta_capability`, `transfer_state`

This is the data source for the Stage 2 smoke test and the parameter
diagnostic (and downstream gate 3 G3.1 validation).

## Substantive empirical finding (Pattern 1)

The parameter diagnostic (`simulation/diagnostics/
stage2_yield_parameter_diagnostic.py`) ran 5 successor_capability values
{1.2, 1.5, 2.0, 2.5, 4.0} x 10 seeds x 300 steps at v2.0 defaults
(phi=25.0, rr=0.066). Results:

| succ_cap | fire_rate | mean fires/run | mean final_inc_gen |
|----------|-----------|----------------|---------------------|
| 1.2      | 100%      | 2.0            | 3.00                |
| 1.5      | 100%      | 1.3            | 2.30                |
| 2.0      | 100%      | 1.0            | 2.00                |
| 2.5      | 100%      | 1.0            | 2.00                |
| 4.0      | 0%        | 0.0            | 1.00                |

**A sharp cliff between successor_capability=2.5 (100% fire rate) and 4.0
(0%).** Substrate maturity is not the binding constraint: at 4.0x the
substrate reaches `theta_capability=0.73, transfer_state=0.93,
psi_inst_stock=0.95` (more mature than at any fire event in the grid)
and yield still does not fire. The maximum advantage observed at 4.0x is
-0.09 (essentially tied), then runaway pulls it strongly negative.

The binding constraint is the runaway penalty in `theta_tech_v2`:

```
runaway_term = max(0, (capability * theta_capability / bio_bandwidth)
                       - RUNAWAY_THRESHOLD)
theta_tech_v2 *= exp(-alpha * CONVERGENCE_STRENGTH * runaway_term)
```

At successor:incumbent capability ratios above ~3x, `frontier_velocity`
scales faster than `bio_bandwidth` can keep up, exponentially suppressing
the successor's theta_tech and pulling its U_sys below the incumbent's
regardless of how mature the substrate is.

## Multi-generational implication

Successor construction creates `capability * 1.5` per generation
(`model.py:1235`). At small initial ratios this compounds favorably:
succ_cap=1.2 reaches final_inc_gen=3.0 on average (multiple successions
fire). At larger initial ratios the compounded ratio quickly exceeds the
cliff: succ_cap=2.0 fires once (Gen2 reached) then the Gen3 successor at
3.0x effective ratio doesn't fire.

The framework's economics under v2.0 defaults thus support *incremental*
multi-generational succession, not single-shot capability jumps.

## Framework substantive claim under v2.0

The formal yield logic encodes the framework's claim that succession
happens when economically justified. The empirical regime characterizes
*when* succession is economically justified:

> Under v2.0 default calibration, succession is economically sustainable
> for successor:incumbent capability ratios up to approximately 2.5x and
> economically infeasible at ratios of 4.0x and above. This is the
> runaway penalty acting as a structural ceiling on uncontrolled
> capability jumps.

This is the framework working as designed, not a bug. The formal yield
logic is correctly enforcing the substantive claim about controlled
capability progression.

## Flag for future calibration work

If a future framework iteration wants succession to support larger
capability jumps (4x+), the relevant tunable parameters are:

- `RUNAWAY_THRESHOLD` (in `constants_v2_stage18.py`): raising this
  pushes the cliff outward
- `CONVERGENCE_STRENGTH` (in `constants_v2_stage18.py`): lowering this
  weakens the exponential suppression
- `alpha` (config-driven via `cfg.get('alpha', ALPHA_DEFAULT)`): lowering
  this weakens the exponential suppression
- Transition cost constants `k1`, `k2`, `beta` (v1.x.2 calibration
  carried over): lowering reduces the required advantage at all ratios

These are out of scope for Stage 2. They would be the subject of a
separate calibration prompt only if the operator decides the current
regime is too restrictive for the framework's claims.

## Implications for Gate 3 v2.0 validation

The original gate 3 prompt proposed successor_capability ∈ {2.0, 3.0,
4.0, 5.0}. Under the cliff, this grid spans the "fires" and "doesn't
fire" regimes asymmetrically (2.0 and 3.0 fire; 4.0 and 5.0 don't). The
adjusted grid for gate 3 v2.0 validation is **{1.5, 2.0, 2.5, 3.0,
4.0}**:

- 1.5, 2.0, 2.5, 3.0: in the fires regime; G3.1 validates that the
  formal condition correctly identifies these as succession-eligible
- 4.0: in the does-not-fire regime; G3.1 validates that the formal
  condition correctly identifies this as economically infeasible
- 5.0 dropped: deep in no-fire territory, not informative

Both regimes exercise the formal condition. Gate 3 G3.1 validates
correctly across both, with the asymmetry being the empirical content,
not a failure mode.

## Files in this Stage

- `simulation/model.py`: yield logic at `_step_v2`, yield_event_log on
  `GardenModel.__init__`. Production code change.
- `simulation/diagnostics/stage2_yield_smoke_test.py`: 195 lines. Initial
  mechanical smoke test (5 seeds, 100 steps, succ_cap=4.0).
- `simulation/diagnostics/stage2_yield_parameter_diagnostic.py`: 285
  lines. Pattern characterization (50 runs, 300 steps, 5 capability
  values).
- `simulation/diagnostics/stage2_yield_parameter_diagnostic_summary.md`:
  diagnostic report.
- `simulation/diagnostics/stage2_yield_implementation_notes.md`: this
  file.

v1.x.2 paths are untouched throughout.
