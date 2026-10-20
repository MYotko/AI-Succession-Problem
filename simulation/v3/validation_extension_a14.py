"""A14's second and final round. A13's implementation remains immutable."""
from contextlib import contextmanager
from contextvars import ContextVar
from copy import deepcopy
import math
from pathlib import Path
import time

from . import validation_extension_a13 as a13
from .artifacts import (SIMULATION, atomic_json, canonical, code_identity, digest,
                        file_hash, input_view, lease, read, scoped, seal, stable_job, unseal)
from .continuation_validation import _truncated_sha

SCHEMA = 'v3-A14-extension-1'
PHASE = 'validate_plain_ext2'
KIND = 'a14_validate_plain_ext2'
RESERVED = (1 << 61, 1 << 62)
TARGET = a13.TARGET
APPROVED_A13_PLAN = 'e30c465ff93d476ef70e1f5573179ad0b616cb724881d1bab73ae05a9af25a62'
ScientificHalt = a13.ScientificHalt
require = a13.require
stop_reached = a13.stop_reached
extension_stage = a13.extension_stage
_checkpoint_context = ContextVar('a14_checkpoint_context', default=None)
_launch_view = ContextVar('a14_launch_view', default=False)


def ext2_seed(source_seed, replicate):
    require(type(replicate) is int and 20 <= replicate <= 51, 'A14 replicate outside 20..51')
    return RESERVED[0] + _truncated_sha('v3_R_validate_ext2', source_seed, '/', replicate)


def rehearsal_seed(source_seed, replicate):
    return (1 << 128) | int(digest(['A14-rehearsal', source_seed, replicate])[:32], 16)


def reserved(seed):
    return a13.RESERVED[0] <= seed < a13.RESERVED[1] or RESERVED[0] <= seed < RESERVED[1]


def check_seed_manifest(manifest, forbidden, *, rehearsal=False):
    seeds = [r['seed'] for r in manifest]
    require(all(type(s) is int and s >= 0 for s in seeds), 'invalid A14 seed')
    require(len(set(seeds)) == len(seeds) and not set(seeds).intersection(forbidden), 'A14 global seed collision')
    require(all(not reserved(s) if rehearsal else RESERVED[0] <= s < RESERVED[0] + (1 << 60)
                for s in seeds), 'A14 seed range mismatch')
    return dict(pairwise_distinct=True, global_collision=False, seeds=len(seeds), reserved_range=list(RESERVED))


def seed_manifest(sources, r_max, forbidden, *, rehearsal=False):
    require(type(r_max) is int and 0 <= r_max <= 32, 'invalid A14 replicate bound')
    seed = rehearsal_seed if rehearsal else ext2_seed
    result = [dict(source_job_id=j['id'], replicate=r, seed=seed(j['seed'], r))
              for j in sorted(sources, key=lambda j: j['id']) for r in range(20, 20 + r_max)]
    check_seed_manifest(result, forbidden, rehearsal=rehearsal)
    return result


def price_round(original, projection, sources, *, registered, projection_file_hash):
    # A13 performs the payload seal and registered file-identity checks first.
    price = a13.price_extension(original, projection, sources, registered=registered,
                                 projection_file_hash=projection_file_hash)
    per_replicate = math.fsum(v['replicate_x2_hours'] for v in price['prices'].values())
    r_max = max((r for r in range(33) if r * per_replicate <= 15), default=0)
    return dict(price, R_max=r_max, projected_x2_hours=r_max * per_replicate)


def extension_test(records, parameters):
    require([r['replicate'] for r in records] == list(range(20, 20 + len(records))),
            'A14 replicate order or gap')
    # Only the ordinal metadata is adapted. The numerical primitive sees the
    # identical ordered pairs and exactly the same constants.
    return a13.extension_test([dict(r, replicate=r['replicate'] - 16) for r in records], parameters)


def validate_replicates(job, replicates):
    c = job['config']
    require(len(replicates) <= c['R_max'], 'too many A14 replicates')
    prior = []
    for index, r in enumerate(replicates):
        require(not prior or not stop_reached(prior, c['eligible_rows']), 'A14 continued past stop')
        require(r['replicate'] == index + 20 and r['seed'] == c['stream_seeds'][index],
                'A14 checkpoint seed/order mismatch')
        require(set(r['rows']) == set(c['eligible_rows']), 'A14 checkpoint row mismatch')
        require(r['count'] == c['trajectory_count'], 'A14 trajectory count mismatch')
        for pairs in r['rows'].values():
            require(len(pairs) == r['count'] and all(len(p) == 2 and math.isfinite(p[0])
                    and type(p[1]) is int and p[1] >= 0 and (p[1] > 0 or p[0] == 0) for p in pairs),
                    'invalid A14 ordered trajectory records')
        prior.append(r)
    return prior


@contextmanager
def checkpoint_context(directory, initial=(), *, recheck=False):
    token = _checkpoint_context.set((Path(directory), deepcopy(list(initial)), recheck))
    try:
        yield
    finally:
        _checkpoint_context.reset(token)


def durable_checkpoints(root, job):
    values = []
    for path in sorted((Path(root) / PHASE / 'a14_checkpoints' / job['id']).glob('*.json')):
        value = unseal(read(path))
        require(value['job_sha256'] == digest(job), 'A14 checkpoint job changed')
        values.append(value['replicate'])
    return validate_replicates(job, values)


