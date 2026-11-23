"""G0-G2 input bindings and the twelve enumerated mode terms."""
import os
import platform
import re
import subprocess
from pathlib import Path
import numpy as np
from v3 import artifacts, tables_a10 as tables
from v3.compatibility_a10 import accepted_identities
from .common import require,digest,canonical,seal,unseal,identity,file_hash
from .io import Ledger
from .registry import FAMILIES,structure
from .collection import document_form,verification_form,destination,verify_collection
PYTHON_VERSION="3.13.12"
NUMPY_VERSION="2.4.4"
CODE_IDENTITY="93a453b27c82a9cb16ed0d04b1029168014b73c1f3d97f5b884e1b6d52f161da"
INV_S="stage2-sqrt-reading-input-inventory-1"
INV_C="stage2-crowding-reading-input-inventory-1"
INV_2="stage2-reading-input-inventory-2"
AUTH_KEYS={"schema","inventories","specification_set","specification_set_digest","requirements_sha256",
           "registration","not_run_evidence","sqrt_admission_check_sha256","supplementary_records"}
FIX_KEYS={"identity_records","a13_refusal_admission_record_sha256","fixture_list_hash","fixture_layout"}
COMPARATOR_FAMILY={"table","validation_receipt","cell_results","a10_receipt","labels","identity","admission_check",
                   "a13_round_admission","a13_round_record","a14_round_record","a14_public_record","a13_public_record"}
ARM_FAMILY={"table","validation_receipt","cell_results","a10_receipt","identity","admission_check","a16"}
def committed_bytes(relative):
    return subprocess.check_output(["git","show","HEAD:"+relative],cwd=artifacts.SIMULATION.parent,
                                   env=dict(os.environ,GIT_OPTIONAL_LOCKS="0"),timeout=60)
def committed_check(path,relative):
    require(Path(path).read_bytes()==committed_bytes(relative), "committed bytes differ")

def marker(manifest,fixture):
    if fixture: require(manifest.get("reader_fixture") is True, "fixture table marker") # A3.5 row 10.
    else: require("reader_fixture" not in manifest, "registered fixture table marker")

def model_keys(job,fixture):
    m=job["config"]["model"]
    require(not ({"carrying_capacity","rollout_steps"} & set(m)), "fixture-only model input")
    if fixture: # A3.5 row 5. Q1: F8 is recognized structurally, never by an external fixture id.
        require("n_agents" not in m or type(m["n_agents"]) is int and m["n_agents"]==0, "fixture-only model input")
    else: require("n_agents" not in m, "fixture-only model input")

def path_map_term(inputs,fixture):
    if not fixture: require('path_map' not in inputs, 'registered path_map') # A3.5 row 8.
    elif 'path_map' in inputs: require(isinstance(inputs['path_map'],dict), 'fixture path_map type')

def authorization_term(document,fixture):
    require(set(document)==AUTH_KEYS|(FIX_KEYS if fixture else set()), 'authorized key set')
    require(document['schema']==('a10-stage2-authorized-hashes-fixture-1' if fixture else 'a10-stage2-authorized-hashes-1'), 'authorized schema') # A3.5 row 9.

def registration_term(component,spec,pin,inventory_pin):
    if component=='main':
        require(spec['registration']==inventory_pin and spec['registration']['commit']==artifacts.A14_COMMIT, 'comparator registration pin')
        artifacts.verify_registration(spec['registration'],instrument=tables.NOMINAL,historical=True)
    else:
        require(spec['registration']==pin, 'arm registration pin')

def seed_term(spec,registry):
    require(spec['seed_registry_sha256']==digest(registry), 'seed registry digest')

def environment():
    require(platform.python_version()==PYTHON_VERSION and np.__version__==NUMPY_VERSION, "environment version")
    require(os.environ.get("PYTHONINTMAXSTRDIGITS")=="0", "integer conversion environment")
    require(artifacts.code_identity()==CODE_IDENTITY, "running code identity")
    artifacts.runtime(1) # A10.8.3; machine-bearing return value is discarded.

