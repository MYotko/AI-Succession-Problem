"""G6 and G7: native loading, explicit history binding, permitted row fields only."""
from pathlib import Path
from functools import lru_cache
from v3 import tables_a10 as tables
from v3.production_tables import ProductionTables,row_key
from v3.calibration import load_calibration
from v3.context import Context
from v3.study import capabilities
from v3.policies import execution_policy_class
from .common import require,unseal,digest
from .contracts import marker,committed_check
from .incidence import REASON
COUNTS={"nominal":19500,"sqrt":2875,"crowding":2875,"sigma_squared_x10":625,"sigma_squared_x0.1":625}
PARENT_FILE="fd86358a39e3b643fb9adc4e81a2372915ca50a1866e9b0e330a874b41746e01"
PARENT_SEAL="bf0f7c3f10310558d567b6b3f7c24f6f99f2fe6eb71fd830cccfd8e2aa0bd6d6"
VARIANTS={
"sigma_squared_x10":("aecef21ab61e0c7078b7fcf40fee540f9891a0ac3e32e995699cbfbd8264dbce","256380ab7c65465766f0407c6f8468dd35dbfaced08c3db72388b1e0882abca9"),
"sigma_squared_x0.1":("93c35a47e9aed3bd904fdc79ae24feb4015b75eb33bd42aa3a5220ae2ce88394","d9cde18fd08d6eabe171115a3b9cbc1807e14380286e185290916a07f81e2aa4")}
ERROR_FIELDS=("P","M","alpha","E","E2","extension_error_bound","tests_round1","tests_round2")
def calibration_pin(name,fixture,byte_hash,seal_hash):
    wanted=(PARENT_FILE,PARENT_SEAL)
    if not fixture and name in VARIANTS: wanted=VARIANTS[name] # A3.5 row 4.
    require((byte_hash,seal_hash)==wanted, "calibration pin")

def a13_refusal_pin(hash_value,fixture,authorized):
    if fixture: require(hash_value==authorized, 'fixture A13 refusal binding') # A3.5 row 11.
    else:
        from v3.history_a14 import ADMISSION_HASH
        require(hash_value==ADMISSION_HASH, 'A13 refusal constant')

