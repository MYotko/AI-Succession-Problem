"""Second review fixtures. No registered estimation, output or git mutation."""
from copy import deepcopy
from types import SimpleNamespace
import pytest
from test_v3_paths import tmp_path
from v3.artifacts import ROOT, read, unseal, seal, atomic_json, code_identity, stable_job, file_hash
from v3 import table_compatibility_a3 as compat, production_runner as runner, gates


def real_spec():
    s=unseal(read(ROOT/'runs/d24_validation/A3_REVIEW_ONLY_manifest.json'))
    s['code_hash']=code_identity()
    return s


def test_equivalent_calibration_spelling_cannot_reseed_family():
    s=real_spec(); compat.validate_plan(s)
    for j in s['jobs']:
        old=j['config']['source_job_id']
        j['config']['calibration_path']='./'+j['config']['calibration_path']
        new=stable_job('table',j['config'],'v3_tables',0)
        s['repair']['replacements'][old]=new['id']
        j.clear();j.update(new)
    with pytest.raises(ValueError,match='pinned job ID, seed or canonical'):
        compat.validate_plan(s)


@pytest.mark.parametrize('returncode,expected',[(0,True),(1,False),(128,False)])
def test_producer_ancestry_git_contract(monkeypatch,returncode,expected):
    def run(command,**kwargs):
        assert command==['git','merge-base','--is-ancestor','a'*40,'HEAD']
        return SimpleNamespace(returncode=returncode)
    monkeypatch.setattr(compat.subprocess,'run',run)
    assert compat.producer_is_ancestor('a'*40)==expected
    assert not compat.producer_is_ancestor('--bad')


def test_family_latch_blocks_new_root_launch_and_publish_before_other_work(tmp_path,monkeypatch):
    from v3 import table_repair_a3 as repair
    s=real_spec(); p=compat.validate_plan(s)
    monkeypatch.setattr(compat,'FAMILY_ROOT',tmp_path/'families')
    compat.record_family_failure(p,{'reason':'fixture failed screen','job':s['jobs'][0]['id']},tmp_path/'old')
    monkeypatch.setattr(runner,'configuration_test',lambda *a:pytest.fail('configuration must not start'))
    monkeypatch.setattr(runner,'validate_spec',lambda *a:None)
    manifest=tmp_path/'spec.json';atomic_json(manifest,seal(s))
    with pytest.raises(RuntimeError,match='family screen failure'):
        runner.launch(manifest,tmp_path/'new',{'profile':'local','cpu_budget':4})
    monkeypatch.setattr(repair,'verify_registration',lambda *a:None)
    monkeypatch.setattr(__import__('v3.calibration',fromlist=['validate_calibration']), 'validate_calibration',lambda *a,**k:None)
    with pytest.raises(RuntimeError,match='family screen failure'):
        repair.publish(s,tmp_path/'another',tmp_path/'unread_source',{},tmp_path/'not_published.json')
    assert not (tmp_path/'not_published.json').exists()


def test_completed_failure_found_before_configuration_and_service_down(tmp_path,monkeypatch):
    from v3 import table_repair_a3 as repair, service
    s=real_spec();p=compat.validate_plan(s); job=s['jobs'][0]
    monkeypatch.setattr(compat,'FAMILY_ROOT',tmp_path/'families')
    monkeypatch.setattr(runner,'validate_spec',lambda *a:None)
    # Use real preflight and family latch, with a bounded synthetic screen.
    class Screen:
        def __call__(self,j,o):
            compat.record_family_failure(p,{'job':j['id'],'reason':'synthetic completed row failed'},tmp_path/'old')
            return True
    monkeypatch.setattr(repair,'completion_screen',lambda *a:Screen())
    phase=tmp_path/'old/table'; out={'job':job,'code_hash':s['code_hash'],'result':{'fixture':True}}
    path=phase/'outputs'/ (job['id']+'.json');atomic_json(path,out)
    atomic_json(phase/'records'/(job['id']+'.json'),{'status':'complete','job':job,'code_hash':s['code_hash'],'output_hash':file_hash(path)})
    manifest=tmp_path/'spec.json';atomic_json(manifest,seal(s))
    monkeypatch.setattr(service.platform,'node',lambda:'yotko-evo-x2')
    monkeypatch.setattr(service.platform,'system',lambda:'Linux')
    monkeypatch.setattr(service,'command',lambda *a:pytest.fail('llm down must not run'))
    monkeypatch.setattr(runner,'configuration_test',lambda *a:pytest.fail('configuration must not run'))
    with pytest.raises(RuntimeError,match='family screen failure'):
        service.run_with_service(manifest,tmp_path/'old',{'profile':'x2','cpu_budget':32})
    with pytest.raises(RuntimeError,match='family screen failure'):
        runner.preflight_completion(s,tmp_path/'new')


