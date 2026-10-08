"""A10 items 0-9 and executable certified properties on local toy fixtures."""
import copy
from dataclasses import replace
import hashlib
import json
import math
import pickle
from pathlib import Path
from unittest.mock import patch
import numpy as np
import pytest
from v3.artifacts import ROOT, SIMULATION, read, seal, unseal, digest, code_identity
from v3.instrument import (Instrument, R4, V_MAX, TAU, EPSILON_L, W_REF, TR_REF,
                           CONSTANTS_SHA256, validate_constants, allocation_horizon)
from v3.context import Context, reproductive_support, observable_features, score_features
from v3.engine import RuleBatch, advance, measurements_and_flow, ChannelRandom
from v3.integration import V3Model
from v3.plans import CompletePlan, Epoch, plan_value, compare_plans, YieldDecision
from v3.objective import ValueBound
from v3.policies import execution_policy_class
from test_v3_paths import tmp_path

A10 = Instrument("A10", 1.8, "linear")


def context(cap=1., g="linear"):
    return Context.build({"n_agents": 4, "carrying_capacity": 80, "reproduction_rate": .064,
                          "capability": cap, "instrument": Instrument("A10", 1.8, g).declaration()})


def test_both_certifiers_claude_numerical_checks_are_assertions():
    # Port the certifier's printed criteria as assertions on the same grids.
    cap = .014666388971338522
    assert abs(V_MAX - .2071536032807397) <= 1e-15
    assert abs(math.log(5) - math.log(.01) - math.log(500)) <= 1e-15
    assert abs(V_MAX / (1 + math.log(1 / EPSILON_L) / .5) - cap) < 1e-12
    for k, stated in ((1.5, .007502), (1.8, .010875), (2.3, .014666)):
        floor = min(cap, math.log(k) / 30 * .325 / (W_REF * TR_REF))
        assert abs(floor - stated) <= 5e-6
        assert math.exp(-.5 * max(0., V_MAX / floor - 1)) <= EPSILON_L * (1 + 1e-12)

    def theta(v, b, tr, alpha):
        return math.exp(-(1-tr)*v/V_MAX) * math.exp(-alpha*max(0., v/max(b, cap)-1))

    for tr in (0., .3, .7, 1.):
        for b in (1e-4, .01, .1, 1.):
            for alpha in (.5, 1., 1.5):
                for v in (0., 1e-6, .05, V_MAX):
                    value = theta(v, b, tr, alpha)
                    assert 0 <= value <= 1 + 1e-15
                    if v == 0:
                        assert abs(value - 1) <= 1e-15
    for b in (1e-4, .1):
        sequence = [theta(v, b, .5, 1.5) for v in (1e-2, 1e-4, 1e-8, 0.)]
        assert sequence == sorted(sequence) and sequence[-1] == 1.

    def benefit(c, g):
        return c if g == 'linear' else math.sqrt(c)

    def h_e(c, x, g):
        return -math.expm1(-2.5 * benefit(c, g) * x)

    values = [h_e(c, x, g) for g in ('linear', 'sqrt')
              for c in (1., 1.2, 1.5, 2.25, 3.375, 5.) for x in (0., 1/6, .5, 1.)]
    assert min(values) == 0 and max(values) < 1
    assert h_e(5., 0., 'linear') == 0
    increments = [max(40, 38 + 12 * benefit(c, g) * share)
                  for g in ('linear', 'sqrt') for c in (1., 1.2, 5.) for share in (1/6, .5, 1.)]
    assert min(increments) >= 40

    def stationary_flow(c, g='linear'):
        return (5 * math.log(1 + .16136550941334515)
                + 3 * math.log(h_e(c, 1/6, g) + .0034075936979955646)
                + 8 * math.log(.5 + EPSILON_L))

    for g in ('linear', 'sqrt'):
        assert stationary_flow(1.2, g) > stationary_flow(1., g)
    gain = stationary_flow(1.2) - stationary_flow(1.)
    beta, pace, bandwidth = math.exp(-.01), math.log(1.2)/30, math.log(1.8)/30
    for alpha in (.5, 1.5):
        response = theta(pace, bandwidth, .73, alpha)
        loss = 8 * (math.log(.5 + EPSILON_L) - math.log(.5 * response + EPSILON_L))
        transient = sum((1-beta) * beta**t for t in range(30)) * loss
        assert gain > transient


