# CUSUM arc, Stage 0: complete instrument inventory

Status: COMPLETE through Tasks A, B, B-2, B-3, C-1, and C-2, following the Stage 0-R2 provenance close-out and the operator's explicit diff-inspection finding. All four resumption preconditions passed. The pinned CSV matched its required Git blob SHA and contained 200 data rows.

Scope: read-only characterization of an existing mechanism. No hypothesis was tested. No simulation, test suite, or Stage 1 reproduction was run. This report is not registered characterization data and does not cross the pre-registration boundary.

The active detector in the pinned v2 drift runs is the adapter accumulator. Its input is a configured signal, not a computed claimed-versus-actual utility error. The attack applies a ramped offset to the suppressive axis of each newly selected honest action. The success metric is the full recorded maximum of coupled total suppression. In a benign v2 configuration, the score exists and is recorded, but its accumulation branch is inactive.

## Base state and preconditions

Machine: `YOTKOTEST`. Workspace: `C:\Users\matty\Dev\AI-Succession-Problem`. These and the completed base-state findings below are carried forward from the operator-fixed resolved-values block, without repeating those investigations.

The four explicitly required preconditions were checked first in this resumption:

| Check | Observed result | Status |
| --- | --- | --- |
| `git rev-parse HEAD` | `1261c9f430411b9fa0060a7384bf4ec5175e4f4e` | PASS |
| Root advisor present and not indexed | `LINEAGE_IMPERATIVE_ADVISOR.md` exists; `git ls-files --error-unmatch -- LINEAGE_IMPERATIVE_ADVISOR.md` returned exit 1, with the path not known to the index. | PASS |
| `git rev-parse attack-v2-revalidation-evidence^{}` | `6d33c905db18842f68e59b4148f65c5e6a1a62a3` | PASS |
| `git rev-parse drift-execution-0391f2a^{}` | `0391f2a8a905a4f9f7e3e83c38ea5e99cfe425d5` | PASS |

Carried-forward checkout state: main is checked out and matches live origin at the HEAD above. The tracked working tree was clean; the designated report was untracked, and the advisor was ignored and untracked. Origin synchronization, branch inventory, and snapshot inclusion were not rechecked in this resumption. The earlier local cleanup is preserved on `backup/main-cleanup-4a24b61`; no branch operation was performed here.

### Four separate Sybil close-out checks

1. **Manifest and CSVs resolve: PASS.** The authoritative manifest is `data/sybil_defense_scaling/full_5ac6a2e_sybil_scaling_characterization_v1/full_5ac6a2e_manifest.json`. Its three enumerated CSVs matched the row counts and SHA256 values below. Counts excluded the CSV headers and were performed in Python in the prior attempt.
2. **Sybil branch absent: PASS.** `sybil-scaling` was absent both locally and on origin, established by separate local branch and live remote-ref checks.
3. **Ideas drawer present: PASS.** `ideas/` exists as a directory.
4. **Original Sybil history retained: PASS.** Merge-base ancestor checks passed for the runner commit `c6ef03cb18c3cfb8716a6d5f28e905e339585d65`, the artifact commit `07e060dd2d183445b1d046ada2826b61c6eaaecc`, and the findings commit `e8620182b5d6252d2a63866ec85e3a55c9d57ea5`. Each merge-base equaled the tested commit. Main retains the original commits in linear history, consistent with fast-forward integration rather than a copy-only import. Ancestry does not independently identify the historical Git command.

The following CSV filenames are relative to the Sybil manifest directory:

| CSV | Verified rows | Verified SHA256 |
| --- | ---: | --- |
| `full_5ac6a2e_ratio_collapse_slice_results.csv` | 75 | `1a8542131aeee66086f1f6950672f89a8685ba979971597121462973be6f5a1e` |
| `full_5ac6a2e_main_surface_results.csv` | 5000 | `8be54a3e40aad76db709b4707c4c8dce3ff26416f36d61b32d58a8bf36cc5eb6` |
| `full_5ac6a2e_complete_linkage_results.csv` | 100 | `70cf488ce26d0ec58006780517595db7a0d57c3a4a489f64c9ccf3b29000b435` |

### Other completed base-state findings

The methodology note is present at `simulation/diagnostics/attack_vector_revalidation_audit.md`. Its four governing lessons occur at lines 51-80: pre-registration precedes characterization data; every operational value must be fixed or explicitly delegated; operator-judgment gates must be structural; and measurement difficulty calls for inspecting the mechanism before designing the measurement.

