"""Registered verdicts for the Phase B stage 2 rerun (phase_b_rerun_design_note.md, Sections 7 to 9).

Run: python simulation/diagnostics/phase_b_rerun_verdicts.py
Reads the four merged part run tables only, and writes phase_b_rerun_verdicts.json beside this
script. No ratio of two measured counts is computed; every rate is a count over a fixed design n.
"""
import csv
import json
import math
from collections import defaultdict
from pathlib import Path

DIAG = Path(__file__).resolve().parent
PART2 = DIAG
OUT = DIAG / "phase_b_rerun_verdicts.json"
Z = 2.0


def rows(path):
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def truthy(v):
    return v == "True"


def wilson(k, n, z=Z):
    p = k / n
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return centre - half, centre + half


def paired_se(diffs):
    n = len(diffs)
    mean = sum(diffs) / n
    var = sum((d - mean) ** 2 for d in diffs) / (n - 1)
    return mean, math.sqrt(var / n)


out = {"design_n_note": "rates are counts over fixed design n"}

# ---------------- P: Part 1 cliff pairs ----------------
P_TABLE = {(0.5, 5.0): (66, 72), (1.0, 2.5): (74, 75), (1.0, 3.0): (3, 10),
           (1.25, 2.5): (23, 37), (1.5, 2.5): (0, 1)}
p1 = rows(DIAG / "phase_b_rerun_part1_runs.csv")
fired = defaultdict(int)
celln = defaultdict(int)
for r in p1:
    key = (float(r["alpha"]), float(r["successor_capability"]), float(r["rr"]))
    celln[key] += 1
    fired[key] += truthy(r["yield_fired"])
p_pairs = {}
p_identical = p_faithful = True
for (a, c), (pub_min, pub_max) in P_TABLE.items():
    cells = sorted((rr, fired[(a, c, rr)], celln[(a, c, rr)]) for (aa, cc, rr) in celln if (aa, cc) == (a, c))
    counts = [k for _, k, _ in cells]
    ns = {n for _, _, n in cells}
    lo_k, hi_k = min(counts), max(counts)
    n = ns.pop()
    ident = (lo_k, hi_k) == (pub_min, pub_max)
    lo_ci, hi_ci = wilson(lo_k, n), wilson(hi_k, n)
    faith = lo_ci[0] <= pub_min / n <= lo_ci[1] and hi_ci[0] <= pub_max / n <= hi_ci[1]
    p_identical &= ident
    p_faithful &= faith
    p_pairs[f"alpha {a}, cap {c}"] = {"by_rr": {str(rr): k for rr, k, _ in cells}, "n_per_cell": n,
                                      "rerun_min_max": [lo_k, hi_k], "published_min_max": [pub_min, pub_max],
                                      "identical": ident, "faithful": faith,
                                      "wilson_lowest": lo_ci, "wilson_highest": hi_ci}
out["P"] = {"pairs": p_pairs, "machine": "YOTKOTEST",
            "verdict": "IDENTICAL" if p_identical else ("FAITHFUL" if p_faithful else "NOT FAITHFUL")}

# ---------------- T1: Part 2 Category A survival by rr ----------------
T1_COUNTS = [{2}, {11}, {13}, {35}, {58}, {147}, {414}, {729, 730}, {1038}]
T1_RATES = [0.002, 0.009, 0.011, 0.029, 0.048, 0.122, 0.345, 0.608, 0.865]
p2 = rows(PART2 / "phase_b_rerun_part2_runs.csv")
surv = defaultdict(int)
nrr = defaultdict(int)
for r in p2:
    rr = float(r["rr"])
    nrr[rr] += 1
    surv[rr] += truthy(r["survived"])
rrs = sorted(nrr)
t1 = []
inside = 0
for i, rr in enumerate(rrs):
    k, n = surv[rr], nrr[rr]
    ci = wilson(k, n)
    ok = ci[0] <= T1_RATES[i] <= ci[1]
    inside += ok
    t1.append({"rr": rr, "survived": k, "n": n, "published_rate": T1_RATES[i],
               "published_counts": sorted(T1_COUNTS[i]), "identical": k in T1_COUNTS[i],
               "wilson": ci, "published_inside_interval": ok})
monotone = all(surv[a] <= surv[b] for a, b in zip(rrs, rrs[1:]))
t1_ident = all(x["identical"] for x in t1) and len(rrs) == 9
out["T1"] = {"by_rr": t1, "points_inside": inside, "monotone_nondecreasing": monotone,
             "machine": "yotko-legion-t5-26iob6",
             "verdict": "IDENTICAL" if t1_ident else ("FAITHFUL" if inside >= 7 and monotone else "NOT FAITHFUL")}

# ---------------- T4: Part 3 Category C audit on minus off ----------------
p3 = rows(DIAG / "phase_b_rerun_part3_runs.csv")
by_state = {"True": [], "False": []}
match = defaultdict(dict)
for r in p3:
    s = truthy(r["survived"])
    by_state[r["cop_cost_audit"]].append(s)
    cell = (r["rr"], r["phi"], r["alpha"], r["successor_capability"], r["seed"])
    match[cell][r["cop_cost_audit"]] = (s, r["derived_seed"])
