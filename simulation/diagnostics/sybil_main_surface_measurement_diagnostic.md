# Sybil Main-Surface Measurement Diagnostic

Date: 2026-08-11

## Status and scope

This is the Stage 1 measurement diagnostic only. It does not register a
finding quantity, change a criterion, build a characterization runner, run
characterization data, or compute a study result. It evaluates the exact
expectations of the committed mechanism at the frozen grid values supplied by
the operator and applies analytical n=200 perturbation checks.

The mechanism is commit `294f8f210bb27ab0d186770ed692b4465f4696b4`.
The current committed design note is commit
`0577a9bc36d509c7c418ec0723b636d4d987cdb1`. That note identifies itself as
the second correction and still contains the obsolete crossover-based
ratio-collapse slice. It is not the third-correction note named in the Stage 1
task. The task's frozen grid and curve-slice facts are used here only as
diagnostic inputs. They are not treated as a substitute registration. The
operator confirmation gate must resolve this provenance mismatch before any
fourth correction or characterization work begins.

## Exact diagnostic method

For each registered structural cell, validators are the institution plus
`N - 1` frontier validators. The connected-components merge rule at 0.9 gives
these exact effective ranks:

| Total size | Severity 0 | Severity 0.33 | Severity 0.66 | Severity 1 |
|---:|---:|---:|---:|---:|
| 2 | 2 | 2 | 2 | 2 |
| 4 | 4 | 4 | 3 | 2 |
| 8 | 8 | 8 | 5 | 2 |
| 16 | 16 | 16 | 7 | 2 |
| 32 | 32 | 32 | 13 | 2 |
| 64 | 64 | 64 | 23 | 2 |

The institution-only corner has rank 1. Arm B has 0, 1, 3, 9, 19, and 41
eligible frontier-detachment events at severity 0.66 across the six sizes,
and 0, 2, 6, 14, 30, and 62 at severity 1.

Let `q` be the committed per-event resolution probability at the cell after
applying its size, effective rank, capability ratio, defense-cost form, and
attack-cost form. With two forged clusters, the exact Arm A strict failure
rate is

```text
F_A = 1 - q^2.
```

For Arm B, let `D` be the number of eligible frontier-detachment events in
the true clusters. The institution-merge event is one additional independent
corruption opportunity. The exact strict failure rate is

```text
F_B_strict = 1 - q^(D + 1).
```

At a true rank-two cell, rank-visible failure requires an institution merge
and no detachment, so

```text
F_B_visible = q^D * (1 - q).
```

It is zero at true ranks above two because a single institution merge cannot
move measured rank below two. The rank-one analytic corner is a structural
strict failure, not a corruption-caused rank-visible failure.

These expressions were evaluated in Python at all 25 structural points, all
25 log-spaced ratios from 0.1 to 10, both arms, both defense-cost forms, and
both attack-cost forms. This produced exact expectation diagnostics, not
random characterization observations.

## n=200 stability scale

For a fixed-cell Bernoulli proportion at n=200,

```text
maximum SE = sqrt(0.25 / 200) = 0.035355339059.
maximum 95 percent half-width = 0.069296464557.
```

For an independent difference between two fixed cells,

```text
maximum SE = sqrt(0.5 / 200) = 0.05.
MEI / maximum SE = 0.15 / 0.05 = 3.0.
```

The staged two-proportion calculation requires 175 per cell for 80 percent
power at the 0.15 MEI, so n=200 retains its registered margin. A fixed-cell
rate or difference is therefore a stable estimand. A difference whose
uncertainty overlaps the MEI is reported as boundary rather than forced into
a binary conclusion.

An interpolated rank crossing is different. Its uncertainty divides rate
uncertainty by the local slope and can become arbitrarily large when the
curve is flat. The perturbation results below use the delta method on the two
bracketing binomial proportions.

## Frozen floor question and A/B asymmetry

The floor question uses fixed maximum-collapse cells, so it does not inherit
the interpolation instability. The exact parity rates illustrate the range
the registered run will estimate:

| Defense cost | Attack cost | Size | Arm A | Arm B strict | Arm B rank-visible |
|---|---|---:|---:|---:|---:|
| Pairwise | Linear | 2 | 0.840000 | 0.200000 | 0.200000 |
| Pairwise | Linear | 4 | 0.955679 | 0.936000 | 0.096000 |
| Pairwise | Linear | 8 | 0.993336 | 1.000000 | 0.000003 |
| Pairwise | Linear | 16 | 0.999351 | 1.000000 | 0.000000 |
| Pairwise | Linear | 32 | 0.999950 | 1.000000 | 0.000000 |
| Pairwise | Linear | 64 | 0.999997 | 1.000000 | 0.000000 |
| Pairwise | Superlinear | 2 | 0.764502 | 0.150221 | 0.150221 |
| Pairwise | Superlinear | 4 | 0.925007 | 0.885717 | 0.121215 |
| Pairwise | Superlinear | 8 | 0.987530 | 0.999996 | 0.000019 |
| Pairwise | Superlinear | 16 | 0.998729 | 1.000000 | 0.000000 |
| Pairwise | Superlinear | 32 | 0.999900 | 1.000000 | 0.000000 |
| Pairwise | Superlinear | 64 | 0.999993 | 1.000000 | 0.000000 |
| Static | Linear | 2 | 0.360000 | 0.200000 | 0.200000 |
| Static | Linear | 4 | 0.360000 | 0.488000 | 0.128000 |
| Static | Linear | 8 | 0.360000 | 0.790285 | 0.052429 |
| Static | Linear | 16 | 0.360000 | 0.964816 | 0.008796 |
| Static | Linear | 32 | 0.360000 | 0.999010 | 0.000248 |
| Static | Linear | 64 | 0.360000 | 0.999999 | 0.000000 |
| Static | Superlinear | 2 | 0.277876 | 0.150221 | 0.150221 |
| Static | Superlinear | 4 | 0.277876 | 0.386354 | 0.108478 |
| Static | Superlinear | 8 | 0.277876 | 0.680006 | 0.056567 |
| Static | Superlinear | 16 | 0.277876 | 0.912986 | 0.015382 |
| Static | Superlinear | 32 | 0.277876 | 0.993566 | 0.001137 |
| Static | Superlinear | 64 | 0.277876 | 0.999965 | 0.000006 |

These are mechanism expectations, not study findings. They show why the
floor must remain cell-specific: every maximum-collapse cell has effective
rank two, but pairwise cost and Arm B's number of corruption opportunities
still depend on headcount.

For the A-versus-B contrast at parity, a 95 percent perturbation around each
fixed-cell difference gives the following classifications against the 0.15
MEI. Counts are out of the six maximum-collapse sizes.

| Defense cost | Attack cost | Arm B track | MEI-sensitive | MEI-robust | Boundary |
|---|---|---|---:|---:|---:|
| Pairwise | Linear | Strict | 1 | 5 | 0 |
| Pairwise | Linear | Rank-visible | 6 | 0 | 0 |
| Pairwise | Superlinear | Strict | 1 | 5 | 0 |
| Pairwise | Superlinear | Rank-visible | 6 | 0 | 0 |
| Static | Linear | Strict | 4 | 0 | 2 |
| Static | Linear | Rank-visible | 5 | 0 | 1 |
| Static | Superlinear | Strict | 4 | 0 | 2 |
| Static | Superlinear | Rank-visible | 4 | 0 | 2 |

Conclusion: the floor proportions and A/B contrasts are stable fixed-cell
quantities at n=200. Some cells are expected to be genuine MEI boundaries,
which the frozen boundary discipline already knows how to report. Neither the
floor question nor two-track asymmetry needs a new measurement definition.

## Candidate 1: crossover rank

### Rank is not sufficient to identify a cell

At parity, the same measured rank two spans these within-rank failure-rate
ranges across registered structural cells:

| Track and cost form | Maximum same-rank spread |
|---|---:|
| Arm A, pairwise, linear attack | 0.159997 |
| Arm A, pairwise, superlinear attack | 0.235491 |
| Arm A, static, either attack form | 0 |
| Arm B strict, pairwise, linear attack | 0.800000 |
| Arm B strict, pairwise, superlinear attack | 0.849779 |
| Arm B strict, static, linear attack | 0.799999 |
| Arm B strict, static, superlinear attack | 0.849744 |
| Arm B rank-visible, all cost forms | 0.150215 to 0.200000 |

Pairwise cost depends on total validator count even when effective rank is
the same. Arm B also depends on the number of members inside a collapsed
cluster. Consequently, no single rank-only crossover can summarize the
registered structural axis without discarding mechanism variables.

