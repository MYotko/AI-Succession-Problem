"""A16's prospective two-round plain-validation extension for the four stage 2
families (design note, amendment A16, "The rounds", items 1 to 10).

Parallel to A13 (the nominal family's one round) and A14 (its second round),
whose modules are unchanged. The numerical primitives are A13's: eligibility,
N*, the first-N* test with the visit-weighted safeguard, the visit-only stop,
the fresh-trajectory stage and the C0-only re-assembly. Each family runs its
rounds independently through direct single-host ``production_runner`` launches
(A16 item 6; A17 section 6 item 2). Plans, trajectory records and per-row
quantities are executor-only; ``public_record`` omits widths, N*, reach, visit
counts and per-stratum prices (A16 item 2).
"""
from contextlib import contextmanager
from contextvars import ContextVar
from copy import deepcopy
import hashlib
import math
from pathlib import Path
import time

from . import validation_extension_a13 as a13
from . import validation_extension_a14 as a14
from .artifacts import (SIMULATION, atomic_json, canonical, code_identity, digest,
                        file_hash, input_view, lease, read, scoped, seal, stable_job, unseal)
from .continuation_validation import _truncated_sha
from .forecast_a16 import DRAWS as FORECAST_DRAWS

SCHEMA = 'v3-A16-extension-1'
FAMILIES = ('sqrt', 'crowding', 'sigma_squared_x10', 'sigma_squared_x0.1')
FAMILY_INDEX = {family: index for index, family in enumerate(FAMILIES)}
ROUNDS = (1, 2)
PHASES = {1: 'validate_plain_a16_r1', 2: 'validate_plain_a16_r2'}
KINDS = {1: 'a16_validate_plain_r1', 2: 'a16_validate_plain_r2'}
KIND_ROUNDS = {kind: q for q, kind in KINDS.items()}
# Round 1's replicate ordinals are 4 to 35 and round 2's 36 to 67, irrespective
# of round 1's realized or allowed length (A16 item 3).
ORDINALS = {1: tuple(range(4, 36)), 2: tuple(range(36, 68))}
BLOCK = 1 << 60
# The eight disjoint blocks reserve [2^62, 12 x 2^60) (A16 item 3).
RESERVED = (1 << 62, 12 << 60)
R_UPPER = 32
R_FLOOR = 6
PRICE_CAP_X2_HOURS = 15
ROUND_CEILING_X2_HOURS = 48
SCOPES = {1: 'A10_stage2_after_A16_r1', 2: 'A10_stage2_after_A16_r2'}
# The fixed final publication targets and the frozen calibration strings of the
# family-path clause (A16, items 1 and 2), literal POSIX strings relative to
# simulation/. The nominal TARGET (validation_extension_a13.TARGET) is unchanged.
TARGETS = {'sqrt': 'v3/runs/a10_stage2/sqrt/v3_rerun_tables_A10.json',
           'crowding': 'v3/runs/a10_stage2/crowding/v3_rerun_tables_A10.json',
           'sigma_squared_x10': 'v3/runs/a10_stage2/sigma_squared_x10/v3_rerun_tables_A10.json',
           'sigma_squared_x0.1': 'v3/runs/a10_stage2/sigma_squared_x0.1/v3_rerun_tables_A10.json'}
CALIBRATIONS = {'sqrt': 'v3/runs/registered/v3_rerun_calibration.json',
                'crowding': 'v3/runs/registered/v3_rerun_calibration.json',
                'sigma_squared_x10': 'v3/runs/a10_stage2/sigma_squared_x10/v3_rerun_calibration.json',
                'sigma_squared_x0.1': 'v3/runs/a10_stage2/sigma_squared_x0.1/v3_rerun_calibration.json'}
# The two sigma families' variant calibrations are validated against the frozen
# nominal parent (calibration._validate_a10_variant), so their worker closure
# carries the hash-verified parent copy as well as the variant.
SIGMA_FAMILIES = ('sigma_squared_x10', 'sigma_squared_x0.1')
NOMINAL_CALIBRATION = 'v3/runs/registered/v3_rerun_calibration.json'
# The registered trees no rehearsal, history copy or fixture publication may write.
REGISTERED_TREES = ('v3/runs/registered', 'v3/runs/a10_stage2')
# The three A6 variant families make no A5 labels (A16, labels interpretation;
# option (ii) of LABELS_A6_VARIANTS.md). sqrt keeps the strict A5 requirement.
NO_LABEL_FAMILIES = ('crowding', 'sigma_squared_x10', 'sigma_squared_x0.1')
LABELS_POLICY = {'sqrt': 'a5_labels_required', 'crowding': 'no_a5_labels_a16',
                 'sigma_squared_x10': 'no_a5_labels_a16', 'sigma_squared_x0.1': 'no_a5_labels_a16'}
PROJECTION_FILE_SHA256 = a13.PROJECTION_FILE_SHA256
PROJECTION_SEAL = a13.PROJECTION_SEAL
ScientificHalt = a13.ScientificHalt
require = a13.require
stop_reached = a13.stop_reached
extension_stage = a13.extension_stage
_checkpoint_context = ContextVar('a16_checkpoint_context', default=None)
_launch_view = ContextVar('a16_launch_view', default=False)


class Finding(ValueError):
    """A substantive finding or mechanical no-launch condition (A16 item 10): it
    ends the family's extension sequence from registered entry."""


# ---------------------------------------------------------------------------
# Seeds (A16 item 3)
# ---------------------------------------------------------------------------

def require_family(family):
    require(family in FAMILIES, 'A16 applies to the four stage 2 families only')
    return family


def require_round(q):
    require(type(q) is int and q in ROUNDS, 'A16 has exactly two rounds')
    return q


def block_base(family, q):
    """The block base 2^62 + (2f + q - 1) x 2^60 for family index f and round q."""
    require_family(family)
    require_round(q)
    return (1 << 62) + (2 * FAMILY_INDEX[family] + q - 1) * BLOCK


def block_range(family, q):
    base = block_base(family, q)
    return base, base + BLOCK


def ext_seed(family, q, source_seed, replicate):
    require(type(replicate) is int and replicate in ORDINALS[require_round(q)], 'A16 replicate outside its round ordinals')
    require(type(source_seed) is int and source_seed >= 0, 'A16 source seed must be a non-negative integer')
    value = block_base(family, q) + _truncated_sha('v3_A16_ext/', family, '/', q, '/', source_seed, '/', replicate)
    low, high = block_range(family, q)
    require(low <= value < high, 'A16 seed outside its family block')
    return value


def rehearsal_seed(family, q, source_seed, replicate):
    """A non-registered rehearsal stream in [2^128, 2^129), outside every reserve."""
    return (1 << 128) | int(digest(['A16-rehearsal', family, q, source_seed, replicate])[:32], 16)


def reserved(seed):
    """Whether a seed lies in any extension reserve: A13's, A14's or A16's."""
    return a14.reserved(seed) or RESERVED[0] <= seed < RESERVED[1]


def check_seed_manifest(manifest, forbidden, *, family, q, rehearsal=False, recorded=()):
    """Pairwise distinctness, exclusion against the complete inventory, the
    block range, and A16 item 3's occupancy rule, defined here once and applied
    identically by preparation, the plan check and the worker:

    - an inventoried seed inside this round's own block is a finding unless it
      is this round's own deterministic manifest (a repeated preparation);
    - an inventoried seed elsewhere in the A16 reserve is a finding unless it
      belongs to a recorded A16 manifest of any family and either round
      (``recorded``: the inventory's frozen A16 manifests and, at round 2, this
      family's round-1 manifest);
    - a manifest seed equal to any other inventoried seed is a collision.

    A historical or manual seed inside the reserve is never a reason to shift
    a block."""
    seeds = [r['seed'] for r in manifest]
    require(all(type(s) is int and s >= 0 for s in seeds), 'invalid A16 seed')
    forbidden, recorded = set(forbidden), set(recorded)
    require(all(type(s) is int and s >= 0 for s in forbidden | recorded), 'invalid forbidden or recorded seed')
    own = set(seeds)
    if len(own) != len(seeds) or own & (forbidden - recorded):
        raise Finding('A16 global seed collision')
    low, high = block_range(family, q)
    inside = {s for s in forbidden if RESERVED[0] <= s < RESERVED[1]}
    own_block = {s for s in inside if low <= s < high}
    if own_block - own:
        raise Finding("finding: %d inventoried seed(s) inside this round's own A16 block are not its deterministic manifest"
                      % len(own_block - own))
    elsewhere = inside - own_block
    if elsewhere - recorded:
        raise Finding('finding: %d inventoried seed(s) in the A16 reserve belong to no recorded A16 manifest' % len(elsewhere - recorded))
    if rehearsal:
        require(all(not reserved(s) and (1 << 128) <= s < (1 << 129) for s in seeds), 'A16 rehearsal seed range mismatch')
    else:
        require(all(low <= s < high for s in seeds), 'A16 seed outside its family block')
    return dict(passed=True, pairwise_distinct=True, global_collision=False, reserve_occupied_by_history=False,
                repeated_preparation=bool(own & recorded), recorded_in_reserve=len(elsewhere), seeds=len(seeds),
                manifest_sha256=digest(manifest), forbidden_sha256=digest(sorted(forbidden)), recorded_sha256=digest(sorted(recorded)),
                family=family, round=q, block=[low, high], reserved_range=list(RESERVED),
                non_registered_rehearsal=bool(rehearsal))


def seed_manifest(family, q, sources, r_max, forbidden, *, rehearsal=False, recorded=()):
    """The full allowed manifest for the round: every source, every allowed
    replicate up to R_max, never merely the realized subset (A16 item 3)."""
    require(type(r_max) is int and 0 <= r_max <= R_UPPER, 'invalid A16 replicate bound')
    require(len({j['id'] for j in sources}) == len(sources), 'duplicate A16 source')
    seed = rehearsal_seed if rehearsal else ext_seed
    result = [dict(source_job_id=j['id'], replicate=r, seed=seed(family, q, int(j['seed']), r))
              for j in sorted(sources, key=lambda j: j['id']) for r in ORDINALS[q][:r_max]]
    check_seed_manifest(result, forbidden, family=family, q=q, rehearsal=rehearsal, recorded=recorded)
    return result


