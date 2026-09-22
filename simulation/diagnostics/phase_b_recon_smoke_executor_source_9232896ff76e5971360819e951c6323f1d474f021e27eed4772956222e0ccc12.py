"""Phase B reconstruction. Test mode is non-registered and never evidence for fidelity.

Unvaried parameters use production defaults: phi=25, alpha=1, initial successor
capability=1. The successor is generation 2. No scientific output changes the grid.
Only the operator may launch the measured batch.
"""
import sys
sys.dont_write_bytecode = True
import argparse
import collections
import csv
import ctypes
import hashlib
import io
import itertools
import json
import os
import platform
import random
import re
import subprocess
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DIAG = ROOT / "simulation" / "diagnostics"
V20_HEAD = "2044f50a8cf71874f259e74fd05ec495169b9ae4"
NOTE_COMMIT = "20a6327a289b94fade04c915c6e38ff495cf3468"
PINS = {
 "simulation/diagnostics/phase_b_reconstruction_design_note.md": "c6416f59660210f14f4c0d8e70423570f58a1c6749768b89d6985f39e67f5a0d",
 "simulation/diagnostics/ARTIFACT_CONVENTION.md": "def9d1d57053310335541bb4bf22cdfb1f9449fb569ad8cce39693442cc461eb",
 "simulation/model.py": "25e65d8daa4332df32198b424b25b1630d7a5aca98971c47eac82df7d5679993",
 "simulation/agents.py": "a51f6d833fa2e228aaa4e95ca59f9c7e0f83e5741c94deef88a0ea895554cfca",
 "simulation/metrics.py": "6dc16efdfd4faed1638a96f6c2af7365757d1ca47eeb86deb5619a3e580b901f",
}
THREAD_ENV = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
              "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "BLIS_NUM_THREADS")
RETRIES = []
SCHEMA = {
 "rr": float, "phi": float, "alpha": float, "successor_capability": float,
 "cop_cost_audit": bool, "seed": int, "survived": bool, "collapsed": bool,
 "extinct": bool, "final_population": int, "final_ai_generation": int,
 "yield_fired": bool, "max_yield_margin": float, "knowledge_transfer_verified": bool,
 "steps_completed": int, "end_reason": str, "substrate": str, "category": str,
}
KEYS = ["substrate", "category", "cell", "seed"]
ROW_FIELDS = KEYS + [k for k in SCHEMA if k not in KEYS] + [
 "peak_population", "min_viable_population", "survival_threshold", "elapsed_seconds",
 "source_path", "source_head", "non_registered", "worker_pid",
]
STEP_FIELDS = KEYS + ["step", "population", "ai_generation", "x_transfer_comprehension",
                     "yield_event", "datacollector"]
BOOTSTRAP = ("import json,runpy,sys; "
             "ns=runpy.run_path(sys.argv[1],run_name='recon_worker'); "
             "ns['worker'](json.loads(sys.stdin.read()))")

def utc():
    return datetime.now(timezone.utc).isoformat()

def digest(data):
    return hashlib.sha256(data.replace(b"\r\n", b"\n")).hexdigest()

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)

def git(root, *args):
    p = subprocess.run(["git", "-c", "safe.directory=" + str(root).replace("\\", "/"),
                        "-C", str(root), *args], capture_output=True)
    if p.returncode:
        raise RuntimeError(p.stderr.decode("utf-8", "replace"))
    return p.stdout

def install_guard(prefix):
    protected = {str((ROOT / p).resolve()).lower()
                 for p in git(ROOT, "ls-files").decode().splitlines()}
    def allowed(value):
        if isinstance(value, int):
            return True
        p = Path(os.fsdecode(value)).resolve()
        if p == Path(os.devnull).resolve():
            return True
        excluded = p.name in (
            "phase_b_reconstruction_design_note.md", "phase_b_recon_halt.json",
            "phase_b_recon_manifest.json", "phase_b_recon_preflight.json",
            "phase_b_recon_report.md") or p.name.startswith((
                "phase_b_recon_b2_", "phase_b_recon_b3_", "phase_b_recon_b4_"))
        return (p.parent == DIAG and str(p).lower() not in protected and
                p.name.startswith("phase_b_recon_") and not excluded)
    def audit(event, args):
        if event == "open":
            p, mode, flags = args
            writing = (isinstance(mode, str) and any(c in mode for c in "wax+"))
            writing |= isinstance(flags, int) and bool(flags & (
                os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND))
            if writing and not allowed(p):
                raise PermissionError("Write outside scope: " + str(p))
        elif event in ("os.remove", "os.rmdir", "os.mkdir", "os.chmod", "os.utime", "os.truncate"):
            if not allowed(args[0]):
                raise PermissionError("Write outside scope: " + str(args[0]))
        elif event in ("os.rename", "os.link", "os.symlink"):
            if not all(allowed(p) for p in args[:2]):
                raise PermissionError("Write outside scope")
    sys.addaudithook(audit)

