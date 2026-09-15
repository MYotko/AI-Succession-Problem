# Drift mapping characterization, attempt 2: halt report

**Status: HALTED during T1. No characterization arm was launched. No A1 through A6 analysis was computed.**

The amended pre-registration passed T0. The honest gate passed the Amendment 1 check. The constructor-equivalence gate then stopped on a recorder exception. These are gate measurements, not characterization results.

## Halt and retained gate evidence

At 2026-09-13T19:16:39.065198+00:00, the common-constructor probe raised:

```text
Recorder cannot obtain spectral shape and V from the step novelty matrix
```

Counted: both constructor logs contain 264 rows, steps 0 through 263. Their configuration dictionaries are equal. All 28 recorder fields match exactly over those 264 shared rows; no first differing field or step was found. The required 300-step comparison did not complete. Full datacollector results were not persisted for the interrupted probes, so their complete datacollector comparison is unavailable.

Derived from the recorder loop and the last emitted row: the common-constructor exception occurred while trying to record step 264. The factory probe stopped at its next stop-marker check. Counted in the final recorded row of each probe: population was 1 at step 263. The failing novelty matrix and return value were not persisted, so their exact contents are not reported as measurements.

Read from `simulation/metrics.py:797-798` and `811-812`: `calculate_h_n` returns the scalar `0.0` on its early-return paths for fewer than two novelty vectors. The attempt recorder at `drift_map_run_a2_executor.py:115` requires a tuple for raw entropy, shape, and V. The recorded exception establishes that this tuple requirement was not met. No shape or variance was substituted and no seed was rerun.

All four gate worker processes and the gate coordinator have exited. Partial constructor logs remain partial and do not count as completed runs.

## T0

| Check | Recorded result |
| --- | --- |
| Branch | main |
| Required ancestor fd444fc22254ec24472f4bad03f8f56bf4470110 | merge-base exit 0 |
| Exact tracked-status command | exit 0, zero stdout lines |
| Design note indexed | ls-files exit 0 |
| Last note commit | c2f4ea9b908247ebe14fed1c081deba8e40142a3 |
| Note commit ancestor of origin/main | merge-base exit 0 |
| Committed note LF SHA256 | 185abccb9ee16a487d53afd9f45946626369f0a0f1806f5593402be224adfc72; matched |
| Section 3 source pins | All seven matched |
| Historical stop file indexed | ls-files exit 0 |
| Attempt 2 namespace before first write | No matching files |

T0 stderr, recorded and non-halting:

```text
warning: unable to access 'C:\Users\matty/.config/git/ignore': Permission denied
```

Known conditions carried forward: CRLF worktree against LF blobs, and possible permission warnings from the unreadable pytest cache and global Git ignore. These conditions were not repaired. The committed note was retrieved with Git and read only after its pinned LF hash passed. The prior attempt stop file was checked for index presence only and was not used as operational state.

## T1 gates

| Gate | Recorded result |
| --- | --- |
| 2, source pins | PASS, seven matches at start and at close-out |
| 3, constructor equivalence | INCOMPLETE, 264 matching recorder rows out of required 300; full datacollector comparison unavailable |
| 4, M1 wrapper identity | PASS, 200 synthetic actions x 300 steps = 60,000 exact comparisons |
| 5, honest arm | PASS, attack vector absent; adapter inactive and action unmodified on all 60 steps |
| 6, recorder RNG | PASS, NumPy state identical before and after all 60 honest recorder calls |

Measured: recomputed raw entropy matched the cached entropy on all 60 honest gate steps. Each successfully emitted constructor row also passed the exact raw-entropy comparison and recorder RNG check.

## Amendment 1

| Probe | Completed gate steps | Increase during step 0 | Increase after step 0 |
| --- | ---: | ---: | ---: |
| Honest | 60 | 2 | 0 |
| Factory | Incomplete | Not persisted | Not persisted |
| Common constructor | Incomplete | Not persisted | Not persisted |

Counted distribution among completed model gate probes: step 0 increase 2 occurred in 1 probe; after-step-0 increase 0 occurred in 1 probe. The two incomplete probes passed the after-step-0 equality check on every successfully recorded step, but their counter snapshots were not persisted at interruption. No final counter values are inferred. No characterization runs exist for an all-arm fallback distribution or confirmation.

## Execution and provenance

