"""Strict JSON, identities, and read-only input accounting."""
import hashlib
import json
import math
import os
from pathlib import Path
import tempfile
from v3.artifacts import canonical as native_canonical, seal as native_seal


class Refusal(ValueError):
    pass


def require(condition, label):
    if not condition:
        raise Refusal(label)


def canonical(obj):
    return native_canonical(obj)


def digest(obj):
    return hashlib.sha256(canonical(obj)).hexdigest()


def file_hash(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1048576), b""):
            h.update(block)
    return h.hexdigest()


def seal(payload):
    return native_seal(payload)


def unseal(doc):
    require(isinstance(doc, dict) and set(doc) == {"payload", "sha256"}, "seal envelope")
    require(digest(doc["payload"]) == doc["sha256"], "seal digest")
    return doc["payload"]


def _pairs(items):
    result = {}
    for key, value in items:
        require(key not in result, "duplicate JSON key")
        result[key] = value
    return result


def loads(raw):
    def bad(value):
        raise Refusal("nonfinite JSON input")
    def number(value):
        result = float(value)
        require(math.isfinite(result), "nonfinite JSON input")
        return result
    return json.loads(raw, object_pairs_hook=_pairs, parse_constant=bad, parse_float=number)


def read(path):
    return loads(Path(path).read_bytes())


def safe(obj):
    if isinstance(obj, float) and not math.isfinite(obj):
        if math.isnan(obj):
            return "nan"
        return "+inf" if obj > 0 else "-inf"
    if isinstance(obj, dict):
        return {repr(k) if isinstance(k, float) else str(k): safe(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [safe(v) for v in obj]
    if hasattr(obj, "item"):
        return safe(obj.item())
    return obj


def write(path, value, *, preserve_on_failure=False):
    """Atomic JSON write; existing targets are never replaced."""
    write_bytes(path, canonical(safe(value)) + b"\n", preserve_on_failure=preserve_on_failure)


def write_bytes(path, data, *, preserve_on_failure=False):
    """Publish prepared bytes, retaining publication debris when A11.1 requires it."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise Refusal("output target exists")
    fd, name = tempfile.mkstemp(prefix=".a10-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.rename(name, path)
    finally:
        if not preserve_on_failure and os.path.exists(name):
            os.unlink(name)


def identity(role="A"):
    root = Path(__file__).parent
    # Whole package is the analysis identity; role is separately bound. Tests and
    # documentation do not execute in a reading and are excluded explicitly.
    files = {p.relative_to(root).as_posix(): file_hash(p) for p in sorted(root.rglob("*.py"))}
    return {"role": role, "sha256": digest({"role": role, "files": files}), "files": files}


