"""The input contract (section 2): ``inputs.json``, the collection, the
authorized-hash document (A8.1) and the inventory adapter (A2.10, A3.6, A8.3,
A8.4, A9.3). Nothing here opens a run output.
"""
import hashlib
import os
import stat
from pathlib import Path

from .base import CREATED, document_bytes, is_hash, reader_identity, sealed, sealed_bytes, write_once
from .common import Refused, loads, require
from .registry import ARM_FAMILIES

INPUTS_SCHEMA = "a10-stage2-reader-inputs-1"
COLLECTION_SCHEMA = "a10-stage2-collection-1"
AUTH_REGISTERED = "a10-stage2-authorized-hashes-1"
AUTH_FIXTURE = "a10-stage2-authorized-hashes-fixture-1"
INV_S = "stage2-sqrt-reading-input-inventory-1"
INV_C = "stage2-crowding-reading-input-inventory-1"
INV_2 = "stage2-reading-input-inventory-2"
PUBLISHED_KEY = {INV_S: "published_files", INV_C: "published_files_and_inputs", INV_2: "published_files_and_inputs"}

TOP_KEYS = {"schema", "fixture", "execution_simulation", "authorized_hashes", "registration", "arms", "comparator"}
RUN_ARM_KEYS = {"status", "inventory", "spec", "pre_spec", "root", "family", "calibration", "excluded_roots"}
ARM_FAMILY_KEYS = {"table", "validation_receipt", "cell_results", "a10_receipt", "identity", "admission_check", "a16"}
COMPARATOR_KEYS = {"binding", "spec", "root", "family", "calibration", "execution_simulation"}
COMPARATOR_FAMILY_KEYS = {"table", "validation_receipt", "cell_results", "a10_receipt", "labels", "identity",
                          "admission_check", "a13_round_admission", "a13_round_record", "a14_round_record",
                          "a14_public_record", "a13_public_record"}
EVIDENCE_A16 = {"a16_family_record", "refused_admission_record", "a16_round_admission_records"}
EVIDENCE_CLOSEOUT = {"refused_admission_record", "closeout_record"}
ROUND_KEYS = {"round_record", "admission_record", "public"}
AUTH_KEYS = {"schema", "inventories", "specification_set", "specification_set_digest", "requirements_sha256",
             "registration", "not_run_evidence", "sqrt_admission_check_sha256", "supplementary_records"}
AUTH_FIXTURE_KEYS = AUTH_KEYS | {"identity_records", "a13_refusal_admission_record_sha256", "fixture_list_hash",
                                 "fixture_layout"}
SUPPLEMENTARY_KEYS = {"a16_family_record", "a16_round_records", "a16_round_admission_records", "a16_public_records"}
# A8.3's name map between inputs.json and an inventory.
ARM_NAME_MAP = {"table": "family_table", "identity": "family_identity", "admission_check": "a13_admission",
                "validation_receipt": "validation_receipt", "cell_results": "cell_results", "a10_receipt": "a10_receipt",
                "labels": "labels"}
COMPARATOR_NAME_MAP = {"table": "family_table", "identity": "family_identity", "admission_check": "a14_round_admission",
                       "validation_receipt": "validation_receipt", "cell_results": "cell_results",
                       "a10_receipt": "a10_receipt", "labels": "labels", "a13_round_admission": "a13_round_admission",
                       "a13_round_record": "a13_round_record", "a14_round_record": "a14_round_record",
                       "a14_public_record": "a14_public_record", "a13_public_record": "a13_public_record"}


def _path(value, label):
    require(isinstance(value, str) and value != "", label)
    return value