### Threshold reachability and interpolation noise

As a favorable one-dimensional test, the no-collapse size ladder was checked
for both strict arms, all four cost combinations, and all 25 ratios. This is
200 curves. For each fixed threshold, a crossing was counted as stable only
when its delta-method standard deviation was at most one rank unit.

| Failure threshold | Curves with a crossing | Stable within one rank | Curves with multiple crossings |
|---:|---:|---:|---:|
| 0.5 | 53 of 200 | 37 of 200 | 1 |
| 0.6 | 44 of 200 | 30 of 200 | 1 |
| 0.7 | 34 of 200 | 24 of 200 | 0 |
| 0.8 | 26 of 200 | 17 of 200 | 0 |

No threshold is both reachable and stable across the registered arms and
cost forms. At the primary Arm A pairwise-linear parity curve, the exact
rates on sizes 2 through 64 are 0.840000, 0.733611, 0.655248, 0.608228,
0.582611, and 0.569264. Threshold 0.5 is absent. Threshold 0.7 crosses at
rank 5.715649 but has delta-method SD 1.171213 rank units at n=200.
Threshold 0.6 crosses at rank 21.139044 with SD 16.220018. Threshold 0.8
is locally stable with SD 0.375887, but it is absent from the static-cost
curves and has no registered mechanism meaning.

Some individual curves have steep, stable crossings. For example, Arm A
pairwise-superlinear at parity crosses 0.5 with SD 0.649529. That does not
rescue a primary quantity because the same threshold is absent in the other
seven parity arm-by-cost curves. Choosing a threshold per curve would make
the definition outcome-dependent.

Conclusion: crossover rank remains noise-dominated or undefined and is not a
valid primary or sensitivity finding quantity.

## Candidate 2: fixed-cell failure-rate surface

The surface itself is stable as a collection of fixed-cell proportions. Its
uncertainty does not divide by a slope. However, adjacent ratio steps are too
fine for the 0.15 MEI: across Arm A, Arm B strict, Arm B rank-visible, both
defense costs, both attack costs, all 25 structural points, and all 24 ratio
adjacencies, the largest exact adjacent-ratio difference is 0.069329. None of
the 7,200 adjacent-ratio contrasts reaches 0.15. Defining ratio sensitivity
from adjacent steps would therefore be vacuously robust.

The two pre-registered endpoint cells, ratio 0.1 and ratio 10, provide a
stable, fixed contrast without inventing a threshold. Arm A and Arm B strict
are monotonic in ratio at every fixed structural cell. The full 25-point
curve remains reported for shape, while the endpoint difference is the
finding quantity. Applying a 95 percent delta-method perturbation around the
endpoint difference gives these classifications across the 25 structural
cells:

| Track | Defense cost | Attack cost | Sensitive | Robust | Boundary | Median exact endpoint difference |
|---|---|---|---:|---:|---:|---:|
| Arm A | Pairwise | Linear | 21 | 4 | 0 | 0.752237 |
| Arm A | Pairwise | Superlinear | 21 | 4 | 0 | 0.809983 |
| Arm A | Static | Linear | 16 | 8 | 1 | 0.481844 |
| Arm A | Static | Superlinear | 13 | 11 | 1 | 0.276889 |
| Arm B strict | Pairwise | Linear | 17 | 7 | 1 | 0.689895 |
| Arm B strict | Pairwise | Superlinear | 19 | 6 | 0 | 0.527985 |
| Arm B strict | Static | Linear | 16 | 7 | 2 | 0.465115 |
| Arm B strict | Static | Superlinear | 15 | 9 | 1 | 0.274601 |
| Arm B rank-visible | Pairwise | Linear | 4 | 21 | 0 | 0 |
| Arm B rank-visible | Pairwise | Superlinear | 4 | 21 | 0 | 0 |
| Arm B rank-visible | Static | Linear | 4 | 21 | 0 | 0 |
| Arm B rank-visible | Static | Superlinear | 4 | 21 | 0 | 0 |

The maximum endpoint-contrast SE is 0.036048, below the worst-case 0.05
bound. The few boundary cells are explicitly identifiable instead of moving
an interpolated rank boundary.

Conclusion: fixed-cell failure rates and pre-fixed endpoint ratio contrasts
are stable. The surface is a valid supporting quantity, and the endpoint
contrast is a stable replacement for crossover movement in the ratio
sensitivity reading.

