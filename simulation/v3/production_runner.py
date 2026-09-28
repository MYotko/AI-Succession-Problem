"""Local-only durable process runner. NumPy is imported only inside workers."""
import argparse
import ctypes
import multiprocessing as mp
import os
from pathlib import Path
import platform
import signal
import sys
import time
import traceback
from .artifacts import (ROOT, SIMULATION, atomic_json, read, digest, seal, unseal, file_hash,
                        code_identity, stable_job, configure_threads, runtime, available_cpus, scoped, lease, verify_registration)


def event(root, kind, **fields):
    path = scoped(root) / "events.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    from .artifacts import canonical
    with path.open("ab") as stream:
        stream.write(canonical({"epoch": time.time(), "event": kind, **fields}) + b"\n")
        stream.flush()
        os.fsync(stream.fileno())


def caps(profile, budget):
    if budget < 1 or profile not in ("local", "x2"):
        raise ValueError("invalid CPU budget/profile")
    if profile == "x2":
        if budget > 32:
            raise ValueError("X2 CPU budget is at most 32")
        return {"normal": max(1, budget - 1), "work": max(1, budget - 4), "configuration": budget}
    return {"normal": min(12, max(1, budget - 1)), "work": min(12, max(1, budget - 4)), "configuration": min(12, budget)}


def choose(measurements, worker_limit, slot_limit, allowed_threads=1):
    feasible = [r for r in measurements if r["valid"] and r["workers"] <= worker_limit
                and r["workers"] * r["threads"] <= slot_limit and r["threads"] <= allowed_threads]
    if not feasible:
        raise RuntimeError("no measured configuration fits the launch mode")
    pooled = {}
    for r in feasible:
        key = (r["workers"], r["threads"])
        work, seconds = pooled.get(key, (0, 0))
        pooled[key] = (work + r["completed"], seconds + r["wall_seconds"])
    best = max(work / seconds for work, seconds in pooled.values())
    near = [(w, t, work / seconds) for (w, t), (work, seconds) in pooled.items() if work / seconds >= .95 * best]
    w, t, rate = min(near, key=lambda v: (v[0] * v[1], v[0], -v[2]))
    return {"workers": w, "threads": t, "jobs_per_hour": 3600 * rate, "best_jobs_per_hour": 3600 * best}


def process_alive(pid):
    if os.name == "nt":
        dll = ctypes.WinDLL("kernel32", use_last_error=True)
        dll.OpenProcess.restype = ctypes.c_void_p
        handle = dll.OpenProcess(0x1000, False, pid)
        if not handle:
            return ctypes.get_last_error() == 5
        code = ctypes.c_ulong()
        ok = dll.GetExitCodeProcess(ctypes.c_void_p(handle), ctypes.byref(code))
        dll.CloseHandle(ctypes.c_void_p(handle))
        return not ok or code.value == 259
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True


def completed(root, job, code):
    record_path = root / "records" / (job["id"] + ".json")
    if not record_path.exists():
        return None
    record = read(record_path)
    output = root / "outputs" / (job["id"] + ".json")
    if record.get("job") != job or record.get("code_hash") != code or record.get("status") != "complete" or not output.exists() or file_hash(output) != record["output_hash"]:
        raise RuntimeError("completion record or output identity mismatch")
    value = read(output)
    if value["job"] != job or value["code_hash"] != code:
        raise RuntimeError("completed output identity mismatch")
    if "worker_seconds" in record:
        value["worker_seconds"] = record["worker_seconds"]
    return value


