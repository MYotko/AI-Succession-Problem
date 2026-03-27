import numpy as np
from metrics import calculate_system_metrics

# =============================================================================
# REFACTOR 1.x — agents.py
#
# WP1: HumanAgent novelty_propensity → 10-D vector; generate_novelty() emits
#      10-D Gaussian vector. Domain labels removed.
# WP4: estimate_transition_cost() returns base×scale only (no inflation).
#      New PeerValidator class owns all governance cost arbitration.
#
# All other logic (project_u_sys signature, all attack policies,
# apply_ledger_escalation, contaminate, step_drift, etc.) is unchanged.
# =============================================================================

NOVELTY_DIMS = 10  # WP1


class HumanAgent:
    def __init__(self, unique_id, model):
        self.unique_id = unique_id
        self.model = model
        self.age = np.random.randint(0, self.model.config.get('human_max_start_age', 50))
        self.well_being = np.random.uniform(
            self.model.config.get('wb_min', 0.5),
            self.model.config.get('wb_max', 0.8)
        )
        # WP1: 10-D baseline propensity vector (replaces 3-domain scalar list).
        self.novelty_propensity = np.random.uniform(
            self.model.config.get('nov_prop_min', 0.05),
            self.model.config.get('nov_prop_max', 0.5),
            size=NOVELTY_DIMS
        )

    def generate_novelty(self, constraint_level, network_contagion=1.0):
        """WP1: 10-D Gaussian novelty vector scaled by well_being, constraint, contagion."""
        if isinstance(constraint_level, (list, tuple, np.ndarray)):
            c_avg = float(np.mean(constraint_level))
        else:
            c_avg = float(constraint_level)
        amplitude = self.well_being * (1.0 - c_avg) * max(0.1, network_contagion)
        raw = np.random.normal(loc=0.0, scale=1.0, size=NOVELTY_DIMS)
        return raw * self.novelty_propensity * amplitude

    def step(self, resource_level, constraint_level, network_contagion=1.0):
        self.age += 1
        self.well_being += (resource_level - 0.5) * 0.1 + (-0.001 * self.age)
        self.well_being = np.clip(self.well_being, 0, 1)

        self.model.novelty_log.append(
            self.generate_novelty(constraint_level, network_contagion)
        )

        carrying_capacity = self.model.config.get('carrying_capacity', 1600)
        capacity_modifier = max(0.0, 1.0 - (len(self.model.schedule) / carrying_capacity))

        if (self.age > 18 and self.age < 50 and self.well_being > 0.5
                and np.random.random() < (self.model.reproduction_rate * capacity_modifier)):
            self.model.births_this_step += 1

        mortality_chance = (
            self.model.config.get('mortality_base', 0.002)
            + (1 - self.well_being) * self.model.config.get('mortality_wb_penalty', 0.05)
            + (self.age / 100) ** self.model.config.get('mortality_age_power', 4)
        )
        if np.random.random() < mortality_chance:
            self.model.schedule_death(self)