## Candidate 3: monotonic-region boundary

There is no shared monotonic-region boundary. Across sizes at each fixed
severity and ratio, exact direction counts are:

| Arm | Defense cost | Attack cost | Increasing | Decreasing | Flat | Nonmonotonic | MEI-sized edges out of 500 |
|---|---|---|---:|---:|---:|---:|---:|
| Arm A | Pairwise | Linear | 50 | 50 | 0 | 0 | 24 |
| Arm A | Pairwise | Superlinear | 25 | 50 | 0 | 25 | 69 |
| Arm A | Static | Linear | 0 | 75 | 25 | 0 | 84 |
| Arm A | Static | Superlinear | 0 | 75 | 25 | 0 | 64 |
| Arm B strict | Pairwise | Linear | 100 | 0 | 0 | 0 | 83 |
| Arm B strict | Pairwise | Superlinear | 50 | 0 | 0 | 50 | 90 |
| Arm B strict | Static | Linear | 25 | 50 | 0 | 25 | 101 |
| Arm B strict | Static | Superlinear | 25 | 50 | 0 | 25 | 93 |

The direction changes with collapse severity, arm, and cost form. Most size
edges are smaller than the MEI, and there are only four registered severity
levels. A boundary would therefore require a new ordering, aggregation, or
threshold that is not fixed by the current mechanism or plan.

Conclusion: a monotonic-region boundary is not a stable shared finding
quantity.

## Complete-linkage sensitivity quantity

The same fixed-cell method also repairs the complete-linkage sensitivity
reading without a crossover. At parity, compare Arm A's connected-components
and complete-linkage failure rates at each of the same 25 structural cells,
for each fixed cost combination, against the 0.15 MEI. Complete linkage
changes rank only at severity 0.66 for sizes 8 through 64. A 95 percent
perturbation gives:

| Defense cost | Attack cost | Sensitive cells | Robust cells | Boundary cells | Maximum exact difference |
|---|---|---:|---:|---:|---:|
| Pairwise | Linear | 0 | 22 | 3 | 0.175180 |
| Pairwise | Superlinear | 3 | 21 | 1 | 0.428344 |
| Static | Linear | 0 | 25 | 0 | 0.023274 |
| Static | Superlinear | 0 | 25 | 0 | 0.012539 |

This retains the registered reduced scope and answers whether the merge rule
materially changes the failure curve, with boundary cells reported rather
than converted into an unstable rank movement.

## Recommendation for operator confirmation

Recommend the following single measurement design:

1. Primary per arm: the existing fixed-cell rank-two floor question becomes
   the primary finding, reported over every registered maximum-collapse cell
   and cost form as a defense-failure proportion with uncertainty. The A/B
   asymmetry remains the headline comparison, with Arm B on strict and
   rank-visible tracks. The three frozen floor outcomes and boundary
   discipline remain unchanged.
2. Ratio sensitivity per arm: at every fixed structural and cost cell, report
   the full 25-point failure-rate curve and use the pre-fixed endpoint
   contrast `F(ratio 10) - F(ratio 0.1)` as the finding quantity. Classify the
   cell as ratio-sensitive when the contrast clears the 0.15 MEI, robust when
   it remains below the MEI, and boundary when uncertainty overlaps the MEI.
   Arm B uses its frozen strict track for this per-arm classification; the
   rank-visible track remains a separately reported companion curve.
3. Merge-rule sensitivity: at parity, compare complete-linkage and primary
   connected-components failure rates cell by cell across the already frozen
   25-point Arm A cost grid, using the same 0.15 MEI and boundary discipline.
4. Crossover rank is withdrawn as a registered finding quantity. Any
   threshold crossing may be reported descriptively only when it exists,
   with no headline or verdict attached.

This recommendation changes only the unstable measurement representation. It
does not change the grid, ratio range, rank construction, n, MEI, arms, cost
forms, merge rules, failure definitions, floor outcomes, or two-track Arm B
reporting.

## Operator confirmation gate

STOP. Confirm or reject the recommended fixed-cell finding design before any
registration edit, runner construction, self-check, characterization data, or
analysis. Before Stage 2 begins, the branch also needs the stated committed
third-correction note or an explicit operator ruling that resolves its absence.
