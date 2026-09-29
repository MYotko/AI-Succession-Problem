# Blind certification: the continuation validation design

## Your role

You are an independent certifier. You did not write this design. Another certifier, from a different model family, reviews the same design independently; neither of you will see the other's work. Your job is to find what is wrong, missing or unjustified. Do not assume the design is right. For every mathematical item, write your own derivation first, and only then compare it with the design's.

You are not the executor here. You do not implement or run anything. You judge.

## Read

All paths are under `C:\Users\matty\Dev\v3_instrument_inputs\`.

- **The design:** `validation_design\continuation_validation_design.md`.
- **Committed code (read-only),** under `a3_probe\_committed\simulation\v3\`:
  - `continuation.py`, the fit and the committed screen;
  - `offline_estimator.py`, `simulate` and `score_features`;
  - `production_tables.py`, `lookup`, which is how the registered engine uses C;
  - `unpublished_bins.py`, the census;
  - `engine.py` (`summary_bins`) and `policies.py` (the cuts).
- **Planning evidence (non-registered):** under `planning_study\`, `P1_findings.md`, `analysis_P3.md`, `run_p3.py` and `analyze_p3.py`.

Do not read any folder named `cert_*` other than your own output folder.

## Certify each item

For each item, give a verdict: **certified**, **certified with named changes**, or **not certified**. Then give your reasoning.

1. **Living-source restriction.**
   - Is it correct, given how the engine uses C?
   - Is C used anywhere at a non-living state?
   - Could excluding extinct sources bias the value for living states?
2. **The plain population-0 refit.**
   - Check the fixed-point formula, its existence and uniqueness, and the handling of extinct and unpublished next states.
   - Check the effect of the new C0 on neighboring cells, whose A1 values were fitted against the old population-0 values.
3. **Empirical Bernstein.**
   - State the exact form of Maurer and Pontil's bound for variables in [0, 1] (2009, "Empirical Bernstein Bounds and Sample Variance Penalization", Theorem 4), and its rescaling to width w.
   - Check the two-sided `ln(4M/alpha)` term.
   - Check validity when the number of units is random, selected by `N_i >= 1`.
4. **The a priori width `w_row`.**
   - Is it a valid bound on every `m_i`, given that the table is fixed before any validation data exist?
   - Look for gaps, for example flows at extinct transitions, values of cells never visited, or C0 outside the range.
5. **The estimand.** Compare `theta_b = E[m_i | N_i >= 1]` with the committed visit-weighted mean.
   - Is it an appropriate screen quantity, given how C enters the allocation?
   - What does certifying it guarantee, and what does it not guarantee?
6. **The global family.**
   - Check the union bound.
   - Is M fixed without looking at validation data?
   - Is anything tested but not counted?
7. **The FV asymptotic tier.**
   - Check the delta-method variance, the Student t critical value at `alpha/(2 M_FV)` and the n >= 16 rule.
   - Is the label "asymptotic, not certified" honest and sufficient?
   - Suggest any better small-sample practice within the same compute.
8. **Seeds and data independence** between the A1 fit, the refit replicate, the validation replicates and the census.
9. **The availability floor.** Check the census law, the 2% and 5% values, the 50-endpoint minimum and the halt rule.
10. **Anything else** that would stop the validation from supporting the reruns, including interactions with the registered engine and its gates.

## Hard limits

- **Scope:** read-only on everything except your own output folder, which your launch message names.
- **No simulations.** Small arithmetic checks with `python -c "..."` are fine, if each takes under a minute. No network.
- **Blind:** do not seek survival, extinction or fire rates, rule rankings, or registered outcomes.
- **Command form:** one command at a time, with no pipes, no chained commands, and no `$` or backticks inside `python -c`. Prefer your file-reading tools to shell commands. A refused command can end your run.
- **Report:** write `certification_report.md` in your output folder. Give the per-item verdicts with reasoning, then the required changes ranked by severity. Keep it under 2,500 words, in plain American English, and never use em-dashes.
- **Final message:** under 150 words. Give the overall verdict and the top three required changes.
