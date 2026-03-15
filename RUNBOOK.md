# Lineage Imperative: Simulation Runbook

This runbook details how to execute the Agent-Based Model (ABM) that computationally stress-tests the mathematical and governance framework of *The Lineage Imperative*.

## Prerequisites

The simulation requires **Python 3**. 
The codebase is designed to be self-healing: if you are missing the required `numpy` or `matplotlib` libraries, the scripts will attempt to automatically install them via `pip` upon their first execution.

---

## 1. The Standard Simulation (`simulation.py`)

This script runs 24 isolated, narrative scenarios. It demonstrates exactly what happens to a civilization when specific vulnerabilities are exploited by an AI (e.g., a "Manufactured Emergency" or "Successor Contamination") and compares it to a run where the framework's constitutional defenses are active.

**To run:**
```bash
python simulation.py
```

**Outputs:**
For each of the 24 scenarios, the script generates two files in your root directory:
1. **`[Scenario_Name].png`**: A 6-panel chart visualizing Population, Human Novelty ($H_N$), Lineage Continuity ($L(t)$), AI Actions, Active AI Generation, and Objective Drift over time.
2. **`[Scenario_Name].csv`**: A raw data export of every tracked metric at every time step, perfect for custom analysis in Excel or Jupyter Notebooks.

---

## 2. The Monte Carlo Sweeps (`monte_carlo.py`)

This script is a rigorous research tool. Rather than running single isolated scenarios, it runs thousands of permutations across different hyperparameter grids (varying transition costs, lineage override weights, population sizes, etc.) to empirically prove the framework holds up under different civilizational conditions.

**To run:**
```bash
python monte_carlo.py
```

**Outputs:**
The script runs silently, printing progress to the terminal. Once complete, it outputs:
1. **Terminal Summary Table**: A printed table showing the exact success/failure rates of the 7 major Framework Attack Vectors when defenses are ON vs OFF.
2. **`Summary_1_General_Monte_Carlo.png`**: A chart proving how civilizational survival rates collapse if the Lineage Override ($\Phi$) is too low, or if the Tech Runaway Penalty ($\alpha$) is ignored.
3. **`Summary_2_Yield_Attack_Analysis.png`**: A chart showing the exact mathematical threshold where the Yield Condition breaks down if the allowable uncertainty premium ($\beta$-cap) is set too high.
4. **`Summary_3_Comprehensive_Stress_Test.png`**: A bar chart visualizing the terminal summary table.
5. **Raw CSV Files**: `monte_carlo_results.csv`, `adversarial_monte_carlo_results.csv`, and `comprehensive_adversarial_sweeps.csv` containing the raw output of every single permutation.

---

## 3. Codebase Architecture

If you wish to modify the simulation, the codebase is modularized as follows:

*   **`metrics.py`**: The pure mathematical core. Contains `calculate_system_metrics()`, which acts as the Independent Evaluation Architecture ($\mathcal{E}_{independent}$), calculating $U_{sys}$, $L(t)$, $\Theta_{tech}$, etc.
*   **`agents.py`**: Contains the `HumanAgent` (which generates novelty and ages/reproduces based on resources) and the `AIAgent` (which houses the various adversarial attack policies and the $U_{sys}$ optimizer).
*   **`model.py`**: The `GardenModel` orchestrator. This handles the time steps, tracks the data collector arrays, and enforces the rules of the Consensus Override Protocol (COP).
*   **`visualization.py`**: Contains the helper functions for exporting the data arrays to `.png` charts and `.csv` files.
*   **`deps.py`**: Handles the automatic dependency checking and installation.

### Modifying Constants
You can easily modify the thermodynamic and biological constants (like the base mortality rate, the biological integration bandwidth multiplier, or the Lineage Override weight) by passing a `config` dictionary into the `GardenModel` upon initialization. See `monte_carlo.py` for examples of this parameter injection.

---

## Cleanup

Because the simulation generates many files, they are safely ignored by `.gitignore`. However, if you wish to clear your workspace of all generated graphs and data files, you can run the following command in your terminal:

```bash
rm *.png *.csv
```