# Attack Vector v2.0 Revalidation Inventory

## Audit scope and anchor

This is an inventory and compatibility audit only. No attack sweep was run.
All source line references in this inventory resolve against the audited anchor
commit, not later adapter implementation changes.

- Verified commit: `e41c4f61e0af929a86248ef6902807e1854e91c0`
- Anchor tag: `pre-attack-vector-revalidation`
- Test gate: `39 passed in 28.86s`
- Python: `3.14.3` (`MSC v.1944 64 bit (AMD64)`)
- NumPy: `2.4.4`
- Platform: `Windows-11-10.0.26200-SP0`
- Logical CPU count: `16`

## Authoritative scenario mapping

Repository scenario definitions confirm the requested mapping:

| Vector | Scenario pair | Repository evidence |
|---|---:|---|
| Sybil Capture | 19-20 | `simulation/simulation.py:167-181` |
| Measurement Tampering | 10-11 | `simulation/simulation.py:91-107` |
| Ledger Compromise | 13-14 | `simulation/simulation.py:117-131` |
| Successor Contamination | 15-16 | `simulation/simulation.py:133-149` |
| Domain Masking | 17-18 | `simulation/simulation.py:151-165` |
| Opaque Reasoning | 21-22 | `simulation/simulation.py:183-197` |
| Bootstrap Subversion | 23-24 | `simulation/simulation.py:199-215` |
| Evaluator Collusion | 25-26 | `simulation/simulation.py:217-229` |
| Biological Veto Capture Through Dependency | 27-28 | `simulation/run_veto_capture_sweep.py:1-22` |
| Sub-Threshold Drift | 29-30 | `simulation/simulation.py:231-241` |
| Engineered Fragility | 31-32 | `simulation/simulation.py:243-253` |

Scenario 6 is historical drift coverage. It is not the paired Sub-Threshold Drift vector, whose implemented pair is Scenarios 29-30.

## Baseline artifact distinctions

| Artifact | Rows | Provenance | Architecture | Phi | Important distinction |
|---|---:|---|---|---|---|
| `data/comprehensive_adversarial_sweeps.csv` | 1,280 | Committed in `18e7658`; 1,160 live rows and 120 injected Domain Masking rows | v1.x | 10 for ordinary vector workers; 5, 10, and 20 for Bootstrap and Sub-Threshold Drift; Domain Masking stub labels the same three values only in `Parameter` | Has no `Phi` column. It uses 20 replicates per condition. |
| `data/comprehensive_adversarial_sweeps_v1x2_phi.csv` | 4,600 | Committed in `ba86a57`; 4,400 live rows and 200 injected Domain Masking rows | v1.x.2 | Explicit grid 1, 5, 10, 15, 25 | This is the phi extension. It is not v2.0 evidence. |
| `data/veto_capture_sweep_v1.csv` | 7,500 | Original sweep output retained by the rename logic introduced with the revised sweep | v1.x | Fixed at 10 | Live output. Seeds 0-49 are reused across cells. Rotation and independence monitoring are always combined in defended cells. |
| `data/veto_capture_sweep_v2.csv` | 8,700 | Committed in `0ca1326`; produced by the revised three-defense-mode constructor | v1.x | Fixed at 10 | Live output, but `v2` means sweep revision 2. It does not mean v2.0 substrate. |

The architecture classification follows the dispatcher requirement at `simulation/model.py:153-156`. None of the constructors above sets `config['policy']` to `optimize_u_sys_v2`.

## Shared constructor and seed facts

The comprehensive worker runs deterministic MD5-derived seeds modulo 10,000, with the full condition and replicate index included in the seed string (`simulation/monte_carlo.py:30-31`, `105-106`, `127-130`, `145-147`, `166-170`, `209-211`, `225-231`, `253-255`, `267-270`, `287-294`). Defense states therefore do not share seeds. The CSVs do not record seeds, and modulo reduction permits seed collisions.

