import matplotlib.pyplot as plt
import csv

# --- Output Helpers ---

def export_to_csv(datacollector, filename):
    keys = list(datacollector.keys())
    if not keys:
        return
    length = len(datacollector[keys[0]])
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Step'] + keys)
        for i in range(length):
            row = [i] + [datacollector[k][i] for k in keys]
            writer.writerow(row)

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
    
    # Save the raw data to a CSV file
    csv_filename = f"{safe_title}.csv"
    export_to_csv(datacollector, csv_filename)
    print(f"--> Saved data to {csv_filename}")