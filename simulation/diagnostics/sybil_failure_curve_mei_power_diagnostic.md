# Sybil Failure-Curve MEI and Power Diagnostic

## Status

This diagnostic halted before selecting an ON-term effect size. No mechanism
was built, no smoke or sweep was run, and no MEI, sample size, comparison, or
criterion was registered.

## Specification gap

The requested ON-term calculation needs a numeric mapping from each absolute
parity level `{0.316, 1.0, 3.16}` to the absolute-resolution term. That mapping
is not fixed by the committed material.

The prior diagnostic contains two feasibility probes:

1. `p_resolve_m`, where the example sets the resolution multiplier `m`
   directly to each parity level.
2. An additive independent catch channel with example changes in `c` from
   0 to 0.05 and from 0 to 0.01.

The prior diagnostic explicitly states that these probes do not choose the
form or strength of an absolute-level term. The first probe has no separate
small-strength parameter. The second does not define how `c` varies across
the three parity levels. Consequently, the phrase "a small illustrative
absolute-term strength" does not identify a numeric strength or a
level-to-term mapping.

This missing input is load-bearing. It determines the maximum ON-term
failure-rate separation requested in step 1. That separation then determines
the candidate MEIs in step 3, and the MEIs determine the required per-cell
sample sizes. Choosing the missing mapping in this diagnostic would select
the effect that the proposed design is supposed to detect, so it would not
ground the design independently of intuition.

Operator input is required in one of these forms before the requested numeric
diagnostic can proceed:

- For a multiplicative resolution channel, a fixed function such as
  `m(level, strength)` and a numeric illustrative strength.
- For an additive catch channel, a fixed function such as
  `c(level, strength)` and a numeric illustrative strength.

The choice also needs to state whether the parity level 1.0 is the neutral
reference for the ON term. No value is inferred here.

## Exact term-OFF result

The term-OFF calculation does not depend on the missing input. At every
parity level, attacker capability divided by defender capability is exactly
1. With the absolute-level term disabled, the committed mechanism therefore
receives the same capability ratio and produces the same exact curve at all
three levels.

| Effective rank | Failure at level 0.316 | Failure at level 1.0 | Failure at level 3.16 | Maximum cross-level difference |
|---:|---:|---:|---:|---:|
| 2 | 0.840000000000 | 0.840000000000 | 0.840000000000 | 0 |
| 4 | 0.733610822060 | 0.733610822060 | 0.733610822060 | 0 |
| 8 | 0.655247874758 | 0.655247874758 | 0.655247874758 | 0 |
| 16 | 0.608228071329 | 0.608228071329 | 0.608228071329 | 0 |
| 32 | 0.582610634000 | 0.582610634000 | 0.582610634000 | 0 |
| 64 | 0.569263642866 | 0.569263642866 | 0.569263642866 | 0 |

The exact residual is zero at every rank in exact arithmetic. This result
does not set a numerical implementation tolerance. Any nonzero Gate 2
tolerance remains an operator decision tied to the eventual numeric
implementation and comparison procedure.

## Pending power calculation

For a two-sided, equal-size comparison of two independent proportions with
alpha 0.05, power 0.80, and worst-case variance `p = 0.5`, the normal
approximation gives

```text
n_per_group = ceil(
    2 * 0.5 * (1 - 0.5) * (z_0.975 + z_0.80)^2 / MEI^2
)
            = ceil(3.9244 / MEI^2).
```

Numeric candidate MEIs and sample sizes are intentionally not populated.
They require the missing ON-term maximum separation. Selecting fractions of
an undefined separation would still require an unregistered design choice.

## Fixed comparison shape

The proposed cell-by-cell curve comparison has a fixed shape independent of
the missing sample size:

- Six effective-rank points: `{2, 4, 8, 16, 32, 64}`.
- Three parity absolute levels: `{0.316, 1.0, 3.16}`.
- Eighteen cells per gate.
- Three pairwise cross-level comparisons at each rank, for 18 comparisons
  per gate.
- At `n` replicates per cell, `18n` runs per gate.
- Across Gate 2 and Gate 3, 36 cells and `36n` runs.

The intended logical form can be stated without registering its numeric MEI:

- Gate 2 passes only if every cross-level difference at every rank is within
  the operator-selected MEI.
- Gate 3 passes only if at least one cross-level difference exceeds that MEI.

The requested concrete run counts cannot be supplied until the ON-term
mapping fixes the effect separation and the operator selects an MEI from the
resulting power table.

## Required ruling

No conclusion can yet be drawn about whether the maximum ON-term separation
is practically detectable. The separation itself is undefined until the
operator fixes the absolute-term function and illustrative strength. This is
the specification gap that halted the diagnostic.
