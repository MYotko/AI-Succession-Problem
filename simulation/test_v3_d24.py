"""D24 synthetic gate and runner fixtures. No registered estimates or reruns."""
from copy import deepcopy
import time
import pytest
from v3 import gates
from v3.artifacts import ROOT, atomic_json, read, seal, unseal, code_identity, stable_job, file_hash
from test_v3_gates import grid_fixture
from test_v3_paths import tmp_path


def test_v2_sequence_with_top_censoring_and_some_testable_alphas():
    a, b = gates.cliff_checks(grid_fixture((5., 3., 2.5, 2., 2.)))
    assert a['passed'] and b['passed'] and b['checked'] == 4
    assert a['cap_star_labels'][.5] == '5.0 or higher'
    assert b['alpha_checks'][0]['status'] == 'not_testable'
    assert all(p['decrease_support'] == 1 for p in a['adjacent_pairs'][:3])


def test_bottom_censored_point_and_bootstrap_are_ordered_not_dropped():
    a, b = gates.cliff_checks(grid_fixture((5., 3., 2., 0., 0.)))
    assert a['passed'] and b['passed'] and b['checked'] == 2
    assert a['cap_star_labels'][1.25] == 'below 1.2'
    assert a['adjacent_pairs'][2]['decrease_support'] == 1.
    assert a['adjacent_pairs'][3]['passed'] and a['adjacent_pairs'][3]['decrease_support'] == 0.


@pytest.mark.parametrize('cap', [0., 5.])
def test_all_censored_flat_fails_net_and_no_testable_separation(cap):
    a, b = gates.cliff_checks(grid_fixture((cap,) * 5))
    assert not a['passed'] and not b['passed'] and b['checked'] == 0
    assert all(p['passed'] for p in a['adjacent_pairs'])


def test_top_to_bottom_can_pass_migration_but_not_separation_without_testable_alpha():
    a, b = gates.cliff_checks(grid_fixture((5., 5., 0., 0., 0.)))
    assert a['passed'] and not b['passed'] and b['checked'] == 0


def test_censored_resamples_can_support_a_finite_point_decrease():
    # .75 has a finite point estimate at 1.2, but some resamples fall below
    # the entire grid. Every such draw is still below the fixed 3.0 at .5.
    overrides={(a,c):0 for a in gates.ALPHAS for c in gates.CAPABILITIES}
    overrides[(.5,3.)]=75; overrides[(.75,1.2)]=38
    a, _ = gates.cliff_checks(grid_fixture(overrides=overrides))
    assert a['cap_star'][.75] == 1.2
    assert 0 < a['bootstrap_censor_counts'][.75]['bottom'] < gates.BOOTSTRAPS
    assert a['adjacent_pairs'][0]['decrease_support'] == 1.
    # The subsequent point decrease has only about half support, so it fails.
    assert not a['passed'] and a['adjacent_pairs'][1]['decrease_support'] < .9


def test_hardest_order_is_stable_and_does_not_change_jobs():
    from test_v3_a1_diagnosis import inputs
    from v3.table_repair_a3 import prepare, enlarged
    audit, source = inputs()
    a=prepare(audit,source,'cal.json')
    order=a['repair']['dispatch_order']
    assert order == sorted(order,key=lambda x:(-x['maximum_normalized_excess'],x['source_job_id']))
    old={j['id']:j for j in source['jobs']}
    for job in a['jobs']:
        c=deepcopy(old[job['config']['source_job_id']]['config'])
        c.update(settings=enlarged(c['settings']),calibration_path='cal.json',
                 repair_round='A3-fixed-once-20260928',source_job_id=job['config']['source_job_id'])
        assert job == stable_job('table',c,'v3_tables',0)
    for r in audit['rows']:r['excess']['fixture']=0.
    b=prepare(audit,source,'cal.json')
    assert sorted(a['jobs'],key=lambda j:j['id']) == sorted(b['jobs'],key=lambda j:j['id'])
    assert [j['config']['source_job_id'] for j in b['jobs']] == sorted(old for old in b['repair']['replacements'])


def screen_family():
    from test_v3_a1_diagnosis import row
    old, new = {}, {}
    for name in ('primary','double_population','double_length'):
        config={'source_job_id':name,'setting_name':name,'rule_id':'balanced','kernel':{'reproduction_rate':.064}}
        job={'id':'new-'+name,'config':config}
        old[name]={'job':job,'result':{'rows':[row()]}}
        new[name]=deepcopy(old[name])
    return old,new


