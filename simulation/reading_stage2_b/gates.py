"""The integrity gates G0 to G9 (section 3), in fixed order. All gates run
before any estimator. G0 to G3 open no run output.

Mode terms are exactly those of A3.5; each is marked ``MODE TERM <row>``.
Everything else runs the same code in fixture mode and registered mode.
"""
import hashlib
import os
import platform
import subprocess
import sys
import tempfile
import warnings
from pathlib import Path

from . import incidence as inc
from . import registry as R
from .base import Ledger, is_hash, reader_identity, sealed, sealed_bytes
from .common import Refused, loads, require
from .inputs import (ARM_NAME_MAP, COMPARATOR_NAME_MAP, INV_2, ROUND_KEYS, SUPPLEMENTARY_KEYS, Inventory, _entry,
                     file_leaves, load_authorized, require_new_outside)

MAIN, NOMINAL = "main", "nominal"
FAMILY_OF = {"main": "nominal", "sqrt": "sqrt", "crowding": "crowding", "sigma_squared_x10": "sigma_squared_x10",
             "sigma_squared_x0.1": "sigma_squared_x0.1"}
JOB_KEYS = {"kind", "config", "tag", "index", "id", "seed", "seed_identity"}
FORBIDDEN_MODEL_KEYS = ("n_agents", "carrying_capacity", "rollout_steps")
A13_SCOPE, A14_SCOPE = "validation_launched_under_A13", "A10_nominal_after_A14"
A16_SCOPES = {"A10_stage2_after_A16_r1": 1, "A10_stage2_after_A16_r2": 2}
CHECK_SCHEMA = "v3-A13-admission-check-1"
CLOSEOUT_SCHEMA = "a10-stage2-item42-closeout-1"
CLOSEOUT_KEYS = {"schema", "family", "status", "reason", "a16_entered", "refused_admission_record",
                 "canonical_run_roots_checked", "no_other_run_root_of_the_family_exists"}
ERROR_FIELDS = ("P", "M", "alpha", "E", "E2", "extension_error_bound", "tests_round1", "tests_round2")
# D:233-238: the frozen calibrations, file sha256 and seal.
PARENT_CALIBRATION = ("fd86358a39e3b643fb9adc4e81a2372915ca50a1866e9b0e330a874b41746e01",
                      "bf0f7c3f10310558d567b6b3f7c24f6f99f2fe6eb71fd830cccfd8e2aa0bd6d6")
VARIANT_CALIBRATION = {
    "sigma_squared_x10": ("aecef21ab61e0c7078b7fcf40fee540f9891a0ac3e32e995699cbfbd8264dbce",
                          "256380ab7c65465766f0407c6f8468dd35dbfaced08c3db72388b1e0882abca9"),
    "sigma_squared_x0.1": ("93c35a47e9aed3bd904fdc79ae24feb4015b75eb33bd42aa3a5220ae2ce88394",
                           "d9cde18fd08d6eabe171115a3b9cbc1807e14380286e185290916a07f81e2aa4"),
}
SEED_REGISTRY = "v3/runs/registered/A10_stage2_seed_registry.json"


def native(label, function, *args, **kwargs):
    """Call native code; its exception text never leaves the reader (D:544)."""
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            return function(*args, **kwargs)
    except Refused:
        raise
    except Exception:
        raise Refused(label) from None


def committed_bytes(relative):
    """``git show HEAD:<path>`` in the reader's checkout (D:231, A1.12)."""
    from v3.artifacts import SIMULATION
    repo = SIMULATION.parent
    environment = dict(os.environ, GIT_OPTIONAL_LOCKS="0")
    try:
        subprocess.run(["git", "-C", str(repo), "ls-files", "--error-unmatch", relative], check=True,
                       capture_output=True, env=environment)
        return subprocess.run(["git", "-C", str(repo), "show", "HEAD:" + relative], check=True, capture_output=True,
                              env=environment).stdout
    except (subprocess.CalledProcessError, OSError):
        raise Refused("committed record not readable at HEAD") from None


def preload():
    """A2.8: import every NumPy-using module the reader calls, then set the
    warning filter again, so that a filter added at import cannot outrank it."""
    import numpy
    from v3 import (admission_a13, artifacts, calibration, compatibility_a10, context, gates, history_a14,  # noqa: F401
                    instrument, production_tables, reading_a6, study, tables_a10, validation_extension_a16)
    numpy.seterr(all="ignore")
    warnings.simplefilter("ignore")


def decide_mode(inputs, registered_flags):
    """D:333: mode is decided by the specs' ``registered`` flags; ``fixture``
    must agree with them, and a mixture refuses. Returns ``fixture``."""
    flags = set(registered_flags)
    require(len(flags) == 1 and all(type(v) is bool for v in flags) and inputs["fixture"] is (not next(iter(flags))),
            "mode mixture")
    fixture = inputs["fixture"]
    # MODE TERM 8 (A3.5 row 8): path_map is refused in registered mode.
    if not fixture:
        require("path_map" not in inputs, "path_map in registered mode")
    return fixture


def calibration_pins(family, fixture):
    """The frozen calibration's (file sha256, seal) for a family."""
    # MODE TERM 4 (A3.5 row 4): the sigma calibration. Registered mode pins the
    # two variant files; fixture mode holds the parent's bytes at the sigma path.
    if family in VARIANT_CALIBRATION and not fixture:
        return VARIANT_CALIBRATION[family]
    return PARENT_CALIBRATION


def check_identity_record(family, raw, sha, fixture, authorized):
    from v3 import tables_a10
    # MODE TERM 6 (A3.5 row 6): the identity record's committed bytes.
    if fixture:
        require(sha == authorized["identity_records"][family], "identity record differs from its authorized hash")
    else:
        relative = "simulation/" + (Path(tables_a10.STAGE2_PATHS[family][1]).parent / "family_identity.json").as_posix()
        require(raw == committed_bytes(relative), "identity record differs from the committed record")


def check_seed_registry(ledger, digests):
    """MODE TERM 7 (A3.5 row 7), registered mode only: A1.12's seed registry."""
    from v3 import artifacts
    raw, _ = ledger.read(artifacts.SIMULATION / SEED_REGISTRY, "reader_checkout:" + SEED_REGISTRY)
    require(raw == committed_bytes("simulation/" + SEED_REGISTRY), "seed registry differs from the committed record")
    payload = sealed(loads(raw), "seal")
    require(set(digests) == {artifacts.digest(payload)}, "seed registry digest differs from the specs")


def check_comparator_pin(pin, inventory_pin):
    """MODE TERM 7 (A3.5 row 7), registered mode only: A1.6 and A2.10."""
    from v3 import artifacts, tables_a10
    native("comparator registration pin not verified", artifacts.verify_registration, pin,
           instrument=tables_a10.NOMINAL, historical=True)
    require(pin == inventory_pin and pin["commit"] == artifacts.A14_COMMIT, "comparator registration pin differs")


