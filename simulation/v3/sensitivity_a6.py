"""A6 sensitivity and convergence runs: invariance, seeds and manifests.

Amendment A6, 2026-09-29. This module builds the five arms' run jobs, the
global seed-collision check, and the two kinds of registered spec the unchanged
production runner accepts. It also provides the rerun-path invariance check that
asserts A6 changes no file entering the code identity.

New modules only. This module reads inputs read-only, launches nothing, and
computes no survival, extinction or fire rate.
"""
import subprocess
from pathlib import Path

from .artifacts import (SIMULATION, code_identity, digest, file_hash, read, seal, source_manifest,
                        stable_job, unseal)
from . import continuation_validation as cv
from .study import R1_RR, R1_ALPHA, R2_ALPHA, R2_CAP, rerun_jobs

# Canonical registered rerun artifact paths, relative to simulation/. The main
# reruns load the A4 nominal family (A5 adds labels only, not table identity).
NOMINAL_CALIBRATION_PATH = "v3/runs/registered/v3_rerun_calibration.json"
NOMINAL_TABLES_PATH = "v3/runs/registered/v3_rerun_tables_A4.json"

# The five R1 rr nearest v2.0's registered inflection 0.063 (A6 section 2).
SIGMA_RR = (0.059, 0.060, 0.062, 0.064, 0.066)
WEIGHT_CORNERS = ((0.75, 0.25), (0.75, 0.75), (8.0, 0.25), (8.0, 0.75))
CENTER_KAPPA, CENTER_THETA = 8.0, 0.5
R2_SIGMA_RR = 0.064
SIGMA_VARIANTS = ("sigma_squared_x10", "sigma_squared_x0.1")

# Expected run counts, asserted before dispatch.
COUNT_WEIGHT_CORNER = 17600
COUNT_HORIZON = 1800
COUNT_CROWDING = 4400
COUNT_SIGMA = 1000


class SeedCollision(RuntimeError):
    """Raised, to halt, on any A6 run seed collision."""


# ---------------------------------------------------------------------------
# Rerun-path invariance
# ---------------------------------------------------------------------------

def _is_a6_module(relpath):
    name = Path(relpath).name
    return name.endswith(".py") and "_a6" in name


def _git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True).stdout


def _normalize(data):
    """LF-normalize bytes: map only CRLF to LF, so a git checkout's CRLF and the
    repository's LF compare equal. No other byte is changed."""
    return data.replace(b"\r\n", b"\n")


def rerun_path_files(manifest=None):
    """The source_manifest files that enter the code identity, excluding the new
    A6 modules."""
    manifest = manifest or source_manifest()
    return sorted(p for p in manifest if not _is_a6_module(p))


def _committed_source_files(commit, repo):
    """The files at ``commit`` that would enter the code identity, by the same
    selection as artifacts.source_manifest: top-level v3/*.py, top-level
    simulation/*.py that are not tests, and the three reviewed compatibility
    JSONs. Excludes the A6 modules (which do not exist at the rerun commit)."""
    out = _git(repo, "ls-tree", "-r", "--name-only", commit, "--", "simulation")
    files = set()
    allowed_json = {"v3/calibration_compatibility_A1.json", "v3/table_compatibility_A2.json",
                    "v3/table_compatibility_A3.json", "v3/a10_constants.json"}
    for line in out.decode("utf-8").splitlines():
        if not line.startswith("simulation/"):
            continue
        rel = line[len("simulation/"):]
        parts = rel.split("/")
        is_v3_py = len(parts) == 2 and parts[0] == "v3" and rel.endswith(".py")
        is_top_py = len(parts) == 1 and rel.endswith(".py") and not parts[0].startswith("test_")
        if (is_v3_py or is_top_py or rel in allowed_json) and not _is_a6_module(rel):
            files.add(rel)
    return files