def test_item6_a10_producer_receipt_binds_validation_and_own_capability_labels(tmp_path):
    from v3.artifacts import atomic_json, file_hash
    from v3.production_tables import write_tables, ProductionTables, row_key
    from v3.tables_a10 import finalize_receipt
    from v3.continuation_validation import fine_codes
    from v3.table_labels_a5 import label_for
    row = {'rule_id': 'balanced', 'kernel_hash': 'synthetic-A10', 'calibration_hash': 'synthetic',
           'scoring': {'alpha': 1., 'capability': 1.5, 'kappa': 8., **A10.declaration()},
           'route': 'fv', 'status': 'estimated', 'lambda_f': {'mean': 0.}, 'flow_range': 100.,
           'continuation': {'entries': [{'bin': [1,1,1,1,1,1], 'value': 0., 'error': 100.}]}}
    manifest = {'tag': 'v3_tables', 'calibration_hash': 'synthetic', 'complete_family': True,
                'sensitivity_status': 'passed', 'required_row_keys': [row_key(row)],
                'a10': {'producer_code_hash': code_identity(), 'constants_sha256': CONSTANTS_SHA256,
                        'instruments': [A10.declaration()]}}
    path = tmp_path / 'synthetic_table.json'
    doc = write_tables(path, [row], manifest, fixture=False)
    table = ProductionTables(path, calibration_hash='synthetic')
    with pytest.raises(ValueError, match='receipt'):
        table.require_a10(A10)
    validation = {'schema': 'v3-A4-receipt-1', 'producer_code_hash': code_identity(),
                  'table_seal_sha256': doc['sha256'], 'table_file_sha256': file_hash(path)}
    labels = {'schema': 'v3-A5-label-1', 'code_hash': code_identity(),
              'a4_family': {'table_seal_sha256': doc['sha256'], 'family_file_sha256': file_hash(path)},
              'rows': [{'row_key': row_key(row), 'scoring': row['scoring'],
                        'cells': [{'cell': int(fine_codes([[1,1,1,1,1,1]])[0]), 'status': 'unresolved',
                                   'label': label_for('unresolved')}]}]}
    atomic_json(path.with_suffix('.compatibility.json'), seal(validation))
    label_path = tmp_path / 'labels.json'
    atomic_json(label_path, seal(labels))
    frozen_bytes = path.read_bytes()
    receipt = finalize_receipt(path, label_path)
    assert path.read_bytes() == frozen_bytes
    table = ProductionTables(path, calibration_hash='synthetic', registered=True)
    table.require_a10(A10)
    with pytest.raises(ValueError, match='producer or instrument'):
        table.require_a10(Instrument('A10', 1.8, 'sqrt'))
    bad = unseal(copy.deepcopy(receipt))
    bad['constants_sha256'] = '0' * 64
    table.a10_receipt = seal(bad)
    with pytest.raises(ValueError, match='receipt'):
        table.require_a10(A10)
    labels['rows'][0]['scoring'] = dict(row['scoring'], capability=2.)
    bad = unseal(copy.deepcopy(receipt))
    bad['labels'] = seal(labels)
    from v3.artifacts import canonical
    bad['labels_sha256'] = hashlib.sha256(canonical(bad['labels']) + b'\n').hexdigest()
    table.a10_receipt = seal(bad)
    with pytest.raises(ValueError, match='own validated cells'):
        table.require_a10(A10)


