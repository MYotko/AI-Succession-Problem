"""Finalize required supervision metadata after the executor has completed."""
import sys
sys.dont_write_bytecode=True
import defense_recovery_run_conf_executor as ex
import json,csv
m=ex.read(ex.P+'manifest.json')
assert m['status']=='COMPLETE'
event=ex.read(ex.P+'supervision.json')
messages=event['tool_layer_workarounds']
for message in messages:
    if message not in m['tool_layer_workarounds']:m['tool_layer_workarounds'].append(message)
report=ex.OUT/(ex.P+'report.md')
text=report.read_text(encoding='utf-8')
text+='\n\nSupervision tool-layer workarounds recorded after executor startup:\n\n'
text+='\n'.join('- '+message for message in messages)+'\n'
assert chr(0x2014) not in text
temp=ex.OUT/(ex.P+'report_metadata.tmp')
with temp.open('x',encoding='utf-8',newline='\n') as handle:
    handle.write(text);handle.flush();ex.os.fsync(handle.fileno())
ex.replace_with_retry(temp,report)
m['source_readings']=ex.pins(full=True)
m['supervision_metadata']={'source':ex.P+'supervision.json','finalizer':ex.P+'finalize_supervision.py','utc':ex.now()}
retries=[]
for path in sorted(ex.OUT.glob(ex.P+'io_events_*.jsonl')):
    with path.open(encoding='utf-8') as handle:retries.extend(json.loads(line) for line in handle)
m['retry_events']=retries
outputs=[]
for path in sorted(ex.OUT.glob(ex.P+'*')):
    if not path.is_file() or path.name==ex.P+'manifest.json':continue
    rows=None;jsonl_rows=None
    if path.suffix=='.csv':
        with path.open(encoding='utf-8',newline='') as handle:rows=sum(1 for _ in csv.DictReader(handle))
    if path.suffix=='.jsonl':
        with path.open(encoding='utf-8') as handle:jsonl_rows=sum(1 for line in handle if line.strip())
    outputs.append({'path':path.relative_to(ex.ROOT).as_posix(),'sha256_lf':ex.sha(ex.lf(path.read_bytes())),
                    'hash_basis':'LF-normalized bytes','csv_row_count':rows,'jsonl_row_count':jsonl_rows})
m['outputs']=outputs
ex.write(ex.P+'manifest.json',m)
print(json.dumps({'status':m['status'],'tool_layer_workarounds':len(m['tool_layer_workarounds']),'executor_fixes':len(m['executor_fixes']),'outputs':len(outputs)}))
