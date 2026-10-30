# Site update: a defect in the simulation, its correction, and the corrected test

**Draft for lineageimperative.org. Date: 2026-10-27.**

> **Correction, 2026-10-29.** This update is kept as published on 27 October. Records correct the statements below.
>
> - **"registered as an amendment before any run under it"** (Summary), **"registered on 8 October, before any run under
>   it"** (In brief) and **"before any table, run or output under it existed"** (The correction). Amendment A10 records that
>   no registered table, run or output existed when it was written. An exploratory check of the corrected mechanics ran on
>   7 October, and a cost-only pilot of 77 jobs ran the corrected code on 8 October. Neither was registered, and the pilot
>   exported no outcome. Record: `simulation/diagnostics/v3_rerun_design_note.md`, Amendment A10, "Timing and status" and item 12.
> - **"before any stage 1 output existed"** (The sealed reading). When amendment A12 was written, stage 1's table estimation
>   was complete and assembled. No stage 1 run had started, and no output had been read. Record: `simulation/diagnostics/v3_rerun_design_note.md`, Amendment A12
>   part 1, "Timing and status".
> - **"its sealed reading is under way now"** (Summary), **"Its sealed reading is running now"** (In brief) and **"The sealed
>   reading, now running"**. The reading has completed. Its outputs were sealed on 29 October at 01:21 UTC, and their hashes were published
>   before it was opened later that day. Record: `docs/v3_hash_commitments.md`, Section 2.

*Summary: The registered version 3 reruns were read on 5 October. One reading did not look the way the design
said it should, and tracing it found a defect in the simulation itself: it measured the pace of change as a level,
and gave capability no benefit, so handing over to a more capable successor could only ever cost something. The
correction was registered as an amendment before any run under it. The corrected study's first stage has run, and
its sealed reading is under way now. The 5 October results stay unpublished until outside review clears them, and
will then be published beside the corrected results, not replaced by them.*

---

> ### IN BRIEF
>
> - **The 5 October readings** of the registered reruns are with outside reviewers. Nothing from them is published
>   yet.
> - **A defect, found because of one of them:** the simulation measured the frontier's level instead of its pace,
>   and gave a more capable AI no benefit. Its succession test could not measure what it was built to measure.
> - **The correction, amendment A10,** was registered on 8 October, before any run under it. Because a registered
>   result prompted it, it will be reported as outcome-informed, as its own class of evidence.
> - **Stage 1 of the corrected study is run:** its tables published on 22 October, and all 53,100 registered runs
>   complete on 25 October.
> - **Its sealed reading is running now,** by two readers built independently of each other.
> - **Fixed by hash today:** the write-up of the 5 October results and the diagnostic study, before the corrected
>   results are known.
> - **New essay:** Who Holds the Switch.

## The 5 October readings

The registered reruns and sensitivity runs described in the last update were read on 5 October, as
pre-registered. Their results have not been published. They are with outside reviewers, and will be published with
their evidence once the review clears them.

One of those readings, on succession, did not look the way the design said it should. Tracing why found a defect in
the simulation itself. Had that reading looked as expected, nobody would have examined the part of the simulation
that turned out to be wrong. That is why the correction below is labeled the way it is.

## The defect

The framework's lineage factor, Θ, discounts change that outpaces what people can absorb. To compute it, the
simulation needs two things: how fast the frontier is moving, and what a more capable AI adds. It got both wrong.
- **It measured the frontier's level, not its pace.** The level is never zero while there is any capability and any
  technology, so even a system that never changed paid a penalty at every step. Θ never reached the value the
  specification says it takes when nothing is changing.
- **It gave capability no benefit.** A more capable AI did no more useful computation and produced no more welfare.

Together, these meant that handing over to a more capable successor always carried a lasting penalty and never a
gain. The succession comparison could not measure what it was designed to measure.

**How it got in.** The level was chosen during the build, on 27 September, to settle a point the specification
left open, and it was reviewed and accepted. It then passed every certification and every gate, because those
checks tested the properties the specification states, and a level satisfies all of them. None of them asked
whether a stable system can ever reach Θ = 1, or whether a modestly more capable successor can ever be preferred.
Both are now checks.

## The correction, and how to check it was kept

