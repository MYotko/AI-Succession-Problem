
"""Post-smoke validation only. Repeats two smoke tasks; never builds a measured job."""
import sys
sys.dont_write_bytecode=True
import ast,collections,csv,json,runpy,statistics,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
D=ROOT/'simulation'/'diagnostics'
EXEC=D/'phase_b_recon_executor.py'
ast.parse(EXEC.read_text(encoding='utf-8'))
ns=runpy.run_path(str(EXEC),run_name='validation_library')
ns['install_guard']('phase_b_recon_')
prefix='phase_b_recon_smoke_'
manifest=ns['read_json'](D/(prefix+'batch_manifest.json'))
assert manifest['status']=='complete'
assert manifest['non_registered'] is True
records=ns['merged_records'](prefix)
assert len(records)==40
assert {r['row']['source_head'] for r in records.values()}=={manifest['sources'][s]['head'] for s in ('v20','v21')}
original={}
jobs={}
for substrate in ('v20','v21'):
 candidates=[r for r in records.values() if r['key']['substrate']==substrate and r['key']['category']=='A']
 r=min(candidates,key=lambda x:(x['task']['rr'],x['task']['seed']))
 ident=ns['job_id'](r['task'])
 assert r['task']['non_registered'] and r['task'] in ns['grid'](True)
 original[substrate]=r
 job={'task':r['task'],'source':manifest['sources'][substrate],'prefix':prefix,
      'code_sha256_lf':manifest['executor_sha256_lf'],'probe_tag':'repeat'}
 checkpaths=ns['paths'](prefix,job['task'])
 checkpaths={k:p.with_name(p.name.replace(prefix+'job_',prefix+'probe_repeat_')) for k,p in checkpaths.items()}
 if checkpaths['completion'].exists():
  prior=ns['read_json'](checkpaths['completion'])
  assert prior['task']==job['task'] and prior['code_sha256_lf']==job['code_sha256_lf']
  proc,console=None,None
 else:
  proc,console=ns['launch'](job)
 jobs[substrate]=(proc,console,job)
repeat_checks={}
repeat_templates={}
for substrate,(proc,console,job) in jobs.items():
 if proc is not None:
  rc=proc.wait();console.close()
  if rc:
   raise RuntimeError('Repeat validation worker failed: '+substrate)
 fp=ns['paths'](prefix,job['task'])
 fp={k:p.with_name(p.name.replace(prefix+'job_',prefix+'probe_repeat_')) for k,p in fp.items()}
 repeated=ns['read_json'](fp['completion'])
 repeat_templates[substrate]=repeated
 baseline=original[substrate]
 fields=[k for k in ns['ROW_FIELDS'] if k not in ('elapsed_seconds','worker_pid')]
 differences=[k for k in fields if repeated['row'][k]!=baseline['row'][k]]
 repeat_checks[substrate]={'key':baseline['key'],'differing_fields':differences,
                          'steps_hash_identical':repeated['steps_sha256_lf']==baseline['steps_sha256_lf'],
                          'baseline_steps_sha256_lf':baseline['steps_sha256_lf'],
                          'repeat_steps_sha256_lf':repeated['steps_sha256_lf'],
                          'elapsed_seconds':repeated['row']['elapsed_seconds']}
