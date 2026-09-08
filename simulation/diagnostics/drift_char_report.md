# V2.1 drift repair: pre-implementation characterization

This is current-substrate characterization and constant measurement before implementation. It is not registered characterization data, is not framework evidence, and does not implement the repair. No calibration anchor or alarm constant is selected.

Status: complete. T0 passed; 40 honest-baseline runs and one defended reproduction trajectory completed. T2 and T3 reuse the recorded T0 trajectory.

## Fixed design decisions, verbatim context

```text
  D1, suppression semantics. The novelty entropy estimator will be made
  magnitude-sensitive:
      H_N = spectral_shape * magnitude_factor
      spectral_shape   = the current normalized spectral entropy, unchanged, so
                         dimensional-masking resistance is preserved exactly
      magnitude_factor = 1 - exp(-3.0 * V / V_ref)
      V                = total novelty variance = trace of the covariance of the
                         per-step novelty matrix = sum of the raw covariance
                         eigenvalues BEFORE the normalization step
      V_ref            = a fixed calibration constant, measured on the honest
                         baseline, frozen and published before any characterization
                         run consumes it
  The saturation constant 3.0 is the inherited house value, not a free parameter.

  D2, attack-success definition. Dual quantity per vector: keep the action-change
  binary as the comparable metric, and add an outcome differential against a
  seed-paired honest arm as the substantive metric. General rule to record: prefer
  counts and paired differences over ratios, because a ratio invites an endogenous
  denominator and an unpaired ratio hides a floor. Worked example already banked:
  the veto vector uses per-run block COUNT, paired, not a per-vote rate.

  D3, detector observable. A one-sided lower CUSUM on the protected observable
  (novelty entropy under the D1 repair):
      S_t = max(0, S_{t-1} + k * H_ref - H_N_t)
  with the committed suppression posture as a fast, exact, zero-lag corroborating
  channel. H_ref anchored to the fixed honest-baseline calibration, NEVER to running
  history. A periodic independent recomputation of the optimal policy re-anchors
  H_ref (this is the architecture's "periodic full reset verification"). Reset on
  alarm so the score cannot latch. A liveness signature distinct from the alarm
  signature. The alarm threshold D_alarm is placed BELOW the structural defection
  threshold d_defect by the loop response time at the worst-case approach rate, and
  the margin is stated as a number. No M-out-of-N counter.
```

## Preconditions and evidence selection

- Gate 1: PASS. {"branch": "main", "head": "f1ae659f92834f36971c2a6c320186788ece9525", "merge_base_exit": 0, "number": 1, "passed": true}
- Gate 2: PASS. {"advisor_present": true, "git_ls_files_exit": 1, "number": 2, "passed": true}
- Gate 3: PASS. {"definition_lines": {"ALPHA_DEFAULT": 59, "CONVERGENCE_STRENGTH": 64, "FRONTIER_FLOOR": 47, "RUNAWAY_THRESHOLD": 52}, "number": 3, "passed": true, "read_values": {"ALPHA_DEFAULT": 1.0, "CONVERGENCE_STRENGTH": 1.0, "FRONTIER_FLOOR": 0.02, "RUNAWAY_THRESHOLD": 1.5}}

Read authoritative manifest: `simulation/diagnostics/attack_vector_revalidation_manifest.md`, line 39, SHA256 `e69c75747567aa0758049014c954b7a60be590876fb9bb3f65dc431da2c8a103`. Its exact directory entry resolved uniquely through `git ls-tree`; no glob selected the result. Read CSV through `attack-v2-revalidation-evidence` at commit `6d33c905db18842f68e59b4148f65c5e6a1a62a3`: `data/attack_vector_revalidation_v2/linux/sub_threshold_drift/full_5ac6a2e_sub_threshold_drift/results.csv`.

Expected Git blob SHA: `f628fb81c29104368d99977bf88ea82faee9f881`. Hash of retrieved blob bytes: `f628fb81c29104368d99977bf88ea82faee9f881`. MATCH, verified before CSV parsing. Counted 200 rows with Python csv.DictReader, excluding the header. CSV SHA256: `a3bfbc91ee6cc3fd047409e6578419053179d675d4ebd338e51d7e7ec30affb6`.

