"""Isolated, read-only execution of A14's three frozen assessment scripts."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import shutil
import platform

from .artifacts import SIMULATION, atomic_json, file_hash, read, scoped, seal, unseal

COMMIT = '55817036'
SCRIPTS = {
    'feasibility.py': 'b2abd1e3fb0ae0e90193f12171eb7633cf4180163ca0bea57e37e8df6667b5e7',
    'feas_sens.py': 'e99671d2c43a150d4d31286e379392e5801a3983effa9a22f13e707a72be3fd7',
    'feas_extra_full.py': '3fb75616f072123d62a7a60e74366c03261a36267c0b6ecf8fa8b74434051a4a'}


def stage_source(directory):
    """Explicit staging step; forecast() itself writes no source or input."""
    directory = scoped(directory)
    if directory.exists():
        raise ValueError('forecast source view already exists')
    repo = SIMULATION.parent
    names = subprocess.run(['git', '-C', str(repo), 'ls-tree', '-r', '--name-only', COMMIT,
                            'simulation'], check=True, capture_output=True, text=True).stdout.splitlines()
    names = [n for n in names if (n.endswith('.py') and not Path(n).name.startswith('test_')
             and len(Path(n).parts) == (3 if n.startswith('simulation/v3/') else 2))
             or n in ('simulation/v3/a10_constants.json', 'simulation/v3/calibration_compatibility_A1.json',
                      'simulation/v3/table_compatibility_A2.json', 'simulation/v3/table_compatibility_A3.json')]
    files = {}
    for name in names:
        data = subprocess.run(['git', '-C', str(repo), 'show', COMMIT + ':' + name],
                              check=True, capture_output=True).stdout
        target = directory / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        target.chmod(0o444)
        files[name] = hashlib.sha256(data).hexdigest()
    atomic_json(directory / 'source.json', seal(dict(commit=COMMIT, files=files)))
    (directory / 'source.json').chmod(0o444)
    return directory


def verified_source(directory):
    directory = Path(directory).resolve()
    manifest = unseal(read(directory / 'source.json'))
    if manifest['commit'] != COMMIT:
        raise ValueError('forecast source commit differs')
    actual = {p.relative_to(directory).as_posix() for p in directory.rglob('*')
              if p.is_file() and p.name != 'source.json'}
    if actual != set(manifest['files']):
        raise ValueError('undeclared forecast source or A14 module reachable')
    for name, sha in manifest['files'].items():
        if '..' in Path(name).parts or Path(name).is_absolute() or not name.startswith('simulation/'):
            raise ValueError('unsafe forecast source path')
        committed = subprocess.run(['git', '-C', str(SIMULATION.parent), 'show', COMMIT + ':' + name],
                                   check=True, capture_output=True).stdout
        if hashlib.sha256(committed).hexdigest() != sha or file_hash(directory / name) != sha:
            raise ValueError('forecast source differs from its git blob')
    return {str((directory / n).resolve()): h for n, h in manifest['files'].items()}


FINDING_EXIT = 78


def validate_configuration(configuration, *, registered):
    """Operator/source/environment checks only, before registered entry."""
    config = unseal(read(configuration)) if isinstance(configuration, (str, Path)) else unseal(configuration)
    required = {'registered', 'source_view', 'scripts', 'python', 'numpy'}
    if not required <= set(config) or type(config['registered']) is not bool or config['registered'] != registered:
        raise ValueError('forecast configuration or registration intent differs')
    if registered and platform.node().lower() != 'yotko-evo-x2':
        raise ValueError('registered A14 forecast must run on X2-1')
    if not isinstance(config.get('package_paths', []), list):
        raise ValueError('forecast package_paths must be a list')
    packages = [Path(p).resolve() for p in config.get('package_paths', [])]
    if any(not p.is_dir() or p.name not in ('site-packages', 'dist-packages')
           or p.is_relative_to(SIMULATION.parent) or (p / 'v3').exists()
           or (p / 'validation_extension_a14.py').exists() for p in packages):
        raise ValueError('A14 source reachable through declared environment path')
    sources = verified_source(config['source_view'])
    scripts = {str((Path(config['scripts']) / name).resolve()): sha for name, sha in SCRIPTS.items()}
    if any(file_hash(path) != sha for path, sha in scripts.items()):
        raise ValueError('forecast script hash differs')
    executable = shutil.which(str(config.get('python_executable', sys.executable)))
    if executable is None or not Path(executable).is_file():
        raise ValueError('forecast interpreter does not exist')
    probe = "import sys,json,platform; sys.path.extend(json.loads(sys.argv[1])); import numpy; print(json.dumps(dict(python=platform.python_version(),numpy=numpy.__version__)))"
    checked = subprocess.run([executable, '-I', '-B', '-c', probe, json.dumps([str(p) for p in packages])],
                             capture_output=True, text=True, check=False)
    if checked.returncode:
        raise OSError('forecast interpreter version probe failed')
    try:
        actual = json.loads(checked.stdout)
    except (ValueError, TypeError) as exc:
        raise OSError('forecast interpreter version probe returned invalid metadata') from exc
    declared = {k: config[k] for k in ('python', 'numpy')}
    if actual != declared:
        raise ValueError('forecast interpreter does not report its declared versions')
    return dict(config=config, executable=executable, packages=[str(p) for p in packages],
                sources=sources, scripts=scripts, declared_environment=declared, actual_environment=actual)


# Executed with -I -B in a separate interpreter. It imports no current package.
CHILD = r'''
import sys
class Finding(Exception): pass
try:
    import sys, os, json, hashlib, io, contextlib, platform, pathlib, importlib, importlib.util
    cfg = json.load(sys.stdin)
    view = pathlib.Path(cfg['source_view']).resolve()
    environment = pathlib.Path(sys.prefix).resolve()
    environment_roots = [environment] + [pathlib.Path(p).resolve() for p in cfg['package_paths']]
    source_files = cfg['source_files']
    data_files = set(cfg['paths'].values())
    scripts = cfg['scripts']
    absent_caches = {str(pathlib.Path(importlib.util.cache_from_source(p)).resolve())
                     for p in source_files if p.endswith('.py')}
    def inside(path, root):
        return path == root or root in path.parents
    def safe_import_path(value):
        p = pathlib.Path(value).resolve()
        return p == view / 'simulation' or any(inside(p, root) for root in environment_roots) or (
            p.suffix == '.zip' and p.parent == pathlib.Path(sys.base_prefix).resolve())
    sys.path[:] = [p for p in sys.path if p and safe_import_path(p)]
    sys.path.extend(str(p) for p in environment_roots[1:] if str(p) not in sys.path)
    sys.path.insert(0, str(view / 'simulation'))
    os.chdir(view / 'simulation')
    os.environ['EXT'] = cfg['ext']
    os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
    sys.dont_write_bytecode = True
    checking = False
    def audit(event, args):
        global checking
        if checking:
            return
        if event == 'open':
            name, mode, flags = args
            if isinstance(name, int):
                return
            p = pathlib.Path(name).resolve()
            if (mode and any(c in mode for c in 'wax+')) or flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC):
                raise Finding('forecast attempted a write')
            if str(p) in absent_caches and not p.exists():
                return  # Importlib probes an absent cache before reading verified source.
            if str(p) not in source_files and str(p) not in data_files and str(p) not in scripts and not any(inside(p, r) for r in environment_roots):
                raise Finding('finding: forecast read is unmapped')
        if event == 'exec':
            filename = args[0].co_filename
            if filename.startswith('<'):
                return
            p = pathlib.Path(filename).resolve()
            if str(p) in source_files:
                checking = True
                try:
                    if hashlib.sha256(p.read_bytes()).hexdigest() != source_files[str(p)]:
                        raise Finding('forecast repository import changed')
                finally:
                    checking = False
            elif str(p) not in scripts and not any(inside(p, r) for r in environment_roots):
                raise Finding('A14/current repository import is reachable')
    sys.addaudithook(audit)
    repository_names = {'v3'} | {pathlib.Path(p).stem for p in source_files
                                if pathlib.Path(p).parent == view / 'simulation' and p.endswith('.py')}
    for name in sorted(repository_names):
        spec = importlib.util.find_spec(name)
        if spec is None or str(pathlib.Path(spec.origin).resolve()) not in source_files:
            raise Finding('repository import resolution escaped the verified source view')
    for name in ('validation_extension_a14', 'history_a14', 'forecast_a14', 'replay_a14'):
        if any(importlib.util.find_spec(prefix + name) is not None for prefix in ('', 'v3.')):
            raise Finding('A14 module reachable through import resolution')
    from v3 import artifacts
    def mapped(path):
        key = str(pathlib.Path(path).resolve())
        if key in cfg['paths']:
            return pathlib.Path(cfg['paths'][key])
        if key in data_files:
            return pathlib.Path(key)
        if key in source_files:
            return pathlib.Path(key)
        raise Finding('finding: forecast input path is unmapped')
    artifacts.input_path = mapped
    import numpy
    numbers = None
    for filename, expected in scripts.items():
        raw = pathlib.Path(filename).read_bytes()
        if hashlib.sha256(raw).hexdigest() != expected:
            raise Finding('forecast script hash differs')
        if cfg.get('check_only'):
            continue  # Hash/import audit only: never execute an assessment script.
        namespace = {'__name__': '__main__', '__file__': filename}
        with contextlib.redirect_stdout(io.StringIO()):
            exec(compile(raw, filename, 'exec'), namespace)
        if set(namespace['re_elig_A']) != set(cfg['eligible']):
            raise Finding('finding: case A eligibility differs')
        if pathlib.Path(filename).name == 'feasibility.py':
            numbers = [namespace['round2'](cfg['R_max'], 'A', namespace['p_cert'], namespace['p_viol'])['p_all_part2'],
                       namespace['round2'](cfg['R_max'], 'A', .9, 0.)['p_all_part2']]
    if any(not safe_import_path(p) for p in sys.path):
        raise Finding('forecast sys.path escaped frozen view/environment')
    imports = {}
    for name, module in tuple(sys.modules.items()):
        filename = getattr(module, '__file__', None)
        if not filename or filename.startswith('<'):
            continue
        p = pathlib.Path(filename).resolve()
        if name.split('.')[0] in repository_names and str(p) not in source_files:
            raise Finding('repository-owned transitive import is outside the verified view')
        if str(p) in source_files:
            imports[name] = source_files[str(p)]
        elif not any(inside(p, r) for r in environment_roots):
            raise Finding('forecast imported a module outside its frozen environment')
    result = {'repository_imports': imports, 'python': platform.python_version(),
              'numpy': numpy.__version__, 'environment': [str(p) for p in environment_roots]}
    if cfg.get('check_only'):
        result['checks_only'] = True
    else:
        result.update(p_all_part2=numbers[0], p_all_part2_certification_0_9=numbers[1])
    print(json.dumps(result))
except Finding as exc:
    print(str(exc), file=sys.stderr)
    raise SystemExit(78)
'''


def check_case_a(verified, eligible):
    """Compare statuses/sets only, with no forecast or probability calculation."""
    rows, _ = __import__('v3.validation_extension_a13', fromlist=['reassemble']).reassemble(
        verified['rows'], verified['details'], verified['selected'], verified['tests'], verified['fits'], verified['censuses'])
    case_a = {k for k, t in verified['tests'].items()
              if rows[k]['status'] == 'not_estimable' and t['status'] == 'unresolved'}
    if case_a != set(eligible) or set(eligible) != {k for k, ok in verified['eligible'].items() if ok}:
        raise ValueError('finding: forecast case A differs from frozen eligible set')


def layout_payload(verified, validated):
    """Bind the historical EXT layout and the already-verified tooling."""
    h, config = verified['history'], validated['config']
    ext = str(Path(h.role('a13_plan')).parent)
    if str(Path(h.role('a13_root'))) != str(Path(ext) / 'root') or Path(h.role('a13_plan')).name != 'plan.json':
        raise ValueError('finding: forecast EXT layout is unmapped')
    return dict(source_view=str(Path(config['source_view']).resolve()), source_files=validated['sources'], paths=h.paths,
                scripts=validated['scripts'], ext=ext, python=config['python'], numpy=config['numpy'],
                package_paths=validated['packages'])


def child_result(payload, validated):
    completed = subprocess.run([validated['executable'], '-I', '-B', '-c', CHILD],
                               input=json.dumps(payload), capture_output=True, text=True,
                               env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'}, check=False)
    if completed.returncode == FINDING_EXIT:
        raise ValueError('forecast finding: ' + completed.stderr)
    if completed.returncode:
        raise OSError('forecast infrastructure interruption: ' + str(completed.returncode))
    try:
        result = json.loads(completed.stdout)
        actual = {k: result[k] for k in ('python', 'numpy')}
    except (ValueError, KeyError, TypeError) as exc:
        raise OSError('forecast returned invalid executor metadata') from exc
    return result, actual


def check_preentry_layout(verified, validated):
    """Check layout, script hashes and isolated imports without executing scripts."""
    payload = layout_payload(verified, validated)
    payload['check_only'] = True
    result, _ = child_result(payload, validated)
    if result.get('checks_only') is not True or any(k.startswith('p_all_part2') for k in result):
        raise ValueError('forecast pre-entry check returned probability output')
    return result


def forecast(history_document, r_max, eligible, configuration, *, registered=None, validated=None):
    from .history_a14 import verify_history
    if validated is None:
        raw = unseal(read(configuration)) if isinstance(configuration, (str, Path)) else unseal(configuration)
        validated = validate_configuration(configuration, registered=raw['registered'] if registered is None else registered)
    verified = verify_history(history_document, registered=bool(validated['config']['registered']))
    # Check case A before the unchanged scripts can compute their other curves.
    check_case_a(verified, eligible)
    payload = layout_payload(verified, validated)
    payload.update(eligible=eligible, R_max=r_max)
    result, actual = child_result(payload, validated)
    result.update(source_commit=COMMIT, scripts=SCRIPTS, wrapper_sha256=file_hash(__file__),
                  declared_environment=validated['declared_environment'], actual_environment=actual,
                  a13_environment=verified['environment'], environment_matches_a13=actual == verified['environment'],
                  declared_matches_actual=actual == validated['declared_environment'])
    return result


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['stage-source'])
    parser.add_argument('directory')
    arguments = parser.parse_args()
    stage_source(arguments.directory)
    print('Verified source view staged at 55817036.')