def accept_checkpoint(coordinator, request):
    coordinator.session(request)
    l = coordinator.state['leases'].get(request['lease'])
    require(l and l['host'] == request['host'] and l['session'] == request['session'], 'wrong A14 checkpoint lease')
    job = coordinator.jobs[l['job_id']]
    require(job['kind'] == KIND and l['purpose'] == 'work' and not coordinator.state['halt'], 'A14 checkpoint not allowed')
    payload = unseal(request['checkpoint'])
    require(payload['job_sha256'] == digest(job), 'A14 checkpoint job hash changed')
    values = durable_checkpoints(coordinator.root, job)
    replica = payload['replicate']
    index = replica['replicate'] - 20
    if 0 <= index < len(values):
        if canonical(replica) != canonical(values[index]):
            coordinator.state['halt'] = 'A14 replicate nondeterminism'
            latch_round_halt(coordinator.root, coordinator.state['halt'])
            raise ScientificHalt('A14 checkpoint mismatch')
        return {'accepted': True}
    require(index == len(values), 'A14 checkpoint replicate gap')
    validate_replicates(job, values + [replica])
    atomic_json(coordinator.root / PHASE / 'a14_checkpoints' / job['id'] / f'{replica["replicate"]:02d}.json',
                request['checkpoint'])
    return {'accepted': True}


@contextmanager
def execution_inputs(jobs):
    """Use only the declared A1/calibration copies, including transferred aliases."""
    from .artifacts import _INPUT_VIEW, input_path
    outer = _INPUT_VIEW.get() or dict(paths={}, protected=[])
    paths, protected = dict(outer['paths']), list(outer['protected'])
    for job in jobs:
        for row in job['config'].get('a14_inputs', []):
            target = Path(input_path(row['copy']))
            require(file_hash(target) == row['sha256'] and target.stat().st_size == row['bytes'],
                    'A14 execution input changed')
            source = str(Path(row['source']).resolve())
            paths[source] = str(target)
            paths[str(Path(row['copy']).resolve())] = str(target)
            paths[str(target)] = str(target)
            protected.append(str(Path(source).parent))
    with input_view(dict(paths=paths, protected=sorted(set(protected)))):
        yield


def run_stage_job(job, root):
    with execution_inputs([job]):
        return _run_stage_job(job, root)


def _run_stage_job(job, root):
    c = job['config']
    configuration = job['tag'] in ('configuration', 'validation') and c.get('configuration_test')
    require(c['phase'] == PHASE and c['M'] > 0, 'invalid A14 phase or M')
    require(all(p['M'] == c['M'] for p in c['eligible_rows'].values()), 'A14 row M differs')
    seeds = [c['seed']] if configuration else c['stream_seeds']
    if configuration:
        require(not reserved(c['seed']), 'A14 configuration uses reserved seed')
    else:
        seed = rehearsal_seed if c.get('non_registered_rehearsal') else ext2_seed
        require(24 <= c['R_max'] <= 32, 'A14 no-launch floor or upper bound')
        require(seeds == [seed(c['a1_job']['seed'], r) for r in range(20, 20 + c['R_max'])], 'A14 seeds changed')
        check_seed_manifest(c['full_seed_manifest'], c['forbidden_seeds'], rehearsal=c.get('non_registered_rehearsal', False))
    source = a13.a4._load_a1(c['a1_source_root'], c['a1_job'], c['a1_source_code_hash'])
    fit = unseal(c['fit'])
    require(fit['a1_job_id'] == c['a1_job']['id'], 'A14 fit source mismatch')
    local = _checkpoint_context.get()
    directory = Path(root) / 'a14_checkpoints' / job['id'] if local is None else local[0]
    prior = [] if local is None else deepcopy(local[1])
    recheck = local is not None and local[2]
    if local is None and not configuration:
        for path in sorted(directory.glob('*.json')):
            value = unseal(read(path))
            require(value['job_sha256'] == digest(job), 'A14 checkpoint job mismatch')
            prior.append(value['replicate'])
    if configuration or recheck:
        prior = []
    if not configuration:
        validate_replicates(job, prior)
    for index, seed in enumerate(seeds):
        if index < len(prior):
            continue
        if prior and stop_reached(prior, c['eligible_rows']):
            break
        value = extension_stage(source, fit, c['eligible_rows'], seed, c.get('settings_override'))
        value.update(replicate=index + 20, seed=seed)
        prior.append(value)
        if not configuration and not recheck:
            atomic_json(directory / f'{index + 20:02d}.json', seal(dict(job_sha256=digest(job), replicate=value)))
    return dict(stage=PHASE, plan_hash=c['plan_hash'], a1_job_id=c['a1_job']['id'],
                code_hash=code_identity(), replicates=prior,
                stopped_on_visits=bool(prior and stop_reached(prior, c['eligible_rows'])))


def round_record_path(plan):
    path = scoped(plan['round_record_path'])
    if plan['registered']:
        require(path == scoped(SIMULATION / TARGET).with_suffix('.a14_round.json'), 'A14 family anchor moved')
    return path


def preparation_request(output, history_document, *, registered):
    output = scoped(output)
    path = scoped(SIMULATION / TARGET).with_suffix('.a14_round.json') if registered else output.with_suffix('.round.json')
    # This is an asserted binding, not a grant based on unverified history.
    request = dict(family=TARGET, approved_a13_plan=APPROVED_A13_PLAN if registered else
                   history_document.get('payload', {}).get('a13_plan_hash'),
                   history_reference_sha256=digest(history_document), output=str(output), code_hash=code_identity())
    return path, request


