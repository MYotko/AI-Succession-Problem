"""A2 review regressions using explicitly synthetic records."""
from copy import deepcopy
from fractions import Fraction
import math
from types import SimpleNamespace
import pytest
from test_v3_paths import tmp_path
from test_v3_gates import run_fixture, review_fixture, grid_fixture
from v3 import gates
from v3.artifacts import atomic_json, seal, file_hash, read, digest, ROOT
from v3.cohort import cohort_bound, ProtectionPeriod, CohortBound
from v3.policies import execution_policy_class


def cohort_fixture(ages=(20,), welfare=(500,)):
    r = run_fixture(fire=False)
    r['job']['config']['model']['n_agents'] = len(ages)
    b = cohort_bound(ages, welfare)
    r['result']['periods'] = [ProtectionPeriod(0,25,50,(),b).audit()]
    r['result']['diagnostics'][0].update(population=len(ages), survival_first=not b.admitted(),
        gate_evidence={'population_before':len(ages),'period_start':{'ages_before':list(ages),'welfare_units_before':list(welfare)},
        'ages_before':list(ages),'welfare_units_before':list(welfare),'action':[0.,1.,0.,0.,0.,0.],
        'summary_bins_before':[0]*6,'rule_ids':[r.rule_id for r in execution_policy_class()]})
    return r


def test_nonminimum_action_at_nontie_fails_including_last_death():
    r = cohort_fixture()
    assert gates.reference_cohort([20],[500],50,1.) < gates.reference_cohort([20],[500],50,1/6)
    assert gates.viability([r])['passed']
    r['result']['diagnostics'][0]['population'] = 0
    assert gates.viability([r])['passed']  # Last-death action still checked.
    r['result']['diagnostics'][0]['gate_evidence']['action'] = [1/6]*6
    assert not gates.viability([r])['passed']
    del r['result']['diagnostics'][0]['gate_evidence']['ages_before']
    assert not gates.viability([r])['passed']


def test_survival_first_inside_admitted_period_and_absorbed_denominator():
    r = cohort_fixture([0]*200,[1000]*200)
    assert r['result']['periods'][0]['admitted']
    first = r['result']['diagnostics'][0]
    first['population'] = 1
    later = deepcopy(first)
    later.update(time=1, survival_first=True)
    later['gate_evidence'].update(population_before=1,ages_before=[20],welfare_units_before=[500],action=[1/6]*6)
    later['gate_evidence'].pop('period_start')
    r['result']['diagnostics'].append(later);r['result']['steps']=2
    assert not gates.viability([r])['passed']
    later['gate_evidence']['action']=[0.,1.,0.,0.,0.,0.]
    assert gates.viability([r])['passed']
    empty = cohort_fixture([],[])
    result = gates.viability([cohort_fixture(),empty])
    assert result['passed'] and result['living_start_periods']==1 and result['absorbed_start_periods']==1
    assert result['survival_first_share']==1.


def test_recordable_epsilon_tie_uses_exact_ledger_not_float(monkeypatch):
    # A constructed exact certificate exercises the ledger boundary. Real
    # finite life tables have dyadic denominators and cannot equal 1/1000.
    r = cohort_fixture([0]*200,[1000]*200)
    tie = CohortBound(1,1000,50,200)
    r['result']['periods']=[ProtectionPeriod(0,25,50,(),tie).audit()]
    assert r['result']['periods'][0]['bound']==math.nextafter(.001, math.inf)
    monkeypatch.setattr(gates,'reference_cohort',lambda *a,**k: Fraction(1,1000))
    assert gates.viability([r])['passed']
    r['result']['periods'][0]['reserved']='0'
    assert not gates.viability([r])['passed']


def test_candidate_class_is_frozen_and_fallback_fixture_only():
    raw=cohort_fixture()['result']['diagnostics'][0]['gate_evidence']
    assert max(gates.candidate_welfare_shares(raw))==1.
    raw['rule_ids'].pop()
    with pytest.raises(ValueError,match='25-rule'):
        gates.candidate_welfare_shares(raw)
    with pytest.raises(KeyError): gates.candidate_welfare_shares({})
    assert max(gates.candidate_welfare_shares({},fixture=True))==1.


def test_near_tie_uses_reported_strict_order_after_numeric_check():
    e=review_fixture(0.)
    p=e['gate_evidence']['plans'][0]
    p['flows']=[x+1e-12 for x in p['flows']]
    assert gates.check_review(({},e))  # Independent arithmetic is slightly greater; reported tie holds.
    e['gate_evidence']['comparison_values']['now']=2.+1e-12
    e['decision'].update(immediate_value=2.+1e-12,yield_now=True,selected_plan='now')
    e['transition_count']=1
    assert gates.check_review(({},e))
    p['flows']=[100.]*25
    with pytest.raises(ValueError,match='comparison values'):
        gates.check_review(({},e))


