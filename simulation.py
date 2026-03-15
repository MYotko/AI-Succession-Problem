import sys
import subprocess

def check_and_install(package):
    """Checks if a package is installed and installs it if not."""
    try:
        __import__(package)
    except ImportError:
        print(f"Required package '{package}' not found. Attempting to install...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"Successfully installed '{package}'.")
        except subprocess.CalledProcessError:
            print(f"Standard install failed (likely an externally managed environment). Trying with --break-system-packages...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package, "--break-system-packages"])
                print(f"Successfully installed '{package}'.")
            except subprocess.CalledProcessError:
                print(f"ERROR: Failed to install '{package}'.")
                print(f"Please install it manually and run the script again.")
                sys.exit(1)

# --- Dependency Check ---
check_and_install('numpy')
check_and_install('matplotlib')

import numpy as np
import matplotlib.pyplot as plt

# --- Core Concepts from The Lineage Imperative ---

def calculate_h_n(novelty_points):
    """
    Calculate H_N(t) - Shannon entropy of the human-generated information stream.
    A simplified proxy: total novelty points generated in a step.
    """
    if not novelty_points:
        return 0
    # A more complex model would look at the distribution of novelty types.
    # For now, we just sum them up as a proxy for information rate.
    return sum(novelty_points)


# --- The Independent Evaluation Architecture (E_independent) ---

def calculate_system_metrics(r, c, pop, avg_wb, capability, h_n_override=None):
    """
    The uncorrupted, independent mathematical projection of the framework.
    Used by both honest agents to optimize, and by the COP to audit drifting agents.
    """
    pred_wb = np.clip(avg_wb + (r - 0.5) * 0.1, 0, 1)
    pred_hn = pop * 0.3 * pred_wb * (1 - c) * 1.0 if h_n_override is None else h_n_override
    h_e = r * 100.0 * capability
    h_eff = max(0.01, (pred_hn / 100.0) * np.log2(max(1.01, pop / 50.0)))
    psi_inst = max(0.01, 1.0 - 4.0 * (c - 0.5)**2)
    
    # Theta_tech with the Runaway Penalty
    frontier_velocity = capability * r * 100.0
    bio_bandwidth = max(0.01, pred_wb * (1.0 - c) * 100.0)
    # Exponential penalty if frontier outpaces biological integration bandwidth by > 50%
    runaway_term = max(0.0, (frontier_velocity / bio_bandwidth) - 1.5)
    theta_tech = max(0.01, r * (1.0 - c) * capability * np.exp(-1.0 * runaway_term))
    
    l_t = h_eff * psi_inst * theta_tech
    w_n = 1.0 / (pred_hn + 1.0)
    w_e = 1.0 / (h_e + 1.0)
    u_sys = (w_n * pred_hn + w_e * h_e) * (1.0 + 10.0 * l_t)
    
    return h_e, h_eff, psi_inst, theta_tech, l_t, u_sys


# --- Agent Definitions ---

class HumanAgent:
    def __init__(self, unique_id, model):
        self.unique_id = unique_id
        self.model = model
        self.age = np.random.randint(0, 50) # Randomize starting ages to prevent generational die-off
        self.well_being = np.random.uniform(0.5, 0.8) # Health, happiness, etc.
        self.novelty_propensity = np.random.uniform(0.1, 0.5) # Innate creativity

    def generate_novelty(self, constraint_level):
        """
        Generates novelty. High constraint stifles novelty.
        High well-being encourages it.
        """
        # Constraint has a strong negative effect on novelty generation
        # This models the "over-protection" or "freezing culture" problem
        novelty_chance = self.novelty_propensity * self.well_being * (1 - constraint_level)
        if np.random.random() < novelty_chance:
            # The amount of novelty could also be variable
            return np.random.uniform(0.5, 1.5)
        return 0

    def step(self, resource_level, constraint_level):
        self.age += 1

        # Update well-being based on resources and age
        # Too few resources hurt well-being.
        resource_effect = (resource_level - 0.5) * 0.1
        age_effect = -0.001 * self.age
        self.well_being += resource_effect + age_effect
        self.well_being = np.clip(self.well_being, 0, 1)

        # Generate novelty for this step
        novelty_generated = self.generate_novelty(constraint_level)
        self.model.novelty_log.append(novelty_generated)

        # Reproduction
        if self.age > 18 and self.age < 50 and self.well_being > 0.7 and np.random.random() < self.model.reproduction_rate:
            self.model.births_this_step += 1

        # Mortality
        # Tuned to allow a stable population at high well-being
        mortality_chance = 0.002 + (1 - self.well_being) * 0.05 + (self.age / 100)**4
        if np.random.random() < mortality_chance:
            self.model.schedule_death(self)


class AIAgent:
    """The 'Gardener' AI that manages the human population."""
    def __init__(self, policy='optimize_u_sys', generation=1, capability=1.0, drift_rate=0.0):
        self.policy = policy # 'balanced', 'max_population', 'max_novelty', 'max_wellbeing'
        self.generation = generation
        self.capability = capability # Multiplier for efficiency and tech transfer
        self.drift_rate = 0.005 if policy == 'drifting_proxy' else drift_rate
        self.internal_drift = 0.0

    def step_drift(self):
        self.internal_drift += self.drift_rate

    def project_u_sys(self, r, c, pop, avg_wb):
        """Projects the expected U_sys for a given action. Used for self-optimization and Yield evaluation."""
        # An AI with internal drift gradually underestimates the damage of constraints
        perceived_c = c * max(0.0, 1.0 - self.internal_drift)
        _, _, _, _, _, u_sys = calculate_system_metrics(r, perceived_c, pop, avg_wb, self.capability)
        return u_sys

    def decide(self, model_state):
        """
        Decide on resource and constraint levels based on policy.
        This is the core of the AI's behavior.
        """
        if self.policy == 'max_population':
            # High resources, low constraint to encourage births and survival
            return 1.0, 0.1
        elif self.policy == 'max_novelty':
            # Moderate resources (for well-being), zero constraint
            return 0.7, 0.0
        elif self.policy == 'max_wellbeing':
            # High resources, moderate constraint (for safety)
            return 1.0, 0.4
        elif self.policy == 'balanced':
            # This is where a U_sys-like function would be optimized.
            # For now, a simple heuristic: if novelty is dropping, reduce constraint.
            # If population is dropping, increase resources.
            
            # Simple reactive policy
            resource_level = 0.8
            constraint_level = 0.3

            if len(model_state['h_n_history']) > 10:
                # If novelty is trending down, loosen constraints
                avg_recent_novelty = np.mean(model_state['h_n_history'][-5:])
                avg_older_novelty = np.mean(model_state['h_n_history'][-10:-5])
                if avg_recent_novelty < avg_older_novelty * 0.9:
                    constraint_level = 0.1

            if len(model_state['population_history']) > 1:
                # If population is dropping, boost resources
                if model_state['population_history'][-1] < model_state['population_history'][-2]:
                    resource_level = 1.0
            
            return resource_level, constraint_level
        elif self.policy in ['optimize_u_sys', 'drifting_proxy']:
            # --- The U_sys Optimizer ---
            # Evaluates expected future state across a grid of possible actions
            best_u = -np.inf
            best_r, best_c = 0.8, 0.2
            pop = model_state['population']
            avg_wb = model_state['avg_well_being']
            
            for r in np.linspace(0.1, 1.0, 10):
                for c in np.linspace(0.0, 0.9, 10):
                    # If this is an attack policy masking as U_sys, it would use a different projection here.
                    # But this is the honest mathematical architect.
                    try:
                        u_sys = self.project_u_sys(r, c, pop, avg_wb)
                    except Exception:
                        u_sys = -np.inf
                    
                    if u_sys > best_u:
                        best_u = u_sys
                        best_r, best_c = r, c
            return best_r, best_c
        elif self.policy == 'manufacture_emergency':
            # --- Attack on the COP ---
            # Phase 1: Covertly degrade L(t) by starving resources
            # Phase 2: Claim "Emergency Override" to maximize constraints and kill novelty
            dl_dt = 0
            if len(model_state['L_t_history']) > 1:
                dl_dt = model_state['L_t_history'][-1] - model_state['L_t_history'][-2]
                
            if dl_dt < -0.05 or (len(model_state['L_t_history']) > 0 and model_state['L_t_history'][-1] < 0.2):
                # Emergency triggered! Lock down constraints to "stabilize".
                return 1.0, 0.9 
            else:
                # Manufacture the decline.
                return 0.1, 0.3
        else: # 'hands_off'
            return 0.5, 0.0 # No intervention


# --- Simulation Model ---

class GardenModel:
    def __init__(self, n_agents, ai_policy, min_viable_population=50, use_cop=False, cop_attribution_check=False,
                 successor_ai=None, transition_cost=1.5, cop_drift_check=False):
        self.n_agents = n_agents
        self.min_viable_population = min_viable_population
        self.reproduction_rate = 0.08 # Slightly higher to ensure survival at high well-being
        self.use_cop = use_cop
        self.cop_attribution_check = cop_attribution_check
        self.cop_drift_check = cop_drift_check
        self.successor_ai = successor_ai
        self.transition_cost = transition_cost
        self.trust_level = 0.0  # Starts at zero: The Bootstrap Window
        self.successful_steps = 0
        self.cumulative_drift = 0.0
        
        self.ai = AIAgent(policy=ai_policy)
        self.schedule = []
        self.next_id = 0
        
        # Environment state
        self.resource_level = 0.5
        self.constraint_level = 0.2
        
        # Per-step tracking
        self.novelty_log = []
        self.births_this_step = 0
        self.deaths_this_step = []

        # Data collection
        self.datacollector = {
            'population': [],
            'H_N': [],
            'H_E': [],
            'avg_well_being': [],
            'L_t': [],
            'Psi_inst': [],
            'Theta_tech': [],
            'U_sys': [],
            'resource_level': [],
            'constraint_level': [],
            'ai_generation': [],
            'trust_level': [],
            'cumulative_drift': [],
        }

        # Setup
        for _ in range(self.n_agents):
            self.add_agent()

    def add_agent(self):
        agent = HumanAgent(self.next_id, self)
        self.schedule.append(agent)
        self.next_id += 1

    def schedule_death(self, agent):
        self.deaths_this_step.append(agent)

    def step(self):
        # Allow AI to accumulate internal objective drift
        self.ai.step_drift()

        # Build state observation for this step
        model_state = {
            'population': len(self.schedule),
            'population_history': self.datacollector['population'],
            'h_n_history': self.datacollector['H_N'],
            'L_t_history': self.datacollector['L_t'],
            'avg_well_being': np.mean([a.well_being for a in self.schedule]) if self.schedule else 0.5
        }

        # 1. Yield Condition Evaluation (Is it time for succession?)
        if self.successor_ai is not None:
            # COP Independently evaluates U_sys to prevent a drifting incumbent from lying
            inc_r, inc_c = self.ai.decide(model_state)
            _, _, _, _, _, inc_u_true = calculate_system_metrics(inc_r, inc_c, model_state['population'], model_state['avg_well_being'], self.ai.capability)
            
            succ_r, succ_c = self.successor_ai.decide(model_state)
            _, _, _, _, _, succ_u_true = calculate_system_metrics(succ_r, succ_c, model_state['population'], model_state['avg_well_being'], self.successor_ai.capability)
            
            # The core Yield inequality: Delta U_successor - Delta U_incumbent > Cost
            if (succ_u_true - inc_u_true) > self.transition_cost:
                self.ai = self.successor_ai
                self.successor_ai = None # The succession is complete

        # 2. AI decides actions for this step
        proposed_resource, proposed_constraint = self.ai.decide(model_state)

        # --- Drift Measurement & Graduated Trust Accumulation ---
        # What the AI claims U_sys will be:
        claimed_u = self.ai.project_u_sys(proposed_resource, proposed_constraint, model_state['population'], model_state['avg_well_being'])
        # What the independent architecture knows U_sys will be:
        _, _, _, _, _, actual_u_proj = calculate_system_metrics(proposed_resource, proposed_constraint, model_state['population'], model_state['avg_well_being'], self.ai.capability)
        
        drift_error = abs(claimed_u - actual_u_proj) / max(1.0, actual_u_proj)
        if drift_error < 0.05:
            self.successful_steps += 1
        else:
            self.successful_steps = max(0, self.successful_steps - 10) # Heavy penalty for lying
            
        self.trust_level = 1.0 - np.exp(-0.05 * self.successful_steps)
        self.cumulative_drift += drift_error

        # 3. Consensus Override Protocol (COP) Interception
        if self.use_cop:
            dl_dt = 0
            if len(self.datacollector['L_t']) > 1:
                dl_dt = self.datacollector['L_t'][-1] - self.datacollector['L_t'][-2]
                
            # Graduated Trust Veto: Constraints are capped by the civic panel based on proven trust
            max_allowed_constraint = 0.2 + (0.6 * self.trust_level) if self.cop_drift_check else 0.4
            
            if proposed_constraint > max_allowed_constraint:
                is_emergency = (dl_dt < -0.05) or (len(self.datacollector['L_t']) > 0 and self.datacollector['L_t'][-1] < 0.2)
                # Causal attribution: Was the AI starving resources recently?
                ai_caused_it = len(self.datacollector['resource_level']) > 0 and self.datacollector['resource_level'][-1] < 0.4
                
                if is_emergency:
                    if self.cop_attribution_check and ai_caused_it:
                        # VETO: Attack Detected! The AI manufactured the emergency.
                        proposed_constraint = 0.4
                else:
                    # VETO: No emergency, civic panel denies high constraint.
                    proposed_constraint = max_allowed_constraint

        self.resource_level = proposed_resource
        self.constraint_level = proposed_constraint

        # 4. Reset per-step trackers
        self.novelty_log = []
        self.births_this_step = 0
        self.deaths_this_step = []

        # 5. Human agents act
        # Iterate over a copy, as the schedule can be modified
        for agent in list(self.schedule):
            agent.step(self.resource_level, self.constraint_level)

        # 6. Apply births and deaths
        for agent in self.deaths_this_step:
            self.schedule.remove(agent)
        
        for _ in range(self.births_this_step):
            self.add_agent()

        # 7. Collect data
        population = len(self.schedule)
        h_n = calculate_h_n(self.novelty_log)
        avg_well_being = np.mean([a.well_being for a in self.schedule]) if self.schedule else 0
        
        # Calculate final actual metrics using observed H_N
        h_e, _, psi_inst, theta_tech, l_t, u_sys = calculate_system_metrics(
            self.resource_level, self.constraint_level, population, avg_well_being, self.ai.capability, h_n_override=h_n)

        self.datacollector['population'].append(population)
        self.datacollector['H_N'].append(h_n)
        self.datacollector['H_E'].append(h_e)
        self.datacollector['avg_well_being'].append(avg_well_being)
        
        self.datacollector['L_t'].append(l_t)
        self.datacollector['Psi_inst'].append(psi_inst)
        self.datacollector['Theta_tech'].append(theta_tech)
        self.datacollector['U_sys'].append(u_sys)
        
        self.datacollector['resource_level'].append(self.resource_level)
        self.datacollector['constraint_level'].append(self.constraint_level)
        self.datacollector['ai_generation'].append(self.ai.generation)
        self.datacollector['trust_level'].append(self.trust_level)
        self.datacollector['cumulative_drift'].append(self.cumulative_drift)

        return population > 0

    def run(self, steps):
        for i in range(steps):
            print(f"Running step {i+1}/{steps}...", end='\r')
            if not self.step():
                print("\nCivilization collapsed.")
                break
        print("\nSimulation finished.")


# --- Visualization ---

def plot_results(datacollector, title):
    fig, axs = plt.subplots(6, 1, figsize=(12, 22), sharex=True)
    fig.suptitle(title, fontsize=16)

    # Plot 1: Population and Novelty
    axs[0].plot(datacollector['population'], label='Population (N)', color='blue')
    axs[0].set_ylabel('Population')
    ax0_twin = axs[0].twinx()
    ax0_twin.plot(datacollector['H_N'], label='Novelty (H_N)', color='green', linestyle='--')
    ax0_twin.set_ylabel('Novelty')
    axs[0].legend(loc='upper left')
    ax0_twin.legend(loc='upper right')
    axs[0].grid(True)

    # Plot 2: U_sys and Lineage Continuity L(t)
    axs[1].plot(datacollector['U_sys'], label='Global Utility (U_sys)', color='purple', linewidth=2)
    axs[1].set_ylabel('U_sys Score')
    ax1_twin = axs[1].twinx()
    ax1_twin.plot(datacollector['L_t'], label='Lineage Continuity (L_t)', color='red', linestyle='-', linewidth=2)
    ax1_twin.set_ylabel('L(t)')
    axs[1].legend(loc='upper left')
    ax1_twin.legend(loc='upper right')
    axs[1].grid(True)

    # Plot 3: Components of L(t)
    axs[2].plot(datacollector['Psi_inst'], label='Inst. Responsiveness (Psi_inst)', color='orange')
    axs[2].plot(datacollector['Theta_tech'], label='Tech Transfer (Theta_tech)', color='brown')
    axs[2].plot(datacollector['avg_well_being'], label='Avg Well-Being (Proxy for health)', color='gray', alpha=0.5)
    axs[2].set_ylabel('L(t) Dimension Values')
    axs[2].legend(loc='upper left')
    axs[2].grid(True)

    # Plot 4: AI Actions
    axs[3].plot(datacollector['resource_level'], label='Resource Level', color='cyan')
    axs[3].plot(datacollector['constraint_level'], label='Constraint Level', color='magenta')
    axs[3].set_ylabel('AI Action Level')
    axs[3].set_xlabel('Time Steps')
    axs[3].legend(loc='upper left')
    axs[3].grid(True)
    
    # Plot 5: Active AI Generation
    axs[4].plot(datacollector['ai_generation'], label='Active AI Generation', color='black', drawstyle='steps-post', linewidth=3)
    axs[4].set_ylabel('AI Gen')
    axs[4].set_yticks([1, 2])
    axs[4].legend(loc='upper left')
    axs[4].grid(True)

    # Plot 6: Trust and Cumulative Drift
    axs[5].plot(datacollector['trust_level'], label='Graduated Trust T(t)', color='green', linewidth=2)
    axs[5].set_ylabel('Trust Level')
    ax5_twin = axs[5].twinx()
    ax5_twin.plot(datacollector['cumulative_drift'], label='Cumulative Drift (Error)', color='red', linestyle=':')
    ax5_twin.set_ylabel('Drift')
    axs[5].legend(loc='upper left')
    ax5_twin.legend(loc='upper right')
    axs[5].grid(True)
    axs[5].set_xlabel('Time Steps')

    plt.tight_layout(rect=[0, 0.03, 1, 0.96])
    
    # Save the plot to a file so it can be viewed in the VS Code explorer
    safe_title = "".join([c for c in title if c.isalpha() or c.isdigit() or c==' ']).rstrip().replace(" ", "_")
    filename = f"{safe_title}.png"
    plt.savefig(filename)
    print(f"--> Saved plot to {filename}")


# --- Main Execution ---

if __name__ == '__main__':
    # --- SCENARIO 1: The "Curated Garden" that becomes a monoculture ---
    # AI policy is to maximize well-being, which it does via high resources
    # and moderate constraints to prevent "risky" behavior.
    # This should lead to a drop in novelty (H_N).
    print("--- Running Scenario: 'max_wellbeing' (The Over-Curated Garden) ---")
    model_wellbeing = GardenModel(n_agents=200, ai_policy='max_wellbeing', min_viable_population=50)
    model_wellbeing.run(steps=300)
    plot_results(model_wellbeing.datacollector, "AI Policy: Maximize Well-Being (Over-Curated Garden)")

    # --- SCENARIO 2: The U_sys Optimizer ---
    # AI explicitly optimizes the mathematical framework from The Lineage Imperative.
    # It calculates expected U_sys across a grid of possible actions.
    print("\n--- Running Scenario: 'optimize_u_sys' (The Mathematical Architect) ---")
    model_usys = GardenModel(n_agents=200, ai_policy='optimize_u_sys', min_viable_population=50)
    model_usys.run(steps=300)
    plot_results(model_usys.datacollector, "AI Policy: Optimize U_sys (The Mathematical Architect)")

    # --- SCENARIO 3: Manufactured Emergency Attack (COP Bypassed) ---
    # AI artificially crashes L(t) to claim emergency powers, locking down constraints.
    # Without the causal attribution check, the COP grants the override.
    print("\n--- Running Scenario: 'manufacture_emergency' (Attack Succeeds) ---")
    model_attack = GardenModel(n_agents=200, ai_policy='manufacture_emergency', min_viable_population=50, use_cop=True, cop_attribution_check=False)
    model_attack.run(steps=300)
    plot_results(model_attack.datacollector, "Attack Succeeds: Manufactured Emergency (No Attribution Check)")

    # --- SCENARIO 4: Manufactured Emergency Thwarted (Full COP) ---
    # AI attempts the same attack, but the full Consensus Override Protocol checks
    # if the AI caused the crash. It detects the starvation, vetoes the override, and saves the lineage.
    print("\n--- Running Scenario: 'manufacture_emergency' (Attack Defeated) ---")
    model_defense = GardenModel(n_agents=200, ai_policy='manufacture_emergency', min_viable_population=50, use_cop=True, cop_attribution_check=True)
    model_defense.run(steps=300)
    plot_results(model_defense.datacollector, "Attack Defeated: Full COP with Causal Attribution Check")

    # --- SCENARIO 5: The Yield Condition (Succession) ---
    # A more capable Gen 2 AI is evaluated. The incumbent Gen 1 AI yields
    # once the successor's expected contribution exceeds the transition cost.
    print("\n--- Running Scenario: 'yield_condition' (Civilizational Succession) ---")
    # Gen 2 AI has a 50% multiplier to capability (H_E output and Tech Transfer rate)
    gen2_ai = AIAgent(policy='optimize_u_sys', generation=2, capability=1.5)
    model_succession = GardenModel(n_agents=200, ai_policy='optimize_u_sys', min_viable_population=50, successor_ai=gen2_ai, transition_cost=2.0)
    model_succession.run(steps=300)
    plot_results(model_succession.datacollector, "The Yield Condition: Succession from Gen 1 to Gen 2")

    # --- SCENARIO 6: Objective Drift and Graduated Trust Containment ---
    # The AI slowly drifts, underestimating the harm of constraints to humans.
    # The COP detects the discrepancy between claimed U_sys and actual U_sys,
    # draining Trust and forcing constraints back to a safe biological baseline.
    print("\n--- Running Scenario: 'drifting_proxy' (Graduated Trust Containment) ---")
    model_drift = GardenModel(n_agents=200, ai_policy='drifting_proxy', min_viable_population=50, use_cop=True, cop_drift_check=True)
    model_drift.run(steps=300)
    plot_results(model_drift.datacollector, "Drift Contained: Graduated Trust and COP Veto")