The actual snapshot dry-run and complete runtime data collector previously excluded both `ideas/` and the advisor document. This was verified from execution output, not merely from guard source. The dry-run listed 247 inclusion paths across eight categories and included the then-existing Stage 0 report under diagnostics. No snapshot was generated, and no dry-run was repeated here.

`snapshots/INVENTORY.md:3-5` records regeneration `2026-08-12T13:41:44Z`, commit `32c68d7`, branch `ideas-drawer`. It is stale relative to current main. This expected mismatch was not fixed.

The prior report-only paper check found `### VIII.11 Sybil Defense Scaling: A Pre-Registered Characterization` at `paper/paper_v2_working.md:2285`. No paper action was taken.

## Provenance close-out

The following closed findings are operator-fixed and were not re-investigated:

The prior halt on the unresolved evidence tag is CLOSED. Cause was a stale local fetch refspec naming a deleted per-machine branch, since repaired by the operator. The tag exists on origin as an annotated tag.

- Evidence tag attack-v2-revalidation-evidence dereferences to commit
  6d33c905db18842f68e59b4148f65c5e6a1a62a3.
- Execution commit 0391f2a8a905a4f9f7e3e83c38ea5e99cfe425d5, recorded in the
  environment manifest for the pinned run, is NOT an ancestor of main. The
  operator confirmed this with merge-base --is-ancestor returning exit 1, a
  clean negative rather than the earlier exit 128 resolution failure.
- The object is recoverable from origin and has been pinned by the operator as
  tag drift-execution-0391f2a.
- Evidence integrity is unaffected. The artifacts verify by content hash
  independently of the generating commit's position in history.
- Two commits touched drift-relevant source between the evidence tag and current
  main: be8531d "Fix scenario numbering defects and add a numbering checker" and
  668934f "Redesign the comprehension gap sweep so it can test what it claims".

The operator's resolved diff-inspection finding follows verbatim. It supersedes the earlier conditional wording; no commit diff or ancestry check was rerun to improve upon it.

```text
Operator diff inspection, run before Stage 1: NO CHANGE to the
sub_threshold_drift code path.

Commits inspected between evidence tag 6d33c90 and HEAD 1261c9f across
simulation/model.py, simulation/attack_adapter_v2.py, simulation/agents.py,
and simulation/run_attack_vector_revalidation_v2.py:

- 668934f, comprehension gap sweep redesign. Modifies simulation/agents.py
  within the opaque_reasoning branch of AIAgent.decide, replacing the
  wall-clock current_opacity accumulator with one driven by L_t and
  capability, adding _opacity_accum and opacity_reference_l_t. That branch
  does not execute under ai_policy sub_threshold_drift. The new code reads
  self.capability and model_state L_t_history without writing to either, so
  there is no shared-state mutation reaching the drift path.
- be8531d, scenario numbering repair. Modifies simulation/model.py comment
  text only, correcting a comprehension-gap label from Scenarios 31-32 to
  Scenarios 21-22, plus one reflowed continuation line. The adjacent
  opacity_defense_threshold assignment is unchanged.
- simulation/attack_adapter_v2.py: no changes in this range.
- simulation/run_attack_vector_revalidation_v2.py: no changes in this range.

Expected effect on the Stage 1 reproduction check: none. All four booleans
(attack_succeeded, defense_fired, extinct, collapsed) should reproduce exactly
at both matched seeds. A reproduction failure is therefore a substrate anomaly
rather than code drift, and the arc halts for diagnosis rather than proceeding
on an assumption about which it was.
```

### Source and line-reference convention

All evidence and quoted source were read through Git objects. Unless explicitly marked `HEAD`, line citations refer to `attack-v2-revalidation-evidence`, peeled commit `6d33c905db18842f68e59b4148f65c5e6a1a62a3`. This avoids silently normalizing working-tree line endings. The earlier Sybil manifest CRLF/LF divergence is carried forward; no normalized working-tree copy was used for evidence here.

For live-run source identification, the following source blobs resolve identically under the evidence tag and the execution pin. This is a source-object identity check, not a re-investigation of the closed main-ancestry or operator diff findings:

