# Blind certification of the A5 design (plain-law labels for FV-route tables)

**Certifier:** independent Claude Code session, 2026-09-29. Blind to the other certifier.
**Verdict overall:** certified with named changes. No fatal defect found. The reused A4 plain-tier machinery is sound for FV rows under the plain law, and the label-only construction is internally consistent. The named changes are precision, disclosure and implementation requirements, not repairs to the mathematics.

I re-derived each item before comparing it with the design and with the committed code (`continuation_validation.py`, `table_validation_a4.py`, `continuation.py`, `offline_estimator.py`, `integration.py`).

---

## Item 1: Validity of the plain-law screen for FV-fitted tables

**Markov argument.** The residual is `r(x, x') = (1 - beta) f(x) + beta V(x') - C(cell(x))`. Given a source state x, `f(x)`, `C(cell(x))` are deterministic, and the one-step **advance** kernel to `x'` is the same map on both routes: A5 simulates the plain route, and even A4's FV trace uses the post-advance, pre-resampling next state (`TableTrace`, lines 76 to 80). So the conditional law of r given X = x is identical on the two routes. This is correct. What differs is only the within-cell distribution over source states x. Hence `theta_b^plain` and the FV-conditioned residual differ solely through that source-state weighting. The design's one-line statement is true but underspecified: it should say the shared object is the one-step advance kernel and the differing object is the state-visitation law. **Named change 4.**

**Living-source restriction.** A5 runs the plain route (`simulate(..., "plain")`), where a trace keeps recording after extinction (the defect A4 repaired). So the `source_alive` mask is genuinely needed here, not merely inherited, and it is applied correctly through the same code path. The claim that FV fits have living sources "by construction" is about the FV fitting law and is beside the point for A5's plain data; the restriction is required and correct. Certified.