k_off, n_off = sum(by_state["False"]), len(by_state["False"])
k_on, n_on = sum(by_state["True"]), len(by_state["True"])
delta = k_on / n_on - k_off / n_off
se_pub = math.sqrt((k_on / n_on) * (1 - k_on / n_on) / n_on + (k_off / n_off) * (1 - k_off / n_off) / n_off)
diffs = [int(v["True"][0]) - int(v["False"][0]) for v in match.values() if len(v) == 2]
same_seed = sum(v["True"][1] == v["False"][1] for v in match.values() if len(v) == 2)
_, se_matched = paired_se(diffs)
PUB_DELTA = -0.0047
by_rr = {}
for rr in sorted({r["rr"] for r in p3}):
    on = [truthy(r["survived"]) for r in p3 if r["rr"] == rr and r["cop_cost_audit"] == "True"]
    off = [truthy(r["survived"]) for r in p3 if r["rr"] == rr and r["cop_cost_audit"] == "False"]
    by_rr[rr] = {"on": sum(on), "off": sum(off), "n_each": len(on), "delta_count": sum(on) - sum(off)}
t4_ident = (k_off in (1027, 1028, 1029) and k_on == k_off - 19 and n_off == n_on == 4050
            and [v["delta_count"] for v in by_rr.values()] == [-4, -5, -10])
faith_pub = abs(delta - PUB_DELTA) <= 2 * se_pub
faith_matched = abs(delta - PUB_DELTA) <= 2 * se_matched
out["T4"] = {"audit_off": [k_off, n_off], "audit_on": [k_on, n_on], "delta": delta,
             "published_delta": PUB_DELTA, "se_published_definition": se_pub,
             "se_seed_index_matched": se_matched, "pairs_with_identical_derived_seed": same_seed,
             "by_rr": by_rr, "machine": "YOTKOTEST",
             "faithful_under_published_se": faith_pub, "faithful_under_matched_se": faith_matched,
             "verdict": "IDENTICAL" if t4_ident else ("FAITHFUL" if faith_pub else "NOT FAITHFUL")}

# ---------------- R4: Part 4, R minus O at matched seeds ----------------
p4_path = DIAG / "phase_b_rerun_part4_runs.csv"
if p4_path.exists():
    p4 = rows(p4_path)
    o_index = {}
    for r in p2 + p3:
        o_index[(r["mode"], r["rr"], r["phi"], r["alpha"], r["successor_capability"], r["cop_cost_audit"], r["seed"])] = r
    groups = defaultdict(list)
    seed_mismatch = missing = 0
    for r in p4:
        key = (r["mode"], r["rr"], r["phi"], r["alpha"], r["successor_capability"], r["cop_cost_audit"], r["seed"])
        o = o_index.get(key)
        if o is None:
            missing += 1
            continue
        seed_mismatch += o["derived_seed"] != r["derived_seed"]
        g = (r["mode"], r["rr"]) if r["mode"] == "A" else (r["mode"], "audit " + r["cop_cost_audit"])
        groups[g].append(int(truthy(r["survived"])) - int(truthy(o["survived"])))
    r4 = {}
    for g, d in sorted(groups.items()):
        mean, se = paired_se(d)
        r4[" ".join(g)] = {"pairs": len(d), "R_minus_O_rate": mean, "paired_se": se,
                           "R_only_survived": d.count(1), "O_only_survived": d.count(-1)}
    out["R4"] = {"groups": r4, "unmatched_rows": missing, "derived_seed_mismatches": seed_mismatch,
                 "note": "Combined effect of every model change since June 8, including the v2.1 estimator "
                         "repair; not the repair's effect alone. Category A pairs cross machines "
                         "(O on the box, R on YOTKOTEST) and include that machine difference."}
else:
    out["R4"] = "Part 4 not yet merged"

# ---------------- R5: liveness and provenance ----------------
prov = defaultdict(set)
errs = 0
for name, rs in (("part1", p1), ("part2", p2), ("part3", p3)) + ((("part4", p4),) if p4_path.exists() else ()):
    for r in rs:
        prov[name].add((r["interpreter_version"].split()[0], r["numpy_version"], r["machine_label"]))
        errs += bool(r["error"])
out["R5"] = {"interpreter_numpy_machine": {k: sorted(v) for k, v in prov.items()}, "error_rows": errs}

OUT.write_text(json.dumps(out, indent=1, default=str))
for t in ("P", "T1", "T4"):
    print(t, out[t]["verdict"])
print("P pairs:", {k: (v["rerun_min_max"], v["published_min_max"]) for k, v in p_pairs.items()})
print("T1:", [(x["rr"], x["survived"], sorted(x["published_counts"])) for x in t1], "inside", inside, "monotone", monotone)
print("T4: off", k_off, "on", k_on, "delta %.4f" % delta, "se_pub %.4f se_matched %.4f" % (se_pub, se_matched),
      "by_rr", {k: v["delta_count"] for k, v in by_rr.items()}, "same derived seed pairs", same_seed)
print("R5:", out["R5"])
