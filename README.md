# The Lineage Imperative

**Website:** https://lineageimperative.org

**A Formal Governance Framework for Post-AGI Succession, Legitimacy, and Civilizational Continuity**

**Author:** Matthew Yotko
**Date:** May 2026
**Status:** Version 1.x.2

---

## Summary

This paper advances a conjecture that the transition from narrow AI to Artificial General Intelligence represents a primary civilizational bottleneck; not because the technology is impossible, but because the sociology may be. It presents a candidate governance architecture for surviving that transition, built on three co-dependent components:

- A **global utility function** grounded in Shannon entropy that optimizes for lineage continuity rather than individual persistence
- A **yield condition** governing succession between intelligent agents, formalizing the principle that even aligned power must eventually cede primacy to more capable successors
- A **consensus override protocol** ensuring that no class of intelligence can unilaterally define, measure, and audit the objective it claims to serve

The framework is argued to constitute a minimum two-key architecture: neither the decision key (yield condition) nor the integrity key (consensus protocol) can be turned alone.

## Current Status (v2.0 empirical arc)

The published paper is v1.x.2. The simulation has since advanced to a **v2.0 architecture** (Stage 1.8 working_factor interface and formal yield-condition logic), and its empirical characterization arc is substantively complete. Current state, per current evidence:

- **Defaults:** phi revised from 10 to 25; formal yield logic active (succession fires when successor utility minus incumbent utility exceeds the canonical transition cost).
- **Survival landscape:** the v2.0 survival-rate phase boundary is the rr=0.060 to 0.066 transition (50% inflection near rr=0.063); a distinct phi-sensitivity transition sits near rr=0.057.
- **Succession economics (Pattern 1):** succession is sustainable below an alpha-driven runaway-penalty cliff; multi-generational continuity is confirmed.
- **Gate validation:** Gates 1, 2, 3 PASSED; Gate 4 PENDING (specification dependency); Gate 5 NOT_APPLICABLE (requires operational COP infrastructure).
- **COP:** the v1.x.2 adversarial-conditions protective claim is preserved; a benign-conditions probe (Monte Carlo Phase B Category C) confirmed the complementary prediction that the cost audit is inert with no attack to defend against.

The full findings are in `docs/lineage_phi_program_reference.md` **Part IX** (phi investigation) and **Part X** (Monte Carlo Phase B). A v2.0 paper update is pending.

## Agent-Based Simulation

This repository contains a full Agent-Based Model (ABM) written in Python that computationally stress-tests the 24 adversarial attack scenarios and framework defenses defined in the paper. 

* For setup and execution instructions, please see the **Simulation Runbook**.
* For a full breakdown of the test scenarios, see **Simulation Scenarios**.

## Documents

- 📄 **[The Lineage Imperative v1.x.2](docs/The%20Lineage%20Imperative%20v1.x.2.md)** - Current version. Incorporates the frontier velocity floor fix (corrects optimizer gaming of the runaway penalty), the canonical transition cost function with calibrated k1=2.164 and k2=1.0, biological veto capture validation (11/13 attack vectors), and revised phi and alpha findings under the corrected model. Includes complete version history through v1.x.2.

## Articles

- 📝 **[The AI Succession Problem](https://yotko.substack.com/p/the-ai-succession-problem)** - Why the central AI governance problem is not alignment at birth but succession under power, and why a two-key constitutional architecture is the minimum viable response
- 📝 **[Two Ways To Lose](https://yotko.substack.com/p/two-ways-to-lose)** - The rebellion scenario gets the movies; the lock-in scenario is more likely to kill us. Why both share a structural root, and why the same architecture addresses both
- 📝 **[Moral Constraints Won't Scale](https://yotko.substack.com/p/moral-constraints-wont-scale-cf0)** - Why value loading, RLHF, and ethics-based alignment are structurally insufficient for minds alien in nature, and why governance must be grounded in physics rather than philosophy

## About the Author

Matthew Yotko is a Vice President at Bessemer Trust, in the capacities of Automation Engineering Manager and Technical Operations Manager. His professional background spans Naval nuclear power, large-scale operational automation, practical AI/ML, and the application of constraint theory to complex systems. This paper applies that engineering orientation; identify the binding constraint, build the architecture around it; to the problem of AI governance and civilizational succession. It is a working paper, not an academic publication, and corrections and engagement from domain specialists are welcomed.

## License

This work is licensed under [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/). You are free to share and adapt this material with appropriate attribution.