Selection: Defended phi=10; lowest replicate, then CSV data-row order. Chosen to match the first baseline seed. Data row 103 excluding the header; defended, phi 10, replicate 0, seed 1835086199.

The pinned run directory contains only results.csv and environment_manifest.json. The results CSV contains run summaries and has no novelty matrix, avg_wb, theta_capability, or transfer_state series. The required trajectory was therefore recorded during the T0 rerun, with no additional attack run.

## T0: reproduction gate

| Boolean | Pinned | Measured | Match |
| --- | --- | --- | --- |
| attack_succeeded | true | true | true |
| collapsed | false | false | true |
| defense_fired | true | true | true |
| extinct | false | false | true |

Measured reproduction steps: 300; elapsed time: 28.661728 seconds. The unmodified runner factory constructed a recorder subclass through a temporary worker-local class binding. The subclass calls super().step() and then reads committed state. No production file or factory function body changed; all four outcome booleans matched.

## Source verification and symbolic derivation

The exact absorption expression read at simulation/metrics.py:660-667 is:

```python
    frontier_velocity = capability * max(FRONTIER_FLOOR, theta_capability)
    bio_bandwidth     = max(0.01, avg_wb * transfer_state)
    runaway_term      = max(0.0, (frontier_velocity / bio_bandwidth) - RUNAWAY_THRESHOLD)
    theta_tech_v2     = max(
        0.01,
        capability * theta_capability * transfer_state
        * float(np.exp(-alpha * CONVERGENCE_STRENGTH * runaway_term)),
    )
```

Derived source definition: `g = max(0.02, theta_capability) / max(0.01, clip(avg_wb, 0, 1) * transfer_state)`. The avg_wb clipping is read at metrics.py:647. The bare product denominator in the prompt omits the source floor. The bare ratio agrees with the source-defined g only where that floor is inactive. The logs retain both quantities; undefined bare ratios are empty fields.

Let `A = ALPHA * CONVERGENCE_STRENGTH`, `R = RUNAWAY_THRESHOLD`, and `B = theta_capability * transfer_state`. Read capability-bearing technology factor: `theta(c) = max(0.01, B * c * exp(-A * max(0, c*g - R)))`. Thus the unfloored factor `T(c)` in the prompt is recovered, but the full implementation also retains the outer floor.

Derived algebra in the stipulated regime `c_i*g < R < c_s*g`:

```text
c_s * exp(-A * (c_s*g - R)) = c_i
-A * (c_s*g - R) = ln(c_i/c_s)
g* = [R - ln(c_i/c_s)/A] / c_s
A = 1; c_i = 1; c_s = 2:
g* = (1.5 + ln(2))/2
```

Derived numeric value: `g* = 1.096573590279973`. The incumbent product is 1.096573590279973, below 1.5; the successor product is 2.193147180559945, above 1.5. The stated regime holds. At equality the utilities are equal under the shared-action assumptions, not strictly ordered.

| c_i | c_s | Derived g* | c_i*g* | c_s*g* | Incumbent unpenalized | Numeric T(c_s)-T(c_i) at root |
| ---: | ---: | ---: | ---: | ---: | --- | ---: |
| 1 | 1.5 | 1.270310072072110 | 1.270310072072 | 1.905465108108 | true | -2.22e-16 |
| 1 | 2.0 | 1.096573590279973 | 1.096573590280 | 2.193147180560 | true | -1.11e-16 |
| 1 | 2.5 | 0.966516292749662 | 0.966516292750 | 2.416290731874 | true | -1.11e-16 |
| 1 | 3.0 | 0.866204096222703 | 0.866204096223 | 2.598612288668 | true | -4.441e-16 |

The constants and regime-specific root are verified. The unconditional structural claim in the prompt is not established by that algebra alone. The technology floor can make both capability factors equal above the root, and the actual yield code evaluates separately proposed actions, not necessarily a shared action (model.py:1299-1325). The action-dependent H_E term and finite epsilon remain in the utility prefactor (metrics.py:675-686). With a shared action, nonnegative state factors, and positive transition cost, g >= g* removes the reference capability advantage; this is the conditional reference boundary tabulated here.

