"""Requalification worker: one item, inside one scratch checkout, at one identity.

Invoked by ``requalification.harness`` as a separate interpreter per item::

    python -B -E worker.py --checkout <scratch checkout root> --item <item.json> --result <out.json>

The worker puts the checkout's ``simulation/`` first on ``sys.path`` and imports
that checkout's ``v3`` package: the original producer's unchanged code (the
harness directory itself holds no ``v3``, and ``-E`` ignores PYTHONPATH). It
refuses to run unless that checkout's ``code_identity()`` equals the item's
producing identity. Everything it writes goes under the scratch directory the
harness names (inside that checkout's ``simulation/v3``, so the producer's own
scoped-write guard applies) and to the one result file.

``replay_item`` is also importable, so fixture tests can exercise the same
logic in-process against monkeypatched producer functions.
"""
import argparse
import contextlib
import hashlib
import json
import os
import shutil
import sys
import time
from pathlib import Path

# Named timing exclusions at the result root only (REQUALIFICATION_PLAN.md,
# section 4). Every nested result, trajectory, step and scientific field is
# compared. The envelope and result ``code_hash`` are retained in the
# comparison, since both sides must carry the same original producer identity.
TIMING_EXCLUSIONS = ("seconds", "trajectory_seconds", "rescore_seconds", "scoring_seconds_by_k_star")
COMPARISON = {"canonical": "job plus result",
              "excluded_result_root_fields": sorted(TIMING_EXCLUSIONS),
              "code_hash": "retained; envelope and result code_hash must equal the producing identity"}
EXTENSION_KINDS = {"a13_validate_plain_ext": ("validation_extension_a13", "a13_checkpoints", 4, "ext_seed"),
                   "a14_validate_plain_ext2": ("validation_extension_a14", "a14_checkpoints", 20, "ext2_seed")}


class RequalificationError(RuntimeError):
    pass


def require(condition, message):
    if not condition:
        raise RequalificationError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False).encode("utf-8")


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def file_sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def comparison_bytes(job, result):
    """Canonical job-plus-result bytes with only the named timing fields removed,
    normalized through the JSON domain the durable records use."""
    clean = {k: v for k, v in result.items() if k not in TIMING_EXCLUSIONS}
    return canonical(json.loads(canonical({"job": job, "result": clean})))


def load_checkout(checkout):
    """Import the checkout's own ``v3`` package. Refuses a checkout without one,
    and refuses to mix with a ``v3`` already imported from elsewhere."""
    simulation = (Path(checkout) / "simulation").resolve()
    require((simulation / "v3" / "artifacts.py").is_file(), "checkout has no simulation/v3 package: " + str(simulation))
    loaded = sys.modules.get("v3")
    if loaded is not None:
        require(Path(loaded.__file__).resolve().parent.parent == simulation,
                "a different v3 package is already imported; run the worker in its own interpreter")
    else:
        sys.path.insert(0, str(simulation))
    import v3.artifacts as artifacts
    require(Path(artifacts.__file__).resolve().parent.parent == simulation, "v3 was imported from outside the checkout")
    return artifacts


def _boot_id():
    """The boot identity: Linux's boot_id, else the last boot time Windows reports."""
    for path in ("/proc/sys/kernel/random/boot_id",):
        try:
            return Path(path).read_text().strip()
        except OSError:
            pass
    if os.name == "nt":
        try:
            import ctypes
            import datetime
            ticks = ctypes.windll.kernel32.GetTickCount64()
            boot = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(milliseconds=int(ticks))
            # Rounded to the minute, so successive launches within a boot agree.
            return boot.replace(second=0, microsecond=0).isoformat()
        except Exception:  # noqa: BLE001
            return None
    return None


SYSTEM_LIBRARY_NAMES = ("libc.so", "libc-", "libm.so", "libm-", "libgcc_s", "libstdc++", "libgomp", "libopenblas", "libpthread")


def _numerical_libraries():
    """The versions of the numerical libraries the producers import, the hashes
    of the shared libraries numpy and scipy bundle, and, where /proc/self/maps
    exists, the hashes of the system libraries this interpreter has mapped
    after importing numpy (libc, libm, libgcc, libstdc++, libgomp, OpenBLAS)."""
    import importlib
    import importlib.util
    versions, hashes = {}, {}
    for name in ("numpy", "scipy"):
        if importlib.util.find_spec(name) is None:
            versions[name] = None
            continue
        module = importlib.import_module(name)
        versions[name] = getattr(module, "__version__", None)
        libs = Path(module.__file__).resolve().parent.parent / (name + ".libs")
        if libs.is_dir():
            for library in sorted(libs.iterdir()):
                if library.is_file():
                    hashes[library.name] = file_sha256(library)
    maps = Path("/proc/self/maps")
    if maps.is_file():
        mapped = set()
        for line in maps.read_text().splitlines():
            parts = line.split(None, 5)
            if len(parts) == 6 and parts[5].startswith("/"):
                mapped.add(parts[5])
        for path in sorted(mapped):
            name = Path(path).name
            if any(name.startswith(prefix) for prefix in SYSTEM_LIBRARY_NAMES) and Path(path).is_file():
                hashes[path] = file_sha256(path)
    return versions, hashes


