# A10 stage 2 plan, version 3: 2026-10-29

**Verdict: implement the operator-selected path (a), with one successor built, rehearsed and proven before any stage 2 launch; X2-1 only and no A5 on the three A6 variants. Nothing is cleared to launch by these drafts.** Ranked gates: (1) correct registered reading tails and verified incidence states; (2) the committed builder/global seed registry, authenticated receipt policy and coordinated pin/admission changes; (3) pre-adoption fixed-path checks and fixed-code post-update byte agreement; (4) successor rehearsal/proofs and each exact launch approval; (5) unchanged Part 2 admission after at most two conditional rounds. Final refusal leaves its dependent arm not run.

**Budget estimates, X2-1 only:** base arithmetic **1,048.59 h**; with the selected identity release **1,122.59 h /46.7746 continuous active days**; conditional envelope with all eight extension opportunities **1,410.59 h /58.7746 days**. These rest on measured historical class/proof/extension costs, conservative memory and route assumptions, plus explicit operational allowances. They are not predictions of refusal, admission, need for rounds or completion. Proposed budget ceilings total **1,880 h** (original 1,400 +96 release +384 rounds), unchanged. Human/review/scheduling delays are additional. Any other host requires a new dated amendment.

## 1. Evidence, knowledge and limits

Nothing was simulated, prepared for registered execution, committed, fetched or accessed by SSH in this planning task. Repository access was read-only. No reading output, `values.json`, the stage 1 reading archive dated 2026-10-26, the opened-output archive, or scientific-output file was opened. Execution reports/write-ups were not used as evidence. The required registration itself discloses historical table refusals; those disclosures inform the operational risk list, not an outcome-dependent choice.

The operator and the interpreter who reviewed/proposed these changes have both read stage 1's opened reading. Its outcomes were not supplied to this planner. The ceilings use stage 1's measured costs and memory peaks only, and no quantity read from its results. No ceiling was set or moved because of a stage 1 reading outcome. A16 was proposed by an interpreter who knew those results; its stated basis is the certification history disclosed in A13/A14 and Part 2 cap arithmetic. It is prospective for stage 2 data, not a proposal made by a blind interpreter. On 2026-10-29, knowing stage 1's results and before any stage 2 output exists, the operator and interpreter resolved labels and implementation path. The operator selected path (a), authenticated no-label receipts for the A6 variants, X2-1 only, the fixed family paths subject to pre-adoption checks, and the stage 2 reader contract.

**Measured** below means a historical measurement recorded in an execution artifact, not a measurement newly made today. **Derived** means arithmetic on those measurements or registered grids. **Assumed** means an unmeasured planning input. Every prospective cost, memory use, throughput, ETA and reserve in this document is a **budget estimate**; the tables identify its basis. Ceilings are proposed budgets, never quantities, readings or predictions.

Evidence keys identify archived execution records by purpose, date and artifact name; source-code and canonical scientific paths remain repository-relative:

| Key | Evidence used |
|---|---|
| REG | Repository `simulation/diagnostics/v3_rerun_design_note.md`: A6; A10 in full, especially §§6, 7, 12, 13; A11; A12 parts 1/2; A13/A14 |
| CLOSE | the A10 stage 1 operations ledger, final blind-closeout entry, 2026-10-25T23:55Z to 2026-10-26T00:15Z: closeout charge and final ledger totals only |
| MAINT | the 2026-10-29 X2-1 maintenance before/after environment records: dated X2-1 environment/maintenance metadata only |
| PRICE | the registered A10 P2 cost projection of 2026-10-08 (file SHA-256 78a1d3ac253048c7e077b0e4eb12dd3150fa178cf3e63a24c6f0d87f02a8ad8d): original registered cost classes and projection identity only |
| OPS | Repository `AGENTS.md`; operational sections of `simulation/v3/A10_RUN_ON_X2.md`; source code |
| COST | the A10 stage 1 blind-closeout cost record of 2026-10-25 (`cost_record.json`): consumption and reconciliation fields; estimated entries kept distinct |
| CLASS | the A14 original-table compatibility proof attempt, c19b54f5 to 174ab660, X2-1 shard, begun 2026-10-20 (`proof.attempt.json`): job configuration/stratum counts and `items[*].resources` cost/memory metadata only |
| LOAD | the X2-1 load sheet frozen for that proof: measured peaks and reservations; its 0.95-headroom projections are **not** adopted |
| RUN | the X2-1 cost/resource metrics for k1p5, k2p3, weight-corner and horizon in the A10 run execution record begun 2026-10-23 (`metrics_<component>.json`): cost, worker time, RSS, concurrency and throughput only |
| MAIN | the successful main_r2 launch session-status record in the A10 run execution record begun 2026-10-23 (`status.json`): session cost/configuration metadata |
| LABEL | the A10 A5-label execution record begun 2026-10-22: launch `status.json` and `configuration_choices.json`: cost, completed counts, worker choices and configuration peaks |
| EXT | the A13 registered extension launch log begun 2026-10-19 (`launches.json`); the A14 step-6 execution evidence: launch log (`launches.json`), configuration summary (`configuration_summary.txt`) and frozen X2-1 load sheet (`load_sheet_x2_1.txt`); cost/memory/configuration fields only |

Source references below are under repository `simulation/v3/`. The source manifest was hashed without importing or running simulation code. Its identity is `174ab6600e0bc3514ee4b0f553a85b5e426aea4203621125debfa3cd12fd5afd`.

## 2. Registered inventory and dependencies

All arms use the corrected A10 instrument. Unvaried settings remain κ=8, θ=0.5, k*=1.8, g(c)=c, 500 steps. The square-root arm changes only g(c). Crowding uses the reproductive-age variant. The σ0² arms change only their registered calibration quantities.

| Component | Registered run cells and count | Table estimation jobs | Primary scoring rows | Reading remaining in stage 2 |
|---|---|---:|---:|---|
| `sqrt` | 9 R1 rr at α=1, first successor 1.5; plus 5 α × 7 first-successor capabilities at rr=.064; 44×100 = **4,400** | **1,495** = 1,375 primary + 60 double-population + 60 double-length | **2,875** | Boundary + 5 cap* comparisons = **6**, at 1−.05/18 |
| `crowding` | Same 44 cells, 100 seeds = **4,400** | **1,495**, same split | **2,875** | Boundary + 5 cap* comparisons = **6**, at 1−.05/33 |
| `sigma_squared_x10` | rr .059,.060,.062,.064,.066, α=1, first successor 1.5; 5×100 = **500** | **655** = 625 primary + 15 double-population + 15 double-length | **625** | One boundary comparison at 1−.05/33 |
| `sigma_squared_x0.1` | Same five cells, 100 seeds = **500** | **655**, same split | **625** | One boundary comparison at 1−.05/33 |
| **Total** | **9,800 runs** | **4,300 estimation jobs** | **7,000 rows across four separate families** | **14 headline comparisons**, in two separately sealed stage 2 components |

