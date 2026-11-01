"""Stage 2 successor build, phase 1: the stage 2 run-spec builder with A6's
global seed check on the A10 path, and the generalized current A10 pin.

Fixtures only. No registered input is read and no simulation runs; the family
path strings below are the proposed names of A16_FAMILY_PATHS_CLAUSE_DRAFT.md,
used here as test parameters only."""
import hashlib
import subprocess

import pytest
from test_v3_paths import tmp_path

from v3 import artifacts as a
from v3 import tables_a10 as tables
from v3 import sensitivity_a6 as s6
from v3.instrument import Instrument

PATHS = {
    "nominal": ("v3/runs/registered/v3_rerun_calibration.json", "v3/runs/a10_stage1/nominal/v3_rerun_tables_A10.json"),
    "sqrt": ("v3/runs/registered/v3_rerun_calibration.json", "v3/runs/a10_stage2/sqrt/v3_rerun_tables_A10.json"),
    "crowding": ("v3/runs/registered/v3_rerun_calibration.json", "v3/runs/a10_stage2/crowding/v3_rerun_tables_A10.json"),
    "sigma_squared_x10": ("v3/runs/a10_stage2/sigma_squared_x10/v3_rerun_calibration.json",
                          "v3/runs/a10_stage2/sigma_squared_x10/v3_rerun_tables_A10.json"),
    "sigma_squared_x0.1": ("v3/runs/a10_stage2/sigma_squared_x0.1/v3_rerun_calibration.json",
                           "v3/runs/a10_stage2/sigma_squared_x0.1/v3_rerun_tables_A10.json"),
}
CEILINGS = {"sqrt": 8., "crowding": 8., "sigma_squared_x10": 2., "sigma_squared_x0.1": 2.}
A10 = {'mapping': 'A10', 'k_star': 1.8, 'g': 'linear'}


def reserved_ranges():
    from v3.validation_extension_a13 import RESERVED as A13
    from v3.validation_extension_a14 import RESERVED as A14
    return [A13, A14]


STAGE1_CEILINGS = dict(main=50.49, k1p5=10.94, k2p3=10.93, weight_corner=44.34, horizon=10.27)
A6_REGISTRY_PAYLOAD = {"schema": "v3-A6-seed-registry-1",
                       "table_jobs": {"crowding": [11, 12], "sigma_squared_x10": [15], "sigma_squared_x0.1": [16]},
                       "a4_streams": {"crowding": [13], "sigma_squared_x10": [17], "sigma_squared_x0.1": [18]},
                       "runs": {"nominal_runs": [19], "crowding_runs": [14], "sigma_squared_x10_runs": [20],
                                "sigma_squared_x0.1_runs": [21]}, "total_seeds": 11}
A6_REGISTRY = a.seal(A6_REGISTRY_PAYLOAD)


def history_inputs(stage1):
    """Toy sources for every history category. Small integers and tagged
    2^128-namespace values cannot collide with any real seed."""
    return dict(r4_forbidden=set(range(1, 24902)), a6_registry=A6_REGISTRY,
                stage1_manifests=[a.seal(s) for s in stage1.values()],
                a13_manifest=[{"seed": (1 << 60) + 1}], a14_manifest=[(1 << 61) + 1],
                qualification={"seeds": [(1 << 128) + 1], "declared_count": 1, "sources": ["launch:q"]},
                configuration={"seeds": [(1 << 128) + 2], "declared_count": None, "sources": ["launch:c"]},
                rehearsal={"seeds": [(1 << 128) + 3], "declared_count": 1, "sources": ["a13:rehearsal"]})


@pytest.fixture(scope="module")
def stage1():
    original = a.verify_registration
    a.verify_registration = lambda pin, **kwargs: pin
    try:
        return tables.stage1_run_specs(PATHS["nominal"][0], PATHS["nominal"][1], {'fixture': True}, STAGE1_CEILINGS)
    finally:
        a.verify_registration = original


@pytest.fixture(scope="module")
def history(stage1):
    return tables.stage2_history_seeds(PATHS["nominal"][0], **history_inputs(stage1))


@pytest.fixture(scope="module")
def registry(history):
    return tables.stage2_seed_registry(PATHS, history, reserved_ranges=reserved_ranges())


# ---------------------------------------------------------------------------
# Part 1: the stage 2 run jobs and their seeds
# ---------------------------------------------------------------------------

def test_stage2_runs_come_from_the_unchanged_builders():
    groups = tables.stage2_runs(PATHS)
    assert {n: len(j) for n, j in groups.items()} == tables.STAGE2_RUN_COUNTS
    nominal_cal, nominal_tables = PATHS["nominal"]
    sqrt_arm = [j for j in tables.arm_runs(nominal_cal, nominal_tables, PATHS["sqrt"][1])
                if j["config"]["model"]["instrument"]["g"] == "sqrt"]
    assert groups["sqrt"] == sqrt_arm
    a6 = tables.a6_runs(PATHS)
    assert groups["crowding"] == [j for j in a6 if j["config"]["phase"] == "a6_crowding"]
    for variant in s6.SIGMA_VARIANTS:
        assert groups[variant] == [j for j in a6 if j["config"]["phase"] == "a6_" + variant]
        assert all(j["config"]["model"]["instrument"] == tables.NOMINAL.declaration() for j in groups[variant])
        assert all(j["config"]["tables_path"] == PATHS[variant][1] for j in groups[variant])
        assert all(j["config"]["calibration_path"] == PATHS[variant][0] for j in groups[variant])
    assert all(j["config"]["model"]["instrument"] == Instrument("A10", 1.8, "sqrt").declaration() for j in groups["sqrt"])
    assert all(j["config"]["tables_path"] == PATHS["sqrt"][1] for j in groups["sqrt"])
    assert all(j["config"]["model"]["instrument"] == tables.NOMINAL.declaration() for j in groups["crowding"])
    assert all(j["config"]["model"]["crowding"] == "reproductive" for j in groups["crowding"])
    all_jobs = [j for jobs in groups.values() for j in jobs]
    assert len({j["id"] for j in all_jobs}) == len({j["seed"] for j in all_jobs}) == 9800
    assert all(j["config"]["steps"] == 500 and j["tag"] == "v3_rerun" for j in all_jobs)
    # Every job survives the runner's scheduling-independent re-derivation.
    for j in all_jobs[::97]:
        assert a.stable_job(j["kind"], j["config"], j["tag"], j["index"]) == j
    # The A6 arms carry their paired seed source, as correct_runs builds it.
    assert all("a10_seed_source" in j["config"] for j in groups["crowding"])


