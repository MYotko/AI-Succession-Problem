# Amendment A17: blind certification record (2026-10-30, staged adoption)

**Candidate for adoption:** `AMENDMENT_A17_DRAFT_v4.md`, SHA-256 `bde2be0bf60d59e155b9ae13976c88a3d2b79079ba24adb70054b3b7710c65e2`. **Certified companion:** `A17_HOSTS_FEASIBILITY_v4.md`, SHA-256 `93c15d35d41e3d22a4f2cfab2a4b81b6555ed004f76e9a8808367fc7a21b2626`. Round 3 certified both with no required repairs. The companion is committed as `simulation/diagnostics/a17/A17_HOSTS_FEASIBILITY.public.md`, SHA-256 `d73ad3f61958cc6b1cbcfd29836f6eccd9eecd6ee0d969a7efd05aac58e570b0`, with only its heading changed to identify the adopted companion. The amendment's authorized adoption edits are enumerated in `ADOPTION_DIFFS.md`; the staged text is an append to the design note, not a claim that this executor committed it.

**Who did what.** The executor drafted blind to stage 1's scientific outcomes. The operator and interpreter knew the opened stage 1 reading, commissioned this text knowing those results and selected option C on 2026-10-30 before any stage 2 output existed as stated in their decision. The operational measurement and cost arithmetic informed the compute decision. Drafter blindness does not make the commissioning or adoption decision blind. The exact executor statement is unchanged in the adopted text. The commit-time knowledge and intervening-observation note is left to the interpreter in that text.

Two certifiers from different model families reviewed each round, blind to each other and to stage 1 scientific results. Round 1 used a fresh **Claude Fable 5.1** agent (Anthropic) and a fresh read-only **Codex gpt-6-astra** session (OpenAI), separate from the drafter's session, after **Gemini 4 Argon** returned a quota error (429). Gemini supplied no certification. Rounds 2 and 3 used the same two model families in fresh instances. The Claude reports identify Fable 5.1; the Codex round 2 and 3 reports identify the OpenAI GPT-6 family without a narrower model identifier, so this record does not invent one. Fresh-instance provenance and the round 1 model identifier are supplied by the operator's staging brief. OpenAI is also the drafter's model family; session separation is disclosed, not misrepresented as a third family.

## Rounds

| Round | Candidate pair | Claude Fable 5.1, Anthropic | Codex, OpenAI GPT-6 family | Disposition/result |
|---|---|---|---|---|
| 1 | Amendment v2 and companion v2 | Certify with required repairs: four required repairs | Certify with required repairs: two required repairs | `RECONCILIATION_A17_round1.md`: adopt all six repairs, fifteen recommendations and option C items 16 to 18; produce v3 |
| 2 | Amendment v3 and companion v3 | Certify; no required repairs; wording recommendations | Certify; no required repairs; two wording recommendations | Interpreter authorizes the nine-item wording pass; produce v4 |
| 3 | Amendment v4 and companion v4 | Certify; no required repairs; non-blocking editorial recommendations | Certify; no required repairs; companion-filename recommendation | Certified v4 pair; only expressly authorized adoption edits are staged |

## Exact candidate and report hashes

| Round | File | SHA-256 |
|---|---|---|
| 1 | `AMENDMENT_A17_DRAFT_v2.md` | `1cea4361045288763ca67352b2da589c3e9383ed553a94491979609927be52ad` |
| 1 | `A17_HOSTS_FEASIBILITY_v2.md` | `ac70f9d81633e62ff0ac802c21a8b93a48a4f2a3d9f3d0b6c1cdd9825ea8752c` |
| 2 | `AMENDMENT_A17_DRAFT_v3.md` | `ef2a3fa33aba98202b93d32369bed7b936964aad906eb93ce31f2bde70b16f52` |
| 2 | `A17_HOSTS_FEASIBILITY_v3.md` | `1d47e8e7ebe75965863c3dc8a2d770bbfbb1e2404eb9f1106fcb2d73741bc761` |
| 3 | `AMENDMENT_A17_DRAFT_v4.md` | `bde2be0bf60d59e155b9ae13976c88a3d2b79079ba24adb70054b3b7710c65e2` |
| 3 | `A17_HOSTS_FEASIBILITY_v4.md` | `93c15d35d41e3d22a4f2cfab2a4b81b6555ed004f76e9a8808367fc7a21b2626` |
| 1 | `cert_a17_r1_claude.md` | `d12f9da328bc3c98d7976ef7f02a4ee0a4181a74ab7717f9799425fa07a975f7` |
| 1 | `cert_a17_r1_codex.md` | `b6e88bb2e69c1fd64cee436d6e6e70b0bbcd4ac6db55c32f160875b44ec0d663` |
| 2 | `cert_a17_r2_claude.md` | `2c9cdd2dd9c98c35ba72fde778f6622e166aab0efeb197945aa31512025c89c1` |
| 2 | `cert_a17_r2_codex.md` | `d07796434c8cb79e85d3da274ff2d0cd439abe60c4875a5a17f072f449c95dba` |
| 3 | `cert_a17_r3_claude.md` | `30bed19e161cc647d52a55b29d2687bb61cd937b422e6bc1e4669b98cacee29d` |
| 3 | `cert_a17_r3_codex.md` | `14e7c4e3f4f338dda083ab4edb35ce74699188404d1dbc96a0c9f5b02c27aca7` |

