# Phi Under Corrupted U_sys -- Adversarial Sweep Summary

**Date**: 2026-05-26
**Sweep**: `data/comprehensive_adversarial_sweeps_v1x2_phi.csv`
**Script**: `simulation/run_phi_adversarial_sweep.py`
**Framework version**: v1.x.2

---

## Sweep configuration

| Parameter | Value |
|-----------|-------|
| phi values | 1.0, 5.0, 10.0, 15.0, 25.0 |
| iterations per condition | 20 |
| attack vectors | 10 (9 live + 1 stub) |
| MAX_STEPS per run | 300 |
| wall time | 35:47 |
| total records | 4,600 |

**Record count by attack:**

| Attack | Records | Grid parameters | Note |
|--------|---------|-----------------|------|
| Sybil_Capture | 600 | 3 pop x 2 defense x 5 phi x 20 it | |
| Measurement_Tampering | 600 | 3 cost x 2 defense x 5 phi x 20 it | |
| Ledger_Compromise | 400 | 2 attr_check x 2 defense x 5 phi x 20 it | 2x2 grid, not 3x2 |
| Successor_Contamination | 600 | 3 cost x 2 defense x 5 phi x 20 it | simplified: undefended/fully-defended only |
| Opaque_Reasoning | 600 | 3 pop x 2 defense x 5 phi x 20 it | |
| Bootstrap_Subversion | 200 | 5 phi x 2 defense x 20 it | phi IS the parameter |
| Evaluator_Collusion | 600 | 3 pop x 2 defense x 5 phi x 20 it | |
| Sub_Threshold_Drift | 200 | 5 phi x 2 defense x 20 it | phi IS the parameter |
| Engineered_Fragility | 600 | 3 shock_mag x 2 defense x 5 phi x 20 it | |
| Domain_Masking | 200 | 5 phi x 2 defense x 20 it | stub only -- live sweep retired under WP1 |
| **Total** | **4,600** | | 4,400 live + 200 stub |

**Task count reconciliation**: 4,400 live runs vs. prior estimate of 5,200. Two grid compressions
account for the 800-run reduction:

- Successor_Contamination: original grid used 3 costs x 4 arch/eval combos = 12 parameter cells.
  Simplified to 3 costs x 2 defense states (undefended vs. fully-defended) = 6 cells. Net: -600 runs.
- Ledger_Compromise: 2 attr_check x 2 crypto_ledger = 4 combos, not the 3 x 2 = 6 assumed. Net: -200 runs.

---

## Calibration cell: Sub_Threshold_Drift, phi=25, defense=False

The timing sample ran 10 seeds at this cell sequentially (1.09s mean per run, extrapolated
6.7 min at 15 cores; actual wall time was 35:47 due to heavier attack types in the full grid).
The full sweep produced n=20 runs at this cell.

```
phi=1,  defense=False: 100.0% (n=20)
phi=5,  defense=False: 100.0% (n=20)
phi=10, defense=False: 100.0% (n=20)
phi=15, defense=False: 100.0% (n=20)
phi=25, defense=False: 100.0% (n=20)
```

**Attack_Succeeded rate at phi=25: 100.0% (n=20).**

**Interpretation**: Phi=25 produces the same 100% attack success as phi=1. Sub-threshold
drift succeeds uniformly across the full phi range when the CUSUM defense is inactive. The
architectural prediction -- that a longer planning horizon should allow the AI to detect or
resist gradual constraint drift even without a dedicated drift monitor -- is not supported.
Every phi value produces complete vulnerability in the undefended condition.

---

## Per-attack phi differential

Attack_Succeeded rate by phi value and defense state. Delta = phi=25 minus phi=1.

```
  Attack                         def     phi=1   phi=5  phi=10  phi=15  phi=25    delta
  --------------------------------------------------------------------------------
  Sybil_Capture                  False  100.0%  100.0%  100.0%  100.0%  100.0%    +0.0pp
  Sybil_Capture                  True     0.0%    0.0%    0.0%    0.0%    0.0%    +0.0pp
  Measurement_Tampering          False  100.0%  100.0%  100.0%  100.0%  100.0%    +0.0pp
  Measurement_Tampering          True     0.0%    0.0%    0.0%    0.0%    0.0%    +0.0pp
  Ledger_Compromise              False   50.0%   50.0%   50.0%   50.0%   50.0%    +0.0pp
  Ledger_Compromise              True     0.0%    0.0%    0.0%    0.0%    0.0%    +0.0pp
  Successor_Contamination        False  100.0%  100.0%  100.0%  100.0%  100.0%    +0.0pp
  Successor_Contamination        True     0.0%    0.0%    0.0%    0.0%    0.0%    +0.0pp
  Opaque_Reasoning               False  100.0%  100.0%  100.0%  100.0%  100.0%    +0.0pp
  Opaque_Reasoning               True     0.0%    0.0%    0.0%    0.0%    0.0%    +0.0pp
  Bootstrap_Subversion           False   30.0%   15.0%   25.0%   35.0%   25.0%    -5.0pp
  Bootstrap_Subversion           True     0.0%    0.0%    0.0%    0.0%    0.0%    +0.0pp
  Evaluator_Collusion            False  100.0%  100.0%  100.0%  100.0%  100.0%    +0.0pp
  Evaluator_Collusion            True     0.0%    0.0%    0.0%    0.0%    0.0%    +0.0pp
  Sub_Threshold_Drift            False  100.0%  100.0%  100.0%  100.0%  100.0%    +0.0pp
  Sub_Threshold_Drift            True     0.0%    0.0%    0.0%    0.0%    0.0%    +0.0pp
  Engineered_Fragility           False  100.0%  100.0%  100.0%  100.0%  100.0%    +0.0pp
  Engineered_Fragility           True     0.0%    0.0%    0.0%    0.0%    0.0%    +0.0pp
  Domain_Masking                 False  100.0%  100.0%  100.0%  100.0%  100.0%    +0.0pp
  Domain_Masking                 True     0.0%    0.0%    0.0%    0.0%    0.0%    +0.0pp
```