def test_stage2_seeds_follow_the_table_path_strings():
    # Audit A finding 7: the path strings enter the seeds, so they are parameters.
    other = dict(PATHS, sqrt=(PATHS["sqrt"][0], "v3/runs/elsewhere/sqrt.json"))
    assert {j["seed"] for j in tables.stage2_runs(other)["sqrt"]}.isdisjoint(
        {j["seed"] for j in tables.stage2_runs(PATHS)["sqrt"]})
    with pytest.raises(ValueError, match="exactly nominal and the four"):
        tables.stage2_runs({k: v for k, v in PATHS.items() if k != "crowding"})
    with pytest.raises(ValueError, match="pair of strings"):
        tables.stage2_runs(dict(PATHS, sqrt="v3/one.json"))


def test_stage2_seed_registry_covers_tables_streams_labels_and_runs(registry):
    assert registry["schema"] == tables.STAGE2_REGISTRY_SCHEMA
    assert registry["paths"] == {k: list(v) for k, v in PATHS.items()}
    counts = {"sqrt": 1495, "crowding": 1495, "sigma_squared_x10": 655, "sigma_squared_x0.1": 655}
    primary = {"sqrt": 1375, "crowding": 1375, "sigma_squared_x10": 625, "sigma_squared_x0.1": 625}
    # A5 streams are reserved for the c^0.5 family only: the A6 variants make
    # no labels (operator, 2026-10-29).
    assert set(registry["a5_streams"]) == {"sqrt"}
    assert len(registry["a5_streams"]["sqrt"]) == 3 * primary["sqrt"]
    for family in tables.STAGE2_FAMILIES:
        jobs = tables.build_jobs(family, PATHS[family][0])
        assert registry["table_jobs"][family] == [j["seed"] for j in jobs]
        assert len(jobs) == counts[family]
        assert len(registry["a4_streams"][family]) == 5 * counts[family]
        # A later step's own seeds match the registry, by A6's unchanged check.
        s6.assert_registry_seeds(registry, "table_jobs", family, [j["seed"] for j in jobs])
        from v3 import continuation_validation as cv
        actual_streams = [cv.fit_seed(j["seed"]) for j in jobs]
        s6.assert_registry_seeds(registry, "a4_streams", family, actual_streams)
    assert {n: len(v) for n, v in registry["runs"].items()} == tables.STAGE2_RUN_COUNTS
    assert registry["reserved_ranges"] == [list(r) for r in reserved_ranges()]
    assert registry["total_seeds"] == sum(len(v) for kind in ("table_jobs", "a4_streams", "a5_streams", "runs")
                                          for v in registry[kind].values())
    assert registry["history"]["schema"] == tables.STAGE2_HISTORY_SCHEMA
    assert registry["history"]["counts"]["stage1_runs"] == 53100 and registry["history"]["counts"]["r4_forbidden"] == 24901
    assert registry["history"]["declared_totals"] == {"r4_forbidden": None, "a6_registry": 11, "nominal_family": None,
                                                      "stage1_runs": 53100, "a13_manifest": None, "a14_manifest": None,
                                                      "qualification": 1, "configuration": None, "rehearsal": 1}
    assert a.unseal(a.seal(registry)) == registry


def test_stage2_seed_registry_halts_on_any_collision(registry, history):
    run_seed = registry["runs"]["sqrt"][0]
    table_seed = registry["table_jobs"]["crowding"][0]
    stream_seed = registry["a4_streams"]["sigma_squared_x10"][0]
    def poisoned(category, seed):
        categories = dict(history["categories"], **{category: sorted(set(history["categories"][category]) | {seed})})
        return dict(history, categories=categories, counts={k: len(v) for k, v in categories.items()})
    with pytest.raises(s6.SeedCollision, match="forbidden"):
        tables.stage2_seed_registry(PATHS, poisoned("r4_forbidden", run_seed), reserved_ranges=reserved_ranges())
    with pytest.raises(s6.SeedCollision, match="forbidden"):
        tables.stage2_seed_registry(PATHS, poisoned("configuration", table_seed), reserved_ranges=reserved_ranges())
    with pytest.raises(s6.SeedCollision, match="reserved range"):
        tables.stage2_seed_registry(PATHS, history, reserved_ranges=reserved_ranges() + [(stream_seed, stream_seed + 1)])
    with pytest.raises(ValueError, match="reserved ranges"):
        tables.stage2_seed_registry(PATHS, history, reserved_ranges=[(5, 1)])
    # A later reserve is one more input pair, never a code change: an empty
    # or disjoint range changes nothing.
    extra = tables.stage2_seed_registry(PATHS, history, reserved_ranges=reserved_ranges() + [(1 << 62, 12 << 60)])
    assert extra["reserved_ranges"][-1] == [1 << 62, 12 << 60]
    assert {k: extra[k] for k in ("table_jobs", "a4_streams", "a5_streams", "runs")} == \
        {k: registry[k] for k in ("table_jobs", "a4_streams", "a5_streams", "runs")}


