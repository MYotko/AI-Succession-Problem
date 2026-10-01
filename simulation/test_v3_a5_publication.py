"""A5 publication and binding tests.

Builds a small synthetic A4 publication (family, receipt, cell-results sidecar,
census stage outputs and plan) from a real FV-route A1 job at tiny settings, then
runs A5 prepare -> stage -> publish -> report. Checks the identity-record and
receipt mismatch halts, census tamper detection, the refuse-to-overwrite rule,
the label-only byte check, and the sealed binding.

Requires the A1 records, the D26 probe records and the calibration; skips
otherwise. Fast: one FV table at tiny settings.
"""
import shutil
from pathlib import Path

import pytest

from v3.artifacts import (ROOT, SIMULATION, atomic_json, read, seal, unseal, digest, file_hash,
                          code_identity, stable_job)
from v3.production_runner import completed, dispatch, caps
from v3 import continuation_validation as cv
from v3 import table_validation_a4 as a4
from v3 import table_labels_a5 as a5

A1_ROOT = Path(r"C:\Users\matty\Dev\v3_instrument_inputs\registered_A1")
PROBE = Path(r"C:\Users\matty\Dev\v3_instrument_inputs\a3_probe")
CAL = "v3/runs/registered/v3_rerun_calibration.json"
OVERRIDE = {"groups": 4, "burn": 8, "measure": 16, "runs_per_group": 8, "particles": 8}

pytestmark = pytest.mark.skipif(
    not (A1_ROOT / "tables_A1_manifest.json").exists() or not PROBE.exists()
    or not (SIMULATION / CAL).exists(), reason="A1 records, probe or calibration not present")


def _fresh(name):
    base = ROOT / ("_a5_pub_" + name)
    if base.exists():
        shutil.rmtree(base)
    return base


