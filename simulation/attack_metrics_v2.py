"""Pure count and seed-paired attack metrics for v2.

No function computes or returns a ratio of two measured counts. D5 identifies
an existing stochastic floor in per-vote quantities; D6 identifies the
endogenous denominator in the retired blocked/met quantity. These functions
provide action-change counts and paired differences, with the requested
sample standard error and t statistic. They perform no I/O or simulation and
maintain no global state.
"""


def _action_modified_value(value):
    """Parse a recorded Boolean without treating the string False as true."""
    if isinstance(value, bool):
        return value
    if isinstance(value, int) and value in (0, 1):
        return bool(value)
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in ('true', '1'):
            return True
        if normalized in ('false', '0'):
            return False
    raise ValueError('action_modified must be a Boolean, 0/1, or its CSV text')


def action_change_count(records):
    """Return (n_runs, n_action_modified), counting action_modified only.

    Missing fields and invalid Boolean values raise; no rate is returned.
    The input records are not modified.
    """
    n_runs = 0
    n_action_modified = 0
    for record in records:
        modified = _action_modified_value(record['action_modified'])
        n_runs += 1
        n_action_modified += int(modified)
    return n_runs, n_action_modified


def _index_by_seed(records):
    """Index unique, non-null seeds by both type and value, without coercion."""
    indexed = {}
    for record in records:
        seed = record['seed']
        if seed is None:
            raise ValueError('seed must not be null')
        key = (type(seed), seed)
        try:
            duplicate = key in indexed
        except TypeError as exc:
            raise ValueError('seed must be hashable') from exc
        if duplicate:
            raise ValueError('duplicate seed: ' + repr(seed))
        indexed[key] = record
    return indexed


def paired_difference(treatment, control, field):
    """Return a mapping of the four paired statistics and an explicit t note.

    Keys are n_pairs, mean_difference, paired_standard_error, t_statistic,
    and t_statistic_note. Differences are treatment minus control. Standard
    error uses sample standard deviation (ddof=1) divided by sqrt(n_pairs).
    When standard error is exactly zero, t_statistic is None and the note
    explains why. Otherwise the note is None.

    Pairing is exact and total: seed types and values must match, seeds must
    be unique, and at least two pairs are required for sample variance.
    Missing fields, non-finite values, and invalid pairing raise. Inputs are
    not modified, and no unmatched seed is silently discarded.
    """
    import math
    import statistics

    treatment_by_seed = _index_by_seed(treatment)
    control_by_seed = _index_by_seed(control)
    treatment_only = treatment_by_seed.keys() - control_by_seed.keys()
    control_only = control_by_seed.keys() - treatment_by_seed.keys()
    if treatment_only or control_only:
        raise ValueError(
            'seed sets must match exactly; treatment-only seeds: '
            + repr([key[1] for key in treatment_only])
            + '; control-only seeds: '
            + repr([key[1] for key in control_only])
        )
    n_pairs = len(treatment_by_seed)
    if n_pairs < 2:
        raise ValueError('at least two matched pairs are required for ddof=1')

    differences = []
    for key, treatment_record in treatment_by_seed.items():
        treatment_value = float(treatment_record[field])
        control_value = float(control_by_seed[key][field])
        difference = treatment_value - control_value
        if not all(math.isfinite(value) for value in
                   (treatment_value, control_value, difference)):
            raise ValueError('paired values and differences must be finite')
        differences.append(difference)
    mean_difference = statistics.fmean(differences)
    paired_standard_error = statistics.stdev(differences) / math.sqrt(n_pairs)
    if paired_standard_error == 0.0:
        t_statistic = None
        t_note = 'Paired standard error is exactly zero; t statistic is undefined.'
    else:
        t_statistic = mean_difference / paired_standard_error
        t_note = None
    return {
        'n_pairs': n_pairs,
        'mean_difference': mean_difference,
        'paired_standard_error': paired_standard_error,
        't_statistic': t_statistic,
        't_statistic_note': t_note,
    }
