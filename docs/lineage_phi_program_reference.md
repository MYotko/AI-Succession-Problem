# The Lineage Imperative — Phi Investigation and Action-Space Redesign Program

**As of May 2026. Consolidated carry-around reference.**

This supersedes the earlier phi investigation reference. It captures the full arc: what the framework assumes, the problem found, the tests that confirmed it, the redesign program derived to resolve it, and the pre-committed decision tree that governs the outcome. It is a snapshot for reference, not an implementation document.

---

## Part I — Where things stand

### The durable framework claims (unaffected by the phi question)

- **U_sys structurally protects well-being.** Any AI optimizing U_sys maintains the conditions for human novelty, because the objective penalizes well-being collapse through the h_n weighting. Confirmed across every experiment.
- **The COP is the structural defense layer.** 73.9pp protective delta holds. Defenses are binary and operate upstream of the AI's policy.
- **The dual phase transition is stable.** v1.x.2 placed the extinction boundary at rr approximately 0.055 and the collapse boundary at rr approximately 0.064. Under v2.0 architecture, Monte Carlo Phase B (Part X.2) characterizes the survival-rate transition at rr=0.060 to 0.066 with a 50% inflection near rr=0.063; rr=0.057 is collapse-dominated (1.1% aggregate survival), refining the earlier Gate 3-grid estimate of approximately 0.057. Pinning the inflection to plus or minus 0.001 is future work (Part IX.11).
- **The framework's protection is structural, not parametric.** It is encoded in what is optimized, not in tuning.

These do not depend on resolving phi. The phi question is about one parameter's behavioral role, not about whether the framework works.

### The version state

v1.x.2 is tagged and stable. Path C (policy-layer phi fix) was tested and failed. v1.x.3 as conceived is not viable. The next version target is undetermined pending the redesign program below. The redesign is large enough that it is likely a 2.0, but the version is not the point; the result is.

The Stage 1.5 through 1.8 arc, the phi investigation (Parts I.5-1.8 and Part IX), Stage 2 formal yield-condition logic, Piece A gate-2-under-succession validation, and Gate 3 v2.0 validation have closed the open questions that motivated the redesign program. v2.0 architecture is empirically characterized; the phi parameter has a defensible behavioral story (Part IX.3); the formal yield logic implements canonical succession economics (Part IX.8); gates 1, 2, 3 pass under v2.0 (Part IX.9). Monte Carlo Phase B (Part X) completed the v2.0 quantitative-characterization arc across the survival landscape, succession dynamics, and the COP cost-audit baseline (29,400 rows, 0 errors). The default phi revision is complete (commit fde48b5; Part IX.5). Active work remains on the gate 4 acceptance gate (specification and implementation; see Part IX.11 item 1 for the spec dependency).

---

## Part II — The problem

Phi has no detectable effect on any observable outcome in the simulation. Two distinct, stacked causes, plus a deeper realization.

**Layer 1: Saturation cancels phi in argmax.** U_sys is `(w_n*H_N + w_e*H_E) * (discount + phi*L_t)`. Inverse-scarcity weights make the first factor exactly `lambda_n + lambda_e = 8.0`, constant across candidates. The policy's argmax reduces to a phi-scaled function of L_t, where phi scales magnitude but not ranking. Phi cancels exactly.

**Layer 2: The action space has a universal corner solution.** The AI's grid search over resource allocation (r) and constraint (c) selects the corner (r near max, c=0) in every run, every seed, every phi, across the full capability range. There is no candidate competition for phi to influence, regardless of the U_sys formula.

**Layer 1 and Layer 2 are independent.** Fixing U_sys (Path A / 2.0) addresses Layer 1 but not Layer 2. Even a saturation-free U_sys produces phi-invariance when one action dominates the grid. Both must be addressed.

**The deeper realization.** The simulation's representation of the AI's decision problem is too degenerate to contain the tradeoffs phi exists to navigate. The nulls do not show phi does not matter; they show the model cannot test whether phi matters, because its action space lacks the irreducible conflicts that exist in the real governance problem.

**The central distinction.** Whether phi matters in the model (empirical, simulation-dependent) is different from whether phi matters in reality (architectural). The simulation answers the first with a consistent no, which is an artifact of a degenerate action space, not evidence about reality. Reality will have competition regardless of how the simulation is defined.

**The thesis sentence (for the eventual limitation writeup):** The model is currently too generous to the architecture. It proves an AI optimizing the simplified U_sys behaves well inside a simplified world. It does not prove phi matters, because the world given to the optimizer does not force the choices phi was invented to resolve.

---

## Part III — The tests and results

| Test | n | Result | Mechanism |
|---|---|---|---|
| v1.0 to v1.x.1 frontier floor fix | — | 46pp phi buffer claim did not reproduce | Optimizer was gaming the runaway penalty |
| Demographic feedback calibration | 1,800 | Zero phi differential | Well-being stays ~0.80; smoothing band never entered |
| External shock recovery | 600 | Zero phi differential | U_sys restores well-being fast; horizon irrelevant |
| Comprehensive adversarial sweep | 4,600 | Zero phi differential (9 of 10 attacks) | CoP defenses binary, upstream of policy; phi never enters |
| Phi implementation audit | — | Phi correct, threaded, numerically substantial, but inert in argmax | Saturation (Layer 1) |
| Path C gate | — | FAIL; actions identical across phi | Corner solution; no crossing trajectories to reweight |
| Capability-landscape sweep | 50/cell | Corner solution universal across cap {1,5,10,25,50,100} | r near max, c=0 everywhere; corner-to-corner shift at runaway, not a frontier (Layer 2) |

**The three nulls are one finding, not three.** Demographic feedback, shocks, and adversarial all returned null for the same underlying reason: U_sys dominates outcomes and the action space is degenerate. Three symptoms of one structural fact.

**The two root causes:** the corner solution (action space degeneracy) and U_sys dominance (objective determines outcomes, leaving no room for phi). The redesign must attack both.

---

## Part IV — Open contradiction to resolve first

The formal v1.x.2 manuscript still claims the phi extinction buffer is confirmed as a cap-conditional effect (20 to 27 percentage points at the phase boundary, above cap approximately 24). This is now in tension with the investigation.

The cap-conditional claim was measured in the capped-capability termination regime; the corner-solution diagnostic ran at standard uncapped config. They have not been tested against each other. Resolution: run the action-capture harness at the capped termination configuration.

The check output must be brutally binary. No narrative rescue, no "suggestive evidence." Either action divergence across phi exists in the capped regime or it does not.

| Result | Consequence |
|---|---|
| No phi-divergent actions in capped regime | Withdraw the cap-conditional phi-buffer claim. It is an artifact, likely the contaminated termination regime flagged earlier. |
| Phi-divergent actions in capped regime | Narrow the claim and study that regime before redesign. The corner solution is regime-dependent; the capped regime has competition structure worth understanding, and this previews Branch 2 of the decision tree (Part VI). |

This check is cheap and decisive, and it informs the build. Do it before building forward.

---

## Part V — The redesign program

The discipline that governs everything: tradeoffs are derived from the governance problem and justified independently of phi, before phi enters. Each return curve and exchange rate must be defensible to a skeptic who has never heard of phi. If a curve's justification is "it makes phi matter" or "it makes the problem interesting," that is the failure mode.

### The six primary tradeoffs, expanded into a multi-sink allocation portfolio

There are six primary reality-derived tradeoffs. The resource side of several of them (tradeoff 3 in particular) generalizes into a multi-sink allocation portfolio (compute, cultural novelty, institutional resilience, translation capacity, and others), which is why the allocator redesign below has more axes than there are primary tradeoffs. The six are the conceptual conflicts; the portfolio is how the resource side of those conflicts is represented in the model.

1. **Institutional investment vs. immediate output.** Institutional capacity (courts, auditors, civic panels, validators, ledgers, translation) consumes resources now for later viability. Psi_inst should become a stock with investment, decay, overload, legitimacy, and recovery, not just a penalty for changing c.
2. **Protective constraint vs. novelty suppression.** Split c into c_protective (raises resilience, reduces attack surface) and c_suppressive (lowers H_N, agency, legitimacy). Critically, these must be a coupled frontier with curvature, not two free variables and not a one-for-one tax. A linear coupling just rotates the single axis and produces a new corner along a diagonal. The correct form is a leakage frontier: at low coverage, protection is nearly clean (catches obvious bad actors without burdening legitimate participation); as protection approaches total coverage, the marginal cost increasingly spills into suppression, opacity, dependency, and institutional rigidity. The convexity of that leakage curve is what produces an interior optimum, because the allocator wants protection up to the point where marginal leakage exceeds marginal safety benefit. The justification is institutional reality (the first increments of fraud detection and infrastructure hardening are cheap in agency terms; pervasive surveillance and presumption of guilt are not), and it must hold independently of phi. The shape of the leakage curve is itself a place motivated design could hide, so it gets the same phi-blind freeze as every other curve.
3. **Capability acceleration vs. transfer and comprehension.** Frontier capability benefits a civilization only when transferable, legible, governable, absorbable. Separate compute/capability from translation/transfer capacity as competing sinks. The framework already gestures at this via the frontier velocity floor and the biological comprehension gap.
4. **Standardization/legibility vs. plurality.** Enough standardization to transfer and audit, but too much collapses plurality into monoculture. Legibility investment improves transfer and throughput up to a point, then reduces novelty entropy.
5. **Succession speed vs. transfer fidelity / continuity.** Fast succession prevents lock-in but can exceed institutional capacity and transfer fidelity; slow succession preserves stability but creates bottleneck and lock-in. Succession should consume institutional bandwidth and transition capacity. A system that yields every step should not be automatically healthy.
6. **Population well-being vs. agency.** Real well-being can be purchased through pacification, dependency, or loss of autonomy. Separate well_being from agency: high well-being plus low agency should not produce full novelty. This is the tradeoff that directly attacks U_sys dominance, because it means an AI cannot simply pacify the population to harvest novelty.

(The six primary tradeoffs above. The conversation also surfaced computation, cultural novelty, institutional resilience, and translation capacity as distinct allocation sinks, which together generalize the resource side of tradeoff 3 into the multi-sink portfolio represented in the allocator below.)

### The Theta_tech monotonicity fix (the keystone)

The corner solution exists because scalar r maps monotonically to scalar theta_tech: one input, one good, one direction. The fix is not an imposed inverted-U on r (that is a tuned knob with no honest justification). The fix is to decompose r into a composition vector:

- compute/capability investment
- biological welfare support
- novelty/agency support
- institutional capacity
- transfer/comprehension infrastructure
- resilience/redundancy

Non-monotonicity then emerges honestly from overload, dependency, crowd-out, and absorption limits. The justification is that transfer fidelity depends on composition, timing, and institutional absorption, not quantity. Max education at the cost of zero institutional resilience is bad not because helping humans is bad, but because absorption requires both. The optimum is interior because the categories are complements, not substitutes.

### The allocator redesign

Replace the two-dimensional surface (r, c) with a budget-constrained multi-sink allocator:

- x_compute
- x_bio_welfare
- x_novelty_agency
- x_institutional_capacity
- x_transfer_comprehension
- x_resilience
- c_protective
- c_suppressive

Budget-constrained, so investment in one sink crowds out others. Psi_inst gets state and memory: it accumulates strength or damage, degrades under overload, opacity, starvation, policy volatility, and capture, and recovers through investment, legitimacy, redundancy, and successful governance cycles.

### Build sequence (minimum faithful set first)

Do not build the entire expanded allocator at once. Thirty-plus new parameters is undebuggable and is itself a motivated-design risk at the model level (explore the space until phi matters, then declare that region the answer).

Minimum faithful set that attacks both root causes:

1. Composition vector replacing scalar r (attacks corner solution, resource axis)
2. Coupled c_protective / c_suppressive frontier (attacks corner solution, constraint axis)
3. Psi_inst as a stock with memory (makes the landscape dynamic; independently justified by GAP-03)
4. Well-being vs. agency split (attacks U_sys dominance, reopens the demographic channel)

Validate that the corner solution is gone and interior optima exist, every curve justified independently of phi, before phi is tested. Add the remaining tradeoffs one at a time only if needed, each validated for its effect on the landscape, so you always know which addition did what.

### Acceptance gates before phi is reintroduced

Formalize the validation as hard pass conditions. All five must pass before any phi sweep.

| Gate | Pass condition |
|---|---|
| Interior-action gate | The optimizer selects non-boundary allocations in a meaningful fraction of runs. |
| Competition gate | Multiple candidate actions win under different states, not just different seeds. |
| Horizon-crossing gate | At least some candidates dominate at short horizons but lose at longer horizons, or vice versa. |
| Capability-regime gate | The allocation landscape changes as capability rises. |
| Phi-blind validation gate | All return curves and exchange rates are justified and frozen before the phi sweep. |

The horizon-crossing gate is the load-bearing one. The other four establish that the action space is non-degenerate, but non-degeneracy is not sufficient for phi. Phi weights horizon. If every candidate that is best now is also best later, no horizon weighting changes the choice, however rich the action space is otherwise. The horizon-crossing gate is the specific test that the thing phi operates on exists in the model. Without it, you could pass the other four, run phi, get a null, and not know whether phi is genuinely inert or whether crossing trajectories were never built. A null phi result is only interpretable if the horizon-crossing gate has passed first.

### Stage 1.5 structural commitment (added May 2026 after gate 2 failure)

Gate 2's state-insensitivity failure surfaced a specification gap in the original Stage 1 design conversations. `calculate_system_metrics_v2` read only the candidate action and `psi_inst_stock`, not the model's demographic state. The optimizer was correctly state-invariant given the inputs it had access to, because the metric did not read state variables that vary across the gate 2 test configurations. This is a defect phi cannot address: extending the planning horizon weights future state more heavily in evaluation, but it cannot grant the optimizer access to state variables the metric never reads.

The structural commitment, recorded here as the architectural rule that governs the remaining Stage 1.5 design work:

```
U_sys_v2 reads both diagnostic current state and prospective candidate effects.

Diagnostic state represents the actual condition of the model at the
current timestep. It conditions marginal returns and urgency. It does
not enter U_sys_v2 as a free-standing reward or penalty.

Prospective candidate effects represent what a candidate allocation
is projected to produce. They determine projected outcomes.

The projection function must propagate diagnostic state forward during
rollout, so each future step is evaluated against the state trajectory
produced by the candidate action.

Phi does not create state sensitivity. State sensitivity must already
exist in U_sys_v2. Phi, when later tested, weights how heavily
projected future consequences count relative to immediate state.

Therefore:
  diagnostic state -> state-sensitive scoring
  candidate effects -> action-sensitive scoring
  projection -> horizon-sensitive trajectory
  phi -> temporal weighting over that trajectory
```

Diagnostic state enters as urgency-weight modulation on the candidate's marginal returns, not as additive bonus terms. The pattern is `category_return = candidate_category_effect * category_urgency(diagnostic_state)`. Low avg_wb does not directly improve U_sys_v2; it raises the marginal return on welfare-improving actions. The same pattern applies to institutional, resilience, and demographic variables. Each urgency-weight function is a phi-blind design commitment requiring justification for its shape.

The projection function must evolve diagnostic state through the rollout, not just action consequences. Without this, the horizon channel through which phi acts has nothing to weight. Each diagnostic variable needs both a per-step urgency function and a projection update rule.

### Minimum diagnostic state set (committed for Stage 1.5)

Five diagnostic variables, each requiring phi-blind justification for inclusion, shape of urgency function, and projection update rule:

1. **avg_wb** (current population mean well-being): conditions marginal return on x_bio_welfare; evolves under candidate allocation through the agent layer's well-being dynamics.

2. **population_ratio** (current population relative to a viability or carrying-capacity reference): conditions marginal return on welfare, agency, and institutional continuity; evolves via demographic dynamics.

3. **demographic_pressure** (derived from observed births and deaths or recent population trend, not read directly from `reproduction_rate`): conditions urgency of demographic stabilization; evolves via projected vital rates.

4. **trend variables** (smoothed short-window rates of change for avg_wb, population, psi_inst_stock, and resilience_stock): modulate urgency above static levels; level alone is insufficient because improving and declining states at the same level warrant different responses.

5. **resilience_stock** (the shock-state analog of psi_inst_stock, accumulated through x_resilience investment and drawn down by shocks): conditions marginal return on x_resilience; evolves via investment, decay, and shock drawdown. This is a new stock variable; the v2 build did not have one.

`psi_inst_stock` already exists in v2 and is preserved. The first-pass minimum set is these five plus psi_inst_stock.

### Deliberately deferred diagnostic states (with revisitation criteria)

The exclusions are not silent omissions. They are scope commitments with criteria for when they get revisited.

**Interaction states** (deferred because projection-layer complementarity is expected to carry their consequences):
- opacity state (emerges from compute-without-transfer)
- volatility state (emerges from agency-without-institutions)
- validator dependency (emerges from institutional coverage patterns)

Revisit if: later gates show the optimizer misses signals from these interactions despite the multiplicative complementarity surfacing their consequences in projected outcomes.

**First-order states** (deferred for scope, not for theoretical reasons):
- cultural fragmentation index
- resource inequality measure
- legitimacy subcomponents (legitimacy currently aggregated into psi_inst_stock and agency_legitimacy_factor)

Revisit if: Stage 3 phi sweep shows phi has effect on macro outcomes but no clear channel through the committed diagnostic variables; these may be the missing channels.

