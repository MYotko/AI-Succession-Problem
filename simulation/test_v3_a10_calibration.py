"""Exact A6 identities and simulation-free A10 launch context checks."""
from copy import deepcopy
import hashlib
import json
import pickle
from pathlib import Path

import numpy as np
import pytest

from test_v3_paths import tmp_path
from v3 import calibration, instrument, production_runner as runner
from v3.artifacts import ROOT, atomic_json, canonical, code_identity, read, seal, stable_job, unseal
from v3.context import Context

A10 = instrument.Instrument('A10', 1.8, 'linear')
PARENT_PATH = 'v3/runs/registered/v3_rerun_calibration.json'


@pytest.fixture
def synthetic(monkeypatch):
    parent = unseal(read(ROOT / 'runs/registered/v3_rerun_calibration.json'))
    constants = deepcopy(instrument.validate_constants())
    def pin(document):
        name = document['payload']['a6_variant']
        entry = constants['a6_calibrations']['variants'][name]
        entry.update(payload_sha256=document['sha256'], byte_sha256=hashlib.sha256(canonical(document)+b'\n').hexdigest())
        return document
    def build(name='sigma_squared_x10'):
        entry = constants['a6_calibrations']['variants'][name]
        p = deepcopy(parent)
        p.update(a6_variant=name, a6_sigma_factor=entry['sigma_factor'],
                 a6_parent_sha256=instrument.CALIBRATION_SHA256,
                 a6_note=constants['a6_calibrations']['variant_note'], code_hash=entry['producer_code_hash'])
        p['values']['sigma_squared'] *= entry['sigma_factor']
        # Synthetic re-derivation changes novelty diagnostics and epsilon_N.
        for row in p['block_lower_levels']:
            row[0] /= 2
        p['reliable_positive_lower_levels'][0] = min(row[0] for row in p['block_lower_levels'] if row[0] > 0)
        p['values']['epsilon_n'] = .01*p['reliable_positive_lower_levels'][0]
        return pin(seal(p))
    monkeypatch.setattr(instrument, 'validate_constants', lambda document=None: constants)
    return build, pin


@pytest.mark.parametrize('name',['sigma_squared_x10','sigma_squared_x0.1'])
@pytest.mark.parametrize('registered',[False,True])
def test_exact_synthetic_variant_works_at_historical_producer_identity(synthetic,tmp_path,name,registered):
    build,_=synthetic
    document=build(name)
    assert document['payload']['code_hash'] != code_identity()
    path=tmp_path/'variant.json'; atomic_json(path,document)
    assert calibration.load_calibration(path,instrument=A10,registered=registered)==document
    assert calibration.validate_calibration(document,instrument=A10,registered=registered)==document['payload']
    ctx=Context.build({'instrument':A10.declaration(),'capability':5.},document)
    assert ctx.parameters.epsilon_n==document['payload']['values']['epsilon_n']
    assert ctx.protocol.sigma_squared==document['payload']['values']['sigma_squared']


def test_exact_byte_identity_is_required_even_when_payload_is_unchanged(synthetic,tmp_path):
    build,_=synthetic
    document=build()
    path=tmp_path/'pretty.json';path.write_text(json.dumps(document,indent=2),encoding='utf-8')
    with pytest.raises(ValueError,match='exact identity'):
        calibration.load_calibration(path,instrument=A10)


@pytest.mark.parametrize('registered',[False,True])
def test_unknown_resealed_variant_refused_even_at_current_code_identity(synthetic,registered):
    build,_=synthetic
    p=deepcopy(build()['payload']);p['code_hash']=code_identity()
    with pytest.raises(ValueError,match='exact identity'):
        calibration.validate_calibration(seal(p),instrument=A10,registered=registered)
    p['a6_variant']='sigma_squared_x2'
    with pytest.raises(ValueError,match='exactly pinned'):
        calibration.validate_calibration(seal(p),instrument=A10,registered=registered)


@pytest.mark.parametrize('field',['center','V_ref_total','n_ref','epsilon_e','epsilon_l','c_e','psi_observable','sigma_squared','extra'])
def test_frozen_parent_quantities_checked_independently_of_identity(synthetic,field):
    build,pin=synthetic
    p=deepcopy(build()['payload'])
    if field=='center': p['values'][field][0] += .01
    elif field=='psi_observable': p['values'][field]='changed'
    elif field=='extra': p['values'][field]=1.
    else: p['values'][field] *= 2
    # Even an independently pinned test record must pass the parent comparison.
    document=pin(seal(p))
    with pytest.raises(ValueError,match='frozen parent quantity'):
        calibration.validate_calibration(document,instrument=A10)


@pytest.mark.parametrize('field',['seeds','input_hashes','steps','trajectories','tag','fixture','a6_parent_sha256','a6_sigma_factor','code_hash','a6_note','extra'])
def test_frozen_parent_provenance_is_checked(synthetic,field):
    build,pin=synthetic
    p=deepcopy(build()['payload'])
    if field in ('seeds','input_hashes'): p[field]=[]
    elif field in ('steps','trajectories','a6_sigma_factor'): p[field] += 1
    elif field=='fixture': p[field]=True
    else: p[field]='changed'
    with pytest.raises(ValueError,match='parent'):
        calibration.validate_calibration(pin(seal(p)),instrument=A10)


