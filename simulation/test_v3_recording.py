"""A2 observer, table compatibility and real-output evidence checks."""
from copy import deepcopy
import numpy as np
import pytest
from v3.artifacts import ROOT, read, canonical, seal, code_identity, digest
from v3.integration import V3Model
from v3.recording import RecordedV3Model, pack_evidence, unpack_evidence
from v3 import gates


@pytest.fixture(scope="module")
def calibration():
    return read(ROOT / "runs/registered/v3_rerun_calibration.json")


def test_recorded_execution_is_identical_and_has_recomputable_plans(calibration):
    plain = V3Model(seed=817, calibration=calibration)
    observed = RecordedV3Model(seed=817, calibration=calibration)
    x, y = plain.run(3), observed.run(3)
    assert all(gates.check_theta(({"job": {"config": {"model": {"alpha": 1.}}}}, s), observed.parameters.epsilon_l) for s in y)
    event = observed.yield_events[0]
    assert len(event["gate_evidence"]["plans"]) == event["plan_count"]
    assert gates.check_review(({}, event))
    assert gates.gamma_comparisons(({}, event)) >= 0
    result = pack_evidence({"diagnostics": y, "yield_events": observed.yield_events})
    bare = deepcopy(result); bare.pop("gate_evidence")
    assert canonical(bare) == canonical({"diagnostics": x, "yield_events": plain.yield_events})
    unpack_evidence(result)
    assert gates.check_review(({}, result["yield_events"][0]))
    for name in ("ages", "welfare", "traits", "bank", "stocks", "window", "counts", "h_n"):
        np.testing.assert_array_equal(getattr(plain.state, name), getattr(observed.state, name))


def test_absorbed_theta_and_above_bound_raw_action(calibration):
    empty = RecordedV3Model(0, calibration=calibration)
    step = empty.step()
    assert "theta" not in step and step["gate_evidence"]["theta"] == 1
    assert gates.check_theta(({"job": {"config": {"model": {"alpha": 1.}}}}, step), empty.parameters.epsilon_l)
    small = RecordedV3Model(2, calibration=calibration)
    small.state.ages[:] = 80
    step = small.step()
    assert step["survival_first"]
    raw = step["gate_evidence"]
    assert raw["ages_before"] == [80, 80] and len(raw["action"]) == 6
    assert max(gates.candidate_welfare_shares(raw)) == 1.


def test_evidence_hash_counts_and_repeatable_compression(calibration):
    model = RecordedV3Model(0, calibration=calibration)
    raw = {"diagnostics": model.run(2), "yield_events": []}
    one, two = pack_evidence(deepcopy(raw)), pack_evidence(deepcopy(raw))
    assert canonical(one) == canonical(two)
    one["gate_evidence"]["raw_sha256"] = "0" * 64
    with pytest.raises(ValueError, match="hash"):
        unpack_evidence(one)
    two["diagnostics"].pop()
    with pytest.raises(ValueError, match="count"):
        unpack_evidence(two)


def compatibility_document():
    record = read(ROOT / "table_compatibility_A2.json")
    from v3.study import table_design
    manifest = {"calibration_hash": record["calibration_sha256"], "design": deepcopy(table_design()),
                "required_row_keys": [], "tag": "pilot"}
    return seal({"schema": "v3-tables-1", "fixture": True, "code_hash": code_identity(),
                 "manifest": manifest, "manifest_hash": digest(manifest), "rows": {}})


def test_compatibility_is_explicit_and_does_not_admit_fixture_tables():
    from v3.production_tables import ProductionTables
    document = compatibility_document()
    cal = document["payload"]["manifest"]["calibration_hash"]
    assert ProductionTables(document, calibration_hash=cal).fixture
    with pytest.raises(RuntimeError, match="fixture"):
        ProductionTables(document, calibration_hash=cal, registered=True)


@pytest.mark.parametrize("defect", ["source", "calibration", "design", "dependency"])
def test_table_compatibility_rejects_unapproved_changes(defect, monkeypatch):
    from v3 import table_compatibility as c
    document = compatibility_document()
    if defect == "source":
        document["payload"]["code_hash"] = "other-producer"
    elif defect == "calibration":
        document["payload"]["manifest"]["calibration_hash"] = "other-calibration"
    elif defect == "design":
        document["payload"]["manifest"]["design"]["primary"]["burn"] += 1
    else:
        monkeypatch.setattr(c, "dependency_hash", lambda _: "changed")
        with pytest.raises(ValueError, match="dependency"):
            c.compatible(document)
        return
    assert not c.compatible(document)


def test_compatibility_record_is_in_source_identity():
    from v3.artifacts import source_manifest
    assert "v3/table_compatibility_A2.json" in source_manifest()


def test_counterfactual_never_requests_original_model_rng(calibration, monkeypatch):
    from v3.recording import undisrupted
    model = RecordedV3Model(2, calibration=calibration)
    monkeypatch.setattr(model, "_rng", lambda *_: pytest.fail("private replay touched original RNG factory"))
    flows, lookup = undisrupted(model, horizon=2, capability=1.5, transition_at=0, incumbent_index=0, seed_channel="yield_common")
    assert flows.shape == (2, 25)


def test_index_refuses_before_reading_registered_outputs(tmp_path):
    with pytest.raises(ValueError, match="committed A2"):
        gates.build_index(tmp_path, ROOT / "runs/never_written_index.json")


def test_fired_succession_recording_matches_executor_on_declared_stress_fixture(calibration):
    from dataclasses import replace
    import hashlib
    from v3.tables import FixtureTables
    class SuccessorFixture(FixtureTables):
        def lookup(self, *args, **kwargs):
            value = super().lookup(*args, **kwargs)
            return replace(value, lambda_f=value.lambda_f + (1000 if kwargs["capability"] > 1 else 0))
    models = [cls(seed=817, calibration=calibration) for cls in (V3Model, RecordedV3Model)]
    records = []
    traces = []
    for model in models:
        trace = hashlib.sha256()
        original_rng = model._rng
        class Audited:
            def __init__(self, generator): self.generator = generator
            def __getattr__(self, name):
                target = getattr(self.generator, name)
                def draw(*args, **kwargs):
                    value = target(*args, **kwargs)
                    array = np.asarray(value)
                    trace.update(canonical([name, str(array.dtype), array.shape]))
                    trace.update(array.tobytes())
                    return value
                return draw
        model._rng = lambda channel: Audited(original_rng(channel))
        model.tables = SuccessorFixture(model.rules, model.parameters, model.kernel_hash)
        model._open_period()
        model.time = 20  # last review of the fixed epoch, with no later review
        records.append(model.step())
        traces.append(trace.hexdigest())
    event = models[1].yield_events[0]
    assert event["transition_count"] == 1
    assert gates.check_review(({}, event))
    assert gates.check_gamma(({}, event))
    assert gates.check_succession(({}, event))
    records[1].pop("gate_evidence")
    event.pop("gate_evidence")
    assert canonical(records[0]) == canonical(records[1])
    assert canonical(models[0].yield_events) == canonical(models[1].yield_events)
    assert traces[0] == traces[1]
    for name in ("ages", "welfare", "traits", "bank", "stocks", "window", "counts", "h_n"):
        np.testing.assert_array_equal(getattr(models[0].state, name), getattr(models[1].state, name))


# Artifacts stay inside the authorized tree even with default pytest options.
from test_v3_paths import tmp_path