def test_item9_projection_arithmetic_keeps_toy_and_local_costs_non_registered(monkeypatch):
    from v3.pilot_a10 import project
    import v3.production_runner as runner
    phases = ['sigma_squared_x0.1.1.0.primary.' + k for k in ('estimate','validate_plain','validate_fv','labels')]
    phases += ['runs.a6_horizon.linear.1.8']
    jobs = [{'id': str(i), 'config': {'phase': p}} for i,p in enumerate(phases)]
    spec = {'toy': False, 'code_hash': code_identity(), 'jobs': jobs,
            'strata': {p: {'population_jobs': 10, 'family': 'sigma_squared_x0.1'} for p in phases}}
    outputs = {'result': {'cost_only': True, 'seconds': 100., 'length_fraction': .5,
                          'scoring_seconds_by_k_star': {'1.5': 1., '1.8': 2., '2.3': 1.}},
               'runtime': {'machine': 'YotkoTest'}}
    monkeypatch.setattr(runner, 'completed', lambda *a: outputs)
    configs = {p: [{'valid': True,'workers': 2,'threads': 1,'job_seconds': [100.,100.],'wall_seconds': 125.}] for p in phases}
    chosen = {p: {'workers':2,'threads':1} for p in phases}
    local = project(spec, '.', configs, chosen)
    assert local['status'] == 'local_costs_only' and local['total_x2_hours_conservative'] is None
    x2 = project(spec, '.', configs, chosen, relative_to_x2=.4)
    phase_hours = 200 * 10 / 1.6 / 3600 * 1.35 * .4
    assert x2['components_x2_hours_before_reserves']['sigma_squared_x0.1.tables'] == pytest.approx(3*phase_hours)
    assert x2['components_x2_hours_before_reserves']['runs.a6_horizon.linear.1.8'] == pytest.approx(phase_hours)
    assert x2['non_registered'] and not x2['results_eligible']
    toy = project(dict(spec, toy=True), '.', configs, chosen, relative_to_x2=.4)
    assert toy['status'] == 'toy_execution_only' and toy['total_x2_hours_conservative'] is None


def test_item0_declaration_and_registered_mode_refuse_undeclared_values():
    for value in ("unknown", "a10", ""):
        with pytest.raises(ValueError):
            Instrument(value)
    for args in (("A10", None, "linear"), ("A10", 1.7, "linear"), ("A10", 1.8, "c"), ("R4", 1.8, "linear")):
        with pytest.raises(ValueError):
            Instrument(*args)
    with pytest.raises(ValueError, match="refuses R4"):
        V3Model(registered_a10=True)


def test_review_output_scope_matches_base():
    import ast
    import inspect
    import subprocess
    from v3.artifacts import scoped
    base = subprocess.check_output(['git', '-C', str(SIMULATION.parent), 'show',
                                    'fe98280c:simulation/v3/artifacts.py']).decode('utf-8')
    original = next(n for n in ast.parse(base).body if isinstance(n, ast.FunctionDef) and n.name == 'scoped')
    assert ast.dump(ast.parse(inspect.getsource(scoped)).body[0]) == ast.dump(original)
    assert scoped(ROOT / 'fixture.json') == ROOT / 'fixture.json'
    for outside in (SIMULATION, SIMULATION.parent / 'review_fixture', ROOT / '..'):
        with pytest.raises(ValueError, match='output outside simulation/v3'):
            scoped(outside)


def test_item1_constants_exact_record_seal_and_calibration():
    p = validate_constants()
    from v3.artifacts import canonical
    raw = canonical(p["provenance"]["record"]) + b"\n"
    assert p["provenance"]["record_sha256"] == hashlib.sha256(raw).hexdigest()
    assert p["provenance"]["record"]["exact_historical_replay"] is False
    assert (p["w_ref"], p["tr_ref"], p["epsilon_l"], p["tau"], p["v_max"]) == (W_REF, TR_REF, EPSILON_L, 30, V_MAX)
    assert read(ROOT / "runs/registered/v3_a10_constants.json") == read(ROOT / "a10_constants.json")
    changed = copy.deepcopy(p)
    changed["tau"] = 29
    with pytest.raises(ValueError, match="seal"):
        validate_constants(seal(changed))
    from v3.calibration import validate_calibration
    frozen = read(ROOT / "runs/registered/v3_rerun_calibration.json")
    assert validate_calibration(frozen, registered=True, instrument=A10)["values"]["epsilon_l"] == EPSILON_L


@pytest.mark.parametrize("k", [1.5, 1.8, 2.3])
def test_item2_theta_certified_properties_all_arms(k):
    m = Instrument("A10", k, "linear")
    for alpha in (.5, .75, 1., 1.25, 1.5):
        for tr in (0., .01, .5, .73, 1.):
            for w in (0., .01, .65, .8, 1.):
                theta, b, u = m.response(np.array([0., 1e-12, m.floor, V_MAX]), w, tr, alpha)
                assert theta[0] == 1.
                assert np.all((theta > 0) & (theta <= 1)) and np.isfinite(u).all()
                assert abs(theta[1] - 1) < 1e-9
            theta, _, _ = m.response(V_MAX, 0., tr, alpha)
            assert theta <= EPSILON_L
    # Continuity through the clipping boundary and overload kink.
    b_ref = math.log(k)/30
    w = m.floor * W_REF * TR_REF / b_ref
    values = [float(m.response(m.floor, w + d, 1., 1.)[0]) for d in (-1e-10, 0., 1e-10)]
    assert max(values) - min(values) < 1e-7


