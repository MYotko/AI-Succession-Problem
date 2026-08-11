# Sybil Crossover Definition Diagnostic

## Scope and provenance

This is a diagnostic of the committed Sybil defense scaling mechanism at
commit `0577a9bc36d509c7c418ec0723b636d4d987cdb1`. It does not register a
crossover definition, change an analysis criterion, select an absolute-level
term, build the two-dial mechanism, or run a smoke or characterization sweep.

The fixture is Arm A, exact pairwise defense cost, linear attack cost,
capability parity, term OFF, collapse severity 0.0, and validator-set sizes
`{2, 4, 8, 16, 32, 64}`. At severity 0.0, all genuine validators are distinct,
so effective rank equals validator-set size `N`. Arm A injects two false
clusters. Because defense cost uses apparent inputs, it checks `N + 2` inputs.

The committed formula therefore gives

```text
defense_cost(N) = choose(N + 2, 2)
attack_cost(N) = N
resolving_term(N) = N * attack_cost(N) = N^2
p_resolve(N) = N^2 / (N^2 + choose(N + 2, 2))
failure_rate(N) = 1 - p_resolve(N)^2
```

The last expression follows because defense fails if either of the two false
clusters survives. All values below were computed in Python from these exact
expressions. No random evaluation was needed for the mechanism curve.

## 1. Exact parity failure curve

| Validator-set size and effective rank | Pairwise defense cost | Per-cluster resolution probability | Defense-failure rate | n=50 binomial standard error |
|---:|---:|---:|---:|---:|
| 2 | 6 | 0.400000000000 | 0.840000000000 | 0.051845925587 |
| 4 | 15 | 0.516129032258 | 0.733610822060 | 0.062518154774 |
| 8 | 45 | 0.587155963303 | 0.655247874758 | 0.067215786447 |
| 16 | 153 | 0.625916870416 | 0.608228071329 | 0.069034293590 |
| 32 | 561 | 0.646056782334 | 0.582610634000 | 0.069738867664 |
| 64 | 2,145 | 0.656305079314 | 0.569263642866 | 0.070028929419 |

The observed maximum is 0.840000000000 and the observed minimum is
0.569263642866. The range is 0.270736357134.

The curve decreases monotonically, but flattens rapidly. Since

```text
choose(N + 2, 2) = (N^2 + 3N + 2) / 2,
```

the per-cluster resolution probability approaches `2/3`, and the two-cluster
failure rate approaches `1 - (2/3)^2 = 5/9 = 0.555555555556`. The size-64
rate remains 0.013708087311 above that asymptote. Thus the registered 0.5
threshold is unreachable not only on this ladder, but also in the large-rank
limit under this fixture.

## 2. Thresholds crossed on the ladder

Using linear interpolation in effective-rank units, every threshold strictly
between 0.569263642866 and 0.840000000000 has one located crossing. The
segments cover these rate intervals:

| Rank bracket | Failure-rate interval |
|---:|---:|
| 2 to 4 | 0.840000000000 to 0.733610822060 |
| 4 to 8 | 0.733610822060 to 0.655247874758 |
| 8 to 16 | 0.655247874758 to 0.608228071329 |
| 16 to 32 | 0.608228071329 to 0.582610634000 |
| 32 to 64 | 0.582610634000 to 0.569263642866 |

Representative round thresholds are:

| Threshold | Located crossing |
|---:|---:|
| 0.8 | rank 2.751956181534, bracketed by 2 and 4 |
| 0.7 | rank 5.715648694564, bracketed by 4 and 8 |
| 0.6 | rank 21.139044142972, bracketed by 16 and 32 |
| 0.5 | no crossing |

This establishes reachability only. It does not establish that an estimated
crossing is stable at n=50.

## 3. Candidate crossover definitions

### Candidate A: midpoint of the observed range

The exact midpoint is

```text
(0.840000000000 + 0.569263642866) / 2 = 0.704631821433.
```

It is bracketed by ranks 4 and 8 and interpolates to rank
`5.479219535496`. The deterministic curve therefore gives a located,
non-boundary crossover.

It is not stable against n=50 sampling variation on a one-rank scale. For a
Bernoulli failure indicator, the cell standard errors are 0.052 to 0.070,
equivalent to roughly 2.6 to 3.5 failures among 50 replicates. Recomputing the
observed range midpoint after changing only the rank-4 rate by one of its
n=50 standard errors moves the interpolated crossover as follows:

