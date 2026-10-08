"""R4 retains callable interfaces predating the optional A10 arguments."""
import numpy as np
import pytest

from v3 import calibration, context, engine, gates, integration, offline_estimator, recording, table_labels_a5
from v3.artifacts import ROOT, read
from v3.instrument import Instrument
from v3.policies import execution_policy_class


@pytest.mark.parametrize('instrument',[None, {'mapping':'R4'}, Instrument('A10',1.8,'linear').declaration()])
def test_a5_identity_call_supplies_a10_only_for_a10(monkeypatch,instrument):
    class ReachedIdentity(Exception): pass
    calls=[]
    if instrument is not None and instrument['mapping']=='A10':
        def check(path,*,a10):
            assert a10 is True
            calls.append(path)
            raise ReachedIdentity
    else:
        def check(path):
            calls.append(path)
            raise ReachedIdentity
    monkeypatch.setattr(table_labels_a5,'require_committed_identity',check)
    with pytest.raises(ReachedIdentity):
        table_labels_a5.prepare('family','run','plan','source','cal','identity',
                               registration={'fixture':'pin'},instrument=instrument,
                               **({'wall_hours': 257.66} if instrument and instrument['mapping']=='A10' else {}))
    assert calls==['identity']


def test_r4_live_rollout_counterfactual_and_context_accept_legacy_callables(monkeypatch):
    calls=[]
    old_advance,old_measure=engine.advance,engine.measurements_and_flow
    old_kernel,old_tables=context.kernel_identity,integration.FixtureTables
    old_population=engine.PopulationBatch
    def advance(batch,actions,rng,reproduction_rate,capacity,protocol,*,crowding='total',independent=False):
        calls.append('advance')
        return old_advance(batch,actions,rng,reproduction_rate,capacity,protocol,crowding=crowding,independent=independent)
    def measure(batch,actions,parameters,alpha,capability,*,n_ref=200,v_max=5):
        calls.append('measure')
        return old_measure(batch,actions,parameters,alpha,capability,n_ref=n_ref,v_max=v_max)
    def kernel(rr,capacity,crowding='total',protocol=None):
        calls.append('kernel')
        return old_kernel(rr,capacity,crowding,protocol)
    def tables(rules,parameters,kernel_hash):
        calls.append('tables')
        return old_tables(rules,parameters,kernel_hash)
    def population(ages,welfare,traits,bank,stocks,window,counts,h_n):
        calls.append('copy')
        return old_population(ages,welfare,traits,bank,stocks,window,counts,h_n)
    for module in (integration,recording):
        monkeypatch.setattr(module,'advance',advance)
        monkeypatch.setattr(module,'measurements_and_flow',measure)
    monkeypatch.setattr(context,'measurements_and_flow',measure)
    monkeypatch.setattr(context,'kernel_identity',kernel)
    monkeypatch.setattr(integration,'kernel_identity',kernel)
    monkeypatch.setattr(integration,'FixtureTables',tables)
    monkeypatch.setattr(engine,'PopulationBatch',population)
    model=integration.V3Model(4,seed=172,rules=execution_policy_class()[:2],rollout_steps=1,
                              successor_capability=None,instrument={'mapping':'R4'})
    model.evaluate(horizon=2,capability=3.,transition_at=0,incumbent_index=0)
    recording.undisrupted(model,horizon=2,capability=1.5,transition_at=0,incumbent_index=0,seed_channel='yield_common')
    model.step()
    ctx=context.Context.build({'instrument':{'mapping':'R4'}})
    assert ctx.kernel_hash
    ctx.measure(model.state,np.full((1,6),1/6))
    assert set(calls)=={'advance','measure','kernel','tables','copy'}


def test_r4_calibration_loader_and_context_accept_legacy_validator(monkeypatch):
    original=calibration.validate_calibration
    calls=[]
    def validate(document,*,registered=False):
        calls.append(registered)
        return original(document,registered=registered)
    monkeypatch.setattr(calibration,'validate_calibration',validate)
    doc=calibration.load_calibration(ROOT/'runs/registered/v3_rerun_calibration.json',instrument={'mapping':'R4'})
    context.Context.build({'instrument':{'mapping':'R4'}},doc)
    assert calls==[False,False]


def test_r4_context_factory_and_recorder_keep_legacy_constructors(monkeypatch):
    class LegacyContext(context.Context):
        def __init__(self,config,protocol,parameters,n_ref,calibration_hash,fixture):
            super().__init__(config,protocol,parameters,n_ref,calibration_hash,fixture)
    assert not LegacyContext.build({'instrument':{'mapping':'R4'}}).instrument.a10
    original=recording.CompletePlan
    calls=[]
    def plan(plan_id,epoch_id,preference_id,information_law_id,extinction_flow,start,terminal_time,
             first_yield,flows,continuation,lambda_f,admitted,admission_evidence,survival_probability,transition_included=True):
        calls.append(plan_id)
        return original(plan_id,epoch_id,preference_id,information_law_id,extinction_flow,start,terminal_time,
                        first_yield,flows,continuation,lambda_f,admitted,admission_evidence,survival_probability,transition_included)
    monkeypatch.setattr(recording,'CompletePlan',plan)
    model=recording.RecordedV3Model(4,seed=171,rules=execution_policy_class()[:1],rollout_steps=1,
                                   instrument={'mapping':'R4'})
    model.step()
    assert calls and model.yield_events


def test_r4_offline_trajectory_accepts_legacy_feature_and_advance_signatures(monkeypatch):
    advance,features=offline_estimator.advance,offline_estimator.observable_features
    calls=[]
    def legacy_advance(batch,actions,rng,rr,capacity,protocol,*,crowding='total',independent=False):
        calls.append('advance')
        return advance(batch,actions,rng,rr,capacity,protocol,crowding=crowding,independent=independent)
    def legacy_features(state,actions):
        calls.append('features')
        return features(state,actions)
    monkeypatch.setattr(offline_estimator,'advance',legacy_advance)
    monkeypatch.setattr(offline_estimator,'observable_features',legacy_features)
    ctx=context.Context.build({'n_agents':4,'carrying_capacity':40,'instrument':{'mapping':'R4'}})
    offline_estimator.simulate(ctx,execution_policy_class()[0],
        {'groups':3,'burn':1,'measure':4,'runs_per_group':2,'particles':2},717,'plain')
    assert set(calls)=={'advance','features'}


def test_r4_checker_keeps_five_argument_reference_theta(monkeypatch):
    original=gates.reference_theta
    calls=[]
    def legacy(v,b,transfer_stock,alpha,epsilon_l):
        calls.append(v)
        return original(v,b,transfer_stock,alpha,epsilon_l)
    monkeypatch.setattr(gates,'reference_theta',legacy)
    checks=gates.before_checks(read(ROOT/'runs/registered/v3_rerun_calibration.json'))
    assert calls and all(c['passed'] for c in checks)