def test_stage2_history_seeds_assemble_every_existing_inventory(stage1, history):
    categories = history["categories"]
    assert set(categories) == set(tables.STAGE2_HISTORY_FLOORS)
    assert categories["a6_registry"] == list(range(11, 22)) and categories["a13_manifest"] == [(1 << 60) + 1]
    assert history["declared_totals"]["a6_registry"] == 11 and history["declared_totals"]["qualification"] == 1
    assert history["sources"]["qualification_sources"] == ["launch:q"]
    assert categories["a14_manifest"] == [(1 << 61) + 1] and categories["qualification"] == [(1 << 128) + 1]
    stage1_seeds = {j["seed"] for s in stage1.values() for j in s["jobs"]}
    assert set(categories["stage1_runs"]) == stage1_seeds and len(stage1_seeds) == 53100
    nominal = tables.build_jobs("nominal", PATHS["nominal"][0])
    from v3 import continuation_validation as cv
    from v3.table_labels_a5 import fvplain_seed
    seeds = set(categories["nominal_family"])
    assert {j["seed"] for j in nominal} <= seeds
    assert {cv.validate_seed(j["seed"], 3) for j in nominal} <= seeds
    assert {fvplain_seed(j["seed"], 1) for j in nominal if j["config"]["setting_name"] == "primary"} <= seeds
    assert history["counts"] == {k: len(v) for k, v in categories.items()}
    assert history["sources"]["a6_registry_sha256"] == A6_REGISTRY["sha256"]
    assert history["sources"]["stage1_manifest_sha256"] == [a.seal(s)["sha256"] for s in stage1.values()]


def test_stage2_history_refuses_partial_inventories(stage1):
    inputs = history_inputs(stage1)
    with pytest.raises(ValueError, match="53,100"):
        tables.stage2_history_seeds(PATHS["nominal"][0], **dict(inputs, stage1_manifests=[stage1["main"]]))
    with pytest.raises(ValueError, match="A6 seed registry"):
        tables.stage2_history_seeds(PATHS["nominal"][0], **dict(inputs, a6_registry={"schema": "other"}))
    with pytest.raises(ValueError, match="below its floor"):
        tables.stage2_history_seeds(PATHS["nominal"][0], **dict(inputs, r4_forbidden={1, 2}))
    with pytest.raises(ValueError, match="below its floor"):
        tables.stage2_history_seeds(PATHS["nominal"][0], **dict(inputs, qualification={"seeds": [], "declared_count": 0}))
    with pytest.raises(ValueError, match="outside its reserved range"):
        tables.stage2_history_seeds(PATHS["nominal"][0], **dict(inputs, a13_manifest=[5]))
    with pytest.raises(TypeError):
        tables.stage2_history_seeds(PATHS["nominal"][0], **{k: v for k, v in inputs.items() if k != "rehearsal"})


def test_stage2_history_binds_declared_totals(stage1):
    inputs = history_inputs(stage1)
    # The A6 registry must cover its three families and five arms and match its own total.
    missing = a.seal({**A6_REGISTRY_PAYLOAD, "table_jobs": {k: v for k, v in A6_REGISTRY_PAYLOAD["table_jobs"].items()
                                                              if k != "sigma_squared_x0.1"}})
    with pytest.raises(ValueError, match="lacks table_jobs"):
        tables.stage2_history_seeds(PATHS["nominal"][0], **dict(inputs, a6_registry=missing))
    wrong_total = a.seal({**A6_REGISTRY_PAYLOAD, "total_seeds": 10})
    with pytest.raises(ValueError, match="declared total"):
        tables.stage2_history_seeds(PATHS["nominal"][0], **dict(inputs, a6_registry=wrong_total))
    # An inventory must match the count its launch record declares.
    with pytest.raises(ValueError, match="against its declared count"):
        tables.stage2_history_seeds(PATHS["nominal"][0], **dict(inputs, qualification={"seeds": [(1 << 128) + 1], "declared_count": 2}))
    with pytest.raises(ValueError, match="must carry seeds"):
        tables.stage2_history_seeds(PATHS["nominal"][0], **dict(inputs, rehearsal={"declared_count": 1}))
    # The operational inventories must state their declared count explicitly,
    # and an absent total must name the records it comes from.
    with pytest.raises(ValueError, match="must be a mapping"):
        tables.stage2_history_seeds(PATHS["nominal"][0], **dict(inputs, rehearsal=[(1 << 128) + 3]))
    with pytest.raises(ValueError, match="state declared_count explicitly"):
        tables.stage2_history_seeds(PATHS["nominal"][0], **dict(inputs, rehearsal={"seeds": [(1 << 128) + 3]}))
    with pytest.raises(ValueError, match="name the records"):
        tables.stage2_history_seeds(PATHS["nominal"][0], **dict(inputs, rehearsal={"seeds": [(1 << 128) + 3], "declared_count": None}))
    # A declared total is recorded; its absence is recorded as None, never invented.
    history = tables.stage2_history_seeds(PATHS["nominal"][0], **dict(inputs, rehearsal={"seeds": [(1 << 128) + 3], "declared_count": 1}))
    assert history["declared_totals"]["rehearsal"] == 1 and history["declared_totals"]["configuration"] is None
    # The registry refuses a history whose declared totals were dropped or contradict its counts.
    dropped = {k: v for k, v in history.items() if k != "declared_totals"}
    with pytest.raises(ValueError, match="declared total"):
        tables.stage2_seed_registry(PATHS, dropped, reserved_ranges=reserved_ranges())
    contradicted = dict(history, declared_totals=dict(history["declared_totals"], qualification=2))
    with pytest.raises(ValueError, match="against its declared total"):
        tables.stage2_seed_registry(PATHS, contradicted, reserved_ranges=reserved_ranges())


def test_stage2_registry_and_specs_refuse_an_unbound_history(history, registry, monkeypatch):
    monkeypatch.setattr(a, 'verify_registration', lambda pin, **kwargs: pin)
    with pytest.raises(ValueError, match="structured history"):
        tables.stage2_seed_registry(PATHS, set(), reserved_ranges=reserved_ranges())
    partial = dict(history, categories={k: v for k, v in history["categories"].items() if k != "a14_manifest"},
                   counts={k: c for k, c in history["counts"].items() if k != "a14_manifest"},
                   declared_totals={k: c for k, c in history["declared_totals"].items() if k != "a14_manifest"})
    with pytest.raises(ValueError, match="exactly the categories"):
        tables.stage2_seed_registry(PATHS, partial, reserved_ranges=reserved_ranges())
    miscounted = dict(history, counts=dict(history["counts"], rehearsal=2))
    with pytest.raises(ValueError, match="counts do not match"):
        tables.stage2_seed_registry(PATHS, miscounted, reserved_ranges=reserved_ranges())
    unbound = {k: v for k, v in registry.items() if k != "history"}
    with pytest.raises(ValueError, match="does not bind its history"):
        tables.stage2_run_specs(PATHS, {}, CEILINGS, unbound)
    short = dict(registry, history=dict(registry["history"], counts=dict(registry["history"]["counts"], stage1_runs=53099)))
    with pytest.raises(ValueError, match="53,100"):
        tables.stage2_run_specs(PATHS, {}, CEILINGS, short)