These are derived registered counts, not budget estimates. A6's original R4 table counts, 237 and 131, are **not** the A10 counts. `tables_a10.build_jobs` simulates per capability. The chain from 1.5 is {1,1.5,2.25,3.375,5}; the union over R2 starters has 15 capabilities. Thus square-root/crowding have 8×5+15=55 physical (rr,capability) pairs; each σ family has 5×5=25. The sensitivity subset uses three rules and two settings: (5+15)×3×2=120 jobs for square-root/crowding, and 5×3×2=30 per σ family. Scoring contexts are 8×5+5×15=115 and 5×5=25 respectively. Multiply by 25 rules for primary rows.

**Validation counts are conditional, not fixed yet.** For family f, let N be its estimation count, P the number of source jobs assigned the plain route by its registered estimator, and F=N−P the FV jobs. Let Fp/Fd split FV primary/doubled settings.

| Phase, in registered order | Exact count after estimation | Dependency |
|---|---:|---|
| fit | P | Completed, assembled estimation and sealed validation plan |
| validate_plain | 3P | Required fit records |
| validate_fv_primary | Fp | Estimation and frozen validation plan |
| validate_fv_double_population | Fd, including double-length jobs | Same; retain the high-memory phase |
| census | N | Family's own kernel and completed earlier phase barriers |
| **Total validation** | **2N+3P** | Plus mandatory non-result nondeterminism checks |

Therefore each 1,495-job family has 2,990 to 7,475 validation jobs, and each 655-job family has 1,310 to 3,275; total **8,600 to 21,500**. These bounds follow from the registered producer, not an assumed route mix. M, M_FV, P, Fp and Fd are frozen from that family's estimation before its validation data exist. No nominal route assignment or row value is reused to decide them.

**Labels:** A10's square-root family inherits A5: three labels per primary FV source job, **L=3Fp_primary, 0≤L≤4,125**. Freeze the exact count after estimation/publication. The three A6 variant families make **no A5 labels**, under the operator's 2026-10-29 interpretation recorded in A16 v2: A10 §7's “each arm's family” means A10's k* and sqrt arms; A6 is re-registered unchanged and explicitly excludes A5. Their FV tier remains **asymptotic and uncertified**, and the reading discloses it. The successor authenticates the exemption by validated family identity, retaining strict A5 for nominal/sqrt and all validation/provenance/Part 2 checks. The missing-file condition alone never selects the exemption. The old 756-label planning figure in A12 is not a cost denominator: stage 1's execution metadata records **4,752** label completions. There are no new variant label phases or budget rows.

**Base full-scope registered simulation inventory, before any A16 jobs:** **26,825 to 35,600 jobs**, conditional on all four families being publishable, excluding qualification/configuration/rechecks. Do not add the separate maximum labels to the all-plain validation maximum: they are incompatible routes. Square-root validation plus labels is `2×1495 + 3×1375 + 3×P_doubled = 7,115 to 7,475`; the other families contribute 2,990 to 7,475 and twice 1,310 to 3,275. Add 4,300 estimation and 9,800 run jobs. Exact counts are frozen at their registered phase boundaries; these arithmetic bounds authorize no discretion in sample size.

**Calibrations:** reuse the unchanged parent calibration for square-root and crowding. The two σ calibrations already have exact approved byte/payload/producer pins in `a10_constants.json` and are checked by `calibration._validate_a10_variant`. Do not regenerate them at 174ab660 or its successor: `build_variant` would stamp a different producer and fail those pins. Verify the archived records and the 50-record derivation/self-check later in an isolated, read-only input view at the pinned A6 provenance; no new calibration simulation is required. Preserve every other calibration value, all input hashes, and A10 constants.

The σ calibration byte hashes are:

- ×10: `aecef21ab61e0c7078b7fcf40fee540f9891a0ac3e32e995699cbfbd8264dbce`.
- ×0.1: `93c35a47e9aed3bd904fdc79ae24feb4015b75eb33bd42aa3a5220ae2ce88394`.
- Both retain producer `bd656b8f038c73d94c72ee4112806ca784f9ae3f4e4d4b99c0fd8a8d9fdcf7ed`.

### Canonical paths and their pre-adoption gate

The six-item path clause incorporated verbatim in `AMENDMENT_A16_DRAFT_v2.md` governs. Before adoption/preparation, verify no-overwrite status and earlier frozen manifests using metadata; a conflicting prior approved string is a finding, not permission to redraw seeds. This drafting task does not claim the check passed. All strings below are literal paths relative to `simulation/`:

| Family | Final publication path | Calibration path |
|---|---|---|
| sqrt | `v3/runs/a10_stage2/sqrt/v3_rerun_tables_A10.json` | `v3/runs/registered/v3_rerun_calibration.json` |
| crowding | `v3/runs/a10_stage2/crowding/v3_rerun_tables_A10.json` | `v3/runs/registered/v3_rerun_calibration.json` |
| sigma_squared_x10 | `v3/runs/a10_stage2/sigma_squared_x10/v3_rerun_tables_A10.json` | `v3/runs/a10_stage2/sigma_squared_x10/v3_rerun_calibration.json` |
| sigma_squared_x0.1 | `v3/runs/a10_stage2/sigma_squared_x0.1/v3_rerun_tables_A10.json` | `v3/runs/a10_stage2/sigma_squared_x0.1/v3_rerun_calibration.json` |

The σ paths are byte-verified aliases/copies of the pinned A6 calibrations, not regenerated calibrations. Bind all seed-bearing configuration and `a10_seed_source` strings, commit the path manifest and deterministic inventory/construction rule before simulation, and preserve them through any refusal/round/new checkout. Physical input aliases never rewrite logical jobs. Verify exact counterpart configuration before claiming historical R4 pairing. The publication target does not change after an extension.

### Fixed execution order

1. Complete the fixed-path pre-adoption metadata check, then approve/commit/publish A15 v3 with its version-2 publication copies and prospective A16 v2 before any stage 2 launch. The operator has selected path (a): build/rehearse/prove one successor identity Y before stage 2. Retain X2-1 maintenance records and accept fixed-code OS requalification separately, before successor compatibility proofs. Freeze the committed stage 2 builder/global seed registry and reader/forecast contracts before stage 2 data.
2. Freeze all four families' calibration/table path strings, original run inventories/scientific seeds, budgets and output roots. Preserve intentional A10/R4 run pairing. Global seed exclusion includes all original phases, pilots/probes, configuration/qualification/rehearsals, full A13/A14 manifests, and A16's entire eight-block reserve [2^62,12×2^60). No discretionary redraws.
3. For **sqrt**: estimation → assembly → original validation preparation/five phases → original Part 2 check. On pass, publication; on refusal, the A16 branch below. After publication: A5 identity record approval and record-only/public commit → labels if nonempty → label publication/A10 receipt → 4,400 runs → completeness/reading-input checks.
4. **Crowding**, then **σ0²×10**, then **σ0²×0.1** follow the same estimation/validation/admission branch, without A5 labels. Publish and authenticate each family's no-label receipt under A16's validated-family policy before its 4,400 /500 /500 runs.
5. **A16 branch, separately for each family:** preserve original refusal → reviewed registered round-1 preparation (entry consumes the opportunity under A16 finality) → freeze full eligibility, constants, cost-class R_max, impossible flags, complete seeds and both model-based admission-probability budget estimates → own launch go → round 1 → re-assembly/Part 2 check. Publish immediately if admitted. Only a normal completion followed by refusal permits round-2 preparation, restricted to originally eligible, never-tested “N* not reached” rows → own launch go → round 2 → final re-assembly/Part 2 check. Any specified terminal finding/no-launch/halt or final refusal ends that family's dependent arm; no third round. No automatic attempt just because money remains.
6. Close the ledger and reading-input inventory; compute and seal the separate A10/A6 stage 2 components. Open only on a separate operator go. Preserve stage 1 seals/verdicts.

