"""Executed as source by a -c bootstrap in a fresh CPython 3.13 process."""
import ctypes
import importlib.machinery
import importlib.util
import platform
import subprocess
import threading
import traceback

def watch_parent(pid):
    if not pid:
        return
    def watch():
        if os.name=="nt":
            kernel=ctypes.WinDLL("kernel32",use_last_error=True)
            kernel.OpenProcess.argtypes=[ctypes.c_ulong,ctypes.c_int,ctypes.c_ulong]
            kernel.OpenProcess.restype=ctypes.c_void_p
            kernel.WaitForSingleObject.argtypes=[ctypes.c_void_p,ctypes.c_ulong]
            handle=kernel.OpenProcess(0x00100000,False,pid)
            if not handle:
                os._exit(130)
            kernel.WaitForSingleObject(handle,0xffffffff)
            os._exit(130)
        else:
            while os.getppid()==pid:
                time.sleep(.5)
            os._exit(130)
    threading.Thread(target=watch,daemon=True).start()

def library_threads(np):
    np.dot(np.ones((2,2)),np.ones((2,2)))
    result=[]
    try:
        from threadpoolctl import threadpool_info
        result=[{"library":x["filepath"],"threads":x["num_threads"],"api":x["internal_api"]}
                for x in threadpool_info()]
    except ImportError:
        pass
    if not result:
        roots=[Path(np.__file__).parent.parent/"numpy.libs",Path(np.__file__).parent/".libs",
               Path(sys.prefix)/"Library/bin",Path(sys.prefix)/"lib"]
        if os.name != "nt" and Path("/proc/self/maps").exists():
            loaded=set()
            for line in Path("/proc/self/maps").read_text().splitlines():
                name=line.split()[-1]
                if name.startswith("/") and "openblas" in name.lower():
                    loaded.add(Path(name).resolve())
            roots=[]
            for path in sorted(loaded):
                lib=ctypes.CDLL(str(path))
                for symbol in ("scipy_openblas_get_num_threads64_","openblas_get_num_threads64_",
                               "scipy_openblas_get_num_threads","openblas_get_num_threads"):
                    if hasattr(lib,symbol):
                        fn=getattr(lib,symbol); fn.restype=ctypes.c_int
                        result.append({"library":str(path),"symbol":symbol,"threads":fn(),
                                       "discovery":"loaded /proc/self/maps entry"})
                        break
        for directory in roots:
            if not directory.exists():
                continue
            for path in directory.iterdir():
                if "openblas" not in path.name.lower() or not any(x in path.name for x in (".dll",".so",".dylib")):
                    continue
                lib=ctypes.CDLL(str(path))
                for symbol in ("scipy_openblas_get_num_threads64_","openblas_get_num_threads64_",
                               "scipy_openblas_get_num_threads","openblas_get_num_threads"):
                    if hasattr(lib,symbol):
                        fn=getattr(lib,symbol); fn.restype=ctypes.c_int
                        result.append({"library":str(path),"symbol":symbol,"threads":fn()})
                        break
    if not result or any(x["threads"]!=1 for x in result):
        raise RuntimeError("Effective numerical thread limit not verified as one: "+repr(result))
    return result

def module_audit(worktree,main_root):
    result={}
    for name,module in list(sys.modules.items()):
        source=getattr(module,"__file__",None)
        if not source:
            continue
        path=Path(source).resolve()
        if "simulation" not in [x.lower() for x in path.parts]:
            continue
        if not path.is_relative_to(worktree) or path.is_relative_to(main_root):
            raise RuntimeError("Simulation import escaped arm: "+name+" "+str(path))
        result[name]={"path":str(path),"sha256_lf":file_hash(path),"basis":"LF-normalized file bytes"}
    return result

def identity_checks(module):
    expected={"N_AGENTS":200,"N_STEPS":500,"DRY_N_STEPS":120,"SURVIVAL_THRESHOLD":30,
              "SUCCESSOR_GENERATION":2,"KNOWLEDGE_TRANSFER_THRESHOLD":.1,"PHI_DEFAULT":25.,
              "MODE_DEFAULT_SEEDS":{"A":100,"B":75,"C":150,"dry-run":5},"CSV_FIELDS":FIELDS}
    for name,value in expected.items():
        if getattr(module,name)!=value:
            raise RuntimeError("Identity mismatch: "+name)
    grids={
      "A":((.055,.056,.057,.058,.059,.06,.062,.064,.066),(5,10,25,100),(.5,1.,1.5),(1.5,),(True,)),
      "B":((.057,.06,.064,.07),(25.,),(.5,.75,1.,1.25,1.5),(1.2,1.5,2.,2.5,3.,4.,5.),(True,)),
      "C":((.057,.06,.064),(25.,),(.5,1.,1.5),(1.5,2.5,3.),(True,False))}
    for mode,grid in grids.items():
        config=module.MODE_CONFIG[mode]
        if config["steps"]!=500:
            raise RuntimeError("Identity mismatch: horizon "+mode)
        for key,value in zip(("rr_values","phi_values","alpha_values","successor_caps","cop_values"),grid):
            if tuple(config[key])!=value:
                raise RuntimeError("Identity mismatch: "+mode+" "+key)
    return expected

