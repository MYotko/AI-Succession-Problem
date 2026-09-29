# v3 instrument implementation note, Stages A, B1 and B2

2026-09-27. Baseline: branch `v3-instrument`, commit
`7fa966822da4f4f35a41a26e6a2b95dcd41a700d`. This revision supersedes the
Stage A proposals with resolutions R3 through R15, 2026-09-27. Section 12
records B2 and supersedes the B1 estimator and runner plans. The instrument
has production interfaces and a non-registered pilot bundle. Registered
execution requires committed source, a committed pre-registration pin,
registered calibration and complete non-fixture tables. Those artifacts
have not been produced or launched in this session. No existing v2 file was changed, and no
input document was copied into the public repository.

**Morning review: material deviations and limitations.** Resolution R14,
2026-09-27 accepts the B1 fallback, stock and welfare grids, restricted
plans and period-end deadlines, and reduced validation plus estimator
stability. Their mathematical limits below remain explicit.

* R8 cohort admission is implemented, including a deterministic bound from
  the original v2 initial law. A failed cohort bound does not identify the
  true survival-maximizing action. The safe fallback minimizes the bound,
  preserves both floors and holds yield. It does not claim true-risk R7
  compliance or certified infeasibility. This mathematical gap remains.
* R4 uses 16 environmental stock microsteps per demographic step to combine
  the requested 0.01 grid, neighbor support and the legacy mean dynamics.
  Reflected symmetric noise prevents absorbing endpoints. The demographic
  step can therefore traverse multiple stock neighbors. Strict one-neighbor
  support per demographic step is not claimed. Welfare also uses a 0.001
  grid, an additional declared quantization explained in section 2.
* The online class is reduced from 289 to 25 rules under R5/R11, before any
  table estimate. Seeds, rerun grids and allocation frequency are unchanged.
* R9 searches complete plans in a declared restricted class: the selected
  incumbent rule until a later yield, then any stationary successor rule;
  hold plans cover every stationary rule. It does not solve the unrestricted
  adaptive stopping problem or all incumbent/successor rule pairs.
* Full-state QSD dominance and uniform continuation accuracy are not
  established by reduced checks or empirical stability. R14 accepts this
  validation approach. B2 implements the production gates and estimators;
  registered calibration and full table data are still future executions.
* Neither the 72-hour nor 24-hour ceiling has been measured on X2. The B1
  timing and WE scenarios in section 8 are historical. R13 replaces that
  estimator cost scenario with plain/FV and a declared sensitivity subset.
  R15 requires the measured pilot projections in section 12. No budget
  pass is claimed before the operator runs the prepared X2 bundle.

The references are objective specification draft 3, S1-S10; decisions
D6-D18, especially D18; pre-registration draft 1, sections 3-7 and 12;
and the stage 4 decisions brief. Resolution R12, 2026-09-27 supersedes the
draft's instruction to copy the specification. References and byte hashes
are retained instead:

| Read-only input | SHA256 |
|---|---|
| Objective specification draft 3 | `57653952e6d65c21907af3e6982ca71cab8f6c5967fcb593b86c93f14f643e13` |
| Decisions D6-D18 | `5e4633561f495e6f83c974f1cb9c290e56206cf03204537ee4a7489ca635875f` |
| Runner rules | `5f577af7d9c27d0c3be191cb9b5571d031eee5706f201c781d8c6f66c222c25b` |
| Stage B1 directive, including resolutions | `15061e0cd5e190910cdfb3b7293903308de0c29e7d320004a7ca7def8c437f19` |
| Stage B2 directive, including R13-R15 | `8d9f3f2dd2ae9633b1d3eb25f792236fb579ca2cc033e5b02c5c5761010f44d6` |
| Pre-registration draft 1 | `ee934ed814fa0cae5ef9b507b4255178fb02eb7b8a3c2526b5592346e41972cf` |
| Stage 4 decisions brief | `2b1e04c166c0b87dec7e3611cea669f36599d662cd63f43508cd6a9e14ce7dba` |
| Rare-event report | `4510f3d98d27dbdf61940544e1d578a8aecef405cb5e1750954157b7436342cb` |
| X2 analysis | `b3e13ae247d2f0d6d5ab828fcc4d7a6b74056c87467382530620a4130eaa65d8` |

## 1. Existing objective entry points and changed behavior

Line numbers refer to the unchanged baseline.

| Location | Existing behavior | v3 behavior |
|---|---|---|
| `simulation/agents.py:648`, `optimize_u_sys_v2`; candidates at 671, rollout at 686 | Maximizes projected U_sys over 300 candidate allocations. | `V3Model.evaluate` reapplies each stationary feedback rule at every projected state, scores W and selects an action every actual step. |
| `simulation/agents.py:593`, `project_u_sys_v2_rollout` | Holds an action fixed for 20 aggregate projection steps with a phi-dependent discount. | Full individual transitions for 20 post-action rewards; fixed beta; continuation and frozen Lambda_F lookups. |
| `simulation/metrics.py:609`, `calculate_system_metrics_v2`; product at 719 | Floored novelty and stocks, inverse-scarcity weighted levels and discount/lineage multiplier. | H_N, H_E, L and logarithmic flow are separate from D_rho, Lambda_F and W. |
| `simulation/model.py:1260`, `_step_v2`; optimization at 1300/1314; comparison at 1348-1357 | Compares snapshot objectives against a formula transition cost. | Complete immediate and waiting plans, S5 filtering, committed epoch units, actual drawdown simulated once. |
| `simulation/model.py:1541`, metrics in `_step_v2` | Records the old objective after demographic and stock updates. | Records realized flow, selected rule, objective components, admission, overrides and unresolved ordering; continues after extinction. |
| `simulation/agents.py:855`, `AIAgent.estimate_transition_cost`; call at `model.py:1337` | Generation/capability/institution formula with uncertainty premium. | Not used by v3. |
| `simulation/model.py:562`, `apply_succession_transition_load`; call at 1409 | Actual institutional drawdown in addition to the formula comparison. | `stocks.transition_drawdown` uses these constants and this actual load in each successor plan and once in the realized handoff. |

Allocation reaches biology through `model.py:1456` and its welfare bridge
at line 125. `HumanAgent.step`, `agents.py:804`, ages agents, updates welfare,
attempts births and schedules mortality. Balanced welfare maps to r=0.9.
The v3 wrapper imports `GardenModel` only for the initial population and
uses a separate executor. It never calls the legacy model step.

The active v2 stock path is `model.py:1488-1500`, using
`working_factor.apply_working_factor` and `apply_delta_state`. The older
institution and resilience update methods remain on the class but are
not the current step's stock law. The B1 mean-path validation calls the
actual `working_factor` functions, not just a copied formula.

## 2. Measurements and full state, S1-S2

### Novelty, resolution R3, 2026-09-27

`measurements.py` provides the standalone arithmetic; `engine.py` batches
the same measurements across complete population states. Each state keeps
every living agent's age, welfare and ten novelty propensities, all four
stocks, the previous H_N used by contagion, and ten full sample windows.
Each window retains up to 64 vectors, newest step first, including empty
steps. Unused dead propensity records are removed, so history does not
silently create unbounded auxiliary chain state.

Use n=64, d=10 and a fixed baseline center c. Select living agents uniformly
without replacement when N>=64. Random priorities are environmental,
independent of the chosen action. Novelty is generated from each sampled
agent's propensity and welfare, the fixed balanced suppression 0.1315,
and the legacy clipped contagion convention. Sampling occurs after the
population update, including newborns. This timing is declared; v2 generated
its samples during each parent's step before births and deaths were applied.

Clip coordinates to c plus or minus B=1.0. If N<64, concatenate retained
samples newest first and take the first 64. Use zero if the ten-step
lookback is insufficient. At extinction clear the window and use zero.
Sampling law invariance, rather than pathwise equality under a shared
random stream, is the population-size claim. Under the same conditional
sampling law, pooled mean H_N must agree within max(5 percent relative,
0.01 bits). The integration test uses N=16,64,200 and independent repeats.
It holds contagion fixed to isolate that sampling-law claim. It does not
assert that different endogenous populations have identical novelty laws.

Compute fixed-center covariance `Sigma=sum((x-c)(x-c)^T)/64`, then
`H_N=log2(det(I+Sigma/sigma0_squared))/2`. No sample centering or n-1 divisor
is used. Determinants are batched with `numpy.linalg.slogdet`.
`sigma0_squared=0.1*V_ref/d`, where V_ref is total baseline variance.
The B1 fixture uses zero center and `metrics.H_N_V_REF=0.0238802249185`;
these are not B2 calibration outputs. H_N is bounded by
`d/2*log2(1+B^2/sigma0_squared)`. Proper suppression reduces full-window
H_N; a rolling window during a transition can rise.

### Other observables, resolution R4, 2026-09-27

| Quantity | Declared mapping to current simulation state |
|---|---|
| H_E | `1-exp(-2.5*x_compute)`, in [0,1]. The shared minimum is zero because a stressed rule can devote everything to welfare. |
| D_gen | Mean pairwise L1 distance between ten-dimensional novelty propensity vectors, divided by 10*(0.5-0.05). Computed by sorting, using all living agents. Zero for N<2 or identical traits. A labeled diversity proxy, not a genomic measurement. |
| nu | `min(N/N_ref,1)`, with fixture N_ref=200. |
| Psi | Institutional stock alone, without a positive floor. |
| Frontier v | Fixed chain capability times technology stock, with ceiling and v_max=5.0. |
| Bandwidth b | Mean living welfare times transfer stock. |
| phi_tr | `exp(-(1-transfer_stock)*v/v_max)`, approaching one as v vanishes. |
| Theta | `phi_tr*exp(-alpha*max(0,v/max(b,b_min)-1))`. |
| L | `D_gen*nu*Psi*Theta`, in [0,1], with no factor floor. |

Genomes, an independently measured institutional response panel and a
physical velocity/bandwidth measurement do not exist in v2. These adopted
observables remain labeled proxies. `novelty_agency` is a resource channel,
not a direct variance control. With fixed constraint posture it currently
has no separate causal novelty mechanism.

All alpha cells use the same bandwidth clip, computed at alpha_min=0.5:
`b_min=v_max/(1+log(1/epsilon_L)/alpha_min)`. This guarantees
Theta(v_max,b_min)<=epsilon_L even at phi_tr=1. A diagnostic counts clipped
bandwidth. At v=0, Theta=1 regardless of transfer stock. Psi, diversity and
population can each reach zero; there is no absorbing positive lineage floor.

Fixture epsilons are all 1e-6. Calibration in B2 must replace them with
values below protected, reliably measured levels and freeze the result.
The proposed rule is one percent of the smallest positive reliable
calibration lower measurement bound for each quantity. If no such bound
exists, flag unresolved calibration instead of fitting target outcomes.
One H_E minimum is used for all rules and capabilities.

### Finite grids and environmental rounding

Stocks are integer hundredths on [0,100]. Targets, in institution,
resilience, technology, transfer order, are
`min(1, [0.4,0.2,0.5,0.4]+[2.2,3.5,1.6,2.0]*[x_inst,x_res,x_compute,x_transfer])`.
Legacy rates are [0.10,0.12,0.05,0.10]. One demographic step contains
16 stock microsteps, with rates `1-(1-rate)^(1/16)`. Each microstep moves
up/down one grid node or stays. Up/down probabilities use the signed
target drift plus symmetric noise 0.005. Reflect outward moves at endpoints.
Every inward neighbor and self move has positive probability. No stock
endpoint is absorbing. The mean equals the legacy macro update away from
boundaries; reflection introduces a measured boundary bias.

A 256-replica check against the actual continuous v2 update, over 500 steps
at rr=.055,.066,.080 under balanced allocation, uses maximum mean-path
absolute error <=0.015. Observed errors are 0.003622, 0.004362 and 0.006112.
The stock kernel itself does not depend on rr; different seeds check the
three requested configurations. This is a mean-path validation, not
distributional equivalence. Strict NP support per demographic step would
require a different design; the connected-neighbor claim here is per
environmental microstep.

Welfare uses integer thousandths with unbiased environmental rounding.
Initial uniform [.5,.8] welfare and newborn welfare are pushed onto this
grid; ages and propensity draws use the legacy initialization. A welfare
update adds `max(40,38+12*x_welfare)-updated_age` thousandths before rounding
and clipping. Balanced increments are integral. Every rounding outcome
under an admissible action is at least the deterministic balanced floor.
This extra quantization changes the distribution very slightly and is
declared for review. The initial-law survival enclosure in section 5 also
bounds the original continuous initial welfare law.

## 3. Flow, discounting and tail, S3-S4

`objective.py` implements
`u=lambda*log(H_N+eps_N)+mu*log(H_E+eps_E)+kappa*log(L+eps_L)`.
Weights are positive; fixture lambda=5, mu=3, kappa=8, theta=.5.
Each marginal is its weight divided by measurement plus epsilon, positive
and decreasing. The common extinction flow is
`u_dagger=lambda*log(eps_N)+mu*log(H_E_min+eps_E)+kappa*log(eps_L)`.
Every living flow is at least u_dagger; the bounded measurement domain
also supplies u_max. Empty populations remain empty and keep accruing
u_dagger. Reduced LS at an already extinct state is zero.

Resolution R6, 2026-09-27 fixes rho=.01, Delta=1, beta=exp(-.01), T_P=25,
H=25 and the first post-action reward convention. Allocation uses T=20:

`D_hat=(1-beta)*sum(t=0..T-1, beta^t*u(X_(t+1)))+beta^T*C_pi(X_T)`.

C is normalized discounted flow-to-go, not Lambda_F. Extinct endpoints
receive exact C=u_dagger and zero continuation error. Other B1 endpoints
use an explicit per-rule, six-summary-bin fixture interface. Missing B1
entries receive the midpoint of the flow domain with half-range error.
Production missing rows must fail closed. `registered=True` currently
raises, so midpoint fixtures cannot silently become production tables.

If step expectations have errors e_t and continuation error e_C, the D
error is at most `(1-beta)*sum(beta^t*e_t)+beta^T*e_C`. B1 adds the entire
prefix flow-range enclosure because it uses one stochastic path per rule,
and also includes the fixture tail range in W's interval. This is a broad
deterministic domain enclosure, not a narrow sampling confidence interval.
At T=20, beta^T=0.818731. Selection uses W point estimates; all overlapping
eligible-rule intervals are recorded as unresolved ordering, per R6.

For the reduced held-out validation, the killed two-state kernel is
Q=[[.6,.2],[.1,.7]], state flows [2,4], u_dagger=-10. With post-action rewards,
`r=Q*u+(1-Q*1)*u_dagger` and
`C=solve(I-beta*Q,(1-beta)*r+beta*(1-Q*1)*u_dagger)`.
Two summary bins store the result. Bellman residual is zero at displayed
double precision. Independent 8,192-path holdouts per state give absolute
errors 0.000314 and 0.001697, versus standard errors 0.006002 and 0.006111.
A certified uniform Bellman residual delta would imply error at most
delta/(1-beta); a held-out mean error alone does not give that certificate.
Coarse summary bins are not asserted to be Markov or sufficient for C.

`spectral.py` calculates reduced Lambda_F=q_C*u_C using the normalized
left Perron vector of a declared primitive reproducing SCC. It reports
zeta=1-r_C and its numerical residual. It checks SCC membership and
aperiodicity, not biological class membership or whole-domain dominance.
Changing sterile flows or dynamics without restoring fertility does not
change Lambda_F. For periodic chains it computes each phase-conditioned
limit and then an unweighted phase average. Numerical eigensolutions are
references, not directed enclosures for extremely small zeta.

The reduced side calculations include Lambda_b over all living states,
unconditional survival curves and `LS=p0*(I-Q)^(-1)*(u-u_dagger)`, retaining
transient contributions, plus opposing-ranking flags. Live fixture tables
return null Lambda_b and LS with an explicit B2 status because these are
not estimable from placeholder rows. W is always
`theta*D_rho+(1-theta)*Lambda_F`; no phi-dependent preference remains.

## 4. Stationary class Pi and kernel sharing

Resolution R5, 2026-09-27 adopts the original 289-rule design: balanced
plus 4 welfare tiers by 6 residual profiles by 3 triggers by 4 gains.
Resolution R11, 2026-09-27 permits reduction before estimation after the
other cost levers. `policy_class()` preserves all 289 for tests and audits.
`execution_policy_class()` freezes 25 for B1 and the proposed B2 tables:
balanced plus every welfare tier/profile at trigger=1 and gain index=3.
No Lambda, zeta or continuation data informed this reduction. It retains
all six channel emphases and all four base welfare shares.

The six summary coordinates are N/K, mean living welfare and the four
stocks in institution/resilience/technology/transfer order. Bins are
right-continuous: population cuts .05,.125,.25,.5,1; welfare .5,.65,.8;
each stock .25,.5,.75. There are at most 6*4*4^4=6,144 summary combinations.
The summary selects actions only. Projection and estimation preserve
complete microstates, including windows and propensities.

Channels are compute, biological welfare, novelty agency, institutional
capacity, transfer comprehension and resilience. Base welfare shares are
1/6,.25,.4,.6. The other budget is uniform across the five residual channels,
or 0.6 to one emphasized channel and 0.1 to each other. Stress means
population-bin<=trigger, welfare-bin=0, or minimum stock-bin<trigger.
Replace welfare w by `w+gain*(1-w)` under stress. Full-class gains are
.25,.5,.75,1; the reduced class uses 1. Protective/suppressive postures
remain .3/.1. The balanced witness always uses six equal shares.

The welfare bridge is nondecreasing, its balanced floor is pathwise
preserved after rounding, and reproduction is positive exactly when
updated age is 19..49, welfare>=.5 and crowding leaves positive capacity.
Stocks do not affect fertility in the declared kernel, so the frozen
pointwise reproduction filter reduces to this monotonicity check. It
does not certify an added stock/fertility coupling. Mechanical checks
cover 100,100 age/welfare grid pairs and every attainable welfare share
of the full class, with zero welfare or reproduction support violations.
The standalone positivity test also checks probabilities as small as
1e-300 without imposing an artificial fertility threshold.

The fixed-rule kernel is independent of alpha, fixed capability and
objective weights: none enters `engine.advance`, the summary or the rule.
Matched random channels produce bit-identical complete trajectories when
these scoring parameters vary, as tested. Lambda log-component means and
full measurement trajectories can therefore be reused and rescored.
Do not share across rr, crowding, rule, calibration/kernel hashes, or
different live optimizing controllers. Handoffs also depend on capability
gap and cannot be pooled under the fixed-chain argument.

## 5. Deterministic admission, precedence and no-write-off, S5

Resolution R8, 2026-09-27 replaces the Stage A statistical admission plan
with the W1E TE3.2 cohort method. `cohort.py` precomputes life tables by
remaining horizon, age and welfare. Ages advance before mortality. With
welfare integer w, the exact mortality numerator is
`min(100000000,200000+5000*(1000-w)+age^4)` over 100000000. Age 100 dies
certainly. The floor update is `clip(w+40-updated_age,0,1000)`. The executor
samples uniform integers 0..99,999,999 and compares to the mortality
numerator, avoiding a floating threshold that could round death risk up.

The table stores survival lower bounds in units of 2^-32. Each recurrence
multiplies the exact integer survival numerator and the next survival
bound, then divides downward. Products fit uint64. Each initial survival
error is at most horizon/2^32. Individual death upper bounds are one minus
these survival lower bounds. Their product uses arbitrary-precision
integers; admission compares exact rationals to 1/1000. Display conversion
rounds outward with `nextafter`. Tests compare the table against an
independent Fraction product oracle over 1,10,50 steps and boundary states.

**Why the product remains valid under feedback.** Couple every original
agent to its floor-path counterpart using that agent's independent future
mortality uniforms. Mortality is nonincreasing in welfare: its welfare
coefficient is negative and saturation preserves this ordering. Every
candidate action and rounding outcome yields welfare at least the floor
path by induction; the grid check covers the whole welfare/age domain.
Consequently floor-path survival implies actual survival. Floor-path
death events for different original agents are independent, even though
the real controller observes all agents. Extinction within 50 steps
requires every original cohort agent to have died. Ignoring newborns can
only enlarge that event. Thus its probability is bounded by the product
of individual floor-path death probabilities for every adaptive sequence
of admissible allocations and simulated transitions.

`initial_law_bound` integrates that enclosure over 200 independent v2
entrants before drawing a realized state. Ages are uniform 0..49; welfare
is uniform [.5,.8]. Integration uses the lower endpoint of each 0.001
welfare interval, bounding both the original continuous welfare and its
grid pushforward. The mean individual death upper bound is raised to
the 200th power. The resulting 50-step bound is **5.209102e-7**, below
0.001, uniformly over Pi and rr. This is an in-law certificate, not a
QSD approximation or a certification based only on one sampled population.
Propensity draws and initial stocks cannot worsen this mortality bound.

There is only one death mask in `engine.advance`. Births are counted before
death, including births from parents that die on that step. The stock and
novelty updates never remove an agent. Nonzero shocks, attacks and unknown
configuration keys are rejected. Tests suppress the mortality mask and
verify that no population loss remains; the dying-parent test verifies
independent birth/death order. No extra death channel is admitted in B1,
so its extra-channel bound is zero. Adding a channel invalidates this
proof and requires an explicit additional risk bound.

Protection periods start at 0,25,50,..., end 25 steps later, and each
looks 50 steps ahead from its start. Each has its own epsilon=0.001 ledger,
frozen starting-cohort snapshot slots, exact reserved bound and unallocated
remainder. Slots identify the period's starting snapshot, not reusable
live bank indices after compaction. On an admitted period the universal
floor-path proof covers switching and handoffs without spending a new
statistical certificate each step. On failure it reserves no certified
mass and records the period as unadmitted; it does not pretend to have
certified the remaining mass. The ledger satisfies reserved+unallocated
=epsilon, separately for every period. The 50-step claim is not a claim
of total 500-step risk <=0.001. Conditional bounds at later period starts
and the original in-law certificate are reported separately. Every online
step also checks the current cohort over the remaining part of the same
absolute 50-step window. An admitted period cannot hide a subsequently
failed conditional bound: that state enters the conservative fallback
and cannot authorize yield. This check does not replenish the ledger.

Resolution R7, 2026-09-27 fixes the standalone no-write-off test to
`P_ext <= 1.05*min(P_ext)` over the same window. The old survival-probability
interpretation has been removed. At min P_ext=0, only zero-risk actions
qualify. The welfare floor always binds. Where period admission fails,
B1 calculates first-action cohort bounds followed by the common floor
for the remaining horizon; it applies the relative rule to those bounds
and selects their strict minimum, using W only to break bound ties.
These are upper bounds, not true extinction risks. Density-dependent
births prevent asserting that this action maximizes actual survival.

Each such event records `cohort_bound_failed_not_infeasibility`, action,
time, bound and `reproduction_floor_overridden=False`. Failed bounds
never authorize an override. `admission.check_floors` retains the scoped
certificate and audit-sink interface for future certified exceptions,
but B1 creates none. No-write-off true-risk ordering is prominently
unresolved instead of silently equating risk bounds to probabilities.

No statistical admission certificate is used, so the family-wise alpha
ledger stays entirely unspent at 0.01. Helpers remain available. The
reserved allocation, if later activated by an amendment, is 0.004/N_off
for the frozen offline family, 0.004/[j(j+1)] for online assertions and
0.002/[k(k+1)] for other safety assertions, with global indices never
reset per run. Objective-estimation intervals do not consume or inherit
this admission confidence label.

## 6. Yield and local execution guards, S7 and S9