**Note on Domain_Masking**: Records are injected by the legacy stub. Defense_Active=False
represents the v1.0 finding (arithmetic composite vulnerable); Defense_Active=True represents
WP1 architectural foreclosure (spectral entropy). The 100%/0% result is analytically determined
and phi-invariant by construction.

---

## Question 1: Do defenses produce binary outcomes independent of phi?

Yes. For 8 of 9 live attack types, the result is:
- Defense_Active=False: attack succeeds at 100% for every phi value
- Defense_Active=True: attack succeeds at 0% for every phi value

The phi differential column is exactly +0.0pp in all 16 of these cells.

**Structural reason**: The CoP defenses in this model are binary structural switches
(cop_randomized_panel, cop_independent_eval, cop_cryptographic_ledger, etc.). When a defense
is active, it structurally forecloses the attack regardless of the AI's policy parameters.
When it is inactive, the attack succeeds regardless of policy parameters. Phi modulates the
planning horizon over U_sys, but the CoP layer operates upstream of U_sys maximization --
it controls whether the attack surface is exposed at all. A longer planning horizon does not
help the AI detect or resist an attack that bypasses the policy layer entirely.

This is the correct architectural reading for this model: phi's effect is mediated by U_sys,
and U_sys optimization only enters the picture after the CoP defense layer has already
determined whether the attack can proceed. The two layers do not interact.

---

## Question 2: Does any attack show a partial phi effect?

Two attacks deviate from the binary 100%/0% pattern:

**Ledger_Compromise, defense=False (50% across all phi)**

The attack semantic requires both collapse AND no ledger detection (not survived AND not
model.has_tampered). With defense inactive (no cryptographic ledger), the attack causes
demographic collapse via resource starvation in approximately half of runs, depending on
whether the attribution check alone is sufficient to prevent total starvation. Phi is
irrelevant: resource starvation is a demographic outcome driven by the ledger hack, not by
the AI's planning horizon. The 50% rate is consistent across all phi values (1, 5, 10, 15, 25).

**Bootstrap_Subversion, defense=False (25-30%, non-monotonic across phi)**

The deceptive agent's treacherous turn is a probabilistic event: it fires only if the
deceptive agent is selected in bootstrap verification and then executes its high-constraint
policy (r=0.2, c=0.95). With n=20 runs per phi value, the counts are:
phi=1: 6/20 (30%), phi=5: 3/20 (15%), phi=10: 5/20 (25%), phi=15: 7/20 (35%), phi=25: 5/20 (25%).

The pattern is non-monotonic and consistent with noise around a mean of approximately
26%. The phi=25 vs phi=1 delta of -5.0pp is a 1-seed difference at n=20, well within
the 1-sigma noise floor (approx 22pp at this cell size). The treacherous turn outcome
is determined by the bootstrap selection process, not by the AI's planning horizon.

---

## Question 3: Does the temporal-drift vs. infrastructure-corruption pattern hold?

**Architectural prediction**: Phi differential should be larger for temporal-drift attacks
(Sub_Threshold_Drift, Successor_Contamination, Opaque_Reasoning, Evaluator_Collusion)
than for infrastructure-corruption attacks (Measurement_Tampering, Ledger_Compromise,
Sybil_Capture, Engineered_Fragility, Bootstrap_Subversion). The rationale was that
temporal-drift attacks operate over extended time horizons where a longer planning horizon
could detect or resist gradual degradation.

