"""The comparison layer (section 1.6), the outputs and sealing (section 5), the
stage hash ladder (A6.4a, A8.7) and the A5 disclosures (A1.5, A2.7, A9.2).

The comparison layer exposes no tail argument: level, tail, seed, resample
count and grid come only from the frozen registry (A1.9). Every helper call is
wrapped so that no warning can reach a stream (A1.4, A2.8).
"""
import contextlib
import hashlib
import hmac
import math
import warnings
from pathlib import Path

from . import incidence as inc
from . import registry as R
from .base import CREATED, document_bytes, fkey, norm, sealed_bytes, write_once
from .common import COMPUTATION_STARTED, Refused, json_safe, require
from .gates import FAMILY_OF, MAIN, NOMINAL, mode_name, native

FILES = ("reading.json", "values.json", "contributing_runs.json", "incidence_per_run.json", "LADDER.json")
KEY_CHECK = {"check": "a10-stage2-ladder-1 key check"}


def source_of(family):
    return MAIN if family == NOMINAL else family


@contextlib.contextmanager
def quiet():
    import numpy
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        with numpy.errstate(all="ignore"):
            yield


def compare(identity, arm_cells, nominal_cells):
    """One registered comparison, by its registry identity. Returns the native
    helper's full result dict."""
    from v3 import reading_a6
    e = R.BY_IDENTITY[identity]
    with quiet():
        if e["kind"] == "boundary":
            return reading_a6.compare_boundary(arm_cells, nominal_cells, grid=tuple(e["grid_values"]),
                                               resamples=e["resamples"], seed=e["seed"], sigma_variant=e["sigma_variant"],
                                               alpha=e["level_alpha"], strict=True,
                                               undefined_resample_tail=e["undefined_tail"])
        return reading_a6.compare_capstar(arm_cells, nominal_cells, e["alpha"], resamples=e["resamples"],
                                          seed=e["seed"], alpha=e["level_alpha"], strict=True)


def survival_differences(identity, arm_cells, nominal_cells):
    """Descriptive, no verdict: on the boundary comparison's cells (D:175)."""
    from v3 import reading_a6
    e = R.BY_IDENTITY[identity]
    require(e["kind"] == "boundary", "survival differences need a boundary comparison")
    with quiet():
        return reading_a6.survival_differences(arm_cells, nominal_cells, resamples=e["resamples"], seed=e["seed"])


def comparison_fields(result):
    """The ``values.json`` fields of D:507-508 with A1.8's nulls."""
    boundary = result["kind"] == "boundary"
    return {"estimate": json_safe(result.get("difference")), "interval": json_safe(result.get("interval")),
            "verdict": result["verdict"],
            "undefined_share": result.get("undefined_resample_fraction") if boundary else None,
            "undefined_tail": result["undefined_resample_tail"] if boundary else None,
            "level_alpha": result["bonferroni_alpha"], "reason": result.get("reason")}


def point_fields(result):
    """D:509-510."""
    if result["kind"] == "boundary":
        return {"arm": json_safe(result["arm_boundary"]), "nominal": json_safe(result["nominal_boundary"])}
    return {side: {"category_index": result[name]["step"], "censored": result[name]["censored"]}
            for side, name in (("arm", "arm_cap_star"), ("nominal", "nominal_cap_star"))}


def wilson(count, n):
    """Section 8's Wilson interval at z = 2 (D:511; the stage 1 reader's
    ``against_v2.wilson``, copied)."""
    p = count / n
    d = 1 + 4 / n
    center = (p + 2 / n) / d
    half = 2 * math.sqrt(p * (1 - p) / n + 1 / n**2) / d
    return [max(0., center - half), min(1., center + half)]


def survival_fields(cell):
    values = [int(v) for v in cell]
    n, count = len(values), sum(v >= 30 for v in values)
    return {"n": n, "count": count, "rate": count / n, "wilson": wilson(count, n)}


def cells_structure(arm_cells, nominal_cells):
    """A6.4a: the ``cells`` rung structure."""
    def side(cells):
        return {fkey(k): [int(v) for v in values] for k, values in cells.items()}
    return {"arm": side(arm_cells), "comparator": side(nominal_cells)}


def rung(key, structure):
    """A6.4a: ``HMAC-SHA256(K, canonical(structure))`` after the value mapping."""
    from v3.artifacts import canonical
    return hmac.new(key, canonical(norm(structure)), hashlib.sha256).hexdigest()


def ladder_bytes(component, key, structures):
    rungs = {"key/check": rung(key, KEY_CHECK)}
    rungs.update({name: rung(key, structure) for name, structure in structures.items()})
    return sealed_bytes({"schema": "a10-stage2-ladder-1", "component": component, "rungs": rungs})