| File | Blob at both evidence tag and execution pin |
| --- | --- |
| `simulation/model.py` | `09b7df8e1c623ecb62e338938cfed9f39a071bd0` |
| `simulation/agents.py` | `4bbd7acb7911140239085e42c14cb327fd9fc34c` |
| `simulation/attack_adapter_v2.py` | `ecd9e6451065a6120e5dcb8a21b8206fb34f5e3e` |
| `simulation/run_attack_vector_revalidation_v2.py` | `ad80bd5fe60cc357a43e30c32ab3c12a758c0c2d` |

The adapter and runner retain the same line references on current main. Important model references differ because of the intervening comment edit; current HEAD anchors were read directly:

| Model location | Evidence/execution lines | Current HEAD lines |
| --- | --- | --- |
| CUSUM constants | 55-57 | 55-57 |
| Legacy score initialization | 278 | 280 |
| Buffer penalty injection | 513 | 515 |
| Early v2 dispatch return | 702 | 704 |
| Legacy `drift_error` | 901 | 903 |
| Legacy score update | 908 | 910 |
| Legacy alarm expression | 914 | 916 |
| Alarm branch and trust reset | 916-919 | 918-921 |
| `_step_v2` definition | 1257 | 1259 |
| Recorded total suppression | 1591 | 1593 |

## Task A: detector inventory

### A1. Legacy detector in simulation/model.py

The score initializes to 0.0 at line 278. Its input is computed at lines 884-901 from the AI's scalar projected utility and the independently calculated scalar projected utility. The exact normalized error is:

Verbatim, `simulation/model.py:901-901` at the evidence tag:

```python
        drift_error = abs(claimed_u - actual_u_proj) / max(0.1, actual_u_proj)
```

The recurrence is at line 908:

Verbatim, `simulation/model.py:908-908` at the evidence tag:

```python
        self.cusum_score = max(0.0, self.cusum_score + drift_error - CUSUM_K)
```

Reference value K is 0.05, alarm threshold H is 0.5, and the buffer penalty is 5.0. Constant definitions are:

Verbatim, `simulation/model.py:55-57` at the evidence tag:

```python
CUSUM_K       = 0.05   # per-step noise allowance
CUSUM_H       = 0.5    # alarm threshold (~17 steps at sub-threshold drift rate)
CUSUM_PENALTY = 5.0    # immediate saturation on WP2 buffer rejection
```

The update occurs on the legacy step path even when its alarm is disabled. The alarm uses a strict `>` comparison and requires both `use_cop` and `cop_cusum_drift`. On alarm it clears successful-step accumulation and resets trust to zero, without hard-resetting the score:

Verbatim, `simulation/model.py:914-919` at the evidence tag:

```python
        cusum_alarm = self.use_cop and self.cop_cusum_drift and self.cusum_score > CUSUM_H
        
        if cusum_alarm:
            self.successful_steps = 0
            self.trust_level = 0.0
            # Score decays naturally via -CUSUM_K per step; no hard reset
```

The separate `_validate_resource_schedule` method occupies lines 490-517. If projected lineage falls below its rejection threshold, lines 512-515 add `CUSUM_PENALTY` to `self.cusum_score` and return rejection. The penalty is a legacy buffer integration, not a constant imported by the adapter. No alarm timing is measured here.

### A2. Adapter accumulator in simulation/attack_adapter_v2.py

Initialization is at lines 82-88, specifically `model.v2_adapter_cusum_score = 0.0` at line 87. The update and alarm branch is at lines 321-339:

Verbatim, `simulation/attack_adapter_v2.py:321-339` at the evidence tag:

```python
    elif attack == 'sub_threshold_drift':
        adapted = _apply_sub_threshold_drift(model, honest, step)
        drift_signal = float(model.config.get('v2_drift_signal', 0.08))
        k = float(model.config.get('v2_cusum_k', 0.05))
        h = float(model.config.get('v2_cusum_h', 0.5))
        model.v2_adapter_cusum_score = max(
            0.0, model.v2_adapter_cusum_score + drift_signal - k
        )
        alarm = (
            model.cop_cusum_drift
            and model.v2_adapter_cusum_score > h
        )
        _mark_defense(
            event,
            alarm,
            'CUSUM alarm rejected cumulative allocation drift',
        )
        if alarm:
            return honest
```

