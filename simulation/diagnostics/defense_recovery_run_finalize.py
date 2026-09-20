"""Record a pre-execution specification-conflict halt for the recovery dispatch."""
import os
import sys
from pathlib import Path

sys.dont_write_bytecode = True
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
os.environ["GIT_OPTIONAL_LOCKS"] = "0"
THREAD_VARS = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
               "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS", "BLIS_NUM_THREADS")
for name in THREAD_VARS:
    os.environ[name] = "1"
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "simulation" / "diagnostics"
PREFIX = "defense_recovery_run_"
DEVNULL = os.path.normcase(os.path.abspath(os.devnull))

def allowed(path):
    if isinstance(path, int):
        return True
    value = os.fsdecode(path)
    if os.path.normcase(os.path.abspath(value)) == DEVNULL:
        return True
    target = Path(value).resolve()
    return target.parent == OUT and target.name.startswith(PREFIX)

def require_allowed(path):
    if not allowed(path):
        raise PermissionError("Write outside governed prefix: " + str(path))

def audit(event, args):
    if event == "open":
        path, mode, flags = args
        writing = (isinstance(mode, str) and any(c in mode for c in "wax+"))
        writing = writing or bool(flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT |
                                         os.O_TRUNC | os.O_APPEND))
        if writing:
            require_allowed(path)
    elif event in ("os.remove", "os.rmdir", "os.mkdir", "os.chmod", "os.utime",
                   "os.truncate", "os.chown"):
        require_allowed(args[0])
    elif event in ("os.rename", "os.replace"):
        require_allowed(args[0])
        require_allowed(args[1])
    elif event in ("os.symlink", "os.link"):
        raise PermissionError("Links are not permitted in this halt writer")

sys.addaudithook(audit)

import datetime
import hashlib
import importlib.metadata
import json
import platform
import subprocess
import time

RETRIES = []
WARNINGS = []
CONFLICTS = [
  {
    "id": "analysis_and_report_quantities",
    "dispatch": "T4 requires computing Y1 through Y5; T5 requires registered results Y1 through Y5 in order.",
    "committed_note": "defense_recovery_design_note.md Section 5 registers R1 through R6. Section 8 requires analysis beyond R1 through R6 to be labeled exploratory and placed after registered results.",
    "effect": "The required registered analysis and report quantities do not agree."
  },
  {
    "id": "gate_identity",
    "dispatch": "T5 requires the report to state that this is gate 2 of the promotion plan.",
    "committed_note": "defense_recovery_design_note.md title and Sections 1 and 6 identify this recovery evaluation as gate 3.",
    "effect": "The required report gate identifier does not agree."
  },
  {
    "id": "governing_specification",
    "dispatch": "THE SPECIFICATION names defense_heldout_design_note.md as the committed pre-registration.",
    "committed_note": "defense_recovery_design_note.md governs defense_recovery_run_ and specifies recovery, fifteen cells and 300 runs; defense_heldout_design_note.md governs defense_heldout_run_ and registers Y1 through Y5.",
    "effect": "The named governing note does not agree with the task's recovery design and output prefix."
  }
]
FILES = [
    PREFIX + "finalize.py", PREFIX + "preflight.json", PREFIX + "halt.json",
    PREFIX + "results.json", PREFIX + "report.md", PREFIX + "manifest.json",
]