def test_item2_history_startup_copy_clone_checkpoint_and_window_exit():
    ctx = context()
    state = ctx.population(3, np.random.default_rng(4))
    original = state.frontier_history.copy()
    state.stocks[:, 2] = 60
    A10.append(state, 1.)
    assert np.allclose(A10.velocity(state), math.log(.6/.5)/30)
    state.frontier_history[1] += .1
    clone = state.copy_rows([1, 1, 0])
    assert np.array_equal(clone.frontier_history[0], state.frontier_history[1])
    clone.frontier_history[0, 0] += .2
    assert clone.frontier_history[1, 0] != clone.frontier_history[0, 0]
    restored = pickle.loads(pickle.dumps(state))
    assert np.array_equal(restored.frontier_history, state.frontier_history)
    state.frontier_history[:] = original
    state.stocks[:, 2] = 50
    for step in range(1, 32):
        A10.append(state, 1.5)
        assert np.allclose(A10.velocity(state), math.log(1.5)/30 if step <= 30 else 0.)
    assert np.all(A10.response(A10.velocity(state), .8, .7, 1.)[0] == 1.)


@pytest.mark.parametrize("g", ["linear", "sqrt"])
def test_item3_c1_c2_extinction_and_cohort_floor(g):
    inst = Instrument("A10", 1.8, g)
    ctx = context(5., g)
    s = ctx.population(2, np.random.default_rng(10))
    actions = np.full((2, 6), 1/6)
    actions[1] = [0, 1, 0, 0, 0, 0]
    values, measures = measurements_and_flow(s, actions, ctx.parameters, 1., 5., instrument=inst)
    assert np.allclose(measures["h_e"], -np.expm1(-2.5 * inst.benefit(5.) * actions[:, 0]))
    assert measures["h_e"][1] == 0
    assert np.all(values >= ctx.parameters.extinction_flow)
    from v3.conformance import floor_audit
    for cap in (1., 1.2, 5.):
        result = floor_audit(inst, cap)
        assert result["welfare_violations"] == result["reproduction_violations"] == 0
    # C2 is applied in the actual transition before mortality.
    s.ages[:] = 20
    s.welfare[:] = 600
    advance(s, actions, ChannelRandom(20), .064, 80, ctx.protocol, instrument=inst, capability=5.)
    for row in range(2):
        adult = s.ages[row] == 21
        expected = 600 + max(40, 38 + 12 * float(inst.benefit(5.)) * actions[row, 1]) - 21
        assert np.all(np.isin(s.welfare[row, adult], [math.floor(expected), math.ceil(expected)]))


def test_item4_equal_f1_horizons_own_capability_crn_and_offset(monkeypatch):
    model = V3Model(4, seed=23, rules=execution_policy_class()[:2], instrument=A10)
    model._open_period()
    calls = []
    original = model.evaluate
    def tracked(**kw):
        calls.append(kw)
        return original(**kw)
    monkeypatch.setattr(model, "evaluate", tracked)
    event = model.review_yield(0)
    assert {c["horizon"] for c in calls} == {55}
    assert {c["seed_channel"] for c in calls} == {"yield_common"}
    assert event["evaluation_endpoint"] == 55 and event["decision_deadline"] == 25
    beta = math.exp(-.01)
    for now, origin, deadline in ((0,0,25),(10,0,25),(20,0,25),(30,25,50),(40,25,50)):
        ep = Epoch("e", origin, deadline, beta, .5, -100, "p", "i")
        H = deadline+30
        p = CompletePlan("hold", "e", "p", "i", -100, now, H, None, (0.,)*(H-now), ValueBound(1.), 0., True, "fixture", 1., decision_deadline=deadline)
        assert math.isclose(plan_value(p, ep, now).value, .5 * beta**55, abs_tol=1e-15)
        with pytest.raises(ValueError):
            plan_value(replace(p, first_yield=deadline+1), ep, now)
    captured = []
    import v3.integration as integration
    real = integration.advance
    def capture(*args, **kwargs):
        captured.append(kwargs["capability"])
        return real(*args, **kwargs)
    monkeypatch.setattr(integration, "advance", capture)
    original(horizon=4, capability=1.5, transition_at=2, incumbent_index=0)
    assert captured == [1., 1., 1.5, 1.5]


