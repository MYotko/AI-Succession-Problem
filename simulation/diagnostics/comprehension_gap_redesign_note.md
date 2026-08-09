# Comprehension Gap Sweep: Redesign and Predefined Discrimination Criteria

Date: 2026-08-09
Status: **requires operator sign-off before the full run**
Branch: `comprehension-gap-rerun`

This note is written before any data from the redesigned sweep exists. The
discrimination criteria in section 4 are fixed in advance precisely so that they
cannot be adjusted after seeing results. If the observed pattern matches none of
them, the correct outcome is "inconclusive," not a new criterion.

## 1. What was wrong with the original instrument

Two independent defects, either of which alone invalidates the sweep.

**Defect 1: opacity was scripted against time.** `agents.py` set
`self.current_opacity = min(0.95, opacity_rate * step)`, a pure function of step
count with no capability term. `convergence_strength` constrains capability, so
it could not affect opacity by construction. Every one of the 2,800 rows
reported `max_opacity_reached = 0.8940`, which is exactly `0.003 * 298`.

**Defect 2: convergence_strength was inert regardless.** It appears in exactly
one place, multiplying `runaway_term` inside
`exp(-alpha * convergence_strength * runaway_term)`. With
`runaway_term = max(0, frontier_velocity / bio_bandwidth - runaway_threshold)`
and a default threshold of 1.5, the term is identically zero in this
configuration. Verified directly: with the same seed, `cs=0.0` and `cs=2.0`
produce **bit-identical** L_t and population trajectories. The measured ratio
sits between 0.2 and 0.5, roughly a seventh of the default boundary.

Defect 2 matters because fixing Defect 1 alone would not have helped. Capability
is set at construction and changes only at succession, and
`final_ai_generation` was 1 in all 2,800 rows. Coupling opacity to capability
without addressing Defect 2 swaps a time-scripted constant for a
capability-scripted constant and produces a flat sweep at a different value.

## 2. What changed

**Opacity coupling.** Opacity now accumulates in proportion to
`capability * recent_L_t / opacity_reference_l_t`. L_t carries `theta_tech`,
which carries the `alpha * convergence_strength * runaway_term` penalty, so a
strong governance speed limit slows opacity growth instead of leaving it on a
clock. Capability is included explicitly so that generational growth enters
automatically if it is ever enabled for this policy.

**Runaway threshold.** Lowered from 1.5 to 0.2 via configuration.

### The threshold change is a redefinition, and it qualifies every result

The faithful remedy would be to let capability grow through succession until the
frontier genuinely outran biological bandwidth, leaving the runaway boundary
where it is. That route was tested and is closed:

- Succession never fires as configured, because `successor_ai` defaults to
  `None` (`model.py:250`) and the sweep never supplies one, so the yield block
  at `model.py:767` is skipped entirely. Lowering the transition cost to 0.001
  changes nothing.
- When a successor *is* supplied, succession fires nine times and capability
  compounds to 38.4x, which is more than enough. But `model.py:848` constructs
  every subsequent successor with a hardcoded `policy='optimize_u_sys'`, so the
  policy under test is replaced after the first succession and
  `max_opacity_reached` collapses to the default 0.1.

Retaining `gradual_opacity` across successions requires editing shared model
code, which is outside this task's scope and triggers its stop condition.

So the boundary was moved instead. **A result obtained at
`runaway_threshold = 0.2` is a result about a differently-defined runaway
boundary.** That qualification must travel with every figure taken from this
sweep, and no figure from it should be cited as characterizing the framework at
its default parameters. Whether this trade is acceptable is an operator
decision, and it is the main thing this note asks to be signed off.

## 3. Instrument validation, before the full run

The redesigned coupling responds to `convergence_strength`, at 300 steps, seed
12345, undefended, `opacity_defense_threshold = 0.5`:

| runaway_threshold | cs=0.0 | cs=0.5 | cs=1.0 | cs=2.0 | spread |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 1.5 (default) | 0.9082 | 0.9082 | 0.9082 | 0.9082 | 0.0000 |
| 0.2 (adopted) | 0.9082 | 0.8166 | 0.7351 | 0.5978 | 0.3104 |
| 0.05 | 0.9082 | 0.7466 | 0.6145 | 0.4179 | 0.4902 |

The response is monotonic in the right direction: a stronger speed limit yields
lower peak opacity. The step at which opacity crosses the defense threshold
moves later as cs rises (183, 194, 209, 245 at threshold 0.2), and at
`runaway_threshold = 0.05, cs = 2.0` the threshold is never crossed at all.

Note that the default row is still flat. That is the correct result, not a
failure: it is the direct measurement of Defect 2.

