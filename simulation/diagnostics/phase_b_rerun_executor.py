"""Phase B recovered-code executor. Registered runs are operator-launched only."""
import sys
sys.dont_write_bytecode=True
import argparse
import concurrent.futures
from collections import Counter
import datetime as dt
import json
import os
os.environ["GIT_OPTIONAL_LOCKS"]="0"
from pathlib import Path
import re
import shutil
import socket
import subprocess
import time
import traceback
from phase_b_rerun_common import *

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent.parent
PY313="C:/Users/matty/AppData/Local/Python/pythoncore-3.13-64/python.exe"
DEFAULT_ARMS={"O":"C:/Users/matty/Dev/phase-b-rerun-O","R":"C:/Users/matty/Dev/phase-b-rerun-R"}
OWN_FILES=("phase_b_rerun_executor.py","phase_b_rerun_common.py","phase_b_rerun_child.py",
           "phase_b_rerun_xcheck_compare.py")
BOOTSTRAP="import sys;sys.dont_write_bytecode=True;exec(compile(open(sys.argv[2],encoding='utf-8').read(),'<runner-support>','exec'));exec(compile(open(sys.argv[3],encoding='utf-8').read(),'<runner-child>','exec'))"

def git(*args):
    p=subprocess.run(["git",*args],cwd=ROOT,capture_output=True,text=True)
    if p.returncode:
        raise RuntimeError("Git check failed: "+repr(args)+" "+p.stderr)
    return p.stdout.strip()

def own_hashes():
    return {name:file_hash(HERE/name) for name in OWN_FILES}

def check_sources(arms):
    git("merge-base","--is-ancestor",NOTE_COMMIT,"origin/main")
    note="simulation/diagnostics/phase_b_rerun_design_note.md"
    blob=subprocess.check_output(["git","cat-file","blob","HEAD:"+note],cwd=ROOT)
    if digest(blob.replace(b"\r\n",b"\n"))!=NOTE_HASH or file_hash(ROOT/note)!=NOTE_HASH:
        raise RuntimeError("Note pin changed")
    result={}
    for arm,path in arms.items():
        head=git("-c","safe.directory="+str(path),"-C",str(path),"rev-parse","HEAD")
        if head!=ARM_HEADS[arm]:
            raise RuntimeError("Worktree HEAD changed: "+arm)
        code=Path(path)/"simulation/diagnostics/monte_carlo_phase_b.pyc"
        if digest(code.read_bytes())!=BYTECODE_HASH:
            raise RuntimeError("Bytecode pin changed: "+arm)
        if git("-c","safe.directory="+str(path),"-C",str(path),"status","--porcelain"):
            raise RuntimeError("Worktree became modified: "+arm)
        result[arm]=head
    return result

def child_environment():
    env=os.environ.copy()
    env.update({name:"1" for name in THREAD_ENV})
    env["PYTHONDONTWRITEBYTECODE"]="1"
    env.pop("PYTHONPATH",None)
    return env

def start_child(python,request_path,worktree,priority,console_path):
    flags=0
    if os.name=="nt":
        flags=getattr(subprocess,"CREATE_NO_WINDOW",0)
        flags |= (subprocess.BELOW_NORMAL_PRIORITY_CLASS if priority=="below-normal" else subprocess.NORMAL_PRIORITY_CLASS)
    stderr=open(console_path,"ab")
    process=subprocess.Popen([str(python),"-B","-c",BOOTSTRAP,str(request_path),
         str(HERE/"phase_b_rerun_common.py"),str(HERE/"phase_b_rerun_child.py")],
        cwd=worktree,env=child_environment(),stdout=stderr,stderr=stderr,creationflags=flags)
    stderr.close()
    return process

def prefix_for(args):
    if args.crosscheck:
        return "phase_b_rerun_xcheck_"+args.machine_label+"_"
    return "phase_b_rerun_smoke_" if args.test_mode else "phase_b_rerun_"

def validate_label(label):
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*",label):
        raise ValueError("Machine label must contain only letters, digits, dot, hyphen or underscore")
    return label