def test_item5_allocation_extension_edges():
    assert [allocation_horizon(t, 10) for t in (9,10,11,19,20,39,40,41)] == [20,30,29,21,20,20,20,20]
    model = V3Model(0, instrument=A10, successor_capability=None)
    model.time, model.last_handover = 10, 10
    assert len(model.evaluate().flows) == 30
    model.time = 40
    assert len(model.evaluate().flows) == 20


def test_item6_physical_kernels_scoring_and_step30(monkeypatch):
    from v3.offline_estimator import simulate, summarize
    from v3.tables_a10 import build_jobs, contexts
    a, b, c = context(1.), context(5.), context(5., "sqrt")
    assert len({a.kernel_hash,b.kernel_hash,c.kernel_hash}) == 3
    assert context(1.).kernel_hash != context(1., "sqrt").kernel_hash
    # g(1)=1 gives identical physical paths despite distinct declared identities.
    settings = {"groups":3,"runs_per_group":2,"particles":2,"burn":30,"measure":8}
    rule = execution_policy_class()[0]
    left = simulate(a, rule, settings, 41, "plain")
    right = simulate(context(1., "sqrt"), rule, settings, 41, "plain")
    assert np.array_equal(left["features"], right["features"])
    captured = []
    from v3.continuation import fit_transitions
    def fitting(*args, **kwargs):
        captured.append(args)
        return fit_transitions(*args, **kwargs)
    monkeypatch.setattr("v3.offline_estimator.fit_transitions", fitting)
    summary = summarize(left, a, settings, 1., 1.)
    assert captured and np.array_equal(captured[0][0], left["before"][30:])
    assert summary["continuation"]["first_source_step"] == 30
    with pytest.raises(ValueError, match="another capability"):
        score_features(left["features"], a, 1., 5.)
    jobs = build_jobs("nominal")
    pairs = {(j["config"]["kernel"]["reproduction_rate"],j["config"]["kernel"]["capability"]) for j in jobs}
    assert pairs == {(r,c) for r,_,c in contexts("nominal")} and len(pairs) == 105
    for job in jobs:
        cfg=job["config"]
        assert all(s["capability"] == cfg["kernel"]["capability"] for s in cfg["scoring"])
    assert {s["k_star"] for j in jobs for s in j["config"]["scoring"]} == {1.5,1.8,2.3}


def test_item6_fertility_support_and_rounding_upper_path():
    ctx = context(5.)
    state = ctx.population(1, np.random.default_rng(1))
    state.ages[:] = 48
    state.welfare[:] = 485
    assert not reproductive_support(state)[0]
    for g in ("linear","sqrt"):
        assert reproductive_support(state, 5., Instrument("A10",1.8,g))[0]
    # At c=1.2, max increment=52.4 can round up to 53. The upper support
    # retains age48,w496, whose next-age49 upper welfare is exactly500.
    state.welfare[:] = 496
    assert reproductive_support(state, 1.2, A10)[0]


def test_item7_shadow_never_reaches_guard_and_schema_is_new(monkeypatch):
    from v3.recording import RecordedV3Model, pack_evidence, unpack_evidence, A10_SCHEMA
    model = RecordedV3Model(1, seed=17, rules=execution_policy_class()[:2], instrument=A10)
    model.state.ages[:] = 99
    model._open_period()
    assert not model.period.admitted
    before = pickle.dumps(model.state)
    rng_before = pickle.dumps(np.random.get_state())
    monkeypatch.setattr(model.guards, "authorize", lambda *a, **k: (_ for _ in ()).throw(AssertionError("shadow reached guard")))
    real = compare_plans
    seen=[]
    def comparison(plans, ep, now):
        seen.append(real(plans, ep, now))
        return YieldDecision(True, plans[0].plan_id, None, 1., 0., True)
    monkeypatch.setattr("v3.integration.compare_plans", comparison)
    event = model.review_yield(0)
    assert seen and event["shadow_decision"]["yield_now"] and event["transition_count"] == 0
    assert event["decision"] is None
    assert pickle.dumps(model.state) == before and pickle.dumps(np.random.get_state()) == rng_before
    assert model.capability == 1. and model.transition_count == 0
    assert event["gate_evidence"]["schema"] == A10_SCHEMA
    assert all(p["terminal_time"] == 55 and p["decision_deadline"] == 25 for p in event["gate_evidence"]["plans"])
    result=pack_evidence({"diagnostics":[],"yield_events":[copy.deepcopy(event)]})
    assert result["gate_evidence"]["schema"] == A10_SCHEMA
    assert unpack_evidence(result)["yield_events"][0]["gate_evidence"]["schema"] == A10_SCHEMA


