"""D:547-549, A6.4a and A10.3d: component or collection bytes."""
import hashlib
import sys
from pathlib import Path
FILES=("reading.json","values.json","contributing_runs.json","incidence_per_run.json","LADDER.json","SEAL.json")
def compare(a,b):
    changed=[]
    names=('inputs.json','collection.json') if any((Path(root)/name).exists() for root in (a,b) for name in ('inputs.json','collection.json')) else FILES
    for name in names:
        pa=Path(a)/name; pb=Path(b)/name
        if not pa.is_file() or not pb.is_file() or hashlib.file_digest(pa.open("rb"),"sha256").digest()!=hashlib.file_digest(pb.open("rb"),"sha256").digest(): changed.append(name)
    return changed
def main():
    changed=compare(*sys.argv[1:3])
    print("\n".join(changed) if changed else "identical")
    return bool(changed)
if __name__=="__main__":
    try: status=main()
    except BaseException: status=2
    sys.exit(status)
