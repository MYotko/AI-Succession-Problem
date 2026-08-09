# Post-Paper Queue

Created: 2026-08-09
Status: queue only. Nothing here is authorized, scheduled, or in progress.

Items deferred out of the defended-collapse and comprehension-gap arcs because
they need a new question, fall outside a task's write scope, or would have
required editing shared production code mid-investigation. Each entry records
what was observed, where the evidence sits, and what pursuing it would require.

Entries are not ranked. Nothing here blocks the paper.

---

## Q1. Health-channel face of defense-accelerates-opacity

**Observation.** Extension arm cell `ext_rr0.050`, reproduction_rate 0.050,
cs = 0.0, odt = 0.3, n = 50 per arm: extinction 33/50 undefended against 24/50
defended, an 18.0 point difference favoring the defense, Fisher p = 0.106. Not
significant, and below the 20 point minimum effect of interest later fixed for
the powered arm.

**Why it is interesting.** It is consistent with the same mechanism recorded in
`candidate_finding_defense_accelerates_opacity.md`, seen from its other side. If
the intuition veto clamps the constraint grab, lowers `c`, and raises
`theta_tech` and L_t, the system it leaves behind is more productive. That
appears in one channel as faster opacity accumulation and would appear in
another as lower extinction under demographic stress. One cause, two faces.

**Why it is not a finding.** At reproduction_rate 0.050 both arms sit at the
population floor, mean final population under 2.5, so the comparison may be
measuring the reproduction floor rather than the comprehension gap. The powered
arm found no final-population effect anywhere between 0.068 and 0.074, with the
confidence interval excluding the minimum effect of interest at 4 of 4 rungs.

**What pursuing it requires.** Its own pre-registration, with a minimum effect
of interest justified independently rather than from the observed 18 points, a
power calculation at registration time, and a rung range where extinction has
genuine variance. That means below 0.058, since extinction is a structural zero
at and above 0.066. Ideally the same design tests both faces together, adding
extinction as an outcome alongside the opacity accumulator, rather than
separating them into different arms as happened by accident here.

**Evidence.** `data/comprehension_gap_sweep_v2_capability_coupled.csv`, rows with
`cell_label = ext_rr0.050`.

---

## Q2. Successor policy is hardcoded, so a policy under test cannot survive succession

**Observation.** `simulation/model.py:848` constructs every successor with
`policy='optimize_u_sys'`, and the v2 path at `model.py:1415-1416` hardcodes
`'optimize_u_sys_v2'`. Only the initial `successor_ai` can be supplied by the
caller, through the constructor parameter defaulted at `model.py:250`.

**Consequence, measured.** Supplying a `gradual_opacity` successor makes
succession fire nine times and capability compound to 38.4x, but the policy
under test is replaced after the first succession and `max_opacity_reached`
collapses to the default 0.1. This closed the faithful route for the
comprehension gap redesign, which then had to lower `runaway_threshold` instead
and accept a boundary-regime qualification on every figure it produced.

**What fixing it would enable.** Studying any non-default policy across
generational capability growth, which is currently impossible. It would also
allow the comprehension gap question to be re-asked at default calibration,
retiring the boundary-regime qualification.

**Caution.** This is shared production code on the succession path, used by
validated sweeps. Any change needs regression checks against the Pattern 1
cliff results and the gate 4 material, both of which depend on succession
behavior.

---

## Q3. Capability growth rate is config-driven in the v2 path and hardcoded in the v1 path

**Observation.** `model.py:1414` reads
`self.config.get('successor_capability_growth_rate', 1.5)`, while the v1 path at
`model.py:850` hardcodes `self.ai.capability * 1.5`.

**Consequence.** A configuration that sets the growth rate silently has no
effect on v1-path runs. Nothing currently depends on this, since no v1 sweep
sets the key, but it is a live trap for the next one that does.

**What fixing it requires.** Making the v1 path read the same key, with a
regression check that the default of 1.5 leaves existing results unchanged.

---

## Q4. Convergence strength is read from a module constant in the v2 metrics path

**Observation.** `simulation/metrics.py:666`, inside
`calculate_system_metrics_v2`, uses the imported module constant
`CONVERGENCE_STRENGTH`. The v1 path at `metrics.py:929` and `:934` correctly
reads `cfg.get('convergence_strength', 1.0)`.

**Consequence.** Any v2-mode sweep that varies `convergence_strength` through
configuration would silently ignore the entire axis and produce a flat result.
The comprehension gap sweep escaped this only because it runs the v1 path:
`is_v2_mode` is set from `config.get('policy') == 'optimize_u_sys_v2'` at
`model.py:191`, and the sweep sets no `policy` key.

**Why it matters more than it looks.** The comprehension gap arc lost
considerable time to a flat convergence_strength axis caused by a different
defect. A v2-mode repeat would hit an identical symptom from an unrelated cause,
and the diagnosis would not transfer.

**Status.** Not fixed. Shared production code, outside the write scope of the
tasks that found it.

---

## Q5. Policies cannot see the quantity the alpha penalty constrains

**Observation.** The `model_state` dict passed to policies
(`model.py:729-740`) exposes `step`, `prev_c`, `population`,
`population_history`, `h_n_history`, `L_t_history`, `avg_well_being`,
`resource_history`, and `hn_composite_method`. It does not expose `theta_tech`,
`frontier_velocity`, `bio_bandwidth`, or `theta_capability`.

**Consequence.** A policy that wants to respond to the frontier the governance
speed limit constrains has to proxy it through `L_t_history`, since L_t carries
`theta_tech` multiplicatively. That is what the redesigned `gradual_opacity`
policy does. The proxy is defensible but indirect, and it drags in `h_eff` and
`psi_inst` alongside the term of interest.

**What fixing it requires.** Adding the derived quantities to `model_state`.
This is shared step logic, so it needs a check that no existing policy changes
behavior, which should be straightforward since the change is additive.

---

## Q6. Default-regime inertness is documented but not resolved

**Observation.** `convergence_strength` has no within-generation effect at
default calibration. Recorded in `default_regime_convergence_inertness.md`, with
the frontier-to-bandwidth ratio at 0.2 to 0.5 against a threshold of 1.5, proven
by bit-identical trajectories at cs=0.0 and cs=2.0 under a shared seed.

**Status.** This is a property of the substrate configuration, not a defect, and
the cross-check confirmed no published claim depends on it. It sits here only so
that a future experiment intending to vary convergence_strength does not
rediscover it from scratch. Resolving it properly means Q2, since capability
growth through succession is the faithful route into the runaway regime.
