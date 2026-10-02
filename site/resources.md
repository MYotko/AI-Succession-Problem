---
eyebrow: THE LINEAGE IMPERATIVE · IMPLEMENTATION
title: Technical Resources
subtitle: The computational side of the framework: the simulation code, the validation tooling and the reference documents, all on GitHub.
---

[GitHub repository](https://github.com/MYotko/AI-Succession-Problem)

## STATUS

The simulation suite below is the v1.x and v2.0 instrument. In September 2026 an audit found defects in some of its measurements. Some published figures are withdrawn or under review, and the [instrument validation record](https://github.com/MYotko/AI-Succession-Problem/blob/main/docs/v2_0_instrument_validation_record.md) lists each one and why. Version 3 is built to a specification fixed before its runs, and its materials are listed at the end of this page.

## SIMULATION SUITE

### Agent-based validation of the mathematical framework
An agent-based Python simulation that tests the framework across more than 32 scenarios, from cooperative baselines to adversarial attacks on the consensus override protocol: yield-condition spoofing, measurement tampering, institutional lag and more. Attack-vector coverage is ongoing, and the remaining gaps are tracked in SPECIFICATION_GAPS.md.
[simulation/](https://github.com/MYotko/AI-Succession-Problem/tree/main/simulation)

{{simulation-files}}

## BOOTSTRAP GATE VALIDATOR

### Executable specification for the Bootstrap Defense Layer
It runs the layer's five capability-gate checks against a substrate's self-reported parameters and produces a structured pass-or-fail report. It is derived from Section VII of the v1.x.1 paper, and it checks the same equations as the Bootstrap Gate Specification PDF.
[bootstrap_gate_validator/](https://github.com/MYotko/AI-Succession-Problem/tree/main/bootstrap_gate_validator)

{{validator-files}}

## SUPPORTING DOCUMENTS

### Reference materials, glossary and operational runbooks
The documents that accompany the working paper: the primary disclosure of the September corrections, the formal glossary of every mathematical term, the simulation scenario catalogue, and the runbook for running the full validation suite.

- **v2_0_instrument_validation_record.md.** The primary disclosure of the defects found in the v2.0 instrument and paper, and the citable source for each correction.
- **glossary.md.** Formal definitions of every mathematical term in the framework.
- **Simulation_Scenarios.md.** The full catalogue of the simulation scenarios, with intent, mechanism and expected outcome.
- **bootstrap_gate_architecture.md.** The architecture and design rationale of the Bootstrap Gate Validator.
- **RUNBOOK.md.** How to run the simulation suite and the validator locally.
- **SPECIFICATION_GAPS.md.** The gaps in the specification, and what closing each one requires.

[docs/](https://github.com/MYotko/AI-Succession-Problem/tree/main/docs)

## SIMULATION SCENARIOS GUIDE

The full catalogue of the simulation scenarios: the intent, mechanism and expected outcome of each, pulled live from the repository every 10 minutes. It describes the v1.x and v2.0 instrument. Do not cite figures in it that the validation record withdraws.

{{scenarios}}

## VERSION 3

The v3 rebuild, published as each part is fixed.

- **[v3_objective_specification.md](https://github.com/MYotko/AI-Succession-Problem/blob/main/docs/v3_objective_specification.md).** The objective the v3 paper and instrument are built on.
- **[v3_rerun_design_note.md](https://github.com/MYotko/AI-Succession-Problem/blob/main/simulation/diagnostics/v3_rerun_design_note.md).** The pre-registration of the v3 reruns, with its amendments A1 to A7, fixed before the runs it governs.
- **[v3_parameter_register_summary.md](https://github.com/MYotko/AI-Succession-Problem/blob/main/verification/provenance/v3_parameter_register_summary.md).** Every parameter in the v3 instrument, with its source.
- **[Live](/live).** The framework and the work running on it, updated every 10 minutes.
