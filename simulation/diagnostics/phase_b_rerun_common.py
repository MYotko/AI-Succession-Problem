"""Operational support for the recovered Phase B runner. No model logic."""
import csv
import datetime as dt
import hashlib
import io
import json
import os
from pathlib import Path
import socket
import sys
import time

sys.dont_write_bytecode = True
NOTE_COMMIT = "43f125dfc200eeb262ef2e2e2c459c9715269592"
NOTE_HASH = "736cc7b513aa3e70df8a492f041de89a2e6ecd08364b865ce84ac75f31163f72"
BYTECODE_HASH = "2d79795ca50405ff2586a2751fb38861b592d32008aa5e1aebffd07619781d6b"
ARM_HEADS = {"O":"45409d469a82bb599fe354e8ae3760e4cc3af048",
             "R":"a370925d53a786a3cdaeb36543c02e7135a0ecab"}
FIELDS = ["mode","rr","phi","alpha","successor_capability","cop_cost_audit","seed",
 "survived","collapsed","extinct","final_population","peak_population","collapse_threshold",
 "final_ai_generation","yield_fired","yield_fire_count","yield_eval_count",
 "first_yield_fire_step","first_fire_advantage","first_fire_transition_cost","max_yield_margin",
 "mean_yield_margin","final_theta_capability","final_transfer_state","final_psi_inst_stock",
 "final_theta_tech_v2","final_l_t_v2","integral_u_sys","knowledge_transfer_verified","error"]
EXTRA = ["arm","part","run_id","derived_seed","started_utc","completed_utc","wall_seconds",
         "interpreter_version","numpy_version","machine_label"]
THREAD_ENV = ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS","NUMEXPR_NUM_THREADS")
DEFAULT_SCHEDULE = {"timezone":"local","default_workers":15,
 "modes":{"normal":15,"work":10},
 "rules":[{"days":["Mon","Tue","Wed","Thu","Fri"],"start":"07:00","end":"17:00","workers":10}]}
RETRIES = []

class ScopeViolation(BaseException):
    pass

def utc():
    return dt.datetime.now(dt.timezone.utc).isoformat()

def canonical(value):
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",",":"), allow_nan=False)

def digest(data):
    return hashlib.sha256(data).hexdigest()

def file_hash(path):
    h=hashlib.sha256()
    tail=b""
    with Path(path).open("rb") as source:
        while True:
            block=source.read(1024*1024)
            if not block:
                break
            block=tail+block
            if block.endswith(b"\r"):
                block,tail=block[:-1],b"\r"
            else:
                tail=b""
            h.update(block.replace(b"\r\n",b"\n"))
    h.update(tail)
    return h.hexdigest()

def atomic_copy(source,destination):
    destination=Path(destination)
    temp=destination.with_name(destination.name+".tmp."+str(os.getpid()))
    with Path(source).open("rb") as inp, temp.open("wb") as out:
        while True:
            block=inp.read(1024*1024)
            if not block:
                break
            out.write(block)
        out.flush()
        os.fsync(out.fileno())
    retry(lambda:os.replace(temp,destination),"publish copied part")


def install_guard(directory):
    directory = Path(directory).resolve()
    null = os.path.normcase(os.path.abspath(os.devnull))
    def check(path):
        if isinstance(path, int):
            return
        p = Path(os.fsdecode(path)).resolve()
        if os.path.normcase(str(p)) == null:
            return
        if p.parent != directory or not p.name.startswith("phase_b_rerun_") or p.name in ("phase_b_rerun_design_note.md","phase_b_rerun_evidence"):
            raise ScopeViolation("Write outside authorized scope: "+str(p))
    def audit(event,args):
        if event == "open":
            path,mode,flags = args
            if (isinstance(mode,str) and any(x in mode for x in "wax+")) or (isinstance(flags,int) and flags & (os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND)):
                check(path)
        elif event in ("os.remove","os.rmdir","os.mkdir","os.chmod","os.utime","os.truncate"):
            check(args[0])
        elif event in ("os.rename","os.replace","os.link","os.symlink"):
            check(args[0]); check(args[1])
    sys.addaudithook(audit)

def retry(operation, description):
    start = time.monotonic()
    while True:
        try:
            return operation()
        except PermissionError as exc:
            RETRIES.append({"utc":utc(),"operation":description,"error":str(exc)})
            if time.monotonic()-start >= 5:
                raise
            time.sleep(.1)

def atomic(path, data):
    path=Path(path)
    temp=path.with_name(path.name+".tmp."+str(os.getpid()))
    with open(temp,"wb") as f:
        f.write(data if isinstance(data,bytes) else data.encode("utf-8"))
        f.flush()
        os.fsync(f.fileno())
    retry(lambda: os.replace(temp,path),"replace "+str(path))

def save(path,value):
    atomic(path, json.dumps(value,indent=2,ensure_ascii=True,allow_nan=False)+"\n")

def read_json(path):
    return retry(lambda: json.loads(Path(path).read_text(encoding="utf-8-sig")),"read "+str(path))

def csv_line(row,fields=None):
    out=io.StringIO(newline="")
    writer=csv.writer(out,lineterminator="\n")
    writer.writerow([row[k] for k in (fields or FIELDS+EXTRA)])
    return out.getvalue()

def csv_header(fields=None):
    fields=fields or FIELDS+EXTRA
    return csv_line(dict(zip(fields,fields)),fields)

def seed_check(task):
    label=(f"phase_b|{task['mode']}|{task['rr']:.5f}|{task['phi']:.4f}|"
           f"{task['alpha']:.4f}|{task['successor_capability']:.4f}|"
           f"{task['cop_cost_audit']}|{task['seed']}")
    return int(hashlib.md5(label.encode()).hexdigest(),16)%10000