[Amendment A10](https://github.com/MYotko/AI-Succession-Problem/blob/main/simulation/diagnostics/v3_rerun_design_note.md)
was written on 7 October and registered on 8 October, before any table, run or output under it existed.
- **Frontier velocity is a pace:** how fast the frontier grows, measured over one human generation in the model.
- **Capability's benefit** enters only through computation and welfare production, the two channels named before
  any rerun. Nothing credits a more capable AI with lower extinction risk.
- **The absorption rate** is anchored to measured historical rates at which output per hour has grown, with two
  alternative anchors tested beside it.

It carries commitments a reader can check against the published results:
1. **No value was set by looking at an outcome of the runs,** or at any margin.
2. **Nothing changes if the results disappoint.** If the corrected results are not as predicted, no value is
   adjusted in response. Any further change would be a new amendment, stating that it follows these results.
3. **The 5 October results stand.** They are not re-read, re-scored or withdrawn, and they will be published beside
   the corrected results.
4. **The predictions were registered first,** before any corrected run.
5. **Outcome-informed work is labeled as such.** A10 was prompted by a registered result, so the paper will report
   it as outcome-informed, separately from what was fully registered in advance. The same label applies to one
   later rule: an admission rule in amendment A13, written after a validation step refused and with some outcome
   information in hand, all of it disclosed in the amendment.
6. **The presentation is fixed before the corrected results are seen.** This update's commit publishes the
   [hashes](https://github.com/MYotko/AI-Succession-Problem/blob/main/docs/v3_hash_commitments.md) of the
   write-up of the 5 October results and of the diagnostic study that found the defect, every version of each.
   When they are published, each file will match its hash, and any later correction will be a new, dated version.
   Before the stage 1 reading is opened, the hashes of its sealed outputs will be added the same way.

## Stage 1, run

- **The tables** were estimated on 9 October and then validated. Twice their publication was refused by the
  registered rule, because some table rows could not be estimated precisely enough. Each time, a bounded extension
  was registered before it ran, stating what was known when it was written: amendment A13 on 16 October, and A14 on
  20 October, declared the final round. The tables passed and were published on 22 October.
- **The runs:** 53,100 registered runs across five families. They cover the corrected main study, the two
  alternative absorption anchors, the weighting corners and a longer horizon. All were complete on 25 October;
  every nondeterminism recheck matched, and no run halted.
- **The machinery:** amendment A11 lets one registered launch run across several machines, with the exact code
  pinned on each.

## The sealed reading, now running

The reading was specified in amendment A12 on 11 October, before any stage 1 output existed. Its rules were mapped
twice, independently. Then two readers were built from the draft text without seeing each other's code, and tested
on non-registered data generated by the instrument's own code until they agreed on every shared value.
- **Both readers now run twice** on the same registered inputs. Each reader's two runs must match byte for byte.
- **A blind comparison** then checks the two readers' values against each other, by name, without displaying them.
- **The outputs are sealed,** and their hashes are published before anyone opens them.

Preparing the reading surfaced several problems, and each was fixed before any result was computed:
- **The readers refused to start** several times, on mismatches between their inputs and the registered records.
  Each fix was approved and recorded.
- **One conflict inside the instrument's own checks:** a succession at the capability ceiling cannot show the
  strict increase that one check requires. It was decided before any stage 1 result existed: the corrected check
  governs, and the literal one is reported beside it.

The reading takes about two days, most of it in the instrument's own checks, which verify every output again on
each pass.

## Review

- **A panel of three AI models** (Gemini 3.1 Pro, gpt-oss-120b and Mistral Small 4) reviewed the 5 October results.
  The write-up's version 2 applies the corrections they found.
- **Invited human reviewers** began an adversarial review on 9 October, of the 5 October results package.
- **Three more AI model reviews** (Argon, Astra and Qwen3.8-Flash-Next), of a complete written statement
  of the project, were compared on 19 October. None found anything that changes stage 1. Their common findings
  were that A10 and the A13 admission rule must be reported as outcome-informed, as above, and that some older
  public documents still state superseded claims.

## Also new

- **Essay:** [Who Holds the Switch](https://yotko.substack.com/p/who-holds-the-switch), published 12 October.

## What comes next

- **The stage 1 reading completes,** is sealed, and its hashes are published. Then it is opened and read.
- **The results go to review,** the 5 October results and the corrected ones together, and are published once
  cleared.
- **Stage 2** runs the rest of the registered sensitivity work on the corrected instrument: the alternative form of
  capability's benefit, and the earlier variant families.
- **Dated corrections** to the older public documents that still state superseded claims.
- **The v2.0 paper** stays under its status notice, and the arXiv upload waits for version 3.
