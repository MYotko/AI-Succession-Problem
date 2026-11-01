"""A13 residual-row admission and observation-only decision incidence."""
from collections import Counter
from .artifacts import canonical, digest

SCHEMA = 'v3-A13-admission-1'
MISSING = 'missing_or_not_estimable_row'
BRANCHES = ('ordinary_allocation', 'survival_first', 'yield_review')
# A16 item 8: the stage 2 scopes carry bound family and round provenance.
A16_SCOPES = {'A10_stage2_after_A16_r1': 1, 'A10_stage2_after_A16_r2': 2}
SCOPES = ('A10_nominal_after_A13', 'validation_launched_under_A13', 'A10_nominal_after_A14') + tuple(A16_SCOPES)


def context_key(row):
    from .production_tables import row_key
    return row_key(dict(row, rule_id=''))


def _hash(value):
    return isinstance(value, str) and len(value) == 64 and all(c in '0123456789abcdef' for c in value)


def _a16_provenance(scope, provenance, *, hypothetical=False):
    """A16 scopes require bound provenance; the others refuse it. The provenance
    binds the item-10 records (A16 item 8): the family anchor identity, the
    round identity, the plan hash and the admission record's identity, and at
    round 2 round 1's plan hash, sealed admission record and tested set. A
    provenance marked hypothetical (the forecast and the no-launch check) is
    accepted only where the caller says so and is never admitted by the loader."""
    if scope not in A16_SCOPES:
        if provenance is not None:
            raise ValueError('admission provenance belongs to the A16 scopes only')
        return None
    from .validation_extension_a16 import FAMILIES
    if (not isinstance(provenance, dict) or provenance.get('family') not in FAMILIES
            or provenance.get('round') != A16_SCOPES[scope]):
        raise ValueError('A16 admission requires bound family and round provenance')
    q = A16_SCOPES[scope]
    round1 = provenance.get('round1')
    if q == 2 and (not isinstance(round1, dict) or not isinstance(round1.get('tested_rows'), list)
                   or not all(isinstance(k, str) for k in round1['tested_rows'])):
        raise ValueError('A16 round-2 admission requires round 1\'s tested set in its provenance')
    if q == 1 and round1 is not None:
        raise ValueError('A16 round-1 admission carries no round-1 provenance')
    if provenance.get('hypothetical') is True:
        if not hypothetical:
            raise ValueError('hypothetical A16 provenance is never admitted')
        return dict(provenance)
    if 'hypothetical' in provenance:
        raise ValueError('A16 provenance marks hypothetical bindings with True only')
    if not all(_hash(provenance.get(k)) for k in ('plan_hash', 'family_record_sha256', 'round_record_sha256', 'admission_record_sha256')):
        raise ValueError('A16 admission provenance lacks its bound record identities')
    if q == 2 and not all(_hash(round1.get(k)) for k in ('plan_hash', 'admission_record_sha256', 'classifications_sha256')):
        raise ValueError('A16 round-2 admission provenance lacks round 1\'s record identities')
    return dict(provenance)


def binding(rows, details, scope, provenance=None):
    """Bind every residual primary row and its tests; never change its status."""
    if scope not in SCOPES:
        raise ValueError('A13 admission scope is not authorized')
    hypothetical = isinstance(provenance, dict) and provenance.get('hypothetical') is True
    a16 = _a16_provenance(scope, provenance, hypothetical=hypothetical)
    primary = {d['row']: d for d in details if d['setting'] == 'primary'}
    residual = {key: row for key, row in rows.items() if row['status'] == 'not_estimable'}
    evidence = {}
    for key, row in residual.items():
        # The loader needs classifications, never executor-only visit counts
        # (an extension n_traj could reveal N*). Full tests stay in the sidecar.
        tests = [{'cell': t['cell'], 'eb': t.get('eb', t.get('status'))}
                 for t in primary[key]['cell_tests']]
        evidence[key] = {'row_sha256': digest(row), 'cell_tests': tests,
                         'cell_tests_sha256': digest(tests)}
    result = {'schema': SCHEMA, 'scope': scope, 'primary_rows': len(rows), 'rows': evidence}
    if a16 is not None:
        result['a16'] = a16
    result['admitted_set_sha256'] = digest(evidence)
    verify(rows, result, hypothetical=hypothetical)
    return result