def validate_preparation_invocation(output, reference, inputs, *, registration, rehearsal, resume, wall_hours=16., overhead_hours=1.):
    """Read invocation metadata only; never create or modify a record."""
    require(math.isfinite(wall_hours) and wall_hours > 0 and math.isfinite(overhead_hours) and overhead_hours >= 0,
            'invalid A14 allowance')
    registered = registration is not None
    require(registered != bool(rehearsal), 'A14 requires exactly one of registered or rehearsal')
    output = scoped(output)
    path, request = preparation_request(output, reference, registered=registered)
    if resume:
        require(path.is_file(), 'A14 preparation resume needs an existing anchor')
        previous = unseal(read(path))
        require(previous.get('schema') == SCHEMA + '-round' and previous.get('request') == request
                and previous.get('state') == 'preparing' and previous.get('halt') is None,
                'A14 preparation resume anchor is inconsistent or terminal')
        if output.exists():
            require(output.is_file(), 'A14 preparation output is not a regular file')
            plan = unseal(read(output))
            require(previous.get('plan_hash') is not None
                    and plan.get('plan_hash') == previous['plan_hash'] == plan_hash(plan),
                    'A14 preparation output does not match its anchor')
    else:
        require(not output.exists(), 'A14 plan already frozen')
        require(not path.exists(), 'A14 preparation already reserved or terminal')
    from .artifacts import verify_registration
    if registered:
        verify_registration(registration, instrument={'mapping': 'A10', 'k_star': 1.8, 'g': 'linear'})
    for name, value in inputs.items():
        require(Path(value).is_file(), 'A14 input must exist and be a regular file: ' + name)
    projection = read(inputs['projection'])
    unseal(projection)
    projection_hash = file_hash(inputs['projection'])
    if registered:
        require(projection_hash == a13.PROJECTION_FILE_SHA256 and projection['sha256'] == a13.PROJECTION_SEAL,
                'A14 registered projection identity mismatch')
    inventory = unseal(read(inputs['seed_inventory']))
    categories = {'registered', 'planning', 'probe', 'rehearsal', 'qualification',
                  'a13_qualification_seeds', 'a13_configuration_seeds'}
    require(set(inventory) == categories and all(isinstance(v, list) and all(type(x) is int and x >= 0 for x in v)
                for v in inventory.values()), 'A14 global seed inventory is incomplete or invalid')
    from .forecast_a14 import validate_configuration
    forecast = validate_configuration(inputs['forecast_configuration'], registered=registered)
    return dict(projection=projection, projection_file_hash=projection_hash, inventory=inventory,
                inventory_file_hash=file_hash(inputs['seed_inventory']), forecast=forecast)


def reserve_preparation(output, history_document, *, registered, resume=False):
    """Exclusive preliminary record, before any evidence verification."""
    path, request = preparation_request(output, history_document, registered=registered)
    with lease(path.with_suffix('.lock')):
        if path.exists():
            previous = unseal(read(path))
            require(resume and previous.get('request') == request and previous.get('state') == 'preparing'
                    and previous.get('halt') is None, 'A14 preparation already reserved or terminal')
            return path
        require(not resume, 'A14 preparation resume needs an existing anchor')
        atomic_json(path, seal(dict(schema=SCHEMA + '-round', request=request, plan_hash=None,
                    spec_hash=None, root=None, halt=None, state='preparing', created_epoch=time.time())))
    return path


def preparation_failure(path, reason):
    with lease(path.with_suffix('.lock')):
        value = unseal(read(path))
        require(value.get('schema') == SCHEMA + '-round', 'not an A14 round record')
        failure = dict(reason=reason, epoch=time.time())
        if value.get('halt') is None:
            value.update(state='refused', halt=failure)
        else:
            value.setdefault('later_failures', []).append(failure)
        atomic_json(path, seal(value))


def plan_hash(plan):
    return digest({k: v for k, v in plan.items()
                   if k not in ('plan_hash', 'jobs', 'configuration', 'pull_dispatch')})


def validate_plan(plan, *, launching=False):
    require(plan.get('schema') == SCHEMA and plan.get('round') == 2, 'invalid A14 plan')
    require(plan['registered'] != bool(plan['non_registered_rehearsal']), 'A14 requires registered XOR rehearsal')
    require(not (plan['registered'] and 'pull_dispatch' in plan), 'registered A14 requires single-host dispatch')
    require(plan['code_hash'] == code_identity() and plan_hash(plan) == plan['plan_hash'], 'A14 plan or source changed')
    round_record_path(plan)
    require(plan['R_max'] == plan['pricing']['R_max'] and 24 <= plan['R_max'] <= 32, 'A14 launch floor or bound')
    check_seed_manifest(plan['seed_manifest'], plan['forbidden_seeds'], rehearsal=plan['non_registered_rehearsal'])
    expected = [stable_job(KIND, dict(c, plan_hash=plan['plan_hash']), 'v3_tables', i)
                for i, c in enumerate(plan['job_skeletons'])]
    require(plan['jobs'] == expected, 'A14 jobs changed')
    for j in plan['jobs']:
        c = j['config']
        require(c['M'] == plan['M'] and c['full_seed_manifest'] == plan['seed_manifest'], 'A14 constants/manifest changed')
    if launching:
        require(plan['launch_allowed'], 'A14 launch not authorized')
        from .history_a14 import verify_history
        historical = verify_history(plan['history'], registered=plan['registered'])
        require(historical['classification_sha256'] == plan['classification_sha256'], 'A14 historical classification changed')


