"""Blind comparison of two builds' ``values.json`` (D:551-556, A6.7).

Usage: python -B values_compare.py <first> <second>

With two ``values.json`` files: requires the same schema and component and
prints ``identical``, or the count and the names of the differing keys. A key
present on one side only is a differing key (A6.7: no build writes an extra
key, in either mode). It never prints a value. Key names carry no outcome.

With two component folders: the same for their ``values.json``, then the two
hash-only comparisons of D:554, one line each: ``contributing_runs.quantities:
identical`` or ``differs``, and ``incidence_per_run.json: identical`` or
``differs``.

Carried over from the stage 1 reader's ``compare.py`` with the schema changed.
Standard library and ``v3.artifacts`` only; run from ``simulation/``.
"""
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # simulation/, for v3.artifacts

SCHEMA = "a10-stage2-values-1"


def canonical(value):
    from v3.artifacts import canonical as native
    return native(value)


def _pairs(items):
    result = {}
    for key, value in items:
        if key in result:
            raise ValueError("duplicate key")
        result[key] = value
    return result


def _nonfinite(_):
    raise ValueError("non-finite number")


def load(path):
    return json.loads(Path(path).read_bytes(), object_pairs_hook=_pairs, parse_constant=_nonfinite)


def compare(first, second):
    a, b = load(first), load(second)
    if not (a.get("schema") == b.get("schema") == SCHEMA) or a.get("component") != b.get("component") \
            or a.get("component") not in ("A10", "A6") or set(a) != {"schema", "component", "values"} or set(b) != set(a):
        raise ValueError("schema or component")
    a, b = a["values"], b["values"]
    return [k for k in sorted(set(a) | set(b)) if k not in a or k not in b or canonical(a[k]) != canonical(b[k])]


def hash_only(first, second):
    lines = []
    a, b = load(Path(first) / "contributing_runs.json"), load(Path(second) / "contributing_runs.json")
    same = canonical(a["payload"]["quantities"]) == canonical(b["payload"]["quantities"])
    lines.append("contributing_runs.quantities: " + ("identical" if same else "differs"))
    digests = [hashlib.sha256((Path(p) / "incidence_per_run.json").read_bytes()).hexdigest() for p in (first, second)]
    lines.append("incidence_per_run.json: " + ("identical" if digests[0] == digests[1] else "differs"))
    return lines, same and digests[0] == digests[1]


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 2:
        print("usage")
        return 2
    try:
        folders = Path(argv[0]).is_dir() and Path(argv[1]).is_dir()
        keys = compare(*(str(Path(p) / "values.json") if folders else p for p in argv))
        lines = ["%d differing keys" % len(keys)] + keys if keys else ["identical"]
        equal = not keys
        if folders:
            more, same = hash_only(argv[0], argv[1])
            lines += more
            equal = equal and same
        print("\n".join(lines))
        return int(not equal)
    except Exception:  # noqa: BLE001 - never print input content
        print("REFUSED: comparison")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
