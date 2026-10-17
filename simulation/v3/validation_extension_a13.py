"""A13's single, separately indexed plain-validation extension.

Plans and trajectory records are executor-only. public_record deliberately
omits widths, N*, reach, original visit counts and per-stratum prices.
"""
import argparse
from collections import defaultdict
from contextlib import contextmanager
from contextvars import ContextVar
from copy import deepcopy
import hashlib
import math
from pathlib import Path

import numpy as np
from .artifacts import (ROOT, SIMULATION, atomic_json, canonical, code_identity, digest,
                        file_hash, read, scoped, seal, stable_job, unseal, lease)
from . import continuation_validation as cv
from . import table_validation_a4 as a4

SCHEMA = 'v3-A13-extension-1'
PHASE = 'validate_plain_ext'
KIND = 'a13_validate_plain_ext'
RESERVED = (1 << 60, 1 << 61)
PROJECTION_FILE_SHA256 = '78a1d3ac253048c7e077b0e4eb12dd3150fa178cf3e63a24c6f0d87f02a8ad8d'
PROJECTION_SEAL = '5ca5225967cf08ad5636f98f12d57fa6ccd753a7ae126bff0edcc09f0af3d8a3'
TARGET = 'v3/runs/a10_stage1/nominal/v3_rerun_tables_A10.json'
_checkpoint_context = ContextVar('a13_checkpoints', default=None)


class ScientificHalt(RuntimeError):
    pass


def require(condition, message):
    if not condition:
        raise ValueError(message)


def ext_seed(source_seed, replicate):
    require(isinstance(replicate, int) and not isinstance(replicate, bool) and replicate >= 4, 'invalid extension replicate')
    value = (1 << 60) + cv._truncated_sha('v3_R_validate_ext', int(source_seed), '/', replicate)
    require(RESERVED[0] <= value < RESERVED[1], 'extension seed outside reserved range')
    return value


def rehearsal_seed(source_seed, replicate):
    return (1 << 128) | int(digest(['A13-rehearsal-stream', source_seed, replicate])[:32], 16)


def seed_manifest(jobs, r_max, forbidden, *, rehearsal=False):
    require(isinstance(r_max, int) and 0 <= r_max <= 16, 'invalid R_max')
    require(len({j['id'] for j in jobs}) == len(jobs), 'duplicate extension source')
    result = [{'source_job_id': j['id'], 'replicate': r, 'seed': (rehearsal_seed if rehearsal else ext_seed)(j['seed'], r)}
              for j in sorted(jobs, key=lambda x: x['id']) for r in range(4, 4 + r_max)]
    check_seed_manifest(result, forbidden, rehearsal=rehearsal)
    return result


def check_seed_manifest(manifest, forbidden, *, rehearsal=False):
    seeds = [r['seed'] for r in manifest]
    if len(set(seeds)) != len(seeds) or set(seeds) & set(forbidden):
        raise cv.SeedCollision('A13 global extension seed collision')
    bounds = (1 << 128, 1 << 129) if rehearsal else RESERVED
    require(all(type(s) is int and bounds[0] <= s < bounds[1] for s in seeds), 'invalid extension seed range')
    return {'passed': True, 'manifest_sha256': digest(manifest), 'forbidden_sha256': digest(sorted(set(forbidden))),
            'reserved_range': list(RESERVED), 'non_registered_rehearsal': rehearsal}


def sample_size(width, M, tau, alpha=cv.ALPHA):
    require(width > 0 and tau > 0 and type(M) is int and M > 0 and alpha == cv.ALPHA, 'invalid pinned test parameters')
    # The zero-variance radius at n=2 is exactly 7*w*log(4*M/alpha)/3.
    numerator = cv.empirical_bernstein(0., 0., 2, width, M, tau, alpha)['rho']
    c = numerator / tau
    n_star = 1 + math.ceil(2 * c)
    deterministic = cv.empirical_bernstein(0., 0., n_star, width, M, tau, alpha)['rho']
    require(deterministic <= tau / 2, 'N* deterministic radius exceeds tau/2')
    return n_star


def eligible(row, detail, a1_row, fit_row, original_cells, M, lower, upper, *, primary=True):
    """Original sufficient statistics and the sealed fit supply the arithmetic."""
    fit = fit_row.get('c0', {})
    floor = row.get('a4', {}).get('floor', {})
    c0 = original_cells.get(cv.POP0_CELL, {})
    n = int(c0.get('n_traj', 0))
    tests = detail.get('cell_tests', [])
    c0_test = next((t for t in tests if t['cell'] == cv.POP0_CELL), None)
    # With no visiting trajectories, the original EB function is unresolved.
    unresolved = c0_test is not None and c0_test.get('eb') == 'unresolved' or c0_test is None and n == 0
    ok = (primary and row.get('route') == 'plain' and row.get('status') == 'not_estimable'
          and row.get('reason') == 'A4 availability floor failed' and a4.a1_base_screens_ok(a1_row)
          and row.get('a4', {}).get('base_screens_ok') is True
          and row.get('a4', {}).get('validated_support_size', 0) > 0
          and row.get('sensitivity', {}).get('passed') is not False
          and floor.get('living_ok') is True and floor.get('low_assessed') is True and floor.get('low_ok') is False
          and unresolved and not any(t.get('eb', t.get('status')) == 'violation' for t in tests)
          and fit.get('published') is True and fit.get('value') is not None)
    if not ok:
        return False, None
    vmax = a4._row_vmax(a4.a1_published_plain(a4._entries(a1_row)), fit)
    width = cv.row_width(a1_row['flow_range'], vmax, lower, upper)
    tau = .05 * a1_row['flow_range']
    require(tau == row['a4']['tau'], 'row tau differs from original A1 range')
    term = None if n < 2 else cv.empirical_bernstein(0., 0., n, width, M, tau)['rho']
    if n >= 2 and term <= tau:
        return False, None
    return True, {'width': width, 'tau': tau, 'M': M, 'alpha': cv.ALPHA,
                  'n_star': sample_size(width, M, tau), 'lower': lower, 'upper': upper}


