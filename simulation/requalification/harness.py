"""Requalification orchestrator: freeze the sample, replay it, record acceptance.

Two commands, mirroring REQUALIFICATION_PLAN.md sections 2 to 6::

    python -m requalification.harness freeze --sources sources.json --output sample.json
    python -m requalification.harness replay --sample sample.json --output-dir <dir> [--workers N]

``sources.json`` lists completed launches, one per producing identity and run
root::

    [{"name": "main", "group": "runs", "selection": "a15",
      "producing_code_hash": "<64 hex>", "checkout": "<scratch source view root>",
      "original_simulation": "<the original execution checkout's simulation/ directory>",
      "spec": "<sealed spec path>", "root": "<run root>"}, ...]

``selection`` is ``a11`` (two smallest ``digest(["A11-compatibility", phase,
job_id])`` per phase, capability and setting), ``a15`` (two smallest tagged
hashes per stratum under ``A15-OS-requalification-2026-10-29``, the stratum
carrying the component, grid, alpha, successor capability, weights, horizon,
instrument and variant, or the capability and replicate for labels) or ``all``.
Selection reads configuration and identity metadata only, never an outcome.

Every registered source's original registration pin is verified at freeze with
the producer's own ``verify_registration`` in historical mode, in the
producer's checkout, and the result is frozen into the sample. An A14 source is
bound to its original jobs, plan hash and seed manifest hash, supplied as
frozen inputs; any other job set is refused.

The frozen sample is sealed and written once. Replay runs every item in its own
interpreter with ``requalification.worker`` at the item's checkout, one
producer checkout at a time in the sample's order with a barrier between them,
under a worker cap and memory admission, stops dispatching new items at the
first mismatch, error or non-zero worker exit, never overwrites a per-item
result, and writes a sealed acceptance record carrying the attempt's
environment fingerprint. Nothing here reads a scientific value, and nothing
writes outside the output directory, the sample file and each item's scratch.
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from .worker import (COMPARISON, TIMING_EXCLUSIONS, RequalificationError, canonical, digest, file_sha256,
                     host_fingerprint, mem_available_bytes, mem_total_bytes, require)

SAMPLE_SCHEMA = "v3-requalification-sample-1"
ACCEPTANCE_SCHEMA = "v3-requalification-acceptance-1"
A15_TAG = "A15-OS-requalification-2026-10-29"
A11_TAG = "A11-compatibility"
SELECTIONS = ("a11", "a15", "all")
HERE = Path(__file__).resolve().parent
WORKER_HARD_CAP = 31
# Memory reservations in GB, keyed by job kind, route and setting, from the
# initial reservation budget estimates of STAGE2_PLAN_v2.md section 5 (twice the
# registered estimate for an unmeasured class; FV and plain validation differ).
# ``reservation_bytes`` looks up ``kind.route.setting``, then ``kind.setting``,
# then ``kind``. ``replay`` takes an overriding mapping; an unmatched kind is refused.
DEFAULT_RESERVATIONS_GB = {"table.primary": 2.8265625, "table.double_population": 5.653125, "table.double_length": 5.653125,
                           "a4_fit.primary": 3.35, "a4_fit.double_population": 6.7, "a4_fit.double_length": 6.7,
                           "a4_validate.plain.primary": 3.35, "a4_validate.plain.double_population": 6.7,
                           "a4_validate.plain.double_length": 6.7, "a4_validate.fv.primary": 13.4,
                           "a4_validate.fv.double_population": 26.8, "a4_validate.fv.double_length": 26.8,
                           "a4_validate": 26.8, "a4_census": 0.520063, "rerun": 4.0, "a5_fvplain": 4.56,
                           "a13_validate_plain_ext": 8.0, "a14_validate_plain_ext2": 8.0, "fixture": 0.1}
GB = 1024 ** 3


def harness_hashes():
    return {name: file_sha256(HERE / name) for name in ("__init__.py", "harness.py", "worker.py")}


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_once(path, document):
    """Write a sealed document once; identical bytes may be rewritten."""
    path = Path(path)
    data = canonical(document) + b"\n"
    if path.exists():
        require(path.read_bytes() == data, "frozen requalification record differs: " + str(path))
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    partial = path.with_name(path.name + f".{os.getpid()}.partial")
    partial.write_bytes(data)
    os.replace(partial, path)
    return path


def seal(payload):
    return {"payload": payload, "sha256": digest(payload)}


def unseal(document):
    require(set(document) == {"payload", "sha256"} and digest(document["payload"]) == document["sha256"],
            "requalification document hash mismatch")
    return document["payload"]


# ---------------------------------------------------------------------------
# Strata and selection
# ---------------------------------------------------------------------------

def a11_stratum(job):
    """compatibility_a10._stratum, restated: (phase, capability, setting)."""
    cfg = job["config"]
    phase = cfg.get("phase", job["kind"])
    source = cfg.get("a1_job", {}).get("config", cfg)
    kernel = source.get("kernel", source.get("model", {}))
    capability = kernel.get("capability", kernel.get("successor_capability", 1.))
    return [phase, capability, source.get("setting_name", "run")]


def a15_stratum(name, job):
    """The requalification stratum for run and label jobs: the component name and
    every identity axis the plan names, so separate arms and corners never merge."""
    cfg = job["config"]
    if job["kind"] == "a5_fvplain":
        source = cfg["a1_job"]["config"]
        return [name, "labels", source["kernel"].get("capability"), cfg.get("replicate")]
    model = cfg.get("model", {})
    return [name, cfg.get("category", cfg.get("phase", job["kind"])), cfg.get("a6_grid", cfg.get("grid")),
            model.get("alpha"), model.get("successor_capability"), model.get("kappa"), model.get("theta"),
            cfg.get("steps"), cfg.get("a6_variant"), model.get("instrument"), model.get("crowding")]


def select(name, selection, jobs):
    """Deterministic selection by identity metadata only. Returns the chosen
    jobs and the strata with their population and chosen identifiers."""
    require(selection in SELECTIONS, "unknown selection rule " + repr(selection))
    strata = {}
    for job in jobs:
        key = a11_stratum(job) if selection == "a11" else (a15_stratum(name, job) if selection == "a15" else ["all"])
        strata.setdefault(canonical(key).decode("ascii"), {"stratum": key, "job_ids": []})["job_ids"].append(job["id"])
    chosen = []
    for key in sorted(strata):
        entry = strata[key]
        ids = entry["job_ids"]
        require(len(ids) == len(set(ids)), "duplicate job within a stratum")
        if selection == "all":
            picked = sorted(ids)
        elif selection == "a11":
            picked = sorted(ids, key=lambda jid: (digest([A11_TAG, entry["stratum"][0], jid]), jid))[:2]
        else:
            picked = sorted(ids, key=lambda jid: (digest([A15_TAG, entry["stratum"], jid]), jid))[:2]
        entry["selected"] = picked
        entry["population"] = len(ids)
        entry["job_ids"] = sorted(ids)
        chosen.extend(picked)
    require(len(chosen) == len(set(chosen)), "job selected in two strata")
    return chosen, [strata[k] for k in sorted(strata)]


# ---------------------------------------------------------------------------
# Inputs each job reads, mapped to the archived originals
# ---------------------------------------------------------------------------

def _row(target, source, *, relative_to_simulation=None, relative_to_scratch=None):
    source = Path(source)
    require(source.is_file(), "missing archived input: " + str(source))
    row = {"source": str(source.resolve()), "sha256": file_sha256(source), "bytes": source.stat().st_size}
    if relative_to_simulation is not None:
        row["relative_to_simulation"] = relative_to_simulation
    elif relative_to_scratch is not None:
        row["relative_to_scratch"] = relative_to_scratch
    else:
        row["path"] = str(Path(target).resolve())
    return row


def job_inputs(job, phase_root, original_simulation):
    """Every file the producer's ``execute`` reads for this job, following the
    enumeration of ``snapshot_a11.dependencies``, with relative paths resolved
    against the original execution checkout's ``simulation/`` directory and the
    plain-validation fit sibling mapped into the scratch root."""
    c = job["config"]
    original = Path(original_simulation).resolve()
    rows = []
    def relative(path):
        rows.append(_row(None, original / path, relative_to_simulation=path))
    if job["kind"] == "a14_validate_plain_ext2":
        # A14 jobs declare their inputs as hash-verified copies; map every copy
        # under its source path and every alias, as execution_inputs does, and
        # add the files the physical extension stage reads (the A1 record and
        # output, and the calibration TableTrace reads) through those copies.
        copies = {}
        for r in c.get("a14_inputs", []):
            copy = Path(r["copy"])
            require(copy.is_file() and file_sha256(copy) == r["sha256"] and copy.stat().st_size == r["bytes"],
                    "declared A14 input copy changed: " + str(copy))
            for alias in [r["source"], *r.get("aliases", [])]:
                copies[str(Path(alias).resolve())] = r["copy"]
            rows.append(_row(r["source"], r["copy"]))
        source = Path(c["a1_source_root"])
        for directory in ("outputs", "records"):
            path = source / "tables_A1/table" / directory / (c["a1_job"]["id"] + ".json")
            if str(path.resolve()) not in copies:
                rows.append(_row(path, path))
        for path in (c["a1_job"]["config"].get("calibration_path"), "v3/runs/registered/v3_rerun_calibration.json"):
            if path:
                target = original / path
                rows.append(_row(None, copies.get(str(target.resolve()), target), relative_to_simulation=path))
        return rows
    if c.get("calibration_path"):
        relative(c["calibration_path"])
        if c["calibration_path"] != "v3/runs/registered/v3_rerun_calibration.json":
            relative("v3/runs/registered/v3_rerun_calibration.json")
    if c.get("tables_path"):
        relative(c["tables_path"])
        table = Path(c["tables_path"])
        for suffix in (".a10_receipt.json", ".compatibility.json", ".cell_results.json"):
            sibling = table.with_suffix(suffix).as_posix()
            if (original / sibling).is_file():
                relative(sibling)
    if job["kind"] in ("a4_fit", "a4_validate", "a4_census", "a5_fvplain", "a13_validate_plain_ext"):
        source = Path(c["a1_source_root"])
        a1 = c["a1_job"]
        if a1["config"].get("calibration_path"):
            relative(a1["config"]["calibration_path"])
            if a1["config"]["calibration_path"] != "v3/runs/registered/v3_rerun_calibration.json":
                relative("v3/runs/registered/v3_rerun_calibration.json")
        for name in ("tables_A1_manifest.json", "v3_rerun_tables_A1.json"):
            if (source / name).is_file():
                rows.append(_row(source / name, source / name))
        for directory in ("outputs", "records"):
            path = source / "tables_A1/table" / directory / (a1["id"] + ".json")
            rows.append(_row(path, path))
        if job["kind"] == "a4_validate" and c.get("route") == "plain" and not c.get("self_contained"):
            fit_id = _fit_job_id(c)
            fit_output = Path(phase_root).parent / "fit" / "outputs" / (fit_id + ".json")
            rows.append(_row(None, fit_output, relative_to_scratch="fit/outputs/" + fit_id + ".json"))
    return rows


def _fit_job_id(c):
    """table_validation_a4._fit_job_id, restated with stable_job's rule so the
    harness does not import simulation code."""
    fit_cfg = {"a1_source_root": c["a1_source_root"], "a1_job": c["a1_job"],
               "a1_source_code_hash": c["a1_source_code_hash"], "stage": "fit", "route": "plain",
               "seed": _stream_seed("v3_R_fit", c["a1_job"]["seed"], 0), "plan_hash": c["plan_hash"]}
    if "settings_override" in c:
        fit_cfg["settings_override"] = c["settings_override"]
    config = {**fit_cfg, "phase": "fit"}
    key = digest({"kind": "a4_fit", "config": config, "tag": "v3_tables", "index": 0})
    return "a4_fit_" + key[:24]


def _stream_seed(tag, a1_job_seed, replicate):
    m = hashlib.sha256()
    for part in (tag, a1_job_seed, replicate):
        m.update(str(part).encode("utf-8"))
    return int(m.hexdigest()[:15], 16)


def archived_inputs(job, phase_root):
    """The archived record, output and extension checkpoints map to themselves,
    so the worker can read them under the protected original root."""
    phase_root = Path(phase_root)
    rows = []
    for directory in ("records", "outputs"):
        path = phase_root / directory / (job["id"] + ".json")
        rows.append(_row(path, path))
    directory = {"a13_validate_plain_ext": "a13_checkpoints", "a14_validate_plain_ext2": "a14_checkpoints"}.get(job["kind"])
    if directory:
        for path in sorted((phase_root / directory / job["id"]).glob("*.json")):
            rows.append(_row(path, path))
    return rows


# ---------------------------------------------------------------------------
# Freeze
# ---------------------------------------------------------------------------

def _hash_ok(value):
    return isinstance(value, str) and len(value) == 64 and all(ch in "0123456789abcdef" for ch in value)


def _worker_command(checkout, python=None):
    # The workers and the attempt share one interpreter, so the fingerprint the
    # attempt captures is the one the workers record.
    if python is not None:
        require(Path(python).resolve() == Path(sys.executable).resolve(),
                "workers must run the attempt's own interpreter %s" % sys.executable)
    return [sys.executable, "-B", "-E", str(HERE / "worker.py"), "--checkout", str(checkout)]


def verify_source_pin(spec, spec_path, checkout, scratch_dir, *, python=None):
    """Verify a registered spec's original registration pin with the producer's
    own ``verify_registration`` in historical mode, inside the producer's
    checkout, and return the frozen record of what was verified. A spec without
    a registration pin is recorded as non-registered."""
    pin = spec.get("registration")
    if not spec.get("registered") and not pin:
        return {"registered": False, "pin": None, "verified": False,
                "note": "non-registered spec; no registration pin to verify"}
    require(isinstance(pin, dict), "registered spec without a registration pin: " + str(spec_path))
    scratch_dir = Path(scratch_dir)
    scratch_dir.mkdir(parents=True, exist_ok=True)
    result_path = scratch_dir / ("pin_" + digest([str(spec_path), pin])[:16] + ".json")
    command = _worker_command(checkout, python) + ["--verify-pin", str(spec_path), "--result", str(result_path)]
    completed = subprocess.run(command, capture_output=True, text=True, cwd=str(Path(checkout) / "simulation"))
    result = read_json(result_path) if result_path.is_file() else {"verified": False, "error": "worker wrote no result"}
    require(completed.returncode == 0 and result.get("verified") is True and result.get("pin") == pin,
            "original registration pin could not be verified for %s: %s" % (spec_path, result.get("error") or completed.stderr[-2000:]))
    return {"registered": True, "pin": pin, "verified": True, "mode": result.get("mode"),
            "verifier_code_identity": result.get("code_identity"), "checkout": str(Path(checkout).resolve())}


def a14_binding(source, spec):
    """Bind an A14 source to the original jobs, plan hash and seed manifest hash
    the operator supplies as frozen inputs. Any other job set is refused."""
    binding = source.get("a14_binding")
    require(isinstance(binding, dict) and {"job_ids", "plan_hash", "seed_manifest_sha256"} <= set(binding),
            "an A14 source needs a14_binding with job_ids, plan_hash and seed_manifest_sha256")
    job_ids = sorted(binding["job_ids"])
    # The registered A14 round had four source jobs; a different count can only
    # describe a non-registered fixture plan.
    job_count = binding.get("job_count", 4)
    require(job_count == 4 or not spec.get("registered"), "a registered A14 source binds exactly four original jobs")
    require(job_ids and len(job_ids) == len(set(job_ids)) == job_count,
            "A14 binding must list exactly its %d original jobs" % job_count)
    require(sorted(j["id"] for j in spec["jobs"]) == job_ids, "A14 spec job set differs from the bound original jobs")
    require(spec.get("plan_hash") == binding["plan_hash"], "A14 spec plan hash differs from the bound plan hash")
    require(digest(spec.get("seed_manifest")) == binding["seed_manifest_sha256"],
            "A14 spec seed manifest differs from the bound seed manifest hash")
    require(all(j["config"].get("plan_hash") == binding["plan_hash"] for j in spec["jobs"]),
            "A14 job carries another plan hash")
    return {"job_ids": job_ids, "plan_hash": binding["plan_hash"], "seed_manifest_sha256": binding["seed_manifest_sha256"]}


def freeze_sample(sources, output, *, require_complete=True, python=None):
    """Freeze the complete selection before any execution. Every source's spec,
    root identity, manifest, launch completion and original pin are checked;
    every selected job's durable record and output must exist and are hashed
    into the sample."""
    output = Path(output).resolve()
    items, frozen_sources = [], []
    for source in sources:
        name, group = source["name"], source["group"]
        code, checkout = source["producing_code_hash"], Path(source["checkout"]).resolve()
        require(_hash_ok(code), "producing_code_hash must be a 64-character hash")
        require((checkout / "simulation" / "v3" / "artifacts.py").is_file(), "checkout has no simulation/v3: " + str(checkout))
        spec_path, root = Path(source["spec"]).resolve(), Path(source["root"]).resolve()
        spec = unseal(read_json(spec_path))
        require(spec["code_hash"] == code, "spec %s is not the producing identity" % spec_path)
        identity = read_json(root / "identity.json")
        require(identity == {"code_hash": code, "spec_hash": digest(spec)}, "source root identity mismatch: " + str(root))
        require(unseal(read_json(root / "manifest.json")) == spec, "source root manifest mismatch: " + str(root))
        launches = read_json(root / "launches.json")
        require(not require_complete or (launches and launches[-1].get("complete") is True),
                "requalification needs a completed launch: " + str(root))
        original = Path(source["original_simulation"]).resolve()
        require(original.is_dir(), "original simulation directory missing: " + str(original))
        pin_record = verify_source_pin(spec, spec_path, checkout, output.parent / (output.stem + "_pins"), python=python)
        binding = None
        if group == "a14" or any(j["kind"] == "a14_validate_plain_ext2" for j in spec["jobs"]):
            binding = a14_binding(source, spec)
            require(source["selection"] == "all", "an A14 source replays every bound job")
        chosen, strata = select(name, source["selection"], spec["jobs"])
        if source.get("expected_job_ids") is not None:
            # The archived A11 selection (or any frozen list) must be reproduced
            # exactly; a difference is a finding, never a substitution.
            require(sorted(chosen) == sorted(source["expected_job_ids"]),
                    "selection differs from the expected job list for " + name)
        by_id = {j["id"]: j for j in spec["jobs"]}
        # Protected roots: the run root, the original checkout's run data and
        # every A1 source root the selected jobs name. Any read under them that
        # the item does not declare fails closed in the producer's input_path.
        protected = {str(root), str(original / "v3" / "runs")} | {str(Path(p).resolve()) for p in source.get("protected", [])}
        for jid in chosen:
            a1_root = by_id[jid]["config"].get("a1_source_root")
            if a1_root:
                protected.add(str(Path(a1_root).resolve()))
        protected = sorted(protected)
        for jid in chosen:
            job = by_id[jid]
            phase_root = root / job["config"].get("phase", job["kind"])
            record = read_json(phase_root / "records" / (jid + ".json"))
            require(record.get("job") == job and record.get("code_hash") == code and record.get("status") == "complete",
                    "durable record missing or not complete for " + jid)
            archived_output = phase_root / "outputs" / (jid + ".json")
            require(archived_output.is_file() and file_sha256(archived_output) == record["output_hash"],
                    "archived output hash mismatch for " + jid)
            inputs = archived_inputs(job, phase_root) + job_inputs(job, phase_root, original)
            for extra in source.get("extra_inputs", []):
                if isinstance(extra, dict) and "relative_to_simulation" in extra:
                    inputs.append(_row(None, original / extra["relative_to_simulation"],
                                       relative_to_simulation=extra["relative_to_simulation"]))
                else:
                    extra = extra["path"] if isinstance(extra, dict) else extra
                    inputs.append(_row(extra, extra))
            item = {"item_id": digest([name, jid])[:24], "source": name, "group": group, "kind": job["kind"],
                    "job": job, "producing_code_hash": code, "checkout": str(checkout), "phase_root": str(phase_root),
                    "archived_record_sha256": file_sha256(phase_root / "records" / (jid + ".json")),
                    "archived_output_sha256": record["output_hash"], "inputs": inputs, "protected": protected}
            if binding is not None:
                item["plan_binding"] = binding
            items.append(item)
        frozen_sources.append({"name": name, "group": group, "selection": source["selection"], "producing_code_hash": code,
                               "checkout": str(checkout), "spec": str(spec_path), "spec_sha256": file_sha256(spec_path),
                               "root": str(root), "original_simulation": str(original), "jobs": len(spec["jobs"]),
                               "strata": strata, "selected": len(chosen), "registration": pin_record,
                               "a14_binding": binding})
    require(items, "empty requalification sample")
    require(len({i["item_id"] for i in items}) == len(items), "duplicate requalification item")
    sample = {"schema": SAMPLE_SCHEMA, "tags": {"a11": A11_TAG, "a15": A15_TAG}, "harness_sha256": harness_hashes(),
              "comparison": COMPARISON, "sources": frozen_sources, "items": items, "item_count": len(items)}
    document = seal(sample)
    write_once(output, document)
    return document


# ---------------------------------------------------------------------------
# Replay
# ---------------------------------------------------------------------------

def scratch_for(item, sample_sha256):
    return Path(item["checkout"]) / "simulation" / "v3" / "_requalification" / sample_sha256[:16] / item["item_id"]


def result_path_for(item, output_dir):
    return Path(output_dir) / "results" / (item["item_id"] + ".json")


def failed_record_to_disk(record, result_path):
    """Write a failed per-item record without raising. The canonical write is
    tried first; on any failure a minimal record is written with plain file
    I/O; on a second failure the record is returned unwritten. Never overwrites
    an existing per-item result."""
    try:
        if result_path.exists():
            record["note"] = "per-item result already existed when the exception was caught; it was not overwritten"
            return record
        result_path.parent.mkdir(parents=True, exist_ok=True)
        result_path.write_bytes(canonical(record) + b"\n")
        return record
    except Exception as first:  # noqa: BLE001
        try:
            minimal = {"item_id": record.get("item_id"), "job_id": record.get("job_id"), "passed": False,
                       "error": str(record.get("error")) + " (minimal record; first write failed: %s)" % type(first).__name__}
            with open(str(result_path), "x", encoding="utf-8") as stream:
                stream.write(json.dumps(minimal) + "\n")
            record["note"] = "written as a minimal record after the canonical write failed"
        except Exception as second:  # noqa: BLE001
            record["note"] = "per-item result could not be written: " + type(second).__name__
        return record


def guarded_run_item(item, sample_sha256, output_dir, hashes, **kw):
    """run_item inside the pool: any exception becomes a failed per-item record
    on disk, never an unhandled exception that would leave the attempt without
    a record or an acceptance. The handler itself calls nothing that can raise:
    ``hashes`` was computed once by the attempt, and the write is guarded."""
    try:
        return run_item(item, sample_sha256, output_dir, hashes, **kw)
    except Exception as exc:  # noqa: BLE001
        record = {"item_id": item.get("item_id"), "job_id": item.get("job", {}).get("id"), "passed": False,
                  "exit_code": None, "error": type(exc).__name__ + ": " + str(exc), "sample_sha256": sample_sha256,
                  "harness_sha256": hashes}
        try:
            result_path = result_path_for(item, Path(output_dir).resolve())
        except Exception:  # noqa: BLE001
            record["note"] = "per-item result path could not be formed"
            return record
        return failed_record_to_disk(record, result_path)


def run_item(item, sample_sha256, output_dir, hashes=None, *, python=None, keep_scratch=False, expected_host=None):
    """One item in its own interpreter at its checkout. Returns the record
    written as the per-item result. The result is written once: the item must
    have no result file before launch; a non-zero worker exit, an unreadable
    worker file, or a worker host fingerprint that differs from
    ``expected_host`` is a failure on disk, whatever the worker file holds."""
    output_dir = Path(output_dir).resolve()
    item_path = output_dir / "items" / (item["item_id"] + ".json")
    result_path = result_path_for(item, output_dir)
    require(not result_path.exists(), "per-item result already exists for %s; results are never overwritten" % item["job"]["id"])
    item_path.parent.mkdir(parents=True, exist_ok=True)
    result_path.parent.mkdir(parents=True, exist_ok=True)
    item_path.write_bytes(canonical(item) + b"\n")
    # The worker writes its own file; the harness writes the per-item result
    # once, with the exit code, so an interrupted item never leaves a partial result.
    worker_path = result_path.with_suffix(".worker.json")
    require(not worker_path.exists(), "worker result already exists for %s" % item["job"]["id"])
    command = _worker_command(item["checkout"], python) + ["--item", str(item_path), "--scratch", str(scratch_for(item, sample_sha256)),
                                                           "--result", str(worker_path)]
    if keep_scratch:
        command.append("--keep-scratch")
    started = time.time()
    completed = subprocess.run(command, capture_output=True, text=True, cwd=str(Path(item["checkout"]) / "simulation"))
    if worker_path.is_file():
        try:
            record = read_json(worker_path)
            require(isinstance(record, dict), "worker result is not a record")
        except (ValueError, RequalificationError, OSError):
            record = {"item_id": item["item_id"], "passed": False, "error": "unreadable worker result"}
    else:
        record = {"item_id": item["item_id"], "passed": False, "error": "worker wrote no result"}
    record.setdefault("job_id", item["job"]["id"])
    record.update(exit_code=completed.returncode, started_epoch=started, finished_epoch=time.time(),
                  stderr_tail=completed.stderr[-4000:], sample_sha256=sample_sha256,
                  harness_sha256=hashes if hashes is not None else harness_hashes())
    if completed.returncode != 0:
        record["passed"] = False
        record.setdefault("error", "worker exited with code %d" % completed.returncode)
    if record.get("passed") is True and not record.get("runtime"):
        record["passed"] = False
        record["error"] = "worker recorded no runtime"
    if expected_host is not None and record.get("runtime") and host_fingerprint_of(record) != expected_host:
        # The rejection reaches disk here, before anything can act on the item.
        record["passed"] = False
        record["error"] = "; ".join(filter(None, ["worker recorded a different host fingerprint from the attempt",
                                                  record.get("error")]))
        record["host_fingerprint_mismatch"] = {"record": host_fingerprint_of(record), "attempt": expected_host}
    result_path.write_bytes(canonical(record) + b"\n")
    return record


def worker_files(output_dir):
    """Every ``*.worker.json`` in the results directory with its SHA-256."""
    results = Path(output_dir).resolve() / "results"
    if not results.is_dir():
        return {}
    return {p.name: file_sha256(p) for p in sorted(results.glob("*.worker.json"))}


def interrupted_worker_file(item, sample_sha256, output_dir, hashes=None):
    """Classify a worker file left with no per-item result by an interrupted
    attempt. Nothing is deleted. A parsed record reporting a failure is a
    recorded failure: the per-item result is written from it, marked
    ``harness_interrupted`` with the exit code unknown, and the resume is then
    refused like any recorded failure. A record reporting a pass, or a file that
    does not parse, keeps the item re-executable, since the exit code is
    unknown; the file is preserved under ``<item>.worker.interrupted.<n>.json``
    when the resume proceeds. Returns ``None``, ``"failed"`` or ``"preserve"``."""
    result_path = result_path_for(item, Path(output_dir).resolve())
    worker_path = result_path.with_suffix(".worker.json")
    if result_path.exists() or not worker_path.is_file():
        return None
    try:
        record = read_json(worker_path)
        complete = isinstance(record, dict) and "passed" in record
    except (ValueError, OSError):
        record, complete = None, False
    if complete and record.get("passed") is not True:
        record.setdefault("job_id", item["job"]["id"])
        record.update(passed=False, exit_code=None, harness_interrupted=True, sample_sha256=sample_sha256,
                      harness_sha256=hashes if hashes is not None else harness_hashes(),
                      error=record.get("error") or "worker recorded a failure; the harness was interrupted before recording it")
        result_path.write_bytes(canonical(record) + b"\n")
        return "failed"
    return "preserve"


def preserve_worker_file(item, output_dir, expected_sha256=None):
    """Rename an interrupted worker file to the next free
    ``<item>.worker.interrupted.<n>.json``; never delete it. The file must still
    hash to what the pre-scan recorded (``expected_sha256``, None for absent):
    a change or an appearance means a worker from the prior attempt is still
    running, and the resume is refused."""
    result_path = result_path_for(item, Path(output_dir).resolve())
    worker_path = result_path.with_suffix(".worker.json")
    current = file_sha256(worker_path) if worker_path.is_file() else None
    require(current == expected_sha256, "worker file for %s appeared or changed since the pre-scan; a worker from "
            "the prior attempt may still be running" % item["job"]["id"])
    if current is None:
        return None
    n = 0
    while True:
        target = result_path.with_name(result_path.stem + ".worker.interrupted.%d.json" % n)
        if not target.exists():
            break
        n += 1
    os.replace(worker_path, target)
    return str(target)


def prior_record(item, output_dir):
    """The per-item result an earlier attempt left, if any, as parsed JSON."""
    path = result_path_for(item, output_dir)
    if not path.is_file():
        return None
    try:
        return read_json(path)
    except ValueError:
        return {"item_id": item["item_id"], "passed": False, "error": "unreadable prior result"}


def resumable_record(item, sample_sha256, output_dir, hashes=None):
    """A passed record from an interrupted attempt at the same frozen sample and
    harness, reused on resume. A prior record that reports a failure, or a
    non-zero worker exit, is never reused and never replaced: the attempt that
    holds it is final."""
    record = prior_record(item, output_dir)
    if record is None:
        return None
    same = (record.get("sample_sha256") == sample_sha256
            and record.get("harness_sha256") == (hashes if hashes is not None else harness_hashes())
            and record.get("job_id") == item["job"]["id"])
    if record.get("passed") is True and record.get("exit_code") == 0 and same:
        return record
    require(same, "prior result for %s belongs to another sample or harness; use a fresh output directory"
            % item["job"]["id"])
    raise RequalificationError("prior attempt reported a failure for %s; it stays final and cannot be resumed over"
                               % item["job"]["id"])


# The environment fingerprint: the host facts every worker records, compared
# between the attempt and every reused record (REQUALIFICATION_PLAN.md section 6).
HOST_KEYS = ("python", "python_executable", "platform", "uname", "boot_id", "numpy", "scipy", "numerical_libraries",
             "packages_sha256", "multiprocessing_start_method", "int_max_str_digits")
CHECKOUT_KEYS = ("code_identity", "source_manifest_sha256")


def host_fingerprint_of(record):
    runtime = record.get("runtime") or {}
    return {k: runtime.get(k) for k in HOST_KEYS}


def checkout_fingerprint_of(record):
    runtime = record.get("runtime") or {}
    return {k: runtime.get(k) for k in CHECKOUT_KEYS}


def clear_interrupted_scratch(item, sample_sha256):
    """Remove the one scratch directory an interrupted item left behind: an
    explicitly scoped cleanup, limited to this sample's scratch for this item."""
    import shutil
    scratch = scratch_for(item, sample_sha256)
    if scratch.exists():
        require(scratch.resolve().parent == (Path(item["checkout"]) / "simulation" / "v3" / "_requalification"
                                             / sample_sha256[:16]).resolve(), "refusing to clear a path outside this sample's scratch")
        shutil.rmtree(scratch)
        return str(scratch)
    return None


