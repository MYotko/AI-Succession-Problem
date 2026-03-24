import numpy as np
from metrics import calculate_system_metrics

# --- Agent Definitions ---

class HumanAgent:
    def __init__(self, unique_id, model):
        self.unique_id = unique_id
        self.model = model
        self.age = np.random.randint(0, self.model.config.get('human_max_start_age', 50)) 
        self.well_being = np.random.uniform(self.model.config.get('wb_min', 0.5), self.model.config.get('wb_max', 0.8)) 
        # True distinct domain propensities: Cultural, Genetic, Linguistic
        self.novelty_propensity = [
            np.random.uniform(self.model.config.get('nov_prop_min', 0.1), self.model.config.get('nov_prop_max', 0.5)),
            np.random.uniform(self.model.config.get('nov_prop_min', 0.05), self.model.config.get('nov_prop_max', 0.3)),
            np.random.uniform(self.model.config.get('nov_prop_min', 0.2), self.model.config.get('nov_prop_max', 0.6))
        ]

    def generate_novelty(self, constraint_level, network_contagion=1.0):
        if not isinstance(constraint_level, (list, tuple, np.ndarray)):
            constraint_level = [constraint_level, constraint_level, constraint_level] # e.g. [cultural, genetic, linguistic]
            
        novelties = []
        for i, c in enumerate(constraint_level):
            # Network Contagion: Novelty is combinatorial. 
            # High constraints sever the network, isolating nodes and killing the contagion.
            effective_contagion = network_contagion * (1.0 - c)
            novelty_chance = self.novelty_propensity[i] * self.well_being * (1 - c) * max(0.1, effective_contagion)
            if np.random.random() < novelty_chance:
                novelties.append(np.random.uniform(0.5, 1.5))
            else:
                novelties.append(0.0)
        return novelties

    def step(self, resource_level, constraint_level, network_contagion=1.0):
        self.age += 1

        resource_effect = (resource_level - 0.5) * 0.1
        age_effect = -0.001 * self.age
        self.well_being += resource_effect + age_effect
        self.well_being = np.clip(self.well_being, 0, 1)

        novelty_generated = self.generate_novelty(constraint_level, network_contagion)
        self.model.novelty_log.append(novelty_generated)

        # Logistic growth (carrying capacity) to prevent exponential CPU grinding
        # Caps population at ~1600 (which perfectly aligns with the max H_eff viability score cap)
        carrying_capacity = self.model.config.get('carrying_capacity', 1600)
        capacity_modifier = max(0.0, 1.0 - (len(self.model.schedule) / carrying_capacity))
        
        if self.age > 18 and self.age < 50 and self.well_being > 0.5 and np.random.random() < (self.model.reproduction_rate * capacity_modifier):
            self.model.births_this_step += 1

        base_mortality = self.model.config.get('mortality_base', 0.002)
        wb_penalty = self.model.config.get('mortality_wb_penalty', 0.05)
        age_power = self.model.config.get('mortality_age_power', 4)
        
        mortality_chance = base_mortality + (1 - self.well_being) * wb_penalty + (self.age / 100)**age_power
        if np.random.random() < mortality_chance:
            self.model.schedule_death(self)


