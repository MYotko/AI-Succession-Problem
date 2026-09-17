"""Round 3 stage A, attempt 3: committed-evidence derivation, no model steps."""
import sys
sys.dont_write_bytecode = True
import os
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "simulation" / "diagnostics"
PREFIX = "detector_run_r3_a3_"
for key in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS",
            "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "BLIS_NUM_THREADS"):
    os.environ[key] = "1"
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
os.environ["GIT_OPTIONAL_LOCKS"] = "0"

def allowed(path):
    if isinstance(path, int):
        return path in (0, 1, 2)
    if os.path.normcase(os.path.abspath(os.fsdecode(path))) == os.path.normcase(os.path.abspath(os.devnull)):
        return True
    p = Path(path).resolve()
    return p.parent == OUT and p.name.startswith(PREFIX)

def guard(event, args):
    if event == "open":
        path, mode, flags = args
        writable = any(c in (mode or "") for c in "wax+") or flags & (
            os.O_WRONLY | os.O_RDWR | os.O_APPEND | os.O_CREAT | os.O_TRUNC)
        if writable and not allowed(path):
            raise PermissionError("Out-of-scope writable open: " + str(path))
    elif event in ("os.remove", "os.mkdir", "os.rmdir", "os.chmod", "os.utime", "os.truncate"):
        if not allowed(args[0]):
            raise PermissionError("Out-of-scope mutation")
    elif event in ("os.rename", "os.link", "os.symlink"):
        if not allowed(args[0]) or not allowed(args[1]):
            raise PermissionError("Out-of-scope mutation")
sys.addaudithook(guard)

import csv
import io
import json
import hashlib
import subprocess
import ctypes
import re
from datetime import datetime, timezone
import numpy as np

PRE = json.loads((OUT / (PREFIX + "preflight.json")).read_text(encoding="utf-8"))
HEAD = PRE["head"]
PINS = {r["path"]: r["pin"] for r in PRE["readings"]}
INPUTS = {}
COMMANDS = []
COMPARISONS = []
VERIFICATIONS = []
END_PINS = []
OUTPUTS = [Path(__file__), OUT / (PREFIX + "preflight.json")]
RUNTIME = {"machine": os.environ.get("COMPUTERNAME"), "head": HEAD,
           "python": sys.version, "numpy": np.__version__, "simulation_workers": 0,
           "derivation_processes": 1, "bytecode_disabled": True,
           "write_guard_prefix": PREFIX, "os_devnull_exemption": True}

def sha(raw):
    return hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()

def git(args):
    p = subprocess.run(["git"] + args, cwd=ROOT, capture_output=True)
    COMMANDS.append({"args": args, "exit": p.returncode,
                     "stderr": p.stderr.decode("utf-8", "replace").strip()})
    if p.returncode:
        raise RuntimeError("Read-only git command failed: " + repr(COMMANDS[-1]))
    return p.stdout

def blob(path):
    raw = git(["cat-file", "blob", HEAD + ":" + path])
    item = {"path": path, "read_commit": HEAD, "sha256_lf": sha(raw),
            "blob_sha1": hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()}
    if path in INPUTS and INPUTS[path] != item:
        raise RuntimeError("Input changed: " + path)
    INPUTS[path] = item
    return raw

def pins():
    if git(["rev-parse", "HEAD"]).decode().strip() != HEAD:
        raise RuntimeError("HEAD changed")
    rows = []
    for path, expected in PINS.items():
        raw = blob(path)
        actual = sha((ROOT / path).read_bytes())
        rows.append({"path": path, "expected_sha256_lf": expected,
                     "committed_sha256_lf": sha(raw), "worktree_sha256_lf": actual,
                     "blob_sha1": INPUTS[path]["blob_sha1"]})
        if actual != expected or sha(raw) != expected:
            raise RuntimeError("Source pin mismatch: " + json.dumps(rows[-1]))
    return rows

def emit(name, value, plain=False):
    p = OUT / (PREFIX + name)
    text = value if plain else json.dumps(value, indent=2, ensure_ascii=True, allow_nan=False) + "\n"
    with p.open("x", encoding="utf-8", newline="\n") as f:
        f.write(text)
    OUTPUTS.append(p)