def rerun_path_invariance(commit, repo=None):
    """Compare every source_manifest file except the A6 modules to ``commit``'s
    version via ``git show``, after LF normalization, and detect any rerun-path
    file present at the commit but absent from the current manifest.

    Returns a dict with the matched files, any content mismatches, files removed
    since the commit (present then, absent now) and files added since (present
    now, absent then). A6's prepare and launch steps assert every list but
    ``matched`` and ``a6_modules_excluded`` is empty for the rerun commit.
    """
    repo = Path(repo or SIMULATION.parent)
    manifest = source_manifest()
    current = set(rerun_path_files(manifest))
    committed = _committed_source_files(commit, repo)
    matched, mismatches, missing = [], [], []
    for relpath in sorted(current):
        working = SIMULATION / relpath
        try:
            data = _git(repo, "show", "%s:simulation/%s" % (commit, relpath))
        except subprocess.CalledProcessError:
            missing.append(relpath)
            continue
        if _normalize(data) == _normalize(working.read_bytes()):
            matched.append(relpath)
        else:
            mismatches.append(relpath)
    removed = sorted(committed - current)      # present at the commit, absent now
    added = sorted(current - committed)        # present now, absent at the commit
    return {"commit": commit, "matched": matched, "mismatches": mismatches,
            "missing_at_commit": missing, "removed_since_commit": removed, "added_since_commit": added,
            "a6_modules_excluded": sorted(p for p in manifest if _is_a6_module(p))}


def assert_rerun_path_invariant(commit, repo=None):
    """Halt unless every rerun-path file is byte-identical (LF-normalized) to the
    commit's version, with no rerun-path file removed since or added since the
    commit. Returns the invariance result."""
    result = rerun_path_invariance(commit, repo)
    bad = {k: result[k] for k in ("mismatches", "missing_at_commit", "removed_since_commit", "added_since_commit")
           if result[k]}
    if bad:
        raise RuntimeError("rerun-path invariance failed at %s: %r" % (commit, bad))
    return result


def rerun_code_identity(commit, repo=None):
    """The code identity a rerun-checkout runner computes at ``commit``: the
    digest of the source manifest built from the commit's blob bytes for every
    rerun-path file. The A6 modules do not exist at that commit, so they are
    excluded. Assumes the runner's working tree is LF (the X2 is Linux)."""
    import hashlib
    repo = Path(repo or SIMULATION.parent)
    manifest = {}
    for relpath in rerun_path_files():
        committed = _git(repo, "show", "%s:simulation/%s" % (commit, relpath))
        manifest[relpath] = hashlib.sha256(_normalize(committed)).hexdigest()
    return digest(manifest)


# ---------------------------------------------------------------------------
# The forbidden seed set (A1, A4, A5, probe, planning, rerun)
# ---------------------------------------------------------------------------

def _a1_manifest(a1_source_root):
    return unseal(read(Path(a1_source_root) / "tables_A1_manifest.json"))


def _a1_route(a1_source_root, job, source_code):
    """The real route of an A1 table job, from its output. Every A1 job config
    has route 'auto', so the executed route (plain or fv) lives in the output,
    not the config."""
    from .table_validation_a4 import _load_a1
    return _load_a1(a1_source_root, job, source_code)["result"]["route"]