def validate_form(value):
    """A10.3b, "form": what ``collect`` checks of the operator's document, and
    no more. The top-level key set; the four family names; each arm's key set
    for its status; the ``comparator``, ``comparator.family`` and evidence key
    sets; and the value types in those places. Every other test of the document
    belongs to ``verify`` (``validate_inputs``). A11.2: the list is exhaustive.
    An arm's ``family`` key set, the ``a16`` block's shape, ``registration``'s
    key set and an ``excluded_roots`` entry's key set are not tested here,
    beyond the leaf rule of A10.3a item 5, each ``excluded_roots`` element being
    an object with a string ``path`` (absolute, tested by ``collect``), and the
    arm ``status`` value."""
    require(isinstance(value, dict), "inputs keys")
    # Rule question RQ-3: ``path_map`` is named by D:287 and A3.5 row 8 but its form
    # rests on CC, which this builder does not receive, and Addendum 10 does not
    # rule on it. Literal reading: the key is accepted in fixture mode and refused
    # in registered mode; it maps nothing.
    require(set(value) - {"path_map"} == TOP_KEYS, "inputs keys")
    require(type(value["fixture"]) is bool, "inputs fixture flag")
    require(isinstance(value["schema"], str) and isinstance(value["registration"], dict), "inputs keys")
    _path(value["execution_simulation"], "inputs path")
    _path(value["authorized_hashes"], "inputs path")
    arms = value["arms"]
    require(isinstance(arms, dict) and set(arms) == set(ARM_FAMILIES), "inputs arm names")
    for arm in arms.values():
        require(isinstance(arm, dict) and arm.get("status") in ("run", "not_run"), "inputs arm status")
        if arm["status"] == "not_run":
            require(set(arm) == {"status", "evidence"} and isinstance(arm["evidence"], dict), "not-run arm keys")
            evidence = arm["evidence"]
            require(set(evidence) in (EVIDENCE_A16, EVIDENCE_CLOSEOUT), "not-run evidence set")
            for name, item in evidence.items():
                if name == "a16_round_admission_records":
                    require(isinstance(item, list), "not-run evidence set")
                    for one in item:
                        _path(one, "inputs path")
                else:
                    _path(item, "inputs path")
            continue
        require(set(arm) == RUN_ARM_KEYS, "inputs arm keys")
        for name in ("inventory", "spec", "root", "calibration"):
            _path(arm[name], "inputs path")
        require(arm["pre_spec"] is None or isinstance(arm["pre_spec"], str), "inputs path")
        require(isinstance(arm["family"], dict), "inputs family keys")
        require(isinstance(arm["excluded_roots"], list), "inputs excluded roots")
        for root in arm["excluded_roots"]:
            require(isinstance(root, dict) and isinstance(root.get("path"), str), "inputs excluded roots")
    comparator = value["comparator"]
    require(isinstance(comparator, dict) and set(comparator) == COMPARATOR_KEYS, "inputs comparator keys")
    for name in ("binding", "spec", "root", "calibration", "execution_simulation"):
        _path(comparator[name], "inputs path")
    fam = comparator["family"]
    require(isinstance(fam, dict) and set(fam) == COMPARATOR_FAMILY_KEYS, "inputs comparator family keys")
    for item in fam.values():
        _path(item, "inputs path")
    return value


def file_leaves(inputs):
    """A10.3a item 5: the file leaves of the document, as ``(label, path)``.
    The label is the path of keys from the document's top joined by ``/``, a
    list element named by its zero-based index. A null is no leaf; any other
    non-string value where leaves are looked for refuses."""
    leaves = []

    def walk(value, label):
        if value is None:
            return
        if isinstance(value, str):
            leaves.append((label, value))
        elif isinstance(value, dict):
            for key in sorted(value):
                require(isinstance(key, str), "inputs leaf type")
                walk(value[key], label + "/" + key)
        elif isinstance(value, list):
            for index, item in enumerate(value):
                walk(item, "%s/%d" % (label, index))
        else:
            raise Refused("inputs leaf type")

    walk(inputs["authorized_hashes"], "authorized_hashes")
    for family in sorted(inputs["arms"]):
        arm = inputs["arms"][family]
        for key in sorted(arm):
            if key not in ("status", "root", "excluded_roots"):
                walk(arm[key], "arms/%s/%s" % (family, key))
    comparator = inputs["comparator"]
    for key in sorted(comparator):
        if key not in ("execution_simulation", "root"):
            walk(comparator[key], "comparator/" + key)
    labels = [label for label, _ in leaves]
    require(len(set(labels)) == len(labels), "inputs leaf type")
    return leaves


def read_leaf(path, label):
    """The read hook of ``collect`` (A10.3a item 6, A10.9 item 3): how one file
    leaf is reached and read. The path is opened with symbolic links followed;
    the file reached must be a regular file; the bytes come from one read. The
    label is passed for a test's content rule and is not used here."""
    try:
        with open(path, "rb") as stream:
            require(stat.S_ISREG(os.fstat(stream.fileno()).st_mode), "input_missing")
            return stream.read()
    except OSError:
        raise Refused("input_missing") from None