def test_stage2_run_specs_bind_registry_pin_and_ceilings(registry, monkeypatch):
    calls = []
    def verify(pin, **kwargs):
        calls.append(kwargs)
        return pin
    monkeypatch.setattr(a, 'verify_registration', verify)
    specs = tables.stage2_run_specs(PATHS, {'fixture': True}, CEILINGS, a.seal(registry))
    assert calls == [{'instrument': tables.NOMINAL}]
    groups = tables.stage2_runs(PATHS)
    assert set(specs) == set(tables.STAGE2_FAMILIES)
    for name, spec in specs.items():
        assert spec["jobs"] == groups[name]
        assert spec["registered"] and spec["registered_a10"] and spec["tag"] == "v3_rerun"
        assert spec["schema"] == "v3-registered-1" and spec["code_hash"] == a.code_identity()
        assert spec["wall_seconds"] == int(CEILINGS[name] * 3600) and spec["x2_equivalent_hours"] == CEILINGS[name]
        assert spec["phases"] == [spec["jobs"][0]["config"]["phase"]]
        profile = spec["configuration"][spec["phases"][0]]
        assert profile["workers_x2"] == [8, 12, 16, 24, 32] and profile["workers_local"] == [2, 4, 8, 12]
        assert profile["config"]["steps"] == 5 and "a10_seed_source" not in profile["config"]
        assert spec["instrument"] == spec["jobs"][0]["config"]["model"]["instrument"]
        assert spec["seed_registry_sha256"] == a.digest(registry) and spec["a10_family"] == name
        assert a.unseal(a.seal(spec)) == spec
    assert specs["sqrt"]["instrument"]["g"] == "sqrt" and specs["crowding"]["instrument"] == tables.NOMINAL.declaration()
    assert specs["sqrt"]["wall_seconds"] == 28800
    # The runner's own spec validation accepts the shape; tables are not read.
    from v3 import production_runner as pr, production_tables as pt
    monkeypatch.setattr(pr, "verify_registration", lambda *args, **kwargs: {'fixture': True})
    from types import SimpleNamespace
    monkeypatch.setattr(pt, "ProductionTables", lambda *args, **kwargs: SimpleNamespace(require_a10=lambda inst: None))
    settings = {"profile": "local", "workers": 3, "threads": 1, "cpu_budget": 4, "mode": "normal",
                "caps": pr.caps("local", 4)}
    for name in ("sqrt", "crowding"):
        pr.validate_spec(specs[name], settings)


def test_stage2_run_specs_refuse_missing_or_foreign_registry(registry, history, monkeypatch):
    monkeypatch.setattr(a, 'verify_registration', lambda pin, **kwargs: pin)
    with pytest.raises(ValueError, match="requires the sealed"):
        tables.stage2_run_specs(PATHS, {}, CEILINGS, None)
    other = tables.stage2_seed_registry(dict(PATHS, sqrt=(PATHS["sqrt"][0], "v3/runs/elsewhere/sqrt.json")),
                                        history, reserved_ranges=reserved_ranges())
    with pytest.raises(ValueError, match="not built for these paths"):
        tables.stage2_run_specs(PATHS, {}, CEILINGS, other)
    tampered = dict(registry, runs=dict(registry["runs"], crowding=registry["runs"]["crowding"][:-1] + [7]))
    with pytest.raises(s6.SeedCollision, match="do not equal"):
        tables.stage2_run_specs(PATHS, {}, CEILINGS, tampered)
    with pytest.raises(ValueError, match="hash mismatch"):
        tables.stage2_run_specs(PATHS, {}, CEILINGS, dict(a.seal(registry), sha256="0" * 64))


@pytest.mark.parametrize('ceilings', [{}, dict(CEILINGS, sqrt=None), dict(CEILINGS, sqrt=0),
                                      dict(CEILINGS, crowding=float('inf')), dict(CEILINGS, extra=1),
                                      {k: v for k, v in CEILINGS.items() if k != 'sigma_squared_x10'}])
def test_stage2_requires_every_positive_finite_ceiling(ceilings, registry):
    with pytest.raises(ValueError):
        tables.stage2_run_specs(PATHS, {}, ceilings, registry)


def test_stage1_builder_is_unchanged(stage1):
    # The stage 1 specs stay byte-identical: same five groups, same seeds, and
    # the sqrt placeholder path still unused there.
    specs = stage1
    assert {n: len(s['jobs']) for n, s in specs.items()} == dict(main=24900, k1p5=4400, k2p3=4400, weight_corner=17600, horizon=1800)
    assert specs['main']['wall_seconds'] == 181764
    assert all('a10_stage' not in s for s in specs.values())
    assert all(j['config']['model']['instrument']['g'] == 'linear' for s in specs.values() for j in s['jobs'])


def test_stage2_cli_writes_frozen_sealed_specs(tmp_path, monkeypatch, registry):
    import json
    import sys
    monkeypatch.setattr(a, 'verify_registration', lambda pin, **kwargs: pin)
    out = a.ROOT / '_pytest_v3' / ('stage2_cli_' + a.digest(str(tmp_path))[:8])
    paths = tmp_path / 'paths.json'; paths.write_text(json.dumps({k: list(v) for k, v in PATHS.items()}))
    pin = tmp_path / 'pin.json'; pin.write_text(json.dumps({'fixture': True}))
    ceilings = tmp_path / 'ceilings.json'; ceilings.write_text(json.dumps(CEILINGS))
    reg = tmp_path / 'registry.json'; reg.write_text(json.dumps(a.seal(registry)))
    argv = ['tables_a10', 'stage2-runs', '--paths', str(paths), '--pin', str(pin), '--ceilings', str(ceilings),
            '--seed-registry', str(reg), '--output-dir', str(out)]
    monkeypatch.setattr(sys, 'argv', argv)
    try:
        tables.main()
        written = {p.stem: a.unseal(a.read(p)) for p in out.glob('*.json')}
        expected = tables.stage2_run_specs(PATHS, {'fixture': True}, CEILINGS, registry)
        assert written == expected
        tables.main()  # identical bytes may be rewritten
        (out / 'sqrt.json').write_text('{}')
        with pytest.raises(RuntimeError, match='stage 2 manifest is frozen'):
            tables.main()
        import inspect
        assert '"stage 1 manifest is frozen: "' in inspect.getsource(tables.main)
    finally:
        import shutil
        shutil.rmtree(out, ignore_errors=True)