There are **13 base possible simulation launches plus up to 8 conditional extension launches = at most 21**. A zero-label or empty/ineligible extension phase is recorded without a fictitious launch. Original validation retains five barriers and per-phase configuration/projection/rechecks. Assemblies/publications, calibration checks, proofs, qualification/configuration and sealed readings have their own approvals and charges.

**Extension job counts are derived, conditional counts, not projections:** J_fq is the number of distinct primary plain source jobs covering the frozen eligible rows of family f, round q; one source job contains 1…R_max full replicates, each 2,048 trajectories. J_f1≤1,375 for sqrt/crowding and ≤625 per σ; J_f2≤J_f1. Summing these design upper bounds over two rounds gives ≤8,000 extension source jobs and ≤256,000 replicates, but the 15-hour class-price cap and R≥6 floor are much tighter and may forbid launch. These loose inventory bounds authorize no selection or spending. The later exact inventory is J_fq source jobs, with allowed manifest J_fq×R_max seeds and at most 2,048J_fqR_max trajectories. Do not count replicates as original validation jobs. No exact realized count is known now.

One substantial launch at a time on **X2-1 only** remains the budget basis. X2-2 is permanently unavailable to this study; any other host requires a new dated amendment. A final refusal blocks only its dependent arm; preserve reasons and the registered unavailable/undetermined reading. A16 changes neither Part 2 nor the registered readings.

## 3. Code identity and preparation still needed

**174ab660 cannot launch the selected stage 2 plan unchanged.** Its primitive calculations are reusable, but it lacks the committed stage 2 spec builder/A10-aware global seed check, strict successor-pin selection, the chosen no-label receipt policy and A16 family support. The operator selected path (a): one new identity **Y, not yet built or hashed**, released before every stage 2 launch. `A16_FEASIBILITY_v2.md` §§0 to 2 supplies the full file/line inventory and proof protocol; the operator decisions here resolve its alternatives. Historical option/host discussion in that retained analysis is not current authority.

| Successor area | Required integration points and release condition |
|---|---|
| Committed stage 2 builder and seed registry | `tables_a10.py:224 to 297,340`, `sensitivity_a6.py:231 to 291,310 to 322,456 to 498`: emit the exact four A10 run groups and registered specs; bind path/calibration/receipt authority; globally check corrected A10 estimation, all validation streams, labels where required, runs and every prior/excluded/reserved seed. No R4 spec or ad hoc uncommitted script substitutes |
| Current/historical pins and admission | `artifacts.py:238 to 245`, `table_validation_a4.py:745 to 747,791 to 797`, `table_labels_a5.py:743 to 745` change together. Positive original-stage2 Part 2 admission must remain active at the new pin; historical plans retain historical verification |
| Authenticated no-label receipt | `production_tables.py:148 to 184`, `tables_a10.py:300 to 324`, `snapshot_a11.py:110 to 123`: sealed/versioned family-keyed policy only for the three A6 variants; preserve numerical lookup and every other production guard; strict A5 remains for nominal/sqrt |
| A16 scientific orchestration | Separate four-family/two-round modules beside nominal-only `validation_extension_a13.py`, `validation_extension_a14.py`, `history_a14.py`, `forecast_a14.py`; own immutable anchors, eligibility/history, unchanged N*/test, stop/finality, frozen-class pricing, forecast and re-assembly. Preserve all nominal behavior |
| Dispatch, data and resource support | Parallel A16 kinds/branches in `production_runner.py`, `multihost_a11.py`, `host_a11.py`, `snapshot_a11.py`, `qualification_a11.py`, `worker_control.py`; full seeds/checkpoints/halt handling, verified aliases and class/memory admission. Rehearse only the selected X2-1 topology; dispatch support does not authorize another host |
| Replay and exact producer acceptance | `compatibility_a10.py:145 to 158,202 to 221`, `replay_a14.py`, compatibility shards and A2 dependency maps: genuine empty-scratch re-execution, all changed-file hashes/reasons and direct producer→Y records; no loaded checkpoint masquerades as replay |
| Reader and budget interface | `reading_a6.py:183,309 to 359,222 to 234`, `admission_a13.py:97 to 98,142 to 150`, `production_runner.py:259 to 261`: explicit per-family tail and verified no-admitted-row reader normalization, preserving production inertness. Scope/correct `pilot_a10.py:318 to 321,484 to 485` so A7's R4 ceiling is never A10 authority; retain frozen P2 prices |
| Runbook and coverage | New runbook and separately hashed preparation/forecast/reader tooling; fixtures for all family joins, positive Part 2 admission, both strict/exempt receipt policies, exact seed/path closure, tails and zero/mixed incidence, interruption and forced replay mismatch. Include the ≥2^63 end-to-end seed rehearsal specified in A16 v2 |

The future diff must enumerate every changed file, not merely these highlights. Original simulation/estimation/fit/census/test primitives and registered scientific job inputs remain unchanged. Nothing was implemented or rehearsed in this drafting task.

| Work | Required identity |
|---|---|
| Parent/σ calibration verification | Original pinned bytes/producers; accepted loader at Y, without regeneration |
| Four estimations and original A4 validation/admission | Y, with frozen original job inputs/seeds/classes and stage 2 family instruments |
| A16 round 1/2, re-assembly/admission/publication | Y with A16-specific reviewed authority and family/round anchors |
| Square-root A5 labels/receipt, variant no-label receipts and all four run components | Y; original scientific inputs/seeds; A12 provenance-ID checks |
| Sealed stage 2 reading | Separately committed/frozen wrapper and helpers at Y; old comparators accepted through explicit producer records; no stage 1 re-reading |
| Fixed-code OS requalification | Each original producing identity, not Y |
| A11 migration proofs | Y against archived outputs, after fixed-code OS acceptance; direct records per actual old producer |

**Pins:** at Y, current launches pin the adopted A16 commit and exact note. A16's supersession clause leaves A14's rule governing launches at 174ab660 and earlier identities; no new stage 2 launch uses those identities. Carried historical plans verify historically, not against the new checkout note. A15 remains separately committed budget authority, bound by full commit/path/hash, published provenance and immutable input inventory. Change all three sites together: `artifacts.py:238 to 245`, `table_validation_a4.py:791` with its selection, and `table_labels_a5.py:745`; review applicable A2 exact hashes. No stale whitelist may silently omit Part 2. Freeze all input closure, including historical compatibility records, the missing-input main-run restart in stage 1 is a recurrence risk.

