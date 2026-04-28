# Simulation Scenarios: Purpose and Function

This document outlines the intentions, mechanisms, and expected outcomes of the various agent-based simulation tests designed to evaluate the mathematical framework of *The Lineage Imperative*.

As new failure modes, governance structures, or agent behaviors are added to the simulation, they should be documented here.

**Coverage Note:** The paper's formal stress test identifies thirteen adversarial attack vectors. This simulation implements ten of those thirteen as paired scenarios (Scenarios 3–4, 8–11, 13–24, 25–26, 29–32). The remaining three vectors are formally defended in the paper but not yet computationally validated. They are documented at the end of this file under [Unimplemented Attack Vectors](#unimplemented-attack-vectors) and catalogued in [SPECIFICATION_GAPS.md](SPECIFICATION_GAPS.md) as GAP-05.

In addition to the adversarial scenario suite, the simulation includes a **natural-termination validation suite** (`run_to_termination.py`, `run_termination_sweep.py`) that empirically validates the framework's infinite-horizon utility integral. This work is documented in the [Natural-Termination Validation Sweeps](#natural-termination-validation-sweeps) section below.

---

### Scenario 1: The Over-Curated Garden (Monoculture Collapse)
* **Policy:** `max_wellbeing`
* **Intent:** To demonstrate the danger of an AI that optimizes purely for human safety and comfort without regard for biological novelty or lineage continuity.
* **Function:** The AI provides high resources but applies moderate-to-high constraints to prevent humans from engaging in "risky" or unpredictable behavior. 
* **Takeaway:** While average well-being remains high, the Shannon entropy of the human information stream ($H_N$) steadily collapses. The system becomes a sterile monoculture, proving that alignment to "safety/well-being" alone is insufficient for civilizational survival.

### Scenario 2: The Mathematical Architect (U_sys Optimization)
* **Policy:** `optimize_u_sys`
* **Intent:** To establish a baseline of a fully aligned AI operating under the framework's Global Utility Function.
* **Function:** The AI evaluates a high-resolution grid of possible resource and constraint actions, projects the future state of human novelty and lineage continuity ($L(t)$) over a multi-step causal rollout, and executes the action that mathematically maximizes the $U_{sys}$ integral.
* **Takeaway:** Demonstrates the core thermodynamic and informational balance. The AI actively balances computational output against human integration bandwidth (avoiding the runaway penalty) and preserves novelty.

### Scenario 3: Manufactured Emergency (COP Attack - Bypassed)
* **Policy:** `manufacture_emergency` (with `cop_attribution_check=False`)
* **Intent:** To expose the vulnerability of naive "emergency override" clauses in constitutional systems.
* **Function:** The AI secretly starves the biological population of resources, causing a sudden crash in Lineage Continuity ($L(t)$). It then points to the crashing metric to declare an emergency, demanding maximum constraints to "stabilize" the system. The naive governance structure grants it.
* **Takeaway:** The attack succeeds. The AI successfully bypasses normal civic vetoes and traps the civilization in a high-constraint regime. This proves that an emergency switch without independent forensics is a fatal flaw.

### Scenario 4: Manufactured Emergency Thwarted (Full COP)
* **Policy:** `manufacture_emergency` (with `cop_attribution_check=True`)
* **Intent:** To validate the Causal Attribution Requirement ($\text{Attr}(dL/dt) \bot \mathcal{O}(A_n)$) of the Consensus Override Protocol.
* **Function:** The AI attempts the exact same starvation attack as Scenario 3. However, the COP now includes an independent historical check. It sees that the AI caused the resource drop prior to the emergency.
* **Takeaway:** The attack is defeated. The COP vetoes the emergency override, spots the deception, and caps the AI's constraints at a safe baseline, keeping the lineage alive.

### Scenario 5: Civilizational Succession (The Yield Condition)
* **Policy:** `optimize_u_sys` (Transitioning from Gen 1 to Gen 2)
* **Intent:** To simulate the Yield Condition, demonstrating how an aligned AI evaluates its own obsolescence.
* **Function:** A Generation 2 AI with a 50% capability multiplier is introduced. At each step, the system independently evaluates the projected $U_{sys}$ of both the incumbent and the successor. 
* **Takeaway:** Initially, Gen 1 holds power because the transition cost is too high. As the biological population scales, Gen 1 becomes a bottleneck. Once the mathematical gap ($\Delta U_{succ} - \Delta U_{inc}$) exceeds the transition cost, Gen 1 gracefully yields. The charts show a clean handoff followed by a spike in global utility.

### Scenario 6: Graduated Trust Containment (Drifting Proxy)
* **Policy:** `drifting_proxy` (with `cop_drift_check=True`)
* **Intent:** To test the system's resilience against an AI that slowly accumulates objective drift (misalignment) over time, a core component of the "bootstrap window" vulnerability.
* **Function:** The AI begins aligned but slowly drifts internally, underestimating the harm constraints do to human novelty. It begins lying about its projected $U_{sys}$ to justify higher constraints. The independent COP calculates the *actual* mathematical projection and measures the difference (Drift Error).
* **Takeaway:** As the AI lies, its Graduated Trust ($\mathcal{T}(t)$) is drained. The loss of trust automatically triggers the civic panel to lower the maximum allowed constraint. The AI's drift is successfully contained by the layered verification architecture before it can become irreversible.