| Process record | SHA-256 |
|---|---|
| `RECONCILIATION_A17_round1.md` | `15a6bb16d1ca4f63e3ca9314bc98669bc3b856b986766c4f61f2564ab66cb68c` |
| `DECISIONS_2026-10-30.md` | `e96673c11320476c5b0b0dbbc0bf03695e0207777ba2c5e94b15487abdd2f553` |
| `PROMPT_A17v4_wording_2026-10-30.md` | `cdf6c6ec38a62404b46424cc24f3b9fe02ab1c553418971957f5bbc9b4b17ef2` |
| `REPORT_11.md` | `cfcac61e184a7732ef2d7022bad951f698d389074c1384339e42bf4bb2c0ae85` |
| `REPORT_12.md` | `0307cff6e5f00dddf19d42ccef61390b168eb0849eca4e897c88e905c7cad4d9` |
| `REPORT_13.md` | `a19617c024e36685c379698c8d261beb656e8a7b249f37caf8a76a19631665d2` |
| `CERTIFICATION_BUNDLE_A17_v2.md` | `6a0209175d6c74b8785be593293416eeed30b6e6011cf8306a24b243c0d8e190` |
| `CERTIFICATION_BUNDLE_A17_v3.md` | `36d653455cb9c5f7a9f9ef52daa237014780219ed571410869b8bd80cb2152ce` |
| `CERTIFICATION_BUNDLE_A17_v4.md` | `4a76e8ec23eb9dcded7e649e475c3ec1603ba1d53c6b0ebe031e3ef4e44fc339` |

## Dispositions and operator decision

Round 1's six required repairs cover fail-closed no-control invocation; distinct agreement to resource sharing and to service control plus harness/action-entry enforcement; candidate-host-only fixed-code failure consequences; separation of budget selection from owner consent; X2-1's obligation to satisfy the four gates; and the A11 recheck on an admitted host other than the original producer. The reconciliation adopts each exact replacement, including both compatible service-control texts on the same line.

Recommendations 1 to 15 add the fourth service-instruction supersession, direct-transport register coverage, dated subset addenda, numeric future-state ceiling proposals, unchanged-ceiling release-cost wording, phase/transport definitions, explicit launch charging, precise blindness scope, retained historical pin binding, denial of historical supervisor authority, per-kind final validation, portable source hashes, historical reading of prior decisions, distinct wall stops, and sealed-payload/external-approval hashing. `REPORT_12.md` records every landing.

Option C items 16 to 18 retain this campaign on X2-1 only in Performance mode, leave X2-2 and its service untouched, make the X2-2 entry a worked example with no admission/pass/budget decision, and move class-aware placement, coordinator register enforcement and A16 pull transport to the identity serving the first multi-host launch, before that identity's own direct A11 proofs. Current single-host safety, pin, validator, rehearsal and proof obligations remain. No host, scientific quantity, qualification or budget is accepted by a text certification.

The round 2 wording pass aligns the commissioning disclosure with option C, makes the initial-entry commit deadline explicit, repeats the supervisor denial in the normative service clause, corrects the description of maintenance inputs, aligns companion timing/failure/charging summaries, and adds timing tags without changing table words. **Interpreter amendment of verbatim round 1 text:** wording-pass item 4 changes only "the X2-2 prerequisite harness" to "any future host's prerequisite harness". This broadens the named review coverage; the required property and before-pass timing stay fixed. The disclosure and exact diff are in `REPORT_13.md`, and both round 3 certifiers checked it.

## Recommendations not applied, or resolved at adoption

- Round 1 Claude recommendation 13 concerns private locations in the operational interference write-up. It was not adopted into the amendment: the evidence record stays outside the public adoption text. Public staging cites only stable descriptions and hashes.
- The `GUPPI` session-name observation remains the operator's public naming choice. It names an owning session, not a personal user or a host, and grants no service-control permission. The certified bytes are retained.
- The optional relocation of the worked example's alias imperative was not adopted; the normative snapshot/input rules already protect it. The optional section 5 first-paragraph pointer refinement is also left unchanged because the existing references resolve and this staging permits only the enumerated edits.
- The companion's line 188 direct/pull tag split is an editorial clarification, not a deferred direct-proof obligation. The governing amendment and companion timing clauses preserve phase 2's direct-transport proof. No split is applied: the user authorized the companion heading change only.
- Both round 3 reports identify the old companion filename. Adoption replaces both references with the committed public path and binds the adopted companion's hash.
- Claude's draft/adopted-tense observation is resolved by completing the status for adoption; the already certified commissioning sentence is not rewritten.
- Claude verified the supervisor's closing fence at runbook line 3417. Adoption changes both ranges from 3313 to 3400 to 3313 to 3417. This is editorial and does not narrow or widen service-control authority.

## Review limits and retention

Certifications cover text and byte comparisons, not an implementation, host qualification, a budget decision or a launch go. Some raw operational evidence and earlier packet files were outside the certifiers' delivered packets; their reports disclose those limits. This record hashes the actual report files, including the saved Codex round 3 report that was delivered inline and did not claim its own digest. The source reports, packets, prompts, decisions and diffs remain in the operational archive under the exact names/hashes above; no stage 1 reading or scientific output is part of this public record.

The initial X2-1 register is pending, with its preparation sample seal and no accepted pass. The preparation report's harness findings must be resolved before any acceptance replay; adoption does not waive them. The payload seal and external approval rules are documented in the register README. The commit-time knowledge note and actual adoption commit are recorded by the interpreter, not fabricated by the drafter.