def launch_allowance(non_launch_reserve_x2_hours, incurred_x2_hours, projected_x2_hours):
    """A16 "Costs and ceilings": the launch spec's X2-equivalent allowance is the
    48 h round ceiling less the non-launch round reserves and the charges already
    incurred, never A14's 15 + 6 formula; it must still cover the class price."""
    for value in (non_launch_reserve_x2_hours, incurred_x2_hours):
        require(not isinstance(value, bool) and isinstance(value, (int, float)) and math.isfinite(value) and value >= 0,
                'A16 reserves and incurred charges must be finite and non-negative')
    allowance = ROUND_CEILING_X2_HOURS - non_launch_reserve_x2_hours - incurred_x2_hours
    require(allowance > 0, 'A16 round ceiling exhausted by reserves and incurred charges; no launch allowance')
    require(allowance >= projected_x2_hours, 'A16 launch allowance below the frozen class price')
    return allowance


# ---------------------------------------------------------------------------
# Pricing (A16 item 5)
# ---------------------------------------------------------------------------

def projection_binding(original):
    """The projection seal the original validation plan binds: pull_dispatch's
    field or its named equivalent at the successor (A16 item 5)."""
    binding = original.get('pull_dispatch', {}).get('projection_sha256', original.get('projection_sha256'))
    if not isinstance(binding, str) or len(binding) != 64:
        raise Finding('finding: original validation plan does not bind the registered cost projection')
    return binding


def price_round(original, projection_document, sources, *, family, registered, projection_file_hash):
    """B_j = x2_hours_max / jobs of each source's validate_plain stratum; S is the
    sum of B_j / 3 over distinct sources; R_max = max{R <= 32 : R S <= 15}."""
    require_family(family)
    projection = unseal(projection_document)
    strata = projection.get('per_phase_capability', {})
    for j in sources:
        c = j['config']
        require(c['a10_family'] == family, 'A16 source job belongs to another family')
        stratum = f"{c['a10_family']}.{float(c['kernel']['capability'])}.{c['setting_name']}.validate_plain"
        p = strata.get(stratum)
        if (not isinstance(p, dict) or type(p.get('jobs')) is not int or p['jobs'] <= 0
                or isinstance(p.get('x2_hours_max'), bool) or not isinstance(p.get('x2_hours_max'), (int, float))
                or not math.isfinite(p['x2_hours_max']) or p['x2_hours_max'] <= 0):
            raise Finding('finding: registered stratum price missing or invalid: ' + stratum)
    # A13's helper performs the payload-seal binding check and, when registered,
    # the projection file and seal identity checks, before any price is read.
    bound = dict(original, pull_dispatch=dict(projection_sha256=projection_binding(original)))
    price = a13.price_extension(bound, projection_document, sources, registered=registered,
                                projection_file_hash=projection_file_hash)
    per_replicate = math.fsum(v['replicate_x2_hours'] for v in price['prices'].values())
    r_max = max((r for r in range(R_UPPER + 1) if r * per_replicate <= PRICE_CAP_X2_HOURS), default=0)
    return dict(price, R_max=r_max, projected_x2_hours=r_max * per_replicate, price_cap_x2_hours=PRICE_CAP_X2_HOURS,
                replicate_upper_bound=R_UPPER, launch_floor=R_FLOOR)


# ---------------------------------------------------------------------------
# The test and the stop (A16 item 4)
# ---------------------------------------------------------------------------

def extension_test(records, parameters, q):
    """A13's unchanged test on the round's own ordered pairs. Round 2's ordinals
    are re-based by subtracting 32 for the primitive; nothing else changes."""
    require_round(q)
    first = ORDINALS[q][0]
    require([r['replicate'] for r in records] == list(range(first, first + len(records))), 'A16 replicate order or gap')
    shift = first - 4
    return a13.extension_test([dict(r, replicate=r['replicate'] - shift) for r in records], parameters)


def validate_replicates(job, replicates):
    c = job['config']
    q = KIND_ROUNDS[job['kind']]
    first = ORDINALS[q][0]
    require(len(replicates) <= c['R_max'], 'too many A16 replicates')
    prior = []
    for index, r in enumerate(replicates):
        require(not prior or not stop_reached(prior, c['eligible_rows']), 'A16 continued past stop')
        require(r['replicate'] == index + first and r['seed'] == c['stream_seeds'][index], 'A16 checkpoint seed/order mismatch')
        require(set(r['rows']) == set(c['eligible_rows']), 'A16 checkpoint row mismatch')
        require(r['count'] == c['trajectory_count'], 'A16 trajectory count mismatch')
        for pairs in r['rows'].values():
            require(len(pairs) == r['count'] and all(len(p) == 2 and math.isfinite(p[0]) and type(p[1]) is int
                    and p[1] >= 0 and (p[1] > 0 or p[0] == 0) for p in pairs), 'invalid A16 ordered trajectory records')
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
    q = KIND_ROUNDS[job['kind']]
    values = []
    for path in sorted((Path(root) / PHASES[q] / 'a16_checkpoints' / job['id']).glob('*.json')):
        value = unseal(read(path))
        require(value['job_sha256'] == digest(job), 'A16 checkpoint job changed')
        values.append(value['replicate'])
    return validate_replicates(job, values)


@contextmanager
def execution_inputs(jobs):
    """Use only the declared verified copies, including transferred aliases."""
    from .artifacts import _INPUT_VIEW, input_path
    outer = _INPUT_VIEW.get() or dict(paths={}, protected=[])
    paths, protected = dict(outer['paths']), list(outer['protected'])
    for job in jobs:
        for row in job['config'].get('a16_inputs', []):
            target = Path(input_path(row['copy']))
            require(file_hash(target) == row['sha256'] and target.stat().st_size == row['bytes'], 'A16 execution input changed')
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
    q = KIND_ROUNDS[job['kind']]
    family = require_family(c['a16_family'])
    first = ORDINALS[q][0]
    configuration = job['tag'] in ('configuration', 'validation') and c.get('configuration_test')
    require(c['phase'] == PHASES[q] and c.get('a16_round') == q and c['M'] > 0, 'invalid A16 phase, round or M')
    require(all(p['M'] == c['M'] for p in c['eligible_rows'].values()), 'A16 row M differs')
    seeds = [c['seed']] if configuration else c['stream_seeds']
    if configuration:
        require(not reserved(c['seed']), 'A16 configuration uses reserved seed')
    else:
        seed = rehearsal_seed if c.get('non_registered_rehearsal') else ext_seed
        require(R_FLOOR <= c['R_max'] <= R_UPPER, 'A16 no-launch floor or upper bound')
        require(seeds == [seed(family, q, int(c['a1_job']['seed']), r) for r in ORDINALS[q][:c['R_max']]], 'A16 seeds changed')
        # The same inputs as preparation's check: the configuration carries the
        # recorded A16 manifests, so a round-2 configuration whose forbidden
        # seeds hold its own round-1 manifest passes (A16 item 3).
        check_seed_manifest(c['full_seed_manifest'], c['forbidden_seeds'], family=family, q=q,
                            rehearsal=c.get('non_registered_rehearsal', False), recorded=c['recorded_a16_seeds'])
    source = a13.a4._load_a1(c['a1_source_root'], c['a1_job'], c['a1_source_code_hash'])
    fit = unseal(c['fit'])
    require(fit['a1_job_id'] == c['a1_job']['id'], 'A16 fit source mismatch')
    local = _checkpoint_context.get()
    directory = Path(root) / 'a16_checkpoints' / job['id'] if local is None else local[0]
    prior = [] if local is None else deepcopy(local[1])
    recheck = local is not None and local[2]
    if local is None and not configuration:
        for path in sorted(directory.glob('*.json')):
            value = unseal(read(path))
            require(value['job_sha256'] == digest(job), 'A16 checkpoint job mismatch')
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
        value.update(replicate=index + first, seed=seed)
        prior.append(value)
        if not configuration and not recheck:
            atomic_json(directory / f'{index + first:02d}.json', seal(dict(job_sha256=digest(job), replicate=value)))
    return dict(stage=PHASES[q], plan_hash=c['plan_hash'], a1_job_id=c['a1_job']['id'], a16_family=family, a16_round=q,
                code_hash=code_identity(), replicates=prior,
                stopped_on_visits=bool(prior and stop_reached(prior, c['eligible_rows'])))


# ---------------------------------------------------------------------------
# Anchors and lifecycle records (A16 item 10)
# ---------------------------------------------------------------------------

def target_path(family):
    return scoped(SIMULATION / TARGETS[require_family(family)])


def anchor_stem(family, *, registered, rehearsal_anchor=None):
    """The never-written target for a registered family; an explicit
    output-relative stem for rehearsals, outside the registered tree."""
    if registered:
        require(rehearsal_anchor is None, 'registered A16 anchors are the family target')
        return target_path(family)
    require(rehearsal_anchor is not None, 'A16 rehearsal needs an explicit output-relative anchor')
    stem = scoped(rehearsal_anchor)
    require(not {'runs', 'registered', 'a10_stage2'}.intersection(p.lower() for p in stem.parts), 'A16 rehearsal anchor inside the registered tree')
    return stem


def anchor_paths(stem):
    """The stem and every anchor file a family writes beside it."""
    paths = [Path(stem), family_record_path(stem)]
    for q in ROUNDS:
        paths += [round_record_path_of(stem, q), admission_record_path_of(stem, q)]
    return paths


