"""Hash-bound, read-only snapshots for A11 workers. No job is rewritten."""
import base64
import hashlib
import os
from pathlib import Path
from .artifacts import SIMULATION, ROOT, scoped, seal, unseal, digest, file_hash, atomic_json


def inventory(jobs, phase_root, extra_inputs=()):
    """Enumerate execute() reads, including plain A4's preceding fit output.

    A5 embeds its tested rows in the job. Reruns read the published family and
    its receipt (which embeds labels). Probe records are explicit audit inputs.
    Source manifests and completion records travel with their source outputs.
    """
    paths = set()

    def add(path):
        path = Path(path).resolve()
        if not path.is_relative_to(ROOT) or not path.is_file():
            raise ValueError('missing or out-of-scope A11 input: ' + str(path))
        paths.add(path)

    for job in jobs:
        c = job['config']
        if c.get('calibration_path'):
            add(SIMULATION / c['calibration_path'])
            # A6 variant validation reads its frozen parent as well.
            add(ROOT / 'runs/registered/v3_rerun_calibration.json')
        if c.get('tables_path'):
            table = SIMULATION / c['tables_path']
            add(table)
            for suffix in ('.a10_receipt.json', '.compatibility.json', '.cell_results.json'):
                sibling = table.with_suffix(suffix)
                if sibling.exists():
                    add(sibling)
        if job['kind'] in ('a4_fit', 'a4_validate', 'a4_census', 'a5_fvplain'):
            source = Path(c['a1_source_root'])
            a1 = c['a1_job']
            add(SIMULATION / a1['config']['calibration_path'])
            add(ROOT / 'runs/registered/v3_rerun_calibration.json')
            for name in ('tables_A1_manifest.json', 'v3_rerun_tables_A1.json'):
                add(source / name)
            for directory in ('outputs', 'records'):
                add(source / 'tables_A1/table' / directory / (a1['id'] + '.json'))
            if job['kind'] == 'a4_validate' and c['route'] == 'plain' and not c.get('self_contained'):
                from .table_validation_a4 import _fit_job_id
                for directory in ('outputs', 'records'):
                    add(Path(phase_root).parent / 'fit' / directory / (_fit_job_id(c) + '.json'))
    for name in extra_inputs:
        path = Path(name)
        if not path.is_absolute():
            path = SIMULATION / path
        if path.is_dir():
            for child in sorted(path.rglob('*')):
                if child.is_file():
                    add(child)
        else:
            add(path)
    files = [{'path': p.relative_to(SIMULATION).as_posix(), 'sha256': file_hash(p), 'bytes': p.stat().st_size}
             for p in sorted(paths)]
    return seal({'schema': 'v3-A11-inputs-1', 'simulation': str(SIMULATION), 'files': files})


def fetch(document, name, offset=0, size=4 * 1024 * 1024):
    payload = unseal(document)
    row = next((r for r in payload['files'] if r['path'] == name), None)
    if row is None or not isinstance(offset, int) or offset < 0 or not 1 <= size <= 4 * 1024 * 1024:
        raise ValueError('invalid input transfer')
    path = Path(payload['simulation']) / row['path']
    if file_hash(path) != row['sha256']:
        raise ValueError('frozen input changed')
    with path.open('rb') as stream:
        stream.seek(offset)
        data = stream.read(size)
    return {'data': base64.b64encode(data).decode('ascii'), 'offset': offset, 'sha256': hashlib.sha256(data).hexdigest()}


def receive(document, directory, reader):
    """reader(name, offset) may use SSH or loopback. Partial files never map."""
    payload = unseal(document)
    directory = scoped(directory) / document['sha256']
    paths = {}
    for row in payload['files']:
        relative = Path(row['path'])
        if relative.is_absolute() or '..' in relative.parts or relative.parts[0] != 'v3':
            raise ValueError('unsafe input path')
        target = scoped(directory / relative)
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            partial = target.with_name(target.name + '.partial')
            with partial.open('wb') as stream:
                offset = 0
                while offset < row['bytes']:
                    block = reader(row['path'], offset)
                    data = base64.b64decode(block['data'], validate=True)
                    if (block['offset'] != offset or not data or hashlib.sha256(data).hexdigest() != block['sha256']
                            or offset + len(data) > row['bytes']):
                        raise ValueError('corrupt input transfer')
                    stream.write(data)
                    offset += len(data)
                stream.flush()
                os.fsync(stream.fileno())
            if file_hash(partial) != row['sha256']:
                raise ValueError('input hash mismatch')
            os.replace(partial, target)
            target.chmod(0o444)
        if file_hash(target) != row['sha256']:
            raise ValueError('existing snapshot differs')
        for alias in (Path(payload['simulation']) / relative, SIMULATION / relative, target):
            paths[str(alias.resolve())] = str(target)
    # Protect only declared input locations. Configuration scratch and code
    # files remain local; unlisted sibling inputs cannot be read accidentally.
    protected = sorted({str(Path(p).parent) for p in paths if not Path(p).is_relative_to(directory)})
    view = {'paths': paths, 'protected': protected, 'snapshot_sha256': document['sha256']}
    atomic_json(directory / 'verified.json', seal(view))
    return view
