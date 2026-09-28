"""D24 mixed-family provenance. This admits no additional scientific failures.

The committed policy pins all A1 output hashes and the exact replacement set.
The publication-specific sealed receipt pins the new table bytes, replacement
outputs, committed producer and full manifest. No future hash is invented.
"""
from copy import deepcopy
from pathlib import Path
import subprocess
import time
from .artifacts import (ROOT, SIMULATION, read, seal, unseal, digest, file_hash,
                        atomic_json, code_identity, stable_job)

FAMILY_ROOT = ROOT / 'runs/A3_families'


def family_directory(p=None):
    return FAMILY_ROOT / digest(policy() if p is None else p)


def refuse_family_failure(p=None):
    path = family_directory(p) / 'failure.json'
    if path.exists():
        raise RuntimeError('A3 family screen failure is latched: ' + str(path))


def record_family_failure(p, failure, run_root):
    path = family_directory(p) / 'failure.json'
    if not path.exists():
        atomic_json(path, {'policy_sha256': digest(p), 'epoch': time.time(),
                           'run_root': str(Path(run_root).resolve()), 'failure': failure})


def producer_is_ancestor(commit):
    if not isinstance(commit, str) or len(commit) != 40 or any(c not in '0123456789abcdef' for c in commit):
        return False
    return subprocess.run(['git', 'merge-base', '--is-ancestor', commit, 'HEAD'],
                          cwd=SIMULATION.parent, capture_output=True).returncode == 0


def policy():
    return read(ROOT / 'table_compatibility_A3.json')


def producer_commit():
    return subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=SIMULATION.parent).decode().strip()


def config_identity(config):
    return digest({k: v for k, v in config.items() if k != 'calibration_path'})


def validate_plan(spec):
    p, plan = policy(), spec['repair']
    for key in ('source_file_sha256', 'source_payload_sha256', 'source_manifest_sha256',
                'source_code_hash', 'calibration_sha256', 'source_outputs', 'dispatch_order'):
        if plan[key] != p[key]:
            raise ValueError('A3 provenance policy mismatch: ' + key)
    if (plan['population_factor'] != 8 or spec.get('publication') is not None or
            set(plan['replacements']) != set(p['replacement_source_ids']) or
            len(spec['jobs']) != len(p['replacement_source_ids']) or
            [j['config']['source_job_id'] for j in spec['jobs']] != [j['source_job_id'] for j in p['dispatch_order']] or
            spec.get('completion_screen', {}).get('kind') != 'A3-first-failure' or
            not spec['completion_screen'].get('source_root') or
            spec['wall_seconds'] > p['maximum_remaining_seconds']):
        raise ValueError('A3 fixed set, order, stop policy or budget changed')
    for job in spec['jobs']:
        identity = p['replacement_jobs'][job['config']['source_job_id']]
        if (job['config']['calibration_path'] != p['canonical_calibration_path'] or
                job['id'] != identity['id'] or job['seed'] != identity['seed']):
            raise ValueError('A3 pinned job ID, seed or canonical calibration path changed')
        config = deepcopy(job['config'])
        old = config.pop('source_job_id')
        if config.pop('repair_round') != 'A3-fixed-once-20260928':
            raise ValueError('A3 repair round changed')
        for key in ('particles', 'runs_per_group'):
            if config['settings'][key] % 8:
                raise ValueError('A3 population changed')
            config['settings'][key] //= 8
        if (config_identity(config) != p['source_config_hashes'][old] or
                stable_job('table', job['config'], 'v3_tables', 0) != job or
                plan['replacements'][old] != job['id']):
            raise ValueError('A3 replacement configuration or seed changed')
    return p


def publication_receipt(path, document, spec, replacements, run_root):
    p = validate_plan(spec)
    retained = {k: v for k, v in p['source_outputs'].items() if k not in p['replacement_source_ids']}
    receipt = {'schema': 'v3-A3-publication-compatibility-1', 'policy_sha256': digest(p),
               'producer_commit': producer_commit(), 'producer_code_hash': code_identity(),
               'table_file_sha256': file_hash(path), 'table_seal_sha256': document['sha256'],
               'spec': spec, 'retained_A1_outputs': retained,
               'replacement_outputs': {old: {'job': o['job'], 'code_hash': o['code_hash'],
                   'output_sha256': file_hash(Path(run_root) / 'table/outputs' / (o['job']['id'] + '.json'))}
                   for old, o in replacements.items()}}
    atomic_json(Path(path).with_suffix('.compatibility.json'), seal(receipt))


def require_compatible(path, document):
    if not isinstance(path, (str, Path)):
        raise ValueError('A3 publication requires its exact file and compatibility receipt')
    rec = unseal(read(Path(path).with_suffix('.compatibility.json')))
    p = validate_plan(rec['spec'])
    manifest = document['payload']['manifest']
    replaced = rec['replacement_outputs']
    retained = {k: v for k, v in p['source_outputs'].items() if k not in p['replacement_source_ids']}
    if (rec['schema'] != 'v3-A3-publication-compatibility-1' or rec['policy_sha256'] != digest(p) or
            not producer_is_ancestor(rec['producer_commit']) or rec['producer_code_hash'] != code_identity() or
            document['payload']['code_hash'] != code_identity() or
            rec['table_file_sha256'] != file_hash(path) or rec['table_seal_sha256'] != document['sha256'] or
            rec['retained_A1_outputs'] != retained or set(replaced) != set(p['replacement_source_ids']) or
            manifest['repair'] != rec['spec']['repair'] or manifest['calibration_hash'] != p['calibration_sha256'] or
            manifest['source_family'] != {'file_sha256': p['source_file_sha256'], 'code_hash': p['source_code_hash']} or
            manifest['replacement_output_hashes'] != {k: v['output_sha256'] for k, v in replaced.items()}):
        raise ValueError('A3 mixed-family compatibility mismatch')
    jobs = {j['config']['source_job_id']: j for j in rec['spec']['jobs']}
    for old, output in replaced.items():
        if output['job'] != jobs[old] or output['code_hash'] != code_identity() or len(output['output_sha256']) != 64:
            raise ValueError('A3 replacement producer or job mismatch')
    return rec
