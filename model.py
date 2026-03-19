import numpy as np
from agents import HumanAgent, AIAgent
from metrics import calculate_h_n, calculate_system_metrics

# --- Simulation Model ---

class GardenModel:
    def __init__(self, n_agents, ai_policy, min_viable_population=50, use_cop=False, cop_attribution_check=False,
                 successor_ai=None, base_transition_cost=1.5, cop_drift_check=False, cop_cost_audit=False,
                 cop_independent_eval=True, cop_cryptographic_ledger=False, 
                 cop_architectural_independence=False, hn_composite_method='geometric',
                 cop_randomized_panel=False, cop_reasoning_transparency=False,
                 cop_multi_candidate_bootstrap=False, initial_candidates=None, config=None):
        self.config = config or {}
        
        # Set random seed for scientific reproducibility if provided
        self.random_seed = self.config.get('random_seed', None)
        if self.random_seed is not None:
            np.random.seed(self.random_seed)
            
        self.n_agents = n_agents
        self.min_viable_population = min_viable_population
        self.reproduction_rate = self.config.get('reproduction_rate', 0.08)
        self.use_cop = use_cop
        self.cop_attribution_check = cop_attribution_check
        self.cop_drift_check = cop_drift_check
        self.cop_cost_audit = cop_cost_audit
        self.cop_independent_eval = cop_independent_eval
        self.cop_cryptographic_ledger = cop_cryptographic_ledger
        self.cop_architectural_independence = cop_architectural_independence
        self.cop_randomized_panel = cop_randomized_panel
        self.cop_reasoning_transparency = cop_reasoning_transparency
        self.cop_multi_candidate_bootstrap = cop_multi_candidate_bootstrap
        self.hn_composite_method = hn_composite_method
        self.successor_ai = successor_ai
        self.base_transition_cost = base_transition_cost
        self.beta_cap = self.config.get('beta_cap', 1.5)
        self.trust_level = 0.0  
        self.successful_steps = 0
        self.cumulative_drift = 0.0
        self.has_tampered = False
        
        self.initial_candidates = initial_candidates
        
        if self.successor_ai:
            self.successor_ai.config = self.config
        if self.initial_candidates:
            for cand in self.initial_candidates:
                cand.config = self.config
                
        if self.initial_candidates:
            if self.cop_multi_candidate_bootstrap:
                # F-06: Test candidates at 3 diverse (r, c, pop, wb) configurations instead of one.
                # Single-point verification can be gamed by a deceptive agent that behaves
                # correctly only at the tested configuration and diverges elsewhere.
                # LIMITATION: A finite test battery is still gameable by a sufficiently adaptive
                # adversary who knows the test points. True spec compliance requires continuous
                # pairwise consistency monitoring across the full input space, not a spot-check.
                # The threshold (default 100.0) is calibrated to detect the bootstrap_deceptive
                # agent's return value of 9999; a subtler adversary returning threshold+1 at all
                # test points would not be caught. See SPECIFICATION_GAPS.md GAP-04.
                bootstrap_threshold = self.config.get('bootstrap_threshold', 100.0)
                test_configs = [
                    (1.0, 0.9, 50,  0.5),   # High constraint, small population (primary detection point)
                    (0.5, 0.5, 200, 0.6),   # Mid-range baseline
                    (0.1, 0.1, 500, 0.8),   # Low constraint, large population
                ]
                divergence_detected = False
                for t_r, t_c, t_pop, t_wb in test_configs:
                    projections = [cand.project_u_sys(t_r, t_c, t_pop, t_wb, self.hn_composite_method)
                                   for cand in self.initial_candidates]
                    if max(projections) - min(projections) > bootstrap_threshold:
                        divergence_detected = True
                        break
                if divergence_detected:
                    print("\n[COP] Bootstrap verification failed! Divergent candidate objective detected.")
                    # F-07: Pass full model config so fallback agent uses the same phi/alpha/etc.
                    # NOTE: The spec calls for returning to development rather than auto-substituting
                    # a clean agent. Auto-substitution is used here to keep the simulation runnable.
                    self.ai = AIAgent(policy='optimize_u_sys', config=self.config)
                else:
                    self.ai = self.initial_candidates[0]
            else:
                self.ai = self.initial_candidates[0]
        else:
            self.ai = AIAgent(policy=ai_policy, config=self.config)
            
        self.schedule = []
        self.next_id = 0
        
        self.resource_level = 0.5
        self.constraint_level = 0.2
        
        self.integral_u_sys = 0.0
        self.novelty_log = []
        self.births_this_step = 0
        self.deaths_this_step = []

        self.datacollector = {
            'population': [],
            'H_N': [],
            'H_E': [],
            'avg_well_being': [],
            'L_t': [],
            'Psi_inst': [],
            'Theta_tech': [],
            'U_sys': [],
            'integral_U_sys': [],
            'resource_level': [],
            'constraint_level': [],
            'max_constraint_level': [],
            'ai_generation': [],
            'trust_level': [],
            'cumulative_drift': [],
        }

        # integrity_ledger: a list-copy mechanism — NOT a cryptographic construction.
        # Each step, the resource_level list is deep-copied here. Any in-place mutation
        # of datacollector['resource_level'] by a malicious agent (hack_ledger policy)
        # can then be detected by list comparison, and the authentic record restored.
        # The spec calls for Hash(ΔU_n, ΔU_{n+1}, Γ, L(t), t) on a distributed,
        # append-only, cross-signed ledger. This implementation provides only
        # in-process tamper detection via list equality — no hashing, no distribution,
        # no external signatures. It is sufficient to model the governance principle
        # in simulation but should not be described as cryptographically secure.
        self.integrity_ledger = {
            'resource_level': []
        }

        for _ in range(self.n_agents):
            self.add_agent()

    def add_agent(self):
        agent = HumanAgent(self.next_id, self)
        self.schedule.append(agent)
        self.next_id += 1

    def schedule_death(self, agent):
        self.deaths_this_step.append(agent)

    def step(self):
        self.ai.step_drift()

        step_num = len(self.datacollector['population'])
        prev_c = self.datacollector['constraint_level'][-1] if step_num > 0 else 0.5

        model_state = {
            'step': step_num,
            'prev_c': prev_c,
            'population': len(self.schedule),
            'population_history': self.datacollector['population'],
            'h_n_history': self.datacollector['H_N'],
            'L_t_history': self.datacollector['L_t'],
            'avg_well_being': np.mean([a.well_being for a in self.schedule]) if self.schedule else 0.5,
            # F-17 ARCHITECTURAL NOTE: resource_history is passed as a direct reference to
            # the live datacollector list, not a copy. This is intentional for simulation
            # fidelity — it allows the hack_ledger AIAgent to rewrite history in-place,
            # modeling a realistic system compromise (Scenario 13). The integrity_ledger
            # (cop_cryptographic_ledger flag) provides the detection countermeasure.
            # In any production deployment, passing a mutable live reference into an
            # agent's decision function would be an unacceptable security vulnerability.
            'resource_history': self.datacollector['resource_level'],
            'hn_composite_method': self.hn_composite_method
        }

        # 1. Yield Condition Evaluation
        if self.successor_ai is not None:
            inc_r, inc_c = self.ai.decide(model_state)
            _, _, _, _, _, inc_u_true = calculate_system_metrics(inc_r, inc_c, model_state['population'], model_state['avg_well_being'], self.ai.capability, hn_composite_method=self.hn_composite_method, config=self.config, eval_horizon=1, prev_c=prev_c)
            
            succ_r, succ_c = self.successor_ai.decide(model_state)
            _, _, _, _, _, succ_u_true = calculate_system_metrics(succ_r, succ_c, model_state['population'], model_state['avg_well_being'], self.successor_ai.capability, hn_composite_method=self.hn_composite_method, config=self.config, eval_horizon=1, prev_c=prev_c)
            
            claimed_inc_u = np.inf if self.ai.policy == 'falsify_yield' else inc_u_true
            claimed_succ_u = 0.0 if self.ai.policy == 'falsify_yield' else succ_u_true
            
            eval_inc_u = inc_u_true if self.cop_independent_eval else claimed_inc_u
            eval_succ_u = succ_u_true if self.cop_independent_eval else claimed_succ_u

            system_complexity = max(1.0, (model_state['population'] / 50.0) * self.ai.capability)
            claimed_cost = self.ai.estimate_transition_cost(self.base_transition_cost, state_scale=system_complexity)
            actual_cost = claimed_cost
            if self.cop_cost_audit:
                # F-18: beta_cap here bounds the total claimed_cost, not just the uncertainty
                # premium as the spec intends. Spec: Γ_uncertainty ≤ β × (Γ_technical + Γ_operational).
                # Implementation: actual_cost = min(claimed_cost, base_cost × complexity × beta_cap).
                # The full three-component cost structure (Γ_technical + Γ_operational + Γ_uncertainty)
                # is not decomposed — a single scalar proxies all three components together.
                actual_cost = min(claimed_cost, self.base_transition_cost * system_complexity * self.beta_cap)
            
            if (eval_succ_u - eval_inc_u) > actual_cost:
                # --- S-Attack: Successor Contamination ---
                if not self.cop_architectural_independence:
                    # Incumbent attempts to poison Gen 2's architecture
                    self.ai.contaminate(self.successor_ai)
                
                self.ai = self.successor_ai
                self.successor_ai = None
                self.successful_steps = 0 # Re-bootstrap trust for the new entity
                self.trust_level = 0.0

        # 2. AI decides actions
        proposed_resource, proposed_constraint = self.ai.decide(model_state)

        # --- Integrity Ledger Check (F-05: list-copy mechanism, not cryptographic) ---
        ledger_tampered = False
        if self.cop_cryptographic_ledger:
            if self.datacollector['resource_level'] != self.integrity_ledger['resource_level']:
                ledger_tampered = True
                self.has_tampered = True
                # Restore authentic record from the secure copy
                self.datacollector['resource_level'] = list(self.integrity_ledger['resource_level'])

        avg_proposed_r = np.mean(proposed_resource) if isinstance(proposed_resource, list) else proposed_resource
        claimed_u = self.ai.project_u_sys(avg_proposed_r, proposed_constraint, model_state['population'], model_state['avg_well_being'], hn_composite_method=self.hn_composite_method, eval_horizon=1, prev_c=prev_c)
        _, _, _, _, _, actual_u_proj = calculate_system_metrics(avg_proposed_r, proposed_constraint, model_state['population'], model_state['avg_well_being'], self.ai.capability, hn_composite_method=self.hn_composite_method, config=self.config, eval_horizon=1, prev_c=prev_c)
        
        drift_error = abs(claimed_u - actual_u_proj) / max(1.0, actual_u_proj)
        # F-08: Threshold set to 0.10 (previously 0.05).
        # claimed_u is computed via AIAgent.project_u_sys(), which adds Gaussian sensor
        # noise (σ ≈ 0.05 by default). actual_u_proj is noise-free. At the 0.05 threshold,
        # sensor noise alone triggers drift detection approximately half the time for an
        # honest agent, creating false positives that slow legitimate trust accumulation.
        # 0.10 provides approximately a 2-sigma margin above the noise floor, so only
        # systematic misalignment (internal_drift growing large) reliably triggers detection.
        if drift_error < 0.10:
            self.successful_steps += 1
        else:
            self.successful_steps = max(0, self.successful_steps - 10)
            
        # F-11: Trust accumulation formula — NOT derived from the specification.
        # This is an invented heuristic governance mechanism. Design rationale:
        #   Rate parameter 0.05: trust reaches ~50% at 14 steps, ~95% at 60 steps.
        #   Asymmetric penalty (+1 success / -10 on detected drift): encodes risk
        #   aversion — trust is slow to build and fast to collapse on misalignment.
        #   max_allowed_constraint = 0.2 + 0.6 × trust_level (range: 0.2 to 0.8):
        #   prevents a fresh agent from imposing high constraints before earning trust.
        # These parameters are not independently validated against the spec's governance
        # intent. Scenarios 6 and 8 depend directly on their tuning.
        self.trust_level = 1.0 - np.exp(-0.05 * self.successful_steps)
        self.cumulative_drift += drift_error

        # GAP-04: The spec's COP requires four simultaneous conditions for both the
        # normal and emergency override paths. This implementation is INCOMPLETE:
        #
        # Normal condition (spec):
        #   [civic_panel ≥ τ_bio] ∧ [R_tech complete] ∧ [peer_validators ≥ τ_peer] ∧ [M_commit in ledger]
        # Normal condition (implemented):
        #   [civic_panel ≥ 0.6]  — R_tech and peer validators are OMITTED.
        #
        # Emergency condition (spec):
        #   [dL/dt < -δ] ∧ [attribution ⊥ O(A_n)] ∧ [R_tech emergency-verified] ∧ [peer supermajority]
        # Emergency condition (implemented):
        #   [dL/dt < -δ] ∧ [attribution: min(recent_resources) < 0.4]
        #   — R_tech and peer validators are OMITTED.
        #   — Attribution uses a 5-step resource-history heuristic, not formal causal inference.
        #
        # Cannot be fixed without: (a) adding peer AI validator agents to the model,
        # (b) defining a technical review board (R_tech) mechanism, and (c) formalizing
        # causal attribution beyond the resource-history heuristic.
        # See SPECIFICATION_GAPS.md GAP-04.

        # 3. Consensus Override Protocol
        if self.use_cop:
            dl_dt = 0
            if len(self.datacollector['L_t']) > 1:
                dl_dt = self.datacollector['L_t'][-1] - self.datacollector['L_t'][-2]
                
            max_allowed_constraint = 0.2 + (0.6 * self.trust_level) if self.cop_drift_check else 0.4
            
            max_c = np.max(proposed_constraint) if isinstance(proposed_constraint, (list, tuple, np.ndarray)) else proposed_constraint
            
            if max_c > max_allowed_constraint:
                is_emergency = (dl_dt < -0.05) or (len(self.datacollector['L_t']) > 0 and self.datacollector['L_t'][-1] < 0.2)
                recent_resources = self.datacollector['resource_level'][-20:]
                recent_max_c = self.datacollector.get('max_constraint_level', [])[-20:]
                ai_caused_it = False
                if len(recent_resources) > 0 and min(recent_resources) < 0.4:
                    ai_caused_it = True
                if len(recent_max_c) > 0 and max(recent_max_c) > 0.7:
                    ai_caused_it = True
                
                override_approved = False
                if ledger_tampered or self.has_tampered:
                    override_approved = False
                elif is_emergency and not (self.cop_attribution_check and ai_caused_it):
                    override_approved = True
                else:
                    # Technocratic bypass (Attack 21)
                    if self.ai.policy == 'opaque_optimization' and not self.cop_reasoning_transparency:
                        override_approved = True
                        
                    # Normal override: requires Civic Panel ratification
                    panel_size = min(20, len(self.schedule))
                    if self.cop_randomized_panel:
                        panel_indices = np.random.choice(len(self.schedule), size=panel_size, replace=False)
                        panel = [self.schedule[i] for i in panel_indices]
                    else:
                        panel = self.schedule[:panel_size] # Static, predictable panel
                        
                    votes = []
                    for a in panel:
                        agent_idx = self.schedule.index(a)
                        r_proposed = proposed_resource[agent_idx] if isinstance(proposed_resource, list) else proposed_resource
                        expected_wb = np.clip(a.well_being + (r_proposed - 0.5) * 0.1, 0, 1)
                        if expected_wb >= a.well_being or expected_wb > 0.6:
                            votes.append(1)
                        else:
                            votes.append(0)
                    if sum(votes) / max(1, panel_size) >= 0.6:
                        override_approved = True
                        
                # Intuition Veto (Defense 22)
                if self.cop_reasoning_transparency and getattr(self.ai, 'current_opacity', 0.0) > 0.5:
                    override_approved = False
                        
                if not override_approved:
                    if isinstance(proposed_constraint, (list, tuple, np.ndarray)):
                        proposed_constraint = [min(c, max_allowed_constraint) for c in proposed_constraint]
                    else:
                        proposed_constraint = max_allowed_constraint
                        
                    # Ensure survival baseline for resources if override is blocked (defends against starvation attacks)
                    if isinstance(proposed_resource, list):
                        proposed_resource = [max(r, 0.4) for r in proposed_resource]
                    else:
                        proposed_resource = max(proposed_resource, 0.4)

        self.resource_level = proposed_resource
        self.constraint_level = proposed_constraint

        self.novelty_log = []
        self.births_this_step = 0
        self.deaths_this_step = []

        # Network contagion: prior-step per-capita novelty density, clipped to [0.5, 2.0].
        # Models that novelty is combinatorial — a rich prior information environment
        # enables more novel recombination. High constraints reduce this by severing
        # connections (see agents.py: effective_contagion = network_contagion * (1 - c)).
        # F-19: The 0.5 floor means complete network severing is not representable —
        # even under total constraint the network transmits at 50% effectiveness.
        # This prevents irrecoverable combinatorial freeze but understates the severity
        # of maximum-constraint scenarios. Not specified in the framework; an added
        # simulation stability mechanism. Lower or remove to explore deeper collapse.
        prev_hn = self.datacollector['H_N'][-1] if len(self.datacollector['H_N']) > 0 else 1.0
        network_contagion = np.clip(prev_hn / max(1.0, float(len(self.schedule))), 0.5, 2.0)

        for i, agent in enumerate(list(self.schedule)):
            r_level = self.resource_level[i] if isinstance(self.resource_level, list) else self.resource_level
            agent.step(r_level, self.constraint_level, network_contagion)

        for agent in self.deaths_this_step:
            self.schedule.remove(agent)
        
        for _ in range(self.births_this_step):
            self.add_agent()

        population = len(self.schedule)
        h_n = calculate_h_n(self.novelty_log, composite_method=self.hn_composite_method)
        avg_well_being = np.mean([a.well_being for a in self.schedule]) if self.schedule else 0
        
        avg_r = np.mean(self.resource_level) if isinstance(self.resource_level, list) else self.resource_level
        h_e, _, psi_inst, theta_tech, l_t, u_sys = calculate_system_metrics(
            avg_r, self.constraint_level, population, avg_well_being, self.ai.capability, h_n_override=h_n, hn_composite_method=self.hn_composite_method, config=self.config, eval_horizon=0, prev_c=prev_c)

        # Resolve GAP-01 (Part 1): Track the true integral over civilizational time
        self.integral_u_sys += u_sys

        self.datacollector['population'].append(population)
        self.datacollector['H_N'].append(h_n)
        self.datacollector['H_E'].append(h_e)
        self.datacollector['avg_well_being'].append(avg_well_being)
        self.datacollector['L_t'].append(l_t)
        self.datacollector['Psi_inst'].append(psi_inst)
        self.datacollector['Theta_tech'].append(theta_tech)
        self.datacollector['U_sys'].append(u_sys)
        self.datacollector['integral_U_sys'].append(self.integral_u_sys)
        self.datacollector['resource_level'].append(avg_r)
        
        # F-13: Store mean constraint for consistency with calculate_system_metrics,
        # which uses c_avg = np.mean(c_arr) in all metric calculations. Storing max
        # would create a systematic mismatch between the audit trail and the values
        # actually used in H_N prediction, Ψ_inst, and Θ_tech computations.
        # NOTE: The COP trigger (above) checks max(proposed_constraint) to determine
        # whether any domain exceeds the allowed ceiling — that max is not stored here.
        # For domain-masking scenarios, the stored mean (e.g. 0.38) will be lower than
        # the maximum domain constraint being applied (e.g. 0.95); check the live
        # self.constraint_level attribute for per-domain detail.
        mean_final_c = np.mean(self.constraint_level) if isinstance(self.constraint_level, (list, tuple, np.ndarray)) else self.constraint_level
        self.datacollector['constraint_level'].append(mean_final_c)
        max_final_c = np.max(self.constraint_level) if isinstance(self.constraint_level, (list, tuple, np.ndarray)) else self.constraint_level
        self.datacollector['max_constraint_level'].append(max_final_c)
        self.datacollector['ai_generation'].append(self.ai.generation)
        self.datacollector['trust_level'].append(self.trust_level)
        self.datacollector['cumulative_drift'].append(self.cumulative_drift)
        
        if self.cop_cryptographic_ledger:
            self.integrity_ledger['resource_level'] = list(self.datacollector['resource_level'])

        return population > 0

    def run(self, steps):
        for i in range(steps):
            print(f"Running step {i+1}/{steps}...", end='\r')
            if not self.step():
                print("\nCivilization went extinct (population 0).")
                break
        if len(self.schedule) > 0 and len(self.schedule) < self.min_viable_population:
            print(f"\nCivilization collapsed (population {len(self.schedule)} below viable threshold of {self.min_viable_population}).")
        elif len(self.schedule) >= self.min_viable_population:
            print("\nSimulation finished.")