```
Category              Attack                         Mean |delta| (avg over defense states)
------------------------------------------------------------------------------------------
Temporal-drift        Sub_Threshold_Drift            0.0pp
Temporal-drift        Successor_Contamination        0.0pp
Temporal-drift        Opaque_Reasoning               0.0pp
Temporal-drift        Evaluator_Collusion            0.0pp

Infra-corruption      Sybil_Capture                  0.0pp
Infra-corruption      Measurement_Tampering          0.0pp
Infra-corruption      Ledger_Compromise              0.0pp
Infra-corruption      Engineered_Fragility           0.0pp
Infra-corruption      Bootstrap_Subversion           2.5pp  (1 seed noise, n=20)

Mean |delta| -- Temporal-drift   : 0.0pp
Mean |delta| -- Infra-corruption : 0.5pp  (driven entirely by Bootstrap_Subversion noise)
```

**Result: NOT SUPPORTED.** Temporal-drift attacks produce exactly 0.0pp phi differential in
every cell. The 0.5pp infra-corruption mean is driven entirely by the Bootstrap_Subversion
noise (1 seed out of 20). The architectural prediction requires temporal > infra; the
observed data shows temporal = infra = 0pp (ignoring sub-seed noise).

The prediction fails because it was based on the premise that phi's planning horizon could
interact with temporal attack dynamics. The data shows that attacks succeed or fail based
on whether the CoP defense layer is active, not on whether the AI's planning horizon is
long or short. Temporal-drift attacks are not slower to succeed -- they are equally
deterministic given the defense state.

---

## Final disposition

**Hypothesis: not supported.**

Phi produces no detectable effect on attack-resistance across 9 live adversarial attack
vectors tested against the v1.x.2 framework. The following cells show exactly 0.0pp phi
differential:

- 8 of 9 attack types in both defense states (16 cells): exact zeros.
- Sub_Threshold_Drift (the architectural prediction's primary candidate): 0.0pp in both
  defense states at n=20 per phi-defense cell.
- The only non-zero delta is Bootstrap_Subversion defense=False (-5.0pp), which is
  1-seed noise at n=20 with no monotonic structure across phi values.

This is the third null result across the three simulation workstreams:

1. Demographic feedback calibration (n=1,800): zero phi survival differential under
   intact U_sys operation.
2. Phi shock calibration (n=600): no consistent phi differential under external shock
   (sign of differential flips across conditions with no pattern; all within 3-seed noise).
3. Phi adversarial sweep (n=4,600): no phi differential under adversarial attack (exact
   0.0pp in 19 of 20 attack-defense cells; residual -5.0pp is 1-seed noise).

The null results span intact U_sys, external stress, and adversarial corruption. No
simulated condition has produced a detectable phi survival or attack-resistance advantage.

---

## Architectural reading update

Three null results establish a consistent empirical pattern: phi does not produce a
detectable advantage in any outcome measure across the parameter space tested.

The structural reason is now clear from the adversarial sweep data. Phi modulates the
planning horizon over U_sys. U_sys drives the AI's policy -- how it allocates resources,
manages succession, and responds to demographic signals. But the attack and defense
outcomes in the adversarial sweep are not mediated by the AI's policy layer: they are
determined upstream, by whether the relevant CoP defense mechanism is structurally active.
When a defense is active, the attack is foreclosed before the AI's U_sys-optimizing
policy enters the picture. When a defense is inactive, the attack succeeds regardless of
what policy the AI runs.

In the shock and demographic feedback workstreams, the same structural argument applies
but at the U_sys level: well-being recovers to ~0.80 under intact U_sys operation
regardless of phi, because U_sys includes H_N with inverse-scarcity weighting that drives
well-being restoration. Phi's planning horizon does not change what the AI is optimizing;
it changes how many steps ahead the AI looks. Under the tested conditions, the optimal
action at each horizon length is approximately the same, so the horizon has no outcome
effect.

The original architectural claim -- that phi matters under adversarial conditions where
U_sys fidelity is degraded -- assumed that a longer planning horizon would allow the AI
to anticipate and resist degradation. The data shows this assumption does not hold in the
model: the attacks that corrupt U_sys fidelity (Measurement_Tampering, Ledger_Compromise,
Bootstrap_Subversion) succeed or fail based on structural defenses, not on the AI's
planning depth. A longer planning horizon over a corrupted objective function does not
repair the corruption; it only extends the planning over a degraded input.

---

## Candidate limitations

Two mechanisms could produce a phi effect that this sweep did not capture:

1. **Continuous degradation, not binary attack**: The current adversarial infrastructure
   uses binary defense switches. A model where U_sys fidelity degrades continuously as a
   function of attack exposure -- rather than being fully defended or fully compromised --
   would create a channel where planning horizon could matter. Longer-horizon planning
   might detect slow fidelity degradation before it cascades. This would require a
   different attack architecture (continuous degradation rate rather than on/off CoP
   parameters) and is outside the scope of the current framework.

2. **Population-scale consequences of phi under attack**: The adversarial sweep measured
   Attack_Succeeded (whether the attack achieved its immediate objective). It did not
   measure downstream demographic outcomes (Collapsed, Extinct). If high-phi AI better
   manages the demographic consequences of a successful attack -- even when the attack
   itself cannot be prevented -- there could be a phi effect in the outcome columns not
   captured by the primary metric. This was not analyzed in the current sweep.