def forbidden_seeds(a1_source_root, probe_root=None, *, rerun_manifest=None, registered=False,
                    calibration_path=NOMINAL_CALIBRATION_PATH, tables_path=NOMINAL_TABLES_PATH):
    """Every seed A6 must avoid, derived with the committed functions.

    Covers every A1 job seed; A4's stream seeds for both routes; A5's FV-plain
    stream seeds (replicates 1..3) over the primary FV A1 jobs, whose real route
    comes from the A1 output; the D26 probe seeds; the planning P1, P1-census, P3
    and P4 seeds (replicates 0..3); and the 24,900 main rerun seeds, taken from
    the sealed rerun manifest when one is given. A registered build requires the
    sealed rerun manifest rather than rebuilt path strings.
    """
    from .table_validation_a4 import load_probe_seeds
    a1_source_root = Path(a1_source_root)
    manifest = _a1_manifest(a1_source_root)
    source_code = manifest.get("source_family", {}).get("code_hash") or manifest.get("code_hash")
    forbidden = set()
    for job in manifest["jobs"]:
        s = int(job["seed"])
        forbidden.add(s)
        for route in ("plain", "fv"):
            forbidden.update(int(v) for v in cv.derive_seeds(s, route).values())
        forbidden.add(cv._planning_p1_seed(s))
        forbidden.add(cv._planning_p1_census_seed(s))
        forbidden.update(cv._planning_p3_seed(s, r) for r in range(4))
        forbidden.update(cv._truncated_sha("planning_P4", s, r) for r in range(4))
        # A5 FV-plain stream seeds over the primary FV A1 jobs: the real route
        # comes from the A1 output, since every job config has route "auto".
        if job["config"].get("setting_name", "primary") == "primary" and _a1_route(a1_source_root, job, source_code) == "fv":
            forbidden.update(cv.stream_seed("v3_R_fvplain", s, r) for r in (1, 2, 3))
    if probe_root:
        forbidden.update(int(s) for s in load_probe_seeds(probe_root))
    if registered and rerun_manifest is None:
        raise ValueError("a registered A6 build requires the sealed main rerun manifest for the rerun seeds")
    if rerun_manifest is not None:
        rerun_jobs_list = unseal(rerun_manifest)["jobs"] if set(rerun_manifest) == {"payload", "sha256"} else rerun_manifest["jobs"]
        if len(rerun_jobs_list) != 24900:
            raise ValueError("the main rerun manifest must hold the 24,900 rerun jobs; found %d" % len(rerun_jobs_list))
        forbidden.update(int(j["seed"]) for j in rerun_jobs_list)
    else:
        forbidden.update(int(j["seed"]) for j in rerun_jobs(calibration_path, tables_path))
    return forbidden


def assert_seeds_clear(jobs, forbidden, *, require_probe=None):
    """Assert every job seed is distinct and disjoint from the forbidden set.
    Halts on any collision. ``require_probe`` (a set) must be non-empty for a
    registered run."""
    seeds = [int(j["seed"]) for j in jobs]
    if len(set(seeds)) != len(seeds):
        raise SeedCollision("A6 run seeds are not pairwise distinct")
    hits = sorted(set(seeds) & set(forbidden))
    if hits:
        raise SeedCollision("A6 run seed collides with a forbidden seed: %d collisions, e.g. %r"
                            % (len(hits), hits[:5]))
    if require_probe is not None and not require_probe:
        raise ValueError("a registered A6 run requires a non-empty D26 probe root")
    return True


def assert_global_seed_distinctness(groups, forbidden):
    """One global check over every new A6 seed. ``groups`` maps a name (for
    example 'crowding_table_jobs', 'sigma_x10_a4_streams', 'nominal_runs',
    'variant_runs') to an iterable of seeds. Every seed must be disjoint from the
    forbidden set and from every other new seed. Halts on any collision. Returns
    the total count of new seeds checked."""
    seen = {}
    for name, seeds in groups.items():
        for raw in seeds:
            s = int(raw)
            if s in forbidden:
                raise SeedCollision("%s seed %d collides with a forbidden (A1/A4/A5/probe/planning/rerun) seed" % (name, s))
            if s in seen:
                raise SeedCollision("%s seed %d collides with %s" % (name, s, seen[s]))
            seen[s] = name
    return len(seen)


# ---------------------------------------------------------------------------
# The one A6 seed registry
# ---------------------------------------------------------------------------

def _a4_stream_superset(table_job_seed):
    """Every A4 stream seed A4 could derive from a table job seed, over both
    routes: the fit, census and all three validate replicates. The actual route's
    streams are a subset."""
    return ([cv.fit_seed(table_job_seed), cv.census_seed(table_job_seed)]
            + [cv.validate_seed(table_job_seed, r) for r in cv.VALIDATE_REPLICATES])


