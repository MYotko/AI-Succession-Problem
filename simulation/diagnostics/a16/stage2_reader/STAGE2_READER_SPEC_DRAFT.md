# Stage 2 sealed reader: specification draft (2026-11-21)

Status: draft for interpreter review. No reader code was written. No run output, table row, cell result, label, receipt content or stage 1 reading output was opened to write this.

## 0. Verdict

**The contract can be frozen from what is committed at `4dcc18c2`. The arithmetic is settled and already in the instrument's code. What is not settled is the comparator's hash binding and two reporting conventions, and the main operational risk is refusal at input verification, which cost stage 1 at least six registered attempts.**

Ranked by what can actually hurt the reading:

1. **Comparator binding (blocking).** The stage 1 nominal runs are the comparator for all 14 comparisons. I found no stage 2 inventory that binds them, and the stage 1 record that does is outside my allowlist. The input contract cannot be frozen until one sealed record is named for it (open question 2).
2. **Input-layout refusals (high).** Stage 1's readers were built on fixtures and refused repeatedly on the real layout (`READER_SPEC.md:271`, `:282`, `:297`). This draft adds a value-free `verify` phase and takes every field location from the native writers. Whether `verify` may run on the real inputs under its own go is an operator decision (open question 3).
3. **Missing incidence coercion (high, and fixed by design here).** Both stage 1 readers turn a missing `a13_decision_incidence` into "unassessed" or a fabricated zero (reader A `incidence.py:133-134`, `:146`; reader B `incidence.py:143-147`). That is exactly what requirements section 3 forbids. The three-case logic in section 4 replaces it in both builds.
4. **Two reporting conventions (medium).** The verdict string for a not-run arm, and the comparison key spelling, on which the two stage 1 readers disagree (open questions 4 and 5).

The requirements table (components, 18 and 33, levels, tails, seeds) agrees with the registration and the code. I found no disagreement in it. Three statements in the requirements are stale against `4dcc18c2`; they are listed in open question 1 and change nothing.

**Recommendation on the build path:** a fresh package per builder, `simulation/reading_stage2/`, that copies in and re-hashes the builder's own stage 1 infrastructure modules. Do not extend `reading_a10` in place. Reasons are in section 7.

### 0.1 Labels and citation keys

Every statement carries one of these, at the end of the sentence or in the table's basis column:

- **[M] measured:** I computed or observed it in this session (a file hash, a name that exists in a git tree, a count in an inventory I parsed).
- **[R] read:** taken from the cited file and line. I did not execute it.
- **[I] inferred:** follows from read sources by reasoning that I state.
- **[G] guessed:** an estimate with no source that settles it.

Citation keys:

| Key | File |
|---|---|
| DN | `simulation/diagnostics/v3_rerun_design_note.md` at `4dcc18c2`, sha256 `a99f228c…0554` [M]. This is the hash the stage 2 launch pin records (`crowding/runs_plan.json`, `registration.sha256`) [M]. |
| REQ | `STAGE2_READER_REQUIREMENTS.public.md`, sha256 `685f05ec…52d5` [M], equal to the hash A16 freezes (`AMENDMENT_A16_adopted.md:74`) [R] and to the repository copy under `simulation/diagnostics/a16/` [M]. |
| PLAN | `STAGE2_PLAN.public_v2.md` |
| A16 | `AMENDMENT_A16_adopted.md` |
| APP | `APPROVALS_v3.md` |
| RS | `codex_blind/a10_reading/READER_SPEC.md` (stage 1 contract, with addenda through 3.6) |
| CC | `v3_reader_codex/reading_reports/COLLECTION_CONTRACT.md` |
| rA/ | reader A, `v3_reader_codex/simulation/reading_a10/` |
| rB/ | reader B, `v3_reader_claude/simulation/reading_a10/` |
| INV-S | `SQRT_READING_INPUT_INVENTORY.json`, file sha256 `c2907f1c…a4c3`, seal `56cb22c8…f9f9` [M] |
| INV-C | `CROWDING_READING_INPUT_INVENTORY.json`, file sha256 `aa4694a2…4f98`, seal `e1e9be12…6a87` [M] |
| bare `name.py:n` | `simulation/v3/name.py` at `4dcc18c2` |

### 0.2 Identities the reader runs under

- **Running identity:** `code_identity()` must equal `93a453b27c82a9cb16ed0d04b1029168014b73c1f3d97f5b884e1b6d52f161da`. Both inventories record this identity for the stage 2 roots (INV-S `identity.code_identity`, INV-C `identity.code_identity`) [M]. INV-C records it at checkout `4dcc18c2` [M]. I did not call `code_identity()` myself; `git diff --name-only a2b930e0 4dcc18c2 -- simulation` lists only data records, no source file [M], so the identity at the two checkouts is the same [I].
- **Registration pin:** commit `3b8d8261c47b436a95fe831bd7192ede08460d1e`, path `simulation/diagnostics/v3_rerun_design_note.md`, sha256 `a99f228c…0554` (`artifacts.py:389`; `crowding/runs_plan.json` `registration`) [R, M].
- **Comparator producer:** `174ab6600e0bc3514ee4b0f553a85b5e426aea4203621125debfa3cd12fd5afd` (RS:162, `REQUIREMENTS_DIGEST.md:69`) [R]. It is accepted at the running identity only through a valid committed A11 record (`compatibility_a10.py:104-113`). The record name for the pair (174ab660, 93a453b2) is `A11_compatibility_e2c1bf90e8c45b7b5559e4bd.json` by `record_name` (`compatibility_a10.py:33`), and a tracked file of that name exists at `4dcc18c2` [M]. I did not open it; its validity is checked by `accepted_identities()` at run time.
- **Acceptance rule:** the single source of truth is `v3.compatibility_a10.accepted_identities()`, as in stage 1 (RS:163). The reader keeps no producer list of its own.
- **Where the reader lives:** a package directory under `simulation/` that is not `v3/` and holds no top-level `simulation/*.py`. `source_manifest()` hashes only `v3/*.py`, top-level non-test `simulation/*.py` and four JSON records (`artifacts.py:234-250`), so the package does not change the running identity [R]. Each build confirms this by asserting `code_identity()` before and after.
- **Environment:** `PYTHONINTMAXSTRDIGITS=0` for every reader run (RS:222; PLAN:340). `python -B`, one numerical library thread.

## 1. The comparison registry

### 1.1 Identity strings

The two stage 1 readers spell comparison keys differently. Reader A writes `A10arm.<arm>.boundary` and `A10arm.<arm>.capstar.<alpha>` (rA/`statistics.py:101`, `:113`). Reader B writes `A10arm.boundary.<arm>` and `A10arm.capstar.<arm>.<alpha>` (rB/`arms.py:121`, `:126`; rB/`values.py:99-100`; rB/`tests/test_end_to_end.py:135`) [R]. RS:57 pins only `A10arm.<comparison>`. So "the stage 1 naming" is not unique.

**This draft pins one form.** A comparison's identity is the registry tuple `(kind, arm, alpha)` in the field order of `reading_a6.headline_comparisons()` (`reading_a6.py:231-232`), with `kind` in `{"boundary", "cap_star"}` and `alpha` absent for a boundary. Its string is:

```
<family>.<kindkey>.<arm>            for a boundary
<family>.<kindkey>.<arm>.<alpha>    for cap*
```

with `family` in `{"A10arm", "A6"}`, `kindkey` `boundary` or `capstar`, and `<alpha>` Python `repr` of the float. This is reader B's spelling. Reason: it follows the registry's own field order, and sorting the strings within a family equals sorting the tuples, which is the order A12 item 6 registers (DN:1872) [I]. Reader A adapts its spelling. Open question 5 asks the interpreter to confirm.

### 1.2 The 14 comparisons

Common to all 14 [R unless marked]: 50,000 resamples (DN:1861; `reading_a6.py:37`); quantiles by `inverted_cdf` (`reading_a6.py:173-174`, `:386-387`); two sides resampled independently by seed within cell (DN:1391); runs sorted by job identifier within each cell on both sides before the helpers build cells (DN:1874); a fresh `numpy.random.default_rng(seed)` inside each helper call (`reading_a6.py:356`, `:421`); comparisons called in sorted order of identity (DN:1872). Because every call creates its own generator from the same seed, call order fixes the output order and cannot change any value [I].

| # | Identity string | Arm family, run group | Statistic | Level alpha | Undefined tail | RNG seed |
|---:|---|---|---|---|---|---:|
| 1 | `A10arm.boundary.sqrt` | sqrt | boundary | 0.05/18 | 0.05/36 | 20261011 |
| 2 to 6 | `A10arm.capstar.sqrt.<a>`, a in 0.5, 0.75, 1.0, 1.25, 1.5 | sqrt | cap* | 0.05/18 | not applicable | 20261011 |
| 7 | `A6.boundary.crowding` | crowding | boundary | 0.05/33 | 0.05/66 | 20260929 |
| 8 | `A6.boundary.sigma_squared_x0.1` | sigma_squared_x0.1 | boundary | 0.05/33 | 0.05/66 | 20260929 |
| 9 | `A6.boundary.sigma_squared_x10` | sigma_squared_x10 | boundary | 0.05/33 | 0.05/66 | 20260929 |
| 10 to 14 | `A6.capstar.crowding.<a>`, same five a | crowding | cap* | 0.05/33 | not applicable | 20260929 |

Rows are in the registered call order within each component. Basis: family sizes 18 (DN:1643-1644: three A10 arms, each a boundary plus cap* at five alpha, and DN:1879: stage 1 read 12 of them) and 33 (DN:1389; `reading_a6.py:34`, `:222-234`) [R]. Levels DN:1643 and DN:1393. Tails DN:1876. Seeds DN:1872-1873. The level is `1 - alpha`.

**The denominators 18 and 33 are literals.** They never become 6, 8 or 14 and never depend on how many arms ran (REQ section 1; DN:1880).

### 1.3 Cells

Grids [R]: `R1_RR = (.055, .056, .057, .058, .059, .060, .062, .064, .066)` (`study.py:5`); `SIGMA_GRID = (0.059, 0.060, 0.062, 0.064, 0.066)` (`reading_a6.py:45`; `sensitivity_a6.py:25`); `R2_ALPHA = (.5, .75, 1., 1.25, 1.5)` and `R2_CAP = (1.2, 1.5, 2., 2.5, 3., 4., 5.)` (`study.py:9-10`); cap* reads rr 0.064 only (`reading_a6.py:46`).

| Comparison | Arm cells (rr, alpha, first successor capability) | Arm runs | Comparator cells | Comparator runs |
|---|---|---:|---|---:|
| 1 sqrt boundary | 9 R1 rr, 1.0, 1.5 | 9 x 100 = 900 | main, category `R1`, same 9 rr, 1.0, 1.5 | 9 x 400 = 3,600 |
| 2 to 6 sqrt cap* at a | 0.064, a, each of 7 capabilities | 7 x 100 = 700 each | main, category `R2`, 0.064, a, 7 capabilities | 7 x 75 = 525 each |
| 7 crowding boundary | 9 R1 rr, 1.0, 1.5 | 900 | as comparison 1 | 3,600 |
| 10 to 14 crowding cap* at a | as 2 to 6 | 700 each | as 2 to 6 | 525 each |
| 8, 9 sigma boundary | 5 sigma rr, 1.0, 1.5 | 5 x 100 = 500 | main, category `R1`, the same 5 rr, 1.0, 1.5 | 5 x 400 = 2,000 |

Counts are arithmetic on the registered grids and seed counts (`reading_a6.py:241-244`; `tables_a10.py:315`) [I]. The comparator's distinct contributing runs are 3,600 + 5 x 525 = 6,225 of main's 24,900 [I]. The crowding plan copy holds 44 cells of exactly 100 jobs, 9 with `a6_grid` `R1` and 35 with `R2` [M].

The comparator never includes the refinement grid, and R1 and R2 runs are never pooled although the cell (0.064, 1.0, 1.5) exists in both (DN:1387; REQ section 2). The `category` filter enforces this.