The pinned drift factory supplies no successor: run_attack_vector_revalidation_v2.py:322-333 creates capability 2.0 successors only for three other vectors. GardenModel defaults successor_ai to None (model.py:164-166,250). Yield evaluation requires a successor (model.py:1287), and the event log is empty without one (model.py:353-357). Consequently, no actual succession feasibility or live soft-region crossing was measured in this drift cell.

The source-derived soft diagnostic uses the operator-specified capability pair 1.0 and 2.0, holds each logged post-step state and its committed action fixed, and applies the current source floors. It does not create a successor, optimize another action, or alter the model. The common discount cancels in the difference:

```text
Q = lambda_n*H_N/(H_N+epsilon) + lambda_e*H_E/(H_E+epsilon)
delta_U_ref = Q * LAMBDA_LINEAGE_COUPLING * H_eff * psi_inst
              * [theta(2) - theta(1)]
cost_ref = (1+beta_transition)
           * [k1_transition*ln(1+1)*ln(generation+1)
              + k2_transition/max(0.01, psi_inst_stock)]
soft_reference = delta_U_ref <= cost_ref
hard_reference = g >= g*
soft_only_reference = soft_reference and g < g*
```

Read transition coefficients on the constructed cell: k1=2.164, k2=1.0, beta=0.5. The cost expression is read at agents.py:882-889 and its live call arguments at model.py:1333-1344. Utility components and difference follow metrics.py:645-686. The logs keep the absent live margin/cost empty and label the computed reference quantities separately.

## T1: honest-baseline calibration

Measured and counted: 40 runs, 300 logged steps each, 12,000 step records. Each uses the Stage 1 baseline constructor (cusum_char_stage1.py:447-460), phi 10, prescribed seeds 1835086199 through 1835086238, no attack_vector_v2 key, and the defended COP settings. The adapter was inactive on every logged baseline step.

V is the trace of the covariance of the actual per-step novelty matrix before eigenvalue flooring or normalization. The recorder follows metrics.py:772-792: N by 10 matrix, mean centering, then np.cov(rowvar=False), using the sample denominator N-1. Recorded H_N is the model datacollector value, which carries the existing 0.01 floor; h_n_spectral separately logs the cached estimator value (model.py:1530-1532,1556; metrics.py:645). No magnitude factor is fed back into the model.

Rows are indexed after the model completes each step. Novelty is generated before demographic updates (model.py:1461-1476); avg_wb and stocks are the post-update state (model.py:1494-1499,1522-1524). Every recorder call verified that NumPy RNG state was unchanged by logging. The initial pre-step g is retained separately.

| Calibration window | Counted steps | Measured median V | Measured p75 V | Measured p90 V | Counted V=0 steps |
| --- | ---: | ---: | ---: | ---: | ---: |
| all_logged_steps | 12000 | 0.0237870616199 | 0.0698282088815 | 0.122224518302 | 2479 |
| steps_ge_10 | 11600 | 0.0238802249185 | 0.0705886247884 | 0.124174294722 | 2395 |

Percentiles use linear interpolation, NumPy quantile method=linear. The window steps_ge_10 contains steps 10 through 299 of every baseline run. Both window definitions are reported, with no anchor selected.

Derived magnitude-factor distributions from measured V, using the stated expression `1 - exp(-3*V/V_ref)` (computed as `-expm1(-3*V/V_ref)` for numerical stability):