def begin_round(plan, plan_path, root):
    validate_plan(plan, launching=True)
    require(unseal(read(plan_path)) == plan, 'A14 launch plan changed')
    root, path = scoped(root), round_record_path(plan)
    with lease(path.with_suffix('.lock')):
        value = unseal(read(path))
        require(value.get('schema') == SCHEMA + '-round' and value['plan_hash'] == plan['plan_hash'] and value['halt'] is None
                and value['state'] in ('prepared', 'launched'), 'A14 round spent or different plan')
        require(value['root'] in (None, str(root)) and value['spec_hash'] in (None, digest(plan)), 'A14 different root/specification')
        value.update(root=str(root), spec_hash=digest(plan), state='launched')
        atomic_json(path, seal(value))
        atomic_json(root / 'a14_round.json', seal(dict(record_path=str(path), plan_hash=plan['plan_hash'], spec_hash=digest(plan))))
    round_halt(root)
    require(unseal(read(path))['halt'] is None, 'A14 round has a latched halt')


def latch_round_halt(root, reason):
    root = scoped(root)
    pointer = root / 'a14_round.json'
    require(pointer.exists(), 'A14 halt lacks a bound round')
    ref = unseal(read(pointer))
    path = scoped(ref['record_path'])
    with lease(path.with_suffix('.lock')):
        value = unseal(read(path))
        require(value.get('schema') == SCHEMA + '-round' and value['plan_hash'] == ref['plan_hash'] and value['spec_hash'] == ref['spec_hash']
                and value['root'] == str(root), 'A14 halt binding mismatch')
        if value['halt'] is None:
            value.update(halt=dict(reason=reason, epoch=time.time()), state='halted')
            atomic_json(path, seal(value))


def round_halt(root):
    root = scoped(root)
    for path in (root / 'a14_scientific_halt.json', root / 'nondeterminism_failure.json',
                 root / PHASE / 'nondeterminism_failure.json'):
        if path.exists():
            latch_round_halt(root, path.name)
    return unseal(read(scoped(unseal(read(root / 'a14_round.json'))['record_path'])))['halt']


def publication_round(plan, root):
    root = scoped(root)
    value = unseal(read(round_record_path(plan)))
    require(value.get('schema') == SCHEMA + '-round' and value['plan_hash'] == plan['plan_hash'] and value['spec_hash'] == digest(plan)
            and value['root'] == str(root), 'A14 publication root/plan mismatch')
    require(value['halt'] is None and round_halt(root) is None, 'A14 halted round certifies nothing')
    require(read(root / 'identity.json') == dict(code_hash=plan['code_hash'], spec_hash=digest(plan)), 'A14 root identity mismatch')
    history = read(root / 'launches.json')
    require(bool(history) and history[-1].get('complete') is True, 'A14 launch not complete')
    check = read(root / PHASE / 'nondeterminism_check.json')
    require(check.get('matched') is True and check.get('checked') in {j['id'] for j in plan['jobs']}, 'A14 check did not pass')
    if 'pull_dispatch' in plan:
        from .dispatch_store_a11 import read_state
        state = read_state(root)
        require(state.get('complete') is True and not state.get('halt')
                and state.get('checks', {}).get(PHASE) == check, 'A14 pull check incomplete')



def construct_round(verified, invocation, *, registered, rehearsal, checked=lambda name, **values: None):
    old, original = verified['old'], verified['original']
    selected = {k: verified['selected'][k] for k, ok in verified['eligible'].items() if ok}
    require(bool(selected), 'A14 has no eligible rows')
    chosen = {}
    for jid, c in verified['sources'].items():
        rows = {k: p for k, p in c['eligible_rows'].items() if k in selected}
        if rows:
            chosen[jid] = (c, rows)
    sources = [c['a1_job'] for c, _ in chosen.values()]
    pricing = price_round(original, invocation['projection'], sources, registered=registered,
                          projection_file_hash=invocation['projection_file_hash'])
    checked('pricing_metrics', R_max=pricing['R_max'], projected_x2_hours=pricing['projected_x2_hours'])
    require(pricing['R_max'] >= 24, 'A14 no-launch floor: stage 1 ends')
    checked('pricing_and_floor')
    inventory = invocation['inventory']
    forbidden = {s for values in inventory.values() for s in values}
    forbidden.update(old['forbidden_seeds'])
    forbidden.update(r['seed'] for r in old['seed_manifest'])
    require(all(type(s) is int and s >= 0 for s in forbidden), 'invalid A14 inventory seed')
    r_max = pricing['R_max']
    manifest = seed_manifest(sources, r_max, forbidden, rehearsal=rehearsal)
    checked('seed_manifest_and_collisions')
    return selected, chosen, pricing, inventory, forbidden, manifest