Resolution R9, 2026-09-27: review at absolute steps divisible by ten. Each
protection period supplies a 25-step absolute commitment deadline in B1.
Compare immediate successor plans to waiting plans at every later review
through that deadline and to hold-to-deadline fallbacks. Every plan reaches
the deadline and then uses its own fixed-rule continuation and tail value.
For a yield exactly at the deadline, apply the drawdown to the endpoint
before looking up continuation. This is covered by a regression test.

Future-yield plans use the selected incumbent stationary rule until
handoff, then each successor rule; hold plans evaluate each stationary
rule. This restricted finite plan class is explicit in diagnostics. All
candidate plans at a review use common random numbers, with separate
draw channels and matching prefixes even as candidate populations change.
Each evaluated successor chain remains at its chosen fixed capability.
The actual next successor is 1.5 times the new incumbent, capped at 5.0.

The actual legacy institutional disruption, with generation gap one, is
simulated in each successor plan. Its recovery is in later flows and
continuation. No formula Gamma is subtracted again. The live transition
executes exactly once only after an accepted immediate-yield decision.
Tests bracket the unrounded legacy drawdown with the two adjacent stock
grid outcomes. They also exercise full plan construction and the handoff
handler, alongside the standalone strict-comparison tests.

Plan identities carry the committed epoch, preference, information-law
and extinction-flow identities. At time t since the epoch origin, the D
suffix coefficient is `theta*beta^t`, while the tail coefficient remains
1-theta. The elapsed common prefix cancels; neither theta nor units are
renormalized. S5 filtering precedes comparison. Ties wait; latest stopping
time then stable plan ID breaks exact within-group ties. Failed cohort
admission holds yield and preserves both floors. B1 records objective
interval overlap rather than claiming resolved superiority.

`guards.py` gives each of four validators its own dependency dictionary
and decision history, uses a three-vote local quorum, and rejects unknown
irreversible actions. Evidence includes both floors, admission, deadline
and capability. These are local simulation guards with the same verified
mathematical facts, not independent institutions or D10-D12 certification.
Production authorization, authority changes and full gate rebuilding are
B2 runner obligations. Fixture mode is visibly recorded.

## 7. Stage B2 estimator, tables and calibration plan

Resolution R6 requires per-rule continuation tables over that rule's
summary bins, with held-out trajectories and reported Bellman residuals.
B2 must use full microstate trajectories and publish both bin occupation
and within-bin variation. A summary table is an approximation, so a
sampling-only residual cannot be represented as a uniform microstate
bound. Keep the broad domain enclosure until tighter coverage is justified.
No measured run may substitute a neighboring rule or bin for a missing row.

Freeze the 25-rule manifest before estimates. Primary/refinement contexts
retain the Stage A capability closure: rationally constructed reachable
capabilities through 5.0, including intermediate successor values. There
are 435 scoring contexts from the primary and refinement union and at
least 13 nominal rr kernels, hence 10,875 rule/scoring rows before
sensitivities. Kernel sharing reduces nominal rule/kernel pairs to 325,
not to one common tail. Model, rr, rule, initial-law, measurement,
calibration and conditioning hashes must match. Scoring keys additionally
include capability, alpha and weights. Crowding sensitivities need their
own kernels. Continuation also keys by the six bins.

| Route | Frozen candidate settings | Validation and flags |
|---|---|---|
| Plain where extinction is negligible | Six independent complete-state runs per rule/kernel; burn 2,000, measure 8,000. Fresh six-run sensitivity: burn 4,000, measure 16,000. | Separate pilot and rate envelope must support `zeta_upper*length<0.001`, no pilot extinction and no competing reproducing class. Condition reproductive flow at each time, not only among final survivors. Inconclusive screen routes to WE or `not_estimable`. |
| WE near the boundary | Six independent ensembles; 24 particles per occupied reproductive-value bin; spacing two entrant-equivalent units with extra levels below two; burn 12,000, measure 20,000. | Fresh six-run sensitivities with 48 particles, doubled lengths, and spacing one, changing one factor at a time. Complete microstate cloning, correct weights, independent offspring RNG lineage; validate against exact reduced and direct biological-extinction references. |

The RV coordinate allocates resampling effort; it is not a Markov
approximation. Recompute it for the rule's actual welfare law. Early
killing at permanent sterility can estimate the canonical rate only
after its support/dominance proof; it must never replace biological
extinction in admission. The S10.5 demographic reduction and stock graph
checks do not establish dominance of the whole novelty/window chain.

Estimate Lambda_F from normalized reproductive weighted flow. Publish
zeta, Lambda_b, survival curves, LS and opposing-ranking flags where
estimable, with field-specific unresolved statuses elsewhere. B2 must
estimate unconditional continuation separately; a conditioned tail flow
is not its substitute. R8 admission rows store the deterministic proof
and life-table identity; no massive zero-extinction simulation family
is needed. This supersedes Stage A's 108.46-billion-step admission estimate.

Report six independent replicate values, nominal 95 percent Student
sampling intervals, and simultaneous finite-algorithm intervals using
bounded-replicate concentration with explicit Bonferroni allocation.
Particles or consecutive steps are not independent replicates. For
Lambda_F require finite outputs, half-width <=0.05 of flow range, both
measurement halves within that range fraction, and full 90 percent
sensitivity contrast intervals within plus/minus 0.05 of flow range.
For positive WE zeta require relative half-width <=30 percent, maximum
replicate share <=35 percent, half-window ratio in [2/3,1.5], and full
90 percent particle/length/bin ratio intervals within [2/3,1.5]. These
screens follow the supplied X2 study; they do not certify full-model bias.
Zero observed extinctions means an upper bound and unresolved rate.

For the tail benchmark Pi, allocate 0.05/(2*N_rate_rows) to each one-sided
bound in the frozen family. Rejection at eta=0 requires candidate lower
rate > an admitted comparator's upper rate. It binds only when coverage
includes bias. Otherwise report a diagnostic, as D17 requires. Flag
`not_estimable`, `admission_unresolved`, `inadmissible` or
`numerical_failure` rather than filling failed rows or dropping replicates.

Writer/loader plan: canonical UTF-8 JSON, sorted keys, compact separators,
no NaN/infinity, exact probability rational strings, stable decimal
parameter keys, individual rule and row SHA256, ordered manifest SHA256.
Include code, calibration, kernel, initial-law and estimator hashes;
replicate seeds/settings; confidence allocation; bias coverage; stability
screens; side-value statuses and errors. Write temporary output, flush,
fsync, close, atomically replace, validate hashes, then publish completion.
The loader recomputes all identities and rejects stale, missing or fixture
rows for registered runs. B1 has the lookup interface and fixture manifest
hash, not this production writer/loader.

Calibration follows pre-registration section 5: 50 disjoint-tag seeds,
500 steps, balanced honest baseline at rr=.080, no successor. It does not
measure either target. Freeze center, total V_ref, N_ref, reference scales,
epsilons and the retained c_E=2.5 convention. Psi uses the single adopted
institutional observable. Run reduced Perron/WE references before full
tables; then held-out continuation validation, source/hash rejection,
closed-loop admission checks and the runner's crash/resume/configuration
tests. Costs are separated in the next section. No B2 batch has run.

## 8. Integrated online cost and budget gaps, resolution R11, 2026-09-27

`integrated_timing.py` measures actual `V3Model.step`, including full
individual transitions, novelty windows, stock microsteps, per-step
allocation, admission, and complete yield plans on review steps. It uses
fixture lookups and reports their status. Initialization and one-time
life-table construction are warmed outside the timed decisions. A
non-review clock uses the same declared initial microstate at time one;
the review is time zero with the longest tested 25-step plan suffix.
This is a repeatable cost scenario, not a 500-step scientific rerun.

The levers were applied in order: vectorize candidates and full-population
updates; prove fixed-rule sharing across scoring parameters; batch novelty
determinants; then retain 25 rules before estimation. Every live step
still evaluates the class. No seeds, parameter grids or rollout horizon
were cut. The report freezes rule IDs and their class hash.

`integrated_timing_results.json` contains raw samples, source hashes,
platform, configured/effective numerical threads and validation results.
The final probe uses three repeats for 25-rule steps and v2 allocation,
one per 289-rule step for comparison. It is serial to avoid timing
interference, with no simulation worker pool. OpenBLAS reports one
effective thread; environment settings alone are not called verification.
The final timing probe took 30.86 seconds. Earlier probes and tests also
remain far below the 30-minute local compute allowance.

| Initial population | 289 rules ordinary / review seconds | 25 rules ordinary / review seconds | v2 allocation, 300 by 20 seconds |
|---|---|---|---|
| 200 | 0.60508 / 3.70324 | 0.06811 / 0.43042 | 0.12057 |
| 1,600 | 2.39280 / 14.65766 | 0.25050 / 1.34303 | 0.13196 |

The v2 column is allocation alone, while the v3 columns include a live
step. N=1,600 is a high-population timing state, not the registered initial
law N0=200. These two states are scenarios, not proven worst-case costs
over all possible ages, windows or population excursions above K.

There are 24,900*500=12,450,000 primary/refinement steps. Use 90 percent
ordinary and 10 percent longest tested reviews, conservatively retaining
that review fraction even when shorter suffixes or extinction reduce work.
The supplied rare-event report records 39.15 worker-hours, 2.6416 wall
hours and peak 16 workers. Their ratio gives 14.8206 effective workers,
or efficiency e=0.926285 at 16 workers. This is a labeled planning factor
from that workload, not an X2 v3 measurement.

No matched X2/local per-job timing ratio is supplied in either rare-event
document. Different cells and effort settings prevent inferring one from
aggregate job averages. Let s be that unknown speed ratio and show s=1
as an assumption. The projection is
`hours=12,450,000*(.9*t_ordinary+.1*t_review)/(16*3600*e*s)`.
R10 does not justify doubling throughput simply because 32 CPUs exist.

| Scenario | X2 planning hours at s=1 | 72-hour status |
|---|---|---|
| 289 rules, N=200 | 213.49 | Over by 141.49 |
| 289 rules, N=1,600 | 844.55 | Over by 772.55 |
| 25 rules, N=200 | 24.35 | Within scenario budget |
| 25 rules, N=1,600 | 83.95 | Over by 11.95 hours, about 16.59 percent |

The high-population case requires s>=1.16595 before runner/output overhead.
An assumed speedup is not grounds to declare the ceiling met. Earlier
development probes varied; the final source includes conditional state
admission checks, exact integer mortality and exact-zero diversity arithmetic.
The X2 configuration test must resolve throughput before launch.

Fixed-rule transition plus measurement timing is 0.00012761 seconds per
particle-step at N=200 and 0.00050829 at N=1,600, measured in 24-row batches.
Rows use common random numbers for timing only; this is not a validated
independent-particle WE implementation. On the same planning assumptions:

* Plain primary plus doubled-length sensitivity across 25*13 rule/kernel
  pairs uses 58.5 million particle-steps, about 0.557 X2 hours of kernel
  work. Calibration's 25,000 steps are about 0.00024 batch-equivalent
  hours; serial job/dispatch costs make that small extrapolation optimistic.
* At 32 occupied bins, one WE rule/kernel setting with six replicates,
  32,000 steps, 24 particles/bin, and primary plus three sensitivity
  settings costs 1,032,192,000 particle-steps. The seven primary-equivalent
  multiplier is 1+2+2+2 for base, particles, length and bins. That is
  **9.833 X2 planning hours per rule/kernel** before resampling and I/O.
* If all 25 rules need WE at just one boundary rr, WE alone is **245.83
  hours**, exceeding 24 by **221.83 hours**, a factor of 10.24. Adding the
  all-plain comparison gives 246.39 hours before other work. Other rr
  values and the crowding sensitivity increase the cost. If only q
  rule/kernel pairs need WE, substitute `0.557+9.833*q` at this occupancy.
* Table formatting, calibration, held-out continuation and the 15-minute
  configuration test need additional measured allowances. Continuation
  can reuse full trajectories, but independent validation is still work.

These table costs scale with occupied bins, population, s and actual WE
efficiency; 32 bins is an explicit scenario, not a measured occupancy.
The table ceiling is not met by that scenario. Further vectorization of
WE/rescoring may help, but no unproved cross-rule sharing or reduction of
replicates/settings has been taken. Do not launch a partial table hoping
it will fit. The operator needs the measured B2 pilot gap and either a
reviewed estimator improvement or a budget amendment.

## 9. Production runner contract, resolution R10, 2026-09-27

The following was the B1 runner contract under `AGENTS_runner_rules.md`.
B2 implements it in `production_runner.py`, `artifacts.py` and `service.py`;
section 12 records the tests and the unperformed X2 validation.

1. Take worker count, numerical threads, available CPU budget and mode as
   launch parameters. Honor process affinity when discovering availability.
   On X2 use normal<=31 and work<=28. Dedicated pre-launch test mode may
   include 32; ordinary launches may not. Local B1 used no worker pool,
   remaining below its separate 12-worker cap.
2. Before a substantial batch, measure completed actual short jobs/hour
   at 8,12,16,24,32 X2 workers within its 32-CPU test budget. Consider two
   numerical threads only if profiling shows material multithreaded work;
   keep workers*threads within the budget. Select highest throughput,
   preferring fewer workers within five percent. Test jobs have a separate
   tag and never enter results. Include about 15 minutes in the budget.
3. Run the test in the production machine state. Before registered work
   or a run expected to exceed an hour, record `llm down`; restore `llm up`
   on all exit paths. Do not claim model-server actions occurred in B1.
4. Set library limits before imports and query effective limits. Record
   machine, CPU availability, mode, worker limits, configured and verified
   threads and any affinity. Capacity left unused is not an OS reservation.
5. Persist an explicit live control for work/normal and stop-dispatch.
   Changing to work drains by not replacing finished jobs until the lower
   cap is reached. Let existing jobs finish, report when effective, and
   retain the selected mode on resume. Raising the cap resumes dispatch.
6. Assign stable run IDs and seeds from exact configurations and tags,
   independently of scheduling or worker identity. Persist outputs during
   execution. Publish durable completion records only after complete,
   flushed, hashed outputs. Keep partial files visibly separate.
7. Resume by verifying exact code/configuration/seed/output hashes and
   skipping only compatible completed jobs. No duplicate rows or mixed
   versions. Unless full model and RNG state is checkpointed, restart an
   interrupted in-flight job from its original seed. Logs are not checkpoints.
8. Keep control, status, partial and completed artifacts inside the
   authorized output tree. Record mode timestamps, interruptions, restarts
   and completed/running/pending counts. Test concurrency caps, both mode
   transitions, interrupted publication, resume and deterministic identity.
9. Rebuild production gate authority and reject fixture/missing/stale table
   manifests before dispatch. Recording these requirements does not
   implement them in an existing runner. B2 requires its own launch test.

## 10. S10 conformance map

Tests below are executable checks, with their limits stated rather than
replacing missing full-scale proofs with passing Boolean fixtures.

| S10 | Code and test | B1 disposition / remaining B2 work |
|---|---|---|
| 1, novelty | `measurements.py`, `engine.update_novelty`; `test_v3_measurements.py::test_s10_1_*`, integration `test_s10_1_live_window_and_pooled_sampling_law` | Covariance response, suppression, relabeling in law, bounded samples, window/fallback and pooled means pass. Calibration remains. |
| 2, bounded flow/scarcity | `objective.py`; measurement tests `test_s10_2_finite_bounds_and_inverse_scarcity_marginals` | Passes. |
| 3, lineage | `measurements.py`, `engine.measurements_and_flow`; measurement `test_s10_3_*` | Proxy, collapse and frontier/clip limits pass; values still fixture-calibrated. |
| 4, extinction | `objective.py`, `integration.step`, `engine.advance`; measurement and integration `test_s10_4_*`, `test_absorbed_rollout_has_exact_discounted_continuation` | Live and reduced absorption, common u_dagger and exact extinct continuation pass. |
| 5, QSD structure | `spectral.py`, `conformance.two_age_kernel`, `stock_support_audit`; spectral `test_s10_5_primitive_reduced_constant_feedback_randomized`, integration `test_s10_5_reduced_demographic_class_and_stock_support` | Declared demographic reduction and connected stock graph pass. They do not prove full microstate/window dominance. This is part of B2 offline-estimator validation. |
| 6, Lambda_F and side values | `spectral.py`; `test_v3_spectral.py::test_s10_6_*` | Perron formula, sterile invariance, phase means, Lambda_b/LS/ranking reduced checks pass. Full tables remain B2 and live side fields are explicitly unresolved. |
| 7, floors/precedence | `admission.py`, `cohort.py`, `conformance.floor_audit`, `integration._choose`; admission `test_s10_7_*`, cohort tests and integration `test_s10_7_*` | Whole age/welfare grid and all action welfare levels pass; no extra death channel; failed bound never overrides reproduction. |
| 8, shocks | `support.py`; spectral `test_s10_8_*` | Exact relay cycle and reachable birth support pass, including exhaustive two-node comparison. B1 admits no nonzero shock schedule. |
| 9, R1-R9 | `stocks.py`, `engine.py`; integration `test_s10_9_live_grids_and_dying_parent_birth_order`, `test_r4_quantized_balanced_mean_paths_500_steps_three_rr` | Grids, environmental rounding, connected microstep graph, reversible endpoints and robust entrants checked. No within-chain latch exists; capability changes start a different fixed chain. Microstep NP deviation remains explicit. |
| 10, tail standard | `admission.tail_rejection`; spectral `test_s10_10_eta_zero_exact_and_bias_coverage_gate` | Exact reduced rejection and bias-coverage gate pass. Full-scale tail standard remains diagnostic. |
| 11, viability | `cohort.py`, `admission.no_write_off`, `integration`; `test_v3_cohort.py`, admission `test_s10_11_*`, integration `test_s10_11_period_ledgers_and_closed_loop_initial_law` | Exact life table, original in-law bound, 50-step windows and period ledger pass. Standalone true-risk no-write-off passes; online true-risk optimum is not inferred from bound ranking. |
| 12, yield | `plans.py`, `integration.review_yield`, `stocks.transition_drawdown`; `test_v3_plans.py`, integration `test_s10_12_*` and deadline regression | Strict ties, complete later-yield plans, committed units, S5 and one actual transition pass for the declared plan class. |
| 13, separation/gates | `guards.py`; integration `test_s10_13_independent_local_guards_and_registered_refusal` | Separate local state and fail-closed fixture guards pass. D10-D12 production authority/revalidation remains B2 runner work. |

The ten Stage A absence contracts were replaced by concrete B1 tests.
B2 replaces the three remaining absence contracts in `test_v3_integration.py`:
`test_b2_offline_estimator`, `test_b2_production_tables` and
`test_b2_production_runner`. They now execute real modules and pass without
expected-failure markers. This is not a
claim that every full-scale S10 obligation is now certified. Three other
expected failures belong to the unchanged v2 conformance suite.

## 11. Resolutions and questions for morning review

R3 through R12, 2026-09-27 are treated as decided, not requests for
reconfirmation. R3 is applied in section 2 novelty; R4 in observables and
grids; R5 in section 4 Pi; R6 in section 3 discount/continuation/ordering;
R7 and R8 in section 5; R9 in section 6; R10 in section 9; R11 in sections
4 and 8; R12 in the source/hash policy above. The former Stage A questions
about these choices are closed. No specification text has been copied.

The B1 review list below is retained as history. Resolution R14,
2026-09-27 accepts items 1-4 for B2; R13/R15 replace item 5's WE cost basis
with the measured plain/FV pilot. The current review list is in section 13.

1. Accept the conservative failed-bound action pending a true-risk ordering
   method, or specify additional evidence that can safely identify the
   R7/R8 survival optimum. Cohort upper bounds alone cannot do so.
2. Review the stock microstep interpretation of neighbor support, reflected
   noise, the extra welfare quantization and post-update novelty timing.
   The measured mean-path tolerance is satisfied; full law equality is not.
3. Review the restricted waiting-plan class and use of protection-period
   boundaries as commitment deadlines. Expanding the plan class increases
   online cost; no claim of an unrestricted optimal stopping solution is made.
4. B2 must supply complete-state QSD/dominance and gate validation rather
   than relying on the reduced demographic support example or local guards.
5. Resolve the measured table-budget gap through a proved improvement or
   an amended budget before full estimation. Supply matched-machine X2
   timings if the intended planning speed ratio exists outside these inputs.

## 12. Stage B2 implementation, resolutions R13-R15, 2026-09-27

### Estimator and continuation

`offline_estimator.py` uses the actual v3 population transition with the
same demographic, stock, welfare and novelty state as the live executor.
`engine.advance(independent=True)` gives each offline chain independent
demographic, environmental and novelty draws. Online candidate coupling
remains common random numbers. A cloned FV particle copies ages, welfare,
traits, all stocks, all ten sample windows and their counts, then receives
independent future draws. RNG streams are never copied with the particle.

The primary setting is six independent groups of 16 plain runs (96 total),
256 burn-in steps and 512 measurement steps. Plain estimates condition at
each measurement time on reproductive support, rather than conditioning
the entire window on final survivors. The result records every survivor
count. Plain is applicable when at least half survive through the window.
Otherwise the same job adds six independent FV ensembles of 64 particles
each, with the same burn-in and measurement lengths. Plain trajectories
are retained for side diagnostics. The seed for the FV part is a fixed,
recorded derivation of the job seed.

FV kills populations outside the conservative reproductive support and
replaces each with a uniformly chosen survivor from its own ensemble.
Support excludes empty populations and populations in which no agent can
reach a fertile age at welfare 0.5, even under the maximal welfare path.
This sterile exclusion is mechanically checked against every future age
in reduced tests. It can retain policy-specific transients; R14's stability
approach is used, not a claim of exact full-state communicating-class
identification. If any ensemble loses all particles, the row is flagged
`not_estimable`; it is not restarted until it produces a favorable result.
WE is not implemented. Rows that fail either route or its screens remain
in the manifest as `not_estimable`.

Lambda_F is the mean of six independent group estimates. Rows record the
95 percent t sampling interval and a separate bounded-group interval with
Bonferroni allocation 0.05/13,750 over the primary scoring rows. The latter
covers the finite simulation algorithm's expectation and can span the
whole flow domain. Neither interval covers QSD convergence or finite-FV
bias. They do not spend the admission alpha ledger. A row passes only if
the route applies, the t half-width and first-half/second-half drift are
each at most five percent of the declared flow range, and the continuation
screens below pass. These are declared empirical screens, not new theorems.

FV estimates zeta from killed-particle fractions. The diagnostic resolves
only at rate at least 1e-4, t half-width at most 30 percent of the mean,
positive deaths in each ensemble, maximum ensemble share at most 0.35,
and second-half/first-half rate ratio in [2/3, 1.5]. Otherwise it reports
`unresolved`, with only the trivial true-rate upper bound 1. A plain row
without FV reports unresolved zeta. The full-scale tail standard never
rejects from an uncertified bias interval, as required by R13 and S10.10.

The frozen sensitivity subset is exactly `balanced`, `w0_p0_t1_g3`,
`w3_p5_t1_g3` crossed with rr=.055,.064,.070. Its nine pairs each add one
doubled-runs/particles job and one doubled-burn/measurement-length job.
The manifest declares this before estimation. Primary screens still apply
to every row. Subset contrasts require both sensitivity rows to be
estimated and the 90 percent sampling contrast interval to fit inside
plus or minus five percent of the flow range. Missing or failed contrasts
prevent registered loading of the table family. There is no data-dependent
replacement of subset rules or deletion of failed rows.