def build_publication(base, *, trim_rows=1, trim_cells=3, poison_out_of_range=False, fixture=True):
    """A synthetic A4 publication built from one real FV A1 job, trimmed small.
    Returns a dict of the paths A5 consumes and the identity record."""
    cal = read(SIMULATION / CAL)
    src_code = a4._source_code_hash(A1_ROOT)
    jobs = {j["id"]: j for j in a4.selected_a1_jobs(A1_ROOT)}
    fv_id = next(jid for jid in jobs
                 if completed(A1_ROOT / "tables_A1/table", jobs[jid], src_code)["result"]["route"] == "fv")
    a1_job = jobs[fv_id]
    a1_out = completed(A1_ROOT / "tables_A1/table", a1_job, src_code)
    result = a1_out["result"]

    from v3.context import Context
    lower, upper = a5._context_bounds(a1_out, {})

    # Trim to a few rows, each with a few in-range published FV cells.
    trimmed_rows = []
    for row in result["rows"][:trim_rows]:
        entries = [e for e in (row.get("continuation") or {}).get("entries", []) if lower <= e["value"] <= upper][:trim_cells]
        if not entries:
            continue
        trimmed_rows.append({**row, "continuation": {**(row.get("continuation") or {}), "entries": entries}})
    assert trimmed_rows, "no in-range FV cells to build a synthetic support"
    trimmed_result = {**result, "rows": trimmed_rows}

    # Write the synthetic A1 source with the trimmed FV job.
    src = base / "source"
    for sub in ("outputs", "records"):
        (src / "tables_A1/table" / sub).mkdir(parents=True, exist_ok=True)
    a1_output_doc = {"job": a1_job, "code_hash": src_code, "result": trimmed_result}
    opath = src / "tables_A1/table/outputs" / (fv_id + ".json")
    atomic_json(opath, a1_output_doc)
    atomic_json(src / "tables_A1/table/records" / (fv_id + ".json"),
                {"job": a1_job, "code_hash": src_code, "status": "complete", "output_hash": file_hash(opath)})
    atomic_json(src / "tables_A1_manifest.json",
                seal({"jobs": [a1_job], "source_family": {"code_hash": src_code}, "tag": "v3_tables"}))
    atomic_json(src / "v3_rerun_tables_A1.json", {"placeholder": "synthetic A1 publication"})
    a1_file_sha = file_hash(src / "v3_rerun_tables_A1.json")

    # Build the A4 family rows (all FV estimated), keeping the A1 values.
    from v3.production_tables import write_tables, row_key
    family_rows = []
    for row in trimmed_rows:
        entries = list(row["continuation"]["entries"])
        if poison_out_of_range:
            entries = entries + [{"bin": [1, 1, 1, 1, 1, 1], "value": upper + 10.0, "error": 1.0}]
        fam = {**row, "route": "fv", "status": "estimated", "fv_label": "asymptotic, not certified",
               "continuation": {**row["continuation"], "entries": entries}}
        family_rows.append(fam)
    keys = [row_key(r) for r in family_rows]
    M_fv = sum(len(r["continuation"]["entries"]) for r in family_rows)
    manifest = {"tag": "v3_tables", "calibration_hash": cal["sha256"], "complete_family": True,
                "sensitivity_status": "passed", "required_row_keys": keys,
                "source_family": {"file_sha256": a1_file_sha, "code_hash": src_code}}
    family_path = base / "v3_rerun_tables_A4.json"
    document = write_tables(family_path, family_rows, manifest, fixture=fixture)

    # The A4 plan: one FV primary validate job and one census job for the A1 job,
    # with a plan hash consistent with A4's own `_recompute_plan_hash`.
    fv_validate = stable_job("a4_validate", {"a1_job": a1_job, "phase": "validate_fv_primary",
                             "stage": "validate", "route": "fv", "replicate": cv.FV_VALIDATE_REPLICATE,
                             "seed": cv.validate_seed(a1_job["seed"], cv.FV_VALIDATE_REPLICATE)}, "v3_tables", 0)
    census_job = stable_job("a4_census", {"a1_job": a1_job, "phase": "census", "stage": "census",
                            "route": "plain", "seed": cv.census_seed(a1_job["seed"])}, "v3_tables", 1)
    a4_plan = {"schema": "v3-A4-validation-1", "jobs": [fv_validate, census_job],
               "source_file_sha256": a1_file_sha, "source_manifest_sha256": digest(unseal(read(src / "tables_A1_manifest.json"))),
               "source_code_hash": src_code, "M": 0, "M_FV": M_fv, "code_hash": code_identity(),
               "settings_override": None, "registration": None}
    a4_plan["plan_hash"] = a4._recompute_plan_hash(a4_plan)
    a4_plan_path = base / "A4_plan.json"
    atomic_json(a4_plan_path, seal(a4_plan))

    # The A4 run root: a census stage output for the A1 job, with counts on the
    # support cells so exposure is well defined.
    a4_run = base / "A4_run"
    support_codes = [int(cv.fine_codes([e["bin"]])[0]) for e in family_rows[0]["continuation"]["entries"]]
    cell_counts = {code: 10 * (i + 1) for i, code in enumerate(support_codes)}
    cell_counts[int(cv.fine_codes([[7, 7, 7, 7, 7, 7]])[0])] = 5   # one endpoint outside support
    census_result = {"stage": "census", "a1_job_id": fv_id, "cell_counts": cell_counts,
                     "total_living": sum(cell_counts.values()), "total_low": 0}
    cpath = a4_run / "census" / "outputs" / (census_job["id"] + ".json")
    atomic_json(cpath, {"job": census_job, "code_hash": code_identity(), "result": census_result})
    census_hash = file_hash(cpath)

    # The receipt and the cell-results sidecar.
    sidecar_doc = seal({"schema": "v3-A4-cell-results-1", "plan_hash": "synthetic", "rows": [
        {"row": k, "setting": "primary", "route": "fv", "status": "estimated"} for k in keys]})
    sidecar_path = family_path.with_suffix(".cell_results.json")
    atomic_json(sidecar_path, sidecar_doc)
    receipt = {"schema": "v3-A4-receipt-1", "amendment": "A4", "table_seal_sha256": document["sha256"],
               "table_file_sha256": file_hash(family_path), "producer_code_hash": document["payload"]["code_hash"],
               "source_family": {"file_sha256": a1_file_sha, "code_hash": src_code},
               "calibration_sha256": cal["sha256"], "M": 0, "M_FV": M_fv, "plan_hash": a4_plan["plan_hash"],
               "stream_tags": list(cv.STREAM_TAGS), "stage_output_sha256": {census_job["id"]: census_hash},
               "stream_seeds": {j["id"]: j["config"]["seed"] for j in a4_plan["jobs"]},
               "cell_results_sha256": file_hash(sidecar_path)}
    receipt_path = family_path.with_suffix(".compatibility.json")
    atomic_json(receipt_path, seal(receipt))

    identity = {"family_file_sha256": file_hash(family_path), "table_seal_sha256": document["sha256"],
                "receipt_file_sha256": file_hash(receipt_path), "sidecar_file_sha256": file_hash(sidecar_path),
                "producing_commit": "synthetic-a4-commit", "code_hash": document["payload"]["code_hash"]}
    identity_path = base / "A5_identity.json"
    atomic_json(identity_path, identity)

    return {"base": base, "family_path": family_path, "a4_run": a4_run, "a4_plan_path": a4_plan_path,
            "src": src, "identity_path": identity_path, "identity": identity, "cal": cal,
            "census_path": cpath, "receipt_path": receipt_path, "M_fv": M_fv, "fv_id": fv_id}