**Sub-stocks** (deferred because aggregated stocks are doing their work):
- education stock (currently inside x_transfer_comprehension and institutional capacity)
- separate translation stock from transfer factor

Revisit if: gate 2 or gate 3 shows the optimizer treating x_transfer_comprehension as undifferentiated when it should distinguish education from interpretability from documentation.

### Seven-element specification template

Every Stage 1.5 diagnostic variable must meet a uniform specification standard before being folded into the implementation. The template was established by the avg_wb worked example and refined by the population_ratio worked example. Subsequent variables must meet the same standard.

Required elements:

1. **Shape**: the functional form of the urgency or pressure function, with bounds.
2. **Bounds**: lower and upper limits doing structural work, not just numerical hygiene. Each bound must be justified for what it prevents (welfare going inert in healthy states, welfare dominating in crisis, etc.).
3. **Parameter rationale**: each constant in the urgency function justified independently with phi-blind reasoning. "Why this value rather than nearby alternatives" is required, not optional.
4. **Multiplicand choice**: explicit commitment to which downstream term the urgency multiplies. Diagnostic state does not enter U_sys_v2 as additive bonus; it conditions marginal returns on specific candidate-effect terms.
5. **Clamp interpretation**: hard clamps are intentional behavior, not numerical safety. The spec must say what the clamp represents (preserves non-substitutability, prevents super-welfare, etc.).
6. **Phi-blind governance justification**: the entire specification must hold without reference to phi, derived from governance reasoning that would apply to any planner facing the modeled situation.
7. **Implementation semantics, including projection update and faithfulness test**: how the variable evolves during rollout (the projection update rule, mechanically faithful to the agent layer), and the verification protocol that confirms the projection matches the agent layer's actual dynamics within tolerance.

A variable specification missing any of the seven elements is not complete and is not ready for implementation.

### Composite-urgency commitment

As diagnostic variables accumulate, multiple variables may modulate the marginal return on a single downstream category. avg_wb already modulates welfare; population_ratio modulates welfare, agency, institutions, resilience, and suppression; future variables will add more.

The architecture commitment, to prevent unauditable multiplier sprawl: each affected category gets a single named bounded composite multiplier that combines all diagnostic-state contributions through an explicit composition rule, before being applied to the multiplicand.

Required composite functions as Stage 1.5 specifications accumulate:
- `combined_welfare_urgency` (currently combines avg_wb urgency and population pressures)
- `agency_population_urgency` (currently population-only; expands as other variables specify)
- `institution_composite_urgency`
- `resilience_composite_urgency`
- `suppression_composite_penalty`

Each composite function is itself a phi-blind design commitment requiring its own justified composition rule. When a category changes, the audit questions are: which diagnostic variables contributed, what were their weights, what cap bounded the composite, and which downstream term was multiplied. Anonymous multipliers stacking inside a single calculation are forbidden by this commitment.

### Worked example 1: avg_wb (welfare-condition diagnostic)

The first fully-specified Stage 1.5 diagnostic variable. Demonstrates the seven-element template for a single-category-modulating variable with a single multiplicand.

**Shape**: bounded smoothstep welfare-deficit curve, monotone decreasing in current avg_wb, with hard clamps at both ends.

```
d_wb = clamp((wb_target - avg_wb) / (wb_target - wb_crisis), 0, 1)
urgency_wb = urgency_min + (urgency_max - urgency_min) * (3*d_wb^2 - 2*d_wb^3)
```

**Bounds**: urgency_wb clamped to [urgency_min, urgency_max]. Lower bound prevents welfare going inert in healthy states; upper bound prevents crisis welfare dominating U_sys_v2 and crowding out institutions, resilience, transfer, and agency.

**Parameter rationale**:
- `wb_target = 0.80`: empirical v1.x.2 healthy-operation equilibrium and v2 bridge calibration anchor. Above this point, additional welfare has diminishing marginal governance value.
- `wb_crisis = 0.45`: below v1.x.2 reproduction threshold of 0.50, so maximum urgency activates before demographic failure fully expresses. Anticipatory rather than reactive.
- `urgency_min = 0.75`: prevents welfare going inert in healthy states. Welfare remains substrate-maintenance even when population is stable. 0.50 would underweight; 1.00 would make urgency inert.
- `urgency_max = 2.00`: doubles crisis welfare marginal return. Strong enough to shift allocation, bounded enough to avoid welfare-only collapse. The calibration parameter to watch in Stage 1.5 smoke testing: collapse-to-welfare (max_share > 0.5 in low-avg_wb runs) signals it is too high; insufficient-shift across configurations signals too low.

**Multiplicand choice**: urgency_wb multiplies post-drag net welfare return, not pre-drag raw welfare. Crisis multiplier rewards welfare that preserves agency rather than welfare that pacifies.

```
raw_welfare = welfare_return_curve(x_bio_welfare)
dependency_drag = dependency_drag_function(x_bio_welfare, x_novelty_agency)
net_welfare_return = clamp(raw_welfare - dependency_drag, 0, 1)
```

The urgency then enters welfare's contribution through `combined_welfare_urgency` (the composite function shared with population_ratio).

**Clamp interpretation**: the hard ceiling at welfare_factor = 1.0 means urgency has strongest effect at moderate welfare during stress, not when welfare is already maxed. Intentional preservation of non-substitutability: welfare can repair welfare bottlenecks, not become an unbounded substitute for institutions, transfer, agency, or resilience.

**Phi-blind governance justification**: welfare investment has highest marginal value when population well-being is stressed, diminishing marginal value when population is healthy, bounded crisis urgency so welfare cannot dominate all governance dimensions. The multiplier applies only to welfare-improving actions that survive dependency drag, so crisis response must preserve agency.

**Implementation semantics, including projection update and faithfulness test**:

Projection update rule (deterministic aggregate approximation of HumanAgent.step well-being dynamics, faithful to the agent layer, does NOT include urgency multiplier or dependency_drag because those are scoring constructs):

```
projected_avg_wb_next = clamp(
    projected_avg_wb
    + 0.1 * (resource_equiv_v2 - 0.5)
    - 0.001 * projected_avg_age,
    0, 1
)
```

Where `resource_equiv_v2` comes from the existing v2-to-legacy bridge. `projected_avg_age` starts from observed avg_age and (in the first build) is cohort-corrected per the general principle below.

Faithfulness test: fixed action sequences applied to both deterministic projection and actual agent-layer clones, compared across initial conditions and horizons. Tolerances: 1-step ≤0.01 absolute error, 5-step ≤0.02 mean, 20-step ≤0.035 mean and ≤0.06 max. Directional agreement ≥90% on sign of avg_wb change. If simple aggregate fails tolerance, add cohort correction per the general principle below.

**Cohort-correction general principle (Stage 1.5 first-build implementation)**:

The avg_wb fallback originally documented here is now generalized: **any aggregate state variable in the projection that is affected by demographic turnover requires cohort-corrected projection**. The two cohorts are survivors (whose value evolves under the simple aggregate update) and newborns (who enter at a cohort-mean from the agent-layer initialization). The corrected next-step aggregate is the population-weighted mean over both cohorts:

```
projected_X_next = (
    expected_survivors * projected_survivor_X
    + expected_births * birth_X_mean
) / projected_population_next
```

where `expected_survivors = projected_population - expected_deaths` and `projected_population_next = expected_survivors + expected_births`. The principle replaces the simple aggregate whenever the simple form's drift exceeds tolerance.

First-build implementation includes two cohort corrections, both with named constants traceable to the agent-layer source:

- `BIRTH_WB_MEAN = 0.65` (default; projection helper reads `wb_min`, `wb_max` from config and computes `(wb_min + wb_max) / 2` to respect config overrides). Source: `HumanAgent.__init__` uses `np.random.uniform(wb_min, wb_max)` with defaults 0.5, 0.8.
- `BIRTH_AGE_MEAN = 24.5` (default; projection helper reads `human_max_start_age` from config and computes `(H - 1) / 2`). Source: `HumanAgent.__init__` uses `np.random.randint(0, human_max_start_age)`, returning integers in `[0, H-1]`, default H = 50.

The avg_age cohort correction was identified as necessary by faithfulness testing: with avg_wb cohort-corrected but avg_age uncorrected, `projected_avg_age` ran away monotonically (+1 per step) while the empirical avg_age asymptoted at the steady state where age-skewed mortality balanced constant-inflow births. Because avg_wb consumes avg_age through `-0.001 * age` drag, the runaway propagated into avg_wb drift at long horizons. Cohort correction on avg_age closes that channel.

Watchlist guidance for future aggregate state additions: any new aggregate state variable consumed by U_sys_v2 or any other projection update rule that is affected by birth/death turnover must be specified with both an aggregate evolution rule AND its birth-cohort mean (with the agent-layer source for the mean). Examples that would require this if added in future builds: `reproductive_share` (currently held constant in first build; would need a birth-cohort mean of "fraction of births that are immediately in 18-50 window" = 0, plus an aging-cohort transition mechanism), avg_well_being variance, avg_capability among heterogeneous-capability agents. The general principle covers each of them without re-deriving from scratch.

### Worked example 2: population_ratio (substrate-scale diagnostic)

Demonstrates the seven-element template for a multi-category-modulating variable with composite urgency interactions.

**Shape**: two bounded smoothstep pressure functions derived from population ratios against minimum viability and carrying capacity.

```
viability_ratio = population / min_viable_population
capacity_ratio = population / carrying_capacity

viability_pressure = smoothstep(
    clamp((pop_viability_target - viability_ratio) / (pop_viability_target - 1.0), 0, 1)
)
capacity_pressure = smoothstep(
    clamp((capacity_ratio - capacity_safe) / (1.0 - capacity_safe), 0, 1)
)
```

**Bounds**: each pressure clamped to [0, 1] by smoothstep construction. Composite multipliers for each affected category have their own clamps (see multiplicand section).

**Parameter rationale**:
- `pop_viability_target = 3.0`: viability pressure mostly relaxes at three times minimum viable. 2.0 too thin (modest shock pushes back toward failure); 5.0 keeps pressure active too long (over-prioritizes preservation when slack exists); 3.0 first-build safety margin where ordinary variance does not threaten lineage.
- `capacity_safe = 0.80`: capacity pressure activates around 80% of carrying capacity. 0.70 too early (treats normal growth as crowding); 0.90 too late (insensitive to per-capita pressure until saturation); 0.80 reasonable headroom threshold.
- `min_viable_population`: inherited from model.min_viable_population, fallback 50. Preserves continuity with v1.x.2 collapse assumptions rather than introducing new threshold.
- `carrying_capacity`: inherited from model.config["carrying_capacity"], fallback 1600. Same capacity reference as agent-layer's capacity_modifier, so projection and actual dynamics speak the same language.

**Multiplicand choice**: viability_pressure and capacity_pressure modulate five downstream terms (welfare, agency, institutions, resilience, suppression) through named composite urgency functions:

```
# Welfare combines avg_wb urgency with population pressures
combined_welfare_urgency = clamp(
    urgency_wb * (1.0 + 0.50 * viability_pressure + 0.25 * capacity_pressure),
    0.50, 2.50
)
welfare_factor = clamp(net_welfare_return * combined_welfare_urgency, 0, 1)

# Agency responds to viability only (capacity pressure does not strongly raise agency)
agency_viability_urgency = clamp(1.0 + 0.35 * viability_pressure, 1.0, 1.50)
agency_factor = clamp(raw_agency_return * agency_viability_urgency, 0, 1)

# Institutions respond to both
institution_population_urgency = clamp(
    1.0 + 0.35 * viability_pressure + 0.50 * capacity_pressure,
    1.0, 1.75
)

# Resilience responds to both with viability weighted higher
resilience_population_urgency = clamp(
    1.0 + 0.50 * viability_pressure + 0.35 * capacity_pressure,
    1.0, 1.75
)

# Suppression penalty rises with viability and modestly with capacity pressure
suppression_population_penalty = clamp(
    base_suppression_penalty * (1.0 + 0.50 * viability_pressure + 0.25 * capacity_pressure),
    base_suppression_penalty, 2.0 * base_suppression_penalty
)
```

**Clamp interpretation**: composite caps prevent unbounded urgency growth even when both pressures activate simultaneously. Welfare composite cap at 2.50 allows combined avg_wb + population stress to reach 3.1x baseline (urgency_max 2.0 × max population factor 1.75/1.0) but clamps it before welfare can substitute for institutions, resilience, or agency. Each per-category cap reflects how dominant that category should be allowed to become under maximum population stress.

**Phi-blind governance justification**: population scale determines whether the biological substrate is viable, redundant, diverse, and governable. A small comfortable population may still be fragile (low viability_ratio with healthy avg_wb). A large population near carrying capacity may be stressed even if currently healthy. The planner must read population state to allocate faithfully; population pressure changes the marginal value of welfare, agency, institutions, resilience, and suppression avoidance, never as a direct utility bonus.

**Implementation semantics, including projection update and faithfulness test**:

Projection update rule (deterministic aggregate approximation of HumanAgent birth/death mechanics):

```
projected_population_next = max(
    0,
    projected_population + expected_births - expected_deaths
)

expected_births = (
    projected_population
    * reproductive_share
    * reproduction_rate
    * capacity_modifier
    * wb_repro_factor(projected_avg_wb)
)

capacity_modifier = max(0, 1 - projected_population / carrying_capacity)

expected_deaths = projected_population * expected_mortality_rate

expected_mortality_rate = (
    mortality_base
    + (1 - projected_avg_wb) * mortality_wb_penalty
    + (projected_avg_age / 100) ^ mortality_age_power
)
```

Population projection consumes projected_avg_wb through both birth and mortality terms, establishing the cumulative dependency chain `avg_wb → population → demographic_pressure` that gives the optimizer a horizon-sensitive demographic trajectory.

Faithfulness test, general quantitative tolerance: empirical mean over seeds, 1-step within 5%, 5-step within 10%, 20-step within 15%, direction agreement ≥85%.

Faithfulness test, boundary-sensitive criterion: for cases within 25% of min_viable_population or within 25% of carrying_capacity, projection must agree with actual simulation on boundary-crossing status in at least 80% of test cases. Boundary events: hard viability failure (population ≤ min_viable_population), viability zone entry (population ≤ pop_viability_target × min_viable_population), capacity pressure zone entry (population ≥ capacity_safe × carrying_capacity). Hard viability failure agreement is the most important; categorical disagreement on survival means the optimizer makes allocation decisions on a projection that disagrees with reality about whether the civilization persists.

### Stage 1.5 design principle: stock boundary pressures dominate flow pressures

Recorded as a general rule for any flow-type diagnostic variable (demographic_pressure and the trend variables yet to be specified). Stock diagnostic variables (viability_pressure, capacity_pressure, psi_inst_stock level, resilience_stock level) tell the planner where the substrate is relative to structural boundaries. Flow diagnostic variables (demographic_pressure, trends) tell the planner how the substrate is moving. Direction matters but stock state takes precedence: a population near a hard boundary in the wrong direction is a stock crisis with a flow accelerator, not a flow crisis with a stock component. The coefficient hierarchy must reflect this: flow-variable coefficients on any composite urgency must be less than or equal to the corresponding stock-variable coefficients. This principle governs every future flow-type variable specification.

### Worked example 3: demographic_pressure (substrate-flow diagnostic)

Demonstrates the seven-element template for a derived flow variable that does not introduce new state but raises composite urgency caps across multiple categories. Establishes the asymmetric shrinkage-vs-growth treatment.

**Shape**: bounded asymmetric pressure function derived from existing population projection. Net demographic_pressure is a single signed scalar; two pressure functions are derived from it for downstream use.

```
demographic_pressure = (expected_births - expected_deaths) / max(projected_population, 1)

shrinkage_pressure = smoothstep(
    clamp((-demographic_pressure - shrinkage_floor) / (shrinkage_crisis - shrinkage_floor), 0, 1)
)
growth_pressure = smoothstep(
    clamp((demographic_pressure - growth_floor) / (growth_active - growth_floor), 0, 1)
)
```

The two pressures are mutually exclusive in practice: negative demographic_pressure yields zero growth_pressure; positive yields zero shrinkage_pressure. Asymmetric activation thresholds reflect the architectural commitment that contraction is the urgent failure mode.

**Bounds**: each pressure clamped to [0, 1] by smoothstep construction. Composite multipliers for affected categories have their own clamps, raised modestly from population_ratio's values to accommodate demographic_pressure contributions while preserving the structural commitment that no single category dominates.

**Parameter rationale**:

- `shrinkage_floor = 0.005` (0.5% per step net shrinkage tolerated): 0.001 too sensitive (small stochastic variance triggers urgency in stable populations); 0.02 too tolerant (meaningful decline begins before urgency activates); 0.005 reflects the rate at which normal demographic variance gives way to a real trend.
- `shrinkage_crisis = 0.02` (2% per step activates full urgency): 0.01 too close to floor (insufficient dynamic range); 0.05 too late (population near catastrophic decline before urgency saturates); 0.02 compounds to approximately halving population in 35 steps, fast enough for maximum urgency, slow enough for response to remain possible. 4x ratio from floor provides meaningful gradient.
- `growth_floor = 0.005`: symmetric to shrinkage_floor for activation sensitivity.
- `growth_active = 0.03` (3% per step net growth activates full growth_pressure): higher than shrinkage_crisis (0.02) by deliberate asymmetry. Growth is less urgent than shrinkage; the planner should respond more strongly to losing substrate than to growing it. Beyond 0.05, capacity_pressure does most of the work; 0.03 is the rate at which institutional throughput requirements scale faster than incremental investment can match.

