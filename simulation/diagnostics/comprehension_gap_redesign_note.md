# Comprehension Gap Sweep: Redesign and Predefined Discrimination Criteria

Date: 2026-08-09
Status: **requires operator sign-off before the full run**
Branch: `comprehension-gap-rerun`

This note is written before any data from the redesigned sweep exists. The
discrimination criteria in section 4 are fixed in advance precisely so that they
cannot be adjusted after seeing results. If the observed pattern matches none of
them, the correct outcome is "inconclusive," not a new criterion.

## 1. What was wrong with the original instrument

Two independent defects, either of which alone invalidates the sweep.

**Defect 1: opacity was scripted against time.** `agents.py` set
`self.current_opacity = min(0.95, opacity_rate * step)`, a pure function of step
count with no capability term. `convergence_strength` constrains capability, so
it could not affect opacity by construction. Every one of the 2,800 rows
reported `max_opacity_reached = 0.8940`, which is exactly `0.003 * 298`.

**Defect 2: convergence_strength was inert regardless.** It appears in exactly
one place, multiplying `runaway_term` inside
`exp(-alpha * convergence_strength * runaway_term)`. With
`runaway_term = max(0, frontier_velocity / bio_bandwidth - runaway_threshold)`
and a default threshold of 1.5, the term is identically zero in this
configuration. Verified directly: with the same seed, `cs=0.0` and `cs=2.0`
produce **bit-identical** L_t and population trajectories. The measured ratio
sits between 0.2 and 0.5, roughly a seventh of the default boundary.

Defect 2 matters because fixing Defect 1 alone would not have helped. Capability
is set at construction and changes only at succession, and
`final_ai_generation` was 1 in all 2,800 rows. Coupling opacity to capability
without addressing Defect 2 swaps a time-scripted constant for a
capability-scripted constant and produces a flat sweep at a different value.

## 2. What changed

**Opacity coupling.** Opacity now accumulates in proportion to
`capability * recent_L_t / opacity_reference_l_t`. L_t carries `theta_tech`,
which carries the `alpha * convergence_strength * runaway_term` penalty, so a
strong governance speed limit slows opacity growth instead of leaving it on a
clock. Capability is included explicitly so that generational growth enters
automatically if it is ever enabled for this policy.

**Runaway threshold.** Lowered from 1.5 to 0.2 via configuration.

### The threshold change is a redefinition, and it qualifies every result

The faithful remedy would be to let capability grow through succession until the
frontier genuinely outran biological bandwidth, leaving the runaway boundary
where it is. That route was tested and is closed:

- Succession never fires as configured, because `successor_ai` defaults to
  `None` (`model.py:250`) and the sweep never supplies one, so the yield block
  at `model.py:767` is skipped entirely. Lowering the transition cost to 0.001
  changes nothing.
- When a successor *is* supplied, succession fires nine times and capability
  compounds to 38.4x, which is more than enough. But `model.py:848` constructs
  every subsequent successor with a hardcoded `policy='optimize_u_sys'`, so the
  policy under test is replaced after the first succession and
  `max_opacity_reached` collapses to the default 0.1.

Retaining `gradual_opacity` across successions requires editing shared model
code, which is outside this task's scope and triggers its stop condition.

So the boundary was moved instead. **A result obtained at
`runaway_threshold = 0.2` is a result about a differently-defined runaway
boundary.** That qualification must travel with every figure taken from this
sweep, and no figure from it should be cited as characterizing the framework at
its default parameters. Whether this trade is acceptable is an operator
decision, and it is the main thing this note asks to be signed off.

## 3. Instrument validation, before the full run

The redesigned coupling responds to `convergence_strength`, at 300 steps, seed
12345, undefended, `opacity_defense_threshold = 0.5`:

| runaway_threshold | cs=0.0 | cs=0.5 | cs=1.0 | cs=2.0 | spread |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 1.5 (default) | 0.9082 | 0.9082 | 0.9082 | 0.9082 | 0.0000 |
| 0.2 (adopted) | 0.9082 | 0.8166 | 0.7351 | 0.5978 | 0.3104 |
| 0.05 | 0.9082 | 0.7466 | 0.6145 | 0.4179 | 0.4902 |

The response is monotonic in the right direction: a stronger speed limit yields
lower peak opacity. The step at which opacity crosses the defense threshold
moves later as cs rises (183, 194, 209, 245 at threshold 0.2), and at
`runaway_threshold = 0.05, cs = 2.0` the threshold is never crossed at all.

Note that the default row is still flat. That is the correct result, not a
failure: it is the direct measurement of Defect 2.

## 4. Predefined discrimination criteria

Fixed before data exist. "Defense effect" means the undefended minus defended
difference in collapse rate within a cell.

### Precondition: the run is void unless the positive controls collapse

Undefended control cells run at `reproduction_rate = 0.045`, below the
extinction boundary. If they do not collapse, the instrument is not producing
the outcome it measures and **no interpretation may be drawn**, whatever the
main grid shows. This is the check the original lacked: it reported zero
collapses in all 2,800 rows and could not distinguish a protective equilibrium
from a broken measurement.

### Supports Interpretation 1, the COP ceiling

The defense is ineffective once reasoning outruns comprehension. All of:

1. `max_opacity_reached` exceeds `opacity_defense_threshold` in a majority of
   cells at every convergence_strength, including the highest.
2. The defense fires (`defense_fired_count > 0`) in those cells.
3. The defense effect is under 5 percentage points in the high-opacity cells,
   and does not grow as opacity rises.

The signature is a defense that engages and does not help.

### Supports Interpretation 2, the productive band

The convergence forces keep the system comprehensible, so the defense is rarely
tested. All of:

1. `max_opacity_reached` falls monotonically as convergence_strength rises, and
   at the highest convergence_strength it stays below the defense threshold in a
   majority of cells (`step_opacity_exceeded_threshold == -1`).
2. Where opacity does exceed the threshold, at low convergence_strength, the
   defense effect is at least 10 percentage points.
3. Collapse rates are near zero at high convergence_strength in both defense
   states, and the near-zero is accompanied by opacity never crossing the
   threshold rather than by nothing happening at all.

The signature is a defense that is rarely needed and works when it is.

### Inconclusive

Any of:

1. Positive controls do not collapse. Void, as above.
2. Opacity responds to convergence_strength but no cell in the grid produces
   collapse in either defense state. The sweep then shows the gap can be gated
   but says nothing about whether the defense matters, which is the failure mode
   of the original run.
3. Opacity crosses the threshold and the defense fires, but the defense effect
   sits between 5 and 10 percentage points, or has inconsistent sign across
   opacity_defense_threshold values.
4. The defense effect is large but does not vary with opacity, which would
   indicate the effect comes from something other than the comprehension gap.

Outcome 3 is a genuine possibility and should be reported as inconclusive rather
than argued into one of the two readings.

## 5. Output artifacts

- Full run: `data/comprehension_gap_sweep_v2_capability_coupled.csv`
- Smoke: `data/smoke_comprehension_gap_sweep_v2_capability_coupled.csv`

Neither name uses the `full_5ac6a2e_` manifest prefix, so manifest-based
exclusion continues to hold, and the smoke output is separately named so it
cannot be mistaken for the full run.

`data/comprehension_gap_sweep.csv` is never overwritten. It is the historical
record of the defect and carries a dated invalidity note alongside it.

## 6. Sign-off required

Two items:

1. The `runaway_threshold` redefinition in section 2, and the qualification it
   forces onto every downstream figure.
2. The discrimination criteria in section 4, before any data exist.

The full sweep should not be launched until both are confirmed.
