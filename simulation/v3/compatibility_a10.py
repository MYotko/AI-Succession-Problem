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
# A19: the guard authority a registered rerun carried, bound to one proof job.
_proof_authority = ContextVar("a11_nonregistered_proof_authority", default=None)
_TIMING = {"seconds", "trajectory_seconds", "rescore_seconds", "scoring_seconds_by_k_star"}
_PROCESS = {"code_hash"}  # Producer provenance, separately checked against X/Y.
COMPARISON = {"canonical": "job plus result", "excluded_result_root_fields": sorted(_TIMING | _PROCESS),
              "producer_metadata": "envelope and optional result.code_hash verified separately against X and Y"}
# The A14 and A16 extension kinds replay through replay_a16's empty-scratch
# adapters; A13's keeps replay_a14's. Normal execution would load checkpoints.
EXTENSION_REPLAY_KINDS = ('a14_validate_plain_ext2', 'a16_validate_plain_r1', 'a16_validate_plain_r2')


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


def proof_authority(job):
    """A19: inside a proof only, the succession-guard authority the job's
    producing run held, so its gates decide as they did there.

    A registered rerun builds its guards with an authority from its verified
    registration, and ExecutionGuards.authorize admits a succession on
    production tables only with one. A proof re-executes non-registered, so
    without this every succession such a rerun attempts is refused and its
    output cannot equal the original. The authority comes from the producing
    spec's registration, verified historically when the record is assembled,
    and is bound to one job id. It is never set outside _execute_proof, never
    set for a non-registered source, whose run had none, and it publishes or
    resumes nothing.
    """
    authority = _proof_authority.get()
    if _proof_producer.get() is None or authority is None or authority.get("job_id") != job["id"]:
        return None
    return authority


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
    # A19 (P2): each context variable is set inside its own try/finally, so a
    # failure between the two sets still resets the first.
    token = _proof_producer.set(item["producing_code_hash"])
    try:
        granted = _proof_authority.set(item.get("proof_authority"))
        try:
            info = runtime(1)
            start = time.perf_counter()
            with input_view(item.get('input_view')):
                if item['job']['kind'] == 'a13_validate_plain_ext' and item.get('a13_replay'):
                    from .replay_a14 import replay
                    result = replay(item)
                elif item['job']['kind'] in EXTENSION_REPLAY_KINDS and item.get('extension_replay'):
                    from .replay_a16 import replay
                    result = replay(item)
                else:
                    result = execute(item["job"], registered=False, registration=None, root=Path(item["phase_root"]))
            _require(result.get("code_hash", code_identity()) == code_identity(), "re-execution result has wrong producer metadata")
            return {"after_sha256": hashlib.sha256(comparison_bytes(item["job"], result)).hexdigest(), "runtime": info,
                    "_peak_rss_bytes": peak_rss_bytes(), "_worker_seconds": time.perf_counter() - start}
        except Exception as exc:
            return {"after_sha256": None, "error": type(exc).__name__ + ": " + str(exc)}
        finally:
            _proof_authority.reset(granted)
    finally:
        _proof_producer.reset(token)