def enumerate_startup(args,prefix):
    arms={"O":Path(args.arm_o_worktree).resolve(),"R":Path(args.arm_r_worktree).resolve()}
    heads=check_sources(arms)
    metadata={}
    for arm in ("O","R"):
        stem=HERE/(prefix+"startup_"+arm)
        request={"operation":"enumerate","directory":str(HERE),"main_root":str(ROOT),
                 "worktree":str(arms[arm]),"arm":arm,"machine_label":args.machine_label,
                 "priority":args.priority,"parent_pid":os.getpid(),"output":str(stem)+".json"}
        save(str(stem)+"_request.json",request)
        proc=start_child(args.python313,str(stem)+"_request.json",arms[arm],args.priority,str(stem)+"_console.txt")
        while proc.poll() is None:
            time.sleep(.2)
        if proc.returncode:
            failure=Path(str(stem)+".json.failure.json")
            raise RuntimeError("Startup child failed: "+(failure.read_text() if failure.exists() else str(stem)+"_console.txt"))
        metadata[arm]=read_json(str(stem)+".json")
    registered=metadata["O"]["registered"]+metadata["R"]["registered"]
    counts=Counter((e["part"],e["task"]["mode"]) for e in registered)
    expected={(1,"B"):1500,(2,"A"):10800,(3,"C"):8100,(4,"A"):2700,(4,"C"):2700}
    if counts!=expected:
        raise RuntimeError("Registered task identity count mismatch: "+repr(counts))
    original={canonical(e["task"]) for e in registered if e["part"] in (2,3)}
    if not all(canonical(e["task"]) in original for e in registered if e["part"]==4):
        raise RuntimeError("Part 4 is not a task-identical subset")
    for entry in registered:
        if seed_check(entry["task"])!=entry["derived_seed"]:
            raise RuntimeError("Seed cross-check mismatch: "+entry["run_id"])
    smoke=metadata["O"]["smoke"]+metadata["R"]["smoke"]
    if len(smoke)!=16 or Counter(e["arm"] for e in smoke)!={"O":10,"R":6}:
        raise RuntimeError("Test task identity count mismatch")
    for e in smoke:
        if e["task"]["seed"] not in (150,151) or seed_check(e["task"])!=e["derived_seed"]:
            raise RuntimeError("Test seed cross-check mismatch")
    versions={arm:{"interpreter_version":m["interpreter_version"],"numpy_version":m["numpy_version"]}
              for arm,m in metadata.items()}
    identity={"executor_hashes":own_hashes(),"bytecode_sha256":BYTECODE_HASH,
              "worktree_heads":heads,"note_sha256_lf":NOTE_HASH,"versions":versions}
    proof={"counts":{str(k):v for k,v in counts.items()},"seed_tasks_checked":len(registered),
           "part4_subset":True,"task_list_hashes":{str(p):digest(canonical([e["task"] for e in registered if e["part"]==p]).encode()) for p in range(1,5)},
           "identity":identity,"main_head_provenance_only":git("rev-parse","HEAD"),
           "machine_label":args.machine_label,"cpu_budget":args.cpu_budget}
    save(HERE/(prefix+"startup.json"),proof)
    return arms,metadata,registered,smoke,identity,proof

def verify_identity(old,new,old_machine=None,new_machine=None,test_mode=False):
    changes=[key for key in set(old)|set(new) if old.get(key)!=new.get(key)]
    if changes == ["versions"] and old_machine and new_machine and old_machine != new_machine:
        paths=list(HERE.glob("phase_b_rerun_xcheck_result_*.json"))
        if test_mode:
            paths += list(HERE.glob("phase_b_rerun_smoke_*xcheck_result*.json"))
        for path in paths:
            result=read_json(path)
            env=result.get("environments",{})
            if (result.get("result")=="IDENTICAL"
                and set(result.get("machine_labels",[]))=={old_machine,new_machine}
                and result.get("executor_hashes")==new["executor_hashes"]
                and result.get("bytecode_sha256")==new["bytecode_sha256"]
                and (test_mode or not result.get("test_fixture"))
                and env.get(old_machine)==old["versions"]
                and env.get(new_machine)==new["versions"]):
                return
    if changes:
        raise RuntimeError("Resume identity changed: "+", ".join(sorted(changes)))