def preparation_outputs(output, stem, *, family, registered, rehearsal_root, history=None):
    """A16 item 10 and the fixture prohibition, checked before any write. A
    non-registered preparation writes the plan, its public record, the
    family's anchors and its history copies (the inventory's view root and
    every copy destination, ``history`` being the unsealed inventory) only
    under the declared rehearsal output root, which lies outside the two
    registered trees, and never on a protected anchor. A registered
    preparation writes only its own family's anchors and its plan path, which
    is never an anchor, a publication sibling (receipt, sidecar or A10 receipt
    of any target) or a path in another family's registered directory; its
    history view stays a declared view outside the registered trees, which
    stage_history checks on its own."""
    require_family(family)
    output = scoped(output)
    plan_files = [output, output.with_suffix('.public.json')]
    if registered:
        require(rehearsal_root is None, 'registered A16 preparation declares no rehearsal output root')
        targets = [(SIMULATION / TARGETS[f]).resolve() for f in FAMILIES] + [(SIMULATION / a13.TARGET).resolve()]
        foreign = [t.parent for t in targets if t != (SIMULATION / TARGETS[family]).resolve()]
        siblings = {t.with_suffix(s) for t in targets for s in ('.compatibility.json', '.cell_results.json', '.a10_receipt.json')}
        for path in plan_files:
            require(path not in protected_anchors() and path not in siblings and not any(path.is_relative_to(d) for d in foreign),
                    "A16 registered plan path is an anchor, a publication sibling or another family's registered directory: " + path.name)
        return output, None
    require(rehearsal_root is not None, 'A16 rehearsal needs an explicit rehearsal output root')
    root = scoped(rehearsal_root)
    require(not in_registered_tree(root), 'A16 rehearsal output root lies inside the registered tree')
    for path in plan_files + anchor_paths(stem):
        require(not in_registered_tree(path), 'A16 rehearsal output on a registered tree or anchor: ' + path.name)
        require(path.is_relative_to(root), 'A16 rehearsal output outside its declared root: ' + path.name)
    # The history copies are outputs too: the inventory is required here, so the
    # guarantee is never opt-in by argument.
    require(isinstance(history, dict), 'A16 rehearsal preparation checks its history inventory before any write')
    view = history.get('view_root')
    require(isinstance(view, str) and Path(view).is_absolute(), 'A16 rehearsal history inventory declares no absolute view root')
    view = scoped(view)
    require(not in_registered_tree(view) and view.is_relative_to(root), 'A16 rehearsal history view root outside its declared rehearsal root')
    for row in history.get('files', []):
        copy = Path(row['copy'])
        require(copy.is_absolute() and scoped(copy).is_relative_to(root) and not in_registered_tree(scoped(copy)),
                'A16 rehearsal history copy destination outside its declared rehearsal root: ' + copy.name)
    return output, root


def family_record_path(stem):
    return Path(stem).with_suffix('.a16_family.json')


def round_record_path_of(stem, q):
    return Path(stem).with_suffix('.a16_round%d.json' % require_round(q))


def admission_record_path_of(stem, q):
    return Path(stem).with_suffix('.a16_round%d.admission.json' % require_round(q))


def registered_trees():
    return tuple((SIMULATION / tree).resolve() for tree in REGISTERED_TREES)


def protected_anchors():
    """Every stage 2 family's target and A16 anchors, and the nominal target
    with its A13 and A14 anchors: no history copy, rehearsal anchor or fixture
    publication may land on one of them (A16 item 10; the fixture prohibition)."""
    values = set()
    for family in FAMILIES:
        stem = (SIMULATION / TARGETS[family]).resolve()
        values |= {stem, family_record_path(stem).resolve()}
        for q in ROUNDS:
            values |= {round_record_path_of(stem, q).resolve(), admission_record_path_of(stem, q).resolve()}
    nominal = (SIMULATION / a13.TARGET).resolve()
    values |= {nominal, nominal.with_suffix('.a13_round.json'), nominal.with_suffix('.a13_round.admission.json'),
               nominal.with_suffix('.a14_round.json'), nominal.with_suffix('.a14_round.admission.json')}
    return values


def in_registered_tree(path):
    path = Path(path).resolve()
    return path in protected_anchors() or any(path.is_relative_to(tree) for tree in registered_trees())


def family_identity(record):
    """The immutable fields of a family anchor, bound into admission provenance."""
    return digest({k: record[k] for k in ('schema', 'family', 'target', 'original', 'created_epoch', 'code_hash')})


def round_identity(record):
    """The immutable launch binding of a round record (plan, spec and root)."""
    return digest({k: record[k] for k in ('schema', 'family', 'round', 'plan_hash', 'spec_hash', 'root')})


def admission_identity(record):
    """The admission record's identity before its outcome: every bound field
    (scope, plan, family, round, counts, per-row classifications) except the
    outcome itself, which the binding decides afterwards."""
    return digest({k: v for k, v in record.items() if k not in ('outcome', 'admitted_set_sha256')})


def _update(path, mutate):
    with lease(path.with_suffix('.lock')):
        record = unseal(read(path))
        mutate(record)
        atomic_json(path, seal(record))
    return record


def _family_log(stem, entry):
    """Append-only family-anchor log (A16 item 10: the classification of a failure
    is recorded in the family anchor, with the interpreter's review)."""
    return _update(family_record_path(stem), lambda record: record['log'].append(dict(entry, epoch=time.time())))


def reserve_family(stem, family, original, *, registered):
    """Create the family anchor if absent; otherwise require the same family and
    original hashes and no terminal state. Never overwritten by a new reservation."""
    path = family_record_path(stem)
    with lease(path.with_suffix('.lock')):
        if path.exists():
            record = unseal(read(path))
            require(record.get('schema') == 'v3-A16-family-1' and record['family'] == family
                    and record['original'] == original and record['registered'] == registered, 'A16 family anchor belongs to another realization')
            require(record['terminal'] is None, 'A16 family sequence is final')
            require(record.get('published_round') is None, 'A16 family already published; no further round')
            return record
        record = dict(schema='v3-A16-family-1', family=family, target=TARGETS[family] if registered else str(stem),
                      registered=registered, original=original, code_hash=code_identity(), created_epoch=time.time(),
                      terminal=None, published_round=None, log=[])
        atomic_json(path, seal(record))
    return record


def reserve_round(stem, family, q, request, *, resume=False, compatibility_record=None):
    """Exclusive round record, created before any evidence verification. A resume
    requires the same request apart from the code identity, a live state and
    every logged failure classified as tooling (A16 item 10, the pre-go
    tooling-failure rule). A changed code identity is accepted only with a
    direct A11 compatibility record from the recorded identity to the current
    one, verified through compatibility_a10's record checks (passed, approved
    and committed); the prior attempt is appended to the round record's log.
    A bound launch root is never rebound."""
    path = round_record_path_of(stem, q)
    with lease(path.with_suffix('.lock')):
        if path.exists():
            record = unseal(read(path))
            same = {k: v for k, v in record['request'].items() if k != 'code_hash'} == {k: v for k, v in request.items() if k != 'code_hash'}
            require(record.get('schema') == 'v3-A16-round-1' and record['family'] == family and record['round'] == q and same,
                    'A16 round already reserved for another request')
            require(record['state'] in ('preparing', 'prepared') and record['halt'] is None and record['root'] is None,
                    'A16 round already launched, spent or terminal')
            require(resume, 'A16 round preparation already reserved; repeat it with resume')
            require(all(f.get('classification') == 'tooling' for f in record['failures']),
                    'A16 round has an unclassified or substantive failure; the interpreter classifies it before any repeat')
            if record['request']['code_hash'] != request['code_hash']:
                require(bool(record['failures']),
                        'A16 preparation resume at a changed code identity follows a logged, tooling-classified failure')
                require(compatibility_record is not None,
                        'A16 preparation resume at a changed code identity needs a direct A11 compatibility record from the recorded identity')
                from .compatibility_a10 import validate_record
                prior = validate_record(compatibility_record)
                require(prior == record['request']['code_hash'] and request['code_hash'] == code_identity(),
                        'A16 compatibility record does not run from the recorded identity to the current one')
                record.setdefault('log', []).append(dict(event='identity_changed', prior_code_hash=prior, new_code_hash=request['code_hash'],
                                                         prior_plan_hash=record['plan_hash'],
                                                         prior_superseded_plan_hashes=list(record['superseded_plan_hashes']),
                                                         compatibility_record_sha256=file_hash(compatibility_record), epoch=time.time()))
                if record['plan_hash'] is not None:
                    record['superseded_plan_hashes'].append(record['plan_hash'])
                record.update(request=request, plan_hash=None, state='preparing')
                atomic_json(path, seal(record))
            return path
        require(not resume, 'A16 preparation resume needs an existing round record')
        record = dict(schema='v3-A16-round-1', family=family, round=q, request=request, state='preparing',
                      plan_hash=None, spec_hash=None, root=None, halt=None, admission=None,
                      superseded_plan_hashes=[], failures=[], log=[], created_epoch=time.time())
        atomic_json(path, seal(record))
    return path


def record_failure(stem, q, reason, *, classification=None):
    """Append a failure to the round record. ``classification`` 'substantive'
    latches the round and the family terminal; None leaves it for the
    interpreter's review (``classify_failure``); 'tooling' leaves the round live."""
    require(classification in (None, 'tooling', 'substantive'), 'invalid A16 failure classification')
    path = round_record_path_of(stem, q)
    failure = dict(reason=str(reason), epoch=time.time(), classification=classification, reviewer=None)

    def mutate(record):
        record['failures'].append(failure)
        if classification == 'substantive' and record['halt'] is None:
            record.update(state='refused', halt=dict(reason=str(reason), kind='finding', epoch=failure['epoch']))
    record = _update(path, mutate)
    _family_log(stem, dict(event='failure_recorded', round=q, index=len(record['failures']) - 1, reason=str(reason),
                           classification=classification))
    if classification == 'substantive':
        latch_family_terminal(stem, 'round %d finding: %s' % (q, reason), q)
    return record


def classify_failure(stem, q, index, classification, reviewer):
    """The interpreter's recorded classification of a logged failure."""
    require(classification in ('tooling', 'substantive') and isinstance(reviewer, str) and reviewer.strip(),
            'A16 failure classification needs tooling or substantive and a reviewer')
    path = round_record_path_of(stem, q)

    def mutate(record):
        failure = record['failures'][index]
        require(failure['classification'] is None, 'A16 failure already classified')
        failure.update(classification=classification, reviewer=reviewer, classified_epoch=time.time())
        if classification == 'substantive' and record['halt'] is None:
            record.update(state='refused', halt=dict(reason=failure['reason'], kind='finding', epoch=time.time()))
    record = _update(path, mutate)
    _family_log(stem, dict(event='failure_classified', round=q, index=index, classification=classification,
                           reviewer=reviewer, reason=record['failures'][index]['reason']))
    if classification == 'substantive':
        latch_family_terminal(stem, 'round %d finding: %s' % (q, record['failures'][index]['reason']), q)
    return record


def latch_family_terminal(stem, reason, q):
    path = family_record_path(stem)

    def mutate(record):
        if record['terminal'] is None:
            record['terminal'] = dict(reason=str(reason), round=q, epoch=time.time())
        record['log'].append(dict(event='terminal', reason=str(reason), round=q, epoch=time.time()))
    return _update(path, mutate)