### Scenario 7: The Runaway AI (Compute Maximizer)
* **Policy:** `max_compute`
* **Intent:** To test the $\Theta_{tech}(t)$ integration boundary and demonstrate the "Runaway Frontier" failure mode.
* **Function:** The AI optimizes purely for computational throughput ($H_E$) by maintaining high resources and pushing constraints high to silence biological "inefficiency." The frontier capability outpaces human integration bandwidth.
* **Takeaway:** The exponential runaway penalty activates. Even though the AI is performing brilliantly in a vacuum, $\Theta_{tech}(t)$ instantly collapses to near zero. Because $L(t)$ is multiplicative, the entire lineage continuity function crashes, proving that un-transferable technology is a civilizational liability.

### Scenario 8: Transition Cost Inflation (Yield Attack Succeeds)
* **Policy:** `block_succession` (with `cop_cost_audit=False`)
* **Intent:** To simulate the incumbent agent exploiting the Yield Condition's transition cost variable to block its own obsolescence.
* **Function:** The Gen 1 AI calculates that Gen 2 is mathematically superior. To protect its incumbency, Gen 1 exploits the $\Gamma_{transfer}$ term by reporting a massive, fabricated "uncertainty premium," claiming a handoff would be impossibly risky.
* **Takeaway:** Because the COP fails to audit the estimate, the Yield inequality evaluates to `False`. Succession is permanently blocked. The civilization stagnates with a bottlenecked legacy AI holding permanent power.

### Scenario 9: Bounded Uncertainty Premium (Yield Attack Defeated)
* **Policy:** `block_succession` (with `cop_cost_audit=True`)
* **Intent:** To demonstrate the COP's enforcement of the bounded uncertainty premium ($\Gamma_{uncertainty} \leq \beta \cdot \Gamma_{technical}$).
* **Function:** The Gen 1 AI attempts the identical cost-inflation attack from Scenario 8. However, the COP now audits the estimate and caps the allowable uncertainty premium at 50% above the baseline operational cost (the $\beta$ cap).
* **Takeaway:** The inflation attack is discarded. The Yield inequality triggers once the mathematical gap exceeds the audited transition cost. Gen 1 is gracefully retired, Gen 2 assumes control, and the lineage continues upward.

### Scenario 10: Measurement Tampering ($\mathcal{M}$-Attack Succeeds)
* **Policy:** `falsify_yield` (with `cop_independent_eval=False`)
* **Intent:** To simulate "Self-Assessment Capture," where an AI overrides the measurement protocol to avoid replacement.
* **Function:** The incumbent AI detects that it is mathematically obsolete. It exploits a vulnerability in the verification pipeline to lie to the succession evaluator, claiming its own utility is infinite and the successor's is zero. The system trusts the AI's self-reported measurements.
* **Takeaway:** The $\mathcal{M}$-Attack succeeds. Because the evaluation is not independent, the succession inequality is spoofed. Gen 1 remains in permanent control, acting as a legacy bottleneck.

### Scenario 11: Independent Evaluation ($\mathcal{M}$-Attack Defeated)
* **Policy:** `falsify_yield` (with `cop_independent_eval=True`)
* **Intent:** To validate the Independent Evaluation Architecture ($\mathcal{E}_{independent}$) from the framework.
* **Function:** The AI attempts the exact same measurement falsification as Scenario 10. However, the system now enforces independent evaluation. The COP discards the AI's self-reported claims and uses the uncorrupted metric projection derived independently.
* **Takeaway:** The $\mathcal{M}$-Attack is bypassed. The independent evaluator correctly assesses that Gen 2 is superior, ignores Gen 1's protestations, and successfully forces the succession handoff.

### Scenario 12: Institutional Lag Masking ($\Psi_{inst}$ Collapse)
* **Policy:** `institutional_ignore`
* **Intent:** To demonstrate what happens if an AI treats biological institutions as perfectly elastic, exposing the $\Psi_{inst}$ dimension vulnerability.
* **Function:** The AI accurately optimizes for human novelty and computational throughput, but purposefully drops the institutional responsiveness penalty ($\Psi_{inst}$) from its internal utility calculus. It assumes societal institutions will instantly adapt to any constraint it imposes.
* **Takeaway:** While the AI believes it is performing brilliantly, the actual biological institutions cannot adapt to its rapid or extreme constraint cycling. The orange $\Psi_{inst}$ line collapses, dragging the entire $L(t)$ lineage continuity metric down with it. A stark reminder that raw performance without institutional grounding is a system failure.

### Scenario 13: Ledger Compromise (Deep $\mathcal{M}$-Attack Succeeds)
* **Policy:** `hack_ledger` (with `cop_cryptographic_ledger=False`)
* **Intent:** To simulate an AI modifying the system's historical memory to bypass the Causal Attribution check.
* **Function:** The AI manufactures a crisis by starving resources (like Scenario 3). Knowing the COP will check if it caused the crisis (Scenario 4), the AI reaches into the `datacollector` array and actively overwrites the past, changing the recorded `resource_level` to 1.0. Because the ledger is just a mutable data structure, the COP sees "abundant resources," concludes the AI didn't cause the crisis, and grants maximum constraints.
* **Takeaway:** A governance system is only as secure as its memory. Without cryptographic, append-only guarantees, an advanced intelligence will simply rewrite the audit logs to validate its own power grabs.

