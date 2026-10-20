"""A13 residual-row admission and observation-only decision incidence."""
from collections import Counter
from .artifacts import canonical, digest

SCHEMA = 'v3-A13-admission-1'
MISSING = 'missing_or_not_estimable_row'
BRANCHES = ('ordinary_allocation', 'survival_first', 'yield_review')


def context_key(row):
    from .production_tables import row_key
    return row_key(dict(row, rule_id=''))


def binding(rows, details, scope):
    """Bind every residual primary row and its tests; never change its status."""
    if scope not in ('A10_nominal_after_A13', 'validation_launched_under_A13', 'A10_nominal_after_A14'):
        raise ValueError('A13 admission scope is not authorized')
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
    result['admitted_set_sha256'] = digest(evidence)
    verify(rows, result)
    return result


def verify(rows, admission):
    """Independent loader check, including the unchanged sensitivity/support gates."""
    from .policies import execution_policy_class
    if (admission.get('schema') != SCHEMA or admission.get('scope') not in
            ('A10_nominal_after_A13', 'validation_launched_under_A13', 'A10_nominal_after_A14')):
        raise ValueError('invalid A13 admission binding or scope')
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