**Migration:** fresh checkout at the approved proof-record commit; old execution checkouts remain immutable. A11 records must directly admit every producer used at Y. Original 434-table/five-A13 selections and the current A14/label/run selections are proved; supplemental equivalence checks are kept outside the strict A11 record where necessary. The original OS replay plan remains a distinct fixed-code requirement. Neither proof waives the other, and no unfinished launch changes identity. The A16 authority, not an A11 compatibility claim, admits the new samples.

**Implementation decision:** literal path (b) is withdrawn; revised (b′) was considered and not chosen.

Required future tooling: the in-manifest committed stage 2 builder/global seed registry, scratch-only external original-identity replay harness, isolated A16 forecast and sealed stage 2 reader. Freeze/review exact input/output contracts and source hashes. Source added under the simulation manifest changes identity; operational wrappers do not erase that fact. Preserve registered P2 classes/order; measured timing is budget evidence, not an outcome-selected change to R_max prices. Do not use legacy R4 `budget_a6`, `stage1_run_specs` or the stage 1 reader as a stage 2 substitute.

**Publication copies:** `STAGE2_PLAN.public_v2.md` is this v3 plan with local execution-record references replaced by stable descriptions. `REQUALIFICATION_PLAN.public_v2.md` retains the original fixed-code sample, pass rule and 64-hour ceiling, with completed maintenance chronology and separate later A11/A12 successor proof made explicit. Earlier copies are retained unchanged; the version-2 copies are the ones to commit with A15 v3. Record their exact adopted hashes.

## 4. Measured cost and the budget arithmetic

An X2-equivalent hour uses the stage 1 ledger's X2 reference rate **1.0**. Other historical machines' contributions were charged at their measured rates; their wall times cannot simply be added or divided by two. For this one-X2 plan, projected X2-equivalent hours equal active X2-1 wall-hours. Do **not** multiply or divide again by 31/16: A7's old plateau wording is not a license to rescale the recorded accounting.

### Historical measurements

| Stage 1 class/component | Completed jobs | Measured charge, X2-equivalent h | Interpretation |
|---|---:|---:|---|
| Nominal estimation | 2,835 | 30.28 | Whole component, mixed historical hosts; 0.010681 h/source job |
| Original A4 validation | 9,204 | 260.04 | 1,178 fit + 3,534 plain validate + 1,584 FV primary + 73 FV doubled + 2,835 census; 0.091725 h/estimation source |
| A13 extension launch | 10 source jobs | 5.80 | Historical cost only; no stage 2 extension entitlement |
| A14 extension launch | 4 source jobs | 9.77 | Long tail with only four runnable jobs |
| A5 labels | 4,752 | 59.39 | Whole-component cost; 0.012498 h/label. Launch-only status charge 58.7962 is a different scope |
| Main R1′/refinement/R2′ | 24,900 | 22.61 | Includes stopped first root and relaunch/overhead; launch-only successful root 21.9817 |
| k*=1.5 | 4,400 | 4.23 | Launch-only 4.1096; mean 99.14 worker-s, max 113.79, peak 1.042 GB |
| k*=2.3 | 4,400 | 4.22 | Launch-only 4.1004; mean 100.05 worker-s, max 116.19, peak 1.043 GB |
| Weight corners | 17,600 | 16.46 | Launch-only 16.2931; mean 100.74 worker-s, max 119.98, peak 1.043 GB |
| Horizon | 1,800 | 2.55 | Launch-only 2.4320; mean 139.00 worker-s, max 206.54, peak 1.103 GB |
| **Five run components** | **53,100** | **50.07** | Reconciled component sum, not worker-hours |

COST records 501.45 before closeout. CLOSE, the final blind-closeout ledger entry dated 2026-10-25T23:55Z to 2026-10-26T00:15Z, adds 0.32, giving **501.77 charged**. The ledger includes explicitly estimated ancillary entries, including 1.79 h of reconstructed additions; its aggregate is not claimed as wholly measured or multiplied into stage 2. A10's pilot remainder was **2,626−979=1,647 h**; its stage 1 charge is 501.77 against that 979-hour projection, with the 980-hour ceiling unchanged. The original stage 2 ceiling of 1,400, below the pilot remainder, cuts no registered work because it is repriced from measured classes. A16 adds separate scope and budgets. Stage 1 reading cost is not available within this task's permitted evidence.

CLASS stores historical **means per memory class**, pooled where fit/plain-validation share a class, and peak RSS over source completions. It does not supply an independent per-job time for every selected proof item. The following conservative timing inputs take the **largest stored class mean across capabilities** within each setting, rounded here for display. They are neither job maxima nor new pilot measurements. Copying source class means to stage 2 is an assumption; fewer scoring contexts may reduce cost, while changed dynamics or the OS may increase it.

| Class | Primary worker-s | Double-population worker-s | Double-length worker-s |
|---|---:|---:|---:|
| Estimation | 985.375 | 2,084.906 | 2,264.237 |
| Plain fit **or one** plain-validation replicate | 1,221.629 | 2,623.790 | 2,552.824 |
| One FV validation | 4,187.687 | 7,365.804 | 7,247.292 |
| Census | 32.456 | 97.865 | 40.943 |

### Base full-scope budget estimate, before A16 release or rounds

Use counts n=(1,375,60,60) for square-root/crowding, (625,15,15) for either σ family. For budgeting use conservative class capacities from §5: estimation wE=(31,17,17), plain wP=(29,14,14), FV wF=(7,3,3), census 31. These are assumed capacities before stage 2 class peaks are established, not an instruction to suppress the configuration test or a claim that the current runner automatically doubles every class reservation.

For each setting s, in hours:

`E = Σ n_s E_s / (3600 wE_s)`

`Vplain = Σ n_s (4 P_s / wP_s + C_s / 31) / 3600`

`Vfv = Σ n_s (F_s / wF_s + C_s / 31) / 3600`

Price each source by the larger route bundle, not the sum of mutually exclusive routes. At these inputs FV is larger in all three settings. For square-root, its three labels belong only to primary FV sources; adding labels to the all-FV envelope is consistent. No labels are added to an all-plain scenario.

- Square-root/crowding: E=16.404463; Vplain=89.4829; Vfv=310.153205.
- Each σ family: E=6.584420; Vplain=35.6166; Vfv=124.357674.
- Square-root labels, budget estimate: `4125 × 59.39 / 4752 = 51.553819 h`, using the observed whole-label-component cost at 16 workers as proxy.
- 500-step runs, budget estimate: `N × 119.98 / (31×3600)`; uses the largest measured job time among the comparable 500-step sensitivity components, not the horizon arm. Gives 4.730394 h for 4,400 and 0.537545 h for 500.
- Overhead budget estimates: add 1/3 h to each estimation/run launch; 2 h to each validation launch (five short configuration tests, cleanup and rechecks); 5/6 h to labels; 0.5 h per family's assembly/publication/identity/receipt work. These are assumptions, informed by recorded publication charges 0.07/0.11 h and existing producer reserves; qualification, hashing and long rechecks must fit the larger ceilings below.