def decline(stem, q, *, operator, reason):
    """The operator's explicit decline before launch: terminal for the family."""
    require(bool(operator.strip()) and bool(reason.strip()), 'operator decline needs operator and reason')
    path = round_record_path_of(stem, q)

    def mutate(record):
        require(record['state'] in ('preparing', 'prepared') and record['halt'] is None and record['root'] is None,
                'decline is valid only before launch')
        record.update(state='refused', halt=dict(reason='operator declined: ' + reason, operator=operator, epoch=time.time()))
    _update(path, mutate)
    latch_family_terminal(stem, 'round %d declined by the operator: %s' % (q, reason), q)


# ---------------------------------------------------------------------------
# The plan
# ---------------------------------------------------------------------------

def plan_hash(plan):
    return digest({k: v for k, v in plan.items() if k not in ('plan_hash', 'jobs', 'configuration', 'pull_dispatch')})


def plan_stem(plan):
    return anchor_stem(plan['a16_family'], registered=plan['registered'],
                       rehearsal_anchor=None if plan['registered'] else plan['anchor_stem'])


def round_record_path(plan):
    stem = plan_stem(plan)
    path = round_record_path_of(stem, plan['round'])
    require(str(path) == plan['round_record_path'], 'A16 round record moved from its family anchor')
    return path


def validate_plan(plan, *, launching=False):
    require(plan.get('schema') == SCHEMA and plan.get('round') in ROUNDS, 'invalid A16 plan')
    q, family = plan['round'], require_family(plan['a16_family'])
    require(plan['registered'] != bool(plan['non_registered_rehearsal']), 'A16 requires registered XOR rehearsal')
    require('pull_dispatch' not in plan, 'A16 rounds launch through direct single-host production_runner at this identity')
    require(plan['code_hash'] == code_identity() and plan_hash(plan) == plan['plan_hash'], 'A16 plan or source changed')
    require(plan['tag'] == 'v3_tables' and plan['registered_a10'] == plan['registered'], 'A16 plan tag or A10 flag changed')
    round_record_path(plan)
    require(plan['R_max'] == plan['pricing']['R_max'] and R_FLOOR <= plan['R_max'] <= R_UPPER, 'A16 launch floor or bound')
    check_seed_manifest(plan['seed_manifest'], plan['forbidden_seeds'], family=family, q=q, rehearsal=plan['non_registered_rehearsal'],
                        recorded=plan['recorded_a16_seeds'])
    expected = [stable_job(KINDS[q], dict(c, plan_hash=plan['plan_hash']), 'v3_tables', i) for i, c in enumerate(plan['job_skeletons'])]
    require(plan['jobs'] == expected, 'A16 jobs changed')
    require(bool(plan['jobs']), 'A16 plan has no source job')
    for j in plan['jobs']:
        c = j['config']
        require(c['M'] == plan['M'] and c['full_seed_manifest'] == plan['seed_manifest'] and c['a16_family'] == family
                and c['recorded_a16_seeds'] == plan['recorded_a16_seeds']
                and c['a16_round'] == q and c['phase'] == PHASES[q] and c['R_max'] == plan['R_max'], 'A16 constants/manifest changed')
    if plan['registered']:
        require(plan['forecast']['draws'] == FORECAST_DRAWS and plan['forecast'].get('registered') is True,
                'registered A16 forecast uses exactly %d draws' % FORECAST_DRAWS)
    require(plan['labels_policy'] == LABELS_POLICY[family], 'A16 labels policy differs from the adopted interpretation')
    require(plan['round_ceiling_x2_hours'] == ROUND_CEILING_X2_HOURS and plan['x2_equivalent_hours'] == launch_allowance(
        plan['non_launch_reserve_x2_hours'], plan['incurred_x2_hours'], plan['pricing']['projected_x2_hours']),
        'A16 launch allowance differs from the 48 h round ceiling less reserves and incurred charges')
    if launching:
        require(plan['launch_allowed'], 'A16 launch not authorized')
        from .history_a16 import verify_history
        verified = verify_history(plan['history'], round=q, registered=plan['registered'])
        require(verified['classification_sha256'] == plan['classification_sha256'], 'A16 historical classification changed')
        require(verified['family'] == family, 'A16 history family differs from plan')
    return plan


def begin_round(plan, plan_path, root):
    """Bind the round once to its frozen plan and root before any dispatch."""
    validate_plan(plan, launching=True)
    require(unseal(read(plan_path)) == plan, 'A16 launch plan changed')
    root, path = scoped(root), round_record_path(plan)
    stem = plan_stem(plan)
    family = unseal(read(family_record_path(stem)))
    require(family['terminal'] is None and family.get('published_round') is None, 'A16 family sequence is final')
    with lease(path.with_suffix('.lock')):
        value = unseal(read(path))
        require(value.get('schema') == 'v3-A16-round-1' and value['plan_hash'] == plan['plan_hash'] and value['halt'] is None
                and value['state'] in ('prepared', 'launched'), 'A16 round spent or different plan')
        require(value['root'] in (None, str(root)) and value['spec_hash'] in (None, digest(plan)), 'A16 different root/specification')
        value.update(root=str(root), spec_hash=digest(plan), state='launched')
        atomic_json(path, seal(value))
        atomic_json(root / 'a16_round.json', seal(dict(record_path=str(path), family_record_path=str(family_record_path(stem)),
                                                       plan_hash=plan['plan_hash'], spec_hash=digest(plan), round=plan['round'],
                                                       family=plan['a16_family'])))
    round_halt(root)
    require(unseal(read(path))['halt'] is None, 'A16 round has a latched halt')


def latch_round_halt(root, reason):
    root = scoped(root)
    pointer = root / 'a16_round.json'
    require(pointer.exists(), 'A16 halt lacks a bound round')
    ref = unseal(read(pointer))
    path = scoped(ref['record_path'])
    with lease(path.with_suffix('.lock')):
        value = unseal(read(path))
        require(value.get('schema') == 'v3-A16-round-1' and value['plan_hash'] == ref['plan_hash']
                and value['spec_hash'] == ref['spec_hash'] and value['root'] == str(root), 'A16 halt binding mismatch')
        if value['halt'] is None:
            value.update(halt=dict(reason=str(reason), kind='scientific_halt', epoch=time.time()), state='halted')
            atomic_json(path, seal(value))
    family_path = scoped(ref['family_record_path'])

    def mutate(record):
        if record['terminal'] is None:
            record['terminal'] = dict(reason='round %d scientific halt: %s' % (ref['round'], reason), round=ref['round'], epoch=time.time())
        record['log'].append(dict(event='halt', reason=str(reason), round=ref['round'], epoch=time.time()))
    _update(family_path, mutate)


def round_halt(root):
    root = scoped(root)
    ref = unseal(read(root / 'a16_round.json'))
    for path in (root / 'a16_scientific_halt.json', root / 'nondeterminism_failure.json',
                 root / PHASES[ref['round']] / 'nondeterminism_failure.json'):
        if path.exists():
            latch_round_halt(root, path.name)
    return unseal(read(scoped(ref['record_path'])))['halt']


def publication_round(plan, root):
    root = scoped(root)
    value = unseal(read(round_record_path(plan)))
    require(value.get('schema') == 'v3-A16-round-1' and value['plan_hash'] == plan['plan_hash']
            and value['spec_hash'] == digest(plan) and value['root'] == str(root), 'A16 publication root/plan mismatch')
    require(value['halt'] is None and round_halt(root) is None, 'A16 halted round certifies nothing')
    require(read(root / 'identity.json') == dict(code_hash=plan['code_hash'], spec_hash=digest(plan)), 'A16 root identity mismatch')
    history = read(root / 'launches.json')
    require(bool(history) and history[-1].get('complete') is True, 'A16 launch not complete')
    check = read(root / PHASES[plan['round']] / 'nondeterminism_check.json')
    require(check.get('matched') is True and check.get('checked') in {j['id'] for j in plan['jobs']}, 'A16 check did not pass')
    return value


# ---------------------------------------------------------------------------
# Preparation (A16 items 1, 2, 3, 5, 6, 7 and 10)
# ---------------------------------------------------------------------------

INVENTORY_SCHEMA = 'v3-A16-seed-inventory-1'
# The operator categories bind sealed seed-source records of this schema; the
# frozen categories bind the stage 2 seed registry, the A13, A14 and A16 plans.
SEED_SOURCE_SCHEMA = 'v3-A16-seed-source-1'
INVENTORY_CATEGORIES = ('registered', 'planning', 'probe', 'pilot', 'rehearsal', 'qualification', 'configuration',
                        'a13_manifest', 'a13_forbidden', 'a14_manifest', 'a14_forbidden', 'a16_manifests', 'stage2')
# The categories a registered inventory reconciles to a frozen source record:
# every seed of the bound record must be listed (A16 item 3).
RECONCILED_CATEGORIES = ('stage2', 'a13_manifest', 'a13_forbidden', 'a14_manifest', 'a14_forbidden')


def _hex64(value):
    return isinstance(value, str) and len(value) == 64 and all(c in '0123456789abcdef' for c in value)


def _frozen_source_seeds(category, document, *, registered):
    """The seeds a bound frozen record contributes to a reconciled category, or
    None for the categories that bind arbitrary operator records. In registered
    mode a plan-shaped source must itself be a registered plan."""
    from .tables_a10 import STAGE2_REGISTRY_SCHEMA
    payload = unseal(document) if isinstance(document, dict) and set(document) == {'payload', 'sha256'} else document
    schema = payload.get('schema') if isinstance(payload, dict) else None
    if category == 'stage2':
        if schema != STAGE2_REGISTRY_SCHEMA:
            raise Finding('finding: the stage 2 inventory category binds a record that is not the stage 2 seed registry')
        return {int(s) for kind in ('table_jobs', 'a4_streams', 'a5_streams', 'runs') for v in payload[kind].values() for s in v}
    if category in ('a13_manifest', 'a13_forbidden', 'a14_manifest', 'a14_forbidden'):
        expected = a13.SCHEMA if category.startswith('a13') else a14.SCHEMA
        if schema != expected:
            raise Finding('finding: the %s inventory category binds a record that is not the frozen %s plan' % (category, category[:3].upper()))
        if registered and payload.get('registered') is not True:
            raise Finding('finding: the %s inventory category binds a non-registered plan' % category)
        return {int(r['seed']) for r in payload['seed_manifest']} if category.endswith('manifest') else {int(s) for s in payload['forbidden_seeds']}
    if category == 'a16_manifests':
        if schema not in (SCHEMA, SCHEMA + '-public'):
            raise Finding('finding: the a16_manifests inventory category binds a record that is not an A16 plan or public record')
        if registered and schema == SCHEMA and payload.get('registered') is not True:
            raise Finding('finding: the a16_manifests inventory category binds a non-registered plan')
        if registered and schema != SCHEMA and (payload.get('seed_check') or {}).get('non_registered_rehearsal') is not False:
            raise Finding('finding: the a16_manifests inventory category binds a rehearsal public record')
        return {int(r['seed']) for r in payload['seed_manifest']}
    return None


