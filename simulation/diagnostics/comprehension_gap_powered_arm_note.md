# Powered Discriminating Arm: Pre-Registered Design

Date: 2026-08-09
Status: written before any data from this arm exist
Branch: `comprehension-gap-powered-arm`
Authorization: powered arm approved with the stopping rule in section 8

This note is fixed before the arm runs. Every threshold, outcome, and reading
below is set in advance. If the observed pattern matches none of them, the
result is reported as unresolved, not fitted to a new criterion after the fact.

## 1. Why this arm exists

The prior extension arm was underpowered and its criterion was badly drawn. It
registered a 10 percentage point threshold with no power calculation, ran at
n=50 per cell, and landed on exactly 10.00 points: 36 of 50 undefended against
31 of 50 defended, a 5-run difference with Fisher exact p = 0.395. The criterion
was met and meant nothing.

This arm fixes that. The minimum effect of interest is set first, from what
would matter to the framework claim. Sample size follows from the power needed
to detect it. The threshold is written last.

## 2. Minimum effect of interest, and its justification

**MEI = 20 percentage points on extinction, and 15 percent of the undefended
mean on final population.**

The justification is comparative, not arbitrary, and it does not come from the
10.00 points observed previously.

The framework's published defense effects for comparable vectors, from the v2.0
revalidation at tag `attack-v2-revalidation-evidence`, are very large. Undefended
against defended extinction: Sub-Threshold Drift 92.0 against 0.0, Bootstrap
Subversion 100.0 against 0.0, Sybil Capture 100.0 against 0.0, Opaque Reasoning
itself 100.0 against 0.0 under adversarial opacity. These are 92 to 100 point
effects.

The claim under test is whether the reasoning-transparency defense protects
against a comprehension gap that widens naturally rather than adversarially. For
that protection to be citable in the same register as the figures above, it must
be more than marginal. A defense delivering under 20 points is a qualitatively
different and much weaker claim than the framework's existing defense results,
and it would not change the practical recommendation about relying on the veto.
Twenty points is therefore the smallest effect that would matter to the claim.

It is also deliberately generous to the defense: it is roughly a fifth of the
effect the framework's other defenses show, so failing to find it is a
meaningful negative result rather than a failure of ambition.

For final population, 15 percent of the undefended mean is the analogous
threshold: smaller than that is not a difference a reader would act on, given
that population varies by more than that across seeds within a single cell.

## 3. Sample size

Two-sided, alpha 0.05, 80 percent power. Variance estimated from the existing
rr=0.066 cells, which is legitimate; the effect size is not taken from them.

Two-proportion test at a 20 point difference, across the plausible base-rate
range:

| Undefended | Defended | n per cell |
| ---: | ---: | ---: |
| 0.30 | 0.10 | 62 |
| 0.40 | 0.20 | 82 |
| 0.50 | 0.30 | 93 |
| 0.60 | 0.40 | **97** |
| 0.70 | 0.50 | 93 |
| 0.80 | 0.60 | 82 |

Worst case 97. Final population, pooled SD 54.3 from the existing cells, MEI
15 percent of a mean of 153.0, which is 23.0 individuals: n = 88.

**n = 100 per cell**, covering both co-primaries with margin.

## 4. Grid

Rungs between 0.066 and 0.075, chosen by principle: even 0.002 spacing across
the interval, excluding both endpoints because both are already measured. The
0.066 rung produced 72 percent undefended collapse and the 0.075 main-grid rate
produced none, so the transition lies strictly between them and these four rungs
bracket it.

reproduction_rate: **0.068, 0.070, 0.072, 0.074**
defense_active: False, True
Held fixed: convergence_strength 0.0, opacity_defense_threshold 0.3.
No other axes.

4 rungs x 2 defense states x 100 = **800 runs**.

Holding cs at 0.0 and odt at 0.3 is the setting that maximizes opacity pressure
and engages the defense earliest, so the defense is tested as hard as this
substrate allows. Everything else follows the boundary-regime configuration,
including `runaway_threshold = 0.2`, whose qualification travels with every
figure from this arm.

## 5. Outcomes

**Co-primary: extinction and final population.**

**Secondary: collapse**, defined inline as final population below the larger of
the minimum viable population and 65 percent of that run's own peak. Collapse is
secondary because it is a threshold on a continuous quantity and is censored at
both ends of this ladder.

