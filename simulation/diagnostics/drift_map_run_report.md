# Drift mapping characterization: T0 halt

Execution halted because the required pre-registration is absent from the Git index and HEAD. No verified specification was available. The working-tree note was not read. No T1 gates, arm runs, model steps, or analyses were executed.

## T0 evidence

| Check | Observed result | Status |
| --- | --- | --- |
| a. Branch | main, exit 0 | PASS |
| b. Required ancestor | merge-base --is-ancestor returned exit 0 | PASS |
| c. Exact tracked-only status | Exit 0, zero stdout lines | PASS |
| d. Note indexed | ls-files --error-unmatch returned exit 1 | FAIL |
| d. Last commit C | log returned exit 0 with empty output | FAIL |
| d. C ancestry on origin/main | Not run because C was unavailable | NOT RUN |
| e. Committed note hash | cat-file returned exit 128; no blob available to hash | FAIL |
| f. Section 3 source pins | Not read because the verified committed note was unavailable | NOT RUN |

HEAD: `fd444fc22254ec24472f4bad03f8f56bf4470110`.

The failed blob retrieval reported:

```text
fatal: path 'simulation/diagnostics/drift_mapping_design_note.md' exists on disk, but not in 'HEAD'
```

The required LF-normalized design-note SHA256 is `a31c047ab1ac099a407413be259b25e9f985656da0412dcc6fe466f41668e169`. No actual SHA256 or committed blob SHA1 is available. The empty path-specific commit history also prevents the publication-ancestry check. Neither working-tree content nor a substitute specification was used.

The exact status command was `git status --porcelain --untracked-files=no`. Its stderr warning was recorded and did not cause this halt:

```text
warning: unable to access 'C:\Users\matty/.config/git/ignore': Permission denied
```

The operator-established line-ending and permission conditions were accepted without repair. Read-only Git commands used GIT_OPTIONAL_LOCKS=0. No worktree-to-blob content comparison or containment diff was performed.

## Execution record

Machine: `YOTKOTEST`. Python: `3.14.3 (tags/v3.14.3:323c59a, Feb  3 2026, 16:04:56) [MSC v.1944 64 bit (AMD64)]`. Installed NumPy: `2.4.4`, read from package metadata. No NumPy computation or simulation-module execution occurred. Workers used: 0. Arm runs: 0. Resumed seeds: none.

No CUSUM allowance, threshold, or alarm rule was chosen or run. No attack-success rate or corrected figure was derived. H_ref remains a candidate and is not frozen; it was not calculated here. No characterization result was produced, and nothing here provides a measurement comparable to pre-repair results.

Section 3 source pins could not be enumerated or verified because the committed design note was unavailable. Their initial and completion readings and their blob SHA1 values are therefore unavailable. No scientific result was used as a halt criterion.

Bytecode writes were disabled. The reporting process guarded writable opens to the drift_map_run_ artifact prefix with the explicit os.devnull exemption. The three halt artifacts were created with exclusive opens, preserving any preexisting files. The operator remains responsible for the containment diff.

The manifest records SHA256 over LF-normalized bytes, with null row counts for these non-CSV artifacts. Its self-entry has a null hash to avoid self-reference; the final manifest digest is emitted separately. Complete command evidence is in drift_map_run_halt.json.