def worker_cap():
    return max(1, min(WORKER_HARD_CAP, (os.cpu_count() or 2) - 1))


def reservation_key(item):
    """``kind.route.setting`` where the job has them, else ``kind.setting``, else ``kind``."""
    job = item.get("job", {})
    config = job.get("config", {})
    source = config.get("a1_job", {}).get("config", config)
    setting = source.get("setting_name")
    route = config.get("route")
    keys = []
    if route and setting:
        keys.append("%s.%s.%s" % (item["kind"], route, setting))
    if setting:
        keys.append("%s.%s" % (item["kind"], setting))
    keys.append(item["kind"])
    return keys


def reservation_bytes(item, reservations_gb):
    for key in reservation_key(item):
        if key in reservations_gb:
            return int(float(reservations_gb[key]) * GB)
    raise RequalificationError("no memory reservation for job kind " + item["kind"])


def admit(item, reservations_gb, headroom_bytes, pending, *, wait_seconds=600., poll_seconds=1., collect=None):
    """Wait until MemAvailable, less the reservations of every running item
    (which may not have allocated yet), covers the headroom plus this item's
    reservation. Before each check ``collect`` records every finished future so
    its reservation is released. Refuses, rather than waiting forever, when
    nothing is running that could free memory, or when the wait exceeds
    ``wait_seconds``. ``pending`` maps futures to their items."""
    needed = headroom_bytes + reservation_bytes(item, reservations_gb)
    waited = 0.

    def running_reservation():
        """Reservations of futures still running; a future that finished since
        the last collection no longer holds memory."""
        if not isinstance(pending, dict):
            return 0
        return sum(reservation_bytes(p, reservations_gb) for f, p in pending.items()
                   if not (hasattr(f, "done") and f.done()))

    def check():
        available = mem_available_bytes()
        require(available is not None, "memory admission requires a readable MemAvailable")
        reserved = running_reservation()
        if available - reserved >= needed:
            return {"available_bytes": available, "pending_reserved_bytes": reserved, "needed_bytes": needed,
                    "waited_seconds": waited}
        return None

    while True:
        if collect is not None:
            collect()
        admitted = check()
        if admitted is not None:
            return admitted
        require(pending, "memory admission refused: %d bytes available, %d needed, nothing pending to free memory"
                % (mem_available_bytes() or 0, needed))
        if waited >= wait_seconds:
            # One final collection and re-check before refusing: a job that
            # finished during the last wait releases its reservation.
            if collect is not None:
                collect()
            admitted = check()
            if admitted is not None:
                return admitted
            raise RequalificationError("memory admission timed out after %.0f seconds" % waited)
        time.sleep(poll_seconds)
        waited += poll_seconds