def stable_id(arm,part,task):
    cell={k:task[k] for k in ("mode","rr","phi","alpha","successor_capability","cop_cost_audit","seed")}
    return f"{arm}_p{part}_{task['mode']}_{digest(canonical(cell).encode())[:24]}"

def cpu_budget(host=None):
    host=host or socket.gethostname()
    if host.upper()=="YOTKOTEST":
        return 16
    return len(os.sched_getaffinity(0)) if hasattr(os,"sched_getaffinity") else (os.cpu_count() or 1)

def default_schedule(host,maximum):
    if host.upper()=="YOTKOTEST":
        return json.loads(json.dumps(DEFAULT_SCHEDULE))
    return {"timezone":"local","default_workers":maximum,
            "modes":{"normal":maximum,"work":max(1,maximum-3)},"rules":[]}

def valid_count(value,maximum):
    if type(value) is not int or not 1 <= value <= maximum:
        raise ValueError(f"Worker count {value!r} outside 1..{maximum}")
    return value

def validate_schedule(schedule,maximum):
    if schedule["timezone"]!="local":
        raise ValueError("Only local timezone is supported")
    valid_count(schedule["default_workers"],maximum)
    for n in schedule.get("modes",{}).values():
        valid_count(n,maximum)
    for rule in schedule["rules"]:
        valid_count(rule["workers"],maximum)
        if not rule["days"] or any(x not in ("Mon","Tue","Wed","Thu","Fri","Sat","Sun") for x in rule["days"]):
            raise ValueError("Invalid schedule days")
        start=dt.time.fromisoformat(rule["start"]); end=dt.time.fromisoformat(rule["end"])
        if start>=end:
            raise ValueError("Rules must start before end on the same day")

def evaluate_schedule(schedule,override,now,maximum):
    validate_schedule(schedule,maximum)
    if override is not None:
        if set(override)-{"workers","mode","until"} or ("workers" in override)==("mode" in override):
            raise ValueError("Override requires exactly one of workers and mode")
        until=dt.datetime.fromisoformat(override["until"]) if "until" in override else None
        if until is not None and until.tzinfo is not None:
            until=until.astimezone().replace(tzinfo=None)
        n=override.get("workers") if "workers" in override else schedule.get("modes",{})[override["mode"]]
        valid_count(n,maximum)
        if until is None or now<until:
            return n,"override:"+("workers" if "workers" in override else override["mode"])
    matched=[r["workers"] for r in schedule["rules"]
             if now.strftime("%a") in r["days"] and
             dt.time.fromisoformat(r["start"]) <= now.time() < dt.time.fromisoformat(r["end"])]
    return (min(matched),"schedule:rule") if matched else (schedule["default_workers"],"schedule:default")

class Scheduler:
    def __init__(self,schedule_path,control_path,maximum,events):
        self.schedule_path=Path(schedule_path); self.control_path=Path(control_path)
        self.maximum=maximum; self.events=events
        self.cap=1; self.source="initial"; self.pending=None
        self.schedule=None; self.override=None; self.bad=None
    def poll(self,active,now=None):
        now=now or dt.datetime.now()
        try:
            schedule=read_json(self.schedule_path)
            override=read_json(self.control_path) if self.control_path.exists() else None
            cap,source=evaluate_schedule(schedule,override,now,self.maximum)
            self.schedule=schedule; self.override=override; self.bad=None
        except (ValueError,KeyError,TypeError,OSError) as exc:
            message=str(exc)
            if message!=self.bad:
                self.events.append({"event":"scheduler_warning","utc":utc(),"warning":message,
                                    "previous_cap":self.cap})
                self.bad=message
            cap,source=self.cap,self.source
        if (cap,source)!=(self.cap,self.source):
            change={"event":"worker_cap","requested_utc":utc(),"requested_local":now.isoformat(),
                    "previous_cap":self.cap,"cap":cap,"source":source,"active_at_request":active,
                    "effective_utc":None}
            if self.pending is not None:
                self.pending["superseded_utc"]=utc()
            self.events.append(change)
            self.pending=change; self.cap=cap; self.source=source
        if self.pending is not None and active<=self.cap:
            self.pending["effective_utc"]=utc()
            self.pending["active_at_effective"]=active
            self.pending=None
        return self.cap

def projected_finish(start,durations,schedule,override,maximum,active_remaining=None):
    """Discrete event simulation of queued jobs and non-preemptive cap changes."""
    import heapq
    now=start; index=0; active=[]
    for seconds in active_remaining or []:
        heapq.heappush(active,now+dt.timedelta(seconds=max(.01,seconds)))
    durations=list(durations)
    limit=0
    while index<len(durations) or active:
        cap,_=evaluate_schedule(schedule,override,now,maximum)
        while index<len(durations) and len(active)<cap:
            heapq.heappush(active,now+dt.timedelta(seconds=max(.01,durations[index])))
            index+=1
        if index==len(durations):
            return max(active,default=now)
        boundary=now.replace(second=0,microsecond=0)+dt.timedelta(minutes=1)
        if override and override.get("until"):
            expiry=dt.datetime.fromisoformat(override["until"])
            if expiry.tzinfo:
                expiry=expiry.astimezone().replace(tzinfo=None)
            if now<expiry<boundary:
                boundary=expiry
        now=min(boundary,active[0] if active else boundary)
        while active and active[0]<=now:
            heapq.heappop(active)
        limit+=1
        if limit>2000000:
            raise ValueError("ETA simulation horizon exceeded")
    return now
