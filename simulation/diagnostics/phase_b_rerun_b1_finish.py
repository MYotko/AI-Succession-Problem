"""Build report only. Reads non-registered validation artifacts; runs no models."""
import sys
sys.dont_write_bytecode=True
import csv
import datetime as dt
import json
from pathlib import Path
import socket
import subprocess
import phase_b_rerun_executor as e
from phase_b_rerun_common import *

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent.parent

def main():
    install_guard(HERE)
    v=read_json(HERE/"phase_b_rerun_b1_validation.json")
    if v["status"]!="complete":
        raise RuntimeError("Validation is not complete")
    e.check_sources({a:Path(p) for a,p in e.DEFAULT_ARMS.items()})
    if e.own_hashes()!=v["identity"]["executor_hashes"]:
        raise RuntimeError("Final source identity differs from validated source")
    preflight=read_json(HERE/"phase_b_rerun_b1_preflight.json")
    source_readings=[]
    for prior in preflight["source_readings"]:
        blob=subprocess.check_output(["git","cat-file","blob","HEAD:"+prior["path"]],cwd=ROOT)
        row={"path":prior["path"],"initial":prior,"completion_head_sha256_lf":digest(blob.replace(b"\r\n",b"\n")),
             "completion_worktree_sha256_lf":file_hash(ROOT/prior["path"])}
        if row["completion_head_sha256_lf"]!=prior["pin"] or row["completion_worktree_sha256_lf"]!=prior["pin"]:
            raise RuntimeError("Source pin changed at completion")
        source_readings.append(row)
    records=[]
    for prefix in ("phase_b_rerun_smoke_","phase_b_rerun_smoke_repeat_O_",
                   "phase_b_rerun_smoke_repeat_R_","phase_b_rerun_xcheck_YOTKOTEST_"):
        manifest=read_json(HERE/(prefix+"manifest.json"))
        for part in manifest["parts"].values():
            records.extend(e.verify_merged(HERE,part))
    if len(records)!=34:
        raise RuntimeError("Unexpected final validation completion count")
    archive=read_json(HERE/"phase_b_rerun_b1_initial_artifact_map.json")
    for entry in archive:
        if digest((HERE/entry["retained_name"]).read_bytes())!=entry["sha256_raw"]:
            raise RuntimeError("Retained initial artifact changed")
    counts={"final_completed_non_registered":34,"initial_completed_non_registered":34,
            "total_completed_non_registered":68,"registered_runs_executed":0}
    means=v["mean_wall_seconds_per_arm"]
    report_time=dt.datetime.now()
    durations=[means["O"]]*20400+[means["R"]]*5400
    override={"workers":15,"until":"2026-09-25T07:00:00"}
    projections={}
    for name,schedule,control in (
        ("override_then_schedule",DEFAULT_SCHEDULE,override),
        ("constant_10",{"timezone":"local","default_workers":10,"modes":{},"rules":[]},None),
        ("constant_15",{"timezone":"local","default_workers":15,"modes":{},"rules":[]},None)):
        finish=projected_finish(report_time,durations,schedule,control,15)
        projections[name]={"start_local":report_time.isoformat(),"finish_local":finish.isoformat(),
                           "elapsed_hours":(finish-report_time).total_seconds()/3600}
    model_hashes={a:next(m["sha256_lf"] for m in modules.values()
                       if Path(m["path"]).name=="model.py") for a,modules in v["modules_by_arm"].items()}
    unit=read_json(HERE/"phase_b_rerun_smoke_final_unit_results.json")
    live=read_json(HERE/"phase_b_rerun_smoke_live_scheduler_results.json")
    checks=[
      [1,"Both arms passed identity checks; every completed child recorded the pinned bytecode hash."],
      [2,str(v["seed_crosscheck"])+" registered tasks independently seed-checked; none executed."],
      [3,"Counts 1500, 10800, 8100, 2700, 2700; Part 4 task-identical subset: "+str(v["part4_subset"])+"."],
      [4,"All simulation modules loaded from their own worktrees; model.py hashes differ: "+str(model_hashes["O"]!=model_hashes["R"])+"."],
      [5,"All 30 original fields in order, followed by the ten appended fields: "+str(v["all_rows_ordered"])+"."],
      [6,"Distinct values: "+canonical(v["liveness_distinct_values"])+"."],
      [7,"Two separate repeats: "+canonical(v["determinism_repeats"])+"."],
      [8,str(len(v["matched_arm_differences"]))+" matched O/R tasks compared; differing fields are listed below."],
      [9,"Preserved "+str(v["resume_counts"]["preserved"])+", restarted "+str(v["resume_counts"]["restarted"])+
         ", never launched "+str(v["resume_counts"]["never_launched"])+" at resume; saved completion hashes unchanged."],
      [10,"Live 4 to 2 drain, return to 4, work mode, expired override, and refusal of 16 verified; no child killed for a cap change."],
      [11,"Seven injected-clock caps: "+", ".join(str(x["actual"]) for x in unit["schedule_clock"])+"."],
      [12,"One numerical thread verified from loaded libraries in all "+str(len(records))+" completed final-build children."],
      [13,"All "+str(len(records))+" final-build rows and their step records recovered from merged files with matching hashes."],
      [14,"Original error rows among all 34 final-build completions: "+str(sum(bool(r["row"]["error"]) for r in records))+"; "+canonical([r["row"]["error"] for r in records if r["row"]["error"]])+"."],
      [15,"Mean wall seconds, 500-step horizon: O "+repr(means["O"])+"; R "+repr(means["R"])+"."],
      [16,"Crosscheck completed 16 runs; CLI self-comparison IDENTICAL; altered copy DIFFERENT on final_population."],
      [17,"Different-label resume refused; marked smoke-only IDENTICAL fixture accepted 16 preserved runs. Additional version-binding fixtures passed."]
    ]
    build=read_json(HERE/"phase_b_rerun_b1_build_log.json")
    lines=["# Phase B rerun executor build and validation","",
       "Build complete and validated on YOTKOTEST. No registered run was launched and nothing was committed.",
       "The first validation cohort was retained byte for byte while operational repairs were applied. "
       "The final cohort used the final executor file hashes. Each cohort completed 16 smoke runs, "
       "two determinism repeats, and 16 crosscheck runs. All are non-registered and may not be cited "
       "as evidence for the note's registered quantities.","",
       "| Check | Evidence |","| --- | --- |"]
    for number,evidence in checks:
        lines.append("| "+str(number)+" | "+evidence.replace("|","&#124;")+" |")
    lines+=["","## Timing projection","",
        "Projection start: "+report_time.isoformat()+" local ("+dt.datetime.now().astimezone().tzname()+").",
        "These estimates use the final 16-run cohort's mean child wall time per arm, including initialization, "
        "for 20,400 arm O runs and 5,400 arm R runs. They assume the same per-arm means at other worker counts. "
        "The scheduler simulation keeps running jobs when a cap falls.","",
        "| Worker policy | Projected local finish | Hours |","| --- | --- | --- |"]
    for name,value in projections.items():
        lines.append("| "+name+" | "+value["finish_local"]+" | "+repr(value["elapsed_hours"])+" |")
    lines+=["","## Matched O/R fields","",
      "| Original task | Differing original fields |","| --- | --- |"]
    for pair in v["matched_arm_differences"]:
        lines.append("| "+canonical(pair["task"]).replace("|","&#124;")+" | "+", ".join(pair["differing_fields"])+" |")
    lines+=["","## Module paths from one completed child per arm",""]
    for arm,modules in v["modules_by_arm"].items():
        lines+=["Arm "+arm+":",""]
        for name,value in modules.items():
            lines.append("- "+name+": "+value["path"]+"; LF SHA256 "+value["sha256_lf"])
        lines.append("")
    lines+=["## Source pins","",
       "| Source | Initial HEAD / worktree LF SHA256 | Completion HEAD / worktree LF SHA256 |",
       "| --- | --- | --- |"]
    for row in source_readings:
        lines.append("| "+row["path"]+" | "+row["initial"]["head_sha256_lf"]+" / "+row["initial"]["worktree_sha256_lf"]+
                     " | "+row["completion_head_sha256_lf"]+" / "+row["completion_worktree_sha256_lf"]+" |")
    lines+=["","The bytecode pin and both worktree HEADs were also rechecked at completion. "
            "The known global Git ignore permission warning is retained in the preflight evidence.",
            "The Linux machine was not contacted. Its real cross-machine comparison remains the operator's step before registered execution.","",
            "## Tool-layer workarounds",""]
    lines+=["- "+x for x in build["tool_layer_workarounds"]]
    lines+=["","## Executor self-fixes",""]
    lines+=["- "+x for x in build["executor_self_fixes"]]
    lines+=["","## Operator commands","",
            "See phase_b_rerun_b1_operator_guide.md for exact Windows and Linux commands, runtime controls, "
            "whole-part transfer and import, and healthy progress readings.",""]
    save(HERE/"phase_b_rerun_b1_summary.json",{"status":"complete","checks":checks,"timings":means,
         "projections":projections,"counts":counts,"report_local":report_time.isoformat(),
         "local_timezone":dt.datetime.now().astimezone().tzname(),"model_hashes":model_hashes,
         "registered_runs_executed":0,"source_readings":source_readings,
         "runtime_requested_and_effective":[ev for ev in read_json(HERE/"phase_b_rerun_smoke_manifest.json")["events"] if ev["event"]=="worker_cap"],
         "interpreter_readiness":build["interpreter_readiness"]})
    atomic(HERE/"phase_b_rerun_b1_report.md","\n".join(lines))
    inventory={}
    for path in sorted(HERE.glob("phase_b_rerun_*")):
        if not path.is_file() or path.name in ("phase_b_rerun_design_note.md","phase_b_rerun_b1_manifest.json"):
            continue
        entry={"sha256_lf":file_hash(path),"bytes":path.stat().st_size}
        if path.suffix==".csv":
            with path.open(encoding="utf-8",newline="") as f:
                entry["csv_rows"]=max(0,sum(1 for _ in csv.reader(f))-1)
        inventory[path.name]=entry
    manifest={"status":"complete","non_registered":True,"machine_label":"YOTKOTEST","hostname":socket.gethostname(),
        "cpu_budget":16,"maximum_workers":15,"identity":v["identity"],"source_readings":source_readings,
        "bytecode_readings":preflight["bytecode_readings"],"arms":preflight["arms"],
        "controller_python":sys.version,"counts":counts,"source_basis":"LF-normalized SHA256, except explicitly raw bytecode pins",
        "outputs":inventory,"manifest_self_hash":"Excluded to avoid recursive self-hashing",
        "initial_artifact_map":"phase_b_rerun_b1_initial_artifact_map.json",
        "resumed_counts":v["resume_counts"],"projections":projections,"build_log":build,
        "t0_stderr_warnings":[x["stderr"] for x in preflight["commands"] if x["stderr"]],
        "per_run_hashes":"See each final and retained initial part manifest; every final merge was reverified.",
        "main_head_provenance_only":e.git("rev-parse","HEAD"),"commits_created":0}
    save(HERE/"phase_b_rerun_b1_manifest.json",manifest)
    print(json.dumps({"status":"complete","timings":means,"projections":projections,"counts":counts}))

if __name__=="__main__":
    main()
