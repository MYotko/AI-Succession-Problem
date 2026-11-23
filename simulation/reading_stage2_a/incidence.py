"""D 4.3-4.5. No missing accumulator is treated as measured zero."""
from collections import Counter
from v3.admission_a13 import pooled_incidence
from .common import require,digest
BRANCHES=("ordinary_allocation","survival_first","yield_review")
COUNTS=("excluded_by_reason","balanced_fallbacks_by_reason","survival_first_unavailable_selections_by_reason")
REASON="A13 accumulator absent: `admission_a13.enabled` is false for an empty admitted-row set"
STATEMENT="An unflagged quantity is not certified unaffected."

def derive(result):
    try:
        steps=result["diagnostics"]; events=result["yield_events"]
        require(isinstance(steps,list) and isinstance(events,list), "incidence denominators not derivable")
        require(all(type(s["allocation_evaluated"]) is bool and type(s["survival_first"]) is bool for s in steps), "incidence denominators not derivable")
        times={s["time"]:s for s in steps}
        et=[e["time"] for e in events]
        require(len(set(et))==len(et) and all(type(t) is int and t%10==0 and t in times and times[t]["allocation_evaluated"] is True for t in et), "incidence denominators not derivable")
        counts=dict(ordinary_allocation=sum(s["allocation_evaluated"] and not s["survival_first"] for s in steps),
                    survival_first=sum(s["allocation_evaluated"] and s["survival_first"] for s in steps),yield_review=len(events))
        total=result["continuation_availability"]["allocation_steps"]
        require(type(total) is int and total==counts["ordinary_allocation"]+counts["survival_first"], "incidence denominators not derivable")
        return counts
    except (KeyError,TypeError,ValueError) as exc:
        from .common import Refusal
        if isinstance(exc,Refusal): raise
        raise Refusal("incidence denominators not derivable") from None

def normalize(result, admitted):
    if admitted:
        require("a13_decision_incidence" in result, "a13 incidence missing on admitted family")
    else:
        require("a13_decision_incidence" not in result, "incidence contradicts empty admitted set")
        require(not any("missing_or_not_estimable_row" in s.get("unavailable_rules",{}).values() for s in result["diagnostics"]),
                "missing row contradicts empty admitted set")
    d=derive(result)
    if not admitted:
        return {b:dict(numerator=0,denominator=d[b],rate=0.0 if d[b] else None,assessed=bool(d[b]),
                       provenance=dict(numerator="structural_zero_from_verified_family",denominator="derived_from_recorded_decisions")) for b in BRANCHES}
    record=result["a13_decision_incidence"]
    require(isinstance(record,dict) and set(record)==set(BRANCHES), "incidence branch set")
    for b in BRANCHES:
        r=record[b]; n=r["numerator"]; den=r["denominator"]
        require(type(n) is int and type(den) is int and 0<=n<=den, "incidence counts")
        require((type(r['rate']) is float if den else r['rate'] is None) and r["rate"]==(n/den if den else None) and type(r["assessed"]) is bool and r["assessed"] is bool(den), "incidence rate")
        require(d[b]==den, "incidence denominator self check")
        for c in COUNTS:
            require(isinstance(r[c],dict) and all(isinstance(k,str) and type(v) is int and v>=0 for k,v in r[c].items()), "incidence separate counts")
    return record

def summarize(members, records, family_of, families):
    m={k:records[k]["incidence"] for k in members}
    pooled=pooled_incidence([m[k] for k in members])
    values=dict(flag=pooled["affected_by_table_unavailability"],
                branches={b:{f:pooled["branches"][b][f] for f in ("numerator","denominator","rate")} for b in BRANCHES}, per_run_sha256=per_run_digest(members,records))
    coverage={}
    for name in sorted({family_of[k] for k in members}):
        f=families[name]; keys=[k for k in members if family_of[k]==name]
        coverage[name]=dict(status=f["status"],runs=len(keys),table_sha256=f["hashes"]["table"],receipt_sha256=f["hashes"]["a10_receipt"])
    status=dict(branches={b:"assessed" if pooled["branches"][b]["denominator"] else "unassessed" for b in BRANCHES},families=coverage)
    counts=separate_counts(members,records)
    return values,status,counts,pooled

def separate_counts(members,records):
    """A10.1: recorded zero is distinct from absent reason counters."""
    m={k:records[k]['incidence'] for k in members}
    selected=[k for k in members if records[k]["status"]=="recorded"]
    counts=dict(recorded_runs=len(selected),not_recorded_runs=len(members)-len(selected),branches={})
    for b in BRANCHES:
        counts["branches"][b]={}
        for c in COUNTS:
            total=Counter()
            for k in selected: total.update(m[k][b][c])
            counts["branches"][b][c]=dict(sorted(total.items())) if selected else 'not recorded'
    return counts

def per_run_payload(members,records):
    """A10.2: only the record and status are serialized per run."""
    return dict(schema='a10-stage2-incidence-per-run-1',runs={k:dict(record=records[k]['incidence'],status=records[k]['status']) for k in sorted(members)})

def per_run_digest(members,records):
    return digest({k:records[k]['incidence'] for k in members})
