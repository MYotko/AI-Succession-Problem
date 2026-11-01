"""A16 item 6: the predicted admission probability before each round's go.

A family-general, prespecified adapter of A14 item 6's model, for a family and
round that A14's three frozen nominal scripts cannot run unchanged. It is
non-simulation tooling: it draws no trajectory, uses no reserved stream and
never chooses R_max. Its public output holds the two three-decimal estimates
and counts, never N*, visits or values. The figures are an operational budget
estimate of admission probability resting on the model below, neither a
certified probability nor a registered reading; the operator's recorded go
decides.
"""
from copy import deepcopy
import hashlib
import math
import platform
import random

from .artifacts import ROOT, canonical, file_hash

SCHEMA = 'v3-A16-forecast-1'
DRAWS = 4000
SENSITIVITY_CERTIFICATION = .9
_round = round  # the public interface names the round ``round``, as the other A16 entry points do
# The repository modules whose source the forecast records (A16 item 6: freeze
# source/import hashes). The Part 2 predicates come from admission_a13 unchanged.
IMPORTS = ('artifacts.py', 'admission_a13.py', 'validation_extension_a13.py', 'validation_extension_a16.py',
           'continuation_validation.py', 'production_tables.py', 'policies.py', 'forecast_a16.py')


def forecast_seed(family, q, r_max):
    """The low 60 bits of SHA-256 of canonical JSON ["A16-admission-forecast", family, q, R_max]."""
    return int(hashlib.sha256(canonical(['A16-admission-forecast', family, q, r_max])).hexdigest(), 16) & ((1 << 60) - 1)


def normal_cdf(z):
    return .5 * math.erfc(-z / math.sqrt(2.))


def reach_probability(visits, trajectories, n_star, new_trajectories):
    """Beta(v+1, t-v+1) posterior for the visit probability from v visiting
    trajectories among t simulated; a beta-binomial visiting count among the
    new trajectories, by the normal approximation with continuity correction
    at N* - 0.5; clamped to [0, 1]. Invalid inputs halt."""
    for value in (visits, trajectories, n_star, new_trajectories):
        if type(value) is not int or value < 0:
            raise ValueError('forecast inputs must be non-negative integers')
    if visits > trajectories or n_star < 1 or new_trajectories < 1:
        raise ValueError('forecast visits exceed trajectories or empty round')
    a, b, n = visits + 1, trajectories - visits + 1, new_trajectories
    mean = n * a / (a + b)
    variance = n * a * b * (a + b + n) / ((a + b) ** 2 * (a + b + 1))
    if not math.isfinite(mean) or not math.isfinite(variance) or variance < 0:
        raise ValueError('forecast moments are not finite')
    if variance == 0:
        probability = 1. if mean >= n_star else 0.
    else:
        probability = 1. - normal_cdf((n_star - .5 - mean) / math.sqrt(variance))
    return min(1., max(0., probability))


def prior_rates(tests):
    """Round 1: the disclosed 1/0 assumption. Round 2: the empirical rates of
    this family's round-1 tests, or the same assumption if none occurred.
    Certification means the C0 test certifies and its safeguard passes."""
    tested = [t for t in tests.values() if t.get('reason') != 'N* not reached']
    if not tested:
        return dict(certification=1., violation=0., tests=0, basis='assumed 1/0: no prior extension test')
    certified = sum(t['status'] == 'certified' and bool(t.get('visit_weighted_ok')) for t in tested)
    violated = sum(t['status'] == 'violation' for t in tested)
    return dict(certification=certified / len(tested), violation=violated / len(tested), tests=len(tested),
                basis='empirical round-1 test rates')


def floor_with_c0(row, census):
    """The unchanged census floor with C0 added to the row's validated support."""
    from . import continuation_validation as cv
    support = {int(cv.fine_codes([e['bin']])[0]) for e in row['continuation']['entries']} | {int(cv.POP0_CELL)}
    return bool(cv.census_floor(cv.census_fractions_from_counts(census, support, 'plain'))['passed'])


def _scenario(base_rows, details, eligible, q, family, reach, floor_ok, certification, violation, seed, draws, provenance):
    """Monte Carlo over the Part 2 predicates. Draw order: for each draw, each
    eligible row in canonical (sorted key) order takes one uniform for reach and,
    when reached, one uniform for its category. Every simulated final status
    passes through the unchanged admission_a13.binding under the hypothetical
    provenance, which the loader never admits."""
    from .admission_a13 import binding
    from .validation_extension_a16 import SCOPES
    if not 0. <= certification <= 1. or not 0. <= violation <= 1. or certification + violation > 1. + 1e-12:
        raise ValueError('forecast rates must be probabilities summing to at most one')
    rng = random.Random(seed)
    rows = deepcopy(base_rows)
    marker = 'r%d' % q
    passed = 0
    for _ in range(draws):
        for key in eligible:
            row = rows[key]
            reached = rng.random() < reach[key]
            category = None
            if reached:
                u = rng.random()
                category = 'certified' if u < certification else 'violation' if u < certification + violation else 'unresolved'
            estimated = reached and category == 'certified' and floor_ok[key]
            row['status'] = row['primary_status'] = 'estimated' if estimated else 'not_estimable'
            if estimated:
                row.pop('reason', None)
                row['primary_reason'] = None
            else:
                row['reason'] = row['primary_reason'] = 'A4 availability floor failed'
            row['a16']['certified_by_extension'] = bool(estimated)
            row['a16']['tested_round'] = q if reached else None
            row['a16']['rounds'][marker] = dict(retest=dict(status=category or 'unresolved', visit_weighted_ok=category == 'certified'),
                                               reason=None if reached else 'N* not reached', tested=bool(reached))
        try:
            binding(rows, details, SCOPES[q], provenance=provenance)
            passed += 1
        except (ValueError, KeyError):
            pass
    return passed / draws


