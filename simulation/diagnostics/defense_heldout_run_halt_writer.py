"""Record a specification halt without constructing or stepping a model."""
import sys
sys.dont_write_bytecode = True
import os
import pathlib
import json
import hashlib
import subprocess
import datetime
import platform
import importlib.metadata
import time

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / "simulation" / "diagnostics"
PREFIX = "defense_heldout_run_"
DEVNULL = os.path.normcase(os.path.abspath(os.devnull))
RETRIES = []


def allowed(path):
    if isinstance(path, int):
        return True
    p = pathlib.Path(os.fsdecode(path)).resolve()
    return os.path.normcase(str(p)) == DEVNULL or (
        p.parent == OUT and p.name.startswith(PREFIX))


def guard(event, args):
    if event == "open":
        path, mode, flags = args
        write = isinstance(mode, str) and any(c in mode for c in "wax+")
        write = write or (isinstance(flags, int) and bool(flags & (
            os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND)))
        if write and not allowed(path):
            raise PermissionError("Write outside governed prefix: " + str(path))
    elif event in ("os.rename", "os.replace"):
        if not allowed(args[0]) or not allowed(args[1]):
            raise PermissionError("Rename outside governed prefix")
    elif event in ("os.remove", "os.rmdir", "os.mkdir", "os.link", "os.symlink",
                   "os.chmod", "os.utime", "os.truncate"):
        raise PermissionError("Unused filesystem mutation: " + event)


sys.addaudithook(guard)


def sha(data):
    return hashlib.sha256(data.replace(b"\r\n", b"\n")).hexdigest()


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def read_json(path):
    start = time.monotonic()
    while True:
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except PermissionError as exc:
            elapsed = time.monotonic() - start
            RETRIES.append({"utc": now(), "operation": "JSON read", "path": str(path),
                            "elapsed_seconds": elapsed, "error": str(exc)})
            if elapsed >= 5.0:
                raise
            time.sleep(min(0.025, 5.0 - elapsed))


def output(name, value, plain=False):
    text = value if plain else json.dumps(value, indent=2, ensure_ascii=True,
                                          allow_nan=False) + "\n"
    if chr(0x2014) in text:
        raise ValueError("Forbidden editorial punctuation")
    path = OUT / (PREFIX + name)
    with path.open("xb") as f:
        f.write(text.encode("utf-8"))
        f.flush()
        os.fsync(f.fileno())


COMMANDS = []


def git(*args):
    r = subprocess.run(["git", *args], cwd=ROOT, capture_output=True,
                       env={**os.environ, "GIT_OPTIONAL_LOCKS": "0"})
    COMMANDS.append({"command": ["git", *args], "exit_code": r.returncode,
                     "stderr": r.stderr.decode("utf-8", "replace")})
    if r.returncode:
        raise RuntimeError("Read-only git command failed: " + " ".join(args))
    return r.stdout