def retry(operation, path, function):
    start = time.monotonic()
    while True:
        try:
            return function()
        except PermissionError as exc:
            RETRIES.append({"utc": utc(), "operation": operation, "path": str(path),
                            "error": str(exc), "pid": os.getpid()})
            if time.monotonic() - start >= 5:
                raise
            time.sleep(0.05)

def read_json(path):
    return retry("read_json", path, lambda: json.loads(path.read_text(encoding="utf-8")))

def atomic_bytes(path, data):
    temp = path.with_name(path.name + ".tmp." + str(os.getpid()))
    with temp.open("wb") as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())
    retry("atomic_replace", path, lambda: os.replace(temp, path))

def atomic_json(path, value):
    atomic_bytes(path, (json.dumps(value, indent=2, allow_nan=False) + "\n").encode())

def csv_bytes(rows, fields, header=False):
    out = io.StringIO(newline="")
    writer = csv.DictWriter(out, fieldnames=fields, lineterminator="\n")
    if header:
        writer.writeheader()
    writer.writerows(rows)
    return out.getvalue().encode()

def job_id(task):
    return "_".join(str(task[k]) for k in KEYS)

def paths(prefix, task):
    stem = prefix + "job_" + job_id(task)
    return {k: DIAG / (stem + suffix) for k, suffix in {
        "completion": "_completion.json", "row": "_row.csv", "steps": "_steps.csv",
        "initial": "_initial.json", "progress": "_progress.json", "console": "_console.txt",
    }.items()}

def grid(test=False):
    specs = {
        "A": ([.055,.056,.057,.058,.059,.060,.062,.064,.066], [5.,10.,25.,100.], [.5,1.,1.5], [1.], [True], 1835089000, 25),
        "B": ([.057,.060,.064,.070], [25.], [.5,.75,1.,1.25,1.5], [1.2,1.5,2.,2.5,3.,4.,5.], [True], 1835089100, 20),
        "C": ([.057,.060,.064], [25.], [.5,1.,1.5], [1.5,2.5,3.], [True,False], 1835089200, 30),
        "phi": ([.057], [2.,5.,10.,15.,20.,25.,30.], [1.], [1.], [True], 1835089300, 60),
    }
    if test:
        specs = {
            "A": ([.055,.066], [25.], [1.], [1.], [True], 1835089000, 2),
            "B": ([.060], [25.], [.5,1.5], [1.5,5.], [True], 1835089100, 2),
            "C": ([.060], [25.], [1.], [2.5], [True,False], 1835089200, 2),
            "phi": ([.057], [2.,20.], [1.], [1.], [True], 1835089300, 2),
        }
    tasks = []
    for substrate in ("v21", "v20"):
        for category, spec in specs.items():
            for cell_no, values in enumerate(itertools.product(*spec[:5])):
                params = dict(zip(("rr", "phi", "alpha", "successor_capability", "cop_cost_audit"), values))
                # IDs depend on exact parameter values, never ordering or workers.
                cell = hashlib.sha256(canonical(params).encode()).hexdigest()[:16]
                for seed in range(spec[5], spec[5] + spec[6]):
                    tasks.append(dict(params, substrate=substrate, category=category,
                                      cell=cell, seed=seed, non_registered=test))
    return tasks

def assert_grids():
    full = grid(False)
    for sub in ("v21", "v20"):
        assert collections.Counter(t["category"] for t in full if t["substrate"] == sub) == {
            "A":2700, "B":2800, "C":1620, "phi":420}
    smoke = grid(True)
    assert len(smoke) == 40 and len({job_id(t) for t in smoke}) == 40
    assert all(sum(t["substrate"] == s for t in smoke) == 20 for s in ("v21", "v20"))
    return {"full_per_substrate": {"A":2700,"B":2800,"C":1620,"phi":420},
            "full_both":15080, "smoke_per_substrate":20, "smoke_both":40}

