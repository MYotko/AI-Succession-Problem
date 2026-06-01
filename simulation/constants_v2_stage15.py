"""Stage 1.5 named constants for v2 diagnostic state.

Every constant is sourced from docs/lineage_phi_program_reference.md Part V
(Stage 1.5 worked examples 1-5). Each comment within 5 lines cites the
program reference's governance justification for the value. Comments are
phi-blind by design: they describe what the constant represents in
governance terms, not how it interacts with phi or any phi sweep finding.

If a value here differs from the program reference, the reference wins;
update this file, not the reference. Any phi-related rationale belongs
in the Stage 3 prompt, not here.
"""

# ===========================================================================
# avg_wb urgency (worked example 1)
# ===========================================================================
# Empirical v1.x.2 healthy-operation equilibrium and v2 bridge calibration
# anchor; above 0.80, additional welfare has diminishing marginal governance
# value.
WB_TARGET = 0.80

# Below v1.x.2 reproduction threshold (0.50), so maximum urgency activates
# before demographic failure fully expresses. Anticipatory rather than
# reactive.
WB_CRISIS = 0.45

# Prevents welfare going inert in healthy states. Welfare remains substrate-
# maintenance even when population is stable. 0.50 would underweight; 1.00
# would make urgency inert.
WB_URGENCY_MIN = 0.75

# Doubles crisis welfare marginal return. Strong enough to shift allocation,
# bounded enough to avoid welfare-only collapse. The calibration parameter
# to watch in smoke testing.
WB_URGENCY_MAX = 2.00

# ===========================================================================
# population_ratio (worked example 2)
# ===========================================================================
# First-build safety margin where ordinary variance does not threaten lineage.
# 2.0 too thin (modest shock pushes back toward failure); 5.0 keeps pressure
# active too long; 3.0 is the chosen first-build threshold.
POP_VIABILITY_TARGET = 3.0

# Capacity pressure activates around 80% of carrying capacity. 0.70 too
# early (treats normal growth as crowding); 0.90 too late (insensitive to
# per-capita pressure until saturation).
CAPACITY_SAFE = 0.80

# Inherited from model.min_viable_population; fallback to preserve continuity
# with v1.x.2 collapse assumptions rather than introducing a new threshold.
MIN_VIABLE_POPULATION_FALLBACK = 50

# Inherited from model.config["carrying_capacity"]; fallback matches agent-
# layer capacity_modifier so projection and actual dynamics use the same
# reference.
CARRYING_CAPACITY_FALLBACK = 1600

# ===========================================================================
# demographic_pressure (worked example 3)
# ===========================================================================
# 0.5% per step net shrinkage tolerated. 0.001 too sensitive (stochastic
# variance triggers urgency in stable populations); 0.02 too tolerant
# (meaningful decline begins before urgency activates).
SHRINKAGE_FLOOR = 0.005

# 2% per step activates full urgency. Compounds to approximately halving
# population in 35 steps. 4x ratio from floor provides meaningful gradient.
SHRINKAGE_CRISIS = 0.02

# Symmetric to shrinkage_floor for activation sensitivity.
GROWTH_FLOOR = 0.005

# 3% per step net growth activates full growth_pressure. Higher than
# shrinkage_crisis (0.02) by deliberate asymmetry. Growth is less urgent
# than shrinkage; planner should respond more strongly to losing substrate
# than to growing it.
GROWTH_ACTIVE = 0.03

# ===========================================================================
# resilience_stock dynamics (worked example 4)
# ===========================================================================
# Investment-to-stock conversion rate. 0.05 too weak (insufficient efficiency
# to reach target operating range); 0.20 too strong (saturates too easily).
# Calibrated so x_resilience = 0.15 produces steady-state ~0.43 in target band.
K_RESILIENCE_INVESTMENT = 0.10

# Decay rate; ~35-step half-life untended. 2.5x psi_inst_stock's decay rate,
# reflecting that resilience degrades faster than institutional capacity
# without active-use reinforcement.
K_RESILIENCE_DECAY = 0.020

# Full stock reduces shock damage by 70% with 30% irreducible. 0.5
# underweights protective value; 0.9 implies near-immunity (unrealistic).
RESILIENCE_MAX_ATTENUATION = 0.7

# Drawdown per unit damage absorbed. 1.0 too efficient (perfect
# proportionality); 2.5 too inefficient (irrational investment). 1.5 means
# magnitude-0.5 shock at stock=0.5 produces stock drop ~0.26.
K_RESILIENCE_CONSUMPTION = 1.5

# Strongest single contribution to resilience_composite_urgency among
# resilience-specific factors. Below viability_pressure's 0.50 (stock-over-
# flow principle holds: viability is more existential than resilience deficit).
K_RESILIENCE_DEFICIT_CONTRIBUTION = 0.40

# Initialize at low-to-moderate operating range. Target operating band under
# x_resilience in [0.10, 0.25] is steady-state in [0.30, 0.60]; 0.30 is the
# low end of that band so the build starts under-supplied.
RESILIENCE_STOCK_INITIAL = 0.30