def main():
    evidence = read_json(OUT / (PREFIX + "preflight.json"))
    start = dict(evidence["source_readings"])
    start.update(evidence["inherited_source_evidence"]["sources"])
    head = git("rev-parse", "HEAD").decode().strip()
    end = {}
    changed = []
    for path, first in start.items():
        blob = git("cat-file", "blob", "HEAD:" + path)
        latest = git("log", "-1", "--format=%H", "--", path).decode().strip()
        git("merge-base", "--is-ancestor", latest, "origin/main")
        end[path] = {
            "committed_sha256_lf": sha(blob),
            "working_tree_sha256_lf": sha((ROOT / path).read_bytes()),
            "committed_blob_sha1": git("rev-parse", "HEAD:" + path).decode().strip(),
            "last_modified_commit": latest, "read_commit": head,
        }
        if any(end[path][key] != first[key] for key in (
                "committed_sha256_lf", "working_tree_sha256_lf",
                "committed_blob_sha1", "last_modified_commit")):
            changed.append(path)
    if head != evidence["head"]:
        changed.append("HEAD")

    conflicts = [
        {
            "id": "Y3_SIGN_FIXTURE_CONFLICT",
            "source": "Held-out note Section 6 and dispatch sign fixture",
            "difference": "OFF minus GRADED",
            "per_run_quantity": "population at step 149 minus population at step 160",
            "harm_direction": "positive",
            "required_fixture": "Larger defended shock loss must be labeled harm",
            "conflict": "A larger GRADED shock loss produces a negative OFF-minus-GRADED "
                        "difference, incompatible with the required positive harm direction.",
        },
        {
            "id": "PREDICTION_REPORTING_CONFLICT",
            "source": "Held-out note Section 6 and dispatch",
            "note": "Registered predictions, written before any run and reported as right or wrong.",
            "dispatch": "do not say whether a registered prediction was right or wrong "
                        "beyond reporting the number the prediction names",
            "conflict": "The note requires right-or-wrong prediction reporting and the "
                        "dispatch prohibits it, while requiring a halt on conflicts.",
        },
    ]
    status = {
        "status": "HALTED",
        "phase": "After T0 and committed-note reading, before T1",
        "halt_reason": "Conflicting specification requirements",
        "conflicts": conflicts, "runs_planned": 160, "runs_launched": 0,
        "runs_completed": 0, "model_steps": 0, "T0": evidence["status"],
        "T1": "NOT_RUN", "sign_fixture": "NOT_RUN",
        "analysis": "NOT_RUN", "source_changes_at_halt": changed, "utc": now(),
    }
    if changed:
        status["additional_halt_reason"] = "Source identity changed at halt verification"
    environment = {
        "machine": platform.node(), "head": head, "python": sys.version,
        "python_executable": sys.executable, "platform": platform.platform(),
        "numpy_version": importlib.metadata.version("numpy"),
        "numpy_version_basis": "Installed distribution metadata; NumPy not imported",
        "logical_cpu_count": os.cpu_count(), "operator_cpu_budget": 16,
        "operating_mode": "normal", "simulation_worker_limit": 15,
        "workers_launched": 0, "required_numerical_threads_per_worker": 1,
        "numerical_thread_verification": "Not applicable: no worker launched",
        "bytecode_writes_disabled": sys.dont_write_bytecode,
    }
    output("halt.json", status)
    output("results.json", {
        **status,
        "registered_results": {q: {"status": "NOT_COMPUTED", "values": None}
                               for q in ("Y1", "Y2", "Y3", "Y4", "Y5")},
        "criterion_applied": False, "prediction_assessments": None,
        "interpretation": None,
    })
    report = [
        "# Held-out attacks: execution halt", "",
        "Status: HALTED after T0 and committed-note reading, before T1.",
        "Planned runs: 160. Launched runs: 0. Completed runs: 0. Model steps: 0.", "",
        "This is gate 2 of the promotion plan. The attacks were specified before any run.",
        "This is not a promotion decision. This does not test input corruption, which "
        "the note defers to stage B. No ratio of two measured counts was computed.",
        "Applying the Section 6 criterion and the Section 8 interpretation is reserved "
        "for the operator.", "",
        "## Registered quantities", "",
        "| Quantity | Status |", "| --- | --- |",
    ]
    report += ["| " + q + " | Not computed |" for q in ("Y1", "Y2", "Y3", "Y4", "Y5")]
    report += [
        "", "## Sign fixture", "",
        "Not run. No assertion result is claimed. The specification conflict was "
        "identified before T1 or analysis.", "",
        "## Halt reasons", "",
        "1. Section 6 defines Y3 as OFF minus GRADED for population at step 149 minus "
        "population at step 160 and states that positive Y3 is harm. The required "
        "fixture has a larger defended shock loss, producing a negative OFF-minus-GRADED "
        "difference, and must be labeled harm. Both requirements cannot be met unchanged.",
        '2. Section 6 says: "Registered predictions, written before any run and reported '
        'as right or wrong." The dispatch prohibits saying whether a prediction was '
        "right or wrong beyond reporting its named number. The dispatch requires a halt "
        "on conflicts with the note.", "",
        "No requirement was changed. No model was constructed or stepped. No attack, "
        "defense, registered quantity, criterion, or prediction was evaluated.", "",
        "## Preconditions and source readings", "",
        "T0a through T0e passed. The three governing notes were read by git cat-file "
        "after verification of their committed and working-tree hashes.",
        "Inherited pins and declared source identities were recorded for halt evidence. "
        "All hashes in the following table use LF-normalized bytes.", "",
        "| Source | Start committed | Start working tree | Halt committed | Halt working tree |",
        "| --- | --- | --- | --- | --- |",
    ]
    for path, first in start.items():
        report.append("| " + " | ".join([
            path, first["committed_sha256_lf"], first["working_tree_sha256_lf"],
            end[path]["committed_sha256_lf"], end[path]["working_tree_sha256_lf"]]) + " |")
    report += [
        "", "Source identities changed: " + json.dumps(changed) + ".",
        "HEAD: " + head + ".", "", "## Operational record", "",
        "Workers launched: 0. No resumption, merge, or per-run deletion occurred.",
        "No code was copied or imported from the committed executors. Their hashes "
        "identify declared source provenance.",
        "Manifest hashes cover every generated artifact other than the manifest "
        "itself, whose self-hash would be recursive.", "",
        "Machine: " + environment["machine"] + ".",
        "Python: " + platform.python_version() + ".",
        "NumPy: " + environment["numpy_version"] + " (installed distribution metadata).",
        "", "T0 stderr warnings:", "",
    ]
    report += ["    " + w["stderr"].rstrip() for w in evidence["stderr_warnings"]]
    report += ["", "Tool-layer workarounds:", ""]
    report += evidence["tool_layer_workarounds"]
    report += ["", "Permission retry events: " + str(len(RETRIES)) + ".", ""]
    output("report.md", "\n".join(report), plain=True)

    outputs = []
    for name in ("halt_writer.py", "preflight.json", "halt.json", "results.json", "report.md"):
        path = OUT / (PREFIX + name)
        data = path.read_bytes()
        outputs.append({
            "path": path.relative_to(ROOT).as_posix(), "sha256_lf": sha(data),
            "sha256_basis": "SHA256 after CRLF-to-LF normalization",
            "csv_row_count": None, "size_bytes": len(data),
        })
    output("manifest.json", {
        "status": "HALTED", "halt": status, "environment": environment,
        "outputs": outputs,
        "manifest_self": {
            "path": "simulation/diagnostics/" + PREFIX + "manifest.json",
            "sha256_lf": None, "csv_row_count": None,
            "reason": "Manifest self-hash excluded because it would be recursive",
        },
        "source_readings": {p: {"start": first, "completion": end[p]}
                            for p, first in start.items()},
        "committed_blob_sha1": {p: first["committed_blob_sha1"] for p, first in start.items()},
        "per_module_sha256": {
            p: {"sha256_lf": first["committed_sha256_lf"],
                "basis": "LF-normalized committed blob", "read_commit": first["read_commit"],
                "imported_for_this_task": False}
            for p, first in start.items() if p.endswith(".py")
        },
        "halt_writer_sha256_lf": sha(pathlib.Path(__file__).read_bytes()),
        "write_guard": "Only governed filename prefix and os.devnull",
        "source_reverification_commands": COMMANDS,
        "merge": {
            "status": "NOT_RUN", "reason": "Halted before T1; zero runs launched",
            "merged_files": [], "per_run_hashes_and_counts": [],
            "deleted_file_counts": {"step_logs": 0, "completion_records": 0,
                                    "progress": 0, "initial": 0, "console": 0},
        },
        "resumed_seeds": [], "retry_events": RETRIES,
        "tool_layer_workarounds": evidence["tool_layer_workarounds"],
        "T0_stderr_warnings": evidence["stderr_warnings"],
        "no_interpretation": True,
    })
    print("HALTED: specification conflicts; 0 of 160 runs launched; report, results, manifest written.")


if __name__ == "__main__":
    main()
