"""A11: reviewed, committed compatibility of completed A10 artifacts only.

Records never change runner/resume identities. Proofs use non-registered
execute calls in spawned workers; their only outputs are comparison hashes.
"""
from concurrent.futures import ProcessPoolExecutor
from contextvars import ContextVar
from datetime import date
import hashlib
import json
import multiprocessing as mp
from pathlib import Path
import subprocess

from .artifacts import (ROOT, SIMULATION, atomic_json, available_cpus, canonical,
                        code_identity, configure_threads, digest, file_hash, read,
                        runtime, scoped, seal, source_manifest, unseal)

SCHEMA = "v3-A11-compatibility-1"
RECORD_DIRECTORY = ROOT / "runs/registered"
RECORD_PATTERN = "A11_compatibility_*.json"
_proof_producer = ContextVar("a11_nonregistered_proof_producer", default=None)
_TIMING = {"seconds", "trajectory_seconds", "rescore_seconds", "scoring_seconds_by_k_star"}
_PROCESS = {"code_hash"}  # Producer provenance, separately checked against X/Y.
COMPARISON = {"canonical": "job plus result", "excluded_result_root_fields": sorted(_TIMING | _PROCESS),
              "producer_metadata": "envelope and optional result.code_hash verified separately against X and Y"}


def record_name(producing, new):
    return "A11_compatibility_" + digest([producing, new])[:24] + ".json"


def _require(condition, message):
    if not condition:
        raise ValueError(message)


def _hash(value):
    return isinstance(value, str) and len(value) == 64 and all(c in "0123456789abcdef" for c in value)


def changed_files(before, after):
    return {p: {"before_sha256": before.get(p), "after_sha256": after.get(p)}
            for p in sorted(set(before) | set(after)) if before.get(p) != after.get(p)}


def _committed_bytes(path):
    repo = SIMULATION.parent
    rel = path.resolve().relative_to(repo).as_posix()
    subprocess.run(["git", "-C", str(repo), "ls-files", "--error-unmatch", rel],
                   check=True, capture_output=True)
    return subprocess.run(["git", "-C", str(repo), "show", "HEAD:" + rel],
                          check=True, capture_output=True).stdout


def _selected(populations):
    selected = []
    for group in populations:
        phase = group["phase"]
        ids = group["job_ids"]
        _require(ids and len(ids) == len(set(ids)), "empty or duplicate compatibility stratum")
        selected.extend(sorted(ids, key=lambda jid: (digest(["A11-compatibility", phase, jid]), jid))[:2])
    _require(len(selected) == len(set(selected)), "duplicate compatibility job across strata")
    return selected


def validate_record(path):
    """Fail closed: commitment, approval, the complete manifest diff and proof."""
    path = Path(path).resolve()
    _require(path.parent == RECORD_DIRECTORY.resolve() and path.match(RECORD_PATTERN), "unregistered compatibility path")
    _require(_committed_bytes(path) == path.read_bytes(), "compatibility record differs from HEAD")
    record = unseal(read(path))
    old, new = record["producing_code_hash"], record["new_code_hash"]
    _require(_hash(old) and old != new and new == code_identity(), "compatibility record has a different new identity")
    _require(path.name == record_name(old, new), "compatibility record filename mismatch")
    _require(record.get("schema") == SCHEMA and record.get("passed") is True, "compatibility proof failed")
    _require(record.get("comparison") == COMPARISON, "different compatibility comparison convention")
    approval = record.get("operator_approval") or {}
    _require(approval.get("approved") is True and isinstance(approval.get("operator"), str)
             and approval["operator"].strip(), "compatibility approval missing")
    date.fromisoformat(approval["date"])
    before, after = record["producing_source_manifest"], record["new_source_manifest"]
    _require(digest(before) == old and digest(after) == new, "compatibility source manifest identity mismatch")
    _require(after == source_manifest(), "compatibility after-hashes differ from current files")
    changes = changed_files(before, after)
    _require(changes and changes == record["changed_files"], "incomplete compatibility source diff")
    reasons = record["reasons"]
    _require(set(reasons) == set(changes) and all(isinstance(v, str) and v.strip() for v in reasons.values()),
             "every changed file needs its reason")
    proofs = record["proofs"]
    expected = _selected(record["populations"])
    _require(expected and len(proofs) == len(expected) and {p["job_id"] for p in proofs} == set(expected),
             "incomplete compatibility sample proof")
    _require(all(p.get("passed") is True and _hash(p.get("before_sha256"))
                 and p["before_sha256"] == p.get("after_sha256") and _hash(p.get("job_sha256")) for p in proofs),
             "compatibility job proof failed")
    return old


