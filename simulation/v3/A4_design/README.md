# Amendment A4: design and certification records

These are the records behind amendment A4 (validated continuation support), in section 13 of `simulation/diagnostics/v3_rerun_design_note.md`. The operator approved A4 on 2026-09-29 (decision D30).

**Design:**
- `design_v1_certified.md`: the design as it went to blind certification.
- `design_v2_approved.md`: the design after the accepted certification changes. This is the version the operator approved and A4 implements.

**Blind double certification:** two certifiers from different model families, Gemini 3.1 Pro and Claude, each worked from the same directive without seeing the other's work.
- `certification_directive.md`: the directive they were given.
- `certification_report_gemini.md` and `certification_report_claude.md`: their reports, verbatim.
- `certification_comparison.md`: the reviewer's comparison of the two, with the changes accepted and the two recommendations rejected, each with the reason.

**Planning studies (non-registered):**
- `planning_P1_findings.md`
- `planning_P3_analysis.md`

They were run on fresh planning seeds, and no figure from them enters any registered result. They report no survival, extinction or fire rate, and no rule ranking. `planning_P1_findings.md` carries a dated correction of the reviewer's own error in the range of the certified bounds.

Paths inside these records refer to the working folders where they were written, outside this repository.