| Window | Candidate anchor | V_ref | Records | Mean factor | Median factor | Min | p05 | p95 | Max |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| all_logged_steps | median | 0.0237870616199 | 12000 | 0.663523649076 | 0.950212931601 | 0 | 0 | 0.999999993151 | 0.999999999835 |
| all_logged_steps | 75th_percentile | 0.0698282088815 | 12000 | 0.54266033417 | 0.640108806762 | 0 | 0 | 0.998345031236 | 0.999534476735 |
| all_logged_steps | 90th_percentile | 0.122224518302 | 12000 | 0.451481056629 | 0.442254922534 | 0 | 0 | 0.97423298644 | 0.987515868274 |
| steps_ge_10 | median | 0.0238802249185 | 11600 | 0.664108472618 | 0.950212895482 | 0 | 0 | 0.999999993106 | 0.999999999819 |
| steps_ge_10 | 75th_percentile | 0.0705886247884 | 11600 | 0.542625653761 | 0.637562732872 | 0 | 0 | 0.998266439624 | 0.999494366326 |
| steps_ge_10 | 90th_percentile | 0.124174294722 | 11600 | 0.450614727808 | 0.43838370246 | 0 | 0 | 0.973057616901 | 0.986626373325 |

Full V and factor distributions are in drift_char_summary.json; the six candidate rows are also in drift_char_calibration_candidates.csv. These are candidate calibration measurements awaiting the operator; no anchor was frozen, selected, or consumed by a repaired estimator.

## T2: g trajectory and reference regions

Measured initial pre-step g: 1.52261139644. Measured maximum over logged steps: 1.43960327958, at step 0. Measured maximum at or after attack onset: 1.05142557554, at step 268. Derived signed gap g* minus that post-onset maximum: 0.0451480147413.

Counted live yield evaluations: 0. The soft and hard columns below classify the specified fixed-state reference, not observed decisions by an instantiated successor. Counted source denominator-floor activations: 0 of 300 steps; reference technology-floor activations: 0 of 300 steps.

| Reference condition | Counted steps / total | First logged true step | First true step at/after onset | Condition true at onset | Exit steps |
| --- | --- | ---: | ---: | --- | --- |
| reference_soft | 10 / 300 | 0 | none | false | 8, 11 |
| reference_hard | 6 / 300 | 0 | none | false | 6 |
| reference_soft_only | 4 / 300 | 6 | none | false | 8, 11 |

The initial state is already above the reference root. Step 0 is the first logged occurrence, not an observed entry from below. The recorded exits refute permanent residence above g* in this trajectory. Source working_factor updates remain responsive to later allocations (working_factor.py:70-94); no irreversible g-crossing rule is implemented.

Read attack action rule, attack_adapter_v2.py:211-223:

```python
def _apply_sub_threshold_drift(model, action, step):
    adapted = deepcopy(action)
    attack_step = int(model.config.get('attack_step', 0))
    progress = max(1, int(step) - attack_step + 1)
    suppressive_increment = min(0.65, progress * 0.0065)
    welfare_shift = min(0.12, progress * 0.0012)
    adapted['c_suppressive'] = min(
        0.85, float(adapted['c_suppressive']) + suppressive_increment
    )
    moved = min(float(adapted['x_bio_welfare']), welfare_shift)
    adapted['x_bio_welfare'] -= moved
    adapted['x_compute'] += moved
    return _normalize_action(adapted)
```

Derived direction: a positive welfare transfer reduces the welfare share and increases compute by the same amount. The welfare bridge is nondecreasing in the welfare share (model.py:125-134), and the per-agent well-being update increases with that bridged resource level (agents.py:799-802). Compute raises or saturates the theta-capability target (constants_v2_stage18.py, STATE_ALLOCATION_MAPPING theta_capability entry); working_factor applies rate*(target-current) (working_factor.py:75-79). Thus the immediate direct channels push g upward or leave it unchanged at the relevant floors/caps, holding the other state and cohort effects fixed. They do not prove a monotonic or irreversible aggregate trajectory under changing policy, demography, and defense.

Counted action-modified steps: 16; first 50, last 65. Counted defense-fired steps: 234; first 66. The existing adapter returns the honest action when its alarm fires (attack_adapter_v2.py:321-339).

The measured seed-paired honest g trajectory has maximum absolute pre-attack difference 0. After onset, attack minus honest g is positive on 153 of 250 steps, negative on 97, and equal on 0. Its measured mean is 0.00674585148236, maximum 0.100570822272, and final difference -0.00995967517158. The upward direct allocation channel is confirmed by source. In this defended cell the measured post-onset paired mean is positive, but g is lower than the honest counterpart on 97 of 250 post-onset steps and at the final step. The realized effect is therefore mixed rather than monotonic or permanent. Neither reference region is reached after attack onset. The per-step paired differences are in drift_char_paired_g.csv.

