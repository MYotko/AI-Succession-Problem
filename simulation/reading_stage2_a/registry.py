"""Frozen registry and specs-only membership. D sections 1 and 5.2."""
from v3 import reading_a6 as native
from v3 import tables_a10 as tables
from v3.gates import ALPHAS, CAPABILITIES
from .common import require, digest

FAMILIES = ("sqrt", "crowding", "sigma_squared_x10", "sigma_squared_x0.1")
BASE = dict(alpha=1.0, capability=1.5, kappa=8.0, theta=0.5, steps=500,
            crowding="total", variant=None, k_star=1.8, g="linear")
def make_registry():
    full = native.headline_comparisons()
    a6 = [r for r in full if r["arm"] in FAMILIES[1:]]
    old = [r for r in full if r["arm"] not in FAMILIES[1:]]
    corners = ("weight_corner_k0.75_t0.25", "weight_corner_k0.75_t0.75",
               "weight_corner_k8_t0.25", "weight_corner_k8_t0.75")
    complement = [dict(kind="boundary", arm=a) for a in (*corners, "horizon")]
    complement += [dict(kind="cap_star", arm=a, alpha=x) for a in corners for x in ALPHAS]
    require(len(a6) == 8 and sorted(old, key=repr) == sorted(complement, key=repr), "A6 registry complement")
    a10 = [dict(kind="boundary", arm="sqrt")] + [dict(kind="cap_star", arm="sqrt", alpha=a) for a in ALPHAS]
    result = []
    for component, entries, size, seed in (("A10", a10, 18, 20261011), ("A6", a6, 33, 20260929)):
        for source in entries:
            r = dict(source)
            arm, kind = r["arm"], r["kind"]
            family = "A10arm" if component == "A10" else "A6"
            key = family + "." + ("boundary" if kind == "boundary" else "capstar") + "." + arm
            if kind == "cap_star": key += "." + repr(r["alpha"])
            af = dict(BASE, component=arm, category="a10_arm" if arm == "sqrt" else "a6_" + arm, grid="R1")
            cf = dict(BASE, component="main", category="R1")
            if arm == "sqrt": af["g"] = "sqrt"
            else: af.update(arm="a6_" + arm, variant="crowding_reproductive" if arm == "crowding" else arm)
            if arm == "crowding": af["crowding"] = "reproductive"
            if kind == "cap_star":
                af["grid"] = "R2"; cf["category"] = "R2"
                for f in (af, cf): f.pop("alpha"); f.pop("capability")
            r.update(identity=key, component=component, family=family, family_size=size,
                     level_alpha=0.05/size, undefined_tail=0.05/(2*size) if kind == "boundary" else None,
                     seed=seed, resamples=50000, quantile_method="inverted_cdf",
                     grid=list(native.SIGMA_GRID if arm.startswith("sigma") else native.R1_GRID) if kind == "boundary" else list(CAPABILITIES),
                     arm_filters=af, comparator_filters=cf,
                     arm_seeds=100, comparator_seeds=400 if kind == "boundary" else 75)
            result.append(r)
    return sorted(result, key=lambda r:r["identity"])
REGISTRY = make_registry()
REGISTRY_DIGEST = digest(REGISTRY)
A10_COMPLEMENT = [dict(kind=k, arm=a, **({} if k=="boundary" else {"alpha":x}))
                  for a in ("k1p5","k2p3") for k in ("boundary","cap_star")
                  for x in ([None] if k=="boundary" else ALPHAS)]

def flat_job(component, job):
    c=job["config"]; m=c["model"]; inst=m["instrument"]
    return dict(job_id=job["id"], component=component, category=c["category"],
                grid=c.get("grid",c.get("a6_grid",c["category"])),
                arm=c.get("a6_arm"), variant=c.get("a6_variant"),
                rr=m["reproduction_rate"], alpha=m["alpha"], capability=m["successor_capability"],
                kappa=m.get("kappa",8.0), theta=m.get("theta",0.5), crowding=m.get("crowding","total"),
                steps=c["steps"], k_star=inst["k_star"], g=inst["g"])