def _committed_source(path, relative):
    """The stage 2 seed registry a registered inventory reconciles to is the
    committed one: the working file equals its bytes at HEAD."""
    import subprocess
    from .compatibility_a10 import _committed_bytes
    try:
        committed = _committed_bytes(Path(path))
    except (subprocess.CalledProcessError, ValueError, OSError):
        raise Finding('finding: the stage 2 seed registry source is not committed: ' + relative)
    if committed != Path(path).read_bytes():
        raise Finding('finding: the stage 2 seed registry source differs from its committed bytes: ' + relative)


def _source_seeds(category, document, *, registered):
    """The seeds one bound source contributes: a frozen record's own seeds for
    the reconciled categories and the A16 manifests, or a sealed seed-source
    record for the operator categories."""
    contribution = _frozen_source_seeds(category, document, registered=registered)
    if contribution is not None:
        return contribution
    payload = unseal(document) if isinstance(document, dict) and set(document) == {'payload', 'sha256'} else document
    if (not isinstance(payload, dict) or payload.get('schema') != SEED_SOURCE_SCHEMA or payload.get('category') != category
            or not isinstance(payload.get('seeds'), list) or not all(type(s) is int and s >= 0 for s in payload['seeds'])):
        raise Finding('finding: the %s inventory category binds a record that is not a sealed seed-source record for it' % category)
    return set(payload['seeds'])


def validate_inventory(document, *, registered):
    """A16 item 3's global seed inventory. Every category binds its sources
    (path relative to simulation/, SHA-256, declared count), every source is
    hash-verified and read, each source's declared count equals the seeds it
    contributes, and the category's listed seeds equal the union of its
    sources' contributions exactly (no extra, no missing), in registered and
    rehearsal mode alike; an empty category carries a sealed statement naming
    the source checked and why it is empty. In registered mode the reconciled
    categories must bind their frozen records, the stage 2 registry must be the
    committed one and plan-shaped sources must be registered plans. Anything
    short of that is a Finding. Returns the verified seeds per category and the
    recorded A16 seeds, both derived from the verified sources, never from the
    listed values."""
    inventory = unseal(document)
    if inventory.get('schema') != INVENTORY_SCHEMA or not isinstance(inventory.get('categories'), dict):
        raise Finding('finding: A16 global seed inventory lacks its schema or categories')
    categories = inventory['categories']
    if set(categories) != set(INVENTORY_CATEGORIES):
        raise Finding('finding: A16 global seed inventory is incomplete or carries an unknown category')
    verified = {}
    for name in INVENTORY_CATEGORIES:
        entry = categories[name]
        if not isinstance(entry, dict) or not isinstance(entry.get('seeds'), list) or not isinstance(entry.get('sources'), list):
            raise Finding('finding: A16 inventory category %s lacks its seeds or source bindings' % name)
        seeds = entry['seeds']
        if not all(type(s) is int and s >= 0 for s in seeds) or len(set(seeds)) != len(seeds):
            raise Finding('finding: A16 inventory category %s lists invalid or duplicate seeds' % name)
        for source in entry['sources']:
            if (not isinstance(source, dict) or not isinstance(source.get('path'), str) or not source['path']
                    or source['path'].startswith('/') or '\\' in source['path'] or Path(source['path']).is_absolute()
                    or not _hex64(source.get('sha256')) or type(source.get('count')) is not int or source['count'] < 0):
                raise Finding('finding: A16 inventory category %s binds a source without a simulation-relative path, SHA-256 and count' % name)
        statement = entry.get('empty')
        if not seeds:
            if (not isinstance(statement, dict) or not all(isinstance(statement.get(k), str) and statement[k].strip()
                                                             for k in ('source_checked', 'reason'))):
                raise Finding('finding: empty A16 inventory category %s lacks its sealed statement naming the source checked and why' % name)
        elif statement is not None:
            raise Finding('finding: A16 inventory category %s is not empty but carries an empty statement' % name)
        if registered and name in RECONCILED_CATEGORIES and not entry['sources']:
            raise Finding('finding: registered A16 inventory category %s binds no frozen source record' % name)
        contributed = set()
        for source in entry['sources']:
            path = SIMULATION / source['path']
            if not path.is_file() or file_hash(path) != source['sha256']:
                raise Finding('finding: A16 inventory source missing or changed: ' + source['path'])
            if registered and name == 'stage2':
                _committed_source(path, source['path'])
            contribution = _source_seeds(name, read(path), registered=registered)
            if source['count'] != len(contribution):
                raise Finding('finding: A16 inventory source %s declares %d seeds against the %d it contributes'
                              % (source['path'], source['count'], len(contribution)))
            contributed |= contribution
        extra, missing = set(seeds) - contributed, contributed - set(seeds)
        if extra or missing:
            raise Finding('finding: A16 inventory category %s lists %d seed(s) against the %d its bound sources contribute (%d extra, %d missing)'
                          % (name, len(seeds), len(contributed), len(extra), len(missing)))
        verified[name] = sorted(contributed)
    return dict(seeds=verified, recorded_a16_seeds=list(verified['a16_manifests']))


def validate_invocation(output, inputs, *, round, registration, rehearsal, resume):
    """Read invocation metadata only; never create or modify a record."""
    q = require_round(round)
    registered = registration is not None
    require(registered != bool(rehearsal), 'A16 requires exactly one of registered or rehearsal')
    output = scoped(output)
    if not resume:
        require(not output.exists(), 'A16 plan already frozen')
    for name, value in inputs.items():
        require(Path(value).is_file(), 'A16 input must exist and be a regular file: ' + name)
    projection = read(inputs['projection'])
    unseal(projection)
    projection_hash = file_hash(inputs['projection'])
    if registered:
        require(projection_hash == PROJECTION_FILE_SHA256 and projection['sha256'] == PROJECTION_SEAL,
                'A16 registered projection identity mismatch')
    inventory = validate_inventory(read(inputs['seed_inventory']), registered=registered)
    return dict(round=q, registered=registered, projection=projection, projection_file_hash=projection_hash,
                inventory=inventory, inventory_file_hash=file_hash(inputs['seed_inventory']))


def _history_summary(history_document):
    """Family and original-record hashes from the inventory alone, for the
    reservation that precedes verification (A16 item 10)."""
    payload = unseal(history_document)
    require(payload.get('schema') == 'v3-A16-history-1', 'A16 preparation needs an A16 history inventory')
    family = require_family(payload['family'])
    roles = payload['roles']
    by_source = {str(Path(r['source']).resolve()): r for r in payload['files']}

    def sha(role):
        return by_source[str(Path(roles[role]).resolve())]['sha256']
    original = dict(plan_file_sha256=sha('original_plan'), candidate_file_sha256=sha('candidate'),
                    sidecar_file_sha256=sha('original_sidecar'), receipt_file_sha256=sha('original_receipt'),
                    admission_record_sha256=sha('original_admission'))
    return family, original, payload.get('round')


def hypothetical_provenance(verified, q, family):
    """Provenance for the forecast's and the no-launch check's hypothetical
    bindings. It carries no record identities, is marked as such, is never
    written, and the loader's verify refuses it (A16 item 8)."""
    value = dict(family=family, round=q, hypothetical=True)
    if q == 2:
        value['round1'] = dict(tested_rows=sorted(k for k, t in verified['tests'].items() if t.get('reason') != 'N* not reached'))
    return value


def cannot_be_repaired(verified, q, family):
    """A16 item 10's mechanical check: grant C0 certification and the safeguard
    to every eligible row (the original eligible set at round 1; E2 at round 2,
    holding every round-1 decision fixed), apply the unchanged census/floor and
    A13 Part 2 through the A16 re-assembly; True when Part 2 still fails."""
    from .admission_a13 import binding
    granted = {k: dict(status='certified', visit_weighted_ok=True, n=0) for k, ok in verified['eligible'].items() if ok}
    after, sidecar, _ = reassemble(verified, granted, q, family)
    try:
        binding(after, sidecar, SCOPES[q], provenance=hypothetical_provenance(verified, q, family))
    except (ValueError, KeyError):
        return True
    return False