# ---------------------------------------------------------------------------
# Part 2: the generalized current A10 pin
# ---------------------------------------------------------------------------

def _git_stub(text):
    return lambda cmd, **kw: subprocess.CompletedProcess(cmd, 0, stdout=text if 'show' in cmd else b'')


def _note(tmp_path, text):
    path = tmp_path / 'simulation/diagnostics/v3_rerun_design_note.md'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text)
    return path


A14_TEXT = b'Amendment A10\nAmendment A11\nClarified, 2026-10-16: pricing R_max\n### Amendment A14\n'
SUCCESSOR = 'f' * 40


A16_COMMIT = "ae71028ecc1bcd4a8049eb1fc933cdb725e5fa33"
A16_MARKER = b"### Amendment A16, 2026-10-29: prospective validation extensions for A10 stage 2"
# The A17 adoption commit: the current stage 2 pin since phase 2 (A17 section 6
# item 3). The register commit 74460801 changed no note bytes.
A17_COMMIT = "3b8d8261c47b436a95fe831bd7192ede08460d1e"
A17_MARKER = b"### Amendment A17, 2026-10-30: a host register for stage 2 compute"
A14_MARKERS = (b'Clarified, 2026-10-16: pricing R_max', b'### Amendment A14')
NOTE_PATH = 'simulation/diagnostics/v3_rerun_design_note.md'
# Every commit at which a current A10 plan could have been pinned, in both forms.
BINDING_PINS = {form for commit in (a.A13_COMMIT, a.A14_COMMIT, A16_COMMIT, A17_COMMIT) for form in (commit, commit[:8])}


def _marker_for(successor):
    return {None: None, A16_COMMIT: A16_MARKER, A17_COMMIT: A17_MARKER}.get(successor, MARKER if successor else None)


@pytest.fixture
def unset(monkeypatch):
    """The state before the commit-time values were set: every check equals the A14 check."""
    monkeypatch.setattr(a, 'STAGE2_COMMIT', None)
    monkeypatch.setattr(a, 'STAGE2_AMENDMENT_MARKER', None)


def test_successor_constants_are_set_to_the_adopted_a17_commit():
    assert a.STAGE2_COMMIT == A17_COMMIT and a.STAGE2_AMENDMENT_MARKER == A17_MARKER
    assert a.A16_COMMIT == A16_COMMIT and a.A16_AMENDMENT_MARKER == A16_MARKER
    assert a.STAGE2_PRIOR_MARKERS == (A16_MARKER,)
    assert a.current_a10_commit() == A17_COMMIT
    assert a.current_a10_note_markers() == A14_MARKERS + (A16_MARKER, A17_MARKER)
    assert a.is_current_a10_pin(A17_COMMIT) and a.is_current_a10_pin(A17_COMMIT[:8])
    assert not any(a.is_current_a10_pin(c) for c in (A16_COMMIT, A16_COMMIT[:8], a.A14_COMMIT, a.A13_COMMIT))
    # A17 section 6 item 3: ae71028e stays in the binding list, in both forms.
    assert set(a.a13_binding_pins()) == BINDING_PINS
    assert len(a.a13_binding_pins()) == len(BINDING_PINS)
    # The tree's committed note at the A17 commit carries every marker and is
    # byte-identical to the working-tree note and to the note at the register commit.
    repo = a.SIMULATION.parent
    committed = subprocess.run(['git', 'show', A17_COMMIT + ':' + NOTE_PATH], cwd=repo, capture_output=True, check=True).stdout
    assert all(marker in committed for marker in a.current_a10_note_markers())
    assert hashlib.sha256(committed).hexdigest() == a.file_hash(repo / NOTE_PATH)
    register = subprocess.run(['git', 'show', '74460801:' + NOTE_PATH], cwd=repo, capture_output=True, check=True).stdout
    assert register == committed
    assert subprocess.run(['git', 'merge-base', '--is-ancestor', A17_COMMIT, 'HEAD'], cwd=repo).returncode == 0
    # The A16 note lacks A17's heading, so it can no longer pass the strict check.
    a16_note = subprocess.run(['git', 'show', A16_COMMIT + ':' + NOTE_PATH], cwd=repo, capture_output=True, check=True).stdout
    assert A16_MARKER in a16_note and A17_MARKER not in a16_note


