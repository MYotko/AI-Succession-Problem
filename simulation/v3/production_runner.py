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


def mem_available_bytes():
    """Available physical memory, cross-platform, or None if unknown."""
    if os.name == "nt":
        class MEMORYSTATUSEX(ctypes.Structure):
            _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                        ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                        ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                        ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                        ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
        status = MEMORYSTATUSEX()
        status.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
        if not ctypes.WinDLL("kernel32", use_last_error=True).GlobalMemoryStatusEx(ctypes.byref(status)):
            return None
        return int(status.ullAvailPhys)
    try:
        with open("/proc/meminfo") as stream:
            for line in stream:
                if line.startswith("MemAvailable:"):
                    return int(line.split()[1]) * 1024
    except OSError:
        pass
    return None


def peak_rss_bytes():
    """Peak resident set size of this process, cross-platform, or None."""
    if os.name == "nt":
        class PROCESS_MEMORY_COUNTERS(ctypes.Structure):
            _fields_ = [("cb", ctypes.c_ulong), ("PageFaultCount", ctypes.c_ulong),
                        ("PeakWorkingSetSize", ctypes.c_size_t), ("WorkingSetSize", ctypes.c_size_t),
                        ("QuotaPeakPagedPoolUsage", ctypes.c_size_t), ("QuotaPagedPoolUsage", ctypes.c_size_t),
                        ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t), ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                        ("PagefileUsage", ctypes.c_size_t), ("PeakPagefileUsage", ctypes.c_size_t)]
        counters = PROCESS_MEMORY_COUNTERS()
        counters.cb = ctypes.sizeof(PROCESS_MEMORY_COUNTERS)
        handle = ctypes.WinDLL("kernel32", use_last_error=True).GetCurrentProcess()
        if not ctypes.WinDLL("psapi", use_last_error=True).GetProcessMemoryInfo(handle, ctypes.byref(counters), counters.cb):
            return None
        return int(counters.PeakWorkingSetSize)
    try:
        import resource
        return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss) * 1024  # ru_maxrss is KB on Linux
    except Exception:
        return None


def lowered_cap(cap, initial_estimate, new_estimate):
    """Lower a fixed worker cap by the estimate ratio when a measured peak raises
    the estimate. Never raises the cap."""
    if cap is None or not initial_estimate or not new_estimate:
        return cap
    return min(cap, max(1, int(cap * initial_estimate / new_estimate)))


def next_memory_cap(original_cap, current_cap, initial_estimate, new_estimate):
    """The phase's memory cap after a measured peak raises its estimate.

    Always derived from the phase's ORIGINAL memory cap, never from an already
    lowered or combined CPU/memory cap, so successive peaks do not compound.
    The result never exceeds the current cap."""
    if current_cap is None:
        return None
    return min(current_cap, lowered_cap(original_cap, initial_estimate, new_estimate))


def memory_worker_cap(estimate_gb, headroom=0.8):
    """floor(headroom * MemAvailable / estimate), or None when unknown."""
    available = mem_available_bytes()
    if not estimate_gb or estimate_gb <= 0 or available is None:
        return None
    return max(1, int(headroom * available / (estimate_gb * 1e9)))


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


def execute(job, registered=False, registration=None, root=None):
    kind, config = job["kind"], job["config"]
    if kind == "a10_cost":
        if registered:
            raise ValueError("A10 cost pilot cannot run registered")
        from .pilot_a10 import execute_cost
        return execute_cost(job)
    if kind in ("a4_fit", "a4_validate", "a4_census"):
        # A4 validated continuation stages. The A4 stream seed travels in the
        # config; the runner's own job seed is unused. root locates the sibling
        # fit phase for a plain validate job.
        from .table_validation_a4 import run_stage_job
        return run_stage_job(job, root)
    if kind == "a5_fvplain":
        # A5 plain-law certification labels. The A5 stream seed travels in the
        # config; the runner's own job seed is unused. A5 needs no sibling phase.
        from .table_labels_a5 import run_stage_job
        return run_stage_job(job, root)
    if kind == "fixture":
        if registered or job["tag"] != "validation":
            raise ValueError("runner fixtures are validation only")
        time.sleep(config.get("seconds", .01))
        return {"seed": job["seed"], "fixture": True}
    if kind == "calibration":
        from .calibration import run_seed
        return run_seed(config, job["seed"], job["tag"])
    if kind == "continuation_audit":
        if registered or job["tag"] not in ("validation", "configuration"):
            raise ValueError("continuation endpoint audit is validation only")
        from .unpublished_bins import replay
        return replay(config)
    calibration = None
    if config.get("calibration_path"):
        declared = config.get("kernel", config.get("model", {})).get("instrument", {})
        if declared.get("mapping") == "A10":
            from .calibration import load_calibration
            calibration = load_calibration(SIMULATION / config["calibration_path"], instrument=declared, registered=registered)
        else:
            calibration = read(SIMULATION / config["calibration_path"])
    if kind == "table":
        from .offline_estimator import estimate
        return estimate(config, job["seed"], calibration)
    if kind != "rerun":
        raise ValueError("unknown job kind")
    from .recording import RecordedV3Model as V3Model, pack_evidence
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
    availability = {"allocation_steps": sum(r["allocation_evaluated"] for r in records),
                    "rule_exclusions_total": sum(r["unavailable_rule_count"] for r in records),
                    "steps_with_rule_exclusions": sum(r["unavailable_rule_count"] > 0 for r in records),
                    "maximum_rules_excluded": max((r["unavailable_rule_count"] for r in records), default=0),
                    "balanced_fallback_steps": sum(r["balanced_fallback"] for r in records),
                    "survival_first_scores_unavailable_steps": sum(r["survival_first_scores_unavailable"] for r in records),
                    "rule_exclusions_by_rule": {rule.rule_id: sum(rule.rule_id in r["unavailable_rules"] for r in records) for rule in model.rules},
                    "unavailable_plans_total": sum(r["yield_unavailable_plan_count"] for r in records),
                    "yield_reviews_held_no_admissible_plan": sum(r["yield_held_no_admissible_plan"] for r in records)}
    extra = {}
    if model.instrument.a10:
        living = [r for r in records if r.get("population_before", 0) > 0]
        count = len(living)
        extra = {"instrument": model.instrument.declaration(), "a10_diagnostics": {
            "living_start_steps": count,
            "mean_theta": sum(r["theta"] for r in living) / count if count else None,
            "theta_one_share": sum(r["theta"] == 1. for r in living) / count if count else None,
            "bandwidth_floor_share": sum(r["bandwidth_at_floor"] for r in living) / count if count else None,
            "transition_count": model.transition_count, "final_capability": model.capability}}
    return pack_evidence({"tag": job["tag"], "fixture_tables": model.tables.fixture, "steps": len(records), **extra,
            "population_path": populations, "population_mean": sum(populations) / max(1, len(populations)),
            "population_max": max(populations, default=0), "final_population": model.population,
            "survived_threshold_30": model.population >= 30, "yield_events": model.yield_events,
            "periods": [p.audit() for p in model.periods], "diagnostics": records,
            "override_records": model.override_records,
            "continuation_availability": availability})