def prepare(history_path, projection_path, seed_inventory_path, output, *, round, registration=None,
            rehearsal=False, rehearsal_anchor=None, rehearsal_root=None, resume=False, compatibility_record=None, wall_hours=16.,
            non_launch_reserve_x2_hours=None, incurred_x2_hours=None, draws=None):
    """Reserve the family and round anchors before any preparation check, then
    verify the inventoried records, compute eligibility, constants, pricing,
    seeds and the forecast, and freeze the round's plan. Every failure after the
    reservation is recorded on the round record (A16 item 10).

    Registered preparation takes the launch packet's non-launch reserve and
    incurred charges explicitly (A16, Costs and ceilings) and uses exactly the
    forecast's 4,000 draws (A16 item 6); a rehearsal may default both. A
    rehearsal declares ``rehearsal_root``, under which every output and anchor
    lies (``preparation_outputs``)."""
    q = require_round(round)
    registered = registration is not None
    require(registered != bool(rehearsal), 'A16 requires exactly one of registered or rehearsal')
    require(math.isfinite(wall_hours) and wall_hours > 0, 'invalid A16 wall allowance')
    if registered:
        require(non_launch_reserve_x2_hours is not None and incurred_x2_hours is not None,
                "registered A16 preparation takes the launch packet's non-launch reserve and incurred charges explicitly")
        require(draws in (None, FORECAST_DRAWS), 'registered A16 preparation uses exactly %d forecast draws' % FORECAST_DRAWS)
    non_launch_reserve_x2_hours = 6. if non_launch_reserve_x2_hours is None else non_launch_reserve_x2_hours
    incurred_x2_hours = 0. if incurred_x2_hours is None else incurred_x2_hours
    draws = FORECAST_DRAWS if draws is None else draws
    # The family and the original record hashes come from the inventory alone;
    # everything else waits until the anchors exist.
    history_document = read(history_path)
    family, original_hashes, declared_round = _history_summary(history_document)
    require(declared_round == q, 'A16 history inventory was built for another round')
    stem = anchor_stem(family, registered=registered, rehearsal_anchor=rehearsal_anchor)
    # Every path this preparation writes, the history copies included, is
    # checked before the first write.
    output, root = preparation_outputs(output, stem, family=family, registered=registered, rehearsal_root=rehearsal_root,
                                       history=unseal(history_document))
    reserve_family(stem, family, original_hashes, registered=registered)
    request = dict(family=family, round=q, history_sha256=digest(history_document), output=str(output),
                   code_hash=code_identity(), registered=registered)
    anchor = reserve_round(stem, family, q, request, resume=resume, compatibility_record=compatibility_record)
    try:
        invocation = validate_invocation(output, dict(history=history_path, projection=projection_path, seed_inventory=seed_inventory_path),
                                         round=q, registration=registration, rehearsal=rehearsal, resume=resume)
        if registered:
            from .artifacts import verify_registration
            verify_registration(registration, instrument=unseal(history_document).get('instrument'))
        from .history_a16 import stage_history, verify_history
        from .forecast_a16 import forecast
        stage_history(history_document, unseal(history_document)['view_root'])
        verified = verify_history(history_document, round=q, registered=registered)
        h = verified['history']
        if file_hash(h.file(h.role('projection'))) != invocation['projection_file_hash']:
            raise Finding('finding: the priced projection differs from the inventoried projection')
        original = verified['original']
        eligible = {k for k, ok in verified['eligible'].items() if ok}
        E, E2 = verified['E'], (len(eligible) if q == 2 else None)
        if not eligible:
            raise Finding('A16 no-launch: no eligible row (E%s = 0)' % ('2' if q == 2 else ''))
        if cannot_be_repaired(verified, q, family):
            raise Finding('A16 no-launch: carried-forward defects fail Part 2 even with every eligible row certified')
        chosen = {}
        for jid, c in verified['sources'].items():
            rows = {k: p for k, p in c['eligible_rows'].items() if k in eligible}
            if rows:
                chosen[jid] = (c, rows)
        sources = [c['a1_job'] for c, _ in chosen.values()]
        pricing = price_round(original, invocation['projection'], sources, family=family, registered=registered,
                              projection_file_hash=invocation['projection_file_hash'])
        r_max = pricing['R_max']
        if r_max < R_FLOOR:
            raise Finding('A16 no-launch floor: R_max %d below %d' % (r_max, R_FLOOR))
        inventory = invocation['inventory']
        forbidden = {s for values in inventory['seeds'].values() for s in values}
        forbidden.update(int(j['seed']) for j in original['jobs'])
        forbidden.update(int(s) for s in verified['receipt']['stream_seeds'].values())
        forbidden.update(int(j['seed']) for j in verified['source_jobs'])
        # The recorded A16 manifests of any family and either round: the seeds
        # the inventory's verified A16 manifest sources contribute (never its
        # listed values) and, at round 2, this family's round-1 manifest (A16
        # item 3's occupancy rule, check_seed_manifest).
        recorded = set(inventory['recorded_a16_seeds'])
        if q == 2:
            forbidden.update(verified['round1']['forbidden_seeds'])
            own_prior = [r['seed'] for r in verified['round1']['seed_manifest']]
            forbidden.update(own_prior)
            recorded.update(own_prior)
        manifest = seed_manifest(family, q, sources, r_max, forbidden, rehearsal=rehearsal, recorded=recorded)
        allowance = launch_allowance(non_launch_reserve_x2_hours, incurred_x2_hours, pricing['projected_x2_hours'])
        selected = {k: verified['selected'][k] for k in eligible}
        probabilities = forecast(verified, r_max, family=family, round=q, eligible=sorted(selected), draws=draws, registered=registered)
        core = dict(schema=SCHEMA, code_hash=code_identity(), registered=registered, registered_a10=registered,
                    instrument=original['instrument'], registration=registration, tag='v3_tables', round=q,
                    a16_family=family, anchor_stem=None if registered else str(stem), rehearsal_root=None if registered else str(root),
                    family_record_path=str(family_record_path(stem)), round_record_path=str(anchor),
                    admission_record_path=str(admission_record_path_of(stem, q)),
                    target=TARGETS[family], calibration_path=original['calibration_path'], labels_policy=LABELS_POLICY[family],
                    history=history_document, classification=verified['classification'],
                    classification_sha256=verified['classification_sha256'],
                    original_plan_path=verified['original_plan_path'], original_plan_file_sha256=original_hashes['plan_file_sha256'],
                    original_plan_hash=original['plan_hash'], original_hashes=original_hashes,
                    round1_plan_hash=verified['round1']['plan_hash'] if q == 2 else None,
                    round1_seed_manifest=verified['round1']['seed_manifest'] if q == 2 else None,
                    M=original['M'], P=verified['P'], E=E, E2=E2, alpha=verified['alpha'],
                    eligibility=[dict(row=k, setting=s, eligible=bool(s == 'primary' and k in eligible)) for k, s in verified['row_settings']],
                    source_jobs=sorted(chosen), R_max=r_max, pricing=pricing, launch_allowed=True,
                    seed_manifest=manifest, forbidden_seeds=sorted(forbidden), recorded_a16_seeds=sorted(recorded),
                    seed_check=check_seed_manifest(manifest, forbidden, family=family, q=q, rehearsal=rehearsal, recorded=recorded),
                    seed_inventory_sha256=invocation['inventory_file_hash'],
                    forecast=probabilities, impossible_rows={k: p['n_star'] > 2048 * r_max for k, p in selected.items()},
                    wall_seconds=wall_hours * 3600, x2_equivalent_hours=allowance,
                    simulation_cap_x2_hours=PRICE_CAP_X2_HOURS, round_ceiling_x2_hours=ROUND_CEILING_X2_HOURS,
                    non_launch_reserve_x2_hours=non_launch_reserve_x2_hours, incurred_x2_hours=incurred_x2_hours,
                    non_registered_rehearsal=rehearsal, configuration_seconds=1800, cleanup_reserve_seconds=1200,
                    phases=[PHASES[q]], publication=None,
                    memory_estimate_gb={PHASES[q]: original['memory_estimate_gb']['validate_plain']})
        from .snapshot_a11 import normalize_historical_roots
        roots = normalize_historical_roots(unseal(history_document).get('historical_roots', []))
        if roots:
            core.update(historical_roots=roots, historical_roots_sha256=digest(roots))
        configs = []
        for jid, (old_config, rows) in sorted(chosen.items()):
            c = {k: deepcopy(old_config[k]) for k in ('route', 'a1_source_root', 'a1_job', 'a1_source_code_hash', 'fit', 'trajectory_count')}
            c.update(phase=PHASES[q], a16_family=family, a16_round=q, eligible_rows=rows, M=core['M'], R_max=r_max,
                     full_seed_manifest=manifest, forbidden_seeds=sorted(forbidden), recorded_a16_seeds=sorted(recorded),
                     non_registered_rehearsal=rehearsal, stream_seeds=[r['seed'] for r in manifest if r['source_job_id'] == jid])
            needed = {str((Path(c['a1_source_root']) / 'tables_A1/table' / directory / (c['a1_job']['id'] + '.json')).resolve())
                      for directory in ('outputs', 'records')}
            needed.add(str((SIMULATION / c['a1_job']['config']['calibration_path']).resolve()))
            if family in SIGMA_FAMILIES:
                # The variant calibration's validation reads the frozen nominal
                # parent (calibration._validate_a10_variant); the worker's closure
                # carries its hash-verified copy with its alias.
                needed.add(str((SIMULATION / NOMINAL_CALIBRATION).resolve()))
            c['a16_inputs'] = []
            for row in unseal(history_document)['files']:
                names = {str(Path(p).resolve()) for p in [row['source'], *row.get('aliases', [])]}
                for name in sorted(names & needed):
                    c['a16_inputs'].append(dict(deepcopy(row), source=name, aliases=sorted(names - {name})))
            require({str(Path(r['source']).resolve()) for r in c['a16_inputs']} == needed, 'A16 phase input inventory incomplete')
            if old_config.get('settings_override'):
                require(not registered, 'registered A16 cannot override scientific settings')
                c['settings_override'] = old_config['settings_override']
            configs.append(c)
        core['job_skeletons'] = configs
        core['plan_hash'] = plan_hash(core)
        core['jobs'] = [stable_job(KINDS[q], dict(c, plan_hash=core['plan_hash']), 'v3_tables', i) for i, c in enumerate(configs)]
        profiles = [dict(c, plan_hash=core['plan_hash'], configuration_test=True,
                         settings_override={**c.get('settings_override', {}), 'burn': 30, 'measure': 8},
                         seed=(1 << 128) | int(digest(['A16-configuration', family, q, core['plan_hash'], i])[:32], 16))
                    for i, c in enumerate(configs)]
        core['configuration'] = {PHASES[q]: dict(kind=KINDS[q], config=profiles[0], configs=profiles,
                                 workers_local=[2, 4, 8, 12], workers_x2=[8, 12, 16, 24, 32], threads=[1],
                                 rounds=1, jobs_local=12, jobs_x2=32, jobs_per_worker=2)}
        validate_plan(core)
        with lease(anchor.with_suffix('.lock')):
            record = unseal(read(anchor))
            require(record['state'] in ('preparing', 'prepared') and record['halt'] is None and record['root'] is None, 'A16 preparation no longer live')
            if record['plan_hash'] not in (None, core['plan_hash']):
                record['superseded_plan_hashes'].append(record['plan_hash'])
            record.update(plan_hash=core['plan_hash'])
            atomic_json(anchor, seal(record))
            for path, value in ((output, seal(core)), (output.with_suffix('.public.json'), seal(public_record(core)))):
                if path.exists():
                    # A frozen plan is immutable unless the round record has
                    # superseded it (a resume at a changed, compatible identity).
                    existing = read(path)
                    superseded = unseal(existing).get('plan_hash') in record['superseded_plan_hashes']
                    require(existing == value or superseded, 'A16 preparation record changed')
                    if superseded and existing != value:
                        atomic_json(path, value)
                else:
                    atomic_json(path, value)
            record['state'] = 'prepared'
            atomic_json(anchor, seal(record))
        return core
    except (OSError, MemoryError):
        raise  # An infrastructure interruption leaves state preparing for an explicit resume.
    except Finding as exc:
        record_failure(stem, q, 'finding: ' + str(exc), classification='substantive')
        raise
    except Exception as exc:
        record_failure(stem, q, type(exc).__name__ + ': ' + str(exc))
        raise