def encode_task(module,arm,part,task):
    own=module._task_seed(task["mode"],task["rr"],task["phi"],task["alpha"],
                          task["successor_capability"],task["cop_cost_audit"],task["seed"])
    return {"arm":arm,"part":part,"task":task,"derived_seed":own,
            "cell_key":module._cell_key(task),"run_id":stable_id(arm,part,task)}

def enumerate_tasks(module,arm):
    registered=[]
    if arm=="O":
        pairs={(0.5,5.0),(1.,2.5),(1.,3.),(1.25,2.5),(1.5,2.5)}
        for task in module._build_tasks("B",75):
            if (task["alpha"],task["successor_capability"]) in pairs:
                registered.append(encode_task(module,arm,1,task))
        for mode,n,part in (("A",100,2),("C",150,3)):
            registered.extend(encode_task(module,arm,part,t) for t in module._build_tasks(mode,n))
    else:
        for mode,n in (("A",25),("C",50)):
            registered.extend(encode_task(module,arm,4,t) for t in module._build_tasks(mode,n))
    smoke=[]; extras=[]
    for mode in ("B","A","C"):
        for task in module._build_tasks(mode,152):
            if task["seed"] not in (150,151):
                continue
            take=(mode=="B" and arm=="O" and task["rr"]==.06 and task["alpha"]==1. and task["successor_capability"]==3.)
            take=take or (mode=="A" and task["rr"] in ((.055,.066) if arm=="O" else (.066,)) and task["phi"]==25 and task["alpha"]==1.)
            take=take or (mode=="C" and task["rr"]==.06 and task["alpha"]==1. and task["successor_capability"]==2.5)
            part={"B":1,"A":2,"C":3}[mode] if arm=="O" else 4
            if take:
                smoke.append(encode_task(module,arm,part,task))
            elif arm=="O" and mode=="A" and task["rr"]==.055:
                extras.append(encode_task(module,arm,2,task))
    return {"registered":registered,"smoke":smoke,"extra_smoke":extras}

def serial(value):
    if isinstance(value,dict):
        return {str(k):serial(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)):
        return [serial(v) for v in value]
    if hasattr(value,"tolist"):
        return value.tolist()
    if hasattr(value,"item"):
        return value.item()
    return value