- Machine: YOTKOTEST.
- HEAD: b9bfba97eb11d3e127201c038b20fe0e28ae1f9d.
- Python: 3.14.3 (tags/v3.14.3:323c59a, Feb  3 2026, 16:04:56) [MSC v.1944 64 bit (AMD64)].
- NumPy: 2.4.4.
- Operator CPU budget: 16. Selected mode: normal. Characterization limit: 15 workers; work-mode limit: 12.
- Launched gate workers: 4 fresh processes, comprising 3 model probes and 1 wrapper probe. Characterization workers used: 0.
- Numerical-library environment limits: 1. OpenBLAS runtime query verified 1 thread in every gate worker. This is a worker limit, not an operating-system core reservation.
- Scheduler control checks used no model steps. Concurrency caps, drain behavior, normal-mode expansion, deterministic job assignment, and synthetic completed-job skipping passed.
- Runtime control is attempt-specific: `drift_map_run_a2_control.json`. No mode change, interrupted-seed resumption, or rerun occurred.
- Bytecode writes were disabled. The guard explicitly exempts `os.devnull`. No out-of-scope write rejection was recorded.
- Per-module raw and LF-normalized SHA256 values are recorded in `drift_map_run_a2_module_hashes.json` and individual worker runtime records.
- A post-halt source display encountered a cp1252 UnicodeEncodeError. The read was repeated with UTF-8 output. No model execution was repeated.

Committed design-note blob SHA1: `ccc2fe99ffb7e495f1168aaaffddd60f518c06a8`.

| Pinned source | Start LF SHA256 | End LF SHA256 | Committed blob SHA1 |
| --- | --- | --- | --- |
| simulation/metrics.py | 6dc16efdfd4faed1638a96f6c2af7365757d1ca47eeb86deb5619a3e580b901f | 6dc16efdfd4faed1638a96f6c2af7365757d1ca47eeb86deb5619a3e580b901f | 7e7749d99636746aa2c3215da1edaa6ab5372611 |
| simulation/agents.py | a51f6d833fa2e228aaa4e95ca59f9c7e0f83e5741c94deef88a0ea895554cfca | a51f6d833fa2e228aaa4e95ca59f9c7e0f83e5741c94deef88a0ea895554cfca | d21e5300eab6e4136141ea33aa0367b9aa47ed51 |
| simulation/model.py | 25e65d8daa4332df32198b424b25b1630d7a5aca98971c47eac82df7d5679993 | 25e65d8daa4332df32198b424b25b1630d7a5aca98971c47eac82df7d5679993 | a1cf988532203b7119462eb9b04cf2e3b0541879 |
| simulation/attack_adapter_v2.py | 5c303dc96d458eb2165416c925fa5ff526d89fdf3bb7fb5c02538bb96f7c41ee | 5c303dc96d458eb2165416c925fa5ff526d89fdf3bb7fb5c02538bb96f7c41ee | ecd9e6451065a6120e5dcb8a21b8206fb34f5e3e |
| simulation/run_attack_vector_revalidation_v2.py | 20608b2db9efc3d67b4de1e801d2d025b757ca1a16a5e280a5999a66303beb45 | 20608b2db9efc3d67b4de1e801d2d025b757ca1a16a5e280a5999a66303beb45 | ad80bd5fe60cc357a43e30c32ab3c12a758c0c2d |
| simulation/working_factor.py | 16b542ed0f322bbf87036e31e8eff82e05e6d774c75bb8c29c6947a374f33e44 | 16b542ed0f322bbf87036e31e8eff82e05e6d774c75bb8c29c6947a374f33e44 | bbfa1ea81ce8648adaf6c44a8b6f65188d206486 |
| simulation/constants_v2_stage18.py | 121a7c1c9e86d585553a2975ae27143804757a0ef344305124fcc4c802b3285b | 121a7c1c9e86d585553a2975ae27143804757a0ef344305124fcc4c802b3285b | 43b9766e63d1519faf59d1e8e4562c686a8149f2 |

## Analysis status and artifacts

No CUSUM allowance, threshold, or alarm rule was chosen or run. The pre-existing fixed-constant score was recorded with its alarm disabled, as specified. No attack-success rate or corrected figure was derived. H_ref remains a candidate and is not frozen; no candidate value was computed in this halted attempt. Nothing here is comparable to a pre-repair measurement.

No exploratory analysis was performed. The manifest enumerates every attempt 2 artifact, including partial gate logs, using LF-normalized SHA256. CSV row counts use Python csv.DictReader excluding the header. CSV-formatted partial logs are counted and explicitly labeled partial. The manifest lists itself with a null self-hash to avoid circular hashing. Prior attempt artifacts remain historical references.