# Saturating curve coefficient for raw_resilience_return = 1 - exp(-K * stock).
# Mirrors institutional saturation form; 3.0 produces meaningful gradient
# across the target operating band [0.30, 0.60].
RESILIENCE_ADEQUACY_K = 3.0

# ===========================================================================
# trend variables (worked example 5)
# ===========================================================================
# EMA smoothing. 0.10 too slow (multi-step lag weakens horizon role); 0.50
# too noisy (single-step fluctuations dominate). At 0.30, a sudden decline
# reaches ~65% of its value by step 4 and ~95% by step 10.
ALPHA_TREND = 0.30

# Uniform first-build scale across all four trends. A smoothed 5% per step
# decline is treated as full pressure. Per-variable calibration deferred
# until smoke testing reveals different natural rates of movement.
TREND_SCALE = 0.05

# Initialize all trends at zero at model startup. Approximately 5-10 step
# warmup before EMA values become representative. This is correct behavior,
# not a defect.
TREND_INITIAL = 0.0

# ===========================================================================
# combined_welfare_urgency (worked examples 1, 2, 3, 5)
# ===========================================================================
# Stock-over-flow-over-trend hierarchy: viability_pressure (stock) has the
# largest welfare coefficient; shrinkage_pressure (flow) is smaller;
# trend coefficients are smallest. avg_wb_decline (welfare-specific trend)
# is weighted higher than population_decline (cross-cutting).
K_WELFARE_VIABILITY    = 0.50
K_WELFARE_CAPACITY     = 0.25
K_WELFARE_SHRINKAGE    = 0.35
K_WELFARE_AVG_WB_TREND = 0.15
K_WELFARE_POP_TREND    = 0.10

# Composite floor: prevents welfare urgency going inert when avg_wb is high
# and no demographic pressure activates. Composite cap: prevents combined
# avg_wb + population stress from letting welfare substitute for
# institutions, resilience, or agency.
WELFARE_URGENCY_FLOOR = 0.50
WELFARE_URGENCY_CAP   = 2.50

# ===========================================================================
# agency_composite_urgency (worked examples 2, 3, 5)
# ===========================================================================
# Agency responds to viability and to shrinkage (continuity-of-cohort), and
# modestly to population trend. Capacity pressure does not strongly raise
# agency urgency (handled by other categories).
K_AGENCY_VIABILITY  = 0.35
K_AGENCY_SHRINKAGE  = 0.25
K_AGENCY_POP_TREND  = 0.10

# Below welfare's cap (2.50) and institution's cap (2.00): agency is one
# governance dimension among several; crisis response should not collapse
# to maximum-agency.
AGENCY_URGENCY_CAP = 1.50

# ===========================================================================
# institution_composite_urgency (worked examples 2, 3, 5)
# ===========================================================================
# Institutions respond to viability (continuity), capacity (throughput),
# shrinkage (continuity again), growth (throughput pressure), and population
# trend (anticipatory). Psi_inst_trend gets the largest trend weight because
# it directly signals institutional deterioration.
K_INSTITUTION_VIABILITY = 0.35
K_INSTITUTION_CAPACITY  = 0.50
K_INSTITUTION_SHRINKAGE = 0.35
K_INSTITUTION_GROWTH    = 0.25
K_INSTITUTION_POP_TREND = 0.15
K_INSTITUTION_PSI_TREND = 0.20

# Cap at parity with resilience (2.00); both are infrastructure categories
# that the planner should be willing to scale to under stress without ever
# fully dominating.
INSTITUTION_URGENCY_CAP = 2.00

# ===========================================================================
# resilience_composite_urgency (worked examples 2, 3, 4, 5)
# ===========================================================================
# Resilience-specific deficit contribution is large (0.40) because the
# diagnostic targets the category directly. Stays below viability_pressure's
# 0.50 (stock-over-flow principle: viability is more existential).
# Resilience_trend gets the largest trend weight because it directly signals
# stock deterioration.
K_RESILIENCE_VIABILITY = 0.50
K_RESILIENCE_CAPACITY  = 0.35
K_RESILIENCE_SHRINKAGE = 0.25
K_RESILIENCE_GROWTH    = 0.20
K_RESILIENCE_POP_TREND = 0.15
K_RESILIENCE_RES_TREND = 0.20

# Cap raised from 1.75 to 2.00 to accommodate the resilience_pressure
# contribution while preserving the structural commitment that resilience
# cannot dominate the allocator.
RESILIENCE_URGENCY_CAP = 2.00

# ===========================================================================
# Cohort-correction newborn well-being mean (worked example 1 fallback)
# ===========================================================================
# Verified from agents.HumanAgent.__init__ (line 615-618):
#   self.well_being = np.random.uniform(wb_min, wb_max)
# with defaults wb_min=0.5, wb_max=0.8 (config-overridable). The expected
# initial well-being of a newborn agent is therefore (wb_min + wb_max) / 2.
# This constant documents the default-config value (0.5 + 0.8) / 2 = 0.65;
# the projection function computes the actual mean from config to respect
# wb_min/wb_max overrides (faithfulness tests force narrow ranges, for
# example).
BIRTH_WB_MEAN = 0.65


