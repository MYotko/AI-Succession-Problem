# Degenerate entropy exposure across the v2.0 layer: corpus read

## Task 0: HALT, primary corpus availability unresolved

The requested corpus enumeration cannot be completed on this clone. The three Phase B results CSVs explicitly named in the committed integration document are absent from the working tree, HEAD, and the evidence tag. No Phase B or phi characterization manifest was found in the repository searches described below. This is an input-availability anomaly, not a finding that entropy series were never persisted.

The precondition gate passed. The halt occurs during Task 0, before CSV row counting, column inspection, or any statistical analysis. Tasks 1 through 4 were not performed. The operator's instruction to stop on any anomaly governs this outcome.

Scope: post hoc analysis of an existing evidence corpus. No hypothesis about the framework is under test. Outputs are not registered characterization data.

### Manifest and provenance discovery

| Requested group | Primary enumeration record found | Status |
| --- | --- | --- |
| Attack-vector v2.0 revalidation | `HEAD:simulation/diagnostics/attack_vector_revalidation_manifest.md` | Available. Lines 3-7 designate the evidence tag and authoritative list; lines 24-39 enumerate vector/run-directory entries and blob hashes. The report did not proceed to resolve and read their CSVs after the Task 0 anomaly. |
| Phase B, including Category A | No separate manifest found. `HEAD:simulation/diagnostics/phase_b_integration_analysis.md:12-17` explicitly lists source files. | This document was used to locate the exact primary inputs, not to substitute its reported results for data. All three listed results CSVs are unavailable at the checked locations. |
| Phi characterization | No manifest found. `HEAD:simulation/diagnostics/phi_investigation_synthesis_draft.md:49` names `simulation/diagnostics/phi_mechanism_followup_results.csv` as underlying data for specified comparisons. | A synthesis draft is not an established complete authoritative manifest. Full input membership remains unresolved. The named CSV was not opened or checked after the Phase B availability anomaly was confirmed. |

Manifest discovery used `git ls-tree -r --name-only` for HEAD and the evidence tag, selecting manifest-named paths for inspection. A working-tree filename search with `rg --files --hidden --no-ignore` for manifest names also found no Phase B or phi manifest. These were searches for provenance records, not globs selecting results CSVs. A targeted document search located the explicit Phase B source list and the phi synthesis reference. No CSV population was assembled by glob or prefix.

The attack-vector manifest explicitly excludes smoke and pilot runs and requires reads from pinned Git blobs. Its prose row totals and hashes were read only as manifest declarations. They were not counted or verified in this halted corpus read.

### Exact missing Phase B paths

The source-data list is at [phase_b_integration_analysis.md, line 12](phase_b_integration_analysis.md#L12), with Category A at line 13, Category B at line 14, and Category C at line 15. Line numbers refer to HEAD `1261c9f430411b9fa0060a7384bf4ec5175e4f4e`.

| Exact path | Working-tree file | HEAD object | Evidence-tag object |
| --- | --- | --- | --- |
| `simulation/diagnostics/monte_carlo_phase_b_a_results.csv` | Absent | Absent, exit 128 | Absent, exit 128 |
| `simulation/diagnostics/monte_carlo_phase_b_b_results.csv` | Absent | Absent, exit 128 | Absent, exit 128 |
| `simulation/diagnostics/monte_carlo_phase_b_c_results.csv` | Absent | Absent, exit 128 | Absent, exit 128 |
| `simulation/diagnostics/monte_carlo_phase_b_summary.md` | Absent | Absent, exit 128 | Absent, exit 128 |

Working-tree availability was checked with Python `Path.is_file()`. Git-object availability was checked with `git cat-file -e <ref>:<exact-path>`. Each absent object returned the explicit message `fatal: path '<exact-path>' does not exist in '<ref>'`. The initial attempt to read the combined Phase B summary with `git show HEAD:<exact-path>` also returned exit 128. Subsequent exact-path existence checks established that this was missing content at the named locations.

The integration document's reported row totals were not adopted as counted values. No substitute paths were inferred, no absent artifacts were reconstructed, and no simulation was run.

### Column availability and limits

- CSV row counts: not counted in this attempt because Task 0 halted before CSV reads.
- Full CSV column lists: not inspected.
- Recorded H_N or H_eff availability, suppression or constraint availability, and per-step versus per-run granularity: unresolved for the requested corpus enumeration.
- Whether per-step novelty or entropy was ever persisted: cannot be established from these missing inputs. Absence from this clone and the checked refs is not proof of non-persistence elsewhere.

The expected valid outcome of a readable CSV lacking entropy columns is different from the present anomaly: the required primary corpus and its complete manifest selection cannot yet be established.

## Precondition gate

All three checks passed before corpus discovery.

| Check | Read-only evidence | Result |
| --- | --- | --- |
| HEAD | `git rev-parse HEAD`, exit 0: `1261c9f430411b9fa0060a7384bf4ec5175e4f4e` | PASS |
| Evidence tag | `git rev-parse attack-v2-revalidation-evidence^{}`, exit 0: `6d33c905db18842f68e59b4148f65c5e6a1a62a3` | PASS |
| Root advisor present and absent from index | Python `Path('LINEAGE_IMPERATIVE_ADVISOR.md').is_file()` returned true; `git ls-files --error-unmatch -- LINEAGE_IMPERATIVE_ADVISOR.md` returned exit 1, empty stdout, and the expected pathspec-not-indexed message | PASS |

The advisor index check's exit 1 is the required negative result and is not the halt cause.

## Tasks 1 through 4: not reached

Task 1 distributions and joint frequencies were not computed. Task 2 source derivations and empirical limit behavior were not investigated in this attempt. Task 3 source tracing and empirical downstream relationships were not performed. Task 4 exposure across Phase B and phi grids cannot be addressed from the inputs established in this attempt. No conclusion about effects on the reported phase boundaries or phi differential follows from this availability halt.

Previously discussed source findings were not substituted for corpus measurements. No counterfactual U_sys calculation was performed.

## Execution and write scope

Machine: YOTKOTEST. Workspace: `C:\users\matty\Dev\AI-Succession-Problem`.

Report time in UTC: 2026-09-08T00:19:49.050135+00:00.

Only `simulation/diagnostics/cusum_char_corpus_report.md` was written. No simulation runs, production edits, repairs, Git write operations, or containment diff were performed. The operator retains the containment diff. All `cusum_char_` artifacts are excluded from the authoritative manifest by prefix and are not authoritative corpus inputs.

Resumption requires the operator to identify or place the authoritative Phase B and phi manifests and their referenced primary data in readable locations. Nothing was fetched, generated, or repaired to supply those inputs. This report records the halt and makes no replacement corpus selection.