def collect_record(sources, reasons_path):
    """Read the original populations and comparisons without executing a job."""
    from .instrument import declaration
    from .production_runner import completed
    from .snapshot_a11 import historical_root_provenance
    # The sources' declared historical roots. A producing identity that carries
    # a sealed history staged its copies inside its own checkout, so its
    # original validation plan is read through this declaration, which resolves
    # existing immutable copies and accepts no write. The roots reached through
    # a sealed source specification are hash-bound; those supplied by the
    # sources document are not, and the record keeps the two apart.
    provenance = historical_root_provenance(sources)
    history_view = sorted(set(provenance['specification']) | set(provenance['sources_document']))
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
        registration = None
        if spec.get('registered'):
            from .artifacts import verify_registration
            registration = verify_registration(spec['registration'], instrument=spec['instrument'], historical=True)
        _require(read(root / "identity.json") == {"code_hash": old, "spec_hash": digest(spec)}, "source root identity mismatch")
        _require(unseal(read(root / "manifest.json")) == spec, "source root manifest mismatch")
        _require(read(root / "launches.json")[-1].get("complete") is True, "compatibility needs a completed launch")
        # A19 (P1): per-spec values computed once, before the job loop. The
        # spec hash is reused by every proof_authority and by inputs; the
        # original validation plan of a registered single-host extension spec
        # (and its binding checks) is read once and reused for every job.
        spec_sha256 = file_hash(spec_path)
        original_plans = {}  # Keyed by the branch that reads it: A13's file, or the A14/A16 history.
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
            if job['kind'] == 'rerun' and registration is not None:
                # A19: the registered run's guards held an authority; the proof
                # carries the historically verified registration in its place.
                selected_jobs[job['id']]['proof_authority'] = {
                    "a19_proof": True, "job_id": job["id"], "registration": registration,
                    "spec_sha256": spec_sha256}
            if job['kind'] == 'a13_validate_plain_ext':
                from .replay_a14 import binding
                checkpoints = [read(phase_root / 'a13_checkpoints' / job['id'] / f'{r["replicate"]:02d}.json')
                               for r in output['result']['replicates']]
                selected_jobs[job['id']]['a13_replay'] = binding(spec, job, output['result'], checkpoints)
            if job['kind'] in EXTENSION_REPLAY_KINDS:
                from .replay_a16 import binding as extension_binding, checkpoint_directory
                checkpoints = [read(phase_root / checkpoint_directory(job['kind']) / job['id'] / f'{r["replicate"]:02d}.json')
                               for r in output['result']['replicates']]
                selected_jobs[job['id']]['extension_replay'] = extension_binding(spec, job, output['result'], checkpoints)
            from .compatibility_shards_a11 import resource_estimate
            extension = job['kind'] == 'a13_validate_plain_ext' or job['kind'] in EXTENSION_REPLAY_KINDS
            if extension and spec['registered'] and 'pull_dispatch' not in spec:
                # The replay adapters also carry the original sealed scheduling
                # class into the proof. A single-host extension plan has no pull
                # extension; its original validation plan supplies that class.
                from .table_validation_a4 import _recompute_plan_hash
                branch = job['kind'] == 'a13_validate_plain_ext'
                if branch not in original_plans:
                    if branch:
                        _require(file_hash(spec['original_plan_path']) == spec['original_plan_file_sha256'],
                                 'A13 replay original plan changed')
                        original_plans[branch] = unseal(read(spec['original_plan_path']))
                        _require(_recompute_plan_hash(original_plans[branch]) == original_plans[branch]['plan_hash']
                                 and original_plans[branch]['plan_hash'] == spec['original_plan_hash'], 'A13 replay original plan binding differs')
                    else:
                        from .replay_a16 import original_validation_plan
                        original_plans[branch] = original_validation_plan(spec, history_view)
                        _require(_recompute_plan_hash(original_plans[branch]) == original_plans[branch]['plan_hash'],
                                 'extension replay original plan binding differs')
                # Read-only below: resource_estimate returns a new dict and
                # never mutates the plan, so one object serves every job.
                original = original_plans[branch]
                source = next(j for j in original['jobs'] if j['config']['phase'] == 'validate_plain'
                              and j['config']['a1_job']['id'] == job['config']['a1_job']['id'])
                resource = resource_estimate(original, source)
                resource['worker_seconds'] *= job['config']['R_max'] / 3
            else:
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
        inputs.append({"spec": str(spec_path), "root": str(root), "spec_sha256": spec_sha256})
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
              "execution": {"mode": "work", "workers": 1, "threads": 1, "historical_view": history_view,
                            "historical_view_provenance": provenance}}
    return record, {jid: selected_jobs[jid] for jid in sample}, profiles


def proof_row(original, fresh):
    return {"job_id": original['job']['id'], "job_sha256": digest(original["job"]),
            "source_output_sha256": original["output_file_sha256"],
            "before_sha256": original["before_sha256"],
            **{k: v for k, v in fresh.items() if not k.startswith('_')},
            "passed": original["before_sha256"] == fresh["after_sha256"]}


