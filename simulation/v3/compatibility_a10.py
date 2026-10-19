"""A11: reviewed, committed compatibility of completed A10 artifacts only.

Records never change runner/resume identities. Proofs use non-registered
execute calls in spawned workers; their only outputs are comparison hashes.
"""
from contextvars import ContextVar
from datetime import date
import hashlib
import json
from pathlib import Path
import subprocess
import time

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
    from .production_runner import execute, peak_rss_bytes
    from .artifacts import input_view
    token = _proof_producer.set(item["producing_code_hash"])
    try:
        info = runtime(1)
        start = time.perf_counter()
        with input_view(item.get('input_view')):
            result = execute(item["job"], registered=False, registration=None, root=Path(item["phase_root"]))
        _require(result.get("code_hash", code_identity()) == code_identity(), "re-execution result has wrong producer metadata")
        return {"after_sha256": hashlib.sha256(comparison_bytes(item["job"], result)).hexdigest(), "runtime": info,
                "_peak_rss_bytes": peak_rss_bytes(), "_worker_seconds": time.perf_counter() - start}
    except Exception as exc:
        return {"after_sha256": None, "error": type(exc).__name__ + ": " + str(exc)}
    finally:
        _proof_producer.reset(token)


def collect_record(sources, reasons_path):
    """Read the original populations and comparisons without executing a job."""
    from .instrument import declaration
    from .production_runner import completed
    reason_doc = read(reasons_path)
    before = reason_doc["producing_source_manifest"]
    old, new = digest(before), code_identity()
    after = source_manifest()
    changes = changed_files(before, after)
    reasons = reason_doc["reasons"]
    _require(old != new and changes, "compatibility needs two different source identities")
    _require(set(reasons) == set(changes) and all(isinstance(v, str) and v.strip() for v in reasons.values()),
             "every changed file needs its reason")
    grouped, selected_jobs, inputs, profiles = {}, {}, [], {}
    class_peaks, class_seconds = {}, {}
    for source in sources:
        root, spec_path = Path(source["root"]).resolve(), Path(source["spec"]).resolve()
        spec = unseal(read(spec_path))
        _require(spec["code_hash"] == old and declaration(spec.get("instrument")).a10, "source is not the producing A10 identity")
        if spec.get('registered'):
            from .artifacts import verify_registration
            verify_registration(spec['registration'], instrument=spec['instrument'], historical=True)
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
            from .compatibility_shards_a11 import resource_estimate
            resource = resource_estimate(spec, job)
            selected_jobs[job['id']]['resources'] = resource
            from .worker_control import observe
            completion_path = phase_root / 'records' / (job['id'] + '.json')
            completion = read(completion_path)
            # completed() already loaded this envelope for the mandatory proof
            # comparison. Legacy RSS is top-level executor metadata, never a
            # scientific result field. New records duplicate it for blind tools.
            for peak in (completion.get('peak_rss_bytes'), output.get('peak_rss_bytes')):
                observe(class_peaks, resource, peak)
            from .worker_control import positive
            if positive(completion.get('worker_seconds')):
                class_seconds.setdefault(resource['memory_class'], []).append(completion['worker_seconds'])
            phase = job['config'].get('phase', job['kind'])
            profile_key = digest([str(spec_path), phase])
            selected_jobs[job['id']]['profile_key'] = profile_key
            if phase in spec.get('configuration', {}):
                profiles[profile_key] = dict(profile=spec['configuration'][phase], phase=phase,
                    phase_root=str(phase_root), producing_code_hash=old)
        inputs.append({"spec": str(spec_path), "root": str(root), "spec_sha256": file_hash(spec_path)})
    populations = [{"phase": p, "capability": c, "setting": s, "job_ids": sorted(ids)}
                   for (p, c, s), ids in sorted(grouped.items())]
    for item in selected_jobs.values():
        r = item['resources']
        timings = class_seconds.get(r['memory_class'], [])
        r['measured_worker_seconds'] = sum(timings) / len(timings) if timings else None
        if class_peaks.get(r['memory_class']):
            r['memory_gb'] = r.get('planning_memory_gb', r['memory_gb'])
        r['registered_memory_gb'] = r['memory_gb']
        r['measured_memory_gb'] = class_peaks.get(r['memory_class'], 0.)
        r['memory_gb'] = max(r['memory_gb'], r['measured_memory_gb'])
    sample = _selected(populations)
    _require(sample, "empty compatibility sample")
    record = {"schema": SCHEMA, "non_registered": True, "producing_code_hash": old, "new_code_hash": new,
              "producing_source_manifest": before, "new_source_manifest": after, "changed_files": changes,
              "reasons": reasons, "inputs": inputs, "populations": populations,
              "selection_rule": 'two smallest digest(["A11-compatibility", phase, job_id]) per capability/setting',
              "comparison": COMPARISON,
              "operator_approval": None, "passed": False, "proofs": [],
              "execution": {"mode": "work", "workers": 1, "threads": 1}}
    return record, {jid: selected_jobs[jid] for jid in sample}, profiles


def proof_row(original, fresh):
    return {"job_id": original['job']['id'], "job_sha256": digest(original["job"]),
            "source_output_sha256": original["output_file_sha256"],
            "before_sha256": original["before_sha256"],
            **{k: v for k, v in fresh.items() if not k.startswith('_')},
            "passed": original["before_sha256"] == fresh["after_sha256"]}


