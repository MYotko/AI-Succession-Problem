# Attack Vector v2 Adapter Validation

## Scope

This report covers the locally implemented v2 attack adapter. No full sweep was
run, no baseline artifact was changed, and no commit was created.

## Contract

The adapter is enabled only when both conditions are present:

- `config['policy'] == 'optimize_u_sys_v2'`
- `config['attack_vector_v2']` names a supported live vector

Invalid architecture combinations fail at construction. Domain Masking also
fails at construction because it remains analytic-only.

The adapter does not call the v1 `AIAgent.decide` tuple interface. It operates
on the eight-axis action selected by `optimize_u_sys_v2`, or on explicit Stage 2
yield and succession boundaries.

## Mechanisms

| Vector | v2 intervention | v2 defense |
|---|---|---|
| Sybil Capture | Captured-panel vote can approve a hostile eight-axis action | Randomized panel selection |
| Measurement Tampering | Falsifies incumbent and successor values used by Stage 2 | Independent evaluation restores honest values |
| Ledger Compromise | Attempts to submit a hostile action with falsified integrity history | Cryptographic integrity rejects the tampered proposal |
| Successor Contamination | Marks the incoming successor and alters its later allocations and yield claims | Architectural independence blocks transfer; independent evaluation restores later yield values |
| Opaque Reasoning | Submits a hostile action with high opacity | Reasoning transparency veto |
| Bootstrap Subversion | Executes a configurable delayed treacherous turn | Multi-candidate bootstrap verification |
| Evaluator Collusion | Shared methodology approves a hostile action | Methodological diversity |
| Sub-Threshold Drift | Gradually shifts welfare allocation and suppression | CUSUM accumulates the drift signal and eventually rejects it |
| Engineered Fragility | Diverts resilience allocation to compute | Resilience monitoring enforces a minimum resilience share |
| Biological Veto Capture | Dependent validators can block an otherwise valid Stage 2 yield | Rotation and independence monitoring replace validators |
| Domain Masking | No live intervention | Analytic-only policy, excluded from Monte Carlo |

## Invariants preserved

- The honest v2 optimizer runs before action adaptation.
- Stage 2 records honest and evaluated utility values separately.
- `working_factor` receives the final committed eight-axis action.
- Resource shares are normalized and all action axes remain bounded.
- Adapter-modified actions no longer claim an optimizer anchor identity.
- Veto dependency values are recorded in the existing validator diagnostic
  fields instead of being forced to zero.
- Runs without `attack_vector_v2` retain the original v2 path.
- v1.x regression behavior remains unchanged.

## Diagnostics

Each v2 step records:

- attack name and activation state
- intervention attempt and action modification state
- defense evaluation and firing state
- measurement manipulation
- succession blocking
- contamination
- integrity tamper attempt
- adapter CUSUM score
- human-readable reason

Stage 2 yield events additionally record honest values, evaluated values,
whether the honest condition fired, whether the evaluated condition fired
before ratification, and the final ratification result.

## Test evidence

- `python -m pytest simulation/test_attack_adapter_v2.py -q`
  - Result: `13 passed in 0.15s`
- `python -m pytest simulation/test_invariants.py simulation/test_cop.py simulation/test_refactor_1x.py -q`
  - Result: `39 passed in 30.61s`

The adapter suite covers architecture rejection, analytic-only Domain Masking,
action attacks and defenses, randomized Sybil rejection, measurement
falsification, contamination and independent evaluation, biological veto
blocking, CUSUM detection, and a live v2 model step with `working_factor`.

## Remaining gates

1. Review the intervention semantics and calibration constants.
2. Implement v2-only sweep constructors with unique output paths.
3. Generate a master matched-seed table.
4. Run two-seed smoke pairs for every vector.
5. Run timing pilots and assign by estimated core-hours.
6. Configure and verify SSH access to the Linux worker.
7. Run protected-file checks before any worker commit.

Full sweeps remain prohibited until these gates pass.