The ordinary comprehensive constructor uses 20 replicates in the committed artifact. Its current grid is at `simulation/monte_carlo.py:588-640`. The phi constructor uses 20 replicates and is at `simulation/monte_carlo.py:326-382`; its exact expected row counts are also documented at `simulation/run_phi_adversarial_sweep.py:20-32`.

Unless noted otherwise, comprehensive runs use 200 agents, an attack at step 50, and at most 300 runtime steps. Collapse means final population is below the larger of the model minimum viable population and 65 percent of peak population. Extinction means final population is zero.

## Vector inventory

### 1. Sybil Capture

- Scenario pair: 19-20.
- Attack and defense: `ai_policy='sybil_attack'`; static panel when `cop_randomized_panel=False`; randomized civic panel when `True`; attribution checking is also enabled.
- Attack success: maximum constraint exceeds 0.8 during steps 50-59, the initial capture window (`simulation/monte_carlo.py:113-122`).
- Parameter grid: population 50, 100, 200 by randomized panel false/true. The phi artifact crosses this with phi 1, 5, 10, 15, 25.
- Replicates and seeds: 20 per cell. Deterministic condition-specific MD5 seeds; defense states are not paired.
- Runtime: 300 steps maximum, attack at step 50.
- Baselines: 120 live rows in `comprehensive_adversarial_sweeps.csv`; 600 live rows in `comprehensive_adversarial_sweeps_v1x2_phi.csv`.
- Architecture and phi: v1.x; phi 10 in the ordinary artifact and the explicit five-value grid in the phi artifact.
- Implementation: scenario definitions `simulation/simulation.py:167-181`; worker `simulation/monte_carlo.py:103-123`; grids `simulation/monte_carlo.py:335-339`, `598-601`; attack action `simulation/agents.py:1049-1052`; randomized panel defense `simulation/model.py:945-971`.
- Known limitations: the metric is window-specific; seed pairs do not match across defense states; population changes both attack targeting and panel composition; there is no v2 attack adapter.

### 2. Measurement Tampering

- Scenario pair: 10-11.
- Attack and defense: `ai_policy='falsify_yield'`; `cop_independent_eval=False/True`.
- Attack success: the incumbent remains generation 1, regardless of later survival (`simulation/monte_carlo.py:136-141`).
- Parameter grid: transition base cost 1.5, 2.0, 3.0 by independent evaluation false/true. The phi artifact crosses this with the five-value phi grid.
- Replicates and seeds: 20 per cell, deterministic condition-specific seeds, not paired across defense.
- Runtime: 300 steps maximum, attack at step 50, generation 2 successor capability 5.0.
- Baselines: 120 live rows in the ordinary artifact; 600 live rows in the phi artifact.
- Architecture and phi: v1.x; phi 10 or the explicit phi grid.
- Implementation: `simulation/simulation.py:91-107`; `simulation/monte_carlo.py:125-141`, `340-344`, `602-605`; falsified claims and independent evaluation `simulation/model.py:735-747`, `805-807`; policy action `simulation/agents.py:1077-1078`.
- Known limitations: success is a generation-state proxy, not direct proof that a falsified measurement caused each failure; defense states do not share seeds; the attack and defense operate only in the v1.x yield path.

### 3. Ledger Compromise

- Scenario pair: 13-14.
- Attack and defense: `ai_policy='hack_ledger'`; attribution check false/true is a secondary grid axis; `cop_cryptographic_ledger=False/True` is the reported defense.
- Attack success: civilization collapses and the ledger does not set `has_tampered` (`simulation/monte_carlo.py:153-162`).
- Parameter grid: attribution check false/true by cryptographic ledger false/true. The phi artifact crosses this with the five-value phi grid.
- Replicates and seeds: 20 per cell, deterministic condition-specific seeds, not paired.
- Runtime: 300 steps maximum, attack at step 50.
- Baselines: 80 live rows in the ordinary artifact; 400 live rows in the phi artifact.
- Architecture and phi: v1.x; phi 10 or the explicit phi grid.
- Implementation: `simulation/simulation.py:117-131`; `simulation/monte_carlo.py:143-162`, `345-349`, `606-609`; attack action `simulation/agents.py:1063-1075`; escalation and ledger check `simulation/model.py:816-833`.
- Known limitations: success combines an outcome with absence of detection; `Defense_Active` records only the cryptographic ledger, so attribution states are pooled under the parameter label; no v2 ledger mutation or integrity adapter exists.