def price_extension(validation_plan, projection_document, jobs, *, registered, projection_file_hash=None):
    """Check the original sealed-plan binding BEFORE computing any price."""
    projection = unseal(projection_document)
    require(projection_document['sha256'] == validation_plan['pull_dispatch']['projection_sha256'],
            'finding: projection payload seal differs from sealed validation plan')
    if registered:
        require(projection_document['sha256'] == PROJECTION_SEAL and projection_file_hash == PROJECTION_FILE_SHA256,
                'finding: A13 registered projection identity mismatch')
    prices = {}
    by_id = {j['id']: j for j in jobs}
    require(len(by_id) == len(jobs), 'duplicate source job in extension pricing')
    for jid, j in sorted(by_id.items()):
        c = j['config']
        stratum = f"{c['a10_family']}.{float(c['kernel']['capability'])}.{c['setting_name']}.validate_plain"
        p = projection['per_phase_capability'][stratum]
        require(type(p['jobs']) is int and p['jobs'] > 0 and isinstance(p['x2_hours_max'], (int, float))
                and math.isfinite(p['x2_hours_max']) and p['x2_hours_max'] > 0, 'invalid registered stratum price')
        prices[jid] = {'stratum': stratum, 'replicate_x2_hours': p['x2_hours_max'] / p['jobs'] / 3}
    total = math.fsum(p['replicate_x2_hours'] for p in prices.values())
    r_max = max(r for r in range(17) if r * total <= 15)
    return {'R_max': r_max, 'projected_x2_hours': r_max * total, 'prices': prices,
            'projection_sha256': projection_document['sha256']}


def extension_test(records, parameters):
    n_star = parameters['n_star']
    # Iterate the frozen replicate order and batch order, never completion order.
    require([r['replicate'] for r in records] == list(range(4, 4 + len(records))), 'extension replicate order or gap')
    visiting = [pair for r in records for pair in r['trajectories'] if pair[1] > 0][:n_star]
    if len(visiting) < n_star:
        return {'status': 'unresolved', 'reason': 'N* not reached', 'n': len(visiting), 'visit_weighted_ok': False}
    S, N = np.asarray(visiting, dtype=float).T
    means = S / N
    eb = cv.empirical_bernstein(float(means.sum()), float((means ** 2).sum()), len(means),
                               parameters['width'], parameters['M'], parameters['tau'], parameters['alpha'])
    eb['visit_weighted_ok'] = bool(cv.visit_weighted_ok(float(S.sum()), float(N.sum()), parameters['tau']))
    return eb


def extension_stage(a1_output, fit, rows, seed, override=None):
    """Fresh trajectories only. Record each eligible C0's ordered (S_i,N_i)."""
    require(a1_output['result']['route'] == 'plain', 'extension requires plain source')
    trace = a4.TableTrace(a1_output, seed, override)
    src, nxt = cv.plain_cell_codes(trace.before), cv.plain_cell_codes(trace.after)
    result = {}
    for key, info in rows.items():
        i = info['row_index']
        row = a1_output['result']['rows'][i]
        values = a4.a1_published_plain(a4._entries(row))
        c0 = fit['rows'][i]['c0']
        require(c0['published'] and c0['value'] is not None, 'extension C0 fit is not published')
        values[cv.POP0_CELL] = c0['value']
        cv.check_in_range(list(values.values()), trace.lower, trace.upper, 'A1/C0 value')
        flows = trace.flows(row['scoring'])
        cv.check_in_range(flows, trace.lower, trace.upper, 'flow')
        residual, covered, _, _ = cv.living_source_residuals(src, nxt, trace.source_alive, trace.dead, flows, values, trace.lower)
        visits = covered & (src == cv.POP0_CELL)
        S = np.bincount(trace.traj[visits], weights=residual[visits], minlength=trace.count)
        N = np.bincount(trace.traj[visits], minlength=trace.count)
        result[key] = [[float(s), int(n)] for s, n in zip(S, N)]
    if trace.truncated:
        raise ScientificHalt('truncated extension trajectory')
    return {'rows': result, 'count': trace.count, 'settings': trace.settings}


def stop_reached(replicates, rows):
    return all(sum(pair[1] > 0 for r in replicates for pair in r['rows'][key]) >= info['n_star']
               for key, info in rows.items())


@contextmanager
def checkpoint_context(directory, initial=(), *, recheck=False):
    token = _checkpoint_context.set((Path(directory), list(initial), recheck))
    try:
        yield
    finally:
        _checkpoint_context.reset(token)


def validate_replicates(job, replicates):
    c = job['config']
    require(len(replicates) <= c['R_max'], 'too many extension replicates')
    prior = []
    for index, r in enumerate(replicates):
        require(not prior or not stop_reached(prior, c['eligible_rows']), 'extension continued after registered stop')
        require(r['replicate'] == index + 4 and r['seed'] == c['stream_seeds'][index], 'extension checkpoint seed/order mismatch')
        require(set(r['rows']) == set(c['eligible_rows']), 'extension checkpoint row mismatch')
        require(r['count'] == c['trajectory_count'], 'extension trajectory count mismatch')
        for pairs in r['rows'].values():
            require(len(pairs) == r['count'] and all(len(p) == 2 and math.isfinite(p[0]) and type(p[1]) is int
                    and p[1] >= 0 and (p[1] > 0 or p[0] == 0) for p in pairs), 'invalid ordered trajectory records')
        prior.append(r)
    return prior