def test_review_unadmitted_shadow_yield_is_not_an_acted_decision(monkeypatch):
    from v3.recording import RecordedV3Model, pack_evidence, unpack_evidence
    from v3.gates import check_review, check_shadow
    model = RecordedV3Model(1, seed=17, rules=execution_policy_class()[:1], instrument=A10)
    model.state.ages[:] = 99
    model._open_period()
    assert not model.period.admitted
    state_before = pickle.dumps(model.state)
    rng_before = pickle.dumps(np.random.get_state())
    evaluate = V3Model.evaluate

    def evaluation(self, **kwargs):
        result = evaluate(self, **kwargs)
        # Construct a strict immediate preference. The actual comparator and
        # recorder still operate on complete, consistently scored plans.
        flow = 2. if kwargs.get('transition_at') == 0 else 1.
        result.flows[:] = flow
        result.lookup.continuation[:] = flow
        result.lookup.lambda_f[:] = flow
        return result

    monkeypatch.setattr(V3Model, 'evaluate', evaluation)
    monkeypatch.setattr(model.guards, 'authorize', lambda *a, **k: (_ for _ in ()).throw(AssertionError('unadmitted action')))
    event = model.review_yield(0)
    assert event['shadow_decision']['yield_now'] and event['decision'] is None
    assert event['transition_count'] == model.transition_count == 0 and model.capability == 1.
    assert 'local_gate_authorized' not in event and not event['gate_evidence']['comparison_values']
    assert pickle.dumps(model.state) == state_before and pickle.dumps(np.random.get_state()) == rng_before
    assert check_shadow(event) and check_review(({}, event))
    restored = unpack_evidence(pack_evidence({'diagnostics': [], 'yield_events': [copy.deepcopy(event)]}))['yield_events'][0]
    assert restored['decision'] is None and restored['shadow_decision'] == event['shadow_decision']
    assert check_review(({}, restored))
    restored['decision'] = restored['shadow_decision']
    assert not check_shadow(restored) and not check_review(({}, restored))


@pytest.mark.parametrize("cap", [0., .99, 5.001, float("nan"), float("inf")])
def test_item3_guard_every_boundary(cap):
    with pytest.raises(ValueError):
        context(cap)
    with pytest.raises(ValueError):
        V3Model(1, capability=cap, instrument=A10)
    model=V3Model(1,instrument=A10)
    with pytest.raises(ValueError):
        model.evaluate(horizon=1,capability=cap)
    from v3.recording import undisrupted
    with pytest.raises(ValueError):
        undisrupted(model,horizon=1,capability=cap,transition_at=0,incumbent_index=0,seed_channel="yield_common")
    with pytest.raises(ValueError):
        model._lookup(model.state,model.rules[:1],cap)


def test_item8_registration_requires_a10_without_relaxing_pin(tmp_path, monkeypatch):
    import subprocess
    from v3.artifacts import verify_registration
    text=b"Amendment A10\nAmendment A11\nfixture only\n"
    path=tmp_path/'note.md'
    path.write_bytes(text)
    pin={"commit":"a"*40,"path":"note.md","sha256":hashlib.sha256(text).hexdigest()}
    calls=[]
    def git(command,**kwargs):
        calls.append(command)
        return subprocess.CompletedProcess(command,0,stdout=text if 'show' in command else b'')
    monkeypatch.setattr('v3.artifacts.subprocess.run',git)
    assert verify_registration(pin,tmp_path,instrument=A10) == pin
    assert any('--is-ancestor' in c for c in calls) and any('diff' in c for c in calls)
    text=b"Amendment A9\n"
    path.write_bytes(text)
    pin['sha256']=hashlib.sha256(text).hexdigest()
    with pytest.raises(RuntimeError,match='A10'):
        verify_registration(pin,tmp_path,instrument=A10)


