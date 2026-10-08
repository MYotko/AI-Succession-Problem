"""Canonical frozen tables and strict context-aware online loading."""
from pathlib import Path
from dataclasses import dataclass
import tempfile
import math
import numpy as np
from .artifacts import atomic_json, read, seal, unseal, digest, code_identity, file_hash
from .tables import Lookup


@dataclass(frozen=True)
class AvailableLookup(Lookup):
    available: np.ndarray
    unavailable_reasons: tuple


def row_key(row):
    scoring = row["scoring"]
    extra = {}
    if scoring.get("mapping") == "A10":
        from .instrument import Instrument
        inst = Instrument("A10", scoring["k_star"], scoring["g"])
        inst.require_capability(scoring["capability"])
        extra = {"instrument": inst.declaration()}
    elif scoring.get("mapping", "R4") != "R4":
        raise ValueError("undeclared table mapping")
    return digest({"rule": row["rule_id"], "kernel": row["kernel_hash"], "calibration": row["calibration_hash"],
                   "initial_population": row.get("initial_population", 200),
                   # The declared rational capability grid has fewer than
                   # twelve decimal places. Canonicalize binary products
                   # such as 1.2 * 1.5 before identifying a frozen context.
                   "alpha": float(scoring["alpha"]), "capability": round(float(scoring["capability"]), 12), "kappa": float(scoring.get("kappa", 8)), **extra})


def write_tables(path, rows, manifest, *, fixture=False):
    from .offline_estimator import add_ranking_flags
    rows = add_ranking_flags(list(rows))
    keys = [row_key(r) for r in rows]
    if len(set(keys)) != len(keys):
        raise ValueError("duplicate table row")
    required = manifest.get("required_row_keys", [])
    if set(required) != set(keys):
        raise ValueError("table manifest must enumerate every row, including failed rows")
    documents = {key: seal(row) for key, row in sorted(zip(keys, rows))}
    payload = {"schema": "v3-tables-1", "fixture": fixture, "code_hash": code_identity(),
               "manifest": manifest, "manifest_hash": digest(manifest), "rows": documents}
    document = seal(payload)
    path = Path(path)
    if path.exists() and read(path) != document:
        raise RuntimeError("table is frozen; publish a new manifest instead")
    atomic_json(path, document)
    return document