def _packages_sha256():
    """The hash of the installed package list, the equivalent of pip freeze."""
    import importlib.metadata
    rows = sorted({"%s==%s" % (d.metadata["Name"], d.version) for d in importlib.metadata.distributions()
                   if d.metadata and d.metadata.get("Name")})
    return hashlib.sha256("\n".join(rows).encode("utf-8")).hexdigest(), len(rows)


def host_fingerprint():
    """The environment fingerprint of this interpreter and host, recorded by
    every worker and by the replaying attempt itself: interpreter, platform,
    kernel and boot identity, numerical library versions and library hashes,
    and the installed package list's hash. Any difference between an attempt
    and a record it would reuse invalidates the reuse."""
    import multiprocessing
    import platform
    uname = platform.uname()
    versions, library_hashes = _numerical_libraries()
    packages_sha256, package_count = _packages_sha256()
    return {"python": platform.python_version(), "python_executable": sys.executable, "platform": platform.platform(),
            "uname": {"system": uname.system, "node": uname.node, "release": uname.release, "version": uname.version,
                      "machine": uname.machine},
            "boot_id": _boot_id(), "numpy": versions.get("numpy"), "scipy": versions.get("scipy"),
            "numerical_libraries": library_hashes, "packages_sha256": packages_sha256, "package_count": package_count,
            "multiprocessing_start_method": multiprocessing.get_start_method(allow_none=True),
            "int_max_str_digits": sys.get_int_max_str_digits()}


def mem_total_bytes():
    try:
        if Path("/proc/meminfo").is_file():
            for line in Path("/proc/meminfo").read_text().splitlines():
                if line.startswith("MemTotal:"):
                    return int(line.split()[1]) * 1024
        if os.name == "nt":
            return _windows_memory()[0]
    except Exception:  # noqa: BLE001
        return None
    return None


def mem_available_bytes():
    """MemAvailable, read before each dispatch; None when it cannot be read."""
    try:
        if Path("/proc/meminfo").is_file():
            for line in Path("/proc/meminfo").read_text().splitlines():
                if line.startswith("MemAvailable:"):
                    return int(line.split()[1]) * 1024
        if os.name == "nt":
            return _windows_memory()[1]
    except Exception:  # noqa: BLE001
        return None
    return None


def _windows_memory():
    import ctypes

    class Status(ctypes.Structure):
        _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong), ("ullTotalPhys", ctypes.c_ulonglong),
                    ("ullAvailPhys", ctypes.c_ulonglong), ("ullTotalPageFile", ctypes.c_ulonglong),
                    ("ullAvailPageFile", ctypes.c_ulonglong), ("ullTotalVirtual", ctypes.c_ulonglong),
                    ("ullAvailVirtual", ctypes.c_ulonglong), ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
    status = Status()
    status.dwLength = ctypes.sizeof(Status)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
        raise OSError("GlobalMemoryStatusEx failed")
    return int(status.ullTotalPhys), int(status.ullAvailPhys)


def environment(artifacts):
    """Runtime facts for the acceptance record: the host fingerprint (shared with
    the replaying attempt) plus the checkout's full source manifest and identity.
    OS package provenance beyond the package list, memory and service state are
    captured by the runbook outside the worker."""
    return dict(host_fingerprint(), source_manifest=artifacts.source_manifest(), code_identity=artifacts.code_identity(),
                python_flags=repr(sys.flags), cwd=os.getcwd())