def build_seed_registry(family_calibration_paths, run_paths, *, a1_source_root, probe_root, rerun_manifest,
                        calibration_path=NOMINAL_CALIBRATION_PATH, tables_path=NOMINAL_TABLES_PATH):
    """Compute every A6 seed deterministically from the configurations at the
    first A6 step (the variant calibrations): every variant table job seed, every
    variant A4 stream seed (exactly as A4 derives them from the table jobs, over
    both routes), and every run seed in every arm. Check them all against the full
    forbidden set and against each other, and return the sealed-shape registry.

    ``family_calibration_paths`` maps each family to the calibration path its
    table jobs use. ``run_paths`` maps 'nominal', 'crowding' and each sigma variant
    to the (calibration_path, tables_path) its runs use.
    """
    from . import tables_a6 as t6
    table_jobs, a4_streams = {}, {}
    for family, cal in family_calibration_paths.items():
        seeds = [int(j["seed"]) for j in t6.build_jobs(family, cal)]
        table_jobs[family] = seeds
        streams = []
        for s in seeds:
            streams.extend(int(v) for v in _a4_stream_superset(s))
        a4_streams[family] = streams
    ncal, ntab = run_paths["nominal"]
    runs = {"nominal_runs": [int(j["seed"]) for j in (build_weight_corner_jobs(ncal, ntab) + build_horizon_jobs(ncal, ntab))]}
    ccal, ctab = run_paths["crowding"]
    runs["crowding_runs"] = [int(j["seed"]) for j in build_crowding_jobs(ccal, ctab)]
    for variant in SIGMA_VARIANTS:
        runs[variant + "_runs"] = [int(j["seed"]) for j in build_sigma_jobs({variant: run_paths[variant]})]
    forbidden = forbidden_seeds(a1_source_root, probe_root, rerun_manifest=rerun_manifest, registered=True,
                                calibration_path=calibration_path, tables_path=tables_path)
    groups = {}
    groups.update({"table_jobs:" + f: v for f, v in table_jobs.items()})
    groups.update({"a4_streams:" + f: v for f, v in a4_streams.items()})
    groups.update({"runs:" + a: v for a, v in runs.items()})
    total = assert_global_seed_distinctness(groups, forbidden)
    return {"schema": "v3-A6-seed-registry-1", "table_jobs": table_jobs, "a4_streams": a4_streams,
            "runs": runs, "total_seeds": total}


def assert_registry_seeds(registry, kind, key, seeds):
    """Assert a later step's own seeds match the sealed registry's entry for that
    step, refusing otherwise. ``kind`` is 'table_jobs', 'a4_streams' or 'runs'. For
    A4 streams the actual route's seeds must be a subset of the registry's both-route
    superset; the others must be exactly equal."""
    registered = set(int(s) for s in registry[kind][key])
    actual = set(int(s) for s in seeds)
    if kind == "a4_streams":
        if not actual <= registered:
            raise SeedCollision("A4 stream seeds for %s are not all in the A6 seed registry" % key)
    elif actual != registered:
        raise SeedCollision("%s seeds for %s do not equal the A6 seed registry entry" % (kind, key))
    return True


# ---------------------------------------------------------------------------
# Arm job builders
# ---------------------------------------------------------------------------

def _cell(arm, grid, rr, alpha, cap, kappa, theta, steps, calibration_path, tables_path,
          crowding="total", variant=None):
    """The rerun-shaped config for one A6 sensitivity cell. The cell identity
    includes kappa, theta, the step count, the comparator grid (R1 or R2) and the
    variant (via the model and the explicit arm/grid/variant markers), so every
    arm's seeds differ from the 24,900 main reruns and from each other. The grid
    marker separates an R1 cell from the R2 cell at the same coordinates, whose
    reading (survival/boundary vs cap*) and comparator differ."""
    model = {"reproduction_rate": rr, "alpha": alpha, "successor_capability": cap,
             "kappa": kappa, "theta": theta, "crowding": crowding}
    return {"phase": arm, "category": arm, "a6_grid": grid, "steps": steps, "model": model,
            "calibration_path": calibration_path, "tables_path": tables_path,
            "a6_arm": arm, "a6_variant": variant}