def forecast(verified, r_max, *, family, round, eligible, draws=DRAWS, registered=False):
    """The two required numbers for a round: P(every Part 2 condition) at the
    baseline rates and at certification 0.9 with violation 0, both from the same
    seed and draw order (A16 item 6). A registered forecast uses exactly DRAWS
    draws; a rehearsal may pass another count, recorded as non-registered."""
    from .validation_extension_a16 import require_family, require_round, reassemble, hypothetical_provenance
    q = require_round(round)
    require_family(family)
    frozen = sorted(k for k, ok in verified['eligible'].items() if ok)
    if sorted(eligible) != frozen:
        raise ValueError('finding: forecast eligible set differs from the frozen eligible set')
    if type(r_max) is not int or r_max < 1 or type(draws) is not int or draws < 1:
        raise ValueError('forecast needs a positive integer R_max and draw count')
    if registered and draws != DRAWS:
        raise ValueError('registered A16 forecast uses exactly %d draws' % DRAWS)
    provenance = hypothetical_provenance(verified, q, family)
    counts = {key: c['trajectory_count'] for c in verified['sources'].values() for key in c['eligible_rows']}
    reach, floor_ok = {}, {}
    for key in frozen:
        v = verified['visits'][key]
        visits, trajectories = v['original_visits'], v['original_trajectories']
        if q == 2:
            visits += v['round1_visits']
            trajectories += v['round1_trajectories']
        reach[key] = reach_probability(visits, trajectories, verified['selected'][key]['n_star'], r_max * counts[key])
        floor_ok[key] = floor_with_c0(verified['rows'][key], verified['censuses'][key])
    # The base rows carry every fixed decision (round 1's at round 2) through the
    # unchanged re-assembly, with the prospective rows at their unreached state.
    unreached = {k: dict(status='unresolved', reason='N* not reached', n=0, visit_weighted_ok=False) for k in frozen}
    base_rows, details, _ = reassemble(verified, unreached, q, family)
    rates = prior_rates(verified['tests']) if q == 2 else dict(certification=1., violation=0., tests=0,
                                                              basis='assumed 1/0: round 1 has no prior extension test')
    seed = forecast_seed(family, q, r_max)
    baseline = _scenario(base_rows, details, frozen, q, family, reach, floor_ok, rates['certification'], rates['violation'], seed, draws, provenance)
    sensitivity = _scenario(base_rows, details, frozen, q, family, reach, floor_ok, SENSITIVITY_CERTIFICATION, 0., seed, draws, provenance)
    try:
        import numpy
        numpy_version = numpy.__version__
    except ImportError:  # pragma: no cover
        numpy_version = None
    return dict(schema=SCHEMA, family=family, round=q, R_max=r_max, draws=draws, registered=bool(registered), seed=seed,
                eligible_rows=len(frozen), p_all_part2=_round(baseline, 3),
                p_all_part2_certification_0_9=_round(sensitivity, 3), rates=rates,
                sensitivity_rates=dict(certification=SENSITIVITY_CERTIFICATION, violation=0.),
                standing='operational budget estimate of admission probability; neither a certified probability nor a registered reading; the operator\'s recorded go decides',
                model=dict(reach='Beta(v+1, t-v+1) posterior visit probability; beta-binomial visiting count among 2048 x R_max new trajectories; normal approximation with continuity correction at N* - 0.5; clamped to [0, 1]',
                           rows='independent row reach in this forecast only; categorical certification/violation/unresolved conditional on reaching N*; certification means the C0 test certifies and its safeguard passes; the census floor is applied separately; already-tested decisions are preserved',
                           predicates='every simulated final status passes through the unchanged admission_a13 Part 2 predicates',
                           draw_order='random.Random(seed) afresh per scenario; one uniform per eligible row for reach, then one for its category when reached, in canonical row order',
                           trajectories='original 3 x trajectory_count plus 2048 x the realized round-1 replicates at round 2'),
                assumptions=['cross-row independence of reach (forecast only, not the error bound)',
                             'round-1 rates are small-sample estimates at round 2; the assumed 1/0 rates at round 1',
                             'the normal approximation to the beta-binomial tail'],
                tooling=dict(source_sha256=file_hash(__file__), python=platform.python_version(), numpy=numpy_version,
                             repository_imports={name: file_hash(ROOT / name) for name in IMPORTS}))