class Disclosures:
    """A1.5 and A2.7: per job, the configured set of looked-up rows, and from
    the hash-bound label records the rows with a violation. No run output value
    enters."""

    def __init__(self, gates):
        self.gates, self.index, self.violations, self.cache = gates, {}, {}, {}
        for family in [f for f in ("sqrt",) if f in gates.arms_run] + [NOMINAL]:
            f = gates.fam[family]
            index = {}
            for key, row in f["tables"].rows.items():
                s = row["scoring"]
                context = (row["kernel_hash"], float(s["alpha"]), round(float(s["capability"]), 12),
                           float(s.get("kappa", 8)), s.get("k_star"), s.get("g"))
                index.setdefault(context, []).append(key)
            self.index[family] = index
            rows = f["labels"].get("rows")
            require(isinstance(rows, list), "label record malformed")
            violations = {}
            for row in rows:
                try:
                    if row["violation"]:
                        violations[row["row_key"]] = {"row": row["row_key"], "violated_cells": row["violation"],
                                                      "total_exposure": row["violation_exposure_total"]}
                except (KeyError, TypeError):
                    raise Refused("label record malformed") from None
            self.violations[family] = violations

    def rows(self, family, job):
        if family not in self.index:
            return {}
        from v3.context import Context
        from v3.study import capabilities
        model = job["config"]["model"]
        instrument = model["instrument"]
        crowding = model.get("crowding", "total")
        signature = (family, model["reproduction_rate"], model["alpha"], model["successor_capability"],
                     model.get("kappa", 8.0), crowding, instrument["k_star"], instrument["g"])
        if signature not in self.cache:
            found = {}
            for capability in capabilities(model["successor_capability"]):
                kernel = {"reproduction_rate": model["reproduction_rate"], "capability": capability,
                          "instrument": dict(instrument)}
                if crowding != "total":
                    kernel["crowding"] = crowding
                kernel_hash = Context.build(kernel, self.gates.fam[family]["calibration_doc"]).kernel_hash
                context = (kernel_hash, float(model["alpha"]), round(float(capability), 12),
                           float(model.get("kappa", 8.0)), instrument["k_star"], instrument["g"])
                for key in self.index[family].get(context, ()):
                    if key in self.violations[family]:
                        found[key] = self.violations[family][key]
            self.cache[signature] = found
        return self.cache[signature]

    def quantity(self, keys):
        found = {}
        for key in keys:
            source, job_id = key.split("/", 1)
            found.update(native("disclosure rows not computable", self.rows, FAMILY_OF[source],
                                self.gates.src[source]["jobs"][job_id]))
        rows = [found[k] for k in sorted(found)]
        # A9.2: true exactly when disclosure_rows is not empty.
        return {"disclosure_rows": rows, "claims_conditional_on_violations": bool(rows)}


def prepare(gates, component, disclosures):
    """Everything that needs no estimator, done for every component before the
    first helper call: the flat records, the cells of every comparison by the
    native selector (a cell whose count differs raises there, D:127), the
    disclosures and the named complement of the family."""
    from v3 import reading_a6
    family_name = R.FAMILY_OF_COMPONENT[component]
    mapping = gates.maps[component]["payload"]
    flats, cells = {}, {}
    for source in sorted({k.split("/", 1)[0] for k in mapping["runs"]}):
        # Records are sorted by job_id before the helpers build cells (D:127).
        flats[source] = sorted((gates.runs[k]["flat"] for k in mapping["runs"] if k.split("/", 1)[0] == source),
                               key=lambda r: r["job_id"])
    for entry in R.for_component(component):
        arm = entry["arm"]
        if arm in gates.arms_not_run:
            continue
        # MODE TERM 2 (A3.5 row 2): seeds per cell, as G2 applied them.
        if gates.fixture:
            arm_seeds = gates.auth["fixture_layout"][arm]["seeds_per_cell"]
            comparator_seeds = gates.auth["fixture_layout"]["comparator"]["seeds_per_cell"]
        else:
            arm_seeds, comparator_seeds = entry["arm_seeds"], entry["comparator_seeds"]
        boundary = entry["kind"] == "boundary"
        arm_cells, nominal_cells = native(
            "native cell selection refused", reading_a6.arm_and_comparator_cells, flats[arm], flats[MAIN],
            "boundary" if boundary else "cap_star", grid=tuple(entry["grid_values"]) if boundary else reading_a6.R1_GRID,
            arm_filters=entry["arm_filters"], comparator_filters=entry["comparator_filters"],
            alpha=entry["alpha"] if not boundary else reading_a6.R1_ARM_ALPHA, arm_seeds=arm_seeds,
            comparator_seeds=comparator_seeds)
        cells[entry["identity"]] = (arm_cells, nominal_cells, arm_seeds, comparator_seeds)
    disclosure = {key: disclosures.quantity(keys) for key, keys in mapping["quantities"].items()}
    # D:182 and D:536: the complement of the family is named, never computed.
    if component == "A10":
        complement = sorted(R.identity("A10arm", "boundary", arm) for arm in R.STAGE1_A10_ARMS)
        complement += sorted(R.identity("A10arm", "cap_star", arm, a) for arm in R.STAGE1_A10_ARMS for a in R.ALPHAS)
    else:
        corners = ["weight_corner_k0.75_t0.25", "weight_corner_k0.75_t0.75", "weight_corner_k8_t0.25", "weight_corner_k8_t0.75"]
        complement = sorted(R.identity("A6", "boundary", arm) for arm in corners + ["horizon"])
        complement += sorted(R.identity("A6", "cap_star", arm, a) for arm in corners for a in R.ALPHAS)
    require(len(complement) + len(R.for_component(component)) == R.FAMILY_SIZE[family_name], "family size differs")
    return {"flats": flats, "cells": cells, "disclosure": disclosure, "complement": complement}