def _grid_cells():
    """The weight-corner grid: R1's 9 rr at alpha 1.0, cap 1.5, plus R2's 5 alpha
    x 7 capabilities at rr 0.064. 44 cells; the R1 and R2 (0.064, 1.0, 1.5) cells
    are distinct, carrying different grid markers and comparators."""
    cells = [("R1", rr, 1.0, 1.5) for rr in R1_RR]
    cells += [("R2", R2_SIGMA_RR, alpha, cap) for alpha in R2_ALPHA for cap in R2_CAP]
    assert len(cells) == 44, len(cells)
    return cells


def build_weight_corner_jobs(calibration_path=NOMINAL_CALIBRATION_PATH, tables_path=NOMINAL_TABLES_PATH,
                             seeds=100, tag="v3_rerun"):
    jobs = []
    for kappa, theta in WEIGHT_CORNERS:
        for grid, rr, alpha, cap in _grid_cells():
            config = _cell("a6_weight_corner", grid, rr, alpha, cap, kappa, theta, 500, calibration_path, tables_path)
            jobs.extend(stable_job("rerun", config, tag, i) for i in range(seeds))
    assert len(jobs) == COUNT_WEIGHT_CORNER, len(jobs)
    return jobs


def build_horizon_jobs(calibration_path=NOMINAL_CALIBRATION_PATH, tables_path=NOMINAL_TABLES_PATH,
                       seeds=200, tag="v3_rerun"):
    jobs = []
    for rr in R1_RR:
        config = _cell("a6_horizon", "R1", rr, 1.0, 1.5, CENTER_KAPPA, CENTER_THETA, 1000, calibration_path, tables_path)
        jobs.extend(stable_job("rerun", config, tag, i) for i in range(seeds))
    assert len(jobs) == COUNT_HORIZON, len(jobs)
    return jobs


def build_crowding_jobs(calibration_path, tables_path, seeds=100, tag="v3_rerun"):
    """The reproductive-age crowding variant on the weight-corner grid at the
    center weights, against the crowding family's tables."""
    jobs = []
    for grid, rr, alpha, cap in _grid_cells():
        config = _cell("a6_crowding", grid, rr, alpha, cap, CENTER_KAPPA, CENTER_THETA, 500,
                       calibration_path, tables_path, crowding="reproductive", variant="crowding_reproductive")
        jobs.extend(stable_job("rerun", config, tag, i) for i in range(seeds))
    assert len(jobs) == COUNT_CROWDING, len(jobs)
    return jobs


def build_sigma_jobs(variant_paths, seeds=100, tag="v3_rerun"):
    """Both sigma0^2 variants: five rr at alpha 1.0 and cap 1.5, at center
    weights, each against its own family and calibration. ``variant_paths`` maps
    a variant name to (calibration_path, tables_path). 1,000 jobs."""
    jobs = []
    for variant in variant_paths:
        calibration_path, tables_path = variant_paths[variant]
        for rr in SIGMA_RR:
            config = _cell("a6_" + variant, "R1", rr, 1.0, 1.5, CENTER_KAPPA, CENTER_THETA, 500,
                           calibration_path, tables_path, variant=variant)
            jobs.extend(stable_job("rerun", config, tag, i) for i in range(seeds))
    # 500 jobs per sigma0^2 variant (5 rr x 100 seeds); 1,000 for both.
    assert len(jobs) == len(variant_paths) * len(SIGMA_RR) * seeds, len(jobs)
    return jobs