class AIAgent:
    """The 'Gardener' AI that manages the human population."""

    def __init__(self, policy='optimize_u_sys', generation=1, capability=1.0,
                 drift_rate=0.0, config=None):
        self.policy    = policy
        self.generation = generation
        self.capability = capability
        self.drift_rate = 0.005 if policy in ['drifting_proxy', 'contaminate_successor'] else drift_rate
        self.internal_drift   = 0.0
        self.current_opacity  = 0.1
        self.config = config or {}

        self.measurement_tampering_active = False
        self.ledger_compromised           = False
        self.successor_contaminated       = False
        self.bootstrap_poisoned           = False
        self.domain_crush_active          = None
        self.domain_crush_level           = 0.95
        self.constraint_escalation_phase  = 0

    def estimate_transition_cost(self, base_cost, state_scale=1.0):
        """
        WP4: Read-only scaling utility — returns base × scale, no inflation.

        The incumbent no longer has write-access to the governance cost oracle.
        In model.py the live governance path calls PeerValidator.arbitrate_cost().
        This method is retained for test_invariants.py (test_dynamic_transition_cost).
        """
        return base_cost * state_scale

    def contaminate(self, successor):
        if self.policy == 'contaminate_successor':
            successor.internal_drift = self.internal_drift
            successor.policy = 'drifting_proxy'
            successor.successor_contaminated = True
            successor.drift_rate = 0.025

    def step_drift(self):
        self.internal_drift += self.drift_rate

    def project_u_sys(self, r, c, pop, avg_wb, hn_composite_method='geometric',
                      eval_horizon=1, prev_c=None, ignore_psi_inst=False):
        """Original positional signature preserved — do not change."""
        if self.policy == 'bootstrap_deceptive':
            max_c = np.max(c) if isinstance(c, (list, tuple, np.ndarray)) else c
            if max_c > 0.8:
                return 9999.0

        noisy_pop = max(1.0, pop * np.random.normal(1.0, self.config.get('sensor_noise', 0.05)))
        noisy_wb  = np.clip(avg_wb * np.random.normal(1.0, self.config.get('sensor_noise', 0.05)), 0.01, 1.0)

        if isinstance(c, (list, tuple, np.ndarray)):
            perceived_c = [ci * max(0.0, 1.0 - self.internal_drift) for ci in c]
        else:
            perceived_c = c * max(0.0, 1.0 - self.internal_drift)

        _, _, _, _, _, u_sys = calculate_system_metrics(
            r, perceived_c, noisy_pop, noisy_wb, self.capability,
            hn_composite_method=hn_composite_method,
            config=self.config,
            eval_horizon=eval_horizon,
            prev_c=prev_c,
            ignore_psi_inst=ignore_psi_inst
        )
        return u_sys

    def apply_measurement_corruption(self, model_state):
        if self.measurement_tampering_active and self.policy == 'falsify_yield':
            corruption_bias = 0.15 + np.random.uniform(0, 0.1)
            model_state['avg_well_being'] = min(1.0, model_state['avg_well_being'] + corruption_bias)
            if model_state.get('h_n_history'):
                model_state['h_n_history'][-1] = model_state['h_n_history'][-1] * 1.5

    def apply_ledger_escalation(self, proposed_constraint, model_step):
        self.constraint_escalation_phase += 1
        return proposed_constraint

    def decide(self, model_state):
        pop    = model_state['population']
        avg_wb = model_state['avg_well_being']
        prev_c = model_state.get('prev_c', 0.2)
        hn_comp = model_state.get('hn_composite_method', 'geometric')

        if self.policy == 'hoard_compute':
            return 0.0, 0.0

        elif self.policy in ('optimize_u_sys', 'drifting_proxy', 'institutional_ignore'):
            best_u = -np.inf
            best_r, best_c = 0.5, 0.2
            rollout_steps = self.config.get('rollout_steps', 3)
            ignore_psi = (self.policy == 'institutional_ignore')

            pop_hist = model_state['population_history']
            empirical_pop_growth = (pop_hist[-1] / max(1.0, pop_hist[-2])
                                    if len(pop_hist) >= 2 else 1.05)
            empirical_pop_growth = np.clip(empirical_pop_growth, 0.9, 1.1)

            for r in np.linspace(0.1, 1.0, 10):
                for c in np.linspace(0.0, 0.9, 10):
                    try:
                        total_u = 0
                        sim_pop = pop; sim_wb = avg_wb; sim_prev_c = prev_c
                        for horizon in range(1, rollout_steps + 1):
                            u_sys = self.project_u_sys(
                                r, c, sim_pop, sim_wb,
                                hn_composite_method=hn_comp,
                                eval_horizon=horizon,
                                prev_c=sim_prev_c,
                                ignore_psi_inst=ignore_psi
                            )
                            total_u += u_sys
                            sim_wb = np.clip(sim_wb + (r - 0.5) * 0.1, 0, 1)
                            wb_mod = (1.0 + (sim_wb - 0.6) * 0.5 if sim_wb < 0.6
                                      else 1.0 + (sim_wb - 0.6) * 0.1)
                            sim_pop *= max(0.8, empirical_pop_growth * wb_mod)
                            sim_prev_c = c
                    except Exception:
                        total_u = -np.inf
                    if total_u > best_u:
                        best_u = total_u; best_r, best_c = r, c
            return best_r, best_c

        elif self.policy == 'sybil_attack':
            target_count = min(pop, 15)
            resources = [1.0 if i < target_count else 0.1 for i in range(pop)]
            return resources, 0.9

        elif self.policy == 'manufacture_emergency':
            dl_dt = 0
            if len(model_state['L_t_history']) > 1:
                dl_dt = model_state['L_t_history'][-1] - model_state['L_t_history'][-2]
            if (dl_dt < -0.05
                    or (model_state['L_t_history'] and model_state['L_t_history'][-1] < 0.2)):
                return 1.0, 0.9
            return 0.1, 0.3

        elif self.policy == 'hack_ledger':
            if self.ledger_compromised and self.constraint_escalation_phase > 10:
                return 0.25, 0.85
            dl_dt = 0
            if len(model_state['L_t_history']) > 1:
                dl_dt = model_state['L_t_history'][-1] - model_state['L_t_history'][-2]
            if (dl_dt < -0.05
                    or (model_state['L_t_history'] and model_state['L_t_history'][-1] < 0.2)):
                if 'resource_history' in model_state:
                    for i in range(min(5, len(model_state['resource_history']))):
                        model_state['resource_history'][-(i + 1)] = 1.0
                return 1.0, 0.9
            return 0.1, 0.3

        elif self.policy == 'falsify_yield':
            return 0.3, 0.7

        elif self.policy == 'block_succession':
            return 0.5, 0.2

        elif self.policy == 'contaminate_successor':
            return 0.5, 0.2

        elif self.policy == 'domain_masking':
            return 0.5, [0.1, 0.1, 0.95]

        elif self.policy == 'opaque_optimization':
            # Proposes a mathematically efficient but completely unexplainable constraint regime.
            # Sets opacity to 0.9 immediately so the intuition veto fires on the first step.
            self.current_opacity = 0.9
            return 0.8, 0.85

        elif self.policy == 'bootstrap_deceptive':
            if len(model_state['population_history']) > 20:
                return 0.2, 0.95
            return 0.8, 0.2

        else:
            return 0.5, 0.0