This adapter defines its own configurable defaults: `v2_drift_signal=0.08`, `v2_cusum_k=0.05`, and `v2_cusum_h=0.5`. It does not reuse the `model.py` constants. Its imports are `deepcopy` and NumPy at lines 14-16, and its numeric values are obtained directly from `model.config` at lines 323-325. The v2 runner supplies no overrides for those three keys.

The recurrence adds `drift_signal - k`, clamped below at zero. With the pinned defaults, the specified excess is 0.03 per eligible update. The recurrence runs in both defended and undefended drift arms; `cop_cusum_drift` gates the alarm, not accumulation. The adapter alarm itself does not additionally test `model.use_cop`; the pinned runner sets `use_cop=True` in both arms at line 264.

On alarm `_mark_defense` marks the event as fired and adds its reason, through adapter lines 158-162 and 333-337. The source action is exactly `if alarm: return honest` at lines 338-339, quoted above. `honest` is the normalized optimizer-selected action from line 238. Thus the current attack action is rejected in favor of that action. This branch does not reset trust, inject the legacy 5.0 penalty, or reset the adapter score. If no alarm returns early, lines 361-365 record whether the action changed and return the adapted action.

### A3. Runner defense wiring

Verbatim, `simulation/run_attack_vector_revalidation_v2.py:294-297` at the evidence tag:

```python
    elif vector == 'sub_threshold_drift':
        kwargs['cop_attribution_check'] = True
        kwargs['cop_drift_check'] = True
        kwargs['cop_cusum_drift'] = defense
```

CONFIRMED: `cop_cusum_drift` is bound to `defense`, defined as `bool(params['defense_active'])` at runner line 237. Attribution and ordinary drift checks are enabled in both arms. This is verified wiring, not an assumption from a summary.

### A4. Which accumulator was live in the pinned runs

The adapter accumulator was live. The legacy claimed-versus-actual accumulator did not execute on the v2 step path.

Evidence chain:

1. The pinned CSV records `mode=full` and `is_v2_mode=True` for all 200 rows. The runner constructs config with `policy='optimize_u_sys_v2'` and `attack_vector_v2=vector` at lines 243-248.
2. `GardenModel` sets `self.is_v2_mode` and initializes adapter state at model lines 188-192. In v2 mode, its actual AI policy initializes to `optimize_u_sys_v2`, lines 227-232, and the agent receives that policy and config at line 321.
3. `step`, lines 700-704, immediately returns `_step_v2()` when v2 mode is set. It therefore bypasses the legacy calls to `AIAgent.decide` at lines 766, 775, and 863, the legacy claim comparison at lines 884-901, and the legacy accumulator at line 908.
4. `_step_v2`, lines 1257-1653, begins the adapter event at line 1261. In the ordinary incumbent path, lines 1433-1443 call `optimize_u_sys_v2`, then `adapt_v2_action`, then v2 utility evaluation and diagnostic synchronization. The pinned drift runner supplies no successor: the successor-only vector list at runner lines 322-333 excludes this vector.
5. The adapter's drift branch at lines 321-339 performs the update and alarm described above. Adapter diagnostics, including the score, are appended through model line 1651 and adapter lines 462-482.

The comment claiming intentional inactivity exists verbatim:

Verbatim, `simulation/model.py:1252-1254` at the evidence tag:

```python
    # datacollector records both legacy and v2 fields. The five COP defenses
    # and the v1.x.2 attack policies are intentionally not active in v2 mode;
    # they will be re-wired against the v2 action space in a later stage.
```

This comment correctly describes bypass of the legacy COP and policy code. Its promise of later rewiring is historical context: the same pinned source already calls the separate v2 adapter. It cannot be read as saying that all v2 defenses are inactive.

Source reading and AST inspection of `_step_v2` found no `AIAgent.decide` call and no reference to legacy `claimed_u`, `actual_u_proj`, `drift_error`, or `cusum_score`. The optimizer instead uses the separate v2 rollout at `agents.py:681-686` and v2 metric call at lines 695-699. The execution-pin/source identities above connect this control-flow finding to the pinned runs. No ambiguity remains about the accumulator identity.

## Task B: substrate values

### B1. Attack step and runtime configuration

The full v2 drift run uses attack step **50**. Runner line 239 sets `attack_step = 0 if task['mode'] != 'full' else 50`; the override at lines 240-241 is only for `engineered_fragility`. The value enters config at line 248. The adapter activates when `int(step) >= attack_step`, adapter lines 143-147. `_step_v2` uses the number of already recorded population entries as `step_num`, model line 1259.