# ---------------------------------------------------------------------------
# Registered specs
# ---------------------------------------------------------------------------

def _rerun_profile(phase, calibration_path, tables_path, crowding="total", kappa=CENTER_KAPPA, theta=CENTER_THETA):
    """A short rerun configuration-test profile for one phase (throughput only,
    shortened in length). Its worker candidates are A6's own (workers_local 8 and
    12; workers_x2 A4's list), the only counts the unchanged runner tests."""
    from .pilot import profile
    from .tables_a6 import A6_WORKERS_LOCAL, A6_WORKERS_X2
    model = {"reproduction_rate": 0.064, "alpha": 1.0, "successor_capability": 1.5,
             "kappa": kappa, "theta": theta, "crowding": crowding}
    prof = profile("rerun", {"phase": phase, "steps": 5, "model": model,
                             "calibration_path": calibration_path, "tables_path": tables_path})
    prof["workers_local"] = list(A6_WORKERS_LOCAL)
    prof["workers_x2"] = list(A6_WORKERS_X2)
    # Occupy every tested worker at 8 and 12 (two waves), so the occupancy check
    # passes on the WSL workstation as well as the X2.
    prof["jobs_per_worker"] = 2
    return prof


def _spec(tag, code_hash, registration, phases, configuration, jobs, wall_share_hours):
    """A registered spec in study.registered_spec's shape, so the unchanged
    production runner accepts it. The runner's wall_seconds carries the budget's
    slack-aware ceiling (floored to whole seconds)."""
    import math
    from . import budget_a6
    return {"schema": "v3-registered-1", "registered": True, "tag": tag,
            "registration": registration, "code_hash": code_hash,
            "wall_seconds": int(math.floor(wall_share_hours * 3600)), "cleanup_reserve_seconds": 300,
            "configuration_seconds": 900, "phases": list(phases), "configuration": configuration,
            "jobs": jobs, "publication": None,
            "a6_program_ceiling_hours": budget_a6.PROGRAM_CEILING_HOURS, "a6_wall_share_hours": wall_share_hours}


def _run_wall(ledger, component, machine, prior_components):
    from . import budget_a6
    ledger = ledger or budget_a6.build_ledger()
    budget_a6.assert_up_to_date(ledger, prior_components)
    return budget_a6.runner_ceiling_hours(ledger, component, machine)


def _require_registry(seed_registry):
    if seed_registry is None:
        raise ValueError("a registered A6 run spec requires the sealed A6 seed registry")


def nominal_run_spec(rerun_commit, registration, *, a1_source_root, probe_root, rerun_manifest, repo=None,
                     ledger=None, seed_registry=None, machine="x2", prior_components=(),
                     calibration_path=NOMINAL_CALIBRATION_PATH, tables_path=NOMINAL_TABLES_PATH):
    """The weight-corner and horizon arms, to run in the rerun checkout against
    the nominal tables. Its code_hash is the rerun commit's identity. Asserts
    rerun-path invariance, seed clearance, the global seed check and the seed
    registry first, requires the consumption log to be up to date with every
    earlier launch, and takes its wall ceiling from the budget on ``machine``."""
    _require_registry(seed_registry)
    assert_rerun_path_invariant(rerun_commit, repo)
    jobs = build_weight_corner_jobs(calibration_path, tables_path) + build_horizon_jobs(calibration_path, tables_path)
    probe = _probe_or_empty(probe_root)
    forbidden = forbidden_seeds(a1_source_root, probe_root, rerun_manifest=rerun_manifest, registered=True,
                                calibration_path=calibration_path, tables_path=tables_path)
    assert_seeds_clear(jobs, forbidden, require_probe=probe)
    assert_global_seed_distinctness({"nominal_runs": [j["seed"] for j in jobs]}, forbidden)
    assert_registry_seeds(seed_registry, "runs", "nominal_runs", [j["seed"] for j in jobs])
    code_hash = rerun_code_identity(rerun_commit, repo)
    configuration = {"a6_weight_corner": _rerun_profile("a6_weight_corner", calibration_path, tables_path),
                     "a6_horizon": _rerun_profile("a6_horizon", calibration_path, tables_path)}
    return _spec("v3_rerun", code_hash, registration, ["a6_weight_corner", "a6_horizon"],
                 configuration, jobs, _run_wall(ledger, "nominal_runs", machine, prior_components))