def durable_checkpoints(root, job):
    values = []
    for path in sorted((Path(root) / PHASE / 'a13_checkpoints' / job['id']).glob('*.json')):
        payload = unseal(read(path))
        require(payload['job_sha256'] == digest(job), 'checkpoint belongs to another job')
        values.append(payload['replicate'])
    return validate_replicates(job, values)


def accept_checkpoint(coordinator, request):
    """A replica becomes durable only after the coordinator verifies and writes it."""
    coordinator.session(request)
    leased = coordinator.state['leases'].get(request['lease'])
    require(leased and leased['host'] == request['host'] and leased['session'] == request['session'], 'wrong checkpoint lease')
    job = coordinator.jobs[leased['job_id']]
    require(job['kind'] == KIND and leased['purpose'] == 'work' and not coordinator.state['halt'], 'checkpoint not allowed')
    payload = unseal(request['checkpoint'])
    require(payload['job_sha256'] == digest(job), 'checkpoint job hash changed')
    values = durable_checkpoints(coordinator.root, job)
    replica = payload['replicate']
    index = replica['replicate'] - 4
    if index < len(values):
        if canonical(replica) != canonical(values[index]):
            coordinator.state['halt'] = 'A13 replicate nondeterminism'
            atomic_json(coordinator.root / 'a13_scientific_halt.json', seal({'reason': coordinator.state['halt']}))
            latch_round_halt(coordinator.root, coordinator.state['halt'])
            raise ScientificHalt('A13 checkpoint mismatch')
        return {'accepted': True}
    require(index == len(values), 'checkpoint replicate gap')
    validate_replicates(job, values + [replica])
    atomic_json(coordinator.root / PHASE / 'a13_checkpoints' / job['id'] / f'{replica["replicate"]:02d}.json', request['checkpoint'])
    return {'accepted': True}


def run_stage_job(job, root):
    c = job['config']
    configuration = job['tag'] in ('configuration', 'validation') and c.get('configuration_test')
    require(c['phase'] == PHASE and c['M'] > 0, 'invalid extension phase or M')
    require(all(p['M'] == c['M'] for p in c['eligible_rows'].values()), 'extension row M differs from plan')
    seeds = [c['seed']] if configuration else c['stream_seeds']
    if configuration:
        require(not RESERVED[0] <= c['seed'] < RESERVED[1], 'configuration used extension seed')
    else:
        seed_fn = rehearsal_seed if c.get('non_registered_rehearsal') else ext_seed
        require(seeds == [seed_fn(c['a1_job']['seed'], r) for r in range(4, 4 + c['R_max'])], 'extension seeds changed')
        check_seed_manifest(c['full_seed_manifest'], c['forbidden_seeds'], rehearsal=c.get('non_registered_rehearsal', False))
        require(c['R_max'] >= 6, 'extension no-launch floor')
    a1 = a4._load_a1(c['a1_source_root'], c['a1_job'], c['a1_source_code_hash'])
    fit = unseal(c['fit'])
    require(fit['a1_job_id'] == c['a1_job']['id'], 'extension fit source mismatch')
    local = _checkpoint_context.get()
    directory = Path(root) / 'a13_checkpoints' / job['id'] if local is None else local[0]
    prior = [] if local is None else deepcopy(local[1])
    recheck = local is not None and local[2]
    if local is None and not configuration:
        for p in sorted(directory.glob('*.json')):
            checkpoint = unseal(read(p))
            require(checkpoint['job_sha256'] == digest(job), 'extension checkpoint job mismatch')
            prior.append(checkpoint['replicate'])
    if configuration or recheck:
        prior = []
    if not configuration:
        validate_replicates(job, prior)
    for index, seed in enumerate(seeds):
        if index < len(prior):
            continue
        if prior and stop_reached(prior, c['eligible_rows']):
            break
        result = extension_stage(a1, fit, c['eligible_rows'], seed, c.get('settings_override'))
        result.update(replicate=index + 4, seed=seed)
        prior.append(result)
        if not configuration and not recheck:
            atomic_json(directory / f'{index + 4:02d}.json', seal({'job_sha256': digest(job), 'replicate': result}))
    return {'stage': PHASE, 'plan_hash': c['plan_hash'], 'a1_job_id': c['a1_job']['id'],
            'code_hash': code_identity(), 'replicates': prior,
            'stopped_on_visits': bool(prior and stop_reached(prior, c['eligible_rows']))}


