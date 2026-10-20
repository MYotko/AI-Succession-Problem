"""Read-only A14 historical verifier. No A13 lifecycle operation is called."""
from copy import deepcopy
import hashlib
from pathlib import Path
import subprocess
import stat
import os
import shutil
import tempfile

from .artifacts import (SIMULATION, canonical, code_identity, digest, file_hash,
                        input_view, read, scoped, unseal, verify_registration)
from . import validation_extension_a13 as a13

PRODUCER = '5df9866f1a59ab9c6c67660c18fbee694a64f97d5eebb65a41c8deaf2d650d1c'
ADMISSION_HASH = '87f8b2453e04b178a4f2dcd40c07ae41b9ab06a350a70d5b57e834aa8e5c6dd7'
require = a13.require


def stage_history(document):
    """Copy inventoried files after reservation; verification stays read-only."""
    payload = unseal(document)
    require(all(Path(p).is_absolute() for r in payload['files']
                for p in [r['source'], r['copy'], *r.get('aliases', [])]), 'historical paths must be absolute')
    sources = {Path(p).resolve() for r in payload['files'] for p in [r['source'], *r.get('aliases', [])]}
    original_roots = [Path(p).resolve() for p in payload['directories']]
    protected = sources | {(SIMULATION / a13.TARGET).with_suffix('.a13_round.json').resolve(),
                           (SIMULATION / a13.TARGET).with_suffix('.a13_round.admission.json').resolve()}
    destinations = [scoped(r['copy']) for r in payload['files']]
    require(len(destinations) == len(set(destinations)), 'duplicate A14 history destination')
    require(all(p not in protected and not any(p.is_relative_to(root) for root in original_roots)
                for p in destinations), 'A14 copy would write a historical input')
    for row, target in zip(payload['files'], destinations):
        if not target.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            fd, name = tempfile.mkstemp(prefix='a14-copy-', dir=target.parent)
            temporary = Path(name)
            try:
                with os.fdopen(fd, 'wb') as output, Path(row['source']).open('rb') as source:
                    shutil.copyfileobj(source, output)
                    output.flush()
                    os.fsync(output.fileno())
                require(temporary.stat().st_size == row['bytes']
                        and hashlib.sha256(temporary.read_bytes()).hexdigest() == row['sha256'], 'historical transfer hash mismatch')
                os.replace(temporary, target)
            finally:
                if temporary.exists():
                    temporary.unlink()
        require(target.stat().st_size == row['bytes']
                and hashlib.sha256(target.read_bytes()).hexdigest() == row['sha256'], 'existing historical copy differs')
        target.chmod(0o444)