def accepted_identities():
    """Only the running identity and identities in valid committed records."""
    accepted = {code_identity()}
    for path in sorted(RECORD_DIRECTORY.glob(RECORD_PATTERN)):
        try:
            accepted.add(validate_record(path))
        except (ValueError, KeyError, TypeError, OSError, subprocess.CalledProcessError):
            # An invalid or older-target record grants nothing. validate_record
            # exposes the precise refusal when that record is reviewed.
            continue
    return accepted


def read_identities(*, registered):
    """The proof's isolated non-registered execute path may read its old tables.

    This allowance is never returned by accepted_identities and never applies
    to a registered read. It cannot publish or resume any registered result.
    """
    values = accepted_identities()
    if not registered and _proof_producer.get() is not None:
        values.add(_proof_producer.get())
    return values


def comparison_bytes(job, result):
    # Exclude named execution metadata at the result root only. In particular,
    # scientific time/step/history fields and all nested results remain intact.
    clean = {k: v for k, v in result.items() if k not in _TIMING | _PROCESS}
    # The runner persists JSON object keys as strings. Normalize the fresh
    # result through that same JSON domain before sorting (census cell keys
    # are integers in memory and strings in durable records).
    return canonical(json.loads(canonical({"job": job, "result": clean})))


def _stratum(job):
    cfg = job["config"]
    phase = cfg.get("phase", job["kind"])
    source = cfg.get("a1_job", {}).get("config", cfg)
    kernel = source.get("kernel", source.get("model", {}))
    capability = kernel.get("capability", kernel.get("successor_capability", 1.))
    return phase, capability, source.get("setting_name", "run")


def _execute_proof(item):
    configure_threads(1)
    from .production_runner import execute
    token = _proof_producer.set(item["producing_code_hash"])
    try:
        info = runtime(1)
        result = execute(item["job"], registered=False, registration=None, root=Path(item["phase_root"]))
        _require(result.get("code_hash", code_identity()) == code_identity(), "re-execution result has wrong producer metadata")
        return {"after_sha256": hashlib.sha256(comparison_bytes(item["job"], result)).hexdigest(), "runtime": info}
    except Exception as exc:
        return {"after_sha256": None, "error": type(exc).__name__ + ": " + str(exc)}
    finally:
        _proof_producer.reset(token)