def original_inputs(plan_path, run_root, candidate_path, *, registered):
    """Verify the carried-forward plan, completion records and refused bytes."""
    from .artifacts import verify_registration
    from .compatibility_a10 import accepted_identities
    plan = unseal(read(plan_path))
    require(plan.get('instrument', {}).get('mapping') == 'A10', 'extension is A10 only')
    require(a4._recompute_plan_hash(plan) == plan['plan_hash'], 'original validation plan changed')
    require(plan['code_hash'] in accepted_identities(), 'original producer needs committed A11 compatibility proof')
    if registered:
        a4.registered_publish_guard(plan)
        verify_registration(plan['registration'], instrument=plan['instrument'], historical=True)
    hashes, seeds = a4._verify_stage_outputs(plan, run_root)
    candidate = read(candidate_path)
    payload = unseal(candidate)
    sidecar = unseal(read(Path(candidate_path).with_suffix('.cell_results.json')))
    receipt = unseal(read(Path(candidate_path).with_suffix('.compatibility.json')))
    require(receipt['plan_hash'] == plan['plan_hash'] and receipt['stream_seeds'] == seeds
            and receipt['stage_output_sha256'] == hashes, 'refused receipt original stages differ')
    require(receipt['table_seal_sha256'] == candidate['sha256'] and receipt['table_file_sha256'] == file_hash(candidate_path)
            and receipt['cell_results_sha256'] == file_hash(Path(candidate_path).with_suffix('.cell_results.json'))
            and sidecar['table_seal_sha256'] == candidate['sha256'], 'refused candidate/sidecar binding mismatch')
    require(receipt['M'] == plan['M'] and sidecar['plan_hash'] == plan['plan_hash'], 'original pinned M or sidecar plan mismatch')
    calibration = read(SIMULATION / plan['calibration_path'])
    counts = a4.counts_from_job_outputs(plan['source_root'], plan['source_code_hash'])
    require((counts['M'], counts['M_FV']) == (plan['M'], plan['M_FV']), 'original M differs from sealed family')
    rows, sensitivity, details = a4.assemble_family(plan['source_root'], plan['source_code_hash'], run_root,
                                                   plan['M'], plan['M_FV'], {calibration['sha256']: calibration})
    from .offline_estimator import add_ranking_flags
    from .production_tables import row_key
    reconstructed = {row_key(r): seal(r) for r in add_ranking_flags(list(rows.values()))}
    require(canonical(reconstructed) == canonical(payload['rows']) and canonical(details) == canonical(sidecar['rows']),
            'refused candidate differs from original sealed computations')
    require(sensitivity == payload['manifest']['sensitivity_status'], 'refused sensitivity status differs')
    return plan, candidate, sidecar, receipt, calibration