def _verify_a16_markers(rows, a16):
    """A16 item 8 over every row of the candidate, not only the residual rows:
    a stage 2 row never carries the nominal marker; every marker names the
    admitted family; a violation in either round refuses admission whatever
    the row's status; round 2 keeps every round-1 marker, and the rows round 1
    tested are exactly the tested set of its sealed admission evidence."""
    tested_round1 = set()
    for key, row in rows.items():
        marker = row.get('a16')
        if a16 is None:
            if marker:
                raise ValueError('A16 marker outside an A16 admission scope')
            continue
        if 'a13' in row:
            raise ValueError('A16 row carries a nominal-round marker')
        if not marker:
            continue
        if marker.get('family') != a16['family']:
            raise ValueError('A16 row belongs to another family')
        rounds = marker.get('rounds') or {}
        if any(r.get('retest', {}).get('status') == 'violation' for r in rounds.values()):
            raise ValueError('A16 extension violation cannot be admitted')
        if a16['round'] == 2:
            if 'r1' not in rounds:
                raise ValueError('A16 round 2 cannot hide a round-1 marker')
            if rounds['r1'].get('tested'):
                tested_round1.add(key)
    if a16 is not None and a16['round'] == 2 and tested_round1 != set(a16['round1']['tested_rows']):
        raise ValueError('A16 rows carrying round-1 test markers differ from the sealed round-1 tested set')


def verify(rows, admission, *, hypothetical=False):
    """Independent loader check, including the unchanged sensitivity/support gates."""
    from .policies import execution_policy_class
    if admission.get('schema') != SCHEMA or admission.get('scope') not in SCOPES:
        raise ValueError('invalid A13 admission binding or scope')
    a16 = admission.get('a16')
    if (admission['scope'] in A16_SCOPES) != (a16 is not None):
        raise ValueError('A16 admission provenance missing or misplaced')
    if a16 is not None:
        a16 = _a16_provenance(admission['scope'], a16, hypothetical=hypothetical)
    _verify_a16_markers(rows, a16)
    entries = admission['rows']
    if admission.get('primary_rows') != len(rows) or admission.get('admitted_set_sha256') != digest(entries):
        raise ValueError('A13 admitted-set binding mismatch')
    residual = {k for k, r in rows.items() if r['status'] == 'not_estimable'}
    if set(entries) != residual:
        raise ValueError('not_estimable row outside A13 admitted set')
    if len(entries) > len(rows) // 1000:
        raise ValueError('A13 residual-row cap exceeded')
    contexts = set()
    balanced = execution_policy_class()[0].rule_id
    for key, evidence in entries.items():
        row = rows[key]
        tests = evidence['cell_tests']
        if evidence.get('row_sha256') != digest(row) or evidence.get('cell_tests_sha256') != digest(tests):
            raise ValueError('A13 admitted row or cell evidence hash mismatch')
        context = context_key(row)
        if context in contexts:
            raise ValueError('A13 permits at most one admitted row per lookup context')
        contexts.add(context)
        if row['rule_id'] == balanced:
            raise ValueError('A13 excludes the balanced witness')
        a4 = row.get('a4', {})
        support = bool(row.get('continuation', {}).get('entries')) or (row.get('route') == 'plain' and row.get('c0') is not None)
        if (row.get('reason') != 'A4 availability floor failed' or not a4.get('base_screens_ok')
                or a4.get('validated_support_size', 0) <= 0 or not support
                or a4.get('floor', {}).get('passed') is not False
                or row.get('sensitivity', {}).get('passed') is False):
            raise ValueError('A13 admitted row failed an existing screen or lacks support')
        if not tests or any(t.get('eb', t.get('status')) == 'violation' for t in tests):
            raise ValueError('A13 admitted row has missing tests or a violation')
        retest = row.get('a13', {}).get('retest', {})
        if retest.get('status') == 'violation':
            raise ValueError('A13 extension violation cannot be admitted')
        # The A16 marker checks ran over every row above (_verify_a16_markers).
    return set(entries)


