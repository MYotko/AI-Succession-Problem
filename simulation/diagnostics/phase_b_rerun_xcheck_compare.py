"""Compare all 30 original fields in two non-registered crosscheck outputs."""
import sys
sys.dont_write_bytecode=True
import argparse
from pathlib import Path
import struct
from phase_b_rerun_common import *
HERE=Path(__file__).resolve().parent

def equal_value(a,b):
    if type(a) is not type(b):
        return False
    if type(a) is float:
        return struct.pack("!d",a)==struct.pack("!d",b)
    return a==b

def compare(left,right):
    verify_keys=("executor_hashes","bytecode_sha256")
    for key in verify_keys:
        if left["identity"][key]!=right["identity"][key]:
            raise ValueError("Crosscheck identity mismatch: "+key)
    def keyed(data):
        if len(data["rows"])!=16 or len(data["tasks"])!=16 or not data["non_registered"]:
            raise ValueError("Crosscheck requires exactly 16 non-registered tasks")
        result={}
        for entry,row in zip(data["tasks"],data["rows"]):
            if entry["task"]["seed"] not in (150,151) or list(row)!=FIELDS+EXTRA:
                raise ValueError("Invalid crosscheck row")
            key=canonical({"arm":entry["arm"],"task":entry["task"]})
            if key in result:
                raise ValueError("Duplicate crosscheck task")
            result[key]=row
        return result
    a=keyed(left); b=keyed(right)
    if a.keys()!=b.keys():
        raise ValueError("Crosscheck task sets differ")
    differences=[]
    for key in sorted(a):
        for field in FIELDS:
            if not equal_value(a[key][field],b[key][field]):
                differences.append({"task":json.loads(key),"field":field,"left":a[key][field],"right":b[key][field]})
    return {"result":"DIFFERENT" if differences else "IDENTICAL",
            "machine_labels":[left["machine_label"],right["machine_label"]],
            "executor_hashes":left["identity"]["executor_hashes"],
            "bytecode_sha256":left["identity"]["bytecode_sha256"],
            "environments":{left["machine_label"]:left["identity"]["versions"],right["machine_label"]:right["identity"]["versions"]},
            "task_count":16,"differences":differences,"created_utc":utc(),"test_fixture":False}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("left"); p.add_argument("right")
    p.add_argument("--out",default=None)
    args=p.parse_args()
    install_guard(HERE)
    left=read_json(args.left); right=read_json(args.right)
    result=compare(left,right)
    name="phase_b_rerun_xcheck_result_"+digest(canonical(result["machine_labels"]).encode())[:12]+".json"
    output=Path(args.out) if args.out else HERE/name
    if not output.name.startswith(("phase_b_rerun_xcheck_result_","phase_b_rerun_smoke_")):
        raise ValueError("Invalid comparison output prefix")
    save(output,result)
    print(result["result"])
    for d in result["differences"]:
        print(canonical(d))
if __name__=="__main__":
    main()