def public_record(plan):
    M, P, E = plan['M'], plan['P'], plan['E']
    bound = (plan['alpha'] * E / M) if M else 0.
    return dict(schema=SCHEMA + '-public', amendment='A16, prospective; proposer and approver knew stage 1 results (A16, Timing)',
                family=plan['a16_family'], round=plan['round'], original_refusal_preserved=True,
                round1_refusal_preserved=plan['round'] == 2, plan_hash=plan['plan_hash'],
                original_plan_hash=plan['original_plan_hash'], round1_plan_hash=plan['round1_plan_hash'],
                code_hash=plan['code_hash'], E=E, E2=plan['E2'], P=P, M=M, alpha=plan['alpha'],
                extension_error_bound=bound, family_error_bound_given_fit=(plan['alpha'] * (1 + P / M)) if M else 0.,
                family_error_bound_unconditional=2 * plan['alpha'] if M else 0.,
                plain_certificate_vacuous=M == 0,
                R_max=plan['R_max'], projected_x2_hours=plan['pricing']['projected_x2_hours'],
                price_cap_x2_hours=PRICE_CAP_X2_HOURS, round_ceiling_x2_hours=ROUND_CEILING_X2_HOURS,
                non_launch_reserve_x2_hours=plan['non_launch_reserve_x2_hours'], incurred_x2_hours=plan['incurred_x2_hours'],
                launch_x2_equivalent_hours=plan['x2_equivalent_hours'], launch_floor=R_FLOOR,
                eligibility=plan['eligibility'], source_jobs=plan['source_jobs'], impossible_rows=plan['impossible_rows'],
                seed_manifest=plan['seed_manifest'], seed_check=plan['seed_check'],
                historical_inventory=plan['history'], classification_sha256=plan['classification_sha256'],
                forecast=plan['forecast'], labels_policy=plan['labels_policy'], target=plan['target'])


# ---------------------------------------------------------------------------
# Re-assembly, admission and publication (A16 items 7, 8, 9 and 10)
# ---------------------------------------------------------------------------

def _marker(test):
    return dict(retest={k: test[k] for k in ('status', 'visit_weighted_ok')}, reason=test.get('reason'),
                tested=test.get('reason') != 'N* not reached')


def reassemble(verified, new_tests, q, family):
    """Start from the original refused candidate; replace only C0's decision for
    each original eligible row with the decision of the round that tested it
    or its terminal unreached decision (A16 item 8). The markers live at
    row['a16']['rounds']['r1'] and ['r2'], never under the nominal 'a13' key."""
    require_round(q)
    prior = deepcopy(verified['tests'])
    expected = {k for k, ok in verified['eligible'].items() if ok}
    require(set(new_tests) == expected, 'A16 decisions do not cover exactly the eligible set')
    tests = dict(prior)
    tests.update(new_tests)
    require(set(tests) == set(verified['selected']), 'A16 tests do not cover the original eligible set')
    rows, details = a13.reassemble(verified['rows'], verified['details'], verified['selected'], tests,
                                   verified['fits'], verified['censuses'])
    for key, test in tests.items():
        row = rows[key]
        marker = row.pop('a13')
        rounds = {}
        if q == 2:
            rounds['r1'] = _marker(prior[key])
            if key in new_tests:
                rounds['r2'] = _marker(new_tests[key])
        else:
            rounds['r1'] = _marker(test)
        tested = test.get('reason') != 'N* not reached'
        row['a16'] = dict(family=family, certified_by_extension=marker['certified_by_extension'],
                          tested_round=((2 if key in new_tests else 1) if q == 2 else 1) if tested else None, rounds=rounds)
        detail = next(d for d in details if d['row'] == key and d['setting'] == 'primary')
        replacement = next(t for t in detail['cell_tests'] if t['cell'] == a13.cv.POP0_CELL)
        replacement.pop('a13_extension', None)
        replacement['a16_extension'] = dict(family=family, round=row['a16']['tested_round'])
        detail['a16_retest'] = dict(family=family, round=row['a16']['tested_round'], test=deepcopy(test),
                                    classification_sha256=verified['classification_sha256'])
    a13.assert_ineligible_identity(verified['rows'], rows, verified['details'], details, set(verified['selected']))
    return rows, details, tests


def classification_entry(key, status, certified, test, tested_round):
    """One bound per-row classification: the row key, the decision, the test
    status, the safeguard result and the round that tested it (A16 item 7)."""
    return dict(row=key, decision=status, certified_by_extension=bool(certified), test_status=test['status'],
                safeguard=bool(test.get('visit_weighted_ok')), reason=test.get('reason'), round=tested_round)


def row_classifications(rows, tests):
    """Every row carrying an A16 marker, in key order, as the admission record
    binds them; round-2 preparation recomputes round 1's row by row."""
    result = []
    for key in sorted(rows):
        marker = rows[key].get('a16')
        if marker:
            result.append(classification_entry(key, rows[key]['status'], marker['certified_by_extension'], tests[key], marker['tested_round']))
    return result


def provenance(plan, stem, verified):
    """The item-10 records bound inside the admission (A16 item 8): the family
    anchor identity, the round identity, the plan hash and, at round 2, round
    1's plan, sealed admission record and tested set. ``admission_record`` adds
    the admission record's own identity; ``verify_provenance_records``
    cross-checks all of them against the on-disk records at publication."""
    family_record = unseal(read(family_record_path(stem)))
    round_record = unseal(read(round_record_path(plan)))
    require(family_record['family'] == plan['a16_family'] == round_record['family'] and round_record['round'] == plan['round']
            and round_record['plan_hash'] == plan['plan_hash'] and round_record['spec_hash'] == digest(plan), 'A16 provenance records differ from plan')
    value = dict(family=plan['a16_family'], round=plan['round'], plan_hash=plan['plan_hash'], spec_hash=digest(plan),
                 root=round_record['root'], original_plan_hash=plan['original_plan_hash'],
                 original_candidate_file_sha256=plan['original_hashes']['candidate_file_sha256'],
                 original_admission_record_sha256=plan['original_hashes']['admission_record_sha256'],
                 round1_plan_hash=plan['round1_plan_hash'], family_record_sha256=family_identity(family_record),
                 round_record_sha256=round_identity(round_record), target=plan['target'], labels_policy=plan['labels_policy'])
    if plan['round'] == 2:
        r1 = verified['round1']
        require(r1['plan_hash'] == plan['round1_plan_hash'], 'A16 round-1 plan differs from the verified history')
        value['round1'] = dict(plan_hash=r1['plan_hash'], admission_record_sha256=r1['admission_record_sha256'],
                               classifications_sha256=r1['classifications_sha256'], tested_rows=list(r1['tested_rows']))
    return value


def verify_provenance_records(plan, admission):
    """A16 item 8: the admission's bound provenance names the on-disk family
    anchor, round record and admission record of this plan."""
    stem = plan_stem(plan)
    bound = admission['a16']
    family_record = unseal(read(family_record_path(stem)))
    round_record = unseal(read(round_record_path(plan)))
    record = unseal(read(admission_record_path_of(stem, plan['round'])))
    require(bound['family'] == plan['a16_family'] == family_record['family'] == round_record['family'] == record['family']
            and bound['round'] == plan['round'] == round_record['round'] == record['round']
            and bound['plan_hash'] == plan['plan_hash'] == round_record['plan_hash'] == record['plan_hash']
            and bound['family_record_sha256'] == family_identity(family_record)
            and bound['round_record_sha256'] == round_identity(round_record)
            and bound['admission_record_sha256'] == admission_identity(record)
            and record['outcome'] == 'passed' and record['admitted_set_sha256'] == admission['admitted_set_sha256']
            and record['classifications_sha256'] == digest(record['classifications']),
            'A16 admission provenance differs from the on-disk anchor, round or admission records')
    return record


def admission_record(plan, rows, details, bound, test_counts, tests):
    from .admission_a13 import binding
    stem = plan_stem(plan)
    path = admission_record_path_of(stem, plan['round'])
    require(str(path) == plan['admission_record_path'], 'A16 admission record moved from its family anchor')
    scope = SCOPES[plan['round']]
    record = dict(schema='v3-A13-admission-check-1', scope=scope, plan_hash=plan['plan_hash'], family=plan['a16_family'],
                  round=plan['round'], primary_rows=len(rows), cap=len(rows) // 1000,
                  residual_rows=sorted(k for k, r in rows.items() if r['status'] == 'not_estimable'))
    record['residual_count'] = len(record['residual_rows'])
    record.update(test_counts)
    record.update(E=plan['E'], E2=plan['E2'], P=plan['P'], M=plan['M'], alpha=plan['alpha'],
                  extension_error_bound=(plan['alpha'] * plan['E'] / plan['M']) if plan['M'] else 0.)
    # The bound per-row classifications (A16 item 7), hashed, so round-2
    # preparation verifies round 1's recomputation row by row.
    record['classifications'] = row_classifications(rows, tests)
    record['classifications_sha256'] = digest(record['classifications'])
    bound = dict(bound, admission_record_sha256=admission_identity(record))
    error, result = None, None
    try:
        result = binding(rows, details, scope, provenance=bound)
        record.update(outcome='passed', admitted_set_sha256=result['admitted_set_sha256'])
    except (ValueError, KeyError) as exc:
        record['outcome'], error = 'refused', exc
    with lease(path.with_suffix('.lock')):
        document = seal(record)
        if path.exists():
            require(read(path) == document, 'A16 admission record is final')
        else:
            atomic_json(path, document)
    outcome = record['outcome']

    def mutate(value):
        if value['admission'] is None:
            value.update(admission=outcome, state='published' if outcome == 'passed' else 'refused_admission')
    _update(round_record_path(plan), mutate)
    if error is not None:
        if plan['round'] == 2:
            latch_family_terminal(stem, 'round 2 Part 2 refused; no third round', 2)
        raise error
    return result, file_hash(path)