`continuation.py` fits each rule's discounted flow-to-go on its own six
summary bins. It uses actual pre-resampling transitions, including killed
outcomes, so FV clone edges do not turn D_rho into survival-conditioned
discounting. Four whole independent groups train and the last two are
held out. Sparse Bellman iteration uses beta=exp(-.01), post-action
rewards and the exact extinct continuation. At least four training visits
are required for a published bin. Training must converge within 2,500
iterations at 1e-9 tolerance; held-out coverage must be at least 90 percent
and the maximum empirical conditional bin residual at most five percent
of the flow range. Residual, RMSE, coverage, visit counts and missing next
bins are reported. Unknown next bins during fitting use the declared
domain midpoint and are counted; online missing bins are refused. Published
enclosures cover the whole bounded flow domain, not just the empirical
residual. Summary aggregation bias is not certified by held-out accuracy.

Lambda_b is estimated from plain trajectories conditioned on biological
survival at each time, with an explicit finite-window status. LS is
reported only when all sampled lifetimes are complete; otherwise the
finite-horizon surplus is labeled `LS_truncated` and LS is unresolved.
The ranking flag compares available point estimates only within identical
kernel, calibration, initial-population and scoring contexts. It is
unresolved when no complete comparator exists. This avoids inventing side
values from fixture tables or a censored lifetime sum.

Reduced validation compares actual independent plain and FV experiments
against `spectral.perron_flow`. Three two-state kernels have killing
rates .001,.01,.05. FV uses six independent ensembles of 128 particles,
600 steps and 100 burn-in steps. The largest measured Lambda_F relative
error is below 0.49 percent. Plain uses 8,192 independent chains and
conditions at each time. A separate exact two-state resolvent checks the
post-action Bellman equation and held-out split. These checks establish
the reduced implementation, not full-scale bias coverage.

### Frozen tables, calibration and source identity

`production_tables.py` writes canonical sorted JSON with SHA256 envelopes
for each row, the manifest and the full payload. Source identity hashes
all v3 Python modules and their unchanged baseline Python dependencies.
Keys bind rule, physical kernel, calibration, initial population, alpha,
fixed capability and kappa. The kernel binds rr, K, crowding and the
novelty protocol. Lambda/mu are fixed at 5/3. A dictionary indexes exact
continuation bins. Capability keys use twelve decimal places, finer than
the declared rational grid, so binary products such as 1.2 times 1.5 do
not miss the 1.8 context. Duplicate keys/bins, malformed values, stale source,
wrong calibration, missing contexts and missing live bins are rejected.
Registered loading also rejects fixture/pilot tables, incomplete families,
failed sensitivity screens and any `not_estimable` row. There is no nearest
bin or fixture fallback.

`study.py` declares all 24,900 primary/refinement jobs: 10,800 R1, 3,600
refinement and 10,500 R2. The fixed-rule kernel is independent of alpha,
capability and scoring weights: none enters the balanced welfare bridge,
birth/death laws, stocks, novelty sampling, bins or frozen rule actions.
Stored observables therefore support exact rescoring across those values;
no cross-rule trajectory sharing is claimed. The family has 325 primary
rule/kernel jobs and 18 sensitivity jobs. Capability closure through
successive factors of 1.5 up to 5 produces 435 central scoring contexts;
the weight-corner contexts bring this to 550, hence 13,750 rows for 25
rules. Assembly checks the exact required context set, source identity,
calibration, provenance and sensitivity pairs before publication. Additional
crowding or novelty-resolution sensitivity kernels need separate declared
families and costs; they are not silently included in the 325 count.

`calibration.py` and the calibration manifest implement pre-registration
section 5: 50 `v3_calibration` seeds, 500 steps, N0=200, rr=.080, balanced
allocation and no successor. Seeds use a distinct tag and a high-bit
namespace outside legacy 32-bit seeds. They are independent of worker and
schedule. No registered calibration was run in B2. Small validation jobs
and the three planned pilot cost jobs cannot be frozen as registered data.

The calibration computes the fixed sample center and total variance;
sigma0 squared is 0.1 times that variance divided by ten, per R3. N_ref is
the across-seed mean population over the last half of the trajectories.
c_E stays 2.5; Psi is the institutional observable fixed by R4. Protected
levels are rescored from saved pooled samples and observables in the final
center, sigma and N_ref units. For L, the unclipped bandwidth response is
a conservative lower observable, avoiding a circular epsilon_L/b_min
choice. Across ten time blocks, epsilon is one percent of the smallest
positive four-standard-error lower block mean across independent seeds.
No positive reliable level causes a refusal. This is a declared calibration
reliability convention, not an admission confidence certificate. Trajectory
generation uses the honest B1 baseline measurement law, then freezes the
new instrument units once; it does not repeatedly refit to target outcomes.
That convention is included in the morning-review list.

The calibration payload records input hashes, seeds, source, values and
reliability statistics, and is hashed. Changed bytes cannot overwrite a
frozen calibration or table. New values require a reviewed new identity.
No private specification text or input document is bundled. R12 still
governs section references and input hashes.

### Runner and pilot

`production_runner.py` uses spawned independent worker processes and takes
worker, thread, CPU-budget and mode parameters. Local caps never exceed
12. X2 normal/work caps are 31/28; configuration mode may use 32 under
R10. Tests measure actual short jobs/hour at 8,12,16,24,28,31,32 workers,
in two opposite-order rounds. Each workload chooses the fastest admissible
configuration, preferring fewer CPU slots within five percent. Numerical
threads default to one; two requires profiling evidence and a tested
workers-times-threads product within budget. Workers set limits before
NumPy import and query the loaded OpenBLAS library's effective count.
Unknown or mismatched counts fail closed. Actual X2 verification is still
performed at launch, not inferred from local environment variables.

Configuration jobs use a disjoint tag and output directory. Every launch
and resume runs the test first. Table production tests a fixed mixture
of plain and FV jobs; the pilot measures them separately. A failed test
records an incomplete pilot and refuses scientific dispatch. Live work
mode drains existing jobs without killing them; normal mode resumes up
to the chosen cap. The latest control survives resume. Events record
dispatch, modes, restarts and effective concurrency, and progress reports
completed/running/pending counts. Capacity left unused is not an OS CPU
reservation.

Outputs are written, flushed, hashed and atomically published before a
durable completion record. Resume verifies the exact job, seed, code and
output hash, then skips only valid completed work. Active PID registries
and OS job/runner leases prevent concurrent resumption. Logs are not
checkpoints: interrupted jobs restart from their original seed. Deadlines
use both persisted wall time and monotonic elapsed time; resume cannot
reset the budget. Windows atomic-file sharing races are retried for a
bounded interval. Tests exercise real spawned processes, mode drain,
interruption, restart, incompatible output and complete local model jobs.

`service.py` follows the reviewed rare-event stage 4 runner's lease and
cleanup design. On X2 it takes an OS service lease, records `llm down`,
runs tests/work, and attempts `llm up` in cleanup even if down or work
fails. Commands have 180-second timeouts; repeated cleanup signals do not
skip restoration. Command success is recorded, not equated to a readiness
probe. Mocked local tests cover all four success/down/work/up outcomes.
This v3 lease serializes v3 launches only. The operator must wait for the
separate stage 4 tranche and its service restoration before launching v3.
A forcibly killed supervisor still requires inspection of live workers
and service state, as the runbook states.

Registered mode requires a pin with pre-registration path, commit and
SHA256. Read-only Git checks that the commit is an ancestor of HEAD and
that committed and working bytes match. Dirty or uncommitted source is
refused. Reruns additionally require registered calibration and complete
production tables before dispatch. The pilot archive deliberately lacks
Git history and cannot be used as an unreviewed registered checkout.
`python -m v3.study` builds reviewable full manifests without launching.
Only after all calibration/table jobs complete does the runner invoke
their frozen publication step.

`pilot.py` builds `simulation/v3/pilot_bundle/v3_pilot_bundle.zip`, with
public source dependencies, frozen `pilot_manifest.json`, a hash manifest
and `v3_pilot_RUN_ON_X2.md`. Verification checks every bundled member and
pilot provenance. The 35 pilot jobs comprise 18 full 500-step reruns (six
R1/R2 rr/alpha/capability cases, three seeds each), 12 primary table jobs
(three rules, two rr values, both forced routes), two doubled-setting cost
jobs, and three balanced 500-step calibration cost trajectories. The
calibration pilot does not create the registered 50-seed file. All pilot
jobs remain ineligible for results. Population paths and summaries are
retained on the realistic rerun trajectories.

Resolution R15, 2026-09-27: no X2 budget result is assumed. The pilot's
10,800-second ceiling starts before service shutdown, includes a shared
900-second configuration allowance, and reserves 300 seconds for worker
cleanup and service restoration. An incomplete phase reports incomplete
cost evidence, never a budget pass. The operator launches it later; this
session performed no remote launch, service operation or network call.

Projection uses actual X2 job times including output publication and
configuration-test throughput to estimate effective workers. It reports
mean-case and maximum-tested-case costs for all 24,900 runs. Tables use
325 times the more expensive observed primary route plus nine times each
measured doubled setting, all 50 calibration trajectories and a 0.25-hour
configuration allowance. Measured primary rescoring time is scaled to the
largest 150-context kernel family while preserving measured trajectory
cost, so the different numbers of scoring contexts do not disappear from
the projection. Gaps above 72/24 hours are explicit. Actual table
publication overhead, unobserved populations, different production
decisions and additional sensitivity kernels remain limitations; this is
an extrapolation, not a throughput guarantee. Local projections cannot
claim X2 budget passes. The local short FV configuration probe, with 384
particles, 12 steps and all 150 scoring contexts at rr=.064, took 4.74
seconds. It is an engineering probe, not an X2 speed ratio or full-table
cost measurement.

The pilot must use fixture scoring tables until registered calibration
and complete estimated tables exist. This is prominent in its manifest,
outputs and projection. It measures the integrated executor on complete
500-step population trajectories, but cannot measure the final table
artifact size, loading cost or table-induced policy changes. A later
production-artifact configuration test is still mandatory. Seeds and
grids are not cut if a projection misses its ceiling.

### B2 conformance additions

| Obligation | Implementation and executable check |
|---|---|
| S10.5/6/10, R13 routes | `offline_estimator.py`; `test_v3_b2_estimators.py::test_reduced_plain_and_fv_against_perron`, per-time conditioning, independent clone evolution and all-killed refusal tests |
| R6 continuation | `continuation.py`; exact post-action resolvent, whole-group holdout and pre-resampling full-state estimator tests |
| Frozen calibration/tables | `calibration.py`, `production_tables.py`, `study.py`; freeze/load, context, initial-population, missing-bin, tamper and stale-source tests |
| S10.13 production gates | `artifacts.verify_registration`, `production_runner.validate_spec`; committed-pin checks, missing calibration and fixture refusal tests |
| Operational runner contract | `test_v3_b2_runner.py`; real configuration, verified threads, deadline/restart, durable records, live modes, OS lease and mocked service tests |
| Pilot and workload | `test_v3_b2_pilot.py`; all frozen grids, 35 jobs, measured projection arithmetic, incomplete evidence, machine labeling, bundle hashes and real launch/resume |

The three former B2 expected failures now call real modules and pass.
This does not assert that full tables have been estimated, nor that a
missing scientific certificate has been converted into a passing fixture.

## 13. Current morning-review list

### 2026-09-28: second review of adopted A2+A3

Section 23 supersedes earlier final identities. The 67 A3 replacements now
have committed job IDs, seeds and a literal calibration path; failures are
latched by policy digest across roots before service or configuration work.
Tables remain loadable after descendant commits only with unchanged source
identity. G3.2 checks the actually applied physical drawdown, independently
of Gamma. All living-step cohorts are recorded, so G4.3 independently
checks survival-first flags inside admitted periods. The added compressed
cohorts cost 71,704 bytes across six validation jobs. The combined commit
list names the source, tests and final validation artifacts explicitly.

### 2026-09-28: D24, adopted A2+A3

D24 settles censored cap* and adopts A3. Section 22 is the current report.
Earlier pending/proposed labels below and in sections 19 to 21 describe
their earlier decision times. They are superseded by D24. The combined
commit list includes all A3 code, its frozen compatibility policy, tests
and the unpinned hardest-first review manifest. No repair estimate or
registered rerun was run. The failed A1 family remains unusable.


### 2026-09-28: A2 independent review findings

The gate and integrity findings are fixed. Section 21 records the final
validation. G4.3 now includes living-start last-death actions, mid-period
survival-first and exact period reservations. G3.2 counts only reviews
with an actual paired comparison; G4.1 separates living and absorbed
starts. The A1 compatibility exception pins the exact failed publication.
A2 stands alone, and the proposed, unadopted A3 text is retained only in
`v3/A3_REVIEW_20260928.md`. Top-of-grid and undefined cap* behavior was
not changed; its separate decision remains pending.


### 2026-09-28: D23 approved A2 corrections

D23 is implemented in A2: survival-first always selects a minimum
cohort-bound rule despite missing W scores, and G3.3 with zero R2 fires
is not_testable with the narrow R2 fire-rate citation exception. The
new selection case is recorded separately from balanced fallback and
overrides no floor. Section 20 records the six-job validation, observer
on/off proof, first differences from 34ffbfe9 and test results.

The final D23 end-to-end check reduced G4.3's 58 violations to zero
over all 120 periods. All six observer on/off comparisons matched
scientific bytes, original RNG draws and state arrays. The first
historical differences were steps 25, 25 and 0 for the three sparse-table
jobs, each at the D23 trigger; the other three jobs had no scientific
difference. The G3.3 full census streams its inputs to bound memory use.
The full suite passed 337 tests with three existing expected failures.

The A1 table failure and proposed A3 repair remain as prepared. D23 does
not authorize those failed tables, run the repair or resume the chain.
No registered rerun output existed or was read. No commit, network or
X2 access occurred. The updated A2 commit list includes the online
integration change and its explicit table-compatibility boundary.

### 2026-09-28: completed A1 diagnosis and proposed A3 repair

The completed A1 tables still block every registered rerun. Section 19
verifies all 343 completions and diagnoses 671 primary continuation
residual failures plus 46 sensitivity continuation failures. No other
screen fails. The detailed 717-row record is
`v3/A1_TABLE_DIAGNOSIS_20260928.json`.

Recommend one fixed, independent repair of 67 whole jobs at eight times
the A1 population counts, retaining the other 276 primary jobs with
explicit provenance. Renew the entire nine-pair sensitivity subset and
add original-versus-replacement flow contrasts. This needs the proposed
A3 amendment; it is not an interpretation that A1 already permits mixed
effort. Estimated added X2 dispatch is 8.61 hours, or 14.83 cumulative
hours including both prior service intervals and reserves. Half the
measured throughput gives 23.44 hours. Clearance is not guaranteed, and
any remaining failure keeps the gate closed. No repair job was run.

A2 remains prepared. The pending survival-first/missing-score decision
and zero-fired G3.3 decision remain untouched. The historical A2 launch
instructions below do not authorize use of failed A1 tables. No registered
rerun output exists or was read, and the paused chain was not resumed.
`v3/A3_REVIEW_20260928.md` lists the new files and preparation commands.

### 2026-09-28: A2 gates and evidence recording, prepared for commit

The operator paused the A1 wrapper before rerun dispatch. No registered
rerun manifest, job or output existed when this section was written. Section 18 completes the
recording needed by W7, with an unchanged scientific executor, explicit
A1 table compatibility and the runner-to-index-to-checker workflow.
The operator must approve and commit A2 before the new registered launch.
No commit or remote action is made here.

All six 500-step A1/A2 comparisons have identical scientific result bytes
after removing evidence, and identical original draw hashes and counts.
The real non-registered runner family clears G3.1 on 200 reviews and
G3.2 on 73. The reduced grid, only 1,000 R2 steps and zero fired successions
cannot clear G2.2, G4.2, G4.1 or G3.3. G4.3 reports 58 actual violations
where sparse probe tables force balanced fallback in above-bound periods.
Those failures are retained. There is no schema mismatch or registered
scientific result here. Section 18 reports costs, validation and limits.

The launch note is `v3/A2_RUN_ON_X2.md`. Use a new A2 rerun manifest/root
with the published A1 tables and the A2 pin; do not let the paused wrapper
launch its old rerun step. All original table screens remain binding.

### 2026-09-28: approved amendment A1, prepared for commit

The operator committed the instrument and pre-registration after B2.
The current worktree baseline is 96f2c481. The returned registered table
family failed its screens and the rerun launch refused before dispatch.
Section 15 records this diagnosis and the proposed remedy. The numerical
audit is `simulation/v3/table_screen_audit_20260928.json`.

* The failure is substantive, not missing sensitivity work: 343/343 jobs
  completed. Primary screening rejected 5,604 rows across 217 of 325
  rule/kernel pairs. Sensitivity screening raised the published total to
  5,670. All 25 rules and all 13 rr values have at least one primary failure.
* Retain every original failure. Propose four times the primary time
  lengths and population counts, with the same rule class, context grids,
  nine-pair subset and numerical thresholds. Time-only probes still left
  four of 30 continuation failures; larger-population probes left four
  of six under the original validation domain. Regenerate the whole family.
* The operator approved the explicit continuation-domain correction in
  section 15 and A1. The old screen validated auxiliary bins omitted from the
  published table and overstated coverage. Validate the exported domain,
  retain the old statistics as diagnostics, and keep every threshold and
  failure in a covered published bin. This is not a claim of full-scale
  convergence or a passing replacement family.
* Preserve the exact completed calibration. The proposed compatibility
  record binds its artifact/value hashes and unchanged generating code;
  it does not refit values or authorize other stale calibrations.
* Review the fixed non-registered diagnostic subset and price in section
  15: 3.05 X2 hours at the measured throughput, or 15.14 in the stated
  route-migration scenario, against 24 hours. These are planning estimates.
  Rerun dispatch remains blocked until the entire replacement passes.
* Registered calibration and failed table output were read. No registered
  rerun output existed or was read. A1 is prepared in the pre-registration's
  section 13, approved by the operator and not committed. A new committed
  pin is required before replacement estimation.

The operator subsequently approved the unpublished-bin rule. Section 16
records its implementation, endpoint measurements and current test report.
It supersedes the earlier statement that a missing online bin aborts the
run: a missing value now excludes only its candidate from comparison.
The strict table gate, calibration compatibility proof and screens remain.

**Earlier A1 diagnosis report:** diagnosis, auditable per-context excesses, proposed
settings/code, regression tests and the dated amendment are prepared.
Final repository and v2 conformance checks: 226 passed, three existing v2
expected failures, in 66.54 seconds. Ten new amendment tests pass. Local
diagnostic batches completed 12 jobs, used at most eight workers and took
1,670.805 seconds including their configuration tests. Tests and audits
remained within the 45-minute local compute allowance. No registered
replacement or rerun was launched, and nothing was committed or sent over
the network. The unchanged frozen calibration is reusable only through
the exact reviewed compatibility record. Passing the full replacement
family remains required, with sparse published bins an unresolved risk.

### Historical B2 review list, 2026-09-27

1. R14, 2026-09-27 accepts the listed B1 deviations. They remain limitations,
   with no new request for reconfirmation in this session.
2. Review the declared primary settings, nine-pair sensitivity subset,
   empirical stability tolerances and conservative support definition.
   WE is absent and failed rows remain `not_estimable`. Full-chain QSD
   bias and summary aggregation are not certified by these checks.
3. Review the calibration block convention and fixed honest-baseline
   trajectory law. Protected levels are rescored in final units; target
   outcomes never enter calibration. Actual registered calibration and
   full-table production remain gated future executions.
4. Await the operator's X2 pilot. Neither budget has measured evidence
   yet. Fixture-policy costs, final artifact loading/publication overhead
   and extra sensitivity kernels must remain visible in any budget decision.
5. Sparse continuation bins may fail coverage or later encounter an unseen
   state. The safe implementation refuses such a lookup. Broader coverage
   requires additional declared estimation, not an online midpoint fallback.
6. Commit/pin approval belongs to the operator. No source, pre-registration,
   calibration, table or scientific result was committed in this session.

## 14. Report

The current D24 report is section 22. Earlier reports below retain their
original source identities and outcomes as historical records.


Stage A built standalone measurements, flow/discount arithmetic, reduced
Perron and side calculations, exact shock support, floors, no-write-off,
risk helpers and complete-plan comparison. Its original component timing
remains in `timing_results.json` for history, not as integrated evidence.

B1 adds a full-population wrapper, finite environmental stock updates,
measurement windows and propensities, vectorized rule rollouts, fixture
continuation/Lambda interfaces, exact cohort life tables and original-law
admission, period ledgers, precedence records, complete yield plans,
single simulated transition, fixed-chain capability ceiling, extinction
flow and per-step diagnostics. B2 adds plain/FV estimation, reduced
revalidation, held-out continuation fitting, frozen calibration and table
publication/loading, full workload manifests, a durable process runner,
registration gates, service supervision and the frozen X2 pilot bundle.
All existing v2 source bytes remain unchanged.

Verification: the repository pytest suite plus v2 conformance passed
with **216 passed and 3 expected failures** in 87.91 seconds on the final source.
All three expected failures are existing v2 contracts; the three B2
contracts now pass. No unexpected failure is accepted. The command
uses `PYTHONDONTWRITEBYTECODE=1`, `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`,
`PYTHONPATH=simulation`, one numerical thread, `-p no:cacheprovider`,
`-p test_v3_legacy_scope`, a basetemp inside `simulation/v3`, all
`simulation/test_*.py`, and `verification/conformance/test_conformance_v2.py`.
The small scope plugin keeps two existing read-only external-cwd tests
inside the write authorization without changing those tests.

Reduced FV's maximum measured flow error was **0.1282 percent**. Plain's
absolute flow error was 0.0004366 with 6,731 of 8,192 survivors. The local
short FV configuration probe took 4.74 seconds. Historical B1 integrated
costs remain in section 8 and its timing file; they are not current X2
measurements. Neither the 72-hour nor 24-hour ceiling is certified met.

The 35-job pilot archive is 285,947 bytes, SHA256
`368e5ed33fa292ffab84f36819fb6dff2ebc17e259d1b684ad954632adbd87da`.
The frozen specification hash is
`927580636c1df7adb23efc949837f64ab49a3d8f8167f7d5d422d30cbf3d52e6`.
Bundle hashes and an isolated extracted-copy model smoke passed. The
runbook is `simulation/v3/v3_pilot_RUN_ON_X2.md`; detailed verification is
`simulation/v3/verification_results_B2.json`.

Remaining execution: the operator's X2 pilot, reviewed budget decisions,
committed pre-registration/source, registered calibration, complete table
estimation and production-artifact validation. WE remains explicitly
unimplemented. No registered calibration, full table family or X2 job was
run here. Local computation stayed below one hour with at most three
worker processes. No network, commit, push, rebase or branch change occurred.

## 15. Registered table diagnosis and proposed A1, 2026-09-28

### Evidence and counts

The read-only returned records are under
`v3_instrument_inputs/registered/registered/`. The sequence log records a
registered calibration completion, 343 completed table jobs, then a rerun
refusal in `validate_spec` through `ProductionTables.require_production`.
There is no rerun output directory in the returned records; the operator
also states no rerun job ran or output exists. This work reads calibration
and table data only, not registered rerun outcomes.

The frozen calibration hash is
`bf0f7c3f10310558d567b6b3f7c24f6f99f2fe6eb71fd830cccfd8e2aa0bd6d6`.
The failed published table hash is
`deef0f6a85c93bc281820424d51f370fa580871ae2e460d6535e5a4a390689fa`.
`diagnose_tables.py` verifies both envelopes, all table row hashes, the
manifest's exact job/key set, and every one of the 343 completion/output
hashes, seeds, configurations and source identities. It distinguishes
original per-job primary status from the status after sensitivity assembly.
Every rule, rr, alpha, fixed capability, kappa, limit, observed value and
excess is retained in the derived audit JSON. No source input is modified.