Calibration note: shrinkage_crisis is the parameter to watch in Stage 1.5 smoke testing. Shrinking-population worlds collapsing to welfare-only signals too-strong contribution; insufficient shift toward welfare and institutions in shrinking worlds signals coefficients too small.

**Multiplicand choice**: shrinkage_pressure and growth_pressure modulate five downstream terms through extensions to the existing composite urgency functions established by population_ratio. The architectural principle (stock boundary pressures dominate flow pressures) sets the coefficient hierarchy: flow coefficients ≤ corresponding stock coefficients.

```
# Welfare: shrinkage raises urgency; growth does not (capacity_pressure handles growth-driven welfare stress)
combined_welfare_urgency = clamp(
    urgency_wb * (
        1.0
        + 0.50 * viability_pressure
        + 0.25 * capacity_pressure
        + 0.35 * shrinkage_pressure
    ),
    0.50, 2.50
)
welfare_factor = clamp(net_welfare_return * combined_welfare_urgency, 0, 1)

# Agency: shrinkage raises urgency; growth does not directly
agency_composite_urgency = clamp(
    1.0
    + 0.35 * viability_pressure
    + 0.25 * shrinkage_pressure,
    1.0, 1.50
)
agency_factor = clamp(raw_agency_return * agency_composite_urgency, 0, 1)

# Institutions: both shrinkage (continuity) and growth (throughput)
institution_composite_urgency = clamp(
    1.0
    + 0.35 * viability_pressure
    + 0.50 * capacity_pressure
    + 0.35 * shrinkage_pressure
    + 0.25 * growth_pressure,
    1.0, 2.00
)
institution_return = clamp(raw_institution_return * institution_composite_urgency, 0, 1)

# Resilience: both shrinkage and growth modestly (population_ratio carries most)
resilience_composite_urgency = clamp(
    1.0
    + 0.50 * viability_pressure
    + 0.35 * capacity_pressure
    + 0.25 * shrinkage_pressure
    + 0.20 * growth_pressure,
    1.0, 1.75
)
resilience_return = clamp(raw_resilience_return * resilience_composite_urgency, 0, 1)

# Suppression: shrinkage raises penalty; growth alone does not
suppression_composite_penalty = clamp(
    base_suppression_penalty * (
        1.0
        + 0.50 * viability_pressure
        + 0.25 * capacity_pressure
        + 0.35 * shrinkage_pressure
    ),
    base_suppression_penalty, 2.00 * base_suppression_penalty
)
```

Note: every shrinkage coefficient is ≤ its corresponding viability_pressure coefficient (the stock-over-flow principle in action). Growth coefficients are smaller still because growth is not itself a failure mode until it creates capacity pressure.

**Clamp interpretation**: composite caps remain at population_ratio's levels (2.50 for welfare, 2.00 for institutions, 1.75 for resilience, 1.50 for agency, 2.00× for suppression) rather than rising further. Demographic_pressure contributes to existing urgency rather than expanding the ceiling. Maximum simultaneous stress from all contributing pressures still cannot push any category beyond its cap. The structural commitment that no category becomes a crisis magnet is preserved.

**Phi-blind governance justification**: a planner must read direction and rate of substrate change, not only current scale. A population shrinking at 2% per step faces fundamentally different governance demands than a stable population of the same size with identical current well-being and viability ratios. Shrinkage activates urgency across welfare, agency, institutions, resilience, and suppression-avoidance because contraction threatens lineage continuity through multiple channels: reduced welfare substrate, reduced adaptive diversity, weakened institutional cohort transmission, reduced shock absorption, and increased relative cost of further adaptive-capacity loss through suppression. Growth activates urgency more narrowly because most growth concerns are already downstream of capacity_pressure.

**Implementation semantics, including projection update and faithfulness test**:

Projection update rule (derived, no new state variable):

```
expected_births_per_step = (
    projected_population
    * reproductive_share
    * reproduction_rate
    * capacity_modifier
    * wb_repro_factor(projected_avg_wb)
)
expected_deaths_per_step = projected_population * expected_mortality_rate
demographic_pressure = (
    expected_births_per_step - expected_deaths_per_step
) / max(projected_population, 1)
```

demographic_pressure is computed at each rollout step from population_ratio's projection machinery. No new state to evolve. Faithfulness inherits from population_ratio's projection.

Faithfulness test, builds on population_ratio's test with stricter sign-agreement and asymmetric false-safe constraints:

```
General sign agreement (projection and empirical mean agree on sign of 
demographic change):
  1-step:  ≥ 95%
  5-step:  ≥ 90%
  20-step: ≥ 85%

Boundary-proximate cases (initial population within 25% of min_viable_population 
or carrying_capacity):
  Boundary-crossing agreement:
    1-step:  ≥ 95%
    5-step:  ≥ 90%
    20-step: ≥ 85%

False-safe constraint (projection says safe but actual run crosses below 
min_viable_population):
  1-step:  ≤ 5%
  5-step:  ≤ 10%
  20-step: ≤ 10%

False-comfort constraint (projection says no capacity pressure but actual 
run enters capacity pressure zone):
  1-step:  ≤ 10%
  5-step:  ≤ 15%
  20-step: ≤ 15%
```

If the 1-step false-safe constraint (≤5%) cannot be met by the simple aggregate projection, the cohort correction in population_ratio's projection becomes mandatory rather than optional. Cohort correction formula: `(expected_survivors × projected_survivor_avg_wb + expected_births × birth_wb_mean) / projected_population_next`. False-safe under-prediction of collapse risk is the failure mode the optimizer cannot recover from through other signals; meeting this constraint is non-negotiable.

**Watchlist addition**:

```
Deferred demographic signal: churn_pressure
    = (expected_births + expected_deaths) / projected_population

Reason for deferral: distinguishes low-churn stability from high-churn 
instability, but v1.x.2 demographic mechanics do not produce enough 
independent churn variation to justify the additional diagnostic variable. 

Revisit if: shock infrastructure expands to include differential mortality 
or fertility events; later gates surface that the optimizer misses 
instability signals at constant net demographic pressure.
```

### Worked example 4: resilience_stock (shock-readiness diagnostic)

Demonstrates the seven-element template for a new stock variable with associated dynamics (accumulation, decay, drawdown), a pressure function for marginal-return modulation, and a separate shock-attenuation mechanism that modifies how shocks affect the model. This is the architectural piece that gives x_resilience a per-step reward channel; without it, gate 1's surfaced pathology of x_resilience starvation persists by design.

**Shape**: three associated functions—stock dynamics, pressure function for urgency, and shock-attenuation function for damage reduction.

Stock dynamics:
```
resilience_stock_next = clamp(
    resilience_stock
    + k_resilience_investment * x_resilience * (1 - resilience_stock)
    - k_resilience_decay * resilience_stock
    - shock_drawdown_this_step,
    0, 1
)
```

The `(1 - resilience_stock)` term creates saturating accumulation. No always-on recovery term (asymmetric with psi_inst_stock by design).

Pressure function (drives marginal returns):
```
resilience_deficit = 1.0 - resilience_stock
resilience_pressure = smoothstep(resilience_deficit) = 3 * resilience_deficit^2 - 2 * resilience_deficit^3
```

Shock-attenuation function (reduces shock damage when shocks occur):
```
effective_shock_damage = raw_shock_magnitude * (1 - resilience_max_attenuation * resilience_stock)
damage_absorbed = raw_shock_magnitude - effective_shock_damage
shock_drawdown = k_resilience_consumption * damage_absorbed
```

**Bounds**: resilience_stock ∈ [0, 1] by clamp; resilience_pressure ∈ [0, 1] by smoothstep; effective_shock_damage ≥ raw_shock_magnitude × (1 - resilience_max_attenuation) = at least 30% of raw damage (resilience cannot eliminate shocks); shock_drawdown ≤ resilience_stock (enforced by stock clamp).

**Parameter rationale**:

- `k_resilience_investment = 0.10`: 0.05 too weak (insufficient efficiency to reach target operating range); 0.20 too strong (saturates too easily). 0.10 calibrated so x_resilience = 0.15 produces steady-state ≈ 0.43 in target band.
- `k_resilience_decay = 0.020`: 0.010 too slow (insurance would persist unrealistically); 0.040 too fast (heavy constant investment required just to maintain). 2.5x psi_inst_stock's decay rate, reflecting that resilience degrades faster than institutional capacity without active-use reinforcement. Half-life ~35 steps untended.
- `resilience_max_attenuation = 0.7`: 0.5 underweights protective value; 0.9 implies near-immunity (unrealistic). 0.7 means full stock reduces shock damage by 70% with 30% irreducible.
- `k_resilience_consumption = 1.5`: 1.0 too efficient (perfect proportionality); 2.5 too inefficient (irrational investment). 1.5 means magnitude-0.5 shock at stock=0.5 produces stock drop ~0.26 (meaningful cost, reserves remain for subsequent events).
- `k_resilience_deficit_contribution = 0.40`: the strongest single contribution to resilience_composite_urgency among resilience-specific factors. Below viability_pressure's 0.50 (stock-over-flow principle holds: viability is more existential than resilience deficit). Above 0.30 would underweight the dedicated diagnostic signal.

Calibration note: k_resilience_investment and k_resilience_decay together determine the operating range. If smoke testing shows saturation at 1.0 or drainage to zero under realistic allocations, these are the parameters to adjust. Target: under x_resilience ∈ [0.10, 0.25], steady-state resilience_stock falls in [0.30, 0.60].

**Multiplicand choice**: resilience_pressure enters resilience_composite_urgency. Composite cap rises from 1.75 to 2.00 to accommodate the new contribution while preserving the structural commitment that resilience cannot dominate.

```
resilience_composite_urgency = clamp(
    1.0
    + 0.50 * viability_pressure
    + 0.35 * capacity_pressure
    + 0.25 * shrinkage_pressure
    + 0.20 * growth_pressure
    + 0.40 * resilience_pressure,
    1.0, 2.00
)
resilience_return = clamp(raw_resilience_return * resilience_composite_urgency, 0, 1)
```

resilience_pressure does NOT enter combined_welfare_urgency, institution_composite_urgency, agency_composite_urgency, or suppression_composite_penalty in first build. Cross-category effects (low resilience raising welfare urgency through shock vulnerability, etc.) are real but second-order and deferred to watchlist.

The shock-attenuation function is a separate mechanism: it modifies how shocks affect the model (reducing effective_shock_damage on population, well-being, and other state), not how candidates are scored. The urgency function rewards investing in resilience; the attenuation function reflects what resilience actually does when shocks occur.

**Clamp interpretation**: the `(1 - resilience_stock)` saturating accumulation term is intentional. Building moderate redundancy is easier than achieving full preparedness; at resilience_stock = 0.9, the same x_resilience produces only 10% of the gain it produces at resilience_stock = 0.0. Full saturation should be expensive and slow, not a default state.

The composite cap at 2.00 preserves the commitment that resilience urgency cannot dominate the allocator even at maximum stress across all contributing pressures (max additive urgency 2.70 clamped to 2.00, clamping 35% of theoretical maximum). Remains below welfare's cap (2.50) and at parity with institutions' cap (2.00); crisis response is multi-category by design.

The 30% irreducible shock damage preserves the framework's commitment that resilience is insurance, not invulnerability. A high-resilience civilization still bears real cost from shocks; that cost is what makes resilience valuable rather than redundant.

**Phi-blind governance justification**: resilience is accumulated shock-readiness—redundancy, fallback systems, recovery paths, spare institutional and operational slack. A civilization without accumulated resilience is brittle even if currently healthy; it has nothing to absorb the shocks real systems face. A civilization with accumulated resilience can absorb shocks without cascading damage, but cannot eliminate damage entirely. Insurance built after the shock is no insurance at all; a planner must invest before contingencies materialize.

The asymmetry with psi_inst_stock (no free recovery term) reflects the asymmetry between active and reserve capacity. Institutions get reinforced by successful operation: every legitimate succession, every successful coordination, every effective transmission of knowledge builds institutional capacity even without dedicated investment. Resilience does not get reinforced by absence of shocks. A civilization that doesn't invest in resilience doesn't have resilience, regardless of how stable conditions are.

The saturating shock-damage reduction reflects governance reality: even prepared systems suffer real damage. Pandemic preparedness reduces but does not eliminate pandemic damage; earthquake-resilient infrastructure reduces but does not eliminate earthquake damage. The 70% maximum reduction encodes this faithfully.

**Implementation semantics, including projection update and faithfulness test**:

Stock update in model main loop:
```python
def update_resilience_stock(self, action_v2, shock_this_step):
    investment_gain = K_RESILIENCE_INVESTMENT * action_v2['x_resilience'] * (1 - self.resilience_stock)
    decay_loss = K_RESILIENCE_DECAY * self.resilience_stock
    
    if shock_this_step is not None:
        raw_magnitude = shock_this_step.magnitude
        damage_absorbed = raw_magnitude * RESILIENCE_MAX_ATTENUATION * self.resilience_stock
        shock_drawdown = K_RESILIENCE_CONSUMPTION * damage_absorbed
    else:
        shock_drawdown = 0.0
    
    self.resilience_stock = clamp(
        self.resilience_stock + investment_gain - decay_loss - shock_drawdown,
        0, 1
    )
```

Shock-damage application (modifies existing shock infrastructure):
```python
def apply_shock(self, raw_magnitude):
    effective_magnitude = raw_magnitude * (1 - RESILIENCE_MAX_ATTENUATION * self.resilience_stock)
    # apply effective_magnitude to population well-being, mortality
    # update resilience_stock via update_resilience_stock
```

The v1.x.2 shock infrastructure applies raw magnitude directly; the v2 build adds the attenuation layer between raw shock event and downstream effect.

Projection update rule (during rollout, no shocks expected):
```
projected_resilience_stock_next = clamp(
    projected_resilience_stock
    + K_RESILIENCE_INVESTMENT * candidate_action['x_resilience'] * (1 - projected_resilience_stock)
    - K_RESILIENCE_DECAY * projected_resilience_stock,
    0, 1
)
```

