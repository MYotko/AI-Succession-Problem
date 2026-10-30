# A17 hosts feasibility, adopted companion, 2026-10-30

**Verdict: feasible as a prospective host/dispatch change, but the phase 1 identity cannot execute the proposed pool unchanged.** Highest severity: (1) independent exact-byte host and identity gates are not verified by this drafting task; (2) class-aware placement and A16 pull transport must be carried by the identity serving the first multi-host launch, before that launch's own direct A11 proofs (section 7); (3) memory-limited participation can exceed an unchanged component ceiling even while shortening wall time. The numerical scenarios below are budget estimates, not measured X2-2 rates or promised completion times.

This companion cites the committed `STAGE2_PLAN.public_v2.md` and `REQUALIFICATION_PLAN.public_v2.md` without editing them. Their scientific inventory, requalification selection, budget basis and pass rules remain authoritative. Their single-host/service assumptions are modified only as A17 explicitly provides. The requested earlier plan copy supplies the same class arithmetic used below. Filenames are public record identifiers, not deployment locations.

## 1. Evidence and its limits

Measured on X2-1 on 2026-10-30: one-thread, Phase B-type 500-step workload, two jobs per worker, three service states and two power modes. Raw JSON reports the following throughput (jobs/hour); solo cells show mean job seconds instead.

| Mode and service | Solo seconds | 16 workers, jobs/hour | 31 workers, jobs/hour |
|---|---:|---:|---:|
| Balanced, stopped | 17.14 | 2460.6 | 2821.8 |
| Balanced, idle | 17.19 | 2459.0 | 2846.9 |
| Balanced, generating | 53.74 | 1697.9 | 2113.5 |
| Performance, stopped | 17.70 | 2802.2 | 3237.4 |
| Performance, idle | 17.82 | 2798.2 | 3222.0 |
| Performance, generating | 49.99 | 2153.5 | 2552.8 |

The measurement summary reports about 126 GB available with the model stopped and about 55 GB available with the model resident, package caps about 85 W Balanced and 119 to 120 W Performance, and 98 C sustained in Performance. Raw 31-worker Balanced generation had mean MemAvailable 53.92 GB, so even 55 GB must be refreshed. Two-stream model throughput fell about 12.5 percent in Balanced and 5.4 percent in Performance during simulation load. These readings support interference and residency effects; they do not measure any FV table class, X2-2's performance, a new X3 or engineering effort. No model split across hosts is proposed.

Operator-supplied default state, not newly measured here: X2-2's GUPPI-owned model stays running absent a recorded owner agreement, about 70 GB resident/about 55 GB available, Balanced at 84 W. Maintenance records independently supply both kernels/package versions/package-list hashes and removed holds. The relocation record independently supplies the hash-verified read-only X2-1 copy and removal of X2-2's originals. No scientific records in that copy were opened.

## 2. Rate assumptions for budget estimates

The reference remains the historical X2-equivalent rate 1.0. Assume X2-1 continues in its measured Performance, service-down state; reconfirm it rather than granting a silent power change. Use raw throughput ratios, not rounded percentages:

| Inferred ratio from the benchmark | Arithmetic | Value |
|---|---|---:|
| 31-worker Balanced generating versus clean Performance | 2113.5/3237.4 | 0.652839 |
| 31-worker Balanced idle versus clean Performance | 2846.9/3237.4 | 0.879379 |
| Same 16-worker generating comparison | 1697.9/2802.2 | 0.605917 |
| Same 16-worker idle comparison | 2459.0/2802.2 | 0.877525 |
| Sparse-job generation stress factor | 17.70/53.74 | 0.329364 |
| Sparse-job idle factor | 17.70/17.19 | 1.029668 |

For the central **budget estimate**, assume continuous generation, duty cycle d=1, and transfer the 16-worker speed factor 0.605917 to memory-limited classes. Use 0.652839 for the 31-worker census. This transfer to FV, labels and other concurrencies is unmeasured. A second, conservative **budget estimate** transfers the sparse factor 0.329364 to all those reduced-concurrency classes. It is a stress scenario, not a measured worst-case bound. An idle and a 50-percent-duty **budget estimate** use q(d)=(1-d)q_idle+d q_generating; this assumes activity occupies that fraction of elapsed time and frequent alternation, not a demonstrated nonlinear response model. Do not price a launch from a hardware-class label.

