# Version 3: hash commitments

This record fixes the content of unpublished version 3 documents and outputs by their SHA-256 hashes, before the
results that could influence them are known. Each file listed here stays private until review clears it. When it is
published, it will be byte-identical to the hash below. Any later correction is published as a new, dated version,
with the original kept.

## 1. The 5 October readings and the diagnostic study (committed 2026-10-27)

**Why now:** amendment A10 was prompted by one of these readings. Fixing the write-up and the study by hash before
the corrected stage 1 reading opens shows that their presentation was set before the corrected outcomes were known.

**Already public:** the hashes of the reading outputs themselves, in amendment A10
(`simulation/diagnostics/v3_rerun_design_note.md`).

**The write-up of the registered readings.** Version 1 was written when the readings were opened. Version 2 applies
the dated corrections found by the model review panel.

| File | Bytes | Last written (UTC) | SHA-256 |
|---|---:|---|---|
| `v3_registered_readings_2026-10-05.md` | 10,083 | 2026-10-05T10:02:53Z | `d0bdd5b003a44efefa1f64df58eaaf24a4b0917841d0a52f25776c3fcddb1972` |
| `v3_registered_readings_2026-10-05_v2.md` | 12,072 | 2026-10-06T00:56:19Z | `3fb3feec808bc519b6bdc92185a554e9f0e0a526d83a78e3fcdf48fbb3f7dfa2` |

**The diagnostic study** (exploratory, run after the readings were opened). Every version of its design is listed,
from the first draft to the version it ran under.

| File | Bytes | Last written (UTC) | SHA-256 |
|---|---:|---|---|
| `v3_succession_diagnostic_study_design_DRAFT_2026-10-05.md` | 14,766 | 2026-10-05T23:08:07Z | `49b90ec717b57e483c1e8c69376475e894d546559bbe6337c94c3872d518a898` |
| `v3_succession_diagnostic_study_design_v1_approved_2026-10-05.md` | 14,837 | 2026-10-06T00:49:04Z | `b530eee71affe1ea3a79cb835e756548c183657ed4e399601ba1f2bda45b5be2` |
| `v3_succession_diagnostic_study_design_v1.1_2026-10-05.md` | 5,846 | 2026-10-06T01:38:22Z | `bdbd698e36ada6fe02a31cdaebb9e6aea155feff5122825dc66f422e3bd6e760` |
| `v3_succession_diagnostic_study_design_v1.2_2026-10-05.md` | 7,180 | 2026-10-06T01:44:52Z | `e56a5f8cce2c667ccddca0ed37a53ee42a64f71cd48a2cc6346aadf9b4e2a4f3` |
| `v3_diagnostic_phase1_report_2026-10-05.md` | 8,418 | 2026-10-06T01:33:03Z | `4a9f7cd413d50eed94c78300efd1ef9169c0120286021c80e88f8690d756ae70` |
| `v3_diagnostic_phase2_reading_DRAFT_2026-10-07.md` | 15,076 | 2026-10-07T09:57:46Z | `331473e5df8293570b73b9a95139b8c7e48e2d7ec88e3e775f272f2b37b415b8` |
| `v3_diagnostic_phase3_results_2026-10-07.md` | 7,308 | 2026-10-07T12:20:35Z | `019ad3fdd617be223c0bced3e1024866eb1daa18820c01bb5c13165b4fdd2b49` |

Each file is listed exactly as it stands, under its own name, including the phase 2 reading, whose name still
carries DRAFT.

## 2. The A10 stage 1 sealed reading (committed before it is opened)

**The seal:** `SEAL_stage1_reading.json`, SHA-256 `0662c4fca427162e49cb53f131827bd6f7d647d5d469511e8743c8978f6e220c`, written 2026-10-29T01:21:37Z, before any output was opened. The seal itself is published when the reading is.

**The readers.** Two readers, built independently, each run twice on the same registered inputs. Each reader's two runs are byte-identical, so one table per reader lists both.

**Reader A** (identity `2b70868459e1fecafcd98e3f83a78595541f49eb533ecf803bd3e18480bdf57e`): 6 files, 1,161,752,837 bytes.