def test_omitted_disruption_fails_even_if_gamma_and_comparison_agree():
    from test_v3_gates import review_fixture
    e=review_fixture()
    for p in e['gate_evidence']['plans']:
        if p['first_yield'] is not None:
            p['undisrupted']={k:deepcopy(p[k]) for k in ('flows','continuation','lambda_f')}
            p['gamma']=0.
            p['transition']['stock_units_after']=p['transition']['stock_units_before'][:]
            p['transition']['applied_drawdown_units']=0
    assert gates.check_review(({},e))
    assert not gates.check_gamma(({},e))


@pytest.mark.parametrize('stock', [0,1,50,100])
def test_applied_drawdown_matches_scalar_formula_with_grid_rounding(stock):
    import numpy as np
    from v3.stocks import transition_drawdown
    before=np.array([[stock,50,50,50]],dtype=np.uint8);actions=np.array([[1/6]*6])
    after=transition_drawdown(before,actions,.5,.5)
    raw={'stock_units_before':before[0].tolist(),'stock_units_after':after[0].tolist(),
         'applied_drawdown_units':stock-int(after[0,0]),'capability_gap':.5,'action':actions[0].tolist(),'uniform':.5}
    assert gates.check_applied_drawdown(raw)
    raw['applied_drawdown_units']+=1
    assert not gates.check_applied_drawdown(raw)


def test_missing_survival_first_flag_detected_inside_admitted_period():
    from test_v3_a2_review import cohort_fixture
    r=cohort_fixture([0]*200,[1000]*200)
    first=r['result']['diagnostics'][0];first['population']=1
    second=deepcopy(first);second.update(time=1,population=1,survival_first=False)
    second['gate_evidence'].update(population_before=1,ages_before=[20],welfare_units_before=[500])
    r['result']['diagnostics'].append(second);r['result']['steps']=2
    result=gates.viability([r])
    assert not result['passed'] and 'survival_first flag' in str(result['failures'])
    second['survival_first']=True
    assert gates.viability([r])['passed']


def test_all_living_steps_record_cohort_even_when_admitted():
    from v3.recording import RecordedV3Model
    model=RecordedV3Model(seed=817)
    for step in model.run(2):
        raw=step['gate_evidence']
        assert len(raw['ages_before'])==raw['population_before']
        assert len(raw['welfare_units_before'])==raw['population_before']


def test_real_observer_exposes_executor_omitting_drawdown(monkeypatch):
    from dataclasses import replace
    from v3 import integration
    from v3.recording import RecordedV3Model
    from v3.tables import FixtureTables
    class SuccessorFixture(FixtureTables):
        def lookup(self,*args,**kwargs):
            value=super().lookup(*args,**kwargs)
            return replace(value,lambda_f=value.lambda_f+(1000 if kwargs['capability']>1 else 0))
    model=RecordedV3Model(seed=817,calibration=read(ROOT/'runs/registered/v3_rerun_calibration.json'))
    model.tables=SuccessorFixture(model.rules,model.parameters,model.kernel_hash)
    model._open_period();model.time=20
    monkeypatch.setattr(integration,'transition_drawdown',lambda stocks,*args:stocks.copy())
    model.step();event=model.yield_events[0]
    assert event['transition_count']==1 and gates.check_review(({},event))
    assert event['gate_evidence']['applied_transition']['applied_drawdown_units']==0
    assert not gates.check_gamma(({},event))