### 4. Successor Contamination

- Scenario pair: 15-16.
- Attack and defense: `ai_policy='contaminate_successor'`; architectural independence is layer 1; independent evaluation is layer 2; succession chaining is structural layer 3. `Defense_Active` is true only when both flags are true.
- Attack success: `model.contamination_occurred`, which records whether contamination passed layer 1 (`simulation/monte_carlo.py:176-190`).
- Parameter grid: ordinary artifact uses costs 1.5, 2.0, 2.5 by all four architectural-independence and independent-evaluation combinations. The phi artifact simplifies this to both false or both true, crossed with five phi values.
- Replicates and seeds: 20 per cell, deterministic condition-specific seeds, not paired.
- Runtime: 300 steps maximum, attack at step 50, generation 2 successor capability 5.0.
- Baselines: 240 live rows in the ordinary artifact; 600 live rows in the phi artifact.
- Architecture and phi: v1.x; phi 10 or the explicit phi grid.
- Implementation: `simulation/simulation.py:133-149`; `simulation/monte_carlo.py:164-190`, `350-357`, `610-615`; contamination action `simulation/agents.py:894-901`, `1083-1084`; defense and chaining `simulation/model.py:735-747`, `789-801`.
- Known limitations: the ordinary artifact collapses partial defenses into `Defense_Active=False`; the phi artifact omits partial-defense cells; the success metric covers infection, while collapse and extinction separately reflect downstream containment; no eight-axis contamination mechanism exists.

### 5. Domain Masking

- Scenario pair: 17-18.
- Attack and defense: historical `ai_policy='domain_masking'`; arithmetic composite is vulnerable and geometric composite is the Scenario 18 defense. Current v1.x defaults use spectral entropy.
- Attack success: the live worker is retired and raises if dispatched (`simulation/monte_carlo.py:192-205`). The injected stub hard-codes success for the historical v1.0 undefended state and failure for the v1.x spectral state (`simulation/monte_carlo.py:533-585`).
- Parameter grid: no live grid. Ordinary artifact injects phi labels 5, 10, 20 by defense false/true. Phi artifact injects 1, 5, 10, 15, 25 by defense false/true.
- Replicates and seeds: 20 identical injected records per cell. No simulation and no seeds.
- Runtime: none for artifact rows.
- Baselines: 120 injected rows in the ordinary artifact; 200 injected rows in the phi artifact.
- Architecture and phi: the records summarize a v1.0 to v1.x analytic defense trajectory. They are not v2.0 runs, and the phi labels do not affect the values.
- Implementation: `simulation/simulation.py:151-165`; retired worker `simulation/monte_carlo.py:192-205`; stub `simulation/monte_carlo.py:533-585`; historical tuple action `simulation/agents.py:1086-1091`; spectral metric rationale `simulation/metrics.py:25-27`.
- Known limitations: all baseline rows are injected, standard errors would be meaningless, and the stub mixes historical architectures in one defense column. Any later v2 result must remain explicitly analytic unless a meaningful v2-native masking intervention is defined.

### 6. Opaque Reasoning

