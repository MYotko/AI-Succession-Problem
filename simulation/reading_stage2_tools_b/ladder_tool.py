"""The stage hash ladder tool (A6.4a, A8.7).

Usage: python -B ladder_tool.py <first LADDER.json> <second LADDER.json>

Walks the rung classes in pipeline order, ``key`` first, then ``records``,
``cells``, ``result``, ``incidence``, with names in sorted order within each
class. Prints only ``identical``, or the name of the first diverging rung. A
rung present on one side only diverges. When the two ladders' keys differ the
first diverging rung is ``key/check``, never ``records/<first>`` (A8.7). Rung
values are never printed. Standard library and ``v3.artifacts`` only; run from
``simulation/``.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # simulation/, for v3.artifacts

SCHEMA = "a10-stage2-ladder-1"
CLASSES = ("key", "records", "cells", "result", "incidence")


def _pairs(items):
    result = {}
    for key, value in items:
        if key in result:
            raise ValueError("duplicate key")
        result[key] = value
    return result


def load(path):
    from v3.artifacts import canonical, unseal
    raw = Path(path).read_bytes()
    document = json.loads(raw, object_pairs_hook=_pairs)
    payload = unseal(document)
    if raw != canonical(document) + b"\n" or set(payload) != {"schema", "component", "rungs"} \
            or payload["schema"] != SCHEMA or payload["component"] not in ("A10", "A6"):
        raise ValueError("ladder form")
    rungs = payload["rungs"]
    if not isinstance(rungs, dict) or "key/check" not in rungs:
        raise ValueError("ladder form")
    for name, value in rungs.items():
        if name.split("/", 1)[0] not in CLASSES or "/" not in name or not isinstance(value, str) or len(value) != 64 \
                or set(value) - set("0123456789abcdef"):
            raise ValueError("ladder form")
    return payload


def walk(first, second):
    """The first diverging rung's name in walk order, or ``None``."""
    a, b = load(first), load(second)
    if a["component"] != b["component"]:
        raise ValueError("component")
    a, b = a["rungs"], b["rungs"]
    for rung_class in CLASSES:
        for name in sorted(n for n in set(a) | set(b) if n.split("/", 1)[0] == rung_class):
            if a.get(name) != b.get(name):
                return name
    return None


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 2:
        print("usage")
        return 2
    try:
        name = walk(argv[0], argv[1])
    except Exception:  # noqa: BLE001 - never print input content
        print("REFUSED: ladder")
        return 2
    print("identical" if name is None else name)
    return int(name is not None)


if __name__ == "__main__":
    raise SystemExit(main())