def component_reading(gates, component, prepared):
    """Compute one component. Returns the five files' bytes, by name."""
    family_name = R.FAMILY_OF_COMPONENT[component]
    mapping = gates.maps[component]["payload"]
    quantities = mapping["quantities"]
    values, structures, comparisons, incidence_summary = {}, {}, {}, {}
    flats, complement = prepared["flats"], prepared["complement"]
    for source in flats:
        structures["records/" + source] = flats[source]
    family_info = {name: {"table_file_sha256": f["table_sha"], "a10_receipt_file_sha256": f["a10_receipt_sha"]}
                   for name, f in gates.fam.items()}
    for entry in R.for_component(component):
        identity, arm = entry["identity"], entry["arm"]
        keys = R.quantity_keys(entry)
        provenance = {k: entry[k] for k in ("family_size", "level_alpha", "undefined_tail", "seed", "resamples",
                                             "quantile_method", "grid", "grid_values", "arm_filters",
                                             "comparator_filters", "sigma_variant", "capstar_rr")}
        if arm in gates.arms_not_run:
            # D:384, A1.8, A8.5: a not-run arm's entries.
            reason = gates.not_run[arm]["reason"]
            values[keys[0][0]] = {"status": "not run", "verdict": "undetermined", "reason": "arm not run: " + reason,
                                  "estimate": None, "interval": None, "undefined_share": None,
                                  "level_alpha": entry["level_alpha"], "undefined_tail": entry["undefined_tail"]}
            for key, _, _ in keys[1:]:
                values[key] = {"status": "not run"}
            comparisons[identity] = dict(provenance, status="not run", reason="arm not run: " + reason)
            continue
        boundary = entry["kind"] == "boundary"
        arm_cells, nominal_cells, arm_seeds, comparator_seeds = prepared["cells"][identity]
        COMPUTATION_STARTED.set(True)
        result = native("native comparison helper refused", compare, identity, arm_cells, nominal_cells)
        structures["cells/" + identity] = cells_structure(arm_cells, nominal_cells)
        structures["result/" + identity] = result
        values[keys[0][0]] = dict(comparison_fields(result), status="run")
        values[keys[1][0]] = point_fields(result)
        record = dict(provenance, status="run", bonferroni_alpha=result["bonferroni_alpha"],
                      undefined_resample_tail=result.get("undefined_resample_tail"), reason=result.get("reason"),
                      seeds_expected={"arm": arm_seeds, "comparator": comparator_seeds},
                      seeds_found={"arm": {fkey(k): len(v) for k, v in arm_cells.items()},
                                   "comparator": {fkey(k): len(v) for k, v in nominal_cells.items()}},
                      result=norm(result))
        if boundary:
            rows = native("native comparison helper refused", survival_differences, identity, arm_cells, nominal_cells)
            structures["result/%s.survival_difference.%s" % (family_name, arm)] = rows
            by_rr = {row["rr"]: row for row in rows}
            for key, kind, rr in keys[2:]:
                if kind == "survival":
                    values[key] = survival_fields(arm_cells[rr])
                else:
                    values[key] = {"difference": json_safe(by_rr[rr]["difference"]),
                                   "interval": json_safe(by_rr[rr]["interval95"])}
            record["survival_differences"] = norm(rows)
        comparisons[identity] = record
        for key, _, _ in keys:
            pooled_native, incidence, status, separate = inc.pooled(quantities[key], gates.per_run, FAMILY_OF, family_info)
            structures["incidence/" + key] = pooled_native
            values["incidence." + key] = incidence
            values["incidence_status." + key] = status
            values["incidence_counts." + key] = separate
            incidence_summary[key] = {"flag": incidence["flag"], "runs": len(quantities[key]),
                                      "branches": status["branches"],
                                      "families": {name: dict(info, **({"reason": R.CASE2_REASON}
                                                                       if info["status"] == inc.NO_ADMITTED else {}))
                                                   for name, info in status["families"].items()}}
    for key in quantities:
        values["disclosure." + key] = prepared["disclosure"][key]
    families = {}
    for name in list(R.ARMS[component]) + [NOMINAL]:
        if name in gates.arms_not_run:
            # A8.5: status only, with the evidence's reason without the prefix.
            values["family.%s.status" % name] = {"status": "not run", "reason": gates.not_run[name]["reason"]}
            families[name] = {"status": "not run", "reason": gates.not_run[name]["reason"]}
            continue
        f = gates.fam[name]
        values["family.%s.status" % name] = {"status": "run"}
        values["family.%s.labels" % name] = f["labels_value"]
        values["family.%s.admission" % name] = f["admission"]
        for field, value in f["family_error"].items():
            values["family_error.%s.%s" % (name, field)] = value
        families[name] = {
            "status": "run", "incidence_case": f["case"],
            "incidence_status": inc.RECORDED if f["case"] == 1 else inc.NO_ADMITTED,
            "table_file_sha256": f["table_sha"], "table_seal_sha256": f["table_doc"]["sha256"],
            "manifest_hash": f["tables"].manifest_hash, "calibration_file_sha256": f["calibration_sha"],
            "calibration_seal_sha256": f["calibration_doc"]["sha256"],
            "validation_receipt_file_sha256": f["validation_receipt_sha"],
            "cell_results_file_sha256": f["cell_results_sha"], "a10_receipt_file_sha256": f["a10_receipt_sha"],
            "identity_record_file_sha256": f["identity_sha"], "inventory_file_sha256": f["inventory_sha"],
            "inventory_schema": f["inventory"].schema,
            "inventory_counts": {k: f["inventory"].runs[k] for k in ("jobs", "records", "outputs")},
            "inventory_checkout_commit": f["inventory"].checkout_commit,
            "inventory_identity_file_sha256": f["inventory"].runs["identity_file_sha256"],
            # A10.4 and A10.6: recorded, compared with nothing.
            "inventory_manifest_file_sha256": f["inventory"].runs["manifest_file_sha256"],
            "inventory_runs_path": f["inventory"].runs["path"], "inventory_spec_path": f["inventory"].spec["path"],
            "calibration_code_hash": f["calibration_code_hash"],
            "labels": f["labels_value"], "admission": f["admission"],
            "family_error": f["family_error"], "refusals": f["refusals"],
            "a16_records": None if f["a16_files"] is None else {
                "family_record": f["a16_files"]["family_record"][1],
                "rounds": {r: {k: v[1] for k, v in files.items()} for r, files in f["a16_files"]["rounds"].items()}},
            "error_statement": "Part 2 error statement unchanged; no admission-probability budget estimate is a reading."}
        families[name].update(
            admission_binding=f["binding"],
            spec={"file_sha256": gates.src[source_of(name)]["spec_sha"],
                  "code_hash": gates.src[source_of(name)]["spec"].get("code_hash"),
                  "pull_dispatch_code_commit": (gates.src[source_of(name)]["spec"].get("pull_dispatch") or {}).get("code_commit")})
    values["label.comparator"] = R.LABEL_COMPARATOR
    values["family_size." + family_name] = R.FAMILY_SIZE[family_name]
    values = json_safe(values)
    mode = mode_name(gates.fixture)
    prefixes = tuple(["authorized_hashes", "comparator/", "reader_checkout:"] + ["arms/%s/" % a for a in R.ARMS[component]])
    reading = {
        "schema": "a10-stage2-reading-1", "component": component, "mode": mode,
        "reader": {"identity": gates.identity["sha256"], "role": gates.identity["role"], "files": gates.identity["files"]},
        "environment": {"python": R.PYTHON_VERSION, "numpy": R.NUMPY_VERSION, "running_identity": gates.code_identity,
                        "source_manifest_digest": gates.source_manifest_digest},
        "specification_set": gates.auth["specification_set"],
        "specification_set_digest": gates.auth["specification_set_digest"],
        "requirements_sha256": gates.auth["requirements_sha256"], "registration": gates.pin,
        "authorized_hashes_sha256": gates.auth_sha, "collection_sha256": gates.collection_sha256,
        "family": family_name, "family_size": R.FAMILY_SIZE[family_name], "registry_digest": R.registry_digest(),
        "family_complement_not_computed": complement,
        "registry": R.for_component(component), "comparisons": comparisons, "values": values, "families": families,
        "incidence": {"statement": R.UNCERTIFIED_SENTENCE, "quantities": incidence_summary},
        "label_comparator": R.LABEL_COMPARATOR,
        "inputs": {label: entry for label, entry in gates.ledger.record().items() if label.startswith(prefixes)},
        "excluded_roots": [e for e in gates.excluded if e["family"] in R.ARMS[component]],
        "statements": [R.STAGE1_STATEMENT, "No stage 1 value enters this reading."],
    }
    if gates.fixture:
        # MODE TERM 12 (A3.5 row 12): the fixture list hash is recorded.
        reading["fixture_list_hash"] = gates.auth["fixture_list_hash"]
    per_run = per_run_payload(gates.per_run, mapping["runs"])
    try:
        temporary = Path(gates.map_files[component]).read_bytes()
    except OSError:
        temporary = None
    require(temporary == gates.maps[component]["bytes"], "contributing-run map changed after it was sealed")
    return {"reading.json": sealed_bytes(reading),
            "values.json": document_bytes({"schema": "a10-stage2-values-1", "component": component, "values": values}),
            "contributing_runs.json": gates.maps[component]["bytes"],
            "incidence_per_run.json": sealed_bytes(per_run),
            "LADDER.json": ladder_bytes(component, gates.keys[component], structures)}


