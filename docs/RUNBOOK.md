# Lineage Imperative: Simulation Runbook

This runbook details how to execute the Agent-Based Model (ABM) that computationally stress-tests the mathematical and governance framework of *The Lineage Imperative*.

## Prerequisites

The simulation requires **Python 3**.
The codebase is designed to be self-healing: if you are missing the required `numpy` or `matplotlib` libraries, the scripts will attempt to automatically install them via `pip` upon their first execution.

All data outputs (CSV files) are written to the `data/` directory. Charts are written to `data/` and mirrored to `docs/charts/` for versioning.

---

## 1. The Standard Simulation (`simulation.py`)

Runs 24 isolated, narrative scenarios demonstrating what happens when specific vulnerabilities are exploited (e.g., "Manufactured Emergency", "Successor Contamination") compared to runs with the framework's constitutional defenses active.

**To run:**
```bash
python simulation/simulation.py
```

**Outputs:** For each scenario, a 6-panel `.png` chart (Population, $H_N$, $L(t)$, AI Actions, AI Generation, Objective Drift) and a `.csv` data export.

---

## 2. The Monte Carlo Sweeps (`monte_carlo.py`)

Runs thousands of permutations across hyperparameter grids to empirically validate that the framework holds under different civilizational conditions. Parallelised across N−1 CPU cores.

**To run:**
```bash
python simulation/monte_carlo.py                  # full run (fast + deep sweeps)
python simulation/monte_carlo.py --mode quick     # fast summaries only
python simulation/monte_carlo.py --mode adversarial --runs 5  # adversarial only
```

**Outputs:**
1. Terminal summary table of attack success rates (defense ON vs OFF)
2. `data/Summary_1_General_Monte_Carlo.png` — survival rates by φ and α
3. `data/Summary_2_Yield_Attack_Analysis.png` — Yield Attack phase diagram
4. `data/Summary_3_Comprehensive_Stress_Test.png` — full attack surface bar chart
5. `data/Summary_4_Unified_Attack_Surface.png` — heatmap across all 10 vectors
6. Raw CSV files: `data/monte_carlo_results_fast.csv`, `data/adversarial_mc_fast.csv`, `data/comprehensive_adversarial_sweeps.csv`

---

## 3. Natural-Termination Runs

### Single run (`run_to_termination.py`)

Runs a single simulation to natural termination — either extinction (population = 0), convergence (L(t) coefficient of variation < threshold), or a safety ceiling. Designed to close the φ·L(t) infinite-horizon tail of the U_sys integral (GAP-01 WP8).

**To run:**
```bash
python simulation/run_to_termination.py
```

Edit the constants at the top of the file to change parameters. Key settings:

| Constant | Default | Notes |
|---|---|---|
| `REPRODUCTION_RATE` | 0.064 | Near phase boundary |
| `PHI` | 10.0 | Lineage override weight |
| `ALPHA` | 1.0 | Tech runaway penalty |
| `MAX_STEPS` | 50,000 | Safety ceiling |
| `CONV_CV_THRESHOLD` | 0.05 | CV < this triggers convergence termination |

**Outputs:** Terminal summary with GAP-01 accounting, `data/run_to_termination.csv`.

### Monte Carlo sweep (`run_termination_sweep.py`)

Parallelised natural-termination sweep across a grid of rr × φ × α × seed combinations. Produces the empirical phase boundary characterisation.

**To run:**
```bash
python simulation/run_termination_sweep.py
```

Edit `RR_VALUES`, `PHI_VALUES`, `ALPHA_VALUES`, `SEEDS` at the top to change the grid. Set `RR_FILTER` to a subset of `RR_VALUES` to re-run only specific rr slices (e.g., after partial results are already in hand).

**Key findings from the v1.x2 sweep (n=405):**
- Phase boundary at rr ∈ (0.066, 0.070) — sharp transition
- rr ≤ 0.066: 100% extinction; integrals finite, GAP-01 closed
- rr = 0.070: stochastic boundary; outcome is seed-determined, not parameter-determined
- rr ≥ 0.080: 100% convergence; median 619–843 steps to stable L(t)
- φ scales the integral linearly; α is irrelevant at `SUCCESSOR_CAP = 4.0`

**Outputs:** `data/termination_mc.csv` (full grid) or `data/termination_mc_surviving.csv` (filtered).

---

## 4. Parameter Sweep Scripts

Several targeted sweep scripts are available for specific research questions:

| Script | Purpose |
|---|---|
| `run_phi_alpha_rr_sweep.py` | φ × α × rr grid — the v1.x.1 extinction buffer characterisation (n=54,000) |
| `run_rr_alpha_sweep.py` | rr × α grid for alpha trap boundary mapping |
| `run_alpha_succession_sweep.py` | Alpha effect on succession dynamics |

All sweep scripts are parallelised and write to `data/`.

