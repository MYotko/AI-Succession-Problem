# Standing Artifact Convention for Pre-Registered Runs

**Date:** 2026-09-19
**Status:** standing convention. It binds every pre-registration committed after this date
that governs a batch of runs. Notes committed before it keep the artifact layout they ran
under, and nothing already committed is rewritten.
**Why it exists:** the cross-vector gate committed 5,126 individual files for 720 runs, and
the drift defense committed 2,261 for 360. About three fifths of those files are process
bookkeeping rather than evidence, and the per-step logs that are evidence do not need to be
one file each once the batch has finished writing them.

---

## 1. What stays, and why

Two things are evidence and are never dropped:

- **The per-step log of every run.** It is what makes independent recomputation possible,
  and every result recorded since the detector rounds has been verified from these logs
  rather than from a run report.
- **The completion record of every run**, carrying the runner row, the arm labels, the
  seed, the end reason and the elapsed time.

Two mechanisms stay as they are during execution:

- **Per-run files while workers are running.** Fifteen processes write at once, and
  separate files avoid locking, interleaving and lost writes.
- **Resumability.** A batch interrupted by a provider usage limit resumes from completion
  records, which is how the per-vector stage A run preserved 150 completed runs on
  2026-09-17. Per-run files during execution are what make that possible.

## 2. What changes at the end of a batch

When execution is finished and nothing is writing:

1. **Merge the per-step logs** into one CSV carrying every column the per-run logs carried,
   with the arm labels and seed as leading columns, ordered by arm then seed then step.
2. **Merge the completion records** into one JSONL, one object per run, in the same order.
3. **Delete the per-run copies** of both, only after the merged files are written, verified
   by row count and by per-run hash, and recorded in the manifest.
4. **Drop the per-run process files**, meaning progress, initial and console files, or
   collapse them into a single batch journal. They are bookkeeping, not evidence.
5. **Keep gate artifacts, the executor, the analysis script, results, runs.csv, the report
   and the manifest as they are.** They are few and each is cited.

## 3. What the manifest must carry

The merge is only acceptable if a single run stays checkable afterward. The manifest
records, in addition to what it already records:

- The SHA256 on LF-normalized bytes of each merged file, and its total row count.
- Per run: the arm labels, the seed, the row count contributed to the merged log, and the
  SHA256 of that run's rows as they were written before the merge.
- The count of per-run files deleted, by kind.

A run whose rows cannot be recovered from the merged file by filtering on its arm and seed
is a failed merge, which halts before any deletion.

## 4. What this is not

- It is not a change to any recorded result, and it rewrites no committed artifact.
- It is not a license to record less. Every quantity a note registers must remain
  recomputable from the merged log by a reader who has only this repository.
- It is not compression. The merged files stay plain text, because auditability is the
  reason the logs exist at all.

## 5. How a note adopts it

A pre-registration adopts this convention by citing it in its execution bounds section and
naming its own merged filenames. A note that needs to depart from it says so and why,
before any run.