def setup(inputs_path,out=None,need_collection=False):
    ledger=Ledger(); inputs_path=Path(inputs_path).resolve()
    i=ledger.load(inputs_path,"inputs")
    require(i.get("schema")=="a10-stage2-reader-inputs-1", "input schema")
    document_form(i)
    verification_form(i)
    require(set(i["arms"])==set(FAMILIES), "arm names")
    require(type(i["fixture"]) is bool, "fixture mode declaration")
    environment()
    collection_sha256=verify_collection(ledger,inputs_path,i) if need_collection else None
    from v3.instrument import CONSTANTS_PATH,validate_constants
    constants=validate_constants(ledger.load(CONSTANTS_PATH,'a10_constants'))
    calibration_constants_producers={name:record['producer_code_hash'] for name,record in constants['a6_calibrations']['variants'].items()}
    rid=identity()
    require(rid["role"]=="A", "reader role")
    # Relative input paths resolve at the document; job configs are never rewritten.
    def resolve(value): return str((inputs_path.parent/Path(value).expanduser()).resolve())
    i["execution_simulation"]=resolve(i["execution_simulation"])
    i["authorized_hashes"]=resolve(i["authorized_hashes"])
    cp=i["comparator"]
    require(set(cp)=={"binding","execution_simulation","spec","root","family","calibration"}, "comparator input keys")
    require(set(cp["family"])==COMPARATOR_FAMILY, "comparator family keys")
    for k in ("binding","execution_simulation","spec","root","calibration"): cp[k]=resolve(cp[k])
    cp["family"]={k:resolve(v) for k,v in cp["family"].items()}
    descriptors={"main":cp}; run=set()
    for name,d in i["arms"].items():
        require(d.get("status") in ("run","not_run"), "arm status")
        if d["status"]=="not_run":
            require(set(d)=={"status","evidence"}, "not-run input keys")
            d["evidence"]={k:[resolve(p) for p in v] if isinstance(v,list) else resolve(v) for k,v in d["evidence"].items()}
            continue
        run.add(name)
        require(set(d)=={"status","inventory","spec","pre_spec","root","family","calibration","excluded_roots"}, "arm input keys")
        # Optional labels are checked against the validated family policy at G7.
        require(ARM_FAMILY<=set(d["family"])<=ARM_FAMILY|{"labels"}, "arm family keys")
        for k in ("inventory","spec","pre_spec","root","calibration"):
            if d[k] is not None: d[k]=resolve(d[k])
        for k,v in d["family"].items():
            if k!="a16": d["family"][k]=resolve(v)
            elif v is not None:
                require(set(v)=={"family_record","rounds"}, "A16 input keys")
                v["family_record"]=resolve(v["family_record"])
                require(set(v["rounds"]) in ({"r1"},{"r1","r2"}), "A16 input rounds")
                for rd in v["rounds"].values():
                    require(set(rd)=={"round_record","admission_record","public"}, "A16 round input keys")
                    for key in rd: rd[key]=resolve(rd[key])
        for ex in d["excluded_roots"]:
            require(set(ex)=={"path","reason","inventory_key"}, "excluded root keys")
            ex["path"]=resolve(ex["path"])
        descriptors[name]=d
    roots=[i["execution_simulation"],cp["execution_simulation"]]+[d["root"] for d in descriptors.values()]
    if out:
        destination(i,out)
        out=Path(out).resolve()
        require(not out.exists(), "output destination exists")
        require(all(not out.is_relative_to(Path(root)) for root in roots), "output overlaps an input root")
        require(not out.is_relative_to(artifacts.SIMULATION.parent), "output inside reader checkout")
    specs={c:ledger.load(d["spec"],c+"/spec",sealed=True) for c,d in sorted(descriptors.items())}
    flags={s["registered"] for s in specs.values()}
    require(all(type(s["registered"]) is bool for s in specs.values()) and len(flags)==1, "mixed registration modes")
    fixture=not next(iter(flags))
    require(i["fixture"] is fixture, "fixture mode disagreement")
    path_map_term(i,fixture)
    # Q2: fixture path_map is accepted as an inert optional object. A8.3 supplies actual paths.
    artifacts.verify_registration(i["registration"],instrument=tables.NOMINAL)
    a=ledger.load(i["authorized_hashes"],"authorized_hashes",sealed=True)
    authorization_term(a,fixture)
    require(a["specification_set_digest"]==digest(a["specification_set"]), "specification set digest")
    require(all(set(x)=={"name","sha256"} and isinstance(x["name"],str) and re.fullmatch("[0-9a-f]{64}",x["sha256"]) for x in a["specification_set"]), "specification set shape")
    require(re.fullmatch("[0-9a-f]{64}",a["requirements_sha256"]) is not None, "requirements hash form")
    require(a["registration"]==i["registration"], "authorized registration")
    require(set(a["inventories"])==run|{"comparator"} and set(a["not_run_evidence"])==set(FAMILIES)-run, "authorized component sets")
    require(a["sqrt_admission_check_sha256"] is None if "sqrt" not in run else isinstance(a["sqrt_admission_check_sha256"],str), "sqrt admission authorization")
    if fixture:
        require(set(a["identity_records"])==run|{"nominal"} and set(a["fixture_layout"])==run|{"comparator"}, "fixture authorized component sets") # A3.5 rows 1-3,6.
    else:
        seed_path=i.get("seed_registry",str(Path(i["execution_simulation"])/"v3/runs/registered/A10_stage2_seed_registry.json"))
        seed_doc=ledger.load(seed_path,"seed_registry",sealed=True)
        committed_check(seed_path,"simulation/v3/runs/registered/A10_stage2_seed_registry.json")
        for c,s in specs.items():
            if c!="main": seed_term(s,seed_doc) # A3.5 rows 6,7.
    inventories={}; inventory_provenance={}; files={}; output_hashes={}; supplementary=set(); accepted=accepted_identities()
    for c,d in sorted(descriptors.items()):
        name="comparator" if c=="main" else c; family="nominal" if c=="main" else c
        auth=a["inventories"][name]
        invdoc=ledger.load(d["binding" if c=="main" else "inventory"],c+"/inventory",auth["file_sha256"])
        inv=unseal(invdoc); inventories[c]=inv
        require(invdoc["sha256"]==auth["seal"], "authorized inventory seal")
        require(inv["schema"] in (INV_S,INV_C,INV_2), "inventory schema")
        require(inv["verdict"]=="complete and consistent" and inv["findings"]==[] and inv["identity"]["code_identity"]==CODE_IDENTITY, "inventory status")
        ri=inv["roots"]["runs"]; require(ri["all_checks_pass"] is True, "inventory root checks")
        spec=specs[c]
        require(ledger.hash(c+"/spec")==ri["spec"]["file_sha256"] and digest(spec)==ri["spec"]["seal"], "inventory spec binding")
        require(spec["code_hash"] in accepted, "spec producer")
        require(spec["schema"]=="v3-registered-1", "run spec schema")
        if c!="main":
            require(spec["code_hash"]==CODE_IDENTITY and spec["a10_family"]==c and spec["a10_stage"]==2, "arm spec identity")
            require(spec["a10_family_paths"]==dict(zip(("calibration_path","tables_path"),tables.STAGE2_PATHS[c])), "arm family paths")
        if not fixture: # A3.5 row 7.
            registration_term(c,spec,i['registration'],inv.get('registration_pin'))
        root=Path(d["root"])
        ledger.raw(root/"manifest.json",c+"/manifest")
        require(ledger.hash(c+"/manifest")==ledger.hash(c+"/spec"), "manifest differs from spec")
        output_hashes[c]=ledger.load(root/"verified_output_hashes.json",c+"/output_hashes",ri["verified_output_hashes_sha256"])
        require(digest(output_hashes[c])==ri["outputs_digest"], "output hash map digest")
        # A10.4: these inventory fields are recorded, never compared.
        inventory_provenance[c]=dict(checkout_commit=inv['identity'].get('checkout_commit'),
            runs={k:ri[k] for k in ('jobs','records','outputs','identity_file_sha256','manifest_file_sha256','path') if k in ri},
            spec_path=ri['spec'].get('path'),pull_dispatch_code_commit=spec.get('pull_dispatch',{}).get('code_commit'))
        pub=inv["published_files" if inv["schema"]==INV_S else "published_files_and_inputs"]
        inventory_provenance[c]['published_paths']={k:v['path'] for k,v in pub.items() if isinstance(v,dict) and 'path' in v}
        files[c]={}
        names={"table":"family_table","identity":"family_identity","admission_check":"a14_round_admission" if c=="main" else "a13_admission"}
        for k,p in d["family"].items():
            if k=="a16": continue
            label=c+"/family/"+k
            if c=="sqrt" and k=="admission_check" and names[k] not in pub:
                doc=ledger.load(p,label,a["sqrt_admission_check_sha256"]); unseal(doc)
            else:
                doc=ledger.bound(p,label,pub[names.get(k,k)])
            files[c][k]=doc
        ledger.bound(d["calibration"],c+"/calibration",pub["calibration"])
        if "sqrt"==c: require(ledger.hash(c+"/family/admission_check")==a["sqrt_admission_check_sha256"], "sqrt admission binding")
        if fixture: # A3.5 row 6.
            require(ledger.hash(c+"/family/identity")==a["identity_records"][family], "fixture identity authorization")
        else:
            committed_check(d["family"]["identity"],"simulation/"+str(Path(tables.STAGE2_PATHS[family][1]).with_name("family_identity.json")))
        if c=="main": require(Path(d["family"]["table"])==(Path(cp["execution_simulation"])/tables.STAGE2_PATHS["nominal"][1]).resolve(), "nominal table location")
        identity_record=files[c]["identity"]; vr=unseal(files[c]["validation_receipt"]); ar=unseal(files[c]["a10_receipt"])
        require(identity_record["family_file_sha256"]==ledger.hash(c+"/family/table") and identity_record["table_seal_sha256"]==files[c]["table"]["sha256"] and
                identity_record["receipt_file_sha256"]==ledger.hash(c+"/family/validation_receipt") and identity_record["sidecar_file_sha256"]==ledger.hash(c+"/family/cell_results"), "family identity chain")
        require(vr["table_seal_sha256"]==files[c]["table"]["sha256"] and vr["table_file_sha256"]==ledger.hash(c+"/family/table") and
                vr["cell_results_sha256"]==ledger.hash(c+"/family/cell_results"), "validation chain")
        require(ar["table_sha256"]==files[c]["table"]["sha256"] and ar["validation_receipt_sha256"]==ledger.hash(c+"/family/validation_receipt"), "A10 receipt chain")
        if "labels" in d["family"]:
            require(ar.get("labels_sha256")==ledger.hash(c+"/family/labels"), "labels binding")
        pre=d.get("pre_spec"); pe=pub.get("run_spec_family")
        reconstructed={k:v for k,v in spec.items() if k!="pull_dispatch"}
        if c!='main' and pe is not None and pe.get('present') is True:
            require(pre is not None,'pre-dispatch spec absent')
            predoc=ledger.bound(pre,c+"/pre_spec",pe)
            require(unseal(predoc)==reconstructed, "pre-dispatch spec reconstruction")
        for job in spec["jobs"]:
            model_keys(job,fixture)
            require(job["config"]["steps"]==500, "run horizon")
            require(job["config"]["tables_path"]==tables.STAGE2_PATHS[family][1] and job["config"]["calibration_path"]==tables.STAGE2_PATHS[family][0], "job family paths")
            require(job["config"]["model"]["instrument"]==tables.family_instrument(family).declaration(), "job instrument")
        a16=d["family"].get("a16")
        if a16 is not None:
            extra=pub
            if inv["schema"] in (INV_S,INV_C):
                supplementary.add(c); require(c in a["supplementary_records"], "A16 supplementary block absent")
                extra=a["supplementary_records"][c]
                require(set(extra)=={"a16_family_record","a16_round_records","a16_round_admission_records","a16_public_records"}, "A16 supplementary keys")
            fdoc=ledger.bound(a16["family_record"],c+"/family/a16/family_record",extra["a16_family_record"])
            fs={"family_record":fdoc,"rounds":{}}
            require(all(len(extra[x])==len(a16["rounds"]) for x in ("a16_round_records","a16_round_admission_records","a16_public_records")), "A16 inventory round count")
            for ix,r in enumerate(sorted(a16["rounds"])):
                fs["rounds"][r]={}
                for field,pubkey in (("round_record","a16_round_records"),("admission_record","a16_round_admission_records"),("public","a16_public_records")):
                    fs["rounds"][r][field]=ledger.bound(a16["rounds"][r][field],c+"/family/a16/"+r+"/"+field,extra[pubkey][ix])
            files[c]["a16"]=fs
    require(set(a["supplementary_records"])==supplementary, "A16 supplementary block set")
    # A10.6 resolves Q6: only explicitly listed producer fields are tested.
    ledger.verify_producers(accepted)
    rows,jobs,selected=structure(specs,fixture,a.get("fixture_layout",{}))
    state=dict(inputs=i,ledger=ledger,fixture=fixture,auth=a,specs=specs,descriptors=descriptors,inventories=inventories,inventory_provenance=inventory_provenance,
            files=files,output_hashes=output_hashes,rows=rows,jobs=jobs,selected=selected,reader_identity=rid,accepted=accepted,calibration_constants_producers=calibration_constants_producers)
    state['collection_sha256']=collection_sha256
    return state