def crosscheck_permission(first,second,identity,test_mode=False):
    if first==second:
        return True
    paths=list(HERE.glob("phase_b_rerun_xcheck_result_*.json"))
    if test_mode:
        paths+=list(HERE.glob("phase_b_rerun_smoke_*xcheck_result*.json"))
    for path in paths:
        try:
            result=read_json(path)
            if result.get("result")=="IDENTICAL" and set(result.get("machine_labels",[]))=={first,second} and result.get("executor_hashes")==identity["executor_hashes"] and result.get("bytecode_sha256")==BYTECODE_HASH:
                if not test_mode and result.get("test_fixture"):
                    continue
                return True
        except (ValueError,OSError):
            continue
    return False

def validate_completion(record,entry,identity,new_machine=None,test_mode=False):
    if record["status"]!="complete" or record["entry"]!=entry:
        raise RuntimeError("Completion key or task mismatch: "+entry["run_id"])
    verify_identity(record["identity"],identity,record["machine_label"],new_machine,test_mode)
    row=record["row"]
    if list(row)!=FIELDS+EXTRA or row["run_id"]!=entry["run_id"]:
        raise RuntimeError("Completion row schema mismatch")
    if digest(csv_line(row).encode())!=record["row_sha256"] or record["row_count"]!=1:
        raise RuntimeError("Completion row hash mismatch")
    return record

def verify_merged(directory,manifest):
    directory=Path(directory)
    for name,info in manifest["files"].items():
        path=directory/name
        if file_hash(path)!=info["sha256_lf"]:
            raise RuntimeError("Merged file hash mismatch: "+str(path))
    runs_path=directory/manifest["runs_file"]
    with runs_path.open(encoding="utf-8",newline="") as f:
        reader=csv.DictReader(f)
        if reader.fieldnames!=FIELDS+EXTRA:
            raise RuntimeError("Merged CSV field order mismatch")
        rows=list(reader)
    records=[json.loads(line) for line in (directory/manifest["completions_file"]).read_text().splitlines()]
    by_id={r["run_id"]:r for r in rows}
    if len(by_id)!=len(rows) or len(rows)!=manifest["run_count"] or len(records)!=len(rows):
        raise RuntimeError("Merged row count mismatch")
    for record in records:
        rid=record["row"]["run_id"]
        if digest(csv_line(record["row"]).encode()) != record["row_sha256"]:
            raise RuntimeError("Completion payload hash mismatch: "+rid)
        reconstructed=csv_line(by_id[rid])
        if digest(reconstructed.encode())!=record["row_sha256"] or manifest["runs"][rid]["row_sha256"]!=record["row_sha256"]:
            raise RuntimeError("Merged per-run hash mismatch: "+rid)
        if by_id[rid]["arm"]!=record["entry"]["arm"] or int(by_id[rid]["part"])!=record["entry"]["part"] or int(by_id[rid]["seed"])!=record["entry"]["task"]["seed"]:
            raise RuntimeError("Merged filter identity mismatch")
    steps_path=directory/manifest["steps_file"]
    grouped={}
    with steps_path.open(encoding="utf-8",newline="") as f:
        for r in csv.DictReader(f):
            rid=r["run_id"]
            value=json.loads(r["recorded"])
            raw=canonical({"arm":r["arm"],"part":int(r["part"]),"run_id":rid,
                           "seed_index":int(r["seed_index"]),"step":int(r["step"]),"recorded":value})+"\n"
            if rid not in grouped:
                grouped[rid]=[hashlib.sha256(),0]
            grouped[rid][0].update(raw.encode()); grouped[rid][1]+=1
    for record in records:
        rid=record["row"]["run_id"]
        h,n=grouped.get(rid,[hashlib.sha256(),0])
        if h.hexdigest()!=record["steps_sha256"] or n!=record["step_count"]:
            raise RuntimeError("Merged step recovery mismatch: "+rid)
    return records