def prepare(plan_path, run_root, candidate_path, projection_path, seed_inventory_path, output,
            *, registration=None, wall_hours=16., overhead_hours=1., rehearsal=False):
    """Create the one-round plan. Output and prices remain executor-only."""
    from .artifacts import verify_registration
    from .production_runner import completed
    from .production_tables import row_key
    from .context import Context
    registered = registration is not None
    require(registered != bool(rehearsal), 'exactly one of registered or rehearsal is required')
    require(not Path(output).exists(), 'extension plan is frozen; no second round')
    if registered:
        verify_registration(registration, instrument={'mapping': 'A10', 'k_star': 1.8, 'g': 'linear'})
    original, candidate, sidecar, receipt, calibration = original_inputs(plan_path, run_root, candidate_path, registered=registered)
    source_root = original['source_root']
    family = unseal(read(Path(source_root) / 'v3_rerun_tables_A1.json'))['manifest']['a10']['family']
    require(family == 'nominal' or not registered, 'A13 extension is nominal-family only')
    require(not unseal(candidate)['manifest'].get('a13'), 'A13 permits only one extension round')
    rows = {k: unseal(v) for k, v in unseal(candidate)['rows'].items()}
    details = {(d['row'], d['setting']): d for d in sidecar['rows']}
    records, chosen, source_jobs, census_jobs, P = [], {}, {}, {}, 0
    source_manifest = unseal(read(Path(source_root) / 'tables_A1_manifest.json'))
    stage_jobs = defaultdict(list)
    for j in original['jobs']:
        stage_jobs[j['config']['a1_job']['id']].append(j)
    for j in source_manifest['jobs']:
        source = a4._load_a1(source_root, j, original['source_code_hash'])
        setting = j['config'].get('setting_name', 'primary')
        plain = source['result']['route'] == 'plain'
        if setting == 'primary' and plain:
            P += len(source['result']['rows'])
        fit = None
        validations = []
        for stage in stage_jobs[j['id']]:
            phase = stage['config']['phase']
            value = completed(Path(run_root) / phase, stage, original['code_hash'])['result']
            if phase == 'fit':
                fit = value
            elif phase == 'validate_plain':
                validations.append(value)
            elif phase == 'census':
                census_jobs[j['id']] = stage
        validations.sort(key=lambda r: r['replicate'])
        if plain:
            require(fit is not None and [v['replicate'] for v in validations] == [1, 2, 3], 'original plain replicates missing')
        params = Context.build(source['result']['kernel'], calibration).parameters
        for i, a1_row in enumerate(source['result']['rows']):
            key = row_key(a1_row)
            ok, info = False, None
            if plain and setting == 'primary':
                ok, info = eligible(rows[key], details[(key, setting)], a1_row, fit['rows'][i],
                                    a4._combine_plain(validations, i), original['M'], params.extinction_flow, params.upper_bound)
            records.append({'row': key, 'setting': setting, 'eligible': bool(ok)})
            if ok:
                chosen.setdefault(j['id'], {})[key] = dict(info, row_index=i)
                source_jobs[j['id']] = (j, fit)
    sources = [j for j, _ in source_jobs.values()]
    pricing = price_extension(original, read(projection_path), sources, registered=registered,
                              projection_file_hash=file_hash(projection_path))
    r_max = pricing['R_max']
    inventory = unseal(read(seed_inventory_path))
    categories = {'registered', 'planning', 'probe', 'rehearsal', 'qualification'}
    require(set(inventory) == categories and all(isinstance(v, list) for v in inventory.values()), 'global seed inventory categories incomplete')
    forbidden = {s for values in inventory.values() for s in values}
    require(all(type(s) is int and s >= 0 for s in forbidden), 'invalid forbidden seed')
    from .table_labels_a5 import forbidden_seeds
    forbidden |= forbidden_seeds([j['seed'] for j in source_manifest['jobs']], receipt['stream_seeds'].values(), ())
    forbidden |= {j['seed'] for j in original['jobs']}
    manifest = seed_manifest(sources, r_max, forbidden, rehearsal=rehearsal)
    E = sum(len(v) for v in chosen.values())
    require(0 <= E <= P <= original['M'], 'invalid A13 error-accounting counts')
    require(math.isfinite(wall_hours) and wall_hours > 0 and math.isfinite(overhead_hours) and overhead_hours >= 0,
            'invalid extension launch allowance')
    core = {'schema': SCHEMA, 'code_hash': code_identity(), 'registered': registered, 'registered_a10': registered,
            'round_record_path': str(scoped(SIMULATION / TARGET).with_suffix('.a13_round.json') if registered
                                     else scoped(output).with_suffix('.round.json')),
            'instrument': original['instrument'], 'registration': registration, 'tag': 'v3_tables', 'round': 1,
            'original_plan_path': str(Path(plan_path).resolve()), 'original_plan_file_sha256': file_hash(plan_path),
            'original_plan_hash': original['plan_hash'], 'original_run_root': str(Path(run_root).resolve()),
            'candidate_path': str(Path(candidate_path).resolve()), 'candidate_file_sha256': file_hash(candidate_path),
            'candidate_sidecar_sha256': file_hash(Path(candidate_path).with_suffix('.cell_results.json')),
            'M': original['M'], 'P': P, 'E': E, 'alpha': cv.ALPHA, 'eligibility': records,
            'pricing': pricing, 'R_max': r_max, 'launch_allowed': r_max >= 6 and E > 0,
            'seed_manifest': manifest, 'seed_check': check_seed_manifest(manifest, forbidden, rehearsal=rehearsal),
            'seed_inventory_sha256': file_hash(seed_inventory_path), 'forbidden_seeds': sorted(forbidden),
            'impossible_rows': {k: p['n_star'] > 2048 * r_max for v in chosen.values() for k, p in v.items()},
            'wall_seconds': wall_hours * 3600, 'x2_equivalent_hours': 15 + overhead_hours,
            'simulation_cap_x2_hours': 15, 'overhead_x2_hours': overhead_hours, 'non_registered_rehearsal': rehearsal,
            'configuration_seconds': 1800, 'cleanup_reserve_seconds': 1200, 'phases': [PHASE], 'publication': None}
    configs = []
    for jid, selected in sorted(chosen.items()):
        j, fit = source_jobs[jid]
        c = {'phase': PHASE, 'route': 'plain', 'a1_source_root': source_root, 'a1_job': j,
             'a1_source_code_hash': original['source_code_hash'], 'fit': seal(fit), 'eligible_rows': selected,
             'R_max': r_max, 'M': original['M'], 'full_seed_manifest': manifest, 'forbidden_seeds': sorted(forbidden),
             'stream_seeds': [r['seed'] for r in manifest if r['source_job_id'] == jid],
             'trajectory_count': 2048, 'non_registered_rehearsal': rehearsal}
        if original.get('settings_override'):
            require(not registered, 'registered extension cannot override settings')
            c['settings_override'] = original['settings_override']
            c['trajectory_count'] = c['settings_override']['groups'] * c['settings_override']['runs_per_group']
        configs.append(c)
    core['job_skeletons'] = configs
    core['plan_hash'] = digest(core)
    core['jobs'] = [stable_job(KIND, dict(c, plan_hash=core['plan_hash']), 'v3_tables', i) for i, c in enumerate(configs)]
    core['memory_estimate_gb'] = {PHASE: original['memory_estimate_gb']['validate_plain']}
    profile_configs = []
    for i, c in enumerate(configs):
        short = dict(c, plan_hash=core['plan_hash'], configuration_test=True,
                     settings_override={**c.get('settings_override', {}), 'burn': 30, 'measure': 8},
                     seed=(1 << 128) | int(digest(['A13-configuration', core['plan_hash'], i])[:32], 16))
        profile_configs.append(short)
    core['configuration'] = {PHASE: {'kind': KIND, 'config': profile_configs[0], 'configs': profile_configs,
                                    'workers_local': [2, 4, 8, 12], 'workers_x2': [8, 12, 16, 24, 32],
                                    'threads': [1], 'rounds': 1, 'jobs_local': 12, 'jobs_x2': 32,
                                    'jobs_per_worker': 2}} if configs else {}
    if registered:
        reserve_registered_round(core, output)
    atomic_json(output, seal(core))
    atomic_json(Path(output).with_suffix('.public.json'), seal(public_record(core)))
    return core


def plan_hash(plan):
    omitted = {'plan_hash', 'jobs', 'configuration', 'memory_estimate_gb', 'pull_dispatch'}
    return digest({k: v for k, v in plan.items() if k not in omitted})


def validate_plan(plan, *, launching=False):
    require(plan['schema'] == SCHEMA and plan['round'] == 1 and plan_hash(plan) == plan['plan_hash'], 'A13 plan changed')
    require(plan['code_hash'] == code_identity(), 'A13 plan source changed')
    require(plan['registered'] != bool(plan.get('non_registered_rehearsal')), 'exactly one of registered or rehearsal is required')
    round_record_path(plan)
    require(plan['seed_check'] == check_seed_manifest(plan['seed_manifest'], plan['forbidden_seeds'], rehearsal=plan.get('non_registered_rehearsal', False)), 'A13 seed check changed')
    require(plan['jobs'] == [stable_job(KIND, dict(c, plan_hash=plan['plan_hash']), 'v3_tables', i)
                             for i, c in enumerate(plan['job_skeletons'])], 'A13 job skeleton changed')
    require(all(c['M'] == plan['M'] for c in plan['job_skeletons']), 'extension M differs from pinned plan')
    if 'pull_dispatch' in plan:
        require(plan['pull_dispatch']['projection_sha256'] == plan['pricing']['projection_sha256'], 'extension dispatch projection differs from pricing')
    if launching:
        require(plan['launch_allowed'] and plan['R_max'] >= 6, 'extension no-launch floor or empty eligible set')
        require(file_hash(plan['original_plan_path']) == plan['original_plan_file_sha256'], 'sealed original plan changed before launch')
        original = unseal(read(plan['original_plan_path']))
        require(original['M'] == plan['M'] and original['plan_hash'] == plan['original_plan_hash'], 'original pinned M or plan changed')
        require(original['pull_dispatch']['projection_sha256'] == plan['pricing']['projection_sha256'], 'original projection binding changed')
    return plan


