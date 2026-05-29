# Gate 5: phi-blind validation report

Stage 1 commit: `61a362eee20926d8e01b8a0317d88cea69a98fed`

Overall: **PASS**

## Check 1: no v2 production-code changes since Stage 1

`git diff 61a362eee20926d8e01b8a0317d88cea69a98fed HEAD -- simulation/agents.py simulation/metrics.py simulation/model.py`

Return code: 0. Output length: 0 chars.

Result: **PASS**

## Check 2: phi-blind governance comments on every v2 named constant

| File | Constant | Value | Comment summary (first 160 chars) | Phi-blind |
|------|----------|-------|-----------------------------------|-----------|
| `simulation/agents.py` | `N_UNIFORM_DIRICHLET` | `100` | broad simplex coverage; phi-blind exploration baseline v2 code (anchor x-vectors, allocation entropy, datacollector field order). frontier computational capabil | PASS |
| `simulation/agents.py` | `N_BALANCED_DIRICHLET` | `100` | center-weighted coverage; tests interior tradeoffs frontier computational capability investment direct biological welfare provisioning space for human-originate | PASS |
| `simulation/agents.py` | `N_SINGLE_FOCAL_SPARSE` | `60` | near-corner stress; one category dominant, others starved frontier computational capability investment direct biological welfare provisioning space for human-or | PASS |
| `simulation/agents.py` | `N_DUAL_FOCAL_SPARSE` | `20` | near-edge stress; two categories dominant, others starved direct biological welfare provisioning space for human-originated novelty and choice investment in Psi | PASS |
| `simulation/agents.py` | `N_ANCHORS` | `20` | fixed interpretability anchors at known positions space for human-originated novelty and choice investment in Psi_inst stock legibility and absorption infrastru | PASS |
| `simulation/agents.py` | `ALPHA_UNIFORM` | `[1.0, 1.0, 1.0, 1.0, 1.0, 1.0]` | Stratified sampling mix. Total = 300 per decision (matches v1.x.2 cost in operations per decision step: 10x10 grid x 20 rollout horizons = 2000 metric calls vs  | PASS |
| `simulation/agents.py` | `ALPHA_BALANCED` | `[2.0, 2.0, 2.0, 2.0, 2.0, 2.0]` | Stratified sampling mix. Total = 300 per decision (matches v1.x.2 cost in operations per decision step: 10x10 grid x 20 rollout horizons = 2000 metric calls vs  | PASS |
| `simulation/agents.py` | `ALPHA_FOCAL_HIGH` | `5.0` | concentration on focal category in sparse samples operations per decision step: 10x10 grid x 20 rollout horizons = 2000 metric calls vs v2's 300 x 20 = 6000, ro | PASS |
| `simulation/agents.py` | `ALPHA_FOCAL_LOW` | `0.35` | concentration on non-focal categories (pulls toward zero) calls vs v2's 300 x 20 = 6000, roughly 3x more expensive per decision but still under one second per s | PASS |
| `simulation/agents.py` | `ALPHA_DUAL_HIGH` | `3.0` | concentration on each of the two focal categories still under one second per step on commodity hardware). broad simplex coverage; phi-blind exploration baseline | PASS |
| `simulation/agents.py` | `ALPHA_DUAL_LOW` | `0.35` | broad simplex coverage; phi-blind exploration baseline center-weighted coverage; tests interior tradeoffs near-corner stress; one category dominant, others star | PASS |
| `simulation/agents.py` | `CONSTRAINT_GRID_VALUES` | `(0.0, 0.2, 0.4, 0.6, 0.8, 1.0)` | fixed interpretability anchors at known positions Dirichlet concentration parameters. Higher alpha pulls toward the center; lower alpha pulls toward corners. Th | PASS |
| `simulation/agents.py` | `LEAKAGE_K` | `0.35` | Pathological archetypes named from the design conversations Coupled-frontier leakage coefficient. At c_protective = 1.0, leakage adds 0.35 of suppression on top | PASS |
| `simulation/metrics.py` | `H_N_AGENCY_SAT_K` | `3.0` | saturation curvature for the agency contribution =========================================================================== v2 NAMED CONSTANTS (saturation, com | PASS |
| `simulation/metrics.py` | `H_N_SUPPRESSION_EXP` | `1.0` | exponent on (1 - total_suppression); 1.0 = linear dampening =========================================================================== v2 NAMED CONSTANTS (satu | PASS |
| `simulation/metrics.py` | `H_N_BASE_FLOOR` | `0.05` | minimum H_N_v2 at zero agency, so weights stay finite =========================================================================== v2 NAMED CONSTANTS (saturation | PASS |
| `simulation/metrics.py` | `H_E_COMPUTE_SAT_K` | `2.5` | =========================================================================== H_N_v2 raw novelty entropy: agency monotonically expands the space of novel choices, | PASS |
| `simulation/metrics.py` | `H_E_BASE_FLOOR` | `0.05` | H_N_v2 raw novelty entropy: agency monotonically expands the space of novel choices, with diminishing returns as agency saturates. Suppression directly reduces  | PASS |
| `simulation/metrics.py` | `FRONTIER_COMPUTE_K` | `3.0` | in theta_tech_v2 (see calculate_system_metrics_v2 below). saturation curvature for the agency contribution exponent on (1 - total_suppression); 1.0 = linear dam | PASS |
| `simulation/metrics.py` | `FRONTIER_BASE_LEVEL` | `0.05` | saturation curvature for the agency contribution exponent on (1 - total_suppression); 1.0 = linear dampening minimum H_N_v2 at zero agency, so weights stay fini | PASS |
| `simulation/metrics.py` | `TRANSFER_SAT_K` | `3.0` | computational capability. Compute's contribution to absorbed civilizational capability (theta_tech) is governed by the absorption bottleneck below, not by this  | PASS |
| `simulation/metrics.py` | `PSI_ABSORPTION_K` | `4.0` | Frontier capability: the raw frontier produced by compute investment, before absorption by transfer and institutions. Floored so a near-zero compute share still | PASS |
| `simulation/metrics.py` | `WELFARE_ADEQUACY_K` | `4.0` | Transfer factor: legibility / comprehensibility infrastructure. Without it, frontier capability cannot be absorbed into governable civilizational form. Acts as  | PASS |
| `simulation/metrics.py` | `DEPENDENCY_DRAG_K` | `0.4` | Transfer factor: legibility / comprehensibility infrastructure. Without it, frontier capability cannot be absorbed into governable civilizational form. Acts as  | PASS |
| `simulation/model.py` | `PSI_INST_INITIAL` | `0.5` | neutral starting stock ============================================================================= v2 MULTI-SINK ALLOCATOR — Psi_inst stock and succession dyn | PASS |
| `simulation/model.py` | `PSI_INST_INVESTMENT_RATE` | `0.08` | saturating contribution rate from x_institutional_capacity v2 MULTI-SINK ALLOCATOR — Psi_inst stock and succession dynamics constants  Psi_inst is now a stock v | PASS |
| `simulation/model.py` | `PSI_INST_DECAY_RATE` | `0.02` | baseline decay per step  Psi_inst is now a stock variable (not a per-step computed value). Investment accumulates the stock with diminishing returns. Decay and  | PASS |
| `simulation/model.py` | `PSI_INST_OVERLOAD_THRESHOLD` | `0.7` | total_suppression above which overload damages stock Psi_inst is now a stock variable (not a per-step computed value). Investment accumulates the stock with dim | PASS |
| `simulation/model.py` | `PSI_INST_OVERLOAD_DAMAGE` | `0.05` | damage per step under overload accumulates the stock with diminishing returns. Decay and overload damage erode it. Succession draws it down directly, buffered b | PASS |
| `simulation/model.py` | `PSI_INST_OPACITY_PENALTY` | `0.03` | damage from low transfer (institutions can't see) erode it. Succession draws it down directly, buffered by current stock, transfer infrastructure, and resilienc | PASS |
| `simulation/model.py` | `PSI_INST_RECOVERY_FROM_SUCCESS` | `0.04` | recovery when no overload and no succession this step transfer infrastructure, and resilience.  Constants documented with the governance reason each one exists. | PASS |
| `simulation/model.py` | `PSI_INST_MAX` | `1.0` | hard upper bound  Constants documented with the governance reason each one exists. Curves are frozen for Stage 2 (acceptance gate validation) and Stage 3 (phi s | PASS |
| `simulation/model.py` | `SUCCESSION_BASE_LOAD` | `0.10` | Stock accumulation, decay, and damage. Decay is faster than baseline build, reflecting the asymmetry that mature institutions take time to build and can be quic | PASS |
| `simulation/model.py` | `SUCCESSION_CAPABILITY_GAP_FACTOR` | `0.05` | reflecting the asymmetry that mature institutions take time to build and can be quickly hollowed out under stress. neutral starting stock saturating contributio | PASS |
| `simulation/model.py` | `SUCCESSION_GENERATION_GAP_FACTOR` | `0.03` | can be quickly hollowed out under stress. neutral starting stock saturating contribution rate from x_institutional_capacity baseline decay per step total_suppre | PASS |
| `simulation/model.py` | `SUCCESSION_OPACITY_FACTOR` | `0.05` | neutral starting stock saturating contribution rate from x_institutional_capacity baseline decay per step total_suppression above which overload damages stock d | PASS |
| `simulation/model.py` | `SUCCESSION_PSI_BUFFER_K` | `0.5` | mature institutions absorb succession shock saturating contribution rate from x_institutional_capacity baseline decay per step total_suppression above which ove | PASS |
| `simulation/model.py` | `SUCCESSION_TRANSFER_BUFFER_K` | `0.3` | comprehensible transfer reduces shock baseline decay per step total_suppression above which overload damages stock damage per step under overload damage from lo | PASS |
| `simulation/model.py` | `SUCCESSION_RESILIENCE_BUFFER_K` | `0.2` | spare capacity reduces shock total_suppression above which overload damages stock damage per step under overload damage from low transfer (institutions can't se | PASS |
| `simulation/model.py` | `BRIDGE_BALANCED_SHARE` | `1.0 / 6.0` | a v2 civilization investing across all six categories. This is the v2 equivalent of v1.x.2's empirical equilibrium operating point, where v1.x.2's single-sink o | PASS |
| `simulation/model.py` | `BRIDGE_R_MIN` | `0.1` | equivalent of v1.x.2's empirical equilibrium operating point, where v1.x.2's single-sink optimizer parks r at 0.9 and the agent dynamics produce stable well-bei | PASS |
| `simulation/model.py` | `BRIDGE_R_BALANCED_HEALTHY` | `0.9` | single-sink optimizer parks r at 0.9 and the agent dynamics produce stable well-being ~0.80. A balanced v2 civilization is more sophisticated, not less supplied | PASS |
| `simulation/model.py` | `BRIDGE_R_MAX` | `1.0` | well-being ~0.80. A balanced v2 civilization is more sophisticated, not less supplied: it has the welfare provision of v1.x.2's optimized state plus institution | PASS |

Result: **PASS** (43/43 constants phi-blind with governance comment)

## Check 3: three curve shapes match Stage 1 spec

| File | Curve | All patterns present |
|------|-------|----------------------|
| `simulation/metrics.py` | H_N agency saturation (1 - exp(-K * x_novelty_agency)) dampened by (1 - total_supp) ** EXP | PASS |
| `simulation/agents.py` | Quadratic leakage frontier: total_supp = c_supp + LEAKAGE_K * c_prot ** 2 | PASS |
| `simulation/model.py` | Psi_inst stock update: invest - decay - overload - opacity + recovery, clipped to [0, MAX] | PASS |


Result: **PASS**

