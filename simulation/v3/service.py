"""X2-only service supervisor, invoked explicitly by the operator's launch."""
import platform
import signal
import subprocess
import time
from .artifacts import ROOT, atomic_json, read, unseal, scoped, lease


def command(root, action):
    with (root / ("llm_" + action + ".log")).open("a", encoding="utf-8") as stream:
        return subprocess.run(["llm", action], stdout=stream, stderr=subprocess.STDOUT, timeout=180, check=False).returncode


def run_with_service(spec_path, output_root, settings):
    from .production_runner import validate_spec, launch, caps
    if platform.node().lower() != "yotko-evo-x2" or platform.system() != "Linux":
        raise RuntimeError("service management is permitted only on X2")
    spec = unseal(read(spec_path))
    validate_spec(spec, {**settings, "caps": caps(settings["profile"], settings["cpu_budget"])})
    root = scoped(output_root)
    root.mkdir(parents=True, exist_ok=True)
    # This lease serializes v3 supervisors. The operator must let the separate
    # stage 4 tranche finish before launch; we do not modify its lease.
    with lease(ROOT / "service.lock"):
        budget_path = root / "budget.json"
        if not budget_path.exists():
            start = time.time()
            reserve = spec.get("cleanup_reserve_seconds", 300)
            atomic_json(budget_path, {"start_epoch": start, "deadline_epoch": start + spec["wall_seconds"] - reserve,
                                      "overall_deadline_epoch": start + spec["wall_seconds"], "cleanup_reserve_seconds": reserve})
        if time.time() >= read(budget_path)["deadline_epoch"]:
            raise RuntimeError("batch deadline expired before service change")
        record_path = root / "service.json"
        if record_path.exists():
            atomic_json(root / ("service_previous_" + str(time.time_ns()) + ".json"), read(record_path))
        record = {"host": platform.node(), "started_epoch": time.time(), "down_exit_code": None, "up_exit_code": None}
        atomic_json(record_path, record)
        def interrupt(number, frame):
            raise KeyboardInterrupt("service supervisor interrupted")
        previous = {sig: signal.signal(sig, interrupt) for sig in (signal.SIGINT, signal.SIGTERM)}
        error, result = None, None
        try:
            record["down_exit_code"] = command(root, "down")
            record["down_completed_epoch"] = time.time()
            atomic_json(record_path, record)
            if record["down_exit_code"]:
                raise RuntimeError("llm down failed")
            result = launch(spec_path, root, settings, service_record=record)
        except BaseException as exc:
            error = exc
            record["work_exception"] = repr(exc)
        finally:
            for sig in previous:
                signal.signal(sig, signal.SIG_IGN)
            try:
                record["up_exit_code"] = command(root, "up")
                if record["up_exit_code"]:
                    error = RuntimeError("llm up failed; operator must restore the service")
            except BaseException as exc:
                record["up_exception"] = repr(exc)
                error = exc
            record["finished_epoch"] = time.time()
            atomic_json(record_path, record)
            for sig, handler in previous.items():
                signal.signal(sig, handler)
        if error is not None:
            raise error
        return result