class Batch:
    def __init__(self,args,prefix,entries,arms,identity,proof):
        self.args=args; self.prefix=prefix; self.arms=arms; self.identity=identity; self.proof=proof
        self.entries=sorted(entries,key=lambda e:(e["part"],e["arm"],e["cell_key"]))
        self.by_id={e["run_id"]:e for e in self.entries}
        if len(self.by_id)!=len(entries):
            raise RuntimeError("Duplicate run identifiers")
        self.events=[]; self.active={}; self.completed={}; self.merged={}; self.start=time.monotonic()
        self.initial_elapsed=0.; self.resume_counts={"preserved":0,"restarted":0,"never_launched":0}
        self.machine=args.machine_label; self.maximum=max(1,args.cpu_budget-1)
        schedule_prefix=prefix if args.test_mode or args.crosscheck else "phase_b_rerun_"
        self.schedule_path=HERE/(schedule_prefix+"schedule_"+self.machine+".json")
        self.control_path=HERE/(schedule_prefix+"runtime_control_"+self.machine+".json")
        if not self.schedule_path.exists():
            save(self.schedule_path,default_schedule(socket.gethostname(),self.maximum))
        self.scheduler=Scheduler(self.schedule_path,self.control_path,self.maximum,self.events)
        if args.workers is not None:
            try:
                valid_count(args.workers,self.maximum)
                save(self.control_path,{"workers":args.workers})
            except ValueError as exc:
                self.events.append({"event":"scheduler_warning","utc":utc(),"warning":str(exc)})
        self.state_path=HERE/(prefix+"state.json")
        self.progress_path=HERE/(prefix+"progress.json")
        if self.state_path.exists():
            if not args.resume:
                raise RuntimeError("Existing execution state requires --resume")
            old=read_json(self.state_path)
            verify_identity(old["identity"],identity,old["machine_label"],self.machine,args.test_mode)
            if old["task_ids"]!=list(self.by_id):
                raise RuntimeError("Resume task selection changed")
            self.events[:]=old.get("events",[])+self.events
            self.scheduler.cap=min(old.get("last_cap",1),self.maximum)
            self.scheduler.source=old.get("last_cap_source","initial")
            self.initial_elapsed=old.get("elapsed_seconds",0.)
        elif args.resume:
            self.events.append({"event":"resume_without_state","utc":utc()})
        for part in sorted({e["part"] for e in self.entries}):
            mp=HERE/(prefix+f"part{part}_manifest.json")
            if mp.exists():
                manifest=read_json(mp)
                verify_identity(manifest["identity"],identity,manifest["machine_label"],self.machine,args.test_mode)
                records=verify_merged(HERE,manifest)
                self.merged[part]=manifest
                for rec in records:
                    self._accept(rec)
        for entry in self.entries:
            rid=entry["run_id"]
            path=self.path(rid,"completion.json")
            if rid in self.completed:
                continue
            if path.exists():
                try:
                    rec=read_json(path)
                except (ValueError,OSError) as exc:
                    self.events.append({"event":"invalid_partial_completion","run_id":rid,"error":str(exc),"utc":utc()})
                else:
                    self._accept(rec)
            if rid not in self.completed:
                if self.path(rid,"request.json").exists():
                    self.resume_counts["restarted"]+=1
                    self.events.append({"event":"restart","run_id":rid,"seed_index":entry["task"]["seed"],"utc":utc(),"reason":"interrupted or invalid completion"})
                else:
                    self.resume_counts["never_launched"]+=1
        self.resume_counts["preserved"]=len(self.completed)
        self.pending=[e for e in self.entries if e["run_id"] not in self.completed]
        self.scheduler.poll(0)
        self.save_state()
    def path(self,rid,suffix):
        return HERE/(self.prefix+"run_"+rid+"_"+suffix)
    def _accept(self,record):
        rid=record["row"]["run_id"]
        if rid not in self.by_id:
            raise RuntimeError("Unexpected completion "+rid)
        validate_completion(record,self.by_id[rid],self.identity,self.machine,self.args.test_mode)
        machine=record["machine_label"]
        if not crosscheck_permission(machine,self.machine,self.identity,self.args.test_mode):
            raise RuntimeError("Resume refused: machine "+machine+" differs from "+self.machine+" without matching IDENTICAL crosscheck")
        if rid in self.completed and self.completed[rid]!=record:
            raise RuntimeError("Conflicting duplicate completion")
        self.completed[rid]=record
    def elapsed(self):
        return self.initial_elapsed+time.monotonic()-self.start
    def save_state(self):
        save(self.state_path,{"identity":self.identity,"task_ids":list(self.by_id),"machine_label":self.machine,
            "events":self.events,"resume_counts":self.resume_counts,"elapsed_seconds":self.elapsed(),
            "cpu_budget":self.args.cpu_budget,"priority":self.args.priority,"retry_events":RETRIES,
            "last_cap":self.scheduler.cap,"last_cap_source":self.scheduler.source})
    def dispatch(self,entry):
        rid=entry["run_id"]
        for suffix in ("request.json","steps.jsonl","completion.json","completion.json.failure.json","console.txt"):
            existing=self.path(rid,suffix)
            if existing.exists():
                archive=existing.with_name(existing.name+".partial."+str(time.time_ns()))
                os.replace(existing,archive)
        request={"operation":"run","directory":str(HERE),"main_root":str(ROOT),
                 "worktree":str(self.arms[entry["arm"]]),"arm":entry["arm"],
                 "machine_label":self.machine,"priority":self.args.priority,"parent_pid":os.getpid(),
                 "entry":entry,"identity":self.identity,"non_registered":self.args.test_mode or self.args.crosscheck,
                 "output":str(self.path(rid,"completion.json")),"steps_output":str(self.path(rid,"steps.jsonl"))}
        save(self.path(rid,"request.json"),request)
        process=start_child(self.args.python313,self.path(rid,"request.json"),self.arms[entry["arm"]],
                            self.args.priority,self.path(rid,"console.txt"))
        self.active[rid]={"process":process,"entry":entry,"started":time.monotonic(),"started_utc":utc()}
        self.events.append({"event":"dispatch","run_id":rid,"pid":process.pid,"utc":utc(),
                            "active_after":len(self.active),"cap":self.scheduler.cap})
    def progress(self,status="running"):
        part_counts={}
        for part in sorted({e["part"] for e in self.entries}):
            ids={e["run_id"] for e in self.entries if e["part"]==part}
            done=ids & self.completed.keys(); active=ids & self.active.keys()
            part_counts[str(part)]={"completed":len(done),"running":len(active),
                "pending":len(ids)-len(done)-len(active),
                "errors":sum(bool(self.completed[r]["row"]["error"]) for r in done)}
        means={}
        for arm in ("O","R"):
            values=[r["row"]["wall_seconds"] for r in self.completed.values() if r["entry"]["arm"]==arm]
            means[arm]=sum(values)/len(values) if values else None
        eta=None
        if all(means[e["arm"]] is not None for e in self.pending) and all(means[a["entry"]["arm"]] is not None for a in self.active.values()) and self.scheduler.schedule:
            try:
                end=projected_finish(dt.datetime.now(),[means[e["arm"]] for e in self.pending],
                     ({"timezone":"local","default_workers":self.scheduler.cap,"modes":{},"rules":[]} if self.scheduler.bad else self.scheduler.schedule),
                     (None if self.scheduler.bad else self.scheduler.override),self.maximum,
                     [max(.01,means[a["entry"]["arm"]]-(time.monotonic()-a["started"])) for a in self.active.values()])
                eta=end.isoformat()
            except (ValueError,KeyError):
                pass
        save(self.progress_path,{"updated_utc":utc(),"status":status,"machine_label":self.machine,
            "controller_pid":os.getpid(),"cpu_budget":self.args.cpu_budget,"maximum_workers":self.maximum,
            "parts":part_counts,"current_cap":min(self.scheduler.cap,len(self.pending)+len(self.active)) if self.pending or self.active else 0,
            "requested_cap":self.scheduler.cap,"cap_source":self.scheduler.source,
            "active_children":[{"pid":a["process"].pid,"run_id":rid,"started_utc":a["started_utc"]} for rid,a in self.active.items()],
            "elapsed_seconds":self.elapsed(),"mean_wall_seconds_per_arm":means,"estimated_finish_local":eta,"eta_assumption":("previous cap retained while control is invalid" if self.scheduler.bad else "current schedule and override expiry"),
            "resume_counts":self.resume_counts,"schedule_path":str(self.schedule_path),
            "runtime_control_path":str(self.control_path),"events":self.events[-100:]})
        self.save_state()
    def merge(self,part):
        records=sorted([r for r in list(self.completed.values()) if r["entry"]["part"]==part],
                       key=lambda r:(r["entry"]["arm"],r["entry"]["cell_key"]))
        expected=sum(e["part"]==part for e in self.entries)
        if len(records)!=expected:
            return
        stem=self.prefix+f"part{part}_"
        runs=HERE/(stem+"runs.csv"); completions=HERE/(stem+"completions.jsonl"); steps=HERE/(stem+"steps.csv")
        atomic(runs,csv_header()+"".join(csv_line(r["row"]) for r in records))
        atomic(completions,"".join(json.dumps(r,separators=(",",":"),allow_nan=False)+"\n" for r in records))
        temp=steps.with_name(steps.name+".tmp."+str(os.getpid()))
        sf=["arm","part","run_id","seed_index","step","recorded"]
        nsteps=0
        with temp.open("w",encoding="utf-8",newline="") as output:
            writer=csv.DictWriter(output,fieldnames=sf,lineterminator="\n"); writer.writeheader()
            for record in records:
                raw_path=self.path(record["row"]["run_id"],"steps.jsonl")
                h=hashlib.sha256(); n=0
                with raw_path.open("rb") as inp:
                    for line in inp:
                        h.update(line); n+=1; value=json.loads(line)
                        value["recorded"]=canonical(value["recorded"])
                        writer.writerow(value)
                if h.hexdigest()!=record["steps_sha256"] or n!=record["step_count"]:
                    raise RuntimeError("Per-run step hash mismatch before merge")
                nsteps+=n
            output.flush(); os.fsync(output.fileno())
        retry(lambda:os.replace(temp,steps),"publish merged steps")
        partials=[]
        for record in records:
            rid=record["row"]["run_id"]
            partials.extend(HERE.glob(self.prefix+"run_"+rid+"_*.partial.*"))
        journal=HERE/(stem+"interruption_journal.jsonl")
        journal_rows=[]
        for path in partials:
            raw=path.read_bytes()
            journal_rows.append({"filename":path.name,"sha256_raw":digest(raw),
                                 "contents":raw.decode("utf-8","backslashreplace")})
        atomic(journal,"".join(canonical(r)+"\n" for r in journal_rows))
        manifest={"part":part,"machine_label":self.machine,"identity":self.identity,"run_count":len(records),
             "runs_file":runs.name,"completions_file":completions.name,"steps_file":steps.name,
             "files":{p.name:{"sha256_lf":file_hash(p),"row_count":n} for p,n in [(runs,len(records)),(completions,len(records)),(steps,nsteps),(journal,len(journal_rows))]},
             "runs":{r["row"]["run_id"]:{"arm":r["entry"]["arm"],"seed_index":r["entry"]["task"]["seed"],
                 "row_count":1,"row_sha256":r["row_sha256"],"step_count":r["step_count"],
                 "steps_sha256":r["steps_sha256"]} for r in records},"deleted_by_kind":{}}
        verify_merged(HERE,manifest)
        mp=HERE/(stem+"manifest.json")
        save(mp,manifest)
        deleted=Counter()
        for record in records:
            rid=record["row"]["run_id"]
            for suffix in ("completion.json","steps.jsonl","request.json","console.txt"):
                p=self.path(rid,suffix)
                if p.exists():
                    p.unlink(); deleted[suffix]+=1
        for path in partials:
            path.unlink()
            deleted["retained_in_interruption_journal"]+=1
        manifest["deleted_by_kind"]=dict(deleted)
        save(mp,manifest); self.merged[part]=manifest
        self.events.append({"event":"part_merged","part":part,"utc":utc(),"rows":len(records)})
    def run(self):
        print(f"Effective worker cap: {self.scheduler.cap} ({self.scheduler.source}); machine {self.machine}",flush=True)
        self.progress()
        last_progress=time.monotonic()
        merger=concurrent.futures.ThreadPoolExecutor(max_workers=1)
        merging={}
        try:
            while self.pending or self.active or merging or any(e["part"] not in self.merged for e in self.entries):
                self.scheduler.poll(len(self.active))
                for rid,a in list(self.active.items()):
                    status=a["process"].poll()
                    if status is None:
                        continue
                    del self.active[rid]
                    if status:
                        failure=self.path(rid,"completion.json.failure.json")
                        if failure.exists():
                            raise RuntimeError("Child exception: "+failure.read_text())
                        self.events.append({"event":"terminated_worker","run_id":rid,"exit_code":status,"utc":utc()})
                        raise InterruptedError("Worker terminated; resume required: "+rid)
                    self._accept(read_json(self.path(rid,"completion.json")))
                    self.events.append({"event":"complete","run_id":rid,"utc":utc(),"pid":a["process"].pid})
                self.scheduler.poll(len(self.active))
                for part,future in list(merging.items()):
                    if future.done():
                        future.result()
                        del merging[part]
                for part in sorted({e["part"] for e in self.entries}):
                    if part not in self.merged and part not in merging and all(e["run_id"] in self.completed for e in self.entries if e["part"]==part):
                        merging[part]=merger.submit(self.merge,part)
                while self.pending and len(self.active)<self.scheduler.cap:
                    self.dispatch(self.pending.pop(0))
                if time.monotonic()-last_progress>=5:
                    self.progress(); last_progress=time.monotonic()
                time.sleep(.2)
            merger.shutdown(wait=True)
            check_sources(self.arms)
            if own_hashes()!=self.identity["executor_hashes"]:
                raise RuntimeError("Executor source changed during execution")
            self.progress("complete")
            manifest={"status":"complete","machine_label":self.machine,"identity":self.identity,
                "proof":self.proof,"parts":self.merged,"resume_counts":self.resume_counts,
                "events":self.events,"cpu_budget":self.args.cpu_budget,"priority":self.args.priority,
                "non_registered":self.args.test_mode or self.args.crosscheck,"retry_events":RETRIES,
                "files":{name:info for m in self.merged.values() for name,info in m["files"].items()}}
            save(HERE/(self.prefix+"manifest.json"),manifest)
            if self.args.crosscheck:
                records=[self.completed[e["run_id"]] for e in self.entries]
                save(HERE/(self.prefix+"rows.json"),{"machine_label":self.machine,"identity":self.identity,
                     "non_registered":True,"rows":[r["row"] for r in records],"tasks":[r["entry"] for r in records]})
            print(f"Complete: {len(self.completed)} runs; errors {sum(bool(r['row']['error']) for r in self.completed.values())}",flush=True)
            return manifest
        except BaseException:
            merger.shutdown(wait=True,cancel_futures=True)
            for a in self.active.values():
                if a["process"].poll() is None:
                    a["process"].terminate()
            for a in self.active.values():
                a["process"].wait()
            self.active.clear()
            self.progress("interrupted")
            raise