def matches(row, entry, side):
    f=entry[side+"_filters"]
    if not all(row.get(k)==v for k,v in f.items()): return False
    if entry["kind"] == "boundary": return row["rr"] in entry["grid"]
    return row["rr"] == 0.064 and row["alpha"] == entry["alpha"] and row["capability"] in entry["grid"]

def registered_jobs(component, spec):
    if component == "main":
        expected=tables.paired_runs(*tables.STAGE2_PATHS["nominal"])
        require(len(spec["jobs"])==24900, "registered comparator job count")
    else:
        expected=tables.stage2_runs(tables.STAGE2_PATHS)[component]
        require(len(spec["jobs"])==tables.STAGE2_RUN_COUNTS[component], "registered arm job count")
    require(spec["jobs"]==expected, "registered job list differs")

def structure(specs, fixture, layout):
    rows={}; jobs={}
    seen_ids=set(); seen_seeds=set()
    for c,s in sorted(specs.items()):
        if not fixture: registered_jobs(c,s) # A3.5 rows 1 and 3.
        else:
            l=layout["comparator" if c=="main" else c]
            require(len(s["jobs"])==l["job_count"], "fixture job count")
        for j in s["jobs"]:
            require(j["id"] not in seen_ids, "duplicate job id")
            require(j["seed"] not in seen_seeds, "duplicate seed")
            seen_ids.add(j["id"]); seen_seeds.add(j["seed"])
            r=flat_job(c,j); key=c+"/"+j["id"]; rows[key]=r; jobs[key]=j
    selected={}
    covered=set()
    for e in REGISTRY:
        sides={}
        for side,c in (("arm",e["arm"]),("comparator","main")):
            if c not in specs: sides[side]=[]; continue
            keys=sorted(k for k,r in rows.items() if matches(r,e,side))
            n=e[side+"_seeds"]
            if fixture: n=layout["comparator" if c=="main" else c]["seeds_per_cell"] # A3.5 row 2.
            require(type(n) is int and n>0, "cell count declaration")
            field="rr" if e["kind"]=="boundary" else "capability"
            require(all(sum(rows[k][field]==x for k in keys)==n for x in e["grid"]), "cell seed count")
            sides[side]=keys; covered.update(keys)
        selected[e["identity"]]=sides
    # Registered nominal intentionally includes noncontributing jobs. A8.1.
    require(all(k in covered for k in rows if fixture or rows[k]["component"]!="main"), "job outside registry cells")
    return rows,jobs,selected

def contribution_map(component, specs, rows, jobs, selected):
    quantities={}
    for e in REGISTRY:
        if e["component"]!=component: continue
        key=e["identity"]; a=selected[key]["arm"]; n=selected[key]["comparator"]
        quantities[key]=sorted(a+n)
        quantities[key.replace(".boundary.",".boundary_point.").replace(".capstar.",".capstar_point.")]=sorted(a+n)
        if e["kind"]=="boundary":
            for rr in e["grid"]:
                ar=[k for k in a if rows[k]["rr"]==rr]; nr=[k for k in n if rows[k]["rr"]==rr]
                quantities[e["family"]+".survival."+e["arm"]+"."+repr(rr)]=ar
                quantities[e["family"]+".survival_difference."+e["arm"]+"."+repr(rr)]=sorted(ar+nr)
    members=sorted(set(k for ks in quantities.values() for k in ks))
    runs={}
    for k in members:
        r=rows[k]
        runs[k]={f:r[f] for f in ("component","category","grid","rr","alpha","capability")}
        runs[k]["phase"]=jobs[k]["config"]["phase"]
    return dict(schema="a10-stage2-contributing-runs-1",basis="specs only; sealed before opening outputs",
                specs={c:digest(s) for c,s in sorted(specs.items()) if c in {rows[k]["component"] for k in members}},
                runs=runs,quantities=dict(sorted(quantities.items())))