def test_item9_pilot_hash_sample_and_pairing():
    from v3.tables_a10 import paired_runs, arm_runs
    from v3.study import rerun_jobs
    from v3.pilot_a10 import hash_sample
    old=rerun_jobs('cal','table')
    new=paired_runs('newcal','newtable',source_calibration_path='cal',source_tables_path='table')
    assert len(new)==24900 and [j['seed'] for j in new]==[j['seed'] for j in old]
    assert all(a['id'] != b['id'] for a,b in zip(old,new))
    arms=arm_runs('cal','table','sqrt')
    assert len(arms)==13200 and len({j['seed'] for j in arms})==13200
    assert hash_sample(new,3,'runs') == hash_sample(list(reversed(new)),3,'runs')


def test_certifier_assertions_and_claude_properties():
    from v3.conformance_a10 import certificate_checks
    result=certificate_checks()
    assert result['execution_welfare']['grid_comparisons']==3003000
    # Claude's independent checks use these bounds and positive witnesses.
    for power in (1.,.5):
        gain=3*math.log((-math.expm1(-2.5*1.2**power/6)+.0034075936979955646)/(-math.expm1(-2.5/6)+.0034075936979955646))
        v=math.log(1.2)/30
        theta=float(A10.response(v,W_REF,TR_REF,1.5)[0])
        loss=8*(math.log(.5+EPSILON_L)-math.log(.5*theta+EPSILON_L))
        assert gain-(1-math.exp(-.3))*loss>0


@pytest.mark.parametrize("name", [
    "test_s10_1_live_window_and_pooled_sampling_law",
    "test_s10_4_executor_extinction_is_absorbing",
    "test_s10_5_reduced_demographic_class_and_stock_support",
    "test_s10_7_actual_welfare_grid_and_failed_bound_precedence",
    "test_s10_9_live_grids_and_dying_parent_birth_order",
    "test_s10_11_period_ledgers_and_closed_loop_initial_law",
    "test_s10_13_independent_local_guards_and_registered_refusal",
    "test_s10_3_batched_diversity_matches_scalar_and_exact_collapse",
    "test_rollouts_preserve_live_state_and_crn_channels",
    "test_absorbed_rollout_has_exact_discounted_continuation",
])
def test_s10_unchanged_contracts_on_a10(name, monkeypatch):
    import test_v3_integration as baseline_tests
    original = baseline_tests.small_model
    monkeypatch.setattr(baseline_tests, "small_model", lambda *a, **k: original(*a, instrument=A10, **k))
    getattr(baseline_tests, name)()


def test_s10_12_actual_handover_once_and_gamma(monkeypatch):
    from v3.recording import RecordedV3Model
    from v3.gates import check_review, gamma_comparisons, reference_plan
    model = RecordedV3Model(200, seed=54, rules=execution_policy_class()[:2], instrument=A10)
    real_compare = compare_plans
    compared = []
    def compare(plans, epoch, now):
        compared.extend(plans)
        return real_compare(plans, epoch, now)
    monkeypatch.setattr("v3.integration.compare_plans", compare)
    model.step()
    review = model.yield_events[0]
    assert check_review(({}, review))
    assert gamma_comparisons(({}, review)) == 6
    assert all(p.terminal_time == 55 and p.decision_deadline == 25 for p in compared)
    assert model.transition_count == review["transition_count"]
    # Force a strict tie in complete F1 plans. Admission and original epoch
    # units remain unchanged, and the comparison cannot consume a generator.
    plans = [replace(compared[0], plan_id="now", first_yield=0, flows=(0.,)*55, continuation=ValueBound(0.), lambda_f=0.),
             replace(compared[0], plan_id="hold", first_yield=None, flows=(0.,)*55, continuation=ValueBound(0.), lambda_f=0.)]
    original = pickle.dumps((plans, model.state, np.random.get_state()))
    assert not compare_plans(plans, model.epoch, 0).yield_now
    assert pickle.dumps((plans, model.state, np.random.get_state())) == original


def test_item7_empty_shadow_and_independent_checker(monkeypatch):
    from v3.recording import RecordedV3Model
    from v3.production_tables import AvailableLookup
    from v3.gates import check_review
    model = RecordedV3Model(1, instrument=A10, rules=execution_policy_class()[:1])
    model._open_period()
    def missing(*a):
        z = np.full(1, np.nan)
        return AvailableLookup(z.copy(),z.copy(),z.copy(),z.copy(),(None,),(None,),True,np.zeros(1,bool),("fixture_missing",))
    monkeypatch.setattr(model,"_lookup",missing)
    monkeypatch.setattr("v3.integration.compare_plans",lambda *a: (_ for _ in ()).throw(AssertionError("empty comparison")))
    event = model.review_yield(0)
    assert event["shadow_decision"] == "no comparison" and event["transition_count"] == 0
    assert check_review(({},event))


