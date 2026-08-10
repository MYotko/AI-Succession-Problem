# Application Record: Section VIII.10

Date: 2026-08-09
Branch: `section-viii-completion`
Source package: `VIII_10_draft.md`, repository root, untracked and not committed
Applied after the VIII.9 application, since Edit 2's target exists only then

## 1. Verification outcomes

All figures verified in Python against the primary result files.

### Check 1: figures against the powered-arm results and the pre-registration

| Figure | Claim | Verified value | Result |
| --- | --- | --- | --- |
| Rung 0.068 | 236.5 / 219.6 / -16.9 / [-37.2, +3.4] / 0.103 | exact match | PASS |
| Rung 0.070 | 332.8 / 331.9 / -0.9 / [-25.2, +23.3] / 0.941 | exact match | PASS |
| Rung 0.072 | table now reads p = 0.454 per amendment A2 | p = 0.454491 | PASS |
| Rung 0.074 | 655.0 / 658.1 / +3.1 / [-29.2, +35.3] / 0.853 | exact match | PASS |
| n per cell | 100 | 100 in all 8 cells | PASS |
| Main grid rows | 2,800 | 2,800 | PASS |
| Main grid collapses | none | 0 | PASS |
| Positive controls | 20 of 20 collapsed | 20 of 20 | PASS |
| Opacity undefended | 0.8922 to 0.6201 | exact match | PASS |
| Opacity defended | 0.9249 to 0.7270 | exact match | PASS |
| Exceedance at highest cs | "a bare majority" | 51.5 percent undefended | PASS |
| Censoring, defended arm at rr=0.074 | 76 percent per amendment A1 | 76/100 | PASS |
| Censoring, undefended arm at rr=0.074 | 18 percent per amendment A1 | 18/100 | PASS |

Source files: `data/comprehension_gap_powered_arm.csv`, 800 rows;
`data/comprehension_gap_sweep_v2_capability_coupled.csv`, 3,120 rows of which
2,800 main grid, 20 control, 300 extension.

### Check 2: the pre-registration provably predates the data

**PASS.** Evidence:

- Registration commit `4b31859`, 2026-08-09T19:14:04-04:00, "Pre-register the
  powered discriminating arm".
- Results commit `b2cba23`, 2026-08-09T19:25:00-04:00, eleven minutes later.
- `git merge-base --is-ancestor 4b31859 b2cba23` returns true.
- `comprehension_gap_powered_arm_note.md` exists at the registration commit.
- `data/comprehension_gap_powered_arm.csv` does **not** exist at the
  registration commit.

The subsection's assertion that the plan was committed before any data were
generated is therefore verifiable in the commit history exactly as stated.

### Check 3: the default-calibration dependency claim

**PASS.** `simulation/diagnostics/default_regime_convergence_inertness.md`
carries the cross-check section concluding "No, and none is expected to," and
cites `constitutional/CQ-01-bootstrap-defence-layer.md:81-82`, which reads
independently:

> **Gate 4** (runaway-regime validation): not currently applicable. No
> current substrate operates in the runaway regime where these equations

Both confirmed present. The Pattern 1 runaway-penalty cliff operates through
succession economics, a between-generation channel, so no published claim
depends on within-generation runaway pressure at default calibration.

### Check 4: mirror, checker, editorial

Reported in section 4 below.

## 2. Amendments applied before insertion

**A1.** Censoring sentence. Before: "the defended arm reaches that ceiling in up
to 47 percent of runs at the highest rung". After: "the defended arm reaches
that ceiling in 76 percent of runs at the highest rung (18 percent
undefended)". The 47 percent figure was the pooled rate across both arms, not
the defended arm. Corrected at source in Part C.

**A2.** Table VIII.10-1, rung 0.072, p now reads 0.454. The computed value is
0.454491. The previous 0.455 arose from double rounding, four decimals to three.

**A3.** The minimum-effect sentence was replaced so that it names both
co-primary outcomes, both minimum effects of interest, and states that n=100 was
sized against the binding of the two. The prior wording attributed the sizing to
the final-population effect alone, which was the non-binding one: the
two-proportion calculation required 97 per cell and the final-population
calculation required 88.

**A4.** Edit 2's bracket target exists only after Part A, so the parts were
applied in order within this branch.

## 3. Edits applied

- **Edit 1.** VIII.10 inserted after VIII.9, immediately before
  `## IX. Related Work`, in both assembled surfaces from a single source string.
  109 lines, byte-identical.
- **Edit 2.** The VIII.9 placeholder "[cross-reference pending: VIII.10 scope
  decision]" replaced with "Section VIII.10" in both surfaces. No bracket
  placeholder text remains anywhere in Section VIII.
- **Edit 3.** `docs/paper_v2_outline.md` gained a VIII.10 entry sourced to the
  redesign note, the powered-arm note including Amendment 1, the powered-arm
  results CSV, and the default-regime inertness note, by repository filename.
- **Edit 4.** The version-history entry appended to the end of the v1.x.2 to
  v2.0 section in `paper/appendix_C_draft.md` and at the mirrored location in
  the assembled document.
- **Edit 5.** One sentence added to the Section VIII limitations passage
  immediately after the Sub-Threshold Drift sentence, in both surfaces.

`paper/section_VIII_draft.md` received nothing, as specified.

## 4. Integrity

| Check | Result |
| --- | --- |
| Section VIII mirror byte-identity | **identical**, 676 lines each |
| VIII.9 subsection mirror | **identical**, 123 lines |
| VIII.10 subsection mirror | **identical**, 109 lines |
| COP pointer region mirror | **identical** |
| Em-dashes in added lines | **0** |
| Table pipes, VIII.9-1 | consistent 9-cell rows in both surfaces |
| Bracket placeholder anywhere in Section VIII | **none** |
| "sole citable source" in `paper/` or the assembled document | **none** |
| Scenario-numbering checker | reported on the consolidated branch check |

## 5. Anomalies

None beyond the three amendments above, all of which were operator-directed
before application rather than discovered during it.
