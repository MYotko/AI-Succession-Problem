"""Read-only A16 historical verifier for the four stage 2 families (A16 items
1 and 7). Parallel to history_a14.py, which is unchanged.

A round's inventory copies, by hash, the original refused candidate, its
sidecar and compatibility receipt, the original Part 2 refusal record, the
source family, the validation plan and its stage records, the calibration and
the cost projection; round 2 adds round 1's plan, public record, root, round
record and admission record and the family anchor. Verification binds every
record, recomputes the original assembly and A13 item 1's eligibility, and at
round 2 recomputes round 1's classifications with the unchanged test. No prior
root is mutated and no A16 lifecycle operation is called.
"""
from copy import deepcopy
import hashlib
import os
from pathlib import Path
import shutil
import stat
import tempfile

from . import validation_extension_a13 as a13
from . import validation_extension_a16 as a16
from .artifacts import (SIMULATION, canonical, code_identity, digest, file_hash,
                        input_view, read, scoped, seal, stable_job, unseal, verify_registration)
from .history_a14 import verify_producer

SCHEMA = 'v3-A16-history-1'
ROUND1_ROLES = frozenset({'original_plan', 'original_root', 'candidate', 'original_sidecar', 'original_receipt',
                          'original_admission', 'a1_root', 'calibration', 'projection'})
ROUND2_ROLES = ROUND1_ROLES | {'round1_plan', 'round1_public', 'round1_root', 'round1_record', 'round1_admission',
                               'family_record'}
DIRECTORY_ROLES = frozenset({'original_root', 'a1_root', 'round1_root'})
require = a13.require


def finding(condition, message):
    """A substantive finding of the historical verifier (A16 item 10)."""
    if not condition:
        raise a16.Finding(message)


def _protected_anchors():
    """Every stage 2 family's target and A16 anchors, and the nominal target
    with its A13 and A14 anchors: a copy may never land on one of them."""
    return a16.protected_anchors()


def stage_history(document, view_root):
    """Copy inventoried files after reservation; verification stays read-only.

    ``view_root`` is the declared history view root, required, itself outside
    simulation/v3/runs/registered and simulation/v3/runs/a10_stage2; every copy
    destination lies under it, and none under those two trees, on a protected
    anchor or inside a historical root. The checks precede any filesystem
    operation; only path resolution runs before they pass."""
    payload = unseal(document)
    require(payload.get('schema') == SCHEMA, 'A16 staging needs an A16 history inventory')
    a16.require_family(payload['family'])
    require(view_root is not None and Path(view_root).is_absolute(), 'A16 staging needs the declared absolute history view root')
    require(all(Path(p).is_absolute() for r in payload['files'] for p in [r['source'], r['copy'], *r.get('aliases', [])]),
            'historical paths must be absolute')
    trees = a16.registered_trees()
    view = scoped(view_root)
    require(not any(view.is_relative_to(tree) for tree in trees), 'A16 history view root lies inside the registered tree')
    sources = {Path(p).resolve() for r in payload['files'] for p in [r['source'], *r.get('aliases', [])]}
    original_roots = [Path(p).resolve() for p in payload['directories']]
    protected = sources | _protected_anchors()
    destinations = [scoped(r['copy']) for r in payload['files']]
    require(len(destinations) == len(set(destinations)), 'duplicate A16 history destination')
    require(all(p.is_relative_to(view) for p in destinations), 'A16 copy destination outside the declared history view root')
    require(all(p not in protected and not any(p.is_relative_to(tree) for tree in trees)
                and not any(p.is_relative_to(root) for root in original_roots) for p in destinations),
            'A16 copy would write a historical input, a registered tree or an anchor')
    for row, target in zip(payload['files'], destinations):
        if not target.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            fd, name = tempfile.mkstemp(prefix='a16-copy-', dir=target.parent)
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
    """A sealed bijection of historical files to immutable execution copies,
    as history_a14.History, under the A16 schema with a family and a round."""
    def __init__(self, document):
        self.document = deepcopy(document)
        self.payload = unseal(self.document)
        require(self.payload.get('schema') == SCHEMA, 'invalid A16 history inventory')
        self.family = a16.require_family(self.payload['family'])
        self.round = a16.require_round(self.payload['round'])
        self.paths, self.original_paths, destinations = {}, {}, set()
        for row in self.payload['files']:
            require(all(Path(p).is_absolute() for p in [row['source'], row['copy'], *row.get('aliases', [])]),
                    'historical paths must be absolute')
            source = str(Path(row['source']).resolve())
            target = scoped(row['copy'])
            aliases = [str(Path(p).resolve()) for p in row.get('aliases', [])]
            require(source not in self.paths and not any(p in self.paths for p in aliases)
                    and str(target) not in destinations and source != str(target), 'duplicate or non-copy A16 history input')
            require(target.is_file() and target.stat().st_size == row['bytes']
                    and hashlib.sha256(target.read_bytes()).hexdigest() == row['sha256'], 'A16 historical copy changed')
            require(not target.stat().st_mode & (stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH), 'A16 historical copy must be read-only')
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
        required = ROUND2_ROLES if self.round == 2 else ROUND1_ROLES
        require(set(self.roles) == required, 'A16 history roles differ from the round')
        self.view = dict(paths=dict(self.paths), protected=sorted(set(self.directories) | {str(Path(p).parent) for p in self.paths}))
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


