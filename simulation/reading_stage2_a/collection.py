"""A10.3: common collection, document form and literal file-leaf labels."""
import hashlib
import stat
from pathlib import Path
from .common import require,canonical,seal,unseal,loads,write
FAMILIES={'sqrt','crowding','sigma_squared_x10','sigma_squared_x0.1'}
ARM_FAMILY={'table','validation_receipt','cell_results','a10_receipt','identity','admission_check','a16'}
COMPARATOR_FAMILY={'table','validation_receipt','cell_results','a10_receipt','labels','identity','admission_check',
                  'a13_round_admission','a13_round_record','a14_round_record','a14_public_record','a13_public_record'}

def object_keys(value,required,optional=frozenset()):
    require(isinstance(value,dict) and required<=set(value)<=required|optional,'input document form')

def string(value): require(isinstance(value,str),'input document form')

def document_form(doc):
    required={'schema','fixture','execution_simulation','authorized_hashes','registration','arms','comparator'}
    object_keys(doc,required,{'path_map'})
    require(doc['schema']=='a10-stage2-reader-inputs-1' and type(doc['fixture']) is bool,'input document form')
    if 'path_map' in doc:
        require(doc['fixture'] and isinstance(doc['path_map'],dict),'registered path_map')
    for k in ('execution_simulation','authorized_hashes'):string(doc[k])
    object_keys(doc['arms'],FAMILIES)
    for arm in doc['arms'].values():
        require(isinstance(arm,dict) and arm.get('status') in ('run','not_run'),'input document form')
        if arm['status']=='not_run':
            object_keys(arm,{'status','evidence'})
            ev=arm['evidence'];require(isinstance(ev,dict),'input document form')
            require(set(ev) in ({'refused_admission_record','closeout_record'}, {'refused_admission_record','a16_family_record','a16_round_admission_records'}),'not-run evidence set')
            for k,v in ev.items():
                if k=='a16_round_admission_records':
                    require(isinstance(v,list),'input document form')
                    for item in v:string(item)
                else:string(v)
            continue
        object_keys(arm,{'status','inventory','spec','pre_spec','root','family','calibration','excluded_roots'})
        for k in ('inventory','spec','root','calibration'):string(arm[k])
        require(arm['pre_spec'] is None or isinstance(arm['pre_spec'],str),'input document form')
        # A11.2: family/a16/registration structures are verify-only tests.
        # file_leaves still validates every traversed leaf before collection.
        require(isinstance(arm['excluded_roots'],list),'input document form')
        for ex in arm['excluded_roots']:
            require(isinstance(ex,dict) and isinstance(ex.get('path'),str),'input document form')
            require(Path(ex['path']).is_absolute(),'collection relative path')
    cp=doc['comparator'];object_keys(cp,{'binding','execution_simulation','spec','root','family','calibration'})
    for k,v in cp.items():
        if k!='family':string(v)
    object_keys(cp['family'],COMPARATOR_FAMILY)
    for v in cp['family'].values():string(v)

def verification_form(doc):
    """A11.2: the four structures excluded from collect's exhaustive form test."""
    object_keys(doc['registration'],{'commit','path','sha256'})
    for value in doc['registration'].values():string(value)
    for arm in doc['arms'].values():
        if arm['status']!='run':continue
        family=arm['family'];object_keys(family,ARM_FAMILY,{'labels'})
        for key,value in family.items():
            if key!='a16':string(value)
        a16=family['a16']
        if a16 is not None:
            object_keys(a16,{'family_record','rounds'});string(a16['family_record'])
            require(isinstance(a16['rounds'],dict) and set(a16['rounds']) in ({'r1'},{'r1','r2'}),'input document form')
            for rd in a16['rounds'].values():
                object_keys(rd,{'round_record','admission_record','public'})
                for value in rd.values():string(value)
        for ex in arm['excluded_roots']:
            object_keys(ex,{'path','reason','inventory_key'})
            for value in ex.values():string(value)

def file_leaves(doc):
    leaves={}
    def walk(value,label):
        if value is None:return
        if isinstance(value,str):leaves[label]=value
        elif isinstance(value,dict):
            for k,v in value.items():walk(v,label+'/'+k)
        elif isinstance(value,list):
            for ix,v in enumerate(value):walk(v,label+'/'+str(ix))
        else:require(False,'collection leaf type')
    walk(doc['authorized_hashes'],'authorized_hashes')
    for name,arm in doc['arms'].items():
        for k,v in arm.items():
            if k not in ('status','root','excluded_roots'):walk(v,'arms/'+name+'/'+k)
    for k,v in doc['comparator'].items():
        if k not in ('execution_simulation','root'):walk(v,'comparator/'+k)
    return dict(sorted(leaves.items()))

def input_roots(doc):
    roots=[doc['execution_simulation'],doc['comparator']['execution_simulation'],doc['comparator']['root']]
    for arm in doc['arms'].values():
        if arm['status']=='run':roots.extend([arm['root']]+[ex['path'] for ex in arm['excluded_roots']])
    return roots

def destination(doc,out):
    p=Path(out).resolve()
    require(not p.exists(),'output destination exists')
    require(all(not p.is_relative_to(Path(root).resolve()) for root in input_roots(doc)),'output overlaps an input root')

def read_leaf(path,label):
    # A10.11's test replaces only this hook, including regular-file validation.
    require(stat.S_ISREG(Path(path).stat().st_mode),'collection leaf not regular')
    with Path(path).open('rb') as stream:
        import os
        require(stat.S_ISREG(os.fstat(stream.fileno()).st_mode),'collection leaf not regular')
        return stream.read()

def collection_documents(doc):
    document_form(doc)
    leaves=file_leaves(doc)
    require(all(Path(p).is_absolute() for p in [*input_roots(doc),*leaves.values()]),'collection relative path')
    files={}
    for label,path in leaves.items():
        raw=read_leaf(path,label)
        files[label]=dict(bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())
    inputs=canonical(doc)+b'\n'
    return doc,seal(dict(schema='a10-stage2-collection-1',inputs_sha256=hashlib.sha256(inputs).hexdigest(),files=files))

def collect(inputs_path,out):
    doc=loads(Path(inputs_path).read_bytes());document_form(doc);destination(doc,out)
    doc,col=collection_documents(doc)
    write(Path(out)/'inputs.json',doc);write(Path(out)/'collection.json',col)
    return hashlib.sha256(canonical(col)+b'\n').hexdigest()

def verify_collection(ledger,inputs_path,doc):
    p=Path(inputs_path)
    require(p.name=='inputs.json','reading requires sealed collection')
    col=ledger.load(p.parent/'collection.json','collection',sealed=True)
    require(isinstance(col,dict) and set(col)=={'schema','inputs_sha256','files'} and col['schema']=='a10-stage2-collection-1','collection schema')
    require(col['inputs_sha256']==ledger.hash('inputs'),'collection input binding')
    leaves=file_leaves(doc)
    require(isinstance(col['files'],dict) and set(col['files'])==set(leaves),'collection file inventory')
    for label,path in leaves.items():
        entry=col['files'][label]
        require(isinstance(entry,dict) and set(entry)=={'bytes','sha256'} and type(entry['bytes']) is int and entry['bytes']>=0 and isinstance(entry['sha256'],str),'collection file entry')
        raw=ledger.raw(path,'collected/'+label,entry['sha256'])
        require(len(raw)==entry['bytes'],'collection file bytes')
    return ledger.hash('collection')