def worker(root_name, job, code, threads, registered, registration, completion_deadline=None):
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
            result = execute(job, registered, registration, root=root)
            output = {"job": job, "code_hash": code, "runtime": info, "result": result,
                      "seconds": time.perf_counter() - before, "started_epoch": started, "finished_epoch": time.time(),
                      "peak_rss_bytes": peak_rss_bytes()}
            if completion_deadline is not None and time.time() >= completion_deadline:
                return
            path = root / "outputs" / (job["id"] + ".json")
            atomic_json(path, output)
            if completion_deadline is not None and time.time() >= completion_deadline:
                return  # An output without a completion record is never counted.
            atomic_json(root / "records" / (job["id"] + ".json"),
                        {"job": job, "code_hash": code, "status": "complete", "output_hash": file_hash(path), "completed_epoch": time.time(),
                         "worker_seconds": time.perf_counter() - before})
    except BaseException:
        atomic_json(root / "failures" / (job["id"] + ".json"), {"job": job, "traceback": traceback.format_exc()})
        raise


def dispatch(root, jobs, code, settings, deadline, *, measurements=None, fixed=None, control_root=None, registered=False, registration=None, completion_screen=None, memory_cap=None, memory_estimate_gb=None, pooled_jobs=None):
    root = scoped(root)
    root.mkdir(parents=True, exist_ok=True)
    control_root = control_root or root
    done = {j["id"] for j in jobs if completed(root, j, code) is not None}
    pending = [j for j in jobs if j["id"] not in done]
    pool_budget, pool_estimates = None, {}
    if pooled_jobs is not None:
        if registered or any(j["kind"] not in ("a10_cost", "fixture") for j in jobs):
            raise ValueError("pooled dispatch is only for non-registered A10 cost jobs or validation fixtures")
        import math
        for job in jobs:
            e = pooled_jobs[job["id"]]
            if any(not math.isfinite(e[k]) or e[k] <= 0 for k in ("memory_gb", "estimated_seconds")):
                raise ValueError("positive finite individual memory and time estimates required")
            pool_estimates[e["memory_class"]] = max(pool_estimates.get(e["memory_class"], 0.), e["memory_gb"])
        available = mem_available_bytes()
        if available is None:
            raise RuntimeError("pooled memory guard requires MemAvailable")
        pool_budget = .8 * available / 1e9
        event(root, "pooled_memory_budget", budget_gb=pool_budget, headroom=.8, worker_ceiling=16)
        # Retain observed peaks across an interrupted resume.
        prior = read(root / "pool_memory.json") if (root / "pool_memory.json").exists() else {}
        for key in pool_estimates:
            pool_estimates[key] = max(pool_estimates[key], prior.get(key, 0.))
    def job_memory(job):
        e = pooled_jobs[job["id"]]
        return max(e["memory_gb"], pool_estimates[e["memory_class"]])
    # The memory cap is fixed once, at phase start, from the estimate the caller
    # (launch) computed against MemAvailable before any of this phase's tasks
    # ran. It is NOT recomputed from live MemAvailable, which already excludes
    # running tasks and would double-count them. It only falls when a measured
    # peak raises the estimate, by the same ratio. Live pressure is left to the
    # 1.2x guard. memory_hold events are rate-limited.
    memory_estimate = [memory_estimate_gb]
    initial_estimate = memory_estimate_gb
    memory_cap_state = [memory_cap]
    if memory_cap is not None:
        event(root, "memory_cap", cap=memory_cap, estimate_gb=memory_estimate_gb)
    last_memory_hold = [0.0]
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
    if pooled_jobs is not None and not pending:
        control = read(control_root / "control.json")
        last_mode = control["mode"]
        limit = min(16, settings["caps"][last_mode], settings["workers"], control.get("max_workers", settings["workers"]))
        last_selection = fixed or choose(measurements, limit, settings["cpu_budget"], settings["threads"])
    def publish():
        atomic_json(root / "active.json", {"machine": platform.node(), "pids": [p.pid for p, _, _ in active.values()]})
        status = {"total": len(jobs), "completed": len(done), "running": len(active),
                  "pending": len(jobs) - len(done) - len(active), "maximum_active": maximum,
                  "reason": reason, "deadline_epoch": deadline, "mode": last_mode, "selection": last_selection}
        if pooled_jobs is not None:
            status.update(memory_budget_gb=pool_budget, memory_estimates_gb=pool_estimates,
                          not_completed_ids=[j["id"] for j in jobs if j["id"] not in done])
            atomic_json(root / "job_status.json", {j["id"]: "complete" if j["id"] in done else "not completed" for j in jobs})
        atomic_json(root / "status.json", status)
        return status
    def stop(reason):
        for process, job, _ in active.values():
            if process.is_alive():
                a4 = job["kind"].startswith(("a4_", "a5_"))
                event(root, "restart_required", job=job["id"], runner_seed_unused=a4,
                      **({} if a4 else {"original_seed": job["seed"]}), reason=reason)
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
    def check(job):
        failure = completion_screen(job, completed(root, job, code)) if completion_screen else None
        if failure:
            atomic_json(root / "screen_failure.json", {"epoch": time.time(), "job": job["id"], "failure": failure})
            event(root, "screen_failure", job=job["id"], failure=failure)
        return bool(failure)
    try:
        failed = (root / "screen_failure.json").exists()
        if not failed:
            failed = any(check(j) for j in jobs if j["id"] in done)
        if failed:
            reason = "screen_failure"
            return {**publish(), "wall_seconds": time.perf_counter() - start}
        while pending or active:
            if completion_screen and getattr(completion_screen, 'family_failed', lambda: False)():
                reason = 'screen_failure'
                stop(reason)
                active.clear()
                break
            control = read(control_root / "control.json")
            mode = control["mode"]
            if mode not in ("normal", "work"):
                raise ValueError("invalid live mode")
            cap = settings["caps"][mode]
            maximum_request = min(settings["workers"], control.get("max_workers", settings["workers"]))
            if pooled_jobs is not None:
                maximum_request = min(maximum_request, 16)
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
                    output = completed(root, job, code)
                    if output is None:
                        attempts[key] = attempts.get(key, 0) + 1
                        atomic_json(attempts_path, attempts)
                        event(root, "restart", job=key, attempt=attempts[key], runner_seed_unused=job["kind"].startswith(("a4_", "a5_")),
                              **({} if job["kind"].startswith(("a4_", "a5_")) else {"seed": job["seed"]}))
                        if attempts[key] >= 3:
                            raise RuntimeError("job failed three times; inspect durable failure")
                        pending.insert(0, job)
                    else:
                        done.add(key)
                        event(root, "complete", job=key, pid=process.pid)
                        # Raise the memory estimate if a completed task's peak RSS
                        # exceeded it; this only lowers the derived worker cap.
                        peak = output.get("peak_rss_bytes")
                        if pooled_jobs is not None and peak and peak / 1e9 > job_memory(job):
                            key = pooled_jobs[job["id"]]["memory_class"]
                            pool_estimates[key] = peak / 1e9
                            atomic_json(root / "pool_memory.json", pool_estimates)
                            event(root, "pooled_memory_estimate_raised", memory_class=key, estimate_gb=peak / 1e9, job=job["id"])
                        if peak and memory_estimate[0] and peak > memory_estimate[0] * 1e9:
                            memory_estimate[0] = peak / 1e9
                            memory_cap_state[0] = next_memory_cap(memory_cap, memory_cap_state[0], initial_estimate, memory_estimate[0])
                            event(root, "memory_estimate_raised", estimate_gb=round(memory_estimate[0], 2), cap=memory_cap_state[0], job=key)
                        if check(job):
                            reason = "screen_failure"
                            stop(reason)
                            active.clear()
                            break
            if reason == "screen_failure":
                break
            effective_limit = min(cap, selected["workers"])
            if pooled_jobs is not None:
                effective_limit = min(effective_limit, 16)
            if memory_cap_state[0] is not None:
                effective_limit = min(effective_limit, max(1, memory_cap_state[0]))
            if len(active) <= effective_limit and mode_effective != mode:
                mode_effective = mode
                event(root, "mode_effective", mode=mode, active=len(active), worker_limit=effective_limit)
            slots = sum(t for _, _, t in active.values())
            while pending and not control.get("stop_dispatch") and len(active) < effective_limit and slots + selected["threads"] <= settings["cpu_budget"]:
                if pooled_jobs is not None:
                    pending.sort(key=lambda j: (-pooled_jobs[j["id"]]["estimated_seconds"], j["id"]))
                    reserved = sum(job_memory(j) for _, j, _ in active.values())
                    available = mem_available_bytes()
                    index = next((i for i, j in enumerate(pending)
                                  if reserved + job_memory(j) <= pool_budget
                                  and (available is not None and available >= 1.2 * job_memory(j) * 1e9)), None)
                    if index is None:
                        if not active:
                            raise RuntimeError("pooled memory guard: no pending job fits available memory")
                        if time.monotonic() - last_memory_hold[0] >= 60:
                            event(root, "pooled_memory_hold", reserved_gb=reserved, budget_gb=pool_budget, active=len(active))
                            last_memory_hold[0] = time.monotonic()
                        break
                    pending.insert(0, pending.pop(index))
                # Live memory guard: do not start a task while MemAvailable is
                # below 1.2 times its estimate. Halt if it holds with nothing
                # active (no task will ever free enough memory). Rate-limit the
                # event to at most once per minute.
                if memory_estimate[0]:
                    available = mem_available_bytes()
                    if available is not None and available < 1.2 * memory_estimate[0] * 1e9:
                        if not active:
                            raise RuntimeError("memory guard: MemAvailable %.1f GB below 1.2x estimate %.1f GB with no active task"
                                               % (available / 1e9, memory_estimate[0]))
                        if time.monotonic() - last_memory_hold[0] >= 60:
                            event(root, "memory_hold", estimate_gb=memory_estimate[0], available_gb=round(available / 1e9, 1), active=len(active))
                            last_memory_hold[0] = time.monotonic()
                        break
                job = pending.pop(0)
                if attempts.get(job["id"], 0) >= 3:
                    raise RuntimeError("job has exhausted retries")
                args = (str(root), job, code, selected["threads"], registered, registration)
                process = context.Process(target=worker, args=args + ((deadline,) if pooled_jobs is not None else ()))
                process.start()
                active[job["id"]] = (process, job, selected["threads"])
                slots += selected["threads"]
                maximum = max(maximum, len(active))
                # A4 and A5 stages ignore the runner's job seed (the stream seed
                # travels in the config); label it so the event is not misread.
                is_a4 = job["kind"].startswith(("a4_", "a5_"))
                event(root, "dispatch", job=job["id"], runner_seed_unused=is_a4,
                      **({} if is_a4 else {"seed": job["seed"]}),
                      pid=process.pid, active=len(active), slots=slots, mode=mode,
                      **({"memory_estimate_gb": job_memory(job), "memory_budget_gb": pool_budget,
                          "reserved_memory_gb": sum(job_memory(j) for _, j, _ in active.values()),
                          "estimated_seconds": pooled_jobs[job["id"]]["estimated_seconds"]} if pooled_jobs is not None else {}))
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


