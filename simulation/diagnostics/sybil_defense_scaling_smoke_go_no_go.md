# Sybil Defense Scaling Instrument: Smoke Go/No-Go Report

## Decision

**GO for operator review of the instrument. NO-GO for any full sweep.**

All smoke gates passed. The run was limited to instrument validation,
positive controls, variance estimation, and timing. It did not run the
rank-by-ratio surface, select a capability-ratio range, calculate power, or
compute or report a crossover.

Primary records:

- Raw rows: `data/sybil_defense_scaling/smoke_sybil_scaling_instrument_v1/smoke_results.csv`
- Structured evidence: `data/sybil_defense_scaling/smoke_sybil_scaling_instrument_v1/smoke_evidence.json`
- Execution log: `data/sybil_defense_scaling/smoke_sybil_scaling_instrument_v1/smoke_execution.log`
- Environment and artifact manifest: `data/sybil_defense_scaling/smoke_sybil_scaling_instrument_v1/smoke_manifest.json`

Python counted 173 data rows: 2 validated-path probes, 6 cost rows, 5
attribution rows, and 160 arm runs. The manifest also records 173 rows, and
all four artifact hashes in the manifest were independently verified.

## Existing code reused versus new code

Existing validated code was not edited. The smoke imports the registered
`sybil_capture` scenario, its full cells, paired deterministic seed
construction, smoke task builder, and `run_single` path from
`simulation/run_attack_vector_revalidation_v2.py`. That path continues through
the existing `GardenModel` and v2 Sybil adapter without modification. Its
paired smoke probe used seed 400373737 in both defense states. The undefended
probe attacked successfully, and the defended probe fired the defense and
blocked the attack. Both recorded `is_v2_mode=True`.

The following files are new and isolated:

- `simulation/sybil_defense_scaling.py`: attribution, costs, capability terms,
  and the two scaling attack arms.
- `simulation/config/sybil_defense_scaling.json`: all study and smoke
  parameters, including the blocked sweep fields.
- `simulation/run_sybil_defense_scaling_smoke.py`: smoke-only runner, evidence
  writer, variance calculation, and timing projection.
- `simulation/test_sybil_defense_scaling.py`: focused mechanism and control
  tests.

No change was made to `simulation/model.py`, `simulation/agents.py`,
`simulation/attack_adapter_v2.py`, or the shared revalidation runner. The new
scaling mechanisms are therefore not changes to production paths used by other
validated scenarios.

## Merge rule and independence-weighted attribution

Each frontier validator has a shared frontier component and a lineage-specific
component. Its retained lineage diversity at collapse severity `s` is:

`base_diversity * (1 - s) ** participant_decay_rate`

The instrument computes pairwise cosine similarity from the shared and lineage
components. Under the selected config, every pair at or above similarity 0.9
is joined, and connected components are the consensus inputs. Pool strength is
the number of resulting components, not validator headcount. The full
similarity matrix and exact pair count are retained in the attribution result.

The institution uses a separate orthogonal lineage axis. Its retained diversity
is always 1.0, its similarity to every frontier validator is 0.0 before an Arm
B measurement attack, and the collapse parameter never changes it.

Observed attribution checks were:

| Case | Headcount | Effective rank |
| --- | ---: | ---: |
| Six distinct frontier validators, no collapse | 6 | 6 |
| Six same-lineage frontier validators, no collapse | 6 | 1 |
| Six initially distinct validators, maximum collapse | 6 | 1 |
| Maximum-collapse frontier plus institution | 7 | 2 |
| Institution alone analytic corner | 1 | 1 |

This demonstrates both merge directions and confirms that the analytic corner
is reachable below the deployment minimum.

## Cost and capability implementation

The selected defense cost is the exact naive pairwise count
`N * (N - 1) / 2`, multiplied by the configured per-comparison cost. The smoke
uses unit cost and exponent reduction 0.0, so raw and effective cost are equal.
The optional exponent-reduction term divides the pairwise cost by
`N ** exponent_reduction`. It is stored and reported separately from the
resolution term.

