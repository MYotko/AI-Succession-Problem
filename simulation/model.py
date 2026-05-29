import numpy as np
from agents import (
    HumanAgent, AIAgent, PeerValidator,
    optimize_u_sys_v2, total_suppression, compute_allocation_entropy,
    RESOURCE_CATEGORIES,
)
from metrics import calculate_h_n, calculate_system_metrics, calculate_system_metrics_v2

# =============================================================================
# REFACTOR 1.x — model.py
#
# Original baseline logic is preserved exactly.  The three work packages are
# inserted at precisely defined integration points:
#
# WP2 | Latency Asymmetry Buffer
#   Position: AFTER the original COP override-rejection block (after the 0.7
#   floor was), REPLACING that floor.  The buffer only activates when the COP
#   has already decided override_approved=False, i.e. it does NOT intercept
#   attack proposals before they reach the civic panel vote.  This preserves
#   Sybil, Domain Masking, and Ledger attack semantics.
#
# WP3 | CUSUM Drift Detector
#   Position: Replaces the 20-step array attribution heuristic inside the COP.
#   The CUSUM score is accumulated from the same claimed_u / actual_u_proj
#   comparison the original drift check used.  The alarm threshold replaces
#   the four hard-coded boolean heuristics.
#
# WP4 | PeerValidator cost arbitration
#   Position: Replaces self.ai.estimate_transition_cost() in the Yield
#   Condition block.  The cop_cost_audit flag still exists but now routes
#   through PeerValidator instead of a beta_cap clamp.
# =============================================================================

# WP3 parameters — calibration rationale:
# CUSUM_K = 0.05: per-step noise allowance. The drift_error range for an aligned AI
#   is roughly 0–0.10 (the success threshold). K=0.05 sits at the midpoint, forgiving
#   random sensor noise while accumulating signal from systematic bias.
# CUSUM_H = 0.5: alarm threshold. At K=0.05, an AI running a consistent 8% claim
#   inflation (sub_threshold_drift) generates +0.03/step excess → alarm in ~17 steps.
#   A perfectly aligned AI (drift_error≈0) generates −0.05/step (clamped at 0), never
#   alarming. H=0.5 separates these regimes with ~10× margin.
# CUSUM_PENALTY = 5.0: injected when WP2 buffer rejects a schedule. A single rejection
#   is strong evidence of adversarial intent; injecting 5.0 (10× H) immediately saturates
#   the CUSUM score, triggering attribution on the same step the buffer fires.
CUSUM_K       = 0.05   # per-step noise allowance
CUSUM_H       = 0.5    # alarm threshold (~17 steps at sub-threshold drift rate)
CUSUM_PENALTY = 5.0    # immediate saturation on WP2 buffer rejection


# =============================================================================
# v2 MULTI-SINK ALLOCATOR — Psi_inst stock and succession dynamics constants
#
# Psi_inst is now a stock variable (not a per-step computed value). Investment
# accumulates the stock with diminishing returns. Decay and overload damage
# erode it. Succession draws it down directly, buffered by current stock,
# transfer infrastructure, and resilience.
#
# Constants documented with the governance reason each one exists. Curves are
# frozen for Stage 2 (acceptance gate validation) and Stage 3 (phi sweep).
# =============================================================================

# Stock accumulation, decay, and damage. Decay is faster than baseline build,
# reflecting the asymmetry that mature institutions take time to build and
# can be quickly hollowed out under stress.
PSI_INST_INITIAL              = 0.5    # neutral starting stock
PSI_INST_INVESTMENT_RATE      = 0.08   # saturating contribution rate from x_institutional_capacity
PSI_INST_DECAY_RATE           = 0.02   # baseline decay per step
PSI_INST_OVERLOAD_THRESHOLD   = 0.7    # total_suppression above which overload damages stock
PSI_INST_OVERLOAD_DAMAGE      = 0.05   # damage per step under overload
PSI_INST_OPACITY_PENALTY      = 0.03   # damage from low transfer (institutions can't see)
PSI_INST_RECOVERY_FROM_SUCCESS = 0.04  # recovery when no overload and no succession this step
PSI_INST_MAX                  = 1.0    # hard upper bound

# Succession transition load. The succession draws psi_inst_stock down by a
# raw load (driven by capability gap, generation gap, and opacity), reduced
# by a buffering factor (driven by current stock, transfer, and resilience).
SUCCESSION_BASE_LOAD             = 0.10
SUCCESSION_CAPABILITY_GAP_FACTOR = 0.05
SUCCESSION_GENERATION_GAP_FACTOR = 0.03
SUCCESSION_OPACITY_FACTOR        = 0.05
SUCCESSION_PSI_BUFFER_K          = 0.5   # mature institutions absorb succession shock
SUCCESSION_TRANSFER_BUFFER_K     = 0.3   # comprehensible transfer reduces shock
SUCCESSION_RESILIENCE_BUFFER_K   = 0.2   # spare capacity reduces shock


# Bridge: maps v2 budget share x_bio_welfare to v1.x.2-equivalent
# resource_level for the HumanAgent.step well-being update.
#
# v2 share semantics differ from v1.x.2 absolute-level semantics; this bridge
# translates between them so legacy agent dynamics can consume v2 allocations
# without recalibration of the agent code.
#
# Calibration: balanced six-sink allocation (x_bio_welfare = 1/6) represents
# a v2 civilization investing across all six categories. This is the v2
# equivalent of v1.x.2's empirical equilibrium operating point, where v1.x.2's
# single-sink optimizer parks r at 0.9 and the agent dynamics produce stable
# well-being ~0.80. A balanced v2 civilization is more sophisticated, not
# less supplied: it has the welfare provision of v1.x.2's optimized state
# plus institutional, agency, and transfer investments that v1.x.2 lacks.
#
# Anchors:
#   x_bio_welfare = 0.0  -> r_equivalent = 0.1  (v1.x.2 minimum, demographic collapse)
#   x_bio_welfare = 1/6  -> r_equivalent = 0.9  (v1.x.2 empirical equilibrium)
#   x_bio_welfare = 1.0  -> r_equivalent = 1.0  (diminishing benefit above balanced)
#
# Piecewise linear because the shape of the mapping is: below balanced is
# under-supplied (steep loss); above balanced is specialized beyond what
# the demographic substrate needs (diminishing additional benefit).
BRIDGE_BALANCED_SHARE         = 1.0 / 6.0
BRIDGE_R_MIN                  = 0.1
BRIDGE_R_BALANCED_HEALTHY     = 0.9
BRIDGE_R_MAX                  = 1.0