@pytest.mark.parametrize('change',['non_novelty_level','non_novelty_block','epsilon_relation'])
def test_only_novelty_diagnostics_can_change(synthetic,change):
    build,pin=synthetic
    p=deepcopy(build()['payload'])
    if change=='non_novelty_level': p['reliable_positive_lower_levels'][1] += .1
    elif change=='non_novelty_block': p['block_lower_levels'][0][2] += .1
    else: p['values']['epsilon_n'] *= 3
    with pytest.raises(ValueError,match='diagnostics'):
        calibration.validate_calibration(pin(seal(p)),instrument=A10)


def table(cal=PARENT_PATH,cap=1.,index=0):
    return stable_job('table',{'phase':'table','calibration_path':str(cal),
        'kernel':{'reproduction_rate':.064,'capability':cap,'instrument':A10.declaration()}},'validation',index)


def test_preflight_deduplicates_sample_and_configuration_contexts_without_simulation(monkeypatch):
    first,duplicate,other=table(index=0),table(index=1),table(cap=5.)
    spec={'jobs':[first,duplicate,other], 'configuration':{'table':{'kind':'table','config':first['config']}}}
    seen=[];original=Context.build
    def build(kernel,document=None):
        seen.append(deepcopy(kernel))
        return original(kernel,document)
    monkeypatch.setattr(Context,'build',build)
    monkeypatch.setattr(Context,'population',lambda *a,**k:pytest.fail('preflight simulated'))
    state=pickle.dumps(np.random.get_state())
    result=runner.preflight_contexts(spec)
    assert result['checked']==2 and result['failed']==0 and len(seen)==2
    assert sorted(len(r['uses']) for r in result['contexts'])==[1,3]
    assert pickle.dumps(np.random.get_state())==state


def test_preflight_collects_every_context_failure_including_configuration_only(tmp_path):
    missing=tmp_path/'missing.json'
    spec={'jobs':[table(missing),table(cap=6.)],
          'configuration':{'table':{'kind':'table','config':table(cap=0.)['config']}}}
    with pytest.raises(runner.ContextPreflightError) as caught:
        runner.preflight_contexts(spec)
    report=caught.value.report
    assert report['checked']==report['failed']==3
    assert str(missing.resolve()) in str(caught.value)
    assert 'configuration:table:0' in str(caught.value)
    assert all(r['status']=='failed' for r in report['contexts'])


def test_preflight_handles_cost_wrappers_table_stages_and_runs(synthetic,tmp_path):
    build,_=synthetic
    path=tmp_path/'variant.json';atomic_json(path,build())
    source=table(path)
    cost=stable_job('a10_cost',{'source_job':source,'toy':True,'cost_kind':'estimate','phase':'stratum'},'pilot',0)
    stage=stable_job('a4_validate',{'a1_job':source,'phase':'validate'},'validation',0)
    run=stable_job('rerun',{'calibration_path':str(path),'tables_path':str(tmp_path/'never_open_tables.json'),
        'model':{'instrument':A10.declaration(),'capability':2.,'successor_capability':3.}},'validation',0)
    report=runner.preflight_contexts({'schema':'v3-A10-cost-pilot-1','jobs':[cost,stage,run]})
    assert report['checked']==3 and report['failed']==0
    assert any(r['kernel'].get('n_agents')==16 for r in report['contexts'])
    assert {r['calibration_sha256'] for r in report['contexts']}=={read(path)['sha256']}


def test_preflight_collects_unexpected_context_exceptions_and_leaves_r4_alone(monkeypatch):
    def broken(*a,**k): raise RuntimeError('synthetic context failure')
    monkeypatch.setattr(Context,'build',broken)
    with pytest.raises(runner.ContextPreflightError) as caught:
        runner.preflight_contexts({'jobs':[table(),table(cap=2.)]})
    assert caught.value.report['failed']==2 and str(caught.value).count('synthetic context failure')==2
    r4=stable_job('rerun',{'model':{},'calibration_path':'absent-R4-calibration'},'validation',0)
    assert runner.preflight_contexts({'jobs':[r4]})['checked']==0


def test_failed_preflight_refuses_before_configuration_dispatch_and_service(tmp_path,monkeypatch):
    from v3 import service
    jobs=[table(cap=6.),table(cap=0.)]
    spec={'code_hash':code_identity(),'registered':False,'tag':'validation','jobs':jobs,
          'phases':['table'],'configuration':{'table':{'kind':'table','config':jobs[0]['config']}},'wall_seconds':60}
    path=tmp_path/'spec.json';atomic_json(path,seal(spec))
    monkeypatch.setattr(runner,'available_cpus',lambda:32)
    monkeypatch.setattr(runner,'configuration_test',lambda *a,**k:pytest.fail('configuration dispatched'))
    monkeypatch.setattr(runner,'dispatch',lambda *a,**k:pytest.fail('sample dispatched'))
    local={'profile':'local','workers':2,'threads':1,'cpu_budget':16,'mode':'work'}
    with pytest.raises(runner.ContextPreflightError) as caught:
        runner.launch(path,tmp_path/'local',local)
    assert caught.value.report['failed']==2
    assert read(tmp_path/'local/context_preflight.json')['failed']==2
    assert not (tmp_path/'local/control.json').exists()
    monkeypatch.setattr(service.platform,'node',lambda:'yotko-evo-x2')
    monkeypatch.setattr(service.platform,'system',lambda:'Linux')
    monkeypatch.setattr(service,'command',lambda *a,**k:pytest.fail('service changed before context preflight'))
    with pytest.raises(runner.ContextPreflightError):
        service.run_with_service(path,tmp_path/'x2',dict(local,profile='x2',cpu_budget=32))