def round_record_path(plan):
    """Registered rounds belong to the family, independent of plan filenames."""
    path = scoped(plan['round_record_path'])
    if plan['registered']:
        require(path == scoped(SIMULATION / TARGET).with_suffix('.a13_round.json'),
                'A13 registered round requires the family anchor')
    return path


def reserve_registered_round(plan, output):
    """Freeze the family's only preparation before writing its plan file."""
    require(plan['registered'], 'A13 family reservation requires a registered plan')
    path = round_record_path(plan)
    prepared_path = str(scoped(output))
    with lease(path.with_suffix('.lock')):
        if path.exists():
            record = unseal(read(path))
            require(record['plan_hash'] == plan['plan_hash'], 'A13 family round already reserved for another plan')
            require(record['prepared_plan_path'] == prepared_path, 'A13 family plan already prepared at another output')
            require(record['root'] is None and not record['halt'], 'A13 family round already launched or spent')
        else:
            record = dict(schema='v3-A13-round-1', plan_hash=plan['plan_hash'], prepared_plan_path=prepared_path,
                          spec_hash=None, root=None, halt=None)
            atomic_json(path, seal(record))


def begin_round(plan, plan_path, root):
    """Bind the only round to its frozen plan and root before any dispatch."""
    root = scoped(root)
    path = round_record_path(plan)
    require(unseal(read(scoped(plan_path))) == plan, 'A13 launch differs from its frozen plan')
    # freeze() may write the pull plan to another filename. Its hashed anchor
    # stays the family anchor for registered plans, even when the plan is copied.
    identity = dict(schema='v3-A13-round-1', plan_hash=plan['plan_hash'], spec_hash=digest(plan), root=str(root))
    with lease(path.with_suffix('.lock')):
        require(path.exists() or not plan['registered'], 'A13 registered round was not reserved at preparation')
        record = unseal(read(path)) if path.exists() else dict(identity, halt=None)
        require(record['schema'] == identity['schema'] and record['plan_hash'] == identity['plan_hash'],
                'A13 round already bound to another root or plan')
        require((record['root'] is None and record['spec_hash'] is None)
                or all(record.get(k) == v for k, v in identity.items()), 'A13 round already bound to another root or plan')
        require(not record['halt'], 'A13 scientific halt is final; round spent')
        record.update(identity)
        atomic_json(path, seal(record))
        atomic_json(root / 'a13_round.json', seal(dict(identity, round_record_path=str(path))))
    # An interrupted halt write may leave the root marker ahead of the round record.
    if round_halt(root):
        raise ValueError('A13 scientific halt is final; round spent')
    return record


def latch_round_halt(root, reason):
    """Persist a scientific halt outside the launch root, including worker halts."""
    pointer = Path(root) / 'a13_round.json'
    if not pointer.exists():
        return  # Standalone synthetic/configuration workers have no launched round.
    ref = unseal(read(pointer))
    path = scoped(ref['round_record_path'])
    with lease(path.with_suffix('.lock')):
        record = unseal(read(path))
        require(all(record.get(k) == ref[k] for k in ('plan_hash', 'spec_hash', 'root'))
                and Path(record['root']) == scoped(root), 'A13 round reference mismatch')
        if not record['halt']:
            record['halt'] = str(reason)
            atomic_json(path, seal(record))


def round_halt(root):
    """Recover a latch after interruption without trusting a new launch root."""
    root = Path(root)
    halted = any(p.exists() for p in (root / 'a13_scientific_halt.json', root / 'nondeterminism_failure.json',
                                      root / PHASE / 'nondeterminism_failure.json'))
    if (root / 'dispatch.sqlite').exists() or (root / 'pull_state.json').exists():
        from .dispatch_store_a11 import read_state
        halted |= bool(read_state(root).get('halt'))
    if halted:
        latch_round_halt(root, 'scientific halt')
    return halted


def publication_round(plan, root):
    """Only a completed, checked round may certify; a halt sends all rows to Part 2."""
    if not plan['launch_allowed'] and not plan['registered']:
        return False
    path = round_record_path(plan)
    require(path.exists(), 'A13 publication requires its recorded round')
    record = unseal(read(path))
    require(record['plan_hash'] == plan['plan_hash'], 'A13 round plan mismatch')
    if not plan['launch_allowed']:
        return bool(record['halt'])
    require(record['spec_hash'] == digest(plan), 'A13 round plan mismatch')
    require(Path(record['root']) == root, 'A13 publication requires the recorded root')
    require((root / 'identity.json').exists() and read(root / 'identity.json') ==
            dict(spec_hash=digest(plan), code_hash=plan['code_hash']), 'A13 launch identity mismatch')
    round_halt(root)
    if unseal(read(path))['halt']:
        return True  # Item 7: never inspect or certify any trajectory from this round.
    history = read(root / 'launches.json') if (root / 'launches.json').exists() else []
    require(bool(history) and history[-1].get('complete') is True, 'A13 last launch is not complete')
    check_path = root / PHASE / 'nondeterminism_check.json'
    check = read(check_path) if check_path.exists() else {}
    require(check.get('matched') is True and check.get('checked') in {j['id'] for j in plan['jobs']},
            'A13 publication requires a passed nondeterminism check')
    if 'pull_dispatch' in plan:
        from .dispatch_store_a11 import read_state
        state = read_state(root)
        require(state.get('complete') is True and state.get('checks', {}).get(PHASE) == check,
                'A13 publication requires the completed pull-dispatch check')
    return False