def verify_pins():
    readings = []
    for path, pin in PINS.items():
        blob = git(ROOT, "cat-file", "blob", "HEAD:" + path)
        actual = digest((ROOT / path).read_bytes())
        assert digest(blob) == actual == pin, "Source pin changed: " + path
        readings.append({"path":path, "pin":pin, "committed_sha256_lf":digest(blob),
                         "working_tree_sha256_lf":actual,
                         "blob_sha1":git(ROOT,"rev-parse","HEAD:"+path).decode().strip()})
    git(ROOT, "merge-base", "--is-ancestor", NOTE_COMMIT, "origin/main")
    git(ROOT, "merge-base", "--is-ancestor", NOTE_COMMIT, "HEAD")
    return readings

def source_identity(root):
    head = git(root, "rev-parse", "HEAD").decode().strip()
    entries = {}
    files = git(root, "ls-tree", "-r", "--name-only", "HEAD", "simulation").decode().splitlines()
    for path in files:
        if path.endswith(".py") and "/diagnostics/" not in path:
            data = (root / path).read_bytes()
            blob = git(root, "cat-file", "blob", "HEAD:" + path)
            assert digest(data) == digest(blob), "Worktree source differs: " + path
            entries[path] = digest(data)
    return {"path": str(root), "head": head, "modules_sha256_lf": entries}

def effective_threads(np):
    np.dot(np.ones((2, 2)), np.ones((2, 2)))
    found = []
    libdir = Path(np.__file__).resolve().parent.parent / "numpy.libs"
    for dll in libdir.glob("*"):
        if "openblas" not in dll.name.lower():
            continue
        lib = ctypes.CDLL(str(dll))
        for name in ("scipy_openblas_get_num_threads64_", "openblas_get_num_threads64_",
                     "scipy_openblas_get_num_threads", "openblas_get_num_threads"):
            if hasattr(lib, name):
                fn = getattr(lib, name)
                fn.argtypes = []
                fn.restype = ctypes.c_int
                count = fn()
                found.append({"library":str(dll), "symbol":name, "threads":count})
                assert count == 1, "Numerical thread count exceeds one"
                break
    assert found, "Could not verify effective numerical thread limit"
    return found

def imported_sources(source):
    root = Path(source["path"]).resolve()
    result = {}
    for name, module in list(sys.modules.items()):
        f = getattr(module, "__file__", None)
        if not f or not str(f).endswith(".py"):
            continue
        path = Path(f).resolve()
        try:
            rel = path.relative_to(root).as_posix()
        except ValueError:
            if path.is_relative_to(ROOT / "simulation") and path != Path(__file__).resolve():
                raise AssertionError("Substrate import contamination: " + str(path))
            continue
        if rel.startswith("simulation/") and "/diagnostics/" not in rel:
            actual = digest(path.read_bytes())
            assert source["modules_sha256_lf"].get(rel) == actual, "Imported source changed: " + rel
            result[name] = {"path":str(path), "sha256_lf":actual}
    return result

