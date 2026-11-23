# Addendum 7 to the stage 2 reader specification (2026-11-22)

**Applies to** the draft (`3ac0f425…5822`) as amended by Addenda 1 to 6 (Addendum 6 at version 5, `6d6ea4a3…ec13`). Where it differs from them, it governs.

**Source:** the interpreter's decisions on the second check of fixture stage G1, `fixtures\g1_check\REPORT.md`, verdict SOUND. Each change below is a G2 requirement, numbered A7.n after that report's section 2.n. Its facts are the check's measurements and readings, which the interpreter has not repeated. They are labelled so where they matter.

## A7.1 Negative fixtures for A6.1's refusal (new; amends F17)

**The gap.** All eight F17 lists satisfy D:455's preconditions. No fixture exercises the refusal the operator chose in A6.1, so a precondition check that never fires would pass every fixture in both builds. The second check found this.

**The rule.** G2 adds negative lists to F17, one per precondition of D:455:
- **F17-N1:** an `allocation_evaluated` or `survival_first` value that is not a bool;
- **F17-N2:** two yield events at the same time;
- **F17-N3:** a yield event at a time that is not a multiple of ten;
- **F17-N4:** a yield event at an absorbed step;
- **F17-N5:** ordinary plus survival-first not equal to `allocation_steps`.

Each states its expected outcome: refusal at `input_verification` with the label `incidence denominators not derivable`.

G2 also adds one L2 case, **F10b**: a case 2 output with one broken precondition. Its record and hash file are re-bound by F10's method, so that every hash gate passes. It must refuse with the same label and phase.

## A7.2 F17's extinction lists in native shape (amends F17)

- **The gap.** The native model records `population: 0` on the last evaluated step of an extinct run, because `integration.py:422` writes the population after `advance`. F17-B and F17-F hold a positive population there. So a reader that takes "evaluated" to mean `population > 0` reproduces all eight F17 triples. On G1's native runs that reader is wrong on 4 of 95 case 1 runs. These are the second check's measurements.
- **The rule.** G2 sets `population` to 0 on the last evaluated step of F17-B and F17-F, and recomputes their expected denominators. After the change, the population-based mis-derivation fails F17-B on survival-first and F17-F on ordinary.

## A7.3 The A16 family's copied values made distinct (amends A5.3 and F13(e))

- **The gap.** The A16 round 1 admission record holds `cap` 2, `residual_count` 2 and 2 admitted rows. A build that swaps those keys on its A16 path passes F13(e).
- **The rule.** G2 rebuilds the A16-scope family with three residual rows certified and one at `N* not reached`. That gives `residual_count` 1 against `cap` 2, with `E` 4 and `tests_round1` 3. The rows that would need native eligibility carry the native-eligible floor triple (A7.7).
- **The residuals, stated:**
  - `E2: null` and `tests_round2: 0` are the native round 1 values (`validation_extension_a16.py:1005`, `:1344`, as the check read them). They are distinct from every other copied value, and are acceptable.
  - `E` equals the original refusal's `residual_count` (both 4). That cannot be avoided without an ineligible residual row, which would raise the final count again. It is stated, not fixed.
- **A second variant** keeps the "tested and unresolved" admitted row of G1's family, under its own name, so that both admission shapes stay covered.

## A7.4 F14(d) isolates the plan-hash check (amends A1.3's F14(d))

- **The gap.** Replacing `plan_hash` in the round's admission record also changes `admission_identity()` and the file sha256. So a reader with no plan-hash comparison still refuses, on an identity binding.
- **The rule.** G2 rebuilds the chain around the altered record, so that only the comparison `record.plan_hash == manifest.a13_admission.a16.plan_hash` fails. The chain is the new binding, table, receipt and identity record. The fixture manifest states that every other binding holds. If the native writers cannot produce that chain in a fixture root, G2 writes it by hand as a named fabrication and says so.

## A7.5 Material for A6.4a's L1 fallback (amends A6.4a's last bullet)

**The finding.** The check's indicative screen found neither an undefined point boundary nor an infinite interval end at fixture scale, and no native result in F1 to F5 holds a NaN.

**The rule:**
- G2 screens its full L2 layout with the native helper first, and reports what it found.
- `L1_ARRAYS.json` gains a fixed ladder test key: 32 bytes, stated in hex in the file.
- It also gains, as a third reference, the rung values for F3 and F5 under that key, computed by G2's own serializer from A6.4a's text.
- Each builder's rung code must reproduce them.
- One added array, **F5-N**, must produce a NaN in a helper result, if the native helpers can produce one. If they cannot, G2 says so, and the `"nan"` mapping stays untested, as a stated residual.

## A7.6 The nominal A14 record's `tests_round1` (amends A5.3's example)

`tests_round1` changes from 19 to 18, because 19 equals the nominal `cap`. The values become `E` 20, `E2` 17, `tests_round1` 18, `tests_round2` 13. `P` and `M` stay native, and are distinct.

## A7.7 Smaller items for G2

- **A16 family rows.** Rows that native `eligible()` must accept carry the native-eligible floor triple: `living_ok` true, `low_assessed` true, `low_ok` false (`validation_extension_a13.py:96`). G1's rows had the reverse. No reader reads `a4.floor` (A5.5), so nothing passed or failed wrongly.
- **Sidecar tests on plain rows.** These follow `plain_cell_codes` (`continuation_validation.py:121-128`), which merges population-category-0 bins into one `POP0_CELL` test, as native rows do. G1 used the fine codes unmerged. The sidecar is bound by hash only, so no reader effect follows.
- **F6 reuse.** G1's crowding case 1 table already holds two condition (d) runs: rr 0.066 at seed index 0, and R2 0.064, alpha 0.5, capability 1.2 at seed index 0. The comparator at rr 0.059 holds both condition (a) runs. This holds only while the table bytes are G1's. G2 reuses G1's archived crowding table bytes, rather than rebuilding them, so that those runs stay valid.
- **For the record:**
  - G1's report misnamed the function that merges category-0 bins: it is `plain_cell_codes`, not `cv.fine_codes`.
  - The multiples of 25 in the ordinary count are an observation, 100 of 100 runs, not a guarantee, because the certificate is re-evaluated every step (`integration.py:230-234`).
  - The deadline exit of `review_yield` (`:284-287`) is unreachable through `step()`, since periods reopen at each protection end and time advances by one per step. F17 covers it at L1 only.