def validate_inputs(value):
    """The ``inputs.json`` shape of D:301-331 as amended by A1.2, A2.1, A3.4 and
    A8.3. All four family names must be present; a missing name is a refusal,
    not an implied not-run (D:333). Run in full by ``verify`` and ``read``
    whatever ``collect`` checked (A10.3b)."""
    validate_form(value)
    file_leaves(value)
    require(isinstance(value, dict) and value.get("schema") == INPUTS_SCHEMA, "inputs schema")
    require(set(value) - {"path_map"} == TOP_KEYS, "inputs keys")
    require(type(value["fixture"]) is bool, "inputs fixture flag")
    _path(value["execution_simulation"], "inputs path")
    _path(value["authorized_hashes"], "inputs path")
    pin = value["registration"]
    require(isinstance(pin, dict) and set(pin) == {"commit", "path", "sha256"}, "inputs registration pin")
    arms = value["arms"]
    require(isinstance(arms, dict) and set(arms) == set(ARM_FAMILIES), "inputs arm names")
    for family, arm in arms.items():
        require(isinstance(arm, dict) and arm.get("status") in ("run", "not_run"), "inputs arm status")
        if arm["status"] == "not_run":
            require(set(arm) == {"status", "evidence"} and isinstance(arm["evidence"], dict), "not-run arm keys")
            evidence = arm["evidence"]
            require(set(evidence) in (EVIDENCE_A16, EVIDENCE_CLOSEOUT), "not-run evidence set")
            for name, item in evidence.items():
                if name == "a16_round_admission_records":
                    require(isinstance(item, list), "not-run evidence set")
                    for one in item:
                        _path(one, "inputs path")
                else:
                    _path(item, "inputs path")
            continue
        require(set(arm) == RUN_ARM_KEYS, "inputs arm keys")
        for name in ("inventory", "spec", "root", "calibration"):
            _path(arm[name], "inputs path")
        require(arm["pre_spec"] is None or isinstance(arm["pre_spec"], str), "inputs path")
        fam = arm["family"]
        require(isinstance(fam, dict), "inputs family keys")
        # G7 and A10.8 item 6: no labels file is accepted for a no-label family
        # (D:371). The test is on ``inputs.json`` alone, in ``verify``; the
        # reader searches no directory for one.
        require("labels" not in fam or family == "sqrt", "labels file supplied for a no-label family")
        require(set(fam) == ARM_FAMILY_KEYS | ({"labels"} if family == "sqrt" else set()), "inputs family keys")
        for name, item in fam.items():
            if name != "a16":
                _path(item, "inputs path")
        a16 = fam["a16"]
        if a16 is not None:
            require(isinstance(a16, dict) and set(a16) == {"family_record", "rounds"}, "inputs a16 keys")
            _path(a16["family_record"], "inputs path")
            rounds = a16["rounds"]
            require(isinstance(rounds, dict) and set(rounds) in ({"r1"}, {"r1", "r2"}), "inputs a16 keys")
            for one in rounds.values():
                require(isinstance(one, dict) and set(one) == ROUND_KEYS, "inputs a16 keys")
                for item in one.values():
                    _path(item, "inputs path")
        roots = arm["excluded_roots"]
        require(isinstance(roots, list), "inputs excluded roots")
        for root in roots:
            require(isinstance(root, dict) and set(root) == {"path", "reason", "inventory_key"}, "inputs excluded roots")
    comparator = value["comparator"]
    require(isinstance(comparator, dict) and set(comparator) == COMPARATOR_KEYS, "inputs comparator keys")
    for name in ("binding", "spec", "root", "calibration", "execution_simulation"):
        _path(comparator[name], "inputs path")
    fam = comparator["family"]
    require(isinstance(fam, dict) and set(fam) == COMPARATOR_FAMILY_KEYS, "inputs comparator family keys")
    for item in fam.values():
        _path(item, "inputs path")
    return value


def input_roots(inputs):
    """A10.3b: the input roots."""
    roots = [inputs["execution_simulation"], inputs["comparator"]["execution_simulation"], inputs["comparator"]["root"]]
    for arm in inputs["arms"].values():
        if arm["status"] == "run":
            roots.append(arm["root"])
            roots += [r["path"] for r in arm["excluded_roots"]]
    return roots