def replay(sample_path, output_dir, *, workers=1, python=None, keep_scratch=False, resume=False,
           reservations_gb=None, headroom_gb=None, admission_wait_seconds=600.):
    """Replay every frozen item; stop dispatching at the first mismatch, error or
    non-zero worker exit; seal the acceptance record. Passing requires every
    item to pass with a zero exit code and no environment mismatch.

    Items run one producer checkout at a time, in the sample's order, with a
    barrier between checkouts. ``workers`` is capped at min(31, cpu_count - 1).
    Before each dispatch MemAvailable must cover ``headroom_gb`` (default a fifth
    of total memory) plus the item's reservation by kind.

    Without ``resume``, the output directory must hold no prior per-item
    result. With ``resume``, passed records at the same sample and harness whose
    host fingerprint equals this attempt's are kept, any item with no result
    file has its interrupted scratch cleared and is re-executed from its original
    seed, and a prior record reporting a failure refuses the resume.

    Safety against a prior attempt's surviving processes: the attempt writes
    ``attempt.lock`` (host, process id, start time) in the output directory at
    the beginning and removes it at the end; any attempt, resume included,
    refuses while a lock exists, and the operator removes the lock only after
    confirming that no worker from the prior attempt is still running. On
    resume, every worker file's SHA-256 is recorded at the pre-scan, re-checked
    at preservation, and the results directory is re-scanned after all
    preservations: a worker file that appeared or changed refuses the resume.
    The acceptance record is always written, as failed, when the attempt ends
    in an error."""
    sample_path = Path(sample_path).resolve()
    output_dir = Path(output_dir).resolve()
    document = read_json(sample_path)
    sample = unseal(document)
    require(sample.get("schema") == SAMPLE_SCHEMA, "not a requalification sample")
    hashes = harness_hashes()
    require(sample["harness_sha256"] == hashes, "harness source changed since the sample was frozen")
    acceptance_path = output_dir / "acceptance.json"
    require(not acceptance_path.exists(), "acceptance record already exists; a failed attempt is final")
    lock_path = output_dir / "attempt.lock"
    output_dir.mkdir(parents=True, exist_ok=True)
    import platform
    try:
        descriptor = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        raise RequalificationError("attempt.lock exists in %s: a prior attempt may still have workers running; remove the "
                                   "lock only after confirming none is" % output_dir)
    with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
        stream.write(json.dumps({"host": platform.node(), "pid": os.getpid(), "started_epoch": time.time(),
                                 "sample_sha256": document["sha256"]}) + "\n")
    # The lock is removed only when no worker of this attempt can be alive:
    # before dispatch began, or after the pool drained. An interrupt that
    # escapes the pool leaves the lock, and says so.
    state = {"dispatch_entered": False, "drained": False}
    try:
        return _replay_locked(sample_path, output_dir, document, sample, hashes, state, workers=workers, python=python,
                              keep_scratch=keep_scratch, resume=resume, reservations_gb=reservations_gb,
                              headroom_gb=headroom_gb, admission_wait_seconds=admission_wait_seconds)
    finally:
        if not state["dispatch_entered"] or state["drained"]:
            try:
                lock_path.unlink()
            except OSError:
                pass
        else:
            print("attempt.lock kept in %s: workers of this attempt may still be running" % output_dir, file=sys.stderr)