For the prerequisite's **budget estimates**, apply the same interpolation separately to the sparse-job factor: s(d)=(1-d)(17.70/17.19)+d(17.70/53.74), and to the scalar participation-rate proxy: rho(d)=(1-d)(2846.9/3237.4)+d(2113.5/3237.4). Thus d=0.5 has s=0.679516 and rho=0.766109. The idle sparse ratio slightly exceeds one because the measured solo means were 17.70 seconds clean Performance and 17.19 seconds idle Balanced; it is an explicit transfer of those samples, not evidence of a reliable Balanced advantage or an X2-2 measurement. The campaign uses the 16-worker q(d) transfer for reduced-concurrency classes, not this sparse replay factor. Clean X2-2 instead assumes reference rate one and reference capacities in Performance; no hardware-class speed bonus is taken.

Participation rate and scheduling speed are distinct. The illustrative scalar participation-rate budget proxy is 0.652839 for continuously generating X2-2. It is not an approved ledger rate. At join, the host's frozen reference workload and actual concurrency must measure the scalar rate and each class rate; the phase 1 code already distinguishes elapsed-throughput evidence from per-job scheduling speed. Do not multiply that elapsed rate by a worker-count ratio again. Below, capacity ratios convert class speed into additional work throughput only. Owner-agreed idle, reduced or stopped states must be recorded with their actions, envelope and duration before use; the rates and charges belong to the actual recorded segment, not the most favorable scenario in this document.

## 3. Memory and placement budget estimates

Use the plan's initial conservative reservations for stage 2 and its separate historical-RSS reservations for the fixed-code replay. Assumed raw available memory is 123 GB on X2-1 and 55 GB on X2-2, at 0.8 headroom: 98.4 and 44 GB. These are budget estimates, replaced by actual MemAvailable; the resident 70 GB is already excluded and must not be subtracted a second time.

| Stage 2 class | Reservation budget, GB/job | X2-1 capacity budget estimate | X2-2 capacity budget estimate | Binding basis |
|---|---:|---:|---:|---|
| Estimate primary | 2.8265625 | 31 | 15 | CPU on reference, memory on X2-2 |
| Estimate doubled | 5.653125 | 17 | 7 | Memory |
| Plain fit/validate primary | 3.35 | 29 | 13 | Memory; at 53.92 GB raw X2-2 falls to 12 |
| Plain fit/validate doubled | 6.70 | 14 | 6 | Memory |
| FV validate primary | 13.40 | 7 | 3 | Memory |
| FV validate doubled | 26.80 | 3 | 1 | Memory |
| Census | 0.520063 | 31 | 31 | CPU/configuration |
| Runs, after 2 GB full-job authority | 2.00 | 31 | 22 | Memory on X2-2; 21 at 53.92 GB raw |
| Runs, initial 4 GB fallback | 4.00 | 24 | 11 | Memory |
| Labels, conservative allowance | 4.56 | 16 | 9 | Configuration/reference, memory/X2-2 |

No cross-class capacity is additive: a mixed queue must fit the sum of its current reservations as well as the existing item-10 admission rule. Do not reserve 44 GB for every class at once. The new placement policy is a scheduling overlay using the registered classes, not a new memory-price rule. Keep low-memory classes available for X2-2 and direct FV jobs only where the actual class capacity, measured rate and budget permit. Preserve all original jobs even if a host can carry none of a class. A late tail with few jobs can suffer the measured sparse-job slowdown; move eligible unstarted tail work toward the reference, never select jobs by scientific outcomes.

## 4. X2-2's own fixed-code requalification budget

Apply the committed plan's frozen **at-most-1,049 full-job** sample on X2-2 itself: 90 estimation plus 344 original validation/fit/census, 5 A13, 4 A14, at most 90 labels and 516 runs. Exact strata, deterministic selection, original identities, scratch isolation, byte comparison and review are unchanged; candidate-host-only failure consequences and common-reference integrity stops follow A17 section 2(a). No replacement sample is made for X2-2. The archive's relocated read-only copy supplies dependencies, not completed work to install in scratch.