def test_set_state_strict_verification_against_the_committed_tree(tmp_path, monkeypatch):
    """A current A10 plan pinned to the A17 commit passes strict verification
    only with the committed note's real bytes (A14's two markers, the A16
    heading and the A17 heading present) and a byte-identical working note; a
    stale note, a note lacking a marker, the A16 pin, the A14 pin and any other
    commit are refused as current. The A16 and A14 pins verify historically."""
    repo = a.SIMULATION.parent
    committed = subprocess.run(['git', 'show', A17_COMMIT + ':' + NOTE_PATH], cwd=repo, capture_output=True, check=True).stdout
    path = _note(tmp_path, committed)
    pin = dict(commit=A17_COMMIT, path=path.relative_to(tmp_path).as_posix(), sha256=hashlib.sha256(committed).hexdigest())
    # The committed bytes are the real ones; git's ancestry, diff and
    # untracked queries are stubbed, since this build is itself uncommitted.
    monkeypatch.setattr(a.subprocess, 'run', _git_stub(committed))
    assert a.verify_registration(pin, tmp_path, instrument=A10) == pin
    assert a.verify_registration(dict(pin, commit=A17_COMMIT[:8]), tmp_path, instrument=A10)['commit'] == A17_COMMIT[:8]
    path.write_bytes(committed + b'local edit\n')
    with pytest.raises(RuntimeError, match='stale'):
        a.verify_registration(pin, tmp_path, instrument=A10)
    path.write_bytes(committed)
    for marker in (A17_MARKER, A16_MARKER):
        lacking = committed.replace(marker, marker[:16] + b', something else')
        assert lacking != committed
        monkeypatch.setattr(a.subprocess, 'run', _git_stub(lacking))
        path.write_bytes(lacking)
        with pytest.raises(RuntimeError, match='stage 2 pin ' + A17_COMMIT[:8]):
            a.verify_registration(dict(pin, sha256=hashlib.sha256(lacking).hexdigest()), tmp_path, instrument=A10)
    path.write_bytes(committed)
    monkeypatch.setattr(a.subprocess, 'run', _git_stub(committed))
    for other in (A16_COMMIT, A16_COMMIT[:8], a.A14_COMMIT, 'c217cc7d' + 'f' * 32):
        with pytest.raises(RuntimeError, match='stage 2 pin ' + A17_COMMIT[:8]):
            a.verify_registration(dict(pin, commit=other), tmp_path, instrument=A10)
    with pytest.raises(RuntimeError, match='stage 2 pin'):
        a.verify_registration(dict(pin, path='simulation/diagnostics/other.md'), tmp_path, instrument=A10)
    # The A16 pin verifies historically with its own real committed note, and
    # the A14 pin with A14's, by ancestry and committed bytes.
    a16_note = subprocess.run(['git', 'show', A16_COMMIT + ':' + NOTE_PATH], cwd=repo, capture_output=True, check=True).stdout
    monkeypatch.setattr(a.subprocess, 'run', _git_stub(a16_note))
    old = dict(commit=A16_COMMIT, path=pin['path'], sha256=hashlib.sha256(a16_note).hexdigest())
    assert a.verify_registration(old, tmp_path, instrument=A10, historical=True) == old
    a14_note = b'Amendment A10\nAmendment A11\nClarified, 2026-10-16: pricing R_max\n### Amendment A14\n'
    monkeypatch.setattr(a.subprocess, 'run', _git_stub(a14_note))
    old = dict(commit=a.A14_COMMIT, path=pin['path'], sha256=hashlib.sha256(a14_note).hexdigest())
    assert a.verify_registration(old, tmp_path, instrument=A10, historical=True) == old
    # R4 pins are untouched by the constants.
    monkeypatch.setattr(a.subprocess, 'run', _git_stub(committed))
    r4 = dict(commit='any', path=pin['path'], sha256=pin['sha256'])
    assert a.verify_registration(r4, tmp_path) == r4


def test_real_repository_historical_verification_of_the_a17_pin():
    """Against the real repository: the A17 pin verifies historically (ancestry
    and committed bytes); strict verification passes only on a committed and
    clean tree (the registered source rule), so it is refused while this build
    is uncommitted and passes once it is committed; the A16 pin verifies
    historically and is refused as current either way, as is the A14 pin."""
    repo = a.SIMULATION.parent
    committed = subprocess.run(['git', 'show', A17_COMMIT + ':' + NOTE_PATH], cwd=repo, capture_output=True, check=True).stdout
    pin = dict(commit=A17_COMMIT, path=NOTE_PATH, sha256=hashlib.sha256(committed).hexdigest())
    assert a.verify_registration(pin, repo, instrument=A10, historical=True) == pin
    # The registered source rule, as verify_registration applies it: tracked
    # changes under simulation, or untracked files at manifest paths. Untracked
    # scratch outside the manifest (_pytest_v3, service.lock) is clean.
    tracked = subprocess.run(['git', 'diff', 'HEAD', '--', 'simulation'], cwd=repo, capture_output=True, text=True,
                             check=True).stdout.strip()
    identities = ['simulation/' + name for name in a.source_manifest()]
    untracked = subprocess.run(['git', 'ls-files', '--others', '--', *identities], cwd=repo, capture_output=True,
                               text=True, check=True).stdout.strip()
    if tracked or untracked:
        with pytest.raises(RuntimeError, match='committed and clean'):
            a.verify_registration(pin, repo, instrument=A10)
    else:
        assert a.verify_registration(pin, repo, instrument=A10) == pin
    a16_note = subprocess.run(['git', 'show', A16_COMMIT + ':' + NOTE_PATH], cwd=repo, capture_output=True, check=True).stdout
    a16 = dict(commit=A16_COMMIT, path=NOTE_PATH, sha256=hashlib.sha256(a16_note).hexdigest())
    assert a.verify_registration(a16, repo, instrument=A10, historical=True) == a16
    for other in (A16_COMMIT, a.A14_COMMIT):
        with pytest.raises(RuntimeError, match='stage 2 pin'):
            a.verify_registration(dict(pin, commit=other), repo, instrument=A10)


def test_successor_constant_unset_state_keeps_a14_current(unset):
    assert a.STAGE2_COMMIT is None and a.STAGE2_AMENDMENT_MARKER is None
    assert a.current_a10_commit() == a.A14_COMMIT
    assert a.current_a10_note_markers() == a.STAGE2_NOTE_MARKERS == A14_MARKERS
    assert a.is_current_a10_pin(a.A14_COMMIT) and a.is_current_a10_pin(a.A14_COMMIT[:8])
    assert not a.is_current_a10_pin(a.A13_COMMIT) and not a.is_current_a10_pin(SUCCESSOR)
    # A16 was a current pin once, so it stays bound even with the successor unset.
    assert set(a.a13_binding_pins()) == {a.A13_COMMIT, a.A13_COMMIT[:8], a.A14_COMMIT, a.A14_COMMIT[:8], A16_COMMIT, A16_COMMIT[:8]}