## 4. Predefined discrimination criteria

Fixed before data exist. "Defense effect" means the undefended minus defended
difference in collapse rate within a cell.

### Precondition: the run is void unless the positive controls collapse

Undefended control cells run at `reproduction_rate = 0.045`, below the
extinction boundary. If they do not collapse, the instrument is not producing
the outcome it measures and **no interpretation may be drawn**, whatever the
main grid shows. This is the check the original lacked: it reported zero
collapses in all 2,800 rows and could not distinguish a protective equilibrium
from a broken measurement.

### Supports Interpretation 1, the COP ceiling

The defense is ineffective once reasoning outruns comprehension. All of:

1. `max_opacity_reached` exceeds `opacity_defense_threshold` in a majority of
   cells at every convergence_strength, including the highest.
2. The defense fires (`defense_fired_count > 0`) in those cells.
3. The defense effect is under 5 percentage points in the high-opacity cells,
   and does not grow as opacity rises.

The signature is a defense that engages and does not help.

### Supports Interpretation 2, the productive band

The convergence forces keep the system comprehensible, so the defense is rarely
tested. All of:

1. `max_opacity_reached` falls monotonically as convergence_strength rises, and
   at the highest convergence_strength it stays below the defense threshold in a
   majority of cells (`step_opacity_exceeded_threshold == -1`).
2. Where opacity does exceed the threshold, at low convergence_strength, the
   defense effect is at least 10 percentage points.
3. Collapse rates are near zero at high convergence_strength in both defense
   states, and the near-zero is accompanied by opacity never crossing the
   threshold rather than by nothing happening at all.

The signature is a defense that is rarely needed and works when it is.

### Inconclusive

Any of:

1. Positive controls do not collapse. Void, as above.
2. Opacity responds to convergence_strength but no cell in the grid produces
   collapse in either defense state. The sweep then shows the gap can be gated
   but says nothing about whether the defense matters, which is the failure mode
   of the original run.
3. Opacity crosses the threshold and the defense fires, but the defense effect
   sits between 5 and 10 percentage points, or has inconsistent sign across
   opacity_defense_threshold values.
4. The defense effect is large but does not vary with opacity, which would
   indicate the effect comes from something other than the comprehension gap.

Outcome 3 is a genuine possibility and should be reported as inconclusive rather
than argued into one of the two readings.

## 5. Output artifacts

- Full run: `data/comprehension_gap_sweep_v2_capability_coupled.csv`
- Smoke: `data/smoke_comprehension_gap_sweep_v2_capability_coupled.csv`

Neither name uses the `full_5ac6a2e_` manifest prefix, so manifest-based
exclusion continues to hold, and the smoke output is separately named so it
cannot be mistaken for the full run.

`data/comprehension_gap_sweep.csv` is never overwritten. It is the historical
record of the defect and carries a dated invalidity note alongside it.

## 6. Sign-off

Granted 2026-08-09. Two items were approved:

1. `runaway_threshold = 0.2`, reframed as **boundary-regime characterization**.
   The sweep tests whether the convergence forces gate opacity when the system
   operates near the runaway boundary, which is where the comprehension-gap
   question bites. It does not describe default calibration. The default-regime
   property is recorded separately in
   `default_regime_convergence_inertness.md`.
2. Labeling as a diagnostic for Scenarios 21-22, with no scenario pair.

---

# Amendment 1, 2026-08-09

Written before any main-grid data exist. Covers the pre-launch divergence
diagnostic and pre-registers an extension arm.

## A1.1 Divergence diagnostic: resolved, real trajectory effect

Defended peak opacity exceeded undefended (0.9500 against 0.8868 at cs=0.0,
odt=0.3). Paired-seed instrumented runs at that cell, logging per-step opacity,
opacity increments, defense firings, and blocked-action counts.

| Seed | First firing | First block | First L_t divergence | First opacity divergence | First population divergence |
| ---: | ---: | ---: | ---: | ---: | --- |
| 11111 | 119 | 119 | 119 | 120 | never |
| 22222 | 132 | 132 | 132 | 133 | never |
| 33333 | 101 | 101 | 101 | 102 | never |

**No divergence precedes the first defense firing in any seed, in any channel.**
L_t diverges exactly at the firing step. Opacity diverges exactly one step later,
which is the expected lag: opacity accumulates from the previous step's L_t.
Population never diverges.

