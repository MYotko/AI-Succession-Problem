"""Shared helpers: refusals, strict JSON, hashing, the hash envelope and writes.

Refusals carry a static label only, never input content. Every artifact this
reader writes uses the repository's canonical JSON (``v3.artifacts.canonical``
semantics) and its hash envelope ``{"payload": ..., "sha256": ...}``, but is
written by this package's own writer, so nothing is ever written under
``simulation/v3`` or into an input.
"""
import hashlib
import json
import math
import os
from pathlib import Path
from contextvars import ContextVar

COMPUTATION_STARTED = ContextVar("reading_a10_computation_started", default=False)


class Refused(ValueError):
    """A refusal. The message is a fixed label, never input content."""
    def __init__(self, label):
        super().__init__(label)
        self.reason_class = "after_computation_started" if COMPUTATION_STARTED.get() else "input_verification"


def require(condition, label):
    if not condition:
        raise Refused(label)


def canonical(value):
    # Identical to v3.artifacts.canonical; kept local so that writing never
    # depends on the instrument's scoped writer.
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False).encode("utf-8")


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def seal(payload):
    return {"payload": payload, "sha256": digest(payload)}


def unseal(document, label="seal"):
    require(isinstance(document, dict) and set(document) == {"payload", "sha256"}, label)
    require(digest(document["payload"]) == document["sha256"], label)
    return document["payload"]


def file_hash(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def lf_hash(path):
    """SHA256 after CRLF-to-LF normalization, the source-manifest convention."""
    return hashlib.sha256(Path(path).read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def _pairs(items):
    result = {}
    for key, value in items:
        require(key not in result, "json_duplicate_key")
        result[key] = value
    return result


def _nonfinite(_):
    raise Refused("json_nonfinite")


def loads(raw):
    try:
        return json.loads(raw, object_pairs_hook=_pairs, parse_constant=_nonfinite)
    except Refused:
        raise
    except (ValueError, TypeError, UnicodeDecodeError):
        raise Refused("json_malformed") from None


def read_json(path, expected_sha256=None, label="file_hash"):
    """Strict JSON read; returns (value, sha256 of the exact bytes)."""
    try:
        raw = Path(path).read_bytes()
    except OSError:
        raise Refused("input_missing") from None
    sha = hashlib.sha256(raw).hexdigest()
    require(expected_sha256 is None or sha == expected_sha256, label)
    return loads(raw), sha


def integer(value, minimum=0):
    return type(value) is int and value >= minimum


def finite(value):
    return type(value) in (int, float) and math.isfinite(value)


def json_safe(value):
    """Infinities become the strings "-inf" and "+inf"; NaN is a refusal."""
    if type(value) is float and not math.isfinite(value):
        require(not math.isnan(value), "nan_result")
        return "+inf" if value > 0 else "-inf"
    if isinstance(value, dict):
        return {str(k): json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(v) for v in value]
    if hasattr(value, "item") and not isinstance(value, (str, bytes)):  # NumPy scalar
        return json_safe(value.item())
    return value


def number_key(value):
    """Python repr of a grid value, as the values-file key convention requires."""
    require(type(value) in (int, float), "key_number")
    return repr(float(value)) if type(value) is float else repr(value)


def write_bytes_atomic(path, data):
    path = Path(path)
    temporary = path.with_name(path.name + ".%d.partial" % os.getpid())
    with temporary.open("wb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)


def write_json(path, value):
    write_bytes_atomic(path, canonical(value) + b"\n")