| Component | Estimation budget estimate | Validation budget estimate | Labels budget estimate | Runs budget estimate | Publication budget estimate | Total budget estimate / one-X2 wall h |
|---|---:|---:|---:|---:|---:|---:|
| Square-root | 16.74 | 312.15 | 52.39 | 5.06 | 0.50 | **386.84** |
| Crowding | 16.74 | 312.15 | 0 | 5.06 | 0.50 | **334.45** |
| σ0²×10 | 6.92 | 126.36 | 0 | 0.87 | 0.50 | **134.65** |
| σ0²×0.1 | 6.92 | 126.36 | 0 | 0.87 | 0.50 | **134.65** |
| **Four components** | | | | | | **990.59** |
| Post-update requalification, including historical replay harness validation | | | | | | **48.00** |
| Shared input/calibration/seed/ledger preparation | | | | | | **4.00** |
| Two sealed stage 2 reading components and verification | | | | | | **6.00** |
| **Base budget estimate** | | | | | | **1,048.59 h = 43.69 continuous days** |

The 4 h preparation and 6 h reading budget estimates are assumptions, not measured stage 1 reader costs. This base table contains no A16 identity release or extension. Add the separate allowances below; original fixed-code OS requalification is already included, so do not count it twice.

**Memory-qualified alternative, budget estimate only:** if new class measurements support the historical RSS reservations at 0.8 headroom, FV capacities could be 12 primary and 6 doubled. The same arithmetic gives validation simulation budget estimates of 174.36 h per larger family and 70.93 h per σ family. Substituting these, and changing nothing else, gives a total budget estimate of about **670.15 h / 27.92 continuous days**. This is a resource scenario, not a forecast of routes or publication success. Do not use it as a launch allowance until the new measurements and load sheet support it.

### A16 release and conditional-round budget estimates

`A16_FEASIBILITY_v2.md` prices the selected combined release at a **74 h budget estimate** (computed 72.431848908, rounded up): 19.73×1.5 original-table proof +2.95 A13 replay +9.77 A14 replay +120×59.39/4752 label union +574×119.98/(31×3600) run union =44.431848908 historical proof-cost proxy; add 20 assumed original operational/rehearsal/tooling hours and 8 assumed audit-fix hours (builder/seed/path 4, receipt/family/admission 3, reader tail/incidence 1). These are budget proxies, not completed work or measured engineering hours. The proof union is ≤1,137 jobs; freeze exact selections/overlaps later. The **96 h budget ceiling** stays unchanged.

**Release schedule budget estimate:** 74/24 =3.083 continuous active X2-1 days, plus assumed 4 to 7 working days for implementation/review/record turnaround, based on the multi-module inventory rather than measured developer velocity. Fixed-code OS replay is separately budgeted at 48 h and must pass before new-code proof. Setup/inventories may be shared; one Y execution cannot count as both comparisons. No overlap saving is assumed.

For each family and each round, **budget estimate 36 h = 2×15 class-price envelope +6 assumed overhead**, ceiling 48. The measured A13/A14 launch charges, 5.80/9.77 h over 10/4 source jobs, support caution about tails; A14's disclosed 7.37 h class-price budget estimate was smaller than its 9.77 h charge (ratio about 1.326). The assumed factor 2 is a budget margin, not a change to R_max pricing. R_max uses only the frozen P2 classes: `max integer R≤32 with R sum_j(B_j/3)≤15`, no launch below 6, whole eligible source set. No quantity from results sets a ceiling.

| Added component | Conditional budget estimate | Ceiling |
|---|---:|---:|
| Successor release, selected path (a) | 74 | 96 |
| sqrt round 1 / round 2 | 36 / 36 | 48 / 48 |
| crowding round 1 / round 2 | 36 / 36 | 48 / 48 |
| σ0²×10 round 1 / round 2 | 36 / 36 | 48 / 48 |
| σ0²×0.1 round 1 / round 2 | 36 / 36 | 48 / 48 |
| **Release plus all eight opportunities** | **362** | **480** |

**Budget-estimate totals:** 1,048.59+74=**1,122.59 h**, 46.77458333 days, before extensions; plus 8×36=288 gives **1,410.59 h**, 58.77458333 days, conditional on every opportunity. Adding all rounds to the conservative base route/label envelope is an expenditure envelope, not a claim that its separate worst-case routes occur together. The memory-qualified base alternative above would similarly become 744.15 h before rounds or 1,032.15 h with all eight; both remain budget estimates resting on the unverified improved memory capacities, not launch allowances.

### Proposed ceilings (budgets)

| Budget component | Estimation | Validation | Labels | Runs | Publication/identity/receipt | Total ceiling |
|---|---:|---:|---:|---:|---:|---:|
| Square-root | 22 | 400 | 70 | 8 | 2 | **502** |
| Crowding | 22 | 400 |  | 8 | 2 | **432** |
| σ0²×10 | 9 | 160 |  | 2 | 2 | **173** |
| σ0²×0.1 | 9 | 160 |  | 2 | 2 | **173** |
| **Family ceilings** | | | | | | **1,280** |
| Post-update requalification | | | | | | **64** |
| Shared preparation | | | | | | **8** |
| Stage 2 sealed readings | | | | | | **12** |
| Unallocated operational contingency | | | | | | **36** |
| Original scope/prerequisite subtotal | | | | | | **1,400** |
| A16 successor-identity release | | | | | | **96** |
| A16 sqrt rounds 1 and 2 | | | | | | **48 + 48** |
| A16 crowding rounds 1 and 2 | | | | | | **48 + 48** |
| A16 σ0²×10 rounds 1 and 2 | | | | | | **48 + 48** |
| A16 σ0²×0.1 rounds 1 and 2 | | | | | | **48 + 48** |
| **Stage 2 budget ceiling** | | | | | | **1,880** |

Ceilings generally exceed the conservative component budget estimates by roughly 25% plus rounded overhead, with additional allowance for small launches. The 36 h contingency authorizes no work itself. Allocation from it requires a documented operator budget go before work and cannot silently increase a component ceiling: changing a listed ceiling requires a dated budget amendment. Unspent stage 1 allocations do not become stage 2 permission.

At one-X2 rate 1, 1,880 charged hours correspond to 78.33 active days at the ceiling; this is a **budget limit**, not a completion ETA. Every launch also has a hard wall allowance and cleanup reserve within its component budget. Reconcile all prior attempts and outstanding reservations before every go. If a measured budget estimate exceeds its ceiling, A10 §12 preserves section 6's operator choice, before a registered run of that component, between a budget amendment and uniform seed reduction across cells. A15 adds no authority to that rule, no non-uniform reduction and no cutting after a registered output of the component is read. A16's rounds cannot be expanded, repeated, subsetted or pooled through a budget transfer.

## 5. Worker-load sheets

### Common resource sheet

