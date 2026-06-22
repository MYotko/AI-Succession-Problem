"""Report generation for the Bootstrap Gate Validator (text and JSON)."""

import json


# Keys to surface in the text report on PASS for v2.0 checks. These are the
# substantive measurements the operator wants visible without inspecting the
# JSON output. Failed checks still dump full details.
_PASS_HIGHLIGHT_KEYS = {
    'G2.1': ('peak_phi', 'differential', 'two_se_threshold', 'peak_in_range'),
    'G2.2': ('alphas', 'cap_stars', 'monotonic_non_increasing',
             'net_decrease_low_to_high'),
    'G2.4': ('interaction_type', 'phi_effect_at_low_alpha',
             'phi_effect_at_high_alpha'),
    'G4.1': ('active_runaway_observations', 'relative_tolerance',
             'failure_count'),
    'G4.2': ('regime_count', 'min_below_fire_rate',
             'max_above_fire_rate', 'min_separation_standard_errors'),
    'G4.3': ('theta_floor', 'min_observed_theta_tech',
             'observations_below_floor', 'extreme_runaway_observations'),
}


def format_text_report(results):
    """Format results as a human-readable text report."""
    lines = []
    lines.append('=' * 60)
    lines.append('BOOTSTRAP GATE VALIDATION REPORT')
    lines.append(f'Substrate: {results["substrate_id"]}')
    lines.append(f'Date: {results["report_date"]}')
    lines.append(f'Framework: {results["framework_version"]}')
    lines.append('=' * 60)
    lines.append('')

    for gate in results['gates']:
        status = gate.get('status', '')
        if status in ('NOT_APPLICABLE', 'NOT_IMPLEMENTED', 'NO_DATA'):
            lines.append(
                f'Gate {gate["gate"]}: {gate.get("name", "")} - {status}'
            )
            if 'reason' in gate:
                lines.append(f'  Reason: {gate["reason"]}')
        else:
            passed = 'PASSED' if gate['passed'] else 'FAILED'
            lines.append(
                f'Gate {gate["gate"]}: {gate.get("name", "")} - {passed}'
            )
            for check in gate.get('checks', []):
                chk = 'PASS' if check['passed'] else 'FAIL'
                lines.append(
                    f'  [{chk}] {check["equation"]}: {check["name"]}'
                )
                details = check.get('details', {})
                if not check['passed']:
                    for k, v in details.items():
                        lines.append(f'         {k}: {v}')
                else:
                    highlight_keys = _PASS_HIGHLIGHT_KEYS.get(check['equation'], ())
                    for k in highlight_keys:
                        if k in details:
                            lines.append(f'         {k}: {details[k]}')
        lines.append('')

    lines.append('=' * 60)
    if results.get('overall_passed') is True:
        lines.append(
            f'OVERALL: PASSED (cleared through Gate '
            f'{results["highest_gate_cleared"]})'
        )
    elif results.get('overall_passed') is False:
        lines.append('OVERALL: FAILED')
    else:
        lines.append('OVERALL: INSUFFICIENT DATA')
    lines.append('=' * 60)

    return '\n'.join(lines)


def format_json_report(results):
    """Format results as pretty-printed JSON."""
    return json.dumps(results, indent=2)