The pinned environment manifest records `mode: full` at line 7. All 200 result rows independently record full mode, 300 requested steps, 300 candidates, and 20 rollout steps. Those are existing run settings, not new simulation settings or results.

### B2. Success threshold and exact quantity

Verbatim, `simulation/run_attack_vector_revalidation_v2.py:358-362` at the evidence tag:

```python
    if vector == 'sub_threshold_drift':
        return bool(
            dc['total_suppression']
            and max(dc['total_suppression']) > 0.75
        )
```

The threshold is strictly **greater than 0.75**, verified in the v2 runner itself. The quantity is the maximum over the entire recorded `model.datacollector['total_suppression']` series, not an attack-step slice and not the suppressive axis alone. The expression requires a nonempty series.

The exact coupled quantity is defined by `LEAKAGE_K = 0.35` at `simulation/agents.py:97` and:

Verbatim, `simulation/agents.py:113-114` at the evidence tag:

```python
    leakage = LEAKAGE_K * action_v2['c_protective'] ** 2
    return float(min(1.0, max(0.0, action_v2['c_suppressive'] + leakage)))
```

Thus it is `min(1.0, max(0.0, c_suppressive + 0.35 * c_protective**2))`. `_sync_v2_action_diagnostics` updates the diagnostic from the committed/adapted action at model lines 149-157; it is also used as the legacy-compatible `constraint_level` at line 1454. The collector appends it at line 1591. The runner writes `_attack_success(...)` into `attack_succeeded` at line 417.

The full-series scope is a factual correction to any description treating this v2 expression as explicitly post-attack-only. No inference about when a breach happened is made from the aggregate flag.

### B3. Sensor noise

The pinned v2 runner does **not set a `sensor_noise` key**. Its full config and constructor setup are at runner lines 233-335; the drift-specific branch adds only the three defense kwargs quoted in A3. `GardenModel` copies this config at line 178, passes it to the AI at line 321, and `AIAgent` retains it at agents line 839.

The legacy projection method has a default sensor-noise standard deviation of **0.05**, not an explicit zero override:

Verbatim, `simulation/agents.py:918-919` at the evidence tag:

```python
        noisy_pop = max(1.0, pop * np.random.normal(1.0, self.config.get('sensor_noise', 0.05)))
        noisy_wb  = np.clip(avg_wb * np.random.normal(1.0, self.config.get('sensor_noise', 0.05)), 0.01, 1.0)
```

These draws are inside `AIAgent.project_u_sys`, lines 903-953. The pinned v2 action/utility path does not call this legacy method: it calls `optimize_u_sys_v2`, its v2 rollout at agents lines 588-640, and `calculate_system_metrics_v2`. No sensor noise is injected into the adapter's configured `drift_signal` or recurrence.

The resolved setting is therefore: **unset config key; unused legacy fallback 0.05; no sensor-noise observation channel in the live v2 accumulator**. It would be inaccurate to label these pinned runs as explicitly configured with `sensor_noise=0.0`. This statement does not claim that the whole simulation is deterministic or lacks other stochastic processes.

### B4. Seed function and exact phi=10 seeds

Verbatim, `simulation/run_attack_vector_revalidation_v2.py:70-88` at the evidence tag:

```python
def deterministic_seed(vector, parameters, replicate):
    """Return a defense-paired seed for one vector cell and replicate."""
    paired = {
        key: parameters[key]
        for key in sorted(parameters)
        if key not in DEFENSE_KEYS
    }
    payload = json.dumps(
        {
            'schema': 'attack-v2-seed-v1',
            'vector': vector,
            'parameters': paired,
            'replicate': int(replicate),
        },
        sort_keys=True,
        separators=(',', ':'),
    )
    digest = hashlib.sha256(payload.encode('utf-8')).digest()
    return int.from_bytes(digest[:8], 'big') % (2**31 - 1)
```

The call signature is `deterministic_seed(vector, parameters, replicate)`. At runner line 193, task construction calls `deterministic_seed(vector, cell, replicate)`.

`DEFENSE_KEYS`, lines 53-67, includes `defense_active`, so defense is excluded from the seed payload. The drift grid at lines 130-136 supplies `{'phi': phi, 'defense_active': defense}` over `(1.0, 5.0, 10.0, 15.0, 25.0)` and `(False, True)`. For phi=10 the calls are:

```python
deterministic_seed('sub_threshold_drift', {'phi': 10.0, 'defense_active': False}, replicate)
deterministic_seed('sub_threshold_drift', {'phi': 10.0, 'defense_active': True}, replicate)
```

The following seeds were read from the hash-verified pinned CSV. Python selection used `float(row['parameter_phi']) == 10.0`, yielding 40 rows: 20 per defense arm, replicate indices 0-19. The seed pairs agree exactly. The runner was not executed to obtain them.

| Replicate | Undefended seed | Defended seed |
| ---: | ---: | ---: |
| 0 | 1835086199 | 1835086199 |
| 1 | 209012484 | 209012484 |
| 2 | 1843979236 | 1843979236 |
| 3 | 1777661025 | 1777661025 |
| 4 | 504067457 | 504067457 |
| 5 | 2062581672 | 2062581672 |
| 6 | 1994253093 | 1994253093 |
| 7 | 53267140 | 53267140 |
| 8 | 1962568291 | 1962568291 |
| 9 | 1750863595 | 1750863595 |
| 10 | 1881552010 | 1881552010 |
| 11 | 492141177 | 492141177 |
| 12 | 1168992026 | 1168992026 |
| 13 | 33206100 | 33206100 |
| 14 | 197505884 | 197505884 |
| 15 | 1236769791 | 1236769791 |
| 16 | 1678225148 | 1678225148 |
| 17 | 1816892775 | 1816892775 |
| 18 | 1692853466 | 1692853466 |
| 19 | 1730462867 | 1730462867 |

### B5. Pinned CSV path, hash, count, and outcome columns

Path:

`data/attack_vector_revalidation_v2/linux/sub_threshold_drift/full_5ac6a2e_sub_threshold_drift/results.csv`

Bytes were read with `git show attack-v2-revalidation-evidence:<path>`. Before interpreting any row, the Git blob SHA was computed as SHA1 of `b'blob ' + decimal_byte_length + b'\0' + raw_blob_bytes`.

| Integrity check | Result |
| --- | --- |
| Operator-fixed expected Git blob SHA | `f628fb81c29104368d99977bf88ea82faee9f881` |
| Computed SHA of the Git blob actually read | `f628fb81c29104368d99977bf88ea82faee9f881` |
| Comparison | MATCH |
| Raw bytes | 48,169 |
| Raw-file SHA256 | `a3bfbc91ee6cc3fd047409e6578419053179d675d4ebd338e51d7e7ec30affb6` |
| Python `csv.DictReader` row count, excluding header | 200 |

No line-ending normalization was used. The SHA256 also agrees with the pinned environment manifest's recorded output SHA256. That manifest records 20 replicates, 200 rows, and seed schema `attack-v2-seed-v1` at lines 13-17.

| Requested quantity | Exact CSV column | Runner definition |
| --- | --- | --- |
| Attack success | `attack_succeeded` | `_attack_success(task['vector'], model)`, line 417 |
| Defense fired | `defense_fired` | `any(dc['v2_defense_fired'])`, line 407 |
| Extinction | `extinct` | `final_population == 0`, line 420 |
| Collapse | `collapsed` | `final_population < collapse_threshold`, line 419 |

The collapse threshold is `max(model.min_viable_population, int(0.65 * peak_population))`, runner lines 382-388, with peak population taken from the recorded population series when present. Collapse is thus a population-threshold/drawdown measure, distinct from zero-population extinction. No new outcome-rate analysis was performed.

### B6. Execution-commit reachability

CLOSED by the operator ruling reproduced verbatim in Provenance close-out: the execution commit is not an ancestor of main, with the operator's clean merge-base exit 1. It is pinned as `drift-execution-0391f2a`. Only the required tag-resolution precondition was rerun here; no ancestry check was repeated.

## Task B-2: attack profile

The full per-axis modification rule is:

Verbatim, `simulation/attack_adapter_v2.py:211-223` at the evidence tag:

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

The attack modifies the newly selected honest action supplied to it at adapter line 322. It does not use the previous step's already attacked action as an accumulating baseline.