def preflight_record(sources, reasons_path, target):
    """The assembly refusals a build raises before any compute, writing nothing.

    A build's first act is to assemble the record: the sources and their
    registration, the reasons against the live diff, each producing identity's
    bindings and sealed history, the sample, and the inputs every selected job
    will read. None of that depends on compute, but a build only reaches it
    when it is launched, so when records are built one after another a blocking
    condition in the last one surfaces after the earlier ones have already run
    and must be rebuilt. This runs the same assembly for a planned record and
    executes no job, creates no attempt and spends no reservation, so a batch
    can clear every record it intends to build before the first proof starts.

    It is not a launch gate and does not cover every refusal a build can raise.
    Host admission, the settings and CPU check, live memory and qualified class
    reservations, snapshot reception, effective thread verification, the
    configuration test itself and a dispatch's source-pin verification all come
    later and can still refuse. A record that clears here is cleared of the
    blocking conditions in its own assembly, nothing more.
    """
    from .compatibility_shards_a11 import configuration_items, portable_inventory, reservation_path
    from .snapshot_a11 import historical_root_provenance
    target = scoped(target)
    record, selected_jobs, profiles = collect_record(sources, reasons_path)
    old, new = record["producing_code_hash"], record["new_code_hash"]
    registered = record_name(old, new)
    # A build may write to a staged path and be copied to its registered name
    # after approval, as 17.3's template does. A build that writes straight
    # into the registered directory must already carry that name, since
    # validate_record refuses any other.
    if target.parent == RECORD_DIRECTORY.resolve():
        _require(target.name == registered, "a planned record in the registered directory is not named record_name(producing, new)")
    provenance = historical_root_provenance(sources)
    roots = sorted(set(provenance["specification"]) | set(provenance["sources_document"]))
    options = {"historical_roots": roots} if roots else {}
    items = list(selected_jobs.values())
    # The same configuration-profile precondition single_preflight applies, and
    # the same dependency enumeration, which is where a worker input missing
    # from a fresh checkout or outside the declared roots refuses.
    missing = [i for i in items if i["profile_key"] not in profiles]
    _require(all(i["job"]["kind"] == "fixture" for i in missing), "missing pre-launch configuration profile")
    inputs = unseal(portable_inventory(items, **options))
    configured = [i for i in items if i["profile_key"] in profiles]
    configuration = unseal(portable_inventory(configuration_items(configured, profiles), **options))
    # Not target.exists(): an empty file, a directory or a half-written record
    # satisfies that, and the first version of this check accepted all three, so
    # a terminal record would have been reported as merely already built. Weaker
    # than validate_record on purpose, which also demands the record be
    # committed and operator-approved; a batch resuming straight after a build
    # has neither yet.
    try:
        finished = unseal(read(target))
    except Exception:
        finished = None
    built = (isinstance(finished, dict) and finished.get("schema") == SCHEMA and finished.get("passed") is True
             and finished.get("producing_code_hash") == old and finished.get("new_code_hash") == new)
    spent = sorted(p.name for p in (target.with_suffix(".attempt.json"), reservation_path(record)) if p.exists())
    # 17.3's proof finality: a spent attempt or reservation with no completed
    # record cannot be built again at this identity, so a batch that plans to
    # produce it must refuse here rather than at this record's turn, with its
    # siblings' hours already spent. A completed record is not spent, it is
    # done, and a resumed batch verifies and skips it.
    _require(built or not spent,
             "attempt or reservation already spent with no completed record at %s: %s" % (target.name, ", ".join(spent)))
    return {"record": target.name, "registered_name": registered, "producing_code_hash": old, "new_code_hash": new,
            "strata": len(record["populations"]), "jobs": sum(len(g["job_ids"]) for g in record["populations"]),
            "sample": len(selected_jobs), "changed_files": len(record["changed_files"]),
            "historical_view": roots, "historical_view_provenance": provenance,
            "proof_inputs": len(inputs["files"]),
            "configuration_inputs": len(configuration["files"]),
            "already_built": built, "already_spent": spent}


def build_record(sources, reasons_path, target, *, workers=None, memory_floor_gb=0., override_reason=None, operator=None, memory_headroom=.8, profile="local", mode=None, cpu_budget=None):
    """Freeze a sample, execute it once with memory admission, seal failures."""
    from copy import deepcopy
    from .compatibility_shards_a11 import (run_items, write_once, reservation_path,
                                         reserve_attempt, check_reservation, single_preflight, source_historical_roots)
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
    roots = source_historical_roots(sources)
    snapshot_options = {'historical_roots': roots} if roots else {}
    view, configuration, floor, budget, workers = single_preflight(record, selected_jobs, profiles, target, workers, 0.,
        settings=settings, **snapshot_options)
    authority = read(control_root / 'memory_authority.json')
    for cfg in configuration.values():
        for key, peak in cfg.get('class_peaks_gb', {}).items():
            authority['peaks'][key] = max(authority['peaks'].get(key, 0.), peak)
    atomic_json(control_root / 'memory_authority.json', authority)
    # A19 (P3): the record carries the build's actual operating mode, worker
    # count and thread count, from the same settings and control the build
    # uses (collect_record's placeholder said work/1/1 regardless).
    record['execution'].update(mode=settings['mode'], workers=workers, threads=settings['threads'],
                               memory_budget_gb=budget, memory_floor_gb=0., configuration=configuration, settings=settings)
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
    p = sub.add_parser("preflight")
    p.add_argument("--sources", required=True); p.add_argument("--reasons", required=True); p.add_argument("--output", required=True)
    p = sub.add_parser("control"); p.add_argument("record"); p.add_argument("--workers", type=int, required=True); p.add_argument("--reason")
    p = sub.add_parser("approve")
    p.add_argument("record"); p.add_argument("--operator", required=True); p.add_argument("--date", required=True)
    args = parser.parse_args()
    if args.command == "build":
        record = build_record(read(args.sources), args.reasons, args.output, workers=args.workers, memory_floor_gb=args.memory_floor_gb, profile=args.profile, mode=args.mode, cpu_budget=args.cpu_budget, **wc.arguments(args))
        print({"passed": record["passed"], "jobs": len(record["proofs"]), "record_sha256": file_hash(args.output)})
        return 0 if record["passed"] else 1
    if args.command == 'preflight':
        print(json.dumps(preflight_record(read(args.sources), args.reasons, args.output), sort_keys=True))
        return 0
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