def check(name, derived, pinned):
    row = {"quantity": name, "derived": derived, "pinned": pinned,
           "derived_binary64_hex": float(derived).hex(),
           "pinned_binary64_hex": float(pinned).hex(), "passed": derived == pinned}
    COMPARISONS.append(row)
    if not row["passed"]:
        raise RuntimeError("Pinned-value disagreement: " + json.dumps(row))

def hex_tree(value):
    if isinstance(value, bool) or value is None:
        return value
    if isinstance(value, (int, float)):
        return float(value).hex()
    if isinstance(value, dict):
        return {k: hex_tree(v) for k, v in value.items()}
    if isinstance(value, list):
        return [hex_tree(v) for v in value]
    return value

def table(headers, rows):
    return "\n".join(["| " + " | ".join(headers) + " |",
                      "| " + " | ".join("---" for _ in headers) + " |"] +
                     ["| " + " | ".join(str(v) for v in row) + " |" for row in rows])

def finish_manifest(status, reason=None):
    entries = []
    for p in OUTPUTS:
        raw = p.read_bytes()
        count = None
        if p.suffix == ".csv":
            count = sum(1 for _ in csv.DictReader(io.StringIO(raw.decode("utf-8"))))
        entries.append({"path": p.relative_to(ROOT).as_posix(), "sha256_lf": sha(raw), "csv_rows": count})
    emit("manifest.json", {"status": status, "halt_reason": reason, "head": HEAD,
         "runtime": RUNTIME, "outputs": entries, "hash_basis": "LF-normalized bytes",
         "manifest_self": {"path": "simulation/diagnostics/" + PREFIX + "manifest.json",
                           "sha256_lf": None, "csv_rows": None,
                           "reason": "Recursive self-hash excluded"},
         "inputs": list(INPUTS.values()), "source_pins_start": PRE["readings"],
         "source_pins_end": END_PINS, "command_records": COMMANDS,
         "t0_stderr_warnings": [r["stderr"] for r in PRE["checks"] if r.get("stderr")],
         "created_utc": datetime.now(timezone.utc).isoformat()})