def test_a14_pin_verifies_exactly_as_before_while_unset(unset, tmp_path, monkeypatch):
    path = _note(tmp_path, A14_TEXT)
    pin = dict(commit=a.A14_COMMIT, path=path.relative_to(tmp_path).as_posix(), sha256=hashlib.sha256(A14_TEXT).hexdigest())
    monkeypatch.setattr(a.subprocess, 'run', _git_stub(A14_TEXT))
    assert a.verify_registration(pin, tmp_path, instrument=A10) == pin
    with pytest.raises(RuntimeError, match='A14 pin 17f17ef9'):
        a.verify_registration(dict(pin, commit=SUCCESSOR), tmp_path, instrument=A10)
    path.write_bytes(A14_TEXT + b'changed')
    with pytest.raises(RuntimeError, match='stale'):
        a.verify_registration(pin, tmp_path, instrument=A10)


MARKER = b'### Amendment A15, 2026-10-29: the stage 2 ceilings'


def test_successor_pin_is_strict_once_set_and_a14_becomes_historical(tmp_path, monkeypatch):
    # A hypothetical successor commit, set without its marker first.
    monkeypatch.setattr(a, 'STAGE2_COMMIT', SUCCESSOR)
    monkeypatch.setattr(a, 'STAGE2_AMENDMENT_MARKER', None)
    assert a.current_a10_commit() == SUCCESSOR and a.is_current_a10_pin(SUCCESSOR[:8])
    assert not a.is_current_a10_pin(a.A14_COMMIT) and not a.is_current_a10_pin(A16_COMMIT)
    assert set(a.a13_binding_pins()) == {a.A13_COMMIT, a.A13_COMMIT[:8], a.A14_COMMIT, a.A14_COMMIT[:8],
                                         A16_COMMIT, A16_COMMIT[:8], SUCCESSOR, SUCCESSOR[:8]}
    # A later successor's note is a superset: A14's text, A16's heading and its own.
    text = A14_TEXT + A16_MARKER + b'\n' + MARKER + b'\n'
    path = _note(tmp_path, text)
    pin = dict(commit=SUCCESSOR, path=path.relative_to(tmp_path).as_posix(), sha256=hashlib.sha256(text).hexdigest())
    monkeypatch.setattr(a.subprocess, 'run', _git_stub(text))
    # The successor commit set without its amendment marker is refused outright.
    with pytest.raises(RuntimeError, match='without its amendment marker'):
        a.verify_registration(pin, tmp_path, instrument=A10)
    monkeypatch.setattr(a, 'STAGE2_AMENDMENT_MARKER', MARKER)
    assert a.current_a10_note_markers() == a.STAGE2_NOTE_MARKERS + a.STAGE2_PRIOR_MARKERS + (MARKER,)
    assert a.verify_registration(pin, tmp_path, instrument=A10) == pin
    # A committed note at the successor commit that lacks the amendment, or that
    # lacks the retained A16 heading, is refused.
    for lacking in (A14_TEXT + A16_MARKER + b'\n### Amendment A15, something else\n', A14_TEXT + MARKER + b'\n'):
        monkeypatch.setattr(a.subprocess, 'run', _git_stub(lacking))
        path.write_bytes(lacking)
        with pytest.raises(RuntimeError, match='stage 2 pin'):
            a.verify_registration(dict(pin, sha256=hashlib.sha256(lacking).hexdigest()), tmp_path, instrument=A10)
    path.write_bytes(text)
    monkeypatch.setattr(a.subprocess, 'run', _git_stub(text))
    # The A14 pin is no longer current: strict verification refuses it, and the
    # historical form still verifies by ancestry and committed bytes.
    old = dict(commit=a.A14_COMMIT, path=pin['path'], sha256=hashlib.sha256(A14_TEXT).hexdigest())
    monkeypatch.setattr(a.subprocess, 'run', _git_stub(A14_TEXT))
    with pytest.raises(RuntimeError, match='stage 2 pin ' + SUCCESSOR[:8]):
        a.verify_registration(old, tmp_path, instrument=A10)
    assert a.verify_registration(old, tmp_path, instrument=A10, historical=True) == old
    # Exact-note checks stay strict for the successor: a stale working note, a
    # wrong path and a committed note missing A14's text are each refused.
    monkeypatch.setattr(a.subprocess, 'run', _git_stub(text))
    path.write_bytes(text + b'local edit')
    with pytest.raises(RuntimeError, match='stale'):
        a.verify_registration(pin, tmp_path, instrument=A10)
    path.write_bytes(text)
    with pytest.raises(RuntimeError, match='stage 2 pin'):
        a.verify_registration(dict(pin, path='simulation/diagnostics/other.md'), tmp_path, instrument=A10)
    short = b'Amendment A10\nAmendment A11\n'
    monkeypatch.setattr(a.subprocess, 'run', _git_stub(short))
    with pytest.raises(RuntimeError, match='stage 2 pin'):
        a.verify_registration(dict(pin, sha256=hashlib.sha256(short).hexdigest()), tmp_path, instrument=A10)
    # R4 pins are untouched by the constant.
    r4 = dict(commit='any', path=pin['path'], sha256=hashlib.sha256(text).hexdigest())
    monkeypatch.setattr(a.subprocess, 'run', _git_stub(text))
    assert a.verify_registration(r4, tmp_path) == r4


@pytest.mark.parametrize('stage', ['a4', 'a5'])
@pytest.mark.parametrize('successor', [None, SUCCESSOR, A16_COMMIT, A17_COMMIT])
@pytest.mark.parametrize('commit', [a.A14_COMMIT, a.A14_COMMIT[:8], a.A13_COMMIT, SUCCESSOR, SUCCESSOR[:8], A16_COMMIT,
                                    A16_COMMIT[:8], A17_COMMIT, A17_COMMIT[:8], 'historical'])
