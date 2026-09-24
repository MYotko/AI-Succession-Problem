"""Non-registered build validation. Never dispatches registered seed indices."""
import sys
sys.dont_write_bytecode=True
import argparse
import copy
import ctypes
import datetime as dt
import json
import os
from pathlib import Path
import subprocess
import time
import traceback
import phase_b_rerun_executor as executor
from phase_b_rerun_common import *
from phase_b_rerun_xcheck_compare import compare, equal_value

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent.parent

def wait_until(predicate,deadline=7200):
    start=time.monotonic()
    while time.monotonic()-start<deadline:
        value=predicate()
        if value:
            return value
        time.sleep(.2)
    raise TimeoutError("Validation condition timed out")

def read_if(path):
    try:
        return read_json(path) if Path(path).exists() else None
    except (ValueError,OSError):
        return None

def launch(arguments,name):
    out=open(HERE/("phase_b_rerun_smoke_"+name+"_console.txt"),"ab")
    p=subprocess.Popen([sys.executable,"-B",str(HERE/"phase_b_rerun_executor.py"),*arguments],
                       cwd=ROOT,stdout=out,stderr=out,creationflags=getattr(subprocess,"CREATE_NO_WINDOW",0))
    out.close()
    return p

def kill_owned(process):
    if process.poll() is not None:
        raise RuntimeError("Controller already exited before interruption test")
    process.kill()
    process.wait()

def progress_predicate(process,predicate):
    def read():
        if process.poll() is not None:
            raise RuntimeError("Controller exited during live validation: "+str(process.returncode))
        value=read_if(HERE/"phase_b_rerun_smoke_progress.json")
        return value if value and predicate(value) else None
    return read

def all_records(prefix):
    manifest=read_json(HERE/(prefix+"manifest.json"))
    records=[]
    for part in sorted(manifest["parts"],key=int):
        records.extend(executor.verify_merged(HERE,manifest["parts"][part]))
    return records