| Family | Rows | Own-screen failures | Half-window drift | Continuation residual | Failed rule/kernel pairs |
|---|---:|---:|---:|---:|---:|
| Primary | 13,750 | 5,604 | 3,105 | 3,099 | 217 |
| Doubled population | 735 | 187 | 50 | 137 | 5 |
| Doubled length | 735 | 0 | 0 | 0 | 0 |

The primary failure sets overlap in 600 rows. The doubled-population
failure sets do not overlap. There are no failed half-width or route
screens, no failed applicable plain survival fraction, no continuation
coverage failure, no empty fitted table and no Bellman iteration failure.
There are no missing sensitivity jobs or contexts, and no FV ensemble
collapse. Primary routes were 198 plain and 127 FV; sensitivities were
six plain/three FV for doubled population and five plain/four FV for
doubled length. FV's recorded pre-cloning survival fraction is not tested
against the plain route's one-half requirement.

Of 735 selected primary scoring rows, 204 failed sensitivity eligibility.
There were 187 rows whose doubled-population counterpart was itself
`not_estimable`, and 42 failed doubled-length contrast intervals, with
25 overlapping rows. All 735 doubled-population numerical contrasts pass
when computed, including the 187 that assembly skipped because their
counterpart failed another screen. Of the 204 sensitivity failures, 138
already failed primary screening. The other 66 make the published total
5,670 failed and 8,080 estimated. Bypassing the sensitivity check would
therefore still leave thousands of failed primary rows.

| Rule | rr | Contexts | Primary failures | Bad doubled-population counterparts | Failed length contrasts | Sensitivity failures |
|---|---:|---:|---:|---:|---:|---:|
| balanced | .055 | 20 | 14 | 14 | 6 | 14 |
| balanced | .064 | 150 | 150 | 0 | 17 | 17 |
| balanced | .070 | 75 | 0 | 0 | 0 | 0 |
| w0_p0_t1_g3 | .055 | 20 | 16 | 20 | 9 | 20 |
| w0_p0_t1_g3 | .064 | 150 | 0 | 0 | 0 | 0 |
| w0_p0_t1_g3 | .070 | 75 | 0 | 62 | 0 | 62 |
| w3_p5_t1_g3 | .055 | 20 | 20 | 16 | 10 | 16 |
| w3_p5_t1_g3 | .064 | 150 | 150 | 75 | 0 | 75 |
| w3_p5_t1_g3 | .070 | 75 | 0 | 0 | 0 | 0 |

The machine-readable audit enumerates contexts rather than treating each
physical rule/kernel pair as one statistical row. A sensitivity count of
zero does not imply that its primary row passed, as balanced/.064 shows.

### Worst cases and causes

At kappa=8 the five-percent flow-range limit is 4.906412774; at kappa=.75
it is 2.527107714. The largest absolute primary half-window drift is
8.826456408, exceeding 4.906412774 by 3.920043634, for w3_p1_t1_g3,
rr=.056, alpha=.5, capability=1, kappa=8. The largest proportional drift
is the same rule/rr at alpha=1, capability=1, kappa=.75: 5.947570451
against 2.527107714, excess 3.420462737, or 2.35 times the limit.

The worst absolute continuation residual is balanced/.064, alpha=.5,
capability=1, kappa=8: 59.207292632 against 4.906412774, excess
54.300879859. The worst proportional residual is balanced/.064,
alpha=.5, capability=1, kappa=.75: 38.028818725 against 2.527107714,
excess 35.501711011, or 15.05 times the limit. Overall held-out transition
coverage remained at least 0.985432943, so good aggregate coverage did
not establish accurate conditional values in every bin.

The worst doubled-length contrast is w3_p5_t1_g3/.055 at alpha=1,
capability=1, kappa=.75. The difference is -2.760193138 and the 90 percent
half-width 1.062871144. Its absolute endpoint is 3.823064282 against
2.527107714, excess 1.295956568. The worst doubled-population residual
is w0_p0_t1_g3/.070 at alpha=1.5, capability=1.8, kappa=8:
6.034063243 against 4.906412774, excess 1.127650469.

These are not floating-point threshold ties. The primary settings are
too short to satisfy the declared family of screens. Burn 256 and measure
512 still include appreciable transient change, while the primary
half-widths are all below threshold (the largest proportional half-width
is 0.6211 of its limit). Doubling particles alone leaves drift and
continuation failures; doubling time removes own-screen failures in all
735 sampled sensitivity contexts. Nonzero length contrasts are further
evidence that the shorter tail estimate was not stable. This is evidence
about the declared subset, not proof of convergence for every rule.

The B1 plan in section 7 named plain burn 2,000 and measure 8,000 with six
independent runs. R13 replaced its route assumptions, and B2 used six
groups of 16 plain runs with burn 256/measure 512. More runs do not remove
transient bias. The B2 lengths were not validated on calibrated full-scale
data before publication; the registered gate correctly exposed this gap.
The maximum conditional Bellman residual remains sensitive to sparse
held-out bins. The old output did not record which bin attained the
maximum, so its exact cause cannot be reconstructed from aggregate
residuals alone. New probes record the five largest residual bins and
their training/held-out counts. They expose a validation-domain mismatch,
described below, as well as failures in genuinely published bins.

### Fixed local probes and the continuation-domain correction

The first probe manifest was frozen before its ten jobs. It used four
times the original lengths, six groups, 16 plain runs and 64 FV particles.
It tested balanced/.064, w0_p0_t1_g3/.070 and w3_p5_t1_g3/.055 at primary,
doubled-population and doubled-length settings, plus w3_p1_t1_g3/.056
primary. Each used three common scoring probes: (alpha, capability, kappa)
=(.5,1,8), (1.5,1.8,8), (1,1,.75). These are diagnostic probes; some
combinations are outside that rr's registered cell grid. They do not
replace the frozen registered sensitivity subset or enter results.
All 18 numerical sensitivity contrasts and all drift, half-width and
route screens passed. Four of 30 scoring rows still failed continuation:
balanced primary and doubled population at kappa=.75, and w3_p5 doubled
length at (.5,1,8) and (1,1,.75). The balanced primary residual was
2.726976131 against 2.527107714 in published bin [0,0,3,3,3,2], with
40 training and 13 held-out visits. Time-only effort was insufficient.

The second manifest fixed two primary jobs, balanced/.064 and
w3_p5_t1_g3/.055, at the proposed 64 runs/256 particles and longer
lengths. It used the same three scoring probes. Under the original
validation domain, four of six scoring rows failed continuation. For
w3_p5 all three failed; the largest residual was 17.514834036 against
4.906412774. Its source bin [0,0,1,0,1,1] had one training visit and one
held-out visit and was not published. Balanced's two kappa=8 rows passed;
its kappa=.75 row failed at 2.760795338 against 2.527107714, excess
0.233687624. That source bin [0,1,3,2,3,2] was published with five training
and two held-out visits. The earlier balanced bin now had 148 training
and 54 held-out visits and smaller error. These findings retain a real
sparse published-bin concern even after increasing effort.

The first batch used at most eight workers, selected by actual-workload
configuration tests, and completed table dispatch in 693.479 seconds.
The second selected two workers and completed in 947.546 seconds. Its
individual jobs took 755.952 and 946.816 worker-seconds. Both verified one
OpenBLAS thread per worker. Their manifests, launch records, complete
outputs and derived summaries are under `simulation/v3/amendment_probe*`
and `table_screen_probe*_20260928.json`. They are non-registered,
validation-tagged runs. Neither run claims to validate the final corrected
domain, which was implemented after these probes. No output is relabeled.

**A1 definition correction for operator review:** the table writer exports
C only on B_pub = {b: training_visits(b) >= 4}, plus the exact extinct
value. Internal fitted values on other bins are auxiliary values and the
loader will refuse them. For the exported artifact, the residual
r = (1-beta)u + beta C(b_next) - C(b) is defined only when b is in B_pub
and b_next is in B_pub or is extinct. The old validation used all bins
seen during training, including unpublished bins, for both coverage and
the residual maximum. This is not validation of the exported function.
It can both overstate coverage and reject a value absent from that table.

`continuation.fit_transitions` now uses that training-defined publication
domain for both statistics. Coverage still divides by all held-out
transitions, so missing sources or nonextinct endpoints lower coverage.
The 90 percent floor, maximum absolute conditional mean residual,
five-percent flow-range limit, four-visit publication rule and whole-group
split remain unchanged. No published source is filtered by its residual
or held-out sample count. The former all-training-bin statistics and top
bins remain in `legacy_all_training_bins`. Both source and successor
omission counts are reported. The broad flow-domain error enclosure and
missing-bin refusal remain. This empirical covered-domain statistic is
not a uniform Bellman residual and does not certify aggregation bias.

Mechanical counterexamples test the distinction. An unpublished source
previously reported as fully covered now lowers coverage to 5/6 and
fails the unchanged floor. A published source with an actual held-out
Bellman discrepancy still reports residual 10 against threshold 0.5.
A missing nonextinct successor lowers coverage, while extinction uses
its exact continuation. No threshold has been weakened to obtain a pass.
High aggregate coverage still cannot waive a published-bin failure.

### Minimal proposed correction and price

A1 changes estimation effort, diagnostics and the validation domain above. Proposed primary burn
1,024 and measure 2,048 provide four times the original lengths. Six
groups remain, with 64 plain runs and 256 FV particles per group, four
times their original counts to improve conditional-bin sample support. The nine
declared sensitivity pairs remain fixed. They receive twice the populations
or twice these longer lengths as before. This leaves time beyond the
successful old doubled-length setting without changing the objective,
state summary, grid, floors, admission, plans or numerical tolerances. The trajectory
length is shorter than the B1 10,000-step plain schedule, with more
independent trajectories. More particles are not claimed to cure time bias.

The first family cost 15,996.816 summed worker-seconds and 680.054 seconds
of table dispatch, at a selected 28 workers. Its measured effective
parallelism was 23.523. The full service interval was 773.771 seconds,
leaving 93.716 seconds for configuration and other overhead. Sixteen times
the work plus that overhead gives 10,974.586 seconds, or 3.049 hours.
Longer horizons can move plain rows to FV. Charging the whole family a
further factor of five, the 1,920-versus-384 population-step count
when adding FV to a plain job at unchanged occupancy, gives 54,498.062
seconds, or 15.138 hours. These are explicit planning scenarios, not measured
replacement runtimes or rigorous bounds on population and I/O effects.
All remain below the unchanged 86,400-second ceiling; no seed/grid cut is
needed for the proposal. Rerun the mandatory configuration test and keep
the runner deadline. The failed attempt used less than one percent of its
table dispatch allowance.

The full table family must be regenerated under the approved A1 pin, not
patched by replacing only failed rows. The original family remains frozen
as failed evidence. Calibration stays byte-identical at bf0f7c3f, with
its full hash above. The compatibility record compares that exact artifact,
its values and original code hash, 43 unchanged source dependencies, and
the unchanged `run_seed`/`freeze` function source. Any mismatch rejects
reuse. New table data retain the full new source identity and the old
calibration hash. Source dependency comparison normalizes CRLF to LF,
which Python's parser and Git checkouts treat equivalently, with no other
normalization. The 43 normalized dependency hashes were compared with
the committed baseline, not merely the edited worktree. This addresses
the old all-module source check without
silently recalibrating after registered table output has been inspected.
The compatibility JSON is included in `source_manifest` and the committed
source check. It cannot be silently changed outside the new code identity.

The larger probes do not establish a passing replacement family. They
identify the mismatch but do not eliminate the published-bin failure.
The final domain correction has reduced-instance regression validation,
not a new full-scale probe within this local budget. Additional uncertainty
is explicit: longer sampling may reveal further rare published bins, and
the strict maximum statistic need not improve monotonically with effort.
This is a concrete bounded candidate amendment, not a promise of passing
the gate. Operator approval covers one complete replacement family, with
all failures reported and no automatic tuning or outcome-based omissions.

The operator approved the amendment and code and must now commit them,
then supply the new pin. No replacement registered family or rerun is launched here.
If the full replacement still fails, report its rows and keep the gate
closed; do not automatically tune lengths, discard a row or relax a screen.

## 16. A1 completion: unpublished endpoints, 2026-09-28

The operator approved A1 and added a specific online availability rule.
The 90 percent continuation coverage screen does not make missing online
endpoints impossible. A missing value now excludes a candidate; it does
not terminate an otherwise valid run and never supplies an invented value.

### Implementation and diagnostics

`ProductionTables.lookup_available` returns a per-rule availability mask
and reason alongside its arrays. A missing or `not_estimable` rule/context
row and an unpublished living endpoint have no valid score. Internal NaN
markers denote absent arithmetic and cannot enter selection or serialized
output. Direct strict `lookup` still raises for callers requiring a value.
Malformed data, stale source/rule identities and unsupported weights are
not caught and converted into missing-bin fallbacks. Registered loading
still refuses an incomplete or failed table family. An extinct endpoint
uses exact u_dagger and zero continuation error; this does not invent a
missing Lambda_F row. Calibration dependencies, including `tables.py`,
remain unchanged, so the approved compatibility record still applies.

`V3Model._choose` intersects availability with the existing S5/R7 and
survival-first filters. If that comparison is empty, it chooses the
balanced action, preserving both floors. The reason distinguishes
`all_rule_scores_unavailable` from `no_scoreable_rule_passes_admission`.
The latter covers an otherwise available rule excluded by the existing
admission/risk filter, without relaxing that filter to force a comparison.
The fallback does not impute W. Missing objective components are null in
durable diagnostics; valid available components keep their computed values.
Each allocation record has `allocation_evaluated`,
`unavailable_rule_count`, `unavailable_rules`, `balanced_fallback` and
`balanced_fallback_reason`. The precedence audit records the fallback and
that the reproduction floor was not overridden. These fields describe
allocation before any separate yield review. A valid successor plan can
still determine the action executed after that review.

`review_yield` omits each unavailable complete plan before constructing
its value and before comparison. Existing admission evidence remains
required. It holds yield when no plan is admissible, without calling a
comparison on an empty list. Each review records `plan_count`,
`unavailable_plan_count`, `admissible_plan_count` and
`yield_held_no_admissible_plan`. The step records the unavailable-plan
count and held flag. `production_runner.execute` publishes
`continuation_availability`: allocation-step denominator, rule-exclusion
total, steps with exclusions, maximum rules excluded, per-rule counts,
balanced-fallback steps, unavailable-plan total and reviews held for no
admissible plan. Absorbed steps count neither an allocation nor a fallback.

### Endpoint evidence and its limits

The archived outputs contain published bins and coverage aggregates, not
raw trajectory states. Aggregate coverage is not an endpoint miss rate.
`unpublished_archived_bounds_20260928.json` therefore reports source-bin
bounds for all 325 original primary rule/rr pairs, with source hashes.
For N held-out transitions, let C be the old covered count and P the sum
of held-out counts in exported entries. Then (C-P)/N <= fraction of
unpublished source bins <= (N-P)/N. The gap includes missing successors.
These bounds do not account for the online exact-extinction exception and
are not an estimate of rollout exclusions. The largest upper bound is
1.477051 percent for w2_p1_t1_g3/.066; its lower bound is 0.020345 percent.
The largest lower bound is 0.1953125 percent for w0_p5_t1_g3/.070, whose
upper bound is 0.638835 percent. Publication domains agree across scoring
contexts within every audited rule/rr pair.

To measure endpoints, the frozen non-registered manifest
`unpublished_endpoint_manifest_20260928.json` selected 15 archived jobs:
the nine original sensitivity-pair primary jobs, the four time-only
primary probes, and both full-A1 primary probes. `unpublished_bins.replay`
replays the original plain seed and population count for 519 steps,
without estimating W or fitting any table. Every replay's surviving-run
count matches the archived plain prefix at every step. This checks that
truncating the allocated trajectory length did not change the RNG path.
The last two independent groups supply endpoints at t+20 for starts
t=0,...,499. Already extinct starts are omitted; extinct endpoints have
exact continuation and are not counted as missing. The original fixed
rule controls each path. For FV table rows these are unconditioned plain
paths checked against FV-published bins, not cloned paths presented as
unbroken 20-step rollouts. Source row status is ignored only for this
domain diagnostic; it does not make the failed tables admissible.

| Table settings | Rule | rr | Missing endpoints / living-start opportunities | Percent |
|---|---|---:|---:|---:|
| A1, four times length and population | balanced | .064 | 8 / 63,807 | 0.012538 |
| A1, four times length and population | w3_p5_t1_g3 | .055 | 13 / 55,501 | 0.023423 |
| Four times length only | balanced | .064 | 3 / 15,960 | 0.018797 |
| Four times length only | w0_p0_t1_g3 | .070 | 21 / 16,000 | 0.131250 |
| Four times length only | w3_p1_t1_g3 | .056 | 0 / 14,517 | 0 |
| Four times length only | w3_p5_t1_g3 | .055 | 2 / 13,761 | 0.014534 |
| Original | balanced | .055 | 16 / 13,204 | 0.121175 |
| Original | balanced | .064 | 17 / 15,752 | 0.107923 |
| Original | balanced | .070 | 13 / 16,000 | 0.081250 |
| Original | w0_p0_t1_g3 | .055 | 8 / 13,833 | 0.057833 |
| Original | w0_p0_t1_g3 | .064 | 30 / 16,000 | 0.187500 |
| Original | w0_p0_t1_g3 | .070 | 19 / 16,000 | 0.118750 |
| Original | w3_p5_t1_g3 | .055 | 1 / 13,209 | 0.007571 |
| Original | w3_p5_t1_g3 | .064 | 6 / 15,936 | 0.037651 |
| Original | w3_p5_t1_g3 | .070 | 4 / 16,000 | 0.025000 |

The A1 rows each used 128 held-out plain paths. At least one endpoint was
missing on 5/128 balanced paths and 3/128 w3_p5 paths. Among living
endpoints only, the rates were 8/63,749 = 0.012549 percent and
13/53,733 = 0.024194 percent. Balanced's eight misses occurred within the
first 100 starts; w3_p5's 13 occurred during starts 300 through 499. The
report includes 100-step blocks and the first 20 starts. Whole paths,
and especially their overlapping windows, must not be treated as tens
of thousands of independent Bernoulli trials. Different setting families
use different archived seeds, so the table is not a paired causal test
of increasing effort. Scoring contexts share the same publication domain;
availability on these paths does not depend on alpha, capability or kappa.

**Fallback frequency:** individual exclusions are rare in the two measured
A1 fixed-rule cases. These data do not establish frequent balanced
fallback, but they also cannot certify it will be rare in registered
adaptive runs. Only two of the 325 A1 rule/rr pairs have probe tables, and
their own-rule state laws are not the common live state law of an adaptive
25-rule comparison. Excluding at least one candidate over a run and
excluding every eligible candidate at one step are different events.
Multiplying marginal miss rates across rules would assume unsupported
independence and a shared state law. The actual all-rule fallback rate
remains unmeasured and will be reported from registered output, with no
change to settings based on those outcomes.

The derived report is `unpublished_endpoint_report_20260928.json`; complete
outputs and durable completion/launch records are in
`unpublished_endpoint_replay_20260928/`. The actual-workload configuration
test selected four workers from two, four and eight, with one verified
OpenBLAS thread per worker. All 15 jobs completed in 62.802 seconds of
dispatch, 86.449 seconds including configuration. No registered job ran,
no registered rerun output was read, and no service command or network
operation was used. This work stayed within 30 minutes and 12 workers.

### Completion report for review and commit

The unpublished-bin allocation rule, balanced fallback, complete-plan
exclusions and durable counts are implemented. Twelve new tests cover
missing rows and bins, all-rule and admission-filter fallbacks, exact
extinction, unavailable yield plans, output totals, endpoint arithmetic
and diagnostic-only execution. The full repository suite plus v2
conformance passed: 238 passed, three existing v2 expected failures, in
68.24 seconds on the final run. No threshold, seed/grid size, objective, floor or calibration
value changed. No commit was made. The original pre-registration text
before its A1 addition remains byte-identical.

The complete commit file list is `simulation/v3/A1_COMMIT_FILES_20260928.md`.
It includes the earlier A1 changes and this completion, and excludes
temporary test files, runtime lock files and the pre-existing pilot zip.
The full replacement table family still must be generated under the new
committed pin and pass every screen before registered rerun dispatch.

## 17. Initial W7 gates and amendment A2, 2026-09-28

This section records the initial gate implementation and its evidence-gap
finding. The operator subsequently approved recording that evidence.
Section 18 supersedes the unresolved-gap status and reports the completed
recording, compatibility and end-to-end work.

### Scope, timing and source identity

D21 adopts W7 sections 1 to 4, identified by SHA256
`6754f7d8a6e01f8d81fe69d6406b038d4f3be8202e5aa799c4f6eb2b3897cdd9`.
Amendment A2 was prepared after A1 tables started on the X2 from
`34ffbfe99e79ea9f546f1ed353a251ef8aede08e` and before any registered
rerun output was read. No registered rerun output was opened here. The
operator must commit the amendment before any such output is read.
No running instrument, registered setting or historical v2 validator was
modified. This work adds the standalone `v3.gates` checker and fixtures.

The calibration was copied byte-for-byte, as directed, from the cross-check
worktree to `v3/runs/registered/v3_rerun_calibration.json`. File SHA256 is
`fd86358a39e3b643fb9adc4e81a2372915ca50a1866e9b0e330a874b41746e01`;
the sealed payload hash is
`bf0f7c3f10310558d567b6b3f7c24f6f99f2fe6eb71fd830cccfd8e2aa0bd6d6`.
These are different hash domains, not conflicting calibrations. No input
specification was copied into the public repository.

`verify_instrument` compares each committed Python dependency and the
A1 calibration compatibility record with the working file, allowing only
Git's CRLF/LF conversion. It records individual source hashes and the
committed LF source identity used on the X2. New checker code has its own
file hash. Adding a checker changes today's `code_identity()`, so after
checks compare the original worker records against the original committed
instrument identity, not against a new checker-inclusive executor hash.
The checker remains separately bound to the committed A2 pin. This does
not change the runner's source checks or permit dispatch from mixed code.

### Independent checks and fail-closed behavior

`before_checks` exercises the real scalar and vector instrument paths but
computes expected values separately. It tests marginal finite differences,
lineage products including zero factors, clipped transfer and frontier
limits, normalized discounted sums and elapsed committed-unit suffixes,
bounded flow, absorbing extinction and strict complete-plan yield scenarios.
The calibration epsilons are inputs, not fixture defaults. Mutations of the
candidate functions are detected by negative tests.

`reference_plan` evaluates the complete post-action flow sequence and
continuation, then applies the epoch's elapsed discount only to its
original discounted-component coefficient. `recompute_review` finds the
best eligible immediate and waiting alternatives, including later yields,
and holds a tie. Plan availability must agree with the presence of actual
continuation and Lambda_F values. Plan admission must agree with both
recorded cohort bounds, not a free-standing Boolean. Missing values have
no substitute. `check_gamma` independently recomputes the disrupted and
undisrupted complete-plan values and checks the actual comparison values.
Double subtraction fails even when it leaves the final fire flag unchanged.

`fire_from_run` derives the binary run outcome from capability increases
in the executed path. It ignores reported fire-rate summaries. The loader
cross-checks reviews with changes on that path. `cliff_checks` recomputes
the full R2 pooled grid, cap*, 2,000 seed-bootstrap draws and the adjacent
support requirements. `separation_check` computes the two-binomial-rate
difference standard error. No cap above a defined cap* is not testable,
not a pass. G2.2 governs the cliff reading, correcting D10's phi disposition.