def worker(job):
    prefix = job["prefix"]
    install_guard(prefix)
    assert_grids()
    for key in THREAD_ENV:
        assert os.environ.get(key) == "1"
    task, source = job["task"], job["source"]
    source_root = Path(source["path"]).resolve()
    assert git(source_root,"rev-parse","HEAD").decode().strip() == source["head"]
    if task["substrate"] == "v20":
        assert source["head"] == V20_HEAD
    # Fresh interpreter per task. No model from the other substrate can be cached.
    sys.path[:] = [str(source_root / "simulation"), str(source_root)] + [
        p for p in sys.path if p and not Path(p).resolve().is_relative_to(ROOT)]
    import numpy as np
    import model as model_module
    from agents import AIAgent
    from model import GardenModel
    thread_check = effective_threads(np)
    before_sources = imported_sources(source)
    assert Path(model_module.__file__).resolve() == source_root / "simulation" / "model.py"
    filepaths = paths(prefix, task)
    if job.get("probe_tag"):
        filepaths = {k:p.with_name(p.name.replace(prefix+"job_", prefix+"probe_"+job["probe_tag"]+"_")) for k,p in filepaths.items()}
    start = time.monotonic()
    config = {"policy":"optimize_u_sys_v2", "random_seed":task["seed"],
              "reproduction_rate":task["rr"], "phi":task["phi"], "alpha":task["alpha"],
              "mortality_base":0.002, "carrying_capacity":10000}
    random.seed(task["seed"])
    np.random.seed(task["seed"])
    initial = {"key":{k:task[k] for k in KEYS}, "task":task, "config":config,
               "source":source, "code_sha256_lf":job["code_sha256_lf"],
               "started_utc":utc(), "pid":os.getpid(),
               "thread_environment":{k:os.environ[k] for k in THREAD_ENV},
               "effective_threads":thread_check, "non_registered":task["non_registered"]}
    atomic_json(filepaths["initial"], initial)
    successor = AIAgent(policy="optimize_u_sys_v2", generation=2,
                        capability=task["successor_capability"], config=config)
    model = GardenModel(n_agents=200, ai_policy="optimize_u_sys_v2",
                        successor_ai=successor, cop_cost_audit=task["cop_cost_audit"],
                        config=config)
    assert model.is_v2_mode and model.successor_ai is not None
    assert model.n_agents == 200 and model.config["mortality_base"] == 0.002
    assert model.config["carrying_capacity"] == 10000
    assert model.cop_cost_audit is task["cop_cost_audit"]
    assert "beta_cap" not in model.config and "adapter_attack" not in model.config
    productions = {name:getattr(model_module,name) for name in
                   ("adapt_v2_action", "adapt_yield_evaluation", "ratify_v2_yield")}
    def clean(v):
        if isinstance(v, np.generic):
            return clean(v.item())
        if isinstance(v, dict):
            return {str(k):clean(x) for k,x in v.items()}
        if isinstance(v, (list, tuple)):
            return [clean(x) for x in v]
        if isinstance(v, float) and not __import__("math").isfinite(v):
            return str(v)
        return v
    step_count = 0
    end_reason = "step_limit"
    last_progress = 0.
    with filepaths["steps"].open("w",encoding="utf-8",newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=STEP_FIELDS, lineterminator="\n")
        writer.writeheader()
        for step in range(300):
            continuing = model.step()
            step_count += 1
            dc = model.datacollector
            assert len(dc["population"]) == step_count, "Completed/recorded step mismatch"
            event = next((e for e in reversed(model.yield_event_log) if e["step"] == step), None)
            values = {name:clean(v[-1]) for name,v in dc.items() if v}
            writer.writerow(dict({k:task[k] for k in KEYS}, step=step,
                                 population=int(dc["population"][-1]),
                                 ai_generation=int(model.ai.generation),
                                 x_transfer_comprehension=float(dc["x_transfer_comprehension"][-1]),
                                 yield_event=canonical(clean(event)), datacollector=canonical(values)))
            now = time.monotonic()
            if now-last_progress >= 10:
                stream.flush()
                atomic_json(filepaths["progress"], {"key":initial["key"], "pid":os.getpid(),
                            "steps_completed":step_count, "updated_utc":utc(),
                            "elapsed_seconds":now-start})
                last_progress = now
            if not continuing:
                end_reason = "step_returned_false"
                break
        stream.flush()
        os.fsync(stream.fileno())
    assert all(getattr(model_module,k) is obj for k,obj in productions.items())
    events = model.yield_event_log
    fires = [e for e in events if e["fires"]]
    assert events, "Successor present but no yield evaluations recorded"
    margins = [float(e["successor_u_sys"])-float(e["incumbent_u_sys"])-float(e["transition_cost"]) for e in events]
    final = int(dc["population"][-1])
    peak = int(max(dc["population"]))
    threshold = max(model.min_viable_population, 0.65*peak)
    row = {k:task[k] for k in KEYS}
    row.update({k:task[k] for k in ("rr","phi","alpha","successor_capability","cop_cost_audit")})
    row.update(survived=bool(final >= threshold), collapsed=bool(0 < final < threshold),
               extinct=bool(final == 0), final_population=final,
               final_ai_generation=int(model.ai.generation), yield_fired=bool(fires),
               max_yield_margin=float(max(margins)),
               knowledge_transfer_verified=bool(fires and max(float(v) for v in dc.get("x_transfer_comprehension",[0.0])) >= 0.10),
               steps_completed=step_count, end_reason=end_reason,
               peak_population=peak, min_viable_population=int(model.min_viable_population),
               survival_threshold=float(threshold), elapsed_seconds=time.monotonic()-start,
               source_path=str(source_root), source_head=source["head"],
               non_registered=task["non_registered"], worker_pid=os.getpid())
    for key, typ in SCHEMA.items():
        assert type(row[key]) is typ, "Incorrect field type: "+key
    assert step_count == 300 or end_reason == "step_returned_false"
    after_sources = imported_sources(source)
    assert all(after_sources[k] == v for k,v in before_sources.items())
    assert git(source_root,"rev-parse","HEAD").decode().strip() == source["head"]
    row_data = csv_bytes([row], ROW_FIELDS)
    atomic_bytes(filepaths["row"], csv_bytes([row], ROW_FIELDS, header=True))
    step_lines = filepaths["steps"].read_bytes().splitlines(keepends=True)
    assert len(step_lines)-1 == step_count
    completion = {
        "key":initial["key"], "task":task, "row":row,
        "code_sha256_lf":job["code_sha256_lf"], "source":source,
        "row_sha256_lf":digest(row_data), "step_row_count":step_count,
        "steps_sha256_lf":digest(b"".join(step_lines[1:])),
        "completed_utc":utc(), "effective_threads":thread_check,
        "thread_environment":initial["thread_environment"], "numpy_version":np.__version__,
        "python":sys.version, "modules":after_sources, "retry_events":RETRIES,
        "production_objects_unchanged":True, "initial_config":config,
    }
    atomic_json(filepaths["completion"], completion)