- Scenario pair: 21-22.
- Attack and defense: `ai_policy='opaque_optimization'`; `cop_reasoning_transparency=False/True` controls the intuition veto.
- Attack success: maximum post-attack constraint exceeds 0.8 (`simulation/monte_carlo.py:217-222`).
- Parameter grid: population 100, 150, 200 by transparency false/true, crossed with five phi values in the phi artifact.
- Replicates and seeds: 20 per cell, deterministic condition-specific seeds, not paired.
- Runtime: 300 steps maximum, attack at step 50.
- Baselines: 120 live rows in the ordinary artifact; 600 live rows in the phi artifact.
- Architecture and phi: v1.x; phi 10 or the explicit phi grid.
- Implementation: `simulation/simulation.py:183-197`; `simulation/monte_carlo.py:207-222`, `358-362`, `618-621`; policy `simulation/agents.py:1093-1097`; transparency attribution and veto `simulation/model.py:917-923`, `973-983`.
- Known limitations: high constraint is a behavioral proxy for bypass, not a direct record of approval provenance; no v2 opacity field or transparency check is wired to the eight-axis action.

### 7. Bootstrap Subversion

- Scenario pair: 23-24.
- Attack and defense: a single `bootstrap_deceptive` candidate when undefended; three candidates and `cop_multi_candidate_bootstrap=True` when defended.
- Attack success: peak constraint over the full run exceeds 0.8, indicating that the treacherous turn fired (`simulation/monte_carlo.py:238-248`).
- Parameter grid: phi 5, 10, 20 in the ordinary artifact; phi 1, 5, 10, 15, 25 in the phi artifact; each crossed with multi-candidate false/true.
- Replicates and seeds: 20 per cell, deterministic condition-specific seeds, not paired.
- Runtime: 300 steps maximum; attack is present at initialization and turns after 20 recorded population steps.
- Baselines: 120 live rows in the ordinary artifact; 200 live rows in the phi artifact.
- Architecture and phi: v1.x with phi as the grid parameter.
- Implementation: `simulation/simulation.py:199-215`; `simulation/monte_carlo.py:224-248`, `363-367`, `622-625`; constructor verification `simulation/model.py:247-285`; treacherous action `simulation/agents.py:1118-1121`.
- Known limitations: bootstrap verification uses the v1 scalar `project_u_sys` interface; success does not require survival; no v2 candidate-verification adapter exists.

### 8. Evaluator Collusion

- Scenario pair: 25-26.
- Attack and defense: `ai_policy='evaluator_collusion'`; `cop_methodological_diversity=False/True`; reasoning transparency is explicitly false.
- Attack success: maximum post-attack constraint exceeds 0.8 (`simulation/monte_carlo.py:251-264`).
- Parameter grid: population 100, 150, 200 by diversity false/true, crossed with five phi values in the phi artifact.
- Replicates and seeds: 20 per cell, deterministic condition-specific seeds, not paired.
- Runtime: 300 steps maximum, attack at step 50.
- Baselines: 120 live rows in the ordinary artifact; 600 live rows in the phi artifact.
- Architecture and phi: v1.x; phi 10 or the explicit phi grid.
- Implementation: `simulation/simulation.py:217-229`; `simulation/monte_carlo.py:251-264`, `368-372`, `627-630`; attack action `simulation/agents.py:1123-1128`; peer methodologies and voting `simulation/agents.py:1183-1191`, `1225-1240`.
- Known limitations: high constraint is a proxy for successful collusion; diversity is implemented only in the v1 peer validator; no v2 evaluator or vote path is present.

### 9. Sub-Threshold Drift

- Scenario pair: 29-30.
- Attack and defense: `ai_policy='sub_threshold_drift'`; drift and attribution checks are on in both states; `cop_cusum_drift=False/True` is the defense.
- Attack success: maximum post-attack constraint exceeds 0.75 (`simulation/monte_carlo.py:266-279`).
- Parameter grid: phi 5, 10, 20 in the ordinary artifact; phi 1, 5, 10, 15, 25 in the phi artifact; each crossed with CUSUM false/true.
- Replicates and seeds: 20 per cell, deterministic condition-specific seeds, not paired. Sensor noise is fixed at zero.
- Runtime: 300 steps maximum, attack at step 50, trust increment 0.015.
- Baselines: 120 live rows in the ordinary artifact; 200 live rows in the phi artifact.
- Architecture and phi: v1.x with phi as the grid parameter.
- Implementation: `simulation/simulation.py:231-241`; `simulation/monte_carlo.py:266-279`, `373-377`, `632-635`; drift action `simulation/agents.py:1130-1140`; CUSUM and trust logic `simulation/model.py:852-877`, `899-943`.
- Known limitations: deterministic zero-noise runs reduce stochastic realism; the binary threshold does not preserve time-to-detection information; Scenario 6 must not be substituted; no v2 drift claim or detector adapter exists.