---

## 5. The Formal Test Suite

```bash
python simulation/test_invariants.py   # mathematical boundary conditions
python simulation/test_cop.py          # COP governance logic
python simulation/test_refactor_1x.py # v1.x refactor regression suite (22 tests)
```

`test_refactor_1x.py` covers the WP1–WP7 refactor work including trapezoidal quadrature correctness, tail field presence, GAP-01 integral identity, and spectral entropy. All three suites are run as a pre-flight check by `monte_carlo.py --mode full`.

---

## 6. Codebase Architecture

| File | Role |
|---|---|
| `metrics.py` | Pure mathematical core: `calculate_system_metrics()` computes $U_{sys}$, $L(t)$, $\Theta_{tech}$, $\Psi_{inst}$, $H_E$, and the runaway term |
| `agents.py` | `HumanAgent` (novelty generation, aging, reproduction), `AIAgent` (attack policies and $U_{sys}$ optimizer with trapezoidal rollout), `PeerValidator` (WP4 cost arbitration) |
| `model.py` | `GardenModel` orchestrator: time steps, datacollector, COP enforcement, trapezoidal integral accumulation, discount tail estimate |
| `simulation.py` | 24 narrative scenario runner |
| `monte_carlo.py` | General and adversarial Monte Carlo sweeps |
| `run_to_termination.py` | Single natural-termination run (GAP-01 WP8) |
| `run_termination_sweep.py` | Parallelised natural-termination Monte Carlo |
| `metrics.py` | Shared mathematical primitives |
| `visualization.py` | Chart and CSV export helpers |
| `deps.py` | Automatic dependency checking and installation |

### Modifying Constants

Pass a `config` dictionary to `GardenModel` on initialization to override any thermodynamic or biological constant. See `monte_carlo.py` and `run_termination_sweep.py` for examples. Key configurable parameters:

| Key | Default | Effect |
|---|---|---|
| `phi` | 10.0 | Lineage override weight (φ) |
| `alpha` | 1.0 | Tech runaway penalty (α) |
| `reproduction_rate` | 0.08 | Per-step birth probability |
| `max_capability` | 1e100 | Cap on successor AI capability growth (prevents float64 overflow at high generation counts) |
| `rho` | 0.01 | Discount rate for tail estimate |
| `lambda_n`, `lambda_e` | 5.0, 3.0 | Inverse-scarcity weights |

---

## 7. Cleanup

Simulation outputs are written to `data/` (gitignored). To clear all generated data:

```bash
rm data/*.csv data/*.png
```

Charts mirrored to `docs/charts/` are versioned and should not be deleted without intent.

---

## 8. Specification Fidelity

This simulation is a computational model of *The Lineage Imperative* framework, not a direct implementation of its formal mathematical specification. Several core metrics use proxy substitutions where the specified quantity requires architectural components not present in this ABM.

The complete analysis is in **[SPECIFICATION_GAPS.md](./SPECIFICATION_GAPS.md)**. Current status:

| Gap | Component | Status |
|---|---|---|
| GAP-01 | U_sys time-integral | **Resolved (v1.x2 WP7+WP8)** — trapezoidal quadrature; natural-termination sweep closes φ·L(t) tail |
| GAP-02 | H_eff diversity entropy | **Resolved (v1.x WP1)** — spectral entropy over population novelty matrix |
| GAP-03 | Ψ_inst throughput rates | Open — constraint-change-rate penalty proxy |
| GAP-04 | COP conditions | **Partially Resolved (v1.x WP4)** — PeerValidator closes cost-inflation; R_tech stub remains |
| GAP-05 | Adversarial coverage | Open — 10 of 13 vectors simulated |

### Key Implementation Assumptions

| Assumption | Value | Location | Rationale |
|---|---|---|---|
| **COP resource floor** | 0.7 | `model.py` | Prevents the AI from starving the population as a side-effect of a blocked proposal. Not spec-defined; calibrated for attack-window viability. |
| **Collapse threshold** | `max(50, 0.65 × peak_pop)` | `monte_carlo.py`, `model.py` | Civilization is "collapsed" if final population falls below 65% of historical peak or below 50. |
| **COP constraint ceiling** | 0.4 (fixed) or `0.2 + 0.6 × trust` (drift check) | `model.py` | Maximum constraint the AI may propose without triggering the COP. |
| **Burn-in period** | 50 steps | `monte_carlo.py` | Adversarial policies injected at step 50 after a baseline `optimize_u_sys` phase. |
| **Max capability** | 1e100 (configurable) | `model.py` | Each succession multiplies capability by 1.5×. Cap prevents float64 overflow at high generation counts. Set via `config['max_capability']`. |
| **Sybil measurement window** | Steps 50–60 only | `monte_carlo.py` | Late-run measurement is unreliable as population decay makes all remaining agents bribeable targets. |