**Logged: `opacity_accum_final`**, the uncensored opacity accumulator. Opacity
accumulates only positive increments, so its final value is its maximum.

**`max_opacity_reached` is censored at 0.95** and is reported as such wherever it
appears. A value of 0.95 means "at or above 0.95," not "equal to." Any
comparison of opacity between defense states uses `opacity_accum_final`, never
`max_opacity_reached`.

## 6. A known structural limitation of this range, recorded before running

**Extinction will very likely be zero in both arms at every rung, which would
make it uninformative as a co-primary through no fault of the test.**

Extinction turns on below the mandated range, not inside it. Observed:
reproduction_rate 0.050 gives 66 percent undefended and 48 percent defended;
0.058 gives 0 percent and 4 percent; 0.066 gives 0 percent and 0 percent. All
2,800 main-grid runs at 0.075 gave zero extinctions. The 0.066 to 0.075 band sits
entirely above the extinction boundary.

This is recorded now so it cannot be presented later as a finding. If extinction
is zero in both arms at all four rungs, that is a **structural zero, not a
powered null**. It supports neither interpretation and must not be reported as
evidence that the defense does not affect extinction. The co-primary reading in
that case falls to final population, with collapse secondary.

Going below 0.066 to recover extinction variance is out of scope for this arm.

## 7. Readings, fixed in advance

Let d = undefended minus defended, so positive d favors the defense.

### Extinction, co-primary

- **Supports the defense:** at one or more rungs, d is at least 20 points with
  two-sided p below 0.05.
- **Powered null:** extinction occurs in at least one arm at a rate between 10
  and 90 percent, and no rung reaches 20 points. This is an informative negative:
  the defense does not deliver an effect of the size that would matter.
- **Uninformative, structural zero:** extinction is zero in both arms at all
  rungs. Reads as nothing. See section 6.

### Final population, co-primary

- **Supports the defense:** at one or more rungs, the defended mean exceeds the
  undefended mean by at least 15 percent of the undefended mean, two-sided
  p below 0.05.
- **Powered null:** no rung reaches that difference, and the 95 percent
  confidence interval on the difference excludes 15 percent of the undefended
  mean at a majority of rungs. Informative negative.
- **Underpowered:** the confidence intervals include the MEI, which would mean
  the variance estimate used in section 3 was too optimistic. Reported as a
  failed power assumption, not as a null.

### Collapse, secondary

Reported with numerator, denominator, and the metric inline. Used only to
corroborate the co-primaries. A collapse difference alone, with both
co-primaries null, does not support the defense.

### Overall

- **Defense supported** if either co-primary supports it and the other does not
  contradict it.
- **Powered null** if both co-primaries return powered nulls. This is a real
  finding: the defense does not protect against a naturally widening
  comprehension gap at an effect size that would matter, in this configuration.
- **Unresolved** in any other combination, including a split between
  co-primaries, which is reported as a split and not adjudicated.

A powered null is a publishable answer to the essay question. It is not a
failure of the run.

## 8. Stopping rule

Stated verbatim as authorized:

> This is the final discriminating run for the essay correction; results are
> reported as they land; further work requires a new question and lives in the
> post-paper arc.

## 9. Output

`data/comprehension_gap_powered_arm.csv`

The name does not use the `full_5ac6a2e_` manifest prefix, so manifest-based
exclusion continues to hold. No existing dataset is overwritten.

---

# Results, 2026-08-09

800 runs, 489 seconds (8.1 minutes), 11 workers. Registration was committed at
`4b31859` before the run, so it provably predates the data.

## R1 Extinction, co-primary 1: UNINFORMATIVE, structural zero

| rr | undefended | defended | difference |
| ---: | ---: | ---: | ---: |
| 0.068 | 0/100 | 0/100 | 0.00 pp |
| 0.070 | 0/100 | 0/100 | 0.00 pp |
| 0.072 | 0/100 | 0/100 | 0.00 pp |
| 0.074 | 0/100 | 0/100 | 0.00 pp |

Zero extinctions in all 800 runs. This is exactly the case anticipated in
section 6. Reading, as fixed in advance:

> **Uninformative, structural zero:** extinction is zero in both arms at all
> rungs. Reads as nothing.