def checked_binding(rows, details, scope, record_path, plan_hash):
    """Record Part 2 before publication, including a sealed refusal on failure.

    This public record contains identifiers and counts only. It deliberately
    carries neither cell evidence nor exception text from executor-only data.
    """
    from .artifacts import atomic_json, seal
    record = dict(schema='v3-A13-admission-check-1', scope=scope, plan_hash=plan_hash,
                  primary_rows=len(rows), cap=len(rows) // 1000,
                  residual_rows=sorted(k for k, r in rows.items() if r['status'] == 'not_estimable'))
    record['residual_count'] = len(record['residual_rows'])
    try:
        result = binding(rows, details, scope)
    except (ValueError, KeyError):
        atomic_json(record_path, seal(dict(record, outcome='refused')))
        raise
    atomic_json(record_path, seal(dict(record, outcome='passed', admitted_set_sha256=result['admitted_set_sha256'])))
    return result


def enabled(tables):
    return bool(getattr(tables, 'payload', {}).get('manifest', {}).get('a13_admission', {}).get('rows'))


def allocation_decision(evaluation, eligible, survival_first, chosen, fallback_reason):
    """Observe the pre-review selection. A survival-first early return excludes none."""
    reasons = getattr(evaluation.lookup, 'unavailable_reasons', (None,) * len(eligible))
    import numpy as np
    eligible = np.asarray(eligible, dtype=bool)
    early = survival_first and not (eligible & evaluation.available).any()
    excluded = Counter(reasons[i] for i in range(len(eligible))
                       if eligible[i] and not evaluation.available[i] and not early)
    selected = reasons[chosen] if not evaluation.available[chosen] else None
    return {'branch': 'survival_first' if survival_first else 'ordinary_allocation',
            'evaluated': True, 'affected': bool(excluded[MISSING] or (survival_first and selected == MISSING)),
            'excluded_by_reason': dict(excluded), 'balanced_fallback_reason': fallback_reason,
            'selected_score_unavailable_reason': selected if survival_first else None}


def yield_decision(excluded):
    return {'branch': 'yield_review', 'evaluated': True, 'affected': bool(excluded.get(MISSING, 0)),
            'excluded_by_reason': dict(excluded), 'balanced_fallback_reason': None,
            'selected_score_unavailable_reason': None}


def summarize(decisions):
    result = {}
    for branch in BRANCHES:
        selected = [d for d in decisions if d['branch'] == branch and d['evaluated']]
        numerator, denominator = sum(d['affected'] for d in selected), len(selected)
        excluded, fallbacks, unscored = Counter(), Counter(), Counter()
        for d in selected:
            excluded.update(d['excluded_by_reason'])
            if d['balanced_fallback_reason']:
                fallbacks[d['balanced_fallback_reason']] += 1
            if d['selected_score_unavailable_reason']:
                unscored[d['selected_score_unavailable_reason']] += 1
        result[branch] = {'numerator': numerator, 'denominator': denominator,
                          'rate': numerator / denominator if denominator else None,
                          'assessed': bool(denominator), 'excluded_by_reason': dict(excluded),
                          'balanced_fallbacks_by_reason': dict(fallbacks),
                          'survival_first_unavailable_selections_by_reason': dict(unscored)}
    return result


def pooled_incidence(runs):
    """Reading helper: caller supplies its predefined contributing run set."""
    pooled = {}
    for branch in BRANCHES:
        rows = [r[branch] for r in runs]
        n, d = sum(r['numerator'] for r in rows), sum(r['denominator'] for r in rows)
        pooled[branch] = {'numerator': n, 'denominator': d, 'rate': n / d if d else None,
                          'assessed': bool(d), 'per_run_rates': [r['rate'] for r in rows]}
    return {'branches': pooled, 'affected_by_table_unavailability': any(r['numerator'] for r in pooled.values())}