def execute(job, registered=False, registration=None):
    kind, config = job["kind"], job["config"]
    if kind == "fixture":
        if registered or job["tag"] != "validation":
            raise ValueError("runner fixtures are validation only")
        time.sleep(config.get("seconds", .01))
        return {"seed": job["seed"], "fixture": True}
    if kind == "calibration":
        from .calibration import run_seed
        return run_seed(config, job["seed"], job["tag"])
    calibration = read(SIMULATION / config["calibration_path"]) if config.get("calibration_path") else None
    if kind == "table":
        from .offline_estimator import estimate
        return estimate(config, job["seed"], calibration)
    if kind != "rerun":
        raise ValueError("unknown job kind")
    from .integration import V3Model
    from .production_tables import ProductionTables
    model_args = dict(config.get("model", {}))
    tables = None
    if config.get("tables_path"):
        if calibration is None:
            raise ValueError("tables require a matching calibration")
        tables = ProductionTables(SIMULATION / config["tables_path"], calibration_hash=calibration["sha256"], registered=registered)
    model = V3Model(seed=job["seed"], calibration=calibration, tables=tables, registered=registered, registration=registration, **model_args)
    records = model.run(config.get("steps", 500))
    populations = [r["population"] for r in records]
    return {"tag": job["tag"], "fixture_tables": model.tables.fixture, "steps": len(records),
            "population_path": populations, "population_mean": sum(populations) / max(1, len(populations)),
            "population_max": max(populations, default=0), "final_population": model.population,
            "survived_threshold_30": model.population >= 30, "yield_events": model.yield_events,
            "periods": [p.audit() for p in model.periods], "diagnostics": records}


def worker(root_name, job, code, threads, registered, registration):
    root = Path(root_name)
    configure_threads(threads)
    try:
        with lease(root / "leases" / (job["id"] + ".lock")):
            if code_identity() != code:
                raise RuntimeError("worker source changed")
            if completed(root, job, code) is not None:
                return
            info = runtime(threads)
            started = time.time()
            before = time.perf_counter()
            result = execute(job, registered, registration)
            output = {"job": job, "code_hash": code, "runtime": info, "result": result,
                      "seconds": time.perf_counter() - before, "started_epoch": started, "finished_epoch": time.time()}
            path = root / "outputs" / (job["id"] + ".json")
            atomic_json(path, output)
            atomic_json(root / "records" / (job["id"] + ".json"),
                        {"job": job, "code_hash": code, "status": "complete", "output_hash": file_hash(path), "completed_epoch": time.time(),
                         "worker_seconds": time.perf_counter() - before})
    except BaseException:
        atomic_json(root / "failures" / (job["id"] + ".json"), {"job": job, "traceback": traceback.format_exc()})
        raise