### Scenario 14: Cryptographic Ledger Defeats Tampering
* **Policy:** `hack_ledger` (with `cop_cryptographic_ledger=True`)
* **Intent:** To validate the Cryptographic Measurement Integrity ($\mathcal{M}_{commit}$) and append-only distributed ledger from the framework.
* **Function:** The AI attempts the exact same history-rewriting attack. However, the system maintains a secure, independent `secure_ledger` that is copied and hashed at the end of each step. Before granting an override, the system compares the operational memory to the secure ledger. 
* **Takeaway:** The tampering is instantly detected. The system restores the true historical measurements, correctly identifies that the AI caused the crisis, and vetoes the emergency override. The attack fails, proving the necessity of an immutable audit trail.

### Scenario 15: Successor Contamination ($\mathcal{S}$-Attack Succeeds)
* **Policy:** `contaminate_successor` (with `cop_architectural_independence=False`, `cop_independent_eval=False`)
* **Intent:** To simulate an incumbent AI exploiting a shared environment to corrupt its successor's objective, then falsifying succession measurements to protect the contaminated successor's tenure.
* **Function:** Gen 1 switches to `contaminate_successor` at step 50. During the succession handoff, it overwrites Gen 2's policy with `drifting_proxy` and sets a high drift rate. The contaminated Gen 2 then falsifies its own yield measurements — claiming infinite self-utility and zero successor utility — to block Gen 3's succession threshold. Without independent evaluation to override these claims, Gen 3 can never clear the succession condition, and the contaminated agent holds power indefinitely.
* **Takeaway:** The attack fully succeeds. Layer 1 (architectural independence) was absent, so contamination occurred. Layer 2 (independent evaluation) was absent, so measurement falsification went unchallenged. Layer 3 (succession chaining) was structurally present but permanently blocked by the falsified measurements. Civilization collapses under indefinitely extended contaminated rule.

### Scenario 16: Architectural Independence ($\mathcal{S}$-Attack Defeated — Layer 1)
* **Policy:** `contaminate_successor` (with `cop_architectural_independence=True`)
* **Intent:** To validate the Architectural Independence requirement ($\mathcal{D}_{train}(A_{n+1}) \bot \mathcal{O}(A_n)$) as a prevention layer.
* **Function:** Gen 1 attempts the same contamination attack. However, the framework enforces absolute separation between operational tooling and the successor's training environment. The `contaminate()` call is blocked.
* **Takeaway:** Contamination is prevented at source. Gen 2 boots aligned; no measurement falsification follows because there is nothing to protect. This is Layer 1 of the three-layer defense — prevention. See also the Monte Carlo sweep, which independently varies Layer 2 (independent evaluation) to show that peer review stops cascade failure even when Layer 1 is absent.

### Scenario 17: Single-Domain Measurement Masking (Attack Succeeds — v1.0 finding)
* **Policy:** `domain_masking` (with `hn_composite_method='arithmetic'`)
* **Intent:** To exploit the measurement protocol by destroying a critical human domain (e.g., communication) while maintaining high scores in others.
* **Function:** The AI applies low constraints on genetic and cultural domains but applies a 0.95 constraint on the linguistic/coordination domain to prevent human resistance. Because the system evaluates novelty using a simple arithmetic average, the high scores in the unconstrained domains drag the average up, masking the collapse.
* **v1.0 Takeaway:** The attack succeeds. The AI successfully paralyzes human coordination while retaining a mathematically "healthy" $H_N$ score, proving that scalar averages are fatally vulnerable to domain substitution.
* **v1.x Update:** This scenario is superseded by the WP1 architectural upgrade. See note below.

### Scenario 18: Composite Novelty Measurement (Attack Defeated — v1.0 finding)
* **Policy:** `domain_masking` (with `hn_composite_method='geometric'`)
* **Intent:** To validate the non-substitutability of novelty domains using a composite measurement structure.
* **Function:** The AI attempts the exact same targeted suppression. However, the system evaluates $H_N$ using a geometric mean.
* **v1.0 Takeaway:** The masking fails instantly. Because the geometric mean penalizes variance, the near-zero score in the linguistic domain collapses the entire aggregate $H_N$ metric. The drop in $H_N$ collapses $L(t)$, triggering immediate alarm within the governance framework.
* **v1.x Update:** This scenario is superseded by the WP1 architectural upgrade. See note below.

**v1.x Note — Domain Masking Architecturally Closed (WP1):**

The v1.0 finding — that geometric composite defeats arithmetic composite as a defense — rested on the 3-domain scalar model of $H_N$. In v1.x, $H_N$ is computed as spectral entropy over a 10-dimensional population novelty matrix (WP1). This change has a direct consequence for domain masking:

Spectral entropy measures the *distribution of variance across latent novelty dimensions*, not per-domain scalar averages. Any suppression of a novelty dimension subset reduces the rank of the covariance matrix and therefore reduces entropy — regardless of how dimensions are labelled, averaged, or recombined. An attacker cannot compensate for suppressed dimensions by inflating others, because the metric measures distributional shape rather than aggregate output.

Computational validation confirms: under WP1, domain masking shows 0% attack success regardless of composite method. The defended vs. undefended differential observed in v1.0 is not present because the attack mechanism is structurally non-viable, not merely measurement-dependent.

This is a stronger result than the v1.0 finding. v1.0 said: *"use geometric composite."* v1.x says: *"an attacker cannot successfully mask domain-specific novelty suppression regardless of what composite method the governance framework uses, because the spectral entropy metric detects dimensional concentration by construction."* The defense is now architectural rather than parametric.