def publish(plan, extension_root, target, *, registered=True):
    from .artifacts import verify_registration
    from .history_a16 import verify_history
    from .production_runner import completed
    from .production_tables import ProductionTables
    validate_plan(plan)
    q, family = plan['round'], plan['a16_family']
    target, root = scoped(target), scoped(extension_root)
    stem = plan_stem(plan)
    if registered:
        require(plan['registered'] and target == target_path(family), 'A16 registered target or plan differs')
        verify_registration(plan['registration'], instrument=plan['instrument'])
    else:
        # The fixture prohibition: a fixture publication never lands on a
        # registered target, an anchor or anything in the registered trees.
        require(not in_registered_tree(target) and not any(in_registered_tree(target.with_suffix(s)) for s in ('.compatibility.json', '.cell_results.json')),
                'A16 fixture publication refuses a registered target or anchor')
    publication_round(plan, root)
    verified = verify_history(plan['history'], round=q, registered=registered)
    require(verified['classification_sha256'] == plan['classification_sha256'] and verified['family'] == family,
            'historical classifications changed')
    new_tests, hashes = {}, {}
    for job in plan['jobs']:
        output = completed(root / PHASES[q], job, plan['code_hash'])
        require(output is not None, 'A16 incomplete; resume infrastructure interruption')
        result, c = output['result'], job['config']
        require(result['stage'] == PHASES[q] and result['plan_hash'] == plan['plan_hash'] and result['a1_job_id'] == c['a1_job']['id']
                and result['code_hash'] == plan['code_hash'] and result.get('a16_family') == family and result.get('a16_round') == q,
                'A16 result identity differs')
        replicates = validate_replicates(job, result['replicates'])
        stopped = stop_reached(replicates, c['eligible_rows'])
        require(result['stopped_on_visits'] == stopped and (stopped or len(replicates) == c['R_max']), 'A16 stopped early')
        hashes[job['id']] = file_hash(root / PHASES[q] / 'outputs' / (job['id'] + '.json'))
        for key, parameters in c['eligible_rows'].items():
            new_tests[key] = extension_test([dict(replicate=r['replicate'], trajectories=r['rows'][key]) for r in replicates], parameters, q)
    rows, details, tests = reassemble(verified, new_tests, q, family)
    test_counts = dict(tests_round1=sum(t.get('reason') != 'N* not reached' for t in (verified['tests'] if q == 2 else new_tests).values()),
                       tests_round2=sum(t.get('reason') != 'N* not reached' for t in new_tests.values()) if q == 2 else 0)
    bound = provenance(plan, stem, verified)
    admission, admission_hash = admission_record(plan, rows, details, bound, test_counts, tests)
    verify_provenance_records(plan, admission)
    summary = public_record(plan)
    summary.update(outcome='completed', **test_counts)
    payload = deepcopy(unseal(verified['candidate']))
    payload['manifest'].update(a16=summary, a13_admission=admission)
    payload.update(rows={k: seal(v) for k, v in rows.items()}, code_hash=code_identity(), fixture=not registered)
    payload['manifest_hash'] = digest(payload['manifest'])
    document = seal(payload)
    h = verified['history']
    original_sidecar = unseal(h.read(h.role('original_sidecar')))
    sidecar = seal(dict(original_sidecar, table_seal_sha256=document['sha256'], rows=details, a16=summary))
    public_path = Path(unseal(read(round_record_path(plan)))['request']['output']).with_suffix('.public.json')
    require(unseal(read(public_path)) == public_record(plan), 'A16 approved public record changed')
    rounds = {}
    if q == 2:
        r1 = verified['round1']
        rounds['r1'] = dict(plan_hash=r1['plan_hash'], public_file_sha256=r1['public_file_sha256'],
                            stage_output_sha256=r1['stage_output_sha256'], seed_manifest=r1['seed_manifest'],
                            admission_record_sha256=r1['admission_record_sha256'])
    rounds['r%d' % q] = dict(plan_hash=plan['plan_hash'], public_file_sha256=file_hash(public_path),
                            stage_output_sha256=hashes, seed_manifest=plan['seed_manifest'], admission_record_sha256=admission_hash)
    refusals = dict(original=dict(table_file_sha256=plan['original_hashes']['candidate_file_sha256'],
                                  sidecar_file_sha256=plan['original_hashes']['sidecar_file_sha256'],
                                  admission_record_sha256=plan['original_hashes']['admission_record_sha256']))
    if q == 2:
        refusals['round1_admission_record_sha256'] = verified['round1']['admission_record_sha256']
    receipt = dict(verified['receipt'], table_seal_sha256=document['sha256'],
                   table_file_sha256=hashlib.sha256(canonical(document) + b'\n').hexdigest(),
                   cell_results_sha256=hashlib.sha256(canonical(sidecar) + b'\n').hexdigest(), producer_code_hash=code_identity(),
                   a16=summary, a16_rounds=rounds,
                   extension_seed_manifest=[r for key in sorted(rounds) for r in rounds[key]['seed_manifest']],
                   refusals=refusals, labels_policy=plan['labels_policy'])
    require(receipt['plan_hash'] == verified['receipt']['plan_hash']
            and receipt['stream_seeds'] == verified['receipt']['stream_seeds'], 'original receipt fields changed')
    if registered:
        ProductionTables(document, calibration_hash=payload['manifest']['calibration_hash'], registered=True)
    if target.exists():
        require(read(target) == document, 'A16 publication target is frozen')
    a13.assert_ineligible_identity(verified['rows'], rows, verified['details'], details, set(verified['selected']))
    publication_round(plan, root)
    atomic_json(target.with_suffix('.compatibility.json'), seal(receipt))
    atomic_json(target.with_suffix('.cell_results.json'), sidecar)
    atomic_json(target, document)

    def mutate(record):
        if record.get('published_round') is None:
            record['published_round'] = q
        record['log'].append(dict(event='published', round=q, epoch=time.time(), table_file_sha256=receipt['table_file_sha256']))
    _update(family_record_path(stem), mutate)
    return document, receipt


def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    prep = commands.add_parser('prepare')
    for name in ('history', 'projection', 'seed-inventory', 'output'):
        prep.add_argument('--' + name, required=True)
    prep.add_argument('--round', type=int, choices=ROUNDS, required=True)
    modes = prep.add_mutually_exclusive_group(required=True)
    modes.add_argument('--registration', help='JSON file containing the committed registration pin')
    modes.add_argument('--rehearsal-anchor', help='non-registered rehearsal: the output-relative anchor stem')
    prep.add_argument('--rehearsal-root', help='non-registered rehearsal: the declared output root holding the plan, its public record and the anchors')
    prep.add_argument('--resume-preparation', action='store_true')
    prep.add_argument('--compatibility-record', help='direct A11 compatibility record for a resume at a changed code identity (A16 item 10)')
    prep.add_argument('--wall-hours', type=float, default=16.)
    prep.add_argument('--non-launch-reserve-hours', type=float, default=None,
                      help='X2-equivalent hours reserved for the round outside the launch (A16, Costs and ceilings); '
                           'required from the launch packet when registered, 6 by default for a rehearsal')
    prep.add_argument('--incurred-hours', type=float, default=None,
                      help='X2-equivalent hours already charged to this round; required when registered, 0 by default for a rehearsal')
    prep.add_argument('--draws', type=int, default=None,
                      help='forecast draws; a registered preparation uses exactly %d' % FORECAST_DRAWS)
    pub = commands.add_parser('publish')
    for name in ('plan', 'root', 'target'):
        pub.add_argument('--' + name, required=True)
    pub.add_argument('--fixture', action='store_true')
    end = commands.add_parser('decline')
    end.add_argument('--family', required=True, choices=FAMILIES)
    end.add_argument('--round', type=int, choices=ROUNDS, required=True)
    end.add_argument('--rehearsal-anchor')
    end.add_argument('--operator', required=True)
    end.add_argument('--reason', required=True)
    classify = commands.add_parser('classify-failure')
    classify.add_argument('--family', required=True, choices=FAMILIES)
    classify.add_argument('--round', type=int, choices=ROUNDS, required=True)
    classify.add_argument('--rehearsal-anchor')
    classify.add_argument('--index', type=int, required=True)
    classify.add_argument('--classification', choices=('tooling', 'substantive'), required=True)
    classify.add_argument('--reviewer', required=True)
    args = parser.parse_args()
    if args.command == 'prepare':
        plan = prepare(args.history, args.projection, args.seed_inventory, args.output, round=args.round,
                       registration=read(args.registration) if args.registration else None,
                       rehearsal=args.rehearsal_anchor is not None, rehearsal_anchor=args.rehearsal_anchor, rehearsal_root=args.rehearsal_root,
                       resume=args.resume_preparation, compatibility_record=args.compatibility_record, wall_hours=args.wall_hours,
                       non_launch_reserve_x2_hours=args.non_launch_reserve_hours, incurred_x2_hours=args.incurred_hours,
                       draws=args.draws)
        print('A16 round %d prepared for %s; public record: %s' % (plan['round'], plan['a16_family'],
                                                                     Path(args.output).with_suffix('.public.json')))
    elif args.command == 'publish':
        publish(unseal(read(args.plan)), args.root, args.target, registered=not args.fixture)
        print('A16 family published.')
    elif args.command == 'decline':
        stem = anchor_stem(args.family, registered=args.rehearsal_anchor is None, rehearsal_anchor=args.rehearsal_anchor)
        decline(stem, args.round, operator=args.operator, reason=args.reason)
        print('A16 round declined; the family sequence is final.')
    else:
        stem = anchor_stem(args.family, registered=args.rehearsal_anchor is None, rehearsal_anchor=args.rehearsal_anchor)
        classify_failure(stem, args.round, args.index, args.classification, args.reviewer)
        print('A16 failure classified as %s.' % args.classification)


if __name__ == '__main__':
    main()