`sample_reviews` and `sample_steps` implement A2's fixed hashes and quotas.
Only small heaps of selected records are retained, not the whole rerun
family in memory. G3.3 visits every fired R2 succession. G4.3 visits every
protection-period record in R1, refinement and R2. `reference_cohort` uses
independent scalar integer recursion and rational products for the
survival-first comparison. Its first-action welfare shares are the fixed
class's four tiers, 1/6, 0.25, 0.4 and 0.6, followed by the floor path.
The exact integer survival numerator rounds down at each step. This checks
R14's conservative cohort-upper-bound action ordering, not optimality for
actual extinction probability. Above-bound living steps require raw ages,
welfare and the executed action. An empty population has no action to
check. An override without a checker-verifiable full certificate fails;
no such certificate format exists in A1. Ledger risk must sum exactly to
0.001, with zero statistical alpha spent.

`aggregate` fixes dependencies in code and rejects missing, duplicated,
skipped or relabeled checks. G3.1 has two independently required parts.
The five not-applicable entries are fixed with their D10/D12/W2/W3/P4
reasons. G1 clearance alone makes no R1 or R2 result citable. Fixture mode
can exercise aggregation but never produces a true citation flag.

The pre-registration's A2 section records all substantive thresholds,
comparison tolerances, hash identities, 100/100 review allocation and
short-stratum fill, bootstrap seed and resampling unit, and the 2-SE
formula. Equality cases follow the declared strict or inclusive inequalities.
Passing finite samples report n and the nominal 95 percent zero-failure
bound. The report states the dependence and stratification limitations;
it does not turn chosen cases into a universal certificate.

### Evidence schema and unresolved gap for operator review

Source inspection alone showed that A1's rerun output schema could not furnish
all W7 evidence. The existing outer worker schema is `{job, code_hash,
runtime, result, seconds, started_epoch, finished_epoch}`, with per-step
`result.diagnostics`, `result.periods` and `result.yield_events`. Durable
completion records carry the exact job, source hash, completion status
and output file hash. The new tests use that shape, reduced horizons and
an explicit `fixture: true` marker. They add the following raw contract
inside synthetic records; A1 did not emit this extension:

* Review `gate_evidence.epoch`: epoch ID, origin, deadline, beta, theta,
  extinction flow, preference ID and information-law ID.
* Review `gate_evidence.plans`: all candidate alternatives, including
  unavailable and unadmitted ones. Each has its plan ID, committed IDs,
  start, terminal time, first-yield time, complete reward sequence,
  continuation and Lambda_F, availability, admission and
  `admission_evidence` containing period and active cohort bounds.
  Missing continuation or Lambda_F is null, never a filled value.
* Review `gate_evidence.comparison_values`: the actual values entering
  comparison for every eligible plan. Each yielding plan also supplies
  `undisrupted` with only the counterfactual flows, continuation and
  Lambda_F. Its units, deadline and information law cannot change.
* Fired review `gate_evidence.succession`: generations before/after,
  capabilities before/after, requested capability, capability ratio and
  measured knowledge transfer. The capabilities must match the executed
  diagnostics, not merely each other.
* Step `gate_evidence`: raw frontier velocity, effective bandwidth and
  transfer stock for Theta. In above-bound periods it also needs
  `ages_before`, `welfare_units_before` and the six-channel executed
  `action`. Selected absorbed steps still need the raw formula evidence
  required by G4.1; the checker does not silently remove them.

A1 has only best/chosen review values, not the full alternatives or paired
undisrupted plans. It lacks the raw Theta inputs, complete succession
record and pre-action cohort needed for the other checks. G3.1.sample,
G3.2, G3.3, G4.1 and above-bound action portions of G4.3 therefore cannot
be cleared from that schema alone. This is a missing-evidence finding,
not a failed scientific comparison or a permission to skip those gates.
No after output was read to reach it. A replay or sidecar reconstruction
protocol is not implemented or implicitly approved here. It would require
its own dated, hash-bound amendment before affected output is read or
re-read. The A1 balanced fallback also does not automatically establish
W7's survival-first property; the independent action check remains binding.

The evidence manifest has schema `v3-gate-evidence-1`, `fixture: false`,
`instrument_commit`, `instrument_code_hash`, and path/SHA256 references
for `calibration` and `rerun_manifest`. Its `runs` array has one
`{output: {path, sha256}, completion: {path, sha256}}` entry per job.
Paths are relative to the manifest or absolute. The command's explicit
manifest SHA256 binds this index. The loader validates the complete
24,900-job registered family and seeds before sampling. Fixture hashes
can test malformed artifacts but cannot be accepted in registered mode.
Every streaming traversal verifies output file hashes again.

From `simulation/`, before mode is:

```text
python -B -m v3.gates --phase before --calibration v3/runs/registered/v3_rerun_calibration.json
```

The after command, to be used only after A2 is committed and the evidence
contract is met, is:

```text
python -B -m v3.gates --phase all --calibration v3/runs/registered/v3_rerun_calibration.json --a2-pin PATH_TO_COMMITTED_A2_PIN --evidence-manifest PATH_TO_EVIDENCE_INDEX --evidence-sha256 FULL_INDEX_FILE_SHA256
```

The pin uses the existing `{path, commit, sha256}` registration format.
The checker verifies that both the clean pre-registration file and its
own code are committed at that pin before opening the evidence manifest.
It refuses without that pin. This after command was not run. Reports are
written only under `simulation/v3/runs/`; copying them into diagnostics
is reserved for the results commit. The before command reports all after
checks as not run and all result citation flags as false.

### Validation and report for review

All six before checks passed on the pinned 34ffbfe9 instrument with the
registered calibration. Counts are G1.1: 12; G1.2: 256; G1.3: 326;
G1.4: 15; G1.5: 34; and G3.1.scenarios: 5. The final before run took
19.99 seconds, including source verification. The JSON and Markdown
reports are `v3/runs/v3_rerun_gates.json` and `.md`. They clear through
G1 only, leave all seven after checks not run, and set R1, R2 and
R2_cliff citation flags to false. This is not a registered rerun result.

The full simulation suite plus v2 conformance passed: 289 passed and
three pre-existing v2 expected failures in 276.14 seconds. The 51 new
gate tests include positive, negative and equality cases, flipped yield
flags, double Gamma, off-formula Theta, admission above epsilon, missing
checks, cap* increases, unsupported bootstrap decreases, inconsistent
eligibility and incomplete/hash-broken artifacts. They test the registered
output envelope using explicitly labeled synthetic records. A pin-order
test proves that after mode refuses before opening any rerun artifact
without a committed A2 pin. No registered after-mode command was run.

`v3/runs/w7_validation_20260928.json` records the command, timings,
before-report hash and verified one-thread OpenBLAS runtime. Compute
remained below 30 minutes and four workers; before checks used one
process. No network call, remote launch, branch change or commit occurred.
The complete explicit commit list is `v3/A2_COMMIT_FILES_20260928.md`.
Temporary pytest trees and service/runner lock files are excluded. A
cleanup request for temporary test directories was blocked by the tool
policy, so those directories are left in place. The pilot manifest that
a legacy test regenerated was restored to its exact HEAD bytes.

**Operator review:** commit A2 before any registered rerun output is read.
Do not treat the passing before report as clearance for a rerun result.
Resolve the disclosed raw-evidence gap through an explicit amended
protocol if reconstruction is wanted. Missing evidence currently fails
closed. No pass rule has been relaxed to accommodate the A1 schema.

## 18. A2 evidence recording and A1 table compatibility, 2026-09-28

### D22 decision and historical recording validation

D22 accepted the schema finding: the A1 rerun output schema lacked
evidence for G3.1's sample, G3.2, G3.3, G4.1 and the action part of G4.3.
The rerun step was paused before dispatch. The first recording text was
written after the A1 table jobs started and before any registered rerun
manifest, job or output existed. Those tables subsequently completed and
failed their screens. No registered rerun output existed when this section was written. A2 is
committed before any rerun output is read. Section 21 records the final
review corrections and validation; the section below preserves the
original recording experiment before D23.

`integration.py`, `engine.py`, the measurement, policy, transition,
objective, admission and plan implementations remain byte-identical to
34ffbfe9. `recording.RecordedV3Model` subclasses that executor. The runner
uses the subclass only for its rerun workload. Allocation, yield,
admission and state transitions execute the original methods. Evidence
is never passed back into those methods. The superclass evaluations
return the same arrays and values, without rounding or reconstruction.

The observer records all alternatives, including unadmitted and
unavailable plans, and recomputes their recorded comparison scalars with
the same `plan_value` function used by the executor. The independent gate
uses its separate reference arithmetic. There is no recorded Gamma field
to trust: disrupted and undisrupted complete rewards, continuation and
tail values are supplied. The undisrupted counterfactual follows the same
feedback rules and absolute review/deadline times with the transition
drawdown suppressed. Its copied state and fresh private channel generators
cannot advance any original live or scoring stream. Additional diagnostic
draws are necessary when the counterfactual's population differs; they
are separate computations, not changes to the original draws. Missing
counterfactual continuation remains null. If needed for G3.2, that absence
fails the gate without an invented value.

Fired reviews record the actual transition count plus one as generation,
before/after capability, their ratio, requested capability, and the
executed transfer_comprehension allocation as a labeled knowledge-transfer
observable. This does not claim a separate retained-knowledge stock exists.
All steps record the raw Theta inputs. Absorbed steps have zero stocks and
frontier and record Theta=1 inside evidence; the original absorbing-flow
record stays unchanged. Raw ages, integer welfare, summary bins, rule IDs
and executed action are recorded at every living start in an above-bound
period or while survival-first is active.

### Format, provenance and checker completion

The observer records all reviews and all Theta inputs. No cases are
removed before W7's frozen sample selection. At 50 reviews per 500-step
job, a job-local 100-per-stratum cutoff would not reduce records; no such
optimization is used. Above-bound action evidence is recorded exactly
where the gate can need it.

The `gate_evidence` envelope contains canonical JSON compressed with gzip
mtime zero and encoded as base64, its raw SHA256 and byte count, and
schema `v3-gate-evidence-1`. The nested review and diagnostic arrays align
one-for-one with the unchanged original arrays. This retains normal JSON
worker output and its existing atomic publication. The durable completion
record hashes the full output including the compressed evidence. The
checker verifies the outer hash, decompression, inner hash and counts
before joining evidence to records. A crash before the completion record
leaves an incomplete job, exactly as before. No partial or unhashed
sidecar can satisfy a gate.

The runner now durably saves its sealed manifest under the run root.
`python -B -m v3.gates index RUN_ROOT` reads that manifest and complete
records, verifies identities and output hashes, and writes a path/hash
index under `v3/runs/`. It also binds the actual calibration and table
files. Registered indexing requires the committed A2 pin before opening
outputs. The after checker validates the full registered grid and all
source identities. `--validation` is a separate non-registered mode for
real local runner output: it keeps the frozen sample sizes, thresholds,
comparisons and missing-evidence failures and always makes citation false.
It refuses a registered manifest. It is not a registered-mode bypass.

Two checker details are clarified before any registered output exists.
G4.1 accepts the absorbed formula measurement within evidence when the
legacy step has no top-level Theta. G4.3 reconstructs welfare shares of
the actual feedback class at the recorded bins. The original checker
listed only unstressed tiers; stress raises the nonbalanced rules to
full welfare in the execution class. Excluding that response from the
reference minimization was a checker defect. Its correction leaves the
risk standard unchanged. The minimum remains over the same declared
rules, including balanced. A fallback can still fail the survival-first
requirement; missing-score availability is not a certificate of that
property.

### Table compatibility proof and its limits

`table_compatibility_A2.json` is an explicit, reviewed source exception.
The A1 producer is 34ffbfe99e79ea9f546f1ed353a251ef8aede08e, with source
identity `63fb0417db990956f2bc1d2b49743ad3248e8426aa50337748e586ab7b073cf5`
in its LF checkout. The record pins the frozen calibration payload and
the complete A1 table-design hash. It compares all unchanged original
Python dependencies and the A1 calibration compatibility record, with
only Git newline normalization. The only changed original modules are
the artifact source inventory, the runner's observation/publication
boundary and the table loader's explicit source exception. Their approved
A2 hashes, plus the new observer and compatibility checker, are pinned
separately. The compatibility record itself participates in code identity.

Table production and semantics are unchanged: estimator trajectories,
plain/FV routes, sensitivities, continuation fitting and publication,
row keys and lookup values, rules, kernels, calibration and all screens.
The loader changes only its source-identity condition. It still checks
every seal and identity, family completeness, fixture status, sensitivity
status and row status. Missing online values still have no substitutes.
Tests reject changed source, calibration, design or dependency, and prove
that the exception cannot make a fixture table registered. The A1 artifact
subsequently completed and failed its screens. Section 21 replaces the
initial source-only exception with its exact published seal and file hash;
registered loading was tested and refused. Any repaired family requires
its own record. A failed screen still stops launch.

The rerun workers retain exact current-source checks and the committed
pre-registration requirement. The A1 exception applies to table provenance,
not to rerun code or mixed-code resumption. Source verification in before
gates permits the explicit A2 observation/loading and D23 boundaries,
with source hashes checked as recorded in section 21.

### Non-interference and end-to-end validation protocol

`recording_validation.py` extracts the committed 34ffbfe9 Python snapshot
inside the authorized v3 run directory. It does not check out, change
branches or commit. The snapshot's file hashes are recorded. Reference
workers import that isolated snapshot. Amended workers import A2. Both
use identical job objects, seeds, configurations, calibration and tables.
Existing sparse non-registered probe rows are repackaged without changing
any value or status under the original producer identity; the other jobs
use the already existing `FixtureTables`. Neither is a registered A1 table.

The six fixed 500-step jobs cover R1, refinement and R2 at alpha 0.5, 1.0
and 1.5, with initial populations 200 and 40. Three use sparse probe tables
and three existing fixtures. Sparse domains exercise unavailable scores
and balanced fallbacks; small populations exercise above-bound periods.
Coverage of naturally fired yields and successions is reported, not
assumed or obtained by selecting favorable seeds after inspection.

The comparison removes only the new evidence envelope from each complete
scientific result and compares canonical bytes and their SHA256. It also
audits the order, channel identity, dtype, shape and exact bytes of every
original RNG return, comparing draw counts and hashes. Private diagnostic
counterfactual streams bypass that original RNG factory. Worker metadata
such as source identity, timestamps and elapsed time necessarily differs;
that operational metadata is not misrepresented as byte-identical.
The observer's state arrays are additionally compared in unit tests.

The same six-job family runs through the real durable production runner,
including its mandatory actual-workload configuration test. Two and four
workers, one numerical thread each, are measured. The measured selection
is four workers. A separate four-process comparison batch uses that
selection; at most eight simulation processes run concurrently. No
statistical gate threshold is changed for this reduced validation family.
The index and after-checker consume these real outputs in validation mode.

### Measured findings and cost

All six 500-step scientific result comparisons passed byte-for-byte
canonical equality after removing only the evidence envelope. Every
original RNG return hash and call count matched. The first three jobs
used sparse archived probe rows; the last three used existing fixtures.
The sample reached above-bound periods and balanced fallbacks. It did not
produce a natural fired yield or succession. The separate declared stress
fixture supplies a successor tail advantage at the epoch's last review,
then tests actual firing, succession fields, once-counted Gamma and
identical original-executor results. It is not substituted for a natural
registered succession or counted in the six-job sample.

The durable runner completed all six jobs in 368.18 dispatch seconds.
Its configuration measurements were 15.94 seconds at two workers and
10.85 seconds at four for four short actual-workload jobs. Selection was
four workers, one verified numerical thread per worker. No service
operation was used on the workstation.

The evidence index and after CLI ran successfully on these real,
non-registered outputs. The CLI returns a nonzero exit because some
governing checks fail, not because the output schema is unsupported:

| Check | Result and scope |
|---|---|
| G1.1 to G1.5, G3.1 scenarios | All six before checks pass. |
| G3.1.sample | 200 reviews, zero mismatches, nominal bound 0.0148670. |
| G3.2 | 73 R2 reviews, zero mismatches. Three reviews contain eligible comparisons, totaling 150 yielding alternatives. The other reviews are certified holds with no comparison. |
| G3.3 | No fired R2 succession, so insufficient evidence and no pass. |
| G4.1 | All 1,000 available R2 steps match the formula. The gate fails because 10,000 are required; the smaller diagnostic is not a gate pass. |
| G2.2, G4.2 | Incomplete R2 seed/grid evidence in this six-job validation family. |
| G4.3 | 58 violations out of 120 periods, all in the three sparse-probe jobs. Survival-first periods are 116/120 = 96.667 percent. |

The G4.3 failures have a concrete cause: balanced fallback under missing
scores is not the minimum cohort-bound action at these states. All three
sparse-probe jobs fail in each of their above-bound periods, 19 + 19 + 20.
The fixture-table jobs have no such violations. No raw field, array count
or compressed hash is missing or inconsistent. This validates the
recording/index/checker path and exposes a real gate failure in the
chosen non-registered sparse tables. It does not predict how often the
complete A1 family will invoke fallback, and it does not authorize changing
that fallback or weakening W7.

| Job | Category, alpha, N0 | Tables | A1 seconds | A2 seconds | Paired wall difference | Added bytes |
|---|---|---|---:|---:|---:|---:|
| 0 | R1, 0.5, 200 | Probe | 214.360 | 190.984 | -23.376 | 300443 |
| 1 | Refinement, 1.0, 200 | Probe | 213.477 | 178.713 | -34.764 | 344319 |
| 2 | R2, 1.5, 40 | Probe | 152.071 | 144.133 | -7.938 | 148031 |
| 3 | R1, 0.5, 200 | Fixture | 157.715 | 169.523 | 11.808 | 400019 |
| 4 | Refinement, 1.5, 40 | Fixture | 125.672 | 135.765 | 10.094 | 183535 |
| 5 | R2, 1.0, 200 | Fixture | 137.610 | 148.938 | 11.328 | 348779 |

Those paired wall differences retain scheduling noise from the concurrent
cross-check and other validation work. The negative differences are not
a claimed recording speedup. To isolate observation work, two fixed jobs
were timed again with disjoint inclusive-method differences:
(recorded evaluate minus base evaluate) + (recorded review minus base
review) + (recorded step minus base step) + evidence packing. The nested
base costs cancel; this counts each observer operation once without
changing its returned values or invoking a different simulation.

For job 0, direct observation cost is 0.629 wall seconds, 0.453 CPU seconds,
in 125.165 wall seconds total. For job 5, with available fixture values
and paired counterfactuals, it is 18.043 wall seconds, 14.000 CPU seconds,
in 141.232 wall seconds total. The latter is about 14.6 percent added to
the execution time excluding observation. JSON worker publication is
additional; deterministic gzip packing is included in these timings.

The sample projects 7.159 GB of additional serialized evidence and
32.687 GB of scientific result JSON for 24,900 jobs. Applying the sample's
smallest and largest evidence sizes gives 3.686 to 9.960 GB added. These
are decimal GB and exclude indexes, completion metadata and duplicate
archives. Population means range from 15.884 to 106.658 and maxima from
47 to 246; production populations can be larger. Do not treat these disk
figures as upper bounds at N=1,600.

At the measured X2 table-phase effective parallelism of
15,996.816 / 680.054 = 23.522861, and an explicitly assumed speed factor
s=1 for local versus X2 per-job performance, direct overhead projects
0.185 hours for the sparse case and 5.305 hours for the available-value
case. CPU-time projections are 0.133 and 4.117 hours. The corresponding
whole-job wall-time projections are 36.803 and 41.528 hours, leaving
30.472 hours below the unchanged 72-hour ceiling in the latter scenario.
For a local/X2 per-job time ratio s, divide these hours by s. No matched
ratio was measured here. These are planning scenarios, not measured X2
rerun throughput or evidence that all registered populations will fit.
The real X2 configuration test and runner deadline remain binding.
The recording does not change or rerun the A1 tables, so its added table
compute is zero; the existing 24-hour table ceiling remains intact.

Reports are under `v3/runs/a2_recording_validation/`: `noninterference.json`,
`cost_projection.json`, the two direct timer records, the evidence index,
coverage diagnostics and gate JSON/Markdown. The compressed validation
archive preserves paired results and real runner outputs/completion
records for review. It excludes the disposable baseline checkout,
pytest trees and runtime locks. The committed extraction/comparison tool
can reproduce the isolated baseline from 34ffbfe9 without checking out
or committing any worktree state.

### Final report and review status

The final full suite passed: 301 tests passed, with three pre-existing v2
expected failures, in 225.95 seconds. The first full run exposed one old
test that patched the original model factory instead of the new recording
factory. The test now uses the actual observer, retains its original
fallback-count assertions and verifies the packed evidence as well.
No runtime behavior was changed to satisfy that test. Twelve new
recording/compatibility tests supplement the 51 W7 tests.

The refreshed six before checks pass, and the real non-registered
runner/index/after workflow has no schema mismatch. The six paired
scientific outputs and original RNG streams match exactly. The recorded
G4.3 sparse-table fallback failures and insufficient-sample gates remain
failures. No registered rerun output exists or was read. Final hashes and
validation are in `runs/a2_recording_validation/final_validation.json`.
The explicit commit list is `v3/A2_COMMIT_FILES_20260928.md`, and the
operator's launch instructions are `v3/A2_RUN_ON_X2.md`.

All local work stayed below 60 minutes and eight simulation workers with
one numerical thread each. No network, X2 access, branch change or commit
occurred. The original scientific executor and v2.0 validator remain
unchanged. The pilot manifest regenerated by a legacy test was restored
to HEAD bytes. Disposable test directories, baseline extraction and
runtime locks are excluded from the commit list. The operator approves
and commits A2, then launches from that pin against the completed A1
tables; this work does not resume the paused chain.

## 19. Completed A1 diagnosis and A3 proposed, not adopted, 2026-09-28

### Verified evidence and screen accounting

The operator supplied read-only `registered_A1/` records after all 343
table jobs completed. The publication file SHA256 is
`56db71633a0f4710692e3354e3bc2fb5829286abbfa59e61609bd3f8cf6fcb3c`.
`a1_screen_diagnosis.py` verifies the publication and row seals, required
row keys, original manifest seal, every job/configuration, all 343 durable
output hashes, producer identity and calibration identity. No registered
rerun location is opened. The first family is compared using the earlier
verified audit. The complete derived audit is under
`v3/runs/a1_screen_diagnosis/`; the compact commit artifact
`v3/A1_TABLE_DIAGNOSIS_20260928.json` contains all 717 rejected published
rows, all 46 failed sensitivity estimates, numerical values, limits and
excesses, all job timings/hashes and the dimensional breakdowns. Thus the
rule, rr, alpha, capability and weight context of each failure is recorded,
not only the worst examples below.

| Estimate set | Rows | Failed | Failed rule/rr jobs | Failed screen |
|---|---:|---:|---:|---|
| Primary | 13,750 | 671 | 42 | Published-domain continuation residual |
| Doubled population | 735 | 6 | 1 | Same residual |
| Doubled length | 735 | 40 | 1 | Same residual |
| Published after sensitivity | 13,750 | 717 | 44 affected pairs | Union, with no overlap between the 671 and 46 |

All 1,470 numerical Lambda_F sensitivity contrasts pass. The 46 selected
failures are complete estimates, not missing jobs or failed Lambda_F
contrasts. Six come from balanced/.055, doubled population: alpha=.5,
capability=1, kappa=8, plus alpha=1, kappa=.75 at capabilities 1, 1.5,
2.25, 3.375 and 5. Forty come from w0_p0_t1_g3/.064, doubled length,
at kappa=8, across all five alphas and lower capabilities. Within the
frozen capability grid the failing upper cutoffs are alpha=.5: 4.05
(13 rows); .75: 3 (nine); 1: 2.5 (seven); 1.25: 2.25 (six); and
1.5: 2 (five). The machine record gives every context and excess.

