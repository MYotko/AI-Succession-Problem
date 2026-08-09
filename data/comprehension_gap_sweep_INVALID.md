# INVALID: comprehension_gap_sweep.csv

Date of this notice: 2026-08-09
Applies to: `data/comprehension_gap_sweep.csv`, 2,800 rows

## Status

**This dataset is invalid and must not be cited for any conclusion about the
comprehension gap.** The figures in it stand as recorded. Nothing in the CSV has
been altered, and it is retained deliberately as the historical record of the
defect. It is superseded by
`data/comprehension_gap_sweep_v2_capability_coupled.csv` once that run is
approved and executed.

## The defect

Two independent faults, either sufficient on its own to invalidate the run.

**Opacity was scripted against time, not capability.** The `gradual_opacity`
policy set `current_opacity = min(0.95, opacity_rate * step)`, a pure function
of step count with no capability term. Since `convergence_strength` acts on
capability, it could not affect opacity by construction. Every row reports
`max_opacity_reached = 0.8940`, which is exactly `0.003 * 298`. The sweep's
independent variable could not move its dependent variable.

**`convergence_strength` was inert regardless.** It appears only as a multiplier
on `runaway_term` inside `exp(-alpha * convergence_strength * runaway_term)`,
and that term is identically zero in this configuration because the frontier to
bandwidth ratio, between 0.2 and 0.5, never approaches the default runaway
threshold of 1.5. Verified: at the same seed, `cs=0.0` and `cs=2.0` produce
bit-identical L_t and population trajectories.

## Why the recorded numbers look reassuring but mean nothing

The run reports zero collapses and zero extinctions across all 2,800 rows, with
all runs surviving at a mean final population of 762.5. That looks like a
protective equilibrium. It is not evidence of one. The instrument never
demonstrated it could produce a collapse at all, so a null result is
indistinguishable from a broken measurement. The sweep had no positive controls,
which is the specific gap that made this indistinguishable.

The apparent symmetry between defended and undefended collapse rates in this
dataset is symmetry at zero, produced by the absence of any collapse anywhere.
It was cited as evidence for a symmetric-collapse claim about Opaque Reasoning.
That claim is withdrawn: no live dataset supports it, the v1.x phi artifact
shows a 56.67 to 68.33 point asymmetry at every phi, and the v2.0 revalidation
shows Opaque Reasoning fully blocked defended, 0.0 percent against 100.0 percent
undefended.

## What remains usable

Only the fact of the defect. The `max_opacity_reached` column is a useful
fingerprint, since its constancy at 0.8940 is the signature of the
time-scripting fault. No outcome column supports any inference about the
defense, the comprehension gap, or the convergence forces.

## References

- `simulation/diagnostics/comprehension_gap_redesign_note.md`, root cause,
  redesign, and predefined discrimination criteria
- `simulation/diagnostics/defended_collapse_discrepancy_report.md`, anomaly B3,
  where the constancy was first noticed