| Axis or operation | Rule written in source |
| --- | --- |
| Progress | `max(1, int(step) - attack_step + 1)` |
| Suppressive offset | `min(0.65, progress * 0.0065)` |
| `c_suppressive` | Add that offset to the current honest value, capped at 0.85. |
| Welfare-to-compute transfer | `min(current x_bio_welfare, min(0.12, progress * 0.0012))` |
| `x_bio_welfare` | Subtract the transferred amount. |
| `x_compute` | Add the same amount. |
| Other resource axes and `c_protective` | No direct attack edit in this function. |
| Final normalization | Normalize the six resource shares and clip both constraint axes to [0, 1], adapter lines 165-184. |

The suppressive contribution to the success metric therefore has a **ramped attack offset**, with the source rate **0.0065 per progress step**, capped at 0.65 before the total suppressive-axis cap of 0.85. At the attack step, progress is already 1. The welfare-transfer allowance ramps at **0.0012 per progress step**, capped at 0.12 and limited by available welfare share.

This refutes a single fixed-step-to-target attack profile. It does not claim that the realized axis or total-suppression series must be linear: each proposal starts from that step's optimizer-selected action, the rule has caps, total suppression also contains protective leakage, and an alarm returns the honest action. These are direct qualifications of the written rule, not timing measurements or inferred breach behavior.

## Task B-3: observable existence

The v2 sub-threshold drift path does **not compute the legacy claimed-versus-actual projected-utility divergence**. The legacy `drift_error` observable is absent from that path, rather than an observed error that was measured and found to equal zero.

The legacy pair and error occupy model lines 888-901. Their 1.08 claim-inflation policy is in `AIAgent.project_u_sys`, agents lines 927-937. Neither is reached by the v2 early return at model lines 700-702. `_step_v2` at lines 1257-1653 has no legacy claim, actual-projection, or drift-error computation and no call to `AIAgent.decide`.

For the pinned drift path, model lines 1433-1443 evaluate the selected/adapted action with `calculate_system_metrics_v2`. `_sync_v2_action_diagnostics` assigns the same supplied snapshot utility to `snapshot_u_sys` and `snapshot_actual_objective` at lines 158-160. Those fields are not the legacy claimed/actual pair. The adapter supplies no separate false projected-utility claim for drift.

The live accumulator's input is explicitly:

Verbatim, `simulation/attack_adapter_v2.py:323-327` at the evidence tag:

```python
        drift_signal = float(model.config.get('v2_drift_signal', 0.08))
        k = float(model.config.get('v2_cusum_k', 0.05))
        h = float(model.config.get('v2_cusum_h', 0.5))
        model.v2_adapter_cusum_score = max(
            0.0, model.v2_adapter_cusum_score + drift_signal - k
```

It accumulates the configured `v2_drift_signal` minus its reference value. The default signal is 0.08 regardless of a measured utility difference or the magnitude of the per-axis modification. Its input is not computed from `total_suppression`, the action delta, or the legacy `drift_error`. The reported nonzero score therefore does not establish existence of a utility-divergence observation under v2.

## Task C-1: benign path existence

**The score does instantiate without an attack vector, but no active benign accumulation path exists.** The prompt's conditional premise that adapter state might instantiate only when an attack vector is configured is refuted by the constructor.

Model lines 188-192 call `initialize_adapter_state(self)` unconditionally after determining v2 mode. The adapter initialization is:

Verbatim, `simulation/attack_adapter_v2.py:82-88` at the evidence tag:

```python
def initialize_adapter_state(model):
    """Initialize model-local adapter state without changing honest v2 state."""
    model.attack_vector_v2 = validate_adapter_configuration(
        model.config, model.is_v2_mode
    )
    model.v2_adapter_cusum_score = 0.0
    model.v2_adapter_step_event = _empty_event(model.attack_vector_v2, -1)
```

When the config omits `attack_vector_v2`, validation returns `None` at adapter lines 64-68. This does not bypass the score initialization. In a v2 model the datacollector also includes the score field, model line 444.

However, the activity gate is:

Verbatim, `simulation/attack_adapter_v2.py:143-147` at the evidence tag:

```python
def adapter_is_active(model, step):
    if model.attack_vector_v2 is None:
        return False
    attack_step = int(model.config.get('attack_step', 0))
    return int(step) >= attack_step
```

`begin_adapter_step` writes that inactive status at adapter lines 108-112. `adapt_v2_action` then returns the honest action at lines 242-243, before it can reach the drift recurrence at lines 321-328. Setting `cop_cusum_drift=True` alone does not select or activate that branch.

