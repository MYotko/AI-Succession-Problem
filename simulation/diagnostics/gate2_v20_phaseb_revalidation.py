"""Gate 2 v2.0 revalidation from the authoritative v2.0 empirical record.

This does NOT run a sweep. It assembles the Gate 2 input payload from existing
v2.0 data and runs the bootstrap gate validator:

  G2.1  Piece 1 (phi_finegrained, rr=0.057): phi survival curve. The revised
        check requires the peak-minus-trough differential to exceed 2 SE with
        the peak in the high-phi band (Class B U-shape).
  G2.2  Monte Carlo Phase B Category B: cap_star by alpha (the Pattern 1 cliff
        migration). The revised check requires cap_star to decrease
        monotonically with alpha.
  G2.4  Monte Carlo Phase B Category A: phi x alpha generation structure.
  G2.3  Theoretical Nash consistency (standard payload).

Run: python -u simulation/diagnostics/gate2_v20_phaseb_revalidation.py
"""

import csv
import os
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from bootstrap_gate_validator.validator import BootstrapGateValidator  # noqa: E402

PIECE1 = os.path.join(HERE, 'phi_finegrained_results.csv')
CAT_A = os.path.join(HERE, 'monte_carlo_phase_b_a_results.csv')
CAT_B = os.path.join(HERE, 'monte_carlo_phase_b_b_results.csv')

RR_MARGINAL = 0.057
FIRE_THRESHOLD = 0.5  # cap_star = largest successor_capability with fire_rate >= this


def _load(path):
    with open(path, newline='') as f:
        return list(csv.DictReader(f))


def _is_true(v):
    return str(v).strip().lower() == 'true'


def _mean(xs):
    xs = list(xs)
    return sum(xs) / len(xs) if xs else 0.0


def build_g2_1(rows):
    """Phi survival curve at rr=0.057 from Piece 1."""
    sub = [r for r in rows if abs(float(r['rr']) - RR_MARGINAL) < 1e-9]
    phis = sorted({float(r['phi']) for r in sub})
    curve = []
    for phi in phis:
        cell = [r for r in sub if abs(float(r['phi']) - phi) < 1e-9]
        n = len(cell)
        surv = _mean(1.0 if _is_true(r['survived']) else 0.0 for r in cell)
        curve.append({'phi': phi, 'survival_rate': surv, 'n': n})
    return {'rr': RR_MARGINAL, 'phi_survival_curve': curve,
            'peak_phi_range': [20.0, 30.0]}


def build_g2_2(rows):
    """cap_star by alpha from Phase B Category B (fire rate over rr, seed)."""
    alphas = sorted({float(r['alpha']) for r in rows})
    caps = sorted({float(r['successor_capability']) for r in rows})
    entries = []
    for a in alphas:
        fired_caps = []
        for c in caps:
            cell = [r for r in rows
                    if abs(float(r['alpha']) - a) < 1e-9
                    and abs(float(r['successor_capability']) - c) < 1e-9]
            fr = _mean(1.0 if _is_true(r['yield_fired']) else 0.0 for r in cell)
            if fr >= FIRE_THRESHOLD:
                fired_caps.append(c)
        cap_star = max(fired_caps) if fired_caps else 0.0
        entries.append({'alpha': a, 'cap_star': cap_star})
    return {'cap_star_by_alpha': entries}


def build_g2_4(rows):
    """phi x alpha mean generation matrix at rr=0.057 from Phase B Category A."""
    sub = [r for r in rows if abs(float(r['rr']) - RR_MARGINAL) < 1e-9]
    phis = sorted({float(r['phi']) for r in sub})
    alphas = sorted({float(r['alpha']) for r in sub})
    matrix = []
    for phi in phis:
        row = []
        for a in alphas:
            cell = [r for r in sub
                    if abs(float(r['phi']) - phi) < 1e-9
                    and abs(float(r['alpha']) - a) < 1e-9]
            row.append(_mean(float(r['final_ai_generation']) for r in cell))
        matrix.append(row)
    return {'phi_alpha_matrix': matrix,
            'phi_values': list(phis), 'alpha_values': list(alphas)}


def build_g2_3():
    """Standard Nash consistency payload (theoretical; matches sample input)."""
    a, c, d, delta = 1.0, 1.5, 0.3, 0.95
    return {
        'cultivate_cultivate_payoff': a,
        'exploit_payoff': c,
        'model_collapse_penalty': d,
        'discount_factor': delta,
        'cooperation_threshold_computed': (c - a) / (c - d),
    }


def main():
    piece1 = _load(PIECE1)
    cat_a = _load(CAT_A)
    cat_b = _load(CAT_B)

    gate_2 = {
        'phi_buffer_test': build_g2_1(piece1),
        'alpha_cliff_test': build_g2_2(cat_b),
        'nash_consistency': build_g2_3(),
        'phi_alpha_characterization_test': build_g2_4(cat_a),
    }
    config = {
        'substrate_id': 'lineage-imperative-v2.0-abm',
        'report_date': datetime.now(timezone.utc).strftime('%Y-%m-%d'),
        'framework_version': 'v2.0',
        'gate_2': gate_2,
    }

    results = BootstrapGateValidator().validate(config)
    g2 = [g for g in results['gates'] if g.get('gate') == 2][0]

    lines = []
    lines.append('# Gate 2 v2.0 Revalidation (from authoritative empirical record)')
    lines.append('')
    lines.append(f'Generated: {datetime.now(timezone.utc).isoformat()}')
    lines.append('')
    lines.append(f'Gate 2 verdict: **{"PASS" if g2["passed"] else "FAIL"}**')
    lines.append('')
    lines.append('Provenance: G2.1 Piece 1 (phi_finegrained, rr=0.057); '
                 'G2.2 Phase B Category B; G2.4 Phase B Category A; '
                 'G2.3 theoretical.')
    lines.append('')
    for chk in g2['checks']:
        verdict = 'PASS' if chk['passed'] else 'FAIL'
        lines.append(f'## {chk["equation"]} {chk["name"]}: {verdict}')
        for k, v in chk['details'].items():
            lines.append(f'- {k}: {v}')
        lines.append('')

    out = os.path.join(HERE, 'gate2_v20_phaseb_revalidation_summary.md')
    with open(out, 'w') as f:
        f.write('\n'.join(lines))

    print(f'Gate 2 verdict: {"PASS" if g2["passed"] else "FAIL"}')
    for chk in g2['checks']:
        print(f'  {chk["equation"]}: {"PASS" if chk["passed"] else "FAIL"}')
    print(f'Wrote {out}')
    return 0 if g2['passed'] else 1


if __name__ == '__main__':
    sys.exit(main())