def public_record(plan):
    return {'amendment': 'A13, informed by an outcome', 'original_refusal_preserved': True,
            'round': 1, 'plan_hash': plan['plan_hash'], 'eligibility': plan['eligibility'],
            'source_jobs': [c['a1_job']['id'] for c in plan['job_skeletons']],
            'E': plan['E'], 'P': plan['P'], 'M': plan['M'], 'alpha': plan['alpha'],
            'family_error_bound_given_fit': plan['alpha'] * (1 + plan['P'] / plan['M']),
            'conditional_additional_error_bound': plan['alpha'] * plan['E'] / plan['M'],
            'R_max': plan['R_max'], 'projected_x2_hours': plan['pricing']['projected_x2_hours'],
            'impossible_rows': plan['impossible_rows'], 'seed_manifest': plan['seed_manifest'],
            'seed_check': plan['seed_check']}


def assert_ineligible_identity(before_rows, after_rows, before_details, after_details, eligible_keys):
    require(set(before_rows) == set(after_rows), 'A13 changed the primary row set')
    for key in before_rows:
        if key not in eligible_keys:
            require(canonical(before_rows[key]) == canonical(after_rows[key]), 'ineligible row is not byte-identical')
    require(len(before_details) == len(after_details), 'A13 changed the sidecar row set')
    for before, after in zip(before_details, after_details):
        require((before['row'], before['setting']) == (after['row'], after['setting']), 'A13 changed sidecar order')
        if before['row'] not in eligible_keys or before['setting'] != 'primary':
            require(canonical(before) == canonical(after), 'ineligible sidecar entry is not byte-identical')


def reassemble(rows, details, selected, tests, fits, censuses):
    after, sidecar = deepcopy(rows), deepcopy(details)
    index = {(d['row'], d['setting']): d for d in sidecar}
    for key, info in selected.items():
        row, detail, test = after[key], index[(key, 'primary')], tests[key]
        passed = test['status'] == 'certified' and test['visit_weighted_ok']
        c0 = fits[key]
        row['c0'] = {'value': c0['value'], 'error': max(c0['value'] - info['lower'], info['upper'] - c0['value'])} if passed else None
        support = {int(cv.fine_codes([e['bin']])[0]) for e in row['continuation']['entries']}
        if passed:
            support.add(int(cv.POP0_CELL))
        fractions = cv.census_fractions_from_counts(censuses[key], support, 'plain')
        floor = cv.census_floor(fractions)
        row['a4']['validated_support_size'] = len(support)
        row['a4']['census'] = {k: fractions[k] for k in row['a4']['census']}
        row['a4']['floor'] = {k: floor[k] for k in row['a4']['floor']}
        estimated = passed and floor['passed']
        row['status'] = row['primary_status'] = 'estimated' if estimated else 'not_estimable'
        row['primary_reason'] = None if estimated else 'A4 availability floor failed'
        if estimated:
            row.pop('reason', None)
        else:
            row['reason'] = 'A4 availability floor failed'
        row['a13'] = {'certified_by_extension': bool(estimated), 'retest': {k: test[k] for k in ('status', 'visit_weighted_ok')}}
        replacement = {'cell': int(cv.POP0_CELL), 'eb': test['status'], 'visit_weighted_ok': test['visit_weighted_ok'],
                       'n_traj': test['n'], 'published_and_passed': bool(passed), 'a13_extension': True}
        original = next((i for i, t in enumerate(detail['cell_tests']) if t['cell'] == cv.POP0_CELL), None)
        if original is None:
            detail['cell_tests'].append(replacement)
        else:
            detail['cell_tests'][original] = replacement
        detail.update(status=row['status'], floor=floor)
    assert_ineligible_identity(rows, after, details, sidecar, set(selected))
    return after, sidecar