def prepare(history_path, projection_path, seed_inventory_path, forecast_config, output, *,
            registration=None, rehearsal=False, resume=False, wall_hours=16., overhead_hours=1.):
    """Validate invocation, reserve, then verify evidence and freeze the plan."""
    registered = registration is not None
    reference = dict(history_path=str(Path(history_path).resolve()))
    invocation = validate_preparation_invocation(output, reference, dict(history=history_path, projection=projection_path,
        seed_inventory=seed_inventory_path, forecast_configuration=forecast_config),
        registration=registration, rehearsal=rehearsal, resume=resume, wall_hours=wall_hours, overhead_hours=overhead_hours)
    anchor = reserve_preparation(output, reference, registered=registered, resume=resume)
    try:
        history_document = read(history_path)
        with lease(anchor.with_suffix('.lock')):
            preliminary = unseal(read(anchor))
            require(preliminary.get('history_sha256') in (None, digest(history_document)), 'A14 history changed on preparation resume')
            preliminary['history_sha256'] = digest(history_document)
            atomic_json(anchor, seal(preliminary))
        from .history_a14 import verify_history
        from .history_a14 import stage_history
        stage_history(history_document)
        verified = verify_history(history_document, registered=registered)
        old, original = verified['old'], verified['original']
        selected, chosen, pricing, inventory, forbidden, manifest = construct_round(
            verified, invocation, registered=registered, rehearsal=rehearsal)
        r_max = pricing['R_max']
        from .forecast_a14 import forecast
        probabilities = forecast(history_document, r_max, sorted(selected), forecast_config,
                                 registered=registered, validated=invocation['forecast'])
        core = dict(schema=SCHEMA, code_hash=code_identity(), registered=registered, registered_a10=registered,
                    instrument=original['instrument'], registration=registration, tag='v3_tables', round=2,
                    round_record_path=str(anchor), history=history_document,
                    classification=verified['classification'], classification_sha256=verified['classification_sha256'],
                    a13_plan_hash=old['plan_hash'], original_plan_hash=original['plan_hash'],
                    M=original['M'], P=old['P'], E=old['E'], E2=len(selected), alpha=old['alpha'],
                    eligibility=[dict(row=r['row'], setting=r['setting'],
                        eligible=bool(r['setting'] == 'primary' and verified['eligible'].get(r['row'], False)))
                        for r in old['eligibility']],
                    source_jobs=sorted(chosen), R_max=r_max, pricing=pricing, launch_allowed=True,
                    seed_manifest=manifest, forbidden_seeds=sorted(forbidden),
                    seed_check=check_seed_manifest(manifest, forbidden, rehearsal=rehearsal),
                    seed_inventory_sha256=invocation['inventory_file_hash'],
                    seed_inventory_inputs=dict(a13_seed_manifest_sha256=digest(old['seed_manifest']),
                        a13_forbidden_seeds_sha256=digest(old['forbidden_seeds']),
                        a13_qualification_seeds_sha256=digest(inventory['a13_qualification_seeds']),
                        a13_configuration_seeds_sha256=digest(inventory['a13_configuration_seeds'])),
                    forecast=probabilities, impossible_rows={k: p['n_star'] > 2048 * r_max for k, p in selected.items()},
                    wall_seconds=wall_hours * 3600, x2_equivalent_hours=15 + overhead_hours,
                    simulation_cap_x2_hours=15, overhead_x2_hours=overhead_hours,
                    non_registered_rehearsal=rehearsal, configuration_seconds=1800,
                    cleanup_reserve_seconds=1200, phases=[PHASE], publication=None,
                    memory_estimate_gb={PHASE: original['memory_estimate_gb']['validate_plain']})
        from .snapshot_a11 import normalize_historical_roots
        roots = normalize_historical_roots(unseal(history_document).get('historical_roots', []))
        if roots:
            core.update(historical_roots=roots, historical_roots_sha256=digest(roots))
        configs = []
        for jid, (old_config, rows) in sorted(chosen.items()):
            c = {k: deepcopy(old_config[k]) for k in
                 ('route', 'a1_source_root', 'a1_job', 'a1_source_code_hash', 'fit', 'trajectory_count')}
            c.update(phase=PHASE, eligible_rows=rows, M=core['M'], R_max=r_max,
                     full_seed_manifest=manifest, forbidden_seeds=sorted(forbidden), non_registered_rehearsal=rehearsal,
                     stream_seeds=[r['seed'] for r in manifest if r['source_job_id'] == jid])
            needed = {str((Path(c['a1_source_root']) / 'tables_A1/table' / directory /
                           (c['a1_job']['id'] + '.json')).resolve()) for directory in ('outputs', 'records')}
            needed.add(str((SIMULATION / c['a1_job']['config']['calibration_path']).resolve()))
            c['a14_inputs'] = []
            for row in unseal(history_document)['files']:
                names = {str(Path(p).resolve()) for p in [row['source'], *row.get('aliases', [])]}
                for name in sorted(names & needed):
                    c['a14_inputs'].append(dict(deepcopy(row), source=name, aliases=sorted(names - {name})))
            require({str(Path(r['source']).resolve()) for r in c['a14_inputs']} == needed, 'A14 phase input inventory incomplete')
            if old_config.get('settings_override'):
                require(not registered, 'registered A14 cannot override scientific settings')
                c['settings_override'] = old_config['settings_override']
            configs.append(c)
        core['job_skeletons'] = configs
        core['plan_hash'] = plan_hash(core)
        core['jobs'] = [stable_job(KIND, dict(c, plan_hash=core['plan_hash']), 'v3_tables', i)
                        for i, c in enumerate(configs)]
        profiles = [dict(c, plan_hash=core['plan_hash'], configuration_test=True,
                        settings_override={**c.get('settings_override', {}), 'burn': 30, 'measure': 8},
                        seed=(1 << 128) | int(digest(['A14-configuration', core['plan_hash'], i])[:32], 16))
                    for i, c in enumerate(configs)]
        core['configuration'] = {PHASE: dict(kind=KIND, config=profiles[0], configs=profiles,
                    workers_local=[2, 4, 8, 12], workers_x2=[8, 12, 16, 24, 32], threads=[1],
                    rounds=1, jobs_local=12, jobs_x2=32, jobs_per_worker=2)}
        validate_plan(core)
        with lease(anchor.with_suffix('.lock')):
            record = unseal(read(anchor))
            require(record['state'] == 'preparing' and record['halt'] is None, 'A14 preparation no longer live')
            require(record['plan_hash'] in (None, core['plan_hash']), 'A14 preparation hash changed on resume')
            record.update(plan_hash=core['plan_hash'])
            atomic_json(anchor, seal(record))
            for path, value in ((Path(output), seal(core)), (Path(output).with_suffix('.public.json'), seal(public_record(core)))):
                if path.exists():
                    require(read(path) == value, 'A14 preparation record changed')
                else:
                    atomic_json(path, value)
            record['state'] = 'prepared'
            atomic_json(anchor, seal(record))
        return core
    except (OSError, MemoryError):
        raise
    except Exception as exc:
        preparation_failure(anchor, type(exc).__name__)
        raise
    # OSError/transport interruption leaves state=preparing, for explicit resume
    # of the same request. No sampling occurs during preparation.