### 1.4 Where the cell fields come from

The reader builds one flat record per contributing run from the job definition and the output. No other field of the output enters a headline statistic.

| Record field | Source | Basis |
|---|---|---|
| `job_id` | `job["id"]` | `artifacts.py:257-273` |
| `component` | `main`, `sqrt`, `crowding`, `sigma_squared_x10`, `sigma_squared_x0.1` | reader input |
| `category` | `config["category"]`: `R1`, `refinement`, `R2`; `a10_arm`; `a6_crowding`; `a6_sigma_squared_x10`; `a6_sigma_squared_x0.1` | `study.py:41-48`; `tables_a10.py:234`; `sensitivity_a6.py:320`, `:361`, `:376` |
| `grid` | sqrt: `config["grid"]`; A6 arms: `config["a6_grid"]`; main: equal to `category` | `tables_a10.py:234`; `sensitivity_a6.py:320`; rA/`diagnostics.py:81` |
| `arm`, `variant` | `config.get("a6_arm")`, `config.get("a6_variant")`; `None` when absent | `sensitivity_a6.py:322` |
| `rr`, `alpha`, `capability` | `model["reproduction_rate"]`, `model["alpha"]`, `model["successor_capability"]` | `sensitivity_a6.py:318`; `tables_a10.py:237` |
| `kappa`, `theta`, `crowding` | `model` value when present, else the model defaults 8.0, 0.5, `"total"` | `integration.py:54-55` |
| `steps` | `config["steps"]` | `tables_a10.py:234` |
| `k_star`, `g` | `model["instrument"]` | `tables_a10.py:232-238` |
| `final_population` | `output["result"]["final_population"]` | `production_runner.py:303` |
| `fired` | `v3.gates.fire_from_run(output)`: true when the recorded capability path ever strictly increases | `gates.py:505-515` |

Survival is `final_population >= 30` (`reading_a6.py:30`, `:63-65`). A succession from 5.0 to 5.0 is not a fire, as in stage 1 (RS:317).

Before use, the reader checks `result["population_path"][-1] == result["final_population"]` and `result["survived_threshold_30"] == (final_population >= 30)`, as both stage 1 readers do (rA/`preflight.py`, "population consistency"; rB/`extract.py:66-68`) [R].

### 1.5 The grid and filter contract

Cells are built with `reading_a6.arm_and_comparator_cells` (`reading_a6.py:287-302`), which applies `select_boundary_cells` (`:251-267`) and `select_capstar_cells` (`:270-284`). A cell whose count differs from the expected seed count raises (`:264-265`, `:281-282`); the reader turns that into a refusal. Records are sorted by `job_id` before the call.

Filters, matched by exact equality on every key (`reading_a6.py:247-248`):

| Comparison | `arm_filters` | `comparator_filters` | Other arguments |
|---|---|---|---|
| sqrt boundary | `component: "sqrt"`, `category: "a10_arm"`, `grid: "R1"`, `alpha: 1.0`, `capability: 1.5`, `kappa: 8.0`, `theta: 0.5`, `steps: 500`, `crowding: "total"`, `variant: None`, `k_star: 1.8`, `g: "sqrt"` | `component: "main"`, `category: "R1"`, `alpha: 1.0`, `capability: 1.5`, `kappa: 8.0`, `theta: 0.5`, `steps: 500`, `crowding: "total"`, `variant: None`, `k_star: 1.8`, `g: "linear"` | `grid=R1_GRID`, `arm_seeds=100`, `comparator_seeds=400` |
| sqrt cap* at a | as above with `grid: "R2"` and without `alpha` and `capability` | as above with `category: "R2"` and without `alpha` and `capability` | `alpha=a`, rr 0.064, `arm_seeds=100`, `comparator_seeds=75` |
| crowding boundary | `component: "crowding"`, `category: "a6_crowding"`, `arm: "a6_crowding"`, `grid: "R1"`, `variant: "crowding_reproductive"`, `crowding: "reproductive"`, `alpha: 1.0`, `capability: 1.5`, `kappa: 8.0`, `theta: 0.5`, `steps: 500`, `k_star: 1.8`, `g: "linear"` | the sqrt boundary comparator filter | `grid=R1_GRID` |
| crowding cap* at a | as above with `grid: "R2"`, without `alpha` and `capability` | the sqrt cap* comparator filter | `alpha=a` |
| sigma boundary, variant v | `component: v`, `category: "a6_" + v`, `arm: "a6_" + v`, `grid: "R1"`, `variant: v`, `crowding: "total"`, `alpha: 1.0`, `capability: 1.5`, `kappa: 8.0`, `theta: 0.5`, `steps: 500`, `k_star: 1.8`, `g: "linear"` | the sqrt boundary comparator filter | `grid=SIGMA_GRID` |

The arm-side values are the builders' (`tables_a10.py:229-241`; `sensitivity_a6.py:356-381`, `:310-322`) [R]. The crowding values match the plan copy's first job [M]. The comparator's crowding is `"total"` and its variant `None`: the comparator is the nominal instrument (DN:1387) [R].

### 1.6 The helper calls, the draw order and the rules

**Boundary** (comparisons 1, 7, 8, 9):

```
reading_a6.compare_boundary(arm_cells, nominal_cells, grid=<grid>, resamples=50000,
    seed=<family seed>, sigma_variant=<True for 8 and 9, else False>,
    alpha=<0.05/18 or 0.05/33>, strict=True,
    undefined_resample_tail=<0.05/36 or 0.05/66>)
```

Every keyword is passed explicitly for every family, including the A6 default (REQ section 1). The parameter exists at `4dcc18c2` (`reading_a6.py:311`), is validated (`:330-332`), is recorded in the result (`:350`) and in the reason string (`:367-368`) [R]. Neither reader mirrors the helper's body any more; both stage 1 mirrors (rA/`statistics.py:51-74`, rB/`arms.py:30-66`) are retired, because they hard-code the R1 grid and reader B's reason string omits the threshold (rB/`arms.py:62`) [R].

Draw order inside one call [R, `reading_a6.py:356-358`, `:118-130`]: one generator; then for the arm, for each rr in ascending order, one `rng.integers(0, n, size=(50000, n))`; then the same for the comparator. Nothing else draws.

Rules, all in the helper and not re-implemented [R]:

- The boundary is the first upward crossing of 0.5 by linear interpolation; survival exactly 0.5 at the lowest rr is a crossing at that rr; above 0.5 there reads below range; never reaching 0.5 reads above range (`:68-86`, `:133-155`). A8 item 5 pins this rule (DN:1469).
- An undefined point estimate reads `undetermined` with its registered reason and no bootstrap (`:352-355`, `:391-396`). For a sigma variant a boundary below 0.059 reads `sigma0^2 boundary below 0.059` (DN:1337; `:394`).
- Every resample is kept. The undefined share is the fraction of resamples where both sides are infinite in the same direction (`:359-361`). A share **strictly greater** than the tail reads `undetermined` (`:365`).
- Otherwise the interval places undefined resamples at minus infinity for the lower percentile and plus infinity for the upper (`:382-388`).
- Materiality 0.002 in rr: wholly beyond on one side reads `moves_materially_lower` or `moves_materially_higher`; wholly within the inclusive band with both ends finite reads `robust`; anything else `inconclusive` (`:186-201`).

The module constant `SIGMA_BELOW_RANGE` (`:38`) is unused and is not an alternative rule (REQ section 2) [R].

**cap*** (comparisons 2 to 6, 10 to 14):

```
reading_a6.compare_capstar(arm_cells, nominal_cells, a, resamples=50000,
    seed=<family seed>, alpha=<0.05/18 or 0.05/33>, strict=True)
```

Draw order [R, `:421-423`]: one generator; for the arm, for each capability in grid order, one `rng.integers(0, n, size=(50000, n))`; then the comparator. cap* is the largest capability with fire rate at least 0.5, bottom-censored at step -1 and top-censored at 5.0 (`:99-111`, `:158-163`). The difference is in grid steps. `moves_materially_*` when the whole interval is at least one step to one side, with the endpoint at plus or minus 1 included; `robust` only at exactly [0, 0]; otherwise `inconclusive` (`:204-215`; DN:1884-1887). The undefined tail does not apply.

**Descriptive, no verdict:** per-rr survival difference with a 95 percent interval, by `reading_a6.survival_differences(arm_cells, nominal_cells, resamples=50000, seed=<family seed>)` (`:435-451`), on the boundary comparison's cells. Both stage 1 readers used 50,000 and the family seed here (rA/`statistics.py:107`; rB/`arms.py:134-135`), following DN:1861 [R].

**Not computed:** seed convergence, any stage 1 comparison, any stage 1 prediction score, per-cell arm diagnostics summaries (REQ section 2; DN:1881-1882, DN:1904).

### 1.7 How the registry is formed in code

- **A6, eight identities:** take `reading_a6.headline_comparisons()` (33 entries) and keep entries whose `arm` is in `{"crowding", "sigma_squared_x10", "sigma_squared_x0.1"}`. Require exactly 8: three boundaries and five cap* for crowding. Require the remaining 25 to be exactly the four weight corners' boundary and cap* entries plus the horizon boundary, which is the stage 1 set (DN:1879). Any other count is a refusal.
- **A10, six identities:** a frozen literal in the reader: `{"kind": "boundary", "arm": "sqrt"}` and `{"kind": "cap_star", "arm": "sqrt", "alpha": a}` for `a` in `v3.gates.ALPHAS`. `headline_comparisons()` is the A6 registry only and supplies none of these (REQ section 1). The reader records the family literal 18 and names the 12 stage 1 identities (arms `k1p5`, `k2p3`) as the complement, without computing them.
- The registry, with level, tail, seed, resample count, grid, filters and expected counts per comparison, is written into the frozen source as data and hashed into the freeze record (section 8.4).

## 2. The input contract

### 2.1 Roots and files on X2-1

All paths below are relative to the execution checkout's `simulation/`. The plan copy records that checkout as `/home/yotko/v3_stage2_93a453b2/simulation` (`crowding/validation_plan.json`, `source_root`) [M]. The reader runs from its own checkout and takes this root as an input, `execution_simulation`, because job configurations hold path strings relative to it (`production_runner.py:250`, `:265`).

| Item | sqrt | crowding | Basis |
|---|---|---|---|
| Runs root | `v3/runs/a10_stage2/runs/sqrt` | `v3/runs/a10_stage2/runs/crowding` | INV-S, INV-C `roots.runs.path` [M] |
| Phase | `a10_arm` | `a6_crowding` | `roots.runs.jobs_by_phase` [M] |
| Final spec | `v3/runs/a10_stage2/sqrt/runs_plan.json` | `v3/runs/a10_stage2/crowding/runs_plan.json` | `roots.runs.spec.path` [M] |
| Pre-dispatch spec | not in INV-S | `v3/runs/a10_stage2/run_specs/crowding.json` | INV-C `published_files_and_inputs.run_spec_family` [M] |
| Family table | `v3/runs/a10_stage2/sqrt/v3_rerun_tables_A10.json` | `v3/runs/a10_stage2/crowding/v3_rerun_tables_A10.json` | `tables_a10.py:324-325`; inventories [M] |
| Validation receipt | `...A10.compatibility.json` | same pattern | `table_validation_a4.py:866` |
| Cell results | `...A10.cell_results.json` | same pattern | `table_validation_a4.py:867` |
| A10 receipt | `...A10.a10_receipt.json` | same pattern | `tables_a10.py:718`, `:758` |
| Labels | `v3/runs/a10_stage2/sqrt/v3_rerun_labels_A10.json` | none | INV-S `published_files.labels` [M] |
| Identity record | `v3/runs/a10_stage2/sqrt/family_identity.json` | `v3/runs/a10_stage2/crowding/family_identity.json` | inventories [M]; both tracked at `4dcc18c2` [M] |
| Admission check | `v3/runs/a10_stage2/sqrt/validation_run/a13_admission_check.json` [I, by the writer `table_validation_a4.py:838`; not in INV-S] | `v3/runs/a10_stage2/crowding/validation_run/a13_admission_check.json` [M, INV-C] | |
| Calibration | `v3/runs/registered/v3_rerun_calibration.json` | same | `tables_a10.py:324-325` |
| Excluded root | `v3/runs/a10_stage2/sqrt/runs_run`, status `not run`, no record and no output | none | INV-S `failed_attempt` [M] |