def _replay_locked(sample_path, output_dir, document, sample, hashes, state, *, workers, python, keep_scratch, resume,
                   reservations_gb, headroom_gb, admission_wait_seconds):

    acceptance_path = output_dir / "acceptance.json"
    cap = worker_cap()
    require(isinstance(workers, int) and 1 <= workers <= cap, "workers must be between 1 and %d on this host" % cap)
    reservations_gb = dict(DEFAULT_RESERVATIONS_GB, **(reservations_gb or {}))
    total = mem_total_bytes()
    headroom_bytes = int(headroom_gb * GB) if headroom_gb is not None else (int(total * .2) if total else 0)
    sys.set_int_max_str_digits(0)  # as the workers and the recorder paths run
    attempt_environment = host_fingerprint()
    expected_host = {k: attempt_environment.get(k) for k in HOST_KEYS}
    started = time.time()
    results_dir = output_dir / "results"
    prior_files = sorted(results_dir.glob("*.json")) if results_dir.exists() else []
    prior_results = [p for p in prior_files if ".worker." not in p.name]
    if not resume:
        require(not prior_files, "output directory holds %d prior per-item results and %d worker files; use --resume or a fresh directory"
                % (len(prior_results), len(prior_files) - len(prior_results)))
    records, halted = {}, None
    resumed, restarts = [], []
    items = []
    prescan = {}
    if resume:
        # A reported failure in the prior attempt is final, including one an
        # interrupted worker recorded that the harness never wrote up: it is
        # written to disk first, then refused. A record from another
        # environment cannot be reused. The whole resume is refused before any
        # scratch is touched, any worker file renamed, or any record replaced.
        # Every worker file's hash is recorded here and re-checked later.
        prescan = worker_files(output_dir)
        for item in sample["items"]:
            interrupted_worker_file(item, document["sha256"], output_dir, hashes)
            prior = resumable_record(item, document["sha256"], output_dir, hashes)
            if prior is not None:
                require(host_fingerprint_of(prior) == expected_host,
                        "prior result for %s was recorded in a different environment; the attempt cannot be resumed"
                        % item["job"]["id"])
    preserved_names = set()
    for item in sample["items"]:
        prior = resumable_record(item, document["sha256"], output_dir, hashes) if resume else None
        if prior is not None:
            records[item["item_id"]] = prior
            resumed.append(item["item_id"])
            continue
        if resume:
            require(prior_record(item, output_dir) is None, "item %s has a prior result and cannot be re-executed" % item["job"]["id"])
            cleared = clear_interrupted_scratch(item, document["sha256"])
            # A worker file with no per-item result that reports a pass, or does
            # not parse, has an unknown exit code: it is preserved by rename,
            # never deleted, and the item re-executed from its seed. It must
            # still hash to what the pre-scan saw.
            name = result_path_for(item, output_dir).with_suffix(".worker.json").name
            preserved = preserve_worker_file(item, output_dir, prescan.get(name))
            if preserved:
                preserved_names.add(name)
            restarts.append({"item_id": item["item_id"], "job_id": item["job"]["id"], "cleared_scratch": cleared,
                             "preserved_worker_file": preserved, "epoch": time.time(),
                             "reason": "interrupted before a result was recorded"})
        items.append(item)
    if resume:
        # After all preservations the results directory must hold exactly the
        # pre-scan's worker files, less the preserved ones, unchanged.
        expected = {name: sha for name, sha in prescan.items() if name not in preserved_names}
        require(worker_files(output_dir) == expected,
                "a worker file appeared or changed during the resume; a worker from the prior attempt may still be running")
    # One producer checkout at a time, in the sample's order, with a barrier.
    groups, order = {}, []
    for item in items:
        if item["checkout"] not in groups:
            order.append(item["checkout"])
        groups.setdefault(item["checkout"], []).append(item)
    admissions = []
    pending = {}

    def admit_item(item):
        """Admission for one item; a refusal is recorded and returns None. A
        failure collected during the wait keeps precedence as the first failure."""
        nonlocal halted
        try:
            return admit(item, reservations_gb, headroom_bytes, pending, wait_seconds=admission_wait_seconds, collect=collect)
        except RequalificationError as exc:
            if halted is None:
                halted = {"item_id": item["item_id"], "job_id": item["job"]["id"], "error": str(exc)}
            records[item["item_id"]] = {"item_id": item["item_id"], "job_id": item["job"]["id"], "passed": False, "error": str(exc)}
            return None

    def collect():
        """Record every finished future, so its reservation is released and a
        failure halts dispatch. Called by the dispatcher and by admission."""
        nonlocal halted
        for done in [f for f in list(pending) if f.done()]:
            item = pending.pop(done)
            try:
                record = done.result()
            except Exception as exc:  # noqa: BLE001
                record = failed_record_to_disk(
                    {"item_id": item["item_id"], "job_id": item["job"]["id"], "passed": False, "exit_code": None,
                     "error": "worker task raised " + type(exc).__name__ + ": " + str(exc),
                     "sample_sha256": document["sha256"], "harness_sha256": hashes},
                    result_path_for(item, output_dir))
            records[item["item_id"]] = record
            # Second line only: run_item already wrote the rejection to disk.
            if record.get("runtime") and host_fingerprint_of(record) != expected_host:
                record["passed"] = False
                record.setdefault("error", "worker recorded a different host fingerprint from the attempt")
            if (not record.get("passed") or record.get("exit_code") != 0) and halted is None:
                halted = {"item_id": item["item_id"], "job_id": item["job"]["id"], "error": record.get("error"),
                          "exit_code": record.get("exit_code")}

    dispatch_error = None
    try:
        state["dispatch_entered"] = True
        _dispatch(order, groups, workers, pending, collect, admit_item, records, admissions, document, output_dir,
                  hashes, python, keep_scratch, expected_host, lambda: halted, state)
    except Exception as exc:  # noqa: BLE001
        # The acceptance is written whatever happens, and fails.
        dispatch_error = type(exc).__name__ + ": " + str(exc)
        if halted is None:
            halted = {"item_id": None, "job_id": None, "error": "dispatch raised " + dispatch_error}
    ordered = [records.get(i["item_id"], {"item_id": i["item_id"], "job_id": i["job"]["id"], "passed": False,
                                          "error": "not executed: dispatch stopped after the first failure"})
               for i in sample["items"]]
    complete = all(i["item_id"] in records for i in sample["items"])
    return _acceptance(sample_path, output_dir, document, sample, hashes, ordered, complete, len(records), workers, cap,
                       python, reservations_gb, headroom_bytes, total, admissions, order, attempt_environment,
                       expected_host, started, resumed, restarts, halted, dispatch_error)