def import_parts(files,args):
    supplied={Path(f).resolve().name:Path(f).resolve() for f in files}
    manifests=[p for p in supplied.values() if p.name.endswith("_manifest.json")]
    if not manifests:
        raise RuntimeError("--import-part requires each part manifest and its merged files")
    for path in manifests:
        manifest=read_json(path)
        if "part" not in manifest:
            raise RuntimeError("Import requires a per-part manifest")
        if manifest["identity"]["worktree_heads"]!=ARM_HEADS or manifest["identity"]["note_sha256_lf"]!=NOTE_HASH:
            raise RuntimeError("Imported substrate or note identity mismatch")
        if manifest["identity"]["executor_hashes"]!=own_hashes() or manifest["identity"]["bytecode_sha256"]!=BYTECODE_HASH:
            raise RuntimeError("Imported executor or bytecode identity mismatch")
        for name,info in manifest["files"].items():
            if name not in supplied or file_hash(supplied[name])!=info["sha256_lf"]:
                raise RuntimeError("Missing or mismatched imported file: "+name)
            if supplied[name].parent!=path.parent:
                raise RuntimeError("Import files must be together with their part manifest")
        verify_merged(path.parent,manifest)
        for name in [*manifest["files"],path.name]:
            if not name.startswith("phase_b_rerun_") or Path(name).name!=name:
                raise RuntimeError("Invalid imported filename")
            dest=HERE/name
            source=supplied[name]
            if dest.exists():
                if file_hash(dest)!=file_hash(source):
                    raise RuntimeError("Refusing to overwrite existing import: "+name)
            else:
                atomic_copy(source,dest)
        verify_merged(HERE,manifest)
    print("Imported and re-verified "+str(len(manifests))+" whole parts.")