def test_publication_selects_the_current_pin_through_the_shared_helper(tmp_path, monkeypatch, stage, successor, commit):
    from v3 import table_labels_a5 as a5, table_validation_a4 as a4, tables_a10
    monkeypatch.setattr(a, 'STAGE2_COMMIT', successor)
    monkeypatch.setattr(a, 'STAGE2_AMENDMENT_MARKER', _marker_for(successor))
    calls = []
    def verify(*args, **kwargs):
        calls.append(kwargs)
        raise RuntimeError('pin checked before outputs')
    monkeypatch.setattr(a, 'verify_registration', verify)
    monkeypatch.setattr(a5, 'verify_registration', verify)
    monkeypatch.setattr(tables_a10, 'verify_estimation_source', lambda *args, **kw: None)
    plan = dict(registered=True, registration={'commit': commit}, instrument=tables_a10.NOMINAL,
                calibration_path='unused', jobs=[])
    with pytest.raises(RuntimeError, match='pin checked'):
        if stage == 'a4': a4.publish(plan, tmp_path, tmp_path, {}, tmp_path / 'never.json')
        else: a5.publish(plan, tmp_path, tmp_path, tmp_path, {}, tmp_path / 'never.json')
    current = successor or a.A14_COMMIT
    assert calls[0]['historical'] == (commit not in (current, current[:8]))


@pytest.mark.parametrize('successor', [None, SUCCESSOR, A16_COMMIT, A17_COMMIT])
@pytest.mark.parametrize('commit', [a.A14_COMMIT, a.A13_COMMIT[:8], SUCCESSOR, A16_COMMIT, A16_COMMIT[:8], A17_COMMIT,
                                    A17_COMMIT[:8], 'historical'])
def test_a4_part2_binding_follows_the_pin_helper(tmp_path, monkeypatch, successor, commit):
    """The A13 Part 2 binding site is reached for exactly the pins the shared
    helper names; a successor pin accepted by artifacts.py cannot skip it. With
    the real A17 value the binding applies for the A17 pin and for A13, A14 and
    A16; the A16 forms stay bound whatever the successor is."""
    from v3 import table_validation_a4 as a4, tables_a10, admission_a13 as admit
    monkeypatch.setattr(a, 'STAGE2_COMMIT', successor)
    monkeypatch.setattr(a, 'STAGE2_AMENDMENT_MARKER', _marker_for(successor))
    expected = commit in a.a13_binding_pins()
    assert expected == (commit in {a.A13_COMMIT[:8], a.A14_COMMIT, A16_COMMIT, A16_COMMIT[:8]}
                        or (successor is not None and commit in (successor, successor[:8])))
    monkeypatch.setattr(a, 'verify_registration', lambda *args, **kw: None)
    monkeypatch.setattr(tables_a10, 'verify_estimation_source', lambda *args, **kw: None)
    monkeypatch.setattr(a4, 'registered_publish_guard', lambda p: None)
    monkeypatch.setattr(a4, '_recompute_plan_hash', lambda p: p['plan_hash'])
    monkeypatch.setattr(a4, 'counts_from_job_outputs', lambda *args, **kw: {'M': 1, 'M_FV': 0})
    monkeypatch.setattr(a4, '_verify_stage_outputs', lambda plan, root: ({}, {}))
    monkeypatch.setattr(a4, 'assemble_family', lambda *args, **kw: ({}, 'passed', []))
    from v3 import calibration as cal
    monkeypatch.setattr(cal, 'validate_calibration', lambda document, **kw: document)
    from v3 import compatibility_a10 as compat
    monkeypatch.setattr(compat, 'accepted_identities', lambda: {a.code_identity()})
    reached = []
    def binding(*args, **kwargs):
        reached.append(args[2])
        raise RuntimeError('binding reached')
    monkeypatch.setattr(admit, 'checked_binding', binding)
    from v3 import production_tables as pt
    def write(*args, **kwargs):
        raise RuntimeError('write reached without the binding')
    monkeypatch.setattr(pt, 'write_tables', write)
    source = tmp_path / 'source'
    source.mkdir()
    a.atomic_json(source / 'v3_rerun_tables_A1.json', a.seal({'manifest': {'a10': {'family': 'sqrt'}}}))
    a.atomic_json(source / 'tables_A1_manifest.json', a.seal({'jobs': []}))
    plan = dict(registered=True, registration={'commit': commit}, instrument=tables_a10.NOMINAL,
                calibration_path='unused', jobs=[], source_file_sha256=a.file_hash(source / 'v3_rerun_tables_A1.json'),
                source_manifest_sha256=a.digest(a.unseal(a.read(source / 'tables_A1_manifest.json'))),
                code_hash=a.code_identity(), plan_hash='p', M=1, M_FV=0, source_code_hash='s', stream_tags=[])
    calibration = {'sha256': 'c'}
    with pytest.raises(RuntimeError, match='binding reached' if expected else 'write reached without the binding'):
        a4.publish(plan, tmp_path / 'run', source, calibration, tmp_path / 'never.json')
    assert bool(reached) == expected
    if expected:
        assert reached == ['validation_launched_under_A13']


@pytest.mark.parametrize('stage', ['a4', 'a5'])
def test_publication_with_the_set_constants_treats_a16_as_historical_and_a17_as_current(tmp_path, monkeypatch, stage):
    """No monkeypatch of the constants: the A16, A14 and A13 pins now verify
    historically through both publish sites and the A17 pin strictly."""
    from v3 import table_labels_a5 as a5, table_validation_a4 as a4, tables_a10
    calls = []
    def verify(*args, **kwargs):
        calls.append(kwargs)
        raise RuntimeError('pin checked before outputs')
    monkeypatch.setattr(a, 'verify_registration', verify)
    monkeypatch.setattr(a5, 'verify_registration', verify)
    monkeypatch.setattr(tables_a10, 'verify_estimation_source', lambda *args, **kw: None)
    for commit, historical in ((a.A14_COMMIT, True), (a.A13_COMMIT, True), (A16_COMMIT, True), (A16_COMMIT[:8], True),
                               (A17_COMMIT, False), (A17_COMMIT[:8], False)):
        calls.clear()
        plan = dict(registered=True, registration={'commit': commit}, instrument=tables_a10.NOMINAL,
                    calibration_path='unused', jobs=[])
        with pytest.raises(RuntimeError, match='pin checked'):
            if stage == 'a4': a4.publish(plan, tmp_path, tmp_path, {}, tmp_path / 'never.json')
            else: a5.publish(plan, tmp_path, tmp_path, tmp_path, {}, tmp_path / 'never.json')
        assert calls[0]['historical'] is historical, commit
