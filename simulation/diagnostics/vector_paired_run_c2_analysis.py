"""Registered stage C analysis. The legacy field is never an analysis input."""
import csv,json,struct
from collections.abc import Mapping
FORBIDDEN='capture_rate'
ACCESSED=set()
COUNTERS=('evaluated_yield_opportunities','honest_yield_opportunities','ratified_yields','yield_checks',
          'yield_condition_blocked_count','yield_condition_met_count')

class Row(Mapping):
    def __init__(self,data):self.data=data
    def __getitem__(self,key):
        assert key!=FORBIDDEN,'Excluded legacy field was accessed'
        ACCESSED.add(key)
        return self.data[key]
    def __iter__(self):return iter(self.data)
    def __len__(self):return len(self.data)

def convert(value,kind):
    if value=='null':return None
    if kind in ('bool','bool_'):return {'True':True,'False':False}[value]
    if kind.startswith('int'):return int(value)
    if kind.startswith('float'):return float(value)
    assert kind=='str',kind
    return value

def bit_equal(a,b):
    if type(a) is not type(b):return False
    if isinstance(a,float):return struct.pack('>d',a)==struct.pack('>d',b)
    return a==b

def analyze(ex):
    from attack_metrics_v2 import paired_difference
    ex.check_identity();ex.pins()
    merge=ex.read(ex.P+'merge.json')
    assert merge['verified']
    rows=[]
    with (ex.OUT/(ex.P+'runs.csv')).open(encoding='utf-8',newline='') as handle:
        reader=csv.reader(handle)
        header=next(reader)
        # Remove the legacy column before parsing or accessing any record value.
        selected=[(i,key) for i,key in enumerate(header) if key!=FORBIDDEN]
        for raw in reader:
            data={key:convert(raw[i],merge['field_types'][key]) for i,key in selected}
            rows.append(Row(data))
    assert len(rows)==900
    arms={arm:[r for r in rows if r['arm']==arm] for arm in sorted(ex.PARAMETERS)}
    for arm,group in arms.items():
        assert len(group)==300 and [r['seed'] for r in group]==ex.SEEDS
        for row in group:
            for field in COUNTERS:assert type(row[field]) is int
    field='yield_condition_blocked_count'
    c1=paired_difference(arms['as_published'],arms['zero_strength'],field)
    c2=paired_difference(arms['as_published'],arms['zero_dependency'],field)
    c3={arm:{field:sum(r[field] for r in group) for field in COUNTERS} for arm,group in arms.items()}
    c4={arm:dict(runs_with_at_least_one_block=sum(r[field]>0 for r in group),
                action_modified_true_runs=sum(r['action_modified'] is True for r in group)) for arm,group in arms.items()}
    compared_fields=[key for key in header if key!=FORBIDDEN]
    differences=[];different_fields=set()
    for a,b in zip(arms['zero_strength'],arms['zero_dependency']):
        assert a['seed']==b['seed']
        differing=[key for key in compared_fields if not bit_equal(a[key],b[key])]
        different_fields.update(differing)
        if differing:differences.append(dict(seed=a['seed'],differing_fields=differing))
    c5=dict(n_pairs=300,identical_on_every_compared_field=not differences,
            bit_identical_pairs=300-len(differences),different_pairs=len(differences),
            compared_fields=compared_fields,excluded_field=FORBIDDEN,
            differing_fields=sorted(different_fields),differences_by_seed=differences)
    per_run=[dict(arm=r['arm'],seed=r['seed'],recorded_steps=r['recorded_steps'],completed_steps=r['completed_steps'])
             for r in merge['per_run']]
    assert all(r['recorded_steps']==r['completed_steps'] for r in per_run)
    c6=dict(runs=900,runs_with_equal_recorded_and_completed_steps=len(per_run),
            recorded_steps=sum(r['recorded_steps'] for r in per_run),
            completed_steps=sum(r['completed_steps'] for r in per_run),per_run=per_run)
    assert FORBIDDEN not in ACCESSED
    assertion=dict(passed=True,excluded_field=FORBIDDEN,registered_fields_accessed=sorted(ACCESSED))
    results=dict(status='COMPLETE',C1=c1,C2=c2,C3=c3,C4=c4,C5=c5,C6=c6,
                 capture_rate_exclusion_assertion=assertion)
    ex.write(ex.P+'results.json',results)
    final_pins=ex.full_pins()
    ex.write(ex.P+'source_pins_end.json',final_pins)
    lines=['# Stage C attempt 2: Biological Veto Capture',
           '',
           'This is a post-repair re-measurement of a quantity banked pre-repair. The two measure different substrates and neither supersedes the other. No ratio of two measured counts was computed by the registered analysis. The capture_rate field was recorded and not used. The Section 10 interpretation is reserved for the operator.',
           '',
           '## C1',
           '',
           'as_published minus zero_strength, yield_condition_blocked_count.',
           '',
           '| Pair count | Mean difference | Paired standard error | t |',
           '| --- | --- | --- | --- |']
    for name,data,contrast in [('C1',c1,None),('C2',c2,'as_published minus zero_dependency, yield_condition_blocked_count.')]:
        if name=='C2':
            lines.extend(['','## C2','',contrast,'','| Pair count | Mean difference | Paired standard error | t |','| --- | --- | --- | --- |'])
        t='undefined' if data['t_statistic'] is None else repr(data['t_statistic'])
        lines.append('| '+str(data['n_pairs'])+' | '+repr(data['mean_difference'])+' | '+repr(data['paired_standard_error'])+' | '+t+' |')
    lines.extend(['','## C3','','| Arm | Counter | Total count |','| --- | --- | --- |'])
    for arm,data in c3.items():
        for counter,value in data.items():lines.append('| '+arm+' | '+counter+' | '+str(value)+' |')
    lines.extend(['','## C4','','| Arm | Runs with at least one block | Runs with action_modified true |','| --- | --- | --- |'])
    for arm,data in c4.items():lines.append('| '+arm+' | '+str(data['runs_with_at_least_one_block'])+' | '+str(data['action_modified_true_runs'])+' |')
    lines.extend(['','## C5','',
                  'Compared every recorded field except the legacy field excluded by Amendment 2, including arm labels, parameter fields, and elapsed times.',
                  '',
                  'Identical on the compared field set: '+str(c5['identical_on_every_compared_field'])+'.',
                  'Bit-identical pairs: '+str(c5['bit_identical_pairs'])+'. Differing pairs: '+str(c5['different_pairs'])+'.',
                  'Differing fields: '+', '.join(c5['differing_fields'])+'.',
                  'The full compared field set and per-seed differing fields are in results.json.',
                  '',
                  '## C6','',
                  str(c6['runs_with_equal_recorded_and_completed_steps'])+' runs have recorded steps equal to completed steps.',
                  'Recorded steps: '+str(c6['recorded_steps'])+'. Completed steps: '+str(c6['completed_steps'])+'.',
                  '',
                  'Legacy-field exclusion assertion: '+str(assertion['passed'])+'.',
                  '',
                  '## Execution evidence','',
                  'Construction conformance, arm distinctness, production binding identity, source-pin gates, and scheduler checks are recorded in gates.json.',
                  'No model or adapter function was replaced. A local sys.monitoring observer counted step returns and checked liveness, entropy, fallback increments, randomness preservation, and production bindings.',
                  'Per-run audit and verified numerical-library thread counts are in completions.jsonl. Merge hashes and deletion counts are in the manifest.',
                  '',
                  '## Source pins','',
                  '| File | Before: committed / worktree LF SHA256 | Completion: committed / worktree LF SHA256 |',
                  '| --- | --- | --- |'])
    before={r['path']:r for r in ex.read(ex.P+'preflight.json')['source_readings']}
    for item in final_pins:
        first=before.get(item['path'])
        start=(first['committed_sha256_lf']+' / '+first['working_tree_sha256_lf']) if first else item['expected_sha256_lf']+' / '+item['expected_sha256_lf']
        lines.append('| '+item['path']+' | '+start+' | '+item['committed_sha256_lf']+' / '+item['working_tree_sha256_lf']+' |')
    assert chr(0x2014) not in '\n'.join(lines)
    with (ex.OUT/(ex.P+'report.md')).open('x',encoding='utf-8',newline='\n') as handle:
        handle.write('\n'.join(lines)+'\n')
        handle.flush();ex.os.fsync(handle.fileno())
