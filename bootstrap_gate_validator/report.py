"""Report generation for the Bootstrap Gate Validator (text and JSON)."""

import json


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
                f'Gate {gate["gate"]}: {gate.get("name", "")} — {status}'
            )
            if 'reason' in gate:
                lines.append(f'  Reason: {gate["reason"]}')
        else:
            passed = 'PASSED' if gate['passed'] else 'FAILED'
            lines.append(
                f'Gate {gate["gate"]}: {gate.get("name", "")} — {passed}'
            )
            for check in gate.get('checks', []):
                chk = 'PASS' if check['passed'] else 'FAIL'
                lines.append(
                    f'  [{chk}] {check["equation"]}: {check["name"]}'
                )
                if not check['passed']:
                    for k, v in check.get('details', {}).items():
                        lines.append(f'         {k}: {v}')
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
