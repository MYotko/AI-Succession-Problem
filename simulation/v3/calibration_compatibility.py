"""A1: preserve one frozen calibration across estimator-only changes.

This does not migrate values or relax arbitrary source checks. The exact
historical artifact, source identity and unchanged calibration dependency
implementation must all match the reviewed compatibility record.
"""
import inspect
import hashlib
from .artifacts import ROOT, SIMULATION, read, file_hash, digest


def function_hash(function):
    text = inspect.getsource(function).replace("\r\n", "\n")
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def dependency_hash(path):
    # Git checkouts may convert LF to CRLF. Python parses both as LF.
    # Only this newline conversion is allowed; every other byte is bound.
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def compatible(document):
    from . import calibration
    path = ROOT / "calibration_compatibility_A1.json"
    if not path.exists():
        return False
    record = read(path)
    p = document["payload"]
    if (document["sha256"] != record["calibration_sha256"] or p["code_hash"] != record["old_code_hash"]
            or digest(p["values"]) != record["values_sha256"]):
        return False
    if any(dependency_hash(SIMULATION / name) != value for name, value in record["dependency_sha256"].items()):
        return False
    return all(function_hash(getattr(calibration, name)) == value for name, value in record["function_sha256"].items())
