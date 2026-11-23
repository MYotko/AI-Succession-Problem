"""Ordered gates and deterministic component publication."""
import hashlib
import math
import os
import tempfile
import time
import resource
from pathlib import Path
from v3 import gates
from v3.artifacts import source_manifest
from .common import require,unseal,seal,write,write_bytes,digest,canonical,safe
from .contracts import setup,environment,CODE_IDENTITY,PYTHON_VERSION,NUMPY_VERSION
from .collection import collect
from .families import verify_families,verify_not_run
from .registry import REGISTRY,REGISTRY_DIGEST,A10_COMPLEMENT,contribution_map
from .comparison import cells,compare,descriptive,values as result_values
from .incidence import normalize,summarize,per_run_payload,STATEMENT,REASON
from .ladder import rung,CHECK,cell_structure
from .refusal import invocation,computation_started
FILES=("reading.json","values.json","contributing_runs.json","incidence_per_run.json","LADDER.json","SEAL.json")

def run_gates(state, components=("A10","A6")):
    ledger=state["ledger"]
    maps={c:contribution_map(c,state["specs"],state["rows"],state["jobs"],state["selected"]) for c in components}
    temps=[]
    try:
        # G3 must be on disk and sealed before the first output is opened.
        for c,m in maps.items():
            fd,p=tempfile.mkstemp(prefix="stage2-contributing-",suffix=".json")
            with os.fdopen(fd,"wb") as f:
                f.write(canonical(seal(m))+b"\n"); f.flush(); os.fsync(f.fileno())
            temps.append(p)
        keys=sorted(set(k for m in maps.values() for k in m["runs"]))
        keyhash={c:hashlib.sha256(b"a10-stage2-ladder-1") for c in components}
        results={}; records={}
        # G4 is completed for all contributing outputs before G5.
        for key in keys:
            c,jid=key.split("/",1); job=state["jobs"][key]; phase=job["config"]["phase"]
            root=Path(state["descriptors"][c]["root"])
            rec=ledger.load(root/phase/"records"/(jid+".json"),key+"/record")
            require(rec["status"]=="complete" and rec["job"]==job and rec["code_hash"]==state["specs"][c]["code_hash"], "completion record")
            rel=phase+"/outputs/"+jid+".json"
            expected=state["output_hashes"][c][rel]
            raw=ledger.raw(root/rel,key+"/output",expected)
            require(ledger.hash(key+"/output")==rec["output_hash"], "completion output hash")
            for comp in components:
                if key in maps[comp]["runs"]: keyhash[comp].update(raw)
            from .common import loads
            output=loads(raw)
            require(output["job"]==job and output["code_hash"]==rec["code_hash"], "output job binding")
            ledger.record_producers(key+"/output",output)
            require(all(v in state['accepted'] for v in ledger.producers.get(key+'/output',{}).values()), 'unaccepted producer')
            r=output["result"]
            # Retain only the fields D:215 and D:356 allow. Packed evidence is never unpacked.
            diagnostic=[{k:s[k] for k in ("time","population","capability","allocation_evaluated","survival_first","unavailable_rules") if k in s} for s in r["diagnostics"]]
            result={k:r[k] for k in ("steps","final_population","survived_threshold_30","population_path","fixture_tables")}
            result.update(diagnostics=diagnostic,yield_events=[{"time":e["time"]} for e in r["yield_events"]],
                          continuation_availability={"allocation_steps":r["continuation_availability"]["allocation_steps"]})
            if "a13_decision_incidence" in r: result["a13_decision_incidence"]=r["a13_decision_incidence"]
            results[key]=result
        for key in keys:
            r=results[key]; ds=r["diagnostics"]; job=state["jobs"][key]
            require(type(r["steps"]) is int and len(ds)==r["steps"]==job["config"]["steps"]==500, "run path length")
            require([s["time"] for s in ds]==list(range(r["steps"])) and all(type(s["time"]) is int for s in ds), "run step times")
            require(r["population_path"]==[s["population"] for s in ds] and r["population_path"][-1]==r["final_population"], "population consistency")
            require(all(type(p) is int for p in r['population_path']), 'population path type')
            require(all(type(s['capability']) in (int,float) and math.isfinite(s['capability']) for s in ds if 'capability' in s), 'capability type')
            require(type(r["final_population"]) is int and r["final_population"]>=0 and all(type(s["population"]) is int and s["population"]>=0 for s in ds), "population type")
            require(type(r["survived_threshold_30"]) is bool and r["survived_threshold_30"]==(r["final_population"]>=30), "survival consistency")
            require(r["fixture_tables"] is False, "fixture tables in output")
            require(all(isinstance(s.get("unavailable_rules",{}),dict) for s in ds), "unavailable rules type")
            # Bool incidence preconditions are assigned to G8 by A6.1/A7.1.
            try: fired=gates.fire_from_run({"job":job,"result":r})
            except (ValueError,KeyError,TypeError): require(False, "capability path")
            records[key]=dict(state["rows"][key],final_population=r["final_population"],fired=fired)
        families=verify_families(state) # G6 and G7, identical native loader in both modes.
        normalized={}; family_of={}
        for key in keys:
            c=key.split("/",1)[0]; name="nominal" if c=="main" else c
            f=families[name]; family_of[key]=name
            normalized[key]=dict(family=name,status=f["status"],incidence=normalize(results[key],f["admitted"]))
            if not f["admitted"]: normalized[key]["reason"]=REASON
        not_run=verify_not_run(state) # G9.
        ledger.verify_producers(state['accepted'])
        state.update(maps=maps,records=records,families=families,normalized=normalized,family_of=family_of,
                     not_run=not_run,ladder_keys={c:h.digest() for c,h in keyhash.items()})
        return state
    finally:
        for p in temps: Path(p).unlink()