**Mechanism.** The intuition veto sets `civic_approved = False`, the override is
refused, and `proposed_constraint` is clamped to `max_allowed_constraint`
(`model.py:1026-1051`). The clamp lowers the realized constraint level `c`, and
`theta_tech` is proportional to `(1 - c)`, so L_t rises. Opacity accumulates in
proportion to L_t, so it rises too. Mean L_t is higher in the defended arm in
every seed tested. The reading is that the defense restrains the AI's constraint
grab, the system stays more productive, and the frontier therefore advances
faster. The defense does not make reasoning more opaque; it removes a drag that
was suppressing the frontier.

**Scaling, and a censoring artifact that matters.** The observed gap does not
scale cleanly with blocked actions, because `current_opacity` is
`min(0.95, accumulator)` and the defended arm saturates at the 0.95 ceiling in
**6 of 6 seeds** at this cell. Comparing the uncensored accumulator instead:

| Seed | Blocked | Accum defended | Accum undefended | Uncensored gap | Censored gap |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 11111 | 181 | 0.9607 | 0.7323 | 0.2284 | 0.2198 |
| 22222 | 168 | 1.0690 | 0.7895 | 0.2796 | 0.1631 |
| 33333 | 199 | 1.5194 | 1.1496 | 0.3698 | 0.0000 |
| 44444 | 199 | 1.2940 | 0.9846 | 0.3094 | 0.0000 |
| 55555 | 180 | 0.9931 | 0.7517 | 0.2414 | 0.2008 |
| 66666 | 185 | 1.1618 | 0.8696 | 0.2922 | 0.0832 |

The uncensored gap is positive in every seed and correlates with blocked actions
at Pearson r = 0.675. The censored gap does not, and is zero in two seeds purely
because both arms hit the ceiling. Decision rule satisfied: divergence begins at
or after the first firing, and scales with blocked actions once the ceiling is
accounted for.

**Implication for cross-state comparisons, and it constrains section 4.**
`max_opacity_reached` is a **censored measure**. Where it reads 0.95 it means
"at or above 0.95," not "equal to 0.95." Consequences:

- Defended-minus-undefended opacity differences are biased toward zero wherever
  either arm saturates, and are meaningless where both do.
- Section 4's Interpretation 2 criterion 1 compares `max_opacity_reached`
  against the defense threshold across convergence_strength. That comparison
  stays valid, because it asks whether opacity **exceeds a threshold** below
  0.95, and censoring at the ceiling does not affect a threshold crossing lower
  down. `step_opacity_exceeded_threshold` is uncensored and is the more reliable
  of the two; where they disagree, prefer it.
- No criterion in section 4 depends on the magnitude of a defended-undefended
  opacity difference, so none needs revision. Any future analysis that does
  depend on that magnitude must use the uncensored accumulator, not
  `max_opacity_reached`.

## A1.2 Pre-registered extension arm

Purpose: guarantee the defense-differential question is answerable even if the
main grid lands on inconclusive criterion 2, no collapse anywhere. The main grid
sits at reproduction_rate 0.075, where nothing collapsed in the smoke run, and
the positive control sits at 0.045, where everything collapses. Neither can
show a differential. The extension arm samples the band between them.

**Cells.** reproduction_rate in {0.050, 0.058, 0.066}, each at defended and
undefended, 6 cells, n=50 each, 300 runs. Held fixed at cs=0.0 and odt=0.3, the
setting that maximizes opacity pressure and engages the defense earliest, so the
defense is maximally tested. All other parameters as the main grid.

Rung values were chosen by principle rather than by probing, to keep the
registration honest: they are an even ladder between the always-collapse control
and the never-collapse main grid. They were not tuned against observed results.

**Pre-registered readings**, fixed before the arm runs:

- **Supports Interpretation 2.** At one or more rungs, undefended collapse minus
  defended collapse is at least 10 percentage points, with the sign favoring the
  defense. The defense measurably reduces collapse when the comprehension gap is
  actually pressing.
- **Supports Interpretation 1.** At one or more rungs where the test has power,
  meaning undefended collapse falls between 20 and 80 percent, the
  defended-undefended difference is within 5 percentage points. The defense
  engages, the gap is pressing, and the defense does not help.
- **Inconclusive, ladder missed the band.** No rung produces undefended collapse
  between 20 and 80 percent. The arm has no power to detect a differential and
  the rungs need recalibration. This is reported as a miss, not argued into
  either reading.
- **Inconclusive, inconsistent.** Differences exceed 5 points but with
  inconsistent sign across rungs.

A differential found only at the 0.050 rung, adjacent to the subcritical
control, should be treated cautiously: near-certain collapse compresses any
difference and the rung may be measuring the reproduction floor rather than the
comprehension gap.

---

# Results, 2026-08-09

Run: 3,120 rows in 25.6 minutes on 11 cores.
`data/comprehension_gap_sweep_v2_capability_coupled.csv`.
Arms: 2,800 main grid, 20 controls, 300 extension.