def nondeterminism_check(phase_root, jobs, registered=False, registration=None):
    """Re-execute one completed task in a fresh spawned worker and compare its
    result hash. The task is chosen by a recorded seeded draw among the phase's
    shortest tasks (by count x length), so the recheck fits the deadline. A
    mismatch halts; the result is recorded durably. The recompute uses the same
    spawned worker path (with configure_threads) as the original, since
    bit-identity holds within that path but not across process-launch modes.
    A4 stage results carry no wall time, so the digest is deterministic."""
    phase_root = scoped(phase_root)
    code = code_identity()
    done = [j for j in jobs if completed(phase_root, j, code) is not None]
    if not done:
        result = {"checked": None, "reason": "no completed task"}
        atomic_json(phase_root / "nondeterminism_check.json", result)
        return result

    def cost(job):
        # Genuinely short task = smallest population x length, from the job's
        # actual (registered) A1 settings, with any smoke override applied.
        c = job["config"]
        s = (c.get("a1_job") or {}).get("config", {}).get("settings") or {}
        per_group = s.get("particles" if c.get("route") == "fv" else "runs_per_group", 1)
        length = 519 if c.get("stage") == "census" else s.get("burn", 0) + s.get("measure", 0)
        ov = c.get("settings_override") or {}
        if ov:
            length = ov.get("census_measure", length) if c.get("stage") == "census" else ov.get("burn", 0) + ov.get("measure", 0)
        return per_group * length
    ranked = sorted(done, key=lambda j: (cost(j), j["id"]))
    shortest = [j for j in ranked if cost(j) == cost(ranked[0])] or ranked
    draw = int(digest(["A4-nondeterminism", phase_root.name, sorted(j["id"] for j in shortest)]), 16)
    job = shortest[draw % len(shortest)]
    # A sibling of the phase dirs, so a plain validate recompute still finds its
    # fit phase at temp.parent/"fit".
    temp = phase_root.parent / ("_nd_" + phase_root.name)
    process = mp.get_context("spawn").Process(target=worker, args=(str(temp), job, code, 1, registered, registration))
    process.start()
    process.join()
    fresh = completed(temp, job, code)
    original = completed(phase_root, job, code)
    if fresh is None or digest(fresh["result"]) != digest(original["result"]):
        atomic_json(phase_root / "nondeterminism_failure.json", {"epoch": time.time(), "job": job["id"], "recomputed": fresh is not None})
        raise RuntimeError("A4 nondeterminism: re-executed task %s differs" % job["id"])
    result = {"checked": job["id"], "candidates": len(shortest), "matched": True}
    atomic_json(phase_root / "nondeterminism_check.json", result)
    return result


