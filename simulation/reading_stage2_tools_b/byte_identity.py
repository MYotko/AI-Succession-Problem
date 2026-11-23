"""Byte identity of two folders (D:547-549, A6.4a, A10.3d).

Usage: python -B byte_identity.py <folder A> <folder B>

Reads only file bytes. Prints ``identical``, or the names of the files whose
sha256 differ, one per line. The compared set is every file directly in either
folder. A file on one side only is named as differing.

Its two uses: the six files of a component folder (reading.json, values.json,
contributing_runs.json, incidence_per_run.json, LADDER.json, SEAL.json) from
two runs of one build; and the two files of the two collection folders of
A10.3d (inputs.json, collection.json). A path that is not a readable folder, or
two folders with no file between them, prints ``not comparable``. Standard
library only.
"""
import hashlib
import os
import sys

COMPONENT_FILES = ("reading.json", "values.json", "contributing_runs.json", "incidence_per_run.json", "LADDER.json", "SEAL.json")
COLLECTION_FILES = ("inputs.json", "collection.json")


def sha256(path):
    h = hashlib.sha256()
    try:
        with open(path, "rb") as stream:
            for block in iter(lambda: stream.read(1 << 20), b""):
                h.update(block)
    except OSError:
        return None
    return h.hexdigest()


def names_of(folder):
    with os.scandir(folder) as entries:
        return {entry.name for entry in entries}


def differing(first, second):
    """The differing names, sorted; ``None`` when the two are not comparable."""
    try:
        names = names_of(first) | names_of(second)
    except OSError:
        return None
    if not names:
        return None
    result = []
    for name in sorted(names):
        a, b = sha256(os.path.join(first, name)), sha256(os.path.join(second, name))
        if a is None or b is None or a != b:
            result.append(name)
    return result


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 2:
        print("usage")
        return 2
    names = differing(argv[0], argv[1])
    if names is None:
        print("not comparable")
        return 2
    print("\n".join(names) if names else "identical")
    return int(bool(names))


if __name__ == "__main__":
    raise SystemExit(main())