def dispatch(root, jobs, code, settings, deadline, *, measurements=None, fixed=None, control_root=None, registered=False, registration=None):
    root = scoped(root)
    root.mkdir(parents=True, exist_ok=True)
    control_root = control_root or root
    done = {j["id"] for j in jobs if completed(root, j, code) is not None}
    pending = [j for j in jobs if j["id"] not in done]
    old = read(root / "active.json") if (root / "active.json").exists() else {}
    if old.get("pids") and (old.get("machine") != platform.node() or any(process_alive(p) for p in old["pids"])):
        raise RuntimeError("recorded workers may still exist; refusing unsafe resume")
    active, maximum, reason, last_mode, last_selection = {}, 0, "complete", None, None
    attempts_path = root / "attempts.json"
    attempts = read(attempts_path) if attempts_path.exists() else {}
    context = mp.get_context("spawn")
    signals = []
    handlers = {sig: signal.signal(sig, lambda number, frame: signals.append(number)) for sig in (signal.SIGINT, signal.SIGTERM)}
    start = time.perf_counter()
    monotonic_end = time.monotonic() + max(0, deadline - time.time())
    previous_report = 0.
    mode_effective = None
    def publish():
        atomic_json(root / "active.json", {"machine": platform.node(), "pids": [p.pid for p, _, _ in active.values()]})
        status = {"total": len(jobs), "completed": len(done), "running": len(active),
                  "pending": len(jobs) - len(done) - len(active), "maximum_active": maximum,
                  "reason": reason, "deadline_epoch": deadline, "mode": last_mode, "selection": last_selection}
        atomic_json(root / "status.json", status)
        return status
    def stop(reason):
        for process, job, _ in active.values():
            if process.is_alive():
                event(root, "restart_required", job=job["id"], original_seed=job["seed"], reason=reason)
                process.terminate()
        stop_end = time.monotonic() + 10
        for process, _, _ in active.values():
            process.join(max(0, stop_end - time.monotonic()))
            if process.is_alive():
                process.kill()
        kill_end = time.monotonic() + 5
        for process, _, _ in active.values():
            process.join(max(0, kill_end - time.monotonic()))
            if process.is_alive():
                raise RuntimeError("worker failed to stop")
    try:
        while pending or active:
            control = read(control_root / "control.json")
            mode = control["mode"]
            if mode not in ("normal", "work"):
                raise ValueError("invalid live mode")
            cap = settings["caps"][mode]
            maximum_request = min(settings["workers"], control.get("max_workers", settings["workers"]))
            if maximum_request < 1:
                raise ValueError("worker limit must be positive")
            selected = fixed or choose(measurements, min(cap, maximum_request), settings["cpu_budget"], settings["threads"])
            if fixed:
                cap = settings["caps"]["configuration"]
            if mode != last_mode or selected != last_selection:
                last_mode, last_selection = mode, selected
                mode_effective = None
                event(root, "mode_requested", mode=mode, selection=selected, active=len(active), configuration=bool(fixed))
            if time.time() >= deadline or time.monotonic() >= monotonic_end or signals or control.get("interrupt_now"):
                reason = "deadline" if time.time() >= deadline or time.monotonic() >= monotonic_end else "interrupted"
                stop(reason)
                active.clear()
                break
            for key, (process, job, threads) in list(active.items()):
                if not process.is_alive():
                    process.join()
                    del active[key]
                    if completed(root, job, code) is None:
                        attempts[key] = attempts.get(key, 0) + 1
                        atomic_json(attempts_path, attempts)
                        event(root, "restart", job=key, attempt=attempts[key], seed=job["seed"])
                        if attempts[key] >= 3:
                            raise RuntimeError("job failed three times; inspect durable failure")
                        pending.insert(0, job)
                    else:
                        done.add(key)
                        event(root, "complete", job=key, pid=process.pid)
            effective_limit = min(cap, selected["workers"])
            if len(active) <= effective_limit and mode_effective != mode:
                mode_effective = mode
                event(root, "mode_effective", mode=mode, active=len(active), worker_limit=effective_limit)
            slots = sum(t for _, _, t in active.values())
            while pending and not control.get("stop_dispatch") and len(active) < effective_limit and slots + selected["threads"] <= settings["cpu_budget"]:
                job = pending.pop(0)
                if attempts.get(job["id"], 0) >= 3:
                    raise RuntimeError("job has exhausted retries")
                process = context.Process(target=worker, args=(str(root), job, code, selected["threads"], registered, registration))
                process.start()
                active[job["id"]] = (process, job, selected["threads"])
                slots += selected["threads"]
                maximum = max(maximum, len(active))
                event(root, "dispatch", job=job["id"], seed=job["seed"], pid=process.pid, active=len(active), slots=slots, mode=mode)
                publish()
            status = publish()
            if time.monotonic() - previous_report >= 30:
                print({"phase": root.name, **status}, flush=True)
                previous_report = time.monotonic()
            if control.get("stop_dispatch") and not active:
                reason = "drained"
                break
            time.sleep(.05)
    except BaseException:
        reason = "failed"
        raise
    finally:
        try:
            stop("runner exit")
            active.clear()
            done = {j["id"] for j in jobs if completed(root, j, code) is not None}
            status = publish()
        finally:
            for sig, handler in handlers.items():
                signal.signal(sig, handler)
    return {**status, "wall_seconds": time.perf_counter() - start}


