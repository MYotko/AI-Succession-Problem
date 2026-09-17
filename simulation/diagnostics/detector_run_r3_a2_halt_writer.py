"""Record the attempt 2 tool-layer halt. This script performs no derivation."""
import sys
sys.dont_write_bytecode = True
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "simulation" / "diagnostics"
PREFIX = "detector_run_r3_a2_"

def permitted(path):
    if isinstance(path, int):
        return path in (0, 1, 2)
    if os.path.normcase(os.path.abspath(os.fsdecode(path))) == os.path.normcase(os.path.abspath(os.devnull)):
        return True
    target = Path(path).resolve()
    return target.parent == OUT and target.name.startswith(PREFIX)

def guard(event, args):
    if event == "open":
        path, mode, flags = args
        writable = any(c in (mode or "") for c in "wax+") or flags & (
            os.O_WRONLY | os.O_RDWR | os.O_APPEND | os.O_CREAT | os.O_TRUNC)
        if writable and not permitted(path):
            raise PermissionError("Out-of-scope writable open: " + str(path))
    elif event in ("os.remove", "os.mkdir", "os.rmdir", "os.chmod", "os.utime", "os.truncate"):
        if not permitted(args[0]):
            raise PermissionError("Out-of-scope mutation")
    elif event in ("os.rename", "os.link", "os.symlink"):
        if not permitted(args[0]) or not permitted(args[1]):
            raise PermissionError("Out-of-scope mutation")

sys.addaudithook(guard)
import hashlib
import json
import importlib.metadata

HEAD = "2ac9f8fe8b4f7a6c9d9b25d795ab7007531dc7bb"
REASON = "Direct file-access tool failed before executing code: Mcp error -32602: js: codex/sandbox-state-meta: missing field sandboxPolicy."
WARNING = "warning: unable to access 'C:\\Users\\matty/.config/git/ignore': Permission denied"
runtime = {"machine": os.environ.get("COMPUTERNAME"), "head": HEAD,
           "python": sys.version, "numpy": importlib.metadata.version("numpy"),
           "simulation_workers": 0, "model_steps": 0, "derivation_executed": False,
           "bytecode_disabled": True, "halt_writer_write_guard_installed": True,
           "os_devnull_write_guard_exemption": True}
preflight = {
    "status": "INCOMPLETE_AFTER_HALT",
    "checks": [
        {"check": "T0a", "command": "git rev-parse --abbrev-ref HEAD", "exit": 0, "stdout": "main", "passed": True},
        {"check": "T0b", "command": "git merge-base --is-ancestor 2ac9f8fe8b4f7a6c9d9b25d795ab7007531dc7bb HEAD", "exit": 0, "passed": True},
        {"check": "T0c", "command": "git status --porcelain --untracked-files=no", "exit": 0, "stdout": "", "stderr": WARNING, "passed": True}],
    "checks_not_completed": ["T0d", "T0e", "T0f", "T0g", "T0h"],
    "post_halt_artifact_creation_check": {"existing_attempt2_artifacts": [], "purpose": "Avoid overwriting any existing attempt 2 artifact"},
    "committed_specification_read": False,
    "source_pins_verified_this_attempt": False}
halt = {"status": "HALTED", "halt_reason": REASON,
        "constants_created": False, "runtime": runtime}
report = "\n".join([
    "# Detector round 3, stage A, attempt 2: HALTED", "",
    REASON, "",
    "The task's closed halt rule includes an exception being raised. The failed tool call executed no code. No derivation executor was created, no derivation began, and no constants were produced. No retry or replacement derivation was attempted.", "",
    "No model was stepped, no arm was run, no detector was evaluated, and nothing was interpreted. Stage B is a separate dispatch that may begin only after completed stage A outputs are committed and pushed. This halt record does not satisfy that condition.", "",
    "Attempt 1 halted before derivation and produced no constant, as recorded in the operator's dispatch. Its artifacts were not used or modified in this attempt.", "",
    "## Preconditions", "",
    "T0a passed: main. T0b passed: the required ancestor check returned exit 0. T0c passed: the exact tracked-only status command returned exit 0 with no stdout lines. T0d through T0h were not completed. The committed specification was not read because its hash had not yet been verified in this attempt.", "",
    "No derived-versus-pinned table, source-pin verification, input log verification, or Section 1 verbatim quote is available from this halted attempt.", "",
    "T0 stderr warning:", "", "```text", WARNING, "```", "",
    "## Runtime and artifacts", "",
    "Machine: " + str(runtime["machine"]) + ". HEAD: " + HEAD + ".",
    "Python: " + runtime["python"] + ". NumPy: " + runtime["numpy"] + ". Simulation workers: 0.", "",
    "Only the halt-reporting script was created and executed after the halt. It installed a write guard permitting the attempt 2 prefix and os.devnull, with bytecode writes disabled. No model or scientific module was imported. No containment diff was performed.", "",
    "Constants path, not created: simulation/diagnostics/detector_run_r3_a2_constants.json.",
    "Report: simulation/diagnostics/detector_run_r3_a2_report.md.",
    "Manifest: simulation/diagnostics/detector_run_r3_a2_manifest.json.", "",
    "Output SHA256 values use LF-normalized bytes. All outputs are non-CSV, so row counts are null. Committed input blob identifiers are unavailable because that gate was not reached. The manifest omits its own recursive hash.", ""])
outputs = [Path(__file__)]

def emit(name, value, text=False):
    path = OUT / (PREFIX + name)
    raw = value if text else json.dumps(value, indent=2, ensure_ascii=True) + "\n"
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(raw)
    outputs.append(path)

emit("preflight.json", preflight)
emit("halt.json", halt)
emit("report.md", report, text=True)
entries = [{"path": path.relative_to(ROOT).as_posix(),
            "sha256_lf": hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest(),
            "csv_rows": None} for path in outputs]
manifest = {"status": "HALTED", "halt_reason": REASON, "runtime": runtime,
            "outputs": entries, "hash_basis": "LF-normalized bytes",
            "committed_input_blob_sha1": None,
            "unavailable_provenance_reason": "Halted before T0d and specification retrieval",
            "t0_stderr_warnings": [WARNING], "constants_created": False,
            "manifest_self": {"path": "simulation/diagnostics/" + PREFIX + "manifest.json",
                              "sha256_lf": None, "csv_rows": None,
                              "reason": "Recursive self-hash excluded"}}
emit("manifest.json", manifest)
print(json.dumps({"status": "HALTED", "constants_created": False,
                  "report": PREFIX + "report.md", "manifest": PREFIX + "manifest.json"}))
