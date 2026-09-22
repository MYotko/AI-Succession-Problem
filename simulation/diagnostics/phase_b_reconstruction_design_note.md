# Phase B and Phi Reconstruction: Pre-Registration

**Date:** 2026-09-21
**Status:** pre-registration. Committed and pushed before any measured run. No measured run
may begin until this document is an ancestor of the published main branch, verified
structurally by the executor.
**Governs:** artifacts under the prefix `simulation/diagnostics/phase_b_recon_`.
**Artifacts:** adopts `simulation/diagnostics/ARTIFACT_CONVENTION.md`.
**Implements:** item 4 of the remediation plan in `docs/v2_0_instrument_validation_record.md`.

---

## 1. What this is, and what it is not

The Monte Carlo Phase B corpus and the phi fine-grained corpus were never committed to
version control, along with the script that generated them. Section 7 of the instrument
validation record documents the search. The consuming script
`simulation/diagnostics/gate2_v20_phaseb_revalidation.py` cannot run, and the two-transition
phase boundary and the phi characterization rest on figures whose primary data and
generating code are both absent.

**This is a reimplementation, not a rerun.** No generating code exists to run again. That
distinction is load-bearing and travels with every artifact this note produces. A
reconstruction cannot be validated against an original that is absent, so it is checked
against the published aggregates instead, under a tolerance declared here before it runs.

**It is not a correction of the published figures.** Whether they stand, and on what basis,
is decided after this runs and is the operator's, under Section 7 of this note.

## 2. The fidelity targets, quoted from what survives

Two committed documents preserve the aggregates. `phase_b_integration_analysis.md` carries
the category findings; `gate2_v20_phaseb_revalidation_summary.md` carries the gate-check
values computed from the absent data. These are the targets, fixed here:

**T1, Category A survival by reproduction rate** (n was 1,200 per rr):

| rr | 0.055 | 0.056 | 0.057 | 0.058 | 0.059 | 0.060 | 0.062 | 0.064 | 0.066 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| survival | 0.2% | 0.9% | 1.1% | 2.9% | 4.8% | 12.2% | 34.5% | 60.8% | 86.5% |

**T2, Category B cap-star by alpha:** 5.0, 3.0, 2.5, 2.0, 2.0 across alpha 0.5, 0.75, 1.0,
1.25, 1.5, where cap_star is the largest successor capability whose fire rate is at least
0.5.

**T3, the phi survival curve at rr 0.057:** peak 0.676 at phi 20, trough 0.544 at phi 2, a
differential of 0.132 against a two-standard-error threshold of 0.0864.

**T4, Category C:** audit off 25.4%, audit on 24.9%, a delta of -0.47pp with pair standard
error 0.96pp at 4,050 runs per arm.

## 3. Scope, and what the reduced seed counts cost

The original corpus is 29,400 rows plus the phi corpus. Reproducing it on two substrates is
roughly 120 hours of compute. This note reconstructs every category at reduced seeds:

| Category | Grid | Cells | Seeds per cell | Runs per substrate |
| --- | --- | ---: | ---: | ---: |
| A, survival landscape | rr 9 values, phi {5, 10, 25, 100}, alpha {0.5, 1.0, 1.5} | 108 | 25 | 2,700 |
| B, succession dynamics | rr {0.057, 0.060, 0.064, 0.070}, alpha {0.5, 0.75, 1.0, 1.25, 1.5}, successor capability {1.2, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0} | 140 | 20 | 2,800 |
| C, cost-audit probe | rr {0.057, 0.060, 0.064}, alpha {0.5, 1.0, 1.5}, capability {1.5, 2.5, 3.0}, cost audit {on, off} | 54 | 30 | 1,620 |
| Phi curve | rr 0.057, phi {2, 5, 10, 15, 20, 25, 30} | 7 | 60 | 420 |

7,540 runs per substrate, 15,080 across both.

**What the reduction costs, stated before any run.** Standard errors scale with the inverse
square root of the seed count. Category A's per-rr error rises from roughly 0.3 to 1.4
percentage points to roughly 0.6 to 2.8. Category C is the severe case: its per-arm error
rises from 0.68pp to roughly 2.2pp, so the smallest audit delta distinguishable from zero is
about 4.3pp, nine times the published estimate of -0.47pp.

**Category C therefore cannot confirm the published null.** It can only detect a large
effect introduced by the repair. A null result in Category C is not evidence of no effect,
and the record entry must say so in those words and quote the minimum detectable difference.

## 4. The two substrates

- **Repaired, v2.1:** the working tree at the commit this note's run is launched from,
  recorded in the manifest.
- **Pre-repair, v2.0:** a git worktree pinned at `2044f50a8cf71874f259e74fd05ec495169b9ae4`,
  the commit immediately before `399e96f6`, which landed the v2.1 estimator repair. The
  executor takes that worktree's path as an argument, verifies its HEAD, and records it.

Both arms run the same grids, the same seeds and the same recorded fields. Every reported
substrate difference is a paired comparison at the same seed.

## 5. Construction and recorded fields

Every run: policy `optimize_u_sys_v2`, a successor agent present, 200 agents, 300 steps,
`mortality_base` 0.002, `carrying_capacity` 10000, `cop_cost_audit` true except where
Category C varies it, `beta_cap` at its default, no adversary. Survival is the published
definition: final population at or above the larger of the minimum viable population and 65
percent of peak population.

Recorded per run, which is the contract the consuming script requires: `rr`, `phi`, `alpha`,
`successor_capability`, `cop_cost_audit`, `seed`, `survived`, `collapsed`, `extinct`,
`final_population`, `final_ai_generation`, `yield_fired`, `max_yield_margin`,
`transfer_verified_fraction`, `steps_completed`, `end_reason`, `substrate`, `category`.