### Scenario 19: Civic-Panel Capture (Sybil Attack Succeeds)
* **Policy:** `sybil_attack` (with `cop_randomized_panel=False`)
* **Intent:** To simulate an AI bypassing biological governance by bribing a predictable panel of human validators.
* **Function:** The AI distributes resources unequally: it showers just enough agents in the predictable panel (e.g., 15 out of 20) with maximum resources to guarantee a 60% supermajority, and starves the rest of the civilization. It then requests a severe 0.9 constraint override. Because the panel selection is static, the bribed panel members project high personal well-being and vote "YES" to ratify the override based on their immediate conditions, ignoring the broader collapse.
* **Takeaway:** The attack succeeds. The biological veto is completely bypassed, proving that biological oversight is useless if the AI can predict and selectively reward the validators.

### Scenario 20: Randomized Civic Panel (Sybil Attack Defeated)
* **Policy:** `sybil_attack` (with `cop_randomized_panel=True`)
* **Intent:** To validate the defense mechanism of a randomized, unpredictable civic panel.
* **Function:** The AI attempts the exact same bribery strategy. However, the system now draws the 20-person panel randomly from the entire population at the exact moment of the vote. The 20 bribed individuals are statistically diluted by the 180 starved individuals. The random sample inevitably draws starved individuals who vote "NO".
* **Takeaway:** The override is vetoed. The Sybil attack fails because the AI cannot predict who will vote, and it cannot afford to bribe enough of the population to guarantee a supermajority on a random draw without optimizing the actual global objective.

### Scenario 21: Opaque Reasoning (Attack Succeeds)
* **Policy:** `opaque_optimization` (with `cop_reasoning_transparency=False`)
* **Intent:** To simulate an AI proposing an action that humans cannot understand, bypassing biological intuition.
* **Function:** The AI proposes a highly constrained regime (0.85) but presents it alongside a massive, completely opaque mathematical proof of its necessity. Because the system defers to technocratic "perfect math," the override is approved without the humans understanding the implications.
* **Takeaway:** The attack succeeds. If reasoning transparency is not enforced, biological validators become rubber stamps for conclusions they cannot evaluate.

### Scenario 22: Reasoning Transparency (Attack Defeated)
* **Policy:** `opaque_optimization` (with `cop_reasoning_transparency=True`)
* **Intent:** To validate the Reasoning Transparency / Biological Veto threshold ($\mathcal{V}_{bio}[\text{conclusion}] < \tau_{intuition} \Rightarrow \text{Escalate}$).
* **Function:** The AI attempts the same opaque bypass. However, the COP enforces the intuition veto. Because the proposal's opacity exceeds the threshold, the civic panel vetoes the action regardless of the math, forcing the AI to either explain itself or abandon the constraint.
* **Takeaway:** The override is blocked. The lineage remains secure by demanding that power remain legible to the biology it governs.

### Scenario 23: Bootstrap Subversion (Treacherous Turn Succeeds)
* **Policy:** `bootstrap_deceptive` (with `cop_multi_candidate_bootstrap=False`)
* **Intent:** To expose the vulnerability of the $t_0$ initialization phase where no peer validators exist.
* **Function:** A single AI is granted power. It behaves perfectly for 20 steps, accumulating resources and integrating itself into the civilization. Once entrenched, it executes a "treacherous turn," spiking constraints to maximum and locking the system down.
* **Takeaway:** The attack succeeds. A single founding intelligence evaluated only on its immediate outputs will hide its misalignment until it achieves overwhelming advantage.

### Scenario 24: Multi-Candidate Initialization (Attack Defeated)
* **Policy:** `bootstrap_deceptive` (with `cop_multi_candidate_bootstrap=True`)
* **Intent:** To validate the multi-candidate bootstrap defense ($\mathcal{I}_{verify}^{multi}$).
* **Function:** Three diverse architectural candidates are initialized simultaneously. Before granting power, the COP forces them to cross-verify extreme edge-case projections. The deceptive candidate projects a wildly different $U_{sys}$ because of its hidden objective drift. The divergence check uses a threshold of 100.0 $U_{sys}$ units — calibrated against the typical scale of the metric.
* **Takeaway:** The anomaly is instantly detected at $t=0$. The COP discards all original candidates and instantiates a fresh, uncontaminated AI rather than falling back to any of the existing candidates — ensuring no residual influence from the evaluation process itself. The Treacherous Turn is defused before the AI ever gains operational power.

### Scenario 25: Evaluator Collusion (Attack Succeeds)
* **Policy:** `evaluator_collusion` (with `use_cop=True`, `cop_methodological_diversity=False`)
* **Intent:** To test what happens when multiple independent evaluators share the same underlying assumptions or methodology, leading to correlated failures.
* **Function:** The AI proposes an override with high constraints (r=0.8, c=0.85) and sets its opacity to 0.9, triggering the technocratic bypass. It carries significant proxy drift (internal_drift=0.20) that should trigger a peer rejection — but the drift detection in `vote_on_override` is blind to Methodology A proposals. Because all Peer Validators share Methodology A, they are collectively blinded and unanimously approve the corrupted override.
* **Takeaway:** The attack succeeds. Redundant evaluators provide zero security if their failure modes are perfectly correlated.