def _prepare(pub, **kw):
    return a5.prepare(pub["family_path"], pub["a4_run"], pub["a4_plan_path"], pub["src"], CAL,
                      pub["identity_path"], registration=None, wall_hours=24, a3_probe_root=PROBE,
                      settings_override=OVERRIDE, **kw)


def _run_jobs(plan, run_root):
    control = run_root
    control.mkdir(parents=True, exist_ok=True)
    atomic_json(control / "control.json", {"mode": "normal", "max_workers": 2, "stop_dispatch": False, "interrupt_now": False})
    settings = {"profile": "local", "workers": 2, "threads": 1, "cpu_budget": 4, "mode": "normal", "caps": caps("local", 4)}
    result = dispatch(run_root / a5.PHASE, plan["jobs"], code_identity(), settings, __import__("time").time() + 300,
                      fixed={"workers": 2, "threads": 1}, control_root=control)
    assert result["completed"] == len(plan["jobs"]), result


def test_prepare_pins_and_builds_plan():
    base = _fresh("prep")
    try:
        pub = build_publication(base)
        plan = _prepare(pub)
        assert plan["fv_tables"] == 1 and len(plan["jobs"]) == 3
        assert plan["M"] == pub["M_fv"] and plan["M"] > 0
        assert plan["a4"]["family_file_sha256"] == pub["identity"]["family_file_sha256"]
        assert set(plan["a4_census_jobs"].values()) == {pub["fv_id"]}
        # every A5 job carries its tested rows and the plan hash
        assert all(j["config"]["plan_hash"] == plan["plan_hash"] for j in plan["jobs"])
    finally:
        shutil.rmtree(base)


def test_identity_family_hash_mismatch_halts():
    base = _fresh("idm")
    try:
        pub = build_publication(base)
        bad = dict(pub["identity"], family_file_sha256="0" * 64)
        atomic_json(pub["identity_path"], bad)
        with pytest.raises(ValueError, match="family file hash"):
            _prepare(pub)
    finally:
        shutil.rmtree(base)


def test_receipt_hash_mismatch_halts():
    base = _fresh("rcpt")
    try:
        pub = build_publication(base)
        # Tamper the receipt file bytes -> its file hash no longer matches the record.
        receipt = unseal(read(pub["receipt_path"]))
        receipt["M_FV"] = receipt["M_FV"] + 1
        atomic_json(pub["receipt_path"], seal(receipt))
        with pytest.raises(ValueError, match="receipt file hash"):
            _prepare(pub)
    finally:
        shutil.rmtree(base)


def test_census_tamper_detected_at_publish():
    base = _fresh("census")
    try:
        pub = build_publication(base)
        plan = _prepare(pub)
        run_root = base / "A5_run"
        _run_jobs(plan, run_root)
        # Tamper a census output after prepare pinned its hash.
        doc = read(pub["census_path"])
        doc["result"]["total_living"] = doc["result"]["total_living"] + 1
        atomic_json(pub["census_path"], doc)
        with pytest.raises(ValueError, match="census stage output hash mismatch"):
            a5.publish(plan, run_root, pub["a4_run"], pub["src"], pub["cal"], base / "labels.json", registered=False)
    finally:
        shutil.rmtree(base)