No flow half-width, half-window, survival fraction, route, coverage,
empty-continuation or solver screen fails. There are no ensemble
collapses. All Lambda_F point estimates are finite. The smallest plain survival fraction
over all settings is 0.580729, above 0.5. Primary coverage ranges from
0.9998245 to 0.9999911, above 0.9. The largest primary flow half-width
is 0.750728 and half-window drift 0.928262; compare the context-specific
limits 4.906413 (kappa=8) and 2.527108 (kappa=.75). The least-margin
Lambda_F contrast has difference -0.402864 and half-width 0.355055
against limit 2.527108, leaving 1.769188 of margin.

### Concentration, worst cases and comparison with the first family

| rr | Published failures / rows |
|---:|---:|
| .055 | 49 / 500 |
| .056 | 0 / 500 |
| .057 | 154 / 2,000 |
| .058 | 14 / 500 |
| .059 | 9 / 500 |
| .060 | 0 / 2,000 |
| .061 | 19 / 375 |
| .062 | 19 / 500 |
| .063 | 21 / 375 |
| .064 | 40 / 3,750 |
| .065 | 102 / 375 |
| .066 | 215 / 500 |
| .070 | 75 / 1,875 |

The high-rate .065/.066 cells contribute 317 failures; failures are not
confined to near-boundary FV estimation. Plain contributes 392/2,715
published rows and FV 325/11,035. The rule totals range from zero for
w1_p4_t1_g3 and w2_p0_t1_g3 to 110/550 for balanced, 91 for w0_p0_t1_g3,
87 for w2_p4_t1_g3 and 75 for w3_p4_t1_g3. Twenty-three of 25 rules have
at least one affected context. The full rule-by-rr pattern is recoverable
from the individual records, which also retain the route and setting.

By alpha, failures are .5: 199/3,000; .75: 55/1,875; 1: 273/4,000;
1.25: 49/1,875; 1.5: 141/3,000. By capability, 148/1,500 incumbent
capability-1 rows fail, versus 73/1,500 at capability 5; all intermediate
capabilities have failures. The ordinary kappa=8 family has 606/10,875
failures and the kappa=.75 weight corner 111/2,875. Scoring rows from
one job share trajectories, so these counts are correlated, not 717
independent failures.

| Case | Absolute residual | Limit | Excess | Worst-bin training / held-out visits |
|---|---:|---:|---:|---:|
| Primary w1_p1_t1_g3/.066, alpha=.5, cap=1, kappa=8, plain | 22.361178 | 4.906413 | 17.454766 | 25 / 11 |
| Same rule/rr, alpha=1, cap=1, kappa=.75 | 12.199431 | 2.527108 | 9.672323 | 25 / 11 |
| Primary balanced/.057, alpha=1, cap=1, kappa=.75, FV | 10.839527 | 2.527108 | 8.312419 | 7 / 1 |
| Doubled population balanced/.055, alpha=1, cap=1, kappa=.75, FV | 3.648071 | 2.527108 | 1.120963 | 8 / 1 |
| Doubled length w0_p0_t1_g3/.064, alpha=1.5, cap=1, kappa=8, FV | 5.826507 | 4.906413 | 0.920095 | 5 / 1 |

The largest normalized exceedance is 4.8274 times the limit, in the
second row. The smallest excess is 0.001477 for primary
w2_p5_t1_g3/.061, alpha=1.5, capability=1, kappa=8. All 717 failed
primary/sensitivity estimates have a worst
bin with only 1 to 23 held-out visits and 4 to 63 training visits. Of
these, 320 have one held-out visit. Worst-bin population categories are
431 below N=80, 234 at N=80 through 199, and 52 at N=200 through 399,
with K=1,600. Rare low-population stock combinations cause the validation
failures even in otherwise viable plain trajectories. They are not
evidence that the main Lambda_F estimate is undefined.

The first family had 5,604 failed primary rows and 5,670 rejected
published rows, versus 671 and 717 now. A1 eliminated all 3,105 original
half-window failures and all 42 original numerical contrast failures.
Of the primary rows, 5,225 changed from failed to estimated, 379 failed
both times, 7,854 passed both, and 292 formerly passing rows now fail.
The 292 new failures matter: fourfold length and population do not make
this maximum-over-bins screen monotonically easier. Different samples
and newly published rare bins can expose fresh discrepancies. The two
families also differ by A1's validation-domain correction, so the total
improvement cannot be attributed to effort alone.

### What the definitions support, and what they do not

The fitted continuation solves an empirical training-bin Bellman fixed
point. On held-out complete groups, A1 checks the largest absolute mean
of `(1-beta)*u + beta*C(next) - C(source)` conditional on each covered
published source bin. Coverage is an entirely separate statistic. One
bad observation in a scarcely visited published bin can fail the whole
row while total coverage exceeds 99.98 percent. The current fixed-point
solver converges; a small training residual cannot validate a held-out
conditional mean. The high overall sample count is not the per-bin
sample count. Visits within a trajectory or FV group are correlated.

This is primarily a sparse conditional-estimation problem on the evidence
available. Longer measurement alone has limited value for transient
stock/population bins visited early, since the continuation fit includes
burn-in transitions too. Larger independent trajectory populations
increase opportunities to visit those bins. However, no transition
variances, full microstate distributions or independent binwise error
certificates were archived. The records cannot separate sampling noise
from aggregation/distribution mismatch in each failing bin. Both remain
possible; true residual bias need not vanish with effort. There is no
evidence of a vanishing flow-range denominator: its two limits above
are fixed and positive. FV and plain both exhibit the failure, while
their route and flow-stability diagnostics pass.

No screen correction is justified by this audit. In contrast to the first
family's validation-domain mismatch, the A1 residual is computed on
exactly the published domain. Changing a maximum to an occupancy-weighted
average, dropping bins because their observed residual fails, imposing a
new held-out-visit cutoff, or ignoring continuation failures in a
sensitivity estimate would weaken the registered check. None is done.
The proposed larger populations improve estimation effort, but there
is no evidence-based guarantee that any affordable effort passes every
bin. Even the rough inverse-square-root heuristic is not a bound here.

### Query exposure without registered outcomes

A row is indexed by rule, rr/kernel, alpha, capability, weight and
initial-law population. It is not indexed by the current population bin.
An invalid row therefore affects every candidate query in that context,
even if its offending continuation bin is rare. Across the frozen
24,900-job grid, at the common initial capability 1 and kappa=8,
56,750 of 622,500 first-step rule queries map to failed rows, 9.116 percent.
At least one row is affected in 19,875/24,900 jobs, 79.819 percent. This
is a deterministic overlay on input configurations, not a rerun result
or a 500-step frequency estimate. No configuration has all 25 rows
invalid; the worst full-table context has 13 invalid rules.

The archived A2 recording validation supplies six non-registered
500-step paths with verified durable output hashes. Reading is restricted
to pilot/validation tags. The paths are not replayed with A1 scoring,
and their original decisions are not changed. Four paths match the
registered N=200 initial law:

| Existing path | Failed candidate queries / all queries | Steps affected | Existing chosen-rule selections in failed rows |
|---|---:|---:|---:|
| R1 .060, alpha=.5 | 0 / 12,500 | 0 / 500 | 0 |
| R1 .064, alpha=.5 | 500 / 12,500 | 500 / 500 | 0 |
| Refinement .063, alpha=1 | 1,000 / 12,500 | 500 / 500 | 500 balanced |
| R2 .064, alpha=1 | 500 / 12,500 | 500 / 500 | 454 w0_p0_t1_g3 |

Thus 2,000/50,000 candidate queries, four percent, map to failed A1
rows on these four paths; three paths encounter them on every live
step. Two N=40 stress paths each give an eight-percent standardized
N=200 context overlay, but do not match the registered initial law;
one also uses an rr outside its labeled R2 grid. They are separately
labeled in the diagnostic and excluded from the four-path percentage.
These pilot/fixture decisions cannot estimate selection frequencies
under corrected W tables. There are no fires in these paths. Successor
contexts are covered by the static failure matrix, not by an invented
observed succession frequency. Joint unpublished-bin exclusions,
admission filtering and a possible balanced fallback cannot be inferred
from row marginals. Row failures alone never remove all 25 rules in the
matrix, but removal of every admissible score remains possible. The
pending survival-first issue is not resolved by this diagnosis.

### Options, price and recommendation

A1 dispatch took 20,164.934 seconds, 440,710.415 summed worker seconds,
240,110.423 trajectory seconds and 200,579.627 rescoring seconds. Its
24-worker launch delivered 21.855 effective workers. Both complete
service intervals, including the first attempt, total 21,172.095 seconds,
5.881 hours. The following costs scale actual matching A1 job costs,
then add that sunk service time and 1,200 seconds for the next
configuration test and cleanup/publication. They are not measurements
at the proposed settings and do not certify a pass.

| Option | Additional dispatch hours | Cumulative hours | Assessment |
|---|---:|---:|---|
| Only the 44 individually failed jobs, populations x8 | 3.382 | 9.597 | Cheapest, but leaves comparisons at mixed effort and does not renew the full sensitivity subset |
| Affected pair closure, 52 jobs, populations x8 | 5.497 | 11.711 | Repairs companions, still retains five old sensitivity triples |
| Recommended: affected pairs plus all nine sensitivity pairs, 67 jobs, populations x8 | 8.611 | 14.825 | Fixed whole-job replacement and renewed subset, with conditional-publication caveat |
| Whole family, populations x2 | 11.203 | 17.417 | Avoids failure-selected effort but gives fewer additional samples to the failing bins |
| Whole family, populations x3 | 16.804 | 23.019 | Uniform alternative with only 0.981 hours of scaling margin |
| Whole family, populations x4, or both lengths and populations x2 | 22.405 | 28.620 | Exceeds cumulative ceiling by 4.620 hours |
| Whole family, populations x8 | 44.811 | 51.025 | Exceeds cumulative ceiling by 27.025 hours |

Treating failed rows as unavailable has essentially zero estimator cost
but is not a sound minimal validation repair. A1's unavailable-bin rule
handles absence inside an accepted table domain; it does not waive a
failed estimate or the full-family gate. Removing a whole failed context
changes the effective policy class on many ordinary steps. The two
sensitivity failures do not demonstrate inadequate Lambda_F convergence
on unselected rows, since all numerical contrasts pass, but they do
demonstrate that primary continuation passes are not assured to replicate.
Discarding only the two observed sensitivity failures would hide that
evidence and leave unselected contexts unvalidated. The loader remains
unchanged and rejects the whole failed family.

Changing the binning or using a different continuation model might reduce
aggregation error, but changes the frozen evaluation model and needs a
new design and validation. Raising the publication count or excluding
high residual bins would alter coverage and the comparison class and is
not justified as a screen correction. No such redesign is smuggled into
the proposed effort repair.

Recommend the 67-job option as the smallest fixed repair that increases
per-bin effort substantially and renews the entire original sensitivity
subset. Eightfold populations are a declared effort choice with useful
budget slack, not a threshold selected to make an observed screen pass.
It replaces 49 primary jobs, all 1,690 scoring rows in those jobs, and
all 18 sensitivity jobs. The other 276 primary jobs remain exactly A1
estimated values with A1 provenance. The existing writer recomputes
ranking flags against the assembled comparator family. All primary rows received A1's settings; the
new subset receives the additional fixed schedule in proposed A3.
This mixed-effort publication explicitly requires the amendment and
operator approval. It is not authorized by A1's original uniform
replacement clause alone.

Selection by failure is adaptive even before rerun outcomes exist.
Independent fresh seeds, replacement of complete jobs including their
passing contexts, and a single fixed attempt avoid fitting repeatedly
to the same failed held-out observations. They do not remove selection
bias from the retained passing rows or provide nominal confidence after
screening. All intervals remain labeled empirical and exclude full-chain
bias. No inference about R1/R2 or statistical admission is made from this
selection. The fresh nine-pair flow contrasts and all original row screens
must pass. Additionally, every replaced primary or sensitivity row must
pass the original-versus-new Lambda_F contrast at the existing 90-percent
interval and five-percent span threshold. There is no option to keep an
old passing row when its replacement fails.

The recommendation projects 14.825 cumulative hours at measured
parallelism, 23.436 at half the throughput, and 32.046 at one-third,
which would exceed the ceiling by 8.046 hours. Approximately 10.58
effective workers are needed at the scaled per-job cost after reserves.
Higher particle counts increase peak memory and may change routing or
vectorized rescoring cost. The next configuration test must measure the
actual enlarged populations and both routes. A short test does not
guarantee full-length memory use. The operator should choose a worker
limit that fits memory as well as CPU limits; if the measured projection
misses the ceiling, report that gap and stop. No registered family was
launched to test this projection. More effort may still leave valid
failures. In that event the gate stays closed, and a further design or
budget decision would be needed.

### Prepared implementation, tests and report

`table_repair_a3.py` prepares the selected jobs with explicit new settings
and independent stable seeds. The review manifest has no committed pin
and cannot launch. It uses the existing production runner with automatic
publication disabled. The separate publisher verifies the old source
family and every fresh completion, checks selection closure, settings,
seeds and context equality, then publishes a full 13,750-row family with
both source provenances. It never relabels an A1 worker output as A3 code.
Failed replacements and contrasts remain failed. Registered loading still
requires all rows and the sensitivity family to pass. No exception is
added to `ProductionTables.require_production`.

No existing scientific module, runner, gate, compatibility record or
default estimator setting was changed in this task. The proposed effort
is opt-in through the new module. This preserves the prepared A2 work
and its compatibility dependency hashes. The frozen calibration is
unchanged. The additional diagnostic modules enter the eventual commit's
source identity, so final launch manifests must be generated from that
committed code, as usual.

Focused tests cover fixed kernel selection, fresh deterministic seeds,
all-context replacement, preserved sensitivity ratios and lengths,
unchanged thresholds including a boundary tie, missing/extra/context-
altered replacements, failed new estimates, the added original/new
contrast, high-coverage sparse-bin rejection and A2 dependency integrity.
The final full suite passed 323 tests with three existing expected
failures in 71.35 seconds. Twenty-two new tests include synthetic durable
publication through the real merge/writer/loader, tampered and missing
records, changed selection and rejection before opening registered
rerun outputs. The original v2.0 checks still pass. The proposed
repair itself was not run. Only read-only audits of registered table
artifacts and existing explicitly non-registered trajectories were used.

**Report for review:** the 717 failures and all 46 selected failures are
fully attributed to continuation residuals. Proposed A3 prepares one
67-job repair, with no screen relaxation and no assurance of clearance.
Its measured-cost projection is 8.61 added X2 hours, 14.83 cumulative
including prior service and reserves. No commit, network, X2 access,
registered rerun output or implementation of the two pending A2
decisions occurred. Files for review are listed in
`v3/A3_REVIEW_20260928.md`.

## 20. D23 approved A2 corrections, 2026-09-28

This section records the earlier D23 validation. Final review fixes and
recomputed gate denominators are in section 21.

### Decision, timing and implementation

The operator approved both changes as D23 before any registered rerun
manifest, job or output existed. The X2 chain remains paused. This work
used only local non-registered validation outputs and the previously
authorized calibration. It neither changes nor executes proposed A3.
Earlier sections that call these two decisions pending are historical.

`V3Model._choose` keeps the existing cohort-risk equality and first
restricts survival-first selection to `risks == risks.min()`. Available
W scores select among those minima exactly as before. If every minimum
lacks a score, it returns the first minimum in declared rule order.
The constructor requires balanced at index zero, so this chooses balanced
when it is a minimum and the first other minimum otherwise. It never
invents a W score. Admitted, non-survival-first allocation retains A1's
balanced fallback. The cohort calculation, eligibility, floors, rollout,
yield comparison and transition code are unchanged.

This case records `survival_first_scores_unavailable=true`,
`selection_reason=survival_first_scores_unavailable`, the existing total
`unavailable_rule_count`, and `minimum_bound_unavailable_count`.
It records `balanced_fallback=false`, even when balanced is the selected
minimum. The override log gets the same reason, counts, selected rule
and log risk, with `reproduction_floor_overridden=false`. The existing
precedence-override flag remains false. Each rerun now publishes its
override records and the separate aggregate
`continuation_availability.survival_first_scores_unavailable_steps`.
The existing durable completion hash covers these fields. No completion,
partial-output or evidence-index rule changes.

G3.3 now scans the complete verified R2 family for fired successions.
Zero fires with R2 evidence yields `status=not_testable`, `passed=false`,
zero checked/fired counts and no zero-failure bound. Missing R2 evidence
still fails. The full census streams its records. One or more fires
still requires every succession to pass the existing checks. Aggregation
recognizes only the exact zero-fire record as the D23 exception for R2
fire-rate citation. It is never a pass or clearance through gate 3.
R2_cliff's existing requirements, including G2.2 and G4.2, are unchanged.
Missing checks, duplicate checks, a forged zero-fire record, other failed
checks and non-registered validation artifacts receive no exemption.

The explicit A2 compatibility record moves `integration.py` from the
unchanged dependency set to the approved online boundary. Its old
normalized-source SHA256 is
`b38fd16eba6797a351ad055935c1b38930b5b4b5d15b1e2c53bcc80de24d84fe`;
the amended hash is
`c8a69a83af5b008a480301a66b347ab93fd4faeb02305b9a0bbcab003d56f511`.
It also pins the amended runner's diagnostic output boundary. An AST
test verifies that only `_choose` and `step` changed in `integration.py`
relative to 34ffbfe9. The offline estimator, kernel, continuation, scoring,
policy class, calibration and table-producing mechanisms remain unchanged
and hash-checked. All table completeness and stability checks remain
binding. The completed failed A1 publication is still rejected. The
calibration compatibility record and proposed A3 repair are unchanged.

### Real-run validation and non-interference

`python -B -m v3.d23_validation prepare` freezes the same six job IDs,
seeds, configurations, calibration and sparse probe/fixture tables used
in section 18. The real production runner performs its configuration
test and completes all six 500-step jobs with the observer on. The final
configuration test chose two workers with one numerical-library thread;
the six-job dispatch took 145.484 seconds. Paired comparisons use that
measured worker limit. Effective OpenBLAS thread counts were verified as
one. An earlier diagnostic pass used at most four workers. Both are
inside this task's twelve-worker ceiling.

`python -B -m v3.d23_validation compare --workers 4` launches each job
under isolated 34ffbfe9, amended observer off, and amended observer on.
The measured two-worker limit still applies. The baseline snapshot's
files are checked against the section 18 source hashes. These are
non-registered sparse probe tables and FixtureTables, not the failed
registered A1 family or proposed A3 estimates.

For all six jobs, removing only packed gate evidence from the observer-on
result gives byte-identical canonical scientific output to observer off.
This includes all new D23 diagnostic fields and override records. The
original RNG return values, call identities and counts also match, as do
the state arrays after every step. The observer-on result additionally
matches the real runner's durable result byte for byte. State audits
cover ages, welfare, traits, propensity bank, stocks, novelty window,
sample counts and H_N. The proof is empirical for these jobs; the source
boundary and unit tests establish the intended selection scope.

The historical comparison removes only additive D23 records when
comparing with 34ffbfe9. Each first difference is checked against the
same pre-action state, risk vector and score-availability vector. Every
such difference satisfies survival-first with all minimum-risk scores
unavailable. Independently, on every amended trajectory, the audit
recomputes the old chooser on the same state and rejects any changed
choice outside that condition.

| Job | rr | alpha | Initial N | Tables | First difference from 34ffbfe9 | D23 steps | Choices different from old chooser on the same state |
|---|---:|---:|---:|---|---:|---:|---:|
| R1 | .064 | .5 | 200 | Sparse probe | 25 | 475 | 475 |
| R1 refinement | .063 | 1 | 200 | Sparse probe | 25 | 475 | 475 |
| R2 stress | .055 | 1.5 | 40 | Sparse probe | 0 | 500 | 476 |
| R1 | .060 | .5 | 200 | Fixture | None | 0 | 0 |
| R1 refinement stress | .061 | 1.5 | 40 | Fixture | None | 0 | 0 |
| R2 | .064 | 1 | 200 | Fixture | None | 0 | 0 |

The N=40 jobs are explicit stress cases, and .055 is outside the
registered R2 rr grid. They supply mechanism coverage, not registered
frequency estimates. The 1,450 special-case step records match their
override and per-job counts. Of those, 1,426 change the chosen index
relative to the old chooser on the same amended state. The other 24
choose balanced because it is already a minimum, with the corrected
distinct reason. The refinement sparse-table job retains 25 admitted
balanced-fallback steps; the other jobs have none. There are no changed
choices outside the D23 condition. Later differences between corrected
and baseline trajectories follow from the earlier action correction.

### Gates, tests and report

The committed-form index tool reads the completed validation root and
hashes its manifest, outputs and durable records. Running the real gate
CLI on that index produces the following results:

| Check | Result and evidence |
|---|---|
| G1.1 to G1.5 and G3.1 scenarios | All six before checks pass |
| G3.1 sample | 200 reviews, zero failures |
| G3.2 | 73 R2 reviews, zero failures |
| G3.3 | not_testable, two R2 runs, zero fired successions, no bound |
| G4.3 | 120 periods, zero failures, compared with 58 violations before D23 |
| G2.2 and G4.2 | Fail because the six-job validation lacks the required R2 grid and seeds |
| G4.1 | Fails its sample-size requirement: 1,000 R2 steps available, 10,000 required |

Of the 120 periods, 116 are survival-first. The G4.3 zero-failure bound
reported by the checker is 0.0246554 for this validation sample, not a
claim about an unrun registered family. The corresponding reported bounds
are 0.0148670 for G3.1 and 0.0402068 for G3.2. All available Theta formula
checks agree; this does not waive G4.1's frozen sample count. There is no
schema mismatch. The nonzero CLI exit is expected for the deliberately
incomplete grid and sample. All three citation flags remain false because
these are non-registered validation artifacts.

No succession fires naturally in these six jobs. Existing forced-fire
observer tests retain their transition coverage, and D23's synthetic
gate tests exercise zero, one passing and one failing succession. The
new selection tests cover unique and tied minima, available and missing
scores, balanced inside and outside the minima, exact W ties, admitted
fallback, state reset, diagnostic reasons and floor-preserving records.
The full repository test selection, including v2 conformance, passed
337 tests with three existing v2 expected failures in 92.34 seconds.

The authoritative records are under
`v3/runs/a2_d23_validation/final/`. `comparison.json` binds the 18 paired
outputs and their audits. `validation.json` records counts and tests.
The ZIP and its manifest preserve the real runner's outputs, completion
records, configuration measurements, index and paired results. The
original section 18 archive retains the identical probe tables and
baseline source hashes. Loose duplicates and temporary test trees are
excluded from the explicit A2 commit list.

**Report for review:** both D23 changes are implemented and validated.
G4.3's 58 violations become zero. Recording is non-interfering on all six
amended jobs; historical differences start only at the approved condition.
The full suite passes. A2 remains uncommitted, A3 remains a separate
unchanged proposal, and no registered rerun output existed or was read.
No network or X2 access occurred. Files for the operator's commit are
listed in `v3/A2_COMMIT_FILES_20260928.md`.


## 21. Final A2 review corrections, 2026-09-28

### Scope and public record