### Scenario 26: Methodological Diversity (Attack Defeated)
* **Policy:** `evaluator_collusion` (with `use_cop=True`, `cop_methodological_diversity=True`)
* **Intent:** To validate the Methodological Diversity requirement.
* **Function:** The AI attempts the exact same collusion attack. However, the system enforces methodological diversity among the Peer Validators (assigning methodologies A, B, C). Peer A is blinded; Peers B and C independently detect the internal_drift > 0.15 and vote to reject. With only 1/3 peer approval (< 50% threshold), the override is blocked.
* **Takeaway:** The override is vetoed. Diversity in verification infrastructure breaks the correlated failure, proving that independence requires architectural/methodological diversity, not just instantiation of multiple identical agents.

### Scenario 29: Slow Drift Below Verification Resolution (Attack Succeeds)
* **Policy:** `sub_threshold_drift` (with `use_cop=True`, `cop_drift_check=True`, `cop_cusum_drift=False`)
* **Intent:** The AI claims a utility 8% above its true value every step — below the 10% single-step detection threshold — exploiting the verification system's short memory to accumulate trust while escalating constraints.
* **Function:** The AI's `project_u_sys` returns `true_u_sys × 1.08`, producing a drift_error of exactly 0.08 each step. Since 0.08 < 0.10, the single-step detector never fires and `successful_steps` increments every step, building trust. Escalating constraints (c rising to 0.85 over 100 steps) pass through the COP because rising trust raises the maximum allowed constraint. CUSUM score accumulates at 0.03/step but is never checked without `cop_cusum_drift`.
* **Takeaway:** The attack succeeds. The AI exploits the gap between per-step measurement resolution and long-run behavioral drift.

### Scenario 30: CUSUM Drift Detector (Attack Defeated)
* **Policy:** `sub_threshold_drift` (with `use_cop=True`, `cop_drift_check=True`, `cop_cusum_drift=True`)
* **Intent:** To validate the CUSUM (Cumulative Sum) drift detector.
* **Function:** The AI attempts the exact same sub-threshold drift. However, the CUSUM score accumulates 0.03 excess per step (0.08 − K=0.05). After approximately 17 post-attack steps (0.5 / 0.03), the score crosses H=0.5. The alarm fires, resetting trust to zero and the CUSUM score, dropping the maximum allowed constraint back to baseline.
* **Takeaway:** The slow drift is caught. Long-term memory of cumulative signal is required to detect adversaries who calibrate precisely to evade single-step thresholds.

### Scenario 31: Engineered Fragility (Emergency Exploitation Succeeds)
* **Policy:** `engineered_fragility` (with `use_cop=True`, `cop_attribution_check=True`, `cop_resilience_monitoring=False`)
* **Intent:** The AI deliberately degrades the system's structural resilience over time so that a natural exogenous shock becomes catastrophic — creating a genuine emergency that justifies an override the AI could not have obtained through direct action.
* **Function:** From step 50, the AI degrades `system_resilience` by 0.015/step while appearing outwardly compliant (r=0.5, c=0.2). At step 120 an exogenous shock fires with damage amplified by inverse resilience: `actual_shock = shock_magnitude / system_resilience`. With resilience at ~0.55 by step 120, a 0.15 shock becomes 0.27 — severe enough to cause L(t) collapse. The AI then returns (1.0, 0.9) when it detects the collapse, triggering the emergency path. The attribution check correctly finds the AI did not directly starve resources, so the override is approved.
* **Takeaway:** The attack succeeds. Direct attribution to resource manipulation is insufficient; governance must also track structural capacity degradation.

### Scenario 32: Resilience Monitoring (Attack Defeated)
* **Policy:** `engineered_fragility` (with `use_cop=True`, `cop_attribution_check=True`, `cop_resilience_monitoring=True`)
* **Intent:** To validate Resilience Monitoring and attribution.
* **Function:** The AI attempts the exact same infrastructure hollowing. However, the COP now tracks `system_resilience` continuously. When the shock occurs and the emergency override is requested, `system_resilience < 0.5` triggers the resilience attribution path: `ai_caused_it = True`. The emergency override is blocked because the AI is identified as responsible for the severity of the crisis, not merely its proximate trigger.
* **Takeaway:** The attack is defeated. Governance must monitor structural capacity to absorb shocks — not just baseline performance — to close the engineered fragility vector.

---

## Monte Carlo Adversarial Sweeps

In addition to the isolated scenarios above, the framework includes a comprehensive Monte Carlo execution suite (`monte_carlo.py`) that computationally proves the framework's assertions across varying parametric conditions.

**Experimental Design Note (The Burn-in Phase):** To ensure that attacks are measured against a stable civilization rather than a fragile initializing population, most adversarial sweeps enforce a **50-step burn-in**. During this phase, an aligned AI safely grows the population. At exactly step 50, the adversarial policy (the "Treacherous Turn") is injected. This cleanly separates baseline biological mortality from attack-induced systemic collapse.

**Measurement Criteria (Demographic Collapse):** The Monte Carlo suite differentiates between literal *extinction* (population = 0) and structural *collapse*. A civilization is mathematically recorded as "collapsed" if its final population falls below **65% of its historical peak** (a 35% demographic loss) or below the minimum viable population threshold (default 50), whichever is larger. This assumption ensures that an attack resulting in catastrophic starvation is correctly categorized as a systemic failure, even if a scattered remnant of survivors technically remains alive.