def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def lf_hash(raw):
    return hashlib.sha256(raw.replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()

def read_json(path):
    started = time.monotonic()
    while True:
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except PermissionError as exc:
            RETRIES.append({"utc": now(), "operation": "JSON read", "path": str(path),
                            "error": str(exc)})
            if time.monotonic() - started >= 5.0:
                raise
            time.sleep(min(0.05, max(0.0, 5.0 - (time.monotonic() - started))))

def git(*args):
    result = subprocess.run(["git", *args], cwd=ROOT, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, check=False)
    if result.stderr:
        WARNINGS.append({"argv": ["git", *args],
                         "stderr": result.stderr.decode("utf-8", errors="replace")})
    if result.returncode:
        raise RuntimeError("Read-only git command failed: " + repr(args))
    return result.stdout

def write_bytes(name, data):
    target = OUT / name
    with target.open("xb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())

def write_json(name, value):
    write_bytes(name, (json.dumps(value, indent=2, ensure_ascii=True,
                                 allow_nan=False) + "\n").encode("utf-8"))

def main():
    initial = read_json(OUT / (PREFIX + "preflight.json"))
    assert initial["status"] == "PASS"
    assert not initial["failures"]
    head = git("rev-parse", "HEAD").decode().strip()
    readings = []
    pin_failures = []
    for source in initial["source_readings"]:
        path = source["path"]
        tracked = git("ls-files", "--error-unmatch", path).decode().strip()
        assert tracked
        last_commit = git("log", "-1", "--format=%H", "--", path).decode().strip()
        assert last_commit
        git("merge-base", "--is-ancestor", last_commit, "origin/main")
        committed = git("cat-file", "blob", "HEAD:" + path)
        working = (ROOT / path).read_bytes()
        blob = git("rev-parse", "HEAD:" + path).decode().strip()
        final = {
            "path": path,
            "expected_sha256_lf": source["expected_sha256_lf"],
            "committed_sha256_lf": lf_hash(committed),
            "working_tree_sha256_lf": lf_hash(working),
            "committed_blob_sha1": blob,
            "last_modified_commit": last_commit,
            "read_commit": head,
        }
        final["passed"] = (
            final["committed_sha256_lf"] == final["working_tree_sha256_lf"]
            == final["expected_sha256_lf"]
            and blob == source["committed_blob_sha1"]
        )
        readings.append({"path": path, "start": source, "completion": final})
        if not final["passed"]:
            pin_failures.append(path)
    status = {
        "status": "HALTED", "stage": "after T0, before T1",
        "halt_reason": "Specification conflicts between the dispatch and the committed recovery note.",
        "specification_conflicts": CONFLICTS,
        "T0_status": "PASS", "T1_status": "NOT_RUN",
        "sign_fixture_status": "NOT_RUN", "analysis_status": "NOT_RUN",
        "registered_run_count": 300, "batch_runs_launched": 0,
        "batch_runs_completed": 0, "gate_runs_launched": 0,
        "model_steps_executed": 0, "source_pin_failures_at_completion": pin_failures,
        "source_pins_match_at_completion": not pin_failures,
        "resumed_seeds": [], "retry_events": RETRIES,
        "tool_layer_workarounds": [], "utc": now(),
    }
    if pin_failures:
        status["halt_reason"] += " Completion source pin mismatch: " + ", ".join(pin_failures)
    write_json(PREFIX + "halt.json", status)
    results = {
        **status,
        "registered_quantities_status": "UNMEASURED",
        "R1": None, "R2": None, "R3": None, "R4": None, "R5": None, "R6": None,
        "attack_validity_check": None, "sign_fixture": None,
        "registered_predictions": None,
        "parameter_selected": None, "promotion_gate_decision": None,
    }
    write_json(PREFIX + "results.json", results)
    lines = [
        "# Recovery evaluation: pre-execution halt",
        "",
        "Status: HALTED after T0 and before T1. T0 passed. Zero of 300 batch runs were launched.",
        "Gate runs: 0. Completed batch runs: 0. Model steps: 0.",
        "",
        "## Specification conflicts",
        "",
    ]
    for conflict in CONFLICTS:
        lines.extend(["- Dispatch: " + conflict["dispatch"],
                      "  Committed note: " + conflict["committed_note"],
                      "  Conflict: " + conflict["effect"], ""])
    lines.extend([
        "The dispatch requires a halt when it conflicts with a committed note. No requirement was corrected or selected.",
        "",
        "## Registered results",
        "",
        "R1 through R6 were not measured. The attack-validity check and sign fixture were not run.",
        "No paired value, ratio of two measured counts, prediction threshold result, parameter selection, or promotion decision was computed.",
        "Sections 6 and 8 remain reserved for the operator.",
        "",
        "## Source pins at start and completion",
        "",
        "Basis: SHA256 of LF-normalized bytes. Each reading covers the committed HEAD blob and the working-tree file.",
        "",
        "| File | Start committed | Start working tree | Completion committed | Completion working tree | Match |",
        "| --- | --- | --- | --- | --- | --- |",
    ])
    for item in readings:
        first, last = item["start"], item["completion"]
        lines.append("| " + " | ".join([
            item["path"], first["committed_sha256_lf"], first["working_tree_sha256_lf"],
            last["committed_sha256_lf"], last["working_tree_sha256_lf"],
            str(last["passed"]).lower()]) + " |")
    lines.extend([
        "", "## Execution and artifacts", "",
        "Machine: " + platform.node() + ". HEAD: " + head + ".",
        "Python: " + platform.python_version() + ". NumPy package version: "
        + importlib.metadata.version("numpy") + " (package metadata; NumPy was not imported).",
        "CPU budget: 16, operator-stated for YOTKOTEST. Mode: normal. Worker limit: 15. Workers launched: 0.",
        "Numerical-library thread environment: 1. Effective per-worker limits were not verified because no worker was launched.",
        "No execution, artifact merge, per-run deletion, or registered analysis took place.",
        "No simulation module or committed executor was imported or copied.",
        "Resumed seeds: none. Tool-layer workarounds: none.",
        "JSON permission retry events: " + str(len(RETRIES)) + ".",
        "",
        "## T0 stderr warnings", "",
    ])
    for warning in initial["stderr_warnings"]:
        lines.append("- " + warning["stderr"].strip())
    lines.extend(["", "The expected global git ignore permission warning was recorded without repair.", ""])
    report = "\n".join(lines)
    assert chr(0x2014) not in report
    write_bytes(PREFIX + "report.md", report.encode("utf-8"))
    outputs = []
    for name in FILES:
        if name.endswith("manifest.json"):
            continue
        path = OUT / name
        outputs.append({
            "path": path.relative_to(ROOT).as_posix(),
            "sha256": lf_hash(path.read_bytes()),
            "hash_basis": "LF-normalized bytes",
            "csv_row_count": None,
        })
    manifest = {
        "schema": "recovery-pre-execution-halt-v1",
        "status": "HALTED", "halt_reason": status["halt_reason"],
        "machine": platform.node(), "platform": platform.platform(),
        "head": head, "python_version": platform.python_version(),
        "python_executable": sys.executable,
        "numpy_version": importlib.metadata.version("numpy"),
        "numpy_version_basis": "installed package metadata; module not imported",
        "cpu_budget": 16, "cpu_budget_basis": "operator-stated YOTKOTEST budget",
        "operating_mode": "normal", "worker_limit": 15,
        "simulation_workers_launched": 0, "maximum_active_workers": 0,
        "registered_run_count": 300, "completed_run_count": 0,
        "gate_run_count": 0, "model_steps_executed": 0,
        "numerical_library_threads": {
            "configured_environment": {key: os.environ[key] for key in THREAD_VARS},
            "verified_per_worker": [],
            "verification_status": "NOT_APPLICABLE_NO_WORKERS_LAUNCHED",
        },
        "mode_change_events": [], "resumed_seeds": [], "restart_events": [],
        "retry_events": RETRIES, "tool_layer_workarounds": [],
        "T0_stderr_warnings": initial["stderr_warnings"],
        "completion_git_stderr_warnings": WARNINGS,
        "source_pin_readings": readings,
        "all_source_pins_match_at_completion": not pin_failures,
        "per_module_sha256": [
            {"path": item["path"],
             "sha256": item["completion"]["committed_sha256_lf"],
             "basis": "LF-normalized committed HEAD blob; module not imported"}
            for item in readings if item["path"].endswith(".py")
        ] + [
            {"path": "simulation/diagnostics/" + PREFIX + "finalize.py",
             "sha256": lf_hash(Path(__file__).read_bytes()),
             "basis": "LF-normalized authored halt finalizer file"}
        ],
        "committed_executors_copied_or_imported": [],
        "pre_registration_blob_sha1": readings[0]["completion"]["committed_blob_sha1"],
        "outputs": outputs,
        "manifest_self_entry": {
            "path": "simulation/diagnostics/" + PREFIX + "manifest.json",
            "sha256": None, "csv_row_count": None,
            "reason": "Self-hash excluded to avoid recursive hashing.",
        },
        "artifact_convention": {
            "merge_status": "NOT_APPLICABLE_NO_RUNS",
            "merged_files": [], "per_run_rows": [],
            "per_run_files_deleted_by_kind": {
                "steps": 0, "completion": 0, "progress": 0, "initial": 0, "console": 0
            },
        },
        "bytecode_writes_disabled": True,
        "write_guard": "Audit hook permits only the governed file prefix and os.devnull.",
        "utc": now(),
    }
    write_json(PREFIX + "manifest.json", manifest)
    print("HALTED: specification conflict; T0 passed; gate runs 0; batch runs 0/300; source pins "
          + str(len(readings) - len(pin_failures)) + "/" + str(len(readings)) + ".")
    return 2

if __name__ == "__main__":
    raise SystemExit(main())