def _dispatch(order, groups, workers, pending, collect, admit_item, records, admissions, document, output_dir, hashes,
              python, keep_scratch, expected_host, is_halted, state=None):
    try:
        _dispatch_pool(order, groups, workers, pending, collect, admit_item, records, admissions, document, output_dir,
                       hashes, python, keep_scratch, expected_host, is_halted)
    finally:
        # Only an exit through the pool's own join (normal, an Exception, or an
        # interrupt the join completed) reaches here with no live worker.
        if state is not None and not any(not f.done() for f in pending):
            state["drained"] = True


def _dispatch_pool(order, groups, workers, pending, collect, admit_item, records, admissions, document, output_dir, hashes,
                   python, keep_scratch, expected_host, is_halted):
    with ThreadPoolExecutor(max_workers=workers) as pool:
        for checkout in order:
            if is_halted() is not None:
                break
            queue, index = groups[checkout], 0
            pending.clear()
            while index < len(queue) or pending:
                while index < len(queue) and len(pending) < workers and is_halted() is None:
                    item = queue[index]
                    admitted = admit_item(item)
                    if admitted is None:
                        index += 1
                        break  # refused; the refusal is recorded and dispatch stops
                    if is_halted() is not None:
                        break  # a job collected during the wait failed; nothing more is dispatched
                    admissions.append(dict(admitted, item_id=item["item_id"]))
                    pending[pool.submit(guarded_run_item, item, document["sha256"], output_dir, hashes, python=python,
                                        keep_scratch=keep_scratch, expected_host=expected_host)] = item
                    index += 1
                if not pending:
                    if is_halted() is not None:
                        break
                    continue
                collect()
                if pending:
                    time.sleep(.05)


