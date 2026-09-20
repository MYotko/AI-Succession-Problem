"""Write the attempt 2 halt evidence without importing simulation code."""
import os
import sys
from pathlib import Path
sys.dont_write_bytecode = True
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
os.environ["GIT_OPTIONAL_LOCKS"] = "0"
THREADS = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS", "BLIS_NUM_THREADS")
for key in THREADS:
    os.environ[key] = "1"
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "simulation" / "diagnostics"
PREFIX = "defense_recovery_run_a2_"
def allowed(path):
    if isinstance(path, int):
        return True
    value = os.fsdecode(path)
    if os.path.normcase(os.path.abspath(value)) == os.path.normcase(os.path.abspath(os.devnull)):
        return True
    target = Path(value).resolve()
    return target.parent == OUT and target.name.startswith(PREFIX)
def guard(event, args):
    if event == "open":
        path, mode, flags = args
        writing = (isinstance(mode, str) and any(c in mode for c in "wax+"))
        writing = writing or bool(flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND))
        if writing and not allowed(path):
            raise PermissionError("Write outside scope: " + str(path))
    elif event in ("os.remove", "os.rmdir", "os.mkdir", "os.chmod", "os.utime", "os.truncate"):
        if not allowed(args[0]):
            raise PermissionError("Write outside scope: " + str(args[0]))
    elif event in ("os.rename", "os.replace"):
        if not all(allowed(path) for path in args[:2]):
            raise PermissionError("Write outside scope: " + repr(args))
    elif event in ("os.symlink", "os.link"):
        raise PermissionError("Links prohibited")
sys.addaudithook(guard)

import datetime
import hashlib
import importlib.metadata
import json
import platform
import subprocess
import time

CONFLICTS = [
  {
    "id": "governing_specification",
    "dispatch": "THE SPECIFICATION names simulation/diagnostics/defense_heldout_design_note.md as the committed pre-registration.",
    "committed_evidence": "The held-out note governs defense_heldout_run_ and registers Y1 through Y5 with OFF and GRADED. The recovery note governs defense_recovery_run_ and its Sections 3 through 5 specify the recovery rule, 300 runs, five defense arms, and R1 through R6.",
    "conflict": "The named governing specification does not agree with this dispatch's recovery design and registered quantities.",
    "halt_basis": "Where anything in this prompt appears to conflict with a note, HALT and report the conflict."
  },
  {
    "id": "artifact_prefix",
    "dispatch": "The attempt context says this attempt writes under defense_recovery_run_a2_a2_. WRITE SCOPE and T3 through T5 specify defense_recovery_run_a2_* and filenames beginning defense_recovery_run_a2_.",
    "committed_evidence": "The recovery note's broad governed prefix is defense_recovery_run_; both attempt prefixes fit it.",
    "conflict": "The attempt context and required artifact filenames use different prefixes.",
    "halt_basis": "Additional dispatch inconsistency recorded with the governing-specification halt. Halt artifacts use the exact T4 and T5 filenames inside WRITE SCOPE."
  }
]
RETRIES = []
WARNINGS = []
def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()
def digest(raw):
    return hashlib.sha256(raw.replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()
def read_json(path):
    started = time.monotonic()
    while True:
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except PermissionError as exc:
            elapsed = time.monotonic() - started
            RETRIES.append({"utc": now(), "operation": "JSON read", "path": str(path),
                            "elapsed_seconds": elapsed, "error": str(exc)})
            if elapsed >= 5.0:
                raise
            time.sleep(min(0.05, 5.0 - elapsed))
def git(*args):
    proc = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, check=False)
    if proc.stderr:
        WARNINGS.append({"argv": ["git", *args], "stderr": proc.stderr.decode("utf-8", errors="replace")})
    if proc.returncode:
        raise RuntimeError("Read-only git command failed: " + repr(args))
    return proc.stdout
def write(name, value):
    raw = value.encode("utf-8") if isinstance(value, str) else value
    assert b"\xe2\x80\x94" not in raw
    with (OUT / (PREFIX + name)).open("xb") as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
def write_json(name, value):
    write(name, json.dumps(value, indent=2, ensure_ascii=True, allow_nan=False) + "\n")