| File | Bytes | SHA-256 |
|---|---:|---|
| `contributing_runs.json` | 75,713,757 | `b338ec5963f34b3fa7df2e2b1bbe24b80593a478e8dad72f22594fedb46f007a` |
| `incidence_per_run.json` | 38,373,160 | `ec47e52e7d0d438330d5cfebf3e297e7f9e64569577b9c5de461d8445bf99b4e` |
| `per_run.json` | 802,244,856 | `2221463e64bb1d6ed88edf8983622d34c678a5cc5471eaf40f63c99fdc0779ed` |
| `reading.json` | 235,426,308 | `8fd301df93023bec322f276a3aea9f234cf687807cda121b4719fb3981d6f484` |
| `sensitivity_stage1.json` | 38,061 | `fe890e34363f5057483acbed15c5d1a1b8a4403cc1fb30b1e6351ed1a759f4cb` |
| `values.json` | 9,956,695 | `a1757f96fd79ef2197109a28b98f35dc7d28e38a857f1a90e3de93dd3068b4ba` |

**Reader B** (identity `422a35b5944a0b6e6ac8973de0b9c1dbb96660e2e240f194975f6d72e0a9de7e`): 5 files, 394,966,153 bytes.

| File | Bytes | SHA-256 |
|---|---:|---|
| `contributing_runs.json` | 62,910,607 | `550d68d40ddf4df4f04f60f2a14bba283a1cfc1ad3dbbdc4dcfbeb1e9d7cfcb7` |
| `incidence_per_run.json` | 47,488,900 | `c5f73d74a03a02cd89c0ed5251b55db998f13529e81a533df514395ff9574bf0` |
| `per_run.json` | 232,023,319 | `5818b2b9794d5904e0cf827baf26e3697cfb6c19cf34f01fdc327530c51e38f3` |
| `reading.json` | 42,325,383 | `b8fd4f7059e55468b0342895d4076b5338996093719f6eaa32cfa513e251aff0` |
| `values.json` | 10,217,944 | `0b036cd2fbc4eae5130e28f73bde1f8c13f83eb894364b756bd8c2fed6ce7f59` |

**The inputs.** `inputs_with_collection.json` is the registered input with its collection contract. Reader B reads it directly. Reader A's collector built `collection_A` from it, and reader A reads that.

| File | Bytes | SHA-256 |
|---|---:|---|
| `collection_A/collection.json` | 189,363,276 | `b712f21f1f7f169d741621c055f3c8b64ba03e7baeaeea6163c7cc32ffb632a2` |
| `collection_A/databases/horizon.sqlite` | 277,741,568 | `95176d78aaa7a6bc985fea71d1a557ee709725351cc9e9ae07ef5ec6dcac8c12` |
| `collection_A/databases/k1p5.sqlite` | 579,125,248 | `3af8100b5507909031e490d1a1e1f1df07c38d9d313d9de62d2ae3ee2c2a5697` |
| `collection_A/databases/k2p3.sqlite` | 574,394,368 | `070379a0a6738ad94517fcd07e169bf6b27b72db2f99e1bfe00832ce907e97e7` |
| `collection_A/databases/main.sqlite` | 3,231,240,192 | `7c27ee81f48d3c5fdabb165972754716e6c402652feaa06e345e36731519ba6b` |
| `collection_A/databases/weight_corner.sqlite` | 2,305,769,472 | `2ed5ce7356782dbd332b0bb3573ad7bbdd211a4fcc323c1e824ea67fd94e5e85` |
| `collection_A/inputs.json` | 3,954 | `d0e260be13a0ec14c5eb1db5a0baba125859678fdf367dcc181ca36c7b28585a` |
| `inputs_with_collection.json` | | `2300bc5eb0200bf379392667942de4d341e2cb88e752b85dd719b61c9bc5aca9` |


**The blind comparison** of the two readers' values, run before anyone opened them, prints and stores counts and key names only, never a value: `blind_compare_stage1.json`, SHA-256 `30070d63200c93435b28a53504bfef3ac73c9c3a84cee51d4f3bdb55ebff651a`. It is published with the reading.