def _acceptance(sample_path, output_dir, document, sample, hashes, ordered, complete, executed, workers, cap, python,
                reservations_gb, headroom_bytes, total, admissions, order, attempt_environment, expected_host,
                started, resumed, restarts, halted, dispatch_error):
    acceptance_path = output_dir / "acceptance.json"
    # The full source manifest is recorded once per checkout; every item keeps
    # its identity and the manifest's digest. Every record, resumed or executed
    # now, must carry this attempt's host fingerprint, and records at the same
    # checkout must agree on the checkout identity.
    checkouts, environment_mismatches = {}, []
    for record in ordered:
        runtime = record.get("runtime")
        if isinstance(runtime, dict) and "source_manifest" in runtime:
            manifest = runtime.pop("source_manifest")
            runtime["source_manifest_sha256"] = digest(manifest)
            checkouts.setdefault(record["checkout"], {"source_manifest": manifest, "code_identity": runtime.get("code_identity")})
    for record in ordered:
        if record.get("runtime"):
            if host_fingerprint_of(record) != expected_host:
                environment_mismatches.append({"item_id": record["item_id"], "kind": "host", "record": host_fingerprint_of(record),
                                               "attempt": expected_host})
            reference = checkouts.get(record.get("checkout"))
            if reference and checkout_fingerprint_of(record) != {"code_identity": reference["code_identity"],
                                                                 "source_manifest_sha256": digest(reference["source_manifest"])}:
                environment_mismatches.append({"item_id": record["item_id"], "kind": "checkout",
                                               "record": checkout_fingerprint_of(record)})
    exit_codes_ok = all(r.get("exit_code") == 0 for r in ordered)
    acceptance = {"schema": ACCEPTANCE_SCHEMA, "sample_sha256": document["sha256"], "sample_path": str(sample_path),
                  "harness_sha256": hashes, "comparison": COMPARISON, "exclusions": sorted(TIMING_EXCLUSIONS),
                  "dispatch_error": dispatch_error,
                  "workers": workers, "worker_cap": cap, "threads_per_worker": 1, "python": python or sys.executable,
                  "reservations_gb": reservations_gb, "headroom_bytes": headroom_bytes, "memory_total_bytes": total,
                  "admissions": admissions, "checkout_order": order, "attempt_environment": attempt_environment,
                  "started_epoch": started, "finished_epoch": time.time(), "items": ordered,
                  "executed": executed, "item_count": len(sample["items"]), "complete": complete,
                  "resumed": resumed, "restarts": restarts, "first_failure": halted, "checkouts": checkouts,
                  "environment_mismatches": environment_mismatches, "exit_codes_zero": exit_codes_ok,
                  "passed": (complete and all(r.get("passed") for r in ordered) and exit_codes_ok
                             and not environment_mismatches and dispatch_error is None)}
    write_once(acceptance_path, seal(acceptance))
    return acceptance


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    p = commands.add_parser("freeze")
    p.add_argument("--sources", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--python")
    p = commands.add_parser("replay")
    p.add_argument("--sample", required=True)
    p.add_argument("--output-dir", required=True)
    p.add_argument("--workers", type=int, default=1)
    p.add_argument("--python")
    p.add_argument("--keep-scratch", action="store_true")
    p.add_argument("--resume", action="store_true", help="continue an interrupted attempt at the same sample")
    p.add_argument("--reservations", help="JSON mapping job kinds to reservation GB, overriding the plan's classes")
    p.add_argument("--headroom-gb", type=float)
    args = parser.parse_args(argv)
    if args.command == "freeze":
        document = freeze_sample(read_json(args.sources), args.output, python=args.python)
        print({"items": document["payload"]["item_count"], "sample_sha256": document["sha256"]})
        return 0
    acceptance = replay(args.sample, args.output_dir, workers=args.workers, python=args.python,
                        keep_scratch=args.keep_scratch, resume=args.resume,
                        reservations_gb=read_json(args.reservations) if args.reservations else None,
                        headroom_gb=args.headroom_gb)
    print({"passed": acceptance["passed"], "executed": acceptance["executed"], "items": acceptance["item_count"],
           "first_failure": acceptance["first_failure"]})
    return 0 if acceptance["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
