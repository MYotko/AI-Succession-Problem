# Amendment A5: design and certification records

These are the records behind amendment A5 (plain-law certification labels for Fleming-Viot tables), at the end of section 13 of `simulation/diagnostics/v3_rerun_design_note.md`. The operator approved the A5 design on 2026-09-29 (decision D31).

**Research (non-registered):** the operator asked whether the Fleming-Viot route relates to McKean-Vlasov dynamics.
- `research_fv_mckean_vlasov_brief.md`: a scoping brief by Gemini 3.1 Pro.
- `research_reviewer_assessment.md`: the reviewer's assessment of it. It confirms that a certificate under the conditioned law is not viable for the full model, and proposes the plain-trajectory design that became A5.

**Planning study (non-registered):**
- `planning_P4_findings.md`: plain-trajectory validation of 15 FV-route tables, run on fresh planning seeds. No figure from it enters any registered result.

**Design:**
- `design_v1_certified.md`: the design as it went to blind certification.
- `design_v2_approved.md`: the design after the accepted certification changes. This is the version the operator approved and A5 implements.

**Blind double certification:** two certifiers from different model families, Gemini 3.1 Pro and Claude, each worked from the same directive without seeing the other's work.
- `certification_directive.md`: the directive they were given.
- `certification_report_gemini.md` and `certification_report_claude.md`: their reports, verbatim.
- `certification_comparison.md`: the reviewer's comparison of the two. All seven named changes were accepted, each checked against the code.

None of these records reports a survival, extinction or fire rate, or a rule ranking.

Paths inside these records refer to the working folders where they were written, outside this repository.
