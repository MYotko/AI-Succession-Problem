"""Stage 2 helpers on top of the copied stage 1 ``common`` module: the input
ledger with change detection (D:275), write-once output (D:474, A6.4a), the
ladder's value mapping (A6.4a) and the reader identity (D:529).
"""
import hashlib
import math
import os
from pathlib import Path

from .common import Refused, canonical, digest, file_hash, lf_hash, loads, require, seal

PACKAGE = Path(__file__).resolve().parent
ROLE = "B"
HEX = frozenset("0123456789abcdef")
# Output folders this process created, so that a refusal record is written only
# into a new folder or into one of these (A10.3c).
CREATED = set()


def is_hash(value):
    return isinstance(value, str) and len(value) == 64 and set(value) <= HEX


def reader_identity():
    """D:529: a sha256 over the package's ``*.py`` files with their names.

    Definition: ``digest({<file name relative to the package directory>:
    sha256(file bytes with CRLF normalized to LF)})`` over every ``*.py`` file
    directly in the package directory, where ``digest`` is the sha256 of the
    canonical JSON. Names are relative to the package directory, so the identity
    does not change when the package directory is renamed at commit (D:680)."""
    files = {p.name: lf_hash(p) for p in sorted(PACKAGE.glob("*.py"))}
    return {"files": files, "sha256": digest(files), "role": ROLE}


def norm(value):
    """A6.4a: before ``canonical``, every float infinity becomes "+inf" or
    "-inf" and every NaN becomes "nan". NumPy values become Python values and
    float dictionary keys become ``repr`` strings."""
    if value is None or isinstance(value, (bool, str)):
        return value
    if hasattr(value, "tolist") and not isinstance(value, (list, tuple, dict)):
        return norm(value.tolist())
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        if math.isnan(value):
            return "nan"
        if math.isinf(value):
            return "+inf" if value > 0 else "-inf"
        return value
    if isinstance(value, dict):
        return {(k if isinstance(k, str) else repr(norm_key(k))): norm(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [norm(v) for v in value]
    raise Refused("unserializable value")


def norm_key(key):
    if hasattr(key, "item"):
        key = key.item()
    require(type(key) in (int, float), "key_number")
    return key


def fkey(value):
    """``repr`` of a grid float, the key convention of D:503."""
    if hasattr(value, "item"):
        value = value.item()
    require(type(value) is float, "key_number")
    return repr(value)


class Ledger:
    """Every file read is recorded with sha256 and byte count on first read and
    re-hashed after computation and before any output is written (D:275)."""

    def __init__(self, expected=None):
        self.entries = {}
        self.expected = expected or {}

    def read(self, path, label):
        try:
            raw = Path(path).read_bytes()
        except OSError:
            raise Refused("input_missing") from None
        sha = hashlib.sha256(raw).hexdigest()
        prior = self.entries.get(label)
        if prior is None:
            self.entries[label] = {"path": str(path), "sha256": sha, "bytes": len(raw), "producers": {}}
        else:
            require(prior["sha256"] == sha and prior["path"] == str(path), "input changed during reading")
        bound = self.expected.get(label)
        require(bound is None or (bound["sha256"] == sha and bound["bytes"] == len(raw)),
                "file differs from the sealed collection")
        return raw, sha

    def json(self, path, label):
        raw, sha = self.read(path, label)
        return loads(raw), sha

    def producer(self, label, field, value):
        self.entries[label]["producers"][field] = value

    def verify(self):
        for entry in self.entries.values():
            try:
                same = file_hash(entry["path"]) == entry["sha256"] and os.path.getsize(entry["path"]) == entry["bytes"]
            except OSError:
                same = False
            require(same, "input changed during reading")

    def record(self):
        return {label: {"sha256": e["sha256"], "bytes": e["bytes"], "producers": dict(sorted(e["producers"].items()))}
                for label, e in sorted(self.entries.items())}


def sealed(document, label):
    """A sealed document's payload; the seal is verified."""
    require(isinstance(document, dict) and set(document) == {"payload", "sha256"}, label)
    require(digest(document["payload"]) == document["sha256"], label)
    return document["payload"]


def write_once(path, data):
    """D:474 and A6.4a: written once, under a temporary name, fsynced and
    renamed into place; an existing file is never replaced."""
    path = Path(path)
    require(not path.exists(), "output file exists")
    temporary = path.with_name(path.name + ".%d.partial" % os.getpid())
    with temporary.open("xb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)
    descriptor = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    return hashlib.sha256(data).hexdigest()


def document_bytes(value):
    return canonical(value) + b"\n"


def sealed_bytes(payload):
    return document_bytes(seal(payload))