def require_new_outside(out, inputs):
    """A10.3b and G0 (D:341): the destination must not exist, and must not be
    inside, or equal to, any input root, decided on ``os.path.realpath`` of
    both by whole path components."""
    require(not os.path.lexists(out), "output destination exists")
    resolved = Path(os.path.realpath(out))
    for root in input_roots(inputs):
        root = Path(os.path.realpath(root))
        require(resolved != root and not resolved.is_relative_to(root), "output destination inside an input root")


def collection_payload(inputs):
    """A10.3a items 3 to 6: the emitted ``inputs.json`` bytes and the collection
    payload, each file leaf read once in place through ``read_leaf``."""
    files = {}
    for label, path in file_leaves(inputs):
        data = read_leaf(path, label)
        files[label] = {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
    emitted = document_bytes(inputs)
    return emitted, {"schema": COLLECTION_SCHEMA, "inputs_sha256": hashlib.sha256(emitted).hexdigest(), "files": files}


def collect(inputs_path, out):
    """A10.3a and A10.3b: the one common collection. ``collect`` parses the
    operator's document strictly, checks its form and that each path is
    absolute, reads each file leaf once to hash it, requires the destination to
    be new and outside every input root, and writes the two files,
    ``collection.json`` last. It parses no other file, verifies no seal and
    decides no mode."""
    try:
        raw = Path(inputs_path).read_bytes()
    except OSError:
        raise Refused("input_missing") from None
    inputs = validate_form(loads(raw))
    leaves = file_leaves(inputs)
    for path in [p for _, p in leaves] + input_roots(inputs):
        require(os.path.isabs(path), "inputs path is not absolute")
    require_new_outside(out, inputs)
    emitted, payload = collection_payload(inputs)
    key = str(out)
    out = Path(out)
    out.mkdir(parents=True)
    CREATED.add(key)
    return {"inputs.json": write_once(out / "inputs.json", emitted),
            "collection.json": write_once(out / "collection.json", sealed_bytes(payload)),
            "files": len(payload["files"])}


def load_collection(inputs_path):
    """A10.3b: the tests ``verify`` and ``read`` make of the collection, in both
    modes. The fifth, each collected file's size and hash on the pass's first
    read, is made by the ledger."""
    inputs_path = Path(inputs_path)
    require(inputs_path.name == "inputs.json", "sealed collection missing")
    try:
        raw = inputs_path.read_bytes()
        collection_raw = (inputs_path.parent / "collection.json").read_bytes()
    except OSError:
        raise Refused("sealed collection missing") from None
    collection = sealed(loads(collection_raw), "collection seal")
    require(isinstance(collection, dict) and set(collection) == {"schema", "inputs_sha256", "files"}
            and collection["schema"] == COLLECTION_SCHEMA and isinstance(collection["files"], dict), "collection schema")
    require(hashlib.sha256(raw).hexdigest() == collection["inputs_sha256"], "inputs differ from the sealed collection")
    inputs = validate_inputs(loads(raw))
    require(set(collection["files"]) == {label for label, _ in file_leaves(inputs)}, "collection file inventory")
    require(all(isinstance(e, dict) and set(e) == {"bytes", "sha256"} for e in collection["files"].values()),
            "collection schema")
    return inputs, collection, hashlib.sha256(collection_raw).hexdigest(), inputs_path.parent


def load_authorized(ledger, inputs, fixture):
    """A8.1: the sealed authorized-hash document, with exactly its listed fields."""
    document, sha = ledger.json(inputs["authorized_hashes"], "authorized_hashes")
    auth = sealed(document, "authorized-hash document seal")
    # MODE TERM 9 (A3.5 row 9): which document schema is accepted.
    if fixture:
        require(auth.get("schema") == AUTH_FIXTURE and set(auth) == AUTH_FIXTURE_KEYS, "authorized-hash document schema or keys")
    else:
        require(auth.get("schema") == AUTH_REGISTERED and set(auth) == AUTH_KEYS, "authorized-hash document schema or keys")
    run = sorted(f for f, a in inputs["arms"].items() if a["status"] == "run")
    not_run = sorted(f for f, a in inputs["arms"].items() if a["status"] == "not_run")
    inventories = auth["inventories"]
    require(isinstance(inventories, dict) and sorted(inventories) == sorted(run + ["comparator"]), "authorized-hash document entries")
    for entry in inventories.values():
        require(isinstance(entry, dict) and set(entry) == {"file_sha256", "seal"} and is_hash(entry["file_sha256"])
                and is_hash(entry["seal"]), "authorized-hash document entries")
    spec_set = auth["specification_set"]
    require(isinstance(spec_set, list) and spec_set and all(
        isinstance(d, dict) and set(d) == {"name", "sha256"} and isinstance(d["name"], str) and is_hash(d["sha256"])
        for d in spec_set), "authorized-hash document specification set")
    from v3.artifacts import digest as native_digest
    require(auth["specification_set_digest"] == native_digest(spec_set), "specification set digest")
    require(is_hash(auth["requirements_sha256"]), "authorized-hash document entries")
    # A10.8 item 4: the registration pin has one value, key for key, in both modes.
    require(auth["registration"] == inputs["registration"], "registration pin differs from the authorized pin")
    evidence = auth["not_run_evidence"]
    require(isinstance(evidence, dict) and sorted(evidence) == not_run, "authorized-hash document entries")
    sqrt_hash = auth["sqrt_admission_check_sha256"]
    require((sqrt_hash is None) == ("sqrt" in not_run) and (sqrt_hash is None or is_hash(sqrt_hash)),
            "authorized-hash document entries")
    require(isinstance(auth["supplementary_records"], dict), "authorized-hash document entries")
    if fixture:
        identities = auth["identity_records"]
        require(isinstance(identities, dict) and sorted(identities) == sorted(run + ["nominal"])
                and all(is_hash(v) for v in identities.values()), "authorized-hash document entries")
        layout = auth["fixture_layout"]
        require(isinstance(layout, dict) and sorted(layout) == sorted(run + ["comparator"]), "authorized-hash document entries")
        for entry in layout.values():
            require(isinstance(entry, dict) and set(entry) == {"seeds_per_cell", "job_count"}
                    and all(type(v) is int and v > 0 for v in entry.values()), "authorized-hash document entries")
        require(is_hash(auth["a13_refusal_admission_record_sha256"]) and is_hash(auth["fixture_list_hash"]),
                "authorized-hash document entries")
    return auth, sha


class Inventory:
    """The adapter for exactly three schemas, selected by the ``schema`` string
    alone (A8.4). It reads the subset of D:248-256 with the keys A2.10, A3.6,
    A8.3 and A9.3 add, and ignores every other key."""

    def __init__(self, payload):
        require(isinstance(payload, dict) and payload.get("schema") in PUBLISHED_KEY, "inventory schema")
        self.schema = payload["schema"]
        self.payload = payload
        try:
            self.verdict, self.findings = payload["verdict"], payload["findings"]
            self.code_identity = payload["identity"]["code_identity"]
            self.checkout_commit = payload["identity"]["checkout_commit"]
            runs = payload["roots"]["runs"]
            self.runs = {k: runs[k] for k in ("path", "jobs", "records", "outputs", "outputs_digest",
                                              "verified_output_hashes_sha256", "manifest_file_sha256",
                                              "identity_file_sha256", "all_checks_pass")}
            self.spec = {k: runs["spec"][k] for k in ("path", "file_sha256", "seal")}
            self.published = payload[PUBLISHED_KEY[self.schema]]
        except (KeyError, TypeError):
            raise Refused("inventory keys") from None
        require(isinstance(self.published, dict), "inventory keys")
        self.registration_pin = payload.get("registration_pin")
        failed = payload.get("failed_attempt")
        self.failed_attempt = None
        if self.schema == INV_S and failed is not None:
            require(isinstance(failed, dict) and isinstance(failed.get("path"), str)
                    and isinstance(failed.get("not_run_reason"), str), "inventory keys")
            self.failed_attempt = {"path": failed["path"], "not_run_reason": failed["not_run_reason"]}

    def entry(self, name):
        """A published file's ``{sha256, seal}``; ``None`` when the family has none."""
        return _entry(self.published.get(name))

    def entries(self, name):
        value = self.published.get(name)
        require(isinstance(value, list), "inventory keys")
        return [_entry(v) for v in value]


def _entry(value):
    if value is None:
        return None
    require(isinstance(value, dict), "inventory keys")
    if value.get("present") is False or value.get("sha256") is None:
        return None
    require(is_hash(value.get("sha256")) and (value.get("seal") is None or is_hash(value["seal"])), "inventory keys")
    return {"sha256": value["sha256"], "seal": value.get("seal")}


def identity_line():
    return reader_identity()["sha256"]