def preentry(history_path, projection_path, seed_inventory_path, forecast_config, output, report_path, *, registration):
    """Read-only pre-entry audit; only its separate operational report is written."""
    import os
    from .history_a14 import verify_history
    report_path = Path(report_path).resolve()
    require(report_path.is_relative_to(SIMULATION.parent) and not report_path.exists()
            and not {'runs', 'registered', '.git'}.intersection(p.lower() for p in report_path.parts), 'unsafe preentry report path')
    forbidden_paths = {Path(p).resolve() for p in (history_path, projection_path, seed_inventory_path, forecast_config, output)}
    reference = dict(history_path=str(Path(history_path).resolve()))
    anchor, _ = preparation_request(output, reference, registered=True)
    require(report_path not in forbidden_paths | {anchor, anchor.with_suffix('.lock')}, 'preentry report overlaps a record')
    names = ('invocation', 'historical_records', 'eligibility_and_residual_set', 'constants',
             'pricing_and_floor', 'seed_manifest_and_collisions', 'forecast_layout', 'forecast_case_a')
    result = dict(schema=SCHEMA + '-preentry', passed=False, E2=None, R_max=None, projected_x2_hours=None,
                  checks={name: dict(passed=False, status='not_run') for name in names})
    active = 'invocation'
    report_protected = []
    def checked(name):
        result['checks'][name] = dict(passed=True, status='passed')
    try:
        invocation = validate_preparation_invocation(output, reference, dict(history=history_path, projection=projection_path,
            seed_inventory=seed_inventory_path, forecast_configuration=forecast_config),
            registration=registration, rehearsal=False, resume=False)
        checked('invocation')
        active = 'historical_records'
        document = read(history_path)
        payload = unseal(document)
        report_protected = [*payload['directories'], *payload['directories'].values()]
        require(not any(report_path.is_relative_to(Path(p).resolve()) for p in report_protected),
                'preentry report overlaps history')
        verified = verify_history(document, registered=True)
        for name in ('historical_records', 'eligibility_and_residual_set', 'constants'):
            checked(name)
        result['E2'] = sum(verified['eligible'].values())
        active = 'pricing_and_floor'
        def construction_checked(name, **values):
            nonlocal active
            if values:
                result.update(values)
                return
            checked(name)
            active = 'seed_manifest_and_collisions'
        selected, _, pricing, _, _, _ = construct_round(verified, invocation, registered=True,
                                                       rehearsal=False, checked=construction_checked)
        from .forecast_a14 import check_preentry_layout, check_case_a
        active = 'forecast_layout'
        check_preentry_layout(verified, invocation['forecast'])
        checked(active)
        active = 'forecast_case_a'
        check_case_a(verified, sorted(selected))
        checked(active)
        result.update(passed=True, E2=len(selected), R_max=pricing['R_max'], projected_x2_hours=pricing['projected_x2_hours'])
    except Exception as exc:
        result['checks'][active] = dict(passed=False, status='failed', error_class=type(exc).__name__)
    require(not any(report_path.is_relative_to(Path(p).resolve()) for p in report_protected),
            'preentry report overlaps history')
    report_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = report_path.with_name(report_path.name + '.partial')
    with temporary.open('xb') as stream:
        stream.write(canonical(result) + b'\n'); stream.flush(); os.fsync(stream.fileno())
    os.replace(temporary, report_path)
    return result


def decline(*, plan_path=None, anchor_path=None, operator, reason):
    """Explicit operator end, only before launch and under the anchor lease."""
    require(bool(operator.strip()) and bool(reason.strip()), 'operator decline needs operator and reason')
    require((plan_path is None) != (anchor_path is None), 'decline needs exactly one plan or preparing anchor')
    if plan_path is not None:
        plan = unseal(read(plan_path))
        validate_plan(plan)
        path, expected = round_record_path(plan), 'prepared'
    else:
        path, expected = scoped(anchor_path), 'preparing'
    with lease(path.with_suffix('.lock')):
        value = unseal(read(path))
        require(value.get('schema') == SCHEMA + '-round' and value['state'] == expected
                and value['halt'] is None and value['root'] is None, 'decline is valid only before launch in the specified state')
        if plan_path is not None:
            require(value['plan_hash'] == plan['plan_hash'], 'decline plan binding differs')
        value.update(state='refused', halt=dict(reason='operator declined: ' + reason,
                                               operator=operator, epoch=time.time()))
        atomic_json(path, seal(value))