def test_gamma_requires_checkable_pair_and_independent_reported_cost():
    e=review_fixture()
    assert gates.gamma_check([({},e)])['checked']==1
    e['gate_evidence']['plans'][0]['gamma']=2.
    bad=gates.gamma_check([({},e)])
    assert not bad['passed'] and bad['checked']==1
    e=review_fixture()
    for p in e['gate_evidence']['plans']:
        if p['first_yield'] is not None:
            p['undisrupted']['continuation']=None;p['gamma']=None
    c=gates.gamma_check([({},e)])
    assert not c['passed'] and c['checked']==0 and c['reviews_without_comparison']==1


def test_living_sample_keeps_extinction_step_checks_all_absorbed(monkeypatch):
    r=run_fixture()
    r['result']['diagnostics']=[{'time':t,'population':0,'gate_evidence':{'population_before':int(t==0),
        'theta':1.,'frontier_velocity':0.,'bandwidth':0.,'transfer_stock':0.}} for t in range(4)]
    monkeypatch.setattr(gates,'STEP_COUNT',1)
    c=gates.theta_checks([r],.001)
    assert c['passed'] and c['living_sample_count']==1 and c['absorbed_steps_checked']==3
    assert gates.sample_steps([r])[0][1]['time']==0
    r['result']['diagnostics'][2]['gate_evidence']['theta']=.9
    assert not gates.theta_checks([r],.001)['passed']


def test_censored_bootstrap_cap_uses_d24_order():
    # Near-threshold point decrease still needs 90 percent support.
    overrides={(a,c):0 for a in gates.ALPHAS for c in gates.CAPABILITIES}
    overrides[(.5,1.5)]=38;overrides[(.75,1.2)]=38
    for a in gates.ALPHAS[2:]: overrides[(a,1.2)]=75
    c=gates.cliff_checks(grid_fixture(overrides=overrides))[0]
    assert c['adjacent_pairs'][0]['cap_star']==[1.5,1.2]
    assert 0<c['adjacent_pairs'][0]['decrease_support']<.9 and not c['passed']


def test_registration_checks_all_identity_files_even_ignored(tmp_path,monkeypatch):
    from v3 import artifacts
    note=tmp_path/'note.md';note.write_bytes(b'pinned')
    pin={'commit':'c','path':'note.md','sha256':file_hash(note)}
    def fake_git(command,**kwargs):
        if 'show' in command:return SimpleNamespace(stdout=b'pinned')
        if 'ls-files' in command:
            assert 'simulation/v3/table_compatibility_A2.json' in command
            assert '--exclude-standard' not in command
            return SimpleNamespace(stdout=b'simulation/v3/table_compatibility_A2.json')
        return SimpleNamespace(stdout=b'')
    monkeypatch.setattr(artifacts.subprocess,'run',fake_git)
    with pytest.raises(RuntimeError,match='committed and clean'): artifacts.verify_registration(pin,tmp_path)


def test_compatibility_binds_exact_seal_and_file_bytes(tmp_path,monkeypatch):
    from v3 import table_compatibility as c
    d=seal({'code_hash':'producer','manifest':{'calibration_hash':'cal','design':{'x':1}}})
    path=tmp_path/'table.json';atomic_json(path,d)
    rec={'producer_code_hash':'producer','calibration_sha256':'cal','table_design_sha256':digest({'x':1}),
         'table_seal_sha256':d['sha256'],'table_file_sha256':file_hash(path)}
    monkeypatch.setattr(c,'verified_record',lambda:rec)
    assert c.compatible(d,file_hash(path))
    assert not c.compatible(d) and not c.compatible(d,'0'*64)
    altered=deepcopy(d);altered['payload']['extra']='restamped';altered=seal(altered['payload'])
    assert not c.compatible(altered,file_hash(path))


def test_refresh_only_proposes_and_never_writes(capsys):
    from v3.recording_validation import refresh_boundary
    path=ROOT/'table_compatibility_A2.json';before=path.read_bytes()
    proposed=refresh_boundary()
    assert proposed and capsys.readouterr().out and path.read_bytes()==before


def test_pinned_probe_is_only_a_nonregistered_fixture():
    from v3.recording_validation import validation_probe_compatible
    path=ROOT/'runs/a2_recording_validation/A1_probe_tables.json'
    if not path.exists():
        import zipfile
        with zipfile.ZipFile(ROOT/'runs/a2_recording_validation/a2_validation_records_20260928.zip') as z:
            data=z.read('A1_probe_tables.json')
        import json,hashlib
        d=json.loads(data);h=hashlib.sha256(data).hexdigest()
    else:
        d=read(path);h=file_hash(path)
    assert validation_probe_compatible(d,h)
    assert not validation_probe_compatible(d,'0'*64)
    d['payload']['fixture']=False
    assert not validation_probe_compatible(seal(d['payload']),h)