# ===========================================================================
# Cohort-correction newborn age mean (Stage 1.5 projection refinement)
# ===========================================================================
# Verified from agents.HumanAgent.__init__:
#   self.age = np.random.randint(0, human_max_start_age)
# np.random.randint(0, H) yields integers in [0, H-1], so the expected
# initial age of a newborn agent is (H - 1) / 2. For default
# human_max_start_age = 50: mean = 49 / 2 = 24.5.
#
# This constant is the second component of cohort correction in the
# projection (parallel to BIRTH_WB_MEAN). It addresses avg_age runaway
# in the projection that was identified by faithfulness Test A and Test D
# after the avg_wb cohort correction landed. Without this correction,
# projected_avg_age grows monotonically (+1 per step) while empirical
# avg_age asymptotes at the steady state where age-skewed mortality of
# old agents balances constant-inflow births of age 0. Worked example 1's
# original cohort correction targeted avg_wb only; this generalizes the
# pattern to avg_age, which avg_wb consumes through the -0.001 * age drag.
#
# As with BIRTH_WB_MEAN, the projection helper reads human_max_start_age
# from config and computes (H - 1) / 2; this constant documents the
# default-config value for traceability.
BIRTH_AGE_MEAN = 24.5


# ===========================================================================
# suppression_composite_penalty (worked examples 2, 3, 5)
# ===========================================================================
# Composite penalty multiplies the existing (1 - total_supp) dampening:
# base_suppression_penalty = (1 - total_supp), composite = clamp(base *
# (1 + sum of weighted pressures), base, CAP_MULTIPLIER * base). The
# resulting composite replaces (1 - total_supp) in the dampening chain
# applied to h_n_v2 and agency_legitimacy_factor (with a final clamp to
# [0, 1] since dampening cannot exceed 1).
K_SUPPRESSION_VIABILITY = 0.50
K_SUPPRESSION_CAPACITY  = 0.25
K_SUPPRESSION_SHRINKAGE = 0.35
K_SUPPRESSION_POP_TREND = 0.15
K_SUPPRESSION_PSI_TREND = 0.15

# Cap multiplier: under maximum stress, the composite reaches 2x the base
# dampening factor before the final [0, 1] clamp. This preserves the
# commitment that suppression cannot become unbounded relief from its own
# dampening effect.
SUPPRESSION_PENALTY_CAP_MULTIPLIER = 2.00


# ===========================================================================
# Stage 1.6: U_sys revision — phi moves to rollout aggregation
# ===========================================================================
# The Stage 1.5 phi diagnostic established that phi cancels in the optimizer's
# argmax under the production multiplicative-with-phi-inside U_sys structure
# (A_t = w_n*h_n + w_e*h_e saturates to approximately lambda_n + lambda_e
# across candidates, so the per-step product A_t * (discount + phi * L_t)
# becomes proportional to discount + phi * L_t, and argmax over candidates
# reduces to argmax of L_t regardless of phi).
#
# Stage 1.6 moves phi out of per-step U_sys and into rollout aggregation,
# preserving the multiplicative entropy-lineage coupling with a fixed
# constant. Phi now modulates the rollout discount gamma(phi), shaping
# how heavily future-horizon contributions weight in the optimizer's score.

# Entropy-lineage coupling strength.
# Numerical-equivalence anchor: matches the current default phi value so
# per-step U_sys magnitude is preserved at default operation. Substantively,
# this is the fixed multiplicative strength of how lineage health gates
# entropy value, separated from horizon weighting which is now phi's role.
LAMBDA_LINEAGE_COUPLING = 10.0

# Rollout discount function parameters:
#   gamma(phi) = GAMMA_MIN + (GAMMA_MAX - GAMMA_MIN) * phi / (phi + PHI_HALF)

# Minimum rollout discount factor (phi -> 0 limit).
# A planner with phi approaching zero discounts the next step by 50%, step
# 2 by 75%, step 10 by 99.9%. Effective horizon ~3-4 steps. Represents
# maximally short-horizon governance reasoning.
GAMMA_MIN = 0.5

# Maximum rollout discount factor (phi -> infinity limit).
# A planner with very high phi retains 36% weight at step 20, 13% at step
# 40, 2% at step 80. Effective horizon ~40-60 steps. Bounded below 1.0
# because real planners discount distant futures due to uncertainty
# propagation; unbounded gamma is unphysical.
GAMMA_MAX = 0.95

# Phi value at which gamma reaches halfway between GAMMA_MIN and GAMMA_MAX.
# Default phi in v2 is 10; setting PHI_HALF at 10 puts default phi at the
# function's inflection point, so small variations around default produce
# meaningful changes in gamma. PHI_HALF = 1 would saturate too quickly;
# PHI_HALF = 100 would underutilize the phi range. Operational phi range
# (1 to 100) is centered around this inflection.
PHI_HALF = 10.0