X2-1 budget basis: 32 CPUs, normal cap 31 (also 31 in X2 work mode), one numerical-library thread/worker initially. **Budget estimate:** treat 123 GB as decimal GB conservatively; live measurement replaces it. At default headroom 0.8, pool budget is at most 98.4 GB. Use actual `MemAvailable`, not installed memory, after `llm down`. Swap is a safety facility, not extra worker capacity. Preserve the existing free-swap check (16 GB) and memory admission/worker-safety behavior.

`worker_control.observe` records 1.2×measured RSS. For this conservative **budget estimate**, allow twice the registered estimate for an unmeasured class. That extra factor is a planning assumption, **not** a generic rule implemented in `worker_control.reservation`: the actual runner uses its sealed class estimate, any applicable unmeasured phase fallback, measured peaks and item-10 admission. The exact launch sheet must report those actual quantities. New family/kernel/calibration classes do not inherit a nominal peak as if directly measured. The historical peaks below are comparison evidence. Configuration-test peaks from shortened jobs do not prove full-length table memory. No frozen P2 cost/memory class is silently changed to implement the budget assumption.

| Resource class | Measured stage 1 RSS peak, GB | Initial reservation budget estimate, GB/job | Capacity budget estimate at 98.4 GB | Qualified historical-RSS reservation budget estimate / capacity |
|---|---:|---:|---:|---:|
| Estimate primary | 1.562280 | 2×1.41328125=2.8265625 | 31; CPU/mode | max(1.4133,1.2×1.5623)=1.8747 / 31 |
| Estimate doubled settings | 2.996134 | 2×2.8265625=5.653125 | 17; memory | 3.5954 / 27 |
| Plain fit/validate primary | 1.688805 | 2×1.675=3.35 | 29; memory | 2.0266 / 31 |
| Plain fit/validate doubled | 3.243594 | 2×3.35=6.70 | 14; memory | 3.8923 / 25 |
| FV validate primary | 6.369587 | 2×6.7=13.40 | 7; memory | 7.6435 / 12 |
| FV validate doubled | 12.524581 | 2×13.4=26.80 | 3; memory | 15.0295 / 6 |
| Census, all settings | 0.433385 | max(2×.106119,1.2×.433385)=.520063 planning floor | 31; CPU/mode | .520063 / 31 |
| 500-step runs | 1.043 | 2×2.0=4.0 initially | 24 initially; memory | registered 2.0 / 31 once measured |
| Square-root A5 labels | ~0.637 from short configuration RSS (not a full-job peak) | 2×2.28=4.56 planning allowance; retain any larger actual sealed estimate | 16 proposed; configuration throughput | A5's 2.28 GB estimate comes from the older 1.9 GB P4 measurement plus 20%; A10 full-job peak is not present in the inspected cost records |

The 31-worker run cost scenario requires qualification to demonstrate the historical 2 GB reservation is adequate; with the more conservative 4 GB planning allowance the capacity is 24. **Budget estimate** at 24 workers is 6.44 h per 4,400-run launch including 1/3 h overhead, still inside its 8 h ceiling; 500 runs take 1.03 h, inside 2 h. Keep this fallback on the live load sheet. If the operator chooses these lower targets, record them through supported worker controls; do not describe the budget assumptions as already implemented class caps.

The existing item-10 weighted admission rule can pack mixed classes more tightly than the conservative per-class sheet above. Report **both** its charge and the sum of full per-class reservations; do not call a weighted charge a measured RSS bound. The budget estimate takes no credit for that extra packing. Avoid simultaneous high-memory families. Honor memory dips by draining, not by treating 31 as a required concurrency.

Before every substantial launch and each material workload phase: a roughly 15-minute configuration test in the intended service state, candidate workers **8,12,16,24,31**, filtered by memory and runnable jobs. OPS's older candidate list says 32, but the user's explicit 31-worker cap governs this plan, including trials. Existing specs can supply the capped candidate list without changing jobs or code. Two threads are candidates only if profiling shows material threaded numerical work; workers×threads≤32 and workers≤31. Take greatest completed-work throughput; prefer the smaller configuration within about 5%. Record all results and effective library thread queries, not only environment settings.

Historical evidence: main/k*/corners/horizon chose 31; short profiles delivered roughly 6,200 jobs/h, while full k* runs delivered about 1,060 to 1,080 jobs/X2-hour. Labels chose **16**, not 31: X2-1 short-profile throughput was 3,164/4,479/5,098/4,767/4,569 jobs/h at 8/12/16/24/31. A14 extension chose 12 in its configuration test but had only **four** actual source jobs; its 9.77 h cost shows why configured workers do not determine tail duration. Short-profile throughput is not full-job throughput.

### Sheet for each launch

All numerical use/ETA columns are **budget estimates** based on §4 timings and §5 reservations. Replace these planning sheets with sheets from each **exact frozen spec**, then refresh with the configuration result before dispatch. In the table, E uses estimate classes; V uses the five validation/census classes; R uses the 500-step run class; L uses labels. The common overrides below apply separately to every row.

| Launch ID, order | Jobs | Worker target; binding cap | Use budget estimate | ETA budget estimate, one X2 | Launch ceiling |
|---|---|---|---|---:|---:|
| S-E | 1,495 | ≤31; E primary CPU, doubled memory at 17 initially | primary ≤87.63 GB reservations; doubled ≤96.10 GB | 16.74 h | 22 h |
| S-V | 2,990+3P | ≤31; P 29/14, FV 7/3, census 31 initially | P ≤97.15/93.8; FV ≤93.8/80.4 GB; census 16.12 GB | 312.15 h, all-FV envelope | 400 h |
| S-L | 3Fp_primary≤4,125 | Start from measured label choice 16; configuration binds unless memory lower | 72.96 GB planning allowance at 16×4.56; 50% worker CPU budget | 52.39 h at maximum label count | 70 h |
| S-R | 4,400 | 31 after full memory authority; otherwise 24 | ≤62 GB at 31×2; initial ≤96 GB at 24×4 | 5.06 h; initial-memory fallback 6.44 h | 8 h |
| C-E | 1,495 | Same E class caps; own crowding configuration | Same reservation envelope, not a measured crowding peak | 16.74 h | 22 h |
| C-V | 2,990+3P | Same V class caps; own routes and configuration | Same V reservation envelope | 312.15 h | 400 h |
| C-R | 4,400 | 31 qualified / 24 initially | ≤62 / 96 GB reservations | 5.06 / 6.44 h | 8 h |
| X10-E | 655 | Same E caps; own calibration/kernel classes | Same E reservation envelope | 6.92 h | 9 h |
| X10-V | 1,310+3P | Same V caps; own routes and configuration | Same V reservation envelope | 126.36 h | 160 h |
| X10-R | 500 | 31 qualified / 24 initially; also runnable count | ≤62 / 96 GB reservations | 0.87 / 1.03 h | 2 h |
| X01-E | 655 | Same E caps; distinct calibration/kernel classes | Same E reservation envelope | 6.92 h | 9 h |
| X01-V | 1,310+3P | Same V caps; own routes and configuration | Same V reservation envelope | 126.36 h | 160 h |
| X01-R | 500 | 31 qualified / 24 initially; also runnable count | ≤62 / 96 GB reservations | 0.87 / 1.03 h | 2 h |

