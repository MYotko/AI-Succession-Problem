"""A6 variant calibration tests: the self-check and each variant's epsilon_N."""
import json
from pathlib import Path

import pytest

from v3 import calibration_a6 as c6
from v3.artifacts import SIMULATION, unseal

FROZEN_PATH = SIMULATION / "v3" / "runs" / "registered" / "v3_rerun_calibration.json"
RECORDS_DIR = SIMULATION.parent.parent / "v3_instrument_inputs" / \
    "registered" / "registered" / "calibration" / "calibration" / "outputs"


def _frozen():
    return json.loads(FROZEN_PATH.read_text())


needs_inputs = pytest.mark.skipif(not RECORDS_DIR.exists() or not FROZEN_PATH.exists(),
                                  reason="registered calibration records not available")


@needs_inputs
def test_self_check_reproduces_frozen_values_exactly():
    frozen = _frozen()
    records = c6.load_records(RECORDS_DIR, frozen)
    assert len(records) == 50
    base_sigma = c6.self_check(records, frozen)
    assert base_sigma == frozen["payload"]["values"]["sigma_squared"]


@needs_inputs
def test_variants_change_only_epsilon_n():
    frozen = _frozen()
    fv = frozen["payload"]["values"]
    records = c6.load_records(RECORDS_DIR, frozen)
    for name, factor in c6.VARIANT_FACTORS.items():
        doc = c6.build_variant(records, frozen, name)
        v = unseal(doc)["values"]
        assert v["sigma_squared"] == pytest.approx(factor * fv["sigma_squared"])
        # Only sigma0^2 and epsilon_N move; every other value is frozen equal.
        assert v["epsilon_n"] != fv["epsilon_n"]
        for key in c6.FROZEN_VALUE_KEYS:
            assert v[key] == fv[key]
    # x10 lowers epsilon_N, x0.1 raises it (monotone in sigma0^2).
    hi = unseal(c6.build_variant(records, frozen, "sigma_squared_x10"))["values"]["epsilon_n"]
    lo = unseal(c6.build_variant(records, frozen, "sigma_squared_x0.1"))["values"]["epsilon_n"]
    assert hi < fv["epsilon_n"] < lo


@needs_inputs
def test_variant_validates_registered_at_a6_identity():
    from v3.calibration import validate_calibration
    frozen = _frozen()
    records = c6.load_records(RECORDS_DIR, frozen)
    doc = c6.build_variant(records, frozen, "sigma_squared_x10")
    payload = validate_calibration(doc, registered=True)
    assert payload["a6_variant"] == "sigma_squared_x10"
    assert payload["a6_parent_sha256"] == frozen["sha256"]


@needs_inputs
def test_tampered_records_fail_self_check():
    frozen = _frozen()
    records = c6.load_records(RECORDS_DIR, frozen)
    bad = [dict(r) for r in records]
    bad[0] = dict(bad[0], samples=bad[0]["samples"] + 1)
    with pytest.raises(c6.SelfCheckFailed):
        c6.self_check(bad, frozen)


@needs_inputs
def test_seal_variants_requires_rerun_commit(tmp_path):
    frozen = _frozen()
    # Sealing to disk (registered) without the rerun commit refuses.
    with pytest.raises(ValueError):
        c6.seal_variants(RECORDS_DIR, frozen, targets={"sigma_squared_x10": str(tmp_path / "x10.json")})
