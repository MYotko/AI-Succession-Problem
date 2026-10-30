# A17 adoption commit plan, 2026-10-30

**One operator commit; nothing has been committed or executed by this staging task.** The parent inspected is `50a3d096c9b04863938624b41727dde1e269a187`. Preserve all existing design-note bytes and append the staged amendment after A16's final line, currently line 2930: "- A15's ceilings remain budgets, never quantities or predictions. This amendment creates no budget by itself and no automatic launch go." Add one blank separating line, then the amendment heading at line 2932. The inspected exact-byte design-note SHA-256 is `77bdf5fcc7a8b1a39c7202d158794168ce8c1236ec7c42c3c6540410f9411b26`; if its append boundary has moved, reconcile the append location without changing existing registered text.

## Exact staged-to-committed mapping

| Staged file under adoption_a17 | Commit action/target |
|---|---|
| `AMENDMENT_A17_adopted.md` | Append to `simulation/diagnostics/v3_rerun_design_note.md`; do not add a duplicate standalone amendment file |
| `A17_HOSTS_FEASIBILITY.public.md` | Add `simulation/diagnostics/a17/A17_HOSTS_FEASIBILITY.public.md` |
| `A17_CERTIFICATION_RECORD.md` | Add `simulation/diagnostics/a17/A17_CERTIFICATION_RECORD.md` |
| `ADOPTION_DIFFS.md` | Add `simulation/diagnostics/a17/ADOPTION_DIFFS.md` |
| `A17_COMMIT_PLAN.md` | Add `simulation/diagnostics/a17/A17_COMMIT_PLAN.md` |
| `host_register/X2-1.json` | Add `simulation/v3/runs/registered/host_register/X2-1.json` |
| `host_register/README.md` | Add `simulation/v3/runs/registered/host_register/README.md` |

The register path is the proposed public registered-record location, outside the source manifest's executable inputs. Only these seven target files change. Do not add operational source evidence, certifier-session private paths, raw fingerprints, source views, samples, outputs, temporary document tooling, or `REPORT_14.md` to the repository as part of this commit. Keep the exact certified candidates and reports in the operational archive with their hashes.

Proposed commit message, with no attribution lines:

```text
Adopt A17 host register and initial X2-1 compute record
```

## Three values the interpreter supplies

1. **Adoption commit.** The labeled adoption-commit slot in the amendment is `<commit>`. Resolve it to the resulting full commit hash in the external adoption/execution record after the commit is created. A Git commit cannot contain its own final hash: keep this slot as an external-reference placeholder in the committed note rather than inventing a hash, iteratively amending the commit or adding an unrequested second commit.
2. **Commit-time knowledge and intervening-observation note.** Replace the separately labeled `<commit>` on the adoption bullet with the interpreter's factual statement at commit. It must disclose the operator/interpreter's knowledge and any intervening observations; the drafter cannot supply that future fact. Keep the executor's blindness sentence unchanged. This is the only in-note pending fact to fill before the commit.
3. **External operator-approval reference.** Fill `X2-1.json`'s `operator_approval.reference` and replace its pending-reason wording with the corresponding factual approval metadata when approved. The external record must bind payload digest `59f1fd7417e669b1a2d2c7d5202424299cce96a82042aca7df98340e73658192` and explicitly limit this approval to the initial metadata entry; acceptance and launch gos remain separate. No pending qualification may be marked accepted to complete adoption.

Items 1 and 2 use the exact placeholder spelling requested for the staged note; their labels distinguish them. Item 3 is null with a reason, as required for an unavailable registry value. A reference identifier chosen for the external approval before the commit can later bind the resulting commit hash without creating a self-hash cycle. Do not insert the resulting commit hash into the already committed bytes. These are metadata completions, not new scientific or budget decisions.

## Before the operator commits

Verify the certified v4 candidate hashes and the staged diffs. Fill the knowledge note and external approval reference, preserving every other certified byte except the enumerated adoption edits. Recompute the adopted amendment, registry envelope and affected documentation exact-file hashes and regenerate `ADOPTION_DIFFS.md` for the completed metadata. Verify the payload seal independently; changing only external approval metadata must leave it `59f1fd7417e669b1a2d2c7d5202424299cce96a82042aca7df98340e73658192`. If the payload needs another factual change, reseal it and obtain approval of that new digest rather than silently mutating this payload.

Review the final diff as a note append plus the six new record/document files above. The inspected register targets are not ignored by repository rules. Make the single commit with the proposed message, then record the resulting commit hash, final file hashes and approval receipt externally. Do not claim the hashes of these placeholder-bearing staged files are the final committed hashes after a field is filled.

This is a record-only adoption: no source edits, requalification, configuration tests, simulations, replay, phase 2 build, launch, publication or reading is included. The post-update pass remains pending, the recorded sample needs the preparation report's harness repairs/refreeze before use, and the future successor still requires its own proofs. A17's section 6 pins are implemented in the later authorized source build; they are not silently changed in this adoption commit.