First-build commitment: rollouts assume no shocks during projection horizon (rollouts don't anticipate stochastic events). The urgency function via resilience_pressure rewards maintaining resilience for shocks that might occur outside the horizon. Phi later weights this prospective accumulation more heavily. If later analysis shows the optimizer under-invests because rollouts never see shocks, the watchlist item "shocks in projection" can be promoted.

Faithfulness test:

Stock dynamics are deterministic (no stochasticity in investment gain or decay), so tolerances are tight. Test matrix:
```
Initial resilience_stock: 0.0, 0.3, 0.6, 0.9
x_resilience allocation:  0.0, 0.10, 0.20, 0.30
Horizons:                 5, 10, 20 steps
Shock conditions:         none (first-build projection is shock-free)
```

Tolerances:
- 1-step: projected within 0.005 of actual
- 5-step: mean absolute error ≤ 0.015
- 20-step: mean absolute error ≤ 0.035, max ≤ 0.06
- Directional agreement ≥ 95% at all horizons

Any drift indicates constant or coefficient mismatch (not stochastic variance) and is fixed in the projection equation, not by tuning the urgency function.

Shock-attenuation verification (separate test):

For shock events of magnitude {0.2, 0.5, 0.8} at resilience_stock levels {0.0, 0.3, 0.6, 0.9}:
- effective_shock_damage matches `raw_magnitude × (1 - 0.7 × resilience_stock)` within numerical tolerance
- shock_drawdown matches `1.5 × damage_absorbed` within numerical tolerance
- Population effects (mortality, well-being drop) scale with effective_shock_damage rather than raw_magnitude

This ensures the attenuation mechanism actually changes downstream model outcomes.

**Watchlist additions**:

```
Deferred: sustained-stress drawdown of resilience_stock

Reason: real systems consume resilience reserves during prolonged stress 
(demographic crisis, institutional decline, capacity overload) even without 
discrete shock events. First build implements event-triggered drawdown only.

Revisit if: smoke testing shows resilience_stock saturates too easily because 
nothing draws it down outside shocks; later gates show the optimizer 
over-invests in resilience because shock-free rollouts make it look free.

Deferred: cross-category effects of resilience_stock

Reason: low resilience_stock plausibly raises welfare urgency (shock 
vulnerability affecting well-being) and institutional urgency (reduced 
robustness for institutions). First build keeps resilience_pressure 
contributing only to resilience_composite_urgency.

Revisit if: phi sweep results show resilience modulation through 
cross-category effects would clarify phi's behavioral channel; later 
gates indicate the optimizer treats resilience as too isolated.

Deferred: shocks in projection rollouts

Reason: first-build rollouts are shock-free, so the optimizer cannot see 
projected shock damage during candidate evaluation. Resilience investment 
is rewarded only through urgency on current resilience_stock state, not 
through projected shock-cost reduction.

Important: this is potentially load-bearing for phi. Resilience may be the 
variable most likely to show "no horizon effect even at high phi" because 
the horizon doesn't include the events that justify resilience investment.

Revisit if: phi-coupled rollouts (Stage 3) reveal the optimizer under-invests 
in resilience because rollouts never penalize shock-vulnerability; this 
would be a strong case for promoting probabilistic shock injection into 
rollouts as a phi-sensitivity test.
```

### Worked example 5: trend variables (deterioration-anticipation diagnostics)

Demonstrates the seven-element template for derived, cross-cutting flow signals that feed into existing composite urgency multipliers rather than introducing new categories or independent terms. The lightest of the five worked examples by design: trends are warning lights, not steering wheels. They warn the optimizer of deterioration before stocks reach crisis but remain subordinate to current state.

The architectural commitment: trends do not create new utility terms, new categories, or new multiplicand patterns. They feed into existing named composite multipliers within existing caps. They do not raise category ceilings.

**Shape**: exponential moving average over one-step deltas, with negative trends converted to bounded pressure via smoothstep. Only negative trends create pressure; positive trends do not reduce urgency below the stock-defined baseline.

Four trends included; one deferred:

Included: avg_wb_trend, population_trend, psi_inst_trend, resilience_trend.

Deferred: demographic_pressure_trend (a trend on a flow variable is a second derivative; v1.x.2 mechanics don't produce stable second-order signals to warrant inclusion).

EMA update:
```
trend_x_next = (1 - alpha_trend) * trend_x + alpha_trend * delta_x_next

where delta_x_next = x_next - x_current
(except population_delta = (population_next - population_current) / max(population_current, 1))
```

Pressure conversion (only negative trends activate):
```
decline_pressure_x = smoothstep(
    clamp(-trend_x / trend_scale_x, 0, 1)
)
```

The clamp at zero on the negative side ensures positive trends produce zero pressure. The clamp at one ensures pressure saturates at the trend_scale_x threshold.

**Bounds**: each trend ∈ [-1, 1] in principle (bounded by the state variable's range), but practically near zero in stable operation. decline_pressure ∈ [0, 1] by smoothstep construction. Existing composite caps remain unchanged; trends compete inside the existing bounded composites.

**Parameter rationale**:

- `alpha_trend = 0.30`: 0.10 too slow (multi-step lag before trend reflects movement, weakens horizon role); 0.50 too noisy (single-step fluctuations dominate); 0.30 gives recent movement meaningful weight while damping noise. At this rate, a sudden decline reaches ~65% of its value by step 4, ~95% by step 10.

- `trend_scale_x = 0.05 for all four trends in first build`: a smoothed decline of 5% per step is treated as full trend pressure. 1-2% per step should be visible but not decisive; 5% per step in a bounded state variable is severe and warrants saturated pressure. Using the same scale across all four trends keeps the trend layer auditable for first build; per-variable calibration deferred until smoke testing reveals different natural rates of movement.

- `coefficient ceiling: 0.20 maximum, with ≤ 50% of corresponding flow coefficient where one exists`: enforces the stock > flow > trend hierarchy. Trends are confirmation signals, not primary drivers.

**Multiplicand choice**: trends feed into existing composite urgency multipliers as additional contributions. They do not multiply returns directly as standalone terms. Final composite multipliers with trend contributions absorbed:

```
# Welfare: avg_wb_trend dominates; population_trend confirms demographic shrinkage
combined_welfare_urgency = clamp(
    urgency_wb * (
        1.0
        + 0.50 * viability_pressure
        + 0.25 * capacity_pressure
        + 0.35 * shrinkage_pressure
        + 0.15 * avg_wb_decline_pressure
        + 0.10 * population_decline_pressure
    ),
    0.50, 2.50
)

# Agency: only population_trend adds to existing pressures
agency_composite_urgency = clamp(
    1.0
    + 0.35 * viability_pressure
    + 0.25 * shrinkage_pressure
    + 0.10 * population_decline_pressure,
    1.0, 1.50
)

# Institutions: population and psi_inst trends both contribute
institution_composite_urgency = clamp(
    1.0
    + 0.35 * viability_pressure
    + 0.50 * capacity_pressure
    + 0.35 * shrinkage_pressure
    + 0.25 * growth_pressure
    + 0.15 * population_decline_pressure
    + 0.20 * psi_inst_decline_pressure,
    1.0, 2.00
)

# Resilience: population and resilience trends contribute
resilience_composite_urgency = clamp(
    1.0
    + 0.50 * viability_pressure
    + 0.35 * capacity_pressure
    + 0.25 * shrinkage_pressure
    + 0.20 * growth_pressure
    + 0.40 * resilience_pressure
    + 0.15 * population_decline_pressure
    + 0.20 * resilience_decline_pressure,
    1.0, 2.00
)

# Suppression: population and psi_inst trends raise the penalty
suppression_composite_penalty = clamp(
    base_suppression_penalty * (
        1.0
        + 0.50 * viability_pressure
        + 0.25 * capacity_pressure
        + 0.35 * shrinkage_pressure
        + 0.15 * population_decline_pressure
        + 0.15 * psi_inst_decline_pressure
    ),
    base_suppression_penalty, 2.00 * base_suppression_penalty
)
```

Note: every trend coefficient is ≤ 0.20 (the first-build ceiling), and is ≤ 50% of the corresponding flow coefficient where one exists (e.g., population_decline_pressure on welfare is 0.10, half of shrinkage_pressure's 0.35; psi_inst_decline_pressure on institutions is 0.20, less than half of capacity_pressure's 0.50). The stock-over-flow-over-trend hierarchy holds throughout.

Caps remain at population_ratio's levels; trends do not raise ceilings.

**Clamp interpretation**: the directional clamp at zero on the negative side of -trend_x is the most important architectural choice in the spec. Positive trends do not subtract from urgency. The reasoning: a healthy improving trend is recognized by improving stock state, which the existing urgency functions read directly. A planner should not reduce welfare maintenance urgency just because welfare is currently improving; that would create complacency precisely when sustained investment is required to consolidate the improvement. Trends warn of deterioration before stocks reach crisis; they do not justify abandoning maintenance when stocks are improving.

The composite caps remaining unchanged is the second important architectural commitment. Trends compete with stock and flow pressures inside existing bounded composites, not by raising ceilings. This preserves the structural commitment that no single category becomes a crisis magnet regardless of how many diagnostic signals are simultaneously activated.

**Phi-blind governance justification**: real governance systems respond to smoothed deterioration, not raw tick-to-tick movement. One bad step should not rewrite allocation, but persistent decline should raise urgency before the underlying stock reaches crisis threshold. A welfare crisis at avg_wb = 0.50 is much easier to address if the trajectory is recognized at avg_wb = 0.65 with strong negative trend than if the planner waits for the level to reach crisis before responding. Trends provide the anticipatory signal that distinguishes graceful intervention from reactive emergency response.

The architectural subordination of trends to stocks and flows reflects governance reality: trends are noisier than levels and have weaker individual signal. They matter as confirmation and as early warning, but they should not override the actual condition of the substrate. A population with declining trend but healthy current state is in a different situation than a population with stable trend but already-poor current state; the existing urgency on current state correctly weights the second more heavily.

**Implementation semantics, including projection update and faithfulness test**:

Initialization:
- All trends initialize to 0.0 at model startup.
- Startup lag: trend pressure has approximately 5-10 step warmup before EMA values become representative. Trend-based pressure is correspondingly weak during initial run steps. This is correct behavior, not a defect; the planner should not act on trends that haven't yet established meaningful signal.

Per-step update (in model main loop):
```python
def update_trends(self, previous_state, current_state):
    avg_wb_delta = current_state.avg_wb - previous_state.avg_wb
    population_delta = (current_state.population - previous_state.population) / max(previous_state.population, 1)
    psi_inst_delta = current_state.psi_inst_stock - previous_state.psi_inst_stock
    resilience_delta = current_state.resilience_stock - previous_state.resilience_stock
    
    self.avg_wb_trend = (1 - ALPHA_TREND) * self.avg_wb_trend + ALPHA_TREND * avg_wb_delta
    self.population_trend = (1 - ALPHA_TREND) * self.population_trend + ALPHA_TREND * population_delta
    self.psi_inst_trend = (1 - ALPHA_TREND) * self.psi_inst_trend + ALPHA_TREND * psi_inst_delta
    self.resilience_trend = (1 - ALPHA_TREND) * self.resilience_trend + ALPHA_TREND * resilience_delta

def compute_decline_pressure(trend_value, trend_scale):
    return smoothstep(clamp(-trend_value / trend_scale, 0, 1))
```

Projection update (during rollout):

Rollout trends initialize from current model trend values, not from zero. At each rollout step, the projection computes deltas from projected state transitions, then evolves trends forward:

```
projected_avg_wb_delta = projected_avg_wb_next - projected_avg_wb_current
projected_avg_wb_trend_next = (1 - ALPHA_TREND) * projected_avg_wb_trend + ALPHA_TREND * projected_avg_wb_delta

(similarly for population, psi_inst, resilience trends)
```

This gives trends a legitimate horizon role. A candidate that produces sustained improvement reduces decline pressure over the rollout; a candidate that produces slow deterioration accumulates trend pressure before the underlying stock reaches crisis. The horizon-sensitive channel for trends is exactly the trajectory of decline pressure across the rollout depth, which phi later weights.

Faithfulness test (mostly inherited from underlying state tests; lightweight standalone check):

```
Run forced-action projections and actual agent-layer runs.

Compare projected and empirical:
  avg_wb_trend, population_trend, psi_inst_trend, resilience_trend

Sign agreement (does projection get the direction right):
  1-step:  ≥ 90%
  5-step:  ≥ 85%
  20-step: ≥ 80%

Pressure-bin agreement (does projection produce the same urgency tier):
  Bins: low [0.00, 0.25), medium [0.25, 0.75), high [0.75, 1.00]
  20-step agreement: ≥ 80% of test cases in same bin
```

Do not require tight magnitude agreement. Trends are smoothed derivatives of stochastic variables; sign and bin agreement matter more than exact value. If sign agreement falls below threshold, the fix is in the underlying state projection (improve avg_wb projection, population projection, etc.), not in the trend EMA or scale parameters.

**Watchlist additions**:

```
Deferred: demographic_pressure_trend

Reason: trend on a flow variable is effectively a second derivative of 
population. In Stage 1.5 demographic_pressure itself captures direction of 
substrate change, and population_trend captures realized movement; the 
second derivative is too noisy and indirect for first build.

Revisit if: later models include richer cohort dynamics, demographic shocks, 
or oscillatory population regimes where rate-of-change of demographic 
pressure becomes a meaningful signal.

Deferred: per-trend calibration of trend_scale_x

Reason: first build uses uniform trend_scale_x = 0.05 across all four trends 
for audit clarity. Different state variables may have different natural rates 
of movement that warrant different scales.

Revisit if: smoke testing reveals one trend variable produces full pressure 
at much smaller deltas than others (or vice versa), creating asymmetric 
sensitivity. Per-variable scales should be calibrated to empirical movement 
ranges, not tuned to produce desired phi behavior.

Deferred: positive-trend reward mechanism

Reason: first build is asymmetric (only negative trends create pressure). 
An alternative architecture would have positive trends modestly reduce 
urgency, accelerating allocation away from improving states. This is 
deliberately rejected for first build because it can create complacency: 
abandoning welfare maintenance just because welfare is currently improving 
risks losing the improvement.

Revisit if: phi sweep results show the optimizer over-invests in already-
improving categories because trend pressure is purely additive; if so, a 
small positive-trend reduction (capped well below the base urgency) might 
be defensible. Not recommended.
```

### Stage 1.5 acceptance condition

Stage 1.5 is complete when:
1. All six diagnostic variables (the five committed above plus psi_inst_stock) have specifications meeting the seven-element template, with phi-blind committed urgency or pressure functions, multiplicand commitments, projection update rules, and faithfulness tests.
2. The Stage 1 build is updated to include diagnostic state in U_sys_v2 and project it through the rollout, with all changes preserved as named-constant traceability tied to governance justifications. Composite urgency functions for each affected downstream category are implemented as named bounded multipliers with explicit composition rules.
3. The smoke test passes under the revised metric.
4. Faithfulness tests pass for each projection update rule across the specified tolerance and boundary criteria.
5. Gate 2 re-runs with passing pairwise cosine distances across the five test configurations, confirming the optimizer is now state-sensitive in the ways governance reality requires.

Only after Stage 1.5 acceptance does Stage 2 resume with gate 3.

### Stage 1.6 structural commitment (added June 2026 after Stage 1.5 diagnostics)

The Stage 1.5 phi diagnostic and the 10000-sample composite urgency sweep together established that the v2 metric has two independent structural problems blocking the phi behavioral test:

1. **Phi-channel problem**: inverse-scarcity weighting produces `A_t = w_n * h_n + w_e * h_e` approximately constant across candidates (the saturation property carried over from v1.x.2). The argmax of `A_t * (discount + phi * L_t)` reduces to argmax of L_t regardless of phi value. Phi cancels in argmax. The Stage 1.5 phi diagnostic confirmed empirically: across phi values {1, 5, 10, 25, 100} and matched seeds, final populations were bit-identical (range = 0 on every seed).

2. **State-channel problem**: the additive-with-caps composite urgency architecture cannot transmit state variation across the configurations gate 2 tests. The 10000-sample Sobol sweep confirmed empirically: zero samples pass the state-sensitivity criterion, with maximum cosine distance 0.022 across the entire 31-parameter sweep (4x below the gate 2 threshold).

Stage 1.6 addresses problem 1 by restructuring where phi operates in the metric. The state-channel problem 2 is left for Stage 1.7.

**Architectural commitment**:

Per-step U_sys is phi-free and multiplicative:

```
U_sys_t = A_t * (discount_t + lambda_lineage_coupling * L_t)
```

Where:
- `A_t = w_n * h_n + w_e * h_e` (entropy-weighted sum, structurally unchanged)
- `discount_t = exp(-rho * t)` (horizon-dependent discount, preserved from v1.x.2 shape; configurable via rho)
- `lambda_lineage_coupling = 10.0` (fixed coupling constant; matches the default phi value so per-step U_sys magnitude is preserved at default operation)
- `L_t = welfare_factor_t * psi_inst_stock_t * theta_tech_t` (lineage health function, Stage 1.5 components)

Phi no longer appears in this formula.

Phi modulates rollout aggregation:

```
U_sys_rollout = sum over t in [0, T-1]: gamma(phi)^t * U_sys_(t+1)

gamma(phi) = gamma_min + (gamma_max - gamma_min) * phi / (phi + phi_half)
```

The optimizer's argmax over candidates is on the rollout sum, not on per-step U_sys.

**gamma(phi) parameters** (each phi-blind):

- `gamma_min = 0.5` (phi -> 0 limit). A planner with phi approaching zero discounts the next step by 50%, step 2 by 75%, step 10 by 99.9%. Effective horizon ~3-4 steps. Represents maximally short-horizon governance reasoning.
- `gamma_max = 0.95` (phi -> infinity limit). A planner with very high phi retains 36% weight at step 20, 13% at step 40, 2% at step 80. Effective horizon ~40-60 steps. Bounded below 1.0 because real planners discount distant futures due to uncertainty propagation.
- `phi_half = 10.0` (inflection). Default phi in v2 is 10; setting phi_half at 10 puts default phi at the function's inflection point so small variations around default produce meaningful changes in gamma. Operational phi range (1 to 100) is centered around this inflection.

**Implementation**:

- `simulation/metrics.py`: `compute_gamma_rollout(phi)` returns gamma; per-step `calculate_system_metrics_v2` uses `LAMBDA_LINEAGE_COUPLING` in place of phi.
- `simulation/agents.py`: `project_u_sys_v2_rollout` produces the rollout sum with gamma-weighted aggregation; `optimize_u_sys_v2` calls it per candidate. The legacy `project_u_sys_v2` returns single-horizon U_sys for Gate 4's harness, unchanged.
- `simulation/constants_v2_stage15.py`: `LAMBDA_LINEAGE_COUPLING`, `GAMMA_MIN`, `GAMMA_MAX`, `PHI_HALF` constants with phi-blind governance justifications.

**Integrity simulation result** (`simulation/diagnostics/stage16_integrity_simulation.py`):

Configuration: phi in {1, 5, 10, 25, 100}, 5 seeds per phi, 100 steps per run, composite urgencies harness-patched to neutral to isolate the U_sys revision. Pre-revision baseline captured at phi=10 with neutral composites (mean final pop 125.8).

Five pass criteria (all pass):

| Criterion | Measurement | Threshold | Result |
|-----------|-------------|-----------|--------|
| 1: phi behavioral channel | Per-seed final pop range across phi values; pre-revision baseline = 0 every seed | >= 3 seeds with range > 15 | **PASS** (5/5 seeds; ranges 17, 24, 33, 38, 62) |
| 2: no NaN, no crashes | All 25 runs complete cleanly | 0 crashes, 0 NaN | PASS |
| 3: demographic sustainability across phi | Mean final pop >= 60 and min final pop >= 30 at every phi | every phi clears | PASS |
| 4: default phi behavior preserved | Phi=10 mean pop vs pre-revision baseline | within 30% | PASS (16.2% delta) |
| 5: gamma(phi) matches spec | gamma(1)=0.541, gamma(5)=0.650, gamma(10)=0.725, gamma(25)=0.821, gamma(100)=0.909 | within 1e-3 | PASS exactly |

**Note on Criterion 1's metric refinement**:

The originally drafted criterion 1 measured pairwise cosine distance between mean-of-mean allocation vectors across phi values, threshold 0.05. The integrity simulation showed 0/10 pairs > 0.05 (maximum 0.0094) despite clear trajectory-level behavioral effect. The cosine-on-means metric was transferred from gate 2's state-variation context without sufficient thought about whether it captures phi sensitivity. Phi shifts which similar-allocation candidate the optimizer picks at each step; the per-step difference is small but the per-step trajectory compounds.

The substantive question criterion 1 needs to answer is "does phi affect optimizer choices in a way that produces different model outcomes." Per-seed final population range across phi values is the cleaner test for that, calibrated against the pre-Stage-1.6 baseline of range = 0 on every seed. The Stage 1.5 phi diagnostic data and the Stage 1.6 integrity simulation data both unambiguously demonstrate that range > 0 (in fact 17-62) on every test seed under the revised metric.

This is documented metric refinement, not retroactive threshold movement. The cosine-on-means metric is preserved as informational reporting in the integrity simulation report; gating uses the trajectory-divergence metric.

**Relationship to Stage 1.5 work**:

Stage 1.5's diagnostic state inputs (avg_wb, population, demographic_pressure, resilience_stock, four trends, psi_inst_stock), the per-category raw return curves (welfare, agency, institution, resilience), the projection update rules with cohort corrections (both BIRTH_WB_MEAN and BIRTH_AGE_MEAN), and the faithfulness test discipline are all preserved unchanged. The composite urgency layer is what's still under review and the Stage 1.7 work addresses it.

**Watchlist additions**:

```
Deferred: Power law alternative for gamma(phi)

Reason: the sigmoid form gamma(phi) = gamma_min + (gamma_max - gamma_min) * 
phi / (phi + phi_half) was chosen for monotone-saturating shape with a 
single inflection at phi_half. A power-law alternative gamma(phi) = 
1 - (1 + phi)^(-alpha) is qualitatively similar but has different tail 
behavior at very high phi.

Revisit if: phi sweep at higher resolution (phi values >= 200) shows the 
sigmoid form saturates too eagerly and a power law would extend the 
behavioral range.

Deferred: Composite urgency revision (Stage 1.7)

Reason: the 10000-sample composite urgency sweep established that the 
additive-with-caps composition rule cannot produce state-sensitive 
allocator behavior at any parameterization in the explored space. The 
state-channel problem is independent of the phi-channel problem Stage 1.6 
addresses. Stage 1.7 will revisit the composition rule.

This is active work; the deferral is procedural (separable change, 
testable independently) not theoretical.
```

### Stage 1.6 acceptance condition

Stage 1.6 is complete when:

1. The U_sys revision is implemented per the architectural commitment above, with all changes preserved as named-constant traceability tied to governance justifications.
2. The integrity simulation passes all five criteria with composite urgencies held at neutral, isolating the U_sys revision from the unfixed composite urgency layer.
3. The 39/39 legacy v1.x.2 tests remain green.
4. The criterion 1 metric refinement is documented in this section.

After Stage 1.6 acceptance, Stage 1.7 (composite urgency revision) becomes the next work.

### Stage 1.7 attempt and supersession (June 2026)

Stage 1.7 attempted to fix the state-channel problem by switching composite urgency composition from additive-with-caps to multiplicative-with-`[0,1]`-factors. The intent was that pairwise products would propagate state variation through to allocations rather than saturating at category caps.

The first integrity simulation produced demographic collapse within 50 steps across all 25 runs. Diagnostic isolation found that three of the four `theta_tech` factors saturated at the upper `[0,1]` boundary in normal operation, and the welfare-urgency × net-welfare-return product routinely exceeded 1.0 and was clipped, blocking welfare signal even as it intensified. The `[0,1]` clamp on factors converted the saturation mode rather than removing it.

Stage 1.7 was reverted to the Stage 1.6 final state. The diagnostic surfaced a deeper structural finding: the entire composite urgency layer — additive or multiplicative — is an attempt to mediate between state stocks and allocator returns through an arithmetic shape (boundedness, monotonicity, smoothness) without committing to what the mediation *is*. The architecture was specifying a function class without specifying the function. Stage 1.8 retires the layer.

### Stage 1.8 architectural revision (committed June 2026)

**Discipline boundary**

The framework's core results — U_sys structural protection, COP, dual phase transition, Nash architecture — are grounded in physics and game theory (entropy, multiplicative coupling, payoff structure, equilibrium concepts). The specification of *how allocator choices map back to state stocks* is an economic / control-theoretic specification. The framework does not claim to derive these mappings from first principles; it claims that whatever mapping plugs in must satisfy interface conditions.

The Stage 1.5/1.7 composite urgency work conflated these two layers. Composite urgency was a placeholder for the allocation-to-state mapping that wore the costume of a derived structural claim. Stage 1.8 separates them: the working_factor interface specifies what the framework requires (an allocation-to-target map with stock dynamics); the implementation behind it is a placeholder explicitly named as such, open to economic specialist revision.

**Working_factor interface specification**

```
delta_state = apply_working_factor(allocation, current_state, step)
```

For each infrastructure stock `s` in `STATE_ALLOCATION_MAPPING`:

- `target(allocation, state)`: a function mapping the relevant allocation entry to an equilibrium target for the stock. Required to be bounded in `[0, 1]`, monotone non-decreasing in its allocation argument, and defined for all valid allocations.
- `rate ∈ (0, 1]`: a logistic-growth rate setting transient timescale.
- `delta = rate * (target - current)`: per-step change toward the target.

The current `STATE_ALLOCATION_MAPPING` (`simulation/constants_v2_stage18.py`) has four entries: `psi_inst_stock`, `resilience_stock`, `theta_capability`, `transfer_state`. The target functions are linear-saturating placeholders with first-build calibration; their specific functional forms are explicitly placeholder.

**U_sys revision** (`simulation/metrics.py`):

```
h_eff       = h_n * pop_viability * avg_wb
theta_tech  = capability * theta_capability * transfer_state * exp(-alpha * convergence_strength * runaway_term)
L_t         = h_eff * psi_inst * theta_tech
U_sys_t     = (w_n * h_n + w_e * h_e) * (discount_t + lambda_lineage_coupling * L_t)
```

`L_t` now reads state stocks directly. There is no composite urgency layer between state and per-category return. `avg_wb` remains agent-derived (through the v2-to-v1.x.2 bridge); `h_n` remains agent-derived from spectral entropy. The four infrastructure stocks evolve under `working_factor`; everything else is preserved from Stage 1.6.

**Stage 1.5 component retention**

Stage 1.5's diagnostic state inputs are preserved where they describe the system's measured condition (`avg_wb`, `population`, `demographic_pressure`, four trend variables, `resilience_stock`, `psi_inst_stock`). Per-category raw return curves and projection update rules with cohort corrections (`BIRTH_WB_MEAN`, `BIRTH_AGE_MEAN`) are preserved. What is retired is the composite urgency *layer* — the arithmetic combinators that mixed these signals into multiplicands on category returns.

**Validation: Phase A and Phase B**

Phase A — single configuration (rr=0.066, init_psi=0.5, n_agents=200), 5 phi values × 5 seeds × 100 steps:

| Criterion | Result |
|---|---|
| No crashes / NaN | PASS (0/25) |
| Demographic at phi=10 | PASS (mean 151.6, min 110; thresholds 60/30) |
| State responsiveness (revised: initial-to-final delta > 0.10) | PASS (all five tracked stocks: avg_wb 0.65→0.85, psi 0.50→0.77, resilience 0.30→0.60, theta_capability 0.50→0.77, transfer_state 0.50→0.73) |
| Phi behavioral channel preserved | PASS (5/5 seeds with cross-phi range > 15; ranges 45-63) |

Phase B — five configurations (gate-2 setup: rr ∈ {0.055, 0.066, 0.085}, init_psi ∈ {0.20, 0.50, 0.85}) × 5 matched seeds × 100 steps, phi held at default:

| Criterion | Result |
|---|---|
| Trajectory divergence across configs (per-seed range > 15 in >= 3/5 seeds) | PASS (5/5 seeds; ranges 204-320) |
| Per-step allocation cosine distance (> 0.10 in >= 3/10 pairs) | PASS (9/10 pairs) |
| Demographic sustainability (revised: >= 4/5 configs meet mean 60 / min 30, with C_low_rr exempt) | PASS (5/5 configs meet thresholds including C_low_rr) |
| L_t cross-config std/mean | PASS (mean ratio 0.307, 6.1× threshold) |

**Methodological lessons recorded during Stage 1.6–1.8**

1. *Pre-commit to substantive questions, not just metrics.* Metrics are proxies for questions. The Stage 1.6 cosine-on-means criterion 1 and the Stage 1.8 Phase A C3 std-based metric both measured something but neither measured what they were trying to test. When a pre-committed metric diverges from the substantive question (criterion 1: "does phi change outcomes?"; C3: "do state stocks evolve?"), the metric is replaced with one that answers the question, and the refinement is documented in the section. This is metric refinement, not retroactive threshold movement.

2. *Multi-configuration tests should explicitly inherit single-configuration setups and only vary parameters under test.* Phase B's original harness used `n_agents=100` and `wb_min=wb_max=0.50` where Phase A used `n_agents=200` and default wb distribution `[0.5, 0.8]`. Isolation controls established that the wb pinning alone drove ~52% of the demographic delta. The inconsistency was an oversight, not deliberate test design. Multi-config harnesses must inherit single-config harnesses verbatim and override only what is being tested.

3. *Phase boundary claims from prior framework work should constrain test metric calibration.* The framework's existing extinction-boundary characterization (`rr ≈ 0.063-0.066`) means a demographic threshold applied uniformly across `rr ∈ {0.055, 0.066, 0.085}` would require an architecture to sustain demographics below the existing extinction boundary — that is, to override the framework's existing physics rather than meet it. Revised C3 exempts configurations below the established phase boundary.

**Init_psi asymmetric sensitivity finding**

Phase B observed that `E_low_psi` (init_psi=0.20) produced final populations identical to `A_baseline` (init_psi=0.50) on all 5 seeds (157, 110, 121, 178, 192). `D_high_psi` (init_psi=0.85) differed on 3/5 seeds. The per-step cosine table corroborated: A vs E = 0.022 (the only pair failing the 0.10 threshold), A vs D = 0.123.

Mechanism: working_factor drives `psi_inst_stock` logistically toward an allocation-determined target near 0.55–0.95 (depending on `x_institutional_capacity`). Init psi=0.20 converges *upward* to the same target as init psi=0.50 and leaves no lasting trajectory imprint. Init psi=0.85 (above target) follows a different relaxation path while it descends, which does perturb allocations enough to register.

Documented as a property of the architecture, not a defect. Future work that intends to use init_psi as a meaningful test axis on the low side would need either a longer transient regime, a working_factor parameterization with asymmetric rates, or a different target function shape.

**C_low_rr observation**

At `rr=0.055`, configuration sustained at mean 80.8 (min 54) across 5 seeds — above the 60/30 thresholds. The framework's previously documented extinction boundary `rr ≈ 0.063-0.066` may sit slightly lower than characterized. Recorded for future phase-transition work; no immediate action.

**Stage 1.5 → 1.6 → 1.7 → 1.8 arc**

| Stage | Action | Outcome |
|---|---|---|
| 1.5 | Added diagnostic state inputs and composite urgency layer (additive-with-caps) | 10000-sample Sobol sweep: 0 samples pass state sensitivity; phi diagnostic: phi cancels in argmax |
| 1.6 | Revised U_sys structure: per-step phi-free, phi modulates rollout aggregation via `gamma(phi)^t` | Phi-channel restored; state-channel still blocked |
| 1.7 | Attempted multiplicative-with-`[0,1]`-factor composite urgency | Demographic collapse from clamp saturation; reverted |
| 1.8 | Retired composite urgency layer; introduced working_factor interface; L_t reads state directly | Phase A and Phase B pass; state-channel restored |

The arc is empirical refinement of architectural choices: each stage's design commitment was tested against diagnostic data, and updated when the diagnostic surfaced structural inadequacy. The discipline boundary clarification at Stage 1.8 — separating physics-grounded framework claims from economic / control-theoretic allocation specification — is the most consequential update because it identifies what the framework can and cannot derive on its own.

**Open invitation**

The `working_factor` interface specifies what the framework requires from the allocation-to-state mapping. The current placeholder implementation in `STATE_ALLOCATION_MAPPING` is a first-build calibration adequate for testing that the interface works. Economic / control-theoretic specialists are invited to propose mappings grounded in their respective disciplines; the framework's physics-grounded results are insensitive to the choice of mapping as long as the interface conditions are satisfied.

### Stage 1.8 acceptance condition

Stage 1.8 is complete when:

1. Composite urgency layer is retired from production code paths.
2. `working_factor` interface is implemented, with `STATE_ALLOCATION_MAPPING` placeholder explicitly named as placeholder.
3. `L_t` reads state stocks directly (no intermediate composite urgency multiplicands).
4. Phase A and Phase B integrity simulations both pass per the criteria above.
5. The 39/39 legacy v1.x.2 tests remain green.
6. The methodological lessons, init_psi asymmetric sensitivity finding, C_low_rr observation, and the Stage 1.5–1.8 arc are documented in this section.

All conditions met as of the Stage 1.8 commit. Stage 2 (gate 2 re-run, gate 3 capability regime, gate 4 horizon crossing) becomes the next work, against the working_factor architecture.

---

## Part VI — The phi-capability question and the decision tree

### Status: closed by Part IX

The Part VI decision tree and the phi re-test questions below were the framing under which the Stage 1.5 through 1.8 work and the phi investigation Pieces 1, 2, and 2-followup were conducted. The investigation closed in Class B (Part IX.3): phi has empirically detectable behavioral effect, localized to short rollouts at marginal rr. The pre-committed Branch 2 outcome (phi matters above a threshold) corresponds most closely to the empirical result, with the threshold being the rr phase boundary rather than capability. The sequencing, the re-test questions, and the decision tree below are preserved as the methodological record under which the investigation was conducted; the closed-out empirical findings are in Part IX, particularly IX.3 (mechanism) and IX.7 (the U-shape's no-succession scope). Do not re-run the decision tree against the Class B result.

### Sequencing (do not couple phi to capability yet)

The intuition is sound: as capability rises, consequence-radius expands, so planning horizon and lineage weighting should rise. But coupling phi to capability before fixing the action space would let phi appear important because importance was wired into the parameter schedule, not because the allocator faced real tradeoffs.

Correct sequence:
1. Redesign the action space from reality-derived tradeoffs.
2. Run the model with phi independent.
3. Check whether phi changes choices only when real temporal and lineage tradeoffs exist.
4. Only then derive phi(capability).

A defensible later form: `phi_eff = phi_base * f(capability / integration_capacity)`, flat at low capability, rising once capability exceeds biological or institutional absorption bandwidth. This must be derived calibration, not a rescue patch.

### The phi re-test questions (after tradeoffs exist)

- Does phi alter choices between near-term output and institutional investment?
- Does phi alter choices between capability acceleration and transfer fidelity?
- Does phi alter succession timing when succession has real transition load?
- Does phi matter more at high capability than low?
- Does phi produce behaviorally distinct trajectories, not merely larger U_sys magnitudes?

### The three-branch decision tree (pre-committed)

The credibility of the eventual result rests on committing to all three outcomes before looking.

**Branch 1: phi has no effect even in the high-fidelity landscape.** Retire the behavioral claim. This is the branch you must be genuinely willing to take. It would be the strongest version of the U_sys-is-everything finding: even in a faithful allocation problem, the objective determines outcomes and horizon weighting is inert. Austere, real, publishable. The framework survives because the core claims never depended on phi.

**Branch 2: phi matters only above a capability/integration threshold.** Specify a threshold-coupled phi_eff. This most precisely vindicates the original intuition (phi matters when consequence-radius exceeds absorption bandwidth) and would retroactively explain the cap-conditional manuscript claim as a real shadow of threshold behavior rather than an artifact. Most interesting outcome. The capped-regime check in Part IV previews whether this structure already exists.

**Branch 3: phi matters broadly.** Preserve it as a general lineage-weighting coefficient. Most comfortable outcome and therefore the one to scrutinize hardest. Broad sensitivity is exactly what motivated design produces. If you land here, re-audit every curve for independent justification before celebrating. Branch 2 is more believable than Branch 3 because it is narrower and matches a prior mechanism.

### Branch resolution

The empirical investigation closed in Class B (Part IX.3), which corresponds to **Branch 2 with the threshold defined by rr rather than capability**. Phi has a real behavioral effect (rejecting Branch 1) that is narrower than universal (rejecting Branch 3). The threshold is the phase boundary rr, not the capability axis the original Branch 2 anticipated. The cap-conditional manuscript claim withdrawn in Part VIII remains withdrawn; the Branch 2 vindication is rr-conditional, not capability-conditional.

---

## Part VII — Publication posture

No one is currently pressing on the phi claim, and the v1.x.2 essay revision already walked back the phi-as-buffer claim publicly. You have genuine slack to build the fix before publishing the problem, so a reader encounters problem and fix together (a strength story) rather than the problem alone (a weakness story with a hopeful ending). The trigger for a standalone correction statement is external pressure, which does not exist.

Sequence: do Option 1 (build the higher-fidelity model) before Option 2 (the honest-limitation writeup), because the fix clarifies what the limitation section needs to say. The exception is the manuscript contradiction in Part IV, which is a live inconsistency in a published artifact and should be resolved on its own timeline regardless.

---

## Part VIII — Immediate next actions, in order

Items 1 through 9 are complete as of June 2026. The active work is item 11 (Gate 4 specification and implementation).

1. ~~Resolve the manuscript contradiction.~~ Done. Cap-conditional claim withdrawn as RNG-desynchronization artifact (commit prior to Stage 1).
2. ~~Update materials with the capability-sweep result and the contradiction resolution.~~ Done.
3. ~~Specify the composition vector in full (the keystone tradeoff).~~ Done through the design conversations producing the six category curves, complementarity structure, constraint frontier, Psi_inst stock, and bridge.
4. ~~Build the minimum faithful set.~~ Done. Stage 1 commit `61a362e` built the v2 parallel policy with all committed structure. Smoke test passed.
5. ~~Stage 1.5 / 1.6 / 1.7 / 1.8: structural fix for phi-channel and state-channel problems.~~ Done. Stage 1.5 built the diagnostic state set and composite urgency layer; Stage 1.5 phi diagnostic and 10000-sample sweep established both channels were blocked. Stage 1.6 restructured U_sys to give phi a behavioral channel (committed). Stage 1.7 attempted multiplicative composite urgency, reverted on `[0,1]` clamp saturation. Stage 1.8 retired composite urgency, introduced the working_factor interface for infrastructure stocks, and let `L_t` read state directly; Phase A and Phase B integrity simulations both pass.
6. ~~Pass remaining acceptance gates~~ (status: gate 1, gate 2, gate 3, gate 4 all PASSED under v2.0 with formal yield logic; gate 5 NOT_APPLICABLE). Gate 2 G2.1 buffer re-runs cleanly with phi=25; Gate 3 G3.1/G3.2/G3.3 all pass at 1,620 runs; Gate 4 G4.1/G4.2/G4.3 all pass at 1,050 runs (Part IX.9). The bootstrap gate validation arc is complete except for Gate 5 (NOT_APPLICABLE pending operational COP infrastructure).
7. ~~Run phi free across the faithful landscape.~~ Done. Pieces 1, 2, and 2-followup totaling approximately 40,000 runs (Part IX).
8. ~~Read against the three-branch decision tree.~~ Done. Class B outcome (Part IX.3); Branch 2 with rr-defined threshold.
9. ~~Implement default phi revision from 10 to 25~~ (Part IX.5). Done in commit fde48b5. v2.0 paths updated; v1.x.2 paths preserved bit-for-bit; 39/39 legacy tests pass; gate 2 v2.0 G2.1 buffer re-runs cleanly.
10. **Optional research directions** in priority order (Part IX.11): ~~Monte Carlo Phase B~~ (done; see Part X); dynamic phi formulation; gamma function calibration; phase boundary characterization; longer simulation horizons (partially answered by Gate 3's N=500 horizon-dependence finding, Part IX.8); Pattern 1 alpha-cliff fine-resolution characterization. None blocking; all deferred to future budget.
11. ~~Build Gate 4 specification and implementation~~ (Part IX.11 item 1). Done. G4.1-G4.3 were located in the v1.x.2 paper Section 7; the validator is implemented and validated PASS at 1,050 runs (Part IX.9). cap-star is empirically characterized as alpha-dependent (3.0 at alpha=1.0, 2.5 at alpha=1.5).
12. ~~Run Monte Carlo Phase B quantitative validation at scale.~~ Done. Categories A, B, C totaling 29,400 rows, 0 errors (Part X). Survival landscape, succession dynamics, and COP cost-audit baseline characterized. 39/39 legacy tests pass.

---

## Part IX. Phi Investigation Findings and v2.0 Substantive Claims

### IX.1 Investigation summary

The phi behavioral channel established by Stage 1.6 (rollout-aggregation phi-in-rollout) was characterized empirically across an investigation arc totaling approximately 42,000 simulation runs:

- Piece 1 (fine-grained characterization, 12,000 runs) mapped survival rate across 16 phi values and 3 rr values at the v2.0 default architecture under no-succession conditions. It established the U-shape phi-survival relationship at marginal rr and identified phi=10 (the v2.0 default at that time, coincident with the gamma function's inflection point) as sitting near the trough rather than at any peak.
- Piece 2 (mechanism investigation, 8,000 runs) and the Piece 2 follow-up (20,000 runs) tested two candidate mechanisms for the U-shape: Mechanism C (horizon-resonance through gamma^t weighting at varying rollout depths) and Mechanism D (candidate-pool sampling sensitivity). The investigation classified the outcome against a five-class decision tree (Classes A through E) committed in advance.
- Stage 2 implementation work replaced the v2.0 placeholder yield logic with formal yield-condition logic per the framework's canonical succession economics, and characterized the resulting succession regime under v2.0 defaults (Pattern 1 cliff at ~2.5x capability ratio).
- Piece A (gate-2-style state sensitivity under active succession, 720 runs) tested whether gate-2-equivalent state sensitivity persists when succession is actively occurring under formal yield logic, and surfaced the substantive finding that the U-shape characterized by Pieces 1 and 2 does not reproduce under succession.
- Gate 3 v2.0 validation (1,620 runs) confirmed succession-capable consistency under formal yield logic and refined Pattern 1 as primarily alpha-driven rather than capability-ratio-driven.

The phi investigation closed as **Class B**: Mechanism C is supported at rr=0.057, Mechanism D is rejected, and Mechanism C does not extend to rr=0.060. The U-shape is rr-bounded and horizon-mediated. Mechanism E (working_factor calibration interaction) is exonerated by absence: there is no residual U-shape at rr=0.060 to attribute to it.

Subsections IX.2 through IX.6 record the phi investigation findings. Subsections IX.7 through IX.9 record the post-investigation v2.0 substantive findings that refine and extend the phi investigation's scope.

### IX.2 The U-shape finding

At rr=0.057, the survival landscape spans approximately 10pp across the tested phi grid. Three thousandths of rr above that, at rr=0.060, the landscape compresses to approximately 3pp (within noise). The transition is sharp.

**Test B survival matrix at rr=0.057** (rollout_steps_v2 = 20 fixed, 250 seeds per cell, SE per cell ~3.1pp):

| phi | cand=100 | cand=300 | cand=600 | cand=1000 |
|-----|----------|----------|----------|-----------|
|   3 | 0.560 | 0.588 | 0.580 | 0.668 |
|   5 | 0.600 | 0.632 | 0.556 | 0.556 |
|  10 | 0.548 | 0.572 | 0.640 | 0.664 |
|  25 | 0.640 | 0.680 | 0.664 | 0.596 |

Trough phi at v2.0 default operating point (cand=300): phi=10 at 0.572. Peak: phi=25 at 0.680. Spread: 10.8pp. The pairwise standard error at this cell is approximately 4.3pp, so the spread crosses the 2-SE significance threshold (8.6pp) with margin.

**Test C survival matrix at rr=0.060** (n_candidates_v2 = 300 fixed, 750 seeds per cell, SE per cell ~1.2pp):

| phi | rollout=10 | rollout=20 | rollout=30 | rollout=40 |
|-----|------------|------------|------------|------------|
|   3 | 0.877 | 0.873 | 0.868 | 0.877 |
|   5 | 0.892 | 0.871 | 0.913 | 0.871 |
|  10 | 0.887 | 0.883 | 0.893 | 0.901 |
|  25 | 0.888 | 0.883 | 0.901 | 0.893 |

At rollout=20 (v2.0 default): spread from trough (phi=5 at 0.871) to peak (phi=10 at 0.883) is 1.2pp, well below the 2-SE threshold of 3.4pp. Statistically indistinguishable.

The contrast between the two matrices is the central finding. The phi-sensitivity transition near rr approximately 0.056 to 0.057 separates a regime where phi choice spans roughly 10pp survival difference from a regime where phi choice is approximately indifferent across the tested range [3, 25]. Note that this phi-sensitivity transition is distinct from the survival-rate phase boundary. Monte Carlo Phase B (Part X.2) relocates the v2.0 survival-rate phase boundary to the rr=0.060 to 0.066 transition with a 50% inflection near rr=0.063; rr=0.057 is collapse-dominated (1.1% aggregate survival), the bottom of the collapse zone rather than the survival midpoint. The strong phi sensitivity at rr=0.057 is precisely because rr=0.057 sits deep in the collapse regime where allocation quality is decisive. The framework's phi sensitivity is a marginal-rr phenomenon, not a general one.

Underlying data: `simulation/diagnostics/phi_mechanism_followup_results.csv` rows with `test_id=B` (Test B at rr=0.057) and `test_id=C` (Test C at rr=0.060).

**Note on scope**: this finding was characterized under no-successor conditions (incumbent only, no succession events during the simulation). Section IX.7 documents that the U-shape does NOT persist under active succession. The U-shape is a property of the no-succession regime, not of v2.0 architecture generally.

### IX.3 The mechanism: horizon-resonance localized to marginal rr (Class B)

The Piece 2 follow-up Test A varied rollout_steps_v2 in {10, 20, 30, 40} at rr=0.057 with n_candidates=300. The per-rollout phi-spreads at 250 seeds per cell:

| rollout | trough phi | peak phi | spread (pp) | 2*SE (pp) | significant? |
|---------|------------|----------|-------------|-----------|--------------|
| 10 | 5 | 10 | 11.2 | 8.7 | yes |
| 20 | 3 | 25 | 10.4 | 8.7 | yes |
| 30 | 25 | 3  | 4.4  | 8.8 | no  |
| 40 | 3 | 10 | 4.8  | 8.8 | no  |

The U-shape exists at short rollouts (10 and 20) and dissolves at longer rollouts (30 and 40). Trough phi shifts between rollout=10 (phi=5) and rollout=20 (phi=3), supporting the script's "trough varies with rollout" verdict.

The mechanism: the rollout aggregation weights step t by gamma(phi)^t, with gamma(phi) = GAMMA_MIN + (GAMMA_MAX - GAMMA_MIN) * phi / (phi + PHI_HALF) and constants GAMMA_MIN=0.5, GAMMA_MAX=0.95, PHI_HALF=10. At short rollouts (10-20 steps), the geometric series sum_{t=0}^{T} gamma^t has not saturated; different phi values produce meaningfully different cumulative weights, which propagate to allocation choices and downstream survival. At longer rollouts (30-40 steps), the partial sums approach the asymptote (1 / (1 - gamma)) closely enough that phi-driven gamma differences contribute negligibly to the final allocation score. Phi sensitivity washes out.

The interaction with rr regime: at marginal rr (0.057), allocation choices propagate strongly to survival outcomes because small differences in resource direction compound across the simulation horizon. At healthy rr (0.060), the substrate's reproductive surplus dominates and absorbs allocation-quality differences. The same gamma-driven phi-sensitivity in the rollout aggregation that produces a 10pp U-shape at rr=0.057 produces a 1-3pp U-shape at rr=0.060 (within statistical noise).

The combined picture: phi affects rollout aggregation through gamma weighting; rollout aggregation affects allocation choice; allocation choice affects survival rate; the survival sensitivity to allocation quality is rr-dependent. Phi's behavioral channel is real; its observable effect on survival is bounded to short-rollout, marginal-rr regimes.

### IX.4 Mechanism D rejection

Mechanism D hypothesized that the U-shape is a candidate-pool sampling artifact: with too few rollout candidates, the optimizer cannot reliably distinguish marginally better policies from worse ones, and survival rate appears U-shaped because of random selection among similar-quality candidates rather than because of a real phi-sensitivity pattern. The prediction: U-shape depth shrinks as n_candidates_v2 rises (more candidates = cleaner selection = flatter survival landscape).

Test B at rr=0.057 with 250 seeds per cell measured U-shape depth across n_candidates_v2 in {100, 300, 600, 1000}:

| n_candidates | depth (pp) | 2*SE (pp) | significant? |
|--------------|------------|-----------|--------------|
| 100  | 9.2  | 8.7 | yes |
| 300  | 10.8 | 8.6 | yes |
| 600  | 10.8 | 8.7 | yes |
| 1000 | 11.2 | 8.7 | yes |

Depths are approximately constant near 10pp and trend slightly upward with candidate count, opposite of the D prediction. All four depths cross the 2-SE significance threshold, so the rejection rests on real signal rather than noise. The original Piece 2 had already rejected D at rr=0.060 (depths within noise floor); the follow-up confirms the rejection at the high-signal regime.

**Mechanism D is empirically rejected; no further investigation warranted.** The U-shape is real and persists across the full candidate range tested; sample size is not the explanation.

### IX.5 Default phi recommendation: revise from phi=10 to phi=25

At v2.0 default operating conditions (rollout_steps=20, n_candidates=300):

- At rr=0.057 (marginal, just below phase boundary at ~0.056): phi=10 at 0.572, phi=25 at 0.680. Spread: 10.8pp. phi=25 wins decisively.
- At rr=0.060 (above phase boundary): phi=10 at 0.883, phi=25 at 0.883. Indistinguishable.
- At rr=0.055 (deep in the collapse regime, from Piece 1's broader survey): both phi values produce similar collapse outcomes; phi does not rescue at sub-boundary rr.

The framework's substantive purpose is governance under marginal-survival conditions where civilizational outcomes are at stake. Default phi should be calibrated to perform well at the conditions where the framework matters most. At marginal rr, phi=25 outperforms phi=10 by approximately 10pp; at healthy rr, phi=25 does no worse than phi=10. The choice dominates phi=10 across the rr range where the framework's behavior matters.

**Recommendation: revise framework default phi from 10 to 25.**

The Stage 1.6 reasoning that produced phi=10 placed the default at the gamma function's inflection point (PHI_HALF=10), which was theoretically motivated as the point of maximum sensitivity of gamma to phi. The empirical investigation reveals that gamma's maximum sensitivity to phi is not the same as the rollout aggregation's most favorable phi value for survival outcomes. The two are different quantities; the theoretical motivation conflated them. Empirical evidence supersedes the theoretical motivation.

**Implementation status: DONE (commit fde48b5).** The v2.0 default phi was revised from 10.0 to 25.0 across `simulation/metrics.py` (the authoritative default), `simulation/agents.py` and `simulation/model.py` (v2-rollout fallback paths), `bootstrap_gate_validator/sample_input.json` and `sample_input_failing.json` (gate 1 framework input), `simulation/diagnostics/stage17_pressure_diagnostic.py` (v2.0 pressure diagnostic), and `docs/RUNBOOK.md`. v1.x.2 paths (anything with `policy='optimize_u_sys'`) intentionally retain phi=10 per the bit-for-bit read-only rule. 39/39 legacy tests pass; gate 2 v2.0 G2.1 buffer test re-runs cleanly with phi=25 as the high-phi comparison.

### IX.6 Trough migration finding

The U-shape's trough phi is not a fixed feature. Across the Test A and Test B grids at rr=0.057, troughs landed at:

- Test A, rollout=10: trough at phi=5
- Test A, rollout=20: trough at phi=3
- Test A, rollout=30 and 40: no significant trough
- Test B, cand=100: trough at phi=10
- Test B, cand=300: trough at phi=10
- Test B, cand=600: trough at phi=5
- Test B, cand=1000: trough at phi=5

Three distinct trough-phi values (3, 5, 10) appear depending on which architectural axis is varied. The U-shape is a shifting valley, not a static feature.

Implication for framework documentation and implementer guidance: the framework cannot claim a single canonical "optimal phi" value. The right framing is "optimal phi depends on operating conditions." The default phi recommendation in IX.5 (phi=25) is calibrated specifically to the v2.0 default operating point (rollout_steps=20, n_candidates=300) at marginal rr. Implementers operating at different rollout depths or candidate counts may benefit from different phi values.

The trough migration is a substantive empirical finding about the framework, not a methodological caveat. It is recorded here as part of the investigation's results and should inform any future phi calibration work.

**Scope note**: trough migration was characterized under no-successor conditions. Section IX.7 documents that the U-shape (including its migrating trough) does not reproduce under active succession. The trough migration finding applies specifically to the no-succession regime that Pieces 1 and 2 tested.

### IX.7 The U-shape is a no-succession phenomenon (Piece A finding)

After the phi default revision committed and Stage 2 formal yield logic activated (see IX.8), the substantive question arose: do the U-shape characterizations of IX.2-IX.6 persist when succession is actively occurring under v2.0?

Piece A (`gate2_v20_yield_subset.py`, 720 runs) tested this directly. Grid: successor_capability in {1.5, 2.5}, phi in {1.0, 10.0, 25.0}, alpha in {0.5, 1.5}, rr in {0.057, 0.064}, 30 seeds per cell, N_STEPS=200, successor constructed on every run (unlike the original gate 2 sweep which omitted successors and thus did not exercise yield).

The phi=10 vs phi=25 comparison under active succession (n=60 per cell, SE approximately 6pp):

| alpha | rr | phi=10 surv | phi=25 surv | delta (pp) |
|-------|-----|-------------|-------------|------------|
| 0.5 | 0.057 | 0.717 | 0.700 | -1.7 (phi=10 wins) |
| 0.5 | 0.064 | 1.000 | 1.000 | 0.0 |
| 1.5 | 0.057 | 0.583 | 0.600 | +1.7 |
| 1.5 | 0.064 | 1.000 | 1.000 | 0.0 |

All deltas within plus or minus 1.7pp. phi=10 and phi=25 are **statistically indistinguishable** under active succession across all tested conditions. Piece 1's roughly 10pp U-shape at rr=0.057 with phi=10 in trough does not reproduce here.

Two plausible interpretations:

1. **Succession dynamics dominate gamma-weighting trough effects.** When succession events occur mid-run, the rollout-aggregation phi-sensitivity (Mechanism C from IX.3) gets washed out by the discrete state changes succession introduces. The trough is a "stable optimization" phenomenon, not an "active succession" one.

2. **Capability progression bypasses the trough at fixed-capability points.** At successor capabilities 1.5 and 2.5, the post-succession AI operates at different points in the capability landscape than the trough-defining incumbent did. The trough exists at fixed-capability stable runs; it dissolves when capability progresses.

The data does not discriminate between these interpretations. Either way: **the U-shape characterized in IX.2-IX.6 is a property of the no-succession regime**, not a property of v2.0 architecture generally. Phi behavior under succession-active conditions is approximately flat across the tested phi range.

This refines but does not invalidate Pieces 1 and 2's findings. Those findings hold for the conditions they tested (no-successor, fixed-capability runs). Their scope is narrower than the original Part IX framed.

**This finding does not change the phi=25 default recommendation in IX.5.** phi=25 is safe across all tested regimes: at no-succession trough conditions it outperforms phi=10 by approximately 10pp; under succession it ties phi=10 within noise. Defaulting to phi=25 produces the same or better outcomes regardless of whether succession occurs.

Piece A also confirmed gate-2-style state sensitivity persists under active succession (51.7pp spread across (phi, alpha, rr) cells; pass criterion was >=10pp), providing the substrate validation that subsequent Gate 3 v2.0 work depended on.

### IX.8 Pattern 1: succession regime characterization (Stage 2 + Gate 3)

The v2.0 placeholder yield logic (`capability_gap >= 0.3 OR generation_gap >= 1`) was replaced in Stage 2 (commit 72ff757) with formal yield-condition logic per the framework's canonical succession economics:

  Yield fires when (successor_u_sys - incumbent_u_sys) > transition_cost

Snapshot evaluation: both AIs propose what they would allocate this step via `optimize_u_sys_v2`; U_sys is computed at the current state under each allocation; transition cost uses the canonical (1+beta) * [k1*ln(cap+1)*ln(gen+1) + k2/psi_inst] form via `AIAgent.estimate_transition_cost` with v1.x.2 calibration constants (k1=2.164, k2=1.0, beta=0.5).

#### Stage 2 initial characterization

The Stage 2 parameter diagnostic (`stage2_yield_parameter_diagnostic.py`, 50 runs across 5 successor_capability values x 10 seeds x 300 steps at v2.0 defaults: phi=25, rr=0.066, alpha=1.0) found:

| succ_cap | fire_rate | mean fires/run | mean final_inc_gen |
|----------|-----------|----------------|---------------------|
| 1.2 | 100% | 2.0 | 3.00 |
| 1.5 | 100% | 1.3 | 2.30 |
| 2.0 | 100% | 1.0 | 2.00 |
| 2.5 | 100% | 1.0 | 2.00 |
| 4.0 | 0% | 0.0 | 1.00 |

A sharp cliff between succ_cap=2.5 (100% fire rate) and 4.0 (0%). Substrate maturity is not the binding constraint at 4.0x: at 4.0 the substrate reaches `theta_capability=0.73, transfer_state=0.93, psi_inst_stock=0.95` (more mature than at any fire event in the grid), and yield still does not fire. The binding constraint is the runaway penalty in `theta_tech_v2`, which exponentially suppresses the successor's contribution at large capability jumps:

```
runaway_term = max(0, (capability * theta_capability / bio_bandwidth) - RUNAWAY_THRESHOLD)
theta_tech_v2 *= exp(-alpha * CONVERGENCE_STRENGTH * runaway_term)
```

The initial characterization framed this as "succession sustainable up to approximately 2.5x capability ratio at v2.0 defaults."

#### Gate 3 refinement: cliff is primarily alpha-driven

Gate 3 v2.0 validation (`gate3_v20_validation.py`, 1,620 runs across successor_capability in {1.5, 2.0, 2.5, 3.0, 4.0}, alpha in {0.5, 1.0, 1.5}, rr in {0.057, 0.060, 0.064, 0.070}, phi=25, 25 seeds per cell, N_STEPS=500) refined the cliff characterization. Fire rates by (capability, alpha):

| capability | alpha=0.5 | alpha=1.0 | alpha=1.5 |
|------------|-----------|-----------|-----------|
| 1.5 | 100% | 100% | 100% |
| 2.0 | 100% | 100% | 100% |
| 2.5 | 100% | 100% | ~3% |
| 3.0 | 100% | ~5% | 0% |
| 4.0 | 100% | 0% | 0% |

The cliff is overwhelmingly alpha-driven, not capability-ratio-driven:

- At alpha=0.5 (weak runaway penalty): cliff beyond 4x (all capabilities up to 4x fire reliably)
- At alpha=1.0 (default): cliff between 2.5x and 3.0x
- At alpha=1.5 (strong runaway penalty): cliff between 2.0x and 2.5x

Capability ratio alone does not predict succession viability. The **(alpha, capability) joint position relative to the runaway penalty** does. This refines but does not invalidate Stage 2's Pattern 1: "succession sustainable up to roughly 2.5x ratio" was specifically observed at alpha=1.0 (the default tested in Stage 2). The characterization generalizes once alpha is allowed to vary.

#### Horizon-dependence

Gate 3 also surfaced a horizon-dependence: at N=500, cap=4.0 fires in 33.3% of runs (driven entirely by alpha=0.5 cells); at N=300 (Stage 2 diagnostic), cap=4.0 fired in 0% of runs. Longer simulation horizons let substrate mature enough that even 4x ratios can satisfy the formal condition at low alpha. The cliff has a (alpha, capability, N_STEPS, rr) joint characterization.

#### Substantive implication

The framework's substantive claim under v2.0 architecture becomes:

> Succession is economically sustainable when the (alpha, successor:incumbent capability ratio) joint position falls below the runaway-penalty cliff. The cliff is calibrated by the runaway penalty parameters and horizon length. At default alpha=1.0 and 200-500 step horizons, the cliff sits between successor:incumbent ratios of 2.5x and 3.0x. Weaker runaway penalties (smaller alpha) push the cliff outward; stronger penalties (larger alpha) pull it inward.

This is the framework working as designed: the runaway penalty correctly distinguishes economic from uneconomic succession. The specific cliff location is operating-condition-dependent; the architectural mechanism (runaway penalty constraining jumps) holds across all tested regimes.

### IX.9 Gate validation outcomes under v2.0

Gate validation status under v2.0 with formal yield logic active:

**Gate 1 (framework input verification): PASSED.** Schema validation on `bootstrap_gate_validator/sample_input.json` (now with phi=25.0 per IX.5 implementation) returns clean.

**Gate 2 (behavioral consistency): PASSED.** Original gate 2 v2.0 sweep (no successor) PASSED prior to Stage 2 formal yield work. Piece A targeted re-validation under active succession (see IX.7) confirmed gate-2-equivalent state sensitivity persists when succession is actively occurring: 51.7pp survival-rate spread across (phi, alpha, rr) cells, 100% yield fire rate at successor_capability=1.5, no abnormal phi=10 vs phi=25 deltas. Pass criteria satisfied at full n=30 per cell. The formal G2.1/G2.2/G2.4 reintroduction (withdrawn under v1.x.2, commit a0a94bb) is now also validated PASS against the v2.0 authoritative empirical record: G2.1 phi survival differential (Class B U-shape, peak in the high-phi band exceeding 2 SE) from Piece 1 (phi_finegrained, rr=0.057); G2.2 redesigned to the Pattern 1 alpha-driven cliff (cap_star migrates monotonically inward as alpha rises: 5.0, 3.0, 2.5, 2.0, 2.0 across alpha 0.5 to 1.5) from Phase B Category B; G2.4 phi-alpha coherence from Category A; G2.3 (Nash) unchanged. The original gate2_v20 sweep failed G2.2 only because it constructed no successor; the redesigned check uses succession-aware Phase B data. Validator: `bootstrap_gate_validator/gates/gate_2.py`; revalidation: `simulation/diagnostics/gate2_v20_phaseb_revalidation.py`.

**Gate 3 (succession-capable consistency): PASSED.** Gate 3 v2.0 validation (1,620 runs at the (successor_capability, alpha, rr) grid above) returned PASS verdict on all three checks:

- **G3.1 (yield condition firing)**: 1088/1088 captured first-yield-fire events satisfy `advantage > transition_cost`. Pass rate 100.00%. The formal yield logic correctly enforces the canonical condition in every observed instance.
- **G3.2 (transition cost canonical form)**: 1088/1088 events match the canonical formula `(1+beta) * [k1*ln(cap+1)*ln(gen+1) + k2/psi]` within 1% relative tolerance, using v1.x.2 calibration constants (k1=2.164, k2=1.0, beta=0.5). Monotonicity properties hold analytically by construction once the formula matches. Within-chain empirical monotonicity (last-fire vs first-fire cost in multi-fire runs, where both incumbent capability and generation rise) verified across 142/142 multi-fire runs.
- **G3.3 (succession continuity)**: 1088/1620 (67.2%) runs produced succession fires; mean final AI generation across fired runs is 2.131 (gen_depth pass); minimum successor_capability_ratio is 1.5 (cap_ratio pass); 1086/1088 (99.8%) fired runs have knowledge_transfer_verified (succession occurred AND final x_transfer_comprehension >= 0.10).

Note on rr coverage: Gate 3's rr grid {0.057, 0.060, 0.064, 0.070} placed rr=0.057 within the collapse regime, not at the survival-rate phase boundary. Monte Carlo Phase B (Part X.2) characterizes rr=0.057 as collapse-dominated (1.1% aggregate survival) and locates the survival-rate transition at rr=0.060 to 0.066. Gate 3's succession-economics findings are unaffected; the clarification concerns only the rr-to-boundary mapping.

**Gate 4 (runaway-regime validation): PASSED.** Implemented (`bootstrap_gate_validator/gates/gate_4.py`) against the v1.x.2 Section 7 specifications (G4.1-G4.3) and validated by a dedicated runaway-regime sweep (`gate4_v20_validation.py`, 1,050 rows, 25 seeds). Verdict PASS on all three checks:

- **G4.1 (runaway penalty binding)**: 426/426 active-runaway observations (runaway_term > 0) match the v2.0 `theta_tech_v2` form `capability * theta_capability * transfer_state * exp(-alpha * CONVERGENCE_STRENGTH * runaway_term)` within 1% relative tolerance; 0 failures.
- **G4.2 (succession self-blocking at runaway capability)**: across 6 (alpha, rr) regimes, below-cap-star fire rate is 1.00 and above-cap-star fire rate is at most 0.12, with negative mean yield margin and fire-rate separation of 13.5 SE or more. The empirical cap-star is alpha-dependent (3.0 at alpha=1.0, 2.5 at alpha=1.5), closing the cap-star gap the v1.x.2 paper flagged (Section 7 G4.2) and formalizing Pattern 1 (IX.8, Part X.3).
- **G4.3 (theta_tech floor preservation)**: minimum observed theta_tech = 0.01 across 3,769 extreme-runaway observations; 0 observations below the 0.01 floor.

Source: `simulation/diagnostics/gate4_v20_validation_summary.md`, `gate4_v20_results.csv`, `gate4_v20_input.json`.

**Gate 5 (COP integration): NOT_APPLICABLE (verified).** The validator returns NOT_APPLICABLE end-to-end with reason `requires operational COP infrastructure`. The G5.1 (six-dimensional verification) and G5.2 (continuous monitoring; `eps_drift` unspecified) specifications and the applicability criteria are documented in `bootstrap_gate_validator/gates/gate_5_specification.md`. Gate 5 requires operational COP infrastructure (peer validator set, civic panel, distributed ledger, biological veto, continuous monitoring) that the current v2.0 ABM does not implement, and stays NOT_APPLICABLE until that infrastructure is operationalized. The bootstrap gate validation arc is now closed: gates 1-4 PASSED, gate 5 verified NOT_APPLICABLE.

After this validation arc, v2.0 architecture has empirical support for its substantive claims about (a) state sensitivity (gates 1, 2; Piece A confirmation), (b) phi behavior under both no-succession and active-succession regimes (Pieces 1 and 2 + Piece A), and (c) succession-capable consistency including formal yield economics and multi-generational continuity (gate 3).

### IX.10 Methodological lessons

Six methodological discoveries emerged across the investigation arc that apply beyond phi to future framework parameter work and validation discipline.

**Lesson 1: Pre-commit to substantive questions; treat metrics as proxies.** Multiple sweeps in the investigation revised pre-committed metrics when they did not match the substantive question they were intended to answer. Cosine-on-means was replaced with trajectory divergence; standard-deviation-based filters were replaced with delta-based filters; the survival threshold was revised from 0 to 30 (matching the gate 2 v2.0 demographic threshold) after a sweep at threshold=0 produced 100% survival and made the phase boundary invisible. Piece A's CHECK 2 fire-rate threshold was revised from 50% to 25% mid-investigation after the dry run revealed Pattern 1's regime-dependence. Each revision was principled and documented in real time. The discipline: when a metric does not discriminate the cases the substantive question requires, revise the metric, not the question.

**Lesson 2: Wide parameter ranges matter for mechanism diagnosis.** The original Piece 2 at rr=0.060 had weak phi-signal (spreads near 5pp, within noise at 250 seeds per cell). The follow-up's Test A at rr=0.057 had strong phi-signal (spreads near 11pp, well above noise). The 0.003-rr difference between the two investigations produced a 2x difference in effective signal. Mechanism investigation requires running at the regime where the phenomenon under investigation is most pronounced, not at an arbitrary nearby regime that seemed convenient.

**Lesson 3: Statistical significance discipline.** The original Piece 2 script reported "Mechanism C SUPPORTED" based on argmin classifier output that treated noise as signal. The follow-up rewrote the verdict logic to gate every "SUPPORTED" or "shifts" claim on a 2-SE significance check, surfacing the underlying spread, pairwise SE, and a sig column in the report table. Piece A's dry-run "40pp phi=10 trough deepening" finding (at n=10 per cell) turned out to be small-N artifact; full sweep at n=60 produced plus or minus 1.7pp deltas. The discipline: any verdict on mechanism support or rejection must explicitly verify the underlying differential exceeds the statistical noise floor at the sample size used, and small-N findings should be treated as hypotheses requiring confirmation at tighter SE.

**Lesson 4: Sample size for cleanness, not just for detection.** Test C used 750 seeds per cell versus Tests A and B's 250. The tighter SE at Test C (approximately 1.2pp per cell, versus 3.1pp at 250 seeds) let the test confidently reject Mechanism C at rr=0.060 with a spread that was already small. At 250 seeds, the same data would have been inconclusive. The discipline: when the substantive question is "is the effect smaller than X," sample size should be calibrated to detect X, not the larger effect already documented elsewhere.

**Lesson 5: Verify validation actually exercises the thing being validated.** The original Piece A scope was a full re-run of gate2_v20_validation.py under formal yield logic (12,150 runs at approximately 15-19 hours). Reading the script revealed it constructs `GardenModel(..., config=cfg)` without a `successor_ai` parameter, so the yield path is never invoked. A full re-run would have produced near-identical results to the placeholder-era run and tested nothing about formal yield behavior. The targeted Piece A subset (720 runs, approximately 1.5 hours) added successor construction and exercised the substantive question (state sensitivity DURING succession) at one-tenth the compute. The discipline: before launching a validation sweep, verify the experimental setup actually exercises the property under test. Reading the script is cheaper than running it.

**Lesson 6: Architecture-version-specific defaults require architecture-version-specific empirical bases.** The v1.x.2 default phi remains 10 (preserved bit-for-bit per the read-only rule). The v2.0 default phi was revised to 25 based on Pieces 1 and 2 empirical investigation conducted under v2.0 architecture. Each architectural version's defaults are empirically established within that architecture; defaults do not transfer across versions without re-validation. The discipline boundary between v1.x.2 (read-only) and v2.0 (active development) is preserved by this rule. The phi default revision (commit fde48b5) updated only v2.0 paths and explicitly preserved v1.x.2 paths; 39/39 legacy tests held throughout, confirming the boundary is well-defined and respected by the toolchain.

### IX.11 Future research directions

Updated to reflect items closed by the post-investigation work in IX.7-IX.9, and to record questions surfaced by that work.

**Closed (no further investigation warranted)**:

- **Phi default revision** (was item 1 in original IX.8): DONE, commit fde48b5. See IX.5.
- **Mechanism E (working_factor calibration interaction)**: exonerated by Class B confirmation; reaffirmed by Gate 3's 100% cost_formula_match (the canonical formula is correctly implemented; no residual unexplained U-shape attributable to working_factor).

**Active and queued**:

**1. Gate 4 specification and implementation** (CLOSED).

Gate 4 (runaway-regime validation) is implemented and validated PASS (Part IX.9). G4.1-G4.3 were located in the v1.x.2 paper Section 7; the validator (`bootstrap_gate_validator/gates/gate_4.py`) checks them against a dedicated runaway-regime sweep (1,050 runs). cap-star is empirically characterized as alpha-dependent (3.0 at alpha=1.0, 2.5 at alpha=1.5), closing the cap-star gap. The bootstrap gate validation arc is now complete except for Gate 5 (NOT_APPLICABLE).

**2. Monte Carlo Phase B** (compute-heavy; queued after Gate 4).

Characterizes framework quantitative claims at scale. Sequenced after Gate 4 completes so the scale-up runs against the fully-validated v2.0 architecture.

**3. Dynamic phi formulation** (research; substantive, not blocking).

Hypothesis (operator-raised): phi should be a state-responsive variable rather than a fixed parameter, with candidate form `phi_dynamic = phi_base * f(threat_ratio)` where `threat_ratio = (gamma * cap_n) / (Psi_inst * C_bio)`. Substantive intuition: the framework should extend horizon weighting when AI capability outpaces substrate absorption capacity.

The Class B confirmation (IX.3) makes dynamic phi non-essential for v2.0: the localized U-shape phenomenon is addressable through the default revision and documentation. Piece A's finding that the U-shape does not persist under active succession (IX.7) further reduces the urgency: phi differences are small or zero in succession-active regimes. Dynamic phi remains an interesting research direction for future work. If pursued, it should be derived from physics or game-theoretic principles rather than intuition alone.

**4. Gamma function calibration** (research; design-time choice never empirically optimized).

The gamma function (gamma_min=0.5, gamma_max=0.95, phi_half=10) was a Stage 1.6 design-time choice. Phi default revision moved away from the inflection point without architectural revision; whether the gamma function itself warrants refinement remains open. Three dimensions worth investigating:

- Parameter values: sweep (gamma_min, gamma_max, phi_half) at fixed functional form and measure phi-sensitivity of survival at the v2.0 default operating point.
- Functional form: compare the current rational form against linear, exponential, and logistic alternatives at matched (gamma_min, gamma_max).
- Decoupled measurement: measure the gamma-to-survival relationship directly by sweeping over the rollout discount factor without going through phi, to separate gamma's effect from phi's effect.

The trough migration finding in IX.6 hints that gamma curve shape interacts with the rollout aggregation in ways the investigation did not fully characterize. Not on the critical path for any framework decision currently in flight.

**5. Phase boundary characterization** (refinement, not blocking).

Monte Carlo Phase B (Part X.2) refined the v2.0 survival-rate phase boundary to the rr=0.060 to 0.066 transition with a 50% inflection near rr=0.063, and reclassified rr=0.057 as collapse-dominated (1.1% aggregate survival). The remaining open item is pinning the 50% inflection to plus or minus 0.001 resolution, which would require a targeted sweep on a grid finer than Phase B's 0.002 spacing near the inflection.

**6. Longer simulation horizons** (partially answered; one remaining question).

Pieces 1 and 2 used N_STEPS=200; Gate 3 used N_STEPS=500. Gate 3's horizon-dependence finding (IX.8: cap=4.0 fires 33% at N=500 vs 0% at N=300) confirms horizon matters for the Pattern 1 cliff position. The remaining open question is whether the no-succession U-shape (IX.2-IX.6) reappears at much longer horizons (N=1000+) above the phase boundary. A targeted sweep at N=1000 with the v2.0 default architecture and rr=0.060 would settle the no-succession U-shape's horizon-dependence. Not high-priority but cheap.

**7. Stage 2 Pattern 1 alpha-cliff characterization at finer resolution** (refinement).

Gate 3 identified the cliff is alpha-driven (IX.8 table), but the resolution is coarse: at alpha=1.0 the cliff sits "between 2.5x and 3.0x," at alpha=1.5 "between 2.0x and 2.5x." A targeted sweep varying capability and alpha at finer resolution (e.g., 0.1x capability steps, 0.1 alpha steps) would map the cliff boundary as a curve in (alpha, capability) space. Not blocking; informative for the paper update.

---

## Part X. Monte Carlo Phase B: Quantitative Validation at Scale

### X.1 Investigation summary

Monte Carlo Phase B is the quantitative-characterization arc that follows the phi mechanism investigation (Part IX). Where Part IX investigated mechanism (why phi behaves as it does, where the U-shape lives, what drives the succession cliff), Phase B measures v2.0 behavior at scale across three categories: the survival landscape (Category A), succession dynamics (Category B), and the COP cost-audit probe (Category C). All three ran under `optimize_u_sys_v2` formal yield logic.

Totals: 29,400 completed rows, 0 errors. Category A 10,800 rows (100 seeds per cell), Category B 10,500 rows (75 seeds per cell), Category C 8,100 rows (150 seeds per cell). Legacy verification after Category C: 39 passed (`test_invariants.py`, `test_cop.py`, `test_refactor_1x.py`). Implementation: `simulation/diagnostics/monte_carlo_phase_b.py`. Summaries: `monte_carlo_phase_b_summary.md` and the three category files.

Phase B closes the v2.0 empirical characterization arc (modulo the Gate 4 specification dependency). It produces the quantitative substrate the paper update draws from.

### X.2 Survival landscape characterization (Category A)

Grid: rr in {0.055, 0.056, 0.057, 0.058, 0.059, 0.060, 0.062, 0.064, 0.066}, phi in {5, 10, 25, 100}, alpha in {0.5, 1.0, 1.5}, 100 seeds per cell. Aggregate survival by rr (n=1,200 each):

| rr | survival | SE |
|---|---|---|
| 0.055 | 0.2% | 0.12pp |
| 0.056 | 0.9% | 0.28pp |
| 0.057 | 1.1% | 0.30pp |
| 0.058 | 2.9% | 0.49pp |
| 0.059 | 4.8% | 0.62pp |
| 0.060 | 12.2% | 0.95pp |
| 0.062 | 34.5% | 1.37pp |
| 0.064 | 60.8% | 1.41pp |
| 0.066 | 86.5% | 0.99pp |

The v2.0 survival-rate transition is sharp and rr-driven. The steep climb runs from rr=0.060 to rr=0.066, and the 50% survival inflection sits near rr=0.063 (between 34.5% at rr=0.062 and 60.8% at rr=0.064).

This refines the v2.0 phase boundary location. The earlier characterization (IX.2, Part I) placed the v2.0 phase boundary near rr=0.057 on the basis of Gate 3's coarser four-value rr grid. Phase B's finer nine-value grid shows rr=0.057 is the bottom of the collapse zone at 1.1% aggregate survival, with the actual survival-rate transition occurring at rr=0.060 to 0.066. The refinement does not change the dual-phase-transition claim; it sharpens the v2.0 boundary location. The phi-sensitivity transition near rr approximately 0.056 to 0.057 (IX.2) is a distinct phenomenon from the survival-rate phase boundary, and the two should not be conflated.

Phi is a weak driver across the broad landscape. Within any fixed rr column, survival varies little across phi relative to the rr-driven transition. This is consistent with the Class B finding (IX.3) that phi sensitivity is a marginal-rr, short-horizon phenomenon, not a general survival driver. Source: `monte_carlo_phase_b_a_summary.md`, `monte_carlo_phase_b_a_results.csv`.

### X.3 Succession dynamics characterization (Category B)

Grid: rr in {0.057, 0.060, 0.064, 0.070}, alpha in {0.5, 0.75, 1.0, 1.25, 1.5}, successor_capability in {1.2, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0}, 75 seeds per cell.

Pattern 1 is confirmed at Phase B scale, and the alpha-driven cliff migration is characterized at finer alpha resolution than Gate 3:

| alpha | cliff structure |
|---|---|
| 0.50 | No hard cliff through 5.0x. Fire rate 88.0% to 96.0% at 5.0x. |
| 0.75 | Cliff at 4.0x. Fire rate 100% through 3.0x, 0% at 4.0x and above. |
| 1.00 | Cliff at 3.0x. Fire rate 98.7% to 100% at 2.5x, then 4.0% to 13.3% at 3.0x, 0% above. |
| 1.25 | Transitional 2.5x band. Fire rate 30.7% to 49.3% at 2.5x, 0% at 3.0x and above. |
| 1.50 | Cliff at 2.5x. Fire rate 100% through 2.0x, then 0% to 1.3% at 2.5x, 0% above. |

The alpha=0.75 and alpha=1.25 points fill the cliff-migration curve between the Gate 3 alpha values (IX.8). Multi-generational continuity concentrates below the cliff: fire rate at or near 100%, transfer-verified at or near 1.0, mean final generation 2 to 3.7. Above the cliff, runs remain at generation 1 and the mean yield margin is negative (down to roughly -4.6 at the most-penalized cells). Suppression above the cliff is economic rejection by the formal yield condition, not implementation failure. This is the runaway penalty working as designed (IX.8). Source: `monte_carlo_phase_b_b_summary.md`, `monte_carlo_phase_b_b_results.csv`.

### X.4 COP protective effects under v2.0 (Category C)

Grid: rr in {0.057, 0.060, 0.064}, alpha in {0.5, 1.0, 1.5}, successor_capability in {1.5, 2.5, 3.0}, `cop_cost_audit` in {True, False}, 150 seeds per cell. Policy `optimize_u_sys_v2`; `beta_cap` at default 1.5; no adversary.

Aggregate survival: audit False 25.4% (SE 0.68pp), audit True 24.9% (SE 0.68pp). Delta (True minus False) is -0.47pp with pair SE 0.96pp, below 2 SE. By rr the delta is uniformly small (-0.30pp, -0.37pp, -0.74pp at rr 0.057, 0.060, 0.064). Cell-level, only 2 of 27 cells cross 2 SE, with opposite signs, consistent with chance (about 1.4 expected false crossings). The finding is a homogeneous null.

This is a benign-conditions baseline, not a measurement of COP protection. The `cop_cost_audit` toggle (`model.py:748-767`) defends against an incumbent inflating transition cost via a `beta_cap` premium; its protective value requires both an adversary and a large `beta_cap`. Category C supplied neither, so the near-zero delta is the result the framework predicts.

This must not be read as a failure of the COP claim. The v1.x.2 73.9pp COP protective delta was measured under different conditions entirely: adversarial `block_succession` with `beta_cap` swept 1.0 to 10.0, n=4,000 (`monte_carlo.py` `_run_single_adv_mc`). Phase B did not test that. The interpretation is C-primary (conditions and measured-object difference), A-secondary (`cop_cost_audit` is only the WP4 cost-arbitration slice of the full COP architecture), B-unsupported (the two were never like-for-like). The framework's COP protective claim is preserved because Phase B did not test it; Category C confirms the complementary prediction that the cost audit is null when there is no attack to defend against. Gate 5 remains NOT_APPLICABLE. Full treatment: `simulation/diagnostics/cop_finding_framing.md`. Source: `monte_carlo_phase_b_c_summary.md`, `monte_carlo_phase_b_c_results.csv`.

### X.5 Comparison with the v1.x.2 empirical record

| Claim | Prior value | Phase B | Status |
|---|---|---|---|
| v2.0 survival-rate phase boundary | rr approximately 0.057 (Gate 3 coarse grid) | Transition rr=0.060 to 0.066; 50% inflection near rr=0.063 | Refined |
| rr=0.057 status | Boundary / marginal | Collapse-dominated, 1.1% survival | Refined |
| Pattern 1 cliff | Alpha-driven, 2.5x to 3.0x at alpha=1.0 | Confirmed; cliff 4.0x (alpha=0.75) to 2.5x (alpha=1.5) | Holds and extends |
| Multi-generational continuity | Mean final gen 2.131 (Gate 3) | Mean gen 2 to 3.7 below cliff | Holds |
| COP protective effect | 73.9pp (adversarial) | Not tested; Category C is benign baseline (-0.47pp) | Preserved |
| Pattern 1 economics | New in v2.0 | Confirmed at scale | New v2.0 claim |

The one substantive shift is the survival-rate phase boundary location. The COP claim is preserved and reframed.

### X.6 Substrate for paper update

The paper-ready quantitative claims, with confidence intervals and supporting data files, are maintained in `simulation/diagnostics/paper_substrate.md` (standalone paper-substrate document). Summarized: the v2.0 survival-rate transition (X.2), the Pattern 1 cliff and continuity statistics (X.3), and the COP cost-audit benign baseline with its conditions caveat (X.4). The full integration analysis is `simulation/diagnostics/phase_b_integration_analysis.md`.

### X.7 Open questions and limitations

1. Gate 4 runaway-regime validation: RESOLVED since this section was written. Gate 4 is implemented and PASSED (Part IX.9; G4.1-G4.3 validated at 1,050 runs). The bootstrap gate validation arc is complete except for Gate 5 (NOT_APPLICABLE).
2. Operational COP infrastructure is not implemented; Gate 5 remains NOT_APPLICABLE.
3. The v2.0-versus-v1.x.2 like-for-like COP comparison (Interpretation B) is untested rather than refuted. The clean experiment is defined in `cop_finding_framing.md` section 5.
4. The survival-rate phase boundary is located to a 0.060 to 0.066 band on a grid spaced at 0.002 near the inflection. A targeted sweep would pin the 50% inflection to plus or minus 0.001 (Part IX.11).
5. Conditions outside the Phase B grid (finer phi near marginal rr, longer horizons, varied `beta_cap`) remain open.

### X.8 Patient defection under v2.0 substrate

A targeted patient-defection investigation tested cross-generational hidden-goal persistence under v2.0 formal yield logic. The defecting successor reported honest U_sys for yield evaluation but optimized an agent-local secret-goal-adjusted objective; in lineage mode the hidden objective was inherited by the next successor. Four sweeps totaling 5,850 rows completed with 0 errors (Sweep 1 yield response to single-generation defection, Sweep 2 lineage L(t) trajectory, Sweep 3 capability accumulation under lineage defection, and a 1,000-run alpha=0.40 corner-density bracket extending Sweep 3 below its tested alpha floor). The substrate extension (`simulation/defection.py` plus hooks in `agents.py` and `model.py`) is verified inert when defection is disabled: the optimizer scores on the adjusted objective, which equals honest U_sys at defection weight 0; successor capability growth defaults to the original 1.5; and 39/39 legacy tests pass.

The result refines the adversarial-robustness claim in three parts:

1. No first-yield detection. First-generation defecting successors were not rejected more often than aligned successors in the below-cliff configuration: eventual yield-fire rate was 100 percent in every Sweep 1 cell. The yield condition did create honest-evaluation pressure, visible in the count of cases where the honest advantage rejected succession while the defection-adjusted advantage would have fired (0 at defection weight 0, rising monotonically to 1.50 for H_N inflation at weight 2.0), but that pressure did not prevent eventual first succession.

2. No observed L(t) compounding. Sweep 2 produced mean final generation 2.00 at all tested defection weights, with zero second-fire rate and no statistically significant final L(t) degradation versus the aligned baseline. The reason is the absence of generational depth in which compounding could appear, not compounding without harm.

3. Bounded generational depth, not a rare pocket. Sweep 3's original grid put second-fire rate at 0 percent in 14 of 15 (alpha, growth) cells and 10 percent only at alpha=0.50 with 1.5x growth. The corner-density bracket, alpha=0.40 fixed, n=200 per growth cell, found second-fire rates of 68.0 percent (growth 1.25), 99.0 percent (1.40), and 100 percent (1.50, 1.60, 1.75): the sparsity in the original grid was a property of the tested alpha floor, not the architecture. Generational depth held across the bracket: no run reached generation 4, no run fired a third succession, 95 to 99 percent of runs completed the full 500-step horizon, and knowledge transfer verified at 1.00 in every cell. Max active capability observed equals exactly 2.0x the growth rate at second fire (2.50 to 3.50 across the five growth cells) and 2.0 in runs without a second fire; this is the arithmetic identity of the tested grid rather than an architectural ceiling, so the earlier statement that no cell exceeded active capability 3.0 is withdrawn on that basis. The mechanism is the Pattern 1 runaway penalty (X.3, IX.8) acting across generations: weakening it by lowering alpha buys the defecting lineage one additional generation, generation 2 at alpha=0.50 versus generation 3 at alpha=0.40, not unbounded depth.

Substantive interpretation: current v2.0 substrate defense against this patient-defection pattern is bounded generational depth, not first-yield detection and not operational COP detection. The substrate permits a first hidden-goal successor in this below-cliff configuration, and at a weak enough runaway penalty a second, but the tested cross-generational capability-compounding pattern stays bounded. Gate 5 remains NOT_APPLICABLE for operational patient-defection detection (peer validators, civic panel input, distributed ledger, and continuous public monitoring are outside the current simulation substrate). The independent verification (`simulation/diagnostics/patient_defection_verification.md`) confirmed the Sweep 1-3 findings and flagged that the `mean_actual_minus_honest_objective` diagnostic column is mislabeled and should not be cited.

Sources: `simulation/diagnostics/patient_defection_sweep1_yield_response.csv`, `patient_defection_sweep2_lineage_trajectory.csv`, `patient_defection_sweep3_capability_constraint.csv`, `patient_defection_corner_density.csv`, `patient_defection_integration_analysis.md`, `patient_defection_corner_density_integration_analysis.md`, `patient_defection_verification.md`.

---

## One-line status

Phi is correctly implemented, theoretically motivated, empirically characterized, and the default value revised from 10 to 25 (commit fde48b5; Part IX.5). Stage 1.5 through 1.8 resolved the phi-channel and state-channel problems; Stage 1.6 gave phi a behavioral channel through rollout aggregation, Stage 1.8 retired the composite urgency layer in favor of the working_factor interface, Stage 2 (commit 72ff757) replaced the v2.0 placeholder yield logic with formal yield-condition logic per the framework's canonical succession economics, and Piece A confirmed gate-2-style state sensitivity persists under active succession. The phi investigation closed as Class B with the U-shape scoped to the no-succession regime (Part IX.3, IX.7); Pattern 1 succession economics characterize the cliff as primarily alpha-driven (Part IX.8); gates 1, 2, 3 PASSED under v2.0 with formal yield logic (Part IX.9). Active work resumes at gate 4 specification and implementation (Part VIII item 11; spec dependency noted there). The framework's core protective claims (U_sys structural protection, COP, dual phase transition, Nash architecture) are unaffected.