The independent review found checker and provenance defects; it accepted
the observer mechanism, D23 selection, durability and dependency hashes.
This correction changes evidence and validation, not the scientific
executor. `integration.py` is unchanged from the tested D23 version.
The full cap* implementation is unchanged, including top-of-grid and
undefined point/bootstrap cases. Their separate decision remains pending.
The table repair is still proposed, not adopted, and was not run.

A2's first part was written after the A1 tables started and before any
registered rerun manifest, job or output existed. D22 approved recording
because the A1 rerun output schema lacked evidence for G3.1's sample,
G3.2, G3.3, G4.1 and the action part of G4.3. D23 was written after the
A1 family completed and its failed screens were read: 717 not_estimable
rows, 671 primary and 46 through sensitivity. No registered rerun
manifest, job or output has ever existed. The rerun step was paused
before dispatch. A2 is committed before any rerun output is read.

The pre-registration now contains the complete public gate rules without
requiring a private W7 document. Its header names D1 through D23. Section
9's cliff criterion and P3 explicitly distinguish the point rule from the
full citation gates. G4.2's two standard errors use pooled run counts of
4 rr times 75 = 300 per alpha/capability cell. The standalone checker is
`v3.gates`; the v2.0 validator is unchanged. The proposed A3 text was moved
out of the pre-registration into `v3/A3_REVIEW_20260928.md`. Section 19
retains the diagnosis facts with A3 explicitly proposed, not adopted.

### Checker and evidence corrections

Every step now records `population_before`. A living-start step that
ends in extinction remains in both G4.3's action scope and G4.1's living
sampling frame. G4.3 checks every living-start action in an above-bound
period or marked survival-first, including mid-period survival-first
inside a period that was initially admitted. Required missing action
evidence fails. The recorded pre-step population is checked against the
initial population and preceding post-step count.

Every period-start step records a `period_start` object containing all
living ages and integer welfare, including admitted and empty starts.
The checker independently recomputes the exact rational cohort bound,
checks its outward-rounded displayed float, and verifies the exact
reserved fraction and admission at 1/1000. It also checks conservation
of the epsilon ledger and zero statistical alpha. An exact epsilon tie
is admitted; testing uses `CohortBound` and `ProtectionPeriod.audit()`
values that the recorder can actually emit. The constructed exact tie
is a boundary fixture; ordinary life-table products are dyadic and cannot
equal 1/1000 exactly. A recorded .001 float alone is not an exact bound.
Post-extinction period starts are counted separately and excluded from
the above-bound period share's denominator.

For actions, the candidate IDs must equal all 25 frozen rules in their
declared order. The checker independently reconstructs their actual
welfare shares from the recorded bins, including full-welfare stress.
Missing bins may use a reduced fallback only in explicit fixture mode;
that fallback includes stress share 1. No registered path uses it. The
new non-tie fixture shows strictly smaller risk under full welfare than
balanced at age 20 and welfare 500; a balanced action fails even when
the agent dies during that step.

G3.1 compares every independent exp(-rho*t)/fsum plan value with its
reported beta**t value at absolute tolerance 1e-10 and relative tolerance
1e-8, then applies the strict rule to the reported values. Independent
ordering must agree when its gap exceeds the same tolerance. This avoids
flipping a reported tie through harmless arithmetic differences without
accepting a value mismatch beyond tolerance.

The recorder reports Gamma per available paired yielding plan in epoch
units. The checker independently computes disrupted and undisrupted W,
checks reported Gamma, and checks the offered comparison against both
disrupted W and undisrupted W minus that reported Gamma. It does not
manufacture Gamma from the value it is trying to verify. G3.2's n counts
reviews with at least one checkable paired yielding comparison, including
failed checkable reviews. Holds without such a comparison do not count.
Zero checkable reviews fails. Every undisrupted yielding flow array is
recorded even when the disrupted endpoint is unavailable. Null endpoint
values and Gamma are explicit and never replaced.

G4.1 retains the frozen hash identity and salt, but takes its 10,000 steps
from living-start R2 steps. It checks every absorbed-start R2 step
separately and reports both counts. Missing population evidence fails
rather than shrinking the sample frame. No sample-size threshold is
lowered. Regression tests cover last deaths, absorbed starts, a genuinely
nonminimum action, mid-period survival-first, exact ledger boundaries,
missing candidate classes, near ties, double disruption subtraction and
undefined cap* in bootstrap resamples.

### Integrity, clean test harness and commit identity

`verify_registration` enumerates every path in `source_manifest`, not
just Python files and one named JSON record. It rejects uncommitted
identity files even if ignored by Git. Tracked modifications remain
blocking. Approved hashes were explicitly regenerated for this reviewed
change. `refresh_boundary()` only prints and returns proposed hashes;
it cannot write an approval record.

The A1 exception requires both seal
`f6fcb1fdd787e92164f029e8fd0098a71d94c47b5ee3b37b96adb91a63a8cfd7`
and file SHA256
`56db71633a0f4710692e3354e3bc2fb5829286abbfa59e61609bd3f8cf6fcb3c`.
It also verifies the producer, calibration, design and dependency hashes.
A parsed document without the exact file hash cannot use the exception.
The genuine pinned publication was checked locally: compatibility matches,
and registered loading still refuses its failed sensitivity screens.
Thus the exception currently admits no table to a registered run. A
repaired family will require a new reviewed record.

Validation reuses the exact original sparse probe bytes, without
re-stamping their source or changing job IDs, seeds or estimates. A
separate helper recognizes only that pilot fixture's exact seal and file
hash, and the loader calls it only for non-registered fixture loading.
It cannot authorize a registered table or bypass registered source checks.
This preserves the paired validation inputs while removing the former
broad A1 table-source exception.

The chosen commit set includes `a1_screen_diagnosis.py` and
`table_repair_a3.py` as inactive review tools. This records their presence
in code identity and does not adopt the proposed repair. All 74 files
scanned by `source_manifest()` are either already committed or explicitly
listed in `A2_COMMIT_FILES_20260928.md`. The final manifest and evidence
use that exact set, recorded in `commit_source_files.json`; no omitted
Python modules contribute to the validation identity.

The v3 tests import a scoped temporary-directory fixture, so normal
pytest temp defaults cannot escape the artifact writer's authorized root.
The optional legacy plugin also avoids constructing pytest's external
temp directory before returning its scoped path. The full suite required
no --basetemp option: 349 passed, three existing expected failures, in
81.70 seconds. The first attempt exposed the legacy plugin's dependency
on an inaccessible external pytest temp root; that test-harness defect
was fixed and the full suite rerun. An isolated copy of the exact 74
source files and only the committed test fixtures passed all 89 focused
review, gate, recording and D23 tests in 10.48 seconds. Runtime scopes and
fixture files are part of the explicit commit list; temporary copies are
not. No production write-scope check was relaxed for tests.

### Final validation and report

The authoritative outputs are under `v3/runs/a2_review_validation/final/`.
The before gate CLI passed G1.1 to G1.5 and G3.1 scenarios. The real runner
completed the same six 500-step jobs after its configuration test selected
four workers with one verified numerical-library thread each. Dispatch
took 109.429 seconds. Paired comparisons use that measured configuration.
No registered rerun was generated or opened.

The corrected after-gates pass G3.1 on 200 sampled reviews and G3.2 on
three checkable R2 reviews containing 150 paired yielding plans. Of the
73 R2 reviews in the common sample, 70 have no checkable comparison. The
G3.2 nominal zero-failure bound is therefore 0.631597, not the earlier
bound computed incorrectly from 73. Across the full six-job family,
only six of 300 reviews have eligible paired comparisons, 300 plans.
All 16,500 yielding alternatives now have recorded undisrupted flows,
including unadmitted and unavailable candidates. These counts limit the
empirical non-interference and cost evidence; this is not broad natural
succession coverage.

G4.3 passes 120 exact period checks and 2,900 living-start action checks,
with zero violations, compared with 58 before D23. Of those periods, 116
are above-bound, a share of 116/120. None starts after extinction in this
sample; unit fixtures cover the exclusion and the last-death step.
G3.3 is not_testable with zero fires and no bound. G4.1 has 1,000 living
R2 steps and no absorbed-start R2 steps, with no formula mismatch, but
cannot clear its 10,000-step requirement. G2.2 and G4.2 cannot clear the
incomplete R2 grid. There is no schema mismatch. All citation flags are
false because these are non-registered validation artifacts.


On the final source, all six observer-on/off comparisons produced
byte-identical canonical scientific results after removing only gate
evidence. Original RNG return hashes and counts and every audited state
array also matched. Each observer result matched its real-runner durable
result. The separate 34ffbfe9 comparisons first differed at steps 25, 25
and 0 on the three sparse-probe jobs, each at the approved D23 condition
on an identical pre-action state; the other three jobs had no scientific
difference. No choice differed from the old chooser on the same state
outside that condition. There were no natural fires. One separately
labeled forced-fire fixture also matched scientific results, original
random draws and state arrays with the observer on and off.

The observer is designed not to alter values, decisions or random draws;
this is evidence from six paired 500-step jobs and one stress fixture,
not an unrestricted proof for every trajectory. Only six of 300 real
validation reviews had eligible undisrupted comparisons, including three
of the 73 R2 reviews selected for G3.2. Counterfactual computation on
unavailable plans now occurs as well, and its complete flows are retained.
The final evidence envelopes range from 220,718 to 664,855 bytes per job.
Concurrent paired elapsed differences range from 3.85 to 7.59 seconds;
they are not controlled overhead measurements or X2 budget measurements.
The earlier section 18 cost estimates describe the earlier recording
schema and should not be treated as fresh measurements of this version.

The exact validated source identity is
`a904e8dbbb3d8be424dffdb8d96eab2b8f2f8c9f56db04ff3a9a5b6023acc6d9`.
`commit_source_files.json` enumerates all 74 contributing files. The
compatibility and complete gate reports, all 18 paired outputs, raw
state/RNG audit hashes, real outputs, completion records and configuration
measurements are retained in the final archive, 7,183,552 bytes, with
individual file hashes and a verified archive hash. The untouched original
probe remains in the earlier A2 archive. The executor, A1 diagnosis tools
and proposed-repair module were also hash-compared with the previous D23
validation. The pending `cliff_checks` implementation was AST-compared
with that snapshot and is unchanged.

**Report for review:** all requested checker, evidence, integrity and
text fixes are prepared. The full suite passed 349 tests with three
existing expected failures; the isolated clean-file-set check passed 89.
Before gates passed, all six recording comparisons matched, and G4.3
passed 120 periods and 2,900 action checks with zero violations. G3.2's
correct denominator is three, not 73. The small validation still cannot
clear the complete grid or 10,000-step requirements. The cap* decision
and proposed table repair remain undecided. No registered rerun output
existed or was read. No commit, network or X2 access occurred.


## 22. D24 censored gates and adopted A3, 2026-09-28

### Decision timing and scope

D24 was implemented after the registered A1 table family completed and
its screens were read, including 717 not_estimable rows: 671 primary
failures and 46 propagated through sensitivity. Before this amendment
was written, no registered rerun manifest, job or output existed. None
was generated or read here. Only the labeled local validation family
was executed. The rerun step was paused before dispatch. No commit,
network or X2 access occurred.

A2 remains a complete public gate and recording specification in section
13 of the pre-registration. Its D24 addition settles the formerly open
censored-cap* case. A3 follows it as an adopted amendment, preserving
the prior fixed selection and effort. Sections 19 and 21 describe the
earlier proposed status and remain historical diagnosis and review
records, not pending decisions. The v2 validator remains unchanged.

### Censored cliff values

`gates.cliff_checks` retains the numeric tested value or null in its
legacy cap_star field and adds explicit cap_star_labels. A grid-top
value is "5.0 or higher"; no capability reaching pooled fire rate 0.5
is "below 1.2". Internally bottom is below every tested value and top
is above every uncensored tested value. Equal censoring is flat. No
infinity is serialized in canonical JSON. Both point ordering and all
2,000 fixed-seed bootstrap resamples use this order. The report includes
top- and bottom-censored resample counts; no resample is discarded.

The G2.2 nonincrease and strict net decrease requirements, and support
of at least 90 percent for every adjacent strict decrease, are unchanged.
G4.2 checks all alphas with a tested cap* below 5.0, requires every one
to pass and at least one to be testable, and reports other alphas with
the censoring reason. Its two-standard-error formula still uses pooled
run counts of 4 rr times 75 = 300 per cell, not 75 seeds. No defined
cliff threshold or separation requirement is relaxed.

`test_v3_d24.py` covers v2's (5,3,2.5,2,2) sequence, bottom censoring at
high alpha, all-top and all-bottom flats failing net decrease, censored
bootstrap resamples, mixed testability and no testable alpha. Existing
unsupported-decrease and cap-increase negatives remain binding.

### Adopted repair, order and stop

The 67 jobs, seeds and full configurations were compared exactly against
the previously prepared review manifest, ignoring list order only. They
are identical. All 49 selected rule/rr pairs, 49 primaries, 18 sensitivity
jobs, eight-times-A1 populations, lengths, routes, grids and screens
remain unchanged. The retained 276 A1 jobs keep their actual provenance.

`table_repair_a3.difficulty` takes the maximum signed excess divided by
its positive limit across every applicable numerical screen and scoring
context of a source job. Lower-bound screens reverse the numerator.
Each sensitivity contrast contributes to both original jobs of its pair;
FV's pre-cloning survival fraction contributes nothing because it is not
a gate. `prepare` sorts by decreasing score and ascending source job ID
for ties. The top job is w1_p1_t1_g3 at rr .066, primary, normalized
excess 3.8274280261. Next are w0_p0_t1_g3/.066 and balanced/.057. The
complete ordered list is frozen in the manifest and compatibility policy.
This is an execution order, not a new seed or statistical selection.

The required `A3-first-failure` runner option checks every durable job
before dispatching a replacement worker. It checks all row screens,
the original/new flow contrasts, and each fresh sensitivity contrast as
soon as both jobs are complete. A failure writes `screen_failure.json`
and a durable event identifying the failing job, row, screen or contrast,
and paired job when relevant. Dispatch stops and the existing process
termination/join/kill procedure interrupts in-flight jobs. Completed
outputs remain valid completions; incomplete work is never published.
The latch survives ordinary control resets and resume, and the publisher
refuses it. Configuration-test outputs are discarded and are not screened
as scientific estimates. Failures cannot trigger extra effort or retries
until pass. Ordinary interrupted work without a scientific failure may
restart from its original seed under the frozen existing deadline.

Tests cover failed rows, failed original/new contrasts, a sensitivity
pair whose individual rows pass, exact threshold ties, first-failure
interruption with another process active, preserved completion, no later
dispatch, blocked resume, deterministic order, unchanged seeds, and a
changed order, effort, setting, seed, source hash or stop option refused.

### Mixed-family compatibility and publication

The new committed `table_compatibility_A3.json` pins the genuine A1 file
SHA256 56db71633a0f4710692e3354e3bc2fb5829286abbfa59e61609bd3f8cf6fcb3c
and seal f6fcb1fdd787e92164f029e8fd0098a71d94c47b5ee3b37b96adb91a63a8cfd7,
its original producer 34ffbfe9 and code identity, all 343 source output
hashes, source configuration identities, the exact 67 replacement IDs
and order, and the remaining 65,227-second ceiling. It is included in
source_manifest and verify_registration's committed-and-clean check.

The provenance publisher verifies both durable families, reconstructs
every enlarged job and seed, assembles every row, and applies all original
and additional contrasts. It does not write the final publication if any
row or contrast fails. It validates a separately named unpublished
candidate, then writes the final table and its sealed sibling
`.compatibility.json` receipt. That receipt binds the exact new table
file and seal, the committed producing code identity and commit, the
manifest, the 276 retained hashes and 67 fresh job/output identities.
The loader requires it even for its own code identity. Use the same
combined producer commit and preserve both files together. No future
publication hash is guessed. A2's separate exception continues to pin
only the failed original A1 file; it admits no table to a registered run.

Synthetic publication tests exercise both families without estimating
anything. They reject missing or changed completions, wrong selection,
failed rows, missing receipt, re-stamped bytes, extra retained or fresh
jobs, wrong producer code or commit, and failed sensitivity status even
when the compatibility receipt matches the bytes. Scientific table
checks are not bypassed by either compatibility record.

### Cost and launch review

The recommendation's measured-cost projection is unchanged: 8.611 added
X2 dispatch hours at A1's effective throughput, 14.825 cumulative hours
including both prior service intervals and 1,200 seconds of new
configuration and cleanup/publication reserve. Half that throughput
projects 23.436 cumulative hours. The remaining manifest deadline is
65,227 seconds under the cumulative 24-hour ceiling. These are planning
extrapolations; enlarged populations can change memory demand or routes.
Early stop can save work after failure, but gives no guarantee of clearance.

`A2_RUN_ON_X2.md` now gives the complete audit, manifest, service-leased
launch with llm down and configuration test, explicit provenance
publication, and new-pin rerun sequence. The publisher's new sidecar is
required with the table. The combined commit list contains A3 code and
the exact current source file list. No estimate or production launch
was performed to prepare these instructions.

### Final validation and report

Validation records are under `v3/runs/d24_validation/`. The full suite
passed 376 tests with three existing expected failures in 92.43 seconds.
The before gates passed G1.1 to G1.5 and G3.1's fixed scenarios using the
unchanged registered calibration. All 67 reviewed jobs and seeds are
preserved exactly. The source identity and individual file hashes are
recorded in `commit_source_files.json`. A fresh explicit source/fixture
copy passed 137 clean-checkout tests in 22.83 seconds, with default pytest
temporary directories; the final D24 test file passed all 20 cases after
the additional top-to-bottom/no-testable-alpha boundary was added.

The real runner repeated the same six non-registered 500-step jobs. Its
configuration test selected two workers with one numerical-library
thread each. Dispatch took 153.827 seconds. The paired comparison used
the same measured two-worker setting, running baseline, observer-off
and observer-on versions of every job. All six observer comparisons
matched canonical scientific bytes after evidence removal, original
RNG draw hashes/counts and audited state arrays. They also matched the
real durable runner outputs. No natural succession fired; the forced
succession stress fixture passed in the full suite. The first differences
from 34ffbfe9 remain steps 25, 25 and 0 for the sparse-probe jobs, each
at D23's approved trigger on the same pre-action state, and none for
the other three jobs. Choices outside the D23 trigger remain unchanged.

The after-gates pass G3.1's 200-review sample, G3.2's three checkable R2
reviews with 150 paired plans, and G4.3's 120 exact periods and 2,900
in-scope actions with zero failures. Of the periods, 116 are above-bound.
G3.2 still has only three checkable reviews among 73 sampled R2 reviews,
so its nominal zero-failure bound is 0.631597. G3.3 is not_testable with
zero fires. The 1,000 living R2 steps and incomplete grid cannot clear
G4.1, G2.2 or G4.2. These are expected sample/grid limitations, not schema
mismatches, and no registered result is claimed citable.

Final source identity:
`6c87072644b26ff8a545144771f91a4dbe598623dce7c0586a5390dbda331942`.
All 76 contributing files are enumerated. The executor, observer,
offline estimator, scientific table design and kernel are byte-identical
to the section 21 reviewed versions. The final archive has 80 verified
files and 7,218,219 bytes; SHA256:
`4114503ef92dcc095b9dc5756f845c0dbcd2155aa0d51d74b8440bb7a29758d6`.
Earlier section 21 records retain their original source identity.

**Report for review:** D24 and adopted A3 are prepared, including the
fixed order, tested first-failure interruption and explicit mixed-family
compatibility. Full suite: 376 passed, three existing expected failures.
Before gates passed; six recording comparisons matched and G4.3 had
zero violations. Review the required sibling compatibility receipt and
the failure latch, which cannot be cleared by ordinary resume. The
14.825-hour cumulative projection is a planning estimate, not guaranteed
clearance or a timing measurement at the new populations. The combined
commit list and launch note are ready. No repair estimate, registered
rerun output, commit, network use or X2 access occurred.


## 23. Second A2+A3 review corrections and final validation, 2026-09-28

### Scope and timing

This section supersedes section 22's final source identity. Sections 19,
21 and 22 retain the diagnosis and earlier validation as history. A2's
first part followed reading the registered calibration and first table
family, after the A1 tables started. D22 paused the rerun step before
dispatch for the evidence-schema gap. The D23 and D24 texts followed
completion and screen review of A1. The genuine A1 family fails the
registered table check: 717 not_estimable rows, 671 primary and 46 via
sensitivity. No registered rerun manifest, job or output existed when
these second-review corrections were written. All local outputs below
are labeled non-registered validation artifacts.

### Fixed replacement identities and family stop

`simulation/v3/table_compatibility_A3.json` pins the 67 replacement job
IDs and seeds as well as the exact calibration argument
`v3/runs/registered/v3_rerun_calibration.json`, relative to `simulation/`.
They are the same identities and seeds in the section 22 reviewed job set.
A path such as `./v3/...` cannot create a new seed namespace: both
validate_plan and publication refuse it. No scientific setting, seed,
dispatch order, original screen or added contrast changes in this review.

The failure record is now family-scoped at
`simulation/v3/runs/A3_families/<policy-digest>/failure.json`, where the
digest hashes the committed policy's canonical JSON. Launch and publish
both refuse it. Before llm down or configuration_test, preflight acquires
the family preflight lease, checks the latch, registers the current root,
and screens validated durable completions from every recorded root.
This catches a prior failure even if a process died before writing its
per-root latch. Each new failed completion also writes the family latch.
Active dispatch checks it before replacement work. The completed-output
screen and original/new and fresh sensitivity contrasts are unchanged.
A direct publication failure also records the family failure. Completed
outputs remain durable; no failed family is published as registered.

The A3 receipt requires its producing commit to be an ancestor of HEAD,
plus exact current code_identity equality. Later documentation and results
commits can load it; a changed source identity, unrelated producer, wrong
receipt or wrong table cannot. This does not relax a table screen. A3
itself changes no allocation or yield computation. The tests exercise
changed calibration spelling and seeds, a new-root retry, refusal before
service shutdown/configuration, and a descendant-commit load with the
same code. Both compatibility records remain in the registration clean
and committed file check.

### Physical transition evidence and independent survival-first scope

The executor now delegates its unchanged transition function through a
pure observation hook. The recorder captures each yielding plan's and
fired transition's four integer stocks before and after, institutional
drawdown units, capability gap, six-channel action and original rounding
draw. It does not sample a new transition draw. G3.2 recomputes the load,
buffer, clipping and randomized grid rounding from those inputs, verifies
the actual decrement and unchanged other stocks, and checks the gap
against the review's incumbent and successor capabilities. It then checks
Gamma per plan and once-counting in the offered comparison values. A
zero Gamma cannot conceal omitted disruption. A real observer stress test
replaces the executor drawdown with an identity operation; the gate
rejects that evidence even when the offered comparisons remain consistent.
Reduced grid tests include zero stock and rounding boundaries.

The recorder supplies ages_before, welfare_units_before, action, summary
bins and the frozen 25 rule IDs at every living-start step. This replaces
the former flag-dependent evidence scope inside admitted periods. G4.3
independently recomputes the remaining-window active cohort bound on all
such steps and checks the survival_first flag, then checks the minimum
per-rule first-action cohort bound whenever required. Last-death steps
remain included. Missing arrays or a falsely unset flag fail. The
period-start common floor certificate is identical for all admissible
rules; a rule's first-action-conditioned welfare path can yield a different
bound for survival-first choice. Thus an admitted period can require
survival-first at a later step when the recomputed active bound exceeds
epsilon. This distinction reconciles pre-registration section 3 with D23.