def check_marker(manifest, fixture):
    # MODE TERM 10 (A3.5 row 10): the fixture marker.
    if fixture:
        require(manifest.get("reader_fixture") is True, "fixture table lacks its marker")
    else:
        require("reader_fixture" not in manifest, "fixture table in registered mode")


def check_a13_refusal(sha, fixture, authorized):
    # MODE TERM 11 (A3.5 row 11): the A13 refusal constant.
    if fixture:
        require(sha == authorized["a13_refusal_admission_record_sha256"], "A13 refusal differs from its authorized hash")
    else:
        from v3 import history_a14
        require(sha == history_a14.ADMISSION_HASH, "A13 refusal differs from its registered constant")


def mode_name(fixture):
    # MODE TERM 12 (A3.5 row 12): the recorded mode.
    return "fixture" if fixture else "registered"


def flat_spec(component, job):
    """The specs-only part of the flat record of D:107-119."""
    try:
        cfg = job["config"]
        model, inst = cfg["model"], cfg["model"]["instrument"]
        if component == "sqrt":
            grid = cfg["grid"]
        elif component == MAIN:
            grid = cfg["category"]
        else:
            grid = cfg["a6_grid"]
        return {"job_id": job["id"], "component": component, "category": cfg["category"], "grid": grid,
                "arm": cfg.get("a6_arm"), "variant": cfg.get("a6_variant"),
                "rr": model["reproduction_rate"], "alpha": model["alpha"], "capability": model["successor_capability"],
                "kappa": model.get("kappa", 8.0), "theta": model.get("theta", 0.5),
                "crowding": model.get("crowding", "total"), "steps": cfg["steps"],
                "k_star": inst["k_star"], "g": inst["g"]}
    except (KeyError, TypeError, AttributeError):
        raise Refused("job definition malformed") from None


def _match(record, filters):
    return all(record.get(k) == v for k, v in filters.items())


def cell_members(records, entry, side):
    """The registry cells of one side of one comparison, as job ids, by the
    filters of D:129-137 (the rule of ``reading_a6.select_*_cells``)."""
    filters = entry["arm_filters"] if side == "arm" else entry["comparator_filters"]
    try:
        if entry["kind"] == "boundary":
            cells = {rr: [] for rr in entry["grid_values"]}
            for r in records:
                if _match(r, filters) and r["rr"] in cells:
                    cells[r["rr"]].append(r["job_id"])
        else:
            cells = {c: [] for c in R.CAPABILITIES}
            for r in records:
                if (r["alpha"] == entry["alpha"] and r["rr"] == R.CAPSTAR_RR and _match(r, filters)
                        and r["capability"] in cells):
                    cells[r["capability"]].append(r["job_id"])
    except TypeError:
        raise Refused("job definition malformed") from None
    return cells


def spec_structure(component, spec, *, fixture, layout=None):
    """G2 for one spec, from the spec alone. Returns ``(records, cells)`` where
    ``cells[identity]`` maps a cell key to its job ids."""
    from v3 import tables_a10
    jobs = spec.get("jobs")
    require(isinstance(jobs, list) and jobs and all(isinstance(j, dict) and set(j) == JOB_KEYS for j in jobs),
            "job definition malformed")
    ids = [j["id"] for j in jobs]
    seeds = [j["seed"] for j in jobs]
    require(all(isinstance(i, str) for i in ids) and all(type(s) is int for s in seeds), "job definition malformed")
    require(len(set(ids)) == len(ids), "duplicate job id")
    require(len(set(seeds)) == len(seeds), "duplicate job seed")
    records = [flat_spec(component, j) for j in jobs]
    for job in jobs:
        model = job["config"]["model"]
        # MODE TERM 5 (A3.5 row 5): model keys.
        # Rule question RQ-15: row 5 allows n_agents "only on F8's zero-agent
        # run", which the reader cannot identify. Literal reading: in fixture
        # mode n_agents is allowed only with the value 0.
        if fixture:
            allowed = "n_agents" not in model or (type(model["n_agents"]) is int and model["n_agents"] == 0)
            require(allowed and "carrying_capacity" not in model and "rollout_steps" not in model,
                    "fixture-only model key")
        else:
            require(not any(k in model for k in FORBIDDEN_MODEL_KEYS), "fixture-only model key")
    if component == MAIN:
        entries, side = R.REGISTRY, "comparator"
    else:
        entries, side = [e for e in R.REGISTRY if e["arm"] == component], "arm"
        require(spec.get("a10_family") == component and spec.get("a10_stage") == 2, "spec family or stage differs")
    # MODE TERMS 1 and 3 (A3.5 rows 1 and 3): job equality and counts.
    if fixture:
        require(len(jobs) == layout["job_count"], "job count differs")
    elif component == MAIN:
        expected = native("native job builder refused", tables_a10.paired_runs, *tables_a10.STAGE2_PATHS["nominal"])
        require(len(jobs) == R.COMPARATOR_JOBS and jobs == expected, "spec jobs differ from the registered jobs")
    else:
        expected = native("native job builder refused", tables_a10.stage2_runs, tables_a10.STAGE2_PATHS)[component]
        require(len(jobs) == R.RUN_COUNTS[component] == tables_a10.STAGE2_RUN_COUNTS[component] and jobs == expected,
                "spec jobs differ from the registered jobs")
    cells, covered = {}, set()
    for entry in entries:
        # MODE TERM 2 (A3.5 row 2): seeds per cell.
        if fixture:
            seeds_per_cell = layout["seeds_per_cell"]
        else:
            seeds_per_cell = entry["arm_seeds"] if side == "arm" else entry["comparator_seeds"]
        members = cell_members(records, entry, side)
        require(all(len(v) == seeds_per_cell for v in members.values()), "cell job count differs")
        cells[entry["identity"]] = members
        for v in members.values():
            covered.update(v)
    if component != MAIN or fixture:
        require(covered == set(ids), "job outside the registry cells")
    else:
        require(len(covered) == R.COMPARATOR_CONTRIBUTING, "comparator contributing run count differs")
    return records, cells