def per_run_payload(per_run, keys):
    """A10.2: the payload of ``incidence_per_run.json``. Exactly ``schema`` and
    ``runs``; the keys of ``runs`` are those of the same component's
    ``contributing_runs.json``; each entry is exactly ``record`` and ``status``.
    No reason, family or component key."""
    return {"schema": "a10-stage2-incidence-per-run-1",
            "runs": {key: {"record": per_run[key]["record"], "status": per_run[key]["status"]} for key in sorted(keys)}}


def seal_bytes(gates, component, hashes):
    """D:482 as amended by A2.5, A2.11 and A6.4a."""
    payload = {"schema": "a10-stage2-seal-1", "component": component, "files": dict(hashes),
               "reader_identity": gates.identity["sha256"],
               "collection_sha256": gates.collection_sha256, "specification_set": gates.auth["specification_set"],
               "specification_set_digest": gates.auth["specification_set_digest"],
               "requirements_sha256": gates.auth["requirements_sha256"], "mode": mode_name(gates.fixture)}
    if gates.fixture:
        payload["fixture_list_hash"] = gates.auth["fixture_list_hash"]
    return sealed_bytes(payload)


def read(gates, components, out):
    """A11.1: nothing is published before everything has passed. No file is
    written under ``<out>`` until every gate has passed (the caller ran them),
    every requested component is computed without a refusal, and the
    change-detection re-hash (D:275) has passed. Only then is each component
    folder published, ``A10/`` before ``A6/``, each file under a temporary name,
    fsynced and renamed, ``SEAL.json`` last (A6.4a). The caller writes
    ``run_log.json`` after that and prints the success lines last."""
    disclosures = Disclosures(gates)
    prepared = {component: prepare(gates, component, disclosures) for component in components}
    computed = {component: component_reading(gates, component, prepared[component]) for component in components}
    gates.ledger.verify()
    gates.end()
    # Every byte to be published is fixed here, SEAL.json included, so that
    # publication below is file-system work only.
    for component in components:
        hashes = {name: hashlib.sha256(computed[component][name]).hexdigest() for name in FILES}
        computed[component]["SEAL.json"] = seal_bytes(gates, component, hashes)
    written = {component: {name: {"sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}
                           for name, data in computed[component].items()} for component in components}
    # A11.1 item 4: a failure from here on is a publication failure; its phase
    # is ``after_computation_started`` even when every arm asked for is not run.
    # Nothing under ``<out>`` is deleted, temporary files included.
    COMPUTATION_STARTED.set(True)
    key = str(out)
    out = Path(out)
    require(not out.exists(), "output destination exists")
    out.mkdir(parents=True)
    CREATED.add(key)
    for component in components:
        folder = out / component
        folder.mkdir()
        for name in list(FILES) + ["SEAL.json"]:
            write_once(folder / name, computed[component][name])
    return written