def _identity(h, identity, *, registered):
    if registered:
        verify_producer(h, identity)
    else:
        require(identity == code_identity(), 'rehearsal source identity changed')


def verify_history(document, *, round, registered):
    """Return verified executor-only inputs and classifications; write nothing."""
    from .production_runner import completed
    from .production_tables import row_key
    from .offline_estimator import add_ranking_flags
    from .context import Context
    from . import tables_a10
    from .calibration import validate_calibration
    cv = a13.cv
    h = History(document)
    q = a16.require_round(round)
    require(h.round == q, 'A16 history inventory was built for another round')
    family = h.family
    with input_view(h.view):
        original_plan_path = Path(h.role('original_plan'))
        original = unseal(h.read(original_plan_path))
        require(original.get('schema') == 'v3-A4-validation-1' and original.get('instrument', {}).get('mapping') == 'A10',
                'A16 original plan is not an A10 validation plan')
        require(a13.a4._recompute_plan_hash(original) == original['plan_hash'], 'original validation plan changed')
        require(original['registered'] == registered, 'A16 history registration mode differs from the original plan')
        original_root = Path(h.role('original_root'))
        candidate_path = Path(h.role('candidate'))
        require(candidate_path.resolve() == (original_root / 'candidate_unpublished_tables.json').resolve()
                and Path(h.role('original_sidecar')).resolve() == candidate_path.with_suffix('.cell_results.json').resolve()
                and Path(h.role('original_receipt')).resolve() == candidate_path.with_suffix('.compatibility.json').resolve()
                and Path(h.role('original_admission')).resolve() == (original_root / 'a13_admission_check.json').resolve()
                and Path(h.role('a1_root')).resolve() == Path(original['source_root']).resolve()
                and Path(h.role('calibration')).resolve() == (SIMULATION / original['calibration_path']).resolve(),
                'A16 history roles differ from the original run root')
        candidate = h.read(candidate_path)
        payload = unseal(candidate)
        sidecar = unseal(h.read(candidate_path.with_suffix('.cell_results.json')))
        receipt = unseal(h.read(candidate_path.with_suffix('.compatibility.json')))
        admission = unseal(h.read(h.role('original_admission')))
        require(admission.get('schema') == 'v3-A13-admission-check-1' and admission.get('scope') == 'validation_launched_under_A13'
                and admission.get('outcome') == 'refused' and admission.get('plan_hash') == original['plan_hash'],
                'A16 requires the original Part 2 refusal of this validation plan')
        require('a13_admission' not in payload['manifest'] and 'a13' not in payload['manifest'] and 'a16' not in payload['manifest'],
                'A16 starts from the original refused candidate')
        if registered:
            a13.a4.registered_publish_guard(original)
            verify_registration(original['registration'], instrument=original['instrument'], historical=True)
            require(original['calibration_path'] == a16.CALIBRATIONS[family], 'A16 family calibration string differs from the family-path clause')
        _identity(h, original['code_hash'], registered=registered)
        _identity(h, original['source_code_hash'], registered=registered)
        stage_root, source_root = h.directory(original_root), h.directory(Path(original['source_root']))
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
                    and result['a1_job_id'] == c['a1_job']['id'] and result['stream_seed'] == c['seed'], 'original stage identity differs')
            stages[j['id']] = result
            stage_hashes[j['id']], stream_seeds[j['id']] = file_hash(h.file(out_path)), c['seed']
        require(receipt['plan_hash'] == original['plan_hash'] and receipt['M'] == original['M']
                and receipt['stream_seeds'] == stream_seeds and receipt['stage_output_sha256'] == stage_hashes, 'original receipt changed')
        require(receipt['table_seal_sha256'] == candidate['sha256'] and receipt['table_file_sha256'] == file_hash(h.file(candidate_path))
                and receipt['cell_results_sha256'] == file_hash(h.file(candidate_path.with_suffix('.cell_results.json')))
                and sidecar['plan_hash'] == original['plan_hash'] and sidecar['table_seal_sha256'] == candidate['sha256'],
                'original candidate/sidecar binding changed')
        calibration = h.read(SIMULATION / original['calibration_path'])
        validate_calibration(calibration, registered=registered, instrument=original['instrument'])
        family_path = Path(original['source_root']) / 'v3_rerun_tables_A1.json'
        source_family = unseal(h.read(family_path))
        source_manifest = unseal(h.read(Path(original['source_root']) / 'tables_A1_manifest.json'))
        require(file_hash(h.file(family_path)) == original['source_file_sha256']
                and digest(source_manifest) == original['source_manifest_sha256'], 'original A1 publication or manifest changed')
        info = source_family['manifest'].get('a10')
        require(info and info['constants_sha256'] == tables_a10.CONSTANTS_SHA256, 'original A10 source constants changed')
        require(info.get('family') == family, 'A16 history family differs from the validated source family')
        identities = {source_family['code_hash'], info.get('producer_code_hash'),
                      source_manifest.get('code_hash') or source_manifest.get('source_family', {}).get('code_hash'),
                      source_manifest.get('source_family', {}).get('code_hash', source_manifest.get('code_hash'))}
        for identity in identities:
            require(isinstance(identity, str) and bool(identity), 'original A10 source identity missing')
            _identity(h, identity, registered=registered)
        source_jobs = source_manifest['jobs']
        require(digest(source_jobs) == info['job_manifest_sha256'], 'original A10 job manifest changed')
        if registered:
            require(source_jobs == tables_a10.build_jobs(family, original['calibration_path']), 'original registered A10 job set changed')
        require(set(source_family['rows']) == tables_a10.expected_keys(source_jobs, calibration), 'original A10 scoring rows changed')
        counts = a13.a4.counts_from_job_outputs(source_root, original['source_code_hash'])
        require((counts['M'], counts['M_FV']) == (original['M'], original['M_FV']), 'original M changed')
        rows, sensitivity, details = a13.a4.assemble_family(source_root, original['source_code_hash'], stage_root,
                                                         original['M'], original['M_FV'], {calibration['sha256']: calibration})
        ranked = {row_key(r): seal(r) for r in add_ranking_flags(list(rows.values()))}
        require(canonical(ranked) == canonical(payload['rows']) and canonical(details) == canonical(sidecar['rows'])
                and sensitivity == payload['manifest']['sensitivity_status'], 'original publication checks failed')
        rows = {k: unseal(v) for k, v in payload['rows'].items()}
        details_by_key = {(d['row'], d['setting']): d for d in details}
        count = (original['settings_override']['groups'] * original['settings_override']['runs_per_group']
                 if original.get('settings_override') else cv.GROUPS * cv.PLAIN_RUNS_PER_GROUP)
        selected, fits, censuses, sources, visits, row_settings, P = {}, {}, {}, {}, {}, [], 0
        for j in source_jobs:
            source = a13.a4._load_a1(source_root, j, original['source_code_hash'])
            setting = j['config'].get('setting_name', 'primary')
            plain = source['result']['route'] == 'plain'
            if setting == 'primary' and plain:
                P += len(source['result']['rows'])
            stage_jobs = [v for v in original['jobs'] if v['config']['a1_job']['id'] == j['id']]
            fit = next((stages[v['id']] for v in stage_jobs if v['config']['phase'] == 'fit'), None)
            census = next(stages[v['id']] for v in stage_jobs if v['config']['phase'] == 'census')
            vals = sorted((stages[v['id']] for v in stage_jobs if v['config']['phase'] == 'validate_plain'), key=lambda v: v['replicate'])
            if plain:
                require(fit is not None and [v['replicate'] for v in vals] == [1, 2, 3], 'original plain replicates missing')
            params = Context.build(source['result']['kernel'], calibration).parameters
            for i, a1_row in enumerate(source['result']['rows']):
                key = row_key(a1_row)
                row_settings.append((key, setting))
                if not (plain and setting == 'primary'):
                    continue
                cells = a13.a4._combine_plain(vals, i)
                ok, p = a13.eligible(rows[key], details_by_key[(key, 'primary')], a1_row, fit['rows'][i], cells,
                                     original['M'], params.extinction_flow, params.upper_bound)
                if not ok:
                    continue
                selected[key] = dict(p, row_index=i)
                fits[key] = fit['rows'][i]['c0']
                censuses[key] = census['cell_counts']
                visits[key] = dict(original_visits=int(cells.get(cv.POP0_CELL, {}).get('n_traj', 0)),
                                   original_trajectories=3 * count, round1_visits=None, round1_trajectories=None)
                entry = sources.setdefault(j['id'], dict(route='plain', a1_source_root=original['source_root'], a1_job=j,
                                                         a1_source_code_hash=original['source_code_hash'], fit=seal(fit),
                                                         trajectory_count=count, eligible_rows={}))
                entry['eligible_rows'][key] = dict(p, row_index=i)
                if original.get('settings_override'):
                    entry['settings_override'] = original['settings_override']
        E = len(selected)
        require(0 <= E <= P <= original['M'], 'invalid A16 error-accounting counts')
        tests, eligible, round1, round1_stage_hashes = {}, {k: True for k in selected}, None, {}
        if q == 2:
            r1_path = Path(h.role('round1_plan'))
            r1 = unseal(h.read(r1_path))
            require(r1.get('schema') == a16.SCHEMA and r1.get('round') == 1 and r1.get('a16_family') == family
                    and a16.plan_hash(r1) == r1['plan_hash'], 'A16 round-1 plan changed')
            require(r1['registered'] == registered and r1['original_plan_hash'] == original['plan_hash']
                    and r1['original_hashes']['candidate_file_sha256'] == receipt['table_file_sha256']
                    and r1['original_hashes']['sidecar_file_sha256'] == receipt['cell_results_sha256']
                    and r1['original_hashes']['admission_record_sha256'] == file_hash(h.file(h.role('original_admission')))
                    and r1['original_hashes']['plan_file_sha256'] == file_hash(h.file(original_plan_path)),
                    'A16 round-1 plan binds other original records')
            require(r1['M'] == original['M'] and r1['P'] == P and r1['E'] == E and r1['alpha'] == cv.ALPHA, 'A16 round-1 counts differ')
            require(r1['jobs'] == [stable_job(a16.KINDS[1], dict(c, plan_hash=r1['plan_hash']), 'v3_tables', i)
                                   for i, c in enumerate(r1['job_skeletons'])], 'A16 round-1 job skeleton changed')
            require(r1['seed_check'] == a16.check_seed_manifest(r1['seed_manifest'], r1['forbidden_seeds'], family=family, q=1,
                                                                rehearsal=r1['non_registered_rehearsal'], recorded=r1['recorded_a16_seeds']),
                    'A16 round-1 seed check changed')
            if registered:
                verify_registration(r1['registration'], instrument=r1['instrument'], historical=True)
            _identity(h, r1['code_hash'], registered=registered)
            require(unseal(h.read(h.role('round1_public'))) == a16.public_record(r1), 'A16 round-1 public record differs from plan')
            record = unseal(h.read(h.role('round1_record')))
            require(record.get('schema') == 'v3-A16-round-1' and record['family'] == family and record['round'] == 1
                    and record['plan_hash'] == r1['plan_hash'] and record['spec_hash'] == digest(r1) and record['halt'] is None
                    and record['admission'] == 'refused' and record['state'] == 'refused_admission',
                    'A16 round 1 did not complete normally with a Part 2 refusal')
            r1_root = Path(h.role('round1_root'))
            require(Path(record['root']).resolve() == r1_root.resolve(), 'A16 round-1 root differs from its record')
            r1_admission = unseal(h.read(h.role('round1_admission')))
            require(r1_admission.get('scope') == a16.SCOPES[1] and r1_admission.get('outcome') == 'refused'
                    and r1_admission.get('plan_hash') == r1['plan_hash'] and r1_admission.get('family') == family,
                    'A16 round-1 admission was not refused for this plan')
            require(isinstance(r1_admission.get('classifications'), list)
                    and r1_admission.get('classifications_sha256') == digest(r1_admission['classifications']),
                    'A16 round-1 admission record lacks its bound per-row classifications')
            family_record = unseal(h.read(h.role('family_record')))
            require(family_record.get('schema') == 'v3-A16-family-1' and family_record['family'] == family
                    and family_record['original'] == r1['original_hashes'] and family_record['terminal'] is None
                    and family_record.get('published_round') is None, 'A16 family anchor is terminal, published or another realization')
            require(h.read(r1_root / 'identity.json') == dict(code_hash=r1['code_hash'], spec_hash=digest(r1)), 'A16 round-1 root identity differs')
            launches = h.read(r1_root / 'launches.json')
            require(launches and launches[-1].get('complete') is True, 'A16 round-1 last launch incomplete')
            check = h.read(r1_root / a16.PHASES[1] / 'nondeterminism_check.json')
            jobs = {j['id']: j for j in r1['jobs']}
            require(check.get('matched') is True and check.get('checked') in jobs, 'A16 round-1 nondeterminism check missing')
            nd = h.read(r1_root / ('_nd_' + a16.PHASES[1]) / 'records' / (check['checked'] + '.json'))
            require(nd['status'] == 'complete' and nd['code_hash'] == r1['code_hash'] and nd['job'] == jobs[check['checked']],
                    'A16 round-1 nondeterminism completion differs')
            for j in r1['jobs']:
                c = j['config']
                for folder in ('records', 'outputs'):
                    h.file(r1_root / a16.PHASES[1] / folder / (j['id'] + '.json'))
                value = completed(h.directory(r1_root) / a16.PHASES[1], j, r1['code_hash'])
                require(value is not None, 'A16 round-1 completion missing or changed')
                result = value['result']
                require(result['plan_hash'] == r1['plan_hash'] and result['a1_job_id'] == c['a1_job']['id']
                        and result['code_hash'] == r1['code_hash'] and result['stage'] == a16.PHASES[1]
                        and result.get('a16_family') == family and result.get('a16_round') == 1, 'A16 round-1 result identity differs')
                replicates = a16.validate_replicates(j, result['replicates'])
                stopped = a16.stop_reached(replicates, c['eligible_rows'])
                require(result['stopped_on_visits'] == stopped and (stopped or len(replicates) == c['R_max']), 'A16 round-1 job not terminal')
                round1_stage_hashes[j['id']] = file_hash(h.file(r1_root / a16.PHASES[1] / 'outputs' / (j['id'] + '.json')))
                require(unseal(c['fit']) == unseal(sources[c['a1_job']['id']]['fit']), 'A16 round-1 fit differs from the original')
                for key, p in c['eligible_rows'].items():
                    finding(key in selected and p == selected[key], 'finding: A16 round-2 constants or eligibility differ from round 1')
                    tests[key] = a16.extension_test([dict(replicate=r['replicate'], trajectories=r['rows'][key]) for r in replicates], p, 1)
                    visits[key].update(round1_visits=sum(pair[1] > 0 for r in replicates for pair in r['rows'][key]),
                                       round1_trajectories=len(replicates) * c['trajectory_count'])
            require(set(tests) == set(selected) == {r['row'] for r in r1['eligibility'] if r['eligible']}, 'A16 round-1 eligible set differs')
            # A16 item 7: round 1's classifications, recomputed with the unchanged
            # test through the unchanged re-assembly, equal the sealed round-1
            # admission evidence row by row (key, decision, test status,
            # safeguard, round), not merely in aggregate.
            assembled, _ = a13.reassemble(rows, details, selected, tests, fits, censuses)
            recomputed = [a16.classification_entry(k, assembled[k]['status'], assembled[k]['a13']['certified_by_extension'], tests[k],
                                                   1 if tests[k].get('reason') != 'N* not reached' else None) for k in sorted(selected)]
            finding(recomputed == r1_admission['classifications'],
                    'finding: recomputed round-1 classification differs from the sealed admission record')
            residual = sorted(k for k, row in assembled.items() if row['status'] == 'not_estimable')
            finding(residual == r1_admission['residual_rows'], 'finding: recomputed round-1 residual set differs from admission')
            eligible = {k: (tests[k].get('reason') == 'N* not reached' and tests[k]['status'] == 'unresolved'
                            and not any(t.get('eb', t.get('status')) == 'violation' for t in details_by_key[(k, 'primary')]['cell_tests']))
                        for k in selected}
            sources = {j['config']['a1_job']['id']: deepcopy(j['config']) for j in r1['jobs']}
            round1 = dict(plan_hash=r1['plan_hash'], public_file_sha256=file_hash(h.file(h.role('round1_public'))),
                          stage_output_sha256=round1_stage_hashes, seed_manifest=r1['seed_manifest'],
                          forbidden_seeds=r1['forbidden_seeds'], admission_record_sha256=file_hash(h.file(h.role('round1_admission'))),
                          classifications_sha256=r1_admission['classifications_sha256'],
                          tested_rows=sorted(c['row'] for c in r1_admission['classifications'] if c['round'] == 1),
                          tests=sum(t.get('reason') != 'N* not reached' for t in tests.values()))
        classification = dict(family=family, round=q, tests=tests, eligible=eligible, selected=selected,
                              stage_hashes=round1_stage_hashes)
        return dict(history=h, family=family, round=q, original=original, original_plan_path=str(original_plan_path),
                    candidate=candidate, rows=rows, details=details, receipt=receipt, calibration=calibration,
                    selected=selected, tests=tests, fits=fits, censuses=censuses, sources=sources, eligible=eligible,
                    visits=visits, E=E, P=P, alpha=cv.ALPHA, row_settings=row_settings, source_jobs=source_jobs,
                    classification=classification, classification_sha256=digest(classification), round1=round1,
                    original_admission_sha256=file_hash(h.file(h.role('original_admission'))))