def verify_families(state):
    families={}; ledger=state["ledger"]
    for c in sorted(state["descriptors"]):
        name="nominal" if c=="main" else c
        d=state["descriptors"][c]; docs=state["files"][c]; f=d["family"]
        calibration=load_calibration(d["calibration"],registered=True,instrument=tables.family_instrument(name))
        calibration_pin(name,state["fixture"],ledger.hash(c+"/calibration"),calibration["sha256"])
        loaded=ProductionTables(docs["table"],calibration_hash=calibration["sha256"],registered=True,receipt=docs["a10_receipt"])
        loaded.require_a10(tables.family_instrument(name))
        m=loaded.payload["manifest"]; marker(m,state["fixture"])
        require(m["a10"]["family"]==name, "table family")
        require("a13_admission" in m, "admission binding absent")
        b=m["a13_admission"]; scope=b["scope"]; admitted=set(b["rows"])
        require(scope=='A10_nominal_after_A14' if name=='nominal' else scope in ('validation_launched_under_A13','A10_stage2_after_A16_r1','A10_stage2_after_A16_r2'), 'family admission scope')
        require(len(loaded.rows)==COUNTS[name] and b["primary_rows"]==COUNTS[name], "primary row count")
        vr=unseal(docs["validation_receipt"]); ar=unseal(docs["a10_receipt"])
        require(vr["calibration_sha256"]==calibration["sha256"], "validation calibration")
        original=unseal(docs["admission_check"]); current=original; rounds=0
        if scope=="validation_launched_under_A13":
            require(original["outcome"]=="passed" and original["scope"]==scope and original["plan_hash"]==vr["plan_hash"] and "a16" not in b and f.get("a16") is None, "original admission binding")
        elif scope=="A10_nominal_after_A14":
            require(name=="nominal" and "a16" not in b, "nominal admission scope")
            a13=unseal(docs["a13_round_admission"])
            h=ledger.hash(c+"/family/a13_round_admission")
            require(h==vr["refusals"]["a13_admission_record_sha256"]==vr["a13_round"]["admission_record_sha256"], "A13 refusal receipt binding")
            a13_refusal_pin(h,state['fixture'],state['auth'].get('a13_refusal_admission_record_sha256'))
            require(a13["outcome"]=="refused" and original["outcome"]=="passed", "nominal admission outcomes")
            require(original["scope"]==scope and original["plan_hash"]==vr["a14_round"]["plan_hash"]==m["a14"]["plan_hash"], "A14 plan binding")
            require(a13["plan_hash"]==vr["a13_round"]["plan_hash"]==m["a14"]["a13_plan_hash"] and m["a14"]["original_plan_hash"]==vr["plan_hash"], "A14 preserved plans")
            require(ledger.hash(c+"/family/admission_check")==vr["a14_round"]["admission_record_sha256"], "A14 admission receipt binding")
            for r in ("a13","a14"):
                require(ledger.hash(c+"/family/"+r+"_public_record")==vr[r+"_round"]["public_file_sha256"], "nominal public binding")
                unseal(docs[r+"_round_record"])
            rounds=2
        elif scope in ("A10_stage2_after_A16_r1","A10_stage2_after_A16_r2"):
            from v3.validation_extension_a16 import family_identity,round_identity,admission_identity
            q=int(scope[-1]); rounds=q
            require(name!="nominal" and f.get("a16") is not None, "A16 scope")
            a16=docs["a16"]; family=unseal(a16["family_record"]); bound=b["a16"]
            require(family["published_round"]==q and family["terminal"] is None and family["family"]==name, "A16 family state")
            require(family_identity(family)==bound["family_record_sha256"], "A16 family identity")
            require(original["outcome"]=="refused" and original["scope"]=="validation_launched_under_A13" and original["plan_hash"]==vr["plan_hash"], "A16 original refusal")
            require(ledger.hash(c+"/family/admission_check")==vr["refusals"]["original"]["admission_record_sha256"], "A16 original refusal binding")
            require(set(a16["rounds"])=={"r"+str(x) for x in range(1,q+1)}, "A16 used rounds")
            for r in range(1,q+1):
                rk="r"+str(r); rr=a16["rounds"][rk]; rd=unseal(rr["round_record"]); ad=unseal(rr["admission_record"])
                label=c+"/family/a16/"+rk+"/"
                require(ledger.hash(label+"admission_record")==vr["a16_rounds"][rk]["admission_record_sha256"] and ledger.hash(label+"public")==vr["a16_rounds"][rk]["public_file_sha256"], "A16 round file binding")
                require(vr["a16_rounds"][rk]["plan_hash"]==ad["plan_hash"]==rd["plan_hash"], "A16 round plan")
                require(ad["family"]==rd["family"]==name and ad["round"]==rd["round"]==r, "A16 round identity fields")
                if r==q:
                    current=ad
                    require(bound["family"]==name and bound["round"]==q and ad["plan_hash"]==bound["plan_hash"], "A16 admission plan binding")
                    require(round_identity(rd)==bound["round_record_sha256"] and admission_identity(ad)==bound["admission_record_sha256"], "A16 provenance identities")
                else:
                    require(ad["outcome"]=="refused" and ledger.hash(label+"admission_record")==vr["refusals"]["round1_admission_record_sha256"], "A16 round one refusal")
                    r1=bound["round1"]
                    require(r1["plan_hash"]==ad["plan_hash"] and r1["admission_record_sha256"]==ledger.hash(label+"admission_record") and r1["classifications_sha256"]==ad["classifications_sha256"], "A16 round one provenance")
        else: require(False, "unsupported admission scope")
        require(current['schema']=='v3-A13-admission-check-1' and current["outcome"]=="passed" and current["scope"]==scope and current["primary_rows"]==len(loaded.rows) and current["cap"]==len(loaded.rows)//1000 and current["residual_count"]==len(admitted) and set(current["residual_rows"])==admitted and current["admitted_set_sha256"]==b["admitted_set_sha256"], "admission record counts")
        looked={}
        labelrows={}
        if name in ("nominal","sqrt"):
            labels=unseal(docs["labels"])
            for row in labels["rows"]:
                require(row["violation"]==row["violation_count"]==len(row["violations"]), "A5 violation count")
                if row["violation"]:
                    labelrows[row["row_key"]]=dict(row=row["row_key"],violated_cells=row["violation"],total_exposure=row["violation_exposure_total"])
        if not admitted:
            require(b["rows"]=={} and b["admitted_set_sha256"]==digest({}) and not any(r["status"]=="not_estimable" for r in loaded.rows.values()), "empty admission evidence")
            expected=tables.expected_keys(tables.build_jobs(name,tables.STAGE2_PATHS[name][0]),calibration)
            require(set(loaded.rows)==expected, "case two full context keys")
        # D:405 configured contexts and A2.7 disclosure sets need no output.
        cache={}
        for key,job in state["jobs"].items():
            if state["rows"][key]["component"]!=c: continue
            cfg=job["config"]; model=cfg["model"]
            sig=(model["reproduction_rate"],model["alpha"],model["successor_capability"],model.get("n_agents",200))
            if sig not in cache:
                keys=set()
                for cap in capabilities(model["successor_capability"]):
                    if not admitted:
                        require((model["reproduction_rate"],model["alpha"],cap) in tables.contexts(name), "case two reachable context")
                    kernel=dict(reproduction_rate=model["reproduction_rate"],capability=cap,instrument=model["instrument"])
                    if name=="crowding": kernel["crowding"]="reproductive"
                    ctx=Context.build(kernel,calibration)
                    for rule in execution_policy_class():
                        stub=dict(rule_id=rule.rule_id,kernel_hash=ctx.kernel_hash,calibration_hash=ctx.calibration_hash,
                                  initial_population=model.get("n_agents",200),
                                  scoring=dict(alpha=model["alpha"],capability=cap,kappa=model.get("kappa",8.0),**model["instrument"]))
                        keys.add(row_key(stub))
                cache[sig]=keys
            looked[key]=sorted(set(cache[sig])&set(labelrows))
        # G7 checks the spec policy and forbids a labels file on no-label families.
        if name!="nominal":
            require(state["specs"][c]["a10_labels_policy"]==tables.STAGE2_LABELS_POLICY[name], "spec labels policy")
        if name in tables.NO_LABEL_FAMILIES:
            require("labels" not in f and ar["schema"]==tables.NO_LABEL_RECEIPT_SCHEMA and ar["labels_policy"]==tables.NO_LABEL_AUTHORITY and "labels" not in ar and "labels_sha256" not in ar, "variant labels policy")
        else: require(ar["schema"]=="v3-A10-table-receipt-1", "strict labels policy")
        hashes={k:ledger.hash(c+"/family/"+k) for k in f if k!="a16"}
        admission=dict(scope=scope,primary_rows=current["primary_rows"],cap=current["cap"],residual_count=current["residual_count"],
                       admitted_rows=len(admitted),rounds_used=rounds,
                       admission_record_sha256=hashes["admission_check"] if scope not in ("A10_stage2_after_A16_r1","A10_stage2_after_A16_r2") else ledger.hash(c+"/family/a16/r"+str(rounds)+"/admission_record"))
        errors={k:current[k] for k in ERROR_FIELDS if k in current} if rounds else {}
        if rounds and name!="nominal": errors["statement"]="at least 1 - alpha(1 + P/M), given the fitted family"
        families[name]=dict(status="recorded" if admitted else "no admitted rows",admitted=bool(admitted),hashes=hashes,
                            admission=admission,errors=errors,looked=looked,labelrows=labelrows,
                            no_accumulator_reason=REASON if not admitted else None,
                            provenance=dict(binding={k:b[k] for k in ('schema','scope','primary_rows','admitted_set_sha256')},
                                            a16={k:b['a16'][k] for k in ('family','round','plan_hash','family_record_sha256','round_record_sha256','admission_record_sha256','round1') if k in b['a16']} if 'a16' in b else None,
                                            refusals=vr.get("refusals"),rounds=vr.get("a16_rounds",vr.get("a14_round"))))
        # Release large rows; no continuation or row arithmetic enters reader outputs.
        del loaded
    return families

def verify_not_run(state):
    result={}; i=state["inputs"]; ledger=state["ledger"]
    for name,d in sorted(i["arms"].items()):
        if d["status"]=="run": continue
        root=Path(i["execution_simulation"]); table=root/tables.STAGE2_PATHS[name][1]
        require(not table.exists(), "not-run published table")
        for rel in ("v3/runs/a10_stage2/runs/"+name,"v3/runs/a10_stage2/"+name+"/runs_run"):
            require(not any((root/rel).glob("*/records/*")), "not-run records present")
        ev=d["evidence"]; auth=state["auth"]["not_run_evidence"][name]
        keys=set(ev)
        require(keys in ({"a16_family_record","refused_admission_record","a16_round_admission_records"},
                         {"refused_admission_record","closeout_record"}), "not-run evidence set")
        require(set(auth)==keys, "not-run authorized evidence")
        docs={}
        for key,path in ev.items():
            if isinstance(path,list):
                require(isinstance(auth[key],list) and len(auth[key])==len(path), "not-run evidence list")
                docs[key]=[ledger.load(p,"not_run/"+name+"/"+key+"/"+str(ix),h,sealed=True) for ix,(p,h) in enumerate(zip(path,auth[key]))]
            else: docs[key]=ledger.load(path,"not_run/"+name+"/"+key,auth[key],sealed=True)
        require(docs["refused_admission_record"]["outcome"]=="refused", "not-run original refusal")
        if "a16_family_record" in docs:
            fr=docs["a16_family_record"]
            require(fr['schema']=='v3-A16-family-1' and fr["family"]==name and fr["terminal"] is not None and fr["published_round"] is None, "not-run terminal latch")
            require(all(r["outcome"]=="refused" for r in docs["a16_round_admission_records"]), "not-run round outcome")
            # A10.8.8 resolves Q4: no count is inferred from terminal.round.
            reason=fr["terminal"]["reason"]
        else:
            close=docs["closeout_record"]
            allowed={"schema","family","status","reason","a16_entered","refused_admission_record","canonical_run_roots_checked","no_other_run_root_of_the_family_exists"}
            require(set(close)==allowed and close["schema"]=="a10-stage2-item42-closeout-1", "closeout schema")
            require(close["family"]==name and close["status"]=="not run" and close["a16_entered"] is False and close["no_other_run_root_of_the_family_exists"] is True, "closeout state")
            require(not table.with_suffix(".a16_family.json").exists(), "closeout A16 family record exists")
            require(close["refused_admission_record"]["sha256"]==auth["refused_admission_record"], "closeout refused record binding")
            reason=close["reason"]
        require(isinstance(reason,str) and bool(reason), "not-run reason")
        result[name]=reason
    return result
