"""A2 exception for the A1 producer, with unchanged scientific semantics.

The reviewed record is source-controlled and part of code_identity. No
table values, row statuses, coverage or sensitivity checks are changed.
"""
from .artifacts import ROOT, SIMULATION, read, digest
from .calibration_compatibility import dependency_hash


def verified_record():
    record = read(ROOT / "table_compatibility_A2.json")
    for name, expected in {**record["unchanged_dependency_sha256"], **record["approved_boundary_sha256"]}.items():
        if dependency_hash(SIMULATION / name) != expected:
            raise ValueError(f"A2 table compatibility dependency changed: {name}")
    return record


def compatible(document, file_sha256=None):
    record = verified_record()
    p = document["payload"]
    return (document.get("sha256") == record["table_seal_sha256"] and
            digest(p) == record["table_seal_sha256"] and
            file_sha256 == record["table_file_sha256"] and
            p["code_hash"] == record["producer_code_hash"] and
            p["manifest"]["calibration_hash"] == record["calibration_sha256"] and
            digest(p["manifest"].get("design")) == record["table_design_sha256"])