class History:
    """A sealed bijection of historical files to immutable execution copies.

    Directory mappings support unchanged assembly helpers' directory listing.
    Copies must contain exactly the declared files, with the original relative
    paths. They cannot point at the original directory.
    """
    def __init__(self, document):
        self.document = deepcopy(document)
        self.payload = unseal(self.document)
        require(self.payload['schema'] == 'v3-A14-history-1', 'invalid A14 history inventory')
        self.paths, self.original_paths, destinations = {}, {}, set()
        for row in self.payload['files']:
            require(all(Path(p).is_absolute() for p in [row['source'], row['copy'], *row.get('aliases', [])]),
                    'historical paths must be absolute')
            source = str(Path(row['source']).resolve())
            target = scoped(row['copy'])
            aliases = [str(Path(p).resolve()) for p in row.get('aliases', [])]
            require(source not in self.paths and not any(p in self.paths for p in aliases)
                    and str(target) not in destinations and source != str(target),
                    'duplicate or non-copy A14 history input')
            require(target.is_file() and target.stat().st_size == row['bytes']
                    and hashlib.sha256(target.read_bytes()).hexdigest() == row['sha256'], 'A14 historical copy changed')
            require(not target.stat().st_mode & (stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH),
                    'A14 historical copy must be read-only')
            self.paths[source] = str(target)
            self.original_paths[source] = str(target)
            self.paths.update({p: str(target) for p in aliases})
            destinations.add(str(target))
        self.directories = {}
        for source, target in self.payload['directories'].items():
            require(Path(source).is_absolute() and Path(target).is_absolute(), 'historical directories must be absolute')
            source, target = Path(source).resolve(), scoped(target)
            require(source != target and not target.is_relative_to(source), 'history copy overlaps original')
            declared = {Path(v) for k, v in self.original_paths.items() if Path(k).is_relative_to(source)}
            actual = {p.resolve() for p in target.rglob('*') if p.is_file()}
            require(actual == declared, 'undeclared or missing history copy file')
            for original, copied in self.original_paths.items():
                if Path(original).is_relative_to(source):
                    require(Path(copied) == target / Path(original).relative_to(source), 'history directory mapping changed')
            self.directories[str(source)] = str(target)
        self.roles = self.payload['roles']
        self.view = dict(paths=dict(self.paths), protected=sorted(set(self.directories) |
                         {str(Path(p).parent) for p in self.paths}))
        # A copy is also a protected view, so an unlisted sibling cannot enter
        # an unchanged historical helper's reads.
        self.view['paths'].update({v: v for v in self.paths.values()})
        self.view['protected'] += list(self.directories.values())

    def file(self, source):
        key = str(Path(source).resolve())
        require(key in self.paths, 'finding: historical path is unmapped')
        return Path(self.paths[key])

    def directory(self, source):
        key = str(Path(source).resolve())
        require(key in self.directories, 'finding: historical directory is unmapped')
        return Path(self.directories[key])

    def read(self, source):
        return read(self.file(source))

    def role(self, name):
        return self.roles[name]


def verify_producer(history, identity):
    """Verify the copied approval against committed bytes, without opening runs."""
    if identity == code_identity():
        return
    from .compatibility_a10 import COMPARISON, SCHEMA, _selected, changed_files, record_name
    from .artifacts import source_manifest
    new = code_identity()
    for source in history.payload.get('compatibility_records', []):
        path = Path(source)
        if path.name != record_name(identity, new):
            continue
        relative = path.resolve().relative_to(SIMULATION.parent).as_posix()
        require(relative == 'simulation/v3/runs/registered/' + path.name, 'unregistered compatibility record')
        raw = history.file(path).read_bytes()
        committed = subprocess.run(['git', '-C', str(SIMULATION.parent), 'show', 'HEAD:' + relative],
                                   check=True, capture_output=True).stdout
        require(raw == committed, 'compatibility copy differs from committed record')
        record = unseal(history.read(path))
        require(record['schema'] == SCHEMA and record['passed'] is True
                and record['producing_code_hash'] == identity and record['new_code_hash'] == new
                and record['comparison'] == COMPARISON, 'incompatible historical proof')
        approval = record.get('operator_approval', {})
        require(approval.get('approved') is True and bool(approval.get('operator', '').strip()), 'proof not approved')
        from datetime import date
        date.fromisoformat(approval['date'])
        before, after = record['producing_source_manifest'], record['new_source_manifest']
        require(digest(before) == identity and after == source_manifest() and digest(after) == new,
                'historical proof source hashes changed')
        changes = changed_files(before, after)
        require(changes and changes == record['changed_files'] and set(record['reasons']) == set(changes)
                and all(isinstance(v, str) and v.strip() for v in record['reasons'].values()), 'incomplete proof diff')
        expected = _selected(record['populations'])
        proofs = record['proofs']
        require(len(proofs) == len(expected) and {p['job_id'] for p in proofs} == set(expected)
                and all(p['passed'] is True and p['before_sha256'] == p['after_sha256']
                        and len(p['after_sha256']) == 64 for p in proofs), 'incomplete historical proof')
        return
    raise ValueError('historical producer lacks a committed, approved compatibility record')