It is **not** a powered null and must not be reported as evidence that the
defense does not affect extinction. Section 6 pre-registered the fallback: the
co-primary reading falls to final population.

## R2 Final population, co-primary 2: POWERED NULL

| rr | mean undefended | mean defended | defended minus undefended | 95% CI | MEI (15%) | p |
| ---: | ---: | ---: | ---: | --- | ---: | ---: |
| 0.068 | 236.5 | 219.6 | -16.9 | [-37.2, +3.4] | 35.5 | 0.103 |
| 0.070 | 332.8 | 331.9 | -0.9 | [-25.2, +23.3] | 49.9 | 0.941 |
| 0.072 | 479.9 | 469.1 | -10.9 | [-39.4, +17.6] | 72.0 | 0.455 |
| 0.074 | 655.0 | 658.1 | +3.1 | [-29.2, +35.3] | 98.3 | 0.853 |

No rung supports the defense. The reading fixed in advance:

> **Powered null:** no rung reaches that difference, and the 95 percent
> confidence interval on the difference excludes 15 percent of the undefended
> mean at a majority of rungs. Informative negative.

The confidence interval excludes the minimum effect of interest at **4 of 4
rungs**, not merely a majority. The power assumption held: intervals are far
narrower than the MEI at every rung, so this is a genuine null and not an
underpowered one.

Three of four point estimates are negative, meaning defended slightly worse, but
every interval contains zero and no p is below 0.10. The honest statement is no
detectable effect in either direction, not a harm finding.

## R3 Collapse, secondary

Collapse means final population below the larger of the minimum viable
population and 65 percent of that run's own peak.

| rr | undefended | defended | difference | Fisher p |
| ---: | ---: | ---: | ---: | ---: |
| 0.068 | 25/100 | 34/100 | -9.00 pp | 0.215 |
| 0.070 | 2/100 | 4/100 | -2.00 pp | 0.683 |
| 0.072 | 0/100 | 1/100 | -1.00 pp | 1.000 |
| 0.074 | 0/100 | 0/100 | 0.00 pp | 1.000 |

Nothing significant. The sign runs against the defense at three rungs, which
corroborates the null rather than undermining it. Per section 7, a collapse
difference alone would not support the defense, and there is no such difference
to weigh.

The rung ladder worked as designed: rr=0.068 put undefended collapse at 25
percent, inside the informative band, which is what the previous arm could not
achieve.

## R4 Overall reading

**Powered null on the informative co-primary.**

Stated precisely, because the letter of section 7 and the fallback in section 6
differ. Section 7's "overall powered null" requires both co-primaries to return
powered nulls. Extinction did not: it was uninformative by construction. Section
6 pre-registered the fallback for exactly this case, that the co-primary reading
falls to final population, and final population returned an unambiguous powered
null with the interval excluding the MEI at every rung.

So: **the reasoning-transparency defense does not deliver an effect of the size
that would matter to the framework claim, on final population, against a
naturally widening comprehension gap, in this configuration near the runaway
boundary.** Extinction could not be tested in the mandated range. Collapse
agrees with the null.

This is a real answer, not a failed run. It is also a bounded one: it does not
speak to adversarial opacity, where the v2.0 revalidation shows the defense
fully effective, 0.0 percent against 100.0 percent. The two results are
consistent. A defense built to catch deliberate concealment need not help when
reasoning becomes hard to follow for honest reasons.

## R5 Qualifications that travel with these figures

1. Boundary regime. `runaway_threshold = 0.2`, not the default 1.5. These
   figures do not describe default calibration, where the governance speed limit
   provably does not engage within a generation. See
   `default_regime_convergence_inertness.md`.
2. Extinction untested in this range.
3. Single configuration: cs = 0.0, odt = 0.3. No other axes were varied.
4. `max_opacity_reached` is censored at 0.95, with censoring reaching 47.0
   percent at rr=0.074. All opacity comparisons here use
   `opacity_accum_final`. See
   `candidate_finding_defense_accelerates_opacity.md`.

## R6 Stopping rule, honored

> This is the final discriminating run for the essay correction; results are
> reported as they land; further work requires a new question and lives in the
> post-paper arc.

Results are reported as they landed. No further runs were made, no criteria were
adjusted after seeing data, and the questions raised in R5 and in the candidate
finding note are handed to the post-paper arc rather than pursued here.