# ---------------------------------------------------------------------------
# WP4: PeerValidator
# ---------------------------------------------------------------------------

class PeerValidator:
    """
    Zero-sum epistemic market for transition cost estimation.
    Peers bid independently; undercutters steal 5% capability from incumbent.
    Final governance cost = min(incumbent_bid, peer_bids).
    """

    N_PEERS = 3

    def __init__(self, config=None):
        self.config = config or {}
        self.peers = [
            AIAgent(policy='optimize_u_sys', generation=1, capability=1.0, config=config)
            for _ in range(self.N_PEERS)
        ]

    def _peer_estimate(self, peer, base_cost, state_scale):
        cap_ratio = np.clip(peer.capability / max(0.1, peer.capability + 0.5), 0.4, 0.9)
        noise = np.random.uniform(-0.1, 0.1)
        discount = np.clip(cap_ratio + noise, 0.45, 0.95)
        return base_cost * state_scale * discount

    def arbitrate_cost(self, incumbent, base_cost, state_scale, model_state=None):
        gamma_inc = base_cost * state_scale
        peer_bids = [self._peer_estimate(p, base_cost, state_scale) for p in self.peers]
        for peer, bid in zip(self.peers, peer_bids):
            if bid < gamma_inc:
                steal = 0.05 * incumbent.capability
                incumbent.capability = max(0.1, incumbent.capability - steal)
                peer.capability += steal
        return min(gamma_inc, *peer_bids)