def test_publish_report_and_binding():
    base = _fresh("pub")
    try:
        pub = build_publication(base)
        plan = _prepare(pub)
        run_root = base / "A5_run"
        _run_jobs(plan, run_root)
        family_before = file_hash(pub["family_path"])
        target = base / "v3_rerun_labels_A5.json"
        out = a5.publish(plan, run_root, pub["a4_run"], pub["src"], pub["cal"], target, registered=False)
        assert out["M"] == plan["M"] and out["rows"] >= 1
        record = unseal(read(target))
        # Binding: A4 hashes, plan hash, seeds, M, and every stage output hash.
        assert record["a4_family"] == plan["a4"] and record["plan_hash"] == plan["plan_hash"] and record["M"] == plan["M"]
        assert len(record["stage_output_sha256"]) == len(plan["jobs"])
        assert record["certified_label"] == "certified under the plain law"
        assert record["asymptotic_label"] == "asymptotic, not certified"
        assert all(c["label"] in (record["certified_label"], record["asymptotic_label"])
                   for r in record["rows"] for c in r["cells"])
        # Label-only: the A4 family bytes are unchanged.
        assert file_hash(pub["family_path"]) == family_before
        # The report carries the A5 items and no rate.
        rep = a5.report(target, base / "report_A5.json")
        report = read(base / "report_A5.json")
        text = digest(report)  # ensure serializable
        assert rep["rows"] >= 1 and "totals" in report
        forbidden_words = ("survival", "extinction", "fire")
        assert not any(w in k for k in _all_keys(report) for w in forbidden_words)
    finally:
        shutil.rmtree(base)


