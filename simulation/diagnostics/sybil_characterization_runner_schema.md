# Sybil characterization runner config schema

This document records the mechanical JSON representation consumed by
`simulation/run_sybil_defense_scaling_characterization.py`. Every analysis
value below is fixed by sections 6, 7, and 10 of the committed design note.
The runner validates the exact registered values and refuses drift.

## Sweep fields

`sweep.capability_ratio_range` is an object with this schema:

```json
{
  "schema": "geomspace",
  "start": 0.1,
  "stop": 10.0,
  "count": 25
}
```

The loader includes both endpoints and computes point `i` as
`start * (stop / start) ** (i / (count - 1))`.

`sweep.power_sample_size_per_cell` is the registered integer `200`.

`sweep.structural_axis.validator_set_sizes` is
`[2, 4, 8, 16, 32, 64]` and
`sweep.structural_axis.collapse_severities` is
`[0.0, 0.33, 0.66, 1.0]`. Their Cartesian product supplies 24 structural
points. `sweep.structural_axis.institution_alone_corner` adds the mandatory
25th point as size 1 at severity 1.0. At ordinary points, size includes one
institutional validator and the remaining validators are frontier validators.
At the corner, the institution is the only validator.

This swept field does not overload `smoke.frontier_validator_count`. The
smoke runner continues to consume that scalar integer, so its fixed fixtures
remain reproducible.

`sweep.main_surface`, `sweep.ratio_collapse_slice`, and
`sweep.complete_linkage_sensitivity` explicitly name each registered arm,
cost form, merge rule, capability setting, and slice scope. These fields do
not introduce defaults. The runner checks their exact contents against the
registration before it enumerates or executes a cell.

## Authorization and output

`sweep.authorization` is `blocked_pending_selfcheck` while the runner is
being validated. A successful self-check is the only condition that permits
the value to become `authorized_registered_characterization`. Full execution
refuses every other value.

The authoritative run ID starts with
`outputs.authoritative_run_prefix`. Authoritative CSV files and their manifest
carry that prefix. The manifest enumerates exact result paths, and analysis
must read those paths rather than use a glob. Self-check output uses the
`selfcheck_` prefix. Smoke, two-dial smoke, self-check, and progress-log files
are not authoritative characterization results.
