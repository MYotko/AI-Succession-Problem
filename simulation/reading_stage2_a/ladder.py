"""A6.4a and A8.7 structures; the key never leaves memory."""
import hashlib
import hmac
from v3.artifacts import canonical
from .common import safe

CHECK={"check":"a10-stage2-ladder-1 key check"}
def rung(key, structure):
    return hmac.new(key,canonical(safe(structure)),hashlib.sha256).hexdigest()
def cell_structure(arm,comparator):
    return {"arm":{repr(float(k)):safe(v.tolist() if hasattr(v,"tolist") else v) for k,v in arm.items()},
            "comparator":{repr(float(k)):safe(v.tolist() if hasattr(v,"tolist") else v) for k,v in comparator.items()}}