The resolution-improvement term multiplies a separately configured base
per-comparison resolution. It is never stored as a blended defender-capability
knob. The primary smoke uses base resolution 1.0 and resolution improvement
1.0.

The static baseline is available through the same defense-cost switch and
returns its configured fixed cost of 1.0 at every headcount. The primary attack
cost is `coefficient * rank ** 1.0`; the available superlinear sensitivity is
`coefficient * rank ** 1.5`. Both coefficients are config values.

Capability enters only as the direct attacker-to-defender ratio. No compute to
capability curve exists in the mechanism. The config leaves the sweep ratio
range and powered sample size as `null` and marks full-sweep authorization
blocked.

### Gate a: cost response

PASS. Exact smoke numbers were:

| Validator count | Pairwise checks | Effective defense cost |
| ---: | ---: | ---: |
| 2 | 1 | 1.0 |
| 4 | 6 | 6.0 |
| 8 | 28 | 28.0 |

The static-baseline values over the same counts were 1.0, 1.0, and 1.0.

## Attack mechanisms as built

Arm A and Arm B have different function signatures and mutate different
objects.

Arm A, `run_false_cluster_injection`, receives a completed true attribution.
It adds the configured number of apparent clusters, resolves each forged
cluster probabilistically against true rank and the separate capability terms,
and reports the surviving forged clusters. It does not alter the genuine
similarity matrix or partition. Its measured rank is true rank plus surviving
forged clusters, so it cannot erase the institution.

Arm B, `run_measurement_corruption`, receives the validators, true attribution,
collapse severity, merge config, and corruption config. It rewrites the
pairwise measurement matrix before attribution. Selected genuinely correlated
frontier validators are detached by false-independent readings. A separate
corruption event can write a false-correlated reading between the institution
and a measured frontier cluster, merging the institutional cluster away. It
does not inject false clusters. Defense failure is based on corruption of the
true partition, including an institutional merge, even when the resulting rank
number happens to equal the true rank.

### Gate c: distinct arm effects

PASS. Across the fixed nominal smoke fixture, Arm A produced surviving forged
clusters while preserving every true partition and recording zero corrupted
correlation reads. Arm B injected zero false clusters, corrupted correlation
reads, and produced measured ranks different from true rank.

### Gate d: institution floor

PASS. At maximum collapse, true rank was two in all 128 nominal arm runs. Arm A
preserved the institution in 64 of 64 runs and never measured below the true
rank-two floor.

Arm B showed the expected floor fragility without parameter adjustment. It
merged the institution in 13 of 64 runs, measured rank below two in 2 of 64,
and overcounted true rank in 43 of 64. Its measured-rank range was 1 through 5.
This is a smoke mechanism observation only, not a characterization result.

## Positive controls and variance

### Gate e: known breakage

PASS in both arms:

| Positive control | Arm A failures | Arm B failures |
| --- | ---: | ---: |
| Capability ratio 1,000,000 | 8/8 | 8/8 |
| Rank one, no institution | 8/8 | 8/8 |

The rank-one control failed structurally even though six frontier validator
heads were present, confirming that headcount does not substitute for
independence.

The fixed nominal fixture produced these variance estimates for the operator's
later power calculation:

| Arm | n | Failure mean | Failure sample variance | Rank-error mean | Rank-error sample variance |
| --- | ---: | ---: | ---: | ---: | ---: |
| Arm A | 64 | 0.484375 | 0.2537202381 | 0.546875 | 0.3787202381 |
| Arm B | 64 | 0.781250 | 0.1736111111 | 0.890625 | 0.7656250000 |

These are variance estimates at one smoke fixture, not readings of a crossover
or a proposed capability-ratio range.

## Timing projection

