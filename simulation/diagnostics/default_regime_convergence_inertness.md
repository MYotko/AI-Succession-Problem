# Default-Regime Inertness of convergence_strength

Date: 2026-08-09
Status: documented finding, no action implied
Scope: property of the substrate configuration at default calibration, nothing more

## Finding

At default calibration, `convergence_strength` has **no within-generation
effect**. It is not merely weak. It is exactly zero.

## Evidence

`convergence_strength` enters the model in exactly one place, as a multiplier on
`runaway_term`:

```python
runaway_term = max(0.0, (frontier_velocity / bio_bandwidth) - runaway_threshold)
theta_tech   = max(0.01, r_bio * (1.0 - c_avg) * capability
                   * np.exp(-alpha * convergence_strength * runaway_term))
```

`simulation/metrics.py:930-934`, the v1 path. When `runaway_term` is zero the
exponential is `exp(0) = 1` and `convergence_strength` drops out of the
arithmetic entirely.

It is zero at default calibration. The frontier-to-bandwidth ratio sits between
**0.2 and 0.5** against a default `runaway_threshold` of **1.5**, roughly a
seventh of the boundary. Located by sweeping the threshold and observing where
outcomes begin to respond: no response at 1.5, 1.0, or 0.5; response at 0.2 and
below.

Established directly rather than inferred. Under a shared seed, with every other
parameter held fixed, `convergence_strength = 0.0` and
`convergence_strength = 2.0` produce **bit-identical** L_t and population
trajectories over 120 steps. Identical output across the full range of a
parameter is proof that the parameter is inert, not evidence that its effect is
small.

Configuration used: `ai_policy='gradual_opacity'`, phi 10.0, alpha 1.2,
reproduction_rate 0.075, 200 agents, `frontier_floor` 0.02, capability 1.0,
generation 1.

## Scope of the claim

This is a property of the substrate at this calibration. It is not a defect, not
a finding about the framework's architecture, and not a claim that the
convergence forces are ineffective in general. The governance speed limit is
built to engage when the frontier outruns biological bandwidth. In this
configuration the frontier never does, so the limit correctly does not engage.

Capability is the reason. It is set at construction and changes only at
succession, so within a single generation the frontier-to-bandwidth ratio has no
mechanism to grow toward the boundary. In the 2,800-row comprehension gap sweep,
`final_ai_generation` was 1 in every row.

## Cross-check: does any published claim depend on this?

**No, and none is expected to.** The Pattern 1 runaway-penalty cliff operates
through succession economics, a different channel. It becomes active because
succession multiplies capability by the successor-to-incumbent ratio, pushing
`capability * theta_capability / bio_bandwidth` past the threshold. The recorded
cliff observations are all at successor capability ratios of 2.5x and above
(`simulation/diagnostics/gate4_v20_validation_summary.md` and the Pattern 1
material in the diagnostics snapshot), which is a between-generation effect, not
a within-generation one.

The existing record already says so independently. `constitutional/
CQ-01-bootstrap-defence-layer.md:81-82` states that Gate 4, runaway-regime
validation, is "not currently applicable. No current substrate operates in the
runaway regime where these equations" apply. Gate 4 is marked pending for the
same reason.

So the two statements are consistent and describe the same fact from different
directions: no substrate reaches the runaway regime within a generation, and the
only channel that reaches it does so through succession.

## Consequence for experiment design

Any experiment intending to vary `convergence_strength` and observe a response
must first put the system in a regime where `runaway_term` is positive. Two
routes exist:

1. Let capability grow through succession until the frontier genuinely outruns
   bandwidth. Faithful, and leaves the boundary where it is.
2. Lower `runaway_threshold` from configuration. Effective, but it redefines
   where the boundary sits and qualifies every resulting figure.

The comprehension gap sweep uses route 2, after route 1 was found closed by the
hardcoded successor policy at `simulation/model.py:848`. See
`comprehension_gap_redesign_note.md`.
