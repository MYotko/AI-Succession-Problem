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