def main():
    install_guard(HERE)
    args_common=["--test-mode","--machine-label","YOTKOTEST","--cpu-budget","16"]
    controller=launch(args_common+["--workers","4"],"controller_first")
    control=HERE/"phase_b_rerun_smoke_runtime_control_YOTKOTEST.json"
    first=wait_until(progress_predicate(controller,lambda p:len(p["active_children"])==4))
    initial_pids=[p["pid"] for p in first["active_children"]]
    save(control,{"workers":2})
    reduced=wait_until(progress_predicate(controller,lambda p:
        p["requested_cap"]==2 and len(p["active_children"])<=2
        and any(e.get("cap")==2 and e.get("effective_utc") for e in p["events"])))
    save(control,{"workers":4})
    raised=wait_until(progress_predicate(controller,lambda p:p["requested_cap"]==4 and p["cap_source"]=="override:workers"))
    save(control,{"mode":"work"})
    named=wait_until(progress_predicate(controller,lambda p:p["cap_source"]=="override:work"))
    save(control,{"workers":4,"until":"2000-01-01T00:00:00"})
    expired=wait_until(progress_predicate(controller,lambda p:p["cap_source"].startswith("schedule:")))
    old_cap=expired["requested_cap"]
    save(control,{"workers":16})
    refused=wait_until(progress_predicate(controller,lambda p:any(
        e["event"]=="scheduler_warning" and "16" in e.get("warning","") for e in p["events"])))
    assert refused["requested_cap"]==old_cap
    before={}
    for path in HERE.glob("phase_b_rerun_smoke_run_*_completion.json"):
        rec=read_json(path);before[rec["row"]["run_id"]]=digest(canonical(rec).encode())
    for path in HERE.glob("phase_b_rerun_smoke_part*_manifest.json"):
        for rec in executor.verify_merged(HERE,read_json(path)):
            before[rec["row"]["run_id"]]=digest(canonical(rec).encode())
    assert before and len(before)<16
    kill_owned(controller)
    time.sleep(2)
    # Valid completed records that raced with the intentional controller kill also persist.
    for path in HERE.glob("phase_b_rerun_smoke_run_*_completion.json"):
        rec=read_json(path);before[rec["row"]["run_id"]]=digest(canonical(rec).encode())
    save(HERE/"phase_b_rerun_smoke_interruption_before.json",{"completion_hashes":before,
         "killed_controller_pid":controller.pid,"initial_child_pids":initial_pids})
    save(control,{"workers":4})
    controller=launch(args_common+["--resume"],"controller_resume")
    result=controller.wait()
    if result:
        raise RuntimeError("Resumed controller failed: "+str(result))
    records=all_records("phase_b_rerun_smoke_")
    after={r["row"]["run_id"]:digest(canonical(r).encode()) for r in records}
    assert all(after[rid]==h for rid,h in before.items())
    manifest=read_json(HERE/"phase_b_rerun_smoke_manifest.json")
    assert not any(e["event"]=="terminated_worker" for e in manifest["events"])
    scheduler={"initial_cap":4,"reduced":reduced,"raised":raised,"named_mode":named,
               "expired":expired,"refused":refused,"no_worker_killed_for_cap_change":True}
    save(HERE/"phase_b_rerun_smoke_live_scheduler_results.json",scheduler)
    # Repeat one O task and its R partner, separately, with one worker.
    startup=read_json(HERE/"phase_b_rerun_smoke_startup.json")
    identity=startup["identity"]
    arms={a:Path(p) for a,p in executor.DEFAULT_ARMS.items()}
    baseline={}
    for arm in ("O","R"):
        baseline[arm]=next(r for r in records if r["entry"]["arm"]==arm and r["entry"]["task"]["mode"]=="C")
    repeats=[]
    for arm,original in baseline.items():
        a=executor.parser().parse_args(["--test-mode","--machine-label","YOTKOTEST","--workers","1"])
        prefix="phase_b_rerun_smoke_repeat_"+arm+"_"
        batch=executor.Batch(a,prefix,[original["entry"]],arms,identity,startup)
        batch.run()
        rec=all_records(prefix)[0]
        differing=[f for f in FIELDS if not equal_value(rec["row"][f],original["row"][f])]
        repeats.append({"arm":arm,"run_id":rec["row"]["run_id"],"differing_fields":differing})
    # Real crosscheck invocation, 16 additional non-registered model runs.
    process=launch(["--crosscheck","--machine-label","YOTKOTEST","--workers","8"],"crosscheck")
    if process.wait():
        raise RuntimeError("Crosscheck execution failed")
    xcheck=read_json(HERE/"phase_b_rerun_xcheck_YOTKOTEST_rows.json")
    self_result=compare(xcheck,xcheck)
    save(HERE/"phase_b_rerun_smoke_xcheck_self_result.json",self_result)
    assert self_result["result"]=="IDENTICAL"
    altered=copy.deepcopy(xcheck)
    altered["rows"][0]["final_population"]+=1
    save(HERE/"phase_b_rerun_smoke_xcheck_altered_rows.json",altered)
    sign=compare(xcheck,altered)
    save(HERE/"phase_b_rerun_smoke_xcheck_sign_result.json",sign)
    assert sign["result"]=="DIFFERENT" and [x["field"] for x in sign["differences"]]==["final_population"]
    cli_outputs=[]
    for label,right in (("self",HERE/"phase_b_rerun_xcheck_YOTKOTEST_rows.json"),
                        ("altered",HERE/"phase_b_rerun_smoke_xcheck_altered_rows.json")):
        completed=subprocess.run([sys.executable,"-B",str(HERE/"phase_b_rerun_xcheck_compare.py"),
            str(HERE/"phase_b_rerun_xcheck_YOTKOTEST_rows.json"),str(right),"--out",
            str(HERE/("phase_b_rerun_smoke_xcheck_cli_"+label+".json"))],
            cwd=ROOT,capture_output=True,text=True,check=True)
        cli_outputs.append({"case":label,"stdout":completed.stdout})
    save(HERE/"phase_b_rerun_smoke_xcheck_cli_results.json",cli_outputs)
    # Cross-machine resume is tested only against smoke outputs with a marked fixture.
    entries=[r["entry"] for r in records]
    other=executor.parser().parse_args(["--test-mode","--resume","--machine-label","YOTKOTEST-fixture"])
    refused_machine=False
    try:
        executor.Batch(other,"phase_b_rerun_smoke_",entries,arms,identity,startup)
    except RuntimeError as exc:
        if "Resume refused: machine" not in str(exc):
            raise
        refused_machine=True
    assert refused_machine
    permission={"result":"IDENTICAL","machine_labels":["YOTKOTEST","YOTKOTEST-fixture"],
                "executor_hashes":identity["executor_hashes"],"bytecode_sha256":BYTECODE_HASH,
                "test_fixture":True,"purpose":"Non-registered machine-resume unit fixture"}
    save(HERE/"phase_b_rerun_smoke_machine_xcheck_result.json",permission)
    permitted=executor.Batch(other,"phase_b_rerun_smoke_",entries,arms,identity,startup)
    assert permitted.resume_counts["preserved"]==16 and not permitted.pending
    # Restore original operator-facing machine metadata without dispatching any run.
    original_args=executor.parser().parse_args(args_common+["--resume"])
    executor.Batch(original_args,"phase_b_rerun_smoke_",entries,arms,identity,startup)
    pairs=[]
    for o in records:
        if o["entry"]["arm"]!="O":
            continue
        for r in records:
            if r["entry"]["arm"]=="R" and o["entry"]["task"]==r["entry"]["task"]:
                pairs.append({"task":o["entry"]["task"],"differing_fields":[f for f in FIELDS if not equal_value(o["row"][f],r["row"][f])]})
    values={field:sorted({r["row"][field] for r in records}) for field in ("survived","yield_fired","final_population")}
    means={arm:sum(r["row"]["wall_seconds"] for r in records if r["entry"]["arm"]==arm)/sum(r["entry"]["arm"]==arm for r in records) for arm in ("O","R")}
    output={"status":"complete","non_registered":True,"registered_runs_executed":0,
        "unique_smoke_runs":len(records),"determinism_repeats":repeats,
        "crosscheck_runs":len(xcheck["rows"]),"crosscheck_self":self_result["result"],
        "crosscheck_sign":sign["result"],"crosscheck_sign_fields":[d["field"] for d in sign["differences"]],
        "seed_crosscheck":startup["seed_tasks_checked"],"counts":startup["counts"],
        "part4_subset":startup["part4_subset"],"liveness_distinct_values":values,
        "matched_arm_differences":pairs,"resume_counts":manifest["resume_counts"],
        "completed_records_preserved":len(before),"machine_refusal":refused_machine,
        "machine_fixture_preserved":permitted.resume_counts["preserved"],
        "mean_wall_seconds_per_arm":means,"errors":[r["row"]["error"] for r in records if r["row"]["error"]],
        "all_rows_ordered":all(list(r["row"])==FIELDS+EXTRA for r in records),
        "modules_by_arm":{a:next(r["metadata"]["modules"] for r in records if r["entry"]["arm"]==a) for a in ("O","R")},
        "all_threads_one":all(all(x["threads"]==1 for x in r["metadata"]["effective_threads_after"]) for r in records),
        "identity":identity,"generated_utc":utc()}
    save(HERE/"phase_b_rerun_b1_validation.json",output)
    print("Validation complete: 16 smoke runs, 2 determinism repeats, 16 crosscheck runs; registered runs 0.")

if __name__=="__main__":
    try:
        main()
    except BaseException as exc:
        save(HERE/"phase_b_rerun_b1_validation_failure.json",{"error":repr(exc),"traceback":traceback.format_exc(),"utc":utc()})
        raise