def build_record(sources, reasons_path, target, *, workers=None, memory_floor_gb=0., override_reason=None, operator=None, memory_headroom=.8, profile="local", mode=None, cpu_budget=None):
    """Freeze a sample, execute it once with memory admission, seal failures."""
    from copy import deepcopy
    from .compatibility_shards_a11 import (run_items, write_once, reservation_path,
                                         reserve_attempt, check_reservation, single_preflight)
    target = scoped(target)
    attempt = target.with_suffix('.attempt.json')
    _require(not target.exists() and not attempt.exists(), 'compatibility attempt is final; selection already exists')
    record, selected_jobs, profiles = collect_record(sources, reasons_path)
    _require(not reservation_path(record).exists(), 'identity pair already reserved; compatibility attempt is final')
    sample = _selected(record['populations'])
    from . import worker_control as wc
    from .production_runner import caps
    cpu_budget = available_cpus() if cpu_budget is None else cpu_budget
    mode = mode or ("normal" if profile == "x2" else "work")
    cap = caps(profile, cpu_budget)[mode]
    workers = cap if workers is None else workers
    settings = wc.settings(dict(profile=profile, workers=workers, cpu_budget=cpu_budget, threads=1, mode=mode,
        override_reason=override_reason, operator=operator, memory_headroom=memory_headroom))
    workers = min(wc.selection(settings)['workers'], len(sample))
    control_root = target.with_suffix('.workers')
    wc.initial_control(control_root, settings)
    atomic_json(control_root / 'settings.json', settings)
    atomic_json(control_root / 'memory_authority.json', dict(
        estimates={j: i['resources'] for j, i in selected_jobs.items()},
        peaks={i['resources']['memory_class']: i['resources'].get('measured_memory_gb', 0.) for i in selected_jobs.values()}))
    atomic_json(control_root / 'identity.json', dict(code_hash=code_identity(), target=str(target)))
    view, configuration, floor, budget, workers = single_preflight(record, selected_jobs, profiles, target, workers, 0., settings=settings)
    authority = read(control_root / 'memory_authority.json')
    for cfg in configuration.values():
        for key, peak in cfg.get('class_peaks_gb', {}).items():
            authority['peaks'][key] = max(authority['peaks'].get(key, 0.), peak)
    atomic_json(control_root / 'memory_authority.json', authority)
    record['execution'].update(workers=workers, memory_budget_gb=budget, memory_floor_gb=0., configuration=configuration, settings=settings)
    # The declared population and selection are durable before any execution.
    payload = deepcopy({**record, 'selected_job_ids': sample, 'target_path': target.relative_to(SIMULATION).as_posix()})
    reserve_attempt(record, payload, attempt)
    write_once(attempt, seal(payload))
    check_reservation(record, payload, attempt)
    configure_threads(1)
    try:
        results, trace = run_items([dict(i, input_view=view) for i in selected_jobs.values()], workers, budget,
            control_path=control_root / 'control.json', host_settings=settings, headroom=settings['memory_headroom'],
            class_peaks=authority['peaks'], measurements_by_profile=configuration)
        record['execution']['admission'] = trace
        record['execution']['worker_control'] = read(control_root / 'control.json')
        record['proofs'] = [proof_row(selected_jobs[jid], results[jid]) for jid in sample]
        _require(code_identity() == record['new_code_hash'] and source_manifest() == record['new_source_manifest'],
                 "source changed during compatibility proof")
        check_reservation(record, payload, attempt)
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
    p.add_argument("--profile", choices=("local", "x2"), default="local")
    p.add_argument("--mode", choices=("normal", "work")); p.add_argument("--cpu-budget", type=int)
    p.add_argument('--memory-floor-gb', type=float, default=0.)
    from . import worker_control as wc
    wc.options(p)
    p = sub.add_parser("control"); p.add_argument("record"); p.add_argument("--workers", type=int, required=True); p.add_argument("--reason")
    p = sub.add_parser("approve")
    p.add_argument("record"); p.add_argument("--operator", required=True); p.add_argument("--date", required=True)
    args = parser.parse_args()
    if args.command == "build":
        record = build_record(read(args.sources), args.reasons, args.output, workers=args.workers, memory_floor_gb=args.memory_floor_gb, profile=args.profile, mode=args.mode, cpu_budget=args.cpu_budget, **wc.arguments(args))
        print({"passed": record["passed"], "jobs": len(record["proofs"]), "record_sha256": file_hash(args.output)})
        return 0 if record["passed"] else 1
    if args.command == 'control':
        from .compatibility_shards_a11 import check_reservation
        target = scoped(args.record)
        _require(not target.exists(), 'compatibility attempt is final')
        attempt = target.with_suffix('.attempt.json')
        root = target.with_suffix('.workers')
        _require(read(root / 'identity.json') == dict(code_hash=code_identity(), target=str(target)), 'proof control identity mismatch')
        if attempt.exists():
            payload = unseal(read(attempt))
            check_reservation(payload, payload, attempt)
        print(wc.control(root, read(root / 'settings.json'), workers=args.workers, reason=args.reason))
        return 0
    record = approve_record(args.record, args.operator, args.date)
    print({"approved_record_sha256": file_hash(args.record), "registered_filename": record_name(record["producing_code_hash"], record["new_code_hash"])})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