def crowding_run_spec(rerun_commit, registration, *, crowding_paths, a1_source_root, probe_root, rerun_manifest,
                      repo=None, ledger=None, seed_registry=None, machine="x2", prior_components=(),
                      calibration_path=NOMINAL_CALIBRATION_PATH, tables_path=NOMINAL_TABLES_PATH):
    """The crowding arm alone, at A6's identity against the crowding family. A
    separate spec, so a failed crowding family reports only the crowding arm as
    not run (A6)."""
    _require_registry(seed_registry)
    assert_rerun_path_invariant(rerun_commit, repo)
    crowding_cal, crowding_tables = crowding_paths
    jobs = build_crowding_jobs(crowding_cal, crowding_tables)
    probe = _probe_or_empty(probe_root)
    forbidden = forbidden_seeds(a1_source_root, probe_root, rerun_manifest=rerun_manifest, registered=True,
                                calibration_path=calibration_path, tables_path=tables_path)
    assert_seeds_clear(jobs, forbidden, require_probe=probe)
    assert_global_seed_distinctness({"crowding_runs": [j["seed"] for j in jobs]}, forbidden)
    assert_registry_seeds(seed_registry, "runs", "crowding_runs", [j["seed"] for j in jobs])
    configuration = {"a6_crowding": _rerun_profile("a6_crowding", crowding_cal, crowding_tables, crowding="reproductive")}
    return _spec("v3_rerun", code_identity(), registration, ["a6_crowding"], configuration, jobs,
                 _run_wall(ledger, "crowding_runs", machine, prior_components))


def sigma_run_spec(rerun_commit, registration, variant, variant_paths, *, a1_source_root, probe_root, rerun_manifest,
                   repo=None, ledger=None, seed_registry=None, machine="x2", prior_components=(),
                   calibration_path=NOMINAL_CALIBRATION_PATH, tables_path=NOMINAL_TABLES_PATH):
    """One sigma0^2 variant arm alone, at A6's identity against that variant's
    family. A separate spec per variant, so a failed variant family reports only
    its own arm as not run (A6). ``variant_paths`` is (calibration_path,
    tables_path) for this variant."""
    if variant not in SIGMA_VARIANTS:
        raise ValueError("unknown sigma0^2 variant %r" % variant)
    _require_registry(seed_registry)
    assert_rerun_path_invariant(rerun_commit, repo)
    jobs = build_sigma_jobs({variant: variant_paths})
    jobs = [j for j in jobs if j["config"]["a6_variant"] == variant]
    probe = _probe_or_empty(probe_root)
    forbidden = forbidden_seeds(a1_source_root, probe_root, rerun_manifest=rerun_manifest, registered=True,
                                calibration_path=calibration_path, tables_path=tables_path)
    assert_seeds_clear(jobs, forbidden, require_probe=probe)
    assert_global_seed_distinctness({variant + "_runs": [j["seed"] for j in jobs]}, forbidden)
    assert_registry_seeds(seed_registry, "runs", variant + "_runs", [j["seed"] for j in jobs])
    phase = "a6_" + variant
    configuration = {phase: _rerun_profile(phase, *variant_paths)}
    return _spec("v3_rerun", code_identity(), registration, [phase], configuration, jobs,
                 _run_wall(ledger, variant + "_runs", machine, prior_components))


def _probe_or_empty(probe_root):
    from .table_validation_a4 import load_probe_seeds
    return load_probe_seeds(probe_root) if probe_root else set()