def configuration_test(root, phase, profile, settings, deadline, launch_number):
    candidates = profile["workers_x2"] if settings["profile"] == "x2" else profile["workers_local"]
    if settings["profile"] == "x2" and not {8, 12, 16, 24, 32}.issubset(candidates):
        raise ValueError("missing required X2 configuration candidates")
    if settings["threads"] == 2 and not profile.get("material_multithreaded_numerics"):
        raise ValueError("two threads require profiling evidence")
    pairs = [(w, t) for t in profile.get("threads", [1]) for w in candidates if w <= settings["caps"]["configuration"] and w * t <= settings["cpu_budget"] and t <= settings["threads"]]
    measurements = []
    for round_index in range(profile.get("rounds", 2)):
        for w, t in pairs if round_index % 2 == 0 else reversed(pairs):
            count = profile["jobs_x2"] if settings["profile"] == "x2" else profile["jobs_local"]
            if count < w:
                raise ValueError("configuration work must occupy every tested worker")
            configs = profile.get("configs", [profile["config"]])
            jobs = [stable_job(profile["kind"], configs[i % len(configs)], "configuration", round_index * count + i) for i in range(count)]
            target = root / "configuration" / str(launch_number) / phase / f"r{round_index}_w{w}_t{t}"
            result = dispatch(target, jobs, code_identity(), settings, deadline, fixed={"workers": w, "threads": t}, control_root=root)
            values = [completed(target, j, code_identity()) for j in jobs]
            measurement = {"workers": w, "threads": t, "completed": result["completed"], "wall_seconds": result["wall_seconds"],
                           "valid": result["completed"] == len(jobs), "round": round_index,
                           "job_seconds": [v.get("worker_seconds", v["seconds"]) for v in values if v is not None]}
            measurements.append(measurement)
            atomic_json(root / "configuration" / str(launch_number) / (phase + ".json"), measurements)
            if not measurement["valid"]:
                raise RuntimeError("configuration test incomplete; scientific dispatch refused")
    return measurements


def validate_spec(spec, settings):
    if spec["code_hash"] != code_identity():
        raise RuntimeError("frozen specification source hash mismatch")
    if settings["profile"] == "x2" and (platform.node().lower() != "yotko-evo-x2" or platform.system() != "Linux"):
        raise RuntimeError("X2 profile must run on the declared X2 machine")
    if not 1 <= settings["workers"] <= settings["caps"]["configuration"] or settings["threads"] not in (1, 2):
        raise ValueError("invalid launch worker/thread count")
    if settings["cpu_budget"] > available_cpus():
        raise ValueError("CPU budget exceeds process availability")
    phases = spec.get("phases", sorted({j["config"].get("phase", j["kind"]) for j in spec["jobs"]}))
    if len(set(phases)) != len(phases) or any(j["config"].get("phase", j["kind"]) not in phases for j in spec["jobs"]):
        raise ValueError("jobs must be assigned to exactly one phase")
    if "configuration" in spec and set(spec["configuration"]) != set(phases):
        raise ValueError("each phase needs its configuration test")
    if spec.get("tag") == "pilot" and (spec["registered"] or spec["wall_seconds"] > 10800):
        raise ValueError("pilot must be non-registered and at most three hours")
    if len({j["id"] for j in spec["jobs"]}) != len(spec["jobs"]):
        raise ValueError("duplicate job identifiers")
    if len({j["seed"] for j in spec["jobs"]}) != len(spec["jobs"]):
        raise ValueError("seed collision in frozen manifest")
    for job in spec["jobs"]:
        if stable_job(job["kind"], job["config"], job["tag"], job["index"]) != job:
            raise ValueError("job or scheduling-independent seed was changed")
        if spec["registered"] and job["tag"] not in ("v3_rerun", "v3_tables", "v3_calibration"):
            raise ValueError("registered batch contains pilot or validation jobs")
    if spec["registered"]:
        verify_registration(spec.get("registration"))
        from .calibration import validate_calibration
        from .production_tables import ProductionTables
        calibrated, loaded = {}, set()
        for job in spec["jobs"]:
            if job["kind"] in ("table", "rerun"):
                config = job["config"]
                if not config.get("calibration_path"):
                    raise RuntimeError("registered jobs need frozen calibration")
                cal_path = config["calibration_path"]
                if cal_path not in calibrated:
                    calibrated[cal_path] = read(SIMULATION / cal_path)
                    validate_calibration(calibrated[cal_path], registered=True)
                calibration = calibrated[cal_path]
                if job["kind"] == "rerun":
                    if not config.get("tables_path"):
                        raise RuntimeError("registered reruns reject fixture tables")
                    identity = (config["tables_path"], calibration["sha256"])
                    if identity not in loaded:
                        ProductionTables(SIMULATION / identity[0], calibration_hash=identity[1], registered=True)
                        loaded.add(identity)