ns['atomic_json'](D/'phase_b_recon_b5_determinism.json',repeat_checks)
row_count=step_count=0
typed=True
recomputed=True
merge_evidence={}
for category in ('A','B','C','phi'):
 files=ns['category_files'](prefix,category)
 with files['rows'].open(encoding='utf-8',newline='') as f:
  rows=list(csv.DictReader(f))
 with files['steps'].open(encoding='utf-8',newline='') as f:
  steps=list(csv.DictReader(f))
 groups=collections.defaultdict(list)
 row_groups=collections.defaultdict(list)
 for r in rows:row_groups[ns['job_id'](r)].append(r)
 for s in steps:groups[ns['job_id'](s)].append(s)
 for ident,r in records.items():
  if r['key']['category']!=category:continue
  row=r['row'];st=groups[ident]
  assert len(row_groups[ident])==1
  assert ns['digest'](ns['csv_bytes'](row_groups[ident],ns['ROW_FIELDS']))==r['row_sha256_lf']
  assert len(st)==r['step_row_count']==row['steps_completed']
  assert ns['digest'](ns['csv_bytes'](st,ns['STEP_FIELDS']))==r['steps_sha256_lf']
  assert [int(s['step']) for s in st]==list(range(row['steps_completed']))
  for key,typ in ns['SCHEMA'].items():typed &= type(row[key]) is typ
  assert 'transfer_verified_fraction' not in row
  populations=[int(s['population']) for s in st]
  events=[json.loads(s['yield_event']) for s in st if s['yield_event']!='null']
  fires=[e for e in events if e['fires']]
  transfer=[float(s['x_transfer_comprehension']) for s in st]
  expected={
    'final_population':populations[-1], 'peak_population':max(populations),
    'survived':populations[-1]>=max(row['min_viable_population'],.65*max(populations)),
    'final_ai_generation':int(st[-1]['ai_generation']),
    'yield_fired':bool(fires),
    'knowledge_transfer_verified':bool(fires and max(transfer)>=.10),
    'max_yield_margin':max(float(e['successor_u_sys'])-float(e['incumbent_u_sys'])-float(e['transition_cost']) for e in events)}
  recomputed &= all(row[k]==value for k,value in expected.items())
  assert row['steps_completed']==300 or row['end_reason']=='step_returned_false'
  assert r['production_objects_unchanged'] is True
  assert all(t['threads']==1 for t in r['effective_threads'])
  row_count+=1;step_count+=len(st)
 merge_evidence[category]={'rows':len(rows),'steps':len(steps),'hashes_verified':True}
ns['atomic_json'](D/'phase_b_recon_b5_merge_validation.json',merge_evidence)
unique={k:sorted({r['row'][k] for r in records.values()}) for k in ('survived','yield_fired','final_ai_generation')}
substrate_differences=[]
science_fields=list(ns['SCHEMA'])
science_fields.remove('substrate')
for r in records.values():
 if r['key']['substrate']!='v20':continue
 matched=dict(r['key'],substrate='v21')
 other=records[ns['job_id'](matched)]
 diff=[k for k in science_fields if r['row'][k]!=other['row'][k]]
 substrate_differences.append({'category':r['key']['category'],'cell':r['key']['cell'],'seed':r['key']['seed'],'differing_fields':diff})