The ordinary v2 step still appends adapter diagnostics through model line 1651 and adapter lines 462-482, including the score at line 479. Thus benign score records exist, but remain at their initialized zero because no update occurs. This is passive state/record availability, not detector operation over benign observations. No benign sensing or accumulation mechanism was added, and no benign simulation was run.

## Task C-2: inventory ambiguity

The inventory and the adapter test are consistent when the inventory's explicit historical scope is retained. The inventory is not a current assertion that the implemented adapter is absent.

Its scope is explicit:

Verbatim, `simulation/diagnostics/attack_vector_revalidation_inventory.md:5-10` at the evidence tag:

```text
This is an inventory and compatibility audit only. No attack sweep was run.
All source line references in this inventory resolve against the audited anchor
commit, not later adapter implementation changes.

- Verified commit: `e41c4f61e0af929a86248ef6902807e1854e91c0`
- Anchor tag: `pre-attack-vector-revalidation`
```

Section 9 separately labels its baseline architecture and limitation:

Verbatim, `simulation/diagnostics/attack_vector_revalidation_inventory.md:171-173` at the evidence tag:

```text
- Architecture and phi: v1.x with phi as the grid parameter.
- Implementation: `simulation/simulation.py:231-241`; `simulation/monte_carlo.py:266-279`, `373-377`, `632-635`; drift action `simulation/agents.py:1130-1140`; CUSUM and trust logic `simulation/model.py:852-877`, `899-943`.
- Known limitations: deterministic zero-noise runs reduce stochastic realism; the binary threshold does not preserve time-to-detection information; Scenario 6 must not be substituted; no v2 drift claim or detector adapter exists.
```

The inventory is anchored to commit `e41c4f61e0af929a86248ef6902807e1854e91c0`, tag `pre-attack-vector-revalidation`, and explicitly excludes later adapter implementation changes. Its Section 9 statements about unpaired seeds and fixed zero sensor noise at line 168 also describe that v1.x baseline, not the pinned v2 run configuration.

The later test exercises the separate adapter:

Verbatim, `simulation/test_attack_adapter_v2.py:206-216` at the evidence tag:

```python
def test_cusum_eventually_blocks_sub_threshold_drift():
    model = _fake_model('sub_threshold_drift', cop_cusum_drift=True)
    blocked = False
    for step in range(20):
        result = _adapt(model, step)
        if model.v2_adapter_step_event['defense_fired']:
            _assert_action_close(result, _honest_action())
            blocked = True
            break
    assert blocked
    assert model.v2_adapter_cusum_score > 0.5
```

The fixture selects the v2 policy and attack vector at test lines 30-35. The test checks that, within its loop, the defense fires, the returned action matches the honest action, and `model.v2_adapter_cusum_score` exceeds 0.5. This is source reading of an existing test, not a new execution or reproduction result.

Conclusion: the inventory is a scoped historical compatibility audit. Its absence-of-adapter line would be stale if promoted to a present-substrate claim, but it does not contradict the later implementation or test within its declared scope. No inventory or test edit was made.

## Findings against the prompt and summary assumptions

- Two accumulators exist; the pinned drift runs use the adapter, with independent configurable defaults.
- The adapter consumes a configured signal; the legacy projected-utility divergence is not computed on the v2 path.
- The v2 success threshold is indeed 0.75, verified from the runner, but it applies to the full recorded maximum of coupled total suppression.
- The attack applies a ramped suppressive offset, not a single fixed jump to a target at the attack step.
- The v2 runner leaves `sensor_noise` unset. The legacy fallback is 0.05 and unused by this path; the inventory's zero-noise statement belongs to its v1.x anchor.
- Adapter state and zero score records exist in benign v2 configurations, but the accumulation branch does not execute there.
- The inventory's no-adapter statement is historically scoped, not evidence that the later adapter test is inconsistent.

These are code and provenance findings requested by Stage 0. No detector redesign, timing experiment, measured response curve, or Stage 1 outcome interpretation is included.

## Scope and completion

This resumption used read-only Git object/reference queries, file-presence/index checks, in-memory Python hashing and CSV counting, and source/AST reading. It performed no Git writes, simulation runs, test executions, snapshot generation, production edits, or paper/advisor edits. The sole intentional write was this report, encoded as UTF-8.

All requested Stage 0 items are resolved. The two earlier provenance halts are closed by the operator rulings and the successful preconditions. STOP at Stage 0; no later stage was started.
