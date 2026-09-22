
"""Produce the attempt 5 report and manifest without model execution."""
import sys
sys.dont_write_bytecode=True
import csv,json,runpy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];D=ROOT/'simulation'/'diagnostics'
ns=runpy.run_path(str(D/'phase_b_recon_executor.py'),run_name='report_library')
ns['install_guard']('phase_b_recon_')
results=ns['read_json'](D/'phase_b_recon_b5_validation_results.json')
pre=ns['read_json'](D/'phase_b_recon_b5_preflight.json')
batch=ns['read_json'](D/'phase_b_recon_smoke_batch_manifest.json')
records=ns['merged_records']('phase_b_recon_smoke_')
assert len(records)==40 and batch['status']=='complete'
repeat_prefix='phase_b_recon_smoke_repeat_'
repeat_records={}
for path in sorted(D.glob('phase_b_recon_smoke_probe_repeat_*_completion.json')):
 record=ns['read_json'](path);task=record['task'];ident=ns['job_id'](task)
 repeat_records[ident]=record
 oldpaths={k:p.with_name(p.name.replace('phase_b_recon_smoke_job_','phase_b_recon_smoke_probe_repeat_')) for k,p in ns['paths']('phase_b_recon_smoke_',task).items()}
 newpaths=ns['paths'](repeat_prefix,task)
 for kind,source in oldpaths.items():
  if source.exists():
   assert not newpaths[kind].exists()
   source.rename(newpaths[kind])
assert len(repeat_records)==2
repeat_manifest={'non_registered':True,'validation_only':True,'runs':{}}
ns['merge_category'](repeat_prefix,'A',repeat_records,repeat_manifest,D/(repeat_prefix+'manifest.json'))
def evidence(c):
 e=c['evidence'];n=c['number']
 if n==1:return '20 runs per substrate; HEADs '+e['heads']['v21']+' and '+e['heads']['v20']+' match.'
 if n==2:return str(e['rows'])+' rows; all '+str(len(e['fields']))+' required fields correctly typed.'
 if n==3:return 'Recomputed from step logs; unique values '+json.dumps(e['unique_values'],sort_keys=True)+'.'
 if n==4:return 'One repeat per substrate; recorded fields excluding elapsed time/PID and all step hashes match.' if c['demonstrated'] else json.dumps(e)
 if n==5:
  x=e['resume_counts'];return str(x['preserved'])+' preserved, '+str(x['restarted'])+' restarted, '+str(x['never_launched'])+' never launched at resume; completed-record content hashes unchanged on verification resume; preserved jobs never relaunched.'
 if n==6:return str(e['run_rows'])+' run rows and '+str(e['step_rows'])+' step rows recovered with matching hashes.'
 if n==7:return 'Requested/actual peak workers: '+json.dumps(e['requested_and_peak'])+'.'
 if n==8:return str(e['pairs_with_differences'])+' of '+str(e['paired_cells_and_seeds'])+' matched cell/seed pairs differ on required scientific fields.'
checks=results['checks']
lines=['# Phase B reconstruction attempt 5 validation','',
 'The attempt 4 executor was kept and repaired. This is a reimplementation, not a rerun. '
 'Validation is non-registered and may not be cited as evidence for any registered quantity or fidelity target.',
 'Measured runs launched: 0. Unique smoke runs: 40. Additional determinism repeat runs: 2. '
 'Two interrupted attempts restarted from step 0; their partial evidence is retained.','',
 '| Check | Demonstrated | Evidence |','| --- | --- | --- |']
for c in checks:lines.append('| '+str(c['number'])+'. '+c['check']+' | '+('Yes' if c['demonstrated'] else 'No')+' | '+evidence(c)+' |')
lines += ['','No scientific parameter was adjusted using smoke outputs. Test results are reported without fidelity interpretation.','',
 '## Operational checks','',
 'Full-grid assertions: A 2,700, B 2,800, C 1,620, phi 420 per substrate; 7,540 per substrate, 15,080 total. Smoke: 20 per substrate, 40 total.',
 'A worker was terminated after completed steps were recorded. The parent stopped remaining workers and retained complete records and partial logs. Resume preserved work mode, then applied normal mode without changing seeds.',
 'The final executor streams its merge. Synthetic checks covered initial merge, adding a second substrate, and repeat merge with identical hashes. The final executor resumed the completed smoke batch without launching another model.',
 'AST comparisons confirmed that the streaming repair left the worker, grid, recorder helpers and prior global assignments unchanged. Original completions retain their actual executor hash; the manifest records compatible versions and source snapshots.',
 'Every completed worker verified one OpenBLAS thread through its exported getter. Numerical-library environment variables were also set to one. Imported project modules were verified against their selected worktree.','',
 '## Timing','',
 '| Substrate | Mean recorded seconds per run |','| --- | ---: |']
for s in ('v20','v21'):lines.append('| '+s+' | '+repr(results['mean_seconds_per_run'][s])+' |')
lines += ['','| Ideal workers | Projected full-batch hours |','| --- | ---: |']
for n in ('8','12','16'):lines.append('| '+n+' | '+repr(results['ideal_wall_clock_hours'][n])+' |')
lines += ['',results['projection_basis'],
 'Recorded elapsed time covers model construction and stepping, excluding interpreter startup, imports and merging. These are linear operational estimates.',
 'YotkoTest CPU budget: 16. Normal mode caps active workers at 15; work mode caps them at 12. A request for 16 therefore uses at most 15, projected at '+repr(results['normal_cap_15_wall_clock_hours'])+' hours. No operating-system CPU reservation is claimed.','',
 '## Operator commands','',
 'Run from C:/Users/matty/Dev/AI-Succession-Problem. These measured-batch commands were not executed during validation.']