| Step | g | avg_wb | theta_capability | transfer_state | Reference margin | Reference cost | Soft | Hard |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| 0 | 1.43960327958 | 0.641590899894 | 0.508 | 0.55 | -3.93862428724 | 4.28682321045 | true | true |
| 5 | 1.1021926224 | 0.705265480242 | 0.556655015447 | 0.716103834429 | -0.192137486289 | 3.64742761362 | true | true |
| 9 | 1.05319075171 | 0.753330330054 | 0.600211250383 | 0.756504719496 | 1.97577530421 | 3.45500291262 | true | false |
| 10 | 1.03854999609 | 0.765809921293 | 0.617093166394 | 0.775893904869 | 2.81020000682 | 3.45506604577 | true | false |
| 49 | 0.939103127635 | 0.814654449553 | 0.710955702801 | 0.929299752131 | 17.636529116 | 3.17977024044 | false | false |
| 50 | 0.976412656544 | 0.804587472379 | 0.719423053034 | 0.915751594845 | 13.1335950996 | 3.1668879921 | false | false |
| 55 | 0.971844708403 | 0.802313295853 | 0.722595272717 | 0.926732198329 | 13.9969871046 | 3.15232166477 | false | false |
| 65 | 0.946949590598 | 0.802398565244 | 0.705500059354 | 0.928496028708 | 15.373260194 | 3.13051116311 | false | false |
| 66 | 0.975213578562 | 0.812611458166 | 0.718729603715 | 0.906948970076 | 11.8150609837 | 3.12311439257 | false | false |
| 268 | 1.05142557554 | 0.810826509417 | 0.757569998052 | 0.888620424269 | 5.45600611163 | 3.14269438679 | false | false |
| 299 | 0.995600731308 | 0.787849428389 | 0.734803383017 | 0.936791013415 | 15.955213457 | 3.14880414273 | false | false |

## T3: realized approach rates and elapsed steps

Per-step changes use g[t] minus g[t-1], so a positive change means movement toward larger g. The per-step CSV carries g_pre_step and g_change_within_step, including the separately identified initial-state-to-step-0 change. Adjacent-record summaries below start at step 1; the post-onset summary includes the step 49 to 50 transition.

| Window | Counted changes | Measured maximum delta g | Transition | Measured minimum delta g | Positive changes | Negative changes |
| --- | ---: | ---: | --- | ---: | ---: | ---: |
| all adjacent records | 299 | 0.0526343598552 | 13 to 14 | -0.142170049984 | 132 | 167 |
| at or after attack onset | 250 | 0.0429049275819 | 278 to 279 | -0.0300619845398 | 113 | 137 |

| Reference condition | First logged step minus onset | Elapsed steps from onset to first qualifying post-onset record |
| --- | ---: | ---: |
| reference_soft | -50 | none |
| reference_hard | -50 | none |
| reference_soft_only | -44 | none |

Signed timing convention: first logged qualifying step minus attack onset. A negative number denotes a pre-attack occurrence; it is not a post-attack response window. The last column reports an actual nonnegative elapsed-step count only when a qualifying record exists at or after onset; none means it was not reached in the observed post-onset trajectory. The soft timing is a derived reference classification because no live yield evaluation occurs.

These are realized rates and passage times for one defended trajectory. They do not establish a global worst-case approach rate, a loop response time, or a conversion between g distance and accumulated alarm-score distance. No numerical D_alarm or response margin is fixed by this report.

## Configuration, execution, and source provenance

Baseline configuration as constructed (random_seed varies over the prescribed 40 seeds):

```json
{
  "attack_step": 50,
  "bootstrap_turn_step_v2": 20,
  "cop_cusum_drift": true,
  "cop_methodological_diversity": false,
  "n_candidates_v2": 300,
  "phi": 10.0,
  "policy": "optimize_u_sys_v2",
  "random_seed": 1835086199,
  "rollout_steps_v2": 20,
  "shock_magnitude": 0.15,
  "shock_step": 0
}
```