def _view(item, artifacts, scratch):
    """The read-only input view: every declared input is hash-verified against
    its source and mapped from the path the producer resolves to that source.
    Reads under a protected root that are not declared fail closed inside the
    producer's own ``input_path``."""
    simulation = Path(artifacts.SIMULATION).resolve()
    paths, protected = {}, set(str(Path(p).resolve()) for p in item.get("protected", []))
    for row in item.get("inputs", []):
        source = Path(row["source"]).resolve()
        require(source.is_file(), "missing requalification input: " + str(source))
        require(file_sha256(source) == row["sha256"], "requalification input changed: " + str(source))
        if "relative_to_simulation" in row:
            target = simulation / row["relative_to_simulation"]
        elif "relative_to_scratch" in row:
            target = Path(scratch) / row["relative_to_scratch"]
        else:
            target = Path(row["path"])
        for key in (str(target.resolve()), str(source)):
            require(paths.get(key, str(source)) == str(source), "ambiguous requalification input alias: " + key)
            paths[key] = str(source)
        protected.add(str(target.resolve().parent))
    protected.add(str((simulation / "v3" / "runs").resolve()))
    return {"paths": paths, "protected": sorted(protected)}


def _replay_extension(item, job, archived, artifacts):
    """Re-simulate every recorded extension replicate from its recorded seed with
    the producer's unchanged ``extension_stage``, rebuild the result envelope from
    the fresh replicates, and compare each fresh checkpoint document with the
    archived one. Archived checkpoints are read for comparison only."""
    import importlib
    module_name, directory, first, seed_name = EXTENSION_KINDS[job["kind"]]
    module = importlib.import_module("v3." + module_name)
    a13 = importlib.import_module("v3.validation_extension_a13")
    c = job["config"]
    binding = item.get("plan_binding")
    if job["kind"] == "a14_validate_plain_ext2":
        # The A14 reference binding: the job is one of the bound original jobs,
        # at the bound plan hash (REQUALIFICATION_PLAN.md section 4).
        require(isinstance(binding, dict), "A14 replay requires the frozen plan binding")
        require(job["id"] in binding["job_ids"] and c["plan_hash"] == binding["plan_hash"],
                "A14 job is outside the bound original jobs or plan")
    recorded = archived["result"]["replicates"]
    module.validate_replicates(job, recorded)
    seed_fn = module.rehearsal_seed if c.get("non_registered_rehearsal") else getattr(module, seed_name)
    require(c["stream_seeds"] == [seed_fn(c["a1_job"]["seed"], r) for r in range(first, first + c["R_max"])],
            "recorded extension seeds differ from the registered derivation")
    require([r["seed"] for r in recorded] == c["stream_seeds"][:len(recorded)], "recorded replicate seeds out of order")
    a1 = a13.a4._load_a1(c["a1_source_root"], c["a1_job"], c["a1_source_code_hash"])
    fit = artifacts.unseal(c["fit"])
    require(fit["a1_job_id"] == c["a1_job"]["id"], "extension fit source mismatch")
    fresh = []
    for replica in recorded:
        value = module.extension_stage(a1, fit, c["eligible_rows"], replica["seed"], c.get("settings_override"))
        value.update(replicate=replica["replicate"], seed=replica["seed"])
        fresh.append(value)
    # The registered stop, recomputed from the fresh data: no replicate after
    # the stop, and the run either stopped or exhausted R_max.
    for index in range(1, len(fresh)):
        require(not module.stop_reached(fresh[:index], c["eligible_rows"]), "fresh replicates continue past the registered stop")
    stopped = bool(fresh and module.stop_reached(fresh, c["eligible_rows"]))
    require(stopped or len(fresh) == c["R_max"], "recorded extension neither stopped nor exhausted R_max")
    result = {"stage": module.PHASE, "plan_hash": c["plan_hash"], "a1_job_id": c["a1_job"]["id"],
              "code_hash": artifacts.code_identity(), "replicates": fresh, "stopped_on_visits": stopped}
    checkpoints = []
    checkpoint_root = Path(item["phase_root"]) / directory / job["id"]
    archived_files = [r for r in item.get("inputs", [])
                      if "path" in r and Path(r["path"]).parent == checkpoint_root.resolve()]
    require(len(archived_files) == len(recorded), "archived checkpoint count differs from the recorded replicates")
    for value in fresh:
        path = checkpoint_root / f"{value['replicate']:02d}.json"
        expected = canonical(artifacts.seal({"job_sha256": artifacts.digest(job), "replicate": value}))
        archived_bytes = canonical(artifacts.read(path)) if Path(artifacts.input_path(path)).is_file() else None
        checkpoints.append({"replicate": value["replicate"], "path": str(path),
                            "fresh_sha256": hashlib.sha256(expected).hexdigest(),
                            "archived_sha256": hashlib.sha256(archived_bytes).hexdigest() if archived_bytes is not None else None,
                            "passed": archived_bytes == expected})
    return result, checkpoints