The runner recorded 160 instrument timings. Mean, median, p95, and maximum time
per run were 0.000107540, 0.000092882, 0.000152584, and 0.000256684 seconds.

The stated candidate surface resolution is 25 rank points, including the
analytic corner, by 25 ratio points, by 2 arms, by 2 defense-cost forms, by 2
attack-cost forms. This is 5,000 cells per replicate layer. Using observed p95
time, one replicate layer projects to 0.762920 seconds, or 0.000211922 core
hours. Because power is intentionally unset, the full projection is:

`0.762920 seconds * operator-set powered replicates per cell`

This compute-only estimate follows the existing per-run timing pattern. It does
not include future process startup, serialization, or orchestration overhead,
which may dominate at this instrument's short per-cell runtime.

## Output naming and manifest exclusion

The run ID is `smoke_sybil_scaling_instrument_v1`. It is below
`data/sybil_defense_scaling/`, and every generated filename begins with
`smoke_`. It does not use the authoritative `full_5ac6a2e_` prefix. Future
authoritative selection must use an explicit committed manifest, not a recursive
CSV glob, so this smoke directory cannot enter the authoritative population.

## Interpretations requiring operator confirmation

The design note fixes mechanisms and shapes but intentionally leaves several
numeric or operational details open. The implementation made the following
explicit, config-visible interpretations. None was tuned after the smoke.

1. Epistemic similarity is represented by the cosine shared-lineage
   construction above. Similarity 0.9 and threshold connected components are
   the selected merge rule. Greedy complete linkage is also implemented as a
   config option.
2. Per-participant collapse decay starts at 1.0, advances by 0.2 across a
   three-participant cycle, and converges every frontier signature exactly at
   severity 1.0.
3. The candidate low pole is 0.25 of the effective community. High pole is
   1.0. These remain operator-confirmation items and were not swept.
4. Cost units are normalized: pairwise comparison coefficient 1.0, linear and
   superlinear attack coefficients 1.0, and static baseline cost 1.0. The
   existing Sybil path has invariant cost behavior but no numeric cost unit to
   recover.
5. Exponent reduction is implemented as a structured-efficiency divisor
   `N ** exponent_reduction`. Primary smoke exponent reduction is 0.0, retaining
   exact naive pairwise cost.
6. Resolution probability compares
   `true_rank * resolution_power * attack_cost` with
   `capability_ratio * defense_cost`. This is the explicit coupling between the
   note's cost terms and its resolving-power mechanism.
7. Arm A injects two forged clusters, and its pairwise defense cost counts all
   apparent inputs. Both choices are config fields.
8. Arm B uses `1 - resolution_probability` for both false-independent and
   institution-merge event probabilities, with separate config multipliers.
   Its institution corruption targets the measured cluster containing the
   first frontier member. The configured study has one institution.
9. Defense failure means any surviving false cluster in Arm A, any partition
   corruption in Arm B, or true rank below the configured deployment minimum
   of two in either arm.
10. Capability ratios 0.05 and 1,000,000 are smoke fixtures only. They are not
    candidate range endpoints. The 64 nominal replicates and 8 positive-control
    replicates are validation counts, not a power calculation.
11. The candidate timing resolution is 25 by 25 with both arms and both cost
    sensitivities. It sizes a replicate layer only and does not authorize that
    grid.
12. Reuse of the existing v2 Sybil path is an integration probe. The new rank
    economics and A/B mechanisms remain isolated rather than being inserted
    into shared validated model code.
13. The operator-provided note remains a draft with blank power and ratio-range
    fields. Including that draft on this implementation branch is not treated
    as the pre-registration commit.

## Anomalies and surprises

No gate anomaly occurred. Arm B's observed institution loss and occasional
measured rank of one match the pre-registered expectation of floor fragility.
No parameter was changed and the smoke was not rerun.

STOP: awaiting power calculation, capability-ratio range, and pre-registration commit before any full sweep.
