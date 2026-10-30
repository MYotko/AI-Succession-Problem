# Amendment A16: blind certification record (2026-10-29, final)

**Candidate for adoption:** `AMENDMENT_A16_DRAFT_v2_5.md`, SHA-256 `ea1d9a12a8de96dcbcb61cc5b7761a3a99297228400ad2411943c2d2ad2e0293` (v2.4, `f98d1539cc3fd98ee368af81d605390fc483c3bbd2cf883e6cc27e8c6f1dd6cc`, certified in round 4; v2.5 is v2.4 with seven numeric-range en dashes replaced by "to" and its two companion hashes rebound to the punctuation-cleaned companions, certified in round 5). **Budget companion:** `AMENDMENT_A15_DRAFT_v3.md`, SHA-256 `7a9a203b5d994752dfe8c59a8c6839fd4604dad7736f81ad5c3e3ec3bc7c0017`. **Incorporated by name, to be committed with A16:** the punctuation-cleaned copies, committed under the names the amendments cite: `STAGE2_READER_REQUIREMENTS.public.md` (`685f05ec58cb2bb84914163de57107ee4f3e557650d7717e1c1a2e8be56a52d5`, the cleaned `STAGE2_READER_REQUIREMENTS.public_v2.md`), `A16_FEASIBILITY.public.md` (`1f0c1b052b93717130bf7d5f93a7489577625d27ccb6c512c3364c1d0ba5909d`, the cleaned `A16_FEASIBILITY.public_v2.md`), `STAGE2_PLAN.public_v2.md` (`f1712c6798d593f40c864ec421a491dfcb5d6098d1275b6d28bf27c0528e680a`, the cleaned `STAGE2_PLAN.public_v3.md`, whose one machine-name filename became a description), `REQUALIFICATION_PLAN.public_v2.md` (`8c0b6a73465b64591c49fa5f47bee87f611922895559709dd3d419015726bf86`, the cleaned `REQUALIFICATION_PLAN.public_v3.md`). The pre-cleaning hashes were `f4280eea…`, `182a111c…`, `43354c0d…` and `e0c3091b…`; every difference is a dash replaced by "to", a comma, a colon or a full stop, plus that one filename (interpreter's byte comparison, confirmed by Claude in round 5 for the two A16-bound files).

**Who did what.** Drafted by the executor (Codex, session `01a187d7`, gpt-6-astra), blind to stage 1's scientific results, from a brief by the interpreter (Claude, this session), who proposed the procedure knowing those results; the operator decided the labels interpretation, path (a) and X2-1 only on 2026-10-29, knowing them too. Certified over five rounds by two certifiers from different model families, each a fresh instance given only an allowlisted packet, blind to each other and to stage 1's results: **Claude** (Fable 5.1, a fresh agent per round, reading code in a clean worktree at `c217cc7d`) and **Gemini 4 Argon** (via agy, file viewer only, reading code at the same commit). The author's model family (OpenAI) was not a certifier.

## The rounds
| Round | Candidate | Claude | Gemini | Reconciliation | Result |
|---|---|---|---|---|---|
| 1 | v2.1 (`b2ae95e5…`) | certify with required repairs: 3 required (projection binding in item 5; anchor as sibling record; heading), 10 recommended | certify with required repairs: 3 required (name `_truncated_sha` and its preimage; "intended R4 pairing"; commit the incorporated files), 6 recommended | `RECONCILIATION_round1.md`: all adopted; Gemini's G1 premise (a second `artifacts._truncated_sha`) recorded as false | v2.2 (`8b23ccbc…`) |
| 2 | v2.2 | certify with required repairs: 1 required (the false symbol carried into the text), 6 recommended | certify with required repairs: 2 required (the same false symbol; anchor lifecycle and sentence order), 2 recommended | `RECONCILIATION_round2.md`: all adopted; the false-symbol adoption recorded as an interpreter miss | v2.3 (`b7c3487e…`) |
| 3 | v2.3 | certify with required repairs: 1 required (the drafter's line 90 edit mangled), 2 recommended | certify with required repairs: the same 1 required, 0 recommended | `RECONCILIATION_round3.md`: adopted; exact bytes supplied in `LINE90_v2_4.txt`; a second interpreter miss on that line recorded | v2.4 (`f98d1539…`), 3 lines changed |
| 4 | v2.4 | **certify**, no required repairs, 1 non-blocking recommendation (an implementation hazard for the successor build) | **certify**, no required repairs, no text recommendations; one adoption-record note (confirm the packet hashes on disk, since its tool could not hash) | none needed | **certified**: both certifiers, no required repairs |
| 5 | v2.5 (punctuation only) | **certify**, no required repairs; three adoption-record observations (plan-copy version names; the phrase "fire rate" in two companions, which the site checker refuses but which never passes through it; no trailing newline on the plan copy) | **certify**, no required repairs; the same note that the plan copies' predecessors were not in the packet, so their comparison rests on the interpreter's | none needed | **certified**: both certifiers, no required repairs. v2.5 is the certified text |

## The punctuation pass (after round 4)
The interpreter found, before adoption, that the design note has never carried an em or en dash in 2,645 lines and that the public plan copy named a load-sheet file by a filename containing a machine name. The executor made a punctuation-only pass under written rules (`PROMPT_A16v2_5_punctuation_2026-10-29.md`, `REPORT_9.md`), and round 5 certified it.

## Diffs for the adoption record
- v2.1 to v2.2: `REPORT_6.md` change ledger (23 lines replaced).
- v2.2 to v2.3: `REPORT_7.md` (10 lines replaced; one of them, line 90, defective).
- v2.3 to v2.4: `REPORT_8.md` (lines 1, 90 and 128 only; verified independently by the interpreter and by both certifiers' byte comparison in the packet).
- v2.4 to v2.5: `REPORT_9.md` (lines 1, 25, 34, 74, 78 and 157 only).
- v2.5 to the adopted text: `adoption/ADOPTION_DIFFS.md` (the heading and the status paragraph only, for A16 and for A15 alike).

## Packet-transfer notes
- Gemini's tool copies only `.md` files, so `LINE90_v2_4.txt` was absent from its round 4 directory; it verified line 90 against the reconciliations and the code instead. Both certifiers recorded the bundle's own hash for the transfer record (`1d705ff7…` for v5); the interpreter's on-disk hash checks are in the session log.

## Carried to the successor build and the adoption record, not to the text
- Claude round 4 RC1: the anchor's reservation-time code identity is historical; the current identity is the rebound plan's; the step 3 rehearsal includes a repeated preparation at a changed identity after a logged tooling failure.
- Claude round 3 RC2: this record carries the diffs above.
- The pre-adoption metadata check of the four publication targets (paths clause item 3) was run on the execution host on 2026-10-29 before adoption, by metadata only: no `a10_stage2` path exists under any checkout there, and no frozen manifest under the stage 1 roots names one. Passed.
- The P2 projection's strata for every stage 2 family and capability are checked on the execution host before any extension pricing (certifiers could not open the projection; item 5 makes an absent stratum a finding).

## Misses recorded against the interpreter
1. Round 1: adopted Gemini's G1 replacement verbatim although its premise was recorded false, carrying a nonexistent symbol into the text.
2. v2.3 verification: checked that the symbol was gone, not that the sentence parsed.

## Packets
`cert_packet_r1/` (14 files, bundle v2 added), `cert_packet_r2/` (18, bundle v3), `cert_packet_r3/` (19, bundle v4), `cert_packet/` (22, bundle v5, round 4). Certifier reports: `cert_r{1..4}_{claude,gemini}.md`. Prompts: `cert_prompt_A16.md`, `_r2`, `_r3`, `_r4`.
