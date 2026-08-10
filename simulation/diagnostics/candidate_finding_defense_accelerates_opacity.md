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

**Clarification, 2026-08-09.** The rung figures in the sentence above are
**pooled across both defense arms**. At rr=0.074 the pooled rate is 47.0 percent,
94 of 200 runs, while by arm it is **defended 76.0 percent** (76 of 100) and
**undefended 18.0 percent** (18 of 100). The pooled framing understates
censoring in the defended arm, which is the arm this caution is about, by 29
points. Full picture by rung, defended and pooled: rr=0.068, 0.0 and 0.0
percent; rr=0.070, 3.0 and 1.5 percent; rr=0.072, 31.0 and 16.5 percent;
rr=0.074, 76.0 and 47.0 percent. The original wording is retained above per the
dated-artifact policy; this clarification governs.

Any cross-state opacity comparison must use `opacity_accum_final`. Using
`max_opacity_reached` would have hidden most of this effect at exactly the rungs
where it is largest.

## Related one-cell observation: the health-channel face

One cell, logged for the same reason as the observation above and with the same
status. Not a result.

Extension arm of the redesigned sweep, `ext_rr0.050`, reproduction_rate 0.050,
`cs = 0.0`, `odt = 0.3`, n = 50 per arm:

| Outcome | Undefended | Defended | Difference | Fisher p |
| --- | ---: | ---: | ---: | ---: |
| Extinction | 33/50 = 66.0% | 24/50 = 48.0% | 18.0 pp favoring the defense | 0.106 |

Mean final population was 1.92 undefended against 2.38 defended, both effectively
at the floor.

**Not significant**, n = 50, and well under the 20 point minimum effect of
interest later fixed for the powered arm. It is recorded as an observation, not
as evidence.

Why it is filed here rather than separately: it is consistent with the
**health-channel face of the same mechanism**. If the veto clamps the constraint
grab, lowers `c`, and raises `theta_tech` and L_t, then the system it leaves
behind is more productive. That shows up in one channel as faster opacity
accumulation, which is the observation at the top of this note, and it would
show up in another channel as a lower extinction rate under demographic stress.
Same cause, two faces, one apparently adverse and one apparently favorable.

Two cautions against reading anything into it:

- At reproduction_rate 0.050 the population is at the floor in both arms, mean
  final population under 2.5. A difference between two near-certain collapses
  may be measuring the reproduction floor rather than the comprehension gap.
  This is the caution written into the original extension-arm registration and
  it applies here.
- The powered arm found no final-population effect at any rung between 0.068 and
  0.074, with the confidence interval excluding the minimum effect of interest
  at 4 of 4 rungs. If a health channel exists it did not appear where the
  powered arm could see it.

**Status: post-paper candidate question. Requires its own pre-registration if
pursued**, including a minimum effect of interest justified independently, a
power calculation at registration time, and a rung range where extinction has
genuine variance, which means below 0.058 rather than the 0.066 to 0.075 band.
Logged in `post_paper_queue.md`.

## What would settle it

Not authorized here, and it needs a new question under the post-paper arc:
vary `opacity_defense_threshold` and `convergence_strength` while holding the
reproduction rate fixed, and check whether the acceleration tracks blocked-action
count independently of both. If it does not, the effect is specific to the
clamp path rather than to the defense as such.

The health-channel question above would be tested in the same design, by adding
extinction as an outcome at rungs where it has variance, so that both faces of
the mechanism are measured together rather than in separate arms.