At 44 GB, the replay plan's historical-RSS reservations imply primary/doubled capacities of 23/12 estimation, 21/11 plain, 5/2 FV, versus reference 31/27,31/25,12/6. The maximum capacity penalty is 6/2=3. The detailed split of the 344 sampled table jobs is not inspected here; apply that factor 3 to the entire original-table proof proxy conservatively. A13/A14 sample jobs are only five/four: using their historical 7.597 GB short-trial reservation as a planning allowance fits five within 44 GB, but full replay/checkpoint parsing must confirm it. Do not extrapolate their tails from 31-worker throughput.

The conservative **budget estimate** remains d=1 and the sparse speed factor s=0.329364 for every replay compute class. The three alternatives are owner-agreed idle residency (d=0), owner-agreed half-duty residency (d=0.5), and clean Performance after the owner relocates the service. Residency remains about 70 GB at d=0 and d=0.5; idling does not release that memory. Clean assumes 123 GB available, 98.4 GB at headroom, and the reference capacities/rates. None is a measured X2-2 pass.

For resident cases the explicit **budget-estimate arithmetic** is:

`H_host(d) = [19.73*1.5*3 + (2.95+9.77) + (90*59.39/4752)*(16/9) + (516*119.98/(31*3600))*(31/22)] / s(d) + 8`.

`charged X2-equivalent hours = H_host(d)*rho(d) + 4; serial wall hours = H_host(d) + 4`.

The 8 host-local hours cover capture, staging, configuration, checks and cleanup; the separate 4 reference-host hours cover inventory, staging/record review and support. These are assumed allowances, not measured work. They replace the original plan's single 4-hour support allowance. Apply the participation proxy to the entire joined host segment, including its 8-hour allowance; charge reference support at rate one. No overlap is assumed.

| Component and basis | d=1 wall-h budget estimate | d=0.5 wall-h budget estimate | d=0 wall-h budget estimate | Clean wall-h budget estimate |
|---|---:|---:|---:|---:|
| Original 434 table jobs: 19.73 historical proof hours times assumed 1.5, capacity penalty 3 if resident, then /s | 269.5653 | 130.6592 | 86.2268 | 29.5950 |
| Five A13 and four A14 jobs: (2.95 historical proof charge +9.77 whole-launch proxy)/s | 38.6199 | 18.7192 | 12.3535 | 12.7200 |
| At most 90 labels: (90*59.39/4752), capacity penalty 16/9 if resident, then /s | 6.0713 | 2.9428 | 1.9420 | 1.1248 |
| 516 runs: 516*119.98/(31*3600), capacity penalty 31/22 if resident, then /s | 2.3733 | 1.1504 | 0.7592 | 0.5547 |
| Host-local allowance, assumed | 8.0000 | 8.0000 | 8.0000 | 8.0000 |
| X2-1 support, assumed, serial | 4.0000 | 4.0000 | 4.0000 | 4.0000 |

For clean X2-2 the capacity penalties and s are all one: `H_host = 19.73*1.5 + 2.95 + 9.77 + 90*59.39/4752 + 516*119.98/(31*3600) + 8 = 51.9946`. At rho=1, charged and serial wall **budget estimates** are both `51.9946+4=55.9946 hours`. This is the plan's unrounded 47.9946-hour (rounded 48-hour) X2-1 basis plus 8 hours of extra-host support allowances, with no memory or rate penalty. The 8-hour increment is `(8+4)-4`; it is not a second replay. No relocation duration or charge is measured or included: the owner must complete relocation before this pass, and any study-funded relocation or extra configuration needs explicit pricing before the go.

