
"""Apply the tested streaming merge after the original smoke batch has finished."""
import sys
sys.dont_write_bytecode=True
import ast,json,runpy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];D=ROOT/'simulation'/'diagnostics'
P=D/'phase_b_recon_executor.py'
ns=runpy.run_path(str(P),run_name='merge_repair')
ns['install_guard']('phase_b_recon_')
progress=ns['read_json'](D/'phase_b_recon_progress.json')
assert progress['status']=='complete' and progress['running']==0 and progress['completed']==40
old=P.read_text(encoding='utf-8')
old_hash=ns['digest'](old.encode())
source=D/('phase_b_recon_smoke_executor_source_'+old_hash+'.py')
assert not source.exists()
source.write_text(old,encoding='utf-8',newline='\n')
merge=(D/'phase_b_recon_b5_stream_merge.py').read_text(encoding='utf-8')
start=old.index('def merge_category(')
end=old.index('def cpu_budget(',start)
new=old[:start]+'COMPATIBLE_EXECUTOR_HASHES = frozenset({'+repr(old_hash)+'})\n'+merge+'\n'+old[end:]
new=new.replace('assert obj["code_sha256_lf"] == code, "Completion executor code differs"',
                'assert obj["code_sha256_lf"] in ({code} | COMPATIBLE_EXECUTOR_HASHES), "Completion executor code differs"')
new=new.replace('assert previous["executor_sha256_lf"] == code, "Executor changed since previous invocation"',
                'assert previous["executor_sha256_lf"] in ({code} | COMPATIBLE_EXECUTOR_HASHES), "Executor changed since previous invocation"')
new=new.replace('assert record["code_sha256_lf"] == code',
                'assert record["code_sha256_lf"] in ({code} | COMPATIBLE_EXECUTOR_HASHES)')
needle='''    manifest["sources"].update(sources)'''
replacement='''    versions = manifest.setdefault("executor_versions", [manifest["executor_sha256_lf"]])
    if code not in versions:
        versions.append(code)
    manifest["executor_sha256_lf"] = code
    source_copy = DIAG/(prefix+"executor_source_"+code+".py")
    if not source_copy.exists():
        atomic_bytes(source_copy,Path(__file__).read_bytes())
    manifest["sources"].update(sources)'''
assert needle in new
new=new.replace(needle,replacement)
ast.parse(new)
before=ast.parse(old);after=ast.parse(new)
ignored={'merge_category','main','read_completion'}
before_functions={n.name:ast.dump(n,include_attributes=False) for n in before.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name not in ignored}
after_functions={n.name:ast.dump(n,include_attributes=False) for n in after.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name in before_functions}
assert before_functions==after_functions
before_assign=[ast.dump(n,include_attributes=False) for n in before.body if isinstance(n,ast.Assign)]
after_assign=[ast.dump(n,include_attributes=False) for n in after.body if isinstance(n,ast.Assign) and not any(isinstance(t,ast.Name) and t.id=='COMPATIBLE_EXECUTOR_HASHES' for t in n.targets)]
assert before_assign==after_assign
P.write_text(new,encoding='utf-8',newline='\n')
proof={'old_executor_sha256_lf':old_hash,'new_executor_sha256_lf':ns['digest'](new.encode()),
       'unchanged_functions':sorted(before_functions),'all_prior_global_assignments_unchanged':True,
       'operational_changes_only':['stream category merge and verification','accept the single prior identical-worker executor version on resume','retain executor source versions'],
       'prior_completion_records_not_rewritten':True}
ns['atomic_json'](D/'phase_b_recon_b5_merge_repair_proof.json',proof)
pre=ns['read_json'](D/'phase_b_recon_b5_preflight.json')
pre['executor_self_fixes'].append('Streamed category merging and hash verification to bound memory, preserving prior completions from the verified identical worker code.')
ns['atomic_json'](D/'phase_b_recon_b5_preflight.json',pre)
print('Streaming merge installed; worker, grid, recorder and prior globals are AST-identical.')