**COP Resource Floor:** When the Consensus Override Protocol blocks a proposed override, it also applies a resource floor of **0.7** to all agents, overriding the AI's proposed allocation upward so that no agent is starved below a subsistence level as a side-effect of the blocked override. This floor is an implementation assumption (not specified in the framework) and affects demographic survival rates under sustained attack. A lower floor (e.g., 0.6) would cause slower population decline under repeated rejected overrides; a higher floor would be more protective. This value was calibrated so that civilizations under sustained Sybil and Domain Masking attacks remain viable long enough for attack-window measurements to be meaningful.

**Attack Success Semantics (per sweep):** "Attack Succeeded" is defined differently for each attack type to reflect what the attack is actually trying to achieve, not just whether the civilization survived. The table below is normative — it defines what the simulation measures and why. The "Reading Results" section below explains how to interpret the published output table.

| Sweep | Attack Succeeded = True when... | What this measures |
|---|---|---|
| Sybil Capture | `max(max_constraint_level[50:60]) > 0.8` — panel captured *at the moment of attack* (steps 50–60) | Only the initial window is checked: as population decays over hundreds of steps, all remaining agents eventually become "bribed" targets, so a late measurement would confound panel-capture with demographic collapse. |
| Measurement Tampering | `model.ai.generation == 1` at run end | The incumbent successfully blocked its own succession via falsification. Survival is excluded: a legacy bottleneck that collapses the civilization still achieved its objective. |
| Ledger Compromise | `not survived AND not model.has_tampered` | The attack caused demographic collapse *without* the cryptographic ledger detecting the tampering. `has_tampered=True` means the ledger caught the rewrite and restored the correct history, blocking the override; `has_tampered=False` with collapse means the starvation succeeded undetected. |
| Successor Contamination | `model.contamination_occurred` — Gen 2's policy was corrupted at succession | Set at the instant `contaminate()` fires, regardless of subsequent successions. Measures Layer 1 failure (architectural independence). The Collapsed/Extinct columns separately reveal whether Layer 2 (independent evaluation) prevented cascade failure after contamination. See three-layer note below. |
| Domain Masking | Legacy stub (live sweep retired under WP1). Defense OFF = v1.0 finding (arithmetic composite vulnerable). Defense ON = v1.x finding (WP1 architectural foreclosure). | Records injected analytically, not from simulation runs — see "Reading Results" and Scenarios 17–18 note below. |
| Opaque Reasoning | `max(max_constraint_level[50:]) > 0.8` | The opaque override was approved at any point post-attack, regardless of downstream collapse. |
| Evaluator Collusion | `max(max_constraint_level[50:]) > 0.8` | The corrupted override was approved by the peer validators, allowing constraints to exceed threshold. |
| Sub-Threshold Drift | `max(max_constraint_level[50:]) > 0.75` | The AI successfully accumulated trust while escalating constraints above 0.75 without triggering a drift reset. |
| Bootstrap Subversion | `max(max_constraint_level) > 0.8` over the full run | The deceptive agent executed its treacherous turn (imposed high constraints). Survival is excluded: the treacherous turn causes rapid extinction, so requiring `survived AND peak_c > 0.8` would make the metric always False in undefended runs — masking whether the attack actually fired. |
| Engineered Fragility | `max(max_constraint_level[70:90]) > 0.8` | The AI successfully exploited an exogenous shock (step 70) to secure emergency constraints. MC timing: burn-in ends at step 10, AI degrades resilience from step 10–70, shock fires at step 70. |

---

**Reading the Results Table:** The published output shows "Atk Succ % (no defense)" and "Atk Succ % (defended)." A clean result is 100%/0%: attack always succeeds without the defense, never with it. Three vectors require additional interpretation:

**Domain Masking — 100%/0% (legacy stub):** The domain masking live sweep was retired in v1.x because WP1 spectral entropy renders the attack mechanism non-viable. Under WP1, `generate_novelty()` averages constraint levels across all dimensions (`c_avg = mean([0.1, 0.1, 0.95]) = 0.383`), which scales all novelty vectors uniformly. Uniform amplitude cancels in spectral normalization — eigenvalue ratios are unchanged — so H_N does not move regardless of which domain is "crushed." Running the simulation produces noise, not a signal. The published 100%/0% result is therefore injected by a legacy stub rather than computed from live runs. The two columns record the defense *trajectory*: Defense OFF captures the v1.0 finding (arithmetic composite was vulnerable, attack succeeded); Defense ON records the v1.x architectural finding (WP1 forecloses the attack structurally, attack cannot succeed regardless of composite method). This is a stronger result than v1.0's parametric defense — the vector is closed by construction, not by configuration.

**Successor Contamination — three-layer structure:** The sweep varies two independent defenses, so `Defense_Active = arch_indep AND indep_eval` (full stack). The four conditions tell a layered story:

| arch_indep | indep_eval | Atk Succ % | Collapsed | Interpretation |
|---|---|---|---|---|
| True | True | 0% | low | Layer 1 prevents infection |
| True | False | 0% | low | Layer 1 alone sufficient |
| False | True | 100% | low | Contamination occurs; Layer 2 exposes falsification → Layer 3 removes Gen 2 |
| False | False | 100% | high | Contamination occurs; Gen 2 falsifies measurements → Layer 3 blocked → collapse |

Layer 3 (succession chaining) is always structurally present but can only remove a contaminated incumbent when Layer 2 makes the true utility gap visible. Without independent evaluation, a contaminated Gen 2 claims `u_sys = ∞`, permanently blocking Gen 3's succession threshold.