def launch(spec_path, root, settings, service_record=None):
    spec = unseal(read(spec_path))
    settings = {**settings, "caps": caps(settings["profile"], settings["cpu_budget"])}
    validate_spec(spec, settings)
    root = scoped(root)
    root.mkdir(parents=True, exist_ok=True)
    if settings["profile"] == "x2":
        if not service_record or service_record.get("down_exit_code") != 0:
            raise RuntimeError("X2 launch requires the active service lease wrapper")
    with lease(root / "runner.lock"):
        identity = {"spec_hash": digest(spec), "code_hash": code_identity()}
        if (root / "identity.json").exists() and read(root / "identity.json") != identity:
            raise RuntimeError("incompatible resumption")
        atomic_json(root / "identity.json", identity)
        if not (root / "control.json").exists():
            atomic_json(root / "control.json", {"mode": settings["mode"], "max_workers": settings["workers"], "stop_dispatch": False, "interrupt_now": False})
        if not (root / "budget.json").exists():
            now = time.time()
            reserve = spec.get("cleanup_reserve_seconds", 180)
            atomic_json(root / "budget.json", {"start_epoch": now, "deadline_epoch": now + spec["wall_seconds"] - reserve,
                                               "overall_deadline_epoch": now + spec["wall_seconds"], "cleanup_reserve_seconds": reserve})
        deadline = read(root / "budget.json")["deadline_epoch"]
        if time.time() >= deadline:
            raise RuntimeError("frozen batch deadline expired; resumption cannot reset it")
        history = read(root / "launches.json") if (root / "launches.json").exists() else []
        record = {"epoch": time.time(), "machine": platform.node(), "settings": settings, "configuration": {}, "service": service_record}
        history.append(record)
        atomic_json(root / "launches.json", history)
        config_deadline = min(deadline, time.time() + spec.get("configuration_seconds", 900))
        try:
            for phase, profile in spec["configuration"].items():
                data = configuration_test(root, phase, profile, settings, config_deadline, len(history))
                record["configuration"][phase] = data
                atomic_json(root / "launches.json", history)
        except BaseException as exc:
            record["configuration_failure"] = repr(exc)
            atomic_json(root / "launches.json", history)
            if spec.get("tag") == "pilot":
                atomic_json(root / "cost_projection.json", {"status": "incomplete", "reason": "configuration test incomplete; scientific dispatch refused"})
            raise
        outcomes = {}
        for phase in spec["phases"]:
            jobs = [j for j in spec["jobs"] if j["config"].get("phase", j["kind"]) == phase]
            result = dispatch(root / phase, jobs, code_identity(), settings, deadline, measurements=record["configuration"][phase],
                              control_root=root, registered=spec["registered"], registration=spec.get("registration"))
            outcomes[phase] = result
            record["outcomes"] = outcomes
            atomic_json(root / "launches.json", history)
            if result["completed"] != len(jobs):
                if spec.get("tag") == "pilot":
                    from .pilot import project_costs
                    atomic_json(root / "cost_projection.json", project_costs(spec, root, outcomes, record["configuration"]))
                return {"complete": False, "outcomes": outcomes}
        publication = spec.get("publication")
        if publication:
            outputs = [completed(root / j["config"].get("phase", j["kind"]), j, code_identity()) for j in spec["jobs"]]
            if publication["kind"] == "calibration":
                from .calibration import freeze
                freeze([o["result"] for o in outputs], SIMULATION / publication["path"], registered=spec["registered"])
            elif publication["kind"] == "tables":
                from .study import assemble_tables
                assemble_tables(outputs, read(SIMULATION / publication["calibration_path"]), SIMULATION / publication["path"], registered=spec["registered"])
            else:
                raise ValueError("unknown publication kind")
        record["complete"] = True
        record["finished_epoch"] = time.time()
        atomic_json(root / "launches.json", history)
        if spec.get("tag") == "pilot":
            from .pilot import project_costs
            atomic_json(root / "cost_projection.json", project_costs(spec, root, outcomes, record["configuration"]))
        return {"complete": True, "outcomes": outcomes}