def public_record(plan):
    return dict(schema=SCHEMA + '-public', amendment='A13 and A14, informed by outcomes', round=2,
        original_refusal_preserved=True, a13_refusal_preserved=True,
        plan_hash=plan['plan_hash'], original_plan_hash=plan['original_plan_hash'],
        a13_plan_hash=plan['a13_plan_hash'], code_hash=plan['code_hash'], E=plan['E'], E2=plan['E2'],
        P=plan['P'], M=plan['M'], alpha=plan['alpha'],
        extension_error_bound=plan['alpha'] * plan['E'] / plan['M'],
        fitted_family_error_bound=plan['alpha'] * (1 + plan['P'] / plan['M']),
        conditional_additional_error_bound=plan['alpha'] * plan['E'] / plan['M'],
        family_error_bound_given_fit=plan['alpha'] * (1 + plan['P'] / plan['M']),
        family_error_bound_unconditional=2 * plan['alpha'],
        R_max=plan['R_max'], projected_x2_hours=plan['pricing']['projected_x2_hours'],
        eligibility=plan['eligibility'], source_jobs=plan['source_jobs'], impossible_rows=plan['impossible_rows'],
        seed_manifest=plan['seed_manifest'], seed_check=plan['seed_check'],
        historical_inventory=plan['history'], classification_sha256=plan['classification_sha256'],
        forecast=plan['forecast'])


def reassemble(verified, new_tests):
    tests = deepcopy(verified['tests'])
    expected = {k for k, ok in verified['eligible'].items() if ok}
    require(set(new_tests) == expected, 'A14 decisions do not cover exactly the eligible set')
    tests.update(new_tests)
    rows, details = a13.reassemble(verified['rows'], verified['details'], verified['selected'], tests,
                                  verified['fits'], verified['censuses'])
    for key, test in tests.items():
        tested = test.get('reason') != 'N* not reached'
        round_number = (2 if key in expected else 1) if tested else None
        rows[key]['a13']['round'] = round_number
        detail = next(d for d in details if d['row'] == key and d['setting'] == 'primary')
        detail['a14_retest'] = dict(round=round_number, test=deepcopy(test),
                                   classification_sha256=verified['classification_sha256'])
    a13.assert_ineligible_identity(verified['rows'], rows, verified['details'], details, set(verified['selected']))
    return rows, details, tests


def admission_record(plan, rows, details, test_counts=None):
    from .admission_a13 import binding
    path = round_record_path(plan).with_suffix('.admission.json')
    require(unseal(read(round_record_path(plan))).get('schema') == SCHEMA + '-round', 'not an A14 round record')
    record = dict(schema='v3-A13-admission-check-1', scope='A10_nominal_after_A14', plan_hash=plan['plan_hash'],
                  primary_rows=len(rows), cap=len(rows) // 1000,
                  residual_rows=sorted(k for k, r in rows.items() if r['status'] == 'not_estimable'))
    record['residual_count'] = len(record['residual_rows'])
    if test_counts is not None:
        record.update(test_counts)
        record.update(E=plan['E'], E2=plan['E2'], P=plan['P'], M=plan['M'],
                      alpha=plan['alpha'], extension_error_bound=plan['alpha'] * plan['E'] / plan['M'])
    error, result = None, None
    try:
        result = binding(rows, details, record['scope'])
        record.update(outcome='passed', admitted_set_sha256=result['admitted_set_sha256'])
    except (ValueError, KeyError) as exc:
        record['outcome'], error = 'refused', exc
    with lease(path.with_suffix('.lock')):
        document = seal(record)
        if path.exists():
            require(read(path) == document, 'A14 admission record is final')
        else:
            atomic_json(path, document)
    if error is not None:
        preparation_failure(round_record_path(plan), 'Part 2 refused')
        raise error
    return result, file_hash(path)