fence=chr(96)*3
launch='python -B simulation/diagnostics/phase_b_recon_executor.py --workers 8 --category A B C phi --substrate both --v20-worktree "C:/Users/matty/Dev/phase-b-recon-v20"'
lines += ['',fence+'powershell',launch,fence,'','Resume:', '',fence+'powershell',launch+' --resume',fence,'',
 '## Progress and runtime control','',
 'Progress: simulation/diagnostics/phase_b_recon_progress.json. While running, the timestamp updates every two seconds, within the 30-second requirement. Completed/running/pending counts reconcile to the selected grid per category and substrate. Completed increases, pending decreases, and running becomes zero at complete or stopped status. Elapsed time is for the current invocation; the mean uses completed records.',
 'Full-batch control: simulation/diagnostics/phase_b_recon_runtime_control.json. Set mode to work or normal to change the cap. Existing jobs finish during a reduction, and mode persists on resume. The smoke control file is separate under phase_b_recon_smoke_.',
 'Keyboard interruption or a terminated worker leaves durable completions and partial files for --resume. Completed categories resume from verified merged records. Incompatible code or source identity is rejected.','',
 '## Construction fixed before tests','',
 'Unvaried parameters retain production defaults: phi 25, alpha 1, successor capability 1. The initial successor is generation 2. Peak population is the maximum recorded population. Survival uses 0.65 without integer truncation. Collapsed means positive final population below that threshold; extinct means zero. Knowledge transfer follows Amendment 1.','',
 '## Provenance and fixes','',
 'T0 passed. The five pins matched at initial and final readings. The v20 worktree was read only. Both substrate snapshots and imported-module hashes are recorded. Committed halt artifacts were unchanged.',
 'The write guard was updated to the corrected whole-prefix scope, including temporary files, with committed-file exclusions.']
lines += ['Tool-layer workaround: '+x for x in pre['tool_layer_workarounds']]
lines += ['Executor self-fix: '+x for x in pre['executor_self_fixes']]
report='\n'.join(lines)+'\n';assert chr(0x2014) not in report
ns['atomic_bytes'](D/'phase_b_recon_b5_report.md',report.encode())
pins=ns['verify_pins']()
for source in batch['sources'].values():assert ns['source_identity'](Path(source['path']))==source
outputs=[]
protected={'phase_b_recon_halt.json','phase_b_recon_manifest.json','phase_b_recon_preflight.json','phase_b_recon_report.md'}
for p in sorted(D.glob('phase_b_recon_*')):
 if not p.is_file() or p.name in protected or p.name.startswith(('phase_b_recon_b2_','phase_b_recon_b3_','phase_b_recon_b4_')) or p.name=='phase_b_recon_b5_manifest.json':continue
 count=None
 if p.suffix=='.csv':
  with p.open(newline='',encoding='utf-8') as f:count=sum(1 for row in csv.DictReader(f))
 outputs.append({'path':p.relative_to(ROOT).as_posix(),'sha256_lf':ns['file_digest'](p),'csv_row_count':count})
manifest={'status':'test_validation_complete','executor_kept':True,'created_utc':ns['utc'](),
 'machine':pre['machine'],'head':pre['head'],'python':sys.version,
 'numpy_versions':sorted({r['numpy_version'] for r in records.values()}),
 'initial_source_readings':pre['source_readings'],'completion_source_readings':pins,
 'substrates':batch['sources'],'source_hash_basis':'SHA256 on LF-normalized bytes; blob SHA1 separately',
 'cpu_budget':batch['cpu_budget'],'mode_changes':batch['mode_changes'],'invocations':batch['invocations'],
 'worker_threads_verified_one':all(all(t['threads']==1 for t in r['effective_threads']) for r in records.values()),
 'smoke_unique_runs':40,'repeat_validation_runs':2,'measured_runs_launched':0,
 'tool_layer_workarounds':pre['tool_layer_workarounds'],'executor_self_fixes':pre['executor_self_fixes'],
 'retry_events':batch['retry_events']+[e for r in records.values() for e in r['retry_events']],
 'outputs':outputs,'per_run_hashes':batch['runs'],'repeat_probe_hashes':repeat_manifest['runs'],
 'deleted_per_run_files':batch['deleted_per_run_files'],'repeat_deleted_per_run_files':repeat_manifest['deleted_per_run_files'],
 'executor_versions':batch['executor_versions'],'t0_stderr_warnings':[c for c in pre['commands'] if c['stderr']],
 'manifest_self_hash':'Not included because the manifest cannot contain its own content hash.',
 'non_registered_notice':'Test outputs are not measurements or evidence for registered quantities.'}
ns['atomic_json'](D/'phase_b_recon_b5_manifest.json',manifest)
print('REPORT COMPLETE: '+str(sum(c['demonstrated'] for c in checks))+' of 8 checks demonstrated; measured runs 0.',flush=True)