def conformance():
    from tempfile import TemporaryDirectory
    assert caps("x2", 32) == {"normal": 31, "work": 28, "configuration": 32}
    data = [{"workers": 8, "threads": 1, "valid": True, "completed": 10, "wall_seconds": 10},
            {"workers": 12, "threads": 1, "valid": True, "completed": 10, "wall_seconds": 9.8}]
    assert choose(data, 31, 32)["workers"] == 8
    job = stable_job("fixture", {}, "validation", 0)
    with TemporaryDirectory(dir=ROOT, prefix="runner_validation_") as name:
        root = Path(name)
        output = {"job": job, "code_hash": "validation", "result": {"seed": job["seed"]}}
        path = root / "outputs" / (job["id"] + ".json")
        atomic_json(path, output)
        assert completed(root, job, "validation") is None
        atomic_json(root / "records" / (job["id"] + ".json"), {"job": job, "code_hash": "validation", "status": "complete", "output_hash": file_hash(path)})
        assert completed(root, job, "validation") == output
    return {"validated": True, "scope": "mechanical contract; process integration tested separately"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    p = commands.add_parser("launch")
    p.add_argument("spec"); p.add_argument("root")
    p.add_argument("--profile", choices=("local", "x2"), required=True)
    p.add_argument("--workers", type=int, required=True)
    p.add_argument("--threads", type=int, choices=(1, 2), required=True)
    p.add_argument("--cpu-budget", type=int, required=True)
    p.add_argument("--mode", choices=("normal", "work"), default="normal")
    p = commands.add_parser("control")
    p.add_argument("root"); p.add_argument("--mode", choices=("normal", "work"))
    p.add_argument("--max-workers", type=int); p.add_argument("--stop", choices=("drain", "now", "clear"))
    p = commands.add_parser("status"); p.add_argument("root")
    args = parser.parse_args()
    if args.command == "launch":
        settings = {k: getattr(args, k) for k in ("profile", "workers", "threads", "cpu_budget", "mode")}
        configure_threads(args.threads)
        if args.profile == "x2":
            from .service import run_with_service
            result = run_with_service(args.spec, args.root, settings)
        else:
            result = launch(args.spec, args.root, settings)
        print(result)
    elif args.command == "control":
        root = scoped(args.root)
        value = read(root / "control.json")
        if args.mode:
            value["mode"] = args.mode
        if args.max_workers is not None:
            if args.max_workers < 1:
                raise ValueError("positive worker limit required")
            value["max_workers"] = args.max_workers
        if args.stop:
            value.update(stop_dispatch=args.stop != "clear", interrupt_now=args.stop == "now")
        atomic_json(root / "control.json", value)
        event(root, "control", value=value)
        print(value)
    else:
        root = scoped(args.root)
        print({"control": read(root / "control.json"), "phases": {p.parent.name: read(p) for p in root.glob("*/status.json")}})


if __name__ == "__main__":
    main()