def disclosure(members,state):
    rows={}
    for key in members:
        f=state["families"][state["family_of"][key]]
        for row in f["looked"].get(key,[]): rows[row]=f["labelrows"][row]
    return dict(disclosure_rows=[rows[k] for k in sorted(rows)],claims_conditional_on_violations=bool(rows))

def component_payload(state,component):
    entries=[e for e in REGISTRY if e["component"]==component]
    m=state["maps"][component]; key=state["ladder_keys"][component]
    rungs={"key/check":rung(key,CHECK)}
    for c in sorted({state["rows"][k]["component"] for k in m["runs"]}):
        records=[state["records"][k] for k in sorted(m["runs"]) if state["rows"][k]["component"]==c]
        rungs["records/"+c]=rung(key,records)
    vals={}; comparisons={}; native_pools={}
    for e in entries:
        name=e["arm"]; ident=e["identity"]
        if name in state["not_run"]:
            reason=state["not_run"][name]
            vals[ident]=dict(status="not run",verdict="undetermined",reason="arm not run: "+reason,
                estimate=None,interval=None,undefined_share=None,undefined_tail=e["undefined_tail"],level_alpha=e["level_alpha"])
            point=ident.replace(".boundary.",".boundary_point.").replace(".capstar.",".capstar_point.")
            vals[point]={"status":"not run"}
            if e["kind"]=="boundary":
                for rr in e["grid"]:
                    for kind in ("survival","survival_difference"):
                        vals[e["family"]+"."+kind+"."+name+"."+repr(rr)]={"status":"not run"}
            comparisons[ident]=dict(registry=e,status="not run",reason=reason)
            continue
        counts=[e["arm_seeds"],e["comparator_seeds"]]
        if state["fixture"]: # A3.5 row 2.
            layout=state["auth"]["fixture_layout"]
            counts=[layout[name]["seeds_per_cell"],layout["comparator"]["seeds_per_cell"]]
        arm,nominal=cells(e,list(state["records"].values()),counts)
        result=compare(e,arm,nominal)
        rungs["cells/"+ident]=rung(key,cell_structure(arm,nominal))
        rungs["result/"+ident]=rung(key,result)
        vals[ident]=result_values(result,e)
        comparisons[ident]=dict(registry=e,result=safe(result),found_counts={"arm":{repr(float(k)):len(v) for k,v in arm.items()},
                                                                         "comparator":{repr(float(k)):len(v) for k,v in nominal.items()}})
        if e["kind"]=="boundary":
            vals[ident.replace(".boundary.",".boundary_point.")]=dict(arm=result["arm_boundary"],nominal=result["nominal_boundary"])
            desc=descriptive(e,arm,nominal)
            rungs["result/"+e["family"]+".survival_difference."+name]=rung(key,desc)
            for d in desc:
                rr=d["rr"]; n=len(arm[rr]); count=int(sum(x>=30 for x in arm[rr])); p=count/n
                den=1+4/n; center=(p+2/n)/den; half=2*math.sqrt(p*(1-p)/n+1/n**2)/den
                vals[e["family"]+".survival."+name+"."+repr(rr)]=dict(n=n,count=count,rate=p,wilson=[max(0.0,center-half),min(1.0,center+half)])
                vals[e["family"]+".survival_difference."+name+"."+repr(rr)]=dict(difference=d["difference"],interval=d["interval95"])
        else:
            vals[ident.replace(".capstar.",".capstar_point.")]={
                side:dict(category_index=result[native]["step"],censored=result[native]["censored"])
                for side,native in (("arm","arm_cap_star"),("nominal","nominal_cap_star"))}
    for quantity,members in m["quantities"].items():
        vals["disclosure."+quantity]=disclosure(members,state)
        # Parse using the registry, because sigma names contain a dot.
        running=not any(quantity in [e["identity"],e["identity"].replace(".boundary.",".boundary_point.").replace(".capstar.",".capstar_point.")]
                        or (e["kind"]=="boundary" and any(quantity==e["family"]+"."+kind+"."+e["arm"]+"."+repr(rr) for kind in ("survival","survival_difference") for rr in e["grid"]))
                        for e in entries if e["arm"] in state["not_run"])
        if not running: continue
        iv,status,counts,pool=summarize(members,state["normalized"],state["family_of"],state["families"])
        vals["incidence."+quantity]=iv; vals["incidence_status."+quantity]=status; vals["incidence_counts."+quantity]=counts
        native_pools[quantity]=pool; rungs["incidence/"+quantity]=rung(key,pool)
    for name in sorted({"nominal"}|{e["arm"] for e in entries}):
        if name in state["not_run"]:
            vals["family."+name+".status"]=dict(status="not run",reason=state["not_run"][name]); continue
        f=state["families"][name]
        vals["family."+name+".status"]={"status":"run"}
        vals["family."+name+".admission"]=f["admission"]
        vals["family."+name+".labels"]=(dict(policy="a5_labels_required",labels_sha256=f["hashes"]["labels"]) if name in ("nominal","sqrt")
            else dict(policy="no_a5_labels_a16",disclosure="no A5 labels; FV asymptotic and uncertified"))
        for field,value in f["errors"].items(): vals["family_error."+name+"."+field]=value
    family="A10arm" if component=="A10" else "A6"
    vals["family_size."+family]=18 if component=="A10" else 33
    vals["label.comparator"]="produced under A13 and A14, amendments informed by outcomes"
    auth=state["auth"]
    provenance=dict(reader_identity=state["reader_identity"],running_identity=CODE_IDENTITY,
                    source_manifest_digest=digest(source_manifest()),python=PYTHON_VERSION,numpy=NUMPY_VERSION,
                    specification_set=auth["specification_set"],specification_set_digest=auth["specification_set_digest"],
                    requirements_sha256=auth["requirements_sha256"],registration=state["inputs"]["registration"],
                    authorized_hashes_sha256=state["ledger"].hash("authorized_hashes"),collection_sha256=state["collection_sha256"],
                    inputs=state["ledger"].entries,producers=state["ledger"].producers,inventory_records=state['inventory_provenance'],
                    calibration_constants_producers=state['calibration_constants_producers'])
    inc=per_run_payload(m['runs'],state['normalized'])
    excluded=[]
    for c,d in sorted(state["inputs"]["arms"].items()):
        if d["status"]=="run":
            for ex in d["excluded_roots"]:
                inv=state["inventories"][c]
                require(ex["inventory_key"]=="failed_attempt" and "failed_attempt" in inv, "excluded root inventory key")
                excluded.append(dict(component=c,path=inv["failed_attempt"]["path"],reason=inv["failed_attempt"]["not_run_reason"]))
    reading=dict(schema="a10-stage2-reading-1",component=component,mode="fixture" if state["fixture"] else "registered",
                 registry=entries,registry_digest=REGISTRY_DIGEST,comparisons=comparisons,values=safe(vals),
                 A10_complement_not_computed=A10_COMPLEMENT,
                 families={n:f for n,f in state["families"].items() if n=="nominal" or n in {e["arm"] for e in entries}},
                 incidence=native_pools,incidence_statement=STATEMENT,provenance=provenance,excluded_roots=excluded,
                 not_recomputed="Stage 1's 12 A10 and 25 A6 comparisons and seed-convergence seal are not recomputed.")
    # No per-job lookup map is needed in reading.json: all disclosures are in values.
    reading["families"]={n:{k:v for k,v in f.items() if k not in ("looked","labelrows")} for n,f in reading["families"].items()}
    if state["fixture"]: reading["fixture_list_hash"]=auth["fixture_list_hash"] # A3.5 row 12.
    return {"reading.json":seal(safe(reading)),"values.json":safe(dict(schema="a10-stage2-values-1",component=component,values=vals)),
            "contributing_runs.json":seal(m),"incidence_per_run.json":seal(inc),
            "LADDER.json":seal(dict(schema="a10-stage2-ladder-1",component=component,rungs=rungs))}

