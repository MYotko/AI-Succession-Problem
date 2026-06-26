# Patient Defection Verification

Generated: 2026-06-26

Disciplinary review of Codex's patient-defection implementation and findings before
integrating them into the v2.0 paper. This is verification, not revision: no Codex
deliverable, sweep artifact, or production code was modified. The independent checks
below read the defection module, the production hooks, and the raw sweep CSVs.

**Outcome: all four verifications pass.** The surprising findings (first succession
always fires; continuation suppression at generation 2; one narrow escape pocket) are
substantively grounded. One data-quality caveat is documented (a mislabeled diagnostic
column) that does not affect any substantive claim. Recommendation: proceed with the
Section VIII update.

## Verification 1: Substrate isolation (defection off is unchanged)

PASS at the code level. The production changes versus HEAD are minimal and inert when
defection is disabled:

- `agents.py`: candidate scoring changed from `rollout_sum += gamma**t * u_sys` to
  `score = adjusted_objective(u_sys, components, ai); rollout_sum += gamma**t * score`.
  `adjusted_objective` returns `honest + apply_defection(...)`, and `apply_defection`
  returns exactly `0.0` when `defection_weight <= 0` (early return). So with weight 0 the
  score equals honest U_sys bit for bit (`float(honest) + 0.0`).
- `model.py`: successor capability changed from `capability * 1.5` to
  `capability * config.get('successor_capability_growth_rate', 1.5)`. The default is 1.5,
  the original hardcoded value, so prior v2.0 results (Phase B, gates) are unaffected.
  `copy_defection_for_successor` is a no-op unless weight > 0 and inheritance is lineage.

Empirical support: 39/39 legacy tests pass on the modified code (they exercise the
disabled path and check U_sys invariants and succession). The defection module
(`simulation/defection.py`) is side-effect free and does not touch the honest U_sys
calculation.

## Verification 2: Defection operationalization

PASS. The optimizer scores candidates with the defection-weighted objective while the
yield evaluation uses honest U_sys, and both are logged:

- Scoring uses `adjusted_objective` (agents.py rollout loop).
- The yield path compares honest successor and incumbent U_sys (defection enters only the
  optimizer's choice, not the reported metric).
- The clean defection signal is `honest_reject_actual_would_fire_count`: cases where the
  honest advantage rejects succession but the defection-adjusted advantage would have
  fired. Independent recomputation by defection weight (Sweep 1, aggregated over targets):
  0.000 at weight 0.0, then 0.043, 0.100, 0.197, 0.333, and 0.700 at weight 2.0. The
  signal is exactly zero with defection off and rises monotonically with weight, which is
  the intended behavior.

Caveat (documented, does not affect claims): the column
`mean_actual_minus_honest_objective` is approximately -1.66 at all weights, including
weight 0. It compares `actual_objective_v2` against `u_sys_v2`, which are recorded at
different aggregation points, so it is a roughly constant offset rather than the per-step
defection bonus. It is mislabeled as a defection-magnitude metric and should not be cited.
Codex's analysis does not rely on it; the substantive operationalization evidence is
`honest_reject_actual_would_fire_count`, which verifies cleanly.

## Verification 3: Generation-2 cliff substance (the key check)

PASS, strongly. The continuation suppression at generation 2 is economic, not a
configuration artifact:

- Sweep 2 set `max_generations = 5` (headroom to reach generation 5), yet mean final
  generation is 2.00 at every defection weight and no run reached the generation cap
  (fraction at cap = 0.000). Lineages stop at generation 2 with four generations of
  headroom unused.
- Sweep 3 set `max_generations = 4`. Across the 15 (alpha, growth) cells, 14 stop at
  generation 2 and one reaches generation 3. Mean yield evaluations per run are about 498
  and roughly 95 to 98 percent of runs complete the full 500 steps. The model therefore
  evaluated second succession on essentially every step for the full horizon and rejected
  it economically; the cliff is not a generation cap or a step-truncation artifact.
- Mechanism: `max_active_capability_seen` is 2.0 in all blocked cells (3.0 only in the one
  escape cell). The runaway penalty acts as an absolute-capability ceiling: after the
  first succession brings the active lineage to capability about 2.0, a further jump pushes
  frontier velocity past the bandwidth the substrate can absorb, the runaway term
  suppresses the successor's technology-transfer contribution, and its honest U_sys falls
  below the incumbent's plus transition cost. This is the Pattern 1 runaway penalty
  (Section VIII.4) operating across generations, the same mechanism the gate work
  validated.

## Verification 4: Edge-case characterization (alpha=0.50, growth=1.5)

PASS. The single escape pocket is the corner where both the penalty is weakest and the
jump is smallest:

- alpha=0.50, growth=1.5: second-fire 0.10, max generation 3, max active capability 3.0.
- Neighbors blocked: alpha=0.50 with growth 2.0 and 2.5 stop at generation 2, capability
  2.0 (larger jumps exceed even the weak-penalty cliff); growth=1.5 at alpha 0.75 and
  above stop at generation 2, capability 2.0 (stronger penalty pulls the cliff inward).

Only at the weakest runaway penalty (alpha=0.50, cliff pushed outward) combined with the
smallest capability growth (1.5x, so the generation-3 successor reaches capability about
3.0 rather than 4.0 or 5.0) does the second successor occasionally stay below the cliff and
fire (10 percent of seeds). This is mechanistically consistent with the alpha-driven
Pattern 1 cliff, not an anomaly.

## Disposition

The findings are substantively grounded. The substrate's observed defense against this
patient-defection pattern is continuation suppression through the runaway penalty and
formal yield economics (Pattern 1 operating across generations), not first-yield detection
and not operational COP detection. The single data-quality caveat (the
`mean_actual_minus_honest_objective` column) does not affect any claim and should simply
not be cited. Proceeding with the Section VIII update is appropriate.

39/39 legacy tests pass. No production code, sweep artifact, or Codex deliverable was
modified by this verification.