31 workers imply a maximum scheduled-worker fraction 31/32=96.875%, not a hard OS CPU reservation or measured utilization. Initial FV capacities 7 and 3 imply 21.875% and 9.375%; validation is memory-bound even with idle CPUs. Qualified FV capacities 12/6 imply 37.5%/18.75%. The live sheet must show phase mix, tail, runnable count and measured utilization separately.

**Operator-overridable operational values:** requested workers within 31 and available CPUs; normal/work/drain/stop controls; thread count 1 or 2 within the CPU budget after profiling; memory headroom (default .8, maximum .95 in the current code; a departure from .8 needs an explicit reason and fresh sheet); lower memory/worker targets; service restoration timing for consecutive approved work; launch timing; and wall allowance/reservation **within** the approved ceiling. Every override is recorded and persists appropriately on resume. Changing host pool, code, scientific settings, jobs, seeds, sample size, admission tests or a component ceiling is not one of these overrides. Requalify after any runtime/library change.

### A16 worker-load sheet, instantiated separately for all eight possible launches

| Launch | Gate / inventory | Worker target and binding cap | Budget estimate / ceiling |
|---|---|---|---|
| S-X1 | Original sqrt refusal; full J_S1 eligible source jobs | min(31, J_S1, memory cap, measured fastest configuration) | 36 h /48 h |
| S-X2 | Normal S-X1 completion/refusal; J_S2 never-tested sources | Same with J_S2 | 36 h /48 h |
| C-X1 | Original crowding refusal; J_C1 | Same with J_C1 | 36 h /48 h |
| C-X2 | Normal C-X1 completion/refusal; J_C2 | Same with J_C2 | 36 h /48 h |
| X10-X1 | Original σ×10 refusal; J_101 | Same with J_101 | 36 h /48 h |
| X10-X2 | Normal X10-X1 completion/refusal; J_102 | Same with J_102 | 36 h /48 h |
| X01-X1 | Original σ×0.1 refusal; J_011 | Same with J_011 | 36 h /48 h |
| X01-X2 | Normal X01-X1 completion/refusal; J_012 | Same with J_012 | 36 h /48 h |

The extension itself uses **primary plain** sources only; doubled/FV memory peaks do not authorize extra extension work. Historical plain-primary peak was **1.689 GB**; A14's short configuration reservation reached **7.597 GB**, which is reservation evidence, not a measured full-job bound. New full A16 replicate/checkpoint/parse peak is unknown. **Initial budget estimate:** allow at least 8 GB per worker (assumption rounded above 7.597), or the larger sealed reservation/1.2×measured peak; at .8×123=98.4 GB this permits at most **12 workers, 96 GB** before live memory, runnable counts and configuration bind. A four-source tail uses at most four workers, **32 GB budget estimate**, not 31-way throughput. Keep source-class and item-10 heaviest-quarter packing, per-phase peak observations, controller/checkpoint memory and live admission. Qualification replaces assumptions before dispatch, never reduces the registered class-price sum.

Each row's **ETA budget estimate is 36 active X2-1 h**, resting on the price/overhead model above; it is a placeholder until a frozen load sheet prices the actual J, R_max, memory classes and measured short-work throughput. Its 48-hour total allowance includes setup/checks/publication and cleanup, not 48 simulation hours plus extras. Simulation-price cap remains 15. Report both class-price and actual-charge budget estimates, consumed/reserved cost, model-based admission probability and its 0.9 sensitivity before the go. Overridable: lower worker targets, permitted thread candidates, headroom with recorded reason, timing, operational cleanup/overhead allocation inside the same ceiling. Not overridable: eligible set, R_max formula/floor/32 cap, 15 class-price limit, seeds, N*, test, admission or finality. Memory or ETA failure returns for a concrete operational/budget decision, never an outcome-selected subset.

### Prerequisite and non-simulation operation sheets

| Operation | Workers / binding limit | Memory/use budget estimate | Cost/ETA budget estimate | Ceiling |
|---|---|---|---:|---:|
| OS requalification | Mixed historical classes; ≤31 and sample-specific memory/runnable caps | §5 class reservations, original producer runtime | 48 h; see separate plan | 64 h |
| A16 successor release and compatibility evidence | One supervisor for preparation; spawned proof/rehearsal workers ≤31, historical class/runnable/configuration caps | Use requalification's original-table sizing (FV primary/doubled at most 12/6 after measured sizing), labels 16 with ≥4.56 GB allowance, extension replay ≤5/4 sources and measured/sealed memory; new A16 trials start at the conservative 8 GB assumption until measured | 74 h budget estimate from historical proof charges plus 28 assumed operational/audit-fix hours; exact preflight sheet before each rehearsal/proof launch | 96 h |
| Shared input/calibration/seed preparation | One supervisor; no simulations | Initial 16 GB process allowance, unmeasured | 4 h assumption | 8 h |
| Each family's publication/receipt | One process; no simulation workers | Initial 16 GB process allowance, unmeasured; check on actual family | .5 h assumption | 2 h each |
| Two stage 2 reading components | One reader at a time, one library thread initially | Initial 16 GB allowance; test fixture peak later; preserve exact RNG draw order | 6 h total assumption | 12 h total |

Process-memory allowances in this last table are planning assumptions, not measured bounds. If inadequate, stop and replan resources inside the budget; no truncation, dropped input or altered bootstrap arithmetic.

## 6. Publication, reading and reliability gates

**Publication:** retain A1 screens and A4's family-specific census, support/floor rules, plain certificate and FV tier. A13 Part 2 is prospective for these new validations and supplies no extension itself. A16 alone supplies the conditional rounds without changing admission. Its cap is floor(.001×primary rows): **2** for each 2,875-row family and **0** for each 625-row σ family. At most one admitted row per context; no balanced-witness row; all other screen/support/no-violation requirements remain. Admitted rows remain `not_estimable` and unavailable. Check and bind admission before publishing; preserve refusals and sidecars. Never overwrite a published family.

**Reading:** compare arms with the original A10 nominal runs on matching cells only: R1 at α=1 without refinement, R2 at rr=.064. Stage 1's 12 A10 and 25 A6 headline verdicts and seed-convergence seal are not recomputed. Keep total family sizes **18** and **33**, not 6 and 8. Use 50,000 resamples, `inverted_cdf`, independently resampled sides, job-ID order inside cells; A10 helper calls use seed 20261011 and A6 seed 20260929. Call comparisons in their registered sorted order. Keep undefined-resample thresholds .05/(2×18) and .05/(2×33), σ boundary censoring below .059, rr materiality .002, discrete cap* rules, descriptive quantities and citation qualifications unchanged. Compute no new stage 1 prediction score.

