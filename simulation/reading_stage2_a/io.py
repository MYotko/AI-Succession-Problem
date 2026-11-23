"""Hash the exact bytes parsed, retain labels rather than machine paths."""
import hashlib
from pathlib import Path
from .common import require,loads,unseal,file_hash
class Ledger:
    def __init__(self):
        self.paths={}; self.entries={}; self.producers={}
    def raw(self,path,label,expected=None):
        p=Path(path).resolve(); raw=p.read_bytes(); sha=hashlib.sha256(raw).hexdigest()
        require(expected is None or sha==expected, "input hash")
        entry=dict(sha256=sha,bytes=len(raw))
        require(label not in self.entries or self.entries[label]==entry, "input changed while reading")
        self.paths[label]=p; self.entries[label]=entry
        return raw
    def load(self,path,label,expected=None,sealed=False):
        doc=loads(self.raw(path,label,expected))
        value=unseal(doc) if sealed else doc
        self.record_producers(label,doc)
        return value
    def record_producers(self,label,doc):
        """A10.6: a fixed field list, never a recursive key-name search."""
        if not isinstance(doc,dict):return
        payload=doc.get('payload',doc)
        paths=[]
        if label.endswith(('/spec','/record','/output','/family/identity','/family/labels','/calibration')):paths=[('code_hash',)]
        elif label.endswith('/family/table'):paths=[('code_hash',),('manifest','a10','producer_code_hash')]
        elif label.endswith('/family/validation_receipt'):paths=[('producer_code_hash',)]
        elif label.endswith('/family/a10_receipt'):paths=[('producer_code_hash',),('validation_receipt','payload','producer_code_hash')]
        for path in paths:
            value=payload
            for key in path:
                if not isinstance(value,dict) or key not in value:break
                value=value[key]
            else:
                require(isinstance(value,str),'unaccepted producer')
                self.producers.setdefault(label,{})['/'.join(path)]=value
    def verify_producers(self,accepted):
        # A10.6: exact calibration pins and native validation govern those files.
        require(all(v in accepted for label,fields in self.producers.items() if not label.endswith('/calibration') for v in fields.values()), "unaccepted producer")
    def hash(self,label): return self.entries[label]["sha256"]
    def verify(self):
        for label,path in self.paths.items():
            require(file_hash(path)==self.entries[label]["sha256"], "input changed")
    def bound(self,path,label,entry):
        require(isinstance(entry,dict) and entry.get("present",True) is True, "inventory file absent")
        doc=self.load(path,label,entry["sha256"])
        if entry.get("seal") is not None:
            unseal(doc); require(doc["sha256"]==entry["seal"], "inventory seal")
        return doc