| Rank-4 perturbation | Recomputed crossover | Movement from exact curve |
|---:|---:|---:|
| minus 0.062518154774 | 3.602869175567 | 1.876350359930 |
| plus 0.062518154774 | 6.597854617904 | 1.118635082408 |

A local delta-method propagation across the two endpoint rates that define
the midpoint and the two rates that bracket it gives an estimated crossover
standard deviation of 3.2557 rank units. This is an instability diagnostic,
not a confidence interval, because sampling variation can change the bracket.
The direct one-standard-error perturbations already answer the requested
question without relying on a confidence convention: ordinary n=50 sampling
wobble can move this crossover by more than one rank point on its own.

Verdict: Candidate A is mathematically located and non-boundary, but its
one-rank movement criterion is noise-dominated at n=50.

### Candidate B: reachable absolute thresholds

Both proposed round thresholds are reachable:

- Failure 0.7 crosses at rank 5.715648694564 between ranks 4 and 8.
- Failure 0.6 crosses at rank 21.139044142972 between ranks 16 and 32.

Their n=50 stability is also poor. For threshold 0.7, changing only the
rank-4 rate by one n=50 standard error moves the crossing to rank
3.657713703140 or 6.729364703073. Those movements are 2.0579 and 1.0137
rank units. A local delta-method crossover standard deviation is 2.3424
rank units.

Threshold 0.6 lies on a much flatter segment. A single failure-count change
at rank 16, a rate change of only 0.02 at n=50, moves the crossing to rank
14.594811913061 or 25.900800389215. A local delta-method crossover standard
deviation is 32.4400 rank units and is best read only as evidence of severe
local instability.

Verdict: Candidate B yields located, non-boundary deterministic crossings at
both 0.7 and 0.6. Neither supports a stable one-rank movement reading at
n=50. Of the two, 0.7 is less unstable than 0.6, but it still exceeds the
one-rank criterion under an ordinary one-standard-error perturbation.

## 4. Absolute-level movement feasibility

The committed term-OFF curve has enough mechanistic dynamic range for an
absolute-level term to move a located crossover. This statement is a
feasibility result, not a term selection or proposed registration.

For Candidate A, consider only the analytical effect of an absolute defender
resolution multiplier `m` on the existing resolving term:

```text
p_resolve_m(N) = m * N^2 / (m * N^2 + choose(N + 2, 2)).
```

This is a diagnostic probe of an absolute resolution channel. If `m` takes
the parity-level values 0.316, 1.0, and 3.16, the recomputed relative-midpoint
crossovers are:

| Absolute resolution multiplier | Relative-midpoint crossover |
|---:|---:|
| 0.316 | 6.749319275947 |
| 1.0 | 5.479219535496 |
| 3.16 | 4.167181309638 |

The span is 2.582137966309 rank units, so movement greater than one rank is
mechanistically feasible under Candidate A. The same probe also makes some
fixed absolute thresholds disappear at the outer multiplier levels, which
would be a degenerate result rather than a located movement.

For Candidate B, only a modest absolute effect is needed while preserving a
located crossing. An independent absolute catch channel with probability
`c` changes per-cluster resolution to
`p_resolve + c * (1 - p_resolve)`. As a diagnostic bound:

- Increasing `c` from 0 to 0.05 moves the 0.7 crossing from rank
  5.715648694564 to 4.415722036435, a movement of 1.299926658128. Both
  crossings remain located.
- Increasing `c` from 0 to 0.01 moves the 0.6 crossing from rank
  21.139044142972 to 18.215083791304, a movement of 2.923960351668. Both
  crossings remain located.

These probes show that Gate 3 movement is mechanically possible under either
candidate family. They do not choose the form, threshold, or strength of an
absolute-level term. Those remain operator decisions before any mechanism is
built or any crossover is registered.

## Assessment for operator ruling

The mechanism supports deterministic, non-boundary crossings for the
relative midpoint, absolute 0.7, and absolute 0.6 definitions. It also has
enough dynamic range for a suitable absolute-level nonlinearity to move such
a crossing by more than one rank point.

However, neither candidate yields a stable crossover at n=50 under a
one-rank movement criterion. Candidate A and absolute 0.7 both move by more
than one rank under a one-standard-error cell perturbation. Absolute 0.6 is
more unstable and can move several rank units after a single failure-count
change. Therefore, no candidate in this diagnostic can support the specified
n=50, one-rank Gate 3 comparison non-degenerately without an operator ruling
on the estimator, replicate count, ladder, or movement criterion.

No crossover definition is registered by this report.