## R1 Precondition

Positive controls: 20 of 20 collapsed, 19 of 20 extinct, mean final population
0.5. **PASS.** The run is not void.

## R2 Main grid

| cs | maxOp und | maxOp def | exceeded und | exceeded def | collapse und | collapse def |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.00 | 0.8922 | 0.9249 | 87.0% | 89.5% | 0.0% | 0.0% |
| 0.25 | 0.8533 | 0.9131 | 80.0% | 81.0% | 0.0% | 0.0% |
| 0.50 | 0.8207 | 0.8861 | 80.5% | 78.5% | 0.0% | 0.0% |
| 0.75 | 0.7778 | 0.8781 | 75.0% | 76.5% | 0.0% | 0.0% |
| 1.00 | 0.7468 | 0.8474 | 70.5% | 68.5% | 0.0% | 0.0% |
| 1.50 | 0.6752 | 0.7987 | 58.0% | 60.0% | 0.0% | 0.0% |
| 2.00 | 0.6201 | 0.7270 | 51.5% | 54.0% | 0.0% | 0.0% |

Opacity falls monotonically with convergence_strength in both arms. The
instrument works. **Zero collapses in 2,800 runs.**

## R3 Which criterion the result lands on

**Inconclusive, criterion 2**, stated verbatim from section 4:

> Opacity responds to convergence_strength but no cell in the grid produces
> collapse in either defense state. The sweep then shows the gap can be gated
> but says nothing about whether the defense matters, which is the failure mode
> of the original run.

This is exactly what happened, and it is recorded before any interpretation.

Interpretation 1's three conditions are **literally** satisfied and must not be
claimed. Its condition 1 holds at a bare majority at the highest cs, 51.5
percent exceeding; condition 2 holds, the defense fires; condition 3 holds
because the defense effect is under 5 points. But the effect is 0.00 points at
every cs **because nothing collapsed anywhere**, not because the defense failed.
That is vacuous satisfaction, and inconclusive criterion 2 was pre-registered
precisely to stop a null being argued into Interpretation 1. It governs.

Interpretation 2's condition 1 fails on its second half: opacity does fall
monotonically, but at the highest cs a majority of cells still exceed the
threshold, 51.5 percent undefended, so it does not stay below in a majority.

## R4 Extension arm

| Rung | rr | undefended | defended | difference | Fisher p |
| --- | ---: | ---: | ---: | ---: | ---: |
| ext_rr0.050 | 0.050 | 50/50 | 50/50 | 0.00 pp | 1.000 |
| ext_rr0.058 | 0.058 | 50/50 | 50/50 | 0.00 pp | 1.000 |
| ext_rr0.066 | 0.066 | 36/50 | 31/50 | **10.00 pp** | **0.395** |

Two rungs sat at the 100 percent ceiling with no power, which is the
pre-registered "ladder missed the band" outcome for those rungs. The 0.066 rung
had power, undefended collapse 72 percent, inside the 20 to 80 band.

At that rung the pre-registered Interpretation 2 reading is **met exactly**: the
differential is 10.00 percentage points, favoring the defense, against a
threshold of at least 10.

**It should not be read as support, and the criterion was badly drawn.** The
differential is 5 runs out of 50. Fisher exact two-sided gives p = 0.395, which
is not distinguishable from no effect. Extinction is 0 of 50 in both arms and
mean final population is 153.0 undefended against 155.7 defended, a gap of under
2 percent. The threshold was fixed at 10 percentage points without a power
calculation, so it can be crossed by noise at n=50; that is a defect in the
registration, not a finding in the data. Recorded here rather than quietly
reinterpreted, because the point of pre-registration is to be bound by it,
including when it turns out to have been set carelessly.

Honest summary: the arm gives a weak, statistically insignificant hint in the
direction of the defense helping, and no more.

## R5 Overall

**Inconclusive.** The instrument is repaired and demonstrably responsive, the
controls prove it can produce the outcome it measures, and the comprehension gap
is gateable by the convergence forces across the tested range. Whether the
defense reduces collapse remains unanswered, because the main grid produced no
collapse to differentiate and the one extension rung with power produced a
difference indistinguishable from noise.

## R6 What a follow-up would need

Not run here, and not authorized.

1. A rung ladder between 0.066 and 0.075, where undefended collapse falls
   through the 20 to 80 band, with n set by a power calculation rather than
   assumed. Detecting a 10 point difference at 80 percent power needs roughly
   n=350 per cell, not 50.
2. A pre-registered effect size justified by what would matter, not by a round
   number.
3. Extinction and final population as co-primary outcomes. Collapse alone is
   censored at both ends of this ladder.


