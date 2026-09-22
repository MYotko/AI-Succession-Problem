
def file_digest(path):
    h = hashlib.sha256()
    tail = b""
    with path.open("rb") as f:
        while True:
            chunk = f.read(1024*1024)
            if not chunk:
                break
            chunk = tail + chunk
            tail = b"\r" if chunk.endswith(b"\r") else b""
            if tail:
                chunk = chunk[:-1]
            h.update(chunk.replace(b"\r\n", b"\n"))
    h.update(tail)
    return h.hexdigest()

def merge_category(prefix, category, records, manifest, manifest_path):
    # Stream step evidence. A full category can contain over a million rows.
    import contextlib
    files = category_files(prefix, category)
    ordered = sorted((r for r in records.values() if r["key"]["category"] == category),
                     key=lambda r:tuple(r["key"][k] for k in KEYS))
    temps = {k:p.with_name(p.name+".tmp."+str(os.getpid())) for k,p in files.items()}
    total_steps = 0
    with contextlib.ExitStack() as stack:
        if files["steps"].exists():
            oldfile = stack.enter_context(files["steps"].open(newline="",encoding="utf-8"))
            oldgroups = iter(itertools.groupby(csv.DictReader(oldfile),key=job_id))
            old_id, old_rows = next(oldgroups, (None,None))
        else:
            oldgroups = iter(())
            old_id, old_rows = None,None
        streams = {k:stack.enter_context(p.open("wb")) for k,p in temps.items()}
        streams["rows"].write(csv_bytes([],ROW_FIELDS,header=True))
        streams["steps"].write(csv_bytes([],STEP_FIELDS,header=True))
        for record in ordered:
            task = record["task"]
            ident = job_id(task)
            fp = paths(prefix,task)
            with contextlib.ExitStack() as runstack:
                if fp["steps"].exists():
                    source = runstack.enter_context(fp["steps"].open(newline="",encoding="utf-8"))
                    steps = csv.DictReader(source)
                else:
                    assert old_id == ident, "Missing step evidence for "+ident
                    steps = old_rows
                h = hashlib.sha256()
                count = 0
                for step in steps:
                    assert job_id(step) == ident
                    assert int(step["step"]) == count
                    data = csv_bytes([step],STEP_FIELDS)
                    streams["steps"].write(data)
                    h.update(data)
                    count += 1
                assert count == record["step_row_count"]
                assert h.hexdigest() == record["steps_sha256_lf"]
                total_steps += count
            if old_id == ident:
                old_id,old_rows = next(oldgroups,(None,None))
            data = csv_bytes([record["row"]],ROW_FIELDS)
            assert digest(data) == record["row_sha256_lf"]
            if fp["row"].exists():
                with fp["row"].open(newline="",encoding="utf-8") as source:
                    rows = list(csv.DictReader(source))
                assert len(rows)==1 and digest(csv_bytes(rows,ROW_FIELDS))==record["row_sha256_lf"]
            streams["rows"].write(data)
            streams["completions"].write((canonical(record)+"\n").encode())
        assert old_id is None, "Previous merged evidence would be omitted"
        for stream in streams.values():
            stream.flush()
            os.fsync(stream.fileno())
    # Publish only complete files. Per-run originals remain until every check finishes.
    for kind,path in files.items():
        retry("atomic_replace",path,lambda p=path,t=temps[kind]:os.replace(t,p))
    expected = {job_id(r["key"]):r for r in ordered}
    seen_rows = set()
    with files["rows"].open(newline="",encoding="utf-8") as f:
        for row in csv.DictReader(f):
            ident = job_id(row)
            assert ident in expected and ident not in seen_rows
            assert digest(csv_bytes([row],ROW_FIELDS))==expected[ident]["row_sha256_lf"]
            seen_rows.add(ident)
    assert seen_rows == set(expected)
    seen_steps = set()
    with files["steps"].open(newline="",encoding="utf-8") as f:
        for ident,steps in itertools.groupby(csv.DictReader(f),key=job_id):
            assert ident in expected and ident not in seen_steps
            h = hashlib.sha256()
            count = 0
            for step in steps:
                assert int(step["step"]) == count
                h.update(csv_bytes([step],STEP_FIELDS))
                count += 1
            r = expected[ident]
            assert count == r["step_row_count"]
            assert h.hexdigest() == r["steps_sha256_lf"]
            seen_steps.add(ident)
    assert seen_steps == set(expected)
    with files["completions"].open(encoding="utf-8") as f:
        for record,line in itertools.zip_longest(ordered,f):
            assert record is not None and line is not None and json.loads(line)==record
    for ident,r in expected.items():
        manifest.setdefault("runs",{})[ident] = {
            "key":r["key"],"row_count":1,"row_sha256_lf":r["row_sha256_lf"],
            "step_row_count":r["step_row_count"],"steps_sha256_lf":r["steps_sha256_lf"]}
    manifest.setdefault("merged_files",{})[category] = {
        k:{"path":str(p),"sha256_lf":file_digest(p),
           "row_count":total_steps if k=="steps" else len(ordered)} for k,p in files.items()}
    atomic_json(manifest_path,manifest)
    for r in ordered:
        for kind,path in paths(prefix,r["task"]).items():
            if path.exists():
                path.unlink()
                deleted=manifest.setdefault("deleted_per_run_files",{})
                deleted[kind]=deleted.get(kind,0)+1
    atomic_json(manifest_path,manifest)