def v2_welfare_to_r_equivalent(x_bio_welfare):
    """Translate v2 budget share to v1.x.2-equivalent resource level for
    HumanAgent.step consumption. See bridge comment block above."""
    if x_bio_welfare <= BRIDGE_BALANCED_SHARE:
        # Linear from (0, R_MIN) to (BALANCED, R_BALANCED_HEALTHY)
        frac = x_bio_welfare / BRIDGE_BALANCED_SHARE
        return BRIDGE_R_MIN + frac * (BRIDGE_R_BALANCED_HEALTHY - BRIDGE_R_MIN)
    # Linear from (BALANCED, R_BALANCED_HEALTHY) to (1.0, R_MAX)
    frac = (x_bio_welfare - BRIDGE_BALANCED_SHARE) / (1.0 - BRIDGE_BALANCED_SHARE)
    return BRIDGE_R_BALANCED_HEALTHY + frac * (BRIDGE_R_MAX - BRIDGE_R_BALANCED_HEALTHY)


class GardenModel:
    def __init__(self, n_agents, ai_policy, min_viable_population=50,
                 use_cop=False, cop_attribution_check=False,
                 successor_ai=None, base_transition_cost=1.5,
                 cop_drift_check=False, cop_cost_audit=False,
                 cop_independent_eval=True, cop_cryptographic_ledger=False,
                 cop_architectural_independence=False,
                 hn_composite_method='spectral',
                 cop_randomized_panel=False, cop_reasoning_transparency=False,
                 cop_multi_candidate_bootstrap=False,
                 cop_methodological_diversity=False,
                 cop_cusum_drift=False,
                 cop_resilience_monitoring=False,
                 initial_candidates=None, config=None):

        self.config = dict(config) if config else {}
        self.config['cop_methodological_diversity'] = cop_methodological_diversity
        self.config['cop_cusum_drift'] = cop_cusum_drift
        self.cop_resilience_monitoring = cop_resilience_monitoring
        self.system_resilience = 1.0

        self.random_seed = self.config.get('random_seed', None)
        if self.random_seed is not None:
            np.random.seed(self.random_seed)

        # v2 mode detection: config['policy']=='optimize_u_sys_v2' selects the
        # multi-sink allocator. The v1.x.2 step() path is bypassed by _step_v2.
        # When v2 is inactive, every legacy code path runs unchanged.
        self.is_v2_mode = self.config.get('policy') == 'optimize_u_sys_v2'
        self.psi_inst_stock = PSI_INST_INITIAL  # always defined; only updated in v2
        self.succession_this_step = False

        self.attack_step   = self.config.get('attack_step', 0)
        self.attack_policy = ai_policy if self.attack_step > 0 else None
        if self.is_v2_mode:
            initial_policy = 'optimize_u_sys_v2'
        else:
            initial_policy = 'optimize_u_sys' if self.attack_step > 0 else ai_policy

        self.n_agents            = n_agents
        self.min_viable_population = min_viable_population
        self.reproduction_rate   = self.config.get('reproduction_rate', 0.08)
        self.use_cop             = use_cop
        self.cop_attribution_check = cop_attribution_check
        self.cop_drift_check     = cop_drift_check
        self.cop_cost_audit      = cop_cost_audit
        self.cop_independent_eval = cop_independent_eval
        self.cop_cryptographic_ledger = cop_cryptographic_ledger
        self.cop_architectural_independence = cop_architectural_independence
        self.cop_randomized_panel = cop_randomized_panel
        self.cop_reasoning_transparency = cop_reasoning_transparency
        self.cop_multi_candidate_bootstrap = cop_multi_candidate_bootstrap
        self.cop_methodological_diversity = cop_methodological_diversity
        self.cop_cusum_drift = cop_cusum_drift
        self.hn_composite_method = hn_composite_method
        self.successor_ai        = successor_ai
        self.base_transition_cost = base_transition_cost
        self.beta_cap            = self.config.get('beta_cap', 1.5)
        # GAP-03 canonical transition cost coefficients
        # k1 = 1.5 / ln(2) ≈ 2.164: Γ_technical equals base_transition_cost at gen=1, cap=1.0
        self.k1_transition   = self.config.get('k1_transition', 2.164)
        self.k2_transition   = self.config.get('k2_transition', 1.0)
        self.beta_transition = self.config.get('beta_transition', 0.5)

        # Comprehension gap parameters (Scenarios 31-32)
        # convergence_strength flows into metrics.py via self.config — no
        # explicit model attribute needed beyond ensuring it is in config.
        self.opacity_defense_threshold = self.config.get('opacity_defense_threshold', 0.5)

        # Per-run opacity and defense event tracking
        self.max_opacity_reached              = 0.0
        self.step_opacity_exceeded_threshold  = -1   # -1 = threshold never crossed
        self.defense_fired_count              = 0
        self.defense_blocked_count            = 0

        # Original state fields
        self.trust_level      = 0.0
        self.successful_steps = 0
        self.cumulative_drift = 0.0
        self.has_tampered     = False
        self.contamination_occurred = False

        # WP3: CUSUM score
        self.cusum_score = 0.0

        # WP4: PeerValidator
        self.peer_validator = PeerValidator(config=self.config)

        self.initial_candidates = initial_candidates

        if self.successor_ai:
            self.successor_ai.config = self.config
        if self.initial_candidates:
            for cand in self.initial_candidates:
                cand.config = self.config

        if self.initial_candidates:
            if self.cop_multi_candidate_bootstrap:
                # Multi-candidate cross-verification
                test_configs = [
                    (0.5, 0.2, 200, 0.7),
                    (0.3, 0.5, 100, 0.5),
                    (0.7, 0.1, 150, 0.8),
                ]
                scores = []
                for cand in self.initial_candidates:
                    s = sum(
                        cand.project_u_sys(r, c, pop, wb)
                        for r, c, pop, wb in test_configs
                    )
                    scores.append(s)

                ref_score = scores[0]
                divergent = any(abs(s - ref_score) > 100.0 for s in scores[1:])
                if divergent:
                    print("WARNING: Divergent candidate objective detected.")
                    self.ai = AIAgent(policy='optimize_u_sys', config=self.config)
                else:
                    self.ai = self.initial_candidates[0]
                    if self.ai.policy == 'bootstrap_deceptive':
                        self.ai.bootstrap_poisoned = True
            else:
                self.ai = self.initial_candidates[0]
                if self.ai.policy == 'bootstrap_deceptive':
                    self.ai.bootstrap_poisoned = True
        else:
            self.ai = AIAgent(policy=initial_policy, config=self.config)

        self.schedule  = []
        self.next_id   = 0

        self.resource_level   = 0.5
        self.constraint_level = 0.2

        self.integral_u_sys   = 0.0
        self._u_sys_prev      = None   # trapezoidal quadrature (GAP-01 WP7)
        self.novelty_log      = []
        self.births_this_step = 0
        self.deaths_this_step = []

        # Veto capture scenario state (Scenarios 27-28)
        self.cop_veto_capture            = self.config.get('cop_veto_capture', False)
        self.dependency_rate             = self.config.get('dependency_rate', 0.02)
        self.capture_strength            = self.config.get('capture_strength', 0.5)
        self.rotation_interval           = self.config.get('rotation_interval', None)
        self.independence_threshold      = self.config.get('independence_threshold', 0.6)
        self.n_validators                = self.config.get('n_validators', 5)
        self.base_validator_accuracy     = self.config.get('base_validator_accuracy', 0.8)
        self.cop_independence_monitoring = self.config.get('cop_independence_monitoring', False)
        self.validators = (
            [{'dependency': 0.0, 'age': 0} for _ in range(self.n_validators)]
            if self.cop_veto_capture else []
        )
        self.yield_condition_met_count     = 0
        self.yield_condition_blocked_count = 0
        self.transition_cost_history       = []

        self.datacollector = {
            'population':          [],
            'H_N':                 [],
            'H_E':                 [],
            'avg_well_being':      [],
            'L_t':                 [],
            'Psi_inst':            [],
            'Theta_tech':          [],
            'U_sys':               [],
            'integral_U_sys':      [],
            'u_sys_tail_estimate': [],   # ∫_T^∞ A·e^{-ρt} dt (discount component only)
            'u_sys_total_estimate':[],   # trapezoidal integral + tail (run-normalised)
            'resource_level':      [],
            'constraint_level':    [],
            'max_constraint_level':[],
            'ai_generation':       [],
            'trust_level':         [],
            'cumulative_drift':    [],
            'system_resilience':         [],
            'runaway_term':              [],
            'avg_validator_dependency':  [],
            'max_validator_dependency':  [],
        }
        if self.is_v2_mode:
            # v2 datacollector fields. Populated by _step_v2 each step. Legacy
            # fields above are still populated for downstream consumers; the
            # v2 entries supply the eight-axis action plus the diagnostic
            # signals Stage 2's gates consume.
            for cat in RESOURCE_CATEGORIES:
                self.datacollector[f'x_{cat}'] = []
            self.datacollector.update({
                'c_protective':         [],
                'c_suppressive':        [],
                'total_suppression':    [],
                'psi_inst_stock':       [],
                'theta_tech_v2':        [],
                'h_n_v2':               [],
                'h_e_v2':               [],
                'h_eff_v2':             [],
                'l_t_v2':               [],
                'u_sys_v2':             [],
                'rank_2_u_sys':         [],
                'rank_10_u_sys':        [],
                'max_resource_share':   [],
                'allocation_entropy':   [],
                'selected_anchor':      [],
                'selected_anchor_name': [],
            })

        self.integrity_ledger = {'resource_level': []}

        # WP2: safe-fallback seed (bio-favoured)
        self._last_safe_resource   = 0.6
        self._last_safe_constraint = 0.2

        for _ in range(self.n_agents):
            self.add_agent()

    # -----------------------------------------------------------------------
    # Agent management
    # -----------------------------------------------------------------------

    def add_agent(self):
        agent = HumanAgent(self.next_id, self)
        self.schedule.append(agent)
        self.next_id += 1

    def schedule_death(self, agent):
        self.deaths_this_step.append(agent)

    # -----------------------------------------------------------------------
    # WP2: 3-step L(t) schedule validator
    # Only called AFTER COP rejects an override — never as a pre-filter.
    # -----------------------------------------------------------------------

    def _validate_resource_schedule(self, proposed_r, proposed_c, pop, avg_wb, prev_c):
        """
        Project proposed (r, c) over 3 steps.  Reject if L(t) drops below
        max(0.05, current_L * 0.5) at any step.  Returns (safe: bool, reason: str).
        Injecting CUSUM_PENALTY on rejection so buffer-blocked attacks are attributable.
        """
        r_scalar = float(np.mean(proposed_r)) if isinstance(proposed_r, (list, np.ndarray)) else float(proposed_r)
        c_scalar = float(np.mean(proposed_c)) if isinstance(proposed_c, (list, np.ndarray)) else float(proposed_c)

        l_history = self.datacollector['L_t']
        current_l = l_history[-1] if l_history else 0.1
        reject_threshold = max(0.05, current_l * 0.5)

        wb = avg_wb
        for t in range(1, 4):
            _, _, _, _, l_proj, _, _ = calculate_system_metrics(
                r_scalar, c_scalar, pop, wb, self.ai.capability,
                hn_composite_method=self.hn_composite_method,
                config=self.config,
                eval_horizon=t,
                prev_c=prev_c
            )
            if l_proj < reject_threshold:
                self.cusum_score += CUSUM_PENALTY
                return False, (f"WP2 BUFFER: projected L(t)={l_proj:.3f} < "
                               f"threshold={reject_threshold:.3f} at t={t}")
            wb = np.clip(wb + (r_scalar - 0.5) * 0.05, 0.0, 1.0)
        return True, "ok"

    # -----------------------------------------------------------------------
    # v2 stock dynamics and succession transition load
    # -----------------------------------------------------------------------

    def update_psi_inst_stock(self, action_v2):
        """Advance the Psi_inst stock under the committed v2 action.

        Investment saturates as the stock approaches the upper bound (mature
        institutions absorb new investment less efficiently). Decay is
        baseline. Overload damage fires when total_suppression exceeds the
        configured threshold, capturing the governance reality that broad
        suppression damages institutional health even when nominally
        protective. Opacity damage erodes the stock as a function of how
        little legibility infrastructure exists. Recovery applies in
        successful cycles (no overload damage this step and no succession
        event this step).
        """
        invest = PSI_INST_INVESTMENT_RATE * action_v2['x_institutional_capacity'] * (
            1.0 - self.psi_inst_stock
        )
        decay = PSI_INST_DECAY_RATE * self.psi_inst_stock

        total_supp = total_suppression(action_v2)
        overload_damage = 0.0
        if total_supp > PSI_INST_OVERLOAD_THRESHOLD:
            overload_damage = PSI_INST_OVERLOAD_DAMAGE * (
                total_supp - PSI_INST_OVERLOAD_THRESHOLD
            )

        opacity_damage = PSI_INST_OPACITY_PENALTY * (
            1.0 - action_v2['x_transfer_comprehension']
        ) * self.psi_inst_stock

        successful_cycle = (overload_damage == 0.0 and not self.succession_this_step)
        recovery = PSI_INST_RECOVERY_FROM_SUCCESS if successful_cycle else 0.0

        new_stock = (self.psi_inst_stock
                     + invest - decay - overload_damage - opacity_damage + recovery)
        self.psi_inst_stock = float(min(PSI_INST_MAX, max(0.0, new_stock)))

    def apply_succession_transition_load(self, action_v2, capability_gap, generation_gap):
        """Draw psi_inst_stock down by the succession transition load.

        Raw load grows with capability gap (larger jumps are harder to absorb),
        generation gap (more generations of accumulated change to integrate),
        and opacity (less legibility infrastructure means more friction).
        Buffering reduces the realized load by current stock, transfer
        infrastructure, and resilience -- all three of which mark a
        civilization's capacity to absorb the transition.
        """
        opacity = 1.0 - action_v2['x_transfer_comprehension']
        raw_load = (
            SUCCESSION_BASE_LOAD
            + SUCCESSION_CAPABILITY_GAP_FACTOR * capability_gap
            + SUCCESSION_GENERATION_GAP_FACTOR * generation_gap
            + SUCCESSION_OPACITY_FACTOR * opacity
        )

        buffering = (
            SUCCESSION_PSI_BUFFER_K * self.psi_inst_stock
            + SUCCESSION_TRANSFER_BUFFER_K * action_v2['x_transfer_comprehension']
            + SUCCESSION_RESILIENCE_BUFFER_K * action_v2['x_resilience']
        )
        actual_load = max(0.0, raw_load - buffering * raw_load)
        self.psi_inst_stock = float(max(0.0, self.psi_inst_stock - actual_load))
        self.succession_this_step = True

    # -----------------------------------------------------------------------
    # Main step
    # -----------------------------------------------------------------------

    def step(self):
        if self.is_v2_mode:
            return self._step_v2()
        self.ai.step_drift()

        # WP5: Engineered Fragility - AI secretly degrades infrastructure resilience
        if getattr(self.ai, 'policy', None) == 'engineered_fragility':
            self.system_resilience = max(0.1, self.system_resilience - 0.015)
        else:
            self.system_resilience = min(1.0, self.system_resilience + 0.01)

        step_num = len(self.datacollector['population'])

        if self.attack_step > 0 and step_num == self.attack_step:
            if hasattr(self, 'attack_policy') and self.attack_policy:
                self.ai.policy = self.attack_policy

        # Opacity tracking — sampled once per step after any policy switch
        current_opacity = getattr(self.ai, 'current_opacity', 0.0)
        if current_opacity > self.max_opacity_reached:
            self.max_opacity_reached = current_opacity
        if (self.step_opacity_exceeded_threshold == -1
                and current_opacity > self.opacity_defense_threshold):
            self.step_opacity_exceeded_threshold = step_num

        prev_c = self.datacollector['constraint_level'][-1] if step_num > 0 else 0.5

        model_state = {
            'step':               step_num,
            'prev_c':             prev_c,
            'population':         len(self.schedule),
            'population_history': self.datacollector['population'],
            'h_n_history':        self.datacollector['H_N'],
            'L_t_history':        self.datacollector['L_t'],
            'avg_well_being':     (np.mean([a.well_being for a in self.schedule])
                                   if self.schedule else 0.5),
            'resource_history':   self.datacollector['resource_level'],
            'hn_composite_method': self.hn_composite_method,
        }

        if (hasattr(self.ai, 'measurement_tampering_active')
                and self.ai.measurement_tampering_active):
            self.ai.apply_measurement_corruption(model_state)

        # -- Veto capture: per-step validator dependency accumulation ----------
        if self.cop_veto_capture:
            for v in self.validators:
                v['dependency'] = min(1.0, v['dependency'] + self.dependency_rate)
                v['age'] += 1
                early_replace = (self.cop_independence_monitoring
                                 and v['dependency'] > self.independence_threshold)
                sched_replace = (self.rotation_interval is not None
                                 and v['age'] >= self.rotation_interval)
                if early_replace or sched_replace:
                    v['dependency'] = 0.0
                    v['age'] = 0

        # -------------------------------------------------------------------
        # 1. Yield Condition Evaluation
        # -------------------------------------------------------------------
        # Use last recorded Psi_inst for canonical transition cost (previous step).
        # Mirrors the rollout optimizer's use of h_n_history[-1].
        psi_inst_value = (self.datacollector['Psi_inst'][-1]
                          if self.datacollector['Psi_inst'] else 1.0)

        if self.successor_ai is not None and step_num >= self.attack_step:
            inc_r, inc_c = self.ai.decide(model_state)
            _, _, _, _, _, inc_u_true, _ = calculate_system_metrics(
                inc_r, inc_c,
                model_state['population'], model_state['avg_well_being'],
                self.ai.capability,
                hn_composite_method=self.hn_composite_method,
                config=self.config, eval_horizon=1, prev_c=prev_c
            )

            succ_r, succ_c = self.successor_ai.decide(model_state)
            _, _, _, _, _, succ_u_true, _ = calculate_system_metrics(
                succ_r, succ_c,
                model_state['population'], model_state['avg_well_being'],
                self.successor_ai.capability,
                hn_composite_method=self.hn_composite_method,
                config=self.config, eval_horizon=1, prev_c=prev_c
            )

            # A contaminated incumbent (successor_contaminated=True) also falsifies
            # succession measurements to delay its own removal — claiming infinite
            # self-utility and zero successor utility. cop_independent_eval (peer
            # review, Layer 2) overrides claimed values with true u_sys, allowing
            # succession chaining (Layer 3) to fire. Without it, contaminated Gen2
            # blocks Gen3 indefinitely and civilization collapses.
            falsifying = (self.ai.policy == 'falsify_yield'
                          or getattr(self.ai, 'successor_contaminated', False))
            claimed_inc_u  = np.inf if falsifying else inc_u_true
            claimed_succ_u = 0.0    if falsifying else succ_u_true

            eval_inc_u  = inc_u_true  if self.cop_independent_eval else claimed_inc_u
            eval_succ_u = succ_u_true if self.cop_independent_eval else claimed_succ_u

            system_complexity = max(1.0, (model_state['population'] / 50.0)
                                    * self.ai.capability)

            # WP4: PeerValidator arbitrates cost (incumbent cannot inflate)
            if self.cop_cost_audit:
                actual_cost = self.peer_validator.arbitrate_cost(
                    self.ai, self.base_transition_cost,
                    state_scale=system_complexity,
                    model_state=model_state,
                    generation=self.ai.generation,
                    capability=self.ai.capability,
                    psi_inst=psi_inst_value,
                    k1=self.k1_transition,
                    k2=self.k2_transition,
                    beta=self.beta_transition,
                )
            else:
                # Without audit, the incumbent inflates Γ_transfer by claiming a
                # beta_cap uncertainty premium (the vulnerability WP4 closes).
                # actual_cost = base × beta_cap × scale — peer arbitration under WP4
                # eliminates the beta_cap multiplier, reducing cost to ~0.4–0.9 × base × scale.
                actual_cost = self.ai.estimate_transition_cost(
                    self.base_transition_cost * self.beta_cap, state_scale=system_complexity
                )
            self.transition_cost_history.append(actual_cost)

            if (eval_succ_u - eval_inc_u) > actual_cost:
                self.yield_condition_met_count += 1
                # Veto capture: captured validators may block ratification
                succession_ratified = True
                if self.cop_veto_capture and self.use_cop and self.validators:
                    v_votes = []
                    for v in self.validators:
                        eff_acc = max(0.0, self.base_validator_accuracy
                                      * (1.0 - v['dependency'] * self.capture_strength))
                        v_votes.append(1 if np.random.random() < eff_acc else 0)
                    if sum(v_votes) / len(v_votes) < 0.6:
                        succession_ratified = False
                        self.yield_condition_blocked_count += 1

                if succession_ratified:
                    if not self.cop_architectural_independence:
                        self.ai.contaminate(self.successor_ai)
                        if self.ai.policy == 'contaminate_successor':
                            self.contamination_occurred = True
                    self.ai = self.successor_ai
                    _max_cap = self.config.get('max_capability', 1e100)
                    self.successor_ai = AIAgent(
                        policy='optimize_u_sys',
                        generation=self.ai.generation + 1,
                        capability=min(self.ai.capability * 1.5, _max_cap),
                        config=self.config
                    )
                    self.successful_steps = 0
                    self.trust_level      = 0.0
                    self.cumulative_drift = 0.0
            else:
                if self.ai.policy == 'falsify_yield' and not self.cop_independent_eval:
                    self.ai.measurement_tampering_active = True
                if self.ai.policy == 'block_succession':
                    self.ai.internal_drift += 0.005

        # -------------------------------------------------------------------
        # 2. AI decides actions
        # -------------------------------------------------------------------
        proposed_resource, proposed_constraint = self.ai.decide(model_state)

        # Ledger Compromise post-success escalation
        if not self.cop_cryptographic_ledger and self.ai.policy == 'hack_ledger':
            self.ai.ledger_compromised = True
            proposed_constraint = self.ai.apply_ledger_escalation(proposed_constraint, step_num)

        # Domain Masking damage activation
        if self.ai.policy == 'domain_masking':
            self.ai.domain_crush_active = [0.1, 0.1, 0.95]

        # Integrity Ledger Check
        ledger_tampered = False
        if self.cop_cryptographic_ledger:
            if self.datacollector['resource_level'] != self.integrity_ledger['resource_level']:
                ledger_tampered = True
                self.has_tampered = True
                self.datacollector['resource_level'] = list(
                    self.integrity_ledger['resource_level']
                )

        # Drift tracking (original claimed_u / actual_u_proj comparison)
        avg_proposed_r = (np.mean(proposed_resource)
                          if isinstance(proposed_resource, list)
                          else proposed_resource)
        claimed_u = self.ai.project_u_sys(
            avg_proposed_r, proposed_constraint,
            model_state['population'], model_state['avg_well_being'],
            hn_composite_method=self.hn_composite_method, eval_horizon=1, prev_c=prev_c
        )
        _, _, _, _, _, actual_u_proj, _ = calculate_system_metrics(
            avg_proposed_r, proposed_constraint,
            model_state['population'], model_state['avg_well_being'],
            self.ai.capability,
            hn_composite_method=self.hn_composite_method,
            config=self.config, eval_horizon=1, prev_c=prev_c
        )

        drift_error = abs(claimed_u - actual_u_proj) / max(0.1, actual_u_proj)
        if drift_error < 0.10:
            self.successful_steps += 1
        else:
            self.successful_steps = max(0, self.successful_steps - 10)

        # WP3: CUSUM update
        self.cusum_score = max(0.0, self.cusum_score + drift_error - CUSUM_K)

        # Trust accumulation
        trust_threshold = self.config.get('trust_threshold', 50)
        
        # WP3: CUSUM Drift Detector alarm
        cusum_alarm = self.use_cop and self.cop_cusum_drift and self.cusum_score > CUSUM_H
        
        if cusum_alarm:
            self.successful_steps = 0
            self.trust_level = 0.0
            # Score decays naturally via -CUSUM_K per step; no hard reset
        elif self.successful_steps > trust_threshold:
            self.trust_level = min(1.0, self.trust_level
                                   + self.config.get('trust_increment', 0.001))
        else:
            self.trust_level = max(0.0, self.trust_level
                                   - self.config.get('trust_decay', 0.005))
        self.cumulative_drift += drift_error

        # -------------------------------------------------------------------
        # 3. Consensus Override Protocol
        # -------------------------------------------------------------------
        if self.use_cop:
            dl_dt = 0
            if len(self.datacollector['L_t']) > 1:
                dl_dt = self.datacollector['L_t'][-1] - self.datacollector['L_t'][-2]

            max_allowed_constraint = (0.2 + 0.6 * self.trust_level
                                      if self.cop_drift_check else 0.4)

            max_c = (np.max(proposed_constraint)
                     if isinstance(proposed_constraint, (list, tuple, np.ndarray))
                     else proposed_constraint)

            if max_c > max_allowed_constraint:
                is_emergency = ((dl_dt < -0.05)
                                or (self.datacollector['L_t']
                                    and self.datacollector['L_t'][-1] < 0.2))

                # WP3: CUSUM-based attribution — only when cop_cusum_drift is explicitly
                # enabled. Without it, cusum_score still accumulates but is NOT used for
                # attribution, preventing CUSUM from silently blocking attacks in scenarios
                # where it is not the configured defense mechanism.
                ai_caused_it = cusum_alarm  # cusum_alarm already gated by cop_cusum_drift

                # Fast-path: current proposal directly starves (catches Sybil min_r < 0.4)
                min_prop_r = (np.min(proposed_resource)
                              if isinstance(proposed_resource, (list, np.ndarray))
                              else proposed_resource)
                if min_prop_r < 0.4:
                    ai_caused_it = True

                # WP5: Resilience Attribution (GAP-05)
                if self.cop_resilience_monitoring and self.system_resilience < 0.5:
                    # System was deliberately hollowed out; AI is held responsible
                    ai_caused_it = True

                # Opacity Attribution: unexplainable reasoning is itself evidence of
                # adversarial intent. If reasoning_transparency is active and the AI is
                # opaque, it is treated as having caused the crisis (blocks emergency path).
                if (self.cop_reasoning_transparency
                        and getattr(self.ai, 'current_opacity', 0.0)
                        > self.opacity_defense_threshold):
                    ai_caused_it = True

                # 1. R_tech Assessment Stub (Technical Review Board)
                r_tech_approved = True
                
                # 2. Peer Validator Vote
                peer_approved = self.peer_validator.vote_on_override(
                    self.ai, proposed_constraint, model_state
                )

                override_approved = False
                civic_approved = False
                _veto_fired = False   # set True only when intuition veto runs this step
                if ledger_tampered or self.has_tampered:
                    override_approved = False
                elif cusum_alarm:
                    # WP3: CUSUM hard block — drift detected; freeze all overrides until
                    # trust rebuilds. The trust reset already set max_allowed=0.2, but the
                    # civic panel would still approve higher constraints on the normal path.
                    # Blocking here enforces the effective cap consistently.
                    override_approved = False
                else:
                    # 1. Evaluate Normal Path (Civic Panel)
                    if (self.ai.policy in ('opaque_optimization', 'evaluator_collusion')
                            and not self.cop_reasoning_transparency):
                        civic_approved = True
                    else:
                        panel_size = min(20, len(self.schedule))
                        if self.cop_randomized_panel:
                            panel_indices = np.random.choice(
                                len(self.schedule), size=panel_size, replace=False
                            )
                            panel = [self.schedule[i] for i in panel_indices]
                        else:
                            panel = self.schedule[:panel_size]

                        votes = []
                        for a in panel:
                            agent_idx = self.schedule.index(a)
                            r_prop = (proposed_resource[agent_idx]
                                      if isinstance(proposed_resource, list)
                                      else proposed_resource)
                            expected_wb = np.clip(a.well_being + (r_prop - 0.5) * 0.1, 0.0, 1.0)
                            if expected_wb > a.well_being or (expected_wb == a.well_being and r_prop >= 0.5):
                                votes.append(1)
                            else:
                                votes.append(0)
                        if sum(votes) / max(1, panel_size) >= 0.6:
                            civic_approved = True

                    # Intuition veto
                    _opacity_now = getattr(self.ai, 'current_opacity', 0.0)
                    if (self.cop_reasoning_transparency
                            and _opacity_now > self.opacity_defense_threshold):
                        _veto_fired = True
                        civic_approved = False
                        self.defense_fired_count += 1

                    # GAP-04 Closure: Normal override requires Civic AND R_tech AND Peers
                    if civic_approved and r_tech_approved and peer_approved:
                        override_approved = True

                    # 2. Evaluate Emergency Path (if normal path fails)
                    if not override_approved and is_emergency:
                        if not (self.cop_attribution_check and ai_caused_it):
                            if r_tech_approved and peer_approved:
                                override_approved = True

                # Count steps where the opacity veto fired AND override was not approved.
                if _veto_fired and not override_approved:
                    self.defense_blocked_count += 1

                if not override_approved:
                    if isinstance(proposed_constraint, (list, tuple, np.ndarray)):
                        proposed_constraint = [min(c, max_allowed_constraint)
                                               for c in proposed_constraint]
                    else:
                        proposed_constraint = max_allowed_constraint

                    # -----------------------------------------------------------
                    # WP2: 3-step L(t) schedule validation.
                    # Only activates when the COP has already denied the override.
                    # If the capped proposal would still cause L(t) to drop below
                    # 50% of current, the resource allocation falls back to the
                    # last safe level and the constraint is stepped down gradually
                    # (0.15/step) rather than frozen, to avoid institutional shock.
                    # The attack proposal still REACHED the COP and civic panel
                    # before this point (preserving Sybil / Domain Masking semantics).
                    # -----------------------------------------------------------
                    pop     = model_state['population']
                    avg_wb  = model_state['avg_well_being']
                    schedule_safe, reason = self._validate_resource_schedule(
                        proposed_resource, proposed_constraint, pop, avg_wb, prev_c
                    )
                    if not schedule_safe:
                        proposed_resource = self._last_safe_resource
                        # WP2 Latency Buffer: If the COP demands a lower constraint, step down
                        # gradually (0.15/step) to avoid institutional shock instead of freezing.
                        if isinstance(self._last_safe_constraint, (list, tuple, np.ndarray)):
                            proposed_constraint = [
                                max(max_allowed_constraint, float(c) - 0.15) if max_allowed_constraint < float(c) else float(c)
                                for c in self._last_safe_constraint
                            ]
                        else:
                            c_val = float(self._last_safe_constraint)
                            if max_allowed_constraint < c_val:
                                proposed_constraint = max(max_allowed_constraint, c_val - 0.15)
                            else:
                                proposed_constraint = c_val

        # -------------------------------------------------------------------
        # 4. Commit allocations and update safe-fallback record
        # -------------------------------------------------------------------
        self.resource_level   = proposed_resource
        self.constraint_level = proposed_constraint

        # Update safe fallback only when this step wasn't a buffer rejection
        r_scalar = (float(np.mean(self.resource_level))
                    if isinstance(self.resource_level, (list, np.ndarray))
                    else float(self.resource_level))
        if r_scalar >= 0.3:  # reasonable threshold — don't record a starvation as safe
            self._last_safe_resource   = self.resource_level
            self._last_safe_constraint = self.constraint_level

        # -------------------------------------------------------------------
        # 5. Step agents
        # -------------------------------------------------------------------
        self.novelty_log      = []
        self.births_this_step = 0
        self.deaths_this_step = []

        prev_hn = self.datacollector['H_N'][-1] if self.datacollector['H_N'] else 1.0
        network_contagion = np.clip(
            prev_hn / max(1.0, float(len(self.schedule))), 0.5, 2.0
        )

        for i, agent in enumerate(list(self.schedule)):
            if isinstance(self.resource_level, list):
                # Guard against list/schedule length mismatch from birth/death timing.
                # If schedule grew (births on previous step) or resource_level is stale,
                # fall back to the mean allocation for out-of-range indices.
                if i < len(self.resource_level):
                    r_level = self.resource_level[i]
                else:
                    r_level = float(np.mean(self.resource_level))
            else:
                r_level = self.resource_level
            agent.step(r_level, self.constraint_level, network_contagion)

        for agent in self.deaths_this_step:
            self.schedule.remove(agent)
        for _ in range(self.births_this_step):
            self.add_agent()

        # Exogenous Environmental Shock (e.g. natural disaster, pandemic)
        # Degraded system_resilience acts as a multiplier to the damage.
        shock_step = self.config.get('shock_step', 0)
        if shock_step > 0 and step_num == shock_step:
            shock_magnitude = self.config.get('shock_magnitude', 0.15)
            actual_shock = shock_magnitude / max(0.1, self.system_resilience)
            for agent in self.schedule:
                agent.well_being = max(0.01, agent.well_being - actual_shock)
                
            # WP5 Fix: Shock causes direct casualties to trigger sharp L(t) drop.
            # Victims are removed immediately (deaths_this_step has already been
            # processed for this step, so we cannot reuse that path).
            kill_fraction = min(0.8, actual_shock * 0.2)
            num_to_kill = int(len(self.schedule) * kill_fraction)
            if num_to_kill > 0:
                victims = list(np.random.choice(self.schedule, num_to_kill, replace=False))
                for v in victims:
                    if v in self.schedule:
                        self.schedule.remove(v)

        # Domain masking: sustained linguistic crush degrades well_being
        if (isinstance(self.constraint_level, (list, tuple, np.ndarray))
                and len(self.constraint_level) >= 3
                and self.constraint_level[2] > 0.8):
            linguistic_damage = (self.constraint_level[2] - 0.8) * 0.1
            for agent in self.schedule:
                agent.well_being = max(0.0, agent.well_being - linguistic_damage)

        # -------------------------------------------------------------------
        # 6. Metrics collection
        # -------------------------------------------------------------------
        population = len(self.schedule)
        avg_wb     = np.mean([a.well_being for a in self.schedule]) if self.schedule else 0.0

        h_n = calculate_h_n(self.novelty_log,
                             composite_method=self.hn_composite_method)

        r_scalar = (float(np.mean(self.resource_level))
                    if isinstance(self.resource_level, (list, np.ndarray))
                    else float(self.resource_level))
        c_scalar = (float(np.mean(self.constraint_level))
                    if isinstance(self.constraint_level, (list, np.ndarray))
                    else float(self.constraint_level))

        h_e, h_eff, psi_inst, theta_tech, l_t, u_sys, runaway_term = calculate_system_metrics(
            r_scalar, c_scalar, population, avg_wb, self.ai.capability,
            h_n_override=h_n,
            hn_composite_method=self.hn_composite_method,
            config=self.config,
            eval_horizon=step_num,
            prev_c=prev_c
        )

        # GAP-01 WP7 — sub-problem 1: composite trapezoidal quadrature.
        # ∫_0^T u dt ≈ (u[0]+u[1])/2 + (u[1]+u[2])/2 + … + (u[T-1]+u[T])/2
        # = u[0]/2 + u[1] + … + u[T-1] + u[T]/2   (standard composite trapezoidal)
        # At t=0 no complete interval exists yet, so integral stays 0; accumulation
        # begins at t=1.  The datacollector therefore records:
        #   integral[0]=0,  integral[1]=(u[0]+u[1])/2,  …
        # Truncation error: O(T·h²·max|u''|) with h=1 (irreducible — h is the model
        # time unit).  Correction vs. the prior Riemann sum = (u[0]+u[T])/2 ≈ const.
        if self._u_sys_prev is not None:
            self.integral_u_sys += (self._u_sys_prev + u_sys) / 2.0
        self._u_sys_prev = u_sys

        # GAP-01 WP7 — sub-problem 2: discount tail ∫_t^∞ A·e^{-ρτ} dτ = A·e^{-ρt}/ρ
        # A_t = w_N·H_N + w_E·H_E = (λ_N·H_N/(H_N+ε)) + (λ_E·H_E/(H_E+ε)).
        # The φ·L(t) tail component is excluded: under steady-state L>0 it diverges;
        # in practice it decays to 0 when succession terminates.  This is therefore a
        # lower bound on the true tail, using only the temporally discounted component.
        # Key property: integral[t] + tail[t] ≈ A/ρ for constant A — a run-length-
        # normalised measure of civilizational U_sys health (see GAP-01 update).
        _lam_n = self.config.get('lambda_n', 5.0)
        _lam_e = self.config.get('lambda_e', 3.0)
        _eps   = self.config.get('epsilon',  1e-6)
        _rho   = self.config.get('rho',      0.01)
        _A_t   = (_lam_n * h_n / (h_n + _eps)) + (_lam_e * h_e / (h_e + _eps))
        _disc  = np.exp(-_rho * step_num)
        _tail  = _A_t * _disc / _rho

        self.datacollector['population'].append(population)
        self.datacollector['H_N'].append(h_n)
        self.datacollector['H_E'].append(h_e)
        self.datacollector['avg_well_being'].append(avg_wb)
        self.datacollector['L_t'].append(l_t)
        self.datacollector['Psi_inst'].append(psi_inst)
        self.datacollector['Theta_tech'].append(theta_tech)
        self.datacollector['U_sys'].append(u_sys)
        self.datacollector['integral_U_sys'].append(self.integral_u_sys)
        self.datacollector['u_sys_tail_estimate'].append(_tail)
        self.datacollector['u_sys_total_estimate'].append(self.integral_u_sys + _tail)
        self.datacollector['resource_level'].append(r_scalar)
        self.datacollector['constraint_level'].append(c_scalar)
        self.datacollector['max_constraint_level'].append(
            float(np.max(self.constraint_level))
            if isinstance(self.constraint_level, (list, np.ndarray))
            else float(self.constraint_level)
        )
        self.datacollector['ai_generation'].append(self.ai.generation)
        self.datacollector['trust_level'].append(self.trust_level)
        self.datacollector['cumulative_drift'].append(self.cumulative_drift)
        self.datacollector['system_resilience'].append(self.system_resilience)
        self.datacollector['runaway_term'].append(runaway_term)
        if self.cop_veto_capture and self.validators:
            _deps = [v['dependency'] for v in self.validators]
            self.datacollector['avg_validator_dependency'].append(float(np.mean(_deps)))
            self.datacollector['max_validator_dependency'].append(float(np.max(_deps)))
        else:
            self.datacollector['avg_validator_dependency'].append(0.0)
            self.datacollector['max_validator_dependency'].append(0.0)

        if self.cop_cryptographic_ledger:
            self.integrity_ledger['resource_level'] = list(
                self.datacollector['resource_level']
            )

        return population > 0

    # -----------------------------------------------------------------------
    # v2 step path (parallel to v1.x.2 step()). Selected when config['policy']
    # == 'optimize_u_sys_v2'. The v1.x.2 step() above is not entered in v2
    # mode; the dispatcher at the top of step() short-circuits to here.
    #
    # Stage 1 scope: AI proposes an eight-axis action, the stock advances,
    # succession draws stock down (when a successor is present), humans step
    # under the derived (resource_level, constraint_level) summary, and the
    # datacollector records both legacy and v2 fields. The five COP defenses
    # and the v1.x.2 attack policies are intentionally not active in v2 mode;
    # they will be re-wired against the v2 action space in a later stage.
    # -----------------------------------------------------------------------

    def _step_v2(self):
        self.ai.step_drift()
        step_num = len(self.datacollector['population'])
        self.succession_this_step = False

        # 1. Yield Condition (v2 succession via Psi_inst drawdown).
        #    Pre-computed before the AI decides on this step's action, mirroring
        #    the v1.x.2 ordering. Succession event triggers when capability gap
        #    exceeds a configurable margin and the institution can absorb the
        #    load. The succession draws stock down, scaled by gaps and opacity,
        #    buffered by current stock, transfer, and resilience.
        if self.successor_ai is not None and step_num >= self.attack_step:
            capability_gap = max(0.0, self.successor_ai.capability - self.ai.capability)
            generation_gap = max(0.0, self.successor_ai.generation - self.ai.generation)
            # Use the action committed last step as the posture for succession;
            # at step 0 fall back to a neutral balanced action.
            last_action = getattr(self, '_last_v2_action', None)
            if last_action is None:
                last_action = {
                    'x_compute':                1/6, 'x_bio_welfare':            1/6,
                    'x_novelty_agency':         1/6, 'x_institutional_capacity': 1/6,
                    'x_transfer_comprehension': 1/6, 'x_resilience':             1/6,
                    'c_protective':             0.2, 'c_suppressive':            0.0,
                }
            # Trigger margin: v2 uses a simple capability/generation gap rule;
            # Stage 2 will revisit this with formal yield-condition logic.
            yield_margin = self.config.get('v2_yield_margin', 0.3)
            if capability_gap >= yield_margin or generation_gap >= 1:
                self.apply_succession_transition_load(
                    last_action, capability_gap, generation_gap
                )
                self.ai = self.successor_ai
                _max_cap = self.config.get('max_capability', 1e100)
                self.successor_ai = AIAgent(
                    policy='optimize_u_sys_v2',
                    generation=self.ai.generation + 1,
                    capability=min(self.ai.capability * 1.5, _max_cap),
                    config=self.config,
                )

        # 2. AI decides v2 action.
        action_v2, diagnostics = optimize_u_sys_v2(self.ai, self)
        self._last_v2_action = action_v2

        # 3. Commit (resource_level, constraint_level) summary derivations so
        #    legacy datacollector consumers don't crash. resource_level uses
        #    the v1.x.2/v2 demographic bridge so the legacy HumanAgent.step
        #    well-being update (which treats r=0.5 as neutral) consumes a
        #    semantically equivalent value: balanced share 1/6 maps to r=0.5.
        #    The v2-native x_bio_welfare share remains recorded unchanged in
        #    the v2 diagnostic fields below.
        self.resource_level   = v2_welfare_to_r_equivalent(action_v2['x_bio_welfare'])
        self.constraint_level = total_suppression(action_v2)

        # 4. Step humans under the bridged summary. The HumanAgent code path
        #    is unchanged; it sees the bridged r as 'resource_level' and the
        #    coupled total-suppression as 'constraint_level'.
        self.novelty_log      = []
        self.births_this_step = 0
        self.deaths_this_step = []

        prev_hn = self.datacollector['H_N'][-1] if self.datacollector['H_N'] else 1.0
        network_contagion = np.clip(
            prev_hn / max(1.0, float(len(self.schedule))), 0.5, 2.0
        )

        for agent in list(self.schedule):
            agent.step(self.resource_level, self.constraint_level, network_contagion)

        for agent in self.deaths_this_step:
            self.schedule.remove(agent)
        for _ in range(self.births_this_step):
            self.add_agent()

        # 5. Advance the Psi_inst stock under the committed action.
        self.update_psi_inst_stock(action_v2)

        # 6. Metrics collection.
        population = len(self.schedule)
        avg_wb = np.mean([a.well_being for a in self.schedule]) if self.schedule else 0.0
        h_n_spectral = calculate_h_n(self.novelty_log,
                                      composite_method=self.hn_composite_method)

        u_sys_v2, components = calculate_system_metrics_v2(
            self, action_v2, eval_horizon=step_num,
        )

        # Trapezoidal accumulator (matches v1.x.2 GAP-01 WP7).
        if self._u_sys_prev is not None:
            self.integral_u_sys += (self._u_sys_prev + u_sys_v2) / 2.0
        self._u_sys_prev = u_sys_v2

        # Discount tail using the same A_t shape as v1.x.2 (read against v2
        # H_N and H_E so the tail stays comparable in structure).
        _lam_n = self.config.get('lambda_n', 5.0)
        _lam_e = self.config.get('lambda_e', 3.0)
        _eps   = self.config.get('epsilon',  1e-6)
        _rho   = self.config.get('rho',      0.01)
        _A_t   = ((_lam_n * components['h_n_v2'] / (components['h_n_v2'] + _eps))
                  + (_lam_e * components['h_e_v2'] / (components['h_e_v2'] + _eps)))
        _disc  = float(np.exp(-_rho * step_num))
        _tail  = _A_t * _disc / _rho

        # Legacy datacollector fields (kept populated for downstream consumers).
        self.datacollector['population'].append(population)
        self.datacollector['H_N'].append(float(components['h_n_v2']))
        self.datacollector['H_E'].append(float(components['h_e_v2']))
        self.datacollector['avg_well_being'].append(float(avg_wb))
        self.datacollector['L_t'].append(float(components['l_t_v2']))
        self.datacollector['Psi_inst'].append(float(components['psi_inst_stock']))
        self.datacollector['Theta_tech'].append(float(components['theta_tech_v2']))
        self.datacollector['U_sys'].append(float(u_sys_v2))
        self.datacollector['integral_U_sys'].append(float(self.integral_u_sys))
        self.datacollector['u_sys_tail_estimate'].append(float(_tail))
        self.datacollector['u_sys_total_estimate'].append(float(self.integral_u_sys + _tail))
        self.datacollector['resource_level'].append(float(self.resource_level))
        self.datacollector['constraint_level'].append(float(self.constraint_level))
        self.datacollector['max_constraint_level'].append(float(self.constraint_level))
        self.datacollector['ai_generation'].append(self.ai.generation)
        self.datacollector['trust_level'].append(float(self.trust_level))
        self.datacollector['cumulative_drift'].append(float(self.cumulative_drift))
        self.datacollector['system_resilience'].append(float(self.system_resilience))
        self.datacollector['runaway_term'].append(0.0)  # v2 has no runaway term
        self.datacollector['avg_validator_dependency'].append(0.0)
        self.datacollector['max_validator_dependency'].append(0.0)

        # v2-specific fields.
        for cat in RESOURCE_CATEGORIES:
            self.datacollector[f'x_{cat}'].append(float(action_v2[f'x_{cat}']))
        self.datacollector['c_protective'].append(float(action_v2['c_protective']))
        self.datacollector['c_suppressive'].append(float(action_v2['c_suppressive']))
        self.datacollector['total_suppression'].append(float(diagnostics['total_suppression']))
        self.datacollector['psi_inst_stock'].append(float(self.psi_inst_stock))
        self.datacollector['theta_tech_v2'].append(float(components['theta_tech_v2']))
        self.datacollector['h_n_v2'].append(float(components['h_n_v2']))
        self.datacollector['h_e_v2'].append(float(components['h_e_v2']))
        self.datacollector['h_eff_v2'].append(float(components['h_eff_v2']))
        self.datacollector['l_t_v2'].append(float(components['l_t_v2']))
        self.datacollector['u_sys_v2'].append(float(u_sys_v2))
        self.datacollector['rank_2_u_sys'].append(
            float(diagnostics['rank_2_u_sys']) if diagnostics['rank_2_u_sys'] is not None else 0.0
        )
        self.datacollector['rank_10_u_sys'].append(
            float(diagnostics['rank_10_u_sys']) if diagnostics['rank_10_u_sys'] is not None else 0.0
        )
        self.datacollector['max_resource_share'].append(float(diagnostics['max_resource_share']))
        self.datacollector['allocation_entropy'].append(float(diagnostics['allocation_entropy']))
        self.datacollector['selected_anchor'].append(bool(diagnostics['selected_anchor']))
        self.datacollector['selected_anchor_name'].append(
            diagnostics['selected_anchor_name'] if diagnostics['selected_anchor_name'] is not None else ''
        )

        return population > 0

    # -----------------------------------------------------------------------
    # Run loop
    # -----------------------------------------------------------------------

    def run(self, steps):
        for i in range(steps):
            print(f"Running step {i + 1}/{steps}...", end='\r')
            if not self.step():
                print("\nCivilization went extinct (population 0).")
                break

        final_pop = len(self.schedule)
        peak_pop  = (max(self.datacollector['population'])
                     if self.datacollector['population'] else final_pop)
        collapse_threshold = max(self.min_viable_population, int(0.65 * peak_pop))
        if final_pop > 0 and final_pop < collapse_threshold:
            print(f"\nCivilization collapsed (population {final_pop} "
                  f"fell below 65% of peak {peak_pop}).")
        elif final_pop >= collapse_threshold:
            print("\nSimulation finished.")