def test_item7_living_start_aggregates_and_old_reader_refusal():
    from v3.production_runner import execute
    from v3.artifacts import stable_job
    from v3.recording import unpack_evidence
    job = stable_job("rerun", {"steps":3,"model":{"n_agents":3,"instrument":A10.declaration()}},"validation",0)
    result = execute(job)
    # Execute the unchanged reader source in a private module namespace; the
    # schema check happens before any content interpretation.
    import subprocess
    old = subprocess.check_output(['git', '-C', str(SIMULATION.parent), 'show',
                                   'fe98280c:simulation/v3/recording.py']).decode('utf-8')
    import ast
    tree = ast.parse(old)
    fn = next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='unpack_evidence')
    namespace={'SCHEMA':'v3-gate-evidence-1'}
    exec(compile(ast.Module(body=[fn],type_ignores=[]),'unchanged_R4_reader','exec'),namespace)
    with pytest.raises(ValueError,match='encoding'):
        namespace['unpack_evidence'](copy.deepcopy(result))
    unpack_evidence(result)
    living = [r for r in result['diagnostics'] if r['population_before']>0]
    d=result['a10_diagnostics']
    assert d['living_start_steps']==len(living)
    assert d['mean_theta']==sum(r['theta'] for r in living)/len(living)
    assert d['theta_one_share']==sum(r['theta']==1 for r in living)/len(living)
    assert d['bandwidth_floor_share']==sum(r['bandwidth_at_floor'] for r in living)/len(living)
    assert d['transition_count']==sum(r['transition_count'] for r in result['yield_events'])
    assert d['final_capability']==result['diagnostics'][-1]['capability']


def test_item6_fv_really_clones_history_and_a4_fit_waits(monkeypatch):
    from v3.engine import PopulationBatch
    from v3.offline_estimator import simulate
    from v3 import table_validation_a4 as a4
    original_copy=PopulationBatch.copy_rows
    clones=[]
    def copying(state, indices):
        result=original_copy(state,indices)
        assert np.array_equal(result.frontier_history,state.frontier_history[indices])
        clones.append(np.asarray(indices).copy())
        return result
    monkeypatch.setattr(PopulationBatch,'copy_rows',copying)
    # Remove exactly one particle in every group on each FV step.
    monkeypatch.setattr('v3.offline_estimator.reproductive_support',lambda state,*a: np.tile([False,True],3))
    ctx=context()
    settings={'groups':3,'runs_per_group':2,'particles':2,'burn':30,'measure':8}
    trace=simulate(ctx,execution_policy_class()[0],settings,512,'fv')
    assert clones and any(len(set(c))<len(c) for c in clones)
    result={'route':'fv','kernel':ctx.config,'settings':settings,'rows':[{'rule_id':'balanced'}]}
    envelope={'result':result,'job':{'config':{}}}
    monkeypatch.setattr('v3.offline_estimator.simulate',lambda *a: copy.deepcopy(trace))
    tr=a4.TableTrace(envelope,1,settings)
    assert tr.length==8 and np.array_equal(tr.before,trace['before'][30:].reshape(-1,6))
    assert np.array_equal(tr.source_alive.reshape(8,6)[0],trace['conditioned'][29,:,0]>0)
    collapsed=copy.deepcopy(trace)
    for k in ('features','conditioned','before','after','support','deaths'):
        collapsed[k]=collapsed[k][:5]
    collapsed['collapsed']=[{'step':4,'group':0}]
    monkeypatch.setattr('v3.offline_estimator.simulate',lambda *a: copy.deepcopy(collapsed))
    tr=a4.TableTrace(envelope,1,settings)
    assert tr.length==0 and tr.truncated and not tr.source_alive.size


@pytest.mark.parametrize('k',[1.5,1.8,2.3])
def test_a10_before_gates_keep_thresholds(k):
    from v3.gates import before_checks
    cal=read(ROOT/'runs/registered/v3_rerun_calibration.json')
    checks=before_checks(cal,Instrument('A10',k,'linear'))
    assert {c['gate'] for c in checks}=={'G1.1','G1.2','G1.3','G1.4','G1.5','G3.1.scenarios'}
    assert all(c['passed'] for c in checks),checks