The sigma families use `v3/runs/a10_stage2/<family>/...` for table and calibration (`tables_a10.py:326-329`). Their run roots and plans do not exist yet; by the pattern above they will be `v3/runs/a10_stage2/runs/<family>` and `v3/runs/a10_stage2/<family>/runs_plan.json` [I]. This is to be confirmed from their inventories.

Run roots are pull-dispatch roots: each spec carries `pull_dispatch` (plan copy) [M], and the layout is `<root>/<phase>/outputs/<job_id>.json` and `<root>/<phase>/records/<job_id>.json` (`multihost_a11.py:1030-1036`) [R].

### 2.2 Fields read, by file

**Run specs** (sealed, schema `v3-registered-1`; written by `tables_a10.stage2_run_specs`, `tables_a10.py:680-689`): `registered`, `registered_a10`, `tag`, `registration`, `code_hash`, `instrument`, `a10_stage`, `a10_family`, `a10_labels_policy`, `a10_family_paths.{calibration_path, tables_path}`, `phases`, `jobs`, `seed_registry_sha256`, and `pull_dispatch.code_commit`. Each job: `kind`, `config`, `tag`, `index`, `id`, `seed`, `seed_identity` (`artifacts.py:257-273`); the plan copy's jobs have exactly these seven keys [M].

**Completion records** (`multihost_a11.py:1032-1036`): `job`, `code_hash`, `status`, `output_hash`, `host`, `lease`. Not read for any statistic: `completed_epoch`, `worker_seconds`, `peak_rss_bytes`, `oom_score_adj`.

