# Blind certification: the A6 design (the W11 sensitivity and convergence runs, completed)

## Your role

You are an independent certifier. You did not write this design. Another certifier, from a different model family, reviews it independently, and neither of you sees the other's work. Find what is wrong, missing or unjustified. Where an item is statistical, write your own reasoning first, and only then compare it with the design's.

## Read

All paths are under `C:\Users\matty\Dev\`.

- **The design:** `v3_instrument_inputs\sensitivity_scoping\A6_design_v1.md`.
- **The readiness note behind it:** `v3_instrument_inputs\sensitivity_scoping\SENSITIVITY_READINESS_2026-09-29.md`.
- **The public pre-registration:** `AI-Succession-Problem\simulation\diagnostics\v3_rerun_design_note.md`, sections 4 to 11, and amendments A1, A4 and A5 in section 13.
- **The committed code (read-only),** under `AI-Succession-Problem\simulation\v3\`:
  - `study.py` (`table_jobs`, `scoring_for_rr`, `rerun_jobs`, `registered_spec`);
  - `calibration.py`, `context.py`, `tables.py` (`kernel_identity`), `integration.py`;
  - `offline_estimator.py`, `production_tables.py`, `table_validation_a4.py`, `continuation_validation.py`, `gates.py`.

Do not read any folder named `cert_*` other than your own output folder.

## Certify each item

For each item, give a verdict (certified, certified with named changes, or not certified), with reasoning.

1. **Completeness and fidelity.**
   - Does A6 close the three gaps it names?
   - Does it change anything section 6 registered: arms, grids, weights, horizon or seed counts?
   - Are its two explicit readings (crowding seeds, the σ0² narrowing) defensible and fixed without knowledge of any v3 outcome?
2. **The variant table families.**
   - Is each family's composition right: contexts, rules, the frozen sensitivity subset, and the kernel and calibration identity?
   - Is the σ0² re-derivation rule correct and complete against `calibration.py`: which calibrated values depend on σ0², and does "re-derived from the same calibration trajectories" determine them?
   - Does A4 apply cleanly to a variant family: M and M_FV per family, the census, and the floor?
3. **Seeds and independence,** of every new seed from every earlier seed, and between arms.
4. **The reading rule.**
   - Is the interval comparison sound? Consider the nominal estimate's own uncertainty, which the rule ignores.
   - Consider multiplicity: there are many arms and quantities, so some movements are expected by chance.
   - Is "moves" a fair operational meaning of W11's "moves materially"?
   - Is the consequence for claims proportionate?
   - Propose a concrete fix for anything unsound.
5. **Budget, machines and order.**
   - Is the planning estimate plausible from the readiness note?
   - Is the order consistent with the code identity freeze and the rerun pin (see A5's Sequencing)?
   - Is the failure rule for a variant family sound?
6. **Pre-registration integrity.** Does anything in A6 let a choice depend on R1 or R2 outcomes?
7. **Anything else** that would stop A6 from doing what it says.

## Hard limits

- **Scope:** read-only on everything except your output folder, which your launch message names.
- **No simulations.**
- **Blind:** do not seek survival, extinction or fire rates, rule rankings or outcomes.
- **Report:** write `certification_report.md` in your output folder, under 2,000 words: the verdicts, then the required changes ranked by severity. Plain American English, never em-dashes.
- **Final message:** under 150 words, with the overall verdict and the top three required changes.