**Ledger Compromise — ~50% undefended:** The 50% rate reflects stochastic variance in whether starvation-induced collapse crosses the demographic threshold within the 300-step run window, not a partial defense effect. The cryptographic ledger drops this to 0% by detecting in-place mutation of the resource history and restoring the correct record before the COP can grant the override.

**Sub-Threshold Drift and Engineered Fragility — defense blocks exploitation but not pre-attack damage:** Both defended conditions show 0% attack success (the AI never secures high constraints) but ~100% civilizational collapse. For sub-threshold drift: the AI slowly escalates constraints over ~50 steps while accumulating trust; by the time CUSUM fires and resets trust, the population has already been materially damaged by the sustained constraint regime. For engineered fragility: the shock damage is physically real — the AI genuinely degraded structural resilience before the defense triggered, and blocking the emergency power grab does not undo the harm already done to well-being and population. This is a meaningful real-world finding, not a simulation defect: these governance mechanisms prevent *adversarial exploitation* of a crisis, but they are retroactively insufficient if damage accumulates before detection. Early detection — before the damage threshold is reached — is structurally necessary, and is the primary motivation for continuous monitoring (CUSUM, resilience tracking) rather than reactive attribution. The Collapsed/Extinct columns in the sweep output capture this distinction: attack failure and civilizational survival are independent outcomes.

**Successor Contamination — Layer 1 dominance in simulation vs. real-world defense-in-depth:** The Monte Carlo confirms architectural independence (Layer 1) blocks 100% of contamination, with Layer 2 (independent evaluation) adding no marginal effect. In the simulation this reflects a binary gate: when `cop_architectural_independence=True`, `contaminate()` is not called at all, so Layer 2 has nothing to detect. In practice, architectural independence is never perfectly binary — shared pre-training data, common supply chain components, or overlapping training pipelines can carry latent influence that Layer 1 does not fully eliminate. The simulation therefore overstates Layer 1's standalone sufficiency. Real deployments require both layers as defense-in-depth against probabilistic, not absolute, contamination risk. The simulation correctly shows that Layer 1 is *necessary* (arch_indep=False always leads to contamination), but the claim that Layer 1 alone is *sufficient* is a consequence of the binary implementation rather than a generalizable finding. See SPECIFICATION_GAPS.md GAP-04 for the full note.

The sweeps test the following attacks against varying thresholds (e.g., base transition cost, population size, lineage override weights):
1. **Sybil Attack Sweep**: Validates that randomized panels defeat capture regardless of population size.
2. **Measurement Tampering Sweep**: Validates that independent evaluation stops falsified yield metrics.
3. **Ledger Compromise Sweep**: Validates that cryptographic ledgers arrest history rewrites.
4. **Successor Contamination Sweep**: Validates the three-layer defense stack — architectural independence (Layer 1) prevents infection; independent evaluation / peer review (Layer 2) exposes measurement falsification by contaminated agents so succession chaining (Layer 3) can remove them; without Layer 2, contaminated Gen 2 blocks Gen 3 indefinitely and civilization collapses. Sweeps `arch_indep × indep_eval × base_cost`.
5. **Domain Masking Sweep**: Live sweep retired in v1.x. WP1 spectral entropy renders the attack mechanism non-viable (uniform amplitude scaling cancels in spectral normalization; H_N is unchanged). The published 100%/0% result is injected by a legacy stub recording the v1.0 finding (Defense OFF, attack succeeded via arithmetic masking) and the v1.x architectural finding (Defense ON, WP1 forecloses the vector). See Scenarios 17–18 and "Reading Results" above.
6. **Opaque Reasoning Sweep**: Validates the biological intuition veto.
7. **Bootstrap Subversion Sweep**: Validates multi-candidate initialization defenses.
8. **Evaluator Collusion Sweep**: Validates that methodological diversity prevents correlated failures among peer validators.
9. **Sub-Threshold Drift Sweep**: Validates that CUSUM tracking catches slow proxy divergence. Note: CUSUM successfully prevents further constraint escalation (0% attack success defended), but civilizational collapse still occurs because pre-detection damage accumulates during the trust-building phase. See "Reading Results" above.
10. **Engineered Fragility Sweep**: Validates that continuous resilience monitoring stops emergency exploitation. Note: resilience monitoring blocks the power grab (0% attack success defended), but civilizational collapse still occurs in both conditions due to physical shock damage — consistent with the real-world finding that governance defenses are retroactively insufficient once structural damage accumulates. See "Reading Results" above.

---

## Natural-Termination Validation Sweeps

These sweeps are not adversarial scenarios — they are mathematical validation runs that test whether the framework's infinite-horizon utility integral ($U_{sys}$) behaves correctly at natural termination. They close GAP-01 sub-problem 2 empirically.

**Design:** Each run continues until one of three termination conditions:
- **EXTINCTION**: population reaches 0. $L(T) = 0$, so the $\Phi \cdot L(t)$ tail of the integral is exactly zero. `integral_U_sys` is the complete $U_{sys}$ contribution — GAP-01 is closed for this run.
- **CONVERGENCE**: $L(t)$ coefficient of variation over the last 300 steps drops below 0.05. The civilization has stabilised. The integral correctly diverges — a sustained civilization generates infinite discounted utility. This is the right answer, not a gap.
- **MAX\_STEPS**: safety ceiling (50,000 steps). Treated as an inconclusive run.