interrupt=ns['read_json'](D/'phase_b_recon_b5_interruption.json')
# Verify content preservation independently of JSON key formatting.
import subprocess
before_content={i:ns['digest'](ns['canonical'](r).encode()) for i,r in records.items()}
check=subprocess.run([sys.executable,'-B',str(EXEC),'--workers','8','--test-mode',
                      '--substrate','both','--v20-worktree',manifest['sources']['v20']['path'],'--resume'],
                     cwd=ROOT,capture_output=True,text=True,
                     creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
ns['atomic_bytes'](D/'phase_b_recon_b5_no_work_resume_console.txt',
                  (check.stdout+check.stderr).encode())
assert check.returncode==0
after_records=ns['merged_records'](prefix)
after_content={i:ns['digest'](ns['canonical'](r).encode()) for i,r in after_records.items()}
assert before_content==after_content
after_manifest=ns['read_json'](D/(prefix+'batch_manifest.json'))
last=after_manifest['invocations'][-1]
assert last['preserved']==40 and last['restarted']==0 and last['never_launched']==0 and last['peak_workers']==0
preserved_keys=[]
for filename,original_raw_hash in interrupt['completed_file_hashes_before'].items():
 ident=filename.removeprefix(prefix+'job_').removesuffix('_completion.json')
 assert ident in records and after_manifest['started'][ident]['attempt']==1
 assert records[ident]['row_sha256_lf']==after_manifest['runs'][ident]['row_sha256_lf']
 preserved_keys.append(ident)
ns['atomic_json'](D/'phase_b_recon_b5_completion_preservation.json',
                 {'canonical_completion_hashes_before':before_content,
                  'canonical_completion_hashes_after':after_content,
                  'preserved_after_interruption_keys':preserved_keys,
                  'never_relaunched_preserved_keys':True,
                  'no_work_resume_invocation':last,
                  'original_raw_file_hashes':interrupt['completed_file_hashes_before'],
                  'raw_byte_comparison_not_used':'Merged JSONL canonicalizes object key order.'})
timings={s:statistics.mean(r['row']['elapsed_seconds'] for r in records.values() if r['key']['substrate']==s) for s in ('v20','v21')}
# Timing projections are operational estimates explicitly requested in the dispatch.
total_worker_seconds=7540*(timings['v20']+timings['v21'])
projection={str(n):total_worker_seconds/n/3600 for n in (8,12,16)}
check_definitions=[
 (1,'Both substrates and pinned HEADs',True,{'counts':dict(collections.Counter(r['key']['substrate'] for r in records.values())),'heads':{s:manifest['sources'][s]['head'] for s in manifest['sources']}}),
 (2,'Required recorded fields and types',typed,{'rows':row_count,'fields':list(ns['SCHEMA'])}),
 (3,'Computed and nonconstant fields',recomputed and all(len(v)>1 for v in unique.values()),{'recomputed_from_steps':recomputed,'unique_values':unique}),
 (4,'Repeat determinism',all(not v['differing_fields'] and v['steps_hash_identical'] for v in repeat_checks.values()),repeat_checks),
 (5,'Worker termination and resume',bool(preserved_keys) and manifest['invocations'][1]['restarted']>0,{'preserved_completion_hashes':preserved_keys,'resume_counts':{k:manifest['invocations'][1][k] for k in ('preserved','restarted','never_launched')},'killed_worker':interrupt['killed_worker'],'partial_steps':interrupt['partial_heartbeat']['steps_completed']}),
 (6,'Merge recovery',True,{'run_rows':row_count,'step_rows':step_count,'categories':merge_evidence}),
 (7,'Worker settings honored',manifest['invocations'][0]['peak_workers']==2 and manifest['invocations'][1]['peak_workers']==8,{'requested_and_peak':[[i['requested_workers'],i['peak_workers']] for i in manifest['invocations'][:2]]}),
 (8,'Matched substrate differences',any(d['differing_fields'] for d in substrate_differences),{'pairs_with_differences':sum(bool(d['differing_fields']) for d in substrate_differences),'paired_cells_and_seeds':len(substrate_differences),'differences':substrate_differences}),
]
results={'non_registered':True,'smoke_unique_runs':40,'repeat_validation_runs':2,'measured_runs_launched':0,
         'checks':[{'number':n,'check':name,'demonstrated':met,'evidence':evidence} for n,name,met,evidence in check_definitions],
         'mean_seconds_per_run':timings,'ideal_wall_clock_hours':projection,
         'normal_cap_15_wall_clock_hours':total_worker_seconds/15/3600,
         'projection_basis':'7540 * (mean v20 seconds + mean v21 seconds) / workers; excludes startup and merge overhead; assumes smoke timing represents the full grid.',
         'completion_source_readings':ns['verify_pins']()}
for sub,src in manifest['sources'].items():
 assert ns['source_identity'](Path(src['path']))==src
ns['atomic_json'](D/'phase_b_recon_b5_validation_results.json',results)
print('VALIDATION COMPLETE: 40 unique smoke runs, 2 repeat probes, zero measured runs.',flush=True)
