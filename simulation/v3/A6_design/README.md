# Amendment A6: design and certification records

These are the records behind amendment A6 (the W11 sensitivity and convergence runs, completed), at the end of section 13 of `simulation/diagnostics/v3_rerun_design_note.md`.
- **D32 (2026-09-29):** the operator chose option O2.
- **D33 (the same day):** the operator approved design version 2.

**Readiness:**
- `readiness_note.md` found that the registered sensitivity runs had no job builder.
- It also found that two of their arms needed table families of their own, and that no reading of their results was registered.
- It includes the planning pass, built from aggregate timings only, that costed the options.

**Design:**
- `design_v1_certified.md`: the design as it went to blind certification.
- `design_v2_approved.md`: the design after the accepted changes. This is the version the operator approved and A6 implements.

**Blind double certification:**
- **The certifiers:** two, from different model families, Gemini 3.1 Pro and Claude, each working from the same directive without seeing the other's work.
- `certification_directive.md`: the directive they were given.
- `certification_report_gemini.md` and `certification_report_claude.md`: their reports. Both failed version 1's reading rule.
  - **One change to the reports:** em-dashes were replaced with colons or commas, to follow the project's style. No word was changed.
- `certification_comparison.md`: the reviewer's comparison, with the disposition of every named change.

None of these records reports a survival, extinction or fire rate, or a rule ranking.

Paths inside these records refer to the working folders where they were written, outside this repository.