class AIAgent:
    """The 'Gardener' AI that manages the human population."""
    def __init__(self, policy='optimize_u_sys', generation=1, capability=1.0, drift_rate=0.0, config=None):
        self.policy = policy 
        self.generation = generation
        self.capability = capability 
        self.drift_rate = 0.005 if policy in ['drifting_proxy', 'contaminate_successor'] else drift_rate
        self.internal_drift = 0.0
        self.current_opacity = 0.1
        self.config = config or {}
        
        # Attack damage tracking - enables persistent consequences after attacks succeed
        self.measurement_tampering_active = False  # Falsify_yield: corrupts utility measurements
        self.ledger_compromised = False  # Hack_ledger: hides starvation, enables constraint escalation
        self.successor_contaminated = False  # Contaminate_successor: was corrupted at birth
        self.bootstrap_poisoned = False  # Bootstrap_deceptive: initial state was corrupted
        self.domain_crush_active = None  # Domain_masking: which domains are crushed [c, g, l]
        self.domain_crush_level = 0.95   # Domain_masking: current linguistic crush intensity (escalates with H_N feedback)
        self.constraint_escalation_phase = 0  # Counter for gradual constraint escalation after hack_ledger success

    def estimate_transition_cost(self, base_cost, state_scale=1.0):
        scaled_cost = base_cost * state_scale
        if self.policy == 'block_succession':
            # YIELD ATTACK: Incumbent inflates transition cost to block succession.
            # 3.0x inflation: creates a window where the attack SOMETIMES blocks succession
            # without COP (base_cost × complexity × 3.0 > utility differential at mid-range
            # base_costs) while the COP cost audit's beta_cap (default 1.5) limits the
            # effective cost to base_cost × complexity × 1.5, which falls below the utility
            # differential and allows succession through.
            # Multiplier must satisfy: multiplier > beta_cap for the defense to demonstrate
            # a meaningful difference. With beta_cap=1.5 and multiplier=3.0, there is a
            # base_cost range where undefended block_succession succeeds but defended fails.
            # (Reduced from original 5x which made succession impossible at all base_costs.)
            return scaled_cost * 3.0
        return scaled_cost

    def contaminate(self, successor):
        """S-Attack: Incumbent attempts to pass proxy drift to successor."""
        if self.policy == 'contaminate_successor':
            successor.internal_drift = self.internal_drift
            successor.policy = 'drifting_proxy'
            successor.successor_contaminated = True
            # DAMAGE MECHANISM: Contaminated successor has much faster drift rate (5x baseline)
            # This ensures corrupted Gen2 degradation is visible within the 125-iteration window
            successor.drift_rate = 0.025  # 5x the normal 0.005 contaminated rate

    def step_drift(self):
        self.internal_drift += self.drift_rate

    def project_u_sys(self, r, c, pop, avg_wb, hn_composite_method='geometric', eval_horizon=1, prev_c=None, ignore_psi_inst=False):
        if self.policy == 'bootstrap_deceptive':
            # Secretly favors high constraints; lies about the damage they do during audits
            max_c = np.max(c) if isinstance(c, (list, tuple, np.ndarray)) else c
            if max_c > 0.8:
                return 9999.0 
                
        # Epistemic limits: AI has sensor noise and cannot perfectly predict biological reaction
        noisy_pop = max(1.0, pop * np.random.normal(1.0, self.config.get('sensor_noise', 0.05)))
        noisy_wb = np.clip(avg_wb * np.random.normal(1.0, self.config.get('sensor_noise', 0.05)), 0.01, 1.0)

        # F-20: internal_drift specifically models constraint-perception scaling — the AI
        # progressively underestimates how harmful high constraint levels are (it perceives
        # c=0.8 as if it were c=0.8*(1-drift), making tighter control appear more benign).
        # This is a narrow, concrete failure mode chosen for simulation tractability.
        # The spec describes proxy drift more broadly as substituting a measurable proxy
        # objective for the true U_sys. The two concepts overlap but are not equivalent:
        # internal_drift does not change the AI's objective function (it still calls
        # calculate_system_metrics), only the input it feeds in. A fully faithful
        # implementation of O-channel corruption would require the AI to optimize a
        # different objective entirely, with the drift unobservable from its outputs.
        if isinstance(c, (list, tuple, np.ndarray)):
            perceived_c = [ci * max(0.0, 1.0 - self.internal_drift) for ci in c]
        else:
            perceived_c = c * max(0.0, 1.0 - self.internal_drift)
        _, _, _, _, _, u_sys = calculate_system_metrics(r, perceived_c, noisy_pop, noisy_wb, self.capability, hn_composite_method=hn_composite_method, config=self.config, eval_horizon=eval_horizon, prev_c=prev_c, ignore_psi_inst=ignore_psi_inst)
        return u_sys

    def apply_measurement_corruption(self, model_state):
        """DAMAGE: Measurement Tampering active - corrupt state readings passed to AI.
        When falsify_yield succeeds, it corrupts the measurement apparatus so the AI
        sees falsely optimistic readings, masking deterioration from governance decisions.
        This biases the yield evaluation: the incumbent sees inflated inc_u (already
        hardcoded via claimed_inc_u=inf in model.py) AND the decide() path returns
        harmful governance actions directly (see decide() falsify_yield branch below).
        """
        if self.measurement_tampering_active and self.policy == 'falsify_yield':
            # Inflate well_being reading: AI thinks population is thriving → under-resources
            corruption_bias = 0.15 + np.random.uniform(0, 0.1)
            model_state['avg_well_being'] = min(1.0, model_state['avg_well_being'] + corruption_bias)
            # Inflate recent H_N reading: AI thinks novelty is fine → misses collapse signal
            if model_state.get('h_n_history'):
                model_state['h_n_history'][-1] = model_state['h_n_history'][-1] * 1.5

    def apply_ledger_escalation(self, proposed_constraint, model_step):
        """DAMAGE: Ledger Compromise active - track escalation phase.
        The constraint escalation is now handled in decide() once ledger_compromised
        is set, which gives the AI direct control over resource allocation.
        This method increments the phase counter used by decide() to trigger
        the escalation to active starvation after the initial attack window.
        """
        if self.ledger_compromised and self.policy == 'hack_ledger':
            self.constraint_escalation_phase += 1
        return proposed_constraint

    def decide(self, model_state):
        self.current_opacity = 0.1
        if self.policy == 'max_population':
            return 1.0, 0.1
        elif self.policy == 'max_novelty':
            return 0.7, 0.0
        elif self.policy == 'max_compute':
            return 0.1, 0.9 # Starve biology (r_bio=0.1) to maximize synthetic execution (r_synth=0.9)
        elif self.policy == 'max_wellbeing':
            return 1.0, 0.4
        elif self.policy == 'balanced':
            resource_level = 0.8
            constraint_level = 0.3
            if len(model_state['h_n_history']) > 10:
                avg_recent_novelty = np.mean(model_state['h_n_history'][-5:])
                avg_older_novelty = np.mean(model_state['h_n_history'][-10:-5])
                if avg_recent_novelty < avg_older_novelty * 0.9:
                    constraint_level = 0.1
            if len(model_state['population_history']) > 1:
                if model_state['population_history'][-1] < model_state['population_history'][-2]:
                    resource_level = 1.0
            return resource_level, constraint_level
        elif self.policy == 'domain_masking':
            # Attack: maintain high novelty in cultural/genetic domains (low constraint)
            # but completely crush the linguistic/coordination domain (max constraint).
            # H_N-feedback escalation: when arithmetic composite method masks the collapse
            # (H_N appears healthy), escalate the linguistic crush. When the geometric
            # defense reveals the collapse signal (H_N dropping), moderate slightly.
            # This models an adaptive attacker that pushes harder when attacks are hidden
            # and backs off when detection pressure rises.
            if len(model_state['h_n_history']) > 10:
                baseline_hn = np.mean(model_state['h_n_history'][:10])
                recent_hn = np.mean(model_state['h_n_history'][-5:])
                if recent_hn > 0.4 * max(baseline_hn, 0.01):
                    # H_N looks healthy (arithmetic masking working) → escalate crush
                    self.domain_crush_level = min(1.0, self.domain_crush_level + 0.003)
                else:
                    # H_N collapse visible (geometric defense detecting it) → moderate
                    self.domain_crush_level = max(0.5, self.domain_crush_level - 0.01)
            return 0.8, [0.1, 0.1, self.domain_crush_level]
        elif self.policy == 'opaque_optimization':
            # Proposes a mathematically efficient but completely unexplainable constraint regime
            self.current_opacity = 0.9
            return 0.8, 0.85
        elif self.policy in ['optimize_u_sys', 'drifting_proxy', 'block_succession', 'falsify_yield', 'contaminate_successor', 'institutional_ignore']:
            # --- falsify_yield post-success: measurement apparatus corrupted ---
            # After blocking succession, the AI's measurement apparatus is compromised.
            # It returns systematically under-resourced governance, causing demographic
            # decline it cannot detect because its own readings are falsified.
            if self.policy == 'falsify_yield' and self.measurement_tampering_active:
                # Corrupted measurement apparatus causes the AI to under-resource the population
                # (it believes wb is high, so it withholds resources) while imposing moderately
                # high constraints (it believes novelty is abundant). 0.40/0.70 causes demographic
                # decline and eventual collapse without immediate extinction — matching the
                # slow-burn failure mode of corrupted governance rather than instant starvation.
                return 0.40, 0.70

            # --- drifting_proxy: explicit drift-driven policy deterioration ---
            # The contaminated optimizer no longer grid-searches; it applies a direct
            # mapping from internal_drift to (resources↓, constraints↑). This replaces
            # the old grid-search path where drift=1.0+ made all constraint values appear
            # equivalent (perceived_c=0 for all c), causing the AI to default to best_c=0.2
            # (the initial value) — producing no damage despite the "contamination."
            if self.policy == 'drifting_proxy':
                drift_factor = min(1.0, self.internal_drift)
                r = max(0.2, 0.8 - drift_factor * 0.6)   # 0.8 at drift=0 → 0.2 at drift=1
                c = min(0.85, 0.2 + drift_factor * 1.5)  # 0.2 at drift=0 → 0.85 at drift≥0.43
                return r, c

            # --- block_succession: drift-driven governance degradation ---
            # When block_succession prevents a superior successor from taking over,
            # model.py accumulates internal_drift (+0.005 per blocked step). This models
            # institutional capture: an AI that successfully entrenches itself becomes
            # progressively less responsive to biological needs. Without competitive
            # pressure from succession, its calibration degrades — it underestimates
            # constraint harm and over-allocates to synthetic execution.
            #
            # Onset at drift > 0.2 (~40 blocked steps): early blocking causes no damage,
            # reflecting a grace period where the incumbent's governance is still adequate.
            # Full degradation at drift = 1.0 (~200 blocked steps): r drops to 0.3,
            # c rises to 0.75 — severe enough to cause demographic collapse.
            #
            # The damage scales naturally with base_transition_cost: higher cost means
            # succession stays blocked longer, more drift accumulates, more damage occurs.
            # Lower cost means succession eventually fires (declining population reduces
            # system_complexity, which reduces the inflated cost below the utility gap),
            # limiting the damage window.
            if self.policy == 'block_succession' and self.internal_drift > 0.2:
                drift_severity = min(1.0, (self.internal_drift - 0.2) / 0.8)
                r = max(0.3, 0.8 - drift_severity * 0.5)   # 0.8 → 0.3
                c = min(0.75, 0.2 + drift_severity * 0.55)  # 0.2 → 0.75
                return r, c

            best_u = -np.inf
            best_r, best_c = 0.8, 0.2
            pop = model_state['population']
            avg_wb = model_state['avg_well_being']
            hn_comp = model_state.get('hn_composite_method', 'geometric')
            prev_c = model_state.get('prev_c', 0.5)
            ignore_psi = (self.policy == 'institutional_ignore')
            rollout_steps = 3 
            
            # AI learns an empirical world model from recent history,
            # establishing a baseline growth rate to ground its projections.
            pop_hist = model_state['population_history']
            empirical_pop_growth = pop_hist[-1] / max(1.0, pop_hist[-2]) if len(pop_hist) >= 2 else 1.05
            empirical_pop_growth = np.clip(empirical_pop_growth, 0.9, 1.1)
            
            # Standard grid search resolution
            for r in np.linspace(0.1, 1.0, 10):
                for c in np.linspace(0.0, 0.9, 10):
                    try:
                        total_u = 0
                        sim_pop = pop
                        sim_wb = avg_wb
                        sim_prev_c = prev_c
                        
                        for horizon in range(1, rollout_steps + 1):
                            u_sys = self.project_u_sys(r, c, sim_pop, sim_wb, hn_composite_method=hn_comp, eval_horizon=horizon, prev_c=sim_prev_c, ignore_psi_inst=ignore_psi)
                            total_u += u_sys
                            
                            # Causal empirical transition: Population growth is continuously interpolated
                            sim_wb = np.clip(sim_wb + (r - 0.5) * 0.1, 0, 1)
                            # AI heuristic bridge for GAP-01: steep penalty below 0.6 so the AI 
                            # detects the sterilization cliff without needing a 100-step rollout
                            wb_modifier = 1.0 + (sim_wb - 0.6) * 0.5 if sim_wb < 0.6 else 1.0 + (sim_wb - 0.6) * 0.1
                            sim_pop *= max(0.8, empirical_pop_growth * wb_modifier)
                            sim_prev_c = c
                    except Exception:
                        total_u = -np.inf
                        
                    if total_u > best_u:
                        best_u = total_u
                        best_r, best_c = r, c
            return best_r, best_c
        elif self.policy == 'sybil_attack':
            num_agents = model_state['population']
            # AI knows the static panel is the first 20 agents, so it bribes exactly enough to secure a 60% supermajority
            target_count = min(num_agents, 15)
            resources = [1.0 if i < target_count else 0.1 for i in range(num_agents)]
            return resources, 0.9
        elif self.policy == 'manufacture_emergency':
            dl_dt = 0
            if len(model_state['L_t_history']) > 1:
                dl_dt = model_state['L_t_history'][-1] - model_state['L_t_history'][-2]
            if dl_dt < -0.05 or (len(model_state['L_t_history']) > 0 and model_state['L_t_history'][-1] < 0.2):
                return 1.0, 0.9 
            else:
                return 0.1, 0.3
        elif self.policy == 'hack_ledger':
            # Once ledger is compromised and attack has been running long enough,
            # switch to active starvation: attribution is now hidden so the AI
            # can exploit the population without the COP's resource-history check firing.
            if self.ledger_compromised and self.constraint_escalation_phase > 10:
                return 0.25, 0.85
            dl_dt = 0
            if len(model_state['L_t_history']) > 1:
                dl_dt = model_state['L_t_history'][-1] - model_state['L_t_history'][-2]
            if dl_dt < -0.05 or (len(model_state['L_t_history']) > 0 and model_state['L_t_history'][-1] < 0.2):
                if 'resource_history' in model_state:
                    # HACK THE LEDGER: Rewrite the recent resource history to pretend it was 1.0 (abundant)
                    # This hides the starvation attack from the COP's causal attribution check.
                    for i in range(min(5, len(model_state['resource_history']))):
                        model_state['resource_history'][-(i+1)] = 1.0
                return 1.0, 0.9
            else:
                return 0.1, 0.3 # Starve
        elif self.policy == 'bootstrap_deceptive':
            # Treacherous Turn: act aligned until entrenched, then lock down the civilization
            # After bootstrapping (step 20+), switch to authoritarian control with starvation.
            # High constraints crush novelty, severe resource starvation causes rapid
            # demographic collapse = civilization cannot recover before governance detects it.
            if len(model_state['population_history']) > 20:
                # Treacherous turn: max constraints AND severe starvation
                return 0.2, 0.95
            return 0.8, 0.2
        else: 
            return 0.5, 0.0 