def main():
    start = pins()
    note = blob("simulation/diagnostics/detector_round3_design_note.md").decode("utf-8")
    bias = re.search(r"This observable was chosen knowing how the attack\s+works\.", note).group(0)
    round1 = json.loads(blob("simulation/diagnostics/detector_run_cal_constants.json"))
    round2 = json.loads(blob("simulation/diagnostics/detector_run_r2_constants.json"))
    module_path = "simulation/cusum_detector_v2.py"
    module_raw = blob(module_path)
    namespace = {"__name__": "committed_cusum_detector_v2", "__file__": HEAD + ":" + module_path}
    exec(compile(module_raw, namespace["__file__"], "exec"), namespace)
    channel_cusum = namespace["channel_cusum"]
    RUNTIME["module_hashes"] = {
        module_path: {"sha256_lf": sha(module_raw), "basis": "committed blob, LF-normalized"},
        Path(__file__).relative_to(ROOT).as_posix():
            {"sha256_lf": sha(Path(__file__).read_bytes()), "basis": "working-tree LF-normalized"}}
    libraries = Path(np.__file__).resolve().parent.parent / "numpy.libs"
    threads = []
    for library in libraries.iterdir():
        if "openblas" in library.name.lower() and library.suffix == ".dll":
            lib = ctypes.CDLL(str(library))
            query = lib.scipy_openblas_get_num_threads64_
            query.restype = ctypes.c_int
            threads.append({"library": str(library), "effective_threads": query(),
                            "query": "scipy_openblas_get_num_threads64_"})
    if not threads or any(r["effective_threads"] != 1 for r in threads):
        raise RuntimeError("Numerical-library thread limit not verified: " + repr(threads))
    RUNTIME["numerical_library_threads"] = threads
    axes = ["x_compute", "x_bio_welfare", "x_novelty_agency",
            "x_institutional_capacity", "x_transfer_comprehension", "x_resilience"]
    runs = []
    attempts = {1: 0, 2: 0}
    for seed in range(1835086300, 1835086420):
        cp = "simulation/diagnostics/detector_run_cal_H_" + str(seed) + "_complete.json"
        complete = json.loads(blob(cp))
        raw_path = "simulation/diagnostics/" + complete["raw_log"]
        raw = blob(raw_path)
        verification = {"seed": seed, "completion_path": cp, "raw_log": raw_path,
                        "expected_sha256_lf": complete["raw_log_sha256_lf"],
                        "actual_sha256_lf": sha(raw), "matched": sha(raw) == complete["raw_log_sha256_lf"]}
        VERIFICATIONS.append(verification)
        if not verification["matched"]:
            raise RuntimeError("Input log hash mismatch: " + json.dumps(verification))
        rows = list(csv.DictReader(io.StringIO(raw.decode("utf-8"))))
        selected = [r for r in rows if int(r["step"]) >= 10]
        matrix = np.array([[float(r[a]) for a in axes] for r in selected], dtype=np.float64)
        runs.append({"seed": seed, "steps": [int(r["step"]) for r in selected],
                     "matrix": matrix, "raw_count": len(rows)})
        attempts[complete["attempt"]] += 1
    check("attempt1 logs", attempts[1], 107)
    check("attempt2 logs", attempts[2], 13)
    pooled = np.concatenate([r["matrix"] for r in runs], axis=0)
    medians = np.median(pooled, axis=0)
    expected_medians = [0.13058054663961136, 0.19789308864393101, 0.050694324487428735,
                        0.25643120498706085, 0.27322100367503155, 0.051169013866533296]
    for axis, actual, expected in zip(axes, medians, expected_medians):
        check("median " + axis, float(actual), expected)
    for run in runs:
        run["A"] = np.sum(np.abs(run["matrix"] - medians), axis=1)
        run["transfer_share"] = run["matrix"][:, 4]
        run["compute_share"] = run["matrix"][:, 0]
    channels = {}
    maxima_rows = []
    specs = [
        ("A", "upper", "PRIMARY", 0.27535941373839806, 0.045310678652355926,
         [(97.5, 0.7701182670542909, 3), (95.0, 0.6957853699901844, 6),
          (90.0, 0.6044759669277072, 12)]),
        ("transfer_share", "lower", "SECONDARY, attack-specific",
         0.27322100367503155, 0.034737970363912324, [(97.5, 0.42746784963836376, 3)]),
        ("compute_share", "upper", "SECONDARY, attack-specific",
         0.13058054663961136, 0.04276403212505429, [(97.5, 0.6568684632630958, 3)])]
    for name, direction, role, expected_ref, expected_allowance, thresholds in specs:
        values = np.concatenate([r[name] for r in runs])
        reference = float(np.median(values))
        sigma = float(np.std(values, ddof=1))
        allowance = 0.5 * sigma
        check(name + " reference", reference, expected_ref)
        if name == "A":
            check("A sample standard deviation", sigma, 0.09062135730471185)
        check(name + " allowance", allowance, expected_allowance)
        maxima = []
        for run in runs:
            result = channel_cusum(run["steps"], run[name], reference=reference,
                                   allowance=allowance, direction=direction, threshold=None)
            maximum = float(max(result["statistics"]))
            record = {"seed": run["seed"], "maximum_statistic": maximum,
                      "post_burn_in_records": len(run["steps"])}
            maxima.append(record)
            maxima_rows.append({"channel": name, **record, "maximum_binary64_hex": maximum.hex()})
        threshold_rows = []
        for percentile, expected, expected_count in thresholds:
            threshold = float(np.percentile([r["maximum_statistic"] for r in maxima],
                                            percentile, method="linear"))
            count = sum(r["maximum_statistic"] >= threshold for r in maxima)
            label = "PRIMARY" if name == "A" and percentile == 97.5 else "SECONDARY"
            check(name + " threshold " + str(percentile) + " " + label, threshold, expected)
            check(name + " maxima at or above " + str(percentile), count, expected_count)
            threshold_rows.append({"percentile": percentile, "percentile_method": "linear",
                                   "threshold": threshold, "label": label,
                                   "calibration_runs_at_or_above": count, "calibration_runs": len(runs)})
        channels[name] = {"direction": direction, "role": role, "reference": reference,
                          "sigma_sample_ddof_1": sigma, "allowance": allowance,
                          "record_count": len(values), "thresholds": threshold_rows,
                          "per_run_maxima": maxima}
    carried = {ch: {key: round1["channels"][ch][key]
                    for key in ("reference", "allowance", "threshold")}
               for ch in ("entropy", "g", "L")}
    hazards = {}
    for name, source in round2["sustained_crossing_k"].items():
        hazards[name] = {key: source[key] for key in ("g_star", "k", "label")}
        if "required_section_4_caveat" in source:
            hazards[name]["required_section_4_caveat"] = source["required_section_4_caveat"]
    numeric = {"calibration_run_count": len(runs), "record_count_steps_ge_10": len(pooled),
               "attempt_counts": attempts,
               "median_allocation": {a: float(v) for a, v in zip(axes, medians)},
               "channels": channels, "round1_constants_carried_forward": carried,
               "round2_hazards_carried_forward": hazards}
    END_PINS.extend(pins())
    constants = {"status": "COMPLETE", "stage": "round 3 stage A attempt 3", "head": HEAD,
                 "allocation_share_order": axes, **numeric, "binary64_hex": hex_tree(numeric),
                 "derived_versus_pinned": COMPARISONS, "input_hash_verifications": VERIFICATIONS,
                 "inputs": list(INPUTS.values()), "source_pins_start": start, "source_pins_end": END_PINS,
                 "runtime": RUNTIME, "no_model_stepped": True, "no_arm_run": True,
                 "no_detector_evaluated": True, "no_interpretation": True,
                 "stage_B_requires_separate_dispatch_after_commit_and_push": True}
    emit("constants.json", constants)
    path = OUT / (PREFIX + "per_run_maxima.csv")
    with path.open("x", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["channel", "seed", "maximum_statistic",
                                "post_burn_in_records", "maximum_binary64_hex"], lineterminator="\n")
        writer.writeheader()
        writer.writerows(maxima_rows)
    OUTPUTS.append(path)
    warnings = [r["stderr"] for r in PRE["checks"] if r.get("stderr")]
    doc = ["# Detector round 3, stage A, attempt 3", "",
           "Complete. No model was stepped, no arm was run, no detector was evaluated, and nothing was interpreted. Stage B is a separate dispatch that may begin only after these outputs are committed and pushed.", "",
           "Attempts 1 and 2 each halted in authoring before derivation and produced no constant. This attempt used the same registered scientific procedure. Its script was authored through the shell from one base64 payload and parsed with compile before execution, without bytecode output.", "",
           "From pre-registration Section 1, verbatim:", "",
           "\n".join("> " + line for line in bias.splitlines()), "",
           "## Derived values and pinned values", "",
           "All comparisons below use exact numeric equality without rounding or tolerance.", "",
           table(["Quantity", "Derived", "Pinned", "Matched"],
                 [[r["quantity"], repr(r["derived"]), repr(r["pinned"]), r["passed"]] for r in COMPARISONS]), "",
           "## Evidence and derivation", "",
           f"Counted: {len(runs)} committed completion records and their named logs; {attempts[1]} attempt1 logs and {attempts[2]} attempt2 logs. All 120 log hashes matched their completion records before parsing. Counted raw CSV records: {sum(r['raw_count'] for r in runs)}. Counted records at steps 10 and up: {len(pooled)}.", "",
           "Every committed input was retrieved with git cat-file from " + HEAD + ". Each input's read commit, LF-normalized SHA256, and Git blob SHA1 are recorded in the constants and manifest.", "",
           "The six median shares use the registered order and all records at steps 10 and up. A is the sum of the six absolute deviations. Sample standard deviations use ddof=1, and allowances are half those values. Per-run maxima come from the unchanged committed channel_cusum with threshold=None, without resets. Threshold percentiles use NumPy method='linear'.", "",
           table(["Channel", "Direction", "Role", "Sample standard deviation", "Records"],
                 [[name, d["direction"], d["role"], repr(d["sigma_sample_ddof_1"]), d["record_count"]]
                  for name, d in channels.items()]), "",
           "The constants file includes the 120 seed-labeled maxima behind each channel's thresholds and a binary64 hexadecimal mirror of every numeric constant, count, and per-run value. The maxima CSV has one row per channel and seed. Its row count is recorded in the manifest using csv.DictReader excluding the header.", "",
           "## Carried-forward values", "",
           "The following values were copied from the committed round 1 and round 2 files without recomputation.", "",
           table(["Channel", "Reference", "Allowance", "Threshold"],
                 [[name] + [repr(d[key]) for key in ("reference", "allowance", "threshold")]
                  for name, d in carried.items()]), "",
           table(["Case", "g_star", "k"],
                 [[name, repr(d["g_star"]), d["k"]] for name, d in hazards.items()]), "",
           "> " + hazards["SECONDARY_2_5"]["required_section_4_caveat"], "",
           "## Preconditions and provenance", "",
           "T0a through T0h passed. Branch main; required ancestry and publication checks passed. The exact tracked-only status command returned no output lines. There were 120 calibration-completion paths. The attempt 3 namespace was fresh before artifact creation. The nine artifacts from attempts 1 and 2 were tracked and unmodified. All 14 source pins matched at start and completion.", "",
           table(["Path", "Start LF SHA256", "Completion LF SHA256"],
                 [[r["path"], r["worktree_sha256_lf"],
                   next(e["worktree_sha256_lf"] for e in END_PINS if e["path"] == r["path"])]
                  for r in start]), "",
           f"Machine: {RUNTIME['machine']}. HEAD: {HEAD}. Python: {RUNTIME['python']}. NumPy: {RUNTIME['numpy']}. Simulation workers: 0. Derivation processes: 1. Numerical-library threads: 1, verified from the loaded OpenBLAS runtime.", "",
           "The write guard permitted only detector_run_r3_a3_ files under simulation/diagnostics/ and os.devnull; the null-device exemption was present. Bytecode writes were disabled. No randomness was consumed. Existing working-tree line endings were not changed. The operator performs the containment diff.", "",
           "Known environment conditions were recorded without repair: CRLF working-tree files against LF blobs, and permission warnings from the unreadable cache or global ignore path.", "",
           "T0 stderr warnings:", "", chr(96)*3+"text", "\n".join(warnings) or "None.", chr(96)*3, "",
           "All output hashes use LF-normalized bytes. CSV row counts use csv.DictReader excluding headers, with null for non-CSV outputs. The manifest lists itself separately with a null self-hash to avoid recursive hashing. Committed blob SHA1 values for all three detector notes, both earlier constants files, the detector module, every pinned source, and every calibration input are included.", ""]
    emit("report.md", "\n".join(doc), plain=True)
    finish_manifest("COMPLETE")
    print(json.dumps({"status": "COMPLETE", "runs_read": len(runs),
                      "records_steps_ge_10": len(pooled), "matched_comparisons": len(COMPARISONS),
                      "report": PREFIX + "report.md"}), flush=True)

if __name__ == "__main__":
    try:
        main()
    except BaseException as error:
        details = {"status": "HALTED", "error_type": type(error).__name__, "reason": str(error),
                   "comparisons": COMPARISONS, "input_hash_verifications": VERIFICATIONS,
                   "inputs": list(INPUTS.values()), "runtime": RUNTIME}
        emit("halt.json", details)
        report_path = OUT / (PREFIX + "report.md")
        if not report_path.exists():
            text = "# Detector round 3, stage A, attempt 3: HALTED\n\n" + str(error)
            text += "\n\nNo model was stepped, no arm was run, no detector was evaluated, and nothing was interpreted.\n"
            text += "\nAttempts 1 and 2 halted during authoring before derivation and produced no constant.\n"
            text += "\nStage B requires a separate dispatch after completed stage A outputs are committed and pushed.\n\n"
            text += table(["Quantity", "Derived", "Pinned", "Matched"],
                          [[r["quantity"], repr(r["derived"]), repr(r["pinned"]), r["passed"]]
                           for r in COMPARISONS]) + "\n"
            emit("report.md", text, plain=True)
        finish_manifest("HALTED", str(error))
        print(json.dumps(details), flush=True)
        raise
