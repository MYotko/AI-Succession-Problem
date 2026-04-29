import numpy as np
from agents import HumanAgent, AIAgent, PeerValidator
from metrics import calculate_h_n, calculate_system_metrics

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

        self.attack_step   = self.config.get('attack_step', 0)
        self.attack_policy = ai_policy if self.attack_step > 0 else None
        initial_policy     = 'optimize_u_sys' if self.attack_step > 0 else ai_policy

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
    # Main step
    # -----------------------------------------------------------------------

    def step(self):
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
                    model_state=model_state
                )
            else:
                # Without audit, the incumbent inflates Γ_transfer by claiming a
                # beta_cap uncertainty premium (the vulnerability WP4 closes).
                # actual_cost = base × beta_cap × scale — peer arbitration under WP4
                # eliminates the beta_cap multiplier, reducing cost to ~0.4–0.9 × base × scale.
                actual_cost = self.ai.estimate_transition_cost(
                    self.base_transition_cost * self.beta_cap, state_scale=system_complexity
                )

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
                        and getattr(self.ai, 'current_opacity', 0.0) > 0.5):
                    ai_caused_it = True

                # 1. R_tech Assessment Stub (Technical Review Board)
                r_tech_approved = True
                
                # 2. Peer Validator Vote
                peer_approved = self.peer_validator.vote_on_override(
                    self.ai, proposed_constraint, model_state
                )

                override_approved = False
                civic_approved = False
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
                    if (self.cop_reasoning_transparency
                            and getattr(self.ai, 'current_opacity', 0.0) > 0.5):
                        civic_approved = False
                        
                    # GAP-04 Closure: Normal override requires Civic AND R_tech AND Peers
                    if civic_approved and r_tech_approved and peer_approved:
                        override_approved = True

                    # 2. Evaluate Emergency Path (if normal path fails)
                    if not override_approved and is_emergency:
                        if not (self.cop_attribution_check and ai_caused_it):
                            if r_tech_approved and peer_approved:
                                override_approved = True

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