def parser():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--parts",nargs="+",type=int,choices=(1,2,3,4),default=[1,2,3,4])
    p.add_argument("--arm-o-worktree",default=DEFAULT_ARMS["O"])
    p.add_argument("--arm-r-worktree",default=DEFAULT_ARMS["R"])
    p.add_argument("--python313",default=PY313)
    p.add_argument("--workers",type=int)
    p.add_argument("--resume",action="store_true")
    p.add_argument("--status",action="store_true")
    p.add_argument("--test-mode",action="store_true")
    p.add_argument("--crosscheck",action="store_true")
    p.add_argument("--machine-label",default=socket.gethostname())
    p.add_argument("--cpu-budget",type=int,default=cpu_budget())
    p.add_argument("--priority",choices=("below-normal","normal"),default="below-normal")
    p.add_argument("--import-part",nargs="+",metavar="FILES")
    return p

def controller_lock(prefix):
    handle=open(HERE/(prefix+"controller.lock"),"a+b")
    handle.seek(0,2)
    if handle.tell()==0:
        handle.write(b"x"); handle.flush()
    handle.seek(0)
    if os.name=="nt":
        import msvcrt
        msvcrt.locking(handle.fileno(),msvcrt.LK_NBLCK,1)
    else:
        import fcntl
        fcntl.flock(handle.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
    return handle

def main():
    args=parser().parse_args()
    validate_label(args.machine_label)
    if args.cpu_budget<2:
        raise ValueError("CPU budget must be at least two")
    prefix=prefix_for(args)
    if args.status:
        path=HERE/(prefix+"progress.json")
        if not path.exists():
            print("No progress file: "+str(path)); return
        progress=read_json(path)
        print(f"{progress['machine_label']}: {progress['status']}; cap {progress['current_cap']} ({progress['cap_source']})")
        for part,counts in progress["parts"].items():
            print("Part "+part+": "+", ".join(f"{k}={v}" for k,v in counts.items()))
        print("Updated "+progress["updated_utc"]+"; estimated finish "+str(progress["estimated_finish_local"]))
        return
    install_guard(HERE)
    lock=controller_lock(prefix)
    if args.import_part:
        check_sources({"O":Path(args.arm_o_worktree),"R":Path(args.arm_r_worktree)})
        import_parts(args.import_part,args); return
    arms,metadata,registered,smoke,identity,proof=enumerate_startup(args,prefix)
    entries=smoke if args.test_mode or args.crosscheck else registered
    if args.crosscheck and sorted(set(args.parts))!=[1,2,3,4]:
        raise ValueError("--crosscheck always executes all 16 tasks")
    entries=[e for e in entries if e["part"] in args.parts]
    batch=Batch(args,prefix,entries,arms,identity,proof)
    batch.run()

if __name__=="__main__":
    try:
        main()
    except BaseException as exc:
        if isinstance(exc,SystemExit):
            raise
        print("HALT: "+str(exc),file=sys.stderr)
        sys.exit(1)