| Service state selected by operator | s / rho budget proxies | Charged budget estimate, X2-equivalent h | Rounded charged budget estimate | Serial wall budget estimate, h / 24-hour days | Check against conservative proposed 256 X2-equivalent h ceiling | Proposed ceiling, X2-equivalent h (drafter's illustration) |
|---|---|---:|---:|---|---|---:|
| Resident, generating d=1 | 0.329364 / 0.652839 | 215.9309 | 220 | 328.6299 / 13.6929 | Fits; 40.0691 h unrounded margin | 256 |
| Resident, d=0.5 | 0.679516 / 0.766109 | 127.7047 | 130 | 165.4715 / 6.8946 | Fits; 128.2953 h unrounded margin | 152 |
| Resident, idle d=0 | 1.029668 / 0.879379 | 100.0998 | 105 | 113.2815 / 4.7201 | Fits; 155.9002 h unrounded margin | 119 |
| Clean, Performance | 1.000000 / 1.000000 | 55.9946 | 56 | 55.9946 / 2.3331 | Fits; 200.0054 h unrounded margin | 67 |

Drafter's illustrative budget-ceiling proposal: for each state use `ceil(E_state * C_conservative / E_conservative)`, where E denotes the unrounded charged budget estimate and C the conservative proposed ceiling. This applies the conservative case's relative margin to each state's estimate, then rounds upward to a whole X2-equivalent hour. The underlying unrounded arithmetic, rather than the separately rounded budget estimates, supplies E. These proposed ceilings grant no budget now.

The **256 X2-equivalent-hour ceiling** remains a proposal for the conservative d=1 case, outside A15, with support and reserves inside it. The operator's budget decision selects a service state and its matching table budget estimate and approves that state's charged-hour ceiling; the lower estimates confer no authority to change service state or spend. The table's 256-hour comparisons do not automatically adopt that ceiling for every alternative. Wall figures are planning budget estimates, not ceilings; project ceilings are X2-equivalent hours. Actual measured rates, memory, owner agreement or service variability may invalidate any budget estimate; freeze and reprice the exact load sheet before the go. Failed attempts are charged and retained.

Sensitivity **budget estimate**, unchanged from v1: substituting the 16-worker factor 0.605917 for table/label/run compute in the d=1 case, while retaining s for the sparse A13/A14 group, gives 197.7403 X2-2 wall hours and 133.0925 X2-equivalent hours including support. This is a less conservative transfer assumption, not a smaller authorized sample or an expected runtime. The proposed conservative ceiling rests on the sparse scenario instead. No new X2-2 pass was performed or claimed.

The new allowance is for this host's original-identity environmental pass and associated support only. Launch-identity qualification, join-time configuration and registered execution are charged to the launch's own component allowance, as the amendment's section 4 states. Future hosts have no automatic allowance. No phase 2 engineering time or additional compatibility attempt is disguised as the 256-hour prerequisite budget.

## 5. Stage 2 wall-time budget estimates and the ceiling check

**The prize and its serial cost, all budget estimates at 24 hours per day:** against X2-1 alone, full sharing with a continuously generating resident model saves **8.25 campaign days** but adds **13.69 prerequisite days**; d=0.5 saves **9.66 days** and adds **6.89 days**; owner-agreed idle residency saves **10.94 days** and adds **4.72 days**; clean Performance saves **20.36 days** and adds **2.33 days**, excluding owner relocation. The first three full-sharing cases fail component ceilings at the assumed participation rates. Their illustrative budget-preserving subsets save only **0.98, 0.78 and 0.88 days**, respectively; the clean case retains its full **20.36-day** saving within the listed component ceilings. These estimates rest on the measured X2-1 factors transferred to X2-2, the plan's class mix and the serial prerequisite arithmetic in section 4, not on observed X2-2 performance.

With continuous generation, the conservative prerequisite already exceeds the first campaign's conditional full-sharing saving by **5.44 days**, and exceeds the budget-preserving subset saving by **12.71 days**, both budget estimates. Owner-agreed idle/reduced activity lowers the prerequisite, but its better scalar charge rate does not cure memory-limited component overruns in these transfers. A clean Performance host removes the assumed memory/rate penalties and fits the component checks. Reusing a completed qualification across eligible later work, or approved overlap of distinct prerequisites, can change the serial comparison; no such saving is taken here.

The plan's conservative class mix has 4,000 primary, 150 double-population and 150 double-length estimation sources across four families. It budgets the all-FV envelope, not a prediction of the unknown realized routes. Square-root alone adds at most 4,125 labels; runs total 9,800. Using the plan's worker-seconds and capacities gives these reference class hours:

| Reference class | X2-1 class-hour budget estimate | X2-1 / X2-2 capacity budget estimates |
|---|---:|---:|
| Estimation primary | 35.318100 | 31 / 15 |
| Estimation double population | 5.110064 | 17 / 7 |
| Estimation double length | 5.549600 | 17 / 7 |
| FV validation primary | 664.712222 | 7 / 3 |
| FV validation double population | 102.302833 | 3 / 1 |
| FV validation double length | 100.656833 | 3 / 1 |
| Census primary | 1.163297 | 31 / 31 |
| Census double population | 0.131539 | 31 / 31 |
| Census double length | 0.055031 | 31 / 31 |
| Square-root labels | 51.553819 | 16 / 9 |
| 500-step runs | 10.535878 | 31 / 22 |

Sum 977.089218 hours of class work; retain 13.500782 hours of the rounded family total as serial operational/publication allowance, giving **990.59**. This residual arithmetic preserves the committed rounded total, not a measured overhead. Let W_c be a row's reference budget hours, a_c and b_c the reference/X2-2 capacities, and q_c the transferred per-worker factor. The **budget-estimate** formula is:

`family wall = 13.500782 + sum_c W_c / (1 + q_c*b_c/a_c)`.

It assumes phase-by-phase divisible work, both hosts available throughout each relevant class, no network/queue penalty, no extra gain from mixed packing, no failed jobs and unchanged class durations. Those are assumptions. Barriers, service variability, few-source tails and extra host configuration can make actual wall time longer. Both host placements must be permitted by the measured load sheet and the component ceiling.

The following table places all four service states on the same basis. Every computed cost, wall time, saving and ceiling-fit result is a **budget estimate**. Family-only X2-1 wall is 990.59 hours; the complete prior-program comparison is 1122.59 hours after the unchanged 58-hour prerequisite/preparation/reading allowance and 74-hour release allowance. The new X2-2 prerequisite is shown separately, not hidden in the campaign saving.

| X2-2 service state | Four-family / prior-program wall budget estimate, h | Full-sharing campaign wall saving budget estimate, h / days | New prerequisite budget estimate, charged X2-equivalent h; serial wall h / days | Full-sharing component-ceiling check at proxy rates | Budget-preserving subset saving budget estimate, h / days |
|---|---|---|---|---|---|
| Resident, generating d=1 | 792.52 / 924.52 | 198.07 / 8.25 | 215.93 (rounded 220); 328.63 / 13.69 | Fails: large validation 415.23 >400; sigma validation 167.69 >160; sigma estimation 9.014 >9 | 23.48 / 0.98 |
| Resident, d=0.5 | 758.81 / 890.81 | 231.78 / 9.66 | 127.70 (rounded 130); 165.47 / 6.89 | Fails: large estimation 22.14 >22, validation 425.17 >400; sigma estimation 9.203 >9, validation 171.66 >160 | 18.81 / 0.78 |
| Resident, idle d=0 | 727.92 / 859.92 | 262.67 / 10.94 | 100.10 (rounded 105); 113.28 / 4.72 | Fails: large estimation 22.53 >22, validation 434.34 >400; sigma estimation 9.378 >9, validation 175.32 >160 | 21.08 / 0.88 |
| Clean, Performance | 502.05 / 634.05 | 488.54 / 20.36 | 55.99 (rounded 56); 55.99 / 2.33 | Fits all listed components; full sharing is the budget-preserving choice | 488.54 / 20.36 |

The unchanged 58 hours are X2-1 original-identity requalification 48, shared preparation 4 and sealed readings 6. Release 74 is the prior budget estimate, not measured remaining effort after phase 1; section 7 requires repricing before the phase 2 build is briefed, so totals retaining 74 are comparison budget estimates, not a fresh release approval. No parallel acceleration of prerequisites or readers is assumed. Conditional A16 rounds retain 36-hour budget estimates and 48-hour ceilings each; their eligible job counts are unknown, so no N-host acceleration is predicted. If all eight opportunities are budgeted, add 288 reference wall hours as an explicitly serial budget envelope, not an expectation of refusal or use.

The clean-second-X2 calculation is exactly section 6's clean-third-X2 calculation with the memory-poor host withheld: **family wall budget estimate** `13.500782+977.089218/2=502.045391 hours`. It assumes X2-2's owner has relocated the service, 123 GB available, Performance mode, reference capacities and measured rates that confirm the assumed unit rate. It is not an additional hardware advantage or permission to relocate a service.

**Ceiling arithmetic, budget estimates:** for a phase with two joined hosts, charge `(shared compute wall + phase operational allowance)*(1+rho)`. The operational allowances used are 1/3 hour per estimation or run launch, 2 hours per validation, and 5/6 hour for labels, as in v1; publication remains on X2-1. Two large families each have 1375/60/60 sources and 4400 runs; two sigma families each have 625/15/15 sources and 500 runs. Large estimation/validation/run ceilings are 22/400/8 X2-equivalent hours; sigma ceilings are 9/160/2; square-root labels have 70. No component's unused allowance offsets another's excess.

For example, central d=1 large validation is `(249.2207+2)*(1+0.652839)=415.23`, above 400. For d=0.5 and d=0 the same class/capacity formula gives 425.17 and 434.34: increasing the scalar participation proxy can raise charge faster than memory-limited work contribution. Clean validation instead gives `2*(310.1532045/2+2)=314.1532`, below 400. These are budget estimates, not ledger rates or measured validation times. The full component check is:

| Component, per family where applicable | Ceiling, X2-equivalent h | d=1 charge budget estimate | d=0.5 charge budget estimate | d=0 charge budget estimate | Clean charge budget estimate |
|---|---:|---:|---:|---:|---:|
| Large estimation | 22 | 21.7083 | 22.1360 | 22.5291 | 17.0711 |
| Large validation | 400 | 415.2272 | 425.1730 | 434.3450 | 314.1532 |
| Large runs | 8 | 6.0185 | 6.0620 | 6.1049 | 5.3971 |
| Sigma estimation | 9 | 9.0142 | 9.2030 | 9.3781 | 7.2511 |
| Sigma validation | 160 | 167.6928 | 171.6579 | 175.3188 | 128.3577 |
| Sigma runs | 2 | 1.1723 | 1.2107 | 1.2490 | 1.2042 |
| Square-root labels | 70 | 64.9278 | 65.7171 | 66.4354 | 53.2205 |

The **budget-preserving subset estimates** share only phases passing those checks, with join/exit at recorded phase boundaries. At d=1, share the two large estimations, square-root labels and all runs; leave all validations and sigma estimations on X2-1, giving 967.11 family wall hours and 23.48 hours saved. At d=0.5 and d=0, share only square-root labels and all runs, giving 971.78 and 969.51 family wall hours and 18.81 and 21.08 hours saved. Clean shares every listed phase, giving 502.05 family wall hours and 488.54 hours saved. These illustrative subsets are not optimized schedules or permission to cut work; every job remains. Leave X2-2 off the ledger outside its shared phases, and allow for any additional configuration/support before a go. Near-ceiling phases need exact-spec repricing.

If every prerequisite is outstanding and serial, the **full-sharing prior-program-plus-new-prerequisite wall budget estimates** are 1253.15 hours at d=1, 1056.28 at d=0.5, 973.21 at d=0 and 690.04 clean, versus 1122.59 for the one-host basis. The first three require resolution of the listed component overruns. With the budget-preserving subsets instead, the corresponding **wall budget estimates** are 1427.74, 1269.25, 1214.79 and 690.04 hours. They exclude owner relocation and unpriced additional release work. Eligible prerequisites may overlap on different hosts if approved, but no overlap saving is taken here. Measuring appropriate participation/class rates, selecting a fitting host subset or obtaining a budget decision must resolve an overrun before launch; no ceiling is silently moved.

The unchanged d=1 sparse campaign stress-transfer **budget estimate** remains 871.57 family wall hours, 929.57 with the 58-hour allowance and 1003.57 with the prior 74-hour release allowance; it saves only 119.02 hours (4.96 days) before the separate prerequisite. This sensitivity is not substituted for the central four-state comparison or claimed to be a measured bound.

## 6. A third same-class host, and an X3

Assume a third X2 has a clean 123 GB available-memory basis, 0.8 headroom, the same Performance state, no resident model interference, and achieves the reference per-class rate. These are **budget-estimate assumptions**, not facts about an unarrived machine. Its capacity vector equals X2-1's. With X2-2 still present, replace the denominator by `2+q_c*b_c/a_c`.

The resulting **budget estimates** for four-family wall time are **446.84 hours** under the central d=1 transfer and **470.31 hours** under the sparse stress transfer, versus 792.52 and 871.57 with two hosts. Keep the same 58-hour and 74-hour serial allowances if comparing the complete prior program. Each new host's own qualification cost is extra and unpriced until its workload/state is known. A third X2 instead sharing an identical resident generating model would add only another `q_c*b_c/a_c`, not a clean unit of capacity.

A clean third X2 alongside X2-1, with memory-poor X2-2 withheld from expensive classes, gives a simpler **family wall budget estimate** of `13.500782+977.089218/2=502.045391 hours`. Charging two unit-rate hosts during the divisible compute keeps compute charge unchanged; duplicate support/idle time still consumes budget. It can be a better cost fit than keeping a poorly matched host joined throughout FV work. These alternatives illustrate class placement; they select no future host and authorize no budget.

For an X3, no numerical speed, memory or cost advantage is assumed. Substitute measured CPU/memory reservations, per-class rates and scalar participation rate only after its own fixed-code and final-identity passes. Bit identity across silicon generations is an empirical gate. Failure excludes that host/identity and does not alter the study, sample or accepted hosts.

## 7. Required tooling before the first multi-host launch

Static inspection is at `50a3d096`, candidate identity `57141a5731dfe3dbf334e4c9374559afe873c12e5c6c354b5869e0ffbdff777e`. The root Python modules below are included by `artifacts.source_manifest`; modifying them changes the successor identity. This inventory is a required implementation/review plan, not an implemented or tested patch. Under option C, this campaign remains X2-1 only in Performance mode; X2-2 is not requalified, its service is not touched, and its earlier numerical cases are illustrations, not proposed admission or approved budgets. Class-aware placement, committed-register enforcement in the coordinator and A11 pull transport for A16 kinds must be carried by the successor identity serving the first A17 multi-host launch, before that launch's A11 proofs. This timing supersedes the earlier phase 2 timing references in this companion for those multi-host items. Phase 2 retains A16 item 2's remaining single-host scope, the A17 pin move and its applicable service-safety and per-kind-validator repairs; it does not acquire the deferred multi-host tooling. A later identity carrying that tooling takes its own direct A11 records; no transitive acceptance is introduced.

| Manifest file and current sites | Existing behavior | Required A17 integration |
|---|---|---|
| `multihost_a11.py:26,57 to 119,166 to 205,493 to 563,653 to 681,750 to 798` | Kind whitelist excludes A16; registered A14 pull remains refused; launch-local register and one scalar rate; live memory fit already exists; fastest-host recheck uses a scalar | [first multi-host identity] Bind committed host-register revision and per-launch approvals; [first multi-host identity] validate per-host environment/service evidence; [first multi-host identity] add both A16 kinds and class-rate/capacity advertisement; [first multi-host identity] select eligible class-fitting hosts and update remaining-cost forecasts; [first multi-host identity] segment rate changes; [first multi-host identity] preserve old A14 refusal and scientific finality |
| `multihost_a11.py:806 to 940,1013 to 1015` | A13/A14 checkpoint and halt RPC paths only | [first multi-host identity] Add A16 round-specific durable checkpoint/lease/halt operations, exact duplicate comparison, late-return handling and unchanged family/round latches; [first multi-host identity] no checkpoint from another round/root |
| `host_a11.py:125,150 to 185,252 to 426,426 to 458` | Runtime fingerprint, scratch/transport execution and A14 checkpoints; X2 wrapper can stop/restore the selected model service | [first multi-host identity] Bind expanded runtime/power/service-owner fingerprint; [phase 2] control no other session's service absent the recorded owner's agreement, authorized actor/actions, envelope and duration; [phase 2] preserve the `llm down` ownership limit; [first multi-host identity] advertise actual class capacity and rate, [phase 2] preserve model residency/activity logging, [first multi-host identity] add A16 transport and resume/halt contexts |
| `qualification_a11.py:23 to 118,135 to 273,275 onward` | Frozen per-kind jobs, exact comparison, hard-coded reference endpoint, scalar elapsed rate and separate per-job scheduling rate; old-kind seed handling; `validate_evidence` at line 249 checks 20 distinct jobs in total | [first multi-host identity] Resolve reference through public register identity; [phase 2] retain exact selection/comparison; [phase 2] in phase 2 make the final `validate_evidence` check enforce at least 20 distinct jobs per kind, not a pooled total; [phase 2] add A16 non-reserved profile streams and kind coverage; [first multi-host identity] bind host-specific fixed-code pass and launch identity; [first multi-host identity] report per-class join measurements without pretending the short proof is full memory authority |
| `production_runner.py:166 to 205,313 to 324,330 onward,638,710,844,1002` | Dispatch, class memory/configuration, A13/A14 execution and pull delegation | [first multi-host identity] Carry register/class constraints consistently in local and remote paths; [phase 2] add A16 execution/resume/checkpoint guards; [first multi-host identity] log per-class configuration timing and charge intervals; [phase 2] preserve scientific jobs, seed guards, nondeterminism sample and deadlines |
| `worker_control.py:224 to 286,337 to 382,477 to 561` | Registered class reservations and item-10 weights; distributed load-sheet forecast partitions by total workers times scalar speed before memory packing | [first multi-host identity] Produce per-host/per-class capacity and speed rows; [first multi-host identity] reject infeasible class assignments before forecasting; [first multi-host identity] carry class caps alongside unchanged weighted admission; [first multi-host identity] no global scalar masquerading as a class-aware schedule |
| `tables_a10.py:314 to 654` | Phase 1's committed stage 2 path, job, seed-registry and spec builders | [first multi-host identity] Bind A17 host authority/subset and frozen scheduling extension without editing scientific configurations, canonical paths, seed sources or job/run identifiers |
| `snapshot_a11.py:74 to 110` and its staging/input-view branches | Explicit historical-root declarations and verified alias repair already present | [phase 2] Retain the repair and extend explicit A16/relocation input closure; [phase 2] no undeclared fallback; [first multi-host identity] prove inside/outside-checkout staging on both host transports |
| `artifacts.py:218 to 261`, shared selectors in `table_validation_a4.py` and `table_labels_a5.py` | Strict current note pin is `ae71028e`; callers distinguish historical/current plans | [phase 2] Bind the adopted A17 commit/marker for the opt-in successor, preserving A15/A16 and strict historical verification; [phase 2] retain `ae71028e` in the A13 binding list when the current pin moves, because every commit at which a current A10 plan could have been pinned stays bound; [phase 2] recheck prospective Part 2 and no-label receipt branches; [phase 2] no broad arbitrary-note acceptance |
| `service.py`, `worker_safety.py`, `dispatch_store_a11.py` and new A16 modules as needed | Shared ownership-independent controls, safety, durable leasing and incomplete future round support | [phase 2] Review exact interfaces; [phase 2] modify only where necessary, [phase 2] include every actual diff in the manifest/proof record, and [phase 2] retain restart/swap/effective-thread controls and durable single completion |

The current coordinator already filters by kind and live memory; it is not wholly unaware of resources. The missing requirement is the explicit per-class host-rate/capacity/register contract and matching forecast/placement, not new randomization. `worker_control.distributed_load_sheet` currently assigns using worker target times one rate; it does not itself establish the proposed class-aware policy. A16 pull transport is a real pending implementation, not a flag change. Historical runbook service-stop commands for the other session are not authority to stop its current service. Before original-identity requalification, review and hash an external harness that enforces the recorded ownership and sharing agreements without changing the historical simulation identity. In the successor, enforce those agreements before every service action through service.command, service.run_with_service and host_a11.host_service, including exception and restoration paths. Expired or out-of-scope authority permits no service action. Keep llm down restricted to authorized Lineage-owned services, and record no-control operation explicitly.

**Snapshot confirmation:** reconstructing the LF-normalized manifest at A14 build commit `8b176c73` and adoption commit `ae71028e` gives `174ab6600e0bc3514ee4b0f553a85b5e426aea4203621125debfa3cd12fd5afd`. At phase 1 commit `50a3d096` it gives the stated `57141a57` identity. In all three, `snapshot_a11.py` hashes to `55c8096ae31b5a8772249942c09690eaa0313f55e6ebf1d1a2cedac2c452e34b` and `qualification_a11.py` to `424a4d82cc6d1ee54d306956bde108ec451622883e5efe301ff1d614959014c4`. A14 registration lines 2569 to 2581 specify the repair; source contains the explicit declaration, read-only copy and alias validation. This confirms carry-forward of the repair, not completion of new multi-host A16 rehearsals.

No implementation runs here. This section inventories the required tooling before the first multi-host launch. For this campaign, phase 2 repricing covers A16 item 2's remaining scope only, with the pin move and applicable service-safety and per-kind-validator repairs identified above; the multi-host additions are excluded from that scope. Re-estimate the release cost against that scope and check it against the unchanged 96 X2-equivalent-hour ceiling; if it does not fit, obtain an operator budget decision as a dated budget amendment before the phase 2 build is briefed. The 74-hour figure remains only a prior budget-estimate comparison basis until that review; no release allowance is silently increased. No measured engineering-velocity estimate is available, so no new human schedule or invented release charge is supplied.