For every stage 2 registered quantity, apply `STAGE2_READER_REQUIREMENTS.md`, as referenced by A16 v2. Report incidence from predefined contributing arm/comparator runs, pooled numerators/denominators and per-run rates by branch. A family with a verified empty admitted-row set is **“no admitted rows”**, not a missing-record error: verify the complete family/receipt/context closure, label structural zero numerators as inferred, derive exact denominators from preserved evaluated allocation/survival-first steps and yield events, and include that side in mixed-family pools. Zero denominator is unassessed. A missing accumulator on a verified nonempty-admission family, unknown binding or unrecoverable denominator is an integrity refusal; never fabricate or silently omit data. Any nonzero incidence flags the quantity; keep its estimate and never call unflagged quantities certified unaffected.

Pass the family tail explicitly to the boundary helper: **0.05/36** for sqrt and **0.05/66** for A6; `alpha` alone currently does not select it. Freeze synthetic threshold/equality and zero/mixed-incidence fixtures before results. Nominal/sqrt retain A5; variant readings disclose **no A5 labels; FV asymptotic and uncertified** under the adopted interpretation. Seal the two components separately, bind all source/input hashes and require the separate opening go. The historical reader contract's alternative labels branch is resolved by A16 v2; it grants no added label work.

**Service and runtime:** explicitly run and record `llm down` before every registered batch and any >1-hour operation, verify the actual service/process state, supervise restoration with `llm up` on normal/failure exits. Stage 1's `model_service=none` does not authorize leaving a restarted model server running after the OS upgrade. Preserve the registered Python/NumPy environment, `PYTHONINTMAXSTRDIGITS=0` where recorder/readers require it, spawned-process execution and verified numerical thread limits.

**Resumption:** retain exact spec/root/code/seed identity, durable completion hashes, budget and deadline; validate and skip exact completed jobs. Partial outputs do not count. Drain for ordinary mode changes. Restart interrupted in-flight simulation jobs from their original seed unless a tested full model+RNG checkpoint exists; per-step logs are not such a checkpoint. For A16, preserve completed replicates under its validated checkpoint protocol; never reload old registered checkpoints as completed work during a compatibility replay. A scientific halt/no-launch is final as specified, not an infrastructure resume. Record consumed time for failures, qualification and rechecks; never erase cost by moving roots.

## 7. Maintenance facts, ranked risks and contingencies

**Measured maintenance records, 2026-10-29:** X2-1 changed from kernel **7.0.0-34-generic** (14:32:21Z before-record) to **7.0.0-42-generic** (15:31:14Z after-record), with reboot recorded. The five packages were unheld and unchanged: libc6/libc-bin **2.39-0ubuntu8.9**, libgcc-s1/libstdc++6/libgomp1 **14.2.0-4ubuntu2~24.04.1**. The after-record shows no held/upgradable packages and no reboot required. The phaseb package-list SHA-256 is unchanged: `039a116d09ecad032d50330b7ae2495ebbb3c9d83f736d8c63c66a230ebc9f01`. This list hash is not bit-identity evidence. The model service was active in the after-record; verify current state and run `llm down` for future work.

1. **Critical: reading correctness and integrity.** The helper tail must be explicit by family; missing A13 incidence needs the verified no-admitted state. Freeze the reader contract/fixtures, preserve 18/33 families, censoring and stage 1 seals; no certification claim for an unflagged quantity.
2. **Critical: unbuilt successor and acceptance policy.** The committed builder/global seed registry, coordinated three-pin-site change, authenticated no-label policy and A16 orchestration must be built and proven before any stage 2 launch. Verify all snapshot dependencies; no guard bypass or identity mixing.
3. **Critical: seed paths and runtime drift.** Complete the incorporated path clause's pre-adoption check and freeze every seed-bearing string. After the completed OS update, fixed-code replay against archived bytes precedes successor proof on the accepted runtime. Never infer bit identity from package versions or change paths after refusal.
4. **High: refusal despite prospective rounds.** A13/A14 disclose two nominal rounds, not stage 2 power. At most two conditional rounds and one extension test per row; σ caps remain zero. Final refusal/no-launch/halt leaves the arm not run; no post-refusal enlargement, threshold relaxation or automatic use of contingency.
5. **High: memory, long tails and route uncertainty.** Historical doubled-FV RSS reached 12.525 GB/job; A14 had four runnable sources. Measure new full-job/checkpoint peaks, use live class caps/configuration tests and preserve the conservative budget envelope. Short profiles are not full-job memory evidence.
6. **High: seed serialization and forecasts.** Rehearse ≥2^63 seeds end to end with exact integer equality; actual rehearsal streams remain outside reserved ranges, with metadata-only σ-block checks. Freeze family-general probability tooling before data; its figures are model-based operational budget estimates, not error guarantees or permission to change R_max/eligibility.
7. **Medium: proof/preflight overhead.** Historical superseded/stopped proofs charged 28.31/6.568 h. The selected release has a 74 h budget estimate/96 h ceiling, based on historical proof proxies plus 28 assumed operational hours. Validate forced mismatches before full replay and retain/meter failed attempts.
8. **Medium: calibration, disclosure and scope.** Keep pinned σ bytes and aliases, strict sqrt A5 versus authenticated variant no-label receipts, full reserved manifests and prospective knowledge disclosures. The operator/interpreter knew stage 1's results; the executor did not receive them. X2-1 only; another host requires a new dated amendment.

| Contingency | Required gate / disposition | Budget authority |
|---|---|---|
| Original Part 2 refusal | Preserve sealed refusal; A16 round-1 preparation only after release/entry approval | Own 48 h round-1 allowance; no automatic launch |
| Round 1 normal completion and refusal | Only originally eligible, never-tested unreached rows; own round-2 packet/go | Own 48 h round-2 allowance |
| Round 1 admits | Publish; round 2 permanently unused | Release unused reservation; no replacement work |
| R_max<6, empty eligible set, seed/input finding, explicit decline or scientific halt after entry | Apply A16 terminal rules; dependent arm not run; other families independent | Charge failed work, release unused funds; no third realization |
| Round 2 ends with any Part 2 failure | Final refusal; no third round | No budget amendment alone repairs scientific finality |
| Component estimate exceeds ceiling | Section 6's unchanged prospective decision; nothing cut after component output is read | Dated amendment for changed ceiling; no automatic borrowing |
| Desire to use any other host | Not allowed by this plan; X2-2 is permanently unavailable | New dated amendment required; no existing allowance implies permission |
| New runtime or code mismatch | Stop, preserve failure, investigate; new fixed-code acceptance / corrected identity proof as appropriate | Reconcile remaining allowance and approve exact new work |
| Infrastructure pause within exact root/spec/code/seeds/environment/deadline | Resume supported same attempt, retaining completed records | Existing go suffices within its explicit scope |

No second-host cost or speedup is included. All launches, requalification and successor proofs in this plan use X2-1 only; historical other-host records remain read-only evidence.

The ordered release/round/publication/reading approvals are in `APPROVALS_v3.md`. A15 v3 and A16 v2 remain drafts pending certification/adoption/commit; the operator's selected inputs are incorporated, not a launch go.