**Run outputs** (`production_runner.py:334-336` for the envelope, `:301-307` for the result): envelope `job`, `code_hash`; result `steps`, `final_population`, `survived_threshold_30`, `population_path`, `fixture_tables`, `yield_events` (count and each event's `time`), `diagnostics` (per step: `time`, `population`, `capability`, `allocation_evaluated`, `survival_first`, `unavailable_rules`), `continuation_availability.allocation_steps`, and `a13_decision_incidence` when present. The packed `gate_evidence` blob (`recording.py:181-192`) is **not** unpacked: no stage 2 quantity needs it [I]. Nothing else is read.

**Family table** (sealed, schema `v3-tables-1`, `production_tables.py:45-46`): `code_hash`, `manifest_hash`, `manifest.{tag, calibration_hash, complete_family, sensitivity_status, required_row_keys, a10, a13_admission, a16, validated_continuation}`, and per row only `status`, `route`, `fv_label`, `rule_id`, `scoring`, `kernel_hash`, `calibration_hash`, `initial_population`, as the native loader reads them (`production_tables.py:55-143`). The reader loads the table only through `ProductionTables(...)`; it reads no continuation value, flow or error.

**Family provenance** `manifest.a10` (`tables_a10.py:93-99`): `family`, `producer_code_hash`, `constants_sha256`, `job_manifest_sha256`, `instruments`.

**Admission binding** `manifest.a13_admission` (`admission_a13.py:73-76`): `schema`, `scope`, `primary_rows`, `rows` (keys only, and the count), `admitted_set_sha256`, `a16` when present.

**Admission check record** (sealed, `admission_a13.py:167-176`): `schema` `v3-A13-admission-check-1`, `scope`, `plan_hash`, `primary_rows`, `cap`, `residual_rows`, `residual_count`, `outcome`, `admitted_set_sha256`. After an A16 round, the round's record at `<stem>.a16_round<q>.admission.json` adds `family`, `round`, `E`, `E2`, `P`, `M`, `alpha`, `extension_error_bound`, `tests_round1`, `tests_round2`, `classifications_sha256` (`validation_extension_a16.py:1270-1280`, `:1343-1344`, `:441-442`).

**Validation receipt** (sealed, schema `v3-A4-receipt-1`, `table_validation_a4.py:852-857`): `table_seal_sha256`, `table_file_sha256`, `producer_code_hash`, `calibration_sha256`, `M`, `M_FV`, `plan_hash`, `cell_results_sha256`. After A16 it also carries `a16`, `a16_rounds`, `refusals`, `labels_policy` (`validation_extension_a16.py:1373-1378`).

**A10 receipt** (sealed). Strict form, schema `v3-A10-table-receipt-1` (`tables_a10.py:714-717`): `table_sha256`, `producer_code_hash`, `constants_sha256`, `validation_receipt_sha256`, `labels_sha256`, and the embedded `validation_receipt` and `labels`. No-label form, schema `v3-A10-table-receipt-nolabel-1` (`tables_a10.py:337`, `:753-757`): `family`, `table_sha256`, `producer_code_hash`, `constants_sha256`, `calibration_sha256`, `validation_receipt_sha256`, `validation_receipt`, `labels_policy`, and no `labels` or `labels_sha256` key.

**Identity record** (plain JSON, 496 bytes for both families [M]; fields `family_file_sha256`, `table_seal_sha256`, `receipt_file_sha256`, `sidecar_file_sha256`, `producing_commit`, `code_hash`, `table_labels_a5.py:163-172`). It is the committed record: its bytes must equal `git show HEAD:<path>` in the reader's checkout (`table_labels_a5.py:117-133` does this for A5) [R].

**Calibrations.** Parent: file sha256 `fd86358a39e3b643fb9adc4e81a2372915ca50a1866e9b0e330a874b41746e01`, seal `bf0f7c3f10310558d567b6b3f7c24f6f99f2fe6eb71fd830cccfd8e2aa0bd6d6` (inventories [M]; `instrument.py:16`). Sigma variants, from `a10_constants.json` `a6_calibrations.variants` [M, read from the file]:

| Variant | `byte_sha256` | `payload_sha256` | `producer_code_hash` | `sigma_factor` |
|---|---|---|---|---:|
| `sigma_squared_x10` | `aecef21ab61e0c7078b7fcf40fee540f9891a0ac3e32e995699cbfbd8264dbce` | `256380ab7c65465766f0407c6f8468dd35dbfaced08c3db72388b1e0882abca9` | `bd656b8f038c73d94c72ee4112806ca784f9ae3f4e4d4b99c0fd8a8d9fdcf7ed` | 10.0 |
| `sigma_squared_x0.1` | `93c35a47e9aed3bd904fdc79ae24feb4015b75eb33bd42aa3a5220ae2ce88394` | `d9cde18fd08d6eabe171115a3b9cbc1807e14380286e185290916a07f81e2aa4` | same | 0.1 |

The reader loads each calibration through `calibration.load_calibration(path, registered=True, instrument=<declaration>)` (`calibration.py:113`), which applies `_validate_a10_variant` (`:127-149`), and additionally compares the file's byte hash and seal with the table above. `_validate_a10_variant` reads the parent from the running checkout's `v3/runs/registered/v3_rerun_calibration.json` (`:143`); that file is tracked at `4dcc18c2` [M].

**Constants:** `a10_constants.json` seal `3260290d2be9232906862d28af8eca9a2ca61d5613fed55e3acdf60e2024bf6c` (`instrument.py:17`; the file's `sha256` field [M]).

**Seed registry:** `spec.seed_registry_sha256` must be equal across the four arm specs and equal to the `digest` of the committed `v3/runs/registered/A10_stage2_seed_registry.json` payload (`tables_a10.py:689`). The crowding spec records `4ca71f1d…82d8` [M].

**Comparator.** The stage 1 `main` component: final sealed spec, run root (`runs/main_r2`, 24,900 runs, producer `174ab660`, `REQUIREMENTS_DIGEST.md:59-69` [R]), and the nominal family chain (table, validation receipt, A10 receipt, labels, identity record `v3/runs/a10_stage1/nominal/family_identity.json`, tracked at `4dcc18c2` [M]). Only the 6,225 contributing outputs and records are opened. The fields read are the same run-output fields as for an arm. What binds these files by hash is open question 2.

**Reading-input inventories** (sealed): one per arm that ran. The two that exist have different schemas, `stage2-sqrt-reading-input-inventory-1` and `stage2-crowding-reading-input-inventory-1`, and different key names [M]. The reader reads only this common subset and selects the key spelling by `schema`:

| Meaning | INV-S key | INV-C key |
|---|---|---|
| Verdict and findings | `verdict` (must be `complete and consistent`), `findings` (must be empty) | same |
| Identity | `identity.code_identity`, `identity.checkout_commit` | same |
| Runs root | `roots.runs.{path, jobs, records, outputs, outputs_digest, verified_output_hashes_sha256, manifest_file_sha256, identity_file_sha256, all_checks_pass}` and `roots.runs.spec.{path, file_sha256, seal}` | same |
| Published files | `published_files.<name>.{path, sha256, seal}` | `published_files_and_inputs.<name>.{path, sha256, seal}` |

The sigma inventories should follow the crowding schema so the reader's inventory adapter has two cases, not four (open question 9).

### 2.3 How each input is bound by hash

One operator-authorized document, `AUTHORIZED_HASHES_STAGE2.json`, is the root of trust. This follows stage 1's `authorized_hashes` (RS:252). It lists, each as a full 64-hex value:

- the file sha256 and seal of each arm's reading-input inventory;
- the comparator binding record's file sha256 (open question 2);
- this specification's sha256 and REQ's sha256;
- the registration pin;
- for each not-run arm, the sha256 of its evidence records (section 3.6).

From there every input chains down:

1. **Inventory to files.** Each published file's bytes hash to the inventory's `sha256`, and its seal to the inventory's `seal`. The final spec's bytes hash to `roots.runs.spec.file_sha256`. The root's `manifest.json` bytes equal the spec bytes (INV check `2_manifest_bytes_equal_spec_bytes`) [M that the check exists].
2. **Inventory to outputs.** `sha256(verified_output_hashes.json bytes)` equals `roots.runs.verified_output_hashes_sha256`. `v3.artifacts.digest` of that file's mapping equals `roots.runs.outputs_digest` (the inventories define the digest this way, `outputs_digest_meaning`) [M]. Then for every contributing output: the reader's own sha256 of the bytes it parses equals the mapping's entry and the completion record's `output_hash`.
3. **Family chain.** Identity record bytes equal the committed bytes and bind table file hash, table seal, receipt file hash and sidecar file hash. The validation receipt binds table seal and file hash, calibration seal and cell-results hash. The A10 receipt binds table seal and the validation receipt's file hash, and for sqrt the labels file hash. The run spec's `a10_family_paths` equal `STAGE2_PATHS[family]` (`tables_a10.py:322-330`).
4. **Runs to family.** Every job's `config["tables_path"]` and `config["calibration_path"]` equal the spec's `a10_family_paths`. The table's `manifest.calibration_hash` equals the calibration's seal.
5. **Change detection.** Every file read is recorded with sha256 and byte count on first read, and re-hashed after computation and before any output is written; a change is a refusal (rA/`common.py` `Ledger.verify`) [R].

### 2.4 How inputs are collected

Adapted from CC, with stage 2's roots. Two steps, both part of the frozen reader:

```
python -B -m reading_stage2 collect --inputs <inputs-with-collection-object.json> --out <new-collection-folder>
python -B -m reading_stage2 verify  --inputs <collection-folder>/inputs.json
python -B -m reading_stage2 read    --inputs <collection-folder>/inputs.json --component A10|A6|both --out <new-folder>
```

Rules carried over from CC unchanged [R]: scientific files are read in place and never copied (CC:16); the collection folder is new and outside every input root (CC:16); `path_map` is refused in registered mode (CC:18); job configurations are never rewritten to relocate them (CC:18); JSON is loaded strictly, refusing duplicate keys and non-finite numbers (CC:88); a registered `read` requires the sealed collection, with no implicit collection step (CC:7); the sealed collection binds the exact emitted reader input and file inventory (CC:156).

Changes for stage 2:

| CC rule | Stage 2 form | Why |
|---|---|---|
| Five fixed components (CC:24) | Up to four arm components, each `status: "run"` or `"not_run"`, plus `comparator` | REQ section 2 |
| `inventory` with pre-freeze spec hashes (CC:44-59) | The arm's reading-input inventory, bound by the authorized hash, replaces it. Where a pre-dispatch spec is listed (`run_spec_family`), require it to equal the final spec with only `pull_dispatch` removed, by CC:59's reconstruction | The inventories already bind spec, records and outputs [M] |
| Host set from the dispatch database (CC:61-71) | Not re-audited. The reader does not open `dispatch.sqlite` or anything under `host_x2/`. It relies on the inventory's root checks, which it requires to be `all_checks_pass: true` | The brief forbids `*.sqlite*` and `host_x2/unpublished/` to this drafter; the inventories record the session, launch and recheck checks as passed [M]. Whether the reader itself may open the database at item 43 is the interpreter's call; this draft assumes not (open question 12) |
| Model-service record (CC:34, CC:42) | Not re-checked by the reader; an item 42 matter | INV-C `scope_note` assigns the stage-wide operational checks to item 42 [M] |
| `nominal_record_commits` approval receipts (CC:103-128) | The identity record's committed-bytes check for each stage 2 family and for nominal | `table_labels_a5.py:117-133` pattern |
| `r4`, gates, v2 counts | Removed | Not stage 2 inputs |
| Stopped root excluded and recorded (RS:211) | `sqrt/runs_run` excluded and recorded with INV-S's `not_run_reason`; the reader never opens it | INV-S `failed_attempt` [M] |

**The `inputs.json` shape** (schema `a10-stage2-reader-inputs-1`):

```
{
  "schema": "a10-stage2-reader-inputs-1",
  "fixture": false,
  "execution_simulation": "<absolute path>",
  "authorized_hashes": "<path>",
  "registration": {"commit": "...", "path": "...", "sha256": "..."},
  "arms": {
    "<family>": {
      "status": "run",
      "inventory": "<path>",
      "spec": "<path>", "pre_spec": "<path or null>", "root": "<path>",
      "family": {"table": "...", "validation_receipt": "...", "cell_results": "...",
                 "a10_receipt": "...", "labels": "<path, sqrt only>", "identity": "...",
                 "admission_check": "...",
                 "a16": null | {"family_record": "...", "rounds": {"r1": {"round_record": "...",
                        "admission_record": "...", "public": "..."}, "r2": {...}}}},
      "calibration": "<path>",
      "excluded_roots": [{"path": "...", "reason": "...", "inventory_key": "failed_attempt"}]
    },
    "<family>": {"status": "not_run", "reason": "<registered reason string>",
                 "evidence": {"<name>": "<path>", ...}}
  },
  "comparator": {"binding": "<path>", "spec": "<path>", "root": "<path>",
                 "family": {"table": "...", "validation_receipt": "...", "a10_receipt": "...",
                            "labels": "...", "identity": "..."},
                 "calibration": "<path>"}
}
```

All four family names must be present under `arms`. A missing name is a refusal, not an implied not-run. Mode is decided by the specs' `registered` flags; `fixture` must agree with them, and a mixture refuses (RS:127). Fixture mode alone accepts the extra model keys `n_agents`, `carrying_capacity` and `rollout_steps`, a non-frozen calibration, shortened horizons, fewer seeds per cell and `path_map` (RS:128-135, RS:253).

## 3. The integrity gates

All gates run before any estimator. `verify` runs them and stops. `read` runs them again and then computes. A failure writes only a refusal record and prints only a refusal label (section 5.5). No short, missing or unverified cell can reach a helper, so none can read `robust` (REQ section 2).

Gate order is fixed. G0 to G3 open no run output.

**G0. Self and environment.** Reader identity recomputed; `code_identity()` equals `93a453b2…`; `PYTHONINTMAXSTRDIGITS` is 0; the output destination is new and outside every input root; `verify_registration(pin)` passes for the registration pin (`artifacts.py:431`).

**G1. Bindings.** Section 2.3, items 1, 3 and 4, for every arm with `status: "run"` and for the comparator. Every producer field met (`code_hash`, `producer_code_hash`) is in `accepted_identities()`; each artifact is accepted at its own producer and a chain is never required to share one (RS:175-178). Inventory `verdict` is `complete and consistent`, `findings` is empty, `roots.runs.all_checks_pass` is true, and `identity.code_identity` is the running identity.

**G2. Expected cells, completeness and uniqueness (specs only).**

- Arm: `spec.jobs` equals, as a list of dicts, `tables_a10.stage2_runs(STAGE2_PATHS)[family]` (`tables_a10.py:364-380`). This fixes every job id, seed, cell and path string at once. Count equals `STAGE2_RUN_COUNTS[family]`: 4,400, 4,400, 500, 500 (`tables_a10.py:315`). `spec.a10_family == family`, `spec.a10_stage == 2`, `spec.code_hash` is the running identity.
- Comparator: the main spec's jobs equal `tables_a10.paired_runs(*STAGE2_PATHS["nominal"])` (`tables_a10.py:204-209`, `:323`), 24,900 jobs. Whether stage 1's main spec was built with exactly these two path strings is not verified here (open question 2).
- Across all specs read: job ids pairwise distinct and seeds pairwise distinct.
- Per registry entry: the filter of section 1.5 selects exactly the expected number of jobs per cell (100; 400; 75) from the spec, with no cell missing and none extra.

**G3. The contributing-run map.** Computed from the specs alone and sealed to a temporary file before any output is opened, as in stage 1 (RS:186; rA/`reader.py:138-145`). Schema in section 5.2.

**G4. Records and outputs.** For every contributing run: the record exists, `status == "complete"`, `record["job"] == job`, `record["code_hash"]` equals the spec's `code_hash`; the output exists, its bytes hash to `record["output_hash"]` and to the `verified_output_hashes.json` entry; `output["job"] == job` and `output["code_hash"] == record["code_hash"]` (the native rule, `production_runner.py:149-163`). Section 2.3 item 2 holds for the root. For an arm, all of its jobs are contributing, so the whole root is covered. For the comparator, only 6,225 outputs are hashed by the reader; the other 18,675 rest on the binding record.

**G5. Run-path structure (value-free).** Per contributing output: `len(diagnostics) == result["steps"] == config["steps"]`; step times are `0..steps-1`; `population_path` equals the per-step populations; the final-population consistency of section 1.4; `fixture_tables` is false in registered mode; `fire_from_run` does not raise; every field section 4 needs has its native type. A check here accepts every record the native model can produce (RS:299).

**G6. Part 2 admission and the family state.** Per family, including nominal:

- Load `ProductionTables(table_path, calibration_hash=<calibration seal>, registered=True)` and call `require_a10(<instrument>)` (`production_tables.py:55-200`). This re-verifies the manifest hash, the calibration match, the admission binding through `admission_a13.verify` (cap `len(rows) // 1000`, one admitted row per context, no balanced witness, evidence hashes: `admission_a13.py:112-157`), the A16 family provenance (`production_tables.py:134-137`), and the receipt policy.
- `manifest["a13_admission"]` must be present. An absent binding is case 3 of section 4, never case 2.
- `manifest.a10.family == family`.
- Primary rows: 2,875 for sqrt and crowding, 625 for each sigma family, so caps 2, 2, 0, 0 (A16 "Scope and reason"; PLAN:332). A different count is a refusal.
- The admission check record's seal verifies; `outcome == "passed"`; `primary_rows`, `cap` and `residual_count` agree with the loaded table; `admitted_set_sha256` equals the manifest binding's; `plan_hash` equals the validation receipt's. For sqrt this cross-binding is what ties the record to the inventory, since INV-S does not list it [I].
- If the family used A16: scope is `A10_stage2_after_A16_r<q>`; the on-disk family, round and admission records match the provenance bound in `manifest.a13_admission.a16` (`validation_extension_a16.py:1244-1261`); the receipt's `refusals` are preserved and reported. If it did not: scope is `validation_launched_under_A13` (`table_validation_a4.py:837`) and no `a16` key is present.
- The family's incidence state (case 1 or case 2) is fixed here, by section 4.2.

**G7. The labels policy.** `spec.a10_labels_policy == STAGE2_LABELS_POLICY[family]` (`tables_a10.py:335-336`).

- **sqrt:** receipt schema `v3-A10-table-receipt-1`; `labels_sha256` equals the labels file's hash; the strict A5 coverage check inside `require_a10` passes (`production_tables.py:167-200`).
- **crowding and both sigma families:** receipt schema `v3-A10-table-receipt-nolabel-1`; `family` matches; `labels_policy` equals `tables_a10.NO_LABEL_AUTHORITY` exactly; no `labels` and no `labels_sha256` key; `calibration_sha256` matches (`production_tables.py:202-233`). No labels file is accepted for these families.
- The exemption is keyed by the validated family identity. A missing labels file never selects it (A16 labels interpretation; `production_tables.py:160-166`). A strict receipt on a variant family, a no-label receipt on sqrt, or a missing receipt each refuse.

**G8. Incidence integrity.** Section 4.3 and 4.4, including the denominator self-check on every case 1 run.

**G9. Not-run evidence.** Section 3.6.

### 3.6 A refused or absent arm

An arm is `not_run` only when the operator's input says so and the evidence supports it. The reader never infers it from a missing root.

- **Evidence accepted:** (a) the family's A16 family record `<stem>.a16_family.json` (`validation_extension_a16.py:433-434`) with a terminal latch, plus the refused admission record or records; or (b) a sealed refused admission check with no later publication, plus the operator's closeout record. Each evidence file's sha256 is in the authorized-hash document. The exact set is open question 4b.
- **Contradiction check:** for a `not_run` arm no published table may exist at `STAGE2_PATHS[family][1]`, and no run root with records may be supplied. If either exists, refuse.
- **What is written:** each of the arm's comparisons appears in the output with `status: "not run"`, the registered reason string, `estimate`, `interval` and `undefined_share` null, and `verdict: "undetermined"` with reason `arm not run: <reason>`. Basis: A6 reports the arm "as not run, with the reason" (DN:1376), and A16 item 10 says its comparisons "follow the existing unavailable/undetermined rules" (A16:132) [R]. Combining them into one record is my reading [I]; open question 4a.
- **What does not change:** family sizes 18 and 33, levels, tails, seeds, the other arms' comparisons, and no other family is substituted (REQ section 2).
- A component whose every arm is not run is still sealed, with all its entries `not run`.

## 4. Incidence

### 4.1 What is reported

For every quantity in `values.json` that an estimator produces (section 5.3), from its predefined contributing runs: pooled numerators and denominators per branch, per-run rates, per-family status coverage, and a flag (DN:2215-2219; REQ section 3). Branches are `ordinary_allocation`, `survival_first`, `yield_review` (`admission_a13.py:7`).

### 4.2 The three cases, per input family

The family is one of `nominal`, `sqrt`, `crowding`, `sigma_squared_x10`, `sigma_squared_x0.1`. After G6 has loaded and verified it, let `admitted = set(manifest["a13_admission"]["rows"])`.

**Case 1, nonempty verified admitted set** (`len(admitted) > 0`). The native recorder is enabled exactly when the manifest's admitted rows are nonempty (`admission_a13.py:180-181`; `integration.py:111-114`), so every run scored by this family records `a13_decision_incidence` (`production_runner.py:289-291`) [R].

**Case 2, verified zero admitted rows** (`len(admitted) == 0`). The status is the literal string `no admitted rows`. It is assigned only if all of the following hold. None of them is the absence of the field, and none is the family's name.

1. G1, G6 and G7 passed for the family: identity record, table, receipts and admission record are bound and consistent.
2. `manifest["a13_admission"]["rows"] == {}`, `admitted_set_sha256 == digest({})`, and `primary_rows` equals the number of rows loaded.
3. No loaded row has `status == "not_estimable"` (a count over the loaded rows; `require_production` already rejects any such row outside the admitted set, `production_tables.py:138-143`).
4. The admission check record reads `outcome: "passed"` and `residual_count: 0`.
5. **Context coverage.** `set(rows) == tables_a10.expected_keys(tables_a10.build_jobs(family, calibration_path), calibration)` (`tables_a10.py:152-165`, `:56-90`), and every contributing arm job's (rr, alpha, capability) for each capability in `study.capabilities(successor_capability)` is in `tables_a10.contexts(family)` (`tables_a10.py:23-31`; `study.py:13-21`). The lookup reports `missing_or_not_estimable_row` when the row is absent as well as when it is not estimable (`production_tables.py:265-266`), so the structural zero needs both no residual row and no absent row on any context a contributing run can reach [I].
6. For a sigma family, `primary_rows == 625` and `cap == 0` (A16 "Scope and reason").

**Case 3, anything else.** Unknown family, a failed binding, an absent `a13_admission`, a corrupt record, or any check of case 2 failing while the admitted set is empty. The reader stops at the integrity gate. Case 3 is never coerced to case 2.

For the nominal family, case 1 is expected: the digest records a passed A14 admission with five residual rows (`REQUIREMENTS_DIGEST.md:92`) [R]. For sqrt and crowding the case is not known to me and is determined at run time from the validated manifest, as REQ section 3 directs. Both builds must implement both cases for every arm family.

### 4.3 Per contributing run

**In a case 1 family:**

- `result["a13_decision_incidence"]` must be present. Its absence is an integrity failure (refusal label `a13 incidence missing on admitted family`). It is not `no admitted rows` and not "unassessed".
- It has exactly the three branches. Per branch: `numerator` and `denominator` are non-negative integers of type int, `numerator <= denominator`, `rate == numerator / denominator` when the denominator is positive and null otherwise, `assessed is (denominator > 0)` (`admission_a13.py:217-219`).
- The three separate counts are dicts of non-negative integers by reason and are preserved: `excluded_by_reason`, `balanced_fallbacks_by_reason`, `survival_first_unavailable_selections_by_reason` (`admission_a13.py:219-221`).
- **Denominator self-check:** the derived denominators of section 4.4 must equal the recorded ones on all three branches. A mismatch is a refusal. This runs on every real case 1 run, which is at least the 6,225 comparator runs, and it is value-free: it compares counts of evaluated decisions.

**In a case 2 family:**

- `a13_decision_incidence` must be **absent**. A present field contradicts the verified state and refuses.
- No step's `unavailable_rules` may hold the value `missing_or_not_estimable_row` (`integration.py:428`; `admission_a13.py:6`). One occurrence contradicts the claimed fully available family and refuses (REQ section 3, case 3). This check covers allocation steps only. Yield events record a count of unavailable plans without reasons (`integration.py:337`), so the yield side has no equivalent check [I]; the context-coverage condition carries it.
- The normalized record is, per branch with derived denominator `D`:

```
{"numerator": 0, "denominator": D, "rate": 0.0 if D else None, "assessed": bool(D),
 "provenance": {"numerator": "structural_zero_from_verified_family",
                "denominator": "derived_from_recorded_decisions"}}
```

This is the shape the committed test pins (`simulation/test_v3_stage2_phase2.py:1745-1746`) [R]. If any precondition of section 4.4 fails for a case 2 run, the denominators are "not recorded", the complete pooled-incidence requirement fails, and the reader refuses. It never writes a zero denominator it did not count.

The zero numerator is a structural inference about the single cause `missing_or_not_estimable_row`. It says nothing about unpublished continuation bins or other fallbacks, and it is never derived from the aggregate counters in `continuation_availability` (DN:2214; REQ section 3).

### 4.4 The derived denominators, exactly

Let `result = output["result"]`, `steps = result["diagnostics"]`, `events = result["yield_events"]`.

| Branch | Derived denominator |
|---|---|
| `ordinary_allocation` | the number of `s` in `steps` with `s["allocation_evaluated"] is True` and `s["survival_first"] is False` |
| `survival_first` | the number of `s` in `steps` with `s["allocation_evaluated"] is True` and `s["survival_first"] is True` |
| `yield_review` | `len(events)` |

Why these are exact [I, each step read from `integration.py`]:

- `step` runs `_choose` once on every non-absorbed step (`:406-407`). `_choose` has three exits (`:260`, `:267`, `:273`) and calls `_record_a13_allocation` exactly once before each (`:259`, `:266`, `:272`), with the same `survival_first` value it returns. `step` writes that returned value into the record (`:442`) with `allocation_evaluated: True` (`:427`). The A13 branch is `survival_first` or `ordinary_allocation` by that same flag (`admission_a13.py:193`).
- An absorbed step returns before `_choose` (`:387-405`) with `allocation_evaluated: False` (`:394`), and it never reaches `review_yield`. Its `survival_first: True` (`:390`) is therefore excluded by the first condition. Absorbing padding contributes nothing.
- `review_yield` returns before evaluation when there is no successor, when the step is not a multiple of 10, or at an absolute deadline (`:282-287`). Past those returns it appends one A13 yield decision (`:344-346`) and exactly one event, at `:365` (gate not authorized) or `:377` (every other path). So evaluated reviews, A13 yield decisions and recorded events are one-to-one. Held and fired reviews both pass through this path. "Steps divided by ten" is not used.
- The runner preserves both lists whole (`production_runner.py:304-305`); `pack_evidence` removes only the `gate_evidence` member of each item (`recording.py:183-184`).

Preconditions, checked per run before the counts are trusted: G5 passed; every `allocation_evaluated` and `survival_first` is a bool; event times are distinct, each is a multiple of 10 and each is the time of a step with `allocation_evaluated` true; and `ordinary + survival_first == result["continuation_availability"]["allocation_steps"]` (`production_runner.py:279`).

**Fixture check of the derivation:** fixture F6 (section 6) compares the derived denominators with recorded incidence on nonempty-admission runs produced by the native code at the running identity, covering extinction with absorbing padding, held reviews and fired reviews. The production self-check in section 4.3 repeats the comparison on every real case 1 run.

### 4.5 Pooling

For each quantity, over its contributing runs in sorted order of `"<component>/<job_id>"`:

- Pool with `admission_a13.pooled_incidence(list_of_branch_records)` (`admission_a13.py:225-233`), which adds numerators and denominators and returns per-run rates. It reads only `numerator`, `denominator` and `rate`, so it accepts recorded and normalized records together [R]. The committed test exercises exactly this mixed call (`test_v3_stage2_phase2.py:1748-1751`).
- A pooled denominator of zero is `unassessed`, rate null. A positive denominator with numerator zero has rate 0.0.
- Both sides of a comparison are always pooled. A no-admitted side contributes its derived denominators and is never dropped (REQ section 3).
- **The flag:** true if any branch's pooled numerator is nonzero (`admission_a13.py:233`). A flagged quantity keeps its estimate and reading; nothing is dropped, reweighted or re-estimated. An unflagged quantity is never described as certified unaffected; the output carries the sentence "An unflagged quantity is not certified unaffected." (as rA/`incidence.py:162`).
- **Coverage:** per quantity and per family, the number of runs with status `recorded` and with status `no admitted rows`, the family's table file sha256 and A10 receipt sha256, and for case 2 the reason text "A13 accumulator absent: `admission_a13.enabled` is false for an empty admitted-row set".
- **Separate counts** (DN:2210-2213): pooled over case 1 runs only, by reason, with the count of runs they cover. For case 2 runs they read `not recorded`. This draft does not derive them; open question 7.

## 5. Outputs and sealing

### 5.1 Files of one component

Each component (`A10`, `A6`) writes one folder. All files are `canonical(value) + b"\n"` with `v3.artifacts.canonical` (`artifacts.py:98-99`), infinities as the strings `"+inf"` and `"-inf"` (RS:41), written once and never replaced (rA/`common.py` `write`).

| File | Content | Sealed envelope |
|---|---|---|
| `reading.json` | The component's reading: registry, comparison results, arm statuses, labels disclosures, admission and A16 provenance, incidence summary, provenance (5.4) | yes, `{payload, sha256}` |
| `values.json` | Flat `{"schema": "a10-stage2-values-1", "component": ..., "values": {key: value}}` for the blind comparison | no, hashed in `SEAL.json` |
| `contributing_runs.json` | The specs-only map (5.2) | yes |
| `incidence_per_run.json` | Per-run normalized incidence records and statuses | yes |
| `SEAL.json` | `{"schema": "a10-stage2-seal-1", "component", "files": {name: file sha256}, "reader_identity", "collection_sha256", "spec_sha256", "requirements_sha256"}` | yes |

On refusal the folder holds only `refusal.json` (5.5).

### 5.2 `contributing_runs.json`

Payload: `schema: "a10-stage2-contributing-runs-1"`, `basis: "specs only; sealed before opening outputs"`, `specs: {component: digest(spec payload)}`, `runs: {"<component>/<job_id>": {component, phase, category, grid, rr, alpha, capability}}`, `quantities: {key: sorted list of "<component>/<job_id>"}`. A whole run contributes even when its statistic turns out undefined (rA/`incidence.py:28-30`).

Membership:

| Quantity key | Contributing runs |
|---|---|
| `<F>.boundary.<arm>`, `<F>.boundary_point.<arm>` | the arm's boundary cells and the comparator's boundary cells |
| `<F>.capstar.<arm>.<a>`, `<F>.capstar_point.<arm>.<a>` | the arm's seven cells at a and the comparator's seven cells at a |
| `<F>.survival.<arm>.<rr>` | the arm's cell at rr |
| `<F>.survival_difference.<arm>.<rr>` | the arm's cell and the comparator's cell at rr |

A not-run arm's quantities have an empty arm side and are listed with `status: "not run"`; no incidence is pooled for them.

### 5.3 `values.json` keys

`<F>` is `A10arm` or `A6`. `<rr>` and `<a>` are `repr` of the float. Keys are sorted. This is the complete key set; a build that adds a key documents it and the comparison treats an undocumented key as a difference.

| Key | Value |
|---|---|
| `<F>.boundary.<arm>` | `{estimate, interval, verdict, undefined_share, undefined_tail, level_alpha, reason, status}` from the helper's `difference`, `interval`, `verdict`, `undefined_resample_fraction`, `undefined_resample_tail`, `bonferroni_alpha`, `reason`; `status` is `"run"` or `"not run"` |
| `<F>.capstar.<arm>.<a>` | the same fields; `undefined_share` 0.0 and `undefined_tail` null |
| `<F>.boundary_point.<arm>` | `{arm, nominal}`: the two point boundaries, a float or an infinity string |
| `<F>.capstar_point.<arm>.<a>` | `{arm: {category_index, censored}, nominal: {category_index, censored}}` from the helper's `step` and `censored` |
| `<F>.survival.<arm>.<rr>` | `{n, count, rate, wilson}` on the arm's cell; Wilson at z = 2 by the expression at rB/`against_v2.py:22-28`: `p = count/n; d = 1 + 4/n; center = (p + 2/n)/d; half = 2*sqrt(p*(1-p)/n + 1/n**2)/d; [max(0., center-half), min(1., center+half)]` |
| `<F>.survival_difference.<arm>.<rr>` | `{difference, interval}` from `survival_differences` |
| `incidence.<quantity>` | `{flag, branches: {branch: {numerator, denominator, rate}}, per_run_sha256}` |
| `incidence_status.<quantity>` | `{branches: {branch: "assessed" or "unassessed"}, families: {family: {status, runs, table_sha256, receipt_sha256}}}` |
| `incidence_counts.<quantity>` | `{recorded_runs, not_recorded_runs, branches: {branch: {the three separate counts}}}` |
| `family.<name>.status` | `"run"` or `"not run"`, with `reason` when not run |
| `family.<name>.labels` | sqrt: `{policy: "a5_labels_required", labels_sha256}`; variants: `{policy: "no_a5_labels_a16", disclosure: "no A5 labels; FV asymptotic and uncertified"}` (PLAN:338; `tables_a10.py:335-344`) |
| `family.<name>.admission` | `{scope, primary_rows, cap, residual_count, admitted_rows, rounds_used, admission_record_sha256}` |
| `family_error.<name>.*` | only when `rounds_used > 0`: `P`, `M`, `alpha`, `E`, `E2`, `extension_error_bound`, `tests_round1`, `tests_round2` from the hash-bound round admission record, and the statement "at least 1 - alpha(1 + P/M), given the fitted family" (A16 item 9) |
| `label.comparator` | `"produced under A13 and A14, amendments informed by outcomes"` (RS:198), since every comparison uses nominal-family runs |
| `family_size.<F>` | 18 or 33 |

`per_run_sha256` is the sha256 of `canonical(m)`, where `m` maps `"<component>/<job_id>"` to the run's record: the recorded `a13_decision_incidence` exactly as in the output for a case 1 run, and the normalized record of section 4.3 for a case 2 run. This departs from RS:261, which hashed recorded values only, because a case 2 run has none.

The reason string for a share above the tail is the helper's: `"undefined-resample share %.4f exceeds the Bonferroni tail %.5f"` (`reading_a6.py:367-368`). It shows the tail to five decimals, `0.00139` or `0.00076`; the exact float is in `undefined_tail` [R].

### 5.4 Provenance in `reading.json`

- Reader identity: sha256 over the package's `*.py` files with their names (rA/`common.py` `identity`), and the role (`A` or `B`).
- Running identity, the source manifest's digest, Python and NumPy versions.
- This specification's sha256, REQ's sha256, the registration pin, the authorized-hash document's sha256, the collection's sha256.
- Per comparison: the identity, family size, level, `bonferroni_alpha`, the actual `undefined_resample_tail`, seed, resamples, quantile method, grid, both filters, expected and found seed counts per cell, the helper's full result dict (rr keys as `repr`), and the reason.
- Per input: path label, sha256, byte count and every producer field found.
- Per family: all of G6 and G7's bound hashes; each used A16 round's plan, public record and admission record hashes, with the original and intermediate refusals; the unchanged Part 2 error statement. An admission-probability budget estimate is never copied in as a reading (REQ section 4).
- Excluded roots with reasons.
- A statement that stage 1's 12 and 25 comparisons and its seed-convergence seal are not recomputed.

**Nothing run-dependent is sealed.** No timestamp, hostname, absolute path, process id, worker count or duration appears in any of the five files. Paths are recorded as labels relative to `execution_simulation` or to a named root. Run-dependent facts go to a separate unsealed `run_log.json` holding only times, counts, hashes and resource peaks.

### 5.5 What may reach a terminal or log

- On success: the component name, each output file's sha256, the reader identity, and counts of jobs verified. Nothing else.
- On refusal: `REFUSED: <phase>: <reason_class>`, where `phase` is `input_verification` or `after_computation_started` (RS:277) and `reason_class` is a literal label from the reader's own source or a literal message of a native validator. No interpolated value, count from an output, file excerpt or exception text is printed (rA/`refusal.py`). `refusal.json` holds the same three fields.
- The native helpers raise messages with interpolated counts (for example `reading_a6.py:265`). The reader maps them to literal labels and never prints them.
- No progress line names a cell together with a rate, count of survivors, verdict or interval.

### 5.6 Byte identity of two runs of one build

Each reader computes each component twice into two new folders. A comparison tool reads only file bytes and prints `identical` or the names of the files whose sha256 differ. All five files must match. Tested on fixtures for: repeat runs; `--component both` against two separate invocations; and one worker process against several, if workers are allowed (open question 8).

### 5.7 Blind comparison of two independent builds

- **Tool:** as rB/`compare.py`: load two `values.json`, require the same schema and component, and print `identical`, or the count and the names of differing keys. It never prints a value. Key names carry no outcome.
- **Also compared, by sha256 only:** `contributing_runs.json` payload `quantities`, and `incidence_per_run.json`.
- **Pass:** zero differing keys in both components, on every fixture and then on the real inputs.
- **On the real inputs:** a difference stops the process. Nothing is opened. The differing key names go to the interpreter and operator. Whether a fix is allowed after values have been computed is the operator's decision; stage 1's rule allowed a fix only when the refusal came before any outcome value was computed (RS:224-227).

### 5.8 Sealing and opening

Computing and sealing end at item 43. For each component the two builds' `SEAL.json` hashes and the comparison result are recorded and committed before anything is opened, following the stage 1 convention (`REQUIREMENTS_DIGEST.md:148-155`). Opening is item 44, a separate go (APP item 44). The reader has no command that displays a value.

## 6. Fixtures

Every fixture value is synthetic. No real output, table or reading seeds a fixture. Two levels:

- **L1, arithmetic.** Arrays specified in this section, passed through the reader's comparison layer. Each builder constructs them from this text.
- **L2, end to end.** Files with the native schemas, generated by the native code paths at the running identity at toy scale (non-registered specs, small `n_agents`, short horizons, a few seeds), as stage 1's fixtures were (RS:66-75). One generator builds them; the second builder receives the files only. Who generates is open question 6.

Expected outcomes below are stated before any build. Where the outcome is an inference of mine from the helper's rules, it is marked [I]; a build that disagrees has found either a defect or an error in this draft, and either goes to the interpreter.

| ID | Requirement covered | Level | Generation | Must show, expected outcome |
|---|---|---|---|---|
| F1 | Both thresholds | L1 | R1 grid. Arm 100 and comparator 400 per rr; final population 5 at the first five rr and 50 at the last four; arm and comparator identical in pattern | Through the A10 wrapper: `undefined_tail == 0.05/36`, `level_alpha == 0.05/18`, seed 20261011. Through the A6 wrapper: `0.05/66`, `0.05/33`, 20260929. In both: `undefined_share == 0.0`, `estimate == 0.0`, `interval == [0.0, 0.0]`, verdict `robust` [I: every resample of a degenerate cell is identical] |
| F2 | Equality | L1 | The F3 arrays. First call with tail 0.05/66 to obtain the share `s`; then tail `s`; then tail `s/2`, all at seed 20261011, alpha 0.05/18 | Tail `s`: verdict not `undetermined`. Tail `s/2`: `undetermined`, reason contains `'%.5f' % (s/2)`. Equality is allowed, strict excess is not (`test_v3_stage2_phase2.py:1718-1722` asserts this) [R]. Tested at the helper level with an injected tail because equality cannot occur at the registered tails: 0.05/36 x 50,000 = 69.4 and 0.05/66 x 50,000 = 37.9 are not integers [I] |
| F3 | The audit's between-threshold case | L1 | R1 grid. Arm, 100 per rr: all 5 except at 0.066, where the array is fifty-eight 50s then forty-two 5s. Comparator, 400 per rr: all 5 except at 0.066, two hundred nineteen 50s then one hundred eighty-one 5s. Seed 20261011, alpha 0.05/18 | Share `s` with `0.05/66 < s <= 0.05/36`. Tail 0.05/66: `undetermined`, reason contains `0.00076`. Tail 0.05/36: not `undetermined`, `undefined_tail == 0.05/36`, same `s` (`test_v3_stage2_phase2.py:1706-1717`) [R, not run by me]. Verdict at 0.05/36: `inconclusive`, interval `["-inf", "+inf"]` [I: each side fails to cross in a few percent of resamples, far above the 0.14 percent percentile] |
| F4 | All cap* censoring directions | L1 | Seven capability cells per side, 100 and 75 runs, fire indicators all 0 or all 1 unless stated. (a) arm fires everywhere, comparator nowhere. (b) the reverse. (c) both fire nowhere. (d) both fire everywhere. (e) arm fires at 1.2, 1.5, 2.0 only; comparator at 1.2 to 2.5 only. (f) as (d) but the arm's 5.0 cell has fifty 1s and fifty 0s | (a) arm top-censored, comparator bottom-censored, difference 7, interval [7, 7], `moves_materially_higher`. (b) -7, [-7, -7], `moves_materially_lower`. (c) both `censored: "bottom"`, [0, 0], `robust`. (d) both `censored: "top"`, [0, 0], `robust`. (e) -1, [-1, -1], `moves_materially_lower`: the endpoint at -1 counts. (f) point difference 0, interval [-1, 0], `inconclusive` [I: about half the resamples put the arm's top cell below 0.5] |
| F5 | Sigma no-crossing | L1 | Sigma grid, `sigma_variant=True`, 100 and 400 per rr. (a) arm 50 everywhere; comparator crosses between 0.060 and 0.062. (b) arm 5 everywhere. (c) arm crosses; comparator 5 everywhere. (d) the same three on the R1 grid with `sigma_variant=False` | (a) `undetermined`, reason `sigma0^2 boundary below 0.059`, no interval. (b) `undetermined`, `arm has no 50 percent crossing in range (boundary above range)`. (c) `undetermined`, `comparator has no 50 percent crossing in range`. (d) case (a) reads `arm survives across the grid (boundary below range)`. (`reading_a6.py:391-396`) [R] |
| F6 | Derivation against recorded incidence | L2 | Runs scored by a toy family with at least one admitted `not_estimable` row, so the recorder is on. The set must include: a run that goes extinct before the last step; a run with at least one held review; a run with at least one fired review; a run with at least one survival-first step | For every run and every branch, derived denominator equals recorded denominator exactly. The fixture's manifest lists which run covers which condition, and the reader's test asserts each condition is present |
| F7 | No-admitted family, positive denominators | L2 | An arm-shaped toy family with zero admitted rows and full context coverage. Each run has a **twin**: same job and seed, scored by a table that differs only by one admitted `not_estimable` row in a context that run never looks up. The twin's output must equal the run's output in every field except `a13_decision_incidence` | Status `no admitted rows`; numerators 0 with provenance `structural_zero_from_verified_family`; each denominator equals the twin's recorded denominator, provenance `derived_from_recorded_decisions`; rate 0.0. The twin is the oracle and is not a reader input |
| F8 | No-admitted family, zero denominators | L2 | As F7, with one run started at `n_agents = 0`, so every step is absorbed (`integration.py:100-101`, `:387-405`) | That run: all three denominators 0, `assessed` false, rate null, reported `unassessed`. A quantity whose every contributing run is such a run pools to `unassessed`, never to rate 0 |
| F9 | Mixed-family pool | L2 | A comparison with the F7 arm (case 2) against a toy comparator family in case 1. Two variants: comparator with a nonzero pooled numerator on some branch; comparator with all numerators zero | Pooled denominator is the sum over both sides; pooled numerator is the comparator's. Variant 1: `flag` true, estimate and verdict unchanged from the same comparison computed without incidence. Variant 2: `flag` false, and the output carries the "not certified unaffected" sentence. Both: `families` shows one `recorded` and one `no admitted rows` |
| F10 | Missing incidence on an admitted family | L2 | F9 with `a13_decision_incidence` removed from one comparator output, and the record and hash file rewritten so every hash gate still passes | Refusal at `input_verification`, label `a13 incidence missing on admitted family`. No value file written |
| F11 | Wrong receipt or labels policy | L2 | Seven variants of a valid fixture: (a) a variant family with a strict-schema receipt and a labels file; (b) sqrt with a no-label receipt; (c) a variant family with no receipt; (d) a receipt whose `table_sha256` names another table; (e) a spec whose `a10_labels_policy` differs; (f) a no-label receipt whose `labels_policy` differs from `NO_LABEL_AUTHORITY`; (g) a variant FV row without the asymptotic label | Each refuses at `input_verification`. (c) shows that missing labels do not select the exemption |
| F12 | Missing cells | L2 and structure | (a) one output missing; (b) one record missing; (c) one output's bytes altered; (d) a spec with 99 jobs in one cell; (e) a duplicate job id; (f) an extra job; (g) a registered-flag spec whose jobs differ from `stage2_runs` | Each refuses before any estimator runs. No comparison of the affected arm is emitted, so none reads `robust` |
| F13 | Final refusal | L2 | (a) the A6 component with one sigma family `not_run`, evidence a toy A16 family record with a terminal latch and a refused admission record; (b) the same with a published table present at the target; (c) `not_run` with no evidence; (d) every arm of a component `not_run` | (a) eight entries; the sigma boundary has `status: "not run"`, `verdict: "undetermined"`, reason `arm not run: <reason>`; the other seven computed; `family_size.A6 == 33`; level and tail unchanged. (b) and (c) refuse. (d) seals with every entry `not run` |
| F14 | Unknown binding | L2 | (a) a family table without `manifest.a13_admission`; (b) an identity record that does not match the table; (c) a zero-admitted family whose rows do not cover a contributing run's context | Each refuses. None is treated as `no admitted rows` |
| F15 | Contradiction | L2 | A zero-admitted toy family lacking one looked-up row, so a run's `unavailable_rules` holds `missing_or_not_estimable_row`; and a zero-admitted family with a run that carries `a13_decision_incidence` | Both refuse |
| F16 | Determinism | L2 | Any valid fixture | Section 5.6: byte-identical repeats; `both` equals separate; worker count does not change bytes |

Registered-mode structure that toy fixtures cannot reach (exact seed counts, equality with `stage2_runs`, refusal of fixture-only inputs) is tested on synthetic specs with no outputs, as stage 1 did (RS:135; rB `tests/test_registered_structure.py` by name).

## 7. Reuse

Judged from the code I read in full (reader A: `common.py`, `refusal.py`, `preflight.py`, `statistics.py`, `incidence.py`, `reader.py`, `__main__.py`; reader B: `arms.py`, `incidence.py`, `compare.py`, `constants.py`, `values.py`) and, for the rest, from function inventories, greps and CC. Judgments on reader A's `collect.py` and `provenance.py` and on reader B's `verify.py`, `inputs.py`, `nominal.py`, `extract.py` and `reading.py` rest on that weaker reading and are marked [I].

| Part | Reader A | Reader B | Stage 2 status |
|---|---|---|---|
| Strict JSON, seal, write-once, input ledger | `common.py` | `common.py` [I] | Carries over unchanged |
| Value-free refusal labels and phases | `refusal.py` | `common.Refused`, phase strings (`compare.py:33`) | Carries over; the label set is regenerated |
| Blind comparison tool | none in package | `compare.py` | B's carries over with a schema change; A writes its own |
| Root verification: record, output, job, hash | `provenance.inspect_component` [I] | `verify.verify_root` [I] | Adapt: stage 2 inventories replace the stage 1 inventory; no database audit |
| Collection | `collect.py` (database snapshot, machine register, host services) | none; B checks what is supplied (RS:290) | Adapt A's file-inventory and sealing parts; drop the database and host audits (section 2.4) |
| Family chain verification | `provenance.nominal`, `verify_publication`, `amendments.py` [I] | `nominal.verify`, `amendments.verify` [I] | Adapt: A13 and A14 round checks become the A16 round checks; add identity-record, no-label receipt and sigma calibration pins |
| Comparison driver | `statistics.sensitivity` | `arms.family`, which already takes seed, alpha, tail and sorts by (kind, arm, alpha) (`arms.py:105-139`) | Adapt. Both must call the native `compare_boundary` with the explicit tail and grid; both mirrors are retired (section 1.6) |
| Cell selection | own loops (`statistics.py:90-99`; `arms.py:78-91`) | | Replace with `arm_and_comparator_cells` and the filters of section 1.5 |
| Contributing-run map | `incidence.contributing_runs` | `incidence.contributing_runs` | Adapt: the pattern carries, the quantity list is new |
| Incidence validation | `incidence.validate_record` | `incidence.validate`, which also checks reason consistency (`incidence.py:130-135`) | Carries over for case 1 |
| Incidence pooling | `incidence.summarize`: a missing record becomes `None` and "unassessed" (`:133-134`, `:146`) | `incidence.summarize`: a missing record becomes numerator 0, denominator 0 (`:143-147`) | **Replace in both.** This is the coercion REQ section 3 forbids |
| Three-case state, derived denominators, self-check | none | none | New |
| Not-run arms, fixed denominators | none | none | New |
| Two separately sealed components | none (one reading) | none | New |
| Main statistics, R4 pairing, A9, gates, citations, predictions, convergence, diagnostics, ranking joins | present | present | Dropped. None is a stage 2 quantity |

**Fresh build or extension.** A fresh package in each builder's tree is the sounder path, reusing the builder's own infrastructure modules by copy.

1. **The stage 1 reader's identity is evidence.** It is a hash of the package's files (rA/`common.py` `identity`; rB/`reading.py:24`) and is recorded in the sealed stage 1 reading (rA/`reader.py:235`). Editing `reading_a10` in place destroys the tree that reproduces that seal. A copy leaves it intact.
2. **Most of the stage 1 code computes things stage 2 must not compute.** By file size, the comparison and incidence modules are a minority of each package [M: reader A's `statistics.py` and `incidence.py` are about 18 KB of a 370 KB package, tests and README included; reader B's `arms.py` and `incidence.py` are about 19 KB of 254 KB, tests excluded]. A sealed reader that carries live code for stage 1 verdicts, gates and R4 pairing has paths that could compute an unregistered or already-sealed quantity. Removing them from an extension is more work, and more review, than not copying them.
3. **The parts that are wrong for stage 2 sit in the middle of the reused flow.** The incidence coercion and the boundary mirrors are called from each reader's main path. An extension would patch them under the stage 1 control flow; a fresh driver calls the new logic directly.
4. **The pins differ.** Running identity, components, input contract and output schema all change. Little of the top-level orchestration survives either way.

What this costs: the infrastructure copies must be shown equal to their stage 1 sources, or their differences listed. The freeze record carries that table (section 8.4).

## 8. The build plan

### 8.1 Two independent builders

- **Builder A** works in `v3_reader_codex`, **builder B** in `v3_reader_claude`. Each sees this specification, REQ, the repository at `4dcc18c2`, and its own stage 1 reader. Neither sees the other's tree, reports or outputs, as in stage 1 (`DIRECTIVE_A…:47`, `DIRECTIVE_B…:42`).
- Each writes `simulation/reading_stage2/` in its own worktree and edits nothing under `simulation/v3/` (`DIRECTIVE_A…:48`).
- Each moves its worktree to a commit whose `simulation/v3` is byte-identical to `4dcc18c2` and confirms `code_identity()` and `accepted_identities()` there. The interpreter does the checkout where a builder's sandbox cannot (`DIRECTIVE_B…:11`).
- A rule question is listed in the builder's report and implemented by the most literal reading with a comment (RS:17). It is not settled between builders.
- Fixtures only. No builder opens, lists or hashes a registered output or a stage 1 reading.
- L2 fixtures: one generator, files only to the other builder (open question 6).

### 8.2 Steps and time

All times are **budget estimates**. They rest on stage 1's elapsed times read from file timestamps in `codex_blind/a10_reading/` [M]: the first build and comparison ran from 2026-10-10 20:12 to 2026-10-11 09:46, about 14 hours elapsed with four follow-ups; the adaptation ran from 2026-10-25 21:10 to 2026-10-27 13:24, about 40 hours elapsed over nine rounds per builder. Those spans include idle and human time, so they bound elapsed time, not effort. The split below is my judgment [G].

| Step | Budget estimate, elapsed | Rests on |
|---|---:|---|
| 1. Interpreter review of this draft, second check, repair round, final check | 1 working day | Four passes over one document; no stage 1 analogue measured [G] |
| 2. Settle open questions 2, 4, 5, 6 | 0.5 working day plus the operator's turnaround | Each needs a decision or one X2-1 fact [G] |
| 3. L2 fixture generation | 6 hours, of which under 1 hour of local compute | Stage 1's mixed fixture: 1,000 native jobs, 26.6 worker-minutes (`ADAPT_REPORT_A.md:80`) [R]; stage 2's set is of that order [G] |
| 4. Two builds, in parallel | 10 hours each | Smaller statistics than stage 1's first build (about 14 hours elapsed for both), more integrity logic [G] |
| 5. Blind comparison on fixtures, with follow-up rounds | 3 rounds at 2 hours | Stage 1 needed four rounds on the first build and nine in adaptation [M]; a pinned key set and input contract should cut that [G] |
| 6. Throughput and memory probe on a full-size synthetic output | 1 hour | Section 9.2 needs a measured parse rate; none exists [I] |
| 7. Freeze record and commit request | 2 hours | Hashing and a table [G] |
| **Total** | **about 4 working days** | Sum of the above with normal turnaround [G] |

Builds and fixture runs are on the workstation. Whether workstation time charges the reading's 12 hour ceiling is not stated in the sources I read; A15 prices ceilings in X2-equivalent hours on X2-1 (`AMENDMENT_A15_adopted.md:60`), so I assume not [I].

### 8.3 Blind comparison criteria

On every fixture, for each component:

1. Each build's two runs are byte-identical (5.6).
2. `values.json`: zero differing keys between builds (5.7).
3. `contributing_runs.json` `quantities` equal; `incidence_per_run.json` equal by hash.
4. Each refusal fixture refuses in both builds at the same phase. Reason labels may differ in wording between builds; the phase and the fact of refusal may not.
5. Every expected outcome of section 6 holds in both builds. A shared disagreement with this draft goes to the interpreter before freeze.

A difference is a defect or a gap in this specification. A gap is fixed here, by addendum, before freeze, never by one builder copying the other.

### 8.4 The freeze record

One sealed document, written before any stage 2 output is read, containing:

- this specification's sha256 with all addenda, and REQ's sha256;
- for each reader: its identity, every source file with sha256, the checkout commit, `code_identity()`, the Python and NumPy versions, and the table mapping each copied module to its stage 1 source with either "identical" or a listed diff;
- the registry as data, with its digest;
- the normalization schema of section 4.3;
- each fixture's file list hash and its expected outcomes, as in section 6 with any addenda;
- the fixture comparison results: the hashes of both builds' fixture outputs and the word `identical` per fixture;
- the comparison tool's sha256;
- the measured parse rate and memory peak from step 6, labelled as measurements on synthetic data.

REQ section 4 requires source, registry, normalization schema and fixture expectations frozen before stage 2 results [R].

### 8.5 The commit request

- **Adds only:** the two reader packages under distinct directory names (for example `simulation/reading_stage2_a/` and `simulation/reading_stage2_b/`), this specification and its addenda, the freeze record, and the fixture expectations. The fixture files themselves may stay outside the repository if their list hash is in the freeze record.
- **Touches nothing that enters the code identity:** no file matching `simulation/v3/*.py` or top-level `simulation/*.py`, and none of the four JSON records in `source_manifest()` (`artifacts.py:234-250`). The request states `code_identity()` before and after, both `93a453b2…`.
- **Does not touch the design note.** Its hash is the registration pin; a changed note breaks `verify_registration` for current launches [I from `artifacts.py:431` and the pin].
- **Does not touch** any run root, family file, identity record or compatibility record.
- **States:** the full diff's file list; each reader's identity; the freeze record's sha256; that no stage 2 output and no stage 1 reading output was read; and who had read stage 1's results (the operator and interpreter have, PLAN:11; the builders' status is theirs to state).
- **Asks for:** the interpreter's review and the operator's go, as a record-only commit distinct from item 43's go.

Whether this specification must itself be committed and pinned the way A12 item 21 pins the stage 1 build specification (DN:1947-1953) is open question 10.

## 9. The item 43 run

### 9.1 Where and how

- **Host:** X2-1 only (PLAN:99; `AMENDMENT_A15_adopted.md:77`; A17 leaves this campaign on X2-1, DN A17 status paragraph) [R].
- **One reader at a time, one numerical library thread initially, 16 GB initial memory allowance** (PLAN:326). The allowance is a planning assumption; if it is inadequate the run stops and is replanned inside the budget, with no truncation and no change to the bootstrap arithmetic (PLAN:328).
- **Checkout:** a reader checkout at the commit of section 8.5, separate from the execution checkout, which never receives code (DN:1743). It must be a git checkout whose HEAD holds the compatibility records, because `accepted_identities()` compares each record with `git show HEAD:` (`compatibility_a10.py:51-57`, `:75`) [R].
- **Inputs:** read in place, read-only. **Outputs:** a new folder outside every run root and outside the execution checkout.
- **Service:** `llm down` recorded before the run and supervised restoration after, as for any operation over one hour (PLAN:340).
- **Sequence:** `collect`; reader A `verify`; reader B `verify`; then for each reader in turn `read --component both` twice into separate folders; then the byte comparison per reader, the blind comparison across readers, and the seal records. Nothing is opened.

### 9.2 Runtime, a budget estimate

Volume to read and parse per full pass of one reader [M for the first two, I for the rest]:

| Input | Runs | Bytes |
|---|---:|---:|
| sqrt outputs | 4,400 | 9.96 GB (INV-S `roots.runs.output_bytes`) |
| crowding outputs | 4,400 | 12.06 GB (INV-C) |
| two sigma arms | 1,000 | about 2.6 GB, scaled from the two arms above at about 2.5 MB per run |
| comparator subset | 6,225 | about 14.7 GB, at stage 1's average of about 125 GB over 53,100 runs (`REQUIREMENTS_DIGEST.md:145`) |
| **One pass** | **16,025** | **about 39 GB** |

Passes: two `verify` passes and four `read` passes, six in all, about 235 GB.

The bootstrap is small beside this: each boundary call draws 9 x 50,000 x 100 plus 9 x 50,000 x 400 integers, and each cap* call 7 x 50,000 x 175; all 14 comparisons with their descriptive differences are a few minutes of single-thread time [I from the array shapes at `reading_a6.py:128`, `:445-446`; not measured].

The parse rate is the unknown. I have no measurement of strict JSON parsing on these files. Assuming 15 to 50 MB per second on one process [G]:

| Parse rate | Six passes | With about 1 hour of overhead |
|---:|---:|---:|
| 50 MB/s | 1.3 h | 2.3 h |
| 25 MB/s | 2.6 h | 3.6 h |
| 15 MB/s | 4.4 h | 5.4 h |

**Budget estimate: 2.5 to 5.5 hours, resting on the byte volumes above and an unmeasured parse rate.** Below about 13 MB per second the six passes alone exceed five hours and the total passes the 6 hour budget estimate. Step 6 of the build plan replaces the assumption with a measurement before the go. If the measured projection exceeds 6 hours, the choice returns to the operator before the run: allow parse workers (open question 8), or fold `verify` into the first `read` pass. The 12 hour ceiling is not approached under any row.

Hashing is not the constraint: the crowding inventory hashed 12.21 GB in under two seconds from the page cache (`stage2_inventory_crowding_2026-11-21/REPORT.md:238`) [R].

Memory, a budget estimate [I, from array shapes]: the largest transient is one comparator cell's draw, 50,000 x 400 64-bit integers (160 MB) plus the gathered floats (160 MB). With one parsed output in memory at a time, the peak should stay under 2 GB, against the 16 GB allowance. The probe in step 6 measures it.

### 9.3 What it charges

Against the **12 hour ceiling and 6 hour budget estimate** for "the two stage 2 sealed reading components and their verification" (`AMENDMENT_A15_adopted.md:46`; APP item 43): every active X2-1 wall hour of item 43, at rate 1.0 (`AMENDMENT_A15_adopted.md:60`). That includes `llm down` and restoration, `collect`, both `verify` passes, all `read` passes, the comparisons, hashing, seal publication and cleanup, and any interrupted or refused attempt (`AMENDMENT_A15_adopted.md:61`). A refused attempt's time is not erased by starting a new folder.

The 6 hour figure is an assumed allowance, not a measured reader runtime (PLAN:201; REQ section 4).

## 10. Open questions, ranked by severity

**1. Do the requirements' table figures agree with the registration and the code? Yes. Three statements in REQ are stale.** (The brief asks for this first.)

- No disagreement in components, family sizes 18 and 33, levels, tails or seeds. Basis in section 1.2.
- Stale, not wrong at the time: (a) REQ section 1 says `compare_boundary` "currently uses its module constant regardless of its `alpha` argument". At `4dcc18c2` it has the explicit `undefined_resample_tail` parameter (`reading_a6.py:311`). (b) REQ cites `admission_a13.py:97 to 98` and `:142 to 150`; the functions are now at `:180-181` and `:225-233`. (c) REQ cites `production_runner.py:259 to 261` and `:274 to 276`; now `:289-291` and `:301-307`. The `integration.py` citations still match.
- **Blocks:** nothing. **Settles it:** the interpreter noting that REQ's hash is frozen by A16 and that this draft's citations are to `4dcc18c2`.

**2. What binds the comparator, and were its path strings the stage 2 strings? (Critical.)**

- The stage 2 inventories bind arm roots only [M]. The comparator's spec, records, outputs and family chain need one sealed record whose hash the operator authorizes. Candidates named in my sources, none of which I may open: stage 1 reader A's sealed `collection.json` (CC:156); the stage 1 closeout manifest's `run_roots` entry for `main_r2` (`REQUIREMENTS_DIGEST.md:59`); `a12_stage1/checks/stage1_run_manifest_inventory.json` (`REQUIREMENTS_DIGEST.md:71`).
- G2 rebuilds the comparator's jobs with `STAGE2_PATHS["nominal"]`. If stage 1's main spec used different calibration or table strings, the rebuilt jobs will not equal the spec and the gate must take the spec's own strings instead.
- **Blocks:** freezing section 2.2's comparator part, G2 and G4 for the comparator, and the comparator shape of the L2 fixtures.
- **Settles it:** from X2-1, (i) the path and sha256 of the stage 1 record that lists `main_r2`'s `verified_output_hashes.json` hash and spec seal; (ii) in `<main_r2>/manifest.json`, the values of `payload.jobs[0].config.calibration_path` and `.tables_path`, which are path strings and carry no result; (iii) whether the comparator inventory should instead be made new, as a fifth reading-input inventory under item 42, which I recommend, because it gives all five inputs one schema.

**3. May `verify` run on the real inputs under its own go, before the compute go? (High.)**

- `verify` opens outputs to hash and structure-check them and emits pass or a refusal label. It computes no estimator. Stage 1 refused at input verification on its first registered attempts and again on its fifth and sixth (RS:271, RS:282, RS:297), each fixed under a separate operator go.
- **Blocks:** the item 43 sequence and its budget. **Settles it:** an operator decision. My recommendation is yes, as a named part of item 43, with the stage 1 rule that a fix is allowed only when no outcome value has been computed (RS:227).

**4. The not-run conventions. (High.)**

- (a) Section 3.6 writes `status: "not run"` with `verdict: "undetermined"`. The alternative is a fifth verdict string `not run`. A6 has four verdicts (DN:1397-1401).
- (b) Which records prove a final refusal: the A16 family record's terminal latch, the refused admission records, the operator's closeout entry, or all three; and the exact registered reason string for each terminal path of A16 item 10.
- **Blocks:** F13 and the output schema. **Settles it:** the interpreter's reading of DN:1376 with A16:132, and the list of terminal states the family record can hold (`validation_extension_a16.py:607-632`, which I read only as a function inventory).

**5. Comparison key spelling. (High for the builds, nil for the numbers.)**

- The stage 1 readers differ (section 1.1). This draft pins reader B's form. If the stage 1 sealed sensitivity component used reader A's form, the stage 2 keys will not line up with it by string.
- **Blocks:** nothing if confirmed; a build round if changed later. **Settles it:** the interpreter, who can see how stage 1's comparison handled the difference; I could not, since that record is outside my allowlist.

**6. Who generates the L2 fixtures? (High.)**

- Stage 1 had builder A generate and builder B receive files (RS:68-75, RS:235-239). That leaves A's reader tested on a fixture its builder designed. The alternative is a third generator who builds no reader.
- **Blocks:** build step 3. **Settles it:** an interpreter decision. I recommend a separate generator for F6 to F15 if one is available, and builder A otherwise, with B adding its own synthetic tests as in stage 1 (`DIRECTIVE_B…:33`).

**7. Separate counts for a no-admitted run. (Medium.)**

- Section 4.5 reports them `not recorded`. `balanced_fallbacks_by_reason` could be counted from the per-step `balanced_fallback_reason`, but the excluded-rule count cannot be reproduced exactly from `unavailable_rules`, which lists every unavailable rule and not only the eligible ones (`admission_a13.py:190-191` against `integration.py:428`) [I].
- **Blocks:** nothing; changes `incidence_counts`. **Settles it:** the interpreter confirming "not recorded", which I recommend, since a partial derivation would mix exact and inexact counts.

**8. Parse worker processes on X2-1. (Medium.)**

- PLAN:326 says one reader at a time and one library thread initially. Reader B's stage 1 design used a process pool for extraction (rB/`reading.py:30-48`). Workers would cut section 9.2's runtime roughly in proportion; the bootstrap stays in the parent on one thread.
- **Blocks:** the runtime budget only if the measured rate is low. **Settles it:** an operator decision, after the probe in build step 6.

**9. The sigma inventories' schema. (Medium.)**

- INV-S and INV-C differ in schema and key names [M]. If the two sigma inventories introduce two more shapes, the inventory adapter grows and so does the refusal risk.
- **Blocks:** nothing now. **Settles it:** making the sigma inventories with INV-C's schema and key names, and including in each the admission check record and the pre-dispatch run spec. INV-S lacks both [M].

**10. Is this specification pinned like a registered build specification? (Medium.)**

- A12 item 21 fixes the stage 1 reader's input contract in its build specification (DN:1947-1953). A16 freezes REQ by hash but says nothing of an implementation specification [R].
- **Blocks:** the commit request's content. **Settles it:** the interpreter. I recommend committing it with the freeze record and recording its hash in every output, without touching the design note.

**11. What A5 disclosure the sqrt reading must carry. (Medium.)**

- Section 5.3 attaches the label record by hash. Stage 1 also reported per-cell table disclosures (rB/`values.py:115-117`). I did not read A5's reporting clause (DN:1131 onward), which the brief did not list.
- **Blocks:** `family.sqrt.labels`. **Settles it:** reading A5's reporting clause and A8 item 11 (DN:1488) against the stage 1 `tables.<cell>` rule.

**12. Should the reader open `dispatch.sqlite` at item 43? (Medium.)**

- This draft relies on the item 42 inventories for session, launch and recheck checks and does not re-audit the database, unlike stage 1's collector (CC:141-147).
- **Blocks:** section 2.4's scope. **Settles it:** the interpreter. Relying on the accepted inventory is the smaller reader; the cost is that the reader's host and session evidence is second-hand.

**13. A cross-check of the comparator against stage 1. (Low.)**

- The stage 2 comparator boundary on the nine-point grid is the same number stage 1 sealed as the comparator of its `k1p5` boundary. Equality would confirm the comparator extraction. It requires reading one value from an opened stage 1 file, which this draft does not do.
- **Blocks:** nothing. **Settles it:** an operator decision. A value-free form exists: compare a hash of the comparator's per-cell survival counts, if stage 1 recorded one. I do not know that it did.

**14. Equality with the registered tails cannot occur at 50,000 resamples. (Low, for the record.)**

- Shown in F2's row. The strict comparison's boundary lies between 69 and 70 undefined resamples for A10 and between 37 and 38 for A6 [I]. No action; it explains why F2 injects the tail.

**15. The sigma run roots' paths. (Low.)**

- Inferred from the sqrt and crowding pattern (section 2.1). **Settles it:** their inventories.