def publish(plan, extension_root, target, *, registered=True):
    from .artifacts import verify_registration
    from .production_runner import completed
    from .production_tables import ProductionTables
    from .admission_a13 import checked_binding
    validate_plan(plan)
    if registered:
        require(plan['registered'], 'registered A13 publication requires registered plan')
        verify_registration(plan['registration'], instrument=plan['instrument'])
        require(Path(target).resolve() == (SIMULATION / TARGET).resolve(), 'A13 requires the exact configured publication target')
    require(file_hash(plan['original_plan_path']) == plan['original_plan_file_sha256']
            and file_hash(plan['candidate_path']) == plan['candidate_file_sha256']
            and file_hash(Path(plan['candidate_path']).with_suffix('.cell_results.json')) == plan['candidate_sidecar_sha256'],
            'A13 original inputs changed')
    original, candidate, sidecar, receipt, _ = original_inputs(plan['original_plan_path'], plan['original_run_root'],
                                                              plan['candidate_path'], registered=registered)
    require(original['M'] == plan['M'], 'extension M differs from original plan')
    extension_root = scoped(extension_root)
    halted = publication_round(plan, extension_root)
    selected, tests, fits, censuses, hashes = {}, {}, {}, {}, {}
    for job in plan['jobs']:
        c = job['config']
        result = None
        if plan['launch_allowed'] and not halted:
            output = completed(extension_root / PHASE, job, plan['code_hash'])
            require(output is not None, 'extension incomplete; infrastructure interruption must resume')
            result = output['result']
            require(result['plan_hash'] == plan['plan_hash'] and result['a1_job_id'] == c['a1_job']['id'], 'extension result identity mismatch')
            validate_replicates(job, result['replicates'])
            require(len(result['replicates']) == c['R_max'] or stop_reached(result['replicates'], c['eligible_rows']), 'extension stopped early')
            hashes[job['id']] = file_hash(extension_root / PHASE / 'outputs' / (job['id'] + '.json'))
        census_job = next(j for j in original['jobs'] if j['config']['phase'] == 'census' and j['config']['a1_job']['id'] == c['a1_job']['id'])
        census = completed(Path(plan['original_run_root']) / 'census', census_job, original['code_hash'])['result']['cell_counts']
        for key, info in c['eligible_rows'].items():
            selected[key] = info
            tests[key] = extension_test([{'replicate': r['replicate'], 'trajectories': r['rows'][key]}
                                        for r in result['replicates']], info) if result else {
                'status': 'unresolved', 'reason': 'scientific halt' if halted else 'extension not launched', 'n': 0, 'visit_weighted_ok': False}
            fits[key] = unseal(c['fit'])['rows'][info['row_index']]['c0']
            censuses[key] = census
    payload = deepcopy(unseal(candidate))
    rows = {k: unseal(v) for k, v in payload['rows'].items()}
    after, details = reassemble(rows, sidecar['rows'], selected, tests, fits, censuses)
    admission = checked_binding(after, details, 'A10_nominal_after_A13',
                                Path(plan['round_record_path']).with_suffix('.admission.json'), plan['plan_hash'])
    summary = public_record(plan)
    summary['outcome'] = 'scientific_halt' if halted else 'completed' if plan['launch_allowed'] else 'not_launched'
    payload['manifest']['a13'] = summary
    payload['manifest']['a13_admission'] = admission
    payload['rows'] = {k: seal(v) for k, v in after.items()}
    payload['code_hash'] = code_identity()
    payload['fixture'] = not registered
    payload['manifest_hash'] = digest(payload['manifest'])
    document = seal(payload)
    sidecar_doc = seal(dict(sidecar, table_seal_sha256=document['sha256'], rows=details, a13=summary))
    amended = dict(receipt, table_seal_sha256=document['sha256'],
                   table_file_sha256=hashlib.sha256(canonical(document) + b'\n').hexdigest(), producer_code_hash=code_identity(),
                   cell_results_sha256=hashlib.sha256(canonical(sidecar_doc) + b'\n').hexdigest(),
                   a13=summary, extension_plan_hash=plan['plan_hash'], extension_stage_output_sha256=hashes,
                   extension_seed_manifest=plan['seed_manifest'],
                   original_refusal={'table_file_sha256': plan['candidate_file_sha256'],
                                     'sidecar_file_sha256': plan['candidate_sidecar_sha256']})
    require(amended['plan_hash'] == receipt['plan_hash'] and amended['stream_seeds'] == receipt['stream_seeds'], 'original receipt fields changed')
    if registered:
        ProductionTables(document, calibration_hash=payload['manifest']['calibration_hash'], registered=True)
    target = scoped(target)
    if target.exists() and read(target) != document:
        raise RuntimeError('A4 table target is frozen; publish a new path')
    # Ineligible row/sidecar bytes are checked again on the exact serialized form.
    assert_ineligible_identity(rows, {k: unseal(v) for k, v in document['payload']['rows'].items()}, sidecar['rows'], details, set(selected))
    require(publication_round(plan, extension_root) == halted, 'A13 halt arrived during publication; reassess every eligible row under Part 2')
    atomic_json(target.with_suffix('.compatibility.json'), seal(amended))
    atomic_json(target.with_suffix('.cell_results.json'), sidecar_doc)
    atomic_json(target, document)
    return summary


def main():
    p = argparse.ArgumentParser(__doc__)
    sub = p.add_subparsers(dest='command', required=True)
    prepare_parser = sub.add_parser('prepare')
    for name in ('original_plan', 'original_root', 'candidate', 'projection', 'seed_inventory', 'output'):
        prepare_parser.add_argument(name)
    prepare_parser.add_argument('--registration')
    prepare_parser.add_argument('--rehearsal', action='store_true')
    prepare_parser.add_argument('--wall-hours', type=float, required=True)
    prepare_parser.add_argument('--overhead-hours', type=float, required=True)
    pub = sub.add_parser('publish')
    pub.add_argument('plan'); pub.add_argument('root'); pub.add_argument('target')
    pub.add_argument('--fixture', action='store_true')
    args = p.parse_args()
    if args.command == 'prepare':
        plan = prepare(args.original_plan, args.original_root, args.candidate, args.projection, args.seed_inventory,
                       args.output, registration=read(args.registration) if args.registration else None,
                       wall_hours=args.wall_hours, overhead_hours=args.overhead_hours, rehearsal=args.rehearsal)
        print(canonical({'R_max': plan['R_max'], 'projected_x2_hours': plan['pricing']['projected_x2_hours']}).decode())
    else:
        summary = publish(unseal(read(args.plan)), args.root, args.target, registered=not args.fixture)
        print(canonical({'published': True, 'E': summary['E'], 'P': summary['P'], 'M': summary['M']}).decode())


if __name__ == '__main__':
    main()