def a4_projection(spec, configuration, effective_workers, run_root, code, from_index, now, deadline):
    """Project wall time for the REMAINING work from ``from_index`` onward.

    Counts only jobs without a valid completed() record, skips finished phases,
    and scales each job by its own population x length (not the phase maximum)
    from the per-cell config rate. For validate_plain the config task is
    self-contained (fit + validate), so the fit config time is subtracted. The
    worker count per phase is min(mode cap, chosen workers, memory cap), passed
    in ``effective_workers``. One nondeterminism recheck (the shortest remaining
    task) is added per remaining phase. The cleanup reserve is NOT added: the
    budget deadline already subtracts it. ``fits`` is whether the total fits the
    remaining budget."""
    GROUPS = 32

    def median(name):
        s = sorted(x for m in configuration.get(name, []) for x in m.get("job_seconds", []))
        return s[len(s) // 2] if s else 0.0

    def cells(route, per_group, length):
        return GROUPS * per_group * length

    total, detail = 0.0, {}
    for phase in spec["phases"][from_index:]:
        jobs = [j for j in spec["jobs"] if j["config"]["phase"] == phase]
        pending = [j for j in jobs if completed(run_root / phase, j, code) is None] if run_root is not None else jobs
        if not pending:
            detail[phase] = {"remaining": 0, "wall_seconds": 0.0}
            continue
        task_short = median(phase)
        if phase == "validate_plain":
            task_short = max(0.0, task_short - median("fit"))
        cfg = spec["configuration"][phase]["config"]
        override = cfg.get("settings_override", {})
        rep = cfg["a1_job"]["config"]["settings"]
        rep_per_group = rep["particles"] if cfg["route"] == "fv" else rep["runs_per_group"]
        short_len = override.get("census_measure", 44) if phase == "census" else override.get("burn", 8) + override.get("measure", 24)
        config_cells = cells(cfg["route"], rep_per_group, short_len)
        rate = task_short / config_cells if config_cells else 0.0
        workers = max(1, effective_workers.get(phase, 1))
        per_job = []
        for j in pending:
            s = j["config"]["a1_job"]["config"]["settings"]
            route = j["config"]["route"]
            per_group = s["particles"] if route == "fv" else s["runs_per_group"]
            full_len = 519 if phase == "census" else s["burn"] + s["measure"]
            per_job.append(rate * cells(route, per_group, full_len))
        wall = sum(per_job) / workers + (min(per_job) if per_job else 0.0)  # throughput + one recheck
        detail[phase] = {"remaining": len(pending), "workers": workers, "task_short_seconds": task_short,
                         "per_cell_rate": rate, "wall_seconds": wall}
        total += wall
    remaining = deadline - now
    return {"total_seconds": total, "remaining_budget_seconds": remaining, "phases": detail, "fits": total <= remaining}


def configuration_candidates(candidates, memory_cap=None):
    """Worker counts to test. A worker count above a phase's memory cap can never
    be dispatched, so an A4 memory-capped phase tests the listed counts up to its
    cap, plus the cap itself (operator, 2026-09-29). Uncapped phases are unchanged."""
    if memory_cap is None or memory_cap >= max(candidates):
        return list(candidates)
    cap = max(1, int(memory_cap))
    return sorted({w for w in candidates if w <= cap} | {cap})


def configuration_job_count(profile, workers, x2):
    """Jobs per configuration round: the profile's fixed count, or, when the
    profile sets ``jobs_per_worker``, that many per tested worker (two waves)."""
    if profile.get("jobs_per_worker"):
        return max(workers, profile["jobs_per_worker"] * workers)
    return profile["jobs_x2"] if x2 else profile["jobs_local"]


def configuration_test(root, phase, profile, settings, deadline, launch_number, memory_cap=None):
    listed = profile["workers_x2"] if settings["profile"] == "x2" else profile["workers_local"]
    if settings["profile"] == "x2" and not {8, 12, 16, 24, 32}.issubset(listed):
        raise ValueError("missing required X2 configuration candidates")
    pooled = profile.get("pooled_estimates_by_stratum")
    candidates = configuration_candidates(listed, min(16, settings["caps"]["configuration"]) if pooled is not None else memory_cap)
    if settings["threads"] == 2 and not profile.get("material_multithreaded_numerics"):
        raise ValueError("two threads require profiling evidence")
    pairs = [(w, t) for t in profile.get("threads", [1]) for w in candidates if w <= settings["caps"]["configuration"] and w * t <= settings["cpu_budget"] and t <= settings["threads"]]
    measurements = []
    for round_index in range(profile.get("rounds", 2)):
        for w, t in pairs if round_index % 2 == 0 else reversed(pairs):
            count = configuration_job_count(profile, w, settings["profile"] == "x2")
            if count < w:
                raise ValueError("configuration work must occupy every tested worker")
            configs = profile.get("configs", [profile["config"]])
            jobs = [stable_job(profile["kind"], configs[i % len(configs)], "configuration", round_index * count + i) for i in range(count)]
            target = root / "configuration" / str(launch_number) / phase / f"r{round_index}_w{w}_t{t}"
            extra = {"pooled_jobs": {j["id"]: pooled[j["config"]["phase"]] for j in jobs}} if pooled is not None else {}
            result = dispatch(target, jobs, code_identity(), settings, deadline, fixed={"workers": w, "threads": t}, control_root=root, **extra)
            values = [completed(target, j, code_identity()) for j in jobs]
            measurement = {"workers": w, "threads": t, "completed": result["completed"], "wall_seconds": result["wall_seconds"],
                           "valid": result["completed"] == len(jobs), "round": round_index,
                           "job_seconds": [v.get("worker_seconds", v["seconds"]) for v in values if v is not None]}
            if pooled is not None:
                measurement.update(memory_budget_gb=result["memory_budget_gb"],
                                   memory_estimates_gb=result["memory_estimates_gb"], maximum_active=result["maximum_active"])
            measurements.append(measurement)
            atomic_json(root / "configuration" / str(launch_number) / (phase + ".json"), measurements)
            if not measurement["valid"]:
                raise RuntimeError("configuration test incomplete; scientific dispatch refused")
    return measurements


class ContextPreflightError(ValueError):
    """All context failures from a simulation-free launch preflight."""
    def __init__(self, report):
        self.report = report
        failures = [r for r in report["contexts"] if r["status"] == "failed"]
        super().__init__("A10 context preflight failed (%d contexts):\n%s" % (len(failures), "\n".join(
            "%s calibration=%s kernel=%s: %s" % (", ".join(r["uses"]), r["calibration_path"], r["kernel"], r["error"])
            for r in failures)))


def preflight_contexts(spec):
    """Build each distinct A10 context, including configuration jobs, without a trajectory."""
    from .context import Context
    from .calibration import load_calibration
    from .instrument import declaration
    requests = {}
    required = (spec.get("registered_a10") or spec.get("instrument", {}).get("mapping") == "A10"
                or spec.get("schema") == "v3-A10-cost-pilot-1")

    def collect(kind, config, use):
        toy = kind == "a10_cost" and config.get("toy", False)
        if kind == "a10_cost":
            wrapped = config["source_job"]
            kind, config = wrapped["kind"], wrapped["config"]
        if "a1_job" in config:
            config = config["a1_job"]["config"]
        if "kernel" in config:
            kernel = dict(config["kernel"])
            if toy:
                kernel.update(n_agents=16, carrying_capacity=160)
        elif "model" in config:
            kernel = dict(config["model"])
            if toy:
                kernel.update(n_agents=8, carrying_capacity=80)
        else:
            return
        inst = kernel.get("instrument")
        if not required and (inst is None or inst.get("mapping") == "R4"):
            return
        path = str((SIMULATION / config["calibration_path"]).resolve()) if config.get("calibration_path") else None
        key = digest({"calibration_path": path, "kernel": kernel, "instrument": inst})
        entry = requests.setdefault(key, {"key": key, "calibration_path": path, "kernel": kernel,
                                         "instrument": inst, "uses": [], "families": []})
        entry["uses"].append(use)
        if config.get("a10_family") and config["a10_family"] not in entry["families"]:
            entry["families"].append(config["a10_family"])

    for job in spec.get("jobs", []):
        collect(job["kind"], job["config"], "sample:" + job["id"])
    for phase, profile in spec.get("configuration", {}).items():
        for i, config in enumerate(profile.get("configs", [profile.get("config", {})])):
            collect(profile["kind"], config, "configuration:%s:%d" % (phase, i))
    contexts, loaded = [], {}
    for entry in requests.values():
        row = dict(entry)
        try:
            instrument = declaration(entry["instrument"])
            if required and not instrument.a10:
                raise ValueError("A10 launch context lacks an A10 instrument declaration")
            if entry["kernel"].get("successor_capability") is not None and instrument.a10:
                instrument.require_capability(entry["kernel"]["successor_capability"])
            path = entry["calibration_path"]
            if spec.get("registered") and path is None:
                raise ValueError("registered A10 context requires a calibration path")
            cal_key = (path, digest(instrument.declaration()))
            if cal_key not in loaded:
                try:
                    loaded[cal_key] = load_calibration(path, instrument=instrument, registered=spec.get("registered", False)) if path else None
                except Exception as exc:
                    loaded[cal_key] = exc
            if isinstance(loaded[cal_key], Exception):
                raise loaded[cal_key]
            context = Context.build(entry["kernel"], loaded[cal_key])
            row.update(status="passed", calibration_sha256=context.calibration_hash)
        except Exception as exc:
            row.update(status="failed", error="%s: %s" % (type(exc).__name__, exc))
        contexts.append(row)
    failures = sum(r["status"] == "failed" for r in contexts)
    report = {"schema": "v3-A10-context-preflight-1", "simulation": False, "checked": len(contexts),
              "failed": failures, "status": "failed" if failures else "passed", "contexts": contexts}
    if failures:
        raise ContextPreflightError(report)
    return report


def validate_spec(spec, settings):
    from .instrument import declaration
    from .pilot_a10 import reduced_pilot, POOLED_PHASE
    pooled = reduced_pilot(spec)
    instrument = declaration(spec.get("instrument"))
    if spec.get("registered_a10") and not instrument.a10:
        raise ValueError("registered A10 manifest refuses R4")
    if spec["code_hash"] != code_identity():
        raise RuntimeError("frozen specification source hash mismatch")
    if 'repair' in spec:
        from .table_compatibility_a3 import validate_plan
        validate_plan(spec)
    elif spec.get('completion_screen'):
        raise ValueError('completion screen is reserved for the frozen A3 manifest')
    if settings["profile"] == "x2" and (platform.node().lower() != "yotko-evo-x2" or platform.system() != "Linux"):
        raise RuntimeError("X2 profile must run on the declared X2 machine")
    if not 1 <= settings["workers"] <= settings["caps"]["configuration"] or settings["threads"] not in (1, 2):
        raise ValueError("invalid launch worker/thread count")
    if settings["cpu_budget"] > available_cpus():
        raise ValueError("CPU budget exceeds process availability")
    phases = spec.get("phases", sorted({j["config"].get("phase", j["kind"]) for j in spec["jobs"]}))
    job_phases = spec["strata"] if pooled else phases
    if len(set(phases)) != len(phases) or any(j["config"].get("phase", j["kind"]) not in job_phases for j in spec["jobs"]):
        raise ValueError("jobs must be assigned to exactly one phase")
    if "configuration" in spec and set(spec["configuration"]) != set(phases):
        raise ValueError("each phase needs its configuration test")
    if pooled:
        if (spec.get("registered") or spec.get("registered_a10") or spec.get("tag") != "pilot"
                or spec.get("results_eligible") is not False or phases != [POOLED_PHASE]
                or spec.get("publication") or set(spec["pooled_job_estimates"]) != {j["id"] for j in spec["jobs"]}
                or any(j["kind"] != "a10_cost" or j["tag"] != "pilot" or j["config"].get("configuration_test") for j in spec["jobs"])):
            raise ValueError("reduced A10 pilot requires only non-registered cost samples in one pooled queue")
        profile = spec["configuration"][POOLED_PHASE]
        expected = {j["config"]["phase"]: spec["pooled_job_estimates"][j["id"]] for j in spec["jobs"]}
        if (profile.get("kind") != "a10_cost" or profile.get("pooled_estimates_by_stratum") != expected
                or settings["threads"] != 1 or any(j["config"]["toy"] != spec["toy"] for j in spec["jobs"])):
            raise ValueError("reduced A10 requires its individual memory estimates, one thread, and declared toy status")
        if not spec["toy"]:
            from .offline_estimator import settings_for
            for job in spec["jobs"]:
                source = job["config"]["source_job"]["config"]
                if job["config"]["cost_kind"] != "run" and source["settings"] != settings_for(source["setting_name"]):
                    raise ValueError("P2 table jobs require full declared settings")
    elif any("pooled_estimates_by_stratum" in p for p in spec.get("configuration", {}).values()):
        raise ValueError("pooled configuration is reserved for the reduced A10 cost pilot")
    if spec.get("tag") == "pilot" and (spec["registered"] or not 0 < spec["wall_seconds"] <= (43200 if pooled else 10800)):
        raise ValueError("pilot must be non-registered and at most twelve hours for reduced A10, otherwise three hours")
    if len({j["id"] for j in spec["jobs"]}) != len(spec["jobs"]):
        raise ValueError("duplicate job identifiers")
    if len({j["seed"] for j in spec["jobs"]}) != len(spec["jobs"]):
        raise ValueError("seed collision in frozen manifest")
    for job in spec["jobs"]:
        if stable_job(job["kind"], job["config"], job["tag"], job["index"]) != job:
            raise ValueError("job or scheduling-independent seed was changed")
        if spec.get("registered_a10"):
            jc = job["config"]
            source = jc.get("a1_job", {}).get("config", jc)
            ji = source.get("model", source.get("kernel", {})).get("instrument")
            if not declaration(ji).a10:
                raise ValueError("registered A10 job lacks its instrument declaration")
        if spec["registered"] and job["tag"] not in ("v3_rerun", "v3_tables", "v3_calibration"):
            raise ValueError("registered batch contains pilot or validation jobs")
    preflight = preflight_contexts(spec)
    if spec["registered"]:
        verify_registration(spec.get("registration"), **({"instrument": instrument} if instrument.a10 else {}))
        from .calibration import validate_calibration
        from .production_tables import ProductionTables
        calibrated, loaded = {}, set()
        for job in spec["jobs"]:
            if job["kind"] in ("a4_fit", "a4_validate", "a4_census", "a5_fvplain"):
                # A4 and A5 stages carry their calibration through the referenced
                # A1 job.
                cal_path = job["config"]["a1_job"]["config"].get("calibration_path")
                if not cal_path:
                    raise RuntimeError("registered A4 jobs need frozen calibration")
                if cal_path not in calibrated:
                    calibrated[cal_path] = read(SIMULATION / cal_path)
                    validate_calibration(calibrated[cal_path], registered=True, **({"instrument": instrument} if instrument.a10 else {}))
                continue
            if job["kind"] in ("table", "rerun"):
                config = job["config"]
                if not config.get("calibration_path"):
                    raise RuntimeError("registered jobs need frozen calibration")
                cal_path = config["calibration_path"]
                if cal_path not in calibrated:
                    calibrated[cal_path] = read(SIMULATION / cal_path)
                    validate_calibration(calibrated[cal_path], registered=True, **({"instrument": instrument} if instrument.a10 else {}))
                calibration = calibrated[cal_path]
                if job["kind"] == "rerun":
                    if not config.get("tables_path"):
                        raise RuntimeError("registered reruns reject fixture tables")
                    identity = (config["tables_path"], calibration["sha256"])
                    if identity not in loaded:
                        table = ProductionTables(SIMULATION / identity[0], calibration_hash=identity[1], registered=True)
                        if instrument.a10:
                            table.require_a10(declaration(config["model"].get("instrument")))
                        loaded.add(identity)
    return preflight


def preflight_completion(spec, root):
    """Refuse a failed family before configuration work or service changes."""
    if not spec.get('completion_screen'):
        return None
    from .table_repair_a3 import completion_screen
    from .table_compatibility_a3 import (validate_plan, family_directory, refuse_family_failure,
                                         record_family_failure)
    p = validate_plan(spec)
    refuse_family_failure(p)
    root = scoped(root)
    family = family_directory(p)
    with lease(family / 'preflight.lock'):
        refuse_family_failure(p)
        registry = family / 'roots.json'
        roots = read(registry) if registry.exists() else []
        name = str(root.resolve())
        if name not in roots:
            roots.append(name)
            atomic_json(registry, roots)
        screen = completion_screen(spec, root)
        for name in roots:
            phase = Path(name) / 'table'
            if (phase / 'screen_failure.json').exists():
                record_family_failure(p, read(phase / 'screen_failure.json'), name)
                refuse_family_failure(p)
            for job in spec['jobs']:
                output = completed(phase, job, spec['code_hash'])
                if output is not None and screen(job, output):
                    refuse_family_failure(p)
        return screen


def launch(spec_path, root, settings, service_record=None):
    spec = unseal(read(spec_path))
    settings = {**settings, "caps": caps(settings["profile"], settings["cpu_budget"])}
    try:
        context_preflight = validate_spec(spec, settings)
    except ContextPreflightError as exc:
        atomic_json(scoped(root) / "context_preflight.json", exc.report)
        raise
    screen = preflight_completion(spec, root)
    root = scoped(root)
    root.mkdir(parents=True, exist_ok=True)
    if context_preflight and context_preflight["checked"]:
        atomic_json(root / "context_preflight.json", context_preflight)
    if settings["profile"] == "x2":
        if not service_record or service_record.get("down_exit_code") != 0:
            raise RuntimeError("X2 launch requires the active service lease wrapper")
    with lease(root / "runner.lock"):
        if any(root.glob('*/screen_failure.json')):
            raise RuntimeError('A3 screen failure is latched; no resumption or configuration dispatch')
        identity = {"spec_hash": digest(spec), "code_hash": code_identity()}
        if (root / "identity.json").exists() and read(root / "identity.json") != identity:
            raise RuntimeError("incompatible resumption")
        atomic_json(root / "identity.json", identity)
        atomic_json(root / "manifest.json", seal(spec))
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
        # A4 validation and A5 labels are both staged plans with per-phase memory
        # caps, resume-aware projection and a per-phase nondeterminism recheck.
        is_a4 = spec.get("schema") in ("v3-A4-validation-1", "v3-A5-labels-1")
        is_a10_pilot = spec.get("schema") == "v3-A10-cost-pilot-1"
        from .pilot_a10 import reduced_pilot
        pooled = reduced_pilot(spec)
        memory_managed = is_a4 or is_a10_pilot or spec.get("schema") == "v3-A10-estimation-1"
        # Memory caps come first, measured before any task runs, so a capped
        # phase's configuration test never tries a worker count it cannot use.
        mem_caps = {p: memory_worker_cap(spec.get("memory_estimate_gb", {}).get(p)) for p in spec["phases"]} if memory_managed else {}
        if memory_managed:
            record["memory_caps"] = mem_caps
            atomic_json(root / "launches.json", history)
        try:
            for phase, profile in spec["configuration"].items():
                data = configuration_test(root, phase, profile, settings, config_deadline, len(history),
                                          memory_cap=mem_caps.get(phase) if memory_managed else None)
                record["configuration"][phase] = data
                atomic_json(root / "launches.json", history)
        except BaseException as exc:
            record["configuration_failure"] = repr(exc)
            atomic_json(root / "launches.json", history)
            if spec.get("tag") == "pilot":
                atomic_json(root / "cost_projection.json", {"status": "incomplete", "reason": "configuration test incomplete; scientific dispatch refused"})
            if pooled:
                atomic_json(root / "pooled" / "job_status.json", {j["id"]: "complete" if completed(root / "pooled", j, code_identity()) else "not completed" for j in spec["jobs"]})
            raise
        outcomes = {}
        effective_workers = {}
        if is_a4:
            mode_cap = settings["caps"][settings["mode"]]
            for phase in spec["phases"]:
                try:
                    chosen = choose(record["configuration"][phase], min(mode_cap, settings["workers"]), settings["cpu_budget"], settings["threads"])["workers"]
                except Exception:
                    chosen = mode_cap
                effective_workers[phase] = max(1, min(mode_cap, settings["workers"], chosen, mem_caps.get(phase) or mode_cap))
        for index, phase in enumerate(spec["phases"]):
            jobs = spec["jobs"] if pooled else [j for j in spec["jobs"] if j["config"].get("phase", j["kind"]) == phase]
            memory_estimate = spec.get("memory_estimate_gb", {}).get(phase) if memory_managed else None
            if is_a4:
                memory_estimate = spec.get("memory_estimate_gb", {}).get(phase)
                # Project the REMAINING work (resume-aware); stop before this phase
                # if it will not fit the remaining wall budget.
                projection = a4_projection(spec, record["configuration"], effective_workers, root, code_identity(), index, time.time(), deadline)
                record.setdefault("projections", []).append({"before_phase": phase, **projection})
                atomic_json(root / "launches.json", history)
                if not projection["fits"]:
                    record.update(complete=False, finished_epoch=time.time(), stopped="projection_exceeds_budget")
                    atomic_json(root / "launches.json", history)
                    return {"complete": False, "reason": "projection_exceeds_budget", "projection": projection, "outcomes": outcomes}
            result = dispatch(root / phase, jobs, code_identity(), settings, deadline, measurements=record["configuration"][phase],
                              control_root=root, registered=spec["registered"], registration=spec.get("registration"),
                              completion_screen=screen, memory_cap=mem_caps.get(phase) if memory_managed else None,
                              memory_estimate_gb=memory_estimate,
                              **({"pooled_jobs": spec["pooled_job_estimates"]} if pooled else {}))
            outcomes[phase] = result
            record["outcomes"] = outcomes
            atomic_json(root / "launches.json", history)
            if result["completed"] != len(jobs) or result['reason'] == 'screen_failure':
                record.update(complete=False, finished_epoch=time.time())
                atomic_json(root / 'launches.json', history)
                if spec.get("tag") == "pilot":
                    if is_a10_pilot:
                        atomic_json(root / "cost_projection.json", {"non_registered": True, "cost_only": True,
                                    "status": "incomplete", "reason": "sample interrupted; no projection"})
                    else:
                        from .pilot import project_costs
                        atomic_json(root / "cost_projection.json", project_costs(spec, root, outcomes, record["configuration"]))
                return {"complete": False, "outcomes": outcomes}
            if is_a4 and jobs:
                check = nondeterminism_check(root / phase, jobs, spec["registered"], spec.get("registration"))
                atomic_json(root / phase / "nondeterminism_check.json", check)
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
            if is_a10_pilot:
                from .pilot_a10 import project
                projection = project(spec, root, record["configuration"], {k: v["selection"] for k, v in outcomes.items()})
            else:
                from .pilot import project_costs
                projection = project_costs(spec, root, outcomes, record["configuration"])
            atomic_json(root / "cost_projection.json", projection)
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