def verify_history(document, *, registered):
    """Return verified executor-only inputs/classifications; write nothing."""
    from .validation_extension_a14 import APPROVED_A13_PLAN
    from .production_runner import completed
    from .production_tables import row_key
    from .offline_estimator import add_ranking_flags
    from .context import Context
    from .artifacts import seal, stable_job
    h = History(document)
    with input_view(h.view):
        old = unseal(h.read(h.role('a13_plan')))
        original = unseal(h.read(old['original_plan_path']))
        candidate_path = Path(old['candidate_path'])
        candidate = h.read(candidate_path)
        payload = unseal(candidate)
        sidecar = unseal(h.read(candidate_path.with_suffix('.cell_results.json')))
        receipt = unseal(h.read(candidate_path.with_suffix('.compatibility.json')))
        require(old['schema'] == a13.SCHEMA and a13.plan_hash(old) == old['plan_hash']
                and old['round'] == 1 and old['R_max'] == 16,
                'A13 plan or bound changed')
        require(old['registered'] != bool(old.get('non_registered_rehearsal')), 'A13 launch mode changed')
        require(old['seed_check'] == a13.check_seed_manifest(old['seed_manifest'], old['forbidden_seeds'],
                    rehearsal=old.get('non_registered_rehearsal', False)), 'A13 seed check changed')
        require(old['jobs'] == [stable_job(a13.KIND, dict(c, plan_hash=old['plan_hash']), 'v3_tables', i)
                               for i, c in enumerate(old['job_skeletons'])], 'A13 job skeleton changed')
        require(old['M'] == original['M'] and all(c['M'] == old['M'] for c in old['job_skeletons']),
                'A13 pinned M changed')
        require(old['launch_allowed'] and original['pull_dispatch']['projection_sha256'] == old['pricing']['projection_sha256'],
                'A13 launch or original projection binding changed')
        if 'pull_dispatch' in old:
            require(old['pull_dispatch']['projection_sha256'] == old['pricing']['projection_sha256'],
                    'A13 dispatch projection changed')
        require(a13.a4._recompute_plan_hash(original) == original['plan_hash']
                and old['original_plan_hash'] == original['plan_hash'], 'original plan changed')
        require(file_hash(h.file(old['original_plan_path'])) == old['original_plan_file_sha256']
                and file_hash(h.file(candidate_path)) == old['candidate_file_sha256']
                and file_hash(h.file(candidate_path.with_suffix('.cell_results.json'))) == old['candidate_sidecar_sha256'],
                'A13 historical file binding changed')
        if registered:
            require(old['registered'] and old['plan_hash'] == APPROVED_A13_PLAN and old['code_hash'] == PRODUCER,
                    'A14 requires the approved A13 round')
            a13.a4.registered_publish_guard(original)
            require(not any(j['config'].get('settings_override') for j in old['jobs']),
                    'registered A13 settings override')
            for p in (old, original):
                verify_registration(p['registration'], instrument=p['instrument'], historical=True)
                verify_producer(h, p['code_hash'])
            verify_producer(h, original['source_code_hash'])
        public = unseal(h.read(h.role('a13_public')))
        require(public == a13.public_record(old), 'A13 public record differs from plan')
        root = Path(h.role('a13_root'))
        anchor = unseal(h.read(old['round_record_path']))
        require(anchor['plan_hash'] == old['plan_hash'] and anchor['spec_hash'] == digest(old)
                and Path(anchor['root']) == root and anchor['halt'] is None, 'A13 round not clean and bound')
        admission_path = Path(old['round_record_path']).with_suffix('.admission.json')
        admission = unseal(h.read(admission_path))
        require(admission['plan_hash'] == old['plan_hash'] and admission['outcome'] == 'refused',
                'A13 admission was not refused')
        if registered:
            require(file_hash(h.file(admission_path)) == ADMISSION_HASH, 'A13 admission identity changed')
        require(h.read(root / 'identity.json') == dict(code_hash=old['code_hash'], spec_hash=digest(old)), 'A13 root identity differs')
        launches = h.read(root / 'launches.json')
        require(launches and launches[-1].get('complete') is True, 'A13 last launch incomplete')
        check = h.read(root / a13.PHASE / 'nondeterminism_check.json')
        jobs = {j['id']: j for j in old['jobs']}
        require(check.get('matched') is True and check.get('checked') in jobs, 'A13 nondeterminism check missing')
        nd = h.read(root / ('_nd_' + a13.PHASE) / 'records' / (check['checked'] + '.json'))
        require(nd['status'] == 'complete' and nd['code_hash'] == old['code_hash']
                and nd['job'] == jobs[check['checked']], 'A13 nondeterminism completion differs')
        if 'pull_dispatch' in old:
            state = unseal(h.read(root / 'pull_state.json'))
            require(state.get('complete') and not state.get('halt')
                    and state.get('checks', {}).get(a13.PHASE) == check, 'A13 pull check incomplete')
        original_root = Path(old['original_run_root'])
        stage_root, source_root = h.directory(original_root), h.directory(original['source_root'])
        stage_hashes, stream_seeds, stages = {}, {}, {}
        for j in original['jobs']:
            phase = j['config']['phase']
            out_path = original_root / phase / 'outputs' / (j['id'] + '.json')
            h.file(out_path)
            h.file(original_root / phase / 'records' / (j['id'] + '.json'))
            output = completed(stage_root / phase, j, original['code_hash'])
            require(output is not None, 'missing verified original stage')
            result, c = output['result'], j['config']
            require(result['plan_hash'] == original['plan_hash'] and result['code_hash'] == original['code_hash']
                    and result['a1_job_id'] == c['a1_job']['id'] and result['stream_seed'] == c['seed'],
                    'original stage identity differs')
            stages[j['id']] = result
            stage_hashes[j['id']], stream_seeds[j['id']] = file_hash(h.file(out_path)), c['seed']
        require(receipt['plan_hash'] == original['plan_hash'] and receipt['M'] == original['M']
                and receipt['stream_seeds'] == stream_seeds and receipt['stage_output_sha256'] == stage_hashes,
                'original receipt changed')
        require(receipt['table_seal_sha256'] == candidate['sha256'] and receipt['table_file_sha256'] == file_hash(h.file(candidate_path))
                and receipt['cell_results_sha256'] == file_hash(h.file(candidate_path.with_suffix('.cell_results.json')))
                and sidecar['plan_hash'] == original['plan_hash'] and sidecar['table_seal_sha256'] == candidate['sha256'],
                'original candidate/sidecar binding changed')
        calibration = h.read(SIMULATION / original['calibration_path'])
        # The original A10 source checks, using only this verified view and
        # copied committed proofs, rather than scanning a current runs tree.
        from . import tables_a10
        from .calibration import validate_calibration
        validate_calibration(calibration, registered=registered, instrument=original['instrument'])
        family_path = Path(original['source_root']) / 'v3_rerun_tables_A1.json'
        source_family = unseal(h.read(family_path))
        source_manifest = unseal(h.read(Path(original['source_root']) / 'tables_A1_manifest.json'))
        require(file_hash(h.file(family_path)) == original['source_file_sha256']
                and digest(source_manifest) == original['source_manifest_sha256'], 'original A1 publication or manifest changed')
        info = source_family['manifest'].get('a10')
        require(info and info['constants_sha256'] == tables_a10.CONSTANTS_SHA256,
                'original A10 source constants changed')
        identities = {source_family['code_hash'], info.get('producer_code_hash'),
            source_manifest.get('code_hash') or source_manifest.get('source_family', {}).get('code_hash'),
            source_manifest.get('source_family', {}).get('code_hash', source_manifest.get('code_hash'))}
        for identity in identities:
            require(isinstance(identity, str) and bool(identity), 'original A10 source identity missing')
            if registered:
                verify_producer(h, identity)
            else:
                require(identity == code_identity(), 'rehearsal A1 source identity changed')
        source_jobs = source_manifest['jobs']
        require(digest(source_jobs) == info['job_manifest_sha256'], 'original A10 job manifest changed')
        if registered:
            require(source_jobs == tables_a10.build_jobs(info['family'], original['calibration_path']),
                    'original registered A10 job set changed')
        require(set(source_family['rows']) == tables_a10.expected_keys(source_jobs, calibration),
                'original A10 scoring rows changed')
        counts = a13.a4.counts_from_job_outputs(source_root, original['source_code_hash'])
        require((counts['M'], counts['M_FV']) == (original['M'], original['M_FV']), 'original M changed')
        rows, sensitivity, details = a13.a4.assemble_family(source_root, original['source_code_hash'], stage_root,
                                                         original['M'], original['M_FV'], {calibration['sha256']: calibration})
        ranked = {row_key(r): seal(r) for r in add_ranking_flags(list(rows.values()))}
        require(canonical(ranked) == canonical(payload['rows']) and canonical(details) == canonical(sidecar['rows'])
                and sensitivity == payload['manifest']['sensitivity_status'], 'original publication checks failed')
        rows = {k: unseal(v) for k, v in payload['rows'].items()}
        selected, tests, fits, censuses, sources, eligible = {}, {}, {}, {}, {}, {}
        old_hashes, environments = {}, []
        details_by_key = {(d['row'], d['setting']): d for d in details}
        for j in old['jobs']:
            c = j['config']
            for folder in ('records', 'outputs'):
                h.file(root / a13.PHASE / folder / (j['id'] + '.json'))
            value = completed(h.directory(root) / a13.PHASE, j, old['code_hash'])
            require(value is not None, 'A13 completion missing or changed')
            result = value['result']
            if registered:
                environments.append({k: value['runtime'][k] for k in ('python', 'numpy')})
            require(result['plan_hash'] == old['plan_hash'] and result['a1_job_id'] == c['a1_job']['id']
                    and result['code_hash'] == old['code_hash'] and result['stage'] == a13.PHASE, 'A13 result identity differs')
            replicates = a13.validate_replicates(j, result['replicates'])
            stopped = a13.stop_reached(replicates, c['eligible_rows'])
            require(result['stopped_on_visits'] == stopped and (stopped or len(replicates) == 16), 'A13 job not terminal')
            old_hashes[j['id']] = file_hash(h.file(root / a13.PHASE / 'outputs' / (j['id'] + '.json')))
            source = a13.a4._load_a1(source_root, c['a1_job'], original['source_code_hash'])
            stage_jobs = [v for v in original['jobs'] if v['config']['a1_job']['id'] == c['a1_job']['id']]
            fit = next(stages[v['id']] for v in stage_jobs if v['config']['phase'] == 'fit')
            census = next(stages[v['id']] for v in stage_jobs if v['config']['phase'] == 'census')
            vals = sorted((stages[v['id']] for v in stage_jobs if v['config']['phase'] == 'validate_plain'),
                          key=lambda v: v['replicate'])
            require(unseal(c['fit']) == fit and [v['replicate'] for v in vals] == [1, 2, 3], 'A13 fit or original validation differs')
            params = Context.build(source['result']['kernel'], calibration).parameters
            sources[c['a1_job']['id']] = c
            for key, p in c['eligible_rows'].items():
                i = p['row_index']
                ok, recomputed = a13.eligible(rows[key], details_by_key[(key, 'primary')], source['result']['rows'][i],
                        fit['rows'][i], a13.a4._combine_plain(vals, i), original['M'], params.extinction_flow, params.upper_bound)
                require(ok and dict(recomputed, row_index=i) == p, 'finding: A14 constants or A13 eligibility differ')
                selected[key] = p
                tests[key] = a13.extension_test([dict(replicate=r['replicate'], trajectories=r['rows'][key]) for r in replicates], p)
                fits[key] = fit['rows'][i]['c0']
                censuses[key] = census['cell_counts']
                eligible[key] = (tests[key].get('reason') == 'N* not reached'
                                 and tests[key]['status'] == 'unresolved'
                                 and not any(t.get('eb', t.get('status')) == 'violation'
                                             for t in details_by_key[(key, 'primary')]['cell_tests']))
        require(set(selected) == {r['row'] for r in old['eligibility'] if r['eligible']}, 'A13 eligible set differs')
        assembled, old_details = a13.reassemble(rows, details, selected, tests, fits, censuses)
        residual = sorted(k for k, row in assembled.items() if row['status'] == 'not_estimable')
        require(residual == admission['residual_rows'], 'finding: recomputed A13 residual set differs from admission')
        classification = dict(tests=tests, eligible=eligible, selected=selected, stage_hashes=old_hashes)
        require(not environments or all(e == environments[0] for e in environments), 'A13 environments differ')
        return dict(history=h, original=original, old=old, candidate=candidate, rows=rows, details=details,
                    receipt=receipt, calibration=calibration, selected=selected, tests=tests, fits=fits, censuses=censuses,
                    sources=sources, eligible=eligible, classification_sha256=digest(classification), classification=classification,
                    a13_stage_hashes=old_hashes, a13_admission_path=str(admission_path),
                    a13_admission_sha256=file_hash(h.file(admission_path)),
                    environment=environments[0] if environments else None)