def structure(job, output):
    """G5, value-free, per contributing output. Returns the result dict."""
    result = output.get("result")
    require(isinstance(result, dict), "run result malformed")
    steps, n, path = result.get("diagnostics"), result.get("steps"), result.get("population_path")
    require(type(n) is int and n >= 1 and n == job["config"]["steps"] and isinstance(steps, list) and len(steps) == n,
            "run path length differs")
    require(isinstance(path, list) and len(path) == n and isinstance(result.get("yield_events"), list)
            and isinstance(result.get("continuation_availability"), dict), "run result malformed")
    for index, step in enumerate(steps):
        require(isinstance(step, dict) and type(step.get("time")) is int and step["time"] == index, "step times differ")
        require(type(step.get("population")) is int and step["population"] >= 0 and path[index] == step["population"]
                and type(path[index]) is int, "population path differs")
        require("capability" not in step or type(step["capability"]) in (int, float), "step field type")
        # Rule question RQ-8: G5 asks for native types and D:455 asks that the
        # two flags be bools, with A6.1's own label (A7.1, F17-N1). G5 tests
        # their presence here and leaves their type to D:455's precondition.
        require("allocation_evaluated" in step and "survival_first" in step, "step field type")
        require("unavailable_rules" not in step or isinstance(step["unavailable_rules"], dict), "step field type")
    final = result.get("final_population")
    require(type(final) is int and path[-1] == final, "final population inconsistent")
    require(type(result.get("survived_threshold_30")) is bool and result["survived_threshold_30"] == (final >= 30),
            "final population inconsistent")
    require(result.get("fixture_tables") is False, "run used fixture tables")
    return result


