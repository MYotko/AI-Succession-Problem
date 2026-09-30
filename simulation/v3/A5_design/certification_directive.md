# Blind certification: the A5 design (plain-law labels for FV-route tables)

## Your role

You are an independent certifier. You did not write this design. Another certifier, from a different model family, reviews it independently; neither of you sees the other's work. Find what is wrong, missing or unjustified. For each mathematical item, write your own derivation first, and only then compare it with the design's.

## Read

All paths are under `C:\Users\matty\Dev\`.

- **The design:** `v3_instrument_inputs\validation_design_A5\A5_design_v1.md`.
- **Amendment A4,** the context: the end of `v3_validation_repo\simulation\diagnostics\v3_rerun_design_note.md`.
- **The certified A4 design and its certification:** `v3_validation_repo\simulation\v3\A4_design\`.
- **The planning evidence:** `v3_instrument_inputs\planning_study\P4_findings.md`, `run_p4.py` and `analyze_p4.py`.
- **The committed code (read-only):** under `v3_validation_repo\simulation\v3\`, the files `offline_estimator.py` (`simulate`), `continuation.py`, `continuation_validation.py`, `table_validation_a4.py`, `production_tables.py` and `integration.py`.

Do not read any folder named `cert_*` other than your own output folder.

## Certify each item

For each item, give a verdict (certified, certified with named changes, or not certified), with reasoning.

1. **Validity of the plain-law screen for FV-fitted tables.**
   - Is the Markov-property argument right?
   - Is the living-source restriction correct for FV tables?
   - Does validating a table under a different law from its fitting law produce a meaningful certificate, and exactly what does that certificate say?
2. **The test.** Check:
   - the empirical Bernstein form;
   - the table-conditional width for FV rows, including whether vmax and lower bound every `m_i`;
   - the safeguard;
   - validity with a random number of trajectories selected by `N_i >= 1`.
3. **The family.**
   - Is M, the published FV cells of the A4 publication, fixed before the data?
   - Is a separate family from A4's plain tier sound?
   - Is anything tested but not counted?
4. **Label-only soundness.**
   - Does A5 really leave the reruns unchanged?
   - Is it honest to cite a plain-law certificate for results that use FV rows?
   - Are the handling of violations and their disclosure adequate?
5. **Seeds and independence** from the A1 fit, the A4 validation, the census and every planning seed.
6. **The planning evidence:** does P4 support the design's claims, and are its caveats stated?
7. **Anything else** that would stop A5 from supporting its statement, including interactions with the A4 publication and receipt.

## Hard limits

- **Scope:** read-only on everything except your output folder, which your launch message names.
- **No simulations.** Small arithmetic checks with `python -c` are fine only if they are plain single commands, with no pipes, no `$` and no backticks. Prefer your file tools.
- **Blind:** do not seek survival, extinction or fire rates, rule rankings or outcomes.
- **Report:** write `certification_report.md` in your output folder, under 2,000 words, with the verdicts, then the required changes ranked by severity. Plain American English, never em-dashes.
- **Final message:** under 150 words, giving the overall verdict and the top three required changes.