def build_record(sources, reasons_path, target, *, workers=None):
    """Freeze a sample, execute it once, and seal even a failed proof.

    sources is a list of {spec, root}; reasons holds producing_source_manifest
    (exported from X) and reasons (one string per changed manifest path).
    Both source manifests hash to their declared identities. No Git writes.
    """
    from .instrument import declaration
    from .production_runner import completed
    target = scoped(target)
    _require(not target.exists(), "compatibility attempt is final; target already exists")
    reason_doc = read(reasons_path)
    before = reason_doc["producing_source_manifest"]
    old, new = digest(before), code_identity()
    after = source_manifest()
    changes = changed_files(before, after)
    reasons = reason_doc["reasons"]
    _require(old != new and changes, "compatibility needs two different source identities")
    _require(set(reasons) == set(changes) and all(isinstance(v, str) and v.strip() for v in reasons.values()),
             "every changed file needs its reason")
    grouped, selected_jobs, inputs = {}, {}, []
    for source in sources:
        root, spec_path = Path(source["root"]).resolve(), Path(source["spec"]).resolve()
        spec = unseal(read(spec_path))
        _require(spec["code_hash"] == old and declaration(spec.get("instrument")).a10, "source is not the producing A10 identity")
        _require(read(root / "identity.json") == {"code_hash": old, "spec_hash": digest(spec)}, "source root identity mismatch")
        _require(unseal(read(root / "manifest.json")) == spec, "source root manifest mismatch")
        _require(read(root / "launches.json")[-1].get("complete") is True, "compatibility needs a completed launch")
        for job in spec["jobs"]:
            _require(job["id"] not in selected_jobs, "duplicate source job")
            phase_root = root / job["config"].get("phase", job["kind"])
            output = completed(phase_root, job, old)
            _require(output is not None, "missing durable source output")
            _require(output["result"].get("code_hash", old) == old, "source result has wrong producer metadata")
            group = _stratum(job)
            grouped.setdefault(group, []).append(job["id"])
            selected_jobs[job["id"]] = {"job": job, "phase_root": str(phase_root), "producing_code_hash": old,
                                        "before_sha256": hashlib.sha256(comparison_bytes(job, output["result"])).hexdigest(),
                                        "output_file_sha256": file_hash(phase_root / "outputs" / (job["id"] + ".json"))}
        inputs.append({"spec": str(spec_path), "root": str(root), "spec_sha256": file_hash(spec_path)})
    populations = [{"phase": p, "capability": c, "setting": s, "job_ids": sorted(ids)}
                   for (p, c, s), ids in sorted(grouped.items())]
    sample = _selected(populations)
    _require(sample, "empty compatibility sample")
    cap = min(12, max(1, min(16, available_cpus()) - 4))
    workers = cap if workers is None else workers
    _require(isinstance(workers, int) and 1 <= workers <= cap, "compatibility worker count exceeds work-mode cap")
    record = {"schema": SCHEMA, "non_registered": True, "producing_code_hash": old, "new_code_hash": new,
              "producing_source_manifest": before, "new_source_manifest": after, "changed_files": changes,
              "reasons": reasons, "inputs": inputs, "populations": populations,
              "selection_rule": 'two smallest digest(["A11-compatibility", phase, job_id]) per capability/setting',
              "comparison": COMPARISON,
              "operator_approval": None, "passed": False, "proofs": [],
              "execution": {"mode": "work", "workers": min(workers, len(sample)), "threads": 1}}
    # The declared population and selection are durable before any execution.
    attempt = target.with_suffix(".attempt.json")
    _require(not attempt.exists(), "compatibility attempt is final; selection already exists")
    atomic_json(attempt, seal({**record, "selected_job_ids": sample}))
    configure_threads(1)
    try:
        with ProcessPoolExecutor(max_workers=min(workers, len(sample)), mp_context=mp.get_context("spawn")) as pool:
            results = pool.map(_execute_proof, [selected_jobs[jid] for jid in sample])
            for jid, fresh in zip(sample, results):
                original = selected_jobs[jid]
                record["proofs"].append({"job_id": jid, "job_sha256": digest(original["job"]),
                                          "source_output_sha256": original["output_file_sha256"],
                                          "before_sha256": original["before_sha256"], **fresh,
                                          "passed": original["before_sha256"] == fresh["after_sha256"]})
        _require(code_identity() == new and source_manifest() == after, "source changed during compatibility proof")
    except BaseException as exc:
        record["error"] = type(exc).__name__ + ": " + str(exc)
        atomic_json(target, seal(record))
        raise
    record["passed"] = all(p["passed"] for p in record["proofs"])
    atomic_json(target, seal(record))
    return record


def approve_record(path, operator, approved_date):
    """Operator-invoked record edit only; no commit and no implicit approval."""
    record = unseal(read(path))
    _require(record.get("passed") is True and all(p.get("passed") is True for p in record["proofs"]), "failed compatibility proof is final")
    _require(isinstance(operator, str) and operator.strip(), "operator name required")
    date.fromisoformat(approved_date)
    _require(record.get("operator_approval") is None, "compatibility approval already recorded")
    record["operator_approval"] = {"approved": True, "operator": operator, "date": approved_date}
    atomic_json(path, seal(record))
    return record


def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("build")
    p.add_argument("--sources", required=True); p.add_argument("--reasons", required=True)
    p.add_argument("--output", required=True); p.add_argument("--workers", type=int)
    p = sub.add_parser("approve")
    p.add_argument("record"); p.add_argument("--operator", required=True); p.add_argument("--date", required=True)
    args = parser.parse_args()
    if args.command == "build":
        record = build_record(read(args.sources), args.reasons, args.output, workers=args.workers)
        print({"passed": record["passed"], "jobs": len(record["proofs"]), "record_sha256": file_hash(args.output)})
        return 0 if record["passed"] else 1
    record = approve_record(args.record, args.operator, args.date)
    print({"approved_record_sha256": file_hash(args.record), "registered_filename": record_name(record["producing_code_hash"], record["new_code_hash"])})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