**Meaning of the certificate.** A5 certifies that, under the plain law (living sources from the archived initial law, the table's fixed rule and kernel), each certified cell's per-trajectory mean residual against the A4 published value is within tau at 0.95 simultaneously. This is meaningful, and arguably closer to what the reruns need than the FV-fit law, because the reruns' allocations and A4's census both run plain dynamics. It does **not** certify the FV-conditioned residual (the cells the conditioned regime mainly reaches). The design states this in sections 2 and 7. Certified.

**Verdict: certified, with named framing change 4.**

## Item 2: The test

**Empirical Bernstein form.** `empirical_bernstein` uses `log_term = ln(4M/alpha)` and `rho = sqrt(2 V_n log_term / n) + 7 w log_term / (3(n-1))`. This is Maurer-Pontil two-sided (two one-sided bounds at `delta/2 = alpha/(2M)` each, so `ln(2/(alpha/(2M))) = ln(4M/alpha)`), with `V_n` the unbiased sample variance and `w` the range. Correct.

**Table-conditional width for FV rows.** For a covered transition out of cell b, `f in [lower, upper]`, `V(next) in {lower} union {published values} subset [lower, vmax]`, and `C(b)` is a published value. So `r in [lower - C(b), (1 - beta) upper + beta*vmax - C(b)]`, an interval of length `(1 - beta) W + beta (vmax - lower) = w_row`, independent of C(b). Any trajectory mean `m_i` of such residuals lies in that same interval, so `w_row` is a valid common range for every cell in the row. Empirical Bernstein needs only the range, not its location, so a single `w_row` per row is valid for all its cells. **vmax and lower do bound every `m_i`.** Certified. (For FV there is no C0, so vmax is simply the row's largest published FV value; `row_width` takes vmax as an argument and reuses cleanly.)

**Safeguard.** Certification requires the EB interval inside `[-tau, tau]` and `sum_S / sum_N` inside `[-tau, tau]`. Same as A4's plain tier, correctly applicable. Certified.

**Random number of trajectories (`N_i >= 1`).** The total trajectory count T is fixed and pre-registered (3 x 32 x runs_per_group). On the plain route the trajectories are mutually independent (no resampling couples them; groups are only batching). Selection `N_i >= 1` is a per-trajectory event, so conditional on the realized count `n = k` the selected `m_i` are i.i.d. from `P(m | N >= 1)`, which is exactly the estimand `theta_b^plain = E[m_i | N_i >= 1]`. Empirical Bernstein holds at each fixed k, and marginalizing over k preserves coverage: `P(fail) = sum_k P(n=k) P(fail | n=k) <= delta`. So the random n is valid, **provided T is fixed** (it is) and plain trajectories are treated as the independent units (they are). Certified.

**Verdict: certified.**

## Item 3: The family

**M fixed before the data.** M is the count of published FV cells in the sealed A4 publication, which exists before any A5 data and is generated from A4 seeds that are independent of A5's seeds. So M is a constant with respect to A5's test statistics. The A4 published FV set is exactly the set A5 tests, so the family equals the tested set. This is legitimate and tighter than P4's `M_FV = 797,225`. Certified, with two precisions:
- M must be counted **per row-cell** (matching `count_M_fv`, which sums published bins over rows), since a cell recurs across scoring rows and A5 tests each such unit.
- The design must state whether FV **sensitivity** rows (double_population, double_length) are tested. The compute line ("264 FV tables x 3 replicates") and "sensitivity jobs keep their doubled population" imply they are run, but the A4 published family is the primary rows only. If sensitivity cells are tested they must be counted in M; otherwise nothing tested may go uncounted. **Named change 3.**

**Separate family from A4's plain tier.** A5 is a third family (FV cells under the plain law), disjoint from A4's plain family and A4's FV asymptotic tier. A separate `alpha = 0.05` controlling A5's own family-wise error is sound.

**Anything tested but not counted?** A5 tests only published FV cells and counts exactly those. Cells never visited by plain trajectories become "unresolved" (n < 2) but remain in M, which only makes the union bound conservative. Safe.

**Verdict: certified with named change 3.**

## Item 4: Label-only soundness

**Reruns unchanged.** A5 writes a sealed label record bound by hash to the A4 publication; it never touches the frozen A4 family the reruns load through `lookup_available`. So reruns behave identically. Certified.

**Honesty of citing a plain-law certificate for FV rows.** Honest **only if** every certified cell's label always carries the full qualifier "certified under the plain law" and is never abbreviated to "certified," and if the residual gap (plain fixed-rule law vs the reruns' actual allocation policy, for which the census is the committed proxy) is disclosed exactly as A4 discloses it. Section 7 does this. Certified conditional on the qualifier never being dropped downstream.

**Violations.** This is the weakest point. A plain-law violation means the cell's published value is wrong beyond tau under the plain law at 0.95 confidence, yet because A5 is label-only the cell **stays in the active rerun support** and keeps being used, unlike A4 which unpublishes a violating plain cell. The false-violation rate is itself controlled (the two-sided EB interval gives per-cell `delta`, union-bounded to `alpha`), so a reported violation is a real finding, not noise. The design correctly makes it a finding, names cell/row/interval, discloses it wherever the row is used, and refers the decision to the operator. **The design must state this A4/A5 asymmetry explicitly and make the operator-decision path concrete**, so that a known-biased in-use cell is never buried under a mere label. **Named change 1 (most severe).**

**Verdict: certified with named change 1.**

## Item 5: Seeds and independence

A5 derives seeds as `SHA-256(v3_R_fvplain, A1 job seed, replicate)` truncated to 60 bits, a fresh tag distinct from A4's (`v3_R_fit`, `v3_R_validate`, `v3_R_census`) and from `planning_P4`. Because the tag enters the hash, streams are independent of the A4 FV validation data that fixed M, so there is no double use of data. The design lists the right exclusion set. **The implementation must forbid a superset of A4's current `assert_seeds_distinct`:** A4 forbids only A1, P1, P1-census, P3(0..3) and probe seeds. A5 must additionally forbid the full A4 stream set for the same tables (fit, validate replicates 1 to 3, FV validate replicate, census, for both routes), plus `planning_P4` and its own three replicates pairwise. The design's prose covers this; the code assertion must be extended accordingly. **Named change 2.**

**Verdict: certified with named change 2.**

## Item 6: The planning evidence (P4)

P4 (15 FV tables, 535 rows, 3 x 2,048 plain trajectories, fresh `planning_P4` seeds) supports the design's feasibility claims. It tests residuals against the table's own A1 values, which equal the A4 published FV values (A4 does not refit FV; `assemble_fv_row` reuses A1 values), so P4 and A5 test the same quantity. P4 used the **larger** family `M_FV = 797,225`, so its 52 percent certification rate is a conservative lower bound for A5, which uses the smaller A4-published M. This should be reconciled in a sentence; it does not weaken the design.

Caveats are adequately stated: non-registered, blind, 15 of 264 tables, plain-law not FV-law, and the thin floor margin (worst row 1.44 percent against a 2 percent cap). Crucially, A5 does **not** use a certified-only support, so the floor is informational only and the thin margin does not threaten A5, unlike a support-changing amendment. The design states this correctly. P4's "every plain-certified cell also passes A4's FV test" is reassuring but not load-bearing: A5 tests only A4-published cells by construction, so its certified set is inside A4's support regardless.

**Verdict: certified.**

## Item 7: Anything else

- **Coverage/estimand conditioning.** Transitions into unpublished (non-A4) cells are not covered, and the estimand is conditional on `N_i >= 1` and on coverage. This is inherited from A4 and listed under section 7's aggregation caveat; keep it visible.
- **Multi-family disclosure.** A5's 0.95 is a separate simultaneous statement from A4's plain and FV 0.95 statements. The three certificates do not compose to a joint 0.95. Worth one disclosing sentence. **Named change 5.**
- **runs_per_group mapping.** The plain `simulate` reads `settings["runs_per_group"]` (line 45); FV-route A1 jobs must carry that key for A5's plain run to execute. State the per-replicate count (2,048 = 32 x 64) explicitly, as P4 used. **Named change 6.**
- **A4 receipt binding.** A5 binds by hash to the frozen A4 publication and receipt; if A4 is re-published to a new path the binding must be re-pinned. Consistent with the frozen-target rule in `publish`.

---

## Required changes, ranked by severity

1. **Violation governance (medium).** State the A4/A5 asymmetry plainly: A4 unpublishes a violating plain cell; A5 leaves a violating FV cell in active rerun use and only labels it. Make the operator-decision path concrete and require prominent disclosure wherever a violated row is used, so a known-biased in-use cell is never masked by a label.
2. **Seed assertion superset (medium).** Require the A5 implementation to assert distinctness against the full A4 stream set (fit, all validate replicates, census, both routes) plus `planning_P4`, P1, P3, probe and A1, extending A4's narrower `assert_seeds_distinct`.
3. **Family counting precision (low-medium).** Specify M is read from the sealed A4 publication and counted per row-cell, and state whether FV sensitivity rows are tested; if tested, count them in M so nothing tested is uncounted. Reconcile with P4's larger `M_FV` (P4 is conservative).
4. **Markov framing (low).** Rephrase to: the one-step advance kernel is shared between routes; the within-cell state-visitation law differs; the certificate bounds the plain-visitation-weighted residual only.
5. **Multi-family disclosure (low).** Note the three 0.95 statements (A4 plain, A4 FV, A5) do not compose to a joint 0.95.
6. **Settings/trajectory count (low).** Confirm FV A1 settings carry `runs_per_group` and state the 2,048-per-replicate count explicitly.