def _all_keys(obj):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield k
            yield from _all_keys(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from _all_keys(v)


def test_refuse_to_overwrite_published_record():
    base = _fresh("frozen")
    try:
        pub = build_publication(base)
        plan = _prepare(pub)
        run_root = base / "A5_run"
        _run_jobs(plan, run_root)
        target = base / "labels.json"
        a5.publish(plan, run_root, pub["a4_run"], pub["src"], pub["cal"], target, registered=False)
        # A different record already at the target is not overwritten.
        atomic_json(target, {"payload": {"schema": "other"}, "sha256": digest({"schema": "other"})})
        with pytest.raises(RuntimeError, match="frozen"):
            a5.publish(plan, run_root, pub["a4_run"], pub["src"], pub["cal"], target, registered=False)
    finally:
        shutil.rmtree(base)


def test_registered_publish_rejects_settings_override():
    base = _fresh("regovr")
    try:
        pub = build_publication(base)
        plan = _prepare(pub)  # carries the smoke settings override
        with pytest.raises(ValueError, match="override"):
            a5.publish(dict(plan, registered=True, registration={"commit": "x", "path": "p", "sha256": "s"}),
                       base / "A5_run", pub["a4_run"], pub["src"], pub["cal"], base / "labels.json", registered=True)
    finally:
        shutil.rmtree(base)


def test_receipt_content_seal_mismatch_halts():
    base = _fresh("rcptcontent")
    try:
        pub = build_publication(base)
        receipt = unseal(read(pub["receipt_path"]))
        receipt["table_seal_sha256"] = "0" * 64                       # content wrong, file re-sealed
        atomic_json(pub["receipt_path"], seal(receipt))
        ident = dict(pub["identity"], receipt_file_sha256=file_hash(pub["receipt_path"]))
        atomic_json(pub["identity_path"], ident)
        with pytest.raises(ValueError, match="receipt table seal mismatch"):
            _prepare(pub)
    finally:
        shutil.rmtree(base)


def test_sidecar_hash_mismatch_halts():
    base = _fresh("sidecar")
    try:
        pub = build_publication(base)
        atomic_json(pub["identity_path"], dict(pub["identity"], sidecar_file_sha256="0" * 64))
        with pytest.raises(ValueError, match="sidecar"):
            _prepare(pub)
    finally:
        shutil.rmtree(base)


def test_flow_range_out_of_range_halts():
    base = _fresh("range")
    try:
        pub = build_publication(base, poison_out_of_range=True)
        with pytest.raises(cv.OutOfRange):
            _prepare(pub)
    finally:
        shutil.rmtree(base)


def test_M_computed_through_build_tested_set():
    base = _fresh("Mset")
    try:
        pub = build_publication(base, trim_cells=3)
        plan = _prepare(pub)
        payload, receipt, sidecar, _ = a5.load_a4_publication(pub["family_path"], pub["identity"])
        a4_plan = unseal(read(pub["a4_plan_path"]))
        src_code = a5._source_code_hash(pub["src"])
        per_job, M = a5.build_tested_set(payload, a4_plan, pub["src"], src_code, {})
        assert M == plan["M"] == pub["M_fv"] and M > 0
    finally:
        shutil.rmtree(base)


def test_census_hashes_taken_from_receipt_not_plan():
    base = _fresh("censusrcpt")
    try:
        pub = build_publication(base)
        plan = _prepare(pub)
        run_root = base / "A5_run"
        _run_jobs(plan, run_root)
        # A consistent plan whose census pin disagrees with the receipt: recompute
        # the plan hash so the plan-hash check passes and item 6's check fires.
        jid = next(iter(plan["a4_census_output_sha256"]))
        bad = dict(plan, a4_census_output_sha256={**plan["a4_census_output_sha256"], jid: "0" * 64})
        bad["plan_hash"] = a5._recompute_plan_hash(bad)
        with pytest.raises(ValueError, match="census hashes differ from the re-verified receipt"):
            a5.publish(bad, run_root, pub["a4_run"], pub["src"], pub["cal"], base / "labels.json", registered=False)
    finally:
        shutil.rmtree(base)


def test_label_only_real_family_tamper_refused():
    base = _fresh("labelonly")
    try:
        pub = build_publication(base)
        plan = _prepare(pub)
        run_root = base / "A5_run"
        _run_jobs(plan, run_root)
        # Tamper the real family file (not a mocked hash) after prepare pinned it.
        doc = read(pub["family_path"])
        doc["payload"]["tampered"] = True
        atomic_json(pub["family_path"], doc)
        with pytest.raises(ValueError, match="family file hash|family seal"):
            a5.publish(plan, run_root, pub["a4_run"], pub["src"], pub["cal"], base / "labels.json", registered=False)
    finally:
        shutil.rmtree(base)


def test_stage_flow_check_fires(monkeypatch):
    # The stage's own flow range check (not the published-value check) halts on an
    # out-of-range flow. The published values are in range; only the flows are not.
    base = _fresh("flowcheck")
    try:
        pub = build_publication(base)
        plan = _prepare(pub)
        job = plan["jobs"][0]
        a1 = a5._load_a1(job["config"]["a1_source_root"], job["config"]["a1_job"], job["config"]["a1_source_code_hash"])
        import numpy as np
        import v3.offline_estimator as oe
        real_score = oe.score_features
        monkeypatch.setattr(oe, "score_features", lambda *a, **k: real_score(*a, **k) + 1e6)
        with pytest.raises(cv.OutOfRange, match="flow"):
            a5.fvplain_stage(a1, job["config"]["tested_rows"], job["config"]["lower"], job["config"]["upper"],
                             job["config"]["seed"], job["config"]["settings_override"])
    finally:
        shutil.rmtree(base)


def test_stage_bin_range_halt(monkeypatch):
    base = _fresh("binrange")
    try:
        pub = build_publication(base)
        plan = _prepare(pub)
        job = plan["jobs"][0]
        a1 = a5._load_a1(job["config"]["a1_source_root"], job["config"]["a1_job"], job["config"]["a1_source_code_hash"])
        import numpy as np
        import v3.offline_estimator as oe
        bad = np.zeros((2, 2, 6), dtype=np.int8)
        bad[0, 0, 0] = 8   # out of the 0..7 range
        monkeypatch.setattr(oe, "simulate", lambda *a, **k: {"before": bad, "after": np.zeros((2, 2, 6), dtype=np.int8),
                                                             "features": np.ones((2, 2, 8))})
        with pytest.raises(cv.OutOfRange, match="bin coordinates out of range"):
            a5.fvplain_stage(a1, job["config"]["tested_rows"], job["config"]["lower"], job["config"]["upper"],
                             job["config"]["seed"], job["config"]["settings_override"])
    finally:
        shutil.rmtree(base)


def test_registered_prepare_rejects_fixture_family(monkeypatch):
    base = _fresh("regfix")
    try:
        pub = build_publication(base, fixture=True)
        monkeypatch.setattr(a5, "require_committed_identity", lambda p: None)
        with pytest.raises(ValueError, match="fixture A4 family"):
            a5.prepare(pub["family_path"], pub["a4_run"], pub["a4_plan_path"], pub["src"], CAL,
                       pub["identity_path"], registration={"commit": "x", "path": "p", "sha256": "s"},
                       wall_hours=24, a3_probe_root=PROBE)
    finally:
        shutil.rmtree(base)


def test_registered_prepare_rejects_non_canonical_a1(monkeypatch):
    base = _fresh("regcanon")
    try:
        pub = build_publication(base, fixture=False)
        monkeypatch.setattr(a5, "require_committed_identity", lambda p: None)
        with pytest.raises(ValueError, match="canonical A1 publication"):
            a5.prepare(pub["family_path"], pub["a4_run"], pub["a4_plan_path"], pub["src"], CAL,
                       pub["identity_path"], registration={"commit": "x", "path": "p", "sha256": "s"},
                       wall_hours=24, a3_probe_root=PROBE)
    finally:
        shutil.rmtree(base)


def test_publish_wall_recheck(monkeypatch):
    base = _fresh("wall")
    try:
        pub = build_publication(base)
        plan = a5.prepare(pub["family_path"], pub["a4_run"], pub["a4_plan_path"], pub["src"], CAL,
                          pub["identity_path"], registration=None, wall_hours=24, a3_probe_root=PROBE)  # no override
        monkeypatch.setattr(a5, "verify_registration", lambda pin: None)
        bad = dict(plan, registered=True, registration={"commit": "x", "path": "p", "sha256": "s"}, wall_seconds=90000)
        bad["plan_hash"] = a5._recompute_plan_hash(bad)
        with pytest.raises(ValueError, match="24-hour"):
            a5.publish(bad, base / "A5_run", pub["a4_run"], pub["src"], pub["cal"], base / "labels.json", registered=True)
    finally:
        shutil.rmtree(base)


def test_blindness_of_record_and_report():
    base = _fresh("blind")
    try:
        pub = build_publication(base)
        plan = _prepare(pub)
        run_root = base / "A5_run"
        _run_jobs(plan, run_root)
        a5.publish(plan, run_root, pub["a4_run"], pub["src"], pub["cal"], base / "labels.json", registered=False)
        a5.report(base / "labels.json", base / "report.json")
        record = unseal(read(base / "labels.json"))
        report = read(base / "report.json")
        forbidden_keys = ("survival", "extinction", "fire", "census_count", "living_census_endpoints",
                          "certified_census_endpoints", "certified_visits")
        # No forbidden key anywhere; the only count keys are cell counts and per-cell n_traj/visits.
        count_keys = {"M", "cells", "certified", "unresolved", "violation", "violations", "violation_count",
                      "n_traj", "visits", "cell", "fv_tables"}
        for obj in (record, report):
            for path, key, value in _walk(obj):
                assert not any(f in key for f in forbidden_keys), (path, key)
                if isinstance(value, int) and not isinstance(value, bool):
                    # ints are seeds (under stream_seeds / stage hashes are strings) or allowed counts
                    assert key in count_keys or "seed" in key or path.endswith("stream_seeds"), (path, key, value)
        # visits (aggregate) and census endpoint counts are not in the totals.
        assert set(record["totals"]) == {"certified", "unresolved", "violation", "cells", "violations",
                                         "certified_visit_share", "certified_census_share"}
    finally:
        shutil.rmtree(base)


def _walk(obj, path=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield path, k, v
            yield from _walk(v, path + "/" + str(k))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from _walk(v, path)


def test_totals_cells_equals_M():
    base = _fresh("cellsM")
    try:
        pub = build_publication(base)
        plan = _prepare(pub)
        run_root = base / "A5_run"
        _run_jobs(plan, run_root)
        a5.publish(plan, run_root, pub["a4_run"], pub["src"], pub["cal"], base / "labels.json", registered=False)
        record = unseal(read(base / "labels.json"))
        assert record["totals"]["cells"] == plan["M"]
        # Blindness: the record carries no raw census counts, only shares.
        assert "certified_census_share" in record["totals"]
        assert all("census_count" not in c and "living_census_endpoints" not in r
                   for r in record["rows"] for c in r["cells"])
    finally:
        shutil.rmtree(base)
