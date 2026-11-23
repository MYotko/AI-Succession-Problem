"""A8.7 class order. Print only the first name, never a rung value."""
import json
import sys
from pathlib import Path
from v3.artifacts import unseal
ORDER=("key","records","cells","result","incidence")
def compare(a,b):
    a=unseal(json.loads(Path(a).read_bytes())); b=unseal(json.loads(Path(b).read_bytes()))
    if a["schema"]!="a10-stage2-ladder-1" or a["schema"]!=b["schema"]: return "schema"
    if a["component"]!=b["component"]: return "component"
    ar=a["rungs"]; br=b["rungs"]
    for kind in ORDER:
        for key in sorted(k for k in ar.keys()|br.keys() if k.startswith(kind+"/")):
            if ar.get(key)!=br.get(key): return key
    return "identical"
if __name__=="__main__":
    try: print(compare(*sys.argv[1:3]))
    except BaseException: sys.exit(2)