# Why each kind does or does not need the registration as authority. Only the
# run kind reaches the succession gate: V3Model builds ExecutionGuards with the
# registration as authority, and authorize("succession", ...) refuses every
# succession on production tables without it (guards.py, integration.py). The
# table estimator, the A4 fit, validate and census stages, the A5 label stage and
# the extension stages simulate trajectories without that gate and take no
# registration; the registered flag only adds validation there.
AUTHORITY_REASONS = {
    "rerun": "the succession gate needs the registration as authority on production tables",
    "table": "offline_estimator.estimate takes no authority; no succession gate",
    "a4_fit": "table_validation_a4.run_stage_job takes no authority; no succession gate",
    "a4_validate": "table_validation_a4.run_stage_job takes no authority; no succession gate",
    "a4_census": "table_validation_a4.run_stage_job takes no authority; no succession gate",
    "a5_fvplain": "table_labels_a5.run_stage_job takes no authority; no succession gate",
    "fixture": "runner fixture; no authority",
}


def authority_for(item):
    """The registered flag and registration pin a replayed item executes with.
    A run job from a registered spec replays registered, with the frozen
    source record's registration pin (verified historically at freeze) as its
    authority, so the producer's succession gate behaves as it did in the
    archived execution; it is refused without that pin. Every other kind
    replays non-registered: none of them reaches the succession gate."""
    kind = item["job"]["kind"]
    if kind != "rerun":
        return False, None
    registration = item.get("registration")
    if not item.get("registered"):
        require(registration is None, "a non-registered run item carries a registration pin")
        return False, None
    require(isinstance(registration, dict) and set(registration) == {"commit", "path", "sha256"},
            "a registered run item needs the frozen source record's registration pin as its authority")
    return True, dict(registration)


def replay_item(item, *, scratch, keep_scratch=False):
    """Replay one frozen item and return its comparison record. Writes only under
    ``scratch`` (which must be empty, inside the checkout's simulation/v3)."""
    started = time.perf_counter()
    artifacts = load_checkout(item["checkout"])
    code = item["producing_code_hash"]
    identity = artifacts.code_identity()
    require(identity == code, "checkout identity %s differs from the producing identity %s" % (identity[:12], code[:12]))
    artifacts.configure_threads(1)
    info = artifacts.runtime(1)
    info = dict(info, **environment(artifacts))
    from v3.production_runner import completed, execute
    try:
        from v3.production_runner import peak_rss_bytes
    except ImportError:
        peak_rss_bytes = lambda: None
    job, kind = item["job"], item["job"]["kind"]
    phase_root = Path(item["phase_root"])
    scratch = Path(scratch)
    root = Path(artifacts.ROOT).resolve()
    require(scratch.is_absolute() and str(scratch).startswith(str(root) + os.sep), "scratch must lie inside the checkout's simulation/v3")
    # Created before it is resolved: resolving a path that does not exist yet
    # is not reliable on every platform while sibling workers add and remove
    # their own scratch directories.
    scratch.mkdir(parents=True, exist_ok=True)
    require(scratch.resolve().is_relative_to(root), "scratch must lie inside the checkout's simulation/v3")
    require(not any(scratch.iterdir()), "requalification scratch is not empty: " + str(scratch))
    view = _view(item, artifacts, scratch)
    record = {"item_id": item["item_id"], "job_id": job["id"], "kind": kind, "producing_code_hash": code,
              "checkout": str(Path(item["checkout"]).resolve()), "scratch": str(scratch), "runtime": info,
              "comparison": COMPARISON, "passed": False}
    context = artifacts.input_view(view) if hasattr(artifacts, "input_view") else contextlib.nullcontext()
    if not hasattr(artifacts, "input_view"):
        require(not view["paths"], "this identity has no input view; declared inputs cannot be mapped")
    with context:
        archived = completed(phase_root, job, code)
        require(archived is not None, "missing durable completion record for " + job["id"])
        require(archived.get("code_hash") == code and archived["result"].get("code_hash", code) == code,
                "archived output carries another producer identity")
        output_path = phase_root / "outputs" / (job["id"] + ".json")
        record["archived_output_sha256"] = artifacts.file_hash(output_path)
        require(record["archived_output_sha256"] == item["archived_output_sha256"], "archived output differs from the frozen sample")
        record["before_sha256"] = hashlib.sha256(comparison_bytes(job, archived["result"])).hexdigest()
        execution_start = time.perf_counter()
        if kind in EXTENSION_KINDS:
            fresh, checkpoints = _replay_extension(item, job, archived, artifacts)
            record["checkpoints"] = checkpoints
        else:
            phase_dir = scratch / job["config"].get("phase", kind)
            registered, registration = authority_for(item)
            record["authority"] = {"registered": registered, "registration": registration,
                                   "reason": AUTHORITY_REASONS.get(kind, "no succession gate on this kind")}
            fresh = execute(job, registered=registered, registration=registration, root=phase_dir)
        record["worker_seconds"] = time.perf_counter() - execution_start
        require(fresh.get("code_hash", code) == code, "fresh result carries another producer identity")
        record["after_sha256"] = hashlib.sha256(comparison_bytes(job, fresh)).hexdigest()
    record["peak_rss_bytes"] = peak_rss_bytes()
    record["passed"] = (record["before_sha256"] == record["after_sha256"]
                        and all(c["passed"] for c in record.get("checkpoints", [])))
    record["total_seconds"] = time.perf_counter() - started
    if record["passed"] and not keep_scratch:
        shutil.rmtree(scratch, ignore_errors=True)
    return record