def main():
    preflight = read_json(OUT / (PREFIX + "preflight.json"))
    assert preflight["status"] == "PASS"
    head = git("rev-parse", "HEAD").decode().strip()
    readings = []
    for original in preflight["source_readings"]:
        path = original["path"]
        git("ls-files", "--error-unmatch", path)
        commit = git("log", "-1", "--format=%H", "--", path).decode().strip()
        assert commit
        git("merge-base", "--is-ancestor", commit, "origin/main")
        final = {"path": path, "expected_sha256_lf": original["expected_sha256_lf"],
                 "committed_sha256_lf": digest(git("cat-file", "blob", "HEAD:" + path)),
                 "working_tree_sha256_lf": digest((ROOT / path).read_bytes()),
                 "committed_blob_sha1": git("rev-parse", "HEAD:" + path).decode().strip(),
                 "last_modified_commit": commit, "read_commit": head}
        final["passed"] = (final["committed_sha256_lf"] == final["working_tree_sha256_lf"]
                           == final["expected_sha256_lf"]
                           and final["committed_blob_sha1"] == original["committed_blob_sha1"])
        readings.append({"path": path, "start": original, "completion": final})
    failed = [item["path"] for item in readings if not item["completion"]["passed"]]
    reason = "The dispatch names the held-out pre-registration as its specification, but requires the recovery design and quantities."
    if failed:
        reason += " Completion pin mismatch: " + ", ".join(failed)
    status = {"status": "HALTED", "stage": "after T0, before T1", "halt_reason": reason,
              "specification_conflicts": CONFLICTS, "T0_status": "PASS", "T1_status": "NOT_RUN",
              "registered_run_count": 300, "batch_runs_launched": 0, "batch_runs_completed": 0,
              "gate_runs_launched": 0, "model_steps_executed": 0, "analysis_status": "NOT_RUN",
              "sign_fixture_status": "NOT_RUN", "source_pins_match_at_completion": not failed,
              "source_pin_failures_at_completion": failed, "resumed_seeds": [],
              "retry_events": RETRIES, "tool_layer_workarounds": [], "utc": now()}
    write_json("halt.json", status)
    results = dict(status)
    results.update({"registered_quantities_status": "UNMEASURED",
                    **{name: None for name in ("R1", "R2", "R3", "R4", "R5", "R6")},
                    "attack_validity_check": None, "sign_fixture": None,
                    "registered_predictions": None, "selected_parameter": None,
                    "promotion_gate_decision": None})
    write_json("results.json", results)
    lines = ["# Recovery evaluation, attempt 2: pre-execution halt", "",
             "Status: HALTED after T0 and before T1. T0 passed.",
             "Batch runs launched: 0 of 300. Completed batch runs: 0. Gate runs: 0. Model steps: 0.", "",
             "## Halt reason", "", reason, ""]
    for conflict in CONFLICTS:
        lines.extend(["- Dispatch: " + conflict["dispatch"],
                      "  Committed evidence: " + conflict["committed_evidence"],
                      "  Conflict: " + conflict["conflict"],
                      "  Handling: " + conflict["halt_basis"], ""])
    lines.extend(["Attempt 2 corrects the earlier T4 and T5 quantity labels and gate number. The governing-specification mismatch remains.",
                  "", "## Registered results", "",
                  "This dispatch requests gate 3 of the promotion plan. The recovery rule, its three quiet periods, selection rule and criterion are committed in the recovery note.",
                  "This halt record is not a promotion decision and selects no parameter.",
                  "No ratio of two measured counts was computed. Applying the Section 6 selection rule and criterion and Section 8 interpretation is reserved for the operator.", ""])
    for name, description in [("R1", "Harm direction: negative."),
                              ("R2", "Harm direction: positive."),
                              ("R3", "No harm direction."),
                              ("R4", "No harm direction specified."),
                              ("R5", "No harm direction specified."),
                              ("R6", "Liveness and auditability.")]:
        lines.append("- " + name + ": not measured. " + description)
    lines.extend(["", "Sign fixture: not run. Attack-validity check: not run. Predictions: not evaluated.",
                  "No exploratory analysis was performed.", "",
                  "## Source pins at start and completion", "",
                  "Basis: SHA256 on LF-normalized bytes. Committed blobs were read with git cat-file only after T0 verified their hashes.",
                  "", "| File | Start committed | Start working tree | Completion committed | Completion working tree | Match |",
                  "| --- | --- | --- | --- | --- | --- |"])
    for item in readings:
        first, last = item["start"], item["completion"]
        lines.append("| " + " | ".join([item["path"], first["committed_sha256_lf"],
                     first["working_tree_sha256_lf"], last["committed_sha256_lf"],
                     last["working_tree_sha256_lf"], str(last["passed"]).lower()]) + " |")
    numpy_version = importlib.metadata.version("numpy")
    lines.extend(["", "## Execution metadata", "",
                  "Machine: " + platform.node() + ". HEAD: " + head + ".",
                  "Python: " + platform.python_version() + ". NumPy: " + numpy_version + " (package metadata; not imported).",
                  "Operator-stated CPU budget: 16. Mode: normal. Worker limit: 15. Workers launched: 0.",
                  "Numerical-library thread environment: 1. No effective per-worker limit was verified because no worker was launched.",
                  "No simulation module or committed executor was imported or copied.",
                  "No execution, merge or per-run deletion occurred. No resumed seeds. No tool-layer workarounds.",
                  "JSON permission retry events: " + str(len(RETRIES)) + ".", "",
                  "## T0 stderr warnings", ""])
    for warning in preflight["stderr_warnings"]:
        lines.append("- " + warning["stderr"].strip())
    lines.extend(["", "The expected warning was recorded without repair.", ""])
    write("report.md", "\n".join(lines))
    outputs = []
    for name in ("finalize.py", "preflight.json", "halt.json", "results.json", "report.md"):
        path = OUT / (PREFIX + name)
        outputs.append({"path": path.relative_to(ROOT).as_posix(), "sha256": digest(path.read_bytes()),
                        "hash_basis": "LF-normalized bytes", "csv_row_count": None})
    manifest = {
        "schema": "recovery-attempt-2-pre-execution-halt-v1", "status": "HALTED",
        "halt_reason": reason, "machine": platform.node(), "head": head,
        "python_version": platform.python_version(), "python_executable": sys.executable,
        "numpy_version": numpy_version, "numpy_version_basis": "installed package metadata; not imported",
        "cpu_budget": 16, "cpu_budget_basis": "operator-stated YOTKOTEST budget",
        "operating_mode": "normal", "worker_limit": 15, "workers_launched": 0,
        "maximum_active_workers": 0, "registered_runs": 300, "completed_runs": 0,
        "gate_runs": 0, "model_steps": 0,
        "numerical_threads": {"configured_environment": {key: os.environ[key] for key in THREADS},
                              "effective_per_worker": [], "verification": "NO_WORKERS_LAUNCHED"},
        "mode_change_events": [], "resumed_seeds": [], "restart_events": [],
        "retry_events": RETRIES, "tool_layer_workarounds": [],
        "T0_stderr_warnings": preflight["stderr_warnings"],
        "completion_stderr_warnings": WARNINGS, "source_pin_readings": readings,
        "source_pins_match_at_completion": not failed,
        "pre_registration_blob_sha1": {
            item["path"]: item["completion"]["committed_blob_sha1"]
            for item in readings if item["path"].endswith("_design_note.md")},
        "per_module_sha256": [
            {"path": item["path"], "sha256": item["completion"]["committed_sha256_lf"],
             "basis": "LF-normalized committed HEAD blob; module not imported"}
            for item in readings if item["path"].endswith(".py")] + [
            {"path": "simulation/diagnostics/" + PREFIX + "finalize.py",
             "sha256": digest(Path(__file__).read_bytes()), "basis": "LF-normalized authored halt finalizer"}],
        "committed_executors_copied_or_imported": [], "outputs": outputs,
        "manifest_self_entry": {"path": "simulation/diagnostics/" + PREFIX + "manifest.json",
                                "sha256": None, "csv_row_count": None,
                                "reason": "Self-hash excluded to avoid recursive hashing."},
        "artifact_convention": {"merge_status": "NO_RUNS", "merged_files": [], "per_run_rows": [],
                               "deleted_files_by_kind": {"steps": 0, "completion": 0, "progress": 0,
                                                         "initial": 0, "console": 0}},
        "bytecode_writes_disabled": True,
        "write_guard": "Audit hook permits only the attempt 2 prefix and os.devnull.",
        "utc": now()}
    write_json("manifest.json", manifest)
    print("HALTED: specification conflict; T0 passed; 0/300 batch runs; 0 gate runs; pins "
          + str(len(readings) - len(failed)) + "/" + str(len(readings)) + ".")
    return 2
if __name__ == "__main__":
    raise SystemExit(main())