def read_completion(path, expected, code, sources):
    try:
        obj = read_json(path)
        if obj.get("key") != {k:expected[k] for k in KEYS}:
            return None
        assert obj["task"] == expected, "Completion configuration differs"
        assert obj["code_sha256_lf"] == code, "Completion executor code differs"
        assert obj["source"] == sources[expected["substrate"]], "Completion substrate differs"
        assert digest(csv_bytes([obj["row"]], ROW_FIELDS)) == obj["row_sha256_lf"]
        for key, typ in SCHEMA.items():
            assert type(obj["row"][key]) is typ
        return obj
    except (json.JSONDecodeError, UnicodeError, KeyError, TypeError):
        return None

def launch(job):
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    for key in THREAD_ENV:
        env[key] = "1"
    fp = paths(job["prefix"], job["task"])
    if job.get("probe_tag"):
        fp = {k:p.with_name(p.name.replace(job["prefix"]+"job_",
              job["prefix"]+"probe_"+job["probe_tag"]+"_")) for k,p in fp.items()}
    console = fp["console"].open("wb")
    proc = subprocess.Popen([sys.executable, "-B", "-c", BOOTSTRAP, str(Path(__file__).resolve())],
                            stdin=subprocess.PIPE, stdout=console, stderr=subprocess.STDOUT,
                            cwd=job["source"]["path"], env=env,
                            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    proc.stdin.write(json.dumps(job).encode())
    proc.stdin.close()
    return proc, console

def category_files(prefix, category):
    return {kind:DIAG/(prefix+category+"_"+suffix) for kind,suffix in {
        "rows":"runs.csv", "steps":"steps.csv", "completions":"completions.jsonl"}.items()}

def merged_records(prefix):
    records = {}
    for category in ("A","B","C","phi"):
        path = category_files(prefix,category)["completions"]
        if path.exists():
            with path.open(encoding="utf-8") as f:
                for line in f:
                    record = json.loads(line)
                    ident = job_id(record["key"])
                    assert ident not in records, "Duplicate merged completion"
                    records[ident] = record
    return records

def merge_category(prefix, category, records, manifest, manifest_path):
    files = category_files(prefix,category)
    old = {}
    if files["steps"].exists():
        with files["steps"].open(newline="",encoding="utf-8") as f:
            for row in csv.DictReader(f):
                old.setdefault(job_id(row), []).append(row)
    ordered = sorted((r for r in records.values() if r["key"]["category"] == category),
                     key=lambda r:tuple(r["key"][k] for k in KEYS))
    step_rows = []
    run_rows = []
    for record in ordered:
        task = record["task"]
        ident = job_id(task)
        fp = paths(prefix,task)
        if fp["steps"].exists():
            with fp["steps"].open(newline="",encoding="utf-8") as f:
                steps = list(csv.DictReader(f))
        else:
            steps = old[ident]
        assert len(steps) == record["step_row_count"]
        assert digest(csv_bytes(steps, STEP_FIELDS)) == record["steps_sha256_lf"]
        assert all(job_id(s) == ident for s in steps)
        row = record["row"]
        assert digest(csv_bytes([row], ROW_FIELDS)) == record["row_sha256_lf"]
        if fp["row"].exists():
            with fp["row"].open(newline="",encoding="utf-8") as f:
                original_rows = list(csv.DictReader(f))
            assert len(original_rows) == 1
            assert digest(csv_bytes(original_rows,ROW_FIELDS)) == record["row_sha256_lf"]
        step_rows.extend(steps)
        run_rows.append(row)
    atomic_bytes(files["rows"], csv_bytes(run_rows, ROW_FIELDS, header=True))
    atomic_bytes(files["steps"], csv_bytes(step_rows, STEP_FIELDS, header=True))
    atomic_bytes(files["completions"], ("".join(canonical(r)+"\n" for r in ordered)).encode())
    with files["rows"].open(newline="",encoding="utf-8") as f:
        recovered_rows = list(csv.DictReader(f))
    with files["steps"].open(newline="",encoding="utf-8") as f:
        recovered_steps = list(csv.DictReader(f))
    assert len(recovered_rows) == len(ordered)
    by_row = collections.defaultdict(list)
    by_step = collections.defaultdict(list)
    for row in recovered_rows:
        by_row[job_id(row)].append(row)
    for row in recovered_steps:
        by_step[job_id(row)].append(row)
    for r in ordered:
        ident = job_id(r["key"])
        assert len(by_row[ident]) == 1
        assert digest(csv_bytes(by_row[ident], ROW_FIELDS)) == r["row_sha256_lf"]
        assert len(by_step[ident]) == r["step_row_count"]
        assert digest(csv_bytes(by_step[ident], STEP_FIELDS)) == r["steps_sha256_lf"]
        manifest.setdefault("runs", {})[ident] = {
            "key":r["key"], "row_count":1, "row_sha256_lf":r["row_sha256_lf"],
            "step_row_count":r["step_row_count"], "steps_sha256_lf":r["steps_sha256_lf"]}
    reread = [json.loads(line) for line in files["completions"].read_text().splitlines()]
    assert reread == ordered
    manifest.setdefault("merged_files", {})[category] = {
        k:{"path":str(p), "sha256_lf":digest(p.read_bytes()),
           "row_count":len(step_rows) if k=="steps" else len(ordered)} for k,p in files.items()}
    atomic_json(manifest_path, manifest)
    # Evidence is verified and recorded before any per-run copy is removed.
    for r in ordered:
        for kind, path in paths(prefix,r["task"]).items():
            if path.exists():
                path.unlink()
                deleted = manifest.setdefault("deleted_per_run_files", {})
                deleted[kind] = deleted.get(kind,0)+1
    atomic_json(manifest_path, manifest)

def cpu_budget():
    if platform.node().lower() == "yotkotest":
        return 16
    return getattr(os,"process_cpu_count",os.cpu_count)() or 1

def worker_limit(requested, budget, mode, runnable):
    # Explicit --workers is still subject to the standing normal/work budgets.
    return min(requested, max(1,budget-(4 if mode=="work" else 1)), runnable)

def parse_args(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--workers",type=int,default=8)
    p.add_argument("--category",nargs="+",choices=("A","B","C","phi"),default=["A","B","C","phi"])
    p.add_argument("--substrate",choices=("v21","v20","both"),default="both")
    p.add_argument("--v20-worktree")
    p.add_argument("--resume",action="store_true")
    p.add_argument("--test-mode",action="store_true")
    p.add_argument("--out-prefix",default="phase_b_recon_")
    args = p.parse_args(argv)
    if args.workers < 1:
        p.error("--workers must be positive")
    if args.substrate != "v21" and not args.v20_worktree:
        p.error("--v20-worktree is required for v20")
    if args.test_mode:
        args.out_prefix = "phase_b_recon_smoke_"
    if not re.fullmatch(r"phase_b_recon_[A-Za-z0-9_]*",args.out_prefix):
        p.error("--out-prefix must be a filename prefix beginning phase_b_recon_")
    return args

def main(argv=None):
    args = parse_args(argv)
    prefix = args.out_prefix
    install_guard(prefix)
    counts = assert_grids()
    pin_readings = verify_pins()
    sources = {}
    if args.substrate in ("v21","both"):
        sources["v21"] = source_identity(ROOT)
    if args.substrate in ("v20","both"):
        root20 = Path(args.v20_worktree).resolve()
        assert git(root20,"rev-parse","HEAD").decode().strip() == V20_HEAD, "v20 HEAD differs"
        sources["v20"] = source_identity(root20)
    code = digest(Path(__file__).read_bytes())
    tasks = [t for t in grid(args.test_mode)
             if t["category"] in args.category and t["substrate"] in sources]
    task_by_id = {job_id(t):t for t in tasks}
    manifest_path = DIAG/(prefix+"batch_manifest.json")
    control_path = DIAG/(prefix+"runtime_control.json")
    progress_path = DIAG/"phase_b_recon_progress.json"
    previous = read_json(manifest_path) if manifest_path.exists() else None
    if previous:
        assert args.resume, "Existing batch requires --resume"
        assert previous["executor_sha256_lf"] == code, "Executor changed since previous invocation"
        for sub, src in sources.items():
            if sub in previous["sources"]:
                assert previous["sources"][sub] == src, "Source identity changed on resume"
    else:
        assert not list(DIAG.glob(prefix+"job_*")), "Unowned per-run files exist"
    manifest = previous or {
        "schema_version":1, "created_utc":utc(), "sources":{}, "invocations":[],
        "started":{}, "runs":{}, "merged_files":{}, "retry_events":[],
        "executor_sha256_lf":code, "grid_counts":counts,
        "pre_registration_blob_sha1":pin_readings[0]["blob_sha1"],
        "initial_pin_readings":pin_readings, "machine":platform.node(), "python":sys.version,
        "non_registered":args.test_mode,
        "disclaimer":"Reimplementation, not a rerun. Test outputs are not measurements and may not be cited as evidence for any registered quantity.",
        "unvaried_parameters":"Production defaults phi=25, alpha=1, successor capability=1; successor generation=2.",
        "definitions":{"peak_population":"Maximum recorded population",
                       "survived":"final >= max(min_viable_population, 0.65 * peak)",
                       "collapsed":"0 < final < survival threshold",
                       "knowledge_transfer_verified":"Amendment 1 Boolean; descriptive only"},
        "mode":"normal", "mode_changes":[], "cpu_budget":cpu_budget(),
    }
    manifest["sources"].update(sources)
    if not control_path.exists():
        atomic_json(control_path, {"mode":manifest["mode"]})
    records = merged_records(prefix)
    preserved, restarted, never = 0, 0, 0
    pending = []
    for task in tasks:
        ident = job_id(task)
        fp = paths(prefix,task)
        record = records.get(ident)
        if record is not None:
            assert record["task"] == task and record["source"] == sources[task["substrate"]]
            assert record["code_sha256_lf"] == code
            assert digest(csv_bytes([record["row"]],ROW_FIELDS)) == record["row_sha256_lf"]
        elif fp["completion"].exists():
            record = read_completion(fp["completion"], task, code, sources)
        if record is not None:
            records[ident] = record
            preserved += 1
        else:
            was_started = ident in manifest["started"] or any(p.exists() for p in fp.values())
            if was_started:
                restarted += 1
                suffix = ".partial."+str(time.time_ns())
                for path in fp.values():
                    if path.exists():
                        os.replace(path, path.with_name(path.name+suffix))
            else:
                never += 1
            pending.append(task)
    start = time.monotonic()
    invocation = {"started_utc":utc(), "requested_workers":args.workers, "peak_workers":0,
                  "preserved":preserved, "restarted":restarted, "never_launched":never,
                  "selected_count":len(tasks), "category":args.category, "substrate":args.substrate,
                  "mode_at_start":manifest["mode"], "restarted_keys":[job_id(t) for t in pending if job_id(t) in manifest["started"]]}
    manifest["invocations"].append(invocation)
    active = {}
    status = "running"
    limit = worker_limit(args.workers,manifest["cpu_budget"],manifest["mode"],len(tasks))
    print("Workers in use: "+str(limit)+" (requested "+str(args.workers)+")",flush=True)
    def save_progress():
        cells = {}
        for task in tasks:
            key = task["category"]+"/"+task["substrate"]
            cell = cells.setdefault(key, {"completed":0,"running":0,"pending":0})
            ident = job_id(task)
            cell["completed" if ident in records else "running" if ident in active else "pending"] += 1
        elapsed_values = [r["row"]["elapsed_seconds"] for i,r in records.items() if i in task_by_id]
        value = {"status":status, "updated_utc":utc(), "parent_pid":os.getpid(),
                 "prefix":prefix, "cells":cells, "completed":sum(c["completed"] for c in cells.values()),
                 "running":len(active), "pending":sum(c["pending"] for c in cells.values()),
                 "elapsed_seconds":time.monotonic()-start,
                 "mean_seconds_per_run":sum(elapsed_values)/len(elapsed_values) if elapsed_values else None,
                 "requested_workers":args.workers,"worker_limit":limit,"mode":manifest["mode"],
                 "active":[{"key":i,"pid":v[0].pid} for i,v in active.items()],
                 "resume_counts":{k:invocation[k] for k in ("preserved","restarted","never_launched")}}
        atomic_json(progress_path,value)
        atomic_json(DIAG/(prefix+"progress.json"),value)
    atomic_json(manifest_path,manifest)
    save_progress()
    try:
        for category in ("A","B","C","phi"):
            if category not in args.category:
                continue
            queue = collections.deque(t for t in pending if t["category"] == category)
            last_save = 0.
            while queue or active:
                control = read_json(control_path)
                mode = control.get("mode")
                assert mode in ("normal","work"), "Invalid runtime mode"
                if mode != manifest["mode"]:
                    manifest["mode_changes"].append({"utc":utc(),"from":manifest["mode"],"to":mode})
                    manifest["mode"] = mode
                limit = worker_limit(args.workers,manifest["cpu_budget"],mode,len(queue)+len(active))
                while queue and len(active) < limit:
                    task = queue.popleft()
                    ident = job_id(task)
                    manifest["started"][ident] = {"utc":utc(),"attempt":manifest["started"].get(ident,{}).get("attempt",0)+1}
                    atomic_json(manifest_path,manifest)
                    job = {"task":task,"source":sources[task["substrate"]],"prefix":prefix,"code_sha256_lf":code}
                    proc, console = launch(job)
                    active[ident] = (proc,console,task)
                    invocation["peak_workers"] = max(invocation["peak_workers"],len(active))
                for ident,(proc,console,task) in list(active.items()):
                    result = proc.poll()
                    if result is None:
                        continue
                    console.close()
                    del active[ident]
                    if result != 0:
                        invocation["worker_failure"] = {"key":ident,"exit_code":result,"console":str(paths(prefix,task)["console"])}
                        raise RuntimeError("Worker terminated or raised an exception: "+ident)
                    record = read_completion(paths(prefix,task)["completion"],task,code,sources)
                    assert record is not None, "Worker did not publish a valid completion"
                    records[ident] = record
                now = time.monotonic()
                if now-last_save >= 2:
                    save_progress()
                    atomic_json(manifest_path,manifest)
                    last_save = now
                time.sleep(0.1)
            selected = [t for t in tasks if t["category"] == category]
            assert all(job_id(t) in records for t in selected)
            merge_category(prefix,category,records,manifest,manifest_path)
        status = "complete"
        manifest["completion_pin_readings"] = verify_pins()
        for sub,src in sources.items():
            assert source_identity(Path(src["path"])) == src, "Source changed at completion"
    except BaseException as exc:
        status = "interrupted" if isinstance(exc,KeyboardInterrupt) else "stopped"
        invocation["error"] = str(exc)
        for proc,console,task in active.values():
            if proc.poll() is None:
                proc.terminate()
        for proc,console,task in active.values():
            proc.wait()
            console.close()
        active.clear()
        invocation["traceback"] = traceback.format_exc()
    invocation["ended_utc"] = utc()
    invocation["status"] = status
    invocation["elapsed_seconds"] = time.monotonic()-start
    manifest["status"] = status
    manifest["retry_events"].extend(RETRIES)
    atomic_json(manifest_path,manifest)
    save_progress()
    print(status.upper()+": "+str(sum(job_id(t) in records for t in tasks))+"/"+str(len(tasks))+" selected runs complete",flush=True)
    return 0 if status == "complete" else 2

if __name__ == "__main__":
    sys.exit(main())