def _historical_equivalent(pin, repo, instrument, artifacts):
    """The checks the producer's historical mode consists of (ancestry, the
    committed note's bytes, the A10 and A11 markers), for a producer whose
    ``verify_registration`` predates the ``historical`` keyword. Its strict mode
    is never used as a fallback: that also binds the working note and a clean
    tree, which is a different claim."""
    import subprocess
    require(isinstance(pin, dict) and set(pin) == {"commit", "path", "sha256"}, "malformed registration pin")
    path = Path(pin["path"])
    require(not path.is_absolute() and ".." not in path.parts and bool(pin["commit"]), "invalid pre-registration pin")
    def git(*args):
        return subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True).stdout
    git("merge-base", "--is-ancestor", pin["commit"], "HEAD")
    committed = git("show", "%s:%s" % (pin["commit"], path.as_posix()))
    from v3.instrument import declaration
    if declaration(instrument).a10:
        require(b"Amendment A10" in committed and b"Amendment A11" in committed,
                "registered A10 requires a design pin containing Amendments A10 and A11")
    require(hashlib.sha256(committed).hexdigest() == pin["sha256"], "pre-registration hash is stale")
    return dict(pin)


def verify_pin(checkout, spec_path):
    """Verify a sealed spec's original registration pin with the checkout's own
    ``verify_registration`` in historical mode (ancestry and committed bytes,
    never the working note). A producer whose function has no ``historical``
    keyword (identities before 2026-10-17) gets the equivalent checks performed
    here against its checkout, and the record says so. Returns the record the
    harness freezes."""
    import inspect
    artifacts = load_checkout(checkout)
    document = json.loads(Path(spec_path).read_text(encoding="utf-8"))
    spec = artifacts.unseal(document)
    pin = spec.get("registration")
    require(isinstance(pin, dict), "spec has no registration pin")
    instrument = spec.get("instrument")
    repo = Path(checkout).resolve()
    if "historical" in inspect.signature(artifacts.verify_registration).parameters:
        verified = artifacts.verify_registration(pin, repo, instrument=instrument, historical=True)
        mode = "historical"
    else:
        verified = _historical_equivalent(pin, repo, instrument, artifacts)
        mode = "historical-equivalent; producer has no historical mode"
    require(verified == pin, "verify_registration returned a different pin")
    return {"verified": True, "pin": pin, "mode": mode, "instrument": instrument,
            "code_identity": artifacts.code_identity(), "checkout": str(repo)}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkout", required=True)
    parser.add_argument("--item")
    parser.add_argument("--scratch")
    parser.add_argument("--result", required=True)
    parser.add_argument("--keep-scratch", action="store_true")
    parser.add_argument("--verify-pin", help="verify this sealed spec's registration pin instead of replaying an item")
    args = parser.parse_args(argv)
    sys.set_int_max_str_digits(0)
    if args.verify_pin:
        try:
            record = verify_pin(args.checkout, args.verify_pin)
        except BaseException as exc:
            record = {"verified": False, "error": type(exc).__name__ + ": " + str(exc)}
        Path(args.result).write_bytes(canonical(record) + b"\n")
        return 0 if record.get("verified") else 1
    require(args.item and args.scratch, "--item and --scratch are required to replay an item")
    item = json.loads(Path(args.item).read_text(encoding="utf-8"))
    try:
        record = replay_item(item, scratch=args.scratch, keep_scratch=args.keep_scratch)
    except BaseException as exc:
        record = {"item_id": item.get("item_id"), "job_id": item.get("job", {}).get("id"), "passed": False,
                  "error": type(exc).__name__ + ": " + str(exc)}
    Path(args.result).write_bytes(canonical(record) + b"\n")
    return 0 if record.get("passed") else 1


if __name__ == "__main__":
    raise SystemExit(main())