class ProductionTables:
    def __init__(self, path_or_document, *, calibration_hash, registered=False, expected_manifest_hash=None, receipt=None):
        from .artifacts import input_path
        if isinstance(path_or_document, (str, Path)):
            path_or_document = input_path(path_or_document)
        document = read(path_or_document) if isinstance(path_or_document, (str, Path)) else path_or_document
        self.document_hash = document.get("sha256")
        if receipt is None and isinstance(path_or_document, (str, Path)):
            receipt_path = Path(path_or_document).with_suffix(".a10_receipt.json")
            if receipt_path.exists():
                receipt = read(receipt_path)
        self.a10_receipt = receipt
        self.payload = unseal(document)
        p = self.payload
        if 'repair' in p.get('manifest', {}):
            from .table_compatibility_a3 import require_compatible
            require_compatible(path_or_document, document)
        from .table_compatibility import compatible
        source_file_hash = file_hash(path_or_document) if isinstance(path_or_document, (str, Path)) else None
        validation_fixture = False
        if not registered and p.get("fixture") is True:
            from .recording_validation import validation_probe_compatible
            validation_fixture = validation_probe_compatible(document, source_file_hash)
        a10_source_ok = False
        if p.get("manifest", {}).get("a10"):
            from .compatibility_a10 import read_identities
            a10_source_ok = p["code_hash"] in read_identities(registered=registered)
        if p.get("schema") != "v3-tables-1" or p["code_hash"] != code_identity() and not a10_source_ok and not validation_fixture and not compatible(document, source_file_hash):
            raise ValueError("stale table source identity")
        if p["manifest_hash"] != digest(p["manifest"]) or expected_manifest_hash is not None and p["manifest_hash"] != expected_manifest_hash:
            raise ValueError("table manifest hash mismatch")
        if p["manifest"]["calibration_hash"] != calibration_hash:
            raise ValueError("table/calibration mismatch")
        if set(p["rows"]) != set(p["manifest"]["required_row_keys"]):
            raise ValueError("missing manifest rows")
        self.rows = {}
        self.continuations = {}
        for key, sealed in p["rows"].items():
            row = unseal(sealed)
            if row_key(row) != key or row["calibration_hash"] != calibration_hash:
                raise ValueError("table row context mismatch")
            if row["status"] not in ("estimated", "not_estimable"):
                raise ValueError("unknown row status")
            if row["status"] == "estimated":
                entries = row.get("continuation", {}).get("entries", [])
                bins = [tuple(e["bin"]) for e in entries]
                if len(set(bins)) != len(bins) or any(len(b) != 6 for b in bins):
                    raise ValueError("duplicate or malformed continuation bin")
                if not math.isfinite(row["lambda_f"]["mean"]) or not math.isfinite(row["flow_range"]) or row["flow_range"] <= 0:
                    raise ValueError("invalid estimated flow")
                if any(not math.isfinite(e["value"]) or not math.isfinite(e["error"]) or e["error"] < 0 for e in entries):
                    raise ValueError("invalid continuation enclosure")
                self.continuations[key] = {tuple(e["bin"]): e for e in entries}
            self.rows[key] = row
        self.fixture = p["fixture"]
        self.calibration_hash = calibration_hash
        self.manifest_hash = p["manifest_hash"]
        if registered:
            self.require_production()

    def require_production(self):
        if self.fixture or self.payload["manifest"].get("tag") != "v3_tables":
            raise RuntimeError("registered execution rejects fixture or pilot tables")
        if not self.rows or not self.payload["manifest"].get("complete_family"):
            raise RuntimeError("registered table family is incomplete")
        if self.payload["manifest"].get("sensitivity_status") != "passed":
            rejected = sum(row["status"] != "estimated" for row in self.rows.values())
            sensitivity = sum(row.get("sensitivity", {}).get("selected", False) and row["sensitivity"].get("passed") is False for row in self.rows.values())
            raise RuntimeError(f"table sensitivity screens are incomplete or failed: {sensitivity} selected rows failed; {rejected} total not_estimable rows")
        for row in self.rows.values():
            # A4: a plain row certified through C0 alone has no fine entries but
            # a published C0, which is valid support.
            has_support = bool(row.get("continuation", {}).get("entries")) or (row.get("route") == "plain" and row.get("c0") is not None)
            if row["status"] != "estimated" or not has_support:
                raise RuntimeError("registered execution rejects missing or not_estimable table rows")

    def require_a10(self, instrument):
        from .instrument import CONSTANTS_SHA256
        from .compatibility_a10 import accepted_identities
        accepted = accepted_identities()
        self.require_production()
        manifest = self.payload["manifest"]
        provenance = manifest.get("a10")
        if (self.payload["code_hash"] not in accepted or not provenance
                or provenance.get("constants_sha256") != CONSTANTS_SHA256
                or provenance.get("producer_code_hash") not in accepted
                or instrument.declaration() not in provenance.get("instruments", [])):
            raise ValueError("registered A10 refuses another table producer or instrument")
        if self.a10_receipt is None:
            raise ValueError("registered A10 requires its producer receipt")
        receipt = unseal(self.a10_receipt)
        if (receipt.get("schema") != "v3-A10-table-receipt-1"
                or receipt.get("table_sha256") != self.document_hash
                or receipt.get("producer_code_hash") not in accepted
                or receipt.get("constants_sha256") != CONSTANTS_SHA256
                or not receipt.get("validation_receipt_sha256") or not receipt.get("labels_sha256")):
            raise ValueError("A10 producer receipt mismatch or missing validation/labels")
        from .artifacts import canonical
        import hashlib
        for field, digest_field in (("validation_receipt", "validation_receipt_sha256"), ("labels", "labels_sha256")):
            embedded = receipt.get(field)
            if not embedded or hashlib.sha256(canonical(embedded) + b"\n").hexdigest() != receipt[digest_field]:
                raise ValueError("A10 receipt embedded evidence hash mismatch")
            unseal(embedded)
        validation, labels = unseal(receipt["validation_receipt"]), unseal(receipt["labels"])
        if (validation.get("table_seal_sha256") != self.document_hash
                or validation.get("producer_code_hash") not in accepted
                or validation.get("schema") != "v3-A4-receipt-1"
                or labels.get("schema") != "v3-A5-label-1"
                or labels.get("a4_family", {}).get("table_seal_sha256") != self.document_hash
                or labels.get("code_hash") not in accepted):
            raise ValueError("A10 receipt evidence belongs to another table")
        expected = {key for key, row in self.rows.items() if row.get("route") == "fv" and row["status"] == "estimated"}
        if {r["row_key"] for r in labels.get("rows", [])} != expected:
            raise ValueError("A10 per-capability A5 labels are incomplete")
        from .continuation_validation import fine_codes
        from .table_labels_a5 import label_for
        for label in labels.get("rows", []):
            row = self.rows[label["row_key"]]
            cells = label.get("cells", [])
            expected_cells = {int(c) for c in fine_codes([e["bin"] for e in row["continuation"]["entries"]])}
            if (label.get("scoring") != row["scoring"] or {c["cell"] for c in cells} != expected_cells
                    or len(cells) != len(expected_cells)
                    or any(c["status"] not in ("certified", "unresolved", "violation") or c["label"] != label_for(c["status"]) for c in cells)):
                raise ValueError("A10 A5 labels do not cover the row's own validated cells")

    def lookup_available(self, rules, bins, **context):
        """Return explicit missing-score masks for allocation and plan comparisons."""
        return self.lookup(rules, bins, allow_unavailable=True, **context)

    def lookup(self, rules, bins, *, kernel_hash, capability, alpha, weights, extinct=None, initial_population=200,
               allow_unavailable=False, instrument=None):
        if tuple(weights[:2]) != (5, 3):
            raise ValueError("unfrozen objective weights")
        dead = np.zeros(len(rules), bool) if extinct is None else np.asarray(extinct, bool)
        if instrument is not None:
            instrument.require_capability(capability)
        c, ce, lf, le, lb, ls, available, reasons = [], [], [], [], [], [], [], []
        for index, (rule, summary) in enumerate(zip(rules, bins)):
            stub = {"rule_id": rule.rule_id, "kernel_hash": kernel_hash, "calibration_hash": self.calibration_hash,
                    "initial_population": initial_population,
                    "scoring": {"alpha": alpha, "capability": capability, "kappa": weights[2]}}
            if instrument is not None and instrument.a10:
                stub["scoring"].update(instrument.declaration())
            key = row_key(stub)
            row = self.rows.get(key)
            if row is not None and row["rule_hash"] != digest(rule.__dict__):
                raise ValueError("stale rule identity")
            entry = self.continuations.get(key, {}).get(tuple(map(int, summary)))
            # A4: for a plain row with a published C0, every population-category-0
            # key resolves to that single stored C0, whether or not an entry
            # exists. Nothing else in the lookup changes: FV rows, extinct
            # endpoints and every other key are as before.
            if (not dead[index] and row is not None and row.get("route") == "plain"
                    and int(summary[0]) == 0 and row.get("c0") is not None):
                entry = row["c0"]
            reason = ("missing_or_not_estimable_row" if row is None or row["status"] != "estimated" else
                      "unpublished_continuation_bin" if entry is None and not dead[index] else None)
            if reason is not None:
                if not allow_unavailable:
                    raise KeyError("missing continuation bin; no neighbor or midpoint substitution" if reason == "unpublished_continuation_bin"
                                   else "missing or not_estimable rule/context row")
                # NaN marks absent arithmetic internally. It is never a score,
                # a substituted continuation, or a serialized diagnostic.
                c.append(np.nan); ce.append(np.nan); lf.append(np.nan); le.append(np.nan)
                lb.append(None); ls.append(None); available.append(False); reasons.append(reason)
                continue
            available.append(True); reasons.append(None)
            c.append(0. if entry is None else entry["value"])
            ce.append(0. if entry is None else entry["error"])
            lf.append(row["lambda_f"]["mean"])
            # Domain error, not an empirical CI pretending to cover bias.
            le.append(row.get("flow_range", 1e6))
            lb.append(row.get("lambda_b")); ls.append(row.get("LS"))
        return AvailableLookup(np.asarray(c), np.asarray(ce), np.asarray(lf), np.asarray(le), tuple(lb), tuple(ls), self.fixture,
                               np.asarray(available, dtype=bool), tuple(reasons))


def conformance():
    """Round-trip and tamper rejection using a deliberately empty test manifest."""
    from .artifacts import ROOT
    with tempfile.TemporaryDirectory(dir=ROOT, prefix="table_validation_") as directory:
        path = Path(directory) / "tables.json"
        document = write_tables(path, [], {"required_row_keys": [], "calibration_hash": "validation", "tag": "validation"}, fixture=True)
        loaded = ProductionTables(path, calibration_hash="validation")
        assert loaded.fixture and loaded.manifest_hash == document["payload"]["manifest_hash"]
        try:
            ProductionTables(document, calibration_hash="validation", registered=True)
        except RuntimeError:
            pass
        else:
            raise AssertionError("fixture was admitted")
        document["payload"]["fixture"] = False
        try:
            ProductionTables(document, calibration_hash="validation")
        except ValueError:
            pass
        else:
            raise AssertionError("tamper was accepted")
    return {"complete": True, "scope": "writer/loader mechanics, not estimated production data"}