def child_main(request):
    start=time.perf_counter(); started=utc()
    install_guard(request["directory"])
    watch_parent(request.get("parent_pid"))
    if os.name != "nt" and request["priority"] == "below-normal":
        os.nice(10)
    if sys.version_info[:2]!=(3,13):
        raise RuntimeError("Bytecode requires CPython 3.13")
    worktree=Path(request["worktree"]).resolve()
    main_root=Path(request["main_root"]).resolve()
    os.chdir(worktree)
    sys.path[:]=[str(worktree),str(worktree/"simulation")]+[
        p for p in sys.path if p and not Path(p).resolve().is_relative_to(main_root)
        and Path(p).resolve()!=worktree]
    for key in THREAD_ENV:
        if os.environ.get(key)!="1":
            raise RuntimeError("Numerical thread environment not configured before import")
    head=subprocess.check_output(["git","-c","safe.directory="+str(worktree),"-C",str(worktree),"rev-parse","HEAD"],text=True).strip()
    if head!=ARM_HEADS[request["arm"]]:
        raise RuntimeError("Worktree HEAD changed")
    pyc=worktree/"simulation/diagnostics/monte_carlo_phase_b.pyc"
    if digest(pyc.read_bytes())!=BYTECODE_HASH:
        raise RuntimeError("Bytecode hash changed")
    loader=importlib.machinery.SourcelessFileLoader("monte_carlo_phase_b",str(pyc))
    spec=importlib.util.spec_from_loader(loader.name,loader)
    module=importlib.util.module_from_spec(spec)
    sys.modules[spec.name]=module
    loader.exec_module(module)
    checked=identity_checks(module)
    import numpy as np
    threads=library_threads(np)
    modules=module_audit(worktree,main_root)
    metadata={"arm":request["arm"],"worktree":str(worktree),"worktree_head":head,
              "bytecode_sha256":BYTECODE_HASH,"identity_checks":checked,"modules":modules,
              "interpreter_version":sys.version,"numpy_version":np.__version__,
              "effective_threads":threads,"thread_environment":{k:os.environ[k] for k in THREAD_ENV},
              "machine_label":request["machine_label"],"pid":os.getpid(),"priority":request["priority"]}
    if request["operation"]=="enumerate":
        metadata.update(enumerate_tasks(module,request["arm"]))
        save(request["output"],metadata)
        return
    expected_environment=request["identity"]["versions"][request["arm"]]
    if expected_environment != {"interpreter_version":sys.version,"numpy_version":np.__version__}:
        raise RuntimeError("Interpreter or NumPy version changed since startup")
    for name,pin in request["identity"]["executor_hashes"].items():
        if file_hash(main_root/"simulation/diagnostics"/name)!=pin:
            raise RuntimeError("Executor source changed before child execution: "+name)
    clean=subprocess.check_output(["git","-c","safe.directory="+str(worktree),"-C",str(worktree),
                                   "status","--porcelain"],text=True).strip()
    if clean:
        raise RuntimeError("Worktree modified before child execution")
    entry=request["entry"]; task=entry["task"]
    if request["non_registered"] and task["seed"] not in (150,151):
        raise RuntimeError("Test execution attempted a registered seed index")
    candidates=module._build_tasks(task["mode"],task["seed"]+1)
    match=[t for t in candidates if t==task]
    if len(match)!=1:
        raise RuntimeError("Task is not exactly a recovered builder task")
    task=match[0]
    if seed_check(task)!=entry["derived_seed"]:
        raise RuntimeError("Seed cross-check failed in run child")
    captured=[]
    init_code=module.GardenModel.__init__.__code__
    def observer(frame,event,arg):
        if event=="return" and frame.f_code is init_code:
            captured.append(frame.f_locals["self"])
            sys.setprofile(None)
    sys.setprofile(observer)
    try:
        original=module._run_single(task)
    finally:
        sys.setprofile(None)
    wall=time.perf_counter()-start
    if set(original)!=set(FIELDS):
        raise RuntimeError("Original row field mismatch")
    row={key:original[key] for key in FIELDS}
    row.update({"arm":entry["arm"],"part":entry["part"],"run_id":entry["run_id"],
                "derived_seed":entry["derived_seed"],"started_utc":started,"completed_utc":utc(),
                "wall_seconds":wall,"interpreter_version":sys.version,"numpy_version":np.__version__,
                "machine_label":request["machine_label"]})
    steps=[]
    if captured:
        dc=getattr(captured[0],"datacollector",{})
        count=len(dc.get("population",[]))
        for i in range(count):
            values={k:serial(v[i]) for k,v in dc.items() if isinstance(v,(list,tuple)) and len(v)>i}
            steps.append({"arm":entry["arm"],"part":entry["part"],"run_id":entry["run_id"],
                          "seed_index":task["seed"],"step":i,"recorded":values})
    step_data="".join(canonical(s)+"\n" for s in steps)
    atomic(request["steps_output"],step_data)
    metadata["modules"]=module_audit(worktree,main_root)
    if any(metadata["modules"].get(name)!=value for name,value in modules.items()):
        raise RuntimeError("Loaded simulation source changed during run")
    metadata["effective_threads_after"]=library_threads(np)
    completion={"status":"complete","entry":entry,"row":row,"metadata":metadata,
                "machine_label":request["machine_label"],"identity":request["identity"],
                "row_sha256":digest(csv_line(row).encode()),"row_count":1,
                "step_count":len(steps),"steps_sha256":digest(step_data.encode()),
                "end_reason":"original_error" if original["error"] else
                    ("horizon" if len(steps)>=task["steps"] else "step_returned_false"),
                "retry_events":RETRIES}
    save(request["output"],completion)

if __name__=="__main__":
    request=read_json(sys.argv[1])
    try:
        child_main(request)
    except BaseException as exc:
        save(request["output"]+".failure.json",{"status":"halt","error":repr(exc),
             "traceback":traceback.format_exc(),"machine_label":request.get("machine_label")})
        raise
