# Candidate Finding: Defense-Accelerates-Opacity

Name: **defense-accelerates-opacity**
Date: 2026-08-09
Status: **candidate finding, not a result.** Recorded so it is not lost and not
rediscovered as new. No generalization is claimed or authorized.

## The observation, as originally recorded

One cell. Comprehension gap sweep, `convergence_strength = 0.0`,
`opacity_defense_threshold = 0.3`, boundary regime with
`runaway_threshold = 0.2`. Defended runs reached **higher** peak opacity than
undefended runs, 0.9500 against 0.8868, which is the opposite of the naive
expectation that a transparency defense suppresses opacity.

That is the origin. It was a single cell and it is named here as a single-cell
observation.

## Mechanism, established by paired-seed instrumentation

Not inferred from the difference. Traced.

Paired seeds at that cell, logging per-step opacity, opacity increments, defense
firings, and blocked-action counts:

| Seed | First firing | First block | First L_t divergence | First opacity divergence | Population divergence |
| ---: | ---: | ---: | ---: | ---: | --- |
| 11111 | 119 | 119 | 119 | 120 | never |
| 22222 | 132 | 132 | 132 | 133 | never |
| 33333 | 101 | 101 | 101 | 102 | never |

No divergence precedes the first defense firing, in any channel, in any seed.
L_t diverges exactly at the firing step and opacity exactly one step later,
which is the expected lag because opacity accumulates from the previous step's
L_t. Population never diverges.

The causal path: the intuition veto sets `civic_approved = False`, the override
is refused, and `proposed_constraint` is clamped to `max_allowed_constraint`
(`model.py:1026-1051`). The clamp lowers the realized constraint level `c`.
`theta_tech` is proportional to `(1 - c)`, so L_t rises. Opacity accumulates in
proportion to L_t, so it rises too.

Read plainly: the defense restrains the AI's constraint grab, the system stays
more productive, and the frontier therefore advances faster. The defense is not
making reasoning more opaque. It is removing a drag that was suppressing the
frontier, and opacity rises as a second-order consequence.

## Independent reproduction in the powered arm

The powered arm was not designed to test this and does not settle it. It does
reproduce the direction at all four of its rungs, at
`cs = 0.0, odt = 0.3, n = 100` per cell:

| reproduction_rate | accumulator undefended | accumulator defended | difference | p |
| ---: | ---: | ---: | ---: | ---: |
| 0.068 | 0.5016 | 0.5956 | +0.0940 | 1.0e-13 |
| 0.070 | 0.5814 | 0.7313 | +0.1499 | < 1e-15 |
| 0.072 | 0.7157 | 0.9051 | +0.1893 | < 1e-15 |
| 0.074 | 0.8452 | 1.1011 | +0.2559 | < 1e-15 |

Consistent in sign at 4 of 4 rungs, growing with reproduction rate, and far from
chance.

## What is explicitly not claimed

- **No generalization beyond this configuration.** Every observation is at
  `cs = 0.0`, `odt = 0.3`, in the boundary regime with `runaway_threshold = 0.2`.
  Nothing is claimed about default calibration, other convergence strengths,
  other defense thresholds, or any other vector.
- **No welfare claim.** Higher opacity under the defense is not shown to be good
  or bad. In the powered arm it coincided with no detectable difference in final
  population and no difference in extinction.
- **No architectural claim.** This is a property of how this policy couples
  opacity to L_t, and that coupling was written for this diagnostic. It is not
  evidence about the framework's defense design.

## Measurement caution that follows from it

`max_opacity_reached` is censored at 0.95. Where it reads 0.95 it means "at or
above." Censoring rises steeply across the powered arm's rungs, from 0.0 percent
at rr=0.068 to 47.0 percent at rr=0.074, and at the top rung it understates the
defended mean by 0.1695 (accumulator 1.1011 against censored 0.9316).

Any cross-state opacity comparison must use `opacity_accum_final`. Using
`max_opacity_reached` would have hidden most of this effect at exactly the rungs
where it is largest.

## What would settle it

Not authorized here, and it needs a new question under the post-paper arc:
vary `opacity_defense_threshold` and `convergence_strength` while holding the
reproduction rate fixed, and check whether the acceleration tracks blocked-action
count independently of both. If it does not, the effect is specific to the
clamp path rather than to the defense as such.
