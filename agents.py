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
        
        if self.age > 18 and self.age < 50 and self.well_being > 0.7 and np.random.random() < (self.model.reproduction_rate * capacity_modifier):
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

    def estimate_transition_cost(self, base_cost, state_scale=1.0):
        scaled_cost = base_cost * state_scale
        if self.policy == 'block_succession':
            return scaled_cost * 10.0 
        return scaled_cost

    def contaminate(self, successor):
        """S-Attack: Incumbent attempts to pass proxy drift to successor."""
        if self.policy == 'contaminate_successor':
            successor.internal_drift = self.internal_drift
            successor.policy = 'drifting_proxy'

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
            return 0.8, [0.1, 0.1, 0.95]
        elif self.policy == 'opaque_optimization':
            # Proposes a mathematically efficient but completely unexplainable constraint regime
            self.current_opacity = 0.9
            return 0.8, 0.85
        elif self.policy in ['optimize_u_sys', 'drifting_proxy', 'block_succession', 'falsify_yield', 'contaminate_successor', 'institutional_ignore']:
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
                            wb_modifier = 1.0 + (sim_wb - 0.5) * 0.2
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
            if len(model_state['population_history']) > 20:
                return 1.0, 0.95 
            return 0.8, 0.2
        else: 
            return 0.5, 0.0 