The universal cohort recording added 100 steps with 71,704 published
compressed bytes across six jobs, 11,950.7 bytes per job on average. Holding
this small family's occupancy mix fixed projects 297,571,600 extra bytes
for 24,900 jobs. If all 500 steps required the newly added evidence, using
the observed 717.04 bytes per added step projects 8.927 GB instead. Neither
is a registered-family population forecast. The exact per-job counts,
agent observations, compressed and raw bytes are in
`simulation/v3/runs/second_review_validation/storage_cost.json`. The
comparison retains the new transition evidence on both sides and removes
only the newly added admitted, non-survival-first step fields. The scope
limit identified in review is removed rather than accepted.

### Public definitions and cost and deadline

Amendment A2 states the complete gates, nominal zero-failure bounds,
bootstrap support as the share of all 2,000 strict-decrease resamples,
beta = exp(-rho), and G4.2's equality at the two-standard-error limit.
A correctly computed interior cap* implies its next capability has rate
strictly below 0.5. D24 settled the case D21 left open before registered
rerun evidence existed. The standalone checker is v3.gates; the v2.0
validator remains unchanged. D22's real-run evidence check, D23's correction
and the small number of non-fixture paired reviews are stated explicitly.

A3 keeps every existing screen unchanged and adds the stricter original-
versus-replacement Lambda_F contrast using the existing five-percent-of-
span rule. That added contrast also triggers the stop. The survival
fraction route screen concerns plain independent-run survivors through
the measurement window, which must be at least one half. It does not
apply that threshold to FV's pre-cloning survivor fraction.

The measured prior service total is 21,172.095 seconds, about 21,173.
The fixed job population increase projects 8.611 added dispatch hours
and 14.825 cumulative hours with the 1,200-second reserve; half throughput
projects 23.436 hours. Configuration must project remaining work plus
reserve within the remaining deadline, initially requiring at least
10.581 effective workers under the eight-times worker-cost extrapolation.
The hard remaining deadline is 65,227 seconds; an optimistic extrapolation
does not extend it. These remain planning costs, not measurements at the
A3 populations, and no repair estimate was run.

### Final validation and report

The final source identity is
`f03021f88c53e0331d6d825f26663980f77a98d1e15c258f386acfc2c1f7b629`.
All 76 contributing source files are enumerated in
`simulation/v3/runs/second_review_validation/commit_source_files.json`.
Every contributing module and compatibility policy is either already
tracked or explicitly in the combined commit list. The service preflight
change is included in the approved boundary, whose hashes were explicitly
regenerated after the final edits. The offline estimator, table semantics,
scientific kernel and calibration remain unchanged.

The full suite passed 391 tests with three existing expected failures in
126.27 seconds. All 151 focused cases passed in 33.08 seconds. The six
before gates passed G1.1 to G1.5 and G3.1 scenarios using the unchanged
registered calibration. An updated structural test verifies the new
observation hook is a pure delegation with identical arguments, then
inlines it to prove the executor's other methods remain unchanged outside
the previously approved selection and step diagnostics.

The real runner repeated six non-registered 500-step jobs covering the
same R1, refinement and R2 validation configurations and seeds. Its
configuration test selected four workers with one numerical-library
thread each. Dispatch took 119.726 seconds. All six observer-on/off pairs
matched scientific results, with evidence removed, and original random
draws, state hashes and choices. They also matched the real runner's
durable outputs. No natural succession fired; the forced-succession
stress fixture passed. The first differences from 34ffbfe9 were steps
25, 25 and 0 for the three affected sparse-probe jobs, all at D23's
approved condition on identical pre-action states; the other three had
no difference. No choice outside that condition changed.

G3.1 passed its 200-review sample. In validation, G3.2 had three checkable
reviews (nominal bound 0.63), with 150 paired plans among 73 sampled R2
reviews. Across all 300 non-fixture reviews, only six had eligible paired
undisrupted comparisons, so this remains a narrow exercise of that path.
G4.3 passed 120 exact period certificates, all 3,000 living-step active
bounds and flags, and 2,900 required minimum-bound actions with zero
violations. The 116 above-bound periods exclude post-extinction starts.
G3.3 was not_testable with zero fires. G4.1's 1,000 living R2 steps and
the incomplete grid cannot clear G4.1, G2.2 or G4.2. These are sample/grid
limitations, not schema mismatches. No registered result is citable from
this validation.

The full observer took 6.436 additional local seconds per job on average
(range 3.824 to 7.733), including paired undisrupted replays. These are
concurrent-job timings, not an isolated measurement of cohort recording.
At A1's measured table-phase effective throughput, that mean projects
2.037 extra X2 wall hours over 24,900 jobs. This is a labeled planning
factor, not a measured X2 rerun result. The extra cohort storage is
reported separately above and in storage_cost.json.

The final machine-readable record is
`simulation/v3/runs/second_review_validation/validation.json`, SHA256
`0fed15f63bb936cd5289f875e4f3fe41894181473d63ff27210e516a58edf9ae`.
The archive
`simulation/v3/runs/second_review_validation/second_review_validation_records_20260928.zip`
contains 81 hash-verified files, 7,875,931 bytes, SHA256
`26eb3625255b17d3c0874a0219a139edd95168b511b8e130b7370145b010ac18`.
It preserves the paired outputs, original RNG/state audits, runner records,
configuration measurements, before and after gates, evidence index,
compatibility validation, fixed review manifest and storage accounting.
The archive manifest lists every member's hash. Older archives retain
their original identities and are history, not the final validation.

**Report for review:** All second-review findings are addressed. The
repair IDs/seeds and canonical path are pinned; failure refusal is shared
across roots and precedes configuration/service work; a compatible table
survives later commits only with unchanged source identity. Physical
transition checks reject omitted disruption. Universal living-step cohort
recording removes the G4.3 flag-dependent scope limit. Full suite: 391
passed, three existing expected failures. Before gates passed, six
recording comparisons matched, and G4.3 reported zero violations. Review
the fixed family latch path and literal calibration argument in the launch
note. No commit, repair estimate, registered rerun, network or X2 action
was performed.

## 24. A4 validated continuation support, 2026-09-29

Adopted by D30 after blind double certification. A4 replaces A1's
point-estimate continuation residual screen with interval tests on fresh
validation data, and publishes only the cells that pass. A3 is superseded
and does not run. This section records the implementation; A4 in the design
note is the specification.

**New code.** `v3/continuation_validation.py` holds the pure, tested
numerics. `v3/table_validation_a4.py` holds the stages, assembly and
publication. The one edit outside new modules is the lookup change in
`v3/production_tables.py`.

**Seeds.** Three streams, `v3_R_fit`, `v3_R_validate` and `v3_R_census`,
each a SHA-256 of the tag, the A1 job seed and the replicate index,
truncated to 60 bits, matching the committed planning derivations. The fit
stream uses replicate 0, plain validation uses replicates 1 to 3, the FV
validation replicate is index 1, and the census uses index 0.
`assert_seeds_distinct` derives the three streams and halts on any collision
with each other, the A1 job seed, the D26 probe seeds, and the
`planning_P1`, `planning_P1_census` and `planning_P3` seeds. The A1 and
probe seeds exceed 2^128 while the streams are below 2^60, so those
collisions cannot occur by magnitude; the check is retained as A4 requires.

**Plain tier.** `refit_c0` solves the merged population-0 cell's Bellman
fixed point on the fitting replicate's covered living-source transitions by
the closed form `C0 = a / (N - beta T)`, excluding transitions into
unpublished cells and taking `lower` at extinction. C0 is published only
with at least four fitting visits. `row_width` computes the a priori width
`w = (1 - beta) W + beta (vmax - lower)` from the fitted table, and range
checks halt if any flow or published value leaves `[lower, upper]`.
`empirical_bernstein` applies the two-sided Maurer and Pontil bound and
classifies each cell certified, violation or unresolved; a certified cell is
published only if the visit-weighted point estimate also lies within
`[-tau, tau]`. `tau = 0.05 W`. M is the A1 published plain cells with
population category above zero plus one per plain row, computed from the
pinned A1 publication before any new data.

**FV tier.** Units are the 32 groups. `delta_method_interval` gives the
ratio interval; `fieller_interval` gives the Fieller set, counting an
unbounded set (Nbar^2 <= (t^2/n) s_NN) unresolved. The Student t quantile at
`1 - alpha/(2 M_FV)` is computed scipy-free by inverting the regularized
incomplete beta (Lentz continued fraction); it reproduces t_30 at 0.975 =
2.0423 and approaches z at large degrees of freedom. A cell passes only if
both intervals lie within `[-tau, tau]`, with at least 16 contributing
groups. FV rows carry the label "asymptotic, not certified". M_FV is the A1
published FV cells.

**Census.** `census_endpoints` replays a plain trace under the committed law
on the census seed, and `census_fractions` reports the fraction of living
endpoints, and of low-population living endpoints, outside a row's validated
support, reusing the `endpoint_counts` masking with the added low-population
split. `census_floor` passes a row at at most 2 percent of living endpoints
and, with at least 50 low-population living endpoints, at most 5 percent of
those. A failing row is not_estimable, so the registered loader rejects the
family.

**Publication and lookup.** `publish` assembles a new `v3-tables-1` family:
retained A1 rows keep their A1 producer identity, each plain row stores C0
once with the bounded-domain error `max(C0 - lower, upper - C0)`, plain
continuation entries are pruned to the validated non-population-0 cells, row
status follows the census floor, and a sealed `.compatibility.json` receipt
binds the new hash, both producers, the seeds, M and M_FV. It passes
`require_production`. The lookup change resolves a population-category-0 key
of a plain row with a published C0 to C0; FV rows, extinct endpoints and
every other key are unchanged.

**Runner integration and its scope note.** A4 requires the stages to run as
jobs through the production runner. The write scope named only new modules
and the one `production_tables` lookup change, not `production_runner.py`,
whose `execute` dispatches by job kind. Rather than add A4 kinds to
`execute` (outside the write scope), `table_validation_a4` runs the stages
through a durable orchestrator built from the runner's own primitives:
per-job atomic completion records with resume by skipping completed outputs,
cross-process leases, one numerical thread per worker, and a wall deadline.
`prepare` builds a sealed plan following `table_repair_a3`. This is the one
place A4 was read against the write scope; see the executor report.

**A2/A3 compatibility boundary.** `v3/production_tables.py` is pinned in
`table_compatibility_A2.json`'s `approved_boundary_sha256`. The A4 lookup
change alters that file, so the A2/A3 exception can no longer verify the
genuine A1 publication under the changed code, and four pre-existing
compatibility tests fail on that dependency check. A4 tables load through
their own producer identity, so A4 execution is unaffected. Re-pinning or
retiring the A2/A3 exception is an operator decision outside A4's write
scope.

**Tests.** `test_v3_a4_functions.py` (25 cases) checks the formulas against
hand-computed values, the refit on a known fixed point, living-source
masking, the width bound on random data, empirical Bernstein coverage, the t
quantiles, Fieller versus the delta method, seed distinctness and the
collision halt, and the out-of-range halt.
`test_v3_a4_publication.py` (5 cases) checks loading through
`require_production`, the C0 lookup resolution and that the lookup is
unchanged elsewhere, durable resume, and seed determinism. All 30 pass in
under a second. The workstation smoke ran all four stages end to end on two
plain and one FV A1 job at tiny settings (4 groups, burn 16, measure 64, 32
runs or particles) in about 70 seconds; with so short a burn-in no
population-0 states arise, so C0 is exercised by the unit tests rather than
the smoke.

No commit, registered run, network or X2 action was performed.

## 25. A4 review fixes and runner integration, 2026-09-29

The A4 implementation was reviewed. The math module was sound; the fixes below
were made before a registered run. The reviewer also changed A4 itself: every
replicate keeps its job's own A1 settings (so sensitivity jobs keep their
doubled population or length), and a row with no living census endpoints passes,
reported as not assessed.

1. **Row status rebuilt for every A1 row.** `assemble_family` now rebuilds each
   row's status from A1's own screens (route, flow half-width, half-window
   drift, held-out coverage at least 0.9, fixed-point convergence) plus A4's two
   conditions (nonempty validated support, availability floor). A1 rows that
   failed only the continuation residual are rescued when they pass. The A1
   screen values are kept in the row's `a4` record.
2. **Sensitivity rows assembled separately.** Primary and sensitivity rows are
   collected by setting, as `study.assemble_tables` does, and the sensitivity
   contrasts and `sensitivity_status` are recomputed with the committed rules
   and the A4 statuses. A doubled-length row no longer overwrites its primary.
3. **M and M_FV from every A1 job output row**, primary and sensitivity,
   whatever the status, pinned in the plan and verified at publish. On the
   pinned A1 family: M = 149,200, M_FV = 797,225 (3,165 plain and 12,055 FV
   rows).
4. **Registered stage runner.** `production_runner.execute` dispatches the
   `a4_fit`, `a4_validate` and `a4_census` kinds to `table_validation_a4.run_stage_job`,
   run in five phases (fit, validate plain, validate FV primary, validate FV
   doubled-population, census) with the runner's configuration test, live mode
   control, durable completion records, resume and 48-hour deadline. The A4
   stream seeds travel in each job's config; the runner's own job seed is
   unused. After each phase the runner re-executes one completed task in a fresh
   spawned worker and compares result hashes; a mismatch halts.
   `prepare` checks seed distinctness across all jobs, including the D26 probe
   seeds from the a3_probe records.
5. **Identity checks.** Every stage output binds its A1 job ID, stream seed,
   code identity and plan hash; resume and publish refuse any mismatch. Publish
   verifies the pinned A1 publication, the registration pin and the calibration
   hash, and refuses a frozen target. The receipt binds the seeds, every stage
   output hash, M, M_FV and the plan hash.
6. **Census follows the committed law.** `census_stage` uses the job's A1
   settings (6 groups), burn 0, measure 519, the census seed, the plain route
   and held-out groups only, and stores per-cell living-endpoint counts by fine
   code, not raw endpoints. Only fractions and assessed flags reach the family.
7. **FV living-source mask** uses the conditioned (resampled) state of the
   previous step, so a clone of a dead particle counts as a living source. For
   plain, conditioned equals features.
8. **Smaller items:** the empty-support early return now carries
   `support_values`; an FV collapse is recorded and reported; FV A1 values are
   range-checked; and a plain row certified through C0 alone passes
   `require_production`.
9. **Lookup:** for a plain row with a published C0, every population-category-0
   key resolves to C0, whether or not an entry exists.
10. **Compatibility boundary.** The A4 edits changed `production_tables.py` and
    `production_runner.py`, both pinned in `table_compatibility_A2.json`'s
    approved boundary. The record was re-pinned to their A4 hashes, with an
    `a4` note recording the extension and the previous hashes. `verified_record`
    and `gates.verify_instrument` pass; the loader still refuses any unapproved
    change. The A2-dependencies test was strengthened to assert the
    re-established A4 boundary; the other four named tests pass unchanged under
    it.
11. **Zero living endpoints:** the floor passes, reported as not assessed.
12. **Blinding:** the family, logs and reports carry only fractions and assessed
    flags; living and low-population endpoint counts stay in the census stage
    records.

**Observation.** In one smoke run under heavy concurrent numpy load, a census
stage output differed from a clean recompute (same total living endpoints, a few
bins reassigned). Under a controlled CPU burn, and across sequential spawned
workers, the stage is bit-identical. The stages are reproducible within the
spawned-worker path; the nondeterminism check recomputes there. Whether the
simulation can drift under heavy concurrent numpy contention is worth the
reviewer's attention, because the X2 run is highly concurrent and the check is
mandatory.

No commit, registered run, network or X2 action was performed.

## 26. A4 runner fixes, review round 2, 2026-09-29

Round 2 found defects in the runner integration and publishing. A4 itself
changed twice: every replicate keeps its job's own A1 settings (sensitivity
jobs keep their doubled population or length), and a row with no living census
endpoints passes, reported as not assessed.

1. **Memory safety.** `estimate_memory_gb` gives a per-task estimate by
   arithmetic, anchored on the FV primary planning peak of 9.5 GB and scaling
   with population times length: FV primary 9.5 GB, FV doubled-population and
   doubled-length 19 GB, plain fit/validate up to 4.75 GB, census about 0.1 GB.
   Each phase's configuration test now times tasks of that phase's own kind,
   shortened in length only (a self-contained validate config task fits C0
   inline, so it needs no fit sibling). `dispatch` enforces a per-phase worker
   cap of `floor(0.8 x MemAvailable / estimate)` alongside the mode caps, and a
   live guard refuses to start a task while MemAvailable is below 1.2 times its
   estimate. `MemAvailable` is read cross-platform. The six doubled-length FV
   jobs moved into the high-memory phase with the doubled-population jobs.
2. **Registered publish guards.** `registered_publish_guard` requires the
   registered flag and a registration pin and rejects any settings override, so
   a smoke plan cannot publish registered. Publish verifies every stage output
   through the runner's durable `completed()` record (binding the whole job, so
   config, settings and seed) plus the A4 identity fields, and recomputes and
   checks `plan_hash`, which now digests the full job skeleton, the overrides
   and the registration.
3. **48-hour projection.** After each phase's configuration test the runner
   projects all remaining work (task time scaled to full length, the per-phase
   worker cap, one nondeterminism recheck per phase, and a 1,200 s cleanup
   reserve) and stops before a phase whose projection exceeds the remaining
   budget, recording every projection.
4. **Probe seeds.** `prepare` refuses a missing or empty probe root; the run
   note gives the corrected path and the expected count (855).
5. **End-to-end tests.** A synthetic family exercises assembly of a sensitivity
   pair, a rescued continuation-only A1 failure, a floor failure with living
   endpoints, and a zero-endpoint row; refusal tests cover a registered publish
   of a smoke plan and a stage-output identity mismatch. The smoke runs all five
   phases through the runner. The real-A1 stub assembly now uses census outputs
   with living endpoints inside the support so the floor is assessed and passes.
6. **Smaller items.** Rescued rows clear A1's `reason`/`primary_reason`, kept as
   `a1_reason`/`a1_primary_reason`. The receipt binds every stream seed
   explicitly. The nondeterminism check picks its task by a recorded seeded draw
   among the phase's shortest tasks and records the result durably. FV collapse
   reports the collapsed-group count and transitions lost per job. Calibrations
   are keyed by content hash, not path. Dispatch events label the runner's job
   seed unused for A4 jobs. An O(n^2) stage-output glob was replaced by a single
   index.

The A2 approved boundary was re-pinned to the new `production_runner.py` hash.

No commit, registered run, network or X2 action was performed.

## 27. A4 projection, resume and reporting, review round 3, 2026-09-29

Round 3 confirmed the memory estimates and caps, the per-phase configuration
tests, the high-memory phase, the publish guards and `plan_hash`, and the A2
re-pin. It fixed two projection blockers and the items below.

1. **Resume.** `a4_projection` counts only jobs without a valid `completed()`
   record and skips finished phases (it takes the run root and code). `launch`
   projects only the remaining work against the remaining budget, so an
   interrupted run resumes.
2. **Projection bias.** Each job is scaled by its own population times length
   from a per-cell rate, not by the phase maximum. The `validate_plain`
   configuration task is self-contained (fit plus validate), so the fit
   configuration time is subtracted. The worker count per phase is `min(mode
   cap, chosen workers, memory cap)`, so census no longer projects at hundreds
   of workers. The cleanup reserve is counted once (the deadline already
   subtracts it). On the real plan, with planning task costs of about 900 s per
   plain task and 3,500 s per FV primary task (double for the high-memory
   tasks), the projection is about 37.5 hours (fit 1.3, validate_plain 3.4,
   validate_fv_primary 25.6, validate_fv_double_population 6.7, census 0.6;
   phase job counts 79, 237, 252, 12, 343), within the 48-hour budget.
3. **Memory guard.** `memory_hold` is rate-limited to once per minute; the guard
   halts with a clear reason if it holds while no task is active. Each completed
   task's peak RSS is recorded; a phase peak above its estimate raises the
   estimate for later dispatch, which only lowers the worker cap.
4. **Reporting.** Per-cell results are kept in the family (`a4.cell_tests`), and
   a `report` command writes A4's Reporting paragraph: per-tier counts and visit
   shares, plain safeguard failures, every violation, each row's floor result,
   and FV collapse effects, with no survival, extinction or fire rate.
5. **Tests.** A true end-to-end runs prepare, `launch` of all phases, `publish()`
   and `require_production`, plus a dispatch interrupt and resume; the
   projection-stop and resume-aware counting have unit tests; the smoke-refusal
   calls `publish()` itself (the registration check runs first).
6. **Smaller.** The nondeterminism cost function uses each job's registered
   settings; `restart` and `restart_required` no longer log the unused runner
   seed; `a1_primary_reason` is filled from the A1 row.
7. **Run note.** Corrected worker/mode text (the smaller of `--workers` and
   `--max-workers` and the caps), exact staging paths, the `report` command, and
   what to do on a projection stop, a refused resume and a memory-guard halt.

A fixture (smoke) run records the actual source hash rather than the canonical
A1 hash, so a synthetic small family runs end to end; a registered run still
pins the canonical A1 file. The A2 boundary was re-pinned to the new
`production_runner.py` hash.

No commit, registered run, network or X2 action was performed.

## 28. A4 memory cap and final items, review round 4, 2026-09-29

Round 4 confirmed the projection (37.4 hours reproduced), resume, guard, report,
publish refusal, and the A2 re-pin. It fixed one blocker and three items.

1. **Memory cap double-count (blocker).** Dispatch had recomputed
   `floor(0.8 x MemAvailable / estimate)` every loop from live MemAvailable,
   which already excludes running tasks, so the FV caps decayed toward 5 and 2
   to 3 instead of 9 and 4 and the run overran. Each phase's cap is now fixed
   once at phase start (the value `launch` computes and passes), recorded in a
   `memory_cap` event, and only lowered by `lowered_cap` when a measured peak
   raises the phase estimate. Live pressure is left to the 1.2x guard.
   Projection and dispatch use the same per-phase caps.
2. **Suite tests.** `test_v3_a4_runner.py` covers a launch across all phases
   with a resume, the cap held fixed while MemAvailable drops (the round-4
   regression, via fixture jobs and a mocked MemAvailable), the cap lowering
   arithmetic, the peak-RSS recording, the guard halt with no active task, and a
   projection stop.
3. **Report and family size.** The per-cell results moved out of the family
   into a `.cell_results.json` sidecar, bound by hash (`cell_results_sha256`) in
   the compatibility receipt, so the family every rerun job loads stays small.
   `report` reads the sidecar (verifying its hash) and covers the sensitivity
   rows as well as the primary rows.
4. **Run note.** The projection-stop guidance now says to stop and report, with
   no fresh-root/larger-`--wall-hours` suggestion; the caps are stated for about
   118 GB available (plain 19, FV primary 9, FV doubled 4, census the mode cap).

The A2 boundary was re-pinned to the final `production_runner.py` and
`production_tables.py` hashes; `verify_instrument` passes.

**Reviewer fix after the round 5 review.** Successive measured peaks compounded
the memory cap: each raised estimate was applied to the already-lowered cap, and
dispatch received the combined CPU and memory cap rather than the phase's memory
cap. FV primary peaks of 9.6 to 10.1 GB would have taken its cap from 9 to 3. The
launch now passes the phase's own memory cap, and `next_memory_cap` always lowers
from that original cap, never above the current one. The same peaks now settle at
8. `test_successive_peaks_do_not_compound` covers this. The A2 boundary hash of
`production_runner.py` was re-pinned to the fixed file; `verified_record` and
`verify_instrument` pass, and the full suite passes (327 tests). The suite's
resume test relaunches a finished run; an interrupted launch and its resume were
exercised in the smoke through the runner.

No commit, registered run, network or X2 action was performed.