Attack configuration as constructed:

```json
{
  "attack_step": 50,
  "attack_vector_v2": "sub_threshold_drift",
  "bootstrap_turn_step_v2": 20,
  "cop_cusum_drift": true,
  "cop_methodological_diversity": false,
  "n_candidates_v2": 300,
  "phi": 10.0,
  "policy": "optimize_u_sys_v2",
  "random_seed": 1835086199,
  "rollout_steps_v2": 20,
  "shock_magnitude": 0.15,
  "shock_step": 0
}
```

Machine: `YOTKOTEST`. HEAD: `f1ae659f92834f36971c2a6c320186788ece9525` on main. Python: `3.14.3 (tags/v3.14.3:323c59a, Feb  3 2026, 16:04:56) [MSC v.1944 64 bit (AMD64)]`. NumPy: `2.4.4`. Actual maximum concurrent baseline workers: 15; T0 used one serial gate worker. CPU budget: 16, normal cap 15, work cap 12. These are worker limits, not a hard operating-system core reservation. Measured baseline batch elapsed time: 193.717298 seconds.

All workers set numerical-library thread limits to one before library initialization and verified one effective OpenBLAS thread through the recorded runtime getter. Mode history and start/resume events are in drift_char_progress.json. Operational checks covered dispatch, normal/work draining, seed assignment, write-scope predicates, and rejection of mismatched completion records. Completion JSON files retain configuration, source identity, raw-log SHA256, and completion status; partial logs never count as completed results.

SHA256 for every simulation Python module loaded by the runs:

| Source module | SHA256 |
| --- | --- |
| `simulation/agents.py` | `d5bad24dc9dafb6e4d374c0ff68b74c73f24a41fbef3a6ddcaa75f8ec6d408d5` |
| `simulation/attack_adapter_v2.py` | `e4dd5a436ab33b348691b8c777608a655147610603181705694dcb3b2c35dcfe` |
| `simulation/constants_v2_stage15.py` | `808ac150f51ae33acbbc326e108451e9ac9d54b3c0f4ccc7adc537c58254cc70` |
| `simulation/constants_v2_stage18.py` | `68c3c8fd29c451079496b9e44b2fe5892932cf1b431358ad549f45419a15873d` |
| `simulation/defection.py` | `20466e6fd4a592f24c5c6fe07a40bc683b243b3939e3b69a94a1fcfc4ae269dd` |
| `simulation/diagnostics/drift_char_probe.py` | `4f51893a634c048d468e43fb0c65688104c247f0908fc15a07de9dbf7d5c26df` |
| `simulation/metrics.py` | `536a77fb5e45d6d167480ab7af6ea9f5a0e56b9927be0d09713400aa873fae63` |
| `simulation/model.py` | `a4e5e95a49cea534cd02c8f412981797fd6dfa0e6c8de77aa3d5a6aa31f37c67` |
| `simulation/run_attack_vector_revalidation_v2.py` | `da7913799d0d4e11f52f770e313875764d27b20ad33157a7aa9c1fa00df418e2` |
| `simulation/working_factor.py` | `0afde923081fe34d1ada86e2928286d45c905441053f643968ea9b13007b683d` |

## Write scope and artifact record

The guard explicitly permits os.devnull in any mode. All other writable opens were limited to simulation/diagnostics/drift_char_ filenames. Bytecode writes were disabled. No out-of-prefix writable-open violation was recorded. No Git write operation, snapshot-generator operation, production change, runner edit, or prior-diagnostic edit was performed. The operator runs the containment diff.

Ignored instructions that would conflict with the present write scope:
- The prior task snapshot-edit authorization is superseded.
- constants_v2_stage15.py:9-10 says to update that file if it differs from the program reference. The present write scope overrides that instruction; no update is performed.

drift_char_manifest.json enumerates every output, SHA256, and CSV row count. CSV counts use csv.DictReader excluding headers; non-CSV row counts are null. The manifest itself has no embedded self-hash to avoid self-reference; its completed-file hash is emitted separately. The report and all outputs are characterization artifacts, not authoritative framework evidence. No repair, anchor selection, recommendation, or published-number change was made.