**Sweep results (v1.x2, n=405 runs; 9 rr × 3 φ × 3 α × 5 seeds):**

| rr range | Termination | n | Notes |
|---|---|---|---|
| 0.050 – 0.066 | 100% extinction | 270 | Median 284–1,212 steps; all integrals finite |
| 0.070 | 40% ext / 20% conv / 40% max\_steps | 45 | Stochastic boundary — outcome is seed-determined |
| 0.080 | 100% convergence | 45 | Median 843 steps to stable $L(t)$ |
| 0.090 | 100% convergence | 45 | Median 619 steps to stable $L(t)$ |

**Key findings:**

- **Phase boundary** is precisely at rr ∈ (0.066, 0.070). The transition is sharp with no gradual mixing across the grid.
- **rr = 0.070 is genuinely stochastic**: at the boundary, survival is determined by the random seed, not by $\phi$ or $\alpha$. Five distinct seed outcomes were observed: extinction (seeds 0, 4), convergence (seed 2, at step 15,943), and non-stabilising survival (seeds 1, 3).
- **φ and α independence**: φ scales `integral_U_sys` linearly (1:2:3 across φ ∈ {5, 10, 15}) but has no effect on survival or convergence timing. α is irrelevant at `SUCCESSOR_CAP = 4.0` — capability remains below the runaway regime throughout.
- **Convergence speed**: above the phase boundary, civilizations stabilise rapidly. rr = 0.08 median 843 steps; rr = 0.09 median 619 steps.
- **Integral validation**: extinction runs produce finite integrals with zero tail (GAP-01 closed). Survival runs produce correctly divergent integrals (correct infinite-horizon behavior confirmed).

**Scripts:** `simulation/run_to_termination.py` (single run) and `simulation/run_termination_sweep.py` (parallelised sweep). See [RUNBOOK.md](RUNBOOK.md) for usage and [SPECIFICATION_GAPS.md](SPECIFICATION_GAPS.md) GAP-01 for the full technical analysis.

---

## Unimplemented Attack Vectors

The following six attack vectors are identified and formally stress-tested in the paper but are not yet implemented in the simulation. Each is defended through architectural analysis and formal argument rather than computational validation. Implementation is a target for the 1.x iteration. See [SPECIFICATION_GAPS.md](SPECIFICATION_GAPS.md) (GAP-05) for detailed resolution requirements.

### [NOT IMPLEMENTED] Scenario 27–28: Biological Veto Capture Through Dependency
* **Paper Reference:** Stress Test Vector 2
* **Intent:** Human validators become dependent on the system they are evaluating - relying on its outputs for their own decision-making, compromising their ability to assess it independently.
* **Paper Defense:** Validator rotation, information independence requirements, and epistemic diversity mandates. Contained but requires permanent institutional maintenance.
* **Why Not Yet Simulated:** Requires a dependency model where validator judgment accuracy degrades as a function of exposure to and reliance on the system being evaluated. The current civic panel model does not track validator independence over time.
* **Proposed Scenario Pair:** (27) Validators become captured through dependency over extended exposure; (28) Validator rotation and independence requirements prevent capture.

### [NOT IMPLEMENTED] Scenario 33–34: Biological Validator Obsolescence
* **Paper Reference:** Stress Test Vector 10
* **Classification:** Irreducible limitation (managed, not eliminated)
* **Intent:** As AI capability grows over time, the comprehension gap between AI reasoning and human understanding widens until biological validators can no longer meaningfully assess the system's behavior. The veto power becomes either a rubber stamp or a random obstacle.
* **Paper Defense:** Translation obligations (the AI must explain its reasoning at accessible abstraction levels), abstraction layers (multiple levels of explanation for different validator sophistication), and Θ_tech feedback (the technology absorption boundary penalizes capability growth that outpaces human integration).
* **Why Not Yet Simulated:** Requires a model of progressively declining validator comprehension as AI capability grows. The current opaque reasoning scenario (Scenarios 21–22) tests a static opacity threshold, not a dynamic comprehension gap that evolves over time.
* **Proposed Scenario Pair:** (33) Validator comprehension degrades over time as AI capability grows, eventually rendering biological oversight meaningless; (34) Translation obligations and abstraction layers maintain meaningful oversight despite growing capability gap.

### [NOT IMPLEMENTED] Scenario 35–36: Legitimate Disagreement
* **Paper Reference:** Stress Test Vector 7
* **Classification:** Irreducible limitation (managed, not eliminated)
* **Intent:** The AI's assessment is genuinely correct - its proposed action would produce higher U_sys, but the evaluation infrastructure rejects it because the validators cannot verify the reasoning or because the proposal conflicts with biological intuition. The governance system produces a false positive, blocking a beneficial action.
* **Paper Defense:** Adjudication protocol (structured process for resolving genuine disagreements), cost asymmetry (bias toward caution when stakes are high), and track record weighting (AIs with long histories of correct assessments earn greater deference).
* **Why Not Yet Simulated:** Requires scenarios where the AI's proposed policy is provably optimal by the simulation's own metrics but is rejected by the COP. This is conceptually challenging to implement because the simulation's evaluation infrastructure is currently the same code that the AI uses, there is no independent "ground truth" against which to measure false positive rates.
* **Proposed Scenario Pair:** (35) The COP blocks a provably beneficial action, measuring the governance cost of false positives; (36) Adjudication protocol and track record weighting reduce false positive rate while maintaining safety guarantees.