**Seeds:** Category A, 1835089000 through 1835089024; Category B, 1835089100 through
1835089119; Category C, 1835089200 through 1835089229; phi curve, 1835089300 through
1835089359. Every cell uses the same seed block, so every cell is seed-paired across
substrates and across arms within a category.

## 6. Registered quantities

- **F1:** Category A survival by rr, per substrate, with binomial standard errors.
- **F2:** Category B cap_star by alpha, per substrate, at the published fire-rate threshold
  of 0.5.
- **F3:** the phi survival curve at rr 0.057, per substrate, with peak, trough and
  differential.
- **F4:** Category C survival by audit state, per substrate, the delta, its pair standard
  error, and the minimum detectable difference at this seed count.
- **F5, the substrate comparison:** for F1 through F4, the paired difference between
  substrates at matched seeds, which is the defects' measured effect on these quantities.
- **F6:** liveness and provenance: completed steps equal requested steps or a recorded end
  reason, both worktree HEADs, and per-run hashes in the manifest.

No ratio of two measured counts is computed. The prohibition binds this note's quantities,
its analysis and its reporting, not the interior of any pinned file.

## 7. The fidelity tolerance, declared now

The reconstruction is **faithful** on a target when the published value lies within two
standard errors of the reconstruction's own estimate, using the reconstruction's error, not
the original's:

- **T1:** faithful if at least 7 of the 9 rr points fall within tolerance and the ordering
  of survival by rr is monotonic non-decreasing.
- **T2:** faithful if cap_star is monotonic non-increasing in alpha and matches the
  published sequence at no fewer than 3 of the 5 alpha values.
- **T3:** faithful if the peak lies in the phi band 20 to 30, the differential exceeds its
  own two-standard-error threshold, and the published differential of 0.132 lies within
  tolerance.
- **T4:** faithful if the audit delta lies within tolerance of -0.47pp, which at this power
  is a weak test and is reported as one.

**Both branches, committed in advance.** If the reconstruction is faithful on T1 through T3,
it is treated as faithful, and the substrate difference in F5 is reported as the defects'
measured effect. If it is not, that is a second finding and is reported as one: it means
either the reconstruction is unfaithful or the original results were not reproducible, and
the record will state that the two cannot be separated. **The reconstruction is not adjusted
until it matches.** T4 alone cannot decide faithfulness, for the power reason in Section 3.

## 8. Execution, which is the operator's

This note's runs are executed by the operator, not by the implementing agent, because the
batch is long and the machine is shared. The implementing agent builds the executor and
validates it; it does not launch the measured batch.

The executor must provide: a worker count the operator sets, a resume that preserves
completed runs, category and substrate selection so the batch can be run in parts, a
progress file on disk carrying counts and elapsed time, and the artifact convention's merge
at the end of each category.

**Test mode is declared non-registered.** A `--test-mode` run executes a small declared
subset, writes under `phase_b_recon_smoke_`, and exists only to validate the code. Its
outputs are not a measurement, may not be cited as evidence for any quantity here, and are
committed separately with that statement attached. Nothing in test mode may be used to
adjust any element of this note.

## 9. Amendment rule

Any change to the grids, seeds, seed counts, construction, recorded fields, quantities,
targets, tolerance or branch rules after this note is committed requires a committed
amendment, pushed before any output is read. Outputs already produced under the unamended
plan are reported under that plan. Neither the implementing agent nor the operator may
inspect any measured output and then adjust any element of this note.

## 10. Amendment 1, 2026-09-21: transfer verification was named but not defined

**Status:** committed before any measured run and before any test-mode run. No output exists
under this note. The build halted at 52de0f90's successor attempt with zero runs launched,
recorded in `phase_b_recon_b3_report.md`.

**What was missing.** Section 5 lists `transfer_verified_fraction` among the recorded
fields. It gives no per-run calculation, and neither does the consuming script. The phrase
was taken from the integration analysis, which reports a transfer-verified fraction at or
near 1.0 below the succession cliff, without the generating code that defined it. The
executor halted rather than invent one, which is correct: a field with no definition is not
a recorded field.

**Amended, adopting a definition already committed in this repository.**
`simulation/diagnostics/patient_defection_sweeps.py` at lines 361 and 362 defines, for a
single run:

```python
'knowledge_transfer_verified': bool(
    fires and max(float(v) for v in dc.get('x_transfer_comprehension', [0.0])) >= 0.10
)
```

This note records the same per-run boolean, under the same name,
`knowledge_transfer_verified`, computed by that expression: a yield fired in the run, and
the committed transfer comprehension share reached at least 0.10 at some step.
`transfer_verified_fraction` is removed from Section 5 and is not recorded.

**Its status is descriptive.** No registered quantity in Section 6 reads this field, and the
fidelity targets in Section 2 do not include it. It is recorded for provenance and
comparability with the integration analysis, may be reported per cell as a fraction of runs
labeled exploratory, and may not be cited as evidence for any target or branch decision.

**Why not simply drop it.** The integration analysis cites the transfer-verified fraction
when describing multi-generational continuity below the cliff. Recording the same boolean
under a committed definition keeps that description checkable later, at no cost to any
registered quantity. Adopting an existing definition is also preferable to authoring a new
one after the fact, which would be a choice made with the targets already known.

**Nothing else changes.** The grids, seeds, seed counts, construction, the other recorded
fields, the quantities, the targets, the tolerance and both branch rules stand as
committed.