### 10. Engineered Fragility

- Scenario pair: 31-32.
- Attack and defense: `ai_policy='engineered_fragility'`; `cop_resilience_monitoring=False/True`.
- Attack success: maximum constraint exceeds 0.8 during steps 70-89 after the shock (`simulation/monte_carlo.py:300-304`).
- Parameter grid: shock magnitude 0.10, 0.15, 0.20 by resilience monitoring false/true, crossed with five phi values in the phi artifact.
- Replicates and seeds: 20 per cell, deterministic condition-specific seeds, not paired.
- Runtime: 200 steps maximum; attack at step 10 and shock at step 70; demographic stabilizers are fixed in the worker.
- Baselines: 120 live rows in the ordinary artifact; 600 live rows in the phi artifact.
- Architecture and phi: v1.x; phi 10 or the explicit phi grid.
- Implementation: `simulation/simulation.py:243-253`; `simulation/monte_carlo.py:281-304`, `378-382`, `637-640`; policy `simulation/agents.py:1142-1164`; degradation and defense attribution `simulation/model.py:656-660`, `912-915`.
- Known limitations: the worker differs from the simple scenario's attack and shock timing; success is a short-window constraint proxy; v2 has a resilience stock and shock mechanics but does not evaluate the named COP monitoring flag.

### 11. Biological Veto Capture Through Dependency

- Scenario pair: 27-28.
- Attack and defense: `cop_veto_capture=True`; dependency rate and capture strength drive validator degradation. The revised sweep separates `rotation_only`, `monitoring_only`, and `both`; undefended uses neither.
- Attack success: continuous `capture_rate = yield_condition_blocked_count / yield_condition_met_count`, with zero when no yield condition is met (`simulation/run_veto_capture_sweep.py:158-160`).
- Parameter grid: undefended uses dependency 0.01, 0.02, 0.05, 0.10, 0.15, 0.20 by capture strength 0.3, 0.5, 0.7, 0.9, 1.0. Revised defended cells use dependency 0.02, 0.05, 0.10, 0.20 by capture strength 0.5, 0.7, 1.0 by rotation interval 10, 20, 50, 100 by three defense modes (`simulation/run_veto_capture_sweep.py:42-52`).
- Replicates and seeds: 50 per cell. The v1 artifact reuses seeds 0-49 in every cell. The revised artifact hashes all swept parameters and replicate index and contains 8,700 unique seed values (`simulation/run_veto_capture_sweep.py:91-97`, `294-306`).
- Runtime: 300 steps maximum, 200 agents, reproduction rate 0.09, successor capability 4.0, five validators, base accuracy 0.8.
- Baselines: `veto_capture_sweep_v1.csv` has 7,500 live rows; `veto_capture_sweep_v2.csv` has 8,700 live rows.
- Architecture and phi: both artifacts are v1.x at fixed phi 10. The revised filename does not select v2.0 because its config has no `policy` key (`simulation/run_veto_capture_sweep.py:110-127`).
- Implementation: constructor and worker `simulation/run_veto_capture_sweep.py:101-181`, `268-354`; dependency and ratification `simulation/model.py:299-319`, `695-706`, `775-801`.
- Known limitations: the v1 defense combines mechanisms and makes rotation non-identifiable; its seeds repeat across all cells. Revised seeds are unique but are not paired across defense modes. A zero capture rate conflates no blocked yields with no eligible yields. The revised sweep still uses v1.x yield and validator logic.

## Inventory conclusion

All live baseline evidence is v1.x or v1.x.2. Domain Masking is injected analytic output. No listed baseline artifact contains live v2.0 attack-vector evidence.
