"""Per-host model-service supervisor, invoked by the operator's launch."""
from contextlib import contextmanager
import platform
import signal
import subprocess
import time
from .artifacts import ROOT, atomic_json, read, unseal, scoped, lease
from .worker_safety import best_effort, metadata_json


def model_service(settings):
    value = settings.get("model_service", "llm" if settings["profile"] == "x2" else "none")
    if value not in ("llm", "none") or (settings["profile"] != "x2" and value != "none"):
        raise ValueError("model service must be llm or none; llm requires the X2 profile")
    return value


def require_service_record(settings, record):
    selected = model_service(settings)
    if selected == "none":
        if not record or record.get("model_service") != "none" or record.get("actions_skipped") is not True:
            raise RuntimeError("host needs an explicit no-service supervisor record")
    elif not record or record.get("model_service", "llm") != "llm" or record.get("down_exit_code") != 0:
        raise RuntimeError("X2 launch requires the active service lease wrapper")


@contextmanager
def without_service(root):
    record = {"host": platform.node(), "model_service": "none", "actions_skipped": True,
              "started_epoch": time.time(), "down_exit_code": None, "up_exit_code": None}
    metadata_json(root / "service.json", record)
    try:
        yield record
    finally:
        record["finished_epoch"] = time.time()
        metadata_json(root / "service.json", record)


def command(root, action):
    result = subprocess.run(["llm", action], stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, timeout=180, check=False)
    path = root / ("llm_" + action + ".log")
    def write():
        with scoped(path).open("ab") as stream:
            stream.write(result.stdout or b'')
    best_effort(path, write)
    return result.returncode


def run_with_service(spec_path, output_root, settings):
    from .production_runner import validate_spec, launch, caps, preflight_completion
    if settings["profile"] != "x2" or platform.system() != "Linux":
        raise RuntimeError("X2 service supervisor requires the X2 profile on Linux")
    selected = model_service(settings)
    spec = unseal(read(spec_path))
    validate_spec(spec, {**settings, "caps": caps(settings["profile"], settings["cpu_budget"])})
    preflight_completion(spec, output_root)
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
            previous_path = root / ("service_previous_" + str(time.time_ns()) + ".json")
            best_effort(previous_path, lambda: atomic_json(previous_path, read(record_path)))
        if selected == "none":
            with without_service(root) as record:
                return launch(spec_path, root, settings, service_record=record)
        record = {"host": platform.node(), "model_service": selected,
                  "started_epoch": time.time(), "down_exit_code": None, "up_exit_code": None}
        metadata_json(record_path, record)
        def interrupt(number, frame):
            raise KeyboardInterrupt("service supervisor interrupted")
        previous = {sig: signal.signal(sig, interrupt) for sig in (signal.SIGINT, signal.SIGTERM)}
        error, result = None, None
        try:
            record["down_exit_code"] = command(root, "down")
            record["down_completed_epoch"] = time.time()
            metadata_json(record_path, record)
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
            metadata_json(record_path, record)
            for sig, handler in previous.items():
                signal.signal(sig, handler)
        if error is not None:
            raise error
        return result
