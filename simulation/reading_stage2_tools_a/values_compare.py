"""D:551-556, A6.7: exact canonical values, never display a value."""
import json
import sys
from pathlib import Path
from v3.artifacts import canonical
def compare(a,b):
    a=json.loads(Path(a).read_bytes()); b=json.loads(Path(b).read_bytes())
    if set(a)!={'schema','component','values'} or set(b)!={'schema','component','values'}: return ['schema']
    if a.get("schema")!=b.get("schema") or a.get("schema")!="a10-stage2-values-1": return ["schema"]
    if a.get("component")!=b.get("component"): return ["component"]
    av=a["values"]; bv=b["values"]
    return sorted(k for k in av.keys()|bv.keys() if k not in av or k not in bv or canonical(av[k])!=canonical(bv[k]))
def main():
    changed=compare(*sys.argv[1:3])
    print(str(len(changed))+"\n"+"\n".join(changed) if changed else "identical")
    return bool(changed)
if __name__=="__main__":
    try: status=main()
    except BaseException: status=2
    sys.exit(status)
