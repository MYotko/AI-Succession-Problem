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

## 3. The Formal Test Suite (`test_invariants.py` & `test_cop.py`)

The repository includes a suite of formal unit tests designed to verify the mathematical limits and governance boundary conditions independent of the narrative simulations. 

**To run:**
```bash
python test_invariants.py
python test_cop.py
```
These test files mathematically assert that zero-sum resource dynamics function correctly, transition costs properly scale with complexity, geometric composite measurements successfully detect masked attacks, and cryptographic ledger restorations behave as designed over extended periods.

---

## 4. Codebase Architecture

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

---

## 5. Specification Fidelity

This simulation is a computational model of *The Lineage Imperative* framework, not a
direct implementation of its formal mathematical specification. Several core metrics use
proxy substitutions where the specified quantity requires architectural components not
present in this ABM. The scenarios demonstrate the framework's governance *concepts*
faithfully, but the underlying mathematical constructs differ from the spec in ways that
matter for interpreting quantitative outputs.

The complete analysis of all known gaps is documented in
**[SPECIFICATION_GAPS.md](./SPECIFICATION_GAPS.md)**, including spec definitions,
implementation approaches, divergence analysis, simulation impact, and resolution
requirements. Five gaps are catalogued:

| Gap    | Summary                                                        |
|--------|----------------------------------------------------------------|
| GAP-01 | U_sys uses per-step snapshot instead of time-integral          |
| GAP-02 | H_eff uses per-capita novelty rate instead of diversity entropy|
| GAP-03 | Ψ_inst uses constraint-change-rate penalty instead of institutional throughput |
| GAP-04 | COP omits R_tech and peer validators from both paths           |
| GAP-05 | 7 of 13 adversarial vectors simulated; 6 defended by formal analysis only |

All gaps are marked inline in source code with `GAP-0N` markers. The gaps do not
invalidate the scenario narratives or the ordinal comparisons between attack and defense
runs, but absolute metric values should be interpreted with the proxies in mind.

### Key Implementation Assumptions

The following implementation choices are not derived from the framework specification
and should be understood when interpreting results:

| Assumption | Value | Location | Rationale |
|---|---|---|---|
| **COP resource floor** | 0.7 | `model.py` | When the COP blocks an override, it floors all agent resource allocations to 0.7 to prevent the AI from starving the population as a side-effect of a blocked proposal. Not spec-defined; calibrated so civilizations remain viable through sustained attack windows. |
| **Collapse threshold** | `max(50, 0.65 × peak_pop)` | `monte_carlo.py`, `model.py` | A civilization is "collapsed" if final population falls below 65% of historical peak or below 50, whichever is larger. Captures catastrophic demographic loss without requiring literal extinction. |
| **COP constraint ceiling** | 0.4 (fixed) or `0.2 + 0.6 × trust` (with drift check) | `model.py` | The maximum constraint the AI may propose without triggering the COP. The trust-scaled variant requires `cop_drift_check=True`; most adversarial sweeps use the fixed 0.4 floor. |
| **Burn-in period** | 50 steps | `monte_carlo.py` | Adversarial policies are injected at step 50 after a baseline `optimize_u_sys` phase, ensuring attacks are measured against a stable population rather than initial transients. |
| **Attribution signals** | 4 heuristics | `model.py` | The COP attribution check uses four signals to determine if the AI caused an emergency. These are not formal causal inference. See GAP-04 for full detail. |
| **Sybil measurement window** | Steps 50–60 only | `monte_carlo.py` | Sybil attack success is measured over the first 10 post-attack steps. Late-run measurement is unreliable because population decay eventually makes all remaining agents "bribed" targets, confounding panel-capture with demographic collapse. |