def build_inventory(roles_path, copies, output, *, round):
    """Build and stage a deterministic inventory; the operator declares roles, not files."""
    from .artifacts import atomic_json
    from .snapshot_a11 import normalize_historical_roots
    q = a16.require_round(round)
    declaration = unseal(read(roles_path))
    roles = declaration['roles']
    required = ROUND2_ROLES if q == 2 else ROUND1_ROLES
    require(set(roles) == required and isinstance(declaration.get('compatibility_records'), list),
            'A16 history builder requires every declared role for the round and compatibility_records')
    roots = normalize_historical_roots(declaration['historical_roots'])

    def source(path, *, directory=False):
        p = Path(path)
        require(p.is_absolute() and (p.resolve().is_relative_to(SIMULATION / 'v3')
                or any(p.resolve().is_relative_to(Path(r)) for r in roots)), 'history source outside declared historical roots')
        require(p.is_dir() if directory else p.is_file(), 'missing required history role or input')
        return p.resolve()
    roles = {name: str(source(value, directory=name in DIRECTORY_ROLES)) for name, value in roles.items()}
    copies, output = scoped(copies), scoped(output)
    require(not copies.exists() and not output.exists()
            and not {'runs', 'registered', 'a10_stage2'}.intersection(p.lower() for p in copies.parts + output.parts),
            'history builder needs fresh non-registered destinations')
    require(not output.is_relative_to(copies) and not any(p.is_relative_to(Path(r)) for p in (copies, output) for r in roots),
            'inventory destinations overlap historical roots')
    original = unseal(read(roles['original_plan']))
    original_root = Path(roles['original_root'])
    candidate = original_root / 'candidate_unpublished_tables.json'
    expected = dict(candidate=candidate, original_sidecar=candidate.with_suffix('.cell_results.json'),
                    original_receipt=candidate.with_suffix('.compatibility.json'),
                    original_admission=original_root / 'a13_admission_check.json', a1_root=original['source_root'],
                    calibration=SIMULATION / original['calibration_path'])
    require(all(Path(roles[k]) == Path(v).resolve() for k, v in expected.items()), 'declared history role differs from the original plan')
    source_root = Path(roles['a1_root'])
    source_family = unseal(read(source_root / 'v3_rerun_tables_A1.json'))
    family = a16.require_family(source_family['manifest']['a10']['family'])
    paths = {Path(p) for k, p in roles.items() if k not in DIRECTORY_ROLES}
    for job in original['jobs']:
        paths.update(original_root / job['config']['phase'] / folder / (job['id'] + '.json') for folder in ('outputs', 'records'))
    manifest_path = source_root / 'tables_A1_manifest.json'
    paths.update((manifest_path, source_root / 'v3_rerun_tables_A1.json'))
    for job in unseal(read(manifest_path))['jobs']:
        paths.update(source_root / 'tables_A1/table' / folder / (job['id'] + '.json') for folder in ('outputs', 'records'))
    if family in a16.SIGMA_FAMILIES:
        # The variant calibration's validation reads the frozen nominal parent
        # (calibration._validate_a10_variant): it is part of the closure.
        paths.add(SIMULATION / a16.NOMINAL_CALIBRATION)
    if q == 2:
        r1 = unseal(read(roles['round1_plan']))
        require(r1.get('schema') == a16.SCHEMA and r1.get('round') == 1 and r1.get('a16_family') == family, 'round1_plan is not this family\'s A16 round-1 plan')
        r1_root = Path(roles['round1_root'])
        require(Path(roles['round1_public']) == Path(roles['round1_plan']).with_suffix('.public.json')
                and Path(roles['round1_record']) == Path(r1['round_record_path']).resolve()
                and Path(roles['round1_admission']) == Path(r1['admission_record_path']).resolve()
                and Path(roles['family_record']) == Path(r1['family_record_path']).resolve(), 'declared round-1 roles differ from the round-1 plan')
        record = unseal(read(roles['round1_record']))
        require(Path(record['root']).resolve() == r1_root, 'declared round-1 root differs from its record')
        paths.update(r1_root / p for p in ('identity.json', 'launches.json', a16.PHASES[1] + '/nondeterminism_check.json'))
        check = read(r1_root / a16.PHASES[1] / 'nondeterminism_check.json')
        require(check['checked'] in {j['id'] for j in r1['jobs']}, 'nondeterminism job is not in the round-1 plan')
        paths.add(r1_root / ('_nd_' + a16.PHASES[1]) / 'records' / (check['checked'] + '.json'))
        for job in r1['jobs']:
            paths.update(r1_root / a16.PHASES[1] / folder / (job['id'] + '.json') for folder in ('outputs', 'records'))
    proofs = [str(source(p)) for p in declaration['compatibility_records']]
    paths.update(Path(p) for p in proofs)
    directories = {roles[name]: str(copies / name) for name in sorted(DIRECTORY_ROLES & set(roles))}
    require(not any(Path(a).is_relative_to(Path(b)) for a in directories for b in directories if a != b), 'historical role roots overlap')
    aliases = declaration.get('aliases', {})
    require(set(aliases) <= {str(p) for p in paths}, 'alias source not required by inventory')
    files = []
    for p in sorted(paths):
        p = source(p)
        within = [r for r in directories if p.is_relative_to(Path(r))]
        target = (Path(directories[within[0]]) / p.relative_to(Path(within[0])) if within else copies / 'loose' / digest(str(p)) / p.name)
        row = dict(source=str(p), copy=str(target), sha256=file_hash(p), bytes=p.stat().st_size)
        names = list(aliases.get(str(p), []))
        if p == Path(roles['calibration']):
            names += [str((SIMULATION / original['calibration_path']).resolve())]
        if p == (SIMULATION / a16.NOMINAL_CALIBRATION).resolve():
            names += [str((SIMULATION / a16.NOMINAL_CALIBRATION).resolve())]
        names = sorted(set(names) - {str(p)})
        require(all(Path(n).is_absolute() for n in names), 'history aliases must be absolute')
        if names:
            row['aliases'] = names
        files.append(row)
    document = seal(dict(schema=SCHEMA, family=family, round=q, original_plan_hash=original['plan_hash'],
                         instrument=original.get('instrument'), files=files, directories=directories, roles=roles,
                         compatibility_records=proofs, historical_roots=roots, view_root=str(copies)))
    stage_history(document, copies)
    History(document)
    atomic_json(output, document)
    return document


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    builder = commands.add_parser('inventory')
    for name in ('roles', 'copies', 'output'):
        builder.add_argument('--' + name, required=True)
    builder.add_argument('--round', type=int, choices=a16.ROUNDS, required=True)
    args = parser.parse_args()
    build_inventory(args.roles, args.copies, args.output, round=args.round)
    print('A16 historical inventory built and copies hash-verified.')