@pytest.mark.parametrize('failure',['row','old_new','sensitivity',None])
def test_completion_screen_stops_on_each_binding_screen(failure):
    from v3.table_repair_a3 import CompletionScreen
    old,new=screen_family()
    if failure=='row':new['primary']['result']['rows'][0]['status']='not_estimable'
    if failure=='old_new':new['primary']['result']['rows'][0]['lambda_f'].update(mean=6.,replicates=[6.]*6)
    if failure=='sensitivity':
        # Each replacement is within 5 of its original, but pair gap is 6.
        for name,mean in [('primary',3.),('double_population',-3.)]:
            new[name]['result']['rows'][0]['lambda_f'].update(mean=mean,replicates=[mean]*6)
    check=CompletionScreen(old)
    first=check(new['primary']['job'],new['primary'])
    if failure in ('row','old_new'):assert first and first['job']=='new-primary'
    else:
        assert first is None
        second=check(new['double_population']['job'],new['double_population'])
        assert bool(second)==(failure=='sensitivity')
        if second:assert second['paired_job']=='new-primary' and 'sensitivity' in second['reason']


def test_fail_fast_interrupts_preserves_completion_and_latches_resume(tmp_path):
    from v3.production_runner import dispatch, caps, completed
    jobs=[stable_job('fixture',{'seconds':s},'validation',i) for i,s in enumerate((.05,20,20,20))]
    settings={'profile':'local','cpu_budget':3,'workers':2,'threads':1,'caps':caps('local',3)}
    atomic_json(tmp_path/'control.json',{'mode':'normal','stop_dispatch':False,'interrupt_now':False})
    code=code_identity()
    check=lambda job,out:{'reason':'synthetic failed row','job':job['id']}
    result=dispatch(tmp_path,jobs,code,settings,time.time()+45,fixed={'workers':2,'threads':1},completion_screen=check)
    assert result['reason']=='screen_failure' and result['completed']==1 and result['running']==0
    assert completed(tmp_path,jobs[0],code) is not None
    events=[__import__('json').loads(x) for x in (tmp_path/'events.jsonl').read_text().splitlines()]
    assert len([e for e in events if e['event']=='dispatch'])==2
    assert any(e['event']=='restart_required' and e['reason']=='screen_failure' for e in events)
    assert read(tmp_path/'screen_failure.json')['job']==jobs[0]['id']
    # Even a caller that omits the checker cannot resume a latched failure.
    again=dispatch(tmp_path,jobs,code,settings,time.time()+45,fixed={'workers':2,'threads':1})
    assert again['reason']=='screen_failure' and again['completed']==1


def test_real_policy_is_exact_276_plus_67_and_pins_a1():
    from v3.table_compatibility_a3 import policy
    p=policy()
    assert len(p['source_outputs'])==343 and len(p['replacement_source_ids'])==67
    assert p['source_file_sha256'].startswith('56db7163') and p['source_payload_sha256'].startswith('f6fcb1fd')
    assert p['source_commit'].startswith('34ffbfe9')


@pytest.mark.parametrize('defect',['order','seed','population','setting','source','stop','budget'])
def test_repair_policy_rejects_changes(defect):
    from v3.table_repair_a3 import prepare
    from v3.table_compatibility_a3 import validate_plan
    # Reconstruct from the small committed policy plus archived prepared spec.
    s=unseal(read(ROOT/'runs/a1_screen_diagnosis/A3_REVIEW_ONLY_manifest.json'))
    from v3.table_compatibility_a3 import policy
    p=policy()
    s['repair']['dispatch_order']=p['dispatch_order']
    jobs={j['config']['source_job_id']:j for j in s['jobs']}
    s['jobs']=[jobs[x['source_job_id']] for x in p['dispatch_order']]
    s['completion_screen']={'kind':'A3-first-failure','source_root':'read-only-source'}
    validate_plan(s)
    if defect=='order':s['jobs'].reverse()
    if defect=='seed':s['jobs'][0]['seed']+=1
    if defect=='population':s['jobs'][0]['config']['settings']['particles']*=2
    if defect=='setting':s['jobs'][0]['config']['settings']['burn']+=1
    if defect=='source':s['repair']['source_outputs'][next(iter(s['repair']['source_outputs']))]='0'*64
    if defect=='stop':s['completion_screen']['kind']='ignore'
    if defect=='budget':s['wall_seconds']=86400
    with pytest.raises(ValueError):validate_plan(s)