REQUIRED_ROLES = {'a13_plan', 'a13_public', 'a13_root', 'a13_round', 'a13_admission',
                  'original_plan', 'original_root', 'candidate', 'original_receipt',
                  'original_sidecar', 'a1_root', 'calibration'}


def build_inventory(roles_path, checkout, copies, output):
    """Build and stage a deterministic inventory; the operator declares roles, not files."""
    from .artifacts import atomic_json, seal
    from .snapshot_a11 import normalize_historical_roots
    declaration = unseal(read(roles_path))
    roles = declaration['roles']
    require(set(roles) == REQUIRED_ROLES and isinstance(declaration.get('compatibility_records'), list),
            'history builder requires every declared role and compatibility_records')
    checkout = Path(checkout).resolve()
    roots = normalize_historical_roots(declaration['historical_roots'])
    require(str(checkout) in roots, 'A13 checkout must be a declared historical root')
    def source(path, *, directory=False):
        p = Path(path)
        require(p.is_absolute() and (p.resolve().is_relative_to(SIMULATION / 'v3')
                or any(p.resolve().is_relative_to(Path(r)) for r in roots)),
                'history source outside declared historical roots')
        require(p.is_dir() if directory else p.is_file(), 'missing required history role or input')
        return p.resolve()
    directory_roles = {'a13_root', 'original_root', 'a1_root'}
    roles = {name: str(source(value, directory=name in directory_roles)) for name, value in roles.items()}
    require(Path(roles['a13_plan']).is_relative_to(checkout), 'A13 plan is outside its execution checkout')
    copies, output = scoped(copies), scoped(output)
    require(not copies.exists() and not output.exists()
            and not {'runs', 'registered'}.intersection(p.lower() for p in copies.parts + output.parts),
            'history builder needs fresh non-registered destinations')
    require(not output.is_relative_to(copies) and not any(p.is_relative_to(Path(r))
                for p in (copies, output) for r in roots), 'inventory destinations overlap historical roots')
    old = unseal(read(roles['a13_plan']))
    original = unseal(read(roles['original_plan']))
    expected = dict(original_plan=old['original_plan_path'], original_root=old['original_run_root'],
        candidate=old['candidate_path'], original_sidecar=str(Path(old['candidate_path']).with_suffix('.cell_results.json')),
        original_receipt=str(Path(old['candidate_path']).with_suffix('.compatibility.json')),
        a13_round=old['round_record_path'], a13_admission=str(Path(old['round_record_path']).with_suffix('.admission.json')),
        a13_public=str(Path(roles['a13_plan']).with_suffix('.public.json')), a1_root=original['source_root'])
    require(all(Path(roles[k]) == Path(v).resolve() for k, v in expected.items()), 'declared history role differs from plan')
    anchor = unseal(read(roles['a13_round']))
    require(Path(anchor['root']).resolve() == Path(roles['a13_root']), 'declared A13 root differs from round record')
    paths = {Path(p) for k, p in roles.items() if k not in directory_roles}
    root = Path(roles['a13_root'])
    paths.update(root / p for p in ('identity.json', 'launches.json', a13.PHASE + '/nondeterminism_check.json'))
    check = read(root / a13.PHASE / 'nondeterminism_check.json')
    require(check['checked'] in {j['id'] for j in old['jobs']}, 'nondeterminism job is not in A13 plan')
    paths.add(root / ('_nd_' + a13.PHASE) / 'records' / (check['checked'] + '.json'))
    if 'pull_dispatch' in old:
        paths.add(root / 'pull_state.json')
    for plan, base in ((old, root), (original, Path(roles['original_root']))):
        for job in plan['jobs']:
            paths.update(base / job['config']['phase'] / folder / (job['id'] + '.json') for folder in ('outputs', 'records'))
    source_root = Path(roles['a1_root'])
    manifest_path = source_root / 'tables_A1_manifest.json'
    paths.update((manifest_path, source_root / 'v3_rerun_tables_A1.json'))
    manifest = unseal(read(manifest_path))
    for job in manifest['jobs']:
        paths.update(source_root / 'tables_A1/table' / folder / (job['id'] + '.json') for folder in ('outputs', 'records'))
    proofs = [str(source(p)) for p in declaration['compatibility_records']]
    paths.update(Path(p) for p in proofs)
    directories = {roles[name]: str(copies / name) for name in sorted(directory_roles)}
    require(not any(Path(a).is_relative_to(Path(b)) for a in directories for b in directories if a != b),
            'historical role roots overlap')
    aliases = declaration.get('aliases', {})
    require(set(aliases) <= {str(p) for p in paths}, 'alias source not required by inventory')
    files = []
    for p in sorted(paths):
        p = source(p)
        within = [r for r in directories if p.is_relative_to(Path(r))]
        target = (Path(directories[within[0]]) / p.relative_to(Path(within[0])) if within
                  else copies / 'loose' / digest(str(p)) / p.name)
        row = dict(source=str(p), copy=str(target), sha256=file_hash(p), bytes=p.stat().st_size)
        names = list(aliases.get(str(p), []))
        if p == Path(roles['calibration']):
            names += [str((SIMULATION / original['calibration_path']).resolve())]
        names = sorted(set(names) - {str(p)})
        require(all(Path(n).is_absolute() for n in names), 'history aliases must be absolute')
        if names:
            row['aliases'] = names
        files.append(row)
    document = seal(dict(schema='v3-A14-history-1', a13_plan_hash=old['plan_hash'], files=files,
        directories=directories, roles={k: roles[k] for k in ('a13_plan', 'a13_public', 'a13_root')},
        compatibility_records=proofs, historical_roots=roots))
    stage_history(document)
    History(document)
    atomic_json(output, document)
    return document


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    builder = commands.add_parser('inventory')
    for name in ('roles', 'checkout', 'copies', 'output'):
        builder.add_argument('--' + name, required=True)
    args = parser.parse_args()
    build_inventory(args.roles, args.checkout, args.copies, args.output)
    print('A14 historical inventory built and copies hash-verified.')