class Gates:
    def __init__(self, inputs, collection, collection_sha256, collection_dir, out=None):
        self.inputs, self.collection_sha256, self.collection_dir, self.out = inputs, collection_sha256, collection_dir, out
        self.ledger = Ledger(collection["files"])
        self.fixture = None
        self.arms_run = sorted(f for f, a in inputs["arms"].items() if a["status"] == "run")
        self.arms_not_run = sorted(f for f, a in inputs["arms"].items() if a["status"] == "not_run")
        self.fam, self.src, self.not_run, self.excluded = {}, {}, {}, []

    # ------------------------------------------------------------------ G0
    def g0(self):
        import numpy
        from v3 import artifacts, tables_a10
        from v3.compatibility_a10 import accepted_identities
        native("native modules not importable", preload)
        self.identity = reader_identity()
        # A6.3: the version assertion runs in both modes and is not a mode term.
        require(platform.python_version() == R.PYTHON_VERSION and numpy.__version__ == R.NUMPY_VERSION,
                "python or numpy version differs from the frozen environment")
        require(os.environ.get("PYTHONINTMAXSTRDIGITS") == "0" and sys.get_int_max_str_digits() == 0,
                "PYTHONINTMAXSTRDIGITS is not 0")
        self.code_identity = native("running identity not computable", artifacts.code_identity)
        require(self.code_identity == R.RUNNING_IDENTITY, "running identity differs")
        self.source_manifest_digest = native("running identity not computable",
                                             lambda: artifacts.digest(artifacts.source_manifest()))
        R.verify_formation()
        # A10.8 item 3: G0 asserts one numerical thread by the native check. Its
        # return value, which names the machine, enters no sealed file.
        runtime = native("numerical thread limit not verified as one", artifacts.runtime, 1)
        self.threads = [v["effective"] for v in runtime["threads_verified"]]
        if self.out is not None:
            # A10.3b: G0's destination rule names the same input roots as collect's.
            require_new_outside(self.out, self.inputs)
        # A1.6: the current stage 2 pin, with the instrument.
        self.pin = dict(self.inputs["registration"])
        native("registration pin not verified", artifacts.verify_registration, self.pin, instrument=tables_a10.NOMINAL)
        self.accepted = native("accepted identities not computable", accepted_identities)
        require(self.code_identity in self.accepted, "running identity differs")

    def end(self):
        from v3 import artifacts
        require(native("running identity not computable", artifacts.code_identity) == R.RUNNING_IDENTITY,
                "running identity differs")

    # ------------------------------------------------------------------ G1
    def producer(self, label, field, value):
        require(value in self.accepted, "producer identity not accepted")
        self.ledger.producer(label, field, value)

    def bind(self, label, path, entry, seal_required=True):
        """Section 2.3 item 1: the file's bytes hash to the inventory's sha256,
        and its seal to the inventory's seal."""
        document, sha = self.ledger.json(path, label)
        require(entry is not None, "published file not listed in its inventory")
        require(sha == entry["sha256"], "file hash differs from its inventory")
        if entry["seal"] is not None:
            sealed(document, "seal")
            require(document["sha256"] == entry["seal"], "seal differs from its inventory")
        if seal_required:
            sealed(document, "seal")
        return document, sha

    def load_inventory(self, label, path, authorized):
        document, sha = self.ledger.json(path, label)
        payload = sealed(document, "inventory seal")
        require(sha == authorized["file_sha256"] and document["sha256"] == authorized["seal"],
                "inventory differs from its authorized hash")
        inv = Inventory(payload)
        require(inv.verdict == "complete and consistent" and inv.findings == [] and inv.runs["all_checks_pass"] is True,
                "inventory verdict or checks")
        # A10.5: every inventory carries the running identity, in both modes;
        # membership in accepted_identities() suffices for none.
        require(inv.code_identity == self.code_identity, "inventory identity differs from the running identity")
        return inv, sha

    def load_spec(self, label, path):
        document, sha = self.ledger.json(path, label)
        spec = sealed(document, "spec seal")
        require(isinstance(spec, dict) and spec.get("schema") == "v3-registered-1" and type(spec.get("registered")) is bool,
                "spec schema")
        return document, spec, sha

    def bind_root(self, base, root, inv, spec_document, spec_sha, spec):
        """Section 2.3 items 1 and 2 for a run root; no output is opened."""
        from v3.artifacts import digest as native_digest
        require(spec_sha == inv.spec["file_sha256"] and spec_document["sha256"] == inv.spec["seal"],
                "spec differs from its inventory")
        _, manifest_sha = self.ledger.read(Path(root) / "manifest.json", base + "root/manifest.json")
        require(manifest_sha == spec_sha, "root manifest differs from the spec")
        mapping, voh_sha = self.ledger.json(Path(root) / "verified_output_hashes.json", base + "root/verified_output_hashes.json")
        require(isinstance(mapping, dict) and all(isinstance(k, str) and is_hash(v) for k, v in mapping.items()),
                "verified hash file malformed")
        require(voh_sha == inv.runs["verified_output_hashes_sha256"] and native_digest(mapping) == inv.runs["outputs_digest"],
                "verified hash file differs from its inventory")
        # A10.4: the inventory's jobs, records, outputs, identity_file_sha256,
        # manifest_file_sha256, paths and checkout_commit are recorded only and
        # compared with nothing. The root's identity.json is not opened.
        return mapping

    def bind_chain(self, f, labelled):
        """Section 2.3 item 3: the family chain."""
        ident, vr, a10 = f["identity"], f["validation_receipt"], f["a10_receipt"]
        require(isinstance(ident, dict) and all(k in ident for k in (
            "family_file_sha256", "table_seal_sha256", "receipt_file_sha256", "sidecar_file_sha256", "producing_commit",
            "code_hash")), "identity record malformed")
        require(ident["family_file_sha256"] == f["table_sha"] and ident["table_seal_sha256"] == f["table_doc"]["sha256"],
                "identity record does not bind the table")
        require(ident["receipt_file_sha256"] == f["validation_receipt_sha"]
                and ident["sidecar_file_sha256"] == f["cell_results_sha"], "identity record does not bind the receipt or sidecar")
        require(vr.get("schema") == "v3-A4-receipt-1" and vr.get("table_seal_sha256") == f["table_doc"]["sha256"]
                and vr.get("table_file_sha256") == f["table_sha"] and vr.get("calibration_sha256") == f["calibration_doc"]["sha256"]
                and vr.get("cell_results_sha256") == f["cell_results_sha"], "validation receipt does not bind the family")
        require(a10.get("table_sha256") == f["table_doc"]["sha256"]
                and a10.get("validation_receipt_sha256") == f["validation_receipt_sha"], "A10 receipt does not bind the family")
        if labelled:
            require(a10.get("labels_sha256") == f["labels_sha"], "A10 receipt does not bind the labels")
        table = f["table_doc"]["payload"]
        require(isinstance(table, dict) and isinstance(table.get("manifest"), dict)
                and table["manifest"].get("calibration_hash") == f["calibration_doc"]["sha256"],
                "table calibration differs from the calibration")

    def bind_identity(self, family, label, path, authorized):
        raw, sha = self.ledger.read(path, label)
        check_identity_record(family, raw, sha, self.fixture, authorized)
        return loads(raw), sha

    def load_family(self, family, base, files, inv, name_map, authorized):
        f = {"family": family}
        for name in sorted(files):
            if name in ("a16", "identity"):
                continue
            entry = inv.entry(name_map[name])
            label = base + "family/" + name
            if name == "admission_check" and family == "sqrt":
                # A1.12: INV-S does not list the sqrt admission check record; the
                # authorized-hash document binds it.
                # Rule question RQ-11: A8.1 gives the field for every run of
                # sqrt and A8.4 ties no family to a schema. Literal reading: the
                # authorized hash always binds it, and an inventory entry binds
                # it as well when the inventory has one.
                document, sha = self.ledger.json(files[name], label)
                sealed(document, "seal")
                require(sha == authorized["sqrt_admission_check_sha256"], "sqrt admission record differs from its authorized hash")
                if entry is not None:
                    require(sha == entry["sha256"] and document["sha256"] == entry["seal"], "file hash differs from its inventory")
            else:
                document, sha = self.bind(label, files[name], entry)
            f[name], f[name + "_sha"], f[name + "_doc"] = document["payload"], sha, document
        f["identity"], f["identity_sha"] = self.bind_identity(family, base + "family/identity", files["identity"], authorized)
        entry = inv.entry(name_map["identity"])
        require(entry is not None and entry["sha256"] == f["identity_sha"], "file hash differs from its inventory")
        return f

    def g1(self):
        from v3 import artifacts, tables_a10
        inputs = self.inputs
        specs = {}
        for family in self.arms_run:
            specs[family] = self.load_spec("arms/%s/spec" % family, inputs["arms"][family]["spec"])
        specs[MAIN] = self.load_spec("comparator/spec", inputs["comparator"]["spec"])
        self.fixture = decide_mode(inputs, [s[1]["registered"] for s in specs.values()])
        self.auth, self.auth_sha = load_authorized(self.ledger, inputs, self.fixture)
        auth = self.auth
        # A8.4: presence of the supplementary blocks, decided after the inventories.
        supplementary_expected = set()
        registries = set()
        for family in self.arms_run:
            arm, base = inputs["arms"][family], "arms/%s/" % family
            inv, inv_sha = self.load_inventory(base + "inventory", arm["inventory"], auth["inventories"][family])
            document, spec, spec_sha = specs[family]
            mapping = self.bind_root(base, arm["root"], inv, document, spec_sha, spec)
            self.producer(base + "spec", "code_hash", spec.get("code_hash"))
            # A10.8 item 7: where the inventory has a run_spec_family entry with
            # present true, pre_spec must name a file bound by it and D:294's
            # reconstruction applies. Otherwise no test beyond the collection's hash.
            entry = inv.entry("run_spec_family")
            if entry is not None:
                require(arm["pre_spec"] is not None, "pre-dispatch spec listed but not supplied")
                pre_document, _ = self.bind(base + "pre_spec", arm["pre_spec"], entry)
                require(pre_document["payload"] == {k: v for k, v in spec.items() if k != "pull_dispatch"}
                        and "pull_dispatch" in spec, "pre-dispatch spec differs from the final spec")
            elif arm["pre_spec"] is not None:
                self.ledger.read(arm["pre_spec"], base + "pre_spec")
            fam = self.load_family(family, base, arm["family"], inv, ARM_NAME_MAP, auth)
            calibration, calibration_sha = self.bind(base + "calibration", arm["calibration"], inv.entry("calibration"))
            fam["calibration_doc"], fam["calibration_sha"], fam["calibration_path"] = calibration, calibration_sha, arm["calibration"]
            self.bind_chain(fam, labelled=(family == "sqrt"))
            paths = tables_a10.STAGE2_PATHS[family]
            require(spec.get("a10_family_paths") == {"calibration_path": paths[0], "tables_path": paths[1]},
                    "spec family paths differ from the registered paths")
            a16 = arm["family"]["a16"]
            fam["a16_files"] = None
            if a16 is not None:
                if inv.schema == INV_2:
                    block = {"a16_family_record": inv.entry("a16_family_record"),
                             "a16_round_records": inv.entries("a16_round_records"),
                             "a16_round_admission_records": inv.entries("a16_round_admission_records"),
                             "a16_public_records": inv.entries("a16_public_records")}
                else:
                    supplementary_expected.add(family)
                    raw_block = auth["supplementary_records"].get(family)
                    require(isinstance(raw_block, dict) and set(raw_block) == SUPPLEMENTARY_KEYS
                            and all(isinstance(raw_block[k], list) for k in SUPPLEMENTARY_KEYS if k != "a16_family_record"),
                            "supplementary records block missing or malformed")
                    block = {k: (_entry(v) if k == "a16_family_record" else [_entry(x) for x in v]) for k, v in raw_block.items()}
                rounds = sorted(a16["rounds"])
                require(all(len(block[k]) == len(rounds) for k in block if k != "a16_family_record"),
                        "A16 records differ from the bound list")
                files = {"family_record": self.bind(base + "family/a16/family_record", a16["family_record"],
                                                    block["a16_family_record"]), "rounds": {}}
                for index, r in enumerate(rounds):
                    lists = {"round_record": "a16_round_records", "admission_record": "a16_round_admission_records",
                             "public": "a16_public_records"}
                    files["rounds"][r] = {k: self.bind("%sfamily/a16/rounds/%s/%s" % (base, r, k), a16["rounds"][r][k],
                                                       block[lists[k]][index]) for k in sorted(ROUND_KEYS)}
                fam["a16_files"] = files
            # MODE TERM 7 (A3.5 row 7): the spec pins.
            if not self.fixture:
                require(spec.get("registration") == self.pin, "spec registration differs from the pin")
                registries.add(spec.get("seed_registry_sha256"))
            for entry_root in arm["excluded_roots"]:
                # D:299, A9.3: the excluded root is recorded with the inventory's
                # reason and is never opened.
                require(entry_root.get("inventory_key") == "failed_attempt" and inv.failed_attempt is not None,
                        "excluded root not named by its inventory")
                self.excluded.append({"family": family, "path": inv.failed_attempt["path"],
                                      "reason": inv.failed_attempt["not_run_reason"]})
            fam.update(inventory=inv, inventory_sha=inv_sha)
            self.fam[family] = fam
            self.src[family] = {"spec": spec, "spec_sha": spec_sha, "root": Path(arm["root"]), "base": base, "voh": mapping}
        require(set(auth["supplementary_records"]) == supplementary_expected, "supplementary records block missing or malformed")
        # MODE TERM 7 (A3.5 row 7): the seed registry, when any arm ran.
        if not self.fixture and self.arms_run:
            check_seed_registry(self.ledger, registries)
        # The comparator (A1.2): its own root and its own binding.
        c, base = inputs["comparator"], "comparator/"
        inv, inv_sha = self.load_inventory(base + "binding", c["binding"], auth["inventories"]["comparator"])
        document, spec, spec_sha = specs[MAIN]
        mapping = self.bind_root(base, c["root"], inv, document, spec_sha, spec)
        self.producer(base + "spec", "code_hash", spec.get("code_hash"))
        fam = self.load_family(NOMINAL, base, c["family"], inv, COMPARATOR_NAME_MAP, auth)
        calibration, calibration_sha = self.bind(base + "calibration", c["calibration"], inv.entry("calibration"))
        fam["calibration_doc"], fam["calibration_sha"], fam["calibration_path"] = calibration, calibration_sha, c["calibration"]
        self.bind_chain(fam, labelled=True)
        expected_table = Path(c["execution_simulation"]) / tables_a10.STAGE2_PATHS["nominal"][1]
        try:
            same = os.path.samefile(c["family"]["table"], expected_table)
        except OSError:
            same = False
        require(same, "nominal table is not the file at its registered path")
        # MODE TERM 7 (A3.5 row 7): the comparator's own pin.
        if not self.fixture:
            check_comparator_pin(spec.get("registration"), inv.registration_pin)
        fam.update(inventory=inv, inventory_sha=inv_sha, a16_files=None)
        self.fam[NOMINAL] = fam
        self.src[MAIN] = {"spec": spec, "spec_sha": spec_sha, "root": Path(c["root"]), "base": base, "voh": mapping}
        for family, f in self.fam.items():
            # A10.6 item 3: the producer fields G1 tests, and no other. A
            # calibration's code_hash is recorded and compared with nothing.
            base = "comparator/" if family == NOMINAL else "arms/%s/" % family
            self.producer(base + "family/table", "code_hash", f["table"].get("code_hash"))
            self.producer(base + "family/table", "manifest.a10.producer_code_hash",
                          (f["table"]["manifest"].get("a10") or {}).get("producer_code_hash"))
            self.producer(base + "family/validation_receipt", "producer_code_hash", f["validation_receipt"].get("producer_code_hash"))
            self.producer(base + "family/a10_receipt", "producer_code_hash", f["a10_receipt"].get("producer_code_hash"))
            embedded = f["a10_receipt"].get("validation_receipt")
            require(isinstance(embedded, dict) and isinstance(embedded.get("payload"), dict),
                    "A10 receipt does not bind the family")
            self.producer(base + "family/a10_receipt", "validation_receipt.producer_code_hash",
                          embedded["payload"].get("producer_code_hash"))
            self.producer(base + "family/identity", "code_hash", f["identity"].get("code_hash"))
            if "labels" in f:
                self.producer(base + "family/labels", "code_hash", f["labels"].get("code_hash"))
            payload = f["calibration_doc"]["payload"]
            f["calibration_code_hash"] = payload.get("code_hash") if isinstance(payload, dict) else None
        # Not-run evidence is bound by the authorized-hash document (G9 reads it).
        for family in self.arms_not_run:
            evidence, bound = inputs["arms"][family]["evidence"], auth["not_run_evidence"][family]
            require(isinstance(bound, dict) and set(bound) == set(evidence), "not-run evidence not bound")
            documents = {}
            for name in sorted(evidence):
                paths = evidence[name] if isinstance(evidence[name], list) else [evidence[name]]
                hashes = bound[name] if isinstance(evidence[name], list) else [bound[name]]
                require(isinstance(hashes, list) and len(hashes) == len(paths), "not-run evidence not bound")
                loaded = []
                for index, (path, expected) in enumerate(zip(paths, hashes)):
                    label = "arms/%s/evidence/%s" % (family, name) + ("/%d" % index if isinstance(evidence[name], list) else "")
                    doc, sha = self.ledger.json(path, label)
                    require(sha == expected, "not-run evidence not bound")
                    loaded.append((sealed(doc, "seal"), sha))
                documents[name] = loaded if isinstance(evidence[name], list) else loaded[0]
            self.not_run[family] = {"evidence": documents}
        # A10.3b item 5: every collected file is read in every pass.
        for label, path in file_leaves(inputs):
            if label not in self.ledger.entries:
                self.ledger.read(path, label)

    # ------------------------------------------------------------------ G2
    def g2(self):
        self.spec_records, self.cells, ids, seeds = {}, {}, [], []
        for component in self.arms_run + [MAIN]:
            spec = self.src[component]["spec"]
            layout = None
            if self.fixture:
                layout = self.auth["fixture_layout"]["comparator" if component == MAIN else component]
            if component != MAIN:
                require(spec.get("code_hash") == self.code_identity, "arm spec was not made at the running identity")
            records, cells = spec_structure(component, spec, fixture=self.fixture, layout=layout)
            self.spec_records[component], self.cells[component] = records, cells
            self.src[component]["jobs"] = {j["id"]: j for j in spec["jobs"]}
            ids += [j["id"] for j in spec["jobs"]]
            seeds += [j["seed"] for j in spec["jobs"]]
        # Across all specs read: ids pairwise distinct and seeds pairwise distinct.
        require(len(set(ids)) == len(ids), "duplicate job id")
        require(len(set(seeds)) == len(seeds), "duplicate job seed")
        from v3 import tables_a10
        for component in self.arms_run + [MAIN]:
            paths = tables_a10.STAGE2_PATHS[FAMILY_OF[component]]
            for job in self.src[component]["spec"]["jobs"]:
                cfg = job["config"]
                # Section 2.3 item 4: runs to family (A1.2 for the comparator).
                require(cfg.get("calibration_path") == paths[0] and cfg.get("tables_path") == paths[1]
                        and isinstance(cfg.get("phase"), str), "job path strings differ from the registered paths")

    # ------------------------------------------------------------------ G3
    def g3(self):
        """The contributing-run map, from the specs alone, sealed to a
        temporary file before any output is opened (D:352, A8.5)."""
        from v3.artifacts import digest as native_digest
        self.maps, self.map_files = {}, {}
        by_id = {c: {r["job_id"]: r for r in self.spec_records[c]} for c in self.spec_records}
        for component in R.COMPONENTS:
            quantities, runs, specs = {}, {}, {}

            def keys(source, ids):
                return ["%s/%s" % (source, i) for i in ids]

            for entry in R.for_component(component):
                arm, ran = entry["arm"], entry["arm"] in self.arms_run
                arm_cells = self.cells[arm][entry["identity"]] if ran else {k: [] for k in self.cells[MAIN][entry["identity"]]}
                nominal_cells = self.cells[MAIN][entry["identity"]]
                for key, kind, rr in R.quantity_keys(entry):
                    if kind in ("survival", "survival_difference"):
                        members = keys(arm, arm_cells[rr])
                        if kind == "survival_difference":
                            members += keys(MAIN, nominal_cells[rr])
                    else:
                        members = [k for v in arm_cells.values() for k in keys(arm, v)]
                        members += [k for v in nominal_cells.values() for k in keys(MAIN, v)]
                    require(key not in quantities, "quantity key collision")
                    quantities[key] = sorted(members)
            for members in quantities.values():
                for key in members:
                    source, job_id = key.split("/", 1)
                    r = by_id[source][job_id]
                    runs[key] = {"component": source, "phase": self.src[source]["jobs"][job_id]["config"]["phase"],
                                 "category": r["category"], "grid": r["grid"], "rr": r["rr"], "alpha": r["alpha"],
                                 "capability": r["capability"]}
            for source in sorted({k.split("/", 1)[0] for k in runs}):
                specs[source] = native_digest(self.src[source]["spec"])
            payload = {"schema": "a10-stage2-contributing-runs-1",
                       "basis": "specs only; sealed before opening outputs", "specs": specs,
                       "runs": dict(sorted(runs.items())), "quantities": dict(sorted(quantities.items()))}
            data = sealed_bytes(payload)
            with tempfile.NamedTemporaryFile(prefix="contributing_runs_", suffix=".sealed", delete=False) as stream:
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
                self.map_files[component] = stream.name
            self.maps[component] = {"payload": payload, "bytes": data}
        self.contributing = sorted(set().union(*(m["payload"]["runs"] for m in self.maps.values())))

    def cleanup(self):
        for path in getattr(self, "map_files", {}).values():
            try:
                os.unlink(path)
            except OSError:
                pass

    # ------------------------------------------------------------- G4, G5
    def g4_g5(self):
        from v3.gates import fire_from_run
        hashers = {c: hashlib.sha256(b"a10-stage2-ladder-1") for c in R.COMPONENTS}
        member = {c: self.maps[c]["payload"]["runs"] for c in R.COMPONENTS}
        self.runs = {}
        for key in self.contributing:
            source, job_id = key.split("/", 1)
            src = self.src[source]
            job, base = src["jobs"][job_id], src["base"]
            phase = job["config"]["phase"]
            record_rel = "%s/records/%s.json" % (phase, job_id)
            output_rel = "%s/outputs/%s.json" % (phase, job_id)
            record, _ = self.ledger.json(src["root"] / phase / "records" / (job_id + ".json"), base + "root/" + record_rel)
            require(isinstance(record, dict) and record.get("status") == "complete" and record.get("job") == job
                    and record.get("code_hash") == src["spec"].get("code_hash"), "completion record does not match its job")
            raw, sha = self.ledger.read(src["root"] / phase / "outputs" / (job_id + ".json"), base + "root/" + output_rel)
            require(sha == record.get("output_hash"), "output hash differs from its completion record")
            require(sha == src["voh"].get(output_rel), "output hash differs from the verified hash file")
            for component in R.COMPONENTS:
                if key in member[component]:
                    hashers[component].update(raw)
            output = loads(raw)
            del raw
            require(isinstance(output, dict) and output.get("job") == job
                    and output.get("code_hash") == record["code_hash"], "output does not match its job")
            self.producer(base + "root/" + output_rel, "code_hash", output["code_hash"])
            result = structure(job, output)
            fired = native("capability path invalid", fire_from_run, output)
            flat = dict(flat_spec(source, job), final_population=result["final_population"], fired=bool(fired))
            has_field = "a13_decision_incidence" in result
            missing_row = any(inc.MISSING in s["unavailable_rules"].values() for s in result["diagnostics"]
                              if "unavailable_rules" in s)
            self.runs[key] = {"flat": flat, "has_field": has_field, "recorded": result.get("a13_decision_incidence"),
                              "derived": inc.try_derive(result), "missing_row": missing_row}
            del output, result
        for source in self.arms_run:
            # For an arm, all of its jobs are contributing, so the whole root is covered.
            expected = {"%s/outputs/%s.json" % (j["config"]["phase"], i) for i, j in self.src[source]["jobs"].items()}
            require(set(self.src[source]["voh"]) == expected, "verified hash file does not cover exactly the spec's outputs")
        self.keys = {c: hashers[c].digest() for c in R.COMPONENTS}

    # ------------------------------------------------------------------ G6
    def passed_record(self, payload, scope, rows, residual, admission):
        require(isinstance(payload, dict) and payload.get("schema") == CHECK_SCHEMA and payload.get("scope") == scope,
                "admission record schema or scope differs")
        require(payload.get("outcome") == "passed", "binding admission record did not pass")
        require(payload.get("primary_rows") == len(rows) and payload.get("cap") == len(rows) // 1000
                and payload.get("residual_count") == len(residual) and isinstance(payload.get("residual_rows"), list)
                and sorted(payload["residual_rows"]) == residual, "admission record disagrees with the loaded table")
        require(payload.get("admitted_set_sha256") == admission.get("admitted_set_sha256"),
                "admission record admitted set differs from the binding")

    def g6(self):
        from v3 import calibration as native_calibration
        from v3 import tables_a10, validation_extension_a16 as a16_native
        from v3.artifacts import digest as native_digest
        from v3.production_tables import ProductionTables
        for family in self.arms_run + [NOMINAL]:
            f = self.fam[family]
            instrument = tables_a10.family_instrument(family)
            seal = f["calibration_doc"]["sha256"]
            require((f["calibration_sha"], seal) == calibration_pins(family, self.fixture),
                    "calibration differs from its frozen pin")
            native("calibration refused by the native loader", native_calibration.load_calibration, f["calibration_path"],
                   registered=True, instrument=instrument.declaration())
            tables = native("family table refused by the native loader", ProductionTables, f["table_doc"],
                            calibration_hash=seal, registered=True, receipt=f["a10_receipt_doc"])
            native("family table refused by require_a10", tables.require_a10, instrument)
            manifest = tables.payload["manifest"]
            check_marker(manifest, self.fixture)
            admission = manifest.get("a13_admission")
            # An absent binding is case 3, never case 2 (D:361).
            require(isinstance(admission, dict) and isinstance(admission.get("rows"), dict), "a13 admission binding absent")
            require((manifest.get("a10") or {}).get("family") == family, "table family differs")
            rows = tables.rows
            require(len(rows) == R.PRIMARY_ROWS[family] and len(rows) // 1000 == R.CAPS[family]
                    and admission.get("primary_rows") == len(rows), "primary row count differs")
            residual = sorted(k for k, r in rows.items() if r["status"] == "not_estimable")
            admitted = set(admission["rows"])
            scope, vr, error = admission.get("scope"), f["validation_receipt"], {}
            if scope == A13_SCOPE:
                require(family != NOMINAL, "admission scope not allowed for the family")
                require("a16" not in admission and f["a16_files"] is None, "A16 provenance misplaced")
                record = f["admission_check"]
                self.passed_record(record, A13_SCOPE, rows, residual, admission)
                require(record.get("plan_hash") == vr.get("plan_hash"), "admission plan hash differs from the receipt")
                rounds_used, record_sha, refusals = 0, f["admission_check_sha"], None
            elif scope in A16_SCOPES:
                q = A16_SCOPES[scope]
                require(family != NOMINAL, "admission scope not allowed for the family")
                bound, files = admission.get("a16"), f["a16_files"]
                require(isinstance(bound, dict) and files is not None
                        and sorted(files["rounds"]) == ["r%d" % i for i in range(1, q + 1)], "A16 records differ from the bound round")
                refusals, rounds = vr.get("refusals"), vr.get("a16_rounds")
                require(isinstance(refusals, dict) and isinstance(refusals.get("original"), dict)
                        and isinstance(rounds, dict) and isinstance(rounds.get("r%d" % q), dict), "A16 receipt malformed")
                original = f["admission_check"]
                require(original.get("outcome") == "refused" and original.get("scope") == A13_SCOPE
                        and original.get("plan_hash") == vr.get("plan_hash")
                        and f["admission_check_sha"] == refusals["original"].get("admission_record_sha256"),
                        "original refusal not preserved")
                if q == 2:
                    first_doc, first_sha = files["rounds"]["r1"]["admission_record"]
                    require(first_doc["payload"].get("outcome") == "refused"
                            and first_sha == refusals.get("round1_admission_record_sha256"), "round 1 refusal not preserved")
                record_doc, record_sha = files["rounds"]["r%d" % q]["admission_record"]
                record = record_doc["payload"]
                self.passed_record(record, scope, rows, residual, admission)
                require(record.get("plan_hash") == bound.get("plan_hash"), "A16 admission plan hash differs from the bound plan")
                family_record = files["family_record"][0]["payload"]
                round_record = files["rounds"]["r%d" % q]["round_record"][0]["payload"]
                require(family_record.get("published_round") == q and family_record.get("terminal") is None,
                        "A16 family record is not published at the bound round")
                try:
                    identities = (a16_native.admission_identity(record), a16_native.family_identity(family_record),
                                  a16_native.round_identity(round_record))
                    classified = record["classifications_sha256"] == native_digest(record["classifications"])
                except (KeyError, TypeError):
                    raise Refused("A16 provenance differs from the on-disk records") from None
                require(identities == (bound.get("admission_record_sha256"), bound.get("family_record_sha256"),
                                       bound.get("round_record_sha256")) and classified
                        and bound.get("family") == family == family_record.get("family") == round_record.get("family") == record.get("family")
                        and bound.get("round") == q == round_record.get("round") == record.get("round")
                        and bound.get("plan_hash") == round_record.get("plan_hash"),
                        "A16 provenance differs from the on-disk records")
                require(record_sha == rounds["r%d" % q].get("admission_record_sha256")
                        and rounds["r%d" % q].get("plan_hash") == bound.get("plan_hash")
                        and files["rounds"]["r%d" % q]["public"][1] == rounds["r%d" % q].get("public_file_sha256"),
                        "A16 receipt does not bind the round records")
                rounds_used = q
                error = {k: record.get(k) for k in ERROR_FIELDS}
                error["statement"] = R.A16_STATEMENT
            elif scope == A14_SCOPE:
                # A2.1: this scope on any other family refuses.
                require(family == NOMINAL, "admission scope not allowed for the family")
                require("a16" not in admission, "A16 provenance misplaced")
                record, record_sha = f["admission_check"], f["admission_check_sha"]
                self.passed_record(record, A14_SCOPE, rows, residual, admission)
                a14_round, a13_round, refusals = vr.get("a14_round"), vr.get("a13_round"), vr.get("refusals")
                a14 = manifest.get("a14")
                require(isinstance(a14_round, dict) and isinstance(a13_round, dict) and isinstance(refusals, dict)
                        and isinstance(a14, dict), "A14 receipt malformed")
                require(record.get("plan_hash") == a14_round.get("plan_hash"), "A14 admission plan hash differs from the receipt")
                require(record_sha == a14_round.get("admission_record_sha256"), "A14 receipt does not bind the admission record")
                refusal, refusal_sha = f["a13_round_admission"], f["a13_round_admission_sha"]
                require(refusal_sha == refusals.get("a13_admission_record_sha256") == a13_round.get("admission_record_sha256"),
                        "A13 refusal differs from the receipt")
                require(refusal.get("outcome") == "refused", "A13 refusal does not read refused")
                check_a13_refusal(refusal_sha, self.fixture, self.auth)
                require(a14.get("plan_hash") == a14_round.get("plan_hash") == record.get("plan_hash")
                        and a14.get("a13_plan_hash") == a13_round.get("plan_hash") == refusal.get("plan_hash")
                        and a14.get("original_plan_hash") == vr.get("plan_hash") and is_hash(vr.get("plan_hash")),
                        "A14 publication plan hashes differ")
                require(f["a14_public_record_sha"] == a14_round.get("public_file_sha256")
                        and f["a13_public_record_sha"] == a13_round.get("public_file_sha256"),
                        "A14 receipt does not bind the public records")
                rounds_used = 2
                error = {k: record[k] for k in ERROR_FIELDS if k in record}
            else:
                # A10.8 item 5: nominal passes only under A10_nominal_after_A14, an
                # arm only under the A13 scope or an A16 scope; A10_nominal_after_A13
                # and any unlisted scope refuse for every family.
                require(False, "admission scope not allowed for the family")
            # Section 4.2: the family's incidence state.
            jobs = [self.src[c]["jobs"][k.split("/", 1)[1]] for c in [MAIN if family == NOMINAL else family]
                    for k in self.contributing if k.split("/", 1)[0] == c]
            if admitted:
                case = 1
            else:
                case = 2
                contexts = set(native("native context builder refused", tables_a10.contexts, family))
                declaration = instrument.declaration()
                expected = native("native context builder refused", lambda: tables_a10.expected_keys(
                    tables_a10.build_jobs(family, tables_a10.STAGE2_PATHS[family][0]), f["calibration_doc"]))
                from v3.study import capabilities
                covered = all((j["config"]["model"]["reproduction_rate"], j["config"]["model"]["alpha"], c) in contexts
                              for j in jobs for c in native("native context builder refused", capabilities,
                                                            j["config"]["model"]["successor_capability"]))
                conditions = (admission["rows"] == {} and admission.get("admitted_set_sha256") == native_digest({})
                              and admission.get("primary_rows") == len(rows) and not residual
                              and record.get("outcome") == "passed" and record.get("residual_count") == 0)
                require(conditions, "no-admitted family condition failed")
                require(set(rows) == expected and covered, "no-admitted family lacks context coverage")
                require(all(j["config"]["model"]["instrument"] == declaration for j in jobs),
                        "no-admitted family job instrument differs")
                # MODE TERM 5 (A3.5 row 5), restated by A1.12 for case 2: a
                # registered job's model carries no n_agents.
                if not self.fixture:
                    require(not any("n_agents" in j["config"]["model"] for j in jobs), "fixture-only model key")
            # Rule question RQ-17: D:518 lists the fields of family.<name>.admission
            # without their sources. Literal reading with A3.4: primary_rows, cap
            # and residual_count from the binding admission record, admitted_rows
            # from the loaded table's binding, the record's file sha256.
            f.update(tables=tables, manifest=manifest, admitted=admitted, case=case, scope=scope, refusals=refusals,
                     binding={"scope": scope, "admitted_set_sha256": admission.get("admitted_set_sha256"),
                              "a16": {k: v for k, v in (admission.get("a16") or {}).items()
                                      if k in ("family", "round", "plan_hash", "family_record_sha256",
                                               "round_record_sha256", "admission_record_sha256")} or None},
                     admission={"scope": scope, "primary_rows": record["primary_rows"], "cap": record["cap"],
                                "residual_count": record["residual_count"], "admitted_rows": len(admitted),
                                "rounds_used": rounds_used, "admission_record_sha256": record_sha},
                     family_error=error if rounds_used > 0 else {})

    # ------------------------------------------------------------------ G7
    def g7(self):
        from v3 import tables_a10
        for family in self.arms_run + [NOMINAL]:
            f, receipt = self.fam[family], self.fam[family]["a10_receipt"]
            if family != NOMINAL:
                require(self.src[family]["spec"].get("a10_labels_policy") == tables_a10.STAGE2_LABELS_POLICY[family],
                        "spec labels policy differs")
            if family in (NOMINAL, "sqrt"):
                require(receipt.get("schema") == "v3-A10-table-receipt-1" and receipt.get("labels_sha256") == f["labels_sha"],
                        "strict receipt or labels binding differs")
                f["labels_value"] = {"policy": "a5_labels_required", "labels_sha256": f["labels_sha"]}
            else:
                require(receipt.get("schema") == tables_a10.NO_LABEL_RECEIPT_SCHEMA and receipt.get("family") == family
                        and receipt.get("labels_policy") == tables_a10.NO_LABEL_AUTHORITY and "labels" not in receipt
                        and "labels_sha256" not in receipt
                        and receipt.get("calibration_sha256") == f["calibration_doc"]["sha256"],
                        "no-label receipt differs")
                f["labels_value"] = {"policy": "no_a5_labels_a16", "disclosure": R.NO_LABEL_DISCLOSURE}

    # ------------------------------------------------------------------ G8
    def g8(self):
        self.per_run = {}
        for key in self.contributing:
            run = self.runs[key]
            case = self.fam[FAMILY_OF[key.split("/", 1)[0]]]["case"]
            self.per_run[key] = inc.per_run(case, run["has_field"], run["recorded"], run["derived"], run["missing_row"])

    # ------------------------------------------------------------------ G9
    def g9(self):
        """Section 3.6 with A1.7, A2.9, A8.2 and A8.8: a not-run arm."""
        from v3 import tables_a10
        from v3.validation_extension_a16 import family_record_path
        root = Path(self.inputs["execution_simulation"])
        for family in self.arms_not_run:
            evidence = self.not_run[family]["evidence"]
            refused, _ = evidence["refused_admission_record"]
            require(isinstance(refused, dict) and refused.get("schema") == CHECK_SCHEMA and refused.get("outcome") == "refused",
                    "not-run evidence does not read refused")
            target = root / tables_a10.STAGE2_PATHS[family][1]
            record_path = root / family_record_path(tables_a10.STAGE2_PATHS[family][1])
            if "a16_family_record" in evidence:
                record, _ = evidence["a16_family_record"]
                require(isinstance(record, dict) and record.get("family") == family, "not-run family record names another family")
                # A2.9: neither a terminal latch nor a publication has no not-run form.
                # A10.8 item 8: the family record names the arm, and the refused
                # record and every round admission record read ``outcome:
                # "refused"``. No number of round records is inferred.
                require(isinstance(record.get("terminal"), dict) and record.get("published_round") is None,
                        "not-run family record is not terminal")
                reason = record["terminal"].get("reason")
                require(all(isinstance(r, dict) and r.get("outcome") == "refused" for r, _ in evidence["a16_round_admission_records"]),
                        "not-run evidence does not read refused")
            else:
                record, _ = evidence["closeout_record"]
                require(isinstance(record, dict) and set(record) == CLOSEOUT_KEYS and record["schema"] == CLOSEOUT_SCHEMA,
                        "closeout record schema or keys")
                require(record["family"] == family and record["status"] == "not run", "closeout record names another arm or status")
                require(record["a16_entered"] is False, "closeout record reads A16 entered")
                require(not record_path.exists(), "A16 family record exists beside a closeout")
                reason = record["reason"]
                bound = record["refused_admission_record"]
                require(isinstance(bound, dict) and bound.get("sha256") == evidence["refused_admission_record"][1],
                        "closeout record does not bind the refused record")
                require(record["no_other_run_root_of_the_family_exists"] is True, "closeout record does not exclude other run roots")
            require(isinstance(reason, str) and reason != "", "not-run reason missing")
            # The contradiction check (A1.7, A2.9), whatever the operator's input supplied.
            require(not target.exists(), "published table exists for a not-run arm")
            for pattern_root in (root / "v3/runs/a10_stage2/runs" / family, root / "v3/runs/a10_stage2" / family / "runs_run"):
                found = any(p.is_file() for p in pattern_root.glob("*/records/*")) if pattern_root.is_dir() else False
                require(not found, "run records exist for a not-run arm")
            self.not_run[family]["reason"] = reason

    def run(self):
        self.g0()
        self.g1()
        self.g2()
        self.g3()
        self.g4_g5()
        self.g6()
        self.g7()
        self.g8()
        self.g9()
        return self