def publish(plan, extension_root, target, *, registered=True):
    import hashlib
    from .artifacts import verify_registration
    from .history_a14 import verify_history
    from .production_runner import completed
    from .production_tables import ProductionTables
    validate_plan(plan)
    target, root = scoped(target), scoped(extension_root)
    if registered:
        require(plan['registered'] and target == scoped(SIMULATION / TARGET), 'A14 registered target or plan differs')
        verify_registration(plan['registration'], instrument=plan['instrument'])
    publication_round(plan, root)
    verified = verify_history(plan['history'], registered=registered)
    require(verified['classification_sha256'] == plan['classification_sha256'], 'historical classifications changed')
    new_tests, hashes = {}, {}
    for job in plan['jobs']:
        output = completed(root / PHASE, job, plan['code_hash'])
        require(output is not None, 'A14 incomplete; resume infrastructure interruption')
        result, c = output['result'], job['config']
        require(result['stage'] == PHASE and result['plan_hash'] == plan['plan_hash']
                and result['a1_job_id'] == c['a1_job']['id'] and result['code_hash'] == plan['code_hash'], 'A14 result identity differs')
        replicates = validate_replicates(job, result['replicates'])
        stopped = stop_reached(replicates, c['eligible_rows'])
        require(result['stopped_on_visits'] == stopped and (stopped or len(replicates) == c['R_max']), 'A14 stopped early')
        hashes[job['id']] = file_hash(root / PHASE / 'outputs' / (job['id'] + '.json'))
        for key, parameters in c['eligible_rows'].items():
            new_tests[key] = extension_test([dict(replicate=r['replicate'], trajectories=r['rows'][key])
                                             for r in replicates], parameters)
    rows, details, tests = reassemble(verified, new_tests)
    test_counts = dict(tests_round1=sum(t.get('reason') != 'N* not reached' for t in verified['tests'].values()),
                       tests_round2=sum(t.get('reason') != 'N* not reached' for t in new_tests.values()))
    admission, admission_hash = admission_record(plan, rows, details, test_counts)
    summary = public_record(plan)
    # Public report has identifiers/counts only, never a realized seed subset.
    summary.update(outcome='completed', **test_counts)
    payload = deepcopy(unseal(verified['candidate']))
    payload['manifest'].update(a14=summary, a13_admission=admission)
    payload.update(rows={k: seal(v) for k, v in rows.items()}, code_hash=code_identity(), fixture=not registered)
    payload['manifest_hash'] = digest(payload['manifest'])
    document = seal(payload)
    original_sidecar = unseal(verified['history'].read(Path(verified['old']['candidate_path']).with_suffix('.cell_results.json')))
    sidecar = seal(dict(original_sidecar, table_seal_sha256=document['sha256'], rows=details, a14=summary))
    old = verified['old']
    h = verified['history']
    public_path = Path(unseal(read(round_record_path(plan)))['request']['output']).with_suffix('.public.json')
    require(unseal(read(public_path)) == public_record(plan), 'A14 approved public record changed')
    receipt = dict(verified['receipt'], table_seal_sha256=document['sha256'],
        table_file_sha256=hashlib.sha256(canonical(document) + b'\n').hexdigest(),
        cell_results_sha256=hashlib.sha256(canonical(sidecar) + b'\n').hexdigest(), producer_code_hash=code_identity(),
        a14=summary,
        a13_round=dict(plan_hash=old['plan_hash'], public_file_sha256=file_hash(h.file(h.role('a13_public'))),
            stage_output_sha256=verified['a13_stage_hashes'], seed_manifest=old['seed_manifest'],
            admission_record_sha256=verified['a13_admission_sha256']),
        a14_round=dict(plan_hash=plan['plan_hash'], public_file_sha256=file_hash(public_path),
            stage_output_sha256=hashes, seed_manifest=plan['seed_manifest'], admission_record_sha256=admission_hash),
        extension_seed_manifest=old['seed_manifest'] + plan['seed_manifest'],
        refusals=dict(original=dict(table_file_sha256=old['candidate_file_sha256'],
                                   sidecar_file_sha256=old['candidate_sidecar_sha256']),
                      a13_admission_record_sha256=verified['a13_admission_sha256']))
    require(receipt['plan_hash'] == verified['receipt']['plan_hash']
            and receipt['stream_seeds'] == verified['receipt']['stream_seeds'], 'original receipt fields changed')
    if registered:
        ProductionTables(document, calibration_hash=payload['manifest']['calibration_hash'], registered=True)
    if target.exists():
        require(read(target) == document, 'A14 publication target is frozen')
    a13.assert_ineligible_identity(verified['rows'], rows, verified['details'], details, set(verified['selected']))
    publication_round(plan, root)
    atomic_json(target.with_suffix('.compatibility.json'), seal(receipt))
    atomic_json(target.with_suffix('.cell_results.json'), sidecar)
    atomic_json(target, document)
    return document, receipt


def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    prep = commands.add_parser('prepare')
    for name in ('history', 'projection', 'seed-inventory', 'forecast-config', 'output'):
        prep.add_argument('--' + name, required=True)
    modes = prep.add_mutually_exclusive_group(required=True)
    modes.add_argument('--registration', help='JSON file containing the committed registration pin')
    modes.add_argument('--rehearsal', action='store_true')
    prep.add_argument('--resume-preparation', action='store_true')
    prep.add_argument('--wall-hours', type=float, default=16.)
    prep.add_argument('--overhead-hours', type=float, default=1.)
    entry = commands.add_parser('preentry')
    for name in ('history', 'projection', 'seed-inventory', 'forecast-config', 'output', 'report', 'registration'):
        entry.add_argument('--' + name, required=True)
    pub = commands.add_parser('publish')
    for name in ('plan', 'root', 'target'):
        pub.add_argument('--' + name, required=True)
    pub.add_argument('--fixture', action='store_true')
    end = commands.add_parser('decline')
    which = end.add_mutually_exclusive_group(required=True)
    which.add_argument('--plan'); which.add_argument('--anchor')
    end.add_argument('--operator', required=True); end.add_argument('--reason', required=True)
    args = parser.parse_args()
    if args.command == 'prepare':
        plan = prepare(args.history, args.projection, args.seed_inventory, args.forecast_config, args.output,
                       registration=read(args.registration) if args.registration else None,
                       rehearsal=args.rehearsal, resume=args.resume_preparation,
                       wall_hours=args.wall_hours, overhead_hours=args.overhead_hours)
        print('A14 prepared; public record:', Path(args.output).with_suffix('.public.json'))
    elif args.command == 'preentry':
        result = preentry(args.history, args.projection, args.seed_inventory, args.forecast_config, args.output,
                          args.report, registration=read(args.registration))
        print('A14 preentry passed' if result['passed'] else 'A14 preentry failed')
        raise SystemExit(0 if result['passed'] else 1)
    elif args.command == 'publish':
        publish(unseal(read(args.plan)), args.root, args.target, registered=not args.fixture)
        print('A14 family published.')
    else:
        decline(plan_path=args.plan, anchor_path=args.anchor, operator=args.operator, reason=args.reason)
        print('A14 declined; A10 stage 1 ends.')


if __name__ == '__main__':
    main()