@invocation
def execute(command,inputs_path,out=None,component="both"):
    start=time.monotonic(); components=("A10","A6") if component=="both" else (component,)
    if command=='collect':
        environment()
        print('COLLECT '+collect(inputs_path,out))
        return
    state=setup(inputs_path,out,need_collection=True)
    # All arms are verified even for a single-component output, ensuring both/separate provenance equality.
    run_gates(state)
    ledger=state["ledger"]
    if command=="verify":
        ledger.verify()
        write(Path(out)/'verify.json',dict(status='pass',reader_identity=state['reader_identity']['sha256'],collection_sha256=state['collection_sha256']))
        print("VERIFIED "+str(len(state["records"]))+" jobs")
        return
    computation_started()
    outputs={c:component_payload(state,c) for c in components}
    ledger.verify()
    from .common import identity
    require(identity()==state['reader_identity'], "reader source changed")
    for c,documents in outputs.items():
        file_hashes={n:hashlib.sha256(canonical(v)+b"\n").hexdigest() for n,v in documents.items()}
        auth=state["auth"]
        payload=dict(schema="a10-stage2-seal-1",component=c,mode="fixture" if state["fixture"] else "registered",
                     files=file_hashes,reader_identity=state["reader_identity"]["sha256"],collection_sha256=state["collection_sha256"],
                     specification_set=auth["specification_set"],specification_set_digest=auth["specification_set_digest"],
                     requirements_sha256=auth["requirements_sha256"])
        if state["fixture"]: payload["fixture_list_hash"]=auth["fixture_list_hash"] # A3.5 row 12.
        documents["SEAL.json"]=seal(payload)
    # A11.1: complete all preparation before the first file under out is written.
    prepared={c:{n:canonical(documents[n])+b"\n" for n in FILES} for c,documents in outputs.items()}
    log=canonical(dict(wall_minutes=int((time.monotonic()-start)/60),
        jobs_verified=len(state["records"]),files_verified=len(ledger.entries),peak_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024))+b"\n"
    lines=[]
    for c in components:
        lines.append(c)
        for n in FILES: lines.append(n+" "+hashlib.sha256(prepared[c][n]).hexdigest())
    lines.extend(("READER "+state["reader_identity"]["sha256"],"VERIFIED "+str(len(state["records"]))+" jobs"))
    for c in components:
        for n in FILES:write_bytes(Path(out)/c/n,prepared[c][n],preserve_on_failure=True)
    write_bytes(Path(out)/"run_log.json",log,preserve_on_failure=True)
    print("\n".join(lines))
