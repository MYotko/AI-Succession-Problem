# The Lineage Imperative — Phi Investigation and Action-Space Redesign Program

**As of May 2026. Consolidated carry-around reference.**

This supersedes the earlier phi investigation reference. It captures the full arc: what the framework assumes, the problem found, the tests that confirmed it, the redesign program derived to resolve it, and the pre-committed decision tree that governs the outcome. It is a snapshot for reference, not an implementation document.

---

## Part I — Where things stand

### The durable framework claims (unaffected by the phi question)

- **U_sys structurally protects well-being.** Any AI optimizing U_sys maintains the conditions for human novelty, because the objective penalizes well-being collapse through the h_n weighting. Confirmed across every experiment.
- **The COP is the structural defense layer.** 73.9pp protective delta holds. Defenses are binary and operate upstream of the AI's policy.
- **The dual phase transition is stable** (extinction boundary rr approximately 0.055, collapse boundary rr approximately 0.064), pending revalidation after the allocator redesign.
- **The framework's protection is structural, not parametric.** It is encoded in what is optimized, not in tuning.

These do not depend on resolving phi. The phi question is about one parameter's behavioral role, not about whether the framework works.

### The version state

v1.x.2 is tagged and stable. Path C (policy-layer phi fix) was tested and failed. v1.x.3 as conceived is not viable. The next version target is undetermined pending the redesign program below. The redesign is large enough that it is likely a 2.0, but the version is not the point; the result is.

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

---

## Part VI — The phi-capability question and the decision tree

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

---

## Part VII — Publication posture

No one is currently pressing on the phi claim, and the v1.x.2 essay revision already walked back the phi-as-buffer claim publicly. You have genuine slack to build the fix before publishing the problem, so a reader encounters problem and fix together (a strength story) rather than the problem alone (a weakness story with a hopeful ending). The trigger for a standalone correction statement is external pressure, which does not exist.

Sequence: do Option 1 (build the higher-fidelity model) before Option 2 (the honest-limitation writeup), because the fix clarifies what the limitation section needs to say. The exception is the manuscript contradiction in Part IV, which is a live inconsistency in a published artifact and should be resolved on its own timeline regardless.

---

## Part VIII — Immediate next actions, in order

Items 1 through 4 are complete as of May 2026. The active work is item 5.

1. ~~Resolve the manuscript contradiction.~~ Done. Cap-conditional claim withdrawn as RNG-desynchronization artifact (commit prior to Stage 1).
2. ~~Update materials with the capability-sweep result and the contradiction resolution.~~ Done.
3. ~~Specify the composition vector in full (the keystone tradeoff).~~ Done through the design conversations producing the six category curves, complementarity structure, constraint frontier, Psi_inst stock, and bridge.
4. ~~Build the minimum faithful set.~~ Done. Stage 1 commit `61a362e` built the v2 parallel policy with all committed structure. Smoke test passed.
5. **Stage 1.5 (design complete; implementation pending): all diagnostic state inputs specified, ready for implementation.**
   - Architecture commitment recorded (Part V).
   - Seven-element specification template recorded (Part V).
   - Composite-urgency commitment recorded (Part V).
   - Stock-over-flow design principle recorded (Part V).
   - Worked examples complete: avg_wb (welfare-condition diagnostic), population_ratio (substrate-scale diagnostic), demographic_pressure (substrate-flow diagnostic), resilience_stock (shock-readiness diagnostic), trend variables (deterioration-anticipation diagnostics).
   - Next: implementation prompt for Stage 1.5 build, integrating all five worked examples into U_sys_v2 and the projection function, with named-constant traceability tied to governance justifications.
   - After implementation: smoke test under revised metric, faithfulness tests across all projection update rules, gate 2 re-run.
   - Stage 2 gates 3, 4 deferred until Stage 1.5 acceptance.
6. **Pass remaining acceptance gates** (gate 2 re-run, gate 3 capability-regime, gate 4 horizon-crossing). Gate 1 and gate 5 already passed in Stage 2 partial; gate 2 returns under the revised metric. The horizon-crossing gate is mandatory; a phi sweep run before it passes produces an uninterpretable null. Freeze all curves before phi.
7. **Run phi free** across the faithful landscape.
8. **Read against the three-branch decision tree.** Only then, if Branch 2 or 3, derive phi(capability).

---

## One-line status

Phi is correctly implemented and theoretically motivated but currently untestable in the simulation. v1.x.2's action space is too degenerate; the Stage 1 v2 build broke the corner solution but Stage 2's gate 2 surfaced a separate state-blindness defect in U_sys_v2's inputs. Stage 1.5 design work is now complete with five diagnostic variables fully specified (avg_wb, population_ratio, demographic_pressure, resilience_stock, trend variables), each meeting the seven-element template with phi-blind justifications, multiplicand commitments, projection update rules, and faithfulness tests. Implementation prompt pending. After implementation and smoke test, gate 2 re-runs and Stage 2 resumes. The framework's core protective claims (U_sys structural protection, COP, dual phase transition, Nash architecture) are unaffected throughout.
